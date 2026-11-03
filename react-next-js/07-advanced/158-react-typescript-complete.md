# 158. React + TypeScript Complete
# हिंदी में: React + TypeScript — Props, Hooks, Events को Type-Safe बनाना

---

## 🔵 Simple Definition (English)
**TypeScript** adds static types to JavaScript. In React it checks, while you write code, that components get the right props, hooks hold the right state, and events have the right shape. Mistakes show up as red underlines in the editor instead of crashes in production.

## 🔵 सरल परिभाषा (Hindi)
**TypeScript** JavaScript में static types जोड़ता है। React में यह code लिखते समय जाँचता है कि components को सही props मिले, hooks में सही state है, और events का shape सही है। गलतियाँ production में crash की जगह editor में लाल लकीर के रूप में दिखती हैं।

---

## 🔴 Problem it Solves

Plain JavaScript React fails at runtime: a typo like `restaurant.nmae` renders `undefined`, a missing prop silently breaks a card, and refactoring a prop name means searching every file. `PropTypes` only warns in the browser console at runtime (and are ignored in React 19).

```jsx
// PROBLEM (JavaScript): no one tells you this is wrong until a user sees it
<RestaurantCard name="Meghana" rating="4.5" />   // rating should be a number
function RestaurantCard({ name, rating }) {
  return <p>{name} {rating.toFixed(1)}</p>;      // crash: "4.5".toFixed is not a function
}
```

## 🔴 यह क्यों बना? (Hindi)
Plain JavaScript React runtime पर फेल होता है: `restaurant.nmae` जैसी typo `undefined` दिखाती है, छूटा हुआ prop card को चुपचाप तोड़ देता है, और prop का नाम बदलने के लिए हर file खोजनी पड़ती है। `PropTypes` सिर्फ browser console में runtime पर चेतावनी देते हैं (और React 19 में नज़रअंदाज़ होते हैं)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Use .tsx files for components (JSX allowed) and .ts for plain logic
Step 2 → Describe props with an interface or type; destructure with that type
Step 3 → Hooks infer types: useState(0) is number; give a generic when needed: useState<User | null>(null)
Step 4 → Type events with React types: React.ChangeEvent<HTMLInputElement>, React.MouseEvent<HTMLButtonElement>
Step 5 → Type children as React.ReactNode; type style/other HTML props with React.ComponentProps<'button'>
Step 6 → Type refs: useRef<HTMLInputElement>(null); type context and reducers explicitly
Step 7 → tsc / the editor checks everything at compile time; the build emits plain JavaScript (types vanish)

Re-render behavior: types have ZERO runtime effect, so re-render behavior is identical to JavaScript.
Performance impact: none at runtime; slightly slower dev builds/type-checks, repaid by fewer bugs.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Components के लिए .tsx files (JSX चलता है) और सामान्य logic के लिए .ts
Step 2 → Props को interface या type से बताओ; उसी type के साथ destructure करो
Step 3 → Hooks type अपने-आप समझते हैं: useState(0) number है; ज़रूरत पर generic दो: useState<User | null>(null)
Step 4 → Events के React types: React.ChangeEvent<HTMLInputElement>, React.MouseEvent<HTMLButtonElement>
Step 5 → children के लिए React.ReactNode; बाकी HTML props के लिए React.ComponentProps<'button'>
Step 6 → Refs: useRef<HTMLInputElement>(null); context और reducers के types साफ़ लिखो
Step 7 → tsc / editor compile time पर सब जाँचता है; build सादा JavaScript बनाता है (types हट जाते हैं)

Re-render behavior: types का runtime पर कोई असर नहीं, इसलिए re-render व्यवहार JavaScript जैसा ही है।
Performance impact: runtime पर शून्य; dev build/type-check थोड़ा धीमा, पर कम bugs से भरपाई।
```

---

## 🟡 Real World Example
**Zomato cart:** The API returns `{ id, name, price, qty }`. With a shared `CartItem` type, the cart list, the quantity stepper, the price summary and the checkout request all agree on the same shape. When the backend renames `price` to `unitPrice`, the compiler lists every file to fix. A new developer sees from the types alone that `onQtyChange` receives `(id: string, qty: number)`.

## 🟡 Real Example Hindi mein
**Zomato cart:** API `{ id, name, price, qty }` भेजता है। साझा `CartItem` type होने से cart list, quantity stepper, price summary और checkout request सब एक ही shape पर सहमत रहते हैं। Backend `price` को `unitPrice` कर दे तो compiler बताता है कि कौन-सी files ठीक करनी हैं। नया developer सिर्फ types से समझ जाता है कि `onQtyChange` को `(id: string, qty: number)` मिलता है।

---

## 💻 Code Example — Basic

```tsx
// Basic: typed props, state, events and children (React 18/19, TypeScript 5)
import { useState, type ReactNode } from 'react';        // type-only import of ReactNode
import { createRoot } from 'react-dom/client';

// Props described by an interface
interface CardProps {
  title: string;                                          // required string
  price?: number;                                         // optional number
  children?: ReactNode;                                   // anything renderable
  onAdd: (title: string) => void;                         // callback with typed argument
}

function Card({ title, price = 0, children, onAdd }: CardProps) {  // default value for optional prop
  return (
    <div>
      <h3>{title}</h3>
      <p>Rs. {price.toFixed(2)}</p>                       {/* price is always number here */}
      {children}
      <button onClick={() => onAdd(title)}>Add</button>   {/* onAdd gets a string */}
    </div>
  );
}

function App() {
  const [count, setCount] = useState(0);                   // inferred as number
  const [name, setName] = useState('');                    // inferred as string

  // Event handler typed with the exact element type
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value);

  return (
    <div>
      <input value={name} onChange={onChange} placeholder="Your name" />
      <Card title="Biryani" price={250} onAdd={() => setCount((c) => c + 1)}>
        <small>Serves 2</small>
      </Card>
      <p>Cart: {count}</p>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App />);  // ! tells TS the element exists
```

## 💻 Code Example — Advanced

```tsx
// Advanced: reducer with discriminated union, typed context, custom hook, ComponentProps, ref
import {
  createContext, useContext, useReducer, useRef, useEffect,
  type ComponentProps, type Dispatch, type ReactNode,
} from 'react';

// ---- domain types ----
type CartItem = { id: string; name: string; price: number; qty: number };

// Discriminated union: the "type" field narrows the payload
type Action =
  | { type: 'add'; item: Omit<CartItem, 'qty'> }          // add needs everything except qty
  | { type: 'remove'; id: string }
  | { type: 'setQty'; id: string; qty: number }
  | { type: 'clear' };

function reducer(state: CartItem[], action: Action): CartItem[] {
  switch (action.type) {
    case 'add': {
      const found = state.find((i) => i.id === action.item.id);       // action.item exists here
      return found
        ? state.map((i) => (i.id === found.id ? { ...i, qty: i.qty + 1 } : i))
        : [...state, { ...action.item, qty: 1 }];
    }
    case 'remove': return state.filter((i) => i.id !== action.id);     // action.id exists here
    case 'setQty': return state.map((i) => (i.id === action.id ? { ...i, qty: action.qty } : i));
    case 'clear': return [];
    default: {
      const _exhaustive: never = action;                               // compile error if a case is missed
      return state;
    }
  }
}

// ---- typed context (null default + safe hook) ----
type CartContextValue = { items: CartItem[]; dispatch: Dispatch<Action>; total: number };
const CartContext = createContext<CartContextValue | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, dispatch] = useReducer(reducer, []);                   // state type inferred from reducer
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);        // derived, no extra state
  return <CartContext.Provider value={{ items, dispatch, total }}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used inside <CartProvider>'); // narrows null away
  return ctx;
}

// ---- component that extends native button props ----
type ButtonProps = ComponentProps<'button'> & { variant?: 'primary' | 'ghost' }; // all <button> props + ours
export function Button({ variant = 'primary', style, ...rest }: ButtonProps) {
  return <button style={{ fontWeight: variant === 'primary' ? 700 : 400, ...style }} {...rest} />;
}

// ---- typed ref: focus an input on mount ----
export function SearchBox() {
  const inputRef = useRef<HTMLInputElement>(null);                     // null until mounted
  useEffect(() => { inputRef.current?.focus(); }, []);                 // optional chaining handles null
  return <input ref={inputRef} placeholder="Search dishes" />;
}
```

---

## 🟠 Next.js Connection

Next.js has first-class TypeScript support: create a project with `create-next-app --typescript`, and it generates `tsconfig.json` and `next-env.d.ts`. Types exist for page props, metadata and route handlers. In Next.js 15 `params` is a Promise, so type it that way. `typedRoutes` (stable or experimental depending on version) can type-check `<Link href>`.

```tsx
// app/restaurants/[slug]/page.tsx (Server Component, Next.js 15)
import type { Metadata } from 'next';                    // official metadata type

type Props = {
  params: Promise<{ slug: string }>;                      // Next.js 15: params is async
  searchParams: Promise<{ sort?: 'rating' | 'eta' }>;     // known query values
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;                          // await before use
  return { title: `Restaurant ${slug}` };
}

export default async function Page({ params, searchParams }: Props) {
  const { slug } = await params;
  const { sort = 'rating' } = await searchParams;         // default value typed from the union
  return <h1>{slug} sorted by {sort}</h1>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `any` to silence errors
✅ **Correct:** Use proper types, `unknown` plus narrowing, or generics

```tsx
// Wrong
const [user, setUser] = useState<any>(null);               // ❌ no safety at all
// Right
type User = { id: string; name: string };
const [user, setUser] = useState<User | null>(null);      // ✅ forces null checks
```

❌ **Mistake 2:** Typing `useState([])` without a generic (inferred as `never[]`)
✅ **Correct:** Provide the element type

```tsx
// Wrong
const [items, setItems] = useState([]);                    // ❌ type never[]; setItems([x]) errors
// Right
const [items, setItems] = useState<CartItem[]>([]);        // ✅
```

❌ **Mistake 3:** Using `React.FC` and relying on implicit children, or non-null assertions (`!`) everywhere
✅ **Correct:** Type props directly; use real null checks

```tsx
// Wrong
const Box: React.FC = ({ children }) => <div>{children}</div>;  // ❌ children not in props since React 18 types
// Right
function Box({ children }: { children: ReactNode }) { return <div>{children}</div>; } // ✅
```

---

## 🧠 Tricky Interview Question

```tsx
const [count, setCount] = useState(0);
const ref = useRef<number>();          // what is ref.current's type?
const ref2 = useRef<number>(0);
const ref3 = useRef<HTMLDivElement>(null);
ref3.current = document.createElement('div');   // is this allowed?
```
**Answer:** With `@types/react` 18, `useRef<number>()` gives `MutableRefObject<number | undefined>`, while `useRef<number>(0)` gives a mutable `{ current: number }`. `useRef<HTMLDivElement>(null)` returns a read-only `RefObject` in `@types/react` 18, so assigning to `.current` is an error (it is meant to be managed by React). In `@types/react` 19, `useRef` requires an argument and refs are mutable, so details differ by version: check your installed types. The key idea is the different overloads: DOM refs (`null` initial) are controlled by React, value refs (non-null initial) are your own mutable box.

---

## ⚫ Interview Questions + Answers

Q1: `interface` or `type` for props?
A1: Both work. `interface` supports declaration merging and `extends`; `type` supports unions, intersections and mapped types. Pick one convention per team. Use `type` for unions such as actions or variants, and `interface` or `type` for plain object props.

Q2: How do you type `children`?
A2: `React.ReactNode` for anything renderable, `React.ReactElement` for a single element, or a function type for render props. Do not rely on `React.FC` to provide it.

Q3: How do you type events and handlers?
A3: Use `React.ChangeEvent<HTMLInputElement>`, `React.FormEvent<HTMLFormElement>`, `React.MouseEvent<HTMLButtonElement>`, and for inline handlers let TypeScript infer from the JSX attribute. For handler props use `(e: React.ChangeEvent<HTMLInputElement>) => void`.

Q4: How do you make a component accept all native props of an element?
A4: `type Props = React.ComponentProps<'button'> & { variant?: 'primary' | 'ghost' }`. In React 19 `ref` is part of `ComponentProps`; in React 18 use `ComponentPropsWithoutRef` plus `forwardRef`.

Q5: What is a discriminated union and why use it in reducers?
A5: A union of object types sharing a literal field (`type`). Checking that field narrows the type, so each `case` knows its payload. Adding a never-check in `default` makes the compiler warn when a new action is not handled.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The codebase has more than one developer or will live for months
- You share APIs, props and data contracts across many components
- You want safe refactoring and better editor autocomplete

❌ **Avoid when:**
- A throwaway prototype or a very small demo
- The team has no time to learn it and the project is short-lived
- You over-engineer types (deep conditional types) that nobody can read

---

## 📊 Visual Diagram

```
  .tsx source ──► TypeScript compiler (tsc / SWC / esbuild strips types)
       │                  │
       │ type check       └──► plain .js  (NO types at runtime)
       ▼
  Errors in editor:
    <Card title={5} />        ✗ number is not string
    <Card />                  ✗ missing onAdd
    dispatch({type:'zzz'})    ✗ not in Action union

  Props flow:   interface CardProps ──► Card({..}: CardProps) ──► <Card .../>  (checked at both ends)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type annotation | Declared type of a value | मान का घोषित type |
| Interface / type | Names for object shapes | Object के shape के नाम |
| Generic | Type with a parameter, `<T>` | Parameter वाला type |
| Union | One of several types, `A \| B` | कई types में से एक |
| Discriminated union | Union tagged with literal field | Literal field से पहचाना union |
| ReactNode | Anything React can render | React जो कुछ render कर सके |
| Type narrowing | Refining a type via checks | जाँच से type को सीमित करना |
| tsconfig | TypeScript settings file | TypeScript की settings file |

---

## ⚡ 3-Line Summary
**English:**
1. TypeScript types props, state, events, refs, context and reducers, and catches bugs before runtime.
2. Use generics for `useState<T>`, discriminated unions for actions, and `ComponentProps` to extend native elements.
3. Avoid `any` and `React.FC` children assumptions; types have no runtime cost.

**Hindi:**
1. TypeScript props, state, events, refs, context और reducers को type करता है और bugs runtime से पहले पकड़ता है।
2. `useState<T>` के लिए generics, actions के लिए discriminated unions, और native elements बढ़ाने के लिए `ComponentProps` इस्तेमाल करो।
3. `any` और `React.FC` के children वाली धारणा से बचो; types का runtime खर्च नहीं है।

---

## ➡️ Next Topic
**159. Generics in React TypeScript** — Reusable components (Table, Select, List) को किसी भी data type के साथ type-safe बनाने के लिए generics सीखेंगे।
