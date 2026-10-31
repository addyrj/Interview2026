---

# 348. Agent Communication
# हिंदी में: Agent Communication

---

## 🔵 Simple Definition (English)
Agent communication is how agents pass information to each other. The main ways are: direct messages (A sends to B), shared state (all read/write one object) and a message bus or queue (publish/subscribe). The format should be structured, not free text.

## 🔵 सरल परिभाषा (Hindi)
Agent communication यानी agents आपस में जानकारी कैसे भेजते हैं। मुख्य तरीके: direct messages (A से B), shared state (सब एक object पढ़ते/लिखते हैं) और message bus/queue (publish/subscribe)। Format structured होना चाहिए, free text नहीं।

---

## 🔴 Problem it Solves
- Agents that cannot share results cannot cooperate.
- Free-text handoffs lose details ("the code I found earlier").
- Passing the full chat history to every agent wastes tokens.
- Without message ids and types, you cannot trace or replay what happened.

## 🔴 यह क्यों बना? (Hindi)
- जो agents results share नहीं कर सकते वे cooperate नहीं कर सकते।
- Free-text handoff में details खो जाती हैं।
- हर agent को पूरी history भेजना tokens की बर्बादी है।
- Message id और type के बिना trace/replay संभव नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a Message schema: id, sender, receiver, type, payload
Step 2 → Sender builds a Message and puts it on a channel (queue / state key)
Step 3 → Receiver reads only messages addressed to it
Step 4 → Receiver validates the payload, runs its LLM/tool step
Step 5 → Receiver publishes a reply Message (same correlation id)
Step 6 → Logger stores every message for tracing and replay
Step 7 → Coordinator stops when a "final" message arrives or max steps hit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Message schema तय करो: id, sender, receiver, type, payload
Step 2 → Sender Message बनाकर channel (queue / state key) में डालता है
Step 3 → Receiver सिर्फ अपने नाम वाले messages पढ़ता है
Step 4 → Receiver payload validate करके अपना LLM/tool step चलाता है
Step 5 → Receiver उसी correlation id के साथ reply Message भेजता है
Step 6 → Logger हर message tracing/replay के लिए store करता है
Step 7 → "final" message आने या max steps पर Coordinator रुकता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: the researcher sends `{"type": "candidates", "codes": ["6109.10", "6110.20"]}` to the validator. The validator replies `{"type": "verdict", "code": "6109.10", "ok": true}`. Both messages carry the same `trace_id`, so support can open one request and see the full agent conversation.

**Zomato**: order agent publishes `order_placed`; delivery and notification agents subscribe. **Amazon**: refund agent listens for `return_approved`.

## 🟡 Real Example Hindi mein
**Tariff System**: researcher validator को `{"type": "candidates", "codes": [...]}` भेजता है। Validator `{"type": "verdict", ...}` से जवाब देता है। दोनों में same `trace_id` है, इसलिए support एक request खोलकर पूरी agent बातचीत देख सकता है।

**Zomato**: order agent `order_placed` publish करता है, delivery और notification agents subscribe करते हैं।

---

## 💻 Code Example — Basic
```python
# A tiny in-memory mailbox so agents can exchange structured messages
from dataclasses import dataclass, field  # typed message container
from collections import defaultdict, deque  # mailbox storage
import uuid  # unique ids


@dataclass
class Message:
    sender: str  # who sent it
    receiver: str  # who should read it
    type: str  # message type, e.g. "candidates"
    payload: dict  # structured data
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:6])  # short id


class Bus:
    def __init__(self) -> None:
        self.boxes: dict[str, deque[Message]] = defaultdict(deque)  # one queue per agent

    def send(self, msg: Message) -> None:
        self.boxes[msg.receiver].append(msg)  # put into receiver's queue

    def receive(self, name: str) -> Message | None:
        box = self.boxes[name]  # get this agent's queue
        return box.popleft() if box else None  # oldest message or None


bus = Bus()  # create the bus
bus.send(Message("researcher", "validator", "candidates", {"codes": ["6109.10"]}))
msg = bus.receive("validator")  # validator reads its mail
print(msg)  # show the message
```

## 💻 Code Example — Advanced
```python
# Async bus with trace ids, validation, timeout and message log
import asyncio  # async primitives
import logging  # logging
from typing import Literal  # restricted values
from pydantic import BaseModel, Field  # validation

log = logging.getLogger("bus")  # logger


class Msg(BaseModel):
    trace_id: str  # one id per user request
    sender: str  # sender name
    receiver: str  # receiver name
    kind: Literal["task", "result", "error", "final"]  # allowed kinds
    payload: dict = Field(default_factory=dict)  # data


class AsyncBus:
    def __init__(self, agents: list[str]) -> None:
        self.queues = {a: asyncio.Queue[Msg]() for a in agents}  # queue per agent
        self.history: list[Msg] = []  # full log for replay

    async def send(self, m: Msg) -> None:
        if m.receiver not in self.queues:  # unknown target
            raise KeyError(f"unknown receiver {m.receiver}")
        self.history.append(m)  # record it
        await self.queues[m.receiver].put(m)  # deliver

    async def recv(self, name: str, timeout: float = 2.0) -> Msg:
        try:  # avoid waiting forever
            return await asyncio.wait_for(self.queues[name].get(), timeout)
        except asyncio.TimeoutError as exc:
            raise TimeoutError(f"{name} got no message") from exc


async def validator(bus: AsyncBus) -> None:
    m = await bus.recv("validator")  # wait for work
    ok = bool(m.payload.get("codes"))  # trivial check
    await bus.send(Msg(trace_id=m.trace_id, sender="validator", receiver="main",
                       kind="final", payload={"ok": ok}))  # reply


async def main() -> None:
    bus = AsyncBus(["validator", "main"])  # create bus
    worker = asyncio.create_task(validator(bus))  # start validator
    await bus.send(Msg(trace_id="t1", sender="main", receiver="validator",
                       kind="task", payload={"codes": ["6109.10"]}))
    print((await bus.recv("main")).payload)  # read final answer
    await worker  # make sure worker ended
    print(len(bus.history), "messages logged")  # audit trail


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Return the message trail with the API result. This makes debugging and audit simple.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class Ask(BaseModel):
    description: str  # product text


@app.post("/classify")
async def classify(req: Ask) -> dict:
    trace_id = "req-123"  # in real code use uuid4
    trail = [  # messages exchanged (mock)
        {"trace_id": trace_id, "from": "researcher", "to": "validator", "kind": "task"},
        {"trace_id": trace_id, "from": "validator", "to": "main", "kind": "final"},
    ]
    return {"answer": "6109.10", "trace": trail}  # answer + audit trail
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph uses shared state plus messages. `MessagesState` holds a list of messages that nodes append to; `Command(goto=..., update=...)` lets a node send a result and choose the next agent in one return.

```python
from langgraph.graph import StateGraph, MessagesState, START, END  # graph API
from langgraph.types import Command  # routing + update object
from langchain_core.messages import AIMessage  # message type


def researcher(state: MessagesState) -> Command:
    msg = AIMessage(content="candidates: 6109.10", name="researcher")  # message to share
    return Command(update={"messages": [msg]}, goto="validator")  # send + route


def validator(state: MessagesState) -> Command:
    last = state["messages"][-1].content  # read previous message
    return Command(update={"messages": [AIMessage(content=f"ok: {last}", name="validator")]}, goto=END)


g = StateGraph(MessagesState)  # graph with message state
g.add_node("researcher", researcher)  # node
g.add_node("validator", validator)  # node
g.add_edge(START, "researcher")  # entry
app = g.compile()  # compile
print(app.invoke({"messages": [("user", "t-shirt")]})["messages"][-1].content)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Free-text handoffs.
✅ Correct: Typed payloads.

```python
# Wrong
handoff = "found a few codes, check them"
# Right
handoff = {"kind": "candidates", "codes": ["6109.10", "6110.20"]}
```

❌ Mistake 2: Broadcasting everything to everyone.
✅ Correct: Address messages and filter.

```python
# Wrong: each agent reads all messages -> N times the tokens
# Right: only messages where receiver == me
inbox = [m for m in [{"to": "a"}, {"to": "b"}] if m["to"] == "a"]
```

---

## 🧠 Tricky Interview Question
**Q**: "Two agents keep replying to each other forever. How do you detect and stop it?"

**Answer**: Add a max-hop counter in the message (or `recursion_limit` in LangGraph), a `final` message type that ends the run, loop detection (same payload hash repeated), and a timeout. Also fix the cause: a missing termination rule in the prompts. On limit, return a partial result with an error flag instead of continuing.

---

## ⚫ Interview Questions + Answers

Q1: What are the ways agents communicate?
A1: Direct messages, shared state (blackboard) and a message bus (pub/sub or queue).

Q2: Why use structured messages?
A2: They can be validated, parsed, logged and replayed; free text is ambiguous and error-prone.

Q3: Shared state versus message passing?
A3: Shared state is simple and good for small workflows, but agents may overwrite each other. Message passing isolates agents, scales better and is easier to audit, but needs routing code.

Q4: What is a trace id?
A4: One id attached to every message of a request, so all LLM calls and messages can be grouped in logs or LangSmith.

Q5: How do you keep communication cost low in a 10-agent system?
A5: Send summaries or references (ids, not full documents), use typed fields, address messages so each agent reads only its own, store big artifacts in a database and pass keys, compress history with summarisation, and cap hops.

---

## 🔷 When to Use + When Not to Use
✅ Use message passing when:
- Agents run in separate processes or services
- You need audit and replay

✅ Use shared state when:
- Small workflow in one process (LangGraph)

❌ Avoid when:
- A direct function call between two Python functions is enough

---

## 📊 Visual Diagram
```
 Direct:      A ───msg──► B

 Shared state:  A ──write──► [ STATE ] ◄──read── B

 Bus:        A ──publish──► [ topic ] ──► B
                                     └──► C
 Every message: {trace_id, sender, receiver, kind, payload}
```

---

## 💰 Cost Impact
Messages that are put into prompts cost input tokens for every receiving agent. If 5 agents each receive a 4,000-token history, one request costs 20,000 input tokens. Pass compact payloads (200 tokens), summaries and ids to cut this by 10x or more. Logging messages itself is free of token cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Message | Unit sent between agents | agents के बीच भेजी इकाई |
| Shared state | Common data object | साझा data object |
| Message bus | Queue/pub-sub channel | message भेजने का channel |
| Trace id | Id grouping one request | एक request का id |
| Payload | Data inside message | message के अंदर का data |
| Hop limit | Max message steps | अधिकतम steps की सीमा |

---

## ⚡ 3-Line Summary
English: Agents communicate by messages, shared state or a bus. Use typed, addressed messages with a trace id. Always add loop limits and log everything.
Hindi: Agents messages, shared state या bus से communicate करते हैं। Typed, addressed messages और trace id use करो। Loop limits ज़रूर लगाओ और सब कुछ log करो।

---

## ➡️ Next Topic
**349. Supervisor Architecture** — one supervisor agent that decides which worker agent runs next.
