# 17. PropTypes Library
# हिंदी में: PropTypes Library — Runtime पर Props की जाँच

---

## 🔵 Simple Definition (English)
**PropTypes** is the `prop-types` npm package that checks the type and shape of a component's props at runtime and prints a console warning in development when something is wrong. It does not stop your app. Since React 19, React no longer runs these checks by itself, so TypeScript is the modern choice.

## 🔵 सरल परिभाषा (Hindi)
**PropTypes** `prop-types` नाम का npm package है जो runtime पर component के props का type और shape जाँचता है और development में कुछ गलत होने पर console में warning छापता है। यह आपके app को रोकता नहीं है। React 19 से React खुद ये checks नहीं चलाता, इसलिए आज TypeScript बेहतर विकल्प है।

---

## 🔴 Problem it Solves

Plain JavaScript has no way to say "this prop must be a number". Before TypeScript became popular, React shipped `React.PropTypes` (React 0.x to 15). In 15.5 it was moved to the separate `prop-types` package. It solved the problem of documenting and checking component contracts without a compiler: a new teammate can open the component and see exactly what props it expects, and wrong data produces a readable warning with the component name.

```jsx
// PROBLEM: this fails silently or crashes far from the real mistake
<OrderRow id="42" total="not-a-number" items="biryani" />
// Inside: items.map is not a function → crash with a confusing stack trace

// SOLUTION: PropTypes warns at the call site in development:
// "Warning: Failed prop type: Invalid prop `items` of type `string` supplied to `OrderRow`,
//  expected an array."
```

## 🔴 यह क्यों बना? (Hindi)
Plain JavaScript में यह कहने का तरीका नहीं कि "यह prop number होना चाहिए"। TypeScript के लोकप्रिय होने से पहले React के साथ `React.PropTypes` आता था (React 0.x से 15 तक)। 15.5 में इसे अलग `prop-types` package में डाल दिया गया। इसने बिना compiler के component के contract को document और check करने की समस्या हल की: नया teammate component खोलकर देख सकता है कि कौन-से props चाहिए, और गलत data पर component के नाम के साथ पढ़ने लायक warning मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install:  npm install prop-types
Step 2 → Import:   import PropTypes from 'prop-types'
Step 3 → Attach a static object to the component:  Card.propTypes = { ... }
Step 4 → Each key maps a prop name to a validator: PropTypes.string, .number, .bool, .func ...
Step 5 → Add .isRequired to make a prop mandatory
Step 6 → Compose: arrayOf(...), shape({...}), oneOf([...]), oneOfType([...]), node, element
Step 7 → In React ≤ 18 DEV mode, React calls checkPropTypes during render → console.error on mismatch
Step 8 → In PRODUCTION the checks are skipped. In React 19 the built-in check is removed:
         call PropTypes.checkPropTypes() yourself, or use TypeScript instead.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Install:  npm install prop-types
Step 2 → Import:   import PropTypes from 'prop-types'
Step 3 → Component पर static object जोड़ो:  Card.propTypes = { ... }
Step 4 → हर key prop के नाम को validator से जोड़ती है: PropTypes.string, .number, .bool, .func ...
Step 5 → Prop को ज़रूरी बनाने के लिए .isRequired जोड़ो
Step 6 → Combine करो: arrayOf(...), shape({...}), oneOf([...]), oneOfType([...]), node, element
Step 7 → React ≤ 18 के DEV mode में React render के दौरान checkPropTypes चलाता है → mismatch पर console.error
Step 8 → PRODUCTION में checks skip होते हैं। React 19 में built-in check हट गया है:
         खुद PropTypes.checkPropTypes() चलाओ, या TypeScript इस्तेमाल करो।
```

---

## 🟡 Real World Example
**Swiggy order summary row:** A legacy JavaScript codebase has an `OrderRow` that receives `id`, `status` (only `'placed'`, `'preparing'`, `'delivered'`), `items` (array of `{ name, qty, price }`) and `onCancel`. When the backend team accidentally sends `status: 'DELIVERED'` in uppercase, the dev console shows a PropTypes warning with the component name, and QA catches the mapping bug in staging.

## 🟡 Real Example Hindi mein
**Swiggy order summary row:** पुराने JavaScript codebase में `OrderRow` को `id`, `status` (सिर्फ `'placed'`, `'preparing'`, `'delivered'`), `items` (`{ name, qty, price }` का array) और `onCancel` मिलते हैं। जब backend team गलती से `status: 'DELIVERED'` (बड़े अक्षरों में) भेजती है, तो dev console में component के नाम के साथ PropTypes warning आती है, और QA staging में mapping bug पकड़ लेती है।

---

## 💻 Code Example — Basic

```jsx
// Basic PropTypes usage
import PropTypes from 'prop-types';                 // npm install prop-types

function MenuItem({ name, price, isVeg, onAdd }) {  // props destructured
  return (
    <li>
      <span>{isVeg ? '🟢' : '🔴'} {name}</span>      {/* veg / non-veg marker */}
      <strong> ₹{price}</strong>                     {/* number */}
      <button onClick={() => onAdd(name)}>Add</button> {/* callback with an argument */}
    </li>
  );
}

MenuItem.propTypes = {                              // static property, not inside the function
  name: PropTypes.string.isRequired,                // must be a string and must be present
  price: PropTypes.number.isRequired,               // must be a number and must be present
  isVeg: PropTypes.bool,                            // optional boolean
  onAdd: PropTypes.func.isRequired,                 // must be a function
};

export default MenuItem;

// <MenuItem name="Paneer Tikka" price="250" onAdd={() => {}} />
// DEV warning (React 18): Invalid prop `price` of type `string` supplied to `MenuItem`, expected `number`.
```

## 💻 Code Example — Advanced

```jsx
// Advanced validators: shape, arrayOf, oneOf, oneOfType, node, custom validator
import PropTypes from 'prop-types';

function OrderRow({ id, status, items, coupon, footer, discount, onCancel }) {
  const total = items.reduce((sum, i) => sum + i.qty * i.price, 0); // sum of lines
  return (
    <section>
      <h4>Order #{id} - {status}</h4>
      <ul>
        {items.map((i) => (
          <li key={i.name}>{i.name} x {i.qty} = ₹{i.qty * i.price}</li> // each line
        ))}
      </ul>
      <p>Total: ₹{total}{discount ? ` (discount ${discount}%)` : ''}</p>
      {coupon && <p>Coupon: {coupon}</p>}
      {footer}                                                           {/* any renderable node */}
      {status === 'placed' && <button onClick={() => onCancel(id)}>Cancel</button>}
    </section>
  );
}

OrderRow.propTypes = {
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired, // string OR number
  status: PropTypes.oneOf(['placed', 'preparing', 'delivered']).isRequired, // enum of allowed values
  items: PropTypes.arrayOf(                                                 // array of objects
    PropTypes.shape({                                                       // object with known keys
      name: PropTypes.string.isRequired,
      qty: PropTypes.number.isRequired,
      price: PropTypes.number.isRequired,
    })
  ).isRequired,
  coupon: PropTypes.string,                                                 // optional
  footer: PropTypes.node,                                                   // anything React can render
  discount(props, propName, componentName) {                                // CUSTOM validator
    const value = props[propName];
    if (value === undefined) return null;                                   // optional prop
    if (typeof value !== 'number' || value < 0 || value > 100) {
      return new Error(`${componentName}: "${propName}" must be a number between 0 and 100`);
    }
    return null;                                                            // valid
  },
  onCancel: PropTypes.func,
};

// React 19: run checks manually in development if you still want PropTypes
if (process.env.NODE_ENV !== 'production') {
  PropTypes.checkPropTypes(
    OrderRow.propTypes,                                       // the schema
    { id: 1, status: 'DELIVERED', items: [] },                // sample props to test
    'prop',                                                   // location label
    'OrderRow'                                                // component name for the message
  );
}

export default OrderRow;
```

---

## 🟠 Real App Integration

In the Next.js App Router with React 19 (Next.js 15 default), PropTypes **no longer warn automatically**, and for new Next.js projects the recommended path is TypeScript. If you keep PropTypes in a JavaScript codebase, treat it as documentation. You can generate PropTypes from TypeScript (`babel-plugin-typescript-to-proptypes`) or the reverse (`InferProps`) so there is one source of truth.

```jsx
// Next.js 14 (React 18): PropTypes still warns in dev for Client Components
// app/components/MenuItem.jsx
'use client';                                    // Client Component

import PropTypes from 'prop-types';

export default function MenuItem({ name, price }) {
  return <li>{name} - ₹{price}</li>;
}

MenuItem.propTypes = {
  name: PropTypes.string.isRequired,
  price: PropTypes.number.isRequired,
};
```

```tsx
// Reuse the schema as a TypeScript type with InferProps (types come from the schema)
import PropTypes, { InferProps } from 'prop-types';

const menuItemTypes = {
  name: PropTypes.string.isRequired,
  price: PropTypes.number.isRequired,
};

type MenuItemProps = InferProps<typeof menuItemTypes>;   // { name: string; price: number }
```

(Version-dependent: whether PropTypes warns depends on React 18 versus 19. Check your installed React version.)

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Writing `propTypes` with a capital `P` or lowercase `PropTypes` on the component
✅ **Correct:** The component property is `propTypes` (lowercase p); the imported object is `PropTypes`

```jsx
// Wrong: typo in the property name, React silently ignores it
MenuItem.PropTypes = { name: PropTypes.string };        // ❌ never checked
MenuItem.proptypes = { name: PropTypes.string };        // ❌ never checked

// Right
MenuItem.propTypes = { name: PropTypes.string };        // ✅
```

❌ **Mistake 2:** Using `PropTypes.object` or `PropTypes.array` and thinking the shape is validated
✅ **Correct:** Use `shape`/`exact` and `arrayOf`

```jsx
// Wrong: accepts ANY object or ANY array
Row.propTypes = { user: PropTypes.object, items: PropTypes.array };   // ❌ too loose

// Right: describe what is inside
Row.propTypes = {
  user: PropTypes.shape({ id: PropTypes.string.isRequired, name: PropTypes.string }),
  items: PropTypes.arrayOf(PropTypes.number),
};
```

❌ **Mistake 3:** Relying on PropTypes in production or for user input validation
✅ **Correct:** PropTypes are development hints only; validate real input with a schema library (Zod) and on the server

```jsx
// Wrong: assuming bad API data is blocked in production
Cart.propTypes = { total: PropTypes.number.isRequired };    // ❌ no check at all in a production build

// Right: validate at the boundary, where data enters the app
import { z } from 'zod';
const CartSchema = z.object({ total: z.number() });
const cart = CartSchema.parse(await res.json());            // ✅ throws if the API sends bad data
```

---

## 🧠 Tricky Interview Question

```jsx
import PropTypes from 'prop-types';

function Price({ amount }) {
  return <p>₹{amount.toFixed(2)}</p>;
}

Price.propTypes = {
  amount: PropTypes.number.isRequired,
};

// Usage
<Price amount="99.5" />
```
Question: What happens (React 18, development mode)? Does the PropTypes warning prevent the crash?

**Answer:** The console shows a warning: *Invalid prop `amount` of type `string` supplied to `Price`, expected `number`*. But PropTypes does **not** stop rendering, so the next line runs `"99.5".toFixed(2)`, which throws `TypeError: amount.toFixed is not a function`, and the component crashes (an error boundary would catch it). PropTypes only reports problems; it does not fix, coerce or block them. In React 19 even the warning is gone, so the app would crash with only the TypeError.

---

## ⚫ Interview Questions + Answers

Q1: What is PropTypes and why was it introduced?
A1: A library (`prop-types`) for runtime type checking of component props in development. It was introduced because JavaScript has no static types, and teams needed a way to document and verify what props a component accepts.

Q2: What is the difference between `PropTypes.shape` and `PropTypes.exact`?
A2: `shape` checks that the listed keys have the right types and allows extra keys. `exact` also warns about unknown keys, so the object must match the description exactly.

Q3: What is the difference between `PropTypes.node` and `PropTypes.element`?
A3: `element` accepts exactly one React element (`<Icon />`). `node` accepts anything React can render: elements, strings, numbers, arrays of those, and fragments. Use `node` for `children`.

Q4: PropTypes versus TypeScript: which should you use?
A4: TypeScript for new projects. It checks at build time (no runtime cost, catches errors before the browser), understands generics and unions, and gives editor autocomplete. PropTypes check only in development at runtime, and only for components that render. React 19 removed the built-in PropTypes check, so use PropTypes only for legacy JavaScript code.

Q5: Do PropTypes run in production?
A5: No. They are for development; the production build skips them for performance. Never use them as a security or data validation layer.

---

## 🔷 When to Use + When Not to Use
✅ **Use PropTypes when:**
- You maintain a large JavaScript (non-TypeScript) codebase on React 15 to 18
- You publish a library for JS users and want runtime hints
- You are learning, and want quick feedback on prop mistakes

❌ **Avoid PropTypes when:**
- You are starting a new project (use TypeScript)
- You use React 19 and expect automatic warnings
- You need validation of real user or API data (use Zod, Yup or server validation)

---

## 📊 Visual Diagram

```
  Component file
  ┌──────────────────────────────────────────────┐
  │ function MenuItem(props) { ... }             │
  │                                              │
  │ MenuItem.propTypes = {                       │
  │    name:  PropTypes.string.isRequired, ──┐   │
  │    price: PropTypes.number.isRequired, ──┤   │
  │ }                                        │   │
  └──────────────────────────────────────────┼───┘
                                             │ schema
  <MenuItem name="Tikka" price="250" />      ▼
          │                         ┌────────────────────┐
          └── props at render ────▶ │ checkPropTypes()   │
                                    └─────┬──────────────┘
                       React ≤ 18 DEV     │ mismatch?
                       (auto-called)      ▼
                                   console.error("Failed prop type ...")
                                   (rendering CONTINUES)

  Production build  → no check at all
  React 19          → no automatic check (call checkPropTypes yourself)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `prop-types` | npm package for runtime prop checks | Runtime पर props जाँचने वाला npm package |
| `isRequired` | Marks a prop as mandatory | Prop को ज़रूरी बनाता है |
| `shape` | Object with known keys and types | जाने-पहचाने keys और types वाला object |
| `arrayOf` | Array whose items have one type | ऐसा array जिसके items का एक type हो |
| `oneOf` | Value must be one from a fixed list | Fixed list में से एक value |
| `node` | Anything React can render | React जो कुछ भी render कर सके |
| Custom validator | Your own function returning an Error | अपना function जो Error return करे |
| `checkPropTypes` | Manually run the checks | Checks को हाथ से चलाना |

---

## ⚡ 3-Line Summary
**English:**
1. PropTypes checks prop types at runtime in development and only prints warnings; it never blocks rendering.
2. Use `isRequired`, `shape`, `arrayOf`, `oneOf` and `node` to describe props, and add `propTypes` as a static property.
3. React 19 removed the automatic check, so use TypeScript for new code and Zod for real data validation.

**Hindi:**
1. PropTypes development में runtime पर prop types जाँचता है और सिर्फ warning छापता है; rendering कभी नहीं रोकता।
2. Props बताने के लिए `isRequired`, `shape`, `arrayOf`, `oneOf` और `node` इस्तेमाल करो, और `propTypes` को static property की तरह जोड़ो।
3. React 19 ने automatic check हटा दिया, इसलिए नए code के लिए TypeScript और असली data के लिए Zod इस्तेमाल करो।

---

## ➡️ Next Topic
**18. defaultProps** — Props की जाँच के बाद देखो कि missing props को default value कैसे मिले, और React 19 में `defaultProps` की जगह default parameters क्यों आए।
