# 16. Props — Types + Validation
# हिंदी में: Props के Types और Validation — गलत data को पहले ही पकड़ना

---

## 🔵 Simple Definition (English)
**Props** can hold any JavaScript value: strings, numbers, booleans, arrays, objects, functions, and even JSX elements. **Prop validation** means checking that a component receives the right type and shape of props, using PropTypes, TypeScript, or manual checks, so that mistakes are caught early instead of causing blank screens.

## 🔵 सरल परिभाषा (Hindi)
**Props** में कोई भी JavaScript value हो सकती है: strings, numbers, booleans, arrays, objects, functions, यहाँ तक कि JSX elements भी। **Prop validation** का मतलब है यह जाँचना कि component को सही type और shape के props मिले हैं, PropTypes, TypeScript या manual checks से, ताकि गलती blank screen बनने से पहले ही पकड़ी जाए।

---

## 🔴 Problem it Solves

JavaScript is dynamically typed. If `RestaurantCard` expects `rating` to be a number but gets the string `"4.5"` or `undefined`, nothing stops you at write time. The bug appears later: `rating.toFixed(1)` throws, `undefined.map` crashes the page, or the UI shows `NaN`. In a team of 20 developers, one person changes an API shape and 40 components break silently. Validation documents what each component expects and fails loudly and early (in development), close to the actual mistake.

```jsx
// PROBLEM: no contract. Which props are required? What types?
function RestaurantCard({ name, rating, tags, onOrder }) {
  return (
    <div>
      <h3>{name}</h3>
      <p>{rating.toFixed(1)}</p>            {/* crashes if rating is undefined or a string */}
      <ul>{tags.map((t) => <li key={t}>{t}</li>)}</ul>   {/* crashes if tags is undefined */}
      <button onClick={onOrder}>Order</button>
    </div>
  );
}
<RestaurantCard name="Biryani House" rating="4.5" />   // string rating, missing tags: runtime crash
```

## 🔴 यह क्यों बना? (Hindi)
JavaScript dynamically typed है। अगर `RestaurantCard` को `rating` number चाहिए पर उसे string `"4.5"` या `undefined` मिले, तो लिखते समय कोई नहीं रोकता। Bug बाद में दिखता है: `rating.toFixed(1)` error देता है, `undefined.map` पूरा page crash कर देता है, या UI में `NaN` आ जाता है। 20 developers की team में कोई एक API shape बदलता है और 40 components चुपचाप टूट जाते हैं। Validation हर component की अपेक्षा को document करती है और गलती के पास ही (development में) साफ़ error देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent passes props: <Card name="X" price={199} tags={['veg']} onAdd={fn} />
Step 2 → React gives the child ONE object: { name, price, tags, onAdd } (read-only)
Step 3 → Props can be any type: string, number, boolean, array, object, function, element, null
Step 4 → You declare the contract using ONE of:
           a) TypeScript types        (compile-time, recommended today)
           b) PropTypes               (runtime warnings in development, covered in topic 17)
           c) Manual guard in the code (throw / fallback)
Step 5 → On mismatch: TypeScript underlines in the editor; PropTypes prints a console warning
Step 6 → Props are immutable: the child never changes them, only the parent can send new ones

TYPES CHEAT: string "a" | number 5 | boolean {true} | array {[1]} | object {{a:1}} | function {fn} | element {<X/>}
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Parent props भेजता है: <Card name="X" price={199} tags={['veg']} onAdd={fn} />
Step 2 → React child को एक ही object देता है: { name, price, tags, onAdd } (read-only)
Step 3 → Props किसी भी type के हो सकते हैं: string, number, boolean, array, object, function, element, null
Step 4 → Contract इनमें से किसी एक से declare करो:
           a) TypeScript types        (compile-time, आज recommended)
           b) PropTypes               (development में runtime warnings, topic 17 में)
           c) Code में manual guard    (throw / fallback)
Step 5 → Mismatch पर: TypeScript editor में लाल रेखा देता है; PropTypes console में warning छापता है
Step 6 → Props immutable हैं: child उन्हें कभी नहीं बदलता, सिर्फ parent नए props भेज सकता है

TYPES CHEAT: string "a" | number 5 | boolean {true} | array {[1]} | object {{a:1}} | function {fn} | element {<X/>}
```

---

## 🟡 Real World Example
**Amazon product tile:** The tile receives `title` (string), `price` (number), `rating` (number 0 to 5), `isPrime` (boolean), `images` (array of URLs), `seller` (object with `id` and `name`), `onAddToCart` (function), and `badge` (a JSX element such as a "Deal of the day" label). If the backend returns `price: "1,299"` as a string for one product, a validated component shows a clear warning in development, and the team fixes the API mapping before release.

## 🟡 Real Example Hindi mein
**Amazon product tile:** Tile को `title` (string), `price` (number), `rating` (number 0 से 5), `isPrime` (boolean), `images` (URLs का array), `seller` (object जिसमें `id` और `name`), `onAddToCart` (function) और `badge` (JSX element, जैसे "Deal of the day" label) मिलते हैं। अगर backend किसी product के लिए `price: "1,299"` string भेजे, तो validated component development में साफ़ warning देता है, और release से पहले team API mapping ठीक कर लेती है।

---

## 💻 Code Example — Basic

```jsx
// All kinds of prop values, with simple manual validation
import { createRoot } from 'react-dom/client';

function ProductTile({
  title,            // string
  price,            // number
  isPrime,          // boolean
  images,           // array of strings
  seller,           // object { id, name }
  onAddToCart,      // function
  badge,            // JSX element (optional)
}) {
  // Manual guard: fail early in development with a clear message
  if (typeof price !== 'number' || Number.isNaN(price)) {
    console.error(`ProductTile: "price" must be a number, got ${typeof price}`);
  }

  return (
    <article>
      <img src={images[0]} alt={title} width="120" />       {/* first image from the array */}
      <h3>{title}</h3>                                       {/* string */}
      {badge}                                                {/* element rendered as is */}
      <p>₹{price.toLocaleString('en-IN')}</p>                {/* number formatted for India */}
      {isPrime && <span>Prime</span>}                        {/* boolean controls display */}
      <small>Sold by {seller.name}</small>                   {/* object property */}
      <button onClick={() => onAddToCart(title)}>Add</button> {/* function called with an argument */}
    </article>
  );
}

createRoot(document.getElementById('root')).render(
  <ProductTile
    title="Wireless Mouse"                      // string literal in quotes
    price={799}                                // numbers need curly braces
    isPrime                                    // shorthand for isPrime={true}
    images={['/mouse.jpg']}                    // array in braces
    seller={{ id: 's1', name: 'TechStore' }}   // object: double braces (braces + object literal)
    onAddToCart={(t) => alert(t + ' added')}   // function
    badge={<strong>Deal of the day</strong>}   // element as a prop
  />
);
```

## 💻 Code Example — Advanced

```jsx
// Production style: TypeScript-style contract in JSDoc + runtime fallback + safe defaults.
// (A .tsx version is shown after this block.)
import { memo } from 'react';

/**
 * @typedef {Object} Seller
 * @property {string} id
 * @property {string} name
 *
 * @typedef {Object} ProductTileProps
 * @property {string} title                        required
 * @property {number} price                        required, in rupees
 * @property {number} [rating]                     optional, 0 to 5
 * @property {boolean} [isPrime]                   optional
 * @property {string[]} [images]                   optional
 * @property {Seller} seller                       required
 * @property {(id: string) => void} onAddToCart    required callback
 * @property {React.ReactNode} [badge]             optional element
 */

/** @param {ProductTileProps} props */
function ProductTile({
  title,
  price,
  rating = 0,           // default value for an optional prop (modern replacement of defaultProps)
  isPrime = false,      // default boolean
  images = [],          // default array: protects images[0] and .map
  seller,
  onAddToCart,
  badge = null,         // default: render nothing
}) {
  const safeRating = Math.min(5, Math.max(0, Number(rating) || 0)); // clamp bad data into 0..5

  return (
    <article aria-label={title}>
      {images[0] ? <img src={images[0]} alt={title} width="120" /> : <div>No image</div>}
      <h3>{title}</h3>
      {badge}
      <p>₹{price.toLocaleString('en-IN')}</p>
      <p>{'★'.repeat(Math.round(safeRating))}</p>             {/* star display */}
      {isPrime && <span>Prime</span>}
      <small>Sold by {seller?.name ?? 'Unknown seller'}</small>  {/* optional chaining for safety */}
      <button onClick={() => onAddToCart(seller?.id)}>Add to cart</button>
    </article>
  );
}

export default memo(ProductTile);   // skip re-render when props are shallow-equal
```

```tsx
// ProductTile.tsx — the same contract in TypeScript (checked while you type, no runtime cost)
import type { ReactNode } from 'react';

type Seller = { id: string; name: string };

type ProductTileProps = {
  title: string;                       // required
  price: number;                       // required
  rating?: number;                     // optional (the ? makes it optional)
  isPrime?: boolean;
  images?: string[];
  seller: Seller;
  onAddToCart: (sellerId: string) => void;   // function signature is checked too
  badge?: ReactNode;                   // anything React can render
};

export function ProductTile({ title, price, seller, onAddToCart }: ProductTileProps) {
  return (
    <article>
      <h3>{title}</h3>
      <p>₹{price}</p>
      <button onClick={() => onAddToCart(seller.id)}>Add</button>
    </article>
  );
}

// <ProductTile title="Mouse" price="799" ... />   ← compile error: string is not a number
```

---

## 🟠 Real App Integration

In the Next.js App Router, props to **Client Components** must be **serializable** when they cross the server-client boundary. You can pass strings, numbers, booleans, arrays, plain objects, `Date` (in React 19 / Next 15 it works), and Server Actions. You cannot pass ordinary functions, class instances or Symbols from a Server Component to a Client Component. Page-level props (`params`, `searchParams`) are also **Promises** in Next.js 15.

```tsx
// app/products/[id]/page.tsx — Server Component (Next.js 15)
import AddButton from './AddButton';          // a 'use client' component

type PageProps = {
  params: Promise<{ id: string }>;            // Next.js 15: params is a Promise (Next 14: plain object)
};

export default async function Page({ params }: PageProps) {
  const { id } = await params;                // await it before use
  return (
    <AddButton
      productId={id}                          // string: serializable ✅
      price={799}                             // number ✅
      // onClick={() => {}}                   // ❌ plain function cannot cross the boundary
    />
  );
}
```

```tsx
// app/products/[id]/AddButton.tsx
'use client';                                  // this component runs in the browser

export default function AddButton({ productId, price }: { productId: string; price: number }) {
  return <button onClick={() => console.log('add', productId)}>Add ₹{price}</button>; // handler defined inside the client file
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating props
✅ **Correct:** Treat props as read-only; copy before changing

```jsx
// Wrong: mutates the parent's array, causes confusing bugs
function Sorted({ items }) {
  items.sort();                                  // ❌ mutates the prop in place
  return <ul>{items.map((i) => <li key={i}>{i}</li>)}</ul>;
}

// Right: sort a copy
function SortedFixed({ items }) {
  const sorted = [...items].sort();              // ✅ new array
  return <ul>{sorted.map((i) => <li key={i}>{i}</li>)}</ul>;
}
```

❌ **Mistake 2:** Passing a string where a number or boolean is needed
✅ **Correct:** Use curly braces for non-string values

```jsx
// Wrong: "5" is a STRING, "false" is a truthy STRING
const bad = [
  <Rating value="5" />,                // ❌ value is the string "5"
  <Modal open="false" />,              // ❌ "false" is truthy, so the modal opens
];

// Right
const good = [
  <Rating value={5} />,                // ✅ number
  <Modal open={false} />,              // ✅ boolean
];
```

❌ **Mistake 3:** Calling the function while passing it (runs on every render)
✅ **Correct:** Pass a reference, or wrap in an arrow function when you need arguments

```jsx
// Wrong: handleDelete(id) runs immediately during render, and its return value is passed
const bad = <button onClick={handleDelete(id)}>Delete</button>;        // ❌

// Right
const good = <button onClick={() => handleDelete(id)}>Delete</button>;  // ✅ runs on click
```

---

## 🧠 Tricky Interview Question

```jsx
function Child({ user, tags }) {
  console.log('Child render');
  return <p>{user.name} {tags.length}</p>;
}

const MemoChild = React.memo(Child);

function Parent() {
  const [n, setN] = React.useState(0);
  return (
    <>
      <button onClick={() => setN(n + 1)}>{n}</button>
      <MemoChild user={{ name: 'Asha' }} tags={['a', 'b']} />
    </>
  );
}
```
Question: Does `MemoChild` skip rendering when you click the button?

**Answer:** **No, it re-renders on every click.** `React.memo` compares props with `Object.is` (shallow). Each render of `Parent` creates a NEW object `{ name: 'Asha' }` and a NEW array `['a', 'b']`. They look the same but have different references, so the props are "changed". Fix by moving the constants outside the component, or by wrapping them in `useMemo` (or let the React Compiler do it). This shows that prop types are not only about validation: object/array/function props affect re-render behavior.

---

## ⚫ Interview Questions + Answers

Q1: What types of values can be passed as props?
A1: Any JavaScript value: string, number, boolean, `null`, `undefined`, array, object, function, JSX element, even another component (as `Icon={StarIcon}`). Non-string values need `{}` in JSX.

Q2: Are props mutable?
A2: No. Props are read-only; a component must never change its own props. To change data, the parent passes new props, or the child keeps its own state and calls a callback prop to ask the parent to update.

Q3: How do you validate props in React?
A3: Modern projects use TypeScript for compile-time checks. For plain JavaScript you can use the `prop-types` package (runtime warnings in development), JSDoc with editor type checking, or manual guards. Note that React 19 removed `propTypes` checking from React itself, so the package no longer validates automatically on React 19.

Q4: What is `props.children`, and what type is it?
A4: `children` is the content between a component's opening and closing tags. It can be a single element, a string, an array of nodes, a function (render prop), or `undefined`. In TypeScript it is typed as `ReactNode`.

Q5: Why does a memoized component still re-render when I pass an object or function prop?
A5: Because a new object/function is created on each parent render, and `memo` does a shallow reference comparison. Stabilize it with a module constant, `useMemo`, `useCallback`, or the React Compiler.

---

## 🔷 When to Use + When Not to Use
✅ **Validate props when:**
- A component is shared by many people or is part of a design system
- Data comes from an API you do not control
- Required versus optional props need to be clear to teammates

❌ **Avoid heavy validation when:**
- It is a tiny private component used in one place with TypeScript already in place
- You add runtime checks in a hot render path for trusted data (cost without benefit)
- You duplicate the same rules in PropTypes and TypeScript (pick one source of truth)

---

## 📊 Visual Diagram

```
  PARENT                                              CHILD
  ┌───────────────────────────────┐                  ┌──────────────────────────┐
  │ <ProductTile                  │   props object   │ function ProductTile(p) {│
  │    title="Mouse"       string │ ───────────────▶ │   p.title   string       │
  │    price={799}         number │   (read-only)    │   p.price   number       │
  │    isPrime             boolean│                  │   p.seller  object       │
  │    seller={{...}}      object │                  │   p.onAdd   function     │
  │    onAdd={fn}          function                  │   p.badge   element      │
  │    badge={<B/>}        element│                  │ }                        │
  └───────────────────────────────┘                  └────────────┬─────────────┘
                                                                  │ validate with
                                                  ┌───────────────┼─────────────────┐
                                                  ▼               ▼                 ▼
                                             TypeScript       PropTypes        manual guard
                                          (editor/build)   (dev console)     (throw / fallback)

  Data flows DOWN only. A child asks for changes by calling a function prop UP.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Props | Read-only inputs to a component | Component के read-only inputs |
| Prop validation | Checking prop type and shape | Prop का type और shape जाँचना |
| TypeScript | Typed JavaScript checked at build time | Build समय पर check होने वाला typed JavaScript |
| PropTypes | Runtime prop checker library | Runtime पर props जाँचने वाली library |
| Required prop | Prop the component cannot work without | जिसके बिना component काम न करे |
| Optional prop | Prop with a default or safe fallback | जिसका default या fallback हो |
| Serializable | Can be converted to plain data (JSON-like) | Plain data में बदली जा सकने वाली value |
| Callback prop | Function prop used to talk to the parent | Parent से बात करने वाला function prop |

---

## ⚡ 3-Line Summary
**English:**
1. Props can be any value (string, number, boolean, array, object, function, element) and are read-only.
2. Validate them with TypeScript (best), PropTypes, or manual guards so wrong data fails early.
3. Object, array and function props are new references each render, which matters for `memo`; in Next.js, server-to-client props must be serializable.

**Hindi:**
1. Props में कोई भी value (string, number, boolean, array, object, function, element) हो सकती है और वे read-only हैं।
2. उन्हें TypeScript (सबसे अच्छा), PropTypes या manual guards से validate करो ताकि गलत data जल्दी पकड़ा जाए।
3. Object, array और function props हर render पर नए reference होते हैं, जो `memo` के लिए मायने रखता है; Next.js में server से client को जाने वाले props serializable होने चाहिए।

---

## ➡️ Next Topic
**17. PropTypes Library** — runtime पर props जाँचने वाली `prop-types` library को detail में देखो: सारे validators, `shape`, `oneOf`, `isRequired`, और React 19 में उसका क्या हुआ।
