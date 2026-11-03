# 148. Atomic Design in React
# हिंदी में: Atomic Design — Components को Atoms से Pages तक व्यवस्थित करना

---

## 🔵 Simple Definition (English)
**Atomic Design** (by Brad Frost) is a way to organise UI into five levels: **atoms** (button, input), **molecules** (search field = label + input + button), **organisms** (header, product grid), **templates** (page layout with placeholders) and **pages** (template filled with real data). Small parts combine into bigger ones.

## 🔵 सरल परिभाषा (Hindi)
**Atomic Design** (Brad Frost का) UI को पाँच स्तरों में बाँटने का तरीका है: **atoms** (button, input), **molecules** (search field = label + input + button), **organisms** (header, product grid), **templates** (placeholders वाला page layout) और **pages** (असली data से भरा template)। छोटे हिस्से मिलकर बड़े बनते हैं।

---

## 🔴 Problem it Solves

As an app grows, `components/` becomes a flat folder with 200 files: `Button`, `Header`, `ProductCardNew`, `ProductCardFinal`, `LoginModal2`. Nobody knows what can be reused, where a new component belongs, or whether changing a button breaks the checkout. Teams also build the same dropdown three times because they cannot find the existing one.

```
PROBLEM: flat folder
components/
  Button.jsx  Header.jsx  Card.jsx  ProductCardNew.jsx  LoginModal2.jsx  SearchStuff.jsx ...
  (what is reusable? what is a page section? what depends on what?)
```

## 🔴 यह क्यों बना? (Hindi)
App बढ़ने पर `components/` एक सपाट folder बन जाता है जिसमें 200 files होती हैं: `Button`, `Header`, `ProductCardNew`, `ProductCardFinal`, `LoginModal2`। किसी को पता नहीं कि क्या दोबारा इस्तेमाल हो सकता है, नया component कहाँ रखें, या button बदलने से checkout टूटेगा या नहीं। Teams एक ही dropdown तीन बार बना देती हैं क्योंकि पहले वाला मिलता ही नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → ATOMS: smallest UI pieces, no business logic (Button, Input, Badge, Icon)
Step 2 → MOLECULES: a few atoms that do one job (SearchField, QuantityStepper)
Step 3 → ORGANISMS: distinct sections made of molecules/atoms (Navbar, RestaurantGrid, CartSummary)
Step 4 → TEMPLATES: page layout with slots, no real data (HomeTemplate = header + grid + footer)
Step 5 → PAGES: a template wired to real data and routes (HomePage fetches data, fills the template)
Step 6 → Rule: a level may use the levels BELOW it, never above (an atom never imports an organism)
Step 7 → Keep data fetching at organism/page level; atoms and molecules take props only

Re-render behavior: atoms/molecules are pure and cheap; wrap hot atoms in React.memo only when
profiling shows wasted renders. State should live as low as possible (a molecule's own input
state) so typing does not re-render the whole page.
Performance impact: reuse means a smaller bundle; clear boundaries make code-splitting by organism easy.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ATOMS: सबसे छोटे UI टुकड़े, business logic नहीं (Button, Input, Badge, Icon)
Step 2 → MOLECULES: कुछ atoms जो एक काम करते हैं (SearchField, QuantityStepper)
Step 3 → ORGANISMS: अलग-अलग sections, molecules/atoms से बने (Navbar, RestaurantGrid, CartSummary)
Step 4 → TEMPLATES: slots वाला page layout, असली data नहीं (HomeTemplate = header + grid + footer)
Step 5 → PAGES: असली data और routes से जुड़ा template (HomePage data लाकर template भरता है)
Step 6 → नियम: एक स्तर सिर्फ नीचे के स्तरों को use कर सकता है, ऊपर वाले को नहीं (atom कभी organism import नहीं करता)
Step 7 → Data fetching organism/page स्तर पर रखो; atoms और molecules सिर्फ props लेते हैं

Re-render behavior: atoms/molecules pure और सस्ते होते हैं; React.memo तभी लगाओ जब profiling में
बेकार renders दिखें। State जितनी नीचे हो सके रखो (molecule की अपनी input state) ताकि typing से
पूरा page re-render न हो।
Performance impact: reuse से bundle छोटा; साफ़ सीमाओं से organism के हिसाब से code-splitting आसान।
```

---

## 🟡 Real World Example
**Swiggy home screen:** Atoms: `Button`, `Rating`, `Image`. Molecule: `RestaurantMeta` (Rating + delivery time + cost). Organism: `RestaurantCard`, then `RestaurantGrid` (many cards plus a filter bar). Template: `HomeTemplate` (top bar, filter row, grid slot, footer). Page: `HomePage` fetches restaurants for your location and puts them into the template. Changing the `Rating` star colour updates every card, search result and cart item.

## 🟡 Real Example Hindi mein
**Swiggy home screen:** Atoms: `Button`, `Rating`, `Image`। Molecule: `RestaurantMeta` (Rating + delivery time + cost)। Organism: `RestaurantCard`, फिर `RestaurantGrid` (कई cards और filter bar)। Template: `HomeTemplate` (top bar, filter row, grid slot, footer)। Page: `HomePage` आपकी location के restaurants लाकर template में रखता है। `Rating` का star colour बदलने से हर card, search result और cart item बदल जाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: atoms -> molecule -> organism, in one file for easy copy-paste
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

// ATOM: a button with no business logic
function Button({ children, onClick, disabled }) {
  return <button onClick={onClick} disabled={disabled}>{children}</button>; // only UI + props
}

// ATOM: a text input
function Input({ value, onChange, placeholder }) {
  return <input value={value} onChange={onChange} placeholder={placeholder} />; // controlled by parent
}

// MOLECULE: Input + Button doing one job (search)
function SearchField({ onSearch }) {
  const [text, setText] = useState('');                       // state lives low: only this molecule re-renders
  return (
    <div>
      <Input value={text} onChange={(e) => setText(e.target.value)} placeholder="Search dishes" />
      <Button onClick={() => onSearch(text)} disabled={!text.trim()}>Search</Button>
    </div>
  );
}

// ORGANISM: a section with a molecule and a list
function DishSection({ dishes, onSearch }) {
  return (
    <section>
      <SearchField onSearch={onSearch} />                      {/* molecule */}
      <ul>{dishes.map((d) => <li key={d}>{d}</li>)}</ul>       {/* list of results */}
    </section>
  );
}

function App() {
  const all = ['Biryani', 'Dosa', 'Paneer Tikka'];             // fake data
  const [shown, setShown] = useState(all);                     // filtered result
  const search = (q) => setShown(all.filter((d) => d.toLowerCase().includes(q.toLowerCase())));
  return <DishSection dishes={shown} onSearch={search} />;
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Template with slots + Page that owns the data + folder structure
//
// src/components/
//   atoms/       Button.jsx  Rating.jsx  Badge.jsx
//   molecules/   RestaurantMeta.jsx  SearchField.jsx
//   organisms/   RestaurantCard.jsx  RestaurantGrid.jsx  Navbar.jsx
//   templates/   HomeTemplate.jsx
//   pages/       HomePage.jsx
import { memo, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

// ---- atoms ----
const Rating = memo(function Rating({ value }) {              // memo: pure, rendered many times in lists
  return <span aria-label={`Rated ${value}`}>★ {value.toFixed(1)}</span>;
});
const Badge = ({ children }) => <small style={{ background: '#eee', padding: '0 6px' }}>{children}</small>;

// ---- molecule ----
const RestaurantMeta = memo(function RestaurantMeta({ rating, eta, cost }) {
  return (
    <p>
      <Rating value={rating} /> · {eta} min · Rs. {cost} for two   {/* atoms combined */}
    </p>
  );
});

// ---- organisms ----
const RestaurantCard = memo(function RestaurantCard({ restaurant }) {
  return (
    <article>
      <h3>{restaurant.name} {restaurant.promoted && <Badge>Ad</Badge>}</h3>
      <RestaurantMeta rating={restaurant.rating} eta={restaurant.eta} cost={restaurant.cost} />
    </article>
  );
});

function RestaurantGrid({ restaurants }) {
  if (restaurants.length === 0) return <p>No restaurants found</p>; // empty state belongs to the organism
  return <div>{restaurants.map((r) => <RestaurantCard key={r.id} restaurant={r} />)}</div>;
}

// ---- template: layout only, receives content through slots, never fetches ----
function HomeTemplate({ header, filters, content, footer }) {
  return (
    <div>
      <header>{header}</header>
      <nav>{filters}</nav>
      <main>{content}</main>
      <footer>{footer}</footer>
    </div>
  );
}

// ---- page: owns data and state, fills the template ----
function HomePage() {
  const [restaurants, setRestaurants] = useState([]);          // server data
  const [loading, setLoading] = useState(true);                // loading flag
  useEffect(() => {
    let ignore = false;                                         // avoid setting state after unmount
    Promise.resolve([                                           // replace with fetch('/api/restaurants')
      { id: 1, name: 'Meghana Foods', rating: 4.5, eta: 32, cost: 800, promoted: true },
      { id: 2, name: 'MTR', rating: 4.3, eta: 25, cost: 500 },
    ]).then((data) => { if (!ignore) { setRestaurants(data); setLoading(false); } });
    return () => { ignore = true; };                            // cleanup
  }, []);
  return (
    <HomeTemplate
      header={<h1>FoodApp</h1>}
      filters={<Badge>Rating 4.0+</Badge>}
      content={loading ? <p>Loading...</p> : <RestaurantGrid restaurants={restaurants} />}
      footer={<p>© FoodApp</p>}
    />
  );
}

createRoot(document.getElementById('root')).render(<HomePage />);
```

---

## 🟠 Next.js Connection

In the App Router, atoms and molecules are usually **Server Components** with no `'use client'` (they are pure UI), so they ship no JS. Only interactive organisms (search, cart steppers) are Client Components. Next.js `app/page.jsx` plays the **page** role and `layout.jsx` plays the **template** role.

```jsx
// app/page.jsx (page: Server Component, fetches data and fills the template)
import HomeTemplate from '@/components/templates/HomeTemplate';   // layout without data
import RestaurantGrid from '@/components/organisms/RestaurantGrid'; // server-rendered organism
import SearchField from '@/components/molecules/SearchField';      // has 'use client' (typing state)
import { getRestaurants } from '@/lib/restaurants';                // server data function

export default async function Page() {
  const restaurants = await getRestaurants();                     // data fetched on the server
  return (
    <HomeTemplate
      header={<h1>FoodApp</h1>}
      filters={<SearchField />}                                    // small client island
      content={<RestaurantGrid restaurants={restaurants} />}       // zero client JS
      footer={<p>© FoodApp</p>}
    />
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Atoms that fetch data or know business rules
✅ **Correct:** Atoms take only props; data and rules live in organisms or pages

```jsx
// Wrong: Button knows about the cart API
function AddButton({ id }) { return <button onClick={() => fetch(`/cart/${id}`)}>Add</button>; } // ❌
// Right: Button is generic; the organism passes onClick
<Button onClick={() => addToCart(id)}>Add</Button>                                                 // ✅
```

❌ **Mistake 2:** Importing upward (a molecule importing an organism)
✅ **Correct:** Dependencies point down only; pass upper parts in as `children` or slots

```jsx
// Wrong: molecules/SearchField.jsx
import Navbar from '../organisms/Navbar';          // ❌ circular, tight coupling
// Right: SearchField exposes onSearch; Navbar imports SearchField           ✅
```

❌ **Mistake 3:** Following the five levels too rigidly (arguing whether a component is a molecule or an organism)
✅ **Correct:** Use the levels as a guide; the goal is reuse and clear dependency direction

```jsx
// Wrong: 40 tiny files for a one-time <div>               ❌
// Right: promote a component to a shared level only when a second place needs it  ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function SearchField({ onSearch }) {
  const [text, setText] = useState('');
  return <input value={text} onChange={(e) => { setText(e.target.value); onSearch(e.target.value); }} />;
}
function Page() {
  const [q, setQ] = useState('');
  console.log('Page render');
  return <><SearchField onSearch={setQ} /><HugeGrid query={q} /></>;
}
```
**Answer:** `Page render` (and `HugeGrid`) re-run on every keystroke because the molecule lifts state up with `onSearch` on each change. Atomic Design suggests keeping state as low as possible: keep `text` inside the molecule and call `onSearch` only on submit or after a debounce (or wrap `HugeGrid` in `React.memo` and deferred value). The structure is fine; the data flow decides performance.

---

## ⚫ Interview Questions + Answers

Q1: What are the five levels of Atomic Design?
A1: Atoms, molecules, organisms, templates, pages. Atoms are basic elements, molecules combine atoms for one function, organisms are full sections, templates define layout without real data, and pages are templates with real content.

Q2: How does it relate to React components?
A2: React components compose naturally, so each level is a component that renders lower levels. It is a naming and folder convention, not a library.

Q3: Where should state and data fetching live?
A3: Atoms and molecules should be presentational (props in, UI out) except for small local UI state. Organisms and pages own data fetching, global state and side effects. In Next.js, fetch in Server Components at page or organism level.

Q4: What are the drawbacks?
A4: Debates about categories, many small files, and the risk of premature abstraction. Some teams use feature-based folders (`features/cart/...`) with a shared atomic `ui/` folder instead.

Q5: How does it help with design systems and Storybook?
A5: Atoms and molecules map directly to design tokens and stories in Storybook, so design and code share vocabulary. Visual regression tests per atom catch style changes early.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You build or maintain a design system with many reusable components
- Several teams share a UI library and need a clear structure
- You want consistent look and easy theming

❌ **Avoid when:**
- The app is tiny (a few screens): a simple folder is enough
- Features are very independent (feature-based folders may work better)
- The team spends more time naming levels than shipping

---

## 📊 Visual Diagram

```
 ATOMS        MOLECULES          ORGANISMS            TEMPLATES            PAGES
 [Button]  ┐
 [Input]   ├► [SearchField] ─┐
 [Rating]  ┐                 ├► [Navbar]      ─┐
 [Badge]   ├► [RestaurantMeta]► [RestaurantCard]├► [HomeTemplate] ─► [HomePage]
 [Image]   ┘                 │   [RestaurantGrid]┘   (layout slots)    (real data)
                             └──────────────────

 Dependency direction:  page → template → organism → molecule → atom   (never upward)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Atom | Smallest UI element | सबसे छोटा UI तत्व |
| Molecule | Group of atoms with one job | एक काम करने वाले atoms का समूह |
| Organism | Complex UI section | जटिल UI section |
| Template | Layout with placeholders | Placeholders वाला layout |
| Page | Template with real data | असली data वाला template |
| Design system | Shared UI rules and components | साझा UI नियम व components |
| Presentational | Props in, UI out | केवल props से UI बनाना |
| Design tokens | Shared colours, spacing values | साझा रंग व spacing मान |

---

## ⚡ 3-Line Summary
**English:**
1. Atomic Design organises UI as atoms, molecules, organisms, templates and pages.
2. Dependencies only point downward; data fetching lives in organisms and pages.
3. Use it as a guide for reuse and clarity, and keep state low to avoid extra re-renders.

**Hindi:**
1. Atomic Design UI को atoms, molecules, organisms, templates और pages में व्यवस्थित करता है।
2. Dependencies सिर्फ नीचे की ओर जाती हैं; data fetching organisms और pages में होती है।
3. इसे reuse और स्पष्टता का guide मानो, और अनावश्यक re-renders से बचने के लिए state नीचे रखो।

---

## ➡️ Next Topic
**149. Micro Frontends Basics** — जब app इतना बड़ा हो जाए कि कई teams को अलग-अलग deploy करना हो, तब UI को स्वतंत्र हिस्सों (micro frontends) में बाँटा जाता है।
