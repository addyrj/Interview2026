# 71. tsconfig Deep Dive — strict Family Flags
# हिंदी में: tsconfig की गहराई — `strict` परिवार के flags

> Verified with TypeScript 5.9 (`tsc --strict`). Version notes: `strictBuiltinIteratorReturn` = TS 5.6 (part of `strict` from 5.6), `exactOptionalPropertyTypes` = 4.4, `noImplicitOverride` = 4.3, `useUnknownInCatchVariables` = 4.4, `erasableSyntaxOnly` = 5.8.

---

## 🔵 Simple Definition (English)
`"strict": true` in `tsconfig.json` is a **single switch that turns on a family of safety flags**: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `strictBuiltinIteratorReturn`, `noImplicitThis`, `useUnknownInCatchVariables` and `alwaysStrict`. You can still turn individual flags off. A few very useful flags (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, ...) are **not** part of `strict` and must be added manually.

## 🔵 सरल परिभाषा (Hindi)
`tsconfig.json` में `"strict": true` एक **अकेला switch है जो safety flags के पूरे परिवार को चालू कर देता है**: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `strictBuiltinIteratorReturn`, `noImplicitThis`, `useUnknownInCatchVariables` और `alwaysStrict`। चाहो तो किसी एक flag को अलग से बंद कर सकते हो। कुछ बहुत काम के flags (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, ...) `strict` में **नहीं** आते, उन्हें खुद जोड़ना पड़ता है।

---

## 🔴 Problem it Solves
A project that starts with loose TypeScript (`strict: false`) quietly accepts `undefined` crashes, implicit `any`, and unsafe callbacks - exactly the bugs TypeScript exists to prevent. Teams then discover that "we use TypeScript" still gives `Cannot read properties of undefined` in production. The strict family flags let you **choose how much safety** you want, and let you migrate old JS-ish code gradually (turn on one flag at a time).

## 🔴 यह क्यों बना? (Hindi)
जो project ढीले TypeScript (`strict: false`) से शुरू होता है, वह `undefined` वाले crashes, implicit `any` और असुरक्षित callbacks चुपचाप स्वीकार कर लेता है - ठीक वही bugs जिन्हें रोकने के लिए TypeScript बना है। फिर पता चलता है कि "हम TypeScript use करते हैं" फिर भी production में `Cannot read properties of undefined` आता है। Strict परिवार के flags से तुम **चुन सकते हो कितनी safety चाहिए**, और पुराने code को धीरे-धीरे migrate कर सकते हो (एक-एक flag चालू करके)।

---

## 🟢 How it Works — Step by Step

Step 1 → `tsc` reads `tsconfig.json` -> `compilerOptions`.
Step 2 → `"strict": true` sets the default of every flag in the family to `true`.
Step 3 → An explicit flag always wins: `{ "strict": true, "strictPropertyInitialization": false }` keeps the rest strict.
Step 4 → Flags **outside** the family (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `noImplicitReturns`, `noFallthroughCasesInSwitch`, `noPropertyAccessFromIndexSignature`, `noUnusedLocals`, `noUnusedParameters`) are opt-in.
Step 5 → New TypeScript versions may add checks to `strict` (e.g. `strictBuiltinIteratorReturn` in 5.6), so an upgrade can create new errors even if your code did not change.
Step 6 → Use `tsc --showConfig` to see the final resolved options.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `tsc` `tsconfig.json` -> `compilerOptions` पढ़ता है।
Step 2 → `"strict": true` परिवार के हर flag का default `true` कर देता है।
Step 3 → अलग से लिखा flag हमेशा जीतता है: `{ "strict": true, "strictPropertyInitialization": false }` बाकी सब strict रखता है।
Step 4 → परिवार के **बाहर** के flags (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `noImplicitReturns`, `noFallthroughCasesInSwitch`, `noPropertyAccessFromIndexSignature`, `noUnusedLocals`, `noUnusedParameters`) opt-in हैं।
Step 5 → नए TypeScript versions `strict` में checks जोड़ सकते हैं (जैसे 5.6 में `strictBuiltinIteratorReturn`), इसलिए upgrade पर code बदले बिना भी नए errors आ सकते हैं।
Step 6 → अंतिम resolved options देखने के लिए `tsc --showConfig` चलाओ।

---

## 🟡 Real World Example
**A Swiggy-style order API** is migrated from JS. Day 1: `strict: false`. The team enables `noImplicitAny` first (fix 300 params), then `strictNullChecks` (fixes 120 "possibly undefined" bugs - several were real production crashes in the "coupon not found" path), then `strictPropertyInitialization`. Finally they add `noUncheckedIndexedAccess` so `orders[0]` is `Order | undefined`. Each step is a separate PR.

## 🟡 Real Example Hindi mein
**Swiggy-जैसे order API** को JS से migrate किया जा रहा है। Day 1: `strict: false`। Team पहले `noImplicitAny` चालू करती है (300 params ठीक करो), फिर `strictNullChecks` (120 "possibly undefined" bugs - कई "coupon not found" path के असली production crashes थे), फिर `strictPropertyInitialization`। आख़िर में `noUncheckedIndexedAccess` जोड़ते हैं ताकि `orders[0]` का type `Order | undefined` हो। हर कदम अलग PR।

---

## 💻 Code Example — Basic

Recommended starting `tsconfig.json` for a Node/Express service (checked with `tsc -p` on a sample project):

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

What the 9 flags inside `strict` catch (each error below is the real compiler output):

```typescript
// 1) noImplicitAny - every parameter needs a type
function total(price: number, qty) { // ❌ error TS7006: Parameter 'qty' implicitly has an 'any' type.
  return price * qty;
}
```

```typescript
// 2) strictNullChecks - null/undefined are separate types
interface User { name: string; email: string | null }
declare function find(id: number): User | undefined;
const u = find(1);
console.log(u.name); // ❌ error TS18048: 'u' is possibly 'undefined'.
const e: string = (u as User).email; // ❌ error TS2322: Type 'string | null' is not assignable to type 'string'.
```

```typescript
// 3) strictPropertyInitialization - fields must be set in the constructor
class Svc {
  name: string; // ❌ error TS2564: Property 'name' has no initializer and is not definitely assigned in the constructor.
}
```

```typescript
// 4) useUnknownInCatchVariables - catch variable is `unknown`, not `any`
try {
  JSON.parse("{bad");
} catch (err) {
  console.log(err.message); // ❌ error TS18046: 'err' is of type 'unknown'.
  if (err instanceof Error) console.log(err.message); // OK: narrowed first
}
```

## 💻 Code Example — Advanced

```typescript
// 5) strictFunctionTypes - function parameters are checked contravariantly
type Handler = (e: string | number) => void;
const h: Handler = (e: string) => {}; // ❌ error TS2322: Type '(e: string) => void' is not assignable to type 'Handler'.
// BUT method-shorthand stays bivariant (deliberate escape hatch, no error):
interface Box { setM(v: string | number): void }
const ok: Box = { setM: (v: string) => {} }; // compiles even under strict (known unsoundness)
```

```typescript
// 6) strictBindCallApply - bind/call/apply are type-checked
function add(a: number, b: number) { return a + b; }
console.log(add.call(null, "1", 2)); // ❌ error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

```typescript
// 7) noImplicitThis
const f2 = function () {
  return this.n; // ❌ error TS2683: 'this' implicitly has type 'any' because it does not have a type annotation.
};
```

```typescript
// 8) strictBuiltinIteratorReturn (TS 5.6) - iterator.next().value may be undefined
const it = [1, 2, 3][Symbol.iterator]();
const r = it.next();
const v: number = r.value; // ❌ error TS2322: Type 'number | undefined' is not assignable to type 'number'.
```

Flags that are **not** in `strict` but you should add (each needs its own flag, shown in the first comment line):

```typescript
// flags: --noUncheckedIndexedAccess
const items = ["a", "b"];
const first: string = items[5]; // ❌ error TS2322: Type 'string | undefined' is not assignable to type 'string'.
const prices: Record<string, number> = {};
const p: number = prices["x"]; // ❌ error TS2322: Type 'number | undefined' is not assignable to type 'number'.
```

```typescript
// flags: --exactOptionalPropertyTypes
interface Opts { retries?: number }
const o: Opts = { retries: undefined }; // ❌ error TS2375: Type '{ retries: undefined; }' is not assignable to type 'Opts' with 'exactOptionalPropertyTypes: true'. Consider adding 'undefined' to the types of the target's properties.
```

```typescript
// flags: --noImplicitOverride
class Base { save() {} }
class Child extends Base {
  save() {} // ❌ error TS4114: This member must have an 'override' modifier because it overrides a member in the base class 'Base'.
}
```

```typescript
// flags: --noPropertyAccessFromIndexSignature
const cfg: { [k: string]: string } = {};
console.log(cfg.host); // ❌ error TS4111: Property 'host' comes from an index signature, so it must be accessed with ['host'].
```

```typescript
// flags: --noImplicitReturns --noFallthroughCasesInSwitch
function label(n: number) {
  if (n > 1) { return "big"; } // ❌ error TS7030: Not all code paths return a value.
}
function g(n: number) {
  switch (n) {
    case 1: console.log("a"); // ❌ error TS7029: Fallthrough case in switch.
    case 2: console.log("b"); break;
  }
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// flags: --noUncheckedIndexedAccess --noImplicitReturns
import express from "express"; // Express with strict typing

const app = express();
app.use(express.json());

// noUncheckedIndexedAccess forces you to handle "missing" explicitly
const stock: Record<string, number> = { "paneer-tikka": 12 };

app.get("/stock/:sku", (req, res) => {
  const qty = stock[req.params.sku]; // type is number | undefined (flag on) -> handle it
  if (qty === undefined) {
    res.status(404).json({ error: "unknown sku" }); // missing sku
    return; // noImplicitReturns: every path ends the same way
  }
  res.json({ sku: req.params.sku, qty }); // qty is a number here
});
```

```tsx
// React + strictNullChecks: state starts as null, so the UI must handle it
import React, { useState } from "react";

export function Profile() {
  const [user, setUser] = useState<{ name: string } | null>(null); // null until loaded
  // return user.name;  // would be an error: 'user' is possibly 'null'.
  return (
    <div>
      <button onClick={() => setUser({ name: "Asha" })}>Load</button>
      <span>{user ? user.name : "Loading..."}</span> {/* narrowing satisfies strictNullChecks */}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Setting `strict: true` but then silencing errors with `any` / `!`
```typescript
declare function find(id: number): { name: string } | undefined;
const name = find(1)!.name; // compiles, but the crash is back at runtime
```
✅ Right: `const u = find(1); if (!u) throw new Error("not found");`.

❌ Mistake 2: Thinking `strict` includes every strict-sounding flag
`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride` are **not** enabled by `strict`. `strict: true` alone does not give you `string | undefined` for `arr[i]`.

❌ Mistake 3: Using `--strict` on the CLI and forgetting tsconfig is ignored
When you pass files directly (`tsc file.ts`), `tsconfig.json` is **ignored**. Use `tsc -p .` or put flags on the CLI.

❌ Mistake 4: Enabling `strictPropertyInitialization` without `strictNullChecks`
```typescript
// In tsconfig: { "strict": false, "strictPropertyInitialization": true }
// ❌ error TS5052: Option 'strictPropertyInitialization' cannot be specified without specifying option 'strictNullChecks'.
```
(Real output from `tsc -p` with exactly that tsconfig.)

---

## 🧠 Tricky Interview Question

```typescript
interface Box { setM(v: string | number): void; setP: (v: string | number) => void }
const b: Box = {
  setM: (v: string) => {},
  setP: (v: string) => {},
};
```
Answer: only `setP` errors under `strict` (`error TS2322 ... Types of parameters 'v' and 'v' are incompatible`). `strictFunctionTypes` applies to **function-typed properties** but **not to method declarations** (`setM(...)`), which stay bivariant. This is why `Array<T>.push` etc. remain usable with subtypes. Rule to remember: prefer the property syntax when you want strict checking of callbacks.

---

## ⚫ Interview Questions + Answers

Q1: What does `"strict": true` enable?
A1: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `strictBuiltinIteratorReturn` (5.6+), `noImplicitThis`, `useUnknownInCatchVariables`, `alwaysStrict` (emits `"use strict"` and parses in strict mode).

Q2: Which flags are commonly added on top of `strict`?
A2: `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `noImplicitReturns`, `noFallthroughCasesInSwitch`, `noPropertyAccessFromIndexSignature`; plus `noUnusedLocals/Parameters` (or let ESLint do that).

Q3: How do you migrate a large JS codebase to strict?
A3: Start with `allowJs/checkJs` off, enable flags one at a time (`noImplicitAny` -> `strictNullChecks` -> rest), use `// @ts-expect-error` (not `@ts-ignore`) for known leftovers, and fail CI on new errors.

Q4: Difference between `// @ts-ignore` and `// @ts-expect-error`?
A4: `@ts-expect-error` errors if the next line has **no** error (so stale suppressions are found); `@ts-ignore` never complains.

Q5: What does `useUnknownInCatchVariables` change?
A5: `catch (e)` gives `e: unknown` instead of `any`, forcing `instanceof Error` or a type guard before using `e.message`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every new project: start with `strict: true` plus the extra flags above
- Libraries you publish (consumers depend on your types)

❌ Avoid / relax when:
- Mid-migration from JS: turn flags on gradually instead of `strict` on day 1
- A flag generates noise you cannot act on (e.g. `exactOptionalPropertyTypes` with old third-party types) - turn that one off, keep the rest

---

## 📊 Visual Diagram
```
 "strict": true
   ├── noImplicitAny
   ├── strictNullChecks
   ├── strictFunctionTypes
   ├── strictBindCallApply
   ├── strictPropertyInitialization   (needs strictNullChecks)
   ├── strictBuiltinIteratorReturn    (5.6+)
   ├── noImplicitThis
   ├── useUnknownInCatchVariables
   └── alwaysStrict

 NOT included (add yourself):
   noUncheckedIndexedAccess, exactOptionalPropertyTypes, noImplicitOverride,
   noImplicitReturns, noFallthroughCasesInSwitch, noPropertyAccessFromIndexSignature
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `strict` | Umbrella flag for the strict family | सुरक्षा flags का समूह |
| `strictNullChecks` | null/undefined are distinct types | null/undefined अलग types |
| `noImplicitAny` | Error when a type falls back to `any` | अपने-आप `any` बनने पर error |
| `noUncheckedIndexedAccess` | `arr[i]` includes `undefined` | `arr[i]` में `undefined` भी जुड़ता है |
| Bivariance | Method params checked in both directions | Method params दोनों दिशा में check |
| `@ts-expect-error` | Suppress an error, fail if none | Error दबाओ, पर error न हो तो fail |

---

## ⚡ 3-Line Summary
English:
1. `strict: true` turns on nine safety flags; individual flags can override it.
2. Add `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride` yourself - they are not in `strict`.
3. Migrate legacy code by enabling flags one by one; `tsc file.ts` ignores tsconfig.

Hindi:
1. `strict: true` नौ safety flags चालू करता है; अलग flag से override कर सकते हो।
2. `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride` खुद जोड़ो - ये `strict` में नहीं हैं।
3. पुराने code को एक-एक flag चालू करके migrate करो; `tsc file.ts` tsconfig को ignore करता है।

---

## ➡️ Next Topic
**72. Module Resolution (node16, bundler, paths)** - How `import "./x"` and `import "pkg"` are found, and which `moduleResolution` to pick.
