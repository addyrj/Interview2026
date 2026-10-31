---

# 057. ReAct Prompting
# हिंदी में: ReAct Prompting

---

## 🔵 Simple Definition (English)
ReAct (Reason + Act) prompting makes the model alternate between Thought (reasoning), Action (a tool call such as search or lookup) and Observation (the tool result), until it can give a Final Answer. It grounds answers in real data instead of memory alone.

## 🔵 सरल परिभाषा (Hindi)
ReAct (Reason + Act) prompting में model बारी-बारी से Thought (सोच), Action (tool call, जैसे search या lookup) और Observation (tool का result) करता है, जब तक Final Answer न दे सके। इससे जवाब सिर्फ़ याददाश्त पर नहीं, असली data पर टिकते हैं।

---

## 🔴 Problem it Solves
- Pure reasoning (CoT) can hallucinate facts the model does not know.
- Pure tool use without reasoning picks wrong tools or loops.
- ReAct lets the model decide what to look up next based on what it just learned.

## 🔴 यह क्यों बना? (Hindi)
- सिर्फ़ reasoning (CoT) में model वे facts hallucinate कर सकता है जो उसे पता नहीं।
- Reasoning के बिना tool use गलत tool चुनता है या loop में फँसता है।
- ReAct में model अभी जो सीखा उसके आधार पर तय करता है कि आगे क्या देखना है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prompt describes the available tools and the Thought/Action/Observation format
Step 2 → Model writes Thought: what do I need to find out?
Step 3 → Model writes Action: tool_name[input]  (or a native tool call)
Step 4 → Your code runs the tool and returns Observation: <result>
Step 5 → Model reads the observation and writes the next Thought
Step 6 → Repeat steps 2-5 (with a maximum step limit)
Step 7 → Model writes Final Answer
Step 8 → Log the trace for debugging and audit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Prompt में उपलब्ध tools और Thought/Action/Observation format बताओ
Step 2 → Model Thought लिखता है: मुझे क्या पता करना है?
Step 3 → Model Action लिखता है: tool_name[input]  (या native tool call)
Step 4 → आपका code tool चलाकर Observation: <result> लौटाता है
Step 5 → Model observation पढ़कर अगला Thought लिखता है
Step 6 → Steps 2-5 दोहराओ (अधिकतम steps की सीमा के साथ)
Step 7 → Model Final Answer लिखता है
Step 8 → Debugging और audit के लिए trace log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Question: "What is the import duty on a Bluetooth speaker into India?"
Thought: I need the HS code. Action: `hs_lookup[bluetooth speaker]` Observation: 8518.22. Thought: now I need the duty for 8518.22 in India. Action: `duty_rate[8518.22, IN]` Observation: 20% BCD. Final Answer: 8518.22, basic duty 20% (plus other taxes). The duty number comes from the database, not from model memory.

**Amazon-style**: Order assistant: Thought: need order status. Action: `get_order[123]` ... Final answer with real status.

## 🟡 Real Example Hindi mein
**Tariff System**: सवाल: "India में Bluetooth speaker import पर कितनी duty है?"
Thought: पहले HS code चाहिए। Action: `hs_lookup[bluetooth speaker]` Observation: 8518.22। Thought: अब India में 8518.22 की duty चाहिए। Action: `duty_rate[8518.22, IN]` Observation: 20% BCD। Final Answer: 8518.22, basic duty 20% (और अन्य taxes)। Duty का number database से आया, model की याददाश्त से नहीं।

**Amazon-style**: Order assistant: Thought: order status चाहिए। Action: `get_order[123]` ... असली status के साथ final answer।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny ReAct loop with a scripted mock model and two tools (runs offline)
import re  # parse "Action: tool[input]"

def hs_lookup(q: str) -> str:
    return {"bluetooth speaker": "8518.22"}.get(q.lower(), "not found")  # fake tool 1

def duty_rate(q: str) -> str:
    return {"8518.22": "20% BCD"}.get(q, "not found")  # fake tool 2

TOOLS = {"hs_lookup": hs_lookup, "duty_rate": duty_rate}  # registry

SCRIPT = iter([  # mock model: replies in order (a real model reads the history instead)
    "Thought: I need the HS code.\nAction: hs_lookup[bluetooth speaker]",
    "Thought: Now I need the duty.\nAction: duty_rate[8518.22]",
    "Thought: I have everything.\nFinal Answer: HS 8518.22, duty 20% BCD",
])

def mock_model(history: str) -> str:
    return next(SCRIPT)  # next scripted reply

def react(question: str, max_steps: int = 5) -> str:
    history = f"Question: {question}\n"  # growing transcript
    for _ in range(max_steps):  # step limit prevents infinite loops
        reply = mock_model(history)  # model thinks
        history += reply + "\n"
        if "Final Answer:" in reply:  # done
            return reply.split("Final Answer:")[1].strip()
        m = re.search(r"Action:\s*(\w+)\[(.*?)\]", reply)  # parse action
        if not m:
            return "Error: no action"
        tool, arg = m.groups()
        fn = TOOLS.get(tool)  # unknown tool protection
        obs = fn(arg) if fn else f"unknown tool {tool}"  # run tool
        history += f"Observation: {obs}\n"  # feed result back
    return "Stopped: step limit"

print(react("Duty on Bluetooth speaker into India?"))
```

## 💻 Code Example — Advanced
```python
# Production-style: ReAct using native tool calling (openai>=1), async, with step limit and errors
import asyncio  # async runtime
import json  # tool args
from typing import Any, Callable  # types
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=20.0)  # shared client

def hs_lookup(query: str) -> str:
    return json.dumps({"hs_code": {"bluetooth speaker": "8518.22"}.get(query.lower(), None)})

def duty_rate(hs_code: str, country: str) -> str:
    return json.dumps({"duty": {"8518.22:IN": "20% BCD"}.get(f"{hs_code}:{country}", None)})

REGISTRY: dict[str, Callable[..., str]] = {"hs_lookup": hs_lookup, "duty_rate": duty_rate}

TOOLS: list[dict[str, Any]] = [
    {"type": "function", "function": {"name": "hs_lookup", "description": "Find HS code for a product",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "duty_rate", "description": "Duty for HS code and country",
     "parameters": {"type": "object", "properties": {"hs_code": {"type": "string"},
                    "country": {"type": "string"}}, "required": ["hs_code", "country"]}}},
]

async def react_agent(question: str, max_steps: int = 6) -> tuple[str, list[dict]]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "Think before acting. Use tools for facts. Never guess duty rates."},
        {"role": "user", "content": question}]
    trace: list[dict] = []  # audit trail of actions
    for _ in range(max_steps):  # bounded loop
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, tools=TOOLS, temperature=0)
        except APIError as exc:
            return f"LLM error: {exc}", trace
        msg = resp.choices[0].message
        if not msg.tool_calls:  # no action requested: final answer
            return msg.content or "", trace
        messages.append(msg)  # keep assistant tool-call message in history
        for call in msg.tool_calls:  # run each action
            try:
                args = json.loads(call.function.arguments)
                obs = REGISTRY[call.function.name](**args)  # observation
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                obs = json.dumps({"error": str(exc)})  # let the model see the error and recover
            trace.append({"tool": call.function.name, "args": call.function.arguments, "obs": obs})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": obs})
    return "Stopped: step limit reached", trace

# print(asyncio.run(react_agent("Duty on a Bluetooth speaker into IN?")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app

class Q(BaseModel):
    question: str  # user question

@app.post("/agent")
async def agent(q: Q) -> dict:
    answer, trace = await react_agent(q.question)  # run ReAct loop
    return {"answer": answer, "steps": len(trace), "trace": trace}  # trace helps debugging/audit
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph's prebuilt `create_react_agent` is a ReAct loop: LLM node -> tool node -> LLM node until no tool call. Prefer LangGraph over the older LangChain `AgentExecutor`.

```python
from langchain_core.tools import tool  # tool decorator
from langchain_openai import ChatOpenAI  # model
from langgraph.prebuilt import create_react_agent  # ready-made ReAct agent

@tool
def hs_lookup(query: str) -> str:
    """Find the HS code for a product."""  # docstring is the tool description
    return {"bluetooth speaker": "8518.22"}.get(query.lower(), "not found")

@tool
def duty_rate(hs_code: str, country: str) -> str:
    """Return the import duty for an HS code and country code."""
    return {"8518.22:IN": "20% BCD"}.get(f"{hs_code}:{country}", "not found")

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini", temperature=0), [hs_lookup, duty_rate])
# out = agent.invoke({"messages": [("user", "Duty on a Bluetooth speaker into IN?")]})
# print(out["messages"][-1].content)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No step limit
✅ Correct: Always cap steps and total tokens.

```python
# Wrong: while True: step()
# Right: for _ in range(max_steps): ...
```

❌ Mistake 2: Crashing when a tool fails
✅ Correct: Return the error as an observation so the model can adapt.

```python
# Wrong: obs = tool(**args)   # exception kills the run
# Right: try ... except Exception as e: obs = json.dumps({"error": str(e)})
```

---

## 🧠 Tricky Interview Question
**Q**: "Your ReAct agent repeats the same search 6 times and never answers. Why and how do you fix it?"

**Answer**: The observation did not contain what the model needed (empty/irrelevant result) and it has no memory that this action already failed, or the prompt does not tell it what to do when a tool returns nothing. Fixes: return informative observations ("no results, try a different keyword"), detect repeated identical actions and stop or force a different strategy, add a step limit with a graceful "I could not find it" answer, improve tool descriptions, and log traces to find the loop.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does ReAct stand for?
A1: Reason + Act: interleaving reasoning with tool actions.

Q2: [Easy] What are the three elements in the loop?
A2: Thought, Action, Observation.

Q3: [Medium] ReAct vs plain CoT?
A3: CoT only reasons from the model's own knowledge. ReAct can fetch external information, so it reduces hallucination for facts and works with live data.

Q4: [Medium] How is ReAct implemented with modern APIs?
A4: With native function/tool calling: the model returns tool calls, you execute them, append tool messages, and call the model again until no tool calls remain. Frameworks like LangGraph provide this loop.

Q5: [Hard] What are the risks of agents and how do you control them?
A5: Infinite loops, wrong tool use, prompt injection via tool results, cost growth and unsafe actions. Controls: step and token budgets, allow-lists, least-privilege tools, argument validation, human approval for risky actions, treating tool output as untrusted, tracing and evals of full trajectories.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers need live or private data (databases, APIs, search)
- Multi-step lookups where next step depends on previous result

❌ Avoid when:
- A fixed pipeline works (use a deterministic workflow, cheaper and more reliable)
- Strict latency limits

---

## 📊 Visual Diagram
```
 Question
    |
    v
 +--> Thought: what do I need?
 |        |
 |        v
 |    Action: tool(args) ---> [Tool/DB/API]
 |        |                       |
 |        v                       |
 |    Observation <---------------+
 |        |
 +--------+  (repeat until enough info or step limit)
          |
          v
     Final Answer
```

---

## 💰 Cost Impact
- Every loop iteration re-sends the growing history, so input tokens grow roughly quadratically with steps. A 5-step run may use 5x-10x the tokens of a single call.
- Example: 5 steps x about 1,500 average input tokens + 5 x 100 output = about 8,000 tokens per question.
- Optimise: keep tool outputs short (return only the needed fields), cap steps, use small models for simple tools, cache tool results, use prompt caching for the static system/tool block, and prefer fixed workflows for predictable tasks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ReAct | Reason + Act loop | सोचो + करो loop |
| Thought | Reasoning step | सोच का कदम |
| Action | Tool call | Tool call |
| Observation | Tool result | Tool का नतीजा |
| Trajectory | Full sequence of steps | पूरे steps का क्रम |
| Tool calling | Model requests functions | Model का function माँगना |

---

## ⚡ 3-Line Summary
English: ReAct alternates Thought, Action and Observation so answers are grounded in tools and data. Always set step limits, validate tool arguments and handle tool errors. Cost grows with each loop because history is re-sent.
Hindi: ReAct में Thought, Action और Observation बारी-बारी से चलते हैं, इसलिए जवाब tools और data पर आधारित होते हैं। Step limit रखो, tool arguments validate करो और tool errors संभालो। हर loop में history दोबारा जाती है इसलिए cost बढ़ती है।

---

## ➡️ Next Topic
**058. System Prompt Design** — how to write the base instructions that guide every conversation.
