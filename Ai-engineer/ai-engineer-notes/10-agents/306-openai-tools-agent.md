---

# 306. OpenAI Tools Agent
# हिंदी में: OpenAI Tools Agent (Function/Tool Calling वाला Agent)

---

## 🔵 Simple Definition (English)
An OpenAI Tools Agent is a loop where the LLM looks at the user question, decides which of your Python functions (tools) to call using the native `tools` / `tool_calls` feature, reads the results, and repeats until it can give a final answer. The model returns structured JSON arguments, so no fragile text parsing is needed.

## 🔵 सरल परिभाषा (Hindi)
OpenAI Tools Agent एक loop है जिसमें LLM user का सवाल देखकर तय करता है कि कौन सा Python function (tool) call करना है। यह OpenAI के native `tools` / `tool_calls` feature से होता है। Model structured JSON arguments देता है, इसलिए text parse करने की झंझट नहीं। Result पढ़कर वह तब तक repeat करता है जब तक final answer तैयार न हो जाए।

---

## 🔴 Problem it Solves
Older ReAct agents asked the model to write "Action: search / Action Input: ..." as plain text and then parsed it with regex. This broke often (extra words, wrong format). Models were also unable to call several tools in one step. The tools API fixes both: the model is fine-tuned to emit valid JSON arguments that match your schema, and it can request multiple tool calls in parallel.

## 🔴 यह क्यों बना? (Hindi)
पुराने ReAct agents model से plain text में "Action: ..." लिखवाते थे और regex से parse करते थे। Format टूटता रहता था। Tools API में model खुद valid JSON arguments देता है (आपके schema के हिसाब से) और एक साथ कई tools भी माँग सकता है। इसलिए agent ज़्यादा भरोसेमंद बना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define tools as JSON schema (name, description, parameters)
Step 2 → Send messages + tools to chat.completions.create
Step 3 → Model replies with message.tool_calls (or a plain final answer)
Step 4 → Your code runs each tool with the parsed JSON arguments
Step 5 → Append the assistant message + one role="tool" message per call (with tool_call_id)
Step 6 → Call the model again with the extended messages
Step 7 → Repeat until no tool_calls remain, or max_steps is hit
Step 8 → Return the final assistant text
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tools को JSON schema में define करो (name, description, parameters)
Step 2 → Messages + tools को model को भेजो
Step 3 → Model या तो tool_calls देता है या सीधा final answer
Step 4 → आपका code हर tool को JSON arguments के साथ चलाता है
Step 5 → Assistant message और हर call का role="tool" result (tool_call_id के साथ) जोड़ो
Step 6 → Model को दोबारा call करो
Step 7 → जब tool_calls खत्म हों या max_steps पूरे हों, रुक जाओ
Step 8 → Final text return करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "What is the import duty for a Bluetooth speaker from China?". The agent calls `search_hs_code("bluetooth speaker")` and gets `8518.22`. Then it calls `get_duty_rate("8518.22", "CN")` and gets `12.5%`. Finally it writes the answer with both facts. Each step is a tool call with validated JSON arguments.

**Zomato-style**: "Order my usual biryani" leads to `get_order_history`, then `check_restaurant_open`, then `place_order`.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "China से Bluetooth speaker का import duty क्या है?" Agent पहले `search_hs_code` call करता है (8518.22 मिलता है), फिर `get_duty_rate("8518.22", "CN")` (12.5%)। अंत में दोनों facts के साथ जवाब लिखता है।
**Zomato**: "मेरी usual biryani order करो" → order history → restaurant open check → order place।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny tools-agent loop with a FAKE model so it runs offline.
import json                                   # to encode/decode tool arguments
from typing import Any, Callable              # type hints for tool registry

# --- Tools (plain Python functions) ---------------------------------
def search_hs_code(product: str) -> str:      # tool 1: product -> HS code
    table = {"bluetooth speaker": "8518.22"}  # tiny fake database
    return table.get(product.lower(), "UNKNOWN")  # return code or UNKNOWN

def get_duty_rate(hs_code: str, country: str) -> str:  # tool 2: duty lookup
    rates = {("8518.22", "CN"): "12.5%"}      # tiny fake rate table
    return rates.get((hs_code, country), "N/A")  # default when missing

TOOLS: dict[str, Callable[..., str]] = {      # registry: name -> function
    "search_hs_code": search_hs_code,         # register tool 1
    "get_duty_rate": get_duty_rate,           # register tool 2
}

# --- Fake model: mimics the shape of OpenAI responses ----------------
def fake_model(messages: list[dict[str, Any]]) -> dict[str, Any]:
    tool_msgs = [m for m in messages if m["role"] == "tool"]   # tool results so far
    if len(tool_msgs) == 0:                   # first turn: ask for HS code
        return {"tool_calls": [{"id": "c1", "name": "search_hs_code",
                                "arguments": json.dumps({"product": "bluetooth speaker"})}]}
    if len(tool_msgs) == 1:                   # second turn: ask for duty
        return {"tool_calls": [{"id": "c2", "name": "get_duty_rate",
                                "arguments": json.dumps({"hs_code": tool_msgs[0]["content"], "country": "CN"})}]}
    return {"content": f"HS {tool_msgs[0]['content']}, duty {tool_msgs[1]['content']}"}  # final

def run_agent(question: str, max_steps: int = 5) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]  # history
    for _ in range(max_steps):                # bounded loop, never infinite
        reply = fake_model(messages)          # "call the LLM"
        calls = reply.get("tool_calls")       # did it ask for tools?
        if not calls:                         # no tools -> final answer
            return reply["content"]           # done
        for call in calls:                    # run every requested tool
            args = json.loads(call["arguments"])        # parse JSON args
            result = TOOLS[call["name"]](**args)        # execute the function
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})  # feed back
    return "Stopped: max_steps reached"       # safety exit

if __name__ == "__main__":                    # run directly
    print(run_agent("Duty for bluetooth speaker from China?"))  # prints final answer
```

## 💻 Code Example — Advanced
```python
# Production: real OpenAI client (openai>=1), async, error handling, type hints.
import asyncio                                # async runtime
import json                                   # arguments parsing
import logging                                # structured logs
from typing import Any                        # type hints
from openai import AsyncOpenAI, APIError, RateLimitError  # real SDK classes

log = logging.getLogger("tools_agent")        # module logger
client = AsyncOpenAI()                        # reads OPENAI_API_KEY from env

TOOL_SCHEMAS: list[dict[str, Any]] = [        # JSON schema the model sees
    {"type": "function", "function": {
        "name": "search_hs_code",             # tool name
        "description": "Find the HS code for a product description.",  # when to use
        "parameters": {"type": "object",
                       "properties": {"product": {"type": "string"}},
                       "required": ["product"]}}},
    {"type": "function", "function": {
        "name": "get_duty_rate",
        "description": "Get import duty percent for an HS code and ISO country.",
        "parameters": {"type": "object",
                       "properties": {"hs_code": {"type": "string"}, "country": {"type": "string"}},
                       "required": ["hs_code", "country"]}}},
]

async def search_hs_code(product: str) -> str:    # async tool implementation
    await asyncio.sleep(0)                    # pretend I/O (DB call)
    return {"bluetooth speaker": "8518.22"}.get(product.lower(), "UNKNOWN")

async def get_duty_rate(hs_code: str, country: str) -> str:
    await asyncio.sleep(0)                    # pretend I/O
    return {("8518.22", "CN"): "12.5%"}.get((hs_code, country), "N/A")

REGISTRY = {"search_hs_code": search_hs_code, "get_duty_rate": get_duty_rate}  # name -> coroutine fn

async def run_tool(name: str, raw_args: str) -> str:
    try:
        fn = REGISTRY[name]                   # KeyError if model invents a tool
        args = json.loads(raw_args)           # JSONDecodeError if malformed
        return str(await fn(**args))          # TypeError if wrong params
    except (KeyError, json.JSONDecodeError, TypeError) as exc:
        return f"TOOL_ERROR: {exc}"           # let the model see and self-correct

async def run_agent(question: str, max_steps: int = 6) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "You are a tariff assistant. Use tools; never guess codes."},
        {"role": "user", "content": question},
    ]
    total_tokens = 0                          # track usage for cost
    for step in range(max_steps):             # hard step limit
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", messages=messages,
                tools=TOOL_SCHEMAS, tool_choice="auto", temperature=0)
        except RateLimitError:                # 429: back off then retry
            await asyncio.sleep(2 ** step)
            continue
        except APIError as exc:               # other API failure
            log.error("API error: %s", exc)
            raise
        total_tokens += resp.usage.total_tokens   # accumulate tokens
        msg = resp.choices[0].message         # assistant message
        if not msg.tool_calls:                # final answer
            return {"answer": msg.content, "steps": step + 1, "tokens": total_tokens}
        messages.append(msg.model_dump(exclude_none=True))  # keep assistant tool_calls in history
        results = await asyncio.gather(*[     # run parallel tool calls concurrently
            run_tool(tc.function.name, tc.function.arguments) for tc in msg.tool_calls])
        for tc, out in zip(msg.tool_calls, results):
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})
    return {"answer": "Max steps reached", "steps": max_steps, "tokens": total_tokens}

if __name__ == "__main__":
    print(asyncio.run(run_agent("Duty for bluetooth speaker from CN?")))
```

---

## 🟠 FastAPI Integration
Expose the agent as an async endpoint. Validate input with Pydantic, convert failures to HTTP errors, and return token usage so clients can see cost.

```python
from fastapi import FastAPI, HTTPException   # web framework
from pydantic import BaseModel, Field        # request validation (pydantic v2)

app = FastAPI(title="Tariff Tools Agent")    # app instance

class AskRequest(BaseModel):                 # input schema
    question: str = Field(min_length=3, max_length=500)  # reject junk

class AskResponse(BaseModel):                # output schema
    answer: str
    steps: int
    tokens: int

@app.post("/agent/ask", response_model=AskResponse)  # POST route
async def ask(req: AskRequest) -> AskResponse:
    try:
        result = await run_agent(req.question)       # agent from the Advanced example
    except Exception as exc:                          # unexpected failure
        raise HTTPException(status_code=502, detail=f"Agent failed: {exc}")
    return AskResponse(**result)                      # validated response
```

---

## 🔗 LangChain / LangGraph Connection
LangChain wraps the same tools API. `create_tool_calling_agent` + `AgentExecutor` is the classic way; LangGraph's `create_react_agent` is the modern one.

```python
from langchain_core.tools import tool                    # decorator -> Tool with schema
from langchain_openai import ChatOpenAI                  # chat model wrapper
from langgraph.prebuilt import create_react_agent        # tool-calling agent graph

@tool                                                    # schema built from signature + docstring
def search_hs_code(product: str) -> str:
    """Find the HS code for a product description."""
    return "8518.22"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)     # model supporting tool calls
agent = create_react_agent(llm, [search_hs_code])        # loop built for you
out = agent.invoke({"messages": [("user", "HS code for bluetooth speaker?")]})
print(out["messages"][-1].content)                       # final answer
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to append the assistant's tool_calls message before the tool results.
✅ Correct: the history must contain the assistant message with `tool_calls`, then tool messages with matching `tool_call_id`.

```python
# Wrong: API returns 400 because tool message has no matching tool_call
messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})
# Right: keep the assistant message first
messages.append(msg.model_dump(exclude_none=True))
messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})
```

❌ Mistake 2: No `max_steps`, so a confused model loops forever and burns money.
✅ Correct: always bound the loop and return a safe fallback.

```python
# Wrong
while True: ...
# Right
for step in range(max_steps): ...
```

❌ Mistake 3: Crashing on bad tool arguments.
✅ Correct: catch the error and send `TOOL_ERROR: ...` back so the model can retry.

---

## 🧠 Tricky Interview Question
**Q**: "Your agent sometimes calls `get_duty_rate` before `search_hs_code` and invents an HS code. How do you fix it?"

**Answer**: The model is guessing because the tool description does not say the HS code must come from `search_hs_code`. Fix with (1) clearer descriptions ("hs_code must come from search_hs_code"), (2) a system prompt rule, (3) validating `hs_code` format inside the tool and returning an error message, (4) an `enum` or regex pattern in the schema, and (5) if the order is fixed, use a LangGraph workflow instead of a free agent. Prompting reduces the problem; validation makes it safe.

---

## ⚫ Interview Questions + Answers

Q1: What is `tool_choice`?
A1: It controls tool use: `"auto"` (model decides), `"none"` (no tools), `"required"` (must call some tool), or a specific function name to force it.

Q2: Why must each tool result have `tool_call_id`?
A2: It links a result to the exact call the model made. With parallel calls, the model needs the id to match answers to requests.

Q3: What are parallel tool calls and when do you disable them?
A3: The model may return several `tool_calls` in one message, which you can run with `asyncio.gather`. Disable with `parallel_tool_calls=False` when tools depend on each other or have side effects with ordering.

Q4: How do you stop prompt injection through tool results?
A4: Treat tool output as untrusted data. Wrap it, strip instructions, limit its size, never let it choose tools with side effects without checks, and use least-privilege tools.

Q5: (Hard) Design retries for a tool-calling agent where one tool is flaky and another charges money.
A5: Make idempotent tools retryable with exponential backoff and jitter. For the paid or side-effect tool, use an idempotency key, retry only on safe errors, and add a human-approval or confirm step. Log every call with its id, and return structured errors to the model so it does not repeat the paid action blindly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The path is unknown and depends on the question
- You have 2-10 well-described tools
- You need structured arguments reliably

❌ Avoid when:
- The steps are always the same (use a fixed chain or LangGraph)
- Latency is critical (each loop is one more LLM call)
- You have 50+ tools (model gets confused; use routing first)

---

## 📊 Visual Diagram
```
User question
     │
     ▼
┌───────────┐  tool_calls   ┌──────────────┐
│   LLM     │ ────────────► │ Run tools    │
│ (+tools)  │ ◄──────────── │ (your code)  │
└───────────┘  role="tool"  └──────────────┘
     │ no tool_calls
     ▼
 Final answer
```

---

## 💰 Cost Impact
Every loop re-sends the full history, so input tokens grow each step. A 3-step run with a 600-token prompt can cost about 3x a single call. Tool schemas also count as input tokens on every call.

Optimise: keep tool descriptions short, use `gpt-4o-mini`, limit `max_steps`, truncate large tool outputs, cache repeated lookups, and use prompt caching for the static system prompt and tools. Always log `usage.total_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool call | Model's request to run a function | Function चलाने की माँग |
| Tool schema | JSON description of a tool | Tool का JSON विवरण |
| tool_call_id | Id linking result to call | Call और result जोड़ने वाली id |
| Parallel tool calls | Several calls in one reply | एक साथ कई calls |
| max_steps | Loop limit | Loop की सीमा |
| tool_choice | Rule for tool usage | Tool use का नियम |

---

## ⚡ 3-Line Summary
English: A tools agent lets the model pick functions through structured JSON tool calls in a loop. Always append the assistant message and matching tool results, bound the loop, and return errors to the model. Watch token growth because history is resent each step.
Hindi: Tools agent में model JSON tool calls से functions चुनता है और loop चलता है। Assistant message और सही tool results जोड़ो, loop सीमित रखो, और errors model को वापस दो। हर step में history दोबारा जाती है, इसलिए tokens पर नज़र रखो।

---

## ➡️ Next Topic
**307. Claude Agent** — the same idea using Anthropic's `tool_use` / `tool_result` content blocks, to compare the two providers.
