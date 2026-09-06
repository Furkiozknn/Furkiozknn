# pollinations-mcp

A text-to-image and text-to-video MCP server in one file, with no dependencies —
no `pip install`, no `npx`, nothing that updates itself between the audit and the
run. `server.py` is 524 lines and is the entire supply chain.

It talks to [Pollinations](https://pollinations.ai), which is the only generative
image/video API surveyed that serves anything at all without a credit card.

## Tools

| Tool | What it does | Needs a key? |
|---|---|---|
| `generate_image` | Text → image, saved to disk, preview inlined into the reply | No |
| `generate_video` | Text → MP4, saved to disk | **Yes** |
| `list_models` | Current image or video model catalogue | No |

## Two tiers, and what actually works without a key

Pollinations moved to a new API host (`gen.pollinations.ai`) whose docs state:
"Everything else | Bearer key required unless the endpoint documents `?key=` support."
The older anonymous host (`image.pollinations.ai/prompt/{prompt}`) still serves
images with no credentials at all, and the model catalogue is public on both.

So the server picks its route based on whether `POLLINATIONS_KEY` is set:

- **No key** — images go to the legacy anonymous host with `nologo=true&private=true`.
  Works out of the box; rate limited to roughly one request every 15 seconds, and
  upstream is clearly winding this path down. `generate_video` refuses with a message
  telling you where to get a key rather than failing obscurely.
- **Key set** — images and video both go to `gen.pollinations.ai`, with the full
  model list (`flux`, `zimage`, `nanobanana`, `seedream5`, … / `veo`, `wan`,
  `seedance-pro`, `nova-reel`, …).

Registration is free at <https://enter.pollinations.ai/keys>. Getting a key is the
single highest-value thing you can do here: it unlocks video and drops the image
throttle from 15s to ~3s.

## Setup

Already wired up in this repo's `.mcp.json`, so it loads in any session opened here.
To add video, export a key before starting Claude Code:

```bash
export POLLINATIONS_KEY=sk_your_key_here
```

Use it in any other project by copying the `mcpServers.pollinations` block into that
project's `.mcp.json` and pointing `args` at this `server.py`.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `POLLINATIONS_KEY` | *(unset)* | API key. Unset = anonymous image-only mode. |
| `POLLINATIONS_OUTPUT_DIR` | `./generated-media` | Where media is written. |
| `POLLINATIONS_TIMEOUT` | `300` | Per-request timeout, seconds. Video is slow. |
| `POLLINATIONS_MIN_INTERVAL` | `3` keyed / `15` anon | Client-side spacing between requests. |

## Design notes

- **Zero dependencies.** Python 3.9+ standard library only (`urllib`, `json`, `base64`).
- **Writes cannot escape the output directory.** Filenames are slugified and the
  resolved path is checked against `POLLINATIONS_OUTPUT_DIR`; `../../etc/passwd` as an
  `output_name` lands harmlessly inside the output dir.
- **Content types are verified before saving.** An HTML error page or a JSON error body
  is reported as an error, never written to disk as a `.jpg` that will not open.
- **Tool failures are `isError` results, not JSON-RPC protocol errors,** so the model
  reads what went wrong and adjusts instead of the session breaking.
- **Rate limits are respected client-side,** with retry-and-backoff on 429/5xx and
  distinct messages for 401 (bad key), 402 (out of balance) and 429 (throttled).
- **Large images are not inlined.** Anything over 3 MB is referenced by path only,
  rather than pushing a huge base64 blob through the context window.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

41 tests, all hermetic — every HTTP call is stubbed, so the suite passes offline.
They cover path-traversal refusal, URL routing between the two hosts, content-type
rejection, error-message mapping, and the MCP handshake.

## Known limits

- **Not verified against the live API from this session.** The environment that built
  this blocks `image.pollinations.ai` and `text.pollinations.ai` at the egress proxy
  (403 on CONNECT), so the tests are hermetic by necessity as well as by preference.
  The URL shapes are taken from the current published `APIDOCS.md`; the first real
  call from an unrestricted machine is still the thing that proves it.
- Anonymous image quality and model choice are whatever the legacy host currently
  defaults to — you do not get to pick from the full catalogue without a key.
- No streaming or progress reporting: a video call blocks until the MP4 arrives.
