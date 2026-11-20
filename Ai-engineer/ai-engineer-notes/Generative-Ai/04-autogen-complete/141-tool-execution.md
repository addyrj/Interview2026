---

# 141. Tool Execution
# हिंदी में: Tool Execution (AutoGen में agent tools कैसे चलाता है)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
In AutoGen AgentChat an `AssistantAgent` receives plain Python functions in `tools=[...]`. The model asks for a tool call, the agent runs the function, and the result goes back to the model as an observation. The function's type hints and docstring become the JSON schema the LLM sees.

## 🔵 सरल परिभाषा (Hindi)
AutoGen AgentChat में `AssistantAgent` को `tools=[...]` में साधारण Python functions दिए जाते हैं। model tool call माँगता है, agent function चलाता है, और नतीजा observation बनकर model को लौटता है। function के type hints और docstring से ही LLM को दिखने वाला JSON schema बनता है।

---

## 🔴 Problem it Solves
Without tool execution an LLM can only talk. It cannot read a tariff table, call your database or compute duty exactly, so it guesses. Hand-written loops (parse model output, dispatch, feed result back, handle errors) are boring and error-prone.

## 🔴 यह क्यों बना? (Hindi)
Tool execution के बिना LLM सिर्फ़ बात कर सकता है। वह tariff table नहीं पढ़ सकता, database call नहीं कर सकता, duty सटीक नहीं निकाल सकता, इसलिए अंदाज़ा लगाता है। खुद का loop (output parse करो, dispatch करो, result लौटाओ, errors सँभालो) उबाऊ और गलतियों वाला होता है।

---

## 🟢 How it Works

```
Step 1 -> User task arrives; agent sends messages + tool schemas to the model client
Step 2 -> Model replies with a FunctionCall (name + JSON arguments)
Step 3 -> Agent emits ToolCallRequestEvent and validates the arguments
Step 4 -> Agent runs the function (async functions are awaited); exceptions become is_error=True results
Step 5 -> Agent emits ToolCallExecutionEvent with FunctionExecutionResult
Step 6 -> reflect_on_tool_use=True: second model call turns the result into a natural-language answer; False: returns a summary of the tool output
Step 7 -> max_tool_iterations controls how many tool rounds one turn may take
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> User का task आता है; agent messages और tool schemas model client को भेजता है
Step 2 -> Model एक FunctionCall (नाम + JSON arguments) लौटाता है
Step 3 -> Agent ToolCallRequestEvent निकालता है और arguments validate करता है
Step 4 -> Agent function चलाता है (async functions await होते हैं); exception है तो is_error=True result बनता है
Step 5 -> Agent ToolCallExecutionEvent और FunctionExecutionResult निकालता है
Step 6 -> reflect_on_tool_use=True: दूसरा model call result को सामान्य भाषा के जवाब में बदलता है; False: tool output का summary लौटता है
Step 7 -> max_tool_iterations तय करता है कि एक turn में कितने tool rounds हो सकते हैं
```

---

## 🟡 Real World Example
**Tariff Agent.** The user asks 'duty on 6403.99?'. The agent calls `hs_rate('6403.99')`, gets 0.25 from the table and answers '25%'. The number comes from code, not from the model's memory, so it is auditable. An unknown chapter raises `KeyError`; AutoGen turns that into an error observation instead of crashing the run.

## 🟡 Real Example Hindi mein
**Tariff Agent.** User पूछता है '6403.99 पर duty?'। Agent `hs_rate('6403.99')` call करता है, table से 0.25 पाता है और '25%' बताता है। संख्या code से आती है, model की याददाश्त से नहीं, इसलिए audit हो सकती है। अज्ञात chapter पर `KeyError` आता है; AutoGen उसे crash बनाने के बजाय error observation बना देता है।

---

## 💻 Code Example — Basic
Basic: one sync tool and a scripted fake model. The fake model first requests the tool, then writes the final sentence. This shows the whole message trace offline.

```python
# Basic: AutoGen tool execution with a scripted (fake) model
import asyncio  # run async code
from autogen_core import FunctionCall  # a model's request to call a tool
from autogen_core.models import CreateResult, RequestUsage  # fake model reply types
from autogen_ext.models.replay import ReplayChatCompletionClient  # offline fake model
from autogen_agentchat.agents import AssistantAgent  # the agent that runs tools

MI = {"vision": False, "function_calling": True, "json_output": False,
      "family": "unknown", "structured_output": False}  # tell AutoGen the fake model can call tools

def hs_rate(code: str) -> float:  # plain Python function = tool; type hints become the JSON schema
    """Return the import duty rate for an HS code."""  # docstring becomes tool description
    return {"8517": 0.0, "6403": 0.25}.get(code[:4], 0.10)  # tiny tariff table

async def main() -> None:  # entry point
    call = CreateResult(finish_reason="function_calls",  # model says: I want a tool call
                        content=[FunctionCall(id="c1", name="hs_rate", arguments='{"code":"6403.99"}')],
                        usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False)
    model = ReplayChatCompletionClient([call, "Duty on 6403.99 is 25%."], model_info=MI)  # step1 tool call, step2 final text
    agent = AssistantAgent("tariff", model, tools=[hs_rate], reflect_on_tool_use=True)  # reflect = 2nd LLM call to phrase answer
    result = await agent.run(task="Duty rate for 6403.99?")  # run one task
    for m in result.messages:  # print the full trace
        print(type(m).__name__, getattr(m, "content", None))  # show message kind + content

asyncio.run(main())  # start the event loop
```

## 💻 Code Example — Advanced
Advanced: FastAPI endpoint, async tool, hard timeout with `asyncio.wait_for`, tool errors collected from `ToolCallExecutionEvent`, and token totals from `models_usage`.

```python
# Advanced: FastAPI + async tool + tool error handling + token usage (fake model so it runs offline)
import asyncio  # async primitives
from fastapi import FastAPI, HTTPException  # web framework
from fastapi.testclient import TestClient  # in-process test client
from pydantic import BaseModel  # request validation
from autogen_core import FunctionCall  # tool call object
from autogen_core.models import CreateResult, RequestUsage  # fake model types
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake model
from autogen_agentchat.agents import AssistantAgent  # agent
from autogen_agentchat.messages import ToolCallExecutionEvent  # event holding tool results

MI = {"vision": False, "function_calling": True, "json_output": False,
      "family": "unknown", "structured_output": False}  # fake model capabilities
RATES: dict[str, float] = {"6403": 0.25, "8517": 0.0}  # tariff table

async def hs_rate(code: str) -> float:  # async tools are awaited by AutoGen
    """Return duty rate for an HS code; raises KeyError if unknown."""  # description for the LLM
    await asyncio.sleep(0)  # pretend to hit a database
    return RATES[code[:4]]  # KeyError on unknown chapter -> becomes an error observation

def fake_model(code: str) -> ReplayChatCompletionClient:  # build a scripted model per request
    call = CreateResult(finish_reason="function_calls",  # first reply: call the tool
                        content=[FunctionCall(id="c1", name="hs_rate", arguments=f'{{"code":"{code}"}}')],
                        usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False)
    return ReplayChatCompletionClient([call, "done"], model_info=MI)  # second reply: final text

app = FastAPI()  # the app

class Req(BaseModel):  # request body
    code: str  # HS code

@app.post("/rate")  # endpoint
async def rate(req: Req) -> dict[str, object]:  # typed response
    agent = AssistantAgent("tariff", fake_model(req.code), tools=[hs_rate], reflect_on_tool_use=True)  # fresh agent per request
    try:  # guard the run
        res = await asyncio.wait_for(agent.run(task=req.code), timeout=30)  # hard timeout
    except asyncio.TimeoutError:  # slow tool or model
        raise HTTPException(504, "agent timed out")  # gateway timeout
    results = [r for m in res.messages if isinstance(m, ToolCallExecutionEvent) for r in m.content]  # collect tool results
    errors = [r.content for r in results if r.is_error]  # tool failures are data, not exceptions
    tokens = sum((m.models_usage.prompt_tokens + m.models_usage.completion_tokens) for m in res.messages if m.models_usage)  # token total
    return {"answer": res.messages[-1].content, "tool_errors": errors, "tokens": tokens}  # response

c = TestClient(app)  # test client
print(c.post("/rate", json={"code": "6403.99"}).json())  # known code
print(c.post("/rate", json={"code": "9999.00"}).json())  # unknown code -> tool error captured
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Tool definition | Python function + @tool / ToolNode | @tool or BaseTool class | @function_tool decorator | Plain function or FunctionTool in tools=[] |
| Schema source | Type hints / docstring | Type hints / args_schema | Type hints / docstring | Type hints / docstring |
| Tool error handling | ToolNode handle_tool_errors | Agent retries with error text | Error returned to model as text | FunctionExecutionResult(is_error=True) to model |
| Async tools | Supported | Supported | Supported | Supported (awaited) |
| Loop control | Graph edges / recursion_limit | max_iter | max_turns | max_tool_iterations, team termination |
| Tool messages visible | State messages | Task output / callbacks | RunItems | ToolCallRequestEvent / ToolCallExecutionEvent in stream |

---

## ⚠️ Common Mistakes
❌ Mistake: Writing a tool without type hints or a docstring: the model gets a poor schema and picks wrong arguments.
✅ Correct: Always type every parameter and write a one-line docstring that says what the tool does and returns.

❌ Mistake: Assuming a tool exception stops the run.
✅ Correct: In AutoGen it becomes an error result the model can read. Check `is_error` and decide: retry, fall back or surface to the user.

❌ Mistake: Reading `messages[-1].content` when `reflect_on_tool_use=False` and expecting a polished sentence.
✅ Correct: Set `reflect_on_tool_use=True` for natural language, or format the summary with `tool_call_summary_format`.

❌ Mistake: Putting slow blocking code in an async tool (requests.get, time.sleep).
✅ Correct: Use async libraries (httpx) or `asyncio.to_thread`, otherwise the whole event loop stalls.

---

## 🧠 Tricky Interview Question
Your tariff agent sometimes returns the wrong duty although the tool is correct. Where do you look?

Answer: Print the whole trace, not only the last message. Usually the model passed wrong arguments (for example a chapter instead of the full HS code) because the schema was vague, or the model ignored the tool result. Fix the docstring and parameter types, add argument validation inside the tool (raise ValueError with a clear message so the model can self-correct), and set `reflect_on_tool_use=True`. Also check `is_error` flags in `ToolCallExecutionEvent`: a swallowed error often looks like a hallucination.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you give an AssistantAgent a tool?
A1: Pass a Python function in `tools=[fn]`. Type hints and the docstring become the schema.

Q2: [Medium] What does reflect_on_tool_use do?
A2: If True the agent makes one more model call after tools run so the model writes a final natural-language answer; if False it returns a summary of tool output using `tool_call_summary_format`.

Q3: [Hard] What happens when a tool raises an exception?
A3: AutoGen catches it and returns a `FunctionExecutionResult` with `is_error=True` and the error text. The model sees it and may retry with new arguments. The example prints these captured errors (`'9999'` KeyError).

Q4: [Hard] How do you stop an agent from looping on tools forever?
A4: Set `max_tool_iterations`, add a team termination condition (MaxMessageTermination, TokenUsageTermination) and wrap the call in `asyncio.wait_for`.

Q5: [System Design] Design a tool layer for 200 tariff tools.
A5: Do not load all 200 into every prompt. Group tools into specialist agents, use a `Workbench` or per-agent subsets, add argument validation, per-tool timeouts, audit logs of every call, idempotent read-only tools by default and an approval step for write tools.

---

## 💰 Cost Impact
Each tool round adds model input tokens: tool schemas (about 50-150 tokens per tool, an estimate) plus the growing history. `reflect_on_tool_use=True` adds one extra model call per turn. Formula: `cost = (calls * (schema_tokens + history_tokens)) * in_price + out_tokens * out_price`. Tips: keep tool count small per agent, keep docstrings short, return compact tool results (not whole tables), cap `max_tool_iterations`. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- The model needs exact data or an action (rates, DB, API).
- You want an audit trail of every call (events in the stream).
- Logic is deterministic and testable in plain Python.

❌ Avoid when:
- The answer is pure language work with no data lookup.
- The tool is dangerous and has no approval step (see 146).
- You have hundreds of tools in one agent (split agents instead).

---

## 📊 Visual Diagram
```
 user task
    |
    v
 AssistantAgent --(messages + tool schemas)--> Model client
    ^                                              |
    |                                       FunctionCall(hs_rate, {code})
    |                                              v
    |                     ToolCallRequestEvent -> run hs_rate()
    |                                              |
    |                     ToolCallExecutionEvent <-+  (ok or is_error)
    |                                              |
    +---- reflect_on_tool_use? -- yes --> 2nd model call -> final text
                                   no  --> tool summary text
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Tool | Python function the model may call | Python function जिसे model call कर सकता है |
| FunctionCall | Model's request: name + JSON args | Model की माँग: नाम + JSON args |
| FunctionExecutionResult | Tool output or error sent back | Tool का output या error जो वापस जाता है |
| is_error | Flag marking a failed tool call | fail हुए tool call का flag |
| reflect_on_tool_use | Extra model call to phrase the answer | जवाब बनाने के लिए अतिरिक्त model call |
| max_tool_iterations | Cap on tool rounds per turn | एक turn में tool rounds की सीमा |
| ToolCallRequestEvent | Event: model asked for a tool | Event: model ने tool माँगा |

---

## ⚡ 3-Line Summary
English: An AssistantAgent runs plain Python functions the model asks for and returns results as observations.
Type hints and docstrings are the schema; tool errors become data, not crashes.
Cap iterations, validate arguments and watch token cost of schemas.
Hindi: AssistantAgent वे Python functions चलाता है जो model माँगता है और नतीजा observation के रूप में लौटाता है।
Type hints और docstring ही schema हैं; tool errors crash नहीं, data बनते हैं।
Iterations सीमित रखें, arguments validate करें और schemas का token cost देखें।

---

## ➡️ Next Topic
142. AutoGen Memory -- how agents remember facts across turns using the `Memory` protocol and `ListMemory`.

---
