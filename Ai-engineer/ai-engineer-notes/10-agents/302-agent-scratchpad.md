---

# 302. Agent Scratchpad
# हिंदी में: Agent Scratchpad

---

## 🔵 Simple Definition (English)
The agent scratchpad is the running record of what the agent has done in the current task: each action it chose and the observation (tool result) it got back. It is placed in the prompt on every loop turn, so the model can see its own earlier steps and decide the next one. In LangChain it is the `agent_scratchpad` placeholder.

## 🔵 सरल परिभाषा (Hindi)
Agent scratchpad current task में agent ने जो किया उसका चलता हुआ record है: हर action और उसका observation (tool result)। यह हर loop turn में prompt में डाला जाता है ताकि model अपने पिछले steps देखकर अगला step तय करे। LangChain में यह `agent_scratchpad` placeholder है।

---

## 🔴 Problem it Solves
An LLM call is stateless. Without a scratchpad, the model would forget it already called `search_hs_codes` and would repeat it forever, or never use the result. The scratchpad gives the model working memory for one task (different from long-term chat memory).

## 🔴 यह क्यों बना? (Hindi)
LLM call stateless होती है। Scratchpad के बिना model भूल जाएगा कि उसने `search_hs_codes` चला दिया है और वही बार-बार दोहराएगा, या result कभी इस्तेमाल नहीं करेगा। Scratchpad एक task के लिए working memory देता है (लंबे chat memory से अलग)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start: scratchpad = [] (empty)
Step 2 → Prompt = system + user question + scratchpad
Step 3 → Model returns an action (tool + args), e.g. search_hs_codes("earbuds")
Step 4 → Run the tool, get observation
Step 5 → Append (action, observation) to the scratchpad
Step 6 → Build the prompt again with the longer scratchpad
Step 7 → Repeat until the model returns a final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → शुरू में: scratchpad = [] (खाली)
Step 2 → Prompt = system + user सवाल + scratchpad
Step 3 → Model action देता है (tool + args), जैसे search_hs_codes("earbuds")
Step 4 → Tool चलाओ, observation लो
Step 5 → (action, observation) को scratchpad में जोड़ो
Step 6 → लंबे scratchpad के साथ prompt फिर बनाओ
Step 7 → तब तक दोहराओ जब तक model final answer न दे
```

---

## 🟡 Real World Example
**Tariff Classification System**: Question: "Duty on wireless earbuds?" Scratchpad after turn 1: `search_hs_codes("wireless earbuds") -> 851830 Headphones`. Turn 2 sees this and calls `get_duty_rate("851830") -> 20%`. Turn 3 sees both and writes the answer. If the scratchpad grew to 40 long entries, cost and confusion would grow, so we trim old observations.

**Zomato AI**: scratchpad holds `search_restaurants -> 5 results`, then `get_menu(id)`.

## 🟡 Real Example Hindi mein
**Tariff System**: सवाल: "Wireless earbuds पर duty?" Turn 1 के बाद scratchpad: `search_hs_codes("wireless earbuds") -> 851830 Headphones`। Turn 2 इसे देखकर `get_duty_rate("851830") -> 20%` चलाता है। Turn 3 दोनों देखकर जवाब लिखता है। 40 लंबी entries हो जाएँ तो cost और confusion बढ़ेगा, इसलिए पुराने observations छोटे करते हैं।

**Zomato AI**: scratchpad में `search_restaurants -> 5 results`, फिर `get_menu(id)`।

---

## 💻 Code Example — Basic
```python
# Basic: a hand-made scratchpad and agent loop with a scripted "LLM" (runs offline)
from dataclasses import dataclass, field               # data structures
from typing import Callable                            # callable type

@dataclass
class Step:
    tool: str            # tool name that was called
    args: dict           # arguments used
    observation: str     # result returned

@dataclass
class Scratchpad:
    steps: list[Step] = field(default_factory=list)    # all steps so far

    def add(self, step: Step) -> None:
        self.steps.append(step)                        # remember this step

    def render(self) -> str:
        """Text version placed in the prompt."""
        return "\n".join(f"Action: {s.tool}({s.args})\nObservation: {s.observation}" for s in self.steps)

TOOLS: dict[str, Callable[..., str]] = {
    "search_hs_codes": lambda query: "851830 Headphones and earphones",
    "get_duty_rate": lambda hs_code: "20%",
}

def scripted_llm(question: str, pad: Scratchpad) -> dict:
    """Fake model: decides next step by looking at the scratchpad."""
    if not pad.steps:                                  # nothing done yet -> search
        return {"action": "search_hs_codes", "args": {"query": question}}
    if len(pad.steps) == 1:                            # have code -> get duty
        return {"action": "get_duty_rate", "args": {"hs_code": "851830"}}
    return {"final": f"Duty is {pad.steps[-1].observation} for HS 851830."}

pad = Scratchpad()
question = "wireless earbuds"
for _ in range(5):                                     # bounded loop
    decision = scripted_llm(question, pad)
    if "final" in decision:                            # model finished
        print("FINAL:", decision["final"])
        break
    obs = TOOLS[decision["action"]](**decision["args"])   # run tool
    pad.add(Step(decision["action"], decision["args"], obs))
print("--- scratchpad ---")
print(pad.render())
```

## 💻 Code Example — Advanced
```python
# Production: LangChain scratchpad with messages, trimming, async, error handling
import asyncio                                           # async runtime
from typing import Any                                   # typing
from langchain_core.tools import tool                    # tools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI                  # chat model

@tool
def get_duty_rate(hs_code: str) -> str:
    """Return duty percent for an HS code."""
    return "20%"

# The scratchpad slot: LangChain agents fill this with AIMessage(tool_calls) + ToolMessage pairs
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff assistant. Use tools for facts."),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),             # REQUIRED name for AgentExecutor agents
])

def trim_scratchpad(pad: list[BaseMessage], keep_last: int = 6, max_obs_chars: int = 500) -> list[BaseMessage]:
    """Keep recent steps; shorten long tool outputs to protect the context window."""
    trimmed: list[BaseMessage] = []
    for m in pad[-keep_last:]:
        if isinstance(m, ToolMessage) and len(str(m.content)) > max_obs_chars:
            m = ToolMessage(content=str(m.content)[:max_obs_chars] + "...[cut]", tool_call_id=m.tool_call_id)
        trimmed.append(m)
    return trimmed

async def run(question: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([get_duty_rate])
    chain = prompt | llm                                  # LCEL chain
    pad: list[BaseMessage] = []                           # our scratchpad as messages
    for _ in range(5):                                    # iteration guard
        ai: AIMessage = await chain.ainvoke({"input": question, "agent_scratchpad": trim_scratchpad(pad)})
        if not ai.tool_calls:
            return str(ai.content)                        # final answer
        pad.append(ai)                                    # action goes into scratchpad
        for call in ai.tool_calls:
            try:
                obs = await get_duty_rate.ainvoke(call["args"]) if call["name"] == "get_duty_rate" else "unknown tool"
            except Exception as exc:                      # error becomes an observation
                obs = f"error: {exc}"
            pad.append(ToolMessage(content=str(obs), tool_call_id=call["id"]))   # observation
    return "Stopped: too many steps"

if __name__ == "__main__":
    print(asyncio.run(run("What is the duty for HS 851830?")))   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Return the scratchpad as a "trace" so support teams can debug. Hide it from normal end users.

```python
from fastapi import FastAPI                              # framework
from pydantic import BaseModel

app = FastAPI()

class Q(BaseModel):
    question: str
    debug: bool = False

@app.post("/agent")
async def agent(q: Q) -> dict[str, Any]:
    pad_text = Scratchpad()                              # reuse the Basic class for trace data
    answer = await run(q.question)
    body: dict[str, Any] = {"answer": answer}
    if q.debug:                                          # only for internal users
        body["trace"] = pad_text.render()
    return body
```

---

## 🔗 LangChain / LangGraph Connection
In legacy `AgentExecutor`, the prompt MUST contain `agent_scratchpad` and the executor fills it via `format_to_tool_messages`. In LangGraph there is no separate scratchpad: the `messages` list in state IS the scratchpad (AIMessage tool calls + ToolMessages accumulate with the `add_messages` reducer).

```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [get_duty_rate])
out = agent.invoke({"messages": [("user", "Duty for HS 851830?")]})
for m in out["messages"]:            # human, ai(tool_call), tool, ai(final) = the scratchpad
    print(type(m).__name__)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `agent_scratchpad` in the prompt
✅ Correct: Add `MessagesPlaceholder("agent_scratchpad")`.

```python
# Wrong - create_tool_calling_agent raises: prompt missing agent_scratchpad
prompt = ChatPromptTemplate.from_messages([("system", "..."), ("human", "{input}")])
# Right
prompt = ChatPromptTemplate.from_messages([("system", "..."), ("human", "{input}"),
                                           MessagesPlaceholder("agent_scratchpad")])
```

❌ Mistake 2: Letting the scratchpad grow without limit
✅ Correct: Trim or summarise old observations.

```python
# Wrong
pad.append(ToolMessage(content=huge_json, tool_call_id=i))
# Right
pad.append(ToolMessage(content=huge_json[:500], tool_call_id=i))
```

---

## 🧠 Tricky Interview Question
**Q**: "Your agent answers correctly on 3-step tasks but gets worse and costs 10x more on 20-step tasks. What is going on?"

**Answer**: The scratchpad is resent in full every turn, so input tokens grow roughly quadratically with steps (turn n pays for all n-1 previous steps). Long, noisy history also dilutes attention ("lost in the middle"). Fixes: truncate tool outputs, summarise old steps, keep only relevant observations, use prompt caching for the stable prefix, break the job into sub-agents with fresh scratchpads, and set an iteration cap.

---

## ⚫ Interview Questions + Answers

Q1: What is the agent scratchpad?
A1: The record of previous actions and observations in the current task, passed to the model each turn.

Q2: Is the scratchpad the same as chat memory?
A2: No. Scratchpad is within one task run; chat memory persists across user turns.

Q3: How is it represented in modern LangChain?
A3: As a list of messages (AIMessage with tool_calls and ToolMessage results) passed through `MessagesPlaceholder("agent_scratchpad")`. Older ReAct agents used one string.

Q4: Why does the scratchpad increase cost?
A4: It is part of the input on every turn, so total input tokens accumulate.

Q5: (Hard) How would you manage a very long scratchpad in production?
A5: Truncate big observations, summarise old steps with a cheap model, store large results externally and keep only an ID/short summary, cache the static prefix, add iteration/time limits, and checkpoint state in LangGraph so you can resume.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Task needs multiple tool steps with dependencies

❌ Avoid when:
- One tool call is enough (no loop needed)
- Steps are independent (run in parallel instead)

---

## 📊 Visual Diagram
```
 Turn 1: [system][question][ ]                       -> Action A
 Turn 2: [system][question][A -> obsA]               -> Action B
 Turn 3: [system][question][A -> obsA][B -> obsB]    -> FINAL ANSWER
                           \_______ scratchpad grows _______/
 Tokens per turn:  t1 < t2 < t3   (history resent each time)
```

---

## 💰 Cost Impact
- Input tokens per turn = base prompt + scratchpad. Sum over N turns is about N x base + N(N+1)/2 x average step size.
- Example: base 800 tokens, step 300 tokens, 10 turns = about 8,000 + 16,500 = 24,500 input tokens.
- Optimise: truncate observations, summarise, prompt caching, fewer steps, cheaper model for simple loops, report usage per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Scratchpad | Working record of steps | Steps का working record |
| Action | Tool call chosen by model | Model द्वारा चुना tool call |
| Observation | Tool result | Tool का नतीजा |
| MessagesPlaceholder | Slot for message list in prompt | Prompt में messages की जगह |
| Trimming | Cutting old/long content | पुराना/लंबा हिस्सा काटना |
| Reducer | Merge rule for state (add_messages) | State जोड़ने का नियम |

---

## ⚡ 3-Line Summary
English: The scratchpad stores the agent's actions and observations so each turn can build on the last. It is resent every turn, so it drives token cost and needs trimming. In LangGraph, the messages list in state plays this role.
Hindi: Scratchpad agent के actions और observations रखता है ताकि हर turn पिछले पर बने। यह हर turn दोबारा भेजा जाता है, इसलिए token cost बढ़ाता है और trimming चाहिए। LangGraph में state की messages list यही काम करती है।

---

## ➡️ Next Topic
**303. Agent Stop Conditions** — how and when an agent should decide it is finished.
