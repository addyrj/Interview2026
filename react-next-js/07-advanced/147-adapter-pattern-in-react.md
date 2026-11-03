# 147. Adapter Pattern in React
# हिंदी में: Adapter Pattern — बाहरी Data/Library को अपने UI के अनुकूल बनाना

---

## 🔵 Simple Definition (English)
The **Adapter pattern** puts a small translation layer between something you do not control (an API response, a third-party library) and your components. Components only know your own clean shape; the adapter converts the outside shape into it.

## 🔵 सरल परिभाषा (Hindi)
**Adapter pattern** में उस चीज़ (API response, third-party library) जिस पर आपका control नहीं है और आपके components के बीच एक छोटी translation layer होती है। Components सिर्फ आपका साफ़ shape जानते हैं; adapter बाहर के shape को उसमें बदल देता है।

---

## 🔴 Problem it Solves

Backend fields are often ugly or inconsistent: `snake_case`, nested, nullable, prices in paise, dates as strings. If components read these directly, the ugly shape spreads across the whole app. When the backend changes `rest_nm` to `restaurant_name`, you must edit dozens of components. Similarly, if you use a date-picker library directly everywhere, replacing it later is a rewrite.

```jsx
// PROBLEM: components know the raw backend shape
<h3>{data.rest_nm}</h3>                          // backend naming leaks into UI
<p>Rs. {data.cost_for_two_paise / 100}</p>       // conversion repeated in many files
<span>{data.deliv?.eta_mins ?? 'NA'} min</span>  // null handling repeated everywhere
```

## 🔴 यह क्यों बना? (Hindi)
Backend के fields अक्सर बेढंगे होते हैं: `snake_case`, nested, nullable, कीमत paise में, तारीख string में। Components सीधे इन्हें पढ़ें तो यह बेढंगा shape पूरे app में फैल जाता है। Backend `rest_nm` को `restaurant_name` कर दे तो दर्जनों components बदलने पड़ते हैं। इसी तरह date-picker library हर जगह सीधे इस्तेमाल करें तो बाद में उसे बदलना पूरा rewrite बन जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the shape your UI wants (a "view model"), e.g. { id, name, costForTwo, etaMinutes }
Step 2 → Write a pure function toRestaurant(raw) that maps raw API data to that shape
Step 3 → Handle defaults, null values, unit conversion and renaming inside the adapter only
Step 4 → Call the adapter at the edge: in the fetch function, queryFn `select`, or server loader
Step 5 → Components receive the clean shape and never see the raw one
Step 6 → For libraries: wrap them in your own component with your own props (a wrapper adapter)
Step 7 → If the backend or library changes, you edit ONE file

Re-render behavior: adapt once in the data layer (or memoise with useMemo); do not map in render
on every keystroke, or objects get new identities and break React.memo.
Performance impact: adapter work is tiny; the benefit is stable object shapes and easy changes.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → UI जो shape चाहता है उसे तय करो ("view model"), जैसे { id, name, costForTwo, etaMinutes }
Step 2 → Pure function toRestaurant(raw) लिखो जो raw API data को उस shape में बदले
Step 3 → Defaults, null values, unit conversion और rename सिर्फ adapter के अंदर संभालो
Step 4 → Adapter को किनारे पर call करो: fetch function, queryFn का `select`, या server loader में
Step 5 → Components को साफ़ shape मिलता है, raw shape वे कभी नहीं देखते
Step 6 → Libraries के लिए: उन्हें अपने component में अपने props के साथ wrap करो (wrapper adapter)
Step 7 → Backend या library बदले तो सिर्फ एक file बदलनी पड़ती है

Re-render behavior: data layer में एक बार adapt करो (या useMemo); हर keystroke पर render में map मत करो,
वरना objects की identity बदलती है और React.memo बेकार हो जाता है।
Performance impact: adapter का काम बहुत छोटा है; फायदा स्थिर shape और आसान बदलाव का है।
```

---

## 🟡 Real World Example
**Zomato restaurant list:** The mobile API, the web API and a partner API all send restaurant data in different shapes (`rest_nm`, `name`, `restaurantName`). One `toRestaurant()` adapter per source converts each into the same `{ id, name, costForTwo, etaMinutes, isOpen }`. The `RestaurantCard` component never changes when a new source is added. The same idea applies to a payment SDK: your `PayButton` wraps Razorpay or Stripe behind one interface.

## 🟡 Real Example Hindi mein
**Zomato restaurant list:** Mobile API, web API और partner API restaurant data अलग-अलग shape में भेजते हैं (`rest_nm`, `name`, `restaurantName`)। हर source के लिए एक `toRestaurant()` adapter उसे एक ही `{ id, name, costForTwo, etaMinutes, isOpen }` में बदलता है। नया source जुड़ने पर `RestaurantCard` नहीं बदलता। यही विचार payment SDK पर लागू होता है: आपका `PayButton` Razorpay या Stripe को एक interface के पीछे छिपाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: a data adapter function + a component that only knows the clean shape
import { createRoot } from 'react-dom/client';

// Raw data as the backend sends it (ugly on purpose)
const raw = { rest_id: 7, rest_nm: 'Meghana Foods', cost_for_two_paise: 80000, deliv: { eta_mins: 32 } };

// ADAPTER: pure function, maps raw -> view model, handles defaults
function toRestaurant(r) {
  return {
    id: r.rest_id,                                   // rename
    name: r.rest_nm ?? 'Unknown',                    // default for missing names
    costForTwo: Math.round((r.cost_for_two_paise ?? 0) / 100), // paise -> rupees
    etaMinutes: r.deliv?.eta_mins ?? null,           // safe nested access
  };
}

// COMPONENT: knows nothing about rest_nm or paise
function RestaurantCard({ restaurant }) {
  return (
    <div>
      <h3>{restaurant.name}</h3>                      {/* clean name */}
      <p>Rs. {restaurant.costForTwo} for two</p>      {/* already in rupees */}
      <p>{restaurant.etaMinutes ? `${restaurant.etaMinutes} min` : 'ETA unavailable'}</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<RestaurantCard restaurant={toRestaurant(raw)} />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: multiple source adapters + a library wrapper adapter + adapting in a hook
import { useMemo, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

// --- 1. Several sources, one output shape ---------------------------------
const adapters = {
  mobile: (r) => ({ id: r.rest_id, name: r.rest_nm, costForTwo: r.cost_for_two_paise / 100 }),
  web: (r) => ({ id: r.id, name: r.name, costForTwo: r.costForTwo }),
  partner: (r) => ({ id: r.restaurantId, name: r.restaurantName, costForTwo: Number(r.avgCost) }),
};

function normalize(source, items) {
  const adapt = adapters[source];                       // choose adapter by source
  if (!adapt) throw new Error(`No adapter for ${source}`); // fail loudly on unknown source
  return items.map(adapt);                              // map each raw item
}

// --- 2. Adapter around a third-party library (swap vendor without touching UI) ---
// Our own stable interface: <PayButton amount onSuccess onFailure />
const gateways = {
  razorpay: ({ amount, onSuccess }) => () => {          // returns the click handler
    // real code: new window.Razorpay({ key, amount: amount * 100, handler: onSuccess }).open();
    onSuccess({ gateway: 'razorpay', paid: amount });   // simulated result
  },
  stripe: ({ amount, onSuccess }) => () => {
    // real code: stripe.confirmPayment({ ... });
    onSuccess({ gateway: 'stripe', paid: amount });
  },
};

function PayButton({ amount, gateway = 'razorpay', onSuccess }) {
  const pay = gateways[gateway]({ amount, onSuccess });  // adapt vendor API to our props
  return <button onClick={pay}>Pay Rs. {amount}</button>;
}

// --- 3. Adapt once in a hook, memoised so identities stay stable ---------------
function useRestaurants(source, rawItems) {
  return useMemo(() => normalize(source, rawItems), [source, rawItems]); // recompute only if inputs change
}

const mobileData = [{ rest_id: 1, rest_nm: 'Meghana', cost_for_two_paise: 80000 }];

function App() {
  const restaurants = useRestaurants('mobile', mobileData); // clean shape for the UI
  const [paid, setPaid] = useState(null);
  useEffect(() => { console.log('adapted', restaurants); }, [restaurants]);
  return (
    <div>
      {restaurants.map((r) => <p key={r.id}>{r.name} - Rs. {r.costForTwo}</p>)}
      <PayButton amount={500} gateway="stripe" onSuccess={setPaid} />
      {paid && <p>Paid via {paid.gateway}</p>}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

---

## 🟠 Next.js Connection

In the App Router, put the adapter in the **server data layer** so the raw shape never reaches the browser. This also shrinks the payload sent to Client Components, since you pass only fields the UI needs. It works the same with TanStack Query's `select` option on the client.

```jsx
// lib/restaurants.js (server-side data function with adapter)
import 'server-only';                                  // never bundle this for the browser

function toRestaurant(r) {                             // adapter
  return { id: r.rest_id, name: r.rest_nm, costForTwo: r.cost_for_two_paise / 100 };
}

export async function getRestaurants() {
  const res = await fetch('https://api.example.com/restaurants', { next: { revalidate: 60 } }); // ISR-style cache
  const raw = await res.json();                        // raw backend data
  return raw.items.map(toRestaurant);                  // only the clean shape leaves this file
}
```

```jsx
// app/restaurants/page.jsx (Server Component)
import { getRestaurants } from '@/lib/restaurants';

export default async function Page() {
  const list = await getRestaurants();                 // already adapted
  return <ul>{list.map((r) => <li key={r.id}>{r.name}</li>)}</ul>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Adapting inside the component body on every render and passing new objects to memoised children
✅ **Correct:** Adapt in the data layer, in `select`, or with `useMemo`

```jsx
// Wrong: new array of new objects on every render → React.memo(Child) never skips
function List({ raw }) {
  const items = raw.map(toRestaurant);                 // ❌ new identities each render
  return <Child items={items} />;
}
// Right
function List({ raw }) {
  const items = useMemo(() => raw.map(toRestaurant), [raw]); // ✅ stable until raw changes
  return <Child items={items} />;
}
```

❌ **Mistake 2:** Leaking raw fields through "just one" component (`data.rest_nm` in a deep child)
✅ **Correct:** Only the adapter touches raw fields; add the field to the view model if the UI needs it

```jsx
<h3>{restaurant.name}</h3>        {/* ✅ view-model field */}
// <h3>{restaurant.raw.rest_nm}</h3>  ❌ defeats the pattern
```

❌ **Mistake 3:** Adapters with side effects or hidden fetching
✅ **Correct:** Keep adapters pure (same input → same output), easy to unit test

```jsx
// Wrong: adapter mutates input and logs
function toRestaurant(r) { r.name = r.rest_nm; console.log('x'); return r; } // ❌
// Right: returns a new object
function toRestaurant(r) { return { name: r.rest_nm }; }                      // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
const Card = React.memo(function Card({ restaurant }) {
  console.log('Card render');
  return <p>{restaurant.name}</p>;
});

function Page({ raw }) {
  const [q, setQ] = useState('');
  const restaurant = { id: raw.rest_id, name: raw.rest_nm };   // adapter inline
  return (
    <>
      <input value={q} onChange={(e) => setQ(e.target.value)} />
      <Card restaurant={restaurant} />
    </>
  );
}
```
**Answer:** `Card render` logs on every keystroke even though `Card` is wrapped in `React.memo`. Each render of `Page` builds a new `restaurant` object, and `memo` compares props with `Object.is`, so the prop looks changed. Fix: `useMemo(() => ({...}), [raw])` or adapt outside the component (in the fetch layer), so the object identity stays the same until `raw` changes.

---

## ⚫ Interview Questions + Answers

Q1: What is the Adapter pattern in React?
A1: A function or wrapper that converts one interface to another: backend data to a UI-friendly view model, or a third-party library's API to your own component props. It isolates changes.

Q2: Where should the adapter live?
A2: At the boundary, as close to the data source as possible: the fetch function, server loader, RTK Query `transformResponse`, or TanStack Query `select`. Components then never see raw data.

Q3: How is it different from the Facade and Decorator patterns?
A3: Adapter changes the shape of an interface to match what the client expects. Facade simplifies a complex subsystem behind a simpler interface. Decorator adds behaviour while keeping the same interface (a React HOC is closer to this).

Q4: How do you test an adapter?
A4: Because it is a pure function, write unit tests with sample raw objects, including edge cases such as missing fields, nulls and unexpected types. No React rendering is needed.

Q5: Can adapters hurt performance?
A5: The mapping cost is usually negligible. The real risk is creating new object identities in render, which breaks memoisation. Adapt once (data layer or `useMemo`), and for huge lists adapt on the server or in a worker.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- API shape is messy, unstable or differs between sources
- You depend on a third-party library you may replace (payments, maps, charts, date pickers)
- You migrate old and new APIs side by side

❌ **Avoid when:**
- The API already returns exactly what the UI needs (extra layer, no gain)
- You wrap every tiny library "just in case" (over-engineering)
- You use TypeScript types only to rename fields in one place (a direct mapping is fine)

---

## 📊 Visual Diagram

```
  Mobile API  { rest_nm, cost_for_two_paise }  ─┐
  Web API     { name, costForTwo }             ─┼─► [ ADAPTERS ] ─► { id, name, costForTwo }
  Partner API { restaurantName, avgCost }      ─┘        pure             │
                                                                          ▼
                                                              <RestaurantCard />  (one version)

  Library adapter:
  <PayButton amount=500>  ─►  gateways[razorpay | stripe]  ─►  vendor SDK
         (our API)              (adapter)                      (their API)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Adapter | Converts one interface into another | एक interface को दूसरे में बदलने वाला |
| View model | Shape the UI wants | UI के लिए चाहा गया shape |
| DTO | Raw data object from API | API से आया raw data object |
| Wrapper | Component around a library | Library के चारों ओर component |
| select | Query option to transform data | Data बदलने वाला query option |
| Pure function | Same input, same output, no side effects | बिना side effect वाला function |
| Boundary | Edge between outside and your code | बाहर और आपके code की सीमा |
| Vendor lock-in | Hard to switch a library | Library बदलना मुश्किल होना |

---

## ⚡ 3-Line Summary
**English:**
1. An adapter translates external data or library APIs into the clean shape your components expect.
2. Keep it pure, put it at the data boundary, and memoise or adapt once to keep object identity stable.
3. Components stay unchanged when the backend or vendor changes; only the adapter is edited.

**Hindi:**
1. Adapter बाहरी data या library API को उस साफ़ shape में बदलता है जो आपके components चाहते हैं।
2. इसे pure रखो, data की सीमा पर रखो, और object identity स्थिर रखने के लिए memoise करो या एक बार adapt करो।
3. Backend या vendor बदलने पर components नहीं बदलते; सिर्फ adapter बदलता है।

---

## ➡️ Next Topic
**148. Atomic Design in React** — अब data की जगह UI को structure करना सीखेंगे: atoms, molecules, organisms, templates और pages में components को व्यवस्थित करना।
