---

# 581. Build ReAct Agent
# हिंदी में: ReAct Agent बनाना

---

## 🔵 Simple Definition (English)
ReAct (Reason + Act) is a prompting pattern where the model writes a short Thought, picks an Action (a tool call), reads the Observation, and repeats until it writes a Final Answer. The reasoning is visible in text, so you can parse, log and debug each step.

## 🔵 सरल परिभाषा (Hindi)
ReAct (Reason + Act) एक pattern है जिसमें model छोटा Thought लिखता है, Action (tool call) चुनता है, Observation पढ़ता है, और Final Answer आने तक दोहराता है। Reasoning text में दिखती है, इसलिए हर step parse, log और debug हो सकता है।

---

## 🔴 Problem it Solves
Reasoning without actions hallucinates facts. Actions without reasoning are blind and pick tools poorly. ReAct interleaves them: each observation grounds the next thought. It also works with models that lack native tool-calling, because the protocol is plain text.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ reasoning से facts गढ़े जाते हैं (hallucination)। सिर्फ actions से tools गलत चुने जाते हैं। ReAct दोनों को जोड़ता है: हर observation अगले thought को ground करता है। यह native tool-calling के बिना भी चलता है क्योंकि protocol plain text है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prompt lists tools and the format: Thought / Action / Observation / Final Answer
Step 2 → Model writes "Thought: ... Action: tool[input]"
Step 3 → Stop generation at "Observation:" (so the model cannot invent it)
Step 4 → Parse Action with a regex; run the tool
Step 5 → Append "Observation: <result>" to the prompt
Step 6 → Repeat until "Final Answer:" or max_steps
Step 7 → Return the answer; log the full transcript
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Prompt में tools और format: Thought / Action / Observation / Final Answer
Step 2 → Model लिखता है "Thought: ... Action: tool[input]"
Step 3 → "Observation:" पर generation रोको (model खुद observation न गढ़े)
Step 4 → Regex से Action parse करो, tool चलाओ
Step 5 → "Observation: <result>" prompt में जोड़ो
Step 6 → "Final Answer:" या max_steps तक दोहराओ
Step 7 → Answer लौटाओ; पूरा transcript log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Duty on a smartphone?" Thought: need HS code. Action: `search_hs[smartphone]`. Observation: 8517.13. Thought: need rate. Action: `duty_rate[8517.13]`. Observation: 0.2. Final Answer: 20%. The auditor can read the transcript and see why. **Zomato-style**: "Best biryani under 300 open now" becomes search, then filter by price, then check hours. **Amazon-style**: compare two products by calling spec lookup twice.

## 🟡 Real Example Hindi mein
**Tariff System**: "Smartphone पर duty?" Thought: HS code चाहिए। Action: `search_hs[smartphone]`। Observation: 8517.13। Thought: rate चाहिए। Action: `duty_rate[8517.13]`। Observation: 0.2। Final Answer: 20%। Auditor transcript पढ़कर कारण देख सकता है। **Zomato**: "300 के अंदर biryani, अभी खुला" = search → price filter → timing check। **Amazon**: दो products compare करने के लिए spec lookup दो बार।

---

## 💻 Code Example — Basic
Full solution in `main.py` (scripted LLM, regex parser, two tools).

```python
import re  # for parsing the Action line

ACTION_RE = re.compile(r"Action:\s*(\w+)\[(.*?)\]")  # matches Action: tool[input]

text = "Thought: need code\nAction: search_hs[smartphone]"  # pretend LLM output
match = ACTION_RE.search(text)  # find the action
if match:  # parsed successfully
    tool, arg = match.groups()  # split into name and argument
    print(tool, arg)  # search_hs smartphone
else:  # malformed output
    print("Observation: could not parse Action")  # tell the model, do not crash
```

## 💻 Code Example — Advanced
`main.py` handles malformed output (feeds an error Observation back), unknown tools, step cap, and an async wrapper. In production add a stop sequence so the model never writes its own Observation (illustrative OpenAI-style parameter):

```python
# Real LLM call with stop sequence (needs API key; illustrative)
from typing import Any

async def next_step(client: Any, prompt: str) -> str:  # one ReAct step
    resp = await client.chat.completions.create(  # chat call
        model="gpt-4o-mini",  # small model is enough for routing
        messages=[{"role": "user", "content": prompt}],  # whole transcript so far
        stop=["Observation:"],  # stop before the model fabricates a result
        max_tokens=200,  # keep thoughts short
        temperature=0,  # deterministic format following
    )
    return resp.choices[0].message.content or ""  # text with Thought/Action
```

---

## 🟠 FastAPI Integration
Stream thoughts to the UI with Server-Sent Events so users see progress.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from main import react  # from main.py

app = FastAPI()  # app

@app.get("/react")  # route
async def run(q: str) -> StreamingResponse:  # query param q
    async def gen():  # async generator of SSE lines
        answer = react(q)  # simple version: compute then emit
        yield f"data: {answer}\n\n"  # SSE frame
    return StreamingResponse(gen(), media_type="text/event-stream")  # stream
```

---

## 🔗 LangChain / LangGraph Connection
The original LangChain `AgentExecutor` + `create_react_agent` implements this text protocol (with a hub prompt). Today LangGraph's `create_react_agent` implements the same idea over native tool calls, with a graph of `agent` and `tools` nodes and checkpointing.

```python
# Illustrative LangGraph prebuilt agent (pip install langgraph langchain-openai)
# from langgraph.prebuilt import create_react_agent
# from langchain_openai import ChatOpenAI
# agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[search_hs, duty_rate])
# result = agent.invoke({"messages": [("user", "Duty on a smartphone?")]})
print("see comments: prebuilt agent = ReAct loop over native tool calls")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting the model write the Observation
✅ Correct: Use a stop sequence and inject real tool output.

```python
# Wrong: no stop, model hallucinates "Observation: 8517.99"
stop = None
# Right
stop = ["Observation:"]
print(stop)
```

❌ Mistake 2: Crash on unparsable output
✅ Correct: Return an instructive Observation and let the model retry.

```python
import re
out = "I think the answer is 20%"  # no Action, no Final Answer
m = re.search(r"Action:\s*(\w+)\[(.*?)\]", out)
# Wrong: m.groups() -> AttributeError
# Right:
obs = "Observation: use Action: tool[input]" if not m else "ok"
print(obs)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your ReAct agent answers correctly but each query costs 5x more than a plain RAG call. Is ReAct the right choice?"

**Answer**: Not necessarily. ReAct pays for several sequential LLM calls and a growing transcript. If the path is mostly fixed (retrieve then answer), use a deterministic pipeline or a small LangGraph with a single decision node. Keep ReAct for open-ended tasks where the number of steps varies. Reduce cost with a cheap model for routing, short thoughts, transcript truncation and caching tool results.

---

## ⚫ Interview Questions + Answers

Q1: What do the letters in ReAct stand for? (Easy)
A1: Reasoning and Acting, interleaved.

Q2: Why a stop sequence on "Observation:"? (Easy)
A2: So the model cannot fabricate tool results; real output is inserted by your code.

Q3: ReAct vs native function calling? (Medium)
A3: Native calling returns structured JSON validated by the provider and is less fragile. ReAct text works on any model and shows reasoning, but needs parsing and is more error-prone.

Q4: Is showing Thoughts to users safe? (Medium)
A4: Thoughts may leak internal prompts, tool names or sensitive data and can be unfaithful explanations. Log them for debugging; show users a sanitised status instead.

Q5: How do you stop an agent that loops with near-identical actions? (Hard)
A5: Track (action, input) pairs; on repeats inject a warning or abort; cap steps and tokens; add a reflection step ("what is different now?"); give a fallback "ask user for clarification" tool; evaluate loops in traces.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Number of steps is unknown beforehand
- You need an auditable reasoning trace

❌ Avoid when:
- A fixed pipeline works (cheaper, more predictable)
- Strict latency SLAs (several sequential calls)

---

## 📊 Visual Diagram
```
 Question
    │
    ▼
 ┌─► Thought ─► Action tool[input] ─► run tool
 │                                      │
 │            Observation ◄─────────────┘
 └──── not done ◄── done? ──yes──► Final Answer
```

---

## 💰 Cost Impact
Cost grows with steps and transcript length (each step re-sends everything). Example (illustrative): 4 steps with a transcript growing from 300 to 900 tokens is about 2,400 input tokens plus outputs. Optimise: short thought style ("be concise"), temperature 0, truncate long observations, cheap model, cache tool results, hard `max_steps`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ReAct | Reason + Act pattern | सोचना + करना |
| Thought | Model's reasoning text | Model की सोच |
| Action | Tool call request | Tool call की माँग |
| Observation | Tool result | Tool का नतीजा |
| Stop sequence | Halts generation | Generation रोकने वाला text |
| Transcript | Full step history | पूरा step इतिहास |

---

## ⚡ 3-Line Summary
English: ReAct loops Thought, Action, Observation until a Final Answer. Parse actions robustly and stop before fake Observations. Cap steps to control cost.
Hindi: ReAct Thought, Action, Observation का loop है जो Final Answer पर रुकता है। Actions को मज़बूती से parse करो और नकली Observation से पहले रोको। Cost के लिए steps सीमित रखो।

---

## ➡️ Next Topic
**582. Build LangGraph Workflow** — make the control flow explicit with nodes, state and conditional edges.
