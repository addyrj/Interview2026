---

# 114. Flow Conditional Branching
# हिंदी में: Flow में शर्त के आधार पर रास्ता चुनना (Branching)
# Framework: CrewAI
# Already Known: No

> Verified against crewai 1.15.41 (offline, fake LLM). `@router`, `or_`, `and_` imported and run.

---

## 🔵 Simple Definition (2-3 lines)
Conditional branching lets a Flow choose its next step at run time. A `@router` method returns a string label (like `"auto"` or `"review"`), and `@listen("auto")` / `@listen("review")` methods run only for the matching label. `or_()` and `and_()` combine several triggers.

## 🔵 सरल परिभाषा (Hindi)
Conditional branching से Flow run के समय अगला step चुनता है। `@router` method एक string label (जैसे `"auto"` या `"review"`) लौटाता है, और `@listen("auto")` / `@listen("review")` वाले methods सिर्फ़ मेल खाने वाले label पर चलते हैं। `or_()` और `and_()` कई triggers को जोड़ते हैं।

---

## 🔴 Problem it Solves
Real pipelines are not straight lines. A low-confidence HS code must go to a human; a high-confidence one can be auto-approved. Without routing you either send everything to review (slow, costly) or approve everything (risky). Writing nested `if/else` around crews in plain Python loses event tracking and visualisation.

## 🔴 यह क्यों बना? (Hindi)
असली pipelines सीधी रेखा नहीं होतीं। कम confidence वाला HS code इंसान के पास जाना चाहिए; ज़्यादा confidence वाला अपने-आप approve हो सकता है। Routing के बिना या तो सब कुछ review में जाएगा (धीमा, महँगा) या सब approve होगा (जोखिम)। Crew के आसपास nested `if/else` लिखने से event tracking और visualisation खो जाते हैं।

---

## 🟢 How it Works

```
Step 1 → @start method produces data (e.g. crew result + confidence)
Step 2 → @router(prev) method inspects self.state, returns a label string
Step 3 → Flow finds every method decorated @listen("<label>") and runs them
Step 4 → Other branches are simply never executed (no tokens spent there)
Step 5 → or_(a, b): run when EITHER finishes; and_(a, b): when BOTH finished
Step 6 → A final @listen(or_(branch_a, branch_b)) merges the paths
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → @start method डेटा बनाता है (जैसे crew result + confidence)
Step 2 → @router(prev) method self.state देखकर एक label string लौटाता है
Step 3 → Flow हर उस method को चलाता है जिस पर @listen("<label>") लगा है
Step 4 → बाकी branches चलते ही नहीं (वहाँ tokens खर्च नहीं होते)
Step 5 → or_(a, b): कोई एक पूरा हो तो चले; and_(a, b): दोनों पूरे हों तब
Step 6 → आख़िर में @listen(or_(branch_a, branch_b)) से रास्ते जुड़ते हैं
```

---

## 🟡 Real World Example
**Tariff Agent**: after classification the Flow computes `confidence`. `>= 0.8` -> `"auto"` path: save HS code and price. `< 0.8` -> `"review"` path: push to a human-review queue. Both paths end in one `finish` step that writes an audit log.

## 🟡 Real Example Hindi mein
**Tariff Agent**: classification के बाद Flow `confidence` निकालता है। `>= 0.8` -> `"auto"` रास्ता: HS code save करो और price निकालो। `< 0.8` -> `"review"` रास्ता: इंसान की review queue में डालो। दोनों रास्ते एक `finish` step पर मिलते हैं जो audit log लिखता है।

---

## 💻 Code Example — Basic
```python
# Run directly: python branching_basic.py (offline, fake LLM)
import os                                              # env switches for demo
os.environ["OTEL_SDK_DISABLED"] = "true"               # no telemetry export
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # no telemetry

from pydantic import BaseModel                         # typed state
from crewai import Flow                                # base Flow class
from crewai.flow.flow import listen, start, router, or_  # branching decorators


class S(BaseModel):                                    # shared state
    hs_code: str = ""                                  # classification result
    confidence: float = 0.0                            # model confidence 0..1


class BranchFlow(Flow[S]):
    @start()                                           # first step
    def classify(self) -> str:
        self.state.hs_code = "6109.10"                 # pretend a crew produced this
        # confidence is injected through inputs in this demo
        return self.state.hs_code

    @router(classify)                                  # decides the path after classify
    def gate(self) -> str:
        return "auto" if self.state.confidence >= 0.8 else "review"  # label string

    @listen("auto")                                    # runs only when label == "auto"
    def auto_path(self) -> str:
        return f"AUTO-APPROVED {self.state.hs_code}"

    @listen("review")                                  # runs only when label == "review"
    def review_path(self) -> str:
        return f"SENT-TO-HUMAN {self.state.hs_code}"

    @listen(or_(auto_path, review_path))               # merge: whichever branch ran
    def finish(self, previous: str) -> str:            # receives the branch's return value
        return f"audit: {previous}"


print(BranchFlow().kickoff(inputs={"confidence": 0.9}))   # -> audit: AUTO-APPROVED 6109.10
print(BranchFlow().kickoff(inputs={"confidence": 0.3}))   # -> audit: SENT-TO-HUMAN 6109.10
```
Ran offline: both lines print as shown. No LLM tokens here (the branch logic is pure code, which is the point).

## 💻 Code Example — Advanced
```python
# Production-style: crew confidence -> router -> async branches -> FastAPI, with error handling
import asyncio                                         # async + timeout
import os                                              # env switches
os.environ["OTEL_SDK_DISABLED"] = "true"               # demo only
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"        # demo only
from typing import Any                                 # type hints
from fastapi import FastAPI, HTTPException             # API layer
from fastapi.testclient import TestClient              # offline test client
from pydantic import BaseModel                         # models
from crewai import Agent, Task, Crew, BaseLLM, Flow   # CrewAI core
from crewai.flow.flow import listen, start, router, or_, and_  # decorators


class FakeLLM(BaseLLM):                                # offline model
    def __init__(self, text: str) -> None:
        super().__init__(model="fake"); self._t = text
    def call(self, messages: Any, tools: Any = None, callbacks: Any = None,
             available_functions: Any = None, from_task: Any = None,
             from_agent: Any = None, response_model: Any = None, **kw: Any) -> str:
        return self._t
    def supports_function_calling(self) -> bool:
        return False


class S(BaseModel):                                    # state
    item: str = ""
    hs_code: str = ""
    confidence: float = 0.0
    decision: str = ""
    saved: bool = False
    audited: bool = False


class TariffFlow(Flow[S]):
    @start()
    def classify(self) -> str:
        # In production the answer text comes from a real LLM; here it is canned.
        reply = "Thought: ok\nFinal Answer: 6109.10" if "shirt" in self.state.item else "Thought: ok\nFinal Answer: UNKNOWN"
        agent = Agent(role="Analyst", goal="HS", backstory="expert",
                      llm=FakeLLM(reply), allow_delegation=False)
        task = Task(description="Classify {item}", expected_output="HS code", agent=agent)
        out = Crew(agents=[agent], tasks=[task], tracing=False).kickoff(inputs={"item": self.state.item})
        self.state.hs_code = out.raw.strip()           # keep text
        # rule-based confidence: a real system would use a logprob/validator/second model
        self.state.confidence = 0.9 if self.state.hs_code[:4].isdigit() else 0.2
        return self.state.hs_code

    @router(classify)
    def gate(self) -> str:
        return "auto" if self.state.confidence >= 0.8 else "review"

    @listen("auto")
    async def save_result(self) -> None:              # async step: pretend DB write
        await asyncio.sleep(0)                         # yield control
        self.state.saved = True
        self.state.decision = "auto"

    @listen("review")
    async def queue_review(self) -> None:
        await asyncio.sleep(0)
        self.state.decision = "review"

    @listen(or_(save_result, queue_review))            # either branch finished
    async def audit(self) -> None:
        self.state.audited = True

    @listen(and_(audit, classify))                     # waits for BOTH to be done
    def payload(self) -> dict[str, Any]:
        return {"hs": self.state.hs_code, "decision": self.state.decision,
                "saved": self.state.saved, "audited": self.state.audited}


app = FastAPI()


class Req(BaseModel):
    item: str


@app.post("/tariff")
async def tariff(req: Req) -> dict[str, Any]:
    try:
        return await asyncio.wait_for(TariffFlow().kickoff_async(inputs={"item": req.item}), 60)
    except asyncio.TimeoutError:
        raise HTTPException(504, "timeout")
    except Exception as e:                             # never leak stack traces
        raise HTTPException(502, f"flow failed: {type(e).__name__}")


with TestClient(app) as c:                             # offline smoke test
    print(c.post("/tariff", json={"item": "cotton shirt"}).json())
    print(c.post("/tariff", json={"item": "mystery box"}).json())
```
Ran offline: shirt -> `decision: auto, saved: True`; mystery box -> `decision: review, saved: False`. Token use: zero extra tokens for routing; only the crew step costs tokens.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Branch primitive | `add_conditional_edges(fn)` | `@router` returning a label | Python `if` / handoff choice | `GraphFlow` conditions / selector |
| Merge of branches | Edge to common node | `@listen(or_(...))` | Manual | Manual |
| Wait for all | Fan-in with reducer | `and_(...)` | `asyncio.gather` | Graph dependencies |
| Visualise | `get_graph().draw_*` | `flow.plot()` | None built in | Studio UI |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Router returns a label with no `@listen("label")` method (typo like `"Auto"` vs `"auto"`).
✅ Correct: Define label constants and reuse them; unit test every label path.

❌ Mistake 2: Using `and_` when only one branch will ever run, so the final step never fires.
✅ Correct: Use `or_` to merge exclusive branches; `and_` only for parallel branches that all execute.

❌ Mistake 3: Letting the LLM output decide routing as free text.
✅ Correct: Parse into a pydantic/enum value, validate, then route on that.

---

## 🧠 Tricky Interview Question
Why might a `@listen(and_(a, b))` step never run, even though no error was raised?

Answer: `and_` waits until both `a` and `b` have completed. If `a` sits on a router branch that was not chosen, it never completes, so the join does not fire, and no exception is raised (verified on crewai 1.15.41: a flow with `@listen(and_(a, b))` where only branch `a` was routed returned `a`'s value and never ran the join). Fix: join exclusive branch outputs with `or_`, or restructure so both parents always run.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `@router` return?
A1: A string label that selects which `@listen("label")` methods run next.

Q2: [Medium] Difference between `or_` and `and_`?
A2: `or_` triggers when any listed method completes; `and_` triggers only after all of them complete.

Q3: [Hard] How do you avoid branching on unreliable LLM confidence numbers?
A3: Do not trust self-reported confidence. Use validators (code table check), agreement between two runs, or a separate judge, then route on that measurable signal.

Q4: [Hard] How do you test every path?
A4: Inject inputs that force each label (`kickoff(inputs={...})`), assert on `flow.state`, and keep the router a pure function of state so it is trivially testable.

Q5: [System Design] Design human-in-the-loop for low-confidence customs decisions.
A5: Router sends `"review"` items to a queue (DB table + UI); reviewer decision re-enters the flow (CrewAI also offers `human_feedback` / resume APIs in `crewai.flow`); SLA timers escalate; approved decisions feed a regression set.

---

## 💰 Cost Impact
- Routing itself costs 0 tokens if it is code. Only branch steps that call a Crew cost tokens.
- Formula: expected cost = P(auto) x cost_auto + P(review) x cost_review.
- Tip: put cheap deterministic checks first so expensive review-crew branches run rarely. Token figures depend on your model; measure with `out.token_usage`.

---

## 🔷 When to Use
✅ Use when:
- Different outcomes need different handling (auto vs manual)
- You want to skip expensive steps for easy cases
- You need visible, testable decision points

❌ Avoid when:
- The path is always the same (use `@listen` chain)
- Decisions are fuzzy and better handled inside one agent prompt

---

## 📊 Visual Diagram
```
 @start classify
        |
        v
   @router gate ---- confidence >= 0.8 ----> @listen("auto")  save_result
        |                                           |
        +------- confidence < 0.8 ----> @listen("review") queue_review
                                                    |
                                  or_(save_result, queue_review)
                                                    v
                                                 audit -> payload
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Router | Returns a label to choose a path | रास्ता चुनने वाला label लौटाता है |
| Label | String matched by `@listen("...")` | मिलान वाली string |
| `or_` | Any trigger fires | कोई भी trigger |
| `and_` | All triggers must fire | सभी triggers ज़रूरी |
| Confidence | How sure the result is | नतीजे पर भरोसा |

---

## ⚡ 3-Line Summary
English: `@router` returns a label; `@listen("label")` runs the matching branch. Merge with `or_`, join parallel work with `and_`. Route on measurable signals, not LLM self-confidence.
Hindi: `@router` label लौटाता है; `@listen("label")` सही branch चलाता है। `or_` से merge करो, parallel काम `and_` से जोड़ो। LLM के अपने भरोसे पर नहीं, नापे जा सकने वाले signal पर route करो।

---

## ➡️ Next Topic
**115. Flow Error Handling** — branches are only useful if failures inside them are caught, retried and reported cleanly.

---
