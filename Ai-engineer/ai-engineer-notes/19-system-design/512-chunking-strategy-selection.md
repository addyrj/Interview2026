---

# 512. Chunking Strategy Selection
# हिंदी में: Chunking Strategy का चुनाव

---

## 🔵 Simple Definition (English)
Chunking is splitting documents into pieces before embedding. Strategy selection means choosing chunk size, overlap and method (fixed size, recursive, structure-aware, semantic, parent-child) so each chunk holds one complete idea and fits the embedding model and the prompt budget.

## 🔵 सरल परिभाषा (Hindi)
Chunking का मतलब embedding से पहले documents को टुकड़ों में बाँटना है। Strategy selection में chunk size, overlap और method (fixed, recursive, structure-aware, semantic, parent-child) चुना जाता है ताकि हर chunk में एक पूरा idea रहे और वह embedding model व prompt budget में fit हो।

---

## 🔴 Problem it Solves
Chunks that are too big dilute meaning and waste tokens; too small lose context ("it" without the subject); splits in the middle of a table or legal clause give wrong answers. Chunking quality often limits RAG quality more than the LLM does.

## 🔴 यह क्यों बना? (Hindi)
बहुत बड़े chunks meaning पतला कर देते हैं और tokens बर्बाद करते हैं; बहुत छोटे chunks context खो देते हैं; table या clause बीच में कटे तो जवाब गलत आता है। RAG की quality अक्सर LLM से ज़्यादा chunking पर निर्भर करती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Look at document types: prose, tables, code, legal clauses, FAQs
Step 2 → Pick a method per type:
         FAQ/short notes     -> one item per chunk
         structured docs     -> split by headings/sections (structure-aware)
         long prose          -> recursive split (paragraph > sentence), 200-500 tokens
         need precision+context -> parent-child (search small, return big parent)
Step 3 → Set overlap (10-20%) so ideas are not cut at boundaries
Step 4 → Attach metadata: source, section title, page, version
Step 5 → Evaluate: retrieval recall@k for several sizes (e.g. 200, 400, 800 tokens)
Step 6 → Choose the best size per quality and token cost
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Document types देखो: prose, tables, code, legal clauses, FAQs
Step 2 → हर type के लिए method चुनो (FAQ: एक item = एक chunk; structured: headings से;
         long prose: recursive 200-500 tokens; precision+context: parent-child)
Step 3 → 10-20% overlap रखो
Step 4 → Metadata जोड़ो: source, section, page, version
Step 5 → अलग-अलग sizes पर recall@k मापो
Step 6 → Quality और token cost के हिसाब से best चुनो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tariff schedules are hierarchical: Section > Chapter > Heading > Subheading, with notes that apply to a whole chapter. Splitting blindly every 500 tokens separates a subheading from its chapter note, and the LLM misses the exclusion. Fix: structure-aware chunks per heading, with the chapter note prepended as metadata or retrieved as the parent.
**Amazon-style example**: Product FAQs: one question-answer pair per chunk works best.

## 🟡 Real Example Hindi mein
**Tariff System**: Tariff schedule hierarchical है: Section > Chapter > Heading > Subheading, और chapter notes पूरे chapter पर लागू होते हैं। हर 500 tokens पर कटने से subheading अपने chapter note से अलग हो जाता है और LLM exclusion miss कर देता है। Fix: heading के हिसाब से chunks, chapter note parent के रूप में साथ।

---

## 💻 Code Example — Basic
```python
# Basic: fixed-size chunking with overlap vs structure-aware chunking (pure Python, offline)
def fixed_chunks(text: str, size: int = 6, overlap: int = 2) -> list[str]:  # word-based windows
    words = text.split()  # split text into words
    step = max(1, size - overlap)  # stride must be positive
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step) if words[i:i + size]]  # windows


def heading_chunks(text: str) -> list[tuple[str, str]]:  # split by lines starting with '#'
    chunks: list[tuple[str, str]] = []  # (heading, body)
    heading, body = "root", []  # state
    for line in text.splitlines():  # loop lines
        if line.startswith("#"):  # new heading
            if body:  # flush previous section
                chunks.append((heading, " ".join(body)))  # save
            heading, body = line.lstrip("# ").strip(), []  # reset
        else:
            body.append(line.strip())  # collect text
    if body:  # flush last section
        chunks.append((heading, " ".join(body)))  # save
    return chunks  # result


doc = "# 8517 Phones\nTelephone sets for cellular networks.\n# 6109 T-shirts\nKnitted cotton shirts."  # sample
print(fixed_chunks(doc))  # may cut across headings
print(heading_chunks(doc))  # keeps each heading's text together
```

## 💻 Code Example — Advanced
```python
# Advanced: async parent-child chunking with token budget and validation
import asyncio  # async runtime
from dataclasses import dataclass  # records


@dataclass
class Chunk:  # one child chunk
    id: str  # id
    parent_id: str  # parent section id
    text: str  # child text


def approx_tokens(text: str) -> int:  # rough estimate: ~4 chars per token (use tiktoken for exact counts)
    return max(1, len(text) // 4)  # at least 1


def split_parent(parent_id: str, text: str, max_tokens: int = 40, overlap_chars: int = 20) -> list[Chunk]:
    if max_tokens < 1:  # validate
        raise ValueError("max_tokens must be >= 1")  # explicit error
    size = max_tokens * 4  # characters per child
    step = max(1, size - overlap_chars)  # stride
    return [Chunk(f"{parent_id}-{i}", parent_id, text[s:s + size])  # child chunks
            for i, s in enumerate(range(0, len(text), step)) if text[s:s + size].strip()]


async def ingest(parents: dict[str, str]) -> tuple[list[Chunk], dict[str, str]]:  # build children + parent store
    await asyncio.sleep(0)  # placeholder for async I/O (DB writes, embeddings)
    children: list[Chunk] = []  # children list
    for pid, text in parents.items():  # per parent
        children += split_parent(pid, text)  # split
    return children, parents  # return both


async def retrieve(query: str, children: list[Chunk], parents: dict[str, str]) -> str:  # search small, return big
    best = max(children, key=lambda c: len(set(query.lower().split()) & set(c.text.lower().split())))  # toy match
    return parents[best.parent_id]  # return the full parent section for the LLM


if __name__ == "__main__":
    parents = {"8517": "Telephone sets including smartphones. Note: excludes parts of chapter 85 " * 3}  # sample
    kids, store = asyncio.run(ingest(parents))  # ingest
    print(len(kids), "children;", asyncio.run(retrieve("smartphones", kids, store))[:60])  # query
```

---

## 🟠 FastAPI Integration
Offer an ingestion endpoint that accepts a document and a strategy name; do heavy chunking in a background task. Keep chunking parameters in config and store them in metadata for reproducibility.

```python
from fastapi import FastAPI, BackgroundTasks, HTTPException  # app, tasks, errors
from pydantic import BaseModel, Field  # schema

app = FastAPI()  # app


class Doc(BaseModel):  # request
    doc_id: str  # id
    text: str = Field(min_length=1)  # content
    strategy: str = "recursive"  # chunk method


def do_ingest(doc: Doc) -> None:  # worker function
    pass  # chunk, embed, upsert here


@app.post("/ingest", status_code=202)  # accepted
async def ingest(doc: Doc, bg: BackgroundTasks) -> dict[str, str]:
    if doc.strategy not in {"fixed", "recursive", "structure", "parent_child"}:  # validate choice
        raise HTTPException(status_code=422, detail="unknown strategy")  # bad input
    bg.add_task(do_ingest, doc)  # run in background
    return {"status": "queued", "doc_id": doc.doc_id}  # ack
```

---

## 🔗 LangChain / LangGraph Connection
LangChain provides `RecursiveCharacterTextSplitter`, `MarkdownHeaderTextSplitter` and `ParentDocumentRetriever` (parent-child).

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter  # real classes

md = "# Chapter 85\nElectrical machinery.\n## 8517\nTelephone sets.\n"  # sample markdown
heads = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "chapter"), ("##", "heading")])  # structure-aware
sections = heads.split_text(md)  # documents with header metadata
rec = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)  # size limit within sections
final = rec.split_documents(sections)  # chunks keep metadata
print([(d.metadata, d.page_content) for d in final])  # inspect
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One size for all document types
✅ Correct: choose the method per type.
```python
# Wrong
chunks = fixed_chunks(any_doc, size=500)  # tables and clauses get cut
# Right
chunks = heading_chunks(doc) if has_headings(doc) else fixed_chunks(doc)  # type-aware
```

❌ Mistake 2: Zero overlap and no metadata
✅ Correct: 10-20% overlap, store section title and source.

---

## 🧠 Tricky Interview Question
**Q**: "Bigger chunks improved answer quality in testing but p95 latency and cost went up. What now?"

**Answer**: Bigger chunks add context but also tokens per query and noise. Use parent-child: embed small chunks for precise retrieval, then return the parent (or neighbouring chunks) only for the top 2-3 hits. Add reranking to keep context tight and compress retrieved text. Compare recall, faithfulness and cost per query across sizes.

---

## ⚫ Interview Questions + Answers

Q1: Why chunk at all? (Easy)
A1: Embedding models have input limits and one vector per huge document blurs meaning; smaller chunks give precise retrieval and fit in prompts.

Q2: What is overlap for? (Easy)
A2: To avoid losing information that straddles a boundary.

Q3: What is semantic chunking? (Medium)
A3: Splitting where embedding similarity between adjacent sentences drops, so chunks follow topic changes. It costs extra embeddings and is not always better, so test it.

Q4: What is parent-child retrieval? (Medium)
A4: Index small child chunks for precision, return the larger parent section for context.

Q5: How do you choose chunk size scientifically? (Hard)
A5: Build a retrieval eval; for sizes like 128, 256, 512, 1024 tokens, measure recall@k, answer faithfulness, tokens per query and latency. Choose the knee of the curve and vary by document type. Re-test when the embedding model changes.

---

## 🔷 When to Use + When Not to Use
✅ Structure-aware / parent-child when:
- Legal, tariff, technical docs with hierarchy and notes

❌ Avoid semantic chunking when:
- Budget is tight and recursive splitting performs equally in your eval

---

## 📊 Visual Diagram
```
Doc ──▶ [Section: Chapter 85 note] ─┐ parent
         ├─ child chunk 1 ──▶ embed ┤
         ├─ child chunk 2 ──▶ embed ┤──▶ vector DB (child + parent_id)
         └─ child chunk 3 ──▶ embed ┘
Query ─▶ match child ─▶ fetch parent ─▶ LLM
```

---

## 💰 Cost Impact
Chunk size sets tokens per query: k chunks x chunk size. 5 x 800 = 4,000 context tokens versus 5 x 250 = 1,250 (illustrative). Overlap increases embedding cost (20% overlap adds about 25% more embedded tokens). Semantic chunking adds embedding calls at ingestion.
Optimise: smaller chunks plus reranking, parent expansion only for top hits, dedupe repeated boilerplate, hash chunks to skip re-embedding.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunk | Piece of a document | दस्तावेज़ का टुकड़ा |
| Overlap | Shared text between chunks | साझा हिस्सा |
| Recursive splitting | Split by paragraph then sentence | क्रमिक विभाजन |
| Parent-child | Search small, return big | छोटा खोजो, बड़ा लौटाओ |
| Semantic chunking | Split by meaning shifts | अर्थ के आधार पर |
| Metadata | Extra info per chunk | अतिरिक्त जानकारी |

---

## ⚡ 3-Line Summary
English: Chunk by document structure so each piece holds one complete idea.
Use overlap and metadata, and consider parent-child for precision plus context.
Pick sizes with a retrieval eval, not guesswork.
Hindi: Document की structure के हिसाब से chunk करो ताकि हर टुकड़े में पूरा idea रहे।
Overlap और metadata रखो, precision और context के लिए parent-child सोचो।
Size का फैसला retrieval eval से करो, अंदाज़े से नहीं।

---

## ➡️ Next Topic
**513. Retrieval Strategy Selection** — dense, sparse, hybrid and filters.
