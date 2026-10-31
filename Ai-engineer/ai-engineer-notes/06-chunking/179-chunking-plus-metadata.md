---

# 179. Chunking + Metadata
# हिंदी में: Chunking + Metadata (chunk के साथ जानकारी जोड़ना)

---

## 🔵 Simple Definition (English)
Metadata is structured information stored next to each chunk: source file, page, section, chunk index, language, date, chapter, HS code, access level. Vectors find "similar meaning"; metadata finds "the right document, the right year, the right user permission". Good chunking always attaches metadata at the moment the chunk is created.

## 🔵 सरल परिभाषा (Hindi)
Metadata वह structured जानकारी है जो हर chunk के साथ रखी जाती है: source file, page, section, chunk index, language, date, chapter, HS code, access level। Vectors "मिलता-जुलता अर्थ" खोजते हैं; metadata "सही document, सही साल, सही user permission" खोजता है। अच्छी chunking में chunk बनते ही metadata जुड़ जाता है।

---

## 🔴 Problem it Solves
- Pure similarity search returns the 2019 rate when the user needs the 2025 rate, or another company's document.
- Without metadata you cannot cite sources (file, page), filter by date/chapter, delete or update one document's chunks, or enforce access control.
- Metadata can be added later only by re-reading the source; adding it at chunk time is cheap.

## 🔴 यह क्यों बना? (Hindi)
- सिर्फ similarity search 2025 की जगह 2019 की rate या किसी और company का document लौटा सकती है।
- Metadata के बिना source cite (file, page), date/chapter से filter, एक document के chunks delete/update, और access control नहीं हो सकते।
- बाद में metadata जोड़ने के लिए source दोबारा पढ़ना पड़ता है; chunk बनाते समय जोड़ना सस्ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide a metadata schema first (required keys, types, allowed values)
Step 2 → Document-level fields: source, title, doc_type, language, effective_date, tenant_id
Step 3 → Position fields (added by the chunker): page, section_path, chunk_index, char_start, char_end
Step 4 → Domain fields (extracted by rules/LLM): chapter, hs_code, product_category
Step 5 → Make a stable chunk id: hash(source + position + text) -> safe re-ingestion and deletes
Step 6 → Store metadata beside the vector (and index the fields you filter on)
Step 7 → Query: pre-filter by metadata (date, tenant, chapter), THEN rank by similarity
Step 8 → Answer: return metadata as citations ("tariff_2025.pdf, p.87")
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले metadata schema तय करो (required keys, types, allowed values)
Step 2 → Document-level fields: source, title, doc_type, language, effective_date, tenant_id
Step 3 → Position fields: page, section_path, chunk_index, char_start, char_end
Step 4 → Domain fields: chapter, hs_code, product_category
Step 5 → Stable chunk id: hash(source + position + text)
Step 6 → Metadata को vector के साथ store करो (जिन fields पर filter करना है उन्हें index करो)
Step 7 → Query: पहले metadata से pre-filter (date, tenant, chapter), फिर similarity से rank
Step 8 → जवाब में metadata से citations ("tariff_2025.pdf, p.87")
```

---

## 🟡 Real World Example
**Tariff Classification System**: Every chunk has `{source: "tariff_2025.pdf", page: 87, chapter: "85", hs4: "8517", effective: "2025-04-01", superseded: null, doc_type: "tariff_line", tenant: "customs-in"}`. A query for a shipment dated 2024-12-10 filters `effective <= 2024-12-10 < superseded` so the 2024 rates are used, not the 2025 ones. The answer cites page 87 and the legal note id.

**Amazon / Zomato style**: Chunks carry `restaurant_id`, `city`, `language`, `updated_at`. "Open now in Pune?" is answered by filtering `city = Pune` before similarity.

## 🟡 Real Example Hindi mein
**Tariff System**: हर chunk में `{source, page, chapter, hs4, effective, superseded, doc_type, tenant}` है। 2024-12-10 की shipment के लिए `effective <= 2024-12-10 < superseded` filter लगता है, इसलिए 2024 की rates मिलती हैं, 2025 की नहीं। जवाब page 87 और legal note id cite करता है।

**Amazon / Zomato**: Chunks में `restaurant_id`, `city`, `language`, `updated_at` रहते हैं। "Pune में अभी खुला?" similarity से पहले `city = Pune` filter से हल होता है।

---

## 💻 Code Example — Basic
```python
# Basic: attach metadata to chunks, then filter BEFORE ranking (pure Python).
chunks = [  # chunks with metadata
    {"text": "smartphones duty ten percent", "meta": {"chapter": "85", "year": 2025, "source": "tariff_2025.pdf", "page": 87}},
    {"text": "smartphones duty twelve percent", "meta": {"chapter": "85", "year": 2024, "source": "tariff_2024.pdf", "page": 85}},
    {"text": "lithium batteries duty twenty percent", "meta": {"chapter": "85", "year": 2025, "source": "tariff_2025.pdf", "page": 90}},
    {"text": "bicycles duty fifteen percent", "meta": {"chapter": "87", "year": 2025, "source": "tariff_2025.pdf", "page": 120}},
]

def matches(meta: dict, flt: dict) -> bool:  # does a chunk pass the filter?
    return all(meta.get(k) == v for k, v in flt.items())  # every filter key must equal

def score(q: str, text: str) -> int:  # naive similarity = shared words
    return len(set(q.lower().split()) & set(text.lower().split()))  # overlap

def search(q: str, flt: dict, k: int = 2) -> list[dict]:  # filter first, rank second
    pool = [c for c in chunks if matches(c["meta"], flt)]  # metadata pre-filter
    return sorted(pool, key=lambda c: -score(q, c["text"]))[:k]  # rank survivors

for hit in search("smartphones duty", {"year": 2025, "chapter": "85"}):  # only 2025, chapter 85
    print(hit["text"], "->", f'{hit["meta"]["source"]} p.{hit["meta"]["page"]}')  # answer + citation
```

## 💻 Code Example — Advanced
```python
# Production: schema-validated metadata, stable chunk ids, date-range filtering, async batch builder.
from __future__ import annotations  # modern hints

import asyncio  # async
import hashlib  # stable ids
from dataclasses import asdict, dataclass  # containers
from datetime import date  # dates


@dataclass(frozen=True)
class ChunkMeta:  # typed metadata (immutable)
    source: str  # file name
    page: int  # page number (1-based)
    section_path: str  # "Ch 85 > 8517"
    chunk_index: int  # order within the document
    doc_type: str  # tariff_line / chapter_note / ruling
    chapter: str  # "85"
    effective: date  # rate start date
    superseded: date | None  # rate end date (None = current)
    tenant: str  # access control key

    def validate(self) -> None:  # reject bad metadata at ingest time
        if self.page < 1:  # pages start at 1
            raise ValueError("page must be >= 1")  # error
        if self.superseded and self.superseded <= self.effective:  # impossible range
            raise ValueError("superseded must be after effective")  # error
        if not self.chapter.isdigit() or len(self.chapter) != 2:  # chapter format
            raise ValueError("chapter must be two digits")  # error


@dataclass
class MetaChunk:  # chunk + metadata + id
    id: str  # stable id
    text: str  # chunk text
    meta: ChunkMeta  # metadata


def chunk_id(meta: ChunkMeta, text: str) -> str:  # same input -> same id (idempotent re-ingest)
    raw = f"{meta.source}|{meta.page}|{meta.chunk_index}|{text}".encode()  # identity string
    return hashlib.sha256(raw).hexdigest()[:16]  # short hash


def build(texts: list[str], base: ChunkMeta) -> list[MetaChunk]:  # attach metadata to raw chunk texts
    out: list[MetaChunk] = []  # result
    for i, t in enumerate(texts):  # each chunk
        meta = ChunkMeta(**{**asdict(base), "chunk_index": i})  # copy with its own index
        meta.validate()  # fail fast on bad data
        out.append(MetaChunk(chunk_id(meta, t), t, meta))  # add
    return out  # chunks


def valid_on(c: MetaChunk, on: date, tenant: str, chapter: str | None = None) -> bool:  # query-time filter
    m = c.meta  # shortcut
    in_range = m.effective <= on and (m.superseded is None or on < m.superseded)  # date range check
    return in_range and m.tenant == tenant and (chapter is None or m.chapter == chapter)  # all conditions


async def build_many(items: list[tuple[list[str], ChunkMeta]]) -> list[MetaChunk]:  # async batch
    parts = await asyncio.gather(*(asyncio.to_thread(build, t, m) for t, m in items))  # parallel
    return [c for p in parts for c in p]  # flatten


if __name__ == "__main__":  # demo
    old = ChunkMeta("tariff_2024.pdf", 85, "Ch 85 > 8517", 0, "tariff_line", "85", date(2024, 4, 1), date(2025, 4, 1), "in")
    new = ChunkMeta("tariff_2025.pdf", 87, "Ch 85 > 8517", 0, "tariff_line", "85", date(2025, 4, 1), None, "in")
    allc = asyncio.run(build_many([(["smartphones duty twelve percent"], old), (["smartphones duty ten percent"], new)]))
    for c in allc:  # filter for a shipment on 2024-12-10
        print(c.id, valid_on(c, date(2024, 12, 10), "in", "85"), c.text)  # only the 2024 rate passes
```

---

## 🟠 FastAPI Integration
The query endpoint takes the user question plus structured filters (shipment date, chapter) and applies them before similarity ranking. The tenant comes from the auth layer, never from the request body.

```python
from datetime import date  # dates
from fastapi import Depends, FastAPI, Header  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app
STORE: list[MetaChunk] = []  # replace with your vector DB


class SearchIn(BaseModel):  # request
    question: str  # user question
    shipment_date: date  # which tariff version applies
    chapter: str | None = None  # optional filter


def tenant_from_auth(x_tenant: str = Header(...)) -> str:  # stand-in for real auth
    return x_tenant  # in production: derive from the verified JWT


@app.post("/search")  # route
async def search(req: SearchIn, tenant: str = Depends(tenant_from_auth)) -> dict:  # handler
    pool = [c for c in STORE if valid_on(c, req.shipment_date, tenant, req.chapter)]  # metadata pre-filter
    qw = set(req.question.lower().split())  # query words
    top = sorted(pool, key=lambda c: -len(qw & set(c.text.lower().split())))[:3]  # rank survivors
    return {"hits": [{"text": c.text, "citation": f"{c.meta.source} p.{c.meta.page}"} for c in top]}  # citations
```

---

## 🔗 LangChain / LangGraph Connection
LangChain `Document` objects have a `metadata` dict, and splitters copy it into every chunk (`split_documents`). Vector stores accept a `filter` in `search_kwargs`. The filter syntax differs by store (Chroma uses `{"chapter": "85"}` or operators like `$and`).

```python
from langchain_core.documents import Document  # document type
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitter

doc = Document(page_content="Smartphones attract ten percent duty. " * 20,
               metadata={"source": "tariff_2025.pdf", "page": 87, "chapter": "85", "year": 2025})  # base metadata
chunks = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20).split_documents([doc])  # metadata copied
print(chunks[0].metadata)  # {'source': 'tariff_2025.pdf', 'page': 87, 'chapter': '85', 'year': 2025}
# retriever = vectorstore.as_retriever(search_kwargs={"k": 4, "filter": {"chapter": "85"}})  # store-specific filter
# LangGraph: put 'filters' in graph state so the retrieve node and the answer node share them.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Filtering after similarity search (post-filter)
✅ Correct: Pre-filter (or use the DB's filtered search) so top-k is taken from valid chunks only.

```python
# Wrong - top 3 are all 2024 chunks; after filtering to 2025 nothing is left
hits = [h for h in vector_top_k(q, 3) if h.meta.year == 2025]  # may be empty

# Right - filter inside the search
hits = vector_top_k(q, 3, where={"year": 2025})  # k results from valid chunks only
```

❌ Mistake 2: Putting access control (tenant, user role) in the prompt instead of in metadata filters.
✅ Correct: Enforce it as a hard metadata filter in the retrieval call.

❌ Mistake 3: Random UUID chunk ids, so re-ingestion creates duplicates.
✅ Correct: Content-based stable ids; delete by `source` before re-ingesting a changed file.

---

## 🧠 Tricky Interview Question
**Q**: "A user asks for a 2023 rate. The vector search returns the 2025 chunk because it matches the text best, and the bot answers with the wrong rate with full confidence. How do you prevent this?"

**Answer**: Similarity does not understand dates. Extract the date constraint (from the question or from the request, such as shipment date) into a structured filter and apply it before ranking: `effective <= date < superseded`. Store validity ranges as metadata at ingestion. If no date is given, either default to "current" and say so in the answer, or ask. Add tests with questions per year and a guard that the answer cites the source version. Finally, surface the effective date in the answer text so humans can notice mistakes.

---

## ⚫ Interview Questions + Answers

Q1: Why attach metadata to chunks?
A1: For filtering (date, tenant, chapter), citations (source, page), updates/deletes per document, and access control.

Q2: What are good minimum metadata fields?
A2: source, page or position, chunk_index, doc_type, language, created/effective date, and tenant or access level.

Q3: Why use content-based chunk ids?
A3: Re-ingestion is idempotent (no duplicates), and you can detect unchanged chunks and skip re-embedding.

Q4: Pre-filter vs post-filter?
A4: Pre-filter applies metadata conditions during search, so top-k comes from valid chunks. Post-filter may return too few results because top-k was already taken from invalid ones.

Q5: (Hard) How do you design metadata for multi-tenant RAG securely?
A5: Store tenant/ACL in metadata, derive the tenant from verified auth (never from user input), enforce it in the database query as a mandatory filter (or separate collections/namespaces per tenant), test for cross-tenant leaks, and never include other tenants' text in prompts or logs.

---

## 🔷 When to Use + When Not to Use
✅ Use rich metadata when:
- Documents have versions, dates, owners or permissions
- You need citations
- Corpus is large and filters can cut the search space

❌ Avoid over-engineering when:
- Tiny single-tenant corpus where all chunks are always valid
- Metadata cannot be trusted or kept up to date (wrong metadata is worse than none)

---

## 📊 Visual Diagram
```
 raw doc ─► chunker ─► chunk text ─┐
                                   ├─► MetaChunk { id, text, meta{source,page,chapter,effective,tenant} }
 doc info + position + domain ─────┘                       │
                                                           ▼
                                                    vector DB (vector + payload)
 query + filters (date, tenant, chapter)
        │
        ▼
  [ metadata PRE-FILTER ] ─► candidates ─► [ similarity rank ] ─► top-k + citations ─► LLM
```

---

## 💰 Cost Impact
- Metadata adds almost no embedding tokens (it is not embedded unless you choose to prepend some fields). Storage grows by tens to hundreds of bytes per chunk.
- Filtering reduces candidates and can lower search latency; fewer irrelevant chunks means smaller prompts: removing wrong-year chunks can cut top-k from 8 to 4 (saving about 1,600 prompt tokens/query at 400 tokens per chunk, about $24/day at 100K queries and $0.15 per 1M).
- Optional: prepend a short header (title, chapter) into the embedded text for better retrieval - adds 10-20 tokens per chunk.
- Optimise: only index fields you filter on; use stable ids to skip re-embedding unchanged chunks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metadata | Structured info about a chunk | Chunk के बारे में structured जानकारी |
| Pre-filter | Filter before ranking | Ranking से पहले filter |
| Citation | Source reference in answer | जवाब में source का हवाला |
| Stable id | Same content -> same id | समान content, समान id |
| Effective date | Date from which data is valid | कब से मान्य |
| Tenant | Customer/organisation | Customer/संस्था |

---

## ⚡ 3-Line Summary
English: Metadata turns chunks from loose text into filterable, citable, updatable records. Attach source, position, dates and access fields at chunk time and pre-filter before similarity. Use stable ids and enforce tenant rules in the database query.
Hindi: Metadata chunks को ढीले text से filter, cite और update हो सकने वाले records बनाता है। Chunk बनाते समय source, position, dates और access fields जोड़ो और similarity से पहले pre-filter करो। Stable ids रखो और tenant नियम database query में लागू करो।

---

## ➡️ Next Topic
**180. Chunking Best Practices** - a checklist that ties all chunking decisions together.
