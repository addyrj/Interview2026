# 62. Component Composition
# हिंदी में: Component Composition — Components को जोड़कर Flexible UI बनाना

---

## 🔵 Simple Definition (English)
**Component composition** means building complex UI by combining smaller components, passing content and other components into them through `children` and named props (slots), instead of creating a new component for every variation. React's guidance is to prefer composition over inheritance.

## 🔵 सरल परिभाषा (Hindi)
**Component composition** का मतलब है छोटे components को एक-दूसरे में जोड़कर बड़ा UI बनाना, और `children` या नाम वाले props (slots) से content व दूसरे components अंदर भेजना। हर variation के लिए नया component बनाने की जगह React composition को prefer करता है, inheritance को नहीं।

---

## 🔴 Problem it Solves

Early on, developers reused UI with inheritance (a `FancyButton extends Button`). It becomes hard to manage when you need many combinations of header, footer, icons and actions. The alternative is a single component with a long list of props (`showHeader`, `headerText`, `footerButtons`, `icon`, `iconPosition`...). That list keeps growing, and every new layout needs a new prop. Composition solves this by letting the caller decide what goes inside, while the component decides only the structure.

```jsx
// PROBLEM: prop explosion
<Card
  showHeader
  headerTitle="Order"
  headerIcon={<Icon />}
  showFooter
  footerButtons={['Cancel', 'Track']}
  footerAlign="right"
/>

// SOLUTION: composition with children and slots
<Card
  header={<><Icon /> <h3>Order</h3></>}   // caller decides the header content
  footer={<><button>Cancel</button><button>Track</button></>}
>
  <p>Your order is on the way</p>          // children: main content
</Card>
```

## 🔴 यह क्यों बना? (Hindi)
पहले developers inheritance से UI दोबारा इस्तेमाल करते थे (`FancyButton extends Button`)। Header, footer, icon और actions की कई combinations आने पर यह संभालना मुश्किल हो जाता था। दूसरा रास्ता था एक component जिसमें लंबी props लिस्ट हो (`showHeader`, `headerText`, `footerButtons`, `icon`...), और यह लिस्ट बढ़ती ही जाती थी। Composition में caller तय करता है कि अंदर क्या जाएगा, और component सिर्फ structure तय करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a "container" component that defines the structure (box, layout, spacing)
Step 2 → Accept content through children (the JSX between the tags)
Step 3 → Accept named slots through props (header, footer, actions) as React elements
Step 4 → The caller composes the final UI by choosing what to pass in
Step 5 → For related parts (Tabs.List, Tabs.Panel), share state with context (compound components)
Step 6 → Result: one reusable structure, unlimited content variations, no inheritance

KEY: props can be elements, not only strings and numbers
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक "container" component बनाओ जो structure तय करे (box, layout, spacing)
Step 2 → children के ज़रिए content लो (tags के बीच का JSX)
Step 3 → Props के ज़रिए नाम वाले slots लो (header, footer, actions) जो React elements हों
Step 4 → Caller चुनकर अंतिम UI बनाता है कि अंदर क्या जाए
Step 5 → जुड़े हुए हिस्से (Tabs.List, Tabs.Panel) state को context से share करते हैं (compound components)
Step 6 → नतीजा: एक reusable structure, अनगिनत content variations, बिना inheritance के

KEY: props सिर्फ strings और numbers नहीं, React elements भी हो सकते हैं
```

---

## 🟡 Real World Example
**Zomato restaurant card:** The same `RestaurantCard` appears in search, in "Order again" and in a promoted banner. In search it shows a delivery-time badge, in "Order again" it shows a reorder button, and in the banner it shows an offer tag. Instead of three components or a dozen flags, the card receives `badge`, `actions` and `children` from each screen. The card's layout and styling stay in one place.

## 🟡 Real Example Hindi mein
**Zomato restaurant card:** वही `RestaurantCard` search, "Order again" और promoted banner में आता है। Search में delivery time badge दिखता है, "Order again" में reorder बटन, और banner में offer tag। तीन अलग components या दर्जनों flags बनाने की जगह card हर screen से `badge`, `actions` और `children` लेता है। Card का layout और styling एक ही जगह रहती है।

---

## 💻 Code Example — Basic

```jsx
// Composition basics: a Card container with children and named slots
import { createRoot } from 'react-dom/client';     // React 18/19 root API

function Card({ header, footer, children }) {      // container: decides the structure only
  return (
    <div style={{ border: '1px solid #ccc', borderRadius: 8, padding: 16 }}> {/* shared look */}
      {header && <header style={{ fontWeight: 'bold' }}>{header}</header>}   {/* optional slot */}
      <section>{children}</section>                 {/* main content from the caller */}
      {footer && <footer style={{ marginTop: 12 }}>{footer}</footer>}       {/* optional slot */}
    </div>
  );
}

function App() {
  return (
    <div>
      <Card                                         // first use: order card
        header={<span>Order #ZOM-101</span>}        // header slot receives an element
        footer={<button>Track order</button>}       // footer slot receives a button element
      >
        <p>Your biryani is being prepared.</p>      {/* children: plain JSX content */}
      </Card>

      <Card header="Offer">                         {/* second use: strings work for slots too */}
        <p>Flat 20% off on your next order.</p>     {/* different content, same structure */}
      </Card>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount the composed UI
```

## 💻 Code Example — Advanced

```jsx
// Compound components: Tabs.Root shares state with Tabs.Tab and Tabs.Panel through context
import { createContext, useContext, useState, useId } from 'react'; // hooks + context
import { createRoot } from 'react-dom/client';                       // React 18/19 root

const TabsContext = createContext(null);             // shared state for the whole Tabs group

// Root: owns the active tab and provides it to all children
function Tabs({ defaultValue, children }) {
  const [active, setActive] = useState(defaultValue); // which tab is selected
  const baseId = useId();                             // unique id prefix (safe with SSR)
  const value = { active, setActive, baseId };        // object shared through context
  return (
    <TabsContext.Provider value={value}>              {/* children can read active state */}
      <div role="tablist">{children}</div>            {/* tablist accessibility role */}
    </TabsContext.Provider>
  );
}

// Tab button: reads the group state, does not need any props about other tabs
function Tab({ value, children }) {
  const ctx = useContext(TabsContext);                // read the nearest Tabs group
  if (!ctx) throw new Error('Tab must be used inside <Tabs>'); // guard against misuse
  const selected = ctx.active === value;              // is this tab the active one?
  return (
    <button
      role="tab"                                      // accessibility role
      aria-selected={selected}                        // screen readers announce the state
      id={`${ctx.baseId}-tab-${value}`}               // unique id for aria-labelledby
      onClick={() => ctx.setActive(value)}            // change the active tab on click
      style={{ fontWeight: selected ? 'bold' : 'normal' }}
    >
      {children}
    </button>
  );
}

// Panel: shows its content only when its value is active
function Panel({ value, children }) {
  const { active, baseId } = useContext(TabsContext); // read active state from the group
  if (active !== value) return null;                  // hidden panels render nothing
  return (
    <div role="tabpanel" aria-labelledby={`${baseId}-tab-${value}`}> {/* linked to its tab */}
      {children}
    </div>
  );
}

// Attach the sub-components to the root: a common compound-component API
Tabs.Tab = Tab;                                        // usage: <Tabs.Tab value="a">
Tabs.Panel = Panel;                                    // usage: <Tabs.Panel value="a">

function RestaurantInfo() {                            // example usage with three tabs
  return (
    <Tabs defaultValue="menu">                         {/* menu is open by default */}
      <Tabs.Tab value="menu">Menu</Tabs.Tab>           {/* tab button 1 */}
      <Tabs.Tab value="reviews">Reviews</Tabs.Tab>     {/* tab button 2 */}
      <Tabs.Panel value="menu"><p>Biryani, Dosa</p></Tabs.Panel>      {/* shown first */}
      <Tabs.Panel value="reviews"><p>4.5 stars</p></Tabs.Panel>       {/* hidden until clicked */}
    </Tabs>
  );
}

createRoot(document.getElementById('root')).render(<RestaurantInfo />);
```

---

## 🟠 Real App Integration

Composition works well with Server Components. A Server Component can render a Client Component and pass it as a slot, and the layout stays on the server. Only the small interactive button ships JavaScript to the browser.

```jsx
// app/components/Card.jsx (Server Component: no 'use client', no hooks, pure structure)
export default function Card({ header, footer, children }) {
  return (
    <div className="card">
      <header>{header}</header>                         {/* slot: any element from the caller */}
      <section>{children}</section>                     {/* main content */}
      <footer>{footer}</footer>                         {/* slot: actions */}
    </div>
  );
}
```

```jsx
// app/restaurants/[slug]/page.jsx (Server Component)
import Card from '@/app/components/Card';               // server-rendered structure
import AddToCartButton from './AddToCartButton';        // 'use client' component with onClick
import { getRestaurant } from '@/lib/restaurants';      // your data layer (hypothetical helper)

export default async function Page({ params }) {
  const { slug } = await params;                        // Next.js 15+: params is a Promise
  const restaurant = await getRestaurant(slug);         // fetched on the server
  return (
    <Card
      header={<h2>{restaurant.name}</h2>}              // slot from the server page
      footer={<AddToCartButton id={restaurant.id} />}   // Client Component passed as a slot
    >
      <p>{restaurant.cuisine}</p>                       {/* children: plain server content */}
    </Card>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating a new component inside another component's render (it remounts and loses state)
✅ **Correct:** Define components at module level, and pass elements or functions as props

```jsx
// Wrong: Label is a NEW function type on every render → React unmounts and remounts it
function Parent() {
  function Label() {                                // ❌ defined inside the render function
    const [clicks, setClicks] = useState(0);        // state resets every time Parent renders
    return <button onClick={() => setClicks(c => c + 1)}>{clicks}</button>;
  }
  return <Label />;
}

// Right: define Label at module level, so its identity is stable
function Label() {                                  // ✅ module level
  const [clicks, setClicks] = useState(0);          // state survives parent re-renders
  return <button onClick={() => setClicks(c => c + 1)}>{clicks}</button>;
}
function Parent() { return <Label />; }
```

❌ **Mistake 2:** Passing a component as a string name and expecting React to resolve it
✅ **Correct:** Pass the component itself, or pass an element with `icon={<Icon />}`

```jsx
// Wrong: a string is not a component
<Card icon="StarIcon" />                            // ❌ React renders a <StarIcon> HTML tag

// Right: pass the element or the component itself
<Card icon={<StarIcon />} />                        // ✅ element as a slot
<Card Icon={StarIcon} />                            // ✅ component reference, rendered by Card
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [n, setN] = useState(0);                   // parent state

  function Label() {                               // defined INSIDE App → new type each render
    const [clicks, setClicks] = useState(0);       // Label's own state
    console.log('Label render, clicks =', clicks);
    useEffect(() => { setClicks(5); }, []);        // Label sets clicks to 5 after mount
    return <p>{clicks}</p>;
  }

  useEffect(() => { setN(1); }, []);               // App re-renders once after mount
  return <div><Label /></div>;
}

createRoot(document.getElementById('root')).render(<App />);
```
**Answer:** The output is:
```
Label render, clicks = 0
Label render, clicks = 0
Label render, clicks = 5
```
After the first commit, two updates are queued: the first `Label`'s `setClicks(5)` and `App`'s `setN(1)`. When `App` re-renders, `Label` is a new function object, so React sees a different component type. It unmounts the old `Label` (discarding its `clicks = 5` update together with its state) and mounts a fresh one. That fresh instance renders with `clicks = 0` (the second line), then its own mount effect runs `setClicks(5)` and it renders `5` (the third line). The state loss is caused by defining the component inside the parent. Moving `Label` to module level keeps the same instance, so the output would be `0` then `5` with only one `0` line.

---

## ⚫ Interview Questions + Answers

Q1: What is component composition?
A1: Building UI by combining components and passing content into them through `children` and props that hold elements (slots). The container defines the structure, the caller decides the content.

Q2: Why does React prefer composition over inheritance?
A2: Inheritance couples a child class to the internals of its parent and gets hard to manage with many variations. Composition uses plain functions and props, so each part is independent, easy to test and easy to rearrange. React's documentation explicitly recommends it.

Q3: What is the difference between `children` and a named slot prop?
A3: `children` is the content placed between the opening and closing tags. A named prop such as `footer` is a labeled slot. Use `children` for the main content and named props when the component has several distinct places for content.

Q4: What are compound components?
A4: A group of components that work together and share state, usually through context. The root holds the state (for example, the active tab) and the parts (`Tabs.Tab`, `Tabs.Panel`) read it. The caller writes a clear, declarative tree, and internal wiring stays hidden.

Q5: Why must you avoid defining a component inside another component?
A5: Each render creates a new function object, which React treats as a different component type. React then unmounts and remounts the subtree, which resets all of its state and DOM. Define components at module level.

---

## 🔷 When to Use + When Not to Use
✅ **Use composition when:**
- Several variations share the same structure (cards, modals, layouts, lists)
- Callers need to decide the content of parts of the UI
- You are building a reusable design system component (tabs, menus, dialogs)

❌ **Avoid composition when:**
- The component has one fixed structure with no variation (just write it directly)
- You are wrapping a single element for no reason (an extra layer adds noise)
- You create components inside other components just to share logic (use a custom hook instead)

---

## 📊 Visual Diagram

```
  Card (container: defines the STRUCTURE)
  ┌───────────────────────────────────────┐
  │ header slot   ← <span>Order #ZOM-101</span>
  │ ─────────────────────────────────────  │
  │ children      ← <p>Your biryani...</p> │
  │ ─────────────────────────────────────  │
  │ footer slot   ← <button>Track</button> │
  └───────────────────────────────────────┘

  Compound components (shared state through context):

  <Tabs defaultValue="menu">          ← owns activeTab state (Provider)
     ├── <Tabs.Tab value="menu" />    ← reads activeTab, sets it on click
     ├── <Tabs.Tab value="reviews" /> ← reads activeTab, sets it on click
     ├── <Tabs.Panel value="menu" />    ← renders only when activeTab === "menu"
     └── <Tabs.Panel value="reviews" /> ← renders only when activeTab === "reviews"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Composition | Building UI by combining components | Components को जोड़कर UI बनाना |
| Inheritance | Reusing code by extending a class | Class extend करके code दोबारा इस्तेमाल |
| children | Content placed between component tags | Component tags के बीच का content |
| Slot | Named prop that accepts an element | Element लेने वाला नाम का prop |
| Container | Component that defines structure | Structure तय करने वाला component |
| Compound component | Group of parts sharing state | State share करने वाले जुड़े हुए components |
| Prop explosion | Too many props on one component | एक component पर बहुत सारे props |
| Remount | Unmount and mount again, losing state | दोबारा mount होना, state खोना |

---

## ⚡ 3-Line Summary
**English:**
1. Composition builds UI from parts: containers define structure, callers provide content through `children` and slots.
2. It replaces both inheritance and long prop lists, and keeps components flexible and independent.
3. Never define components inside other components (they remount), and use context for compound component state.

**Hindi:**
1. Composition में containers structure तय करते हैं, और callers `children` व slots से content देते हैं।
2. यह inheritance और लंबी props लिस्ट दोनों की जगह लेता है, और components को flexible व independent रखता है।
3. Components को दूसरे components के अंदर कभी न बनाओ (वे remount होते हैं), और compound components की state के लिए context इस्तेमाल करो।

---

## ➡️ Next Topic
**63. Children Prop** — `props.children` क्या है, `React.Children` utilities कैसे काम करती हैं, और single vs multiple children को कैसे handle करें। Composition की सबसे ज़रूरी building block यही है।
