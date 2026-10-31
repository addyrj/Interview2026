---

# 354. Researcher + Writer Pattern
# हिंदी में: Researcher + Writer Pattern

---

## 🔵 Simple Definition (English)
Two agents with separate jobs: the Researcher collects facts from tools (search, RAG, database) and returns notes with sources. The Writer turns those notes into the final text for the reader. The writer is not allowed to invent facts beyond the notes.

## 🔵 सरल परिभाषा (Hindi)
दो agents, अलग काम: Researcher tools (search, RAG, database) से facts जमा करके sources के साथ notes देता है। Writer उन notes को पाठक के लिए final text बनाता है। Writer को notes से बाहर facts गढ़ने की अनुमति नहीं होती।

---

## 🔴 Problem it Solves
- One agent that researches and writes at the same time mixes tool noise into the prose and may hallucinate.
- Long raw search results flood the writing prompt.
- Grounding is hard to check when facts and wording are mixed.

## 🔴 यह क्यों बना? (Hindi)
- जो agent research और writing साथ करता है वह tool का noise prose में मिला देता है और hallucinate कर सकता है।
- लंबे raw search results writing prompt को भर देते हैं।
- Facts और wording मिले हों तो grounding check करना मुश्किल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User asks a question / report topic
Step 2 → Researcher runs searches and retrieval with tools
Step 3 → Researcher outputs structured notes: [{fact, source_id}]
Step 4 → Notes are validated (non-empty, sources present)
Step 5 → Writer receives ONLY the notes + style guide
Step 6 → Writer drafts text citing source ids
Step 7 → Optional check: every claim maps to a note, then deliver
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User सवाल / report topic देता है
Step 2 → Researcher tools से search और retrieval करता है
Step 3 → Researcher structured notes देता है: [{fact, source_id}]
Step 4 → Notes validate होते हैं (खाली नहीं, sources मौजूद)
Step 5 → Writer को सिर्फ notes + style guide मिलती है
Step 6 → Writer source ids cite करते हुए draft लिखता है
Step 7 → Optional check: हर claim किसी note से जुड़ा हो, फिर deliver
```

---

## 🟡 Real World Example
**Tariff Classification System**: The researcher retrieves the HS chapter notes, past customs rulings and duty rates for "knitted cotton t-shirt". The writer produces a plain-language classification memo for the importer: "Classified under 6109.10 because ... [ruling R-2231]". Because the writer sees only notes, every sentence can be traced.

**Amazon**: researcher gathers product specs, writer drafts the listing. **Zomato**: researcher gets menu data, writer creates the restaurant description.

## 🟡 Real Example Hindi mein
**Tariff System**: Researcher "knitted cotton t-shirt" के लिए HS chapter notes, पुराने customs rulings और duty rates निकालता है। Writer importer के लिए आसान भाषा में memo लिखता है: "6109.10 में classify क्योंकि ... [ruling R-2231]"। Writer सिर्फ notes देखता है इसलिए हर वाक्य trace हो सकता है।

---

## 💻 Code Example — Basic
```python
# Researcher gathers notes, writer composes text only from notes (mock tools, no API)
from dataclasses import dataclass  # container


@dataclass
class Note:
    fact: str  # a fact
    source: str  # where it came from


def researcher(topic: str) -> list[Note]:  # pretend search/RAG
    db = {
        "t-shirt": [Note("Knitted cotton tops fall under heading 6109", "chapter-61"),
                    Note("Ruling R-2231 confirms 6109.10 for cotton", "R-2231")],
    }
    return db.get(topic, [])  # empty list if nothing found


def writer(topic: str, notes: list[Note]) -> str:  # compose from notes only
    if not notes:  # refuse to invent
        return "No verified information found."
    lines = [f"- {n.fact} [{n.source}]" for n in notes]  # cite sources
    return f"Memo on {topic}:\n" + "\n".join(lines)


topic = "t-shirt"
print(writer(topic, researcher(topic)))
```

## 💻 Code Example — Advanced
```python
# Async researcher (parallel sources) + writer with grounding check and error handling
import asyncio  # async runtime
import re  # regex for citations
from pydantic import BaseModel, Field  # validation


class Note(BaseModel):
    fact: str = Field(min_length=3)  # fact text
    source: str  # source id


async def search_rulings(q: str) -> list[Note]:  # source 1 (mock)
    await asyncio.sleep(0.02)
    return [Note(fact="Ruling R-2231 says 6109.10 for cotton tops", source="R-2231")]


async def search_notes(q: str) -> list[Note]:  # source 2 (mock)
    await asyncio.sleep(0.01)
    return [Note(fact="Heading 6109 covers knitted t-shirts", source="ch61")]


async def researcher(q: str) -> list[Note]:
    results = await asyncio.gather(search_rulings(q), search_notes(q), return_exceptions=True)
    notes: list[Note] = []
    for r in results:  # skip failed sources, keep good ones
        if isinstance(r, Exception):
            continue
        notes.extend(r)
    if not notes:
        raise LookupError("researcher found nothing")  # do not let writer guess
    return notes


async def writer_llm(notes: list[Note]) -> str:  # mock LLM output with citations
    await asyncio.sleep(0.01)
    return "Cotton t-shirts are classified as 6109.10 [R-2231][ch61]."


def grounded(text: str, notes: list[Note]) -> bool:  # check every citation exists
    cited = set(re.findall(r"\[([^\]]+)\]", text))
    return bool(cited) and cited <= {n.source for n in notes}


async def pipeline(q: str) -> str:
    notes = await researcher(q)
    draft = await writer_llm(notes)
    if not grounded(draft, notes):  # reject ungrounded text
        raise ValueError("draft cites unknown sources")
    return draft


if __name__ == "__main__":
    print(asyncio.run(pipeline("cotton t-shirt")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Req(BaseModel):
    topic: str  # topic to research


class Memo(BaseModel):
    text: str  # final memo
    sources: list[str]  # cited ids


@app.post("/memo", response_model=Memo)
async def memo(req: Req) -> Memo:
    notes = [("Heading 6109 covers knitted t-shirts", "ch61")]  # mocked researcher result
    if not notes:
        raise HTTPException(status_code=404, detail="no sources found")
    text = " ".join(f"{f} [{s}]" for f, s in notes)  # mocked writer
    return Memo(text=text, sources=[s for _, s in notes])
```

---

## 🔗 LangChain / LangGraph Connection
In LCEL, researcher and writer are two runnables joined with `|`. In LangGraph they are two nodes writing to a shared state.

```python
from typing import TypedDict  # state
from langgraph.graph import StateGraph, START, END  # graph


class S(TypedDict, total=False):
    topic: str  # input
    notes: list[str]  # researcher output
    memo: str  # writer output


def researcher(s: S) -> dict:  # would call retriever/tools
    return {"notes": [f"fact about {s['topic']} [src1]"]}


def writer(s: S) -> dict:  # would call LLM with notes only
    return {"memo": "Memo: " + " ".join(s["notes"])}


g = StateGraph(S)
g.add_node("researcher", researcher)
g.add_node("writer", writer)
g.add_edge(START, "researcher")
g.add_edge("researcher", "writer")
g.add_edge("writer", END)
print(g.compile().invoke({"topic": "t-shirt"}))
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Giving the writer web access.
✅ Correct: Writer gets only the notes.

```python
# Wrong
# writer = Agent(tools=[web_search])  # may add unverified facts
# Right
# writer = Agent(tools=[])  # writes only from provided notes
```

❌ Mistake 2: Writing when research is empty.
✅ Correct: Stop or say "not found".

```python
notes: list[str] = []
# Wrong: draft = write(notes)  # model will invent
# Right
draft = "No verified information found." if not notes else "..."
```

---

## 🧠 Tricky Interview Question
**Q**: "Writer output includes a plausible fact that is not in the notes. How do you prevent it?"

**Answer**: Constrain the prompt ("use only the notes; if missing say unknown"), give the writer no tools, require citations per sentence, add an automatic grounding check (all citations exist; optionally an NLI/LLM-judge confirming each claim is supported), use temperature 0-0.3, and add a critic step (next topics). Log ungrounded drafts as evaluation failures.

---

## ⚫ Interview Questions + Answers

Q1: What does the researcher produce?
A1: Structured notes with sources, not prose.

Q2: Why separate writer from researcher?
A2: Cleaner context, easier grounding checks, independent testing and different model choices.

Q3: How do you make output traceable?
A3: Source ids on every note, citations in the draft, and a check that cited ids exist.

Q4: What if research sources conflict?
A4: Researcher records both with confidence and recency; writer states the conflict or a rule (newest ruling wins); escalate if material.

Q5: How would you scale the pattern for 100 reports per hour?
A5: Async parallel retrieval, caching of retrieved notes per topic, cheap model for research summarisation and better model for writing, queues with concurrency limits, a grounding check as a quality gate, and tracing to find slow sources.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reports, memos, answers that must cite sources
- Raw tool outputs are long

❌ Avoid when:
- Simple Q&A that RAG chain already handles
- Creative writing needing no facts

---

## 📊 Visual Diagram
```
 Topic ─► RESEARCHER ──(tools: search, RAG, DB)
              │
              ▼
        notes [{fact, source}]
              │  (validated, non-empty)
              ▼
          WRITER (no tools) ─► draft with [citations]
              │
              ▼
        grounding check ─► final memo
```

---

## 💰 Cost Impact
Researcher tool outputs can be large; summarise them into short notes so the writer prompt stays small (for example 2,000 raw tokens become 300 note tokens). Use a cheap model for research summarisation, a stronger one for writing. Cache notes per topic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Researcher | Gathers facts | facts जमा करने वाला |
| Writer | Composes text | text लिखने वाला |
| Notes | Structured facts + sources | sources के साथ facts |
| Grounding | Claims backed by sources | claims का source से समर्थन |
| Citation | Reference to source | source का हवाला |
| Hallucination | Invented facts | गढ़े हुए facts |

---

## ⚡ 3-Line Summary
English: The researcher collects sourced notes with tools, and the writer composes only from those notes. This reduces hallucination and makes output traceable. Add an empty-research stop and a grounding check.
Hindi: Researcher tools से sourced notes जमा करता है और writer सिर्फ उन्हीं से लिखता है। इससे hallucination घटता है और output traceable बनता है। Empty-research पर रुकना और grounding check जोड़ो।

---

## ➡️ Next Topic
**355. Planner + Executor Pattern** — plan the steps first, then execute them one by one.
