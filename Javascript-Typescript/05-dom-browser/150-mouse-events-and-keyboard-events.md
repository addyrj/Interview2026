# 150. Mouse Events + Keyboard Events
# हिंदी में: माउस इवेंट्स + कीबोर्ड इवेंट्स (Mouse & Keyboard Events)

---

## 🔵 Simple Definition (English)
Mouse events (`mousedown`, `mouseup`, `click`, `mousemove`) tell you what the pointer did on an element. Keyboard events (`keydown`, `keyup`) tell you which key the user pressed, using `event.key` for the character and `event.code` for the physical key.

## 🔵 सरल परिभाषा (Hindi)
Mouse events (`mousedown`, `mouseup`, `click`, `mousemove`) बताते हैं कि pointer ने किसी element पर क्या किया। Keyboard events (`keydown`, `keyup`) बताते हैं कि user ने कौन-सा key दबाया, जिसमें `event.key` character देता है और `event.code` physical key देता है।

---

## 🔴 Problem it Solves
Before these events were standard, pages could not react to user input in a predictable way. Developers used different browser-specific events, and `keyCode` numbers were hard to read. Without a clear event model, things like drag-and-drop, custom menus, and keyboard shortcuts were fragile. The DOM event model gives one consistent event object for mouse and keyboard, with coordinates, buttons, and modifier keys (Shift, Ctrl, Alt, Meta) already filled in.

## 🔴 यह क्यों बना? (Hindi)
Standard events आने से पहले pages user input पर भरोसेमंद तरीके से react नहीं कर पाते थे। Browsers के अलग-अलग events थे और `keyCode` के numbers समझना मुश्किल था। साफ event model न होने पर drag-and-drop, custom menus और keyboard shortcuts नाज़ुक बन जाते थे। DOM event model mouse और keyboard दोनों के लिए एक ही event object देता है, जिसमें coordinates, buttons और modifier keys (Shift, Ctrl, Alt, Meta) पहले से होते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → The user moves the mouse or presses a key. The OS sends the input to the browser.
Step 2 → Mouse events are sent to the element under the pointer (hit testing). Keyboard events are sent to the focused element, or to `document.body` if nothing is focused.
Step 3 → The event bubbles up the DOM tree, so a listener on a parent can see events from its children.
Step 4 → A mouse click sends events in order: `mousedown` → `mouseup` → `click`.
Step 5 → `event.preventDefault()` cancels the default action, such as following a link or typing a character.
Step 6 → Modifier flags like `ctrlKey`, `shiftKey`, `altKey`, and `metaKey` are true or false on each event.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User mouse हिलाता है या key दबाता है। OS यह input browser को भेजता है।
Step 2 → Mouse events उस element को जाते हैं जो pointer के नीचे है (hit testing)। Keyboard events focused element को जाते हैं, और कुछ focus न हो तो `document.body` को।
Step 3 → Event DOM tree में ऊपर की ओर bubble करता है, इसलिए parent पर लगा listener children के events देख सकता है।
Step 4 → Mouse click में events इस क्रम में आते हैं: `mousedown` → `mouseup` → `click`।
Step 5 → `event.preventDefault()` default action रोकता है, जैसे link पर जाना या character type होना।
Step 6 → हर event पर `ctrlKey`, `shiftKey`, `altKey` और `metaKey` जैसे modifier flags true या false होते हैं।

---

## 🟡 Real World Example
On Zomato's restaurant page, a user can click the veg/non-veg filter with the mouse or press Tab and Enter. The page listens to `click` (which also fires for Enter on a real `<button>`) so both inputs work. On Amazon's product image gallery, hovering shows a zoom using `mousemove`, and the left and right arrow keys change the image through `keydown`. Razorpay's card form uses `keydown` to block non-digit keys in the card number field.

## 🟡 Real Example Hindi mein
Zomato के restaurant page पर user mouse से veg/non-veg filter click कर सकता है या Tab और Enter दबा सकता है। Page `click` सुनता है, जो असली `<button>` पर Enter से भी चलता है, इसलिए दोनों तरह का input चलता है। Amazon की product image gallery में hover करने पर `mousemove` से zoom दिखता है और `keydown` से left-right arrow keys से image बदलती है। Razorpay के card form में `keydown` से card number field में digits के अलावा keys रोकी जाती हैं।

---

## 💻 Code Example — Basic
Save as `mouse-keyboard-basic.html` and open it in a browser. Then open DevTools (Console) and interact with the page.

```html
<!DOCTYPE html>                                      <!-- declares an HTML5 document -->
<html lang="en">                                     <!-- root element, English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 so Hindi text shows correctly -->
  <title>Mouse and Keyboard Basic</title>           <!-- text shown in the browser tab -->
  <style>
    #box { width: 220px; height: 120px; background: #cde; }  /* the box we will interact with */
  </style>
</head>
<body>
  <div id="box">Click or move over me</div>         <!-- target element for mouse events -->
  <input id="typing" placeholder="Type here">       <!-- input that receives key events -->

  <script>
    const box = document.getElementById("box");     // find the box element by its id
    box.addEventListener("mousedown", (e) => {      // runs when any mouse button goes down
      console.log("mousedown button:", e.button);   // 0 = left, 1 = middle, 2 = right
    });
    box.addEventListener("mouseup", () => {         // runs when the button is released
      console.log("mouseup");                       // log the release
    });
    box.addEventListener("click", (e) => {          // runs after mousedown + mouseup on the same element
      console.log("click at", e.clientX, e.clientY);// pointer position relative to the viewport
    });
    box.addEventListener("mousemove", (e) => {      // runs many times while the pointer moves over the box
      console.log("moved horizontally by", e.movementX); // pixels moved since the last event
    });

    document.addEventListener("keydown", (e) => {   // listen on document to catch keys from any element
      console.log("key:", e.key, "code:", e.code);  // key = "a" or "Enter"; code = "KeyA" or "Enter"
    });
    document.addEventListener("keyup", (e) => {     // runs when a key is released
      console.log("released:", e.key);              // log the released key
    });

    document.addEventListener("keydown", (e) => {   // a shortcut listener
      const isCtrlK = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k"; // Ctrl+K or Cmd+K
      if (isCtrlK) {                                // only run when the shortcut is pressed
        e.preventDefault();                         // stop the browser's own action for this key
        console.log("shortcut Ctrl+K or Cmd+K");    // our custom action
      }
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `drag-and-keys-advanced.html`. A card can be dragged with the mouse, moved with arrow keys when focused, and cancelled with Escape. All window-level listeners are removed with one `AbortController` when the drag ends.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Drag with mouse, nudge with keys</title>    <!-- tab title -->
  <style>
    body { margin: 0; height: 100vh; }              /* full-height page so the card has room */
    #card { position: absolute; left: 100px; top: 100px; width: 180px; height: 90px;
            background: #ffd; border: 1px solid #aa0; user-select: none; }  /* draggable card */
  </style>
</head>
<body>
  <div id="card" tabindex="0">Drag me, or focus and use arrow keys</div> <!-- tabindex makes it focusable -->

  <script>
    const card = document.getElementById("card");   // the element we drag
    const STEP = 10;                                // pixels moved by one arrow key press
    let drag = null;                                // drag state; null when not dragging
    let controller = null;                          // AbortController that owns the window listeners

    function onMove(e) {                            // runs on every mouse move while dragging
      if (!drag) return;                            // safety check: ignore if no drag is active
      card.style.left = e.clientX - drag.offsetX + "px"; // place card under the pointer
      card.style.top = e.clientY - drag.offsetY + "px";  // keep the same grab point
    }

    function endDrag(cancel) {                      // finish the drag; cancel = true restores position
      if (!drag) return;                            // nothing to end
      if (cancel) {                                 // Escape was pressed
        card.style.left = drag.startLeft + "px";    // go back to the start x
        card.style.top = drag.startTop + "px";      // go back to the start y
      }
      drag = null;                                  // clear the drag state
      controller.abort();                           // remove every listener added with this signal
      controller = null;                            // reset the controller
    }

    card.addEventListener("mousedown", (e) => {     // start a drag when the mouse goes down on the card
      if (e.button !== 0 || drag) return;           // only the left button, and only if not dragging
      drag = {                                      // save where the drag began
        offsetX: e.clientX - card.offsetLeft,       // gap between pointer and card's left edge
        offsetY: e.clientY - card.offsetTop,        // gap between pointer and card's top edge
        startLeft: card.offsetLeft,                 // original x for Escape to restore
        startTop: card.offsetTop,                   // original y for Escape to restore
      };
      controller = new AbortController();           // one controller for this drag session
      const { signal } = controller;                // share the signal with all listeners below
      window.addEventListener("mousemove", onMove, { signal }); // follow the pointer
      window.addEventListener("mouseup", () => endDrag(false), { signal, once: true }); // drop
      e.preventDefault();                           // stop text selection while dragging
    });

    window.addEventListener("keydown", (e) => {     // Escape can cancel a drag from anywhere
      if (e.key === "Escape") endDrag(true);        // cancel and restore the start position
    });

    const moves = {                                 // map each arrow key to [dx, dy]
      ArrowLeft: [-STEP, 0],                        // move left
      ArrowRight: [STEP, 0],                        // move right
      ArrowUp: [0, -STEP],                          // move up
      ArrowDown: [0, STEP],                         // move down
    };
    card.addEventListener("keydown", (e) => {       // runs only when the card has focus
      const delta = moves[e.key];                   // look up the movement for this key
      if (!delta) return;                           // not an arrow key: do nothing
      e.preventDefault();                           // stop the page from scrolling
      card.style.left = card.offsetLeft + delta[0] + "px"; // move horizontally
      card.style.top = card.offsetTop + delta[1] + "px";   // move vertically
    });
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Mouse and keyboard events run only in the browser, so Express never sees them directly. The closest real usage is to serve the page that has the listeners, and to receive batched UI events (for analytics or heatmaps) from the browser. `navigator.sendBeacon` is used because it sends data reliably even while the page is closing.

```javascript
// server.js — npm install express ; run: node server.js
const express = require("express");               // web framework
const app = express();                            // create the app
app.use(express.json({ limit: "50kb" }));         // parse JSON bodies and cap their size at 50 KB
app.use(express.static("public"));                // serve public/index.html and public/app.js

// Endpoint that receives batched UI events sent by the browser
app.post("/api/ui-events", (req, res) => {        // handle POST /api/ui-events
  const events = req.body && req.body.events;     // expect a body like { events: [...] }
  if (!Array.isArray(events) || events.length === 0) { // validate the input
    return res.status(400).json({ error: "events must be a non-empty array" });
  }
  const safe = events.slice(0, 100).map((ev) => ({ // keep at most 100 events
    type: String(ev.type).slice(0, 20),           // limit the length of the type string
    key: typeof ev.key === "string" ? ev.key : null, // store the key name only if it is a string
    at: Date.now(),                               // server-side timestamp
  }));
  console.log("received", safe.length, "events"); // demo log; a real app writes to a DB or queue
  res.status(204).end();                          // 204 No Content: success, nothing to return
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server

// public/app.js (browser side, not Node):
// const queue = [];                                 // holds events until the page is leaving
// document.addEventListener("keydown", (e) => queue.push({ type: "keydown", key: e.key }));
// window.addEventListener("pagehide", () => {       // page is closing or navigating away
//   const blob = new Blob([JSON.stringify({ events: queue })], { type: "application/json" });
//   navigator.sendBeacon("/api/ui-events", blob);   // send the batch without blocking unload
// });
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `click` on a `<div>` for a button, so keyboard users cannot activate it
✅ Correct: Use a real `<button>`. It gets focus with Tab and fires `click` on Enter and Space. If you must use a `<div>`, add `tabindex="0"` and handle `keydown` for Enter and Space too.

```javascript
// Wrong — a div only responds to the mouse; Tab cannot reach it and Enter does nothing
const fakeBtn = document.createElement("div");   // not focusable, no keyboard support
fakeBtn.addEventListener("click", save);         // only mouse clicks reach this

// Right — a real button gets Tab focus, Enter, and Space for free
const realBtn = document.createElement("button"); // focusable and keyboard-accessible
realBtn.addEventListener("click", save);          // one listener covers mouse and keyboard
function save() {}                                // placeholder handler
```

❌ **Mistake 2:** Using the deprecated `keypress` event or `keyCode` numbers
✅ Correct: Use `keydown` (or `keyup`) and read `e.key`. `keypress` is deprecated and `keyCode` is hard to read.

```javascript
// Wrong — keypress is deprecated and keyCode 13 is hard to understand
input.addEventListener("keypress", (e) => {       // deprecated event name
  if (e.keyCode === 13) submit();                 // magic number for Enter
});

// Right — keydown with e.key is clear and works with modern browsers
input.addEventListener("keydown", (e) => {        // current event for key presses
  if (e.key === "Enter") submit();                // readable key name
});
function submit() {}                              // placeholder handler
```

❌ **Mistake 3:** Calling `preventDefault()` on every `mousedown`, which also stops the input from getting focus
✅ Correct: Call `preventDefault()` only when you really need to stop the default action, such as during a drag (as in the advanced example).

```javascript
// Wrong — every mousedown is cancelled, so the input never gets focus and cannot be typed in
input.addEventListener("mousedown", (e) => e.preventDefault()); // blocks focus

// Right — cancel only during the case you need, here a drag on a non-input handle
handle.addEventListener("mousedown", (e) => {   // only the drag handle
  if (e.button === 0) e.preventDefault();       // left button drag: avoid text selection
});
```

---

## 🧠 Tricky Interview Question
A user focuses a `<button>` with Tab and presses Enter. What is printed?

```html
<button id="save">Save</button>                   <!-- a real button, focusable -->
<script>
  const save = document.getElementById("save");   // the button
  save.addEventListener("keydown", (e) => {       // listener 1: keyboard
    if (e.key === "Enter") {                      // only Enter
      console.log("keydown Enter");               // print first
      e.preventDefault();                         // cancel the browser's default action
    }
  });
  save.addEventListener("click", () => {          // listener 2: click
    console.log("click");                         // print if click fires
  });
  save.focus();                                   // put the button in focus for the demo
</script>
```

Answer: The output is only:
```
keydown Enter
```
Explanation: For a focused `<button>`, pressing Enter makes the browser dispatch a `click` as the default action of the `keydown`. The first listener calls `e.preventDefault()`, which cancels that default action, so the browser never dispatches `click`. The second listener is not run. This is why calling `preventDefault()` on `keydown` can silently break button activation, and it is a common reason for "my button does nothing" bugs.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `event.key` and `event.code`?
A1: `event.key` is the character or name produced by the key, and it depends on the keyboard layout and Shift state (for example "a" or "A"). `event.code` is the physical key position, and it does not change with layout (for example "KeyA"). Use `key` for text and shortcuts, and `code` for game controls.

Q2: What is the order of mouse events for one click?
A2: `mousedown`, then `mouseup`, then `click`. A `dblclick` event follows two clicks in quick succession. `contextmenu` is separate and fires on a right-click.

Q3: Why does `keydown` fire again and again when a key is held?
A3: Holding a key causes the operating system to send repeated key presses. Each repeat fires `keydown` again with `e.repeat === true`. Check `e.repeat` if you want to ignore auto-repeat.

Q4: Why should you prefer `click` over `mousedown` for button actions?
A4: `click` fires only when the press and release both happen on the same element, so a user can cancel by moving away before releasing. `click` also fires for keyboard activation, so the same listener covers both input types.

Q5: How do you read modifier keys on a mouse event?
A5: Use the booleans `e.shiftKey`, `e.ctrlKey`, `e.altKey`, and `e.metaKey` (Cmd on macOS). For example, `e.metaKey || e.ctrlKey` detects a shortcut on both Mac and Windows.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need custom interaction such as drag-and-drop, sliders, or a canvas drawing tool
- You add keyboard shortcuts to a web app (with `preventDefault` only for your own keys)
- You want to track UI usage for analytics or heatmaps

❌ Avoid when:
- A native element (`<button>`, `<input>`, `<a>`) already does the job; use the native behavior
- You listen to `mousemove` on many elements; attach one listener to a parent and check `e.target` instead
- You need touch or pen support only; use Pointer Events (`pointerdown`), which cover mouse, touch, and pen

---

## 📊 Visual Diagram
```
User presses a key / moves the mouse
              │
              ▼
   OS input ──► Browser event system
              │
     ┌────────┴─────────────────────────┐
     │ mouse: hit test the element      │ keyboard: focused element
     │ under the pointer                │ (or document.body)
     └────────┬─────────────────────────┘
              ▼
   Event object created (key, code, clientX, button, ctrlKey …)
              │
              ▼  capture phase (down to target)
   target element  ──► listeners run here
              │
              ▼  bubble phase (up to document)
   parent elements ──► delegated listeners run here
              │
              ▼
   default action (click, typing, scroll) unless preventDefault()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MouseEvent | Event object for mouse actions | माउस action का event object |
| KeyboardEvent | Event object for key presses | Key press का event object |
| `event.key` | Character or name of the key pressed | दबाई गई key का नाम या character |
| `event.code` | Physical key position, layout-independent | Physical key की स्थिति |
| `event.button` | Which mouse button (0 left, 1 middle, 2 right) | कौन-सा mouse button |
| `clientX` / `clientY` | Pointer position relative to the viewport | Viewport के हिसाब से pointer की स्थिति |
| Modifier key | Shift, Ctrl, Alt, Meta (Cmd) | Shift, Ctrl, Alt, Meta (Cmd) जैसी keys |
| `preventDefault()` | Cancels the browser's default action | Browser का default action रोकना |
| Hit testing | Finding which element is under the pointer | Pointer के नीचे का element ढूँढना |

---

## ⚡ 3-Line Summary
**English:**
1. Mouse events describe pointer actions (`mousedown`, `mouseup`, `click`, `mousemove`), and keyboard events describe key presses (`keydown`, `keyup`).
2. Use `e.key` for characters and shortcuts, and use real `<button>` elements so the keyboard and mouse both work.
3. Call `preventDefault()` only when you must stop the default action, and remove window listeners when an interaction ends.

**Hindi:**
1. Mouse events pointer की action बताते हैं (`mousedown`, `mouseup`, `click`, `mousemove`) और keyboard events key press बताते हैं (`keydown`, `keyup`)।
2. Characters और shortcuts के लिए `e.key` इस्तेमाल करें, और mouse व keyboard दोनों चलाने के लिए असली `<button>` रखें।
3. `preventDefault()` तभी लगाएँ जब default action रोकना ज़रूरी हो, और interaction खत्म होने पर window listeners हटाएँ।

---

## ➡️ Next Topic
**151. Form Events (submit, change, input, focus, blur)** — अगला topic form के events बताता है, जहाँ user के input, validation और submit को सही तरीके से handle करना सीखेंगे।
