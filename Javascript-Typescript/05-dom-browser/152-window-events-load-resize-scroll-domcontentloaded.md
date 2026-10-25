# 152. Window Events (load, resize, scroll, DOMContentLoaded)
# हिंदी में: Window Events (load, resize, scroll, DOMContentLoaded)

---

## 🔵 Simple Definition (English)
Window events tell you about the whole page. `DOMContentLoaded` fires when the HTML is parsed, `load` fires when images and other resources are also ready, `resize` fires when the viewport changes size, and `scroll` fires when the page moves. Listen to them on `window` or `document`.

## 🔵 सरल परिभाषा (Hindi)
Window events पूरे page के बारे में बताते हैं। `DOMContentLoaded` तब चलता है जब HTML parse हो जाता है, `load` तब चलता है जब images और दूसरे resources भी तैयार हो जाते हैं, `resize` तब चलता है जब viewport का size बदलता है, और `scroll` तब चलता है जब page खिसकता है। इन्हें `window` या `document` पर सुनते हैं।

---

## 🔴 Problem it Solves
Code that touches DOM elements can run before they exist, which causes `null` errors. Code that measures images can run before images have a size, which gives wrong numbers. Code that reacts to layout changes needs to know when the viewport changes. Before these events were standard, developers used `window.onload` and polling loops. `DOMContentLoaded` gives a fast, reliable point to start, and `resize` and `scroll` let layouts and lazy-loading react as the page changes.

## 🔴 यह क्यों बना? (Hindi)
जो code DOM elements छूता है, वह उनके बनने से पहले चल सकता है, जिससे `null` errors आते हैं। जो code images को नापता है, वह images का size आने से पहले चल सकता है, जिससे गलत numbers मिलते हैं। Layout बदलने पर react करने के लिए viewport बदलने की खबर चाहिए। Standard events से पहले developers `window.onload` और polling loops इस्तेमाल करते थे। `DOMContentLoaded` शुरू करने का तेज़ और भरोसेमंद बिंदु देता है, और `resize` व `scroll` layout और lazy-loading को page के बदलने पर react करने देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → The browser downloads and parses the HTML. Scripts without `defer` or `async` block parsing while they run.
Step 2 → When the HTML is fully parsed, the browser fires `DOMContentLoaded` on `document`. It does not wait for images.
Step 3 → When all images, iframes, and stylesheets are loaded, the browser fires `load` on `window`.
Step 4 → After that, `resize` fires on `window` whenever the viewport changes, and `scroll` fires whenever the scroll position changes.
Step 5 → `scroll` and `resize` can fire many times per second, so throttle them with `requestAnimationFrame` or a debounce.
Step 6 → Listeners added after an event has already fired do not run again for that event. Check `document.readyState` first.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Browser HTML download और parse करता है। `defer` या `async` के बिना scripts चलते समय parsing रोक देते हैं।
Step 2 → HTML पूरा parse होने पर browser `document` पर `DOMContentLoaded` चलाता है। यह images का इंतज़ार नहीं करता।
Step 3 → सारी images, iframes और stylesheets लोड होने पर browser `window` पर `load` चलाता है।
Step 4 → इसके बाद viewport बदलने पर `resize` और scroll position बदलने पर `scroll` चलता है।
Step 5 → `scroll` और `resize` एक सेकंड में कई बार चल सकते हैं, इसलिए `requestAnimationFrame` या debounce से throttle करें।
Step 6 → जो listener event चल चुकने के बाद जोड़ा जाए, वह उसी event के लिए दोबारा नहीं चलता। पहले `document.readyState` देखें।

---

## 🟡 Real World Example
When you open Swiggy's restaurant list, the page shows the header and menu skeleton on `DOMContentLoaded`, so the user sees something quickly. Product images on Flipkart are measured after `load`, so the layout is correct. While you scroll the Amazon search results, a `scroll` listener checks if you are near the bottom and loads the next page. When you rotate a phone, the layout adjusts on `resize`. When you switch to another tab, `visibilitychange` pauses video.

## 🟡 Real Example Hindi mein
जब आप Swiggy का restaurant list खोलते हैं, तो `DOMContentLoaded` पर page का header और menu skeleton दिख जाता है, इसलिए user को जल्दी कुछ दिखता है। Flipkart की product images `load` के बाद नापी जाती हैं, इसलिए layout सही रहता है। Amazon के search results scroll करते समय `scroll` listener देखता है कि आप नीचे के पास हैं या नहीं और अगला page लोड करता है। फ़ोन घुमाने पर `resize` से layout बदलता है। दूसरा tab खोलने पर `visibilitychange` से video रुक जाता है।

---

## 💻 Code Example — Basic
Save as `window-events-basic.html` and open it in a browser. Resize the window, scroll, and switch tabs. Watch the Console.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Window Events Basic</title>                <!-- tab title -->
  <style>
    body { height: 3000px; }                        /* tall page so we can scroll */
  </style>
</head>
<body>
  <img src="https://picsum.photos/seed/a/600/300" alt="sample">  <!-- an image: load waits for it -->

  <script>
    document.addEventListener("DOMContentLoaded", () => {  // HTML parsed; images may still load
      console.log("DOMContentLoaded: DOM is ready");       // safe to use getElementById now
    });

    window.addEventListener("load", () => {        // everything, including the image, has loaded
      console.log("load: images and resources ready");     // measure images here if you need sizes
    });

    window.addEventListener("resize", () => {      // fires when the window size changes
      console.log("resize: width", window.innerWidth);     // current viewport width in pixels
    });

    window.addEventListener("scroll", () => {      // fires when the page scrolls
      console.log("scroll: y", window.scrollY);            // how far the page is scrolled from top
    }, { passive: true });                         // passive: true tells the browser we will not cancel scrolling

    document.addEventListener("visibilitychange", () => { // fires when the tab is hidden or shown
      console.log("visibility:", document.visibilityState); // "visible" or "hidden"
    });

    window.addEventListener("pagehide", () => {    // fires when the page is leaving (navigate, close)
      console.log("pagehide: saving state");       // a good place to send final analytics
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `window-events-advanced.html`. It starts safely whether or not the DOM is ready, throttles `scroll` with `requestAnimationFrame`, debounces `resize`, detects when the user nears the bottom, and removes every window listener on `pagehide` with one `AbortController`.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Window Events Advanced</title>             <!-- tab title -->
  <style>
    body { height: 4000px; font-family: sans-serif; } /* tall page for scrolling */
    #status { position: fixed; top: 0; left: 0; background: #eef; padding: 6px; } /* fixed info bar */
  </style>
</head>
<body>
  <div id="status">starting...</div>                <!-- shows the current state -->

  <script>
    const statusEl = document.getElementById("status"); // the info bar element
    const controller = new AbortController();         // one controller to remove all listeners later
    const { signal } = controller;                    // the signal shared by every listener
    let frameRequested = false;                       // true while a rAF update is queued
    let resizeTimer = null;                           // holds the debounce timeout id

    function start() {                                // runs once the DOM is ready
      statusEl.textContent = "ready";                   // update the info bar
      render();                                       // draw the first state right away
    }

    // If the script runs after DOMContentLoaded (e.g. async), the event is already gone
    if (document.readyState === "loading") {          // still parsing: wait for the event
      document.addEventListener("DOMContentLoaded", start, { once: true }); // run start once
    } else {                                          // already interactive or complete
      start();                                        // call start directly, do not wait
    }

    function render() {                               // draws the current scroll state
      frameRequested = false;                         // the queued frame has now run
      const max = document.documentElement.scrollHeight - window.innerHeight; // max scroll distance
      const percent = max > 0 ? Math.round((window.scrollY / max) * 100) : 0; // progress as percent
      statusEl.textContent = `scrolled ${percent}%`;    // show progress in the info bar
      if (percent >= 90) {                            // user is near the bottom
        console.log("near bottom: load the next page here"); // a real app fetches more items
      }
    }

    window.addEventListener("scroll", () => {         // runs on each scroll event (can be very frequent)
      if (frameRequested) return;                     // already queued: skip extra work
      frameRequested = true;                          // mark that a frame is queued
      requestAnimationFrame(render);                  // run render once per screen refresh
    }, { passive: true, signal });                    // passive for smooth scrolling; removed with signal

    window.addEventListener("resize", () => {         // runs on each resize event (many per drag)
      clearTimeout(resizeTimer);                      // cancel the previous timer
      resizeTimer = setTimeout(() => {                // wait until resizing has paused for 150 ms
        console.log("final width:", window.innerWidth); // now do the expensive work once
        render();                                     // recalculate the progress with new size
      }, 150);                                        // debounce delay in milliseconds
    }, { signal });                                   // removed together with the other listeners

    window.addEventListener("pagehide", () => {       // runs when the page is leaving
      controller.abort();                             // remove every listener added with the signal
      clearTimeout(resizeTimer);                      // cancel any pending debounce timer
      console.log("listeners removed");               // confirm the cleanup in the console
    }, { once: true });                               // run this cleanup only once
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Window events run only in the browser, so Express never sees them directly. The closest real usage is serving the page with the listeners, and answering the requests that a `scroll` listener triggers, such as "give me the next page of results." The server does the paging; the browser decides when to ask.

```javascript
// server.js — npm install express ; run: node server.js
const express = require("express");               // web framework
const app = express();                            // create the app
app.use(express.static("public"));                // serve public/index.html (with the scroll listener)

const ITEMS = Array.from({ length: 95 }, (_, i) => ({ id: i + 1, name: `Restaurant ${i + 1}` })); // fake data

// Called by the browser when the user scrolls near the bottom
app.get("/api/restaurants", (req, res) => {       // handle GET /api/restaurants?page=2
  const page = Math.max(1, parseInt(req.query.page, 10) || 1); // default to page 1; never below 1
  const size = 20;                                // items per page
  const start = (page - 1) * size;                // index of the first item on this page
  const items = ITEMS.slice(start, start + size); // slice out just this page
  res.set("Cache-Control", "no-store");           // do not cache the list; it can change
  res.json({                                      // send the page as JSON
    page,                                         // current page number
    items,                                        // the items for this page
    hasMore: start + size < ITEMS.length,         // tells the browser whether to keep scrolling
  });
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Adding a `load` listener after `load` has already fired, so it never runs
✅ Correct: Check `document.readyState` first, or run the code directly if it is already `"complete"`.

```javascript
// Wrong — by the time this line runs, load has already fired; the handler never runs
window.addEventListener("load", () => setupCharts()); // waits for an event that is gone

// Right — run now if the page is already loaded, otherwise wait for load
function whenLoaded(fn) {                         // small helper
  if (document.readyState === "complete") fn();   // already loaded: run now
  else window.addEventListener("load", fn, { once: true }); // not yet: wait for load
}
whenLoaded(setupCharts);                          // safe in every case
function setupCharts() {}                         // placeholder
```

❌ **Mistake 2:** Doing heavy work directly in a `scroll` listener, which makes scrolling janky
✅ Correct: Schedule the work with `requestAnimationFrame` and mark `passive: true` for scroll listeners.

```javascript
// Wrong — expensive DOM reads and writes run on every scroll event (dozens per second)
window.addEventListener("scroll", () => {       // no throttling, no passive flag
  updateHeavyLayout();                          // runs many times per second
});

// Right — run at most once per frame, and tell the browser scrolling is not blocked
let scheduled = false;                          // flag: is a frame already queued?
window.addEventListener("scroll", () => {       // lightweight handler
  if (scheduled) return;                        // skip if a frame is already queued
  scheduled = true;                             // queue one update
  requestAnimationFrame(() => {                 // run before the next paint
    scheduled = false;                          // allow the next queue
    updateHeavyLayout();                        // the expensive work runs once per frame
  });
}, { passive: true });                          // passive: scrolling never waits for us
function updateHeavyLayout() {}                 // placeholder
```

❌ **Mistake 3:** Using `DOMContentLoaded` to measure images, which may not have loaded yet
✅ Correct: Use `load` on `window` when you need image sizes, or wait for each image's own `load` event.

```javascript
// Wrong — images may still be 0 x 0 when DOMContentLoaded fires
document.addEventListener("DOMContentLoaded", () => {
  const h = document.querySelector("img").naturalHeight; // often 0 here
  console.log("image height:", h);                       // wrong number
});

// Right — wait for load, when the image has its real size
window.addEventListener("load", () => {
  const h = document.querySelector("img").naturalHeight; // correct after load
  console.log("image height:", h);                        // right number
});
```

---

## 🧠 Tricky Interview Question
What is printed? The script is at the end of `<body>`, and the page has no slow images.

```html
<script>
  window.addEventListener("load", () => {         // listener 1, added before load fires
    console.log("load handler 1");                // runs once, when load fires
    window.addEventListener("load", () => {       // listener 2, added during load dispatch
      console.log("load handler 2");              // would print if it ever runs
    });
  });
  document.addEventListener("DOMContentLoaded", () => {  // listener 3
    console.log("DOMContentLoaded");              // runs before load
  });
</script>
```

Answer: The output is:
```
DOMContentLoaded
load handler 1
```
Explanation: `DOMContentLoaded` fires first, when the HTML is parsed. `load` fires later, and listener 1 prints. Listener 2 is added while `load` is being dispatched, and `load` never fires again on `window`, so listener 2 never prints. A listener added after an event has finished is never called for that event, even if it is attached on the same target. This is the same reason as Mistake 1, and it is why `document.readyState` checks matter when scripts load late.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `DOMContentLoaded` and `load`?
A1: `DOMContentLoaded` fires when the HTML is parsed and the DOM is ready, without waiting for images or stylesheets. `load` fires after all resources (images, iframes, stylesheets) are loaded.

Q2: Why is `scroll` often used with `passive: true`?
A2: A passive listener promises it will not call `preventDefault()`. The browser can then scroll without waiting for the listener, which keeps scrolling smooth on touch and wheel input.

Q3: How do you avoid running a `resize` handler hundreds of times during a window drag?
A3: Debounce it: clear and reset a `setTimeout` on each event so the work runs only after the resizing pauses. Or throttle it with `requestAnimationFrame` if you need updates while resizing.

Q4: Where should you put `<script>` tags so `DOMContentLoaded` is not needed?
A4: Put scripts at the end of `<body>`, or use `defer`. A `defer` script runs after the HTML is parsed and before `DOMContentLoaded`, in order, so the DOM is ready when it runs.

Q5: How do you detect that the page is being hidden or closed?
A5: Use `document.visibilitychange` to pause work when `visibilityState` becomes `"hidden"`, and `pagehide` for the final cleanup. `beforeunload` exists, but it blocks some browser optimizations, so avoid it unless you must warn the user.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You start page code that needs the DOM ready (`DOMContentLoaded`)
- You need final image sizes or fonts ready (`load`)
- You need to respond to viewport changes, such as responsive charts (`resize`) or infinite scroll (`scroll`)

❌ Avoid when:
- You do heavy work on every `scroll` event without throttling; use `requestAnimationFrame`
- You add `beforeunload` for normal pages; it is annoying and hurts performance
- You use `window.onload = ...` assignments; they overwrite each other, so use `addEventListener`

---

## 📊 Visual Diagram
```
Time ──────────────────────────────────────────────────────────────►

 HTML download & parse     DOMContentLoaded     images/CSS/iframes      load
 ───────────────────────────────►  ●  ─────────────────────────────────►  ●
                                   │                                      │
                                   │  (DOM ready; images may be 0x0)      │  (all resources ready)
                                                                          │
 user drags window edge  ── resize ── resize ── resize ───── (debounced) ──►  one work call
 user scrolls the page   ── scroll ── scroll ── scroll ───► rAF ──► one render per frame

 Listener added AFTER load  ──────────────────────────────────────►  never runs (event is gone)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `DOMContentLoaded` | HTML parsed; DOM ready | HTML parse होने और DOM तैयार होने का event |
| `load` | Page and all resources loaded | Page और सारे resources लोड होने का event |
| `resize` | Viewport size changed | Viewport का size बदलना |
| `scroll` | Page scroll position changed | Page की scroll position बदलना |
| `readyState` | Loading state: loading, interactive, complete | Page की loading स्थिति |
| `passive` | Listener promises not to block scrolling | Listener scroll को नहीं रोकेगा, यह वादा |
| Debounce | Run work only after events stop for a while | Events रुकने के बाद ही काम करना |
| Throttle | Run work at most once per interval or frame | हर interval या frame में अधिकतम एक बार काम |
| `requestAnimationFrame` | Schedules code before the next paint | अगले paint से पहले code चलाना |
| `visibilitychange` | Tab hidden or shown | Tab छिपना या दिखना |

---

## ⚡ 3-Line Summary
**English:**
1. `DOMContentLoaded` means the DOM is ready, and `load` means images and resources are ready too.
2. `resize` and `scroll` fire very often, so throttle them with `requestAnimationFrame` or debounce them with a timer.
3. A listener added after an event has fired never runs, so check `document.readyState` before waiting.

**Hindi:**
1. `DOMContentLoaded` का मतलब है DOM तैयार है, और `load` का मतलब है images और resources भी तैयार हैं।
2. `resize` और `scroll` बहुत बार चलते हैं, इसलिए उन्हें `requestAnimationFrame` से throttle या timer से debounce करें।
3. जो listener event के बाद जोड़ा जाए वह कभी नहीं चलता, इसलिए इंतज़ार करने से पहले `document.readyState` देखें।

---

## ➡️ Next Topic
**153. Intersection Observer API** — अगला topic बताता है कि element viewport में कब दिखता है, बिना `scroll` listener के, जो lazy-loading और infinite scroll का सही तरीका है।
