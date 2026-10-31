# 69. Suspense + lazy loading
# हिंदी में: Suspense + lazy loading — Loading states को declarative तरीके से संभालना

---

## 🔵 Simple Definition (English)
**`React.lazy`** lets you load a component's code only when it is first rendered (on demand). **`<Suspense fallback={...}>`** shows a fallback UI while anything inside it is "not ready yet" — code still downloading, or data a framework is waiting for.

## 🔵 सरल परिभाषा (Hindi)
**`React.lazy`** किसी component का code तभी load करता है जब वह पहली बार render होने वाला हो (on demand)। **`<Suspense fallback={...}>`** तब तक fallback UI दिखाता है जब तक उसके अंदर का कोई हिस्सा "तैयार नहीं" है — code अभी download हो रहा हो, या framework किसी data का इंतज़ार कर रहा हो।

---

## 🔴 Problem it Solves
एक बड़ी React app का JavaScript bundle अगर 2 MB का हो, तो user को पहली बार page खोलने में सब कुछ download करना पड़ता है, भले ही वह सिर्फ login page देखने आया हो। साथ ही, हर component में `isLoading` flag और spinner का code हाथ से लिखना पड़ता था, जो बहुत repetitive और error-prone था।

## 🔴 यह क्यों बना? (Hindi)
Flipkart जैसी app में checkout, reviews, और seller map के लिए अलग code है। Home page खुलते समय ये सब download करने की ज़रूरत नहीं। `lazy` से code split होता है और `Suspense` से loading UI एक जगह से declare होता है — हर component में manual `isLoading` checks की ज़रूरत नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component को lazy से define करो
         const Chart = lazy(() => import('./Chart'));

Step 2 → Chart को Suspense के अंदर render करो
         <Suspense fallback={<Spinner />}><Chart /></Suspense>

Step 3 → React Chart render करने जाता है, पर module अभी load नहीं हुआ
         → Chart "suspend" करता है (एक promise throw करके)

Step 4 → नज़दीकी Suspense boundary पकड़ती है और fallback दिखाती है

Step 5 → Promise resolve होता है → React वही render दोबारा करता है
         → अब असली Chart दिखता है और fallback हट जाता है

KEY: lazy() का factory एक बार चलता है और result cache होता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → lazy() से component define करो, factory में import() हो
Step 2 → उसे Suspense के अंदर render करो
Step 3 → Module अभी नहीं आया → component "suspend" करता है
Step 4 → Suspense fallback दिखाता है
Step 5 → Module आ गया → React दोबारा render करता है, असली UI दिखता है
KEY: lazy का factory सिर्फ एक बार चलता है, result cache हो जाता है
```

---

## 🟡 Real World Example
**Swiggy restaurant page:** Menu और cart page तुरंत खुलते हैं। "Live order map" वाला code (जिसमें बड़ी map library है) सिर्फ तब load होता है जब user "Track order" पर tap करता है। Map का code download होने तक एक छोटा skeleton दिखता है। इससे पहली बार page खुलने की speed काफी बढ़ जाती है।

## 🟡 Real Example Hindi mein
**Swiggy restaurant page:** Menu और cart तुरंत खुलते हैं। "Live order map" वाला code (बड़ी map library के साथ) सिर्फ तब load होता है जब user "Track order" पर tap करता है। Map का code आने तक एक छोटा skeleton दिखता है। इससे पहली बार page खुलने की speed काफी बढ़ती है।

---

## 💻 Code Example — Basic

```jsx
import { Suspense, lazy, useState } from 'react'; // lazy और Suspense React से आते हैं

// ── BASIC: एक heavy component को lazy load करो ──
// lazy() एक function लेता है जो import() return करता है (Promise of module)
// Module में default export होना ज़रूरी है
const HeavyChart = lazy(() => import('./HeavyChart')); // अभी code download नहीं हुआ

export default function Dashboard() {
  const [showChart, setShowChart] = useState(false); // शुरू में chart hidden है

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={() => setShowChart(true)}>Show Sales Chart</button>

      {showChart && (                                  // सिर्फ click के बाद render होगा
        // Suspense: जब तक HeavyChart का code download हो रहा है, fallback दिखे
        <Suspense fallback={<p>Chart load ho raha hai...</p>}>
          <HeavyChart />                               {/* अब जाकर chunk download होता है */}
        </Suspense>
      )}
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { Suspense, lazy, useState, useTransition } from 'react';
import ErrorBoundary from './ErrorBoundary'; // topic 68 वाला boundary — chunk fail होने पर पकड़ेगा

// ── Retry wrapper: network glitch में chunk load को दोबारा try करो ──
function lazyWithRetry(importFn, retries = 2) {
  return lazy(async function load() {          // lazy के लिए async loader
    let lastError;                             // आखिरी error याद रखो
    for (let attempt = 0; attempt <= retries; attempt++) { // कुल 1 + retries बार try
      try {
        return await importFn();               // सफल हुआ तो module return करो
      } catch (err) {
        lastError = err;                       // असफल — error save करो और अगली बार try करो
      }
    }
    throw lastError;                           // सब attempts fail → boundary पकड़ेगी
  });
}

// हर section अलग chunk में है
const Reviews = lazyWithRetry(() => import('./Reviews'));   // reviews का code
const StoreMap = lazyWithRetry(() => import('./StoreMap')); // map का code

// Preload: download पहले शुरू कर दो, user के click से पहले
const loadStoreMap = () => import('./StoreMap'); // import() call होते ही download शुरू; browser cache करता है

export default function ProductPage({ product }) {
  const [tab, setTab] = useState('reviews');  // कौन सा tab active है
  const [isPending, startTransition] = useTransition(); // पुराना tab दिखता रहे, जब तक नया load हो

  function selectTab(next) {
    startTransition(() => setTab(next));      // non-urgent update → navigation पर fallback flash नहीं
  }

  return (
    <section>
      <h2>{product.name}</h2>
      <nav>
        <button onClick={() => selectTab('reviews')}>Reviews</button>
        {/* hover पर preload: click होने तक code तैयार */}
        <button onMouseEnter={loadStoreMap} onClick={() => selectTab('map')}>Store Map</button>
      </nav>
      {isPending && <span>Loading...</span>}      {/* transition चल रहा हो तो छोटा indicator */}
      <ErrorBoundary>                              {/* chunk fail → crash नहीं, fallback */}
        <Suspense fallback={<p>Section load ho raha hai...</p>}>
          {tab === 'reviews'
            ? <Reviews productId={product.id} />   // reviews tab
            : <StoreMap storeId={product.storeId} />} {/* map tab */}
        </Suspense>
      </ErrorBoundary>
    </section>
  );
}
```

---

## 🟠 Real app integration

**Next.js App Router** में `loading.js` file उस route segment के लिए अपने-आप `<Suspense>` boundary बनाती है। Server Components में `await` करने पर भी यही fallback दिखता है।

```jsx
// app/dashboard/loading.js — Next.js इसे page के चारों ओर Suspense fallback की तरह use करता है
export default function Loading() {
  return <div className="skeleton">Dashboard load ho raha hai...</div>; // skeleton UI
}
```

```jsx
// app/dashboard/page.js — Server Component में streaming के लिए Suspense
import { Suspense } from 'react';        // Suspense React से
import Revenue from './Revenue';         // async Server Component (DB/API से data लाता है)

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>                 {/* यह तुरंत भेज दिया जाता है */}
      <Suspense fallback={<p>Revenue load ho raha hai...</p>}>
        <Revenue />                      {/* data तैयार होते ही HTML stream होता है */}
      </Suspense>
    </div>
  );
}
```

```jsx
// components/StoreMap.js — client-only component को next/dynamic से lazy load करना
'use client';                            // ssr: false Client Component के अंदर ही use करो
import dynamic from 'next/dynamic';      // Next.js का lazy loader

const StoreMap = dynamic(() => import('./Map'), { // Map का code अलग chunk में
  ssr: false,                            // server पर render मत करो (browser-only library)
  loading: () => <p>Map load ho raha hai...</p>, // download के दौरान fallback
});

export default function StoreSection() {
  return <StoreMap />;                   // उपयोग में वैसे ही जैसे normal component
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `lazy()` को component के अंदर call करना
```jsx
// ❌ Wrong: हर render पर नया lazy component type बनता है
function Parent() {
  const Chart = lazy(() => import('./Chart')); // हर render पर नया type → remount, state खो जाता है
  return <Suspense fallback="..."><Chart /></Suspense>;
}

// ✅ Right: lazy को module scope में बनाओ — एक बार, हमेशा के लिए
const Chart = lazy(() => import('./Chart')); // सिर्फ एक बार define
function Parent() {
  return <Suspense fallback="..."><Chart /></Suspense>; // same type हर बार
}
```

❌ **Mistake 2:** Lazy component के ऊपर Suspense boundary न होना
```jsx
// ❌ Wrong: कोई Suspense नहीं — fallback के बिना component suspend नहीं संभाल पाएगा
function App() {
  return <Chart />; // Chart lazy है, पर कहीं कोई fallback declare नहीं
}

// ✅ Right: lazy component को कम से कम एक Suspense के अंदर रखो
function App() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <Chart />                          {/* अब fallback मिलेगा */}
    </Suspense>
  );
}
```

---

## 🧠 Tricky Interview Question

```jsx
import { lazy, Suspense, useState } from 'react';

// Child.js: export default function Child() { return <input />; }

export default function App() {
  const [count, setCount] = useState(0);
  // lazy() को RENDER के अंदर call किया गया है
  const Child = lazy(() => {
    console.log('loading');                 // factory कितनी बार चलती है?
    return import('./Child');
  });

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>Clicked {count}</button>
      <Suspense fallback={<p>...</p>}>
        <Child />                           {/* Child के <input /> में user text type करे, फिर button दबाए */}
      </Suspense>
    </div>
  );
}
// Question: हर button click पर क्या होगा? Input का text बचेगा?
```

**Answer:** हर click पर App दोबारा render होता है और `lazy()` को फिर से call करता है, यानी `Child` एक **नया component type** बन जाता है। React type की पहचान से component को same मानता है, इसलिए नए type के कारण वह पुराने `Child` को unmount करके नया mount करता है। इसका मतलब: (1) `loading` console में हर click पर दिखेगा (पहली बार के अलावा भी), (2) `<input />` का text खो जाएगा क्योंकि उसका state reset हो गया, और (3) नया lazy component फिर से suspend कर सकता है, जिससे fallback दिखता है। Fix यह है कि `lazy()` को module scope में रखो, तब factory सिर्फ एक बार चलेगा।

---

## ⚫ Interview Questions + Answers

**Q1: `React.lazy` और `Suspense` कैसे काम करते हैं?**
A1: `lazy(() => import(...))` component को on-demand load करता है। जब component पहली बार render होता है और module तैयार नहीं है, तो वह suspend करता है। नज़दीकी `<Suspense fallback>` तब तक fallback दिखाता है जब तक module आ न जाए, फिर React दोबारा render करता है।

**Q2: `lazy` component default export ही क्यों चाहिए?**
A2: `React.lazy` की API अपेक्षा करती है कि import का resolved value `{ default: Component }` के रूप में हो। इसलिए `import('./X')` में `export default` होना चाहिए, या factory में `.then(m => ({ default: m.Named }))` से map करना होगा।

**Q3: Suspense सिर्फ lazy components के लिए है?**
A3: नहीं। React 18 से Suspense data fetching के लिए भी है, पर इसके लिए data को Suspense-compatible तरीके से लाना होता है, जैसे Next.js के Server Components, React 19 का `use(promise)`, या Relay। Plain `useEffect` + `fetch` Suspense को trigger नहीं करता।

**Q4: `useTransition` के साथ Suspense क्यों use होता है?**
A4: Tab या route बदलते समय अगर नया content suspend करे, तो बिना transition के पुराना UI हटकर fallback दिखता है। `startTransition` से update non-urgent हो जाता है और React पुराना UI बनाए रखता है, जब तक नया तैयार न हो।

**Q5: Lazy loading का सबसे बड़ा trade-off क्या है?**
A5: पहली बार उस component पर पहुंचने पर network delay और fallback दिखता है। इसे कम करने के लिए preload (hover या idle पर `import()` call करना) और सही जगह पर boundaries रखना ज़रूरी है। Critical above-the-fold UI को lazy नहीं करना चाहिए।

---

## 🔷 When to Use + When Not to Use
✅ **Use lazy + Suspense when:**
- Component बड़ा है और हर user को हर समय नहीं चाहिए (charts, maps, editors)
- Route या tab के हिस्से हैं जो अलग-अलग समय पर खुलते हैं
- Browser-only libraries हैं (`ssr: false` के साथ `next/dynamic`)
- Framework (Next.js, Relay) data के लिए Suspense support करता है

❌ **Avoid when:**
- Component छोटा है और हमेशा first paint में दिखता है (header, logo)
- Critical above-the-fold UI को lazy कर रहे हो — इससे LCP बिगड़ता है
- Plain client-side `fetch` को Suspense से जोड़ने की कोशिश (यह trigger नहीं होता)
- Boundary के बिना lazy component रखना

---

## 📊 Visual Diagram

```
  App renders
     │
     ▼
  <Suspense fallback={<Skeleton/>}>
     │
     ├── <Header/>             ✅ सामान्य render
     │
     └── <Chart/> (lazy)
           │
           ├── Module ready?  ──No──► throw promise ──► Suspense shows Skeleton
           │                                              │
           │                              promise resolves│
           │                                              ▼
           └── Module ready?  ──Yes─► React re-renders ──► Real <Chart/> ✅

  Chunks on network:
  main.js (small) ──────────────── loaded at start
  chart.chunk.js  ──── loaded on first render of <Chart/>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `React.lazy` | Component को on-demand load करने का API | Component को ज़रूरत पर load करने का API |
| `Suspense` | Loading के दौरान fallback दिखाने वाला boundary | Loading में fallback दिखाने वाला boundary |
| Suspend | Component का render "रुकना" जब data/code तैयार न हो | Component का render रुकना |
| Fallback | Loading के समय दिखने वाला UI | Loading के समय का UI |
| Chunk | Code को split करके बना अलग file टुकड़ा | Code का अलग टुकड़ा (file) |
| Preload | Click से पहले `import()` शुरू करना | Click से पहले code download शुरू करना |

---

## ⚡ 3-Line Summary
**English:**
1. `React.lazy` component को on-demand load करता है और `Suspense` loading के दौरान fallback दिखाता है।
2. `lazy()` को module scope में रखो, render के अंदर नहीं — वरना हर render पर remount होगा।
3. Next.js में `loading.js`, streaming Suspense और `next/dynamic` (client-only के लिए `ssr: false`) use करो।

**Hindi:**
1. `React.lazy` component को ज़रूरत पड़ने पर load करता है और `Suspense` loading में fallback दिखाता है।
2. `lazy()` को module scope में रखो, render के अंदर नहीं — वरना हर render पर remount होगा।
3. Next.js में `loading.js`, streaming Suspense और `next/dynamic` (client-only के लिए `ssr: false`) use करो।

---

## ➡️ Next Topic
**70. Code Splitting in React** — bundle को कैसे split करें, route-based splitting, और `import()` के बाद bundle analysis कैसे करें।
