# 86. Runtime Validation with Zod + z.infer
# हिंदी में: Zod से Runtime Validation + z.infer

> Verified with **TypeScript 5.9.x** and **zod 4.x** (outputs below are real `tsx` output; error message wording differs slightly in zod 3). `z.infer`, `z.input`, `z.output` exist in zod 3 and 4.

---

## 🔵 Simple Definition (English)
**Zod** is a schema library: you describe the shape of data **once** as a runtime object (`z.object({...})`), and Zod gives you (a) a **validator** that checks real data (`parse`, `safeParse`) and (b) the matching **TypeScript type** via `z.infer<typeof schema>`. One source of truth for runtime checks and compile-time types.

## 🔵 सरल परिभाषा (Hindi)
**Zod** एक schema library है: आप data की shape **एक बार** runtime object (`z.object({...})`) में लिखते हैं, और Zod देता है (a) **validator** जो असली data जाँचता है (`parse`, `safeParse`) और (b) उसी से बना **TypeScript type** `z.infer<typeof schema>` के ज़रिए। Runtime checks और compile-time types के लिए एक ही source of truth।

---

## 🔴 Problem it Solves
TypeScript types are **erased**. `req.body: CreateOrderDto` is only a hope — a client (or attacker) can POST `{ "qty": "DROP TABLE" }`. Writing an `interface` plus a separate hand-written validator means two sources that drift apart. Zod unifies them: change the schema and both the runtime check and the type update together.

## 🔴 यह क्यों बना? (Hindi)
TypeScript types **erase** हो जाते हैं। `req.body: CreateOrderDto` सिर्फ उम्मीद है — client (या attacker) `{ "qty": "DROP TABLE" }` भेज सकता है। `interface` और अलग से हाथ से लिखा validator दो sources बनाते हैं जो अलग-अलग हो जाते हैं। Zod दोनों को जोड़ देता है: schema बदलो तो runtime check और type साथ में बदलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm i zod`. Build a schema with primitives: `z.string()`, `z.number()`, `z.enum([...])`, `z.object({...})`, `z.array(...)`.
Step 2 → Add refinements: `.min(1)`, `.email()`, `.int().positive()`, `.optional()`, `.default(...)`.
Step 3 → Derive the type: `type CreateOrderDto = z.infer<typeof CreateOrder>`.
Step 4 → Validate unknown data: `schema.parse(x)` (throws `ZodError`) or `schema.safeParse(x)` (returns `{ success, data | error }`, a discriminated union).
Step 5 → Transform at the boundary: `z.coerce.number()` for query strings, `.transform(...)` for derived values. Then **input type ≠ output type** → `z.input<>` vs `z.output<>` (`z.infer` = output).
Step 6 → Plug into Express as middleware so handlers receive already-validated, correctly-typed data.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm i zod`। Primitives से schema बनाओ: `z.string()`, `z.number()`, `z.enum([...])`, `z.object({...})`, `z.array(...)`।
Step 2 → Refinements जोड़ो: `.min(1)`, `.email()`, `.int().positive()`, `.optional()`, `.default(...)`।
Step 3 → Type निकालो: `type CreateOrderDto = z.infer<typeof CreateOrder>`।
Step 4 → Unknown data validate करो: `schema.parse(x)` (`ZodError` throw) या `schema.safeParse(x)` (`{ success, data | error }` लौटाता है, discriminated union)।
Step 5 → Boundary पर transform: query strings के लिए `z.coerce.number()`, derived values के लिए `.transform(...)`। तब **input type ≠ output type** → `z.input<>` बनाम `z.output<>` (`z.infer` = output)।
Step 6 → Express में middleware बनाकर लगाओ ताकि handlers को validated, सही typed data मिले।

---

## 🟡 Real World Example
A **Razorpay "create payment link"** endpoint accepts `{ amount, currency, customer: { email, phone }, notes? }`. `amount` must be an integer ≥ 100 (paise), `currency` one of `INR|USD`, `email` valid. The same schema validates the request on the server and drives the TypeScript type used by the React form — no duplicated rules.

## 🟡 Real Example Hindi mein
**Razorpay का "create payment link"** endpoint `{ amount, currency, customer: { email, phone }, notes? }` लेता है। `amount` integer ≥ 100 (paise), `currency` `INR|USD` में से, `email` valid होना चाहिए। वही schema server पर request validate करता है और React form के TypeScript type को भी चलाता है — rules दोहराने की ज़रूरत नहीं।

---

## 💻 Code Example — Basic

```typescript
// zod-basic.ts — run: npx tsx zod-basic.ts
import { z } from "zod"; // schema library

// 1) Describe the shape ONCE at runtime
const CreateOrder = z.object({
  userId: z.string().min(1),                 // non-empty string
  items: z.array(                            // array of line items
    z.object({
      sku: z.string(),                       // product id
      qty: z.coerce.number().int().positive(), // "2" (from query/form) -> 2, must be a positive int
    }),
  ).min(1),                                  // at least one item
  couponCode: z.string().optional(),         // string | undefined
});

// 2) Derive the TypeScript type FROM the schema (no separate interface to maintain)
type CreateOrderDto = z.infer<typeof CreateOrder>;
// => { userId: string; items: { sku: string; qty: number }[]; couponCode?: string | undefined }

// 3) Validate unknown data. safeParse never throws.
const good = CreateOrder.safeParse({ userId: "u1", items: [{ sku: "p1", qty: "2" }] });
console.log(good.success, good.success && good.data);
// real output: true { userId: 'u1', items: [ { sku: 'p1', qty: 2 } ] }   <- qty coerced to number 2

const bad = CreateOrder.safeParse({ userId: "", items: [] });
if (!bad.success) {                           // discriminated union: error exists only when success is false
  console.log(JSON.stringify(bad.error.flatten()));
  // real output (zod 4):
  // {"formErrors":[],"fieldErrors":{"userId":["Too small: expected string to have >=1 characters"],"items":["Too small: expected array to have >=1 items"]}}
}

// 4) After validation, TS knows the exact type
function total(dto: CreateOrderDto): number {
  return dto.items.reduce((s, i) => s + i.qty, 0); // i.qty is number (not string) thanks to coerce
}
if (good.success) console.log(total(good.data)); // 2
```

```typescript
// ❌ The inferred type is real: assigning a wrong type fails at compile time
import { z } from "zod";
const Order = z.object({ id: z.string(), total: z.number() });
type OrderT = z.infer<typeof Order>;
const o: OrderT = { id: "o1", total: "10" };
// error TS2322: Type 'string' is not assignable to type 'number'.
```

## 💻 Code Example — Advanced

```typescript
// zod-advanced.ts — input vs output, enums, discriminated unions, refine, Express middleware
import { z } from "zod";
import type { Request, Response, NextFunction, RequestHandler } from "express";

// transform => input type differs from output type
const Pagination = z.object({
  page: z.coerce.number().int().min(1).default(1),   // "3" -> 3, missing -> 1
  limit: z.coerce.number().int().min(1).max(100).default(20),
});
type PageIn = z.input<typeof Pagination>;  // what callers may pass (page?: unknown...)
type PageOut = z.output<typeof Pagination>; // what you receive after parsing (z.infer is the same as output)
const p: PageOut = Pagination.parse({ page: "3" });
console.log(p); // { page: 3, limit: 20 }

// z.enum -> string union type; discriminatedUnion -> tagged union (topic 26)
const PaymentMethod = z.discriminatedUnion("type", [
  z.object({ type: z.literal("upi"), vpa: z.string().includes("@") }),            // UPI needs a VPA
  z.object({ type: z.literal("card"), last4: z.string().length(4), network: z.enum(["visa", "rupay"]) }),
]);
type PaymentMethod = z.infer<typeof PaymentMethod>; // same name for value and type is allowed
function describe(m: PaymentMethod): string {
  switch (m.type) {                                  // narrowing works on the inferred union
    case "upi":  return `UPI ${m.vpa}`;              // m.vpa is string here
    case "card": return `${m.network} ****${m.last4}`; // m.last4 is string here
  }
}
console.log(describe({ type: "upi", vpa: "a@okaxis" })); // UPI a@okaxis

// refine for cross-field rules
const Refund = z.object({ paid: z.number(), refund: z.number() })
  .refine((r) => r.refund <= r.paid, { message: "refund exceeds paid", path: ["refund"] });
console.log(Refund.safeParse({ paid: 100, refund: 150 }).success); // false

// Generic validate middleware: schema in, typed + parsed body out
function validateBody<S extends z.ZodType>(schema: S): RequestHandler<{}, unknown, z.output<S>> {
  return (req: Request, res: Response, next: NextFunction) => {
    const parsed = schema.safeParse(req.body);        // validate untrusted body
    if (!parsed.success) {
      res.status(400).json({ error: { code: "VALIDATION", details: z.flattenError(parsed.error) } }); // zod 4 helper
      return;                                         // stop
    }
    req.body = parsed.data;                           // replace with the coerced/clean data
    next();                                           // handler now receives validated body
  };
}
export { validateBody };
```

---

## 🟠 Node/Express + React Integration

```typescript
// shared/schemas.ts — the SAME schema file imported by Express and React
import { z } from "zod";

export const LoginSchema = z.object({
  email: z.string().email(),            // zod 4 also offers z.email()
  password: z.string().min(8),          // simple rule shared by UI + API
});
export type LoginInput = z.infer<typeof LoginSchema>; // { email: string; password: string }
```

```typescript
// server: handler gets a validated body
import express from "express";
import { LoginSchema, type LoginInput } from "./shared/schemas";

const app = express();
app.use(express.json());
app.post("/login", (req, res) => {
  const parsed = LoginSchema.safeParse(req.body); // never trust req.body
  if (!parsed.success) { res.status(400).json(parsed.error.issues); return; }
  const input: LoginInput = parsed.data;          // fully typed
  res.json({ ok: true, email: input.email });
});
```

```typescript
// React: validate before submit (same schema) — works with react-hook-form via @hookform/resolvers/zod
import { LoginSchema } from "./shared/schemas";

export function validateForm(values: unknown): string | null {
  const r = LoginSchema.safeParse(values);              // same rules as the server
  return r.success ? null : r.error.issues[0]?.message ?? "Invalid"; // first message for the UI
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Writing both an `interface` and a zod schema by hand — they drift.
✅ `type T = z.infer<typeof Schema>` only.

❌ Mistake 2: `schema.parse(x) as T` or `x as T` instead of parsing.
✅ Parse the unknown value; use the returned `data`.

❌ Mistake 3: Using `z.infer` when the schema has `.transform()/.default()/coerce` and you need the **input**. ✅ `z.input<typeof S>` for what callers send, `z.output<typeof S>` (= `z.infer`) for what you receive.

❌ Mistake 4: Using `z.number()` for query params — `req.query.page` is a string, so validation fails. ✅ `z.coerce.number()`. Beware: `z.coerce.boolean()` turns `"false"` into `true` (any non-empty string). Use `z.enum(["true","false"]).transform(v => v === "true")`.

❌ Mistake 5: Validating only on the client (React). ✅ Always on the server; client validation is UX only.

❌ Mistake 6: Putting heavy schemas inside request handlers (rebuilt per request). ✅ Define schemas at module scope.

---

## 🧠 Tricky Interview Question
**Q:** "`const S = z.object({ n: z.string().transform(s => s.length), d: z.string().default('x') })`. What are `z.input<typeof S>` and `z.infer<typeof S>`?"

**A:** `z.input<typeof S>` is `{ n: string; d?: string | undefined }` (what you pass in: `n` is a string, `d` may be omitted). `z.infer<typeof S>` (= `z.output`) is `{ n: number; d: string }` (what you get out: `n` became its length, `d` is always present). I verified this on the compiler: `const i: In = { n: "abc" }; const o: Out = S.parse(i);` compiles, and `console.log(o)` prints `{ n: 3, d: 'x' }`.

---

## ⚫ Interview Questions + Answers

Q1: Why isn't a TypeScript interface enough for API input?
A1: Interfaces vanish at runtime; JSON from the network is unchecked. You need a runtime validator, and zod derives the static type from it so both agree.

Q2: `parse` vs `safeParse`?
A2: `parse` throws `ZodError` on failure (good with a central error middleware). `safeParse` returns `{ success: true, data } | { success: false, error }` — a discriminated union that TS narrows, good for handling errors inline.

Q3: How does `z.infer` work conceptually?
A3: Each schema class carries phantom generic parameters for its output (and input) types; `z.infer<T>` extracts `T["_output"]` with an indexed-access type. No runtime cost — it is purely type-level.

Q4: How do you handle optional vs nullable vs nullish?
A4: `.optional()` → `T | undefined` (key may be missing); `.nullable()` → `T | null`; `.nullish()` → both. Match your JSON/SQL: SQL Server NULL arrives as `null`, absent JSON keys as `undefined`.

Q5: How would you share validation between Express and React?
A5: Put schemas in a shared package or folder (monorepo), export both schema and `z.infer` types, use the schema in server middleware and in the React form resolver. Keep server-only rules (DB uniqueness) out of the shared file.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any untrusted input: request body/query/params, env vars (topic 87), third-party API responses, localStorage
- You want a single source of truth for types

❌ Avoid when:
- Hot inner loops over millions of items (validation has a cost — validate at the boundary only)
- Pure internal function calls between trusted modules — plain types are enough
- Bundle size is critical in the browser and you only need a trivial check (consider zod/mini or valibot)

---

## 📊 Visual Diagram
```
           z.object({ ... })   ← written ONCE
              │            │
   runtime ◄──┘            └──► compile time
  schema.safeParse(x)         type T = z.infer<typeof schema>
        │                               │
  { success, data/error }        used in handlers, services, React props
        ▼
   unknown JSON ──validate──► typed, clean data (or 400 error)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Runtime description of a shape | Runtime पर shape का वर्णन |
| `z.infer` | Type derived from a schema | Schema से निकला type |
| `safeParse` | Validate without throwing | बिना throw किए validate |
| Coercion | Convert type during parse | Parse के दौरान type बदलना |
| `transform` | Change value after validation | Validation के बाद value बदलना |
| `z.input` / `z.output` | Types before / after parsing | Parse से पहले / बाद के types |
| Refinement | Custom validation rule | Custom validation नियम |

---

## ⚡ 3-Line Summary
English:
1. Zod defines a schema once and gives both runtime validation and the TS type via `z.infer`.
2. Use `safeParse`/`parse` at every boundary (body, query, env); `z.coerce` for strings; `z.input` vs `z.output` when transforms exist.
3. Validate on the server always; share schemas with React for the same rules.

Hindi:
1. Zod schema एक बार define करता है और runtime validation व `z.infer` से TS type दोनों देता है।
2. हर boundary (body, query, env) पर `safeParse`/`parse`; strings के लिए `z.coerce`; transforms हों तो `z.input` बनाम `z.output`।
3. Validation हमेशा server पर; वही नियम पाने के लिए schemas React के साथ share करो।

---

## ➡️ Next Topic
**87. Typed Environment Config** — validate `process.env` once at startup with zod and export a typed `config`.
