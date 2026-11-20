---

# 153. Message Protocol
# हिंदी में: Message Protocol (agents के बीच messages का तरीका)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
In AutoGen Core agents talk only through typed messages (dataclasses or pydantic models). There are two delivery styles: direct request/response with `send_message` to an `AgentId`, and publish/subscribe with `publish_message` to a topic (`DefaultTopicId`). Subscribers declared with `@default_subscription` receive every published message whose type they handle.

## 🔵 सरल परिभाषा (Hindi)
AutoGen Core में agents सिर्फ़ typed messages (dataclass या pydantic models) से बात करते हैं। डिलीवरी के दो तरीके: `AgentId` को `send_message` से सीधा request/response, और topic (`DefaultTopicId`) पर `publish_message` से publish/subscribe। `@default_subscription` वाले subscribers हर उस published message को पाते हैं जिसका type वे सँभालते हैं।

---

## 🔴 Problem it Solves
If agents call each other directly they become tightly coupled: adding an auditor means editing the sender. Free-form strings are ambiguous and break silently. A protocol of typed messages and topics lets you add subscribers without touching producers and gives validation and serialisation.

## 🔴 यह क्यों बना? (Hindi)
Agents सीधे एक-दूसरे को call करें तो वे कसकर जुड़ जाते हैं: auditor जोड़ना हो तो sender बदलना पड़ता है। Free-form strings अस्पष्ट होती हैं और चुपचाप टूटती हैं। Typed messages और topics का protocol producers को छुए बिना subscribers जोड़ने देता है और validation व serialisation देता है।

---

## 🟢 How it Works

```
Step 1 -> Define typed messages (pydantic BaseModel is JSON-serialisable)
Step 2 -> Agents declare @message_handler for each message type they accept
Step 3 -> @default_subscription subscribes the agent to the default topic
Step 4 -> Producer calls publish_message(msg, DefaultTopicId()) and returns immediately
Step 5 -> Runtime delivers the message to EVERY subscriber with a matching handler
Step 6 -> A handler may publish follow-up events (a chain)
Step 7 -> Errors are handled inside handlers so one bad message does not kill the pipeline
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Typed messages बनाओ (pydantic BaseModel JSON-serialisable है)
Step 2 -> Agents हर स्वीकार्य message type के लिए @message_handler घोषित करते हैं
Step 3 -> @default_subscription agent को default topic से subscribe करता है
Step 4 -> Producer publish_message(msg, DefaultTopicId()) call करके तुरंत लौटता है
Step 5 -> Runtime message को हर उस subscriber तक पहुँचाता है जिसका handler मेल खाता है
Step 6 -> Handler आगे के events publish कर सकता है (श्रृंखला)
Step 7 -> Errors handlers के अंदर सँभाले जाते हैं ताकि एक खराब message पूरी pipeline न रोके
```

---

## 🟡 Real World Example
**Tariff Agent pipeline.** `InvoiceReady` is published once; `Auditor` and `Biller` both receive it (observed output: `auditor saw INV-1`, `biller duty=250.0`). In the FastAPI version `Shipment` events flow `Customs` -> `Cleared` -> `Notifier`; a bad HS code `9999` is recorded as `rejected S2: unknown HS` while the good one gives `cleared S1`, `notified S1`.

## 🟡 Real Example Hindi mein
**Tariff Agent pipeline.** `InvoiceReady` एक बार publish होता है; `Auditor` और `Biller` दोनों उसे पाते हैं (देखा गया output: `auditor saw INV-1`, `biller duty=250.0`)। FastAPI संस्करण में `Shipment` events `Customs` -> `Cleared` -> `Notifier` में बहते हैं; गलत HS code `9999` का नतीजा `rejected S2: unknown HS` दर्ज होता है जबकि सही वाले का `cleared S1`, `notified S1`।

---

## 💻 Code Example — Basic
Basic: two subscribers to the default topic receive the same pydantic event. Event handlers return `None`: publish is fire-and-forget.

```python
# Basic: message protocol: typed pydantic messages, pub/sub on topics (no direct addressing)
import asyncio  # loop
from pydantic import BaseModel  # message base
from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, default_subscription, message_handler  # core

class InvoiceReady(BaseModel):  # an event message (pydantic is JSON-serialisable)
    invoice_id: str  # id
    value: float  # value in USD

@default_subscription  # subscribes to the default topic
class Auditor(RoutedAgent):  # subscriber 1
    def __init__(self) -> None:  # init
        super().__init__("auditor")  # description

    @message_handler  # handler
    async def on_invoice(self, message: InvoiceReady, ctx: MessageContext) -> None:  # no return: events are fire-and-forget
        print(f"auditor saw {message.invoice_id}")  # side effect

@default_subscription  # also subscribes
class Biller(RoutedAgent):  # subscriber 2
    def __init__(self) -> None:  # init
        super().__init__("biller")  # description

    @message_handler  # handler
    async def on_invoice(self, message: InvoiceReady, ctx: MessageContext) -> None:  # handler
        print(f"biller duty={message.value * 0.25}")  # side effect

async def main() -> None:  # entry
    rt = SingleThreadedAgentRuntime()  # runtime
    await Auditor.register(rt, "auditor", lambda: Auditor())  # register
    await Biller.register(rt, "biller", lambda: Biller())  # register
    rt.start()  # start
    await rt.publish_message(InvoiceReady(invoice_id="INV-1", value=1000), DefaultTopicId())  # one publish -> both agents get it
    await rt.stop_when_idle()  # drain

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: request/response and pub/sub mixed in a FastAPI app: `/ship` publishes and returns immediately (`queued`); processing happens asynchronously; handler-side try/except records rejections; the runtime drains on shutdown (`stop_when_idle`) so the log is complete.

```python
# Advanced: request/response + pub/sub mixed, handler-side error handling, FastAPI trigger
from contextlib import asynccontextmanager  # lifespan
from typing import AsyncIterator  # type
from fastapi import FastAPI  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # messages
from autogen_core import DefaultTopicId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, default_subscription, message_handler  # core

LOG: list[str] = []  # collects what agents did (demo)

class Shipment(BaseModel):  # event
    sid: str  # id
    hs: str  # code

class Cleared(BaseModel):  # follow-up event
    sid: str  # id

@default_subscription  # listens on default topic
class Customs(RoutedAgent):  # first stage
    def __init__(self) -> None:  # init
        super().__init__("customs")  # desc

    @message_handler  # handles Shipment
    async def on_shipment(self, message: Shipment, ctx: MessageContext) -> None:  # handler
        try:  # isolate failures: one bad message must not kill the runtime
            if message.hs == "9999":  # invalid code
                raise ValueError("unknown HS")  # simulate failure
            LOG.append(f"cleared {message.sid}")  # record
            await self.publish_message(Cleared(sid=message.sid), DefaultTopicId())  # emit next event
        except ValueError as e:  # handle
            LOG.append(f"rejected {message.sid}: {e}")  # record rejection

@default_subscription  # listens
class Notifier(RoutedAgent):  # second stage
    def __init__(self) -> None:  # init
        super().__init__("notifier")  # desc

    @message_handler  # handles Cleared
    async def on_cleared(self, message: Cleared, ctx: MessageContext) -> None:  # handler
        LOG.append(f"notified {message.sid}")  # record

runtime = SingleThreadedAgentRuntime()  # runtime

@asynccontextmanager  # lifespan
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # signature
    await Customs.register(runtime, "customs", lambda: Customs())  # register
    await Notifier.register(runtime, "notifier", lambda: Notifier())  # register
    runtime.start()  # start
    yield  # serve
    await runtime.stop_when_idle()  # drain

app = FastAPI(lifespan=lifespan)  # app

@app.post("/ship")  # endpoint
async def ship(s: Shipment) -> dict[str, str]:  # handler
    await runtime.publish_message(s, DefaultTopicId())  # publish returns immediately (async processing)
    return {"queued": s.sid}  # ack

with TestClient(app) as c:  # lifespan
    print(c.post("/ship", json={"sid": "S1", "hs": "6403"}).json())  # good
    print(c.post("/ship", json={"sid": "S2", "hs": "9999"}).json())  # bad
print(LOG)  # after shutdown drain
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline (scripted `ReplayChatCompletionClient` or no model at all, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Message format | State dict | Strings / pydantic outputs | Items (pydantic/dataclass for output) | Typed dataclass / pydantic messages |
| Direct call | Edge to a node | Task delegation | Handoff / as_tool | send_message(msg, AgentId) request/response |
| Pub/sub | Not native | Not native | Not native | publish_message + subscriptions (topics) |
| Decoupling | Medium (edges) | Low | Low | High: add subscribers without changing producers |
| Validation | TypedDict/Pydantic state | Pydantic output | Pydantic output_type | Pydantic or dataclass types |
| Serialisation | Checkpoint | Limited | Limited | Built-in for pydantic / dataclass (needed for distributed) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting publish_message to return a reply.
✅ Correct: Publish is fire-and-forget (returns immediately). Use `send_message` when you need an answer.

❌ Mistake: Forgetting `@default_subscription` (or a subscription).
✅ Correct: Without a subscription a published message reaches nobody.

❌ Mistake: Letting exceptions escape in event handlers.
✅ Correct: Handle errors inside; record or publish a failure event so the pipeline continues.

❌ Mistake: Reading results before the runtime drained.
✅ Correct: Call `stop_when_idle()` before reading side effects (we print LOG after shutdown).

---

## 🧠 Tricky Interview Question
Three agents subscribe to the same event and one of them is slow, delaying a customer response. How do you design it?

Answer: Publish-based processing is asynchronous: the API should acknowledge (`queued`) and return; do not wait for all subscribers. Give the customer a job id and notify (webhook, polling) when the slow subscriber finishes. Keep handlers small, put slow LLM calls in their own agent, add timeouts and failure events, and use idempotency (event ids) so retries are safe. If the response truly depends on the slow agent, use `send_message` to that agent with a timeout instead of pub/sub.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] send_message vs publish_message?
A1: send_message addresses one agent by AgentId and awaits a reply; publish_message broadcasts an event to subscribers and returns immediately.

Q2: [Medium] Why pydantic for messages?
A2: Validation, JSON serialisation and clear schemas; essential if the runtime is distributed.

Q3: [Hard] How is a handler chosen?
A3: By the type annotation of the `message` parameter among the agent's @message_handler methods.

Q4: [Hard] How do you make event handlers safe to retry?
A4: Idempotency keys (event id), side-effect checks, deduplication store, and failure events instead of raising.

Q5: [System Design] Design a shipment event pipeline.
A5: Events: ShipmentReceived, HSValidated, DutyCalculated, Cleared/Rejected; one agent per stage; topics per tenant; dead-letter topic; metrics per event type; replay by event id.

---

## 💰 Cost Impact
Messaging itself costs no tokens. It can reduce LLM cost: rule-based stages (validation, rates) consume events without a model, and LLM agents only subscribe to the events that need language work. Keep message payloads compact: any content you forward into a prompt becomes input tokens. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Multiple consumers for one event (audit, billing, notification).
- You want decoupled stages.
- Async processing is acceptable.

❌ Avoid when:
- The caller needs one immediate answer (use send_message).
- Two-agent chat with a simple loop (AgentChat is enough).
- You cannot tolerate eventual consistency.

---

## 📊 Visual Diagram
```
 producer: publish_message(InvoiceReady, DefaultTopicId())
                     |
                     v
              [ topic: default ]
                 /          \
                v            v
          [Auditor]       [Biller]        (both @default_subscription)
        on_invoice()     on_invoice()
                              |
                              +--> publish(Cleared) --> [Notifier] ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Message | Typed data passed between agents | agents के बीच typed data |
| topic | Named channel for events | events का नामित channel |
| publish/subscribe | One-to-many delivery | एक-से-अनेक डिलीवरी |
| DefaultTopicId | The default topic | default topic |
| default_subscription | Subscribe agent to default topic | agent को default topic से जोड़ना |
| fire-and-forget | No reply expected | जवाब की अपेक्षा नहीं |
| idempotent | Safe to repeat | दोहराने पर भी सुरक्षित |

---

## ⚡ 3-Line Summary
English: Agents exchange typed messages: direct (send_message) or broadcast (publish_message).
Subscribers decouple producers from consumers.
Handle errors in handlers and drain the runtime before reading results.
Hindi: Agents typed messages का आदान-प्रदान करते हैं: सीधे (send_message) या broadcast (publish_message)।
Subscribers producers को consumers से अलग रखते हैं।
Handlers में errors सँभालें और नतीजे पढ़ने से पहले runtime को drain करें।

---

## ➡️ Next Topic
154. Agent Runtime -- lifecycle, identity (AgentId), state and shutdown.

---
