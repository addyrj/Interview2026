# 90. TypeScript with React — Props, Children, Events
# हिंदी में: React के साथ TypeScript — Props, Children, Events

> Verified with **TypeScript 5.9 (5.x)**, `@types/react` 19, `jsx: react-jsx`, `--strict`.

---

## 🔵 Simple Definition (English)
In a React + TypeScript app, a component is just a function whose **props are an object type**. You describe that type with an `interface` or `type`, and TypeScript checks every place the component is used. `children` is typed as `ReactNode`, and DOM events are typed with generics like `ChangeEvent<HTMLInputElement>` or `MouseEvent<HTMLButtonElement>`.

## 🔵 सरल परिभाषा (Hindi)
React + TypeScript में component बस एक function है जिसके **props एक object type** होते हैं। आप उस type को `interface` या `type` से बताते हो और TypeScript हर उस जगह check करता है जहाँ component use हुआ है। `children` का type `ReactNode` होता है, और DOM events के types `ChangeEvent<HTMLInputElement>` या `MouseEvent<HTMLButtonElement>` जैसे generics से बनते हैं।

---

## 🔴 Problem it Solves
In JavaScript React you rely on `PropTypes` (runtime only, dev-only warnings) or memory. Pass `price="100"` instead of `100`, forget a required prop, or read `e.target.value` on the wrong element, and you find the bug in the browser. TypeScript moves all of this to **compile time** and gives autocomplete for props, and refactoring a prop name updates every usage.

## 🔴 यह क्यों बना? (Hindi)
JavaScript React में आप `PropTypes` (सिर्फ runtime, सिर्फ dev warnings) या याददाश्त पर निर्भर रहते हो। `price="100"` पास कर दिया (100 की जगह), required prop भूल गए, या गलत element पर `e.target.value` पढ़ लिया, तो bug browser में दिखता है। TypeScript यह सब **compile time** पर पकड़ता है, props का autocomplete देता है, और prop का नाम बदलने पर हर usage अपने आप check होता है।

---

## 🟢 How it Works — Step by Step
Step 1 → Define `interface Props { ... }` (use `?` for optional props).
Step 2 → Annotate the destructured parameter: `function Card({ name, price }: Props)`. (Plain function + typed props is preferred over `React.FC`.)
Step 3 → For wrapper components use `children: ReactNode` or `PropsWithChildren<Props>`.
Step 4 → For callbacks, type them as functions: `onSelect: (id: number) => void`.
Step 5 → For DOM events use React's generic event types (`ChangeEvent<HTMLInputElement>`) or the handler aliases (`ChangeEventHandler<HTMLInputElement>`).
Step 6 → To wrap a native element, extend its props: `ComponentPropsWithoutRef<"button">`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `interface Props { ... }` बनाओ (optional के लिए `?`)।
Step 2 → Destructured parameter annotate करो: `function Card({ name, price }: Props)`। (`React.FC` की जगह plain function + typed props बेहतर है।)
Step 3 → Wrapper components के लिए `children: ReactNode` या `PropsWithChildren<Props>` use करो।
Step 4 → Callbacks को function type दो: `onSelect: (id: number) => void`।
Step 5 → DOM events के लिए React के generic types (`ChangeEvent<HTMLInputElement>`) या handler aliases (`ChangeEventHandler<HTMLInputElement>`) लगाओ।
Step 6 → Native element को wrap करने के लिए उसके props extend करो: `ComponentPropsWithoutRef<"button">`।

---

## 🟡 Real World Example
**Zomato's `DishCard`** receives `name`, `price`, `veg` and an `onAdd(dishId)` callback. The cart page passes `price={199}`; if a developer passes `"199"`, the build fails. A `Modal` wrapper takes `children`, and a `SearchBox` handles `onChange` with the correct `ChangeEvent<HTMLInputElement>` so `e.target.value` is a string.

## 🟡 Real Example Hindi mein
**Zomato का `DishCard`** `name`, `price`, `veg` और `onAdd(dishId)` callback लेता है। Cart page `price={199}` देता है; अगर कोई developer `"199"` दे दे तो build fail हो जाता है। `Modal` wrapper `children` लेता है, और `SearchBox` सही `ChangeEvent<HTMLInputElement>` के साथ `onChange` handle करता है, इसलिए `e.target.value` string होता है।

---

## 💻 Code Example — Basic

```tsx
// DishCard.tsx — typed props, optional prop, callback prop
import type { ReactNode } from "react"; // type-only import (erased at build time)

interface DishCardProps {
  id: number;                       // required: dish id
  name: string;                     // required: dish name
  price: number;                    // required: price in rupees
  veg?: boolean;                    // optional: may be undefined
  onAdd: (id: number) => void;      // callback: receives the dish id, returns nothing
  badge?: ReactNode;                // optional: anything renderable (string, element, null)
}

// Plain function component; props annotated on the destructured parameter
export function DishCard({ id, name, price, veg = true, onAdd, badge }: DishCardProps) {
  return (
    <div>
      <h3>{name} {veg ? "🟢" : "🔴"} {badge}</h3>          {/* veg defaults to true */}
      <p>₹{price.toFixed(2)}</p>                            {/* price is number, so toFixed exists */}
      <button onClick={() => onAdd(id)}>Add</button>        {/* inline arrow gets typed MouseEvent for free */}
    </div>
  );
}

// Usage - TypeScript checks every prop
export const Demo = () => <DishCard id={1} name="Paneer Tikka" price={199} onAdd={(id) => console.log(id)} />;
```

## 💻 Code Example — Advanced

```tsx
// Advanced: children, event types, wrapping native elements, generic list, discriminated props
import type {
  ChangeEvent, FormEvent, KeyboardEvent, MouseEvent,
  ComponentPropsWithoutRef, PropsWithChildren, ReactNode,
} from "react";

// 1) children via PropsWithChildren (adds children?: ReactNode)
export function Modal({ title, children }: PropsWithChildren<{ title: string }>) {
  return <section><h2>{title}</h2>{children}</section>; // children can be text, elements, arrays
}

// 2) Extend a native element's props, then add your own
type ButtonProps = ComponentPropsWithoutRef<"button"> & { variant?: "primary" | "danger" };
export function PayButton({ variant = "primary", children, ...rest }: ButtonProps) {
  return <button data-variant={variant} {...rest}>{children}</button>; // rest has onClick, disabled, type, ...
}

// 3) Event handlers with exact element types
export function SearchForm({ onSearch }: { onSearch: (q: string) => void }) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {   // e.target is HTMLInputElement
    console.log(e.target.value);                                  // value: string
  };
  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {     // keyboard event on an input
    if (e.key === "Enter") onSearch(e.currentTarget.value);       // currentTarget is the input
  };
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {       // form submit event
    e.preventDefault();                                           // stop page reload
  };
  const handleClick = (e: MouseEvent<HTMLButtonElement>) => {     // click on a button
    console.log(e.currentTarget.name);                            // name is string on a button
  };
  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} onKeyDown={handleKey} />
      <button name="go" onClick={handleClick}>Search</button>
    </form>
  );
}

// 4) Generic component: T is inferred from `items`
interface ListProps<T> { items: T[]; render: (item: T) => ReactNode; keyOf: (item: T) => string | number }
export function List<T>({ items, render, keyOf }: ListProps<T>) {
  return <ul>{items.map((i) => <li key={keyOf(i)}>{render(i)}</li>)}</ul>; // render gets T
}
export const Menu = () => (
  <List items={[{ id: 1, name: "Dosa" }]} keyOf={(d) => d.id} render={(d) => d.name} /> // d inferred
);

// 5) Discriminated-union props: only valid combinations compile
type AlertProps =
  | { kind: "success"; message: string }
  | { kind: "error"; message: string; retry: () => void };
export function Alert(p: AlertProps) {
  return <div>{p.message}{p.kind === "error" && <button onClick={p.retry}>Retry</button>}</div>; // retry narrowed
}
```

---

## 🟠 Node/Express + React Integration

```tsx
// Share ONE type between API and UI. In a monorepo this lives in a shared package.
export interface OrderDTO { id: number; item: string; amount: number; status: "PLACED" | "PAID" } // API contract

// React side: component takes the DTO as props
export function OrderRow({ order, onPay }: { order: OrderDTO; onPay: (id: number) => void }) {
  return (
    <tr>
      <td>{order.item}</td>
      <td>{order.amount}</td>
      <td>{order.status === "PLACED" ? <button onClick={() => onPay(order.id)}>Pay</button> : "Paid"}</td>
    </tr>
  );
}
```

```typescript
// Express side returns the SAME type, so a renamed field breaks both sides at compile time
import express from "express";
interface OrderDTO { id: number; item: string; amount: number; status: "PLACED" | "PAID" } // same shape

const app = express();
app.get("/api/orders", (_req, res) => {
  const orders: OrderDTO[] = [{ id: 1, item: "Biryani", amount: 320, status: "PLACED" }]; // checked against DTO
  res.json(orders); // JSON sent to React
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Missing required prop
```tsx
// ❌ WRONG
import type { FC } from "react";
interface CardProps { name: string; price: number }
const Card: FC<CardProps> = ({ name, price }) => <p>{name}{price}</p>;
export const A = () => <Card name="Pizza" />;
// error TS2741: Property 'price' is missing in type '{ name: string; }' but required in type 'CardProps'.
```

❌ Mistake 2: Wrong prop type (string vs number)
```tsx
// ❌ WRONG
import type { FC } from "react";
interface CardProps { name: string; price: number }
const Card: FC<CardProps> = ({ name, price }) => <p>{name}{price}</p>;
export const B = () => <Card name="Pizza" price="100" />;
// error TS2322: Type 'string' is not assignable to type 'number'.
```
✅ Correct: `price={100}`.

❌ Mistake 3: Wrong element type in the event handler
```tsx
// ❌ WRONG
import { useState, type ChangeEvent } from "react";
export const C = () => {
  const [q, setQ] = useState("");
  const h = (e: ChangeEvent<HTMLButtonElement>) => setQ(e.target.value);
  return <input value={q} onChange={h} />;
};
// error TS2322: Type '(e: ChangeEvent<HTMLButtonElement>) => void' is not assignable to type
// 'ChangeEventHandler<HTMLInputElement, HTMLInputElement>'.
//   Types of parameters 'e' and 'event' are incompatible. ... (long chain ending in HTMLInputElement vs HTMLButtonElement)
```
✅ Correct: `ChangeEvent<HTMLInputElement>` for an `<input>`.

❌ Mistake 4: Using the DOM `MouseEvent` instead of React's
```tsx
// ❌ WRONG
export const D = () => <input onChange={(e: MouseEvent) => {}} />;
// error TS2322: Type '(e: MouseEvent) => void' is not assignable to type 'ChangeEventHandler<HTMLInputElement, HTMLInputElement>'.
//   Type 'ChangeEvent<HTMLInputElement, HTMLInputElement>' is missing the following properties from type 'MouseEvent': altKey, button, ...
```
✅ Correct: import event types from `"react"` and match the event (`ChangeEvent`, not `MouseEvent`).

---

## 🧠 Tricky Interview Question

```tsx
// ❌ Why does this fail even though onClick IS a function?
interface Props { onClick: (id: number) => void }
const Btn = ({ onClick }: Props) => <button onClick={onClick}>x</button>;
// error TS2322: Type '(id: number) => void' is not assignable to type 'MouseEventHandler<HTMLButtonElement>'.
//   Types of parameters 'id' and 'event' are incompatible.
//     Type 'MouseEvent<HTMLButtonElement, MouseEvent>' is not assignable to type 'number'.
```
**Answer:** `<button onClick>` expects `MouseEventHandler<HTMLButtonElement>`, i.e. `(event) => void`. Passing `onClick` typed `(id: number) => void` directly fails: the first argument React supplies is an *event*, not a number. Fix by wrapping: `onClick={() => onClick(1)}`. Interview point: callback props that expect domain values (`id`) and DOM handlers are different types - never pass one where the other is expected.

---

## ⚫ Interview Questions + Answers

Q1: `React.FC` vs a plain function with typed props?
A1: Since React 18 types, `FC` no longer adds implicit `children`. Plain functions infer return type, work cleanly with generics (`List<T>`), and support default values easily. `FC` is fine but not required; most style guides prefer plain functions.

Q2: `ReactNode` vs `ReactElement` vs `JSX.Element`?
A2: `ReactNode` = anything renderable (string, number, element, array, null, boolean). `ReactElement` = only an element object. Use `ReactNode` for `children` and slots; use `ReactElement` only when you must clone/inspect an element.

Q3: How do you type a wrapper around `<input>`?
A3: `ComponentPropsWithoutRef<"input"> & { label: string }`, then spread `...rest` onto the `<input>`. This keeps every native attribute (`type`, `onChange`, `disabled`) typed. Use `forwardRef` (or `ref` prop in React 19) when the parent needs the DOM node.

Q4: `e.target` vs `e.currentTarget`?
A4: `currentTarget` is the element the handler is attached to (typed precisely, e.g. `HTMLInputElement`). `target` is the element that triggered the event (typed as `EventTarget`/`Element` in general). Prefer `currentTarget` for typed access.

Q5: How do you stop invalid prop combinations?
A5: Discriminated-union props (`kind: "error"` requires `retry`) or `never`-based exclusive props. The compiler rejects `<Alert kind="success" retry={...} />`.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- Typed props on every shared component (design-system parts, cards, forms)
- Generic components (`List<T>`, `Table<T>`, `Select<T>`)
- Extending native props for wrappers (Button, Input)

❌ Avoid:
- `props: any` or `{}` as the props type
- Over-engineering: massive conditional prop types for a one-off component
- Duplicating API types by hand in the UI - import the shared DTO instead

---

## 📊 Visual Diagram
```
<DishCard id={1} name="Dosa" price={99} onAdd={fn} />
            │
            ▼
   interface DishCardProps { id; name; price; veg?; onAdd }
            │  checked by tsc
            ▼
   function DishCard(props) ──► JSX

 Events:  <input onChange=(e: ChangeEvent<HTMLInputElement>)>
                                   e.target.value : string
 Children: PropsWithChildren<P>  =  P & { children?: ReactNode }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Props | Inputs of a component | Component के inputs |
| ReactNode | Anything React can render | React जो भी render कर सके |
| ChangeEvent<T> | Typed input change event | typed input change event |
| PropsWithChildren | Adds `children` to props | props में `children` जोड़ता है |
| ComponentPropsWithoutRef | Native element props type | Native element के props का type |
| Discriminated props | Props chosen by a tag field | tag field से चुने गए props |

---

## ⚡ 3-Line Summary
English:
1. Type props with an `interface`; the compiler flags missing or wrong props at every usage.
2. `children` is `ReactNode`; DOM events are `ChangeEvent<HTMLInputElement>`, `MouseEvent<HTMLButtonElement>` etc. from `"react"`.
3. Wrap native elements with `ComponentPropsWithoutRef<"tag">`, use generics for lists, unions for exclusive props.

Hindi:
1. Props को `interface` से type करो; missing या गलत props हर usage पर compiler पकड़ लेता है।
2. `children` `ReactNode` है; DOM events `"react"` से आते हैं जैसे `ChangeEvent<HTMLInputElement>`।
3. Native element wrap करने के लिए `ComponentPropsWithoutRef<"tag">`, lists के लिए generics, exclusive props के लिए unions।

---

## ➡️ Next Topic
**91. TypeScript with React Hooks (useState, useReducer, useRef)** — typing state, reducers and refs.
