---

# 485. Fairness in AI Systems
# हिंदी में: AI Systems में Fairness (निष्पक्षता)

---

## 🔵 Simple Definition (English)
Fairness means an AI system gives comparable quality and outcomes to different groups. There are several mathematical definitions (demographic parity, equal opportunity, equalized odds) and they can conflict, so you pick the one that fits the business and legal risk. Fixing bias can be done before, during or after training.

## 🔵 सरल परिभाषा (Hindi)
Fairness का मतलब है कि AI अलग-अलग groups को बराबर quality और outcomes दे। इसकी कई mathematical definitions हैं (demographic parity, equal opportunity, equalized odds) और ये आपस में टकरा सकती हैं, इसलिए business और legal risk के हिसाब से एक चुनते हैं।

---

## 🔴 Problem it Solves
Detecting bias (topic 484) is not enough. Teams need a clear target ("what is fair here?") and techniques to reach it. Without a definition, arguments go in circles and fixes break accuracy elsewhere.

## 🔴 यह क्यों बना? (Hindi)
Bias पकड़ना (topic 484) काफी नहीं। Team को target चाहिए ("यहाँ fair क्या है?") और उसे पाने की techniques। Definition नहीं होगी तो बहस चलती रहेगी और fix से दूसरी जगह accuracy टूटेगी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose fairness definition that matches the harm (who is hurt by a miss?)
Step 2 → Measure the metric per group (from topic 484)
Step 3 → Pick a mitigation: pre-process (rebalance data), in-process (constraints), post-process (per-group thresholds)
Step 4 → For LLMs: improve prompts, add balanced few-shot examples, add region-specific retrieval data
Step 5 → Re-measure; check overall accuracy did not collapse
Step 6 → Document the trade-off and monitor in production
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Harm के हिसाब से fairness definition चुनो
Step 2 → Metric per group measure करो
Step 3 → Mitigation चुनो: data rebalance / constraints / per-group thresholds
Step 4 → LLM में: बेहतर prompts, balanced few-shot, region-specific retrieval data
Step 5 → दोबारा measure करो, overall accuracy न गिरे
Step 6 → Trade-off document करो और production में monitor करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Harm = wrongly flagging shipments for inspection. Use **equal opportunity / equal false-positive rate** across origin countries, so honest importers from any country face the same inspection rate. If one region's goods are flagged 3x more because RAG documents are mostly about other regions, add regional tariff notes to the vector store and tune the thresholds per category.
**Zomato-style example**: Restaurant ranking should not systematically bury small restaurants only because they have fewer reviews (cold-start fairness).

## 🟡 Real Example Hindi mein
**Tariff System**: Harm = गलत तरीके से shipment inspection के लिए flag होना। Origin countries में equal false-positive rate रखो, ताकि ईमानदार importers को हर देश से बराबर inspection rate मिले। किसी region का माल 3x ज़्यादा flag हो रहा है तो उस region के tariff notes vector store में जोड़ो।

---

## 💻 Code Example — Basic
```python
# Basic: demographic parity and equal opportunity in pure Python (runs offline)
def rate(values: list[int]) -> float:  # average of 0/1 list
    return sum(values) / len(values) if values else 0.0  # avoid divide by zero


data = [  # (group, actual_good, predicted_approve)
    ("A", 1, 1), ("A", 1, 1), ("A", 0, 0), ("A", 1, 0),
    ("B", 1, 1), ("B", 1, 0), ("B", 1, 0), ("B", 0, 0),
]
groups = {g for g, _, _ in data}  # unique groups
for g in sorted(groups):  # per group metrics
    preds = [p for gg, _, p in data if gg == g]  # all predictions
    pos_preds = [p for gg, a, p in data if gg == g and a == 1]  # only truly good items
    print(g, "approval_rate=", round(rate(preds), 2),  # demographic parity metric
          "TPR=", round(rate(pos_preds), 2))  # equal opportunity metric (true positive rate)
# Output shows A has higher TPR than B -> unfair under equal opportunity
```

## 💻 Code Example — Advanced
```python
# Advanced: post-processing with per-group thresholds, async scoring, error handling
import asyncio  # async runtime
from dataclasses import dataclass  # records


@dataclass(frozen=True)
class Scored:  # one scored item
    group: str  # group name
    score: float  # model score 0..1


async def score_item(group: str, text: str) -> Scored:  # mock async model
    await asyncio.sleep(0.001)  # simulate latency
    base = 0.8 if "electronics" in text else 0.55  # toy score
    return Scored(group, base)  # return


def pick_threshold(scores: list[float], target_tpr: float = 0.9) -> float:  # per-group cutoff
    if not scores:  # no data
        raise ValueError("no scores for group")  # explicit error
    ordered = sorted(scores, reverse=True)  # high to low
    idx = max(0, int(len(ordered) * target_tpr) - 1)  # position for target recall
    return ordered[idx]  # threshold value


async def main() -> None:  # demo
    items = [("A", "electronics x"), ("A", "electronics y"), ("B", "textile a"), ("B", "textile b")]  # inputs
    try:  # guard whole batch
        scored = await asyncio.gather(*(score_item(g, t) for g, t in items))  # parallel scoring
    except Exception as exc:  # unexpected failure
        print("scoring failed:", exc)  # report
        return  # stop safely
    by_group: dict[str, list[float]] = {}  # collect scores per group
    for s in scored:  # loop
        by_group.setdefault(s.group, []).append(s.score)  # append
    thresholds = {g: pick_threshold(v) for g, v in by_group.items()}  # one threshold per group
    print(thresholds)  # inspect (note: legality of group-specific thresholds varies; get legal review)


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Expose a fairness dashboard endpoint and a config endpoint for thresholds. Keep thresholds in config (not hard-coded) and log which threshold was applied to each decision for audits.

```python
from fastapi import FastAPI, Depends  # app + dependency injection
from pydantic import BaseModel  # schema

app = FastAPI()  # app


class Settings(BaseModel):  # config object
    review_threshold: float = 0.75  # below this go to human
    max_gap: float = 0.05  # allowed fairness gap


def get_settings() -> Settings:  # dependency
    return Settings()  # load from env/DB in prod


@app.get("/fairness/status")  # status route
async def status(cfg: Settings = Depends(get_settings)) -> dict[str, float | bool]:
    gap = 0.23  # replace with latest measured gap
    return {"max_gap": gap, "allowed": cfg.max_gap, "pass": gap <= cfg.max_gap}  # gate result
```

---

## 🔗 LangChain / LangGraph Connection
Fairness mitigation for RAG usually happens in retrieval: use metadata filters and balanced retrievers so every region or category has coverage. In LangGraph, add an evaluation node after generation that compares answers for paired inputs.

```python
# LangChain: balanced retrieval using a metadata filter per region (real API: as_retriever search_kwargs)
# retriever = vectorstore.as_retriever(search_kwargs={"k": 4, "filter": {"region": region}})
from langchain_core.documents import Document  # real document type

docs = [Document(page_content="Handloom textile note", metadata={"region": "IN"}),
        Document(page_content="Electronics note", metadata={"region": "US"})]  # sample store
by_region = {}  # group docs
for d in docs:  # loop
    by_region.setdefault(d.metadata["region"], []).append(d)  # bucket
print({k: len(v) for k, v in by_region.items()})  # coverage per region
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Optimising one fairness metric and assuming all are satisfied
✅ Correct: state which metric you chose and why; know that they conflict.
```python
# Wrong
assert demographic_parity_ok  # ignoring error rates
# Right
assert equal_opportunity_gap <= 0.05 and overall_accuracy >= 0.9  # explicit trade-off
```

❌ Mistake 2: Fixing the model but not the data/retrieval
✅ Correct: check the knowledge base coverage first.
```python
# Wrong
prompt += "Be fair."  # vague
# Right
add_regional_documents(vectorstore, region="IN")  # fix the real cause
```

---

## 🧠 Tricky Interview Question
**Q**: "Can a system satisfy demographic parity and equal opportunity at the same time?"

**Answer**: Generally no, unless base rates are equal across groups or the classifier is perfect. Known impossibility results show several fairness criteria conflict. So choose based on the harm: if false rejections are the main harm, prefer equal opportunity; if equal selection rates are legally required, use parity. Document the choice.

---

## ⚫ Interview Questions + Answers

Q1: What is demographic parity? (Easy)
A1: Each group gets the positive outcome at the same rate, regardless of true labels.

Q2: What is equal opportunity? (Easy)
A2: Among people who truly deserve the positive outcome, each group has the same true positive rate.

Q3: Name three mitigation stages. (Medium)
A3: Pre-processing (rebalance or reweigh data), in-processing (add fairness constraints or loss), post-processing (adjust thresholds or outputs). For LLM apps: prompt changes, retrieval coverage, output filters.

Q4: Why can fairness reduce accuracy? (Medium)
A4: Constraints limit the best unconstrained decision boundary. Often the drop is small, and sometimes the unfair accuracy was inflated by majority-group performance. Report the trade-off.

Q5: Design a fairness review for a high-impact LLM classifier. (Hard)
A5: Define harm and metric, build stratified eval sets, measure gaps with confidence intervals, test counterfactuals, fix data/retrieval first, then thresholds, re-test regressions, get legal review for group-aware methods, add human appeal, log decisions, and monitor gaps with alerts and scheduled re-audits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Decisions affect access, money, safety or opportunity
- Regulated domains or enterprise requirements

❌ Avoid / caution:
- Group-specific thresholds without legal review
- Chasing fairness metrics on tiny samples

---

## 📊 Visual Diagram
```
 Data ──▶ [Pre-process: rebalance]
              │
              ▼
          Model ──▶ [In-process: constraints]
              │
              ▼
          Scores ──▶ [Post-process: thresholds / review]
              │
              ▼
        Per-group metrics ──▶ gap <= limit ? ──▶ ship
                                   │ no
                                   └──▶ iterate
```

---

## 💰 Cost Impact
Fairness work costs mostly evaluation tokens and engineering time. Larger eval sets per group raise token usage (illustrative: 5 groups x 500 items x 700 tokens = 1.75M tokens per full run). Extra retrieval data increases embedding and storage cost.
Optimise: stratified sampling, cheaper model for broad sweeps, cache embeddings of the regional documents, run full audits on release rather than per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Demographic parity | Equal positive rate per group | बराबर selection rate |
| Equal opportunity | Equal true positive rate | बराबर TPR |
| Equalized odds | Equal TPR and FPR | बराबर TPR और FPR |
| Threshold | Score cutoff | सीमा |
| Mitigation | Method to reduce bias | समाधान तकनीक |
| Trade-off | Gain one, lose another | समझौता |

---

## ⚡ 3-Line Summary
English: Fairness needs a chosen definition tied to real harm.
Mitigate through data, retrieval, thresholds and human review, then re-measure.
Metrics can conflict, so document the trade-off.
Hindi: Fairness के लिए real harm से जुड़ी एक definition चुननी पड़ती है।
Data, retrieval, thresholds और human review से सुधार करो, फिर दोबारा measure करो।
Metrics टकरा सकते हैं, इसलिए trade-off document करो।

---

## ➡️ Next Topic
**506. AI System Design — Framework** — a repeatable method to structure any AI system design interview answer.
