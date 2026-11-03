# 21. DOM — Document Object Model
# हिंदी में: DOM — Browser में HTML का Tree रूप

---

## 🔵 Simple Definition (English)
The **DOM** is a live, in-memory **tree of objects** the browser builds from your HTML. Every tag, attribute and piece of text becomes a node. JavaScript can read and change this tree (add, remove, edit nodes), and the browser instantly updates what the user sees. HTML is the text file; the DOM is the living model of it.

## 🔵 सरल परिभाषा (Hindi)
**DOM** वो live, memory में बना **objects का tree** है जो browser आपकी HTML से बनाता है। हर tag, attribute और text एक node बन जाता है। JavaScript इस tree को पढ़ और बदल सकती है (node जोड़ना, हटाना, edit करना), और browser तुरंत screen अपडेट कर देता है। HTML text file है; DOM उसका जीवित model है।

---

## 🔴 Problem it Solves
```
PROBLEM: HTML is just a static text file.
  - How can a page react to clicks, show a new message, update a cart count
    WITHOUT reloading the whole page from the server?
  - How can JavaScript "talk to" the page?

SOLUTION: the DOM
  - The browser parses HTML into a tree of objects with properties and methods.
  - JS gets a standard API:  document.querySelector('.cart').textContent = '3'
  - Same API in every browser (W3C/WHATWG standard).
  - Changes -> browser re-renders only what changed (style/layout/paint).

Without the DOM there would be no dynamic web: no Gmail inbox updating live,
no Instagram infinite scroll, no React.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या: HTML सिर्फ एक static text file है।
  - Page click पर प्रतिक्रिया कैसे करे, नया message कैसे दिखाए, cart count कैसे
    बदले, बिना पूरा page server से दोबारा load किए?
  - JavaScript page से "बात" कैसे करे?

समाधान: DOM
  - Browser HTML को properties और methods वाले objects के tree में parse करता है।
  - JS को standard API मिलती है:  document.querySelector('.cart').textContent = '3'
  - हर browser में वही API (W3C/WHATWG standard)।
  - बदलाव होने पर browser सिर्फ बदला हुआ हिस्सा दोबारा बनाता है।

DOM के बिना dynamic web नहीं होता: Gmail inbox live update, Instagram infinite
scroll, React कुछ भी नहीं।
```

---

## 🟢 How it Works — Step by Step

```
1. PARSE:  Browser receives HTML bytes -> characters -> tokens -> nodes -> DOM tree.

   <html>                              document
     <body>                              └── html
       <h1 class="t">Hello</h1>               ├── head
       <p>Hi <b>there</b></p>                 └── body
     </body>                                      ├── h1.t
   </html>                                        │    └── "Hello" (text node)
                                                  └── p
                                                       ├── "Hi " (text node)
                                                       └── b
                                                            └── "there"

2. NODE TYPES:
   Element (nodeType 1)   -> <div>, <p>
   Text    (nodeType 3)   -> the words inside
   Comment (nodeType 8)   -> <!-- ... -->
   Document (nodeType 9)  -> the root `document`
   Attributes are accessed via element.attributes / getAttribute.

3. RELATIONSHIPS: parent, child, sibling.
   el.parentElement  el.children (elements only)  el.childNodes (all nodes)
   el.firstElementChild  el.nextElementSibling  el.previousElementSibling

4. SELECT:
   document.getElementById('id')
   document.querySelector('.card')        (first match, any CSS selector)
   document.querySelectorAll('li.item')   (static NodeList)
   el.closest('.card')                    (walk up to nearest ancestor match)
   (getElementsByClassName returns a LIVE HTMLCollection; querySelectorAll is static)

5. CHANGE:
   el.textContent = 'safe text'           (text only, safe)
   el.innerHTML = '<b>html</b>'           (parses HTML; XSS risk with user input)
   el.setAttribute('href', '/x');  el.classList.add/remove/toggle('active')
   el.style.color = 'red'                 (inline style)
   const n = document.createElement('li'); parent.append(n);  el.remove();
   el.cloneNode(true)

6. EVENTS:
   el.addEventListener('click', handler)
   Events BUBBLE up the tree: click on a <li> also fires on its <ul>, <body>...
   Event delegation: one listener on the parent handles all children via e.target.

7. RENDER PIPELINE: DOM + CSSOM = Render Tree -> Layout (reflow) -> Paint -> Composite.
   Changing the DOM can trigger reflow/repaint, so batch updates (see topic 37).

DOM vs HTML SOURCE vs VIEW SOURCE:
   View Source shows the ORIGINAL HTML text. DevTools "Elements" shows the CURRENT DOM,
   including changes by JS and fixes the parser made (e.g. adding <tbody>).

DOM vs VIRTUAL DOM: React keeps a lightweight JS copy of the tree, diffs it and
applies only the minimum changes to the real DOM.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. PARSE:  Browser HTML bytes -> characters -> tokens -> nodes -> DOM tree बनाता है।

   <html>                              document
     <body>                              └── html
       <h1 class="t">Hello</h1>               ├── head
       <p>Hi <b>there</b></p>                 └── body
     </body>                                      ├── h1.t -> "Hello"
   </html>                                        └── p -> "Hi ", b -> "there"

2. NODE TYPES:
   Element (1) -> <div>, <p>;  Text (3) -> अंदर के शब्द;
   Comment (8) -> <!-- -->;   Document (9) -> root `document`

3. RELATIONSHIPS: parent, child, sibling
   el.parentElement  el.children  el.nextElementSibling

4. SELECT:
   getElementById('id'), querySelector('.card') (पहला match),
   querySelectorAll('li.item') (static list), el.closest('.card') (ऊपर की ओर खोज)

5. CHANGE:
   textContent (सुरक्षित text), innerHTML (HTML parse करता है; XSS का खतरा),
   setAttribute, classList.add/remove/toggle, style, createElement + append, remove()

6. EVENTS:
   addEventListener('click', handler)
   Events ऊपर की ओर BUBBLE होते हैं। Event delegation: parent पर एक listener,
   e.target से child पहचानो।

7. RENDER: DOM + CSSOM = Render Tree -> Layout (reflow) -> Paint -> Composite।
   DOM बदलने पर reflow/repaint हो सकता है, इसलिए updates batch करो।

View Source में ORIGINAL HTML दिखती है; DevTools Elements में CURRENT DOM
(JS के बदलाव और parser के सुधार के साथ, जैसे अपने आप <tbody> जुड़ना)।

Virtual DOM: React tree की हल्की JS copy रखता है, diff निकालता है और असली DOM में
सिर्फ ज़रूरी बदलाव करता है।
```

---

## 🟡 Real World Example
**Zomato cart:** when you tap "+" on a dish, JavaScript finds the cart-count element in the DOM, updates its text to `3`, adds a new `<li>` for the dish and recalculates the total; the page never reloads. **Instagram like button:** clicking toggles a class (`liked`) on the heart `<svg>` and updates the like-count text node. **Gmail:** new mail arrives, and a new `<tr>` is inserted into the inbox table in the DOM, and the unread counter changes.

## 🟡 Real Example Hindi mein
**Zomato cart:** जब आप किसी dish पर "+" दबाते हो, JavaScript DOM में cart-count element ढूँढकर उसका text `3` कर देती है, dish के लिए नया `<li>` जोड़ती है और total दोबारा निकालती है; page reload नहीं होता। **Instagram like button:** click पर heart `<svg>` पर class (`liked`) toggle होती है और like-count का text node बदलता है। **Gmail:** नया mail आने पर inbox table में DOM के अंदर नया `<tr>` डाला जाता है और unread counter बदल जाता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DOM Demo: Mini Cart</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 520px; margin: 24px auto; padding: 0 16px; }
    h1 { display: flex; justify-content: space-between; align-items: center; }
    #count { background: #e23744; color: #fff; border-radius: 999px; padding: 2px 12px; font-size: 16px; }
    .menu, .cart { list-style: none; padding: 0; margin: 0 0 20px; }
    .menu li, .cart li { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
    button { background: #e23744; color: #fff; border: 0; border-radius: 6px; padding: 6px 12px; cursor: pointer; }
    button.remove { background: #777; }
    .liked { color: #e23744; font-weight: bold; }       /* class toggled by JS */
    .empty { color: #888; font-style: italic; }
    #total { font-weight: bold; text-align: right; }
    pre { background: #222; color: #9f9; padding: 10px; border-radius: 6px; font-size: 12px; overflow: auto; }
  </style>
</head>
<body>
  <h1>Menu <span id="count">0</span></h1>

  <!-- data-* holds the item info; JS reads it from the DOM -->
  <ul class="menu" id="menu">
    <li data-name="Margherita" data-price="199"><span>Margherita (Rs 199)</span> <button class="add">Add</button></li>
    <li data-name="Farmhouse"  data-price="299"><span>Farmhouse (Rs 299)</span>  <button class="add">Add</button></li>
    <li data-name="Paneer Tikka" data-price="349"><span>Paneer Tikka (Rs 349)</span> <button class="add">Add</button></li>
  </ul>

  <h2>Cart</h2>
  <ul class="cart" id="cart"><li class="empty">Cart is empty</li></ul>
  <p id="total">Total: Rs 0</p>

  <p><span id="like" role="button" tabindex="0">&#9825; Like this menu</span></p>
  <button id="tree">Print the DOM tree of #cart</button>
  <pre id="out"></pre>

  <script>
    // 1. SELECT nodes (cache them in variables; lookups cost time)
    const menu = document.getElementById('menu');
    const cart = document.querySelector('#cart');
    const countEl = document.getElementById('count');
    const totalEl = document.getElementById('total');
    let total = 0;

    // 2. EVENT DELEGATION: ONE listener on the parent handles all Add buttons
    menu.addEventListener('click', (e) => {
      const btn = e.target.closest('button.add');   // which button was clicked?
      if (!btn) return;                              // click was elsewhere
      const li = btn.closest('li');                  // walk UP to the item
      const { name, price } = li.dataset;            // read data-name and data-price

      // Remove "empty" placeholder if present
      cart.querySelector('.empty')?.remove();

      // 3. CREATE new nodes
      const item = document.createElement('li');
      item.dataset.price = price;
      const label = document.createElement('span');
      label.textContent = `${name} (Rs ${price})`;   // textContent is XSS safe
      const del = document.createElement('button');
      del.className = 'remove';
      del.textContent = 'Remove';
      item.append(label, del);                       // 4. INSERT into the tree
      cart.append(item);

      total += Number(price);
      updateSummary();
    });

    // Delegation again for dynamically created Remove buttons
    cart.addEventListener('click', (e) => {
      const del = e.target.closest('button.remove');
      if (!del) return;
      const item = del.closest('li');
      total -= Number(item.dataset.price);
      item.remove();                                  // 5. REMOVE from the tree
      if (!cart.children.length) cart.innerHTML = '<li class="empty">Cart is empty</li>';  // safe: static string, no user data
      updateSummary();
    });

    function updateSummary() {
      const items = cart.querySelectorAll('li:not(.empty)').length;
      countEl.textContent = items;                    // change text
      totalEl.textContent = 'Total: Rs ' + total;
    }

    // 6. CLASS toggle + ATTRIBUTE change
    const like = document.getElementById('like');
    const toggleLike = () => {
      const on = like.classList.toggle('liked');
      like.textContent = (on ? '♥' : '♡') + ' Like this menu';
      like.setAttribute('aria-pressed', on);          // accessibility state
    };
    like.addEventListener('click', toggleLike);
    like.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') toggleLike(); });

    // 7. WALK the tree
    document.getElementById('tree').addEventListener('click', () => {
      const lines = [];
      (function walk(node, depth) {
        if (node.nodeType === 1) lines.push('  '.repeat(depth) + '<' + node.tagName.toLowerCase() + '>');
        else if (node.nodeType === 3 && node.nodeValue.trim()) lines.push('  '.repeat(depth) + '"' + node.nodeValue.trim() + '"');
        node.childNodes.forEach(c => walk(c, depth + 1));
      })(cart, 0);
      document.getElementById('out').textContent = lines.join('\n') || '(empty)';
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// React does not make you touch the DOM directly. You describe the UI from STATE
// and React updates the real DOM for you using a Virtual DOM + diffing.
import { useState } from 'react';

export default function Cart() {
  const [items, setItems] = useState([]);          // state, not DOM, is the source of truth
  const total = items.reduce((s, i) => s + i.price, 0);

  return (
    <>
      <button onClick={() => setItems([...items, { id: Date.now(), name: 'Margherita', price: 199 }])}>
        Add
      </button>
      <ul>
        {items.map(i => (
          <li key={i.id}>{i.name}   {/* key lets React match nodes across renders */}
            <button onClick={() => setItems(items.filter(x => x.id !== i.id))}>Remove</button>
          </li>
        ))}
      </ul>
      <p>Total: Rs {total}</p>
    </>
  );
}

// When you do need the real DOM node (focus, scroll, measure, video.play()):
const inputRef = useRef(null);
useEffect(() => { inputRef.current?.focus(); }, []);   // runs in the BROWSER after render
<input ref={inputRef} />

// Next.js/SSR: the server has NO DOM. `document` and `window` do not exist on the server,
// so DOM code must run in useEffect or in a Client Component ('use client'),
// or you get "document is not defined".
// Hydration: React attaches to the server-rendered DOM; a mismatch between server HTML
// and client render causes hydration errors.
// Avoid mixing manual DOM edits (innerHTML, appendChild) with React-managed nodes.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the DOM and how is it different from HTML?**
A1: HTML is the static source text. The DOM is the browser's live tree of objects created by parsing that HTML, exposed to JavaScript through APIs. The DOM can differ from the source: JS changes it, and the parser fixes mistakes (like adding `<tbody>`). DevTools Elements shows the DOM; View Source shows the original HTML.

**Q2: What is the difference between `innerHTML`, `textContent` and `innerText`?**
A2: `textContent` gets/sets raw text of the node and its descendants, fast and safe. `innerText` is similar but is aware of CSS (ignores hidden elements, respects line breaks) and triggers layout, so it is slower. `innerHTML` parses a string as HTML, so it can create elements but opens an XSS hole with untrusted input and is slower for big updates.

**Q3: What is event bubbling and event delegation?**
A3: When an event fires on an element it bubbles up through its ancestors (target, parent, ..., document). Capturing is the opposite direction (down). Event delegation attaches one listener to a common parent and uses `e.target` / `closest()` to detect the child, which saves memory and works for elements added later. `stopPropagation()` stops bubbling; `preventDefault()` stops the default action.

**Q4: `querySelectorAll` vs `getElementsByClassName`: what is the difference?**
A4: `querySelectorAll` accepts any CSS selector and returns a **static** `NodeList` (a snapshot that does not change later; it supports `forEach`). `getElementsByClassName`/`getElementsByTagName` return a **live** `HTMLCollection` that updates automatically when the DOM changes (no `forEach`; convert with `Array.from`). Live collections can cause surprising infinite loops when you modify the DOM while iterating.

**Q5: What is the Virtual DOM and why does React use it?**
A5: The Virtual DOM is a lightweight JavaScript representation of the UI tree. On a state change React renders a new virtual tree, diffs it against the previous one (reconciliation) and applies only the minimal changes to the real DOM. This avoids manual DOM manipulation and batches updates, since real DOM operations (especially causing reflow) are comparatively expensive. It is not magic: it is a tradeoff for predictable declarative code.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `innerHTML` with user input
```js
el.innerHTML = userComment;   // XSS if it contains <img onerror=...>
```
✅ **Correct way:** `el.textContent = userComment;` (or sanitize with DOMPurify).

❌ **Mistake 2:** Querying before the DOM is ready
```html
<script>document.getElementById('btn').onclick = f;</script>  <!-- null: button not parsed yet -->
<button id="btn">Go</button>
```
✅ **Correct way:** Place the script at the end of body, use `<script defer>`, or wrap in `DOMContentLoaded`.

❌ **Mistake 3:** Reading and writing layout in a loop (layout thrashing)
```js
items.forEach(i => { i.style.width = i.offsetWidth + 10 + 'px'; });  // forces reflow each time
```
✅ **Correct way:** Read all measurements first, then write; or use `requestAnimationFrame`, CSS classes and DocumentFragment.

❌ **Mistake 4:** Attaching a listener to every item or manipulating the DOM directly inside React
✅ **Correct way:** Use event delegation in vanilla JS; in React use state and refs only when necessary.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DOM | Live tree of page objects | Page के objects का live tree |
| Node | Any item in the tree | Tree की कोई भी इकाई |
| Element | Node for an HTML tag | HTML tag का node |
| Text node | Node holding text | Text वाला node |
| NodeList / HTMLCollection | Lists of nodes (static / live) | Nodes की सूचियाँ |
| Event bubbling | Event travels up to ancestors | Event का ऊपर की ओर जाना |
| Event delegation | One parent listener for many children | Parent पर एक listener |
| Virtual DOM | React's in-memory copy used for diffing | React की memory वाली copy |

---

## ⚡ 3-Line Summary
**English:**
1. The DOM is the browser's live tree of nodes built from HTML; JavaScript reads and changes it and the screen updates.
2. Select with `querySelector`, change with `textContent`, `classList`, `createElement`; use event delegation and avoid `innerHTML` with user data.
3. React hides direct DOM work behind state and a Virtual DOM; use refs/effects for the real DOM, and remember the server has no `document`.

**Hindi:**
1. DOM, HTML से बना browser का live nodes का tree है; JavaScript इसे पढ़ती-बदलती है और screen अपडेट होती है।
2. `querySelector` से चुनो, `textContent`, `classList`, `createElement` से बदलो; event delegation use करो और user data के साथ `innerHTML` से बचो।
3. React सीधा DOM काम state और Virtual DOM के पीछे छुपाता है; असली DOM के लिए refs/effects और याद रखो server पर `document` नहीं होता।

---

## ➡️ Next Topic
**22. HTML Accessibility (ARIA roles, alt text, label)** — DOM सबके लिए काम करे, इसके लिए: screen readers, keyboard users और सही semantic markup।
