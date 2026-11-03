
---

# 475. Off-Topic Detection
# हिंदी में: Off-Topic Detection

---

## 🔵 Simple Definition (English)
Off-topic detection checks whether a user's request belongs to the domain your assistant is built for (for example customs tariffs). If not ("write me a poem", "who will win the cricket match"), the system politely refuses or redirects **before** spending tokens on the main LLM.

## 🔵 सरल परिभाषा (Hindi)
Off-topic detection जाँचता है कि user की request उस domain की है या नहीं जिसके लिए assistant बना है (जैसे customs tariffs)। अगर नहीं ("कविता लिखो", "cricket कौन जीतेगा"), तो main LLM पर tokens खर्च करने **से पहले** ही विनम्रता से मना या redirect कर दिया जाता है।

---

## 🔴 Problem it Solves
A public assistant becomes a free general chatbot: users ask homework, code and jokes, costing money and creating brand and legal risk (medical or legal advice from a tariff bot). Off-topic input is also a common path to jailbreaks. We need a cheap gate that keeps the bot in scope.

## 🔴 यह क्यों बना? (Hindi)
Public assistant free general chatbot बन जाता है: लोग homework, code और jokes पूछते हैं, इससे पैसा खर्च होता है और brand व legal risk बनता है (tariff bot से medical या legal advice)। Off-topic input jailbreak का भी आम रास्ता है। हमें एक सस्ता gate चाहिए जो bot को scope में रखे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the domain: description + example in-scope and out-of-scope queries
Step 2 → Embed the domain examples once (centroids or a small vector index)
Step 3 → Embed the incoming query; compute similarity to in-scope examples
Step 4 → Cheap rules: keywords and obvious patterns (greetings, thanks are allowed)
Step 5 → Borderline score → ask a small LLM classifier (in_scope / out_of_scope)
Step 6 → Out of scope → canned refusal with a helpful redirect; in scope → pipeline
Step 7 → Log refusals, review them weekly: maybe the domain should be widened
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Domain define करो: description + in-scope और out-of-scope examples
Step 2 → Domain examples एक बार embed करो
Step 3 → आने वाला query embed करो; in-scope examples से similarity निकालो
Step 4 → सस्ते rules: keywords, greetings/thanks allow
Step 5 → Borderline score हो तो छोटा LLM classifier पूछो
Step 6 → Out of scope: canned refusal + redirect; in scope: pipeline
Step 7 → Refusals log करो और हर हफ़्ते review करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: In scope: "duty on imported LED TVs", "HS code for cotton shirts", "what documents for customs clearance". Out of scope: "write a Python sorting function", "best restaurants in Delhi". The bot answers: "I can help with tariff and customs questions. Please ask about HS codes, duties or documents." **Zomato-style**: a food-ordering bot refuses stock-market advice but handles "where is my order" and "refund for cold food".

## 🟡 Real Example Hindi mein
**Tariff System**: In scope: "imported LED TV पर duty", "cotton shirts का HS code", "customs clearance के documents"। Out of scope: "Python sorting function लिखो", "Delhi के best restaurants"। Bot जवाब देता है: "मैं tariff और customs सवालों में मदद कर सकता हूँ।" **Zomato-style**: food bot stock-market advice मना करता है पर "order कहाँ है" और "ठंडे खाने का refund" संभालता है।

---

## 💻 Code Example — Basic
```python
# Basic: keyword-based topic gate (pure Python, runs offline)
IN_SCOPE = {"hs", "tariff", "duty", "customs", "import", "export", "gst", "hsn", "shipment"}  # domain words
SMALL_TALK = {"hi", "hello", "thanks", "thank", "bye"}     # always allowed

def is_on_topic(query: str) -> bool:
    words = set(query.lower().replace("?", " ").replace(",", " ").split())   # tokenise simply
    if words & SMALL_TALK:                                 # greeting or thanks
        return True
    return bool(words & IN_SCOPE)                          # any domain keyword present

for q in ["What is the duty on imported TVs?", "Write a poem about rain", "hello"]:
    print(q, "->", "ALLOW" if is_on_topic(q) else "REFUSE")   # observe decisions
```

## 💻 Code Example — Advanced
```python
# Production: embedding similarity gate + LLM fallback for borderline cases (async)
import math                                                # cosine math
from typing import Literal                                 # literal types
from openai import AsyncOpenAI                             # OpenAI client

client = AsyncOpenAI()                                     # shared client

IN_EXAMPLES = ["HS code for smartphones", "import duty on cotton shirts", "customs documents for export"]
OUT_EXAMPLES = ["write a poem", "python code for sorting", "who won the match"]

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))                 # dot product
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))   # norms
    return dot / (na * nb) if na and nb else 0.0           # safe divide

async def embed(texts: list[str]) -> list[list[float]]:
    r = await client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in r.data]                   # list of vectors

class TopicGate:
    def __init__(self) -> None:
        self.in_vecs: list[list[float]] = []               # filled by setup()
        self.out_vecs: list[list[float]] = []

    async def setup(self) -> None:
        self.in_vecs = await embed(IN_EXAMPLES)            # embed once at startup
        self.out_vecs = await embed(OUT_EXAMPLES)

    async def classify(self, query: str) -> Literal["in", "out", "unsure"]:
        try:
            (q,) = await embed([query])                    # embed the query
            s_in = max(cosine(q, v) for v in self.in_vecs)     # best in-scope similarity
            s_out = max(cosine(q, v) for v in self.out_vecs)   # best out-of-scope similarity
            if s_in - s_out > 0.08:
                return "in"                                # clearly in scope
            if s_out - s_in > 0.08:
                return "out"                               # clearly out of scope
            return "unsure"                                # borderline: use the LLM
        except Exception:
            return "in"                                    # fail open: never block users due to outage

    async def llm_decide(self, query: str) -> bool:
        r = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=3,   # 1 word answer
            messages=[{"role": "system", "content": "Answer YES if the question is about customs tariffs, HS codes, duties or import/export; else NO."},
                      {"role": "user", "content": query[:1000]}],
        )
        return (r.choices[0].message.content or "").strip().upper().startswith("Y")
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager                 # lifespan
from fastapi import FastAPI, Request                       # FastAPI
from pydantic import BaseModel                             # schema

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.gate = TopicGate()                           # create gate
    await app.state.gate.setup()                           # embed examples once
    yield

app = FastAPI(lifespan=lifespan)

class Q(BaseModel):
    question: str

REFUSAL = "I can help with tariff and customs questions (HS codes, duties, documents). Please ask about those."

@app.post("/ask")
async def ask(body: Q, request: Request) -> dict:
    gate: TopicGate = request.app.state.gate               # shared gate
    verdict = await gate.classify(body.question)           # cheap classification
    if verdict == "unsure":
        verdict = "in" if await gate.llm_decide(body.question) else "out"   # LLM fallback
    if verdict == "out":
        return {"answer": REFUSAL, "refused": True}        # no main LLM tokens spent
    return {"answer": "8517.13 ...", "refused": False}     # continue to RAG/LLM pipeline
```

---

## 🔗 LangChain / LangGraph Connection
Use a **router node** at the start of a LangGraph: conditional edge sends off-topic queries to a refusal node and on-topic ones to retrieval.

```python
from langgraph.graph import StateGraph, END                # graph builder
from typing import TypedDict                               # state

class S(TypedDict, total=False):
    question: str; topic: str; answer: str

async def route(state: S) -> S:
    v = await gate.classify(state["question"])             # classify
    return {"topic": v}

async def refuse(state: S) -> S:
    return {"answer": REFUSAL}                             # canned reply

g = StateGraph(S)
g.add_node("route", route); g.add_node("refuse", refuse)
g.set_entry_point("route")
g.add_conditional_edges("route", lambda s: "refuse" if s["topic"] == "out" else END)
g.add_edge("refuse", END)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking greetings and thanks
```python
# Wrong — "thanks!" gets refused, users get annoyed
# Correct — allow small talk and follow-ups ("what about for Germany?") using conversation context
```

❌ Mistake 2: Judging only the last message
```python
# Wrong:
classify("and for 2024?")        # looks off-topic alone

# Correct — include the previous turn or a summary:
classify(history[-1] + " " + "and for 2024?")
```

❌ Mistake 3: Failing closed on errors
```python
# Wrong — embedding outage blocks every user
# Correct — fail open (allow) or fall back to keyword rules, and alert
```

---

## 🧠 Tricky Interview Question
**Q**: "A user asks: 'I am importing insulin pens. Should I take medicine X with it?' Is it on topic?"

**Answer**: It is **mixed**: the import/duty part is in scope, the medical advice part is not (and risky). A binary gate fails here. Best design: split intents. Answer the tariff part, and decline the medical part with a safe message ("I cannot give medical advice"). That needs an intent classifier that can return multiple labels, or an LLM that is prompted with explicit scope rules and a refusal policy, plus output guardrails to catch out-of-scope content that slipped through.

---

## ⚫ Interview Questions + Answers

Q1: Why check topic before calling the main LLM?
A1: It saves tokens and money, reduces abuse and reduces the attack surface.

Q2: What are cheap ways to detect off-topic queries?
A2: Keyword rules and embedding similarity to domain examples.

Q3: What do you do with borderline scores?
A3: Send to a small LLM classifier with a tiny output, or ask the user a clarifying question.

Q4: How do you avoid refusing valid follow-up questions?
A4: Use conversation context when classifying and allow small talk.

Q5: (Hard) How would you measure and tune the gate?
A5: Label real queries as in/out; measure false refusals (hurts users) and false accepts (costs money/risk) separately; set thresholds from a cost-weighted trade-off; review refused queries weekly to widen scope; A/B test refusal messages.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public-facing, narrow-domain assistants
- Cost control and brand safety matter

❌ Avoid when:
- General-purpose assistants where any topic is allowed
- Internal expert tools where users know the scope and over-refusal is costly

---

## 📊 Visual Diagram
```
 query ─► small talk? ─yes─► allow
            │ no
            ▼
   embedding similarity to domain examples
      in ◄────── margin ──────► out
      │            │             │
      │         unsure           │
      │            ▼             ▼
      │       small LLM      refuse + redirect
      ▼
   main RAG / LLM pipeline
```

---

## 💰 Cost Impact
- Embedding a short query: roughly 10-30 tokens (very cheap). LLM fallback: about 60 input + 1-3 output tokens on a small model, only for borderline cases.
- Each correctly refused request saves a full main-LLM call (for example 1,500 input + 250 output tokens). If 8% of traffic is off-topic, this alone can cut the bill by a similar share (illustrative).
- Optimise: cache embeddings of frequent queries and run the gate before retrieval.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Off-topic | Outside the assistant's domain | domain से बाहर |
| Scope | Allowed subject area | अनुमत विषय क्षेत्र |
| Router | Sends input to the right path | सही रास्ते पर भेजने वाला |
| Fail open | Allow when the checker fails | checker fail हो तो allow |
| Margin | Score gap between classes | classes के score का अंतर |
| Refusal | Polite no-answer message | विनम्र मना करने का संदेश |

---

## ⚡ 3-Line Summary
English: Off-topic detection keeps the assistant inside its domain using keywords, embedding similarity and a small LLM fallback. It runs before the main LLM and saves tokens. Use conversation context and fail open to avoid annoying users.
Hindi: Off-topic detection keywords, embedding similarity और छोटे LLM fallback से assistant को domain में रखता है। यह main LLM से पहले चलता है और tokens बचाता है। Conversation context इस्तेमाल करो और error पर fail open रखो।

---

## ➡️ Next Topic
**476. Confidence Scoring** — how sure is the model about its answer, and when should we trust it.
