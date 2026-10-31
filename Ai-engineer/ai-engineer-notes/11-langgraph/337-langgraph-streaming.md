---

# 337. LangGraph Streaming
# हिंदी में: LangGraph Streaming (धीरे-धीरे output भेजना)

---

## 🔵 Simple Definition (English)
Streaming means getting results while the graph is still running instead of waiting for the final answer. LangGraph can stream several things, chosen with `stream_mode`: the full state after each step (`values`), only what each node changed (`updates`), LLM tokens as they are produced (`messages`), your own progress events (`custom`), and debug traces (`debug`). You can combine modes in a list.

## 🔵 सरल परिभाषा (Hindi)
Streaming का मतलब है graph के चलते-चलते results पाना, final answer का इंतज़ार किए बिना। LangGraph `stream_mode` से कई चीज़ें stream कर सकता है: हर step के बाद पूरी state (`values`), हर node ने सिर्फ़ क्या बदला (`updates`), LLM tokens बनते ही (`messages`), आपके अपने progress events (`custom`), और debug traces (`debug`)। कई modes को list में मिला सकते हैं।

---

## 🔴 Problem it Solves
A multi-step agent can take 10-30 seconds. With `invoke`, the user stares at a blank screen and may think the app is broken. Waiting also wastes the chance to show partial progress ("classifying... checking legal rules..."). Streaming improves perceived latency: the first token appears in under a second even if the full job takes 20 seconds.

## 🔴 यह क्यों बना? (Hindi)
Multi-step agent को 10-30 seconds लग सकते हैं। `invoke` में user खाली screen देखता रहता है और सोचता है app खराब है। इंतज़ार में partial progress दिखाने का मौका भी चला जाता है ("classify हो रहा है... legal rules check हो रहे हैं...")। Streaming से perceived latency घटती है: पूरा काम 20 seconds का हो तब भी पहला token 1 second से कम में दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Call graph.stream(...) / graph.astream(...) instead of invoke
Step 2 → Choose stream_mode: "values" | "updates" | "messages" | "custom" | "debug" (or a list)
Step 3 → LangGraph yields chunks as nodes finish (updates/values) or as tokens arrive (messages)
Step 4 → Inside a node, get_stream_writer() lets you emit custom progress dicts
Step 5 → With a list of modes each chunk is a tuple (mode, data)
Step 6 → Your server forwards chunks to the client (SSE or WebSocket)
Step 7 → The last "values" chunk equals what invoke would have returned
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → invoke की जगह graph.stream(...) / graph.astream(...) call करो
Step 2 → stream_mode चुनो: "values" | "updates" | "messages" | "custom" | "debug" (या list)
Step 3 → Nodes खत्म होने पर (updates/values) या tokens आने पर (messages) chunks मिलते हैं
Step 4 → Node के अंदर get_stream_writer() से custom progress dict भेज सकते हो
Step 5 → Modes की list देने पर हर chunk एक tuple (mode, data) होता है
Step 6 → आपका server chunks को client तक भेजता है (SSE या WebSocket)
Step 7 → आखिरी "values" chunk वही है जो invoke return करता
```

---

## 🟡 Real World Example
**Tariff Classification System**: the officer types a product. The UI shows live progress: "Step 1: classifying" (custom event), "Step 2: legal check done" (updates), then the explanation appearing word by word (messages). **Zomato AI**: the support bot streams the reply tokens like a chat typing effect, while a separate event updates "Looking up your order..."

## 🟡 Real Example Hindi mein
**Tariff System**: Officer product लिखता है। UI में live progress दिखता है: "Step 1: classify हो रहा है" (custom event), "Step 2: legal check पूरा" (updates), फिर explanation शब्द-दर-शब्द आता है (messages)। **Zomato AI**: Support bot reply tokens को chat typing की तरह stream करता है, और अलग event "आपका order देख रहे हैं..." दिखाता है।

---

## 💻 Code Example — Basic
```python
# Streaming modes demo - runs offline using a fake chat model (pip install langgraph)
import itertools  # to repeat the canned answer forever

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel  # offline LLM stand-in
from langchain_core.messages import AIMessage  # message type
from langgraph.graph import END, START, MessagesState, StateGraph  # graph API

llm = GenericFakeChatModel(messages=itertools.cycle([AIMessage(content="HS code is 8517.13 for phones")]))  # repeats this answer, streams tokens


def bot(state: MessagesState) -> dict:  # node that calls the LLM
    return {"messages": [llm.invoke(state["messages"])]}  # LLM call (streams tokens internally)


builder = StateGraph(MessagesState)  # builder
builder.add_node("bot", bot)  # node
builder.add_edge(START, "bot")  # entry
builder.add_edge("bot", END)  # exit
graph = builder.compile()  # compile
inp = {"messages": [("user", "HS code for phone?")]}  # input

print("--- updates: what each node changed ---")
for chunk in graph.stream(inp, stream_mode="updates"):  # one chunk per node
    print(chunk)  # {'bot': {'messages': [AIMessage(...)]}}

print("--- messages: token by token ---")
for token, meta in graph.stream(inp, stream_mode="messages"):  # (message_chunk, metadata) pairs
    print(repr(token.content), meta["langgraph_node"])  # each piece of text + which node produced it
```

## 💻 Code Example — Advanced
```python
# Custom progress events + multiple modes + async + error handling
import asyncio  # async
from typing import TypedDict  # typing

from langgraph.config import get_stream_writer  # emit custom events from inside nodes
from langgraph.graph import END, START, StateGraph  # graph API


class State(TypedDict):  # state
    product: str
    hs_code: str
    legal: str


async def classify(state: State) -> dict[str, str]:  # node 1
    write = get_stream_writer()  # writer bound to current run
    write({"progress": "classifying", "pct": 10})  # custom event
    await asyncio.sleep(0.01)  # LLM call placeholder
    write({"progress": "classified", "pct": 50})  # another event
    return {"hs_code": "8517.13"}


async def legal_check(state: State) -> dict[str, str]:  # node 2
    write = get_stream_writer()
    write({"progress": "legal check", "pct": 75})
    await asyncio.sleep(0.01)
    return {"legal": "allowed"}


builder = StateGraph(State)  # builder
builder.add_node("classify", classify)  # node
builder.add_node("legal_check", legal_check)  # node
builder.add_edge(START, "classify")  # entry
builder.add_edge("classify", "legal_check")  # next
builder.add_edge("legal_check", END)  # end
graph = builder.compile()  # compile


async def run(product: str) -> None:
    try:
        async for mode, data in graph.astream(  # list of modes -> tuples
            {"product": product, "hs_code": "", "legal": ""},
            stream_mode=["custom", "updates"],  # progress events + node results
        ):
            print(mode, "->", data)  # forward to the client in real apps
    except asyncio.CancelledError:  # client disconnected: stop work quietly
        print("client left, stream cancelled")
        raise


if __name__ == "__main__":
    asyncio.run(run("smart phone"))
```

---

## 🟠 FastAPI Integration
Use Server-Sent Events (SSE). Always send a final "done" event and handle client disconnects so the graph does not keep spending tokens for nobody.

```python
import json  # serialise chunks

from fastapi import FastAPI, Request  # web + disconnect check
from fastapi.responses import StreamingResponse  # streaming body
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Q(BaseModel):  # request
    product: str


def sse(event: str, data: object) -> str:  # format one SSE frame
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@app.post("/classify/stream")
async def classify_stream(q: Q, request: Request) -> StreamingResponse:  # route
    async def gen():  # async generator for the body
        try:
            async for mode, data in graph.astream(  # graph from Advanced example
                {"product": q.product, "hs_code": "", "legal": ""}, stream_mode=["custom", "updates"]
            ):
                if await request.is_disconnected():  # client closed the tab
                    break  # stop streaming (and stop paying)
                yield sse(mode, data)  # send chunk
            yield sse("done", {"ok": True})  # final marker
        except Exception as exc:  # report errors inside the stream
            yield sse("error", {"detail": str(exc)})
    return StreamingResponse(gen(), media_type="text/event-stream")  # SSE response
```

---

## 🔗 LangChain / LangGraph Connection
`stream_mode="messages"` works with any LangChain chat model called inside a node (`ChatOpenAI(streaming=True)` is not required; LangGraph uses the model's streaming callbacks). Use `metadata["langgraph_node"]` to filter tokens from the node that talks to the user and ignore tokens from internal routing nodes. `astream_events(version="v2")` is the lower-level LangChain API that emits fine-grained events (`on_chat_model_stream`, `on_tool_start`, ...) when you need tool-level detail.

```python
from langchain_openai import ChatOpenAI  # model

llm = ChatOpenAI(model="gpt-4o-mini")  # real model


async def stream_answer(graph, text: str):  # only user-facing tokens
    async for token, meta in graph.astream({"messages": [("user", text)]}, stream_mode="messages"):
        if meta["langgraph_node"] == "writer" and token.content:  # skip router/classifier tokens
            yield token.content  # forward the token
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Streaming a graph that has only synchronous nodes through the async API (or the reverse)
✅ Correct: Match the API to the node type, or provide both.

```python
# Wrong - async-only node used with sync .stream() -> TypeError "No synchronous function provided"
async def classify(state): ...
for chunk in graph.stream(inp): ...

# Right
async for chunk in graph.astream(inp): ...
```

❌ Mistake 2: Forwarding every token including internal nodes (router, classifier JSON)
✅ Correct: Filter by `langgraph_node` or tags.

```python
# Wrong - user sees raw router JSON: {"next": "legal"}
for token, meta in graph.stream(inp, stream_mode="messages"):
    send(token.content)

# Right
for token, meta in graph.stream(inp, stream_mode="messages"):
    if meta["langgraph_node"] == "writer":
        send(token.content)
```

---

## 🧠 Tricky Interview Question

**Q**: "Streaming works locally but behind Nginx/a cloud load balancer the client receives everything at the end in one burst. Why?"

**Answer**: Proxies buffer responses by default. The graph streams correctly, but the proxy holds chunks until the buffer fills or the response ends. Fix: disable proxy buffering for the route (`X-Accel-Buffering: no` header for Nginx, `proxy_buffering off`), use `text/event-stream`, send periodic heartbeat comments, avoid gzip on the stream, and confirm that the platform supports streaming (some serverless gateways need a special streaming mode). The bug is in the transport layer, not LangGraph.

---

## ⚫ Interview Questions + Answers

Q1: Which stream modes exist? (Easy)
A1: `values` (full state each step), `updates` (node deltas), `messages` (LLM tokens), `custom` (your events), `debug` (detailed traces). A list can combine them.

Q2: Difference between `values` and `updates`? (Easy)
A2: `values` sends the entire state after each step; `updates` sends only what each node changed, keyed by node name. `updates` is lighter on the network.

Q3: How do you emit progress events from inside a node? (Medium)
A3: `writer = get_stream_writer(); writer({"progress": "..."})` and consume them with `stream_mode="custom"`.

Q4: How do you stream only the final answer tokens to the user? (Medium)
A4: Use `stream_mode="messages"` and filter on `metadata["langgraph_node"]` (or tags) so only the answering node's tokens are forwarded.

Q5: What happens if the client disconnects mid-stream, and how do you handle it? (Hard)
A5: The graph may keep running and keep spending tokens unless you stop it. In FastAPI check `request.is_disconnected()` or catch `CancelledError`, break out of the `async for`, and use timeouts. For long jobs, run the graph in a background task with a job id and let the client re-attach to a stored stream (or poll), so a disconnect does not cancel paid work that you still want.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat UIs and any step that takes more than ~2 seconds
- You want live progress for multi-step agents
- You need to show partial results or tool activity

❌ Avoid when:
- Machine-to-machine batch jobs that only need the final result (`invoke` is simpler)
- The consumer cannot handle SSE/WebSocket
- Strict output validation must pass before anything is shown (stream after validation instead)

---

## 📊 Visual Diagram
```
 graph.astream(input, stream_mode=["custom","updates","messages"])

 time ─────────────────────────────────────────────────────────►
 custom : {"progress":"classifying"} . . {"progress":"legal check"}
 updates:        {classify:{...}} . . . . . {legal_check:{...}}
 messages:                                   "HS"" code"" is"...
                │                │                 │
                ▼                ▼                 ▼
          FastAPI SSE ──► browser shows progress bar + typing effect
```

---

## 💰 Cost Impact
- Streaming does not change the token price: same input and output tokens as `invoke`. It improves perceived speed, not cost.
- Hidden savings: stopping the stream when the user leaves can prevent unused output tokens (output costs about 4x input on `gpt-4o-mini`: $0.60 vs $0.15 per 1M).
- Hidden cost: `stream_mode="values"` re-sends the full state each step, which increases network bytes (not LLM tokens). Prefer `updates`.
- Token usage is available at the end of the stream (final `AIMessage.usage_metadata`); with OpenAI streaming you may need `stream_usage=True` on the model to receive it.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| stream_mode | What kind of chunks to stream | कैसे chunks चाहिए |
| values | Full state after each step | हर step की पूरी state |
| updates | Only node changes | सिर्फ node के बदलाव |
| messages | LLM tokens as they arrive | आते हुए LLM tokens |
| custom | Your own events via writer | अपने events |
| SSE | Server-Sent Events over HTTP | HTTP पर सर्वर से events |

---

## ⚡ 3-Line Summary
English: Streaming returns chunks while the graph runs, chosen by `stream_mode` (`values`, `updates`, `messages`, `custom`, `debug`). It makes apps feel fast and lets you show progress. Filter tokens by node, stop on disconnect, and disable proxy buffering.
Hindi: Streaming में graph चलते समय chunks मिलते हैं, जो `stream_mode` से चुने जाते हैं (`values`, `updates`, `messages`, `custom`, `debug`)। इससे app तेज़ लगता है और progress दिखता है। Tokens को node से filter करो, disconnect पर रुको और proxy buffering बंद करो।

---

## ➡️ Next Topic
**338. LangGraph + FastAPI** — packaging a graph as a production API: lifespan, checkpointers, auth, errors.
