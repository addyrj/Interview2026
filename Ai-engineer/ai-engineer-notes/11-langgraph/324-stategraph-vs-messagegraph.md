---

# 324. StateGraph vs MessageGraph
# हिंदी में: StateGraph बनाम MessageGraph

---

## 🔵 Simple Definition (English)
`StateGraph` is the main LangGraph class: you define a state schema (a TypedDict or Pydantic model with many fields) and nodes update parts of it. `MessageGraph` was a special graph whose entire state was just a list of messages. `MessageGraph` is deprecated since LangGraph 1.0; use `StateGraph` with `MessagesState` (a state that has a `messages` key) instead.

## 🔵 सरल परिभाषा (Hindi)
`StateGraph` LangGraph की मुख्य class है: आप state schema (कई fields वाला TypedDict या Pydantic model) define करते हैं और nodes उसके हिस्से update करते हैं। `MessageGraph` में पूरी state सिर्फ messages की list होती थी। LangGraph 1.0 से `MessageGraph` deprecated है; इसकी जगह `StateGraph` के साथ `MessagesState` (जिसमें `messages` key होती है) use करो।

---

## 🔴 Problem it Solves
Chatbots need a message history, so `MessageGraph` made that easy. But real apps need more than messages: a tariff app also needs `hs_code`, `confidence`, `attempts`, `user_id`. With `MessageGraph` you had to squeeze these into message text or metadata. `StateGraph` solves this by allowing any typed fields, each with its own reducer (how updates merge), while `MessagesState` gives you the chat history for free.

## 🔴 यह क्यों बना? (Hindi)
Chatbot को message history चाहिए, इसलिए `MessageGraph` आसान था। पर real apps को messages से ज़्यादा चाहिए: tariff app को `hs_code`, `confidence`, `attempts`, `user_id` भी चाहिए। `MessageGraph` में इन्हें message text में ठूँसना पड़ता था। `StateGraph` कोई भी typed field देता है, हर field का अपना reducer (updates कैसे merge हों) होता है, और `MessagesState` chat history मुफ्त देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define state: class State(TypedDict) with fields (+ reducers via Annotated)
Step 2 → StateGraph(State) creates a builder bound to that schema
Step 3 → Nodes receive the whole state, return only the keys they change
Step 4 → For each key LangGraph applies the reducer: overwrite (default) or merge (add_messages, operator.add)
Step 5 → MessagesState = { messages: Annotated[list[AnyMessage], add_messages] } is a ready-made schema
Step 6 → Extend it: class State(MessagesState): hs_code: str
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State define करो: fields वाला class State(TypedDict) (+ Annotated से reducers)
Step 2 → StateGraph(State) उस schema से बँधा builder बनाता है
Step 3 → Nodes पूरी state पाते हैं, सिर्फ बदली हुई keys return करते हैं
Step 4 → हर key पर reducer लगता है: overwrite (default) या merge (add_messages, operator.add)
Step 5 → MessagesState = { messages: Annotated[list[AnyMessage], add_messages] } तैयार schema है
Step 6 → इसे बढ़ाओ: class State(MessagesState): hs_code: str
```

---

## 🟡 Real World Example
**Tariff Classification System**: state = `messages` (chat with the customs officer) + `product` + `hs_code` + `confidence` + `sources` (list of cited tariff rules, merged with `operator.add` so parallel nodes can both append). `MessageGraph` could not hold `confidence` cleanly. **Zomato AI**: state = messages + `order_id` + `refund_amount`; the refund node writes `refund_amount` without touching chat history.

## 🟡 Real Example Hindi mein
**Tariff System**: state = `messages` (customs officer से chat) + `product` + `hs_code` + `confidence` + `sources` (cited tariff rules की list, `operator.add` से merge ताकि parallel nodes दोनों append कर सकें)। `MessageGraph` में `confidence` ठीक से रखना संभव नहीं था। **Zomato AI**: state = messages + `order_id` + `refund_amount`; refund node chat history छुए बिना `refund_amount` लिखता है।

---

## 💻 Code Example — Basic
```python
# StateGraph with MessagesState - runs offline (pip install langgraph)
from langchain_core.messages import AIMessage, HumanMessage  # message classes (installed with langgraph)
from langgraph.graph import END, START, MessagesState, StateGraph  # MessagesState has the messages key


class State(MessagesState):  # inherit the messages key + reducer
    hs_code: str  # extra custom field - impossible in MessageGraph


def tariff_bot(state: State) -> dict:  # a fake "LLM" node
    last = state["messages"][-1].content  # read the latest user message
    reply = AIMessage(content=f"HS code for '{last}' is 8517.13")  # build the answer
    return {"messages": [reply], "hs_code": "8517.13"}  # messages are APPENDED, hs_code is OVERWRITTEN


builder = StateGraph(State)  # builder bound to the schema
builder.add_node("bot", tariff_bot)  # register node
builder.add_edge(START, "bot")  # entry
builder.add_edge("bot", END)  # exit
graph = builder.compile()  # compile

out = graph.invoke({"messages": [HumanMessage(content="smartphone")]})  # run once
print(out["messages"][-1].content)  # the AI reply
print(out["hs_code"])  # custom field: 8517.13
print(len(out["messages"]))  # 2 -> human + ai (add_messages appended)
```

## 💻 Code Example — Advanced
```python
# Custom reducers, Pydantic-free typed state, async node, error handling
import asyncio  # async runner
import operator  # operator.add as list-merge reducer
from typing import Annotated, TypedDict  # Annotated attaches a reducer

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage  # message types
from langgraph.graph import END, START, StateGraph  # graph API
from langgraph.graph.message import add_messages  # reducer that appends / updates by id


class State(TypedDict):  # explicit schema without MessagesState
    messages: Annotated[list[AnyMessage], add_messages]  # chat history, merged by id
    sources: Annotated[list[str], operator.add]  # lists are concatenated, not replaced
    confidence: float  # plain field: last write wins


async def retrieve(state: State) -> dict:  # node 1 adds a source
    return {"sources": ["HS Note 8517(a)"]}  # appended to existing list


async def legal_rules(state: State) -> dict:  # node 2 adds another source
    return {"sources": ["CBIC circular 12/2024"]}  # also appended (no overwrite)


async def answer(state: State) -> dict:  # node 3 composes the answer
    try:
        if not state["sources"]:  # guard: no evidence
            raise ValueError("no sources")  # fail loudly
        text = f"8517.13 (sources: {', '.join(state['sources'])})"  # cite sources
        return {"messages": [AIMessage(content=text)], "confidence": 0.9}  # update two keys
    except ValueError:
        return {"messages": [AIMessage(content="Need human review")], "confidence": 0.0}  # safe fallback


builder = StateGraph(State)  # builder
builder.add_node("retrieve", retrieve)  # node
builder.add_node("legal_rules", legal_rules)  # node
builder.add_node("answer", answer)  # node
builder.add_edge(START, "retrieve")  # fan-out: two parallel branches
builder.add_edge(START, "legal_rules")  # second branch starts at the same time
builder.add_edge(["retrieve", "legal_rules"], "answer")  # join: wait for both
builder.add_edge("answer", END)  # exit
graph = builder.compile()  # compile


async def main() -> None:
    out = await graph.ainvoke({"messages": [HumanMessage(content="phone")], "sources": [], "confidence": 0.0})
    print(out["sources"])  # both sources survive thanks to operator.add
    print(out["messages"][-1].content)  # final answer


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Return the message text plus the custom fields. With `StateGraph` you can return structured data instead of a blob of chat text.

```python
from fastapi import FastAPI  # web
from langchain_core.messages import HumanMessage  # message type
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Ask(BaseModel):  # request
    question: str


class Reply(BaseModel):  # typed response built from state fields
    answer: str
    confidence: float
    sources: list[str]


@app.post("/ask", response_model=Reply)
async def ask(body: Ask) -> Reply:  # route
    out = await graph.ainvoke(  # graph from Advanced example
        {"messages": [HumanMessage(content=body.question)], "sources": [], "confidence": 0.0}
    )
    return Reply(answer=out["messages"][-1].content, confidence=out["confidence"], sources=out["sources"])
```

---

## 🔗 LangChain / LangGraph Connection
`add_messages` is the reducer behind `MessagesState`. It appends new messages and, if a message has an existing `id`, replaces it (useful for editing or removing messages with `RemoveMessage`). Chat models from LangChain (`ChatOpenAI`, `ChatAnthropic`) accept `state["messages"]` directly. Prebuilt agents (`create_react_agent`, and `create_agent` in LangChain 1.x) are built on `StateGraph` with a `messages` key.

```python
from langchain_openai import ChatOpenAI  # pip install langchain-openai
from langgraph.graph import END, START, MessagesState, StateGraph  # graph API

llm = ChatOpenAI(model="gpt-4o-mini")  # chat model


def chat(state: MessagesState) -> dict:  # node
    return {"messages": [llm.invoke(state["messages"])]}  # pass full history, append the reply


g = StateGraph(MessagesState)  # standard replacement for MessageGraph
g.add_node("chat", chat)
g.add_edge(START, "chat")
g.add_edge("chat", END)
app_graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the deprecated `MessageGraph` in new code
✅ Correct: `StateGraph(MessagesState)`.

```python
# Wrong - deprecated since LangGraph 1.0, removal planned in 2.0
from langgraph.graph import MessageGraph
g = MessageGraph()

# Right
from langgraph.graph import MessagesState, StateGraph
g = StateGraph(MessagesState)
```

❌ Mistake 2: Returning the full list and expecting overwrite (or forgetting a reducer)
✅ Correct: Return only new items for reducer-backed keys; add a reducer for list keys that must accumulate.

```python
# Wrong - 'sources' has no reducer, parallel nodes overwrite each other
class State(TypedDict):
    sources: list[str]          # 2 parallel writers -> InvalidUpdateError

# Right
class State(TypedDict):
    sources: Annotated[list[str], operator.add]   # merges writes from both nodes
```

---

## 🧠 Tricky Interview Question

**Q**: "Two parallel nodes both return `{'confidence': 0.8}` and `{'confidence': 0.6}` in the same step. What happens?"

**Answer**: `confidence` has no reducer, so LangGraph cannot decide which write wins and raises `InvalidUpdateError` ("can receive only one value per step"). Fix by giving the key a reducer (for example `max` via a small function, or `operator.add` for lists), or by writing to different keys and combining them in a join node. The default overwrite behaviour is only safe when one node writes the key per step.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference between `StateGraph` and `MessageGraph`? (Easy)
A1: `StateGraph` has a custom multi-field state schema; `MessageGraph` had only a list of messages as state. `MessageGraph` is deprecated.

Q2: What is `MessagesState`? (Easy)
A2: A ready-made state class with one key, `messages`, using the `add_messages` reducer. Subclass it to add your own fields.

Q3: What does a reducer do? (Medium)
A3: It defines how a node's returned value is merged into the existing value of that key. Default is overwrite; `add_messages` appends/updates by id; `operator.add` concatenates lists. Reducers make parallel branches safe.

Q4: TypedDict vs Pydantic state - trade-offs? (Medium)
A4: TypedDict is lightweight and fast, with no runtime validation. Pydantic models validate on input (type coercion, constraints) but add overhead and can behave differently with partial updates. Use TypedDict for internal state; use Pydantic for the API boundary or when strict validation matters.

Q5: How do you control the size of `messages` so cost does not explode in long chats? (Hard)
A5: Trim before the LLM call with `trim_messages` (keep last N tokens), summarise old turns into one message and delete originals with `RemoveMessage`, or keep long-term facts in separate state fields/a store. Input tokens grow with every turn because the full history is resent, so unbounded history makes cost grow quadratically across a conversation.

---

## 🔷 When to Use + When Not to Use
✅ Use `StateGraph` when:
- Always for new code; it covers chat-only and rich-state apps
- You need extra fields (scores, ids, sources) next to messages
- Parallel nodes write to shared lists (use reducers)

❌ Avoid `MessageGraph` when:
- Writing anything new (deprecated)
- You need any non-message data

---

## 📊 Visual Diagram
```
MessageGraph (old)                  StateGraph + MessagesState (now)
state = [msg, msg, msg]             state = {
                                      messages:   [msg, msg]   <- add_messages
node(list) -> list                    hs_code:    "8517.13"    <- overwrite
                                      sources:    [a, b]       <- operator.add
                                      confidence: 0.9          <- overwrite
                                    }
                                    node(state) -> partial dict
```

---

## 💰 Cost Impact
- The schema itself is free, but `messages` is resent to the LLM at every call. A 20-turn tariff chat at ~150 tokens per turn means ~3,000 input tokens on turn 20 (about $0.00045 with `gpt-4o-mini` input pricing of $0.15 / 1M tokens).
- Optimise: store structured facts in separate fields (`hs_code`, `product`) and send only those plus the last few messages; use `trim_messages`; summarise older turns.
- Do not stuff large documents into `messages`; keep them in a separate field and inject only relevant chunks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| StateGraph | Graph with custom state schema | Custom state वाला graph |
| MessageGraph | Old graph with only messages (deprecated) | पुराना, सिर्फ messages वाला graph |
| MessagesState | Prebuilt state with `messages` key | तैयार messages state |
| Reducer | Rule to merge updates into a key | Update merge करने का नियम |
| add_messages | Reducer that appends / updates by id | Messages जोड़ने वाला reducer |
| Partial update | Node returns only changed keys | सिर्फ बदली keys return करना |

---

## ⚡ 3-Line Summary
English: `StateGraph` holds typed multi-field state; `MessageGraph` only held messages and is now deprecated. Use `StateGraph(MessagesState)` and extend it with your own fields. Reducers decide how parallel updates merge.
Hindi: `StateGraph` में कई typed fields की state होती है; `MessageGraph` में सिर्फ messages थे और अब deprecated है। `StateGraph(MessagesState)` use करो और अपने fields जोड़ो। Reducers तय करते हैं कि parallel updates कैसे merge हों।

---

## ➡️ Next Topic
**325. Checkpointer — Memory** — saving state after every step so conversations persist across calls using `thread_id`.
