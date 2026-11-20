# 115. TypeScript Interview Classics — 30 Most Asked Questions
# हिंदी में: TypeScript Interview के 30 सबसे ज़्यादा पूछे जाने वाले सवाल

> TypeScript 5.x | हर code block `tsc --strict` (TS 5.9) से verify हुआ; runnable blocks `npx tsx` से चलाकर असली output दिया है। TS-version-dependent: `satisfies` = **4.9**, `const enum`/enum union semantics = **5.0**, decorators (standard) = **5.0**, `using` = **5.2**, `NoInfer` = **5.4**, `moduleResolution: bundler` = **5.0**।

---

## 🔵 Simple Definition (English)
This is the **revision capsule** of the whole TypeScript course: 30 questions that appear again and again in senior full-stack interviews, grouped as (A) type basics, (B) generics and advanced types, (C) your stack (Express, Zod, React, Redux Toolkit) and (D) config/tooling. Every answer is short enough to say out loud in 30 seconds and backed by compiler-verified code.

## 🔵 सरल परिभाषा (Hindi)
यह पूरे TypeScript course का **revision capsule** है: 30 सवाल जो senior full-stack interviews में बार-बार आते हैं, चार groups में: (A) type basics, (B) generics और advanced types, (C) आपका stack (Express, Zod, React, Redux Toolkit), (D) config/tooling। हर जवाब 30 सेकंड में बोलने लायक छोटा है और compiler-verified code से पक्का किया गया है।

---

## 🔴 Problem it Solves
At 8-10 years, interviewers do not ask "what is a type"; they ask *why* `unknown` beats `any`, *when* `satisfies` beats `as`, *how* you type an Express `req.user`, and *what* breaks if you turn on `noUncheckedIndexedAccess`. Candidates fail by giving textbook definitions with no trade-off. This note gives the trade-off, the code, and the exact error message for each classic.

## 🔴 यह क्यों बना? (Hindi)
8-10 साल के अनुभव पर interviewer "type क्या है" नहीं पूछते; वे पूछते हैं कि `unknown` `any` से बेहतर *क्यों* है, `satisfies` `as` से कब बेहतर है, Express में `req.user` कैसे type करोगे, और `noUncheckedIndexedAccess` चालू करने पर क्या टूटेगा। Candidates सिर्फ textbook definition देकर, trade-off बताए बिना, फेल होते हैं। यह note हर classic का trade-off, code और असली error message देता है।

---

## 🟢 How it Works — Step by Step
Step 1 → Read the question group (A-D) that matches the interview round.
Step 2 → Say the one-line answer first, then the trade-off, then a tiny example (the pattern used below).
Step 3 → Run the matching code block with `npx tsx` / `tsc --noEmit --strict` to see it yourself.
Step 4 → For every "why" answer, name the compiler flag or TS version involved (`strictNullChecks`, TS 4.9 ...).
Step 5 → Practise the tricky question aloud (array covariance below), because interviewers love unsoundness.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → जिस round का interview है, उससे मेल खाता group (A-D) पढ़ो।
Step 2 → पहले एक लाइन का जवाब, फिर trade-off, फिर छोटा example (नीचे यही pattern है)।
Step 3 → संबंधित code block `npx tsx` / `tsc --noEmit --strict` से खुद चलाओ।
Step 4 → हर "क्यों" वाले जवाब में compiler flag या TS version का नाम लो (`strictNullChecks`, TS 4.9 ...)।
Step 5 → Tricky question (नीचे array covariance) ज़ोर से बोलकर practise करो, क्योंकि interviewers unsoundness पसंद करते हैं।

---

## 🟡 Real World Example
A **Razorpay-style checkout** interview round: "Design the types for `POST /orders`." A strong answer chains classics: Zod schema with `z.infer` (Q22) for the body, branded `OrderId` (Q18), a discriminated union for payment events with an exhaustive `never` check (Q6), `req.user` via declaration merging (Q23), and `noUncheckedIndexedAccess` (Q21) for the cart map. Five classics, one coherent design.

## 🟡 Real Example Hindi mein
**Razorpay जैसे checkout** के interview round में सवाल: "`POST /orders` के types design करो।" मजबूत जवाब कई classics जोड़ता है: body के लिए `z.infer` वाला Zod schema (Q22), branded `OrderId` (Q18), payment events के लिए exhaustive `never` check वाला discriminated union (Q6), `req.user` declaration merging से (Q23), और cart map के लिए `noUncheckedIndexedAccess` (Q21)। पाँच classics, एक सुसंगत design।

---

## 💻 Code Example — Basic

Covers Q1-Q10. Run with `npx tsx`.

```typescript
// Q1-Q10: language basics, runnable (npx tsx)

// Q1 interface vs type: interface merge hota hai, type union/mapped bana sakta hai
interface Cart { items: string[] }
interface Cart { total: number } // declaration merging: Cart ab dono fields rakhta hai
type PayMode = 'upi' | 'card' | 'cod'; // union sirf type alias se

// Q2 any vs unknown vs never
function parse(raw: unknown): number { // unknown: use karne se pehle check zaroori
  if (typeof raw === 'number') return raw;
  if (typeof raw === 'string' && raw.trim() !== '') return Number(raw);
  throw new Error('not a number');
}
function fail(msg: string): never { throw new Error(msg); } // never: kabhi return nahi karta

// Q3 enum ka alternative: as const object + union
const Status = { Placed: 'placed', Paid: 'paid', Delivered: 'delivered' } as const; // Q4 as const
type Status = (typeof Status)[keyof typeof Status]; // 'placed' | 'paid' | 'delivered'

// Q5 satisfies (TS 4.9+): type check bhi, literal type bhi bachta hai
const fees = { upi: 0, card: 2, cod: 15 } satisfies Record<PayMode, number>;
const upiFee = fees.upi; // type: number (not just from Record index)

// Q6 discriminated union + exhaustive check
type OrderEvent =
  | { kind: 'placed'; orderId: string }
  | { kind: 'paid'; orderId: string; paise: number }
  | { kind: 'cancelled'; reason: string };
function describe(e: OrderEvent): string {
  switch (e.kind) {
    case 'placed': return `placed ${e.orderId}`;
    case 'paid': return `paid ${e.paise / 100} for ${e.orderId}`;
    case 'cancelled': return `cancelled: ${e.reason}`;
    default: { const _never: never = e; return fail(`unhandled ${JSON.stringify(_never)}`); } // naya kind aaya to yahin error
  }
}

// Q7 user-defined type guard
function isPaid(e: OrderEvent): e is Extract<OrderEvent, { kind: 'paid' }> { return e.kind === 'paid'; }

// Q8 structural typing: shape match hota hai, naam nahi
interface HasId { id: number }
const row = { id: 1, name: 'Biryani' };
const hasId: HasId = row; // extra field 'name' theek hai (variable, literal nahi)

// Q9 keyof + generics
function pluck<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }

// Q10 readonly + tuple
const point: readonly [number, number] = [28.6, 77.2];

const cart: Cart = { items: ['pizza'], total: 299 };
console.log(parse('42'), cart.total, upiFee, Status.Paid);
console.log(describe({ kind: 'paid', orderId: 'O1', paise: 49900 }));
console.log(isPaid({ kind: 'placed', orderId: 'O2' }), hasId.id, pluck(row, 'name'), point);
// OUTPUT:
// 42 299 0 paid
// paid 499 for O1
// false 1 Biryani [ 28.6, 77.2 ]
```

## 💻 Code Example — Advanced

Covers Q11-Q21 (generics, conditionals, brands, `#private`).

```typescript
// Q11-Q22: generics, advanced types (runnable)

// Q11 generic constraint + default
interface Repo<T extends { id: number }, K = T['id']> { get(id: K): T | undefined }
const orders: Repo<{ id: number; paise: number }> = { get: (id) => (id === 1 ? { id, paise: 500 } : undefined) };

// Q12 mapped type + utility types
type Dto = { id: number; name: string; email: string };
type Patch = Partial<Omit<Dto, 'id'>>; // id nahi badal sakte, baaki optional
type Flags<T> = { [K in keyof T]: boolean };

// Q13 conditional + infer
type Unwrap<T> = T extends Promise<infer U> ? U : T;
type Item<T> = T extends (infer E)[] ? E : never;

// Q14 distributive conditional
type ToArray<T> = T extends unknown ? T[] : never;
type D1 = ToArray<string | number>; // string[] | number[]
type ND = [string | number] extends [unknown] ? (string | number)[] : never; // (string|number)[]

// Q15 template literal
type Handler<E extends string> = `on${Capitalize<E>}`;
type H = Handler<'click' | 'submit'>; // 'onClick' | 'onSubmit'

// Q16 overloads
function toId(x: string): string;
function toId(x: number): number;
function toId(x: string | number) { return x; }
const a = toId('a'); // string
const b = toId(5); // number

// Q17 this parameter
function greet(this: { name: string }) { return `Hi ${this.name}`; }

// Q18 branded types
type Brand<T, B extends string> = T & { readonly __brand: B };
type UserId = Brand<number, 'UserId'>;
type OrderId = Brand<number, 'OrderId'>;
const mkUser = (n: number) => n as UserId;
const mkOrder = (n: number) => n as OrderId;
function cancel(id: OrderId) { return `cancel ${id}`; }

// Q19 private (compile-time) vs #private (runtime)
class Wallet {
  private paise = 100; // sirf TS check
  #secret = 'k'; // real JS private
  reveal() { return this.#secret; }
}
const w = new Wallet();
console.log(Object.keys(w), (w as unknown as { paise: number }).paise); // 'paise' runtime pe dikhta hai

// Q20 catch variable unknown (useUnknownInCatchVariables, strict me on)
try { JSON.parse('{bad'); } catch (err) {
  console.log(err instanceof SyntaxError ? 'bad json' : 'other'); // err: unknown, narrow karo
}

// Q21 noUncheckedIndexedAccess-style safe lookup
const prices: Record<string, number> = { pizza: 299 };
const p: number | undefined = prices['burger']; // runtime me undefined, type me bhi dhyan do
console.log(p ?? 0);

console.log(orders.get(1), greet.call({ name: 'Aditya' }), a, b, cancel(mkOrder(9)), mkUser(1));
const x: D1 = ['a'];
const y: ND = [1, 'a'];
const f: Flags<Dto> = { id: true, name: false, email: true };
const pa: Patch = { name: 'N' };
const hh: H = 'onClick';
const un: Unwrap<Promise<number>> = 1;
const it: Item<string[]> = 'x';
console.log(x, y, f, pa, hh, un, it);
// OUTPUT:
// [ 'paise' ] 100
// bad json
// 0
// { id: 1, paise: 500 } Hi Aditya a 5 cancel 9 1
// [ 'a' ] [ 1, 'a' ] { id: true, name: false, email: true } { name: 'N' } onClick 1 x
```

---

## 🟠 Node/Express + React Integration

**Express + Zod (Q22-Q24)**: schema, `z.infer`, `req.user` merging, typed error middleware.

```typescript
import express from 'express';
import { z } from 'zod';

// Q22 Zod: runtime validation + z.infer se type (single source of truth)
const CreateOrder = z.object({
  userId: z.number().int().positive(),
  items: z.array(z.object({ sku: z.string(), qty: z.number().int().min(1) })).min(1),
  mode: z.enum(['upi', 'card', 'cod']),
});
type CreateOrderInput = z.infer<typeof CreateOrder>; // compile-time type, schema se hi

// Q23 declaration merging: Express Request me user jodna
declare global {
  namespace Express {
    interface Request { user?: { id: number; role: 'admin' | 'customer' } }
  }
}

// Q24 typed error class + unknown error narrowing
class HttpError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

const app = express();
app.use(express.json());
app.use((req, _res, next) => { req.user = { id: 1, role: 'customer' }; next(); }); // auth stub

app.post('/orders', (req, res) => {
  const parsed = CreateOrder.safeParse(req.body); // req.body: any, ab validate hua
  if (!parsed.success) return res.status(400).json(parsed.error.flatten());
  const input: CreateOrderInput = parsed.data;
  res.status(201).json({ by: req.user?.id, count: input.items.length });
});

app.use((err: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  if (err instanceof HttpError) return res.status(err.status).json({ error: err.message });
  res.status(500).json({ error: 'internal' });
});

const ok = CreateOrder.safeParse({ userId: 1, items: [{ sku: 'p', qty: 2 }], mode: 'upi' });
const bad = CreateOrder.safeParse({ userId: -1, items: [], mode: 'cash' });
console.log(ok.success, bad.success);
export default app;
// OUTPUT:
// true false
```

**React + Redux Toolkit (Q25-Q26)**: typed hooks, `ReactNode` children, event types.

```tsx
import { useState, type ChangeEvent, type ReactNode } from 'react';
import { configureStore, createSlice, type PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, type TypedUseSelectorHook } from 'react-redux';

// Q25 Redux Toolkit: RootState + AppDispatch infer hote hain, hand-write nahi
const cart = createSlice({
  name: 'cart',
  initialState: { items: {} as Record<string, number> },
  reducers: { add(s, a: PayloadAction<{ sku: string; qty: number }>) { s.items[a.payload.sku] = (s.items[a.payload.sku] ?? 0) + a.payload.qty; } },
});
const store = configureStore({ reducer: { cart: cart.reducer } });
type RootState = ReturnType<typeof store.getState>;
type AppDispatch = typeof store.dispatch;
const useAppDispatch: () => AppDispatch = useDispatch; // typed hooks, pure app me yahi use karo
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// Q26 React: props, children, events, useState with union
interface CardProps { title: string; children?: ReactNode }
function Card({ title, children }: CardProps) { return <section><h2>{title}</h2>{children}</section>; }

function Search() {
  const [q, setQ] = useState(''); // string infer
  const [err, setErr] = useState<string | null>(null); // union dena padta hai
  const dispatch = useAppDispatch();
  const count = useAppSelector((s) => Object.keys(s.cart.items).length);
  const onChange = (e: ChangeEvent<HTMLInputElement>) => { setQ(e.target.value); setErr(null); };
  return (
    <Card title={`Cart (${count})`}>
      <input value={q} onChange={onChange} />
      <button onClick={() => dispatch(cart.actions.add({ sku: q, qty: 1 }))}>Add</button>
      {err && <p>{err}</p>}
    </Card>
  );
}
export { Search };
```

---

## ⚠️ Common Mistakes to Avoid

❌ Q27: the classic compiler errors (each line is a separate mistake).

```typescript
// Q27 Mistakes
let a: any = 'x'; a.foo(); // any: koi error nahi, runtime crash
const n: number = 'five'; // ❌
interface Order { id: number }
const o: Order = { id: 1, status: 'paid' }; // ❌ excess property
function f(x: string | number) { return x.toFixed(); } // ❌ narrowing nahi
const fees = { upi: 0 } as const; fees.upi = 1; // ❌ readonly
const el = document.getElementById('x'); el.value = '1'; // ❌ possibly null
function h(x: unknown) { return x.length; } // ❌ unknown
// error TS2322: Type 'string' is not assignable to type 'number'.
// error TS2353: Object literal may only specify known properties, and 'status' does not exist in type 'Order'.
// error TS2339: Property 'toFixed' does not exist on type 'string | number'.
//   Property 'toFixed' does not exist on type 'string'.
// error TS2540: Cannot assign to 'upi' because it is a read-only property.
// error TS18047: 'el' is possibly 'null'.
// error TS2339: Property 'value' does not exist on type 'HTMLElement'.
// error TS18046: 'x' is of type 'unknown'.
// (line 1, `a.foo()` on `any`, compiles silently: that is the danger of any)
```

✅ Fixes: annotate/convert correctly, remove extra property or extend the interface, narrow with `typeof`, do not mutate `as const`, check `el instanceof HTMLInputElement`, narrow `unknown` before use.

---

## 🧠 Tricky Interview Question

**"Does this compile? What happens at runtime?"**

```typescript
class Animal { name = 'animal'; }
class Dog extends Animal { bark() { return 'woof'; } }
class Cat extends Animal { meow() { return 'meow'; } }

const dogs: Dog[] = [new Dog()];
const animals: Animal[] = dogs; // compiles: arrays covariant (unsound by design)
animals.push(new Cat()); // compiles too! dogs me ab Cat hai
try { dogs.forEach((d) => d.bark()); } catch (e) { console.log((e as Error).message); }
// OUTPUT:
// d.bark is not a function
```

Answer: It **compiles**, and crashes at runtime. Arrays are treated **covariantly** (`Dog[]` is assignable to `Animal[]`) even though `push` makes that unsound. TypeScript deliberately trades soundness for convenience. Method parameters are also **bivariant** (the `strictFunctionTypes` flag only tightens *function-typed properties*, not methods). Fixes: declare `readonly Animal[]` / `ReadonlyArray<Animal>` when you only read, or copy (`[...dogs]`). Hindi: arrays covariant हैं, इसलिए compile होता है पर runtime पर फटता है; सिर्फ पढ़ना हो तो `readonly Animal[]` लो।

---

## ⚫ Interview Questions + Answers (30 Classics)

**A. Types basics (Q1-Q10, code: Basic block)**

Q1: `interface` vs `type`?
A1: Both describe object shapes. `interface` supports declaration merging and `extends`; `type` supports unions, tuples, mapped/conditional types. Rule: `interface` for public object contracts and class `implements`, `type` for unions and computed types. Hindi: object contract के लिए `interface`, union/computed के लिए `type`।

Q2: `any` vs `unknown` vs `never`?
A2: `any` turns checking off. `unknown` is the safe top type: you must narrow before use. `never` is the empty type: functions that throw, impossible branches. Hindi: `unknown` = "पता नहीं, पहले जाँचो"; `any` = "जाँच बंद"।

Q3: Enums or something else?
A3: Numeric enums emit runtime code and accept any number (pre-5.0). Prefer a union of string literals or an `as const` object. `const enum` is inlined but problematic with `isolatedModules`. TS 5.0 made all enums union enums.

Q4: What does `as const` do?
A4: Freezes the type: deep `readonly`, literals not widened (`'paid'`, not `string`), arrays become readonly tuples. Used for route tables, status maps, action types.

Q5: `satisfies` (TS 4.9) vs `as` vs annotation?
A5: Annotation widens to the annotated type; `as` overrides the checker (unsafe); `satisfies` checks against a type but keeps the precise inferred type. Use it for config objects.

Q6: How do discriminated unions and exhaustive checks work?
A6: A shared literal field (`kind`) lets `switch` narrow each branch. In `default`, assign to `never`; adding a new member makes that line a compile error. Hindi: नया `kind` जोड़ते ही compiler बताता है कौन-सी जगह भूली।

Q7: Type guards vs assertion functions?
A7: `x is T` returns boolean and narrows in the `true` branch; `asserts x is T` throws or narrows the rest of the scope. Make sure the body really matches the claim: TypeScript trusts you.

Q8: Structural typing and excess property checks?
A8: Compatibility is by shape, not name. Fresh object **literals** are checked for extra properties; a variable holding the same object is not (see `hasId = row`).

Q9: Why `K extends keyof T`?
A9: It ties the key to the object so `pluck(row, 'nmae')` fails and the return type is exactly `T[K]`.

Q10: `readonly` and tuples?
A10: `readonly` is compile-time only (no runtime freeze). Tuples fix length and per-position types; `readonly [number, number]` stops mutation and is not assignable to a mutable tuple.

**B. Generics and advanced types (Q11-Q21, code: Advanced block)**

Q11: Constraints and defaults?
A11: `T extends X` limits what callers may pass; `K = T['id']` supplies a default. Constrain as little as the body needs.

Q12: Utility types you must know?
A12: `Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`, `Exclude`, `Extract`, `NonNullable`, `ReturnType`, `Parameters`, `Awaited`. `Patch = Partial<Omit<Dto, 'id'>>` is the standard PATCH payload.

Q13: Conditional types and `infer`?
A13: `T extends U ? X : Y` branches on types; `infer` captures a part (`Promise<infer U>`). It is the type-level `if` plus pattern matching.

Q14: What is a distributive conditional type?
A14: With a naked `T`, the conditional runs per union member (`ToArray<string | number>` = `string[] | number[]`). Wrap in `[T]` to prevent it. `never` yields `never` (note 114).

Q15: Template literal types?
A15: String types computed from other types: `on${Capitalize<E>}`. Combined with `infer` they parse strings (note 112).

Q16: Overloads: when and how?
A16: Several call signatures plus one implementation signature (invisible to callers). Prefer a generic or a union when it can express the same thing; overloads are for genuinely different return types per argument.

Q17: The `this` parameter?
A17: A fake first parameter (`this: { name: string }`) that types `this` and is erased at compile time; prevents calling a method detached from its object.

Q18: Branded types?
A18: `number & { __brand: 'OrderId' }` makes `UserId` and `OrderId` incompatible although both are numbers. Create them only at the validation boundary (note 108).

Q19: `private` vs `#private`?
A19: `private` is erased: the field exists at runtime (`Object.keys(w)` shows `['paise']` in the output above). `#secret` is a real JS private field. Use `#` when secrecy matters.

Q20: `catch (err)` type?
A20: `unknown` under `strict` (`useUnknownInCatchVariables`, TS 4.4+). Narrow with `instanceof` before reading `.message`.

Q21: Index access and `noUncheckedIndexedAccess`?
A21: `prices['burger']` is typed `number` by default although it is `undefined` at runtime. Turning on `noUncheckedIndexedAccess` makes it `number | undefined`; recommended for senior code bases.

**C. Your stack (Q22-Q27, code: Express / React / Redux blocks)**

Q22: Why Zod with `z.infer`?
A22: Types vanish at runtime but `req.body` is untrusted. The schema validates at runtime and `z.infer` derives the TS type, so there is one source of truth.

Q23: How do you add `req.user` in Express?
A23: Declaration merging: `declare global { namespace Express { interface Request { user?: ... } } }` in a module file. Mark it optional because middleware may not have run.

Q24: Typed errors in Express?
A24: Subclass `Error` (`HttpError` with `status`), and in the 4-argument error middleware narrow `err: unknown` with `instanceof`. Never type `err` as `any`.

Q25: `RootState` and `AppDispatch` in RTK?
A25: Infer them: `ReturnType<typeof store.getState>` and `typeof store.dispatch`. Export typed hooks once (`useAppSelector`, `useAppDispatch`) and use only those.

Q26: Typing React props, children, events, state?
A26: `children?: ReactNode`; events `ChangeEvent<HTMLInputElement>`; `useState<string | null>(null)` when the initial value is narrower than the type; avoid `React.FC` unless you need it.

Q27: Most common compiler errors?
A27: `TS2322` (not assignable), `TS2345` (argument), `TS2339` (property missing / narrowing), `TS18047/18048` (possibly null/undefined), `TS18046` (unknown), `TS2353` (excess property), `TS7006` (implicit any). See Mistakes below.

**D. Config and tooling (Q28-Q30)**

Q28: What does `"strict": true` include?
A28: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables`, `alwaysStrict`. Not included but worth adding: `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`.

Q29: `import type`, `isolatedModules`, `moduleResolution`?
A29: `import type` is erased, so bundlers (Vite, esbuild) never see a runtime import. `isolatedModules` makes every file compilable alone (needed for esbuild/swc). `moduleResolution: "bundler"` (TS 5.0+) for Vite/webpack apps, `"nodenext"` for Node ESM.

Q30: Decorators: experimental vs standard?
A30: `experimentalDecorators` (legacy, used by NestJS/TypeORM with `emitDecoratorMetadata`) differs from the TC39 standard decorators supported since **TS 5.0**. They are not compatible: pick one per project. `using` / `await using` (TS 5.2) are resource-management keywords, not decorators.


---

## 🔷 When to Use + When Not to Use
✅ Use this note when:
- You have 1-2 days before a senior TypeScript/React/Node interview and need a high-yield pass.
- You want one-line answers plus the "why" and a compile-verified snippet.

❌ Do not rely on it alone when:
- You are learning a topic for the first time: read the dedicated note (numbers in brackets in this course) first.
- The role is library-author level: also practise notes 101-114 (type-level puzzles).

---

## 📊 Visual Diagram
```
30 CLASSICS MAP
  A. BASICS (Q1-10)     interface/type, any/unknown/never, enum, as const,
                        satisfies, unions, guards, structural, keyof, readonly
  B. ADVANCED (Q11-21)  constraints, mapped, conditional/infer, distribution,
                        template literal, overloads, this, brands, #private,
                        catch unknown, noUncheckedIndexedAccess
  C. YOUR STACK (22-27) Zod z.infer, Express merging, typed errors,
                        RTK RootState, React props/events, common errors
  D. TOOLING (28-30)    strict family, import type/isolatedModules/resolution,
                        decorators (experimental vs TS 5 standard)

  ANSWER FORMULA:  one line  ->  trade-off  ->  tiny code  ->  flag/version
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structural typing | Compatibility by shape | Shape से compatibility |
| Narrowing | Refining a type via checks | Checks से type छोटा करना |
| Covariance | Subtype allowed where supertype expected | Subtype को supertype की जगह मानना |
| Bivariance | Method params accepted both ways | Method params का दोनों तरफ मान्य होना |
| Declaration merging | Same-name declarations combine | Same नाम की declarations जुड़ जाना |
| Type erasure | Types vanish at runtime | Runtime पर types का गायब होना |

---

## ⚡ 3-Line Summary
English:
1. Answer each classic as: one line, the trade-off, a tiny example, the flag or TS version.
2. Most "gotchas" come from erasure (types vanish), structural typing, and unsound-by-design features (array covariance, bivariant methods).
3. Tie answers to your stack: Zod `z.infer`, Express merging, RTK `RootState`, React events.

Hindi:
1. हर classic का जवाब: एक लाइन, trade-off, छोटा example, flag या TS version।
2. ज़्यादातर gotchas erasure (types गायब), structural typing और जान-बूझकर unsound features (array covariance, bivariant methods) से आते हैं।
3. जवाब अपने stack से जोड़ो: Zod `z.infer`, Express merging, RTK `RootState`, React events।

---

## ➡️ Next Topic
**Quick Revision (`quick-revision/` folder)** — पूरे course की cheat-sheets, `tsconfig` templates और रोज़ की revision के लिए एक-पन्ने के नोट्स।
