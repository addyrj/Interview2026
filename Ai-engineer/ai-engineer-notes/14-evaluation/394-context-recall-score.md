---

# 394. Context Recall Score
# हिंदी में: Context Recall Score

---

## 🔵 Simple Definition (English)
Context recall measures whether the retrieved context contains all the information needed to produce the correct (ground-truth) answer. Split the reference answer into claims; recall = claims supported by the retrieved context / total claims. High recall means the retriever did not miss anything.

## 🔵 सरल परिभाषा (Hindi)
Context recall मापता है कि retrieved context में सही (ground-truth) जवाब बनाने की सारी जानकारी है या नहीं। Reference answer को claims में बाँटो; recall = retrieved context से supported claims / कुल claims। High recall मतलब retriever ने कुछ miss नहीं किया।

---

## 🔴 Problem it Solves
A RAG answer can be wrong simply because the right chunk was never retrieved. Faithfulness cannot catch this (the LLM faithfully used incomplete context). Context recall isolates retriever misses from generator errors.

## 🔴 यह क्यों बना? (Hindi)
RAG का जवाब सिर्फ़ इसलिए गलत हो सकता है कि सही chunk retrieve ही नहीं हुआ। Faithfulness इसे नहीं पकड़ता (LLM ने अधूरे context का ही ईमानदारी से इस्तेमाल किया)। Context recall retriever की चूक को generator की गलती से अलग करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prepare a test row: question, retrieved_contexts, reference (ground truth)
Step 2 → Break the reference into atomic claims/sentences
Step 3 → For each claim, ask: can it be attributed to the retrieved context?
Step 4 → Count supported claims
Step 5 → recall = supported / total (0 to 1)
Step 6 → Low score -> fix chunking, k, embeddings, hybrid search
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Test row तैयार करो: question, retrieved_contexts, reference (ground truth)
Step 2 → Reference को atomic claims/sentences में तोड़ो
Step 3 → हर claim के लिए पूछो: क्या retrieved context से मिलता है?
Step 4 → Supported claims गिनो
Step 5 → recall = supported / total (0 से 1)
Step 6 → Score कम हो तो chunking, k, embeddings, hybrid search ठीक करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Reference: "Lithium-ion packs fall under HS 8507.60. Basic duty is 20 percent. A BIS certificate is required." Retrieved chunks mention the HS code and duty but not BIS. Claims supported = 2/3, recall = 0.67; the missing BIS chunk shows the retriever needs a larger k or better chunking. **Amazon-style**: product Q&A misses the "return policy" chunk.

## 🟡 Real Example Hindi mein
**Tariff System**: Reference: "Lithium-ion packs HS 8507.60 में आते हैं। Basic duty 20 percent है। BIS certificate ज़रूरी है।" Retrieved chunks में HS code और duty हैं पर BIS नहीं। Supported claims = 2/3, recall = 0.67; BIS chunk छूटा, यानी k बढ़ाना या chunking सुधारना होगा। **Amazon-style**: product Q&A में "return policy" chunk miss हो गया।

---

## 💻 Code Example — Basic
```python
# Pure Python approximation of context recall (word-overlap judge instead of an LLM). Runs offline.
import re                                                     # sentence split

def claims(reference: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", reference.strip().rstrip(".!?")) if s.strip()]   # one claim per sentence

def supported(claim: str, contexts: list[str], threshold: float = 0.6) -> bool:
    words = set(claim.lower().split())                        # claim words
    for ctx in contexts:
        overlap = len(words & set(ctx.lower().split())) / len(words)   # share of claim words found
        if overlap >= threshold:
            return True                                       # supported by this chunk
    return False

def context_recall(reference: str, contexts: list[str]) -> float:
    cl = claims(reference)
    return sum(supported(c, contexts) for c in cl) / len(cl) if cl else 0.0

ref = "Lithium-ion packs fall under HS 8507.60. Basic duty is 20 percent. A BIS certificate is required."
ctx = ["Lithium-ion packs fall under HS 8507.60 as accumulators", "Basic duty is 20 percent for 8507.60"]
print(round(context_recall(ref, ctx), 2))                     # 0.67
```
This word-overlap judge is only a teaching proxy; real scoring uses an LLM judge (see Advanced).

## 💻 Code Example — Advanced
```python
# Production: LLM-as-judge context recall with JSON output, async, concurrency limit, error handling.
import asyncio                                                # async
import json                                                   # parse
import logging                                                # logs
from openai import AsyncOpenAI, OpenAIError                   # client

log = logging.getLogger("ctx_recall")                         # logger
client = AsyncOpenAI()                                        # needs OPENAI_API_KEY
sem = asyncio.Semaphore(5)                                    # limit concurrent judge calls

JUDGE = ("Given a question, a reference answer and retrieved context, split the reference into "
         "sentences. For each, say whether it can be attributed to the context. "
         'Return JSON {"verdicts":[{"sentence":str,"attributed":0|1}]}.')

async def context_recall(question: str, reference: str, contexts: list[str]) -> float:
    ctx = "\n---\n".join(contexts)                            # join chunks
    async with sem:                                           # throttle
        try:
            r = await client.chat.completions.create(
                model="gpt-4o-mini", temperature=0, max_tokens=400,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": JUDGE},
                          {"role": "user", "content": f"Question: {question}\nReference: {reference}\nContext:\n{ctx}"}])
            verdicts = json.loads(r.choices[0].message.content or "{}").get("verdicts", [])
        except (OpenAIError, json.JSONDecodeError) as exc:
            log.error("judge failed: %s", exc)
            return float("nan")                               # unknown, not zero
    if not verdicts:
        return float("nan")
    return sum(int(v.get("attributed", 0)) for v in verdicts) / len(verdicts)

async def evaluate(rows: list[dict]) -> float:
    scores = await asyncio.gather(*(context_recall(r["q"], r["ref"], r["ctx"]) for r in rows))
    valid = [s for s in scores if s == s]                     # drop NaN
    return sum(valid) / len(valid) if valid else float("nan")
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                                   # app
from pydantic import BaseModel                                # models

app = FastAPI()                                               # app

class Row(BaseModel):
    question: str                                             # question
    reference: str                                            # ground truth
    contexts: list[str]                                       # retrieved chunks

@app.post("/eval/context-recall")
async def eval_recall(row: Row) -> dict[str, float]:
    return {"context_recall": await context_recall(row.question, row.reference, row.contexts)}
```
Use this endpoint in CI on a golden set and fail the build if the mean drops.

---

## 🔗 LangChain / LangGraph Connection
```python
# Ragas has a ready metric (needs the ragas package and an LLM wrapper):
from ragas import evaluate, EvaluationDataset                 # dataset + runner
from ragas.metrics import LLMContextRecall                    # context recall metric
from ragas.llms import LangchainLLMWrapper                    # wrap a LangChain model
from langchain_openai import ChatOpenAI                       # model

llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))    # judge LLM
ds = EvaluationDataset.from_list([{
    "user_input": "Duty on lithium battery?",
    "retrieved_contexts": ["Lithium-ion packs fall under HS 8507.60."],
    "reference": "HS 8507.60, duty 20 percent.",
}])
# result = evaluate(ds, metrics=[LLMContextRecall()], llm=llm); print(result)
# In LangGraph, log retrieved docs in state so the eval set can be built from real traces.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating without ground truth
✅ Correct: recall needs a reference answer written or verified by an expert.

```python
# Wrong
context_recall(question, "", contexts)  # empty reference
# Right
context_recall(question, reference_from_expert, contexts)
```

❌ Mistake 2: Treating NaN/failed judge as 0
✅ Correct: exclude or retry.

```python
# Wrong
score = 0.0  # on error
# Right
score = float("nan")  # filter NaNs when averaging
```

---

## 🧠 Tricky Interview Question
**Q**: "Context recall is 1.0 but answers are still wrong. How?"

**Answer**: Recall only says needed info was present somewhere in the context. The generator may still ignore it (low faithfulness/answer correctness), the right chunk may be buried in noise (low precision, lost in the middle), or the reference itself may be wrong. Check precision, faithfulness and answer correctness together.

---

## ⚫ Interview Questions + Answers

Q1: What does context recall measure? (Easy)
A1: Whether retrieved context covers everything in the ground-truth answer.

Q2: Does it need ground truth? (Easy)
A2: Yes, a reference answer is required.

Q3: Recall vs precision? (Medium)
A3: Recall: did we retrieve all needed info. Precision: is the retrieved info (and ranking) relevant, with little noise.

Q4: How to raise a low recall? (Medium)
A4: Increase k, improve chunking and overlap, hybrid search, query rewriting, better embeddings, metadata filters.

Q5: How do you build a trustworthy golden set? (Hard)
A5: Sample real queries, have domain experts write references, version the set, cover edge cases, re-run on each retriever change, and track confidence intervals because LLM judges are noisy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tuning the retriever
- Regression testing RAG

❌ Avoid when:
- No reference answers available (use faithfulness/relevancy instead)

---

## 📊 Visual Diagram
```
 reference: [claim1][claim2][claim3]
                │       │       │
 retrieved ctx: ✔       ✔       ✘
 recall = 2/3 = 0.67  -> retriever missed claim3
```

---

## 💰 Cost Impact
One judge call per row: about 500-1000 input tokens plus 100-200 output. With gpt-4o-mini that is about $0.0002 per row, so 500 rows is about $0.10. Optimise: evaluate samples, use a cheap judge, cache results for unchanged rows, run nightly rather than per commit.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context recall | Coverage of needed info | ज़रूरी info का coverage |
| Reference | Ground-truth answer | सही जवाब |
| Claim | Atomic statement | एक छोटा कथन |
| Attributed | Supported by context | context से समर्थित |
| LLM judge | LLM that scores | scoring करने वाला LLM |

---

## ⚡ 3-Line Summary
English: Context recall = share of reference claims found in retrieved context. It tests the retriever, not the generator. It needs ground-truth answers.
Hindi: Context recall = reference के कितने claims retrieved context में मिले। ये retriever को test करता है, generator को नहीं। इसके लिए ground-truth जवाब चाहिए।

---

## ➡️ Next Topic
**395. Context Relevancy** - how much of the retrieved context is actually relevant (noise check).
