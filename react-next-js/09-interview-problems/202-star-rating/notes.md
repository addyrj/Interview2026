# 202. Build Star Rating Component
# हिंदी में: Star Rating Component बनाना

> Code: [App.jsx](./App.jsx) (complete, tested with jsdom: click sets rating, click again clears)

---

## 🔵 Simple Definition (English)
A **star rating component** shows a row of stars. The user hovers to preview and clicks to choose a score. It is a classic "controlled component": the parent owns the value, and the component reports changes through `onChange`.

## 🔵 सरल परिभाषा (Hindi)
**Star rating component** तारों की एक row दिखाता है। User hover करके preview देखता है और click करके score चुनता है। यह एक classic "controlled component" है: value parent के पास रहती है, और component बदलाव `onChange` से बताता है।

---

## 🔴 Problem it Solves
Rating inputs need two kinds of state: the saved value and the temporary hover value. Beginners mix them up or duplicate the value inside the component, so the parent and child disagree. This problem tests controlled components, local UI state, event handling, accessibility and reusable props (`max`, `readOnly`).

## 🔴 यह क्यों बना? (Hindi)
Rating input में दो तरह की state चाहिए: saved value और अस्थायी hover value। Beginners इन्हें मिला देते हैं या value को component के अंदर duplicate कर देते हैं, जिससे parent और child में फर्क आ जाता है। यह problem controlled components, local UI state, events, accessibility और reusable props (`max`, `readOnly`) की समझ परखती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Props: value (saved), onChange, max (default 5), readOnly
Step 2 → Local state: hover (0 = none). Displayed stars = hover || value
Step 3 → Render max buttons with role="radio" inside role="radiogroup"
Step 4 → onMouseEnter(star) sets hover; onMouseLeave on the group resets it to 0
Step 5 → onClick calls onChange(star); clicking the current star again calls onChange(0)
Step 6 → Star i is filled when i <= shown, otherwise empty

Re-render: hover changes re-render only StarRating (local state). A click calls the parent's
setter, so the parent and the component re-render once.
Performance: 5 tiny buttons; no memo needed. For a list of 1000 rated items wrap in React.memo.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Props: value (saved), onChange, max (default 5), readOnly
Step 2 → Local state: hover (0 = कोई नहीं)। दिखने वाले stars = hover || value
Step 3 → role="radiogroup" के अंदर role="radio" वाले max buttons render करो
Step 4 → onMouseEnter(star) hover सेट करता है; group का onMouseLeave उसे 0 कर देता है
Step 5 → onClick onChange(star) बुलाता है; वही star दोबारा दबाने पर onChange(0)
Step 6 → Star i तब भरा होता है जब i <= shown, वरना खाली

Re-render: hover बदलने पर सिर्फ StarRating (local state) re-render होता है। Click से parent का
setter चलता है, इसलिए parent और component एक बार re-render होते हैं।
Performance: 5 छोटे buttons; memo की ज़रूरत नहीं। 1000 items की list में React.memo लगाओ।
```

---

## 🟡 Real World Example
**Zomato / Swiggy order review:** After delivery you see "Rate your food". Moving the mouse over the 4th star lights up four stars, leaving the stars returns to your saved rating, and clicking saves it. On the restaurant page the average (4.2) is shown as read-only stars.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy order review:** Delivery के बाद "Rate your food" दिखता है। 4th star पर mouse ले जाओ तो चार stars जल जाते हैं, बाहर निकलो तो saved rating लौट आती है, और click करने पर rating save होती है। Restaurant page पर average (4.2) read-only stars में दिखता है।

---

## 💻 Code Example — Basic

```jsx
// Basic star rating: click only, no hover
import { useState } from 'react';                       // state hook
import { createRoot } from 'react-dom/client';          // root API

function App() {
  const [rating, setRating] = useState(0);              // 0 = not rated yet
  return (
    <div>
      {[1, 2, 3, 4, 5].map((n) => (                     // render 5 stars
        <span
          key={n}                                       // stable key: the star number
          onClick={() => setRating(n)}                  // pass a FUNCTION, do not call setRating(n) here
          style={{ cursor: 'pointer', color: n <= rating ? 'gold' : 'gray' }} // fill up to rating
        >
          ★
        </span>
      ))}
      <p>Rating: {rating}</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Reusable, accessible, controlled component (same as App.jsx)
import { useState } from 'react';

export function StarRating({ value = 0, onChange, max = 5, readOnly = false }) {
  const [hover, setHover] = useState(0);                // preview star
  const shown = hover || value;                         // hover wins while the mouse is inside

  return (
    <div role="radiogroup" aria-label="Rating" onMouseLeave={() => setHover(0)}>
      {Array.from({ length: max }, (_, i) => i + 1).map((star) => (
        <button
          key={star}
          type="button"                                 // never submit a parent form by accident
          role="radio"
          aria-checked={value === star}                 // screen reader state
          aria-label={`${star} star${star > 1 ? 's' : ''}`}
          disabled={readOnly}
          onMouseEnter={() => !readOnly && setHover(star)}
          onClick={() => onChange?.(star === value ? 0 : star)} // same star again clears
          style={{ background: 'none', border: 'none', fontSize: 28,
                   color: star <= shown ? '#f5a623' : '#ccc' }}
        >
          {star <= shown ? '★' : '☆'}
        </button>
      ))}
    </div>
  );
}

// Usage: the parent OWNS the value (controlled component)
// const [rating, setRating] = useState(0);
// <StarRating value={rating} onChange={setRating} />
// <StarRating value={4} readOnly />   // display-only average
```

Extra credit: support half stars by measuring the mouse position inside the star
(`e.nativeEvent.offsetX < width / 2` means a half star) and using step 0.5.

---

## 🟠 Next.js Connection
The read-only display of an average rating needs no state, so it can stay a **Server Component** and send no JavaScript. Only the interactive input needs `'use client'`. Submit the chosen rating with a Server Action so it works with a normal form and validates on the server.

```jsx
// app/orders/[id]/RatingForm.jsx
'use client';                                           // needs hover state and onClick
import { useState } from 'react';
import { StarRating } from './StarRating';
import { submitRating } from './actions';               // 'use server' function

export default function RatingForm({ orderId }) {
  const [rating, setRating] = useState(0);
  return (
    <form action={submitRating}>                        {/* Server Action receives FormData */}
      <input type="hidden" name="orderId" value={orderId} />
      <input type="hidden" name="rating" value={rating} /> {/* carries the chosen value */}
      <StarRating value={rating} onChange={setRating} />
      <button type="submit" disabled={!rating}>Submit</button>
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling the handler instead of passing it
✅ **Correct:** Wrap in an arrow function

```jsx
// Wrong: runs during render → "Too many re-renders"
<span onClick={setRating(n)}>★</span>
// Right
<span onClick={() => setRating(n)}>★</span>
```

❌ **Mistake 2:** Copying `value` into local state (`useState(value)`)
✅ **Correct:** Use the prop directly (controlled) and keep only the hover in local state

```jsx
// Wrong: parent changes value, but the child keeps the old copy
const [rating, setRating] = useState(value);
// Right: read props.value, call props.onChange
```

❌ **Mistake 3:** Using only `<span>` with no keyboard or ARIA support
✅ **Correct:** Use `<button>` elements with `role="radio"` so Tab, Space and screen readers work

```jsx
// Wrong: not focusable, invisible to screen readers
<span onClick={...}>★</span>
// Right
<button type="button" role="radio" aria-checked={value === star}>★</button>
```

---

## 🧠 Tricky Interview Question

```jsx
function Stars() {
  const [rating, setRating] = useState(0);
  return [1, 2, 3].map((n) => (
    <button key={n} onClick={setRating(n)}>{n}</button>
  ));
}
```
**Answer:** React throws "Too many re-renders". `setRating(n)` is executed during render (the result `undefined` is passed to `onClick`). It queues a state update, which causes a render, which calls `setRating` again, forever. React stops the loop after a limit and throws. Fix: `onClick={() => setRating(n)}`.

---

## ⚫ Interview Questions + Answers

Q1: What is a controlled component?
A1: A component whose value comes from props and whose changes are reported via a callback. The parent is the single source of truth. Here `value` and `onChange` make `StarRating` controlled.

Q2: Why is hover kept in local state?
A2: It is temporary UI state that the parent does not care about. Keeping it local avoids re-rendering the parent on every mouse move.

Q3: How do you make it accessible?
A3: Use `role="radiogroup"` with `role="radio"` buttons, `aria-checked`, readable labels, and real `<button>` elements so keyboard users can Tab and press Space. Optionally add arrow-key navigation.

Q4: How would you support half ratings?
A4: Track the pointer position inside each star and decide whether the click is on the left or right half, then use steps of 0.5. Render a clipped half-filled star for fractional values.

Q5: How do you prevent unnecessary re-renders in a list of rating widgets?
A5: Wrap `StarRating` in `React.memo` and give `onChange` a stable identity with `useCallback` (or pass an id and let the child call a single stable handler).

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You need a discrete score of 1 to N (reviews, feedback)
- You want a reusable controlled input

❌ **Avoid when:**
- You need precise numeric input (use a slider or number input)
- A thumbs up/down is enough (simpler and clearer)

---

## 📊 Visual Diagram

```
  value = 3 (saved)             hover = 0
   ★ ★ ★ ☆ ☆                    shown = hover || value = 3

  mouse enters star 5:          hover = 5 → shown = 5
   ★ ★ ★ ★ ★   (preview only, value still 3)

  mouse leaves group:           hover = 0 → back to 3
  click star 5:                 onChange(5) → parent sets value = 5
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Controlled component | Value owned by the parent via props | Parent के props से चलने वाला component |
| Local state | State used only inside the component | सिर्फ component के अंदर की state |
| radiogroup | ARIA role for one-of-many choice | कई में से एक चुनने वाला ARIA role |
| aria-checked | Tells screen readers if selected | Selected है या नहीं, यह बताता है |
| Hover preview | Temporary highlight on mouse over | Mouse ले जाने पर अस्थायी highlight |
| Stable key | Unique, unchanging list identity | हर item की अनोखी, न बदलने वाली पहचान |

---

## ⚡ 3-Line Summary
**English:**
1. Build it as a controlled component: `value` and `onChange` from the parent, `hover` in local state.
2. Show `hover || value`, and use buttons with radio roles for keyboard and screen reader support.
3. In Next.js keep read-only display on the server and submit the rating with a Server Action.

**Hindi:**
1. इसे controlled component बनाओ: `value` और `onChange` parent से, `hover` local state में।
2. `hover || value` दिखाओ, और keyboard व screen reader के लिए radio role वाले buttons इस्तेमाल करो।
3. Next.js में read-only display server पर रखो और rating को Server Action से submit करो।

---

## ➡️ Next Topic
**203. Build Drag and Drop** — अब browser events की practice: native drag events से Kanban board, बिना किसी library के।
