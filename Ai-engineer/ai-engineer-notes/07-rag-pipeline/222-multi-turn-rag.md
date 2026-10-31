---

# 222. Multi-turn RAG
# हिंदी में: Multi-turn RAG (बातचीत वाला RAG)

---

## 🔵 Simple Definition (English)
Multi-turn RAG is a RAG system that handles a **conversation**, not just one question. Follow-up questions like "and for China?" are first rewritten into a standalone query using chat history, then retrieval and answering happen as usual. The history is also trimmed so it never fills the context window.

## 🔵 सरल परिभाषा (Hindi)
Multi-turn RAG वो RAG है जो पूरी **बातचीत** संभालता है, सिर्फ़ एक सवाल नहीं। "और China के लिए?" जैसे follow-up को पहले chat history की मदद से पूरा (standalone) सवाल बनाया जाता है, फिर retrieval और answer होता है। History को छोटा भी रखा जाता है ताकि context window न भरे।

---

## 🔴 Problem it Solves
- A vector search for "and for China?" finds nothing useful: the words "duty", "laptops" are missing.
- Dumping the full chat into the retriever adds noise and wastes tokens.
- Without history the LLM cannot resolve pronouns ("it", "that code").
- Long chats overflow the context window and cost more every turn.

## 🔴 यह क्यों बना? (Hindi)
- "और China के लिए?" को vector search में डालो तो कुछ काम का नहीं मिलता, क्योंकि "duty", "laptop" शब्द ही नहीं हैं।
- पूरी chat retriever को देने से noise बढ़ता है और tokens बर्बाद होते हैं।
- History के बिना LLM "it", "वो code" जैसे शब्द नहीं समझ पाता।
- लंबी chat से context भर जाता है और हर turn महंगा होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User sends a new message + session_id
Step 2 → Load the last N turns of history for that session
Step 3 → Condense: LLM rewrites (history + message) into ONE standalone question
Step 4 → Retrieve top-k chunks using the standalone question (not the raw message)
Step 5 → Generate: prompt = system + context chunks + trimmed history + original message
Step 6 → Return answer + sources, token usage
Step 7 → Save the user message and answer to history (trim/summarize if too long)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User नया message + session_id भेजता है
Step 2 → उस session की पिछली N turns की history load होती है
Step 3 → Condense: LLM (history + message) को एक standalone सवाल में बदलता है
Step 4 → Standalone सवाल से top-k chunks retrieve होते हैं (raw message से नहीं)
Step 5 → Generate: system + chunks + trimmed history + असली message से जवाब बनता है
Step 6 → Answer + sources + token usage वापस
Step 7 → Message और answer history में save; लंबी हो तो trim/summarize
```

---

## 🟡 Real World Example
**Tariff Classification System**: Turn 1: "What is the import duty on laptops in India?" Turn 2: "And for tablets?" Turn 3: "Which HS code did you use for the first one?" Turn 2 is rewritten to "What is the import duty on tablets in India?" so retrieval hits the right tariff chunk. Turn 3 needs the history itself, because the answer is in the previous reply.
**Zomato AI**: "Show veg options" then "under 300" then "which is fastest?" Each follow-up depends on earlier turns.

## 🟡 Real Example Hindi mein
**Tariff System**: Turn 1: "India में laptop की import duty?" Turn 2: "और tablet?" Turn 3: "पहले वाले के लिए कौन सा HS code लिया?" Turn 2 को "India में tablet की import duty?" बनाया जाता है ताकि सही chunk मिले। Turn 3 में history खुद चाहिए क्योंकि जवाब पिछले reply में है।
**Zomato AI**: "Veg options दिखाओ" फिर "300 के नीचे" फिर "सबसे तेज़ कौन सा?" हर follow-up पिछली turns पर निर्भर है।

---

## 💻 Code Example — Basic
```python
# Pure Python demo of multi-turn RAG: no API key needed (LLM and retriever are mocked)
from typing import Dict, List

# Tiny knowledge base: topic keyword -> tariff fact
KB: Dict[str, str] = {
    "laptops": "Laptops (HS 8471.30) carry 0% basic customs duty in India.",
    "tablets": "Tablets (HS 8471.30) carry 0% basic customs duty in India.",
    "phones": "Mobile phones (HS 8517.13) carry 20% duty in India.",
}

def condense(history: List[Dict[str, str]], question: str) -> str:
    """Mock 'LLM' rewrite: if question has no known topic, borrow it from history."""
    q = question.lower()
    # If the question already names a topic, it is standalone
    if any(topic in q for topic in KB):
        return question
    # Otherwise search history backwards for the last mentioned topic
    for turn in reversed(history):
        for topic in KB:
            if topic in turn["content"].lower():
                return f"{question} (about {topic})"
    return question  # nothing to borrow

def retrieve(query: str) -> List[str]:
    """Mock retriever: keyword match instead of vector search."""
    return [fact for topic, fact in KB.items() if topic in query.lower()]

def answer(question: str, history: List[Dict[str, str]]) -> str:
    standalone = condense(history, question)          # step 3
    chunks = retrieve(standalone)                      # step 4
    reply = chunks[0] if chunks else "I could not find this in the tariff data."
    history.append({"role": "user", "content": question})   # step 7 save
    history.append({"role": "assistant", "content": reply})
    print(f"Q: {question!r}\n   standalone: {standalone!r}\n   A: {reply}")
    return reply

if __name__ == "__main__":
    chat: List[Dict[str, str]] = []                    # one session's history
    answer("Duty on laptops?", chat)
    answer("And for tablets?", chat)                   # explicit topic
    answer("What was the HS code again?", chat)        # borrows the last topic
```

## 💻 Code Example — Advanced
```python
# Production-style multi-turn RAG: async, typed, history trimming, error handling
import asyncio
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI, APIError, RateLimitError  # openai>=1

client = AsyncOpenAI()  # reads OPENAI_API_KEY from the environment
MAX_TURNS = 6           # keep only the last 6 messages in the prompt

CONDENSE_SYSTEM = (
    "Rewrite the user's last message as a standalone question using the chat "
    "history. Return ONLY the question. If it is already standalone, return it unchanged."
)

@dataclass
class Session:
    """Holds one user's conversation."""
    messages: list[dict[str, str]] = field(default_factory=list)

class MultiTurnRAG:
    def __init__(self, retriever: Any) -> None:
        self.retriever = retriever                      # object with async search(q, k)
        self.sessions: dict[str, Session] = {}          # session_id -> Session

    async def _condense(self, history: list[dict[str, str]], question: str) -> str:
        """Step 3: standalone question. Skip the LLM call when there is no history."""
        if not history:
            return question                              # saves tokens on turn 1
        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history[-MAX_TURNS:])
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=80,                               # a question is short
            messages=[
                {"role": "system", "content": CONDENSE_SYSTEM},
                {"role": "user", "content": f"History:\n{transcript}\n\nLast message: {question}"},
            ],
        )
        return (resp.choices[0].message.content or question).strip()

    async def ask(self, session_id: str, question: str) -> dict[str, Any]:
        session = self.sessions.setdefault(session_id, Session())
        try:
            standalone = await self._condense(session.messages, question)
            docs: list[str] = await self.retriever.search(standalone, k=4)
            context = "\n\n".join(docs)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=400,
                messages=[
                    {"role": "system", "content": f"Answer using ONLY this context:\n{context}"},
                    *session.messages[-MAX_TURNS:],       # trimmed history
                    {"role": "user", "content": question},
                ],
            )
        except RateLimitError:
            return {"answer": "Busy, please retry shortly.", "error": "rate_limit"}
        except APIError as exc:                          # any other OpenAI failure
            return {"answer": "Service error.", "error": str(exc)}

        answer = resp.choices[0].message.content or ""
        # Step 7: save both sides of the turn
        session.messages += [{"role": "user", "content": question},
                             {"role": "assistant", "content": answer}]
        usage = resp.usage
        return {"answer": answer, "standalone_query": standalone, "docs": len(docs),
                "tokens": usage.total_tokens if usage else None}

async def demo() -> None:
    class FakeRetriever:                                 # replace with a real vector store
        async def search(self, q: str, k: int = 4) -> list[str]:
            return ["Tablets (HS 8471.30): 0% basic duty."]
    rag = MultiTurnRAG(FakeRetriever())
    print(await rag.ask("s1", "Duty on laptops?"))
    print(await rag.ask("s1", "And tablets?"))

if __name__ == "__main__":
    asyncio.run(demo())   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Keep the session id in the request. Store history in Redis (not process memory) so multiple workers share it.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
rag = MultiTurnRAG(FakeRetrieverInstance)  # from the advanced example; build once at startup

class ChatIn(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)  # validated input
    message: str = Field(min_length=1, max_length=2000)

class ChatOut(BaseModel):
    answer: str
    standalone_query: str | None = None
    tokens: int | None = None

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn) -> ChatOut:
    result = await rag.ask(body.session_id, body.message)  # async: does not block the loop
    if "error" in result:
        raise HTTPException(status_code=503, detail=result["answer"])
    return ChatOut(**{k: result[k] for k in ("answer", "standalone_query", "tokens") if k in result})
```

---

## 🔗 LangChain / LangGraph Connection
LangChain ships this as `create_history_aware_retriever` (the condense step) plus `RunnableWithMessageHistory` (the memory). In LangGraph, put `messages` in the state and add a checkpointer; each node (condense, retrieve, generate) reads the same message list.

```python
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
condense_prompt = ChatPromptTemplate.from_messages([
    ("system", "Rewrite the last question as a standalone question."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
# retriever = vectorstore.as_retriever()   # your existing retriever
history_aware = create_history_aware_retriever(llm, retriever, condense_prompt)
# history_aware.invoke({"input": "And tablets?", "chat_history": [...]}) -> list[Document]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Retrieving with the raw follow-up.
✅ Correct: Condense first, then retrieve.

```python
# Wrong: "And for China?" has no keywords, so retrieval returns junk
docs = await retriever.search(user_message, k=4)
# Right: rewrite with history first
docs = await retriever.search(await rag._condense(history, user_message), k=4)
```

❌ Mistake 2: Sending the entire history every turn (cost grows with every turn, then overflows).
✅ Correct: Keep the last N turns or summarize the old ones.

```python
# Wrong
messages = full_history + [new_msg]
# Right
messages = full_history[-6:] + [new_msg]
```

❌ Mistake 3: Storing sessions in a Python dict with multiple workers (each worker has different memory).
✅ Correct: Use Redis or a database keyed by session_id.

---

## 🧠 Tricky Interview Question
**Q**: "Your multi-turn RAG answers turn 1 well, but after 10 turns answers become vague and wrong. Retrieval logs look fine. What is wrong?"

**Answer**: Likely the history has grown and pushes the retrieved context into the "lost in the middle" zone, or the condense step is drifting (it keeps rewriting with old topics). Fixes: cap history to the last few turns, summarize older ones, put retrieved context close to the question, and log the standalone query for each turn. Also check that topic switches ("now ask about shipping") are not forced into the old topic by the condense prompt.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between single-turn and multi-turn RAG?
A1: Single-turn answers one self-contained question. Multi-turn keeps history, rewrites follow-ups into standalone queries, and manages memory size.

Q2: Why rewrite the question before retrieval?
A2: Embeddings match meaning of the text given. A follow-up like "and for China?" lacks the topic, so the search is poor. A standalone question carries the full meaning.

Q3: Should the condense step use the same model as the answer step?
A3: Usually a cheaper, small model (gpt-4o-mini) with temperature 0 and a tiny max_tokens. The task is simple rewriting, and it runs on every turn, so cost matters.

Q4: How do you stop history from growing without limit?
A4: Sliding window (last N messages), token budget trimming, or summarizing old turns into a short summary message. Always keep the system prompt and the newest message.

Q5: How would you evaluate a multi-turn RAG system?
A5: Build conversation test sets with follow-ups, then measure (a) condense accuracy (does the rewritten query match a human rewrite), (b) retrieval recall on the rewritten query, (c) answer faithfulness, and (d) per-turn degradation: score turn 1 vs turn 8. Log standalone queries in production for debugging.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users chat with the bot (support, tariff assistant, food ordering)
- Follow-ups use pronouns or omit the topic
- Sessions last more than 2-3 turns

❌ Avoid when:
- Each call is an independent search (one-shot API)
- Latency budget is very tight and the extra condense call hurts
- Batch jobs with no conversation

---

## 📊 Visual Diagram
```
 User msg ──┐
            ▼
 ┌──────────────────┐  history   ┌──────────────┐
 │ Condense (LLM)   │◄───────────│ Session store│
 └────────┬─────────┘            └──────▲───────┘
          │ standalone query            │ save turn
          ▼                             │
 ┌──────────────────┐   top-k    ┌──────┴───────┐
 │ Retriever        │───────────►│ Generate(LLM)│──► Answer
 └──────────────────┘   chunks   └──────────────┘
```

---

## 💰 Cost Impact
- Extra condense call per turn: roughly 150-400 input tokens, ~30 output tokens. On gpt-4o-mini that is about $0.00005 per turn.
- History in the answer prompt is the main cost: 6 messages of ~100 tokens add ~600 input tokens every turn.
- Optimise: skip condense on turn 1, use a small model for condense, trim or summarize history, cap `max_tokens`, cache answers for repeated standalone queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multi-turn | Conversation with many exchanges | कई बार की बातचीत |
| Standalone question | Follow-up rewritten to be self-contained | पूरा, अपने आप में समझने वाला सवाल |
| Condense step | LLM rewrite using history | History से सवाल दोबारा लिखना |
| Session | One user's conversation | एक user की चैट |
| Sliding window | Keep only the last N messages | सिर्फ़ आख़िरी N messages रखना |

---

## ⚡ 3-Line Summary
English: Multi-turn RAG rewrites each follow-up into a standalone question using chat history before retrieval. It trims or summarizes history so cost and context stay under control. Store sessions outside process memory for production.
Hindi: Multi-turn RAG हर follow-up को history की मदद से standalone सवाल बनाकर retrieve करता है। History को trim या summarize करके cost और context काबू में रखा जाता है। Production में sessions को process memory के बाहर (Redis) रखो।

---

## ➡️ Next Topic
**223. RAG Memory**: short-term vs long-term memory for RAG bots, and how to store facts across sessions.
