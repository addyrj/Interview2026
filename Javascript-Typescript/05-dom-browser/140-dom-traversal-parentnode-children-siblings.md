# 140. DOM Traversal (parentNode, children, siblings)
# हिंदी में: DOM Traversal (parentNode, children, siblings)

---

## 🔵 Simple Definition (English)
DOM traversal means moving through the tree from one node to another: up to the parent, down to children, and sideways to siblings. Properties such as `parentElement`, `children`, `firstElementChild`, and `nextElementSibling` do this movement.

## 🔵 सरल परिभाषा (Hindi)
DOM traversal का मतलब है tree में एक node से दूसरे node तक जाना: ऊपर parent की तरफ, नीचे children की तरफ, और बगल में siblings की तरफ। `parentElement`, `children`, `firstElementChild`, और `nextElementSibling` जैसी properties यह movement करती हैं।

---

## 🔴 Problem it Solves
Often you have one node (for example a "Delete" button) and need its surrounding node (the whole row or card). Or you have a list and need the next item. You could search the whole document again with `querySelector`, but that is slow and fragile if ids change. Traversal uses the structure you already have: from the current node you move to its relation, which is fast and exact.

## 🔴 यह क्यों बना? (Hindi)
अक्सर हमारे पास एक node होता है (जैसे "Delete" button) और उसके आसपास वाला node चाहिए (पूरी row या card)। या list में अगला item चाहिए। पूरा document दोबारा `querySelector` से ढूँढ सकते हैं, लेकिन वह धीमा और नाजुक है। Traversal वही structure इस्तेमाल करता है जो पहले से है: मौजूदा node से उसके relation तक जाना तेज़ और सटीक है।

---

## 🟢 How it Works — Step by Step

Step 1 → Start with a known node, for example the clicked button.
Step 2 → Go UP with `parentElement` (element parent) or `parentNode` (any parent, including `document`).
Step 3 → Go DOWN with `children` (elements only) or `childNodes` (includes text and comments), plus `firstElementChild` and `lastElementChild`.
Step 4 → Go SIDEWAYS with `nextElementSibling` and `previousElementSibling`.
Step 5 → Text nodes between tags (whitespace) appear in `childNodes`, `firstChild`, `nextSibling`. Use the `Element` versions to skip them.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → किसी ज्ञात node से शुरू करें, जैसे clicked button।
Step 2 → `parentElement` (element parent) या `parentNode` (कोई भी parent, `document` सहित) से ऊपर जाएँ।
Step 3 → `children` (सिर्फ elements) या `childNodes` (text और comments सहित), और `firstElementChild` / `lastElementChild` से नीचे जाएँ।
Step 4 → `nextElementSibling` और `previousElementSibling` से बगल में जाएँ।
Step 5 → Tags के बीच का whitespace text node बनता है, जो `childNodes`, `firstChild`, `nextSibling` में आता है। Element वाली versions से उसे छोड़ सकते हैं।

---

## 🟡 Real World Example
On Zomato's cart page, each item row has a "+" and "-" button. When the user clicks "+", the code needs the quantity label that sits next to it and the row total. It moves from the button to its parent row with `closest` or `parentElement`, then to the quantity node with `previousElementSibling`. On Amazon's product list, "Next item" arrow focus moves to `nextElementSibling`. Paytm's contact list uses the same movement to highlight the next contact on keyboard arrow keys.

## 🟡 Real Example Hindi mein
Zomato के cart page पर हर item row में "+" और "-" buttons हैं। जब user "+" दबाता है, तो code को बगल में बैठा quantity label और row का total चाहिए। वह button से उसकी parent row तक `parentElement` से जाता है, फिर `previousElementSibling` से quantity node तक। Amazon की product list में arrow key से अगला item focus करना `nextElementSibling` से होता है। Paytm की contact list में keyboard arrow से अगला contact highlight करना भी यही movement है।

---

## 💻 Code Example — Basic
Save as `traversal-basic.html` and open it in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DOM Traversal Basic</title>
</head>
<body>
  <ul id="cart">                              <!-- list of cart items -->
    <li id="item-1">Pizza</li>                <!-- first item -->
    <li id="item-2">Burger</li>               <!-- middle item -->
    <li id="item-3">Coke</li>                 <!-- last item -->
  </ul>

  <script>
    const burger = document.getElementById("item-2"); // start from the middle item

    // Going UP: parent of the li is the ul
    console.log(burger.parentElement.id);       // "cart"

    // Going DOWN: children of the ul are the three li elements
    const cart = burger.parentElement;          // the ul element
    console.log(cart.children.length);          // 3

    // Going SIDEWAYS: next and previous sibling elements
    console.log(burger.nextElementSibling.textContent);     // "Coke"
    console.log(burger.previousElementSibling.textContent); // "Pizza"

    // First and last child elements
    console.log(cart.firstElementChild.textContent); // "Pizza"
    console.log(cart.lastElementChild.textContent);  // "Coke"

    // Loop through the children of the list
    for (const li of cart.children) {           // children is iterable
      console.log("Item:", li.textContent);     // print each item name
    }

    // Walking the sibling chain manually (a common pattern)
    let node = cart.firstElementChild;          // start at the first li
    while (node) {                              // continue while there is a node
      console.log("Chain:", node.id);           // print its id
      node = node.nextElementSibling;           // move to the next sibling; null at the end
    }

    // Last piece: document-level relations
    console.log(document.documentElement.parentElement); // null: <html> has no element parent
    console.log(document.documentElement.parentNode.nodeName); // "#document"
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `traversal-advanced.html`. It builds a keyboard-navigable cart: arrow keys move between rows with siblings, and the quantity updates through `closest` and sibling traversal.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cart traversal</title>
</head>
<body>
  <ul id="cart">
    <li class="row" tabindex="0">               <!-- tabindex makes the row focusable -->
      <span class="name">Pizza</span>
      <button class="minus">-</button>
      <span class="qty">1</span>               <!-- quantity label next to the buttons -->
      <button class="plus">+</button>
    </li>
    <li class="row" tabindex="0">
      <span class="name">Burger</span>
      <button class="minus">-</button>
      <span class="qty">2</span>
      <button class="plus">+</button>
    </li>
  </ul>

  <script>
    const cart = document.getElementById("cart"); // container for all rows

    // Event delegation on the cart: one listener for all buttons
    cart.addEventListener("click", (event) => {   // handle clicks anywhere inside the cart
      const button = event.target.closest("button"); // nearest button, if any
      if (!button) return;                         // ignore clicks on non-buttons

      const row = button.closest(".row");          // walk UP to the row that holds the button

      // Find the quantity node inside this row (scoped query on the row)
      const qty = row.querySelector(".qty");       // quantity node for this row only
      let value = Number(qty.textContent);         // read current quantity as a number

      if (button.classList.contains("plus")) value += 1;      // increase
      if (button.classList.contains("minus")) value = Math.max(0, value - 1); // decrease, not below 0

      qty.textContent = String(value);             // write the new quantity
      console.log("Updated", row.querySelector(".name").textContent, "to", value); // log change
    });

    // Keyboard navigation: arrow keys move focus to the sibling row
    cart.addEventListener("keydown", (event) => {  // listen for key presses inside cart
      const row = event.target.closest(".row");    // current row (if focus is on one)
      if (!row) return;                            // ignore keys outside rows
      if (event.key === "ArrowDown" && row.nextElementSibling) {  // there is a next row
        row.nextElementSibling.focus();            // move focus to it
        event.preventDefault();                    // stop the page from scrolling
      }
      if (event.key === "ArrowUp" && row.previousElementSibling) { // there is a previous row
        row.previousElementSibling.focus();        // move focus up
        event.preventDefault();                    // stop scrolling
      }
    });

    // Parent chain: check how deep the clicked item is (for debugging)
    function depth(node) {                         // count ancestors until document
      let d = 0;                                   // start at zero
      let current = node;                          // begin at the node
      while (current.parentNode) {                 // stop when there is no parent (document)
        d++;                                       // one level up
        current = current.parentNode;              // move to parent
      }
      return d;                                    // number of ancestors
    }
    console.log("Depth of cart:", depth(cart));    // ancestors: body, html, document
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Traversal is browser-side. Express's role is to return HTML with a consistent structure (rows, buttons, labels in the same order) so the traversal code works. A cart API also returns the same row order, and the client renders rows with the same structure.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");         // web framework
const app = express();                      // create app
app.use(express.json());                    // parse JSON bodies for POST requests

// In-memory cart (real apps use a database)
const cart = [                              // array of items in the order they are shown
  { id: 1, name: "Pizza", qty: 1 },         // first row
  { id: 2, name: "Burger", qty: 2 },        // second row
];

// Returns the cart; the client builds rows in this order, so siblings line up
app.get("/api/cart", (req, res) => {        // handle GET /api/cart
  res.json(cart);                           // send array as JSON
});

// Updates one quantity; the client finds the row by data-id and updates its .qty node
app.post("/api/cart/:id/qty", (req, res) => { // handle POST /api/cart/:id/qty
  const item = cart.find((i) => i.id === Number(req.params.id)); // find item by id
  if (!item) return res.status(404).json({ error: "Not found" }); // 404 if missing
  item.qty = Math.max(0, Number(req.body.qty) || 0); // validate and clamp at 0
  res.json(item);                            // return updated item
});

app.listen(3000, () => console.log("Cart API on http://localhost:3000/api/cart"));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `childNodes` or `firstChild` and getting whitespace text nodes
✅ Correct: Use `children`, `firstElementChild`, and `nextElementSibling` when you need elements.

```javascript
// Wrong — the first "child" is probably a whitespace text node, not the <li>
const first = cart.firstChild;            // may be "\n    " text
console.log(first.textContent);           // whitespace, not "Pizza"

// Right — the first element child
const first2 = cart.firstElementChild;    // the first <li>
console.log(first2.textContent);          // "Pizza"
```

❌ **Mistake 2:** Assuming `parentNode` is always an element
✅ Correct: `parentNode` can be the `document` node. Use `parentElement` when you need an element (it is `null` for `<html>`).

```javascript
// Wrong — for <html>, parentNode is the document, so .classList fails
document.documentElement.parentNode.classList.add("x"); // TypeError: classList undefined

// Right — check for null first
const p = document.documentElement.parentElement;     // null
if (p) p.classList.add("x");                          // only when an element exists
```

❌ **Mistake 3:** Forgetting that `nextElementSibling` can be `null`
✅ Correct: Always check before using the sibling.

```javascript
// Wrong — crashes on the last row because nextElementSibling is null
row.nextElementSibling.focus();

// Right — guard the null case
if (row.nextElementSibling) row.nextElementSibling.focus();
```

---

## 🧠 Tricky Interview Question
The page is `<ul id="list">` on its own lines, with `<li>A</li>`, then `<li>B</li>`, separated by newlines and indentation.

```javascript
const list = document.getElementById("list");     // the ul

console.log(list.childNodes.length);              // ?
console.log(list.children.length);                // ?
console.log(list.firstChild.nodeType);            // ?
console.log(list.firstElementChild.textContent);  // ?
console.log(list.firstElementChild.nextSibling.nodeType); // ?
console.log(list.firstElementChild.nextElementSibling.textContent); // ?
```

Answer: The outputs are `5`, `2`, `3`, `A`, `3`, and `B`. The `ul` has five child nodes: a whitespace text node, `li A`, a whitespace text node, `li B`, and a whitespace text node before `</ul>`. So `childNodes.length` is 5 and `children.length` is 2. `firstChild` is the first whitespace text node, whose `nodeType` is 3. `firstElementChild` skips whitespace and gives `li A`. Its `nextSibling` is the whitespace text node between the two items, so its type is 3 again. `nextElementSibling` skips that whitespace and gives `li B`. The key idea is that `...Element` properties ignore text nodes and the `non-Element` versions do not.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `parentNode` and `parentElement`?
A1: `parentNode` returns any parent node, which can be the `document` node. `parentElement` returns only an element parent and returns `null` when the parent is not an element, as with `<html>`.

Q2: What is the difference between `children` and `childNodes`?
A2: `children` is a live HTMLCollection of element children only. `childNodes` is a live NodeList of all child nodes, including text and comment nodes such as whitespace.

Q3: How do you get the next element sibling?
A3: Use `element.nextElementSibling`. It skips text and comment nodes. `nextSibling` returns any node, including whitespace text nodes, so it is less reliable for element work.

Q4: Why is traversal often better than `querySelector` for finding related nodes?
A4: Traversal starts from a node you already have and moves along the tree relations, so it is fast and does not depend on ids or class names. It is ideal for event handlers, where `event.target` is the starting point.

Q5: How would you count the depth of a node in the DOM?
A5: Start at the node and repeatedly move to `parentNode` while it exists, counting steps. The loop ends at `document`, which has no parent. Using `parentElement` would stop at `<html>` instead.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Working from an event target to its row, card, or container (`closest` or `parentElement`)
- Moving focus or selection to the next or previous item (`nextElementSibling`)
- Iterating over direct child elements (`children`)

❌ Avoid when:
- You need a far-away element that is not related in the structure; use `querySelector` instead
- Structure changes often and the code depends on exact child positions; use data attributes or ids
- You need to iterate the whole subtree; use `querySelectorAll` or a TreeWalker

---

## 📊 Visual Diagram
```
                  ul#cart              <── parentElement of each li
                /   |    \
     li#item-1   li#item-2   li#item-3   <── children (elements only)
                    ▲  │
         previousElementSibling  │  nextElementSibling
                    │     ▼
          li#item-1 ◄── burger ──► li#item-3

Going UP    : node.parentElement / node.parentNode  (document is the top)
Going DOWN  : node.children / firstElementChild / lastElementChild
Going SIDE  : node.nextElementSibling / previousElementSibling
Text nodes  : childNodes / firstChild / nextSibling  (includes whitespace!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Traversal | Moving through the tree | Tree में आगे-पीछे जाना |
| parentElement | Parent that is an element | Element वाला parent |
| parentNode | Any parent node (may be document) | कोई भी parent node |
| children | Element children only (live) | सिर्फ element children |
| childNodes | All children including text (live) | Text सहित सारे children |
| nextElementSibling | Next element at the same level | उसी level का अगला element |
| Sibling | Node with the same parent | एक ही parent के बच्चे |
| Whitespace node | Text node made of spaces or newlines | Spaces या newlines वाला text node |

---

## ⚡ 3-Line Summary
**English:**
1. Move up with `parentElement`, down with `children` or `firstElementChild`, and sideways with `nextElementSibling`.
2. Prefer the `Element` versions, because `childNodes` and `nextSibling` include whitespace text nodes.
3. Always check for `null` at the edges of the tree, such as the last sibling or the `<html>` parent.

**Hindi:**
1. ऊपर `parentElement` से, नीचे `children` या `firstElementChild` से, और बगल में `nextElementSibling` से जाएँ।
2. `Element` वाली versions बेहतर हैं, क्योंकि `childNodes` और `nextSibling` में whitespace text nodes आते हैं।
3. Tree के किनारों पर हमेशा `null` check करें, जैसे आखिरी sibling या `<html>` का parent।

---

## ➡️ Next Topic
**141. Events — Complete Guide** — अब सीखेंगे कि browser में user actions (click, input, keyboard) को कैसे पकड़ें और handle करें।
