"""Hermetic tests for pollinations-mcp.

No network, no fixtures downloaded at run time: every HTTP call is stubbed, so
this suite passes on a machine with the ethernet cable pulled out.
"""

import base64
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server  # noqa: E402


class EnvMixin(unittest.TestCase):
    """Give each test a clean output dir and no inherited key/rate-limit state."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(
            os.environ,
            {
                "POLLINATIONS_OUTPUT_DIR": self.tmp.name,
                "POLLINATIONS_MIN_INTERVAL": "0",
            },
            clear=False,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("POLLINATIONS_KEY", None)
        server._last_request_at = 0.0


class TestSlugify(unittest.TestCase):
    def test_collapses_unsafe_characters(self):
        self.assertEqual(server.slugify("a red fox, in snow!"), "a-red-fox-in-snow")

    def test_strips_path_separators(self):
        self.assertNotIn("/", server.slugify("../../etc/passwd"))

    def test_empty_input_gets_a_name(self):
        self.assertEqual(server.slugify("///"), "untitled")

    def test_respects_limit(self):
        self.assertLessEqual(len(server.slugify("x" * 200)), 48)


class TestSafeOutputPath(EnvMixin):
    def test_writes_inside_output_dir(self):
        path = server.safe_output_path("cat", "prompt", ".jpg")
        self.assertTrue(path.startswith(os.path.realpath(self.tmp.name)) or path.startswith(self.tmp.name))
        self.assertTrue(path.endswith("cat.jpg"))

    def test_traversal_in_name_is_neutralised(self):
        path = server.safe_output_path("../../../../etc/passwd", "prompt", ".jpg")
        self.assertTrue(path.startswith(server.output_dir() + os.sep))
        self.assertNotIn("..", path)

    def test_does_not_double_the_extension(self):
        path = server.safe_output_path("fox.jpg", "prompt", ".jpg")
        self.assertTrue(path.endswith("fox.jpg"))
        self.assertFalse(path.endswith("fox.jpg.jpg"))

    def test_prompt_is_used_when_no_name_given(self):
        path = server.safe_output_path(None, "a red fox", ".png")
        self.assertIn("a-red-fox", os.path.basename(path))


class TestExtensionFor(unittest.TestCase):
    def test_known_types(self):
        self.assertEqual(server.extension_for("image/jpeg", ".bin"), ".jpg")
        self.assertEqual(server.extension_for("video/mp4", ".bin"), ".mp4")

    def test_strips_charset_parameter(self):
        self.assertEqual(server.extension_for("image/png; charset=binary", ".bin"), ".png")

    def test_falls_back_when_unknown(self):
        self.assertEqual(server.extension_for("application/x-nonsense", ".jpg"), ".jpg")


class TestQueryBuilding(unittest.TestCase):
    def test_drops_none_and_empty(self):
        self.assertEqual(server._query({"a": None, "b": "", "c": 1}), "c=1")

    def test_booleans_become_lowercase_words(self):
        self.assertEqual(server._query({"audio": True}), "audio=true")
        self.assertEqual(server._query({"audio": False}), "audio=false")

    def test_zero_is_kept(self):
        # seed=0 is meaningful (it is the documented default), so it must survive.
        self.assertEqual(server._query({"seed": 0}), "seed=0")


class TestUrlBuilding(EnvMixin):
    def test_image_without_key_uses_legacy_anonymous_host(self):
        url = server.build_image_url("a red fox", {"width": 512})
        self.assertTrue(url.startswith("https://image.pollinations.ai/prompt/"))
        self.assertIn("width=512", url)

    def test_image_with_key_uses_gen_host(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        url = server.build_image_url("a red fox", {})
        self.assertTrue(url.startswith("https://gen.pollinations.ai/image/"))

    def test_prompt_is_percent_encoded(self):
        url = server.build_image_url("a/b?c=d", {})
        self.assertNotIn("a/b?c=d", url)
        self.assertIn("a%2Fb%3Fc%3Dd", url)

    def test_video_always_uses_gen_host(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        url = server.build_video_url("sunset", {"duration": 4})
        self.assertTrue(url.startswith("https://gen.pollinations.ai/video/"))
        self.assertIn("duration=4", url)


class TestGenerateImage(EnvMixin):
    def test_saves_file_and_inlines_preview(self):
        payload = b"\xff\xd8\xff" + b"jpegbytes"
        with mock.patch.object(server, "http_get", return_value=(payload, "image/jpeg")):
            content = server.tool_generate_image({"prompt": "a red fox", "output_name": "fox"})

        path = os.path.join(server.output_dir(), "fox.jpg")
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), payload)

        self.assertEqual(content[0]["type"], "text")
        self.assertIn(path, content[0]["text"])
        self.assertEqual(content[1]["type"], "image")
        self.assertEqual(base64.b64decode(content[1]["data"]), payload)

    def test_oversized_image_is_not_inlined(self):
        payload = b"x" * (server.MAX_INLINE_PREVIEW_BYTES + 1)
        with mock.patch.object(server, "http_get", return_value=(payload, "image/png")):
            content = server.tool_generate_image({"prompt": "big", "output_name": "big"})
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["type"], "text")

    def test_html_error_page_is_rejected_not_saved_as_an_image(self):
        with mock.patch.object(server, "http_get", return_value=(b"<html>nope</html>", "text/html")):
            with self.assertRaises(server.ToolError) as caught:
                server.tool_generate_image({"prompt": "x"})
        self.assertIn("expected an image", str(caught.exception))

    def test_empty_prompt_is_refused(self):
        with self.assertRaises(server.ToolError):
            server.tool_generate_image({"prompt": "   "})

    def test_anonymous_requests_ask_for_no_watermark(self):
        captured = {}

        def fake_get(url, **kwargs):
            captured["url"] = url
            return b"\xff\xd8\xff", "image/jpeg"

        with mock.patch.object(server, "http_get", side_effect=fake_get):
            server.tool_generate_image({"prompt": "x"})
        self.assertIn("nologo=true", captured["url"])


class TestGenerateVideo(EnvMixin):
    def test_without_key_explains_how_to_get_one(self):
        with self.assertRaises(server.ToolError) as caught:
            server.tool_generate_video({"prompt": "sunset"})
        message = str(caught.exception)
        self.assertIn("POLLINATIONS_KEY", message)
        self.assertIn("enter.pollinations.ai", message)

    def test_with_key_saves_mp4(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        with mock.patch.object(server, "http_get", return_value=(b"mp4data", "video/mp4")):
            content = server.tool_generate_video({"prompt": "sunset", "output_name": "sunset"})
        path = os.path.join(server.output_dir(), "sunset.mp4")
        self.assertTrue(os.path.exists(path))
        self.assertIn(path, content[0]["text"])

    def test_non_video_response_is_rejected(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        with mock.patch.object(server, "http_get", return_value=(b'{"error":"x"}', "application/json")):
            with self.assertRaises(server.ToolError):
                server.tool_generate_video({"prompt": "sunset"})


class TestListModels(EnvMixin):
    def test_parses_openai_style_data_list(self):
        body = json.dumps({"data": [{"id": "flux"}, {"id": "zimage"}]}).encode()
        with mock.patch.object(server, "http_get", return_value=(body, "application/json")):
            content = server.tool_list_models({"kind": "image"})
        self.assertIn("flux", content[0]["text"])
        self.assertIn("zimage", content[0]["text"])

    def test_parses_bare_list(self):
        body = json.dumps(["veo", "wan"]).encode()
        with mock.patch.object(server, "http_get", return_value=(body, "application/json")):
            content = server.tool_list_models({"kind": "video"})
        self.assertIn("veo", content[0]["text"])

    def test_rejects_unknown_kind(self):
        with self.assertRaises(server.ToolError):
            server.tool_list_models({"kind": "audio"})

    def test_invalid_json_is_reported_clearly(self):
        with mock.patch.object(server, "http_get", return_value=(b"not json", "application/json")):
            with self.assertRaises(server.ToolError) as caught:
                server.tool_list_models({})
        self.assertIn("valid JSON", str(caught.exception))


class TestHttpErrorMessages(unittest.TestCase):
    def test_401_points_at_the_key(self):
        self.assertIn("POLLINATIONS_KEY", server._explain_http_error(401, ""))

    def test_402_mentions_balance(self):
        self.assertIn("balance", server._explain_http_error(402, ""))

    def test_429_mentions_rate_limit(self):
        self.assertIn("rate limited", server._explain_http_error(429, ""))


class TestProtocol(EnvMixin):
    def test_initialize_reports_tools_capability(self):
        response = server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["result"]["protocolVersion"], server.PROTOCOL_VERSION)
        self.assertIn("tools", response["result"]["capabilities"])
        self.assertEqual(response["result"]["serverInfo"]["name"], "pollinations-mcp")

    def test_initialized_notification_gets_no_response(self):
        self.assertIsNone(server.handle_message({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tools_list_declares_three_tools_with_schemas(self):
        response = server.handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = response["result"]["tools"]
        self.assertEqual({t["name"] for t in tools}, {"generate_image", "generate_video", "list_models"})
        for tool in tools:
            self.assertEqual(tool["inputSchema"]["type"], "object")
            self.assertTrue(tool["description"])

    def test_unknown_method_returns_method_not_found(self):
        response = server.handle_message({"jsonrpc": "2.0", "id": 3, "method": "nope"})
        self.assertEqual(response["error"]["code"], -32601)

    def test_unknown_notification_is_silently_ignored(self):
        self.assertIsNone(server.handle_message({"jsonrpc": "2.0", "method": "nope"}))

    def test_tool_failure_is_an_iserror_result_not_a_protocol_error(self):
        response = server.handle_message({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "generate_video", "arguments": {"prompt": "x"}},
        })
        self.assertNotIn("error", response)
        self.assertTrue(response["result"]["isError"])

    def test_unknown_tool_name_is_an_iserror_result(self):
        response = server.handle_message({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "rm_rf", "arguments": {}},
        })
        self.assertTrue(response["result"]["isError"])

    def test_every_response_is_a_single_json_line(self):
        # The stdio transport is newline-delimited: an embedded newline would
        # split one message into two and desynchronise the client.
        response = server.handle_message({"jsonrpc": "2.0", "id": 6, "method": "tools/list"})
        self.assertNotIn("\n", json.dumps(response))


if __name__ == "__main__":
    unittest.main(verbosity=2)
