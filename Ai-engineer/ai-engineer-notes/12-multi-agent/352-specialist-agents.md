---

# 352. Specialist Agents
# हिंदी में: Specialist Agents

---

## 🔵 Simple Definition (English)
A specialist agent is built for one narrow domain: customs law, SQL, math, code review, translation. It has a focused prompt, domain tools, domain data (RAG) and often its own tuned model. It does one thing very well instead of everything averagely.

## 🔵 सरल परिभाषा (Hindi)
Specialist agent एक narrow domain के लिए बना होता है: customs law, SQL, math, code review, translation। उसके पास focused prompt, domain tools, domain data (RAG) और अक्सर अपना model होता है। वह सब कुछ average करने की जगह एक काम बहुत अच्छा करता है।

---

## 🔴 Problem it Solves
- Generalist agents mix domains and give shallow or wrong answers.
- Domain knowledge (HS chapter notes, SQL schema) is too large for one prompt.
- Risky actions (running SQL) need a tightly controlled agent.
- Different domains need different models, temperatures and guardrails.

## 🔴 यह क्यों बना? (Hindi)
- Generalist agents domains मिला देते हैं और shallow/गलत जवाब देते हैं।
- Domain knowledge (HS chapter notes, SQL schema) एक prompt के लिए बहुत बड़ा है।
- Risky actions (SQL चलाना) के लिए tightly controlled agent चाहिए।
- अलग domains को अलग models, temperature और guardrails चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a narrow domain and define its boundary (what it will NOT do)
Step 2 → Give it domain knowledge: RAG index, schema, rules
Step 3 → Give it only domain tools (e.g. hs_search, rate_lookup)
Step 4 → Set model + temperature (0 for precise tasks) + output schema
Step 5 → Add refusal: if the question is out of domain, say so / escalate
Step 6 → Evaluate it alone on a domain test set
Step 7 → Register it so a router/supervisor can call it
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Narrow domain चुनो और boundary तय करो (क्या नहीं करेगा)
Step 2 → Domain knowledge दो: RAG index, schema, rules
Step 3 → सिर्फ domain tools दो (जैसे hs_search, rate_lookup)
Step 4 → Model + temperature (precise tasks के लिए 0) + output schema तय करो
Step 5 → Refusal जोड़ो: domain के बाहर हो तो बताओ / escalate करो
Step 6 → Domain test set पर अकेले evaluate करो
Step 7 → Router/supervisor के लिए register करो
```

---

## 🟡 Real World Example
**Tariff Classification System** specialists:
- *Chapter-85 agent* (electronics) with RAG on Chapter 85 notes.
- *Textile agent* (Chapters 50-63) knowing knitted vs woven rules.
- *Duty-rate agent* that only reads the rate table.
A router picks the specialist from the product category; accuracy rises because each prompt contains only the relevant legal notes.

**Amazon**: separate agents for electronics warranty and fashion size help. **Zomato**: a dietary-restriction specialist.

## 🟡 Real Example Hindi mein
**Tariff System** specialists: *Chapter-85 agent* (electronics, उसके chapter notes का RAG), *Textile agent* (Chapters 50-63, knitted बनाम woven rules), *Duty-rate agent* (सिर्फ rate table पढ़ता है)। Router category से specialist चुनता है; हर prompt में सिर्फ relevant legal notes होने से accuracy बढ़ती है।

---

## 💻 Code Example — Basic
```python
# Registry of specialists + keyword router (no API key needed)
from dataclasses import dataclass  # container


@dataclass
class Specialist:
    name: str  # agent name
    keywords: tuple[str, ...]  # words that signal this domain
    notes: str  # domain knowledge snippet (would come from RAG)

    def answer(self, q: str) -> str:  # would call an LLM with notes in the prompt
        return f"[{self.name}] using '{self.notes}' -> answer for: {q}"


SPECIALISTS = [
    Specialist("textile", ("shirt", "cotton", "knitted"), "Ch.61 knitted apparel"),
    Specialist("electronics", ("phone", "laptop", "drone"), "Ch.85 electrical machinery"),
]


def route(q: str) -> Specialist | None:  # pick by keyword
    low = q.lower()  # normalise
    for s in SPECIALISTS:
        if any(k in low for k in s.keywords):  # any keyword matches
            return s
    return None  # nobody fits


q = "cotton knitted shirt"
sp = route(q)
print(sp.answer(q) if sp else "No specialist, escalate to human")
```

## 💻 Code Example — Advanced
```python
# Async specialists with out-of-domain refusal, confidence and fallback generalist
import asyncio  # async runtime
from pydantic import BaseModel, Field  # schema


class Answer(BaseModel):
    agent: str  # who answered
    code: str | None  # HS code or None
    confidence: float = Field(ge=0, le=1)  # certainty
    in_domain: bool  # did the question belong here


async def textile_llm(q: str) -> Answer:  # mocked LLM call
    await asyncio.sleep(0.01)
    if "shirt" not in q:  # out-of-domain refusal
        return Answer(agent="textile", code=None, confidence=0.0, in_domain=False)
    return Answer(agent="textile", code="6109.10", confidence=0.9, in_domain=True)


async def generalist_llm(q: str) -> Answer:  # fallback
    await asyncio.sleep(0.01)
    return Answer(agent="generalist", code="9999.00", confidence=0.4, in_domain=True)


async def classify(q: str, threshold: float = 0.7) -> Answer:
    try:
        spec = await asyncio.wait_for(textile_llm(q), timeout=3)  # bounded time
        if spec.in_domain and spec.confidence >= threshold:
            return spec  # trust the specialist
    except asyncio.TimeoutError:
        pass  # fall through to generalist
    return await generalist_llm(q)  # fallback path


if __name__ == "__main__":
    print(asyncio.run(classify("knitted cotton shirt")))
    print(asyncio.run(classify("lithium battery")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app
REGISTRY = {"textile": "Ch.50-63", "electronics": "Ch.85"}  # available specialists


class Q(BaseModel):
    question: str  # input
    specialist: str | None = None  # optional manual override


@app.post("/ask")
async def ask(q: Q) -> dict:
    name = q.specialist or ("textile" if "shirt" in q.question else None)  # auto-route
    if name is None:
        raise HTTPException(status_code=422, detail="no specialist matches")
    if name not in REGISTRY:
        raise HTTPException(status_code=404, detail="unknown specialist")
    return {"specialist": name, "scope": REGISTRY[name], "answer": "6109.10"}
```

---

## 🔗 LangChain / LangGraph Connection
Specialist = retriever scoped to a domain + prompt. Use `RunnableBranch`-style routing or a LangGraph conditional edge.

```python
from langgraph.graph import StateGraph, START, END  # graph
from typing import TypedDict  # state


class S(TypedDict, total=False):
    q: str  # question
    a: str  # answer


def pick(s: S) -> str:  # conditional edge function returns node name
    return "textile" if "shirt" in s["q"] else "electronics"


def textile(s: S) -> dict:
    return {"a": "textile specialist: 6109.10"}


def electronics(s: S) -> dict:
    return {"a": "electronics specialist: 8517.13"}


g = StateGraph(S)
g.add_node("textile", textile)
g.add_node("electronics", electronics)
g.add_conditional_edges(START, pick, {"textile": "textile", "electronics": "electronics"})
g.add_edge("textile", END)
g.add_edge("electronics", END)
print(g.compile().invoke({"q": "cotton shirt"}))
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Specialist without a boundary.
✅ Correct: Make it refuse out-of-domain input.

```python
# Wrong: always answers, even about phones
# Right
def guard(q: str) -> bool:
    return "shirt" in q  # only answer textile questions
```

❌ Mistake 2: Creating a specialist for every tiny difference.
✅ Correct: Specialise by data/tools, not by wording.

```python
# Wrong: "polite_textile", "short_textile", "formal_textile"
# Right: one textile agent + an output-style parameter
style = "short"
```

---

## 🧠 Tricky Interview Question
**Q**: "Router sends a 'smartwatch with cotton strap' to the textile agent, and the answer is wrong. How do you handle borderline products?"

**Answer**: Specialist routing has hard edge cases. Let the router return top-2 candidates with scores, run both specialists in parallel when the margin is small, then use a validator (or a judge with chapter notes) to pick, or escalate to a human when both are low confidence. Also log such cases and add them to the router's evaluation set and few-shot examples. Specialists must report `in_domain` and confidence so the system can detect misrouting.

---

## ⚫ Interview Questions + Answers

Q1: What is a specialist agent?
A1: An agent focused on one narrow domain with its own prompt, knowledge and tools.

Q2: Why are specialists more accurate?
A2: Shorter, domain-specific context, relevant retrieval only, fewer tools to confuse the model.

Q3: How does the system choose a specialist?
A3: A router (rules, embeddings similarity or an LLM classifier) selects based on the input.

Q4: How do you handle questions outside every specialist's domain?
A4: A generalist fallback, a clarification question, or human escalation, plus logging.

Q5: How do you decide between fine-tuning and RAG for a specialist?
A5: Use RAG first for changing knowledge (rulings, notes updated often). Fine-tune only for stable style/format or latency needs. Measure on the domain test set; combine them if needed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Domains have large separate knowledge bases
- Wrong answers are costly (legal, finance)

❌ Avoid when:
- Domains overlap heavily
- Few queries, so maintenance cost outweighs gain

---

## 📊 Visual Diagram
```
 Query ──► Router ──┬─► Textile specialist  ─► RAG(Ch.50-63)
                    ├─► Electronics special. ─► RAG(Ch.85)
                    ├─► Duty-rate specialist ─► rate table
                    └─► Fallback generalist / human
```

---

## 💰 Cost Impact
Specialists use shorter prompts (only relevant notes), so each call costs fewer input tokens, and cheaper models often suffice. Routing adds one small call (or none if rule/embedding based). Cache embeddings for the router and reuse retrieved chunks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Specialist | Domain-focused agent | domain-विशेष agent |
| Router | Picks specialist | specialist चुनने वाला |
| In-domain | Question belongs to agent | agent के domain में |
| Fallback | Backup path | backup रास्ता |
| Confidence | Certainty score | भरोसे का score |
| Domain RAG | Retrieval limited to domain | domain तक सीमित retrieval |

---

## ⚡ 3-Line Summary
English: Specialist agents are narrow, domain-focused agents with their own knowledge and tools. They are more accurate and cheaper per call. Always add routing, refusal and a fallback.
Hindi: Specialist agents narrow, domain-focused होते हैं जिनके पास अपना knowledge और tools होते हैं। वे ज़्यादा accurate और प्रति call सस्ते हैं। Routing, refusal और fallback हमेशा रखो।

---

## ➡️ Next Topic
**353. Orchestrator Agent** — the agent that plans, delegates to specialists and merges their outputs.
