"""Hermetic tests for genmedia-mcp.

No network: every HTTP call is stubbed, so this suite passes with the ethernet
cable pulled out. That is deliberate -- the environment this was written in has
every provider host blocked at the egress proxy, so the live proof is
`server.py --selfcheck` on an unrestricted machine, and everything that can be
tested without a network is tested here.
"""

import base64
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import http_client  # noqa: E402
import providers  # noqa: E402
import server  # noqa: E402

PROVIDER_ENV = (
    "POLLINATIONS_KEY",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "GEMINI_API_KEY",
    "TOGETHER_API_KEY",
    "IMAGE_PROVIDERS",
)


class Base(unittest.TestCase):
    """Clean output dir, no inherited credentials, no throttling."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict(
            os.environ,
            {"POLLINATIONS_OUTPUT_DIR": self.tmp.name, "POLLINATIONS_MIN_INTERVAL": "0"},
            clear=False,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        for var in PROVIDER_ENV:
            os.environ.pop(var, None)
        http_client._last_call_at.clear()


# --------------------------------------------------------------------------
# filesystem safety
# --------------------------------------------------------------------------

class TestSlugify(unittest.TestCase):
    def test_collapses_unsafe_characters(self):
        self.assertEqual(server.slugify("a red fox, in snow!"), "a-red-fox-in-snow")

    def test_strips_path_separators(self):
        self.assertNotIn("/", server.slugify("../../etc/passwd"))

    def test_empty_input_gets_a_name(self):
        self.assertEqual(server.slugify("///"), "untitled")

    def test_respects_limit(self):
        self.assertLessEqual(len(server.slugify("x" * 200)), 48)


class TestSafeOutputPath(Base):
    def test_writes_inside_output_dir(self):
        path = server.safe_output_path("cat", "prompt", ".jpg")
        self.assertTrue(path.startswith(server.output_dir() + os.sep))
        self.assertTrue(path.endswith("cat.jpg"))

    def test_traversal_in_name_is_neutralised(self):
        path = server.safe_output_path("../../../../etc/passwd", "prompt", ".jpg")
        self.assertTrue(path.startswith(server.output_dir() + os.sep))
        self.assertNotIn("..", path)

    def test_does_not_double_the_extension(self):
        self.assertTrue(server.safe_output_path("fox.jpg", "p", ".jpg").endswith("fox.jpg"))
        self.assertFalse(server.safe_output_path("fox.jpg", "p", ".jpg").endswith("fox.jpg.jpg"))

    def test_prompt_is_used_when_no_name_given(self):
        self.assertIn("a-red-fox", os.path.basename(server.safe_output_path(None, "a red fox", ".png")))


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
        self.assertEqual(providers._query({"a": None, "b": "", "c": 1}), "c=1")

    def test_booleans_become_lowercase_words(self):
        self.assertEqual(providers._query({"audio": True}), "audio=true")
        self.assertEqual(providers._query({"audio": False}), "audio=false")

    def test_zero_is_kept(self):
        # seed=0 is the documented default and is meaningful, so it must survive.
        self.assertEqual(providers._query({"seed": 0}), "seed=0")


# --------------------------------------------------------------------------
# provider chain
# --------------------------------------------------------------------------

class TestChainResolution(Base):
    def test_default_chain_falls_back_to_keyless_pollinations(self):
        chain = providers.resolve_chain(None)
        self.assertEqual([p.name for p in chain], ["pollinations"])

    def test_configured_providers_come_before_pollinations(self):
        os.environ["GEMINI_API_KEY"] = "k"
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = "a"
        os.environ["CLOUDFLARE_API_TOKEN"] = "t"
        self.assertEqual(
            [p.name for p in providers.resolve_chain(None)],
            ["cloudflare", "gemini", "pollinations"],
        )

    def test_env_override_controls_order(self):
        os.environ["GEMINI_API_KEY"] = "k"
        os.environ["IMAGE_PROVIDERS"] = "pollinations,gemini"
        self.assertEqual([p.name for p in providers.resolve_chain(None)], ["pollinations", "gemini"])

    def test_env_override_skips_unconfigured_entries(self):
        os.environ["IMAGE_PROVIDERS"] = "together,pollinations"
        self.assertEqual([p.name for p in providers.resolve_chain(None)], ["pollinations"])

    def test_explicit_provider_is_used_alone(self):
        os.environ["GEMINI_API_KEY"] = "k"
        self.assertEqual([p.name for p in providers.resolve_chain("gemini")], ["gemini"])

    def test_unknown_provider_lists_the_valid_names(self):
        with self.assertRaises(http_client.ToolError) as caught:
            providers.resolve_chain("dall-e")
        self.assertIn("cloudflare", str(caught.exception))

    def test_empty_chain_is_reported(self):
        os.environ["IMAGE_PROVIDERS"] = "gemini"
        with self.assertRaises(http_client.ToolError):
            providers.resolve_chain(None)


# --------------------------------------------------------------------------
# individual provider adapters
# --------------------------------------------------------------------------

class TestPollinationsProvider(Base):
    def test_without_key_uses_legacy_host_and_asks_for_no_watermark(self):
        seen = {}

        def fake(url, **kwargs):
            seen["url"] = url
            seen["headers"] = kwargs.get("headers", {})
            return b"\xff\xd8\xff", "image/jpeg"

        with mock.patch.object(providers, "http_request", side_effect=fake):
            providers.REGISTRY["pollinations"].generate("a fox", {})
        self.assertIn("image.pollinations.ai/prompt/", seen["url"])
        self.assertIn("nologo=true", seen["url"])
        self.assertNotIn("Authorization", seen["headers"])

    def test_with_key_uses_gen_host_and_bearer_auth(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        seen = {}

        def fake(url, **kwargs):
            seen["url"] = url
            seen["headers"] = kwargs.get("headers", {})
            return b"\xff\xd8\xff", "image/jpeg"

        with mock.patch.object(providers, "http_request", side_effect=fake):
            providers.REGISTRY["pollinations"].generate("a fox", {})
        self.assertIn("gen.pollinations.ai/image/", seen["url"])
        self.assertEqual(seen["headers"]["Authorization"], "Bearer sk_test")

    def test_prompt_is_percent_encoded(self):
        seen = {}
        with mock.patch.object(providers, "http_request", side_effect=lambda url, **k: (seen.setdefault("u", url), (b"\xff\xd8\xff", "image/jpeg"))[1]):
            providers.REGISTRY["pollinations"].generate("a/b?c=d", {})
        self.assertIn("a%2Fb%3Fc%3Dd", seen["u"])

    def test_html_error_page_is_rejected(self):
        with mock.patch.object(providers, "http_request", return_value=(b"<html>no</html>", "text/html")):
            with self.assertRaises(http_client.ToolError):
                providers.REGISTRY["pollinations"].generate("x", {})


class TestCloudflareProvider(Base):
    def setUp(self):
        super().setUp()
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = "acct123"
        os.environ["CLOUDFLARE_API_TOKEN"] = "tok"

    def test_parses_base64_envelope(self):
        raw = b"pngbytes"
        body = json.dumps({"success": True, "result": {"image": base64.b64encode(raw).decode()}}).encode()
        with mock.patch.object(providers, "http_request", return_value=(body, "application/json")):
            payload, mime = providers.REGISTRY["cloudflare"].generate("x", {})
        self.assertEqual(payload, raw)
        self.assertTrue(mime.startswith("image/"))

    def test_accepts_raw_binary_from_models_that_stream_it(self):
        with mock.patch.object(providers, "http_request", return_value=(b"\x89PNG", "image/png")):
            payload, mime = providers.REGISTRY["cloudflare"].generate("x", {})
        self.assertEqual(payload, b"\x89PNG")
        self.assertEqual(mime, "image/png")

    def test_success_false_surfaces_the_error_list(self):
        body = json.dumps({"success": False, "errors": [{"message": "no such model"}]}).encode()
        with mock.patch.object(providers, "http_request", return_value=(body, "application/json")):
            with self.assertRaises(http_client.ToolError) as caught:
                providers.REGISTRY["cloudflare"].generate("x", {})
        self.assertIn("no such model", str(caught.exception))

    def test_account_id_and_model_land_in_the_url(self):
        seen = {}
        body = json.dumps({"result": {"image": base64.b64encode(b"x").decode()}}).encode()

        def fake(url, **kwargs):
            seen["url"] = url
            seen["body"] = json.loads(kwargs["body"])
            return body, "application/json"

        with mock.patch.object(providers, "http_request", side_effect=fake):
            providers.REGISTRY["cloudflare"].generate("a fox", {"steps": 4})
        self.assertIn("/accounts/acct123/ai/run/@cf/black-forest-labs/flux-1-schnell", seen["url"])
        self.assertEqual(seen["body"], {"prompt": "a fox", "steps": 4})

    def test_non_json_body_is_reported_not_saved(self):
        with mock.patch.object(providers, "http_request", return_value=(b"gateway timeout", "text/plain")):
            with self.assertRaises(http_client.ToolError) as caught:
                providers.REGISTRY["cloudflare"].generate("x", {})
        self.assertIn("non-JSON", str(caught.exception))


class TestGeminiProvider(Base):
    def setUp(self):
        super().setUp()
        os.environ["GEMINI_API_KEY"] = "gk"

    def test_parses_inline_data(self):
        raw = b"imgbytes"
        body = json.dumps({
            "candidates": [{"content": {"parts": [
                {"text": "here you go"},
                {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(raw).decode()}},
            ]}}]
        }).encode()
        with mock.patch.object(providers, "http_request", return_value=(body, "application/json")):
            payload, mime = providers.REGISTRY["gemini"].generate("x", {})
        self.assertEqual(payload, raw)
        self.assertEqual(mime, "image/png")

    def test_accepts_snake_case_inline_data(self):
        raw = b"imgbytes"
        body = json.dumps({
            "candidates": [{"content": {"parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(raw).decode()}}
            ]}}]
        }).encode()
        with mock.patch.object(providers, "http_request", return_value=(body, "application/json")):
            payload, mime = providers.REGISTRY["gemini"].generate("x", {})
        self.assertEqual(payload, raw)
        self.assertEqual(mime, "image/jpeg")

    def test_text_only_refusal_surfaces_what_the_model_said(self):
        body = json.dumps({"candidates": [{"content": {"parts": [{"text": "I can't make that."}]}}]}).encode()
        with mock.patch.object(providers, "http_request", return_value=(body, "application/json")):
            with self.assertRaises(http_client.ToolError) as caught:
                providers.REGISTRY["gemini"].generate("x", {})
        self.assertIn("I can't make that.", str(caught.exception))

    def test_api_key_goes_in_the_header_not_the_url(self):
        seen = {}
        body = json.dumps({"candidates": [{"content": {"parts": [
            {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(b"x").decode()}}
        ]}}]}).encode()

        def fake(url, **kwargs):
            seen["url"] = url
            seen["headers"] = kwargs["headers"]
            return body, "application/json"

        with mock.patch.object(providers, "http_request", side_effect=fake):
            providers.REGISTRY["gemini"].generate("x", {})
        self.assertNotIn("gk", seen["url"])
        self.assertEqual(seen["headers"]["x-goog-api-key"], "gk")


class TestTogetherProvider(Base):
    def setUp(self):
        super().setUp()
        os.environ["TOGETHER_API_KEY"] = "tk"

    def test_parses_b64_json(self):
        raw = b"imgbytes"
        body = json.dumps({"data": [{"b64_json": base64.b64encode(raw).decode()}]}).encode()
        with mock.patch.object(providers, "http_request", return_value=(body, "application/json")):
            payload, _ = providers.REGISTRY["together"].generate("x", {})
        self.assertEqual(payload, raw)

    def test_defaults_to_the_free_flux_endpoint(self):
        seen = {}
        body = json.dumps({"data": [{"b64_json": base64.b64encode(b"x").decode()}]}).encode()

        def fake(url, **kwargs):
            seen["body"] = json.loads(kwargs["body"])
            return body, "application/json"

        with mock.patch.object(providers, "http_request", side_effect=fake):
            providers.REGISTRY["together"].generate("x", {})
        self.assertEqual(seen["body"]["model"], "black-forest-labs/FLUX.1-schnell-Free")
        self.assertEqual(seen["body"]["response_format"], "b64_json")

    def test_missing_data_is_reported(self):
        with mock.patch.object(providers, "http_request", return_value=(b'{"data":[]}', "application/json")):
            with self.assertRaises(http_client.ToolError):
                providers.REGISTRY["together"].generate("x", {})


# --------------------------------------------------------------------------
# tool behaviour
# --------------------------------------------------------------------------

class TestGenerateImage(Base):
    def test_saves_file_and_inlines_preview(self):
        payload = b"\xff\xd8\xffjpegbytes"
        with mock.patch.object(providers, "http_request", return_value=(payload, "image/jpeg")):
            content = server.tool_generate_image({"prompt": "a red fox", "output_name": "fox"})

        path = os.path.join(server.output_dir(), "fox.jpg")
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), payload)
        self.assertEqual(content[1]["type"], "image")
        self.assertEqual(base64.b64decode(content[1]["data"]), payload)

    def test_oversized_image_is_not_inlined(self):
        payload = b"x" * (server.MAX_INLINE_PREVIEW_BYTES + 1)
        with mock.patch.object(providers, "http_request", return_value=(payload, "image/png")):
            content = server.tool_generate_image({"prompt": "big", "output_name": "big"})
        self.assertEqual(len(content), 1)

    def test_falls_through_to_the_next_provider_and_says_so(self):
        os.environ["GEMINI_API_KEY"] = "gk"  # chain becomes gemini -> pollinations
        calls = []

        def fake(url, **kwargs):
            calls.append(url)
            if "googleapis" in url:
                raise http_client.ToolError("429 from generativelanguage.googleapis.com: slow down")
            return b"\xff\xd8\xff", "image/jpeg"

        with mock.patch.object(providers, "http_request", side_effect=fake):
            content = server.tool_generate_image({"prompt": "fox", "output_name": "fox"})

        self.assertEqual(len(calls), 2)
        text = content[0]["text"]
        self.assertIn("provider: pollinations", text)
        self.assertIn("fell back after", text)
        self.assertIn("gemini", text)

    def test_pinned_provider_does_not_silently_fall_back(self):
        os.environ["GEMINI_API_KEY"] = "gk"
        with mock.patch.object(providers, "http_request", side_effect=http_client.ToolError("boom")):
            with self.assertRaises(http_client.ToolError) as caught:
                server.tool_generate_image({"prompt": "fox", "provider": "gemini"})
        message = str(caught.exception)
        self.assertIn("gemini", message)
        self.assertNotIn("pollinations", message)

    def test_all_providers_failing_reports_every_reason(self):
        os.environ["GEMINI_API_KEY"] = "gk"
        with mock.patch.object(providers, "http_request", side_effect=http_client.ToolError("down")):
            with self.assertRaises(http_client.ToolError) as caught:
                server.tool_generate_image({"prompt": "fox"})
        message = str(caught.exception)
        self.assertIn("gemini", message)
        self.assertIn("pollinations", message)
        self.assertIn("selfcheck", message)

    def test_empty_prompt_is_refused(self):
        with self.assertRaises(http_client.ToolError):
            server.tool_generate_image({"prompt": "   "})


class TestGenerateVideo(Base):
    def test_without_key_explains_that_no_free_keyless_video_exists(self):
        with self.assertRaises(http_client.ToolError) as caught:
            server.tool_generate_video({"prompt": "sunset"})
        message = str(caught.exception)
        self.assertIn("POLLINATIONS_KEY", message)
        self.assertIn("enter.pollinations.ai", message)

    def test_with_key_saves_mp4(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        with mock.patch.object(server, "http_request", return_value=(b"mp4data", "video/mp4")):
            content = server.tool_generate_video({"prompt": "sunset", "output_name": "sunset"})
        self.assertTrue(os.path.exists(os.path.join(server.output_dir(), "sunset.mp4")))
        self.assertIn("sunset.mp4", content[0]["text"])

    def test_non_video_response_is_rejected(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        with mock.patch.object(server, "http_request", return_value=(b'{"error":"x"}', "application/json")):
            with self.assertRaises(http_client.ToolError):
                server.tool_generate_video({"prompt": "sunset"})

    def test_duration_and_aspect_ratio_reach_the_url(self):
        os.environ["POLLINATIONS_KEY"] = "sk_test"
        seen = {}

        def fake(url, **kwargs):
            seen["url"] = url
            return b"mp4", "video/mp4"

        with mock.patch.object(server, "http_request", side_effect=fake):
            server.tool_generate_video({"prompt": "sunset", "duration": 6, "aspect_ratio": "9:16"})
        self.assertIn("duration=6", seen["url"])
        self.assertIn("aspectRatio=9%3A16", seen["url"])


class TestListProviders(Base):
    def test_shows_ready_and_missing_with_signup_links(self):
        os.environ["GEMINI_API_KEY"] = "gk"
        text = server.tool_list_providers({})[0]["text"]
        self.assertIn("[ready]   gemini", text)
        self.assertIn("[missing] cloudflare", text)
        self.assertIn("CLOUDFLARE_API_TOKEN", text)
        self.assertIn("Active image chain: gemini -> pollinations", text)

    def test_makes_no_network_calls(self):
        with mock.patch.object(providers, "http_request", side_effect=AssertionError("network!")):
            server.tool_list_providers({})


class TestListModels(Base):
    def test_parses_openai_style_data_list(self):
        body = json.dumps({"data": [{"id": "flux"}, {"id": "zimage"}]}).encode()
        with mock.patch.object(server, "http_request", return_value=(body, "application/json")):
            text = server.tool_list_models({"kind": "image"})[0]["text"]
        self.assertIn("flux", text)

    def test_rejects_unknown_kind(self):
        with self.assertRaises(http_client.ToolError):
            server.tool_list_models({"kind": "audio"})

    def test_invalid_json_is_reported_clearly(self):
        with mock.patch.object(server, "http_request", return_value=(b"not json", "application/json")):
            with self.assertRaises(http_client.ToolError) as caught:
                server.tool_list_models({})
        self.assertIn("valid JSON", str(caught.exception))


# --------------------------------------------------------------------------
# HTTP layer
# --------------------------------------------------------------------------

class TestHttpErrorMessages(unittest.TestCase):
    def test_401_and_403_point_at_credentials(self):
        self.assertIn("credentials", http_client.explain_http_error(401, "", "h"))
        self.assertIn("credentials", http_client.explain_http_error(403, "", "h"))

    def test_402_mentions_balance(self):
        self.assertIn("balance", http_client.explain_http_error(402, "", "h"))

    def test_429_mentions_falling_through_to_another_provider(self):
        self.assertIn("another provider", http_client.explain_http_error(429, "", "h"))

    def test_host_is_named_so_you_know_which_provider_failed(self):
        self.assertIn("api.cloudflare.com", http_client.explain_http_error(500, "", "api.cloudflare.com"))

    def test_body_whitespace_is_collapsed(self):
        self.assertIn("a b", http_client.explain_http_error(500, "a\n\n   b", "h"))


class TestThrottle(unittest.TestCase):
    def test_throttling_is_per_host(self):
        # A slow anonymous Pollinations tier must not delay a Cloudflare call.
        http_client._last_call_at.clear()
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("POLLINATIONS_MIN_INTERVAL", None)
            with mock.patch.object(http_client.time, "sleep") as slept:
                http_client._throttle("image.pollinations.ai", 15.0)
                http_client._throttle("api.cloudflare.com", 0.0)
                slept.assert_not_called()


# --------------------------------------------------------------------------
# protocol
# --------------------------------------------------------------------------

class TestProtocol(Base):
    def test_initialize_reports_tools_capability(self):
        response = server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(response["result"]["protocolVersion"], server.PROTOCOL_VERSION)
        self.assertIn("tools", response["result"]["capabilities"])

    def test_initialized_notification_gets_no_response(self):
        self.assertIsNone(server.handle_message({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tools_list_declares_four_tools_with_schemas(self):
        tools = server.handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual(
            {t["name"] for t in tools},
            {"generate_image", "generate_video", "list_providers", "list_models"},
        )
        for tool in tools:
            self.assertEqual(tool["inputSchema"]["type"], "object")
            self.assertTrue(tool["description"])

    def test_provider_enum_matches_the_registry(self):
        tools = {t["name"]: t for t in server.TOOLS}
        enum = tools["generate_image"]["inputSchema"]["properties"]["provider"]["enum"]
        self.assertEqual(set(enum), set(providers.REGISTRY))

    def test_unknown_method_returns_method_not_found(self):
        response = server.handle_message({"jsonrpc": "2.0", "id": 3, "method": "nope"})
        self.assertEqual(response["error"]["code"], -32601)

    def test_unknown_notification_is_silently_ignored(self):
        self.assertIsNone(server.handle_message({"jsonrpc": "2.0", "method": "nope"}))

    def test_tool_failure_is_an_iserror_result_not_a_protocol_error(self):
        response = server.handle_message({
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "generate_video", "arguments": {"prompt": "x"}},
        })
        self.assertNotIn("error", response)
        self.assertTrue(response["result"]["isError"])

    def test_unknown_tool_name_is_an_iserror_result(self):
        response = server.handle_message({
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "rm_rf", "arguments": {}},
        })
        self.assertTrue(response["result"]["isError"])

    def test_every_response_is_a_single_json_line(self):
        # The stdio transport is newline-delimited: an embedded newline would
        # split one message in two and desynchronise the client.
        response = server.handle_message({"jsonrpc": "2.0", "id": 6, "method": "tools/list"})
        self.assertNotIn("\n", json.dumps(response))


if __name__ == "__main__":
    unittest.main(verbosity=2)
