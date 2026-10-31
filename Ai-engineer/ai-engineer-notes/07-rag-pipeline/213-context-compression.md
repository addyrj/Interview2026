---

# 213. Context Compression
# हिंदी में: Context Compression

---

## 🔵 Simple Definition (English)
Context compression shrinks retrieved chunks before they reach the LLM, keeping only the sentences or facts that matter for the question. You can extract, filter, or summarise. The result: fewer tokens, less noise, same or better answer.

## 🔵 सरल परिभाषा (Hindi)
Context compression retrieved chunks को LLM तक पहुँचने से पहले छोटा करता है और सिर्फ़ वही sentences या facts रखता है जो सवाल के लिए ज़रूरी हैं। आप extract, filter या summarise कर सकते हैं। नतीजा: कम tokens, कम noise, वही या बेहतर answer।

---

## 🔴 Problem it Solves
A chunk of 500 tokens often has only 1-2 relevant sentences. The rest is noise that costs money, adds latency, and distracts the LLM. Compression removes that noise so you can include more distinct sources in the same budget.

## 🔴 यह क्यों बना? (Hindi)
500 tokens के chunk में अक्सर सिर्फ़ 1-2 sentences काम के होते हैं। बाकी noise है जो पैसे खर्च करता है, latency बढ़ाता है और LLM को distract करता है। Compression noise हटाता है ताकि उसी budget में ज़्यादा अलग sources आ सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Retrieve (and rerank) the top chunks
Step 2 → Choose a compressor:
         a) Extractive : keep only sentences similar to the query (cheap, no LLM)
         b) LLM extract: LLM copies only relevant spans (accurate, costs tokens)
         c) Filter     : drop whole chunks judged irrelevant
         d) Abstractive: LLM summarises (shortest, risk of losing exact numbers)
Step 3 → Apply per chunk, keep the source id with the compressed text
Step 4 → Drop empty results
Step 5 → Check the compressed size against the token budget
Step 6 → Send compressed context to the final LLM
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Top chunks retrieve (और rerank) करो
Step 2 → Compressor चुनो:
         a) Extractive : query से मिलते sentences रखो (सस्ता, LLM नहीं)
         b) LLM extract: LLM सिर्फ़ relevant spans copy करता है (accurate, tokens लगते हैं)
         c) Filter     : irrelevant पूरे chunks हटाओ
         d) Abstractive: LLM summary बनाता है (सबसे छोटा, exact numbers खोने का risk)
Step 3 → हर chunk पर लगाओ, source id साथ रखो
Step 4 → खाली results हटाओ
Step 5 → Compressed size को token budget से check करो
Step 6 → Compressed context final LLM को भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A 600-token chunk of Chapter 85 contains a long preamble, exceptions, and one line: "Smartphones, HS 8517.13, 20 percent". Extractive compression keeps that line and the exception line mentioning "refurbished", reducing 600 tokens to 80. **Zomato**: a long restaurant policy compressed to "refund within 7 days for cold food". **Amazon**: 50 reviews compressed to the sentences that mention battery.

## 🟡 Real Example Hindi mein
**Tariff System**: Chapter 85 के 600-token chunk में लंबा preamble, exceptions और एक line है: "Smartphones, HS 8517.13, 20 percent"। Extractive compression वह line और "refurbished" वाली exception line रखता है; 600 tokens घटकर 80। **Zomato**: लंबी policy घटकर "ठंडे खाने पर 7 दिन में refund"। **Amazon**: 50 reviews में से सिर्फ़ battery वाले sentences।

---

## 💻 Code Example — Basic
```python
# Pure Python extractive compression: keep sentences that share words with the query.
import re  # sentence splitting
from typing import List  # type hints

STOP = {"the", "a", "of", "is", "for", "on", "and", "to", "in"}  # tiny stopword list


def words(text: str) -> set:
    """Lowercase content words without stopwords."""
    return {w for w in re.findall(r"[a-z0-9\.]+", text.lower()) if w not in STOP}  # set of words


def compress(query: str, chunk: str, max_sentences: int = 2) -> str:
    """Keep the top sentences by overlap with the query, in original order."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", chunk) if s.strip()]  # split sentences
    q = words(query)  # query words
    scored = sorted(range(len(sentences)), key=lambda i: len(q & words(sentences[i])), reverse=True)  # rank indexes
    keep = sorted(i for i in scored[:max_sentences] if q & words(sentences[i]))  # drop zero-overlap, restore order
    return " ".join(sentences[i] for i in keep)  # compressed text (may be empty)


if __name__ == "__main__":
    chunk = (
        "Chapter 85 covers electrical machinery. Many items have special notes. "
        "Smartphones HS 8517.13 attract 20 percent duty. Refurbished smartphones need a licence. "
        "Annual reviews are published each March."
    )
    out = compress("duty on smartphones", chunk)  # compress
    print(len(chunk), "->", len(out), "chars")  # size change
    print(out)  # compressed text
```

## 💻 Code Example — Advanced
```python
# Production: LLM extractive compression in parallel, with budget, fallback and token tracking.
import asyncio  # concurrency
import logging  # logs

from openai import AsyncOpenAI  # openai>=1

logger = logging.getLogger("compress")  # logger
client = AsyncOpenAI()  # env key
NO_INFO = "NO_RELEVANT_INFO"  # sentinel for irrelevant chunks


async def compress_one(query: str, chunk: str, sem: asyncio.Semaphore) -> tuple[str, int]:
    """Return (compressed_text, tokens_used). Falls back to the original chunk on error."""
    async with sem:  # limit concurrent API calls
        try:  # API may fail
            resp = await client.chat.completions.create(  # call model
                model="gpt-4o-mini", temperature=0, max_tokens=200,  # cheap, deterministic, capped
                messages=[
                    {"role": "system", "content": f"Copy ONLY the sentences from the passage that help answer the question, verbatim. If none, output {NO_INFO}."},
                    {"role": "user", "content": f"Question: {query}\n\nPassage:\n{chunk}"},
                ],
            )
            text = (resp.choices[0].message.content or "").strip()  # model output
            tokens = resp.usage.total_tokens if resp.usage else 0  # usage
            return text, tokens  # result
        except Exception as exc:  # fallback keeps the pipeline alive
            logger.warning("compress failed: %s", exc)  # log
            return chunk, 0  # use original chunk


async def compress_all(query: str, chunks: list[str], concurrency: int = 5) -> tuple[list[str], int]:
    """Compress all chunks in parallel, drop irrelevant ones, return total tokens spent."""
    sem = asyncio.Semaphore(concurrency)  # concurrency cap
    results = await asyncio.gather(*(compress_one(query, c, sem) for c in chunks))  # parallel
    kept = [t for t, _ in results if t and NO_INFO not in t]  # drop empty/irrelevant
    return kept, sum(tok for _, tok in results)  # texts + cost
```

---

## 🟠 FastAPI Integration
Compress after reranking and before the final call. Return before/after token counts so you can track savings.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Req(BaseModel):
    question: str  # question


@app.post("/ask")  # route
async def ask(req: Req) -> dict:
    chunks = ["long chunk 1 ...", "long chunk 2 ..."]  # reranked top chunks
    compressed, spent = await compress_all(req.question, chunks)  # compress
    return {"chunks_in": len(chunks), "chunks_out": len(compressed), "compression_tokens": spent}  # report
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's compressors plug into `ContextualCompressionRetriever`: `LLMChainExtractor` (LLM extracts relevant parts), `LLMChainFilter` (drops irrelevant docs), and `EmbeddingsFilter` (drops docs with low similarity, no LLM).

```python
from langchain.retrievers import ContextualCompressionRetriever  # wrapper
from langchain.retrievers.document_compressors import EmbeddingsFilter, LLMChainExtractor  # compressors
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # models

# cheap = EmbeddingsFilter(embeddings=OpenAIEmbeddings(), similarity_threshold=0.76)  # no LLM, fast
# smart = LLMChainExtractor.from_llm(ChatOpenAI(model="gpt-4o-mini", temperature=0))  # LLM extract
# retriever = ContextualCompressionRetriever(base_compressor=smart, base_retriever=base)
# docs = await retriever.ainvoke("duty on smartphones")  # compressed Documents
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Abstractive summaries for numbers and legal text
✅ Correct: Use extractive (verbatim) compression where exact values matter.

```python
# Wrong: summary may turn "20 percent" into "around 20 percent" or lose a clause
summary = llm("Summarise this tariff passage")

# Right: verbatim sentences
extract = llm("Copy only the relevant sentences verbatim")
```

❌ Mistake 2: Compression that costs more than it saves
✅ Correct: Compare tokens: compression call cost vs tokens removed.

```python
# Wrong: 5 LLM calls x 600 input tokens just to save 1,500 tokens of final prompt
# Right: use a cheap embeddings/sentence filter first; use LLM extraction only for high-value queries
```

---

## 🧠 Tricky Interview Question
**Q**: "After adding LLM compression, token cost on the final call fell 60 percent but total cost per query went UP. Why?"

**Answer**: The compression step itself reads all original chunks (input tokens) and writes extracts (output tokens), per chunk. If you compress 10 chunks of 500 tokens, you spent about 5,000 input tokens just to compress, which can exceed the savings, and output tokens are priced higher. Fix: compress fewer chunks (after reranking), use a cheaper model, use non-LLM extractive filters, or skip compression when chunks are already short.

---

## ⚫ Interview Questions + Answers

Q1: What is context compression?
A1: Reducing retrieved text to only what is relevant before sending it to the LLM.

Q2: Name two compression styles.
A2: Extractive (keep original sentences) and abstractive (summarise).

Q3: Why can compression improve accuracy?
A3: Less noise and distraction, and less "lost in the middle" effect.

Q4: What are the risks?
A4: Losing needed details (conditions, exceptions), hallucinated summaries, extra latency and cost, and broken citation offsets.

Q5: How do you keep citations working after compression?
A5: Carry chunk id and metadata with every compressed fragment, prefer verbatim extraction so you can map back to character offsets, and display the original chunk when the user opens a source.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chunks are long and mostly noise
- Many sources must fit a tight budget
- Token cost is a concern at scale

❌ Avoid when:
- Chunks are already short and precise
- Exact legal wording is critical and you cannot risk any cut (use verbatim only)
- Latency is very tight

---

## 📊 Visual Diagram
```
 chunk (600 tokens)
 ┌──────────────────────────────────────────────┐
 │ preamble.... notes.... [KEY LINE] ...appendix │
 └──────────────────────────────────────────────┘
          │ compressor (query = "duty on smartphones")
          ▼
 ┌────────────────────┐
 │ [KEY LINE] (80 tok)│   ← 87 percent smaller
 └────────────────────┘
```

---

## 💰 Cost Impact
- Savings: final-call input tokens drop by the compression ratio (e.g. 5 chunks x 500 = 2,500 down to about 500).
- Cost: LLM-based compression adds tokens (read all chunks, write extracts); embedding/sentence filters add near zero.
- Rule: use LLM compression only when savings x number of final calls exceeds the compression cost; otherwise prefer extractive filters.
- Optimise: compress after reranking, small model, cache by (query, chunk id), concurrency limit.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compression | Make context smaller | Context छोटा करना |
| Extractive | Copy original sentences | Original sentences निकालना |
| Abstractive | Rewrite as summary | Summary में दोबारा लिखना |
| Verbatim | Word-for-word | शब्दशः |
| Compression ratio | Output size / input size | छोटा होने का अनुपात |

---

## ⚡ 3-Line Summary
English: Context compression keeps only the relevant parts of retrieved chunks. It cuts noise and tokens, but LLM-based compression has its own cost. Prefer verbatim extraction for exact data like duties and codes.
Hindi: Context compression retrieved chunks के सिर्फ़ relevant हिस्से रखता है। यह noise और tokens घटाता है, पर LLM-based compression का अपना cost है। Duty और codes जैसे exact data के लिए verbatim extraction चुनो।

---

## ➡️ Next Topic
**214. Lost in Middle — Fix** — even compressed context fails if the key chunk is buried; learn how to order it.
