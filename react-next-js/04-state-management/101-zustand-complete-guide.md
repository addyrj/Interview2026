# 101. Zustand — Complete Guide
# हिंदी में: Zustand — Complete Guide (हल्की और सरल Global State)

---

## 🔵 Simple Definition (English)
**Zustand** is a small global state library built around a single `create()` call. It returns a React hook that components use to read slices of state, and the same store can be read and changed outside React with `getState()` and `setState()`. There is no Provider, no action types, and very little boilerplate. The `persist` middleware can save state to `localStorage`.

## 🔵 सरल परिभाषा (Hindi)
**Zustand** एक छोटी global state library है, जो एक `create()` call के चारों ओर बनी है। यह एक React hook लौटाता है, जिससे components state का हिस्सा पढ़ते हैं। वही store React के बाहर `getState()` और `setState()` से भी पढ़ा और बदला जा सकता है। इसमें न Provider होता है, न action types, और boilerplate बहुत कम है। `persist` middleware state को `localStorage` में save कर सकता है।

---

## 🔴 Problem it Solves
Context API से global state बनाओ तो हर value बदलने पर उस Provider के सारे consumers re-render होते हैं। Redux में सब कुछ सही है, पर छोटे feature के लिए बहुत सारी files (slice, actions, store, Provider) लिखनी पड़ती हैं। कई apps को बस इतना चाहिए: एक store, कुछ actions, और components सिर्फ जो चाहिए वही सुनें।

**Swiggy-style cart example:** Cart की items header badge, checkout page और restaurant page तीनों को चाहिए। Zustand में एक store बनता है, badge सिर्फ `items.length` select करता है, और cart बदलने पर बाकी components re-render नहीं होते जब तक उनका selected हिस्सा न बदले।

## 🔴 यह क्यों बना? (Hindi)
Redux का mental model भारी लगता था छोटे apps के लिए। Context से performance समस्या थी। Zustand ने बीच का रास्ता दिया: एक plain JavaScript store, selector-based subscription (सिर्फ जो बदला वही re-render), और कोई Provider जरूरी नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → create() को एक function दो जो (set, get) लेता है
         const useCart = create((set, get) => ({ items: [], add: ... }))

Step 2 → create() दो चीज़ें लौटाता है: एक hook और store API
         useCart(selector)  → React component में
         useCart.getState() → React के बाहर पढ़ो

Step 3 → Component selector देता है: useCart((s) => s.items.length)
         Zustand पुरानी और नई selected value compare करता है (Object.is)

Step 4 → set() call होने पर state merge होती है (top-level shallow merge)
         सिर्फ selected value बदली तो सिर्फ वही component re-render होता है

Step 5 → persist middleware हर बदलाव को storage (localStorage) में लिख देता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → create((set, get) => ({...})) से store बनाओ
Step 2 → Hook React में और getState()/setState() React के बाहर इस्तेमाल होता है
Step 3 → Component selector देता है; Zustand सिर्फ selected value compare करता है
Step 4 → set() top-level merge करता है; सिर्फ बदली value वाले components re-render होते हैं
Step 5 → persist middleware state को localStorage में save करता है
```

---

## 🟡 Real World Example
**Swiggy cart badge:** Header में cart count दिखता है, और cart page पूरी list दिखाता है। दोनों एक Zustand store से जुड़े हैं। User एक item add करता है, तो `add` action store अपडेट करता है। Header सिर्फ `items.length` पर subscribe है, इसलिए उसका count बदलता है, और cart page की list भी अपडेट होती है। Browser refresh के बाद cart `persist` की वजह से वापस आ जाता है।

## 🟡 Real Example Hindi mein
**Swiggy cart badge:** Header में cart count दिखता है और cart page पूरी list दिखाता है। दोनों एक Zustand store से जुड़े हैं। User एक item add करता है, तो `add` action store अपडेट करता है। Header सिर्फ `items.length` पर subscribe है, इसलिए उसका count बदलता है और cart page की list भी अपडेट होती है। Browser refresh के बाद cart `persist` की वजह से वापस आ जाता है।

---

## 💻 Code Example — Basic

```javascript
// Basic: create() se store, actions, getState, subscribe — ESM file (.mjs ya "type": "module")
import { create } from 'zustand';                                  // zustand ka main function
const useCounterStore = create((set) => ({                         // store: state + actions ek jagah
  count: 0,                                                        // state
  increment: () => set((state) => ({ count: state.count + 1 })),   // action: sirf count update
  reset: () => set({ count: 0 }),                                  // seedha value set karna
}));
useCounterStore.getState().increment();                            // React ke bahar bhi action chalta hai
useCounterStore.getState().increment();                            // ab count 2 hai
console.log(useCounterStore.getState().count);                     // 2
const unsubscribe = useCounterStore.subscribe((state, prev) =>     // har change par listener
  console.log('changed from', prev.count, 'to', state.count));     // old aur new value
useCounterStore.getState().increment();                            // listener chalega
unsubscribe();                                                     // listener band karo
useCounterStore.getState().reset();                                // count 0 par
console.log(useCounterStore.getState().count);                     // 0
// Expected output:
// 2
// changed from 2 to 3
// 0
```

## 💻 Code Example — Advanced

```javascript
// Advanced: persist middleware + partialize + version/migrate — ESM file (.mjs)
import { create } from 'zustand';                                  // hook-based store
import { persist, createJSONStorage } from 'zustand/middleware';   // persist + JSON adapter

// Browser mein localStorage hota hai; Node mein nahi, isliye memory storage (same interface) use karte hain
const memory = new Map();                                          // key-value store
const memoryStorage = {                                            // StateStorage interface: get/set/remove
  getItem: (name) => memory.get(name) ?? null,                     // key na ho to null
  setItem: (name, value) => memory.set(name, value),               // string save karo
  removeItem: (name) => memory.delete(name),                       // key delete karo
};
const storage = typeof localStorage !== 'undefined' ? localStorage : memoryStorage; // browser par localStorage
// Purane version (1) ka saved data pehle se pada hai, jaise user ne pichli baar cart banaya tha
memory.set('cart-store', JSON.stringify({ state: { items: [{ id: 'P1', qty: 2 }], coupon: 'SAVE10' }, version: 1 }));

const useCartStore = create()(                                     // create()() curried form (TypeScript friendly)
  persist(
    (set, get) => ({                                               // state aur actions
      items: [],                                                   // cart items
      coupon: null,                                                // applied coupon
      addItem: (item) => set((s) => ({ items: [...s.items, item] })), // immutable update
      total: () => get().items.reduce((sum, i) => sum + i.price * i.qty, 0), // derived value
      clear: () => set({ items: [], coupon: null }),               // cart reset
    }),
    {
      name: 'cart-store',                                          // storage key
      version: 2,                                                  // schema ka current version
      storage: createJSONStorage(() => storage),                   // JSON serialize/parse adapter
      partialize: (state) => ({ items: state.items, coupon: state.coupon }), // functions save nahi honge
      migrate: (persisted, fromVersion) => {                       // purane data ko naye shape mein badlo
        if (fromVersion === 1) {                                   // version 1 se aaya data
          return { ...persisted, items: persisted.items.map((i) => ({ ...i, price: i.price ?? 0 })) };
        }
        return persisted;                                          // baaki versions ke liye same
      },
    }
  )
);

console.log('hydrated items:', useCartStore.getState().items.length); // hydrated items: 1
useCartStore.getState().addItem({ id: 'P2', name: 'Naan', price: 150, qty: 1 }); // naya item
console.log('total:', useCartStore.getState().total());              // total: 150
const saved = JSON.parse(memory.get('cart-store'));                 // storage mein kya save hua
console.log('saved version:', saved.version, 'items:', saved.state.items.length); // saved version: 2 items: 2
// Expected output:
// hydrated items: 1
// total: 150
// saved version: 2 items: 2
```

---

## 🟠 Real app integration

Next.js mein server par `localStorage` nahi hota, isliye `persist` ke storage ko `typeof window` se guard karte hain. Client Component mein selector se sirf zaroori hissa lete hain. (Yeh snippet syntax-level example hai.)

```jsx
// store/cartStore.js — client-only persist store
import { create } from 'zustand';                                   // store banane ke liye
import { persist, createJSONStorage } from 'zustand/middleware';    // persist middleware
const noopStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} }; // server ke liye no-op
export const useCartStore = create()(
  persist(
    (set) => ({
      items: [],                                                    // cart items
      add: (item) => set((s) => ({ items: [...s.items, item] })),   // immutable add
    }),
    {
      name: 'cart',                                                 // localStorage key
      storage: createJSONStorage(() =>
        typeof window !== 'undefined' ? window.localStorage : noopStorage // server par crash nahi
      ),
      skipHydration: true,                                          // SSR mismatch se bachne ke liye
    }
  )
);

```

```jsx
// components/AddButton.jsx — selectors se sirf zaroori hissa
'use client';
import { useEffect } from 'react';                                  // effect hook
import { useCartStore } from '@/store/cartStore';                   // hook
export default function AddButton({ dish }) {
  const add = useCartStore((s) => s.add);                           // sirf action select: count badle to bhi re-render nahi
  const count = useCartStore((s) => s.items.length);                // sirf count select
  useEffect(() => { useCartStore.persist.rehydrate(); }, []);       // client par saved data load karo
  return <button onClick={() => add(dish)}>Add ({count})</button>;  // button + count
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Poora store select karna
✅ **Correct:** Selector se sirf zaroori value lo, warna har change par re-render

```jsx
// Wrong
function CartBadge() {
  const store = useCartStore();                       // ❌ poora store: koi bhi change = re-render
  return <span>{store.items.length}</span>;
}

// Right
function CartBadgeFixed() {
  const count = useCartStore((s) => s.items.length);  // ✅ sirf count par re-render
  return <span>{count}</span>;
}
```

❌ **Mistake 2:** State ko directly mutate karna
✅ **Correct:** `set` ke zariye naya object/array banao, mutation se UI update nahi hota

```javascript
// Wrong
const addWrong = (item) => {
  useCartStore.getState().items.push(item);           // ❌ same array mutate, koi re-render nahi
};

// Right
const addRight = (item) => {
  useCartStore.setState((s) => ({ items: [...s.items, item] })); // ✅ naya array, subscribers ko pata chalega
};
```

---

## 🧠 Tricky Interview Question

```javascript
// ESM file (.mjs) — setState merge ka test
import { create } from 'zustand';                                   // store library
const useStore = create(() => ({ user: { name: 'Asha' }, theme: 'dark' })); // initial state
useStore.setState({ theme: 'light' });                              // (A) top-level merge
console.log(JSON.stringify(useStore.getState()));                   // (1)
useStore.setState({ user: { age: 20 } });                          // (B) user object replace
console.log(JSON.stringify(useStore.getState()));                   // (2)
useStore.setState({ theme: 'blue' }, true);                        // (C) replace = true
console.log(JSON.stringify(useStore.getState()));                   // (3)
console.log(typeof useStore.getState().user);                       // (4)
```

**Answer:** Output is:
```
{"user":{"name":"Asha"},"theme":"light"}
{"user":{"age":20},"theme":"light"}
{"theme":"blue"}
undefined
```
Reasoning: `setState` default mein top-level merge karta hai. (A) mein sirf `theme` badla, `user` waisa hi raha. (B) mein `user` ko naya object diya gaya, aur Zustand nested object ko deep merge nahi karta, isliye `name` gaya. (C) mein `replace = true` ne poora state hi badal diya, isliye `user` ab exist hi nahi karta, aur `typeof` `undefined` deta hai. Nested update ke liye spread use karo: `set((s) => ({ user: { ...s.user, age: 20 } }))`.

---

## ⚫ Interview Questions + Answers

**Q1: Zustand mein Provider kyon nahi chahiye?**
A1: Store ek module-level variable hai (`create` ka return), isliye koi bhi component import karke use kar sakta hai. Context ki zarurat nahi, aur store React tree ke bahar bhi accessible rehta hai.

**Q2: Selector kya hai aur kyon zaroori hai?**
A2: Selector `(state) => value` function hai. Zustand sirf selected value compare karta hai (`Object.is`), isliye component sirf us value ke badalne par re-render hota hai.

**Q3: Object ya array select karne par kya problem hoti hai?**
A3: `useStore((s) => ({ a: s.a, b: s.b }))` har render par naya object banata hai, to `Object.is` hamesha false, aur infinite re-render ka khatra hai. Zustand v5 mein `useShallow` (`zustand/react/shallow`) se wrap karo.

**Q4: `persist` middleware kaise kaam karta hai?**
A4: Har `set` ke baad `partialize` se chuna hissa storage (localStorage) mein JSON ke roop mein save hota hai. Startup par `persist` saved data ko state mein merge karta hai. `version` aur `migrate` purane data ko naye shape mein badalte hain.

**Q5: Zustand ko Redux ke bajay kab chunein?**
A5: Chhote se medium apps, ya jab boilerplate kam chahiye aur middleware/DevTools jaisa ecosystem zaroori ho tab. Bahut bade team-based apps mein Redux ke strict patterns kaam aate hain (topic 102 mein comparison hai).

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Global state chahiye, par Redux ka boilerplate nahi chahiye
- Kai components ko same chhota state chahiye (cart, theme, filters)
- React ke bahar bhi store read/write karna hai (utils, event handlers)
- State ko localStorage mein save karna hai (`persist`)

❌ **Avoid when:**
- State sirf ek parent-child ke beech hai: props ya `useState` kaafi hain
- Server data cache chahiye: RTK Query ya TanStack Query better hain
- Team ko Redux ke strict patterns aur time-travel debugging chahiye
- Ek hi value ke liye poori store library: `useState` ya Context kaafi hai

---

## 📊 Visual Diagram

```
create((set, get) => ({ count, increment }))
                │
                ▼
      ┌──────────────────────┐
      │   Zustand STORE      │◀── set() : shallow merge ──┐
      │  { count: 2, ... }   │                            │
      └──────────┬───────────┘                            │
                 │ subscribers (selector compare)         │
     ┌───────────┼──────────────────────┐                 │
     ▼           ▼                      ▼                 │
 Header        CartPage             AddButton ── add() ──┘
 select:       select:              select:
 items.length  items (array)        add (function)
 re-render     re-render            no re-render
 on count      on items change      (function ref same)

 persist middleware ──▶ localStorage["cart-store"] (partialize ke baad)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| create | Store banane wala function | Store बनाने वाला function |
| Selector | State ka hissa chunne wala function | State का हिस्सा चुनने वाला function |
| getState / setState | React ke bahar state padhna/badalna | React के बाहर state पढ़ना/बदलना |
| set | State update function (merge hota hai) | State update करने वाला function (merge होता है) |
| persist | State ko storage mein save karne wala middleware | State को storage में save करने वाला middleware |
| partialize | Save hone wala hissa chunna | Save होने वाला हिस्सा चुनना |
| useShallow | Object/array selectors ke liye shallow compare | Object/array selectors के लिए shallow compare |
| migrate | Purane persisted data ko naye shape mein badalna | पुराने data को नए shape में बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. `create()` ek store aur React hook deta hai, bina Provider ke.
2. Selectors se component sirf zaroori value par re-render hota hai; `set` state ko top-level merge karta hai.
3. `persist` se state localStorage mein save hoti hai, `partialize` aur `version/migrate` ke saath.

**Hindi:**
1. `create()` बिना Provider के एक store और React hook देता है।
2. Selectors से component सिर्फ ज़रूरी value पर re-render होता है; `set` state को top-level merge करता है।
3. `persist` से state localStorage में save होती है, `partialize` और `version/migrate` के साथ।

---

## ➡️ Next Topic
**102. Zustand vs Redux** — दोनों libraries की तुलना: boilerplate, DevTools, middleware, team size और performance के आधार पर, ताकि interview में सही choice बता सको।
