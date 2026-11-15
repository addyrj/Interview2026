# 13. Type Aliases
# हिंदी में: Type Aliases (type को नाम देना)

> TypeScript 5.x | Recursive aliases for JSON-like shapes need TS 3.7+

---

## 🔵 Simple Definition (English)
A **type alias** gives a name to any type using the `type` keyword: `type Price = number`, `type Status = 'a' | 'b'`, `type Handler = (id: string) => void`, `type Point = { x: number; y: number }`. An alias does NOT create a new type. It is just another name (a label) for an existing type expression, so `Price` and `number` are fully interchangeable. Unlike `interface`, an alias can name unions, tuples, primitives, function types and mapped/conditional types.

## 🔵 सरल परिभाषा (Hindi)
**Type alias** `type` keyword से किसी भी type को नाम देता है: `type Price = number`, `type Status = 'a' | 'b'`, `type Handler = (id: string) => void`, `type Point = { x: number; y: number }`। Alias कोई **नया type नहीं** बनाता, यह मौजूदा type expression का सिर्फ़ दूसरा नाम (label) है, इसलिए `Price` और `number` पूरी तरह interchangeable हैं। `interface` के उलट, alias unions, tuples, primitives, function types और mapped/conditional types को भी नाम दे सकता है।

---

## 🔴 Problem it Solves
Long type expressions get copy-pasted: `{ id: string; amount: number; currency: 'INR' | 'USD' }` appears in the API client, the Redux slice, the React props and the test. When the shape changes, you fix three places and forget the fourth. A named alias gives one definition, a readable name in error messages and hover tooltips, and a place to attach a comment. It also lets you express domain meaning: `type Rupees = number` documents intent even though the compiler treats it as `number`.

## 🔴 यह क्यों बना? (Hindi)
लंबे type expressions बार-बार copy-paste होते हैं: `{ id: string; amount: number; currency: 'INR' | 'USD' }` API client, Redux slice, React props और test, चारों में दिखता है। Shape बदलने पर तीन जगह ठीक होती हैं और चौथी छूट जाती है। Named alias एक ही definition देता है, error messages और hover में पढ़ने लायक नाम देता है, और comment लगाने की जगह भी। यह domain का मतलब भी बताता है: `type Rupees = number` intent document करता है, भले compiler इसे `number` ही माने।

---

## 🟢 How it Works — Step by Step

Step 1 → Write `type Name = <any type expression>`. The right-hand side can be anything: primitive, union, object, tuple, function, generic.
Step 2 → The compiler stores a label. Wherever `Name` appears, it is substituted by the expression (aliases are erased in JS output, zero runtime cost).
Step 3 → Aliases can take type parameters: `type ApiResponse<T> = { data: T; error?: string }`.
Step 4 → Aliases can reference other aliases, and (since TS 3.7) themselves, for recursive shapes such as JSON or a menu tree.
Step 5 → You CANNOT declare the same alias name twice in one scope (no declaration merging, error TS2300). That is the main behavioural difference from `interface`.
Step 6 → Combine aliases with `&` (intersection) to compose bigger shapes from small ones.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `type Name = <कोई भी type expression>` लिखो। दाईं तरफ़ कुछ भी हो सकता है: primitive, union, object, tuple, function, generic।
Step 2 → Compiler एक label याद रखता है। जहाँ `Name` आता है वहाँ expression substitute हो जाती है (JS output में alias नहीं रहता, runtime cost zero)।
Step 3 → Alias type parameters ले सकता है: `type ApiResponse<T> = { data: T; error?: string }`।
Step 4 → Alias दूसरे aliases को, और (TS 3.7 से) खुद को भी refer कर सकता है, JSON या menu tree जैसी recursive shapes के लिए।
Step 5 → एक scope में एक ही alias नाम दो बार declare नहीं कर सकते (declaration merging नहीं, error TS2300)। `interface` से यही मुख्य behavioural फ़र्क है।
Step 6 → `&` (intersection) से छोटे aliases जोड़कर बड़े shapes बनाओ।

---

## 🟡 Real World Example
**Razorpay's checkout payload** has a `Money` concept (`amount` in paise plus `currency`), a `PaymentMethod` union (`'upi' | 'card' | 'netbanking' | 'wallet'`), a callback type `OnSuccess = (paymentId: string) => void`, and an API envelope `ApiResponse<T>`. Each is a type alias used in dozens of files. When Razorpay adds `'emi'` to `PaymentMethod`, one edit propagates to the whole app and the compiler shows every `switch` that is now incomplete.

## 🟡 Real Example Hindi mein
**Razorpay के checkout payload** में `Money` concept है (paise में `amount` और `currency`), `PaymentMethod` union (`'upi' | 'card' | 'netbanking' | 'wallet'`), callback type `OnSuccess = (paymentId: string) => void`, और API envelope `ApiResponse<T>`। हर एक type alias दर्जनों files में इस्तेमाल होता है। जब Razorpay `PaymentMethod` में `'emi'` जोड़ता है तो एक edit पूरे app में फैल जाती है और compiler वो हर `switch` दिखा देता है जो अब अधूरी है।

---

## 💻 Code Example — Basic

```typescript
// alias-basic.ts  (TypeScript 5.x, strict)

type Rupees = number;                                   // alias for a primitive (documents intent)
type PaymentMethod = 'upi' | 'card' | 'netbanking';     // alias for a literal union
type Coordinates = [lat: number, lng: number];          // alias for a labeled tuple
type OnSuccess = (paymentId: string) => void;           // alias for a function type

// alias for an object shape, composed from the aliases above
type Payment = {
  id: string;               // unique payment id
  amount: Rupees;           // reads better than a bare number
  method: PaymentMethod;    // only the three allowed methods
  location?: Coordinates;   // optional tuple
};

// alias with a type parameter: reusable API envelope
type ApiResponse<T> = { ok: true; data: T } | { ok: false; error: string };

const pay: Payment = { id: 'pay_1', amount: 499, method: 'upi' }; // checked against Payment
const done: OnSuccess = (paymentId) => console.log('paid', paymentId); // paymentId inferred as string

function load(): ApiResponse<Payment> { return { ok: true, data: pay }; } // declared return type keeps the full union
const res = load();                // type is ApiResponse<Payment>, not narrowed by assignment
if (res.ok) {
  done(res.data.id);                 // narrowed: res.data exists only when ok is true
} else {
  console.log(res.error);            // narrowed: error exists only when ok is false
}

// Rupees and number are the SAME type: an alias is only a label
const base: number = 100;
const total: Rupees = base + 50;     // no error: aliases do not create new types
console.log(total);
```

Run with `npx tsx alias-basic.ts`. Real output:
```
paid pay_1
150
```

## 💻 Code Example — Advanced

```typescript
// alias-advanced.ts  (TypeScript 5.x)

// 1. Recursive alias: a JSON value (allowed since TS 3.7)
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };

// 2. Recursive alias for a menu tree (Zomato-style categories)
type MenuNode = { name: string; children?: MenuNode[] };

// 3. Composition with intersection
type WithTimestamps = { createdAt: Date; updatedAt: Date };
type WithId = { id: number };
type OrderRow = WithId & WithTimestamps & { total: number }; // mirrors a SQL Server row

// 4. Generic alias with a default and a constraint
type Paginated<T extends WithId, Meta = { page: number }> = { items: T[]; meta: Meta };

// 5. Alias of a mapped type: make every key nullable (SQL Server columns allow NULL)
type Nullable<T> = { [K in keyof T]: T[K] | null };

// 6. Alias derived from a value (typeof) and from a function (ReturnType)
const defaultCart = { items: [] as string[], coupon: null as string | null };
type Cart = typeof defaultCart;                 // { items: string[]; coupon: string | null }
function makeOrder() { return { id: 1, total: 250 }; }
type MadeOrder = ReturnType<typeof makeOrder>;  // { id: number; total: number }

// Usage
const payload: Json = { ok: true, tags: ['a', 1, null], nested: { deep: [1, 2] } };
const menu: MenuNode = { name: 'Menu', children: [{ name: 'Starters', children: [{ name: 'Paneer Tikka' }] }] };

function countNodes(n: MenuNode): number {
  // recursion on a recursive type: children is optional, so default to []
  return 1 + (n.children ?? []).reduce((sum, c) => sum + countNodes(c), 0);
}

const row: OrderRow = { id: 7, total: 300, createdAt: new Date(0), updatedAt: new Date(0) };
const page: Paginated<OrderRow> = { items: [row], meta: { page: 1 } };
const nullableRow: Nullable<OrderRow> = { ...row, total: null }; // total may now be null
const cart: Cart = defaultCart;
const made: MadeOrder = makeOrder();

console.log(countNodes(menu), JSON.stringify(payload), page.items.length);
console.log(nullableRow.total, cart.items.length, made.total);
```

Run with `npx tsx alias-advanced.ts`. Real output:
```
3 {"ok":true,"tags":["a",1,null],"nested":{"deep":[1,2]}} 1
null 0 250
```

---

## 🟠 Node/Express + React Integration

```tsx
// types/api.ts: shared aliases used by server and client
export type OrderId = string;
export type OrderItem = { sku: string; qty: number; price: number };
export type Order = { id: OrderId; items: OrderItem[]; total: number };
export type ApiResponse<T> = { data: T } | { error: string };

// server/orders.ts  (Express): the alias types the response body
import express, { type Request, type Response } from 'express';
const app = express();

// Response<ApiResponse<Order>> makes res.json() check the payload shape
app.get('/orders/:id', (req: Request<{ id: OrderId }>, res: Response<ApiResponse<Order>>) => {
  const order: Order = { id: req.params.id, items: [{ sku: 'BIRYANI', qty: 1, price: 220 }], total: 220 };
  res.json({ data: order });                 // ok: matches the { data: Order } branch
});

// store/ordersSlice.ts  (Redux Toolkit): alias reused for state
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
type OrdersState = { byId: Record<OrderId, Order>; loading: boolean };
const initialState: OrdersState = { byId: {}, loading: false };
export const ordersSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    orderLoaded(state, action: PayloadAction<Order>) {
      state.byId[action.payload.id] = action.payload; // keyed by OrderId
    },
  },
});

// components/OrderRow.tsx  (React): alias as props type
type OrderRowProps = { order: Order; onSelect: (id: OrderId) => void };
export function OrderRow({ order, onSelect }: OrderRowProps) {
  return <li onClick={() => onSelect(order.id)}>{order.id}: Rs {order.total}</li>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Declaring the same alias twice (aliases do not merge)
```typescript
// ❌ Wrong: type aliases cannot be re-opened like interfaces
type P = { a: number };
type P = { b: number };
// error TS2300: Duplicate identifier 'P'.
```
```typescript
// ✅ Right: one definition using an intersection, or use an interface if you need merging
type P1 = { a: number };
type P = P1 & { b: number };
const p: P = { a: 1, b: 2 };
```

❌ Mistake 2: Thinking an alias creates a distinct (nominal) type
```typescript
type UserId = string;
type OrderId = string;
function cancel(id: OrderId) { console.log(id); }
const u: UserId = 'u_1';
cancel(u); // compiles! UserId and OrderId are both just string
```
✅ Correct: aliases are transparent. If you need `UserId` and `OrderId` to be incompatible, use branded types (topic 58).

❌ Mistake 3: A self-referencing alias that is not wrapped in an object/array. `type Bad = Bad | string` is a circular reference. Recursion must go through an object, array or tuple, e.g. `type Json = string | Json[]`.

---

## 🧠 Tricky Interview Question

```typescript
type Price = number;
type Discount = number;

const price: Price = 500;
const discount: Discount = 0.1;
const wrong: Price = discount;   // does this compile?
```
Answer: Yes, it compiles. `Price` and `Discount` are both aliases of `number`, so they are the same type; TypeScript is structurally typed and an alias adds no new identity. This is why a function `applyDiscount(price: Price, d: Discount)` accepts its arguments in the wrong order silently. To make the compiler catch this you need branded types: `type Price = number & { readonly __brand: 'Price' }`.

---

## ⚫ Interview Questions + Answers

Q1: What does a type alias create: a new type or a name?
A1: Only a name. `type A = B` makes `A` and `B` identical for the compiler, no runtime code is emitted. Error messages may print either name, and TypeScript often keeps the alias name in hover text for readability.

Q2: What can a `type` alias express that an `interface` cannot?
A2: Unions (`A | B`), tuples, primitives (`type Id = string`), function types with overloads of unions, conditional types, mapped types and template literal types. An `interface` can only describe object shapes (including callable and constructable ones).

Q3: Can you recursively reference an alias?
A3: Yes, since TS 3.7, as long as the recursion is nested inside an object type, array or tuple: `type Json = string | number | Json[] | { [k: string]: Json }`. A direct circular union such as `type A = A | string` is an error.

Q4: Why can't you merge two `type` declarations with the same name?
A4: Aliases are not "open". Duplicate names give TS2300. Interfaces are open and merge, which is how libraries are augmented (for example `Express.Request`). If you need extension use an intersection (`&`) or an interface.

Q5: How do you build a type alias from an existing value or function?
A5: `typeof value` in type position and `ReturnType<typeof fn>`: `type Cart = typeof defaultCart`. This keeps the alias in sync with the runtime value, instead of maintaining the shape twice.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Naming unions, tuples, function types or primitives (an interface cannot)
- Building new types from others with `keyof`, mapped or conditional types
- Naming a long inline object type used in more than one place

❌ Avoid when:
- You are describing a public object contract that consumers may need to extend through declaration merging (prefer `interface`, see topic 15)
- You expect the alias to prevent mixing IDs. It will not; use branded types
- The type is used exactly once and is short; an inline annotation is clearer

---

## 📊 Visual Diagram
```
 type Price = number            ┌───────────┐
 type Cost  = number   ───────► │  number   │  (one type, many labels)
                                └───────────┘
 type Order = {...}  ──► label stuck on an object shape
 type Status = 'a'|'b' ► label stuck on a union

 Alias:      label ──► type expression      (erased at runtime)
 Interface:  name that can be re-opened (merge) and extended
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type alias | A name for any type expression | किसी type expression का नाम |
| Intersection `&` | Combines types: must satisfy all | सब types को मिलाना |
| Generic alias | Alias with type parameters | Type parameters वाला alias |
| Recursive type | Alias that refers to itself | खुद को refer करने वाला type |
| Structural typing | Compatibility by shape, not name | Shape से compatibility |
| Branded type | Alias made incompatible via a tag | Tag लगाकर अलग किया गया type |

---

## ⚡ 3-Line Summary
English:
1. `type` names any type (union, tuple, function, object, generic) and is erased at runtime.
2. An alias is only a label, so `type UserId = string` is still interchangeable with `string` and `OrderId`.
3. Aliases do not merge (TS2300); use intersections to compose or an interface when you need declaration merging.

Hindi:
1. `type` किसी भी type (union, tuple, function, object, generic) को नाम देता है और runtime पर मिट जाता है।
2. Alias सिर्फ़ label है, इसलिए `type UserId = string` अब भी `string` और `OrderId` से interchangeable है।
3. Aliases merge नहीं होते (TS2300); compose करने के लिए intersection और merging चाहिए तो interface इस्तेमाल करो।

---

## ➡️ Next Topic
**14. Interfaces** — object contracts that can be extended, implemented by classes and merged across declarations.
