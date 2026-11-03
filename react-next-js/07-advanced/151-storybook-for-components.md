# 151. Storybook for Components
# हिंदी में: Storybook — Components को अलग से बनाना, देखना और टेस्ट करना

---

## 🔵 Simple Definition (English)
**Storybook** is a tool that lets you build, view and test UI components in isolation, outside your real app. Each component gets "stories": saved examples of it in different states (loading, error, empty, disabled). It also works as living documentation for your design system.

## 🔵 सरल परिभाषा (Hindi)
**Storybook** एक tool है जिसमें आप components को अपने असली app के बाहर, अलग से बनाते, देखते और टेस्ट करते हैं। हर component की "stories" होती हैं: अलग-अलग states (loading, error, empty, disabled) के saved examples। यह design system की जीती-जागती documentation का भी काम करता है।

---

## 🔴 Problem it Solves

When you build a `PaymentButton` inside a real app, to see its "failed payment" state you must log in, add items to the cart, go to checkout and force a failure. This is slow. Edge cases (very long names, 0 items, slow network) are rarely checked, so bugs reach production. Designers and QA also cannot review a component without running the whole app and backend. Storybook gives every component a small sandbox where each state is one click away, with no backend needed.

```
WITHOUT Storybook:  login → add to cart → checkout → force error → finally see the error button
WITH Storybook:     open "PaymentButton / Failed" story → see it instantly
```

## 🔴 यह क्यों बना? (Hindi)
जब आप असली app के अंदर `PaymentButton` बनाते हैं, तो उसकी "failed payment" state देखने के लिए आपको login करना, cart में items डालना, checkout जाना और error force करना पड़ता है। यह धीमा है। Edge cases (बहुत लंबा नाम, 0 items, slow network) कम ही चेक होते हैं, इसलिए bugs production तक पहुँच जाते हैं। Designers और QA भी पूरे app और backend के बिना component review नहीं कर सकते। Storybook हर component को एक छोटा sandbox देता है जहाँ हर state एक click दूर है, backend की ज़रूरत नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install Storybook in your project: npx storybook@latest init
Step 2 → Storybook detects your framework (React + Vite, or Next.js) and creates a .storybook/ folder
Step 3 → Write a "stories file" next to a component: Button.stories.jsx
Step 4 → The default export (meta) says which component and where it appears in the sidebar
Step 5 → Each named export is one story = the component with specific args (props)
Step 6 → Run npm run storybook → opens a browser UI with a sidebar of all components
Step 7 → "Controls" panel lets you change props live, "Actions" panel logs callbacks
Step 8 → Optional: "play" functions simulate clicks, and the test runner runs stories as tests
Step 9 → Publish with npm run build-storybook → static site for designers, QA, the team
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Project में Storybook install करो: npx storybook@latest init
Step 2 → Storybook आपका framework (React + Vite, या Next.js) पहचानकर .storybook/ folder बनाता है
Step 3 → Component के पास "stories file" लिखो: Button.stories.jsx
Step 4 → Default export (meta) बताता है कि कौन सा component है और sidebar में कहाँ दिखेगा
Step 5 → हर named export एक story है = कुछ खास args (props) के साथ component
Step 6 → npm run storybook चलाओ → browser में सारे components की sidebar वाला UI खुलता है
Step 7 → "Controls" panel से props live बदलो, "Actions" panel callbacks को log करता है
Step 8 → Optional: "play" functions clicks simulate करते हैं, और test runner stories को tests की तरह चलाता है
Step 9 → npm run build-storybook से static site बनाओ, designers, QA और team के लिए publish करो
```

---

## 🟡 Real World Example
**Swiggy restaurant card:** The design team defines one `RestaurantCard`. Its states are: normal, "Closed now" (greyed out), "Promoted", "50% OFF" offer badge, very long restaurant name, and missing image. In Storybook each state is a story. A designer opens the published Storybook link, checks all six states on mobile and desktop widths, and approves, without asking an engineer to run the app. Later, a visual regression tool (Chromatic) compares screenshots of every story on each pull request and flags accidental changes.

## 🟡 Real Example Hindi mein
**Swiggy restaurant card:** Design team एक `RestaurantCard` तय करती है। उसकी states हैं: normal, "Closed now" (धुंधला), "Promoted", "50% OFF" offer badge, बहुत लंबा restaurant नाम, और image नहीं। Storybook में हर state एक story है। Designer published Storybook link खोलकर mobile और desktop widths पर सारी छह states देखता है और approve करता है, engineer से app चलवाए बिना। बाद में visual regression tool (Chromatic) हर pull request पर हर story के screenshots compare करके अनचाहे बदलाव पकड़ता है।

---

## 💻 Code Example — Basic

```jsx
// RestaurantCard.jsx : the component we want to document
export function RestaurantCard({ name, rating, eta, closed = false, onOpen }) { // props with a default
  return (
    <div
      style={{ border: '1px solid #ddd', padding: 12, opacity: closed ? 0.5 : 1 }} // grey out when closed
    >
      <h3>{name}</h3>                                   {/* restaurant name */}
      <p>{rating} stars • {eta} min</p>                 {/* rating and delivery time */}
      <button disabled={closed} onClick={onOpen}>       {/* cannot open a closed restaurant */}
        {closed ? 'Closed now' : 'View menu'}           {/* label depends on state */}
      </button>
    </div>
  );
}
```

```jsx
// RestaurantCard.stories.jsx : Storybook 8 style (CSF3 = Component Story Format 3)
import { fn } from '@storybook/test';                   // spy function, shown in the Actions panel (SB 8; in SB 9 it is 'storybook/test')
import { RestaurantCard } from './RestaurantCard';      // component under documentation

// META: describes the whole file
const meta = {
  title: 'Cards/RestaurantCard',                        // sidebar path: Cards > RestaurantCard
  component: RestaurantCard,                            // enables auto docs and controls
  tags: ['autodocs'],                                   // generate a Docs page automatically
  args: { onOpen: fn() },                               // default arg: logs every click
  argTypes: {
    rating: { control: { type: 'number', min: 1, max: 5, step: 0.1 } }, // slider-like control
  },
};
export default meta;                                    // required default export

// Each named export is ONE story (one state of the component)
export const Normal = {                                 // story 1: default look
  args: { name: 'Meghana Foods', rating: 4.5, eta: 30 },// props for this story
};

export const Closed = {                                 // story 2: closed restaurant
  args: { ...Normal.args, closed: true },               // reuse Normal args, override one
};

export const LongName = {                               // story 3: edge case, layout stress test
  args: {
    ...Normal.args,
    name: 'The Very Long Named Restaurant & Kitchen of South Indian Specialities',
  },
};
```

## 💻 Code Example — Advanced

```jsx
// CartDrawer.stories.jsx : real-world story with decorators, MSW mocking and a play function
import { expect, userEvent, within } from '@storybook/test'; // testing helpers inside Storybook (SB 8 path)
import { http, HttpResponse } from 'msw';                    // mock the network (needs msw-storybook-addon)
import { Provider } from 'react-redux';                      // the component reads from Redux
import { configureStore } from '@reduxjs/toolkit';           // build a tiny store per story
import cartReducer from './cartSlice';                       // real reducer, fake data
import { CartDrawer } from './CartDrawer';                   // component under test

// Helper: a fresh store with initial items so stories do not share state
const makeStore = (items) =>
  configureStore({ reducer: { cart: cartReducer }, preloadedState: { cart: { items } } });

const meta = {
  title: 'Checkout/CartDrawer',
  component: CartDrawer,
  parameters: { layout: 'fullscreen' },                 // remove default padding for a drawer
};
export default meta;

export const WithItems = {
  // Decorator wraps the story: gives it a Redux store, like the real app does
  decorators: [
    (Story) => (
      <Provider store={makeStore([{ id: 1, name: 'Butter Chicken', qty: 2, price: 320 }])}>
        <Story />                                       {/* the actual story is rendered here */}
      </Provider>
    ),
  ],
  parameters: {
    msw: {                                              // network mocks used only for this story
      handlers: [
        http.post('/api/coupon', () => HttpResponse.json({ discount: 50 })), // fake coupon API
      ],
    },
  },
  // play = automated user interaction after the story renders (also acts as a test)
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);               // scope queries to this story only
    await userEvent.type(canvas.getByPlaceholderText('Coupon'), 'SAVE50'); // type a coupon code
    await userEvent.click(canvas.getByRole('button', { name: /apply/i })); // click Apply
    // findBy waits for the async mocked response before asserting
    await expect(await canvas.findByText('Discount: ₹50')).toBeInTheDocument();
  },
};

export const EmptyCart = {
  decorators: [(Story) => <Provider store={makeStore([])}><Story /></Provider>], // empty state
};
```

```js
// .storybook/main.js : minimal config for React + Vite (Storybook 8)
export default {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],     // where to find story files
  addons: ['@storybook/addon-essentials', '@storybook/addon-a11y'], // controls, docs, a11y checks
  framework: { name: '@storybook/react-vite', options: {} }, // build with Vite
};
```

---

## 🟠 Next.js Connection

Storybook has an official Next.js framework package, `@storybook/nextjs` (Webpack/SWC based) and, in newer versions, `@storybook/nextjs-vite`. It mocks `next/image`, `next/link`, `next/navigation` and `next/font`, so components using them render in Storybook. Which package and mocks are available is **version-dependent** (Storybook 8 vs 9), so check the docs for your version.

Important limit: **async Server Components** (components that `await` data on the server) cannot be rendered in Storybook directly, because Storybook runs in the browser. The usual pattern is to keep server components thin and put the UI in plain presentational components that receive props, then write stories for those.

```jsx
// ProductPage.stories.jsx : story for a component using next/navigation
import { ProductCard } from './ProductCard';           // presentational component (no data fetching)

const meta = {
  title: 'Shop/ProductCard',
  component: ProductCard,
  parameters: {
    nextjs: {
      appDirectory: true,                              // tell the addon we use the App Router
      navigation: { pathname: '/products/phone' },     // fake usePathname() value
    },
  },
};
export default meta;

export const Default = { args: { title: 'iPhone 15', price: 69999 } }; // plain props, no server code
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Writing stories that depend on the real backend or global state
✅ **Correct:** Pass fake data through args, and mock the network with MSW, so stories are deterministic

```jsx
// Wrong: story fetches a real API, so it breaks when the network or server is down
export const Orders = { render: () => <OrderList url="https://api.myapp.com/orders" /> };

// Right: component gets data by props, or the request is mocked
export const OrdersMocked = {
  args: { orders: [{ id: 1, item: 'Pizza', status: 'Delivered' }] }, // fixed fake data
};
```

❌ **Mistake 2:** One huge story with many props instead of small focused stories
✅ **Correct:** One story per meaningful state, and reuse args

```jsx
// Wrong: one story where you must toggle ten controls to see anything useful
export const Everything = { args: { loading: true, error: true, empty: true } };

// Right: separate stories, each named after the state it shows
export const Loading = { args: { loading: true } };
export const ErrorState = { args: { error: 'Payment failed' } };
export const Empty = { args: { items: [] } };
```

❌ **Mistake 3:** Forgetting providers (theme, router, store), so the story crashes
✅ **Correct:** Add them once as global decorators in `.storybook/preview.jsx`

```jsx
// .storybook/preview.jsx : wrap every story with the providers the app uses
import { ThemeProvider } from '../src/theme';          // your app's theme provider

export const decorators = [
  (Story) => (
    <ThemeProvider>                                    {/* same wrapper as in the real app */}
      <Story />
    </ThemeProvider>
  ),
];
```

---

## 🧠 Tricky Interview Question

```jsx
// Counter.stories.jsx
import { useState } from 'react';
import { Counter } from './Counter';        // Counter({ value, onChange }) is a CONTROLLED component

export const Broken = {
  args: { value: 0, onChange: () => {} },   // value is fixed at 0, onChange does nothing
};

export const Working = {
  render: (args) => {
    const [value, setValue] = useState(0);   // hook inside render function
    return <Counter {...args} value={value} onChange={setValue} />;
  },
};
```
What happens when you click "+" in each story?

**Answer:** In `Broken`, the UI does not change: `Counter` is controlled, so it only shows the `value` prop, which is always `0`. The click calls `onChange`, but nothing updates the value. Changing the `value` control in the Controls panel is the only way to move it. In `Working`, a `render` function owns real state, so clicking updates the value and the component re-renders (only `Counter` and its children re-render, since state lives in the story wrapper). Storybook allows hooks inside `render` because it treats it as a component; a lint rule may warn, in which case name the function (`render: function Render(args) {...}`) or wrap in a small component.

---

## ⚫ Interview Questions + Answers

Q1: What is Storybook and why use it?
A1: A tool to develop, document and test UI components in isolation. It speeds up development (no need to reach a state in the real app), documents the design system, helps designers and QA review, and enables visual and interaction testing.

Q2: What is a story and what is CSF3?
A2: A story is one rendered state of a component, defined by args. CSF3 (Component Story Format 3) is the file format: a default export `meta` (title, component) and named exports that are plain objects (`args`, `render`, `play`). It replaced older function-based stories.

Q3: What are args, controls and decorators?
A3: Args are the props given to a story. Controls are auto-generated UI inputs that edit args live. Decorators are wrappers around stories, used for providers (theme, Redux, router) or layout.

Q4: How do you test with Storybook?
A4: Three ways. Interaction tests with `play` functions (using `userEvent` and `expect`), run in the browser or in CI with the test runner. Accessibility checks with the a11y addon (uses axe). Visual regression with tools such as Chromatic that compare screenshots per story. Stories can also be reused in Jest/Vitest tests with `composeStories`.

Q5: How do you handle API calls or Next.js features in stories?
A5: Prefer presentational components that take data through props. For network calls, mock with MSW (`msw-storybook-addon`). For Next.js, use the Next.js framework package, which mocks `next/image`, `next/link` and `next/navigation`. Async Server Components cannot be rendered in Storybook; test their client parts instead.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You maintain a shared component library or design system
- Many states and edge cases must be reviewed by designers and QA
- You want visual regression and accessibility checks per component

❌ **Avoid when:**
- The app is tiny, with a handful of one-off components (maintenance cost is higher than the benefit)
- Stories are not kept updated: stale stories mislead people
- The "component" is really a full page tied to server data (test that with E2E tests instead)

**Performance and re-render note:** Storybook does not affect production bundle size, because it is a dev-time tool with its own build. Inside it, changing a control updates args and re-renders only that story. Use it with React Profiler addons if you want to inspect re-renders per story.

---

## 📊 Visual Diagram

```
 Button.stories.jsx ──┐
 Card.stories.jsx   ──┼──►  Storybook (separate dev server / static site)
 Cart.stories.jsx   ──┘        │
                               ├── Canvas   : the component rendered in isolation
                               ├── Controls : edit props live
                               ├── Actions  : log onClick, onChange
                               ├── Docs     : auto documentation page
                               └── Tests    : play() interactions + a11y + visual diffs

 Real app:   page → API → store → component          (hard to reach every state)
 Storybook:  story → args → component                (every state one click away)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Story | One saved state of a component | Component की एक saved state |
| CSF3 | Component Story Format 3, plain-object stories | Stories लिखने का format |
| Args | Props passed to a story | Story को दिए गए props |
| Controls | Live editing panel for args | Args को live बदलने वाला panel |
| Decorator | Wrapper around a story (providers, layout) | Story के चारों ओर wrapper |
| Play function | Scripted user interaction after render | Render के बाद automated user actions |
| Autodocs | Auto generated documentation page | अपने-आप बना documentation |
| Chromatic | Visual regression service for stories | Stories के screenshots compare करने वाली service |
| MSW | Mock Service Worker, mocks network calls | Network calls को नकली बनाने वाला tool |

---

## ⚡ 3-Line Summary
**English:**
1. Storybook lets you build and test components in isolation, with each state saved as a story.
2. Use args, controls, decorators and play functions to document, mock and test behaviour.
3. Keep components presentational and stories deterministic; async Server Components cannot be rendered in it.

**Hindi:**
1. Storybook में components अलग से बनते और टेस्ट होते हैं, हर state एक story के रूप में सेव रहती है।
2. Documentation, mocking और testing के लिए args, controls, decorators और play functions इस्तेमाल करो।
3. Components को presentational रखो और stories को deterministic; async Server Components इसमें render नहीं हो सकते।

---

## ➡️ Next Topic
**152. Testing in React (Jest + RTL)** — Storybook UI को देखने और interaction test करने में मदद करता है। अब सीखो असली automated tests कैसे लिखते हैं: Jest runner और React Testing Library से components को user की नज़र से टेस्ट करना।
