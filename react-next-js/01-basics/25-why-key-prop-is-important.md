# 25. Why key Prop is Important
# हिंदी में: key Prop क्यों ज़रूरी है

---

## 🔵 Simple Definition (English)
The **`key`** prop is a special identifier you give each element in a list (or any sibling group) so React can tell which item is which between renders. With stable, unique keys React moves, adds and removes the right items and keeps each item's state attached to it.

## 🔵 सरल परिभाषा (Hindi)
**`key`** prop एक खास पहचान है जो आप list (या किसी sibling group) के हर element को देते हैं, ताकि React renders के बीच बता सके कि कौन सा item कौन सा है। Stable और unique keys होने पर React सही items को move, add और remove करता है और हर item की state उसी item से जुड़ी रहती है।

---

## 🔴 Problem it Solves

When a list changes, React has to match the old items with the new items. Without extra information, it can only compare **by position**: first with first, second with second. If you delete or insert an item at the top, every item after it is now "different" by position. That causes wasted DOM work, and worse, **wrong state**: the typed text of row 1 stays on screen, but now in the row of a different dish.

```jsx
// Index as key: delete the first dish and the input values slide to the wrong rows
{dishes.map((d, i) => (
  <li key={i}>{d.name} <input /></li>      // ❌ key 0,1,2 → after delete: key 0,1
))}
```

Keys give every item an identity that does not depend on the position.

## 🔴 यह क्यों बना? (Hindi)
List बदलने पर React को पुराने items को नए items से match करना होता है। अतिरिक्त जानकारी के बिना वह सिर्फ **position से** तुलना कर सकता है: पहला-पहले से, दूसरा-दूसरे से। अगर आप ऊपर से कोई item हटाएँ या डालें, तो उसके बाद का हर item position के हिसाब से "अलग" दिखता है। इससे DOM का फालतू काम होता है, और उससे भी बुरा, **गलत state**: row 1 में लिखा text स्क्रीन पर रहता है पर अब किसी दूसरी dish की row में।

Keys हर item को ऐसी पहचान देती हैं जो position पर निर्भर नहीं करती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You render a list and give each item key={uniqueId}
Step 2 → React stores the key together with each element in the tree
Step 3 → On the next render it matches old and new siblings BY KEY, not by position
Step 4 → Same key found       → keep the component instance, update props, KEEP state
Step 5 → New key (not before) → mount a new component instance
Step 6 → Old key missing now  → unmount it and destroy its state
Step 7 → Same key, new position → move the DOM node (no remount)

Key rules: unique among SIBLINGS only, stable between renders (not Math.random()),
           comes from your data (id), not generated during render.
Bonus trick: changing a component's key on purpose RESETS its state.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप list render करते हैं और हर item को key={uniqueId} देते हैं
Step 2 → React key को हर element के साथ tree में रखता है
Step 3 → अगले render में वह पुराने और नए siblings को KEY से match करता है, position से नहीं
Step 4 → वही key मिली         → component instance रखो, props update करो, state बनी रहे
Step 5 → नई key (पहले नहीं थी) → नया component instance mount करो
Step 6 → पुरानी key अब नहीं है → unmount करो और उसकी state खत्म
Step 7 → वही key, नई position → DOM node को move करो (remount नहीं)

नियम: key सिर्फ SIBLINGS में unique हो, renders में stable हो (Math.random() नहीं),
      data से आए (id), render के समय बनाई न जाए।
Bonus trick: जानबूझकर key बदलने से component की state RESET हो जाती है।
```

---

## 🟡 Real World Example
**Swiggy cart:** The cart shows dishes, and each row has a quantity stepper and a "cooking instructions" text box. A customer types "less spicy" into the second row and then removes the first dish. With `key={index}`, the "less spicy" text jumps to the row that is now second (a different dish) or the wrong row disappears. With `key={dish.id}`, React knows exactly which row was removed, so the instruction stays with its dish. The same issue appears in chat apps, notification lists and to-do lists.

## 🟡 Real Example Hindi mein
**Swiggy cart:** Cart में dishes दिखती हैं, और हर row में quantity stepper और "cooking instructions" का text box है। Customer दूसरी row में "less spicy" लिखता है और फिर पहली dish हटा देता है। `key={index}` के साथ "less spicy" वाला text उस row में चला जाता है जो अब दूसरी है (अलग dish), या गलत row गायब होती है। `key={dish.id}` से React ठीक जानता है कि कौन सी row हटी, इसलिए instruction अपनी dish के साथ रहती है। यही समस्या chat apps, notification lists और to-do lists में भी आती है।

---

## 💻 Code Example — Basic

```jsx
// Basic: correct keys in a list
import { createRoot } from 'react-dom/client';       // React 18/19 root API

const dishes = [                                     // data comes with stable ids from the backend
  { id: 'd101', name: 'Paneer Tikka' },
  { id: 'd102', name: 'Butter Naan' },
  { id: 'd103', name: 'Dal Makhani' },
];

function Menu() {
  return (
    <ul>
      {dishes.map((dish) => (                        // map returns an array of elements
        <li key={dish.id}>{dish.name}</li>           // key goes on the OUTERMOST element returned by map
      ))}
    </ul>
  );
}

createRoot(document.getElementById('root')).render(<Menu />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: compare index keys vs id keys with stateful rows, and use key to reset a form
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

let nextId = 4;                                      // simple id generator (a real app gets ids from the server)

// Each row has its OWN state (the note text). The state lives with the component instance.
function CartRow({ dish, onRemove }) {
  const [note, setNote] = useState('');              // cooking instruction typed by the user
  return (
    <li style={{ margin: '6px 0' }}>
      {dish.name}{' '}
      <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="note" /> {/* row state */}
      <button onClick={() => onRemove(dish.id)}>Remove</button>
    </li>
  );
}

function Cart({ useIndexKey }) {
  const [dishes, setDishes] = useState([             // list owned by the cart
    { id: 1, name: 'Paneer Tikka' },
    { id: 2, name: 'Butter Naan' },
    { id: 3, name: 'Dal Makhani' },
  ]);
  const remove = (id) => setDishes((d) => d.filter((x) => x.id !== id)); // immutable removal
  const addToTop = () => setDishes((d) => [{ id: nextId++, name: `Dish ${nextId - 1}` }, ...d]); // insert at the top

  return (
    <div>
      <button onClick={addToTop}>Add to top</button> {/* inserting at top breaks index keys */}
      <ul>
        {dishes.map((dish, index) => (
          <CartRow
            key={useIndexKey ? index : dish.id}      // ❌ index vs ✅ id: type a note, then add/remove
            dish={dish}
            onRemove={remove}
          />
        ))}
      </ul>
    </div>
  );
}

// Second use of key: reset a component's state when the "identity" changes
function CheckoutForm({ address }) {
  const [instructions, setInstructions] = useState(''); // draft for ONE address
  return <textarea value={instructions} onChange={(e) => setInstructions(e.target.value)} placeholder={address} />;
}

function Checkout() {
  const [address, setAddress] = useState('Home');
  return (
    <div>
      <button onClick={() => setAddress('Office')}>Deliver to Office</button>
      {/* key changes with the address → React remounts → draft is cleared automatically */}
      <CheckoutForm key={address} address={address} />
    </div>
  );
}

function App() {
  return (
    <>
      <h4>Index keys (buggy)</h4><Cart useIndexKey />
      <h4>Id keys (correct)</h4><Cart />
      <h4>key to reset state</h4><Checkout />
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

---

## 🟠 Next.js Connection
Keys work exactly the same in Server Components and Client Components. In the App Router the list is often rendered on the server from database rows, so use the database id as key. Another useful point: in Next.js, navigating between pages of the same dynamic route (`/restaurant/1` → `/restaurant/2`) can keep a Client Component instance alive, and its state will survive. Adding a `key` based on the param makes it reset.

```jsx
// app/restaurant/[id]/page.jsx (Server Component)
import ReviewForm from './ReviewForm';               // client component with local draft state
import { getRestaurant } from '@/lib/restaurants';   // hypothetical helper

export default async function Page({ params }) {
  const { id } = await params;                       // Next.js 15+: params is a Promise
  const r = await getRestaurant(id);                 // server fetch
  return (
    <section>
      <h1>{r.name}</h1>
      <ul>
        {r.reviews.map((rev) => <li key={rev.id}>{rev.text}</li>)} {/* DB id as key */}
      </ul>
      <ReviewForm key={id} restaurantId={id} />      {/* new restaurant → fresh form, no leftover draft */}
    </section>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using the array index as key for lists that change (insert, delete, sort, filter)
✅ **Correct:** Use a stable unique id from your data

```jsx
// Wrong
items.map((item, i) => <Row key={i} item={item} />);       // ❌ identity = position

// Right
items.map((item) => <Row key={item.id} item={item} />);    // ✅ identity = the item
// Index is acceptable ONLY for a static list that is never reordered or filtered.
```

❌ **Mistake 2:** Generating keys during render (`Math.random()`, `crypto.randomUUID()`)
✅ **Correct:** Generate the id once when the data is created

```jsx
// Wrong: new key every render → every row remounts, state and focus are lost
items.map((item) => <Row key={Math.random()} item={item} />);   // ❌ very slow, loses focus

// Right: create the id when the item is created
const [items, setItems] = useState([]);
const add = (text) => setItems((p) => [...p, { id: crypto.randomUUID(), text }]); // ✅ stored once
```

❌ **Mistake 3:** Putting the key on the wrong element (inside the component instead of where you map)
✅ **Correct:** Put the key on the element returned by `map`

```jsx
// Wrong: key on the inner element, the outer Fragment/Row has no key → warning
items.map((i) => <><li key={i.id}>{i.name}</li></>);       // ❌

// Right
items.map((i) => <Fragment key={i.id}><li>{i.name}</li></Fragment>); // ✅
// Also remember: key is NOT passed as a prop; props.key is undefined inside the component.
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function Row({ label }) {
  const [text, setText] = useState('');
  return <li>{label}: <input value={text} onChange={(e) => setText(e.target.value)} /></li>;
}

function App() {
  const [items, setItems] = useState(['A', 'B', 'C']);
  return (
    <>
      <button onClick={() => setItems(items.slice(1))}>Remove first</button>
      <ul>{items.map((label, i) => <Row key={i} label={label} />)}</ul>
    </>
  );
}
// The user types "hello" in the row labelled A, then clicks "Remove first". What does the screen show?
```
**Answer:** The list shows `B` and `C`, but the input next to `B` contains `hello`. Keys are `0,1,2` and then `0,1`, so React keeps the instances with key 0 and 1 (which hold the typed text of A and B) and just changes their `label` prop, and it destroys the instance with key 2. The state moved by position, not by item. With `key={label}` (or a real id), React would destroy the row for `A` together with its text, and `B`/`C` would keep their own (empty) inputs.

---

## ⚫ Interview Questions + Answers

Q1: Why does React need keys?
A1: To identify list items across renders. React uses keys to match old and new elements, so it can reorder, insert and remove the right DOM nodes and keep component state attached to the correct item. Without keys it falls back to position and shows a warning.

Q2: Why is using the index as key a bad idea?
A2: The index is the position, not the identity. When items are inserted, removed or sorted, the same index points to a different item, so state (inputs, focus, checkboxes) and DOM nodes get mixed up, and React does extra work. It is acceptable only for static lists that never change order.

Q3: Should keys be globally unique?
A3: No. They must be unique only among siblings in the same array. Two different lists can use the same keys. Also keys should be stable: the same item must get the same key on every render.

Q4: Can I use `key` to reset a component?
A4: Yes. When the key of a component changes, React unmounts the old instance and mounts a new one with fresh state. It is the recommended way to reset a form or a draft when an "identity" changes (for example, a different user or product id), instead of syncing with `useEffect`.

Q5: Is `key` available as `props.key`?
A5: No. `key` (and `ref` in older versions) is reserved for React. It is not passed down as a prop. If the child needs the value, pass it with another name such as `id`.

---

## 🔷 When to Use + When Not to Use
✅ **Use stable id keys when:**
- Rendering any dynamic list (`map`) of components or elements
- Items can be added, removed, reordered or filtered
- Rows hold state (inputs, expanded panels, animations)

✅ **Use a changing key on purpose when:**
- You want to reset a component's state (form for a different user, a stepper after submit)

❌ **Avoid:**
- Index keys on dynamic lists
- Random keys generated on each render
- Non-unique keys among siblings (duplicate key warning, items lost or duplicated)

---

## 📊 Visual Diagram

```
 Remove first item, KEY = INDEX                Remove first item, KEY = ID
 ┌───────────┬──────────────┐                 ┌───────────┬──────────────┐
 │ before    │ after        │                 │ before    │ after        │
 │ 0: A "hi" │ 0: B (+ "hi")│ ← state of A    │ a1: A "hi"│   (removed)  │
 │ 1: B ""   │ 1: C         │   stays on B!   │ b2: B ""  │ b2: B ""     │
 │ 2: C ""   │ (2 removed)  │                 │ c3: C ""  │ c3: C ""     │
 └───────────┴──────────────┘                 └───────────┴──────────────┘
   React matches by position                    React matches by identity

 Performance: good keys let React MOVE existing DOM nodes instead of
 recreating them; bad keys (random) recreate everything on every render.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| key | Special prop identifying an element among siblings | Siblings में element की पहचान वाला खास prop |
| Reconciliation | React's diffing of old vs new tree | पुराने और नए tree की तुलना |
| Identity | Which item an element represents | Element किस item को दर्शाता है |
| Sibling | Elements in the same array/parent | उसी array/parent के elements |
| Remount | Destroy and create the instance again | Instance को खत्म करके दोबारा बनाना |
| Stable key | Same key for the same item every render | हर render में उसी item की वही key |
| Index key | Using array position as key | Array position को key बनाना |
| Fragment key | key on `<Fragment key=...>` for grouped list items | Grouped list items के लिए Fragment पर key |

---

## ⚡ 3-Line Summary
**English:**
1. `key` gives each list item a stable identity so React matches items by identity, not position.
2. Use unique ids from your data; avoid index keys on changing lists and never use random keys.
3. Changing a key on purpose remounts a component and resets its state.

**Hindi:**
1. `key` हर list item को stable पहचान देती है ताकि React items को position नहीं, पहचान से match करे।
2. Data से unique id इस्तेमाल करो; बदलने वाली lists में index key से बचो और random key कभी मत लगाओ।
3. जानबूझकर key बदलने से component remount होता है और उसकी state reset हो जाती है।

---

## ➡️ Next Topic
**27. Synthetic Events** — Lists में buttons और inputs होते हैं, जिनके events React अपने wrapper (SyntheticEvent) से संभालता है। अगला topic बताता है कि यह wrapper क्या है और browser के native event से कैसे अलग है।
