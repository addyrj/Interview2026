# Top 50 React + Next.js Interview Q&A

Concise answers drawn from the Interview Questions and notes in each topic. Version-dependent facts are flagged. Each has a Hindi hint and its source note (under `react-next-js/`).


## 1. React fundamentals

**Q1. What is React and how does it differ from a framework?**  
A: A JavaScript library for building UIs (the view layer only). A framework like Angular is opinionated and bundles routing and HTTP; with React you choose your router and tools.  
हिंदी: React सिर्फ UI library है, बाकी चीज़ें आप खुद चुनते हो।  
Source: `01-basics/01-what-is-react.md`

**Q2. What is the Virtual DOM and why use it?**  
A: A lightweight JS object tree mirroring the real DOM. React compares new and old trees and applies only the minimal changes, since real DOM work is expensive. It is not faster than hand-tuned DOM code; the gain is the declarative model plus batching.  
हिंदी: Virtual DOM सिर्फ बदलाव ढूँढकर असली DOM में कम काम करवाता है।  
Source: `01-basics/04-virtual-dom.md, 05-virtual-dom-vs-real-dom.md`

**Q3. What is reconciliation and how does diffing work?**  
A: Comparing the new Virtual DOM with the previous one. Two heuristics give O(n): different element types give different trees, and `key` identifies stable list items. Same type updates props only.  
हिंदी: अलग type हो तो पूरा subtree बदलता है, वही type हो तो सिर्फ props।  
Source: `01-basics/04-virtual-dom.md`

**Q4. How does JSX work and how does it differ from HTML?**  
A: JSX compiles (via Babel) to `React.createElement()` calls that produce plain objects. Differences: `className`, `htmlFor`, self-closing tags, `{}` for expressions only (no `if`/`for` statements), camelCase events, `style` as an object. With the React 17+ transform no manual `React` import is needed.  
हिंदी: JSX असल में function call है, इसलिए `{}` में सिर्फ expressions चलते हैं।  
Source: `01-basics/07-jsx.md`

**Q5. Functional vs class components: what still needs a class?**  
A: Function components use Hooks and have no `this`; they are the recommended default. Error Boundaries (`getDerivedStateFromError`, `componentDidCatch`) still require a class as of React 18/19. Classes are not being removed.  
हिंदी: सिर्फ Error Boundary के लिए अब class चाहिए।  
Source: `01-basics/13-functional-vs-class-components.md`

**Q6. What is hydration?**  
A: React attaches event handlers and sets up its tree on HTML already rendered by the server. The server gives a fast first paint; hydration then makes it interactive.  
हिंदी: Server का HTML पहले दिखता है, फिर hydration उसे interactive बनाता है।  
Source: `01-basics/04-virtual-dom.md`


## 2. Props, state, rendering, forms

**Q7. State vs props?**  
A: Props come from the parent and are read-only; state is owned by the component and changed via its setter. Both trigger a re-render when they change. A child changes parent state only through a callback prop: data down, events up.  
हिंदी: Props पढ़ने के लिए, state बदलने के लिए।  
Source: `01-basics/21-state-vs-props.md`

**Q8. Why does `setCount(count + 1)` three times give 1, and how do you fix it?**  
A: All three calls use the same render's snapshot (`count = 0`) and are batched. Use the updater form `setCount(c => c + 1)` to get 3. Lazy init: `useState(() => expensive())` runs only on the first render.  
हिंदी: Updater form हमेशा ताज़ा value देता है।  
Source: `01-basics/20-usestate.md`

```jsx
setCount((c) => c + 1); // three calls => +3 in one render
```

**Q9. Why are keys important, and why not use the index?**  
A: Keys let React match old and new items so it reorders/removes the right nodes and keeps state with the right item. Index is position, not identity: insert, remove or sort and state and DOM get mixed. Keys must be unique among siblings and stable; changing a key remounts the component (a reset trick). `key` is not available as `props.key`.  
हिंदी: Key पहचान है, position नहीं; stable id इस्तेमाल करो।  
Source: `01-basics/25-why-key-prop-is-important.md`

**Q10. Controlled vs uncontrolled components?**  
A: Controlled: value from state via `value` + `onChange`; React is the source of truth (validation, formatting, reset). Uncontrolled: DOM keeps the value, read with a ref or `FormData`, initial via `defaultValue`. `<input type="file">` is always uncontrolled. Reset: controlled sets state; uncontrolled uses `form.reset()` or a new `key`.  
हिंदी: Live validation चाहिए तो controlled, सरल form में uncontrolled।  
Source: `01-basics/29-controlled-vs-uncontrolled-components.md`

**Q11. Does a child re-render when its parent re-renders?**  
A: Yes, by default, even with the same props. It stops only with `React.memo` and shallow-equal props. A component re-renders on its own state change, a parent render, or a consumed context change.  
हिंदी: Parent दोबारा चला तो child भी चलता है, जब तक memo न हो।  
Source: `01-basics/21-state-vs-props.md, 06-performance/121-react-performance-problems.md`

**Q12. How does React handle events (SyntheticEvent)?**  
A: One listener per event type on the root container (event delegation) with a cross-browser SyntheticEvent wrapper (`e.nativeEvent` for the native one). Pooling was removed in React 17. `e.target` is the deepest element, `e.currentTarget` is where the handler is attached. React `onChange` fires on every keystroke.  
हिंदी: React एक ही जगह सारे events सुनता है।  
Source: `01-basics/27-synthetic-events.md`


## 3. Hooks

**Q13. What are the Rules of Hooks and why?**  
A: Call hooks at top level, in the same order every render, only from components or custom hooks. React matches hooks by call position in a list, so a skipped hook shifts the rest into wrong slots ("Rendered more hooks than previous render").  
हिंदी: क्रम बदला तो hooks गलत slot पढ़ते हैं।  
Source: `02-hooks/57-rules-of-hooks-why-these-rules.md`

```jsx
if (on) { const [x] = useState('hello'); } // BAD: conditional hook
```

**Q14. Explain the three forms of the useEffect dependency array.**  
A: No array: every render. `[]`: once after mount. `[a, b]`: when a dep changes (compared with `Object.is`, so new objects or functions each render re-run it). List everything the effect reads.  
हिंदी: तीन रूप: हर बार, एक बार, dep बदलने पर।  
Source: `02-hooks/36-useeffect.md, 37-useeffect-dependency-array.md`

**Q15. What is the cleanup function and when does it run?**  
A: The function returned from an effect. It runs before the next effect and on unmount. Use it for timers, listeners, sockets, `controller.abort()`. It sees its own render's values.  
हिंदी: Cleanup के बिना memory leak और bugs होते हैं।  
Source: `02-hooks/38-useeffect-cleanup-function.md`

```jsx
useEffect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id);
}, []);
```

**Q16. How do you avoid race conditions when fetching in an effect?**  
A: Create an `AbortController`, pass `signal` to `fetch`, abort in cleanup; or use an `ignore` flag set in cleanup. Never make the effect callback itself `async`.  
हिंदी: पुराना request abort करो ताकि पुराना data state न बदले।  
Source: `02-hooks/36-useeffect.md`

**Q17. useRef vs useState?**  
A: State is for values shown on screen and re-renders on change; a ref is a mutable box (DOM node, timer id, previous or latest value) that never re-renders. Do not read or write refs during render.  
हिंदी: दिखने वाला data state में, छुपा data ref में।  
Source: `02-hooks/41-useref-vs-usestate.md`

**Q18. useMemo vs useCallback vs React.memo?**  
A: `useMemo` caches a value, `useCallback` caches a function, `React.memo` skips a component when props are shallow-equal. They work together: stable props from the first two let `memo` skip. They have overhead, so measure first.  
हिंदी: तीनों मिलकर stable references से re-render रोकते हैं।  
Source: `02-hooks/49-usememo-vs-usecallback.md, 03-intermediate/58-react-memo.md`

**Q19. useReducer vs useState?**  
A: `useState` for simple values; `useReducer` for related state with rules, using a pure reducer and stable `dispatch`. Reducers must not mutate state (same reference means no re-render) or run side effects. The choice is about clarity and testability, not speed.  
हिंदी: जटिल transitions के लिए `useReducer`।  
Source: `02-hooks/46-usereducer-vs-usestate.md`

**Q20. useEffect vs useLayoutEffect?**  
A: `useEffect` runs after paint (non-blocking); `useLayoutEffect` after DOM update but before paint (blocking), for measuring layout and preventing flicker. It does not run on the server, so use it in Client Components in Next.js.  
हिंदी: Default `useEffect`, flicker रोकने को `useLayoutEffect`।  
Source: `02-hooks/50-uselayouteffect-vs-useeffect.md`

**Q21. What are custom hooks and do they share state?**  
A: `use...` functions that package reusable stateful logic. Each call gets its own isolated state: hooks share logic, not data. To share state use Context or a store.  
हिंदी: Logic साझा होता है, state नहीं।  
Source: `02-hooks/55-custom-hooks.md`


## 4. Performance and patterns

**Q22. Why shouldn't you memoize everything, and what should you try first?**  
A: Each memo costs comparisons and memory and risks stale closures. Try first: move state down (colocation), lift content and pass `children`, then reduce work (paginate, virtualize). Measure with the Profiler on a production build.  
हिंदी: पहले measure करो, फिर optimize।  
Source: `06-performance/125-when-not-to-optimize.md`

**Q23. Why does `React.memo` fail with inline objects or functions?**  
A: `Object.is` compares references and each render creates a new object or function, so props always look changed. Fix with `useMemo`/`useCallback` or move constants outside. `memo` cannot block state or context re-renders.  
हिंदी: Inline object हर बार नया reference है।  
Source: `03-intermediate/58-react-memo.md`

**Q24. What is list virtualization?**  
A: Render only visible rows plus an overscan buffer (react-window). Trade-offs: Ctrl+F cannot see off-screen rows, accessibility needs care, variable heights need measuring.  
हिंदी: सिर्फ दिखने वाली rows बनती हैं।  
Source: `06-performance/127-virtualization-react-window.md`

**Q25. How do you split code with React.lazy and Suspense?**  
A: `lazy(() => import('./X'))` loads on demand; the nearest `<Suspense fallback>` shows while loading. The import must provide a default export. Define `lazy` at module scope. A static import elsewhere keeps the module in the main bundle.  
हिंदी: `lazy` को component के बाहर बनाओ।  
Source: `03-intermediate/69-suspense-and-lazy-loading.md, 70-code-splitting-in-react.md`

**Q26. Compare composition, HOC, render props and custom hooks.**  
A: Composition (`children` and slots) is the default. HOC wraps a component (good for route guards). Render props pass a function that returns UI. Custom hooks reuse stateful logic without extra tree layers and have mostly replaced the other two.  
हिंदी: आज ज़्यादातर काम custom hooks और composition से।  
Source: `03-intermediate/66-hoc-vs-custom-hooks.md`

**Q27. What are compound components?**  
A: A root plus parts sharing state through context, composed freely by the caller (`Toggle.On`, `Toggle.Button`). Prefer context to `cloneElement` and throw if used outside the root.  
हिंदी: Parts आपस में context से बात करते हैं।  
Source: `07-advanced/143-compound-components-pattern.md`

**Q28. What are portals and Error Boundaries?**  
A: `createPortal` renders into another DOM node but events bubble through the React tree. Error Boundaries (class) catch render and lifecycle errors, not event handler or async errors. In Next.js `error.js` is the per-segment boundary.  
हिंदी: Portal DOM में बाहर, React tree में अंदर।  
Source: `03-intermediate/67-react-portals.md, 68-error-boundaries.md`


## 5. State management and data fetching

**Q29. Context vs props drilling: when to use Context?**  
A: Context is good for slow-changing app-wide values (theme, locale, user). Every consumer re-renders when the value changes (even `memo` cannot stop it), so memoize the value and split contexts; use a store for fast-changing state. Try composition first.  
हिंदी: तेज़ बदलने वाली state के लिए Context ठीक नहीं।  
Source: `02-hooks/44-context-api-vs-props-drilling.md`

**Q30. What are Redux's core principles?**  
A: One store, read-only state changed only by dispatching actions, pure reducers. Mutating state keeps the same reference, so `useSelector` misses the change.  
हिंदी: एक store, plain actions, pure reducers।  
Source: `04-state-management/94-redux-core-concepts.md`

```jsx
const counterSlice = createSlice({ name: 'counter', initialState: { value: 0 }, reducers: { increment(state) { state.value += 1; } } });
```

**Q31. What does Redux Toolkit add?**  
A: `createSlice` (reducer plus actions), `configureStore` (thunk, DevTools, dev checks), `createAsyncThunk` (pending/fulfilled/rejected), Immer for safe "mutation".  
हिंदी: RTK से boilerplate कम होता है।  
Source: `04-state-management/97-redux-toolkit-rtk-complete-guide.md`

**Q32. Zustand vs Redux?**  
A: Redux Toolkit: strict structure, DevTools and ecosystem, for larger teams. Zustand: minimal store, no Provider, selectors, built-in middleware (`persist`, `devtools`). Zustand `set` merges only top-level. Use RTK Query or TanStack Query for server data.  
हिंदी: छोटे app में Zustand, बड़ी टीम में Redux।  
Source: `04-state-management/102-zustand-vs-redux.md`

**Q33. How do you choose a state-management tool?**  
A: Classify the state: local UI, form, URL (shareable filters), server data, shared client state. Pick the tool by type, and do not store derived values separately.  
हिंदी: पहले state का प्रकार, फिर tool।  
Source: `04-state-management/105-when-to-use-which-state-manager.md`

**Q34. Why TanStack Query instead of `useEffect` + `fetch`?**  
A: It handles caching, dedupe, retries, background refetch, cancellation and keeps server state out of component state. `staleTime` (default 0) is freshness; `gcTime` (default 5 min) is how long unused data is kept. v5: `isPending` means no data yet, `cacheTime` became `gcTime`.  
हिंदी: Cache, retry और dedupe अपने आप।  
Source: `05-data-fetching/110-react-query-tanstack-query.md, 111-usequery-hook.md`

**Q35. What UI states should a data-driven component handle?**  
A: Loading, error (with retry), empty, success, refetching. Prefer one `status` over separate booleans to avoid impossible combinations; check `res.ok` because `fetch` does not reject on HTTP errors; use `finally` to clear loading.  
हिंदी: `fetch` 404 पर reject नहीं करता।  
Source: `05-data-fetching/109-loading-error-states.md`


## 6. React 18/19 and Server Components

**Q36. What is new in React 18?**  
A: Concurrent rendering (opt in via `createRoot`), automatic batching everywhere (opt out with `flushSync`), `useTransition`/`useDeferredValue`, Suspense with streaming SSR and selective hydration.  
हिंदी: `createRoot` से नई सुविधाएँ चालू होती हैं।  
Source: `07-advanced/136-react-18-new-features.md`

**Q37. What is new in React 19?**  
A: Actions (async functions in transitions), `use(resource)` (reads promise or context, can be conditional), `useOptimistic`, `ref` as a normal prop so `forwardRef` is no longer needed.  
हिंदी: `use` शर्त के अंदर भी चलता है।  
Source: `07-advanced/137-react-19-new-features.md`

**Q38. useTransition vs useDeferredValue?**  
A: `useTransition` wraps the state update and gives `isPending`; `useDeferredValue` wraps a value and returns a lagging copy. Neither is debouncing and neither reduces network calls.  
हिंदी: Transition update को, deferred value को लपेटता है।  
Source: `02-hooks/52-usetransition-hook.md, 53-usedeferredvalue-hook.md`

**Q39. SSR vs Server Components?**  
A: SSR renders HTML on the server but ships all component code and hydrates it. RSC run only on the server and never ship or hydrate. Most apps use both. The RSC Payload is the serialized tree streamed to the client.  
हिंदी: RSC का code browser तक जाता ही नहीं।  
Source: `07-advanced/138-server-components-rsc.md`

**Q40. What does the React Compiler do?**  
A: A build-time plugin that auto-memoizes components and hooks, so `useMemo`/`useCallback`/`memo` are mostly unnecessary. Code must follow the Rules of React; unsafe code is skipped.  
हिंदी: Compiler खुद memo लगाता है।  
Source: `07-advanced/142-react-compiler.md`


## 7. Next.js

**Q41. React vs Next.js, and when to choose each?**  
A: Next.js adds routing, rendering strategies, data fetching, API routes, optimization and deployment on top of React, and sends real HTML (better SEO). Plain React/Vite suits private dashboards and internal tools.  
हिंदी: Public SEO वाले app में Next.js।  
Source: `08-nextjs/167-nextjs-vs-react.md`

**Q42. App Router vs Pages Router?**  
A: App Router (`app/`): Server Components by default, nested layouts, `loading.js`/`error.js`, streaming, Server Actions, Route Handlers. Pages Router (`pages/`): `getServerSideProps`/`getStaticProps`. They can coexist but no URL in both.  
हिंदी: नए project में App Router।  
Source: `08-nextjs/168-app-router-vs-pages-router.md`

**Q43. Server vs Client Components and what does `'use client'` do?**  
A: Server Components render on the server only, can be async, no client JS, but no state, effects or handlers. `'use client'` marks a boundary: the file and its imports go to the client bundle; they are still pre-rendered on the server then hydrated. A client file cannot import a Server Component but can receive one as `children`. Props crossing the boundary must be serializable.  
हिंदी: `'use client'` का मतलब सिर्फ browser नहीं।  
Source: `08-nextjs/170-server-components-in-nextjs.md, 171-client-components-in-nextjs.md`

**Q44. SSR vs SSG vs ISR vs CSR?**  
A: SSR: per request (fresh, personalised, slower). SSG: once at build (fastest). ISR: static plus background refresh via `revalidate` or on-demand. CSR: browser fetch (private pages). In the App Router: static by default, dynamic APIs make SSR.  
हिंदी: ज़रूरत के हिसाब से हर page का तरीका चुनो।  
Source: `08-nextjs/175-ssr-vs-ssg-vs-isr-vs-csr.md`

**Q45. Explain Next.js caching layers and the 14 to 15 change.**  
A: Request Memoization, Data Cache, Full Route Cache, Router Cache. Control with `revalidate`, `revalidateTag`/`revalidatePath`, `no-store`. Version-dependent: Next.js 14 cached `fetch` and GET handlers by default; Next.js 15 does not.  
हिंदी: Version के हिसाब से default अलग है।  
Source: `08-nextjs/190-nextjs-caching-strategies.md`

**Q46. What are Server Actions and are they secure?**  
A: `'use server'` async functions callable from forms or handlers. They are public endpoints, so authenticate, authorize and validate inside. Use for UI mutations; Route Handlers for external clients and webhooks.  
हिंदी: Server Action public endpoint है, जाँच ज़रूरी है।  
Source: `08-nextjs/184-server-actions-in-nextjs.md`

**Q47. What does Middleware do?**  
A: Runs before a route (Edge by default): redirect, rewrite, headers, cookies. Limit with `matcher`. It is only a first filter; real authorization belongs in the data layer. Version-dependent: renamed `proxy` in very recent versions.  
हिंदी: Middleware सिर्फ पहला filter है।  
Source: `08-nextjs/177-middleware-in-nextjs.md`

```jsx
export const config = { matcher: ['/orders/:path*', '/profile/:path*'] };
```

**Q48. How do loading, error and not-found files work?**  
A: `loading.js` wraps the page in Suspense; `error.js` is a Client Component error boundary with `reset()` (cannot catch its sibling layout's errors); `notFound()` shows `not-found.js`.  
हिंदी: तीनों के लिए अलग special files।  
Source: `08-nextjs/181-nextjs-loading-error-pages.md`

**Q49. How do environment variables work?**  
A: No prefix = server only; `NEXT_PUBLIC_` is inlined into browser JS at build time, so changing it needs a rebuild. Never put secrets in public variables.  
हिंदी: `NEXT_PUBLIC_` सबको दिखता है।  
Source: `08-nextjs/189-nextjs-environment-variables.md`

```jsx
console.log(process.env.API_KEY); // undefined in the browser: no NEXT_PUBLIC_ prefix
```

**Q50. How do you improve Next.js performance and SEO?**  
A: Core Web Vitals (LCP under 2.5 s, INP under 200 ms, CLS under 0.1); Server Components, small client leaves, parallel fetch, Suspense streaming, `next/image`, `next/font`, `next/script`; `metadata`/`generateMetadata` for SEO tags. Avoid dynamic APIs in the root layout.  
हिंदी: पहले measure, फिर JS घटाओ।  
Source: `08-nextjs/187-nextjs-performance.md, 180-nextjs-metadata-seo.md`
