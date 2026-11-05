# Tricky Interview Questions (collected from the notes)

Each item: the trap, the short answer, a Hindi hint, and the note it came from (paths under `react-next-js/`). Version-dependent answers are flagged.

## Basics (01-basics)

**1. Renders and StrictMode**  
**Q:** How many times does a component log on mount in dev?  
**A:** Mount once plus every state change; in React 18 StrictMode (dev) the initial render runs twice. Production renders once.  
हिंदी: Dev में StrictMode पहला render दो बार चलाता है, production में एक बार। (from `01-basics/01-what-is-react.md`)

**2. Batching in one handler**  
**Q:** Three `setState` calls in one handler: how many renders?  
**A:** One render; updates are batched (React 18 batches even across async boundaries).  
हिंदी: एक handler की सारी updates मिलकर एक ही render करती हैं। (from `01-basics/04-virtual-dom.md`)

**3. Same type, same position**  
**Q:** Toggle between two `<input>` branches: is typed text kept?  
**A:** Same type at the same position reuses the DOM node, so text stays; a different `key` makes React remount and the text is lost.  
हिंदी: Type और position वही हो तो node दोबारा इस्तेमाल होता है, key बदली तो नया बनता है। (from `01-basics/05-virtual-dom-vs-real-dom.md`)

**4. `0 &&` in JSX**  
**Q:** `{items.length && <p>..</p>}` with an empty array?  
**A:** Renders the number `0` on screen. Fix: `items.length > 0 && ...`.

```jsx
{items.length > 0 && <p>Items: {items.length}</p>}
```

हिंदी: `0 && ...` स्क्रीन पर 0 दिखाता है, इसलिए `> 0` लिखो। (from `01-basics/07-jsx.md`)

**5. What JSX renders**  
**Q:** What do `null`, `undefined`, `false`, `true`, `''`, `0`, `NaN` render?  
**A:** Nothing for null/undefined/booleans/empty string; numbers render, including `0` and `NaN`.  
हिंदी: null, undefined और boolean कुछ नहीं दिखाते, पर 0 और NaN दिखते हैं। (from `01-basics/08-jsx-rules-best-practices.md`)

**6. Function vs class closures**  
**Q:** Click, then change the selected user within 3 s: which name shows?  
**A:** Function component shows the click-time props (closure); a class reads `this.props` later and sees the new one.  
हिंदी: Function component click के समय की value पकड़ता है, class बाद की। (from `01-basics/13-functional-vs-class-components.md`)

**7. Three `setCount(count + 1)`**  
**Q:** What is count after one click?  
**A:** 1, not 3: each uses the same render's snapshot. Use `setCount(c => c + 1)` for 3.

```jsx
setCount(count + 1); setCount(count + 1); setCount(count + 1); // 1
setCount((c) => c + 1); // x3 => 3
```

हिंदी: तीनों call एक ही पुरानी count देखती हैं, इसलिए नतीजा 1 आता है। (from `01-basics/20-usestate.md`)

**8. Prop copied into state**  
**Q:** Parent changes `initialName`; does the child's state follow?  
**A:** No; `useState` ignores its argument after mount. Use the prop directly or change the `key`.  
हिंदी: State सिर्फ पहली बार prop से भरती है, बाद में नहीं बदलती। (from `01-basics/21-state-vs-props.md`)

**9. Element identity skips children**  
**Q:** Does `<Expensive />` re-render when a sibling's state changes?  
**A:** No: the same element object passed as `children` lets React skip the subtree.  
हिंदी: वही element object मिले तो React subtree छोड़ देता है। (from `01-basics/22-rendering-how-react-renders.md`)

**10. Index as key**  
**Q:** Delete the first item; what happens to edited inputs?  
**A:** State and DOM stay with the position, so the wrong row keeps the typed text. Use stable ids.  
हिंदी: Index key से typed text गलत row के साथ चला जाता है। (from `01-basics/25-why-key-prop-is-important.md`)

**11. `stopPropagation`**  
**Q:** Button handler `+10` with `stopPropagation`, div handler `+1`: result?  
**A:** 10; the div's handler does not run. Without it, 11.  
हिंदी: stopPropagation से parent का handler नहीं चलता। (from `01-basics/26-event-handling.md`)

**12. Uncontrolled to controlled**  
**Q:** `value={text}` where `text` starts `undefined`?  
**A:** Works but warns: starts uncontrolled, becomes controlled. Initialize with `''`.  
हिंदी: शुरू में `''` रखो ताकि input बीच में controlled न बने। (from `01-basics/29-controlled-vs-uncontrolled-components.md`)

## Hooks (02-hooks)

**13. Early return before a hook**  
**Q:** `if (!id) return null;` before `useEffect`?  
**A:** Violates Rules of Hooks: "Rendered more hooks than previous render". Return after all hooks.  
हिंदी: Hook से पहले return मत करो। (from `02-hooks/34-what-are-hooks.md`)

**14. Mixed updater queue**  
**Q:** `+1, +1, c=>c+1, set(count+5), c=>c+1` from 0?  
**A:** 6 in one render: plain values replace, updaters use the queue result.  
हिंदी: Plain value state बदल देती है, updater पिछला नतीजा लेता है। (from `02-hooks/35-usestate-deep-dive.md`)

**15. Stale interval**  
**Q:** `setCount(count + 1)` in `setInterval` with `[]`?  
**A:** Shows 1 forever (closure holds count = 0). Fix: `setCount(c => c + 1)`.

```jsx
useEffect(() => {
  const id = setInterval(() => setCount((c) => c + 1), 1000);
  return () => clearInterval(id);
}, []);
```

हिंदी: Closure में count = 0 अटका रहता है। (from `02-hooks/36-useeffect.md`)

**16. Object dependency**  
**Q:** `setUser({ name: 'A' })` again: does the effect re-run?  
**A:** Yes: new reference. `setUser(user)` (same reference) bails out.  
हिंदी: नया object बना तो dependency बदली मानी जाती है। (from `02-hooks/37-useeffect-dependency-array.md`)

**17. Cleanup logs old value**  
**Q:** Click twice: log order?  
**A:** `effect 0`, then `cleanup 0`, `effect 1`, then `cleanup 1`, `effect 2`: cleanup sees its own render's `n`.  
हिंदी: Cleanup अपने पुराने render की value देखता है। (from `02-hooks/38-useeffect-cleanup-function.md`)

**18. Interval logs 0**  
**Q:** Log `count` inside an interval set in a `[]` effect?  
**A:** Logs 0 forever (a class's `this.state` would be fresh). Add `count` to deps or use a ref.  
हिंदी: Hooks में closure पुरानी value रखता है, class में `this` बदलता है। (from `02-hooks/39-useeffect-vs-componentdidmount.md`)

**19. Ref vs state in setTimeout**  
**Q:** 3 s alert, increment 5 times meanwhile?  
**A:** State shows 0 (stale), ref shows 5 (always latest).  
हिंदी: Ref में हमेशा ताज़ा value मिलती है। (from `02-hooks/40-useref.md`)

**20. Context re-renders**  
**Q:** 3 clicks changing the Provider value: Child logs?  
**A:** 4 times (mount + 3); all consumers re-render on value change.  
हिंदी: Value बदलने पर हर consumer दोबारा render होता है। (from `02-hooks/42-usecontext.md`)

**21. memo cannot block context**  
**Q:** `React.memo` child uses `useContext`: skipped on context change?  
**A:** No: it still re-renders; memo only stops prop-driven renders.  
हिंदी: Context update को `memo` नहीं रोकता। (from `02-hooks/43-context-api-complete-guide.md`)

**22. useReducer init**  
**Q:** Third argument of `useReducer`?  
**A:** A lazy initializer called once as `init(initialArg)`.  
हिंदी: तीसरा argument शुरुआती state बनाने वाला function है। (from `02-hooks/45-usereducer.md`)

**23. Mutating reducer**  
**Q:** Reducer does `state.count += 1; return state`?  
**A:** UI stays 0: same reference, `Object.is` bails out; StrictMode runs reducers twice.  
हिंदी: Reducer में mutate करने से UI नहीं बदलता। (from `02-hooks/46-usereducer-vs-usestate.md`)

**24. Two useMemo calls**  
**Q:** `value === sameValue` for identical memos?  
**A:** `false`: separate calls give separate objects.  
हिंदी: दो अलग `useMemo` के objects अलग होते हैं। (from `02-hooks/47-usememo.md`)

**25. useCallback with memo**  
**Q:** Typing in an input: does `memo(Counter)` re-render?  
**A:** No: `useCallback(..., [])` keeps the prop reference stable.  
हिंदी: Reference स्थिर हो तो memo child नहीं चलता। (from `02-hooks/48-usecallback.md`)

**26. Which child re-renders**  
**Q:** One child gets memoized props, one inline props?  
**A:** Only the inline-props child re-renders.  
हिंदी: Inline object और function हर बार नए बनते हैं। (from `02-hooks/49-usememo-vs-usecallback.md`)

**27. Effect ordering**  
**Q:** Mount and click log order with layout effect and effect?  
**A:** Mount: render, layout effect, effect. Click: render, layout cleanup, layout effect, effect cleanup, effect.  
हिंदी: Layout effect paint से पहले, normal effect बाद में। (from `02-hooks/50-uselayouteffect-vs-useeffect.md`)

**28. isPending in handler**  
**Q:** `console.log(isPending)` right after `startTransition`?  
**A:** `false`: it is a snapshot of the current render.  
हिंदी: `isPending` handler में पुरानी value है। (from `02-hooks/52-usetransition-hook.md`)

**29. Imperative handle shape**  
**Q:** What is `r.current` in the parent?  
**A:** The custom object: `focus` is a function, `value` is `undefined`, not an `HTMLInputElement`.  
हिंदी: Parent को सिर्फ चुने हुए methods मिलते हैं। (from `02-hooks/54-useimperativehandle-hook.md`)

**30. Conditional hook**  
**Q:** `if (on) useState(...)`: what breaks?  
**A:** React throws "Rendered more hooks than during the previous render" (wording version-dependent).  
हिंदी: Hook का क्रम बदला तो React slot नहीं मिला पाता। (from `02-hooks/57-rules-of-hooks-why-these-rules.md`)

## Intermediate and state management (03, 04)

**31. Batched class setState**  
**Q:** Two `this.setState({count: this.state.count + 1})`?  
**A:** Final count is 1; use the functional form.  
हिंदी: दोनों call `0` पढ़ती हैं, इसलिए नतीजा 1। (from `03-intermediate/58-component-lifecycle-class.md`)

**32. memo with a new array**  
**Q:** `memo` child gets `items={['a','b','c']}` inline?  
**A:** Re-renders every time; move it outside or `useMemo`.  
हिंदी: हर render नया array बनता है। (from `03-intermediate/58-react-memo.md`)

**33. Children.count vs toArray**  
**Q:** `{false}{null}<span/>`?  
**A:** `count` is 3, `toArray` length is 1.  
हिंदी: `toArray` null और false हटा देता है। (from `03-intermediate/63-children-prop.md`)

**34. Portal event bubbling**  
**Q:** Click inside a portal: does the React parent's `onClick` fire?  
**A:** Yes: events follow the React tree, not the DOM tree.  
हिंदी: Portal का click React parent तक पहुँचता है। (from `03-intermediate/67-react-portals.md`)

**35. Error boundary and handlers**  
**Q:** Does an error boundary catch an `onClick` error?  
**A:** No: only render, lifecycle, constructors. Use try/catch for handlers and async code.  
हिंदी: Event handler के error boundary नहीं पकड़ती। (from `03-intermediate/68-error-boundaries.md`)

**36. lazy inside a component**  
**Q:** `lazy()` called during render?  
**A:** New component type each render: remounts and re-suspends. Define `lazy` at module level.  
हिंदी: `lazy` को component के बाहर बनाओ। (from `03-intermediate/69-suspense-and-lazy-loading.md`)

**37. Debounce inside render**  
**Q:** Debounce created in the component body?  
**A:** Does not work: each render makes a new timer closure, nothing cancels earlier timers. Use `useRef`/`useMemo`.  
हिंदी: हर render नया timer बनाता है। (from `03-intermediate/82-debounce-in-react.md`)

**38. Router params are strings**  
**Q:** `useParams()` gives `007`: `id === 7`?  
**A:** `false`; it is the string `"007"`. Convert with `Number(id)`.  
हिंदी: `useParams` हमेशा string देता है। (from `03-intermediate/86-usenavigate-and-useparams-and-uselocation.md`)

**39. Protected route on first render**  
**Q:** Logged-in user lands on `/login` after refresh?  
**A:** `user` is `null` until the session fetch finishes, so redirect fires first; add a loading state.  
हिंदी: Session आने तक loading दिखाओ। (from `03-intermediate/88-protected-routes.md`)

**40. State copy from props**  
**Q:** `useState(items.length)` after the prop changes?  
**A:** Stays old; derive `const total = items.length`.  
हिंदी: Derived value को state में मत रखो। (from `04-state-management/91-state-management-why-needed.md`)

**41. Mutated Redux state**  
**Q:** Reducer mutates and returns same object?  
**A:** `before === after`, so `useSelector` skips re-render.  
हिंदी: Mutation से reference नहीं बदलता। (from `04-state-management/94-redux-core-concepts.md`)

**42. Action type typo**  
**Q:** `'todos/ad'` instead of `'todos/add'`?  
**A:** No error, falls into `default`; state unchanged. Use action creators.  
हिंदी: गलत type चुपचाप ignore होता है। (from `04-state-management/95-redux-actions-and-reducers-and-store.md`)

**43. Reassigning Immer draft**  
**Q:** `state = { value: 99 }` in a slice reducer?  
**A:** Silent no-op; mutate `state.value = 99` or return a new object.  
हिंदी: `state` को दोबारा assign मत करो। (from `04-state-management/98-createslice-and-configurestore.md`)

**44. Zustand set merges shallowly**  
**Q:** `set({ user: { age: 20 } })` with existing `user.name`?  
**A:** Replaces `user` entirely (top-level merge only), so `name` is gone.  
हिंदी: Nested object पूरा बदल जाता है। (from `04-state-management/101-zustand-complete-guide.md`)

**45. Stored total drifts**  
**Q:** `items` updated but stored `total` not?  
**A:** Stale; compute `total` with a selector.  
हिंदी: Total को store में मत रखो। (from `04-state-management/105-when-to-use-which-state-manager.md`)

## Data fetching, performance (05, 06)

**46. Fetch in StrictMode**  
**Q:** Effect without cleanup in dev?  
**A:** Fetch runs twice (mount, unmount, mount); production once. Add cleanup or use a cache library.  
हिंदी: Dev में effect दो बार चलता है। (from `05-data-fetching/107-useeffect-fetch-basic.md`)

**47. Loading forever**  
**Q:** `r.json()` throws on a 500 HTML body?  
**A:** `setLoading(false)` never runs; use try/catch/finally.  
हिंदी: Error पर भी loading बंद करो। (from `05-data-fetching/109-loading-error-states.md`)

**48. Query dedupe**  
**Q:** Three components, same `queryKey`: fetch count?  
**A:** Once; shared in-flight request and cache.  
हिंदी: Same key का एक ही request जाता है। (from `05-data-fetching/110-react-query-tanstack-query.md`)

**49. v5 isLoading vs isPending**  
**Q:** Disabled query: `isLoading`?  
**A:** `false`; `isPending` is `true` (no data yet). `isLoading = isFetching && isPending` (v5).  
हिंदी: v5 में `isPending` का मतलब है अभी data नहीं। (from `05-data-fetching/111-usequery-hook.md`)

**50. staleTime and gcTime**  
**Q:** `staleTime` 5 s, remount at 3 s and 8 s?  
**A:** 2 requests total: at 3 s fresh cache; at 8 s stale data shows while refetching.  
हिंदी: Fresh में cache, stale में background refetch। (from `05-data-fetching/113-react-query-caching.md`)

**51. Optimistic update flip-back**  
**Q:** Optimistic update while a refetch is in flight?  
**A:** Old server data overwrites it; cancel queries first and restore on error.  
हिंदी: पहले in-flight fetch रोकना ज़रूरी है। (from `05-data-fetching/114-optimistic-updates.md`)

**52. memo with inline handler**  
**Q:** `memo` child with an inline `onClick`?  
**A:** Re-renders every parent render (mount + 3 clicks = 4); `useCallback` fixes it.  
हिंदी: Inline function नया reference है। (from `06-performance/121-react-performance-problems.md`)

**53. Lazy hero image**  
**Q:** `loading="lazy"` on the hero image?  
**A:** Hurts LCP; use eager with `fetchpriority="high"`, and set width/height to avoid layout shift.  
हिंदी: ऊपर की image lazy मत करो। (from `06-performance/128-image-optimization-in-react.md`)

**54. Nested Suspense**  
**Q:** Outer child suspends: what shows?  
**A:** The outer fallback replaces the whole subtree, including the inner boundary.  
हिंदी: बाहरी fallback पूरा subtree ढक देता है। (from `06-performance/132-suspense-for-data-fetching.md`)

## Advanced (07)

**55. flushSync**  
**Q:** `flushSync` between two state updates?  
**A:** Flushes all pending updates at once; escape hatch from batching, use rarely.  
हिंदी: `flushSync` batching तोड़ता है। (from `07-advanced/136-react-18-new-features.md`)

**56. `use` in conditionals**  
**Q:** Can `use(promise)` be called inside `if`?  
**A:** Yes, unlike hooks; but only inside a component or hook.  
हिंदी: `use` शर्त के अंदर चल सकता है। (from `07-advanced/137-react-19-new-features.md`)

**57. Server Component inside client**  
**Q:** Client Component rendering a Server Component?  
**A:** Cannot import it, but can receive it as `children`.  
हिंदी: `children` के रूप में Server Component दिया जा सकता है। (from `07-advanced/138-server-components-rsc.md`)

**58. Function props across the boundary**  
**Q:** Inline function from Server to Client Component?  
**A:** Error: props must be serializable; use a Server Action instead.  
हिंदी: Function props server से client नहीं जाते। (from `07-advanced/139-client-vs-server-components.md`)

**59. One Suspense for two children**  
**Q:** `Fast` and `Slow` in one boundary?  
**A:** Both appear together after Slow; use separate boundaries.  
हिंदी: हर हिस्से को अलग Suspense दो। (from `07-advanced/140-streaming-ssr.md`)

**60. Compiler memoization**  
**Q:** Does `<Child value="fixed" />` re-render with the compiler?  
**A:** No: cached because inputs never change; without it `renders` increases.  
हिंदी: Compiler खुद memo लगाता है। (from `07-advanced/142-react-compiler.md`)

**61. Fragments in compound components**  
**Q:** `cloneElement` over children with a Fragment?  
**A:** The Fragment receives the props; `Children.map` does not flatten it.  
हिंदी: Fragment के अंदर के parts काम नहीं करते। (from `07-advanced/143-compound-components-pattern.md`)

**62. `user.click` not awaited**  
**Q:** Test asserts right after `user.click(...)`?  
**A:** Flaky/fails; `await` it (User Event v14 is async).  
हिंदी: `await user.click` लिखो। (from `07-advanced/152-testing-in-react-jest-rtl.md`)

## Next.js (08)

**63. `useState` in App Router**  
**Q:** `useState` in a plain file?  
**A:** Server Components by default, so it errors until `'use client'`.  
हिंदी: `'use client'` जोड़ो। (from `08-nextjs/167-nextjs-vs-react.md`)

**64. Same URL in app and pages**  
**Q:** Route in both routers?  
**A:** Build/dev error for conflicting routes; migrate one route at a time.  
हिंदी: एक URL दोनों में नहीं। (from `08-nextjs/168-app-router-vs-pages-router.md`)

**65. Where do logs print?**  
**Q:** `console.log` in a Server Component?  
**A:** Server terminal only; Client Components log on the server (pre-render) and in the browser (hydration).  
हिंदी: Server Component का log terminal में दिखता है। (from `08-nextjs/170-server-components-in-nextjs.md`)

**66. Shared module variable**  
**Q:** `let hits` at module level in `getServerSideProps`?  
**A:** Shared across users (same Node process): A sees 1, B sees 2.  
हिंदी: Module variable सब users में साझा है। (from `08-nextjs/172-getserversideprops-pages.md`)

**67. ISR timing**  
**Q:** `revalidate: 10`, visit at 15 s?  
**A:** Stale page served immediately and regeneration starts; the next visitor gets the new one.  
हिंदी: पहला visitor पुराना पेज देखता है। (from `08-nextjs/173-getstaticprops-pages.md`)

**68. `cookies()` makes SSR**  
**Q:** `revalidate = 60` plus `cookies()`?  
**A:** Dynamic (SSR); revalidate has no effect for that HTML.  
हिंदी: `cookies()` route को dynamic बना देता है। (from `08-nextjs/175-ssr-vs-ssg-vs-isr-vs-csr.md`)

**69. Middleware redirect loop**  
**Q:** Redirect `/login` to `/login`?  
**A:** Infinite loop (ERR_TOO_MANY_REDIRECTS); exclude the target path.  
हिंदी: Target path को बाहर रखो। (from `08-nextjs/177-middleware-in-nextjs.md`)

**70. Remote image without size**  
**Q:** `<Image src="https://cdn..."/>` without width/height?  
**A:** Error; also needs the host in `images.remotePatterns`.  
हिंदी: Remote image को size और allowlist चाहिए। (from `08-nextjs/178-nextjs-image-optimization.md`)

**71. font-family string**  
**Q:** `fontFamily: 'Inter'` after `next/font`?  
**A:** Not used: hashed family name; use `inter.className`.  
हिंदी: `inter.className` इस्तेमाल करो। (from `08-nextjs/179-nextjs-font-optimization.md`)

**72. `error.js` and layout**  
**Q:** Does `app/shop/error.jsx` catch its own layout's error?  
**A:** No: it wraps the page, not the layout beside it; bubbles up or to `global-error`.  
हिंदी: Layout का error ऊपर वाली boundary पकड़ती है। (from `08-nextjs/181-nextjs-loading-error-pages.md`)

**73. Intercepting route on refresh**  
**Q:** Refresh at `/photo/5` opened as a modal?  
**A:** The full page shows; interception is soft-navigation only.  
हिंदी: Refresh पर modal नहीं, पूरा पेज। (from `08-nextjs/183-nextjs-intercepting-routes.md`)

**74. Prisma too many connections**  
**Q:** Dev hot reload creates clients?  
**A:** Each reload opens a pool; keep a singleton on `globalThis`.  
हिंदी: एक ही client रखो। (from `08-nextjs/185-nextjs-prisma-postgresql.md`)

**75. `role` undefined in session**  
**Q:** Why is `session.user.role` missing?  
**A:** The `jwt` callback never copied it to the token.  
हिंदी: पहले `jwt`, फिर `session` callback। (from `08-nextjs/186-nextjs-authentication-nextauth.md`)

**76. `cookies()` in root layout**  
**Q:** Static pages turn slow?  
**A:** Dynamic API in root layout opts every route out of static rendering.  
हिंदी: Root layout में dynamic API मत डालो। (from `08-nextjs/187-nextjs-performance.md`)

**77. Caching defaults 14 vs 15**  
**Q:** `fetch` with no options?  
**A:** Version-dependent: cached in Next.js 14, not cached in 15; set caching explicitly.  
हिंदी: 14 और 15 के defaults अलग हैं। (from `08-nextjs/190-nextjs-caching-strategies.md`)

