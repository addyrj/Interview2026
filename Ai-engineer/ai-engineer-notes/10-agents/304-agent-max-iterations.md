---

# 304. Agent Max Iterations
# हिंदी में: Agent Max Iterations

---

## 🔵 Simple Definition (English)
Max iterations is a hard cap on how many reasoning-and-tool turns an agent may take for one request. In LangChain `AgentExecutor(max_iterations=15)` is the default; in LangGraph the equivalent is `recursion_limit` (default 25 supersteps). When the cap is hit, the run is stopped so the agent cannot loop forever.

## 🔵 सरल परिभाषा (Hindi)
Max iterations एक request के लिए agent कितने reasoning-और-tool turns ले सकता है उसकी कठोर सीमा है। LangChain में `AgentExecutor(max_iterations=15)` default है; LangGraph में इसके बराबर `recursion_limit` है (default 25 supersteps)। सीमा आने पर run रोक दिया जाता है ताकि agent हमेशा loop न करता रहे।

---

## 🔴 Problem it Solves
Each iteration costs an LLM call plus tool latency, and the prompt grows each time. A confused agent can run dozens of turns. The cap is the simplest, most reliable circuit breaker for cost, latency and runaway behaviour.

## 🔴 यह क्यों बना? (Hindi)
हर iteration में एक LLM call और tool latency लगती है, और prompt हर बार बड़ा होता है। भ्रमित agent दर्जनों turns चला सकता है। यह सीमा cost, latency और बेकाबू व्यवहार के लिए सबसे सरल और भरोसेमंद circuit breaker है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Set max_iterations (e.g. 6) based on measured task complexity
Step 2 → Each loop turn increments a counter
Step 3 → If the model finishes first -> normal answer
Step 4 → If counter reaches the cap -> loop is cut
Step 5 → early_stopping_method decides the output ("force" message or "generate" answer)
Step 6 → App logs the event and returns a graceful message
Step 7 → Tune: look at p50/p95 steps, failures hitting the cap, and cost
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → मापी गई task जटिलता के आधार पर max_iterations तय करो (जैसे 6)
Step 2 → हर loop turn counter बढ़ाता है
Step 3 → Model पहले खत्म करे -> सामान्य जवाब
Step 4 → Counter सीमा पर पहुँचे -> loop कट जाता है
Step 5 → early_stopping_method तय करता है output ("force" संदेश या "generate" जवाब)
Step 6 → App event log करके graceful संदेश लौटाता है
Step 7 → Tune: p50/p95 steps, सीमा छूने वाली failures और cost देखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Typical successful run: search codes (1), get duty (2), final (3). Measured p95 = 5 steps. We set `max_iterations=8`. An ambiguous product ("device") makes the model keep searching; at step 8 the system stops and asks the user: "Please describe the product more precisely." Better than 15 wasted calls.

**Zomato AI**: a booking agent with cap 6 hands over to a human if not done.

## 🟡 Real Example Hindi mein
**Tariff System**: सामान्य सफल run: codes search (1), duty निकालो (2), final (3)। मापा गया p95 = 5 steps। हमने `max_iterations=8` रखा। अस्पष्ट product ("device") पर model search करता रहता है; step 8 पर system रुककर user से पूछता है: "कृपया product को और साफ़ बताइए।" यह 15 बेकार calls से बेहतर है।

**Zomato AI**: cap 6 वाला booking agent पूरा न हो तो human को सौंप देता है।

---

## 💻 Code Example — Basic
```python
# Basic: measure step counts and pick a cap from data (pure Python, runs offline)
import statistics                                        # percentile helper

# Steps used by 20 past successful agent runs (pretend logs)
steps_used: list[int] = [3, 3, 4, 3, 5, 3, 4, 3, 3, 6, 4, 3, 5, 3, 4, 3, 7, 3, 4, 5]

def percentile(data: list[int], p: float) -> float:
    """Simple percentile using sorted data."""
    ordered = sorted(data)
    idx = min(len(ordered) - 1, int(round(p * (len(ordered) - 1))))   # nearest rank
    return float(ordered[idx])

p50, p95, worst = percentile(steps_used, 0.5), percentile(steps_used, 0.95), max(steps_used)
print(f"mean={statistics.mean(steps_used):.1f} p50={p50} p95={p95} max={worst}")
cap = int(p95) + 2                                       # headroom above p95
print("suggested max_iterations =", cap)

def run_with_cap(needed_steps: int, cap: int) -> str:
    """Simulate an agent that needs `needed_steps` to finish."""
    for i in range(1, cap + 1):                          # iterations 1..cap
        if i >= needed_steps:
            return f"done in {i} steps"
    return f"stopped at cap={cap} (needed {needed_steps})"

print(run_with_cap(4, cap))                              # finishes
print(run_with_cap(30, cap))                             # stuck agent is cut off
```

## 💻 Code Example — Advanced
```python
# Production: AgentExecutor and LangGraph caps, graceful handling, async
import asyncio                                            # async runtime
import logging                                            # logs
from typing import Any                                    # typing
from langchain.agents import AgentExecutor, create_tool_calling_agent   # pip install langchain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.errors import GraphRecursionError

logger = logging.getLogger("iterations")

@tool
def search_hs_codes(query: str) -> str:
    """Search HS codes by product description."""
    return "no clear match"                               # simulates an ambiguous search

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You classify products into HS codes using tools."),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# 1) Classic AgentExecutor
executor = AgentExecutor(
    agent=create_tool_calling_agent(llm, [search_hs_codes], prompt),
    tools=[search_hs_codes],
    max_iterations=6,                                     # hard cap on turns
    max_execution_time=30,                                # seconds, checked between steps
    early_stopping_method="force",                        # return stop message at the cap
    handle_parsing_errors=True,                           # do not crash on bad model output
    return_intermediate_steps=True,                       # keep trace for logs
)

async def classify(question: str) -> dict[str, Any]:
    try:
        out = await executor.ainvoke({"input": question})
    except Exception as exc:
        logger.exception("executor failed")
        return {"answer": "internal error", "capped": False}
    capped = "Agent stopped due to" in str(out.get("output", ""))   # default stop message text
    return {"answer": out["output"], "capped": capped, "steps": len(out.get("intermediate_steps", []))}

# 2) LangGraph version: recursion_limit counts graph steps (each node run), not just tool calls
graph_agent = create_react_agent(llm, [search_hs_codes])
def classify_graph(question: str) -> dict[str, Any]:
    try:
        res = graph_agent.invoke({"messages": [("user", question)]}, {"recursion_limit": 12})
        return {"answer": res["messages"][-1].content, "capped": False}
    except GraphRecursionError:
        return {"answer": "Please describe the product more precisely.", "capped": True}

if __name__ == "__main__":
    print(asyncio.run(classify("Classify: device")))
    print(classify_graph("Classify: device"))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                              # framework
from pydantic import BaseModel

app = FastAPI()

class Q(BaseModel):
    question: str

@app.post("/classify")
async def classify_route(q: Q) -> dict:
    result = await classify(q.question)                  # from Advanced
    # 200 with a flag lets the UI show a follow-up question; 5xx would hide a recoverable case
    return result
```

---

## 🔗 LangChain / LangGraph Connection
- `AgentExecutor`: `max_iterations` counts agent loop turns; `max_execution_time` stops by seconds.
- LangGraph: `recursion_limit` (config) counts supersteps. A ReAct loop uses about 2 supersteps per tool round (agent node + tools node), so `recursion_limit=12` is roughly 5-6 tool rounds. Exceeding it raises `GraphRecursionError`.

```python
config = {"recursion_limit": 12, "configurable": {"thread_id": "t1"}}   # per-invoke override
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating recursion_limit like the number of tool calls
✅ Correct: Each node execution counts; a tool round is about 2 steps.

```python
# Wrong: expecting 10 tool calls
agent.invoke(inp, {"recursion_limit": 10})
# Right: ~2 per tool round, so allow for it
agent.invoke(inp, {"recursion_limit": 2 * 10 + 1})
```

❌ Mistake 2: Setting a huge cap "just to be safe"
✅ Correct: Pick p95 + headroom, and handle the cap gracefully.

```python
# Wrong
AgentExecutor(agent=a, tools=t, max_iterations=100)
# Right
AgentExecutor(agent=a, tools=t, max_iterations=8, max_execution_time=30)
```

---

## 🧠 Tricky Interview Question
**Q**: "Raising max_iterations from 5 to 20 improved accuracy on your eval set by 3%, but cost doubled. Should you keep 20?"

**Answer**: Not automatically. Check where the gain comes from. If only a few hard cases need more steps, use adaptive budgets (higher cap for complex routes, low cap for simple ones) or fix the root cause (better tool descriptions, better retrieval, clearer prompts). Compare cost per correct answer, p95 latency and the share of runs that hit the cap. Perhaps a smarter first-step plan reaches the same accuracy within 8 steps.

---

## ⚫ Interview Questions + Answers

Q1: What is the default max_iterations in AgentExecutor?
A1: 15.

Q2: What is the LangGraph equivalent of max iterations?
A2: `recursion_limit` in the run config (default 25). It raises `GraphRecursionError` when exceeded.

Q3: What should the user see when the cap is reached?
A3: A friendly message with partial progress or a clarifying question, not a stack trace.

Q4: Is a cap enough to control cost?
A4: No. It limits turns, not tokens per turn. Add token budgets and output truncation.

Q5: (Hard) How do you choose the cap scientifically?
A5: Log steps per run on a representative eval set, compute the distribution, set the cap near p95 plus headroom, monitor the share of capped runs, investigate each capped run category (ambiguity, tool failure, prompt issue), and use per-route caps for different task types.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always for production agents

❌ Avoid when:
- Using the cap as the only safeguard (combine with time, token, repeat limits)

---

## 📊 Visual Diagram
```
 steps:   1     2     3     4     5     6     7     8 (cap)
          |     |     |     |     |     |     |     |
 normal:  tool  tool  FINAL
 stuck:   tool  tool  tool  tool  tool  tool  tool  X  -> STOP, graceful message
 cost:    ====  ====== ======== ==========  (grows each step)
```

---

## 💰 Cost Impact
- A stuck agent at cap 15 with 600 tokens/step history growth pays about 15 x base + 600 x 120 = large; at cap 6 it pays under a third.
- Typical savings: lowering the cap from 15 to 8 can cut worst-case spend by around 60 percent, with no effect on runs that finish earlier.
- Optimise: p95-based caps, per-route caps, truncated observations, cheaper model for exploratory steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| max_iterations | Cap on agent turns | Agent turns की सीमा |
| recursion_limit | LangGraph step cap | LangGraph step सीमा |
| Superstep | One graph execution round | Graph का एक execution round |
| early_stopping_method | Behaviour at the cap | सीमा पर व्यवहार |
| p95 | 95th percentile | 95वाँ percentile |
| Circuit breaker | Automatic cut-off | अपने-आप रोकने वाली व्यवस्था |

---

## ⚡ 3-Line Summary
English: Max iterations caps agent turns (AgentExecutor default 15, LangGraph recursion_limit default 25). Choose it from measured p95 steps, handle the cap gracefully, and combine it with time and token limits. It is the cheapest protection against runaway cost.
Hindi: Max iterations agent turns की सीमा है (AgentExecutor default 15, LangGraph recursion_limit default 25)। इसे मापे गए p95 steps से चुनें, cap आने पर graceful व्यवहार रखें, और time व token limits के साथ जोड़ें। यह बेकाबू cost से सबसे सस्ती सुरक्षा है।

---

## ➡️ Next Topic
**305. OpenAI Functions Agent** — the first function-calling agent type and how it relates to modern tool-calling agents.
