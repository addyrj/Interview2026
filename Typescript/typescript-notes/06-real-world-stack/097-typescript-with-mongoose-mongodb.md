# 97. TypeScript with Mongoose / MongoDB
# हिंदी में: Mongoose / MongoDB के साथ TypeScript

> Verified with **TypeScript 5.9 (5.x)**, `mongoose` 9 (types bundled). Type-checked only; no MongoDB server was started.

---

## 🔵 Simple Definition (English)
Mongoose ships its own types. You describe a document with an **interface** (`IOrder`), pass it as a generic to `new Schema<IOrder>(...)` and `model<IOrder>(...)`, and Mongoose types `create`, `find`, `findOne`, etc. Two document flavours matter: **hydrated documents** (full Mongoose objects with `save()`, `_id`, virtuals - `HydratedDocument<IOrder>`) and **lean objects** (`.lean()` plain JS objects - faster, no methods). Alternatively, `InferSchemaType<typeof schema>` derives the interface from the schema so you define the shape once.

## 🔵 सरल परिभाषा (Hindi)
Mongoose अपने types के साथ आता है। आप document को **interface** (`IOrder`) से describe करते हो, उसे `new Schema<IOrder>(...)` और `model<IOrder>(...)` में generic की तरह देते हो, और Mongoose `create`, `find`, `findOne` आदि को type कर देता है। दो तरह के documents मायने रखते हैं: **hydrated documents** (`save()`, `_id`, virtuals वाले पूरे Mongoose objects - `HydratedDocument<IOrder>`) और **lean objects** (`.lean()` से plain JS objects - तेज़, बिना methods)। विकल्प: `InferSchemaType<typeof schema>` से schema से ही interface निकालो ताकि shape एक ही जगह लिखना पड़े।

---

## 🔴 Problem it Solves
MongoDB is schemaless, so any shape can be inserted. Plain JS Mongoose lets `Order.create({ amount: "abc" })` through until runtime validation. With TS, `create({ amount: "5" })` fails at compile time, `findOne()` returns `Doc | null` forcing a null check (the classic "Cannot read properties of null"), and lean vs hydrated results have correct types so you do not call `.save()` on a plain object.

## 🔴 यह क्यों बना? (Hindi)
MongoDB schemaless है, इसलिए कोई भी shape insert हो सकता है। Plain JS Mongoose में `Order.create({ amount: "abc" })` runtime validation तक निकल जाता है। TS में `create({ amount: "5" })` compile time पर fail होता है, `findOne()` `Doc | null` देता है जिससे null check करना पड़ता है (क्लासिक "Cannot read properties of null"), और lean बनाम hydrated results के सही types होते हैं ताकि plain object पर `.save()` call न हो।

---

## 🟢 How it Works — Step by Step
Step 1 → `interface IOrder { userId: string; amount: number; status: "PLACED" | "PAID"; items: {sku: string; qty: number}[] }`.
Step 2 → `const schema = new Schema<IOrder>({ ... })` - Mongoose checks that schema keys match the interface.
Step 3 → `export const Order = model<IOrder>("Order", schema)`.
Step 4 → `await Order.create({...})` returns a hydrated document; `Order.findById(id)` returns `HydratedDocument<IOrder> | null`.
Step 5 → `.lean<IOrder>()` returns plain objects (use for read-only API responses).
Step 6 → Instance methods, statics and virtuals need extra generics (`Schema<IOrder, Model<IOrder>, IOrderMethods>`) - or infer from schema options.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `interface IOrder { userId: string; amount: number; status: "PLACED" | "PAID"; items: {sku: string; qty: number}[] }`।
Step 2 → `const schema = new Schema<IOrder>({ ... })` - Mongoose जाँचता है कि schema keys interface से मेल खाती हैं।
Step 3 → `export const Order = model<IOrder>("Order", schema)`।
Step 4 → `await Order.create({...})` hydrated document देता है; `Order.findById(id)` `HydratedDocument<IOrder> | null` देता है।
Step 5 → `.lean<IOrder>()` plain objects देता है (read-only API responses के लिए)।
Step 6 → Instance methods, statics और virtuals के लिए extra generics चाहिए (`Schema<IOrder, Model<IOrder>, IOrderMethods>`)।

---

## 🟡 Real World Example
**Zomato order-history service** on MongoDB: each order document has `userId`, `items[]`, `status`, `createdAt`. The list API uses `.lean()` for speed and returns plain `IOrder` objects; the "mark delivered" API loads a hydrated doc, mutates `status`, and calls `save()` so schema validators and middleware run. TypeScript guarantees that `status` can only be one of the allowed literals.

## 🟡 Real Example Hindi mein
**Zomato order-history service** MongoDB पर: हर order document में `userId`, `items[]`, `status`, `createdAt` हैं। List API speed के लिए `.lean()` लेती है और plain `IOrder` objects लौटाती है; "delivered" API hydrated doc load करके `status` बदलती है और `save()` call करती है ताकि validators और middleware चलें। TypeScript गारंटी देता है कि `status` सिर्फ allowed literals में से ही होगा।

---

## 💻 Code Example — Basic

```typescript
// order.model.ts — interface + schema + model
import { Schema, model, type HydratedDocument } from "mongoose";

// 1) The plain data shape (what you store and return)
export interface IOrder {
  userId: string;                          // owner
  amount: number;                          // total in rupees
  status: "PLACED" | "PAID" | "DELIVERED"; // literal union: invalid values are compile errors
  items: { sku: string; qty: number }[];   // embedded sub-documents
  createdAt?: Date;                        // set by timestamps option, optional on create
}

// 2) Schema<IOrder>: keys are checked against the interface
const orderSchema = new Schema<IOrder>(
  {
    userId: { type: String, required: true, index: true },        // required string
    amount: { type: Number, required: true, min: 0 },              // number >= 0
    status: { type: String, enum: ["PLACED", "PAID", "DELIVERED"], default: "PLACED" }, // enum validator
    items: [{ sku: { type: String, required: true }, qty: { type: Number, required: true } }],
  },
  { timestamps: true },                                            // adds createdAt/updatedAt
);

// 3) The model
export const Order = model<IOrder>("Order", orderSchema);

// 4) Typed usage
export async function demo(): Promise<void> {
  const created = await Order.create({ userId: "u1", amount: 450, items: [{ sku: "dosa", qty: 2 }] }); // hydrated doc
  console.log(created.amount);                                     // number
  const found: HydratedDocument<IOrder> | null = await Order.findById(created._id); // may be null!
  if (found) {                                                     // narrow before use
    found.status = "PAID";                                         // only allowed literals
    await found.save();                                            // hydrated docs have save()
  }
}
```

## 💻 Code Example — Advanced

```typescript
// advanced: InferSchemaType, lean, methods/statics, aggregate, populate-friendly types
import {
  Schema, model, Types, type Model, type InferSchemaType, type HydratedDocument,
} from "mongoose";

// 1) Define the shape ONCE in the schema; derive the TS type
const productSchema = new Schema(
  {
    name: { type: String, required: true },                // required => string
    price: { type: Number, required: true },               // required => number
    tags: { type: [String], default: [] },                 // string[]
    sellerId: { type: Schema.Types.ObjectId, ref: "Seller", required: true }, // ObjectId
  },
  { timestamps: true },
);
export type IProduct = InferSchemaType<typeof productSchema>;   // derived interface
export type ProductDoc = HydratedDocument<IProduct>;            // hydrated flavour

// 2) Instance method + static, with their types declared
interface IUser { email: string; walletBalance: number }
interface UserMethods { debit(amount: number): boolean }                       // instance method
interface UserModel extends Model<IUser, object, UserMethods> {                // statics
  findByEmail(email: string): Promise<HydratedDocument<IUser, UserMethods> | null>;
}
const userSchema = new Schema<IUser, UserModel, UserMethods>({
  email: { type: String, required: true, unique: true },
  walletBalance: { type: Number, default: 0 },
});
userSchema.method("debit", function debit(amount: number): boolean {            // `this` is the document
  if (this.walletBalance < amount) return false;                                // typed access
  this.walletBalance -= amount;
  return true;
});
userSchema.static("findByEmail", function findByEmail(email: string) {          // `this` is the model
  return this.findOne({ email });
});
export const User = model<IUser, UserModel>("User", userSchema);

export const Product = model("Product", productSchema);

// 3) lean(): plain objects typed explicitly
export async function listProducts(): Promise<(IProduct & { _id: Types.ObjectId })[]> {
  return Product.find({ price: { $lt: 500 } }).lean();                          // plain objects, no save()
}

// 4) Using the method
export async function pay(email: string, amount: number): Promise<boolean> {
  const u = await User.findByEmail(email);                                      // doc | null
  if (!u) return false;                                                         // narrow
  if (!u.debit(amount)) return false;                                           // typed method
  await u.save();
  return true;
}

// 5) Aggregation result types are YOURS to declare (Mongoose cannot infer pipelines)
interface SalesBySeller { _id: Types.ObjectId; total: number }
export async function sales(): Promise<SalesBySeller[]> {
  return Product.aggregate<SalesBySeller>([{ $group: { _id: "$sellerId", total: { $sum: "$price" } } }]);
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express route: ObjectId validation, null handling, lean response typed as the DTO
import express from "express";
import { Schema, model, isValidObjectId } from "mongoose";

interface IOrder { userId: string; amount: number; status: "PLACED" | "PAID" }
const Order = model<IOrder>("Order", new Schema<IOrder>({
  userId: { type: String, required: true },
  amount: { type: Number, required: true },
  status: { type: String, enum: ["PLACED", "PAID"], default: "PLACED" },
}));

const app = express();
app.use(express.json());

app.get("/api/orders/:id", async (req, res) => {
  const id = String(req.params.id);                                 // params are strings
  if (!isValidObjectId(id)) { res.status(400).json({ error: "bad id" }); return; } // else CastError
  const o = await Order.findById(id).lean();                        // plain object | null
  if (!o) { res.status(404).json({ error: "not found" }); return; }
  res.json({ id: String(o._id), amount: o.amount, status: o.status }); // _id (ObjectId) -> string for JSON
});

app.post("/api/orders", async (req, res) => {
  const body = req.body as Partial<IOrder>;                         // validate in real code (zod)
  const doc = await Order.create({ userId: body.userId ?? "", amount: body.amount ?? 0 }); // typed create
  res.status(201).json({ id: String(doc._id) });
});
```

```tsx
// React side: ObjectId arrives as a string, so the UI type uses string ids
interface OrderDTO { id: string; amount: number; status: "PLACED" | "PAID" }
export const OrderBadge = ({ o }: { o: OrderDTO }) => <span>{o.id.slice(-6)} - {o.status}</span>;
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong field type in `create`, and ignoring `null` from `findOne`
```typescript
// ❌ WRONG
import { Schema, model } from "mongoose";
interface U { name: string; age: number }
const sc = new Schema<U>({ name: String, age: Number });
const M = model<U>("U", sc);
async function f() { await M.create({ name: "x", age: "5" }); const d = await M.findOne(); d.name; }
// error TS2769: No overload matches this call.
//   The last overload gave the following error.
//     Type 'string' is not assignable to type 'number'.
// error TS18047: 'd' is possibly 'null'.
```
✅ Correct: `age: 5` and `const d = await M.findOne(); if (d) d.name;`

❌ Mistake 2: Using an `ObjectId` where the DTO expects `string`
`res.json({ id: doc._id })` serializes fine at runtime, but your React type says `string` and the TS type of `_id` is `Types.ObjectId`. ✅ Correct: `String(doc._id)` (or `doc.id`, the virtual string getter on hydrated docs).

❌ Mistake 3: Calling `.save()` on a lean result
`const o = await Order.findById(id).lean(); o.save();` - TS errors because lean objects are plain `IOrder` (no `save`). ✅ Correct: omit `.lean()` when you need to mutate and save.

❌ Mistake 4: Interface and schema drifting apart
If the interface says `status: "PLACED" | "PAID"` but the schema enum has a third value, Mongoose cannot catch it. ✅ Correct: derive the type with `InferSchemaType` or keep enum values in one `as const` array used by both.

---

## 🧠 Tricky Interview Question

```typescript
// Why doesn't TypeScript catch this wrong value?
import { Schema, model } from "mongoose";
interface IOrder { status: "PLACED" | "PAID" }
const Order = model<IOrder>("Order", new Schema<IOrder>({ status: { type: String, enum: ["PLACED", "PAID"] } }));
export async function bad() {
  await Order.updateOne({}, { $set: { status: "SHIPPED" } });
}
```
**Answer:** I compiled this under `strict` - in the Mongoose version tested it type-checks **without any error** in this form, because update filters are loosely typed (`UpdateQuery<T>` allows operator payloads that TypeScript cannot narrow per field in every case). At runtime, `updateOne` does **not run validators by default** either, so `"SHIPPED"` can be written to the database. Fix: pass `{ runValidators: true }`, and prefer load-modify-`save()` for critical writes. Lesson: Mongoose typing protects `create`/`new Model()` best; query/update operators are the weak spot, so validate input with zod before building updates.

---

## ⚫ Interview Questions + Answers

Q1: `HydratedDocument<T>` vs `T` vs `.lean()` result?
A1: `T` is the plain data shape. `HydratedDocument<T>` is `T` + Mongoose document API (`save`, `_id`, `isModified`, virtuals). `.lean()` returns plain objects of `T` (plus `_id`), faster and lower memory, but no methods or getters.

Q2: Interface-first or `InferSchemaType`?
A2: Interface-first gives readable domain types and is checked against the schema (`Schema<IOrder>`). `InferSchemaType` removes duplication but hides the type behind a derived alias; good when the schema is the source of truth. Both work in Mongoose 6+.

Q3: Why does `findById` return `| null`?
A3: A missing document is not an error; it resolves to `null`. TS forces you to branch. Use `findById(...).orFail()` to throw instead and get a non-null type.

Q4: How do you type `populate`?
A4: Declare the ref field as `Types.ObjectId`, and use `populate<{ seller: ISeller }>("seller")` so the result type replaces the id with the populated object. Without the generic, the populated field stays typed as an id.

Q5: Mongoose vs native `mongodb` driver typing?
A5: Native driver: `collection<IOrder>("orders")` types filters/updates with `Filter<T>`/`UpdateFilter<T>` (stricter on query paths) but no validation/middleware. Mongoose adds schema validation, hooks, virtuals and population, at the cost of looser query typing and an extra abstraction.

---

## 🔷 When to Use + When Not to Use
✅ Use Mongoose + TS when:
- You want validation, defaults, hooks and population with typed models
- Documents have a stable shape worth enforcing (orders, users, catalog)

❌ Avoid / be careful when:
- You need very dynamic documents (use native driver + `Collection<T>`)
- Heavy analytics/pipelines (types are manual)
- You rely on TS alone for correctness - add runtime validation (zod) at the API edge

---

## 📊 Visual Diagram
```
interface IOrder ──► new Schema<IOrder>() ──► model<IOrder>("Order")
                                                   │
        create / new Order()  ──► HydratedDocument<IOrder>   (save, _id, virtuals)
        findById()            ──► HydratedDocument<IOrder> | null
        find().lean()         ──► IOrder & { _id }  (plain object, no save)
        aggregate<T>()        ──► T[]   (you declare T)

Express: String(doc._id) ──► JSON ──► React OrderDTO { id: string }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Mongoose definition of a document | document की Mongoose definition |
| HydratedDocument | Full Mongoose doc with methods | methods वाला पूरा Mongoose doc |
| lean() | Return plain JS objects | plain JS objects लौटाना |
| InferSchemaType | Derive TS type from schema | schema से TS type निकालना |
| populate | Replace ids with referenced docs | ids की जगह referenced docs |
| ObjectId | MongoDB's 12-byte id type | MongoDB का 12-byte id type |

---

## ⚡ 3-Line Summary
English:
1. Pass an interface to `Schema<T>` and `model<T>`; `create` is checked, `findOne` returns `Doc | null`.
2. Use `.lean()` for read-only plain objects, hydrated docs when you need `save()`; `InferSchemaType` avoids duplication.
3. Updates/aggregations are loosely typed and validators are off by default - validate input at the edge.

Hindi:
1. `Schema<T>` और `model<T>` में interface दो; `create` check होता है, `findOne` `Doc | null` देता है।
2. Read-only plain objects के लिए `.lean()`, `save()` चाहिए तो hydrated docs; `InferSchemaType` duplication हटाता है।
3. Updates/aggregations का typing ढीला है और validators default में बंद हैं - input को edge पर validate करो।

---

## ➡️ Next Topic
**98. TypeScript with NestJS Basics** — decorators, DI, DTOs and typed controllers.
