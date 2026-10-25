# 142. Event Listeners (addEventListener, removeEventListener)
# हिंदी में: Event Listeners (addEventListener, removeEventListener)

---

## 🔵 Simple Definition (English)
`addEventListener(type, listener, options)` attaches a function to run whenever an event of that type happens on a node. `removeEventListener` detaches it, but only if you pass the same function reference and the same capture setting that you used to add it.

## 🔵 सरल परिभाषा (Hindi)
`addEventListener(type, listener, options)` किसी node पर एक function जोड़ता है जो उस type का event होने पर चलता है। `removeEventListener` उसे हटाता है, लेकिन सिर्फ तब जब आप वही function reference और वही capture setting दें जो जोड़ते समय दी थी।

---

## 🔴 Problem it Solves
Earlier you could attach only one handler per event on a node by assigning a property like `onclick`. Libraries and features that needed to listen to the same event would overwrite each other. There was also no clean way to remove a handler later, which caused memory leaks and bugs in single-page apps, where components are created and destroyed many times. `addEventListener` allows many listeners per event, and `removeEventListener` plus the `signal` option allows clean teardown.

## 🔴 यह क्यों बना? (Hindi)
पहले एक node पर एक event के लिए सिर्फ एक handler लग सकता था, `onclick` जैसी property assign करके। अलग-अलग features एक ही event सुनना चाहते तो एक-दूसरे को overwrite कर देते। बाद में handler हटाने का साफ तरीका भी नहीं था, जिससे single-page apps में memory leaks और bugs आते थे, जहाँ components बार-बार बनते और हटते हैं। `addEventListener` एक event के लिए कई listeners देता है, और `removeEventListener` व `signal` option से साफ cleanup होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Call `el.addEventListener("click", handler, options)`. The browser stores the handler with its type and capture flag.
Step 2 → Duplicate check: if the same function, type, and capture flag already exist on that node, the browser ignores the second add.
Step 3 → When the event fires, the browser calls each stored handler in the order they were added (for the same phase).
Step 4 → `once: true` removes the listener automatically after the first call.
Step 5 → `removeEventListener(type, handler, capture)` finds the stored entry by matching type, function identity, and capture flag, then removes it.
Step 6 → `signal` from an `AbortController` removes the listener when `controller.abort()` is called. This is the easiest way to remove many listeners at once.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `el.addEventListener("click", handler, options)` call करें। Browser handler को type और capture flag के साथ store करता है।
Step 2 → Duplicate check: अगर उसी node पर वही function, type और capture flag पहले से है, तो browser दूसरी बार add को ignore करता है।
Step 3 → Event होने पर browser stored handlers को उसी phase में, जोड़े जाने के क्रम में चलाता है।
Step 4 → `once: true` पहली call के बाद listener को अपने-आप हटा देता है।
Step 5 → `removeEventListener(type, handler, capture)` type, function की identity और capture flag मिलाकर entry ढूँढता है और हटाता है।
Step 6 → `AbortController` का `signal` देने पर `controller.abort()` से listener हट जाता है। एक साथ कई listeners हटाने का यह सबसे आसान तरीका है।

---

## 🟡 Real World Example
On Swiggy's live order tracking screen, the app attaches a `resize` and a `visibilitychange` listener when the screen opens. When the user leaves the screen, the app aborts one `AbortController` so all of these listeners disappear together. Without that cleanup, every visit would add another listener and the page would slow down. Razorpay's checkout modal adds a `keydown` listener for the Escape key and removes it when the modal closes.

## 🟡 Real Example Hindi mein
Swiggy के live order tracking screen पर, screen खुलते ही app `resize` और `visibilitychange` listeners लगाता है। User screen से जाता है तो app एक `AbortController` को abort करता है, जिससे ये सारे listeners एक साथ हट जाते हैं। ऐसी cleanup न होने पर हर visit पर एक और listener जुड़ता और page धीमा हो जाता। Razorpay के checkout modal में Escape key के लिए `keydown` listener लगता है और modal बंद होने पर हटा दिया जाता है।

---

## 💻 Code Example — Basic
Save as `listeners-basic.html` and open it in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Event Listeners Basic</title>
</head>
<body>
  <button id="btn">Click me</button>            <!-- button we will attach listeners to -->
  <button id="off">Remove listener</button>     <!-- button that removes the listener -->

  <script>
    const btn = document.getElementById("btn");  // the target button
    const off = document.getElementById("off");  // the remove button

    // A NAMED function: we keep a reference so we can remove it later
    function sayHello() {                        // named handler
      console.log("Hello from sayHello");        // prints on each click
    }

    btn.addEventListener("click", sayHello);     // attach the named function
    btn.addEventListener("click", sayHello);     // same function again: ignored (duplicate)

    btn.addEventListener("click", () => {        // anonymous arrow function
      console.log("Anonymous listener");         // prints on each click
    });

    // Remove the named listener when the second button is clicked
    off.addEventListener("click", () => {        // handler for the remove button
      btn.removeEventListener("click", sayHello);// same reference, so it works
      console.log("sayHello removed");           // confirm in console
    });

    // once: the listener runs one time only, then removes itself
    btn.addEventListener("click", () => {        // one-time handler
      console.log("This prints only once");      // runs only on the first click
    }, { once: true });                           // options object: once = true

    // Capture option: true runs this listener during the capture phase
    document.addEventListener("click", () => {   // listener on document
      console.log("document capture");           // runs first on any click
    }, true);                                    // third argument true = capture
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `listeners-advanced.html`. It builds a small widget that adds and cleans up several listeners with one `AbortController`, and shows a reusable `on()` helper that returns an unsubscribe function.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Listener lifecycle</title>
</head>
<body>
  <div id="modal" hidden>                        <!-- modal hidden by default -->
    <p>Checkout modal. Press Escape to close.</p>
    <button id="close">Close</button>
  </div>
  <button id="open">Open modal</button>

  <script>
    // Reusable helper: attaches a listener and returns a function that removes it
    function on(target, type, handler, options) { // generic subscribe helper
      target.addEventListener(type, handler, options); // attach with the given options
      return () => target.removeEventListener(type, handler, options); // unsubscribe later
    }

    const modal = document.getElementById("modal");     // modal container
    let controller = null;                              // holds the AbortController while open

    function openModal() {                              // called when the modal opens
      if (controller) return;                           // already open: do nothing
      modal.hidden = false;                             // show the modal
      controller = new AbortController();               // one controller for all listeners
      const { signal } = controller;                    // the signal shared by listeners

      // Escape key closes the modal; signal removes this listener on close
      document.addEventListener("keydown", (e) => {     // listen for key presses
        if (e.key === "Escape") closeModal();           // close on Escape
      }, { signal });                                   // automatic removal via signal

      // Clicking the close button also closes it
      document.getElementById("close").addEventListener("click", closeModal, { signal });

      // Using the helper: we keep the unsubscribe function if we want manual control
      const unsubscribeResize = on(window, "resize", () => {
        console.log("Window width:", window.innerWidth); // log size changes
      }, { passive: true });                            // passive: we never call preventDefault
      // Note: this one is NOT tied to the signal, so we call unsubscribeResize() on close
      controller.unsubscribeResize = unsubscribeResize; // store it on the controller object
    }

    function closeModal() {                             // called when the modal closes
      if (!controller) return;                          // nothing to close
      controller.unsubscribeResize();                   // remove the manual listener
      controller.abort();                               // remove every listener with the signal
      controller = null;                                // reset state
      modal.hidden = true;                              // hide the modal
    }

    document.getElementById("open").addEventListener("click", openModal);

    // Check: after closing, the Escape key should do nothing
    console.log("Ready. Open the modal, close it, then press Escape to confirm no listeners remain.");
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Listeners are client-side code, but the server supports them by providing the resources they call. Express can serve a page that loads a listener script, and it can provide an endpoint that the listener calls when an event happens, such as a "notify me when restaurant opens" request.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");               // web framework
const path = require("path");                     // path helper
const app = express();                            // create app
app.use(express.json());                          // parse JSON request bodies

// Serve the page that contains the listener script (public/index.html + public/app.js)
app.use(express.static(path.join(__dirname, "public")));

// Endpoint the listener calls when the user clicks "Notify me" (a click event handler)
app.post("/api/notify", (req, res) => {           // handle POST /api/notify
  const { restaurantId, email } = req.body || {}; // read the fields from the request
  if (!restaurantId || !email) {                  // validate required fields
    return res.status(400).json({ error: "restaurantId and email are required" });
  }
  // Save the subscription in a real database here
  console.log(`Subscribed ${email} to restaurant ${restaurantId}`); // log for demo
  res.status(201).json({ ok: true });             // 201 Created: subscription stored
});

app.listen(3000, () => console.log("http://localhost:3000"));

// public/app.js (browser side):
// document.getElementById("notify").addEventListener("click", async () => {
//   const res = await fetch("/api/notify", { method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ restaurantId: 7, email: "a@b.com" }) });
//   console.log(res.status);                     // 201 on success
// });
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Removing a listener with a new anonymous function
✅ Correct: `removeEventListener` needs the exact same function reference. A new arrow function is a different object, so nothing is removed.

```javascript
// Wrong — the arrow function passed to remove is NEW, so the listener stays
btn.addEventListener("click", () => console.log("hi"));
btn.removeEventListener("click", () => console.log("hi")); // does nothing

// Right — keep a reference
const hi = () => console.log("hi");
btn.addEventListener("click", hi);
btn.removeEventListener("click", hi); // removed
```

❌ **Mistake 2:** Forgetting that the capture flag must match when removing
✅ Correct: If you added with `capture: true`, you must remove with the same `true`.

```javascript
// Wrong — added in the capture phase, but removal says bubble (default false)
document.addEventListener("click", handler, true);
document.removeEventListener("click", handler);      // does NOT remove it

// Right — same capture value
document.removeEventListener("click", handler, true); // removed
```

❌ **Mistake 3:** Adding listeners every time a component renders without cleaning up
✅ Correct: Store the controller or the unsubscribe function and remove listeners when the component is done.

```javascript
// Wrong — every call adds another resize listener; they pile up
function onOpen() {
  window.addEventListener("resize", update);  // leak: never removed
}

// Right — one controller per open, aborted on close
let ctrl = null;
function onOpen2() {
  ctrl?.abort();                               // remove old listeners first
  ctrl = new AbortController();
  window.addEventListener("resize", update, { signal: ctrl.signal });
}
function onClose2() { ctrl?.abort(); ctrl = null; } // clean up everything at once
function update() {}                              // placeholder handler
```

---

## 🧠 Tricky Interview Question
Run this in the console on a page with `<button id="b">`.

```javascript
const btn = document.getElementById("b");          // the button

btn.addEventListener("click", () => console.log("A")); // anonymous A
btn.removeEventListener("click", () => console.log("A")); // a different function object

const handler = () => console.log("B");            // named handler B
btn.addEventListener("click", handler);            // add B
btn.addEventListener("click", handler);            // add B again

btn.click();                                       // simulate a click
btn.removeEventListener("click", handler);         // remove B once
btn.click();                                       // simulate another click
```

Answer: The output is:
```
A        <- first click: the anonymous listener A
B        <- first click: handler B (added once, not twice)
A        <- second click: A is still attached
```
Explanation: The first `removeEventListener` receives a new arrow function, which is a different object, so no stored entry matches it. The anonymous `A` stays attached and runs on every click. `handler` is added twice, but the browser stores a function only once for the same type and capture flag, so the second `addEventListener` does nothing. There is one stored `B`. The first click runs `A` and then `B`. After `removeEventListener("click", handler)`, `B` is gone, so the second click prints only `A`.

---

## ⚫ Interview Questions + Answers

Q1: What arguments does `addEventListener` take?
A1: `type` (the event name, such as "click"), `listener` (the function), and an optional third argument: either a boolean for `capture` or an options object with `capture`, `once`, `passive`, and `signal`.

Q2: Why does adding the same function twice only register it once?
A2: The browser identifies a listener by type, function reference, and capture flag. If all three match an existing entry, the new add is ignored. This prevents duplicate handlers when code runs more than once.

Q3: How do you remove a listener that was added with an anonymous function?
A3: You cannot, because you have no reference to the original function. Store the function in a variable, or use the `signal` option with an `AbortController`, which removes the listener without needing a reference.

Q4: What does `once: true` do?
A4: It makes the listener run at most once. After it runs, the browser removes it automatically. It is useful for one-time setup, like the first user interaction that starts audio.

Q5: What is the benefit of `AbortController` for listeners?
A5: One `controller.abort()` call removes all listeners that were added with its `signal`. This makes cleanup simple when a component, modal, or page section is destroyed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need several handlers for the same event on the same node
- You need to remove handlers later, such as when a modal or component is closed
- You need options like `passive` for scroll performance or `once` for one-time actions

❌ Avoid when:
- Attaching a listener to every item in a large list; delegate to a parent instead
- Inside a render loop without cleanup, which causes duplicate listeners and memory leaks
- Using inline anonymous functions when you plan to remove them later

---

## 📊 Visual Diagram
```
Node: <button id="btn">

Listener list (type, function, capture) stored by the browser:
┌──────────┬───────────────────┬─────────┐
│ type     │ function          │ capture │
├──────────┼───────────────────┼─────────┤
│ click    │ sayHello          │ false   │  ◄── add: stored
│ click    │ sayHello          │ false   │  ◄── add again: IGNORED (duplicate)
│ click    │ anonymous#1       │ false   │  ◄── stored, cannot be removed by a new arrow
│ click    │ handler           │ false   │
└──────────┴───────────────────┴─────────┘

removeEventListener("click", sayHello, false) ──► matches row 1 ──► removed
removeEventListener("click", () => {}, false)  ──► no match (new object) ──► nothing
controller.abort()  ──► removes every row whose options.signal = controller.signal
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| addEventListener | Attaches a handler to an event | Event पर handler जोड़ना |
| removeEventListener | Detaches the same handler | वही handler हटाना |
| Listener reference | The function object identity used to remove | Function की वह पहचान जिससे हटाते हैं |
| capture | Runs during the capture phase | Capture phase में चलना |
| once | Runs one time, then removes itself | एक बार चलकर अपने-आप हटना |
| signal | Option that links the listener to an AbortController | Listener को AbortController से जोड़ने वाला option |
| AbortController | Object that can abort many listeners at once | एक साथ कई listeners हटाने वाला object |
| Memory leak | Unused listeners kept alive forever | Bekaar listeners जो हमेशा memory में रहते हैं |

---

## ⚡ 3-Line Summary
**English:**
1. `addEventListener` attaches many handlers per event; keep a reference to the function if you need to remove it.
2. `removeEventListener` needs the same function and the same capture flag; anonymous functions cannot be removed.
3. Use `once`, or an `AbortController` signal to remove a whole group of listeners at once and avoid memory leaks.

**Hindi:**
1. `addEventListener` एक event पर कई handlers जोड़ता है; हटाना हो तो function का reference रखें।
2. `removeEventListener` को वही function और वही capture flag चाहिए; anonymous functions हटाए नहीं जा सकते।
3. `once` या `AbortController` का signal इस्तेमाल करें, ताकि listeners का पूरा group एक साथ हटे और memory leak न हो।

---

## ➡️ Next Topic
**143. Event Object (target, currentTarget, type)** — अब सीखेंगे कि handler को मिलने वाले event object में कौन-सी जानकारी होती है।
