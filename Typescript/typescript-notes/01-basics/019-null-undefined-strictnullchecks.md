# 19. null and undefined + strictNullChecks
# हिंदी में: null, undefined और strictNullChecks

> TypeScript 5.x | `strictNullChecks` is part of `"strict": true` | `?.` and `??` since TS 3.7 | `NonNullable` utility since TS 2.8

---

## 🔵 Simple Definition (English)
`undefined` means "no value was assigned / the thing is missing"; `null` means "there is deliberately no value". They are separate types in TypeScript. With **`strictNullChecks` ON** (part of `strict`), `null` and `undefined` are NOT members of other types: `string` means a real string and `string | null` means "a string or null", so the compiler forces you to check before you use a possibly-missing value. With it OFF, `null` and `undefined` are silently assignable to everything, and the famous `Cannot read properties of undefined` crashes return.

## 🔵 सरल परिभाषा (Hindi)
`undefined` का मतलब "कोई value assign नहीं हुई / चीज़ गायब है"; `null` का मतलब "जानबूझकर कोई value नहीं"। TypeScript में ये दो अलग types हैं। **`strictNullChecks` ON** होने पर (यह `strict` का हिस्सा है) `null` और `undefined` दूसरे types के सदस्य **नहीं** होते: `string` का मतलब असली string और `string | null` का मतलब "string या null", इसलिए compiler आपको गायब हो सकने वाली value इस्तेमाल करने से पहले check करने पर मजबूर करता है। OFF होने पर `null` और `undefined` हर type में चुपचाप assign हो जाते हैं और मशहूर `Cannot read properties of undefined` crashes वापस आ जाते हैं।

---

## 🔴 Problem it Solves
Tony Hoare called null references his "billion dollar mistake". In JavaScript, `user.address.city` crashes if `address` is missing, `map.get(key)` may return `undefined`, `array.find()` may find nothing, `document.getElementById` may return `null`, and a SQL Server `NULL` column arrives as `null`. These are the most common production errors in Node and React apps. `strictNullChecks` makes absence part of the type, so every place that can be missing is visible and must be handled before you dereference it.

## 🔴 यह क्यों बना? (Hindi)
Tony Hoare ने null references को अपनी "billion dollar mistake" कहा था। JavaScript में अगर `address` गायब हो तो `user.address.city` crash करता है, `map.get(key)` `undefined` दे सकता है, `array.find()` को कुछ न मिले, `document.getElementById` `null` दे सकता है, और SQL Server का `NULL` column `null` बनकर आता है। Node और React apps में production के सबसे आम errors यही हैं। `strictNullChecks` absence को type का हिस्सा बना देता है, इसलिए जो भी जगह गायब हो सकती है वह दिखती है और dereference से पहले उसे handle करना पड़ता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Turn on `"strict": true` (or `"strictNullChecks": true`) in tsconfig. Now `let s: string = null` is an error (TS2322).
Step 2 → Model absence explicitly: `string | null` (explicitly empty), `string | undefined` (not provided), or optional `x?: string`.
Step 3 → Sources of `undefined` in the standard library are typed for you: `Array.prototype.find` returns `T | undefined`, `Map.get` returns `V | undefined`, optional properties are `T | undefined`, indexed access with `noUncheckedIndexedAccess` adds `| undefined`.
Step 4 → Using a possibly-null value (`x.length`) gives TS18047 "'x' is possibly 'null'" (or TS18048 for `undefined`, TS2532 in older versions). You must **narrow** first.
Step 5 → Narrow with: `if (x)` (truthiness, also removes `0`/`''`), `x !== null`, `x != null` (removes both `null` and `undefined`), `typeof x === 'string'`, early return.
Step 6 → Operators: optional chaining `a?.b?.c` stops at null/undefined and returns `undefined`; nullish coalescing `a ?? def` uses `def` only for `null`/`undefined` (unlike `||`, which also replaces `0` and `''`).
Step 7 → The non-null assertion `x!` tells the compiler "trust me", with no runtime check. Use sparingly (see topic 20).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → tsconfig में `"strict": true` (या `"strictNullChecks": true`) चालू करो। अब `let s: string = null` error है (TS2322)।
Step 2 → Absence को साफ़ model करो: `string | null` (जानबूझकर खाली), `string | undefined` (दिया नहीं गया), या optional `x?: string`।
Step 3 → Standard library में `undefined` के स्रोत पहले से type हैं: `Array.prototype.find` `T | undefined` देता है, `Map.get` `V | undefined`, optional properties `T | undefined`, और `noUncheckedIndexedAccess` के साथ indexed access में `| undefined` जुड़ता है।
Step 4 → Possibly-null value इस्तेमाल करने (`x.length`) पर TS18047 "'x' is possibly 'null'" (या `undefined` के लिए TS18048, पुराने versions में TS2532) आता है। पहले **narrow** करना पड़ता है।
Step 5 → Narrow करने के तरीके: `if (x)` (truthiness, `0`/`''` भी हटते हैं), `x !== null`, `x != null` (`null` और `undefined` दोनों हटाता है), `typeof x === 'string'`, early return।
Step 6 → Operators: optional chaining `a?.b?.c` null/undefined पर रुककर `undefined` देता है; nullish coalescing `a ?? def` सिर्फ़ `null`/`undefined` पर `def` लेता है (`||` के उलट, जो `0` और `''` भी बदल देता है)।
Step 7 → Non-null assertion `x!` compiler से कहता है "मुझ पर भरोसा करो", runtime check के बिना। कम इस्तेमाल करो (topic 20 देखो)।

---

## 🟡 Real World Example
**Paytm's wallet screen** shows `user.profile.photoUrl`. In the SQL Server `Users` table `PhotoUrl` is nullable, so the Express API sends `photoUrl: null` for many users, and the `GET /users/:id` query may return no row at all (`undefined`). With `strictNullChecks`, the type is `User | undefined` for the lookup and `photoUrl: string | null` for the field. The React component must render a placeholder for `null` and a 404 for `undefined`; forgetting either is a compile error instead of a blank-screen crash for 1% of users in production.

## 🟡 Real Example Hindi mein
**Paytm की wallet screen** `user.profile.photoUrl` दिखाती है। SQL Server की `Users` table में `PhotoUrl` nullable है, इसलिए Express API कई users के लिए `photoUrl: null` भेजती है, और `GET /users/:id` query कोई row भी न दे सकती है (`undefined`)। `strictNullChecks` के साथ lookup का type `User | undefined` और field का `photoUrl: string | null` है। React component को `null` के लिए placeholder और `undefined` के लिए 404 दिखाना ही पड़ता है; इनमें से कुछ भूलना compile error है, production में 1% users के लिए blank-screen crash नहीं।

---

## 💻 Code Example — Basic

```typescript
// null-basic.ts  (TypeScript 5.x, strict)

interface User {
  id: number;
  name: string;
  photoUrl: string | null;     // DB column is NULL when the user has no photo
  phone?: string;              // optional: may be undefined
}

const users: User[] = [
  { id: 1, name: 'Asha', photoUrl: 'https://cdn/asha.png' },
  { id: 2, name: 'Ravi', photoUrl: null, phone: '98765' },
];

// find returns User | undefined: the compiler knows nothing may match
function findUser(id: number): User | undefined {
  return users.find((u) => u.id === id);
}

// 1. Narrowing with an early return
function photoOf(id: number): string {
  const user = findUser(id);                 // User | undefined
  if (!user) return 'user not found';        // narrow: undefined removed
  if (user.photoUrl === null) return '/placeholder.png'; // narrow: null removed
  return user.photoUrl;                      // here photoUrl is string
}

// 2. Optional chaining + nullish coalescing
function phoneOf(id: number): string {
  return findUser(id)?.phone ?? 'no phone';  // ?. stops at undefined, ?? gives the default
}

// 3. ?? vs ||: they differ for 0 and ''
const discount = 0;
console.log(discount || 10);                 // 10: || replaces 0 (usually a bug)
console.log(discount ?? 10);                 // 0: ?? only replaces null/undefined

// 4. != null removes BOTH null and undefined
function len(s: string | null | undefined): number {
  return s != null ? s.length : 0;           // s is string in the true branch
}

console.log(photoOf(1), photoOf(2), photoOf(9));
console.log(phoneOf(2), phoneOf(1), phoneOf(9), len(null), len('abc'));
```

Run with `npx tsx null-basic.ts`. Real output:
```
10
0
https://cdn/asha.png /placeholder.png user not found
98765 no phone no phone 0 3
```

## 💻 Code Example — Advanced

```typescript
// null-advanced.ts  (TypeScript 5.x)

// 1. NonNullable<T> strips null and undefined from a type
type MaybeId = number | null | undefined;
type DefiniteId = NonNullable<MaybeId>;               // number

// 2. A user-defined type guard that filters out nulls from an array
function isPresent<T>(value: T): value is NonNullable<T> {
  return value !== null && value !== undefined;
}
const raw: (string | null | undefined)[] = ['a', null, 'b', undefined];
const clean: string[] = raw.filter(isPresent);        // string[] (plain filter(Boolean) would keep the union)

// 3. Distinguishing null vs undefined meaning in an API result
type Lookup<T> = { status: 'found'; value: T } | { status: 'missing' };
function lookup(map: Map<string, number>, key: string): Lookup<number> {
  const v = map.get(key);                             // number | undefined
  return v === undefined ? { status: 'missing' } : { status: 'found', value: v };
}

// 4. Assertion function (TS 3.7+) that throws on absence
function assertPresent<T>(v: T, msg: string): asserts v is NonNullable<T> {
  if (v === null || v === undefined) throw new Error(msg);
}

const prices = new Map<string, number>([['paneer', 220]]);
const p = prices.get('paneer');                       // number | undefined
assertPresent(p, 'price missing');                    // after this call p is number
const withTax: number = p * 1.05;                     // no error: narrowed by the assertion

// 5. Optional call and element access
type Handlers = { onPaid?: (id: string) => void; tags?: string[] };
const h: Handlers = {};
h.onPaid?.('pay_1');                                  // call only if defined
const firstTag = h.tags?.[0] ?? 'none';               // safe indexing

// 6. Null in JSON/SQL: nullable column => T | null, not T | undefined
interface Row { Id: number; DeletedAt: string | null }
const row: Row = { Id: 1, DeletedAt: null };
const isDeleted = row.DeletedAt !== null;

console.log(clean, lookup(prices, 'x').status, lookup(prices, 'paneer'));
console.log(withTax.toFixed(1), firstTag, isDeleted);

type D = DefiniteId;                                  // use the alias so it is not "unused"
const sample: D = 5;
console.log(sample);
```

Run with `npx tsx null-advanced.ts`. Real output:
```
[ 'a', 'b' ] missing { status: 'found', value: 220 }
231.0 none false
5
```

---

## 🟠 Node/Express + React Integration

```tsx
// server.ts  (Express + mssql): the lookup may return no row
import express from 'express';
const app = express();

interface UserRow { Id: number; Name: string; PhotoUrl: string | null }
const db = new Map<number, UserRow>([[1, { Id: 1, Name: 'Asha', PhotoUrl: null }]]);

app.get('/users/:id', (req, res) => {
  const row = db.get(Number(req.params.id));        // UserRow | undefined
  if (!row) {                                       // handle absence BEFORE using row
    res.status(404).json({ error: 'not found' });
    return;
  }
  res.json({ id: row.Id, name: row.Name, photoUrl: row.PhotoUrl }); // photoUrl stays string | null
});

// Express: req.query values are string | ParsedQs | string[] | undefined
app.get('/search', (req, res) => {
  const q = typeof req.query.q === 'string' ? req.query.q : ''; // narrow before use
  res.json({ q });
});

// Avatar.tsx  (React): null from API, null from refs
import { useRef } from 'react';
export function Avatar({ photoUrl }: { photoUrl: string | null }) {
  const imgRef = useRef<HTMLImageElement>(null);    // RefObject: .current is HTMLImageElement | null
  const onClick = () => {
    imgRef.current?.focus();                        // must handle null: component may be unmounted
  };
  return photoUrl ? <img ref={imgRef} src={photoUrl} onClick={onClick} /> : <span>No photo</span>;
}

// authSlice.ts  (Redux Toolkit): null as "not logged in" state
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
interface AuthState { userId: number | null }
const slice = createSlice({
  name: 'auth',
  initialState: { userId: null } as AuthState,      // widen the initial null to the union
  reducers: {
    loggedIn(state, action: PayloadAction<number>) { state.userId = action.payload; },
    loggedOut(state) { state.userId = null; },
  },
});
export const { loggedIn, loggedOut } = slice.actions;
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a possibly-null value without checking
```typescript
// ❌ Wrong: x might be null
function f(x: string | null) { return x.length; }
// error TS18047: 'x' is possibly 'null'.
```
```typescript
// ✅ Right: narrow first (or use ?.)
function f(x: string | null): number { return x === null ? 0 : x.length; }
```

❌ Mistake 2: Assigning `null` / ignoring `Map.get` and `find`
```typescript
// ❌ Wrong: null is not a string under strictNullChecks
let q: string = null;
// error TS2322: Type 'null' is not assignable to type 'string'.
const m = new Map<string, number>();
// ❌ Wrong: get() may return undefined
const v: number = m.get('a');
// error TS2322: Type 'number | undefined' is not assignable to type 'number'.
//   Type 'undefined' is not assignable to type 'number'.
```
✅ Correct: `let q: string | null = null;` and `const v = m.get('a') ?? 0;`.

❌ Mistake 3: Using `||` for defaults when `0`, `''` or `false` are valid values: `const qty = input.qty || 1` turns an intentional `0` into `1`. Use `??`.

❌ Mistake 4: Switching `strictNullChecks` off "to make errors go away". The errors are real bugs. Fix them with narrowing; migrate old JS code file by file instead.

---

## 🧠 Tricky Interview Question

```typescript
console.log(typeof null, typeof undefined);
console.log(null == undefined, null === undefined);
const n = null as string | null;           // variables, so TS 5.x does not flag always-nullish literals
const z = 0 as number | null;
const e = '' as string;
const u = undefined as { x: number } | undefined;
console.log(n ?? 'a', z ?? 'a', e || 'a', u?.x);
```
Answer: Output is `object undefined`, then `true false`, then `a 0 a undefined`. `typeof null === 'object'` is a historic JavaScript quirk (TypeScript still types `null` as its own type). `==` treats `null` and `undefined` as equal but `===` does not, which is why `x != null` is the idiomatic way to check for both. `??` only replaces `null`/`undefined`, so `0 ?? 'a'` is `0`, while `'' || 'a'` is `'a'` because `||` replaces every falsy value. `undefined?.x` short-circuits to `undefined`. (Note: TS 5.6+ reports error TS2871 "This expression is always nullish" if you write the literals `null ?? 'a'` or `undefined?.x` directly, so the example uses typed variables, as real code does.)

---

## ⚫ Interview Questions + Answers

Q1: What does `strictNullChecks` change?
A1: `null` and `undefined` become their own types and are no longer assignable to every other type. A `string` is always a string; to allow absence you write `string | null` or `string | undefined`. Any dereference of such a union (`x.length`) is an error until you narrow it. Without it, TypeScript lets null/undefined flow everywhere and you lose most of the safety.

Q2: `null` vs `undefined`: which to use and when?
A2: `undefined` = "not provided/uninitialised" (missing property, optional parameter, `find` result, function with no return). `null` = "explicitly empty" (a nullable SQL column, JSON from an API, a cleared form value, `useRef(null)`). Pick a convention at the API boundary (SQL Server NULL becomes JSON `null`), and use `x != null` when you want to treat both the same.

Q3: Difference between `?.`, `??` and `!`?
A3: `a?.b` safely reads `b`, producing `undefined` if `a` is null/undefined. `a ?? b` picks `b` only when `a` is null/undefined (not for `0`, `''`, `false`). `a!` is a compile-time assertion that `a` is neither null nor undefined with NO runtime check, so a wrong assumption still crashes.

Q4: How do you filter nulls out of an array and keep the type clean?
A4: `arr.filter((x): x is NonNullable<typeof x> => x != null)` or a reusable `isPresent<T>(v: T): v is NonNullable<T>` guard. (TypeScript 5.5 infers type predicates for simple inline arrow functions like `x => x !== null`, but an explicit guard works in every 5.x version.) `filter(Boolean)` does not narrow the type.

Q5: What does `noUncheckedIndexedAccess` add?
A5: It makes array and index-signature access return `T | undefined` (`arr[0]` is `string | undefined`), catching out-of-bounds reads. It is not part of `strict`; many strict codebases enable it, accepting a few extra checks for more safety.

---

## 🔷 When to Use + When Not to Use
✅ Use `strictNullChecks` (always) and:
- `T | null` for nullable DB columns and JSON, `T | undefined` or `?` for "not provided"
- `?.` and `??` to read deep optional data, early returns to narrow

❌ Avoid:
- Turning the flag off, or sprinkling `!` to silence it
- Using `||` for defaults when `0`/`''`/`false` are legitimate values
- Returning both `null` and `undefined` from the same function with different meanings, unless documented

---

## 📊 Visual Diagram
```
 strictNullChecks OFF               strictNullChecks ON
 string  = string + null + undef    string          = string only
                                    string | null   = string OR null
 x.length  ✔ compiles, may crash    x.length  ✘ TS18047 until narrowed

 narrow ──►  if (x)  |  x !== null  |  x != null  |  x?.length  |  x ?? 'default'

 DB NULL ──► JSON null ──► T | null ──► React: render placeholder
 map.get / find ──► T | undefined ──► Express: 404
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| strictNullChecks | null/undefined are separate types | null/undefined अलग types |
| Narrowing | Removing union members via checks | Checks से union छोटा करना |
| Optional chaining `?.` | Safe property access | सुरक्षित property access |
| Nullish coalescing `??` | Default only for null/undefined | सिर्फ़ null/undefined पर default |
| NonNullable<T> | Removes null and undefined | null और undefined हटाता है |
| Non-null assertion `!` | Compiler trust, no runtime check | बिना check का भरोसा |
| noUncheckedIndexedAccess | Index reads include undefined | Index read में undefined जुड़ता है |

---

## ⚡ 3-Line Summary
English:
1. With `strictNullChecks`, `null` and `undefined` are separate types, so `string` is never null and absence is written as `string | null`.
2. Narrow before use (`if`, `!= null`, `?.`) and prefer `??` over `||` for defaults.
3. Avoid `!` and never turn the flag off; use `T | null` for DB/JSON nulls and `T | undefined` for "missing".

Hindi:
1. `strictNullChecks` में `null` और `undefined` अलग types हैं, इसलिए `string` कभी null नहीं होता और absence को `string | null` लिखा जाता है।
2. इस्तेमाल से पहले narrow करो (`if`, `!= null`, `?.`) और defaults के लिए `||` की जगह `??` लो।
3. `!` से बचो और flag कभी बंद मत करो; DB/JSON nulls के लिए `T | null` और "गायब" के लिए `T | undefined` इस्तेमाल करो।

---

## ➡️ Next Topic
**20. Type Assertions (as) and the Non-null Assertion (!)** — when you know more than the compiler, how to say so safely, and the cost of being wrong.
