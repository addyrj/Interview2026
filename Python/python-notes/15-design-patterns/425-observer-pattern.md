---

# 425. Observer Pattern
# हिंदी में: Observer Pattern (एक बदलाव पर कई subscribers को खबर)

---

## 🔵 Simple Definition (English)
Observer lets one object (the subject) notify many other objects (observers) when something happens, without knowing who they are. Observers subscribe and unsubscribe at runtime. It is the basis of event systems and pub/sub.

## 🔵 सरल परिभाषा (Hindi)
Observer में एक object (subject) कुछ होने पर कई दूसरे objects (observers) को खबर देता है, बिना यह जाने कि वे कौन हैं। Observers runtime पर subscribe और unsubscribe करते हैं। Event systems और pub/sub की यही बुनियाद है।

---

## 🔴 Problem it Solves
When an order is paid, you must send a receipt, update stock, and record analytics. If `pay_order()` calls all three directly, it becomes tightly coupled: every new reaction means editing `pay_order()`, and one failing step breaks the rest. With Observer the payment code just publishes `order.paid`; reactions are added from outside.

## 🔴 यह क्यों बना? (Hindi)
Order paid होने पर receipt भेजनी है, stock update करना है और analytics लिखना है। अगर `pay_order()` तीनों को सीधे बुलाता है तो वह tightly coupled हो जाता है: हर नई reaction के लिए `pay_order()` बदलना पड़ता है, और एक step fail हो तो बाकी रुक जाते हैं। Observer में payment code सिर्फ `order.paid` publish करता है; reactions बाहर से जुड़ती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Subject keeps a list of subscriber callbacks per topic
Step 2 → Observers call subscribe(topic, handler) and get an unsubscribe function
Step 3 → Something happens: subject calls publish(topic, payload)
Step 4 → Subject loops over a COPY of the handler list
Step 5 → Each handler runs inside try/except so one failure does not stop others
Step 6 → Observers can unsubscribe any time
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Subject हर topic के लिए subscriber callbacks की list रखता है
Step 2 → Observers subscribe(topic, handler) बुलाते हैं और unsubscribe function पाते हैं
Step 3 → कुछ होता है: subject publish(topic, payload) बुलाता है
Step 4 → Subject handlers की list की COPY पर loop चलाता है
Step 5 → हर handler try/except में चलता है ताकि एक की failure बाकी को न रोके
Step 6 → Observers कभी भी unsubscribe कर सकते हैं
```

---

## 🟡 Real World Example
Razorpay-style webhooks, Django signals (`post_save`), Node's `EventEmitter`, and UI frameworks all use Observer. In an e-commerce backend, `order.paid` triggers the receipt mailer, inventory updater, loyalty-points service and analytics, each registered separately. A stock-price feed notifies dashboards the same way.

## 🟡 Real Example Hindi mein
Razorpay जैसे webhooks, Django signals (`post_save`), Node का `EventEmitter` और UI frameworks सब Observer इस्तेमाल करते हैं। E-commerce backend में `order.paid` से receipt mailer, inventory updater, loyalty-points service और analytics चलते हैं, हर एक अलग से registered। Stock-price feed भी dashboards को इसी तरह खबर देता है।

---

## 💻 Code Example — Basic
```python
# Basic Observer: subject notifies all subscribed observers
from typing import Callable                   # type for callbacks


class Subject:
    def __init__(self) -> None:
        self._observers: list[Callable[[str], None]] = []   # subscriber list

    def subscribe(self, fn: Callable[[str], None]) -> None:
        self._observers.append(fn)            # add subscriber

    def notify(self, msg: str) -> None:
        for fn in self._observers:            # call each subscriber
            fn(msg)


def email(msg: str) -> None:
    print("email:", msg)                      # observer 1


def sms(msg: str) -> None:
    print("sms:", msg)                        # observer 2


s: Subject = Subject()
s.subscribe(email)
s.subscribe(sms)
s.notify("order shipped")                     # both get it

# Output:
# email: order shipped
# sms: order shipped
```

## 💻 Code Example — Advanced
```python
# Production style: typed event bus, unsubscribe, one bad handler cannot break others
import logging                                # report handler failures
from collections import defaultdict           # topic -> handlers
from typing import Any, Callable              # types

logging.basicConfig(level=logging.ERROR, format="%(levelname)s %(message)s")
Handler = Callable[[dict[str, Any]], None]    # handler signature


class EventBus:
    def __init__(self) -> None:
        self._subs: defaultdict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, topic: str, fn: Handler) -> Callable[[], None]:
        self._subs[topic].append(fn)          # register
        return lambda: self._subs[topic].remove(fn)   # returns an unsubscribe function

    def publish(self, topic: str, payload: dict[str, Any]) -> int:
        delivered: int = 0                    # successful deliveries
        for fn in list(self._subs[topic]):    # copy: handlers may unsubscribe during loop
            try:
                fn(payload)
                delivered += 1
            except Exception:                 # isolate failures
                logging.exception("handler %s failed", fn.__name__)
        return delivered


def send_receipt(p: dict[str, Any]) -> None:
    print("receipt for", p["order_id"])


def update_stock(p: dict[str, Any]) -> None:
    raise RuntimeError("stock db down")       # simulated failure


def analytics(p: dict[str, Any]) -> None:
    print("analytics:", p["amount"])


bus: EventBus = EventBus()
bus.subscribe("order.paid", send_receipt)
bus.subscribe("order.paid", update_stock)
unsub = bus.subscribe("order.paid", analytics)
print("delivered:", bus.publish("order.paid", {"order_id": 7, "amount": 499}))
unsub()                                       # analytics leaves
print("delivered:", bus.publish("order.paid", {"order_id": 8, "amount": 99}))

# Output:
# receipt for 7
# analytics: 499
# delivered: 2
# receipt for 8
# delivered: 1
```

Note: the `ERROR handler update_stock failed` log plus a traceback goes to stderr (not stdout); only the prints are shown above. Handler order is the subscription order.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Built-in emitter | none in stdlib (write one, or use `blinker`) | `EventEmitter` (Node), `addEventListener` (browser) |
| Subscribe | `bus.subscribe(topic, fn)` | `emitter.on(topic, fn)` |
| Unsubscribe | returned function / `remove` | `emitter.off(topic, fn)` |
| Async handlers | `await` inside async handlers | promises / async functions |

```python
# Python way
unsub = bus.subscribe("order.paid", send_receipt)   # returns an unsubscribe function
bus.publish("order.paid", {"order_id": 7})          # all handlers run
unsub()                                             # leave
```
```javascript
// JavaScript way
const emitter = new EventEmitter();
emitter.on("order.paid", sendReceipt);              // subscribe
emitter.emit("order.paid", { orderId: 7 });         // publish
emitter.off("order.paid", sendReceipt);             // unsubscribe
```

Key difference: Node.js ships `EventEmitter` and browsers have `addEventListener`, so JS developers use Observer daily. Python has no built-in event emitter; you write a tiny bus (as above) or use `blinker` (used by Flask signals). Note that Node's emitter propagates a handler exception to the emitter, so isolate handlers yourself in both languages.

---

## 🟠 FastAPI Connection
In FastAPI the lightest observer is `BackgroundTasks`: after the response is sent, each observer function runs. For cross-service reactions use a real broker (Redis pub/sub, Kafka, RabbitMQ). Do not run slow observers inside the request path.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from fastapi import FastAPI, BackgroundTasks
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()
log: list[str] = []
handlers = []                                 # observers


def on_signup_email(email: str) -> None: log.append(f"welcome mail to {email}")
def on_signup_crm(email: str) -> None: log.append(f"crm lead {email}")
handlers += [on_signup_email, on_signup_crm]


@app.post("/signup")
def signup(email: str, bg: BackgroundTasks) -> dict[str, str]:
    for h in handlers:                        # notify observers after response is sent
        bg.add_task(h, email)
    return {"status": "created"}


print(TestClient(app).post("/signup", params={"email": "a@x.com"}).json())
print(log)

# Output:
# {'status': 'created'}
# ['welcome mail to a@x.com', 'crm lead a@x.com']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Modifying the observer list while looping over it
✅ Correct: loop over a copy

```python
subs = [a, b, c]
# Wrong: for f in subs: f()   # if f removes itself, the next observer is skipped
# Right:
for f in list(subs):           # copy: safe against unsubscribe during notify
    f()
```

❌ Mistake 2: One failing observer breaks everyone after it
✅ Correct: catch and log per handler

```python
# Wrong
for fn in handlers: fn(payload)            # first exception stops the loop
# Right
for fn in handlers:
    try:
        fn(payload)
    except Exception:
        logging.exception("handler failed")   # others still run
```

❌ Mistake 3: Never unsubscribing (memory leak)
✅ Correct: keep the unsubscribe function and call it on shutdown

```python
# Wrong: bus.subscribe("x", obj.method) forever -> the bus keeps obj alive
# Right: unsub = bus.subscribe("x", obj.method); ...; unsub()
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
subs = []
def a(): print("a"); subs.remove(a)           # unsubscribes itself
def b(): print("b")
def c(): print("c")
subs += [a, b, c]
for f in subs: f()
print(len(subs))
```
Answer: Output: `a`, `c`, `2`. Handler `a` removes itself from the list while the `for` loop is iterating it. The list shifts left, the iterator's index moves to position 1 which is now `c`, so `b` is silently skipped. Looping over `list(subs)` fixes it.

---

## ⚫ Interview Questions + Answers

Q1: What problem does Observer solve?
A1: It decouples the code that produces an event from the code that reacts to it. New reactions are added without changing the producer.

Q2: Observer vs Pub/Sub?
A2: Observer: subject holds the observers directly (same process). Pub/Sub: a broker sits between publishers and subscribers using topics, often across processes (Redis, Kafka).

Q3: What happens if a handler raises?
A3: In a naive loop the remaining handlers never run. Production buses wrap each call in try/except, log, and optionally retry or send to a dead-letter queue.

Q4: How do you avoid memory leaks?
A4: A bus that stores bound methods keeps those objects alive. Return an unsubscribe function, or store `weakref.WeakMethod` references.

Q5: Are observers called synchronously?
A5: In the simple version yes, so a slow observer slows the publisher. Use async handlers, threads, `BackgroundTasks` or a queue for slow work.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One event must trigger several independent reactions
- Producer must not know its consumers
- Plugin or hook style extension points

❌ Avoid when:
- Strict order or transaction guarantees across handlers are needed
- Handlers are slow and the publisher must stay fast: use a queue
- Only one fixed consumer: call it directly

---

## 📊 Visual Diagram
```
publish("order.paid")
        |
   +----v-----+---> send_receipt()   ok
   |   Bus    |---> update_stock()    FAILS -> logged, loop continues
   +----------+---> analytics()       ok

unsubscribe() removes a handler from the topic list
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Subject | Object that announces events | Events की घोषणा करने वाला object |
| Observer | Object that reacts to events | Events पर प्रतिक्रिया देने वाला object |
| Topic | Name of an event channel | Event channel का नाम |
| Pub/Sub | Observer through a broker | Broker के जरिए Observer |
| Dead letter | Event that failed too many times | बहुत बार fail हुआ event |

---

## ⚡ 3-Line Summary
English: Observer lets a subject notify many subscribers without knowing them. Loop over a copy, isolate failures, and keep unsubscribe handles. For slow or cross-service work use a queue or broker instead of in-process calls.
Hindi: Observer में subject कई subscribers को बिना जाने खबर देता है। Copy पर loop चलाएं, failures को अलग रखें और unsubscribe handles संभालें। धीमे या cross-service काम के लिए in-process calls की जगह queue या broker इस्तेमाल करें।

---

## ➡️ Next Topic
**426. Strategy Pattern** — swap an algorithm at runtime behind a common interface.
