---

# 221. Conversational RAG
# हिंदी में: Conversational RAG

---

## 🔵 Simple Definition (English)
Conversational RAG lets users ask follow-up questions in a chat ("and for laptops?"). Because a vector search for "and for laptops?" finds nothing useful, the system first rewrites the follow-up into a standalone question using the chat history, then runs normal RAG.

## 🔵 सरल परिभाषा (Hindi)
Conversational RAG users को chat में follow-up सवाल ("और laptops के लिए?") पूछने देता है। "और laptops के लिए?" का vector search कुछ काम का नहीं ढूँढता, इसलिए system पहले chat history से follow-up को standalone सवाल में बदलता है, फिर normal RAG चलाता है।

---

## 🔴 Problem it Solves
Chat users speak in references: "that one", "what about the duty?", "and in India?". Retrieval has no memory, so these queries return random chunks. Passing the whole history to the retriever is noisy. The fix is query condensation (also called query rewriting): history + follow-up becomes one clear question.

## 🔴 यह क्यों बना? (Hindi)
Chat में users references में बोलते हैं: "वो वाला", "duty क्या होगी?", "और India में?"। Retrieval को memory नहीं होती, इसलिए ऐसी queries random chunks लाती हैं। पूरी history retriever को देना noisy है। समाधान है query condensation (query rewriting): history + follow-up मिलकर एक साफ़ सवाल बनते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User sends message + session id
Step 2 → Load chat history for the session (last N turns)
Step 3 → If history is empty: use the message as is
Step 4 → Else: LLM "condenser" rewrites it as a standalone question
Step 5 → Retrieve (and rerank) using the standalone question
Step 6 → Generate answer using context + (short) history + original message
Step 7 → Save user message and answer to the history store
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User message + session id भेजता है
Step 2 → उस session की chat history load करो (आख़िरी N turns)
Step 3 → History खाली हो तो message जैसा है वैसा use करो
Step 4 → वरना LLM "condenser" उसे standalone सवाल में बदलता है
Step 5 → Standalone सवाल से retrieve (और rerank) करो
Step 6 → Context + (छोटी) history + original message से answer बनाओ
Step 7 → User message और answer को history store में save करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Turn 1: "HS code for smartphones?" Turn 2: "And what is the duty on it from China?" The condenser rewrites turn 2 as "What is the import duty on smartphones (HS 8517.13) from China?" Retrieval now hits the right chunks. Turn 3: "Compare with laptops" becomes "Compare import duty from China for smartphones and laptops". **Zomato**: "Is it veg?" after discussing a dish. **Amazon**: "Does it come in blue?" about the product just discussed.

## 🟡 Real Example Hindi mein
**Tariff System**: Turn 1: "Smartphones का HS code?" Turn 2: "और China से इस पर duty क्या है?" Condenser turn 2 को "China से smartphones (HS 8517.13) पर import duty क्या है?" में बदलता है। अब retrieval सही chunks पकड़ता है। Turn 3: "Laptops से compare करो" बनता है "China से smartphones और laptops की import duty compare करो"। **Zomato**: किसी dish की बात के बाद "क्या ये veg है?" **Amazon**: अभी चर्चा वाले product के लिए "क्या ये blue में आता है?"

---

## 💻 Code Example — Basic
```python
# Pure Python: rule-based follow-up condensing + keyword retrieval. Runs offline.
from typing import Dict, List  # type hints

KB: List[str] = [
    "Smartphones HS 8517.13 duty 20 percent from China.",
    "Laptops HS 8471.30 duty 0 percent from China.",
]
HISTORY: Dict[str, List[Dict[str, str]]] = {}  # session_id -> messages


def condense(history: List[Dict[str, str]], follow_up: str) -> str:
    """Naive condenser: if follow-up is short or has pronouns, prepend the last user topic."""
    if not history:  # first turn
        return follow_up  # nothing to resolve
    pronouns = {"it", "that", "this", "those", "and"}  # triggers
    words = set(follow_up.lower().replace("?", "").split())  # words in follow-up
    if len(words) <= 6 or words & pronouns:  # likely depends on history
        last_user = [m["content"] for m in history if m["role"] == "user"][-1]  # previous question
        return f"{last_user} | {follow_up}"  # combined query
    return follow_up  # already standalone


def retrieve(q: str) -> str:
    """Top-1 by word overlap."""
    qw = set(q.lower().replace("?", "").replace("|", " ").split())  # query words
    return max(KB, key=lambda d: len(qw & set(d.lower().split())))  # best doc


def chat(session: str, msg: str) -> str:
    hist = HISTORY.setdefault(session, [])  # get/create history
    standalone = condense(hist, msg)  # rewrite
    answer = f"[{standalone}] -> {retrieve(standalone)}"  # fake generation
    hist += [{"role": "user", "content": msg}, {"role": "assistant", "content": answer}]  # save turn
    return answer  # reply


if __name__ == "__main__":
    print(chat("s1", "Duty on smartphones from China?"))  # turn 1
    print(chat("s1", "And what about laptops?"))  # turn 2 depends on turn 1
```

## 💻 Code Example — Advanced
```python
# Production: LLM condenser (async), bounded history, per-session store, graceful fallback.
import logging  # logs
from collections import defaultdict, deque  # history storage

from openai import AsyncOpenAI  # openai>=1

logger = logging.getLogger("conv_rag")  # logger
client = AsyncOpenAI()  # env key
MAX_TURNS = 6  # keep only recent messages

store: dict[str, deque[dict[str, str]]] = defaultdict(lambda: deque(maxlen=MAX_TURNS * 2))  # session -> history


async def condense_question(history: list[dict[str, str]], follow_up: str) -> str:
    """Rewrite follow-up into a standalone question. Falls back to the raw follow-up."""
    if not history:  # no history -> no rewrite needed
        return follow_up  # skip the LLM call (saves tokens)
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in history)  # compact history
    try:  # LLM call
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=80,  # cheap and short
            messages=[
                {"role": "system", "content": "Rewrite the last user message as ONE standalone question. Keep entities. Output only the question."},
                {"role": "user", "content": f"Chat:\n{transcript}\n\nLast user message: {follow_up}"},
            ],
        )
        rewritten = (resp.choices[0].message.content or "").strip()  # model output
        return rewritten or follow_up  # guard empty output
    except Exception as exc:  # fallback keeps chat working
        logger.warning("condense failed: %s", exc)  # log
        return follow_up  # raw follow-up


async def chat(session_id: str, message: str, retrieve) -> dict:
    """retrieve: async function(question) -> list[str]."""
    hist = list(store[session_id])  # snapshot history
    standalone = await condense_question(hist, message)  # step 1
    chunks = await retrieve(standalone)  # step 2: retrieval with rewritten query
    ctx = "\n".join(f"[S{i}] {c}" for i, c in enumerate(chunks, 1))  # context
    resp = await client.chat.completions.create(  # step 3: answer
        model="gpt-4o-mini", temperature=0, max_tokens=300,
        messages=[{"role": "system", "content": "Answer only from context. Cite [S#]."}, *hist,
                  {"role": "user", "content": f"<context>\n{ctx}\n</context>\nQuestion: {message}"}],
    )
    answer = resp.choices[0].message.content or ""  # answer text
    store[session_id].extend([{"role": "user", "content": message}, {"role": "assistant", "content": answer}])  # save turn
    return {"answer": answer, "standalone_question": standalone}  # return both for debugging
```

---

## 🟠 FastAPI Integration
Keep history keyed by `session_id` in Redis or a DB in real deployments (in-memory dict breaks with multiple workers). Return the rewritten question for debugging.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # models

app = FastAPI()  # app


class ChatReq(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)  # conversation id
    message: str = Field(min_length=1, max_length=1000)  # user text


async def my_retrieve(q: str) -> list[str]:
    return ["Smartphones HS 8517.13 duty 20 percent."]  # replace with vector search


@app.post("/chat")  # route
async def chat_route(req: ChatReq) -> dict:
    return await chat(req.session_id, req.message, my_retrieve)  # conversational RAG
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `create_history_aware_retriever` (condenses question + history, then retrieves) plus `create_retrieval_chain`, and `RunnableWithMessageHistory` for storing history. LangGraph: use `MessagesState` and a checkpointer (`MemorySaver`, Postgres saver) keyed by `thread_id`.

```python
from langchain.chains import create_history_aware_retriever, create_retrieval_chain  # helpers
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # prompts

contextualize_prompt = ChatPromptTemplate.from_messages([  # condense step
    ("system", "Rewrite the user's last message as a standalone question using the chat history."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
# history_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)
# rag_chain = create_retrieval_chain(history_retriever, combine_docs_chain)
# result = await rag_chain.ainvoke({"input": "And for laptops?", "chat_history": messages})
# LangGraph: graph.compile(checkpointer=MemorySaver()); config={"configurable": {"thread_id": session_id}}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the raw follow-up for retrieval
✅ Correct: Condense first.

```python
# Wrong: searching "and for laptops?" returns unrelated chunks
chunks = await retrieve(message)

# Right
chunks = await retrieve(await condense_question(history, message))
```

❌ Mistake 2: Unlimited history
✅ Correct: Keep a window (and summarise older turns).

```python
# Wrong: every turn adds tokens forever
messages = all_messages

# Right
messages = all_messages[-12:]   # or deque(maxlen=12)
```

---

## 🧠 Tricky Interview Question
**Q**: "The condenser sometimes changes the meaning (for example it drops 'China' from the question). Retrieval then returns the wrong tariff. How do you reduce this risk?"

**Answer**: Constrain the condenser: low temperature, "preserve all entities, numbers, and constraints", few-shot examples, and short output. Log raw vs rewritten queries and sample for review. Add a safety net: run retrieval with both original (plus last topic) and rewritten queries and merge, or extract entities into a session state (country=China) and apply them as metadata filters instead of relying on text. Evaluate on a multi-turn test set with labelled standalone questions.

---

## ⚫ Interview Questions + Answers

Q1: Why can't we embed the follow-up directly?
A1: It lacks context ("and for laptops?" has no topic), so the embedding is meaningless for search.

Q2: What is query condensation?
A2: Rewriting a follow-up using chat history into a standalone question.

Q3: Where should chat history be stored?
A3: Redis or a database keyed by session or thread id; in-memory only for single-process demos.

Q4: Do you give the history to the final answer LLM too?
A4: Usually a short window, yes, for tone and references; retrieval uses the condensed question. Limit tokens.

Q5: How to scale conversational RAG to millions of sessions?
A5: Stateless API workers with history in Redis/DB, TTL and truncation, summarisation of older turns, skip condensation on first turns or when no pronouns, a small model for condensation, caching rewritten questions, and per-user rate limits. Use checkpointers in LangGraph with a durable backend.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chatbots with follow-ups
- Users refer to earlier answers
- Sessions have multiple turns

❌ Avoid when:
- Single-shot Q&A APIs
- Each request is already standalone (skip the extra LLM call)

---

## 📊 Visual Diagram
```
 History: U: "Duty on smartphones from China?"  A: "20 percent [S1]"
 New msg: "And what about laptops?"
                 │
                 ▼
        ┌──────────────────┐
        │ Condenser (LLM)  │  ~150 tokens
        └────────┬─────────┘
                 ▼
 "What is the duty on laptops from China?"
                 ▼
        retrieve → rerank → generate ─► answer ─► save to history
```

---

## 💰 Cost Impact
- Extra call per follow-up turn: about history tokens (200-500) + 80 output on a small model. About $0.0001 on gpt-4o-mini.
- History inside the final prompt grows with every turn; unbounded history is the biggest hidden cost.
- Optimise: skip condensing on turn 1, window history to the last 4-6 turns, summarise older turns, cap condenser max_tokens, cache rewrites, use a small model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Follow-up | Question that depends on earlier chat | पिछली बात पर निर्भर सवाल |
| Condensation | Rewrite into standalone question | Standalone सवाल में बदलना |
| Session / thread id | Conversation identifier | बातचीत की पहचान |
| Checkpointer | Saves graph state per thread | Thread का state सेव करने वाला |
| Standalone question | Understood without history | बिना history समझ आने वाला सवाल |

---

## ⚡ 3-Line Summary
English: Conversational RAG rewrites follow-up messages into standalone questions using chat history, then retrieves normally. Store history per session and keep it bounded. Log both raw and rewritten questions to catch errors.
Hindi: Conversational RAG follow-up messages को chat history से standalone सवालों में बदलता है, फिर normal retrieval करता है। History session के हिसाब से रखो और सीमित रखो। गलतियाँ पकड़ने के लिए raw और rewritten दोनों सवाल log करो।

---

## ➡️ Next Topic
**222. Multi-turn RAG** — handling retrieval across many turns: caching context, re-retrieving only when needed, and topic shifts.
