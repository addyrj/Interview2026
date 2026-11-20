---

# 11. Building MCP Server (Node.js)
# हिंदी में: Node.js में MCP Server बनाना
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `@modelcontextprotocol/sdk` 1.32.2, `zod` 4.6.7, Node v24.2.0 (server + Node client), and `mcp` 1.30.0 + `fastapi` 0.163.0 (Python side). The Node server ran over stdio, tested by both a Node client and a Python FastAPI client. Not run: Streamable HTTP in Node and any real LLM host (needs an API key).

---

## 🔵 Simple Definition (2-3 lines)
A Node.js MCP server uses `McpServer` from `@modelcontextprotocol/sdk`, registers tools, resources and prompts with `zod` schemas, and connects a `StdioServerTransport`. It speaks exactly the same protocol as a Python server, so any host or framework can use it. Choose Node when your team or your existing business code is in JavaScript/TypeScript.

## 🔵 सरल परिभाषा (Hindi)
Node.js MCP server `@modelcontextprotocol/sdk` का `McpServer` इस्तेमाल करता है, `zod` schemas के साथ tools, resources और prompts register करता है और `StdioServerTransport` जोड़ता है। यह Python server जैसा ही protocol बोलता है, इसलिए कोई भी host या framework इसे इस्तेमाल कर सकता है। जब आपकी team या मौजूदा business code JavaScript/TypeScript में हो तब Node चुनें।

---

## 🔴 Problem it Solves
Many companies keep pricing, tariff and order logic in Node/TypeScript services. Rewriting it in Python only to expose it to an agent duplicates logic. An MCP server in Node wraps the existing modules once and exposes them to a Python agent (LangGraph, CrewAI, OpenAI Agents SDK, AutoGen), Claude Desktop and IDEs, with no language lock-in.

## 🔴 यह क्यों बना? (Hindi)
कई companies की pricing, tariff और order logic Node/TypeScript services में होती है। उसे सिर्फ़ agent के लिए Python में दोबारा लिखना logic दोहराना है। Node में MCP server मौजूदा modules को एक बार wrap करके Python agent (LangGraph, CrewAI, OpenAI Agents SDK, AutoGen), Claude Desktop और IDEs को देता है, भाषा की बंदिश नहीं रहती।

---

## 🟢 How it Works

```
Step 1 -> npm init -y && npm i @modelcontextprotocol/sdk zod     (ESM: use .mjs or "type": "module")
Step 2 -> const server = new McpServer({ name, version }, { instructions })
Step 3 -> server.registerTool(name, { title, description, inputSchema: {zod shape}, outputSchema, annotations }, handler)
Step 4 -> server.registerResource(name, new ResourceTemplate("uri/{x}", { list: undefined }), meta, handler)
Step 5 -> server.registerPrompt(name, { argsSchema }, handler)
Step 6 -> await server.connect(new StdioServerTransport())
Step 7 -> NEVER console.log (stdout = protocol) -> use console.error
Step 8 -> test with a client: Node `Client` + `StdioClientTransport`, or a Python `stdio_client`
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> npm init -y && npm i @modelcontextprotocol/sdk zod     (ESM: .mjs या "type": "module")
Step 2 -> const server = new McpServer({ name, version }, { instructions })
Step 3 -> server.registerTool(name, { title, description, inputSchema: {zod shape}, outputSchema, annotations }, handler)
Step 4 -> server.registerResource(name, new ResourceTemplate("uri/{x}", { list: undefined }), meta, handler)
Step 5 -> server.registerPrompt(name, { argsSchema }, handler)
Step 6 -> await server.connect(new StdioServerTransport())
Step 7 -> कभी console.log नहीं (stdout = protocol) -> console.error इस्तेमाल करें
Step 8 -> client से test करें: Node `Client` + `StdioClientTransport`, या Python `stdio_client`
```

---

## 🟡 Real World Example
**Tariff Agent**: the customs team's existing duty calculator is a Node module. A thin `tariff-server.mjs` wraps it as `get_duty_rate`. The Python FastAPI agent spawns the Node process over stdio and calls it through the `mcp` client, so the Node calculator stays the single source of truth. Invalid HS codes are rejected by the zod `regex` before the handler runs.

## 🟡 Real Example Hindi mein
**Tariff Agent**: customs team का मौजूदा duty calculator Node module है। एक पतली `tariff-server.mjs` उसे `get_duty_rate` के रूप में wrap करती है। Python FastAPI agent Node process को stdio पर spawn करके `mcp` client से call करता है, इसलिए Node calculator ही एकमात्र source of truth रहता है। गलत HS code को handler से पहले zod का `regex` ही reject कर देता है।

---

## 💻 Code Example — Basic
```javascript
// server.mjs - minimal Node MCP server (ran over stdio)
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";          // high-level server class
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";   // stdio transport
import { z } from "zod";                                                        // schema library used by the SDK

const server = new McpServer({ name: "tariff-node", version: "1.0.0" });        // server identity
const RATES = { "8517": 0, "6403": 10 };                                        // demo data

server.tool("get_duty_rate", "Duty percent for an HS code", { hs_code: z.string() },   // name, description, zod shape
  async ({ hs_code }) => {                                                      // handler gets validated args
    if (!(hs_code in RATES)) {                                                  // business error
      return { isError: true, content: [{ type: "text", text: `unknown HS code ${hs_code}` }] };   // readable by the LLM
    }
    return { content: [{ type: "text", text: String(RATES[hs_code]) }] };       // success: text content
  });

await server.connect(new StdioServerTransport());                               // start serving on stdin/stdout
```
Ran with a Python client: tools listed `['get_duty_rate']`, code 6403 returned `10`, an unknown code returned `isError True`. (`server.tool(...)` worked in 1.32.2 for this run; the newer `registerTool` shown below is what the advanced example uses - check the SDK changelog before depending on either.)

## 💻 Code Example — Advanced
```javascript
// tariff-server.mjs - typed input/output, annotations, resource template, prompt, stderr logging (ran)
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";   // server + template helper
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";        // transport
import { z } from "zod";                                                                  // validation

const log = (...args) => console.error("[tariff]", ...args);       // stderr only: stdout is the protocol channel
const RATES = new Map([["8517", 0], ["6403", 10], ["6109", 12]]);   // replace with your existing module/DB

const server = new McpServer(                                       // create server
  { name: "tariff-node", version: "1.0.0" },                        // name + version
  { instructions: "Look up customs duty rates by 4-digit HS code." },   // hint shown to hosts/LLMs
);

server.registerTool(                                                // tool with full metadata
  "get_duty_rate",
  {
    title: "Duty lookup",                                           // UI name
    description: "Return the duty percent for a 4-digit HS code, e.g. 6403.",   // LLM-visible text
    inputSchema: { hs_code: z.string().regex(/^\d{4}$/, "hs_code must be 4 digits") },   // validated BEFORE handler
    outputSchema: { hs_code: z.string(), rate_pct: z.number() },    // typed result
    annotations: { readOnlyHint: true, idempotentHint: true },      // hints, not security
  },
  async ({ hs_code }) => {                                          // async handler
    if (!RATES.has(hs_code)) {                                      // unknown code
      return { isError: true, content: [{ type: "text", text: `unknown HS code ${hs_code}; known: ${[...RATES.keys()].sort().join(", ")}` }] };   // fix-it message
    }
    log("lookup", hs_code);                                         // audit log (stderr)
    const out = { hs_code, rate_pct: RATES.get(hs_code) };          // structured result
    return { content: [{ type: "text", text: JSON.stringify(out) }], structuredContent: out };   // text + typed
  },
);

server.registerResource(                                            // resource template
  "rates",
  new ResourceTemplate("tariff://rates/{hs_code}", { list: undefined }),   // no listing, read by URI
  { title: "Rate", mimeType: "text/plain" },                        // metadata
  async (uri, { hs_code }) => ({ contents: [{ uri: uri.href, text: `${hs_code}: ${RATES.get(hs_code) ?? "unknown"}` }] }),   // read handler
);

server.registerPrompt(                                              // user-controlled template
  "review",
  { title: "Review", argsSchema: { hs_code: z.string() } },
  ({ hs_code }) => ({ messages: [{ role: "user", content: { type: "text", text: `Review classification ${hs_code}` } }] }),
);

await server.connect(new StdioServerTransport());                   // serve
log("ready on stdio");                                              // visible in host logs
```
Node client test (ran: printed the tool name, `{ hs_code: '6403', rate_pct: 10 }`, `true unknown HS code 9999; known: 6109, 6403, 8517`, an `MCP error -32602: Input validation error` for `"64"`, and `8517: 0` from the resource):
```javascript
// client-test.mjs - spawn the server like a host would
import { Client } from "@modelcontextprotocol/sdk/client/index.js";            // client class
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";   // spawns the process

const transport = new StdioClientTransport({ command: "node", args: ["tariff-server.mjs"] });   // how to launch
const client = new Client({ name: "test-client", version: "1.0.0" });        // client identity
await client.connect(transport);                                              // handshake
console.log((await client.listTools()).tools.map((t) => t.name));             // discovery
const ok = await client.callTool({ name: "get_duty_rate", arguments: { hs_code: "6403" } });   // success
console.log(ok.structuredContent);                                            // typed result
const bad = await client.callTool({ name: "get_duty_rate", arguments: { hs_code: "9999" } });   // handled error
console.log(bad.isError, bad.content[0].text);                                // true + message
await client.close();                                                         // shutdown
```
FastAPI consumer of the Node server (ran with `TestClient`; async, typed, error mapped to HTTP 422):
```python
# nodebridge.py - Python FastAPI service calling the Node MCP server
from collections.abc import AsyncIterator                   # lifespan type
from contextlib import asynccontextmanager                  # lifespan helper
from fastapi import FastAPI, HTTPException                  # web layer
from mcp import ClientSession, StdioServerParameters        # MCP client
from mcp.client.stdio import stdio_client                   # stdio transport

PARAMS = StdioServerParameters(command="node", args=["node/tariff-server.mjs"])   # launch the Node server

@asynccontextmanager                                        # keep ONE session for the app lifetime
async def lifespan(app: FastAPI) -> AsyncIterator[None]:    # startup/shutdown
    async with stdio_client(PARAMS) as (read, write):       # spawn Node process
        async with ClientSession(read, write) as session:   # protocol session
            await session.initialize()                      # handshake
            app.state.mcp = session                         # share with handlers
            yield                                           # serve requests

app = FastAPI(lifespan=lifespan)                            # app

@app.get("/duty/{hs_code}")                                 # REST facade over the MCP tool
async def duty(hs_code: str) -> dict[str, float | str]:     # typed response
    res = await app.state.mcp.call_tool("get_duty_rate", {"hs_code": hs_code})   # MCP call
    if res.isError:                                         # tool-level failure
        raise HTTPException(status_code=422, detail=res.content[0].text)   # surface the message
    return res.structuredContent                            # typed JSON from the tool
```
Output: `{'hs_code': '6403', 'rate_pct': 10.0}`, then `422` for `9999` and `422` for `64`. Token usage: zod descriptions and regex messages become part of the tool schema sent to the LLM, so keep them short.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Can use a Node MCP server | Yes via the MCP adapter with stdio params (verify adapter docs) | Yes via MCP integration (verify) | Yes, `MCPServerStdio(params={"command": "node", "args": [...]})` (class import verified earlier) | Yes via stdio params (verify) |
| Needs Node on the host machine | Yes (spawns `node`) | Yes | Yes | Yes |
| Tool schema source | zod -> JSON Schema | same | same | same |

Because MCP is a protocol, none of the four frameworks care whether the server is Python or Node.

---

## ⚠️ Common Mistakes
❌ Mistake 1: `console.log` in the server.
✅ Correct: `console.error` (stderr). stdout is JSON-RPC only.

❌ Mistake 2: Mixing CommonJS and ESM imports (the SDK uses `.js` subpaths).
✅ Correct: Use `.mjs` or `"type": "module"` and import with the `.js` suffix as shown.

❌ Mistake 3: Throwing for expected errors.
✅ Correct: Return `{ isError: true, content: [...] }` with a fix-it message. Remember validation failures from zod come back as an `isError` result with `MCP error -32602` in our run.

❌ Mistake 4: Hard-coding absolute `node`/script paths in host configs without checking the host's PATH.
✅ Correct: Use absolute paths to `node` and the script; desktop apps often do not load your shell profile.

❌ Mistake 5: Copying API shapes from old blog posts.
✅ Correct: SDKs evolve (`tool` vs `registerTool`). Check the installed version's exports/types.

---

## 🧠 Tricky Interview Question
"A Python agent calls your Node MCP server 50 times per request. Latency is terrible. Where do you look?"

Answer: First, whether a new Node process is spawned per call: a stdio server should be started once per application (FastAPI lifespan) and reused, since process start and handshake cost far more than a call. Second, serialize concurrency: one stdio pipe handles requests in order unless the server is async, so batch lookups into one tool (`get_duty_rates(codes[])`) or run several server processes behind a pool. Third, the number of LLM round trips (50 sequential tool calls means 50 model turns) - fix by batching in the tool or using parallel tool calls. (We did not measure latency here; profile before changing.)

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why zod?
A1: The SDK takes zod shapes to validate input and generate JSON Schema for `tools/list`.

Q2: [Medium] How does a Python client talk to a Node server?
A2: Via stdio: the Python `stdio_client` spawns `node server.mjs` and both speak JSON-RPC over stdin/stdout. We ran exactly this.

Q3: [Hard] Where do logs go and why?
A3: stderr. stdout carries protocol messages; any extra output corrupts framing.

Q4: [Hard] How do invalid inputs surface?
A4: zod validation fails before the handler; the SDK returned an `isError` result with `MCP error -32602: Input validation error` text in our run (check this behaviour per SDK version).

Q5: [System Design] Expose a legacy Node pricing service to 3 agent frameworks.
A5: One MCP wrapper server, typed schemas, stdio for local use and Streamable HTTP for shared use (not run here), auth and rate limits at the HTTP layer, contract tests with a client in CI.

---

## 💰 Cost Impact
No LLM cost from the server itself. Compute: a Node process idles at tens of MB (approximate; measure). LLM cost depends on tool-schema size and result size: keep `description` short, return only needed fields, and batch lookups so the model makes fewer turns (each turn re-sends history, which dominates cost).

---

## 🔷 When to Use
✅ Use when:
- Your business logic already lives in Node/TypeScript
- You want one wrapper for many agent frameworks

❌ Avoid when:
- A Python-only team would have to maintain Node just for one tool
- You need Python libraries (pandas, ML) in the tool - keep it in Python

---

## 📊 Visual Diagram
```
 Python FastAPI agent (LangGraph / CrewAI / OpenAI SDK / AutoGen)
        |  mcp ClientSession (stdio, started once in lifespan)
        v
   [ node tariff-server.mjs ]
     zod validate -> handler -> existing JS modules / DB
        |
        +-- stdout: JSON-RPC only
        +-- stderr: logs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| McpServer | High-level Node server class | Node का high-level server class |
| zod | Schema validation library | schema validation library |
| StdioServerTransport | stdin/stdout transport | stdin/stdout transport |
| registerTool | Register a tool with metadata | metadata के साथ tool register करना |
| ESM | JavaScript modules (`import`) | JavaScript modules |

---

## ⚡ 3-Line Summary
English: A Node MCP server is `McpServer` plus zod schemas and a stdio transport. It is fully interchangeable with a Python server from the client's view. Log to stderr and test with a real client.
Hindi: Node MCP server यानी `McpServer`, zod schemas और stdio transport। Client के नज़रिए से यह Python server जैसा ही है। Logs stderr पर रखें और असली client से test करें।

---

## ➡️ Next Topic
**012. MCP Server with FastAPI** - serve your MCP server over HTTP inside a FastAPI app with lifespan, health checks and auth.

---
