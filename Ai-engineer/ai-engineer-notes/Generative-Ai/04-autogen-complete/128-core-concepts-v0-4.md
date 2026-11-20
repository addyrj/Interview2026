---

# 128. Core Concepts v0.4
# हिंदी में: AutoGen v0.4 की मूल अवधारणाएँ
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
AutoGen Core (`autogen-core`) is the lowest layer of v0.4. It has four ideas: messages (plain dataclasses/pydantic), agents (`RoutedAgent` with `@message_handler` methods), a runtime (`SingleThreadedAgentRuntime`) that delivers messages, and topics/subscriptions for publish-subscribe. AgentChat is built on top of it.

## 🔵 सरल परिभाषा (Hindi)
AutoGen Core (`autogen-core`) v0.4 की सबसे निचली layer है। इसमें चार विचार हैं: messages (सादे dataclass/pydantic), agents (`@message_handler` वाले methods के साथ `RoutedAgent`), runtime (`SingleThreadedAgentRuntime`) जो messages पहुँचाता है, और publish-subscribe के लिए topics/subscriptions। AgentChat इसी के ऊपर बना है।

---

## 🔴 Problem it Solves
High-level chat abstractions hide how messages flow. When you need agents that react to events (a new shipment arrives, a customs update is published), run in different processes, mix languages (Python and .NET) or have exact control over who gets which message, a chat loop is too limiting. Without a clear runtime model you also cannot reason about concurrency, state per agent instance, or message ordering.

## 🔴 यह क्यों बना? (Hindi)
High-level chat abstractions यह छुपा देते हैं कि messages कैसे बहते हैं। जब agents को events पर react करना हो (नई shipment आई, customs update publish हुआ), अलग processes में चलना हो, या यह तय करना हो कि कौन सा message किसे जाए, तब chat loop कम पड़ता है। साफ runtime model के बिना concurrency, per-agent state और message ordering समझना भी मुश्किल है।

---

## 🟢 How it Works

```
Step 1 -> Define message types (dataclass): RateQuery, RateReply
Step 2 -> Subclass RoutedAgent; mark methods with @message_handler (type hint of `message` selects the handler)
Step 3 -> Create a runtime: SingleThreadedAgentRuntime()
Step 4 -> Register an agent TYPE with a factory: Agent.register(runtime, 'tariff', lambda: Agent())
Step 5 -> runtime.start()  (background loop processes the queue)
Step 6 -> Direct call: await runtime.send_message(msg, AgentId('tariff','key'))  -> returns reply
Step 7 -> Or broadcast: await runtime.publish_message(msg, DefaultTopicId())  -> every subscriber handles it
Step 8 -> AgentId(type, key) lazily creates ONE instance per key (state isolation per session)
Step 9 -> await runtime.stop_when_idle() drains the queue and stops
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> message types (dataclass) बनाओ: RateQuery, RateReply
Step 2 -> RoutedAgent को subclass करो; methods पर @message_handler लगाओ (`message` का type hint handler चुनता है)
Step 3 -> runtime बनाओ: SingleThreadedAgentRuntime()
Step 4 -> agent TYPE को factory के साथ register करो: Agent.register(runtime, 'tariff', lambda: Agent())
Step 5 -> runtime.start()  (background loop queue process करता है)
Step 6 -> सीधा call: await runtime.send_message(msg, AgentId('tariff','key'))  -> reply मिलता है
Step 7 -> या broadcast: await runtime.publish_message(msg, DefaultTopicId())  -> हर subscriber handle करता है
Step 8 -> AgentId(type, key) हर key पर एक instance lazily बनाता है (session के हिसाब से state अलग)
Step 9 -> await runtime.stop_when_idle() queue खाली करके रुकता है
```

---

## 🟡 Real World Example
**Tariff event pipeline.** A customs broker system publishes a `Shipment` event. A `DutyAgent` computes duty, an `AuditAgent` writes an audit line, both subscribed to the same topic. Neither knows the other exists. Adding a `FraudAgent` later means registering one more agent, with no changes to the publisher. This is the decoupling that chat-style frameworks do not give you.

## 🟡 Real Example Hindi mein
**Tariff event pipeline.** Customs broker system एक `Shipment` event publish करता है। `DutyAgent` duty निकालता है, `AuditAgent` audit line लिखता है, दोनों एक ही topic पर subscribed हैं। कोई किसी को नहीं जानता। बाद में `FraudAgent` जोड़ना हो तो बस एक और agent register करो, publisher में बदलाव नहीं। यह decoupling chat-style frameworks में नहीं मिलती।

---

## 💻 Code Example — Basic
Basic: a `RoutedAgent` with one `@message_handler`, called directly with `send_message`. No LLM involved: Core is about message delivery.

```python
# AutoGen v0.4 CORE: agent + message + runtime (autogen-core 0.7.5, offline, no LLM needed)
import asyncio                                                    # core is async
from dataclasses import dataclass                                 # messages are plain dataclasses/pydantic models
from autogen_core import (AgentId, MessageContext, RoutedAgent,   # core building blocks
                          SingleThreadedAgentRuntime, message_handler)

@dataclass                                                        # message type 1: request
class RateQuery:
    hs_code: str                                                  # HS code asked about

@dataclass                                                        # message type 2: reply
class RateReply:
    rate: str                                                     # duty rate found

class TariffLookupAgent(RoutedAgent):                             # RoutedAgent dispatches by message TYPE
    def __init__(self) -> None:
        super().__init__("Looks up tariff rates")                 # description of the agent
        self._table: dict[str, str] = {"6109.10": "20%"}          # private state (one instance per AgentId)

    @message_handler                                              # handler chosen from the type hint of `message`
    async def on_query(self, message: RateQuery, ctx: MessageContext) -> RateReply:
        return RateReply(rate=self._table.get(message.hs_code, "unknown"))  # return value = direct response

async def main() -> None:
    runtime = SingleThreadedAgentRuntime()                        # in-process runtime (local; a gRPC runtime exists for distributed)
    await TariffLookupAgent.register(runtime, "tariff", lambda: TariffLookupAgent())  # agent TYPE + factory
    runtime.start()                                               # start background message loop
    reply = await runtime.send_message(                           # direct (RPC-style) message
        RateQuery("6109.10"), AgentId("tariff", "session-1"))     # AgentId = (type, key) -> one instance per key
    print(reply)                                                  # RateReply(rate='20%')
    await runtime.stop_when_idle()                                # drain and stop cleanly

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: publish/subscribe with two subscribers on the default topic, exposed through FastAPI with input validation and a timeout around `stop_when_idle`.

```python
# Core pub/sub (topics + subscriptions) behind a FastAPI endpoint, with error handling
import asyncio                                                    # async runtime
from dataclasses import dataclass                                 # message types
from fastapi import FastAPI, HTTPException                        # web layer
from fastapi.testclient import TestClient                         # offline test of the API
from autogen_core import (DefaultTopicId, MessageContext, RoutedAgent,  # core pieces
                          SingleThreadedAgentRuntime, default_subscription, message_handler)

@dataclass
class Shipment:                                                   # event published to the topic
    hs_code: str                                                  # product code
    value_usd: float                                              # declared value

RESULTS: list[str] = []                                           # shared sink for the demo (use a queue/DB in prod)

@default_subscription                                             # every agent subscribes to the default topic
class DutyAgent(RoutedAgent):                                     # computes duty
    def __init__(self) -> None:
        super().__init__("duty calculator")                       # description
    @message_handler                                              # runs for each Shipment published
    async def on_shipment(self, message: Shipment, ctx: MessageContext) -> None:
        rate = {"6109.10": 0.20}.get(message.hs_code)             # lookup
        if rate is None:                                          # unknown code -> record error, do not crash runtime
            RESULTS.append(f"ERROR unknown hs_code {message.hs_code}")
            return
        RESULTS.append(f"duty={message.value_usd * rate:.2f} USD") # business result

@default_subscription                                             # second subscriber to the SAME topic
class AuditAgent(RoutedAgent):                                    # audit log (fan-out demo)
    def __init__(self) -> None:
        super().__init__("auditor")
    @message_handler
    async def on_shipment(self, message: Shipment, ctx: MessageContext) -> None:
        RESULTS.append(f"audit: saw {message.hs_code}")           # both agents receive the same event

app = FastAPI()                                                   # web app

@app.post("/shipment")                                            # async endpoint
async def post_shipment(s: dict) -> dict:
    if "hs_code" not in s or "value_usd" not in s:                # validate input early
        raise HTTPException(422, "hs_code and value_usd required")
    RESULTS.clear()                                               # demo only
    runtime = SingleThreadedAgentRuntime()                        # one runtime per request keeps demo isolated
    await DutyAgent.register(runtime, "duty", lambda: DutyAgent())    # register types
    await AuditAgent.register(runtime, "audit", lambda: AuditAgent())
    runtime.start()                                               # start loop
    try:
        await runtime.publish_message(Shipment(s["hs_code"], float(s["value_usd"])), DefaultTopicId())  # fan-out
        await asyncio.wait_for(runtime.stop_when_idle(), timeout=10)  # wait until all handlers finish
    except asyncio.TimeoutError:
        raise HTTPException(504, "agents timed out")
    return {"results": sorted(RESULTS)}                           # deterministic order

if __name__ == "__main__":
    print(TestClient(app).post("/shipment", json={"hs_code": "6109.10", "value_usd": 500}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Core primitive | State + node functions | Agent/Task/Crew | Agent + Runner | Message + RoutedAgent + Runtime |
| Communication | Shared graph state | Task output passes on | Handoff / tool call | Direct send or pub-sub topics |
| Event-driven | Via triggers/streams | Limited | No (loop based) | Yes, first-class |
| Per-agent state | In graph state | Agent memory | Agent context object | One instance per AgentId key |
| Distribution | Hosted platform | No | No | gRPC host + workers (extension) |
| Learning curve | Medium | Low | Low | Higher (actor model) |

---

## ⚠️ Common Mistakes
❌ Mistake: Treating `AgentId` as a class name. Calling `send_message(msg, 'tariff')`.
✅ Correct: `AgentId(type, key)`: the type is the registered name, the key selects the instance (e.g. session id).

❌ Mistake: Forgetting `runtime.start()` or `stop_when_idle()`: messages are queued but nothing runs, or the program exits early.
✅ Correct: Always `start()` after registration and `await stop_when_idle()` (or `stop()`) at the end.

❌ Mistake: Putting per-user data in module globals shared by all instances.
✅ Correct: Keep state on `self`; use the key in `AgentId` for isolation, and external storage if you scale beyond one process.

❌ Mistake: Raising exceptions in a handler and expecting the caller to survive.
✅ Correct: For `send_message` the exception propagates to the caller; for `publish_message` it is logged by the runtime. Catch and convert to a result message yourself.

---

## 🧠 Tricky Interview Question
Two requests with different session ids hit the same registered agent type at the same time. Does user B ever see user A's state?

Answer: No, as long as you use different `AgentId` keys. The runtime lazily creates one agent instance per (type, key), so `self` state is per key. But handlers of one instance are processed sequentially (single threaded runtime), so a slow handler blocks other messages for that same instance, not for other keys. The danger is shared module-level state or reusing one key for all users. For a multi-process deployment you also need an external store because instances live in process memory, and you must route the same key to the same worker.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What are the three layers of AutoGen v0.4?
A1: Core (runtime, messages, agents), AgentChat (AssistantAgent, teams), Extensions (model clients, code executors, MCP and other integrations).

Q2: [Medium] What is the difference between `send_message` and `publish_message`?
A2: `send_message` is a direct RPC-style call to one AgentId and returns the handler's return value. `publish_message` broadcasts to a TopicId; every agent subscribed gets it and there is no return value.

Q3: [Hard] How does a `RoutedAgent` decide which method handles a message?
A3: `@message_handler` inspects the type annotation of the `message` parameter; the runtime dispatches by message type (and optionally a match function).

Q4: [Hard] Why does AutoGen use an actor-style runtime instead of a plain chat loop?
A4: Actors isolate state per instance, process messages sequentially per instance, and communicate only by messages. That gives concurrency without locks, easy distribution across processes, and loose coupling between agents.

Q5: [System Design] Design a duty-and-compliance system where new checks are added without touching existing code.
A5: Publish a `Shipment` event to a topic. Each check (duty, sanctions, restricted goods) is a separate subscribed `RoutedAgent` that publishes its own result event. An aggregator agent subscribes to result events keyed by shipment id and publishes the final decision. Add checks by registering new agents; use a gRPC worker runtime when checks must scale independently.

---

## 💰 Cost Impact
Core itself spends no tokens: message passing is just Python. Cost appears only when a handler calls a model client. Pub-sub fan-out multiplies cost: if 5 subscribers each call an LLM with a 1,500 token prompt, one event costs about 5 x (1,500 prompt + completion) tokens. Mitigate by (1) using plain code or rules in handlers that do not need an LLM, (2) filtering with specific topics instead of the default topic, (3) caching results by key. Formula: `event_cost = sum(handler_prompt_tokens * in_price + handler_completion_tokens * out_price)`. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Event-driven systems: many agents reacting to the same events.
- Agents must run in different processes/languages.
- You need full control over message types and routing.
- You are building your own higher-level abstraction.

❌ Avoid when:
- A simple assistant with tools: AgentChat's `AssistantAgent` is faster to build.
- A small team with fixed order: use `RoundRobinGroupChat`.
- Your team cannot support actor-model debugging.

---

## 📊 Visual Diagram
```
 publisher / API
      | publish_message(Shipment, TopicId)          send_message(RateQuery, AgentId)
      v                                                   |
 +--------------- SingleThreadedAgentRuntime ---------------+
 |   message queue  ->  subscription matching  ->  dispatch |
 +----------------------------------------------------------+
      |                        |                         |
      v                        v                         v
 DutyAgent[key=s1]      AuditAgent[key=s1]       TariffLookupAgent[key=s1]
 @message_handler       @message_handler         @message_handler -> returns RateReply
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Runtime | Delivers messages and manages agent lifecycle | Messages पहुँचाता है और agents manage करता है |
| RoutedAgent | Agent whose handlers are chosen by message type | message type से handler चुनने वाला agent |
| AgentId | (type, key) pair identifying one instance | (type, key) जो एक instance पहचानता है |
| TopicId | (type, source) address for broadcast | broadcast का पता |
| Subscription | Rule linking topics to agent types | topic को agent type से जोड़ने का नियम |
| message_handler | Decorator marking a handler method | handler method का decorator |
| send_message | Direct RPC-style call | सीधा RPC-style call |
| publish_message | Broadcast to subscribers | subscribers को broadcast |

---

## ⚡ 3-Line Summary
English: Core = messages + RoutedAgent + runtime + topics.
Use `send_message` for direct calls and `publish_message` for fan-out; one agent instance exists per AgentId key.
Core spends no tokens by itself; cost comes from LLM calls inside handlers.
Hindi: Core = messages + RoutedAgent + runtime + topics।
सीधे call के लिए `send_message` और fan-out के लिए `publish_message`; हर AgentId key पर एक agent instance बनता है।
Core खुद tokens खर्च नहीं करता; खर्च handlers के अंदर के LLM calls से आता है।

---

## ➡️ Next Topic
129. AgentChat -- High Level API -- the layer you will use 90 percent of the time, built on the Core ideas above.

---
