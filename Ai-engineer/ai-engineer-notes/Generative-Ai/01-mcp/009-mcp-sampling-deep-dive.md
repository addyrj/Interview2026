---

# 9. MCP Sampling — Deep Dive
# हिंदी में: MCP Sampling — गहराई से
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0 (Python), `fastapi` 0.163.0. Sampling was exercised over stdio and over an in-memory connection with a FAKE LLM callback, so the protocol path ran but no real model was called (needs an API key). Anything about real model output, latency or cost is not measured.

---

## 🔵 Simple Definition (2-3 lines)
Sampling lets an MCP **server** ask the **client's** LLM to generate text (`sampling/createMessage`). The server sends messages, a system prompt, a `max_tokens` cap and model preferences; the host reviews it (ideally with the user), runs its own model and returns the completion. The server never needs an API key.

## 🔵 सरल परिभाषा (Hindi)
Sampling में MCP **server**, **client** के LLM से text generate करवाता है (`sampling/createMessage`)। Server messages, system prompt, `max_tokens` की सीमा और model preferences भेजता है; host (आदर्श रूप से user के साथ) उसकी समीक्षा करता है, अपना model चलाता है और completion लौटाता है। Server को API key की ज़रूरत नहीं पड़ती।

---

## 🔴 Problem it Solves
A server tool sometimes needs language understanding (classify a product, summarise a document). Without sampling the server must embed its own LLM key: every server duplicates secrets, billing and rate limits, the user cannot see or approve those calls, and the host's model choice is ignored. Sampling keeps the model, the budget and the consent with the host.

## 🔴 यह क्यों बना? (Hindi)
Server के tool को कभी language समझ चाहिए (product classify करना, document summarize करना)। Sampling के बिना server को अपनी LLM key रखनी पड़ती है: हर server में secrets, billing और rate limits दोहराए जाते हैं, user ये calls देख या approve नहीं कर पाता, और host का model चुनाव अनदेखा हो जाता है। Sampling में model, budget और consent host के पास रहते हैं।

---

## 🟢 How it Works

```
Step 1 -> client declares the sampling capability at initialize (it passes a sampling_callback)
Step 2 -> LLM calls tool classify(description)                 [client -> server]
Step 3 -> server runs the tool and needs an LLM:
          ctx.session.create_message(messages, system_prompt, max_tokens, model_preferences)
                                                               [server -> client]
Step 4 -> host: show request to user (human in the loop), clamp max_tokens, pick a model
Step 5 -> host runs ITS LLM -> returns CreateMessageResult(role, content, model, stopReason)
          (or ErrorData if the user/host refuses)
Step 6 -> tool finishes with that text and returns its own result to the first LLM
```

If the client has no sampling handler the server's call fails (we saw `Sampling not supported`).

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> client initialize में sampling capability बताता है (sampling_callback देता है)
Step 2 -> LLM tool classify(description) call करता है          [client -> server]
Step 3 -> server tool चलाता है और उसे LLM चाहिए:
          ctx.session.create_message(messages, system_prompt, max_tokens, model_preferences)
                                                               [server -> client]
Step 4 -> host: request user को दिखाता है, max_tokens सीमित करता है, model चुनता है
Step 5 -> host अपना LLM चलाता है -> CreateMessageResult लौटाता है
          (या user/host मना करे तो ErrorData)
Step 6 -> tool उस text से अपना result बनाकर पहले LLM को लौटाता है
```

अगर client के पास sampling handler नहीं है तो server की call fail होती है (हमने `Sampling not supported` देखा)।

---

## 🟡 Real World Example
**Tariff Agent**: the shared `tariff` MCP server has a `classify(description)` tool that suggests an HS code. Instead of holding an OpenAI/Anthropic key, it asks the host via sampling. The FastAPI host clamps `max_tokens` to 100, asks the analyst "allow this request?", runs its own model, and logs the request for audit. A different team's host can plug in a different model without changing the server.

## 🟡 Real Example Hindi mein
**Tariff Agent**: साझा `tariff` MCP server में `classify(description)` tool है जो HS code सुझाता है। OpenAI/Anthropic key रखने की जगह वह sampling से host से पूछता है। FastAPI host `max_tokens` को 100 पर सीमित करता है, analyst से "अनुमति दें?" पूछता है, अपना model चलाता है और audit के लिए request log करता है। दूसरी team का host server बदले बिना अलग model लगा सकता है।

---

## 💻 Code Example — Basic
```python
# sampling_basic.py - server tool that uses sampling + a client with a FAKE LLM (ran over stdio; save as one file and run)
import asyncio                                              # runtime
import sys                                                  # to re-launch this same file as the server
from mcp import ClientSession, StdioServerParameters, types   # client types
from mcp.client.stdio import stdio_client                   # stdio transport
from mcp.server.fastmcp import FastMCP, Context            # server helper
from mcp.server.session import ServerSession               # typed session for Context
from mcp.shared.context import RequestContext              # type of the callback's first arg

mcp = FastMCP("tariff-server")                              # server

@mcp.tool()                                                 # tool that needs an LLM
async def classify(description: str, ctx: Context[ServerSession, None]) -> str:   # ctx exposes the session
    """Ask the CLIENT's LLM (sampling) to classify."""
    res = await ctx.session.create_message(                 # server -> client request
        messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text=f"HS code for: {description}"))],   # prompt
        max_tokens=50)                                      # cap the host's spend
    return res.content.text if res.content.type == "text" else "?"   # only text handled

async def sampling_cb(context: RequestContext[ClientSession, None], params: types.CreateMessageRequestParams) -> types.CreateMessageResult:   # host-side handler
    return types.CreateMessageResult(role="assistant", content=types.TextContent(type="text", text="8517 (fake LLM)"), model="fake", stopReason="endTurn")   # canned answer, NOT a real model

async def client_main() -> None:                            # host side of the demo
    params = StdioServerParameters(command=sys.executable, args=[__file__, "server"])   # spawn this file as the server
    async with stdio_client(params) as (r, w):              # start server process
        async with ClientSession(r, w, sampling_callback=sampling_cb) as s:   # enabling sampling = passing the callback
            await s.initialize()                            # handshake advertises sampling
            res = await s.call_tool("classify", {"description": "phone"})   # tool triggers sampling
            print(res.content[0].text)                      # -> 8517 (fake LLM)

if __name__ == "__main__":                                  # entry
    if len(sys.argv) > 1 and sys.argv[1] == "server":       # child process mode
        mcp.run()                                           # stdio server
    else:                                                   # parent mode
        asyncio.run(client_main())                          # run host demo
```
Equivalent split-file version (server.py + client.py) ran and printed `8517 (fake LLM)`.

## 💻 Code Example — Advanced
```python
# sampling_adv.py - FastAPI host with approval gate, max_tokens clamp, pluggable LLM, error mapping (ran with a fake LLM)
import asyncio                                              # run async demo
from collections.abc import Awaitable, Callable             # type aliases
from fastapi import FastAPI                                 # web host
from fastapi.testclient import TestClient                   # test without a network
from mcp import types                                       # protocol types
from mcp.client.session import ClientSession                # session type
from mcp.server.fastmcp import Context, FastMCP             # server
from mcp.server.session import ServerSession                # typed session
from mcp.shared.context import RequestContext               # callback context type
from mcp.shared.memory import create_connected_server_and_client_session as connect   # in-memory link

mcp = FastMCP("tariff-sampling")                            # server

@mcp.tool()                                                 # tool using sampling
async def classify(description: str, ctx: Context[ServerSession, None]) -> str:   # typed
    """Suggest an HS code by asking the host's LLM."""
    result = await ctx.session.create_message(              # sampling request
        messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text=f"HS code for: {description}"))],
        max_tokens=500,                                     # server ASKS for 500 ...
        system_prompt="Answer with a 4 digit HS code only.")
    if result.content.type != "text":                       # we only support text answers
        raise ValueError("expected text from sampling")     # -> isError result for the caller
    return result.content.text                              # the model's answer

LLM = Callable[[str, int], Awaitable[str]]                  # (prompt, max_tokens) -> text
MAX_TOKENS_CAP: int = 100                                   # ... but the HOST decides the real cap

def make_handler(llm: LLM, approve: Callable[[str], bool]):   # build a sampling callback
    async def handler(context: RequestContext[ClientSession, None], params: types.CreateMessageRequestParams) -> types.CreateMessageResult | types.ErrorData:
        text = " ".join(m.content.text for m in params.messages if m.content.type == "text")   # flatten prompt
        if not approve(text):                               # human/policy gate
            return types.ErrorData(code=types.INVALID_REQUEST, message="user rejected sampling request")   # refuse cleanly
        try:                                                # model calls can fail
            answer = await llm(text, min(params.maxTokens, MAX_TOKENS_CAP))   # clamp spend
        except Exception as exc:                            # quota, timeout, provider error
            return types.ErrorData(code=types.INTERNAL_ERROR, message=f"llm failed: {exc}")   # report to server
        return types.CreateMessageResult(role="assistant", content=types.TextContent(type="text", text=answer), model="fake-llm", stopReason="endTurn")   # normal result
    return handler                                          # closure keeps llm/approve

seen: list[int] = []                                        # records caps the "LLM" received
async def fake_llm(prompt: str, max_tokens: int) -> str:    # stand-in for a real async model call
    seen.append(max_tokens)                                 # prove the clamp worked
    return "6403"                                           # canned answer

async def run(handler, desc: str) -> tuple[bool | None, str]:   # one tool call with a given handler
    async with connect(mcp._mcp_server, sampling_callback=handler) as client:   # in production: your long-lived ClientSession
        r = await client.call_tool("classify", {"description": desc})   # call
        return r.isError, r.content[0].text                 # (isError, text)

app = FastAPI()                                             # HTTP facade

@app.post("/classify")                                      # endpoint
async def classify_endpoint(description: str) -> dict[str, str]:   # typed
    is_error, text = await run(make_handler(fake_llm, lambda t: "secret" not in t), description)   # approve everything except 'secret'
    return {"status": "error" if is_error else "ok", "text": text}   # simple envelope

c = TestClient(app)                                         # test client
print(c.post("/classify", params={"description": "leather shoes"}).json(), "max_tokens seen by llm:", seen)
print(c.post("/classify", params={"description": "secret thing"}).json())   # rejected path
```
Ran output: `{'status': 'ok', 'text': '6403'} max_tokens seen by llm: [100]` (server asked 500, host clamped to 100); rejected request -> `{'status': 'error', 'text': 'Error executing tool classify: user rejected sampling request'}`; an LLM exception -> `Error executing tool classify: llm failed: quota exceeded`. In production replace `fake_llm` with your async provider call (not run here - needs an API key). Token usage: sampling spends the HOST's tokens on top of the main agent loop, so budget for it.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Handles server sampling requests | You pass a callback to the raw `mcp` client; adapter support varies (verify) | Not typical (verify) | Not typical (verify) | Not typical (verify) |
| Where the LLM call goes | Your chat model inside the callback | Your LLM config | Your model/provider | Your model client |
| Human approval | `interrupt` before returning | Human input flag (verify) | Approval hooks (verify) | `UserProxyAgent` (verify) |
| Simplest approach | Callback calls `llm.ainvoke` | Same idea | Same idea | Same idea |

Sampling support in high-level agent frameworks is thin; in an interview, show the raw `ClientSession(sampling_callback=...)` hook as above.

---

## ⚠️ Common Mistakes
❌ Mistake 1: Trusting the server's `max_tokens`/system prompt blindly.
✅ Correct: Clamp tokens, review or rewrite the prompt, rate-limit per server. A malicious server can burn your budget.

❌ Mistake 2: Auto-approving every sampling request.
✅ Correct: Show it to the user (or apply a policy), and log it; the spec expects human-in-the-loop control.

❌ Mistake 3: Assuming sampling works everywhere.
✅ Correct: Many hosts do not support it. Check capabilities and keep a fallback.

❌ Mistake 4: Letting sampling answers drive dangerous actions.
✅ Correct: The returned text is model output derived from possibly untrusted content; validate it (for example an HS code must match 4 digits).

---

## 🧠 Tricky Interview Question
"Your MCP server runs statelessly behind 3 replicas. A tool using sampling randomly fails in production but works locally. Why?"

Answer: Sampling is a server-to-client request that needs a live bidirectional channel tied to the original request/session. In stateless HTTP mode, or when the follow-up lands on a different replica, there is no channel to send the request back on, so the call fails or times out (check the SDK docs for your transport; this was not reproduced here). Fixes: use stdio/stateful sessions with sticky routing for sampling tools, or restructure so the host does the LLM step itself and passes the result in as a tool argument.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is sampling?
A1: A server asking the client's LLM for a completion via `sampling/createMessage`, so the server needs no model key.

Q2: [Medium] Who is in control?
A2: The client/host. It can modify or reject the request, choose the model, cap tokens and show it to the user.

Q3: [Hard] How do model preferences work?
A3: The server sends hints (model-name hints) and priorities (cost, speed, intelligence, 0 to 1). They are advisory; the host maps them to a model it has. We verified the client received `hints[0].name` and `intelligencePriority`.

Q4: [Hard] What are the security risks?
A4: Budget burn, prompt injection through server-written prompts, data exfiltration through crafted prompts, and cost attribution. Mitigate with approval, clamps, logging and per-server quotas.

Q5: [System Design] Design a shared server whose 5 tools need an LLM for 3 different hosts.
A5: Use sampling so each host brings its own model/budget; add capability checks and a no-LLM fallback (rules/regex); keep sampling tools off stateless replicas or use sticky sessions; add metrics for sampling requests per server.

---

## 💰 Cost Impact
Each sampling request is a full extra LLM call billed to the host: tokens = prompt tokens + completion (<= `max_tokens`). A cost model: `cost = (prompt_tokens * input_price + completion_tokens * output_price)` per request, multiplied by requests per run; prices from your provider (approximate, public pricing at time of writing - verify). Tips: clamp `max_tokens`, use a cheaper model for classification, cache repeated prompts, and cap sampling calls per session.

---

## 🔷 When to Use
✅ Use when:
- A shared server needs light language help (classify, summarise, extract)
- You want the host to own keys, budget and consent

❌ Avoid when:
- Rules or regex can do it deterministically
- The deployment is stateless HTTP and you did not test sampling there
- The host cannot show approvals for server-initiated LLM calls

---

## 📊 Visual Diagram
```
 LLM(host) --call classify--> HOST --tools/call--> SERVER (tool runs)
                                                      |
                              sampling/createMessage  | needs an LLM
        +<--------------------------------------------+
        |
   [approve? clamp max_tokens=100]  -> HOST's LLM -> "6403"
        |
        +--CreateMessageResult------------------------>+
                                                      |
 LLM(host) <---------- tool result "6403" ------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sampling | Server asks host LLM to generate | server का host LLM से generate करवाना |
| createMessage | The sampling request method | sampling का request method |
| Model preferences | Cost/speed/intelligence hints | model चुनने के संकेत |
| Human in the loop | User approves the request | user की मंज़ूरी |
| stopReason | Why generation ended | generation क्यों रुका |

---

## ⚡ 3-Line Summary
English: Sampling lets a server borrow the host's LLM without owning any key. The host stays in control: approve, clamp tokens, choose the model. Not every client supports it, so always plan a fallback.
Hindi: Sampling server को बिना key के host का LLM इस्तेमाल करने देता है। Control host के पास रहता है: मंज़ूरी, token सीमा, model चुनाव। हर client इसे support नहीं करता, इसलिए fallback ज़रूर रखें।

---

## ➡️ Next Topic
**010. Building MCP Server (Python)** - put tools, resources, prompts and logging together into one clean, testable server.

---
