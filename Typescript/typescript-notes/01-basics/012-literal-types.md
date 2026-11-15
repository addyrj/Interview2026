# 12. Literal Types
# हिंदी में: Literal Types (सटीक मान वाले types)

> TypeScript 5.x | `satisfies` = TS 4.9+ | Template literal types = TS 4.1+

---

## 🔵 Simple Definition (English)
A **literal type** is a type that allows exactly ONE specific value, such as `'placed'`, `42` or `true`. Instead of saying "this is a `string`", you say "this is exactly the string `'placed'`". Combine several literals with `|` (union) and you get a small, closed set of allowed values, like `'placed' | 'preparing' | 'delivered'`. TypeScript has three kinds: string literals, number literals and boolean literals (plus bigint literals and enum members).

## 🔵 सरल परिभाषा (Hindi)
**Literal type** ऐसा type है जो सिर्फ़ एक सटीक value allow करता है, जैसे `'placed'`, `42` या `true`। "यह कोई भी `string` है" कहने की जगह आप कहते हैं "यह बिल्कुल `'placed'` string है"। कई literals को `|` (union) से जोड़ दो तो एक छोटा, बंद set मिलता है: `'placed' | 'preparing' | 'delivered'`। तीन तरह के literals होते हैं: string, number और boolean (साथ में bigint literals और enum members)।

---

## 🔴 Problem it Solves
A plain `string` accepts typos. If an order status is typed as `string`, then `'delivred'` (typo) or `'CANCELLED'` (a status your backend never sends) compiles fine and breaks at runtime: a `switch` falls to `default`, a Redux reducer ignores the action, a SQL Server `CHECK` constraint rejects the insert. Literal types move these bugs from production to the editor: only the values you listed are legal, autocomplete shows them, and rename-refactoring works across the codebase.

## 🔴 यह क्यों बना? (Hindi)
सादा `string` typo भी accept कर लेता है। अगर order status को `string` type किया है तो `'delivred'` (गलत spelling) या `'CANCELLED'` (जो backend कभी भेजता ही नहीं) भी compile हो जाता है और runtime पर टूटता है: `switch` `default` में चला जाता है, Redux reducer action ignore कर देता है, SQL Server का `CHECK` constraint insert reject कर देता है। Literal types ये bugs production की जगह editor में पकड़ लेते हैं: सिर्फ़ वही values legal हैं जो आपने लिखी हैं, autocomplete उन्हें दिखाता है, और rename-refactor पूरे codebase में चलता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Writing `const status = 'placed'` makes TypeScript infer the literal type `'placed'` (a `const` can never change, so the type is narrow).
Step 2 → Writing `let status = 'placed'` infers the wider type `string` (a `let` can be reassigned, so the type is **widened**).
Step 3 → A union of literals (`'a' | 'b'`) defines a closed set. Assigning anything outside the set gives error TS2322.
Step 4 → Object properties are mutable, so `{ status: 'placed' }` is inferred as `{ status: string }`. Widening happens here too. Fix it with an annotation, `as const`, or `satisfies`.
Step 5 → Control-flow narrowing (`if`, `switch`) removes members from the union one by one, which enables exhaustive checks with `never`.
Step 6 → Template literal types build new literal unions from existing ones: `` `order:${OrderStatus}` ``.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const status = 'placed'` लिखने पर TypeScript literal type `'placed'` infer करता है (`const` कभी बदलता नहीं, इसलिए type narrow रहता है)।
Step 2 → `let status = 'placed'` पर चौड़ा type `string` infer होता है (`let` बदला जा सकता है, इसलिए type **widen** हो जाता है)।
Step 3 → Literals का union (`'a' | 'b'`) एक बंद set बनाता है। set के बाहर कुछ भी assign करने पर error TS2322 आता है।
Step 4 → Object properties mutable होती हैं, इसलिए `{ status: 'placed' }` का type `{ status: string }` बनता है। यहाँ भी widening होती है। इसे annotation, `as const` या `satisfies` से ठीक करो।
Step 5 → Control-flow narrowing (`if`, `switch`) union के members को एक-एक करके हटाती है, जिससे `never` वाले exhaustive checks संभव होते हैं।
Step 6 → Template literal types मौजूदा unions से नए literal unions बनाते हैं: `` `order:${OrderStatus}` ``।

---

## 🟡 Real World Example
**Swiggy's order tracker** moves an order through fixed stages: `placed → preparing → out_for_delivery → delivered` (or `cancelled`). The mobile app, the Node/Express API and the SQL Server `Orders.Status` column must all agree on these exact strings. Modelling the status as a literal union gives one source of truth: a typo in the React component, or a new stage added in the backend without updating the UI reducer, becomes a compile error. HTTP methods (`'GET' | 'POST'`), Razorpay currency (`'INR'`) and sort directions (`'asc' | 'desc'`) are the same idea.

## 🟡 Real Example Hindi mein
**Swiggy का order tracker** order को fixed stages में ले जाता है: `placed → preparing → out_for_delivery → delivered` (या `cancelled`)। Mobile app, Node/Express API और SQL Server का `Orders.Status` column, तीनों को इन्हीं exact strings पर सहमत होना पड़ता है। Status को literal union बनाने से एक ही source of truth मिलता है: React component में typo, या backend में नया stage जोड़ना और UI reducer अपडेट न करना, compile error बन जाता है। HTTP methods (`'GET' | 'POST'`), Razorpay currency (`'INR'`) और sort direction (`'asc' | 'desc'`) भी यही idea हैं।

---

## 💻 Code Example — Basic

```typescript
// literal-basic.ts  (TypeScript 5.x, strict mode)

// A union of string literals: the ONLY legal order statuses
type OrderStatus = 'placed' | 'preparing' | 'out_for_delivery' | 'delivered' | 'cancelled';

// const => the type is the literal 'placed', not string
const first = 'placed';          // type: "placed"
// let => widened to string, because it can be reassigned
let second = 'placed';           // type: string

// Annotating with the union keeps the variable narrow but reassignable
let current: OrderStatus = 'placed'; // ok: 'placed' is in the set
current = 'delivered';               // ok: 'delivered' is in the set

// A number literal union: HTTP status codes we handle
type HandledStatusCode = 200 | 201 | 400 | 404 | 500;
// A boolean literal: this flag can only ever be true
type AlwaysTrue = true;

// Function parameter restricted to a closed set
function label(status: OrderStatus): string {
  // Narrowing: inside each case TypeScript knows the exact literal
  switch (status) {
    case 'placed': return 'Order received';
    case 'preparing': return 'Restaurant is cooking';
    case 'out_for_delivery': return 'Partner is on the way';
    case 'delivered': return 'Enjoy your meal';
    case 'cancelled': return 'Order cancelled';
  }
}

// Using the helpers so nothing is unused
const code: HandledStatusCode = 201;
const flag: AlwaysTrue = true;
console.log(first, second, current, code, flag);
console.log(label(current));
```

Run with `npx tsx literal-basic.ts`. Real output:
```
placed placed delivered 201 true
Enjoy your meal
```

## 💻 Code Example — Advanced

```typescript
// literal-advanced.ts  (TypeScript 5.x)

// Source of truth is a runtime array; the type is DERIVED from it
const STATUSES = ['placed', 'preparing', 'delivered'] as const; // readonly tuple of literals
type OrderStatus = (typeof STATUSES)[number];                   // "placed" | "preparing" | "delivered"

// Template literal type: builds "order:placed" | "order:preparing" | "order:delivered"
type OrderEvent = `order:${OrderStatus}`;

// Event name -> handler map is fully checked
const handlers: Record<OrderEvent, (id: number) => string> = {
  'order:placed': (id) => `#${id} placed`,
  'order:preparing': (id) => `#${id} preparing`,
  'order:delivered': (id) => `#${id} delivered`,
};

// Runtime type guard that bridges unknown JSON (API / DB) into the literal union
function isOrderStatus(value: unknown): value is OrderStatus {
  return typeof value === 'string' && (STATUSES as readonly string[]).includes(value);
}

// Overloads using literals: the return type depends on the literal argument
function fetchOrders(kind: 'count'): number;
function fetchOrders(kind: 'list'): string[];
function fetchOrders(kind: 'count' | 'list'): number | string[] {
  return kind === 'count' ? 2 : ['#1', '#2'];
}

// satisfies (TS 4.9+): checks the shape but KEEPS the literal types
const routes = {
  track: { method: 'GET', path: '/orders/:id' },
  cancel: { method: 'POST', path: '/orders/:id/cancel' },
} satisfies Record<string, { method: 'GET' | 'POST'; path: string }>;

const m: 'GET' = routes.track.method; // still the literal 'GET', not string

const raw: unknown = 'preparing';       // pretend this came from SQL Server
if (isOrderStatus(raw)) {
  console.log(handlers[`order:${raw}`](101)); // raw is OrderStatus here
}
console.log(fetchOrders('count'), fetchOrders('list'), m);
```

Run with `npx tsx literal-advanced.ts`. Real output:
```
#101 preparing
2 [ '#1', '#2' ] GET
```

---

## 🟠 Node/Express + React Integration

```tsx
// shared/order.ts: one file imported by BOTH the Express API and the React app
export const ORDER_STATUSES = ['placed', 'preparing', 'delivered'] as const;
export type OrderStatus = (typeof ORDER_STATUSES)[number];

// api/orders.ts  (Express + mssql style)
import express from 'express';
const app = express();
app.use(express.json());

// Express does not know req.body shape, so we validate and narrow ourselves
app.patch('/orders/:id/status', (req, res) => {
  const next: unknown = req.body.status;               // untrusted input
  if (typeof next !== 'string' || !(ORDER_STATUSES as readonly string[]).includes(next)) {
    res.status(400).json({ error: 'Invalid status' });  // reject unknown strings
    return;
  }
  const status = next as OrderStatus;                   // safe: we just checked it
  // UPDATE Orders SET Status = @status WHERE Id = @id   (SQL Server)
  res.json({ id: req.params.id, status });
});

// store/orderSlice.ts  (Redux Toolkit)
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface OrderState { status: OrderStatus }
const initialState: OrderState = { status: 'placed' };  // literal checked by the annotation

export const orderSlice = createSlice({
  name: 'order',
  initialState,
  reducers: {
    // payload is the closed union, so dispatch(statusChanged('typo')) fails to compile
    statusChanged(state, action: PayloadAction<OrderStatus>) {
      state.status = action.payload;
    },
  },
});

// components/StatusBadge.tsx  (React)
const COLORS: Record<OrderStatus, string> = {  // adding a new status forces you to add a color
  placed: 'gray',
  preparing: 'orange',
  delivered: 'green',
};
export function StatusBadge({ status }: { status: OrderStatus }) {
  return <span style={{ color: COLORS[status] }}>{status}</span>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Object properties get widened to `string`
```typescript
type OrderStatus = 'placed' | 'preparing' | 'delivered';
function track(x: OrderStatus) { console.log(x); }

// ❌ Wrong: property 'status' is inferred as string, not 'placed'
const o = { status: 'placed' };
track(o.status);
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'OrderStatus'.
```
```typescript
type OrderStatus = 'placed' | 'preparing' | 'delivered';
function track(x: OrderStatus) { console.log(x); }

// ✅ Right: as const freezes the literal (or annotate: const o: { status: OrderStatus })
const o = { status: 'placed' } as const;
track(o.status); // ok
```

❌ Mistake 2: Value outside the set
```typescript
type OrderStatus = 'placed' | 'preparing' | 'delivered';
// ❌ Wrong: 'cancelled' was never added to the union
let s: OrderStatus = 'cancelled';
// error TS2322: Type '"cancelled"' is not assignable to type 'OrderStatus'.
type Dice = 1 | 2 | 3;
const d: Dice = 4;
// error TS2322: Type '4' is not assignable to type 'Dice'.
```
✅ Correct: add the member to the union (`| 'cancelled'`), and the compiler then points to every `switch` and `Record` that must handle it.

❌ Mistake 3: Using `let` and expecting a literal. `let method = 'GET'` is `string`, so `fetch(url, { method })` is fine but your own `(m: 'GET' | 'POST')` function rejects it. Use `const`, or annotate `let method: 'GET' | 'POST' = 'GET'`.

---

## 🧠 Tricky Interview Question

```typescript
const a = 'x';
let b = 'x';
const arr = [a];
const obj = { a };

type TA = typeof a;      // ?
type TB = typeof b;      // ?
type TArr = typeof arr;  // ?
type TObj = typeof obj;  // ?
```
Answer: `TA` is `"x"` (const keeps the literal). `TB` is `string` (let widens). `TArr` is `string[]` and `TObj` is `{ a: string }`. When a literal type is placed inside a mutable location (array element, object property) TypeScript widens it, because you could later push or assign another string. A `const` variable holding a literal has a "fresh/non-widening" type only on the variable itself. Use `as const` (`['x'] as const` gives `readonly ["x"]`) or `satisfies` to prevent widening.

---

## ⚫ Interview Questions + Answers

Q1: What is a literal type and how is it different from `string`?
A1: A literal type contains exactly one value (`'placed'`), while `string` contains every possible string. `'placed'` is a subtype of `string`, so it can be assigned to `string` but not the other way round. Unions of literals model closed sets such as status codes, HTTP methods or Redux action types.

Q2: Why does `const x = 'a'` have type `"a"` but `let x = 'a'` has type `string`?
A2: TypeScript infers the most useful type for how the variable can be used. A `const` can never be reassigned, so the narrow literal is safe. A `let` can be reassigned to another string, so the literal is widened to `string`. You can opt into narrowness with `let x: 'a' | 'b' = 'a'`.

Q3: How do you get a union type from a runtime array so the two never drift apart?
A3: Declare the array with `as const` and index its type: `const S = ['a','b'] as const; type T = (typeof S)[number];`. Now `S` can be used at runtime (validation, dropdown options, `includes`) and `T` at compile time, from a single definition.

Q4: How does a literal union differ from an `enum`?
A4: A literal union is erased at compile time (zero JS output), is structurally typed, and works directly with JSON/API strings. A regular `enum` generates runtime code and string enums are NOT assignable from plain string literals. Most modern codebases prefer literal unions or `as const` objects (see topic 16).

Q5: What does `satisfies` do for literals (TS 4.9+)?
A5: `satisfies` validates a value against a type without changing the inferred type. `{ method: 'GET' } satisfies { method: 'GET' | 'POST' }` checks the value yet keeps `method` as the literal `'GET'`, whereas an annotation would widen it to the whole union and `as const` would add `readonly`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A value comes from a small fixed set: statuses, roles, HTTP methods, sort order, Redux action `type`s, feature flags
- You want autocomplete and compile-time checking of magic strings
- You need discriminated unions (a literal `type` / `kind` field) in topic 26

❌ Avoid when:
- The set is large or changes at runtime (country codes loaded from a DB). Use `string` plus runtime validation
- Values are free text such as names or addresses
- You need to iterate over values at runtime AND don't want a second definition. Derive the type from an `as const` array instead of hand-writing the union

---

## 📊 Visual Diagram
```
 string  (all strings)
 ┌──────────────────────────────────────────────┐
 │                                              │
 │   OrderStatus = 'placed' | 'preparing' | ... │
 │   ┌──────────────────────────────────────┐   │
 │   │ 'placed'   'preparing'   'delivered' │   │
 │   └──────────────────────────────────────┘   │
 │        ▲                                     │
 │        │ const s = 'placed'  -> "placed"     │
 │        │ let   s = 'placed'  -> string       │
 └──────────────────────────────────────────────┘
 'cancelled' is a string but NOT in OrderStatus  -> TS2322
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Literal type | Type with exactly one value | सिर्फ़ एक value वाला type |
| Union of literals | Closed set of allowed values | Allowed values का बंद set |
| Widening | `'a'` becoming `string` in mutable places | Literal का `string` बन जाना |
| Narrowing | Shrinking a union via checks | Checks से union छोटा करना |
| `as const` | Keeps literals and adds readonly | Literals को freeze करता है |
| Template literal type | String type built from other literals | Literals से बना string type |

---

## ⚡ 3-Line Summary
English:
1. A literal type allows exactly one value; unions of literals give you a closed set such as `'placed' | 'delivered'`.
2. `const` keeps the literal, `let` and object properties widen to `string`; fix with annotations, `as const` or `satisfies`.
3. Derive the union from an `as const` array so runtime list and compile-time type share one source of truth.

Hindi:
1. Literal type सिर्फ़ एक value allow करता है; literals का union `'placed' | 'delivered'` जैसा बंद set देता है।
2. `const` literal रखता है, `let` और object properties `string` में widen हो जाते हैं; annotation, `as const` या `satisfies` से ठीक करो।
3. Union को `as const` array से derive करो ताकि runtime list और compile-time type की एक ही source of truth रहे।

---

## ➡️ Next Topic
**13. Type Aliases** — naming any type (unions, objects, functions, tuples) with the `type` keyword so you can reuse it everywhere.
