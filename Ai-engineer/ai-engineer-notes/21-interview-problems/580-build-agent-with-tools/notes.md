---

# 580. Build Agent with Tools
# हिंदी में: Tools वाला Agent बनाना

---

## 🔵 Simple Definition (English)
A tool-using agent is an LLM in a loop. The model returns either a final answer or a request to call a function (a tool) with JSON arguments. Your code validates and runs the tool, sends the result back, and repeats until the model answers.

## 🔵 सरल परिभाषा (Hindi)
Tool-using agent एक LLM है जो loop में चलता है। Model या तो final answer देता है या किसी function (tool) को JSON arguments के साथ call करने की request। आपका code validate करके tool चलाता है, result वापस भेजता है, और model के answer देने तक दोहराता है।

---

## 🔴 Problem it Solves
LLMs cannot look up live data, do exact arithmetic reliably, or change anything in the world. Tools give them facts (database), precision (calculators) and actions (create ticket). Hard-coding the sequence of steps is brittle; the model decides which tool to call and in what order.

## 🔴 यह क्यों बना? (Hindi)
LLM live data नहीं देख सकता, exact गणित में भरोसेमंद नहीं, और दुनिया में कुछ बदल नहीं सकता। Tools facts (database), precision (calculator) और actions (ticket बनाना) देते हैं। Steps hard-code करना कमजोर है; model तय करता है कौन सा tool, किस क्रम में।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Describe tools to the model (name, description, JSON schema)
Step 2 → Send user question + tool list
Step 3 → Model replies: tool_call(name, args) OR final text
Step 4 → Your code validates name + args against a whitelist
Step 5 → Run the tool, catch errors, return result as a tool message
Step 6 → Call model again with the result
Step 7 → Stop on final answer or max_steps
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Model को tools बताओ (नाम, description, JSON schema)
Step 2 → Question + tool list भेजो
Step 3 → Model: tool_call(name, args) या final text
Step 4 → Name और args whitelist से validate करो
Step 5 → Tool चलाओ, errors पकड़ो, result tool message में भेजो
Step 6 → Result के साथ model को फिर call करो
Step 7 → Final answer या max_steps पर रुको
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Duty on a $1000 smartphone?" The agent calls `lookup_hs_code("smartphone")` then `calc_duty("smartphone", 1000)` and answers "HS 8517.13, duty $200". The LLM never invents a rate; it quotes tool output. **Zomato-style**: `search_restaurants`, `check_eta`, `place_order`. **Amazon-style**: `track_order`, `start_return`.

## 🟡 Real Example Hindi mein
**Tariff System**: "$1000 के smartphone पर duty?" Agent `lookup_hs_code` फिर `calc_duty` call करता है और बताता है "HS 8517.13, duty $200"। LLM rate खुद नहीं गढ़ता, tool का output बताता है। **Zomato**: `search_restaurants`, `check_eta`, `place_order`। **Amazon**: `track_order`, `start_return`।

---

## 💻 Code Example — Basic
Full solution in `main.py` (two tools, scripted mock LLM, loop with step cap).

```python
# Basic: a registry of tools and a dispatcher
import json  # to pass results as text

def add_duty(value: float, rate: float) -> float:  # a simple tool
    return round(value * rate, 2)  # exact arithmetic, no LLM guessing

TOOLS = {"add_duty": add_duty}  # name -> function whitelist

call = {"tool": "add_duty", "args": {"value": 1000, "rate": 0.2}}  # what an LLM would return
fn = TOOLS.get(call["tool"])  # look up safely
result = fn(**call["args"]) if fn else "unknown tool"  # run only whitelisted tools
print(json.dumps({"result": result}))  # send this back as the tool message
```

## 💻 Code Example — Advanced
`main.py`: `run_tool` turns exceptions into JSON error observations so the model can self-correct, `run_agent` enforces `max_steps`, `arun_agent` is async. With a real provider, the same loop uses the native tool-calling API (illustrative):

```python
# Real tool calling with the OpenAI SDK shape (needs OPENAI_API_KEY; illustrative)
import json
from typing import Any

SPEC: list[dict[str, Any]] = [{  # tool schema sent to the model
    "type": "function",
    "function": {"name": "calc_duty", "description": "Compute import duty",
                 "parameters": {"type": "object",
                                "properties": {"product": {"type": "string"}, "value_usd": {"type": "number"}},
                                "required": ["product", "value_usd"]}},
}]

async def agent(client: Any, tools: dict, question: str, max_steps: int = 5) -> str:  # async loop
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]  # conversation
    for _ in range(max_steps):  # bounded loop
        resp = await client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=SPEC)  # call
        msg = resp.choices[0].message  # first choice
        if not msg.tool_calls:  # no tool requested
            return msg.content or ""  # final answer
        messages.append(msg)  # keep assistant tool request
        for tc in msg.tool_calls:  # may request several
            try:  # isolate failures
                out = tools[tc.function.name](**json.loads(tc.function.arguments))  # run tool
            except Exception as exc:  # report error to model
                out = {"error": str(exc)}
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out)})  # reply
    return "max_steps reached"  # safety stop
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from main import arun_agent  # from main.py

app = FastAPI()  # app

class AskIn(BaseModel):  # request
    question: str = Field(min_length=3, max_length=1000)  # user question

@app.post("/agent")  # route
async def ask(body: AskIn) -> dict[str, str]:  # handler
    answer = await arun_agent(body.question)  # run the loop
    return {"answer": answer}  # respond
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `@tool` decorator builds the schema from type hints and docstring; `llm.bind_tools([...])` attaches it. LangGraph's `create_react_agent` (prebuilt) wires the loop with `ToolNode`.

```python
# Illustrative (pip install langchain-core langgraph langchain-openai)
from langchain_core.tools import tool  # decorator

@tool  # schema comes from hints + docstring
def calc_duty(product: str, value_usd: float) -> float:  # tool function
    """Compute import duty in USD for a product."""
    return value_usd * 0.2  # fake flat rate for the demo

# from langgraph.prebuilt import create_react_agent
# agent = create_react_agent(model, [calc_duty])  # model: a chat model instance
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No step cap
✅ Correct: Always bound the loop.

```python
# Wrong: may loop forever and burn tokens
while True:
    pass
# Right
for _ in range(5):
    break
```

❌ Mistake 2: Crashing on tool errors / running arbitrary names
✅ Correct: Whitelist tools and return errors as observations.

```python
TOOLS = {"calc": lambda x: x}  # whitelist
name = "rm_rf"
# Wrong: globals()[name]()  -- executes anything the model says
# Right:
out = TOOLS[name]("1") if name in TOOLS else {"error": "no such tool"}
print(out)
```

---

## 🧠 Tricky Interview Question
**Q**: "The model keeps calling `lookup_hs_code` with 'phone' and the tool returns NOT_FOUND again and again. What do you change?"

**Answer**: Make errors informative ("unknown product 'phone'. Try: smartphone, laptop, tshirt"), improve the tool description and enum-constrain arguments, deduplicate identical failing calls in the loop (inject "you already tried this"), and cap steps. Return structured errors, not stack traces. Optionally add a fuzzy-match tool.

---

## ⚫ Interview Questions + Answers

Q1: Does the LLM execute the tool? (Easy)
A1: No. It only emits a request (name + JSON args). Your code executes it.

Q2: Why describe tools with JSON schema? (Easy)
A2: It tells the model valid argument names/types and lets you validate before running.

Q3: How do you make tools safe? (Medium)
A3: Whitelist, validate args (pydantic), least-privilege credentials, timeouts, idempotency keys for writes, human approval for destructive actions.

Q4: Parallel tool calls? (Medium)
A4: Models can return several calls in one turn; run independent ones with `asyncio.gather` and return each result with its `tool_call_id`.

Q5: How do you debug an agent that picks the wrong tool? (Hard)
A5: Trace every step (inputs, tool choice, outputs), review tool descriptions for overlap, reduce the tool count or route to sub-agents, add few-shot examples, evaluate on a golden set of tasks with expected tool sequences, and consider forcing `tool_choice` for deterministic steps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Needs live data, exact computation or side effects
- Steps vary by question

❌ Avoid when:
- The workflow is fixed (use a plain pipeline or a graph)
- Latency/cost budget cannot afford several LLM calls

---

## 📊 Visual Diagram
```
 question ─► LLM ──► final text? ──yes──► answer
              │ no
              ▼
        tool_call(name,args)
              ▼
     validate ─► run tool ─► result
              ▲                │
              └──── append ────┘   (max_steps guard)
```

---

## 💰 Cost Impact
Every loop iteration is a full LLM call that re-sends the growing message list plus tool schemas. Example (illustrative): 3 iterations x ~1,200 input tokens = 3,600 input tokens. Optimise: fewer, well-named tools; short descriptions; cheap model for routing; cap steps; cache tool results (same lookup twice); truncate large tool outputs before returning them to the model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool / function calling | Model requests a function run | Model function चलाने को कहता है |
| JSON schema | Describes arguments | Arguments का ढांचा |
| Observation | Tool result fed back | Tool का नतीजा |
| Agent loop | Think-act-observe cycle | सोचो-करो-देखो चक्र |
| max_steps | Loop safety cap | Loop की सीमा |
| Whitelist | Only approved tools | सिर्फ approved tools |

---

## ⚡ 3-Line Summary
English: An agent is an LLM in a loop that requests tools. Your code validates and runs them and returns results. Always cap steps and whitelist tools.
Hindi: Agent loop में चलने वाला LLM है जो tools माँगता है। आपका code validate करके चलाता है और result लौटाता है। Steps की सीमा रखो और tools whitelist करो।

---

## ➡️ Next Topic
**581. Build ReAct Agent** — the Thought/Action/Observation pattern behind the loop, with explicit reasoning.
