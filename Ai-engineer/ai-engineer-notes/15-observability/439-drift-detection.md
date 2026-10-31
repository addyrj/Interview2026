---

# 439. Drift Detection
# हिंदी में: Drift Detection (बदलाव पकड़ना)

---

## 🔵 Simple Definition (English)
Drift detection means noticing when the world your AI app sees has changed from what you tested on. **Input drift**: users send different kinds of text. **Retrieval/data drift**: the knowledge base changes. **Output drift**: model answers change in length, style or distribution. **Concept drift**: the correct answer itself changes (new tariff rules).

## 🔵 सरल परिभाषा (Hindi)
Drift detection का मतलब है यह पकड़ना कि आपका AI app जो दुनिया देख रहा है वह उससे बदल गई है जिस पर test हुआ था। **Input drift**: users अलग तरह का text भेज रहे हैं। **Retrieval/data drift**: knowledge base बदल गया। **Output drift**: model के जवाबों की लंबाई, style या distribution बदली। **Concept drift**: सही जवाब ही बदल गया (नए tariff rules)।

---

## 🔴 Problem it Solves
- Accuracy falls slowly and labels arrive late; drift signals arrive first and need no labels.
- New product categories (for example "smart rings") are outside the prompt's examples and the retrieval index.
- Annual HS code revisions make old answers obsolete.

## 🔴 यह क्यों बना? (Hindi)
- Accuracy धीरे गिरती है और labels देर से आते हैं; drift signals पहले आते हैं और labels नहीं माँगते।
- नई product categories (जैसे "smart rings") prompt के examples और retrieval index से बाहर हैं।
- HS code की वार्षिक revision पुराने जवाबों को अप्रचलित कर देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose features to watch: input length, language mix, top categories, embedding
         distribution, retrieval scores, output length, code distribution, refusal rate
Step 2 → Freeze a REFERENCE window (for example the last good 2 weeks)
Step 3 → Compute the same features on a CURRENT window (last 24 hours)
Step 4 → Compare distributions: PSI, KS test, chi-square, or embedding centroid distance
Step 5 → Threshold: PSI > 0.2 = significant drift; require enough samples
Step 6 → Inspect: which segment drifted? sample examples, check retrieval hit rate
Step 7 → Respond: update index/prompt/examples, retrain classifier, refresh golden set
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → देखने वाले features चुनो: input length, भाषा mix, top categories, embedding distribution,
         retrieval scores, output length, code distribution, refusal rate
Step 2 → REFERENCE window freeze करो (जैसे पिछले अच्छे 2 हफ्ते)
Step 3 → वही features CURRENT window (पिछले 24 घंटे) पर निकालो
Step 4 → Distributions की तुलना: PSI, KS test, chi-square या embedding centroid distance
Step 5 → Threshold: PSI > 0.2 = ज़रूरी drift; पर्याप्त samples चाहिए
Step 6 → जाँच: कौन सा segment बदला? examples देखो, retrieval hit rate देखो
Step 7 → कदम: index/prompt/examples अपडेट, classifier retrain, golden set refresh
```

---

## 🟡 Real World Example
**Tariff Classification System**: Reference week: 70% electronics, 20% textiles, 10% other. After a new customer onboards, current week: 35% auto parts. PSI on the chapter distribution is above 0.2 (drift). The average top-1 retrieval score drops from 0.78 to 0.61 for those queries because the index has few chapter-87 chunks. The team adds more auto-parts documents and examples before accuracy complaints start.

**Zomato-style**: during a festival, query mix shifts to sweets and gifting; a drift alert tells the team to refresh the menu index and prompt examples.

## 🟡 Real Example Hindi mein
**Tariff System**: Reference सप्ताह: 70% electronics, 20% textiles, 10% अन्य। नया customer जुड़ने के बाद current सप्ताह: 35% auto parts। Chapter distribution पर PSI 0.2 से ऊपर (drift)। उन queries के लिए retrieval का औसत top-1 score 0.78 से 0.61 हो गया क्योंकि index में chapter-87 के chunks कम हैं। Complaints शुरू होने से पहले team और auto-parts documents और examples जोड़ती है।

---

## 💻 Code Example — Basic
Population Stability Index for categorical distributions (pure Python, run directly).

```python
# PSI: compare category distributions between reference and current windows
import math                                           # log
from collections import Counter                       # counting


def distribution(items: list[str], cats: list[str]) -> list[float]:
    c = Counter(items)                                # count per category
    n = max(len(items), 1)                            # avoid divide by zero
    eps = 1e-4                                        # avoid log(0)
    return [max(c[k] / n, eps) for k in cats]         # proportions


def psi(reference: list[str], current: list[str]) -> float:
    cats = sorted(set(reference) | set(current))      # union of categories
    r = distribution(reference, cats)                 # reference proportions
    c = distribution(current, cats)                   # current proportions
    return sum((ci - ri) * math.log(ci / ri) for ri, ci in zip(r, c))


ref = ["electronics"] * 70 + ["textiles"] * 20 + ["other"] * 10
cur = ["electronics"] * 35 + ["textiles"] * 20 + ["other"] * 10 + ["auto"] * 35

score = psi(ref, cur)
print(f"PSI = {score:.2f}")                           # > 0.2 means significant drift
print("DRIFT" if score > 0.2 else "stable")
```

## 💻 Code Example — Advanced
Embedding drift (centroid cosine distance) plus retrieval-score drift with a KS test; async embedding calls with error handling. (`pip install openai numpy scipy`)

```python
# Production drift monitor: embedding centroid shift + retrieval score distribution (KS test)
import asyncio                                                   # async
import logging
from dataclasses import dataclass

import numpy as np                                               # vector math
from scipy.stats import ks_2samp                                 # two-sample KS test
from openai import AsyncOpenAI

log = logging.getLogger("drift")
client = AsyncOpenAI()


async def embed(texts: list[str]) -> np.ndarray:
    try:
        r = await client.embeddings.create(model="text-embedding-3-small", input=texts)
    except Exception as exc:                                     # do not crash monitoring job silently
        log.error("embedding failed: %s", exc)
        raise
    return np.array([d.embedding for d in r.data], dtype=np.float32)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


@dataclass
class DriftReport:
    centroid_distance: float
    ks_pvalue: float
    drifted: bool


async def check_drift(ref_texts: list[str], cur_texts: list[str],
                      ref_scores: list[float], cur_scores: list[float]) -> DriftReport:
    ref_emb, cur_emb = await asyncio.gather(embed(ref_texts), embed(cur_texts))
    dist = cosine_distance(ref_emb.mean(axis=0), cur_emb.mean(axis=0))   # centroid shift
    ks = ks_2samp(ref_scores, cur_scores)                                # score distribution test
    drifted = dist > 0.05 or ks.pvalue < 0.01                            # thresholds: tune on history
    return DriftReport(dist, float(ks.pvalue), drifted)
```

---

## 🟠 FastAPI Integration
Log lightweight features per request, and expose an endpoint that computes drift (in production use a cron/worker instead).

```python
# FastAPI: capture drift features per request; compute PSI on demand
from collections import deque
from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel

from drift_basic import psi                                    # from the basic example

app = FastAPI()
REFERENCE: list[str] = ["electronics"] * 70 + ["textiles"] * 20 + ["other"] * 10
CURRENT: deque[str] = deque(maxlen=2000)                       # rolling window of categories


class Req(BaseModel):
    product: str


@app.post("/classify")
async def classify(req: Req) -> dict:
    category = "electronics"                                   # predicted chapter group
    CURRENT.append(category)                                   # feature for drift
    return {"category": category}


@app.get("/admin/drift")
async def drift() -> dict:
    if len(CURRENT) < 200:                                     # not enough data yet
        return {"status": "insufficient_data", "n": len(CURRENT)}
    score = psi(REFERENCE, list(CURRENT))
    return {"psi": round(score, 3), "drift": score > 0.2,
            "at": datetime.now(timezone.utc).isoformat()}
```

---

## 🔗 LangChain / LangGraph Connection
A retriever wrapper can log top-k scores; LangGraph can include a "drift guard" node that routes out-of-distribution queries to a fallback.

```python
# LangChain: wrap a vector store search to record similarity scores for drift monitoring
from langchain_core.vectorstores import VectorStore

SCORES: list[float] = []


def retrieve_with_scores(store: VectorStore, query: str, k: int = 4):
    pairs = store.similarity_search_with_score(query, k=k)       # [(Document, score), ...]
    if pairs:
        SCORES.append(float(pairs[0][1]))                        # top-1 score (meaning depends on the store's metric)
    return [d for d, _ in pairs]

# Compare SCORES (today) with a stored reference distribution using the KS test.
# LangGraph: add a conditional edge that sends queries with a poor top-1 score
# to a "human_review" or "broader_search" node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Alerting on tiny samples
✅ Correct: require minimum counts and use statistical tests.

```python
# Wrong: 12 requests today, 8 are textiles -> "huge drift!"
# Right
if len(current) >= 200 and psi(reference, current) > 0.2:
    alert()
```

❌ Mistake 2: Never updating the reference window
✅ Correct: refresh the reference after accepting a legitimate change.

```python
# Wrong: reference is from last year forever; permanent alarm
# Right: after verification, reference = current accepted window
REFERENCE = list(CURRENT)
```

---

## 🧠 Tricky Interview Question
**Q**: "Input drift is high, but accuracy on labelled samples is unchanged. Do you act?"

**Answer**: Not urgently, but investigate. Input drift is a risk signal, not proof of failure. The model may generalise well to the new inputs. Check segment-level accuracy (the new segment may have few labels), retrieval scores, and confidence for the drifted segment. Conversely, concept drift (rules change) can occur with NO input drift, so you need both input monitoring and label-based quality monitoring.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What is data drift?
A1: A change in the distribution of input data over time compared with the data you built or tested on.

Q2 (Easy): What is concept drift?
A2: The relationship between input and correct output changes, for example the tariff schedule is revised and the same product now has a different code.

Q3 (Medium): What is PSI and what thresholds are common?
A3: Population Stability Index measures how much a distribution shifted. Rule of thumb: below 0.1 stable, 0.1 to 0.25 moderate, above 0.25 significant.

Q4 (Medium): How do you monitor drift for free-text inputs?
A4: Track simple stats (length, language, vocabulary), cluster embeddings and watch cluster proportions, measure centroid distance, and watch the rate of queries with low retrieval scores or "unknown" intents.

Q5 (Hard): How do you distinguish model drift from data drift when accuracy drops?
A5: Replay a fixed golden set on the current model: if it still scores the same, the model is stable and the inputs/knowledge changed (data/concept drift). If the golden set score drops with no input change, the provider model changed. Also run the old pinned model on current traffic for comparison.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long-running production systems with changing users or knowledge
- Labels are slow or expensive

❌ Avoid when:
- Stable, closed-domain tool with a fixed input set
- Too many features with tight thresholds create alert fatigue

---

## 📊 Visual Diagram
```
 Reference (good weeks)           Current (last 24h)
 electronics ███████ 70%          electronics ████ 35%
 textiles    ██ 20%               textiles    ██ 20%
 other       █ 10%                other       █ 10%
                                  auto parts  ████ 35%  <-- NEW
              \                        /
               └──── PSI > 0.2 ───────┘  -> DRIFT
 Retrieval top-1 score: 0.78 -> 0.61  -> add auto-parts docs, examples, golden cases
```

---

## 💰 Cost Impact
- Cheap features (counts, lengths) cost nothing. Embedding drift costs tokens: embedding 1,000 sampled queries of 30 tokens with `text-embedding-3-small` is 30k tokens, a fraction of a cent.
- Drift triggers spending (re-indexing, new examples), but avoids a larger cost: wrong answers, rework and customer loss.
- Optimise: sample 1-5% of traffic, reuse embeddings already computed for retrieval, run daily not per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Data drift | Input distribution changes | Input distribution बदलना |
| Concept drift | Correct answer rule changes | सही जवाब का नियम बदलना |
| PSI | Distribution shift score | Distribution बदलाव का score |
| KS test | Compares two distributions | दो distributions की तुलना |
| Reference window | Baseline data period | Baseline अवधि का data |
| Centroid | Mean of embeddings | Embeddings का औसत |
| Out-of-distribution | Unlike training/test data | परिचित data से अलग |

---

## ⚡ 3-Line Summary
English: Drift detection compares current inputs, retrieval scores and outputs with a reference window using PSI, KS tests or embedding distance. It warns you before labelled accuracy drops. Respond by updating data, prompts and golden sets.
Hindi: Drift detection current inputs, retrieval scores और outputs की तुलना reference window से PSI, KS test या embedding distance से करता है। यह labelled accuracy गिरने से पहले चेतावनी देता है। जवाब में data, prompts और golden sets अपडेट करो।

---

## ➡️ Next Topic
**440. AI Observability Best Practices** — putting traces, metrics, evals and drift together into a practical production checklist.
