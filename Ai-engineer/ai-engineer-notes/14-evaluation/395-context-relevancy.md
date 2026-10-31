---

# 395. Context Relevancy
# हिंदी में: Context Relevancy

---

## 🔵 Simple Definition (English)
Context relevancy measures how much of the retrieved context is actually relevant to the question. Score = relevant sentences (or chunks) / total retrieved. It needs no ground-truth answer and catches noisy retrieval.

## 🔵 सरल परिभाषा (Hindi)
Context relevancy मापता है कि retrieved context का कितना हिस्सा सवाल से सच में relevant है। Score = relevant sentences (या chunks) / कुल retrieved। इसे ground-truth जवाब नहीं चाहिए और ये noisy retrieval पकड़ता है।

---

## 🔴 Problem it Solves
Retrieving 10 chunks where only 2 matter wastes tokens, raises cost and confuses the model. Context relevancy exposes retrieval noise even when you have no reference answers.

## 🔴 यह क्यों बना? (Hindi)
10 chunks retrieve करना जिनमें सिर्फ़ 2 काम के हैं, tokens बर्बाद करता है, cost बढ़ाता है और model को confuse करता है। Context relevancy बिना reference जवाबों के भी retrieval noise दिखा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take question + retrieved contexts (no reference needed)
Step 2 → Split contexts into sentences/chunks
Step 3 → Judge each: is it needed to answer the question?
Step 4 → relevant_count / total_count = score
Step 5 → (Ragas variant) ask the judge to rate 0, 1 or 2 per context and normalise
Step 6 → Low score -> reduce k, add reranker, better chunk size
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Question + retrieved contexts लो (reference नहीं चाहिए)
Step 2 → Contexts को sentences/chunks में बाँटो
Step 3 → हर एक judge करो: क्या जवाब देने के लिए ज़रूरी है?
Step 4 → relevant_count / total_count = score
Step 5 → (Ragas variant) judge से हर context को 0, 1 या 2 rating दिलाओ और normalise करो
Step 6 → Score कम हो तो k घटाओ, reranker लगाओ, chunk size सुधारो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Question "Duty on lithium battery?" retrieves 5 chunks: battery HS code, battery duty, a chapter on textiles, shipping insurance, and customs history. Relevant 2/5 = 0.4. A reranker plus k=3 lifts it to 0.67 and cuts tokens 40 percent. **Zomato-style**: a refund question retrieves restaurant menu chunks - irrelevant noise.

## 🟡 Real Example Hindi mein
**Tariff System**: सवाल "Lithium battery पर duty?" 5 chunks लाता है: battery HS code, battery duty, textiles का chapter, shipping insurance, customs history। Relevant 2/5 = 0.4। Reranker और k=3 से score 0.67 और tokens 40 percent कम। **Zomato-style**: refund सवाल पर restaurant menu chunks आ गए - noise।

---

## 💻 Code Example — Basic
```python
# Pure Python approximation: fraction of chunks sharing enough words with the question. Offline.
STOP = {"the", "on", "a", "of", "is", "what", "for", "and", "to", "in"}   # ignore these words

def keywords(text: str) -> set[str]:
    return {w for w in text.lower().replace("?", "").split() if w not in STOP}

def context_relevancy(question: str, contexts: list[str]) -> float:
    q = keywords(question)                                    # question keywords
    if not contexts or not q:
        return 0.0
    relevant = sum(1 for c in contexts if len(q & keywords(c)) >= 1)   # chunk shares a keyword
    return relevant / len(contexts)

q = "duty on lithium battery?"
ctx = ["lithium battery HS 8507.60", "battery duty is 20 percent",
       "cotton textiles chapter 52", "marine insurance rules"]
print(context_relevancy(q, ctx))                              # 0.5
```
This is a crude proxy to show the formula; real systems use an LLM judge.

## 💻 Code Example — Advanced
```python
# Production: per-chunk LLM relevance judging, async + bounded concurrency + retries.
import asyncio                                                # async
import logging                                                # logs
from openai import AsyncOpenAI, OpenAIError, RateLimitError   # client + errors

log = logging.getLogger("ctx_rel")                            # logger
client = AsyncOpenAI()                                        # needs OPENAI_API_KEY
sem = asyncio.Semaphore(8)                                    # throttle

async def judge_chunk(question: str, chunk: str, retries: int = 3) -> int | None:
    prompt = (f"Question: {question}\nChunk: {chunk}\n"
              "Is the chunk useful to answer the question? Reply with exactly 1 or 0.")
    for attempt in range(retries):
        try:
            async with sem:
                r = await client.chat.completions.create(
                    model="gpt-4o-mini", temperature=0, max_tokens=2,
                    messages=[{"role": "user", "content": prompt}])
            out = (r.choices[0].message.content or "").strip()
            return 1 if out.startswith("1") else 0
        except RateLimitError:
            await asyncio.sleep(2 ** attempt)                 # exponential backoff
        except OpenAIError as exc:
            log.error("judge error: %s", exc)
            return None                                       # unknown
    return None

async def context_relevancy(question: str, contexts: list[str]) -> float:
    verdicts = await asyncio.gather(*(judge_chunk(question, c) for c in contexts))
    valid = [v for v in verdicts if v is not None]
    return sum(valid) / len(valid) if valid else float("nan")
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                                   # app
from pydantic import BaseModel                                # model

app = FastAPI()                                               # app

class In(BaseModel):
    question: str                                             # question
    contexts: list[str]                                       # retrieved chunks

@app.post("/eval/context-relevancy")
async def endpoint(body: In) -> dict[str, float]:
    return {"context_relevancy": await context_relevancy(body.question, body.contexts)}
```
Run it on a sample (e.g. 5 percent) of production traffic to monitor retrieval drift.

---

## 🔗 LangChain / LangGraph Connection
```python
# Ragas ships a "ContextRelevance" metric (NVIDIA-style, 0-1) and "LLMContextPrecisionWithoutReference".
from ragas import evaluate, EvaluationDataset                 # runner
from ragas.metrics import ContextRelevance                    # relevancy metric
from ragas.llms import LangchainLLMWrapper                    # LLM wrapper
from langchain_openai import ChatOpenAI                       # model

llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
ds = EvaluationDataset.from_list([{
    "user_input": "Duty on lithium battery?",
    "retrieved_contexts": ["Lithium-ion packs: HS 8507.60", "Cotton textiles chapter 52"],
}])
# result = evaluate(ds, metrics=[ContextRelevance()], llm=llm)
# Metric names change across Ragas versions - check the docs for yours.
# LangGraph tip: add a grader node that filters irrelevant docs before generation (Corrective RAG).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing it up with context recall
✅ Correct: relevancy = noise check (no reference); recall = completeness check (reference).

```python
# Wrong
# use context_relevancy to prove nothing was missed
# Right
# use context_recall for missing info; relevancy for extra noise
```

❌ Mistake 2: Judging at the chunk level only
✅ Correct: large chunks may be half relevant; judge at sentence level for precision.

```python
# Wrong
judge(chunk)
# Right
[judge(s) for s in split_sentences(chunk)]
```

---

## 🧠 Tricky Interview Question
**Q**: "You reduced k from 10 to 3 and relevancy rose from 0.3 to 0.7, but answer quality dropped. Why?"

**Answer**: Relevancy only measures noise, not completeness. Cutting k removed useful chunks too (recall fell). Always track relevancy/precision together with recall and answer correctness; better to rerank 10 then keep top 3.

---

## ⚫ Interview Questions + Answers

Q1: What is context relevancy? (Easy)
A1: Share of retrieved context that is relevant to the question.

Q2: Does it need ground truth? (Easy)
A2: No, only question and contexts.

Q3: How is it different from context precision? (Medium)
A3: Precision also considers ranking (relevant chunks should come first), usually using references; relevancy is a simpler share of relevant content.

Q4: Why does low relevancy raise cost? (Medium)
A4: Irrelevant chunks are paid for as input tokens on every call and can distract the model.

Q5: How would you improve it? (Hard)
A5: Reranker, smaller chunks, metadata filters, query rewriting, score threshold instead of fixed k, and a grader node that drops irrelevant docs; verify with recall so completeness does not suffer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Monitoring production without labels
- Tuning k and chunking

❌ Avoid relying on it alone when:
- Completeness matters (add recall)

---

## 📊 Visual Diagram
```
 retrieved: [A✔][B✔][C✘][D✘][E✘]   relevancy = 2/5 = 0.4
 after rerank + k=3: [A✔][B✔][C✘]   relevancy = 2/3 = 0.67, fewer tokens
```

---

## 💰 Cost Impact
Evaluation: one tiny call per chunk (about 150 tokens each, roughly $0.00003). Bigger payoff: each irrelevant 300-token chunk removed from production saves 300 input tokens per query; at 1M queries/month with 3 chunks removed that is about 900M tokens, about $135 on gpt-4o-mini input pricing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context relevancy | Share of useful context | काम के context का हिस्सा |
| Noise | Irrelevant retrieved text | बेकार retrieved text |
| Reranker | Re-orders by relevance | relevance से क्रम बदलने वाला |
| Grader | LLM that filters docs | docs छाँटने वाला LLM |
| Reference-free | No ground truth needed | बिना ground truth |

---

## ⚡ 3-Line Summary
English: Context relevancy = relevant retrieved text / all retrieved text. It needs no ground truth and finds noisy retrieval. Pair it with recall.
Hindi: Context relevancy = relevant retrieved text / कुल retrieved text। इसे ground truth नहीं चाहिए और ये noisy retrieval पकड़ता है। इसे recall के साथ इस्तेमाल करो।

---

## ➡️ Next Topic
**396. Answer Correctness** - judging the final answer against the ground truth.
