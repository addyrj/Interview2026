# 145. Event Capturing
# हिंदी में: Event Capturing

---

## 🔵 Simple Definition (English)
Event capturing is the first phase of event dispatch. The event travels down from `window` and `document` through each ancestor until it reaches the target. Listeners registered with `capture: true` run during this phase, before the target's own listeners.

## 🔵 सरल परिभाषा (Hindi)
Event capturing event dispatch का पहला चरण है। Event `window` और `document` से शुरू होकर हर ancestor से होता हुआ नीचे target तक जाता है। `capture: true` के साथ लगाए गए listeners इसी चरण में चलते हैं, target के अपने listeners से पहले।

---

## 🔴 Problem it Solves
Sometimes a parent must see an event before the child does. For example, a payment page may need to block clicks on "Cancel" while a payment is running, and an analytics script may need to record every click before any handler changes the page. Bubbling runs too late for this, because children have already handled the event. Capturing gives the parent the first look.

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी parent को child से पहले event देखना पड़ता है। जैसे payment चलते समय payment page पर "Cancel" click रोकना, या analytics को हर click किसी handler के page बदलने से पहले record करना। Bubbling इसके लिए देर से चलता है, क्योंकि children event संभाल चुके होते हैं। Capturing parent को पहली नज़र देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → User clicks the inner `<button>`. The browser builds the event path from `window` down to the target.
Step 2 → Capture phase: the event goes down from `window`, then `document`, then each ancestor. Listeners added with `capture: true` run here.
Step 3 → Target phase: the event reaches the `<button>`. Both capture and normal listeners on the button run. Modern browsers run capture listeners first here.
Step 4 → Bubble phase: the event goes back up from the button to `document` and `window`. Normal (non-capture) listeners run here.
Step 5 → `event.eventPhase` shows the phase: 1 for capturing, 2 for at-target, 3 for bubbling.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User अंदर के `<button>` पर click करता है। Browser `window` से target तक का event path बनाता है।
Step 2 → Capture phase: event `window` से `document` और फिर हर ancestor से नीचे जाता है। `capture: true` वाले listeners यहाँ चलते हैं।
Step 3 → Target phase: event `<button>` तक पहुँचता है। Button के capture और normal, दोनों listeners चलते हैं। आधुनिक browsers यहाँ पहले capture listeners चलाते हैं।
Step 4 → Bubble phase: event button से ऊपर `document` और `window` की तरफ लौटता है। Normal (non-capture) listeners यहाँ चलते हैं।
Step 5 → `event.eventPhase` बताता है कि कौन-सा चरण चल रहा है: capturing के लिए 1, at-target के लिए 2, bubbling के लिए 3।

---

## 🟡 Real World Example
On Paytm's payment screen, the app adds a capture-phase listener on `document` while a UPI payment is pending. Any click on "Cancel order" is stopped at the top, before the cancel button's own handler runs, so the order cannot be cancelled mid-payment. The same app also uses a capture listener on `window` to log every click for analytics, because that log must include clicks that other handlers later block. When the payment finishes, the app removes the guard with an `AbortController`.

## 🟡 Real Example Hindi mein
Paytm की payment screen पर UPI payment चलते समय app `document` पर एक capture-phase listener लगाता है। "Cancel order" पर होने वाला हर click सबसे ऊपर ही रोक दिया जाता है, cancel button के अपने handler से पहले, इसलिए payment के बीच order cancel नहीं हो सकता। उसी app में `window` पर एक capture listener हर click को analytics के लिए log करता है, क्योंकि यह log उन clicks को भी रखना चाहिए जिन्हें बाद में कोई handler रोक दे। Payment खत्म होने पर app `AbortController` से guard हटा देता है।

---

## 💻 Code Example — Basic
Save as `event-capturing-basic.html` and open it in a browser. It records the order of the three phases.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                  <!-- UTF-8 encoding -->
  <title>Event Capturing Basic</title>                    <!-- tab title -->
</head>
<body>
  <div id="grandparent">                                  <!-- outer box -->
    <div id="parent">                                     <!-- middle box -->
      <button id="child">Click me</button>                <!-- the target -->
    </div>
  </div>
  <pre id="log"></pre>                                    <!-- output area -->

  <script>
    const log = document.getElementById("log");           // output element
    const order = [];                                     // records each step in the order it runs

    // Capture listeners: the third argument true means "run in the capture phase"
    document.addEventListener("click", () => order.push("document capture"), true);      // runs first
    document.getElementById("grandparent").addEventListener("click", () => order.push("grandparent capture"), true); // second
    document.getElementById("parent").addEventListener("click", () => order.push("parent capture"), true);           // third

    // Bubble listeners: no third argument (false by default), they run on the way back up
    document.getElementById("child").addEventListener("click", () => order.push("child bubble"));       // at target
    document.getElementById("parent").addEventListener("click", () => order.push("parent bubble"));     // on the way up
    document.addEventListener("click", (e) => {          // document bubble listener: last step
      order.push("document bubble");                      // record it
      log.textContent = order.join("\n") + "\neventPhase at end = " + e.eventPhase; // show the full order
    });

    document.getElementById("child").click();             // simulate a click on the target
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `event-capturing-advanced.html`. A capture-phase guard blocks the "Cancel" button while a payment runs. Capture-phase analytics records every click. The guard is removed with an `AbortController` when the payment ends, and errors are handled in `try` and `finally`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                  <!-- UTF-8 for ₹ and Hindi -->
  <title>Event Capturing Advanced</title>
</head>
<body>
  <button id="pay">Pay ₹499</button>                      <!-- starts the payment -->
  <button id="cancel">Cancel order</button>               <!-- must be blocked while paying -->
  <p id="status">Idle</p>                                 <!-- shows the current state -->
  <pre id="log"></pre>                                    <!-- output area -->

  <script>
    const payBtn = document.getElementById("pay");        // pay button
    const cancelBtn = document.getElementById("cancel");  // cancel button
    const statusEl = document.getElementById("status");   // status text
    const logEl = document.getElementById("log");         // log output
    let guard = null;                                     // AbortController for the active guard

    function logLine(t) { logEl.textContent += t + "\n"; } // helper: append one line

    // Analytics: window capture listener sees EVERY click first, even ones that get stopped later
    window.addEventListener("click", (e) => {             // runs in the capture phase on window
      logLine("analytics: " + (e.target.id || e.target.tagName)); // record the target
    }, true);                                             // capture = true

    function startPaying() {                              // turn the guard on
      guard = new AbortController();                      // one controller to remove the guard later
      // Capture listener on document: runs before the cancel button's own handlers
      document.addEventListener("click", (e) => {        // guard for all clicks
        if (e.target.closest("#cancel")) {                // the click is on cancel or inside it
          e.stopPropagation();                            // stop the event before it reaches cancel
          e.preventDefault();                             // no default action for the button
          logLine("Blocked: cancel during payment");      // explain in the log
        }
      }, { capture: true, signal: guard.signal });        // capture, removed when guard.abort() runs
      statusEl.textContent = "Paying...";                 // update the UI
    }

    function stopPaying() {                               // remove the guard
      if (!guard) return;                                 // nothing to remove
      guard.abort();                                      // removes the capture listener
      guard = null;                                       // reset the state
      statusEl.textContent = "Idle";                      // update the UI
    }

    payBtn.addEventListener("click", async () => {        // pay handler (target phase on payBtn)
      try {
        startPaying();                                    // guard is on
        logLine("Payment request sent");                  // log the step
        await new Promise((resolve) => setTimeout(resolve, 1000)); // simulate the gateway call
        logLine("Payment done");                          // success message
      } catch (err) {                                     // any error from the flow
        logLine("Payment failed: " + err.message);        // report it
      } finally {
        stopPaying();                                     // always remove the guard
      }
    });

    cancelBtn.addEventListener("click", () => {           // cancel handler (runs only if not blocked)
      logLine("Order cancelled");                         // prints only when the guard is off
    });
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Capturing is a browser feature, so Express does not have it. The closest server-side idea is middleware that runs before the route handler. It sees each request first, can block it, and then calls `next()` to let it reach the real handler. This is the same pattern as the payment guard above: the outer layer checks first, the inner layer does the work.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");                       // web framework
const app = express();                                    // create the app
app.use(express.json());                                  // parse JSON bodies

const paymentsInProgress = new Set();                     // user ids who have a payment running

// Outer guard: runs BEFORE the order routes, like a capture listener runs before the target
app.use("/api/orders", (req, res, next) => {              // applies to every /api/orders request
  const userId = req.get("x-user-id");                    // user id sent by the client
  if (req.method === "DELETE" && paymentsInProgress.has(userId)) { // cancel during payment
    return res.status(409).json({ error: "payment in progress" }); // 409 Conflict: stop here
  }
  next();                                                 // allowed: continue to the route
});

// Target handler: does the real work
app.post("/api/orders/pay", async (req, res, next) => {   // POST /api/orders/pay
  const userId = req.get("x-user-id");                    // who is paying
  if (!userId) return next(Object.assign(new Error("missing x-user-id"), { status: 400 })); // validate
  paymentsInProgress.add(userId);                         // lock: guard is now active
  try {
    await new Promise((resolve) => setTimeout(resolve, 1000)); // simulate the payment gateway call
    res.json({ ok: true });                               // payment success
  } finally {
    paymentsInProgress.delete(userId);                    // always unlock, even on error
  }
});

app.delete("/api/orders/:id", (req, res) => {             // cancel an order
  res.json({ cancelled: req.params.id });                 // reached only when no payment is running
});

app.use((err, req, res, next) => {                        // error layer: 4 arguments
  res.status(err.status || 500).json({ error: err.message }); // send the error as JSON
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting the `true` flag and expecting capture
✅ Correct: Without `true` (or `{ capture: true }`), the listener runs in the bubble phase, so it runs after the children.

```html
<!-- Wrong: this runs in the bubble phase, after the button's handler -->
<script>
  parent.addEventListener("click", () => console.log("parent"));  // bubble by default
  child.addEventListener("click", () => console.log("child"));    // prints child, then parent
</script>

<!-- Right: the third argument true makes the parent run first -->
<script>
  parent.addEventListener("click", () => console.log("parent"), true); // capture
  child.addEventListener("click", () => console.log("child"));         // prints parent, then child
</script>
```

❌ **Mistake 2:** Calling `stopPropagation()` in a capture listener on `window` and blocking the whole app
✅ Correct: A capture listener on `window` runs before everything else. If it calls `stopPropagation()` for all clicks, no element gets the click. Limit the check to the elements you mean to block.

```html
<!-- Wrong: every click on the page stops here, including the buttons the user needs -->
<script>
  window.addEventListener("click", (e) => {
    e.stopPropagation();                                  // blocks all clicks, even valid ones
  }, true);
</script>

<!-- Right: block only the element that must be guarded -->
<script>
  window.addEventListener("click", (e) => {
    if (e.target.closest("#cancel")) e.stopPropagation(); // only the cancel button is blocked
  }, true);
</script>
```

❌ **Mistake 3:** Trying to listen for `focus` on a parent without capture
✅ Correct: `focus` does not bubble, so a normal listener on a parent never sees it. Capture still sees `focus` as it travels down, so add `true`. (`focusin` is another option.)

```html
<!-- Wrong: never fires for inputs inside the form -->
<script>
  form.addEventListener("focus", () => console.log("focus")); // focus does not bubble
</script>

<!-- Right: the capture phase sees focus on every input inside the form -->
<script>
  form.addEventListener("focus", (e) => console.log("focused", e.target.name), true); // works
</script>
```

---

## 🧠 Tricky Interview Question
What is printed when the button is clicked? Paste the script into a page with these elements.

```html
<div id="box">                                            <!-- outer box -->
  <button id="btn">Go</button>                            <!-- target button -->
</div>

<script>
  const box = document.getElementById("box");             // the outer element
  const btn = document.getElementById("btn");             // the target
  box.addEventListener("click", () => console.log("box capture"), true);  // capture on box
  btn.addEventListener("click", () => console.log("btn bubble"));         // bubble on btn (added first)
  btn.addEventListener("click", () => console.log("btn capture"), true);  // capture on btn (added second)
  box.addEventListener("click", () => console.log("box bubble"));         // bubble on box
  btn.click();                                            // simulate the click
</script>
```

Answer: The output is:
```
box capture
btn capture
btn bubble
box bubble
```
Explanation: The capture phase runs first and goes from the outer element to the target, so `box capture` prints before anything on the button. At the target, the button has one capture listener and one normal listener. In the current DOM specification and modern browsers, the capture listener on the target runs before the normal one, even though the normal listener was added first. Older browsers ran target listeners in registration order, so the order can differ on very old engines. After the target, the bubble phase goes up, so `box bubble` runs last.

---

## ⚫ Interview Questions + Answers

Q1: What are the three phases of event dispatch, in order?
A1: Capturing (from `window` down to the target), target (the element itself), and bubbling (from the target back up to `window`).

Q2: How do you register a capture listener?
A2: Pass `true` as the third argument, or pass `{ capture: true }` in the options object. Remove it with `removeEventListener` using the same capture value, or use an `AbortController` signal.

Q3: What do the numbers in `event.eventPhase` mean?
A3: `1` is CAPTURING_PHASE, `2` is AT_TARGET, and `3` is BUBBLING_PHASE. `0` means NONE, which is the value before dispatch starts or after it finishes.

Q4: Why would you use capture instead of bubble?
A4: Capture lets an ancestor see or block an event before the target handles it. It is also the only way to see non-bubbling events like `focus` on children from a parent.

Q5: What happens if a capture listener on `document` calls `stopPropagation()`?
A5: The event stops moving down the path, so the target and everything below it never receive the event. Bubble listeners on the target and above also do not run. Use this only when blocking is the intent.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A parent must check or block an event before a child handles it, such as a payment guard
- You need to see non-bubbling events, such as `focus` or `blur`, on many children at once
- You want analytics or logging that runs for every click, even when other handlers stop the event later

❌ Avoid when:
- A simple bubble listener on the parent is enough (most delegation uses bubbling)
- You would call `stopPropagation()` on every event, which hides events from the rest of the app
- You do not need the extra order control, since capture adds mental overhead for other developers

---

## 📊 Visual Diagram
```
Click on <button id="btn">

  window         ---- capture ---->   (1) window capture     <- runs first
  document       ---- capture ---->   (2) document capture
  <div id="box"> ---- capture ---->   (3) box capture
  <button>       ---- TARGET  ---->   (4) btn capture, then btn bubble
  <div id="box"> <--- bubble  ----    (5) box bubble
  document       <--- bubble  ----    (6) document bubble
  window         <--- bubble  ----    (7) window bubble      <- runs last

  Phase values:  1 = CAPTURING   2 = AT_TARGET   3 = BUBBLING
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Capturing | Event goes down from window to the target | Event का window से target तक नीचे जाना |
| Capture listener | Listener registered with `capture: true` | `capture: true` वाला listener |
| Target phase | The moment the event reaches its target | Event का target तक पहुँचने का चरण |
| `eventPhase` | Number that shows the current phase | वर्तमान चरण बताने वाली संख्या |
| Event path | Ordered list of elements the event passes | Elements की वह सूची जिनसे event गुज़रता है |
| Guard | A listener that blocks some events early | कुछ events को पहले ही रोकने वाला listener |
| `signal` | Option that removes a listener through an AbortController | AbortController से listener हटाने का option |
| `focus` capture | Capture still sees non-bubbling focus events | Non-bubbling focus को capture देख सकता है |

---

## ⚡ 3-Line Summary
**English:**
1. Capturing runs first, from `window` down to the target, when the listener is registered with `capture: true`.
2. Use capture to let a parent check or block an event before the child, or to see `focus` on many children.
3. Keep `stopPropagation()` in capture listeners narrow, because it can hide the event from the target and the whole app.

**Hindi:**
1. Capturing सबसे पहले चलता है, `window` से target तक नीचे की तरफ, जब listener `capture: true` के साथ लगाया गया हो।
2. Capture का इस्तेमाल तब करें जब parent को child से पहले event जाँचना या रोकना हो, या बहुत सारे children पर `focus` देखना हो।
3. Capture listeners में `stopPropagation()` को सीमित रखें, क्योंकि यह event को target और पूरे app से छिपा सकता है।

---

## ➡️ Next Topic
**146. Event Delegation** — अब सीखेंगे कि एक parent listener से हज़ारों children को कैसे संभालें, और bubbling व capturing को मिलाकर यह pattern कैसे बनता है।
