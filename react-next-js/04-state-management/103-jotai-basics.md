# 103. Jotai Basics
# हिंदी में: Jotai Basics — Atoms से Global State

---

## 🔵 Simple Definition (English)
**Jotai** is an atomic state library for React. State is split into small pieces called **atoms**. Each atom is created with `atom(initialValue)`, and components read it with `useAtom` (value + setter) or `useAtomValue`. A **derived atom** computes its value from other atoms, and only components that read the atoms they depend on re-render. No big store and no Provider are required.

## 🔵 सरल परिभाषा (Hindi)
**Jotai** React के लिए एक atomic state library है। State को छोटे-छोटे टुकड़ों में बाँटा जाता है, जिन्हें **atoms** कहते हैं। हर atom `atom(initialValue)` से बनता है, और components `useAtom` (value + setter) या `useAtomValue` से उसे पढ़ते हैं। **Derived atom** दूसरे atoms से अपनी value निकालता है, और सिर्फ वही components re-render होते हैं जो उन atoms को पढ़ते हैं। कोई बड़ा store या Provider ज़रूरी नहीं।

---

## 🔴 Problem it Solves
Context में एक बड़ा object रखो तो कोई भी एक field बदलने पर उस Context के सारे consumers re-render होते हैं। Redux में store एक ही है, और selectors सुनने का काम करते हैं, पर छोटे features के लिए बहुत सारा setup लगता है। कई बार हमें सिर्फ इतना चाहिए: हर छोटी value अपने आप में global हो, और उसे बदलने पर सिर्फ उसी को पढ़ने वाले components अपडेट हों।

**Flipkart-style example:** Product page पर selected size, selected color और quantity तीन अलग-अलग atoms हैं। Quantity बदलने पर सिर्फ quantity वाला component re-render होता है, size और color वाले नहीं। Total price एक derived atom है जो quantity और price से बनता है।

## 🔴 यह क्यों बना? (Hindi)
Recoil ने atom model दिखाया, पर उसके साथ extra complexity आई। Jotai ने वही विचार सरल रखा: atom एक plain value है, कोई key नहीं, कोई string id नहीं, और derived atoms सीधे दूसरे atoms से जुड़ते हैं। नतीजा: छोटा API, Provider optional, और React के बाहर भी `createStore()` से काम।

---

## 🟢 How it Works — Step by Step

```
Step 1 → atom(initialValue) से एक atom बनाओ
         const countAtom = atom(0);

Step 2 → Derived atom: getter function (get) => लिखो
         const doubleAtom = atom((get) => get(countAtom) * 2);

Step 3 → Component useAtom(countAtom) से value और setter लेता है
         const [count, setCount] = useAtom(countAtom);

Step 4 → Jotai default store में atom की value रखता है
         (Provider तभी चाहिए जब अलग-अलग isolated stores चाहिए)

Step 5 → Atom बदलने पर सिर्फ उस atom के subscribers (components और derived atoms) अपडेट होते हैं
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → atom(initialValue) से atom बनाओ
Step 2 → Derived atom (get) => ... में दूसरे atoms पढ़ता है
Step 3 → useAtom(atom) value और setter देता है
Step 4 → Default store atom values संभालता है; Provider सिर्फ अलग stores के लिए
Step 5 → Atom बदलने पर सिर्फ उसके subscribers re-render होते हैं
```

---

## 🟡 Real World Example
**Swiggy-style product page:** Dish page पर "Quantity" बदलने पर "Total" अपडेट होना चाहिए, पर "Veg/Non-veg" filter का component नहीं। Quantity atom बदलता है, `totalAtom` (derived) नया total निकालता है, और सिर्फ total दिखाने वाला component re-render होता है। Header का cart badge अपने `cartCountAtom` को पढ़ता है, जो इस बदलाव से अलग है, इसलिए वह भी re-render नहीं होता।

## 🟡 Real Example Hindi mein
**Swiggy-style dish page:** "Quantity" बदलने पर "Total" अपडेट होना चाहिए, पर "Veg/Non-veg" filter वाला component नहीं। Quantity atom बदलता है, `totalAtom` (derived) नया total निकालता है, और सिर्फ total दिखाने वाला component re-render होता है। Header का cart badge अपने `cartCountAtom` को पढ़ता है, जो इस बदलाव से अलग है, इसलिए वह भी re-render नहीं होता।

---

## 💻 Code Example — Basic

```javascript
// Basic: atom, derived atom, createStore — ESM file (.mjs ya "type": "module")
import { atom, createStore } from 'jotai';                         // atom banane aur store banane ke functions
const countAtom = atom(0);                                         // ek atom = ek chhota state tukda, default 0
const doubleAtom = atom((get) => get(countAtom) * 2);              // derived: countAtom par depend karta hai
const store = createStore();                                       // store (React ke bahar bhi chalta hai)
console.log(store.get(countAtom), store.get(doubleAtom));          // 0 0
store.set(countAtom, 5);                                           // countAtom ko 5 set karo
console.log(store.get(countAtom), store.get(doubleAtom));          // 5 10
// Expected output:
// 0 0
// 5 10
```

## 💻 Code Example — Advanced

```javascript
// Advanced: atomWithStorage, write-only action atom, derived total, subscription count — ESM file (.mjs)
import { atom, createStore } from 'jotai';                          // core API
import { atomWithStorage, createJSONStorage } from 'jotai/utils';   // utils: storage-backed atom

// Browser mein localStorage hota hai; Node mein nahi, isliye memory storage (same interface) use karte hain
const memory = new Map();                                           // key-value store
const memoryStorage = {                                             // string storage interface
  getItem: (key) => memory.get(key) ?? null,                        // missing key par null
  setItem: (key, value) => memory.set(key, value),                  // string save
  removeItem: (key) => memory.delete(key),                          // delete
};

const cartAtom = atomWithStorage('cart', [], createJSONStorage(() => memoryStorage)); // localStorage-backed atom
const addToCartAtom = atom(null, (get, set, item) => {              // write-only action atom (value nahi, sirf setter)
  set(cartAtom, [...get(cartAtom), item]);                          // naya array banakar cart update
});
const totalAtom = atom((get) =>                                     // derived: cart se total nikalo
  get(cartAtom).reduce((sum, item) => sum + item.price, 0)
);

const store = createStore();                                        // isolated store (test ke liye useful)
let updates = 0;                                                    // totalAtom kitni baar badla
const unsub = store.sub(totalAtom, () => { updates += 1; });        // subscription: totalAtom badle to callback
store.set(addToCartAtom, { id: 'P1', price: 120 });                 // item 1
store.set(addToCartAtom, { id: 'P2', price: 80 });                  // item 2
console.log('total:', store.get(totalAtom));                        // total: 200
console.log('saved items:', JSON.parse(memory.get('cart')).length); // saved items: 2
console.log('updates:', updates);                                   // updates: 2
unsub();                                                            // subscription band karo
// Expected output:
// total: 200
// saved items: 2
// updates: 2
```

---

## 🟠 Real app integration

Next.js App Router mein Jotai default store se kaam chalta hai, Provider zaroori nahi. Client Component mein `useAtom` value aur setter deta hai, aur `useSetAtom` sirf setter chahiye to component re-render nahi hota jab value badle. (Syntax-level snippet.)

```jsx
// lib/atoms.js — module level par atoms
import { atom } from 'jotai';                                        // atom banane ke liye
export const quantityAtom = atom(1);                                 // quantity, default 1
export const pricePerItemAtom = atom(180);                           // price, default 180
export const totalAtom = atom((get) => get(quantityAtom) * get(pricePerItemAtom)); // derived total

```

```jsx
// components/Quantity.jsx — value aur setter dono
'use client';
import { useAtom } from 'jotai';                                     // value + setter hook
import { quantityAtom } from '@/lib/atoms';                          // atom import
export default function Quantity() {
  const [qty, setQty] = useAtom(quantityAtom);                       // qty padho aur badlo
  return (
    <div>
      <button onClick={() => setQty((q) => Math.max(1, q - 1))}>-</button> {/* minimum 1 */}
      <span>{qty}</span>
      <button onClick={() => setQty((q) => q + 1)}>+</button>
    </div>
  );
}

```

```jsx
// components/ResetButton.jsx — sirf setter, value nahi, isliye re-render nahi
'use client';
import { useSetAtom } from 'jotai';                                  // sirf setter hook
import { quantityAtom } from '@/lib/atoms';
export default function ResetButton() {
  const setQty = useSetAtom(quantityAtom);                           // setter only
  return <button onClick={() => setQty(1)}>Reset</button>;           // qty ko 1 par set
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Component ke andar atom banana
✅ **Correct:** Atom module level par banao, warna har render par naya atom aur state reset

```jsx
// Wrong
function QuantityWrong() {
  const qtyAtom = atom(1);                             // ❌ har render par naya atom, state reset
  const [qty, setQty] = useAtom(qtyAtom);
  return <button onClick={() => setQty(qty + 1)}>{qty}</button>;
}

// Right
const qtyAtomRight = atom(1);                          // ✅ module level, ek hi atom
function QuantityRight() {
  const [qty, setQty] = useAtom(qtyAtomRight);
  return <button onClick={() => setQty(qty + 1)}>{qty}</button>;
}
```

❌ **Mistake 2:** Sirf setter chahiye, par `useAtom` le liya
✅ **Correct:** Sirf update chahiye to `useSetAtom`, sirf read chahiye to `useAtomValue`

```jsx
// Wrong
const [, setQty] = useAtom(quantityAtom);              // ❌ value unused, par har change par re-render

// Right
const setQtyRight = useSetAtom(quantityAtom);          // ✅ value subscribe nahi, re-render nahi
```

---

## 🧠 Tricky Interview Question

```javascript
// ESM file (.mjs) — derived atom kab dobara compute hota hai?
import { atom, createStore } from 'jotai';                         // core API
const nameAtom = atom('Asha');                                     // naam atom
const countAtom = atom(0);                                         // count atom (naam se alag)
let computeCount = 0;                                              // derived function kitni baar chala
const greetingAtom = atom((get) => {                               // derived: sirf nameAtom padhta hai
  computeCount += 1;                                               // compute count badhao
  return `Hi ${get(nameAtom)}`;                                    // greeting string
});
const store = createStore();                                       // store
store.get(greetingAtom);                                           // (1) pehli baar
store.get(greetingAtom);                                           // (2) dobara
store.set(countAtom, 1);                                           // (3) count badla, name nahi
store.get(greetingAtom);                                           // (4)
store.set(nameAtom, 'Ravi');                                       // (5) name badla
console.log(store.get(greetingAtom), computeCount);                // (6) kya print hoga?
```

**Answer:** Output is `Hi Ravi 2`. Reasoning: Jotai derived atom ki value cache karta hai, aur dependency (`nameAtom`) badle bina dobara compute nahi karta. (1) mein compute hua (count = 1). (2) mein cache se mila. (3) mein `countAtom` badla, jo `greetingAtom` ka dependency hi nahi hai, isliye compute nahi hua. (4) cache se mila. (5) mein `nameAtom` badla, to (6) mein `store.get` ne dobara compute kiya (count = 2) aur naya string diya. Lesson: derived atom sirf jo atoms `get` se padhta hai, unhi par depend karta hai.

---

## ⚫ Interview Questions + Answers

**Q1: Jotai mein atom kya hai?**
A1: Ek chhota state unit jo `atom(initialValue)` se banta hai. Value default store mein rehti hai, aur components ya dusre atoms use subscribe karte hain.

**Q2: Derived atom kaise kaam karta hai?**
A2: `atom((get) => ...)` function diya jaata hai. `get(otherAtom)` se jo atom padha jaata hai, woh dependency ban jaata hai. Dependency badle to derived atom dobara compute hota hai.

**Q3: `useAtom`, `useAtomValue`, `useSetAtom` mein kya fark hai?**
A3: `useAtom` value aur setter dono deta hai. `useAtomValue` sirf value (read-only), aur `useSetAtom` sirf setter. Sirf setter wale component ko value ke change par re-render ki zarurat nahi hoti.

**Q4: Provider kab chahiye?**
A4: Default store ke bajay isolated state chahiye (jaise ek hi page par do alag instances, ya tests mein fresh state), tab `<Provider>` ya `createStore()` ka use hota hai.

**Q5: Write-only atom kya hai?**
A5: `atom(null, (get, set, arg) => ...)` jisme sirf setter hota hai, value nahi. Yeh action ki tarah kaam karta hai: `useSetAtom(addToCartAtom)` se call hota hai aur business logic ek jagah rehti hai.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- State chhote tukdon mein baantna hai, aur har tukda independent re-render chahiye
- Derived values (total, filtered list) bina manual sync ke chahiye
- Form fields ya UI toggles ko global karna hai
- Suspense-friendly async atoms chahiye

❌ **Avoid when:**
- Ek bade object ke saath aana aur usme ek tarah ki centralized business logic chahiye: Redux Toolkit better hai
- Server data cache chahiye: RTK Query ya TanStack Query
- Team ko single store aur strict DevTools flow chahiye
- Atoms ko component ke andar banane ka plan hai: yeh bug hai

---

## 📊 Visual Diagram

```
  Atoms (module level)
  ┌──────────────┐    ┌──────────────┐
  │ quantityAtom │    │ priceAtom    │
  │     = 2      │    │    = 180     │
  └──────┬───────┘    └──────┬───────┘
         │ get()             │ get()
         └──────────┬────────┘
                    ▼
         ┌──────────────────────┐
         │ totalAtom (derived)  │  = 360  (cached until qty/price change)
         └──────────┬───────────┘
                    │
     ┌──────────────┼────────────────┐
     ▼              ▼                ▼
 <Total/>       <Quantity/>      <Header cart/>
 useAtomValue   useAtom(qty)     cartCountAtom (alag atom)
 re-render      re-render        NO re-render on qty change
 on total       on qty           (sirf apne atom par)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| atom | Chhota state unit | छोटा state unit |
| Primitive atom | `atom(initial)` se bana atom | `atom(initial)` से बना atom |
| Derived atom | `get` se doosre atoms par depend karne wala atom | दूसरे atoms पर depend करने वाला atom |
| Write-only atom | Sirf setter wala atom (action) | सिर्फ setter वाला atom (action) |
| useAtom | Value + setter dene wala hook | Value और setter देने वाला hook |
| useSetAtom | Sirf setter hook | सिर्फ setter वाला hook |
| atomWithStorage | localStorage se sync hone wala atom | localStorage से sync होने वाला atom |
| createStore | Isolated store banane wala function | Isolated store बनाने वाला function |

---

## ⚡ 3-Line Summary
**English:**
1. Jotai state ko `atom(initialValue)` ke chhote tukdon mein rakhta hai, aur `useAtom` se components jude rehte hain.
2. Derived atoms `get` se dependencies track karte hain, aur sirf zaroori components re-render hote hain.
3. Provider optional hai; `useSetAtom` aur `useAtomValue` se re-render aur bhi kam kiya ja sakta hai.

**Hindi:**
1. Jotai state को `atom(initialValue)` के छोटे टुकड़ों में रखता है, और `useAtom` से components जुड़े रहते हैं।
2. Derived atoms `get` से dependencies track करते हैं, और सिर्फ ज़रूरी components re-render होते हैं।
3. Provider optional है; `useSetAtom` और `useAtomValue` से re-render और भी कम किया जा सकता है।

---

## ➡️ Next Topic
**104. Recoil Basics** — Facebook की atom और selector model, जो Jotai जैसी है, पर इसका ecosystem और status अलग है (Recoil maintenance mode में है), इसलिए इसे पढ़कर compare करना interview में काम आता है।
