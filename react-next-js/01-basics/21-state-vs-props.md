# 21. State vs Props — Difference
# हिंदी में: State बनाम Props — फर्क क्या है?

---

## 🔵 Simple Definition (English)
**Props** are inputs a component receives from its parent, and they are read-only. **State** is data a component owns and can change itself. Props flow down from parent to child; state lives inside one component, and changing either one causes a re-render.

## 🔵 सरल परिभाषा (Hindi)
**Props** वे inputs हैं जो component को अपने parent से मिलते हैं, और वे read-only होते हैं। **State** वह data है जिसका component खुद owner है और खुद बदल सकता है। Props parent से child की ओर बहते हैं; state एक component के अंदर रहती है, और दोनों में से कुछ भी बदले तो re-render होता है।

---

## 🔴 Problem it Solves

Beginners confuse the two and either copy props into state (which goes stale) or put everything in state (which causes extra bugs). Without a clear rule, data flow becomes unpredictable: who is allowed to change this value, and where does it come from?

React's rule: **one owner per piece of data.** The owner keeps it as state. Everyone else receives it as a prop and can only ask the owner to change it (through a callback prop).

```jsx
// The classic mistake: copying a prop into state
function Price({ amount }) {
  const [value] = useState(amount);   // ❌ takes amount ONLY on the first render
  return <b>{value}</b>;              // parent changes amount → this never updates
}
```

## 🔴 यह क्यों बना? (Hindi)
Beginners दोनों में confuse होते हैं और या तो props को state में copy कर देते हैं (जो पुरानी पड़ जाती है) या सब कुछ state में डाल देते हैं (जिससे extra bugs आते हैं)। साफ नियम के बिना data flow अनिश्चित हो जाता है: यह value कौन बदल सकता है, और कहाँ से आती है?

React का नियम: **हर data का एक ही owner।** Owner उसे state में रखता है। बाकी सब उसे prop की तरह पाते हैं और बदलाव के लिए सिर्फ owner से (callback prop के ज़रिए) कह सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent owns the data in state:        const [qty, setQty] = useState(1)
Step 2 → Parent passes data DOWN as a prop:    <Item qty={qty} />
Step 3 → Parent also passes a callback prop:   <Item qty={qty} onChange={setQty} />
Step 4 → Child reads props, never assigns them (props are frozen/read-only)
Step 5 → Child calls onChange(newValue) → "event goes UP"
Step 6 → Parent updates its state → re-renders → passes the new prop DOWN
Step 7 → Child re-renders with the new prop value

Pattern name: "data down, events up" (one-way data flow)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent data को state में रखता है:        const [qty, setQty] = useState(1)
Step 2 → Parent data को prop की तरह NEECHE भेजता है: <Item qty={qty} />
Step 3 → Parent callback prop भी भेजता है:         <Item qty={qty} onChange={setQty} />
Step 4 → Child props पढ़ता है, उन्हें बदलता नहीं (props read-only हैं)
Step 5 → Child onChange(newValue) call करता है → "event ऊपर जाता है"
Step 6 → Parent अपनी state update करता है → re-render → नई prop नीचे भेजता है
Step 7 → Child नई prop value के साथ re-render होता है

Pattern का नाम: "data नीचे, events ऊपर" (one-way data flow)
```

---

## 🟡 Real World Example
**Amazon product page:** The page component owns the selected `quantity` in state. The `QuantityDropdown` child receives `value` and `onChange` as props. The `PriceSummary` child receives `quantity` and `unitPrice` as props and shows the total. Only the page can change the quantity. Both children just display it, so the price and dropdown can never disagree. Inside the dropdown, the "is the menu open?" flag is its own state, because nobody else needs it.

## 🟡 Real Example Hindi mein
**Amazon product page:** Page component चुनी हुई `quantity` को state में रखता है। `QuantityDropdown` child को `value` और `onChange` props में मिलते हैं। `PriceSummary` child को `quantity` और `unitPrice` props में मिलते हैं और total दिखाता है। Quantity सिर्फ page बदल सकता है। दोनों children सिर्फ दिखाते हैं, इसलिए price और dropdown कभी अलग नहीं होंगे। Dropdown के अंदर "menu खुला है?" वाला flag उसकी अपनी state है, क्योंकि और किसी को इसकी ज़रूरत नहीं।

---

## 💻 Code Example — Basic

```jsx
// Basic: state in the parent, props in the children
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function PriceSummary({ qty, unitPrice }) {         // receives props: read-only inputs
  // qty = 5;                                         // ❌ would be a bug: never assign to props
  return <p>Total: ₹{qty * unitPrice}</p>;           // just display derived data
}

function QuantityPicker({ value, onChange }) {      // value + callback come from the parent
  return (
    <div>
      <button onClick={() => onChange(value - 1)} disabled={value <= 1}>-</button> {/* ask parent to change */}
      <span style={{ margin: '0 8px' }}>{value}</span> {/* show the prop */}
      <button onClick={() => onChange(value + 1)}>+</button> {/* ask parent to change */}
    </div>
  );
}

function ProductPage() {
  const [qty, setQty] = useState(1);                 // OWNER of qty: it is state here
  return (
    <div>
      <h3>boAt Earbuds</h3>
      <QuantityPicker value={qty} onChange={setQty} /> {/* data down, event up */}
      <PriceSummary qty={qty} unitPrice={1299} />      {/* same data down to a second child */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<ProductPage />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: the same component with BOTH props and its own internal state,
// plus the "derive from props" pattern instead of copying props into state
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

// A filter dropdown: "open" is its own UI state, "selected" is controlled by the parent
function FilterDropdown({ options, selected, onSelect }) {
  const [open, setOpen] = useState(false);           // internal state: nobody else cares about it
  const label = options.find((o) => o.id === selected)?.label ?? 'Select'; // DERIVED from props, not state

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button onClick={() => setOpen((o) => !o)}>{label} ▾</button> {/* toggles own state */}
      {open && (
        <ul style={{ position: 'absolute', margin: 0, padding: 8, background: '#fff', border: '1px solid #ccc' }}>
          {options.map((o) => (
            <li key={o.id} style={{ listStyle: 'none' }}>
              <button
                onClick={() => {
                  onSelect(o.id);                    // tell the parent (event UP)
                  setOpen(false);                    // close own menu (own state)
                }}
              >
                {o.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

const RESTAURANTS = [                                // sample data
  { id: 1, name: 'Biryani Blues', rating: 4.4, veg: false },
  { id: 2, name: 'Green Bowl', rating: 4.6, veg: true },
  { id: 3, name: 'Pizza Hub', rating: 3.9, veg: false },
];
const SORTS = [
  { id: 'rating', label: 'Rating' },
  { id: 'name', label: 'Name' },
];

function RestaurantList() {
  const [sort, setSort] = useState('rating');        // parent owns "sort" (shared with the list)
  const [vegOnly, setVegOnly] = useState(false);     // parent owns "vegOnly"

  // derived list: computed from state during render, not stored
  const visible = RESTAURANTS
    .filter((r) => !vegOnly || r.veg)                // apply the veg filter
    .sort((a, b) => (sort === 'rating' ? b.rating - a.rating : a.name.localeCompare(b.name))); // sort (filter made a copy)

  return (
    <div>
      <FilterDropdown options={SORTS} selected={sort} onSelect={setSort} /> {/* props down, events up */}
      <label style={{ marginLeft: 12 }}>
        <input type="checkbox" checked={vegOnly} onChange={(e) => setVegOnly(e.target.checked)} /> Veg only
      </label>
      <ul>{visible.map((r) => <li key={r.id}>{r.name} ★{r.rating}</li>)}</ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<RestaurantList />); // mount
```

---

## 🟠 Next.js Connection
In the App Router, a Server Component can pass **props** to a Client Component, and those props must be serializable (strings, numbers, plain objects, arrays, Server Actions). Functions and class instances cannot be passed as props across the server/client boundary, except Server Actions. State exists only in the Client Component. A common trick is to use the URL (`searchParams`) as shared "state" so the server page can read it too.

```jsx
// app/restaurants/page.jsx (Server Component: reads the URL, passes plain props)
import SortDropdown from './SortDropdown';           // client component
import { getRestaurants } from '@/lib/restaurants';  // hypothetical data helper

export default async function Page({ searchParams }) {
  const { sort = 'rating' } = await searchParams;    // Next.js 15+: searchParams is a Promise
  const list = await getRestaurants(sort);           // server decides the data from the URL
  return (
    <>
      <SortDropdown current={sort} />                {/* serializable prop: a string */}
      <ul>{list.map((r) => <li key={r.id}>{r.name}</li>)}</ul>
    </>
  );
}
```

```jsx
// app/restaurants/SortDropdown.jsx
'use client';                                        // needs router hooks
import { useRouter } from 'next/navigation';         // App Router navigation

export default function SortDropdown({ current }) {  // prop from the server
  const router = useRouter();                        // used to update the URL
  return (
    <select value={current} onChange={(e) => router.push(`?sort=${e.target.value}`)}> {/* URL = shared state */}
      <option value="rating">Rating</option>
      <option value="name">Name</option>
    </select>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Copying a prop into state ("stale prop")
✅ **Correct:** Use the prop directly, or reset the state with a `key` when the identity changes

```jsx
// Wrong: initial value is read once
function Profile({ user }) {
  const [name, setName] = useState(user.name);       // ❌ new user prop is ignored
  return <input value={name} onChange={(e) => setName(e.target.value)} />;
}

// Right: if you need an editable copy, remount when the user changes
<Profile key={user.id} user={user} />                // ✅ different key → fresh state
```

❌ **Mistake 2:** Trying to change a prop inside the child
✅ **Correct:** Call a callback prop and let the parent update its state

```jsx
// Wrong
function Counter({ count }) {
  return <button onClick={() => { count += 1; }}>{count}</button>; // ❌ local reassign, no render
}

// Right
function Counter({ count, onIncrement }) {
  return <button onClick={onIncrement}>{count}</button>;           // ✅ parent owns count
}
```

❌ **Mistake 3:** Keeping the same data in two components' state
✅ **Correct:** Lift state up to the common parent and pass it as props

```jsx
// Wrong: two copies can disagree
function A() { const [q, setQ] = useState(1); /* ... */ }
function B() { const [q, setQ] = useState(1); /* ... */ }

// Right: one owner
function Parent() {
  const [q, setQ] = useState(1);                     // ✅ single source of truth
  return <><A q={q} setQ={setQ} /><B q={q} /></>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function Child({ initialName }) {
  const [name] = useState(initialName);              // copy prop into state
  return <p>{name}</p>;
}

function Parent() {
  const [n, setN] = useState('Aman');
  return (
    <>
      <button onClick={() => setN('Riya')}>Change</button>
      <Child initialName={n} />
    </>
  );
}
// What is shown after clicking "Change"?
```
**Answer:** It still shows `Aman`. `Child` re-renders with `initialName = 'Riya'`, but `useState` ignores its argument after the first render, so `name` stays `Aman`. The fix is to use the prop directly (`<p>{initialName}</p>`) or give the child a changing `key` (`<Child key={n} ... />`) so React creates a new instance with fresh state. The word `initial` in the prop name is a hint that this is the intended "seed only" pattern.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between state and props?
A1: Props are passed from the parent and are read-only for the receiving component. State is owned by the component and changed with its setter. Props make a component configurable; state makes it interactive. Both trigger a re-render when they change.

Q2: Can a child change its parent's state?
A2: Not directly. The parent passes a callback (for example `onChange={setQty}`) as a prop, and the child calls it. React keeps one-way data flow: data down, events up.

Q3: Why are props read-only?
A3: Components should be pure functions of their inputs. If a child mutated props, the parent would not know, the data would drift, and bugs would be hard to trace. The owner of the data is the only one allowed to change it.

Q4: Is it okay to put a prop into state?
A4: Only when you want an editable draft seeded by the prop, and then you must handle changes (reset using `key`). Otherwise it creates a stale copy. Prefer computing from props during render.

Q5: Does a child re-render when the parent re-renders even if props did not change?
A5: Yes, by default. Re-render follows the parent unless the child is wrapped in `React.memo` and the props are shallow-equal. Changing a prop value is one reason for a render, but not the only one.

---

## 🔷 When to Use + When Not to Use
✅ **Use props when:**
- Data comes from a parent and the child only needs to display or use it
- You want a reusable, configurable component (button label, size, onClick)
- Several siblings need the same data (lift state up, pass down as props)

✅ **Use state when:**
- The component itself changes the data over time (input text, open/closed, selected tab)
- The data is purely local UI detail that no parent needs

❌ **Avoid:**
- Copying props into state without a reason
- Duplicating the same data in props and state
- Storing derived values in state

---

## 📊 Visual Diagram

```
                 ┌──────────────────────────┐
                 │ ProductPage              │
                 │ STATE: qty = 2  (owner)  │
                 └───────┬──────────┬───────┘
         props ↓ value,onChange     │ props ↓ qty, unitPrice
                 ▼                  ▼
        ┌────────────────┐   ┌────────────────┐
        │ QuantityPicker │   │ PriceSummary   │
        │ own state:     │   │ (no state,     │
        │  open = false  │   │  only props)   │
        └───────┬────────┘   └────────────────┘
                │ onChange(3)  ↑ event goes UP
                ▼
        ProductPage setQty(3) → re-render → new props flow DOWN

  State:  inside a component, changeable by itself
  Props:  from outside, read-only
  Performance: a state change re-renders the owner + all children (unless memoized)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Props | Read-only inputs from the parent | Parent से आने वाले read-only inputs |
| State | Data owned and changed by the component | Component का अपना बदलने वाला data |
| One-way data flow | Data goes only parent → child | Data सिर्फ parent से child की ओर |
| Callback prop | Function prop the child calls to notify the parent | Child जो function call करके parent को बताता है |
| Source of truth | The single owner of a piece of data | Data का एकमात्र owner |
| Lifting state up | Moving state to the common parent | State को common parent में ले जाना |
| Stale prop copy | State that copied a prop and never updated | Prop की पुरानी पड़ चुकी copy |
| Serializable | Can be converted to JSON-like data | JSON जैसे data में बदलने लायक |

---

## ⚡ 3-Line Summary
**English:**
1. Props come from the parent and are read-only; state is owned by the component and changed with its setter.
2. Data flows down as props and events flow up as callbacks, so every value has exactly one owner.
3. Do not copy props into state; derive values, or reset with `key`. In Next.js, props crossing the server/client boundary must be serializable.

**Hindi:**
1. Props parent से आते हैं और read-only हैं; state component की अपनी है और setter से बदलती है।
2. Data props की तरह नीचे और events callbacks की तरह ऊपर बहते हैं, इसलिए हर value का एक ही owner होता है।
3. Props को state में copy मत करो; derive करो या `key` से reset करो। Next.js में server/client सीमा पार करने वाले props serializable होने चाहिए।

---

## ➡️ Next Topic
**22. Rendering — How React Renders** — State या props बदलने पर आगे क्या होता है? Render phase, commit phase और re-render के कारण समझना ज़रूरी है, क्योंकि performance और hooks के सभी नियम इसी पर टिके हैं।
