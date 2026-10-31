---

# 174. Agentic Chunking
# हिंदी में: Agentic Chunking (LLM खुद तय करे कि chunk कहाँ कटे)

---

## 🔵 Simple Definition (English)
In agentic chunking an LLM "agent" reads the text and decides where to cut and which pieces belong together. Typical recipe: break the text into small self-contained statements (propositions), then for each statement ask the LLM "does this belong to an existing chunk, or should I start a new one?". Chunks end up grouped by meaning, not by length or punctuation.

## 🔵 सरल परिभाषा (Hindi)
Agentic chunking में एक LLM "agent" text पढ़कर तय करता है कि कहाँ काटना है और कौन से हिस्से साथ रहें। आम तरीका: text को छोटे, अपने-आप में पूरे वाक्यों (propositions) में तोड़ो, फिर हर वाक्य के लिए LLM से पूछो "यह किसी मौजूदा chunk का हिस्सा है या नया chunk शुरू करें?"। Chunks अर्थ के आधार पर बनते हैं, लंबाई या punctuation के आधार पर नहीं।

---

## 🔴 Problem it Solves
- Rule-based splitters (size, headings, regex) cannot understand meaning: two paragraphs about the same topic may be separated, or two topics glued together.
- Messy sources (transcripts, emails, scraped pages, OCR text) have no reliable structure.
- Pronouns and references ("they", "this rate") make chunks unreadable alone; propositions rewrite them into standalone facts.

## 🔴 यह क्यों बना? (Hindi)
- Rule-based splitters (size, headings, regex) अर्थ नहीं समझते: एक ही topic के दो paragraphs अलग हो सकते हैं या दो topics जुड़ सकते हैं।
- Messy sources (transcripts, emails, scraped pages, OCR) में भरोसेमंद structure नहीं होता।
- Pronouns ("they", "this rate") chunk को अकेले अपठनीय बना देते हैं; propositions उन्हें standalone facts में बदल देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Split raw text into sentences/paragraphs (cheap, rule-based)
Step 2 → LLM rewrites each piece into standalone propositions
         ("They attract 10%" -> "Smartphones attract 10% duty")
Step 3 → Start with an empty list of chunks (each has a title + summary)
Step 4 → For each proposition ask the LLM: "Which chunk does it belong to? or NEW"
Step 5 → If a chunk matches, append the proposition and refresh title/summary
Step 6 → If NEW, create a chunk with an LLM-written title and summary
Step 7 → Enforce limits: max chunk size, min size, max number of chunks to compare
Step 8 → Embed chunks (title + summary + propositions) and store with metadata
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Raw text को sentences/paragraphs में बाँटो (सस्ता, rule-based)
Step 2 → LLM हर टुकड़े को standalone propositions में बदलता है
Step 3 → खाली chunk list से शुरू करो (हर chunk का title + summary)
Step 4 → हर proposition के लिए LLM से पूछो: "कौन सा chunk? या NEW"
Step 5 → Match मिले तो proposition जोड़ो और title/summary refresh करो
Step 6 → NEW हो तो नया chunk बनाओ, LLM title और summary लिखे
Step 7 → Limits लगाओ: max size, min size, compare किए जाने वाले chunks की संख्या
Step 8 → Chunks embed करके metadata के साथ store करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Officer chat transcripts and email threads discuss many goods at once: "For the phones, use 8517.13. By the way the batteries inside are separate - 8507. Back to phones: the duty is 10%". A size-based splitter mixes phones and batteries. An agentic chunker produces two chunks: "Smartphones (8517.13): duty 10%" and "Lithium batteries (8507)", even though the text interleaves them.

**Zomato style**: A long customer-support call transcript jumps between "refund", "delivery delay" and "coupon". Agentic chunking groups all refund statements into one chunk and all delay statements into another.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer chat और email threads में कई goods एक साथ आते हैं: "Phones के लिए 8517.13। वैसे अंदर की batteries अलग हैं - 8507। वापस phones: duty 10%"। Size-based splitter phones और batteries मिला देगा। Agentic chunker दो chunks बनाता है: "Smartphones (8517.13): duty 10%" और "Lithium batteries (8507)", भले ही text में वे interleaved हों।

**Zomato**: Support call transcript "refund", "delivery delay" और "coupon" के बीच कूदता है। Agentic chunking सारे refund वाक्य एक chunk में और delay वाले दूसरे में रखता है।

---

## 💻 Code Example — Basic
```python
# Basic agentic-style grouping WITHOUT an API: a keyword "agent" decides which chunk a statement joins.
statements = [  # already standalone propositions
    "Smartphones are classified under 8517.13.",
    "Lithium batteries are classified under 8507.",
    "Smartphones attract ten percent duty.",
    "Lithium batteries attract twenty percent duty.",
]

TOPICS = {"smartphones": "Smartphones", "batteries": "Batteries"}  # keyword -> chunk title

def decide(statement: str, chunks: dict[str, list[str]]) -> str:  # the "agent" decision
    for key, title in TOPICS.items():  # look for a known topic word
        if key in statement.lower():  # match found
            return title if title in chunks else "NEW:" + title  # existing chunk or create new
    return "NEW:Misc"  # unknown topic -> new misc chunk

chunks: dict[str, list[str]] = {}  # title -> list of statements
for s in statements:  # process in order
    choice = decide(s, chunks)  # ask the agent
    title = choice.removeprefix("NEW:")  # chunk title
    chunks.setdefault(title, []).append(s)  # add (creating the chunk if needed)

for title, items in chunks.items():  # show result
    print(title, "->", items)  # statements are grouped by meaning even though they were interleaved
```

## 💻 Code Example — Advanced
```python
# Production-style agentic chunker. The LLM is injected: `decide(statement, chunk_summaries)` must
# return an existing chunk id or "NEW". A heuristic stub keeps the file runnable offline.
from __future__ import annotations  # modern hints

import asyncio  # async
import re  # tokenizer for the stub
from dataclasses import dataclass, field  # containers
from typing import Awaitable, Callable  # types

Decide = Callable[[str, dict[int, str]], Awaitable[str]]  # (statement, {id: summary}) -> "id" | "NEW"
Summarise = Callable[[list[str]], Awaitable[str]]  # statements -> short title/summary


@dataclass
class AChunk:  # one agentic chunk
    id: int  # chunk id
    statements: list[str] = field(default_factory=list)  # member statements
    summary: str = ""  # title/summary kept up to date


class AgenticChunker:  # the chunker
    def __init__(self, decide: Decide, summarise: Summarise, max_statements: int = 12,
                 max_candidates: int = 20) -> None:
        self.decide, self.summarise = decide, summarise  # LLM functions
        self.max_statements = max_statements  # cap per chunk
        self.max_candidates = max_candidates  # cap on chunks shown to the LLM (cost control)
        self.chunks: dict[int, AChunk] = {}  # id -> chunk
        self._next = 0  # id counter

    async def add(self, statement: str) -> int:  # place one statement
        if not statement.strip():  # validate
            raise ValueError("empty statement")  # error
        recent = dict(list({i: c.summary for i, c in self.chunks.items()}.items())[-self.max_candidates:])  # candidates
        try:  # LLM can fail
            choice = await self.decide(statement, recent) if recent else "NEW"  # first statement -> NEW
        except Exception:  # fall back safely
            choice = "NEW"  # never lose a statement
        cid = int(choice) if choice.isdigit() and int(choice) in self.chunks else None  # validate LLM output
        if cid is None or len(self.chunks[cid].statements) >= self.max_statements:  # new or full
            cid = self._next  # allocate id
            self._next += 1  # advance
            self.chunks[cid] = AChunk(cid)  # create chunk
        self.chunks[cid].statements.append(statement)  # add statement
        self.chunks[cid].summary = await self.summarise(self.chunks[cid].statements)  # refresh summary
        return cid  # where it went

    async def run(self, statements: list[str]) -> list[AChunk]:  # process all, order matters
        for s in statements:  # sequential: each decision depends on previous chunks
            await self.add(s)  # place it
        return list(self.chunks.values())  # final chunks


STOP = {"are", "under", "classified", "attract", "percent", "duty", "ten", "twenty"}  # filler words for the stub


def _words(t: str) -> set[str]:  # helper tokenizer
    return set(re.findall(r"[a-z0-9]+", t.lower())) - STOP  # content words only


async def stub_decide(statement: str, cands: dict[int, str]) -> str:  # heuristic stand-in for the LLM
    await asyncio.sleep(0)  # async placeholder
    best = max(cands, key=lambda i: len(_words(statement) & _words(cands[i])))  # most shared words
    return str(best) if len(_words(statement) & _words(cands[best])) >= 1 else "NEW"  # threshold: share one content word


async def stub_summarise(statements: list[str]) -> str:  # stand-in summary = first statement
    await asyncio.sleep(0)  # async placeholder
    return statements[0]  # simple title


if __name__ == "__main__":  # demo
    sts = ["Smartphones are classified under 8517.13.", "Lithium batteries are classified under 8507.",
           "Smartphones attract ten percent duty.", "Lithium batteries attract twenty percent duty."]  # data
    for c in asyncio.run(AgenticChunker(stub_decide, stub_summarise).run(sts)):  # run
        print(c.id, c.summary, "|", len(c.statements), "statements")  # show chunks
```

---

## 🟠 FastAPI Integration
Agentic chunking is slow and costs LLM calls, so expose it as an asynchronous job: POST creates a job and returns an id; a worker processes it; GET polls the result. The sketch below keeps jobs in memory.

```python
import uuid  # job ids
from fastapi import BackgroundTasks, FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # pydantic v2

app = FastAPI()  # app
JOBS: dict[str, dict] = {}  # in-memory job store (use Redis/DB in production)


class AgenticIn(BaseModel):  # request
    statements: list[str] = Field(min_length=1, max_length=2000)  # standalone statements


async def _work(job_id: str, statements: list[str]) -> None:  # background worker
    try:  # protect the job state
        chunks = await AgenticChunker(stub_decide, stub_summarise).run(statements)  # chunk
        JOBS[job_id] = {"status": "done", "chunks": [{"summary": c.summary, "n": len(c.statements)} for c in chunks]}
    except Exception as exc:  # record failure
        JOBS[job_id] = {"status": "failed", "error": str(exc)}  # visible to the client


@app.post("/chunk/agentic")  # route
async def start(req: AgenticIn, bg: BackgroundTasks) -> dict:  # create job
    job_id = uuid.uuid4().hex  # new id
    JOBS[job_id] = {"status": "running"}  # initial state
    bg.add_task(_work, job_id, req.statements)  # run after response
    return {"job_id": job_id}  # client polls


@app.get("/chunk/agentic/{job_id}")  # route
async def result(job_id: str) -> dict:  # poll
    if job_id not in JOBS:  # unknown
        raise HTTPException(404, "unknown job")  # not found
    return JOBS[job_id]  # state or result
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph fits agentic chunking naturally: state = {pending statements, chunks}; a node `assign` calls the LLM for the next statement; a conditional edge loops until no statements remain. The LLM call itself is an LCEL chain with structured output (pydantic) so the decision is always valid.

```python
from pydantic import BaseModel  # structured output schema
# from langgraph.graph import StateGraph, END
# from langchain_openai import ChatOpenAI


class Decision(BaseModel):  # what the LLM must return
    chunk_id: int | None  # existing chunk id, or None for a new chunk
    reason: str  # short explanation (useful for debugging)

# llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Decision)  # validated output
# graph = StateGraph(dict)
# graph.add_node("assign", assign_node)          # calls llm.ainvoke(...) and updates chunks
# graph.set_entry_point("assign")
# graph.add_conditional_edges("assign", lambda s: "assign" if s["pending"] else END)  # loop until done
# app_graph = graph.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting free-text LLM output as a chunk id
✅ Correct: Use structured output and validate; fall back to NEW on invalid answers.

```python
# Wrong - crashes or corrupts when the LLM replies "chunk two, I think"
cid = int(llm_reply)  # ValueError

# Right - validate and fall back
cid = int(choice) if choice.isdigit() and int(choice) in chunks else None  # safe
```

❌ Mistake 2: Showing the LLM every existing chunk (token cost explodes as chunks grow).
✅ Correct: Show only titles/summaries of recent or top-N similar chunks (pre-filter with embeddings).

❌ Mistake 3: Using agentic chunking on a huge, already well-structured corpus.
✅ Correct: Use cheap structural splitters first; reserve agentic chunking for messy, high-value text.

---

## 🧠 Tricky Interview Question
**Q**: "Your agentic chunker produced great chunks in the demo, but running it twice on the same document gives different chunks, and your regression tests keep failing. What do you do?"

**Answer**: LLM decisions are non-deterministic. Set temperature to 0 and a fixed seed where supported, use structured outputs, and cache decisions by content hash so the same statement set gives the same chunks. Do not test for exact equality; test properties instead (every statement appears exactly once, no chunk above max size, topical purity measured on a labelled sample, retrieval metrics on an eval set). Version the chunker prompt and re-run evaluations whenever you change the model or prompt.

---

## ⚫ Interview Questions + Answers

Q1: What is agentic chunking?
A1: Using an LLM to decide chunk boundaries and group statements by meaning, often after converting text into standalone propositions.

Q2: What is a proposition?
A2: A short self-contained statement with pronouns resolved, for example "Smartphones attract 10% duty" instead of "They attract 10%".

Q3: What are its main drawbacks?
A3: Cost, latency, non-determinism, and sequential processing (each decision depends on earlier chunks).

Q4: When is it worth it?
A4: Messy, unstructured, high-value text such as transcripts, emails and scraped pages, where rule-based splitters fail and retrieval quality matters.

Q5: (Hard) How do you make it affordable at scale?
A5: Pre-filter candidate chunks with embeddings, use a small model with structured output, batch statements, run documents in parallel (but each document sequentially), cache decisions by hash, cap summary updates (refresh every N additions), and use agentic chunking only for sources that fail a cheap quality check.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Source text is unstructured and topics are interleaved
- Retrieval precision is critical and volume is moderate

❌ Avoid when:
- Documents have clear structure (headings, rows, records)
- Millions of documents with tight budgets
- You need reproducible, deterministic builds

---

## 📊 Visual Diagram
```
 raw text ─► sentences ─► [LLM] propositions (standalone facts)
                                     │
                    for each proposition p:
                                     ▼
                  ┌──────────── [LLM agent] ────────────┐
                  │ "Which chunk fits p?  (or NEW)"     │
                  └───────┬───────────────────┬─────────┘
                    existing chunk          NEW chunk
                    append + refresh        create + title
                          │                    │
                          └────────► chunks grouped by MEANING ─► embed ─► store
```

---

## 💰 Cost Impact
- One decision call per proposition: input = statement + candidate summaries (about 300-800 tokens), output about 10-30 tokens. 10,000 propositions x 600 input tokens = 6M tokens, about $0.90 at $0.15 per 1M (small model), plus summary refresh calls.
- Proposition rewriting adds another pass over all text (input and output tokens).
- Optimise: pre-filter candidates with embeddings (show 3-5 summaries, not 50), refresh summaries only every few additions, small model + structured output, cache by hash, run only on messy sources.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agentic chunking | LLM decides chunk grouping | LLM द्वारा chunk तय करना |
| Proposition | Standalone atomic statement | स्वतंत्र छोटा तथ्य |
| Chunk summary | Title kept for each chunk | हर chunk का सार |
| Structured output | Schema-validated LLM reply | Schema वाला LLM जवाब |
| Non-determinism | Different results per run | हर बार अलग नतीजा |
| Candidate chunks | Chunks the LLM compares | तुलना के लिए chunks |

---

## ⚡ 3-Line Summary
English: Agentic chunking lets an LLM turn text into standalone statements and group them into chunks by meaning. It works well on messy, interleaved text but costs more and is non-deterministic. Pre-filter candidates, validate outputs and use it only where structure-based splitting fails.
Hindi: Agentic chunking में LLM text को standalone statements में बदलकर उन्हें अर्थ के आधार पर chunks में group करता है। Messy, interleaved text पर अच्छा काम करता है पर महँगा और non-deterministic है। Candidates pre-filter करो, outputs validate करो और सिर्फ वहाँ इस्तेमाल करो जहाँ structure-based splitting फेल हो।

---

## ➡️ Next Topic
**175. Chunking Evaluation** - how to prove one chunking strategy is better than another with numbers.
