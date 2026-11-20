---

# 131. AssistantAgent
# हिंदी में: AssistantAgent — LLM + tools वाला मुख्य agent
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`AssistantAgent` is the main LLM-backed agent of AutoGen v0.4 AgentChat. You give it a `model_client`, a `system_message` and optionally `tools`, `handoffs`, `memory`, a `model_context` and an `output_content_type`. It decides when to call tools, can loop over several tool rounds and can return structured (pydantic) output.

## 🔵 सरल परिभाषा (Hindi)
`AssistantAgent` AutoGen v0.4 AgentChat का मुख्य LLM agent है। इसे `model_client`, `system_message` और वैकल्पिक रूप से `tools`, `handoffs`, `memory`, `model_context` और `output_content_type` दिए जाते हैं। यह तय करता है कि tool कब call करना है, कई tool rounds चला सकता है और structured (pydantic) output लौटा सकता है।

---

## 🔴 Problem it Solves
A raw model client call only returns text. Real agents need: tool calling with argument validation, feeding tool results back, deciding whether to summarise the result, remembering context, handing off to other agents and returning parseable JSON. Without a standard agent class you re-implement this loop (and its bugs) for every project.

## 🔴 यह क्यों बना? (Hindi)
सीधा model call सिर्फ़ text देता है। असली agents को चाहिए: argument validation के साथ tool calling, tool result वापस model को देना, तय करना कि result का summary बनाना है या नहीं, context याद रखना, दूसरे agents को handoff और parseable JSON लौटाना। standard agent class के बिना हर project में यह loop (और उसके bugs) दोबारा लिखना पड़ता है।

---

## 🟢 How it Works

```
Step 1 -> on_messages receives new messages; they are added to model_context
Step 2 -> Memory (if any) is queried and injected into the context
Step 3 -> LLM call with system_message + context + tool schemas
Step 4 -> If the model returns tool calls -> ToolCallRequestEvent
Step 5 -> Tools run (async-aware, errors captured as is_error=True) -> ToolCallExecutionEvent
Step 6 -> reflect_on_tool_use=True: second LLM call to write the final answer; False: tool_call_summary_format is returned
Step 7 -> max_tool_iterations > 1: loop steps 3-6 until the model stops calling tools
Step 8 -> Handoff tool called -> HandoffMessage to another agent (Swarm)
Step 9 -> output_content_type set -> final reply parsed into StructuredMessage[Model]
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> on_messages नए messages लेता है; वे model_context में जुड़ते हैं
Step 2 -> Memory (अगर है) query होकर context में डलती है
Step 3 -> system_message + context + tool schemas के साथ LLM call
Step 4 -> model tool calls लौटाए -> ToolCallRequestEvent
Step 5 -> tools चलते हैं (async-aware, errors is_error=True में) -> ToolCallExecutionEvent
Step 6 -> reflect_on_tool_use=True: final जवाब के लिए दूसरा LLM call; False: tool_call_summary_format लौटता है
Step 7 -> max_tool_iterations > 1: model के tool call रोकने तक steps 3-6 दोहराओ
Step 8 -> handoff tool call हुआ -> दूसरे agent को HandoffMessage (Swarm)
Step 9 -> output_content_type सेट हो तो final reply StructuredMessage[Model] में parse होता है
```

---

## 🟡 Real World Example
**Tariff classifier with typed output.** The agent must return `{hs_code, rate, confidence}`. With `output_content_type=TariffAnswer` the final message is a validated pydantic object, so the API layer can return it directly and downstream code never regex-parses free text. If the model returns invalid JSON, the call fails and you map it to a 502 and retry or fall back.

## 🟡 Real Example Hindi mein
**Typed output वाला Tariff classifier.** Agent को `{hs_code, rate, confidence}` लौटाना है। `output_content_type=TariffAnswer` देने पर final message validated pydantic object होता है, इसलिए API layer उसे सीधे लौटा सकती है और downstream code को free text regex से parse नहीं करना पड़ता। Model का JSON गलत हो तो call fail होती है, आप उसे 502 में map करके retry या fallback करते हैं।

---

## 💻 Code Example — Basic
Basic: a tool call with `reflect_on_tool_use=True`, printing every event type and the token usage of the last message.

```python
# AssistantAgent: tool + reflect_on_tool_use + token usage (offline)
import asyncio                                                    # async
from autogen_agentchat.agents import AssistantAgent              # the agent
from autogen_core import FunctionCall                             # scripted tool call
from autogen_core.models import CreateResult, RequestUsage        # scripted model result
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

def get_tariff_rate(hs_code: str) -> str:                         # tool with type hints
    """Return duty rate for an HS code."""
    return {"6109.10": "20%"}.get(hs_code, "unknown")

INFO = {"function_calling": True, "vision": False, "json_output": False,
        "family": "unknown", "structured_output": False}          # fake model capabilities

async def main() -> None:
    call = FunctionCall(id="1", name="get_tariff_rate", arguments='{"hs_code": "6109.10"}')
    client = ReplayChatCompletionClient([
        CreateResult(finish_reason="function_calls", content=[call],
                     usage=RequestUsage(prompt_tokens=0, completion_tokens=0), cached=False),
        "The duty is 20%.",
    ], model_info=INFO)
    agent = AssistantAgent(
        "tariff", model_client=client, tools=[get_tariff_rate],
        reflect_on_tool_use=True,                                 # True: 2nd LLM call turns tool output into prose (extra tokens!)
        max_tool_iterations=1,                                    # default 1; >1 lets the agent chain several tool rounds
        system_message="You are a tariff expert. Use the tool for rates.",
    )
    res = await agent.run(task="Duty for 6109.10?")
    for m in res.messages:                                        # inspect every event type
        print(type(m).__name__, "|", getattr(m, "content", None))
    print("tokens:", res.messages[-1].models_usage)               # per-message usage (None for non-LLM events)

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: structured output with `output_content_type`, timeout and error mapping in a FastAPI endpoint.

```python
# AssistantAgent advanced: structured output + tool errors + timeout + FastAPI
import asyncio                                                    # async
from fastapi import FastAPI, HTTPException                        # web
from fastapi.testclient import TestClient                         # offline test
from pydantic import BaseModel                                    # schema for structured output
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.messages import StructuredMessage          # typed message
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

INFO = {"function_calling": True, "vision": False, "json_output": True,
        "family": "unknown", "structured_output": True}           # structured output needs this flag

class TariffAnswer(BaseModel):                                    # the contract the agent must return
    hs_code: str                                                  # classified code
    rate: str                                                     # duty rate
    confidence: float                                             # 0..1

def build_agent() -> AssistantAgent:
    client = ReplayChatCompletionClient(['{"hs_code": "6109.10", "rate": "20%", "confidence": 0.9}'], model_info=INFO)
    return AssistantAgent("classifier", model_client=client,
                          output_content_type=TariffAnswer,       # final message becomes StructuredMessage[TariffAnswer]
                          system_message="Classify the product. Reply in the required JSON schema.")

app = FastAPI()

@app.post("/classify", response_model=TariffAnswer)
async def classify(body: dict) -> TariffAnswer:
    agent = build_agent()                                         # fresh agent = fresh model_context
    try:
        res = await asyncio.wait_for(agent.run(task=body.get("product", "")), timeout=20)
    except asyncio.TimeoutError:
        raise HTTPException(504, "model timeout")
    except Exception as exc:                                      # bad JSON from model, auth errors, etc.
        raise HTTPException(502, f"model error: {exc}")
    last = res.messages[-1]                                       # final message
    if not isinstance(last, StructuredMessage):                   # defensive: model ignored the schema
        raise HTTPException(502, "no structured output")
    return last.content                                           # already a TariffAnswer instance

if __name__ == "__main__":
    print(TestClient(app).post("/classify", json={"product": "cotton t-shirt"}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Tool calling | ToolNode + bind_tools | Agent tools list | Agent(tools=[...]) | AssistantAgent(tools=[...]) |
| Structured output | with_structured_output | output_pydantic on Task | output_type on Agent | output_content_type |
| Multi tool rounds | Graph loop | max_iter | Runner loop (max_turns) | max_tool_iterations |
| Handoffs | Command / edges | Delegation | handoffs=[...] | handoffs=[...] with Swarm |
| Memory | Store / checkpointer | Memory modules | Sessions | memory=[...] + model_context |
| Tool errors | ToolNode handle_tool_errors | Retries/guardrails | Error as tool output | is_error result fed back to model |

---

## ⚠️ Common Mistakes
❌ Mistake: Setting `tools=` on a model whose `model_info['function_calling']` is False: ValueError at construction (seen with the replay client).
✅ Correct: Use a model that supports function calling, or declare it correctly for custom clients.

❌ Mistake: Expecting a tool exception to crash the run. AutoGen catches it and returns `is_error=True` with the message to the model.
✅ Correct: Decide the policy: let the model retry, or validate inside the tool and return a clear error string.

❌ Mistake: Sharing one `AssistantAgent` across users: its `model_context` accumulates everyone's messages.
✅ Correct: Create one per session or call `on_reset`.

❌ Mistake: Tools without type hints or docstrings: the schema sent to the model is poor, so the model misuses the tool.
✅ Correct: Add type hints, `Annotated[str, 'description']` and a docstring.

---

## 🧠 Tricky Interview Question
Your agent calls a tool, the tool returns a 20 KB JSON, and the next LLM call is slow and expensive. What do you do?

Answer: The raw tool result is added to the context and re-sent on every later call. Fixes: (1) shrink inside the tool: return only the fields the model needs; (2) use `tool_call_summary_formatter` / `tool_call_summary_format` so the reply is short when `reflect_on_tool_use=False`; (3) use a bounded `model_context` (keep last N messages) so old large results fall out; (4) for big documents store them outside and return an id plus a short summary, with a second tool to fetch pieces. Measure with `models_usage.prompt_tokens` before and after.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `reflect_on_tool_use` do?
A1: If True, after tools run the agent makes another model call so the model writes a natural-language answer from the tool results. If False, it returns the tool results formatted by `tool_call_summary_format` (default `{result}`). Cost: one more LLM call.

Q2: [Medium] How does `AssistantAgent` handle tool errors?
A2: Exceptions are caught and returned as a `FunctionExecutionResult` with `is_error=True` and the error text, which is fed back to the model (verified offline: message 'db down' arrived as an error result).

Q3: [Hard] What is `max_tool_iterations`?
A3: The maximum number of consecutive model-to-tool rounds in one turn (default 1 in 0.7.5). Raise it for tasks needing chained lookups.

Q4: [Hard] How do you get typed JSON output?
A4: Pass a pydantic class as `output_content_type`; the final message becomes `StructuredMessage[YourModel]`. The model must support structured output (declared in `model_info`).

Q5: [System Design] Design an agent that classifies goods, checks restrictions and cites sources, with predictable cost.
A5: `AssistantAgent` with 2 tools (hs_search, restriction_lookup), `max_tool_iterations=3`, `output_content_type` with a `sources: list[str]` field, bounded `model_context`, timeouts, per-request token budget checked from `models_usage`, and a cheaper model for the search step if you split into two agents.

---

## 💰 Cost Impact
Each LLM call = system message + tool schemas + context + output. Tool schemas are re-sent every call: 5 tools can add several hundred prompt tokens per call. A turn with one tool use and `reflect_on_tool_use=True` makes 2 LLM calls; `max_tool_iterations=3` can make up to roughly 4. Formula: `turn_tokens = sum over calls (prompt_i + completion_i)`, with `prompt_i` growing as tool results join the context. Optimisations: fewer, tighter tools; `reflect_on_tool_use=False` when raw output is acceptable; bounded `model_context`; a smaller model for simple lookups. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Single agent with tools.
- You need typed output for an API.
- Agent in a team (round robin, selector, swarm).
- Handoff-based routing.

❌ Avoid when:
- A deterministic step with no language need: use a plain function or `BaseChatAgent`.
- Very long-running workflows needing durable checkpoints per step: add external state or use a workflow engine.

---

## 📊 Visual Diagram
```
 task --> [model_context] --> LLM(system + tool schemas)
                                   |
                  +----------------+-----------------+
                  | tool calls?                      | text / JSON
                  v                                  v
        ToolCallRequestEvent                  final message
                  |                         (TextMessage or
                  v                          StructuredMessage[T])
         run tools (errors -> is_error)
                  |
                  v
        ToolCallExecutionEvent --reflect_on_tool_use--> LLM again --> final answer
                  | (max_tool_iterations loops)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| system_message | Fixed instruction at top of every prompt | हर prompt के ऊपर स्थायी instruction |
| tools | Functions the model may call | जो functions model call कर सकता है |
| reflect_on_tool_use | Extra LLM call to explain tool output | tool output समझाने वाला अतिरिक्त LLM call |
| max_tool_iterations | Max chained tool rounds per turn | एक turn में अधिकतम tool rounds |
| model_context | History sent to the LLM | LLM को भेजा जाने वाला history |
| output_content_type | Pydantic class for typed reply | typed reply के लिए pydantic class |
| handoffs | Targets this agent can transfer to | जिन agents को control दे सकता है |
| memory | Pluggable long-term memory | लंबी अवधि की memory |

---

## ⚡ 3-Line Summary
English: AssistantAgent = model client + system message + tools (+ handoffs, memory, structured output).
Tool errors come back to the model as error results; `reflect_on_tool_use` costs one extra LLM call.
Create one per session and keep tool results small to control prompt tokens.
Hindi: AssistantAgent = model client + system message + tools (+ handoffs, memory, structured output)।
Tool errors model को error result के रूप में लौटते हैं; `reflect_on_tool_use` से एक अतिरिक्त LLM call लगता है।
हर session के लिए एक बनाएँ और prompt tokens नियंत्रित करने के लिए tool results छोटे रखें।

---

## ➡️ Next Topic
132. UserProxyAgent -- how a human joins the loop for approvals and corrections.

---
