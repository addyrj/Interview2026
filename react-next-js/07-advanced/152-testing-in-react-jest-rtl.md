# 152. Testing in React (Jest + RTL)
# हिंदी में: React में Testing — Jest और React Testing Library

---

## 🔵 Simple Definition (English)
**Jest** is a JavaScript test runner (it finds tests, runs them, checks results with `expect`). **React Testing Library (RTL)** renders React components in a fake DOM and lets you find elements the way a user does (by text, label, role). Together they check that your UI behaves correctly.

## 🔵 सरल परिभाषा (Hindi)
**Jest** एक JavaScript test runner है (tests ढूँढता है, चलाता है, `expect` से नतीजे जाँचता है)। **React Testing Library (RTL)** components को नकली DOM में render करती है और elements को वैसे ढूँढने देती है जैसे user ढूँढता है (text, label, role से)। दोनों मिलकर जाँचते हैं कि आपका UI सही व्यवहार करता है।

---

## 🔴 Problem it Solves

Without tests, every change is a gamble: fixing the cart total might silently break the coupon box. Manual testing is slow and misses cases. Older tools such as Enzyme tested internals (`state()`, `instance()`), so tests broke whenever you refactored even though the app still worked. RTL's philosophy is: "The more your tests resemble the way your software is used, the more confidence they give you." You test what the user sees and does, not how the component is built inside.

## 🔴 यह क्यों बना? (Hindi)
Tests के बिना हर बदलाव एक जुआ है: cart total ठीक करने पर coupon box चुपचाप टूट सकता है। Manual testing धीमी है और cases छूट जाते हैं। Enzyme जैसे पुराने tools internals (`state()`, `instance()`) टेस्ट करते थे, इसलिए refactor करने पर tests टूट जाते थे जबकि app ठीक चलता था। RTL का सिद्धांत है: "आपके tests जितने ज़्यादा असली इस्तेमाल जैसे होंगे, उतना ज़्यादा भरोसा देंगे।" यानी user जो देखता और करता है उसे टेस्ट करो, component अंदर से कैसा बना है उसे नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install: npm i -D jest jest-environment-jsdom @testing-library/react
         @testing-library/jest-dom @testing-library/user-event (+ babel or SWC transform)
Step 2 → Configure Jest: testEnvironment "jsdom", setup file that imports "@testing-library/jest-dom"
Step 3 → Write Component.test.jsx next to the component
Step 4 → render(<Component />) mounts it into a jsdom document
Step 5 → Find elements with screen queries: getByRole, getByLabelText, getByText
Step 6 → Act like a user: await user.click(...), await user.type(...)
Step 7 → Assert the visible result: expect(...).toBeInTheDocument()
Step 8 → Run npx jest. RTL cleans up the DOM after each test automatically

Query families:  getBy (must exist now)   queryBy (may be null, use for "not there")
                 findBy (async, waits)    + All variants for many elements
Priority:        getByRole > getByLabelText > getByText > getByTestId (last resort)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Install करो: npm i -D jest jest-environment-jsdom @testing-library/react
         @testing-library/jest-dom @testing-library/user-event (+ babel या SWC transform)
Step 2 → Jest configure करो: testEnvironment "jsdom", और setup file जिसमें "@testing-library/jest-dom" import हो
Step 3 → Component के पास Component.test.jsx लिखो
Step 4 → render(<Component />) उसे jsdom document में mount करता है
Step 5 → screen queries से elements ढूँढो: getByRole, getByLabelText, getByText
Step 6 → User की तरह करो: await user.click(...), await user.type(...)
Step 7 → जो दिखे उसे assert करो: expect(...).toBeInTheDocument()
Step 8 → npx jest चलाओ। हर test के बाद RTL DOM अपने-आप साफ करती है

Query families:  getBy (अभी मौजूद होना चाहिए)   queryBy (null हो सकता है, "नहीं है" जाँचने के लिए)
                 findBy (async, इंतज़ार करता है)   + All versions कई elements के लिए
Priority:        getByRole > getByLabelText > getByText > getByTestId (आखिरी विकल्प)
```

---

## 🟡 Real World Example
**Amazon quantity selector:** A product page has a "+" and "-" button and a quantity number. Tests: the number starts at 1, clicking "+" shows 2, clicking "-" at 1 does nothing (minimum is 1), and at the maximum of 10 the "+" button is disabled. None of these tests care whether the component uses `useState` or `useReducer`. If the team rewrites it with a reducer, all tests still pass, which is exactly what we want.

## 🟡 Real Example Hindi mein
**Amazon quantity selector:** Product page पर "+" और "-" बटन और quantity संख्या होती है। Tests: संख्या 1 से शुरू होती है, "+" दबाने पर 2 दिखता है, 1 पर "-" दबाने से कुछ नहीं होता (minimum 1 है), और maximum 10 पर "+" बटन disabled हो जाता है। किसी test को परवाह नहीं कि component `useState` इस्तेमाल करता है या `useReducer`। अगर team इसे reducer से दोबारा लिखे, तब भी सारे tests पास होंगे, और हमें यही चाहिए।

---

## 💻 Code Example — Basic

```jsx
// QuantitySelector.jsx : component to test
import { useState } from 'react';                       // local state

export function QuantitySelector({ min = 1, max = 10 }) { // limits come as props
  const [qty, setQty] = useState(min);                  // start at the minimum
  return (
    <div>
      <button onClick={() => setQty((q) => Math.max(min, q - 1))} aria-label="Decrease">-</button>
      <span data-testid="qty">{qty}</span>              {/* the displayed number */}
      <button
        onClick={() => setQty((q) => Math.min(max, q + 1))}
        disabled={qty >= max}                           // cannot go above the maximum
        aria-label="Increase"
      >
        +
      </button>
    </div>
  );
}
```

```jsx
// QuantitySelector.test.jsx
import { render, screen } from '@testing-library/react';        // render + queries
import userEvent from '@testing-library/user-event';            // realistic user actions
import '@testing-library/jest-dom';                             // matchers like toBeDisabled
import { QuantitySelector } from './QuantitySelector';          // component under test

describe('QuantitySelector', () => {                            // group related tests
  test('starts at the minimum', () => {
    render(<QuantitySelector />);                               // mount into jsdom
    expect(screen.getByTestId('qty')).toHaveTextContent('1');   // assert visible number
  });

  test('increases when + is clicked', async () => {
    const user = userEvent.setup();                             // create a user-event instance
    render(<QuantitySelector />);
    await user.click(screen.getByRole('button', { name: 'Increase' })); // click by accessible name
    expect(screen.getByTestId('qty')).toHaveTextContent('2');   // state updated, UI updated
  });

  test('does not go below the minimum', async () => {
    const user = userEvent.setup();
    render(<QuantitySelector min={1} />);
    await user.click(screen.getByRole('button', { name: 'Decrease' })); // try to go below 1
    expect(screen.getByTestId('qty')).toHaveTextContent('1');   // still 1
  });

  test('disables + at the maximum', async () => {
    const user = userEvent.setup();
    render(<QuantitySelector min={1} max={2} />);
    await user.click(screen.getByRole('button', { name: 'Increase' })); // 1 → 2 (max)
    expect(screen.getByRole('button', { name: 'Increase' })).toBeDisabled(); // now disabled
  });
});
```

## 💻 Code Example — Advanced

```jsx
// SearchBox.test.jsx : async behaviour, custom wrapper (providers), timers, and fake functions
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'; // TanStack Query v5
import { SearchBox } from './SearchBox';                                  // uses useQuery inside

// Custom render: wraps UI in the providers the real app has
function renderWithProviders(ui) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },        // do not retry failed calls in tests
  });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

// Replace the real API module with a Jest mock (hoisted above imports by babel-jest)
jest.mock('./api', () => ({ searchRestaurants: jest.fn() }));
import { searchRestaurants } from './api';                // the mocked function

describe('SearchBox', () => {
  beforeEach(() => jest.clearAllMocks());                 // reset call counts between tests

  test('shows results after typing', async () => {
    searchRestaurants.mockResolvedValue([{ id: 1, name: 'Biryani Blues' }]); // fake API reply
    const user = userEvent.setup();
    renderWithProviders(<SearchBox />);

    await user.type(screen.getByRole('searchbox'), 'biryani'); // type like a human
    // findBy waits (default 1s) until the element appears
    expect(await screen.findByText('Biryani Blues')).toBeInTheDocument();
    expect(searchRestaurants).toHaveBeenCalledWith('biryani');  // API got the right argument
  });

  test('shows an error message when the API fails', async () => {
    searchRestaurants.mockRejectedValue(new Error('Network down')); // simulate failure
    const user = userEvent.setup();
    renderWithProviders(<SearchBox />);

    await user.type(screen.getByRole('searchbox'), 'pizza');
    // role="alert" is the accessible way to find error messages
    expect(await screen.findByRole('alert')).toHaveTextContent(/something went wrong/i);
  });

  test('does not call the API for an empty query', async () => {
    renderWithProviders(<SearchBox />);
    // queryBy returns null instead of throwing, so we can assert absence
    expect(screen.queryByRole('list')).not.toBeInTheDocument();
    await waitFor(() => expect(searchRestaurants).not.toHaveBeenCalled());
  });
});
```

```js
// jest.config.js : minimal config for a Vite/CRA-less React project (babel-jest assumed)
module.exports = {
  testEnvironment: 'jsdom',                               // browser-like DOM
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],        // runs before each test file
  moduleNameMapper: { '\\.(css|svg)$': '<rootDir>/__mocks__/fileMock.js' }, // ignore assets
};
// jest.setup.js contains one line:  import '@testing-library/jest-dom';
```

---

## 🟠 Next.js Connection

Next.js ships a Jest helper, `next/jest`, that sets up the SWC transform, handles CSS and image imports, and loads `.env` files. This is the recommended setup for Next.js 13 to 15.

```js
// jest.config.mjs : Next.js recommended config
import nextJest from 'next/jest.js';                       // official helper

const createJestConfig = nextJest({ dir: './' });          // path to the Next.js app

export default createJestConfig({
  testEnvironment: 'jest-environment-jsdom',               // DOM for client components
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],         // import jest-dom here
});
```

```jsx
// Mock the App Router hooks, which need a Next.js runtime that does not exist in Jest
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn(), replace: jest.fn() }), // fake router object
  usePathname: () => '/restaurants',                          // fake current path
  useSearchParams: () => new URLSearchParams('q=pizza'),      // fake query string
}));
```

**Limitation:** Jest and RTL cannot render `async` Server Components (as of Next.js 15, this is documented as unsupported). Test the logic as plain functions, test the Client Components with RTL, and cover whole pages with E2E tests (Playwright or Cypress).

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Testing implementation details (state, class names, internal functions)
✅ **Correct:** Test what the user sees and does

```jsx
// Wrong: depends on internals, breaks on refactor
expect(container.querySelector('.qty-value').className).toBe('qty-value active');

// Right: depends on visible behaviour
expect(screen.getByText('2')).toBeInTheDocument();
```

❌ **Mistake 2:** Using `getByTestId` for everything, or `getBy` to check that something is absent
✅ **Correct:** Prefer `getByRole`, and use `queryBy` for absence, `findBy` for async

```jsx
// Wrong: getBy throws immediately if the element is missing
expect(screen.getByText('Loading')).not.toBeInTheDocument();  // throws, never reaches expect
const btn = screen.getByTestId('submit');                     // not how a user finds it

// Right
expect(screen.queryByText('Loading')).not.toBeInTheDocument(); // null is fine here
const btnRight = screen.getByRole('button', { name: /submit/i }); // also checks accessibility
```

❌ **Mistake 3:** Not awaiting async work, causing flaky tests and "not wrapped in act" warnings
✅ **Correct:** `await` user events and use `findBy` or `waitFor`

```jsx
// Wrong: assertion runs before the fetch finishes
render(<Orders />);
expect(screen.getByText('Order #1')).toBeInTheDocument();     // fails, data not loaded yet

// Right: wait for the element
render(<Orders />);
expect(await screen.findByText('Order #1')).toBeInTheDocument();
```

---

## 🧠 Tricky Interview Question

```jsx
test('toggle', async () => {
  const user = userEvent.setup();
  render(<Toggle />);                                   // <button>{on ? 'ON' : 'OFF'}</button>
  user.click(screen.getByRole('button'));               // NOTE: no await
  expect(screen.getByRole('button')).toHaveTextContent('ON');
});
```
Will this test pass?

**Answer:** It is flaky and normally fails. `user.click` returns a Promise. Without `await`, the assertion runs before the click and the React update are finished, so the button still says `OFF`. The fix is `await user.click(...)`. User Event v14 is async by design (it simulates pointer events step by step), and RTL wraps these in `act` so state updates are flushed before the `await` resolves. Related trap: `fireEvent.click` is synchronous and works without `await`, but it dispatches a single event, not a full user interaction.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Jest and React Testing Library?
A1: Jest is the test runner and assertion library: it finds tests, runs them, mocks modules and reports results. RTL is a set of utilities to render React components and query/interact with the DOM like a user. They are separate; RTL can also run on Vitest.

Q2: Why does RTL discourage testing implementation details?
A2: Tests tied to internal state or class names break on harmless refactors and give false failures, but they can also pass while the real UI is broken. Testing behaviour (text, roles, events) gives tests that survive refactors and match user experience.

Q3: Explain `getBy`, `queryBy` and `findBy`.
A3: `getBy*` returns the element or throws if missing (use when it must exist). `queryBy*` returns `null` if missing (use to assert absence). `findBy*` returns a Promise that waits up to a timeout for the element (use for async UI). The `All` versions return arrays.

Q4: `fireEvent` vs `userEvent`?
A4: `fireEvent` dispatches one low-level DOM event. `userEvent` simulates a full interaction: for typing it fires keydown, keypress, input and keyup, and it respects disabled elements and focus. Prefer `userEvent` (v14: call `userEvent.setup()` and `await` actions).

Q5: How do you test a component that calls an API?
A5: Either mock the module (`jest.mock`) or intercept the network with MSW, then render, await the result with `findBy`, and assert both success and failure states. Disable retries for libraries like TanStack Query in tests so failures appear immediately.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You have business logic in components (forms, carts, filters, validation)
- You want fast feedback in CI and safe refactoring
- You test accessibility-friendly behaviour (roles, labels)

❌ **Avoid when:**
- Testing layout, pixels or animations (use visual tests or Storybook)
- Testing async Server Components or full user journeys across pages (use E2E)
- Snapshot-testing large trees: noisy, nobody reviews the diffs

**Re-render and performance note:** RTL does not measure re-renders, it checks outcomes. A test that asserts "result is correct" is stable even if you add `memo`. For speed, avoid `render` in `beforeAll` shared state, mock heavy modules, and use `jest --watch` or `--onlyChanged` locally. jsdom is far faster than a real browser but lacks layout (no real sizes).

---

## 📊 Visual Diagram

```
 test file                     jsdom (fake browser)             your component
 ─────────                     ───────────────────              ──────────────
 render(<App/>)         ─────►  document.body  ◄─────  React renders here
 screen.getByRole(...)  ─────►  finds DOM node (like a user would)
 await user.click(node) ─────►  dispatches pointer + click events ─► onClick runs
                                                        setState ─► re-render
 expect(...).toBeInTheDocument() ◄── reads updated DOM

 Testing pyramid:      E2E (few, slow)
                     Integration (RTL, many)
                   Unit (pure functions, most, fastest)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Jest | Test runner with assertions and mocks | Test चलाने वाला tool |
| RTL | Library to test components like a user | User की तरह components टेस्ट करने की library |
| jsdom | Fake browser DOM in Node | Node में नकली browser DOM |
| Query | Function to find an element (getBy, queryBy, findBy) | Element ढूँढने का function |
| user-event | Library simulating real user actions | असली user actions simulate करने वाली library |
| Matcher | Assertion helper like toBeDisabled | Assertion का helper |
| Mock | Fake replacement of a function or module | असली की जगह नकली version |
| act | Flushes React updates in tests | Tests में React updates पूरे करवाता है |
| Snapshot | Saved output compared in later runs | Saved output जिससे बाद में तुलना होती है |

---

## ⚡ 3-Line Summary
**English:**
1. Jest runs tests and mocks; React Testing Library renders components and finds elements like a user.
2. Query by role or label, act with user-event (awaited), and assert what the user sees.
3. In Next.js use `next/jest`, mock `next/navigation`, and test async Server Components with E2E instead.

**Hindi:**
1. Jest tests चलाता है और mocks देता है; React Testing Library components render करती है और user की तरह elements ढूँढती है।
2. Role या label से ढूँढो, user-event से (await करके) action करो, और जो user देखता है उसे assert करो।
3. Next.js में `next/jest` इस्तेमाल करो, `next/navigation` को mock करो, और async Server Components को E2E से टेस्ट करो।

---

## ➡️ Next Topic
**153. Unit Testing Components** — अब बारीकी से सीखो कि एक अकेले component को कैसे टेस्ट करें: props, events, conditional rendering, forms और custom hooks, और क्या mock करें व क्या नहीं।
