---

# 7. MCP Resources — Deep Dive
# हिंदी में: MCP Resources — गहराई से
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0 (Python), `@modelcontextprotocol/sdk` 1.32.2 (Node), `fastapi` 0.163.0. Resource listing, templates, text/blob reads and error cases ran offline over an in-memory connection; the Node resource template ran over stdio. No LLM was called (needs an API key).

---

## 🔵 Simple Definition (2-3 lines)
A resource is read-only data a server exposes under a URI such as `tariff://schedule/current`. Clients discover them with `resources/list` (fixed URIs) and `resources/templates/list` (URI patterns like `tariff://docs/{name}`) and load them with `resources/read`. The host application, not the model, normally decides which ones to attach to the conversation.

## 🔵 सरल परिभाषा (Hindi)
Resource एक read-only data है जिसे server किसी URI (जैसे `tariff://schedule/current`) पर देता है। Client `resources/list` (fixed URIs) और `resources/templates/list` (pattern जैसे `tariff://docs/{name}`) से उन्हें खोजता है और `resources/read` से लोड करता है। कौन सा resource chat में जोड़ना है, यह आम तौर पर host application तय करता है, model नहीं।

---

## 🔴 Problem it Solves
If documents, schemas and config are exposed only as tools, the model must call a tool on every question, tool results pile up in history and nothing tells the UI "this is a file you can attach". Resources give a standard addressable catalogue of context (files, DB rows, logs, API responses) with MIME types, so the app can show a picker, cache by URI and control exactly what enters the prompt.

## 🔴 यह क्यों बना? (Hindi)
अगर documents, schemas और config सिर्फ़ tools से दिए जाएँ तो model को हर सवाल पर tool call करनी पड़ती है, नतीजे history में जमा होते हैं और UI को पता नहीं चलता कि "यह file attach की जा सकती है"। Resources context (files, DB rows, logs, API responses) की standard addressable सूची देते हैं, MIME type के साथ, ताकि app picker दिखा सके, URI से cache कर सके और तय कर सके कि prompt में क्या जाए।

---

## 🟢 How it Works

```
Step 1 -> server declares the resources capability at initialize
Step 2 -> client: resources/list           -> fixed resources (uri, name, mimeType)
Step 3 -> client: resources/templates/list -> templates like tariff://docs/{name}
Step 4 -> user / app picks one (or app auto-attaches by rule)
Step 5 -> client: resources/read {uri}     -> contents[]: text OR base64 blob + mimeType
Step 6 -> host puts the text in the LLM context (or shows it in the UI)
Step 7 -> unknown / invalid URI -> JSON-RPC error (McpError), not an LLM-readable tool result
```

Content shapes: `TextResourceContents` (`text`) for text, `BlobResourceContents` (`blob`, base64) for binary such as images/PDF.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> server initialize में resources capability बताता है
Step 2 -> client: resources/list           -> fixed resources (uri, name, mimeType)
Step 3 -> client: resources/templates/list -> templates जैसे tariff://docs/{name}
Step 4 -> user / app एक चुनता है (या app नियम से अपने-आप attach करता है)
Step 5 -> client: resources/read {uri}     -> contents[]: text या base64 blob + mimeType
Step 6 -> host text को LLM context में डालता है (या UI में दिखाता है)
Step 7 -> unknown / गलत URI -> JSON-RPC error (McpError), tool जैसा LLM-readable result नहीं
```

Text के लिए `TextResourceContents` (`text`), और binary (image/PDF) के लिए `BlobResourceContents` (`blob`, base64)।

---

## 🟡 Real World Example
**Tariff Agent**: `tariff://schedule/current` is a fixed resource (the current rate schedule, JSON). `tariff://docs/{name}` is a template that serves customs circulars from a folder. In the desktop UI the analyst attaches `tariff://docs/schedule-2026.md` to the chat; the agent then answers questions using that text without calling any tool.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `tariff://schedule/current` एक fixed resource है (मौजूदा rate schedule, JSON)। `tariff://docs/{name}` एक template है जो folder से customs circulars देता है। Desktop UI में analyst `tariff://docs/schedule-2026.md` को chat में attach करता है; फिर agent बिना कोई tool call किए उसी text से जवाब देता है।

---

## 💻 Code Example — Basic
```python
# res_basic.py - fixed + templated resource and a binary resource (ran offline)
from mcp.server.fastmcp import FastMCP                      # server helper

mcp = FastMCP("tariff-res")                                 # server name

@mcp.resource("tariff://schedule/current", mime_type="application/json")   # FIXED URI -> shows in resources/list
def schedule() -> str:                                      # returns text
    return '{"version": "2026-01"}'                         # JSON text body

@mcp.resource("tariff://rates/{hs_code}", mime_type="text/plain")   # TEMPLATE -> shows in templates/list
def rate(hs_code: str) -> str:                              # {hs_code} bound from the URI
    return f"{hs_code}: 10%"                                # demo body

@mcp.resource("tariff://logo", mime_type="image/png")       # binary resource
def logo() -> bytes:                                        # bytes -> sent as base64 blob
    return b"\x89PNG-fake-bytes"                            # demo bytes (not a real image)

if __name__ == "__main__":                                  # entry
    mcp.run()                                               # stdio
```
Verified with a client: `list_resources()` showed the fixed ones, `list_resource_templates()` showed `tariff://rates/{hs_code}`, reading the logo returned a `BlobResourceContents` with `image/png`, and reading `tariff://nope` raised `McpError: Unknown resource: tariff://nope`.

## 💻 Code Example — Advanced
```python
# res_adv.py - folder-backed template with path-traversal protection + error handling (ran offline)
import asyncio                                              # demo runtime
import json                                                 # build JSON text
import tempfile                                             # throwaway docs folder for the demo
from pathlib import Path                                    # safe path handling
from mcp.server.fastmcp import FastMCP                      # server
from mcp.shared.memory import create_connected_server_and_client_session as connect   # in-memory client

DOCS: Path = Path(tempfile.mkdtemp())                       # pretend this is /srv/customs-docs
(DOCS / "schedule-2026.md").write_text("# Tariff schedule 2026\nChapter 85: 0%")   # sample doc

mcp = FastMCP("tariff-resources")                           # server

@mcp.resource("tariff://schedule/current", mime_type="application/json", title="Current schedule")   # fixed resource with a title
def current() -> str:                                       # sync handler is fine for cheap data
    return json.dumps({"version": "2026-01", "chapters": 97})   # JSON string

@mcp.resource("tariff://docs/{name}", mime_type="text/markdown")   # template: one URI per file
def doc(name: str) -> str:                                  # `name` comes from untrusted input (LLM/user)
    target: Path = (DOCS / name).resolve()                  # resolve ".." and symlinks first
    if DOCS.resolve() not in target.parents:                # must stay inside the docs folder
        raise ValueError("path outside docs folder")        # block path traversal
    if not target.is_file():                                # missing file
        raise ValueError(f"no such doc: {name}")            # clear error for logs
    return target.read_text()                               # use aiofiles / to_thread for big files

async def main() -> None:                                   # demo client
    async with connect(mcp._mcp_server) as c:               # connect in memory
        print([(r.name, str(r.uri), r.mimeType) for r in (await c.list_resources()).resources])   # fixed list
        print([t.uriTemplate for t in (await c.list_resource_templates()).resourceTemplates])     # templates
        print((await c.read_resource("tariff://docs/schedule-2026.md")).contents[0].text.splitlines()[0])   # first line
        for bad in ("tariff://docs/..%2Fsecret", "tariff://docs/missing.md", "tariff://nope"):   # failure paths
            try:                                            # resource errors are exceptions, not isError results
                await c.read_resource(bad)                  # should fail
            except Exception as e:                          # McpError
                print("ERR", type(e).__name__, str(e)[:60]) # all three raised McpError

asyncio.run(main())                                         # run
```
FastAPI integration: mount the same `mcp` with `app.mount("/tariff", mcp.streamable_http_app())` (see topic 012), and put authentication middleware in FastAPI so each user only sees their own resources. Node SDK equivalent (ran over stdio): `server.registerResource("rates", new ResourceTemplate("tariff://rates/{hs_code}", { list: undefined }), { mimeType: "text/plain" }, async (uri, { hs_code }) => ({ contents: [{ uri: uri.href, text: ... }] }))`. Token usage: a resource costs tokens only when the host places its text in the prompt, but then it is re-sent each turn, so attach small slices.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Auto-load MCP resources | Adapter has helpers to fetch resources (verify current docs) | Not typical | Not a first-class concept (verify) | Not typical |
| Who picks the resource | Your graph code decides what to read | Your task code | Your app code | Your app code |
| Easiest path | Call `session.read_resource(uri)` and add text to state | Same | Same, or wrap as a tool | Same |

In practice with agent frameworks you either read the resource yourself and inject it into the prompt/state, or wrap it in a small tool so the model can pull it on demand.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Building the file path directly from the URI template (`open(DOCS + name)`).
✅ Correct: Resolve the path and verify it stays inside the base folder (path traversal is a real vulnerability).

❌ Mistake 2: Expecting the model to browse resources by itself.
✅ Correct: Resources are application-controlled. If the model must fetch them, add a tool that reads the same data.

❌ Mistake 3: Returning huge files as one resource.
✅ Correct: Split by section/page with a template (`tariff://docs/{name}/{page}`) and use accurate MIME types.

❌ Mistake 4: Expecting an `isError` result when the URI is wrong.
✅ Correct: Resource failures are protocol errors (`McpError`). Catch them in the host.

---

## 🧠 Tricky Interview Question
"A customs circular changes mid-conversation. How does the agent see the new version?"

Answer: The text already read is a copy in the LLM context and will not update. The protocol offers subscriptions and `list_changed` notifications for servers that support them, so the host can re-read the URI. But many clients ignore them, so a robust design versions the URI or content (`tariff://docs/schedule-2026-v3`), tells the user a newer version exists, and re-reads at the start of each task rather than relying on live updates. (Subscription behaviour was not run here; check the spec/SDK for the exact API.)

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is a resource template?
A1: A URI pattern with variables, like `tariff://docs/{name}`, listed via `resources/templates/list`; the server resolves any matching URI on read.

Q2: [Medium] Resource vs tool?
A2: Resources are read-only, addressable context controlled by the app; tools are actions/queries controlled by the model. Use a tool when the model must decide to fetch or when there are side effects.

Q3: [Hard] How do you stop path traversal in a file-backed resource?
A3: Resolve the final path and require that the base directory is among its parents (`Path.resolve()` and `parents`), reject symlinks out of the tree, never concatenate raw strings, and apply per-user authorization.

Q4: [Hard] How are binary resources sent?
A4: As `BlobResourceContents` with base64 `blob` and a `mimeType`; text uses `TextResourceContents`.

Q5: [System Design] Serve 10,000 customs PDFs to an agent.
A5: Do not list 10,000 fixed resources. Use a template plus a search tool that returns URIs; chunk PDFs into text pages; cache by URI; enforce per-user access; attach only the top few chunks to the prompt.

---

## 💰 Cost Impact
A resource is free until placed in the prompt; then it costs input tokens every turn it stays in history (rough English estimate: tokens ~ characters / 4, approximate - measure it). Tips: attach only needed sections, summarise old attachments, use prompt caching for stable documents if your provider supports it (verify), and avoid auto-attaching everything at session start.

---

## 🔷 When to Use
✅ Use when:
- You have documents, schemas, configs or logs to share as context
- The UI should list/attach items and cache by URI

❌ Avoid when:
- The data changes every second (use a tool)
- The action has side effects
- You cannot restrict access per user

---

## 📊 Visual Diagram
```
 +------ HOST ------+                       +------ MCP SERVER ------+
 | UI picker        |--resources/list------>| tariff://schedule/current
 |                  |--templates/list------>| tariff://docs/{name}
 | user attaches    |--resources/read------>| validate -> read file/DB
 |  tariff://docs/  |<--text | blob+mime-----|
 |  schedule-2026.md|                       +------------------------+
 |        |         |
 |        v         |
 |  put text in LLM context (costs tokens every turn)
 +------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Resource | Read-only data at a URI | URI पर read-only data |
| URI template | Pattern with `{variables}` | `{variables}` वाला pattern |
| MIME type | Content type label | content का प्रकार |
| Blob | Base64 binary content | base64 binary data |
| Path traversal | `..` escaping a folder | `..` से folder के बाहर निकलना |

---

## ⚡ 3-Line Summary
English: Resources are URI-addressed, read-only context that the app attaches. Use templates for families of items and validate every parameter. Errors are protocol errors, not LLM-readable results.
Hindi: Resources URI वाले read-only context हैं जिन्हें app attach करता है। Items के परिवार के लिए templates इस्तेमाल करें और हर parameter validate करें। Errors protocol errors हैं, LLM के पढ़ने वाले result नहीं।

---

## ➡️ Next Topic
**008. MCP Prompts - Deep Dive** - reusable, parameterised message templates that users trigger by name.

---
