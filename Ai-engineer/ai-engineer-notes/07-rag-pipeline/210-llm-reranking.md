---

# 210. LLM Reranking
# हिंदी में: LLM Reranking

---

## 🔵 Simple Definition (English)
LLM reranking asks a general chat model to judge or sort retrieved chunks by relevance. It can follow detailed instructions ("prefer the latest notification, ignore draft rules"), which trained rerankers cannot. It is slower and costs tokens.

## 🔵 सरल परिभाषा (Hindi)
LLM reranking में एक general chat model से कहा जाता है कि retrieved chunks को relevance के हिसाब से judge या sort करे। यह detailed instructions ("सबसे नया notification चुनो, draft rules छोड़ो") follow कर सकता है, जो trained rerankers नहीं कर पाते। यह धीमा है और tokens खर्च करता है।

---

## 🔴 Problem it Solves
Cross-encoders only know generic relevance. Real domains need rules: effective dates, jurisdiction, exceptions, "must mention a HS code". An LLM can reason over these. It is also useful when you have no labelled data to fine-tune a reranker, or the query needs reasoning to decide relevance.

## 🔴 यह क्यों बना? (Hindi)
Cross-encoder सिर्फ़ generic relevance जानते हैं। Real domains में rules होते हैं: effective dates, jurisdiction, exceptions। LLM इन पर reason कर सकता है। जब fine-tune के लिए labelled data नहीं हो, या relevance तय करने में reasoning लगे, तब भी यह काम आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Retrieve top-N chunks (N = 10-30, small, because tokens cost money)
Step 2 → Pick a strategy:
         a) Pointwise : score each chunk 0-10 independently
         b) Listwise  : give all chunks, ask for the ranked list of ids
Step 3 → Ask for STRUCTURED output (JSON with ids and scores), temperature 0
Step 4 → Parse + validate (ids must exist, no duplicates)
Step 5 → Sort / keep top-K, fall back to retrieval order on failure
Step 6 → Build final prompt with kept chunks
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Top-N chunks लाओ (N = 10-30, छोटा, क्योंकि tokens महँगे हैं)
Step 2 → Strategy चुनो:
         a) Pointwise : हर chunk को अलग 0-10 score
         b) Listwise  : सारे chunks देकर ranked ids की list माँगो
Step 3 → STRUCTURED output (JSON) माँगो, temperature 0
Step 4 → Parse + validate करो (ids मौजूद हों, duplicates नहीं)
Step 5 → Sort करके top-K रखो, fail हो तो retrieval order पर fallback
Step 6 → रखे हुए chunks से final prompt बनाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "duty on imported solar panels". Retrieved chunks include an old 2019 notification and the 2024 amendment. The rerank prompt says: "Prefer chunks with the latest effective date; penalise superseded rules." The LLM puts the 2024 amendment first, which a cross-encoder cannot do since it has no concept of dates. **Zomato**: rank restaurants by "best for a quiet date, not too spicy". **Amazon**: rank reviews by usefulness to a specific question.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "imported solar panels पर duty"। Retrieved chunks में 2019 का पुराना notification और 2024 का amendment है। Rerank prompt कहता है: "सबसे नई effective date वाले chunks को प्राथमिकता दो; superseded rules को नीचे रखो।" LLM 2024 amendment को पहले रखता है; cross-encoder dates नहीं समझता। **Zomato**: "शांत date के लिए, ज़्यादा तीखा नहीं" के हिसाब से restaurants rank। **Amazon**: किसी सवाल के लिए सबसे काम के reviews।

---

## 💻 Code Example — Basic
```python
# Basic: pointwise LLM-style reranking with a mock "LLM" so it runs offline.
import json  # parse model output
from typing import Dict, List  # type hints

CHUNKS: Dict[int, str] = {  # id -> chunk text
    1: "Solar panels HS 8541 duty 40 percent (notification 2019, superseded)",
    2: "Solar panels HS 8541 duty 20 percent (amendment 2024, effective)",
    3: "Solar water heaters HS 8419 duty 7.5 percent",
}


def mock_llm(prompt: str) -> str:
    """Pretend LLM: rewards 'effective' and 'solar panels', penalises 'superseded'."""
    scores: Dict[str, int] = {}  # id -> score
    for line in prompt.splitlines():  # each chunk line looks like "[1] text"
        if line.startswith("["):  # a chunk line
            cid = line[1:line.index("]")]  # extract id
            s = 5  # base score
            s += 3 if "effective" in line else 0  # prefer current
            s -= 4 if "superseded" in line else 0  # demote old
            s += 2 if "Solar panels" in line else 0  # topic match
            scores[cid] = max(0, min(10, s))  # clamp 0-10
    return json.dumps({"scores": scores})  # JSON like a real LLM would return


def llm_rerank(query: str, chunks: Dict[int, str], top_k: int = 2) -> List[int]:
    """Build prompt, call model, parse JSON, sort ids."""
    body = "\n".join(f"[{i}] {t}" for i, t in chunks.items())  # numbered chunks
    prompt = f"Query: {query}\nScore each chunk 0-10, prefer latest rules.\n{body}"  # prompt
    try:  # JSON may be broken
        data = json.loads(mock_llm(prompt))  # call + parse
        scores = {int(k): float(v) for k, v in data["scores"].items()}  # typed scores
    except (json.JSONDecodeError, KeyError, ValueError):  # bad output
        return list(chunks)[:top_k]  # fallback order
    return sorted(scores, key=scores.get, reverse=True)[:top_k]  # best ids


if __name__ == "__main__":
    ids = llm_rerank("duty on imported solar panels", CHUNKS)  # run
    for i in ids:  # print winners
        print(i, CHUNKS[i])  # id and text
```

## 💻 Code Example — Advanced
```python
# Production: listwise reranking with structured output, async, validation and fallback.
import logging  # logs
from typing import List  # typing

from openai import AsyncOpenAI  # openai>=1
from pydantic import BaseModel, Field  # pydantic v2

logger = logging.getLogger("llm_rerank")  # logger
client = AsyncOpenAI()  # env OPENAI_API_KEY


class Ranking(BaseModel):
    """LLM must return chunk ids, best first."""
    ranked_ids: List[int] = Field(description="Chunk ids ordered most to least relevant")


async def llm_rerank(query: str, chunks: dict[int, str], top_k: int = 5, model: str = "gpt-4o-mini") -> list[int]:
    """Listwise rerank; returns validated ids, falls back to input order."""
    fallback = list(chunks)[:top_k]  # safe default
    if len(chunks) <= 1:  # nothing to sort
        return fallback  # return
    body = "\n".join(f"[{i}] {t[:600]}" for i, t in chunks.items())  # truncate chunks to save tokens
    try:  # API/parse can fail
        resp = await client.beta.chat.completions.parse(  # structured output
            model=model,  # cheap model
            messages=[
                {"role": "system", "content": "Rank passages by how well they answer the query. Prefer the most recent effective rule. Return ids only."},
                {"role": "user", "content": f"Query: {query}\n\nPassages:\n{body}"},
            ],
            response_format=Ranking,  # schema
            temperature=0,  # deterministic
            max_tokens=100,  # ids are short
        )
        parsed = resp.choices[0].message.parsed  # typed or None
        if parsed is None:  # refusal
            return fallback  # fallback
        seen: set[int] = set()  # de-dup
        ids = [i for i in parsed.ranked_ids if i in chunks and not (i in seen or seen.add(i))]  # validate ids
        ids += [i for i in chunks if i not in seen]  # append any the model forgot
        return ids[:top_k]  # final list
    except Exception as exc:  # network etc.
        logger.warning("llm rerank failed: %s", exc)  # log
        return fallback  # fallback
```

---

## 🟠 FastAPI Integration
Use LLM reranking only for hard or high-value queries (a "deep mode" flag), to protect latency and cost.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Req(BaseModel):
    query: str  # question
    deep: bool = False  # enable LLM rerank


@app.post("/retrieve")  # route
async def retrieve(req: Req) -> dict:
    chunks = {1: "chunk A", 2: "chunk B", 3: "chunk C"}  # from vector search
    ids = await llm_rerank(req.query, chunks) if req.deep else list(chunks)  # optional rerank
    return {"ids": ids, "reranked": req.deep}  # response
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `LLMChainFilter` and `LLMChainExtractor` (keep or trim docs using an LLM) in `langchain.retrievers.document_compressors`. For listwise ranking, build your own LCEL chain with `with_structured_output`.

```python
from langchain.retrievers.document_compressors import LLMChainFilter  # LLM yes/no filter
from langchain_openai import ChatOpenAI  # model

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # judge model
# compressor = LLMChainFilter.from_llm(llm)  # keeps only relevant docs
# retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base)
# LangGraph: node `rerank` calls the LLM and writes ranked docs into state["docs"].
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Free-text output you parse with regex
✅ Correct: Use structured output (JSON schema / pydantic).

```python
# Wrong: "The best are 2, then 1 and maybe 3" -> fragile regex
ids = [int(x) for x in re.findall(r"\d+", text)]

# Right: schema-enforced
resp = await client.beta.chat.completions.parse(..., response_format=Ranking)
```

❌ Mistake 2: Sending 100 full chunks
✅ Correct: Rerank only top 10-20 and truncate each chunk.

```python
# Wrong: 100 x 500 tokens = 50k tokens per query
body = "\n".join(all_100_chunks)

# Right: 15 x 150 tokens = about 2k tokens
body = "\n".join(f"[{i}] {t[:600]}" for i, t in top15.items())
```

---

## 🧠 Tricky Interview Question
**Q**: "Your LLM reranker is accurate but ranks the same chunk differently across runs, and prefers whichever chunk is listed first. What is going on and how do you fix it?"

**Answer**: LLMs have position bias and sampling randomness. Fix: temperature 0, shuffle input order and average over 2-3 passes (or run pointwise scoring where each chunk is judged alone), use clear scoring rubrics, ask for structured output, and check with a labelled set. For stable production use, distil the LLM judgements into a smaller cross-encoder trained on its labels.

---

## ⚫ Interview Questions + Answers

Q1: What is LLM reranking?
A1: Asking an LLM to score or order retrieved chunks by relevance to the query.

Q2: Pointwise vs listwise?
A2: Pointwise scores each chunk alone (parallel, stable, more calls). Listwise ranks all chunks in one prompt (cheaper, but position bias and context length limits).

Q3: Why use an LLM instead of a cross-encoder?
A3: It follows custom instructions and can reason (dates, exceptions, jurisdictions) without training data.

Q4: What are the downsides?
A4: Higher latency and cost, nondeterminism, position bias, prompt injection risk from chunk text.

Q5: How do you protect against prompt injection in chunks during reranking?
A5: Put chunks in clearly delimited data blocks, instruct the model to treat them only as data, use structured output (ids only, so injected text cannot produce arbitrary content), validate that returned ids exist, and never pass tools to the rerank call. Strip suspicious instructions in ingestion if needed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Rules beyond similarity (recency, authority, jurisdiction)
- Low volume, high value queries
- No labelled data for a trained reranker

❌ Avoid when:
- High QPS and tight latency
- Simple relevance is enough (use cross-encoder/Cohere)
- Strong need for reproducible scores

---

## 📊 Visual Diagram
```
 top-15 chunks ──► [Prompt: query + rubric + numbered chunks]
                          │
                          ▼
                 ┌─────────────────┐
                 │ LLM (temp = 0)  │  ~2,000 input tokens
                 └────────┬────────┘
                          ▼
              {"ranked_ids": [2, 1, 3, ...]}
                          │ validate ids
                          ▼
                  top-5 → final answer prompt
```

---

## 💰 Cost Impact
- Cost = tokens of all candidate chunks + query + rubric (input) + a few output tokens.
- Example: 15 chunks x 150 tokens + 100 = about 2,350 input tokens. At gpt-4o-mini input price (check the current price list) this is a fraction of a cent, but multiply by traffic.
- Optimise: truncate chunks, rerank only N=10-15, use a small model, use pointwise with cached scores per (query-hash, chunk-id), route only hard queries, or distil into a cross-encoder.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pointwise | Score one chunk at a time | एक-एक chunk का score |
| Listwise | Rank the whole list at once | पूरी list एक साथ rank |
| Position bias | LLM favours early items | शुरुआती items को पसंद करना |
| Rubric | Scoring instructions | Scoring के नियम |
| Distillation | Teach small model from big one | बड़े model से छोटे को सिखाना |

---

## ⚡ 3-Line Summary
English: LLM reranking lets a chat model sort chunks using custom rules and reasoning. It is flexible but slow, costly and a bit random. Use structured output, small N, and a fallback.
Hindi: LLM reranking में chat model custom rules और reasoning से chunks sort करता है। यह flexible है पर धीमा, महँगा और थोड़ा random है। Structured output, छोटा N और fallback रखो।

---

## ➡️ Next Topic
**211. RAG Prompt Template** — once chunks are chosen, how to write the prompt that makes the LLM use them correctly.
