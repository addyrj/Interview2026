---

# 329. Human in the Loop (HITL)
# हिंदी में: Human in the Loop (इंसान की मंज़ूरी के साथ AI)

---

## 🔵 Simple Definition (English)
Human in the Loop means the AI workflow pauses at a risky step and waits for a person to approve, edit or reject before continuing. In LangGraph this is built from three parts: a checkpointer (to save state), `interrupt()` (to pause), and `Command(resume=...)` (to continue). The graph can wait seconds or days.

## 🔵 सरल परिभाषा (Hindi)
Human in the Loop का मतलब है कि AI workflow किसी risky step पर रुक जाता है और आगे बढ़ने से पहले इंसान की approve, edit या reject का इंतज़ार करता है। LangGraph में तीन चीज़ें मिलकर यह बनाती हैं: checkpointer (state save), `interrupt()` (pause), और `Command(resume=...)` (आगे चलाना)। Graph सेकंड या दिनों तक इंतज़ार कर सकता है।

---

## 🔴 Problem it Solves
LLMs make confident mistakes. A wrong HS code means wrong customs duty, a fine, or a stuck shipment. A bot that sends emails, refunds money or files declarations without a check is dangerous. Fully manual work is slow, and fully automatic work is risky. HITL gives automation for the easy 90 percent and human judgement for the risky 10 percent.

## 🔴 यह क्यों बना? (Hindi)
LLM पूरे भरोसे के साथ गलती करते हैं। गलत HS code का मतलब गलत customs duty, जुर्माना या अटका हुआ shipment। जो bot बिना जाँच के email भेजे, refund करे या declaration file करे, वह खतरनाक है। पूरा manual काम धीमा है और पूरा automatic काम risky। HITL आसान 90 प्रतिशत में automation देता है और risky 10 प्रतिशत में इंसानी फ़ैसला।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Compile the graph WITH a checkpointer (required for pausing)
Step 2 → Node runs the LLM and produces a proposal (e.g. HS code + confidence)
Step 3 → Approval node calls interrupt({...payload for the human...})
Step 4 → Graph STOPS; state is saved; invoke() returns with "__interrupt__" in the result
Step 5 → Your app shows the payload in a UI / Slack / queue and waits (minutes or days)
Step 6 → Human decides: approve | edit | reject
Step 7 → App calls graph.invoke(Command(resume=decision), same thread_id)
Step 8 → The node restarts, interrupt() now RETURNS the decision, and the graph continues
Step 9 → Route on the decision: save, re-run LLM with feedback, or end
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Graph को checkpointer के साथ compile करो (pause के लिए ज़रूरी)
Step 2 → Node LLM चलाकर proposal बनाता है (जैसे HS code + confidence)
Step 3 → Approval node interrupt({...इंसान के लिए payload...}) call करता है
Step 4 → Graph रुक जाता है; state save होती है; invoke() result में "__interrupt__" के साथ लौटता है
Step 5 → App payload को UI / Slack / queue में दिखाकर इंतज़ार करता है
Step 6 → इंसान फ़ैसला करता है: approve | edit | reject
Step 7 → App वही thread_id देकर graph.invoke(Command(resume=decision)) call करता है
Step 8 → Node फिर से शुरू होता है, interrupt() अब decision RETURN करता है, graph आगे बढ़ता है
Step 9 → Decision के हिसाब से route: save, feedback के साथ LLM दोबारा, या end
```

---

## 🟡 Real World Example
**Tariff Classification System**: The LLM proposes HS code 8517.13 with 0.62 confidence. Rule: confidence below 0.8 or duty above 1 lakh rupees goes to a customs officer. The officer sees product text, proposed code and reasoning, then clicks Approve, edits the code to 8517.62, or rejects with a comment. Only then is the declaration filed.

**Amazon-style**: A refund agent auto-approves refunds under 500 rupees. Above that the graph pauses and a support lead approves in a dashboard.

## 🟡 Real Example Hindi mein
**Tariff System**: LLM 0.62 confidence के साथ HS code 8517.13 सुझाता है। नियम: confidence 0.8 से कम या duty 1 लाख रुपये से ज़्यादा हो तो customs officer के पास जाए। Officer को product text, सुझाया code और reasoning दिखती है, वह Approve करता है, code बदलकर 8517.62 करता है, या comment के साथ reject करता है। उसके बाद ही declaration file होता है।

**Amazon-style**: Refund agent 500 रुपये से कम के refunds अपने आप approve करता है। उससे ज़्यादा पर graph रुकता है और support lead dashboard में approve करता है।

---

## 💻 Code Example — Basic
```python
# Basic HITL: pause for approval, then resume (offline: the "LLM" is a fake function)
from typing import Literal, TypedDict                    # type hints

from langgraph.checkpoint.memory import MemorySaver      # needed so state survives the pause
from langgraph.graph import END, START, StateGraph      # graph API
from langgraph.types import Command, interrupt           # pause + resume primitives


class State(TypedDict, total=False):                     # total=False: keys are filled over time
    product: str                                         # input text
    hs_code: str                                         # proposed / final code
    status: str                                          # approved | rejected


def propose(state: State) -> dict:                       # step 1: "LLM" suggests a code
    return {"hs_code": "8517.13"}                        # fake proposal for a smartphone


def human_review(state: State) -> Command[Literal["finalize", "reject"]]:   # step 2: approval gate
    decision = interrupt({                               # PAUSE here; payload goes to the caller
        "question": "Approve this HS code?",             # what the human sees
        "product": state["product"],                     # context for the human
        "proposed": state["hs_code"],                    # the proposal
    })                                                   # on resume, this returns the human's value
    if decision.get("approved"):                         # human said yes
        code = decision.get("edited_code", state["hs_code"])   # human may have edited the code
        return Command(goto="finalize", update={"hs_code": code})   # go on with (maybe edited) code
    return Command(goto="reject")                        # human said no


def finalize(state: State) -> dict:                      # step 3a: file the declaration
    return {"status": "approved"}                        # mark done


def reject(state: State) -> dict:                        # step 3b: stop
    return {"status": "rejected"}                        # mark rejected


builder = StateGraph(State)                              # build graph
builder.add_node("propose", propose)                     # node 1
builder.add_node("human_review", human_review)           # node 2 (returns Command so no edge needed)
builder.add_node("finalize", finalize)                   # node 3a
builder.add_node("reject", reject)                       # node 3b
builder.add_edge(START, "propose")                       # start
builder.add_edge("propose", "human_review")              # go to the gate
builder.add_edge("finalize", END)                        # end
builder.add_edge("reject", END)                          # end
app = builder.compile(checkpointer=MemorySaver())        # checkpointer is REQUIRED for interrupt()

cfg = {"configurable": {"thread_id": "case-77"}}         # same id for pause and resume

first = app.invoke({"product": "Samsung smartphone"}, cfg)   # runs until interrupt
print(first["__interrupt__"][0].value)                   # payload shown to the human
print(app.get_state(cfg).next)                           # ('human_review',) -> waiting

final = app.invoke(Command(resume={"approved": True, "edited_code": "8517.13.00"}), cfg)  # resume
print(final["status"], final["hs_code"])                 # approved 8517.13.00
```

## 💻 Code Example — Advanced
```python
# Production style: confidence gate, async, validation, timeout/escalation, type hints
import asyncio                                           # async runtime
import logging                                           # logs
from typing import Any, Literal, TypedDict               # type hints

from langgraph.checkpoint.memory import MemorySaver      # swap for Postgres/Redis in production
from langgraph.graph import END, START, StateGraph      # graph API
from langgraph.types import Command, interrupt           # HITL primitives
from pydantic import BaseModel, Field, ValidationError   # validate human input

logger = logging.getLogger("tariff.hitl")                # logger
CONF_THRESHOLD: float = 0.80                             # below this a human must review


class Decision(BaseModel):                               # shape of the human's answer
    action: Literal["approve", "edit", "reject"]         # allowed actions only
    code: str | None = Field(default=None, pattern=r"^\d{4}\.\d{2}(\.\d{2})?$")  # HS format
    comment: str = ""                                    # optional note


class State(TypedDict, total=False):                     # graph state
    product: str                                         # product text
    hs_code: str                                         # current code
    confidence: float                                    # model confidence
    status: str                                          # final status
    audit: list[dict[str, Any]]                          # who decided what


async def classify(state: State) -> dict[str, Any]:      # async LLM node
    await asyncio.sleep(0)                               # placeholder for `await llm.ainvoke(...)`
    low = "unknown" in state["product"].lower()          # fake: weird products have low confidence
    return {"hs_code": "8517.13", "confidence": 0.55 if low else 0.95}   # fake output


def route_by_confidence(state: State) -> Literal["human_review", "finalize"]:   # conditional edge
    return "human_review" if state["confidence"] < CONF_THRESHOLD else "finalize"   # gate logic


def human_review(state: State) -> Command[Literal["finalize", "classify", "__end__"]]:
    raw = interrupt({                                    # pause for a person
        "product": state["product"], "proposed": state["hs_code"],
        "confidence": state["confidence"], "options": ["approve", "edit", "reject"],
    })                                                   # NOTE: code before interrupt re-runs on resume
    try:                                                 # never trust human/UI input blindly
        d = Decision.model_validate(raw)                 # validate with pydantic v2
    except ValidationError as exc:                       # bad payload from the UI
        logger.warning("invalid decision: %s", exc)      # log it
        return Command(goto="__end__", update={"status": "invalid_decision"})   # fail safe
    audit = [{"action": d.action, "comment": d.comment}]  # audit trail entry
    if d.action == "approve":                            # accept as is
        return Command(goto="finalize", update={"audit": audit})
    if d.action == "edit" and d.code:                    # human fixes the code
        return Command(goto="finalize", update={"hs_code": d.code, "audit": audit})
    return Command(goto="__end__", update={"status": "rejected", "audit": audit})   # reject


def finalize(state: State) -> dict[str, Any]:            # file declaration
    return {"status": "filed"}                           # mark filed


def build():                                             # create the app
    b = StateGraph(State)                                # builder
    b.add_node("classify", classify)                     # node
    b.add_node("human_review", human_review)             # node
    b.add_node("finalize", finalize)                     # node
    b.add_edge(START, "classify")                        # start
    b.add_conditional_edges("classify", route_by_confidence)   # auto vs human
    b.add_edge("finalize", END)                          # end
    return b.compile(checkpointer=MemorySaver())         # compile with saver


async def main() -> None:                                # demo
    app = build()                                        # graph
    cfg = {"configurable": {"thread_id": "case-9"}}      # thread
    out = await app.ainvoke({"product": "unknown gadget"}, cfg)   # low confidence -> pauses
    print("paused:", "__interrupt__" in out)             # True
    out = await app.ainvoke(Command(resume={"action": "edit", "code": "8543.70", "comment": "fixed"}), cfg)
    print(out["status"], out["hs_code"], out["audit"])   # filed 8543.70 [...]


if __name__ == "__main__":                               # entry
    asyncio.run(main())                                  # run
```

---

## 🟠 FastAPI Integration
Two endpoints: one starts a case and returns either the final result or a "needs review" payload; the other receives the human decision and resumes. The `thread_id` is the case id. In production use a shared checkpointer (Postgres/Redis) so any pod can resume.

```python
# FastAPI + HITL: /classify starts, /cases/{id}/decision resumes
import uuid                                                       # case ids
from typing import Any, Literal, TypedDict                        # type hints

from fastapi import FastAPI, HTTPException                        # web framework
from langgraph.checkpoint.memory import MemorySaver               # use a shared saver in production
from langgraph.graph import END, START, StateGraph               # graph API
from langgraph.types import Command, interrupt                    # HITL
from pydantic import BaseModel                                    # models


class S(TypedDict, total=False):                                  # state
    product: str                                                  # input
    hs_code: str                                                  # code
    status: str                                                   # status


def propose(s: S) -> dict: return {"hs_code": "8517.13"}          # fake LLM
def gate(s: S) -> dict:                                           # approval node
    ok = interrupt({"proposed": s["hs_code"], "product": s["product"]})   # pause
    return {"status": "approved" if ok else "rejected"}           # resume value is a bool here


b = StateGraph(S)                                                 # build graph
b.add_node("propose", propose)                                    # node
b.add_node("gate", gate)                                          # node
b.add_edge(START, "propose")                                      # start
b.add_edge("propose", "gate")                                     # next
b.add_edge("gate", END)                                           # end
graph = b.compile(checkpointer=MemorySaver())                     # compile once

app = FastAPI(title="Tariff HITL")                                # API


class ClassifyIn(BaseModel):                                      # body
    product: str                                                  # text


class DecisionIn(BaseModel):                                      # human decision body
    approved: bool                                                # yes/no


@app.post("/classify")                                            # start a case
async def classify(body: ClassifyIn) -> dict[str, Any]:           # handler
    case_id = str(uuid.uuid4())                                   # new case id = thread id
    cfg = {"configurable": {"thread_id": case_id}}                # config
    out = await graph.ainvoke({"product": body.product}, cfg)     # run until interrupt
    if "__interrupt__" in out:                                    # paused for review
        return {"case_id": case_id, "state": "needs_review",
                "review": out["__interrupt__"][0].value}          # payload for the UI
    return {"case_id": case_id, "state": "done", "result": out}   # no review needed


@app.post("/cases/{case_id}/decision")                            # human decision
async def decide(case_id: str, body: DecisionIn) -> dict[str, Any]:   # handler
    cfg = {"configurable": {"thread_id": case_id}}                # same thread
    snap = await graph.aget_state(cfg)                            # check the case is really waiting
    if not snap.next:                                             # nothing pending
        raise HTTPException(409, "case is not waiting for review")   # conflict
    out = await graph.ainvoke(Command(resume=body.approved), cfg)   # resume
    return {"case_id": case_id, "result": out}                    # final state
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph offers two ways to pause. (1) Dynamic `interrupt()` inside a node, which is the recommended way because the payload and resume value can be any JSON. (2) Static breakpoints `compile(interrupt_before=["node"], interrupt_after=[...])`, handy for debugging. Tool calls in a ReAct agent can also be wrapped so that dangerous tools (send email, file declaration) call `interrupt()` before executing.

```python
# Guard a dangerous tool with HITL
from langchain_core.tools import tool                       # tool decorator
from langgraph.types import interrupt                       # pause


@tool                                                       # exposes the function to the LLM
def file_declaration(hs_code: str, value_inr: float) -> str:   # dangerous action
    """File a customs declaration."""                       # docstring is the tool description
    ok = interrupt({"action": "file_declaration", "hs_code": hs_code, "value_inr": value_inr})
    if ok is not True:                                      # human did not approve
        return "Cancelled by officer."                      # tell the agent
    return f"Filed declaration for {hs_code}"               # real work would be here
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No checkpointer
✅ Correct: HITL needs saved state, otherwise nothing can be resumed.

```python
# Wrong
app = builder.compile()                                     # interrupt() raises an error

# Right
app = builder.compile(checkpointer=MemorySaver())
```

❌ Mistake 2: Side effects before `interrupt()` in the same node
✅ Correct: the node is re-executed from the top on resume, so anything before `interrupt()` runs twice. Keep it idempotent or put side effects after.

```python
# Wrong — email is sent twice (before pause and after resume)
def node(s):
    send_email(s["to"])
    ok = interrupt("approve?")

# Right — approve first, act after
def node(s):
    ok = interrupt("approve?")
    if ok:
        send_email(s["to"])
```

❌ Mistake 3: Resuming with a different `thread_id` or invoking with fresh input
✅ Correct: pass `Command(resume=...)` and the SAME thread_id. A new input restarts the graph.

---

## 🧠 Tricky Interview Question

**Q**: "An officer approves a case two days later, but the declaration is filed twice. The graph used `interrupt()` and a Postgres checkpointer. Why?"

**Answer**: Two common causes. First, the node re-runs from its start on resume, so a side effect placed before `interrupt()` runs again. Second, the UI sent the approval twice (double click, retry), and there was no check that the thread was still waiting. Fix: put side effects after `interrupt()` in a separate node, make them idempotent with a unique key (case id + action), check `get_state(cfg).next` before resuming (return 409 if not waiting), and store a decision id for deduplication.

---

## ⚫ Interview Questions + Answers

Q1: What is Human in the Loop? (Easy)
A1: A design where an AI workflow pauses at sensitive steps for a person to approve, edit or reject. It improves safety and trust.

Q2: What is needed in LangGraph to pause a run? (Easy)
A2: A checkpointer, a `thread_id` in config, and `interrupt()` (or `interrupt_before` at compile time). Resume with `Command(resume=value)`.

Q3: `interrupt()` versus `interrupt_before`? (Medium)
A3: `interrupt()` is called inside a node, can send a custom payload, and returns the human's value on resume. `interrupt_before=["node"]` is a static breakpoint that stops before a named node and resumes with `invoke(None, cfg)`. It is simpler and good for debugging, but less flexible.

Q4: How do you let a human edit the state instead of only approving? (Medium)
A4: Return the edited value through `Command(resume=...)` and update state in the node, or call `graph.update_state(cfg, {...})` while paused, then resume with `invoke(None, cfg)`. `update_state` can also act as a specific node (`as_node`).

Q5: How would you design HITL for 10,000 cases per day with 20 reviewers? (Hard)
A5: Automate high-confidence cases. Store paused cases in a durable checkpointer, keep a review queue table (case id, priority, SLA, assignee, interrupt payload), and show it in a UI. Add timeouts and escalation jobs (if no decision in 24 hours, escalate). Use idempotent resume with decision ids, role-based access and an audit log. Feed rejected and edited cases into an evaluation set and fine-tuning or prompt improvement so the human load decreases over time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Actions are irreversible or costly (filings, payments, emails)
- Confidence is low or legal responsibility exists
- You need an audit trail and training data from human corrections

❌ Avoid when:
- The task is low risk and high volume (use sampling and monitoring)
- Real-time latency is critical and no human is available
- You have no process to handle the pending queue (cases will pile up)

---

## 📊 Visual Diagram
```
 user input
    │
    ▼
 [classify (LLM)] ──conf >= 0.8──────────────┐
    │ conf < 0.8                              │
    ▼                                         ▼
 [human_review]  interrupt(payload)       [finalize] ─► END
    │   state saved in checkpointer           ▲
    │   ... minutes / days ...                │
    │                                         │
 Human UI  ── Command(resume=decision) ───────┘
   approve / edit / reject
```

---

## 💰 Cost Impact
Waiting costs zero tokens: the graph is just a row in the checkpointer, no LLM or compute is running. The cost is human time (a reviewer at 300 rupees/hour handling 30 cases/hour is 10 rupees per case) and extra tokens if you re-run the LLM after a rejection. Optimise: send only low-confidence cases to humans (a threshold turns 100 percent review into 10 percent), show humans a short payload, resume without re-running earlier nodes (checkpoint does this), and use human edits as few-shot examples to improve accuracy.

Token example: a classify call with 800 input and 150 output tokens on gpt-4o-mini costs about $0.00021. The review itself adds no tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HITL | Human approves/edits during the workflow | Workflow में इंसान की मंज़ूरी |
| interrupt() | Pauses a node and returns a payload | Node को रोकने वाला function |
| Command(resume=) | Continues a paused graph with a value | रुके graph को आगे चलाना |
| Checkpointer | Saves state so pause is possible | State save करने वाला |
| Breakpoint | Static pause before/after a node | Node से पहले/बाद में रुकना |
| Idempotent | Same action twice gives same effect | दो बार चलाने पर भी एक जैसा असर |
| Audit trail | Record of who decided what | किसने क्या फ़ैसला लिया उसका record |

---

## ⚡ 3-Line Summary
English: HITL pauses a LangGraph run for human approval using a checkpointer, `interrupt()` and `Command(resume=...)`. Only risky or low-confidence cases need a person, and waiting costs no tokens. Keep side effects after the interrupt and make resume idempotent.
Hindi: HITL में checkpointer, `interrupt()` और `Command(resume=...)` से LangGraph इंसान की मंज़ूरी के लिए रुकता है। सिर्फ़ risky या कम confidence वाले cases में इंसान चाहिए, और इंतज़ार में tokens खर्च नहीं होते। Side effects interrupt के बाद रखो और resume को idempotent बनाओ।

---

## ➡️ Next Topic
**330. Interrupt + Resume** — a deeper look at the mechanics: multiple interrupts, `interrupt_before`, `update_state`, and re-execution rules.
