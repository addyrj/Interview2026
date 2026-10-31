# 72. When to use React.memo
# हिंदी में: React.memo कब लगाएं — Decision लेने का तरीका

---

## 🔵 Simple Definition (English)
**`React.memo`** wraps a component so React can skip re-rendering it when its props are shallow-equal to the last render. Knowing **when** to use it is about measuring first: apply it only where a profiler shows real, repeated, expensive re-renders with stable props.

## 🔵 सरल परिभाषा (Hindi)
**`React.memo`** एक component को wrap करता है ताकि props पिछले render जैसे ही हों तो React उसे दोबारा render न करे। सवाल यह है कि इसे **कब** लगाएं — जवाब है: पहले measure करो। इसे सिर्फ वहीं लगाओ जहां profiler में बार-बार होने वाले, महंगे re-renders दिखें और props stable हों।

---

## 🔴 Problem it Solves
Memo की basics (topic 58) समझ आ गई, पर असली सवाल यह है कि हर component पर memo लगाना सही है या नहीं। ज़्यादातर developers memo को "हमेशा तेज़ करने वाला" मान लेते हैं। नतीजा यह कि code में noise बढ़ता है, props की comparison का overhead आता है, और कोई फायदा नहीं होता। असली समस्या यह जानना है कि किस component का re-render महंगा है और किसने उसे trigger किया।

## 🔴 यह क्यों बना? (Hindi)
Amazon के product listing पर हर keystroke से search bar update होता है। अगर सब product cards हर keystroke पर re-render हों, तो typing laggy लगती है। Memo यहां मदद करता है। पर एक छोटे `<Label>` पर memo लगाना बेकार है। Developer को यह पहचानना सीखना है कि कौन-सा re-render असली समस्या है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Problem पहचानो: Profiler खोलो (React DevTools → Profiler tab)
         "Record" दबाओ, user action करो, फिर "Stop"

Step 2 → Flamegraph/Ranked chart में देखो:
         कौन-सा component बार-बार render हो रहा है?
         कितना time लग रहा है (commit में कितने ms)?

Step 3 → Cause देखो: "Why did this render?" → props changed या parent re-render?

Step 4 → Decision:
         ✅ Expensive + frequent + props mostly stable → memo लगाओ
         ❌ Cheap या props हर बार बदलते हैं → memo मत लगाओ

Step 5 → Memo के साथ props stable करो (useMemo/useCallback)
         → फिर दोबारा Profiler चलाकर verify करो कि फायदा हुआ

KEY: Measure → Decide → Verify. Guess पर memo मत लगाओ।
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Profiler से समस्या पहचानो (कौन-सा component बार-बार render)
Step 2 → देखो कि render महंगा है या नहीं (ms में)
Step 3 → Cause जांचो: props बदले या सिर्फ parent re-render हुआ
Step 4 → Expensive + stable props → memo; वरना नहीं
Step 5 → Fix के बाद फिर से Profiler चलाओ और फायदा verify करो
KEY: पहले measure, फिर decide, फिर verify। अंदाज़े से memo मत लगाओ।
```

---

## 🟡 Real World Example
**Zomato restaurant search:** User "biryani" टाइप कर रहा है। हर keystroke पर search input update होता है और 200 restaurant cards की list re-filter होती है। Profiler दिखाता है कि हर card का render 3 ms लेता है (image, rating, offers, सब एक साथ) और props बदल भी नहीं रहे, सिर्फ parent re-render हो रहा है। यहां `memo` लगाने से typing smooth होती है। पर नीचे footer पर memo लगाना बेकार होगा, क्योंकि वह एक बार render होता है और कभी re-render नहीं होता।

## 🟡 Real Example Hindi mein
**Zomato restaurant search:** User "biryani" type कर रहा है। हर keystroke पर 200 restaurant cards re-filter होती हैं। Profiler बताता है कि हर card 3 ms लेता है और props भी नहीं बदल रहे, सिर्फ parent re-render हो रहा है। यहां `memo` से typing smooth होती है। पर footer पर memo लगाना बेकार है, क्योंकि वह कभी बार-बार render ही नहीं होता।

---

## 💻 Code Example — Basic

```jsx
import { memo, useState } from 'react';           // memo और useState React से

// ── BASIC: Profiler से निर्णय, फिर memo ──

// Expensive card: हर render पर भारी काम (simulate किया गया)
const RestaurantCard = memo(function RestaurantCard({ restaurant }) {
  // Real app में यहां heavy JSX, images, computations होते हैं
  console.log('RestaurantCard render:', restaurant.name); // देखने के लिए: कब render हुआ
  return (
    <div>
      <h3>{restaurant.name}</h3>                  {/* नाम दिखाओ */}
      <p>⭐ {restaurant.rating}</p>               {/* rating दिखाओ */}
    </div>
  );
});

// Footer: सिर्फ एक बार render होता है, memo की ज़रूरत नहीं
function Footer() {
  return <footer>© 2026 Zomato-style app</footer>; // स्थिर UI, कोई props नहीं
}

// Static data: module scope पर, ताकि reference हमेशा एक जैसा रहे
const RESTAURANTS = [
  { id: 1, name: 'Biryani House', rating: 4.5 },   // restaurant 1
  { id: 2, name: 'Pizza Corner', rating: 4.2 },    // restaurant 2
];

export default function SearchPage() {
  const [query, setQuery] = useState('');          // search text (हर keystroke पर बदलेगा)

  return (
    <div>
      <input
        value={query}                              // controlled input
        onChange={e => setQuery(e.target.value)}   // हर keystroke पर parent re-render
      />
      {RESTAURANTS.map(r => (
        // RESTAURANTS[i] का reference नहीं बदलता, इसलिए memo card skip करता है ✅
        <RestaurantCard key={r.id} restaurant={r} />
      ))}
      <Footer />                                   {/* Footer re-render होगा, पर यह ठीक है: यह हल्का है */}
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { memo, useCallback, useMemo, useState } from 'react';

// ── ADVANCED: Profiler-guided optimization with a measurable check ──

// 1. Expensive child: memo + stable props की उम्मीद
const MenuItem = memo(function MenuItem({ item, onAdd, isInCart }) {
  // Heavy work simulate करने के लिए (real app में यह JSX/format calc होता है)
  const priceLabel = formatINR(item.price);           // helper: हर render पर चलता है
  return (
    <li>
      <span>{item.name}</span> <strong>{priceLabel}</strong>
      <button onClick={() => onAdd(item.id)} disabled={isInCart}>
        {isInCart ? 'Added' : 'Add'}                  {/* cart में है तो button बदले */}
      </button>
    </li>
  );
});

// Pure helper: इसे सिर्फ demo के लिए रखा गया है
function formatINR(amount) {
  return `₹${amount.toLocaleString('en-IN')}`;        // भारतीय format में कीमत
}

// 2. Parent: stable props तैयार करो ताकि memo काम करे
export default function Menu({ items }) {
  const [cart, setCart] = useState(new Set());        // cart में कौन-से item id हैं
  const [filter, setFilter] = useState('');           // search filter (typing से बदलेगा)

  // useCallback: function reference स्थिर रहे, वरना memo टूटेगा
  const handleAdd = useCallback((id) => {
    setCart(prev => new Set(prev).add(id));           // नया Set बनाओ (immutable update)
  }, []);                                             // setCart stable है, deps खाली

  // useMemo: filter तभी दोबारा चले जब items या filter बदले
  const visible = useMemo(() => {
    const q = filter.trim().toLowerCase();            // खोज का text साफ करो
    return items.filter(i => i.name.toLowerCase().includes(q)); // नाम से filter
  }, [items, filter]);                                // deps: items या filter

  return (
    <div>
      <input
        placeholder="Dish खोजो"
        value={filter}
        onChange={e => setFilter(e.target.value)}      // typing → filter बदला → parent re-render
      />
      <ul>
        {visible.map(item => (
          <MenuItem
            key={item.id}                              // stable key (index नहीं)
            item={item}                                // item object: items array से आ रहा है, reference stable
            onAdd={handleAdd}                          // useCallback से stable
            isInCart={cart.has(item.id)}               // boolean primitive → memo के लिए आदर्श
          />
        ))}
      </ul>
    </div>
  );
}

// 3. Verification: React Profiler में "Why did this render?" से देखो कि props बदले या नहीं
// Chrome/React DevTools → Profiler → "Record" → typing करो → MenuItem का render count घटा?
```

---

## 🟠 Real app integration

Next.js में सबसे आम जगह एक **Client Component** की list है, जैसे search results या cart। Server Components को memo की ज़रूरत नहीं पड़ती, क्योंकि वे client पर re-render ही नहीं होते।

```jsx
// app/search/SearchClient.js — Client Component (search typing के लिए state चाहिए)
'use client';                                    // हस्ताक्षर: यह browser में चलेगा
import { memo, useState, useMemo } from 'react'; // hooks और memo

const ProductRow = memo(function ProductRow({ product }) { // हर row memo
  return <li>{product.title} — ₹{product.price}</li>;       // सिर्फ title और price
});

export default function SearchClient({ products }) {       // server से products prop आते हैं
  const [q, setQ] = useState('');                           // search text
  const results = useMemo(                                  // filter महंगा है, इसलिए memo
    () => products.filter(p => p.title.includes(q)),        // q बदले तभी चले
    [products, q]                                           // deps
  );
  return (
    <>
      <input value={q} onChange={e => setQ(e.target.value)} /> {/* controlled input */}
      <ul>
        {results.map(p => <ProductRow key={p.id} product={p} />)} {/* memo rows */}
      </ul>
    </>
  );
}
```

यह pattern तब काम का है जब `products` array server से एक बार आता है और typing हर keystroke पर होती है।

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** बिना profiling के हर component पर memo लगाना
```jsx
// ❌ Wrong: यह component हल्का है, memo का comparison overhead उससे ज़्यादा है
const Badge = memo(({ text }) => <span className="badge">{text}</span>);

// ✅ Right: पहले Profiler चलाओ। सिर्फ तभी memo लगाओ जब Badge बार-बार महंगा render हो।
const Badge = ({ text }) => <span className="badge">{text}</span>; // सामान्य component
```

❌ **Mistake 2:** memo लगाया, पर parent हर बार नया object/function भेजता है
```jsx
// ❌ Wrong: onAdd हर render पर नया function है, memo कभी skip नहीं करेगा
<MenuItem item={item} onAdd={(id) => addToCart(id)} />

// ✅ Right: useCallback से function को stable रखो
const handleAdd = useCallback((id) => addToCart(id), [addToCart]); // addToCart स्थिर हो तो deps सही
<MenuItem item={item} onAdd={handleAdd} />                         // अब memo काम करेगा
```

---

## 🧠 Tricky Interview Question

```jsx
import { memo, useState } from 'react';

const Heavy = memo(function Heavy({ data }) {
  console.log('Heavy render');                     // कितनी बार चलेगा?
  return <p>{data.value}</p>;
});

export default function App() {
  const [n, setN] = useState(0);                   // counter
  const [text, setText] = useState('');            // input text (alag state)
  const data = { value: 'fixed' };                 // हर render पर नया object!

  return (
    <div>
      <button onClick={() => setN(n + 1)}>{n}</button>
      <input value={text} onChange={e => setText(e.target.value)} />
      <Heavy data={data} />
    </div>
  );
}
// Question: Typing करने (text बदलने) पर "Heavy render" कितनी बार log होगा?
// और counter button दबाने पर?
```

**Answer:** हर बार जब `text` या `n` बदलता है, `App` दोबारा render होता है। `data` एक **नया object** है, जो हर render पर बनता है। `memo` shallow `Object.is` से compare करता है: `oldData !== newData`, इसलिए `Heavy` हर keystroke और हर button click पर re-render होगा। Memo "fixed" value की वजह से skip नहीं करेगा, क्योंकि value से नहीं, reference से compare होता है। Fix: `data` को module scope पर रखो (`const DATA = { value: 'fixed' }` बाहर) या `useMemo(() => ({ value: 'fixed' }), [])` से बनाओ। तब दोनों पर `Heavy` एक बार भी re-render नहीं करेगा।

---

## ⚫ Interview Questions + Answers

**Q1: `React.memo` कब लगाना चाहिए?**
A1: जब Profiler में कोई component बार-बार render हो रहा हो, उसका render महंगा हो, और उसके props ज़्यादातर stable हों (primitives या memoized objects/functions)। अंदाज़े से नहीं, measurement के आधार पर।

**Q2: React Compiler के आने के बाद manual memo की ज़रूरत है?**
A2: React Compiler (React 19 के साथ) components और hooks के लिए automatic memoization करता है, इसलिए कई मामलों में manual `memo`, `useMemo` और `useCallback` की ज़रूरत कम हो जाती है। फिर भी profiling की ज़रूरत है और Compiler सभी code पर लागू नहीं होता, इसलिए पुरानी codebase में memo का ज्ञान ज़रूरी है।

**Q3: `memo` के साथ `useMemo`/`useCallback` क्यों ज़रूरी हैं?**
A3: `memo` props की reference equality देखता है। Parent हर render पर नया object या function बनाए, तो memo हमेशा "props बदले" मानेगा। `useMemo` और `useCallback` से reference स्थिर रहता है।

**Q4: Memo लगाने का नुकसान क्या है?**
A4: हर render पर props की comparison का cost होता है, code में complexity बढ़ती है, और stale props या बग्स का खतरा रहता है। अगर component हमेशा props बदलने से re-render होता है, तो memo सिर्फ overhead जोड़ता है।

**Q5: कैसे पता करें कि memo ने काम किया?**
A5: React DevTools Profiler में पहले और बाद में recording compare करो। "Why did this render?" option से देखो कि render कम हुए या नहीं, और commit time (ms) घटा या नहीं। बिना measurement के "लगता है तेज़ हुआ" मत मानो।

---

## 🔷 When to Use + When Not to Use
✅ **Use React.memo when:**
- Profiler में component बार-बार और महंगा render हो रहा हो (जैसे 200 item list)
- Parent बार-बार re-render होता है, पर child के props ज़्यादातर नहीं बदलते
- Props stable हैं (primitives, या `useMemo`/`useCallback` से बने values)
- Component में heavy JSX, computation या large subtree है

❌ **Skip React.memo when:**
- Component छोटा है (जैसे badge, label, icon)
- Props हर render पर बदलते हैं (नया object, नया function, बदलता हुआ data)
- Component कम render होता है या बस एक बार
- आपने अभी तक profile नहीं किया — यह premature optimization है

---

## 📊 Visual Diagram

```
  Decision flow:

  Profiler में बार-बार render दिखा?
        │
        ├── नहीं ──► memo मत लगाओ ❌
        │
        └── हाँ
              │
              ├── Render cheap है (< 1 ms)? ──► memo मत लगाओ ❌
              │
              └── Render महंगा है
                    │
                    ├── Props हर बार बदलते हैं? ──► पहले props stable करो (useMemo/useCallback)
                    │                                 │
                    │                                 └──► फिर memo ✅
                    │
                    └── Props stable हैं ──► React.memo ✅
                                              │
                                              └── Profiler से verify करो
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Profiler | React DevTools का tool जो render time नापता है | Render time नापने वाला tool |
| Why did this render? | Profiler का option जो कारण बताता है | Render का कारण बताने वाला option |
| Reference equality | `Object.is` से दो values की पहचान | Dono values की identity की तुलना |
| Premature optimization | बिना measurement के किया गया optimization | बिना measure किया optimization |
| Commit time | Render के बाद DOM update में लगा समय | DOM update में लगा समय |
| React Compiler | React 19 का build-time tool जो auto-memoize करता है | Auto-memoize करने वाला build tool |

---

## ⚡ 3-Line Summary
**English:**
1. `React.memo` लगाने से पहले React DevTools Profiler से साबित करो कि re-render महंगा और बार-बार है।
2. Memo तभी काम करता है जब props stable हों; नए object या function के लिए `useMemo`/`useCallback` लगाओ।
3. Cheap components और हमेशा बदलने वाले props पर memo मत लगाओ; React Compiler भी कई cases संभालता है।

**Hindi:**
1. `React.memo` लगाने से पहले React DevTools Profiler से साबित करो कि re-render महंगा और बार-बार होता है।
2. Memo तभी काम करता है जब props stable हों; नए object या function के लिए `useMemo`/`useCallback` लगाओ।
3. हल्के components और हमेशा बदलने वाले props पर memo मत लगाओ; React Compiler भी कई cases संभालता है।

---

## ➡️ Next Topic
**73. Reconciliation — How React Diffs** — React virtual DOM को कैसे compare करता है, element type और keys का role क्या है।
