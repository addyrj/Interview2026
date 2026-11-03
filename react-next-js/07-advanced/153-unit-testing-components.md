# 153. Unit Testing Components
# हिंदी में: Components की Unit Testing — एक component को अलग से जाँचना

---

## 🔵 Simple Definition (English)
**Unit testing a component** means rendering one component alone, giving it props, simulating user actions, and checking its output. Child components are real or lightly mocked, and network or other modules are replaced with fakes. The test is small, fast and focused on one behaviour.

## 🔵 सरल परिभाषा (Hindi)
**Component की unit testing** का मतलब है एक component को अकेले render करना, उसे props देना, user actions simulate करना और उसका output जाँचना। Child components असली या हल्के mock होते हैं, और network या दूसरे modules की जगह नकली चीज़ें लगाई जाती हैं। Test छोटा, तेज़ और एक ही behaviour पर केंद्रित होता है।

---

## 🔴 Problem it Solves

Big end-to-end tests are slow and fail for unrelated reasons (network, login, data). When one fails you do not know which component is guilty. Unit tests pin the problem to one component: "the `OrderStatusBadge` shows the wrong colour for `CANCELLED`". They run in milliseconds, so you can run hundreds on every save. They also act as a spec: the test names describe what the component promises.

## 🔴 यह क्यों बना? (Hindi)
बड़े end-to-end tests धीमे होते हैं और असंबंधित कारणों (network, login, data) से fail होते हैं। एक fail हो तो पता नहीं चलता कि कौन सा component दोषी है। Unit tests समस्या को एक component तक सीमित कर देते हैं: "`OrderStatusBadge` में `CANCELLED` का रंग गलत है।" ये milliseconds में चलते हैं, इसलिए हर save पर सैकड़ों चला सकते हैं। ये spec का काम भी करते हैं: test के नाम बताते हैं कि component क्या वादा करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick ONE behaviour: "shows Closed when restaurant is closed"
Step 2 → Arrange: render the component with props that set up that situation
Step 3 → Act: simulate what the user does (click, type) if needed
Step 4 → Assert: check visible output or that a callback prop was called
Step 5 → Mock only the boundaries: API modules, router, timers (not your own small children)
Step 6 → Name the test as a sentence: "calls onAdd with item id when Add is clicked"
Step 7 → Repeat for each branch: loading, error, empty, success, disabled

Pattern:  Arrange → Act → Assert (AAA)
Test:     inputs (props, events)  →  outputs (DOM, callbacks)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → एक ही behaviour चुनो: "restaurant बंद हो तो Closed दिखाता है"
Step 2 → Arrange: ऐसे props के साथ component render करो जो वह स्थिति बनाएँ
Step 3 → Act: ज़रूरत हो तो user जैसा करो (click, type)
Step 4 → Assert: दिखने वाला output या callback prop का call होना जाँचो
Step 5 → सिर्फ boundaries mock करो: API modules, router, timers (अपने छोटे children नहीं)
Step 6 → Test का नाम वाक्य जैसा रखो: "Add दबाने पर item id के साथ onAdd call होता है"
Step 7 → हर branch के लिए दोहराओ: loading, error, empty, success, disabled

Pattern:  Arrange → Act → Assert (AAA)
Test:     inputs (props, events)  →  outputs (DOM, callbacks)
```

---

## 🟡 Real World Example
**Zomato "Add to cart" button on a dish card.** Behaviours to unit test: it shows the dish name and price formatted as ₹250; clicking "ADD" calls `onAdd` with the dish id; when `soldOut` is true the button is disabled and says "Sold out"; when a dish is veg a green dot is shown (by accessible label "Vegetarian"). These are four tiny tests with no server. A fifth test for a form component, like the coupon box, checks that invalid input shows an error and a valid one calls `onApply`.

## 🟡 Real Example Hindi mein
**Zomato की dish card पर "ADD" बटन।** Unit test करने योग्य behaviours: dish का नाम और कीमत ₹250 के format में दिखती है; "ADD" दबाने पर dish id के साथ `onAdd` call होता है; `soldOut` true हो तो बटन disabled और "Sold out" लिखा होता है; dish veg हो तो हरा बिंदु दिखता है (accessible label "Vegetarian" से)। ये चार छोटे tests हैं, server के बिना। पाँचवाँ test coupon box जैसे form के लिए: गलत input पर error दिखता है और सही input पर `onApply` call होता है।

---

## 💻 Code Example — Basic

```jsx
// DishCard.jsx : component under test
export function DishCard({ dish, onAdd }) {              // dish data + callback from the parent
  const price = new Intl.NumberFormat('en-IN', {         // format number as Indian rupees
    style: 'currency', currency: 'INR', maximumFractionDigits: 0,
  }).format(dish.price);
  return (
    <article>
      <h3>{dish.name}</h3>                               {/* dish name */}
      <p>{price}</p>                                     {/* formatted price */}
      {dish.veg && <span aria-label="Vegetarian">🟢</span>} {/* label for assistive tech and tests */}
      <button disabled={dish.soldOut} onClick={() => onAdd(dish.id)}> {/* parent decides what add means */}
        {dish.soldOut ? 'Sold out' : 'ADD'}              {/* label depends on stock */}
      </button>
    </article>
  );
}
```

```jsx
// DishCard.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { DishCard } from './DishCard';

// A helper builds a default dish so each test only overrides what matters
const makeDish = (overrides = {}) => ({
  id: 7, name: 'Paneer Tikka', price: 250, veg: true, soldOut: false, ...overrides,
});

test('shows name and formatted price', () => {
  render(<DishCard dish={makeDish()} onAdd={jest.fn()} />);            // Arrange
  expect(screen.getByRole('heading', { name: 'Paneer Tikka' })).toBeInTheDocument(); // Assert
  expect(screen.getByText(/250/)).toBeInTheDocument();                  // contains ₹250
});

test('calls onAdd with the dish id when ADD is clicked', async () => {
  const onAdd = jest.fn();                                // fake callback records calls
  const user = userEvent.setup();
  render(<DishCard dish={makeDish()} onAdd={onAdd} />);   // Arrange
  await user.click(screen.getByRole('button', { name: 'ADD' })); // Act
  expect(onAdd).toHaveBeenCalledTimes(1);                 // Assert: exactly one call
  expect(onAdd).toHaveBeenCalledWith(7);                  // with the right argument
});

test('disables the button when sold out', async () => {
  const onAdd = jest.fn();
  const user = userEvent.setup();
  render(<DishCard dish={makeDish({ soldOut: true })} onAdd={onAdd} />);
  const button = screen.getByRole('button', { name: 'Sold out' });
  expect(button).toBeDisabled();                          // disabled state
  await user.click(button);                               // user-event ignores disabled clicks
  expect(onAdd).not.toHaveBeenCalled();                   // nothing happened
});

test('shows the vegetarian marker only for veg dishes', () => {
  const { rerender } = render(<DishCard dish={makeDish({ veg: true })} onAdd={jest.fn()} />);
  expect(screen.getByLabelText('Vegetarian')).toBeInTheDocument();
  rerender(<DishCard dish={makeDish({ veg: false })} onAdd={jest.fn()} />); // same instance, new props
  expect(screen.queryByLabelText('Vegetarian')).not.toBeInTheDocument();
});
```

## 💻 Code Example — Advanced

```jsx
// CouponForm.jsx : form with validation and an async submit
import { useState } from 'react';

export function CouponForm({ onApply }) {                // onApply returns a Promise<{ ok, message }>
  const [code, setCode] = useState('');                  // controlled input
  const [error, setError] = useState('');                // validation or server error
  const [loading, setLoading] = useState(false);         // prevents double submit

  async function handleSubmit(e) {
    e.preventDefault();                                  // stop page reload
    if (!/^[A-Z0-9]{4,10}$/.test(code)) {                // simple client-side rule
      setError('Enter a valid coupon code');
      return;
    }
    setError(''); setLoading(true);                      // clear error, show busy state
    const result = await onApply(code);                  // ask the parent/server
    setLoading(false);
    if (!result.ok) setError(result.message);            // show server message
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="coupon">Coupon</label>
      <input id="coupon" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} />
      <button type="submit" disabled={loading}>{loading ? 'Applying...' : 'Apply'}</button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
```

```jsx
// CouponForm.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { CouponForm } from './CouponForm';

// Small setup helper: renders the form and returns the user and the fake callback
function setup(onApply = jest.fn().mockResolvedValue({ ok: true })) {
  const user = userEvent.setup();
  render(<CouponForm onApply={onApply} />);
  return { user, onApply, input: screen.getByLabelText('Coupon') }; // label lookup = accessibility check
}

test('rejects an invalid code without calling onApply', async () => {
  const { user, onApply, input } = setup();
  await user.type(input, 'a!');                           // too short and invalid characters
  await user.click(screen.getByRole('button', { name: 'Apply' }));
  expect(screen.getByRole('alert')).toHaveTextContent('Enter a valid coupon code');
  expect(onApply).not.toHaveBeenCalled();                 // validation stopped the call
});

test('uppercases input and submits a valid code', async () => {
  const { user, onApply, input } = setup();
  await user.type(input, 'save50');                       // user types lower case
  expect(input).toHaveValue('SAVE50');                    // component uppercases it
  await user.click(screen.getByRole('button', { name: 'Apply' }));
  expect(onApply).toHaveBeenCalledWith('SAVE50');
});

test('shows the server message when the coupon is expired', async () => {
  const onApply = jest.fn().mockResolvedValue({ ok: false, message: 'Coupon expired' });
  const { user, input } = setup(onApply);
  await user.type(input, 'OLD2023');
  await user.click(screen.getByRole('button', { name: 'Apply' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Coupon expired'); // async result
});

test('disables the button while applying', async () => {
  let resolve;                                            // we control when the promise finishes
  const pending = new Promise((r) => { resolve = r; });
  const { user, input } = setup(jest.fn().mockReturnValue(pending));
  await user.type(input, 'SAVE50');
  await user.click(screen.getByRole('button', { name: 'Apply' }));
  expect(screen.getByRole('button', { name: 'Applying...' })).toBeDisabled(); // busy state
  resolve({ ok: true });                                  // finish the request
  expect(await screen.findByRole('button', { name: 'Apply' })).toBeEnabled();
});
```

```jsx
// Testing a custom hook with renderHook (RTL v13.1+)
import { renderHook, act } from '@testing-library/react';
import { useState, useCallback } from 'react';

function useCounter(start = 0) {                          // hook under test
  const [n, setN] = useState(start);
  const inc = useCallback(() => setN((x) => x + 1), []);  // stable function identity
  return { n, inc };
}

test('increments', () => {
  const { result } = renderHook(() => useCounter(5));     // result.current is the latest return value
  act(() => result.current.inc());                        // state updates must be inside act
  expect(result.current.n).toBe(6);
});
```

---

## 🟠 Next.js Connection

In Next.js unit tests, three things need special handling. (1) `next/image` and `next/link` mostly work in Jest through `next/jest`. (2) `next/navigation` hooks (`useRouter`, `usePathname`, `useSearchParams`) need mocks. (3) **Server Actions** passed as props to a Client Component can be tested by passing a plain `jest.fn()`, because the component only sees a function.

```jsx
// AddressForm.test.jsx : Client Component that receives a Server Action as a prop
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AddressForm } from './AddressForm';            // 'use client' component

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn(), refresh: jest.fn() }), // fake router
}));

test('submits the address through the action prop', async () => {
  const saveAddress = jest.fn().mockResolvedValue({ ok: true }); // stands in for the server action
  const user = userEvent.setup();
  render(<AddressForm saveAddress={saveAddress} />);
  await user.type(screen.getByLabelText('City'), 'Pune');
  await user.click(screen.getByRole('button', { name: /save/i }));
  expect(saveAddress).toHaveBeenCalled();               // logic verified without a server
});
```

Async Server Components cannot be unit tested with RTL (Next.js docs recommend E2E for them). Keep logic in plain functions and presentational components so most of it stays unit-testable.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mocking your own child components everywhere (shallow rendering)
✅ **Correct:** Render real children; mock only network, router and other boundaries

```jsx
// Wrong: the parent test passes even if the child is broken
jest.mock('./DishCard', () => () => <div>DishCard</div>);

// Right: use the real DishCard, and mock the API layer instead
jest.mock('./api');
```

❌ **Mistake 2:** Several unrelated assertions in one giant test, with state leaking between tests
✅ **Correct:** One behaviour per test, fresh render and fresh mocks each time

```jsx
// Wrong: shared object mutated across tests, order-dependent
const props = { items: [] };
test('a', () => { props.items.push(1); /* ... */ });
test('b', () => { /* items is not empty any more */ });

// Right: build props inside each test (or a factory) and reset mocks
beforeEach(() => jest.clearAllMocks());
const makeProps = () => ({ items: [] });                // new object every call
```

❌ **Mistake 3:** Asserting on `console.log` output or on how many times a component rendered
✅ **Correct:** Assert on DOM output and callback calls

```jsx
// Wrong: render counts are an implementation detail and change with React versions (e.g. Strict Mode double render)
expect(renderSpy).toHaveBeenCalledTimes(2);

// Right: user-visible result
expect(screen.getByText('Total: ₹500')).toBeInTheDocument();
```

---

## 🧠 Tricky Interview Question

```jsx
function Price({ value }) {
  return <p>{value.toFixed(2)}</p>;                      // crashes if value is undefined
}

test('shows price', () => {
  render(<Price />);                                     // forgot the prop
  expect(screen.getByText('0.00')).toBeInTheDocument();
});
```
What happens, and what does it tell you?

**Answer:** The test fails with `TypeError: Cannot read properties of undefined (reading 'toFixed')`, thrown while rendering, and React also logs an error to the console. The test is revealing a real bug: the component does not handle a missing prop. You can fix the component (`value = 0` default), or intentionally test the failure with `expect(() => render(<Price />)).toThrow()` (and silence the expected `console.error` with a spy). The lesson: unit tests are cheap ways to cover missing, empty and `null` props that never appear in happy-path manual testing.

---

## ⚫ Interview Questions + Answers

Q1: What should a good component unit test cover?
A1: Rendering for given props, each conditional branch (loading, error, empty, success), user interactions and the callbacks they trigger, form validation, and accessibility basics (roles and labels). It should not cover internal state or private functions.

Q2: What should you mock in a component test and what should you not?
A2: Mock boundaries you do not own or that are slow or non-deterministic: network calls, router, timers, `localStorage`, date/time, and third-party widgets. Do not mock your own simple child components or React itself, because that hides integration bugs.

Q3: How do you test that a callback prop was called?
A3: Pass `jest.fn()` as the prop, perform the user action, then use `toHaveBeenCalledTimes` and `toHaveBeenCalledWith`. Check the call count as well as the arguments.

Q4: How do you unit test a custom hook?
A4: Use `renderHook` from RTL. Read the latest value from `result.current`, wrap state-changing calls in `act`, and pass a `wrapper` when the hook needs context providers. If a hook is only used by one component, testing the component is often enough.

Q5: What is the difference between a unit test and an integration test for components?
A5: A unit test focuses on one component with its dependencies mocked. An integration test renders several components together (a page with a list, filters and a cart) and checks that they work together, mocking only the network. Both use the same tools.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A component has logic, branches, validation or callbacks
- You are building shared components (buttons, inputs, modals) used in many places
- You fix a bug: write a failing test first, then fix

❌ **Avoid when:**
- The component is a trivial wrapper with no behaviour (a test just repeats the code)
- You would assert styling details or exact class names
- Behaviour only emerges from several components together (write an integration test)

**Re-render and performance note:** Do not assert render counts in unit tests. React 18/19 Strict Mode renders components twice in development, so counts are unreliable. Unit tests run in milliseconds per test; keep them fast by avoiding real timers (use `jest.useFakeTimers()`), and by not rendering the whole app for a small behaviour.

---

## 📊 Visual Diagram

```
        ARRANGE                  ACT                      ASSERT
   ┌────────────────┐     ┌───────────────┐      ┌─────────────────────┐
   │ props = {...}  │     │ user.click()  │      │ DOM shows 'Sold out'│
   │ onAdd = fn()   │ ──► │ user.type()   │ ──►  │ onAdd called with 7 │
   │ render(<Dish/>)│     │               │      │ no error alert      │
   └────────────────┘     └───────────────┘      └─────────────────────┘

   Boundaries mocked:   [ API ]  [ router ]  [ timers ]  [ localStorage ]
   Real:                the component + its small children
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Unit test | Test of one small unit in isolation | एक छोटे हिस्से का अलग टेस्ट |
| AAA | Arrange, Act, Assert | तैयारी, क्रिया, जाँच |
| jest.fn() | Fake function that records calls | Calls को record करने वाला नकली function |
| renderHook | RTL helper to test hooks | Hooks टेस्ट करने का helper |
| rerender | Render same tree again with new props | नए props के साथ दोबारा render |
| Factory | Helper that builds default test data | Test data बनाने वाला helper |
| Boundary | Edge of your code (network, router) | आपके code की सीमा (network, router) |
| Fake timers | Jest-controlled setTimeout and Date | Jest के नियंत्रण वाला समय |

---

## ⚡ 3-Line Summary
**English:**
1. A component unit test renders one component, acts like a user and asserts visible output and callbacks.
2. Mock only boundaries (network, router, timers), build fresh props per test, and never assert internals.
3. In Next.js, mock `next/navigation`, pass Server Actions as plain `jest.fn()`, and leave async Server Components to E2E.

**Hindi:**
1. Component unit test एक component render करता है, user की तरह काम करता है और दिखने वाला output व callbacks जाँचता है।
2. सिर्फ boundaries (network, router, timers) mock करो, हर test में नए props बनाओ, और internals कभी assert मत करो।
3. Next.js में `next/navigation` mock करो, Server Actions को साधारण `jest.fn()` की तरह दो, और async Server Components को E2E के लिए छोड़ो।

---

## ➡️ Next Topic
**154. Integration Testing** — अब कई components को एक साथ टेस्ट करना सीखो: पूरा page, उसका store, filters और cart, ताकि पता चले कि हिस्से आपस में सही जुड़े हैं।
