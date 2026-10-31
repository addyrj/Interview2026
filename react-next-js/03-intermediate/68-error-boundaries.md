# 68. Error Boundaries
# हिंदी में: Error Boundaries — UI crash होने से पूरे app को बचाना

---

## 🔵 Simple Definition (English)
An **Error Boundary** is a component that catches JavaScript errors thrown while **rendering** its children, and shows a **fallback UI** instead of crashing the whole app. It must be a **class component** (using `getDerivedStateFromError` or `componentDidCatch`) — there is no hook equivalent yet.

## 🔵 सरल परिभाषा (Hindi)
**Error Boundary** एक component है जो अपने children के **render** के दौरान आने वाले JavaScript errors पकड़ लेता है और पूरे app को crash करने की जगह एक **fallback UI** दिखाता है। यह **class component** होना चाहिए (`getDerivedStateFromError` या `componentDidCatch` के साथ) — hooks वाला equivalent अभी तक नहीं है।

---

## 🔴 Problem it Solves
React 15 तक, किसी एक component में render-time error आने पर React पूरे tree को unmount कर देता था। मतलब एक बेकार widget के कारण पूरी page सफ़ेद (white screen) हो जाती थी। सोचो Swiggy पर एक restaurant card का data corrupt है — पूरा menu page बंद हो जाए, यह user experience के लिए बहुत बुरा है। Error Boundaries ने इसे सीमित (isolated) करने का तरीका दिया।

## 🔴 यह क्यों बना? (Hindi)
पहले एक छोटे component के error से पूरी app गिर जाती थी। Zomato पर एक restaurant का data खराब हो तो पूरा feed बंद नहीं होना चाहिए। Error Boundary "crash का दायरा" (blast radius) छोटा करता है — सिर्फ वही section fallback दिखाए, बाकी app चलती रहे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Child component render के दौरान error throw करता है
         function RestaurantCard() { return <h3>{restaurant.name}</h3> } // restaurant = null

Step 2 → React tree ऊपर जाकर सबसे नज़दीकी Error Boundary ढूंढता है

Step 3 → getDerivedStateFromError(error) call होता है (render phase)
         → return { hasError: true } → state update → fallback UI render

Step 4 → componentDidCatch(error, info) call होता है (commit phase)
         → यहां logging / monitoring (Sentry जैसे tools) करो

Step 5 → Reset: state clear करो, children फिर से render हों (Retry button)

KEY: Boundary सिर्फ अपने CHILDREN का render error पकड़ता है — खुद को नहीं
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Child render में error throw होता है
Step 2 → React सबसे नज़दीकी Error Boundary खोजता है
Step 3 → getDerivedStateFromError → state में error save → fallback दिखे
Step 4 → componentDidCatch → error log करो (side effects यहीं)
Step 5 → Retry पर state clear → children दोबारा render
KEY: Boundary अपने children के render errors पकड़ता है, अपने खुद के नहीं
```

---

## 🟡 Real World Example
**Zomato restaurant feed:** 20 restaurant cards एक साथ दिख रहे हैं। एक card में एक field `null` आ जाती है और उसका render crash होता है। Error Boundary उस एक card की जगह "Details unavailable" दिखाता है, बाकी 19 cards और header, search bar सब चलते रहते हैं। Sentry में error report भी हो जाता है।

## 🟡 Real Example Hindi mein
**Zomato restaurant feed:** 20 restaurant cards दिख रहे हैं। एक card में एक field `null` आ जाती है और उसका render crash होता है। Error Boundary उस एक card की जगह "Details unavailable" दिखाता है, बाकी 19 cards, header और search bar चलते रहते हैं। Sentry में error report भी हो जाती है।

---

## 💻 Code Example — Basic

```jsx
import { Component } from 'react'; // Error Boundary के लिए Component base class चाहिए

// ── BASIC ERROR BOUNDARY (class component) ──
class ErrorBoundary extends Component {
  // Constructor: component का initial state set करता है
  constructor(props) {
    super(props);                  // parent constructor को props के साथ call करो
    this.state = { hasError: false }; // शुरू में कोई error नहीं है
  }

  // Render phase में call होता है जब कोई child throw करे — नया state return करो
  static getDerivedStateFromError(error) {
    return { hasError: true }; // अगले render में fallback UI दिखेगा
  }

  // Commit phase में call होता है — side effects (logging) के लिए सही जगह
  componentDidCatch(error, info) {
    console.error('Caught:', error.message, info.componentStack); // monitoring को भेजो
  }

  render() {
    if (this.state.hasError) {     // अगर error पकड़ा गया है
      return <h2>Kuch galat ho gaya. Page refresh karein.</h2>; // fallback UI
    }
    return this.props.children;    // सामान्य स्थिति: children जैसे हैं वैसे render करो
  }
}

// ── Child component जो crash होता है ──
function RestaurantCard({ restaurant }) {
  // restaurant null हो तो .name पर TypeError throw होगा
  return <h3>{restaurant.name}</h3>;
}

// ── Usage ──
export default function App() {
  return (
    <div>
      <h1>Zomato Feed</h1>
      <ErrorBoundary>                       {/* यह boundary RestaurantCard के error को पकड़ेगा */}
        <RestaurantCard restaurant={null} /> {/* crash होगा → fallback दिखेगा */}
      </ErrorBoundary>
      <p>Header और बाकी app चलती रहेगी</p>  {/* boundary के बाहर है, तो सही render होगा */}
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { Component } from 'react';

// ── PRODUCTION ERROR BOUNDARY ──
// Real app में यहां Sentry.captureException(error, { extra: info }) होता है
function reportError(error, info) {
  console.error('[monitoring]', error.message, info?.componentStack ?? ''); // optional chaining से safe
}

class AppErrorBoundary extends Component {
  state = { error: null };          // class field: caught error store करने के लिए (null = कोई error नहीं)

  // Render phase: error को state में रखो ताकि अगला render fallback दिखाए
  static getDerivedStateFromError(error) {
    return { error };               // सिर्फ state update, कोई side effect नहीं
  }

  // Commit phase: logging और reporting यहां करो
  componentDidCatch(error, info) {
    reportError(error, info);       // monitoring को error भेजो
  }

  // जब resetKey बदले (जैसे user दूसरे page पर जाए), तो error अपने-आप clear हो जाए
  componentDidUpdate(prevProps) {
    if (this.state.error && prevProps.resetKey !== this.props.resetKey) {
      this.setState({ error: null }); // error clear → children फिर से render होंगे
    }
  }

  // Retry button का handler — arrow function ताकि `this` सही रहे
  reset = () => this.setState({ error: null });

  render() {
    const { error } = this.state;   // destructuring: error निकाल लो
    if (error) {
      // fallback prop दिया हो तो वही render करो, वरना default UI
      return this.props.fallback
        ? this.props.fallback({ error, reset: this.reset }) // render prop pattern
        : (
          <div role="alert">        {/* role="alert": screen readers इसे तुरंत announce करते हैं */}
            <p>Is section mein problem hai.</p>
            <button onClick={this.reset}>Dobara try karein</button>
          </div>
        );
    }
    return this.props.children;     // error नहीं → normal rendering
  }
}

// ── Usage: page बदलने पर boundary अपने-आप reset होती है ──
export default function OrdersPage({ page }) {
  return (
    <AppErrorBoundary
      resetKey={page}                // page बदला → boundary reset
      fallback={({ reset }) => (     // fallback एक function है, जो reset पास करता है
        <div role="alert">
          <p>Orders load nahi ho paaye.</p>
          <button onClick={reset}>Retry</button> {/* click → state clear → children retry */}
        </div>
      )}
    >
      <OrderList page={page} />      {/* कोई भी render error यहां से पकड़ा जाएगा */}
    </AppErrorBoundary>
  );
}
```

---

## 🟠 Real app integration

Next.js App Router में Error Boundary **अपने-आप** बन जाती है। `error.js` file हर route segment के लिए एक boundary होती है और इसे **Client Component** होना चाहिए।

```jsx
// app/orders/error.js
'use client';                          // error.js को Client Component होना ज़रूरी है
import { useEffect } from 'react';     // side effect (logging) के लिए

export default function OrdersError({ error, reset }) { // Next.js error और reset props देता है
  useEffect(() => {
    console.error(error);              // production में यहां Sentry/monitoring भेजो
  }, [error]);                         // जब error बदले तभी log करो

  return (
    <div role="alert">
      <h2>Orders load nahi ho paaye</h2>
      <button onClick={() => reset()}>Try again</button> {/* segment को दोबारा render करता है */}
    </div>
  );
}
```

Root layout का error पकड़ने के लिए `app/global-error.js` (भी `'use client'`) use करते हैं। Production में React 19 `createRoot` के `onCaughtError` और `onUncaughtError` options से errors centrally report कर सकते हैं। Ready-made solution चाहिए तो `react-error-boundary` package का `ErrorBoundary` component भी आम तौर पर use होता है।

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Event handler के error को boundary से पकड़ने की उम्मीद करना
```jsx
// ❌ Wrong: onClick का error boundary तक नहीं पहुंचता
<ErrorBoundary>
  <button onClick={() => { throw new Error('payment failed'); }}>Pay</button>
</ErrorBoundary>

// ✅ Right: handler में try/catch करो और error को state में डालकर RENDER में throw करो
function PayButton() {
  const [error, setError] = useState(null);     // error store करने के लिए state
  if (error) throw error;                       // render में throw → boundary पकड़ेगी
  return (
    <button onClick={() => {
      try { payOrder(); }                       // payOrder() तुम्हारा function है
      catch (e) { setError(e); }                // handler का error state में
    }}>Pay</button>
  );
}
function payOrder() { throw new Error('payment failed'); } // demo के लिए
```

❌ **Mistake 2:** पूरी app पर सिर्फ एक boundary लगाना
```jsx
// ❌ Wrong: एक छोटे widget का error पूरी app की जगह fallback दिखा देगा
<ErrorBoundary>
  <App />
</ErrorBoundary>

// ✅ Right: हर महत्वपूर्ण section पर अलग boundary लगाओ
<Header />
<ErrorBoundary><Feed /></ErrorBoundary>      {/* feed crash हो तो header चलता रहे */}
<ErrorBoundary><Sidebar /></ErrorBoundary>   {/* sidebar crash हो तो feed चलता रहे */}
```

---

## 🧠 Tricky Interview Question

```jsx
import { Component } from 'react';

class Boundary extends Component {
  state = { caught: null };                    // शुरू में कोई error नहीं
  static getDerivedStateFromError(error) {
    return { caught: error.message };          // error का message state में
  }
  render() {
    return this.state.caught
      ? <p>Caught: {this.state.caught}</p>     // fallback
      : this.props.children;                   // normal children
  }
}

function Bomb() {
  throw new Error('boom');                     // render-time error
}

function Clicky() {
  const handle = () => { throw new Error('click'); }; // event handler error
  return <button onClick={handle}>Click me</button>;
}

export default function App() {
  return (
    <div>
      <Boundary><Bomb /></Boundary>            {/* Boundary 1 */}
      <Boundary><Clicky /></Boundary>          {/* Boundary 2 */}
    </div>
  );
}
// Question: Initially क्या दिखेगा? Button click करने पर क्या होगा?
```

**Answer:** शुरू में पहले boundary का `Bomb` throw करता है, इसलिए वहां `Caught: boom` दिखता है। दूसरा boundary ठीक है, तो `Click me` button दिखता है। Button click करने पर `handle` throw करता है, लेकिन यह error **event handler** में हुआ है, render में नहीं। Error Boundary event handlers के errors नहीं पकड़ती, इसलिए boundary कुछ नहीं करती, button वैसा ही रहता है और error सिर्फ console में uncaught error के रूप में जाता है। Boundaries render, lifecycle methods और constructors के errors पकड़ती हैं — events, `setTimeout` और promises के errors नहीं।

---

## ⚫ Interview Questions + Answers

**Q1: Error Boundary क्या है और किस प्रकार का component होता है?**
A1: Error Boundary एक class component है जो अपने children के render, lifecycle methods और constructors में आने वाले errors पकड़ता है और fallback UI दिखाता है। इसमें `static getDerivedStateFromError` (state update के लिए) और `componentDidCatch` (logging के लिए) होते हैं। Hooks से अभी इसका direct equivalent नहीं है।

**Q2: Error Boundary क्या नहीं पकड़ती?**
A2: Event handlers (`onClick`) के errors, async code (`setTimeout`, promises, `async` functions) के errors, server-side rendering errors (कुछ हद तक), और खुद Error Boundary के अंदर के errors। इन्हें `try/catch` या `.catch()` से handle करना होता है।

**Q3: `getDerivedStateFromError` और `componentDidCatch` में क्या अंतर है?**
A3: `getDerivedStateFromError(error)` render phase में चलता है और सिर्फ नया state return करता है, इसमें side effects नहीं होने चाहिए। `componentDidCatch(error, info)` commit phase में चलता है, इसलिए यहां logging या API call (जैसे Sentry को भेजना) सुरक्षित है।

**Q4: Error Boundary को कहां रखें?**
A4: Granular तरीके से — हर स्वतंत्र section (feed, sidebar, widget) पर अलग boundary। एक root boundary से पूरी app एक fallback पर चली जाती है। Route level पर Next.js `error.js` हर segment की boundary होती है।

**Q5: Next.js App Router में error handling कैसे होती है?**
A5: `error.js` (Client Component) उस route segment के children के errors पकड़ता है और `error` व `reset` props देता है। `reset()` से segment फिर से render होता है। Root layout के errors के लिए `global-error.js` होता है।

---

## 🔷 When to Use + When Not to Use
✅ **Use Error Boundaries when:**
- Third-party widgets (payment, map, chat) अक्सर fail होते हैं और app को बचाना है
- Large pages के independent sections हैं जो अलग-अलग crash हो सकते हैं
- User को recovery (Retry) का option देना है
- Production में errors को monitoring tool (Sentry) में report करना है

❌ **Avoid / Don't rely on them when:**
- Event handler या async errors को handle करना है (इनके लिए `try/catch` use करो)
- Form validation errors हैं — वे normal UI state हैं, exception नहीं
- Boundary को सिर्फ एक जगह रखकर सब कुछ handle करने की कोशिश करना
- Expected "not found" या "empty" cases — इनके लिए normal conditional rendering बेहतर है

---

## 📊 Visual Diagram

```
           <App>
             │
   ┌─────────┴──────────┐
   │ ErrorBoundary (A)  │ ◄── getDerivedStateFromError + componentDidCatch
   │  ┌───────────────┐ │
   │  │ Feed          │ │
   │  │  ├─ Card 1 ✅ │ │
   │  │  ├─ Card 2 💥 │ │  ◄── render error thrown here
   │  │  └─ Card 3 ✅ │ │
   │  └───────────────┘ │
   └─────────┬──────────┘
             │  error caught at nearest boundary
             ▼
   ┌────────────────────┐
   │ Fallback UI        │  "Is section mein problem hai" [Retry]
   └────────────────────┘
             │  Retry → state reset → children re-render
             ▼
        Feed ✅ (recovered)

   Header, Sidebar  ──► boundary के बाहर → कभी प्रभावित नहीं होते
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Error Boundary | Render errors पकड़ने वाला class component | Render errors पकड़ने वाला component |
| getDerivedStateFromError | Error के बाद state update करने वाला static method | Error के बाद state update करने वाला method |
| componentDidCatch | Commit phase में error log करने का lifecycle | Error log करने का lifecycle method |
| Fallback UI | Error के समय दिखने वाला वैकल्पिक UI | Error के समय दिखने वाला UI |
| Blast radius | Error से प्रभावित UI का दायरा | Error से प्रभावित हिस्से का दायरा |
| error.js | Next.js App Router की route-level error boundary | Next.js की route-level error boundary |

---

## ⚡ 3-Line Summary
**English:**
1. Error Boundary (class component) children के render errors पकड़कर fallback UI दिखाता है, पूरी app crash नहीं होती।
2. यह event handlers, async code और खुद अपने errors नहीं पकड़ता — उनके लिए `try/catch` use करो।
3. Boundaries को granular रखो (हर section पर), और Next.js में `error.js` (Client Component) use करो।

**Hindi:**
1. Error Boundary (class component) children के render errors पकड़कर fallback UI दिखाता है, पूरा app crash नहीं होता।
2. यह event handlers, async code और अपने खुद के errors नहीं पकड़ता — उनके लिए `try/catch` use करो।
3. Boundaries को हर section पर अलग रखो, और Next.js में `error.js` (Client Component) use करो।

---

## ➡️ Next Topic
**69. Suspense + lazy loading** — loading states को declarative तरीके से handle करना और components को on-demand load करना।
