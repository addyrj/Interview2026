---

# 309. Agent with Human in Loop
# हिंदी में: Human in Loop वाला Agent (इंसान की मंज़ूरी के साथ)

---

## 🔵 Simple Definition (English)
Human-in-the-loop (HITL) means the agent pauses before a risky or uncertain step, asks a person to approve, edit or reject it, and then continues. The agent's state is saved while it waits, so the person can answer minutes or days later.

## 🔵 सरल परिभाषा (Hindi)
Human-in-the-loop (HITL) में agent किसी risky या अनिश्चित step से पहले रुकता है, इंसान से approve, edit या reject करवाता है, और फिर आगे बढ़ता है। इंतज़ार के दौरान agent की state save रहती है, इसलिए इंसान मिनटों या दिनों बाद भी जवाब दे सकता है।

---

## 🔴 Problem it Solves
Agents make mistakes. A wrong HS code on a customs filing means fines. A wrong refund or email cannot be undone. Fully autonomous agents are risky for money, legal and irreversible actions. HITL adds a safety gate where accuracy matters most, while still automating the boring parts.

## 🔴 यह क्यों बना? (Hindi)
Agents गलतियाँ करते हैं। Customs filing में गलत HS code का मतलब जुर्माना है। गलत refund या email वापस नहीं होता। Money, legal और irreversible actions के लिए पूरी तरह autonomous agent खतरनाक है। HITL वहाँ safety gate लगाता है जहाँ accuracy सबसे ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Agent plans an action (e.g. submit_filing(hs_code))
Step 2 → A policy decides: risky? low confidence? high value?
Step 3 → If risky → INTERRUPT: save state, expose the proposed action
Step 4 → Human reviews in UI: approve / edit / reject (+ comment)
Step 5 → System RESUMES from the saved state with the human's decision
Step 6 → Approved → run action; edited → run with new args; rejected → agent re-plans
Step 7 → Log who approved what and when (audit trail)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Agent एक action plan करता है (जैसे submit_filing)
Step 2 → Policy तय करती है: risky? कम confidence? ज़्यादा value?
Step 3 → Risky हो तो INTERRUPT: state save, प्रस्तावित action दिखाओ
Step 4 → इंसान review करता है: approve / edit / reject
Step 5 → Saved state से RESUME, इंसान के फैसले के साथ
Step 6 → Approve तो चलाओ; edit तो नए args से; reject तो दोबारा plan
Step 7 → किसने क्या approve किया, इसका audit log रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The agent classifies "industrial servo motor" with confidence 0.62. Policy says confidence under 0.8 needs review. The case goes to a customs broker's queue. The broker changes the code from 8501.31 to 8501.32 and approves. The agent files the declaration with the corrected code. High-confidence items (0.95) are filed automatically.

**Amazon-style**: refunds above a limit need manager approval.

## 🟡 Real Example Hindi mein
**Tariff System**: Agent "industrial servo motor" को 0.62 confidence से classify करता है। Policy: 0.8 से कम पर review। Case customs broker की queue में जाता है। Broker code 8501.31 से 8501.32 करके approve करता है। Agent सही code से filing करता है। 0.95 confidence वाले items अपने आप file होते हैं।
**Amazon**: सीमा से बड़े refund पर manager की मंज़ूरी।

---

## 💻 Code Example — Basic
```python
# Basic: approval gate in plain Python (offline; human input is simulated).
from dataclasses import dataclass               # simple record
from typing import Literal                      # decision type

Decision = Literal["approve", "reject", "edit"] # allowed human decisions

@dataclass
class Proposal:                                 # what the agent wants to do
    action: str                                 # action name
    hs_code: str                                # proposed HS code
    confidence: float                           # model confidence 0..1

def needs_review(p: Proposal, threshold: float = 0.8) -> bool:
    return p.confidence < threshold             # low confidence -> human

def human_review(p: Proposal) -> tuple[Decision, str]:
    # In real life this is a UI/queue. Here we simulate an edit.
    return "edit", "8501.32"                    # human changes the code

def execute(p: Proposal) -> str:
    return f"FILED {p.action} with {p.hs_code}" # the real side effect

def run(p: Proposal) -> str:
    if not needs_review(p):                     # confident -> auto
        return execute(p)
    decision, value = human_review(p)           # pause for human
    if decision == "reject":                    # human said no
        return "REJECTED: agent must re-plan"
    if decision == "edit":                      # human fixed it
        p.hs_code = value
    return execute(p)                           # approve or edited

if __name__ == "__main__":
    print(run(Proposal("submit_filing", "8501.31", 0.62)))   # FILED ... 8501.32
    print(run(Proposal("submit_filing", "8517.13", 0.95)))   # auto filed
```

## 💻 Code Example — Advanced
```python
# Production: pause/resume with persistent state, async, timeout and audit log.
import asyncio                                  # async primitives
import logging                                  # logging
import time                                     # timestamps
import uuid                                     # ids for pending reviews
from dataclasses import dataclass, field        # records
from typing import Any

log = logging.getLogger("hitl")                 # logger

@dataclass
class PendingReview:                            # saved while waiting for a human
    review_id: str
    payload: dict[str, Any]                     # proposed action + args
    created: float = field(default_factory=time.time)
    future: "asyncio.Future[dict[str, Any]]" = field(default=None)  # resolved by human

class ReviewQueue:
    def __init__(self) -> None:
        self.pending: dict[str, PendingReview] = {}   # use DB/Redis in production
        self.audit: list[dict[str, Any]] = []         # who did what

    async def request(self, payload: dict[str, Any], timeout: float = 3600) -> dict[str, Any]:
        rid = str(uuid.uuid4())                       # new review id
        fut: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self.pending[rid] = PendingReview(rid, payload, future=fut)
        try:
            return await asyncio.wait_for(fut, timeout)   # wait for the human
        except asyncio.TimeoutError:                       # nobody answered
            log.warning("review %s timed out", rid)
            return {"decision": "reject", "reason": "timeout"}   # fail safe = do NOT act
        finally:
            self.pending.pop(rid, None)                    # cleanup

    def respond(self, rid: str, reviewer: str, decision: str, edits: dict[str, Any] | None = None) -> None:
        item = self.pending.get(rid)                       # find pending item
        if item is None:
            raise KeyError("unknown or expired review")    # surface to API as 404
        self.audit.append({"rid": rid, "by": reviewer, "decision": decision, "t": time.time()})
        item.future.set_result({"decision": decision, "edits": edits or {}})   # wake agent

queue = ReviewQueue()

async def agent_step(hs_code: str, confidence: float) -> str:
    if confidence >= 0.8:                                  # auto path
        return f"FILED {hs_code}"
    answer = await queue.request({"action": "file", "hs_code": hs_code, "confidence": confidence})
    if answer["decision"] == "reject":
        return "NOT FILED"
    final = answer["edits"].get("hs_code", hs_code)        # use human's edit if given
    return f"FILED {final}"

async def demo() -> None:
    task = asyncio.create_task(agent_step("8501.31", 0.6))   # agent pauses
    await asyncio.sleep(0.05)                                # let it register
    rid = next(iter(queue.pending))                          # simulate reviewer
    queue.respond(rid, "broker_1", "edit", {"hs_code": "8501.32"})
    print(await task)                                        # FILED 8501.32

if __name__ == "__main__":
    asyncio.run(demo())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException      # framework
from pydantic import BaseModel                  # validation

app = FastAPI()

class Decision(BaseModel):                      # reviewer payload
    reviewer: str
    decision: str                               # approve | reject | edit
    edits: dict | None = None

@app.get("/reviews")                            # reviewer UI lists pending items
async def list_reviews() -> list[dict]:
    return [{"id": r.review_id, **r.payload} for r in queue.pending.values()]

@app.post("/reviews/{rid}")                     # reviewer answers
async def answer(rid: str, body: Decision) -> dict:
    try:
        queue.respond(rid, body.reviewer, body.decision, body.edits)
    except KeyError:
        raise HTTPException(404, "Review not found or expired")
    return {"ok": True}
```
In a real system the agent run and the review API may be different processes, so save the pending state in a database (this is why LangGraph checkpointers exist).

---

## 🔗 LangChain / LangGraph Connection
LangGraph has first-class support: `interrupt()` pauses the graph, a checkpointer saves state, and `Command(resume=...)` continues it.

```python
from typing import TypedDict                               # state type
from langgraph.graph import StateGraph, START, END         # graph builder
from langgraph.checkpoint.memory import MemorySaver        # needed for interrupts
from langgraph.types import interrupt, Command            # HITL primitives

class S(TypedDict):
    hs_code: str
    status: str

def propose(state: S) -> S:
    return {"hs_code": "8501.31", "status": "proposed"}

def approval(state: S) -> S:
    decision = interrupt({"question": "Approve this HS code?", "hs_code": state["hs_code"]})  # PAUSE here
    return {"hs_code": decision.get("hs_code", state["hs_code"]), "status": "approved"}

g = StateGraph(S)
g.add_node("propose", propose); g.add_node("approval", approval)
g.add_edge(START, "propose"); g.add_edge("propose", "approval"); g.add_edge("approval", END)
app_graph = g.compile(checkpointer=MemorySaver())

cfg = {"configurable": {"thread_id": "case-1"}}
app_graph.invoke({"hs_code": "", "status": ""}, cfg)                    # stops at interrupt
final = app_graph.invoke(Command(resume={"hs_code": "8501.32"}), cfg)   # human answer
print(final)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Blocking a web request while waiting for a human.
✅ Correct: return a `pending` status immediately, store the state, and resume later via another endpoint.

```python
# Wrong: HTTP request hangs for hours
answer = input("approve? ")
# Right: save state, respond 202, resume in /reviews/{id}
```

❌ Mistake 2: Interrupting on everything (review fatigue) or nothing.
✅ Correct: use thresholds: money value, confidence, irreversible actions.

❌ Mistake 3: Default to "approve" on timeout.
✅ Correct: fail safe, so timeout means reject or escalate.

---

## 🧠 Tricky Interview Question
**Q**: "In LangGraph, after resuming from an interrupt, your node's side-effect (sending an email) ran twice. Why?"

**Answer**: When a graph resumes, the interrupted node is **re-executed from its start**; `interrupt()` then returns the human's value. Any code before `interrupt()` in the same node runs again. So put side effects after the interrupt, or in a separate node, or make them idempotent with an idempotency key.

---

## ⚫ Interview Questions + Answers

Q1: What is human-in-the-loop?
A1: A design where a person approves, edits or rejects agent actions at chosen checkpoints.

Q2: Why do we need a checkpointer for HITL?
A2: The graph must stop and later continue, possibly in another process. The checkpointer stores state keyed by `thread_id`.

Q3: Which actions should require approval?
A3: Irreversible or costly ones: payments, deletes, emails to customers, legal filings, and low-confidence decisions.

Q4: How do you avoid review fatigue?
A4: Review only exceptions by confidence or risk, batch similar items, show clear diffs and sources, and sample-audit auto-approved items.

Q5: (Hard) Design HITL for 10,000 classifications per day with 5 reviewers.
A5: Route by confidence: more than 0.9 auto, otherwise queue by priority and SLA. Save state in a DB, assign items with locks, show evidence (retrieved rules, top-3 candidates), record decisions as labelled data, and use them to retrain prompts or thresholds. Monitor queue age and reviewer agreement.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Actions are irreversible or regulated
- Model confidence is low
- You need an audit trail

❌ Avoid when:
- Actions are cheap and reversible
- Volume is too high for humans and errors are acceptable
- Low latency is required end to end

---

## 📊 Visual Diagram
```
 Agent ──► propose action ──► risky? ──no──► execute
                               │yes
                               ▼
                    save state + INTERRUPT
                               │
                      ┌────────▼────────┐
                      │ Human: approve  │
                      │ / edit / reject │
                      └────────┬────────┘
                               ▼
                       RESUME (Command)
                               ▼
                    execute / re-plan / stop
```

---

## 💰 Cost Impact
While the agent waits, no LLM tokens are used, so waiting is free. Costs come from human time and from re-running work after rejection. Optimise by sending only low-confidence cases to humans, giving the reviewer concise evidence (short context), and using review decisions to improve prompts so fewer cases need review. On resume, only the interrupted node re-runs, so earlier tokens are not spent again.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HITL | Human approves agent steps | इंसान की मंज़ूरी |
| Interrupt | Pause the graph | Graph को रोकना |
| Resume | Continue after human input | आगे बढ़ाना |
| Checkpointer | Saves graph state | State सहेजने वाला |
| Audit trail | Record of decisions | फैसलों का रिकॉर्ड |
| Idempotent | Safe to repeat | दोबारा चलाने पर भी सुरक्षित |

---

## ⚡ 3-Line Summary
English: HITL pauses an agent before risky steps so a human can approve, edit or reject. It needs saved state (checkpointer), a review API and fail-safe timeouts. Waiting costs no tokens; side effects must be idempotent.
Hindi: HITL में risky step से पहले agent रुकता है और इंसान approve, edit या reject करता है। इसके लिए saved state, review API और fail-safe timeout चाहिए। इंतज़ार में tokens खर्च नहीं होते; side effects idempotent रखो।

---

## ➡️ Next Topic
**310. Agent Error Handling** — retries, fallbacks and safe failure when tools or models break.
