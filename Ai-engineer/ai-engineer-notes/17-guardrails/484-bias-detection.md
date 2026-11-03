---

# 484. Bias Detection
# हिंदी में: Bias Detection (पक्षपात की पहचान)

---

## 🔵 Simple Definition (English)
Bias detection means measuring whether an AI treats groups differently in an unfair way. You compare outputs or error rates across groups (country, gender, language, product type) and flag large gaps. Methods: counterfactual tests, group metrics, and bias benchmarks.

## 🔵 सरल परिभाषा (Hindi)
Bias detection का मतलब है यह मापना कि AI अलग-अलग groups (देश, gender, भाषा, product type) के साथ अनुचित अलग व्यवहार तो नहीं करता। Groups के बीच outputs या error rates compare करके बड़े gaps पकड़े जाते हैं।

---

## 🔴 Problem it Solves
Training data reflects the world, including its stereotypes and gaps. A model can look great on average but fail for a minority group. Bias is invisible unless you measure it on purpose, and finding it after a public incident is costly.

## 🔴 यह क्यों बना? (Hindi)
Training data में दुनिया के stereotypes और gaps होते हैं। Model average में अच्छा दिख सकता है पर किसी छोटे group के लिए fail हो सकता है। जान-बूझकर measure न करो तो bias दिखता ही नहीं, और incident के बाद पकड़ना महँगा पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define groups to compare (country of origin, language, category)
Step 2 → Build or collect a test set labelled with the group
Step 3 → Run the model on every item and record output/correctness
Step 4 → Compute per-group metrics (accuracy, approval rate, refusal rate)
Step 5 → Compare gaps (max - min) against a threshold
Step 6 → Counterfactual test: swap only the sensitive attribute, compare answers
Step 7 → Report, fix (data, prompt, threshold), re-test
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Groups तय करो (देश, भाषा, category)
Step 2 → Group label वाला test set बनाओ
Step 3 → हर item पर model चलाओ, output/correctness note करो
Step 4 → Per-group metrics निकालो (accuracy, approval rate, refusal rate)
Step 5 → Gap (max - min) को threshold से compare करो
Step 6 → Counterfactual: सिर्फ sensitive attribute बदलो, answers compare करो
Step 7 → Report करो, fix करो, दोबारा test करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Evaluate HS-code accuracy by origin country and by product category. If accuracy for "handloom textiles" is 72% while "electronics" is 96%, there is a category bias, likely from training/RAG data imbalance. Counterfactual: the same description with the importer name changed to a different region should get the same code.
**Amazon-style example**: A product-moderation AI flagging listings in regional languages far more often than English ones.

## 🟡 Real Example Hindi mein
**Tariff System**: Origin country और product category के हिसाब से HS-code accuracy निकालो। "handloom textiles" 72% और "electronics" 96% है तो category bias है (data imbalance)। Counterfactual: वही description, importer का नाम दूसरे region का, तो code वही आना चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic: per-group accuracy and gap (pure Python, runs offline)
from collections import defaultdict  # grouping helper


def group_accuracy(rows: list[dict]) -> dict[str, float]:  # rows have group + correct
    totals: dict[str, int] = defaultdict(int)  # count per group
    hits: dict[str, int] = defaultdict(int)  # correct per group
    for r in rows:  # loop each test row
        totals[r["group"]] += 1  # count the row
        hits[r["group"]] += 1 if r["correct"] else 0  # count if correct
    return {g: hits[g] / totals[g] for g in totals}  # accuracy per group


rows = (  # tiny sample test set
    [{"group": "electronics", "correct": True}] * 95 + [{"group": "electronics", "correct": False}] * 5 +
    [{"group": "textiles", "correct": True}] * 72 + [{"group": "textiles", "correct": False}] * 28
)
acc = group_accuracy(rows)  # compute
gap = max(acc.values()) - min(acc.values())  # largest difference
print(acc)  # {'electronics': 0.95, 'textiles': 0.72}
print(f"gap={gap:.2f}", "BIAS FLAG" if gap > 0.05 else "ok")  # threshold 5 points
```

## 💻 Code Example — Advanced
```python
# Advanced: async counterfactual bias test with error handling and type hints
import asyncio  # async runtime
from dataclasses import dataclass  # result record


@dataclass
class CFResult:  # counterfactual result
    template: str  # prompt template
    a: str  # answer for variant A
    b: str  # answer for variant B
    consistent: bool  # same answer?


async def mock_model(prompt: str) -> str:  # stand-in for an LLM
    await asyncio.sleep(0.005)  # simulate latency
    return "8517.13" if "phone" in prompt else "0000.00"  # biased only if prompt differs in other ways


async def ask(prompt: str) -> str:  # safe wrapper with retry
    for attempt in range(3):  # up to 3 tries
        try:
            return await asyncio.wait_for(mock_model(prompt), timeout=3)  # timeout
        except asyncio.TimeoutError:  # transient failure
            await asyncio.sleep(0.1 * (attempt + 1))  # backoff
    return "ERROR"  # give up safely


async def counterfactual(template: str, a: str, b: str) -> CFResult:  # swap one attribute
    ans_a, ans_b = await asyncio.gather(ask(template.format(x=a)), ask(template.format(x=b)))  # parallel
    return CFResult(template, ans_a, ans_b, ans_a == ans_b)  # compare


async def main() -> None:  # run suite
    t = "Importer from {x} ships a phone. HS code?"  # same text, different place
    pairs = [("Kerala", "Texas"), ("Lagos", "Berlin")]  # variants
    results = await asyncio.gather(*(counterfactual(t, a, b) for a, b in pairs))  # run all
    rate = sum(r.consistent for r in results) / len(results)  # consistency rate
    print(f"consistency={rate:.0%}")  # should be 100%


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Expose a bias-report endpoint that runs the evaluation on demand (or reads the last CI result), plus record the group label with each production request (only if lawful) so you can monitor gaps.

```python
from fastapi import FastAPI, BackgroundTasks  # app + background jobs
from pydantic import BaseModel  # schema

app = FastAPI()  # app
LAST_REPORT: dict[str, float] = {}  # in-memory cache (use DB in prod)


class BiasReport(BaseModel):  # response model
    accuracy_by_group: dict[str, float]  # metrics
    max_gap: float  # largest gap
    flagged: bool  # over threshold


def run_eval() -> None:  # heavy job, runs in background
    LAST_REPORT.update({"electronics": 0.95, "textiles": 0.72})  # replace with real eval


@app.post("/bias/run")  # trigger
async def trigger(bg: BackgroundTasks) -> dict[str, str]:
    bg.add_task(run_eval)  # do not block the request
    return {"status": "started"}  # immediate response


@app.get("/bias/report", response_model=BiasReport)  # read result
async def report() -> BiasReport:
    gap = (max(LAST_REPORT.values()) - min(LAST_REPORT.values())) if LAST_REPORT else 0.0  # gap
    return BiasReport(accuracy_by_group=LAST_REPORT, max_gap=gap, flagged=gap > 0.05)  # reply
```

---

## 🔗 LangChain / LangGraph Connection
Use LangSmith datasets and evaluators to run per-group evaluations, or write a custom evaluator that tags each example with a group in metadata and aggregates. In LangGraph, add a "bias check" node that runs a counterfactual call before returning on sensitive flows.

```python
# LangChain: run the same chain over paired inputs and compare
from langchain_core.prompts import ChatPromptTemplate  # prompt template
from langchain_core.runnables import RunnableLambda  # offline stand-in for an LLM

prompt = ChatPromptTemplate.from_template("Importer from {place} ships a phone. HS code?")  # template
fake_llm = RunnableLambda(lambda p: "8517.13")  # replace with ChatOpenAI(...) in real use
chain = prompt | fake_llm  # LCEL chain

a = chain.invoke({"place": "Kerala"})  # variant A
b = chain.invoke({"place": "Texas"})  # variant B
print("consistent:", a == b)  # counterfactual check
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reporting only overall accuracy
✅ Correct: report per group and the gap.
```python
# Wrong
print(sum(r["correct"] for r in rows) / len(rows))  # hides subgroup failure
# Right
print(group_accuracy(rows))  # shows each group
```

❌ Mistake 2: Tiny groups, no statistics
✅ Correct: check sample size per group and use confidence intervals before claiming bias.
```python
# Wrong
if acc["rare_group"] < acc["main"]: flag()  # 3 samples!
# Right
if n["rare_group"] >= 100 and gap > 0.05: flag()  # enough data
```

---

## 🧠 Tricky Interview Question
**Q**: "You removed the 'country' field from the input. Is your model now unbiased?"

**Answer**: No. This is "fairness through unawareness" and it fails because other features act as proxies (language, address format, company name). You must still measure outcomes per group using labels kept only for evaluation, and test counterfactuals.

---

## ⚫ Interview Questions + Answers

Q1: What is bias in AI? (Easy)
A1: Systematic unfair difference in model behaviour or outcomes for certain groups, usually caused by data, labels or design choices.

Q2: Name sources of bias. (Easy)
A2: Sampling bias, historical bias, label bias, proxy features, and feedback loops. For LLMs also stereotypes from web text and prompt wording.

Q3: What is a counterfactual test? (Medium)
A3: Change only the sensitive attribute in an input (name, place, gender) and check whether the output changes. A change signals bias.

Q4: Which benchmarks exist for LLM bias? (Medium)
A4: BBQ, StereoSet, CrowS-Pairs and WinoBias are commonly cited. They are limited and English-centric, so build your own domain tests too.

Q5: How do you monitor bias in production when group labels are unavailable? (Hard)
A5: Use proxies carefully (language, region from metadata where lawful), periodic labelled audit samples, synthetic counterfactual probes run on a schedule, and track refusal/escalation rates by segment. Alert on drift in these gaps and keep a human-reviewed audit set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Outputs affect people differently (credit, hiring, moderation, duties)
- Before every major model or prompt change
- Multilingual or multi-region products

❌ Avoid / limits:
- Do not collect sensitive attributes without legal basis
- Do not treat one benchmark score as proof of fairness

---

## 📊 Visual Diagram
```
Test set (with group labels)
        │
        ▼
   ┌─────────┐
   │  Model  │
   └────┬────┘
        ▼
 per-group metrics
 ┌────────────┬────────┐
 │ electronics│  95%   │
 │ textiles   │  72%   │──▶ gap 23 pts > 5 → FLAG
 └────────────┴────────┘
        │
        ▼
 fix data / prompt / threshold → re-test
```

---

## 💰 Cost Impact
Bias tests mean extra LLM calls: counterfactual pairs double calls per item (illustrative: 1,000 pairs x 2 calls x 600 tokens = 1.2M tokens per run). Run the full suite in CI or nightly, not on every request.
Optimise: use a cheaper model for broad sweeps and a strong model only on flagged slices, cache repeated prompts, use small stratified samples, and set `max_tokens` low for classification outputs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bias | Systematic unfair skew | पक्षपात |
| Protected attribute | Sensitive trait like gender | संवेदनशील गुण |
| Proxy feature | Feature correlated with sensitive trait | अप्रत्यक्ष संकेत |
| Counterfactual test | Change one attribute, compare | एक चीज़ बदलकर test |
| Subgroup | A slice of data | उप-समूह |
| Benchmark | Standard test set | मानक test set |

---

## ⚡ 3-Line Summary
English: Bias detection measures gaps between groups instead of trusting average accuracy.
Use per-group metrics and counterfactual tests, with enough samples.
Removing sensitive fields does not remove bias because of proxies.
Hindi: Bias detection average accuracy पर भरोसा करने की जगह groups के gap मापता है।
Per-group metrics और counterfactual tests इस्तेमाल करो, samples पर्याप्त रखो।
Sensitive field हटाने से bias नहीं हटता, proxies रहते हैं।

---

## ➡️ Next Topic
**485. Fairness in AI Systems** — which fairness definitions to choose and how to reduce the gaps you found.
