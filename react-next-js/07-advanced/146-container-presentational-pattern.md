# 146. Container + Presentational Pattern
# हिंदी में: Container + Presentational Pattern — Logic और UI को अलग करना

---

## 🔵 Simple Definition (English)
The **Container + Presentational pattern** splits a feature into two parts: a **container** that fetches data and holds logic/state, and a **presentational** component that only receives props and renders UI. Today, custom hooks and Server Components often play the container role.

## 🔵 सरल परिभाषा (Hindi)
**Container + Presentational pattern** किसी feature को दो हिस्सों में बाँटता है: **container** जो data लाता है और logic/state रखता है, और **presentational** component जो सिर्फ props लेकर UI दिखाता है। आजकल custom hooks और Server Components अक्सर container का काम करते हैं।

---

## 🔴 Problem it Solves

When one component fetches data, handles errors, filters, formats and renders markup, it grows huge, is hard to test (needs network mocks), and cannot be reused with different data or shown in Storybook.

```jsx
// PROBLEM: everything in one component
function RestaurantList() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { fetch('/api/restaurants').then(r => r.json()).then(d => { setData(d); setLoading(false); }); }, []);
  if (loading) return <p>Loading</p>;
  return <ul>{data.map(r => <li key={r.id}>{r.name} - {r.rating}</li>)}</ul>;   // UI tied to fetching
}

// SOLUTION: presentational part is pure and reusable
function RestaurantListView({ restaurants }) {               // no fetching, easy to test
  return <ul>{restaurants.map(r => <li key={r.id}>{r.name} - {r.rating}</li>)}</ul>;
}
```

## 🔴 यह क्यों बना? (Hindi)
जब एक ही component data लाता है, errors संभालता है, filter और format करता है और markup भी बनाता है, तो वह बहुत बड़ा हो जाता है, test करना कठिन होता है (network mock चाहिए), और अलग data के साथ दोबारा इस्तेमाल या Storybook में दिखाना मुश्किल होता है। Presentational हिस्सा शुद्ध (pure) और reusable रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify the two concerns: HOW things work (data, state, handlers) vs HOW things look (markup, styles)
Step 2 → Write the Presentational component: props in, JSX out, minimal or no state (only UI state like open/closed)
Step 3 → Write the Container: fetches/derives data, holds state, defines handlers
Step 4 → Container renders the Presentational one and passes data + callbacks as props
Step 5 → Test the view with plain props; test the container's logic separately
Step 6 → Modern form: the container becomes a custom hook (useRestaurants) or a Server Component

Evolution: Dan Abramov (who popularized the pattern) later said it is not a strict rule; hooks reduced the need for a separate container component
Re-render: when container state changes, the presentational child re-renders; wrap it in memo if it is heavy and props are stable
Performance: no direct cost; clearer boundaries make memoization and testing simpler
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → दो चिंताएँ पहचानो: चीज़ें कैसे काम करती हैं (data, state, handlers) बनाम कैसी दिखती हैं (markup, styles)
Step 2 → Presentational component लिखो: props अंदर, JSX बाहर, न्यूनतम या कोई state नहीं (सिर्फ UI state जैसे open/closed)
Step 3 → Container लिखो: data लाता/निकालता है, state रखता है, handlers बनाता है
Step 4 → Container, Presentational को render करके data + callbacks props में देता है
Step 5 → View को सीधे props से test करो; container का logic अलग test करो
Step 6 → आधुनिक रूप: container एक custom hook (useRestaurants) या Server Component बन जाता है

विकास: इस pattern को लोकप्रिय करने वाले Dan Abramov ने बाद में कहा कि यह कड़ा नियम नहीं है; hooks ने अलग container component की ज़रूरत घटा दी
Re-render: container की state बदलने पर presentational child re-render होता है; भारी हो और props स्थिर हों तो memo लगाओ
Performance: सीधा cost नहीं; साफ सीमाओं से memoization और testing आसान होते हैं
```

---

## 🟡 Real World Example
**Zomato order tracking screen:** The `OrderTrackerContainer` polls the order status API every 10 seconds, handles errors and retries. The `OrderTrackerView` receives `{ status, eta, rider }` and draws the progress bar and rider card. Designers can open `OrderTrackerView` in Storybook with fake data ("Delivered", "Delayed") without any backend, and QA tests each state by passing props.

## 🟡 Real Example Hindi mein
**Zomato order tracking screen:** `OrderTrackerContainer` हर 10 सेकंड में order status API poll करता है, errors और retries संभालता है। `OrderTrackerView` को `{ status, eta, rider }` मिलता है और वह progress bar व rider card बनाता है। Designers `OrderTrackerView` को Storybook में fake data ("Delivered", "Delayed") के साथ बिना backend खोल सकते हैं, और QA हर state props देकर test करता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: Container (logic) + Presentational (UI) for a restaurant list
import { useEffect, useState } from 'react';                    // hooks for the container
import { createRoot } from 'react-dom/client';                   // root API

// PRESENTATIONAL: only props → UI, no fetching, easy to test
function RestaurantListView({ restaurants, loading, error, onRetry }) {
  if (loading) return <p>Loading restaurants...</p>;             // loading UI
  if (error) return <div><p>Failed: {error}</p><button onClick={onRetry}>Retry</button></div>; // error UI
  return (
    <ul>
      {restaurants.map((r) => (                                  // render each restaurant
        <li key={r.id}>{r.name} - {r.rating} stars</li>
      ))}
    </ul>
  );
}

// CONTAINER: data + state + handlers
function RestaurantListContainer() {
  const [restaurants, setRestaurants] = useState([]);            // data state
  const [loading, setLoading] = useState(true);                  // loading state
  const [error, setError] = useState(null);                      // error state
  const [attempt, setAttempt] = useState(0);                     // change to refetch

  useEffect(() => {
    let ignore = false;                                          // avoid setting state after unmount
    setLoading(true); setError(null);
    fetch('https://jsonplaceholder.typicode.com/users')          // demo public API
      .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then((d) => { if (!ignore) setRestaurants(d.map((u) => ({ id: u.id, name: u.name, rating: 4 }))); })
      .catch((e) => { if (!ignore) setError(e.message); })
      .finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };                             // cleanup
  }, [attempt]);

  return (
    <RestaurantListView
      restaurants={restaurants}                                  // pass data down
      loading={loading}
      error={error}
      onRetry={() => setAttempt((a) => a + 1)}                   // pass behavior down
    />
  );
}

createRoot(document.getElementById('root')).render(<RestaurantListContainer />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced (modern): the container is a custom hook; the view stays pure and memoized; logic is testable without React
import { memo, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';

// 1) Pure logic: no React at all → trivial unit tests
export function filterAndSort(items, { veg, sortBy }) {
  const filtered = veg ? items.filter((i) => i.veg) : items;     // filter
  return [...filtered].sort((a, b) =>                            // copy then sort (never mutate)
    sortBy === 'price' ? a.price - b.price : b.rating - a.rating
  );
}

// 2) "Container" as a hook: owns state + derives data
export function useMenu(allItems) {
  const [veg, setVeg] = useState(false);                         // filter state
  const [sortBy, setSortBy] = useState('rating');                // sort state
  const items = useMemo(                                         // derived list, recalculated when needed
    () => filterAndSort(allItems, { veg, sortBy }),
    [allItems, veg, sortBy]
  );
  return { items, veg, sortBy, toggleVeg: () => setVeg((v) => !v), setSortBy };
}

// 3) Presentational: memo skips re-render when props are unchanged
const MenuView = memo(function MenuView({ items, veg, sortBy, onToggleVeg, onSort }) {
  return (
    <section>
      <label><input type="checkbox" checked={veg} onChange={onToggleVeg} /> Veg only</label>
      <select value={sortBy} onChange={(e) => onSort(e.target.value)}>
        <option value="rating">Top rated</option>
        <option value="price">Price: low to high</option>
      </select>
      <ul>{items.map((i) => <li key={i.id}>{i.name} - Rs {i.price} ({i.rating})</li>)}</ul>
    </section>
  );
});

// 4) Thin container component wiring hook → view
const MENU = [
  { id: 1, name: 'Paneer Tikka', price: 220, rating: 4.4, veg: true },
  { id: 2, name: 'Butter Chicken', price: 320, rating: 4.7, veg: false },
  { id: 3, name: 'Dal Makhani', price: 180, rating: 4.5, veg: true },
];
function MenuPage() {
  const m = useMenu(MENU);                                        // logic
  return <MenuView items={m.items} veg={m.veg} sortBy={m.sortBy} onToggleVeg={m.toggleVeg} onSort={m.setSortBy} />;
}

createRoot(document.getElementById('root')).render(<MenuPage />);
```

---

## 🟠 Next.js Connection

In the App Router the pattern is built in: a **Server Component** is the container (fetches data directly, no hooks) and passes plain props to a presentational component, which may be a Server or Client Component. Keep presentational components free of data fetching, so they work in both worlds. Interactive logic stays in a small Client Component (`'use client'`).

```jsx
// app/restaurants/page.jsx (Server Component = Container)
import RestaurantListView from './RestaurantListView';        // presentational, no 'use client' needed
import { getRestaurants } from '@/lib/restaurants';           // hypothetical data layer

export default async function Page() {
  const restaurants = await getRestaurants();                  // data fetching on the server
  return <RestaurantListView restaurants={restaurants} />;     // pass plain serializable props
}

// app/restaurants/RestaurantListView.jsx (Presentational: pure props → UI)
export default function RestaurantListView({ restaurants }) {
  return (
    <ul>
      {restaurants.map((r) => <li key={r.id}>{r.name}</li>)}   {/* no fetch, no state */}
    </ul>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Presentational components that secretly fetch or read global stores
✅ **Correct:** Pass everything through props so they remain pure and testable

```jsx
// Wrong: "view" that calls the API
function PriceTag({ id }) { const p = useSWR('/api/price/' + id); return <b>{p.data}</b>; }   // ❌
// Right
function PriceTag({ price }) { return <b>Rs {price}</b>; }                                      // ✅
```

❌ **Mistake 2:** Splitting everything mechanically (a container for every tiny component)
✅ **Correct:** Split only when logic and view are both non-trivial; use a custom hook for logic

```jsx
// Wrong: ButtonContainer + ButtonView for a button with no logic   // ❌ pure noise
// Right: <Button onClick={...}>Pay</Button>                         // ✅
```

❌ **Mistake 3:** Prop drilling through many presentational layers from the container
✅ **Correct:** Use composition (children/slots) or context for deep data

```jsx
// Wrong: container passes 12 props through 4 view layers
// Right: container renders <Page header={<Header user={user}/>}>...</Page>
```

---

## 🧠 Tricky Interview Question

```jsx
const View = memo(function View({ items, onSelect }) {
  console.log('View render');
  return <ul>{items.map(i => <li key={i} onClick={() => onSelect(i)}>{i}</li>)}</ul>;
});

function Container() {
  const [count, setCount] = useState(0);
  const items = ['a', 'b'];                         // created every render
  const onSelect = (i) => console.log(i);           // created every render
  return <><button onClick={() => setCount(count + 1)}>{count}</button><View items={items} onSelect={onSelect} /></>;
}
```
**Answer:** `View render` prints on every click even though `View` is wrapped in `memo`. `memo` compares props with `Object.is`, and `items` (new array) and `onSelect` (new function) are new references each render, so the comparison fails. Fix by moving `items` outside the component (or `useMemo`) and wrapping `onSelect` in `useCallback`, or rely on the React Compiler to do it automatically.

---

## ⚫ Interview Questions + Answers

Q1: What is the Container/Presentational pattern?
A1: Separating components that handle data and behavior (containers) from components that only render UI based on props (presentational). It improves reuse, testing and clarity.

Q2: How has it changed with hooks?
A2: A custom hook can hold the logic, so you do not need a separate container component. The component calls the hook and renders markup. The separation of concerns remains, only the mechanism changed.

Q3: How does it map to Server Components?
A3: A Server Component fetches data and passes it to presentational components as props. It is a container that never ships to the browser.

Q4: What are the benefits?
A4: Easier testing (view with plain props), reuse of views with different data, Storybook and design iteration without backend, and clearer responsibilities for team members.

Q5: What are its downsides?
A5: More files and indirection, and prop drilling when layers increase. Over-splitting small components adds noise, so apply it where logic and UI are both substantial.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A component mixes complex data logic with complex markup
- The same view must work with different data sources (API, mock, cache)
- You want Storybook/visual tests for every UI state

❌ **Avoid when:**
- The component is tiny and has little logic
- A single custom hook already separates logic cleanly
- Splitting only creates prop drilling and boilerplate

---

## 📊 Visual Diagram

```
 ┌──────────── Container (hook / Server Component) ─────────────┐
 │  fetch data · hold state · handlers · derive values          │
 └───────────────┬──────────────────────────────────────────────┘
        props: { data, loading, error, onRetry }
                 ▼
 ┌──────────── Presentational (View) ───────────────────────────┐
 │  pure function: props → JSX · styles · markup                │
 └──────────────────────────────────────────────────────────────┘
 Test View: pass fake props.   Test logic: run the hook/function alone.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Container | Component with data and logic | Data और logic वाला component |
| Presentational | Component that only renders UI from props | सिर्फ props से UI बनाने वाला component |
| Separation of concerns | Each unit has one responsibility | हर इकाई की एक ज़िम्मेदारी |
| Pure component | Same props give same output | वही props तो वही output |
| Custom hook | Reusable logic function with hooks | Hooks वाला reusable logic function |
| Storybook | Tool to view UI states in isolation | UI states अलग से देखने का tool |
| Serializable props | Props that can cross server/client | Server/client पार जा सकने वाले props |
| Prop drilling | Passing props through many layers | कई layers से props भेजना |

---

## ⚡ 3-Line Summary
**English:**
1. Keep data and logic in a container, and UI in a pure presentational component.
2. Today the container is usually a custom hook or a Server Component.
3. Do not over-split; keep views pure so they are testable and reusable.

**Hindi:**
1. Data और logic container में रखो, और UI एक pure presentational component में।
2. आज container आमतौर पर custom hook या Server Component होता है।
3. ज़्यादा मत बाँटो; views को pure रखो ताकि वे testable और reusable रहें।

---

## ➡️ Next Topic
**147. Adapter Pattern in React** — Backend/third-party data के अलग-अलग format को अपने UI के format में बदलने की परत, ताकि API बदलने पर UI न टूटे।
