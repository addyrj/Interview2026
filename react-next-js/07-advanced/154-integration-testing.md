# 154. Integration Testing
# हिंदी में: Integration Testing — कई हिस्सों को साथ में जाँचना

---

## 🔵 Simple Definition (English)
**Integration testing** checks that several parts of your app work correctly together: for example a page with a search box, a list, a Redux store or React Query cache, and a cart, with only the network faked. It tests a whole user flow instead of a single component.

## 🔵 सरल परिभाषा (Hindi)
**Integration testing** जाँचती है कि आपके app के कई हिस्से साथ में सही काम करते हैं: जैसे search box, list, Redux store या React Query cache और cart वाला page, जिसमें सिर्फ network नकली हो। यह एक अकेले component की जगह पूरे user flow को टेस्ट करती है।

---

## 🔴 Problem it Solves

Every component can pass its own unit tests, yet the app still breaks: the search box sends `q` but the list reads `query`, or the cart slice expects `id` while the dish card sends `dishId`. These bugs live in the gaps between parts. Full E2E tests would find them but are slow and flaky. Integration tests sit in the middle: fast like unit tests (jsdom, no real browser or server) and realistic enough to catch wiring mistakes.

## 🔴 यह क्यों बना? (Hindi)
हर component अपने unit tests पास कर सकता है, फिर भी app टूट सकता है: search box `q` भेजता है पर list `query` पढ़ती है, या cart slice `id` माँगती है जबकि dish card `dishId` भेजता है। ऐसे bugs हिस्सों के बीच की जगह में छिपे होते हैं। पूरे E2E tests इन्हें पकड़ लेते हैं पर धीमे और flaky होते हैं। Integration tests बीच में बैठते हैं: unit tests जैसे तेज़ (jsdom, असली browser या server नहीं) और wiring की गलतियाँ पकड़ने जितने असली।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose a user flow: "search a dish, add it to cart, see the cart total"
Step 2 → Build a renderWithProviders helper: real store, real router, real query client
Step 3 → Render a big unit: the page or feature (not every tiny piece)
Step 4 → Fake ONLY the outside world: HTTP (with MSW), not your reducers or hooks
Step 5 → Drive the flow with user-event: type, click, select
Step 6 → Assert at the end of each meaningful step (result list, cart badge, total)
Step 7 → Use a fresh store/cache per test so tests stay independent
Step 8 → Keep a small number of these (they cost more than unit tests)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → एक user flow चुनो: "dish search करो, cart में डालो, cart total देखो"
Step 2 → renderWithProviders helper बनाओ: असली store, असली router, असली query client
Step 3 → बड़ी इकाई render करो: page या feature (हर छोटा हिस्सा नहीं)
Step 4 → सिर्फ बाहरी दुनिया नकली करो: HTTP (MSW से), अपने reducers या hooks नहीं
Step 5 → user-event से flow चलाओ: type, click, select
Step 6 → हर ज़रूरी चरण के बाद assert करो (result list, cart badge, total)
Step 7 → हर test में नया store/cache रखो ताकि tests independent रहें
Step 8 → इनकी संख्या कम रखो (ये unit tests से महँगे हैं)
```

---

## 🟡 Real World Example
**Swiggy menu to cart flow.** The user opens a restaurant page. The menu loads from `/api/menu/42`. The user types "paneer" in the dish filter, the list narrows to two dishes, the user clicks ADD on "Paneer Tikka", and the header cart badge shows `1` and the cart drawer shows ₹250. This involves the menu list, filter input, Redux cart slice, header badge and drawer, all in one test. A unit test per component would never notice if the badge subscribed to the wrong slice.

## 🟡 Real Example Hindi mein
**Swiggy का menu से cart तक flow।** User restaurant page खोलता है। Menu `/api/menu/42` से load होता है। User dish filter में "paneer" लिखता है, list दो dishes तक घट जाती है, user "Paneer Tikka" पर ADD दबाता है, और header के cart badge में `1` और cart drawer में ₹250 दिखता है। इसमें menu list, filter input, Redux cart slice, header badge और drawer सब एक ही test में शामिल हैं। हर component के अलग unit test को कभी पता नहीं चलता कि badge गलत slice को subscribe कर रहा है।

---

## 💻 Code Example — Basic

```jsx
// A tiny feature: filter input + list + counter, sharing state through the parent
import { useState } from 'react';

export function DishList({ dishes }) {
  const [filter, setFilter] = useState('');                  // shared state used by both children
  const [cartCount, setCartCount] = useState(0);             // cart badge state
  const visible = dishes.filter((d) =>                       // filtering logic
    d.name.toLowerCase().includes(filter.toLowerCase())
  );
  return (
    <div>
      <p aria-label="cart count">Cart: {cartCount}</p>       {/* badge */}
      <label htmlFor="f">Filter</label>
      <input id="f" value={filter} onChange={(e) => setFilter(e.target.value)} />
      <ul>
        {visible.map((d) => (
          <li key={d.id}>
            {d.name}
            <button onClick={() => setCartCount((c) => c + 1)}>Add {d.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

```jsx
// DishList.integration.test.jsx : filter + list + badge working together
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { DishList } from './DishList';

test('filter narrows the list and adding updates the cart badge', async () => {
  const user = userEvent.setup();
  const dishes = [
    { id: 1, name: 'Paneer Tikka' },
    { id: 2, name: 'Paneer Butter Masala' },
    { id: 3, name: 'Veg Biryani' },
  ];
  render(<DishList dishes={dishes} />);                                  // one render, whole feature

  await user.type(screen.getByLabelText('Filter'), 'biryani');           // step 1: filter
  expect(screen.getAllByRole('listitem')).toHaveLength(1);                // only one dish remains
  expect(screen.queryByText(/Paneer/)).not.toBeInTheDocument();           // others are gone

  await user.click(screen.getByRole('button', { name: 'Add Veg Biryani' })); // step 2: add
  expect(screen.getByLabelText('cart count')).toHaveTextContent('Cart: 1');  // step 3: badge updates
});
```

## 💻 Code Example — Advanced

```jsx
// test-utils.jsx : one helper that wires every provider, reused by all integration tests
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';                       // Redux Toolkit store provider
import { configureStore } from '@reduxjs/toolkit';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'; // v5
import { MemoryRouter } from 'react-router-dom';              // fake URL history for tests
import cartReducer from './store/cartSlice';                  // REAL reducers (not mocked)

export function renderWithProviders(ui, { route = '/', preloadedState } = {}) {
  const store = configureStore({ reducer: { cart: cartReducer }, preloadedState }); // fresh store per test
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } }, // no retries, no stale cache between tests
  });
  const utils = render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
      </QueryClientProvider>
    </Provider>
  );
  return { store, queryClient, ...utils };                    // tests can inspect the store if needed
}
```

```jsx
// RestaurantPage.integration.test.jsx : MSW fakes HTTP, everything else is real
import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { setupServer } from 'msw/node';                       // MSW v2 server for Node/Jest
import { http, HttpResponse } from 'msw';
import { renderWithProviders } from './test-utils';
import { RestaurantPage } from './RestaurantPage';            // menu + filter + header + cart drawer

const server = setupServer(                                   // default network behaviour
  http.get('/api/menu/42', () =>
    HttpResponse.json([
      { id: 1, name: 'Paneer Tikka', price: 250 },
      { id: 2, name: 'Veg Biryani', price: 180 },
    ])
  )
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' })); // unknown requests fail loudly
afterEach(() => server.resetHandlers());                         // undo per-test overrides
afterAll(() => server.close());                                  // clean up

test('user adds a dish and sees the right cart total', async () => {
  const user = userEvent.setup();
  renderWithProviders(<RestaurantPage id="42" />, { route: '/restaurant/42' });

  // Wait for the menu (loading state → data)
  expect(screen.getByText(/loading menu/i)).toBeInTheDocument();
  await user.click(await screen.findByRole('button', { name: /add paneer tikka/i }));
  await user.click(screen.getByRole('button', { name: /add paneer tikka/i })); // quantity 2

  await user.click(screen.getByRole('button', { name: /open cart/i }));        // open the drawer
  const drawer = screen.getByRole('dialog', { name: /your cart/i });
  expect(within(drawer).getByText('Paneer Tikka x 2')).toBeInTheDocument();    // line item
  expect(within(drawer).getByText('Total: ₹500')).toBeInTheDocument();          // 2 x 250
});

test('shows an error and lets the user retry when the menu fails', async () => {
  // Override the default handler for THIS test only
  server.use(http.get('/api/menu/42', () => new HttpResponse(null, { status: 500 })));
  const user = userEvent.setup();
  renderWithProviders(<RestaurantPage id="42" />);

  expect(await screen.findByRole('alert')).toHaveTextContent(/could not load/i);

  server.resetHandlers();                                       // network "recovers"
  await user.click(screen.getByRole('button', { name: /retry/i }));
  expect(await screen.findByText('Veg Biryani')).toBeInTheDocument();
});
```

---

## 🟠 Next.js Connection

For App Router apps, integration tests with RTL work well for the **client side of a page**: a Client Component tree plus the store and query cache. Server Components that fetch data cannot be rendered by RTL, so the usual split is:

- **Integration (Jest/Vitest + RTL + MSW):** client trees. Pass the data that the server component would fetch as props, or seed the TanStack Query cache.
- **E2E (Playwright):** the real server + client flow including routing, Server Components and Server Actions.

```jsx
// Seeding data the Server Component would normally fetch, then testing the client tree
import { renderWithProviders } from './test-utils';
import { MenuClient } from './MenuClient';                 // 'use client' component used by app/restaurant/[id]/page.jsx

test('MenuClient filters server-provided dishes', async () => {
  const initialDishes = [{ id: 1, name: 'Paneer Tikka', price: 250 }]; // what page.jsx would pass as props
  renderWithProviders(<MenuClient initialDishes={initialDishes} />);
  expect(screen.getByText('Paneer Tikka')).toBeInTheDocument();
});
```

MSW works with Next.js fetch in Node tests, but Next.js patches `fetch` for caching; behaviour in tests may differ between versions (version-dependent), so keep cache concerns in E2E.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mocking the Redux store, hooks or reducers in an integration test
✅ **Correct:** Use the real store and reducers, fake only the network

```jsx
// Wrong: the cart logic is mocked, so you are not testing integration at all
jest.mock('./store/cartSlice');
jest.mock('./hooks/useCart');

// Right: real store through the helper, MSW for HTTP
renderWithProviders(<RestaurantPage id="42" />);
```

❌ **Mistake 2:** Sharing one store or QueryClient between tests (state leaks)
✅ **Correct:** Create them inside the render helper, one per test

```jsx
// Wrong: module-level singletons keep data from the previous test
const queryClient = new QueryClient();
const store = configureStore({ reducer: { cart: cartReducer } });

// Right: new instances for every render
function renderApp(ui) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const st = configureStore({ reducer: { cart: cartReducer } });
  return render(<Provider store={st}><QueryClientProvider client={qc}>{ui}</QueryClientProvider></Provider>);
}
```

❌ **Mistake 3:** Sleeping with fixed delays (`setTimeout`, `sleep(1000)`) to wait for data
✅ **Correct:** Wait for a visible condition with `findBy` or `waitFor`

```jsx
// Wrong: slow and flaky
await new Promise((r) => setTimeout(r, 1000));
expect(screen.getByText('Paneer Tikka')).toBeInTheDocument();

// Right: waits only as long as needed
expect(await screen.findByText('Paneer Tikka')).toBeInTheDocument();
```

---

## 🧠 Tricky Interview Question

```jsx
test('shows items', async () => {
  renderWithProviders(<Menu />);                        // Menu uses useQuery with default retry
  server.use(http.get('/api/menu', () => new HttpResponse(null, { status: 500 })));
  expect(await screen.findByRole('alert')).toBeInTheDocument();
});
```
This test takes about 7 seconds and sometimes times out. Why?

**Answer:** TanStack Query retries failed queries 3 times by default, with exponential backoff (1s, 2s, 4s), so the error state only appears after about 7 seconds, longer than `findBy`'s default 1 second timeout. Create the test `QueryClient` with `retry: false`. A second subtle bug: the handler is added after `render`, so the first request may already have used the default handler. Register `server.use(...)` before rendering. Always build the test environment so failures show immediately.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between unit, integration and E2E tests?
A1: Unit tests check one piece in isolation, integration tests check several pieces together with only external systems faked, and E2E tests drive the real app in a real browser against real (or staging) services. Cost and flakiness rise from unit to E2E, speed falls.

Q2: What should be real and what should be fake in an integration test?
A2: Real: components, hooks, store, router, validation, query cache. Fake: HTTP (via MSW), time, randomness, browser APIs that jsdom lacks (e.g. `IntersectionObserver`, `matchMedia`).

Q3: Why use MSW instead of mocking `fetch` or axios?
A3: MSW intercepts at the network level, so your real fetch/axios/React Query code runs unchanged. Tests stay valid if you swap the HTTP library, and the same handlers can be reused in Storybook and the browser during development.

Q4: How do you keep integration tests fast and non-flaky?
A4: Fresh store and cache per test, `retry: false`, no fixed sleeps (use `findBy`), fake timers for debounce, `onUnhandledRequest: 'error'` to catch unexpected calls, and keep the count small by testing important flows only.

Q5: How do you integration test routing?
A5: Wrap the UI in `MemoryRouter` (React Router) with `initialEntries`, click links, and assert the new content. For Next.js App Router, mock `next/navigation` for client tests, and use Playwright for true navigation tests.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A feature involves several components plus shared state (cart, auth, filters)
- You want to verify wiring between UI, store and API layer
- A bug appeared at the boundary of two parts

❌ **Avoid when:**
- Simple pure components (unit tests are enough and cheaper)
- You need real browser behaviour: layout, scroll, real CSS, cookies (use E2E)
- You would be re-testing every unit test again at a higher cost

**Re-render and performance note:** Integration tests render big trees, so they are slower (tens to hundreds of ms each). A fresh `QueryClient` and store per test avoids cross-test leaks. You can assert on the result of re-renders (badge updated) without counting renders. Slow suites usually mean too many integration tests or heavy real timers.

---

## 📊 Visual Diagram

```
                    ┌────────────────────────────────────────────┐
  user-event ─────► │ <RestaurantPage>                           │
  (click, type)     │   ├─ <FilterInput>  ─┐                     │
                    │   ├─ <MenuList>   ◄──┤  REAL components    │
                    │   ├─ <HeaderBadge> ◄─┤  + REAL Redux store │
                    │   └─ <CartDrawer>  ◄─┘  + REAL query cache │
                    └──────────────┬─────────────────────────────┘
                                   │ fetch('/api/menu/42')
                              ┌────▼─────┐
                              │   MSW    │  ← the ONLY fake: network
                              └──────────┘
  Pyramid:   E2E (few) → Integration (some) → Unit (many)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Integration test | Tests several parts working together | कई हिस्सों का साथ में टेस्ट |
| E2E test | Full app in a real browser | असली browser में पूरा app |
| MSW | Mock Service Worker, mocks at network level | Network स्तर पर नकली server |
| Test double | Fake object replacing a real dependency | असली की जगह नकली चीज़ |
| Test pyramid | Many unit, fewer integration, fewest E2E | Tests की संख्या का पिरामिड |
| Flaky test | Test that passes and fails randomly | कभी पास कभी फेल होने वाला test |
| MemoryRouter | Router with in-memory history for tests | Tests के लिए memory वाला router |
| Seeding | Pre-filling store or cache with data | Store या cache में पहले से data भरना |

---

## ⚡ 3-Line Summary
**English:**
1. Integration tests render a feature with real components, store and cache, and fake only the network.
2. Build a `renderWithProviders` helper, use a fresh store and QueryClient per test, and wait with `findBy`.
3. In Next.js, test client trees with RTL and MSW, and leave Server Components to Playwright E2E tests.

**Hindi:**
1. Integration tests असली components, store और cache के साथ feature render करते हैं, और सिर्फ network नकली रखते हैं।
2. `renderWithProviders` helper बनाओ, हर test में नया store और QueryClient रखो, और `findBy` से इंतज़ार करो।
3. Next.js में client trees को RTL और MSW से टेस्ट करो, और Server Components को Playwright E2E tests के लिए छोड़ो।

---

## ➡️ Next Topic
**155. Mocking API in Tests** — Integration tests में network नकली करना सबसे ज़रूरी हिस्सा है। अगला topic बताता है कि `jest.mock`, `fetch` mock और MSW में क्या फर्क है और कब कौन सा चुनें।
