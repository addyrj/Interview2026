---

# 170. Parent-Child Chunking
# हिंदी में: Parent-Child Chunking (छोटे chunk से खोजो, बड़ा chunk दो)

---

## 🔵 Simple Definition (English)
Parent-child chunking stores two levels: small "child" chunks (about 100-300 tokens) used for searching, and bigger "parent" chunks (about 800-2000 tokens, or a whole section) given to the LLM. You search with the sharp child, then return its parent for full context. Also called "small-to-big" retrieval.

## 🔵 सरल परिभाषा (Hindi)
Parent-child chunking में दो level होते हैं: छोटे "child" chunks (100-300 tokens) जिनसे search होती है, और बड़े "parent" chunks (800-2000 tokens या पूरा section) जो LLM को दिए जाते हैं। Search तेज़ child से, context पूरा parent से। इसे "small-to-big" retrieval भी कहते हैं।

---

## 🔴 Problem it Solves
- Small chunks give precise search but too little context for the LLM to answer.
- Big chunks give context but their embeddings are blurry, so search is less precise.
- You cannot have both with a single chunk size. Parent-child decouples "what we search" from "what we send".

## 🔴 यह क्यों बना? (Hindi)
- छोटे chunks से search precise होती है पर LLM के लिए context कम पड़ता है।
- बड़े chunks में context होता है पर embedding धुंधली, search कमज़ोर।
- एक size से दोनों नहीं मिलते। Parent-child "क्या search करें" और "क्या भेजें" को अलग कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Split the document into PARENT chunks (a section or ~1000 tokens)
Step 2 → Split each parent into CHILD chunks (~200 tokens)
Step 3 → Give every child a parent_id; store parents in a doc store (key -> text)
Step 4 → Embed only the CHILDREN into the vector store
Step 5 → Query: embed question, find top-k children
Step 6 → Map children to parent_ids, deduplicate (many children can share one parent)
Step 7 → Fetch parents from the doc store, send the top 1-3 parents to the LLM
Step 8 → Answer + cite the parent section
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Document को PARENT chunks में बाँटो (section या ~1000 tokens)
Step 2 → हर parent को CHILD chunks में बाँटो (~200 tokens)
Step 3 → हर child को parent_id दो; parents doc store में रखो
Step 4 → सिर्फ CHILDREN को embed करके vector store में डालो
Step 5 → Query: top-k children खोजो
Step 6 → Children से parent_ids निकालो, duplicates हटाओ
Step 7 → Doc store से parents लाओ, top 1-3 parents LLM को भेजो
Step 8 → जवाब + parent section cite करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A child chunk "Smartphones 8517.13.00 duty 10%" matches the query precisely. But to classify correctly the LLM also needs the surrounding heading 8517 with its exclusions ("does not include ... "). The parent is the whole heading section (8517), so the LLM sees the line plus the exclusions and Chapter note references.

**Amazon / Zomato style**: Child = a single review sentence or a dish line (precise match for "spicy paneer"). Parent = the whole review or the full restaurant menu section, so the answer has context.

## 🟡 Real Example Hindi mein
**Tariff System**: Child chunk "Smartphones 8517.13.00 duty 10%" query से बिल्कुल match करता है। पर सही classification के लिए LLM को heading 8517 की exclusions भी चाहिए। Parent = पूरा heading section (8517), तो LLM को line + exclusions + notes के reference मिलते हैं।

**Amazon / Zomato**: Child = review का एक वाक्य या dish line। Parent = पूरा review या menu section।

---

## 💻 Code Example — Basic
```python
# Basic parent-child retrieval in pure Python (word-overlap "embedding", no API needed)
import re  # tokenizer

doc = (  # document with two sections
    "# Heading 8517\n"
    "Smartphones attract ten percent duty. Cordless phones attract twelve percent duty. "
    "Exclusion: parts of phones are classified elsewhere.\n"
    "# Heading 8507\n"
    "Lithium batteries attract twenty percent duty. Lead acid batteries attract fifteen percent duty."
)  # sample text

parents = [p.strip() for p in re.split(r"(?m)^# ", doc) if p.strip()]  # parent = section
store: dict[int, str] = dict(enumerate(parents))  # parent doc store: id -> text

children: list[tuple[int, str]] = []  # (parent_id, child_text)
for pid, ptext in store.items():  # each parent
    for sent in re.split(r"(?<=[.])\s+", ptext):  # child = sentence
        children.append((pid, sent))  # remember parent id

def words(t: str) -> set[str]:  # tokenizer
    return set(re.findall(r"[a-z]+", t.lower()))  # unique lowercase words

def search(query: str, k: int = 2) -> list[int]:  # find parent ids
    scored = sorted(children, key=lambda c: -len(words(query) & words(c[1])))  # rank children
    seen: list[int] = []  # ordered unique parent ids
    for pid, _ in scored[:k]:  # top-k children
        if pid not in seen:  # deduplicate
            seen.append(pid)  # keep order
    return seen  # parent ids

for pid in search("duty on smartphones"):  # run a query
    print("PARENT SENT TO LLM:", store[pid])  # whole section, including the exclusion line
```

## 💻 Code Example — Advanced
```python
# Production: parent-child index with injected embedder, dedup, token budget, async API.
from __future__ import annotations  # modern hints

import asyncio  # async
import math  # cosine
import uuid  # ids
from dataclasses import dataclass, field  # containers
from typing import Awaitable, Callable  # types

Embedder = Callable[[list[str]], Awaitable[list[list[float]]]]  # async embedding function


@dataclass
class Child:  # small searchable chunk
    id: str  # child id
    parent_id: str  # link to parent
    text: str  # child text
    vec: list[float] = field(default_factory=list)  # embedding


class ParentChildIndex:  # the index
    def __init__(self, embed: Embedder, child_size: int = 40, parent_size: int = 160) -> None:
        if child_size >= parent_size:  # children must be smaller
            raise ValueError("child_size must be < parent_size")  # guard
        self.embed = embed  # embedder
        self.child_size = child_size  # words per child
        self.parent_size = parent_size  # words per parent
        self.parents: dict[str, str] = {}  # doc store
        self.children: list[Child] = []  # vector store (in memory)

    @staticmethod
    def _windows(words: list[str], size: int) -> list[str]:  # fixed windows
        return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]  # slices

    async def add(self, text: str) -> int:  # index one document
        words = text.split()  # tokens ~ words
        new: list[Child] = []  # children of this doc
        for ptext in self._windows(words, self.parent_size):  # parents
            pid = uuid.uuid4().hex  # parent id
            self.parents[pid] = ptext  # store parent
            for ctext in self._windows(ptext.split(), self.child_size):  # children
                new.append(Child(uuid.uuid4().hex, pid, ctext))  # create child
        try:  # embedding may fail
            vecs = await self.embed([c.text for c in new])  # embed children only
        except Exception as exc:  # wrap error
            raise RuntimeError("embedding failed during indexing") from exc  # message
        for c, v in zip(new, vecs):  # attach vectors
            c.vec = v  # set
        self.children.extend(new)  # add to index
        return len(new)  # number of children

    @staticmethod
    def _cos(a: list[float], b: list[float]) -> float:  # cosine similarity
        d = sum(x * y for x, y in zip(a, b))  # dot
        n = (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1.0  # norms
        return d / n  # score

    async def query(self, q: str, k_children: int = 6, max_parents: int = 2) -> list[str]:
        if not self.children:  # empty index
            return []  # nothing to find
        qv = (await self.embed([q]))[0]  # embed query
        ranked = sorted(self.children, key=lambda c: -self._cos(qv, c.vec))  # best children first
        parent_ids: list[str] = []  # ordered unique parents
        for c in ranked[:k_children]:  # top children
            if c.parent_id not in parent_ids:  # dedupe
                parent_ids.append(c.parent_id)  # keep
            if len(parent_ids) == max_parents:  # token budget reached
                break  # stop
        return [self.parents[p] for p in parent_ids]  # return parents


async def letter_embed(texts: list[str]) -> list[list[float]]:  # toy embedder for the demo
    await asyncio.sleep(0)  # pretend async
    return [[t.lower().count(ch) for ch in "abcdefghijklmnopqrstuvwxyz"] for t in texts]  # letter counts


if __name__ == "__main__":  # demo
    async def main() -> None:  # async main
        idx = ParentChildIndex(letter_embed, child_size=8, parent_size=24)  # small sizes for demo
        n = await idx.add("Smartphones heading 8517 duty ten percent exclusion parts of phones go elsewhere "
                          "Batteries heading 8507 duty twenty percent lithium and lead acid types included")  # text
        print("children:", n)  # count
        print(await idx.query("smartphones duty"))  # returns parents, not tiny children
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Two endpoints: `/index` builds the parent-child index; `/ask` retrieves parents and calls the LLM. The index object lives in app state. In production the doc store would be Redis/Postgres and the vectors in a vector DB.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app
index = ParentChildIndex(letter_embed)  # global index (replace embedder with a real one)


class DocIn(BaseModel):  # indexing body
    text: str  # document text


class AskIn(BaseModel):  # question body
    question: str  # user question


@app.post("/index")  # route
async def add_doc(d: DocIn) -> dict:  # index handler
    try:  # guard failures
        return {"children": await index.add(d.text)}  # return count
    except RuntimeError as exc:  # embedding failure
        raise HTTPException(502, str(exc))  # upstream error


@app.post("/ask")  # route
async def ask(a: AskIn) -> dict:  # query handler
    parents = await index.query(a.question)  # retrieve parent contexts
    if not parents:  # nothing indexed
        raise HTTPException(404, "no documents indexed")  # not found
    context = "\n---\n".join(parents)  # build prompt context
    return {"context_chars": len(context), "context": context}  # (call the LLM here)
```

---

## 🔗 LangChain / LangGraph Connection
LangChain provides `ParentDocumentRetriever`: pass a child splitter, an optional parent splitter, a vector store (for children) and a docstore (for parents).

```python
from langchain.retrievers import ParentDocumentRetriever  # retriever
from langchain.storage import InMemoryStore  # parent doc store
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitters
# from langchain_chroma import Chroma ; from langchain_openai import OpenAIEmbeddings

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1500)  # big parents
child_splitter = RecursiveCharacterTextSplitter(chunk_size=300)  # small children
# vectorstore = Chroma(collection_name="children", embedding_function=OpenAIEmbeddings())  # child vectors
# retriever = ParentDocumentRetriever(vectorstore=vectorstore, docstore=InMemoryStore(),
#                                     child_splitter=child_splitter, parent_splitter=parent_splitter)
# retriever.add_documents(docs)  # splits + indexes
# retriever.invoke("duty on smartphones")  # returns PARENT documents
# In LangGraph, use this retriever inside the 'retrieve' node of a RAG graph.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Embedding the parents too
✅ Correct: Embed only children; parents live in the doc store. Embedding both wastes cost and mixes granularities.

```python
# Wrong - parents and children in the same vector index
vectors = embed(parents + children)  # duplicates content, blurry hits

# Right - children only
vectors = embed(children)  # parents fetched by parent_id
```

❌ Mistake 2: Not deduplicating parents, so the same parent is sent 3 times.
✅ Correct: Collect unique parent_ids in rank order.

❌ Mistake 3: Parents so large that 3 of them blow the prompt budget.
✅ Correct: Cap parent size (about 1000-1500 tokens) and `max_parents`.

---

## 🧠 Tricky Interview Question
**Q**: "With parent-child chunking, recall improved but your LLM bill doubled. What happened and how do you fix it without losing quality?"

**Answer**: Each retrieval now sends full parents (for example 3 x 1500 = 4500 tokens) rather than small chunks (3 x 200 = 600). Fixes: (1) rerank children, then expand only the top 1-2 parents; (2) shrink parents to section-sized ~800 tokens; (3) expand to the child plus its neighbours (window) instead of the full parent; (4) use a cheaper model for the first pass; (5) cache by parent_id and use prompt caching for frequent parents. Always track tokens per query as a metric next to recall.

---

## ⚫ Interview Questions + Answers

Q1: What is parent-child chunking?
A1: Index small child chunks for search, store bigger parent chunks, and return the parent of the matching child to the LLM.

Q2: Which chunks do you embed?
A2: Only the children. Parents are stored in a docstore and fetched by id.

Q3: How do child and parent sizes compare?
A3: Typical: child 100-300 tokens, parent 800-2000 tokens or one section. Ratio about 4-8x.

Q4: Parent-child vs just using bigger chunks?
A4: Bigger chunks give blurry embeddings. Parent-child keeps precise search (small embedding) and rich context (large parent).

Q5: (Hard) Trade-offs and failure modes?
A5: Higher prompt tokens, extra storage layer, and consistency risk (children and parents out of sync after updates). Mitigate with ids derived from content hashes, transactional updates, a parent token cap, and monitoring "parent fetch misses".

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers need surrounding context (legal notes, manuals, policies)
- Questions are specific but explanations are long

❌ Avoid when:
- Documents are already short and atomic (FAQ, reviews)
- Very tight token budget or latency budget with no reranker

---

## 📊 Visual Diagram
```
 Document
   │
   ├─ PARENT 1 (section, ~1000 tok) ──► docstore[p1]
   │     ├─ child 1a (200 tok) ┐
   │     ├─ child 1b           ├─► embed ─► vector store (children only)
   │     └─ child 1c           ┘      each child has parent_id = p1
   └─ PARENT 2 ...

 query ─► embed ─► top-k children ─► unique parent_ids ─► docstore ─► PARENTS ─► LLM
```

---

## 💰 Cost Impact
- Embedding cost is the same as plain chunking (children cover the whole text once, no overlap needed).
- Prompt cost rises: top 2 parents of 1000 tokens = 2000 tokens vs 3 children of 200 = 600 tokens. At $0.15 per 1M input: $0.0003 vs $0.00009 per query; 100K queries/day = $30 vs $9.
- Optimise: rerank before expanding, expand only the top 1-2 parents, cap parent size, use prompt caching for repeated parents, keep a small model for simple queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parent chunk | Large context chunk | बड़ा context chunk |
| Child chunk | Small search chunk | छोटा search chunk |
| Docstore | Key-value store of parents | Parents का store |
| Small-to-big | Search small, return big | छोटा खोजो, बड़ा दो |
| parent_id | Link from child to parent | Child से parent की कड़ी |
| Deduplicate | Remove repeated parents | दोहराव हटाना |

---

## ⚡ 3-Line Summary
English: Search with small child chunks and answer with their bigger parent chunks. Embed only children; keep parents in a docstore linked by parent_id. Control cost by expanding only the top 1-2 parents.
Hindi: छोटे child chunks से search करो और उनके बड़े parent chunks से जवाब दो। सिर्फ children embed करो; parents docstore में parent_id से जुड़े रहें। सिर्फ top 1-2 parents expand करके cost कंट्रोल करो।

---

## ➡️ Next Topic
**171. Hierarchical Chunking** - more than two levels: document, chapter, section, paragraph, with summaries.
