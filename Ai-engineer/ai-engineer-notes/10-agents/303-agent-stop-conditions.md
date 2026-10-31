---

# 303. Agent Stop Conditions
# हिंदी में: Agent Stop Conditions

---

## 🔵 Simple Definition (English)
Stop conditions are the rules that end an agent loop. The normal stop is "the model gives a final answer with no tool call". Safety stops are: max iterations, max time, token or cost budget, repeated identical actions, a tool error threshold, and a human cancel. Good agents have several of these, not just one.

## 🔵 सरल परिभाषा (Hindi)
Stop conditions वे नियम हैं जो agent loop को खत्म करते हैं। सामान्य stop: "model बिना tool call के final answer दे दे"। सुरक्षा stops: max iterations, max time, token/cost budget, बार-बार वही action, tool errors की सीमा, और human cancel। अच्छे agents में एक नहीं, कई stops होते हैं।

---

## 🔴 Problem it Solves
An agent is a loop driven by an LLM, and LLMs can get stuck: repeating a failing tool, asking itself the same question, or wandering. Without stop rules the loop burns money and time, and may hit rate limits or take unsafe actions repeatedly.

## 🔴 यह क्यों बना? (Hindi)
Agent LLM से चलने वाला loop है, और LLM अटक सकता है: fail होता tool दोहराना, वही सवाल खुद से पूछना, भटकना। Stop rules के बिना loop पैसा और समय जलाता है, rate limits तोड़ सकता है, और असुरक्षित actions बार-बार कर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Loop starts: iteration = 0, start_time = now, tokens_used = 0
Step 2 → Call the model
Step 3 → CHECK natural stop: no tool_calls? -> return final answer
Step 4 → CHECK budgets: iterations, seconds, tokens/cost
Step 5 → CHECK repetition: same tool + same args as before? -> stop
Step 6 → Run tools, count errors; too many consecutive errors -> stop
Step 7 → On any forced stop, return a graceful partial answer + reason
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Loop शुरू: iteration = 0, start_time = अभी, tokens_used = 0
Step 2 → Model call करो
Step 3 → स्वाभाविक stop जाँचो: tool_calls नहीं? -> final answer लौटाओ
Step 4 → Budgets जाँचो: iterations, seconds, tokens/cost
Step 5 → Repetition जाँचो: वही tool + वही args? -> रुक जाओ
Step 6 → Tools चलाओ, errors गिनो; लगातार बहुत errors -> रुक जाओ
Step 7 → Forced stop पर partial answer + कारण लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The agent searches HS codes. The search API starts returning errors. The model keeps retrying the same query. Stop rule "3 identical failing calls" ends the loop and the agent replies: "I could not reach the tariff search service; please retry or contact support" and logs a ticket. Without it, 15 iterations x 3 pages of history would have been billed.

**Amazon AI**: a refund agent stops after 6 steps or when cost exceeds a few cents and hands over to a human.

## 🟡 Real Example Hindi mein
**Tariff System**: Agent HS codes search करता है। Search API errors देने लगती है। Model वही query बार-बार चलाता है। नियम "3 बार वही failing call" loop रोक देता है और agent कहता है: "Tariff search service तक नहीं पहुँच सका; कृपया फिर कोशिश करें" और ticket log करता है। इसके बिना 15 iterations का बिल बनता।

**Amazon AI**: refund agent 6 steps या कुछ cents से ज़्यादा cost पर रुककर human को सौंप देता है।

---

## 💻 Code Example — Basic
```python
# Basic: a stop-condition checker for any agent loop (pure Python, runs offline)
import time                                              # wall-clock time
from dataclasses import dataclass, field                 # data helpers

@dataclass
class StopPolicy:
    max_iterations: int = 6          # hard cap on loop turns
    max_seconds: float = 20.0        # time budget
    max_tokens: int = 20_000         # token budget
    max_repeats: int = 2             # same (tool,args) allowed this many times
    max_errors: int = 3              # consecutive tool errors allowed

@dataclass
class LoopState:
    started: float = field(default_factory=time.monotonic)   # start time
    iterations: int = 0
    tokens: int = 0
    errors_in_row: int = 0
    seen: dict[tuple, int] = field(default_factory=dict)      # (tool,args) -> count

def should_stop(policy: StopPolicy, st: LoopState, tool: str | None, args: dict | None) -> str | None:
    """Return a reason string if the loop must stop, else None."""
    if st.iterations >= policy.max_iterations:
        return "max_iterations"
    if time.monotonic() - st.started > policy.max_seconds:
        return "max_time"
    if st.tokens >= policy.max_tokens:
        return "max_tokens"
    if st.errors_in_row >= policy.max_errors:
        return "too_many_errors"
    if tool is not None:
        key = (tool, tuple(sorted((args or {}).items())))    # hashable identity of the call
        st.seen[key] = st.seen.get(key, 0) + 1
        if st.seen[key] > policy.max_repeats:
            return "repeated_action"
    return None

# Demo: a "stuck" agent keeps calling the same failing tool
policy, state = StopPolicy(), LoopState()
for i in range(10):
    state.iterations += 1
    state.errors_in_row += 1                             # pretend tool failed
    reason = should_stop(policy, state, "search_hs_codes", {"query": "earbuds"})
    print(i, reason)
    if reason:
        break
```

## 💻 Code Example — Advanced
```python
# Production: agent loop with layered stop conditions, async, graceful partial answers
import asyncio                                            # async runtime
import logging                                            # logs
import time                                               # timing
from typing import Any                                    # typing
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

logger = logging.getLogger("agent_stop")

@tool
async def search_hs_codes(query: str) -> str:
    """Search HS codes by product description."""
    return "851830 Headphones"

TOOLS = {t.name: t for t in [search_hs_codes]}

async def run_agent(question: str, max_iter: int = 6, max_seconds: float = 25, max_repeat: int = 2) -> dict[str, Any]:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(list(TOOLS.values()))
    msgs: list[BaseMessage] = [SystemMessage(content="Use tools when needed, then answer."), HumanMessage(content=question)]
    started, seen, tokens, errors = time.monotonic(), {}, 0, 0
    for i in range(max_iter):                             # STOP 1: iteration cap
        if time.monotonic() - started > max_seconds:      # STOP 2: time cap
            return {"answer": "Partial: time limit reached", "stop": "max_time", "steps": i}
        ai = await llm.ainvoke(msgs)
        tokens += (ai.usage_metadata or {}).get("total_tokens", 0)
        msgs.append(ai)
        if not ai.tool_calls:                             # STOP 0: natural finish
            return {"answer": str(ai.content), "stop": "final_answer", "steps": i + 1, "tokens": tokens}
        for call in ai.tool_calls:
            key = (call["name"], str(sorted(call["args"].items())))
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > max_repeat:                    # STOP 3: repetition
                return {"answer": "Partial: agent was repeating itself", "stop": "repeated_action", "steps": i + 1}
            try:
                out = await asyncio.wait_for(TOOLS[call["name"]].ainvoke(call["args"]), timeout=8)
                errors = 0                                # success resets error counter
            except Exception as exc:
                out, errors = f"error: {exc}", errors + 1
                if errors >= 3:                           # STOP 4: consecutive errors
                    return {"answer": "Partial: tools are failing", "stop": "too_many_errors", "steps": i + 1}
            msgs.append(ToolMessage(content=str(out), tool_call_id=call["id"]))
    return {"answer": "Partial: iteration limit reached", "stop": "max_iterations", "steps": max_iter, "tokens": tokens}

if __name__ == "__main__":
    print(asyncio.run(run_agent("HS code for bluetooth earbuds?")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException               # framework
from pydantic import BaseModel

app = FastAPI()

class Q(BaseModel):
    question: str

@app.post("/agent")
async def agent(q: Q) -> dict:
    try:
        result = await asyncio.wait_for(run_agent(q.question), timeout=40)   # outer request timeout
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="agent timed out")
    result["complete"] = result["stop"] == "final_answer"   # let the client know if it was forced
    return result
```

---

## 🔗 LangChain / LangGraph Connection
`AgentExecutor` has `max_iterations`, `max_execution_time`, and `early_stopping_method`. In LangGraph, the loop ends when the router sends to `END` (no tool calls); the safety stop is `recursion_limit` which raises `GraphRecursionError`.

```python
from langgraph.prebuilt import create_react_agent
from langgraph.errors import GraphRecursionError
agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [search_hs_codes])
try:
    agent.invoke({"messages": [("user", "HS code for earbuds?")]}, {"recursion_limit": 8})
except GraphRecursionError:
    print("stopped: recursion limit")                    # return a graceful message instead
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Relying only on the model to say "I'm done"
✅ Correct: Add hard external limits (iterations, time, budget).

```python
# Wrong
while True:
    step = llm.invoke(msgs)
# Right
for _ in range(MAX_ITER):
    step = llm.invoke(msgs)
```

❌ Mistake 2: Forced stop returns an exception or empty result
✅ Correct: Return a partial answer plus the stop reason.

```python
# Wrong
raise RuntimeError("too many steps")
# Right
return {"answer": "Partial result so far...", "stop": "max_iterations"}
```

---

## 🧠 Tricky Interview Question
**Q**: "Your agent has max_iterations=10, yet one request still cost 50 times the average. How?"

**Answer**: An iteration cap limits turns, not tokens per turn. A single tool returned a huge document (100K tokens) that went into every following turn, or parallel tool calls produced many results per turn. Add a token/cost budget, truncate tool outputs, cap parallel calls, and use a smaller context for observations. Also add a time limit, since one slow tool can occupy a worker for minutes.

---

## ⚫ Interview Questions + Answers

Q1: What is the natural stop condition of a tool-calling agent?
A1: The model replies with a message that has no tool calls; that is the final answer.

Q2: Name three safety stop conditions.
A2: Max iterations, max execution time, and repeated actions. Also token/cost budget and consecutive tool errors.

Q3: What does `early_stopping_method` do in AgentExecutor?
A3: It controls what happens when the limit is hit. `"force"` returns a fixed stop message; `"generate"` (supported in some versions) asks the LLM for a final answer from the steps so far.

Q4: How do you detect an agent that is looping?
A4: Hash (tool, args) per call and count repeats, or detect identical consecutive observations; stop or inject a hint to change strategy.

Q5: (Hard) How would you design stop conditions for a long-running, human-supervised agent?
A5: Use LangGraph checkpointing; stop at risky steps with `interrupt`; keep budgets per task; persist state so a stop is resumable, not lost; provide a cancel API; return structured stop reasons for dashboards and alerts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production agent (always)

❌ Avoid when:
- Setting limits so low that normal tasks fail; measure typical step counts first (p95) and set the cap slightly above

---

## 📊 Visual Diagram
```
        +-----------------------+
        |  call model           |
        +-----------+-----------+
                    v
         tool_calls? --no--> FINAL ANSWER (stop)
                    | yes
                    v
   iterations/time/tokens over budget? --yes--> PARTIAL ANSWER (stop)
                    | no
   same call repeated too often?       --yes--> PARTIAL ANSWER (stop)
                    | no
              run tools -> errors in a row? --yes--> STOP
                    | no
                    +---- back to "call model"
```

---

## 💰 Cost Impact
- Worst-case cost = max_iterations x (growing prompt). A cap of 6 vs 15 can cut worst-case cost by more than half.
- Token budgets bound cost per request; time limits bound worker usage.
- Optimise: measure the real step distribution, set p95-based caps, truncate observations, and alert when stops other than `final_answer` exceed a threshold (indicates bugs or abuse).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stop condition | Rule ending the loop | Loop खत्म करने का नियम |
| Final answer | Reply without tool call | बिना tool call वाला जवाब |
| Budget | Limit on tokens/cost/time | Tokens/cost/समय की सीमा |
| Repetition guard | Detects repeated calls | दोहराव पकड़ने वाला guard |
| Graceful degradation | Partial result on failure | विफलता पर आंशिक नतीजा |
| recursion_limit | LangGraph step cap | LangGraph का step cap |

---

## ⚡ 3-Line Summary
English: Agents stop naturally when the model gives a final answer, and forcibly through iteration, time, token, repetition and error limits. Always return a partial answer with a stop reason. Limits protect cost, latency and safety.
Hindi: Agent स्वाभाविक रूप से तब रुकता है जब model final answer दे, और जबरन iteration, समय, token, दोहराव व error limits से। हमेशा stop reason के साथ partial answer लौटाएँ। Limits cost, latency और safety की रक्षा करती हैं।

---

## ➡️ Next Topic
**304. Agent Max Iterations** — choosing and tuning the iteration cap in detail.
