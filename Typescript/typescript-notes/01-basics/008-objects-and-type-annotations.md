# 8. Objects and Type Annotations
# हिंदी में: Objects और Type Annotations

> Version note: **TypeScript 5.x** (5.9.3 पर verify)। `exactOptionalPropertyTypes` (4.4+) और `satisfies` (4.9+) इस note में आते हैं।

---

## 🔵 Simple Definition (English)
A **type annotation** is the `: Type` you write after a variable, parameter or return to tell TypeScript what it is. An **object type** describes the **shape** of an object: which property names exist and the type of each, e.g. `{ id: string; qty: number; note?: string }`. TypeScript uses **structural typing**: any value that has (at least) those properties with compatible types is accepted — the *name* of the type does not matter.

## 🔵 सरल परिभाषा (Hindi)
**Type annotation** वह `: Type` है जो आप variable, parameter या return के बाद लिखते हैं ताकि TypeScript को पता चले कि वह क्या है। **Object type** किसी object का **shape** बताता है: कौन से property names हैं और हर एक का type क्या है, जैसे `{ id: string; qty: number; note?: string }`। TypeScript **structural typing** इस्तेमाल करता है: जिस value में (कम से कम) वे properties compatible types के साथ हों वह स्वीकार होती है — type का *नाम* मायने नहीं रखता।

---

## 🔴 Problem it Solves
In JS, objects are bags of anything: `order.itmes` (typo) returns `undefined`, a missing `address` crashes later in a different file, and nobody can tell from a function signature what `payload` must contain. Object types make the contract explicit at the exact place the data is used: the editor autocompletes `order.` with the right keys, missing required fields are flagged on creation, and a rename of `totalPaise` shows every affected file.

## 🔴 यह क्यों बना? (Hindi)
JS में objects किसी भी चीज़ की पोटली हैं: `order.itmes` (typo) चुपचाप `undefined` देता है, `address` न होने पर crash किसी और file में बाद में आता है, और function के signature से कोई नहीं बता सकता कि `payload` में क्या होना चाहिए। Object types contract को ठीक उसी जगह साफ़ कर देते हैं जहाँ data इस्तेमाल होता है: editor `order.` पर सही keys दिखाता है, ज़रूरी field गायब हो तो बनाते समय ही flag होता है, और `totalPaise` rename करने पर प्रभावित हर file दिख जाती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Inline annotation: `const p: { id: string; qty: number } = { id: "A", qty: 1 }`.
Step 2 → Optional property `note?: string` → type `string | undefined`; read-only `readonly id: string` → assignment error after creation.
Step 3 → Nested objects: `{ address: { city: string; pin: string } }`. Annotate each level, or extract to a named `interface`/`type` (topics 013–014).
Step 4 → **Structural check on assignment:** all required props must exist; types must be compatible. Extra props are OK when assigning a *variable*, but are an **excess property error** for a fresh *object literal* (topic 040).
Step 5 → `object` (any non-primitive), `{}` (any non-null value — includes `"abc"` and `5`!), `Object` (avoid) and `Record<string, unknown>` (any string-keyed object) are different. Prefer a real shape.
Step 6 → Method vs property syntax: `{ pay(amount: number): void }` (method, bivariant) vs `{ pay: (amount: number) => void }` (property, checked strictly under `strictFunctionTypes`).
Step 7 → Annotate **boundaries** (function params, return types of exported functions, API data) and let inference handle local variables (topic 009).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Inline annotation: `const p: { id: string; qty: number } = { id: "A", qty: 1 }`।
Step 2 → Optional property `note?: string` → type `string | undefined`; read-only `readonly id: string` → बनने के बाद assign करने पर error।
Step 3 → Nested objects: `{ address: { city: string; pin: string } }`। हर level annotate करो, या नाम वाले `interface`/`type` में निकालो (topics 013–014)।
Step 4 → **Assignment पर structural check:** सारे required props होने चाहिए; types compatible हों। *Variable* assign करते समय extra props चलते हैं, पर *fresh object literal* में **excess property error** आता है (topic 040)।
Step 5 → `object` (कोई भी non-primitive), `{}` (कोई भी non-null value — `"abc"` और `5` भी!), `Object` (बचो) और `Record<string, unknown>` (string-keyed कोई भी object) अलग हैं। असली shape लिखना बेहतर।
Step 6 → Method बनाम property syntax: `{ pay(amount: number): void }` (method, bivariant) बनाम `{ pay: (amount: number) => void }` (property, `strictFunctionTypes` में सख्ती से check)।
Step 7 → **Boundaries** annotate करो (function params, exported functions के return types, API data) और local variables के लिए inference पर भरोसा करो (topic 009)।

---

## 🟡 Real World Example
**Swiggy order payload:** `{ orderId, restaurant: { id, name }, items: [{ sku, qty, pricePaise }], deliveryAddress: { line1, city, pincode }, couponCode? }`. The `couponCode` is optional (users may not apply one) and `orderId` is `readonly` once the server assigns it. The Express handler accepts `CreateOrderRequest`; the React checkout form builds exactly that shape; the SQL Server layer maps it into `Orders` and `OrderItems` rows. One shape, three layers.

## 🟡 Real Example Hindi mein
**Swiggy order payload:** `{ orderId, restaurant: { id, name }, items: [{ sku, qty, pricePaise }], deliveryAddress: { line1, city, pincode }, couponCode? }`। `couponCode` optional है (user coupon न लगाए) और server द्वारा `orderId` मिलने के बाद वह `readonly` है। Express handler `CreateOrderRequest` लेता है; React checkout form ठीक वही shape बनाता है; SQL Server layer उसे `Orders` और `OrderItems` rows में map करता है। एक shape, तीन layers।

---

## 💻 Code Example — Basic

```typescript
// objects-basic.ts

// Inline object type annotation on a variable
const customer: { id: number; name: string; phone?: string } = {
  id: 7,                    // required number
  name: "Aditya",           // required string
  // phone is optional, so we may omit it
};

// Read optional property safely: its type is string | undefined
console.log(customer.phone?.length ?? 0);   // 0

// Annotation on parameters and on the return value
function describe(c: { id: number; name: string }): string {
  return `#${c.id} ${c.name}`;              // both props are guaranteed
}
console.log(describe(customer));            // #7 Aditya

// Structural typing: extra properties on a VARIABLE are fine
const loyal = { id: 9, name: "Riya", tier: "gold" };  // has extra "tier"
console.log(describe(loyal));               // #9 Riya  (OK: shape includes id + name)

// Nested object types
const order: {
  orderId: string;
  address: { city: string; pincode: string };
  items: { sku: string; qty: number }[];
} = {
  orderId: "SW-1",
  address: { city: "Bengaluru", pincode: "560001" },
  items: [{ sku: "PIZZA", qty: 2 }],
};
console.log(order.address.city, order.items[0]?.qty);   // Bengaluru 2

// Output:
// 0
// #7 Aditya
// #9 Riya
// Bengaluru 2
```

```typescript
// ❌ intentional errors — real tsc 5.9 output
const c1: { id: number; name: string } = { id: 1 };
// error TS2741: Property 'name' is missing in type '{ id: number; }' but required in type '{ id: number; name: string; }'.

const c2: { id: number; name: string } = { id: 1, name: "A", tier: "gold" };
// error TS2353: Object literal may only specify known properties, and 'tier' does not exist in type '{ id: number; name: string; }'.

const c3: { id: number; name: string } = { id: "1", name: "A" };
// error TS2322: Type 'string' is not assignable to type 'number'.

const c4: { readonly id: number } = { id: 1 };
c4.id = 2;
// error TS2540: Cannot assign to 'id' because it is a read-only property.
```

## 💻 Code Example — Advanced

```typescript
// objects-advanced.ts — object, {}, Record, method vs property, satisfies (TS 4.9+)

// 1) `object` vs `{}` vs Record<string, unknown>
function onlyObjects(o: object): string { return Object.keys(o).join(","); } // rejects primitives
function anyNonNull(v: {}): string { return String(v); }                     // accepts 5 and "abc" too!
function bag(r: Record<string, unknown>): number { return Object.keys(r).length; }
console.log(onlyObjects({ a: 1, b: 2 }));   // a,b
console.log(anyNonNull(5));                 // 5
console.log(bag({ x: 1, y: "z" }));         // 2

// 2) Optional property: with exactOptionalPropertyTypes (4.4+) `undefined` must be explicit
type Patch = { note?: string };              // by default also accepts note: undefined
const patch: Patch = { note: undefined };    // OK unless exactOptionalPropertyTypes is on

// 3) Index into object types by key (indexed access, details in topic 033)
type Order = { id: string; totalPaise: number; address: { city: string } };
type City = Order["address"]["city"];        // string
const city: City = "Pune";
console.log(city);                           // Pune

// 4) satisfies (TS 4.9+): validate shape but keep the precise literal types
const config = {
  port: 3000,                                // stays number
  env: "prod",                               // stays "prod" with satisfies + as const-like check
} satisfies { port: number; env: "dev" | "prod" };
const e: "prod" = config.env;                // works because "prod" literal is preserved
console.log(config.port + 1, e);             // 3001 prod

// 5) Methods in object types and `this`-less callbacks
interface PaymentGateway {
  charge(amountPaise: number): Promise<string>;   // method syntax
  readonly name: string;                          // readonly property
}
const razorpay: PaymentGateway = {
  name: "razorpay",
  async charge(amountPaise) {                     // param type inferred from the interface
    return `pay_${amountPaise}`;
  },
};
razorpay.charge(49950).then(console.log);         // pay_49950

// 6) Destructuring with annotations applies to the whole pattern
function total({ items, tax = 0 }: { items: number[]; tax?: number }): number {
  return items.reduce((a, b) => a + b, 0) + tax;
}
console.log(total({ items: [100, 200] }));        // 300

// Output:
// a,b
// 5
// 2
// Pune
// 3001 prod
// 300
// pay_49950
```

---

## 🟠 Node/Express + React Integration

**Express — typing the request body, params and the response object:**

```typescript
// checkout-route.ts
import express, { Request, Response } from "express";

// Request body shape (what the client must send)
interface CreateOrderBody {
  restaurantId: string;
  items: { sku: string; qty: number }[];
  couponCode?: string;                    // optional
}
// Response shape (what we promise to send)
interface CreateOrderResponse { orderId: string; totalPaise: number }

const app = express();
app.use(express.json());

// Request<Params, ResBody, ReqBody> — generics are positional
app.post(
  "/orders",
  (req: Request<unknown, CreateOrderResponse, CreateOrderBody>, res: Response<CreateOrderResponse>) => {
    const { items, couponCode } = req.body;                     // typed destructuring
    const total = items.reduce((s, i) => s + i.qty * 19900, 0); // qty is number
    const discount = couponCode === "WELCOME" ? 5000 : 0;      // optional prop handled
    res.status(201).json({ orderId: "SW-1", totalPaise: total - discount });
  }
);
export default app;
```

**React — props are an object type, and `children`/handlers go in the same shape:**

```tsx
// OrderSummary.tsx
type Address = { line1: string; city: string };
type OrderSummaryProps = {
  orderId: string;
  address: Address;                          // nested object type reused
  onReorder?: (orderId: string) => void;     // optional callback prop
};

export function OrderSummary({ orderId, address, onReorder }: OrderSummaryProps) {
  return (
    <div>
      <p>{orderId} - {address.city}</p>
      {onReorder && <button onClick={() => onReorder(orderId)}>Reorder</button>}
    </div>
  );
}
```
Redux Toolkit: a slice's `initialState` annotation is an object type: `const initialState: CartState = { items: [], couponCode: null }` — annotate it so `createSlice` infers `state` correctly (topic 094). SQL Server: map `recordset` rows (`IRecordSet<OrderRow>`) onto the same object type.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `Object`, `{}` or `object` where you need a shape
```typescript
// ❌ Wrong — `object` says nothing about properties; real compiler output below
function show(o: object) {
  return o.id;
}
// error TS2339: Property 'id' does not exist on type 'object'.
```
```typescript
// ✅ Right
function show2(o: { id: string }) { return o.id; }
console.log(show2({ id: "A" })); // A
```

❌ Mistake 2: Assuming optional means "can be null"
✅ Correct: `note?: string` is `string | undefined`. `null` is NOT allowed under `strictNullChecks`; write `note: string | null` if the API returns `null`.

❌ Mistake 3: Mutating a `readonly` prop through an alias — `readonly` is shallow and compile-time only. `Object.freeze` is runtime.

❌ Mistake 4: Annotating everything — `const total: number = items.length` is noise. Annotate boundaries; let inference do the rest.

---

## 🧠 Tricky Interview Question

```typescript
type Point = { x: number; y: number };
const p3 = { x: 1, y: 2, z: 3 };
const a: Point = p3;               // line A
const b: Point = { x: 1, y: 2, z: 3 }; // line B  ❌ (TS2353)
```
**Question:** Which line errors and why?

**Answer:** **Only line B.** Line A assigns a *variable* — TS checks structural compatibility only, and `{ x, y, z }` has everything `Point` needs, so extra `z` is fine. Line B is a **fresh object literal**, and TS performs the extra **excess property check** (`TS2353: Object literal may only specify known properties, and 'z' does not exist in type 'Point'`) because it is almost certainly a typo. Workaround to intentionally allow: assign to a variable first, add an index signature, or use `satisfies`.

```typescript
// ❌ verified: only line B fails
type Point = { x: number; y: number };
const p3 = { x: 1, y: 2, z: 3 };
const a: Point = p3;
const b: Point = { x: 1, y: 2, z: 3 };
// error TS2353: Object literal may only specify known properties, and 'z' does not exist in type 'Point'.
```

---

## ⚫ Interview Questions + Answers

Q1: What is structural typing and how is it different from nominal typing?
A1: In structural typing, two types are compatible if their shapes match; names are irrelevant (Java/C# are nominal). So `{id:number}` objects can be passed anywhere a `{id:number}` is expected. For nominal behaviour you add "brands" (topic 058).

Q2: `object` vs `{}` vs `Object` vs `Record<string, unknown>`?
A2: `object` = any non-primitive (arrays, functions, objects). `{}` = any non-null/undefined value including primitives. `Object` = the wrapper-interface type, avoid. `Record<string, unknown>` = an object whose keys are strings and values unknown (arrays and interfaces without index signature may not be assignable).

Q3: What is excess property checking?
A3: When you directly assign an object **literal** to a typed target, TS reports properties not in the target, to catch typos. It does not apply when assigning from a variable.

Q4: How is `x?: T` different from `x: T | undefined`?
A4: The optional form lets the key be **absent**; the union form requires the key to be present (even if `undefined`). `exactOptionalPropertyTypes` makes `x?: T` disallow an explicit `undefined`.

Q5: When should you annotate and when rely on inference?
A5: Annotate function parameters, exported function return types, class members, and empty/literal-widening initialisers. Skip annotating simple locals and values with obvious initialisers, since inference gives the same type and stays in sync.

---

## 🔷 When to Use + When Not to Use
✅ Use inline object types for one-off shapes (a single function param, local config); extract to `interface`/`type` when used in 2+ places or exported (topics 013–015).

❌ Avoid inline types for large payloads (hard to read), `Object`/`{}` for "any object", and annotations that merely repeat what inference already knows.

---

## 📊 Visual Diagram
```
 type Order = {
   readonly id: string;          ← cannot reassign after creation
   totalPaise: number;           ← required
   couponCode?: string;          ← optional  (string | undefined)
   address: { city: string };    ← nested object type
 }

 value { id:"A", totalPaise:1, address:{city:"X"}, extra:1 }
        │
        ├── assigned from a VARIABLE  ─► ✅ structural match (extra ignored)
        └── assigned as a FRESH LITERAL ─► ❌ TS2353 excess property
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type annotation | `: Type` written explicitly | साफ़ लिखा हुआ `: Type` |
| Object type | Shape of an object | Object का shape |
| Structural typing | Compatible if shapes match | Shape मिले तो compatible |
| Optional property | `key?: T`, may be missing | `key?: T`, ग़ायब हो सकता है |
| readonly | Cannot be reassigned (compile-time) | दोबारा assign नहीं हो सकता |
| Excess property check | Extra keys in fresh literal flagged | Fresh literal में extra keys पर error |
| Fresh literal | Object literal written inline | सीधे लिखा object literal |

---

## ⚡ 3-Line Summary
English:
1. Object types describe shape (`{ id: string; note?: string }`); TS checks them structurally, not by name.
2. Fresh object literals get excess-property checks; variables do not — optional means `T | undefined`, `readonly` is shallow.
3. Annotate boundaries (params, returns, API data), prefer real shapes over `object`/`{}`/`Object`, and let inference handle locals.

Hindi:
1. Object types shape बताते हैं (`{ id: string; note?: string }`); TS इन्हें नाम से नहीं, structure से check करता है।
2. Fresh object literal पर excess-property check लगता है, variable पर नहीं — optional मतलब `T | undefined`, `readonly` shallow है।
3. Boundaries annotate करो (params, returns, API data), `object`/`{}`/`Object` की जगह असली shape लिखो, और locals के लिए inference पर छोड़ो।

---

## ➡️ Next Topic
**009. Type Inference** — how TypeScript figures out types for you, widening, contextual typing and when to help it.
