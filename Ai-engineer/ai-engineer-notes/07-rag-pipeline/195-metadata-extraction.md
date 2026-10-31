---

# 195. Metadata Extraction
# हिंदी में: Metadata Extraction (मेटाडेटा निकालना)

---

## 🔵 Simple Definition (English)
Metadata extraction attaches structured facts (title, chapter, HS code, country, date, language, entities, summary) to every chunk. Some fields come free from the source (file name, page), some from rules (regex), and some from an LLM. Metadata powers filtering, citations, routing and better retrieval.

## 🔵 सरल परिभाषा (Hindi)
Metadata extraction हर chunk के साथ structured facts (title, chapter, HS code, country, date, language, entities, summary) जोड़ती है। कुछ fields source से मुफ्त मिलते हैं (file name, page), कुछ rules (regex) से, और कुछ LLM से। Metadata filtering, citations, routing और बेहतर retrieval को संभव बनाता है।

---

## 🔴 Problem it Solves
A chunk like "The rate is 5 percent." is useless alone: which product, country, year? Pure vector search cannot filter "only 2025 rules for India" because that information lives nowhere except inside the text. Without metadata you cannot filter, cite, delete or update precisely.

## 🔴 यह क्यों बना? (Hindi)
"The rate is 5 percent." जैसा chunk अकेले बेकार है: कौन सा product, देश, साल? सिर्फ vector search "India के 2025 के नियम" filter नहीं कर सकता क्योंकि वह जानकारी text के अंदर ही दबी है। Metadata के बिना precise filter, cite, delete या update नहीं हो सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Free metadata: source, file name, page, section heading, loaded_at
Step 2 → Rule-based extraction: regex for HS codes (\d{4}\.\d{2}), dates, country codes
Step 3 → (Optional) LLM extraction with a Pydantic schema: product, category, country, effective_year, summary
Step 4 → Validate values (allowed enums, year range); fall back to null if unsure
Step 5 → Inherit document-level metadata into every chunk (chapter, version)
Step 6 → Store in the vector DB as filterable fields (only simple types: str, int, float, bool)
Step 7 → Use at query time: filters, citations, "keep latest version only"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Free metadata: source, file name, page, section heading, loaded_at
Step 2 → Rule-based: HS codes (\d{4}\.\d{2}), dates, country codes के लिए regex
Step 3 → (Optional) Pydantic schema के साथ LLM extraction: product, category, country, effective_year, summary
Step 4 → Values validate करो (allowed enums, year range); पक्का न हो तो null
Step 5 → Document-level metadata हर chunk में inherit कराओ (chapter, version)
Step 6 → Vector DB में filterable fields के रूप में रखो (सिर्फ simple types)
Step 7 → Query पर इस्तेमाल: filters, citations, "सिर्फ latest version"
```

---

## 🟡 Real World Example
**Tariff Classification System**: Each chunk gets `{hs_code: "8518.30", chapter: 85, country: "IN", effective_year: 2025, doc_type: "tariff_schedule"}`. HS code and year come from regex (cheap, exact); `product_category` and a one-line `summary` come from an LLM. At query time "2025 India earphones" filters `country=IN, effective_year=2025` before similarity.
**Zomato AI**: Menu items get `cuisine`, `veg`, `price_band`, `spice_level` extracted from descriptions.

## 🟡 Real Example Hindi mein
**Tariff System**: हर chunk को `{hs_code: "8518.30", chapter: 85, country: "IN", effective_year: 2025, doc_type: "tariff_schedule"}` मिलता है। HS code और year regex से (सस्ता, exact); `product_category` और एक-line `summary` LLM से। Query "2025 India earphones" पर similarity से पहले `country=IN, effective_year=2025` filter लगता है।
**Zomato AI**: Menu items के descriptions से `cuisine`, `veg`, `price_band`, `spice_level` निकाले जाते हैं।

---

## 💻 Code Example — Basic
```python
# Rule-based metadata extraction with regex (standard library only)
import re
from typing import Dict, List, Optional

HS_RE = re.compile(r"\b(\d{4})\.(\d{2})\b")  # HS code like 8518.30
YEAR_RE = re.compile(r"\b(20\d{2})\b")  # 2000-2099
COUNTRIES = {"india": "IN", "china": "CN", "usa": "US"}  # tiny lookup table

def extract_metadata(text: str, source: str, page: int) -> Dict[str, object]:
    """Build a metadata dict for one chunk."""
    meta: Dict[str, object] = {"source": source, "page": page}  # free fields
    hs: List[str] = [f"{a}.{b}" for a, b in HS_RE.findall(text)]  # all HS codes
    if hs:
        meta["hs_code"] = hs[0]  # primary code
        meta["chapter"] = int(hs[0][:2])  # first 2 digits = chapter
    years = YEAR_RE.findall(text)  # years mentioned
    if years:
        meta["effective_year"] = int(max(years))  # latest year mentioned
    lowered = text.lower()  # for country search
    for name, code in COUNTRIES.items():
        if name in lowered:
            meta["country"] = code  # first country found
            break
    return meta

def matches(meta: Dict[str, object], flt: Dict[str, object]) -> bool:
    """Simple equality filter, as a vector DB would do."""
    return all(meta.get(k) == v for k, v in flt.items())

if __name__ == "__main__":
    chunk = "India: HS 8518.30 earphones, duty 0 percent, effective 2025."
    m = extract_metadata(chunk, "tariff.pdf", 12)  # extract
    print(m)  # {'source':..., 'hs_code': '8518.30', 'chapter': 85, 'effective_year': 2025, 'country': 'IN'}
    print(matches(m, {"country": "IN", "effective_year": 2025}))  # True
    print(matches(m, {"country": "CN"}))  # False
```

## 💻 Code Example — Advanced
```python
# LLM-based extraction with a Pydantic v2 schema, validation, retries, async concurrency
import asyncio
import json
import logging
from typing import Awaitable, Callable, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("meta")  # logger

class ChunkMeta(BaseModel):
    product_category: Optional[Literal["electronics", "footwear", "food", "textile", "other"]] = None  # enum
    country: Optional[str] = Field(default=None, pattern=r"^[A-Z]{2}$")  # ISO-2
    effective_year: Optional[int] = Field(default=None, ge=1990, le=2100)  # sane range
    summary: Optional[str] = Field(default=None, max_length=160)  # short summary

LLMJson = Callable[[str], Awaitable[tuple[str, int]]]  # returns (json_text, tokens)

PROMPT = ("Extract metadata as JSON with keys product_category, country (ISO-2), effective_year, summary. "
          "Use null if not stated. Text:\n{text}")  # instruction

async def extract_one(llm: LLMJson, text: str, retries: int = 2) -> tuple[ChunkMeta, int]:
    tokens = 0  # token counter
    for attempt in range(retries + 1):
        try:
            raw, used = await llm(PROMPT.format(text=text[:2000]))  # cap input size
            tokens += used
            return ChunkMeta.model_validate(json.loads(raw)), tokens  # validated result
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("invalid metadata (attempt %d): %s", attempt, exc)  # retry
        except Exception:
            logger.exception("llm error"); break  # provider error, stop
    return ChunkMeta(), tokens  # safe empty metadata (never crash ingestion)

async def extract_many(llm: LLMJson, texts: list[str], concurrency: int = 8) -> list[ChunkMeta]:
    sem = asyncio.Semaphore(concurrency)  # rate-limit friendly
    async def run(t: str) -> ChunkMeta:
        async with sem:
            meta, _ = await extract_one(llm, t); return meta
    return await asyncio.gather(*(run(t) for t in texts))  # parallel

async def fake_llm(prompt: str) -> tuple[str, int]:
    return '{"product_category": "electronics", "country": "IN", "effective_year": 2025, "summary": "Earphones duty 0"}', 120

if __name__ == "__main__":
    print(asyncio.run(extract_many(fake_llm, ["India HS 8518.30 earphones duty 0 effective 2025"])))
```

---

## 🟠 FastAPI Integration
Add an `/ingest` route that extracts metadata at ingestion and a `/search` route that accepts optional filters. Validate filters with Pydantic so clients cannot send arbitrary keys.

```python
# FastAPI: validated metadata filters on search
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()  # app

class SearchReq(BaseModel):
    query: str  # search text
    country: Optional[str] = None  # ISO-2 filter
    effective_year: Optional[int] = None  # year filter

@app.post("/search")
async def search(req: SearchReq) -> dict:
    flt = {k: v for k, v in req.model_dump(exclude={"query"}).items() if v is not None}  # only provided filters
    hits = await vector_search(req.query, flt)  # your vector DB call with metadata filter
    return {"filters": flt, "results": hits}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `create_metadata_tagger` / `DocumentTransformer` style extraction with `with_structured_output`, and `SelfQueryRetriever` which uses metadata field descriptions so an LLM turns natural language into a filter. LlamaIndex has `TitleExtractor`, `KeywordExtractor`, `QuestionsAnsweredExtractor`.

```python
# Structured extraction as an LCEL runnable (needs langchain-core, langchain-openai, pydantic v2)
from typing import Optional
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class Meta(BaseModel):
    country: Optional[str]  # ISO-2 or None
    effective_year: Optional[int]  # year or None

extractor = (ChatPromptTemplate.from_template("Extract metadata from: {text}")
             | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Meta))  # typed result

def tag(doc: Document) -> Document:
    # meta = extractor.invoke({"text": doc.page_content})   # needs OPENAI_API_KEY
    # doc.metadata.update(meta.model_dump(exclude_none=True))
    return doc  # (network call commented so this block is import-safe)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asking an LLM for metadata that a regex can extract exactly.
✅ Correct: Regex first (free, deterministic), LLM only for fuzzy fields.

```python
# Wrong: LLM call per chunk to find "8518.30"
# Right
hs = HS_RE.findall(text)
```

❌ Mistake 2: Storing nested dicts or lists as metadata in vector DBs that only support scalars.
✅ Correct: Flatten to scalar fields (or join lists to strings, or use the DB's array type).

```python
# Wrong
metadata = {"codes": ["8518.30", "8517.13"], "info": {"year": 2025}}
# Right
metadata = {"primary_hs_code": "8518.30", "info_year": 2025}
```

---

## 🧠 Tricky Interview Question
**Q**: "LLM-extracted `effective_year` is wrong for 5 percent of chunks, and filters on year now hide correct answers. What do you do?"

**Answer**: Wrong filters silently drop correct results, so treat LLM metadata as noisy. Inherit year from the document level (title page/filename) instead of inferring per chunk; validate against allowed ranges; store `null` when unsure and treat null as "matches any" in filters; keep a confidence flag; run an eval comparing filtered vs unfiltered recall; use soft boosts instead of hard filters for uncertain fields.

---

## ⚫ Interview Questions + Answers

Q1: What is metadata in RAG?
A1: Structured information about a chunk (source, page, date, category) stored next to its vector.

Q2: Name three uses of metadata.
A2: Pre-filtering search, citations, access control (tenant/role), versioning and deletion.

Q3: When do you use an LLM for extraction vs regex?
A3: Regex for patterned values (codes, dates); LLM for semantic fields (category, summary, intent) that have no fixed pattern.

Q4: What is a Self-Query Retriever?
A4: An LLM converts a natural-language query into a semantic query plus a structured metadata filter, using descriptions of the available metadata fields.

Q5: How do you control cost of LLM metadata extraction on 1M chunks?
A5: Extract at document or section level and inherit; use a small model; truncate input; batch/async with concurrency limits; cache by chunk hash; run regex first and call the LLM only when needed. Estimate: 1M x 500 tokens x 0.15 USD/1M = 75 USD input on gpt-4o-mini, plus small output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Corpus spans many versions, countries, tenants or document types
- You need citations and filters
- Queries contain constraints (year, price, location)

❌ Avoid when:
- Tiny homogeneous corpus
- Metadata would be guessed unreliably (then do not filter on it)

---

## 📊 Visual Diagram
```
 chunk text ─┬─► free fields: source, page, heading
             ├─► regex: hs_code, year, country_code     (exact, free)
             └─► LLM + schema: category, summary        (fuzzy, costs tokens)
                         │ validate (enum / range / null)
                         ▼
        vector DB record: { vector, text, metadata }
                         │
                         ▼
        query ─► filter(country=IN, year=2025) ─► similarity search
```

---

## 💰 Cost Impact
Rules and free fields cost nothing. LLM extraction costs one call per chunk (or per section): 500 input + 80 output tokens on gpt-4o-mini is about 0.00012 USD per chunk, or 120 USD per 1M chunks. Metadata also adds a little storage and slightly increases index size, but filtering reduces candidate chunks and the context sent to the generator.
Optimize: document-level inheritance, regex first, small model, concurrency limits, caching by hash.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metadata | Structured info about a chunk | Chunk की structured जानकारी |
| Regex | Pattern matching rule | Pattern match करने का नियम |
| Schema | Defined fields and types | Fields और types की परिभाषा |
| Inheritance | Chunk copies doc-level fields | Doc के fields chunk में आना |
| Self-query | LLM builds filter from text | LLM text से filter बनाए |
| Enum | Fixed allowed values | तय किए हुए मान |

---

## ⚡ 3-Line Summary
English: Metadata extraction adds filterable, citable facts to every chunk.
Use free fields and regex first, LLM schema extraction only for fuzzy fields, and validate everything.
Treat uncertain metadata as soft signals, not hard filters.
Hindi: Metadata extraction हर chunk में filter और cite करने लायक facts जोड़ती है।
पहले free fields और regex, फिर सिर्फ fuzzy fields के लिए LLM schema extraction, और सब validate करो।
अनिश्चित metadata को hard filter नहीं, soft signal मानो।

---

## ➡️ Next Topic
**196. Metadata Filtering in RAG**: using that metadata at query time (pre-filter, post-filter, hybrid, access control).
