# 141. Events — Complete Guide
# हिंदी में: Events — पूरी गाइड

---

## 🔵 Simple Definition (English)
An event is a signal that something happened in the browser: a click, a key press, a typed letter, a form submit, or the page finishing loading. JavaScript listens for events on a node and runs a function (a handler) when the event happens.

## 🔵 सरल परिभाषा (Hindi)
Event वह signal है जो बताता है कि browser में कुछ हुआ: click, key press, टाइप किया गया letter, form submit, या page load पूरा होना। JavaScript किसी node पर events को सुनता है और event होने पर एक function (handler) चलाता है।

---

## 🔴 Problem it Solves
Without events, a page could only run code when it loaded. Users would click buttons, type into search boxes, or scroll, and nothing would happen. Events connect user actions and browser activity to your code. Older code used inline attributes like `onclick="..."` mixed with HTML, which was hard to maintain. The standard event system (DOM Events) gives a clean, flexible way to attach many handlers, control their order, and stop unwanted default behavior.

## 🔴 यह क्यों बना? (Hindi)
Events के बिना page सिर्फ load होने पर code चला सकता था। User button दबाता, search box में टाइप करता, या scroll करता, और कुछ नहीं होता। Events user action और browser की activity को आपके code से जोड़ते हैं। पुराना code `onclick="..."` जैसे inline attributes HTML में मिलाता था, जो maintain करना मुश्किल था। Standard event system कई handlers जोड़ने, उनका क्रम संभालने, और default behavior रोकने का साफ तरीका देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → The browser creates an Event object when something happens (for example `click`), and sets its `target` to the node that was acted on.
Step 2 → The event travels through three phases: capture (down from window to target), target, and bubble (up from target to window).
Step 3 → Listeners registered with `addEventListener` on nodes along the path run when the event passes them.
Step 4 → Handlers can call `event.preventDefault()` to block default behavior (like form submit reloading the page) and `event.stopPropagation()` to stop the travel.
Step 5 → Some events are built-in (`click`, `input`, `submit`, `DOMContentLoaded`), and you can create your own with `new CustomEvent` and send it with `dispatchEvent`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → कुछ होने पर browser एक Event object बनाता है (जैसे `click`), और उसका `target` उस node पर सेट करता है जिस पर action हुआ।
Step 2 → Event तीन phases से गुज़रता है: capture (window से target तक नीचे), target, और bubble (target से window तक ऊपर)।
Step 3 → `addEventListener` से लगाए गए listeners, जो event के रास्ते में आते हैं, चलते हैं।
Step 4 → Handler `event.preventDefault()` से default behavior रोक सकता है (जैसे form submit से page reload होना) और `event.stopPropagation()` से यात्रा रोक सकता है।
Step 5 → कुछ events built-in हैं (`click`, `input`, `submit`, `DOMContentLoaded`), और अपने events `new CustomEvent` से बनाकर `dispatchEvent` से भेज सकते हैं।

---

## 🟡 Real World Example
On Zomato's checkout, pressing "Place Order" submits a form. The app calls `preventDefault()` on the submit event so the page does not reload, then sends the order with `fetch`. While typing an address, the `input` event fires on every key stroke to show suggestions. When the cart count changes, the app dispatches a custom `cart:updated` event so the header badge can update without the cart code knowing about the header. Analytics on Flipkart use `navigator.sendBeacon` on `pagehide` to send click data even as the user leaves.

## 🟡 Real Example Hindi mein
Zomato के checkout पर "Place Order" दबाने से form submit होता है। App submit event पर `preventDefault()` लगाता है ताकि page reload न हो, फिर `fetch` से order भेजता है। Address टाइप करते समय हर key पर `input` event चलता है और suggestions दिखते हैं। Cart count बदलने पर app एक custom `cart:updated` event भेजता है, ताकि header badge बदल जाए और cart का code header को न जाने। Flipkart की analytics user के page छोड़ते समय `pagehide` पर `navigator.sendBeacon` से click data भेजती है।

---

## 💻 Code Example — Basic
Save as `events-basic.html` and open it in a browser. Watch the DevTools Console while you click and type.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Events Basic</title>
</head>
<body>
  <button id="like">Like (0)</button>          <!-- button whose text we update -->
  <input id="search" placeholder="Search dish"> <!-- text box for the input event -->
  <form id="order">                             <!-- form for the submit event -->
    <button type="submit">Place order</button>  <!-- submit button inside the form -->
  </form>

  <script>
    // DOMContentLoaded fires when the HTML is parsed (before images finish loading)
    document.addEventListener("DOMContentLoaded", () => {
      console.log("DOM is ready");              // runs after parsing finishes
    });

    // Click event: count the likes
    let likes = 0;                              // our counter
    const likeBtn = document.getElementById("like"); // the button node
    likeBtn.addEventListener("click", () => {   // run this every time the button is clicked
      likes++;                                  // increase the counter
      likeBtn.textContent = `Like (${likes})`;  // show the new count
    });

    // Input event: fires on every change to the text box
    const search = document.getElementById("search"); // the input node
    search.addEventListener("input", (event) => {     // event.target is the input
      console.log("Typing:", event.target.value);     // print the current text
    });

    // Submit event: stop the page from reloading and handle it ourselves
    document.getElementById("order").addEventListener("submit", (event) => {
      event.preventDefault();                   // block the default form submit (page reload)
      console.log("Order placed (no reload)");  // our own handling
    });

    // Custom event: any code can announce a change, and any code can listen
    document.addEventListener("cart:updated", (event) => {  // listen on document
      console.log("Cart now has", event.detail.count, "items"); // detail carries data
    });
    // Dispatch the custom event: bubbles so document listeners can hear it
    document.dispatchEvent(new CustomEvent("cart:updated", { detail: { count: 3 } }));

    // load event on window: fires after images, styles, and scripts finish loading
    window.addEventListener("load", () => {
      console.log("Page fully loaded");          // runs last
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `events-advanced.html`. It uses a passive scroll listener, `once`, an `AbortController` to remove a group of listeners at once, and a custom event with error handling.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Events Advanced</title>
  <style>
    body { height: 2000px; }                    /* tall page so we can scroll */
    #toast { position: fixed; bottom: 16px; }  /* fixed toast at the bottom */
  </style>
</head>
<body>
  <button id="start">Start tracking</button>    <!-- starts a set of listeners -->
  <button id="stop">Stop tracking</button>      <!-- removes all of them at once -->
  <div id="toast"></div>                        <!-- where messages are shown -->

  <script>
    const toast = document.getElementById("toast"); // message area

    // A single AbortController can remove many listeners in one call
    let controller = null;                      // will hold the controller while tracking

    document.getElementById("start").addEventListener("click", () => {
      controller = new AbortController();       // create a fresh controller
      const { signal } = controller;            // the signal we pass to each listener

      // passive: true tells the browser we will not call preventDefault, so scrolling stays smooth
      window.addEventListener("scroll", () => {
        toast.textContent = `Scrolled to ${Math.round(scrollY)}px`; // show scroll position
      }, { passive: true, signal });            // removed automatically when signal aborts

      // once: true runs this handler only the first time the user presses a key
      window.addEventListener("keydown", (e) => {
        toast.textContent = `First key was: ${e.key}`; // show the first key pressed
      }, { once: true, signal });                // also removed on abort

      toast.textContent = "Tracking started";   // confirm to the user
    });

    document.getElementById("stop").addEventListener("click", () => {
      if (controller) {                          // only if we started tracking
        controller.abort();                      // remove every listener that used this signal
        controller = null;                       // reset the reference
        toast.textContent = "Tracking stopped";  // confirm to the user
      }
    });

    // Custom event with validation: listeners receive detail and may reject bad data
    function emitCartUpdate(count) {            // helper that dispatches the event
      if (!Number.isInteger(count) || count < 0) { // validate before sending
        throw new RangeError(`Invalid count: ${count}`); // fail loudly on bad input
      }
      const evt = new CustomEvent("cart:updated", {  // create the event
        detail: { count },                       // data for listeners
        bubbles: true,                           // let it travel up to document
        cancelable: true,                        // allow listeners to call preventDefault
      });
      const notAllowed = !document.body.dispatchEvent(evt); // false if preventDefault was called
      if (notAllowed) console.log("A listener cancelled the update");
    }

    // Listener that cancels updates above 10 items
    document.addEventListener("cart:updated", (e) => {
      if (e.detail.count > 10) e.preventDefault(); // cancel the update, signal to dispatcher
    });

    try {
      emitCartUpdate(3);                          // valid: no cancel
      emitCartUpdate(-1);                         // invalid: throws RangeError
    } catch (err) {                               // catch the thrown error
      console.error(err.name, err.message);       // print the error name and message
    }
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Browser events often need to reach the server, for example analytics. `navigator.sendBeacon` sends data reliably even when the page is closing. Express receives it on a POST route.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");                 // web framework
const app = express();                              // create app

// Parse JSON bodies; sendBeacon sends the Blob with type application/json
app.use(express.json({ limit: "10kb" }));           // limit body size to protect the server

// Receive click and page events from the browser
app.post("/api/analytics", (req, res) => {          // handle POST /api/analytics
  const { type, target, at } = req.body || {};      // read the event fields
  if (typeof type !== "string") {                   // basic validation
    return res.status(400).json({ error: "type is required" }); // reject bad data
  }
  console.log(`[analytics] ${type} on ${target} at ${at}`); // store or forward in real life
  res.status(204).end();                            // 204 No Content: success, nothing to return
});

app.listen(3000, () => console.log("Analytics on http://localhost:3000"));

// Browser side (inside your page script):
// window.addEventListener("pagehide", () => {
//   const payload = JSON.stringify({ type: "leave", target: "/checkout", at: Date.now() });
//   navigator.sendBeacon("/api/analytics", new Blob([payload], { type: "application/json" }));
// });
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `element.onclick = ...` and expecting both handlers to run
✅ Correct: A property holds only one handler, so a second assignment replaces the first. Use `addEventListener` to attach many.

```javascript
// Wrong — the second assignment silently overwrites the first
btn.onclick = () => console.log("A");
btn.onclick = () => console.log("B");   // only B runs

// Right — both listeners run
btn.addEventListener("click", () => console.log("A"));
btn.addEventListener("click", () => console.log("B")); // A and B both run
```

❌ **Mistake 2:** Forgetting `preventDefault()` on a form submit, so the page reloads
✅ Correct: Call `preventDefault()` in the submit handler when you handle the form with JavaScript.

```javascript
// Wrong — the browser submits the form and reloads the page
form.addEventListener("submit", () => sendOrder());

// Right — stop the default reload first
form.addEventListener("submit", (event) => {
  event.preventDefault();   // block the default navigation
  sendOrder();              // handle it with fetch
});
```

❌ **Mistake 3:** Calling `preventDefault()` inside a passive listener
✅ Correct: Passive listeners (the default for window/document `touchstart`, `touchmove`, and `wheel` in modern browsers) ignore `preventDefault()`. Pass `{ passive: false }` if you must block scrolling, and only when needed.

```javascript
// Wrong — the browser ignores this and still scrolls (warning in console)
window.addEventListener("wheel", (e) => e.preventDefault());

// Right — explicitly non-passive when you truly need to block scrolling
window.addEventListener("wheel", (e) => e.preventDefault(), { passive: false });
```

---

## 🧠 Tricky Interview Question
Run this in the console on a page with a `<button id="b">`.

```javascript
const btn = document.getElementById("b");   // the button

btn.onclick = () => console.log("prop 1");  // property handler, first assignment
btn.addEventListener("click", () => console.log("listener"));  // second handler
btn.onclick = () => console.log("prop 2");  // property handler, second assignment

btn.click();                                // simulate a click
```

Answer: The output is:
```
prop 2
listener
```
The property `onclick` is one slot in the browser's listener list. It is registered at the moment you first assign it, which is before the `addEventListener` call. Assigning `onclick` again does not add a new listener; it replaces the function stored in that same slot. So the slot keeps its original position (first) and now holds `prop 2`. `prop 1` is gone entirely. The `addEventListener` listener is a separate entry, so it still runs second. This is why mixing `onclick` with `addEventListener` leads to confusing bugs.

---

## ⚫ Interview Questions + Answers

Q1: What are the three ways to attach an event handler?
A1: Inline HTML attributes (`onclick="..."`), DOM properties (`element.onclick = fn`), and `addEventListener`. `addEventListener` is preferred because it can attach many handlers, supports options like `once` and `passive`, and keeps JavaScript out of HTML.

Q2: What is the difference between `DOMContentLoaded` and `load`?
A2: `DOMContentLoaded` fires when the HTML has been parsed and the DOM is ready, without waiting for images or stylesheets. `load` fires later, after all resources such as images and external resources are loaded.

Q3: What does `preventDefault()` do, and what does it not do?
A3: It cancels the default browser action, such as form submission, link navigation, or scrolling with some events. It does not stop the event from traveling to other listeners. Use `stopPropagation()` for that. It only works when the event is `cancelable`.

Q4: What is a custom event, and why use one?
A4: You create it with `new CustomEvent(name, { detail, bubbles, cancelable })` and send it with `dispatchEvent`. It lets parts of the app communicate without direct references, such as a cart module telling a header to update.

Q5: Why use `navigator.sendBeacon` for analytics?
A5: `sendBeacon` queues a small POST request that the browser sends even when the page is closing or navigating away. A normal `fetch` may be cancelled in that moment. It does not wait for a response, so it does not slow down the page.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Responding to user actions: click, input, submit, keydown
- Handling page lifecycle: `DOMContentLoaded`, `load`, `visibilitychange`
- Decoupling components with custom events

❌ Avoid when:
- Using inline `onclick` attributes in HTML (hard to maintain and blocked by strict Content Security Policy)
- Attaching a listener to every item in a large list; use event delegation instead
- Relying on `onclick` property assignments when several parts of the code need to listen

---

## 📊 Visual Diagram
```
An event: a click on the <button> inside <div id="menu"> inside <body>

 window ──┐  CAPTURE phase (top → down)
 document │
 body     │
 div#menu │
 button   ◄── TARGET phase (event.target)
 div#menu │
 body     │  BUBBLE phase (bottom → up)
 document │
 window ──┘

addEventListener(type, fn, { capture, once, passive, signal })
  capture: true  -> runs during the capture phase
  default        -> runs during bubble (and at target)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | Signal that something happened | कुछ होने का signal |
| Handler / Listener | Function that runs for an event | Event पर चलने वाला function |
| Target | Node where the event started | जिस node पर event हुआ |
| preventDefault | Cancels the default browser action | Browser का default action रोकना |
| stopPropagation | Stops the event from traveling further | Event की यात्रा रोकना |
| CustomEvent | Your own event with data in detail | `detail` में data वाला अपना event |
| sendBeacon | Sends data reliably while leaving the page | Page छोड़ते समय data भेजना |
| AbortController | Removes listeners with one signal | एक signal से listeners हटाना |

---

## ⚡ 3-Line Summary
**English:**
1. An event is a browser signal; you attach handlers with `addEventListener` and read details from the event object.
2. Events travel in capture, target, and bubble phases; `preventDefault` stops default actions, `stopPropagation` stops travel.
3. Use custom events to communicate, `sendBeacon` for reliable analytics, and remember that a property like `onclick` holds only one handler.

**Hindi:**
1. Event browser का signal है; handler `addEventListener` से जोड़ें और details event object से पढ़ें।
2. Events capture, target, और bubble phases में चलते हैं; `preventDefault` default action रोकता है, `stopPropagation` यात्रा रोकता है।
3. Communication के लिए custom events, भरोसेमंद analytics के लिए `sendBeacon` इस्तेमाल करें, और याद रखें कि `onclick` जैसी property में सिर्फ एक handler रहता है।

---

## ➡️ Next Topic
**142. Event Listeners (addEventListener, removeEventListener)** — अब सीखेंगे कि listeners को सही तरीके से जोड़ना और हटाना कैसे है, और memory leaks कैसे रोकें।
