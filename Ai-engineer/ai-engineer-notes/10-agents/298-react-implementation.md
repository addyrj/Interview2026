---

# 298. ReAct Implementation
# हिंदी में: ReAct Implementation (शुरू से बनाना)

---

## 🔵 Simple Definition (English)
A ReAct implementation is the actual code that runs the loop: build a prompt, call the LLM, parse Thought/Action, run the tool, append the Observation, and repeat until a Final Answer or a limit. Here we build it from scratch with a tool registry, a pluggable LLM, error handling and tracing.

## 🔵 सरल परिभाषा (Hindi)
ReAct implementation वह असली code है जो loop चलाता है: prompt बनाओ, LLM call करो, Thought/Action parse करो, tool चलाओ, Observation जोड़ो और Final Answer या limit तक दोहराओ। यहाँ हम इसे शुरू से बनाते हैं: tool registry, बदले जा सकने वाला LLM, error handling और tracing के साथ।

---

## 🔴 Problem it Solves
Frameworks hide the loop, so engineers cannot debug "why does my agent loop forever?" or "why is it so expensive?". Interviewers often ask you to write a ReAct loop on a whiteboard. Building it once removes the mystery and shows exactly where tokens, latency and failures come from.

## 🔴 यह क्यों बना? (Hindi)
Frameworks loop छुपा देते हैं, इसलिए "agent बार-बार क्यों घूम रहा है?" या "इतना महँगा क्यों है?" debug नहीं हो पाता। Interview में अक्सर ReAct loop लिखने को कहा जाता है। एक बार खुद बनाने से रहस्य खत्म होता है और पता चलता है tokens, latency और failures कहाँ से आते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → ToolRegistry: name -> (function, description)
Step 2 → build_system_prompt(): list tools + format rules
Step 3 → Loop i in range(max_steps):
Step 4 →    llm(transcript)  (stop at "Observation:")
Step 5 →    parse -> Final? return : Action?
Step 6 →    run tool safely (timeout, try/except), truncate result
Step 7 →    transcript += Observation; record trace (tokens, latency)
Step 8 → Limit reached -> return partial answer + reason
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → ToolRegistry: name -> (function, description)
Step 2 → build_system_prompt(): tools की list + format नियम
Step 3 → Loop i in range(max_steps):
Step 4 →    llm(transcript)  ("Observation:" पर stop)
Step 5 →    parse -> Final? लौटाओ : Action?
Step 6 →    tool सुरक्षित चलाओ (timeout, try/except), result truncate
Step 7 →    transcript += Observation; trace रिकॉर्ड (tokens, latency)
Step 8 → Limit पर -> अधूरा जवाब + कारण लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Landed cost of 100 cotton t-shirts at USD 5 each, Vietnam to India, in INR" needs four tools: `search_hs_codes`, `get_tariff_rate`, `get_exchange_rate`, `calculator`. Our class runs 4-5 loops, logs each step, and returns `{answer, steps, tokens}` to the API.

**Zomato AI**: "Cheapest veg biryani within 3 km that opens before 9" - `search_restaurants`, `get_menu`, `filter_by_time`.

## 🟡 Real Example Hindi mein
**Tariff System**: "100 cotton t-shirts, USD 5 प्रति, Vietnam से India, INR में landed cost" के लिए चार tools चाहिए। हमारी class 4-5 loops चलाती है, हर step log करती है और API को `{answer, steps, tokens}` लौटाती है।

**Zomato AI**: "3 km में सबसे सस्ती veg biryani जो 9 बजे से पहले खुले" - `search_restaurants`, `get_menu`, `filter_by_time`।

---

## 💻 Code Example — Basic
```python
# Complete ReAct agent from scratch with a scripted LLM (runs offline)
import ast, operator, re
from typing import Callable

def calculator(expr: str) -> str:
    """Safe arithmetic tool using ast."""
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
    def ev(n: ast.AST) -> float:
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in ops: return ops[type(n.op)](ev(n.left), ev(n.right))
        raise ValueError("unsupported")
    try:
        return str(ev(ast.parse(expr, mode="eval").body))
    except Exception as exc:
        return f"error: {exc}"

TOOLS: dict[str, Callable[[str], str]] = {
    "search_hs_codes": lambda q: "6109.10 T-shirts, cotton",
    "get_tariff_rate": lambda c: "20",
    "get_exchange_rate": lambda p: "83.2",
    "calculator": calculator,
}

class ScriptedLLM:
    """Replace with a real LLM client; here it replays a fixed plan."""
    def __init__(self) -> None:
        self.outputs = iter([
            "Thought: Find HS code.\nAction: search_hs_codes\nAction Input: cotton t-shirt",
            "Thought: Get rate.\nAction: get_tariff_rate\nAction Input: 6109.10",
            "Thought: Get FX.\nAction: get_exchange_rate\nAction Input: USD INR",
            "Thought: Value 100*5*83.2 = 41600 INR, duty 20%.\nAction: calculator\nAction Input: 100*5*83.2*0.20",
            "Thought: Done.\nFinal Answer: Duty is Rs 8320 on goods worth Rs 41600.",
        ])
    def __call__(self, transcript: str) -> str:
        return next(self.outputs)

class ReActAgent:
    def __init__(self, llm: Callable[[str], str], tools: dict[str, Callable[[str], str]], max_steps: int = 8):
        self.llm, self.tools, self.max_steps = llm, tools, max_steps
        self.pattern = re.compile(r"Action:\s*(.+)\nAction Input:\s*(.+)")

    def run(self, question: str) -> dict:
        transcript, steps = f"Question: {question}\n", []
        for i in range(1, self.max_steps + 1):
            out = self.llm(transcript)                                  # model turn
            transcript += out + "\n"
            if "Final Answer:" in out:
                return {"answer": out.split("Final Answer:")[1].strip(), "steps": steps, "status": "ok"}
            m = self.pattern.search(out)
            if not m:
                transcript += "Observation: format error, use Action/Action Input\n"
                continue
            name, arg = m.group(1).strip(), m.group(2).strip()
            tool = self.tools.get(name)
            obs = tool(arg) if tool else f"unknown tool {name}"          # run tool
            steps.append({"i": i, "tool": name, "input": arg, "obs": obs})
            transcript += f"Observation: {obs}\n"
        return {"answer": None, "steps": steps, "status": "max_steps"}

result = ReActAgent(ScriptedLLM(), TOOLS).run("Duty on 100 cotton t-shirts at USD 5 each?")
for s in result["steps"]:
    print(s)
print(result["answer"], "|", result["status"])
```

## 💻 Code Example — Advanced
```python
# Production class: async, real OpenAI, timeouts, token accounting, tracing, truncation
import asyncio, re, time
from dataclasses import dataclass, field
from typing import Awaitable, Callable
from openai import AsyncOpenAI

ToolFn = Callable[[str], Awaitable[str]]

@dataclass
class Tool:
    name: str
    description: str
    fn: ToolFn

@dataclass
class Trace:
    steps: list[dict] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0

class AsyncReActAgent:
    ACTION = re.compile(r"Action:\s*(.+)\nAction Input:\s*(.+)")

    def __init__(self, tools: list[Tool], model: str = "gpt-4o-mini", max_steps: int = 8,
                 tool_timeout: float = 10.0, max_obs_chars: int = 1000) -> None:
        self.tools = {t.name: t for t in tools}
        self.model, self.max_steps = model, max_steps
        self.tool_timeout, self.max_obs_chars = tool_timeout, max_obs_chars
        self.client = AsyncOpenAI()
        self.system = (
            "Solve the task. Available tools:\n"
            + "\n".join(f"- {t.name}: {t.description}" for t in tools)
            + "\nUse exactly:\nThought: <short>\nAction: <tool name>\nAction Input: <input>\n"
            "After you receive an Observation, continue. Finish with:\nFinal Answer: <answer>"
        )

    async def _call_tool(self, name: str, arg: str) -> str:
        tool = self.tools.get(name)
        if tool is None:
            return f"Unknown tool '{name}'. Valid tools: {', '.join(self.tools)}"
        try:
            out = await asyncio.wait_for(tool.fn(arg), timeout=self.tool_timeout)
        except asyncio.TimeoutError:
            return "Tool timed out."
        except Exception as exc:
            return f"Tool error: {type(exc).__name__}: {exc}"
        return out[: self.max_obs_chars]

    async def run(self, question: str) -> tuple[str, Trace]:
        trace = Trace()
        transcript = f"Question: {question}\n"
        for i in range(1, self.max_steps + 1):
            started = time.perf_counter()
            try:
                resp = await self.client.chat.completions.create(
                    model=self.model, temperature=0, max_tokens=200, stop=["Observation:"],
                    messages=[{"role": "system", "content": self.system},
                              {"role": "user", "content": transcript}],
                )
            except Exception as exc:
                return f"LLM failure: {exc}", trace
            if resp.usage:
                trace.input_tokens += resp.usage.prompt_tokens
                trace.output_tokens += resp.usage.completion_tokens
            text = resp.choices[0].message.content or ""
            transcript += text.strip() + "\n"
            if "Final Answer:" in text:
                return text.split("Final Answer:", 1)[1].strip(), trace
            m = self.ACTION.search(text)
            if not m:
                transcript += "Observation: Invalid format. Use Action and Action Input.\n"
                continue
            name, arg = m.group(1).strip(), m.group(2).strip()
            obs = await self._call_tool(name, arg)
            trace.steps.append({"i": i, "tool": name, "input": arg, "obs": obs[:80],
                                "ms": round((time.perf_counter() - started) * 1000)})
            transcript += f"Observation: {obs}\n"
        return "Stopped: step limit reached.", trace
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

async def get_rate(code: str) -> str:
    return "20"

agent = AsyncReActAgent([Tool("get_tariff_rate", "Duty percent for an HS code", get_rate)])   # build once

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)

@app.post("/agent")
async def run_agent(body: Ask) -> dict:
    try:
        answer, trace = await asyncio.wait_for(agent.run(body.question), timeout=45)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="agent timeout")
    return {
        "answer": answer,
        "steps": trace.steps,
        "tokens": {"input": trace.input_tokens, "output": trace.output_tokens},
    }
```

---

## 🔗 LangChain / LangGraph Connection
```python
# What our class does, written with LangGraph's prebuilt agent:
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
async def get_tariff_rate(hs_code: str) -> str:
    """Duty percent for an HS code."""
    return "20"

lg_agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini", temperature=0), [get_tariff_rate])
# await lg_agent.ainvoke({"messages": [("user", "Duty for 6109.10?")]}, {"recursion_limit": 12})
```
Mapping: our `run` loop = the graph's agent<->tools cycle; `max_steps` = `recursion_limit`; `transcript` = `messages` state; our `Trace` = LangSmith traces.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutating one shared transcript across users
✅ Correct: Keep transcript local to each `run` call.

```python
# Wrong — state leaks between requests:
class Agent:
    transcript = ""            # class attribute
# Right:
def run(self, q): transcript = f"Question: {q}\n"
```

❌ Mistake 2: Re-creating the client for every request
✅ Correct: Build the agent/client once at startup.

```python
# Wrong:
@app.post("/agent")
async def r(): return await AsyncReActAgent(tools).run(q)
# Right: create at module/lifespan level and reuse
```

❌ Mistake 3: Not recording tokens per run, so cost spikes go unnoticed.

---

## 🧠 Tricky Interview Question

**Q**: "Your ReAct agent works for one user but under 50 concurrent users answers are mixed up. What is the bug?"

**Answer**: Shared mutable state: a transcript, scratchpad or steps list stored on a singleton agent (instance or class attribute) is shared across requests. Fix: keep all per-run state local (or in a per-run object), keep only immutable config on the shared agent, and use async-safe resources (one HTTP client is fine to share). Add a concurrency test.

---

## ⚫ Interview Questions + Answers

Q1: What are the main components of a ReAct implementation? (Easy)
A1: Tool registry, prompt builder, LLM caller, output parser, tool executor, loop controller with limits, and trace/logging.

Q2: Why parse with a stop sequence? (Easy)
A2: To stop the model before it fabricates an Observation; only real tool output should follow an Action.

Q3: What do you do when the tool name is unknown? (Medium)
A3: Return an Observation that names valid tools so the model can correct itself, and count it toward the step limit.

Q4: How do you track cost per run? (Medium)
A4: Sum `usage.prompt_tokens` and `completion_tokens` for each LLM call into a Trace, multiply by model prices, return/log them, and alert on outliers.

Q5: How would you scale this to 500 requests per second? (Hard)
A5: Stateless horizontal replicas, shared async HTTP clients with connection pooling, rate-limit handling with backoff and per-tenant quotas, step and time caps, caching of tool results, a queue for long runs, small models for most steps, and observability (per-step latency, tokens, tool error rates).

---

## 🔷 When to Use + When Not to Use
✅ Use a custom loop when:
- You need full control over parsing, limits and logging
- Teaching or debugging
- Minimal dependencies

❌ Avoid when:
- You need checkpoints, human approval, streaming and branching (use LangGraph)
- Team already standardised on a framework

---

## 📊 Visual Diagram
```
 run(question)
   │ transcript = "Question: ..."
   ▼
 ┌──────────────── loop (i <= max_steps) ───────────────┐
 │  llm(system, transcript, stop="Observation:")        │
 │        │                                             │
 │   parse ─ Final Answer? ──yes──► return              │
 │        │ no                                          │
 │   tool = registry[name]  (timeout, try/except)       │
 │        ▼                                             │
 │   transcript += "Observation: ..." ; trace.append    │
 └──────────────────────────────────────────────────────┘
   │ limit hit
   ▼
 return "step limit"
```

---

## 💰 Cost Impact
Cost per run = sum over steps of (system + tools + transcript so far) as input, plus short outputs. With a 400-token system prompt, 100 tokens added per step and 5 steps: input about 400x5 + 100x(0+1+2+3+4) = 3,000 tokens, output about 5x60 = 300 tokens, roughly $0.0006 on gpt-4o-mini. With gpt-4o it is about 30x more.

Optimize: shorten the system prompt, truncate observations, cap steps, cache tool results, use prompt caching on the static prefix, and use a cheap model unless accuracy drops.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool registry | Map of name to function | Tools की सूची |
| Transcript | Full text so far | अब तक का पूरा text |
| Trace | Record of steps, tokens, latency | Steps का रिकॉर्ड |
| Step limit | Max loops | अधिकतम loops |
| Shared mutable state | Data shared across requests | साझा बदलने योग्य state |
| Usage | Token counts from API | API द्वारा दिए tokens |

---

## ⚡ 3-Line Summary
English: A ReAct agent is a loop: call the LLM, parse, run the tool, append the Observation, stop on Final Answer or a limit. Keep state per run, add timeouts, truncation and token tracing. Frameworks like LangGraph give the same loop plus checkpoints and streaming.
Hindi: ReAct agent एक loop है: LLM call, parse, tool चलाओ, Observation जोड़ो, Final Answer या limit पर रुको। State हर run का अलग रखो, timeouts, truncation और token tracing जोड़ो। LangGraph वही loop checkpoints और streaming के साथ देता है।

---

## ➡️ Next Topic
**299. ReAct in LangChain** — the same agent using `create_react_agent`, the ReAct prompt and tools.
