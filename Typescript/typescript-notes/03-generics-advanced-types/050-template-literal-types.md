# 50. Template Literal Types
# हिंदी में: Template Literal Types (string types जोड़ना और parse करना)

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). Template literal types TS 4.1 से; intrinsic `Uppercase/Lowercase/Capitalize/Uncapitalize` भी TS 4.1 से।

---

## 🔵 Simple Definition (English)
A **template literal type** uses JavaScript template syntax at the type level: `` `user_${string}` `` or `` `${Method} ${Path}` ``. It builds new string literal types from other string-like types. With unions it expands to every combination (a cross product), and together with `infer` it can **parse** strings, so route params or event names become typed.

## 🔵 सरल परिभाषा (Hindi)
**Template literal type** JavaScript की template syntax को type level पर इस्तेमाल करता है: `` `user_${string}` `` या `` `${Method} ${Path}` ``। यह दूसरे string types से नए string literal types बनाता है। Unions के साथ यह हर combination (cross product) बना देता है, और `infer` के साथ strings को **parse** भी कर सकता है, इसलिए route params और event names typed हो जाते हैं।

---

## 🔴 Problem it Solves
Event names (`onClick`, `onSubmit`), CSS classes (`btn-primary`), API routes (`GET /orders/:id`), Redux action types (`cart/add`) are strings, so TypeScript used to accept any `string`. Typos like `"cart/ad"` only fail at runtime. Writing every legal combination by hand (`"GET /orders" | "POST /orders" | ...`) does not scale. Template literal types make string formats part of the type system.

## 🔴 यह क्यों बना? (Hindi)
Event names (`onClick`), CSS classes (`btn-primary`), API routes (`GET /orders/:id`), Redux action types (`cart/add`) सब strings हैं, इसलिए TypeScript कोई भी `string` मान लेता था। `"cart/ad"` जैसा typo runtime पर ही पकड़ में आता। हर legal combination हाथ से लिखना (`"GET /orders" | "POST /orders" | ...`) scale नहीं करता। Template literal types string formats को type system का हिस्सा बना देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Write backticks in a type: `` type Id = `ord_${number}` ``. Matches `"ord_1"`, `"ord_42.5"`, not `"ord_x"`.
Step 2 → Interpolate unions: `` `${"GET" | "POST"} /orders` `` becomes `"GET /orders" | "POST /orders"`.
Step 3 → Two unions multiply: 3 methods x 4 paths = 12 members (watch the 100,000 member limit, TS2590).
Step 4 → Intrinsic helpers: `Uppercase<S>`, `Lowercase<S>`, `Capitalize<S>`, `Uncapitalize<S>`.
Step 5 → Parse with `infer`: `` S extends `${infer Head}/${infer Tail}` `` splits at the first `/`. `infer` against `string` takes the shortest match for the first slot.
Step 6 → Combine with mapped types and `as` to rename keys (`getName`, `onClick`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Type में backticks लिखो: `` type Id = `ord_${number}` ``। `"ord_1"` match, `"ord_x"` नहीं।
Step 2 → Unions interpolate करो: `` `${"GET" | "POST"} /orders` `` से `"GET /orders" | "POST /orders"` बनता है।
Step 3 → दो unions गुणा होते हैं: 3 methods x 4 paths = 12 members (100,000 members की सीमा, TS2590)।
Step 4 → Intrinsic helpers: `Uppercase<S>`, `Lowercase<S>`, `Capitalize<S>`, `Uncapitalize<S>`।
Step 5 → `infer` से parse करो: `` S extends `${infer Head}/${infer Tail}` `` पहले `/` पर तोड़ता है।
Step 6 → Mapped types और `as` के साथ keys rename करो (`getName`, `onClick`)।

---

## 🟡 Real World Example
**Razorpay's** webhook events look like `payment.captured`, `payment.failed`, `order.paid`, `refund.processed`. Instead of one giant union, the team defines `Entity = "payment" | "order" | "refund"` and `Action = ...` and builds `` `${Entity}.${string}` ``. The handler registry `on("payment.captured", fn)` is then autocompleted and wrong event names do not compile. For REST routes, a typed router extracts `:orderId` from `/orders/:orderId` at compile time so `req.params.orderId` exists.

## 🟡 Real Example Hindi mein
**Razorpay** के webhook events ऐसे दिखते हैं: `payment.captured`, `payment.failed`, `order.paid`, `refund.processed`। एक बड़ा union लिखने की जगह team `Entity = "payment" | "order" | "refund"` बनाती है और `` `${Entity}.${string}` `` से type बनाती है। फिर `on("payment.captured", fn)` में autocomplete मिलता है और गलत event name compile नहीं होता। REST routes में typed router `/orders/:orderId` से `:orderId` compile time पर निकाल लेता है, इसलिए `req.params.orderId` मौजूद होता है।

---

## 💻 Code Example — Basic

```typescript
// 1) Pattern with a placeholder: any string starting with ord_
type OrderId = `ord_${string}`;
const ok: OrderId = "ord_123"; // OK
// const bad: OrderId = "pay_123"; // would be an error

// 2) Union cross product
type Method = "GET" | "POST";
type Path = "/orders" | "/cart";
type Endpoint = `${Method} ${Path}`; // 4 combinations
const ep: Endpoint = "POST /cart"; // OK

// 3) Intrinsic string helpers
type Evt = "click" | "submit";
type Handler = `on${Capitalize<Evt>}`; // "onClick" | "onSubmit"
type Loud = Uppercase<Evt>; // "CLICK" | "SUBMIT"
const h: Handler = "onSubmit";
const l: Loud = "CLICK";

// 4) number and boolean placeholders
type Version = `v${number}`; // "v1", "v2.5"
type Flag = `feature_${boolean}`; // "feature_true" | "feature_false"
const v: Version = "v2";
const f: Flag = "feature_true";

console.log(ok, ep, h, l, v, f); // ord_123 POST /cart onSubmit CLICK v2 feature_true
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: extract :params from a route (parsing with infer)
type RouteParams<S extends string> = S extends `${string}:${infer P}/${infer Rest}`
  ? { [K in P | keyof RouteParams<`/${Rest}`>]: string } // this param plus params in the rest
  : S extends `${string}:${infer P}`
    ? { [K in P]: string } // last param
    : {}; // no params
type P1 = RouteParams<"/orders/:orderId/items/:itemId">; // { orderId: string; itemId: string }
const p1: P1 = { orderId: "o1", itemId: "i9" };

// Advanced 2: typed route function: params required only if the route has them
function buildUrl<S extends string>(route: S, params: RouteParams<S>): string {
  let url: string = route; // start from template
  for (const [k, v] of Object.entries(params as Record<string, string>)) {
    url = url.replace(`:${k}`, encodeURIComponent(v)); // substitute each param
  }
  return url;
}
console.log(buildUrl("/orders/:orderId/items/:itemId", p1)); // /orders/o1/items/i9

// Advanced 3: snake_case <-> camelCase on string literal types
type Camel<S extends string> = S extends `${infer A}_${infer B}` ? `${A}${Capitalize<Camel<B>>}` : S;
type Snake<S extends string> = S extends `${infer H}${infer T}`
  ? `${H extends Lowercase<H> ? H : `_${Lowercase<H>}`}${Snake<T>}`
  : S;
type C1 = Camel<"order_total_amount">; // "orderTotalAmount"
type S1 = Snake<"orderTotalAmount">; // "order_total_amount"
const c1: C1 = "orderTotalAmount";
const s1: S1 = "order_total_amount";

// Advanced 4: typed event emitter, listener names derived from keys
type Events = { paid: { id: string }; failed: { reason: string } };
type Listeners<E> = { [K in keyof E & string as `on${Capitalize<K>}`]: (p: E[K]) => void };
const listeners: Listeners<Events> = {
  onPaid: (p) => console.log("paid", p.id), // p is { id: string }
  onFailed: (p) => console.log("failed", p.reason), // p is { reason: string }
};
listeners.onPaid({ id: "o1" }); // paid o1
console.log(c1, s1); // orderTotalAmount order_total_amount
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: typed registry of "METHOD /path" keys so route table typos fail at compile time
import express from "express";

type Verb = "get" | "post" | "delete";
type RouteKey = `${Uppercase<Verb>} /${string}`; // "GET /orders", "POST /cart"

const routes: Record<RouteKey, string> = {
  "GET /orders": "list orders",
  "POST /orders": "create order",
  "DELETE /orders/:id": "cancel order",
};

const app = express();
for (const [key, desc] of Object.entries(routes)) {
  const [verb, path] = key.split(" ") as [Uppercase<Verb>, string]; // split key
  app[verb.toLowerCase() as Verb](path, (_req, res) => { res.json({ desc }); }); // register
}
```

```tsx
// React: design-system prop that accepts only valid class tokens
import type { ReactNode } from "react";

type Size = "sm" | "md" | "lg";
type Tone = "primary" | "danger";
type ClassName = `btn-${Tone}-${Size}`; // 6 valid class names

interface Props {
  className: ClassName; // restricts to the valid set
  children: ReactNode; // button label
}
export const Btn = ({ className, children }: Props) => <button className={className}>{children}</button>;

export const Demo = () => <Btn className="btn-danger-sm">Cancel</Btn>; // "btn-danger-xl" would be an error
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using an unsupported type in `${}`
```typescript
// ❌ Wrong
type Bad = `id_${{ a: 1 }}`;
// error TS2322: Type '{ a: 1; }' is not assignable to type 'string | number | bigint | boolean | null | undefined'.
```

❌ Mistake 2: Assigning a string that does not match the pattern
```typescript
// ❌ Wrong
type OrderId = `ord_${number}`;
const id: OrderId = "ord_abc";
// error TS2322: Type '"ord_abc"' is not assignable to type '`ord_${number}`'.
```

❌ Mistake 3: Union explosion
```typescript
// ❌ Wrong
type D = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";
type Big = `${D}${D}${D}${D}${D}${D}`; // 1,000,000 members
// error TS2590: Expression produces a union type that is too complex to represent.
// ✅ Right: use `${number}` or a pattern like `${string}-${string}`
```

---

## 🧠 Tricky Interview Question

```typescript
type Split<S extends string> = S extends `${infer A}.${infer B}` ? [A, B] : [S];
type X = Split<"a.b.c">;
```
**What is `X`?**

Answer: `["a", "b.c"]`. With two `infer` slots, TypeScript assigns the **shortest possible match to the first slot** and puts the rest in the last one, so the string is split only at the first `.`. For a full split you recurse: `` S extends `${infer A}.${infer B}` ? [A, ...Split<B>] : [S] `` which gives `["a","b","c"]`. This is a classic type-challenge.

---

## ⚫ Interview Questions + Answers

Q1: What are template literal types and when were they added?
A1: String literal types built with backticks and `${}` placeholders, added in TS 4.1. They compute new string types from unions and other string-like types.

Q2: What can go inside `${}` in a type?
A2: `string`, `number`, `bigint`, `boolean`, `null`, `undefined`, literal types and unions of these. Objects or arrays are errors.

Q3: How do unions behave inside a template literal?
A3: They distribute as a cross product: `` `${"a"|"b"}-${1|2}` `` yields four strings. Beware very large products (TS2590).

Q4: How do you extract route params with types?
A4: Use `infer` with recursion on `` `${string}:${infer P}/${infer Rest}` `` as in `RouteParams` above. Libraries like Express's typed `RouteParameters` do the same, which is why `req.params.id` is typed when the path is a literal.

Q5: Which intrinsic string types exist?
A5: `Uppercase`, `Lowercase`, `Capitalize`, `Uncapitalize`. They are compiler built-ins (not definable in userland) and are applied to literal types and unions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Naming conventions are part of the contract (event names, action types, CSS tokens, ids)
- Parsing route or key strings (`:id`, `a.b.c` paths, snake to camel)
- Generating handler or getter names with mapped types

❌ Avoid when:
- A runtime parser is needed anyway and types add no safety
- The cross product is huge; use `string` plus runtime validation
- Parsing deeply nested grammar; compile time and error messages degrade

---

## 📊 Visual Diagram
```
  type Endpoint = `${Method} ${Path}`

   Method: GET | POST          Path: /orders | /cart
          \                       /
           ──── cross product ────
   "GET /orders" "GET /cart" "POST /orders" "POST /cart"

  Parsing:  "/orders/:orderId"
      `${string}:${infer P}`  ──►  P = "orderId"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Template literal type | Backtick string type | Backtick वाला string type |
| Cross product | All combinations of unions | Unions के सारे combinations |
| Intrinsic type | Compiler built-in (Uppercase...) | Compiler का built-in type |
| Parsing | Split/extract with infer | infer से तोड़ना/निकालना |
| Key remapping | Rename mapped keys | Keys का नाम बदलना |

---

## ⚡ 3-Line Summary
English:
1. Template literal types build and validate string formats at compile time (TS 4.1+).
2. Unions multiply, intrinsics change case, and `infer` parses strings like routes.
3. Combine with mapped types for typed events, getters, and routers; avoid exploding unions.

Hindi:
1. Template literal types compile time पर string formats बनाते और validate करते हैं (TS 4.1+)।
2. Unions गुणा होते हैं, intrinsics case बदलते हैं, और `infer` routes जैसी strings को parse करता है।
3. Typed events, getters, routers के लिए mapped types के साथ जोड़ो; unions को फटने मत दो।

---

## ➡️ Next Topic
**51. Recursive Types** — खुद को refer करने वाले types (JSON, tree, comments, `DeepPartial`)।
