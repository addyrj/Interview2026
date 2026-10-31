---

# 297. ReAct — Thought, Action, Observation
# हिंदी में: ReAct — Thought, Action, Observation

---

## 🔵 Simple Definition (English)
In ReAct every loop has three parts. **Thought** is the model's short reasoning about what to do next. **Action** is the tool it chooses plus the input. **Observation** is the real result your code returns. The model produces Thought and Action; only your code produces Observation.

## 🔵 सरल परिभाषा (Hindi)
ReAct के हर loop में तीन हिस्से होते हैं। **Thought** यानी आगे क्या करना है इसकी model की छोटी सोच। **Action** यानी चुना हुआ tool और उसका input। **Observation** यानी आपके code का लौटाया असली result। Thought और Action model बनाता है; Observation सिर्फ़ आपका code बनाता है।

---

## 🔴 Problem it Solves
If the model's output is free-form prose, your program cannot know which tool to run. If the model is allowed to write the Observation too, it makes up results. A strict three-part structure makes the loop parseable, auditable (you can read why it did something) and safe (tool results come only from real code).

## 🔴 यह क्यों बना? (Hindi)
अगर output सामान्य गद्य हो तो program नहीं जान सकता कौन सा tool चलाना है। अगर model Observation भी लिख दे तो वह नतीजे गढ़ लेता है। तीन-हिस्सों का सख़्त structure loop को parse-योग्य, audit-योग्य (क्यों किया पता चलता है) और सुरक्षित (tool results सिर्फ़ असली code से) बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prompt defines the format: Thought / Action / Action Input / Observation
Step 2 → Model emits "Thought: ..." (reasoning, 1-2 sentences)
Step 3 → Model emits "Action: <tool>" and "Action Input: <arg>"
Step 4 → Generation STOPS at "Observation:" (stop sequence)
Step 5 → Parser extracts tool name + input with regex (or JSON)
Step 6 → Code validates tool name, runs it, builds "Observation: <result>"
Step 7 → Append to transcript, loop; or parse "Final Answer:" and finish
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Prompt format तय करता है: Thought / Action / Action Input / Observation
Step 2 → Model "Thought: ..." लिखता है (1-2 वाक्य की सोच)
Step 3 → Model "Action: <tool>" और "Action Input: <arg>" लिखता है
Step 4 → "Observation:" पर generation रुक जाता है (stop sequence)
Step 5 → Parser regex (या JSON) से tool नाम + input निकालता है
Step 6 → Code tool नाम validate करके चलाता है, "Observation: <result>" बनाता है
Step 7 → Transcript में जोड़ो, loop; या "Final Answer:" parse करके खत्म
```

---

## 🟡 Real World Example
**Tariff Classification System** trace for "Duty on a Bluetooth speaker?":

```
Thought: I need the HS code for a Bluetooth speaker.
Action: search_hs_codes
Action Input: bluetooth speaker
Observation: 8518.22 Loudspeakers; 8517.62 Wireless apparatus (ambiguous)
Thought: Two candidates. A speaker's main function is sound, so 8518.22. Check its rate.
Action: get_tariff_rate
Action Input: 8518.22
Observation: 15%
Thought: I now know the answer.
Final Answer: 15% under HS 8518.22 (sound is the principal function).
```
Notice the second Thought: it reasons about ambiguity in the observation. That is the value of ReAct.

**Zomato AI**: Thought "user is vegetarian" -> Action `search_restaurants(veg=true)` -> Observation 12 results.

## 🟡 Real Example Hindi mein
**Tariff System**: "Bluetooth speaker की duty?" पर agent पहले HS code खोजता है, Observation में दो विकल्प मिलते हैं (8518.22 और 8517.62); दूसरा Thought अस्पष्टता पर सोचता है ("मुख्य काम आवाज़ है, इसलिए 8518.22"), फिर rate देखता है। यही ReAct की ताकत है।

**Zomato AI**: Thought "user vegetarian है" -> Action `search_restaurants(veg=true)` -> Observation में 12 results।

---

## 💻 Code Example — Basic
```python
# Parsing Thought / Action / Observation (pure Python, runs offline)
import re
from dataclasses import dataclass

@dataclass
class Step:
    """One parsed model turn."""
    thought: str
    action: str | None = None
    action_input: str | None = None
    final_answer: str | None = None

THOUGHT_RE = re.compile(r"Thought:\s*(.*?)(?=\n(?:Action|Final Answer):|\Z)", re.S)
ACTION_RE = re.compile(r"Action:\s*(.+?)\s*\nAction Input:\s*(.+?)\s*(?:\n|\Z)", re.S)
FINAL_RE = re.compile(r"Final Answer:\s*(.+)", re.S)

def parse(text: str) -> Step:
    """Turn raw model text into a Step; raise ValueError when format is broken."""
    t = THOUGHT_RE.search(text)
    thought = t.group(1).strip() if t else ""
    if (f := FINAL_RE.search(text)):                       # Final Answer wins
        return Step(thought, final_answer=f.group(1).strip())
    if (a := ACTION_RE.search(text)):
        return Step(thought, action=a.group(1).strip(), action_input=a.group(2).strip())
    raise ValueError("output has neither Action nor Final Answer")

sample = "Thought: I need the HS code.\nAction: search_hs_codes\nAction Input: bluetooth speaker"
print(parse(sample))
print(parse("Thought: Done.\nFinal Answer: 15%"))
try:
    parse("I think the answer is 15%")                     # model ignored the format
except ValueError as exc:
    print("parse error ->", exc)
```

## 💻 Code Example — Advanced
```python
# Production: robust parser, observation truncation, error-as-observation, async loop
import asyncio, re
from dataclasses import dataclass
from typing import Awaitable, Callable
from openai import AsyncOpenAI

client = AsyncOpenAI()
MAX_OBS_CHARS = 1200                                       # keep observations small

@dataclass
class Step:
    thought: str
    action: str | None = None
    action_input: str | None = None
    final: str | None = None

class FormatError(Exception):
    """Model broke the Thought/Action format."""

def parse(text: str) -> Step:
    thought = (re.search(r"Thought:\s*(.*)", text) or [None, ""])[1].strip()
    if "Final Answer:" in text:
        return Step(thought, final=text.split("Final Answer:", 1)[1].strip())
    m = re.search(r"Action:\s*(.+)\nAction Input:\s*(.+)", text)
    if not m:
        raise FormatError("Reply with 'Action:' and 'Action Input:' or 'Final Answer:'.")
    return Step(thought, m.group(1).strip().strip("[]"), m.group(2).strip().strip('"'))

def make_observation(raw: str) -> str:
    """Observation must be short and clearly marked as data."""
    return raw if len(raw) <= MAX_OBS_CHARS else raw[:MAX_OBS_CHARS] + " ...[truncated]"

async def run(question: str, tools: dict[str, Callable[[str], Awaitable[str]]], system: str,
              max_steps: int = 6) -> str:
    transcript = f"Question: {question}\n"
    format_errors = 0
    for _ in range(max_steps):
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=200, stop=["Observation:"],
            messages=[{"role": "system", "content": system}, {"role": "user", "content": transcript}],
        )
        text = resp.choices[0].message.content or ""
        transcript += text.rstrip() + "\n"
        try:
            step = parse(text)
        except FormatError as exc:
            format_errors += 1
            if format_errors >= 2:                         # do not loop on a confused model
                return "Agent could not follow the required format."
            transcript += f"Observation: {exc}\n"          # error becomes an observation
            continue
        if step.final is not None:
            return step.final
        fn = tools.get(step.action or "")
        try:
            obs = await asyncio.wait_for(fn(step.action_input or ""), 10) if fn else \
                  f"Unknown tool '{step.action}'. Valid: {list(tools)}"
        except Exception as exc:
            obs = f"Tool error: {type(exc).__name__}: {exc}"
        transcript += f"Observation: {make_observation(obs)}\n"
    return "Step limit reached."
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

async def trace_stream(question: str):
    """Stream each Thought/Action/Observation as Server-Sent Events."""
    # In a real agent, yield inside the loop. Here we show the event shape.
    for event in [
        {"type": "thought", "text": "I need the HS code."},
        {"type": "action", "tool": "search_hs_codes", "input": "bluetooth speaker"},
        {"type": "observation", "text": "8518.22"},
        {"type": "final", "text": "15%"},
    ]:
        yield f"data: {json.dumps(event)}\n\n"             # SSE format

@app.get("/react/stream")
async def stream(question: str) -> StreamingResponse:
    return StreamingResponse(trace_stream(question), media_type="text/event-stream")
```
Showing Thoughts in the UI builds trust, but never expose raw tool output containing private data.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

# The classic LangChain ReAct prompt uses exactly these markers:
TEMPLATE = """Answer the question using these tools:
{tools}

Format:
Question: the input question
Thought: reasoning
Action: one of [{tool_names}]
Action Input: input
Observation: result
... (repeat)
Thought: I now know the final answer
Final Answer: answer

Question: {input}
Thought:{agent_scratchpad}"""
prompt = PromptTemplate.from_template(TEMPLATE)
# agent = create_react_agent(llm, tools, prompt)
# executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)
```
`return_intermediate_steps=True` gives you (AgentAction, observation) pairs, which are the structured version of Action and Observation. With native tool-calling agents (LangGraph), Action = `AIMessage.tool_calls` and Observation = `ToolMessage`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No stop sequence
✅ Correct: Stop at `Observation:`.

```python
# Wrong — the model continues and writes fake Observation lines itself:
create(messages=msgs)
# Right:
create(messages=msgs, stop=["Observation:"])
```

❌ Mistake 2: Crashing when parsing fails
✅ Correct: Feed the format error back as an Observation (limited tries).

```python
# Wrong:
step = parse(text)                      # ValueError kills the request
# Right:
try: step = parse(text)
except FormatError as e: transcript += f"Observation: {e}\n"; continue
```

❌ Mistake 3: Huge observations (full web pages). Truncate or summarise.

---

## 🧠 Tricky Interview Question

**Q**: "In production the model sometimes outputs both an Action and a Final Answer in the same turn. What should your parser do and why?"

**Answer**: This is ambiguous and dangerous: the Final Answer was written before seeing the Observation, so it is likely hallucinated. A safe policy is: if an Action is present, run the Action, discard any Final Answer in the same output, and continue the loop. (LangChain raises a parsing error for this case.) Also use a stop sequence so the model cannot continue past the Action, and prefer native tool calling where a turn is either text or tool calls.

---

## ⚫ Interview Questions + Answers

Q1: Who writes the Observation? (Easy)
A1: Your code. The model must stop before it, using a stop sequence, so observations are always real tool output.

Q2: What is `Action Input`? (Easy)
A2: The argument string for the chosen tool, such as the product text or an HS code.

Q3: How is the Thought used by your program? (Medium)
A3: It is not executed; it improves reasoning quality, helps debugging/audit and can be streamed to the UI. It also costs tokens, so keep it short.

Q4: Text ReAct vs native tool calling? (Medium)
A4: Text ReAct parses free text with regex and is model-agnostic but fragile. Native tool calling returns structured `tool_calls` validated by the API, which is more reliable and supports parallel calls. Modern code prefers native tool calling.

Q5: How do you make observations safe? (Hard)
A5: Truncate size, strip HTML, label as data, validate with schemas, filter secrets, detect injection phrases, and never let observations change system instructions. Treat them as untrusted input.

---

## 🔷 When to Use + When Not to Use
✅ Use the text format when:
- Learning/debugging how agents work
- Model has no native tool calling
- You need a readable audit trail

❌ Avoid when:
- A model with native tool calling is available (more reliable)
- Output must be strictly structured (use structured outputs)

---

## 📊 Visual Diagram
```
 Model writes ─────────────────────────┐  Your code writes
 ┌──────────────────────────────┐      │  ┌─────────────────────┐
 │ Thought: why                 │      │  │ Observation: result │
 │ Action: tool_name            │ ─► parse ─► run tool ─────────►│
 │ Action Input: arg            │  STOP│  └─────────────────────┘
 └──────────────────────────────┘      │            │
        ▲                              │            │ append to transcript
        └──────────────────────────────┴────────────┘
```

---

## 💰 Cost Impact
Thoughts are output tokens (more expensive than input, e.g. $0.60/1M vs $0.15/1M on gpt-4o-mini). A verbose 80-token Thought times 6 steps is about 500 output tokens. Observations are input tokens re-sent on every later step.

Optimize: instruct "Thought: one short sentence", truncate observations to a few hundred tokens, cap `max_tokens`, and drop old steps when the transcript gets long.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Thought | Reasoning text | सोच |
| Action | Tool name chosen | चुना हुआ tool |
| Action Input | Tool argument | Tool का input |
| Observation | Tool result | Tool का नतीजा |
| Stop sequence | String that halts generation | Generation रोकने वाला string |
| Parser | Extracts structure from text | Text से structure निकालने वाला |

---

## ⚡ 3-Line Summary
English: Thought is reasoning, Action is the tool call, Observation is the real result. The model writes the first two; your code writes the third, enforced by a stop sequence. Parse strictly, handle format errors as observations and keep observations short.
Hindi: Thought सोच है, Action tool call है और Observation असली result है। पहले दो model लिखता है; तीसरा आपका code, stop sequence के साथ। सख़्ती से parse करो, format errors को observation बनाओ और observations छोटे रखो।

---

## ➡️ Next Topic
**298. ReAct Implementation** — building a complete ReAct agent class from scratch with tools, memory and limits.
