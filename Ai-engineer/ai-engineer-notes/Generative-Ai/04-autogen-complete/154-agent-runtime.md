---

# 154. Agent Runtime
# हिंदी में: Agent Runtime (agents को चलाने वाला engine)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
The runtime is the engine that creates agent instances lazily, queues and delivers messages, and manages lifecycle. `SingleThreadedAgentRuntime` runs everything in one process on one asyncio loop. Lifecycle: register -> `start()` -> `send_message` / `publish_message` -> `stop_when_idle()` (or `stop()`) -> `close()`. Each `AgentId(type, key)` is a separate instance with its own state; `save_state()` snapshots all agents.

## 🔵 सरल परिभाषा (Hindi)
Runtime वह engine है जो agent instances आलसी तरीके से बनाता है, messages को queue करके पहुँचाता है और lifecycle सँभालता है। `SingleThreadedAgentRuntime` सब कुछ एक process में एक asyncio loop पर चलाता है। Lifecycle: register -> `start()` -> `send_message` / `publish_message` -> `stop_when_idle()` (या `stop()`) -> `close()`। हर `AgentId(type, key)` अलग instance है जिसकी अपनी state होती है; `save_state()` सभी agents का snapshot लेता है।

---

## 🔴 Problem it Solves
Services need many isolated agent instances (one per tenant or conversation), clean startup and shutdown, and a way to save state. Without a runtime you would write your own queues, instance management and shutdown logic.

## 🔴 यह क्यों बना? (Hindi)
Services को कई अलग-थलग agent instances चाहिए (हर tenant या बातचीत के लिए एक), साफ़ startup और shutdown, और state सहेजने का तरीका। Runtime के बिना आपको अपनी queues, instance management और shutdown logic लिखनी पड़ती।

---

## 🟢 How it Works

```
Step 1 -> Create SingleThreadedAgentRuntime()
Step 2 -> register(runtime, 'counter', factory): tells the runtime how to build instances
Step 3 -> start() launches the message-processing task
Step 4 -> First message to AgentId('counter','importer-a') creates that instance lazily
Step 5 -> Different key = different instance = separate state (5, 12 for A; 1 for B in our run)
Step 6 -> save_state() snapshots every agent (returns a dict)
Step 7 -> stop_when_idle() drains the queue; stop() stops now; close() releases resources
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> SingleThreadedAgentRuntime() बनाओ
Step 2 -> register(runtime, 'counter', factory): runtime को instances बनाना सिखाता है
Step 3 -> start() message-processing task शुरू करता है
Step 4 -> AgentId('counter','importer-a') को पहला message उस instance को आलसी तरीके से बनाता है
Step 5 -> अलग key = अलग instance = अलग state (हमारे run में A के लिए 5, 12; B के लिए 1)
Step 6 -> save_state() हर agent का snapshot लेता है (dict लौटाता है)
Step 7 -> stop_when_idle() queue खाली करता है; stop() तुरंत रोकता है; close() resources छोड़ता है
```

---

## 🟡 Real World Example
**Tariff Agent per importer.** `AgentId('counter','importer-a')` and `...-b` are separate instances: sending 5 then 7 to A gives 5 then 12, and 1 to B gives 1. The same idea gives one tariff agent per customer with its own history, without any global dict. In the FastAPI example a slow job is bounded inside the handler by a 1-second budget and the API answers 504.

## 🟡 Real Example Hindi mein
**हर importer के लिए Tariff Agent.** `AgentId('counter','importer-a')` और `...-b` अलग instances हैं: A को 5 फिर 7 भेजने पर 5 फिर 12, और B को 1 भेजने पर 1 मिला। यही विचार हर customer के लिए अपनी history वाला tariff agent देता है, बिना global dict के। FastAPI example में धीमा job handler के अंदर 1 सेकंड के budget से बाँधा गया और API ने 504 दिया।

---

## 💻 Code Example — Basic
Basic: lifecycle plus identity. Observed output: `5 12 1` and the saved-state keys `['counter/importer-a', 'counter/importer-b']`.

```python
# Basic: runtime lifecycle: register -> start -> send/publish -> stop_when_idle; agent identity (type, key)
import asyncio  # loop
from dataclasses import dataclass  # message
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler  # core

@dataclass  # message
class Ping:  # request
    n: int  # number

class Counter(RoutedAgent):  # agent with per-key state
    def __init__(self) -> None:  # init
        super().__init__("counter")  # description
        self.total = 0  # state lives in THIS instance (one per AgentId)

    @message_handler  # handler
    async def on_ping(self, message: Ping, ctx: MessageContext) -> int:  # handler
        self.total += message.n  # mutate state
        return self.total  # reply

async def main() -> None:  # entry
    rt = SingleThreadedAgentRuntime()  # create
    await Counter.register(rt, "counter", lambda: Counter())  # register type "counter"
    rt.start()  # begin processing
    a = AgentId("counter", "importer-a")  # instance for importer A
    b = AgentId("counter", "importer-b")  # separate instance for importer B
    print(await rt.send_message(Ping(5), a), await rt.send_message(Ping(7), a), await rt.send_message(Ping(1), b))  # 5 12 1
    state = await rt.save_state()  # snapshot every agent
    print(list(state.keys()))  # which agents exist
    await rt.stop_when_idle()  # stop after queue empties
    await rt.close()  # release resources

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: one runtime per FastAPI app (lifespan), one agent instance per tenant via `AgentId` key, the timeout enforced inside the handler. We observed that cancelling `send_message` from outside (`asyncio.wait_for` around it) logged a `task_done()` error in 0.7.5, so the timeout lives in the handler instead.

```python
# Advanced: one agent instance per tenant (AgentId key), per-request timeout, FastAPI
import asyncio  # asyncio
from contextlib import asynccontextmanager  # lifespan
from dataclasses import dataclass  # messages
from typing import AsyncIterator  # type
from fastapi import FastAPI, HTTPException  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler  # core

@dataclass  # message
class Job:  # request
    seconds: float  # how long the 'work' takes

class Worker(RoutedAgent):  # agent
    def __init__(self) -> None:  # init
        super().__init__("worker")  # desc

    @message_handler  # handler
    async def on_job(self, message: Job, ctx: MessageContext) -> str:  # handler
        try:  # bound the work INSIDE the handler (cancelling send_message from outside logged a task_done() error in 0.7.5)
            await asyncio.wait_for(asyncio.sleep(message.seconds), timeout=1.0)  # pretend LLM/tool latency, 1s budget
        except asyncio.TimeoutError:  # too slow
            return "timeout"  # signal to the caller
        return "done"  # reply

runtime = SingleThreadedAgentRuntime()  # runtime

@asynccontextmanager  # lifespan
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # signature
    await Worker.register(runtime, "worker", lambda: Worker())  # register
    runtime.start()  # start
    yield  # serve
    await runtime.stop()  # stop now (cancel pending)
    await runtime.close()  # release

app = FastAPI(lifespan=lifespan)  # app

class Req(BaseModel):  # body
    tenant: str  # tenant id = AgentId key
    seconds: float  # work time

@app.post("/job")  # endpoint
async def job(req: Req) -> dict[str, str]:  # handler
    out = await runtime.send_message(Job(req.seconds), AgentId("worker", req.tenant))  # per-tenant agent instance
    if out == "timeout":  # handler reported a timeout
        raise HTTPException(504, "job timed out")  # 504
    return {"result": out}  # response

with TestClient(app) as c:  # lifespan
    print(c.post("/job", json={"tenant": "acme", "seconds": 0.01}).json())  # fast
    print(c.post("/job", json={"tenant": "acme", "seconds": 5}).status_code)  # timeout
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline (scripted `ReplayChatCompletionClient` or no model at all, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Runtime / executor | Pregel graph executor | Crew.kickoff engine | Runner | SingleThreadedAgentRuntime (or distributed runtime) |
| Per-user instances | thread_id | New crew per user | Session per user | AgentId(type, key) per tenant |
| State save | Checkpointer | Limited | Session store | runtime.save_state() / agent save_state() |
| Lifecycle | compile / invoke | kickoff | Runner.run | register, start, stop_when_idle, close |
| Concurrency | Async graph | Async tasks | Async runs | Single asyncio loop; handlers are async |
| Distributed | LangGraph Platform | Not core | Not core | Distributed runtime available in autogen-ext (not tested here) |

---

## ⚠️ Common Mistakes
❌ Mistake: Creating a new runtime per HTTP request.
✅ Correct: Create one per app (lifespan); per-request runtimes lose state and cost startup time.

❌ Mistake: Using the same key for all users.
✅ Correct: The key is the tenant/conversation id; a shared key shares state between users.

❌ Mistake: Cancelling `send_message` from outside to implement timeouts.
✅ Correct: Bound the work inside the handler (`asyncio.wait_for`) as in the example; we saw an error logged when cancelling externally.

❌ Mistake: Not calling `close()` / `stop_when_idle()` on shutdown.
✅ Correct: Use lifespan shutdown so queues drain and resources are released.

---

## 🧠 Tricky Interview Question
Your service restarts during a deploy and every importer's in-memory agent state is lost. Fix?

Answer: Treat agent instances as caches, not the source of truth. Persist state: call `save_state()` (runtime) or each agent's `save_state()` periodically and on shutdown into a database, and `load_state()` on startup, or store per-tenant data in your DB and load it on first message. Use `stop_when_idle()` for graceful drain, version your state schema, and test restore from a snapshot. For high availability use a distributed runtime or an external queue.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is an AgentId?
A1: A (type, key) pair identifying one agent instance.

Q2: [Medium] When is an agent instance created?
A2: Lazily, when the first message is addressed to that AgentId (via the registered factory).

Q3: [Hard] stop() vs stop_when_idle()?
A3: `stop_when_idle()` waits for queued messages to finish; `stop()` stops immediately.

Q4: [Hard] How do you isolate tenants?
A4: Use a different key per tenant so each gets its own instance and state; never share keys; validate the key from your auth layer.

Q5: [System Design] Scale to 100k tenants.
A5: Agents are created lazily per key; evict idle instances after saving state; shard keys across processes with a distributed runtime; persist snapshots; monitor queue depth and handler latency.

---

## 💰 Cost Impact
The runtime has no token cost. Per-tenant instances let you keep each tenant's small state instead of re-sending a long history on every call, which can reduce input tokens. Memory cost grows with the number of live instances; evict idle ones. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Many isolated stateful agent instances.
- Services needing clean startup/shutdown.
- Snapshot/restore of agent state.

❌ Avoid when:
- A one-shot script (AgentChat team is enough).
- Cross-machine scale-out needed but you only have the single-threaded runtime.
- State must never be lost and you have no persistence.

---

## 📊 Visual Diagram
```
 FastAPI lifespan: register -> start()  ...serve...  stop_when_idle -> close()
                     |
 request(tenant) --> send_message(msg, AgentId('worker', tenant))
                     |
        +------------+-------------+
        v                          v
 [worker/acme] state A     [worker/globex] state B     (lazy instances)
        |                          |
        +---- save_state() ---> snapshot dict ---> your DB
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Runtime | Engine that delivers messages | messages पहुँचाने वाला engine |
| AgentId | Type + key identity | type + key पहचान |
| lazy instantiation | Create on first use | पहली बार इस्तेमाल पर बनाना |
| stop_when_idle | Drain then stop | queue खाली करके रोकना |
| save_state | Snapshot of agent state | agent state का snapshot |
| tenant | One customer's isolated space | एक customer की अलग जगह |
| lifespan | App startup/shutdown scope | app startup/shutdown दायरा |

---

## ⚡ 3-Line Summary
English: The runtime creates agents lazily per AgentId, delivers messages and manages lifecycle.
Same type with a different key is a different instance with separate state.
Use one runtime per app, bound work inside handlers and persist state.
Hindi: Runtime हर AgentId पर agents आलसी तरीके से बनाता है, messages पहुँचाता है और lifecycle सँभालता है।
वही type पर अलग key यानी अलग instance और अलग state।
एक app में एक runtime रखें, काम handlers के अंदर सीमित करें और state सहेजें।

---

## ➡️ Next Topic
155. SingleThreadedAgentRuntime -- the in-process runtime used here, in more detail.

---
