# 31. React Fragments (<> </>)
# हिंदी में: React Fragments — बिना Extra DOM Node के कई Elements Return करना

---

## 🔵 Simple Definition (English)
A **Fragment** lets a component return several elements without adding an extra wrapper node to the DOM. The short syntax is `<> ... </>`, and the long syntax is `<React.Fragment key="x"> ... </React.Fragment>`, which is the only one that accepts a `key`.

## 🔵 सरल परिभाषा (Hindi)
**Fragment** एक component को कई elements return करने देता है, बिना DOM में extra wrapper node जोड़े। Short syntax `<> ... </>` है, और long syntax `<React.Fragment key="x"> ... </React.Fragment>` है, जो `key` स्वीकार करने वाला अकेला रूप है।

---

## 🔴 Problem it Solves

A component must return **one** root element. The old fix was wrapping everything in a `<div>`, but extra divs break HTML structure in many places: a `<tr>` can only contain `<td>`, a `<ul>` only `<li>`, a `<dl>` needs `<dt>/<dd>` pairs, and Flexbox/Grid layouts are disturbed when a wrapper div sits between the container and its children. Extra nodes also make the DOM bigger (slightly slower, harder to style and debug).

```jsx
// PROBLEM 1: two siblings, no single root → SyntaxError
function Bad() {
  // ❌ SyntaxError: Adjacent JSX elements must be wrapped in an enclosing tag
  // return (
  //   <h1>Title</h1>
  //   <p>Text</p>
  // );
}

// PROBLEM 2: a wrapper div creates INVALID HTML inside a table
function Columns() {
  return <div><td>Name</td><td>Price</td></div>;   // ❌ <div> inside <tr> is invalid
}

// SOLUTION: Fragment, no extra DOM node
function ColumnsFixed() {
  return <><td>Name</td><td>Price</td></>;          // ✅ renders only the two <td>
}
```

## 🔴 यह क्यों बना? (Hindi)
Component को **एक** root element return करना पड़ता है। पुराना उपाय सब कुछ `<div>` में लपेटना था, लेकिन extra div कई जगह HTML structure तोड़ देता है: `<tr>` में सिर्फ `<td>` हो सकता है, `<ul>` में सिर्फ `<li>`, `<dl>` में `<dt>/<dd>` जोड़ी चाहिए, और Flexbox/Grid layout बिगड़ जाते हैं जब container और उसके children के बीच wrapper div आ जाए। Extra nodes से DOM भी बड़ा होता है (थोड़ा धीमा, style और debug करना कठिन)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component needs to return multiple siblings (h1 + p, or td + td)
Step 2 → Wrap them in <> ... </>   (Babel/TS turns it into React.Fragment)
Step 3 → React builds the element tree, with the Fragment as the root "grouping" node
Step 4 → During commit, React inserts the children directly into the parent DOM node
Step 5 → The browser DOM has NO node for the Fragment (it exists only in React's tree)
Step 6 → Need a key (list of groups)? Use <Fragment key={id}> from 'react' (short syntax has no key)

SYNTAX
  <> ...children... </>                      short, no props allowed
  <React.Fragment key={id}> ... </...>       long, supports key (and nothing else)
  return [<li key="a"/>, <li key="b"/>]      array form also works (keys required)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Component को कई siblings return करने हैं (h1 + p, या td + td)
Step 2 → उन्हें <> ... </> में लपेटो   (Babel/TS इसे React.Fragment बना देता है)
Step 3 → React element tree बनाता है, जिसमें Fragment root "grouping" node है
Step 4 → Commit के समय React children को सीधे parent DOM node में डालता है
Step 5 → Browser के DOM में Fragment का कोई node नहीं होता (वह सिर्फ React के tree में है)
Step 6 → Groups की list में key चाहिए? 'react' से <Fragment key={id}> इस्तेमाल करो (short syntax में key नहीं)

SYNTAX
  <> ...children... </>                      short, props की अनुमति नहीं
  <React.Fragment key={id}> ... </...>       long, key स्वीकार करता है (और कुछ नहीं)
  return [<li key="a"/>, <li key="b"/>]      array form भी चलता है (keys ज़रूरी)
```

---

## 🟡 Real World Example
**Flipkart order table:** Each order row is a component that returns four `<td>` cells (image, title, price, status). A `<div>` wrapper would put a div inside `<tr>`, which is invalid HTML and shows hydration warnings in Next.js. A Fragment returns the cells directly. Another case is the Swiggy menu: each category renders a heading plus a list of dishes, and a `<Fragment key={category.id}>` groups the `<h3>` and `<ul>` per category without a wrapper that would break the sticky heading CSS.

## 🟡 Real Example Hindi mein
**Flipkart order table:** हर order row एक component है जो चार `<td>` cells (image, title, price, status) return करता है। `<div>` wrapper से `<tr>` में div आ जाता, जो invalid HTML है और Next.js में hydration warning देता। Fragment cells को सीधे return करता है। दूसरा उदाहरण Swiggy menu है: हर category एक heading और dishes की list render करती है, और `<Fragment key={category.id}>` हर category के `<h3>` और `<ul>` को ऐसे wrapper के बिना group करता है जो sticky heading के CSS को तोड़ देता।

---

## 💻 Code Example — Basic

```jsx
// Fragment basics: short syntax, long syntax and a valid table
import { Fragment } from 'react';                    // needed only for the long form
import { createRoot } from 'react-dom/client';

// Short syntax: two siblings, no wrapper div in the DOM
function Intro() {
  return (
    <>
      <h1>Welcome to FoodApp</h1>                     {/* sibling 1 */}
      <p>Order your favourite dishes.</p>             {/* sibling 2 */}
    </>
  );
}

// Valid table markup: the component returns <td> cells directly
function OrderCells({ order }) {
  return (
    <>
      <td>{order.title}</td>                          {/* cell 1 */}
      <td>₹{order.price}</td>                         {/* cell 2 */}
      <td>{order.status}</td>                         {/* cell 3 */}
    </>
  );
}

// Long syntax: only this form can take a key
function Glossary({ terms }) {
  return (
    <dl>
      {terms.map((t) => (
        <Fragment key={t.id}>                         {/* key goes on the Fragment, not the children */}
          <dt>{t.word}</dt>                           {/* <dt>/<dd> must stay direct children of <dl> */}
          <dd>{t.meaning}</dd>
        </Fragment>
      ))}
    </dl>
  );
}

function App() {
  const orders = [{ id: 1, title: 'Biryani', price: 250, status: 'Delivered' }];
  const terms = [{ id: 'a', word: 'ETA', meaning: 'Estimated time of arrival' }];
  return (
    <>
      <Intro />
      <table><tbody>
        {orders.map((o) => <tr key={o.id}><OrderCells order={o} /></tr>)}
      </tbody></table>
      <Glossary terms={terms} />
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Real world: grouped menu with sticky headings, plus a conditional Fragment and a helper component
import { Fragment, useState } from 'react';

const MENU = [
  { id: 'c1', name: 'Starters', dishes: [{ id: 1, name: 'Paneer Tikka', price: 220 }] },
  { id: 'c2', name: 'Main Course', dishes: [{ id: 2, name: 'Dal Makhani', price: 260 }, { id: 3, name: 'Biryani', price: 310 }] },
];

// A component that returns a Fragment: heading + list stay siblings in the DOM
function MenuCategory({ category }) {
  return (
    <>
      <h3 style={{ position: 'sticky', top: 0, background: '#fff' }}>{category.name}</h3> {/* sticky works because parent is the scroll container */}
      <ul>
        {category.dishes.map((d) => (
          <li key={d.id}>{d.name} - ₹{d.price}</li>
        ))}
      </ul>
    </>
  );
}

export default function Menu() {
  const [vegOnly, setVegOnly] = useState(false);       // some UI state

  return (
    <section style={{ display: 'grid', gap: 8 }}>      {/* grid children = h3/ul directly, no extra div */}
      <label>
        <input type="checkbox" checked={vegOnly} onChange={(e) => setVegOnly(e.target.checked)} />
        Veg only
      </label>

      {MENU.map((c) => (
        <Fragment key={c.id}>                          {/* keyed Fragment per category */}
          <MenuCategory category={c} />
        </Fragment>
      ))}

      {vegOnly && (
        <>                                             {/* conditional group of siblings */}
          <hr />
          <small>Showing vegetarian dishes only</small>
        </>
      )}
    </section>
  );
}
```

---

## 🟠 Real App Integration

In Next.js, Fragments appear everywhere: layouts, pages and Server Components. They matter most for **hydration**: if the server HTML and the client HTML differ (for example invalid nesting like `<div>` inside `<tr>` or `<p>` inside `<p>`), React logs a hydration error. Fragments keep markup valid. Note that the root `layout.jsx` must return `<html>` and `<body>`, not a Fragment, in the App Router.

```jsx
// app/orders/page.jsx — Server Component (Next.js 14/15)
import { Fragment } from 'react';

async function getOrders() {
  const res = await fetch('https://api.example.com/orders', { cache: 'no-store' });
  return res.json();                                  // [{ id, title, items: [...] }]
}

export default async function OrdersPage() {
  const orders = await getOrders();                   // fetched on the server
  return (
    <table>
      <tbody>
        {orders.map((o) => (
          <Fragment key={o.id}>                       {/* two <tr> per order, no wrapper */}
            <tr><th colSpan={2}>{o.title}</th></tr>
            {o.items.map((i) => (
              <tr key={i.id}><td>{i.name}</td><td>₹{i.price}</td></tr>
            ))}
          </Fragment>
        ))}
      </tbody>
    </table>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using the short syntax `<>` when you need a `key`
✅ **Correct:** Use `<Fragment key={...}>` imported from `react`

```jsx
// Wrong: short syntax cannot take a key, so React warns "Each child in a list should have a unique key"
{items.map((i) => (
  <>                                 {/* ❌ no place to put the key */}
    <dt>{i.k}</dt><dd>{i.v}</dd>
  </>
))}

// Right
{items.map((i) => (
  <Fragment key={i.id}>              {/* ✅ key on the Fragment */}
    <dt>{i.k}</dt><dd>{i.v}</dd>
  </Fragment>
))}
```

❌ **Mistake 2:** Adding a wrapper `<div>` that breaks HTML validity or CSS layout
✅ **Correct:** Use a Fragment

```jsx
// Wrong: div inside <tr>, and it breaks the flex layout
function BadRow() {
  return <tr><div><td>A</td><td>B</td></div></tr>;       // ❌ invalid HTML (div inside tr)
}
function BadWrapper() {
  return <div><Item /><Item /></div>;                    // ❌ extra div between the flex container and items
}

// Right
function GoodRow() {
  return <tr><><td>A</td><td>B</td></></tr>;             // ✅ valid HTML
}
function GoodWrapper() {
  return <><Item /><Item /></>;                          // ✅ items are direct flex children
}
```

❌ **Mistake 3:** Putting a Fragment where you needed a real element (for example to attach `className`, a ref or an event handler)
✅ **Correct:** Use a real element when you need DOM features

```jsx
// Wrong: Fragment cannot take className, ref or onClick
const bad = (
  <React.Fragment className="card" onClick={open}>      {/* ❌ React warns: invalid props on Fragment */}
    <h3>Title</h3>
  </React.Fragment>
);

// Right
const good = (
  <div className="card" onClick={open}>                  {/* ✅ a real DOM node is needed here */}
    <h3>Title</h3>
  </div>
);
```

---

## 🧠 Tricky Interview Question

```jsx
function Parent() {
  const [flag, setFlag] = React.useState(true);
  return (
    <>
      <button onClick={() => setFlag(!flag)}>Toggle</button>
      {flag ? (
        <>
          <input defaultValue="" />
        </>
      ) : (
        <div>
          <input defaultValue="" />
        </div>
      )}
    </>
  );
}
```
Question: The user types "hello" in the input and clicks Toggle. Is the text kept?

**Answer:** **No, the input is reset.** React compares element **types** at the same position in the tree. In one branch the position holds a Fragment, in the other a `div`. Different types mean React unmounts the old subtree and mounts a new one, so the input state (and DOM node) is lost. If both branches used the same wrapper type (both `<div>`, or both Fragment) at that position, the input would be preserved. Fragments are invisible in the DOM but still count in React's reconciliation.

---

## ⚫ Interview Questions + Answers

Q1: What is a Fragment and why do we need it?
A1: A built-in React component that groups children without creating a DOM node. It is needed because components must return a single root, and an extra `div` can break valid HTML (tables, lists) or CSS layouts (flex, grid).

Q2: What is the difference between `<>` and `<React.Fragment>`?
A2: They are the same thing. `<>` is shorthand, but it cannot take any props. `<React.Fragment>` can take a `key` (and only a `key`), so use it when rendering lists of groups. In older toolchains (before Babel 7) the shorthand was not supported.

Q3: Does a Fragment affect performance?
A3: Slightly in a good way: fewer DOM nodes means less memory, faster layout and simpler CSS selectors. The Fragment itself is only a React object that disappears at commit, so it costs almost nothing.

Q4: Can a Fragment have attributes, refs or events?
A4: No. Only `key` is allowed (and in newer React versions, an experimental ref support exists for `Fragment` refs, version-dependent). For `className`, `onClick`, ref and styling, use a real element.

Q5: Can a component return an array or a string instead of a Fragment?
A5: Yes. Since React 16 a component can return an array (with keys), a string, a number, `null` or a portal. A Fragment is just the cleanest way to return multiple JSX elements.

---

## 🔷 When to Use + When Not to Use
✅ **Use a Fragment when:**
- A component returns siblings that must be direct children of the parent (table cells, list items, grid or flex items)
- You render a list of groups and need a `key` (`<Fragment key>`)
- You only need to group children and no wrapper styling or events

❌ **Avoid a Fragment when:**
- You need a wrapper to style, position, attach a ref, or handle an event (use `div`, `section`, etc.)
- You wrap one single child (a Fragment around a single element is noise)
- You need accessibility landmarks or semantic grouping (use `section`, `fieldset`)

---

## 📊 Visual Diagram

```
  JSX                                     React tree                    Browser DOM
  ─────────────────────                   ──────────────                ──────────────
  function Row() {                         Row                           <tr>
    return (                                └─ Fragment (virtual)          <td>Biryani</td>
      <>                                         ├─ td                     <td>₹250</td>
        <td>Biryani</td>                         └─ td                     <td>Delivered</td>
        <td>₹250</td>                                                      <td>...</td>
      </>                                  (Fragment exists here)         </tr>
    );                                                                   (NO Fragment node here)
  }
  
  With <div> wrapper:                      <tr><div><td/><td/></div></tr>   ❌ invalid HTML
  With Fragment:                           <tr><td/><td/></tr>              ✅ valid HTML

  Same position, different types (Fragment ↔ div) → React remounts → state is lost
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fragment | Groups children, adds no DOM node | Children को group करता है, DOM node नहीं जोड़ता |
| Short syntax `<>` | Fragment without props | बिना props वाला Fragment |
| Keyed Fragment | `<Fragment key>` for lists | Lists के लिए `<Fragment key>` |
| Wrapper div | Extra `div` used only to group | सिर्फ group करने के लिए extra `div` |
| Sibling | Elements at the same level | एक ही level के elements |
| Hydration | Attaching React to server HTML | Server HTML पर React जोड़ना |
| Reconciliation | Comparing old and new trees | पुराने और नए tree की तुलना |
| Single root | Rule: a component returns one top node | नियम: component एक ही top node return करे |

---

## ⚡ 3-Line Summary
**English:**
1. A Fragment (`<>...</>`) groups several elements without adding a DOM node.
2. Use `<Fragment key={id}>` for keyed lists, and keep table, list and grid markup valid.
3. Fragments cannot take className, refs or events, and switching between a Fragment and a div at the same position remounts the subtree.

**Hindi:**
1. Fragment (`<>...</>`) कई elements को बिना DOM node जोड़े group करता है।
2. Keyed lists के लिए `<Fragment key={id}>` इस्तेमाल करो, और table, list व grid का markup valid रखो।
3. Fragment में className, refs या events नहीं लगते, और एक ही जगह Fragment और div के बीच बदलने से subtree फिर से mount होता है।

---

## ➡️ Next Topic
**32. React StrictMode** — Fragment की तरह `<StrictMode>` भी DOM में कुछ नहीं जोड़ता, लेकिन development में आपके code की छिपी गलतियों को पकड़ता है। इसे समझना ज़रूरी है।
