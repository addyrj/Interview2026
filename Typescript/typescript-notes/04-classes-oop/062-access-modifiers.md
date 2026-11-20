# 62. Access Modifiers (public, private, protected, #private)
# हिंदी में: Access Modifiers (public, private, protected, #private)

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। `public/private/protected` TS-only हैं (compile time, runtime पर erase); `#private` ECMAScript standard है (TS 3.8+, target ES2015+ चाहिए) और runtime पर भी enforce होता है।

---

## 🔵 Simple Definition (English)
Access modifiers control **who can use a class member**:
- `public` (default) - anywhere.
- `protected` - inside the class and its **subclasses**.
- `private` - only inside the **same class** (TypeScript check only; erased at runtime).
- `#name` (ECMAScript private field) - only inside the class, **enforced by the JS engine at runtime** too.

## 🔵 सरल परिभाषा (Hindi)
Access modifiers तय करते हैं कि **class का member कौन इस्तेमाल कर सकता है**:
- `public` (default) - कहीं भी।
- `protected` - class और उसकी **subclasses** के अंदर।
- `private` - सिर्फ **उसी class** के अंदर (सिर्फ TypeScript check; runtime पर erase)।
- `#name` (ECMAScript private field) - सिर्फ class के अंदर, और **JS engine runtime पर भी enforce** करता है।

---

## 🔴 Problem it Solves
A `Wallet` class with a public `balance` can be modified by any code: `wallet.balance = 1_000_000`. A `PaymentGateway` base class has helper methods that should be reused by subclasses (`RazorpayGateway`, `PaytmGateway`) but never called from controllers. Without modifiers, **invariants** (balance never negative, API key never logged) cannot be protected and the public surface of the class grows into an accidental API that you must support forever. Access modifiers make the intended API explicit and let the compiler guard it.

## 🔴 यह क्यों बना? (Hindi)
Public `balance` वाली `Wallet` class को कोई भी code बदल सकता है: `wallet.balance = 1_000_000`। `PaymentGateway` base class में helper methods हैं जिन्हें subclasses (`RazorpayGateway`, `PaytmGateway`) reuse करें पर controllers कभी call न करें। Modifiers के बिना **invariants** (balance कभी negative नहीं, API key कभी log नहीं) बचाए नहीं जा सकते और class की public surface अनजाने API बन जाती है जिसे हमेशा support करना पड़ता है। Access modifiers intended API साफ़ बताते हैं और compiler उसकी रक्षा करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → No modifier = `public`. Everything is reachable from outside the class.
Step 2 → `protected` members are visible in the class body **and in derived classes**, but not on instances from outside.
Step 3 → `private` members are visible **only in the declaring class** (not even subclasses). The check is **compile-time only**: `(obj as any).secret` or plain JS still reads it, and it appears in the emitted JS and in `console.log`.
Step 4 → `#field` (hash private) uses JS **private fields**: real runtime privacy, invisible to `Object.keys`, `JSON.stringify` and `console.log`; accessing it from outside is a **syntax error** even in JS. `#method()` works too.
Step 5 → Use `private` for "don't touch" in TS-only code, `#` when privacy must hold at runtime (secrets, libraries used from JS).
Step 6 → **Parameter properties**: `constructor(private readonly repo: Repo)` declares and assigns in one place (topic 66).
Step 7 → Classes with `private`/`protected`/`#` members are **nominal-like**: another class with the same public shape is **not** assignable.
Step 8 → `protected constructor` stops `new` from outside (base/abstract-like); `private constructor` + `static getInstance()` gives singleton/factory patterns.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → कोई modifier नहीं = `public`। सब कुछ class के बाहर से पहुँच में है।
Step 2 → `protected` members class body **और derived classes** में दिखते हैं, पर बाहर से instance पर नहीं।
Step 3 → `private` members **सिर्फ declare करने वाली class** में दिखते हैं (subclass में भी नहीं)। Check **सिर्फ compile time** पर है: `(obj as any).secret` या plain JS अब भी पढ़ लेते हैं, emitted JS और `console.log` में भी दिखता है।
Step 4 → `#field` (hash private) JS के **private fields** हैं: असली runtime privacy, `Object.keys`, `JSON.stringify` और `console.log` में नहीं दिखते; बाहर से access JS में भी **syntax error** है। `#method()` भी चलता है।
Step 5 → "मत छुओ" के लिए सिर्फ-TS code में `private`; जब runtime पर privacy चाहिए (secrets, JS से use होने वाली libraries) तब `#`।
Step 6 → **Parameter properties**: `constructor(private readonly repo: Repo)` एक जगह declare और assign करता है (topic 66)।
Step 7 → `private`/`protected`/`#` members वाली classes **nominal-जैसी** हो जाती हैं: वही public shape वाली दूसरी class assignable **नहीं**।
Step 8 → `protected constructor` बाहर से `new` रोकता है; `private constructor` + `static getInstance()` से singleton/factory pattern बनता है।

---

## 🟡 Real World Example
A **Paytm**-style `Wallet` keeps `#balance` private and exposes `credit()`/`debit()` that enforce "never below zero"; no code can set the balance directly. A **Razorpay**-like `BaseGateway` has `protected sign(payload)` used by `UpiGateway` and `CardGateway`, while the controller only sees `public charge(amount)`. The `apiKey` is `#apiKey`, so even `console.log(gateway)` or `JSON.stringify(gateway)` in a bug report can never leak it.

## 🟡 Real Example Hindi mein
**Paytm** जैसी `Wallet` में `#balance` private है और `credit()`/`debit()` "कभी शून्य से नीचे नहीं" enforce करते हैं; कोई code balance सीधे set नहीं कर सकता। **Razorpay** जैसी `BaseGateway` में `protected sign(payload)` है जिसे `UpiGateway` और `CardGateway` इस्तेमाल करती हैं, जबकि controller को सिर्फ `public charge(amount)` दिखता है। `apiKey` `#apiKey` है, इसलिए bug report में `console.log(gateway)` या `JSON.stringify(gateway)` भी इसे कभी leak नहीं कर सकता।

---

## 💻 Code Example — Basic

```typescript
class Wallet {
  public owner: string; // public: anyone can read/write (explicit, same as no modifier)
  protected currency = "INR"; // protected: this class + subclasses
  private balancePaise = 0; // private: this class only (TS check)
  #pin: string; // #private: this class only (TS check + runtime privacy)

  constructor(owner: string, pin: string) {
    this.owner = owner; // assign public
    this.#pin = pin; // assign hash-private
  }

  credit(paise: number): void {
    this.balancePaise += paise; // allowed: inside the class
  }

  get balance(): number {
    return this.balancePaise / 100; // controlled read access, in rupees
  }

  verify(pin: string): boolean {
    return this.#pin === pin; // allowed: inside the class
  }
}

const w = new Wallet("Riya", "4321"); // create wallet
w.credit(50000); // OK: public method
console.log(w.owner, w.balance, w.verify("4321")); // Riya 500 true

// ❌ Reading a private member from outside
console.log(w.balancePaise);
// error TS2341: Property 'balancePaise' is private and only accessible within class 'Wallet'.

// ❌ Reading a protected member from outside
console.log(w.currency);
// error TS2445: Property 'currency' is protected and only accessible within class 'Wallet' and its subclasses.

// ❌ Reading a #private field from outside
console.log(w.#pin);
// error TS18013: Property '#pin' is not accessible outside class 'Wallet' because it has a private identifier.
```

## 💻 Code Example — Advanced

```typescript
// protected: shared with subclasses, hidden from consumers
abstract class BaseGateway {
  protected constructor(protected readonly name: string) {} // protected ctor: only subclasses can call super(...)
  protected sign(payload: string): string { return `${this.name}:sig(${payload.length})`; } // helper for subclasses
  abstract charge(amountPaise: number): string; // public API
}
class UpiGateway extends BaseGateway {
  constructor() { super("upi"); } // allowed: we are a subclass
  charge(amountPaise: number): string { return this.sign(`pay:${amountPaise}`); } // sign is protected, usable here
}
const upi = new UpiGateway(); // public constructor of the subclass
console.log(upi.charge(49900)); // upi:sig(9)

// ❌ Cannot call protected helper from outside
upi.sign("x");
// error TS2445: Property 'sign' is protected and only accessible within class 'BaseGateway' and its subclasses.

// ❌ Cannot instantiate the base with a protected/abstract constructor
new BaseGateway("x");
// error TS2674: Constructor of class 'BaseGateway' is protected and only accessible within the class declaration.

// private is TS-only: still visible at runtime
class Secret {
  private tsPrivate = "visible-at-runtime"; // TS private
  #jsPrivate = "truly-hidden"; // JS private
  hasJs(): boolean { return this.#jsPrivate.length > 0; } // use it so it is not "unused"
}
const s = new Secret(); // instance
console.log(JSON.stringify(s)); // {"tsPrivate":"visible-at-runtime"}   <- #jsPrivate is NOT there
console.log((s as unknown as { tsPrivate: string }).tsPrivate); // visible-at-runtime  (private is erased)
console.log(s.hasJs()); // true

// Nominal-like typing: same public shape is not enough when private members exist
class UserId { private brand = "u"; constructor(public value: string) {} } // has a private member
class OrderId { private brand = "o"; constructor(public value: string) {} } // same shape, different class
const uid: UserId = new UserId("1"); // OK
// ❌ Different class with a private member is not assignable
const oid: OrderId = uid;
// error TS2322: Type 'UserId' is not assignable to type 'OrderId'.
//   Types have separate declarations of a private property 'brand'.

// Private constructor + static factory (singleton)
class Config {
  private static instance?: Config; // holds the single instance
  private constructor(readonly env: string) {} // nobody can call `new Config()` outside
  static get(): Config { return (Config.instance ??= new Config("production")); } // lazy singleton
}
console.log(Config.get() === Config.get()); // true
// ❌ Constructor is private
new Config("dev");
// error TS2673: Constructor of class 'Config' is private and only accessible within the class declaration.

// Private static + #private methods
class Counter {
  static #count = 0; // private static
  #bump(): number { return ++Counter.#count; } // private method
  next(): number { return this.#bump(); } // public wrapper
}
console.log(new Counter().next(), new Counter().next()); // 1 2
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Service whose internals are private; controller sees only the public API
class OrderService {
  readonly #orders = new Map<string, { id: string; amount: number }>(); // hidden store
  private audit(msg: string): void { console.log(`[audit] ${msg}`); } // internal helper

  create(id: string, amount: number): { id: string; amount: number } {
    const order = { id, amount }; // new order
    this.#orders.set(id, order); // store it
    this.audit(`created ${id}`); // internal logging
    return order; // return plain object
  }
}

const service = new OrderService(); // one instance
const app = express(); // create app
app.use(express.json()); // parse JSON
app.post("/orders", (req, res) => {
  const { id, amount } = req.body as { id: string; amount: number }; // trust-but-validate in real code
  res.status(201).json(service.create(id, amount)); // only public API is callable
});
// service.audit("x");  // would be TS2341 - the controller cannot reach it
```

```tsx
import { Component, type ReactNode } from "react";

// Class component: keep helpers private, lifecycle/render public
interface Props { amount: number } // props type
export class PayTimer extends Component<Props, { secs: number }> {
  state = { secs: 0 }; // initial state
  #id?: ReturnType<typeof setInterval>; // hash-private timer handle

  private tick = (): void => this.setState((s) => ({ secs: s.secs + 1 })); // internal handler

  componentDidMount(): void { this.#id = setInterval(this.tick, 1000); } // start timer
  componentWillUnmount(): void { clearInterval(this.#id); } // clean up
  render(): ReactNode { return <span>₹{this.props.amount} - {this.state.secs}s</span>; } // public render
}
```

```typescript
// Redux: serialisable state must be plain objects. Keep classes with #private OUT of the store.
class Money {
  #paise: number; // hidden
  constructor(paise: number) { this.#paise = paise; } // set
  toJSON(): { paise: number } { return { paise: this.#paise }; } // explicit serialisation
}
console.log(JSON.stringify(new Money(500))); // {"paise":500}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting `private` for security
```typescript
class Vault {
  private apiKey = "sk_live_123"; // TS private only
}
const v = new Vault();
console.log(JSON.stringify(v)); // {"apiKey":"sk_live_123"}  <- leaks in logs / responses!
// Right: use #apiKey (not serialised) or keep secrets out of objects entirely
class SafeVault { #apiKey = "sk_live_123"; has(): boolean { return this.#apiKey.length > 0; } }
console.log(JSON.stringify(new SafeVault())); // {}
```

❌ Mistake 2: Making a member `private` and then needing it in a subclass
```typescript
class Base { private secret = 1; }
class Child extends Base {
  read(): number { return this.secret; } // ❌ subclass cannot see private
}
// error TS2341: Property 'secret' is private and only accessible within class 'Base'.
// Right: declare it `protected secret = 1;`
```

❌ Mistake 3: Using `#private` with a target below ES2015
```typescript
// tsconfig target: "ES5"  ->  error TS18028: Private identifiers are only available when targeting ECMAScript 2015 and higher.  (verified with tsc --target ES5)
```
✅ Correct: use `target: ES2022` (modern Node 18+/browsers), or fall back to TS `private`.

❌ Mistake 4: Testing private members through `as any` everywhere
✅ Correct: test through the public API; if a private method needs its own test it probably deserves to be its own class/function.

---

## 🧠 Tricky Interview Question

```typescript
class A { private x = 1; equals(o: A): boolean { return this.x === o.x; } }
class B { private x = 1; equals(_o: A): boolean { return true; } }
const a: A = new B(); // (1) ❌
const a2 = new A(); a2.equals(new A()); // (2)
```
**Answer:** (1) is an **error**: `B` is not assignable to `A` because they declare **separate** private `x` properties. (2) **compiles** - **inside** the class `A`, `o.x` is accessible on **other instances** of `A` (privacy is per-class, not per-instance, in both TS and JS `#`).
```typescript
class A2 { private x = 1; }
class B2 { private x = 1; }
const a: A2 = new B2(); // ❌ same public shape, separate private declarations
// error TS2322: Type 'B2' is not assignable to type 'A2'.
//   Types have separate declarations of a private property 'x'.
```

---

## ⚫ Interview Questions + Answers

Q1: `private` vs `#private` - what is the difference?
A1: `private` is a TypeScript compile-time check only; the property exists at runtime and shows up in `Object.keys`, `JSON.stringify` and `console.log`. `#x` is a real ECMAScript private field: not visible to reflection, accessing it from outside is a syntax error even in JS, and it survives `as any`. `#` needs target ES2015+, and has a small perf/transpile cost on old targets. Use `#` for secrets and library internals.

Q2: How does `protected` differ from `private` in inheritance?
A2: `private` members are visible only in the declaring class; subclasses cannot access them. `protected` members are visible in the class and every subclass (accessed via `this` or an instance of the subclass), but not from unrelated code. Use `protected` for template-method hooks and shared helpers.

Q3: Can two classes with identical public shapes be assigned to each other?
A3: Without private/protected members, yes (structural typing). If either declares a `private`/`protected`/`#` member, types are compatible only if the member comes from the **same declaration** (the same class or its subclass). This is a cheap way to get nominal typing for classes.

Q4: How do you implement a singleton or restrict instantiation?
A4: Make the constructor `private` and expose a `static getInstance()`; or `protected constructor` for classes that should only be extended. TS reports `TS2673` / `TS2674` when code outside tries `new`. Note it is TS-only; JS callers can still call `new` unless you also use `#`/closure tricks.

Q5: Are TS access modifiers enforced at runtime?
A5: No for `public/private/protected` - they are erased at compile time, so plain JS, `any` casts, and reflection ignore them. Only `#fields`/`#methods` give runtime enforcement. This is why secrets should use `#` (or closures), and why DTOs sent over the wire never contain TS-private "protection".

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Protecting invariants (`balance`, state machines) behind public methods
- Sharing helpers with subclasses only (`protected`)
- Hiding secrets/tokens from serialisation and logs (`#field`)
- Restricting instantiation (`private constructor`) for singletons/factories

❌ Avoid when:
- A plain data object/DTO is enough - modifiers add nothing to interfaces and JSON
- You need to store the object in Redux/React state (non-serialisable, hidden state)
- You are over-hiding: tests and extension become painful; prefer small public API + composition

---

## 📊 Visual Diagram
```
                       same class   subclass   outside   runtime-enforced
  public   (default)      ✅           ✅         ✅          -
  protected               ✅           ✅         ❌          ❌ (TS only)
  private                 ✅           ❌         ❌          ❌ (TS only)
  #private                ✅           ❌         ❌          ✅ (JS engine)

  class Wallet {
    public  owner      ──► visible everywhere
    protected currency ──► Wallet + UpiWallet extends Wallet
    private balance    ──► Wallet only (but still in JSON.stringify!)
    #pin               ──► Wallet only (not in JSON, not via `as any`)
  }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| public | Visible everywhere (default) | हर जगह दिखता है |
| protected | Class + subclasses only | class और subclasses तक |
| private | Declaring class only, TS check | सिर्फ declaring class, TS check |
| `#private` | JS runtime-private field | JS का runtime-private field |
| Nominal-like typing | Same declaration required for compatibility | compatibility के लिए same declaration |
| Singleton | One shared instance | एक ही shared instance |

---

## ⚡ 3-Line Summary
English:
1. `public` is default, `protected` shares with subclasses, `private` is a TS-only wall, `#private` is a real runtime wall.
2. Private/protected/# members make classes nominal-like and protect invariants like `balance`.
3. Never rely on TS `private` for secrets; use `#` and keep secrets out of serialised objects.

Hindi:
1. `public` default है, `protected` subclasses से share करता है, `private` सिर्फ TS की दीवार है, `#private` असली runtime दीवार है।
2. Private/protected/# members classes को nominal-जैसा बनाते हैं और `balance` जैसे invariants बचाते हैं।
3. Secrets के लिए TS `private` पर भरोसा मत करो; `#` इस्तेमाल करो और secrets को serialise होने वाले objects से दूर रखो।

---

## ➡️ Next Topic
**63. readonly and static Members** — immutable fields, shared class-level state and static factories.
