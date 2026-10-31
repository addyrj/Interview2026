---

# 252. MessagesPlaceholder
# हिंदी में: MessagesPlaceholder (Messages की list डालने की जगह)

---

## 🔵 Simple Definition (English)
`MessagesPlaceholder("history")` is a slot inside a `ChatPromptTemplate` that is filled with a **list of message objects** at runtime (chat history, agent scratchpad, retrieved examples). Normal variables insert *text*; a placeholder inserts *whole messages* with their roles preserved.

## 🔵 सरल परिभाषा (Hindi)
`MessagesPlaceholder("history")` `ChatPromptTemplate` के अंदर एक slot है जिसमें runtime पर **message objects की list** भरती है (chat history, agent scratchpad, examples)। Normal variable *text* डालता है; placeholder *पूरे messages* role के साथ डालता है।

---

## 🔴 Problem it Solves
A chatbot must remember earlier turns. If you format history into a single string (`"User: hi\nAI: hello"`), the roles become plain text; models handle real role-tagged messages better, tool-call messages break, and you cannot trim or count messages cleanly. You need a way to say "put the previous conversation HERE".

## 🔴 यह क्यों बना? (Hindi)
Chatbot को पिछली बातचीत याद रखनी होती है। History को एक string (`"User: hi\nAI: hello"`) बना देने पर roles सिर्फ़ text बन जाते हैं, tool-call messages टूट जाते हैं और trimming/counting मुश्किल हो जाती है। MessagesPlaceholder कहता है: "पिछली बातचीत यहाँ डालो" — असली message objects के रूप में।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prompt = [("system", rules), MessagesPlaceholder("history"), ("human", "{input}")]
Step 2 → Caller passes {"history": [HumanMessage, AIMessage, ...], "input": "new question"}
Step 3 → Template expands: system + all history messages + new human message
Step 4 → Chat model receives one flat list of messages
Step 5 → Model answers; app appends HumanMessage + AIMessage to its stored history
Step 6 → Before the next call history is trimmed/summarised to control tokens
Step 7 → optional=True means: if "history" is missing, insert nothing instead of raising
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Prompt = [("system", rules), MessagesPlaceholder("history"), ("human", "{input}")]
Step 2 → Caller {"history": [HumanMessage, AIMessage, ...], "input": "नया सवाल"} देता है
Step 3 → Template फैलता है: system + पूरी history + नया human message
Step 4 → Chat model को एक flat list मिलती है
Step 5 → Model जवाब देता है; app उसे history में जोड़ता है
Step 6 → अगली call से पहले history trim/summarise होती है
Step 7 → optional=True हो तो "history" न मिलने पर error नहीं, कुछ नहीं डलता
```

---

## 🟡 Real World Example
**Tariff Classification System**: Officer asks "HS code for power bank?" then "And for the one without battery?". The second question only makes sense with history. The placeholder injects the first Q/A pair so the model knows "the one" means a power bank. In an agent, `MessagesPlaceholder("agent_scratchpad")` carries tool calls and results.

**Zomato AI**: Order-support bot: "Where is my order?" → "Cancel it" — the bot needs the previous turns to know which order.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer पूछता है "Power bank का HS code?" फिर "और बिना battery वाले का?"। दूसरा सवाल history के बिना समझ नहीं आता। Placeholder पहला Q/A inject करता है ताकि model समझे "वाले" का मतलब power bank है। Agent में `MessagesPlaceholder("agent_scratchpad")` tool calls और results ले जाता है।

**Zomato AI**: Order-support bot: "मेरा order कहाँ है?" → "इसे cancel करो" — bot को पिछली बातें चाहिए कि कौन-सा order।

---

## 💻 Code Example — Basic
```python
# Basic: MessagesPlaceholder with chat history (offline, no API key)
from langchain_core.messages import AIMessage, HumanMessage            # message objects
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # prompt pieces

prompt = ChatPromptTemplate.from_messages([                            # build the template
    ("system", "You are a tariff assistant."),                         # rules
    MessagesPlaceholder("history"),                                    # <- previous turns go here
    ("human", "{input}"),                                              # new question
])

history = [                                                            # earlier conversation
    HumanMessage(content="HS code for a power bank?"),
    AIMessage(content="Heading 8507."),
]
msgs = prompt.invoke({"history": history, "input": "And without battery?"}).to_messages()
for m in msgs:                                                         # show final message list
    print(f"{type(m).__name__:14}| {m.content}")                       # role class + content

# optional=True: no history on the first turn is fine
first_turn = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff assistant."),
    MessagesPlaceholder("history", optional=True),                     # may be missing
    ("human", "{input}"),
])
print(len(first_turn.invoke({"input": "Hello"}).to_messages()))       # 2 (system + human)

# Limit how many messages are inserted (keeps the LAST n):
limited = ChatPromptTemplate.from_messages([
    MessagesPlaceholder("history", n_messages=2),                      # only last 2 messages used
    ("human", "{input}"),
])
print(len(limited.invoke({"history": history * 3, "input": "x"}).to_messages()))  # 3 = 2 + 1

# Tuple shortcut with the same effect (optional placeholder):
short = ChatPromptTemplate.from_messages([("placeholder", "{history}"), ("human", "{input}")])
print(len(short.invoke({"history": history, "input": "x"}).to_messages()))  # 3
```

## 💻 Code Example — Advanced
```python
# Production: history store per session + trimming + async chain
# pip install langchain-core
import asyncio                                                         # async
from langchain_core.chat_history import InMemoryChatMessageHistory     # simple history store
from langchain_core.language_models import BaseChatModel               # llm type
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, trim_messages  # messages + trimming
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff assistant. Use the conversation for context."),
    MessagesPlaceholder("history", optional=True),
    ("human", "{input}"),
])

_SESSIONS: dict[str, InMemoryChatMessageHistory] = {}                  # demo store; use Redis/DB in production


def get_history(session_id: str) -> InMemoryChatMessageHistory:
    """Return (or create) the history object for one user session."""
    return _SESSIONS.setdefault(session_id, InMemoryChatMessageHistory())


def trimmed(history: list[BaseMessage], max_messages: int = 8) -> list[BaseMessage]:
    """Keep only recent messages; token_counter=len counts one per message."""
    return trim_messages(
        history,
        max_tokens=max_messages,          # with token_counter=len this means "number of messages"
        token_counter=len,                # cheap counter (use a real tokenizer for exact tokens)
        strategy="last",                  # keep the newest messages
        start_on="human",                 # history must not start with an AI message
        include_system=False,             # system prompt is in the template, not in history
    )


async def chat(llm: BaseChatModel, session_id: str, text: str) -> str:
    """One chat turn with error handling; history is saved only on success."""
    hist = get_history(session_id)                                     # load session history
    chain = PROMPT | llm | StrOutputParser()                           # prompt -> model -> text
    answer = await chain.ainvoke({"history": trimmed(hist.messages), "input": text})  # if this raises, history stays clean
    await hist.aadd_messages([HumanMessage(content=text), AIMessage(content=answer)])  # save both turns only on success
    return answer
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, Header, HTTPException            # FastAPI
from pydantic import BaseModel, Field                                  # schemas
from langchain_core.language_models import BaseChatModel

app = FastAPI()                                                        # app


def get_llm() -> BaseChatModel:
    raise NotImplementedError                                          # shared model instance


class Msg(BaseModel):                                                  # request body
    text: str = Field(min_length=1, max_length=2000)


@app.post("/chat")                                                     # stateful chat endpoint
async def chat_endpoint(
    msg: Msg,
    x_session_id: str = Header(min_length=8, max_length=64),           # client sends a session id header
    llm: BaseChatModel = Depends(get_llm),
) -> dict:
    try:
        answer = await chat(llm, x_session_id, msg.text)               # function from the advanced block
    except Exception as exc:                                           # map provider failures
        raise HTTPException(status_code=503, detail="LLM unavailable") from exc
    return {"answer": answer}
```
Never trust history sent by the client for authorisation; store it server-side keyed by an authenticated session.

---

## 🔗 LangChain / LangGraph Connection
```python
# 1) RunnableWithMessageHistory loads/saves history automatically (topic 257):
chain_with_memory = RunnableWithMessageHistory(
    PROMPT | llm, get_history, input_messages_key="input", history_messages_key="history"
)

# 2) Agents: MessagesPlaceholder("agent_scratchpad") holds tool calls/results.
# 3) LangGraph: MessagesState has a "messages" list with the add_messages reducer;
#    nodes call (ChatPromptTemplate with MessagesPlaceholder("messages") | llm).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a normal variable for history
```python
# Wrong — list is converted to a string like "[HumanMessage(content=...)]":
("human", "History: {history}\n{input}")

# Correct:
MessagesPlaceholder("history"), ("human", "{input}")
```

❌ Mistake 2: Passing strings instead of message objects
```python
# Wrong — placeholder expects messages (or (role, text) tuples), a raw str is one human message:
prompt.invoke({"history": "User: hi\nAI: hello", "input": "x"})

# Correct:
prompt.invoke({"history": [HumanMessage("hi"), AIMessage("hello")], "input": "x"})
```

❌ Mistake 3: Never trimming history
```python
# Wrong — history grows forever: cost and latency increase every turn, eventually context overflow
history.append(...)

# Correct — trim_messages / summarise / n_messages cap (topics 258-259)
```

---

## 🧠 Tricky Interview Question

**Q**: "Your chatbot's cost per message keeps rising during a long conversation, even though each user message is short. Why, and how do you fix it?"

**Answer**: Every turn re-sends the entire history because the LLM is stateless. Turn N costs roughly the sum of all previous turns, so total tokens over a conversation grow quadratically (O(N²)). Fixes: cap history (`n_messages`, `trim_messages` by tokens), summarise old turns (ConversationSummaryMemory pattern), store facts in a vector/DB memory and retrieve only relevant ones, and use provider prompt caching for the stable prefix. Track `usage_metadata.input_tokens` per turn to catch it early.

---

## ⚫ Interview Questions + Answers

Q1: What is MessagesPlaceholder? (Easy)
A1: A prompt slot that is replaced by a list of messages at runtime — used for chat history or agent scratchpad.

Q2: What happens if the key is missing? (Easy)
A2: A `KeyError`-style validation error, unless `optional=True`, in which case nothing is inserted.

Q3: How do you limit history length? (Medium)
A3: `MessagesPlaceholder(..., n_messages=k)` keeps the last k messages; or use `trim_messages` with a token counter before invoking; or summarise older messages.

Q4: Difference between a normal variable and MessagesPlaceholder? (Medium)
A4: A normal variable is formatted into the text of one message. A placeholder splices multiple message objects into the list, preserving types, roles, tool calls and ids.

Q5: Design memory for 1M users with long conversations. (Hard)
A5: Store messages in Redis/Postgres keyed by session id (TTL for old ones). Per turn load only the last N messages plus a rolling summary and top-k relevant facts retrieved from a vector store. Use trimming by tokens, async I/O, per-user rate limits, encryption/PII rules, and a background job to summarise and archive. Measure tokens/turn and p95 latency.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat history must be sent with each request
- Agents need a scratchpad of tool messages
- Few-shot examples are stored as message lists

❌ Avoid when:
- Single-turn tasks (classification, extraction) — there is no history
- History is huge and irrelevant — retrieve selectively instead

---

## 📊 Visual Diagram
```
 ChatPromptTemplate
 ┌───────────────────────────────┐
 │ system: rules                 │
 │ MessagesPlaceholder(history) ─┼──► [Human "HS for power bank?",
 │                               │     AI "8507",
 │                               │     Human "and without battery?",
 │                               │     AI "8504"]
 │ human: {input}                │
 └───────────────────────────────┘
          ▼
 flat list: system, H, A, H, A, H(new)  ──► LLM
```

---

## 💰 Cost Impact
Each turn re-sends all history. If each Q/A pair is 150 tokens: turn 1 sends ~150, turn 10 sends ~1,500, turn 30 sends ~4,500. Total input tokens for a 30-turn chat ≈ 150 × (30×31/2) ≈ 69,750 tokens versus 4,500 without history. On gpt-4o-mini that is about $0.0105 per conversation — fine for one user, large at 1M conversations ($10,500).

Optimise: keep the last 6-10 messages, summarise the rest, retrieve only relevant memories, and enable prompt caching for the stable prefix.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MessagesPlaceholder | Slot for message list | Messages की list का slot |
| History | Previous turns | पिछली बातचीत |
| `optional` | Missing key allowed | न मिले तो चलेगा |
| `n_messages` | Keep last n messages | आख़िरी n messages |
| Scratchpad | Agent tool calls/results | Agent के काम का रफ़ पन्ना |
| `trim_messages` | Cut history by size | History को छोटा करना |

---

## ⚡ 3-Line Summary
English: MessagesPlaceholder splices a list of role-tagged messages into a prompt, the right way to pass chat history and agent scratchpads. Use `optional=True` for first turns and always trim history. History is re-sent every turn, so cost grows quickly.
Hindi: MessagesPlaceholder role वाले messages की list को prompt में जोड़ता है, chat history और agent scratchpad के लिए सही तरीका। पहली turn के लिए `optional=True` और history हमेशा trim करो। History हर turn दोबारा जाती है, इसलिए cost तेज़ी से बढ़ती है।

---

## ➡️ Next Topic
**253. OutputParsers** — turn the model's reply (text) into strings, JSON or typed objects your code can use.
