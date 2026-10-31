# 104. Recoil Basics
# हिंदी में: Recoil Basics — atom और selector वाला State Model

> **Status note:** Recoil (Meta) की GitHub README के अनुसार यह project **maintenance mode** में है, यानी नए features लगभग नहीं आ रहे। नए projects के लिए Jotai, Zustand या Redux Toolkit को प्राथमिकता दो, और interview में यह status ज़रूर बताओ। Concepts (atoms, selectors) समझने के लिए यह topic अब भी उपयोगी है।

---

## 🔵 Simple Definition (English)
**Recoil** is a React state library from Meta built on two ideas: **atoms** (units of shared state that components can subscribe to) and **selectors** (derived state computed from atoms or other selectors). Wrap your app in `<RecoilRoot>` (the store boundary), then read and write atoms with hooks like `useRecoilState`, `useRecoilValue`, and `useSetRecoilState`.

## 🔵 सरल परिभाषा (Hindi)
**Recoil** Meta की React state library है, जो दो विचारों पर बनी है: **atoms** (shared state के छोटे tukde, जिन्हें components subscribe करते हैं) और **selectors** (atoms या दूसरे selectors से निकाला गया derived state)। App को `<RecoilRoot>` में लपेटो (यही store की boundary है), फिर `useRecoilState`, `useRecoilValue`, `useSetRecoilState` से atoms पढ़ो और लिखो।

---

## 🔴 Problem it Solves
React का `useState` एक component तक सीमित है। Props drilling से कई levels नीचे तक state भेजना पड़ता है। Context से एक बड़ा object सबको भेजो तो एक field बदलने पर सभी consumers re-render होते हैं। Derived values (जैसे filtered list या total) हर जगह अलग से गणना करनी पड़ती हैं।

**Zomato-style filter example:** Restaurant list पर "Veg only", "Price range" और "Rating" filters हैं। Filters एक atom में हैं, filtered list एक selector में है (जो filters पढ़ता है), और list, count badge व empty-state सब उसी selector से पढ़ते हैं। Filters बदलें तो सिर्फ जुड़े हुए components अपडेट होते हैं।

## 🔴 यह क्यों बना? (Hindi)
Meta को ऐसा state चाहिए था जो React की तरह component-based हो, पर global हो, और derived values को भी सही तरीके से track करे। Recoil ने atoms (छोटे shared state) और selectors (derived state) का model दिया, जिसमें dependencies अपने आप track होती हैं। Context के मुकाबले फायदा यह है कि हर atom अलग subscription है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → atom({ key, default }) से shared state का tukda बनाओ
         const filterVegState = atom({ key: 'filterVeg', default: false });

Step 2 → selector({ key, get }) से derived state बनाओ
         get(filterVegState) से dependency बनती है

Step 3 → App को <RecoilRoot> में लपेटो (यह अलग-अलग state stores की boundary है)

Step 4 → Component hooks से पढ़ता या लिखता है
         useRecoilState(atom)   → [value, setter]
         useRecoilValue(sel)    → sirf value (selector ke liye)
         useSetRecoilState(atom)→ sirf setter

Step 5 → Atom बदलने पर सिर्फ उस atom या selector पर subscribe components re-render होते हैं
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → atom({ key, default }) से shared state
Step 2 → selector({ key, get }) से derived state; get() dependency बनाता है
Step 3 → <RecoilRoot> state store की boundary है
Step 4 → useRecoilState / useRecoilValue / useSetRecoilState से पढ़ो/लिखो
Step 5 → सिर्फ subscribe components अपडेट होते हैं
```

---

## 🟡 Real World Example
**Zomato restaurant filters:** User "Veg only" चालू करता है। `filterVegState` बदलता है, `filteredRestaurantsState` selector नई list निकालता है, और list व "X restaurants found" badge दोनों उसी selector से अपडेट होते हैं। Header का "Login" button किसी atom को नहीं पढ़ता, इसलिए वह re-render नहीं होता।

## 🟡 Real Example Hindi mein
**Zomato restaurant filters:** User "Veg only" चालू करता है। `filterVegState` बदलता है, `filteredRestaurantsState` selector नई list निकालता है, और list व "X restaurants found" badge दोनों उसी selector से अपडेट होते हैं। Header का "Login" button किसी atom को नहीं पढ़ता, इसलिए वह re-render नहीं होता।

---

## 💻 Code Example — Basic

```jsx
// Basic: atom + useRecoilState + RecoilRoot — self-contained JSX
// Node mein JSX chalane ke liye esbuild/Babel se transpile karte hain; yahan test ke liye renderToString use hua
import React from 'react';                                             // JSX ke liye React
import { RecoilRoot, atom, useRecoilState } from 'recoil';           // Recoil ke main exports
import { renderToString } from 'react-dom/server';                    // server par HTML banane ke liye (test)

const countState = atom({                                             // atom: shared state ka ek tukda
  key: 'countState',                                                  // poore app mein unique key
  default: 0,                                                         // shuruaati value
});

function Counter() {                                                  // component jo atom padhta hai
  const [count, setCount] = useRecoilState(countState);               // value + setter (useState jaisa)
  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>; // click par +1
}

function App() {                                                      // root component
  return (
    // Recoil state ki boundary (zaroori)
    <RecoilRoot>
      {/* atom ka reader */}
      <Counter />
    </RecoilRoot>
  );
}

console.log(renderToString(<App />));                                 // server HTML print
// Expected output (React server rendering text nodes ke beech comment dalta hai):
// <button>Count: <!-- -->0</button>
```

## 💻 Code Example — Advanced

```jsx
// Advanced: atomFamily, selector, selectorFamily, effects, initializeState — self-contained JSX
import React from 'react';                                            // JSX
import {                                                              // Recoil APIs
  RecoilRoot, atom, atomFamily, selector, selectorFamily, useRecoilValue, useSetRecoilState,
} from 'recoil';
import { renderToString } from 'react-dom/server';                    // test ke liye server render

// Effect: atom ke lifecycle mein side-effect (yahan sirf change par log, real app mein analytics/storage)
const logCartEffect = ({ onSet }) => {                                // effect function ko Recoil argument deta hai
  onSet((newValue) => {                                               // har set par chalta hai
    console.log('[effect] cart size now', newValue.length);           // side-effect (SSR mein nahi chalta)
  });
};

const cartState = atom({                                              // cart ka atom
  key: 'cart',                                                        // unique key
  default: [],                                                        // shuruaat: khaali cart
  effects: [logCartEffect],                                           // effects ki list
});

const cartTotalState = selector({                                     // derived: cart ka total
  key: 'cartTotal',                                                   // unique key
  get: ({ get }) => get(cartState).reduce((sum, item) => sum + item.price * item.qty, 0), // dependency: cartState
});

const dishPriceState = selectorFamily({                               // parameterized selector (id se price)
  key: 'dishPrice',                                                   // unique key
  get: (dishId) => ({ get }) => ({ P1: 180, P2: 120 })[dishId] ?? 0,  // dishId param, default 0
});

const dishQtyState = atomFamily({                                     // parameterized atom: har dish ki alag quantity
  key: 'dishQty',                                                     // unique key
  default: 1,                                                         // har dish ki default quantity
});

function CartSummary() {                                              // total dikhane wala component
  const total = useRecoilValue(cartTotalState);                       // selector: sirf value
  const p1 = useRecoilValue(dishPriceState('P1'));                    // family selector: P1 ki price
  const qtyP1 = useRecoilValue(dishQtyState('P1'));                   // family atom: P1 ki quantity
  return <p>Total: {total} | P1: {p1} x {qtyP1}</p>;                  // summary line
}

function AddButton() {                                                // sirf setter wala component
  const setCart = useSetRecoilState(cartState);                       // setter only: re-render value par nahi
  return <button onClick={() => setCart((c) => [...c, { id: 'P2', price: 120, qty: 1 }])}>Add</button>;
}

function Menu() {                                                     // dono components ko compose karta hai
  return <div><CartSummary /><AddButton /></div>;                     // summary + button
}

const initialCart = [{ id: 'P1', price: 180, qty: 2 }];               // server par initial data

console.log(renderToString(                                           // RecoilRoot ko initializeState do
  <RecoilRoot initializeState={({ set }) => set(cartState, initialCart)}>
    <Menu />
  </RecoilRoot>
));
// Expected output:
// <div><p>Total: <!-- -->360<!-- --> | P1: <!-- -->180<!-- --> x <!-- -->1</p><button>Add</button></div>
```

---

## 🟠 Real app integration

Next.js App Router mein `RecoilRoot` ek Client Component wrapper mein rakhte hain, kyunki Recoil hooks client par chalte hain. Atoms module level par define karte hain, aur `key` har atom ke liye unique hona chahiye. (Syntax-level snippet.)

```jsx
// app/providers.jsx — Recoil root ek client wrapper mein
'use client';                                                         // hooks client par chalenge
import { RecoilRoot } from 'recoil';                                  // store boundary
export function Providers({ children }) {                             // children = pages
  return <RecoilRoot>{children}</RecoilRoot>;                         // sab components ko state access
}

```

```jsx
// lib/filters.js — atoms aur selector module level par
import { atom, selector } from 'recoil';
export const filterVegState = atom({ key: 'filterVeg', default: false });       // veg-only toggle
export const restaurantsState = atom({ key: 'restaurants', default: [] });      // API se aaya data
export const filteredRestaurantsState = selector({                             // derived list
  key: 'filteredRestaurants',
  get: ({ get }) => {
    const veg = get(filterVegState);                                  // dependency 1
    const list = get(restaurantsState);                               // dependency 2
    return veg ? list.filter((r) => r.isVeg) : list;                 // filter lagao ya nahi
  },
});

```

```jsx
// components/RestaurantList.jsx — selector se list aur count
'use client';
import { useRecoilValue } from 'recoil';
import { filteredRestaurantsState } from '@/lib/filters';
export default function RestaurantList() {
  const list = useRecoilValue(filteredRestaurantsState);              // derived list
  return <p>{list.length} restaurants mile</p>;                       // count dikhao
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Duplicate `key` values dena
✅ **Correct:** Har atom/selector ka `key` poore app mein unique rakho, warna dev mein error aata hai

```jsx
// Wrong
const userAtom = atom({ key: 'user', default: null });       // ❌ key 'user'
const cartAtomX = atom({ key: 'user', default: [] });        // ❌ same key: duplicate error

// Right
const userAtomR = atom({ key: 'userProfile', default: null }); // ✅ unique key
const cartAtomR = atom({ key: 'userCart', default: [] });      // ✅ unique key
```

❌ **Mistake 2:** Selector ke andar state mutate karna ya `set` jaisa kaam karna
✅ **Correct:** Selector sirf pure computation kare; state badalne ke liye atom ka setter use karo

```jsx
// Wrong
const totalSel = selector({
  key: 'totalWrong',
  get: ({ get }) => {
    const items = get(cartAtomR);
    items.push({ id: 'X', price: 0, qty: 1 });          // ❌ selector mein mutation, side-effect
    return items.length;
  },
});

// Right
const countSel = selector({
  key: 'countRight',
  get: ({ get }) => get(cartAtomR).length,              // ✅ pure: sirf read aur compute
});
// Badlne ke liye component mein useSetRecoilState(cartAtomR) se setter lo
```

---

## 🧠 Tricky Interview Question

```jsx
// Self-contained JSX — do RecoilRoot ek saath render hote hain
import React from 'react';                                            // JSX
import { RecoilRoot, atom, useRecoilValue } from 'recoil';           // Recoil
import { renderToString } from 'react-dom/server';                    // server render

const baseState = atom({ key: 'base', default: 2 });                 // default 2

function Show() {                                                     // atom ki value dikhane wala
  const value = useRecoilValue(baseState);                            // value padho
  return <span>{value}</span>;                                        // span mein value
}

const html = renderToString(                                          // do roots, ek saath
  <>
    {/* root A: 5 set */}
    <RecoilRoot initializeState={({ set }) => set(baseState, 5)}>
      <Show />
    </RecoilRoot>
    {/* root B: default */}
    <RecoilRoot>
      <Show />
    </RecoilRoot>
  </>
);
console.log(html);                                                    // kya print hoga?
```

**Answer:** Output is `<span>5</span><span>2</span>`. Reasoning: har `<RecoilRoot>` apna alag state store banata hai. Same atom (`baseState`) dono roots mein hai, lekin root A ke `initializeState` ne uski value 5 kar di, aur root B ne koi initialization nahi ki, isliye usne default 2 hi dekha. Atom ki definition (key aur default) shared hai, par value har root ke andar alag rehti hai. Isi wajah se tests mein har test ko fresh `RecoilRoot` dena achha hota hai.

---

## ⚫ Interview Questions + Answers

**Q1: Recoil mein atom aur selector mein kya fark hai?**
A1: Atom ek writable state unit hai jo `default` se shuru hota hai. Selector derived read-only value hai jo `get` se atoms ya dusre selectors padhta hai, aur dependencies badlne par dobara compute hota hai.

**Q2: `useRecoilState`, `useRecoilValue`, `useSetRecoilState` kab use karein?**
A2: `useRecoilState` value aur setter dono ke liye. `useRecoilValue` sirf read ke liye (selectors ke liye bhi). `useSetRecoilState` sirf write ke liye, jisse component value par subscribe nahi hota.

**Q3: `<RecoilRoot>` ka role kya hai?**
A3: Yeh state store ki boundary hai. Saare atoms ki values is root ke andar rehti hain. Alag roots ki values alag hoti hain.

**Q4: Atom family aur selector family kyon hain?**
A4: Jab ek hi type ki kai parameterized values chahiye (jaise har dish ki quantity, ya dishId se price), tab `atomFamily(...)` aur `selectorFamily(...)` ek template dete hain, aur param ke hisaab se alag atom/selector milta hai.

**Q5: Recoil ke status ke baare mein interview mein kya bolna chahiye?**
A5: Recoil maintenance mode mein hai (README ke hisaab se), isliye nayi projects mein Jotai, Zustand ya Redux Toolkit ko prefer karna chahiye. Recoil ki concepts (atoms, selectors) samajhna purane codebases aur comparisons ke liye zaroori hai.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Existing codebase mein Recoil pehle se hai, aur migration ka plan nahi hai
- Derived state ke liye selectors ka clean model chahiye aur Recoil team ke pattern se mel khata hai
- Parameterized state (families) ki zarurat ho

❌ **Avoid when:**
- Naya project shuru ho raha hai: Jotai ya Zustand behtar active options hain
- Maintenance mode ke kaaran long-term support ki chinta ho
- Sirf server data cache chahiye: RTK Query ya TanStack Query
- Ek component ka local state hai: `useState` kaafi hai

---

## 📊 Visual Diagram

```
<RecoilRoot>                       ← state store ki boundary
   │
   ├── atom: filterVegState = false
   ├── atom: restaurantsState = [...]
   │
   └── selector: filteredRestaurantsState
          get(filterVegState) ──┐
          get(restaurantsState) ┴── returns filtered list
                 │
     ┌───────────┴────────────┐
     ▼                        ▼
 <RestaurantList/>       <CountBadge/>
 useRecoilValue(sel)     useRecoilValue(sel)
 (re-render on change)   (re-render on change)

 <FilterToggle/>
 useSetRecoilState(filterVegState)   ← sirf setter, value par subscribe nahi
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| atom | Shared, writable state unit | Shared, writable state का tukda |
| selector | Derived, computed state | Derived, computed state |
| RecoilRoot | State store ki boundary | State store की boundary |
| key | Atom/selector ki unique pehchan | Atom/selector की unique पहचान |
| atomFamily | Parameter ke hisaab se alag atoms | Parameter के हिसाब से अलग atoms |
| selectorFamily | Parameter ke hisaab se alag selectors | Parameter के हिसाब से अलग selectors |
| effects | Atom lifecycle mein side-effects | Atom के lifecycle में side-effects |
| initializeState | RecoilRoot ki shuruaati values | RecoilRoot की शुरुआती values |

---

## ⚡ 3-Line Summary
**English:**
1. Recoil ka model atoms (shared state) aur selectors (derived state) par hai, aur `<RecoilRoot>` store ki boundary hai.
2. Hooks `useRecoilState`, `useRecoilValue`, `useSetRecoilState` se components sirf apne atoms par subscribe hote hain.
3. Recoil maintenance mode mein hai, isliye naye projects mein Jotai ya Zustand ko prefer karo, aur Recoil ke concepts ko comparison ke liye samjho.

**Hindi:**
1. Recoil का model atoms (shared state) और selectors (derived state) पर है, और `<RecoilRoot>` store की boundary है।
2. Hooks `useRecoilState`, `useRecoilValue`, `useSetRecoilState` से components सिर्फ अपने atoms पर subscribe होते हैं।
3. Recoil maintenance mode में है, इसलिए नए projects में Jotai या Zustand चुनो, और Recoil के concepts comparison के लिए समझो।

---

## ➡️ Next Topic
**105. When to Use Which State Manager** — Context, useState, Zustand, Jotai, Recoil और Redux Toolkit में से कौन सा कब चुनें, इसका decision framework, जो इस पूरे section को समेटता है।
