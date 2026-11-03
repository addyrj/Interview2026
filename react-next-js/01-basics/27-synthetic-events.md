# 27. Synthetic Events
# हिंदी में: Synthetic Events — React का अपना Event Wrapper

---

## 🔵 Simple Definition (English)
A **SyntheticEvent** is React's cross-browser wrapper around the browser's native event. When you write `onClick={handler}`, your handler receives this wrapper object, which has the same interface as the native event (`target`, `preventDefault()`, `stopPropagation()`) and behaves the same in every browser. The original event is available as `e.nativeEvent`.

## 🔵 सरल परिभाषा (Hindi)
**SyntheticEvent** browser के native event के चारों ओर React का cross-browser wrapper है। जब आप `onClick={handler}` लिखते हैं, तो आपके handler को यही wrapper object मिलता है, जिसमें native event जैसा ही interface (`target`, `preventDefault()`, `stopPropagation()`) होता है और जो हर browser में एक जैसा चलता है। असली event `e.nativeEvent` में मिलता है।

---

## 🔴 Problem it Solves

In old browsers (IE, early Safari) events behaved differently: different property names, different bubbling rules, `onChange` that did not fire on every keystroke. Developers wrote browser checks everywhere. Also, attaching a native listener to every button in a long list (hundreds of Flipkart product cards) wastes memory and needs manual cleanup.

React solved both: one consistent API, and **event delegation** (React attaches a single listener per event type at the root container, then routes events to the right component handler).

## 🔴 यह क्यों बना? (Hindi)
पुराने browsers (IE, शुरुआती Safari) में events अलग व्यवहार करते थे: अलग property names, अलग bubbling नियम, और `onChange` हर keystroke पर नहीं चलता था। Developers हर जगह browser checks लिखते थे। साथ ही, लंबी list के हर button पर native listener लगाना (Flipkart के सैकड़ों product cards) memory बर्बाद करता है और cleanup हाथ से करनी पड़ती है।

React ने दोनों हल किए: एक जैसा API, और **event delegation** (React हर event type के लिए root container पर सिर्फ एक listener लगाता है और फिर event को सही component के handler तक पहुँचाता है)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → React attaches ONE listener per event type to the root container (the div you pass to createRoot)
Step 2 → User clicks a button deep inside the app
Step 3 → The native click bubbles up the DOM to the root container
Step 4 → React's listener catches it and creates a SyntheticEvent wrapping the native event
Step 5 → React finds which component the target belongs to, then walks up the React tree
Step 6 → It calls each matching onClick handler (capture handlers like onClickCapture first)
Step 7 → Your handler runs with the synthetic event: e.target, e.preventDefault(), e.stopPropagation()
Step 8 → After handlers finish, state updates from the event are batched into one render

Notes:
- Since React 17, listeners are on the root container, not on document.
- Since React 17, there is NO event pooling: you can read e.target in async code.
- Some names differ: onChange fires on every input change (like native "input"), onDoubleClick, onFocus bubbles.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → React हर event type के लिए root container पर (जो div आप createRoot में देते हैं) एक listener लगाता है
Step 2 → User app के अंदर गहरे किसी button पर click करता है
Step 3 → Native click DOM में ऊपर bubble होकर root container तक पहुँचता है
Step 4 → React की listener उसे पकड़कर native event को लपेटने वाला SyntheticEvent बनाती है
Step 5 → React पता लगाता है कि target किस component का है, फिर React tree में ऊपर चलता है
Step 6 → हर matching onClick handler call करता है (capture handlers जैसे onClickCapture पहले)
Step 7 → आपका handler synthetic event के साथ चलता है: e.target, e.preventDefault(), e.stopPropagation()
Step 8 → Handlers के बाद, event की state updates एक render में batch हो जाती हैं

Notes:
- React 17 से listeners document पर नहीं, root container पर होती हैं।
- React 17 से event pooling नहीं है: async code में भी e.target पढ़ सकते हैं।
- कुछ नाम अलग हैं: onChange हर input change पर चलता है (native "input" जैसा), onDoubleClick, onFocus bubble करता है।
```

---

## 🟡 Real World Example
**Flipkart product grid:** A page shows 200 product cards, each with an "Add to cart" button and the whole card is clickable to open the product page. The button's handler calls `e.stopPropagation()` so that clicking "Add to cart" does not also open the product page. React does not attach 200 native listeners; it uses one at the root. Inside a form, `e.preventDefault()` stops the browser from reloading the page on submit.

## 🟡 Real Example Hindi mein
**Flipkart product grid:** Page पर 200 product cards हैं, हर card में "Add to cart" बटन है और पूरा card click करने पर product page खुलता है। बटन का handler `e.stopPropagation()` call करता है ताकि "Add to cart" दबाने पर product page न खुले। React 200 native listeners नहीं लगाता; root पर एक ही listener से काम चलता है। Form के अंदर `e.preventDefault()` browser को submit पर page reload करने से रोकता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: reading the synthetic event
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function EventDemo() {
  function handleClick(e) {                          // e is a SyntheticEvent
    console.log(e.type);                             // "click"
    console.log(e.target.tagName);                   // the element that was clicked, e.g. BUTTON
    console.log(e.currentTarget.tagName);            // the element the handler is attached to
    console.log(e.nativeEvent instanceof MouseEvent);// true: the original browser event
  }

  function handleSubmit(e) {
    e.preventDefault();                              // stop the browser's default form submit (page reload)
    console.log('Form submitted without reload');
  }

  return (
    <form onSubmit={handleSubmit}>
      <button type="button" onClick={handleClick}>Click me</button> {/* camelCase name, function reference */}
      <button type="submit">Submit</button>
    </form>
  );
}

createRoot(document.getElementById('root')).render(<EventDemo />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: bubbling, stopPropagation, delegation by data-attribute, capture phase
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function ProductGrid() {
  const [log, setLog] = useState([]);                // simple on-screen event log
  const write = (msg) => setLog((l) => [...l, msg]); // add a message immutably

  const products = [                                 // sample data
    { id: 'p1', name: 'Redmi Note' },
    { id: 'p2', name: 'Realme 12' },
  ];

  // ONE handler on the parent handles clicks from every card (manual delegation, optional)
  function onGridClick(e) {
    const card = e.target.closest('[data-id]');      // find the card that contains the click
    if (card) write(`open product ${card.dataset.id}`);
  }

  function addToCart(e, id) {
    e.stopPropagation();                             // do NOT let the click reach the card/grid handlers
    write(`added ${id} to cart`);
  }

  return (
    <div>
      {/* Capture phase runs first: useful for analytics that must see every click */}
      <div onClickCapture={() => write('capture: grid')} onClick={onGridClick}>
        {products.map((p) => (
          <div key={p.id} data-id={p.id} style={{ border: '1px solid #ccc', margin: 6, padding: 8 }}>
            {p.name}{' '}
            <button onClick={(e) => addToCart(e, p.id)}>Add to cart</button> {/* stops bubbling */}
          </div>
        ))}
      </div>

      {/* Keyboard events and modifiers on the synthetic event */}
      <input
        placeholder="Press Enter or Ctrl+K"
        onKeyDown={(e) => {
          if (e.key === 'Enter') write(`search: ${e.currentTarget.value}`); // e.key is normalized
          if (e.ctrlKey && e.key.toLowerCase() === 'k') {                   // modifier keys are booleans
            e.preventDefault();                                             // stop the browser shortcut
            write('quick search opened');
          }
        }}
      />
      <pre>{log.join('\n')}</pre>                    {/* show the log */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<ProductGrid />);
```

---

## 🟠 Next.js Connection
Event handlers need a Client Component. A Server Component cannot have `onClick`, because the function would have to be sent to the browser. Add `'use client'` to the file that has the handlers. Server Components can pass Server Actions to forms instead of event handlers (`<form action={serverAction}>`), which work even before the JS loads.

```jsx
// app/product/AddToCartButton.jsx (Client Component)
'use client';                                        // required: this file uses onClick
import { useState } from 'react';

export default function AddToCartButton({ productId }) {
  const [added, setAdded] = useState(false);         // local UI state
  async function handleClick(e) {
    e.stopPropagation();                             // synthetic event works the same in Next.js
    await fetch('/api/cart', { method: 'POST', body: JSON.stringify({ productId }) }); // call a route handler
    setAdded(true);                                  // update the UI after success
  }
  return <button onClick={handleClick}>{added ? 'Added' : 'Add to cart'}</button>;
}
```

```jsx
// app/product/page.jsx (Server Component): NO onClick here
import AddToCartButton from './AddToCartButton';

export default function Page() {
  return (
    <div>
      <h1>Redmi Note</h1>
      {/* <button onClick={...}> would be an error here: event handlers cannot be passed in a Server Component */}
      <AddToCartButton productId="p1" />
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling the handler instead of passing it
✅ **Correct:** Pass a function reference (or wrap in an arrow function to pass arguments)

```jsx
// Wrong: runs during render, and its return value becomes the handler
<button onClick={handleClick()}>Buy</button>         // ❌ called immediately, can cause an infinite loop if it sets state

// Right
<button onClick={handleClick}>Buy</button>           // ✅ reference
<button onClick={() => handleClick(id)}>Buy</button> // ✅ arrow wrapper when you need arguments
```

❌ **Mistake 2:** Using `return false` to stop the default action
✅ **Correct:** Call `e.preventDefault()` explicitly

```jsx
// Wrong: return false works in plain HTML attributes, not in React
<a href="/x" onClick={() => { return false; }}>Link</a>  // ❌ the browser still navigates

// Right
<a href="/x" onClick={(e) => { e.preventDefault(); }}>Link</a> // ✅
```

❌ **Mistake 3:** Mixing native `addEventListener` on document with React handlers and expecting a certain order
✅ **Correct:** Prefer React handlers; if you must use native ones, remember React listens at the root container

```jsx
// Wrong assumption: e.stopPropagation() in React will stop a native listener on document
useEffect(() => {
  const h = () => console.log('document click');
  document.addEventListener('click', h);             // fires AFTER React's root listener
  return () => document.removeEventListener('click', h); // always clean up native listeners
}, []);
// In React 17+, calling e.stopPropagation() in a React handler stops the native event at the root,
// so this document listener does not run. Native listeners ON the root or the element itself are different.
```

---

## 🧠 Tricky Interview Question

```jsx
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    const h = () => console.log('native body');
    document.body.addEventListener('click', h);       // native listener on body
    return () => document.body.removeEventListener('click', h);
  }, []);

  return (
    <div onClick={() => console.log('react div')}>
      <button
        onClick={(e) => {
          console.log('react button');
          e.stopPropagation();                        // synthetic stopPropagation
        }}
      >
        Click
      </button>
    </div>
  );
}
// The user clicks the button. What is logged (React 17+)?
```
**Answer:** Only `react button`. React's single listener is on the root container, which sits **below** `body` in the DOM. When the native click arrives at the root container, React dispatches `react button`, then `e.stopPropagation()` stops both the synthetic propagation (`react div` is skipped) and the native propagation (so it never reaches `body`, and `native body` is not logged). In React 16, listeners were on `document`, so the native listener on `body` would have fired first, and the result was different. This is why the 17 change matters for apps that mix React with other libraries.

---

## ⚫ Interview Questions + Answers

Q1: What is a SyntheticEvent?
A1: A wrapper object React creates around the browser's native event. It has the same interface (`target`, `preventDefault`, `stopPropagation`, `key`) but works consistently across browsers. The native event is at `e.nativeEvent`.

Q2: How does React handle events internally?
A2: By event delegation. React registers one listener per event type on the root container, and when an event bubbles up, React figures out which components' handlers should run and calls them with a SyntheticEvent. Fewer listeners mean less memory and no manual cleanup.

Q3: What was event pooling and is it still there?
A3: Before React 17, SyntheticEvent objects were reused (pooled) and their properties were nulled after the handler finished, so you needed `e.persist()` for async access. React 17 removed pooling, so reading `e.target` in `setTimeout` or after `await` works now. `e.persist()` is a no-op kept for compatibility.

Q4: What is the difference between `e.target` and `e.currentTarget`?
A4: `target` is the element that actually triggered the event (the deepest clicked element). `currentTarget` is the element the handler is attached to. With nested elements and bubbling, they can differ.

Q5: Why does React `onChange` fire on every keystroke while the native `change` fires on blur?
A5: React's `onChange` maps to the native `input` event (plus others) for text inputs so that controlled inputs can update with every key. The native `change` event only fires when the input loses focus after a change. It is a deliberate React difference.

---

## 🔷 When to Use + When Not to Use
✅ **Use React event props when:**
- You handle user actions in components (click, change, submit, key events)
- You need one consistent behavior across browsers
- Lists are long and you want delegation without managing listeners

❌ **Use native `addEventListener` (in `useEffect`, with cleanup) when:**
- Events happen outside React's tree: `window` resize/scroll, `document` keydown shortcuts, `online/offline`
- You need non-React-supported options like `{ passive: true }` or a non-bubbling event not exposed by React
- You integrate a third-party non-React library

---

## 📊 Visual Diagram

```
 User clicks <button>
      │  native click event bubbles up the real DOM
      ▼
 ┌─────────────────────────────────────────┐
 │ root container <div id="root">          │ ◄── React's ONE click listener
 │   <div onClick=...>      (React tree)   │
 │     <button onClick=...> (React tree)   │
 └─────────────────────────────────────────┘
      │ React makes a SyntheticEvent (wraps nativeEvent)
      ▼
 capture handlers (parent → child) → target handler → bubble handlers (child → parent)
      │
      ▼  e.stopPropagation() stops this chain AND the native event at the root

 Performance: one listener per event type instead of one per element;
 handlers created inline cause no extra renders by themselves.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SyntheticEvent | React's cross-browser event wrapper | React का cross-browser event wrapper |
| nativeEvent | The original browser event | असली browser event |
| Event delegation | One listener at the top handles many elements | ऊपर एक listener कई elements संभालती है |
| Bubbling | Event travels from child up to parents | Event child से parents की ओर जाना |
| Capture phase | Event travels from root down to target first | Event पहले root से target तक नीचे जाना |
| preventDefault | Stop the browser's default action | Browser की default action रोकना |
| stopPropagation | Stop the event from reaching parent handlers | Event को parent handlers तक पहुँचने से रोकना |
| Event pooling | Old reuse of event objects (removed in 17) | Event objects का पुराना reuse (17 में हटा) |

---

## ⚡ 3-Line Summary
**English:**
1. React wraps native events in SyntheticEvent objects with a consistent, cross-browser API and uses one delegated listener per event type at the root.
2. Pass function references in camelCase props, use `preventDefault()` and `stopPropagation()` explicitly, and remember there is no pooling since React 17.
3. In Next.js, event handlers work only in Client Components (`'use client'`); use native listeners with cleanup for `window` and `document` events.

**Hindi:**
1. React native events को SyntheticEvent में लपेटता है जिसका API हर browser में एक जैसा है, और root पर हर event type के लिए एक delegated listener लगाता है।
2. camelCase props में function reference दो, `preventDefault()` और `stopPropagation()` खुद call करो, और याद रखो कि React 17 से pooling नहीं है।
3. Next.js में event handlers सिर्फ Client Components (`'use client'`) में चलते हैं; `window` और `document` events के लिए cleanup के साथ native listeners इस्तेमाल करो।

---

## ➡️ Next Topic
**28. Forms in React** — Events समझने के बाद सबसे आम इस्तेमाल है forms: input, submit, validation और React 19 के form actions। Real apps (login, checkout, search) इसी के बिना नहीं बनते।
