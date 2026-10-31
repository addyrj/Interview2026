---

# 396. Answer Correctness
# हिंदी में: Answer Correctness

---

## 🔵 Simple Definition (English)
Answer correctness compares the generated answer with the ground-truth answer. In Ragas it combines factual correctness (claims overlap, F1-style) and semantic similarity (embedding closeness) into one 0-1 score.

## 🔵 सरल परिभाषा (Hindi)
Answer correctness generated answer की तुलना ground-truth answer से करता है। Ragas में ये factual correctness (claims का overlap, F1-style) और semantic similarity (embedding की निकटता) को मिलाकर 0-1 score देता है।

---

## 🔴 Problem it Solves
Other RAG metrics check pieces (retrieval, grounding). End users care whether the final answer is right. Correctness is the end-to-end quality number to track across prompt, model and retriever changes.

## 🔴 यह क्यों बना? (Hindi)
बाकी RAG metrics हिस्सों को जाँचते हैं (retrieval, grounding)। End users को परवाह है कि final जवाब सही है या नहीं। Correctness वो end-to-end quality number है जिसे prompt, model और retriever बदलते समय track करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input: question, generated answer, reference answer
Step 2 → Extract claims from both answer and reference
Step 3 → Classify claims: TP (in both), FP (only in answer), FN (only in reference)
Step 4 → Factual score = F1 = 2TP / (2TP + FP + FN)
Step 5 → Semantic score = cosine(embedding(answer), embedding(reference))
Step 6 → Final = weighted mean (Ragas default roughly 0.75 factual / 0.25 semantic)
Step 7 → Track mean and distribution over the test set
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input: question, generated answer, reference answer
Step 2 → Answer और reference दोनों से claims निकालो
Step 3 → Claims बाँटो: TP (दोनों में), FP (सिर्फ़ answer में), FN (सिर्फ़ reference में)
Step 4 → Factual score = F1 = 2TP / (2TP + FP + FN)
Step 5 → Semantic score = cosine(embedding(answer), embedding(reference))
Step 6 → Final = weighted mean (Ragas default लगभग 0.75 factual / 0.25 semantic)
Step 7 → Test set पर mean और distribution track करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Reference: "HS 8507.60; duty 20 percent." Answer A: "HS 8507.60, duty 20 percent, BIS needed." TP=2, FP=1, FN=0, F1=0.8. Answer B: "HS 8507.60, duty 10 percent." TP=1, FP=1, FN=1, F1=0.5. B is wrong on the number that matters. **Amazon-style**: "delivery in 2 days" vs reference "delivery in 5 days" - semantically close, factually wrong; that is why factual claims matter.

## 🟡 Real Example Hindi mein
**Tariff System**: Reference: "HS 8507.60; duty 20 percent।" Answer A: "HS 8507.60, duty 20 percent, BIS चाहिए।" TP=2, FP=1, FN=0, F1=0.8। Answer B: "HS 8507.60, duty 10 percent।" TP=1, FP=1, FN=1, F1=0.5। B उस number पर गलत है जो मायने रखता है। **Amazon-style**: "2 दिन में delivery" बनाम reference "5 दिन में" - semantically पास, factually गलत; इसीलिए factual claims ज़रूरी हैं।

---

## 💻 Code Example — Basic
```python
# Pure Python: F1 over claim sets (claims given by hand, no LLM). Offline and exact.
def f1(answer_claims: set[str], reference_claims: set[str]) -> float:
    tp = len(answer_claims & reference_claims)                # claims in both
    fp = len(answer_claims - reference_claims)                # extra/wrong claims
    fn = len(reference_claims - answer_claims)                # missing claims
    denom = 2 * tp + fp + fn
    return 2 * tp / denom if denom else 0.0                   # F1 formula

ref = {"hs=8507.60", "duty=20%"}
ans_a = {"hs=8507.60", "duty=20%", "bis=required"}
ans_b = {"hs=8507.60", "duty=10%"}
print(round(f1(ans_a, ref), 2))                               # 0.8
print(round(f1(ans_b, ref), 2))                               # 0.5
```

## 💻 Code Example — Advanced
```python
# Production: LLM claim extraction + F1 + embedding similarity, async, error handling.
import asyncio                                                # async
import json                                                   # parse
import logging                                                # logs
import numpy as np                                            # vectors
from openai import AsyncOpenAI, OpenAIError                   # client

log = logging.getLogger("answer_correctness")                 # logger
client = AsyncOpenAI()                                        # needs OPENAI_API_KEY

async def claims_of(text: str) -> set[str]:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=200,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content":
                   'List atomic factual claims in this text as JSON {"claims":[str]}, short and normalised:\n' + text}])
    return {c.strip().lower() for c in json.loads(r.choices[0].message.content or "{}").get("claims", [])}

async def embed(text: str) -> np.ndarray:
    r = await client.embeddings.create(model="text-embedding-3-small", input=text)
    v = np.array(r.data[0].embedding, dtype=np.float32)
    return v / np.linalg.norm(v)                              # unit vector

async def answer_correctness(answer: str, reference: str, w_fact: float = 0.75) -> float:
    try:
        a_claims, r_claims, a_vec, r_vec = await asyncio.gather(
            claims_of(answer), claims_of(reference), embed(answer), embed(reference))
    except (OpenAIError, json.JSONDecodeError) as exc:
        log.error("scoring failed: %s", exc)
        return float("nan")
    tp, fp, fn = len(a_claims & r_claims), len(a_claims - r_claims), len(r_claims - a_claims)
    fact = 2 * tp / (2 * tp + fp + fn) if (tp + fp + fn) else 0.0   # F1
    sem = float(a_vec @ r_vec)                                # cosine similarity
    return w_fact * fact + (1 - w_fact) * sem
```
Note: exact string matching of LLM-written claims is brittle; Ragas uses an NLI-style LLM step to match claims by meaning. Treat this as a simplified version.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                                   # app
from pydantic import BaseModel                                # model

app = FastAPI()                                               # app

class Pair(BaseModel):
    answer: str                                               # system answer
    reference: str                                            # ground truth

@app.post("/eval/answer-correctness")
async def endpoint(p: Pair) -> dict[str, float]:
    return {"answer_correctness": await answer_correctness(p.answer, p.reference)}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from ragas import evaluate, EvaluationDataset                 # runner
from ragas.metrics import AnswerCorrectness                   # combined metric (also FactualCorrectness exists)
from ragas.llms import LangchainLLMWrapper                    # wrappers
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))
ds = EvaluationDataset.from_list([{
    "user_input": "Duty on lithium battery?",
    "response": "HS 8507.60, duty 20 percent.",
    "reference": "HS 8507.60; duty 20 percent.",
}])
# result = evaluate(ds, metrics=[AnswerCorrectness()], llm=llm, embeddings=emb)
# Run your LangGraph app on each question to fill "response", then evaluate.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using only embedding similarity
✅ Correct: include factual claim matching; numbers/negations barely change embeddings.

```python
# Wrong
score = cosine(emb(answer), emb(reference))
# Right
score = 0.75 * claim_f1 + 0.25 * cosine
```

❌ Mistake 2: Judging with the same model that generated the answer
✅ Correct: use a different (stronger) judge to avoid self-preference bias.

```python
# Wrong
judge = generator_model
# Right
judge = stronger_or_different_model
```

---

## 🧠 Tricky Interview Question
**Q**: "Your answer is correct but more detailed than the reference and scores 0.6. Is the metric broken?"

**Answer**: Extra true claims count as false positives, lowering F1. Either enrich the reference, use a recall-oriented mode (penalise only missing claims), or separate "correctness" from "completeness/verbosity" by reporting precision and recall of claims individually.

---

## ⚫ Interview Questions + Answers

Q1: What does answer correctness compare? (Easy)
A1: Generated answer versus ground-truth answer.

Q2: Which two parts make the score? (Easy)
A2: Factual correctness (claim F1) and semantic similarity.

Q3: Why include semantic similarity? (Medium)
A3: It rewards paraphrases and partial meaning match where claim extraction is imperfect.

Q4: What are the limits of LLM-judged correctness? (Medium)
A4: Judge noise, bias to its own style, cost, sensitivity to claim extraction; mitigate with temperature 0, multiple runs, human spot checks.

Q5: How do you use it in CI? (Hard)
A5: Version a golden set, run the pipeline offline on each change, compute mean and per-slice scores, set a threshold with tolerance for judge noise, block merges on significant regression, and store results for trend dashboards.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have reference answers
- Comparing models/prompts

❌ Avoid when:
- Open-ended creative answers (no single truth)
- No ground truth (use faithfulness/relevancy)

---

## 📊 Visual Diagram
```
 answer claims:    {A, B, X}        reference claims: {A, B, C}
 TP=2 (A,B)  FP=1 (X)  FN=1 (C)   F1 = 4/(4+1+1) = 0.67
 semantic cosine = 0.9
 correctness = 0.75*0.67 + 0.25*0.9 = 0.73
```

---

## 💰 Cost Impact
Per row: two claim-extraction calls (about 300 tokens each) plus two embeddings: roughly $0.0003 on gpt-4o-mini. A 1000-row nightly run is about $0.30. Optimise: cache reference claims (they never change), evaluate stratified samples, use cheaper judge for smoke runs and a stronger one for releases.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Answer correctness | Match with ground truth | ground truth से मेल |
| Factual correctness | Claim-level F1 | claims का F1 |
| Semantic similarity | Embedding closeness | embedding की निकटता |
| TP/FP/FN | Matched/extra/missing claims | मिले/अतिरिक्त/छूटे claims |
| Golden set | Verified test set | जाँचा हुआ test set |

---

## ⚡ 3-Line Summary
English: Answer correctness scores the final answer against a reference using claim F1 plus semantic similarity. It is the end-to-end quality metric. Judge noise and extra true claims affect it.
Hindi: Answer correctness final जवाब को reference से claim F1 और semantic similarity से score करता है। ये end-to-end quality metric है। Judge noise और अतिरिक्त सही claims इसे प्रभावित करते हैं।

---

## ➡️ Next Topic
**397. Ragas - Complete Guide** - the framework that bundles all these metrics.
