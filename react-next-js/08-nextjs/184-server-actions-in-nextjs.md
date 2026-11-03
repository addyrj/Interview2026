# 184. Server Actions in Next.js
# हिंदी में: Next.js Server Actions — बिना API route के server पर चलने वाले functions

---

## 🔵 Simple Definition (English)
A **Server Action** is an async function marked with `'use server'` that runs on the server but can be called directly from a form or a Client Component. Next.js creates the HTTP endpoint for you, so you can mutate data without writing a separate API route.

## 🔵 सरल परिभाषा (Hindi)
**Server Action** एक async function है जिस पर `'use server'` लगा होता है; वह server पर चलता है लेकिन form या Client Component से सीधे call हो सकता है। Next.js खुद HTTP endpoint बना देता है, इसलिए data बदलने के लिए अलग API route लिखने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves

To submit a form you used to write: a client `onSubmit`, a `fetch` call, a Route Handler, JSON parsing, error handling, then manually refresh the UI. Forms did not work without JavaScript. Server Actions collapse this into one function, support progressive enhancement (the form works before JS loads), and can refresh cached data with `revalidatePath` in the same step.

```jsx
// PROBLEM: lots of plumbing
// client: onSubmit → fetch('/api/cart', {method:'POST', body}) → setState
// server: app/api/cart/route.js → parse → validate → DB

// SOLUTION: one function
'use server';
export async function addToCart(formData) { /* runs on the server */ }
```

## 🔴 यह क्यों बना? (Hindi)
Form submit करने के लिए पहले लिखना पड़ता था: client का `onSubmit`, `fetch` call, Route Handler, JSON parsing, error handling, और फिर UI हाथ से refresh करना। JavaScript के बिना forms चलते भी नहीं थे। Server Actions यह सब एक function में समेट देते हैं, progressive enhancement देते हैं (JS load होने से पहले भी form चलता है), और उसी step में `revalidatePath` से cached data refresh कर देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write an async function with 'use server' (top of file, or inside the function)
Step 2 → Pass it to <form action={fn}> or call it from an event handler / useTransition
Step 3 → On submit the browser (or React) sends a POST request to Next.js with the arguments
Step 4 → Next.js runs the function on the server, with access to DB, cookies(), secrets
Step 5 → Inside, validate the input and check authentication (never trust the client)
Step 6 → Call revalidatePath('/cart') or revalidateTag(...) to refresh cached data
Step 7 → Optionally redirect() or return a result object; React updates the UI with the new data
Step 8 → useActionState holds the returned state; useFormStatus shows the pending state

Server Actions are public HTTP endpoints: treat them like API routes for security
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → 'use server' वाला async function लिखो (file के ऊपर, या function के अंदर)
Step 2 → उसे <form action={fn}> को दो या event handler / useTransition से call करो
Step 3 → Submit पर browser (या React) arguments के साथ Next.js को POST request भेजता है
Step 4 → Next.js function को server पर चलाता है, जहाँ DB, cookies(), secrets उपलब्ध हैं
Step 5 → अंदर input validate करो और authentication check करो (client पर भरोसा मत करो)
Step 6 → cached data refresh करने के लिए revalidatePath('/cart') या revalidateTag(...) call करो
Step 7 → चाहो तो redirect() करो या result object return करो; React नए data से UI update करता है
Step 8 → useActionState returned state रखता है; useFormStatus pending state दिखाता है

Server Actions public HTTP endpoints हैं: security के लिए इन्हें API routes जैसा ही समझो
```

---

## 🟡 Real World Example
**Amazon "Add to cart" and Zomato review form:** Pressing "Add to cart" calls a Server Action that checks the logged-in user from the cookie, inserts the item into the database, and revalidates the cart page so the badge count updates. The review form validates the rating on the server, returns field errors if invalid, and shows a "Submitting..." button state while pending, without writing any `/api/reviews` route.

## 🟡 Real Example Hindi mein
**Amazon "Add to cart" और Zomato review form:** "Add to cart" दबाने पर एक Server Action चलता है जो cookie से logged-in user देखता है, item database में डालता है, और cart page को revalidate करता है ताकि badge की गिनती update हो। Review form server पर rating validate करता है, गलती हो तो field errors लौटाता है, और pending होने पर बटन पर "Submitting..." दिखाता है, बिना कोई `/api/reviews` route लिखे।

---

## 💻 Code Example — Basic

```jsx
// app/feedback/actions.js: the Server Action
'use server';                                          // everything exported here runs on the server

export async function sendFeedback(formData) {         // form passes a FormData object
  const message = formData.get('message');             // read the input named "message"
  if (!message || message.length < 3) return;          // minimal validation (see advanced for errors)
  console.log('Saving feedback:', message);            // replace with a database insert
}
```

```jsx
// app/feedback/page.jsx: a Server Component using the action in a plain form
import { sendFeedback } from './actions';              // import the server function

export default function FeedbackPage() {
  return (
    <form action={sendFeedback}>                       {/* works even before JavaScript loads */}
      <textarea name="message" placeholder="Your feedback" /> {/* name is the FormData key */}
      <button type="submit">Send</button>
    </form>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// app/reviews/actions.js: validation, auth check, revalidation, returned state
'use server';
import { revalidatePath } from 'next/cache';           // refresh cached pages
import { cookies } from 'next/headers';                // read the session cookie
import { z } from 'zod';                               // validation library (npm i zod)

const schema = z.object({
  restaurantId: z.string().min(1),                     // required id
  rating: z.coerce.number().int().min(1).max(5),       // string → number 1..5
  comment: z.string().min(5, 'Write at least 5 characters').max(500),
});

// useActionState passes (previousState, formData)
export async function addReview(prevState, formData) {
  const session = (await cookies()).get('session')?.value; // Next.js 15+: cookies() is async
  if (!session) return { ok: false, errors: { _form: ['Please log in'] } }; // always check auth

  const parsed = schema.safeParse(Object.fromEntries(formData)); // validate on the server
  if (!parsed.success) {
    return { ok: false, errors: parsed.error.flatten().fieldErrors }; // return errors, do not throw
  }

  // await db.review.create({ data: { ...parsed.data, userId } }); // real DB write (see topic 185)
  revalidatePath(`/restaurants/${parsed.data.restaurantId}`);       // refresh the restaurant page
  return { ok: true, errors: {} };                     // success state
}
```

```jsx
// app/reviews/ReviewForm.jsx: Client Component with pending + error UI
'use client';
import { useActionState } from 'react';                // React 19 (Next.js 15 App Router). In React 18 canary it was useFormState
import { useFormStatus } from 'react-dom';             // pending state of the parent form
import { addReview } from './actions';

function SubmitButton() {
  const { pending } = useFormStatus();                 // true while the action is running
  return <button type="submit" disabled={pending}>{pending ? 'Submitting...' : 'Post review'}</button>;
}

export default function ReviewForm({ restaurantId }) {
  const [state, formAction] = useActionState(addReview, { ok: false, errors: {} }); // state from the action
  return (
    <form action={formAction}>                         {/* formAction wraps addReview */}
      <input type="hidden" name="restaurantId" value={restaurantId} /> {/* extra data via hidden input */}
      <select name="rating" defaultValue="5">
        {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n} stars</option>)}
      </select>
      <textarea name="comment" />
      {state.errors.comment && <p role="alert">{state.errors.comment[0]}</p>} {/* field error */}
      {state.errors._form && <p role="alert">{state.errors._form[0]}</p>}     {/* general error */}
      {state.ok && <p>Thanks for your review!</p>}
      <SubmitButton />
    </form>
  );
}
```

---

## 🟠 Real App Integration

Call an action outside a form with `useTransition`, and update the UI instantly with `useOptimistic` for actions like "like" or "add to cart".

```jsx
// app/cart/AddButton.jsx: call a Server Action from an event handler
'use client';
import { useTransition } from 'react';                  // marks the call as a non-urgent transition
import { addToCart } from './cartActions';              // 'use server' function (hypothetical)

export default function AddButton({ productId }) {
  const [isPending, startTransition] = useTransition(); // isPending while the action runs
  return (
    <button
      disabled={isPending}                              // block double clicks
      onClick={() => startTransition(async () => { await addToCart(productId); })} // async transition (React 19)
    >
      {isPending ? 'Adding...' : 'Add to cart'}
    </button>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not checking authentication or validating input inside the action
✅ **Correct:** Treat every action as a public endpoint: authenticate, authorize and validate

```jsx
// Wrong: anyone can delete any order by calling the action with another id
'use server';
export async function deleteOrder(id) {
  await db.order.delete({ where: { id } });             // ❌ no auth, no ownership check
}

// Right
'use server';
export async function deleteOrder(id) {
  const user = await getCurrentUser();                  // ✅ who is calling?
  if (!user) throw new Error('Unauthorized');
  await db.order.deleteMany({ where: { id, userId: user.id } }); // ✅ only own orders
  revalidatePath('/orders');
}
```

❌ **Mistake 2:** Forgetting to revalidate, so the UI keeps showing old data
✅ **Correct:** Call `revalidatePath` or `revalidateTag` after the mutation

```jsx
// Wrong: data is saved but the list on screen is stale
export async function addItem(fd) { await db.item.create({ data: { name: fd.get('name') } }); } // ❌

// Right
export async function addItem(fd) {
  await db.item.create({ data: { name: fd.get('name') } });
  revalidatePath('/items');                             // ✅ refresh the cached page
}
```

---

## 🧠 Tricky Interview Question

```jsx
// app/page.jsx (Server Component)
export default function Page() {
  async function save(formData) {
    'use server';
    console.log('saved', formData.get('name'));
  }
  const secret = process.env.API_KEY;
  return <form action={save}><input name="name" /><button>Save</button></form>;
}
```
**Answer:** This works. An inline Server Action inside a Server Component is allowed with the directive inside the function body. Two traps: (1) the action is a public endpoint, so it must validate and authorize; (2) variables from the enclosing scope that the action closes over (such as `secret` if used inside) are serialized and encrypted by Next.js, but you should still not rely on closures for sensitive data; read secrets from `process.env` inside the action. Inline actions are not allowed in Client Components; there you must import the action from a separate `'use server'` file.

---

## ⚫ Interview Questions + Answers

Q1: What is a Server Action?
A1: An async function with `'use server'` that executes on the server and can be invoked from forms or client code. Next.js generates the POST endpoint and handles serialization.

Q2: How do Server Actions differ from Route Handlers?
A2: Server Actions are meant for mutations triggered by your own UI, integrate with forms and cache revalidation, and are called as functions. Route Handlers are generic HTTP endpoints for external clients and webhooks, and also serve GET.

Q3: Are Server Actions secure by default?
A3: No. They are public HTTP endpoints. Next.js adds CSRF protection (origin checks) and encrypted closure variables, but you must still authenticate, authorize and validate inputs.

Q4: What do `useActionState`, `useFormStatus` and `useOptimistic` do?
A4: `useActionState` stores the action's returned state (errors, success). `useFormStatus` gives the pending status of the parent form. `useOptimistic` shows an immediate optimistic UI before the server confirms. (`useActionState` is React 19; older canaries named it `useFormState`.)

Q5: How does the UI update after an action?
A5: Call `revalidatePath` or `revalidateTag` (or `redirect`) in the action; Next.js re-renders the affected Server Components and sends the new UI in the same response.

---

## 🔷 When to Use + When Not to Use
✅ **Use Server Actions when:**
- Submitting forms and mutating data from your own UI
- You want progressive enhancement and less boilerplate
- You need automatic cache revalidation after a write

❌ **Avoid when:**
- External clients (mobile apps, partners, webhooks) must call the endpoint (use Route Handlers)
- You need to read data (use Server Components or Route Handlers; actions run one at a time, sequentially)
- You need streaming responses or custom HTTP behavior

---

## 📊 Visual Diagram

```
  <form action={addReview}>   (Client or Server Component)
        │ submit (POST, FormData)
        ▼
  ┌──────────────────────────────────┐
  │ Server: addReview(prev, formData)│
  │  1 check session                 │
  │  2 validate (zod)                │
  │  3 write to DB                   │
  │  4 revalidatePath('/restaurants')│
  │  5 return { ok, errors }         │
  └────────────┬─────────────────────┘
               ▼ response: new state + fresh Server Component output
  React updates: useActionState state, page data refreshed

  Re-render behavior: the form component re-renders when the returned state
  changes; only revalidated Server Components re-render with new data.
  Performance: one round trip does mutation plus data refresh; actions run
  sequentially, so avoid using them for parallel reads.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server Action | Server function callable from UI | UI से call होने वाला server function |
| 'use server' | Directive marking server functions | Server functions का directive |
| FormData | Browser form data object | Form data का object |
| revalidatePath | Refresh cache for a path | किसी path का cache refresh |
| useActionState | Hook for action result state | Action के नतीजे की state का hook |
| useFormStatus | Hook for form pending state | Form के pending का hook |
| useOptimistic | Show expected result instantly | अपेक्षित नतीजा तुरंत दिखाना |
| Progressive enhancement | Works before JS loads | JS load होने से पहले भी काम |

---

## ⚡ 3-Line Summary
**English:**
1. Server Actions are `'use server'` async functions that run on the server and can be used directly in forms or event handlers.
2. They remove API boilerplate, support progressive enhancement and revalidate cached data after writes.
3. They are public endpoints, so always authenticate, authorize and validate inside them.

**Hindi:**
1. Server Actions `'use server'` वाले async functions हैं जो server पर चलते हैं और सीधे forms या event handlers में इस्तेमाल होते हैं।
2. ये API का boilerplate हटाते हैं, progressive enhancement देते हैं और writes के बाद cached data revalidate करते हैं।
3. ये public endpoints हैं, इसलिए अंदर हमेशा authenticate, authorize और validate करो।

---

## ➡️ Next Topic
**185. Next.js + Prisma + PostgreSQL** — Prisma ORM से PostgreSQL database जोड़ना, schema, migrations, client singleton और Server Components/Actions में queries चलाना।
