# 99. TypeScript with Jest and Testing Library
# हिंदी में: Jest और Testing Library के साथ TypeScript

> Verified (type-checked) with **TypeScript 5.9 (5.x)**, `jest` 30 types (`@types/jest`), `@testing-library/react` 16, `@testing-library/user-event` 14, `@testing-library/jest-dom`. The tests were **type-checked, not executed** (no jest/jsdom config was run).

---

## 🔵 Simple Definition (English)
Jest is the test runner/assertion/mocking library; Testing Library renders React components and queries the DOM like a user would. With TypeScript you add `@types/jest` (globals like `describe`, `it`, `expect`, `jest`), run TS tests through `ts-jest`, `@swc/jest` or `babel` (Jest cannot read TS alone), and type your **mocks** (`jest.fn<ReturnType, Args>()`, `jest.Mocked<T>`, `jest.mocked(fn)`) so a test cannot call a mock with the wrong arguments or assert a wrong return value.

## 🔵 सरल परिभाषा (Hindi)
Jest test runner/assertion/mocking library है; Testing Library React components को render करती है और DOM को user की तरह query करती है। TypeScript के साथ आप `@types/jest` (globals जैसे `describe`, `it`, `expect`, `jest`) जोड़ते हो, TS tests `ts-jest`, `@swc/jest` या `babel` से चलाते हो (Jest अकेले TS नहीं पढ़ सकता), और अपने **mocks** को type करते हो (`jest.fn<ReturnType, Args>()`, `jest.Mocked<T>`, `jest.mocked(fn)`) ताकि test mock को गलत arguments से call न कर सके या गलत return value assert न करे।

---

## 🔴 Problem it Solves
Untyped mocks are `jest.Mock<any, any>`: when a function signature changes (`charge(amount)` -> `charge(amount, currency)`), tests keep passing against a stale mock while production breaks. Typed mocks make that a compile error in the test. Also, matchers like `toBeInTheDocument` do not exist on `expect` unless `jest-dom` types are loaded, and `screen.getByRole` returns `HTMLElement` which you may need to narrow for element-specific properties.

## 🔴 यह क्यों बना? (Hindi)
Untyped mocks `jest.Mock<any, any>` होते हैं: जब function signature बदलती है (`charge(amount)` -> `charge(amount, currency)`) तो tests पुराने mock के साथ पास होते रहते हैं और production टूट जाता है। Typed mocks इसे test में compile error बना देते हैं। साथ ही `toBeInTheDocument` जैसे matchers `expect` पर तब तक नहीं होते जब तक `jest-dom` types load न हों, और `screen.getByRole` `HTMLElement` देता है जिसे element-specific properties के लिए narrow करना पड़ सकता है।

---

## 🟢 How it Works — Step by Step
Step 1 → Install `jest`, `@types/jest`, `ts-jest` (or `@swc/jest`), and for React: `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom`, `jest-environment-jsdom`.
Step 2 → Configure `jest.config.ts` (`preset: "ts-jest"`, `testEnvironment: "jsdom"`), and add `import "@testing-library/jest-dom"` in a setup file (this also loads the matcher **types**).
Step 3 → Add `"types": ["jest", "@testing-library/jest-dom"]` to the test `tsconfig` (or import the globals from `@jest/globals`).
Step 4 → Type mocks: `const charge = jest.fn<Promise<Receipt>, [number]>()` (Jest 29 style) or `jest.fn<(n: number) => Promise<Receipt>>()` (Jest 30 style), or `jest.Mocked<PaymentGateway>` for a whole object.
Step 5 → Render with `render(<Cart />)`, query with `screen.getByRole(...)`, interact with `await userEvent.click(...)`.
Step 6 → Assert: `expect(...).toBeInTheDocument()`, `expect(mock).toHaveBeenCalledWith(...)` - arguments are checked against the mock's parameter types.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `jest`, `@types/jest`, `ts-jest` (या `@swc/jest`) install करो, और React के लिए `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom`, `jest-environment-jsdom`।
Step 2 → `jest.config.ts` (`preset: "ts-jest"`, `testEnvironment: "jsdom"`) बनाओ, और setup file में `import "@testing-library/jest-dom"` डालो (इससे matcher **types** भी load होते हैं)।
Step 3 → Test `tsconfig` में `"types": ["jest", "@testing-library/jest-dom"]` जोड़ो (या `@jest/globals` से globals import करो)।
Step 4 → Mocks type करो: `jest.fn<Promise<Receipt>, [number]>()` (Jest 29 style) या `jest.fn<(n: number) => Promise<Receipt>>()` (Jest 30 style), या पूरे object के लिए `jest.Mocked<PaymentGateway>`।
Step 5 → `render(<Cart />)` से render करो, `screen.getByRole(...)` से query करो, `await userEvent.click(...)` से interact करो।
Step 6 → Assert: `expect(...).toBeInTheDocument()`, `expect(mock).toHaveBeenCalledWith(...)` - arguments mock के parameter types से check होते हैं।

---

## 🟡 Real World Example
**Razorpay checkout service test**: `CheckoutService` depends on a `PaymentGateway` interface. In the test we create a `jest.Mocked<PaymentGateway>` whose `charge` resolves a receipt; we assert `charge` was called with `(49900, "INR")`. For the React `PayButton`, we render it, click, and assert the "Paid" text appears - without hitting the network.

## 🟡 Real Example Hindi mein
**Razorpay checkout service test**: `CheckoutService` एक `PaymentGateway` interface पर निर्भर है। Test में हम `jest.Mocked<PaymentGateway>` बनाते हैं जिसका `charge` receipt resolve करता है; और assert करते हैं कि `charge` `(49900, "INR")` से call हुआ। React `PayButton` के लिए उसे render करते हैं, click करते हैं और "Paid" text दिखने की जाँच करते हैं - network छुए बिना।

---

## 💻 Code Example — Basic

```typescript
// checkout.test.ts — typed unit test with a typed mock (type-checked; run with jest + ts-jest)
interface Receipt { id: string; amount: number }                          // gateway result
interface PaymentGateway { charge(amount: number, currency: string): Promise<Receipt> } // dependency

class CheckoutService {
  constructor(private readonly gw: PaymentGateway) {}                    // inject the dependency
  async pay(rupees: number): Promise<Receipt> {
    return this.gw.charge(rupees * 100, "INR");                          // convert to paise
  }
}

describe("CheckoutService", () => {                                      // jest globals typed by @types/jest
  it("charges in paise", async () => {
    // jest.Mocked<T> = T whose methods are jest.MockedFunction
    const gw: jest.Mocked<PaymentGateway> = {
      charge: jest.fn<Promise<Receipt>, [number, string]>(),             // Jest 29 generic form: <Return, Args>
    };
    gw.charge.mockResolvedValue({ id: "r1", amount: 49900 });            // value must be a Receipt

    const svc = new CheckoutService(gw);                                 // pass the mock as the interface
    const receipt = await svc.pay(499);                                  // receipt: Receipt

    expect(receipt.id).toBe("r1");                                       // matcher
    expect(gw.charge).toHaveBeenCalledWith(49900, "INR");                // checked against (number, string)
  });
});
```

## 💻 Code Example — Advanced

```tsx
// pay-button.test.tsx — React Testing Library + user-event + jest-dom, typed
import "@testing-library/jest-dom";                           // adds toBeInTheDocument etc. (and their types)
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";

// ----- component under test -----
interface PayButtonProps { amount: number; onPay: (amount: number) => Promise<void> }
function PayButton({ amount, onPay }: PayButtonProps) {
  const [state, setState] = useState<"idle" | "paying" | "paid" | "error">("idle"); // simple state machine
  async function click() {
    setState("paying");                                       // show spinner text
    try { await onPay(amount); setState("paid"); }            // success path
    catch { setState("error"); }                              // failure path
  }
  return (
    <div>
      <button onClick={click} disabled={state === "paying"}>Pay ₹{amount}</button>
      {state === "paid" && <p role="status">Paid</p>}
      {state === "error" && <p role="alert">Failed</p>}
    </div>
  );
}

// ----- typed helpers -----
// Factory that returns a typed mock for the prop; override per test
function setup(overrides: Partial<PayButtonProps> = {}) {
  const onPay = jest.fn<Promise<void>, [number]>().mockResolvedValue(undefined); // typed prop mock
  render(<PayButton amount={499} onPay={onPay} {...overrides} />);               // render with defaults
  const user = userEvent.setup();                                                // v14 API
  return { onPay, user };
}

describe("PayButton", () => {
  it("calls onPay with the amount and shows Paid", async () => {
    const { onPay, user } = setup();
    await user.click(screen.getByRole("button", { name: /pay ₹499/i }));         // query by role like a user
    expect(onPay).toHaveBeenCalledWith(499);                                     // typed argument check
    expect(await screen.findByRole("status")).toHaveTextContent("Paid");         // async appearance
  });

  it("shows an error when payment fails", async () => {
    const onPay = jest.fn<Promise<void>, [number]>().mockRejectedValue(new Error("declined")); // typed rejection
    const { user } = setup({ onPay });                                                           // override prop
    await user.click(screen.getByRole("button"));
    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());   // retry until true
  });

  it("narrows HTMLElement when you need element-specific props", () => {
    setup();
    const btn = screen.getByRole("button");                                       // HTMLElement
    expect(btn).toBeEnabled();                                                    // jest-dom matcher
    if (btn instanceof HTMLButtonElement) expect(btn.disabled).toBe(false);       // narrow to read .disabled
  });
});

// ----- jest.mocked: type an imported function mock without casts -----
function fetchOrder(id: number): Promise<{ id: number }> { return Promise.resolve({ id }); }
it("jest.mocked keeps the original signature", () => {
  const spy = jest.spyOn({ fetchOrder }, "fetchOrder");                           // spy typed from the object
  spy.mockResolvedValue({ id: 7 });                                               // must be { id: number }
  expect(jest.isMockFunction(spy)).toBe(true);
});
```

---

## 🟠 Node/Express + React Integration

```typescript
// Testing an Express handler as a pure function (no server needed) with typed fakes.
import type { Request, Response } from "express";

interface Payment { id: string; amount: number }
interface PaymentRepo { find(id: string): Promise<Payment | null> }

// The handler is created by a factory so the repo can be injected (easy to test)
const getPayment = (repo: PaymentRepo) => async (req: Request<{ id: string }>, res: Response): Promise<void> => {
  const p = await repo.find(req.params.id);                       // Payment | null
  if (!p) { res.status(404).json({ error: "not found" }); return; }
  res.json(p);                                                    // 200
};

it("returns 404 when payment is missing", async () => {
  const repo: jest.Mocked<PaymentRepo> = { find: jest.fn<Promise<Payment | null>, [string]>() };
  repo.find.mockResolvedValue(null);                              // typed: null is allowed
  const json = jest.fn();                                         // spy for res.json
  const status = jest.fn(() => ({ json }));                       // res.status(404) returns { json }
  const res = { status, json } as unknown as Response;            // partial Response: cast through unknown ONCE, here
  await getPayment(repo)({ params: { id: "x" } } as Request<{ id: string }>, res);
  expect(status).toHaveBeenCalledWith(404);                       // assert
});
```

```json
// jest.config / tsconfig notes (not TypeScript, shown for completeness)
// jest.config.ts  -> { preset: "ts-jest", testEnvironment: "jsdom", setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"] }
// jest.setup.ts   -> import "@testing-library/jest-dom";
// tsconfig.json   -> { "compilerOptions": { "types": ["jest", "@testing-library/jest-dom"], "jsx": "react-jsx" } }
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling the code under test with a wrong argument type
```typescript
// ❌ WRONG
declare function add(a: number, b: number): number;
test("x", () => { expect(add(1, "2")).toBe(3); });
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```
✅ Correct: pass numbers; the compiler stops you from writing a test that cannot match the contract.

❌ Mistake 2: Calling a typed mock with the wrong argument
```typescript
// ❌ WRONG
test("m", () => { const m = jest.fn<number, [string]>(); m(5); });
// error TS2345: Argument of type 'number' is not assignable to parameter of type 'string'.
```

❌ Mistake 3: Using `as any` to silence a mock mismatch
`const gw = { charge: jest.fn() } as any` makes every future signature change invisible. ✅ Correct: `jest.Mocked<PaymentGateway>` or `Pick<PaymentGateway, "charge">`; if you must fake a huge object (like `Response`), cast through `unknown` once in a helper.

❌ Mistake 4: Forgetting jest-dom types
`expect(el).toBeInTheDocument()` errors with "Property 'toBeInTheDocument' does not exist on type 'JestMatchers<HTMLElement>'" if `@testing-library/jest-dom` is not imported/listed in `types`. ✅ Correct: import it in a setup file included by your tsconfig.

---

## 🧠 Tricky Interview Question

```typescript
// Why does this test pass type-checking and still prove nothing about the real function?
interface Gateway { charge(amount: number): Promise<string> }
export async function t() {
  const gw = { charge: jest.fn() } as unknown as Gateway;         // double-cast
  (gw.charge as jest.Mock).mockResolvedValue(123);                // number, but interface says string!
  const r: string = await gw.charge(1);                           // TS thinks r is string, runtime is 123
  return r;
}
```
**Answer:** Casting through `unknown` and `jest.Mock` (which is `Mock<any, any>`) switches off all checking, so `mockResolvedValue(123)` is accepted although `charge` must resolve a `string`. The test passes while encoding a lie. Use `jest.Mocked<Gateway>` (its `charge.mockResolvedValue` demands a `string`) or `jest.mocked(gw).charge.mockResolvedValue("ok")`. Rule: **mocks should be typed from the real interface, never cast away.**

---

## ⚫ Interview Questions + Answers

Q1: How do you run TypeScript tests in Jest?
A1: Jest only understands JS, so transform TS with `ts-jest` (type-checks), `@swc/jest` or Babel (fast, no type-check), or run `tsc --noEmit` separately. Many teams use swc for speed + `tsc` in CI for types. Vitest handles TS out of the box.

Q2: `jest.fn()`, `jest.Mocked<T>`, `jest.mocked()` - differences?
A2: `jest.fn()` creates an untyped/loosely typed mock. `jest.Mocked<T>` is a type: all methods of `T` as typed mocks. `jest.mocked(x)` is a helper that returns `x` typed as mocked (for `jest.mock("./module")` imports) with no runtime effect.

Q3: Why prefer `getByRole` and `userEvent`?
A3: They test what users perceive (accessible roles/names) and simulate real event sequences (focus, keydown, click) rather than implementation details; they also make accessibility regressions visible. `fireEvent` is lower-level.

Q4: How do you test code using `fetch` with types?
A4: `jest.spyOn(global, "fetch").mockResolvedValue(new Response(JSON.stringify(data)))`, or use MSW to intercept at network level and keep the real client code under test. Build typed fixture factories (`makeOrder(overrides: Partial<Order>)`).

Q5: Where do tests fit in a typed codebase?
A5: Tests are code: type-check them in CI (`tsc --noEmit -p tsconfig.test.json`), keep fixtures typed with the production types, and use `satisfies` (TS 4.9+) for literal fixtures that must match an interface while keeping literal types.

---

## 🔷 When to Use + When Not to Use
✅ Use typed tests when:
- Contracts change often (API clients, gateways, reducers)
- You mock dependencies (`jest.Mocked<T>` catches signature drift)
- Testing user-visible behaviour of components (Testing Library)

❌ Avoid:
- Testing implementation details (internal state, private methods)
- `as any` mocks, snapshots of huge trees, asserting TS types at runtime (use `expectTypeOf`/`tsd` for type tests instead)
- Real network/DB calls in unit tests

---

## 📊 Visual Diagram
```
 production code            test code
 ─────────────────          ───────────────────────────────────────
 interface Gateway   ───►   jest.Mocked<Gateway>   (typed from the SAME interface)
 CheckoutService     ───►   new CheckoutService(mockGw)
                            expect(mockGw.charge).toHaveBeenCalledWith(49900,"INR")
 <PayButton/>        ───►   render(<PayButton/>) → screen.getByRole("button")
                            await user.click(...) → expect(...).toBeInTheDocument()

 Signature changes ⇒ mock + call-site compile errors ⇒ tests updated before bugs ship
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mock | Fake dependency recording calls | नकली dependency जो calls record करती है |
| jest.Mocked<T> | T with all methods mocked, typed | T जिसके सब methods typed mocks हों |
| Testing Library | DOM testing like a user | user की तरह DOM testing |
| jest-dom | Extra DOM matchers | अतिरिक्त DOM matchers |
| userEvent | Realistic user interaction API | असली जैसा user interaction API |
| ts-jest | Jest transformer for TS | TS के लिए Jest transformer |

---

## ⚡ 3-Line Summary
English:
1. Add `@types/jest` + a TS transformer (ts-jest/swc); load jest-dom types in a setup file.
2. Type mocks from real interfaces (`jest.Mocked<T>`, `jest.fn<Return, Args>()`) so signature drift fails to compile.
3. Test React like a user (`getByRole`, `userEvent`); never silence mocks with `as any`.

Hindi:
1. `@types/jest` + TS transformer (ts-jest/swc) जोड़ो; setup file में jest-dom types load करो।
2. Mocks को असली interfaces से type करो (`jest.Mocked<T>`, `jest.fn<Return, Args>()`) ताकि signature बदलने पर compile fail हो।
3. React को user की तरह test करो (`getByRole`, `userEvent`); mocks को `as any` से चुप मत कराओ।

---

## ➡️ Next Topic
**100. Common Compiler Errors and How to Read Them** — decode the most frequent TS error messages.
