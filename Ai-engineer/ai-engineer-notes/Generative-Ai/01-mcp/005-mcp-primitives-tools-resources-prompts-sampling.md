---

# 5. MCP Primitives (Tools, Resources, Prompts, Sampling)
# हिंदी में: MCP Primitives (Tools, Resources, Prompts, Sampling)
# Framework: MCP (used by all frameworks)
# Already Known: No

> Verified against: `mcp` 1.30.0 (Python), `@modelcontextprotocol/sdk` 1.32.2 (Node), `fastapi` 0.163.0. Everything below ran offline with an in-memory MCP connection and a fake sampling callback. No real LLM was called (needs an API key). Latency/cost numbers are not measured.

---

## 🔵 Simple Definition (2-3 lines)
MCP has four building blocks. **Tools** are actions the model can call. **Resources** are read-only data the app can load. **Prompts** are reusable message templates the user picks. **Sampling** is the reverse direction: the server asks the client's LLM to generate text. Each has a different "who controls it" rule.

## 🔵 सरल परिभाषा (Hindi)
MCP के चार building blocks हैं। **Tools** वे actions हैं जिन्हें model call करता है। **Resources** read-only data हैं जिन्हें app load करता है। **Prompts** दोबारा इस्तेमाल होने वाले message templates हैं जिन्हें user चुनता है। **Sampling** उल्टी दिशा है: server, client के LLM से text generate करवाता है। हर primitive में "कौन control करता है" अलग है।

---

## 🔴 Problem it Solves
Without separate primitives everything becomes a "tool". Then the model gets read-only reference data, user-triggered workflows and dangerous actions in one flat list, and nobody can tell what is safe to auto-run. Separate primitives give clear control: model-controlled (tools), application-controlled (resources), user-controlled (prompts), and a safe way for servers to use an LLM without holding API keys (sampling).

## 🔴 यह क्यों बना? (Hindi)
अलग primitives न हों तो सब कुछ "tool" बन जाता है। तब model को read-only reference data, user के workflows और खतरनाक actions एक ही flat list में मिलते हैं, और कोई नहीं जान पाता कि क्या अपने-आप चलाना safe है। अलग primitives साफ़ control देते हैं: model-controlled (tools), application-controlled (resources), user-controlled (prompts), और server को API key रखे बिना LLM इस्तेमाल करने का सुरक्षित तरीका (sampling)।

---

## 🟢 How it Works

```
Primitive  | Direction        | Who decides to use it | Typical Tariff Agent use
-----------+------------------+-----------------------+---------------------------
Tool       | client -> server | the MODEL             | get_duty_rate("6403")
Resource   | client -> server | the APP / user        | tariff://schedule/current
Prompt     | client -> server | the USER (slash cmd)  | /review_classification
Sampling   | server -> client | the SERVER asks,      | "classify this product text"
           |                  | the HOST approves     |

Flow:
Step 1 -> initialize: server advertises which primitives it supports (capabilities)
Step 2 -> client lists them: tools/list, resources/list, prompts/list
Step 3 -> model calls tool / app reads resource / user picks prompt
Step 4 -> (optional) server sends sampling/createMessage back to the client
Step 5 -> host shows the request to the user, runs its own LLM, returns result
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> initialize: server बताता है कि वह कौन से primitives support करता है
Step 2 -> client सब list करता है: tools/list, resources/list, prompts/list
Step 3 -> model tool call करता है / app resource पढ़ता है / user prompt चुनता है
Step 4 -> (optional) server, client को sampling/createMessage भेजता है
Step 5 -> host user को request दिखाता है, अपना LLM चलाता है, नतीजा लौटाता है
```

---

## 🟡 Real World Example
**Tariff Agent**: the `tariff` server exposes (a) tool `get_duty_rate(hs_code)`, (b) resource `tariff://rates/{hs_code}` so the app can attach the rate table to the chat, (c) prompt `review(hs_code)` which the analyst triggers from a menu, and (d) sampling: a tool that needs an HS-code guess asks the host's own model instead of embedding an API key in the server.

## 🟡 Real Example Hindi mein
**Tariff Agent**: `tariff` server (a) tool `get_duty_rate(hs_code)`, (b) resource `tariff://rates/{hs_code}` (app इसे chat में attach कर सकता है), (c) prompt `review(hs_code)` (analyst menu से चलाता है), और (d) sampling देता है: जिस tool को HS code का अंदाज़ा चाहिए वह server में API key रखने की जगह host के अपने model से पूछता है।

---

## 💻 Code Example — Basic
```python
# prim_basic.py - one server with all server-side primitives (ran offline)
from mcp.server.fastmcp import FastMCP                      # high-level server helper

mcp = FastMCP("tariff-primitives")                          # server name shown to clients
RATES: dict[str, float] = {"8517": 0.0, "6403": 10.0}       # tiny in-memory rate table

@mcp.tool()                                                 # TOOL: model-controlled action
def get_duty_rate(hs_code: str) -> float:                   # typed arg -> JSON schema generated for the LLM
    """Return duty percent for an HS code."""               # docstring becomes the tool description
    if hs_code not in RATES:                                # unknown code is bad input, not a crash
        raise ValueError(f"unknown HS code {hs_code}")      # SDK turns this into isError=True result
    return RATES[hs_code]                                   # structured float result

@mcp.resource("tariff://rates/{hs_code}")                   # RESOURCE template: app-controlled read
def rate_resource(hs_code: str) -> str:                     # {hs_code} is filled from the URI
    return f"{hs_code}: {RATES.get(hs_code)}"               # plain text body

@mcp.prompt()                                               # PROMPT: user-controlled template
def review(hs_code: str) -> str:                            # argument shown in the client's UI
    return f"Review the classification {hs_code} and list risks."   # becomes a user message

if __name__ == "__main__":                                  # script entry
    mcp.run()                                               # stdio transport by default
```
Run offline with the client from topic 003 (`python client.py`): it printed the tool list, `{'result': 0.0}` for code 8517, `isError True` for an unknown code, `6403: 10.0` from the resource and the rendered prompt text.

## 💻 Code Example — Advanced
```python
# prim_adv.py - tool that READS a resource and then uses SAMPLING (ran with a fake LLM callback)
import asyncio                                              # async runtime for the demo
from mcp import types                                       # protocol types
from mcp.server.fastmcp import FastMCP, Context             # server + request context
from mcp.server.session import ServerSession                # typed session for Context
from mcp.shared.memory import create_connected_server_and_client_session as connect   # in-memory client<->server

mcp = FastMCP("tariff-prim")                                # server

@mcp.resource("tariff://rates/{hs_code}", mime_type="application/json")   # JSON resource template
async def rate(hs_code: str) -> str:                        # async handlers are fine
    return '{"hs": "%s", "pct": 10}' % hs_code              # demo payload

@mcp.tool()                                                 # tool that composes primitives
async def summarize(hs_code: str, ctx: Context[ServerSession, None]) -> str:   # ctx gives access to client features
    """Read the rate resource and ask the CLIENT's LLM to summarise it."""
    contents = await ctx.read_resource(f"tariff://rates/{hs_code}")   # tool -> resource inside same server
    body: str = str(list(contents)[0].content)              # first content block as text
    res = await ctx.session.create_message(                 # SAMPLING: server -> client request
        messages=[types.SamplingMessage(role="user", content=types.TextContent(type="text", text=body))],   # what to send the LLM
        max_tokens=40,                                      # cap tokens: the HOST pays for this call
        system_prompt="You are a customs analyst.",         # optional system prompt
        temperature=0.0)                                    # deterministic for classification-like tasks
    return res.content.text if res.content.type == "text" else "?"   # only text handled here

async def fake_llm(ctx, params: types.CreateMessageRequestParams) -> types.CreateMessageResult | types.ErrorData:   # client-side sampling handler
    print("host sees system prompt:", params.systemPrompt)  # real hosts show this to the user for approval
    return types.CreateMessageResult(role="assistant", content=types.TextContent(type="text", text="summary (fake)"), model="fake-1", stopReason="endTurn")   # canned answer

async def main() -> None:                                   # drive the demo
    async with connect(mcp._mcp_server, sampling_callback=fake_llm) as client:   # client with sampling support
        r = await client.call_tool("summarize", {"hs_code": "6403"})   # triggers resource read + sampling
        print(r.content[0].text)                            # -> summary (fake)
    async with connect(mcp._mcp_server) as client:          # client WITHOUT a sampling handler
        r = await client.call_tool("summarize", {"hs_code": "6403"})
        print(r.isError, r.content[0].text)                 # True, "Sampling not supported" (error handling path)

asyncio.run(main())                                         # run
```
Ran output: `host sees system prompt: You are a customs analyst.`, `summary (fake)`, then `True Error executing tool summarize: Sampling not supported`. FastAPI: a FastAPI host can pass the same `sampling_callback=` into `ClientSession` and forward the request to its LLM (see topics 009 and 013). Token usage: tools/resources/prompts cost tokens only when their text enters the LLM context; sampling spends the host's tokens (set `max_tokens`).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Tools | Converted to LangChain tools by the MCP adapter (not verified here) | Supported via MCP integration (verify docs) | `MCPServerStdio/StreamableHttp` expose tools (import verified in earlier topic) | MCP workbench/tools (verify docs) |
| Resources | Adapter can load resources (verify) | Rare | Not a first-class feature (verify) | Rare |
| Prompts | Adapter can load prompts (verify) | Rare | Prompts supported by the MCP server classes (verify) | Rare |
| Sampling | You write the client callback | Not common | Not common | Not common |

Most agent frameworks only auto-wire **tools**. Resources/prompts/sampling usually need the raw `mcp` client (as in this note).

---

## ⚠️ Common Mistakes
❌ Mistake 1: Making everything a tool, including static reference data.
✅ Correct: Static/readable data -> resource; the model only pays tokens when the app chooses to load it.

❌ Mistake 2: Assuming the model can call resources and prompts.
✅ Correct: Tools are model-controlled. Resources are app-controlled, prompts are user-controlled. Wrap data as a tool too if the model must fetch it itself.

❌ Mistake 3: Putting an LLM API key into the MCP server for "smart" tools.
✅ Correct: Use sampling so the host's model, quota and user approval apply.

❌ Mistake 4: Relying on sampling without checking client capability.
✅ Correct: Many clients do not support it (we got `Sampling not supported`). Provide a fallback.

---

## 🧠 Tricky Interview Question
"Your tool returns a 40-page tariff schedule and the agent gets slow and expensive. Which primitive would you change and why?"

Answer: Do not return the whole document from a tool every time. Expose it as a **resource** (or a resource template per section) and let the host decide what to attach, and give the model a narrow search tool that returns only the matching snippet. This cuts input tokens on every later turn, because tool results stay in the message history. Also consider pagination or a summary field in the tool result.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Name the four MCP primitives.
A1: Tools, resources, prompts (server features) and sampling (a client feature the server can request). Newer protocol versions add more (for example elicitation), check the spec.

Q2: [Medium] Who controls each primitive?
A2: Tools - model; resources - application; prompts - user; sampling - server requests, host/user approves.

Q3: [Hard] Why is sampling safer than giving the server an API key?
A3: The host keeps its own model, quota, rate limits and logging, shows the request to the user, and can refuse or edit it. The server never sees credentials.

Q4: [Hard] What happens if a client does not support sampling?
A4: The server's `create_message` call fails. In our run the tool returned `isError=True` with "Sampling not supported". Servers should check capability or degrade gracefully.

Q5: [System Design] Design the Tariff Agent's MCP surface.
A5: Tools for lookups/calculation (`get_duty_rate`, `calculate_landed_cost`), resources for versioned schedule documents, prompts for analyst workflows (review, audit), sampling only for optional classification help. Read-only tools annotated `readOnlyHint`, writes behind human approval.

---

## 💰 Cost Impact
Tokens: tool/prompt/resource text that enters the context is billed as input on every later turn (approximate: tokens ~ characters / 4 for English; measure with your tokenizer). Tool *definitions* are also sent each request, so many verbose tools raise cost. Sampling adds a full extra LLM call paid by the host. Tips: keep tool descriptions short, return only needed fields, use resources instead of giant tool outputs, cap sampling `max_tokens`.

---

## 🔷 When to Use
✅ Use tools when: the model must decide to act or fetch.
✅ Use resources when: the app/user should attach reference data (files, schedules, schemas).
✅ Use prompts when: you want reusable, parameterised workflows users trigger by name.
✅ Use sampling when: a server needs LLM help but should not own keys.

❌ Avoid when:
- A resource is used for something with side effects (use a tool with approval).
- Sampling is used in a stateless/multi-replica HTTP deployment without checking it works there.

---

## 📊 Visual Diagram
```
            +---------------- HOST (FastAPI agent) ----------------+
            |   LLM                                                |
            |    ^  tool calls          user picks      app loads  |
            +----|-----------------------|-----------------|-------+
                 |                       |                 |
          tools/call                prompts/get      resources/read
                 v                       v                 v
            +--------------- MCP SERVER (tariff) -----------------+
            |  tools        prompts           resources           |
            |      \                                  /           |
            |       +---- sampling/createMessage ----+            |
            +------------------------|---------------------------+
                                     v   (server -> client)
                              host's own LLM answers
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool | Action callable by the model | model द्वारा चलाया जाने वाला action |
| Resource | Read-only data addressed by URI | URI से मिलने वाला read-only data |
| Prompt | Reusable message template | दोबारा इस्तेमाल होने वाला template |
| Sampling | Server asks client's LLM to generate | server का client के LLM से generate करवाना |
| Capability | Feature advertised at handshake | handshake में बताई गई क्षमता |

---

## ⚡ 3-Line Summary
English: Tools are model-controlled actions, resources are app-controlled data, prompts are user-controlled templates. Sampling lets a server borrow the host's LLM. Pick the primitive by who should be in control.
Hindi: Tools model के actions हैं, resources app का data हैं, prompts user के templates हैं। Sampling server को host का LLM उधार देता है। Primitive इस आधार पर चुनें कि control किसके पास होना चाहिए।

---

## ➡️ Next Topic
**006. MCP Tools - Deep Dive** - the primitive you will use 90% of the time: schemas, annotations, structured output, errors and progress.

---
