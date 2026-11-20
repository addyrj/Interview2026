# 103. Type-safe Event Emitter
# हिंदी में: Type-safe Event Emitter

> Verified with **TypeScript 5.9.3** (`--strict`) and `@types/node` (generic `EventEmitter<T>` needs a recent `@types/node`, 20+). The core pattern works on any TS 3.x+.

---

## 🔵 Simple Definition (English)
A **type-safe event emitter** is an `on` / `off` / `emit` class where the **event name decides the payload type**. You define one **event map** (`{ paid: { orderId: string; amount: number }; cancelled: string }`) and make the class generic over it: `class Emitter<E>`. Then `emit("paid", ...)` only accepts the payload declared for `"paid"`, and `on("paid", payload => ...)` gives `payload` the right type automatically. The technique is **`K extends keyof E`** + **indexed access `E[K]`**.

## 🔵 सरल परिभाषा (Hindi)
**Type-safe event emitter** एक `on` / `off` / `emit` class है जिसमें **event का नाम ही payload का type तय करता है**। आप एक **event map** (`{ paid: { orderId: string; amount: number }; cancelled: string }`) define करते हो और class को उस पर generic बनाते हो: `class Emitter<E>`। फिर `emit("paid", ...)` सिर्फ वही payload लेता है जो `"paid"` के लिए declare है, और `on("paid", payload => ...)` में `payload` का सही type अपने-आप मिलता है। Technique है **`K extends keyof E`** + **indexed access `E[K]`**।

---

## 🔴 Problem it Solves
Node's classic `EventEmitter` is untyped: `emitter.emit("paid", 1, 2, 3)` and `emitter.on("paid", (x) => x.foo)` both compile because listeners are `(...args: any[]) => void`. Typos in event names (`"payed"`), wrong payload shapes, and refactors that change a payload all fail **at runtime, in production, silently** (a misspelled event just never fires). A typed emitter turns every one of those into a compile error.

## 🔴 यह क्यों बना? (Hindi)
Node का classic `EventEmitter` untyped है: `emitter.emit("paid", 1, 2, 3)` और `emitter.on("paid", (x) => x.foo)` दोनों compile हो जाते हैं क्योंकि listeners `(...args: any[]) => void` होते हैं। Event name की typo (`"payed"`), गलत payload shape, और payload बदलने वाले refactors **runtime पर, production में, चुपचाप** fail होते हैं (गलत spelling वाला event बस कभी fire नहीं होता)। Typed emitter इन सबको compile error बना देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare an **event map** type: keys = event names, values = payload types.
Step 2 → Make the class generic: `class TypedEmitter<E extends object>`.
Step 3 → Type `on` as `on<K extends keyof E>(event: K, handler: (payload: E[K]) => void)`. TypeScript **infers `K` from the string literal** you pass, then `E[K]` gives the payload.
Step 4 → Store listeners in `Map<keyof E, Set<Function>>`. One internal cast is unavoidable because a map cannot express "key K has handler of type E[K]".
Step 5 → Return an **unsubscribe function** from `on` (avoids `off` mismatches and helps React `useEffect` cleanups).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Event map** type declare करो: keys = event names, values = payload types।
Step 2 → Class को generic बनाओ: `class TypedEmitter<E extends object>`।
Step 3 → `on` को `on<K extends keyof E>(event: K, handler: (payload: E[K]) => void)` type करो। TypeScript आपके दिए **string literal से `K` infer करता है**, फिर `E[K]` payload देता है।
Step 4 → Listeners को `Map<keyof E, Set<Function>>` में रखो। एक internal cast ज़रूरी है क्योंकि map यह express नहीं कर सकता कि "key K का handler type E[K] है"।
Step 5 → `on` से **unsubscribe function** लौटाओ (`off` mismatches से बचाता है और React `useEffect` cleanup में काम आता है)।

---

## 🟡 Real World Example
**Paytm wallet service**: after a top-up, several independent modules must react: `"wallet:credited"` (send SMS), `"wallet:low-balance"` (push notification), `"wallet:kyc-expired"` (block transfers). Each event has a different payload. With a typed emitter, the SMS module cannot accidentally subscribe to `"wallet:creditd"` and the low-balance module cannot read `payload.amount` if that event only carries `{ balance }`.

## 🟡 Real Example Hindi mein
**Paytm wallet service**: top-up के बाद कई independent modules को react करना है: `"wallet:credited"` (SMS भेजो), `"wallet:low-balance"` (push notification), `"wallet:kyc-expired"` (transfers block करो)। हर event का payload अलग है। Typed emitter के साथ SMS module गलती से `"wallet:creditd"` subscribe नहीं कर सकता और low-balance module `payload.amount` नहीं पढ़ सकता अगर उस event में सिर्फ `{ balance }` है।

---

## 💻 Code Example — Basic

```typescript
// emitter-basic.ts — a minimal, fully typed emitter
class TypedEmitter<E extends object> { // E is the event map: name -> payload
  private listeners = new Map<keyof E, Set<(payload: never) => void>>(); // internal store (loosely typed)

  on<K extends keyof E>(event: K, handler: (payload: E[K]) => void): () => void { // K inferred from the literal
    const set = this.listeners.get(event) ?? new Set(); // get or create the handler set
    set.add(handler as (payload: never) => void); // store (one safe cast, we control both ends)
    this.listeners.set(event, set); // save the set back
    return () => { set.delete(handler as (payload: never) => void); }; // unsubscribe function
  }

  emit<K extends keyof E>(event: K, payload: E[K]): void { // payload type depends on the event
    this.listeners.get(event)?.forEach((h) => (h as (p: E[K]) => void)(payload)); // call each handler
  }
}

interface WalletEvents { // event map for the wallet service
  credited: { userId: string; amount: number }; // top-up done
  lowBalance: { userId: string; balance: number }; // below threshold
  kycExpired: string; // payload is just a userId string
}

const bus = new TypedEmitter<WalletEvents>(); // create typed bus

const off = bus.on("credited", (p) => { // p is { userId: string; amount: number }, inferred
  console.log(`SMS to ${p.userId}: Rs ${p.amount} added`); // use payload safely
});
bus.on("kycExpired", (userId) => console.log("block", userId.toUpperCase())); // userId is string

bus.emit("credited", { userId: "u1", amount: 500 }); // prints SMS to u1: Rs 500 added
bus.emit("kycExpired", "u9"); // prints block U9
off(); // unsubscribe the first handler
bus.emit("credited", { userId: "u1", amount: 100 }); // prints nothing, handler removed
```

```typescript
// emitter-errors.ts — what the compiler now catches
class TypedEmitter<E extends object> { // same class, trimmed to signatures
  on<K extends keyof E>(event: K, handler: (payload: E[K]) => void): void {} // typed on
  emit<K extends keyof E>(event: K, payload: E[K]): void {} // typed emit
}
interface WalletEvents { credited: { userId: string; amount: number }; kycExpired: string } // event map
const bus = new TypedEmitter<WalletEvents>(); // bus

// ❌ 1. misspelled event name
bus.emit("creditd", { userId: "u1", amount: 5 });
// error TS2345: Argument of type '"creditd"' is not assignable to parameter of type 'keyof WalletEvents'.

// ❌ 2. wrong payload shape for a valid event
bus.emit("credited", { userId: "u1" });
// error TS2345: Argument of type '{ userId: string; }' is not assignable to parameter of type '{ userId: string; amount: number; }'.
//   Property 'amount' is missing in type '{ userId: string; }' but required in type '{ userId: string; amount: number; }'.
```

## 💻 Code Example — Advanced

```typescript
// emitter-advanced.ts — once(), listener-tuple style (like Node), and a typed async waitFor
type Listener<A extends unknown[]> = (...args: A) => void; // multiple-argument handlers

class Emitter<E extends Record<keyof E, unknown[]>> { // E maps name -> TUPLE of arguments
  private map = new Map<keyof E, Set<Listener<never[]>>>(); // untyped inner store

  on<K extends keyof E>(event: K, fn: Listener<E[K]>): () => void { // fn args = the tuple
    const set = this.map.get(event) ?? new Set<Listener<never[]>>(); // find or create set
    set.add(fn as unknown as Listener<never[]>); // store
    this.map.set(event, set); // persist
    return () => { set.delete(fn as unknown as Listener<never[]>); }; // unsubscribe
  }

  once<K extends keyof E>(event: K, fn: Listener<E[K]>): void { // fires a single time
    const off = this.on(event, ((...args: E[K]) => { off(); fn(...args); }) as Listener<E[K]>); // wrap and self-remove
  }

  emit<K extends keyof E>(event: K, ...args: E[K]): boolean { // rest args typed by the tuple
    const set = this.map.get(event); // listeners for this event
    set?.forEach((f) => (f as unknown as Listener<E[K]>)(...args)); // call each with typed args
    return !!set && set.size > 0; // true if anyone listened (like Node)
  }

  waitFor<K extends keyof E>(event: K): Promise<E[K]> { // promise that resolves with the args tuple
    return new Promise((resolve) => this.once(event, (...args) => resolve(args))); // resolve on first emit
  }
}

type OrderEvents = { // tuple-style event map
  placed: [orderId: string, amount: number]; // two labelled args
  shipped: [orderId: string]; // one arg
  closed: []; // no args at all
};

const orders = new Emitter<OrderEvents>(); // typed instance
orders.on("placed", (id, amount) => console.log(id, amount.toFixed(2))); // id: string, amount: number
orders.once("shipped", (id) => console.log("shipped once:", id)); // auto-removing handler

orders.emit("placed", "o-1", 499); // prints o-1 499.00
orders.emit("shipped", "o-1"); // prints shipped once: o-1
orders.emit("shipped", "o-1"); // nothing, once() already removed itself
const hadListeners = orders.emit("closed"); // no args allowed for "closed"
console.log(hadListeners); // prints false

orders.waitFor("placed").then(([id, amt]) => console.log("awaited", id, amt)); // await style
orders.emit("placed", "o-2", 99); // prints o-2 99.00 then awaited o-2 99
```

---

## 🟠 Node/Express + React Integration

```typescript
// node-events.ts — Node's own EventEmitter is generic since @types/node 20
import { EventEmitter } from "node:events"; // built-in module

type PaymentEvents = { // tuple map as Node expects
  captured: [paymentId: string, amount: number]; // two args
  failed: [paymentId: string, reason: string]; // two args
};

const payments = new EventEmitter<PaymentEvents>(); // generic EventEmitter<T>

payments.on("captured", (id, amount) => console.log("capture", id, amount)); // typed args
payments.emit("captured", "pay_1", 1200); // prints capture pay_1 1200
// payments.emit("captured", "pay_1"); would be a compile error: missing amount
```

```typescript
// express-sse.ts — Express route that emits a domain event after saving
import express from "express"; // express + types

type Bus = { orderPlaced: [id: string, total: number] }; // events of this service
class Mini<E extends Record<keyof E, unknown[]>> { // tiny emitter for the demo
  private h: { [K in keyof E]?: Array<(...a: E[K]) => void> } = {}; // handlers per event
  on<K extends keyof E>(e: K, f: (...a: E[K]) => void) { (this.h[e] ??= []).push(f); } // register
  emit<K extends keyof E>(e: K, ...a: E[K]) { this.h[e]?.forEach((f) => f(...a)); } // fire
}

const bus = new Mini<Bus>(); // service-wide bus
bus.on("orderPlaced", (id, total) => console.log("email receipt", id, total)); // email module subscribes

const app = express(); // app
app.use(express.json()); // JSON body
app.post("/orders", (req: express.Request<unknown, unknown, { id: string; total: number }>, res) => {
  bus.emit("orderPlaced", req.body.id, req.body.total); // typed emit after "saving"
  res.status(201).json({ ok: true }); // respond
});
```

```tsx
// useEmitter.tsx — React hook that subscribes and cleans up
import { useEffect } from "react"; // hooks

interface Subscribable<E> { // minimal shape of our emitter
  on<K extends keyof E>(event: K, handler: (payload: E[K]) => void): () => void; // returns unsubscribe
}

export function useEvent<E, K extends keyof E>(bus: Subscribable<E>, event: K, handler: (payload: E[K]) => void) {
  useEffect(() => bus.on(event, handler), [bus, event, handler]); // returning unsubscribe = cleanup function
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Typing `emit` with `string` and `any`
```typescript
// wrong-emitter.ts
class Loose {
  emit(event: string, payload: any): void {} // wrong: no link between event and payload
}
new Loose().emit("paid", 12345); // compiles, whatever you pass is accepted
```
```typescript
// right-emitter.ts
class Strict<E extends object> {
  emit<K extends keyof E>(event: K, payload: E[K]): void {} // right: event name drives payload type
}
const s = new Strict<{ paid: { id: string } }>(); // map
s.emit("paid", { id: "x" }); // ok
console.log("done"); // prints done
```

❌ Mistake 2: Defining the map as `Record<string, ...>` and losing event-name checks
```typescript
// string-keys.ts
type Loose = Record<string, { id: string }>; // every string is "a valid event"
type L = keyof Loose; // string, so typos like "creditd" are accepted
const e: L = "anything-goes"; // compiles
console.log(e); // prints anything-goes
```
✅ Correct: use an `interface` / `type` with **explicit literal keys**.

❌ Mistake 3: Forgetting to unsubscribe in React/long-lived services
✅ Correct: return the unsubscribe function from `on`, call it in `useEffect` cleanup. Leaked listeners cause duplicate side effects and `MaxListenersExceededWarning` in Node.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — is this emitter really type-safe? Spot the hole.
class TypedEmitter<E extends object> {
  emit<K extends keyof E>(event: K, payload: E[K]): void {} // the "obvious" signature
}
interface Ev { a: number; b: string } // two events
const em = new TypedEmitter<Ev>(); // instance
const evName = (Math.random() > 0.5 ? "a" : "b") as "a" | "b"; // a union of event names, e.g. from a variable

em.emit(evName, "oops"); // compiles! K = "a" | "b" so payload = number | string
em.emit(evName, 1); // compiles too, even if evName is "b" at runtime
console.log("both compile"); // prints both compile (types are fine, runtime would be wrong)
```
**Answer:** When the event name is a **union**, `K` is inferred as `"a" | "b"` and `E[K]` becomes `number | string`, so *any* of the payloads is accepted for *any* of the events. The simple signature is **unsound for union arguments**. The fix is to turn the call into a **union of valid `[event, payload]` tuples** using a distributive conditional, so each pair stays linked:

```typescript
// tricky-fixed.ts — distributive rest-args make the pair inseparable
class SafeEmitter<E extends object> {
  emit<K extends keyof E>(...args: K extends K ? [event: K, payload: E[K]] : never): void {} // K extends K distributes over the union
}
interface Ev { a: number; b: string } // two events
const em = new SafeEmitter<Ev>(); // instance
const evName = (Math.random() > 0.5 ? "a" : "b") as "a" | "b"; // union again

em.emit("a", 1); // ok
em.emit("b", "x"); // ok

// ❌ wrong payload for a literal event
em.emit("a", "wrong");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.

// ❌ a union name can no longer be paired with an arbitrary payload
em.emit(evName, 1);
// error TS2345: Argument of type '["a" | "b", 1]' is not assignable to parameter of type '[event: "a", payload: number] | [event: "b", payload: string]'.
//   Type '["a" | "b", 1]' is not assignable to type '[event: "b", payload: string]'.
//     Type at position 0 in source is not compatible with type at position 0 in target.
//       Type '"a" | "b"' is not assignable to type '"b"'.
//         Type '"a"' is not assignable to type '"b"'.
```
The user must now **narrow** `evName` (`if (evName === "a") em.emit(evName, 1)`) first, which is exactly the safe behaviour.

---

## ⚫ Interview Questions + Answers

Q1: Why `K extends keyof E` instead of `event: string`?
A1: A generic `K` captures the **literal** type of the argument ("paid") so `E[K]` can look up that event's payload. `string` throws away the literal, so there is nothing to look up.

Q2: Why is one cast needed inside the implementation?
A2: The internal `Map<keyof E, Set<Function>>` cannot express "the handler stored under key `K` has parameter `E[K]`" (a correlated-type limitation). We keep the **public API strictly typed** and cast once internally. This is acceptable because the only entry points (`on`/`emit`) are typed.

Q3: Object-payload map vs tuple map: which is better?
A3: Object payload (`credited: { userId; amount }`) is easier to evolve (add optional fields without breaking). Tuple map matches Node's variadic `emit(event, ...args)` and is what `EventEmitter<T>` in `@types/node` expects.

Q4: How do you prevent memory leaks?
A4: Return an unsubscribe function from `on`, provide `once`, clean up in React `useEffect`, and set `emitter.setMaxListeners` deliberately in Node.

Q5: How would you type `off(event, handler)`?
A5: Same signature as `on`: `off<K extends keyof E>(event: K, handler: (payload: E[K]) => void)`. Handler identity matters, so an inline arrow can never be removed, which is why returning an unsubscribe closure is preferred.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Decoupling modules inside one process (wallet -> SMS, orders -> email)
- UI-wide event buses, WebSocket message routers keyed by message type

❌ Avoid when:
- You need cross-service delivery or durability (use a queue: Azure Service Bus / Kafka)
- A plain function call or React context would be simpler and easier to trace

---

## 📊 Visual Diagram
```
 Event map E
 ┌───────────────────────────────┐
 │ credited : {userId, amount}   │
 │ kycExpired: string            │
 └───────────────┬───────────────┘
                 │ K extends keyof E
   emit("credited", payload)
        │            │
        │            └─► payload must be E["credited"]
        ▼
   listeners.get("credited")  ─►  handler(payload: E["credited"])

 on() ──► returns unsubscribe () => void   (call in useEffect cleanup)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event map | Type mapping event names to payloads | Event नाम से payload का mapping type |
| `keyof E` | Union of event names | Event नामों का union |
| `E[K]` | Payload type of event K | Event K का payload type |
| Unsubscribe | Function that removes a listener | Listener हटाने वाला function |
| Literal inference | `K` captures `"paid"`, not `string` | `K` literal पकड़ता है |
| Correlated types | Key and value types linked by the same K | Same K से जुड़े key और value types |

---

## ⚡ 3-Line Summary
English:
1. Make the emitter generic over an event map; `on`/`emit` use `K extends keyof E` and `E[K]`.
2. Keep the public API strict and cast once inside the implementation.
3. Return unsubscribe functions, support `once`, and prefer Node's `EventEmitter<T>` when on Node 20+ types.

Hindi:
1. Emitter को event map पर generic बनाओ; `on`/`emit` में `K extends keyof E` और `E[K]` इस्तेमाल करो।
2. Public API strict रखो और implementation के अंदर एक बार cast करो।
3. Unsubscribe functions लौटाओ, `once` support करो, और Node 20+ types पर Node का `EventEmitter<T>` इस्तेमाल करो।

---

## ➡️ Next Topic
**104. Typed Pub/Sub** — topic-based publish/subscribe with wildcards and typed message channels.
