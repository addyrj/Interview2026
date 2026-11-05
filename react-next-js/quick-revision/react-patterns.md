# React Patterns Cheatsheet

Composition, HOC, render props, compound components, custom hooks, and state-management choices. Sources: `03-intermediate/`, `04-state-management/`, `07-advanced/`, plus custom hooks from `02-hooks/`.

---

# Part 1: Reuse and structure patterns

## Component composition (62)
- Build UI from parts: a container defines structure, the caller supplies content through `children` and named slot props.
- Replaces inheritance and long prop lists.
- Never define a component inside another component: it becomes a new type every render and remounts.

```jsx
function Card({ header, footer, children }) {
  return (
    <div>
      {header && <header>{header}</header>}
      <section>{children}</section>
      {footer && <footer>{footer}</footer>}
    </div>
  );
}
```

> हिंदी: Inheritance की जगह composition: `children` और slots से लचीले components बनाओ।

---

## The `children` prop (63)
- `children` is a normal prop: one element for one child, an array for many.
- `Children.count` counts `null` and `false` too; `Children.toArray` keeps only renderable children.

```jsx
// <Box>{false}{null}<span/></Box>
Children.count(children);        // 3
Children.toArray(children).length; // 1
```

> हिंदी: `children` कई हों तो array होता है, loop के लिए `Children.toArray` इस्तेमाल करो।

---

## Props drilling and its fixes (60, 61)
- Drilling passes data through middle components that never use it; it couples components and adds noise.
- Fixes: composition for layout, Context for shared values, a store for app-wide state.
- A non-memoized middle component re-renders `Leaf` even when its props did not change.

```jsx
// Fix by composition: pass the already built element down
<Layout sidebar={<Sidebar user={user} />} />
```

> हिंदी: बीच के components को बेकार props देने से बचो, composition या Context इस्तेमाल करो।

---

## Render props (64)
- A function prop: the owner calls it with its data and returns the UI it produces.
- Separates logic (owner) from presentation (caller). Custom hooks have mostly replaced it.
- A new inline function each render breaks `React.memo` on the owner.

```jsx
function Toggle({ render }) {
  const [on, setOn] = useState(false);
  return render({ on, toggle: () => setOn((v) => !v) });
}
// <Toggle render={({ on, toggle }) => <button onClick={toggle}>{on ? 'ON' : 'OFF'}</button>} />
```

> हिंदी: Logic एक जगह, UI बुलाने वाला तय करे: function prop से data दो।

---

## Higher-Order Component, HOC (65)
- A function that takes a component and returns an enhanced component.
- Always forward props, use `forwardRef` for refs, set `displayName`, create the enhanced component at module level.
- Still useful for route guards and wrapping third-party components.

```jsx
function withLoading(WrappedComponent) {
  function WithLoading({ isLoading, ...rest }) {
    if (isLoading) return <p>Loading your data...</p>;
    return <WrappedComponent {...rest} />;
  }
  WithLoading.displayName = `withLoading(${WrappedComponent.displayName || WrappedComponent.name})`;
  return WithLoading;
}
```
Trap: `<Wrapped {...props} user={x} />` lets the HOC value win; `user={x} {...props}` lets the caller win (later props override).

> हिंदी: HOC component को लपेटकर नया behaviour देता है, आज ज़्यादातर काम hooks से होता है।

---

## HOC vs custom hooks (66)
- HOC wraps a component and adds a layer to the tree; a custom hook is called inside a component and returns values.
- Prefer hooks for shared stateful logic; HOC for route guards or wrapping whole components. Error boundaries must still be classes.
- Both can combine: logic in a hook, an HOC that calls it and decides what to render.

```jsx
function useCounter() { const [n, setN] = useState(0); return [n, () => setN((c) => c + 1)]; }
// a and b from two useCounter() calls are independent: hooks share logic, not state
```

> हिंदी: Hook logic share करता है, state नहीं; हर call की अपनी state होती है।

---

## Custom hooks (55, 56)
- A `use...` function that packages reusable stateful logic with other hooks.
- Clean up effects, guard browser APIs for SSR, return stable references.

```jsx
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t); // cancel on change or unmount
  }, [value, delay]);
  return debounced;
}
```

> हिंदी: बार-बार लिखी जाने वाली stateful logic को `use` वाले function में निकाल दो।

---

## Compound components (143)
- A root plus parts that share state through context; the caller composes the parts freely.
- Prefer context over `cloneElement`, memoize the provider value, throw if a part is used outside the root.
- In Next.js put them in a `'use client'` file.

```jsx
const ToggleContext = createContext(null);
function Toggle({ children }) {
  const [on, setOn] = useState(false);
  return <ToggleContext.Provider value={{ on, toggle: () => setOn((o) => !o) }}>{children}</ToggleContext.Provider>;
}
function useToggle() {
  const ctx = useContext(ToggleContext);
  if (!ctx) throw new Error('Use Toggle parts inside <Toggle>');
  return ctx;
}
Toggle.On = ({ children }) => (useToggle().on ? children : null);
Toggle.Button = () => { const { on, toggle } = useToggle(); return <button onClick={toggle}>{on ? 'Off' : 'On'}</button>; };
```
Trap: `React.Children.map` does not flatten Fragments, so `cloneElement` props go to the Fragment, not the parts.

> हिंदी: `Tabs`, `Tabs.Panel` जैसे जुड़े हुए parts, जो context से आपस में बात करते हैं।

---

## Controlled components pattern (144)
- Controlled: parent owns state via `value` and `onChange`, so it can validate, reset, sync.
- Uncontrolled: component keeps its own state; simpler for small forms and file inputs.
- Never switch modes accidentally; initialize with a defined value.

```jsx
function Limited({ value, onChange }) {
  return <input value={value} onChange={(e) => e.target.value.length <= 3 && onChange(e.target.value)} />;
}
// the 4th character vanishes because state did not change
```

> हिंदी: Controlled में state parent के पास होती है, इसलिए नियम वही तय करता है।

---

## Provider pattern (145)
- A Provider holds state and shares it to descendants via context plus a custom hook.
- Memoize the value, split contexts by update frequency, throw when the Provider is missing.
- In Next.js, make Providers Client Components in `providers.jsx` and keep pages as server children.

```jsx
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  const value = useMemo(() => ({ theme, toggle: () => setTheme((t) => (t === 'light' ? 'dark' : 'light')) }), [theme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
```

> हिंदी: Provider एक बार ऊपर लगाओ और `useTheme` जैसे hook से कहीं भी पढ़ो।

---

## Container / Presentational (146)
- Container holds data and logic; presentational is a pure UI component.
- Today the container is usually a custom hook or a Server Component. Do not over-split.
- Passing fresh `items`/`onSelect` each render breaks `memo` on the view.

```jsx
function OrdersContainer() {
  const { orders, loading } = useOrders();      // logic
  return <OrdersView orders={orders} loading={loading} />; // pure UI
}
```

> हिंदी: Data वाला हिस्सा और दिखने वाला हिस्सा अलग रखो ताकि UI test करना आसान हो।

---

## Adapter pattern (147)
- Translates external data or library APIs into the clean shape components expect.
- Keep it pure, place it at the data boundary, adapt once (or `useMemo`) so object identity stays stable.

```jsx
const toRestaurant = (raw) => ({ id: raw.rid, name: raw.rest_name, rating: Number(raw.avg) });
```

> हिंदी: Backend का अजीब data एक adapter में बदलो, components को छूना न पड़े।

---

## Atomic design (148)
- UI as atoms, molecules, organisms, templates, pages; dependencies point downward only.
- Fetching lives in organisms and pages. Keep state low to avoid extra re-renders.

> हिंदी: छोटे हिस्सों से बड़ा UI बनाओ और state जितनी हो सके नीचे रखो।

---

## React.memo (58, 72)
- Skips re-render when props are shallow-equal (`Object.is`). Only stops parent-triggered renders, not state or context.
- Inline objects and functions defeat it; pair with `useMemo`/`useCallback` or move constants outside.

```jsx
const Row = React.memo(function Row({ item, onSelect }) { return <li onClick={() => onSelect(item.id)}>{item.name}</li>; });
```

> हिंदी: Props वही हों तभी `memo` re-render रोकता है, inline object हो तो नहीं।

---

## Portals and Error Boundaries (67, 68)
- `createPortal(children, domNode)` renders elsewhere in the DOM but stays in the React tree; events bubble to React parents.
- Create portals only in the browser (never during server rendering).
- Error boundary is a class (`getDerivedStateFromError`, `componentDidCatch`); it does not catch event handlers or async errors.

```jsx
createPortal(<Modal />, document.body);
```

> हिंदी: Modal `document.body` में दिखता है पर React tree में अपनी जगह ही रहता है।

---

# Part 2: State-management choices

## Why state management, lifting state (91, 92)
- Lift state to the nearest common parent; pass values and updaters down.
- Store each value once and derive the rest; `useState(items.length)` copies only the first value.
- Keep state as local as possible; put shareable filters in the URL.

```jsx
const total = items.length; // derive, do not store a copy
```

> हिंदी: Data एक ही जगह रखो, बाकी सब उसी से निकालो।

---

## Context for state (93)
- Nearest Provider wins; the default applies only when no Provider exists (a Provider with `value={undefined}` gives `undefined`).
- Every consumer re-renders on change, so keep values stable, split contexts, use a store for frequent updates.

> हिंदी: Context कम बदलने वाली value (theme, locale) के लिए ठीक है, तेज़ बदलाव के लिए नहीं।

---

## Redux core (94, 95, 96)
- One store, state changed only by dispatching plain actions, pure reducers.
- Mutating state hides the change (same reference), so `useSelector` skips the re-render.
- Typo in an action type fails silently; use action creators. Middleware runs in order on the way in and reverses on the way out.

```js
function reducer(state = { count: 0 }, action) {
  switch (action.type) {
    case 'inc': return { ...state, count: state.count + 1 };
    default: return state;
  }
}
```
Next.js: do not use a module-level singleton store on the server (per-request store).

> हिंदी: Redux में एक store, plain action और pure reducer; state कभी mutate मत करो।

---

## Redux Toolkit and thunks (97, 98, 99)
- `createSlice` gives reducer and actions (types `name/key`); `configureStore` adds thunk, DevTools, dev checks.
- Immer lets you "mutate" a draft; reassigning the `state` parameter does nothing.
- `createAsyncThunk` dispatches pending / fulfilled / rejected.

```js
const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: { increment(state) { state.value += 1; } },
});
const store = configureStore({ reducer: { counter: counterSlice.reducer } });
```

> हिंदी: RTK से boilerplate कम होता है और Immer की वजह से "mutation" वाला code सुरक्षित रहता है।

---

## RTK Query vs React Query (100, 110, 116)
- RTK Query: `createApi` endpoints, auto hooks, cache keyed by args, dedupes in-flight calls; needs both `api.reducer` and `api.middleware` in the store; refresh lists with `invalidatesTags`.
- TanStack Query: `queryKey` identifies cache, `staleTime` (default 0) vs `gcTime` (default 5 min). Version flag: in v5 `cacheTime` became `gcTime`, `isLoading` became `isPending` for "no data yet".
- Keep server data in these tools and client UI state elsewhere.

```jsx
const { data, isPending, isError } = useQuery({ queryKey: ['restaurants'], queryFn: fetchRestaurants });
```

> हिंदी: Server का data इन tools में, सिर्फ UI की state अलग रखो।

---

## Zustand (101, 102)
- `create()` gives a store hook with no Provider; selectors limit re-renders; `set` merges top-level only (nested objects are replaced).
- Selecting a new object or array each time re-renders on every change.
- `persist` middleware saves to localStorage (`partialize`, `version/migrate`).

```js
const useCounterStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

> हिंदी: Zustand छोटा और बिना Provider का है, selector से सिर्फ ज़रूरी हिस्सा सुनो।

---

## Jotai and Recoil (103, 104)
- Jotai: small `atom`s; derived atoms track dependencies and are cached; Provider optional.
- Recoil: atoms plus selectors inside `<RecoilRoot>`; each root has its own store. Version flag: Recoil is in maintenance mode, so prefer Jotai or Zustand for new projects.

```js
const countAtom = atom(0);
const doubleAtom = atom((get) => get(countAtom) * 2);
```

> हिंदी: नया project हो तो Recoil की जगह Jotai या Zustand चुनो।

---

## When to use which (105)
- First classify the state: local UI, form, URL, server data, or shared client state; the tool follows the type.
- URL for shareable state (filters, tabs, page); Context for slow values; Zustand/Jotai/Redux for client state; RTK Query / TanStack Query for server data.
- Do not store derived values (`total`) separately: they drift out of sync.

| State type | First choice |
|---|---|
| Local UI | useState / useReducer |
| Shareable filters | URL search params |
| Theme, locale, user | Context |
| Shared client state | Zustand, Jotai or Redux Toolkit |
| Server data | TanStack Query or RTK Query |

> हिंदी: पहले state का प्रकार पहचानो, फिर tool चुनो, library का नाम देखकर नहीं।
