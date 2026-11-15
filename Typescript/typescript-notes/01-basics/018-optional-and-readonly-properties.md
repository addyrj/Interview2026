# 18. Optional and readonly Properties
# हिंदी में: Optional (`?`) और `readonly` Properties

> TypeScript 5.x | `exactOptionalPropertyTypes` is NOT part of `strict`; enable it separately (TS 4.4+)

---

## 🔵 Simple Definition (English)
An **optional property** (`nickname?: string`) may be missing from the object; reading it gives `string | undefined`. A **`readonly` property** (`readonly id: number`) can be set when the object is created but cannot be reassigned afterwards. Both are **compile-time only** modifiers. `readonly` is also available for arrays (`readonly string[]` / `ReadonlyArray<string>`) and tuples, and the utility types `Partial<T>` (make all optional) and `Readonly<T>` (make all readonly) apply them in bulk.

## 🔵 सरल परिभाषा (Hindi)
**Optional property** (`nickname?: string`) object में हो भी सकती है और नहीं भी; इसे पढ़ने पर `string | undefined` मिलता है। **`readonly` property** (`readonly id: number`) object बनते समय set हो सकती है पर बाद में बदली नहीं जा सकती। दोनों **सिर्फ़ compile-time** modifiers हैं। `readonly` arrays (`readonly string[]` / `ReadonlyArray<string>`) और tuples के लिए भी है, और utility types `Partial<T>` (सब optional) और `Readonly<T>` (सब readonly) इन्हें एक साथ लगा देते हैं।

---

## 🔴 Problem it Solves
Real data is incomplete and some fields must never change. A user may not have a profile photo (optional); an order's `id`, `createdAt` and `paymentId` must not be overwritten by a bug somewhere in a reducer (readonly). Without these modifiers you either mark everything required (and invent fake values like `''`) or leave everything writable (and hope nobody mutates). Optional forces callers to handle absence; readonly turns accidental mutation into a compile error, which is especially valuable in Redux where state must be updated immutably.

## 🔴 यह क्यों बना? (Hindi)
असली data अधूरा होता है और कुछ fields कभी बदलनी नहीं चाहिए। किसी user की profile photo नहीं भी हो सकती (optional); order का `id`, `createdAt` और `paymentId` किसी reducer के bug से overwrite नहीं होना चाहिए (readonly)। इन modifiers के बिना या तो सब कुछ required कर देते हैं (और `''` जैसी नकली values बनाते हैं) या सब writable छोड़कर उम्मीद करते हैं कि कोई mutate नहीं करेगा। Optional callers को absence handle करने पर मजबूर करता है; readonly गलती से mutation को compile error बना देता है, जो Redux में खास तौर पर काम का है जहाँ state immutably update होनी चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → `name?: string` means the key may be absent. The type of `obj.name` becomes `string | undefined` (under `strictNullChecks`).
Step 2 → Optional is NOT the same as `name: string | undefined`. With the optional form you may omit the key; with the union form the key is required (but may hold `undefined`).
Step 3 → By default `{ name: undefined }` is accepted for `name?: string`. With `exactOptionalPropertyTypes` (TS 4.4+) it is rejected (TS2375): "missing" and "present but undefined" become different things, matching JSON and `Object.keys` behaviour.
Step 4 → `readonly id: number` blocks assignment `obj.id = 2` (TS2540). It does NOT block mutation of things inside: `readonly tags: string[]` still allows `obj.tags.push('x')`, because `readonly` is shallow.
Step 5 → `readonly string[]` blocks `push`, `pop` and index assignment. A mutable array is assignable to `readonly string[]`, but not the other way (TS4104).
Step 6 → `readonly` does not affect assignability between object types: `{ readonly id: number }` is assignable to `{ id: number }`. That is a known soundness gap.
Step 7 → `Partial<T>`, `Required<T>` and `Readonly<T>` add or remove `?` and `readonly` for all keys; `-?` and `-readonly` in mapped types remove them.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `name?: string` का मतलब key गायब हो सकती है। `obj.name` का type `string | undefined` बनता है (`strictNullChecks` में)।
Step 2 → Optional और `name: string | undefined` एक जैसे नहीं हैं। Optional में key छोड़ सकते हो; union वाले रूप में key required है (पर उसकी value `undefined` हो सकती है)।
Step 3 → Default में `name?: string` के लिए `{ name: undefined }` accept होता है। `exactOptionalPropertyTypes` (TS 4.4+) में यह reject होता है (TS2375): "गायब" और "मौजूद पर undefined" अलग चीज़ें बन जाती हैं, जो JSON और `Object.keys` के व्यवहार से मेल खाता है।
Step 4 → `readonly id: number` असाइनमेंट `obj.id = 2` रोकता है (TS2540)। यह अंदर की चीज़ों का mutation **नहीं** रोकता: `readonly tags: string[]` पर भी `obj.tags.push('x')` चलता है, क्योंकि `readonly` shallow है।
Step 5 → `readonly string[]` `push`, `pop` और index assignment रोकता है। Mutable array को `readonly string[]` में दे सकते हैं, उल्टा नहीं (TS4104)।
Step 6 → `readonly` object types के बीच assignability नहीं बदलता: `{ readonly id: number }` को `{ id: number }` में assign कर सकते हैं। यह ज्ञात soundness gap है।
Step 7 → `Partial<T>`, `Required<T>` और `Readonly<T>` सारी keys पर `?` और `readonly` जोड़ते या हटाते हैं; mapped types में `-?` और `-readonly` इन्हें हटाते हैं।

---

## 🟡 Real World Example
**Swiggy's address form** has required `line1` and `pincode`, an optional `landmark` and `instructions` (not every address has one), and a `readonly addressId` assigned by SQL Server on insert that must never be edited in the UI. A "PATCH /address/:id" endpoint accepts `Partial<Address>` (only changed fields), while the Redux state stores `Readonly<Address>[]` so that reducers cannot mutate objects by mistake. Optional handles "may be missing", readonly handles "must not change".

## 🟡 Real Example Hindi mein
**Swiggy के address form** में `line1` और `pincode` required हैं, `landmark` और `instructions` optional हैं (हर address में नहीं होते), और `readonly addressId` SQL Server insert पर देता है जो UI में कभी edit नहीं होनी चाहिए। "PATCH /address/:id" endpoint `Partial<Address>` लेता है (सिर्फ़ बदली fields), और Redux state `Readonly<Address>[]` रखती है ताकि reducers गलती से objects mutate न कर सकें। Optional "गायब हो सकता है" संभालता है, readonly "बदलना नहीं चाहिए" संभालता है।

---

## 💻 Code Example — Basic

```typescript
// optional-readonly-basic.ts  (TypeScript 5.x, strict)

interface Address {
  readonly addressId: number;   // set once (e.g. by SQL Server IDENTITY), never edited
  line1: string;                // required
  pincode: string;              // required
  landmark?: string;            // optional: string | undefined
  instructions?: string;        // optional
}

const home: Address = { addressId: 1, line1: '12 MG Road', pincode: '560001' }; // optionals omitted

// Reading an optional: TypeScript forces you to handle undefined
function describe(a: Address): string {
  // a.landmark.toUpperCase() would be an error: possibly undefined
  const landmark = a.landmark ?? 'no landmark';       // default when missing
  return `${a.line1} (${landmark})`;
}

home.line1 = '99 Brigade Road';                       // ok: not readonly
// home.addressId = 2;                                // error TS2540 (see Common Mistakes)

// readonly arrays: can read and iterate but not mutate
const pincodes: readonly string[] = ['560001', '110001'];
const lengths = pincodes.map((p) => p.length);        // non-mutating methods are fine
// pincodes.push('400001');                           // error TS2339

// Optional parameter-like property in an options bag
interface Options { retries?: number; timeoutMs?: number }
function call(opts: Options = {}): number {
  return (opts.retries ?? 3) * (opts.timeoutMs ?? 1000); // defaults for missing keys
}

console.log(describe(home));
console.log(lengths, call(), call({ retries: 1 }));
```

Run with `npx tsx optional-readonly-basic.ts`. Real output:
```
99 Brigade Road (no landmark)
[ 6, 6 ] 3000 1000
```

## 💻 Code Example — Advanced

```typescript
// optional-readonly-advanced.ts  (TypeScript 5.x)

interface Order {
  readonly id: number;
  readonly createdAt: Date;
  status: 'placed' | 'delivered';
  note?: string;
}

// 1. Partial: PATCH payload where every key is optional
type OrderPatch = Partial<Omit<Order, 'id' | 'createdAt'>>; // can't patch readonly columns

function applyPatch(order: Order, patch: OrderPatch): Order {
  return { ...order, ...patch };                       // new object: immutable update
}

// 2. Readonly<T> is SHALLOW
interface Cart { readonly items: string[] }
const cart: Cart = { items: ['paneer'] };
cart.items.push('naan');                               // allowed: only the property is readonly

// 3. A deep readonly helper (recursive mapped type)
type DeepReadonly<T> = T extends (infer U)[]
  ? ReadonlyArray<DeepReadonly<U>>
  : T extends object
    ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
    : T;
type FrozenCart = DeepReadonly<{ items: string[]; meta: { coupon?: string } }>;
const frozen: FrozenCart = { items: ['a'], meta: {} };
// frozen.items.push('b');       // would be an error now
// frozen.meta.coupon = 'X';     // would be an error now

// 4. Removing modifiers with mapped type modifiers: -readonly and -?
type Mutable<T> = { -readonly [K in keyof T]: T[K] };
type Complete<T> = { [K in keyof T]-?: T[K] };
type EditableOrder = Mutable<Order>;                   // id and createdAt writable
type FullOrder = Complete<Order>;                      // note is now required

const draft: EditableOrder = { id: 1, createdAt: new Date(0), status: 'placed' };
draft.id = 2;                                          // allowed on the Mutable copy
const full: FullOrder = { id: 1, createdAt: new Date(0), status: 'placed', note: 'less spicy' };

// 5. readonly does NOT affect assignability (known gap)
const ro: { readonly n: number } = { n: 1 };
const rw: { n: number } = ro;                          // compiles!
rw.n = 99;                                             // mutates the same object
console.log(ro.n);

const placed: Order = { id: 7, createdAt: new Date(0), status: 'placed' };
console.log(applyPatch(placed, { status: 'delivered', note: 'ok' }).status);
console.log(cart.items.length, frozen.items[0], draft.id, full.note);
```

Run with `npx tsx optional-readonly-advanced.ts`. Real output:
```
99
delivered
2 a 2 less spicy
```

---

## 🟠 Node/Express + React Integration

```tsx
// models.ts
export interface Profile {
  readonly id: number;              // primary key from SQL Server
  name: string;
  avatarUrl?: string;               // optional column (NULL in DB)
}

// server.ts  (Express): PATCH accepts Partial, id comes from the URL not the body
import express from 'express';
const app = express();
app.use(express.json());

type ProfilePatch = Partial<Omit<Profile, 'id'>>;      // client cannot send id

app.patch('/profiles/:id', (req, res) => {
  const patch: ProfilePatch = req.body;                 // body is any; annotate and validate (Zod later)
  const id = Number(req.params.id);
  // UPDATE Profiles SET Name = COALESCE(@name, Name) WHERE Id = @id   (SQL Server)
  res.json({ id, ...patch });
});

// profileSlice.ts  (Redux Toolkit): Immer lets you "mutate" drafts; readonly protects non-draft code
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
interface ProfileState { readonly list: readonly Profile[] }
const initialState: ProfileState = { list: [] };
const slice = createSlice({
  name: 'profiles',
  initialState,
  reducers: {
    renamed(state, action: PayloadAction<{ id: number; name: string }>) {
      const p = state.list.find((x) => x.id === action.payload.id);
      if (p) p.name = action.payload.name;              // name is not readonly; id would be an error
    },
  },
});
export const { renamed } = slice.actions;

// ProfileCard.tsx  (React): optional props with defaults
interface CardProps { profile: Profile; compact?: boolean }
export function ProfileCard({ profile, compact = false }: CardProps) {
  return (
    <div>
      {profile.avatarUrl && <img src={profile.avatarUrl} alt="" />}
      <b>{profile.name}</b>{compact ? null : <span> #{profile.id}</span>}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assigning to a readonly property
```typescript
interface U2 { readonly id: number; nick?: string }
const u: U2 = { id: 1 };
// ❌ Wrong: id is readonly
u.id = 2;
// error TS2540: Cannot assign to 'id' because it is a read-only property.
```
```typescript
interface U2 { readonly id: number; nick?: string }
const u: U2 = { id: 1 };
// ✅ Right: create a new object instead of mutating
const u2: U2 = { ...u, id: 2 };
```

❌ Mistake 2: Using an optional property as if it were always present
```typescript
interface U2 { readonly id: number; nick?: string }
const u: U2 = { id: 1 };
// ❌ Wrong: nick may be undefined
const n: string = u.nick;
// error TS2322: Type 'string | undefined' is not assignable to type 'string'.
//   Type 'undefined' is not assignable to type 'string'.
```
✅ Correct: `const n: string = u.nick ?? 'guest'`.

❌ Mistake 3: Mutating a readonly array, or passing it where a mutable one is required
```typescript
const ro: readonly number[] = [1];
// ❌ Wrong:
ro.push(2);
// error TS2339: Property 'push' does not exist on type 'readonly number[]'.
ro[0] = 3;
// error TS2542: Index signature in type 'readonly number[]' only permits reading.
const r: readonly string[] = ['a'];
const mm: string[] = r;
// error TS4104: The type 'readonly string[]' is 'readonly' and cannot be assigned to the mutable type 'string[]'.
```
✅ Correct: use `ro.concat(2)` / `[...ro, 2]` for a new array, and make function parameters `readonly T[]` so both kinds are accepted.

❌ Mistake 4: `exactOptionalPropertyTypes` surprise (flag must be turned on in tsconfig)
```typescript
interface P { nick?: string }
// ❌ Wrong with "exactOptionalPropertyTypes": true: explicit undefined is not the same as missing
const a: P = { nick: undefined };
// error TS2375: Type '{ nick: undefined; }' is not assignable to type 'P' with 'exactOptionalPropertyTypes: true'. Consider adding 'undefined' to the types of the target's properties.
```
✅ Correct: declare `nick?: string | undefined` if you really send `undefined`, or omit the key.

---

## 🧠 Tricky Interview Question

```typescript
interface Cart { readonly items: string[] }
const c: Cart = { items: [] };
c.items.push('x');   // (1)
c.items = ['y'];     // (2) ❌ TS2540
const m: { items: string[] } = c;  // (3)
m.items = ['z'];     // (4)
```
Answer: (1) is allowed because `readonly` is shallow: it protects the property binding, not the array's contents. (2) is an error: `TS2540: Cannot assign to 'items' because it is a read-only property.` (3) is allowed: readonly does not take part in assignability, so `Cart` is assignable to the mutable type. (4) is then allowed, and it also changes `c.items` at runtime since both point to the same object. To really protect it, declare `readonly items: readonly string[]`, and remember all of this vanishes at runtime.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `x?: string` and `x: string | undefined`?
A1: With `x?: string` the key may be omitted entirely. With `x: string | undefined` the key is required and you must write `x: undefined` explicitly. Reading both gives `string | undefined`. With `exactOptionalPropertyTypes`, the optional form additionally forbids assigning an explicit `undefined`.

Q2: Is `readonly` deep? How do you make it deep?
A2: No, it is shallow and compile-time only. For nested protection use `readonly T[]` arrays, a recursive `DeepReadonly<T>` mapped type, `as const` for literals, and `Object.freeze` for runtime. Libraries like Immer give immutability by producing new objects.

Q3: What do `Partial`, `Required` and `Readonly` do?
A3: They are mapped types: `Partial<T>` = `{ [K in keyof T]?: T[K] }`, `Required<T>` = `{ [K in keyof T]-?: T[K] }`, `Readonly<T>` = `{ readonly [K in keyof T]: T[K] }`. `-?` and `-readonly` remove the modifiers. `Partial` is the usual type for PATCH payloads and `useState` update objects.

Q4: Why is `readonly` useful in Redux if Immer already handles immutability?
A4: Immer makes updates safe inside reducers, but selectors, components and middleware receive state that must not be mutated. Typing state as `readonly` (or using `Readonly<T>`) catches accidental `state.list.push()` outside reducers at compile time. Inside `createSlice` the draft is typed as writable (`WritableDraft`) so reducers still compile.

Q5: Can you assign an object with a `readonly` property to a type where it is mutable?
A5: Yes. Property-level `readonly` is ignored by assignability (a long-standing unsoundness). Arrays differ: `readonly T[]` is NOT assignable to `T[]` (TS4104). Do not rely on `readonly` as a security boundary.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `?` for genuinely absent data: nullable DB columns, optional config, optional props
- `readonly` for IDs, timestamps, config, Redux state and parameters you do not intend to modify
- `Partial<T>` for PATCH/update payloads and form drafts

❌ Avoid when:
- Everything is optional "just in case": callers then handle `undefined` everywhere. Model separate types (`NewOrder` vs `Order`)
- You expect runtime protection from `readonly`; use `Object.freeze` or Immer
- A field is "optional" only during construction: use a builder or two types instead

---

## 📊 Visual Diagram
```
 interface Order { readonly id: number; note?: string }

 order.id = 5       ──► TS2540  (readonly)
 order.note         ──► string | undefined   (optional)
 { id: 1 }          ──► valid, note omitted
 { id: 1, note: undefined } ──► valid, unless exactOptionalPropertyTypes

 Partial<T>  : every key gets ?        Required<T> : every key loses ?
 Readonly<T> : every key gets readonly Mutable<T>  : { -readonly [K in keyof T]: T[K] }

 readonly is SHALLOW:   items: string[]  (property locked, array contents NOT locked)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Optional property | `?`, may be missing | `?`, गायब हो सकती है |
| readonly | Cannot be reassigned after init | बाद में reassign नहीं हो सकती |
| Shallow | Applies to the first level only | सिर्फ़ पहले level पर लागू |
| Partial / Required / Readonly | Bulk modifier utility types | एक साथ modifiers लगाने वाले utilities |
| `-?` / `-readonly` | Remove a modifier in a mapped type | Mapped type में modifier हटाना |
| exactOptionalPropertyTypes | Missing is not the same as `undefined` | "गायब" और `undefined` अलग |
| ReadonlyArray | Array without mutating methods | Mutating methods के बिना array |

---

## ⚡ 3-Line Summary
English:
1. `?` makes a key omittable (reads as `T | undefined`); `readonly` blocks reassignment; both are compile-time only.
2. `readonly` is shallow and ignored by assignability; use `readonly T[]`, `DeepReadonly`, `as const` or `Object.freeze` for more.
3. Use `Partial<T>` for patches, `Readonly<T>` for state, and turn on `exactOptionalPropertyTypes` if you need missing and `undefined` to differ.

Hindi:
1. `?` key को छोड़ने लायक बनाता है (पढ़ने पर `T | undefined`); `readonly` reassignment रोकता है; दोनों सिर्फ़ compile-time हैं।
2. `readonly` shallow है और assignability में ignore होता है; ज़्यादा सुरक्षा के लिए `readonly T[]`, `DeepReadonly`, `as const` या `Object.freeze` इस्तेमाल करो।
3. Patches के लिए `Partial<T>`, state के लिए `Readonly<T>`, और "गायब" व `undefined` को अलग रखना हो तो `exactOptionalPropertyTypes` चालू करो।

---

## ➡️ Next Topic
**19. null and undefined + strictNullChecks** — the "billion dollar mistake", how strict mode models absence, and the operators `?.`, `??`, `!`.
