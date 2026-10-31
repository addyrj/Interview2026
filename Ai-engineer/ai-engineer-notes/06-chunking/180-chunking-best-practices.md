---

# 180. Chunking Best Practices
# हिंदी में: Chunking की Best Practices

---

## 🔵 Simple Definition (English)
Chunking best practices are the rules of thumb that make chunks good for retrieval: respect document structure, keep chunks self-contained, use sensible size and small overlap, attach metadata, test with real questions, and check chunk quality automatically before indexing. This topic is the checklist that ties topics 164-179 together.

## 🔵 सरल परिभाषा (Hindi)
Chunking best practices वे अनुभव-आधारित नियम हैं जो chunks को retrieval के लिए अच्छा बनाते हैं: document structure का सम्मान, chunks self-contained, सही size और छोटा overlap, metadata, असली questions से test, और indexing से पहले chunk quality की automatic जाँच। यह topic 164-179 को जोड़ने वाली checklist है।

---

## 🔴 Problem it Solves
- Teams jump to the vector database and skip chunk quality; 70% of bad RAG answers trace back to bad chunks or bad retrieval, not to the LLM.
- Mistakes are silent: nothing crashes, answers are just worse.
- A checklist makes quality repeatable across documents, people and time.

## 🔴 यह क्यों बना? (Hindi)
- Teams सीधे vector database पर कूद जाती हैं और chunk quality छोड़ देती हैं; ज़्यादातर खराब RAG जवाबों की जड़ खराब chunks या retrieval होती है, LLM नहीं।
- गलतियाँ चुपचाप होती हैं: कुछ crash नहीं होता, बस जवाब बिगड़ते हैं।
- Checklist से quality लोगों, documents और समय के पार दोहराई जा सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Know your questions first: sample 50+ real queries; they define the right chunk unit
Step 2 → Clean the source: remove boilerplate (headers, footers, nav), fix encoding, OCR errors
Step 3 → Split by structure first (headings, records, functions), then by size (recursive)
Step 4 → Size in TOKENS: start 300-500 tokens (prose), atomic records stay whole
Step 5 → Overlap 10-15% for prose; 0 for atomic/structure-based chunks
Step 6 → Make chunks self-contained: prepend heading path / short context; resolve "it/this"
Step 7 → Attach metadata: source, page, section, dates, tenant; use stable chunk ids
Step 8 → Automated lint: size limits, empty/duplicate chunks, broken sentences, missing metadata
Step 9 → Evaluate with a golden set (recall@k, precision, answer correctness, tokens/query)
Step 10 → Monitor in production: no-answer rate, thumbs-down, chunk hit distribution; re-tune
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले अपने questions जानो: 50+ असली queries; वही सही chunk unit तय करते हैं
Step 2 → Source साफ करो: header, footer, nav हटाओ, encoding/OCR errors ठीक करो
Step 3 → पहले structure से (headings, records, functions), फिर size से split
Step 4 → Size TOKENS में: 300-500 से शुरू; atomic records पूरे रखो
Step 5 → Prose के लिए overlap 10-15%; atomic के लिए 0
Step 6 → Chunks self-contained: heading path जोड़ो; "it/this" हल करो
Step 7 → Metadata जोड़ो; stable chunk ids
Step 8 → Automatic lint: size limits, empty/duplicate chunks, टूटे वाक्य, missing metadata
Step 9 → Golden set से evaluate करो
Step 10 → Production में monitor करो और दोबारा tune करो
```

---

## 🟡 Real World Example
**Tariff Classification System** - the final recipe:
1. Tariff schedule: one tariff line per chunk with breadcrumb (topic 169), zero overlap.
2. Chapter notes and rulings: recursive splitting 400 tokens, 10% overlap, heading path prefix.
3. Parent-child for notes (topic 170) so exclusions arrive with the rule.
4. Metadata: hs_code, chapter, effective/superseded, source+page (topic 179).
5. Hybrid search (BM25 + vectors) for exact HS codes.
6. Golden set of 150 past rulings in CI (topic 175); lint step blocks bad ingests.

**Zomato style**: dish = chunk, review = chunk, help article = heading sections, all with city and updated_at metadata.

## 🟡 Real Example Hindi mein
**Tariff System** - अंतिम recipe:
1. Tariff schedule: एक tariff line = एक chunk, breadcrumb सहित, overlap 0।
2. Chapter notes और rulings: recursive 400 tokens, 10% overlap, heading path prefix।
3. Notes के लिए parent-child ताकि exclusions नियम के साथ आएँ।
4. Metadata: hs_code, chapter, effective/superseded, source+page।
5. Exact HS code के लिए hybrid search (BM25 + vectors)।
6. CI में 150 पुराने rulings का golden set; lint step खराब ingest रोकता है।

**Zomato**: dish = chunk, review = chunk, help article = heading sections, सब पर city और updated_at metadata।

---

## 💻 Code Example — Basic
```python
# Basic chunk linter in pure Python: catches common chunking problems before indexing.
import re  # regex helpers

def lint(chunks: list[str], min_words: int = 5, max_words: int = 200) -> list[str]:  # returns a list of problems
    problems: list[str] = []  # collected issues
    seen: set[str] = set()  # for duplicate detection
    for i, c in enumerate(chunks):  # each chunk
        words = len(c.split())  # word count
        if words == 0:  # empty chunk
            problems.append(f"#{i}: empty chunk")  # report
            continue  # nothing else to check
        if words < min_words:  # too small to carry meaning
            problems.append(f"#{i}: too short ({words} words)")  # report
        if words > max_words:  # too large
            problems.append(f"#{i}: too long ({words} words)")  # report
        if c[0].islower():  # starts mid-sentence (usually a bad cut)
            problems.append(f"#{i}: starts mid-sentence")  # report
        if not re.search(r"[.!?:;)\]\"']$", c.strip()):  # does not end like a sentence
            problems.append(f"#{i}: ends mid-sentence")  # report
        key = re.sub(r"\W+", " ", c.lower()).strip()  # normalised text
        if key in seen:  # exact duplicate
            problems.append(f"#{i}: duplicate chunk")  # report
        seen.add(key)  # remember
    return problems  # all issues

demo = ["Smartphones attract ten percent duty under heading 8517.",  # good
        "rate does not apply to refurbished units and",  # bad cut
        "Smartphones attract ten percent duty under heading 8517.",  # duplicate
        "Short."]  # too short
for p in lint(demo):  # print issues
    print(p)  # each problem
```

## 💻 Code Example — Advanced
```python
# Production quality gate: async lint with metadata checks, token budget, report, and a pass/fail decision.
from __future__ import annotations  # modern hints

import asyncio  # async
import hashlib  # duplicate detection
from dataclasses import dataclass, field  # containers


@dataclass
class Candidate:  # chunk about to be indexed
    text: str  # chunk text
    metadata: dict  # metadata dict


@dataclass
class GateReport:  # outcome of the quality gate
    total: int  # chunks checked
    issues: dict[str, int] = field(default_factory=dict)  # issue type -> count
    examples: dict[str, str] = field(default_factory=dict)  # issue type -> one example
    passed: bool = True  # gate decision

    def add(self, kind: str, example: str) -> None:  # record an issue
        self.issues[kind] = self.issues.get(kind, 0) + 1  # count
        self.examples.setdefault(kind, example[:80])  # keep first example


REQUIRED = ("source", "page", "doc_type")  # metadata keys that must exist


def approx_tokens(text: str) -> int:  # cheap token estimate (words x 1.3)
    return int(len(text.split()) * 1.3)  # avoids a tokenizer dependency


def check_one(c: Candidate, max_tokens: int, min_tokens: int) -> list[str]:  # issues for one chunk
    found: list[str] = []  # list of issue names
    t = c.text.strip()  # trimmed
    n = approx_tokens(t)  # tokens
    if not t:  # empty
        return ["empty"]  # stop here
    if n > max_tokens:  # oversize
        found.append("too_long")  # issue
    if n < min_tokens:  # undersize
        found.append("too_short")  # issue
    if any(k not in c.metadata for k in REQUIRED):  # metadata missing
        found.append("missing_metadata")  # issue
    if t[0].islower():  # probable mid-sentence start
        found.append("mid_sentence_start")  # issue
    if sum(ch.isalpha() for ch in t) / max(1, len(t)) < 0.5:  # mostly symbols/numbers: OCR garbage or tables
        found.append("low_text_ratio")  # issue
    return found  # all issues


async def quality_gate(chunks: list[Candidate], max_tokens: int = 600, min_tokens: int = 8,
                       max_bad_ratio: float = 0.05) -> GateReport:  # run all checks
    if not chunks:  # validate
        raise ValueError("no chunks to check")  # error
    rep = GateReport(total=len(chunks))  # report
    seen: set[str] = set()  # duplicate hashes
    results = await asyncio.gather(*(asyncio.to_thread(check_one, c, max_tokens, min_tokens) for c in chunks))  # parallel
    bad = 0  # chunks with any issue
    for c, found in zip(chunks, results):  # combine
        h = hashlib.md5(c.text.strip().lower().encode()).hexdigest()  # duplicate key (not for security)
        if h in seen:  # duplicate
            found = found + ["duplicate"]  # add issue
        seen.add(h)  # remember
        for kind in found:  # record each
            rep.add(kind, c.text)  # count
        bad += 1 if found else 0  # count bad chunks
    rep.passed = bad / len(chunks) <= max_bad_ratio  # gate decision
    return rep  # report


if __name__ == "__main__":  # demo
    meta = {"source": "t.pdf", "page": 1, "doc_type": "note"}  # good metadata
    items = [Candidate("Smartphones attract ten percent duty under heading 8517 of the schedule.", meta),
             Candidate("rate applies only to refurbished units", meta),  # mid-sentence start
             Candidate("Smartphones attract ten percent duty under heading 8517 of the schedule.", meta),  # duplicate
             Candidate("Batteries attract twenty percent duty under heading 8507 of the schedule.", {})]  # no metadata
    r = asyncio.run(quality_gate(items))  # run gate
    print(r.passed, r.issues)  # decision and counts
```

---

## 🟠 FastAPI Integration
Run the quality gate as part of the ingestion endpoint: if too many chunks are bad, reject the batch (HTTP 422) with a report instead of polluting the index.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app


class ChunkIn(BaseModel):  # one chunk in the request
    text: str  # chunk text
    metadata: dict  # metadata


class IngestIn(BaseModel):  # request
    chunks: list[ChunkIn]  # chunk list


@app.post("/ingest")  # route
async def ingest(req: IngestIn) -> dict:  # handler
    try:  # gate may raise on empty input
        rep = await quality_gate([Candidate(c.text, c.metadata) for c in req.chunks])  # check quality
    except ValueError as exc:  # no chunks
        raise HTTPException(422, str(exc))  # client error
    if not rep.passed:  # too many bad chunks
        raise HTTPException(422, {"message": "chunk quality gate failed", "issues": rep.issues, "examples": rep.examples})
    # ... embed and upsert into the vector DB here ...
    return {"indexed": rep.total, "issues": rep.issues}  # success summary
```

---

## 🔗 LangChain / LangGraph Connection
Model the pipeline as a LangGraph with a gate: `load -> clean -> split -> enrich_metadata -> lint -> (pass) embed_and_store / (fail) report`. The conditional edge after `lint` implements the quality gate.

```python
# from langgraph.graph import StateGraph, END
# graph = StateGraph(dict)
# for name, fn in [("load", load), ("clean", clean), ("split", split), ("enrich", enrich), ("lint", lint_node), ("store", store)]:
#     graph.add_node(name, fn)                       # one node per stage
# graph.set_entry_point("load")
# graph.add_edge("load", "clean"); graph.add_edge("clean", "split"); graph.add_edge("split", "enrich"); graph.add_edge("enrich", "lint")
# graph.add_conditional_edges("lint", lambda s: "store" if s["gate_passed"] else END, {"store": "store", END: END})
# graph.add_edge("store", END)
# app_graph = graph.compile()
from langchain_text_splitters import RecursiveCharacterTextSplitter  # the split stage uses a standard splitter

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40, separators=["\n\n", "\n", ". ", " ", ""])  # structure-first
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Copy-pasting chunk_size=1000, chunk_overlap=200 for every document type
✅ Correct: Choose per document type and verify with an eval set.

```python
# Wrong - same settings for FAQ, tariff table and legal prose
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # one-size-fits-all

# Right - strategy per type
STRATEGY = {"faq": "one record per chunk", "tariff_line": "one line + breadcrumb", "notes": "400 tokens, 10% overlap"}
```

❌ Mistake 2: Never looking at actual chunks
✅ Correct: Print and read 20 random chunks after every ingestion change. Many bugs are visible in seconds.

❌ Mistake 3: Skipping metadata and evaluation "for later"
✅ Correct: Add both from day one; retrofitting means re-ingesting everything.

❌ Mistake 4: Re-embedding everything on every update.
✅ Correct: Stable chunk ids and content hashes; embed only what changed.

---

## 🧠 Tricky Interview Question
**Q**: "You have one week to improve a RAG system whose answers are poor. You suspect chunking. What do you do, in order?"

**Answer**: (1) Collect real failing questions and label the right source passage. (2) Read what is retrieved for each failure (top-5 chunks) and classify the cause: bad extraction, cut-off answer, missing context, wrong version, exact-code miss, or noise. (3) Fix by cause, cheapest first: clean boilerplate and extraction, switch to structure-based splitting, add heading-path prefixes, add metadata filters, add hybrid search, use parent-child expansion; only then tune sizes or consider contextual/agentic chunking. (4) Measure with a golden set before and after, change one thing at a time. (5) Add a lint gate and CI regression. Looking at data comes before any tuning.

---

## ⚫ Interview Questions + Answers

Q1: What is the first thing to do when designing chunking?
A1: Look at the documents and the real questions users ask; these decide the natural chunk unit.

Q2: What chunk size and overlap would you start with?
A2: About 300-500 tokens with 10-15% overlap for prose; atomic records unsplit with no overlap; then evaluate.

Q3: Why is metadata part of chunking?
A3: It enables filtering, citations, versioning, access control and idempotent updates; it is cheapest to add when chunks are created.

Q4: How do you detect bad chunks automatically?
A4: Lint checks: empty, too short/long, duplicates, mid-sentence cuts, low text ratio, missing metadata; set a maximum bad-chunk ratio as a quality gate.

Q5: (Hard) How do you keep chunking quality from regressing over time?
A5: Golden-set evaluation in CI, quality gate at ingestion, monitoring of chunk-size distribution and retrieval metrics, versioned chunking configs, snapshot tests for each source format, and alerts when the source structure changes.

---

## 🔷 When to Use + When Not to Use
✅ Apply the full checklist when:
- RAG quality or cost matters in production
- Corpus is large, changing, or has several document types

❌ Keep it light when:
- Prototype or hackathon with a few documents
- Everything fits in the context window (no RAG needed)

---

## 📊 Visual Diagram
```
 sources ─► clean ─► split by STRUCTURE ─► split by SIZE ─► add context + metadata
                                                                  │
                                                          ┌───────▼────────┐
                                                          │  QUALITY GATE  │  lint + dedupe + metadata check
                                                          └───────┬────────┘
                                             fail ◄───────────────┤───────────────► pass
                                      report + stop                                  embed + store
                                                                                      │
                          golden-set eval (CI) ◄── monitor in production ◄────────────┘
```

---

## 💰 Cost Impact
- Cleaning and structure-based splitting reduce wasted tokens: typically 20-40% fewer tokens embedded and 20-40% fewer prompt tokens per query (less noise, smaller top_k).
- The lint gate is almost free (pure Python) and prevents re-indexing mistakes that would cost another full embedding run (for example 50M tokens x $0.02/1M = $1, plus engineer time).
- Stable ids and hashing avoid re-embedding unchanged chunks, often 90%+ savings on updates.
- Evaluation costs a few cents per run for retrieval metrics; LLM-judged runs cost more, so run nightly.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Quality gate | Automatic pass/fail check | स्वचालित pass/fail जाँच |
| Lint | Static check for problems | समस्याओं की जाँच |
| Self-contained chunk | Understandable alone | अकेले समझ आने वाला chunk |
| Golden set | Labelled eval questions | जाँच के लिए सही प्रश्न-उत्तर |
| Idempotent ingest | Re-run gives same state | दोबारा चलाने पर वही स्थिति |
| Regression | Quality drop after a change | बदलाव के बाद गिरावट |

---

## ⚡ 3-Line Summary
English: Good chunking respects structure, stays self-contained, uses sensible size and small overlap, and carries metadata. Lint chunks before indexing and evaluate with real questions. Look at the data first and tune last.
Hindi: अच्छी chunking structure का सम्मान करती है, self-contained रहती है, सही size और छोटा overlap रखती है और metadata साथ रखती है। Indexing से पहले chunks lint करो और असली questions से evaluate करो। पहले data देखो, tuning सबसे अंत में।

---

## ➡️ Next Topic
**181. RAG Complete** is already covered in this guide, so continue with **182. RAG vs Fine-tuning** - when retrieval beats training a model, and when it does not.
