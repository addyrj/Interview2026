---

# 171. Hierarchical Chunking
# हिंदी में: Hierarchical Chunking (कई स्तरों वाली chunking)

---

## 🔵 Simple Definition (English)
Hierarchical chunking builds a tree of chunks with several levels: document > chapter > section > paragraph. Each level has its own text or summary, and each node knows its parent and children. Retrieval can start at a high level ("which chapter?") and walk down to the exact paragraph, or start low and walk up for context.

## 🔵 सरल परिभाषा (Hindi)
Hierarchical chunking chunks का एक tree बनाती है जिसमें कई levels होते हैं: document > chapter > section > paragraph। हर node का अपना text या summary होता है और वह अपने parent और children को जानता है। Retrieval ऊपर से ("कौन सा chapter?") नीचे exact paragraph तक जा सकती है, या नीचे से ऊपर context के लिए।

---

## 🔴 Problem it Solves
- Parent-child has only two levels; large documents (500 pages) have natural structure with more levels.
- Searching all 100,000 paragraphs is slow and noisy; narrowing by chapter first is faster and more accurate.
- Questions can be broad ("summarise chapter 85 rules") or narrow ("duty for 8517.13.00"). One chunk size cannot serve both.

## 🔴 यह क्यों बना? (Hindi)
- Parent-child में सिर्फ दो levels हैं; 500 page के document में structure के कई levels होते हैं।
- 1,00,000 paragraphs में search धीमी और noisy है; पहले chapter से narrow करना तेज़ और सटीक है।
- Questions broad ("chapter 85 के rules का सार") भी होते हैं और narrow भी ("8517.13.00 की duty")। एक chunk size दोनों नहीं सँभाल सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Detect structure: headings, numbering, page ranges (levels L0..L3)
Step 2 → Create a node per unit: {id, level, parent_id, children_ids, text}
Step 3 → Leaf nodes (paragraphs) hold raw text, split to ~200-300 tokens
Step 4 → Internal nodes (section, chapter) hold a SUMMARY of their children
Step 5 → Embed nodes at the levels you want to search (leaf + section summaries)
Step 6 → Query: search section summaries first, keep top sections
Step 7 → Search leaves ONLY inside those sections (filter by ancestor id)
Step 8 → Return leaf text + its ancestor breadcrumb (and, for broad questions, the summaries)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Structure पहचानो: headings, numbering, page ranges (L0..L3)
Step 2 → हर unit का node: {id, level, parent_id, children_ids, text}
Step 3 → Leaf (paragraph) में raw text, ~200-300 tokens
Step 4 → ऊपर के nodes (section, chapter) में बच्चों का SUMMARY
Step 5 → जिन levels पर search करनी है उन्हें embed करो
Step 6 → Query: पहले section summaries में खोजो, top sections रखो
Step 7 → फिर सिर्फ उन sections के अंदर leaves खोजो
Step 8 → Leaf text + ancestor breadcrumb लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The full tariff has 21 sections, 97 chapters, about 1,200 headings and about 10,000 lines. For the query "lithium battery for e-bike", step 1 searches chapter summaries and picks Chapter 85 (electrical) and 87 (vehicles). Step 2 searches headings only inside those chapters, then step 3 retrieves tariff lines only inside the best headings. This cuts the candidate set from 10,000 to a few hundred and avoids wrong-chapter lookalikes.

**Amazon style**: Category tree Electronics > Batteries > Lithium; search the category summary first, then the products inside it.

## 🟡 Real Example Hindi mein
**Tariff System**: पूरे tariff में 21 sections, 97 chapters, ~1,200 headings, ~10,000 lines हैं। "e-bike की lithium battery" query पर पहले chapter summaries में खोजकर Chapter 85 और 87 चुने जाते हैं, फिर सिर्फ उनके headings में, फिर सिर्फ चुने headings की lines में। Candidates 10,000 से कुछ सौ रह जाते हैं और गलत-chapter वाले lookalikes से बचाव होता है।

**Amazon**: Category tree Electronics > Batteries > Lithium; पहले category summary में खोजो, फिर उसके products में।

---

## 💻 Code Example — Basic
```python
# Basic hierarchical retrieval in pure Python: chapter -> section -> paragraph
import re  # tokenizer

tree = {  # a tiny 3-level tree: chapter -> section -> paragraphs
    "Ch85 Electrical": {
        "8517 Telephones": ["Smartphones attract ten percent duty.", "Cordless phones attract twelve percent duty."],
        "8507 Batteries": ["Lithium batteries attract twenty percent duty.", "Lead acid batteries attract fifteen percent duty."],
    },
    "Ch87 Vehicles": {
        "8711 Motorcycles": ["Electric bikes attract fifteen percent duty."],
    },
}  # hand-made data

def words(t: str) -> set[str]:  # simple tokenizer
    return set(re.findall(r"[a-z0-9]+", t.lower()))  # lowercase words

def overlap(q: str, t: str) -> int:  # similarity = shared words
    return len(words(q) & words(t))  # count

def search(q: str) -> tuple[str, str, str]:  # walk top-down
    chapter = max(tree, key=lambda c: overlap(q, c + " " + " ".join(tree[c])))  # best chapter by its text
    section = max(tree[chapter], key=lambda s: overlap(q, s))  # best section inside chapter
    para = max(tree[chapter][section], key=lambda p: overlap(q, p))  # best paragraph inside section
    return chapter, section, para  # breadcrumb + text

print(search("lithium batteries duty"))  # ('Ch85 Electrical', '8507 Batteries', 'Lithium batteries ...')
```

## 💻 Code Example — Advanced
```python
# Production-style tree: nodes with parent links, summaries from an injected async summariser,
# top-down retrieval with ancestor filtering. Embedding = injected async function.
from __future__ import annotations  # modern hints

import asyncio  # async
import math  # cosine
from dataclasses import dataclass, field  # containers
from typing import Awaitable, Callable  # types

Embedder = Callable[[list[str]], Awaitable[list[list[float]]]]  # embed function
Summariser = Callable[[str], Awaitable[str]]  # summary function (LLM in production)


@dataclass
class Node:  # one tree node
    id: str  # unique id
    level: int  # 0 chapter, 1 section, 2 paragraph
    text: str  # raw text (leaf) or summary (internal)
    parent_id: str | None = None  # link up
    children: list[str] = field(default_factory=list)  # links down
    vec: list[float] = field(default_factory=list)  # embedding


class HierIndex:  # the index
    def __init__(self, embed: Embedder, summarise: Summariser) -> None:
        self.embed, self.summarise = embed, summarise  # dependencies
        self.nodes: dict[str, Node] = {}  # id -> node

    async def build(self, data: dict[str, dict[str, list[str]]]) -> None:  # data: chapter->section->paras
        for ch, sections in data.items():  # chapters
            ch_id = f"c:{ch}"  # chapter id
            self.nodes[ch_id] = Node(ch_id, 0, "")  # placeholder, summary later
            for sec, paras in sections.items():  # sections
                s_id = f"{ch_id}/s:{sec}"  # section id
                self.nodes[s_id] = Node(s_id, 1, "", ch_id)  # placeholder
                self.nodes[ch_id].children.append(s_id)  # link
                for i, p in enumerate(paras):  # paragraphs
                    p_id = f"{s_id}/p:{i}"  # paragraph id
                    self.nodes[p_id] = Node(p_id, 2, p, s_id)  # leaf with raw text
                    self.nodes[s_id].children.append(p_id)  # link
                self.nodes[s_id].text = await self.summarise(f"{sec}: " + " ".join(paras))  # section summary
            self.nodes[ch_id].text = await self.summarise(
                f"{ch}: " + " ".join(self.nodes[s].text for s in self.nodes[ch_id].children))  # chapter summary
        try:  # embed all nodes in one call
            vecs = await self.embed([n.text for n in self.nodes.values()])  # vectors
        except Exception as exc:  # wrap error
            raise RuntimeError("embedding failed") from exc  # message
        for n, v in zip(self.nodes.values(), vecs):  # attach
            n.vec = v  # set

    @staticmethod
    def _cos(a: list[float], b: list[float]) -> float:  # cosine
        d = sum(x * y for x, y in zip(a, b))  # dot
        n = (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1.0  # norms
        return d / n  # similarity

    def _best(self, qv: list[float], ids: list[str], k: int) -> list[str]:  # top-k among ids
        return sorted(ids, key=lambda i: -self._cos(qv, self.nodes[i].vec))[:k]  # ranked

    async def search(self, q: str, k_per_level: int = 1) -> list[str]:  # top-down search
        qv = (await self.embed([q]))[0]  # embed query
        level0 = [i for i, n in self.nodes.items() if n.level == 0]  # chapters
        chosen = self._best(qv, level0, k_per_level)  # best chapters
        for _ in range(2):  # descend two levels
            kids = [c for i in chosen for c in self.nodes[i].children]  # children of chosen
            chosen = self._best(qv, kids, k_per_level)  # best children
        return [f"{i} :: {self.nodes[i].text}" for i in chosen]  # leaf text with its path in the id


async def toy_embed(texts: list[str]) -> list[list[float]]:  # letter-count embedder (demo only)
    await asyncio.sleep(0)  # async placeholder
    return [[t.lower().count(c) for c in "abcdefghijklmnopqrstuvwxyz"] for t in texts]  # vectors


async def toy_summary(text: str) -> str:  # trivial "summary" = first 80 chars (LLM in production)
    await asyncio.sleep(0)  # async placeholder
    return text[:80]  # truncated text


if __name__ == "__main__":  # demo
    async def main() -> None:  # async main
        idx = HierIndex(toy_embed, toy_summary)  # create index
        await idx.build({"Ch85": {"8517 phones": ["smartphones duty ten percent"],
                                  "8507 batteries": ["lithium batteries duty twenty percent"]},
                         "Ch87": {"8711 bikes": ["electric bikes duty fifteen percent"]}})  # build
        print(await idx.search("lithium battery duty"))  # search
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Expose a `/search` endpoint with a `mode`: `broad` returns section/chapter summaries (for "explain" questions), `precise` returns leaf paragraphs with their breadcrumb.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # pydantic v2

app = FastAPI()  # app
index = HierIndex(toy_embed, toy_summary)  # replace with real embedder/summariser


class SearchIn(BaseModel):  # request
    query: str = Field(min_length=2)  # question
    mode: str = Field(default="precise", pattern="^(broad|precise)$")  # broad or precise


@app.post("/search")  # route
async def search(req: SearchIn) -> dict:  # handler
    if not index.nodes:  # index not built
        raise HTTPException(503, "index not ready")  # service unavailable
    if req.mode == "precise":  # leaf search
        return {"hits": await index.search(req.query)}  # leaves
    qv = (await index.embed([req.query]))[0]  # broad: rank section summaries
    secs = [i for i, n in index.nodes.items() if n.level == 1]  # sections
    return {"hits": [index.nodes[i].text for i in index._best(qv, secs, 3)]}  # summaries
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `MultiVectorRetriever` (store summaries/children in the vector store, full docs in a docstore) and a LlamaIndex-style hierarchical approach (`HierarchicalNodeParser` + `AutoMergingRetriever`) exists in LlamaIndex. In LangGraph, model the descent as a loop: `pick_chapter -> pick_section -> pick_leaf`, each a conditional node.

```python
from langchain.retrievers.multi_vector import MultiVectorRetriever  # summary -> full doc retriever
from langchain.storage import InMemoryStore  # docstore
# retriever = MultiVectorRetriever(vectorstore=summary_vectorstore, docstore=InMemoryStore(), id_key="doc_id")
# retriever.vectorstore.add_documents(summary_docs)   # each summary has metadata {"doc_id": ...}
# retriever.docstore.mset(list(zip(doc_ids, full_docs)))  # full sections
# docs = retriever.invoke("lithium battery duty")  # matches summaries, returns full sections
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Summaries that drop key identifiers (HS codes, numbers)
✅ Correct: Summaries must keep codes and names so top-down routing works.

```python
# Wrong - vague summary, routing fails
summary = "This chapter covers machines."  # no code, no names

# Right - routing-friendly summary
summary = "Chapter 85: electrical machinery - phones 8517, batteries 8507, TVs 8528"  # keeps codes
```

❌ Mistake 2: Pruning too early (top-1 chapter) - one routing error loses the answer.
✅ Correct: Keep top-2 or top-3 at upper levels, narrow later, or add a flat fallback search.

❌ Mistake 3: Generating summaries on every re-index.
✅ Correct: Cache summaries by content hash; only re-summarise changed sections.

---

## 🧠 Tricky Interview Question
**Q**: "Hierarchical retrieval is faster but accuracy on cross-chapter questions dropped. Why and what do you do?"

**Answer**: Top-down routing commits to a branch early. For questions that span branches (for example "duty on phone batteries" touches Chapter 85 twice or Chapters 85 and 87), a wrong or narrow choice at the top removes the right leaves. Fixes: keep top-k > 1 at each level, add a flat leaf-level search in parallel and merge (reciprocal rank fusion), use query decomposition for multi-topic questions, and measure routing accuracy per level separately.

---

## ⚫ Interview Questions + Answers

Q1: What is hierarchical chunking?
A1: A tree of chunks at several granularities (document, chapter, section, paragraph) with parent/child links and often summaries at internal nodes.

Q2: How is it different from parent-child chunking?
A2: Parent-child is a special case with two levels. Hierarchical has more levels and supports top-down narrowing and summaries.

Q3: What goes into internal nodes?
A3: A summary of children (LLM generated) or heading text plus key terms. They are the routing layer.

Q4: What are the benefits?
A4: Faster search (smaller candidate sets), better precision, support for both broad and narrow questions, and natural breadcrumbs for citations.

Q5: (Hard) How do you keep the tree correct when documents change?
A5: Use stable ids from content hashes; on change, rebuild only the affected branch and recompute summaries up to the root; version the tree; run integrity checks (every child has a parent, no orphan leaves).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Very large, well-structured corpora (tariffs, legal codes, manuals)
- Both summary-style and detail-style questions are asked

❌ Avoid when:
- Small corpus (flat search is fine)
- Documents have no real structure
- You cannot afford summary generation

---

## 📊 Visual Diagram
```
 L0 Document ─ "Customs Tariff"
 │
 ├─ L1 Chapter 85 (summary) ◄── search here first
 │    ├─ L2 Heading 8517 (summary)
 │    │    ├─ L3 line 8517.13.00  (leaf text)  ◄── answer comes from here
 │    │    └─ L3 line 8517.18.00
 │    └─ L2 Heading 8507 (summary)
 └─ L1 Chapter 87 (summary)

 query ─► rank chapters ─► rank headings (in chosen chapters) ─► rank lines (in chosen headings)
```

---

## 💰 Cost Impact
- Extra cost at index time: one summary call per internal node. Example: 1,300 internal nodes x ~600 input tokens + 100 output tokens at gpt-4o-mini prices ($0.15/$0.60 per 1M) = about $0.12 + $0.08 = $0.20 one-time. Cheap.
- Query time: top-down search needs 3 small searches, but over small candidate sets, so latency usually drops.
- Optimise: summarise with a small model, cache by content hash, embed summaries with a cheap embedding model, skip upper levels for queries that contain an exact HS code.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Node | One chunk in the tree | Tree में एक chunk |
| Leaf | Lowest-level raw chunk | सबसे निचला chunk |
| Internal node | Summary of children | बच्चों का सार |
| Top-down retrieval | Narrow level by level | ऊपर से नीचे खोज |
| Routing | Choosing the branch | सही शाखा चुनना |
| Breadcrumb | Path from root | Root से path |

---

## ⚡ 3-Line Summary
English: Hierarchical chunking builds a multi-level tree with summaries at internal nodes. Retrieval narrows from chapter to section to paragraph, which is faster and more precise. Keep top-k above 1 at upper levels to avoid routing errors.
Hindi: Hierarchical chunking में कई levels का tree बनता है और ऊपरी nodes में summary रहती है। Retrieval chapter से section और फिर paragraph तक narrow होती है - तेज़ और सटीक। ऊपरी levels पर top-k 1 से ज़्यादा रखो ताकि routing error से बचो।

---

## ➡️ Next Topic
**172. Late Chunking** - embed the whole document first, then chunk the embeddings so each chunk keeps global context.
