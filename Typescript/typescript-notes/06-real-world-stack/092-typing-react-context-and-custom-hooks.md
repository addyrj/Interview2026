# 92. Typing React Context and Custom Hooks
# हिंदी में: React Context और Custom Hooks को Type करना

> Verified with **TypeScript 5.9 (5.x)**, `@types/react` 19, `--strict`. `use(Context)` is React 19; `useContext` works everywhere.

---

## 🔵 Simple Definition (English)
`createContext<T>(default)` creates a typed channel for sharing state (theme, auth user, cart) without prop drilling. The tricky part is the **default value**: you rarely have a real value before the Provider mounts. The standard pattern is `createContext<T | undefined>(undefined)` plus a **custom hook** (`useCart()`) that throws if the Provider is missing, so consumers always get a non-undefined `T`. Custom hooks are just functions starting with `use`; typing them means typing their parameters and a precise return type (object or `as const` tuple).

## 🔵 सरल परिभाषा (Hindi)
`createContext<T>(default)` state (theme, auth user, cart) को prop drilling के बिना share करने का typed channel बनाता है। मुश्किल हिस्सा है **default value**: Provider mount होने से पहले असली value शायद ही मिलती है। Standard pattern: `createContext<T | undefined>(undefined)` और एक **custom hook** (`useCart()`) जो Provider न मिलने पर error throw करे, ताकि consumers को हमेशा `undefined` के बिना `T` मिले। Custom hook बस `use` से शुरू होने वाला function है; उसे type करने का मतलब है parameters और सटीक return type (object या `as const` tuple) देना।

---

## 🔴 Problem it Solves
Two bugs: (1) `createContext<Cart>({} as Cart)` lies to the compiler - forget the Provider and you get `undefined.items` at runtime. (2) Using `T | undefined` honestly forces `?.` / `if` checks in **every** component. The throw-in-the-hook pattern fixes both: one runtime guard, zero repeated checks, correct type everywhere. Custom hooks also need explicit return types so changing internals does not silently change the public API.

## 🔴 यह क्यों बना? (Hindi)
दो bugs: (1) `createContext<Cart>({} as Cart)` compiler से झूठ बोलता है - Provider भूल गए तो runtime पर `undefined.items`। (2) `T | undefined` ईमानदारी से रखो तो **हर** component में `?.` / `if` लगाना पड़ता है। Hook में throw करने का pattern दोनों हल करता है: एक runtime guard, repeat checks शून्य, और हर जगह सही type। Custom hooks को explicit return type चाहिए ताकि internals बदलने से public API चुपचाप न बदल जाए।

---

## 🟢 How it Works — Step by Step
Step 1 → Define the context value type: `interface CartContextValue { items; add; remove }`.
Step 2 → `const CartContext = createContext<CartContextValue | undefined>(undefined)`.
Step 3 → Write a `CartProvider` component that builds the value (state + stable callbacks) and renders `<CartContext value={...}>` (React 19) or `<CartContext.Provider value={...}>`.
Step 4 → Write `useCart()`: call `useContext`, `throw` if `undefined`, return the narrowed `CartContextValue`.
Step 5 → Export only the Provider and the hook, not the raw context.
Step 6 → For generic hooks (`useLocalStorage<T>`) return a tuple with `as const` or an explicit tuple type.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Context value का type बनाओ: `interface CartContextValue { items; add; remove }`।
Step 2 → `const CartContext = createContext<CartContextValue | undefined>(undefined)`।
Step 3 → `CartProvider` बनाओ जो value (state + stable callbacks) बनाकर `<CartContext value={...}>` (React 19) या `<CartContext.Provider value={...}>` render करे।
Step 4 → `useCart()` लिखो: `useContext` call करो, `undefined` हो तो `throw`, narrowed `CartContextValue` return करो।
Step 5 → सिर्फ Provider और hook export करो, raw context नहीं।
Step 6 → Generic hooks (`useLocalStorage<T>`) में tuple `as const` या explicit tuple type से return करो।

---

## 🟡 Real World Example
**Swiggy cart**: a `CartProvider` wraps the whole app. `RestaurantPage` calls `useCart().add(item)`, the header badge calls `useCart().items.length`, and checkout calls `useCart().total`. Because `useCart` throws outside the provider, a test that forgets to wrap the component fails with a clear message instead of a vague `undefined` crash.

## 🟡 Real Example Hindi mein
**Swiggy cart**: `CartProvider` पूरे app को wrap करता है। `RestaurantPage` `useCart().add(item)` call करता है, header badge `useCart().items.length` पढ़ता है, और checkout `useCart().total`। क्योंकि `useCart` provider के बाहर throw करता है, जो test wrap करना भूले वो साफ़ message के साथ fail होता है, अस्पष्ट `undefined` crash के साथ नहीं।

---

## 💻 Code Example — Basic

```tsx
// cart-context.tsx — typed context + guard hook
import { createContext, useContext, useState, type ReactNode } from "react";

interface CartItem { id: number; name: string; price: number } // one cart line

interface CartContextValue {
  items: CartItem[];                 // current items
  add: (item: CartItem) => void;     // add action
  total: number;                     // derived total
}

// undefined default = honest "no provider" state
const CartContext = createContext<CartContextValue | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);                     // state lives in provider
  const add = (item: CartItem) => setItems((prev) => [...prev, item]);   // immutable update
  const total = items.reduce((sum, i) => sum + i.price, 0);              // derived value
  return <CartContext.Provider value={{ items, add, total }}>{children}</CartContext.Provider>;
}

// Custom hook: narrows away `undefined` ONCE for every consumer
export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);                                    // type: CartContextValue | undefined
  if (ctx === undefined) throw new Error("useCart must be used inside <CartProvider>"); // guard
  return ctx;                                                             // now CartContextValue
}

// Consumer: no ?. needed
export function CartBadge() {
  const { items, total } = useCart();                                     // fully typed
  return <span>{items.length} items / ₹{total}</span>;
}
```

## 💻 Code Example — Advanced

```tsx
// advanced: factory for context+hook, split state/dispatch contexts, generic custom hooks
import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
  type Dispatch, type SetStateAction, type ReactNode,
} from "react";

// 1) Factory: removes the boilerplate for every new context
export function createStrictContext<T>(name: string) {
  const Ctx = createContext<T | undefined>(undefined);        // one context per call
  function useStrict(): T {
    const v = useContext(Ctx);                                // T | undefined
    if (v === undefined) throw new Error(`${name} provider missing`);
    return v;                                                  // T
  }
  return [Ctx.Provider, useStrict] as const;                  // as const => fixed tuple, not array
}

interface Auth { user: { id: string; name: string } | null; login: (name: string) => void }
export const [AuthProvider, useAuth] = createStrictContext<Auth>("Auth"); // typed pair

// 2) Split contexts: components that only dispatch do not re-render on state change
type Theme = "light" | "dark";
const ThemeStateCtx = createContext<Theme>("light");                                  // default is real here
const ThemeSetCtx = createContext<Dispatch<SetStateAction<Theme>> | undefined>(undefined);
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  return (
    <ThemeStateCtx.Provider value={theme}>
      <ThemeSetCtx.Provider value={setTheme}>{children}</ThemeSetCtx.Provider>
    </ThemeStateCtx.Provider>
  );
}
export const useTheme = (): Theme => useContext(ThemeStateCtx);

// 3) Generic custom hook returning a tuple (like useState)
export function useLocalStorage<T>(key: string, initial: T): readonly [T, (v: T) => void] {
  const [value, setValue] = useState<T>(() => {                 // lazy init
    const raw = typeof localStorage === "undefined" ? null : localStorage.getItem(key);
    return raw === null ? initial : (JSON.parse(raw) as T);     // JSON.parse returns any -> assert T
  });
  const set = useCallback((v: T) => setValue(v), []);           // stable setter
  useEffect(() => { localStorage.setItem(key, JSON.stringify(value)); }, [key, value]); // persist
  return useMemo(() => [value, set] as const, [value, set]);    // readonly tuple
}

export function Settings() {
  const [lang, setLang] = useLocalStorage<"en" | "hi">("lang", "en"); // lang: "en" | "hi"
  return <button onClick={() => setLang(lang === "en" ? "hi" : "en")}>{lang}</button>;
}
```

---

## 🟠 Node/Express + React Integration

```tsx
// AuthProvider that talks to an Express /api/me endpoint.
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

interface User { id: string; name: string; role: "admin" | "customer" } // shape of GET /api/me

type AuthState =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "authenticated"; user: User };               // user only exists when authenticated

const AuthCtx = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: "loading" });
  useEffect(() => {
    fetch("/api/me", { credentials: "include" })           // cookie session set by Express
      .then(async (r) => (r.ok ? ((await r.json()) as User) : null))
      .then((u) => setState(u ? { status: "authenticated", user: u } : { status: "anonymous" }))
      .catch(() => setState({ status: "anonymous" }));
  }, []);
  return <AuthCtx.Provider value={state}>{children}</AuthCtx.Provider>;
}

export function useAuthState(): AuthState {
  const v = useContext(AuthCtx);
  if (!v) throw new Error("AuthProvider missing");
  return v;
}

export function AdminOnly({ children }: { children: ReactNode }) {
  const a = useAuthState();
  if (a.status !== "authenticated") return null;           // narrowed below
  return a.user.role === "admin" ? <>{children}</> : null;  // a.user exists here
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Consuming `T | undefined` without a guard
```tsx
// ❌ WRONG
import { createContext, useContext } from "react";
interface Cart { items: string[] }
const Ctx = createContext<Cart | undefined>(undefined);
export const A = () => { const c = useContext(Ctx); return <p>{c.items.length}</p>; };
// error TS18048: 'c' is possibly 'undefined'.
```
✅ Correct: wrap in `useCart()` that throws, or check `if (!c) return null`.

❌ Mistake 2: Fake default with a wrong shape
```tsx
// ❌ WRONG
import { createContext } from "react";
interface Cart { items: string[] }
const Ctx2 = createContext<Cart>({});
// error TS2345: Argument of type '{}' is not assignable to parameter of type 'Cart'.
//   Property 'items' is missing in type '{}' but required in type 'Cart'.
```
✅ Correct: either a *real* default (`{ items: [] }`) or `T | undefined`. Avoid `{} as Cart`; it silences the error but lets bugs through.

❌ Mistake 3: Returning an array from a hook (widens to `(A | B)[]`)
```tsx
// ❌ WRONG (the hook itself compiles; the error appears at the call site)
import { useState } from "react";
export function useToggle() {
  const [on, setOn] = useState(false);
  return [on, () => setOn(!on)];               // inferred (boolean | (() => void))[]
}
const [flag, toggle] = useToggle();
toggle();
// error TS2349: This expression is not callable.
//   Not all constituents of type 'boolean | (() => void)' are callable.
//     Type 'false' has no call signatures.
```
✅ Correct: `return [on, () => setOn(!on)] as const;`

---

## 🧠 Tricky Interview Question

```tsx
// Will <Child/> re-render when only `setTheme` is used but the value object is rebuilt each render?
import { createContext, useContext, useState } from "react";
const Ctx = createContext<{ theme: string; setTheme: (t: string) => void } | undefined>(undefined);
export function P({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState("light");
  return <Ctx.Provider value={{ theme, setTheme }}>{children}</Ctx.Provider>; // new object every render!
}
export const Child = () => { const c = useContext(Ctx); return <b>{c?.theme}</b>; };
```
**Answer:** Yes. `{ theme, setTheme }` is a **new object each render**, so every consumer re-renders whenever `P` re-renders, even if `theme` is unchanged. The types are perfect but performance is not - typing does not fix referential identity. Solutions: `useMemo` the value, or split into a state context and a dispatch context (the Advanced example).

---

## ⚫ Interview Questions + Answers

Q1: Why `createContext<T | undefined>(undefined)` instead of `createContext<T>({} as T)`?
A1: The cast hides a missing-provider bug and gives `undefined` crashes. With `| undefined` plus a throwing hook, the type is honest and consumers get a clean `T`.

Q2: Why export a hook and not the context?
A2: Encapsulation: the hook narrows `undefined`, gives better error messages, and lets you change the internals (e.g. move to Redux) without touching consumers.

Q3: `as const` on a hook's return?
A3: It makes the array a `readonly [A, B]` tuple, so destructuring keeps each element's own type. Without it TS infers `(A | B)[]` and calling the function element fails (TS2349).

Q4: How do you avoid unnecessary re-renders with context?
A4: Memoize the value (`useMemo`), split state vs dispatch contexts, or use a selector library/Redux for fine-grained subscriptions. Context re-renders **all** consumers when the value identity changes.

Q5: Is `React.use(Context)` typed differently?
A5: Same type as `useContext`, but React 19's `use` can be called conditionally and also unwraps promises. Types come from the same `createContext<T>`.

---

## 🔷 When to Use + When Not to Use
✅ Use context for:
- Low-frequency global state: theme, locale, auth user, feature flags
- Dependency injection (API client, router) in a subtree

❌ Avoid for:
- High-frequency changing state (typing input, live prices) - use Redux/Zustand with selectors
- Passing props through just one or two levels
- `{} as T` defaults

---

## 📊 Visual Diagram
```
createContext<Cart | undefined>(undefined)
          │
 <CartProvider value={{items,add,total}}>
          │
   ┌──────┴──────────┐
 <Header/>       <Checkout/>
   useCart()  ──►  useContext(Ctx)
                     │ undefined? ── throw Error
                     ▼
                 CartContextValue  (narrowed once)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context | Shared value for a subtree | subtree में share होने वाली value |
| Provider | Component that supplies the value | value देने वाला component |
| Custom hook | `use*` function reusing logic | logic reuse करने वाला `use*` function |
| as const | Makes a literal readonly/fixed | literal को readonly/fixed बनाता है |
| Guard hook | Hook that throws if no provider | provider न होने पर throw करने वाला hook |
| Tuple | Fixed-position typed array | fixed-position typed array |

---

## ⚡ 3-Line Summary
English:
1. Use `createContext<T | undefined>(undefined)` and a `useX()` hook that throws, so consumers always get `T`.
2. Return tuples from custom hooks with `as const`; give public hooks explicit return types.
3. Context re-renders every consumer on a new value identity - memoize or split contexts.

Hindi:
1. `createContext<T | undefined>(undefined)` और throw करने वाला `useX()` hook लगाओ, ताकि consumers को हमेशा `T` मिले।
2. Custom hook से tuple `as const` के साथ return करो; public hooks को explicit return type दो।
3. नई value identity पर context हर consumer को re-render कराता है - memoize करो या contexts split करो।

---

## ➡️ Next Topic
**93. TypeScript with Redux Toolkit — RootState and AppDispatch** — the typed store setup every RTK app needs.
