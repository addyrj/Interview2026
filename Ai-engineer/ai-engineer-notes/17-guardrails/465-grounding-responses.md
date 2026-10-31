---

# 465. Grounding Responses
# हिंदी में: Responses को Grounded बनाना

---

## 🔵 Simple Definition (English)
Grounding means every claim in the LLM's answer is tied to a trusted source: retrieved documents, a database row, or a tool result. The model is told to answer only from that source and to show where each fact came from.

## 🔵 सरल परिभाषा (Hindi)
Grounding का मतलब है कि LLM के जवाब का हर दावा किसी भरोसेमंद source से जुड़ा हो: retrieved documents, database row, या tool result। Model से कहा जाता है कि सिर्फ उसी source से जवाब दे और हर fact कहाँ से आया यह दिखाए।

---

## 🔴 Problem it Solves
Without grounding the model answers from memory, which is old, vague and unverifiable. With grounding, answers are traceable: if a source is wrong you fix the source, not the model.

## 🔴 यह क्यों बना? (Hindi)
Grounding के बिना model अपनी memory से जवाब देता है, जो पुरानी, धुंधली और unverifiable होती है। Grounding से जवाब traceable होते हैं: source गलत हो तो source ठीक करो, model नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Retrieve relevant sources, each with an id: [S1], [S2]...
Step 2 → Put them in the prompt inside clear delimiters
Step 3 → Instruct: "Answer only from sources. Cite ids. If missing, say so."
Step 4 → Model writes answer with inline ids: "Duty is 10% [S2]."
Step 5 → Code checks: every id exists, every claim has an id
Step 6 → Render the answer with links to sources
Step 7 → Log (answer, source ids) for audit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → प्रासंगिक sources लाओ, हर एक का id: [S1], [S2]...
Step 2 → उन्हें साफ delimiters के अंदर prompt में रखो
Step 3 → निर्देश: "सिर्फ sources से जवाब दो। ids cite करो। न मिले तो बताओ।"
Step 4 → Model inline ids के साथ लिखता है: "Duty 10% है [S2]."
Step 5 → Code जाँचता है: हर id मौजूद है, हर claim पर id है
Step 6 → जवाब sources के links के साथ दिखाओ
Step 7 → Audit के लिए (answer, source ids) log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Sources are `[S1] Chapter 61 heading text`, `[S2] Duty schedule row 6109.10`, `[S3] Customs notification dated 2026-03-01`. Answer: "Cotton t-shirts are classified under 6109.10 [S1]. Basic duty is 10% [S2]." A broker clicks `[S2]` and sees the exact row. If a rule changed, only the source document is updated.

**Zomato AI**: "This place serves jain food [menu item #482]" - the claim links to the menu data.

## 🟡 Real Example Hindi mein
**Tariff System**: Sources हैं `[S1] Chapter 61 का heading text`, `[S2] 6109.10 की duty schedule row`, `[S3] 2026-03-01 का customs notification`। जवाब: "Cotton t-shirts 6109.10 में आती हैं [S1]। Basic duty 10% है [S2]।" Broker `[S2]` पर click करके सटीक row देख सकता है। Rule बदले तो सिर्फ source document update होता है।

**Zomato AI**: "यह जगह jain food परोसती है [menu item #482]" - दावा menu data से जुड़ा है।

---

## 💻 Code Example — Basic
```python
# Basic: build a grounded prompt and check citation ids - pure Python
import re  # regex for [S1]

SOURCES: dict[str, str] = {
    "S1": "Cotton t-shirts are classified under HS 6109.10.",
    "S2": "Basic customs duty on HS 6109.10 is 10 percent.",
}


def build_prompt(question: str) -> str:
    blocks = "\n".join(f"[{sid}] {text}" for sid, text in SOURCES.items())  # numbered sources
    return (
        "Answer ONLY using the sources. Cite ids like [S1]. "
        "If the sources do not contain the answer, say 'Not in sources'.\n\n"
        f"Sources:\n{blocks}\n\nQuestion: {question}"
    )


def check_citations(answer: str) -> bool:
    ids = re.findall(r"\[(S\d+)\]", answer)  # cited ids
    return bool(ids) and all(i in SOURCES for i in ids)  # all exist and at least one


print(build_prompt("HS code and duty for cotton t-shirts?"))
print(check_citations("HS 6109.10 [S1], duty 10% [S2]."))  # True
print(check_citations("Duty is 10%."))  # False: no citation
print(check_citations("Duty is 10% [S9]."))  # False: unknown source
```

## 💻 Code Example — Advanced
```python
# Production: grounded generation with sentence-level citation enforcement, async
import asyncio  # async runtime
import os  # env
import re  # parsing
from dataclasses import dataclass  # result type


@dataclass
class Source:
    sid: str  # id like S1
    text: str  # content
    url: str  # link for UI


@dataclass
class Grounded:
    answer: str  # final text
    cited: list[str]  # source ids used
    ungrounded_sentences: list[str]  # sentences with no valid citation


async def generate(prompt: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):  # offline mock output
        return "Cotton t-shirts fall under 6109.10 [S1]. Duty is 10% [S2]. It is popular in Europe."
    from openai import AsyncOpenAI

    client = AsyncOpenAI()
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=250,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.choices[0].message.content or ""


def enforce(answer: str, sources: list[Source]) -> Grounded:
    valid = {s.sid for s in sources}  # allowed ids
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
    ok_sentences: list[str] = []
    bad: list[str] = []
    cited: set[str] = set()
    for sent in sentences:  # check each sentence
        ids = set(re.findall(r"\[(S\d+)\]", sent))
        if ids and ids <= valid:  # has citations and all are valid
            ok_sentences.append(sent)
            cited |= ids
        else:
            bad.append(sent)  # ungrounded sentence
    return Grounded(" ".join(ok_sentences) or "Not in sources", sorted(cited), bad)


async def grounded_answer(question: str, sources: list[Source]) -> Grounded:
    ctx = "\n".join(f"[{s.sid}] {s.text}" for s in sources)
    prompt = f"Use only sources, cite [Sx] per sentence.\n{ctx}\nQ: {question}"
    try:
        raw = await asyncio.wait_for(generate(prompt), timeout=30)  # bounded call
    except Exception:  # timeout or API failure
        return Grounded("Service unavailable", [], [])
    return enforce(raw, sources)  # drop ungrounded sentences


if __name__ == "__main__":
    srcs = [Source("S1", "T-shirts: HS 6109.10", "/doc/1"), Source("S2", "Duty 10%", "/doc/2")]
    print(asyncio.run(grounded_answer("Code and duty?", srcs)))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()


class Ask(BaseModel):
    question: str  # user question


class Resp(BaseModel):
    answer: str  # grounded text
    sources: list[dict[str, str]]  # id + url for UI links


@app.post("/ask", response_model=Resp)
async def ask(body: Ask) -> Resp:
    srcs = [Source("S1", "T-shirts: HS 6109.10", "/doc/1"), Source("S2", "Duty 10%", "/doc/2")]  # retriever
    g = await grounded_answer(body.question, srcs)  # advanced function
    used = [{"id": s.sid, "url": s.url} for s in srcs if s.sid in g.cited]  # only cited sources
    return Resp(answer=g.answer, sources=used)
```

---

## 🔗 LangChain / LangGraph Connection
`create_retrieval_chain` / LCEL RAG chains are grounding by design. Use document metadata (`source`, `page`) to build ids. In LangGraph keep `documents` in state so a later `verify` node can check citations.

```python
from langchain_core.documents import Document  # doc type

docs = [Document(page_content="Duty 10%", metadata={"sid": "S2", "url": "/doc/2"})]
context = "\n".join(f"[{d.metadata['sid']}] {d.page_content}" for d in docs)  # numbered context
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrieved context but no instruction to use only it
✅ Correct: Say it explicitly and give an abstention phrase.

```python
# Wrong
prompt = f"{context}\n{question}"
# Right
prompt = f"Answer ONLY from sources; else 'Not in sources'.\n{context}\n{question}"
```

❌ Mistake 2: Trusting the citation without checking
✅ Correct: Verify the id exists and the claim matches the source.

```python
# Wrong
return answer
# Right
g = enforce(answer, sources)
```

---

## 🧠 Tricky Interview Question
**Q**: "The answer cites [S2] correctly, but the claim is not in S2. What happened?"

**Answer**: This is a "citation hallucination" or misattribution: the id is valid but the content does not support the claim. Existence checks are not enough; you need claim-to-source entailment (NLI or judge) or quote matching. This is why topic 466 exists.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is grounding?
A1: Tying answers to trusted sources so they can be verified.

Q2: [Easy] How is grounding different from fine-tuning?
A2: Grounding gives facts at query time and is easy to update. Fine-tuning changes weights and is poor at fresh facts.

Q3: [Medium] Why numbered source ids?
A3: They make citations short, machine-checkable and linkable in the UI.

Q4: [Medium] What if retrieval returns nothing relevant?
A4: Detect low similarity scores and answer "Not in sources" instead of letting the model fall back to memory.

Q5: [Hard] How do you ground answers needing math, like duty on invoice value?
A5: Use a tool: the LLM extracts value and code, Python computes duty with the DB rate, and the answer cites both the rate source and the tool result. Never let the model do the arithmetic.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Facts, rules or policies drive answers
- Auditability is required

❌ Avoid when:
- Open creative generation
- No trusted source exists (then fix the data first)

---

## 📊 Visual Diagram
```
Question ─► Retriever ─► [S1][S2][S3] ─► Prompt("only sources, cite")
                                              │
                                              ▼
                                         LLM answer: "... [S1]. ... [S2]."
                                              │
                                    check ids + claim support
                                              │
                               UI shows answer + clickable sources
```

---

## 💰 Cost Impact
Sources add input tokens: 3 sources x 250 tokens = 750 tokens, about $0.00011 per call on gpt-4o-mini; answer plus ids adds roughly 20 output tokens. Cheap compared with the cost of wrong answers. Optimise: smaller chunks, rerank to top 3, cache retrieval for repeat questions, and use provider prompt caching for the fixed instruction block.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Grounding | Answer tied to sources | जवाब का source से जुड़ाव |
| Citation | Reference to a source | source का हवाला |
| Source id | Short label like S1 | source का छोटा नाम |
| Attribution | Which source supports which claim | कौन सा claim किस source से |
| Abstain | Say not found | "नहीं मिला" कहना |
| Delimiter | Marker around sources | sources को घेरने वाला चिन्ह |

---

## ⚡ 3-Line Summary
English: Grounding ties each claim to a retrieved source with an id. Instruct the model to use only sources, cite ids, and abstain if missing. Verify citations in code.
Hindi: Grounding हर claim को id के साथ retrieved source से जोड़ती है। Model को निर्देश दो कि सिर्फ sources use करे, ids cite करे और न मिलने पर abstain करे। Citations को code से verify करो।

---

## ➡️ Next Topic
**466. Citation + Source Verification** - checking that cited sources really support the claims.
