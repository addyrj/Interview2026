# 144. Event Bubbling
# हिंदी में: Event Bubbling

---

## 🔵 Simple Definition (English)
Event bubbling means that after an event fires on the innermost element, it travels up through each ancestor, from the target to `document` and then `window`. Each ancestor with a matching listener gets a chance to run. Most events bubble by default.

## 🔵 सरल परिभाषा (Hindi)
Event bubbling का मतलब है कि event सबसे अंदरूनी element पर होने के बाद ऊपर के हर ancestor से होकर गुज़रता है, target से `document` और फिर `window` तक। हर ancestor जिसके पास matching listener है, उसे चलने का मौका मिलता है। ज़्यादातर events by default bubble करते हैं।

---

## 🔴 Problem it Solves
Suppose a Swiggy cart has 50 "+" and "-" buttons. Without bubbling, you would need 50 separate listeners. Bubbling lets one listener on the parent catch clicks from all children. Bubbling also lets a page-level listener react to clicks anywhere, such as closing a dropdown when the user clicks outside it.

## 🔴 यह क्यों बना? (Hindi)
मान लीजिए Swiggy cart में 50 "+" और "-" buttons हैं। Bubbling के बिना हर button पर अलग listener लगाना पड़ता। Bubbling से एक listener parent पर लगता है और सभी children के clicks पकड़ लेता है। साथ ही page-level listener पूरे page पर होने वाले clicks पर प्रतिक्रिया दे सकता है, जैसे dropdown के बाहर click होने पर उसे बंद करना।

---

## 🟢 How it Works — Step by Step

Step 1 → User clicks the inner `<button>`. The browser creates the event with `bubbles: true` (for click).
Step 2 → The event first reaches the target, the `<button>`. Its listeners run.
Step 3 → The event moves to the parent, `<div id="parent">`. Its listeners run.
Step 4 → It continues up to `<body>`, `<html>`, `document`, and finally `window`.
Step 5 → Any handler can call `event.stopPropagation()` to stop the travel. The remaining ancestors then do not get the event.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User अंदर के `<button>` पर click करता है। Browser event बनाता है जिसमें `bubbles: true` होता है (click के लिए)।
Step 2 → Event पहले target, यानी `<button>` पर पहुँचता है। उसके listeners चलते हैं।
Step 3 → Event parent `<div id="parent">` की तरफ बढ़ता है। उसके listeners चलते हैं।
Step 4 → यह आगे `<body>`, `<html>`, `document` और आखिर में `window` तक जाता है।
Step 5 → कोई भी handler `event.stopPropagation()` को call करके यात्रा रोक सकता है। फिर बाकी ancestors को event नहीं मिलता।

---

## 🟡 Real World Example
On Razorpay's checkout page, the "Pay" button sits inside a form, inside a card, inside the page body. A click on the button bubbles up through all of them. The form listens for `submit`, the card listens for clicks to expand details, and the page-level analytics script listens for every click to log it. None of these needs its own listener on the button. Amazon's cart page uses the same idea: one listener on the cart table handles the quantity buttons in every row.

## 🟡 Real Example Hindi mein
Razorpay के checkout page पर "Pay" button एक form के अंदर, एक card के अंदर, और page body के अंदर होता है। Button पर click ऊपर की सभी परतों से bubble होकर गुज़रता है। Form `submit` सुनता है, card click से details खोलता है, और page का analytics script हर click log करता है। इनमें से किसी को button पर अलग listener नहीं चाहिए। Amazon के cart page पर भी यही होता है: cart table पर एक listener हर row के quantity buttons को संभालता है।

---

## 💻 Code Example — Basic
Save as `event-bubbling-basic.html` and open it in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                  <!-- UTF-8 encoding -->
  <title>Event Bubbling Basic</title>                     <!-- tab title -->
</head>
<body>
  <div id="grandparent">                                  <!-- outermost box -->
    <div id="parent">                                     <!-- middle box -->
      <button id="child">Click me</button>                <!-- innermost: the real target -->
    </div>
  </div>
  <pre id="log"></pre>                                    <!-- output area -->

  <script>
    const log = document.getElementById("log");           // output element
    const order = [];                                     // names of handlers, in the order they ran

    document.getElementById("child").addEventListener("click", () => { // child listener
      order.push("child");                                // record that it ran
    });
    document.getElementById("parent").addEventListener("click", () => { // parent listener
      order.push("parent");                               // record that it ran
    });
    document.getElementById("grandparent").addEventListener("click", () => { // grandparent listener
      order.push("grandparent");                          // record that it ran
    });
    document.addEventListener("click", (e) => {           // document listener: near the top of the path
      order.push("document");                             // record that it ran
      // Show the order, the real target, and whether the event bubbles
      log.textContent = order.join(" -> ") +
        "\nevent.target = " + e.target.id +
        "\nevent.bubbles = " + e.bubbles;
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `event-bubbling-advanced.html`. It uses bubbling three ways: a delegated listener on a cart table, a dropdown that closes on an outside click, and a `stopPropagation()` call used only where it is needed. It also shows that `focusin` bubbles while `focus` does not.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                  <!-- UTF-8 for Hindi and the rupee sign -->
  <title>Event Bubbling Advanced</title>
  <style>
    .menu { display: none; border: 1px solid #999; padding: 8px; width: 200px; } /* hidden by default */
    .menu.open { display: block; }                        /* visible when the open class is added */
  </style>
</head>
<body>
  <table id="cart">                                       <!-- one listener on this table serves every row -->
    <tr data-item="Paneer"><td>Paneer</td><td><button data-op="inc">+</button><button data-op="dec">-</button></td><td class="qty">1</td></tr>
    <tr data-item="Roti"><td>Roti</td><td><button data-op="inc">+</button><button data-op="dec">-</button></td><td class="qty">2</td></tr>
  </table>

  <button id="toggle">Options</button>                    <!-- opens and closes the dropdown -->
  <div id="menu" class="menu">                            <!-- dropdown panel -->
    <input id="note" placeholder="Add a note">           <!-- focusable input inside the panel -->
  </div>
  <pre id="log"></pre>                                    <!-- output area -->

  <script>
    const cart = document.getElementById("cart");         // table for delegation
    const toggle = document.getElementById("toggle");     // dropdown button
    const menu = document.getElementById("menu");         // dropdown panel
    const logEl = document.getElementById("log");         // output area
    function logLine(t) { logEl.textContent += t + "\n"; } // helper: append one line

    // 1) Delegation: a click on any + or - bubbles up to the table
    cart.addEventListener("click", (e) => {               // runs for clicks anywhere in the table
      const btn = e.target.closest("button[data-op]");    // the quantity button, or null
      if (!btn) return;                                   // not a quantity button: ignore
      const row = btn.closest("tr");                      // the row this button belongs to
      const qtyCell = row.querySelector(".qty");          // the quantity cell in that row
      const current = Number(qtyCell.textContent);        // read the current number
      const next = btn.dataset.op === "inc"               // + increases the number
        ? current + 1
        : Math.max(0, current - 1);                       // - decreases, but never below zero
      qtyCell.textContent = String(next);                 // write the new number
      logLine(`${row.dataset.item} -> ${next} (handled on the table)`); // log it
    });

    // 2) Dropdown: stop this click from bubbling to document, or the outside-click rule would close it
    toggle.addEventListener("click", (e) => {             // handler on the toggle button
      e.stopPropagation();                                // stop the bubble here, on purpose
      menu.classList.toggle("open");                      // open or close the panel
    });

    // 3) Outside click: document is near the top of the bubble path, so it sees most clicks
    document.addEventListener("click", (e) => {           // runs for clicks that reach document
      if (!menu.contains(e.target)) {                     // the click was outside the panel
        menu.classList.remove("open");                    // close it
      }
    });

    // 4) focusin bubbles from the input up to the menu; focus does not bubble
    menu.addEventListener("focusin", (e) => {             // listener on the panel
      logLine("focusin reached the menu, target = " + e.target.id); // logs when the input gets focus
    });
    menu.addEventListener("focus", () => {                // NOT called for the input: focus does not bubble
      logLine("this line never prints for the input");    // kept to show the difference
    });
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Bubbling is a browser feature. There is no DOM on the server, so Express cannot bubble events. The closest real idea is Express's middleware chain: a request passes through layers in order, and each layer can call `next()` to pass control onward, much as an event passes from child to parent. The browser side uses bubbling to find the clicked row, then sends a request that the chain handles.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");                       // web framework
const app = express();                                    // create the app
app.use(express.json());                                  // parse JSON bodies

// Layer 1: runs for every request, like the first listener on the bubble path
app.use((req, res, next) => {                             // middleware with next()
  console.log(req.method, req.url);                       // log the method and path
  next();                                                 // pass control to the next layer
});

// Layer 2: the route that receives the delegated click (the "parent" handled the event in the browser)
app.post("/api/cart/:itemId/:op", (req, res, next) => {   // POST /api/cart/3/inc
  const { itemId, op } = req.params;                      // read the item id and operation from the URL
  if (!["inc", "dec"].includes(op)) {                     // validate the operation
    const err = new Error("operation must be inc or dec"); // build an error
    err.status = 400;                                     // attach an HTTP status
    return next(err);                                     // skip ahead to the error layer
  }
  res.json({ ok: true, itemId, op });                     // success response
});

// Error layer: has 4 arguments, runs only when next(err) is called
app.use((err, req, res, next) => {                        // error middleware
  res.status(err.status || 500).json({ error: err.message }); // send the error as JSON
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server

// Browser side: the table listener finds the row, then calls
// fetch(`/api/cart/${row.dataset.id}/${btn.dataset.op}`, { method: "POST" });
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling `stopPropagation()` to hide a bug
✅ Correct: Stopping the bubble also stops listeners on higher ancestors, such as `document` analytics or outside-click handlers. Fix the logic in the handler, and stop propagation only when you need to block the parent on purpose.

```html
<!-- Wrong: the button stops every click, so the outside-click handler never runs -->
<script>
  button.addEventListener("click", (e) => {
    e.stopPropagation();                                  // silences document listeners too
  });
  document.addEventListener("click", closeMenus);         // never gets this click
</script>

<!-- Right: let the event bubble and handle the case in the document listener -->
<script>
  document.addEventListener("click", (e) => {
    if (!e.target.closest("#menu, #toggle")) closeMenus(); // ignore only the clicks we care about
  });
  function closeMenus() {}                                 // placeholder for the real close logic
</script>
```

❌ **Mistake 2:** Expecting `focus`, `blur`, `mouseenter`, or `mouseleave` to bubble
✅ Correct: These events do not bubble. Use `focusin` and `focusout` for focus on children, or add the listener on the element itself, or use capture (topic 145).

```html
<!-- Wrong: a focus listener on the form never runs when an input inside it gets focus -->
<script>
  form.addEventListener("focus", () => console.log("focused")); // focus does not bubble
</script>

<!-- Right: focusin bubbles, so the form hears when any child input gets focus -->
<script>
  form.addEventListener("focusin", (e) => console.log("focused", e.target.name)); // works
</script>
```

❌ **Mistake 3:** Thinking the parent's listener runs before the child's
✅ Correct: In bubbling, the target runs first and the ancestors run after, in that order. Only the capture phase runs parents first.

```html
<!-- Wrong: assuming parent runs first -->
<script>
  parent.addEventListener("click", () => console.log("parent first"));
  child.addEventListener("click", () => console.log("child first"));
  child.click(); // prints "child first", then "parent first"
</script>
```

---

## 🧠 Tricky Interview Question
What is printed when the button is clicked? Paste the script into a page with these elements.

```html
<div id="a">                                              <!-- outer box -->
  <div id="b">                                            <!-- middle box -->
    <button id="c">x</button>                             <!-- innermost button -->
  </div>
</div>

<script>
  const c = document.getElementById("c");                 // the button
  c.addEventListener("click", (e) => {                    // first listener on c
    console.log("c1");                                    // print c1
    e.stopPropagation();                                  // stop going up to b, a, and document
  });
  c.addEventListener("click", () => {                     // second listener on the same element
    console.log("c2");                                    // print c2
  });
  document.getElementById("b").addEventListener("click", () => console.log("b")); // middle listener
  document.addEventListener("click", () => console.log("document"));              // top listener
  c.click();                                              // simulate a click on the button
</script>
```

Answer: The output is:
```
c1
c2
```
Explanation: `stopPropagation()` stops the event from moving to the next element up the path, so `b` and `document` never run. It does not stop other listeners on the same element `c`. The second listener on `c` still runs, because the event is still at `c`. If you want to stop the other listeners on the same element too, use `e.stopImmediatePropagation()`.

---

## ⚫ Interview Questions + Answers

Q1: What is event bubbling?
A1: It is the default way events travel. The event starts at the target element and moves up through its ancestors, until it reaches `document` and `window`. Listeners on each ancestor run in that order.

Q2: Which events bubble?
A2: Most UI events bubble, including `click`, `input`, `change`, `keydown`, `submit`, `focusin`, and `focusout`. Events such as `focus`, `blur`, `mouseenter`, `mouseleave`, and `load` on an image do not bubble.

Q3: What is the difference between `stopPropagation()` and `preventDefault()`?
A3: `stopPropagation()` stops the event from reaching other elements. `preventDefault()` stops the browser's default action, such as following a link or submitting a form. You can call one without the other.

Q4: How does `bubbles` relate to event delegation?
A4: Delegation depends on bubbling. Because a click on a child bubbles to the parent, one parent listener can handle all children, and it uses `event.target` to find which child was clicked.

Q5: What is `stopImmediatePropagation()`?
A5: It stops the event from reaching other elements, and it also stops the remaining listeners on the current element. Use it only when a later listener must never run.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want one listener on a parent to handle many child elements (delegation)
- You want a page-level listener to see clicks from anywhere, such as analytics or outside-click handling
- You want to check `event.target` in a shared handler

❌ Avoid when:
- You call `stopPropagation()` just to stop a bug, since it breaks other listeners
- You rely on `focus`, `blur`, or `mouseenter` to bubble (they do not)
- You attach the same listener to hundreds of children when one parent listener would do

---

## 📊 Visual Diagram
```
Click on <button id="c">

  Bubble path (target first, then up):

  [1] <button id="c">      <-- target: c1 runs, then c2 (same element)
        |
        v   stopPropagation() called in c1 blocks the climb here
  [2] <div id="b">         <-- NOT reached
        |
  [3] <div id="a">         <-- NOT reached
        |
  [4] document             <-- NOT reached
        |
  [5] window               <-- NOT reached

  Without stopPropagation: c -> b -> a -> document -> window
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bubbling | Event travels from target up to ancestors | Event का target से ऊपर की तरफ जाना |
| Target | The innermost element where the event starts | जहाँ से event शुरू होता है |
| Ancestor | A parent, grandparent, and so on | Parent, दादा-परदादा जैसे ऊपर के elements |
| `stopPropagation()` | Stops the event from moving to the next ancestor | Event को आगे जाने से रोकना |
| `stopImmediatePropagation()` | Also stops the other listeners on the same element | उसी element के बाकी listeners भी रोकना |
| `bubbles` | Property that tells whether the event bubbles | Event ऊपर जाता है या नहीं, यह बताने वाली property |
| `focusin` | Focus event that bubbles | ऊपर तक जाने वाला focus event |
| Delegation | One parent listener handles many children | एक parent listener से कई children संभालना |

---

## ⚡ 3-Line Summary
**English:**
1. Bubbling sends an event from the target up through every ancestor to `document` and `window`.
2. One parent listener can handle many children because the click bubbles up to it.
3. `stopPropagation()` blocks the climb and can break other listeners, so use it only on purpose.

**Hindi:**
1. Bubbling में event target से ऊपर के हर ancestor, `document` और `window` तक जाता है।
2. क्योंकि click ऊपर bubble होता है, एक parent listener कई children को संभाल सकता है।
3. `stopPropagation()` ऊपर जाने को रोकता है और दूसरे listeners को तोड़ सकता है, इसलिए इसे सोच-समझकर ही use करें।

---

## ➡️ Next Topic
**145. Event Capturing** — अब सीखेंगे कि event ऊपर से नीचे target तक कैसे जाता है, और capture listeners कब उपयोगी होते हैं।
