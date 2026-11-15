# 17. const Assertions (as const)
# हिंदी में: const Assertions (`as const` से values को freeze करना)

> TypeScript 5.x | `as const` since TS 3.4 | `const` type parameters (`<const T>`) since TS 5.0 | `satisfies` since TS 4.9

---

## 🔵 Simple Definition (English)
A **const assertion** is the expression `value as const`. It tells the compiler: "infer the narrowest possible type for this value". Effects: string/number/boolean literals keep their exact literal type (no widening), object properties become `readonly`, and array literals become `readonly` tuples with known length and positions. It is a **compile-time only** hint (it does not freeze the object at runtime; use `Object.freeze` for that) and it can only be applied to literals, not to variables or function calls.

## 🔵 सरल परिभाषा (Hindi)
**Const assertion** यानी `value as const`। यह compiler से कहता है: "इस value का सबसे narrow type infer करो"। असर: string/number/boolean literals अपना exact literal type रखते हैं (widening नहीं), object properties `readonly` बन जाती हैं, और array literals ज्ञात length और positions वाले `readonly` tuples बन जाते हैं। यह **सिर्फ़ compile-time** hint है (runtime पर object freeze नहीं होता; उसके लिए `Object.freeze`) और सिर्फ़ literals पर लगता है, variables या function calls पर नहीं।

---

## 🔴 Problem it Solves
TypeScript widens by default: `const cfg = { method: 'GET', retries: 3 }` is inferred as `{ method: string; retries: number }` because properties are mutable. That loses information: you cannot pass `cfg.method` to a function that wants `'GET' | 'POST'`, you cannot derive a union type from a list of roles, and a tuple like `[lat, lng]` becomes `number[]`. Before `as const` you wrote the type twice (a runtime array and a duplicate union). `as const` keeps one source of truth: the value itself, and you derive the types from it.

## 🔴 यह क्यों बना? (Hindi)
TypeScript default में widen करता है: `const cfg = { method: 'GET', retries: 3 }` का type `{ method: string; retries: number }` बनता है क्योंकि properties mutable हैं। इससे जानकारी खो जाती है: आप `cfg.method` को ऐसे function में नहीं दे सकते जो `'GET' | 'POST'` माँगता है, roles की list से union type derive नहीं कर सकते, और `[lat, lng]` जैसा tuple `number[]` बन जाता है। `as const` से पहले आप type दो बार लिखते थे (runtime array और duplicate union)। `as const` एक ही source of truth रखता है: value खुद, और types उसी से derive होते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Without it: `const a = ['x', 'y']` has type `string[]` (widened, mutable).
Step 2 → With it: `const a = ['x', 'y'] as const` has type `readonly ['x', 'y']` (exact positions and literals).
Step 3 → For objects every property becomes `readonly` AND keeps its literal type: `{ readonly method: 'GET'; readonly retries: 3 }`. This applies recursively to nested objects and arrays.
Step 4 → Writes are blocked at compile time: `cfg.retries = 4` gives TS2540, `a.push('z')` gives TS2339 (no `push` on a readonly tuple).
Step 5 → Derive types with `typeof`: `type Role = (typeof ROLES)[number]` turns the array into a union of its elements.
Step 6 → Restrictions: `as const` works only on literal expressions (strings, numbers, booleans, bigint, enum members, array and object literals, template literals). `let x = y as const` is an error.
Step 7 → The `readonly` is not emitted: at runtime the object is still mutable. Combine with `Object.freeze` when you need runtime immutability.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → इसके बिना: `const a = ['x', 'y']` का type `string[]` (widened, mutable)।
Step 2 → इसके साथ: `const a = ['x', 'y'] as const` का type `readonly ['x', 'y']` (exact positions और literals)।
Step 3 → Objects में हर property `readonly` बनती है और अपना literal type रखती है: `{ readonly method: 'GET'; readonly retries: 3 }`। यह nested objects और arrays पर recursively लागू होता है।
Step 4 → Writes compile time पर रुकते हैं: `cfg.retries = 4` पर TS2540, `a.push('z')` पर TS2339 (readonly tuple पर `push` नहीं)।
Step 5 → `typeof` से types derive करो: `type Role = (typeof ROLES)[number]` array को उसके elements के union में बदल देता है।
Step 6 → पाबंदियाँ: `as const` सिर्फ़ literal expressions (strings, numbers, booleans, bigint, enum members, array और object literals, template literals) पर चलता है। `let x = y as const` error है।
Step 7 → `readonly` emit नहीं होता: runtime पर object अब भी mutable है। Runtime immutability चाहिए तो `Object.freeze` साथ लगाओ।

---

## 🟡 Real World Example
**Zomato's filter bar** has a fixed list of cuisines and sort options: `['north-indian', 'chinese', 'pizza']` and `['rating', 'delivery_time', 'cost']`. The same list is needed in three places: the React dropdown (runtime), the Express query validation (runtime) and the function signature `sortBy(key: SortKey)` (compile time). With `as const` the array is written once; the union type is derived. Add `'offers'` to the array and the dropdown, validation and type all update together. Route tables and Redux action-type maps use the same trick.

## 🟡 Real Example Hindi mein
**Zomato के filter bar** में cuisines और sort options की fixed list है: `['north-indian', 'chinese', 'pizza']` और `['rating', 'delivery_time', 'cost']`। यही list तीन जगह चाहिए: React dropdown (runtime), Express query validation (runtime) और function signature `sortBy(key: SortKey)` (compile time)। `as const` से array एक बार लिखी जाती है और union type उसी से derive होता है। Array में `'offers'` जोड़ो तो dropdown, validation और type तीनों साथ बदल जाते हैं। Route tables और Redux action-type maps भी यही trick इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic

```typescript
// const-basic.ts  (TypeScript 5.x, strict)

// 1. Without as const: widened types
const widened = { method: 'GET', retries: 3 };        // { method: string; retries: number }
const arr1 = ['upi', 'card'];                         // string[]
const pair1 = [19.07, 72.87];                         // number[]  (lost: it is exactly 2 numbers)

// 2. With as const: narrow + readonly
const cfg = { method: 'GET', retries: 3 } as const;   // { readonly method: 'GET'; readonly retries: 3 }
const METHODS = ['upi', 'card', 'wallet'] as const;   // readonly ['upi', 'card', 'wallet']
const coords = [19.07, 72.87] as const;               // readonly [19.07, 72.87]

// 3. Derive types from the values
type PayMethod = (typeof METHODS)[number];            // 'upi' | 'card' | 'wallet'
type Method = (typeof cfg)['method'];                 // 'GET'

// 4. The literal can be passed to a function wanting a union
function request(method: 'GET' | 'POST', retries: number): string {
  return `${method} x${retries}`;                     // just formats a string
}
console.log(request(cfg.method, cfg.retries));        // ok: 'GET' is a literal, not string

// request(widened.method, 1) would FAIL: widened.method is string

// 5. Tuple positions are known
const [lat, lng] = coords;                            // lat: 19.07, lng: 72.87
const first: PayMethod = METHODS[0];                  // 'upi'

// 6. Runtime use stays normal: it is a plain JS array/object
console.log(METHODS.includes('card'), lat, lng, first);
console.log(widened.method, arr1.length, pair1.length);
```

Run with `npx tsx const-basic.ts`. Real output:
```
GET x3
true 19.07 72.87 upi
GET 2 2
```

## 💻 Code Example — Advanced

```typescript
// const-advanced.ts  (TypeScript 5.x)

// 1. Lookup table: one object drives types AND runtime
const ROUTES = {
  orderList: '/orders',
  orderDetail: '/orders/:id',
  payment: '/payments/:id/capture',
} as const;

type RouteName = keyof typeof ROUTES;                 // 'orderList' | 'orderDetail' | 'payment'
type RoutePath = (typeof ROUTES)[RouteName];          // '/orders' | '/orders/:id' | '/payments/:id/capture'

// 2. Union of object shapes from a readonly array of objects
const PLANS = [
  { id: 'free', priceRs: 0 },
  { id: 'pro', priceRs: 499 },
] as const;

type Plan = (typeof PLANS)[number];                   // the union of both object types
type PlanId = Plan['id'];                             // 'free' | 'pro'

function priceOf(id: PlanId): number {
  const found = PLANS.find((p) => p.id === id);       // p is the union element
  return found ? found.priceRs : 0;                   // found.priceRs is 0 | 499
}

// 3. const type parameter (TS 5.0+): the function infers literals without the caller writing as const
function defineRoutes<const T extends readonly string[]>(names: T): T {
  return names;                                        // T is inferred as a readonly tuple of literals
}
const names = defineRoutes(['home', 'cart']);         // readonly ['home', 'cart'], not string[]
type Name = (typeof names)[number];                   // 'home' | 'cart'

// 4. satisfies + as const together: validated AND narrow
type Endpoint = { method: 'GET' | 'POST'; path: string };
const API = {
  list: { method: 'GET', path: '/orders' },
  create: { method: 'POST', path: '/orders' },
} as const satisfies Record<string, Endpoint>;        // satisfies after as const (TS 5.0+ pattern)

// 5. Making a readonly array mutable again needs a copy, not an assertion
const copy: string[] = [...PLANS.map((p) => p.id)];  // a new mutable array

// 6. Runtime freeze: as const does NOT freeze at runtime
const live = { retries: 3 } as const;
(live as { retries: number }).retries = 5;            // type hack: JS allows it
const frozen = Object.freeze({ retries: 3 });         // runtime + readonly type
console.log(live.retries, Object.isFrozen(frozen));

const n: Name = 'cart';
const p: RoutePath = ROUTES.orderDetail;
console.log(priceOf('pro'), API.create.method, copy, n, p);
```

Run with `npx tsx const-advanced.ts`. Real output:
```
5 true
499 POST [ 'free', 'pro' ] cart /orders/:id
```

---

## 🟠 Node/Express + React Integration

```tsx
// shared/constants.ts: one list used by server validation, React UI and types
export const SORT_KEYS = ['rating', 'delivery_time', 'cost'] as const;
export type SortKey = (typeof SORT_KEYS)[number];

export function isSortKey(v: unknown): v is SortKey {
  return typeof v === 'string' && (SORT_KEYS as readonly string[]).includes(v);
}

// server.ts  (Express): validate query param at runtime using the SAME list
import express from 'express';
const app = express();
app.get('/restaurants', (req, res) => {
  const sort = req.query.sort;                      // string | ParsedQs | string[] | undefined
  if (!isSortKey(sort)) {                           // narrows to SortKey below
    res.status(400).json({ error: `sort must be one of ${SORT_KEYS.join(', ')}` });
    return;
  }
  res.json({ sortedBy: sort });                     // sort: SortKey
});

// SortSelect.tsx  (React): render options from the SAME constant
export function SortSelect({ value, onChange }: { value: SortKey; onChange: (k: SortKey) => void }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value as SortKey)}>
      {SORT_KEYS.map((k) => <option key={k} value={k}>{k}</option>)}
    </select>
  );
}

// store.ts  (Redux Toolkit): action type constants with as const
export const ACTIONS = { sortChanged: 'filters/sortChanged' } as const;
type SortAction = { type: typeof ACTIONS.sortChanged; payload: SortKey };
export function filtersReducer(state: SortKey = 'rating', action: SortAction): SortKey {
  return action.type === ACTIONS.sortChanged ? action.payload : state;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `as const` to be mutable
```typescript
const cfg = { method: 'GET', retries: 3 } as const;
// ❌ Wrong: every property is readonly
cfg.retries = 4;
// error TS2540: Cannot assign to 'retries' because it is a read-only property.
const arr = ['a', 'b'] as const;
// ❌ Wrong: a readonly tuple has no push
arr.push('c');
// error TS2339: Property 'push' does not exist on type 'readonly ["a", "b"]'.
```
✅ Correct: keep a separate mutable copy (`const list = [...arr]`) or do not use `as const` for data that must change.

❌ Mistake 2: Passing a readonly tuple to a function that takes a mutable array
```typescript
const ROLES = ['admin', 'user'] as const;
function printAll(items: string[]): void { console.log(items); }
// ❌ Wrong: readonly ["admin", "user"] is not assignable to string[]
printAll(ROLES);
```
Real compiler message: `error TS2345: Argument of type 'readonly ["admin", "user"]' is not assignable to parameter of type 'string[]'.` followed by `The type 'readonly ["admin", "user"]' is 'readonly' and cannot be assigned to the mutable type 'string[]'.`
✅ Correct: declare the parameter as `readonly string[]`. Accepting `readonly` arrays is good API design anyway.

❌ Mistake 3: Applying `as const` to a variable. `const v = someVar as const` is an error (TS1355: "A 'const' assertions can only be applied to references to enum members, or string, number, boolean, array, or object literals."). Apply it where the literal is written.

---

## 🧠 Tricky Interview Question

```typescript
const user = { name: 'Asha', tags: ['vip'] } as const;
user.tags[0] = 'x';          // (a) ❌
user.tags.push('y');         // (b) ❌
const copy = Object.assign({}, user);
copy.name = 'Ravi';          // (c) ❌
```
Answer: all three lines fail. (a) `error TS2540: Cannot assign to '0' because it is a read-only property.` (b) `error TS2339: Property 'push' does not exist on type 'readonly ["vip"]'.` (c) `error TS2540: Cannot assign to 'name' because it is a read-only property.` Many people expect (c) to work because `Object.assign` makes a fresh object, but its return type is the intersection of the source types, so the `readonly` modifiers are carried over. The deeper point: `as const` is deep but **type-level only**, erased at runtime, and does not stop a mutation made through an alias typed as non-readonly. For runtime protection use `Object.freeze` (shallow) or a deep-freeze helper.

---

## ⚫ Interview Questions + Answers

Q1: What does `as const` do?
A1: It makes the compiler infer the most specific type: literals are not widened, object properties become `readonly`, and arrays become `readonly` tuples. It only affects types. At runtime nothing changes and the object is still mutable.

Q2: How do you build a union type from an array of strings without writing the values twice?
A2: Declare the array with `as const` and index it with `number`: `const ROLES = ['admin','user'] as const; type Role = (typeof ROLES)[number];`. For an object use `(typeof OBJ)[keyof typeof OBJ]` for values or `keyof typeof OBJ` for keys.

Q3: What is the difference between `as const`, `readonly` annotation and `Object.freeze`?
A3: `as const` narrows the inferred type and adds `readonly` deeply (types only). A `readonly` annotation or `Readonly<T>` only makes top-level properties read-only (types only). `Object.freeze` freezes the object at runtime (shallow) and its return type is `Readonly<T>`. Use `as const` plus `Object.freeze` for both compile-time and runtime guarantees.

Q4: What is a `const` type parameter (TS 5.0)?
A4: `function f<const T>(x: T)` makes the inference of `T` behave as if the argument had `as const`. So `f({ a: [1, 2] })` infers `{ readonly a: readonly [1, 2] }` and the caller does not have to remember to write `as const`. It only affects inference for literals written at the call site.

Q5: Where does `as const satisfies X` help?
A5: `satisfies` checks that the value conforms to a type (catching typos and missing keys) while `as const` keeps the narrow literal types. Together you get validation plus precise, readonly inference, ideal for route tables, feature flags and config objects (TS 5.0+ for combining the two in one expression).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Config objects, route tables, action-type maps, feature flags and lists of allowed values
- You want a union type derived from a runtime array/object (one source of truth)
- Returning tuples from helper functions (`return [a, b] as const`) so callers get positional types

❌ Avoid when:
- The data is built dynamically or must be mutated later; the `readonly` types will fight you
- You need to pass it to APIs that take mutable arrays and cannot change them (copy first)
- You expect runtime immutability; `as const` does not provide it

---

## 📊 Visual Diagram
```
 const x = ['a','b']             ──►  string[]                (widened, mutable)
 const x = ['a','b'] as const    ──►  readonly ['a','b']      (exact, readonly)

 { method:'GET', n:3 }           ──►  { method: string;        n: number }
 { method:'GET', n:3 } as const  ──►  { readonly method:'GET'; readonly n:3 }

 one value ──as const──► typeof VALUE ──[number]/[keyof]──► union type
 (runtime)               (compile time)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| const assertion | `as const`, infer narrowest type | सबसे narrow type infer कराना |
| Widening | Literal turning into its base type | Literal का base type बनना |
| Readonly tuple | Fixed-length, read-only array type | Fixed-length read-only array |
| `typeof` (type position) | Gets the type of a value | Value का type लेना |
| `const` type parameter | `<const T>` literal inference (TS 5.0) | Literal inference वाला type parameter |
| Single source of truth | One definition drives everything | एक ही definition से सब कुछ |

---

## ⚡ 3-Line Summary
English:
1. `as const` keeps literals narrow, makes properties `readonly` and arrays `readonly` tuples, at compile time only.
2. Derive unions with `(typeof X)[number]` or `(typeof X)[keyof typeof X]` so runtime lists and types share one definition.
3. It does not freeze at runtime; accept `readonly` arrays in function parameters, and use `<const T>` or `satisfies` (TS 5.x) for generics and validation.

Hindi:
1. `as const` literals को narrow रखता है, properties को `readonly` और arrays को `readonly` tuples बनाता है, सिर्फ़ compile time पर।
2. `(typeof X)[number]` या `(typeof X)[keyof typeof X]` से unions derive करो ताकि runtime list और types की एक ही definition रहे।
3. यह runtime पर freeze नहीं करता; function parameters में `readonly` arrays लो, और generics व validation के लिए `<const T>` या `satisfies` (TS 5.x) इस्तेमाल करो।

---

## ➡️ Next Topic
**18. Optional and readonly Properties** — `?`, `readonly`, `Partial`/`Readonly` and what `exactOptionalPropertyTypes` changes.
