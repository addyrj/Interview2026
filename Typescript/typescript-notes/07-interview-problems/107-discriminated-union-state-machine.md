# 107. Discriminated Union State Machine
# हिंदी में: Discriminated Union से State Machine

> Verified with **TypeScript 5.9.3** (`--strict`). Uses only discriminated unions, `Extract`, mapped types and `never`; works on TS 3.2+ (`satisfies` shown is **TS 4.9+**).

---

## 🔵 Simple Definition (English)
A **state machine** has a fixed set of **states**, a fixed set of **events**, and rules for which event moves which state to which next state. In TypeScript you model states as a **discriminated union** (every member has a literal `status` field), so each state **carries only the data that makes sense for it** (`succeeded` has a `txnId`, `failed` has an `error`, `idle` has neither). The goal is **"make illegal states unrepresentable"**: the compiler refuses code that reads `txnId` while the payment is still processing, and an **exhaustive `switch` with `never`** refuses to compile when you add a state but forget to handle it.

## 🔵 सरल परिभाषा (Hindi)
**State machine** में **states** का fixed set, **events** का fixed set, और नियम होते हैं कि कौन सा event किस state को किस अगली state में ले जाएगा। TypeScript में states को **discriminated union** से model करते हैं (हर member में literal `status` field), इसलिए हर state **सिर्फ वही data रखती है जो उसके लिए सही है** (`succeeded` में `txnId`, `failed` में `error`, `idle` में कुछ नहीं)। लक्ष्य है **"illegal states को represent ही न होने देना"**: payment अभी processing में हो तो compiler `txnId` पढ़ने वाला code reject करता है, और **`never` वाला exhaustive `switch`** नया state जोड़कर handle करना भूलने पर compile होने से मना करता है।

---

## 🔴 Problem it Solves
The classic bug-factory is a bag of booleans: `{ isLoading: boolean; isError: boolean; data?: Order; error?: string }`. That type allows `isLoading && isError`, `isError` with no `error`, or `data` present while loading: **2^n impossible combinations**, each needing defensive `if`s in the UI. A discriminated union has exactly the valid states, nothing else, and the UI `switch` becomes the only place where each state is rendered.

## 🔴 यह क्यों बना? (Hindi)
Bug पैदा करने वाली classic चीज़ booleans का थैला है: `{ isLoading: boolean; isError: boolean; data?: Order; error?: string }`। यह type `isLoading && isError`, बिना `error` के `isError`, या loading के दौरान `data` मौजूद होना, सब allow करता है: **2^n impossible combinations**, जिनके लिए UI में defensive `if` लगाने पड़ते हैं। Discriminated union में सिर्फ valid states होते हैं, और UI का `switch` वह अकेली जगह बनता है जहाँ हर state render होती है।

---

## 🟢 How it Works — Step by Step

Step 1 → List the **states** as a union with a literal discriminant: `{ status: "idle" } | { status: "processing"; startedAt: number } | ...`.
Step 2 → List the **events** as another discriminated union with `type`: `{ type: "PAY" } | { type: "SUCCESS"; txnId: string } | ...`.
Step 3 → Write `transition(state, event): State` as a **pure function** (it is exactly a Redux reducer). Switch on `state.status`, then on `event.type`; unknown pairs return the same state.
Step 4 → End each switch with an **exhaustive check**: `default: const _x: never = state; return _x;`. Adding a state now produces a compile error here.
Step 5 → For compile-time **illegal transitions**, use the **typestate** style: functions typed with `Extract<State, { status: "idle" }>` as input and the next state as output, so `pay(succeededState)` simply does not type-check.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **States** को literal discriminant वाले union में लिखो: `{ status: "idle" } | { status: "processing"; startedAt: number } | ...`।
Step 2 → **Events** को `type` वाले दूसरे discriminated union में लिखो: `{ type: "PAY" } | { type: "SUCCESS"; txnId: string } | ...`।
Step 3 → `transition(state, event): State` को **pure function** बनाओ (यह बिल्कुल Redux reducer है)। पहले `state.status` पर switch, फिर `event.type` पर; unknown pair पर वही state लौटाओ।
Step 4 → हर switch के अंत में **exhaustive check** लगाओ: `default: const _x: never = state; return _x;`। नया state जोड़ते ही यहाँ compile error आएगा।
Step 5 → Compile-time **illegal transitions** के लिए **typestate** style: input `Extract<State, { status: "idle" }>` और output अगला state, ताकि `pay(succeededState)` type-check ही न हो।

---

## 🟡 Real World Example
**Razorpay checkout**: `idle -> processing -> succeeded | failed`, and `failed -> processing` (retry, max 3) or `failed -> idle` (cancel). The UI shows a spinner only in `processing`, the receipt only in `succeeded` (where `txnId` exists), and the retry button only in `failed` (where `retries` exists). A double-click on "Pay" in `processing` is ignored by the transition function instead of creating two charges.

## 🟡 Real Example Hindi mein
**Razorpay checkout**: `idle -> processing -> succeeded | failed`, और `failed -> processing` (retry, अधिकतम 3) या `failed -> idle` (cancel)। UI में spinner सिर्फ `processing` में, receipt सिर्फ `succeeded` में (जहाँ `txnId` है), और retry button सिर्फ `failed` में (जहाँ `retries` है)। `processing` में "Pay" पर double-click transition function ignore कर देता है, दो बार charge नहीं होता।

---

## 💻 Code Example — Basic

```typescript
// payment-machine.ts — states, events, pure transition, exhaustive check
type PaymentState = // each member carries ONLY its own data
  | { status: "idle" } // nothing happened yet
  | { status: "processing"; startedAt: number } // waiting for the gateway
  | { status: "succeeded"; txnId: string } // money moved
  | { status: "failed"; error: string; retries: number }; // gateway said no

type PaymentEvent = // everything that can happen
  | { type: "PAY"; at: number } // user clicked Pay
  | { type: "SUCCESS"; txnId: string } // gateway ok
  | { type: "FAIL"; error: string } // gateway error
  | { type: "RETRY"; at: number } // user retries
  | { type: "RESET" }; // user cancels

function transition(state: PaymentState, event: PaymentEvent): PaymentState { // pure function
  switch (state.status) { // narrow by the discriminant
    case "idle":
      return event.type === "PAY" ? { status: "processing", startedAt: event.at } : state; // only PAY is legal
    case "processing":
      if (event.type === "SUCCESS") return { status: "succeeded", txnId: event.txnId }; // done
      if (event.type === "FAIL") return { status: "failed", error: event.error, retries: 0 }; // failed
      return state; // ignore double PAY: no double charge
    case "succeeded":
      return state; // terminal state: nothing can change it
    case "failed":
      if (event.type === "RETRY" && state.retries < 3) // state.retries exists here
        return { status: "processing", startedAt: event.at }; // retry allowed
      if (event.type === "RESET") return { status: "idle" }; // back to start
      return state; // everything else ignored
    default: { // exhaustive check: if a new state is added and not handled, this line fails to compile
      const unreachable: never = state; // state is `never` only when ALL cases are covered
      return unreachable; // satisfies the return type
    }
  }
}

let s: PaymentState = { status: "idle" }; // start
s = transition(s, { type: "PAY", at: 1 }); // -> processing
s = transition(s, { type: "PAY", at: 2 }); // ignored (double click)
s = transition(s, { type: "SUCCESS", txnId: "txn_42" }); // -> succeeded
console.log(s.status === "succeeded" ? `paid ${s.txnId}` : s.status); // prints paid txn_42
```

```typescript
// payment-errors.ts — the compiler guards illegal reads and forgotten states
type PaymentState =
  | { status: "idle" }
  | { status: "processing"; startedAt: number }
  | { status: "succeeded"; txnId: string }; // pretend "failed" was just added by a teammate below

declare const s: PaymentState; // some state

// ❌ 1. reading txnId without narrowing
console.log(s.txnId);
// error TS2339: Property 'txnId' does not exist on type 'PaymentState'.
//   Property 'txnId' does not exist on type '{ status: "idle"; }'.

type WithFailed = PaymentState | { status: "failed"; error: string }; // a new state arrives
function label(st: WithFailed): string {
  switch (st.status) {
    case "idle": return "Pay now"; // handled
    case "processing": return "Please wait"; // handled
    case "succeeded": return "Done"; // handled
    default: {
      // ❌ 2. "failed" forgotten: exhaustiveness check catches it
      const _x: never = st;
      return _x;
      // error TS2322: Type '{ status: "failed"; error: string; }' is not assignable to type 'never'.
    }
  }
}
```

## 💻 Code Example — Advanced

```typescript
// payment-typestate.ts — illegal transitions fail at COMPILE time + a data-driven transition table
type State = // same states as before
  | { status: "idle" }
  | { status: "processing"; startedAt: number }
  | { status: "succeeded"; txnId: string }
  | { status: "failed"; error: string; retries: number };

type Of<S extends State["status"]> = Extract<State, { status: S }>; // pick one member by its status

// Typestate functions: input and output types are the exact allowed states
const pay = (_s: Of<"idle">, at: number): Of<"processing"> => ({ status: "processing", startedAt: at }); // idle -> processing
const succeed = (_s: Of<"processing">, txnId: string): Of<"succeeded"> => ({ status: "succeeded", txnId }); // processing -> succeeded
const fail = (_s: Of<"processing">, error: string): Of<"failed"> => ({ status: "failed", error, retries: 0 }); // processing -> failed
const retry = (s: Of<"failed">, at: number): Of<"processing"> => ({ status: "processing", startedAt: at + s.retries }); // failed -> processing

const p0: Of<"idle"> = { status: "idle" }; // start
const p1 = pay(p0, 1); // p1: processing
const p2 = succeed(p1, "txn_7"); // p2: succeeded
console.log(p2.txnId); // prints txn_7 (txnId is known to exist, no narrowing needed)

// ❌ cannot pay again after success: the type of p2 has no overlap with Of<"idle">
pay(p2, 3);
// error TS2345: Argument of type '{ status: "succeeded"; txnId: string; }' is not assignable to parameter of type '{ status: "idle"; }'.
//   Types of property 'status' are incompatible.
//     Type '"succeeded"' is not assignable to type '"idle"'.

// Data-driven table: which events are legal from each state (compile-checked with satisfies, TS 4.9+)
const allowed = {
  idle: ["PAY"], // idle accepts PAY only
  processing: ["SUCCESS", "FAIL"], // two outcomes
  succeeded: [], // terminal
  failed: ["RETRY", "RESET"], // retry or give up
} as const satisfies Record<State["status"], readonly string[]>; // missing a state = compile error

type AllowedEvent<S extends State["status"]> = (typeof allowed)[S][number]; // "PAY" for idle, never for succeeded
const e: AllowedEvent<"failed"> = "RETRY"; // ok
console.log(allowed.failed.includes("RETRY"), e); // prints true RETRY
console.log(retry({ status: "failed", error: "x", retries: 2 }, 10).startedAt); // prints 12
console.log(fail(p1, "declined").retries); // prints 0
```

---

## 🟠 Node/Express + React Integration

```typescript
// order-route.ts — Express: server enforces the same machine, rejects illegal events with 409
import express from "express"; // express + types

type OrderStatus = "placed" | "packed" | "shipped" | "delivered"; // lifecycle
const next: Record<OrderStatus, OrderStatus | null> = { placed: "packed", packed: "shipped", shipped: "delivered", delivered: null }; // table
const orders = new Map<number, OrderStatus>([[1, "placed"]]); // demo store (SQL Server in real life)

const app = express(); // app
app.post("/orders/:id/advance", (req, res) => {
  const cur = orders.get(Number(req.params.id)); // current status or undefined
  if (cur === undefined) { res.sendStatus(404); return; } // unknown order
  const to = next[cur]; // legal next status
  if (to === null) { res.status(409).json({ error: `already ${cur}` }); return; } // terminal: conflict
  orders.set(Number(req.params.id), to); // persist transition
  res.json({ from: cur, to }); // report
});
```

```tsx
// PayButton.tsx — React useReducer + the union: UI renders per state, no boolean flags
import { useReducer } from "react"; // hooks

type S = { status: "idle" } | { status: "processing" } | { status: "succeeded"; txnId: string } | { status: "failed"; error: string }; // states
type E = { type: "PAY" } | { type: "OK"; txnId: string } | { type: "ERR"; error: string } | { type: "RESET" }; // events

function reducer(s: S, e: E): S { // reducer = transition function
  if (e.type === "RESET") return { status: "idle" }; // always allowed
  if (s.status === "idle" && e.type === "PAY") return { status: "processing" }; // idle -> processing
  if (s.status === "processing" && e.type === "OK") return { status: "succeeded", txnId: e.txnId }; // success
  if (s.status === "processing" && e.type === "ERR") return { status: "failed", error: e.error }; // failure
  return s; // everything else: ignore
}

export function PayButton() { // component
  const [s, dispatch] = useReducer(reducer, { status: "idle" }); // s: S, dispatch: (e: E) => void
  switch (s.status) { // one switch = one place per state
    case "idle": return <button onClick={() => dispatch({ type: "PAY" })}>Pay</button>; // pay button
    case "processing": return <button disabled>Processing</button>; // spinner state
    case "succeeded": return <p>Paid {s.txnId}</p>; // txnId available only here
    case "failed": return <button onClick={() => dispatch({ type: "RESET" })}>{s.error}, try again</button>; // error available only here
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Boolean flags instead of a union
```typescript
// wrong-flags.ts
interface Bad { isLoading: boolean; isError: boolean; data?: string; error?: string } // wrong: allows nonsense
const impossible: Bad = { isLoading: true, isError: true, data: "x" }; // compiles but means nothing

type Good = { status: "loading" } | { status: "error"; error: string } | { status: "ok"; data: string }; // right
const fine: Good = { status: "ok", data: "x" }; // only valid shapes exist
console.log(impossible.isLoading, fine.status); // prints true ok
```

❌ Mistake 2: Using a plain `string` as the discriminant
```typescript
// wrong-string.ts
type Wrong = { status: string; txnId?: string }; // wrong: "status" is any string, no narrowing

function show(w: Wrong): string {
  // ❌ txnId is optional, so even after checking status the compiler still sees string | undefined
  return w.status === "succeeded" ? w.txnId.toUpperCase() : "";
  // error TS18048: 'w.txnId' is possibly 'undefined'.
}
console.log(show({ status: "succeeded", txnId: "a" })); // never reached when compiling
```
✅ Correct: use **literal** types for the discriminant and put data in the member that owns it.

❌ Mistake 3: Mutating the state object inside `transition`
✅ Correct: always return a **new** object (`{ ...state, ... }`). React and Redux detect changes by reference.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — why does the exhaustive check compile here?
type Shape = { kind: "circle"; r: number } | { kind: "square"; s: number }; // two shapes

function area(x: Shape): number {
  if (x.kind === "circle") return Math.PI * x.r ** 2; // circle
  if (x.kind === "square") return x.s ** 2; // square
  const _never: never = x; // x is never here
  return _never; // fine
}
const bad = { kind: "triangle", b: 1 } as unknown as Shape; // lies to the compiler
console.log(Number.isNaN(area(bad))); // what happens at runtime?
```
**Answer:** It compiles because after both `if`s TypeScript has narrowed `x` to `never`. At **runtime** the lie (`as unknown as Shape`) bypasses the types, `area(bad)` reaches `return _never` and silently returns the object where a number is expected; `Number.isNaN` of a non-number returns `false`, so it prints `false`. Exhaustiveness checks protect you from **your own forgotten cases**, not from untrusted data. For API boundaries, add a runtime default that **throws** (``throw new Error(`Unhandled: ${JSON.stringify(x)}`)``) or validate with Zod before the data enters the typed world.

---

## ⚫ Interview Questions + Answers

Q1: What makes a union "discriminated"?
A1: Every member has a property with a **literal type** (the discriminant, e.g. `status`). Checking it (`===`, `switch`) narrows the union to the matching member.

Q2: How does the `never` exhaustive check work?
A2: After all cases are handled the variable's type is `never`. Assigning it to a `never` variable compiles; if a case is missing, the remaining member is not assignable to `never` and you get `TS2322`. That makes adding a new state a compile-time to-do list.

Q3: State machine vs useState with booleans?
A3: The machine has exactly the valid states and explicit transitions, so impossible combinations cannot exist. Booleans allow 2^n combinations, most invalid, and the UI needs defensive checks.

Q4: What is the typestate pattern?
A4: Encode the current state in the **type** of the value and make each operation accept one state type and return the next. `pay(succeeded)` becomes a type error. Best for in-memory workflows where one code path holds the value; for DB-backed state use a runtime transition table, as the server cannot know the type.

Q5: When would you use XState instead?
A5: When you need hierarchical/parallel states, timers (`after`), actors, visualisation, or the machine is shared across teams. For 4-6 states a union plus `switch` is simpler and has zero dependencies.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Async UI flows (loading/error/success), checkout/payment, form wizards
- Order/ticket lifecycles on the server with strict legal transitions

❌ Avoid when:
- There are only two trivial states (a boolean is fine)
- States number in the dozens with parallel regions (use XState or a statechart)

---

## 📊 Visual Diagram
```
                 PAY                SUCCESS
     ┌──────┐ ───────► ┌────────────┐ ───────► ┌───────────┐
     │ idle │          │ processing │          │ succeeded │ (terminal)
     └──────┘ ◄─────── └────────────┘          └───────────┘
        ▲      RESET        │ FAIL
        │                   ▼
        │             ┌──────────┐   RETRY (retries < 3)
        └─── RESET ── │  failed  │ ─────────────► processing
                      └──────────┘

 { status: "succeeded"; txnId }   <- only this member has txnId
 default: const _x: never = state // adding a state => compile error here
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Discriminant | Literal field that identifies the member | Member पहचानने वाला literal field |
| Narrowing | Compiler refines a union after a check | Check के बाद union संकरा होना |
| Exhaustive check | `never` assignment proves all cases handled | `never` से सब cases handled का प्रमाण |
| Typestate | State encoded in the value's type | State को type में encode करना |
| Transition | Function (state, event) -> next state | (state, event) से अगला state |
| Illegal state | Combination that should not exist | जो combination होना ही नहीं चाहिए |

---

## ⚡ 3-Line Summary
English:
1. Model states as a discriminated union where each member carries only its own data.
2. Write `transition(state, event)` as a pure function and finish every switch with a `never` exhaustive check.
3. For compile-time illegal transitions use typestate functions with `Extract<State, { status: S }>`; on the server also keep a runtime transition table.

Hindi:
1. States को discriminated union से model करो जहाँ हर member सिर्फ अपना data रखे।
2. `transition(state, event)` को pure function लिखो और हर switch `never` वाले exhaustive check से ख़त्म करो।
3. Compile-time illegal transitions के लिए `Extract<State, { status: S }>` वाले typestate functions इस्तेमाल करो; server पर runtime transition table भी रखो।

---

## ➡️ Next Topic
**108. Branded IDs (UserId vs OrderId)** — stopping `getOrder(userId)` bugs with nominal-style types.
