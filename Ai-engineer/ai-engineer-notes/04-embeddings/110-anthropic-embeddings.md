---

# 110. Anthropic Embeddings — Complete Guide
# हिंदी में: Anthropic Embeddings — पूरी Guide

---

## 🔵 Simple Definition (English)
Anthropic (the maker of Claude) does **not** offer its own embedding model. Its documentation recommends **Voyage AI** for embeddings to use alongside Claude. So "Anthropic embeddings" in practice means: use Claude for generation and Voyage (or another provider) for vectors.

## 🔵 सरल परिभाषा (Hindi)
Anthropic (Claude बनाने वाली company) का अपना embedding model **नहीं** है। उनकी documentation embeddings के लिए **Voyage AI** recommend करती है। यानी practice में: generation के लिए Claude, vectors के लिए Voyage (या कोई और provider)।

---

## 🔴 Problem it Solves
A common interview trap: people assume Claude has an `embeddings.create` endpoint. It does not. Teams building RAG on Claude need a clear answer for retrieval. Voyage models (such as `voyage-3`, `voyage-3-large`, `voyage-3-lite`, `voyage-code-3`, `voyage-law-2`) provide high-quality general and domain-specific embeddings, with `input_type` for query vs document.

(Model names change often; always check the current Voyage and Anthropic docs.)

## 🔴 यह क्यों बना? (Hindi)
Interview का आम trap: लोग मान लेते हैं कि Claude का `embeddings.create` endpoint है। नहीं है। Claude पर RAG बनाने वाली teams को retrieval के लिए साफ जवाब चाहिए। Voyage models (जैसे `voyage-3`, `voyage-code-3`, `voyage-law-2`) general और domain-specific embeddings देते हैं, और `input_type` से query व document अलग किए जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Get a Voyage API key (VOYAGE_API_KEY); pip install voyageai
Step 2 → Offline: vo.embed(docs, model="voyage-3", input_type="document")
Step 3 → Store vectors in a vector DB (dimension depends on the model)
Step 4 → Online: embed the user query with input_type="query"
Step 5 → Vector search returns top-k chunks
Step 6 → Send chunks + question to Claude (anthropic SDK messages.create)
Step 7 → Claude answers grounded in the chunks; cite sources
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Voyage API key (VOYAGE_API_KEY) लो; pip install voyageai
Step 2 → Offline: vo.embed(docs, model="voyage-3", input_type="document")
Step 3 → Vectors को vector DB में store करो
Step 4 → Online: user query को input_type="query" से embed करो
Step 5 → Vector search से top-k chunks मिलते हैं
Step 6 → Chunks + सवाल Claude को भेजो (anthropic SDK messages.create)
Step 7 → Claude chunks के आधार पर जवाब देता है; sources cite करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Ingestion embeds HS code notes with `voyage-3`. At query time the importer's description is embedded with `input_type="query"`, top-8 notes retrieved, then **Claude** decides the final HS code and explains why. Embedding provider and generation provider are different, which is normal.

**Amazon-style**: Product Q&A bot, Voyage vectors for retrieval and Claude for answer writing.

## 🟡 Real Example Hindi mein
**Tariff System**: Ingestion में HS code notes `voyage-3` से embed होते हैं। Query के समय importer का description `input_type="query"` से embed होता है, top-8 notes निकलते हैं, फिर **Claude** final HS code तय करके कारण बताता है। Embedding और generation के providers अलग हैं, यह सामान्य है।

**Amazon-style**: Product Q&A bot, retrieval के लिए Voyage vectors और जवाब लिखने के लिए Claude।

---

## 💻 Code Example — Basic
```python
# Voyage embeddings (Anthropic's recommended partner). Offline fallback included.
import os                                      # read env var
from typing import Literal                     # restrict input_type values

InputType = Literal["query", "document"]       # Voyage accepts these two


def embed(texts: list[str], input_type: InputType = "document") -> list[list[float]]:
    """Embed texts with Voyage; return a fake vector when no key is set."""
    key = os.getenv("VOYAGE_API_KEY")          # key from environment
    if not key:                                # offline demo path
        return [[float(len(t)), float(t.count(" ")), 1.0] for t in texts]
    import voyageai                            # pip install voyageai
    vo = voyageai.Client(api_key=key)          # sync client
    result = vo.embed(texts, model="voyage-3", input_type=input_type)  # API call
    print("tokens used:", result.total_tokens) # billing info
    return result.embeddings                   # list of vectors


docs = embed(["Headphones and earphones", "Coffee, not roasted"], "document")
query = embed(["wireless earbuds"], "query")[0]
print(len(docs), "doc vectors; dim =", len(query))   # voyage-3 gives 1024
```

## 💻 Code Example — Advanced
```python
# RAG: Voyage retrieval + Claude generation, async, with error handling
import asyncio
import os
import numpy as np
import voyageai                                # pip install voyageai
import anthropic                               # pip install anthropic

vo = voyageai.AsyncClient()                    # reads VOYAGE_API_KEY
claude = anthropic.AsyncAnthropic()            # reads ANTHROPIC_API_KEY
EMBED_MODEL = "voyage-3"
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")   # check docs for latest id


async def embed(texts: list[str], input_type: str) -> np.ndarray:
    """Embed with Voyage; wrap provider errors."""
    try:
        r = await vo.embed(texts, model=EMBED_MODEL, input_type=input_type)
    except Exception as exc:
        raise RuntimeError(f"voyage failed: {exc}") from exc
    v = np.asarray(r.embeddings, dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)    # unit vectors


async def answer(question: str, docs: list[str], doc_vecs: np.ndarray, k: int = 3) -> str:
    """Retrieve top-k docs, then ask Claude to answer using only them."""
    q = (await embed([question], "query"))[0]
    top = np.argsort(-(doc_vecs @ q))[:k]                  # nearest docs
    context = "\n".join(f"- {docs[i]}" for i in top)
    try:
        msg = await claude.messages.create(
            model=CLAUDE_MODEL, max_tokens=300,
            messages=[{"role": "user",
                       "content": f"Use only this context:\n{context}\n\nQuestion: {question}"}],
        )
    except anthropic.APIError as exc:
        raise RuntimeError(f"claude failed: {exc}") from exc
    return msg.content[0].text


async def main() -> None:
    docs = ["8518.30 Headphones and earphones", "0901.11 Coffee, not roasted"]
    vecs = await embed(docs, "document")
    print(await answer("Which code for wireless earbuds?", docs, vecs, k=1))


if __name__ == "__main__":
    asyncio.run(main())                        # needs both API keys
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import voyageai

app = FastAPI()
vo = voyageai.AsyncClient()                    # shared client


class QueryEmbedReq(BaseModel):
    text: str = Field(min_length=1)


@app.post("/embed/query")
async def embed_query(req: QueryEmbedReq) -> dict[str, int]:
    try:
        r = await vo.embed([req.text], model="voyage-3", input_type="query")
    except Exception as exc:                   # rate limit / auth / network
        raise HTTPException(status_code=502, detail=str(exc))
    return {"dims": len(r.embeddings[0]), "tokens": r.total_tokens}
```
Keep the generation route (Claude) separate from the embedding route so each can scale and fail independently.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_voyageai import VoyageAIEmbeddings       # pip install langchain-voyageai
from langchain_anthropic import ChatAnthropic           # pip install langchain-anthropic

emb = VoyageAIEmbeddings(model="voyage-3")              # embeddings from Voyage
llm = ChatAnthropic(model="claude-sonnet-4-5")          # generation from Claude

vec = emb.embed_query("wireless earbuds")
print(len(vec))
```
In LangGraph: node 1 retrieves with `VoyageAIEmbeddings` + vector store, node 2 calls `ChatAnthropic` with the retrieved context.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling a non-existent Claude embedding endpoint
✅ Correct: Use Voyage (or OpenAI/Cohere/local) for vectors.

```python
# Wrong
anthropic.Anthropic().embeddings.create(...)    # does not exist
# Right
voyageai.Client().embed(texts, model="voyage-3", input_type="document")
```

❌ Mistake 2: Omitting `input_type`
✅ Correct: Use "document" for corpus and "query" for searches; Voyage adds an optimised prefix.

❌ Mistake 3: Using Claude to "generate embeddings" by asking for numbers
✅ Correct: LLM-written numbers are not real embeddings and are not reproducible.

---

## 🧠 Tricky Interview Question

**Q**: "We use Claude for generation. Is it a problem to use OpenAI embeddings for retrieval?"

**Answer**: No. Embeddings and generation are independent: retrieval only needs consistent vectors, then retrieved text (not vectors) goes into Claude's prompt. The trade-offs are operational: two vendors, two keys, two privacy reviews, and data leaves your network to both. Pick the embedding model by retrieval quality on your eval set, price, and latency.

---

## ⚫ Interview Questions + Answers

Q1: Does Anthropic provide an embeddings API?
A1: No. Anthropic recommends Voyage AI.

Q2: What is `input_type` in Voyage?
A2: "query" or "document"; it tells the model how to encode the text, improving retrieval.

Q3: Can query vectors from Voyage be compared with OpenAI document vectors?
A3: No. Different vector spaces. Use one model for both sides.

Q4: What dimensions does `voyage-3` produce?
A4: 1024 by default (check the docs; some Voyage models support multiple output dimensions).

Q5: Design a Claude-based RAG with Voyage for a privacy-sensitive company.
A5: Chunk and embed with Voyage (check their data retention terms) or a local model if data cannot leave; store vectors in your own DB; retrieve top-k; rerank; send only the necessary chunks to Claude; log token usage; add citations and a refusal path when no chunk is relevant; version the embedding model name in metadata.

---

## 🔷 When to Use + When Not to Use
✅ Use Voyage with Claude when:
- You want strong retrieval quality and domain models (code, law, finance)
- You want Anthropic-recommended pairing

❌ Avoid when:
- Single-vendor procurement is mandatory (use one provider that has both)
- Data cannot leave the network (use local sentence-transformers)

---

## 📊 Visual Diagram
```
 docs ──► Voyage embed (document) ──► vector DB
                                         ▲
 question ► Voyage embed (query) ────────┘ top-k chunks
                                           │
                                           ▼
                                  Claude (messages.create)
                                           │
                                           ▼
                                  grounded answer
```

---

## 💰 Cost Impact
Voyage charges per input token (roughly cents per 1M tokens; the exact price and the free monthly token allowance vary by model, check the Voyage pricing page). Claude charges separately for input and output tokens. RAG saves Claude cost by sending 3 to 5 chunks (about 1,500 tokens) instead of the whole document. Optimise: cache embeddings, use `voyage-3-lite` for cheap bulk data, rerank to send fewer chunks, and use Claude prompt caching for static instructions.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Voyage AI | Embedding provider recommended by Anthropic | Anthropic का recommended embedding provider |
| `input_type` | "query" or "document" | Query या document का type |
| voyage-3 | General embedding model | General embedding model |
| voyage-code-3 | Code-specialised model | Code के लिए model |
| Grounding | Answer based on retrieved text | Retrieved text पर आधारित जवाब |

---

## ⚡ 3-Line Summary
English: Anthropic has no embedding endpoint; use Voyage AI (recommended) or any other provider. Use `input_type` correctly and keep one model for queries and documents. Claude only sees the retrieved text, not the vectors.
Hindi: Anthropic का embedding endpoint नहीं है; Voyage AI (recommended) या कोई और provider use करो। `input_type` सही रखो और query/documents में एक ही model। Claude सिर्फ retrieved text देखता है, vectors नहीं।

---

## ➡️ Next Topic
**111. Cohere Embeddings** - another strong provider with multilingual models and `input_type`.
