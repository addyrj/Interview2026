# 111. Typed Dependency Injection Container
# हिंदी में: Typed Dependency Injection Container (type-safe dependency देने वाला container)

> TypeScript 5.x | `tsc --strict` पर verify किया गया (TS 5.9). `const` type parameter (`getAll<const Ts>`) = **TS 5.0+**.

---

## 🔵 Simple Definition (English)
A **Dependency Injection (DI) container** is an object that knows *how to build* your services (database, payment gateway, logger) and hands them to whoever asks. A **typed** container goes one step further: the compiler knows exactly which keys are registered and what type each key returns, so `container.resolve('gateway')` is a `Gateway`, and `container.resolve('gatewey')` (typo) is a compile error, not a 3 AM production crash.

## 🔵 सरल परिभाषा (Hindi)
**Dependency Injection (DI) container** एक ऐसा object है जिसे पता होता है कि आपकी services (database, payment gateway, logger) *कैसे बनानी हैं*, और जो माँगता है उसे दे देता है। **Typed** container में compiler को पता होता है कि कौन-से keys register हैं और हर key किस type की value देती है। इसलिए `container.resolve('gateway')` का type `Gateway` होता है, और typo वाला `resolve('gatewey')` **compile time** पर ही पकड़ा जाता है, रात 3 बजे production में नहीं।

---

## 🔴 Problem it Solves
Without DI, a class creates its own dependencies: `new RazorpayClient()` inside `OrderService`. Now you cannot unit-test it without hitting the real Razorpay, you cannot swap SQL Server for an in-memory fake, and every change in a constructor ripples through the whole codebase. An *untyped* container (`container.get('db') as any`) fixes testability but loses safety: wrong key, wrong type, wrong registration order all explode at runtime. In interviews this question tests whether you can encode a **registry in the type system** (type-state, generics, mapped tuples).

## 🔴 यह क्यों बना? (Hindi)
DI के बिना class अपनी dependencies खुद बनाती है: `OrderService` के अंदर `new RazorpayClient()`। तब आप real Razorpay को hit किए बिना unit test नहीं कर सकते, SQL Server की जगह in-memory fake नहीं लगा सकते, और constructor बदलते ही पूरे codebase में बदलाव फैलता है। *Untyped* container (`container.get('db') as any`) testability तो देता है पर safety खो देता है: गलत key, गलत type, गलत registration order, सब runtime पर फटते हैं। Interview में यह सवाल देखने के लिए पूछा जाता है कि क्या आप **registry को type system में encode** कर सकते हैं (type-state, generics, mapped tuples)।

---

## 🟢 How it Works — Step by Step
Step 1 → Define small interfaces (`Db`, `Gateway`), never concrete classes, as the contract.
Step 2 → `register(key, factory)` stores the factory in a `Map` at runtime AND returns a container whose **type** now includes `Record<K, V>` (key `K` literal, value `V` inferred from the factory).
Step 3 → Chained `register` calls accumulate the type: `Container<{} & Record<'db', Db> & Record<'gateway', Gateway>>`.
Step 4 → `resolve<K extends keyof TReg>(key: K): TReg[K]` only accepts registered keys and returns the right type (indexed access type).
Step 5 → Runtime: lazily call the factory, cache the result (singleton) or skip the cache (transient).
Step 6 → For classes/interfaces without a string key, use a **Token&lt;T&gt;** (phantom type) so the key itself carries the type.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → छोटे interfaces (`Db`, `Gateway`) बनाओ, concrete classes नहीं, यही contract है।
Step 2 → `register(key, factory)` runtime पर factory को `Map` में रखता है और **type** में `Record<K, V>` जोड़कर नया container type return करता है (key `K` literal रहता है, `V` factory से infer होता है)।
Step 3 → chain में हर `register` type को जमा करता जाता है: `Container<{} & Record<'db', Db> & Record<'gateway', Gateway>>`।
Step 4 → `resolve<K extends keyof TReg>(key: K): TReg[K]` सिर्फ registered keys लेता है और सही type लौटाता है (indexed access type)।
Step 5 → Runtime पर factory lazily चलती है; result cache हो तो singleton, cache न हो तो transient।
Step 6 → जहाँ string key नहीं चाहिए, वहाँ **Token&lt;T&gt;** (phantom type) इस्तेमाल करो ताकि key खुद type साथ ले चले।

---

## 🟡 Real World Example
**Swiggy's order service** needs a `PaymentGateway`, an `OrderRepo` (SQL Server) and a `Notifier` (SMS/push). In production these are Razorpay, `mssql` and Firebase. In a CI test they are three tiny fakes. The *composition root* (one file near `main.ts`) is the only place that knows the real classes; everything else asks the container, and TypeScript guarantees nobody asks for something that was never wired.

## 🟡 Real Example Hindi mein
**Swiggy की order service** को एक `PaymentGateway`, एक `OrderRepo` (SQL Server) और एक `Notifier` (SMS/push) चाहिए। Production में ये Razorpay, `mssql` और Firebase हैं; CI test में तीन छोटे fakes। *Composition root* (`main.ts` के पास की एक file) अकेली जगह है जो real classes जानती है; बाकी सब container से माँगते हैं, और TypeScript गारंटी देता है कि कोई ऐसी चीज़ न माँगे जो wire ही नहीं हुई।

---

## 💻 Code Example — Basic

```typescript
// Container jo registered keys ko apne TYPE me yaad rakhta hai
class Container<TReg extends object = {}> {
  private factories = new Map<PropertyKey, () => unknown>(); // key -> factory
  private cache = new Map<PropertyKey, unknown>(); // singleton cache

  register<K extends string, V>(
    key: K, // naya key, literal type ban jaata hai
    factory: (c: Container<TReg>) => V, // factory purane container ko dekh sakti hai
  ): Container<TReg & Record<K, V>> { // return type me naya key add ho gaya
    this.factories.set(key, () => factory(this));
    return this as unknown as Container<TReg & Record<K, V>>; // runtime me same object
  }

  resolve<K extends keyof TReg>(key: K): TReg[K] { // sirf registered key allowed
    if (!this.cache.has(key)) {
      const f = this.factories.get(key);
      if (!f) throw new Error(`Not registered: ${String(key)}`);
      this.cache.set(key, f()); // pehli baar banao, phir cache
    }
    return this.cache.get(key) as TReg[K];
  }
}

interface Db { query(sql: string): string[] }
interface Gateway { charge(paise: number): string }

const container = new Container()
  .register('db', (): Db => ({ query: (sql) => [`rows for: ${sql}`] }))
  .register('gateway', (): Gateway => ({ charge: (p) => `razorpay_${p}` }))
  .register('orders', (c) => ({
    place(amountPaise: number) {
      const id = c.resolve('gateway').charge(amountPaise); // 'gateway' ka type pata hai
      return { id, rows: c.resolve('db').query('SELECT 1') };
    },
  }));

console.log(container.resolve('orders').place(49900));
console.log(container.resolve('orders') === container.resolve('orders'));
// OUTPUT:
// { id: 'razorpay_49900', rows: [ 'rows for: SELECT 1' ] }
// true
```

## 💻 Code Example — Advanced

```typescript
// Token-based injector: lifetimes + cycle detection + tuple resolve
class Token<T> {
  declare readonly _phantom: T; // sirf type ke liye, runtime pe exist nahi karta
  constructor(readonly name: string) {}
}
type TokenValue<T> = T extends Token<infer V> ? V : never; // Token se value type nikalo
type Lifetime = 'singleton' | 'transient';

class Injector {
  private bindings = new Map<Token<any>, { make: (i: Injector) => unknown; life: Lifetime }>();
  private singletons = new Map<Token<any>, unknown>();
  private resolving: string[] = []; // cycle detect karne ke liye stack

  bind<T>(token: Token<T>, make: (i: Injector) => T, life: Lifetime = 'singleton'): this {
    this.bindings.set(token, { make, life });
    return this;
  }

  get<T>(token: Token<T>): T {
    const b = this.bindings.get(token);
    if (!b) throw new Error(`No binding for ${token.name}`);
    if (b.life === 'singleton' && this.singletons.has(token)) return this.singletons.get(token) as T;
    if (this.resolving.includes(token.name)) {
      throw new Error(`Cycle: ${[...this.resolving, token.name].join(' -> ')}`);
    }
    this.resolving.push(token.name);
    try {
      const value = b.make(this) as T;
      if (b.life === 'singleton') this.singletons.set(token, value);
      return value;
    } finally {
      this.resolving.pop();
    }
  }

  // tuple-in, tuple-out: har token ka sahi type milta hai
  getAll<const Ts extends readonly Token<any>[]>(...tokens: Ts): { [I in keyof Ts]: TokenValue<Ts[I]> } {
    return tokens.map((t) => this.get(t)) as any;
  }
}

interface Logger { log(m: string): void }
interface Mailer { send(to: string, body: string): void }
const LOGGER = new Token<Logger>('Logger');
const MAILER = new Token<Mailer>('Mailer');
const REQ_ID = new Token<number>('RequestId');

let counter = 0;
const inj = new Injector()
  .bind(LOGGER, () => ({ log: (m) => console.log('[log]', m) }))
  .bind(MAILER, (i) => ({ send: (to, body) => i.get(LOGGER).log(`mail to ${to}: ${body}`) }))
  .bind(REQ_ID, () => ++counter, 'transient'); // har get pe naya

const [logger, mailer, reqId] = inj.getAll(LOGGER, MAILER, REQ_ID); // Logger, Mailer, number
logger.log(`request ${reqId}`);
mailer.send('aditya@example.com', 'Order confirmed');
console.log(inj.get(REQ_ID), inj.get(REQ_ID)); // transient: alag alag
console.log(inj.get(LOGGER) === inj.get(LOGGER)); // singleton: same

const A = new Token<string>('A');
const B = new Token<string>('B');
const bad = new Injector().bind(A, (i) => i.get(B)).bind(B, (i) => i.get(A));
try { bad.get(A); } catch (e) { console.log((e as Error).message); }
// OUTPUT:
// [log] request 1
// [log] mail to aditya@example.com: Order confirmed
// 2 3
// true
// Cycle: A -> B -> A
```

---

## 🟠 Node/Express + React Integration

**Express**: pass dependencies into a `createApp(deps)` factory. Production and tests build different `deps`.

```typescript
import express from 'express';

interface OrderRepo { insert(userId: number, paise: number): Promise<number> } // SQL Server wrapper
interface PaymentGateway { charge(orderId: number, paise: number): Promise<'captured' | 'failed'> }

class OrderService { // dependencies constructor se aate hain, import se nahi
  constructor(private repo: OrderRepo, private gateway: PaymentGateway) {}
  async place(userId: number, paise: number) {
    const orderId = await this.repo.insert(userId, paise);
    const status = await this.gateway.charge(orderId, paise);
    return { orderId, status };
  }
}

// composition root: yahin saari wiring hoti hai
function createApp(deps: { orders: OrderService }) {
  const app = express();
  app.use(express.json());
  app.post('/orders', async (req, res) => {
    const { userId, paise } = req.body as { userId: number; paise: number };
    res.status(201).json(await deps.orders.place(userId, paise));
  });
  return app;
}

// production wiring
const prod = createApp({
  orders: new OrderService(
    { insert: async () => 101 }, // asli me mssql repo
    { charge: async () => 'captured' }, // asli me Razorpay client
  ),
});
// test wiring: fake gateway, SQL Server ki zarurat nahi
const test = createApp({
  orders: new OrderService({ insert: async () => 1 }, { charge: async () => 'failed' }),
});
export { prod, test };
```

**React**: a context + generic `useService(key)` hook gives the same typed lookup in the UI (swap `api` with a mock in Storybook/tests).

```tsx
import { createContext, useContext, type ReactNode } from 'react';

interface Services { // poore frontend ke services ka map
  api: { get<T>(url: string): Promise<T> };
  analytics: { track(event: string): void };
}

const ServicesContext = createContext<Services | null>(null); // null = provider nahi mila

function ServicesProvider({ services, children }: { services: Services; children: ReactNode }) {
  return <ServicesContext.Provider value={services}>{children}</ServicesContext.Provider>;
}

function useService<K extends keyof Services>(key: K): Services[K] { // key se sahi type
  const s = useContext(ServicesContext);
  if (!s) throw new Error('useService must be used inside ServicesProvider');
  return s[key];
}

function CheckoutButton() {
  const analytics = useService('analytics'); // type: Services['analytics']
  return <button onClick={() => analytics.track('checkout_click')}>Pay</button>;
}
export { ServicesProvider, CheckoutButton };
```

**Redux Toolkit** note: pass services via `configureStore({ middleware: (gDM) => gDM({ thunk: { extraArgument: services } }) })`, then thunks receive typed `extra`. Same idea, no globals.

**Redux Toolkit note (Hindi)**: services को `thunk.extraArgument` में पास करो; thunks को typed `extra` मिलता है। Global singleton की ज़रूरत नहीं।

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Registering a service that depends on another *before* that one is registered.

```typescript
// @prepend:1  (Basic example वाला Container यहाँ मान लो)
interface Gw { charge(p: number): string }
const bad1 = new Container()
  .register('orders', (c) => c.resolve('gateway')) // ❌ gateway abhi register nahi hua
  .register('gateway', (): Gw => ({ charge: (p) => `rzp_${p}` }));
// error TS2345: Argument of type '"gateway"' is not assignable to parameter of type 'never'.
// Right: pehle 'gateway' register karo, phir 'orders'.
```

❌ Mistake 2: Assuming the resolved type, or typo in the key.

```typescript
// @prepend:1
interface Gw { charge(p: number): string }
const ok = new Container().register('gateway', (): Gw => ({ charge: (p) => `rzp_${p}` }));
const n: number = ok.resolve('gateway'); // ❌ galat type
// error TS2322: Type 'Gw' is not assignable to type 'number'.
ok.resolve('gatewey'); // ❌ typo
// error TS2345: Argument of type '"gatewey"' is not assignable to parameter of type '"gateway"'.
```

❌ Mistake 3 (no compiler error!): **Service Locator anti-pattern**. Calling `container.resolve()` deep inside business logic hides dependencies. Prefer constructor injection and resolve only in the composition root.
✅ Hindi: `resolve()` को business logic के अंदर मत बुलाओ; dependencies constructor में लो, container सिर्फ `main.ts` में use करो।

---

## 🧠 Tricky Interview Question

**"`register` ends with `return this as unknown as Container<...>`. Isn't that a lie? Why is it still safe?"**

Answer: At runtime it IS the same object; only its *type* changes. This is the **type-state pattern**: the mutable object is the same, but each chain step gives it a "narrower view" that records progress, like a builder. It is safe as long as (1) you never keep using the *old* reference expecting old behaviour, and (2) `resolve` checks `keyof TReg` while the runtime `Map` really has those keys. The cast hides the mutation; the cure is to use the **returned** container (chain or reassign), not the original variable. Hindi: type बदलता है, object नहीं; इसलिए हमेशा *returned* container इस्तेमाल करो।

---

## ⚫ Interview Questions + Answers

Q1: Why depend on interfaces and not concrete classes?
A1: So any implementation (real, fake, in-memory) satisfies the contract structurally. TypeScript is structural, so a plain object literal `{ charge: ... }` is a valid `Gateway`. This enables unit tests without mocking libraries. Hindi: interface contract है, इसलिए fake object भी चलता है।

Q2: How does `Container<TReg & Record<K, V>>` accumulate the registry?
A2: Each `register` is generic over `K extends string` (kept as a literal) and `V` (inferred from the factory return). The return type intersects the old registry with `Record<K, V>`. `keyof (A & B)` = `keyof A | keyof B`, so `resolve` sees all keys.

Q3: Singleton vs transient: how would you model it?
A3: Store the lifetime next to the factory. Singleton: cache by key/token on first resolve. Transient: call the factory every time. Scoped (per HTTP request) = a child injector created in middleware, discarding its cache at end of request.

Q4: How do you detect circular dependencies?
A4: Keep a `resolving` stack. If the token is already on the stack when resolved, throw `Cycle: A -> B -> A` (see the Advanced example). Compile time cannot detect it for runtime factories.

Q5: What is the `declare readonly _phantom: T` field in `Token<T>`?
A5: A **phantom type**: the field never exists at runtime (`declare`), but it makes `Token<Logger>` and `Token<number>` structurally *different* so `inject.get(LOGGER)` can infer `Logger`. Without any use of `T`, TypeScript would treat all tokens as the same type.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many services with layered dependencies (repo -> service -> controller) and you need test fakes.
- Plugin-style apps where the wiring differs per environment (dev/test/prod, Azure vs local).
- You want compile-time safety for lookups.

❌ Avoid when:
- Small app: plain constructor arguments and a `createApp(deps)` function are enough.
- You are on NestJS/Angular: they already ship a DI container (decorators + `reflect-metadata`). Do not build a second one.
- Do not spread `container.resolve` everywhere (service locator).

---

## 📊 Visual Diagram
```
COMPOSITION ROOT (main.ts)
  new Container()
    .register('db',      () => mssqlRepo)        Container<{} & {db: Db}>
    .register('gateway', () => razorpay)         ...      & {gateway: Gateway}
    .register('orders',  c => new OrderService(  ...      & {orders: OrderService}
                               c.resolve('db'),
                               c.resolve('gateway')))
                 |
                 v  resolve<K extends keyof TReg>(key: K): TReg[K]
       Express routes / React Provider / Redux thunk extra
                 |
   TEST: same shape, different factories (fakes)  ->  same types, zero real I/O
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DI container | Object that builds and supplies dependencies | Dependencies बनाने और देने वाला object |
| Composition root | Single place where everything is wired | वह एक जगह जहाँ सब जुड़ता है |
| Type-state | Type changes as methods are called | Method calls के साथ type बदलना |
| Phantom type | Type parameter with no runtime value | Type parameter जिसकी runtime value नहीं |
| Singleton / Transient | One shared instance / new each time | एक shared instance / हर बार नया |
| Service locator | Anti-pattern: resolving inside logic | Logic के अंदर resolve करना (anti-pattern) |

---

## ⚡ 3-Line Summary
English:
1. A typed container records registrations in its type via `Container<TReg & Record<K, V>>`, so `resolve` is checked.
2. Use `Token<T>` phantom types, lifetimes and a resolving stack for production-grade behaviour.
3. Wire in one composition root; pass deps into Express/React/Redux explicitly.

Hindi:
1. Typed container registrations को type में `Container<TReg & Record<K, V>>` से याद रखता है, इसलिए `resolve` checked रहता है।
2. Production के लिए `Token<T>` phantom types, lifetimes और cycle-detect stack इस्तेमाल करो।
3. सब कुछ एक composition root में wire करो; Express/React/Redux में deps explicitly पास करो।

---

## ➡️ Next Topic
**112. Typed Route Params Extraction (template literal types)** — `'/orders/:orderId'` से `{ orderId: string }` type निकालना।
