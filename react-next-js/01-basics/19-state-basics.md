# 19. State — Basics
# हिंदी में: State — Component की याददाश्त (Memory)

---

## 🔵 Simple Definition (English)
**State** is data that a component remembers between renders and that can change over time. When state changes, React re-renders the component so the screen matches the new data. Normal local variables are reset on every render, so they cannot do this job.

## 🔵 सरल परिभाषा (Hindi)
**State** वह data है जिसे component renders के बीच याद रखता है और जो समय के साथ बदल सकता है। State बदलने पर React component को दोबारा render करता है ताकि screen नए data से match करे। साधारण local variables हर render पर reset हो जाते हैं, इसलिए वे यह काम नहीं कर सकते।

---

## 🔴 Problem it Solves

In plain JavaScript you change the page by hand: find the element, set `textContent`, keep the data and the screen in sync yourself. In a big app (cart count, filters, logged-in user) this becomes buggy, because the data and the screen drift apart. A normal variable inside a component does not help either:

```jsx
function Counter() {
  let count = 0;                         // ❌ reset to 0 on EVERY render
  return <button onClick={() => { count++; }}>{count}</button>; // changes variable, but React is never told to re-render
}
```

Two things are missing: (1) memory that survives re-renders, and (2) a signal that tells React "data changed, render again". State gives both.

## 🔴 यह क्यों बना? (Hindi)
Plain JavaScript में page हाथ से बदलना पड़ता है: element ढूँढो, `textContent` set करो, और data व screen को खुद sync रखो। बड़े app में (cart count, filters, logged-in user) यह bugs देता है क्योंकि data और screen अलग हो जाते हैं। Component के अंदर साधारण variable भी काम नहीं करता (ऊपर का code देखो)। दो चीज़ें चाहिए थीं: (1) ऐसी memory जो re-renders में बची रहे, और (2) React को बताने का तरीका कि "data बदला, फिर render करो"। State दोनों देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component calls useState(initial) on the first render
Step 2 → React stores the value in a slot attached to this component instance
Step 3 → useState returns [value, setValue]; value is a SNAPSHOT for this render
Step 4 → User clicks → handler calls setValue(newValue)
Step 5 → React schedules a re-render (it does NOT change the variable right now)
Step 6 → Component function runs again; useState returns the NEW stored value
Step 7 → React compares old and new output (diffing) and updates only changed DOM

RULES: never mutate state directly, call hooks only at the top level,
       state belongs to one component instance (two <Counter/> = two separate states)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component पहले render में useState(initial) call करता है
Step 2 → React value को इस component instance से जुड़े slot में रखता है
Step 3 → useState [value, setValue] देता है; value इस render का SNAPSHOT है
Step 4 → User click करता है → handler setValue(newValue) call करता है
Step 5 → React re-render schedule करता है (variable अभी नहीं बदलता)
Step 6 → Component function फिर चलता है; useState अब NAYI stored value देता है
Step 7 → React पुराने और नए output की diffing करके सिर्फ बदला हुआ DOM update करता है

RULES: state को सीधे mutate मत करो, hooks सिर्फ top level पर call करो,
       state एक component instance की होती है (दो <Counter/> = दो अलग states)
```

---

## 🟡 Real World Example
**Swiggy cart:** Each "Add" button on a dish increases the quantity. The quantity shown next to the dish, the cart badge in the header and the bill total all come from state. When you tap "+", state changes and React re-renders everything that depends on it. Nobody writes code to "find the badge and update the number". Another example is the Zomato search box: the text you typed is state, and the filtered restaurant list is calculated from it.

## 🟡 Real Example Hindi mein
**Swiggy cart:** हर dish के "Add" बटन से quantity बढ़ती है। Dish के पास दिखने वाली quantity, header का cart badge और bill total, सब state से आते हैं। "+" दबाने पर state बदलती है और React उन सब को re-render करता है जो उस पर निर्भर हैं। कोई "badge ढूँढकर number बदलो" वाला code नहीं लिखता। दूसरा उदाहरण Zomato का search box: जो text आपने लिखा वह state है, और filtered restaurants की list उसी से निकलती है।

---

## 💻 Code Example — Basic

```jsx
// Basic state: a quantity stepper for a dish
import { useState } from 'react';                    // import the state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function DishQuantity() {
  const [qty, setQty] = useState(0);                 // qty = current value, setQty = updater, 0 = initial

  return (
    <div>
      <button onClick={() => setQty(qty - 1)} disabled={qty === 0}>-</button> {/* decrease, never below 0 */}
      <span style={{ margin: '0 8px' }}>{qty}</span>  {/* show the current snapshot */}
      <button onClick={() => setQty(qty + 1)}>+</button> {/* increase: schedules a re-render */}
    </div>
  );
}

function App() {
  return (
    <div>
      <h3>Paneer Tikka</h3>
      <DishQuantity />                               {/* own state: separate from the next one */}
      <h3>Butter Naan</h3>
      <DishQuantity />                               {/* second instance = second, independent state */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount the app
```

## 💻 Code Example — Advanced

```jsx
// Advanced: cart with immutable updates of an object/array state and derived values
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

const MENU = [                                       // static menu data (outside component = created once)
  { id: 1, name: 'Paneer Tikka', price: 220 },
  { id: 2, name: 'Butter Naan', price: 40 },
  { id: 3, name: 'Dal Makhani', price: 260 },
];

function Cart() {
  const [items, setItems] = useState({});            // state shape: { [dishId]: quantity }

  const add = (id) =>
    setItems((prev) => ({ ...prev, [id]: (prev[id] ?? 0) + 1 })); // new object, never prev[id]++

  const remove = (id) =>
    setItems((prev) => {
      const next = { ...prev };                      // copy the old object first
      if ((next[id] ?? 0) <= 1) delete next[id];     // remove the key at 0 (safe: it is our own copy)
      else next[id] -= 1;                            // otherwise decrease the quantity
      return next;                                   // return the new object so React sees a change
    });

  // DERIVED values: calculate during render, do NOT store them in extra state
  const count = Object.values(items).reduce((a, b) => a + b, 0);       // total items
  const total = MENU.reduce((sum, d) => sum + d.price * (items[d.id] ?? 0), 0); // bill total

  return (
    <div style={{ maxWidth: 360 }}>
      <h3>Cart ({count})</h3>                        {/* badge: derived from state */}
      {MENU.map((dish) => (
        <div key={dish.id} style={{ display: 'flex', justifyContent: 'space-between', margin: '6px 0' }}>
          <span>{dish.name} - ₹{dish.price}</span>
          <span>
            <button onClick={() => remove(dish.id)}>-</button>            {/* decrease */}
            <b style={{ margin: '0 6px' }}>{items[dish.id] ?? 0}</b>      {/* quantity or 0 */}
            <button onClick={() => add(dish.id)}>+</button>               {/* increase */}
          </span>
        </div>
      ))}
      <hr />
      <strong>Total: ₹{total}</strong>                {/* derived total */}
      <button style={{ marginLeft: 12 }} onClick={() => setItems({})}>Clear</button> {/* reset state */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Cart />); // mount the cart
```

---

## 🟠 Next.js Connection
In the App Router, components are **Server Components by default**, and they cannot use `useState`. Add `'use client'` at the top of the file to make it a Client Component. Good practice: keep the page on the server (fetch data there) and push only the small interactive part (the stepper) into a Client Component.

```jsx
// app/menu/QuantityStepper.jsx  (Client Component: it needs state and onClick)
'use client';                                        // required for useState in the App Router
import { useState } from 'react';                    // hooks work only in Client Components

export default function QuantityStepper({ initial = 0 }) {
  const [qty, setQty] = useState(initial);           // initial value comes from the server as a prop
  return (
    <span>
      <button onClick={() => setQty((q) => Math.max(0, q - 1))}>-</button> {/* never below 0 */}
      {qty}
      <button onClick={() => setQty((q) => q + 1)}>+</button>
    </span>
  );
}
```

```jsx
// app/menu/page.jsx  (Server Component: fetches data, renders the client stepper)
import QuantityStepper from './QuantityStepper';     // client island
import { getDishes } from '@/lib/dishes';            // your data layer (hypothetical helper)

export default async function MenuPage() {
  const dishes = await getDishes();                  // runs on the server, no useEffect needed
  return dishes.map((d) => (
    <div key={d.id}>{d.name} <QuantityStepper /></div> // JS is shipped only for the stepper
  ));
}
```

Re-render behavior: when `qty` changes, only `QuantityStepper` re-renders (and its children). The server page does not run again.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state directly
✅ **Correct:** Create a new array/object and pass it to the setter

```jsx
// Wrong: same array reference, React sees no change, screen does not update
items.push('naan');          // ❌ mutation
setItems(items);             // ❌ same reference

// Right: new array each time
setItems([...items, 'naan']);                        // ✅ new reference, React re-renders
```

❌ **Mistake 2:** Reading state right after setting it and expecting the new value
✅ **Correct:** State is a snapshot. Use the value you computed, or the next render

```jsx
// Wrong
setQty(qty + 1);
console.log(qty);            // ❌ still the OLD value in this render

// Right
const next = qty + 1;        // ✅ compute once
setQty(next);
console.log(next);           // uses the new value
```

❌ **Mistake 3:** Storing derived data in state (duplicate source of truth)
✅ **Correct:** Calculate it during render

```jsx
// Wrong: total can go out of sync with items
const [items, setItems] = useState([]);
const [total, setTotal] = useState(0);                 // ❌ extra state to keep in sync

// Right
const total = items.reduce((s, i) => s + i.price, 0);  // ✅ always correct, no extra render
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function App() {
  const [n, setN] = useState(0);                       // starts at 0
  function addThree() {
    setN(n + 1);                                       // n is 0 in this render → sets 1
    setN(n + 1);                                       // still 0 → sets 1
    setN(n + 1);                                       // still 0 → sets 1
  }
  return <button onClick={addThree}>{n}</button>;
}
// What is shown after ONE click?
```
**Answer:** `1`, not `3`. Inside one render, `n` is a fixed snapshot (0). All three calls say "set state to 1", and React batches them into one re-render. To add three, use the updater form: `setN(p => p + 1)` three times, which queues three functions that run one after the other (0 → 1 → 2 → 3). This is explained further in topic 35.

---

## ⚫ Interview Questions + Answers

Q1: What is state in React?
A1: State is data owned by a component that React remembers between renders. Changing it with the setter schedules a re-render. Unlike a local variable, it survives renders; unlike props, the component itself owns and changes it.

Q2: Why can't we use a normal variable instead of state?
A2: A normal variable is re-created on every render, so it loses its value. Also changing it does not tell React to re-render. State solves both: it is stored by React and its setter triggers a render.

Q3: Is `setState` synchronous?
A3: No. It schedules an update. The new value is visible only on the next render. Since React 18, updates are batched automatically everywhere (event handlers, timeouts, promises), so several setters in one tick cause one render.

Q4: What happens if you call `setState` with the same value?
A4: React compares with `Object.is`. If it is equal, React bails out and does not re-render the children or run effects (it may still call the component function once more). This is why mutating an object and passing it back does not work.

Q5: Where should state live?
A5: In the closest common parent of all components that need it ("lifting state up"). Keep it as small as possible and derive everything else. If many far-away components need it, consider context or a state library.

---

## 🔷 When to Use + When Not to Use
✅ **Use state when:**
- The data changes over time because of user actions (typing, clicking, toggling)
- The screen must update when the data changes
- The value must survive re-renders (form input, open/closed menu, cart)

❌ **Avoid state when:**
- The value can be calculated from props or other state (derive it)
- It changes but should not cause a render, for example a timer id or previous value (use `useRef`)
- It is constant data (keep it outside the component)

---

## 📊 Visual Diagram

```
 Render 1                  click "+"                   Render 2
 ┌──────────────┐        setQty(qty + 1)         ┌──────────────┐
 │ qty = 0      │ ─────────────────────────────► │ qty = 1      │
 │ UI shows 0   │   React stores 1, schedules    │ UI shows 1   │
 └──────────────┘   a re-render of this component└──────────────┘
        ▲                                                │
        └──── React's memory slot keeps the value ───────┘

 Two instances:  <Counter/> ─ slot A (qty=2)
                 <Counter/> ─ slot B (qty=7)    (independent)

 Performance: a state change re-renders the owner and its children,
 so keep state as close as possible to where it is used.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Data a component remembers and can change | Component की याद रखने वाली, बदलने वाली data |
| Setter | Function that updates state and schedules a render | State बदलने और render schedule करने वाला function |
| Snapshot | Fixed value of state for one render | एक render के लिए state की तय value |
| Re-render | Running the component again after a change | बदलाव के बाद component फिर चलाना |
| Batching | Combining several updates into one render | कई updates को एक render में जोड़ना |
| Immutable update | Make a new copy instead of changing the old | पुराने को बदलने की जगह नई copy बनाना |
| Derived state | Value calculated from other state/props | दूसरी state/props से निकाली गई value |
| Lifting state up | Moving state to a common parent | State को common parent में ले जाना |

---

## ⚡ 3-Line Summary
**English:**
1. State is a component's memory: it survives renders, and changing it triggers a re-render.
2. State is a snapshot per render, and updates are batched, so never mutate it and never expect an instant change.
3. Keep state minimal, derive everything else, and in Next.js use state only in `'use client'` components.

**Hindi:**
1. State component की memory है: यह renders में बची रहती है और बदलने पर re-render कराती है।
2. State हर render का snapshot है और updates batch होते हैं, इसलिए इसे कभी mutate मत करो और तुरंत बदलाव की उम्मीद मत रखो।
3. State कम से कम रखो, बाकी सब derive करो, और Next.js में state सिर्फ `'use client'` components में इस्तेमाल करो।

---

## ➡️ Next Topic
**21. State vs Props — Difference** — अब जब props (15) और state (19) दोनों समझ आ गए, तो इनका फर्क, कौन किसका owner है और data किस दिशा में बहता है, यह साफ करना ज़रूरी है। Interview का यह बहुत पूछा जाने वाला सवाल है।
