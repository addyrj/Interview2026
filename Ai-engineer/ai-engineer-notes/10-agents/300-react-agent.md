---

# 300. ReAct Agent
# हिंदी में: ReAct Agent (पूरा agent)

---

## 🔵 Simple Definition (English)
A ReAct agent is a complete system built around the ReAct loop: an LLM (the brain), tools (hands), memory (conversation and state), a prompt (instructions), and a controller (limits, errors, logging). It decides step by step how to achieve a goal instead of following a fixed script.

## 🔵 सरल परिभाषा (Hindi)
ReAct agent ReAct loop पर बना पूरा system है: LLM (दिमाग), tools (हाथ), memory (बातचीत और state), prompt (निर्देश) और controller (limits, errors, logging)। यह तय script की जगह लक्ष्य पाने के लिए कदम-दर-कदम खुद निर्णय लेता है।

---

## 🔴 Problem it Solves
Pipelines break on open-ended requests: "Is this shipment compliant, and what will it cost?" may need 2 or 12 steps depending on the data. Hard-coding every path is impossible. An agent adapts, but only if it is wrapped with memory, limits and safety, otherwise it loops, forgets context, or takes unsafe actions.

## 🔴 यह क्यों बना? (Hindi)
Open-ended सवालों पर pipelines टूट जाते हैं: "यह shipment compliant है और cost क्या होगी?" में data के हिसाब से 2 या 12 steps लग सकते हैं। हर रास्ता hard-code करना असंभव है। Agent adapt करता है, पर memory, limits और safety के साथ ही; वरना वह loop में फँसता है, context भूलता है या असुरक्षित actions लेता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Receive goal + load memory (chat history, user profile, prior results)
Step 2 → Build prompt: role, rules, tool list, memory, goal
Step 3 → LLM reasons and picks an action (tool) or answers
Step 4 → Controller validates the action (allowlist, args, permission, budget)
Step 5 → Execute tool; get observation; update state/memory
Step 6 → Loop until goal done, limit hit, or human input required
Step 7 → Return answer + trace; save conversation to memory
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → लक्ष्य लो + memory load करो (chat history, user profile, पिछले results)
Step 2 → Prompt बनाओ: role, rules, tool list, memory, goal
Step 3 → LLM सोचकर action (tool) चुनता है या जवाब देता है
Step 4 → Controller action validate करता है (allowlist, args, permission, budget)
Step 5 → Tool चलाओ; observation लो; state/memory update
Step 6 → लक्ष्य पूरा, limit या human input की ज़रूरत तक loop
Step 7 → जवाब + trace लौटाओ; conversation memory में सेव
```

---

## 🟡 Real World Example
**Tariff Classification System** agent: Goal "Classify this invoice and estimate duty." It reads invoice lines (file tool), classifies each line (search + LLM), looks up rates (DB tool), converts currency (API tool), totals (calculator), and flags uncertain lines for human review. Memory keeps the importer's previous classifications to stay consistent.

**Zomato AI**: a support agent with memory of the current order that can look up the order, refund (with approval), or hand over to a human.

## 🟡 Real Example Hindi mein
**Tariff System** agent: लक्ष्य "इस invoice को classify करो और duty अनुमानित करो।" वह invoice lines पढ़ता है (file tool), classify करता है, rates देखता है (DB tool), currency बदलता है (API tool), total निकालता है (calculator) और अनिश्चित lines को human review के लिए flag करता है। Memory importer की पिछली classifications याद रखती है।

**Zomato AI**: support agent जिसे current order की memory है; order देख सकता है, refund (approval के साथ) कर सकता है या इंसान को सौंप सकता है।

---

## 💻 Code Example — Basic
```python
# ReAct agent with memory + limits (offline demo using a scripted decision function)
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Memory:
    """Short-term conversation memory with a size cap."""
    turns: list[tuple[str, str]] = field(default_factory=list)
    max_turns: int = 6

    def add(self, role: str, text: str) -> None:
        self.turns.append((role, text))
        self.turns = self.turns[-self.max_turns:]          # keep only recent turns (token control)

    def render(self) -> str:
        return "\n".join(f"{r}: {t}" for r, t in self.turns)

def get_rate(code: str) -> str:
    return {"6109.10": "20%"}.get(code, "unknown")

@dataclass
class ReActAgent:
    decide: Callable[[str], dict]                          # stands in for the LLM: returns an action or answer
    tools: dict[str, Callable[[str], str]]
    memory: Memory = field(default_factory=Memory)
    max_steps: int = 5

    def run(self, goal: str) -> str:
        self.memory.add("user", goal)
        scratch = ""
        for _ in range(self.max_steps):
            decision = self.decide(self.memory.render() + "\n" + scratch)
            if "answer" in decision:                       # finished
                self.memory.add("agent", decision["answer"])
                return decision["answer"]
            tool = self.tools.get(decision["tool"])
            obs = tool(decision["input"]) if tool else "unknown tool"
            scratch += f"Action {decision['tool']}({decision['input']}) -> {obs}\n"
        return "I could not finish within the step limit."

# Fake brain: first call the tool, then answer using the observation
def fake_decide(text: str) -> dict:
    if "->" not in text:
        return {"tool": "get_rate", "input": "6109.10"}
    return {"answer": "Duty for 6109.10 is " + text.split("->")[-1].strip()}

agent = ReActAgent(fake_decide, {"get_rate": get_rate})
print(agent.run("Duty for cotton t-shirts (6109.10)?"))   # Duty for 6109.10 is 20%
print(agent.memory.render())
```

## 💻 Code Example — Advanced
```python
# Production agent with native tool calling, per-session memory, guardrails and budgets
import asyncio, json
from typing import Any
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

client = AsyncOpenAI()
SESSIONS: dict[str, list[dict[str, Any]]] = {}          # demo store; use Redis/DB in production
MAX_HISTORY = 12                                        # messages kept per session

class RateArgs(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")

async def get_rate(a: RateArgs) -> dict[str, Any]:
    return {"hs_code": a.hs_code, "duty_pct": 20}

TOOLS = {"get_rate": (RateArgs, get_rate)}
SCHEMA = [{"type": "function", "function": {
    "name": "get_rate", "description": "Duty percent for a KNOWN HS code (format 6109.10).",
    "parameters": {"type": "object", "properties": {"hs_code": {"type": "string"}}, "required": ["hs_code"]}}}]

SYSTEM = ("You are a customs tariff assistant. Use tools for facts. If a tool fails or data is missing, "
          "say so. Never invent rates. Ask the user when information is ambiguous.")

async def run_tool(name: str, raw: str) -> dict[str, Any]:
    if name not in TOOLS:
        return {"ok": False, "error": f"unknown tool {name}"}
    model, fn = TOOLS[name]
    try:
        return {"ok": True, "data": await asyncio.wait_for(fn(model.model_validate_json(raw)), 10)}
    except ValidationError as exc:
        return {"ok": False, "error": exc.errors()[0]["msg"]}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}

async def agent_turn(session_id: str, user_text: str, max_steps: int = 5) -> dict[str, Any]:
    history = SESSIONS.setdefault(session_id, [])
    history.append({"role": "user", "content": user_text})
    tokens = 0
    for _ in range(max_steps):
        msgs = [{"role": "system", "content": SYSTEM}] + history[-MAX_HISTORY:]
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", messages=msgs, tools=SCHEMA, temperature=0, max_tokens=300)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
        tokens += resp.usage.total_tokens if resp.usage else 0
        msg = resp.choices[0].message
        history.append(msg.model_dump(exclude_none=True))      # store assistant message
        if not msg.tool_calls:
            return {"ok": True, "answer": msg.content, "tokens": tokens}
        for call in msg.tool_calls:
            result = await run_tool(call.function.name, call.function.arguments)
            history.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return {"ok": False, "error": "step limit reached", "tokens": tokens}
```
Note: trimming history with `history[-MAX_HISTORY:]` can cut an assistant `tool_calls` message away from its `tool` replies, which the API rejects; in production trim on turn boundaries or summarise old turns.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Chat(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=1000)

@app.post("/chat")
async def chat(body: Chat) -> dict:
    result = await agent_turn(body.session_id, body.message)
    if not result["ok"]:
        raise HTTPException(status_code=502, detail=result["error"])
    return result

@app.delete("/chat/{session_id}")
async def reset(session_id: str) -> dict:
    SESSIONS.pop(session_id, None)                      # let users clear memory (privacy)
    return {"cleared": True}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_rate(hs_code: str) -> str:
    """Duty percent for a KNOWN HS code like 6109.10."""
    return "20%"

agent = create_react_agent(
    ChatOpenAI(model="gpt-4o-mini", temperature=0),
    [get_rate],
    checkpointer=MemorySaver(),            # per-thread memory (use Postgres/SQLite saver in prod)
    prompt="You are a customs tariff assistant. Never invent rates.",
)
cfg = {"configurable": {"thread_id": "user-42"}, "recursion_limit": 10}
agent.invoke({"messages": [("user", "Duty for 6109.10?")]}, cfg)
agent.invoke({"messages": [("user", "And how much on USD 500 of them?")]}, cfg)   # remembers context
```
In older LangGraph versions the system text parameter is called `state_modifier` or `messages_modifier`; recent versions use `prompt`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Unlimited memory
✅ Correct: Window or summarise history.

```python
# Wrong — every turn is re-sent forever:
messages = full_history
# Right:
messages = [system] + history[-12:]        # or summarise older turns
```

❌ Mistake 2: Giving the agent every tool and every permission
✅ Correct: Smallest toolset, least privilege, approval for risky actions.

```python
# Wrong:
tools = ALL_COMPANY_TOOLS
# Right:
tools = [get_rate, search_hs_codes]       # read-only for this agent
```

❌ Mistake 3: Using an agent where a fixed pipeline works (slower, costlier, less predictable).

---

## 🧠 Tricky Interview Question

**Q**: "Users complain the agent 'forgets' earlier answers after about 10 turns, yet you store the full history. What is going on?"

**Answer**: You may be trimming history (window) and cutting out facts, or the context is so long that the model suffers "lost in the middle" and ignores earlier details. Fixes: summarise older turns into a running summary, store key facts (user's country, product type) as structured state that is injected each turn, retrieve relevant past turns (vector memory), and put critical instructions at the start and end of the prompt.

---

## ⚫ Interview Questions + Answers

Q1: What are the parts of an agent? (Easy)
A1: LLM, tools, memory, prompt/instructions, and a controller that enforces limits, validation and logging.

Q2: Agent vs chain? (Easy)
A2: A chain follows a fixed sequence written by developers. An agent lets the LLM decide the next action dynamically.

Q3: What kinds of memory does an agent use? (Medium)
A3: Short-term (current conversation/scratchpad), long-term (stored facts or vector store across sessions), and structured state (task variables). Each has different storage and token costs.

Q4: How do you stop an agent doing harmful things? (Medium)
A4: Least-privilege tools, argument validation, approval for risky actions, output filtering, step/time/cost budgets, sandboxing, and monitoring.

Q5: How do you evaluate an agent? (Hard)
A5: Build a dataset of tasks with expected outcomes; measure task success, tool-call correctness, steps per task, cost and latency; evaluate trajectories (not just final answers) with rules or LLM judges; add adversarial tests; run regression suites on every prompt or tool change and track metrics in production.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Task is open-ended and multi-step
- Tools and data sources vary per request
- Users ask follow-up questions

❌ Avoid when:
- Fixed workflow
- Strict latency/cost limits
- High-stakes actions without human review

---

## 📊 Visual Diagram
```
           ┌────────────── Controller (limits, logging, guardrails) ─────────────┐
 User ───► │  Prompt  ─►  LLM (brain)  ─► Action ─► Tools (hands) ─► Observation  │
           │     ▲             ▲                                          │       │
           │     └── Memory ───┴──────────────────────────────────────────┘       │
           └──────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
                                   Final answer
```

---

## 💰 Cost Impact
Memory is a hidden cost: 12 messages of 150 tokens add about 1,800 input tokens to every LLM call in the loop. A 5-step run re-sends that 5 times (9,000 tokens, about $0.0014 on gpt-4o-mini). Long-running sessions without trimming grow linearly per turn and quadratically per session.

Optimize: windowed or summarised memory, structured state instead of raw transcripts, tool-result truncation, prompt caching for the static prefix, and step limits.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | LLM that decides actions in a loop | Loop में निर्णय लेने वाला LLM |
| Memory | Stored context | संग्रहीत context |
| Checkpointer | Saves agent state per thread | State सेव करने वाला |
| Guardrail | Safety limit | सुरक्षा सीमा |
| Trajectory | Sequence of steps taken | उठाए गए steps का क्रम |
| Thread id | Conversation identifier | बातचीत की पहचान |

---

## ⚡ 3-Line Summary
English: A ReAct agent combines an LLM, tools, memory, a prompt and a controller to solve open-ended tasks step by step. Memory and limits are what make it production-safe. Use a plain pipeline when the steps are fixed.
Hindi: ReAct agent LLM, tools, memory, prompt और controller मिलाकर open-ended काम कदम-दर-कदम हल करता है। Memory और limits इसे production-safe बनाती हैं। Steps तय हों तो साधारण pipeline चुनो।

---

## ➡️ Next Topic
**301. AgentExecutor** — LangChain's runtime for agents: options, limits and error handling in detail.
