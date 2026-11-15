---

# 433. Event-Driven in Python
# हिंदी में: Event-Driven in Python (Events से चलने वाला design)

---

## 🔵 Simple Definition (English)
In an event-driven design, parts of the system communicate by emitting events (facts like `user.created`) and reacting to them, instead of calling each other directly. Producers and consumers do not know each other, and work can happen asynchronously.

## 🔵 सरल परिभाषा (Hindi)
Event-driven design में system के हिस्से एक-दूसरे को सीधे बुलाने की जगह events (तथ्य, जैसे `user.created`) emit और उन पर react करके बात करते हैं। Producers और consumers एक-दूसरे को नहीं जानते, और काम asynchronously हो सकता है।

---

## 🔴 Problem it Solves
If signup directly calls email, CRM, analytics, and fraud services one after another, the user waits for all of them, any slow service slows signup, and any failure breaks signup. Adding a new reaction means editing signup code. Events let signup finish fast, and every reaction runs independently with its own retries.

## 🔴 यह क्यों बना? (Hindi)
अगर signup सीधे email, CRM, analytics और fraud services को एक के बाद एक बुलाता है तो user सबके खत्म होने का इंतजार करता है, कोई भी धीमी service signup धीमा करती है और कोई भी failure signup तोड़ देती है। नई reaction जोड़ने के लिए signup code बदलना पड़ता है। Events से signup जल्दी खत्म होता है और हर reaction अपने retries के साथ स्वतंत्र चलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Something happens: the producer builds an Event (name + data)
Step 2 → Producer publishes it to a bus or queue and returns immediately
Step 3 → A worker takes events off the queue (asyncio.Queue, Redis, Kafka)
Step 4 → Worker runs every handler registered for that event name
Step 5 → If a handler fails: retry up to N times
Step 6 → After N failures: move the event to a dead-letter list for humans
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → कुछ होता है: producer Event (नाम + data) बनाता है
Step 2 → Producer उसे bus या queue में publish करके तुरंत लौट जाता है
Step 3 → Worker queue से events निकालता है (asyncio.Queue, Redis, Kafka)
Step 4 → Worker उस event के लिए registered हर handler चलाता है
Step 5 → Handler fail हो तो N बार तक retry
Step 6 → N failures के बाद event dead-letter list में जाता है ताकि इंसान देखें
```

---

## 🟡 Real World Example
Swiggy/Zomato order flow: `order.placed` triggers restaurant notification, payment capture, rider assignment, and analytics, each by a separate consumer. Razorpay webhooks, Stripe events, Kafka pipelines, and AWS SNS/SQS all work like this. In Python the same idea scales from `asyncio.Queue` to Celery to Kafka.

## 🟡 Real Example Hindi mein
Swiggy/Zomato order flow: `order.placed` से restaurant notification, payment capture, rider assignment और analytics शुरू होते हैं, हर एक अलग consumer से। Razorpay webhooks, Stripe events, Kafka pipelines और AWS SNS/SQS सब इसी तरह काम करते हैं। Python में यही सोच `asyncio.Queue` से Celery और Kafka तक फैलती है।

---

## 💻 Code Example — Basic
```python
# Basic Event-Driven: producers emit events, consumers react; neither knows the other
from collections import defaultdict           # topic -> handlers
from typing import Callable

handlers: defaultdict[str, list[Callable[[dict], None]]] = defaultdict(list)


def on(event: str, fn: Callable[[dict], None]) -> None:
    handlers[event].append(fn)                # subscribe


def emit(event: str, data: dict) -> None:
    for fn in handlers[event]:                # deliver
        fn(data)


on("user.created", lambda d: print("welcome mail ->", d["email"]))
on("user.created", lambda d: print("crm lead   ->", d["email"]))
emit("user.created", {"email": "a@x.com"})

# Output:
# welcome mail -> a@x.com
# crm lead   -> a@x.com
```

## 💻 Code Example — Advanced
```python
# Production style: async event queue with workers, retries and a dead-letter list
import asyncio                                # async runtime
from dataclasses import dataclass             # event type
from typing import Awaitable, Callable


@dataclass
class Event:
    name: str
    data: dict[str, int]
    attempts: int = 0


Handler = Callable[[Event], Awaitable[None]]


class AsyncBus:
    def __init__(self, max_attempts: int = 3) -> None:
        self.q: asyncio.Queue[Event] = asyncio.Queue()
        self.handlers: dict[str, list[Handler]] = {}
        self.dead: list[Event] = []               # dead letters (failed too many times)
        self.max_attempts = max_attempts

    def on(self, name: str, fn: Handler) -> None:
        self.handlers.setdefault(name, []).append(fn)

    async def publish(self, e: Event) -> None:
        await self.q.put(e)                   # producer returns immediately

    async def worker(self) -> None:
        while True:
            e = await self.q.get()
            try:
                for fn in self.handlers.get(e.name, []):
                    await fn(e)
            except Exception as ex:
                e.attempts += 1
                if e.attempts >= self.max_attempts:
                    self.dead.append(e)       # give up: dead letter
                    print(f"dead-lettered {e.name} after {e.attempts} tries: {ex}")
                else:
                    await self.q.put(e)       # retry later
            finally:
                self.q.task_done()


async def main() -> None:
    bus = AsyncBus()
    state = {"fails": 0}

    async def send_mail(e: Event) -> None:
        print("mail for order", e.data["id"])

    async def flaky_stock(e: Event) -> None:
        state["fails"] += 1
        if e.data["id"] == 2:
            raise RuntimeError("stock service down")   # id 2 always fails
        print("stock updated for", e.data["id"])

    bus.on("order.paid", send_mail)
    bus.on("order.paid", flaky_stock)
    w = asyncio.create_task(bus.worker())     # start consumer
    await bus.publish(Event("order.paid", {"id": 1}))
    await bus.publish(Event("order.paid", {"id": 2}))
    await bus.q.join()                        # wait until all processed
    w.cancel()                                # stop worker
    print("dead letters:", [d.data for d in bus.dead])


asyncio.run(main())

# Output:
# mail for order 1
# stock updated for 1
# mail for order 2
# mail for order 2
# mail for order 2
# dead-lettered order.paid after 3 tries: stock service down
# dead letters: [{'id': 2}]
```

Note: order 2's mail printed three times because the whole event was retried when `flaky_stock` failed. This is why handlers must be idempotent (safe to run again) or tracked per handler.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| In-process events | custom bus, `blinker` | `EventEmitter` (built-in) |
| Async queue | `asyncio.Queue` | promises, `async` iterators |
| Background jobs | Celery, RQ, arq | BullMQ, Agenda |
| Brokers | Kafka, RabbitMQ, Redis Streams | same |

```python
# Python way
await bus.publish(Event("order.paid", {"id": 1}))   # returns immediately
# a worker task consumes the queue and calls the handlers
```
```javascript
// JavaScript way
emitter.emit("order.paid", { id: 1 });              // Node: synchronous by default
// BullMQ: await queue.add("order.paid", { id: 1 }) // durable background job
```

Key difference: Node's `EventEmitter` is built in and synchronous; JavaScript is event-loop based by nature, so async feels default. Python needs `asyncio` (or threads/processes) explicitly, and an `asyncio.Queue` lives only inside one process: it is lost if the process dies. For durability use a broker.

---

## 🟠 FastAPI Connection
FastAPI can host a small event-driven loop: start a consumer task in `lifespan`, let routes `await queue.put(event)` and return quickly. For durability and multiple workers use Redis Streams, RabbitMQ, Kafka, or Celery. Webhook endpoints (Razorpay, Stripe) are event producers calling your API.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient

q: asyncio.Queue[str] = asyncio.Queue()
done: list[str] = []


async def consumer() -> None:
    while True:
        done.append(await q.get())            # background consumer inside the app


@asynccontextmanager
async def lifespan(app: FastAPI):
    t = asyncio.create_task(consumer())       # start on startup
    yield
    t.cancel()                                # stop on shutdown


app: FastAPI = FastAPI(lifespan=lifespan)


@app.post("/events")
async def publish(name: str) -> dict[str, str]:
    await q.put(name)
    return {"queued": name}


with TestClient(app) as c:                    # 'with' runs lifespan
    print(c.post("/events", params={"name": "user.created"}).json())
    import time; time.sleep(0.1)
print(done)

# Output:
# {'queued': 'user.created'}
# ['user.created']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One failing handler stops later handlers
✅ Correct: isolate failures per handler

```python
# Wrong
for h in handlers: h(data)              # ZeroDivisionError in handler 2 -> handler 3 never runs
# Right
for h in handlers:
    try:
        h(data)
    except Exception:
        logging.exception("handler failed")
```

❌ Mistake 2: Non-idempotent handlers with retries
✅ Correct: make handlers safe to run twice (use an event id / dedupe key)

```python
# Wrong: send_receipt(order)                       # retry -> customer gets 3 emails
# Right: if not already_sent(event.id): send_receipt(order); mark_sent(event.id)
```

❌ Mistake 3: Trusting an in-memory queue for important events
✅ Correct: use a durable broker for events that must not be lost

```python
# Wrong: asyncio.Queue for payments   # process crash = events gone
# Right: Redis Streams / RabbitMQ / Kafka / a DB outbox table
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
handlers = [lambda d: print("mail"), lambda d: 1 / 0, lambda d: print("crm")]
try:
    for h in handlers: h({})
except ZeroDivisionError as e:
    print("stopped:", e)
```
Answer: Output: `mail`, then `stopped: division by zero`. The second handler raises, the exception leaves the `for` loop, and the third handler (`crm`) never runs. In an event-driven system each handler must be isolated with try/except (or run as its own task) so one bad consumer cannot block the others.

---

## ⚫ Interview Questions + Answers

Q1: What is event-driven architecture?
A1: Components communicate through events (immutable facts that something happened) rather than direct calls. Producers do not know consumers, which gives loose coupling and independent scaling.

Q2: Event vs Command?
A2: A command is a request ('PlaceOrder') sent to one handler and may be rejected. An event is a fact in the past ('OrderPlaced') that any number of consumers may react to.

Q3: What does idempotent mean here?
A3: Processing the same event twice has the same effect as processing it once. Needed because brokers deliver at-least-once and retries duplicate work.

Q4: What is a dead-letter queue?
A4: A holding place for events that failed after the maximum retries, kept for inspection and manual or automatic replay instead of blocking the main queue.

Q5: Which Python tools exist?
A5: `asyncio.Queue` (in-process), Celery/RQ/arq (background jobs), `aiokafka`/`confluent-kafka`, `aio-pika` (RabbitMQ), Redis Streams, and `blinker` for simple in-process signals.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One action triggers several independent reactions
- Slow work (email, reports) must not block the request
- Services should be loosely coupled and scaled separately

❌ Avoid when:
- You need an immediate answer and strict ordering/consistency: use a direct call
- Small app: events add moving parts you must monitor
- You cannot make handlers idempotent

---

## 📊 Visual Diagram
```
producer --publish--> [ queue ] --> worker --> handler A (mail)
 (returns fast)                          |-> handler B (stock)  fails
                                         |      retry 1,2,3
                                         v
                                   dead letters (inspect/replay)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | Fact that something happened | कुछ हुआ उसका तथ्य |
| Producer / Consumer | Sender / receiver of events | Events भेजने / पाने वाला |
| Broker | Middleman storing and routing events | Events रखने और भेजने वाला बिचौलिया |
| Idempotent | Safe to repeat | दोहराना सुरक्षित |
| Dead-letter queue | Failed events parking area | Failed events का parking |

---

## ⚡ 3-Line Summary
English: Event-driven design lets producers publish facts and independent consumers react through a queue or broker, with retries and dead letters for failures. It decouples services and speeds up requests but demands idempotent handlers and durable queues for important data.
Hindi: Event-driven design में producers तथ्य publish करते हैं और स्वतंत्र consumers queue या broker के जरिए react करते हैं, failures के लिए retries और dead letters के साथ। यह services को अलग करता है और requests तेज करता है, पर idempotent handlers और जरूरी data के लिए durable queues मांगता है।

---

## ➡️ Next Topic
**434. Clean Architecture Python** — layers (entities, use cases, adapters) that keep business rules independent of frameworks.
