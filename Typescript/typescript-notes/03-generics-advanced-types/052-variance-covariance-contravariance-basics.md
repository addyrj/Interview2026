# 52. Variance (covariance / contravariance) Basics
# हिंदी में: Variance (covariance / contravariance) की बुनियाद

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). `strictFunctionTypes` TS 2.6 से (`strict` में शामिल); `in` / `out` variance annotations TS 4.7 से।

---

## 🔵 Simple Definition (English)
**Variance** describes how subtyping of a generic type relates to subtyping of its type argument. If `Dog` is a subtype of `Animal`: **covariant** means `Box<Dog>` is assignable to `Box<Animal>` (same direction, typical for outputs/readers); **contravariant** means `Handler<Animal>` is assignable to `Handler<Dog>` (reversed, typical for inputs/consumers); **invariant** means neither direction works (read and write); **bivariant** means both work (unsound, TypeScript allows it for method parameters and, for arrays, writes).

## 🔵 सरल परिभाषा (Hindi)
**Variance** बताता है कि generic type का subtyping उसके type argument के subtyping से कैसे जुड़ा है। मान लो `Dog`, `Animal` का subtype है: **covariant** यानी `Box<Dog>`, `Box<Animal>` में assign हो सकता है (वही दिशा, outputs/readers के लिए); **contravariant** यानी `Handler<Animal>`, `Handler<Dog>` में assign हो सकता है (उल्टी दिशा, inputs/consumers के लिए); **invariant** यानी कोई दिशा नहीं चलती (read और write दोनों); **bivariant** यानी दोनों चलती हैं (unsound, TypeScript method parameters में allow करता है)।

---

## 🔴 Problem it Solves
Understanding variance explains confusing errors: why can I pass `string[]` where `(string | number)[]` is expected but not a `(x: string) => void` callback where `(x: string | number) => void` is expected? It also prevents runtime bugs: a Redux `Dispatch<Action>` accepting only `AddToCart` must not be used where any `Action` can be dispatched. Without variance rules, code that compiles could crash at runtime.

## 🔴 यह क्यों बना? (Hindi)
Variance समझने से confusing errors का कारण पता चलता है: मैं `string[]` को `(string | number)[]` की जगह दे सकता हूँ, पर `(x: string) => void` callback को `(x: string | number) => void` की जगह क्यों नहीं? यह runtime bugs भी रोकता है: जो Redux `Dispatch<Action>` सिर्फ `AddToCart` लेता है, उसे वहाँ नहीं देना चाहिए जहाँ कोई भी `Action` dispatch हो सकता है। Variance rules के बिना compile होने वाला code runtime पर crash कर सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Subtype: `Dog` is assignable to `Animal` (Dog has everything Animal has, plus more).
Step 2 → **Covariant (out)**: a type that only **produces** T: `() => T`, `ReadonlyArray<T>`, `Promise<T>`, properties you only read. `Producer<Dog>` can go where `Producer<Animal>` is expected.
Step 3 → **Contravariant (in)**: a type that only **consumes** T: `(x: T) => void`. A function that accepts any `Animal` can safely handle a `Dog`, so `(a: Animal) => void` is assignable to `(d: Dog) => void`. Only under `strictFunctionTypes`.
Step 4 → **Invariant**: both reads and writes of T: `{ get(): T; set(v: T): void }` as property functions. Neither direction is safe.
Step 5 → TypeScript quirks: **method shorthand** parameters (`set(v: T): void`) stay bivariant even under strict; plain arrays `T[]` are treated covariantly even though `push` writes (unsound by design, for practicality).
Step 6 → Annotations (TS 4.7+): `interface Producer<out T>`, `interface Consumer<in T>`, `interface Both<in out T>`. The compiler checks your annotation and uses it to speed up comparisons.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Subtype: `Dog`, `Animal` को assignable है (Dog में Animal का सब कुछ और उससे ज़्यादा है)।
Step 2 → **Covariant (out)**: जो type सिर्फ T **produce** करता है: `() => T`, `ReadonlyArray<T>`, `Promise<T>`। `Producer<Dog>`, `Producer<Animal>` की जगह जा सकता है।
Step 3 → **Contravariant (in)**: जो सिर्फ T **consume** करता है: `(x: T) => void`। जो function कोई भी `Animal` ले सकता है वह `Dog` भी सँभाल लेगा, इसलिए `(a: Animal) => void`, `(d: Dog) => void` को assignable है। सिर्फ `strictFunctionTypes` में।
Step 4 → **Invariant**: T को read और write दोनों। कोई दिशा safe नहीं।
Step 5 → TypeScript के quirks: **method shorthand** के parameters strict में भी bivariant रहते हैं; `T[]` को covariant माना जाता है, भले ही `push` लिखता है (जानबूझकर unsound)।
Step 6 → Annotations (TS 4.7+): `out T`, `in T`, `in out T`।

---

## 🟡 Real World Example
**Razorpay's** SDK has `EventHandler<E>`. A generic logger handler `(e: PaymentEvent) => void` is safe to register as the handler for the narrower `payment.captured` event, because it accepts every payment event (contravariance). But a handler written only for `Captured` must NOT be registered for all payment events: it would receive a `Failed` event and read a missing field. In Redux, `Dispatch<AnyAction>` vs `Dispatch<AddToCart>` follows the same logic.

## 🟡 Real Example Hindi mein
**Razorpay** के SDK में `EventHandler<E>` है। Generic logger handler `(e: PaymentEvent) => void` को narrow `payment.captured` event का handler बनाना safe है, क्योंकि वह हर payment event ले सकता है (contravariance)। लेकिन सिर्फ `Captured` के लिए लिखा handler सभी payment events पर register नहीं होना चाहिए: उसे `Failed` event मिलेगा और वह ग़ायब field पढ़ेगा। Redux में `Dispatch<AnyAction>` बनाम `Dispatch<AddToCart>` में भी यही तर्क है।

---

## 💻 Code Example — Basic

```typescript
// Subtype relation: Dog extends Animal
interface Animal { name: string }
interface Dog extends Animal { breed: string }

const dog: Dog = { name: "Tommy", breed: "Lab" };
const animal: Animal = dog; // OK: Dog is assignable to Animal

// COVARIANCE: producers keep the direction
type Producer<T> = () => T;
const makeDog: Producer<Dog> = () => dog;
const makeAnimal: Producer<Animal> = makeDog; // OK: covariant (returns a Dog, caller expects Animal)

// CONTRAVARIANCE: consumers reverse the direction (needs strictFunctionTypes, part of strict)
type Consumer<T> = (x: T) => void;
const feedAnimal: Consumer<Animal> = (a) => console.log("feeding", a.name); // accepts any Animal
const feedDog: Consumer<Dog> = feedAnimal; // OK: a handler for Animals can handle Dogs
feedDog(dog); // feeding Tommy

// Read-only arrays are covariant
const dogs: readonly Dog[] = [dog];
const animals: readonly Animal[] = dogs; // OK: reading Animals from Dogs is safe
console.log(animals.length, makeAnimal().name); // 1 Tommy
```

```typescript
// The same relationships in the WRONG direction are compile errors
interface Animal { name: string }
interface Dog extends Animal { breed: string }

type Consumer<T> = (x: T) => void;
const feedDogOnly: Consumer<Dog> = (d) => console.log(d.breed); // reads breed
const feedAnyAnimal: Consumer<Animal> = feedDogOnly; // ❌
// error TS2322: Type 'Consumer<Dog>' is not assignable to type 'Consumer<Animal>'.
//   Property 'breed' is missing in type 'Animal' but required in type 'Dog'.
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: explicit variance annotations (TS 4.7+) document and enforce intent
interface Animal { name: string }
interface Dog extends Animal { breed: string }

interface Reader<out T> { get(): T } // T only appears in output positions: covariant
interface Writer<in T> { set(value: T): void } // T only in input positions: contravariant
interface Cell<in out T> { get(): T; set(value: T): void } // both: invariant

const dogReader: Reader<Dog> = { get: () => ({ name: "Tommy", breed: "Lab" }) }; // real value
const animalReader: Reader<Animal> = dogReader; // OK covariant

const animalWriter: Writer<Animal> = { set: (v) => console.log("set", v.name) }; // real value
const dogWriter: Writer<Dog> = animalWriter; // OK contravariant

const dogCell: Cell<Dog> = { get: () => ({ name: "Rex", breed: "Pug" }), set: () => {} }; // real value
// const animalCell: Cell<Animal> = dogCell; // would be an error: invariant

// Advanced 2: array covariance is unsound but allowed
const dogsArr: Dog[] = [{ name: "Tommy", breed: "Lab" }];
const animalsArr: Animal[] = dogsArr; // compiles! (T[] is treated covariantly)
animalsArr.push({ name: "Cat" }); // compiles, but now dogsArr contains a non-Dog
console.log(dogsArr[1]?.name); // Cat (a Dog-typed array holds a plain Animal: runtime hole)

// Advanced 3: method shorthand is bivariant even with strictFunctionTypes
interface BivariantHandler { handle(a: Animal): void } // method syntax: bivariant
interface StrictHandler { handle: (a: Animal) => void } // property syntax: contravariant

const dogOnly = { handle(d: Dog) { console.log(d.breed.toUpperCase()); } };
const bi: BivariantHandler = dogOnly; // compiles (unsound!) because methods are bivariant
// const st: StrictHandler = dogOnly; // would be an error under strictFunctionTypes
console.log(typeof bi.handle, dogCell.get().name, animalReader.get().name); // function Rex Tommy
dogWriter.set({ name: "Bruno", breed: "Lab" }); // set Bruno
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: middleware handlers are contravariant in the request they accept
import express, { type Request, type Response } from "express";

interface AuthedRequest extends Request {
  userId?: string; // set by an auth middleware
}

// A handler accepting plain Request can be used where AuthedRequest is expected (contravariance)
const logRequest = (req: Request, _res: Response) => { console.log(req.method); };
const needsAuthed: (req: AuthedRequest, res: Response) => void = logRequest; // OK

const app = express();
app.get("/me", (req: AuthedRequest, res) => { res.json({ id: req.userId ?? null }); });
```

```tsx
// React: callback props are contravariant: a handler for a wider event fits a narrower slot
import type { ChangeEvent, SyntheticEvent } from "react";

// Handler declared for the base event type
const trackAny = (e: SyntheticEvent) => { console.log(e.type); };

export function SearchBox() {
  // onChange expects (e: ChangeEvent<HTMLInputElement>) => void; trackAny accepts a wider type: OK
  const onChange: (e: ChangeEvent<HTMLInputElement>) => void = trackAny;
  return <input onChange={onChange} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming `Dog[]` is safely assignable to `Animal[]`
```typescript
interface Animal { name: string }
interface Dog extends Animal { breed: string }
const dogs: Dog[] = [];
const animals: Animal[] = dogs; // compiles (array covariance is unsound)
animals.push({ name: "Cat" }); // runtime bug: dogs now contains a Cat
// ✅ Right: use readonly Animal[] when you only read
const safe: readonly Animal[] = dogs;
```

❌ Mistake 2: Wrong direction for callback parameters
```typescript
// ❌ Wrong
interface Animal { name: string }
interface Dog extends Animal { breed: string }
declare function onDog(cb: (d: Dog) => void): void;
declare const needsAnimal: (a: Animal) => void;
declare function onAnimal(cb: (a: Animal) => void): void;
declare const needsDog: (d: Dog) => void;
onAnimal(needsDog);
// error TS2345: Argument of type '(d: Dog) => void' is not assignable to parameter of type '(a: Animal) => void'.
//   Types of parameters 'd' and 'a' are incompatible.
//     Property 'breed' is missing in type 'Animal' but required in type 'Dog'.
```

❌ Mistake 3: Variance annotation that lies
```typescript
// ❌ Wrong: T is used in an input position but declared `out`
interface Bad<out T> { set: (v: T) => void } // property syntax, so it is checked strictly
// error TS2636: Type 'Bad<sub-T>' is not assignable to type 'Bad<super-T>' as implied by variance annotation.
```

---

## 🧠 Tricky Interview Question

```typescript
interface Animal { name: string }
interface Dog extends Animal { breed: string }

let a: (x: Dog) => void = (x: Animal) => {};
let b: (x: Animal) => void = (x: Dog) => {}; // ❌
```
**Which line fails under `--strict`, and which compiles without `strictFunctionTypes`?**

Answer: Line `a` compiles (a function accepting `Animal` can accept `Dog`: contravariant OK). Line `b` fails: `Type '(x: Dog) => void' is not assignable to type '(x: Animal) => void'`. Without `strictFunctionTypes` (i.e. `strict: false`) both compile because function parameters are bivariant. Method shorthand declarations remain bivariant even with the flag, which is why `handle(a: Animal): void` interface members behave differently from `handle: (a: Animal) => void` properties.

---

## ⚫ Interview Questions + Answers

Q1: Explain covariance and contravariance with an example.
A1: Covariant: `Promise<Dog>` fits `Promise<Animal>` (output). Contravariant: `(a: Animal) => void` fits `(d: Dog) => void` (input), because the function handles more than needed. Rule of thumb: producing (out) is covariant, consuming (in) is contravariant, doing both is invariant.

Q2: What does `strictFunctionTypes` do?
A2: It makes function type parameters contravariant (checked strictly) for function type literals and properties. Methods declared with method shorthand, constructors and some callbacks in lib.d.ts stay bivariant for compatibility.

Q3: Why is `T[]` covariant if `push` writes T?
A3: A deliberate unsound trade-off for usability; making arrays invariant would break very common code. Use `readonly T[]` for guaranteed-safe covariance.

Q4: What do `in` and `out` annotations on type parameters do?
A4: TS 4.7+ lets you declare intended variance. The compiler verifies it against the structure (TS2636 if you lie) and uses it for faster type comparisons of deep generic types.

Q5: How does variance matter in React/Redux typing?
A5: Callback props (`onChange`, `Dispatch`) are contravariant in their argument, so a handler for a wider type can be passed to a narrower slot. For Redux `Dispatch`, a function accepting a union of actions can be used where a narrower action is dispatched, not the reverse. Mixing these up gives the "Types of parameters are incompatible" errors.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging "Types of parameters are incompatible" errors
- Designing library generics (event emitters, stores, repositories); add `in`/`out`
- Choosing `readonly T[]` for safe covariant inputs

❌ Avoid when:
- Fine-grained annotations in ordinary application code; they add noise
- Relying on bivariance (method shorthand) for safety; it is a known hole

---

## 📊 Visual Diagram
```
   Dog  ──is-a──►  Animal           (Dog is the subtype)

   COVARIANT (out)       Producer<Dog>  ─────►  Producer<Animal>     same direction
   CONTRAVARIANT (in)    Consumer<Animal> ───►  Consumer<Dog>        reversed
   INVARIANT (in out)    Cell<Dog>  ✗ Cell<Animal>   neither
   BIVARIANT             method params, T[] writes   (unsound, allowed)

   Rule:  T read-only  → out     T write-only → in     both → in out
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Covariant | Same direction as T | T जैसी ही दिशा |
| Contravariant | Opposite direction | उल्टी दिशा |
| Invariant | Exact match only | सिर्फ exact match |
| Bivariant | Both accepted (unsound) | दोनों दिशाएँ (unsound) |
| strictFunctionTypes | Strict parameter checks | Parameters की सख़्त जाँच |
| `in` / `out` | Variance annotations | Variance की घोषणा (TS 4.7+) |

---

## ⚡ 3-Line Summary
English:
1. Covariant = produces T (same direction), contravariant = consumes T (reversed), invariant = both.
2. `strictFunctionTypes` enforces contravariant parameters, but method shorthand and `T[]` stay loose.
3. Use `readonly T[]` and `in`/`out` (TS 4.7+) to make safe intent explicit.

Hindi:
1. Covariant = T produce करता है (वही दिशा), contravariant = T consume करता है (उल्टी), invariant = दोनों।
2. `strictFunctionTypes` parameters को contravariant बनाता है, पर method shorthand और `T[]` ढीले रहते हैं।
3. सुरक्षित मंशा साफ़ करने के लिए `readonly T[]` और `in`/`out` (TS 4.7+) इस्तेमाल करो।

---

## ➡️ Next Topic
**53. Utility Types — Partial, Required, Readonly** — built-in mapped types जो हर रोज़ patch/update payloads में काम आते हैं।
