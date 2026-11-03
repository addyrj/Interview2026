# 24. data- Attributes
# हिंदी में: data- Attributes — HTML Elements में अपना Custom Data

---

## 🔵 Simple Definition (English)
`data-*` attributes let you store **custom information** on any HTML element, like `data-user-id="42"` or `data-price="199"`. They are valid HTML, invisible to users, readable from JavaScript through `element.dataset`, and usable in CSS through attribute selectors, `attr()` and more.

## 🔵 सरल परिभाषा (Hindi)
`data-*` attributes से आप किसी भी HTML element पर **अपनी custom जानकारी** रख सकते हो, जैसे `data-user-id="42"` या `data-price="199"`। ये valid HTML हैं, users को दिखते नहीं, JavaScript में `element.dataset` से पढ़े जा सकते हैं और CSS में attribute selectors से भी।

---

## 🔴 Problem it Solves
```
BEFORE data-* (HTML4 era): developers invented fake attributes or abused others
  <li price="199" userid="42">         <- invalid HTML, validators fail
  <li class="item item-id-42">         <- stuffing data into class names
  <input type="hidden" value="42">     <- clutters forms
  <li id="item_42">                    <- parsing id strings: id.split('_')[1]
  or keeping a separate JS object and manually syncing it with the DOM.

WITH data-*:
  <li data-id="42" data-price="199" data-category="pizza">Margherita</li>
  - Valid HTML, standardized, namespaced (nobody else's attribute will clash)
  - JS: li.dataset.price      CSS: li[data-category="pizza"] { ... }
  - Data travels with the element: perfect for event handlers (which item was clicked?)
```

## 🔴 यह क्यों बना? (Hindi)
```
data-* से पहले (HTML4 का दौर): developers अपने fake attributes बनाते थे
  <li price="199" userid="42">         <- invalid HTML, validators fail
  <li class="item item-id-42">         <- class names में data ठूँसना
  <input type="hidden" value="42">     <- form में गंदगी
  <li id="item_42">                    <- id.split('_')[1] से parse करना
  या अलग JS object रखकर DOM से manually sync करना।

data-* के साथ:
  <li data-id="42" data-price="199" data-category="pizza">Margherita</li>
  - Valid HTML, standard, namespaced (किसी और attribute से टकराव नहीं)
  - JS: li.dataset.price      CSS: li[data-category="pizza"] { ... }
  - Data element के साथ चलता है: event handlers के लिए बढ़िया (कौन सा item click हुआ?)
```

---

## 🟢 How it Works — Step by Step

```
SYNTAX RULES:
  name must start with "data-", then at least one character, lowercase letters,
  digits, hyphens (and a few others). Value is ALWAYS a string.
     <div data-user-id="42" data-is-admin="true" data-tags='["a","b"]'>

1. READ IN JS: element.dataset  (a DOMStringMap)
   data-user-id   ->   el.dataset.userId        (kebab-case becomes camelCase)
   data-is-admin  ->   el.dataset.isAdmin       (value is the STRING "true")
   Numbers/booleans/JSON must be converted:
     Number(el.dataset.price)    el.dataset.isAdmin === 'true'    JSON.parse(el.dataset.tags)

2. WRITE IN JS:
   el.dataset.status = 'done'         ->   adds data-status="done"
   el.dataset.userId = 7              ->   data-user-id="7" (coerced to string)
   delete el.dataset.status           ->   removes the attribute
   el.getAttribute('data-user-id') / setAttribute / removeAttribute also work.

3. USE IN CSS:
   [data-status="done"] { color: green; }       attribute selector (topic 90)
   [data-theme="dark"] body { ... }             theme switching on <html data-theme="dark">
   [data-open] { display: block; }              presence selector
   [data-tag^="new"] / [data-tag*="sale"]       prefix / substring match
   .badge::after { content: attr(data-count); } display the value via content
                                                (attr() in `content` works everywhere;
                                                 using attr() for other properties is new)

4. SELECT IN JS: document.querySelectorAll('[data-id="42"]'), el.closest('[data-id]')

5. WHAT data-* IS FOR:
   Small bits of metadata about an element: ids for event delegation, state flags
   for CSS (data-state="open"), config for plugins, testing hooks (data-testid),
   analytics (data-track="add-to-cart"), tooltips (data-tooltip="Help").

6. WHAT IT IS NOT FOR / LIMITS:
   - NOT secure: anyone can see and edit it in DevTools. Never store secrets/tokens.
   - NOT for large data: it bloats HTML; use a JS variable, JSON script tag or API.
   - NOT indexed by SEO as content; not visible to users or screen readers.
   - Do not use it as the source of truth for app state (state lives in JS), only as a
     hook or a mirror for styling.
   - Do not use for content users must see: put that in the DOM text.

PERFORMANCE: dataset access is fast; attribute selectors in CSS are fine in normal
quantities.
```

## 🟢 कैसे काम करता है? (Hindi)

```
SYNTAX नियम:
  नाम "data-" से शुरू होना चाहिए, फिर कम से कम एक character, lowercase letters,
  digits, hyphens। Value हमेशा STRING होती है।
     <div data-user-id="42" data-is-admin="true">

1. JS में पढ़ना: element.dataset
   data-user-id   ->   el.dataset.userId        (kebab-case, camelCase बन जाता है)
   data-is-admin  ->   el.dataset.isAdmin       (value STRING "true" है)
   Number/boolean/JSON खुद convert करो:
     Number(el.dataset.price)    el.dataset.isAdmin === 'true'    JSON.parse(...)

2. JS में लिखना:
   el.dataset.status = 'done'         ->   data-status="done" जुड़ जाता है
   delete el.dataset.status           ->   attribute हट जाता है

3. CSS में use:
   [data-status="done"] { color: green; }
   [data-theme="dark"] body { ... }      <html data-theme="dark"> से theme बदलना
   .badge::after { content: attr(data-count); }   value को दिखाना

4. JS में चुनना: document.querySelectorAll('[data-id="42"]'), el.closest('[data-id]')

5. किस काम के लिए:
   Element के बारे में छोटी metadata: event delegation के लिए ids, CSS के लिए state
   flags (data-state="open"), testing hooks (data-testid), analytics (data-track)।

6. सीमाएँ:
   - सुरक्षित नहीं: DevTools में कोई भी देख/बदल सकता है। Secrets/tokens कभी नहीं।
   - बड़े data के लिए नहीं: HTML भारी होगा; JS variable या API use करो।
   - Users को दिखने वाला content DOM text में रखो, data-* में नहीं।
   - App state का असली source JS में रहे; data-* सिर्फ hook या CSS mirror है।
```

---

## 🟡 Real World Example
**Zomato / Swiggy menu list:** each dish row is `<li data-dish-id="8841" data-price="299" data-veg="true">`. One click listener on the list reads `e.target.closest('[data-dish-id]').dataset.dishId` to know which dish to add to the cart. **Dark mode on Gmail-like apps:** `<html data-theme="dark">` flips all CSS variables at once. **Amazon:** product tiles carry analytics attributes like `data-asin` and `data-component-type` used by tracking scripts. **QA teams:** `data-testid="checkout-button"` gives tests a stable hook that does not change when styling changes.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy menu list:** हर dish row होती है `<li data-dish-id="8841" data-price="299" data-veg="true">`। List पर एक click listener `e.target.closest('[data-dish-id]').dataset.dishId` पढ़कर जान लेता है कि कौन सी dish cart में जोड़नी है। **Dark mode:** `<html data-theme="dark">` से सारे CSS variables एक साथ बदल जाते हैं। **Amazon:** product tiles में `data-asin` और `data-component-type` जैसे analytics attributes होते हैं जिन्हें tracking scripts पढ़ती हैं। **QA टीमें:** `data-testid="checkout-button"` tests को एक stable hook देता है जो styling बदलने पर नहीं बदलता।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">  <!-- data-theme drives the CSS theme -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>data-* Attributes Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }

    /* THEME via data attribute on <html> */
    :root, [data-theme="light"] { --bg: #ffffff; --fg: #1a1a1a; --card: #f5f5f5; }
    [data-theme="dark"]         { --bg: #121212; --fg: #f1f1f1; --card: #1e1e1e; }

    body { background: var(--bg); color: var(--fg); font-family: system-ui, sans-serif; max-width: 560px; margin: 24px auto; padding: 0 16px; transition: background .2s; }
    ul { list-style: none; padding: 0; }
    li { background: var(--card); padding: 12px; margin: 8px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    button { background: #e23744; color: #fff; border: 0; padding: 6px 12px; border-radius: 6px; cursor: pointer; }

    /* STYLE based on data attributes (attribute selectors) */
    li[data-veg="true"]  { border-left: 6px solid #2e7d32; }     /* green = veg */
    li[data-veg="false"] { border-left: 6px solid #b3261e; }     /* red = non-veg */
    li[data-status="added"] { outline: 2px solid #2e7d32; }      /* state flag set by JS */
    li[data-price]::after { content: "Rs " attr(data-price); font-weight: 700; }   /* show value with attr() */

    /* Tooltip using data-tooltip and attr() */
    [data-tooltip] { position: relative; cursor: help; border-bottom: 1px dotted; }
    [data-tooltip]:hover::before, [data-tooltip]:focus::before {
      content: attr(data-tooltip);
      position: absolute; left: 0; bottom: 120%;
      background: #000; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap;
    }

    #log { background: #222; color: #9f9; padding: 10px; border-radius: 6px; font-size: 13px; min-height: 60px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>Menu</h1>
  <p><span data-tooltip="Veg = green bar, Non-veg = red bar" tabindex="0">Hover or focus for legend</span></p>

  <!-- Each item stores its own metadata. Values are STRINGS. -->
  <ul id="menu">
    <li data-id="101" data-price="199" data-veg="true"  data-tags='["bestseller","cheesy"]'><span>Margherita</span> <button type="button" data-action="add">Add</button></li>
    <li data-id="102" data-price="349" data-veg="false" data-tags='["spicy"]'><span>Chicken Tikka Pizza</span> <button type="button" data-action="add">Add</button></li>
    <li data-id="103" data-price="299" data-veg="true"  data-tags='["new"]'><span>Paneer Tikka</span> <button type="button" data-action="add">Add</button></li>
  </ul>

  <button type="button" id="theme" data-testid="theme-toggle">Toggle theme</button>
  <h2>Log</h2>
  <div id="log" aria-live="polite"></div>

  <script>
    const menu = document.getElementById('menu');
    const log = document.getElementById('log');
    let total = 0;

    // EVENT DELEGATION using data-action + dataset
    menu.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action="add"]');
      if (!btn) return;
      const li = btn.closest('[data-id]');            // nearest element that has data-id

      // READ: camelCase names; everything is a string, so convert types
      const id    = Number(li.dataset.id);
      const price = Number(li.dataset.price);
      const veg   = li.dataset.veg === 'true';        // boolean from string
      const tags  = JSON.parse(li.dataset.tags);      // array from JSON string

      // WRITE: adds data-status="added", which CSS reacts to
      li.dataset.status = 'added';
      total += price;
      log.textContent += `Added #${id} (${li.querySelector('span').textContent}) veg=${veg} tags=${tags.join(',')}  total=Rs ${total}\n`;
    });

    // THEME toggle: flip data-theme on <html>; CSS variables do the rest
    document.getElementById('theme').addEventListener('click', () => {
      const root = document.documentElement;
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    });

    // Querying by data attribute
    console.log('Veg items:', document.querySelectorAll('[data-veg="true"]').length);
    // delete li.dataset.status   -> removes the attribute again
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// In JSX, data-* attributes are written exactly as in HTML (kebab-case, lowercase).
// (aria-* and data-* are the exceptions to camelCase.)
function DishRow({ dish, onAdd }) {
  return (
    <li
      data-id={dish.id}
      data-veg={dish.veg}                // boolean true/false becomes the string "true"/"false"
      data-status={dish.added ? 'added' : undefined}   // undefined removes the attribute
      data-testid={`dish-${dish.id}`}    // stable hook for React Testing Library / Cypress / Playwright
    >
      {dish.name}
      <button onClick={() => onAdd(dish.id)}>Add</button>
    </li>
  );
}

// In React you usually do NOT need data-id for click handlers because closures give you
// the item directly (onClick={() => onAdd(dish.id)}). Use data-* mainly for:
//   1. Styling hooks from state:     <div data-state={open ? 'open' : 'closed'}>
//   2. Test ids:                     screen.getByTestId('checkout-button')
//   3. Analytics:                    data-track="add-to-cart"
//   4. Libraries: Radix UI exposes state through data attributes (data-state, data-disabled,
//      data-orientation) so you can style them.

// Tailwind has data-attribute variants (v3.2+ for arbitrary, v4 simple):
//   className="data-[state=open]:bg-red-500 data-[veg=true]:border-green-600"
//   group-data-[state=open]:rotate-180

// Reading in an event handler: e.currentTarget.dataset.id  (strings!)
// Theme switching (next-themes): sets <html data-theme="dark"> or class="dark".
// Never put secrets or large JSON in data-*: it is shipped in the HTML/DOM and visible.
```

---

## ⚫ Interview Questions + Answers

**Q1: What are `data-*` attributes and how do you access them in JavaScript?**
A1: They are custom attributes for storing extra information on elements, valid in HTML5 when named `data-` plus a lowercase name. In JS use `element.dataset`; kebab-case becomes camelCase (`data-user-id` becomes `dataset.userId`). You can also use `getAttribute('data-user-id')`. Setting `el.dataset.x = 'y'` adds the attribute and `delete el.dataset.x` removes it.

**Q2: What is the type of a `dataset` value?**
A2: Always a string. `data-price="199"` gives `"199"`, and `data-active="false"` gives the string `"false"`, which is truthy! Convert explicitly: `Number(...)`, `el.dataset.active === 'true'`, `JSON.parse(...)`. Assigning a number stores it as a string.

**Q3: How can CSS use data attributes?**
A3: Through attribute selectors: `[data-state="open"]`, `[data-theme="dark"]`, `[data-id^="a"]`, plus `content: attr(data-label)` in pseudo-elements to show the value (tooltips, badges). It is a clean way to drive styles from state without long class names, and it is what UI libraries like Radix do (`data-state`).

**Q4: When should you not use `data-*`?**
A4: Do not store sensitive data (users can read and edit it in DevTools), large data (bloats HTML and slows DOM), or the real application state (keep that in JS/React state or a server). Do not hide content users need to read or that SEO should index. Prefer semantic attributes (`href`, `value`, `aria-*`) when one exists.

**Q5: How is `data-*` used in React and testing?**
A5: JSX writes `data-*` the same as HTML. With React, handlers normally use closures instead of reading dataset values, so `data-*` is mostly for style hooks driven by state, analytics tags and test ids (`data-testid` with `getByTestId`). Tailwind has `data-[state=open]:` variants and Radix UI exposes state through data attributes.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using camelCase or uppercase in the HTML name
```html
<div data-userId="42"></div>   <!-- HTML lowercases it to data-userid: dataset.userid -->
```
✅ **Correct way:** `data-user-id="42"` and read `el.dataset.userId`.

❌ **Mistake 2:** Treating values as numbers/booleans
```js
if (el.dataset.active) { ... }          // "false" is truthy!
const sum = el.dataset.a + el.dataset.b; // "1" + "2" = "12"
```
✅ **Correct way:** `el.dataset.active === 'true'`, `Number(el.dataset.a) + Number(el.dataset.b)`.

❌ **Mistake 3:** Storing secrets or big JSON blobs
```html
<div data-token="eyJhbGciOi..." data-all-users='[ ...5000 users... ]'></div>
```
✅ **Correct way:** Keep tokens in httpOnly cookies/server, and fetch big data through an API or JS state.

❌ **Mistake 4:** Using data-* as the source of truth and syncing it by hand
✅ **Correct way:** Keep state in JS (or React state) and reflect it to `data-*` only for styling hooks.

❌ **Mistake 5:** Inventing non-standard attributes like `price="199"`
✅ **Correct way:** Always prefix with `data-`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| data-* attribute | Custom attribute for extra info | Extra जानकारी वाला custom attribute |
| dataset | JS object that exposes data-* | data-* को JS में देने वाला object |
| DOMStringMap | Type of `dataset` (string values) | `dataset` का type (string values) |
| camelCase conversion | `data-user-id` to `userId` | नाम का camelCase में बदलना |
| Attribute selector | CSS `[data-x="y"]` | Attribute से चुनने वाला CSS selector |
| attr() | CSS function reading an attribute | Attribute पढ़ने वाला CSS function |
| data-testid | Stable attribute for automated tests | Tests के लिए stable hook |
| Event delegation | One parent listener reading data-* | Parent पर एक listener |

---

## ⚡ 3-Line Summary
**English:**
1. `data-*` attributes store custom string metadata on elements; read/write them with `element.dataset` (kebab-case becomes camelCase).
2. Use them for event delegation, CSS state hooks (`[data-state="open"]`, themes), tooltips with `attr()`, test ids and analytics.
3. Values are always strings and fully visible to users, so never store secrets or large data; in React prefer closures and use `data-*` mainly for styling and testing.

**Hindi:**
1. `data-*` attributes elements पर custom string metadata रखते हैं; `element.dataset` से पढ़ो/लिखो (kebab-case, camelCase बन जाता है)।
2. इन्हें event delegation, CSS state hooks (`[data-state="open"]`, themes), `attr()` वाले tooltips, test ids और analytics के लिए use करो।
3. Values हमेशा string होती हैं और users को दिख सकती हैं, इसलिए secrets या बड़ा data मत रखो; React में closures पसंद करो और `data-*` ज़्यादातर styling व testing के लिए।

---

## ➡️ Next Topic
**25. iframe Tag + Use Cases** — दूसरे page (YouTube, Google Maps) को अपने page में embed करना और उसकी security सीमाएँ।
