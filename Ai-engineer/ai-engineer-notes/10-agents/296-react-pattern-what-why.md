---

# 296. ReAct Pattern — What + Why
# हिंदी में: ReAct Pattern — क्या है और क्यों

---

## 🔵 Simple Definition (English)
ReAct (Reason + Act) is a pattern where an LLM alternates between thinking ("I need the HS code first") and acting (calling a tool), then reads the result and thinks again, until it can give a final answer. It was introduced in the 2022 paper "ReAct: Synergizing Reasoning and Acting in Language Models".

## 🔵 सरल परिभाषा (Hindi)
ReAct (Reason + Act) एक pattern है जिसमें LLM बारी-बारी से सोचता है ("पहले HS code चाहिए") और काम करता है (tool call), फिर result पढ़कर दोबारा सोचता है, जब तक final answer न दे सके। यह 2022 के paper "ReAct: Synergizing Reasoning and Acting in Language Models" से आया।

---

## 🔴 Problem it Solves
Reasoning-only prompts (chain-of-thought) can hallucinate facts because the model cannot check anything. Acting-only systems (call tools blindly) cannot plan, adapt to results or recover from dead ends. Many real questions need several dependent steps whose next step depends on the previous observation: "find the HS code, then its duty, then convert currency."

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ reasoning (chain-of-thought) में model facts गढ़ सकता है क्योंकि कुछ verify नहीं कर सकता। सिर्फ़ acting (अंधाधुंध tool calls) में plan और adaptation नहीं होता। असली सवालों में कई dependent steps होते हैं जहाँ अगला step पिछले result पर निर्भर करता है: "HS code खोजो, फिर duty, फिर currency convert।"

---

## 🟢 How it Works — Step by Step

```
Step 1 → Give the LLM a question + a list of tools + the ReAct format
Step 2 → LLM writes Thought: "I need the HS code for a cotton shirt"
Step 3 → LLM writes Action: search_hs_codes   Action Input: "cotton shirt"
Step 4 → Your code runs the tool, gets Observation: "6109.10 T-shirts of cotton"
Step 5 → Observation is appended to the prompt; LLM writes a new Thought
Step 6 → Repeat steps 2-5 until LLM writes "Final Answer: ..."
Step 7 → Stop on Final Answer, max iterations, or error; return answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM को सवाल + tools की list + ReAct format दो
Step 2 → LLM लिखता है Thought: "cotton shirt का HS code चाहिए"
Step 3 → LLM लिखता है Action: search_hs_codes   Action Input: "cotton shirt"
Step 4 → Code tool चलाता है, Observation: "6109.10 T-shirts of cotton"
Step 5 → Observation prompt में जुड़ता है; LLM नया Thought लिखता है
Step 6 → Steps 2-5 दोहराओ जब तक "Final Answer: ..." न आए
Step 7 → Final Answer, max iterations या error पर रुको; जवाब लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: "What duty applies to importing a cotton t-shirt from Vietnam, value USD 500, in INR?"

```
Thought: I need the HS code.
Action: search_hs_codes("cotton t-shirt")        -> Observation: 6109.10
Thought: Now the duty rate.
Action: get_tariff_rate("6109.10")               -> Observation: 20%
Thought: Convert USD 500 to INR.
Action: get_exchange_rate("USD","INR")           -> Observation: 83.2
Thought: duty = 500 * 83.2 * 0.20
Action: calculator("500*83.2*0.20")              -> Observation: 8320
Final Answer: Duty is about Rs 8,320.
```

**Amazon AI**: "Is my package late, and can I get a refund?" - look up the order, check the delivery date, then check the refund policy.

## 🟡 Real Example Hindi mein
**Tariff System**: "Vietnam से cotton t-shirt (USD 500) import पर duty INR में?" Agent चरणों में: HS code खोजता है -> duty rate -> exchange rate -> calculator -> Final Answer "लगभग Rs 8,320"।

**Amazon AI**: "मेरा package late है, refund मिलेगा?" पहले order देखो, delivery date check करो, फिर refund policy।

---

## 💻 Code Example — Basic
```python
# Minimal ReAct loop with a scripted fake LLM (runs offline, no API key)
import re                                       # to parse the model's text
from typing import Callable

def search_hs_codes(q: str) -> str:
    """Tool 1: fake HS lookup."""
    return "6109.10" if "shirt" in q.lower() else "unknown"

def get_tariff_rate(code: str) -> str:
    """Tool 2: fake rate lookup."""
    return {"6109.10": "20"}.get(code, "unknown")

TOOLS: dict[str, Callable[[str], str]] = {"search_hs_codes": search_hs_codes, "get_tariff_rate": get_tariff_rate}

SCRIPT = iter([                                 # what a real LLM might write, step by step
    "Thought: I need the HS code.\nAction: search_hs_codes\nAction Input: cotton shirt",
    "Thought: Now the duty rate.\nAction: get_tariff_rate\nAction Input: 6109.10",
    "Thought: I know the answer.\nFinal Answer: Duty on cotton shirts (6109.10) is 20%.",
])

def fake_llm(prompt: str) -> str:
    """Pretend LLM: returns the next scripted step."""
    return next(SCRIPT)

def react(question: str, max_steps: int = 5) -> str:
    prompt = f"Question: {question}\n"          # the growing transcript (the 'scratchpad')
    for step in range(max_steps):               # hard cap on loops
        out = fake_llm(prompt)                  # LLM thinks
        prompt += out + "\n"
        if "Final Answer:" in out:              # stop condition
            return out.split("Final Answer:")[1].strip()
        m = re.search(r"Action: (.+)\nAction Input: (.+)", out)   # parse the action
        if not m:
            prompt += "Observation: could not parse action\n"
            continue
        name, arg = m.group(1).strip(), m.group(2).strip()
        tool = TOOLS.get(name)
        obs = tool(arg) if tool else f"unknown tool {name}"       # run tool
        prompt += f"Observation: {obs}\n"       # feed result back
        print(f"step {step + 1}: {name}({arg!r}) -> {obs}")
    return "Stopped: max steps reached."

print(react("Duty on cotton shirts?"))
```

## 💻 Code Example — Advanced
```python
# Production-style ReAct with a real LLM, async tools, parsing and safety limits
import asyncio, re
from typing import Awaitable, Callable
from openai import AsyncOpenAI

client = AsyncOpenAI()
ToolFn = Callable[[str], Awaitable[str]]

async def search_hs_codes(q: str) -> str:
    await asyncio.sleep(0)
    return "6109.10 (T-shirts, cotton)"

async def get_tariff_rate(code: str) -> str:
    await asyncio.sleep(0)
    return "20%"

TOOLS: dict[str, ToolFn] = {"search_hs_codes": search_hs_codes, "get_tariff_rate": get_tariff_rate}

SYSTEM = """Answer the question using this format exactly:
Thought: your reasoning
Action: one of [{tools}]
Action Input: the input
(then STOP and wait for Observation)
When done:
Thought: I now know the answer
Final Answer: the answer"""

ACTION_RE = re.compile(r"Action:\s*(.+?)\s*\nAction Input:\s*(.+)", re.S)

async def react_agent(question: str, max_steps: int = 6) -> str:
    system = SYSTEM.format(tools=", ".join(TOOLS))
    transcript = f"Question: {question}\n"
    for _ in range(max_steps):
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": transcript}],
                stop=["Observation:"],            # model must not invent observations
                temperature=0, max_tokens=250,
            )
        except Exception as exc:
            return f"LLM error: {exc}"
        text = resp.choices[0].message.content or ""
        transcript += text + "\n"
        if "Final Answer:" in text:
            return text.split("Final Answer:", 1)[1].strip()
        m = ACTION_RE.search(text)
        if not m:
            transcript += "Observation: Invalid format. Use Action and Action Input.\n"
            continue
        name, arg = m.group(1).strip(), m.group(2).strip().split("\n")[0]
        fn = TOOLS.get(name)
        try:
            obs = await asyncio.wait_for(fn(arg), timeout=10) if fn else f"Unknown tool {name}"
        except Exception as exc:
            obs = f"Tool error: {exc}"
        transcript += f"Observation: {obs}\n"
    return "Stopped: step limit reached."
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)

@app.post("/react")
async def react_route(body: Ask) -> dict:
    """Expose the ReAct agent; include steps count in real systems for debugging."""
    answer = await react_agent(body.question)
    return {"answer": answer}
```
For long agent runs, stream steps to the client with Server-Sent Events (`StreamingResponse`) so users see "Searching HS code..." instead of waiting.

---

## 🔗 LangChain / LangGraph Connection
```python
from langgraph.prebuilt import create_react_agent   # modern LangGraph ReAct agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_tariff_rate(hs_code: str) -> str:
    """Duty for a known HS code."""
    return "20%"

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [get_tariff_rate])
print(agent.invoke({"messages": [("user", "Duty for 6109.10?")]})["messages"][-1].content)
```
LangChain's older `create_react_agent` + `AgentExecutor` (text-based Thought/Action format) and LangGraph's prebuilt agent (native tool calling) implement the same idea. See notes 299-301.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting the model write the Observation
✅ Correct: Stop generation at `Observation:` so only your tool can produce it.

```python
# Wrong — model hallucinates tool results:
client.chat.completions.create(model=m, messages=msgs)
# Right:
client.chat.completions.create(model=m, messages=msgs, stop=["Observation:"])
```

❌ Mistake 2: No step limit
✅ Correct: Always cap iterations.

```python
# Wrong:
while True: step()
# Right:
for _ in range(max_steps): step()
```

---

## 🧠 Tricky Interview Question

**Q**: "ReAct gives better answers but your latency tripled. Is ReAct the wrong choice?"

**Answer**: Each Thought/Action cycle is a full LLM round trip, so latency grows with steps. If the path is fixed (rate lookup then calculation), use a deterministic chain with one LLM call. Use ReAct only when the next step depends on observations. You can also cut cost with a smaller model, parallel tool calls, fewer tools per request, and streaming progress.

---

## ⚫ Interview Questions + Answers

Q1: What does ReAct stand for? (Easy)
A1: Reasoning + Acting. The model interleaves reasoning traces with tool actions.

Q2: What are the three parts of one ReAct step? (Easy)
A2: Thought (reasoning), Action (tool + input), Observation (tool result).

Q3: How does ReAct reduce hallucination? (Medium)
A3: The model gets real observations from tools and bases later reasoning on them, instead of recalling facts from memory.

Q4: ReAct vs plain chain-of-thought? (Medium)
A4: CoT reasons internally with no external information; ReAct can fetch information and take actions, so it can verify and adapt. ReAct costs more calls.

Q5: What are ReAct's weaknesses and mitigations? (Hard)
A5: Looping, format errors, error compounding, high latency and cost, prompt injection through observations. Mitigate with step caps, stop sequences, strict parsing or native tool calling, validation, smaller toolsets, planning-then-execution variants and guardrails.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Next step depends on previous results
- Task needs external facts or actions
- Number of steps is unknown beforehand

❌ Avoid when:
- Steps are fixed (use a chain)
- Single lookup is enough
- Strict latency/cost limits

---

## 📊 Visual Diagram
```
         ┌──────────────────────────────────────────┐
         ▼                                          │
 Question ─► Thought ─► Action(tool,input) ─► Observation
                │                                   │
                └─── enough info? ──yes──► Final Answer
```

---

## 💰 Cost Impact
Each iteration re-sends the question, tool list and the whole transcript, so input tokens grow roughly quadratically: with a 600-token base and 150 new tokens per step, 5 steps send about 600+750+900+1050+1200 = 4,500 input tokens (about $0.0007 on gpt-4o-mini).

Optimize: low `max_tokens`, short tool descriptions, trimmed observations, a step cap, prompt caching for the static prefix, and a cheaper model for simple steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ReAct | Reason + Act loop | सोचो और करो loop |
| Thought | Model's reasoning step | Model की सोच |
| Action | Tool call chosen by model | चुना गया tool call |
| Observation | Tool result | Tool का नतीजा |
| Final Answer | Last output to user | अंतिम जवाब |
| Scratchpad | Running transcript of steps | चरणों का रिकॉर्ड |

---

## ⚡ 3-Line Summary
English: ReAct makes an LLM alternate Thought, Action and Observation until it has a Final Answer. It grounds reasoning in real tool results and handles dependent multi-step tasks. Cap the steps because cost and latency grow every loop.
Hindi: ReAct में LLM Thought, Action और Observation बारी-बारी करता है जब तक Final Answer न मिले। इससे reasoning असली tool results पर टिकती है और dependent multi-step काम हो पाते हैं। हर loop पर cost और latency बढ़ती है, इसलिए steps की limit रखो।

---

## ➡️ Next Topic
**297. ReAct — Thought, Action, Observation** — a deeper look at each part and how to write and parse them.
