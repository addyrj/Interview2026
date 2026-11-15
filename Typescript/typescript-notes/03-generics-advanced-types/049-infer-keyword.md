# 49. infer Keyword
# हिंदी में: infer Keyword (type को "पकड़ना")

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). `infer` TS 2.8 से; `infer X extends Y` (constraint on infer) TS 4.7 से।

---

## 🔵 Simple Definition (English)
`infer` declares a **type variable inside the `extends` clause of a conditional type** so TypeScript captures whatever type sits in that position. Example: `T extends Promise<infer U> ? U : T` means "if T is a Promise of something, call that something `U` and return it". It is pattern matching for types. `ReturnType`, `Parameters` and `Awaited` are built with it.

## 🔵 सरल परिभाषा (Hindi)
`infer` conditional type के **`extends` हिस्से में एक type variable** बनाता है ताकि TypeScript उस position का जो भी type हो उसे पकड़ ले। उदाहरण: `T extends Promise<infer U> ? U : T` यानी "अगर T किसी चीज़ का Promise है, तो उस चीज़ को `U` कहो और लौटा दो"। यह types के लिए pattern matching है। `ReturnType`, `Parameters`, `Awaited` इसी से बने हैं।

---

## 🔴 Problem it Solves
Your Express service function `getOrder()` returns `Promise<Order>`. In a React hook you want the `Order` type without re-declaring it. Writing `type Order = ...` by hand duplicates and drifts. You need a way to **extract a piece of an existing type**: the resolved value of a Promise, the element of an array, the args of a function, the props of a component.

## 🔴 यह क्यों बना? (Hindi)
आपके Express service function `getOrder()` का return `Promise<Order>` है। React hook में आपको `Order` type चाहिए, दोबारा declare किए बिना। हाथ से `type Order = ...` लिखने पर duplicate होता है और बदलाव पर अलग हो जाता है। चाहिए ऐसा तरीका जो **मौजूदा type का एक हिस्सा निकाल ले**: Promise का resolved value, array का element, function के args, component के props।

---

## 🟢 How it Works — Step by Step

Step 1 → `infer` only works inside the `extends` clause of a conditional type.
Step 2 → Write a pattern: `T extends (...args: any[]) => infer R ? R : never`.
Step 3 → TypeScript tries to match `T` to the pattern. Where `infer R` sits, it **captures** the matching type.
Step 4 → If the match succeeds, `R` is usable in the true branch. If not, the false branch runs.
Step 5 → Multiple infers are allowed: `T extends (infer A)[] | Set<infer A>`; the same name in covariant positions yields a union, in contravariant positions an intersection.
Step 6 → TS 4.7+: constrain the capture, `T extends [infer H extends string, ...unknown[]] ? H : never`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `infer` सिर्फ conditional type के `extends` हिस्से में चलता है।
Step 2 → Pattern लिखो: `T extends (...args: any[]) => infer R ? R : never`।
Step 3 → TypeScript `T` को pattern से match करता है। जहाँ `infer R` है वहाँ का type **capture** हो जाता है।
Step 4 → Match हो गया तो true branch में `R` usable है। नहीं हुआ तो false branch चलती है।
Step 5 → कई infers allowed हैं; एक ही नाम covariant positions में union देता है, contravariant में intersection।
Step 6 → TS 4.7+: capture को constrain करो, `infer H extends string`।

---

## 🟡 Real World Example
**Zomato's** frontend calls `api.getRestaurant(id)` which returns `Promise<Restaurant>`. A Redux thunk's fulfilled payload must be exactly `Restaurant`. Instead of importing and duplicating, the team writes `type Payload = Awaited<ReturnType<typeof api.getRestaurant>>`. Both utilities use `infer` inside. If the API changes its return shape, the Redux slice type changes automatically and wrong usages break at compile time.

## 🟡 Real Example Hindi mein
**Zomato** का frontend `api.getRestaurant(id)` call करता है जो `Promise<Restaurant>` लौटाता है। Redux thunk का fulfilled payload ठीक `Restaurant` होना चाहिए। Import और duplicate करने की जगह team लिखती है `type Payload = Awaited<ReturnType<typeof api.getRestaurant>>`। दोनों utilities अंदर `infer` इस्तेमाल करती हैं। API का return shape बदला तो Redux slice का type अपने आप बदलता है और गलत usage compile time पर टूटता है।

---

## 💻 Code Example — Basic

```typescript
// 1) Extract a function's return type
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// 2) Extract a function's parameter tuple
type MyParameters<T> = T extends (...args: infer P) => any ? P : never;

// 3) Unwrap a Promise (one level)
type Unwrap<T> = T extends Promise<infer U> ? U : T;

// 4) Element type of an array
type Elem<T> = T extends readonly (infer E)[] ? E : never;

interface Order {
  id: string; // order id
  amount: number; // amount
}
async function getOrder(id: string, withItems: boolean): Promise<Order> {
  return { id, amount: withItems ? 500 : 400 }; // fake db call
}

type R = MyReturnType<typeof getOrder>; // Promise<Order>
type P = MyParameters<typeof getOrder>; // [id: string, withItems: boolean]
type U = Unwrap<R>; // Order
type E = Elem<Order[]>; // Order

const args: P = ["ord_1", true]; // tuple parameters, labels preserved
getOrder(...args).then((o: U) => console.log(o.amount)); // 500
const first: E = { id: "x", amount: 1 }; // E is Order
console.log(first.id); // x
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: recursive Awaited-like unwrap (nested promises)
type DeepAwaited<T> = T extends Promise<infer U> ? DeepAwaited<U> : T;
type Z = DeepAwaited<Promise<Promise<number>>>; // number
const z: Z = 42;

// Advanced 2: pick out first and last of a tuple, variadic tuple patterns
type First<T extends unknown[]> = T extends [infer H, ...unknown[]] ? H : never;
type Last<T extends unknown[]> = T extends [...unknown[], infer L] ? L : never;
type Row = [id: number, name: string, active: boolean];
const f: First<Row> = 1; // number
const l: Last<Row> = true; // boolean

// Advanced 3: parse a route string "/orders/:orderId/items/:itemId" (template literal + infer)
type ParamNames<S extends string> = S extends `${string}:${infer Param}/${infer Rest}`
  ? Param | ParamNames<`/${Rest}`> // param followed by more path
  : S extends `${string}:${infer Param}`
    ? Param // last param
    : never;
type Params = ParamNames<"/orders/:orderId/items/:itemId">; // "orderId" | "itemId"
const pn: Params = "itemId";

// Advanced 4: infer with constraint (TS 4.7+): only accept string heads
type HeadString<T> = T extends [infer H extends string, ...unknown[]] ? H : never;
type HS = HeadString<["UPI", 1]>; // "UPI"
type HN = HeadString<[1, "UPI"]>; // never
const hs: HS = "UPI";

// Advanced 5: contravariant infer gives an intersection (union -> intersection trick)
type UnionToIntersection<U> = (U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never;
type I = UnionToIntersection<{ a: 1 } | { b: 2 }>; // { a: 1 } & { b: 2 }
const inter: I = { a: 1, b: 2 };

console.log(z, f, l, pn, hs, inter); // 42 1 true itemId UPI { a: 1, b: 2 }
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: reuse the service return type in the controller (single source of truth)
import express from "express";

const orderService = {
  async list(userId: number) {
    return [{ id: 1, userId, total: 499 }]; // return type is inferred by TS
  },
};
type OrderList = Awaited<ReturnType<typeof orderService.list>>; // { id; userId; total }[]
type OrderRow = OrderList[number]; // one row

const app = express();
app.get("/users/:id/orders", async (req, res) => {
  const rows: OrderList = await orderService.list(Number(req.params.id)); // typed
  const first: OrderRow | undefined = rows[0];
  res.json({ count: rows.length, first });
});
```

```tsx
// React: get the props of any component, and the payload of an async function used in a hook
import { type ComponentProps, useEffect, useState } from "react";

function PriceTag(props: { amount: number; currency: "INR" | "USD" }) {
  return <span>{props.currency} {props.amount}</span>;
}
type PriceTagProps = ComponentProps<typeof PriceTag>; // uses infer internally

async function fetchCart() {
  return { items: 3, total: 1250 }; // inferred shape
}
type Cart = Awaited<ReturnType<typeof fetchCart>>; // { items: number; total: number }

export function CartBadge(p: PriceTagProps) {
  const [cart, setCart] = useState<Cart | null>(null); // state typed from the function
  useEffect(() => { fetchCart().then(setCart); }, []);
  return <PriceTag {...p} amount={cart?.total ?? p.amount} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `infer` outside a conditional type
```typescript
// ❌ Wrong
type Bad<T> = infer U;
// error TS1338: 'infer' declarations are only permitted in the 'extends' clause of a conditional type.
```

❌ Mistake 2: Using `infer` in the true/false branch instead of the `extends` clause
```typescript
// ❌ Wrong
type Bad2<T> = T extends Promise<unknown> ? infer U : never;
// error TS1338: 'infer' declarations are only permitted in the 'extends' clause of a conditional type.
```

❌ Mistake 3: Expecting `ReturnType` to work on a value instead of a function type
```typescript
// ❌ Wrong
function mk() { return 1; }
type Bad3 = ReturnType<mk>;
// error TS2749: 'mk' refers to a value, but is being used as a type here. Did you mean 'typeof mk'?
// ✅ Right
type Ok3 = ReturnType<typeof mk>; // number
```

---

## 🧠 Tricky Interview Question

```typescript
type Overloaded = {
  (x: string): string;
  (x: number): number;
};
type R = ReturnType<Overloaded>;
```
**What is `R`?**

Answer: `number`. When inferring from a type with several call signatures (overloads), TypeScript uses the **last** signature. That is why `ReturnType` and `Parameters` of overloaded functions are surprising. Interviewers use this to test whether you know `infer` has limits: it cannot see all overloads. Workaround: handle each signature manually or avoid overloading in types you need to infer from.

---

## ⚫ Interview Questions + Answers

Q1: What does `infer` do?
A1: It introduces a type variable inside the `extends` clause of a conditional type and lets TypeScript fill it by matching. `T extends (...a: any[]) => infer R ? R : never` captures the return type.

Q2: How are `ReturnType`, `Parameters` and `Awaited` implemented?
A2: `ReturnType<T> = T extends (...args: any) => infer R ? R : any`; `Parameters<T> = T extends (...args: infer P) => any ? P : never`; `Awaited` recursively unwraps thenables with `infer`.

Q3: What is the difference between `infer` in covariant and contravariant positions with the same name?
A3: Multiple candidates from covariant positions (return, property) are unioned. From contravariant positions (parameters) they are intersected. The `UnionToIntersection` trick above relies on this.

Q4: What happens with overloaded functions?
A4: Inference picks the last overload signature. Other overloads are ignored.

Q5: How would you extract the props of a React component or the state shape from a Redux store?
A5: `ComponentProps<typeof Comp>` (uses infer), and `ReturnType<typeof store.getState>` for `RootState` and `typeof store.dispatch` for `AppDispatch`. This is exactly how RTK's recommended typing works.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a type that already exists inside another type (return, args, element, Promise value)
- Parsing string literal types (routes, event names) with template literals
- Building reusable utility types

❌ Avoid when:
- You can simply export the type and import it (clearer)
- The source has overloads or generics; `infer` may give a surprising or `unknown` answer
- Deeply recursive `infer` on large unions slows the compiler

---

## 📊 Visual Diagram
```
  T extends Promise<infer U> ? U : T

   T = Promise<Order>
         │
         ▼   pattern match
   Promise< ░░░ >      ◄── ░░░ = U (captured)
         │
         ▼
   U = Order   ──► true branch returns Order

   T = number  ──► no match ──► false branch returns number
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| infer | Capture a type in a pattern | Pattern से type पकड़ना |
| Pattern matching | Match shape, extract parts | Shape मिलाकर हिस्से निकालना |
| Variadic tuple | `[...A, B]` patterns | Tuple में बाकी elements |
| Covariant position | Return/property | Output वाली जगह |
| Contravariant position | Parameter | Input वाली जगह |

---

## ⚡ 3-Line Summary
English:
1. `infer X` inside a conditional type's `extends` clause captures part of the matched type.
2. It powers `ReturnType`, `Parameters`, `Awaited`, `ComponentProps`, route-param parsing.
3. Limits: only in `extends`, picks the last overload, and `infer X extends Y` needs TS 4.7+.

Hindi:
1. Conditional type के `extends` में `infer X` match हुए type का हिस्सा पकड़ लेता है।
2. `ReturnType`, `Parameters`, `Awaited`, `ComponentProps` और route-param parsing इसी से चलते हैं।
3. सीमाएँ: सिर्फ `extends` में चलता है, overloads में आखिरी signature लेता है, और `infer X extends Y` के लिए TS 4.7+ चाहिए।

---

## ➡️ Next Topic
**50. Template Literal Types** — string types को जोड़ना और parse करना (`on${Capitalize<E>}`, route params)।
