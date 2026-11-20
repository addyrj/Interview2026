---

# 139. AutoGen Tools
# हिंदी में: AutoGen Tools — functions को LLM के tools बनाना
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
A tool is a function the model can ask the agent to run. In AutoGen v0.4 you can pass a typed Python function (sync or async) directly in `tools=[...]`, or wrap it in `FunctionTool` (from `autogen_core.tools`) to control name and description. The JSON schema is generated from type hints, `Annotated` descriptions and the docstring.

## 🔵 सरल परिभाषा (Hindi)
Tool एक function है जिसे model agent से चलवाने को कह सकता है। AutoGen v0.4 में आप typed Python function (sync या async) सीधे `tools=[...]` में दे सकते हैं, या नाम और description नियंत्रित करने के लिए `FunctionTool` (`autogen_core.tools` से) में लपेट सकते हैं। JSON schema type hints, `Annotated` descriptions और docstring से अपने आप बनता है।

---

## 🔴 Problem it Solves
Models cannot access your database, tariff API or calculator. Without tools they guess HS codes and duty rates. Writing JSON schemas by hand is error-prone and drifts from the code. Tool errors must be reported to the model in a way it can recover from, instead of crashing the agent.

## 🔴 यह क्यों बना? (Hindi)
Models आपके database, tariff API या calculator तक नहीं पहुँच सकते। Tools के बिना वे HS codes और duty rates का अंदाज़ा लगाते हैं। JSON schema हाथ से लिखना error-prone है और code से अलग हो जाता है। Tool errors model को ऐसे बताने चाहिए कि वह सुधर सके, agent crash न हो।

---

## 🟢 How it Works

```
Step 1 -> Write a function with type hints and a docstring (or Annotated arg descriptions)
Step 2 -> Optional: FunctionTool(fn, description='...') (name defaults to fn.__name__)
Step 3 -> AutoGen builds a JSON schema -> sent to the model with every request
Step 4 -> Model replies with a FunctionCall(name, arguments JSON)
Step 5 -> Agent validates arguments, runs the tool (awaits async tools)
Step 6 -> Success -> FunctionExecutionResult(content, is_error=False)
Step 7 -> Exception -> FunctionExecutionResult(content=error text, is_error=True), fed back to the model
Step 8 -> Model recovers (retries with new args, apologises, or asks the user)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> type hints और docstring (या Annotated arg descriptions) वाला function लिखो
Step 2 -> optional: FunctionTool(fn, description='...') (नाम default में fn.__name__)
Step 3 -> AutoGen JSON schema बनाता है -> हर request में model को जाता है
Step 4 -> Model FunctionCall(name, arguments JSON) लौटाता है
Step 5 -> Agent arguments validate करके tool चलाता है (async tools await होते हैं)
Step 6 -> सफल -> FunctionExecutionResult(content, is_error=False)
Step 7 -> Exception -> FunctionExecutionResult(content=error text, is_error=True), model को लौटाया जाता है
Step 8 -> Model सुधरता है (नए args से retry, माफ़ी, या user से पूछना)
```

---

## 🟡 Real World Example
**Exchange-rate tool failure.** The model asks for USD to XYZ. The tool raises `ValueError('unsupported pair USD->XYZ')`. AutoGen does not crash: the error text goes back as an error result and the model answers 'please use USD to INR'. In the verified offline run, `tool_error` was True and the final message was the model's recovery text.

## 🟡 Real Example Hindi mein
**Exchange-rate tool failure।** Model USD से XYZ का rate माँगता है। Tool `ValueError('unsupported pair USD->XYZ')` raise करता है। AutoGen crash नहीं होता: error text error result बनकर model को लौटता है और model कहता है 'कृपया USD से INR use करें'। Verified offline run में `tool_error` True था और final message model का recovery text था।

---

## 💻 Code Example — Basic
Basic: `FunctionTool` with an `Annotated` argument description; it prints the generated schema and runs the tool directly with `run_json`.

```python
# AutoGen tools: plain functions and FunctionTool (schema is auto-built from type hints + docstring)
import asyncio, json                                              # stdlib
from typing import Annotated                                      # to attach per-argument descriptions
from autogen_core import CancellationToken                        # needed to run a tool directly
from autogen_core.tools import FunctionTool                       # wrap a function as a tool

def get_tariff_rate(hs_code: Annotated[str, "10-digit or 6-digit HS code"]) -> str:  # Annotated text becomes the arg description
    return {"6109.10": "20%"}.get(hs_code, "unknown")             # fake lookup

async def main() -> None:
    tool = FunctionTool(get_tariff_rate, description="Look up import duty for an HS code")  # description is REQUIRED here
    print(tool.name)                                              # name = function name
    print(json.dumps(tool.schema["parameters"]["properties"]))    # JSON schema sent to the LLM (costs prompt tokens every call)
    out = await tool.run_json({"hs_code": "6109.10"}, CancellationToken())  # run directly (what the agent does internally)
    print(out)                                                    # 20%

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: an async tool that raises; the scripted model first calls it with a bad argument and then recovers. FastAPI returns the tool's `is_error` flag and the final answer.

```python
# Async tools, tool errors, and an agent that survives them. FastAPI + usage.
import asyncio                                                    # async
from fastapi import FastAPI                                       # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_core import FunctionCall                             # scripted tool calls
from autogen_core.models import CreateResult, RequestUsage        # scripted model results
from autogen_core.tools import FunctionTool                       # tool wrapper
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

INFO = {"function_calling": True, "vision": False, "json_output": False, "family": "unknown", "structured_output": False}

async def fetch_exchange_rate(src: str, dst: str) -> float:      # async tool: awaited by the agent
    await asyncio.sleep(0)                                        # real: await httpx.get(...)
    if (src, dst) != ("USD", "INR"):                              # unknown pair
        raise ValueError(f"unsupported pair {src}->{dst}")        # exceptions do NOT crash the agent...
    return 83.2

def call(name: str, args: str, cid: str) -> CreateResult:         # helper to script a model tool call
    return CreateResult(finish_reason="function_calls", content=[FunctionCall(id=cid, name=name, arguments=args)],
                        usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False)

def build() -> AssistantAgent:
    client = ReplayChatCompletionClient([
        call("fetch_exchange_rate", '{"src": "USD", "dst": "XYZ"}', "1"),   # model asks for a bad pair
        "I could not fetch that rate; please use USD to INR.",              # ...and recovers after seeing the error
    ], model_info=INFO)
    tool = FunctionTool(fetch_exchange_rate, description="USD->INR style exchange rate")
    return AssistantAgent("fx", client, tools=[tool], reflect_on_tool_use=True)

app = FastAPI()

@app.get("/fx")
async def fx() -> dict:
    res = await build().run(task="rate USD to XYZ?")
    ev = [m for m in res.messages if type(m).__name__ == "ToolCallExecutionEvent"][0]  # inspect the tool result
    r = ev.content[0]
    return {"tool_error": r.is_error, "tool_message": r.content, "final": str(res.messages[-1].content)}  # error goes BACK to the LLM as text

if __name__ == "__main__":
    print(TestClient(app).get("/fx").json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Define a tool | @tool + bind_tools / ToolNode | @tool or BaseTool | @function_tool | Plain typed function or FunctionTool |
| Schema source | Type hints / pydantic args_schema | Type hints / args_schema | Type hints + docstring | Type hints + Annotated + description |
| Async tools | Yes | Limited | Yes | Yes (awaited by the agent) |
| Error handling | handle_tool_errors option | Retries / guardrails | Error string to model (configurable) | is_error=True result back to model |
| Tool-use loop | Graph loop | Agent executor | Runner loop | AssistantAgent (max_tool_iterations) |

---

## ⚠️ Common Mistakes
❌ Mistake: Tools without type hints: schema becomes vague or fails.
✅ Correct: Annotate every parameter and the return type.

❌ Mistake: Returning huge payloads from tools: tokens explode, since results re-enter the context.
✅ Correct: Return only needed fields; truncate; paginate.

❌ Mistake: Swallowing errors inside the tool and returning 'ok'.
✅ Correct: Raise or return a clear error string so the model can react.

❌ Mistake: Tools with side effects (refund, file filing) that are not idempotent: a retry doubles the action.
✅ Correct: Idempotency keys, confirmation steps, and approval for dangerous tools.

---

## 🧠 Tricky Interview Question
The model calls your `file_declaration` tool twice because the first response timed out. How do you protect the real world?

Answer: Treat tools as at-least-once. Add idempotency: require a client-generated key (hash of declaration payload plus session id) and make the backend return the existing result for a repeated key. Separate read tools from write tools; protect write tools with approval (`UserProxyAgent` or `approval` logic) and rate limits; log every call with the tool call id. Do not rely on the LLM to avoid duplicates. Also set a timeout inside the tool, since the agent waits for it.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How is a tool schema produced?
A1: From the function signature: parameter names and types (via pydantic), `Annotated[type, 'description']`, the function docstring or the `description` passed to `FunctionTool`.

Q2: [Medium] Are async tools supported?
A2: Yes: the agent awaits them; blocking sync tools should be offloaded to threads if long-running.

Q3: [Hard] What happens when a tool raises?
A3: The agent returns the error as a function result with `is_error=True` and gives it to the model; the run continues.

Q4: [Hard] Why do tool schemas affect cost?
A4: They are included in every LLM request; more tools or long descriptions mean more prompt tokens on every call.

Q5: [System Design] Design a safe set of tools for a tariff agent that can also file declarations.
A5: Read tools: hs_search, get_rate, get_restrictions. Write tool: submit_declaration with idempotency key, schema validation, dry-run mode, and human approval gate. Per-tenant authorisation inside each tool (never trust the model's arguments for identity), timeouts, audit log, rate limits, tests with a replay client that scripts bad arguments.

---

## 💰 Cost Impact
Tool schemas ride along on every request: each tool adds prompt tokens (name + description + parameter schema; often 50-200 tokens per tool, measure yours with your tokenizer). A turn using one tool and `reflect_on_tool_use=True` makes 2 model calls. Large tool outputs are re-sent on later calls. Formula: `call_prompt = system + tool_schemas + history + tool_results`. Reduce by keeping only relevant tools per agent, concise descriptions, result truncation, and bounded context. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Anything the model cannot know or compute reliably.
- Deterministic business logic (rates, validation).
- Integrations with APIs and databases.

❌ Avoid when:
- Logic the model can do from the prompt alone.
- Dozens of tools on one agent: split roles or use routing.
- Non-idempotent actions without safeguards.

---

## 📊 Visual Diagram
```
 python function  --typehints/docstring-->  JSON schema
        ^                                        |
        |                                        v
   run tool (await)  <-- FunctionCall <-- LLM request(system + tools + history)
        |
        +--ok--> FunctionExecutionResult(is_error=False) --+
        +--exception--> FunctionExecutionResult(is_error=True, text) --+
                                                                       v
                                            back to the LLM: answer, retry or ask user
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FunctionTool | Wrapper turning a function into a tool | function को tool बनाने वाला wrapper |
| Annotated | Attach metadata to a type hint | type hint में metadata जोड़ना |
| FunctionCall | Model's request to run a tool | tool चलाने का model का अनुरोध |
| FunctionExecutionResult | Tool output wrapper | tool output wrapper |
| is_error | Flag that a tool failed | tool fail हुआ इसका flag |
| schema | JSON description of arguments | arguments का JSON विवरण |
| idempotent | Safe to repeat | दोहराना सुरक्षित |
| run_json | Run tool from a dict of args | dict args से tool चलाना |

---

## ⚡ 3-Line Summary
English: Tools are typed functions whose schema AutoGen builds from hints and docstrings.
Errors are returned to the model as is_error results instead of crashing the run.
Schemas and results cost tokens on every call: keep tools few, tight and idempotent.
Hindi: Tools typed functions हैं जिनका schema AutoGen hints और docstrings से बनाता है।
Errors run को crash करने की जगह is_error results के रूप में model को लौटते हैं।
Schemas और results हर call में tokens खाते हैं: tools कम, कसे हुए और idempotent रखें।

---

## ➡️ Next Topic
140. Tool Registration -- how and where to attach tools: tools=, workbench, MCP, and the v0.2 register_for_llm.

---
