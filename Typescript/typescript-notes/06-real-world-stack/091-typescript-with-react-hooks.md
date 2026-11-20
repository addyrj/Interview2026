# 91. TypeScript with React Hooks (useState, useReducer, useRef)
# हिंदी में: React Hooks के साथ TypeScript (useState, useReducer, useRef)

> Verified with **TypeScript 5.9 (5.x)**, `@types/react` 19, `--strict`. Note: in `@types/react` 19, `useRef` requires an initial argument.

---

## 🔵 Simple Definition (English)
Hooks are generic functions. TypeScript usually **infers** the type from the initial value (`useState(0)` is `number`), but you must pass a type argument when the initial value cannot describe the full type (`useState<User | null>(null)`). `useReducer` is typed by a **state type + a discriminated-union action type**, and `useRef` has two faces: a DOM ref (`useRef<HTMLInputElement>(null)`, `.current` may be `null`) and a mutable value box (`useRef<number>(0)`).

## 🔵 सरल परिभाषा (Hindi)
Hooks generic functions हैं। TypeScript अक्सर initial value से type **infer** कर लेता है (`useState(0)` = `number`), लेकिन जब initial value पूरा type नहीं बताती तब type argument देना पड़ता है (`useState<User | null>(null)`)। `useReducer` का type **state type + discriminated-union action type** से बनता है, और `useRef` के दो रूप हैं: DOM ref (`useRef<HTMLInputElement>(null)`, `.current` `null` हो सकता है) और mutable value box (`useRef<number>(0)`)।

---

## 🔴 Problem it Solves
`useState(null)` makes the state type literally `null`, so `setUser({...})` is rejected. A reducer with `action: any` accepts `{ type: "typo" }`. `inputRef.current.focus()` crashes at runtime when the ref is not yet attached. Typed hooks make these three classic bugs **compile errors**.

## 🔴 यह क्यों बना? (Hindi)
`useState(null)` से state का type सिर्फ `null` बन जाता है, इसलिए `setUser({...})` reject होता है। `action: any` वाला reducer `{ type: "typo" }` भी मान लेता है। `inputRef.current.focus()` तब crash होता है जब ref अभी attach नहीं हुआ। Typed hooks ये तीनों पुराने bugs **compile error** बना देते हैं।

---

## 🟢 How it Works — Step by Step
Step 1 → `useState(init)` infers `T` from `init`; use `useState<T | null>(null)` for "empty then loaded" states.
Step 2 → The setter is `Dispatch<SetStateAction<T>>`: accepts a value or `(prev: T) => T`.
Step 3 → `useReducer(reducer, init)` infers state and action from the reducer's parameter types.
Step 4 → Model actions as a discriminated union on `type`; `switch` + `never` check gives exhaustiveness.
Step 5 → `useRef<HTMLElement>(null)` returns `RefObject<HTMLElement | null>` - optional-chain `.current?.`.
Step 6 → `useRef<number>(0)` is a mutable box for values that must not trigger a re-render (timers, previous value).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `useState(init)` में `T` init से infer होता है; "पहले खाली फिर load" वाली state के लिए `useState<T | null>(null)` लिखो।
Step 2 → Setter `Dispatch<SetStateAction<T>>` है: value या `(prev: T) => T` दोनों मान लेता है।
Step 3 → `useReducer(reducer, init)` में state और action reducer के parameter types से infer होते हैं।
Step 4 → Actions को `type` पर discriminated union बनाओ; `switch` + `never` check से exhaustiveness मिलती है।
Step 5 → `useRef<HTMLElement>(null)` `RefObject<HTMLElement | null>` देता है - `.current?.` optional chaining से use करो।
Step 6 → `useRef<number>(0)` mutable box है, उन values के लिए जो re-render trigger न करें (timers, पिछली value)।

---

## 🟡 Real World Example
**Paytm checkout**: a `useState<Wallet | null>(null)` holds the loaded wallet; a `useReducer` drives the payment steps (`idle -> processing -> success/failed`); a `useRef<HTMLInputElement>` focuses the UPI-ID box when validation fails; a `useRef<number>` keeps the retry timer id.

## 🟡 Real Example Hindi mein
**Paytm checkout**: `useState<Wallet | null>(null)` load हुआ wallet रखती है; `useReducer` payment steps चलाता है (`idle -> processing -> success/failed`); validation fail होने पर `useRef<HTMLInputElement>` UPI-ID box पर focus करता है; `useRef<number>` retry timer का id रखता है।

---

## 💻 Code Example — Basic

```tsx
// hooks-basic.tsx
import { useRef, useState } from "react"; // the hooks we need

interface Wallet { balance: number; owner: string } // data shape for the wallet

export function WalletBox() {
  const [count, setCount] = useState(0);                    // inferred: number
  const [wallet, setWallet] = useState<Wallet | null>(null); // explicit: starts null, later Wallet
  const [tags, setTags] = useState<string[]>([]);            // [] alone would infer never[], so annotate
  const inputRef = useRef<HTMLInputElement>(null);           // DOM ref: current is HTMLInputElement | null
  const renders = useRef(0);                                 // mutable box: MutableRef<number> (no re-render)
  renders.current += 1;                                       // allowed: number box is writable

  const load = () => setWallet({ balance: 500, owner: "Asha" }); // set a Wallet
  const add = () => {
    setCount((prev) => prev + 1);            // functional update: prev is number
    setTags((prev) => [...prev, "new"]);      // prev is string[]
    inputRef.current?.focus();                // ?. because current may be null
  };

  return (
    <div>
      <input ref={inputRef} />                {/* attach ref to the DOM node */}
      <button onClick={add}>+{count}</button>
      <button onClick={load}>Load</button>
      <p>{wallet ? `${wallet.owner}: ₹${wallet.balance}` : "no wallet"} {tags.length} {renders.current}</p>
    </div>
  );
}
```

## 💻 Code Example — Advanced

```tsx
// hooks-advanced.tsx — useReducer with a discriminated union + exhaustiveness
import { useReducer, useRef, useEffect } from "react";

// State machine for a payment: each status carries only its own data
type PayState =
  | { status: "idle" }
  | { status: "processing"; amount: number }
  | { status: "success"; txnId: string }
  | { status: "failed"; reason: string };

// Actions: discriminated by `type`
type PayAction =
  | { type: "START"; amount: number }
  | { type: "SUCCESS"; txnId: string }
  | { type: "FAIL"; reason: string }
  | { type: "RESET" };

// Helper that makes the compiler complain if a case is forgotten
function assertNever(x: never): never { throw new Error(`Unhandled: ${JSON.stringify(x)}`); }

// Pure reducer: (state, action) => state
function reducer(state: PayState, action: PayAction): PayState {
  switch (action.type) {
    case "START":   return { status: "processing", amount: action.amount }; // action.amount is number here
    case "SUCCESS": return { status: "success", txnId: action.txnId };      // action.txnId is string here
    case "FAIL":    return { status: "failed", reason: action.reason };
    case "RESET":   return { status: "idle" };
    default:        return assertNever(action);                              // error if a new action is not handled
  }
}

export function Checkout() {
  const [state, dispatch] = useReducer(reducer, { status: "idle" }); // state: PayState, dispatch: Dispatch<PayAction>
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined); // works in browser AND node typings

  useEffect(() => {
    if (state.status === "processing") {                                         // narrowed: state.amount exists
      timer.current = setTimeout(() => dispatch({ type: "SUCCESS", txnId: `T${state.amount}` }), 500);
    }
    return () => clearTimeout(timer.current);                                    // cleanup the timer
  }, [state]);

  return (
    <div>
      <button onClick={() => dispatch({ type: "START", amount: 499 })}>Pay</button>
      {state.status === "success" && <p>Paid {state.txnId}</p>}   {/* txnId only on success */}
      {state.status === "failed" && <p>{state.reason}</p>}        {/* reason only on failed */}
    </div>
  );
}
```

---

## 🟠 Node/Express + React Integration

```tsx
// A reusable typed data-loading hook talking to an Express endpoint
import { useEffect, useState } from "react";

// Generic: caller decides T, we return a precise union
type AsyncState<T> = { loading: true } | { loading: false; error: string } | { loading: false; error?: undefined; data: T };

export function useApi<T>(url: string): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ loading: true }); // start in loading
  useEffect(() => {
    const ac = new AbortController();                                      // cancel on unmount
    fetch(url, { signal: ac.signal })
      .then((r) => r.json() as Promise<T>)                                 // trust-cast: validate with zod in real code
      .then((data) => setState({ loading: false, data }))                  // success branch
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;  // ignore cancel
        setState({ loading: false, error: e instanceof Error ? e.message : "failed" });
      });
    return () => ac.abort();                                               // cleanup
  }, [url]);
  return state;
}

interface Order { id: number; amount: number }
export function Orders() {
  const s = useApi<Order[]>("/api/orders");              // Express: app.get("/api/orders", ...)
  if (s.loading) return <p>...</p>;                      // narrowed
  if (s.error !== undefined) return <p>{s.error}</p>;    // narrowed to error variant
  return <p>{s.data.length} orders</p>;                  // data: Order[]
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `useState(null)` without a type argument
```tsx
// ❌ WRONG
import { useState } from "react";
export const A = () => {
  const [u, setU] = useState(null);
  setU({ name: "x" });
  // error TS2353: Object literal may only specify known properties, and 'name' does not exist in type '(prevState: null) => null'.
  return null;
};
```
✅ Correct: `useState<{ name: string } | null>(null)`.

❌ Mistake 2: Using a DOM ref without a null check
```tsx
// ❌ WRONG
import { useRef } from "react";
export const A = () => {
  const r = useRef<HTMLInputElement>(null);
  r.current.focus();
  // error TS18047: 'r.current' is possibly 'null'.
  return null;
};
```
✅ Correct: `r.current?.focus()`.

❌ Mistake 3: Writing the wrong type into a ref box
```tsx
// ❌ WRONG
import { useRef } from "react";
export const A = () => {
  const r2 = useRef<number>(0);
  r2.current = "x";
  // error TS2322: Type 'string' is not assignable to type 'number'.
  return null;
};
```

❌ Mistake 4: Dispatching an invalid action
```tsx
// ❌ WRONG
import { useReducer } from "react";
type Act = { type: "inc" } | { type: "add"; n: number };
export const A = () => {
  const [s, d] = useReducer((s: number, a: Act) => s, 0);
  d({ type: "add" });
  // error TS2345: Argument of type '{ type: "add"; }' is not assignable to parameter of type 'Act'.
  //   Property 'n' is missing in type '{ type: "add"; }' but required in type '{ type: "add"; n: number; }'.
  d({ type: "zzz" });
  // error TS2322: Type '"zzz"' is not assignable to type '"inc" | "add"'.
  return s;
};
```

---

## 🧠 Tricky Interview Question

```tsx
// ❌ Why does this fail?
import { useState } from "react";
export const A = () => {
  const [items, setItems] = useState([]);
  setItems(["biryani"]);
  // error TS2322: Type 'string' is not assignable to type 'never'.
  return null;
};
```
**Answer:** `useState([])` infers the state as `never[]` (an empty array literal has no element type under `strict`), so any element you try to add is rejected as "not assignable to `never`". Fix: `useState<string[]>([])`. Rule: **empty array or `null` initial values always need an explicit type argument.**

---

## ⚫ Interview Questions + Answers

Q1: When can you skip the generic on `useState`?
A1: When the initial value is a complete example of the type (`0`, `""`, `false`, a full object). You need it for `null`, `undefined`, `[]`, or unions.

Q2: Difference between `useRef<HTMLDivElement>(null)` and `useRef<number>(0)`?
A2: The first gives a read-only-to-you DOM ref whose `.current` is `T | null` (React sets it). The second is a mutable box you write to freely and that never causes a re-render.

Q3: Why model reducer actions as a discriminated union?
A3: Inside each `case`, TS narrows `action` so only that action's payload fields exist, and `default: assertNever(action)` fails the build when someone adds an action but forgets the reducer branch.

Q4: Type of the timer id?
A4: Use `ReturnType<typeof setTimeout>` - it is `number` in the DOM lib and `NodeJS.Timeout` with `@types/node`. Hard-coding `number` breaks in mixed setups.

Q5: How do you type a lazy initial state?
A5: `useState<Cart>(() => loadFromStorage())` - the initializer function returns `Cart`; use it to avoid parsing localStorage on every render.

---

## 🔷 When to Use + When Not to Use
✅ Use `useReducer` when:
- Next state depends on several fields / actions (payment, wizard, cart)
- You want a state machine with discriminated-union states

❌ Avoid:
- `useReducer` for one boolean (`useState` is simpler)
- `useRef` for values the UI must show (changes do not re-render)
- Fighting inference: do not write `useState<number>(0)` when `useState(0)` is enough

---

## 📊 Visual Diagram
```
useState<T>(init) ─► [T, Dispatch<SetStateAction<T>>]
useReducer(r, s0) ─► [S, Dispatch<A>]      S,A inferred from r(state:S, action:A)
useRef<T>(null)   ─► RefObject<T | null>   (DOM; use ?.)
useRef<T>(init)   ─► RefObject<T>          (mutable box)

 action {type:"START"} ──► reducer switch ──► new PayState
                              └─ default: assertNever(action)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type argument | `<T>` passed to a generic hook | hook को दिया गया `<T>` |
| SetStateAction | Value or updater function | value या updater function |
| Reducer | Pure `(state, action) => state` | शुद्ध function: state + action से नई state |
| RefObject | Object with `.current` | `.current` वाला object |
| Exhaustiveness | All union cases handled | union के सारे cases handle |
| Lazy init | Initial state from a function | function से initial state |

---

## ⚡ 3-Line Summary
English:
1. Let inference work for complete initial values; add `<T>` for `null`, `[]` and unions.
2. Type reducers with state + discriminated-union actions and an `assertNever` default.
3. DOM refs are `T | null` (use `?.`); value refs are mutable boxes that never re-render.

Hindi:
1. पूरी initial value हो तो inference पर छोड़ो; `null`, `[]` और unions के लिए `<T>` दो।
2. Reducer को state + discriminated-union actions और `assertNever` default के साथ type करो।
3. DOM ref `T | null` होता है (`?.` लगाओ); value ref mutable box है जो re-render नहीं करता।

---

## ➡️ Next Topic
**92. Typing React Context and Custom Hooks** — safe context without `undefined` checks everywhere.
