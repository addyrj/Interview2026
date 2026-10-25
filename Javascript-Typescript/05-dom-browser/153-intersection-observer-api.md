# 153. Intersection Observer API
# हिंदी में: Intersection Observer API

---

## 🔵 Simple Definition (English)
`IntersectionObserver` tells you when an element enters or leaves the visible area of the screen (or of a scrolling container). You give it a callback, and it runs the callback only when visibility crosses a threshold. It does not need a `scroll` listener.

## 🔵 सरल परिभाषा (Hindi)
`IntersectionObserver` बताता है कि कोई element screen (या किसी scroll होने वाले container) के visible हिस्से में कब आता या निकलता है। आप इसे एक callback देते हैं, और visibility तय threshold पार करने पर ही callback चलता है। इसके लिए `scroll` listener की ज़रूरत नहीं है।

---

## 🔴 Problem it Solves
Before this API, developers checked visibility with a `scroll` listener and `getBoundingClientRect()`. That code ran on every scroll event, forced the browser to calculate layout again and again, and caused stutter on long pages with many items. Lazy-loading images, infinite scroll, and ad viewability tracking all needed this check. `IntersectionObserver` moves the work into the browser, which calculates intersections efficiently and calls your code only when something changes.

## 🔴 यह क्यों बना? (Hindi)
इस API से पहले developers visibility चेक करने के लिए `scroll` listener और `getBoundingClientRect()` इस्तेमाल करते थे। यह code हर scroll event पर चलता था, browser को बार-बार layout दोबारा निकालना पड़ता था, और लंबे pages पर scrolling अटकती थी। Lazy-loading images, infinite scroll और ad viewability tracking को यही check चाहिए था। `IntersectionObserver` यह काम browser को सौंपता है, जो intersections कुशलता से निकालता है और कुछ बदलने पर ही आपका code बुलाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an observer: `new IntersectionObserver(callback, options)`. The options are `root`, `rootMargin`, and `threshold`.
Step 2 → Call `observer.observe(element)` for each element you want to watch.
Step 3 → The browser calculates how much of each element is inside the root (the viewport by default).
Step 4 → When visibility crosses a threshold, the browser queues a callback with an array of entries.
Step 5 → The callback also runs once right after `observe()`, even if the element is not visible, so you always get a first reading.
Step 6 → Call `observer.unobserve(el)` when you no longer need an element, and `observer.disconnect()` to stop everything.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Observer बनाएँ: `new IntersectionObserver(callback, options)`। Options हैं `root`, `rootMargin` और `threshold`।
Step 2 → जिन elements को देखना है, हर एक के लिए `observer.observe(element)` करें।
Step 3 → Browser हर element का कितना हिस्सा root (डिफ़ॉल्ट रूप से viewport) के अंदर है, यह निकालता है।
Step 4 → Visibility threshold पार करने पर browser entries के array के साथ callback queue करता है।
Step 5 → `observe()` के तुरंत बाद callback एक बार चलता है, भले ही element visible न हो, इसलिए पहली reading हमेशा मिलती है।
Step 6 → जब element की ज़रूरत न रहे तो `observer.unobserve(el)` करें, और सब रोकने के लिए `observer.disconnect()`।

---

## 🟡 Real World Example
On Swiggy's restaurant feed, each restaurant image has a placeholder until it enters the screen, and then the real image loads. Flipkart's product grid uses a sentinel element at the bottom; when it becomes visible, the page fetches the next batch. Ad networks use the same API to count an ad as "viewable" only when at least half of it has been on screen for one second. The `threshold: 0.5` option handles the "half visible" check.

## 🟡 Real Example Hindi mein
Swiggy के restaurant feed में हर restaurant image पहले placeholder दिखाती है, और screen पर आने पर असली image लोड होती है। Flipkart के product grid के नीचे एक sentinel element होता है; वह visible होते ही page अगला batch लाता है। Ad networks इसी API से तय करते हैं कि ad तभी "viewable" गिना जाए जब आधा ad एक सेकंड तक screen पर रहा हो। `threshold: 0.5` option यह "आधा visible" वाला check करता है।

---

## 💻 Code Example — Basic
Save as `intersection-basic.html` and open it in a browser. Scroll slowly and watch the Console.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Intersection Observer Basic</title>        <!-- tab title -->
  <style>
    .box { height: 400px; margin: 20px; background: #cde; } /* tall boxes so only some are visible */
  </style>
</head>
<body>
  <div class="box" id="box-1">Box 1</div>           <!-- first box -->
  <div class="box" id="box-2">Box 2</div>           <!-- second box -->
  <div class="box" id="box-3">Box 3</div>           <!-- third box -->

  <script>
    const observer = new IntersectionObserver((entries) => {  // callback gets an array of entries
      entries.forEach((entry) => {                  // check each entry that changed
        const id = entry.target.id;                 // which element changed
        const ratio = entry.intersectionRatio.toFixed(2); // share of the element visible, 0 to 1
        if (entry.isIntersecting) {                 // true when the element is in the root area
          console.log(`${id} entered view, ratio ${ratio}`); // log the entry
        } else {                                    // false when the element left the root area
          console.log(`${id} left view`);           // log the exit
        }
      });
    }, {
      root: null,                                   // null means the browser viewport
      threshold: [0, 0.5, 1],                       // fire when 0%, 50%, and 100% are visible
    });

    document.querySelectorAll(".box").forEach((box) => { // find every box
      observer.observe(box);                        // start watching this box
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `intersection-advanced.html`. It lazy-loads images with a `data-src` attribute, starts loading 200px before an image appears, stops watching each image after it loads, falls back safely when the API is missing, and disconnects on `pagehide`.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Lazy images with IntersectionObserver</title> <!-- tab title -->
  <style>
    img, .slot { display: block; width: 300px; height: 200px; margin: 40px auto; background: #eee; } /* image size */
  </style>
</head>
<body>
  <img class="slot" alt="photo 1" data-src="https://picsum.photos/seed/1/300/200"> <!-- real src is in data-src -->
  <img class="slot" alt="photo 2" data-src="https://picsum.photos/seed/2/300/200"> <!-- lazy image two -->
  <img class="slot" alt="photo 3" data-src="https://picsum.photos/seed/3/300/200"> <!-- lazy image three -->

  <script>
    const images = document.querySelectorAll("img[data-src]"); // every image that needs lazy loading

    function loadImage(img) {                       // swap in the real source
      img.src = img.dataset.src;                    // copy data-src into src so the browser fetches it
      img.removeAttribute("data-src");              // remove the attribute so we do not load it twice
    }

    if (!("IntersectionObserver" in window)) {      // very old browser: no observer API
      images.forEach(loadImage);                    // fallback: load everything immediately
    } else {                                        // modern browser: use the observer
      const io = new IntersectionObserver((entries, observer) => { // callback and the observer itself
        for (const entry of entries) {              // check each changed entry
          if (!entry.isIntersecting) continue;      // skip images that are not on screen
          loadImage(entry.target);                  // load the image that just came into view
          observer.unobserve(entry.target);         // stop watching it: it only needs one load
        }
      }, { rootMargin: "200px 0px" });              // start loading 200 px before the image appears

      images.forEach((img) => io.observe(img));     // watch every lazy image

      window.addEventListener("pagehide", () => {   // page is leaving
        io.disconnect();                            // stop all observation at once
      }, { once: true });                           // run the cleanup only once
    }
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
`IntersectionObserver` runs only in the browser, so Express never sees the observer. The closest real usage is an infinite-scroll feed: the browser watches a sentinel element, and when it appears, it asks the server for the next batch. The server uses cursor-based pagination, which stays stable when new items are added at the top.

```javascript
// server.js — npm install express ; run: node server.js
const express = require("express");               // web framework
const app = express();                            // create the app
app.use(express.static("public"));                // serve public/index.html (with the observer)

// Fake photo data: ids 1 to 120
const PHOTOS = Array.from({ length: 120 }, (_, i) => ({
  id: i + 1,                                      // unique, increasing id, used as the cursor
  url: `https://picsum.photos/seed/${i + 1}/300/200`, // image address
}));

// Called when the sentinel element becomes visible in the browser
app.get("/api/photos", (req, res) => {            // handle GET /api/photos?after=12&limit=12
  const limit = Math.min(50, Math.max(1, parseInt(req.query.limit, 10) || 12)); // clamp 1..50
  const after = parseInt(req.query.after, 10) || 0; // cursor: id of the last photo the browser has
  const items = PHOTOS.filter((p) => p.id > after).slice(0, limit); // next items after the cursor
  const nextCursor = items.length === limit ? items[items.length - 1].id : null; // null = no more
  res.set("Cache-Control", "no-store");           // the feed changes; do not cache it
  res.json({ items, nextCursor });                // send the page and the next cursor
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `scroll` plus `getBoundingClientRect()` to check visibility
✅ Correct: Use `IntersectionObserver`, which runs only when visibility changes and does not force layout on every scroll.

```javascript
// Wrong — runs on every scroll event and forces layout each time
window.addEventListener("scroll", () => {
  const r = card.getBoundingClientRect();        // forces a layout calculation
  if (r.top < window.innerHeight) load(card);    // manual visibility check
});

// Right — the browser tells us when the card enters the viewport
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) load(e.target); // only on change
});
io.observe(card);                                // watch the card once
function load(el) {}                             // placeholder loader
```

❌ **Mistake 2:** Forgetting that the callback runs once on `observe()`, so a hidden element triggers a `false` entry first
✅ Correct: Always check `entry.isIntersecting` inside the callback, and do not assume the first entry means "visible".

```javascript
// Wrong — treats every entry as visible, so hidden elements also load
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => load(e.target));        // runs even for isIntersecting false
});

// Right — check the flag before acting
const io2 = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) load(e.target);        // act only when really visible
  });
});
function load(el) {}                             // placeholder loader
```

❌ **Mistake 3:** Never calling `unobserve` or `disconnect`, so the observer keeps watching elements that are no longer needed
✅ Correct: Unobserve an element after you have done its one-time work, and disconnect the observer when its component goes away.

```javascript
// Wrong — the image is loaded again every time it re-enters the screen
io.observe(img);                                 // observes forever

// Right — stop watching after the one-time load
const io3 = new IntersectionObserver((entries, obs) => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;             // skip hidden ones
    load(e.target);                              // one-time work
    obs.unobserve(e.target);                     // stop watching this element
  }
});
const img = document.createElement("img");       // placeholder element
io3.observe(img);                                // watch it
function load(el) {}                             // placeholder loader
```

---

## 🧠 Tricky Interview Question
What is printed? The element is `display: none`, so it takes no space on the page.

```html
<div id="ghost" style="display: none">Hidden</div> <!-- not rendered at all -->
<script>
  const io = new IntersectionObserver((entries) => {   // the callback
    entries.forEach((e) => {                           // each entry
      console.log(e.target.id, e.isIntersecting);      // print id and flag
    });
  });
  io.observe(document.getElementById("ghost"));        // watch the hidden element
</script>
```

Answer: The output is:
```
ghost false
```
Explanation: The callback runs once right after `observe()`, even though the element is not on screen. Its `isIntersecting` is `false`, so the code prints `ghost false`. Nothing else prints because the element never becomes visible. Many developers expect no callback until something changes, but the first reading is always delivered. This is why you check `isIntersecting` and do not assume that a callback means "visible".

---

## ⚫ Interview Questions + Answers

Q1: What does `threshold` mean?
A1: It is the fraction of the element that must be visible for the callback to fire. `threshold: 0` fires on the first pixel entering, `threshold: 1` fires only when the whole element is visible, and an array like `[0, 0.5, 1]` fires at each step.

Q2: What is `rootMargin` used for?
A2: It grows or shrinks the root box using CSS margin syntax, such as `"200px 0px"`. A positive value makes the element count as visible before it reaches the screen, which is how lazy-loading starts early.

Q3: Why is `IntersectionObserver` better than a `scroll` listener?
A3: The browser calculates intersections in an optimized way and calls your callback only when visibility crosses a threshold. A `scroll` listener runs on every scroll event and often forces layout, which is slower.

Q4: What is the difference between `unobserve` and `disconnect`?
A4: `unobserve(el)` stops watching one element. `disconnect()` stops watching all elements of that observer. Use `disconnect` when the whole component is destroyed.

Q5: What is `entry.intersectionRatio`?
A5: It is a number from 0 to 1 that gives the share of the target that is inside the root. It is useful for ad viewability (for example, at least 0.5 visible for one second).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You lazy-load images or video only when they are about to be seen
- You build infinite scroll with a sentinel element at the bottom of the list
- You track whether an element (such as an ad or a banner) was viewed

❌ Avoid when:
- You need exact pixel positions every frame (for example, a drag animation); use `getBoundingClientRect()` in a `requestAnimationFrame` loop
- A native attribute already does the job, such as `<img loading="lazy">` for simple lazy-loading
- You need the size of an element, not its visibility; use `ResizeObserver` (topic 155)

---

## 📊 Visual Diagram
```
           viewport (root)
  ┌──────────────────────────────┐  <- root edge (rootMargin "200px" extends it)
  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░  │  <- 200px zone: images start loading here
  │ ┌──────────────────────────┐ │
  │ │ Box 1  (ratio 0.30)      │ │  isIntersecting = true, ratio = 0.30
  │ └──────────────────────────┘ │
  │ ┌──────────────────────────┐ │
  │ │ Box 2  (ratio 1.00)      │ │  fully inside: crossed threshold 1
  │ └──────────────────────────┘ │
  └──────────────────────────────┘
           (below the fold)
  ┌──────────────────────────────┐
  │ Box 3  ratio 0               │  isIntersecting = false
  └──────────────────────────────┘
  sentinel ──► when visible: fetch(next page) ──► append items ──► observe new sentinel
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IntersectionObserver | Browser API that reports visibility changes | Visibility बदलने की खबर देने वाला browser API |
| Root | Area used for visibility (default: viewport) | Visibility के लिए इस्तेमाल होने वाला क्षेत्र |
| `rootMargin` | Extra space around the root, in CSS margin form | Root के चारों ओर अतिरिक्त जगह |
| `threshold` | Visible fraction that triggers the callback | Callback चलाने वाला visible हिस्सा |
| `isIntersecting` | True when the element is inside the root | Element root के अंदर है या नहीं |
| `intersectionRatio` | Visible share of the element, 0 to 1 | Element का visible हिस्सा, 0 से 1 |
| Sentinel | Empty element placed at the end of a list | List के अंत में रखा गया खाली element |
| Lazy loading | Loading a resource only when needed | ज़रूरत पड़ने पर ही resource लोड करना |
| `unobserve` | Stop watching one element | एक element को देखना बंद करना |

---

## ⚡ 3-Line Summary
**English:**
1. `IntersectionObserver` reports when an element enters or leaves the visible area, without a `scroll` listener.
2. Use `threshold` for how much must be visible and `rootMargin` to start early, and always check `isIntersecting`.
3. Unobserve after one-time work and disconnect when the component goes away, so nothing keeps running.

**Hindi:**
1. `IntersectionObserver` बताता है कि element visible area में कब आता या निकलता है, बिना `scroll` listener के।
2. कितना हिस्सा visible होना चाहिए यह `threshold` से और जल्दी शुरू करने के लिए `rootMargin` से तय करें, और हमेशा `isIntersecting` देखें।
3. एक बार का काम हो जाने पर unobserve करें और component हटने पर disconnect करें, ताकि कुछ भी बेवजह न चले।

---

## ➡️ Next Topic
**154. Mutation Observer API** — अगला topic बताता है कि DOM में बदलाव (elements जुड़ना, हटना या attributes बदलना) कैसे देखें, जो third-party widgets और dynamic pages के लिए बहुत उपयोगी है।
