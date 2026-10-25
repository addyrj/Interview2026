# 154. Mutation Observer API
# हिंदी में: Mutation Observer API

---

## 🔵 Simple Definition (English)
`MutationObserver` watches a DOM node and tells you when its children, attributes, or text change. You give it a callback, and it receives a batch of change records after the current code finishes. It is the tool for reacting to changes that you do not make yourself.

## 🔵 सरल परिभाषा (Hindi)
`MutationObserver` किसी DOM node को देखता है और बताता है कि उसके children, attributes या text कब बदले। इसे एक callback दिया जाता है, और मौजूदा code खत्म होने के बाद उसे बदलावों की एक batch मिलती है। जो बदलाव आप खुद नहीं करते, उन पर react करने का यह सही tool है।

---

## 🔴 Problem it Solves
Sometimes the DOM changes without your code: a third-party widget injects a chat button, a payment iframe is added late, or a framework re-renders part of the page. Old approaches used "mutation events" (`DOMNodeInserted` and similar), which were slow and are removed from modern browsers. Polling with `setInterval` to check the DOM wasted CPU. `MutationObserver` gives a fast, batched, and standard way to know exactly what changed.

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी DOM आपके code के बिना बदलता है: कोई third-party widget chat button डालता है, कोई payment iframe देर से जुड़ता है, या framework page का हिस्सा दोबारा render करता है। पुराने तरीके "mutation events" (`DOMNodeInserted` आदि) थे, जो धीमे थे और आधुनिक browsers से हटा दिए गए हैं। DOM जाँचने के लिए `setInterval` polling CPU बर्बाद करती थी। `MutationObserver` एक तेज़, batched और standard तरीका देता है, जिससे पता चलता है कि ठीक क्या बदला।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an observer: `new MutationObserver(callback)`.
Step 2 → Call `observer.observe(target, options)`. Options include `childList`, `attributes`, `characterData`, and `subtree`. You must choose at least one of the first three.
Step 3 → The browser records each matching change as a mutation record (type, target, added nodes, removed nodes, attribute name).
Step 4 → The callback is queued as a microtask, so it runs after the current script finishes, not in the middle of your code.
Step 5 → All changes made in the same synchronous block arrive together in one `records` array.
Step 6 → Call `observer.disconnect()` to stop watching. Call `observer.takeRecords()` to read pending records right away.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Observer बनाएँ: `new MutationObserver(callback)`।
Step 2 → `observer.observe(target, options)` करें। Options में `childList`, `attributes`, `characterData` और `subtree` हैं। पहले तीन में से कम से कम एक चुनना ज़रूरी है।
Step 3 → Browser हर matching बदलाव को mutation record (type, target, जुड़े nodes, हटे nodes, attribute का नाम) के रूप में रखता है।
Step 4 → Callback एक microtask के रूप में queue होता है, इसलिए वह मौजूदा script खत्म होने के बाद चलता है, बीच में नहीं।
Step 5 → एक ही synchronous block में हुए सारे बदलाव एक `records` array में एक साथ आते हैं।
Step 6 → देखना बंद करने के लिए `observer.disconnect()` करें। तुरंत pending records पढ़ने के लिए `observer.takeRecords()`।

---

## 🟡 Real World Example
Flipkart product pages load a third-party review widget late. A `MutationObserver` on the container notices the new node and starts the widget's setup code. Zomato's restaurant page embeds a chat helper that adds its button after load; the page watches for it and moves it above the sticky footer. In Notion-style editors, a `MutationObserver` on the document saves a change whenever the text block list changes.

## 🟡 Real Example Hindi mein
Flipkart के product pages पर third-party review widget देर से लोड होता है। Container पर लगा `MutationObserver` नए node को पकड़ता है और widget का setup code शुरू करता है। Zomato के restaurant page पर chat helper load के बाद अपना button डालता है; page उसे देखकर sticky footer के ऊपर कर देता है। Notion जैसे editors में document पर लगा `MutationObserver` हर बार text block list बदलने पर बदलाव save करता है।

---

## 💻 Code Example — Basic
Save as `mutation-basic.html` and open it in a browser. Click the buttons and watch the Console.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Mutation Observer Basic</title>            <!-- tab title -->
</head>
<body>
  <ul id="list"><li>Existing item</li></ul>         <!-- the list we will watch -->
  <button id="add">Add item</button>                <!-- adds an item to the list -->
  <button id="rename">Change first item</button>    <!-- changes text of the first item -->

  <script>
    const list = document.getElementById("list");   // the node we watch
    const observer = new MutationObserver((records, obs) => { // callback gets all records in one batch
      console.log("batch of", records.length, "record(s)"); // how many changes arrived together
      for (const r of records) {                    // check each change
        if (r.type === "childList") {               // a child was added or removed
          console.log("added:", r.addedNodes.length, "removed:", r.removedNodes.length); // counts
        }
      }
    });

    observer.observe(list, {                        // start watching the list
      childList: true,                              // watch for added and removed children
      characterData: true,                          // watch for text changes inside children
      subtree: true,                                // also watch all descendants, not just direct children
    });

    document.getElementById("add").addEventListener("click", () => { // when Add is clicked
      const li = document.createElement("li");      // create a new list item
      li.textContent = "New item " + (list.children.length + 1); // give it text
      list.appendChild(li);                         // add it to the list (this is observed)
    });

    document.getElementById("rename").addEventListener("click", () => { // when Rename is clicked
      list.firstElementChild.firstChild.data = "Renamed"; // change text node (characterData)
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `mutation-advanced.html`. It waits for an element that a third-party script will inject later, with a timeout, and removes the observer when the element is found or the wait fails. It works even if the element is already there.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>waitForElement with MutationObserver</title> <!-- tab title -->
</head>
<body>
  <div id="app">Loading widget...</div>             <!-- page content that exists already -->

  <script>
    // Resolves with the element once it appears, or rejects after timeoutMs
    function waitForElement(selector, timeoutMs = 5000) { // selector and max wait in ms
      return new Promise((resolve, reject) => {     // return a Promise
        const existing = document.querySelector(selector); // check if it is already there
        if (existing) return resolve(existing);     // found immediately: no observer needed

        const observer = new MutationObserver(() => { // runs after DOM changes in the page
          const el = document.querySelector(selector); // look again after each batch of changes
          if (el) {                                 // the element has appeared
            cleanup();                              // stop observing and cancel the timer
            resolve(el);                            // deliver the element to the caller
          }
        });

        const timer = setTimeout(() => {            // timeout: element never appeared
          cleanup();                                // stop observing to avoid leaks
          reject(new Error(`Timed out waiting for ${selector}`)); // report the failure
        }, timeoutMs);

        function cleanup() {                        // shared teardown for success and failure
          observer.disconnect();                    // stop the MutationObserver
          clearTimeout(timer);                      // cancel the timeout timer
        }

        observer.observe(document.body, {           // watch the whole body
          childList: true,                          // new or removed elements
          subtree: true,                            // at any depth
        });
      });
    }

    // Simulate a third-party script that injects a widget after 1.5 seconds
    setTimeout(() => {                              // runs once, later
      const widget = document.createElement("div"); // create the widget element
      widget.className = "chat-widget";             // give it a class to find
      widget.textContent = "Chat is ready";         // visible text
      document.body.appendChild(widget);            // inject it into the page
    }, 1500);                                       // 1.5 seconds later

    (async () => {                                  // async IIFE: we can use await at top level here
      try {
        const widget = await waitForElement(".chat-widget", 5000); // wait up to 5 seconds
        console.log("Found:", widget.textContent);  // widget is ready to use
      } catch (err) {                               // timeout or other error
        console.error("Widget error:", err.message); // log the problem; the page keeps working
      }
    })();
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
`MutationObserver` runs only in the browser. The closest real usage is a server that returns an HTML fragment, which the page inserts into the DOM with `fetch`. The `MutationObserver` on the container sees the new node and sets it up (for example, attaching click handlers). This is the pattern behind "hydrate content loaded from the server".

```javascript
// server.js — npm install express ; run: node server.js
const express = require("express");               // web framework
const app = express();                            // create the app
app.use(express.static("public"));                // serve public/index.html (with the observer)

// Returns a small HTML fragment for one restaurant rating
app.get("/fragments/rating/:id", (req, res) => {  // handle GET /fragments/rating/42
  const id = Number(req.params.id);               // convert the URL part to a number
  if (!Number.isInteger(id) || id <= 0) {         // validate: must be a positive integer
    return res.status(400).type("text").send("invalid id"); // reject bad input
  }
  res.type("html").send(                          // send an HTML fragment, not a full page
    `<div class="rating" data-restaurant="${id}">★★★★☆</div>` // safe: id is a verified integer
  );
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server

// public/app.js (browser side, not Node):
// const box = document.getElementById("ratings");          // the container to watch
// const mo = new MutationObserver((records) => {           // runs after each batch of inserts
//   for (const r of records) for (const node of r.addedNodes) { // every new node
//     if (node.classList && node.classList.contains("rating")) setup(node); // initialize it
//   }
// });
// mo.observe(box, { childList: true });                    // watch direct children only
// fetch("/fragments/rating/42").then((r) => r.text())      // load the fragment
//   .then((html) => box.insertAdjacentHTML("beforeend", html)); // insert it; the observer fires
// function setup(el) { el.title = "Tap to rate"; }        // example setup for the new node
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Passing no observe options, so `observe()` throws an error
✅ Correct: You must choose at least one of `childList`, `attributes`, or `characterData`. Setting only `subtree` is not enough.

```javascript
// Wrong — throws TypeError: The options object must set at least one of
// 'attributes', 'characterData', or 'childList' to true.
observer.observe(list, { subtree: true });       // error: no kind of change chosen

// Right — choose what you want to watch
observer.observe(list, { childList: true, subtree: true }); // watch added and removed nodes
```

❌ **Mistake 2:** Forgetting that the callback is async, so code after `appendChild` runs first
✅ Correct: Do not expect the callback to run inside the same statement block. Read the state inside the callback, and do not assume the change is already reported.

```javascript
// Wrong — assumes the callback has already run when the next line executes
list.appendChild(li);                            // mutation happens now
console.log(callbackCount);                      // still 0: the callback has not run yet

// Right — do the work inside the callback that the observer gives you
const mo = new MutationObserver(() => {          // runs later, after the current code
  console.log("now we know the list changed");   // safe place for the reaction
});
mo.observe(list, { childList: true });           // watch the list
list.appendChild(li);                            // triggers the callback later
```

❌ **Mistake 3:** Never calling `disconnect()`, so the observer keeps running after the component is removed
✅ Correct: Call `disconnect()` when the component or page section is torn down, especially with `subtree: true` on `document.body`.

```javascript
// Wrong — the observer stays alive forever, even after the widget is removed
const mo2 = new MutationObserver(handle);        // created once
mo2.observe(document.body, { childList: true, subtree: true }); // watches the entire page forever

// Right — stop watching when the widget is removed
function closeWidget() {
  mo2.disconnect();                              // stop observing
  widget.remove();                               // remove the widget from the DOM
}
function handle() {}                             // placeholder callback
const widget = document.createElement("div");    // placeholder widget
const mo3 = new MutationObserver(handle);        // observer for this widget
mo3.observe(document.body, { childList: true, subtree: true });
```

---

## 🧠 Tricky Interview Question
What is printed? The code runs in one synchronous script with no awaits.

```javascript
const list = document.createElement("ul");      // a detached list (still fine to observe)
const a = document.createElement("li");         // first item
const b = document.createElement("li");         // second item

const mo = new MutationObserver((records) => {  // callback
  console.log("callback got", records.length, "records"); // how many records in this batch
});
mo.observe(list, { childList: true });          // watch the list for added children

list.appendChild(a);                            // change 1
list.appendChild(b);                            // change 2
console.log("sync code done");                  // printed before the callback
```

Answer: The output is:
```
sync code done
callback got 2 records
```
Explanation: The callback is queued as a microtask, so it runs only after the current synchronous code finishes. The line `sync code done` prints first. Both `appendChild` calls happened during the same synchronous block, so the browser delivers them together as one batch with two records. The observer does not call the callback once per change; it groups changes, which is why it is efficient.

---

## ⚫ Interview Questions + Answers

Q1: What is a mutation record?
A1: It is an object describing one change, with fields like `type` ("childList", "attributes", or "characterData"), `target` (the node that changed), `addedNodes`, `removedNodes`, and `attributeName`.

Q2: Why is `MutationObserver` better than the old mutation events?
A2: Mutation events fired synchronously for every change and slowed the page. `MutationObserver` batches changes and calls your callback as a microtask, so it is much faster.

Q3: What does `subtree: true` do?
A3: It extends the observation from the target's direct children to all of its descendants. Without it, only direct children changes are seen.

Q4: What is `takeRecords()` used for?
A4: It returns the pending records immediately and empties the queue, so you can process changes before the callback runs. It is also useful before calling `disconnect()` if you need the last changes.

Q5: Can a `MutationObserver` watch a node that is not in the document?
A5: Yes. The tricky example above observes a detached `<ul>` and still gets the records. This is useful when you build a subtree before inserting it into the page.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Third-party code or a framework changes the DOM and you must react to it
- You need to initialize content that arrives later, such as HTML from `fetch` or an injected widget
- You need to save or sync a document whenever its structure changes

❌ Avoid when:
- You only need to know when your own element is resized; use `ResizeObserver` (topic 155)
- You only need visibility; use `IntersectionObserver` (topic 153)
- You observe `document.body` with `subtree: true` and `attributes: true` all the time; this fires for almost every change and is costly

---

## 📊 Visual Diagram
```
 Your code / third-party script / framework
              │  changes DOM (appendChild, innerHTML, setAttribute...)
              ▼
 ┌──────────────────────────────────────────┐
 │ Browser checks: is this node observed?    │
 │ does this change type match options?     │
 └──────────────────┬───────────────────────┘
                    │ yes: create a mutation record
                    ▼
 ┌──────────────────────────────────────────┐
 │ records queue  [ r1, r2, r3 ... ]        │  the queue holds changes until the batch runs
 └──────────────────┬───────────────────────┘
                    │ current script finishes (microtask checkpoint)
                    ▼
     callback(records, observer)  ──►  your reaction code
                    │
     observer.disconnect() ──► stop observing (queue cleared)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MutationObserver | Watches DOM changes and reports them | DOM बदलावों को देखकर रिपोर्ट करने वाला API |
| Mutation record | One object describing one change | एक बदलाव का विवरण देने वाला object |
| `childList` | Watch added and removed child nodes | जुड़ने-हटने वाले children देखना |
| `attributes` | Watch attribute changes | Attribute बदलाव देखना |
| `characterData` | Watch text changes inside a node | Text के बदलाव देखना |
| `subtree` | Watch all descendants, not just children | सभी नीचे के nodes देखना |
| Microtask | Small task that runs after the current script | मौजूदा script के बाद चलने वाला छोटा task |
| `disconnect()` | Stop observing all targets | सब देखना बंद करना |
| `takeRecords()` | Read and clear pending records now | अभी के pending records पढ़ना |

---

## ⚡ 3-Line Summary
**English:**
1. `MutationObserver` reports changes to children, attributes, or text of a DOM node, in batches.
2. Choose `childList`, `attributes`, or `characterData` in the options, and add `subtree` for deeper nodes.
3. The callback runs after the current code, so disconnect the observer when it is no longer needed.

**Hindi:**
1. `MutationObserver` DOM node के children, attributes या text के बदलावों की रिपोर्ट batches में देता है।
2. Options में `childList`, `attributes` या `characterData` चुनें, और गहरे nodes के लिए `subtree` जोड़ें।
3. Callback मौजूदा code के बाद चलता है, इसलिए ज़रूरत न रहे तो observer को disconnect करें।

---

## ➡️ Next Topic
**155. ResizeObserver API** — अगला topic बताता है कि किसी element का size कब बदलता है, जो responsive charts और layout के लिए सही तरीका है।
