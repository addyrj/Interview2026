# 54. useImperativeHandle Hook
# हिंदी में: useImperativeHandle — Parent को child के सिर्फ चुने हुए methods देना

---

## 🔵 Simple Definition (English)
`useImperativeHandle` lets a child component decide exactly what a parent gets when the parent uses `ref` on it. Instead of exposing the raw DOM node, the child exposes a small custom object (for example `{ focus, clear }`). It is an escape hatch, used rarely.

## 🔵 सरल परिभाषा (Hindi)
`useImperativeHandle` से child component तय करता है कि parent को `ref` के ज़रिए क्या मिलेगा। पूरा DOM node देने की जगह child एक छोटा custom object (जैसे `{ focus, clear }`) देता है। यह एक escape hatch है और कभी-कभी ही इस्तेमाल होता है।

---

## 🔴 Problem it Solves

React is declarative: the parent sends props, the child renders. But some things are naturally imperative: focus an input, scroll a list to the top, play or pause a video, open a modal. If you forward a plain `ref` to the DOM node, the parent gets full access to the node and can change anything (`style`, `value`, `remove()`), which breaks encapsulation. `useImperativeHandle` exposes only a safe, small API.

```jsx
// PROBLEM: parent receives the raw <input> and can do anything with it
<FancyInput ref={ref} />
ref.current.style.display = 'none';   // parent breaks the child's internals

// SOLUTION: parent only gets { focus, clear }
ref.current.focus();                  // allowed
ref.current.clear();                  // allowed
// ref.current.style → undefined (not exposed)
```

## 🔴 यह क्यों बना? (Hindi)
React declarative है: parent props भेजता है, child render करता है। लेकिन कुछ काम imperative होते हैं: input पर focus करना, list को ऊपर scroll करना, video play/pause करना। अगर आप सीधा `ref` DOM node तक forward करें तो parent के पास पूरा node आ जाता है और वह `style`, `value`, `remove()` कुछ भी बदल सकता है, जिससे encapsulation टूटती है। `useImperativeHandle` सिर्फ एक छोटा और सुरक्षित API देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent creates a ref:                 const ref = useRef(null)
Step 2 → Parent passes it to the child:        <Child ref={ref} />
Step 3 → Child receives it (React 19: normal prop; React 18: forwardRef)
Step 4 → Child keeps its own inner ref for the real DOM node
Step 5 → Child calls useImperativeHandle(ref, () => ({ focus, clear }), [deps])
Step 6 → After commit React sets ref.current = the object returned by the function
Step 7 → On unmount React sets ref.current = null; if deps change the object is rebuilt

SIGNATURE: useImperativeHandle(ref, createHandle, dependencies?)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent एक ref बनाता है:               const ref = useRef(null)
Step 2 → उसे child को देता है:                 <Child ref={ref} />
Step 3 → Child उसे लेता है (React 19: normal prop; React 18: forwardRef)
Step 4 → Child असली DOM node के लिए अपना अंदरूनी ref रखता है
Step 5 → Child बुलाता है useImperativeHandle(ref, () => ({ focus, clear }), [deps])
Step 6 → Commit के बाद React ref.current = उस function का returned object कर देता है
Step 7 → Unmount पर ref.current = null; deps बदलें तो object दोबारा बनता है

SIGNATURE: useImperativeHandle(ref, createHandle, dependencies?)
```

---

## 🟡 Real World Example
**Swiggy login OTP screen:** There are six small OTP boxes inside an `OtpInput` component. The parent screen has a "Resend OTP" button. After resending, the parent must clear all boxes and focus the first one. The parent does not know about the six inputs. `OtpInput` exposes `{ clear, focusFirst }` and the parent just calls `otpRef.current.clear()`.

## 🟡 Real Example Hindi mein
**Swiggy login OTP screen:** `OtpInput` component के अंदर छह छोटे OTP boxes हैं। Parent screen पर "Resend OTP" बटन है। Resend के बाद parent को सारे boxes खाली करके पहले box पर focus करना है। Parent को छह inputs के बारे में कुछ नहीं पता। `OtpInput` सिर्फ `{ clear, focusFirst }` देता है और parent बस `otpRef.current.clear()` बुलाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: expose focus() and clear() from a custom input (React 19 style, ref is a normal prop)
import { useRef, useImperativeHandle } from 'react';   // hooks we need
import { createRoot } from 'react-dom/client';          // React 18/19 root API

function FancyInput({ ref, placeholder }) {             // React 19: ref arrives as a prop
  const inputRef = useRef(null);                        // inner ref to the real <input>

  useImperativeHandle(ref, () => ({                     // what the PARENT will see in ref.current
    focus() { inputRef.current.focus(); },              // allowed: focus the input
    clear() { inputRef.current.value = ''; },           // allowed: empty the input
  }), []);                                              // no dependencies: object is created once

  return <input ref={inputRef} placeholder={placeholder} />; // the real DOM node stays private
}

function App() {
  const fancyRef = useRef(null);                        // parent ref, will hold { focus, clear }
  return (
    <div>
      <FancyInput ref={fancyRef} placeholder="Search dishes" /> {/* give the ref to the child */}
      <button onClick={() => fancyRef.current.focus()}>Focus</button>  {/* calls the exposed method */}
      <button onClick={() => fancyRef.current.clear()}>Clear</button>  {/* calls the exposed method */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount the app
```

```jsx
// React 18 version: the same child needs forwardRef to receive ref
import { forwardRef, useRef, useImperativeHandle } from 'react';

const FancyInput18 = forwardRef(function FancyInput18({ placeholder }, ref) { // ref as 2nd argument
  const inputRef = useRef(null);                        // inner DOM ref
  useImperativeHandle(ref, () => ({                     // same exposed API
    focus: () => inputRef.current.focus(),
    clear: () => { inputRef.current.value = ''; },
  }), []);
  return <input ref={inputRef} placeholder={placeholder} />;
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: OTP input with an imperative API; handle depends on props, so deps are listed
import { useRef, useState, useImperativeHandle } from 'react';
import { createRoot } from 'react-dom/client';

function OtpInput({ ref, length = 6, onComplete }) {
  const [digits, setDigits] = useState(Array(length).fill(''));   // controlled values
  const boxes = useRef([]);                                       // array of the real <input> nodes

  useImperativeHandle(ref, () => ({
    focusFirst() { boxes.current[0]?.focus(); },                  // move cursor to box 1
    clear() {
      setDigits(Array(length).fill(''));                          // reset the state
      boxes.current[0]?.focus();                                  // and focus the first box
    },
    getValue() { return digits.join(''); },                       // reads the CURRENT digits
  }), [length, digits]);                                          // rebuild when digits change, so getValue is never stale

  function handleChange(i, v) {
    if (!/^\d?$/.test(v)) return;                                 // allow only one digit
    const next = [...digits];                                     // copy, never mutate state
    next[i] = v;                                                  // set this box
    setDigits(next);                                              // update state
    if (v && i < length - 1) boxes.current[i + 1].focus();        // auto-advance
    if (next.every(Boolean)) onComplete?.(next.join(''));         // all filled → notify parent
  }

  return (
    <div>
      {digits.map((d, i) => (
        <input
          key={i}                                                 // fixed length list, index key is fine
          ref={el => { boxes.current[i] = el; }}                  // store each node
          value={d}
          maxLength={1}
          inputMode="numeric"
          onChange={e => handleChange(i, e.target.value)}
          style={{ width: 32, marginRight: 6, textAlign: 'center' }}
        />
      ))}
    </div>
  );
}

function LoginScreen() {
  const otpRef = useRef(null);                                    // will hold the exposed API
  return (
    <div>
      <OtpInput ref={otpRef} onComplete={code => console.log('OTP', code)} />
      <button onClick={() => otpRef.current.clear()}>Resend OTP</button> {/* parent uses the API */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<LoginScreen />);
```

---

## 🟠 Next.js Connection

`useImperativeHandle` needs a ref and the browser DOM, so the component that uses it must be a **Client Component** (`'use client'`). A Server Component page can still render it. Refs cannot be passed from a Server Component, so keep the parent that holds the ref (the one with `useRef`) in a client file too.

```jsx
// app/login/LoginForm.jsx (Client Component: uses refs and hooks)
'use client';                                        // required: refs and hooks only work on the client
import { useRef } from 'react';
import OtpInput from './OtpInput';                   // also a 'use client' file (the one using the hook)

export default function LoginForm() {
  const otpRef = useRef(null);                       // ref lives in the client tree
  return (
    <>
      <OtpInput ref={otpRef} />
      <button onClick={() => otpRef.current.clear()}>Resend</button>
    </>
  );
}
```

```jsx
// app/login/page.jsx (Server Component: no hooks, just renders the client form)
import LoginForm from './LoginForm';                 // client boundary starts inside LoginForm
export default function Page() { return <LoginForm />; } // static shell from the server
```

Re-render behavior: the handle object is recreated after a render only if `deps` changed (or on every render when `deps` is omitted). Performance impact is tiny, but a `getValue` that reads state needs that state in `deps`.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using refs for things props can do (for example controlling a modal with `ref.open()` instead of an `isOpen` prop)
✅ **Correct:** Use props and state first. Use imperative handles only for focus, scroll, play/pause, text selection and similar.

```jsx
// Wrong: imperative modal control, hard to reason about and to test
modalRef.current.open();

// Right: declarative, state drives the UI
<Modal isOpen={isOpen} onClose={() => setIsOpen(false)} />
```

❌ **Mistake 2:** Forgetting the dependency array when the handle reads props or state (stale values)
✅ **Correct:** List everything the handle uses in `deps`

```jsx
// Wrong: getValue always returns the value from the first render
useImperativeHandle(ref, () => ({ getValue: () => value }), []);   // ❌ stale

// Right: rebuild the handle when value changes
useImperativeHandle(ref, () => ({ getValue: () => value }), [value]); // ✅ fresh
```

❌ **Mistake 3:** Expecting `ref.current` to be the DOM node, or reading it during render
✅ **Correct:** `ref.current` is your custom object, and it is only set after commit. Use it in event handlers or effects.

```jsx
// Wrong: ref.current is null during the first render
function Parent() {
  const ref = useRef(null);
  const text = ref.current.value;                    // ❌ TypeError: null
  return <Child ref={ref} />;
}

// Right: read it later, in a handler or effect
function Parent2() {
  const ref = useRef(null);
  return <><Child ref={ref} /><button onClick={() => ref.current.focus()}>Go</button></>; // ✅
}
```

---

## 🧠 Tricky Interview Question

```jsx
import { forwardRef, useRef, useEffect, useImperativeHandle } from 'react';

const Input = forwardRef((props, ref) => {
  const inner = useRef(null);
  useImperativeHandle(ref, () => ({
    focus() { inner.current.focus(); },
  }), []);
  return <input ref={inner} />;
});

function App() {
  const r = useRef(null);
  useEffect(() => {
    console.log(typeof r.current.focus);
    console.log(r.current.value);
    console.log(r.current instanceof HTMLInputElement);
  }, []);
  return <Input ref={r} />;
}
```
**Answer:** The output is `function`, `undefined`, `false`. The parent's `r.current` is the custom object `{ focus }`, not the `<input>`. So `focus` exists, but `value` was never exposed (`undefined`), and the object is not an `HTMLInputElement`. The imperative handle replaces the default ref value. The effect in the parent runs after the child's handle is attached, so `r.current` is not `null` there.

---

## ⚫ Interview Questions + Answers

Q1: What does `useImperativeHandle` do?
A1: It customizes the value that a parent receives in `ref.current` when it passes a `ref` to the child. The child returns an object with only the methods it wants to expose.

Q2: Why not just forward the ref to the DOM node?
A2: Forwarding gives the parent full control of the node, so it can change styles or value and break the child's internals. An imperative handle gives a small, stable API, so the child can change its internals later without breaking parents.

Q3: How do you receive `ref` in React 19 versus React 18?
A3: React 19 passes `ref` as a normal prop to function components, so `function Child({ ref })` works. In React 18 you wrap the component with `forwardRef` and get `ref` as the second argument. `forwardRef` still works in 19 but is planned to be deprecated.

Q4: When is the dependency array important?
A4: When the returned object uses props or state. Without correct deps the methods close over old values (stale closure). If you omit the array, the handle is recreated after every render, which is always fresh but does a little extra work.

Q5: When should you avoid it?
A5: Whenever a prop or state can express the same thing. Imperative code is harder to read and test. Keep it for focus, scroll, media playback, text selection and integration with non-React libraries.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The parent must trigger an action: focus, scroll to item, play/pause, reset
- You build a reusable library component (input, video player, virtual list) with a small public API
- You wrap a third-party imperative widget (map, chart, editor)

❌ **Avoid when:**
- A prop (`isOpen`, `value`, `autoFocus`) can describe the behavior
- You only need the DOM node: forward the `ref` directly
- You want to share data (use props, context or state, not a ref)

---

## 📊 Visual Diagram

```
  WITHOUT useImperativeHandle         WITH useImperativeHandle

  Parent                              Parent
   ref ───────────┐                    ref ───────────┐
                  ▼                                   ▼
            Child                               Child
            <input> (full DOM node)             { focus(), clear() }  ← custom object
            parent can touch anything                 │
                                                      ▼ uses inner ref privately
                                                 <input> (hidden from the parent)

  Timeline: render → commit → ref.current = handle → (deps change → handle rebuilt) → unmount → null
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Imperative | Telling the DOM exactly what to do | सीधे command देना (कैसे करना है) |
| Declarative | Describing the result, React does the work | नतीजा बताना, काम React करता है |
| ref | Mutable box that survives renders | Renders के बीच बचा रहने वाला box |
| forwardRef | React 18 way to pass ref into a component | Component में ref भेजने का React 18 तरीका |
| Handle | Custom object exposed through ref | ref से दिया गया custom object |
| Encapsulation | Hiding internals, exposing a small API | अंदर की चीज़ें छुपाकर छोटा API देना |
| Stale closure | Function using old values | पुरानी values इस्तेमाल करने वाला function |
| Escape hatch | Rare tool to step outside React's model | React के model से बाहर जाने का रास्ता |

---

## ⚡ 3-Line Summary
**English:**
1. `useImperativeHandle(ref, create, deps)` replaces what the parent sees in `ref.current` with a small custom object.
2. Use it only for imperative actions like focus, clear, scroll and play, and keep everything else in props and state.
3. List all values the handle reads in `deps`, and remember that the component needs `'use client'` in Next.js.

**Hindi:**
1. `useImperativeHandle(ref, create, deps)` parent के `ref.current` को एक छोटे custom object से बदल देता है।
2. इसे सिर्फ focus, clear, scroll, play जैसे imperative कामों के लिए इस्तेमाल करो, बाकी सब props और state में रखो।
3. Handle जो values पढ़ता है उन्हें `deps` में लिखो, और Next.js में component को `'use client'` चाहिए।

---

## ➡️ Next Topic
**56. Custom Hook — Real Examples** — अब तक के hooks सीखने के बाद देखें कि असली projects में `useFetch`, `useDebounce`, `useLocalStorage` जैसे custom hooks कैसे बनते हैं और logic कैसे reuse होता है।
