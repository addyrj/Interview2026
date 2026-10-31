---

# 380. Memory + RAG Together
# हिंदी में: Memory + RAG एक साथ

---

## 🔵 Simple Definition (English)
RAG answers from a shared knowledge base (tariff books, manuals). Memory answers from what we know about this user and this chat. Using both means one prompt with three parts: user memories, retrieved documents, and the question.

## 🔵 सरल परिभाषा (Hindi)
RAG shared knowledge base (tariff books, manuals) से जवाब देता है। Memory इस user और इस chat के बारे में जो पता है उससे जवाब देती है। दोनों साथ इस्तेमाल करने पर एक prompt में तीन हिस्से होते हैं: user memories, retrieved documents और सवाल।

---

## 🔴 Problem it Solves
RAG alone is impersonal ("which port?" - it does not know yours). Memory alone does not know the law or product catalogue and hallucinates. Together: correct public knowledge, personalised to the user.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ RAG impersonal है ("कौन सा port?" - उसे आपका पता नहीं)। सिर्फ़ memory को कानून या catalogue नहीं पता, वो hallucinate करती है। साथ में: सही public knowledge, user के हिसाब से personalised।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Receive question
Step 2 → (Optional) rewrite it using recent chat so "it" becomes a name
Step 3 → Retrieve user memories (vector/entity) in parallel
Step 4 → Retrieve documents from the knowledge base in parallel
Step 5 → Rank / trim both to a token budget
Step 6 → Build prompt: system + memories + documents + question
Step 7 → Generate, then save new facts back to memory
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → सवाल लो
Step 2 → (Optional) recent chat से rewrite करो ताकि "it" नाम बन जाए
Step 3 → User memories साथ-साथ retrieve करो (vector/entity)
Step 4 → Knowledge base से documents साथ-साथ retrieve करो
Step 5 → दोनों को token budget में rank / trim करो
Step 6 → Prompt बनाओ: system + memories + documents + सवाल
Step 7 → Generate करो, फिर नए facts memory में save करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Question "duty on my usual shipment?" Memory: "usual shipment = 48V batteries from Vietnam to Mumbai". RAG: HS 8507.60 chapter notes and BCD rate. Answer combines both. **Amazon-style**: memory knows your size and brand; RAG knows the catalogue and reviews.

## 🟡 Real Example Hindi mein
**Tariff System**: सवाल "मेरी usual shipment पर duty?" Memory: "usual shipment = Vietnam से Mumbai 48V batteries"। RAG: HS 8507.60 chapter notes और BCD rate। जवाब दोनों जोड़ता है। **Amazon-style**: memory को आपका size और brand पता है; RAG को catalogue और reviews।

---

## 💻 Code Example — Basic
```python
# Pure Python: combine memory + document retrieval into one prompt (offline).
MEMORY = {"u1": ["usual shipment: 48V batteries, Vietnam to Mumbai"]}     # user memories
DOCS = [
    "HS 8507.60: lithium-ion accumulators, duty 20 percent",              # tariff doc 1
    "HS 6109.10: cotton t-shirts, duty 25 percent",                       # tariff doc 2
]

def overlap(a: str, b: str) -> int:
    return len(set(a.lower().split()) & set(b.lower().split()))           # shared word count

def top(items: list[str], q: str, k: int = 1) -> list[str]:
    return sorted(items, key=lambda t: overlap(t, q), reverse=True)[:k]   # best k by overlap

def build_prompt(user_id: str, question: str) -> str:
    mems = top(MEMORY.get(user_id, []), question)                         # memory retrieval
    docs = top(DOCS, question + " " + " ".join(mems))                     # use memory to enrich doc search
    return (f"User memory:\n- " + "\n- ".join(mems)                       # memory section
            + "\n\nDocuments:\n- " + "\n- ".join(docs)                    # document section
            + f"\n\nQuestion: {question}")                                # question

print(build_prompt("u1", "duty on my usual shipment batteries?"))          # inspect final prompt
```

## 💻 Code Example — Advanced
```python
# Production: parallel retrieval with asyncio.gather, token budget, error handling.
import asyncio                                             # async + gather
import logging                                             # logs
import tiktoken                                            # token counting
from openai import AsyncOpenAI, OpenAIError                # LLM client

log = logging.getLogger("mem_rag")                         # logger
enc = tiktoken.get_encoding("o200k_base")                  # gpt-4o family encoding

async def get_memories(user_id: str, q: str) -> list[str]:
    await asyncio.sleep(0)                                 # placeholder for mem0/Zep/vector call
    return ["usual shipment: 48V batteries Vietnam to Mumbai"]

async def get_docs(q: str) -> list[str]:
    await asyncio.sleep(0)                                 # placeholder for vector DB call
    return ["HS 8507.60: lithium-ion accumulators, duty 20 percent"]

def fit(items: list[str], budget: int) -> list[str]:
    """Keep items in order until token budget is used."""
    out, used = [], 0                                      # result and counter
    for it in items:
        n = len(enc.encode(it))                            # tokens in this item
        if used + n > budget:                              # would overflow
            break
        out.append(it); used += n                          # accept
    return out

async def answer(user_id: str, q: str) -> str:
    results = await asyncio.gather(                        # run both retrievals together
        get_memories(user_id, q), get_docs(q), return_exceptions=True)
    mems = results[0] if isinstance(results[0], list) else []   # failed memory -> empty
    docs = results[1] if isinstance(results[1], list) else []   # failed docs -> empty
    prompt = ("User memory:\n" + "\n".join(fit(mems, 200))      # 200 tokens for memory
              + "\n\nDocuments:\n" + "\n".join(fit(docs, 1500)) # 1500 tokens for docs
              + f"\n\nQuestion: {q}")
    try:
        client = AsyncOpenAI()                             # needs OPENAI_API_KEY
        r = await client.chat.completions.create(
            model="gpt-4o-mini", max_tokens=300,
            messages=[{"role": "system", "content": "Answer only from memory and documents."},
                      {"role": "user", "content": prompt}])
        return r.choices[0].message.content or ""
    except OpenAIError as exc:
        log.error("llm failed: %s", exc)
        return "Service temporarily unavailable."

if __name__ == "__main__":
    print(asyncio.run(answer("u1", "duty on my usual shipment?")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI                                # framework
from pydantic import BaseModel                             # models

app = FastAPI()                                            # app

class Ask(BaseModel):
    user_id: str                                           # for memory scope
    question: str                                          # user question

@app.post("/ask")
async def ask(body: Ask) -> dict[str, str]:
    return {"answer": await answer(body.user_id, body.question)}   # memory + RAG pipeline
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.runnables import RunnableParallel, RunnableLambda   # parallel LCEL
from langchain_core.prompts import ChatPromptTemplate                  # prompt
from langchain_openai import ChatOpenAI                                # model

prompt = ChatPromptTemplate.from_template(
    "Memory:\n{memory}\n\nDocs:\n{docs}\n\nQuestion: {question}")       # 3-part prompt

chain = (
    RunnableParallel(                                                  # runs branches concurrently
        memory=RunnableLambda(lambda x: "usual shipment: 48V batteries"),   # swap for memory retriever
        docs=RunnableLambda(lambda x: "HS 8507.60 duty 20 percent"),        # swap for doc retriever
        question=lambda x: x["question"],                              # pass question through
    )
    | prompt | ChatOpenAI(model="gpt-4o-mini")
)
# chain.invoke({"question": "duty on my usual shipment?"})
# LangGraph: two retrieval nodes fan out from START, join before the "generate" node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating memory text as trusted facts about the law
✅ Correct: label sections; tell the model documents win for legal facts.

```python
# Wrong
prompt = memories + docs + q
# Right
prompt = "USER PREFERENCES (may be outdated):\n...\nOFFICIAL DOCUMENTS (authoritative):\n...\n" + q
```

❌ Mistake 2: Sequential retrieval (slow)
✅ Correct: `asyncio.gather`.

```python
# Wrong
m = await get_memories(u, q); d = await get_docs(q)
# Right
m, d = await asyncio.gather(get_memories(u, q), get_docs(q))
```

---

## 🧠 Tricky Interview Question
**Q**: "Memory says duty is 10 percent (told by the user last year); the document says 20 percent. Which wins?"

**Answer**: Documents (authoritative, current) win for facts about the world; memory wins for facts about the user. Enforce this in the system prompt, tag sources with dates, and surface the conflict ("You mentioned 10 percent earlier, current tariff is 20 percent"). Never store externally-verifiable facts as user memory without a source.

---

## ⚫ Interview Questions + Answers

Q1: Difference between memory and RAG? (Easy)
A1: Memory is per-user/per-chat and written at runtime; RAG is a shared corpus, usually curated offline.

Q2: Why run them in parallel? (Easy)
A2: They are independent I/O calls; parallel cuts latency to the slower of the two.

Q3: How to split the token budget? (Medium)
A3: Fixed shares, e.g. system 10 percent, memory 10-15 percent, docs 50-60 percent, history/answer rest; trim lowest-ranked items first.

Q4: Can memory improve retrieval? (Medium)
A4: Yes: use memory to rewrite the query ("my usual shipment" -> "48V lithium battery Vietnam"), improving doc recall.

Q5: How do you evaluate the combined system? (Hard)
A5: Evaluate RAG with context precision/recall and faithfulness (Ragas), and memory with recall-of-known-facts tests; add end-to-end tests with conflicting memory and docs. Track latency and tokens per section.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Personalised assistants over a knowledge base
- Returning users

❌ Avoid when:
- Anonymous one-shot Q&A
- Privacy rules forbid storing user data

---

## 📊 Visual Diagram
```
                 ┌─► [User memory] ─┐
 question ─rewrite┤                  ├─► trim to budget ─► PROMPT ─► LLM ─► answer
                 └─► [Doc RAG]  ────┘                                  │
                          ▲                                            ▼
                          └──────────── save new facts ◄───────────────┘
```

---

## 💰 Cost Impact
Prompt = system (150) + memory (100-200) + docs (800-1500) + question (50). Memory is the cheap part. Cost is dominated by retrieved docs, so tune k and chunk size. Optimise: rerank then keep top 3, cap each section, cache frequent doc answers, use gpt-4o-mini.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieve docs then generate | docs निकालकर generate |
| Memory | Per-user stored facts | user के stored facts |
| Query rewrite | Make query self-contained | query को पूरा बनाना |
| Token budget | Max tokens per section | हर हिस्से की token सीमा |
| Authoritative | Trusted source | भरोसेमंद स्रोत |

---

## ⚡ 3-Line Summary
English: RAG brings public knowledge, memory brings user context. Retrieve both in parallel and trim to a budget. Tell the model which source wins on conflicts.
Hindi: RAG public knowledge लाता है, memory user context। दोनों को parallel retrieve करो और budget में trim करो। Conflict में कौन सा source जीतेगा, model को बताओ।

---

## ➡️ Next Topic
**381. Context Window Management** - how to decide what stays in the window as chats and documents grow.
