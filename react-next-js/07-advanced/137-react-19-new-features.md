# 137. React 19 — New Features
# हिंदी में: React 19 — नए Features (Actions, use, useOptimistic, ref as prop)

---

## 🔵 Simple Definition (English)
**React 19** (stable since December 2024) makes forms and async work first-class. It adds **Actions** (async functions in transitions), the hooks `useActionState`, `useFormStatus`, `useOptimistic`, the `use` API for reading promises and context, `ref` as a normal prop, document metadata tags, and stable Server Components and Server Actions.

## 🔵 सरल परिभाषा (Hindi)
**React 19** (दिसंबर 2024 से stable) forms और async काम को आसान बनाता है। इसमें **Actions** (transition में async functions), `useActionState`, `useFormStatus`, `useOptimistic` hooks, promise व context पढ़ने के लिए `use` API, `ref` का सामान्य prop बनना, document metadata tags, और stable Server Components व Server Actions आते हैं।

---

## 🔴 Problem it Solves

In React 18 a form submit needed lots of boilerplate: `useState` for loading, error and data, `e.preventDefault()`, a `try/catch`, manual reset, and manual optimistic UI. `forwardRef` was awkward, and reading a promise in render needed libraries.

```jsx
// PROBLEM (React 18): manual pending/error/data state for every form
const [pending, setPending] = useState(false);   // loading flag
const [error, setError] = useState(null);        // error message
async function onSubmit(e) {
  e.preventDefault();                            // stop browser submit
  setPending(true);                              // show spinner
  try { await save(new FormData(e.target)); }    // call API
  catch (err) { setError(err.message); }         // store error
  finally { setPending(false); }                 // hide spinner
}
```

## 🔴 यह क्यों बना? (Hindi)
React 18 में form submit के लिए बहुत boilerplate लगता था: loading, error, data के `useState`, `e.preventDefault()`, `try/catch`, manual reset, और हाथ से optimistic UI। `forwardRef` भी अटपटा था, और render में promise पढ़ने के लिए libraries चाहिए थीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → <form action={fn}> accepts a function. React calls it with FormData on submit
Step 2 → The function runs inside a transition (an "Action"): React tracks pending state for you
Step 3 → useActionState(fn, initial) returns [state, formAction, isPending]
Step 4 → useFormStatus() in a child of the form reads { pending } without prop drilling
Step 5 → useOptimistic(value) shows the expected result at once, auto-reverts on error
Step 6 → use(promise) suspends until the promise resolves; use(context) works even after if/loops
Step 7 → ref is a plain prop in function components; ref callbacks may return a cleanup function
Step 8 → On success React auto-resets uncontrolled form fields

Re-render behavior: pending, state and optimistic value change in the same transition, batched.
Performance impact: less state/effect code, fewer renders; compiler (separate) can memoise further.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <form action={fn}> function लेता है। Submit पर React उसे FormData के साथ call करता है
Step 2 → Function transition (एक "Action") में चलता है: pending state React खुद track करता है
Step 3 → useActionState(fn, initial) [state, formAction, isPending] देता है
Step 4 → Form के child में useFormStatus() बिना prop drilling के { pending } पढ़ता है
Step 5 → useOptimistic(value) अपेक्षित नतीजा तुरंत दिखाता है, error पर अपने-आप लौट जाता है
Step 6 → use(promise) promise के resolve होने तक suspend करता है; use(context) if/loop के बाद भी चलता है
Step 7 → Function components में ref सामान्य prop है; ref callback cleanup function लौटा सकता है
Step 8 → सफल होने पर React uncontrolled form fields अपने-आप reset करता है

Re-render behavior: pending, state और optimistic value एक ही transition में batch होकर बदलते हैं।
Performance impact: कम state/effect code, कम renders; compiler (अलग topic) और memoise कर सकता है।
```

---

## 🟡 Real World Example
**Swiggy "Add to cart" and checkout form:** When you tap "+" on a dish, the cart count must change instantly even though the server call takes 800 ms. `useOptimistic` shows the new count immediately and rolls back if the server rejects it. The "Apply coupon" form uses `useActionState`: it shows "Invalid coupon" from the returned state and disables the button while pending via `useFormStatus`.

## 🟡 Real Example Hindi mein
**Swiggy "Add to cart" और checkout form:** Dish पर "+" दबाने पर cart count तुरंत बदलना चाहिए, भले ही server call में 800 ms लगें। `useOptimistic` नया count तुरंत दिखाता है और server मना करे तो वापस कर देता है। "Apply coupon" form `useActionState` इस्तेमाल करता है: returned state से "Invalid coupon" दिखाता है और `useFormStatus` से pending में button disable रखता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: form action + useActionState + useFormStatus (React 19)
import { useActionState } from 'react';                  // React 19 hook
import { useFormStatus } from 'react-dom';               // read parent form pending state
import { createRoot } from 'react-dom/client';

// Fake API: pretend to validate a coupon on the server
async function applyCouponApi(code) {
  await new Promise((r) => setTimeout(r, 600));          // simulate network delay
  return code === 'SWIGGY50' ? { ok: true } : { ok: false };
}

// Submit button reads pending state from the nearest <form>, no props needed
function SubmitButton() {
  const { pending } = useFormStatus();                   // must be used inside a <form> child
  return <button disabled={pending}>{pending ? 'Applying...' : 'Apply'}</button>;
}

function CouponForm() {
  // action receives (previousState, formData); returned value becomes the new state
  const [state, formAction] = useActionState(async (prev, formData) => {
    const code = formData.get('code');                   // read the input by its name
    const res = await applyCouponApi(code);              // call the API
    return res.ok ? { message: `Coupon ${code} applied` } : { message: 'Invalid coupon' };
  }, { message: '' });                                   // initial state

  return (
    <form action={formAction}>                           {/* function as action, no onSubmit */}
      <input name="code" placeholder="Coupon code" />    {/* name is used by FormData */}
      <SubmitButton />
      <p>{state.message}</p>                             {/* result from the action */}
    </form>
  );
}

createRoot(document.getElementById('root')).render(<CouponForm />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: optimistic cart, use() with a promise, ref as prop, <title> metadata
import { Suspense, use, useOptimistic, useState, useTransition } from 'react';
import { createRoot } from 'react-dom/client';

// ref as a prop: no forwardRef needed in React 19
function FancyInput({ ref, ...props }) {
  return <input ref={ref} {...props} />;                 // ref arrives like any other prop
}

// use(): read a promise created OUTSIDE render (e.g. passed from a parent or a cache)
function RestaurantName({ promise }) {
  const restaurant = use(promise);                       // suspends until resolved; throws if rejected
  return (
    <>
      <title>{restaurant.name} | Swiggy</title>          {/* React 19 hoists this to <head> */}
      <h2>{restaurant.name}</h2>
    </>
  );
}

// Optimistic cart count
function Cart({ initialCount, saveToServer }) {
  const [count, setCount] = useState(initialCount);                 // real (confirmed) value
  const [optimisticCount, addOptimistic] = useOptimistic(           // temporary value
    count,
    (current, delta) => current + delta                             // how to apply an optimistic change
  );
  const [, startTransition] = useTransition();                      // actions run inside a transition

  function add() {
    startTransition(async () => {                                   // async Action (new in 19)
      addOptimistic(1);                                             // UI shows +1 immediately
      const saved = await saveToServer(count + 1);                  // slow network call
      setCount(saved);                                              // confirm; if it throws, optimistic reverts
    });
  }
  return <button onClick={add}>Cart ({optimisticCount})</button>;
}

const restaurantPromise = new Promise((r) => setTimeout(() => r({ name: 'Meghana Foods' }), 500)); // created once, outside render

function App() {
  return (
    <>
      <Suspense fallback={<p>Loading restaurant...</p>}>
        <RestaurantName promise={restaurantPromise} />
      </Suspense>
      <Cart initialCount={0} saveToServer={async (n) => { await new Promise((r) => setTimeout(r, 800)); return n; }} />
      <FancyInput placeholder="Notes for the chef" />
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

---

## 🟠 Next.js Connection

Next.js 15 requires React 19 for the App Router. **Server Actions** are the server-side version of form Actions: a function marked `'use server'` is passed to `<form action>` and runs on the server, even before JavaScript loads (progressive enhancement). Next.js 15 also made `params` and `searchParams` Promises, which you read with `await` (server) or `use` (client).

```jsx
// app/actions.js
'use server';                                              // all exports run on the server only
export async function addToCart(prevState, formData) {
  const id = formData.get('dishId');                       // read hidden field
  // await db.cart.add(id);                                // your data layer (hypothetical)
  return { message: `Added dish ${id}` };                  // becomes the new state
}
```

```jsx
// app/menu/AddForm.jsx
'use client';                                              // useActionState is a client hook
import { useActionState } from 'react';
import { addToCart } from '../actions';                    // Server Action import

export default function AddForm({ dishId }) {
  const [state, action, isPending] = useActionState(addToCart, { message: '' }); // wire the action
  return (
    <form action={action}>
      <input type="hidden" name="dishId" value={dishId} /> {/* sent inside FormData */}
      <button disabled={isPending}>Add</button>
      <p>{state.message}</p>
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating a new promise inside the component and passing it to `use`
✅ **Correct:** Create the promise outside render (or in a Server Component / cache) so its identity is stable

```jsx
// Wrong: new promise every render → suspends forever / infinite loop
function Menu() {
  const data = use(fetch('/api/menu').then((r) => r.json()));   // ❌
  return <p>{data.length}</p>;
}

// Right: promise comes from a parent or a cache
function Menu({ menuPromise }) {
  const data = use(menuPromise);                                // ✅
  return <p>{data.length}</p>;
}
```

❌ **Mistake 2:** Calling `useFormStatus` in the same component that renders the `<form>`
✅ **Correct:** Call it in a child component rendered inside the form

```jsx
// Wrong: this component renders the form, so there is no parent form to read
function Form() {
  const { pending } = useFormStatus();    // ❌ always false
  return <form action={act}><button disabled={pending}>Go</button></form>;
}
// Right: move the button into its own child (see SubmitButton above)   ✅
```

❌ **Mistake 3:** Still using `forwardRef`, `propTypes` and `ReactDOM.render` expecting them to work
✅ **Correct:** `ref` as a prop; use TypeScript for types; `createRoot`

```jsx
// Wrong in 19: propTypes are ignored, ReactDOM.render and string refs are removed
Button.propTypes = { label: String };    // ❌ silently ignored

// Right: TypeScript types or runtime validation (zod) at boundaries
function Button({ label, ref }) { return <button ref={ref}>{label}</button>; } // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Demo({ flag }) {
  if (flag) {
    const theme = use(ThemeContext);   // does this throw?
    return <p>{theme}</p>;
  }
  return null;
}
```
**Answer:** It works. Unlike hooks, `use` may be called inside `if` statements and loops. That is its main difference from `useContext`. The restriction is that it must still be called inside a component or a hook, not in an event handler. Also, `use` with a promise must receive a promise with a stable identity, and `use` cannot be called inside a `try/catch` for suspense (use an Error Boundary instead).

---

## ⚫ Interview Questions + Answers

Q1: What are Actions in React 19?
A1: Async functions run inside a transition. React manages pending state, errors (with Error Boundaries), optimistic updates and form resets for you. You pass them to `<form action>`, `<button formAction>` or call them inside `startTransition`.

Q2: What does `use` do and how is it different from `useContext`?
A2: `use(resource)` reads a promise (suspending until it resolves) or a context. Unlike hooks it can be called conditionally. For context it behaves like `useContext` but without the ordering restriction.

Q3: How does `useOptimistic` work?
A3: It returns a temporary value derived from the real state and a function to change it. While an Action is pending the temporary value is shown. When the action finishes (success or failure) React drops the temporary value and shows the real state, so failures roll back automatically.

Q4: What changed about `ref`?
A4: Function components receive `ref` as a normal prop, so `forwardRef` is no longer needed (it will be deprecated). Ref callbacks can return a cleanup function, which replaces the old pattern of calling the callback with `null`.

Q5: What other notable changes are in React 19?
A5: `<Context>` works as a provider directly (no `.Provider`), document metadata (`<title>`, `<meta>`, `<link>`) renders from any component, stylesheets and scripts get precedence and de-duplication, better hydration error messages, custom elements support, and removed APIs (`propTypes`, `defaultProps` on functions, legacy context, `ReactDOM.render`). Details of some items can vary by minor version: check the official upgrade guide.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You build forms (login, checkout, coupons) and want less state boilerplate
- You need optimistic updates (likes, cart, comments)
- You use Next.js 15 / Server Components and Server Actions

❌ **Avoid when:**
- Your libraries do not yet support React 19 (check peer dependencies first)
- You need complex client-side validation with many interactions (a form library may still fit better)
- You create promises in render for `use` (use a data library or Server Components instead)

---

## 📊 Visual Diagram

```
  <form action={fn}>
        │ submit
        ▼
  startTransition(async () => { ... })     ← an "Action"
        │            │              │
        │            │              └─► useOptimistic: show expected UI NOW
        │            └─► useFormStatus: pending = true in children
        ▼
  useActionState: [state, formAction, isPending]
        │ success                │ error
        ▼                        ▼
  new state + form reset     Error Boundary + optimistic value rolls back
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Action | Async function run in a transition | Transition में चलने वाला async function |
| useActionState | State + action + pending for forms | Form का state, action और pending |
| useFormStatus | Read parent form pending state | Parent form की pending स्थिति |
| useOptimistic | Show expected result before server replies | Server से पहले अपेक्षित नतीजा दिखाना |
| use | Read promise or context in render | Render में promise/context पढ़ना |
| Server Action | Server function called from client | Client से बुलाया जाने वाला server function |
| ref as prop | ref passed like any prop | ref का सामान्य prop बनना |
| Metadata hoisting | title/meta moved to head | title/meta का head में जाना |

---

## ⚡ 3-Line Summary
**English:**
1. React 19 adds Actions, `useActionState`, `useFormStatus`, `useOptimistic` and `use` to remove form and async boilerplate.
2. `ref` is a normal prop, metadata tags work anywhere, and Server Components and Actions are stable.
3. Create promises outside render, call `useFormStatus` in a child of the form, and check library compatibility before upgrading.

**Hindi:**
1. React 19 में Actions, `useActionState`, `useFormStatus`, `useOptimistic` और `use` form व async का boilerplate हटाते हैं।
2. `ref` सामान्य prop है, metadata tags कहीं भी चलते हैं, और Server Components व Actions stable हैं।
3. Promise render के बाहर बनाओ, `useFormStatus` form के child में बुलाओ, और upgrade से पहले libraries की compatibility जाँचो।

---

## ➡️ Next Topic
**138. Server Components (RSC)** — Actions और `use` का असली फायदा तब दिखता है जब components server पर चलते हैं। RSC समझना Next.js App Router की नींव है।
