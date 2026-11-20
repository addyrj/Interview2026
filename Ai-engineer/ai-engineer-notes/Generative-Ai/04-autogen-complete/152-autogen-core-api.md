---

# 152. AutoGen Core API
# हिंदी में: AutoGen Core API (नीचे की actor-style परत)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`autogen-core` is the low-level layer of AutoGen v0.4: agents are actors that exchange typed messages through a runtime. You subclass `RoutedAgent`, decorate handlers with `@message_handler`, register the agent type with a `SingleThreadedAgentRuntime` and send messages. AgentChat (AssistantAgent, teams) is built on top of this.

## 🔵 सरल परिभाषा (Hindi)
`autogen-core` AutoGen v0.4 की निचली परत है: agents actors हैं जो runtime के ज़रिए typed messages का आदान-प्रदान करते हैं। आप `RoutedAgent` को subclass करते हैं, handlers पर `@message_handler` लगाते हैं, agent type को `SingleThreadedAgentRuntime` में register करते हैं और messages भेजते हैं। AgentChat (AssistantAgent, teams) इसी के ऊपर बना है।

---

## 🔴 Problem it Solves
AgentChat is great for chat-style teams, but some systems are event-driven: many independent services, custom routing, no 'conversation', maybe distributed. You need explicit message types, handlers, identity and lifecycle control. Core gives that without forcing a chat model.

## 🔴 यह क्यों बना? (Hindi)
AgentChat chat-style teams के लिए बढ़िया है, पर कुछ systems event-driven होते हैं: कई स्वतंत्र services, custom routing, कोई 'बातचीत' नहीं, शायद distributed। आपको स्पष्ट message types, handlers, पहचान और lifecycle नियंत्रण चाहिए। Core यह बिना chat मॉडल थोपे देता है।

---

## 🟢 How it Works

```
Step 1 -> Define message classes (dataclass or pydantic)
Step 2 -> Subclass RoutedAgent; mark methods with @message_handler (routed by the type hint of `message`)
Step 3 -> Create SingleThreadedAgentRuntime()
Step 4 -> await MyAgent.register(runtime, 'type_name', lambda: MyAgent())
Step 5 -> runtime.start() starts the processing loop
Step 6 -> await runtime.send_message(msg, AgentId(type, key)) = request/response
Step 7 -> await runtime.stop_when_idle() then close()
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Message classes बनाओ (dataclass या pydantic)
Step 2 -> RoutedAgent को subclass करो; methods पर @message_handler लगाओ (`message` के type hint से routing)
Step 3 -> SingleThreadedAgentRuntime() बनाओ
Step 4 -> await MyAgent.register(runtime, 'type_name', lambda: MyAgent())
Step 5 -> runtime.start() processing loop शुरू करता है
Step 6 -> await runtime.send_message(msg, AgentId(type, key)) = request/response
Step 7 -> await runtime.stop_when_idle() फिर close()
```

---

## 🟡 Real World Example
**Tariff Agent as a service.** A `Classifier` agent handles a `Classify` message and returns `Classified(hs='6403', tokens_estimate=...)`. FastAPI owns one runtime for the app's lifetime (lifespan). Empty text raises `ValueError` inside the handler; it propagates to the caller and becomes HTTP 422. The LLM call is a stand-in here, so the token number is a rough 4-characters-per-token heuristic, not a measurement.

## 🟡 Real Example Hindi mein
**Service के रूप में Tariff Agent.** `Classifier` agent `Classify` message सँभालकर `Classified(hs='6403', tokens_estimate=...)` लौटाता है। FastAPI पूरे app जीवनकाल के लिए एक runtime रखता है (lifespan)। खाली text पर handler में `ValueError` आता है; वह caller तक जाकर HTTP 422 बनता है। LLM call यहाँ नकली है, इसलिए token संख्या सिर्फ़ 4-अक्षर-प्रति-token अंदाज़ा है, मापी हुई नहीं।

---

## 💻 Code Example — Basic
Basic: a `RoutedAgent` with one typed handler, registered and called directly with `send_message`. The result was `RateResponse(rate=0.25)`.

```python
# Basic: AutoGen Core: a RoutedAgent with a typed message handler, called directly
import asyncio  # loop
from dataclasses import dataclass  # message classes
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler  # core API

@dataclass  # request message
class RateRequest:  # typed
    hs_code: str  # HS code

@dataclass  # response message
class RateResponse:  # typed
    rate: float  # duty rate

class RateAgent(RoutedAgent):  # your own agent class
    def __init__(self) -> None:  # constructor
        super().__init__("Looks up duty rates")  # description

    @message_handler  # routes by the type hint of `message`
    async def on_request(self, message: RateRequest, ctx: MessageContext) -> RateResponse:  # handler
        return RateResponse(rate=0.25 if message.hs_code.startswith("6403") else 0.10)  # logic

async def main() -> None:  # entry
    rt = SingleThreadedAgentRuntime()  # in-process runtime
    await RateAgent.register(rt, "rate_agent", lambda: RateAgent())  # factory: runtime creates instances lazily
    rt.start()  # start the background loop
    out = await rt.send_message(RateRequest("6403.99"), AgentId("rate_agent", "default"))  # direct request/response
    print(out)  # RateResponse(rate=0.25)
    await rt.stop_when_idle()  # drain and stop

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: one runtime for the app lifetime started and stopped in a FastAPI lifespan, handler-side validation, HTTP 422 on handler errors. The classification is a stand-in for an LLM call.

```python
# Advanced: Core agent wrapping an LLM-style tool + FastAPI + error handling; one runtime for the app lifetime
from contextlib import asynccontextmanager  # lifespan
from dataclasses import dataclass  # messages
from typing import AsyncIterator  # type
from fastapi import FastAPI, HTTPException  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler  # core

@dataclass  # message
class Classify:  # request
    text: str  # product text

@dataclass  # message
class Classified:  # response
    hs: str  # code
    tokens_estimate: int  # rough size

class Classifier(RoutedAgent):  # agent
    def __init__(self) -> None:  # init
        super().__init__("HS classifier")  # description

    @message_handler  # handler
    async def on_classify(self, message: Classify, ctx: MessageContext) -> Classified:  # typed
        if not message.text.strip():  # validate
            raise ValueError("empty text")  # propagates to the caller of send_message
        hs = "6403" if "shoe" in message.text.lower() else "9999"  # stand-in for an LLM call
        return Classified(hs=hs, tokens_estimate=len(message.text) // 4)  # ~4 chars per token heuristic

runtime = SingleThreadedAgentRuntime()  # one runtime per process

@asynccontextmanager  # lifespan
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # signature
    await Classifier.register(runtime, "classifier", lambda: Classifier())  # register
    runtime.start()  # start
    yield  # serve
    await runtime.stop_when_idle()  # graceful stop
    await runtime.close()  # release

app = FastAPI(lifespan=lifespan)  # app

class Req(BaseModel):  # body
    text: str  # text

@app.post("/classify")  # endpoint
async def classify(req: Req) -> dict[str, object]:  # handler
    try:  # guard
        out = await runtime.send_message(Classify(req.text), AgentId("classifier", "default"))  # call agent
    except Exception as e:  # handler error
        raise HTTPException(422, str(e))  # client error
    return {"hs": out.hs, "tokens_estimate": out.tokens_estimate}  # response

with TestClient(app) as c:  # lifespan runs inside context manager
    print(c.post("/classify", json={"text": "leather shoes"}).json())  # ok
    print(c.post("/classify", json={"text": " "}).status_code)  # error path
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline (scripted `ReplayChatCompletionClient` or no model at all, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Abstraction level | Graph (high) | Crew/Task (high) | Agents/Runner (high) | Core: actors + messages (low), AgentChat on top |
| Message types | State dict / TypedDict | Task context strings | Items / strings | Typed dataclass or pydantic messages |
| Routing | Edges | Process | Handoffs | @message_handler by type; topics for pub/sub |
| Distributed | Via platform | Not core | Not core | Runtime can be local (SingleThreaded) or distributed (gRPC extension) |
| Identity | Node names | Agent role | Agent name | AgentId(type, key) |
| Best for | Workflows | Role teams | Agent apps | Event-driven, custom architectures |

---

## ⚠️ Common Mistakes
❌ Mistake: Calling handlers directly instead of through the runtime.
✅ Correct: Always `send_message` / `publish_message`; the runtime provides identity, queues and context.

❌ Mistake: Forgetting `runtime.start()`.
✅ Correct: Messages are queued but never processed; the call hangs.

❌ Mistake: Missing type hint on `message`.
✅ Correct: Routing uses the annotation of the `message` parameter; without it the handler is not found.

❌ Mistake: Not stopping the runtime.
✅ Correct: Use `stop_when_idle()` (drain) or `stop()` and then `close()`, ideally in the app lifespan.

---

## 🧠 Tricky Interview Question
When would you drop below AgentChat to Core?

Answer: When the conversation metaphor does not fit: independent services reacting to events, custom message protocols, agents that run for long times with their own state, multi-tenant agent instances addressed by key, or distributed deployment across processes. Use AgentChat for normal tool-using assistants and teams (less code); use Core when you need explicit control of messages, topics, identities and lifecycle. Both can mix: AgentChat agents can run on a Core runtime.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does @message_handler do?
A1: It registers a method as the handler for the message type given in the annotation of its `message` parameter.

Q2: [Medium] What is an AgentId?
A2: A pair (type, key): the registered agent type and an instance key, e.g. AgentId('classifier','default').

Q3: [Hard] Why must you start the runtime?
A3: `runtime.start()` starts the background message-processing task; before it, send_message awaits forever.

Q4: [Hard] How do errors in handlers surface?
A4: For request/response `send_message` the exception propagates to the caller (we mapped it to HTTP 422).

Q5: [System Design] Design an event-driven customs system with Core.
A5: Typed events (ShipmentReceived, HSAssigned, DutyCalculated), one agent type per stage subscribing to topics, per-shipment keys for state, a dead-letter handling policy, runtime per process or distributed runtime, metrics per handler.

---

## 💰 Cost Impact
Core itself costs no tokens; only your handlers' model calls do. Because you control messages, you control prompts: send small typed payloads rather than whole histories. Per-key agent instances (see 154) keep per-tenant state without re-sending it. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Event-driven or distributed agent systems.
- You need typed messages and explicit identity.
- You are building a framework layer.

❌ Avoid when:
- A chat-style team of 2-3 agents (AgentChat is simpler).
- Prototype speed matters most.
- You do not want to manage the runtime lifecycle.

---

## 📊 Visual Diagram
```
 FastAPI request
     |
     v
 SingleThreadedAgentRuntime  (start ... stop_when_idle / close)
     |  send_message(Classify, AgentId('classifier','default'))
     v
 +---------------------------+
 | Classifier(RoutedAgent)   |
 |  @message_handler         |
 |  on_classify(Classify)    |--> Classified(hs, tokens_estimate)
 +---------------------------+
     | exception -> propagates -> HTTP 422
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| RoutedAgent | Agent base class that routes by message type | message type से route करने वाली base class |
| message_handler | Decorator registering a handler | handler register करने वाला decorator |
| runtime | Engine delivering messages | messages पहुँचाने वाला engine |
| AgentId | (type, key) identity | (type, key) पहचान |
| send_message | Request/response call | request/response call |
| register | Bind agent type to a factory | agent type को factory से जोड़ना |
| actor | Independent message-driven component | स्वतंत्र message-चालित घटक |

---

## ⚡ 3-Line Summary
English: Core is the actor-style layer: typed messages, RoutedAgent handlers, a runtime.
Register, start, send, stop_when_idle, close.
Use it for event-driven systems; AgentChat is built on it.
Hindi: Core actor-style परत है: typed messages, RoutedAgent handlers, runtime।
Register, start, send, stop_when_idle, close।
Event-driven systems के लिए इस्तेमाल करें; AgentChat इसी पर बना है।

---

## ➡️ Next Topic
153. Message Protocol -- designing typed messages, topics and pub/sub.

---
