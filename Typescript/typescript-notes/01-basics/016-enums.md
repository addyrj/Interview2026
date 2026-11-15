# 16. Enums (numeric, string, const) + Alternatives
# हिंदी में: Enums (नाम वाले constants का set) और उनके विकल्प

> TypeScript 5.x | Enums are one of the few TS features that emit runtime JavaScript | `--erasableSyntaxOnly` (TS 5.8) and Node's type-stripping reject enums

---

## 🔵 Simple Definition (English)
An **enum** defines a named set of constants. **Numeric enums** (`enum Dir { Up, Down }`) map names to numbers starting at 0 (with a reverse mapping number to name). **String enums** (`enum Status { Placed = 'PLACED' }`) map names to strings and have no reverse mapping. **`const enum`** is inlined at compile time and produces no object. Because enums generate real JavaScript (an object) and behave nominally, many teams now prefer alternatives: a union of string literals, or an `as const` object plus a derived union type.

## 🔵 सरल परिभाषा (Hindi)
**Enum** नाम वाले constants का set define करता है। **Numeric enum** (`enum Dir { Up, Down }`) नामों को 0 से शुरू होने वाले numbers से map करता है (साथ में number से नाम का reverse mapping भी)। **String enum** (`enum Status { Placed = 'PLACED' }`) नामों को strings से map करता है और इसमें reverse mapping नहीं होती। **`const enum`** compile time पर inline हो जाता है और कोई object नहीं बनाता। क्योंकि enums असली JavaScript (एक object) बनाते हैं और nominal की तरह व्यवहार करते हैं, कई teams अब विकल्प पसंद करती हैं: string literals का union, या `as const` object के साथ derived union type।

---

## 🔴 Problem it Solves
Magic numbers and magic strings (`if (status === 3)`) are unreadable and easy to get wrong. A named set (`OrderStatus.Delivered`) is self-documenting, autocompleted and refactorable. Enums were TypeScript's early answer, before string-literal unions existed (TS 1.8). Today you need to know them for two reasons: legacy and library code is full of enums (and interviewers love their quirks), and you must be able to explain why modern codebases replace them.

## 🔴 यह क्यों बना? (Hindi)
Magic numbers और magic strings (`if (status === 3)`) पढ़ने में मुश्किल और गलत होने में आसान होते हैं। नाम वाला set (`OrderStatus.Delivered`) खुद-documenting, autocomplete वाला और refactor के लायक होता है। String-literal unions (TS 1.8) से पहले enums ही TypeScript का जवाब थे। आज दो कारणों से इन्हें जानना ज़रूरी है: legacy और library code enums से भरा है (और interviewers को इनकी quirks पसंद हैं), और आपको समझाना आना चाहिए कि modern codebases इन्हें क्यों बदल रहे हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `enum Dir { Up, Down }` compiles to an object built by an IIFE: `Dir[Dir["Up"] = 0] = "Up"`. So `Dir.Up === 0` AND `Dir[0] === "Up"` (reverse mapping).
Step 2 → Numeric members auto-increment from the previous value; you can set the start: `enum Code { Ok = 200, Created, Accepted }` gives 200, 201, 202.
Step 3 → String enum members must each be initialised explicitly. They emit only the forward mapping `Status.Placed = 'PLACED'`.
Step 4 → String enums are **nominal-ish**: a plain `'PLACED'` literal is NOT assignable to `Status` (error TS2322). You must write `Status.Placed`.
Step 5 → `const enum` members are replaced by their literal values at each use site and the enum object is not emitted. With `isolatedModules` / Babel / esbuild / SWC this is fragile, so avoid it across files.
Step 6 → The alternative `const Status = { Placed: 'PLACED' } as const; type Status = (typeof Status)[keyof typeof Status];` gives a runtime object AND a union type with no special emit.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `enum Dir { Up, Down }` एक IIFE से बना object बनता है: `Dir[Dir["Up"] = 0] = "Up"`। इसलिए `Dir.Up === 0` और `Dir[0] === "Up"` दोनों सच (reverse mapping)।
Step 2 → Numeric members पिछली value से auto-increment होते हैं; शुरुआत भी set कर सकते हो: `enum Code { Ok = 200, Created, Accepted }` से 200, 201, 202।
Step 3 → String enum के हर member को explicitly initialise करना पड़ता है। इनमें सिर्फ़ forward mapping बनती है `Status.Placed = 'PLACED'`।
Step 4 → String enums **nominal जैसे** हैं: सादा `'PLACED'` literal `Status` में assignable नहीं है (error TS2322)। `Status.Placed` ही लिखना पड़ता है।
Step 5 → `const enum` के members हर use की जगह literal values से बदल दिए जाते हैं और enum object emit नहीं होता। `isolatedModules` / Babel / esbuild / SWC के साथ यह नाज़ुक है, इसलिए files के पार avoid करो।
Step 6 → विकल्प `const Status = { Placed: 'PLACED' } as const; type Status = (typeof Status)[keyof typeof Status];` runtime object और union type दोनों देता है, बिना किसी special emit के।

---

## 🟡 Real World Example
**Swiggy's delivery partner states** (`OFFLINE`, `AVAILABLE`, `ON_ORDER`) are stored as strings in SQL Server and sent over JSON. With a string `enum`, every API response string must be converted before it can be passed to a function expecting the enum, and a literal `'ON_ORDER'` is rejected. With an `as const` object, the same values work as plain strings everywhere, you can still write `PartnerState.OnOrder` for readability, and `Object.values(PartnerState)` gives a dropdown list. HTTP codes (`200`, `404`) are the classic numeric enum use case.

## 🟡 Real Example Hindi mein
**Swiggy के delivery partner states** (`OFFLINE`, `AVAILABLE`, `ON_ORDER`) SQL Server में strings की तरह रखे जाते हैं और JSON में भेजे जाते हैं। String `enum` के साथ, हर API response string को enum चाहिए वाले function में देने से पहले convert करना पड़ता है, और literal `'ON_ORDER'` reject हो जाता है। `as const` object के साथ वही values हर जगह सादी strings की तरह चलती हैं, पढ़ने के लिए `PartnerState.OnOrder` भी लिख सकते हो, और `Object.values(PartnerState)` से dropdown list मिल जाती है। HTTP codes (`200`, `404`) numeric enum का classic उदाहरण हैं।

---

## 💻 Code Example — Basic

```typescript
// enum-basic.ts  (TypeScript 5.x, strict)

// 1. Numeric enum: auto-increments from 0
enum Direction {
  Up,      // 0
  Down,    // 1
  Left,    // 2
  Right,   // 3
}

// 2. Numeric enum with a custom start: values continue from 200
enum HttpCode {
  Ok = 200,        // 200
  Created,         // 201
  BadRequest = 400 // 400
}

// 3. String enum: every member needs an initializer, no reverse mapping
enum OrderStatus {
  Placed = 'PLACED',
  Delivered = 'DELIVERED',
}

// 4. const enum: erased, usages are replaced by literal values
const enum Role {
  Admin = 'admin',
  Customer = 'customer',
}

const d: Direction = Direction.Left;          // typed as the enum
console.log(d, Direction[d]);                 // reverse mapping: 2 -> 'Left'
console.log(HttpCode.Created);                // 201
console.log(OrderStatus.Placed);              // 'PLACED'
console.log(Role.Admin);                      // inlined as 'admin' by the compiler

function isSuccess(code: HttpCode): boolean {
  return code >= HttpCode.Ok && code < 300;   // numeric comparison works on numeric enums
}
console.log(isSuccess(HttpCode.Created), isSuccess(HttpCode.BadRequest));
console.log(Object.keys(Direction));          // numeric enums have BOTH names and numbers as keys
console.log(Object.keys(OrderStatus));        // string enums only have names
```

Run with `npx tsx enum-basic.ts`. Real output:
```
2 Left
201
PLACED
admin
true false
[
  '0',    '1',
  '2',    '3',
  'Up',   'Down',
  'Left', 'Right'
]
[ 'Placed', 'Delivered' ]
```

## 💻 Code Example — Advanced

```typescript
// enum-advanced.ts  (TypeScript 5.x)

// ===== The modern alternative: as const object + derived union type =====
const PartnerState = {
  Offline: 'OFFLINE',
  Available: 'AVAILABLE',
  OnOrder: 'ON_ORDER',
} as const;                                                // readonly literal values

// Same name for the TYPE: union of all the values
type PartnerState = (typeof PartnerState)[keyof typeof PartnerState]; // "OFFLINE" | "AVAILABLE" | "ON_ORDER"

// Plain strings from JSON/SQL are accepted, no conversion needed
function canAssign(state: PartnerState): boolean {
  return state === PartnerState.Available;                 // compare with the readable constant
}

console.log(canAssign('AVAILABLE'));                       // plain literal works
console.log(canAssign(PartnerState.OnOrder));              // constant works too
console.log(Object.values(PartnerState));                  // runtime list for dropdowns

// ===== Exhaustive handling works on unions =====
function label(s: PartnerState): string {
  switch (s) {
    case 'OFFLINE': return 'Not working';
    case 'AVAILABLE': return 'Ready for orders';
    case 'ON_ORDER': return 'Busy';
    default: {
      const _never: never = s;                             // compile error here if a member is added but not handled
      return _never;
    }
  }
}

// ===== Enum with computed + heterogeneous members (rare, shown for interviews) =====
enum Mixed { No = 0, Yes = 'YES' }                         // heterogeneous enum: discouraged

// ===== Enum as a TYPE for a Record: every member must be a key =====
enum Plan { Free = 'free', Pro = 'pro' }
const limits: Record<Plan, number> = {                     // forgetting Plan.Pro would be an error
  [Plan.Free]: 10,
  [Plan.Pro]: 1000,
};

console.log(label('ON_ORDER'), Mixed.Yes, limits[Plan.Pro]);
```

Run with `npx tsx enum-advanced.ts`. Real output:
```
true
false
[ 'OFFLINE', 'AVAILABLE', 'ON_ORDER' ]
Busy YES 1000
```

---

## 🟠 Node/Express + React Integration

```tsx
// shared/status.ts: the alternative pattern is easiest to share with JSON APIs
export const OrderStatus = { Placed: 'PLACED', Delivered: 'DELIVERED' } as const;
export type OrderStatus = (typeof OrderStatus)[keyof typeof OrderStatus];

// server.ts  (Express + SQL Server): values arrive as plain strings from the DB
import express from 'express';
const app = express();

interface OrderRow { Id: number; Status: OrderStatus }     // mssql recordset row type

app.get('/orders/:id', (req, res) => {
  const row: OrderRow = { Id: Number(req.params.id), Status: 'PLACED' }; // no enum conversion needed
  res.json(row);
});

// With a real string enum you would need a runtime conversion at the boundary:
enum LegacyStatus { Placed = 'PLACED' }
function parseLegacy(s: string): LegacyStatus | undefined {
  return (Object.values(LegacyStatus) as string[]).includes(s) ? (s as LegacyStatus) : undefined;
}
console.log(parseLegacy('PLACED'));

// orderSlice.ts  (Redux Toolkit): enum values are fine for state
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
const slice = createSlice({
  name: 'order',
  initialState: { status: OrderStatus.Placed as OrderStatus },
  reducers: {
    changed(state, action: PayloadAction<OrderStatus>) { state.status = action.payload; },
  },
});
export const { changed } = slice.actions;

// Badge.tsx  (React): iterate the runtime object to render options
export function StatusSelect({ onPick }: { onPick: (s: OrderStatus) => void }) {
  return (
    <select onChange={(e) => onPick(e.target.value as OrderStatus)}>
      {Object.values(OrderStatus).map((s) => <option key={s} value={s}>{s}</option>)}
    </select>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing a raw string where a string enum is expected
```typescript
enum S2 { A = 'a' }
// ❌ Wrong: the literal 'a' is not an S2, even though the value is equal
const ss: S2 = 'a';
// error TS2322: Type '"a"' is not assignable to type 'S2'.
```
```typescript
enum S2 { A = 'a' }
// ✅ Right: use the member (or switch to an as const object + union)
const ss: S2 = S2.A;
```

❌ Mistake 2: Out-of-range value for a numeric enum
```typescript
enum Dir { Up, Down }
// ❌ Wrong: 99 is not a member (TS 5.0+ checks this; older versions allowed any number)
const dd: Dir = 99;
// error TS2322: Type '99' is not assignable to type 'Dir'.
```
✅ Correct: use `Dir.Up`. Note that before TS 5.0, any `number` was assignable to a numeric enum, which was a famous hole.

❌ Mistake 3: Relying on `const enum` across packages or with `isolatedModules`. Bundlers such as esbuild/Babel compile one file at a time and cannot inline a `const enum` from another file, so you get a runtime `undefined` or a build error. Prefer a regular enum or an `as const` object. Also remember `enum` is not allowed under `--erasableSyntaxOnly` (TS 5.8) and in Node's built-in TypeScript stripping.

---

## 🧠 Tricky Interview Question

```typescript
enum E { A, B, C = 10, D }
console.log(E.D, E[1], E[11], Object.keys(E).length);
```
Answer: Output is `11 B D 8`. `A=0, B=1, C=10`, and `D` continues from 10 so `D=11`. The numeric enum has a reverse mapping, so `E[1]` is `'B'` and `E[11]` is `'D'`. `Object.keys(E)` contains both directions: `'0','1','10','11','A','B','C','D'` = 8 keys. A string enum would have only 4. This is exactly why iterating a numeric enum with `Object.keys` is a classic bug.

---

## ⚫ Interview Questions + Answers

Q1: What JavaScript does a numeric enum generate?
A1: An object created by an IIFE with a two-way mapping: `E[E["A"] = 0] = "A"`. So the object holds `A -> 0` and `0 -> "A"`. String enums only generate `A -> 'a'`. This is runtime code, which is why enums are not "just types".

Q2: What is a `const enum` and what are its risks?
A2: A `const enum` emits no object; every use is replaced by the literal value at compile time, so there is zero runtime cost. Risks: you cannot iterate it or use reverse mapping, and with `isolatedModules`, Babel, esbuild or SWC cross-file usage breaks because the compiler needs whole-program knowledge. Library authors should not export them.

Q3: Why do many teams avoid enums?
A3: They emit runtime code, string enums are not assignable from plain literals (awkward with JSON), numeric enums were historically unsound (any number assignable before TS 5.0), `const enum` is fragile in single-file transpilers, and enums are not part of JavaScript so type-stripping tools and `--erasableSyntaxOnly` reject them.

Q4: What is the best alternative to an enum?
A4: An `as const` object plus a derived union: `const S = { A: 'a' } as const; type S = (typeof S)[keyof typeof S];`. It has a runtime object (iterate with `Object.values`), a union type that accepts plain strings, and no special emit. A plain string-literal union is enough when you do not need a runtime list.

Q5: How do you make sure every enum member is handled in a switch?
A5: Add a `default` branch that assigns the value to a `never` variable (`const _x: never = s`). If a member is added and not handled the compiler reports an error there. This works for enums, unions and discriminated unions alike.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Working in an existing codebase or library (Angular, NestJS and older code) that already uses enums
- You want a nominal-style type where raw strings must NOT be accepted
- Bit-flag numeric enums (`Read = 1 << 0, Write = 1 << 1`)

❌ Avoid when:
- Values arrive as JSON or SQL strings and you want them used directly (prefer `as const` or a union)
- You run with `isolatedModules`, esbuild, SWC, Babel, Node type-stripping or `--erasableSyntaxOnly` (avoid `const enum` entirely)
- You publish a library where consumers cannot be forced into your enum import

---

## 📊 Visual Diagram
```
 enum Dir { Up, Down }                      emitted JS object
 ┌───────────────┐                          ┌─────────────────────┐
 │ Up   = 0      │  ───────────────────►    │ { 0:'Up', 1:'Down', │
 │ Down = 1      │   (two-way mapping)      │   Up:0,  Down:1 }   │
 └───────────────┘                          └─────────────────────┘
 enum S { A = 'a' }   ──►  { A: 'a' }          (one-way)
 const enum           ──►  nothing emitted     (values inlined)

 Alternative:
 const S = { A:'a', B:'b' } as const;
 type S  = (typeof S)[keyof typeof S];   // 'a' | 'b'   + runtime object
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Enum | Named set of constants | नाम वाले constants का set |
| Reverse mapping | Number to name lookup `E[0]` | Number से नाम खोजना |
| String enum | Members are strings, no reverse map | String values वाला enum |
| const enum | Inlined, no runtime object | Inline हो जाने वाला enum |
| Heterogeneous enum | Mixes numbers and strings | Numbers और strings का मिश्रण |
| as const object | Literal object + derived union | Literal object और उससे बना union |
| erasableSyntaxOnly | TS 5.8 flag that forbids enums | Enums मना करने वाला TS 5.8 flag |

---

## ⚡ 3-Line Summary
English:
1. Enums emit a runtime object; numeric enums add a reverse mapping, string enums do not, `const enum` is inlined.
2. String enums reject plain string literals, and `const enum` breaks under single-file transpilers.
3. Prefer a string-literal union or an `as const` object plus `(typeof X)[keyof typeof X]` in new code.

Hindi:
1. Enums runtime object बनाते हैं; numeric enums में reverse mapping होती है, string enums में नहीं, `const enum` inline हो जाता है।
2. String enums सादी string literals reject करते हैं और `const enum` single-file transpilers में टूटता है।
3. नए code में string-literal union या `as const` object और `(typeof X)[keyof typeof X]` पसंद करो।

---

## ➡️ Next Topic
**17. const Assertions (as const)** — freezing literals and building readonly tuples and lookup tables.
