# 155. Mocking API in Tests
# हिंदी में: Tests में API को Mock करना

---

## 🔵 Simple Definition (English)
**Mocking an API in tests** means replacing real network calls with fake, controlled responses, so tests are fast, repeatable and do not need a real server. You can mock at three levels: the function (`jest.fn`), `fetch` itself, or the network layer (MSW).

## 🔵 सरल परिभाषा (Hindi)
**Tests में API mock करना** का मतलब है असली network calls की जगह नकली, नियंत्रित responses लगाना, ताकि tests तेज़ और दोहराने योग्य हों और असली server की ज़रूरत न पड़े। Mock तीन स्तर पर हो सकता है: function (`jest.fn`), `fetch` खुद, या network layer (MSW)।

---

## 🔴 Problem it Solves

Real APIs are slow, change over time, need login, can be down, and cost money (payment, SMS). A test that calls the real Zomato API fails when the internet drops, and you cannot easily make it return a 500 error or an empty list on demand. Mocking gives you control: any status code, any delay, any data, and every run gives the same result.

## 🔴 यह क्यों बना? (Hindi)
असली APIs धीमी होती हैं, समय के साथ बदलती हैं, login माँगती हैं, down हो सकती हैं और पैसे भी खर्च कराती हैं (payment, SMS)। असली Zomato API को call करने वाला test internet जाने पर fail हो जाता है, और आप उसे आसानी से 500 error या खाली list वापस करने को मजबूर नहीं कर सकते। Mocking आपको नियंत्रण देती है: कोई भी status code, कोई भी delay, कोई भी data, और हर run में वही नतीजा।

---

## 🟢 How it Works — Step by Step

```
Level 1: Mock the module        jest.mock('./api')        replace your own api functions
Level 2: Mock global fetch      jest.spyOn(global,'fetch') replace fetch itself
Level 3: Mock the network       MSW (Mock Service Worker)  intercepts real requests

Step 1 → Decide what the component calls (fetch, axios, a useQuery wrapper)
Step 2 → Choose the level (prefer MSW for integration, jest.mock for quick unit tests)
Step 3 → Define the fake response for the happy path
Step 4 → Define error, empty, slow and malformed responses too
Step 5 → Render, act, and assert on what the user sees
Step 6 → Reset mocks after each test so they do not leak
Step 7 → Optionally assert the request itself (URL, method, body, headers)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Level 1: Module mock           jest.mock('./api')         अपने api functions बदल दो
Level 2: Global fetch mock     jest.spyOn(global,'fetch') fetch खुद बदल दो
Level 3: Network mock          MSW (Mock Service Worker)  असली requests को रोक लेता है

Step 1 → तय करो कि component क्या call करता है (fetch, axios, useQuery wrapper)
Step 2 → स्तर चुनो (integration के लिए MSW बेहतर, जल्दी unit tests के लिए jest.mock)
Step 3 → Happy path का नकली response बनाओ
Step 4 → Error, empty, slow और malformed responses भी बनाओ
Step 5 → Render करो, action करो, और जो user देखता है उसे assert करो
Step 6 → हर test के बाद mocks reset करो ताकि leak न हो
Step 7 → चाहो तो request को भी assert करो (URL, method, body, headers)
```

---

## 🟡 Real World Example
**Flipkart product search.** The search page calls `GET /api/search?q=phone`. Tests need: a normal result with 3 phones, an empty result ("No products found"), a 500 server error ("Something went wrong, retry"), a slow response (skeleton loader visible), and a 401 (redirect to login). With MSW each scenario is a few lines, and the same component code runs unchanged. The team also checks that typing "phone" sends exactly one request with `q=phone` after the debounce.

## 🟡 Real Example Hindi mein
**Flipkart product search।** Search page `GET /api/search?q=phone` call करता है। Tests को चाहिए: 3 phones वाला normal result, खाली result ("No products found"), 500 server error ("Something went wrong, retry"), धीमा response (skeleton loader दिखे), और 401 (login पर redirect)। MSW से हर scenario कुछ ही lines में बनता है, और component का code वैसा ही चलता है। Team यह भी जाँचती है कि "phone" टाइप करने पर debounce के बाद ठीक एक request `q=phone` के साथ जाती है।

---

## 💻 Code Example — Basic

```jsx
// ProductSearch.jsx : calls fetch directly
import { useEffect, useState } from 'react';

export function ProductSearch({ query }) {
  const [state, setState] = useState({ status: 'loading', items: [] }); // one state object for status + data
  useEffect(() => {
    let ignore = false;                                   // avoid setting state after unmount / stale query
    setState({ status: 'loading', items: [] });
    fetch(`/api/search?q=${encodeURIComponent(query)}`)   // real network call
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status))))
      .then((items) => { if (!ignore) setState({ status: 'done', items }); })
      .catch(() => { if (!ignore) setState({ status: 'error', items: [] }); });
    return () => { ignore = true; };                      // cleanup on query change
  }, [query]);

  if (state.status === 'loading') return <p>Loading...</p>;
  if (state.status === 'error') return <p role="alert">Something went wrong</p>;
  if (state.items.length === 0) return <p>No products found</p>;
  return <ul>{state.items.map((p) => <li key={p.id}>{p.name}</li>)}</ul>;
}
```

```jsx
// ProductSearch.test.jsx : Level 2, mocking global fetch with jest.spyOn
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProductSearch } from './ProductSearch';

// Helper creates a minimal fake Response (only what the component uses)
const okResponse = (data) => ({ ok: true, status: 200, json: async () => data });

afterEach(() => jest.restoreAllMocks());                  // put the real fetch back

test('renders products from the API', async () => {
  jest.spyOn(global, 'fetch').mockResolvedValue(okResponse([{ id: 1, name: 'Moto G' }]));
  render(<ProductSearch query="phone" />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();          // first render: loading
  expect(await screen.findByText('Moto G')).toBeInTheDocument();       // then the data
  expect(global.fetch).toHaveBeenCalledWith('/api/search?q=phone');    // correct URL
});

test('shows an error on a failed request', async () => {
  jest.spyOn(global, 'fetch').mockResolvedValue({ ok: false, status: 500 }); // server error
  render(<ProductSearch query="phone" />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Something went wrong');
});

test('shows empty state', async () => {
  jest.spyOn(global, 'fetch').mockResolvedValue(okResponse([]));       // empty list
  render(<ProductSearch query="zzz" />);
  expect(await screen.findByText('No products found')).toBeInTheDocument();
});
```

## 💻 Code Example — Advanced

```js
// mocks/handlers.js : MSW v2 handlers shared by Jest, Storybook and the browser dev server
import { http, HttpResponse, delay } from 'msw';

export const handlers = [
  http.get('/api/search', ({ request }) => {              // access the real Request object
    const q = new URL(request.url).searchParams.get('q'); // read the query string
    if (q === 'zzz') return HttpResponse.json([]);        // empty result for a special query
    return HttpResponse.json([{ id: 1, name: `${q} Pro` }]);
  }),

  http.post('/api/orders', async ({ request }) => {       // check the request body too
    const body = await request.json();
    if (!body.items?.length) {
      return HttpResponse.json({ message: 'Cart is empty' }, { status: 422 });
    }
    await delay(150);                                     // simulate latency (MSW v2 helper)
    return HttpResponse.json({ orderId: 'ORD-1001' }, { status: 201 });
  }),
];
```

```js
// jest.setup.js : start the server for every test file (Node environment)
import '@testing-library/jest-dom';
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

export const server = setupServer(...handlers);          // build the server from shared handlers

beforeAll(() => server.listen({ onUnhandledRequest: 'error' })); // unknown calls = test failure
afterEach(() => server.resetHandlers());                 // remove per-test overrides
afterAll(() => server.close());                          // stop intercepting
// Note: jsdom may lack global fetch/Response in older Jest setups; Node 18+ provides them,
// but jest-environment-jsdom may need polyfills (version-dependent).
```

```jsx
// Checkout.test.jsx : overriding handlers per test, asserting the outgoing request
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '../jest.setup';
import { Checkout } from './Checkout';

test('sends the cart in the request body and shows the order id', async () => {
  let captured;                                           // will hold the body the app sent
  server.use(
    http.post('/api/orders', async ({ request }) => {     // override for this test only
      captured = await request.json();                    // record the request payload
      return HttpResponse.json({ orderId: 'ORD-7' }, { status: 201 });
    })
  );
  const user = userEvent.setup();
  render(<Checkout items={[{ id: 1, qty: 2 }]} />);
  await user.click(screen.getByRole('button', { name: /place order/i }));
  expect(await screen.findByText(/ORD-7/)).toBeInTheDocument();       // UI result
  expect(captured).toEqual({ items: [{ id: 1, qty: 2 }] });           // request contract
});

test('shows the server validation message', async () => {
  server.use(
    http.post('/api/orders', () =>
      HttpResponse.json({ message: 'Payment declined' }, { status: 402 })
    )
  );
  const user = userEvent.setup();
  render(<Checkout items={[{ id: 1, qty: 1 }]} />);
  await user.click(screen.getByRole('button', { name: /place order/i }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Payment declined');
});
```

```js
// Level 1 reference: jest.mock on your own API module (fast unit tests)
jest.mock('./api');                                       // auto-mocks every export of ./api
import { getProducts } from './api';
getProducts.mockResolvedValueOnce([{ id: 1, name: 'Moto G' }]); // first call returns data
getProducts.mockRejectedValueOnce(new Error('boom'));           // second call rejects
```

---

## 🟠 Next.js Connection

In Next.js, API calls happen in several places and each needs a plan:

- **Client Components:** same as React. Use MSW (Node server) in Jest/Vitest.
- **Route Handlers (`app/api/.../route.js`):** they are plain functions that take a `Request` and return a `Response`, so you can unit test them directly without a server.
- **Server Components and Server Actions:** async Server Components cannot be rendered by RTL. Test the data-fetching function separately (mock `fetch` or use MSW), and cover the rendered page with Playwright, using `page.route()` to mock network calls from the browser (server-side fetches are not visible to `page.route`).

```js
// app/api/search/route.test.js : testing a Route Handler directly (no server needed)
import { GET } from './route';                              // exported handler function

test('returns products for a query', async () => {
  const req = new Request('http://localhost/api/search?q=phone'); // standard Web Request
  const res = await GET(req);                                      // call the handler
  expect(res.status).toBe(200);                                    // status check
  const data = await res.json();                                   // parse body
  expect(Array.isArray(data)).toBe(true);
});
```

Next.js extends `fetch` with caching options (`cache`, `next.revalidate`); how this behaves under test is version-dependent, so avoid asserting on caching in unit tests.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to restore or reset mocks, so one test affects the next
✅ **Correct:** Reset in `afterEach`

```jsx
// Wrong: mockResolvedValue from test A still applies in test B
jest.spyOn(global, 'fetch').mockResolvedValue(okResponse([]));

// Right: clean up automatically
afterEach(() => { jest.restoreAllMocks(); });             // for spies
// and for MSW:  afterEach(() => server.resetHandlers());
```

❌ **Mistake 2:** Mocking so much that the test only proves the mock works
✅ **Correct:** Mock the outermost boundary (network), keep your code real

```jsx
// Wrong: mocking the hook that contains all the logic you wanted to test
jest.mock('./useProducts', () => ({ useProducts: () => ({ data: [{ id: 1 }], isLoading: false }) }));

// Right: let useProducts (and React Query) run for real, mock only the HTTP response
server.use(http.get('/api/products', () => HttpResponse.json([{ id: 1, name: 'Moto G' }])));
```

❌ **Mistake 3:** Mock data that does not match the real API shape (contract drift)
✅ **Correct:** Build mocks from shared types, schemas or recorded real responses

```jsx
// Wrong: the real API returns { items: [...] } but the mock returns an array,
// the tests pass while production breaks
HttpResponse.json([{ id: 1 }]);

// Right: one shared factory, typed or validated (e.g. with zod) so changes fail loudly
const productListMock = () => ({ items: [{ id: 1, name: 'Moto G', price: 12999 }] });
HttpResponse.json(productListMock());
```

---

## 🧠 Tricky Interview Question

```jsx
jest.spyOn(global, 'fetch').mockResolvedValue({ json: async () => [{ id: 1, name: 'Moto G' }] });

render(<ProductSearch query="phone" />);        // component checks r.ok before r.json()
expect(await screen.findByText('Moto G')).toBeInTheDocument();
```
Does this pass?

**Answer:** No. The fake response has no `ok` property, so `r.ok` is `undefined` (falsy). The component takes the error branch and renders "Something went wrong", so `findByText('Moto G')` times out. This is the danger of hand-made fake responses: they must mimic the properties the code reads (`ok`, `status`, `json()`). MSW avoids this because it returns real `Response` objects, so `ok`, `headers` and `status` behave as in production.

---

## ⚫ Interview Questions + Answers

Q1: Why mock APIs in tests?
A1: To make tests fast, deterministic and independent of the network or server state, to easily simulate errors, empty data and delays, and to avoid side effects like real payments or emails.

Q2: Compare `jest.mock`, `jest.spyOn(fetch)` and MSW.
A2: `jest.mock` replaces your own module; it is quick but bypasses your fetch code. Spying on `fetch` fakes the global function; you must hand-craft Response-like objects. MSW intercepts real requests at the network level, so all your client code runs; it needs a little setup but gives the most realistic and reusable mocks. For integration tests, prefer MSW.

Q3: How do you test loading, success and error states?
A3: Render and immediately assert the loading UI, then `await findBy...` for success. For errors, override the handler with `server.use(...)` to return a 500, or make the mock reject, and assert the error message. Disable retries in React Query so the error appears quickly.

Q4: How do you verify what request your app sent?
A4: In MSW, read `request.url`, `request.json()` or headers inside the handler and store them, then assert. With `jest.fn`/`fetch` spies use `toHaveBeenCalledWith`. Assert the request only when the contract matters (for example POST bodies).

Q5: What is the risk of mocks and how do you reduce it?
A5: Mocks can drift from the real API, so tests pass but production fails. Reduce this with shared types or schemas, contract tests (such as Pact), recorded real responses, and a few E2E tests against a staging backend.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The code calls external services (payment, maps, SMS, your backend)
- You need to reproduce error, empty, slow or unusual responses
- Tests must run offline and quickly in CI

❌ **Avoid when:**
- You are verifying the real backend contract (use contract or E2E tests)
- The mock is more complex than the code it replaces
- You mock your own pure functions just to be able to assert calls

**Re-render and performance note:** A mocked API resolves almost instantly, so the loading state may flash for only one tick; always assert loading synchronously after `render`, before awaiting. Use `delay()` in MSW to test slow networks and skeleton loaders. Mocks make suites much faster than hitting real APIs (milliseconds instead of seconds per call).

---

## 📊 Visual Diagram

```
  Component ──► fetch('/api/search?q=phone')
                   │
      ┌────────────┼──────────────────────────────┐
      │ Level 1    │ Level 2           Level 3    │
      │ jest.mock  │ spyOn(fetch)      MSW        │
      │ api.js     │ fake Response     real-looking│
      │ replaced   │ object            network      │
      └────────────┼──────────────────────────────┘
                   ▼
             Fake response (200 / 404 / 500 / [] / slow)
                   ▼
          Component renders loading → success | error | empty

  More realistic ─────────────────────────────► Less setup
  MSW (L3)                 fetch spy (L2)        jest.mock (L1)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mock | Fake stand-in with controlled behaviour | नियंत्रित व्यवहार वाला नकली विकल्प |
| Stub | Fake that only returns canned data | सिर्फ तैयार data लौटाने वाला नकली |
| Spy | Wrapper that records calls to a real function | Calls को record करने वाला wrapper |
| MSW | Library mocking requests at the network level | Network स्तर पर requests mock करने वाली library |
| Handler | MSW rule: which request gets which response | कौन सी request को कौन सा response |
| Contract | Agreed shape of requests and responses | Request/response की तय बनावट |
| Latency | Delay in a response | Response में देरी |
| Route Handler | Next.js API function in app/api | Next.js का API function |

---

## ⚡ 3-Line Summary
**English:**
1. Mock APIs to make tests fast, repeatable and able to simulate errors, empty data and delays.
2. Prefer MSW for realistic network-level mocks; use `jest.mock` or `fetch` spies for quick unit tests.
3. Reset mocks after each test, keep mock data matching the real contract, and test Next.js Route Handlers directly.

**Hindi:**
1. APIs mock करो ताकि tests तेज़ और दोहराने योग्य हों, और errors, खाली data व delays simulate हो सकें।
2. असली network-level mocks के लिए MSW चुनो; जल्दी unit tests के लिए `jest.mock` या `fetch` spies इस्तेमाल करो।
3. हर test के बाद mocks reset करो, mock data को असली contract जैसा रखो, और Next.js Route Handlers को सीधे टेस्ट करो।

---

## ➡️ Next Topic
**156. Accessibility in React (a11y)** — Tests में हमने `getByRole` और labels इस्तेमाल किए। अब सीखो कि वही roles, labels और keyboard support असल में अपने components में कैसे बनाएँ ताकि हर user app चला सके।
