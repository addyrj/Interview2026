---

# 410. Human Evaluation
# हिंदी में: Human Evaluation (इंसानी मूल्यांकन)

---

## 🔵 Simple Definition (English)
Human evaluation means real people (domain experts or trained annotators) read LLM outputs and rate them using a clear rubric: correct/incorrect, 1-5 scales, or A-vs-B preference. It is slow and costly but remains the reference standard that automatic metrics and LLM judges are checked against.

## 🔵 सरल परिभाषा (Hindi)
Human evaluation में असली लोग (domain experts या trained annotators) LLM outputs पढ़कर साफ rubric से rating देते हैं: सही/गलत, 1-5 scale, या A-बनाम-B preference। यह धीमा और महँगा है, पर वही reference standard है जिससे automatic metrics और LLM judges जाँचे जाते हैं।

---

## 🔴 Problem it Solves
Automatic metrics miss tone, legal correctness, subtle hallucinations and usefulness. LLM judges have biases. For high-stakes domains (customs, medical, finance) a human must confirm quality, and humans are needed to create labels and calibrate everything else.

## 🔴 यह क्यों बना? (Hindi)
Automatic metrics tone, legal correctness, बारीक hallucinations और usefulness चूक जाते हैं। LLM judges में bias होता है। High-stakes domains (customs, medical, finance) में इंसान को quality confirm करनी पड़ती है, और बाकी सब को calibrate करने के लिए labels भी इंसान ही बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the question: what exactly are raters judging? (correctness, helpfulness, safety)
Step 2 → Write a rubric with anchored scale and examples; train raters
Step 3 → Sample outputs (random + low-confidence + flagged); hide system identity (blind)
Step 4 → Show items in random order; 2-3 raters per item
Step 5 → Collect ratings + free-text comments
Step 6 → Measure agreement (kappa / Krippendorff alpha); adjudicate disagreements
Step 7 → Aggregate (majority/mean), analyse by slice, feed findings into prompts, golden set, judges
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → सवाल तय करो: raters क्या judge कर रहे हैं? (correctness, helpfulness, safety)
Step 2 → Anchored scale और examples के साथ rubric लिखो; raters को train करो
Step 3 → Outputs sample करो (random + कम-confidence + flagged); system का नाम छुपाओ (blind)
Step 4 → Items random order में दिखाओ; हर item पर 2-3 raters
Step 5 → Ratings + free-text comments इकट्ठा करो
Step 6 → Agreement नापो (kappa / Krippendorff alpha); असहमति adjudicate करो
Step 7 → Aggregate (majority/mean), slice-wise विश्लेषण, findings को prompts, golden set, judges में डालो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Each week, 40 answers are sampled: 20 random, 20 with low model confidence. Two customs officers rate "HS code correct?" (yes/no) and "explanation acceptable?" (1-5), blind to model version. Disagreements go to a senior officer. Findings: errors cluster in "parts vs complete machines", so those cases are added to the golden set and the prompt gets a new rule.

**Zomato-style**: Raters compare two recommendation lists (A/B) for relevance, with sides randomised.

## 🟡 Real Example Hindi mein
**Tariff System**: हर हफ्ते 40 answers sample होते हैं: 20 random, 20 कम model confidence वाले। दो customs officers "HS code सही?" (हाँ/नहीं) और "explanation स्वीकार्य?" (1-5) rate करते हैं, model version जाने बिना। असहमति senior officer को जाती है। नतीजा: errors "parts बनाम complete machines" में हैं, इसलिए वे cases golden set में जुड़े और prompt में नया rule आया।

**Zomato-style**: Raters दो recommendation lists (A/B) की relevance तुलना करते हैं, sides random रखकर।

---

## 💻 Code Example — Basic
```python
# Basic: aggregate human ratings + agreement (pure Python, offline)
from collections import Counter  # vote counting
from statistics import mean  # averages

ratings: dict[str, list[int]] = {  # item id -> ratings from 3 raters (1..5)
    "q1": [5, 5, 4],
    "q2": [2, 4, 1],  # high disagreement
    "q3": [4, 4, 4],
}


def majority(votes: list[bool]) -> bool:  # majority vote for yes/no labels
    return Counter(votes).most_common(1)[0][0]  # most frequent label


def disagreement(vals: list[int]) -> int:  # range of ratings as a simple spread measure
    return max(vals) - min(vals)  # larger = more disagreement


for item, vals in ratings.items():  # check every item
    flag = "REVIEW" if disagreement(vals) >= 2 else "ok"  # flag spread >= 2
    print(item, "mean", round(mean(vals), 2), flag)  # q1 ok, q2 REVIEW, q3 ok
print(majority([True, True, False]))  # True
```

## 💻 Code Example — Advanced
```python
# Advanced: review queue with smart sampling + validated ratings + async storage-safe aggregation
import asyncio  # lock for safe concurrent updates
import logging  # logs
import random  # sampling
from collections import defaultdict  # grouping
from statistics import mean  # average
from typing import Literal  # types

from pydantic import BaseModel, Field  # validation

log = logging.getLogger("human_eval")  # logger


class Item(BaseModel):  # an output waiting for review
    id: str
    question: str
    answer: str
    confidence: float = Field(ge=0, le=1)  # model-reported or judge-derived confidence


class Rating(BaseModel):  # one human rating
    item_id: str
    rater: str
    correct: bool  # primary label
    quality: int = Field(ge=1, le=5)  # secondary 1-5
    comment: str = ""  # free text


class ReviewQueue:
    def __init__(self, raters_per_item: int = 2) -> None:
        self.items: dict[str, Item] = {}  # item store
        self.ratings: dict[str, list[Rating]] = defaultdict(list)  # item -> ratings
        self.k = raters_per_item  # how many ratings needed
        self._lock = asyncio.Lock()  # avoid race conditions

    def sample(self, pool: list[Item], n_random: int, n_low_conf: int, seed: int = 0) -> None:
        rng = random.Random(seed)  # reproducible
        low = sorted(pool, key=lambda i: i.confidence)[:n_low_conf]  # least confident items
        rest = [i for i in pool if i not in low]  # others
        picked = low + rng.sample(rest, min(n_random, len(rest)))  # mix targeted + random
        rng.shuffle(picked)  # random order (avoid order effects)
        for it in picked:  # enqueue
            self.items[it.id] = it

    async def submit(self, r: Rating) -> None:
        async with self._lock:  # safe update
            if r.item_id not in self.items:  # validate id
                raise KeyError(f"unknown item {r.item_id}")
            if any(x.rater == r.rater for x in self.ratings[r.item_id]):  # one rating per rater
                raise ValueError("rater already rated this item")
            self.ratings[r.item_id].append(r)  # store

    def report(self) -> dict:
        done = {i: rs for i, rs in self.ratings.items() if len(rs) >= self.k}  # fully rated
        conflicts = [i for i, rs in done.items() if len({x.correct for x in rs}) > 1]  # disagree
        acc = mean(sum(x.correct for x in rs) / len(rs) for rs in done.values()) if done else 0.0
        return {"rated": len(done), "pending": len(self.items) - len(done),
                "accuracy": round(acc, 3), "needs_adjudication": conflicts}  # summary
```

---

## 🟠 FastAPI Integration
A simple annotation backend: fetch next item, submit rating, view report.

```python
from fastapi import FastAPI, HTTPException  # web

app = FastAPI()  # app
queue = ReviewQueue(raters_per_item=2)  # shared queue


@app.get("/review/next/{rater}")  # get an item this rater has not rated
async def next_item(rater: str) -> Item:
    for it in queue.items.values():  # scan items
        rs = queue.ratings[it.id]  # existing ratings
        if len(rs) < queue.k and all(r.rater != rater for r in rs):  # needs more, not by this rater
            return it  # serve
    raise HTTPException(404, "nothing to review")  # empty


@app.post("/review/rate", status_code=201)  # save rating
async def rate(r: Rating) -> dict:
    try:
        await queue.submit(r)  # validate + store
    except (KeyError, ValueError) as exc:  # bad input
        raise HTTPException(400, str(exc))
    return {"ok": True}


@app.get("/review/report")  # progress
async def report() -> dict:
    return queue.report()  # aggregated
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph supports **human-in-the-loop**: `interrupt()` pauses a graph for human review and resumes with the human's decision; LangSmith has annotation queues to collect human feedback on traces. Both feed the same loop: human labels become eval data.

```python
# LangGraph: pause for human approval when confidence is low (langgraph>=0.2)
from langgraph.types import interrupt  # pauses the graph and waits for input

def review_node(state: dict) -> dict:
    if state["confidence"] < 0.6:  # low confidence -> ask a human
        decision = interrupt({"question": state["question"], "answer": state["answer"]})  # waits
        return {"approved": decision == "approve"}  # resume value from human
    return {"approved": True}  # auto-approve confident answers
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Raters see which model produced the output (bias)
✅ Correct: blind, randomised

```python
# Wrong
show(f"[GPT-4o] {answer}")
# Right
show(answer)   # no model name, random order
```

❌ Mistake 2: Vague rubric ("rate quality")
✅ Correct: anchored definitions with examples.

❌ Mistake 3: One rater per item and no agreement metric
✅ Correct: 2-3 raters, kappa/alpha, adjudication.

---

## 🧠 Tricky Interview Question
**Q**: "Your annotators agree 95% of the time, yet your model is clearly flawed on cases they approved. How is that possible?"

**Answer**: High agreement does not mean correctness: raters may share the same bias or not know the domain rule, or the rubric only checks surface qualities (fluent, on-topic). Also, with skewed labels (95% 'correct') raw agreement is misleading; use kappa. Fix with domain experts, adversarial test cases, and checking against objective ground truth where available.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why is human evaluation still needed?
A1: It is the reference for correctness and nuance; automated metrics and judges must be calibrated against it.

Q2: [Easy] What is a blind evaluation?
A2: Raters do not know which system produced an output, avoiding brand bias.

Q3: [Medium] Pointwise vs pairwise human rating?
A3: Pointwise rates one output on a scale (noisy between raters); pairwise preference is easier and more consistent for ranking systems.

Q4: [Medium] How many items and raters?
A4: 100-300 items for a system comparison and 2-3 raters each, enough for stable estimates and agreement metrics; more for small differences.

Q5: [Hard] How do you scale human review in production?
A5: Sample smartly (random for unbiased estimate + low-confidence/flagged for efficiency), use LLM judges for broad coverage, route disagreements to humans, and recalibrate the judge periodically against fresh human labels.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- High-stakes domains and launch decisions
- Creating golden data and calibrating judges

❌ Avoid when:
- You need thousands of evaluations per day (use judges + human sampling)

---

## 📊 Visual Diagram
```
 outputs ─► sample (random + low-confidence) ─► blind + shuffle
                                                   │
                                  Rater A ─┐       │
                                  Rater B ─┼─► agreement (kappa) ─► adjudicate
                                  Rater C ─┘                           │
                                                   labels ─► golden set / judge calibration / prompt fixes
```

---

## 💰 Cost Impact
Humans are the main cost: e.g. 200 items x 2 raters x 2 min = ~13 hours. LLM tokens are negligible, but you can cut human hours by pre-screening with an LLM judge (e.g. ~1.5K tokens/item ≈ $0.0003 on gpt-4o-mini) and sending only uncertain or failing items to people.
Optimise: stratified sampling, clear rubric (faster ratings), good tooling, reuse labels for the golden set.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Annotator / Rater | Person labelling outputs | Output label करने वाला व्यक्ति |
| Rubric | Rating guidelines | Rating के दिशानिर्देश |
| Blind evaluation | Hidden system identity | System पहचान छुपी |
| Inter-rater agreement | How much raters agree | Raters की सहमति |
| Adjudication | Resolving conflicts | मतभेद सुलझाना |

---

## ⚡ 3-Line Summary
English: Human evaluation is the trusted but expensive standard: blind, randomised, rubric-based, multiple raters. Measure agreement and adjudicate conflicts. Use it to build golden sets and calibrate automated judges.
Hindi: Human evaluation भरोसेमंद पर महँगा standard है: blind, random, rubric-आधारित, कई raters। Agreement नापो और मतभेद सुलझाओ। इससे golden sets बनाओ और automatic judges calibrate करो।

---

## ➡️ Next Topic
**411. A/B Testing RAG Systems** - compare two versions on live traffic with statistics.
