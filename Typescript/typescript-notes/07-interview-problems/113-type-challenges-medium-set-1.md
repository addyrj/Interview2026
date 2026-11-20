# 113. Type-challenges: Medium Set 1
# हिंदी में: Type-challenges: Medium Set 1 (type-level पहेलियाँ)

> TypeScript 5.x | हर block `tsc --strict` (TS 5.9) से verify हुआ। `as` clause in mapped types = **TS 4.1+**; variadic tuples (`[...infer Rest, unknown]`) = **TS 4.0+**। Challenges का असली source: github.com/type-challenges/type-challenges।

---

## 🔵 Simple Definition (English)
**Type challenges** are small puzzles where you re-implement TypeScript's built-in type helpers (or invent new ones) using only the type system: `infer`, conditional types, mapped types, template literals and recursion. Each puzzle comes with **compile-time tests** (`Expect<Equal<A, B>>`), so "passing" means the file compiles. Set 1 covers the most asked "medium" ones: `ReturnType`, `Omit`, `TupleToUnion`, `Last`/`Pop`, `LookUp`, `Trim`, `Replace`, `AppendArgument`, `Readonly2`, `Awaited`.

## 🔵 सरल परिभाषा (Hindi)
**Type challenges** छोटी पहेलियाँ हैं जिनमें आप TypeScript के built-in type helpers (या नए) सिर्फ type system से दोबारा बनाते हैं: `infer`, conditional types, mapped types, template literals और recursion। हर पहेली के साथ **compile-time tests** (`Expect<Equal<A, B>>`) होते हैं, यानी file compile हो गई तो आप pass। Set 1 में सबसे ज़्यादा पूछे जाने वाले "medium" सवाल हैं: `ReturnType`, `Omit`, `TupleToUnion`, `Last`/`Pop`, `LookUp`, `Trim`, `Replace`, `AppendArgument`, `Readonly2`, `Awaited`।

---

## 🔴 Problem it Solves
Senior interviews ask "implement `Omit` / `ReturnType` yourself" to check that you *understand* the utility types you use daily, not just call them. These puzzles train the five core moves: (1) `infer` to capture, (2) conditional types to branch, (3) mapped types with `as` to filter keys, (4) recursion for strings/tuples, (5) distributive behaviour on unions. In real code the same moves power typed Redux action lookups, Express handler wrappers and API-client generics.

## 🔴 यह क्यों बना? (Hindi)
Senior interviews में पूछा जाता है "`Omit` / `ReturnType` खुद implement करो", ताकि पता चले कि आप रोज़ इस्तेमाल होने वाले utility types को *समझते* हैं, सिर्फ call नहीं करते। ये पहेलियाँ पाँच बुनियादी चालें सिखाती हैं: (1) `infer` से पकड़ना, (2) conditional types से branch करना, (3) `as` वाले mapped types से keys filter करना, (4) strings/tuples पर recursion, (5) unions पर distributive behaviour। असली code में यही चालें typed Redux action lookup, Express handler wrappers और API-client generics चलाती हैं।

---

## 🟢 How it Works — Step by Step
Step 1 → Read the tests first: they are the spec (`Expect<Equal<MyOmit<Order,'id'>, {...}>>`).
Step 2 → Pick the tool: *extract* something? `infer`. *Filter/transform keys*? mapped type + `as`. *Process a string/tuple piece by piece*? recursive conditional type.
Step 3 → Constrain the generic honestly (`K extends keyof T`) so wrong usage fails at the call site, not inside your helper.
Step 4 → Handle the base case (empty tuple, no match) with `never`, `[]` or the input itself.
Step 5 → Run `tsc`. A red `Expect<...>` line with `Type 'false' does not satisfy the constraint 'true'` = your answer is wrong; hover the types to see the difference.
Step 6 → Check edge cases: `[]`, unions, `readonly` tuples, `any`, `never`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पहले tests पढ़ो: वही spec हैं (`Expect<Equal<MyOmit<Order,'id'>, {...}>>`)।
Step 2 → औज़ार चुनो: कुछ *निकालना* है तो `infer`; *keys filter/बदलनी* हैं तो mapped type + `as`; string/tuple को *टुकड़े-टुकड़े* process करना है तो recursive conditional type।
Step 3 → Generic को ईमानदारी से constrain करो (`K extends keyof T`) ताकि गलत use call site पर ही फटे, तुम्हारे helper के अंदर नहीं।
Step 4 → Base case संभालो (खाली tuple, कोई match नहीं): `never`, `[]` या input खुद।
Step 5 → `tsc` चलाओ। लाल `Expect<...>` लाइन और `Type 'false' does not satisfy the constraint 'true'` = जवाब गलत; types hover करके फर्क देखो।
Step 6 → Edge cases जाँचो: `[]`, unions, `readonly` tuples, `any`, `never`।

---

## 🟡 Real World Example
**Paytm's checkout frontend** keeps a Redux `CartAction` union. A `LookUp<CartAction, 'cart/remove'>` gives exactly the `remove` action shape, so each reducer handler gets the precise payload type with no `if (action.type === ...)` chains. The same file uses `MyOmit` to strip `onClick` from button props and force callers to pass `onPay(orderId)` instead of a raw DOM event.

## 🟡 Real Example Hindi mein
**Paytm के checkout frontend** में Redux `CartAction` union है। `LookUp<CartAction, 'cart/remove'>` ठीक `remove` action की shape देता है, इसलिए हर reducer handler को सटीक payload type मिलता है, `if (action.type === ...)` की chain के बिना। उसी file में `MyOmit` से button props से `onClick` हटाकर caller को raw DOM event की जगह `onPay(orderId)` देने पर मजबूर किया जाता है।

---

## 💻 Code Example — Basic

Five warm-ups with built-in compile-time tests. If this file compiles, all tests pass.

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T; // false aaya to compile error

// 1) MyReturnType: function ka return type nikalo
type MyReturnType<F extends (...args: any[]) => any> = F extends (...args: any[]) => infer R ? R : never;

// 2) MyOmit: keys hatao. 'as' clause se key filter hoti hai (TS 4.1+)
type MyOmit<T, K extends keyof T> = { [P in keyof T as P extends K ? never : P]: T[P] };

// 3) TupleToUnion: ['a','b'] -> 'a' | 'b'
type TupleToUnion<T extends readonly unknown[]> = T[number];

// 4) Last / Pop: variadic tuple pattern
type Last<T extends unknown[]> = T extends [...unknown[], infer L] ? L : never;
type Pop<T extends unknown[]> = T extends [...infer Rest, unknown] ? Rest : [];

const placeOrder = (userId: number, paise: number) => ({ orderId: `ORD-${userId}`, paise });
interface Order { id: number; status: 'placed' | 'paid'; paise: number }
const statuses = ['placed', 'paid', 'delivered'] as const;

type Cases = [
  Expect<Equal<MyReturnType<typeof placeOrder>, { orderId: string; paise: number }>>,
  Expect<Equal<MyOmit<Order, 'paise' | 'id'>, { status: 'placed' | 'paid' }>>,
  Expect<Equal<TupleToUnion<typeof statuses>, 'placed' | 'paid' | 'delivered'>>,
  Expect<Equal<Last<[1, 2, 3]>, 3>>,
  Expect<Equal<Last<[]>, never>>,
  Expect<Equal<Pop<[1, 2, 3]>, [1, 2]>>,
  Expect<Equal<Pop<[]>, []>>,
];
export type { Cases };
```

## 💻 Code Example — Advanced

Five more: `LookUp`, `Trim`, `Replace`/`ReplaceAll`, `AppendArgument`, `MyReadonly2`, `MyAwaited`.

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

// 5) LookUp: discriminated union se type ke hisaab se member nikalo (Redux action!)
type LookUp<U extends { type: string }, T extends U['type']> = U extends { type: T } ? U : never;

// 6) Trim: string ke dono taraf ka whitespace hatao (recursive)
type Space = ' ' | '\n' | '\t';
type TrimLeft<S extends string> = S extends `${Space}${infer R}` ? TrimLeft<R> : S;
type TrimRight<S extends string> = S extends `${infer R}${Space}` ? TrimRight<R> : S;
type Trim<S extends string> = TrimLeft<TrimRight<S>>;

// 7) Replace / ReplaceAll
type Replace<S extends string, From extends string, To extends string> =
  From extends '' ? S : S extends `${infer A}${From}${infer B}` ? `${A}${To}${B}` : S;
type ReplaceAll<S extends string, From extends string, To extends string> =
  From extends '' ? S : S extends `${infer A}${From}${infer B}` ? `${A}${To}${ReplaceAll<B, From, To>}` : S;

// 8) AppendArgument: function me ek aur last argument jodo
type AppendArgument<F extends (...args: any[]) => any, A> =
  F extends (...args: infer P) => infer R ? (...args: [...P, A]) => R : never;

// 9) MyReadonly2: sirf diye gaye keys readonly
type MyReadonly2<T, K extends keyof T = keyof T> =
  { readonly [P in keyof T as P extends K ? P : never]: T[P] } & { [P in keyof T as P extends K ? never : P]: T[P] };

// 10) MyAwaited: nested Promise khol do
type MyAwaited<T> = T extends PromiseLike<infer U> ? MyAwaited<U> : T;

type CartAction =
  | { type: 'cart/add'; sku: string; qty: number }
  | { type: 'cart/remove'; sku: string }
  | { type: 'cart/clear' };
interface Todo { title: string; description: string; done: boolean }

type Cases = [
  Expect<Equal<LookUp<CartAction, 'cart/remove'>, { type: 'cart/remove'; sku: string }>>,
  Expect<Equal<Trim<'  Biryani \n'>, 'Biryani'>>,
  Expect<Equal<Replace<'a-b-c', '-', '_'>, 'a_b-c'>>,
  Expect<Equal<ReplaceAll<'a-b-c', '-', '_'>, 'a_b_c'>>,
  Expect<Equal<AppendArgument<(a: number) => string, boolean>, (a: number, x: boolean) => string>>,
  Expect<Equal<MyAwaited<Promise<Promise<number>>>, number>>,
];

// MyReadonly2: 'title' readonly, baaki mutable
const t: MyReadonly2<Todo, 'title'> = { title: 'x', description: 'y', done: false };
t.done = true; // ok
export type { Cases };
export { t };
```

---

## 🟠 Node/Express + React Integration

**Express + Redux + service layer** in one file (run with `npx tsx`):

```typescript
import express from 'express';

type AppendArgument<F extends (...args: any[]) => any, A> =
  F extends (...args: infer P) => infer R ? (...args: [...P, A]) => R : never;
type LookUp<U extends { type: string }, T extends U['type']> = U extends { type: T } ? U : never;
type MyAwaited<T> = T extends PromiseLike<infer U> ? MyAwaited<U> : T;

// --- Express: handler me ctx (logger, user) automatically jodna ---
interface Ctx { userId: number; log: (m: string) => void }
type Handler = (req: express.Request, res: express.Response) => void;
type CtxHandler = AppendArgument<Handler, Ctx>; // (req, res, ctx) => void

function withCtx(h: CtxHandler): Handler {
  return (req, res) => h(req, res, { userId: 7, log: (m) => console.log(m) });
}
const app = express();
app.get('/me', withCtx((req, res, ctx) => { ctx.log('me'); res.json({ id: ctx.userId }); }));

// --- Redux: har action type ke liye ek handler, LookUp se payload type milta hai ---
type CartAction =
  | { type: 'cart/add'; sku: string; qty: number }
  | { type: 'cart/remove'; sku: string }
  | { type: 'cart/clear' };
type CartState = Record<string, number>;
type Handlers = { [T in CartAction['type']]: (s: CartState, a: LookUp<CartAction, T>) => CartState };

const handlers: Handlers = {
  'cart/add': (s, a) => ({ ...s, [a.sku]: (s[a.sku] ?? 0) + a.qty }), // a: add action
  'cart/remove': (s, a) => { const { [a.sku]: _gone, ...rest } = s; return rest; },
  'cart/clear': () => ({}),
};
function cartReducer(s: CartState = {}, a: CartAction): CartState {
  return (handlers[a.type] as (s: CartState, a: CartAction) => CartState)(s, a);
}
console.log(cartReducer(cartReducer({}, { type: 'cart/add', sku: 'pizza', qty: 2 }), { type: 'cart/add', sku: 'pizza', qty: 1 }));

// --- Service layer: Promise ke andar ka type ---
async function loadOrder() { return { id: 1, total: 499 }; }
type LoadedOrder = MyAwaited<ReturnType<typeof loadOrder>>; // { id: number; total: number }
const o: LoadedOrder = { id: 1, total: 499 };
console.log(o.total);
export default app;
// OUTPUT:
// { pizza: 3 }
// 499
```

**React**: `MyOmit` + `TupleToUnion` for a safer button API.

```tsx
import type { ButtonHTMLAttributes } from 'react';

type MyOmit<T, K extends keyof T> = { [P in keyof T as P extends K ? never : P]: T[P] };
type TupleToUnion<T extends readonly unknown[]> = T[number];

const VARIANTS = ['primary', 'danger', 'ghost'] as const; // runtime array + type dono
type Variant = TupleToUnion<typeof VARIANTS>; // 'primary' | 'danger' | 'ghost'

// onClick hata ke apna typed callback do: parent ko event nahi, orderId milega
type PayButtonProps = MyOmit<ButtonHTMLAttributes<HTMLButtonElement>, 'onClick'> & {
  variant: Variant;
  orderId: string;
  onPay: (orderId: string) => void;
};

function PayButton({ variant, orderId, onPay, ...rest }: PayButtonProps) {
  return <button {...rest} className={`btn-${variant}`} onClick={() => onPay(orderId)}>Pay now</button>;
}
export const ok = <PayButton variant="danger" orderId="ORD-1" onPay={(id) => console.log(id)} />;
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Skipping the constraint, hitting `readonly` tuples, and wrong expected values.

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;
type MyOmit<T, K extends keyof T> = { [P in keyof T as P extends K ? never : P]: T[P] };
interface Order { id: number; status: string }
type Bad = MyOmit<Order, 'price'>; // ❌ key hai hi nahi
type Last<T extends unknown[]> = T extends [...unknown[], infer L] ? L : never;
type Wrong = Expect<Equal<Last<[1, 2, 3]>, 2>>; // ❌ galat expected value
type Pop<T extends unknown[]> = T extends [...infer Rest, unknown] ? Rest : [];
type NotTuple = Pop<readonly [1, 2]>; // ❌ readonly tuple
// error TS2344: Type '"price"' does not satisfy the constraint 'keyof Order'.
// error TS2344: Type 'false' does not satisfy the constraint 'true'.
// error TS2344: Type 'readonly [1, 2]' does not satisfy the constraint 'unknown[]'.
//   The type 'readonly [1, 2]' is 'readonly' and cannot be assigned to the mutable type 'unknown[]'.
// Right: constraint `T extends readonly unknown[]` use karo jab readonly bhi allow karna ho.
```

❌ Mistake 2 (no compiler error!): writing `Replace` without the `From extends ''` guard. Without it, `Replace<'abc', '', 'x'>` compiles but quietly returns `'axbc'` (verified: assigning `'zzz'` to it reports `Type '"zzz"' is not assignable to type '"axbc"'`), because `${infer A}` takes one character before the empty match. Always test the empty-string edge case.
✅ Hindi: खाली `From` का guard लगाओ, वरना `Replace<'abc', '', 'x'>` चुपचाप `'axbc'` देगा।

---

## 🧠 Tricky Interview Question

**"Why not write `type Equal<A, B> = A extends B ? true : false`? What breaks?"**

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;
type NaiveEqual<A, B> = A extends B ? true : false; // distributive + one-way: galat tareeka

type N1 = NaiveEqual<'a' | 'b', 'a'>; // boolean (true | false), 'false' hona chahiye tha
type N2 = NaiveEqual<{ a: 1; b: 2 }, { a: 1 }>; // true, jabki types alag hain
type N3 = NaiveEqual<any, string>; // boolean

type Proof = [
  Expect<Equal<N1, boolean>>, // naive ne 'true | false' diya
  Expect<Equal<N2, true>>, // naive ne alag types ko 'equal' bol diya
  Expect<Equal<Equal<'a' | 'b', 'a'>, false>>, // asli Equal sahi 'false' deta hai
  Expect<Equal<Equal<{ a: 1; b: 2 }, { a: 1 }>, false>>,
  Expect<Equal<Equal<any, string>, false>>,
];
export type { Proof, N3 };
```

Answer: `A extends B` is a **one-way** (assignability) check, and because `A` is a naked type parameter it is **distributive** over unions: `'a' | 'b'` becomes `('a' extends 'a' ? ...) | ('b' extends 'a' ? ...)` = `true | false` = `boolean`. It also says `{a:1;b:2}` "equals" `{a:1}` (a subtype is assignable), and `any` matches everything. The standard `Equal` compares two *deferred generic function types*: TypeScript only treats them as identical if the `X` and `Y` are *identical* types, which gives strict equality. Hindi: `extends` बराबरी नहीं, assignability जाँचता है, इसलिए असली `Equal` में function-trick लगता है।

---

## ⚫ Interview Questions + Answers

Q1: Implement `MyOmit<T, K>` without using `Exclude`/`Pick`.
A1: `{ [P in keyof T as P extends K ? never : P]: T[P] }`. The `as` clause (TS 4.1+) remaps keys; mapping a key to `never` drops it. Constrain `K extends keyof T` so a typo errors.

Q2: How does `Last<T>` work?
A2: `T extends [...unknown[], infer L] ? L : never`. A variadic tuple pattern: anything, then one captured last element. `Pop` is the mirror: `[...infer Rest, unknown]`. Empty tuple matches neither pattern, so `Last<[]>` = `never` and `Pop<[]>` falls to `[]`.

Q3: Why does `LookUp` use a conditional on the union itself?
A3: `U extends { type: T } ? U : never` is *distributive*: it runs once per member of `U` and unions the survivors. That is exactly "filter the union by discriminant". It is what `Extract<U, { type: T }>` does.

Q4: How does `AppendArgument` preserve parameter names and return type?
A4: `F extends (...args: infer P) => infer R` captures the parameters as a tuple `P`; the result `(...args: [...P, A]) => R` spreads `P` and adds `A`. Because `P` is a labeled tuple, labels survive.

Q5: Why is `MyAwaited` recursive?
A5: A promise can wrap a promise (`Promise<Promise<number>>`); `T extends PromiseLike<infer U> ? MyAwaited<U> : T` keeps unwrapping until a non-thenable remains. The real `Awaited` also guards objects with a `then` that is not callable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Practising for interviews: re-implementing utilities proves understanding.
- Building library-grade helpers (typed Redux handler maps, Express wrappers).
- Writing compile-time tests (`Expect<Equal<...>>`) for your own complex types.

❌ Avoid when:
- A built-in exists (`Omit`, `ReturnType`, `Awaited`): use it, because it is battle-tested.
- The type is so clever teammates cannot maintain it; prefer simple types plus runtime validation.
- Deep recursion on huge unions: compile times and "excessively deep" errors.

---

## 📊 Visual Diagram
```
TOOLBOX                        EXAMPLE                         RESULT
-------------------------------------------------------------------------
infer (capture)         F extends (...a:any[]) => infer R      MyReturnType
mapped type + as        [P in keyof T as P extends K?never:P]  MyOmit
indexed access T[number]  readonly ['a','b'][number]           TupleToUnion
variadic tuple          T extends [...infer R, unknown]        Pop / Last
distributive filter     U extends {type:T} ? U : never         LookUp
recursive template      S extends `${Space}${infer R}`         Trim
tuple spread            (...args: [...P, A]) => R              AppendArgument
recursive unwrap        T extends PromiseLike<infer U>         MyAwaited
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `Expect<Equal<A,B>>` | Compile-time test | Compile-time test |
| Distributive conditional | Runs per union member | Union के हर member पर चलने वाला conditional |
| Variadic tuple | Tuple with spread `[...T, U]` | Spread वाला tuple |
| `as` clause | Rename/drop keys in mapped type | Mapped type में key बदलना/हटाना |
| Labeled tuple | Tuple with named elements | नाम वाले elements का tuple |
| Base case | Stopping point of recursion | Recursion का रुकने का बिंदु |

---

## ⚡ 3-Line Summary
English:
1. Type challenges re-build utilities using `infer`, conditionals, mapped types with `as`, and recursion.
2. Tests are `Expect<Equal<A, B>>`: the file compiling means you pass; never use plain `extends` for equality.
3. The same patterns power real code: Redux `LookUp`, Express wrappers, typed props.

Hindi:
1. Type challenges में `infer`, conditionals, `as` वाले mapped types और recursion से utilities दोबारा बनाते हैं।
2. Tests `Expect<Equal<A, B>>` हैं: file compile हुई तो pass; बराबरी के लिए सादा `extends` कभी नहीं।
3. यही patterns असली code चलाते हैं: Redux `LookUp`, Express wrappers, typed props।

---

## ➡️ Next Topic
**114. Type-challenges: Medium Set 2** — `Permutation`, `LengthOfString`, `Flatten`, `KebabCase`, `Diff`, `AnyOf`, `IsNever`, `IsUnion`।
