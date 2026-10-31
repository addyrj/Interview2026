---

# 422. Feedback in LangSmith
# हिंदी में: LangSmith में Feedback

---

## 🔵 Simple Definition (English)
Feedback is a score or comment attached to a run: a user thumbs-up/down, a human reviewer's grade, or an automatic evaluator result. Each feedback has a key (like `correctness`), a score or value, and optional comment. It tells you which production answers were good or bad.

## 🔵 सरल परिभाषा (Hindi)
Feedback किसी run से जुड़ा score या comment है: user का thumbs-up/down, human reviewer का grade, या automatic evaluator का result। हर feedback में एक key (जैसे `correctness`), score या value, और optional comment होता है। इससे पता चलता है कि production के कौन से answers अच्छे या बुरे थे।

---

## 🔴 Problem it Solves
- Traces tell you what happened, not whether it was good.
- Without a signal, you cannot find bad answers among millions of requests.
- Quality opinions live in Slack and spreadsheets, disconnected from the exact trace.

## 🔴 यह क्यों बना? (Hindi)
- Traces बताते हैं क्या हुआ, यह नहीं कि अच्छा था या नहीं।
- Signal के बिना लाखों requests में खराब answers ढूँढना असंभव है।
- Quality की राय Slack और spreadsheets में रहती है, सही trace से जुड़ी नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App returns the answer + the run_id of the trace to the client
Step 2 → User clicks 👍/👎 (or a reviewer grades, or an evaluator runs)
Step 3 → Client sends feedback with run_id to your backend
Step 4 → Backend calls client.create_feedback(run_id, key, score, comment)
Step 5 → Feedback appears on the run and in project stats
Step 6 → Filter runs by feedback (e.g. correctness = 0)
Step 7 → Send negatives to annotation queue or dataset; fix and re-evaluate
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → App answer के साथ trace का run_id client को लौटाता है
Step 2 → User 👍/👎 दबाता है (या reviewer grade करता है, या evaluator चलता है)
Step 3 → Client run_id के साथ feedback आपके backend को भेजता है
Step 4 → Backend client.create_feedback(run_id, key, score, comment) बुलाता है
Step 5 → Feedback run पर और project stats में दिखता है
Step 6 → Feedback से runs filter करो (जैसे correctness = 0)
Step 7 → Negatives को annotation queue या dataset में भेजो; ठीक करो; दोबारा evaluate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The UI shows the HS code with "Correct / Wrong" buttons. When a customs officer clicks Wrong and types the right code, the backend logs `key="correctness", score=0, comment="should be 8507.60"`. Weekly, the team filters `correctness=0` runs (about 3% of traffic), adds them to dataset `tariff-failures` with corrected outputs, and re-runs evaluation. Accuracy on that hard set goes from 52% to 74% after a prompt fix.

**Zomato AI**: "Was this recommendation helpful?" thumbs are stored as `helpfulness`; an LLM judge adds `relevance` automatically on 5% sampled traces.

## 🟡 Real Example Hindi mein
**Tariff System**: UI में HS code के साथ "सही / गलत" buttons हैं। Customs officer "गलत" दबाकर सही code लिखता है तो backend `key="correctness", score=0, comment="should be 8507.60"` log करता है। हर हफ़्ते team `correctness=0` runs (लगभग 3% traffic) filter करती है, सही outputs के साथ dataset `tariff-failures` में डालती है और evaluation दोबारा चलाती है। Prompt fix के बाद इस कठिन set पर accuracy 52% से 74% हुई।

**Zomato AI**: "क्या यह suggestion काम का था?" के thumbs `helpfulness` में जाते हैं; LLM judge 5% sampled traces पर `relevance` अपने-आप जोड़ता है।

---

## 💻 Code Example — Basic
```python
# Basic: a feedback store keyed by run_id (pure Python, offline)
from dataclasses import dataclass, field                      # structures
from collections import defaultdict                           # grouping

@dataclass
class Feedback:                                               # one feedback entry
    run_id: str                                               # which run it belongs to
    key: str                                                  # metric name, e.g. correctness
    score: float                                              # 0..1
    comment: str = ""                                         # optional text

STORE: dict[str, list[Feedback]] = defaultdict(list)          # run_id -> feedback list

def add_feedback(run_id: str, key: str, score: float, comment: str = "") -> None:
    if not 0.0 <= score <= 1.0:                               # validate range
        raise ValueError("score must be between 0 and 1")
    STORE[run_id].append(Feedback(run_id, key, score, comment))  # save

add_feedback("run-1", "correctness", 1.0)                     # thumbs up
add_feedback("run-2", "correctness", 0.0, "should be 8507.60")  # thumbs down with note
bad = [rid for rid, fbs in STORE.items() if any(f.key == "correctness" and f.score == 0 for f in fbs)]
print("runs needing review:", bad)                            # ['run-2']
```

## 💻 Code Example — Advanced
```python
# Real LangSmith feedback: user feedback + automatic evaluator, async, error-safe
# pip install langsmith
import asyncio                                                # async runtime
import logging                                                # logs
from uuid import UUID                                         # run ids are UUIDs
from langsmith import Client                                  # SDK client

log = logging.getLogger("feedback")                           # logger
_client: Client | None = None                                 # lazy singleton

def get_client() -> Client:
    global _client                                            # reuse one client
    if _client is None:
        _client = Client()                                    # needs LANGSMITH_API_KEY
    return _client

def send_feedback_sync(run_id: str, key: str, score: float, comment: str | None = None) -> bool:
    try:
        UUID(run_id)                                          # validate id format early
        get_client().create_feedback(
            run_id=run_id,                                    # target run
            key=key,                                          # metric name
            score=score,                                      # numeric score
            comment=comment,                                  # optional explanation
            source_info={"origin": "tariff-ui"},              # where it came from
        )
        return True
    except Exception as exc:                                  # never break the user's request
        log.warning("feedback failed: %s", type(exc).__name__)
        return False

async def send_feedback(run_id: str, key: str, score: float, comment: str | None = None) -> bool:
    return await asyncio.to_thread(send_feedback_sync, run_id, key, score, comment)  # keep loop free

def code_format_check(answer: str) -> float:                  # automatic evaluator: valid HS format?
    digits = answer.replace(".", "")
    return 1.0 if digits.isdigit() and len(digits) in (6, 8, 10) else 0.0

async def auto_feedback(run_id: str, answer: str) -> None:
    await send_feedback(run_id, "valid_format", code_format_check(answer), "rule-based check")

if __name__ == "__main__":
    print(code_format_check("8507.60"), code_format_check("abc"))   # 1.0 0.0 (runs offline)
```

---

## 🟠 FastAPI Integration
Two routes: `/classify` returns the answer plus `run_id`; `/feedback` accepts thumbs from the UI. Feedback is sent in a background task, so the user gets an instant response.

```python
from fastapi import BackgroundTasks, FastAPI                  # framework + background tasks
from pydantic import BaseModel, Field                         # validation
from langsmith import traceable                               # tracing
from langsmith.run_helpers import get_current_run_tree        # run id

app = FastAPI()                                               # app

@traceable(name="classify_api")
async def classify(product: str) -> dict[str, str]:
    rt = get_current_run_tree()                               # current run
    return {"hs_code": "8507.60", "run_id": str(rt.id) if rt else ""}

class FeedbackIn(BaseModel):                                  # request body
    run_id: str
    correct: bool
    comment: str | None = Field(default=None, max_length=500)

@app.get("/classify")
async def classify_route(product: str) -> dict[str, str]:
    return await classify(product)                            # includes run_id for the UI

@app.post("/feedback", status_code=202)
async def feedback(fb: FeedbackIn, bg: BackgroundTasks) -> dict[str, str]:
    bg.add_task(send_feedback, fb.run_id, "correctness", 1.0 if fb.correct else 0.0, fb.comment)
    return {"status": "accepted"}
```

---

## 🔗 LangChain / LangGraph Connection
To get the run id of a LangChain call, use `collect_runs` or a callback. LangSmith evaluators in `evaluate()` also write feedback automatically (one key per evaluator).

```python
from langchain_core.tracers.context import collect_runs       # capture runs in a block
from langchain_core.runnables import RunnableLambda           # simple chain

chain = RunnableLambda(lambda x: "8507.60")                   # stand-in chain
with collect_runs() as cb:                                    # collect runs created inside
    answer = chain.invoke("power bank")                       # run the chain
    run_id = cb.traced_runs[0].id                             # id of the root run
print(answer, run_id)                                         # later: create_feedback(run_id, ...)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not returning the run id to the client, so feedback cannot be linked.
✅ Correct: return `run_id` (or a header) with each answer.

```python
# Wrong
return {"hs_code": code}
# Right
return {"hs_code": code, "run_id": run_id}
```

❌ Mistake 2: Blocking the response on feedback submission, or failing the user request if LangSmith is down.
✅ Correct: background task + try/except.

```python
# Wrong
client.create_feedback(run_id, "correctness", score=0)   # raises -> 500 for the user
# Right
bg.add_task(send_feedback, run_id, "correctness", 0.0)   # safe, async
```

---

## 🧠 Tricky Interview Question
**Q**: "Thumbs-up rate is 92%, yet the business says quality is poor. Why can feedback mislead?"

**Answer**: User feedback is biased: only a tiny, self-selected fraction responds; people rarely click on wrong answers they cannot recognise as wrong (HS codes look plausible); and politeness inflates positives. Combine with expert review on a random sample, automatic evaluators, and outcome signals (e.g. customs rejection of a declaration). Use feedback to *find* candidates, not as the only measure.

---

## ⚫ Interview Questions + Answers

Q1: What is feedback in LangSmith? (Easy)
A1: A score/comment with a key attached to a run, from users, humans or automatic evaluators.

Q2: Name three sources of feedback. (Easy)
A2: End-user thumbs, human annotators (annotation queues), and programmatic evaluators or LLM judges.

Q3: How do you connect UI feedback to the right trace? (Medium)
A3: Return the run id with the answer; the UI posts it back; the backend calls `create_feedback(run_id=...)`.

Q4: How do you use feedback to improve the system? (Medium)
A4: Filter negative runs, review root causes, add them to a dataset with corrected answers, change prompt/retrieval, and re-run the evaluation to confirm improvement without regressions.

Q5: How do you design a feedback strategy for a high-traffic app? (Hard)
A5: Collect cheap implicit signals (copy, retry, edit), explicit thumbs for a fraction, auto LLM-judge on sampled traces, expert review on random plus low-confidence samples. Use consistent keys, normalise scores to 0-1, store a reviewer id, handle duplicate submissions, protect against spam, and monitor feedback trends per prompt version with alerts on drops.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have real users or reviewers
- You want automatic quality scoring on production traffic

❌ Avoid when:
- Treating thumbs as ground truth
- Collecting feedback with no plan to act on it

---

## 📊 Visual Diagram
```
 User ─► answer + run_id ─► [👍 👎 + comment]
                                   │
                                   ▼
                    POST /feedback → create_feedback(run_id, key, score)
                                   │
        ┌──────────────────────────┼───────────────────────────┐
        ▼                          ▼                           ▼
  filter score=0         annotation queue            auto evaluators
        └────────► dataset (corrected outputs) ◄────────────────┘
                              │
                     evaluate → fix → ship
```

---

## 💰 Cost Impact
- Manual and thumbs feedback use no tokens. An LLM-judge evaluator costs tokens: judging 5% of 100K daily traces at 1,200 tokens each is 6M tokens/day, about $1-$4 per day on a small model.
- Optimise: judge a sample, use rule-based checks first, binary outputs with tiny `max_tokens`, cache by answer hash, and run judges asynchronously offline rather than inline.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Feedback | Score/comment on a run | Run पर score/comment |
| Feedback key | Name of the metric | Metric का नाम |
| Annotation queue | Runs waiting for human review | Human review की कतार |
| Evaluator | Code/LLM that scores output | Output को score करने वाला code/LLM |
| Implicit signal | Behaviour like copy or retry | Behaviour से मिला संकेत |
| Ground truth | Verified correct answer | जाँचा हुआ सही answer |

---

## ⚡ 3-Line Summary
English: Feedback attaches scores and comments to runs from users, reviewers or evaluators. Return the run id with each answer and post feedback in the background without blocking users. Use negative feedback to build datasets and verify fixes, but do not trust thumbs alone.
Hindi: Feedback users, reviewers या evaluators से runs पर score और comment जोड़ता है। हर answer के साथ run id लौटाओ और feedback background में भेजो ताकि user रुके नहीं। Negative feedback से dataset बनाओ और fixes जाँचो, पर सिर्फ़ thumbs पर भरोसा मत करो।

---

## ➡️ Next Topic
**423. Datasets in LangSmith** — storing the examples that feedback and failures feed into.
