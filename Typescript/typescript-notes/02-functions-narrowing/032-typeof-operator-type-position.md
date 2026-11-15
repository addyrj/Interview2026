# 32. typeof Operator (type position)
# हिंदी में: `typeof` Operator (type की जगह — value से type निकालना)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`. `import("x")` types and `as const` + `typeof` work on all 5.x.

---

## 🔵 Simple Definition (English)
In JavaScript `typeof x` is a runtime expression returning a string like `"number"`. In a **type position** (after `:`, in `type X = ...`), `typeof value` instead takes a **value and returns its TypeScript type**. It lets you derive types from real objects (config, constants, functions) so that the value is the single source of truth.

## 🔵 सरल परिभाषा (Hindi)
JavaScript में `typeof x` runtime expression है जो `"number"` जैसी string देता है। **Type position** में (`:` के बाद, `type X = ...` में) `typeof value` किसी **value को लेकर उसका TypeScript type** लौटाता है। इससे आप असली objects (config, constants, functions) से types निकालते हैं, ताकि value ही एकमात्र source of truth रहे।

---

## 🔴 Problem it Solves
You write a config object, then write an `interface` describing it by hand, and soon the two drift apart. Or you have a function whose return type you need elsewhere. `typeof` removes the duplication: change the value and every derived type updates, no manual sync.

## 🔴 यह क्यों बना? (Hindi)
आप config object लिखते हो, फिर उसी का `interface` हाथ से लिखते हो, और दोनों धीरे-धीरे अलग हो जाते हैं। या किसी function का return type कहीं और चाहिए। `typeof` duplication हटाता है: value बदलो और हर derived type अपने आप update हो जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Two different `typeof`: the JS one is in expressions (`if (typeof x === "string")`), the TS one is in type positions (`type T = typeof x`).
Step 2 → `type Config = typeof config` takes the INFERRED type of the variable `config`.
Step 3 → Combine with `as const` to get literal, readonly types: `typeof routes` becomes exact strings.
Step 4 → Combine with `keyof`: `keyof typeof routes` is the union of the object's keys (`"home" | "cart"`).
Step 5 → `(typeof arr)[number]` gives the element union of a `const` array (a standard enum alternative).
Step 6 → `ReturnType<typeof fn>` and `Parameters<typeof fn>` extract a function's types.
Step 7 → `typeof` only works on identifiers and property access (`typeof a.b`), not on arbitrary expressions like `typeof fn()`. Use `ReturnType<typeof fn>`.
Step 8 → For classes, `typeof ClassName` is the CONSTRUCTOR type (the static side); `ClassName` alone is the instance type.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → दो अलग `typeof`: JS वाला expressions में (`if (typeof x === "string")`) और TS वाला type positions में (`type T = typeof x`)।
Step 2 → `type Config = typeof config` variable `config` का INFERRED type लेता है।
Step 3 → `as const` के साथ जोड़ो तो literal, readonly types मिलते हैं: `typeof routes` exact strings बन जाता है।
Step 4 → `keyof` के साथ: `keyof typeof routes` object की keys का union है (`"home" | "cart"`)।
Step 5 → `(typeof arr)[number]` `const` array के elements का union देता है (enum का आम विकल्प)।
Step 6 → `ReturnType<typeof fn>` और `Parameters<typeof fn>` function के types निकालते हैं।
Step 7 → `typeof` सिर्फ़ identifiers और property access (`typeof a.b`) पर चलता है, `typeof fn()` जैसे expressions पर नहीं। `ReturnType<typeof fn>` इस्तेमाल करो।
Step 8 → Classes के लिए `typeof ClassName` CONSTRUCTOR type (static side) है; सिर्फ़ `ClassName` instance type है।

---

## 🟡 Real World Example
**Swiggy app config**: a `const config = { apiBase: "...", retries: 3, features: { upi: true } }` lives in one file. Other files need `Config` type for props and tests. `type Config = typeof config` keeps them in sync: add a feature flag to the object and the type updates automatically.

## 🟡 Real Example Hindi mein
**Swiggy app config**: एक file में `const config = { apiBase: "...", retries: 3, features: { upi: true } }` है। दूसरी files को props और tests के लिए `Config` type चाहिए। `type Config = typeof config` दोनों को sync रखता है: object में feature flag जोड़ो तो type अपने आप update हो जाता है।

---

## 💻 Code Example — Basic

```typescript
// A runtime value: the single source of truth
const config = {
  apiBase: "https://api.example.com", // string
  retries: 3, // number
  features: { upi: true, cod: false }, // nested object
};

// Type derived from the VALUE (no hand-written interface)
type Config = typeof config; // { apiBase: string; retries: number; features: { upi: boolean; cod: boolean } }

// Use the derived type for a function parameter
function printBase(c: Config): string {
  return `${c.apiBase} x${c.retries}`; // fully typed access
}
console.log(printBase(config)); // works for the original value

// Deep property access also works in type position
type Features = typeof config.features; // { upi: boolean; cod: boolean }
const f: Features = { upi: false, cod: true }; // valid
console.log(f.cod); // true
```

Run with `npx tsx`:

```
https://api.example.com x3
true
```

## 💻 Code Example — Advanced

```typescript
// Advanced: as const + typeof + keyof for enum-like unions, route tables, and function-derived types

// 'as const' freezes literals and makes everything readonly
const ORDER_STATUS = ["placed", "preparing", "delivered"] as const; // readonly tuple of literals
type OrderStatus = (typeof ORDER_STATUS)[number]; // "placed" | "preparing" | "delivered"

const routes = { home: "/", cart: "/cart", pay: "/pay" } as const; // literal values
type RouteName = keyof typeof routes; // "home" | "cart" | "pay"
type RoutePath = (typeof routes)[RouteName]; // "/" | "/cart" | "/pay"

function go(name: RouteName): RoutePath {
  return routes[name]; // exact literal type returned
}
console.log(go("cart"), ORDER_STATUS.includes("placed")); // /cart true

// Derive types from a function (service layer stays the source of truth)
async function fetchOrder(id: number) {
  return { id, total: 499, status: "placed" as OrderStatus }; // return type is inferred
}
type Order = Awaited<ReturnType<typeof fetchOrder>>; // { id: number; total: number; status: OrderStatus }
type FetchArgs = Parameters<typeof fetchOrder>; // [id: number]

const sample: Order = { id: 1, total: 100, status: "delivered" }; // valid
const args: FetchArgs = [42]; // tuple of params
console.log(sample.status, args[0]); // delivered 42

// typeof on a class gives the constructor type (static side)
class Cart { constructor(public items: string[] = []) {} } // instance has items
type CartCtor = typeof Cart; // new (items?: string[]) => Cart
function make(ctor: CartCtor): Cart { return new ctor(["dosa"]); } // build via constructor type
console.log(make(Cart).items); // [ 'dosa' ]
```

Run with `npx tsx`:

```
/cart true
delivered 42
[ 'dosa' ]
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: derive request/response shapes from a validation schema and a defaults object
import express from "express"; // express
import type { Request, Response } from "express"; // types
import { z } from "zod"; // zod schema library

// Zod schema is a VALUE; z.infer turns it into a type (same idea as typeof)
const OrderBody = z.object({ sku: z.string(), qty: z.number().int().positive() }); // runtime validator
type OrderBody = z.infer<typeof OrderBody>; // derived static type, name reused for value and type

// Defaults object as the single source of truth for options
const defaults = { page: 1, pageSize: 20, sort: "price" as "price" | "rating" }; // typed defaults
type ListOptions = typeof defaults; // { page: number; pageSize: number; sort: "price" | "rating" }

const app = express(); // app
app.use(express.json()); // body parser

app.post("/orders", (req: Request, res: Response) => {
  const parsed = OrderBody.safeParse(req.body); // validate unknown body
  if (!parsed.success) { res.status(400).json(parsed.error.issues); return; } // reject
  const body: OrderBody = parsed.data; // typed from the schema
  const opts: ListOptions = { ...defaults, pageSize: 50 }; // typed from the defaults
  res.json({ sku: body.sku, qty: body.qty, opts }); // respond
});
```

```tsx
// React: derive prop types from a component and a constants object
import type { ComponentProps } from "react"; // helper for props

// A button component
function PayButton(props: { amount: number; label?: string }) {
  return <button>{props.label ?? "Pay"} Rs {props.amount}</button>; // UI
}

// Props derived FROM the component value, no duplicated interface
type PayButtonProps = ComponentProps<typeof PayButton>; // { amount: number; label?: string }

// Theme constants as the source for a union of allowed colors
const theme = { primary: "#5f259f", danger: "#e11d48" } as const; // literal hex values
type ThemeColor = keyof typeof theme; // "primary" | "danger"

export function Badge({ color }: { color: ThemeColor }) {
  return <span style={{ background: theme[color] }}>New</span>; // typed lookup
}

const props: PayButtonProps = { amount: 199 }; // valid props object
export const demo = <PayButton {...props} />; // use it
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Calling a function inside `typeof` (it takes identifiers only).**

```typescript
// ❌ WRONG: typeof cannot take a function call expression
function getUser() { return { id: 1, name: "Asha" }; } // returns an object
type User = typeof getUser(); // ❌ syntax error
```

Real compiler output:

```
error TS1005: ';' expected.
error TS1109: Expression expected.
```

```typescript
// ✅ RIGHT: use ReturnType
function getUser2() { return { id: 1, name: "Asha" }; } // returns an object
type User2 = ReturnType<typeof getUser2>; // { id: number; name: string }
const u: User2 = { id: 2, name: "Ravi" }; // valid
console.log(u.name);
```

**Mistake 2: Forgetting `as const` (types widen to `string`).**

```typescript
// ❌ WRONG: without as const the keys' values widen to string
const routes = { home: "/", cart: "/cart" }; // values are string
type RoutePath = (typeof routes)["home"]; // string, not "/"
const p: RoutePath = "anything"; // accepted
// ✅ FIX: const routes = { home: "/", cart: "/cart" } as const;  -> RoutePath = "/"
console.log(p);
```

**Mistake 3: Using `typeof` on a type (not a value).**

```typescript
// ❌ WRONG: Order is an interface (type only), it does not exist at runtime
interface Order { id: number } // type only
type T = typeof Order; // ❌ error
```

Real compiler output:

```
error TS2693: 'Order' only refers to a type, but is being used as a value here.
```

---

## 🧠 Tricky Interview Question

**Q: A class `Cart` is declared. What is the difference between `Cart` and `typeof Cart` in a type position?**

```typescript
class Cart {
  static taxRate = 0.18; // static member: lives on the class itself
  items: string[] = []; // instance member
}

const instance: Cart = new Cart(); // Cart = instance type
const klass: typeof Cart = Cart; // typeof Cart = the constructor + statics
console.log(instance.items.length, klass.taxRate); // ?
// instance.taxRate;   // ❌ does not exist on the instance type
// klass.items;        // ❌ does not exist on the constructor type
```

Real output with `npx tsx`:

```
0 0.18
```

**Answer:** `Cart` as a type is the **instance** side (properties of `new Cart()`). `typeof Cart` is the type of the class VALUE: the constructor signature plus static members. Passing a class around ("give me a class that builds Carts") needs `typeof Cart` or `new () => Cart`. The two commented lines fail to compile because each member lives on only one side. Real tsc output when uncommented: `error TS2576: Property 'taxRate' does not exist on type 'Cart'. Did you mean to access the static member 'Cart.taxRate' instead?` and `error TS2339: Property 'items' does not exist on type 'typeof Cart'.`

---

## ⚫ Interview Questions + Answers

Q1: How does `typeof` in a type position differ from `typeof` in an expression?
A1: The expression one runs at runtime and returns a string. The type-position one is erased and produces the static type of a value. TypeScript decides by context.

Q2: How do you build a union type from a constant array?
A2: `const A = ["a","b"] as const; type U = (typeof A)[number];` giving `"a" | "b"`, with a runtime array you can also iterate.

Q3: Why can't I write `typeof fn()`?
A3: `typeof` accepts only identifiers and property paths. Use `ReturnType<typeof fn>`, wrapped in `Awaited<>` for async functions.

Q4: `keyof typeof obj` vs `keyof Type`?
A4: `keyof Type` works on an existing type; `typeof obj` first derives the type from a value, then `keyof` gets its keys. You need both when only a value exists.

Q5: Is `typeof` the best way to share types?
A5: Good for config, constants, and Zod/RTK slices (`typeof store.getState`). For public API contracts, explicit interfaces are clearer and give better error messages and fewer accidental changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Constants, config, route tables, and enum-like arrays (`as const`) should drive types
- Extracting function types: `ReturnType`, `Parameters`, `Awaited`
- Redux: `type RootState = ReturnType<typeof store.getState>`

❌ Avoid when:
- A public contract should be explicit and stable (prefer a named interface)
- The value's inferred type is huge or complex (hurts error readability)
- You are tempted to run `typeof` on a type name (does not exist at runtime)

---

## 📊 Visual Diagram
```
 VALUE WORLD (runtime)                TYPE WORLD (compile time)
 ─────────────────────                ─────────────────────────
 const config = {...}   ──typeof──►   type Config
 const A = [..] as const ─(typeof A)[number]► union of elements
 function fn() {...}    ──ReturnType<typeof fn>► return type
 class Cart {...}       ──typeof Cart► constructor + statics
                        └─ Cart       ► instance type
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| typeof (type) | Value to its type | Value से उसका type |
| as const | Literal, readonly inference | Literal, readonly inference |
| Single source of truth | One place defines it | एक ही जगह definition |
| ReturnType | Function return type utility | Function का return type |
| Constructor type | `typeof Class` | Class का constructor type |

---

## ⚡ 3-Line Summary
English:
1. In a type position `typeof value` gives the value's static type.
2. Combine with `as const`, `keyof`, `[number]`, `ReturnType` to derive unions and shapes.
3. It only accepts identifiers; `typeof Class` is the constructor side, not the instance.

Hindi:
1. Type position में `typeof value` value का static type देता है।
2. `as const`, `keyof`, `[number]`, `ReturnType` के साथ unions और shapes निकालो।
3. यह सिर्फ़ identifiers लेता है; `typeof Class` constructor side है, instance नहीं।

---

## ➡️ Next Topic
**33. Indexed Access Types** — read the type of a property with `T["key"]`, including arrays and unions.
