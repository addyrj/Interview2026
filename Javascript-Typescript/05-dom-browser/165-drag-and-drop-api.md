# 165. Drag and Drop API
# हिंदी में: Drag and Drop API

---

## 🔵 Simple Definition (English)
The Drag and Drop API lets the user pick up an element with the mouse or touch, move it, and release it on another target. The browser fires events on the dragged element (`dragstart`, `dragend`) and on the target (`dragenter`, `dragover`, `drop`). You also get a `DataTransfer` object that carries the data and the dropped files.

## 🔵 सरल परिभाषा (Hindi)
Drag and Drop API user को mouse या touch से किसी element को उठाकर खींचने और दूसरे target पर छोड़ने देता है। Browser dragged element पर (`dragstart`, `dragend`) और target पर (`dragenter`, `dragover`, `drop`) events चलाता है। साथ में `DataTransfer` object मिलता है, जिसमें data और छोड़ी गई files होती हैं।

---

## 🔴 Problem it Solves
Reordering a list or uploading a file by dragging needed a lot of custom code: `mousedown`, `mousemove`, `mouseup`, plus a ghost image and hit testing. It also failed on touch screens. The browser now does the hard parts. It draws the drag image, tracks the pointer, and gives you the data and files. For files, the API is also the only way to accept a file dropped from the desktop without a visible `<input type="file">`.

## 🔴 यह क्यों बना? (Hindi)
List को खींचकर reorder करने या file upload के लिए पहले बहुत custom code लगता था: `mousedown`, `mousemove`, `mouseup`, drag की image और hit testing। Touch screens पर यह अक्सर टूट जाता था। अब browser मुश्किल हिस्से खुद करता है: drag की image बनाता है, pointer को track करता है, और data व files देता है। Files के लिए यही तरीका है जिससे desktop से छोड़ी गई file बिना दिखने वाले `<input type="file">` के स्वीकार हो सके।

---

## 🟢 How it Works — Step by Step

Step 1 → Set `draggable="true"` on the element you want to move. Links and images are draggable by default.
Step 2 → On `dragstart`, call `e.dataTransfer.setData("text/plain", value)` if you need data, and store any state you need in a variable.
Step 3 → While the pointer is over a target, the browser fires `dragover` many times per second.
Step 4 → In `dragover`, call `e.preventDefault()`. Without it, the browser decides the target is not droppable and `drop` never fires.
Step 5 → On `drop`, call `e.preventDefault()` again, to stop the browser from opening a dropped link or file. Then read `e.dataTransfer.getData()` or `e.dataTransfer.files`.
Step 6 → The `dragend` event fires on the source element when the drag finishes, whether or not it was dropped.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → जिस element को खींचना है, उस पर `draggable="true"` लगाएँ। Links और images अपने-आप draggable होते हैं।
Step 2 → `dragstart` पर ज़रूरत हो तो `e.dataTransfer.setData("text/plain", value)` लगाएँ, और जो state चाहिए उसे variable में रखें।
Step 3 → जब pointer किसी target पर हो, browser हर सेकंड कई बार `dragover` चलाता है।
Step 4 → `dragover` में `e.preventDefault()` लगाएँ। इसके बिना browser उस target को droppable नहीं मानता और `drop` कभी नहीं चलता।
Step 5 → `drop` में फिर `e.preventDefault()` लगाएँ, ताकि browser छोड़ा गया link या file न खोले। फिर `e.dataTransfer.getData()` या `e.dataTransfer.files` पढ़ें।
Step 6 → Drag खत्म होने पर source element पर `dragend` चलता है, चाहे कुछ drop हुआ हो या नहीं।

---

## 🟡 Real World Example
A restaurant admin panel lets the owner drag menu items to change their order, so the most popular dishes like Paneer Tikka appear first. On a food delivery site, a user can drop a photo of a dish into a review box to upload it. A Razorpay or Paytm merchant dashboard can drag a CSV file onto the page for bulk settlements. In all three cases the app reads `dataTransfer`, updates its state, and sends the result to the server.

## 🟡 Real Example Hindi mein
Restaurant के admin panel में मालिक menu items को खींचकर क्रम बदल सकता है, ताकि Paneer Tikka जैसे लोकप्रिय items सबसे ऊपर दिखें। Food delivery site पर user review वाले box में खाने की फ़ोटो छोड़कर upload कर सकता है। Razorpay या Paytm merchant dashboard पर bulk settlement के लिए CSV file page पर छोड़ी जा सकती है। तीनों में app `dataTransfer` पढ़ता है, अपनी state बदलता है और नतीजा server पर भेजता है।

---

## 💻 Code Example — Basic
Browser-only. Save as `dnd-basic.html` and open it in a browser. The drag events exist only in the browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                      <!-- text encoding -->
  <title>Drag and Drop Basic</title>
  <style>
    li { padding: 8px; margin: 4px 0; border: 1px solid #aaa; list-style: none; cursor: grab; } /* row look */
    .dragging { opacity: 0.4; }                                /* faded while being dragged */
  </style>
</head>
<body>
  <ul id="list">                                               <!-- the list we reorder -->
    <li draggable="true">Dal Makhani</li>                      <!-- draggable row 1 -->
    <li draggable="true">Naan</li>                             <!-- draggable row 2 -->
    <li draggable="true">Paneer Tikka</li>                     <!-- draggable row 3 -->
  </ul>

  <script>
    const list = document.getElementById("list");              // the container
    let dragged = null;                                        // the row being dragged

    list.addEventListener("dragstart", (e) => {                // fires on the row that starts the drag
      dragged = e.target;                                      // remember which row is moving
      dragged.classList.add("dragging");                       // fade it while dragging
      e.dataTransfer.effectAllowed = "move";                   // allowed effect: move
    });

    list.addEventListener("dragend", () => {                   // fires when the drag ends, dropped or not
      dragged.classList.remove("dragging");                    // restore the look
      dragged = null;                                          // forget the dragged row
    });

    list.addEventListener("dragover", (e) => {                 // fires many times while hovering a row
      e.preventDefault();                                      // REQUIRED: marks this target as droppable
      e.dataTransfer.dropEffect = "move";                      // show the move cursor
    });

    list.addEventListener("drop", (e) => {                     // fires when the user releases over a target
      e.preventDefault();                                      // stop any browser default action
      const target = e.target.closest("li");                   // the row under the pointer, even if we hit text
      if (!target || target === dragged) return;               // dropped outside a row or on itself
      const rect = target.getBoundingClientRect();             // size and position of the target row
      const after = e.clientY > rect.top + rect.height / 2;    // true if dropped in the lower half
      if (after) target.after(dragged);                        // insert below the target
      else target.before(dragged);                             // insert above the target
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Browser-only page with two features: reorder a list without changing the original array, and accept a dropped image file. The `moveItem` helper has no DOM code, so Node can test it. Save as `dnd-advanced.html`, run the Express server below, and open `http://localhost:3000`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                      <!-- text encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1"> <!-- phone width -->
  <title>Drag and Drop Advanced</title>
  <style>
    body { font-family: sans-serif; margin: 16px; }            /* page spacing */
    li { padding: 8px; margin: 4px 0; border: 1px solid #ccc; background: #fff; cursor: grab; list-style: none; }
    li.dragging { opacity: 0.4; }                              /* faded row */
    #zone { border: 2px dashed #888; padding: 24px; text-align: center; border-radius: 8px; } /* drop area */
    #zone.over { border-color: #2a9d8f; background: #e9f5f3; } /* highlight while a file hovers */
  </style>
</head>
<body>
  <h3>Reorder the menu</h3>
  <ul id="menu"></ul>                                          <!-- rows are created by JavaScript -->
  <h3>Upload a dish photo</h3>
  <div id="zone">Drop an image here</div>                      <!-- file drop target -->
  <p id="statusText"></p>                                      <!-- upload result text -->

  <script>
    // ---- Pure helper: returns a NEW array with the item moved (no DOM, Node can test it) ----
    function moveItem(list, from, to) {                        // from and to are indexes
      const copy = list.slice();                               // never change the array we were given
      if (from === to) return copy;                            // nothing to move
      const [item] = copy.splice(from, 1);                     // take the item out
      copy.splice(to, 0, item);                                // put it back at the new index
      return copy;                                             // the new order
    }

    // ---- DOM part (browser only) ----
    let items = ["Dal Makhani", "Naan", "Paneer Tikka", "Lassi"]; // the menu state
    let dragIndex = null;                                      // index of the row being dragged
    const menu = document.getElementById("menu");              // the list element

    function renderMenu() {                                    // draws the list from the state
      menu.textContent = "";                                   // remove the old rows
      items.forEach((name, index) => {                         // one row per item
        const li = document.createElement("li");               // new row element
        li.textContent = name;                                 // text is safe from HTML injection
        li.draggable = true;                                   // rows can be dragged
        li.addEventListener("dragstart", (e) => {              // the drag begins on this row
          dragIndex = index;                                   // remember the source position
          e.dataTransfer.effectAllowed = "move";               // move, not copy
          e.dataTransfer.setData("text/plain", name);          // Firefox needs data to start a drag
          li.classList.add("dragging");                        // fade the row
        });
        li.addEventListener("dragend", () => li.classList.remove("dragging")); // restore the look
        li.addEventListener("dragover", (e) => {               // hovering a row
          e.preventDefault();                                  // REQUIRED to allow the drop
          e.dataTransfer.dropEffect = "move";                  // move cursor
        });
        li.addEventListener("drop", (e) => {                   // released on this row
          e.preventDefault();                                  // no default action
          if (dragIndex === null || dragIndex === index) return; // nothing changed
          items = moveItem(items, dragIndex, index);           // new array in the new order
          dragIndex = null;                                    // clear the drag state
          renderMenu();                                        // redraw from the new state
        });
        menu.appendChild(li);                                  // add the row to the list
      });
    }
    renderMenu();                                              // first draw

    const zone = document.getElementById("zone");              // file drop area
    const statusText = document.getElementById("statusText"); // status message element

    ["dragenter", "dragover"].forEach((type) => {              // a file is hovering the zone
      zone.addEventListener(type, (e) => {
        e.preventDefault();                                    // allow the drop
        zone.classList.add("over");                            // highlight the zone
      });
    });
    zone.addEventListener("dragleave", () => zone.classList.remove("over")); // hover ended

    zone.addEventListener("drop", async (e) => {               // a file was released on the zone
      e.preventDefault();                                      // do not let the browser open the file
      zone.classList.remove("over");                           // remove the highlight
      const file = e.dataTransfer.files[0];                    // first dropped File object
      if (!file) return;                                       // dropped text or nothing
      if (!file.type.startsWith("image/")) { statusText.textContent = "Only images are allowed."; return; }
      if (file.size > 5 * 1024 * 1024) { statusText.textContent = "Maximum size is 5 MB."; return; }
      statusText.textContent = `Uploading ${file.name}...`;    // progress message
      try {                                                    // network and HTTP errors go to catch
        const res = await fetch("/api/upload", {               // send the file to the server
          method: "POST",                                      // create a new upload
          headers: {                                           // describe the body
            "Content-Type": file.type,                         // for example image/png
            "X-File-Name": encodeURIComponent(file.name),      // keep the name safe in a header
          },
          body: file,                                          // a File is a Blob, so fetch streams it
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);    // 4xx or 5xx: treat as failure
        const data = await res.json();                         // read the JSON reply
        statusText.textContent = `Saved as ${data.saved}`;     // show the saved name
      } catch (err) {                                          // failed upload
        statusText.textContent = `Upload failed: ${err.message}`; // show the reason
      }
    });
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Express receives the dropped file as raw bytes. `express.raw()` keeps the body as a `Buffer` instead of parsing it. The server checks the type and size, removes unsafe characters from the name, and writes the file. This is the server for the advanced page.

```javascript
// server.js — npm install express; put the page in public/index.html; run: node server.js
const express = require("express");                          // web framework
const fs = require("fs/promises");                           // promise-based file system API
const path = require("path");                                // path helper

const app = express();                                       // create the app
app.use(express.static(path.join(__dirname, "public")));     // serve public/index.html
const UPLOAD_DIR = path.join(__dirname, "uploads");          // folder for uploaded files

// express.raw keeps the body as a Buffer for any type, up to 5 MB
app.post("/api/upload", express.raw({ type: "*/*", limit: "5mb" }), async (req, res) => {
  if (!Buffer.isBuffer(req.body) || req.body.length === 0) { // no bytes sent
    return res.status(400).json({ error: "empty file" });   // bad request
  }
  const type = String(req.get("Content-Type") || "");        // type the browser sent
  if (!type.startsWith("image/")) {                          // only images are accepted
    return res.status(415).json({ error: "images only" });   // 415 Unsupported Media Type
  }
  let name;                                                  // decoded file name
  try {
    name = decodeURIComponent(req.get("X-File-Name") || "upload"); // undo the browser's encoding
  } catch {
    return res.status(400).json({ error: "bad file name" });  // malformed percent-encoding
  }
  const safe = path.basename(name).replace(/[^a-zA-Z0-9._-]/g, "_"); // no folders, no odd characters
  const target = path.join(UPLOAD_DIR, `${Date.now()}-${safe}`); // unique name with a timestamp
  try {
    await fs.mkdir(UPLOAD_DIR, { recursive: true });         // create the folder if needed
    await fs.writeFile(target, req.body);                    // save the bytes to disk
    res.status(201).json({ saved: path.basename(target), bytes: req.body.length }); // created
  } catch (err) {                                             // disk failure
    console.error("upload failed:", err.message);             // log for the team
    res.status(500).json({ error: "could not save file" });   // generic message to the client
  }
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not calling `preventDefault()` in `dragover`, so `drop` never fires
✅ Correct: The browser treats a target as droppable only if `dragover` is cancelled.

```javascript
// Wrong — drop never runs, because the target is not marked as droppable
zone.addEventListener("dragover", (e) => {
  console.log("hovering");                                 // runs, but nothing else happens
});
zone.addEventListener("drop", (e) => console.log("dropped")); // never printed

// Right — cancel dragover to allow the drop
zone.addEventListener("dragover", (e) => {
  e.preventDefault();                                      // allow dropping here
});
zone.addEventListener("drop", (e) => console.log("dropped")); // runs now
```

❌ **Mistake 2:** Reading `getData()` during `dragover`
✅ Correct: Browsers hide drag data until `drop`. During `dragover`, `getData()` returns an empty string. Read data on `drop`, or save it in `dragstart`.

```javascript
// Wrong — always empty while the pointer is still moving
row.addEventListener("dragover", (e) => {
  e.preventDefault();
  const id = e.dataTransfer.getData("text/plain");       // "" during dragover
  console.log("hover over", id);                          // prints an empty name
});

// Right — read on drop
row.addEventListener("drop", (e) => {
  e.preventDefault();
  const id2 = e.dataTransfer.getData("text/plain");      // data is available now
  console.log("dropped", id2);
});
```

❌ **Mistake 3:** Using `e.target` when the drop lands on a child element
✅ Correct: `e.target` is the innermost element under the pointer, such as a `<span>` inside a row. Use `closest()` to find the row, or `currentTarget` on the listener.

```javascript
// Wrong — the row is missing when the pointer is over the text span
list.addEventListener("drop", (e) => {
  e.target.classList.add("done");                         // adds the class to the span, not the row
});

// Right — walk up to the row
list.addEventListener("drop", (e) => {
  const row = e.target.closest("li");                    // the nearest li, or null
  if (row) row.classList.add("done");                    // safe: only rows change
});
```

---

## 🧠 Tricky Interview Question
This test uses only plain JavaScript, so run it with `node tricky-dnd.js`. The helper looks like it returns a new array, but it does not.

```javascript
// tricky-dnd.js — run with: node tricky-dnd.js
function moveItem(list, from, to) {                        // a helper that moves an item
  const [item] = list.splice(from, 1);                     // removes the item from the ARRAY PASSED IN
  list.splice(to, 0, item);                                // inserts it back into the same array
  return list;                                             // returns the same array object
}

const original = ["A", "B", "C", "D"];                     // the menu before the drop
const result = moveItem(original, 0, 2);                   // move "A" to index 2
console.log(result);                                       // what is printed?
console.log(original);                                     // and what about this one?
console.log(result === original);                          // are they the same object?
```

Answer: The output is:
```
[ 'B', 'C', 'A', 'D' ]
[ 'B', 'C', 'A', 'D' ]
true
```
Explanation: `splice` changes the array in place. `splice(0, 1)` removes "A", leaving `["B", "C", "D"]`. Then `splice(2, 0, "A")` inserts "A" at index 2, giving `["B", "C", "A", "D"]`. The function returns the same array object, so `original` is changed too, and `result === original` is `true`. The advanced example avoids this by calling `list.slice()` first. In React or any state-based UI, mutating state in place is a bug, because the UI may not re-render.

---

## ⚫ Interview Questions + Answers

Q1: Which events does the dragged element fire, and which does the target fire?
A1: The dragged element fires `dragstart`, `drag` (repeatedly), and `dragend`. The target fires `dragenter`, `dragover` (repeatedly), `dragleave`, and `drop`.

Q2: Why must `dragover` call `preventDefault()`?
A2: By default, the browser does not allow a drop on any element. Cancelling `dragover` tells it the element accepts the drop, which then fires `drop`.

Q3: How do you accept a file dropped from the desktop?
A3: Listen for `drop`, call `preventDefault()`, and read `e.dataTransfer.files`. Each item is a `File`, which is a `Blob`, so you can send it with `fetch` or read it with `FileReader`.

Q4: Why does `e.dataTransfer.getData()` return an empty string in `dragover`?
A4: For security, browsers hide the data until the drop. `dragover` only exposes the types, so store the state in `dragstart` if you need it earlier.

Q5: Does drag and drop work on touch screens?
A5: Modern browsers support it with pointer and touch, but HTML5 drag and drop is not always reliable on mobile. For a touch-first reorder, many teams use pointer events directly or a library that handles touch.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The user reorders items in a list, board, or menu on a desktop
- The user drops files onto a page, such as photo or CSV upload
- You want a built-in drag image and cursor, without writing hit testing

❌ Avoid when:
- The app must work well on phones, because HTML5 drag and drop has weak touch support; use pointer events or a touch library
- A simple file input (`<input type="file">`) is enough and the user does not need drop
- The drag has to be keyboard-accessible but you have not added keyboard controls (for example, arrow keys to move an item)

---

## 📊 Visual Diagram
```
 User action            Browser event on the TARGET           Your code
 ───────────            ──────────────────────────           ─────────
 press + drag row  ──►  dragstart (on source row)  ───────►  save dragIndex
                        │
 hover over row    ──►  dragover (many times)      ───────►  e.preventDefault()
                        │                                    (required, or no drop)
 release mouse     ──►  drop                        ───────►  e.preventDefault()
                        │                                    read dataTransfer
                        ▼                                    moveItem() -> new state
                       dragend (on source row)  ───────►  cleanup

 Drop a file from the desktop:
   drop ─► e.dataTransfer.files[0] (File) ─► fetch(POST, body: file) ─► server saves
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| draggable | Attribute that lets an element be dragged | Element को खींचने लायक बनाने वाला attribute |
| dragstart | Fires on the source when a drag begins | Drag शुरू होने पर source पर चलने वाला event |
| dragover | Fires many times while hovering a target | Target पर मंडराते समय बार-बार चलने वाला event |
| drop | Fires on the target when the user releases | Target पर छोड़ने पर चलने वाला event |
| dragend | Fires on the source when the drag finishes | Drag खत्म होने पर source पर चलने वाला event |
| DataTransfer | Object holding drag data and files | Drag का data और files रखने वाला object |
| dropEffect | Cursor shown for the drop (copy, move, link) | Drop के लिए दिखने वाला cursor |
| preventDefault | Cancels the browser default and marks a target droppable | Browser का default रोकना और target को droppable बनाना |
| File | A file object (a kind of Blob) from the desktop | Desktop की file का object (Blob का एक प्रकार) |

---

## ⚡ 3-Line Summary
**English:**
1. Make an element `draggable`, store state in `dragstart`, and read the data in `drop`.
2. Cancel `dragover` with `preventDefault()` so the drop can happen, and cancel `drop` too.
3. Use `dataTransfer.files` for dropped files, and never mutate the array you receive; return a new one.

**Hindi:**
1. Element को `draggable` बनाएँ, `dragstart` में state रखें, और `drop` में data पढ़ें।
2. `dragover` में `preventDefault()` लगाएँ ताकि drop हो सके, और `drop` में भी।
3. छोड़ी गई files के लिए `dataTransfer.files` लें, और जो array मिले उसे न बदलें; नया array लौटाएँ।

---

## ➡️ Next Topic
**166. (next topic in the 05-dom-browser series)** — DOM और browser APIs वाले इस section में 165 के बाद का अगला topic। इसका title इस task की list में नहीं है, इसलिए यहाँ सिर्फ़ number दिया गया है।
