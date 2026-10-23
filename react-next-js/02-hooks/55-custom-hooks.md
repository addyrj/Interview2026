# 55. Custom Hooks — Complete Guide
# हिंदी में: Custom Hooks — Stateful Logic Reuse करना

---

## 🔵 Simple Definition (English)
A **Custom Hook** is a JavaScript function whose name starts with `use` that calls other React hooks inside it. Custom hooks let you **extract and share stateful logic** between components — without changing component hierarchy or using HOCs/render props.

## 🔵 सरल परिभाषा (Hindi)
**Custom Hook** एक JavaScript function है जिसका नाम `use` से शुरू होता है और अंदर अन्य React hooks call करता है। Custom hooks आपको components के बीच **stateful logic extract और share** करने देते हैं — component hierarchy बदले बिना और HOCs/render props use किए बिना।

---

## 🔴 Problem it Solves

```jsx
// PROBLEM: Same stateful logic repeated in many components

// Component A: needs fetch logic
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(data => { setUser(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [userId]);

  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;
  return <div>{user?.name}</div>;
}

// Component B: SAME fetch logic, just different URL!
function ProductDetails({ productId }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);    // DUPLICATE!
  const [error, setError] = useState(null);         // DUPLICATE!
  // ... same useEffect pattern duplicated!
}

// Custom Hook: extract ONCE, use everywhere!
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// PROBLEM: Same stateful logic कई components में repeat होती है
// Solution: Custom hook में extract करो — एक बार लिखो, कहीं भी use करो
// Component hierarchy नहीं बदलती — यही HOCs से बड़ा फायदा है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify repeated stateful pattern in components
         (fetch + loading + error, form state, subscription, etc.)

Step 2 → Create function starting with "use"
         function useFetch(url) { ... }

Step 3 → Move state + effects into the hook
         const [data, setData] = useState(null);
         useEffect(() => { fetch(url)... }, [url]);

Step 4 → Return what components need
         return { data, loading, error };

Step 5 → Use in any component
         const { data, loading, error } = useFetch('/api/users');
         Each component gets its OWN isolated state (not shared!)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Components में repeated stateful pattern identify करो

Step 2 → "use" से शुरू होने वाला function बनाओ
         function useFetch(url) { ... }

Step 3 → State + effects को hook में move करो

Step 4 → Components को जो चाहिए वो return करो
         return { data, loading, error };

Step 5 → किसी भी component में use करो
         const { data, loading, error } = useFetch('/api/users');
         हर component को अपनी isolated state मिलती है (shared नहीं!)
```

---

## 🟡 Real World Example
**Amazon's Product Page** likely has custom hooks like: `useProduct(productId)` for product data, `useWishlist()` for wishlist state, `usePriceHistory(productId)` for price charts, `useReviews(productId, page)` for paginated reviews. Each component stays clean — the complexity lives in the hook.

## 🟡 Real Example Hindi mein
**Amazon Product Page** पर custom hooks जैसे: `useProduct(productId)`, `useWishlist()`, `usePriceHistory(productId)`, `useReviews(productId, page)` होंगे। हर component clean रहता है — complexity hook में रहती है।

---

## 💻 Code Example — Basic

```jsx
import { useState, useEffect } from 'react';

// ── CUSTOM HOOK 1: useFetch ───────────────
// Reusable data fetching with loading/error
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!url) return;

    const controller = new AbortController();

    setLoading(true);
    setError(null);

    fetch(url, { signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => controller.abort(); // cleanup on unmount or url change
  }, [url]);

  return { data, loading, error };
}

// Usage in MULTIPLE components — no code duplication!
function UserProfile({ userId }) {
  const { data: user, loading, error } = useFetch(`/api/users/${userId}`);

  if (loading) return <Spinner />;
  if (error) return <p>Error: {error}</p>;
  return <div>Hello, {user?.name}!</div>;
}

function ProductDetails({ productId }) {
  const { data: product, loading, error } = useFetch(`/api/products/${productId}`);
  // Same hook, different URL — isolated state!
  if (loading) return <Spinner />;
  return <div>{product?.name} — ₹{product?.price}</div>;
}

// ── CUSTOM HOOK 2: useLocalStorage ────────
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = (newValue) => {
    try {
      setValue(newValue);
      localStorage.setItem(key, JSON.stringify(newValue));
    } catch (error) {
      console.error('localStorage write failed:', error);
    }
  };

  return [value, setStoredValue]; // same API as useState!
}

// Usage:
function Settings() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  // persists across page reloads automatically!
  return (
    <button onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
      Theme: {theme}
    </button>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useEffect, useRef, useCallback } from 'react';

// ── CUSTOM HOOK 3: useDebounce ─────────────
// Delay fast-changing values (search input)
function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer); // cancel on new value
  }, [value, delay]);

  return debouncedValue;
}

// Usage: search that doesn't fire on every keystroke
function SearchBar() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 400); // waits 400ms

  const { data: results, loading } = useFetch(
    debouncedQuery ? `/api/search?q=${debouncedQuery}` : null
  );

  return (
    <div>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search..."
      />
      {loading && <span>Searching...</span>}
      {results?.map(r => <div key={r.id}>{r.name}</div>)}
    </div>
  );
}

// ── CUSTOM HOOK 4: useForm ─────────────────
// Form state management — reusable across all forms
function useForm(initialValues, validate) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  }, [errors]);

  const handleBlur = useCallback((e) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));

    // Validate on blur
    if (validate) {
      const validationErrors = validate(values);
      setErrors(validationErrors);
    }
  }, [validate, values]);

  const handleSubmit = useCallback((onSubmit) => async (e) => {
    e.preventDefault();

    // Validate all fields
    const validationErrors = validate ? validate(values) : {};
    setErrors(validationErrors);
    setTouched(Object.keys(values).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {}));

    if (Object.keys(validationErrors).length === 0) {
      setIsSubmitting(true);
      try {
        await onSubmit(values);
      } finally {
        setIsSubmitting(false);
      }
    }
  }, [validate, values]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
  };
}

// Usage:
function LoginForm() {
  const validate = (values) => {
    const errors = {};
    if (!values.email) errors.email = 'Email required';
    if (!values.password) errors.password = 'Password required';
    return errors;
  };

  const form = useForm({ email: '', password: '' }, validate);

  const onSubmit = async (data) => {
    await api.login(data);
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input
        name="email"
        value={form.values.email}
        onChange={form.handleChange}
        onBlur={form.handleBlur}
      />
      {form.touched.email && form.errors.email && (
        <span className="error">{form.errors.email}</span>
      )}

      <input
        name="password"
        type="password"
        value={form.values.password}
        onChange={form.handleChange}
        onBlur={form.handleBlur}
      />

      <button type="submit" disabled={form.isSubmitting}>
        {form.isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

// ── CUSTOM HOOK 5: useIntersectionObserver ─
// For infinite scroll, lazy loading
function useIntersectionObserver(options = {}) {
  const [isVisible, setIsVisible] = useState(false);
  const targetRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setIsVisible(entry.isIntersecting);
    }, options);

    const target = targetRef.current;
    if (target) observer.observe(target);

    return () => { if (target) observer.unobserve(target); };
  }, []);

  return [targetRef, isVisible];
}

// Usage: lazy load images
function LazyImage({ src, alt }) {
  const [ref, isVisible] = useIntersectionObserver({ threshold: 0.1 });

  return (
    <div ref={ref}>
      {isVisible ? (
        <img src={src} alt={alt} />
      ) : (
        <div className="placeholder" />
      )}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// Custom hooks work in Next.js Client Components

// Example: Next.js-specific custom hook for router
'use client';
import { useRouter, useSearchParams } from 'next/navigation';
import { useCallback } from 'react';

// Custom hook that combines router + search params
function useQueryParams() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const setParam = useCallback((key, value) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value === null || value === undefined) {
      params.delete(key);
    } else {
      params.set(key, String(value));
    }
    router.push(`?${params.toString()}`, { scroll: false });
  }, [router, searchParams]);

  const getParam = useCallback((key, defaultValue = null) => {
    return searchParams.get(key) ?? defaultValue;
  }, [searchParams]);

  return { getParam, setParam };
}

// Usage in product filter:
function ProductFilter() {
  const { getParam, setParam } = useQueryParams();

  const category = getParam('category', 'all');
  const sort = getParam('sort', 'popular');

  return (
    <div>
      <select
        value={category}
        onChange={e => setParam('category', e.target.value)}
      >
        <option value="all">All</option>
        <option value="food">Food</option>
      </select>
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not starting with `use`
```jsx
// WRONG: hooks inside, but name doesn't start with 'use'
function fetchUserData(userId) { // ❌ React doesn't know this has hooks
  const [data, setData] = useState(null); // Rules of Hooks won't lint-check this
  // ...
}

// CORRECT:
function useFetchUser(userId) { // ✅ clear it's a hook
  const [data, setData] = useState(null);
  // ...
}
```

❌ **Mistake 2:** Thinking hooks share state
```jsx
// WRONG assumption: two components using same hook share state
function ComponentA() {
  const { count, setCount } = useCounter(); // ← OWN count
}

function ComponentB() {
  const { count, setCount } = useCounter(); // ← DIFFERENT count!
}
// Each component gets ISOLATED state — hooks don't share state!
// Use Context if you need shared state
```

❌ **Mistake 3:** Putting UI/JSX in a hook
```jsx
// WRONG: hook returns JSX
function useUserCard(userId) {
  const [user] = useFetch(`/api/users/${userId}`);
  return <div>{user?.name}</div>; // ❌ hooks shouldn't return JSX
}

// CORRECT: hooks return data/logic, components render JSX
function useUser(userId) {
  return useFetch(`/api/users/${userId}`); // ✅ return data
}

function UserCard({ userId }) {
  const { data: user, loading } = useUser(userId);
  return loading ? <Spinner /> : <div>{user?.name}</div>; // component renders JSX
}
```

---

## 🧠 Tricky Interview Question

```jsx
function useCounter(initial = 0) {
  const [count, setCount] = useState(initial);
  const increment = () => setCount(c => c + 1);
  const decrement = () => setCount(c => c - 1);
  return { count, increment, decrement };
}

// Component A and B both use useCounter()
// If Component A increments its counter, does Component B's counter change?
```
**Answer:** No. Each component calling `useCounter()` gets its own **isolated** state. Custom hooks share logic/behavior, not state. The `useState` inside the hook creates separate state for each component instance. To share state, you'd need Context or a state manager (Zustand/Redux).

---

## ⚫ Interview Questions + Answers

**Q1: What is a custom hook and why should you create one?**
A1: A custom hook is a function starting with `use` that uses React hooks internally. Create one when: (1) The same stateful logic pattern appears in 2+ components (DRY principle). (2) A component's hook logic is complex enough to be hard to read inline. (3) You want to share logic across projects (hook libraries). They extract logic without changing component structure — cleaner than HOCs or render props.

**Q2: What is the difference between a custom hook and a regular utility function?**
A2: A custom hook can call React hooks (useState, useEffect, etc.) — making it stateful and lifecycle-aware. A regular utility function can't call hooks (violates Rules of Hooks). If your function needs state or lifecycle, it must be a custom hook. If it's pure computation (format a date, sort an array), a regular function is fine.

**Q3: Do custom hooks share state between components?**
A3: No. Each component calling a custom hook gets its own isolated state. Calling `useCounter()` in ComponentA and ComponentB creates two separate `count` states. Custom hooks share **logic** (the pattern), not **state** (the values). To share state between components, lift it up to a common parent, use Context, or use a global state manager.

**Q4: Can custom hooks call other custom hooks?**
A4: Yes — this is a key strength. `useSearchWithDebounce` can call both `useDebounce` and `useFetch`. This composability lets you build complex behavior from simple building blocks. As long as the naming convention (`use*`) is maintained and Rules of Hooks are followed, custom hooks can call any other hooks.

**Q5: What are some common custom hook patterns you'd use in a real app?**
A5: Common patterns: `useFetch(url)` — data fetching with loading/error states. `useDebounce(value, delay)` — delay fast-changing inputs. `useLocalStorage(key, initial)` — persistent state. `useWindowSize()` — responsive layout. `useOnClickOutside(ref, handler)` — dismiss dropdowns. `usePrevious(value)` — compare with last render. `useForm(initialValues, validate)` — form management. `useInfiniteScroll(fetchFn)` — load more pattern.

---

## 🔷 When to Use + When Not to Use
✅ **Create a custom hook when:**
- Same stateful logic in 2+ components
- Complex hook logic makes a component hard to read
- Logic needs to be tested independently
- Sharing logic across projects/packages

❌ **Don't create a custom hook when:**
- Logic is used in only one place (just keep it in the component)
- It's pure computation with no hooks (use a regular function)
- You'd be creating a hook just to "organize" — hooks add abstraction cost

---

## 📊 Visual Diagram

```
BEFORE CUSTOM HOOKS — Logic Duplicated:
──────────────────────────────────────────────
  UserProfile          ProductDetails
  ┌──────────────┐     ┌──────────────┐
  │ useState(null)│     │ useState(null)│  DUPLICATE!
  │ useState(true)│     │ useState(true)│  DUPLICATE!
  │ useState(null)│     │ useState(null)│  DUPLICATE!
  │ useEffect(   │     │ useEffect(   │  DUPLICATE!
  │  fetch/error)│     │  fetch/error)│
  │ return JSX   │     │ return JSX   │
  └──────────────┘     └──────────────┘

AFTER CUSTOM HOOKS — Logic Extracted Once:
──────────────────────────────────────────────
  useFetch(url)
  ┌──────────────────────────────┐
  │ useState(data, loading, error)│  ← defined ONCE
  │ useEffect(fetch + cleanup)   │
  │ return { data, loading, error}│
  └──────────────────────────────┘
           │                   │
           ▼                   ▼
  UserProfile            ProductDetails
  ┌──────────────┐       ┌──────────────┐
  │ useFetch(url)│       │ useFetch(url)│  REUSED! ✅
  │ return JSX   │       │ return JSX   │
  └──────────────┘       └──────────────┘
  (own isolated state)  (own isolated state)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom Hook | Reusable function with hooks | Hooks वाला reusable function |
| Isolated state | Each component's own state | हर component की अपनी state |
| Logic extraction | Moving code to a separate function | Code को अलग function में ले जाना |
| Composable | Can be combined with other hooks | दूसरे hooks के साथ combine हो सके |
| DRY | Don't Repeat Yourself | खुद को repeat मत करो |

---

## ⚡ 3-Line Summary
**English:**
1. Custom hooks = functions starting with `use` that call other hooks — extract shared stateful logic into reusable pieces.
2. Each component calling a custom hook gets its OWN isolated state — custom hooks share logic, not state.
3. Common patterns: `useFetch`, `useDebounce`, `useForm`, `useLocalStorage`, `useWindowSize` — build once, use everywhere.

**Hindi:**
1. Custom hooks = `use` से शुरू होने वाले functions जो दूसरे hooks call करते हैं — shared stateful logic को reusable pieces में extract करते हैं।
2. हर component को अपनी ISOLATED state मिलती है — custom hooks logic share करते हैं, state नहीं।
3. Common patterns: `useFetch`, `useDebounce`, `useForm`, `useLocalStorage` — एक बार बनाओ, कहीं भी use करो।

---

## ➡️ Next Topic
**56. Custom Hook — Real Examples** — Production-grade custom hooks जो real apps में use होते हैं।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Custom Hooks](https://www.youtube.com/results?search_query=custom+hooks+react+akshay+saini+namaste) | Custom hooks in Hindi |
| 📺 YouTube | [Jack Herrington — Custom Hooks](https://www.youtube.com/results?search_query=custom+react+hooks+jack+herrington) | 10 custom hooks you need |
| 📝 Website | [usehooks.com](https://usehooks.com) | Library of production custom hooks |
| 📝 Article | [react.dev — Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks) | Official guide with examples |
