# 104. Typed Pub/Sub
# हिंदी में: Typed Pub/Sub (Publish-Subscribe)

> Verified with **TypeScript 5.9.3** (`--strict`). Uses **template literal types** (TS 4.1+) and **distributive conditional types**. No 5.x-only features needed.

---

## 🔵 Simple Definition (English)
**Pub/Sub** (publish/subscribe) decouples **publishers** (who announce "something happened") from **subscribers** (who react). A **typed** Pub/Sub keeps a single **topic map** (`"order.created" -> { orderId; total }`) so that `publish("order.created", payload)` checks the payload, `subscribe("order.created", handler)` types the handler, and **wildcard-by-namespace** subscriptions (`"order"` = every `order.*` topic) receive a **discriminated union** of all matching `{ topic, payload }` pairs. It builds on the typed emitter (topic 103) but adds namespaces, async fan-out and error isolation.

## 🔵 सरल परिभाषा (Hindi)
**Pub/Sub** (publish/subscribe) **publishers** (जो बताते हैं "कुछ हुआ") को **subscribers** (जो react करते हैं) से अलग करता है। **Typed** Pub/Sub एक **topic map** (`"order.created" -> { orderId; total }`) रखता है ताकि `publish("order.created", payload)` payload check करे, `subscribe("order.created", handler)` handler को type दे, और **namespace-wildcard** subscriptions (`"order"` = हर `order.*` topic) को सभी matching `{ topic, payload }` pairs का **discriminated union** मिले। यह typed emitter (topic 103) पर बना है पर namespaces, async fan-out और error isolation जोड़ता है।

---

## 🔴 Problem it Solves
In a growing backend, `OrderService` ends up importing `EmailService`, `InventoryService`, `AnalyticsService`... a tangle of direct calls. Pub/Sub inverts it: `OrderService` just publishes `"order.paid"`. But untyped pub/sub (`publish("order.paid", anything)`) brings back the same bugs: misspelled topics that silently never fire, payload shape drift between publisher and subscriber, and wildcard handlers that must guess which payload they got. Types make the **contract** between modules explicit and refactor-safe.

## 🔴 यह क्यों बना? (Hindi)
बढ़ते backend में `OrderService` को `EmailService`, `InventoryService`, `AnalyticsService`... सबको import करना पड़ता है, direct calls का जाल। Pub/Sub इसे उलट देता है: `OrderService` बस `"order.paid"` publish करता है। पर untyped pub/sub (`publish("order.paid", anything)`) वही bugs वापस लाता है: गलत spelling के topics जो चुपचाप कभी fire नहीं होते, publisher और subscriber के बीच payload shape drift, और wildcard handlers को अंदाज़ा लगाना पड़ता है कि कौन सा payload मिला। Types modules के बीच **contract** को साफ़ और refactor-safe बनाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Define the **topic map**: a type whose keys look like `"namespace.action"`.
Step 2 → Extract namespaces with a template literal type: ``K extends `${infer N}.${string}` ? N : never``.
Step 3 → `subscribe<K extends keyof T>(topic, handler: (payload: T[K]) => void)` for exact topics.
Step 4 → `subscribeNs<N extends Namespace>(ns, handler)` where the handler argument is a **distributed union**: `{ [K in Matching<N>]: { topic: K; payload: T[K] } }[Matching<N>]`. Checking `msg.topic` then narrows `msg.payload`.
Step 5 → `publish` calls exact handlers and namespace handlers; use `Promise.allSettled` so one failing subscriber does not stop the others.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Topic map** define करो: ऐसा type जिसकी keys `"namespace.action"` जैसी हों।
Step 2 → Template literal type से namespaces निकालो: ``K extends `${infer N}.${string}` ? N : never``।
Step 3 → Exact topics के लिए `subscribe<K extends keyof T>(topic, handler: (payload: T[K]) => void)`।
Step 4 → `subscribeNs<N extends Namespace>(ns, handler)` जहाँ handler का argument **distributed union** है: `{ [K in Matching<N>]: { topic: K; payload: T[K] } }[Matching<N>]`। `msg.topic` check करने से `msg.payload` narrow हो जाता है।
Step 5 → `publish` exact handlers और namespace handlers दोनों call करता है; `Promise.allSettled` इस्तेमाल करो ताकि एक subscriber fail होने पर बाकी न रुकें।

---

## 🟡 Real World Example
**Swiggy order pipeline**: when payment succeeds, `PaymentService` publishes `"payment.captured"`. `OrderService` subscribes to it to mark the order confirmed and publishes `"order.confirmed"`. `NotificationService` subscribes to the **`order` namespace** (all `order.*`), `RestaurantService` to `"order.confirmed"` only, and an audit logger to **every namespace**. Nobody imports anybody; the **topic map** is the only shared file.

## 🟡 Real Example Hindi mein
**Swiggy order pipeline**: payment सफल होने पर `PaymentService` `"payment.captured"` publish करती है। `OrderService` उसे subscribe करके order confirm करती है और `"order.confirmed"` publish करती है। `NotificationService` **`order` namespace** (सभी `order.*`) subscribe करती है, `RestaurantService` सिर्फ `"order.confirmed"`, और audit logger **हर namespace**। कोई किसी को import नहीं करता; सिर्फ **topic map** साझा file है।

---

## 💻 Code Example — Basic

```typescript
// pubsub-basic.ts — exact-topic typed pub/sub
class PubSub<T extends object> { // T is the topic map
  private subs = new Map<keyof T, Set<(payload: never) => void>>(); // topic -> handlers (inner store loose)

  subscribe<K extends keyof T>(topic: K, handler: (payload: T[K]) => void): () => void { // typed handler
    const set = this.subs.get(topic) ?? new Set(); // find or create
    set.add(handler as (payload: never) => void); // register
    this.subs.set(topic, set); // persist
    return () => { set.delete(handler as (payload: never) => void); }; // unsubscribe
  }

  publish<K extends keyof T>(topic: K, payload: T[K]): number { // returns how many handlers ran
    const set = this.subs.get(topic); // who listens?
    set?.forEach((h) => (h as (p: T[K]) => void)(payload)); // call them
    return set?.size ?? 0; // count
  }
}

interface Topics { // the contract shared by all services
  "payment.captured": { paymentId: string; amount: number }; // from PaymentService
  "order.confirmed": { orderId: string; eta: number }; // from OrderService
}

const bus = new PubSub<Topics>(); // one bus per process
bus.subscribe("payment.captured", (p) => { // p typed as { paymentId; amount }
  console.log(`confirm order for ${p.paymentId}`); // handler body
  bus.publish("order.confirmed", { orderId: "o-1", eta: 30 }); // chain a second topic
});
bus.subscribe("order.confirmed", (p) => console.log(`ETA ${p.eta} min`)); // typed eta: number

console.log(bus.publish("payment.captured", { paymentId: "pay_9", amount: 450 })); // prints confirm..., ETA 30 min, then 1
```

```typescript
// pubsub-errors.ts — typed topics reject typos and bad payloads
class PubSub<T extends object> { // signatures only
  publish<K extends keyof T>(topic: K, payload: T[K]): void {} // typed publish
}
interface Topics { "order.confirmed": { orderId: string; eta: number } } // one topic
const bus = new PubSub<Topics>(); // instance

// ❌ typo in topic name
bus.publish("order.confirmd", { orderId: "o1", eta: 5 });
// error TS2345: Argument of type '"order.confirmd"' is not assignable to parameter of type '"order.confirmed"'.

// ❌ payload field has the wrong type
bus.publish("order.confirmed", { orderId: "o1", eta: "soon" });
// error TS2322: Type 'string' is not assignable to type 'number'.
```

## 💻 Code Example — Advanced

```typescript
// pubsub-advanced.ts — namespace wildcards producing a discriminated union + async fan-out
type Namespace<K extends string> = K extends `${infer N}.${string}` ? N : never; // "order.paid" -> "order"
type InNs<K extends string, N extends string> = Extract<K, `${N}.${string}`>; // all topics in namespace N

class PubSub<T extends object> { // T = topic map
  private exact = new Map<string, Set<(p: never) => unknown>>(); // topic handlers
  private ns = new Map<string, Set<(m: never) => unknown>>(); // namespace handlers

  subscribe<K extends keyof T & string>(topic: K, fn: (payload: T[K]) => unknown): () => void { // exact
    const s = this.exact.get(topic) ?? new Set(); // set for topic
    s.add(fn as (p: never) => unknown); // add
    this.exact.set(topic, s); // save
    return () => { s.delete(fn as (p: never) => unknown); }; // unsubscribe
  }

  // handler receives a union such as { topic: "order.created"; payload: ... } | { topic: "order.paid"; payload: ... }
  subscribeNs<N extends Namespace<keyof T & string>>(
    ns: N, // namespace name, only real ones accepted
    fn: (msg: { [K in InNs<keyof T & string, N>]: { topic: K; payload: T[K] } }[InNs<keyof T & string, N>]) => unknown,
  ): () => void {
    const s = this.ns.get(ns) ?? new Set(); // set for namespace
    s.add(fn as (m: never) => unknown); // add
    this.ns.set(ns, s); // save
    return () => { s.delete(fn as (m: never) => unknown); }; // unsubscribe
  }

  async publish<K extends keyof T & string>(topic: K, payload: T[K]): Promise<PromiseSettledResult<unknown>[]> {
    const nsName = topic.split(".")[0] ?? ""; // namespace of this topic
    const calls: Array<() => unknown> = []; // collected calls
    this.exact.get(topic)?.forEach((h) => calls.push(() => (h as (p: T[K]) => unknown)(payload))); // exact
    this.ns.get(nsName)?.forEach((h) => calls.push(() => (h as (m: unknown) => unknown)({ topic, payload }))); // ns
    return Promise.allSettled(calls.map(async (c) => c())); // one failing handler cannot stop the rest
  }
}

interface Topics { // contract
  "order.created": { orderId: string; total: number }; // order service
  "order.cancelled": { orderId: string; reason: string }; // order service
  "payment.captured": { paymentId: string }; // payment service
}

const bus = new PubSub<Topics>(); // instance

bus.subscribeNs("order", (msg) => { // msg is a union of the two order.* messages
  if (msg.topic === "order.created") console.log("new order", msg.payload.total); // narrowed: total exists
  else console.log("cancelled", msg.payload.reason); // narrowed: reason exists
});
bus.subscribe("order.created", () => { throw new Error("email service down"); }); // a failing subscriber

async function main() { // run the demo
  const r1 = await bus.publish("order.created", { orderId: "o1", total: 450 }); // prints new order 450; the exact handler throws but does not stop the ns handler
  console.log(r1.map((r) => r.status)); // prints [ 'rejected', 'fulfilled' ] (exact handlers run first, then namespace handlers)
  await bus.publish("order.cancelled", { orderId: "o1", reason: "out of stock" }); // prints cancelled out of stock
}
main(); // start
```

---

## 🟠 Node/Express + React Integration

```typescript
// webhook-route.ts — Razorpay-style webhook publishes a typed topic
import express from "express"; // express + types

interface Topics { "payment.captured": { paymentId: string; amount: number } } // topic map
const handlers: Array<(p: Topics["payment.captured"]) => void> = []; // minimal bus to keep the demo short
const publish = <K extends keyof Topics>(_t: K, p: Topics[K]) => handlers.forEach((h) => h(p as Topics["payment.captured"])); // typed publish

handlers.push((p) => console.log("mark paid", p.paymentId)); // OrderService subscribes

const app = express(); // app
app.use(express.json()); // JSON body parser
app.post("/webhooks/razorpay", (req: express.Request<unknown, unknown, { id: string; amount: number }>, res) => {
  publish("payment.captured", { paymentId: req.body.id, amount: req.body.amount }); // route knows nothing about subscribers
  res.sendStatus(200); // ack fast, work happens in subscribers
});
```

```tsx
// useTopic.tsx — React hook over a typed bus (e.g. fed by a WebSocket)
import { useEffect, useState } from "react"; // hooks

interface Bus<T> { // minimal bus contract
  subscribe<K extends keyof T>(topic: K, fn: (payload: T[K]) => void): () => void; // returns unsubscribe
}

export function useTopic<T, K extends keyof T>(bus: Bus<T>, topic: K): T[K] | undefined {
  const [last, setLast] = useState<T[K] | undefined>(undefined); // latest message, none yet
  useEffect(() => bus.subscribe(topic, (p) => setLast(p)), [bus, topic]); // subscribe, unsubscribe on cleanup
  return last; // component re-renders on every message
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Declaring topics as plain `string` so wildcards get no types
```typescript
// wrong-string-topics.ts
type Handler = (topic: string, payload: unknown) => void; // wrong: every handler must cast the payload
const h: Handler = (topic, payload) => { console.log(topic, (payload as { total: number }).total); }; // unsafe cast
h("order.created", { total: 450 }); // prints order.created 450
```
✅ Correct: derive the union `{ topic: K; payload: T[K] }` (see `subscribeNs`) so narrowing on `topic` types `payload`.

❌ Mistake 2: Subscribing to a namespace that does not exist
```typescript
// bad-namespace.ts
type Namespace<K extends string> = K extends `${infer N}.${string}` ? N : never; // helper
type Allowed = Namespace<"order.created" | "payment.captured">; // "order" | "payment"

// ❌ "ordr" is not a namespace
const ns: Allowed = "ordr";
// error TS2820: Type '"ordr"' is not assignable to type 'Allowed'. Did you mean '"order"'?
```

❌ Mistake 3: Letting one subscriber's exception break the publisher
✅ Correct: wrap handler calls (`Promise.allSettled` / try-catch) and log failures. The publisher must not depend on subscriber health.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — what does Namespace give for a topic with TWO dots?
type Namespace<K extends string> = K extends `${infer N}.${string}` ? N : never; // first-dot split
type A = Namespace<"order.item.added">; // ?
type B = Namespace<"heartbeat">; // ?
const a: A = "order"; // compiles
console.log(a); // prints order
```
**Answer:** `A` is `"order"` and `B` is `never`. Template-literal inference with ``${infer N}.${string}`` is **non-greedy for the first placeholder**: `N` takes the shortest prefix up to the **first** dot, so `"order.item.added"` gives `"order"`. A topic without a dot does not match the pattern, hits the `: never` branch, and **disappears from the union**, so a dotless topic can never be subscribed through a namespace. For nested namespaces use a recursive type that accumulates segments (`"order" | "order.item"`).

---

## ⚫ Interview Questions + Answers

Q1: Pub/Sub vs the Observer pattern?
A1: Observer has subjects that know their observers directly. Pub/Sub adds a **broker/bus in the middle** so publishers and subscribers do not know each other, and often supports topics, wildcards and async delivery.

Q2: How do you give a wildcard handler a correctly-typed payload?
A2: Build a **distributed union** over matching topics: `{ [K in Matching]: { topic: K; payload: T[K] } }[Matching]`. The `topic` field becomes a discriminant, so `if (msg.topic === "...")` narrows `payload`.

Q3: What guarantees does in-process pub/sub NOT give?
A3: No persistence, retries, ordering across processes, or delivery after a crash. For that use Azure Service Bus / Event Grid / Kafka, and type the message contracts with the **same** topic map shared as a package.

Q4: Why `Promise.allSettled` for fan-out?
A4: `Promise.all` rejects as soon as one handler fails and hides the others' results; `allSettled` waits for all and reports each outcome, so one bad subscriber cannot break the publisher.

Q5: How do you version payloads safely?
A5: Add optional fields only (backward compatible), or version the topic name (`"order.created.v2"`) and keep both in the topic map during migration. Validate incoming messages from the network with Zod, since types do not exist at runtime.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Domain events inside a modular monolith (order -> email/inventory/analytics)
- Fan-out of WebSocket/SSE messages to many React components

❌ Avoid when:
- You need guaranteed delivery across services (use a durable broker)
- Only one consumer exists, a direct function call is clearer

---

## 📊 Visual Diagram
```
 PaymentService ──publish("payment.captured", {...})──┐
                                                       ▼
                                              ┌─────────────────┐
 OrderService  ◄── subscribe exact ───────────│      BUS        │
 Notification  ◄── subscribeNs("order") ──────│  Topics map     │
 Audit logger  ◄── subscribeNs("payment") ────│  (typed)        │
                                              └─────────────────┘
 subscribeNs("order") handler receives:
   { topic: "order.created";   payload: {orderId,total} }
 | { topic: "order.cancelled"; payload: {orderId,reason} }   <- narrow on .topic
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Publisher / Subscriber | Sender / receiver of events | भेजने / पाने वाला |
| Topic map | Type listing topics and payloads | Topics और payloads का type |
| Namespace | Prefix before the first dot | पहले dot से पहले का हिस्सा |
| Template literal type | String-pattern type | String pattern वाला type |
| Fan-out | One message to many handlers | एक message कई handlers को |
| `allSettled` | Wait for all promises, never reject | सबका इंतज़ार, कभी reject नहीं |

---

## ⚡ 3-Line Summary
English:
1. One topic map is the contract: `publish`/`subscribe` use `K extends keyof T` and `T[K]`.
2. Namespace wildcards use template literal types to build a discriminated union of `{ topic, payload }`.
3. Isolate subscriber failures with `Promise.allSettled`; use a durable broker when delivery must be guaranteed.

Hindi:
1. एक topic map ही contract है: `publish`/`subscribe` में `K extends keyof T` और `T[K]` इस्तेमाल होता है।
2. Namespace wildcards template literal types से `{ topic, payload }` का discriminated union बनाते हैं।
3. Subscriber failures को `Promise.allSettled` से अलग रखो; delivery guarantee चाहिए तो durable broker इस्तेमाल करो।

---

## ➡️ Next Topic
**105. Typed fetch Wrapper with Generics** — `api.get<Order>("/orders/1")`, error handling and runtime validation.
