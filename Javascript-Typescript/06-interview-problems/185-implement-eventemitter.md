# 185. Implement EventEmitter
# हिंदी में: EventEmitter बनाना — on, once, off और emit वाला Publish-Subscribe सिस्टम

---

## 🔵 Simple Definition (English)
An EventEmitter lets code register functions (listeners) for a named event and runs all of them when that event fires. Node.js ships it as `require("events")`, and streams, HTTP servers, and `process` are built on it.

## 🔵 सरल परिभाषा (Hindi)
EventEmitter वह object है जिसमें किसी event के नाम पर functions (listeners) रजिस्टर होते हैं, और event होने पर सभी को चलाया जाता है। Node.js में यह `require("events")` से मिलता है, और streams, HTTP servers व `process` इसी पर बने हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Build a class with `on(event, listener)`, `once(event, listener)`, `off(event, listener)`, and `emit(event, ...args)`. `emit` returns `true` if at least one listener ran and `false` otherwise. An unhandled `"error"` event must throw.

Without an emitter, the payment code must know about the email sender, the kitchen screen, and the analytics code, and call each one directly. That is tight coupling. With an emitter, the payment code only says "order paid", and anyone who cares reacts.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** एक class बनाओ जिसमें `on(event, listener)`, `once(event, listener)`, `off(event, listener)` और `emit(event, ...args)` हों। `emit` `true` लौटाए अगर कम से कम एक listener चला, वरना `false`। बिना handler वाला `"error"` event throw करे।

Emitter के बिना payment code को email sender, kitchen screen और analytics, सबके बारे में पता होना चाहिए और हर एक को सीधे call करना पड़ता है। यह tight coupling है। Emitter से payment code बस "order paid" बोलता है, और जिसे फ़र्क पड़ता है वह react करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Keep a `Map` from event name to an array of listener functions.
Step 2 → `on` pushes a listener onto the array for that event.
Step 3 → `once` wraps the listener so the wrapper removes itself on its first run.
Step 4 → `off` finds the listener (or its `once` wrapper) and removes it.
Step 5 → `emit` copies the array, calls every listener with the arguments, and returns `true` or `false`.
Step 6 → For an unhandled `"error"` event, `emit` throws instead of failing silently.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Event के नाम से listener arrays तक जाने के लिए एक `Map` रखो।
Step 2 → `on` उस event के array में listener जोड़ता है।
Step 3 → `once` listener को wrapper में लपेटता है, जो पहली बार चलने पर खुद को हटा देता है।
Step 4 → `off` listener (या उसके `once` wrapper) को ढूँढकर हटाता है।
Step 5 → `emit` array की copy लेता है, हर listener को arguments देकर चलाता है, और `true` या `false` लौटाता है।
Step 6 → Handler न होने पर `"error"` event throw करता है, चुपचाप नहीं जाता।

---

## 🟡 Real World Example
Swiggy's order service emits `order.placed`. The kitchen display, billing, and the SMS sender each subscribe on their own. The order code does not know they exist, so adding a loyalty-points subscriber later needs no change to the order code.

Scenario: A customer orders "Paneer Tikka". Three listeners run for `order.placed`: the kitchen screen shows the ticket, billing prints the bill, and the SMS sender texts the customer.

## 🟡 Real Example Hindi mein
Swiggy का order service `order.placed` emit करता है। Kitchen display, billing और SMS sender अपने-अपने listener से उसे सुनते हैं। Order code को इनके बारे में पता नहीं, इसलिए बाद में loyalty points subscriber जोड़ने पर order code नहीं बदलता।

उदाहरण: Customer "Paneer Tikka" order करता है। `order.placed` के लिए तीन listeners चलते हैं: kitchen screen पर ticket आती है, billing bill छापती है, और SMS sender customer को message भेजता है।

---

## 💻 Code Example — Basic
```javascript
// Basic: store listeners in a plain object and call all of them on emit
class MiniEmitter {
  constructor() {
    this.events = {};                              // event name -> array of listener functions
  }
  on(name, fn) {
    (this.events[name] ||= []).push(fn);           // create the array if missing, then add the listener
    return this;                                   // return this so calls can be chained
  }
  emit(name, ...args) {
    (this.events[name] || []).forEach((fn) => fn(...args)); // call each listener with the arguments
  }
}

const shop = new MiniEmitter();                    // create an emitter for the restaurant
shop.on("order", (item) => console.log("Kitchen got:", item));  // listener 1
shop.on("order", (item) => console.log("Billing got:", item));   // listener 2
shop.emit("order", "Paneer Tikka");                // notify every listener of "order"
// Expected output: Kitchen got: Paneer Tikka
// Expected output: Billing got: Paneer Tikka
```

## 💻 Code Example — Advanced
```javascript
// Advanced: an EventEmitter with on, once, off, emit, listenerCount, removeAllListeners
class EventEmitter {
  constructor() {
    this._events = new Map();                      // Map: event name -> array of listeners (keeps insertion order)
  }

  on(eventName, listener) {
    if (typeof listener !== "function") {          // guard: a listener must be a function
      throw new TypeError("listener must be a function");
    }
    if (!this._events.has(eventName)) {            // first listener for this event?
      this._events.set(eventName, []);             // create an empty list for it
    }
    this._events.get(eventName).push(listener);    // add the listener at the end of the list
    return this;                                   // chaining: bus.on(...).on(...)
  }

  once(eventName, listener) {
    const wrapper = (...args) => {                 // the function that actually gets registered
      this.off(eventName, wrapper);                // remove itself first, so it never runs twice
      listener.apply(this, args);                  // then call the real listener with the same this and args
    };
    wrapper.listener = listener;                   // remember the original so off(original) can find the wrapper
    return this.on(eventName, wrapper);            // register the wrapper as a normal listener
  }

  off(eventName, listener) {
    const list = this._events.get(eventName);      // listeners registered for this event
    if (!list) return this;                        // unknown event: nothing to remove
    const index = list.findIndex(                  // find the original or its once wrapper
      (fn) => fn === listener || fn.listener === listener
    );
    if (index !== -1) list.splice(index, 1);       // remove exactly one match
    if (list.length === 0) this._events.delete(eventName); // delete empty lists
    return this;                                   // chaining
  }

  emit(eventName, ...args) {
    const list = this._events.get(eventName);      // listeners for this event
    if (!list || list.length === 0) {              // nobody is listening
      if (eventName === "error") {                 // Node rule: an unhandled "error" must not vanish
        throw args[0] instanceof Error ? args[0] : new Error("Unhandled error event");
      }
      return false;                                // no listeners: report false
    }
    for (const fn of [...list]) {                  // loop over a copy, so off() inside a listener is safe
      fn.apply(this, args);                        // call the listener with this and the arguments
    }
    return true;                                   // at least one listener ran
  }

  listenerCount(eventName) {
    return (this._events.get(eventName) || []).length; // 0 when the event is unknown
  }

  removeAllListeners(eventName) {
    if (eventName === undefined) this._events.clear(); // no name: remove every event
    else this._events.delete(eventName);           // name given: remove only that event
    return this;                                   // chaining
  }
}

// ---- Tests: run with plain node ----
const bus = new EventEmitter();                    // create the bus
bus.on("pay", (amt) => console.log("email receipt for", amt)); // permanent listener
bus.once("pay", (amt) => console.log("first payment bonus", amt)); // runs only once
// Expected output: email receipt for 500
// Expected output: first payment bonus 500
// Expected output: true
console.log(bus.emit("pay", 500));                 // first emit: both listeners run, then true
// Expected output: email receipt for 700
// Expected output: true
console.log(bus.emit("pay", 700));                 // second emit: the once listener is gone
// Expected output: 1
console.log(bus.listenerCount("pay"));             // only the permanent listener is left
// Expected output: false
console.log(bus.emit("refund", 10));               // no listeners for "refund" -> false
try {
  bus.emit("error", new Error("card declined")); // no handler for "error": must throw
} catch (err) {
  console.log("caught:", err.message);             // Expected output: caught: card declined
}

// Time:  emit is O(k), k = listeners on that event; on and off are O(k) because of findIndex/splice
// Space: O(total listeners) for the Map and the arrays
```

### Edge Cases
```javascript
// Node's built-in emitter follows the same rules, so these edge checks use it directly
const { EventEmitter: NodeEmitter } = require("events"); // built-in class, runs with no setup

// Edge 1: the same listener added twice runs twice
const twice = new NodeEmitter();                   // new emitter
const hello = () => console.log("hi");             // one listener function
twice.on("greet", hello).on("greet", hello);       // register it two times
twice.emit("greet");                               // two calls happen
// Expected output: hi
// Expected output: hi

// Edge 2: removing a listener during emit does not skip the next one
const safe = new NodeEmitter();                    // new emitter
const first = () => { console.log("first"); safe.off("go", first); }; // removes itself
safe.on("go", first);                              // register first
safe.on("go", () => console.log("second"));        // register second
safe.emit("go");                                   // emit runs on a copy of the list
// Expected output: first
// Expected output: second

// Edge 3: off() on an unknown event is a safe no-op
console.log(new NodeEmitter().off("nothing", () => {}).eventNames().length); // Expected output: 0
```

---

## 🟠 Express.js Integration
Express builds on Node's streams and HTTP server, which are EventEmitters. A common real use is `res.on("finish", ...)` for request timing logs. An app-level bus also lets route handlers publish domain events without knowing who listens.

```javascript
// Express.js: publish order events on a bus, and log each response when it finishes
const express = require("express");               // import Express
const { EventEmitter } = require("events");       // Node's built-in emitter
const app = express();                            // create the app
app.use(express.json());                          // parse JSON request bodies

const bus = new EventEmitter();                   // one shared event bus for the app
bus.on("order.placed", (o) => console.log("Kitchen ticket:", o.item)); // kitchen subscriber
bus.on("order.placed", (o) => console.log("Billing amount:", o.amount)); // billing subscriber

// Logging middleware: res is an EventEmitter, so listen to its "finish" event
app.use((req, res, next) => {
  const started = Date.now();                     // record the start time
  res.on("finish", () => {                        // fires after the response is fully sent
    console.log(req.method, req.url, res.statusCode, Date.now() - started, "ms");
  });
  next();                                         // continue to the route
});

// POST /api/orders: validate, publish the event, and reply
app.post("/api/orders", (req, res) => {
  const { item, amount } = req.body || {};        // read the order from the body
  if (!item || typeof amount !== "number") {      // validate the input
    return res.status(400).json({ error: "item and numeric amount are required" }); // 400 Bad Request
  }
  const order = { id: Date.now(), item, amount }; // build the order object
  bus.emit("order.placed", order);                // notify every subscriber
  res.status(201).json(order);                    // 201 Created with the order
});

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Order API running");               // ready message
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling `off` with the original function after registering it with `once` through a plain wrapper
✅ **Correct:** Keep the original on the wrapper (`wrapper.listener`) so `off` can match it

```javascript
// Wrong: off() compares with the original, but the list holds only the wrapper, so nothing is removed
const naive = {
  list: [],                                        // registered functions
  once(fn) {
    const wrapper = (...a) => { this.list.splice(this.list.indexOf(wrapper), 1); fn(...a); };
    this.list.push(wrapper);                       // store only the wrapper
  },
  off(fn) { this.list = this.list.filter((f) => f !== fn); }, // compares with the original
};
const hello = () => console.log("hello");          // one function reference
naive.once(hello);                                 // register it as once
naive.off(hello);                                  // off with the original: no match
console.log(naive.list.length);                    // Expected output: 1 (still registered, bug)

// Right: the built-in emitter matches the original through its once wrapper
const { EventEmitter: NodeEmitter } = require("events"); // built-in class, imported here so the block runs alone
const fixed = new NodeEmitter();                   // built-in emitter
fixed.once("x", hello);                            // register once
fixed.off("x", hello);                             // off() finds the wrapped original
console.log(fixed.listenerCount("x"));             // Expected output: 0
```

❌ **Mistake 2:** Looping over the live listener array while listeners remove themselves
✅ **Correct:** Loop over a copy so every listener still runs

```javascript
// Wrong: A removes itself, so B shifts into index 0 and the index loop skips it
const live = [];                                   // live listener array
const A = () => { console.log("A"); live.splice(live.indexOf(A), 1); }; // removes itself
const B = () => console.log("B");                  // should also run
live.push(A, B);                                   // register both
for (let i = 0; i < live.length; i++) live[i]();   // index loop over the changing array
// Expected output: A

// Right: iterate over a copy
const copy = [];                                   // another listener array
const A2 = () => { console.log("A"); copy.splice(copy.indexOf(A2), 1); }; // removes itself
const B2 = () => console.log("B");                 // B
copy.push(A2, B2);                                 // register both
for (const fn of [...copy]) fn();                  // copy first, so nothing is skipped
// Expected output: A
// Expected output: B
```

---

## 🧠 Tricky Interview Question
```javascript
const { EventEmitter: E } = require("events");     // built-in emitter
const e = new E();                                 // new emitter
e.once("tick", () => console.log("once"));         // runs one time only
e.on("tick", () => console.log("always"));         // runs every time
console.log(e.emit("tick"));                       // ?
console.log(e.emit("tick"));                       // ?
console.log(e.listenerCount("tick"));              // ?
```
Answer: `once`, `always`, `true`, `always`, `true`, `1`.
The first `emit` runs both listeners, and the `once` wrapper removes itself before calling the real function. The second `emit` runs only the `always` listener. Both `emit` calls return `true` because at least one listener ran. After the first emit, only one listener is left, so `listenerCount` is `1`.

---

## ⚫ Interview Questions + Answers

**Q1: What data structure stores the listeners?**
A1: A `Map` from event name to an array of functions. The Map gives fast lookup by name, and the array keeps insertion order.

**Q2: How does `once` remove itself?**
A2: It registers a wrapper. The wrapper calls `off` on itself first, then calls the real listener. It keeps a reference to the original, so `off(original)` also works.

**Q3: Why copy the array before looping in `emit`?**
A3: A listener may call `off` or `once` during the loop. Iterating a copy means no listener is skipped because of a removal.

**Q4: What does `emit` return?**
A4: `true` if at least one listener ran, otherwise `false`, so the caller can tell whether anyone handled the event.

**Q5: Why does an unhandled `"error"` event throw?**
A5: Errors must not disappear quietly. Node throws so a failed stream or failed payment is visible instead of hidden.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several parts of the app must react to one event (order placed, user logged in, file uploaded)
- You want producers and consumers decoupled
- You need streams or jobs that report progress over time

❌ Avoid when:
- A plain function call is enough; events hide control flow and make debugging harder
- You need delivery guarantees across machines; use a queue such as RabbitMQ, Kafka, or SQS
- Listeners are added in a loop without `off`; this leaks memory and triggers Node's "possible EventEmitter memory leak" warning

---

## 📊 Visual Diagram
```
  order service
       |
  emit("order.placed", order)
       |
       v
  _events Map:
    "order.placed" -> [ kitchenListener,  --> kitchen screen
                        billingListener,  --> billing table
                        smsWrapper(once)  --> one SMS, then removed ]
       |
  returns true (3 listeners ran)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | A named signal such as `order.placed` | एक नाम वाला संकेत |
| Listener | A function registered for an event | किसी event के लिए रजिस्टर function |
| Emit | Fire an event and call its listeners | Event चलाना और listeners को call करना |
| Once | A listener that runs one time and removes itself | एक बार चलकर हट जाने वाला listener |
| Decoupling | Producers do not need to know consumers | Producer को consumer के बारे में न जानना |
| Wrapper | A function that wraps another to add behaviour | Behaviour जोड़ने वाला लिफ़ाफ़ा function |

---

## ⚡ 3-Line Summary
English:
1. An EventEmitter maps event names to lists of listener functions, and `emit` calls them all.
2. `on` adds, `once` adds and auto-removes, `off` removes, and `emit` returns `true` or `false`.
3. Loop over a copy of the list, and throw for unhandled `"error"` events.

Hindi:
1. EventEmitter event नाम को listener functions की list से जोड़ता है, और `emit` सबको चलाता है।
2. `on` जोड़ता है, `once` जोड़कर खुद हटा देता है, `off` हटाता है, और `emit` `true` या `false` लौटाता है।
3. Loop list की copy पर चलाओ, और बिना handler वाले `"error"` पर throw करो।

---

## ➡️ Next Topic
**186. Implement LRU Cache** — the emitter managed a changing list of listeners; the next problem uses a `Map` again, this time as a fixed-size cache that evicts the least recently used item.
