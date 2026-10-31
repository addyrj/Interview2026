---

# 351. Peer-to-Peer Agents
# हिंदी में: Peer-to-Peer Agents

---

## 🔵 Simple Definition (English)
In a peer-to-peer (network) design there is no central boss. Every agent can hand work directly to any other agent it thinks is best. Control moves from agent to agent, which is also called the "handoff" or "swarm" pattern.

## 🔵 सरल परिभाषा (Hindi)
Peer-to-peer (network) design में कोई central boss नहीं होता। हर agent सीधे किसी भी दूसरे agent को काम दे सकता है जो उसे सबसे सही लगे। Control एक agent से दूसरे को जाता है; इसे "handoff" या "swarm" pattern भी कहते हैं।

---

## 🔴 Problem it Solves
- A supervisor is a single point of failure and adds an extra LLM call per step.
- Some workflows are conversations where the next speaker is obvious to the current agent (triage -> billing -> shipping).
- Central routing needs knowledge of all agents; peers only need to know their neighbours.

## 🔴 यह क्यों बना? (Hindi)
- Supervisor single point of failure है और हर step पर extra LLM call जोड़ता है।
- कुछ workflows बातचीत जैसे होते हैं जहाँ अगला agent current agent को पता होता है।
- Central routing को सभी agents की जानकारी चाहिए; peers को सिर्फ पड़ोसी चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Entry agent receives the user message
Step 2 → It answers OR decides to hand off to a peer
Step 3 → Handoff = (target agent name + reason + context summary)
Step 4 → Active agent changes; the new agent continues the conversation
Step 5 → Peers can hand back or onward
Step 6 → An agent that has the final answer replies to the user
Step 7 → Hop limit and loop detection stop endless ping-pong
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Entry agent को user message मिलता है
Step 2 → वह खुद जवाब देता है या peer को handoff करता है
Step 3 → Handoff = (target agent का नाम + कारण + context summary)
Step 4 → Active agent बदलता है; नया agent बातचीत आगे बढ़ाता है
Step 5 → Peers वापस या आगे handoff कर सकते हैं
Step 6 → जिसके पास final answer है वह user को जवाब देता है
Step 7 → Hop limit और loop detection endless ping-pong रोकते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A *Triage* agent receives "my shipment was held at customs". It hands off to the *Dispute* agent, which needs the HS code and hands off to the *Classifier* peer; the classifier answers, hands back to *Dispute*, which writes the appeal. No manager is involved.

**Zomato**: Chat starts with a general agent, which hands off to refund agent when it sees "money not returned". **Amazon**: Sales assistant hands to returns assistant.

## 🟡 Real Example Hindi mein
**Tariff System**: *Triage* agent को "shipment customs में रुकी है" मिलता है। वह *Dispute* agent को handoff करता है; उसे HS code चाहिए तो *Classifier* peer को handoff करता है; classifier जवाब देकर वापस *Dispute* को देता है, जो appeal लिखता है। बीच में कोई manager नहीं।

---

## 💻 Code Example — Basic
```python
# Peer handoff with plain Python; each agent returns (reply, next_agent)
from typing import Callable  # type hints

Handler = Callable[[str], tuple[str, str | None]]  # returns reply and optional next peer


def triage(msg: str) -> tuple[str, str | None]:
    if "held" in msg or "customs" in msg:  # simple rule instead of LLM
        return "Passing to dispute agent", "dispute"
    return "Hello, how can I help?", None


def dispute(msg: str) -> tuple[str, str | None]:
    if "code" not in msg:  # missing info -> ask peer
        return "Need HS code", "classifier"
    return "Appeal drafted", None


def classifier(msg: str) -> tuple[str, str | None]:
    return "HS code 6109.10 found", "dispute"


AGENTS: dict[str, Handler] = {"triage": triage, "dispute": dispute, "classifier": classifier}

msg, current = "shipment held at customs", "triage"  # start
for _ in range(6):  # hop limit
    reply, nxt = AGENTS[current](msg)  # active agent acts
    print(f"{current}: {reply}")  # show the conversation
    if nxt is None:  # nobody to hand off to
        break
    if nxt == "dispute" and current == "classifier":
        msg += " code 6109.10"  # share new info
    current = nxt  # hand off
```

## 💻 Code Example — Advanced
```python
# Async swarm with typed handoff, visited-path loop guard and error handling
import asyncio  # async runtime
from dataclasses import dataclass, field  # containers


@dataclass
class Handoff:
    to: str  # target agent
    reason: str  # why
    context: str  # short summary for the next agent


@dataclass
class Turn:
    reply: str  # text for the user
    handoff: Handoff | None = None  # optional handoff


async def triage(ctx: str) -> Turn:
    await asyncio.sleep(0.01)
    return Turn("Routing you", Handoff("classifier", "needs code", ctx))


async def classifier(ctx: str) -> Turn:
    await asyncio.sleep(0.01)
    return Turn("HS code is 6109.10")  # final answer, no handoff


AGENTS = {"triage": triage, "classifier": classifier}  # registry


@dataclass
class Swarm:
    max_hops: int = 5  # limit
    trail: list[str] = field(default_factory=list)  # visited agents

    async def run(self, start: str, ctx: str) -> str:
        current = start
        for _ in range(self.max_hops):
            if current not in AGENTS:  # bad handoff target
                raise KeyError(f"unknown agent {current}")
            self.trail.append(current)  # record visit
            if self.trail.count(current) > 2:  # simple loop detection
                raise RuntimeError(f"loop at {current}")
            turn = await AGENTS[current](ctx)  # run active agent
            if turn.handoff is None:
                return turn.reply  # done
            current, ctx = turn.handoff.to, turn.handoff.context  # switch
        raise RuntimeError("hop limit")


if __name__ == "__main__":
    s = Swarm()
    print(asyncio.run(s.run("triage", "cotton t-shirt held")), s.trail)
```

---

## 🟠 FastAPI Integration
Keep the "active agent" in the session so the conversation continues with the right peer on the next request.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app
SESSIONS: dict[str, str] = {}  # session_id -> active agent (use Redis in production)


class Chat(BaseModel):
    session_id: str  # conversation id
    message: str  # user text


@app.post("/chat")
async def chat(req: Chat) -> dict:
    active = SESSIONS.get(req.session_id, "triage")  # resume active agent
    if "customs" in req.message:  # mock handoff rule
        active = "dispute"
    SESSIONS[req.session_id] = active  # persist
    return {"active_agent": active, "reply": f"{active} here"}
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph "network" architecture: every node can return `Command(goto=other_agent)`. The package `langgraph-swarm` provides ready handoff tools (`create_handoff_tool`), but plain `Command` is enough.

```python
from langgraph.graph import StateGraph, MessagesState, START, END  # graph
from langgraph.types import Command  # routing
from typing import Literal  # types


def triage(s: MessagesState) -> Command[Literal["classifier"]]:
    return Command(goto="classifier")  # peer handoff


def classifier(s: MessagesState) -> Command[Literal["__end__"]]:
    return Command(goto=END)  # finish


g = StateGraph(MessagesState)  # graph
g.add_node("triage", triage)
g.add_node("classifier", classifier)
g.add_edge(START, "triage")  # entry agent
print(g.compile().invoke({"messages": [("user", "held at customs")]})["messages"][-1].content)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No loop protection.
✅ Correct: Hop limit plus visited counter.

```python
# Wrong
# while nxt: nxt = AGENTS[nxt](msg)[1]
# Right
for _ in range(6):
    break
```

❌ Mistake 2: Handoff without context.
✅ Correct: Pass a summary.

```python
# Wrong
handoff = {"to": "classifier"}
# Right
handoff = {"to": "classifier", "context": "cotton t-shirt, knitted, seeking 8-digit code"}
```

---

## 🧠 Tricky Interview Question
**Q**: "In a swarm, two agents each think the other is better suited and bounce the user back and forth. How do you fix this?"

**Answer**: This is a handoff loop from overlapping or unclear responsibilities. Fixes: a hop limit and visited-agent counter, rules that an agent must answer if it was already visited, clearer role boundaries and handoff criteria in prompts, a fallback "owner" agent (or human) after N hops, and trace review to see which phrases trigger the bounce.

---

## ⚫ Interview Questions + Answers

Q1: What is a peer-to-peer agent system?
A1: Agents hand off directly to each other without a central supervisor.

Q2: Name one benefit and one risk.
A2: Benefit: no central bottleneck and fewer LLM calls. Risk: loops and unpredictable paths.

Q3: What should a handoff contain?
A3: Target agent, reason and a concise context summary (plus any structured data needed).

Q4: Supervisor versus network pattern?
A4: Supervisor centralises decisions (predictable, easier to control, extra calls). Network decentralises (faster, flexible, harder to debug).

Q5: How do you make a swarm production-safe?
A5: Hop and time limits, loop detection, typed handoffs, persisted active-agent per session, tracing of the path, a human-escalation fallback, and tests that replay recorded conversations to confirm routing stays stable after prompt changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Conversational flows (support, triage)
- Each agent knows its natural next step

❌ Avoid when:
- You need strict, auditable order
- Many agents overlap in skills

---

## 📊 Visual Diagram
```
   ┌────────┐  handoff  ┌──────────┐
   │ Triage │──────────►│ Dispute  │
   └────────┘           └──┬────▲──┘
                           │    │
                   handoff │    │ result
                           ▼    │
                        ┌───────┴──┐
                        │Classifier│
                        └──────────┘
          (no central manager)
```

---

## 💰 Cost Impact
Fewer routing calls than a supervisor design (no manager LLM call per hop), but bad loops can burn tokens quickly. Pass summaries instead of the whole chat on handoff, set hop limits, and use small models for triage.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Peer | Equal agent | बराबरी का agent |
| Handoff | Transfer of control | control का transfer |
| Swarm | Network of peers | peers का network |
| Active agent | Agent currently in control | जिसके पास control है |
| Loop guard | Protection from cycles | cycle से बचाव |
| Escalation | Fallback to human/owner | human/owner को भेजना |

---

## ⚡ 3-Line Summary
English: Peer-to-peer agents hand off directly with no central boss. It is fast and flexible but can loop. Use typed handoffs, hop limits and a fallback owner.
Hindi: Peer-to-peer agents बिना central boss के सीधे handoff करते हैं। यह तेज़ और flexible है पर loop हो सकता है। Typed handoffs, hop limits और fallback owner रखो।

---

## ➡️ Next Topic
**352. Specialist Agents** — deep, narrow agents (legal, math, code) and how to build and combine them.
