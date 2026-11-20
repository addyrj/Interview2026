---

# 188. Swarm Pattern — Deep
# हिंदी में: Swarm Pattern (बिना बॉस के Agents का झुंड) — विस्तार से
# Framework: All
# Already Known: No

> Verified offline with fake agents (no API key). Python 3.13, fastapi 0.163.1, httpx 0.28.1, pydantic 2.14.3. The code is a framework-free implementation of the idea; it does not use any Swarm library. Real LLM calls: not run, needs an LLM API key. Token figures are approximate formulas only.

---

## 🔵 Simple Definition (2-3 lines)
In a Swarm there is no central supervisor. Each agent has its own instructions and tools, and any agent can hand the conversation over to a peer when it decides that peer is better suited. Control moves from agent to agent; the shared conversation state travels with it.

## 🔵 सरल परिभाषा (Hindi)
Swarm में कोई केंद्रीय supervisor नहीं होता। हर agent के अपने instructions और tools होते हैं, और कोई भी agent बातचीत किसी साथी agent को सौंप सकता है जब उसे लगे कि वह बेहतर है। Control एक agent से दूसरे तक घूमता है और साझा बातचीत का state साथ चलता है।

---

## 🔴 Problem it Solves
A supervisor is a bottleneck and a single point of failure, and it pays one LLM call per step just to coordinate. For conversational flows (support, triage, onboarding) the agent that currently talks to the user often knows best who should take over. A swarm removes the extra hop, keeps each prompt small, and scales by adding agents.

## 🔴 यह क्यों बना? (Hindi)
Supervisor एक bottleneck और single point of failure है, और सिर्फ़ coordination के लिए हर step पर एक LLM call लगती है। Support, triage, onboarding जैसे बातचीत वाले flows में जो agent अभी user से बात कर रहा है वही अक्सर जानता है कि आगे कौन सँभाले। Swarm अतिरिक्त hop हटाता है, prompts छोटे रखता है और agent जोड़कर scale होता है।

---

## 🟢 How it Works

```
Step 1 → Start with an entry agent (e.g. Triage) and the shared context
Step 2 → Active agent reads context and either:
           (a) answers the user, or
           (b) returns a HANDOFF to another agent (a "transfer" function)
Step 3 → On handoff, the active agent changes; the context (history + variables) is kept
Step 4 → New agent continues with its own instructions and tools
Step 5 → Repeat until an agent answers the user without handing off
Step 6 → Guards: max_handoffs, block ping-pong A -> B -> A, track the trail
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Entry agent (जैसे Triage) और साझा context से शुरू करो
Step 2 → Active agent context पढ़ता है और या तो:
           (a) user को जवाब देता है, या
           (b) किसी दूसरे agent को HANDOFF लौटाता है (एक "transfer" function)
Step 3 → Handoff पर active agent बदलता है; context (history + variables) वही रहता है
Step 4 → नया agent अपने instructions और tools के साथ आगे बढ़ता है
Step 5 → तब तक दोहराओ जब तक कोई agent बिना handoff के user को जवाब न दे
Step 6 → Guards: max_handoffs, A -> B -> A ping-pong रोको, trail रिकॉर्ड करो
```

---

## 🟡 Real World Example
**Tariff Agent support desk**: User chats with the Triage agent. It hands off to the Classification agent for "what is the HS code". That agent, after finding the code, notices the user asks about restrictions and hands off to the Compliance agent. Compliance answers. No manager decided any of this; each agent knew its neighbours. Customer Support and Code Agent teams use the same idea.

## 🟡 Real Example Hindi mein
**Tariff Agent support desk**: User Triage agent से बात करता है। "HS code क्या है" पर वह Classification agent को handoff करता है। उस agent को code मिलने के बाद लगता है कि user restrictions पूछ रहा है, तो वह Compliance agent को handoff करता है। Compliance जवाब देता है। यह किसी manager ने तय नहीं किया; हर agent अपने पड़ोसियों को जानता था। Customer Support और Code Agent टीमें भी यही तरीका अपनाती हैं।

---

## 💻 Code Example — Basic
```python
# Basic swarm: agents return either text or a Handoff to a peer. Runs offline.
from dataclasses import dataclass, field          # data containers


@dataclass
class Handoff:                                    # signal: "give control to this agent"
    to: str


@dataclass
class Context:                                    # shared state travelling with control
    user_msg: str
    vars: dict[str, str] = field(default_factory=dict)
    trail: list[str] = field(default_factory=list)  # which agents ran


def triage(ctx: Context) -> str | Handoff:        # agent 1: only routes
    if "hs" in ctx.user_msg.lower():
        return Handoff("classification")
    return "Hi! How can I help with tariffs?"


def classification(ctx: Context) -> str | Handoff:  # agent 2
    ctx.vars["hs_code"] = "8518.22"               # work product kept in shared vars
    if "restrict" in ctx.user_msg.lower():        # peer is better suited -> handoff
        return Handoff("compliance")
    return f"HS code is {ctx.vars['hs_code']}"


def compliance(ctx: Context) -> str | Handoff:    # agent 3
    return f"Code {ctx.vars.get('hs_code')} needs a BIS certificate"


AGENTS = {"triage": triage, "classification": classification, "compliance": compliance}


def run(msg: str, start: str = "triage", max_handoffs: int = 4) -> str:
    ctx = Context(user_msg=msg)
    active = start
    for _ in range(max_handoffs + 1):             # bounded number of hops
        ctx.trail.append(active)
        out = AGENTS[active](ctx)                 # active agent acts
        if isinstance(out, Handoff):              # control moves to a peer
            active = out.to
            continue
        print("trail:", " -> ".join(ctx.trail))   # observability
        return out                                # plain text = final answer
    return "Too many handoffs, escalating to a human."


if __name__ == "__main__":
    print(run("HS code for speaker, is it restricted?"))
```

## 💻 Code Example — Advanced
```python
# Advanced: async swarm with typed handoffs (allow-list), ping-pong guard,
# per-agent timeout, FastAPI endpoint, approximate token accounting. Offline.
import asyncio                                    # async + timeout
from dataclasses import dataclass, field
from fastapi import FastAPI                       # web framework
from fastapi.testclient import TestClient         # offline client
from pydantic import BaseModel                    # request model


@dataclass
class Handoff:
    to: str


@dataclass
class Ctx:
    msg: str
    vars: dict[str, str] = field(default_factory=dict)
    trail: list[str] = field(default_factory=list)
    tokens: int = 0                               # approximate running tokens


ALLOWED: dict[str, set[str]] = {                  # who may hand off to whom (security)
    "triage": {"classification", "compliance"},
    "classification": {"compliance"},
    "compliance": set(),                          # terminal agent
}


def est(t: str) -> int:                           # ~4 chars per token (approximate)
    return max(1, len(t) // 4)


async def triage(c: Ctx) -> str | Handoff:       # fake async LLM agents
    await asyncio.sleep(0)
    return Handoff("classification") if "hs" in c.msg.lower() else "How can I help?"


async def classification(c: Ctx) -> str | Handoff:
    await asyncio.sleep(0)
    c.vars["hs_code"] = "8518.22"
    return Handoff("compliance") if "restrict" in c.msg.lower() else f"HS {c.vars['hs_code']}"


async def compliance(c: Ctx) -> str | Handoff:
    await asyncio.sleep(0)
    return f"{c.vars.get('hs_code', '?')} requires BIS certification"


AGENTS = {"triage": triage, "classification": classification, "compliance": compliance}


async def swarm(msg: str, max_handoffs: int = 4) -> dict:
    c = Ctx(msg=msg)
    active = "triage"
    for _ in range(max_handoffs + 1):
        c.trail.append(active)
        try:
            out = await asyncio.wait_for(AGENTS[active](c), 5.0)   # bounded agent turn
        except asyncio.TimeoutError:
            return {"answer": "Agent timed out", "trail": c.trail, "escalate": True}
        c.tokens += est(c.msg)                    # each agent re-reads the context
        if isinstance(out, Handoff):
            if out.to not in ALLOWED[active]:     # block illegal / hallucinated handoffs
                return {"answer": "Invalid handoff", "trail": c.trail, "escalate": True}
            if out.to in c.trail:                 # ping-pong guard
                return {"answer": "Handoff loop", "trail": c.trail, "escalate": True}
            active = out.to
            continue
        return {"answer": out, "trail": c.trail, "approx_tokens": c.tokens, "escalate": False}
    return {"answer": "Too many handoffs", "trail": c.trail, "escalate": True}


class Req(BaseModel):
    message: str


app = FastAPI()


@app.post("/chat")
async def chat(req: Req) -> dict:
    return await swarm(req.message)


if __name__ == "__main__":
    client = TestClient(app)
    print(client.post("/chat", json={"message": "hello"}).json())
    print(client.post("/chat", json={"message": "HS code, is it restricted?"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Swarm support | Graph where agent nodes route to each other (peer edges / commands) | Not its main model (crews are task/role based; delegation between agents is possible) | Handoffs are a first-class idea; the Agents SDK is the production successor of the earlier educational Swarm project | Swarm-style team where agents hand off to named agents |
| Control passing | Edge or command to next node | Delegation | Handoff to another agent | Handoff message |
| Shared context | Graph state | Task context | Run context / history | Message history |
| Guard rails | Recursion limit, your checks | Your checks | `max_turns` and your checks | Termination conditions |
| Best for | Explicit peer graphs | Role crews | Support/triage flows | Chat teams |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Letting any agent hand off to any agent.
✅ Correct: Use an allow-list of handoffs; reject invalid targets.

❌ Mistake 2: No ping-pong guard (A hands to B, B back to A).
✅ Correct: Track the trail, cap handoffs, escalate to a human.

❌ Mistake 3: Each agent has a long prompt describing everything about all peers.
✅ Correct: Each agent knows only its neighbours and a one-line description of each.

❌ Mistake 4: Dropping context at handoff so the new agent re-asks questions.
✅ Correct: Carry history and structured variables across handoffs.

---

## 🧠 Tricky Interview Question
Why does a swarm often feel faster than a supervisor system, yet is harder to debug and govern?

Answer: Faster because no coordinator LLM call sits between steps: the agent already in control picks the next owner, so there is one hop less per transfer. Harder to debug because control flow is emergent: no single component owns the plan, so a wrong handoff decision is distributed across prompts. Governance suffers too: budgets, audit and stop rules must be enforced by a shared runtime, not by a boss agent. Mitigations: an allow-list of handoffs, a trail logged on every turn, a max-handoff cap, evaluation of handoff accuracy, and falling back to a supervisor for sensitive flows (payments, legal).

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What is a swarm of agents?
A1: Peer agents that hand the conversation to each other without a central coordinator.

Q2: (Medium) Swarm vs supervisor?
A2: Supervisor: central control, more predictable, one extra LLM call per step. Swarm: decentralized, lower coordination overhead, emergent control flow.

Q3: (Hard) How do you prevent infinite handoffs?
A3: Max handoff count, trail tracking to block cycles, an allow-list graph, and an escalation path to a human or supervisor.

Q4: (Hard) What state should travel on handoff?
A4: The conversation history (possibly summarized), structured variables (hs_code, user_id), and the reason for the handoff. Not raw private tool outputs the next agent should not see.

Q5: (System Design) Design a support swarm for tariff questions across 5 specialties.
A5: Triage entry agent; specialists with small prompts and an allow-list; shared structured context in Redis or a DB keyed by session; handoff cap of about 4; escalation to humans; trace every handoff with reason; evaluation set of conversations with labelled correct owners; canary new agents.

---

## 💰 Cost Impact
- Token formula (approximate): `total ≈ Σ per active agent (its instructions + shared history)`. No coordinator calls, but every agent re-reads the growing history.
- Tips: summarize history at handoff, small prompts per agent, cheaper model for triage, cap hops, cache static instructions where the provider supports prompt caching (check provider docs).
- Pricing: approximate, from public pricing at time of writing, verify.

---

## 🔷 When to Use
✅ Use when:
- Conversational flows where the current agent knows who is next
- You want low coordination overhead and small prompts
- Specialties are clear and few handoff paths exist

❌ Avoid when:
- You need strict central governance or a fixed audit order
- Many agents with dense handoff graphs (becomes unpredictable)
- High-risk actions needing one accountable planner

---

## 📊 Visual Diagram
```
 user --> [Triage] --hs?--> [Classification] --restricted?--> [Compliance] --> answer
              |                   |                                |
              +---- answer <------+------------- answer <----------+
        (any agent may answer directly; handoff only along allowed edges)
        shared context: history + variables travel with control
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Swarm | Peer agents without a boss | झुंड |
| Handoff | Passing control to a peer | कार्य हस्तांतरण |
| Entry agent | First agent that gets the user | प्रवेश agent |
| Allow-list | Permitted handoff targets | अनुमत सूची |
| Ping-pong | Agents bouncing the task back | आगे-पीछे चक्कर |
| Trail | Record of agents visited | मार्ग रिकॉर्ड |

---

## ⚡ 3-Line Summary
English: A swarm is a set of peer agents that hand control to each other, with shared context travelling along.
It avoids a coordinator bottleneck but makes control flow emergent.
Use allow-lists, hop caps and trail logging for safety.

Hindi: Swarm साथी agents का समूह है जो आपस में control सौंपते हैं और साझा context साथ चलता है।
इससे coordinator का bottleneck हटता है पर control flow अपने-आप उभरता है।
सुरक्षा के लिए allow-list, hop cap और trail logging लगाओ।

---

## ➡️ Next Topic
189. Handoff Pattern: the single building block of a swarm, studied in detail (what to pass, how to validate, how to return).

---
