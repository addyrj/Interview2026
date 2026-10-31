---

# 257. Memory in LangChain
# हिंदी में: LangChain में Memory

---

## 🔵 Simple Definition (English)
Memory in LangChain is the mechanism that lets a chain or agent remember earlier messages in a conversation. LLMs are stateless, so memory loads past messages and puts them into the prompt each turn, then saves the new turn. Today the recommended tools are `RunnableWithMessageHistory` and LangGraph checkpointers; old `Conversation*Memory` classes are legacy.

## 🔵 सरल परिभाषा (Hindi)
LangChain में Memory वो तरीका है जिससे chain या agent बातचीत के पिछले messages याद रखता है। LLM stateless है, इसलिए memory हर turn में पुराने messages prompt में डालती है और नया turn save करती है। आज के लिए recommended तरीका `RunnableWithMessageHistory` और LangGraph checkpointer है; पुरानी `Conversation*Memory` classes legacy हैं।

---

## 🔴 Problem it Solves
- Each LLM call is independent: "And for tablets?" means nothing alone.
- Developers manually concatenated history strings (error-prone).
- Different users need separate histories.
- Growing history needs trimming policies.

## 🔴 यह क्यों बना? (Hindi)
- हर LLM call स्वतंत्र है: "और tablets?" अकेले का कोई मतलब नहीं।
- Developers हाथ से history string जोड़ते थे (गलतियाँ होती थीं)।
- अलग-अलग users की अलग history चाहिए।
- बढ़ती history को trim करने की policy चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A session_id identifies the conversation
Step 2 → get_session_history(session_id) returns a chat-history object
Step 3 → Before each call: load stored messages into a MessagesPlaceholder
Step 4 → LLM answers using system + history + new input
Step 5 → After the call: append human message + AI message to the history
Step 6 → Trim or summarize if history grows too big
Step 7 → Swap the storage (in-memory, Redis, SQL) without changing the chain
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → session_id बातचीत की पहचान है
Step 2 → get_session_history(session_id) chat-history object देता है
Step 3 → हर call से पहले: stored messages MessagesPlaceholder में load होते हैं
Step 4 → LLM system + history + नए input से जवाब देता है
Step 5 → Call के बाद: human और AI message history में जुड़ते हैं
Step 6 → History बड़ी हो तो trim या summarize
Step 7 → Storage (in-memory, Redis, SQL) बदलो, chain वही रहे
```

---

## 🟡 Real World Example
**Tariff Classification System**: A broker asks "HS code for a Bluetooth speaker?", then "What duty on it?" The word "it" needs memory. Each broker has a `session_id`, so two brokers chatting at once never see each other's messages.
**Zomato AI**: remembers the cart and cuisine choices during one ordering session.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker पूछता है "Bluetooth speaker का HS code?", फिर "उस पर duty कितनी?" यहाँ "उस" के लिए memory चाहिए। हर broker का `session_id` है, इसलिए एक साथ chat करने वाले दो brokers एक-दूसरे के messages नहीं देखते।
**Zomato AI**: एक order session में cart और cuisine पसंद याद रखता है।

---

## 💻 Code Example — Basic
```python
# Basic: memory concept in plain Python (what LangChain automates)
from typing import Dict, List

# session_id -> list of messages
STORE: Dict[str, List[Dict[str, str]]] = {}

def get_history(session_id: str) -> List[Dict[str, str]]:
    # Create an empty history the first time we see this session
    return STORE.setdefault(session_id, [])

def fake_llm(messages: List[Dict[str, str]]) -> str:
    # Pretend LLM: it can only answer "it" questions if history mentions a product
    last = messages[-1]["content"].lower()
    if "it" in last.split():
        for m in reversed(messages[:-1]):               # look backwards through history
            if "speaker" in m["content"].lower():
                return "Speaker duty is 20%."
    return "Bluetooth speaker: HS 8518.22."

def chat(session_id: str, text: str) -> str:
    history = get_history(session_id)                   # load
    history.append({"role": "user", "content": text})   # add new input
    reply = fake_llm(history)                           # call "model" with full history
    history.append({"role": "assistant", "content": reply})  # save answer
    return reply

if __name__ == "__main__":
    print(chat("broker-1", "HS code for a Bluetooth speaker?"))
    print(chat("broker-1", "What duty on it?"))          # uses memory
    print(chat("broker-2", "What duty on it?"))          # separate session: no memory
```

## 💻 Code Example — Advanced
```python
# Modern LangChain memory: RunnableWithMessageHistory + trimming + async + error handling
import asyncio

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

_stores: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Swap this for RedisChatMessageHistory / SQLChatMessageHistory in production."""
    if session_id not in _stores:
        _stores[session_id] = InMemoryChatMessageHistory()
    return _stores[session_id]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=300)

# Keep the last ~1000 tokens of history so cost stays bounded
trimmer = trim_messages(max_tokens=1000, strategy="last", token_counter=llm,
                        include_system=True, start_on="human")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff classification assistant. Be concise."),
    MessagesPlaceholder("history"),          # past messages are injected here
    ("human", "{input}"),
])

# Trim the history, then run prompt and llm
chain = RunnablePassthrough.assign(history=lambda x: trimmer.invoke(x["history"])) | prompt | llm

with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

async def ask(session_id: str, text: str) -> str:
    try:
        result = await with_memory.ainvoke(
            {"input": text},
            config={"configurable": {"session_id": session_id}},   # which conversation
        )
        return str(result.content)
    except Exception as exc:                                       # network, auth, rate limit
        return f"Sorry, something went wrong: {type(exc).__name__}"

async def demo() -> None:
    print(await ask("broker-1", "HS code for a Bluetooth speaker?"))
    print(await ask("broker-1", "What duty on it?"))

if __name__ == "__main__":
    asyncio.run(demo())   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
The API is stateless; the client sends `session_id` and the server loads history from a shared store.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class ChatIn(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=2000)

@app.post("/chat")
async def chat_route(body: ChatIn) -> dict[str, str]:
    answer = await ask(body.session_id, body.message)   # from the advanced example
    return {"answer": answer}

@app.delete("/chat/{session_id}")
async def clear(session_id: str) -> dict[str, str]:
    get_session_history(session_id).clear()             # let users reset the chat
    return {"status": "cleared"}
```

---

## 🔗 LangChain / LangGraph Connection
In LangGraph, memory is built in: pass a checkpointer when compiling, and use `thread_id` instead of `session_id`. State (including `messages`) is saved after every step. This is the officially recommended replacement for legacy memory classes.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def call_model(state: MessagesState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}   # state holds history

builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_edge(START, "model")
app_graph = builder.compile(checkpointer=MemorySaver())    # memory on

cfg = {"configurable": {"thread_id": "broker-1"}}
app_graph.invoke({"messages": [("user", "HS code for a speaker?")]}, cfg)
app_graph.invoke({"messages": [("user", "Duty on it?")]}, cfg)   # remembers
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: One global history for all users.
✅ Correct: One history per `session_id`.

```python
# Wrong: every user shares this list
history = []
# Right
history = get_session_history(session_id)
```

❌ Mistake 2: Never trimming (cost and context overflow).
✅ Correct: Use `trim_messages` or summarize.

❌ Mistake 3: Using in-memory store with several server workers or after restart (history lost or split).
✅ Correct: Redis or a database.

❌ Mistake 4: Starting new projects with legacy `ConversationBufferMemory`.
✅ Correct: Use `RunnableWithMessageHistory` or LangGraph persistence.

---

## 🧠 Tricky Interview Question
**Q**: "Your chatbot remembers perfectly on your laptop, but in production behind 4 pods users randomly lose context. Why?"

**Answer**: History is stored in each pod's process memory (`InMemoryChatMessageHistory`). The load balancer sends turns to different pods, so a pod may not have earlier messages. Move history to a shared store (Redis/Postgres) keyed by session_id, or use a LangGraph Postgres/Redis checkpointer. Sticky sessions are only a workaround, because pod restarts still lose data.

---

## ⚫ Interview Questions + Answers

Q1: Why do LLM apps need memory?
A1: LLM APIs are stateless. Memory re-sends relevant earlier messages so the model can resolve follow-ups.

Q2: What is `session_id` in `RunnableWithMessageHistory`?
A2: A key passed in `config["configurable"]` that selects which stored history to load and update.

Q3: What are the memory strategies?
A3: Buffer (all messages), window (last N), token-trimmed, summary (LLM summarises old turns), and retrieval/entity memory (store facts, fetch relevant ones).

Q4: Why are old memory classes considered legacy?
A4: They were tied to legacy Chains, hidden state inside the object, and poorly supported multi-user, async, and streaming. Message-history runnables and LangGraph persistence are explicit and storage-agnostic.

Q5: Design memory for a chatbot with 100k daily users and long chats.
A5: Redis (or Postgres) keyed by session_id with TTL; token-based trimming for the prompt; rolling summary stored alongside last messages; async writes; separate long-term fact store for preferences; monitor tokens per turn; encrypt and allow deletion for privacy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UIs with follow-up questions
- Agents that continue tasks over multiple calls
- Users expect continuity

❌ Avoid when:
- Single-shot extraction or classification (stateless is cheaper)
- Batch pipelines
- Privacy rules forbid storing messages

---

## 📊 Visual Diagram
```
 session_id ──► get_session_history ──► [msg1, msg2, msg3]
                                              │ load
                                              ▼
 user input ──► prompt( system + history + input ) ──► LLM ──► answer
                                              ▲                  │
                                              └──── save human + AI messages
```

---

## 💰 Cost Impact
- Every remembered message is re-sent as input tokens on every turn. 20 turns of ~100 tokens means ~2000 extra input tokens per call.
- Cost per turn grows with conversation length; total conversation cost grows roughly quadratically.
- Optimise: `trim_messages` with a token budget, rolling summaries, small model for summaries, prompt caching for the stable system prompt, and starting a new thread for new topics.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memory | Stored earlier messages | पिछले messages की याददाश्त |
| session_id | Conversation identifier | बातचीत की पहचान |
| MessagesPlaceholder | Prompt slot for history | History के लिए prompt में जगह |
| Checkpointer | LangGraph state saver | LangGraph की state save करने वाला |
| thread_id | LangGraph conversation key | LangGraph में बातचीत की key |
| trim_messages | Cut history to a token budget | History को token सीमा में काटना |

---

## ⚡ 3-Line Summary
English: LangChain memory loads past messages into the prompt and saves new ones per session. Use RunnableWithMessageHistory or LangGraph checkpointers, not legacy memory classes. Trim history and use shared storage for production.
Hindi: LangChain memory हर session के पुराने messages prompt में डालती है और नए save करती है। Legacy memory classes की जगह RunnableWithMessageHistory या LangGraph checkpointer इस्तेमाल करो। Production में history trim करो और shared storage रखो।

---

## ➡️ Next Topic
**258. ConversationBufferMemory**: the simplest legacy memory class, still asked about in interviews.
