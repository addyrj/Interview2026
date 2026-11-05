# Hooks Cheatsheet (Topics 34-57)

Quick revision of every hook in `02-hooks/`. Each item: gist, key snippet, one-line Hindi hint. Full detail lives in the numbered note.

---

## 34. What are Hooks (+ Rules)
- Hooks are `use*` functions that give function components state, lifecycle, context and refs.
- Rules: call only at top level (never in conditions or loops) and only from components or custom hooks.
- Custom hooks extract shared stateful logic, which is the real win over HOCs and render props.

```jsx
function useData(id) {
  const [data, setData] = useState(null);
  useEffect(() => { if (id) fetchData(id).then(setData); }, [id]); // condition INSIDE the hook
  return data;
}
```
Trap: an early `return` before a hook throws "Rendered more hooks than previous render". Put returns after all hooks.

> हिंदी: Hooks सिर्फ top level पर बुलाओ, condition या loop के अंदर कभी नहीं।

---

## 35. useState deep dive
- Returns a snapshot value plus a setter that schedules a re-render; updates are batched.
- Use the updater form for updates based on previous state, a lazy initializer for expensive start values, copies for objects/arrays.
- Setting the same value (`Object.is`) causes no re-render.

```jsx
setCount(count + 1);          // plain value: replaces state, uses snapshot
setCount((c) => c + 1);       // updater: gets the latest queued value
const [v] = useState(() => JSON.parse(localStorage.getItem('v'))); // lazy init
```
Trap: `+1, +1, updater +1, set(count+5), updater +1` from 0 gives 6 with one render.

> हिंदी: पिछली state पर निर्भर update हो तो `setX(x => ...)` वाला form इस्तेमाल करो।

---

## 36. useEffect
- Runs after render. `[]` = once on mount, `[dep]` = when dep changes, no array = every render.
- Return a cleanup function for timers, listeners, subscriptions.
- Never make the effect callback `async`; define an async function inside and call it.

```jsx
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal }).then((r) => r.json()).then(setData);
  return () => controller.abort(); // avoids race conditions and stale setState
}, [url]);
```
Trap: `setInterval(() => setCount(count + 1), 1000)` with `[]` shows `1` forever (stale closure); use `setCount(c => c + 1)`.

> हिंदी: Effect render के बाद चलता है; cleanup हमेशा लिखो और callback को async मत बनाओ।

---

## 37. useEffect dependency array
- Decides when the effect re-runs: never (`[]`), always (no array), or when listed values change.
- Compared with `Object.is`, so a new object, array or function each render re-runs the effect.
- List everything the effect reads; fix the design instead of silencing the linter.

```jsx
useEffect(() => { console.log('ran'); }, [user]);
// setUser({ name: 'A' }) again => NEW object => effect runs again
// setUser(user) (same reference) => bails out, no effect
```

> हिंदी: Dependency में नया object/function हर render बनता है, इसलिए effect बार-बार चलता है।

---

## 38. useEffect cleanup
- The returned function runs before the next effect and on unmount.
- Use it to stop timers, remove listeners, close sockets and abort stale requests.
- Cleanup sees the values of its own render; StrictMode's double-run helps catch missing cleanups.

```jsx
useEffect(() => {
  console.log('effect', n);
  return () => console.log('cleanup', n); // logs the OLD n
}, [n]);
```

> हिंदी: Cleanup अपने ही render की पुरानी value देखता है और अगले effect से पहले चलता है।

---

## 39. useEffect vs componentDidMount
- One dependency-driven hook replaces `componentDidMount`, `componentDidUpdate`, `componentWillUnmount`.
- Runs after paint, captures its own render's values, keeps setup and cleanup together.
- Classes are still needed for Error Boundaries; Server Components remove much mount-time fetching.

```jsx
useEffect(() => {
  const id = setInterval(() => console.log(count), 1000); // logs 0 forever with []
  return () => clearInterval(id);
}, []);
```
Fix: add `count` to deps, or read from a ref.

> हिंदी: तीनों lifecycle methods की जगह एक `useEffect`, पर closure की पुरानी value से सावधान।

---

## 40. useRef
- Two uses: a DOM element reference and a persistent mutable value (timer ids, flags, previous values).
- Changing `ref.current` does NOT trigger a re-render.
- Read `ref.current` in handlers or effects, never during render.

```jsx
const inputRef = useRef(null);
const latest = useRef(count);
useEffect(() => { latest.current = count; });   // ref escapes stale closures
<input ref={inputRef} />;  // inputRef.current.focus() in a handler
```

> हिंदी: `useRef` की value बदलने से re-render नहीं होता, DOM पकड़ने और latest value रखने के काम आता है।

---

## 41. useRef vs useState
- `useState` is for values shown on screen; `useRef` is a mutable box that never re-renders.
- Refs for DOM nodes, timer ids, previous values; state for UI data.
- Do not read or write refs during render, and do not hide visible data in refs.

```jsx
function handle() {
  setCount(count + 1);          // snapshot: logs old count
  ref.current = ref.current + 1; // already updated
  console.log('state:', count, 'ref:', ref.current); // state: 0 ref: 1
}
```

> हिंदी: स्क्रीन पर दिखने वाला data state में, छुपा हुआ bookkeeping ref में।

---

## 42. useContext
- `useContext(Ctx)` reads the nearest Provider value without prop drilling.
- Every consumer re-renders when the value changes, so avoid fast-changing data.
- Pattern: `createContext` -> Provider -> custom hook with an error check.

```jsx
const CountContext = createContext(0);
function Child() { const count = useContext(CountContext); return <div>{count}</div>; }
// Parent: <CountContext.Provider value={count}><Child /></CountContext.Provider>
```
Trap: 3 clicks = Child logs 4 times (1 mount + 3 updates).

> हिंदी: Context value बदली तो उसे पढ़ने वाले सारे components दोबारा render होते हैं।

---

## 43. Context API complete guide
- Context broadcasts a Provider value to every consumer below it.
- Memoize the value and split contexts by update frequency.
- For slow-changing app-wide data; in Next.js it needs Client Components.

```jsx
const Ctx = createContext('default');
const Memo = React.memo(function Child() { console.log(useContext(Ctx)); return null; });
// Ctx.Provider value changes => Memo STILL re-renders: memo cannot block context
```

> हिंदी: `React.memo` context के update को नहीं रोक सकता।

---

## 44. Context vs props drilling
- Props are explicit and best for short paths; Context is implicit and best for slow, widely used data.
- Try composition and moving state down before Context.
- Fast-changing global state belongs in a store.

```jsx
function Parent() { console.log('Parent'); return <Child />; }
// App re-renders => new <Parent /> element => Parent logs again (not because of context)
```

> हिंदी: Context से पहले composition और state को नीचे ले जाना आज़माओ।

---

## 45. useReducer
- `useReducer(reducer, initialState)`: all update logic in one pure `(state, action) => newState`.
- Reducer must not mutate or run side effects.
- Optional third argument is a lazy initializer: `init(initialArg)` runs once on mount.

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'INCREMENT': return { ...state, count: state.count + 1 };
    default: return state;
  }
}
const [state, dispatch] = useReducer(reducer, startCount, init);
```

> हिंदी: जटिल state और कई जुड़े fields के लिए `useReducer`, reducer हमेशा pure रखो।

---

## 46. useReducer vs useState
- `useState` for simple values; `useReducer` for related state with rules.
- `dispatch` is stable; choice is about clarity and testability, not speed.
- React 19 `useActionState` is a reducer for form actions.

```jsx
function reducer(state, action) {
  state.count += 1;   // mutation + same reference => Object.is bails out, UI stays 0
  return state;
}
```
Fix: `return { ...state, count: state.count + 1 }`. StrictMode calls reducers twice to expose impurity.

> हिंदी: Reducer में state mutate करोगे तो UI update ही नहीं होगा।

---

## 47. useMemo
- `useMemo(fn, deps)` caches the return value; recomputes only when deps change.
- Two uses: expensive calculations, and a stable object reference for `React.memo` children.
- Has overhead; profile before using.

```jsx
const visible = useMemo(() => items.filter((i) => i.ok), [items]);
const value = useMemo(() => ({ number: count }), [count]);
const same = useMemo(() => ({ number: count }), [count]);
console.log(value === same); // false: two separate calls, two objects
```

> हिंदी: भारी गणना या stable reference के लिए `useMemo`, हर जगह मत लगाओ।

---

## 48. useCallback
- `useCallback(fn, deps)` returns the same function reference until deps change.
- Only useful together with `React.memo` (or effect deps) that rely on that stability.
- Empty deps with outside values gives a stale closure.

```jsx
const handleIncrement = useCallback(() => setCount((c) => c + 1), []);
<Counter onIncrement={handleIncrement} />; // memo(Counter) skips when typing elsewhere
```

> हिंदी: `useCallback` function का reference स्थिर रखता है, `memo` के साथ ही फायदा देता है।

---

## 49. useMemo vs useCallback
- `useMemo` caches a computed value; `useCallback` caches a function. Both recompute only on dependency change.
- Measure first, list all dependencies, skip for trivial work; the React Compiler can automate most of it.

```jsx
const style = useMemo(() => ({ color: 'red' }), []);
const onClick = useCallback(() => console.log('clicked'), []);
// <Child style={style} onClick={onClick} /> skips; inline {{...}} and () => ... re-render it
```

> हिंदी: Value cache करनी हो तो `useMemo`, function cache करना हो तो `useCallback`।

---

## 50. useLayoutEffect vs useEffect
- `useLayoutEffect` runs after DOM update but before paint (blocking); `useEffect` after paint.
- Default to `useEffect`; use layout effect only to measure/adjust layout and avoid flicker.
- Does not run on the server; in Next.js use it in Client Components.

```text
Mount:  render 0 -> layout effect 0 -> effect 0
Click:  render 1 -> layout cleanup 0 -> layout effect 1 -> effect cleanup 0 -> effect 1
```

> हिंदी: Paint से पहले layout मापना हो तभी `useLayoutEffect`, वरना `useEffect`।

---

## 51. useId
- Returns a unique id that is identical on server and client (no hydration mismatch).
- Use for `htmlFor` and ARIA links; derive more ids with suffixes from one call.
- Not for list keys or CSS selectors. Id format (like `:r0:`) is version-dependent.

```jsx
const id = useId();
return (<><label htmlFor={id + '-email'}>Email</label><input id={id + '-email'} /></>);
```

> हिंदी: Server और client पर एक जैसी unique id के लिए `useId`, list key के लिए नहीं।

---

## 52. useTransition
- Marks a heavy state update as low priority so urgent work (typing) stays instant.
- Returns `isPending`; React can interrupt and restart the transition.
- Do not wrap input values or cheap updates; it does not fix slow networks.

```jsx
const [isPending, startTransition] = useTransition();
startTransition(() => setCount((c) => c + 1));
console.log(isPending); // false in the handler: it is a snapshot of this render
```

> हिंदी: भारी update को `startTransition` में डालो ताकि typing अटके नहीं।

---

## 53. useDeferredValue
- Gives a lagging copy of a value so heavy UI updates in the background.
- Pair with `memo`; compare `value !== deferred` for a stale indicator.
- It is not debouncing and does not reduce network requests.

```jsx
const deferred = useDeferredValue(text);
console.log(text, deferred); // after typing: "ab a" first, then "ab ab"
```

> हिंदी: `useDeferredValue` value की पीछे चलने वाली copy देता है, debounce नहीं है।

---

## 54. useImperativeHandle
- `useImperativeHandle(ref, create, deps)` replaces what the parent sees in `ref.current` with a small custom object.
- For imperative actions only (focus, clear, scroll, play); everything else stays props and state.
- Needs `'use client'` in Next.js; list handle dependencies in `deps`.

```jsx
const Input = forwardRef((props, ref) => {
  const inner = useRef(null);
  useImperativeHandle(ref, () => ({ focus() { inner.current.focus(); } }), []);
  return <input ref={inner} />;
});
// parent: typeof r.current.focus === 'function', r.current.value === undefined
```
Version note: in React 19, `ref` is a normal prop and `forwardRef` is no longer needed.

> हिंदी: Parent को पूरा DOM node नहीं, सिर्फ चुने हुए methods दिखाने के लिए।

---

## 55. Custom hooks
- A function starting with `use` that calls other hooks to package reusable stateful logic.
- Each call gets its OWN isolated state: hooks share logic, not state.
- Common: `useFetch`, `useDebounce`, `useForm`, `useLocalStorage`, `useWindowSize`.

```jsx
function useCounter(initial = 0) {
  const [count, setCount] = useState(initial);
  return { count, increment: () => setCount((c) => c + 1) };
}
```
To share state across components use Context or a store.

> हिंदी: हर component को hook की अपनी अलग state मिलती है, साझा नहीं।

---

## 56. Custom hook real examples
- Always clean up effects, guard browser APIs for SSR, return stable references.
- Calling `inc()` twice with `setCount(count + 1)` only adds 1; use the updater form for 2.

```jsx
function useWindowSize() {
  const [size, setSize] = useState({ w: 0, h: 0 }); // 0 on the server: SSR safe
  useEffect(() => {
    const on = () => setSize({ w: window.innerWidth, h: window.innerHeight });
    on();
    window.addEventListener('resize', on);
    return () => window.removeEventListener('resize', on);
  }, []);
  return size;
}
```

> हिंदी: Browser API सिर्फ effect के अंदर छुओ ताकि SSR न टूटे।

---

## 57. Rules of Hooks: why
- Same order on every render, top level only, only from components or custom hooks.
- React matches hooks by call position in a list; skipping one shifts the later ones into wrong slots.
- Put conditions inside hooks or in child components; keep the `react-hooks` ESLint rule on.

```jsx
function App() {
  const [on, setOn] = useState(false);
  if (on) { const [x] = useState('hello'); } // BAD: error "Rendered more hooks than ..."
  return <button onClick={() => setOn(true)}>Click</button>;
}
```
Exact error wording is version-dependent.

> हिंदी: Hooks list में position से मिलते हैं, इसलिए क्रम कभी नहीं बदलना चाहिए।

---

## One-glance table

| Hook | Re-renders? | Use for |
|---|---|---|
| useState | yes | UI data |
| useRef | no | DOM, mutable box |
| useReducer | yes | related state, rules |
| useContext | when value changes | shared slow data |
| useMemo / useCallback | n/a | stable value / function |
| useEffect | after paint | side effects |
| useLayoutEffect | before paint | measure DOM |
| useTransition / useDeferredValue | n/a | keep UI responsive |
| useId | n/a | SSR-safe ids |
| useImperativeHandle | n/a | expose small ref API |

> हिंदी: पहले state/ref चुनो, फिर ज़रूरत हो तभी memo और बाकी optimization hooks।
