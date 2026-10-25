# 143. Event Object (target, currentTarget, type)
# हिंदी में: Event Object (target, currentTarget, type)

---

## 🔵 Simple Definition (English)
When an event fires, the browser passes your handler an **event object** that describes what happened: its `type` (like "click"), the element where the event started (`target`), and the element whose listener is running right now (`currentTarget`). Think of it as the receipt of the event.

## 🔵 सरल परिभाषा (Hindi)
जब कोई event होता है, browser आपके handler को एक **event object** देता है, जो बताता है कि क्या हुआ: उसका `type` (जैसे "click"), वह element जहाँ से event शुरू हुआ (`target`), और वह element जिसका listener अभी चल रहा है (`currentTarget`)। इसे event की रसीद (receipt) समझें।

---

## 🔴 Problem it Solves
Without an event object, a handler would only know that "something was clicked", not which item, which button, or where. A menu with 200 dishes needs to know which dish was tapped. The event object carries that information, so one handler can serve many elements.

## 🔴 यह क्यों बना? (Hindi)
Event object के बिना handler को सिर्फ़ इतना पता होता कि "कुछ click हुआ है", पर कौन-सा item या कहाँ, यह नहीं। 200 dishes वाले menu को पता होना चाहिए कि किस dish पर tap हुआ। Event object यही जानकारी देता है, इसलिए एक ही handler कई elements के लिए काम कर सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → User clicks an `<li>` inside a `<ul>`. The browser creates an Event object.
Step 2 → `event.target` is set to the innermost element that was actually clicked (the `<li>`, or a `<span>` inside it).
Step 3 → `event.currentTarget` is set to the element whose listener is running (the `<ul>`, if the handler is attached to the `<ul>`).
Step 4 → `event.type` holds the event name, such as "click".
Step 5 → When the dispatch finishes, `event.currentTarget` becomes `null`. Save what you need while the handler runs.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User `<ul>` के अंदर के `<li>` पर click करता है। Browser एक Event object बनाता है।
Step 2 → `event.target` को वह सबसे अंदरूनी element मिलता है जिस पर सचमुच click हुआ (`<li>` या उसके अंदर का `<span>`)।
Step 3 → `event.currentTarget` उस element को मिलता है जिसका listener अभी चल रहा है (handler `<ul>` पर हो तो `<ul>`)।
Step 4 → `event.type` में event का नाम रहता है, जैसे "click"।
Step 5 → Dispatch खत्म होने पर `event.currentTarget` `null` हो जाता है। ज़रूरी value handler चलते समय ही save कर लें।

---

## 🟡 Real World Example
On Zomato's restaurant menu, every "Add" button shares one click handler on the menu container. When a user taps "Add" on Paneer Butter Masala, `event.target` is the button and `event.currentTarget` is the menu container. The handler calls `event.target.closest("[data-dish-id]")` to find which dish was tapped. Amazon's product grid works the same way: one handler, many product cards.

## 🟡 Real Example Hindi mein
Zomato के restaurant menu में हर "Add" button के लिए एक ही click handler menu container पर लगा होता है। User "Paneer Butter Masala" पर "Add" दबाता है, तो `event.target` वह button है और `event.currentTarget` menu container। Handler `event.target.closest("[data-dish-id]")` से पता लगाता है कि कौन-सा dish चुना गया। Amazon की product grid भी ऐसे ही काम करती है: एक handler, कई product cards।

---

## 💻 Code Example — Basic
Save as `event-object-basic.html` and open it in a browser. No server needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                      <!-- UTF-8 so Hindi text shows correctly -->
  <title>Event Object Basic</title>                           <!-- tab title -->
</head>
<body>
  <ul id="menu">                                              <!-- parent list: the listener goes here -->
    <li data-dish="Dal Makhani"><span>Dal Makhani</span></li> <!-- item with a span inside -->
    <li data-dish="Naan"><span>Naan</span></li>               <!-- second item -->
  </ul>
  <pre id="log"></pre>                                        <!-- output area for the event info -->

  <script>
    const menu = document.getElementById("menu");             // the element that owns the listener
    const log = document.getElementById("log");               // where we print the results

    menu.addEventListener("click", (event) => {               // handler receives the event object
      const lines = [];                                       // collect the lines to print
      lines.push("type: " + event.type);                      // "click"
      lines.push("target: " + event.target.tagName);          // SPAN if you hit the text, LI if you hit the padding
      lines.push("currentTarget: " + event.currentTarget.id); // "menu", the element with the listener
      lines.push("isTrusted: " + event.isTrusted);            // true for a real user click, false for .click()
      log.textContent = lines.join("\n");                     // show all lines inside the <pre>
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `event-object-advanced.html`. One delegated listener on the menu handles every dish. It reads the dish from `event.target`, reads the price from `dataset`, guards against missing elements, and keeps the cart total correct.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                      <!-- UTF-8 for the rupee sign and Hindi -->
  <title>Event Object Advanced</title>
</head>
<body>
  <ul id="menu">                                              <!-- one listener on this list serves all dishes -->
    <li data-dish-id="1" data-price="250">                    <!-- dish row: id and price stored as data attributes -->
      <span class="name">Paneer Butter Masala</span>          <!-- name text, clicking it is also valid -->
      <button data-action="add">Add</button>                  <!-- add one portion -->
      <button data-action="remove">Remove</button>            <!-- remove one portion -->
    </li>
    <li data-dish-id="2" data-price="60">                     <!-- second dish row -->
      <span class="name">Garlic Naan</span>                   <!-- name of the second dish -->
      <button data-action="add">Add</button>                  <!-- add button for naan -->
    </li>
  </ul>
  <p>Cart total: ₹<span id="total">0</span></p>               <!-- running total in rupees -->
  <pre id="log"></pre>                                        <!-- debug output -->

  <script>
    const menu = document.getElementById("menu");             // delegated listener lives here
    const totalEl = document.getElementById("total");         // shows the total
    const logEl = document.getElementById("log");             // debug output
    const cart = new Map();                                   // dish id (string) -> quantity

    function logLine(text) {                                  // helper: append one line
      logEl.textContent += text + "\n";                        // add the text and a newline
    }

    menu.addEventListener("click", (event) => {               // runs for every click inside the menu
      // event.target can be the span, a button, or the li; closest() finds the dish row
      const row = event.target.closest("li[data-dish-id]");   // the <li> that owns this click
      if (!row) return;                                       // no dish row: ignore the click

      // event.target may also be a button; closest() returns null when it is not a button
      const btn = event.target.closest("button[data-action]");// the action button, if one was clicked
      if (!btn) {                                             // the name was clicked, not a button
        logLine("Dish info: " + row.querySelector(".name").textContent); // just show the name
        return;                                               // nothing more to do
      }

      const id = row.dataset.dishId;                          // "1" or "2" from data-dish-id
      const price = Number(row.dataset.price);                // dataset values are strings, so convert
      const qty = cart.get(id) ?? 0;                          // current quantity, default 0

      if (btn.dataset.action === "add") {                     // the Add button
        cart.set(id, qty + 1);                                // one more portion
      } else if (btn.dataset.action === "remove" && qty > 0) {// Remove, but never below zero
        cart.set(id, qty - 1);                                // one less portion
      }

      let total = 0;                                          // start the total at zero
      for (const [dishId, count] of cart) {                   // walk every dish in the cart
        const item = menu.querySelector(`[data-dish-id="${dishId}"]`); // find its row again
        if (!item) continue;                                  // error guard: skip unknown dish
        total += Number(item.dataset.price) * count;          // price times quantity
      }
      totalEl.textContent = String(total);                    // show the new total
      // event.type and event.currentTarget are still valid here because we are inside the handler
      logLine(`${event.type} on ${btn.dataset.action} for dish ${id}, currentTarget=${event.currentTarget.id}`);
    });
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
The event object exists only in the browser, so Express never sees `event.target`. Express receives the data the handler sends. The menu handler reads `dataset` values from the event and posts them to the server, which checks the price itself.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");                          // web framework
const app = express();                                       // create the app
app.use(express.json());                                     // parse JSON bodies into req.body
app.use(express.static(__dirname + "/public"));              // serve public/index.html with the handler

// Server-side price list: the source of truth (never trust a price sent by the browser)
const DISHES = {
  1: { name: "Paneer Butter Masala", price: 250 },           // dish id 1
  2: { name: "Garlic Naan", price: 60 },                     // dish id 2
};

// The browser handler sends { dishId, action } built from row.dataset and btn.dataset
app.post("/api/cart", (req, res) => {                        // POST /api/cart
  const { dishId, action } = req.body || {};                 // read the fields, default to {}
  const dish = DISHES[dishId];                               // look up the dish by id
  if (!dish) {                                               // unknown id
    return res.status(404).json({ error: "dish not found" }); // 404 Not Found
  }
  if (!["add", "remove"].includes(action)) {                 // validate the action string
    return res.status(400).json({ error: "action must be add or remove" }); // 400 Bad Request
  }
  // In a real app, update the cart for the logged-in user in a database here
  res.json({ ok: true, dish: dish.name, price: dish.price, action }); // echo the accepted change
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server

// Browser side, inside the menu click handler:
// fetch("/api/cart", { method: "POST", headers: { "Content-Type": "application/json" },
//   body: JSON.stringify({ dishId: Number(row.dataset.dishId), action: btn.dataset.action }) });
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `event.target` when the listener's own element is needed
✅ Correct: Use `event.currentTarget` for the element with the listener, or `closest()` on `event.target` for the element you care about.

```html
<!-- Wrong: if the user clicks the inner <span>, target is the span and has no dataset.dishId -->
<script>
  menu.addEventListener("click", (e) => {
    console.log(e.target.dataset.dishId);                   // undefined when the span is clicked
  });
</script>

<!-- Right: walk up from the target to the row that has the attribute -->
<script>
  menu.addEventListener("click", (e) => {
    const row = e.target.closest("li[data-dish-id]");       // always the <li>
    console.log(row.dataset.dishId);                        // reliable value
  });
</script>
```

❌ **Mistake 2:** Reading `event.currentTarget` after the handler has finished
✅ Correct: `currentTarget` is `null` once dispatch ends. Copy the value into a variable during the handler.

```html
<!-- Wrong: the timer runs after dispatch, so currentTarget is already null -->
<script>
  menu.addEventListener("click", (e) => {
    setTimeout(() => console.log(e.currentTarget.id), 0);   // TypeError: Cannot read properties of null
  });
</script>

<!-- Right: save the element first, then use it later -->
<script>
  menu.addEventListener("click", (e) => {
    const list = e.currentTarget;                           // copy the element now
    setTimeout(() => console.log(list.id), 0);              // prints "menu"
  });
</script>
```

❌ **Mistake 3:** Using `this` in an arrow function and expecting the element
✅ Correct: Arrow functions do not have their own `this`. In a normal `function`, `this` equals `currentTarget`.

```html
<!-- Wrong: `this` is the outer scope (window in a plain script), not the menu -->
<script>
  menu.addEventListener("click", (e) => console.log(this.id)); // prints "" or undefined
</script>

<!-- Right: use a normal function, or read e.currentTarget -->
<script>
  menu.addEventListener("click", function (e) {
    console.log(this.id, e.currentTarget.id);               // both print "menu"
  });
</script>
```

---

## 🧠 Tricky Interview Question
What is printed? Save as an HTML page and open it, or paste the script into a page that has these elements.

```html
<div id="outer">                                <!-- outer box with the listener -->
  <button id="inner">Pay</button>               <!-- inner button that will be clicked -->
</div>

<script>
  const outer = document.getElementById("outer");          // the element with the listener
  outer.addEventListener("click", (e) => {                 // handler on outer
    console.log("1", e.target.id, e.currentTarget.id);     // print during dispatch
    setTimeout(() => {                                     // runs after dispatch ends
      console.log("2", e.target.id, e.currentTarget);      // print target and currentTarget later
    }, 0);
  });
  document.getElementById("inner").click();                // synthetic click on the button
</script>
```

Answer: The output is:
```
1 inner outer
2 inner null
```
Explanation: During the click, `event.target` is the button (`inner`), because that is where the click started. `event.currentTarget` is `outer`, because that is the element whose listener is running. The `setTimeout` callback runs after the browser finishes dispatching the event. At that point the browser resets `currentTarget` to `null`, but `target` still points to the button. So the first line is correct and the second line shows `null` for `currentTarget`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `event.target` and `event.currentTarget`?
A1: `target` is the element where the event started (the innermost element clicked). `currentTarget` is the element whose listener is currently running. They are the same only when the listener is on the clicked element itself.

Q2: What does `event.type` contain?
A2: The name of the event as a string, such as "click", "input", "keydown", or "submit". It is the same name you passed to `addEventListener`.

Q3: Why do we use `closest()` inside a delegated handler?
A3: The user may click a child element, such as a `<span>` inside a button. `closest(selector)` walks up from `event.target` and returns the nearest matching ancestor, or `null` if none matches. This makes the handler reliable for nested markup.

Q4: What is `event.isTrusted`?
A4: It is `true` when the browser created the event from a real user action, such as a mouse or keyboard input. It is `false` for events created by code, such as `element.click()` or `new Event("click")`.

Q5: Can you call `preventDefault()` on the event object?
A5: Yes, when the event is `cancelable`. Check `event.cancelable` first. Calling `preventDefault()` stops the default action, such as following a link or submitting a form, and sets `event.defaultPrevented` to `true`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to know which element was clicked or typed into
- One handler serves many similar elements, such as menu items or table rows
- You need the event type or extra details, such as keys pressed or input values

❌ Avoid when:
- You read `event.currentTarget` after the handler has ended (it is `null` then)
- You assume `target` is always the element with the listener (it is often a child)
- You need data that is not in the event; store it in your app state instead

---

## 📊 Visual Diagram
```
<ul id="menu">                              <-- currentTarget: the listener is attached here
  <li data-dish-id="1">                     <-- closest("li[data-dish-id]") returns this row
    <span class="name">Paneer</span>        <-- event.target when the name text is clicked
    <button data-action="add">Add</button>  <-- event.target when the Add button is clicked
  </li>
</ul>

Click on the Add button:
  event.type          = "click"
  event.target        = <button>             (where the click started)
  event.currentTarget = <ul id="menu">       (where the listener is running)
  after dispatch      -> event.currentTarget = null
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event object | Object passed to the handler that describes the event | Handler को मिलने वाला event का विवरण |
| `type` | Name of the event, such as "click" | Event का नाम |
| `target` | Element where the event started | जहाँ से event शुरू हुआ वह element |
| `currentTarget` | Element whose listener is running now | जिस element का listener अभी चल रहा है |
| `closest()` | Finds the nearest matching ancestor, including itself | सबसे नज़दीकी matching ancestor ढूँढना |
| `isTrusted` | True when a real user caused the event | असली user action से आया event |
| `dataset` | Access to `data-*` attributes as strings | `data-*` attributes की values |
| `cancelable` | True when `preventDefault()` has an effect | जिस event का default रोका जा सकता है |

---

## ⚡ 3-Line Summary
**English:**
1. The event object tells the handler what happened: `type`, `target` (where it started), and `currentTarget` (where the listener is).
2. Use `closest()` on `target` to find the real item in a delegated handler, and copy `currentTarget` before any async code.
3. `currentTarget` becomes `null` after dispatch, so never read it inside a timer or promise callback.

**Hindi:**
1. Event object handler को बताता है कि क्या हुआ: `type`, `target` (कहाँ से शुरू हुआ) और `currentTarget` (listener कहाँ है)।
2. Delegated handler में असली item ढूँढने के लिए `target` पर `closest()` लगाएँ, और async code से पहले `currentTarget` को copy कर लें।
3. Dispatch के बाद `currentTarget` `null` हो जाता है, इसलिए timer या promise callback में इसे कभी न पढ़ें।

---

## ➡️ Next Topic
**144. Event Bubbling** — अब सीखेंगे कि event नीचे के element से ऊपर के parents तक कैसे जाता है, और यही delegation की नींव क्यों है।
