---

# 572. Build RAG from Scratch
# हिंदी में: शुरू से RAG बनाना

---

## 🔵 Simple Definition (English)
RAG (Retrieval-Augmented Generation) first finds the most relevant text chunks for a question from your own documents, then gives them to the LLM as context so it answers from facts instead of memory. Building it from scratch means writing chunking, embedding, search and prompting yourself.

## 🔵 सरल परिभाषा (Hindi)
RAG (Retrieval-Augmented Generation) पहले आपके documents से सवाल के सबसे relevant text chunks ढूँढता है, फिर उन्हें LLM को context के रूप में देता है ताकि वह याददाश्त के बजाय तथ्यों से जवाब दे। From scratch बनाने का मतलब chunking, embedding, search और prompting खुद लिखना।

---

## 🔴 Problem it Solves
LLMs do not know your private data, can be out of date, and hallucinate. Fine-tuning for facts is costly and goes stale. Interviewers use this problem to check that you understand each stage (chunk, embed, retrieve, prompt, refuse) rather than just calling a framework.

## 🔴 यह क्यों बना? (Hindi)
LLM आपका private data नहीं जानते, पुराने हो सकते हैं और hallucinate करते हैं। तथ्यों के लिए fine-tuning महँगा है और जल्दी पुराना होता है। Interviewer देखना चाहते हैं कि आप हर stage (chunk, embed, retrieve, prompt, refuse) समझते हैं, सिर्फ framework call नहीं करते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load documents (tariff notes)
Step 2 → Chunk: split into overlapping windows so facts at borders survive
Step 3 → Embed each chunk into a vector; store in an index
Step 4 → Query: embed the question with the SAME embedding model
Step 5 → Retrieve top-k chunks by cosine similarity; drop weak hits (min score)
Step 6 → Prompt: "Answer ONLY from context, cite ids, else say I don't know"
Step 7 → LLM answers; return answer + source ids
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Documents load करो (tariff notes)
Step 2 → Chunk: overlapping windows ताकि border के facts न कटें
Step 3 → हर chunk का vector बनाओ और index में रखो
Step 4 → सवाल को उसी embedding model से embed करो
Step 5 → cosine से top-k chunks लाओ; कमज़ोर hits हटाओ
Step 6 → Prompt: "सिर्फ context से जवाब दो, ids cite करो, वरना I don't know"
Step 7 → LLM जवाब देता है; answer + source ids लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Officer asks "duty on smartphones?". Retrieval returns the HS 8517 chunk; the LLM answers "20 percent [hs-8517]". For "tax on rocket fuel", nothing passes the score threshold, so the system says "I don't know" instead of inventing a number.

**Amazon-style**: Customer-support bot answering from return-policy pages.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer पूछता है "smartphones पर duty?" Retrieval HS 8517 का chunk लाता है; LLM "20 percent [hs-8517]" बताता है। "Rocket fuel पर tax" के लिए कोई chunk threshold पार नहीं करता, इसलिए system अंदाज़ा लगाने के बजाय "I don't know" कहता है।

---

## 💻 Code Example — Basic
Full file: `main.py` (stdlib only). I ran `python main.py`: it indexed 6 chunks, answered the smartphone question with a `[hs-8517]` grounded line and sources `['hs-8517', 'hs-6109']`, and returned "I don't know" for the unrelated query. Note: the embedding is a toy hashing bag-of-words, so relevance is rough, and the mock LLM just echoes the top context line.

```python
# Chunking with overlap (from main.py)
def chunk_text(doc_id: str, text: str, size: int = 12, overlap: int = 3) -> list[tuple[str, str]]:
    if size <= overlap:
        raise ValueError("size must be larger than overlap")   # prevent endless loop
    words = text.split()                                       # tokens by whitespace
    step = size - overlap                                      # window stride
    out: list[tuple[str, str]] = []                            # result
    for start in range(0, max(len(words), 1), step):           # slide window
        piece = " ".join(words[start:start + size])            # one chunk
        if piece:
            out.append((doc_id, piece))                        # store
        if start + size >= len(words):
            break                                              # done
    return out
```

## 💻 Code Example — Advanced
`main.py` has `VectorIndex.search` (cosine, top-k, `min_score` guard), `build_prompt` (grounding + citation instruction), async `RAG.ask`, and a FastAPI `/ask` route. Production swaps: real embeddings (e.g. `text-embedding-3-small`), a vector DB (Qdrant/pgvector), hybrid search plus reranking, token-aware chunking, and an evaluation set.

```python
# Excerpt: refuse when retrieval is weak (main.py)
hits = self.index.search(question)                      # top-k above min_score
if not hits:
    return {"answer": "I don't know", "sources": []}    # no grounding -> no guessing
answer = await generate(build_prompt(question, hits))   # grounded generation
return {"answer": answer, "sources": [c.doc_id for c, _ in hits]}
```

---

## 🟠 FastAPI Integration
```python
# main.py exposes POST /ask; build the index once at startup, not per request
rag = RAG()                      # service object
rag.ingest(DOCS)                 # embed + index at startup (use a lifespan hook or a worker for big corpora)

@app.post("/ask")
async def ask(q: Q) -> dict[str, object]:
    return await rag.ask(q.question)   # async: retrieval is fast, LLM call is awaited
```
Heavy ingestion belongs in a background job, not a request. (FastAPI was not installed here, so the route was not executed.)

---

## 🔗 LangChain / LangGraph Connection
Each hand-written stage has a LangChain equivalent: `RecursiveCharacterTextSplitter` (chunk), `Embeddings` (embed), `VectorStore.as_retriever()` (retrieve), `ChatPromptTemplate` (prompt), then the model. See 573 for the full chain. In LangGraph, make `retrieve` and `generate` two nodes with a conditional edge to an "I don't know" node.

```python
# Mapping (illustrative)
# chunk_text -> RecursiveCharacterTextSplitter
# VectorIndex -> InMemoryVectorStore / Qdrant / PGVector
# build_prompt -> ChatPromptTemplate
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Different embedding models for documents and queries
✅ Correct: Same model and settings for both sides.
```python
# Wrong
index.add(embed_v1(chunk)); q = embed_v2(question)   # different vector spaces -> nonsense scores
# Right
index.add(embed(chunk)); q = embed(question)         # same function
```

❌ Mistake 2: Always answering even with no relevant context
✅ Correct: Use a similarity threshold and a refusal instruction.
```python
# Wrong: pass top-3 whatever the score -> confident hallucination
# Right: if best_score < 0.3: return "I don't know"
```

---

## 🧠 Tricky Interview Question
**Q**: "Retrieval returns the right chunk, but the answer is still wrong. What do you check?"

**Answer**: (1) Chunk boundaries: the answer may be split across chunks; add overlap or parent-document retrieval. (2) Context order: "lost in the middle", so put the best chunk first. (3) Prompt: instruct to answer only from context and cite. (4) Conflicting chunks (old vs new tariff); add metadata filters like effective date. (5) Model too weak for the reasoning; test a stronger model. Measure retrieval and generation separately (recall@k vs faithfulness).

---

## ⚫ Interview Questions + Answers

Q1: What is an embedding?
A1: A vector of numbers representing meaning; similar texts have nearby vectors.

Q2: Why chunk documents?
A2: Embeddings of a whole document are blurry and context windows are limited; chunks give focused retrieval.

Q3: What does overlap do and what is its cost?
A3: Preserves facts that span borders; costs extra storage and duplicate tokens in prompts.

Q4: How do you evaluate a RAG system?
A4: Retrieval: recall@k, MRR on labelled questions. Generation: faithfulness (grounded in context), answer relevance. Use a golden set plus spot checks.

Q5: How would you scale this to 10 million chunks?
A5: Vector DB with ANN (HNSW), metadata filtering, hybrid BM25+vector, reranker on top 50, async batch ingestion, embedding cache, sharding, and monitoring of retrieval quality and latency.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers must come from private or frequently changing documents
- You need citations

❌ Avoid when:
- The whole corpus fits in the prompt cheaply (just stuff it, maybe with prompt caching)
- Task needs reasoning/tools more than lookup

---

## 📊 Visual Diagram
```
 INDEXING                                  QUERY
 docs ─► chunk ─► embed ─► [vector index]   question ─► embed
                              ▲                          │
                              └──── top-k cosine ◄───────┘
                                        │ (score >= min?)
                                        ▼
                         prompt(context + question) ─► LLM ─► answer + sources
                                        │ no hits
                                        └─► "I don't know"
```

---

## 💰 Cost Impact
Indexing: one-time embedding cost = total chunk tokens x embedding price (re-paid only for changed docs). Query: question embedding (tiny) + LLM input = question + k chunks. With k=4 and 200-token chunks that is ~900 input tokens, versus pasting a 50-page document (tens of thousands). Optimise: smaller k, reranking to keep only the best chunks, caching frequent questions, prompt caching for static instructions, cheap model for simple queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieve then generate | पहले खोजो फिर जवाब दो |
| Chunk | Piece of a document | Document का टुकड़ा |
| Embedding | Meaning as a vector | अर्थ का vector |
| Cosine similarity | Angle-based closeness | Vectors की समानता |
| top-k | Best k results | सबसे अच्छे k नतीजे |
| Grounding | Answer tied to sources | स्रोत पर आधारित जवाब |

---

## ⚡ 3-Line Summary
English: RAG = chunk, embed, retrieve, prompt, answer with sources. Use the same embedding model for both sides and refuse when retrieval is weak. Measure retrieval and generation separately.
Hindi: RAG = chunk, embed, retrieve, prompt, sources के साथ जवाब। दोनों तरफ़ वही embedding model रखें और retrieval कमज़ोर हो तो मना करें। Retrieval और generation को अलग-अलग मापें।

---

## ➡️ Next Topic
**573. Build RAG with LangChain** — the same pipeline using LangChain components and LCEL.
