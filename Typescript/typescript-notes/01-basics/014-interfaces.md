# 14. Interfaces
# हिंदी में: Interfaces (object का contract)

> TypeScript 5.x | Interfaces exist only at compile time (erased in JS output)

---

## 🔵 Simple Definition (English)
An **interface** declares the shape (contract) of an object: which properties it has, their types, which are optional or `readonly`, and which methods or call signatures it supports. Any value that has at least those members satisfies the interface (structural typing), no `implements` keyword needed. Interfaces can `extend` other interfaces, can be implemented by classes, and are "open": two interfaces with the same name in the same scope merge into one (declaration merging).

## 🔵 सरल परिभाषा (Hindi)
**Interface** किसी object की shape (contract) बताता है: कौन सी properties हैं, उनके types क्या हैं, कौन सी optional या `readonly` हैं, और कौन से methods या call signatures हैं। जिस value में कम से कम वही members हों वह interface को satisfy करती है (structural typing), `implements` लिखना ज़रूरी नहीं। Interface दूसरे interfaces को `extend` कर सकता है, classes उसे implement कर सकती हैं, और वह "open" है: एक ही scope में एक नाम के दो interfaces अपने-आप merge हो जाते हैं (declaration merging)।

---

## 🔴 Problem it Solves
In plain JavaScript a function that receives a "user" or "order" object has no declared contract. Someone passes `{ name: 'A' }` without `price`, and `price.toFixed()` explodes in production. Interfaces make the contract explicit and checkable: the API response shape, the props of a React component, the row returned from SQL Server and the service a class must provide are all written once and verified everywhere. They also give editors autocomplete, safe refactoring (rename a property and every use updates) and readable documentation.

## 🔴 यह क्यों बना? (Hindi)
सादे JavaScript में जो function "user" या "order" object लेता है उसका कोई declared contract नहीं होता। कोई `price` के बिना `{ name: 'A' }` भेज देता है और production में `price.toFixed()` फट जाता है। Interfaces contract को साफ़ और checkable बनाते हैं: API response की shape, React component के props, SQL Server से आई row, और class को जो service देनी है, सब एक बार लिखे जाते हैं और हर जगह verify होते हैं। साथ में editor को autocomplete, safe refactoring (property rename करो तो हर use बदल जाए) और पढ़ने लायक documentation मिलता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare `interface Item { name: string; price: number }`. Members end with `;` or `,`.
Step 2 → A value is assignable if it has all required members with compatible types. Extra members are fine for variables, but a fresh object literal is checked for excess properties (error TS2353).
Step 3 → Mark members optional with `?` and immutable with `readonly`.
Step 4 → Interfaces can describe functions (call signature `(x: number): string`), constructors (`new (...)`), and index signatures (`[key: string]: number`).
Step 5 → `interface B extends A, C` copies all members of A and C into B. Conflicting member types are reported at the `extends` line.
Step 6 → Declaring `interface Cart` twice merges the members. This is how libraries are augmented (for example adding `user` to Express `Request`).
Step 7 → `class X implements I` forces the class to provide everything in `I`; `I` itself disappears from the JS output.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `interface Item { name: string; price: number }` declare करो। Members `;` या `,` से खत्म होते हैं।
Step 2 → कोई value तब assignable है जब उसमें सारे required members compatible types के साथ हों। Variables में extra members चलते हैं, लेकिन नए object literal पर excess properties check होती है (error TS2353)।
Step 3 → `?` से member optional और `readonly` से immutable बनाओ।
Step 4 → Interface functions (call signature `(x: number): string`), constructors (`new (...)`) और index signatures (`[key: string]: number`) भी describe कर सकता है।
Step 5 → `interface B extends A, C` A और C के सारे members B में ले आता है। Conflicting types `extends` वाली line पर report होते हैं।
Step 6 → `interface Cart` दो बार declare करने पर members merge हो जाते हैं। Libraries को इसी तरह augment करते हैं (जैसे Express `Request` में `user` जोड़ना)।
Step 7 → `class X implements I` class को `I` का सब कुछ देने पर मजबूर करता है; `I` खुद JS output से गायब हो जाता है।

---

## 🟡 Real World Example
**Paytm's wallet service** defines `interface WalletTransaction { readonly txnId: string; amount: number; note?: string }` and `interface PaymentGateway { charge(amount: number): Promise<string> }`. The `UpiGateway` and `CardGateway` classes both `implements PaymentGateway`. The checkout code depends only on the `PaymentGateway` interface, so swapping providers or writing a fake gateway for tests needs no change in checkout. The same `WalletTransaction` interface types the SQL Server row, the Express response and the React list item.

## 🟡 Real Example Hindi mein
**Paytm की wallet service** `interface WalletTransaction { readonly txnId: string; amount: number; note?: string }` और `interface PaymentGateway { charge(amount: number): Promise<string> }` define करती है। `UpiGateway` और `CardGateway` classes दोनों `implements PaymentGateway` करती हैं। Checkout code सिर्फ़ `PaymentGateway` interface पर निर्भर है, इसलिए provider बदलने या test के लिए fake gateway लिखने पर checkout नहीं बदलना पड़ता। वही `WalletTransaction` interface SQL Server row, Express response और React list item तीनों को type करता है।

---

## 💻 Code Example — Basic

```typescript
// interface-basic.ts  (TypeScript 5.x, strict)

// 1. Object contract with optional and readonly members
interface Item {
  readonly sku: string;   // cannot be reassigned after creation
  name: string;           // required
  price: number;          // required
  discount?: number;      // optional: may be undefined
}

// 2. Extending: CartItem has everything in Item plus qty
interface CartItem extends Item {
  qty: number;            // added member
}

// 3. Method signature inside an interface
interface Cart {
  items: CartItem[];                 // array of CartItem
  total(): number;                   // method returning a number
}

// 4. A function type described as an interface (call signature)
interface PriceFormatter {
  (amount: number): string;          // callable: formatter(100)
}

const formatRs: PriceFormatter = (amount) => `Rs ${amount.toFixed(2)}`;

// Build a cart that satisfies the interface structurally (no "implements" needed)
const cart: Cart = {
  items: [
    { sku: 'P1', name: 'Paneer Tikka', price: 220, qty: 2 },       // discount omitted: ok
    { sku: 'P2', name: 'Butter Naan', price: 50, discount: 5, qty: 3 },
  ],
  total() {
    // reduce over the typed items; discount is number | undefined so default it
    return this.items.reduce((sum, i) => sum + (i.price - (i.discount ?? 0)) * i.qty, 0);
  },
};

console.log(formatRs(cart.total()));  // 220*2 + 45*3 = 575
console.log(cart.items[0].name);
```

Run with `npx tsx interface-basic.ts`. Real output:
```
Rs 575.00
Paneer Tikka
```

## 💻 Code Example — Advanced

```typescript
// interface-advanced.ts  (TypeScript 5.x)

// 1. Interface + class: implements enforces the contract
interface PaymentGateway {
  readonly name: string;
  charge(amountPaise: number): Promise<string>;   // resolves to a payment id
}

class UpiGateway implements PaymentGateway {
  readonly name = 'UPI';                          // satisfies readonly name
  async charge(amountPaise: number): Promise<string> {
    return `upi_${amountPaise}`;                  // pretend to call the bank
  }
}

class FakeGateway implements PaymentGateway {     // test double: same contract
  readonly name = 'FAKE';
  async charge(): Promise<string> { return 'fake_1'; } // fewer params is allowed
}

// 2. Generic interface: reusable repository contract (SQL Server / Mongo)
interface Repository<T, K extends string | number = number> {
  findById(id: K): Promise<T | undefined>;
  save(entity: T): Promise<void>;
}

interface User { id: number; email: string }

class InMemoryUserRepo implements Repository<User> {
  private rows = new Map<number, User>();
  async findById(id: number) { return this.rows.get(id); }
  async save(u: User) { this.rows.set(u.id, u); }
}

// 3. Index signature: dictionary of prices by sku
interface PriceList { [sku: string]: number }

// 4. Declaration merging: two declarations become ONE interface
interface Settings { theme: 'light' | 'dark' }
interface Settings { currency: 'INR' | 'USD' }
const settings: Settings = { theme: 'dark', currency: 'INR' }; // needs both members

// 5. Dependency inversion: checkout depends on the interface only
async function checkout(gw: PaymentGateway, rupees: number): Promise<string> {
  const id = await gw.charge(rupees * 100);       // paise
  return `${gw.name}:${id}`;
}

async function main() {
  const repo = new InMemoryUserRepo();
  await repo.save({ id: 1, email: 'a@b.com' });
  const prices: PriceList = { P1: 220, P2: 50 };
  console.log(await repo.findById(1), prices.P1, settings.theme);
  console.log(await checkout(new UpiGateway(), 499));
  console.log(await checkout(new FakeGateway(), 1));
}
main();
```

Run with `npx tsx interface-advanced.ts`. Real output:
```
{ id: 1, email: 'a@b.com' } 220 dark
UPI:upi_49900
FAKE:fake_1
```

---

## 🟠 Node/Express + React Integration

```tsx
// models.ts: ONE interface describing a SQL Server row, reused everywhere
export interface Order {
  id: number;
  customer: string;
  total: number;
  status: 'placed' | 'delivered';
}

// server.ts  (Express)
import express, { type Request, type Response } from 'express';
const app = express();
app.use(express.json());

// Declaring body type through Request generics: Request<Params, ResBody, ReqBody>
interface CreateOrderBody { customer: string; total: number }

app.post('/orders', (req: Request<{}, Order, CreateOrderBody>, res: Response<Order>) => {
  const { customer, total } = req.body;          // typed, no any
  const created: Order = { id: 1, customer, total, status: 'placed' };
  res.status(201).json(created);                 // must match Order
});

// OrderCard.tsx  (React): interface for props (the classic choice)
interface OrderCardProps {
  order: Order;
  onDeliver?: (id: number) => void;              // optional callback prop
}
export function OrderCard({ order, onDeliver }: OrderCardProps) {
  return (
    <div>
      {order.customer}: Rs {order.total}
      {onDeliver && <button onClick={() => onDeliver(order.id)}>Mark delivered</button>}
    </div>
  );
}

// orderSlice.ts  (Redux Toolkit): interface for state
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
interface OrdersState { list: Order[] }
const initialState: OrdersState = { list: [] };
export const slice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    added(state, action: PayloadAction<Order>) { state.list.push(action.payload); },
  },
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Missing a required property
```typescript
interface Item { name: string; price: number }
// ❌ Wrong: price is required
const it: Item = { name: 'x' };
// error TS2741: Property 'price' is missing in type '{ name: string; }' but required in type 'Item'.
```
```typescript
interface Item { name: string; price: number; discount?: number }
// ✅ Right: provide it, or declare it optional with ?
const it: Item = { name: 'x', price: 10 };
```

❌ Mistake 2: Extra property in a fresh object literal (excess property check)
```typescript
interface Item { name: string; price: number }
// ❌ Wrong: 'qty' is not part of Item
const it2: Item = { name: 'x', price: 1, qty: 2 };
// error TS2353: Object literal may only specify known properties, and 'qty' does not exist in type 'Item'.
```
✅ Correct: add `qty` to the interface, or build the object in a variable first (`const raw = {...}; const it: Item = raw;`), which is allowed because the excess check only applies to fresh literals.

❌ Mistake 3: Forgetting that a duplicate interface name MERGES instead of erroring
```typescript
interface Cart { id: string }
interface Cart { total: number }   // merges: Cart now needs BOTH id and total
// ❌ Wrong: the author expected the first Cart only
const c: Cart = { id: '1' };
// error TS2741: Property 'total' is missing in type '{ id: string; }' but required in type 'Cart'.
```
✅ Correct: use unique names, or rely on merging deliberately (module augmentation).

---

## 🧠 Tricky Interview Question

```typescript
interface Animal { name: string }
interface Dog { name: string; bark(): void }

const d: Dog = { name: 'Tommy', bark() {} };
const a: Animal = d;                   // (1)
const d2: Dog = a;                     // (2) ❌
// error TS2741: Property 'bark' is missing in type 'Animal' but required in type 'Dog'.
```
Answer: (1) compiles, (2) does not. `Dog` has every member of `Animal`, so a `Dog` is assignable to `Animal` (structural subtyping, no `extends` needed). The reverse fails because `Animal` lacks `bark`: error TS2741 `Property 'bark' is missing in type 'Animal' but required in type 'Dog'`. Interfaces are compared by shape, not by declared relationship.

---

## ⚫ Interview Questions + Answers

Q1: What is an interface and does it exist at runtime?
A1: An interface is a compile-time contract for the shape of a value. It is completely erased in the emitted JavaScript, so you cannot use `instanceof` with an interface or loop over its keys at runtime. For runtime checks use type guards or a schema library such as Zod.

Q2: What is declaration merging?
A2: Multiple `interface X` declarations in the same scope are combined into one type with all members. It is used to augment third-party types (for example `declare global { namespace Express { interface Request { user?: User } } }`). `type` aliases cannot do this.

Q3: What is the difference between `extends` on an interface and `implements` on a class?
A3: `interface B extends A` creates a new interface containing A's members (type-level inheritance). `class C implements I` only checks that the class provides I's members; it does not inherit any code or types. A class can implement several interfaces and extend one class.

Q4: Why does TypeScript allow an object with extra properties sometimes and reject it at other times?
A4: Excess property checking only applies to fresh object literals assigned directly to a typed target. A variable holding an object with extra members is assignable (structural typing). This catches typos in literals without breaking legitimate subtype assignments.

Q5: How do you type a function with properties, e.g. a callable with a `.cache`?
A5: Use an interface with a call signature plus members: `interface Memo { (n: number): number; cache: Map<number, number> }`. This is one of the cases that reads more naturally with an interface than with `type`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Describing object shapes: API DTOs, React props, Redux state, DB rows
- A class must satisfy a contract (`implements`), dependency inversion, test doubles
- Library authors need consumers to augment types via declaration merging
- Deep `extends` hierarchies (interfaces are checked faster than big intersections)

❌ Avoid when:
- You need a union, tuple, primitive alias or conditional/mapped type (use `type`)
- Accidental merging would be dangerous (a name collision across files silently merges)
- You need to describe a value only at runtime; interfaces vanish, use Zod

---

## 📊 Visual Diagram
```
 interface Item { name; price }          interface CartItem extends Item { qty }
        ▲                                         │
        │ structurally satisfies                  ▼
 { name:'x', price:1, qty:2 }  ───────►  CartItem = { name; price; qty }

 interface Cart {id}  +  interface Cart {total}   ==merge==►  Cart { id; total }

 class UpiGateway ──implements──► interface PaymentGateway   (erased at runtime)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Interface | Compile-time contract for an object shape | Object shape का compile-time contract |
| Structural typing | Compatible if the shape matches | Shape मिले तो compatible |
| extends | One interface inherits members of another | एक interface दूसरे के members लेता है |
| implements | Class promises to satisfy an interface | Class contract निभाने का वादा करती है |
| Declaration merging | Same-name interfaces combine | एक नाम के interfaces जुड़ जाते हैं |
| Call signature | Interface describing a callable | Callable का description |
| Excess property check | Rejects unknown keys in fresh literals | Literal में अनजान keys reject |

---

## ⚡ 3-Line Summary
English:
1. An interface is an erased, compile-time contract for an object's shape, checked structurally.
2. Interfaces support `extends`, `implements`, optional and `readonly` members, call signatures and declaration merging.
3. Use them for DTOs, props, state and class contracts; use Zod when you need runtime validation.

Hindi:
1. Interface object की shape का compile-time contract है जो runtime में मिट जाता है और structurally check होता है।
2. Interfaces `extends`, `implements`, optional और `readonly` members, call signatures और declaration merging support करते हैं।
3. DTOs, props, state और class contracts के लिए इस्तेमाल करो; runtime validation चाहिए तो Zod।

---

## ➡️ Next Topic
**15. interface vs type — When to Use Which** — a practical decision guide with the real differences (merging, unions, performance, error messages).
