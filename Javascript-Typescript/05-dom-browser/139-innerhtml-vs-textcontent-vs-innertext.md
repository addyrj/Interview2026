# 139. innerHTML vs textContent vs innerText
# हिंदी में: innerHTML vs textContent vs innerText

---

## 🔵 Simple Definition (English)
These three properties read or write the content of an element. `innerHTML` works with markup (HTML tags as a string), `textContent` works with all raw text (ignores CSS and hidden state), and `innerText` works with the text the user actually sees on screen (respects CSS).

## 🔵 सरल परिभाषा (Hindi)
ये तीनों properties किसी element का content पढ़ती या लिखती हैं। `innerHTML` markup (HTML tags वाली string) के साथ काम करता है, `textContent` सारे raw text के साथ (CSS और hidden state को ignore करके), और `innerText` वह text देता है जो user को screen पर दिखता है (CSS का सम्मान करके)।

---

## 🔴 Problem it Solves
A developer often needs to show a value on the page. Sometimes the value is plain text (a username), sometimes it is formatted markup (bold price), and sometimes they need only what is visible (for copying to clipboard). Using the wrong property causes bugs: broken layout, security holes, or missing text. Three separate properties exist because the browser needs to handle three different questions: "what is the markup?", "what is the raw text?", and "what does the user see?"

## 🔴 यह क्यों बना? (Hindi)
Developer को अक्सर page पर कोई value दिखानी होती है। कभी वह plain text होती है (username), कभी formatted markup (bold price), और कभी सिर्फ वही जो visible है (clipboard पर copy करने के लिए)। गलत property चुनने से bugs आते हैं: layout टूटना, security holes, या text का गायब होना। तीन अलग properties इसलिए हैं क्योंकि browser तीन सवालों का जवाब देता है: "markup क्या है?", "raw text क्या है?", और "user को क्या दिख रहा है?"

---

## 🟢 How it Works — Step by Step

Step 1 → `innerHTML` getter serializes the child nodes back into an HTML string. Setter parses the string as HTML and replaces all children.
Step 2 → `textContent` getter concatenates the text of all descendant text nodes, including hidden ones and `<script>` / `<style>` content. Setter replaces children with one text node and does no parsing.
Step 3 → `innerText` getter computes the rendered text: it skips `display: none` content, applies `text-transform`, and turns block boxes into line breaks. This needs style and layout information.
Step 4 → `innerText` setter converts `\n` into `<br>` elements and does not parse HTML.
Step 5 → Performance: `textContent` is the cheapest, `innerHTML` costs parsing, and `innerText` can force layout (reflow).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `innerHTML` getter child nodes को वापस HTML string में बदलता है। Setter string को HTML की तरह parse करके सारे children बदल देता है।
Step 2 → `textContent` getter सारे descendant text nodes का text जोड़ता है, hidden text और `<script>` / `<style>` का content भी। Setter एक text node रखता है और कोई parsing नहीं करता।
Step 3 → `innerText` getter rendered text निकालता है: यह `display: none` वाला content छोड़ देता है, `text-transform` लगाता है, और block boxes को line breaks बनाता है। इसके लिए style और layout की जानकारी चाहिए।
Step 4 → `innerText` setter `\n` को `<br>` में बदलता है और HTML parse नहीं करता।
Step 5 → Performance: `textContent` सबसे सस्ता है, `innerHTML` में parsing लगती है, और `innerText` layout (reflow) को force कर सकता है।

---

## 🟡 Real World Example
On a Paytm bill page, the amount is shown in bold: `₹<b>499</b>`. The page sets `innerHTML` because it contains real markup. The user's name, which may contain characters like `<` or `&`, is set with `textContent`, so it can never inject markup. When a Flipkart user taps "Copy coupon code", the app reads `innerText` of the coupon box, because it must copy only what is visible, not hidden helper text.

## 🟡 Real Example Hindi mein
Paytm के bill page पर amount bold में दिखता है: `₹<b>499</b>`। यहाँ `innerHTML` इस्तेमाल होता है क्योंकि असली markup है। User का नाम, जिसमें `<` या `&` हो सकते हैं, `textContent` से लिखा जाता है, ताकि कभी भी markup inject न हो। Flipkart पर "Copy coupon code" दबाने पर app coupon box का `innerText` पढ़ता है, क्योंकि उसे सिर्फ वही copy करना है जो दिखता है, hidden helper text नहीं।

---

## 💻 Code Example — Basic
Save as `text-props-basic.html` and open it in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>innerHTML vs textContent vs innerText</title>
  <style>
    .hidden { display: none; }               /* hidden from the layout and from innerText */
    .upper  { text-transform: uppercase; }   /* CSS changes how text looks */
  </style>
</head>
<body>
  <div id="box">                             <!-- element we will read and write -->
    Price: <b>₹499</b>                       <!-- bold text is a child element -->
    <span class="hidden">(secret)</span>     <!-- hidden with CSS -->
  </div>
  <p id="upper" class="upper">zomato</p>     <!-- CSS will display this in capitals -->

  <script>
    const box = document.getElementById("box");  // the element to inspect

    // innerHTML returns the markup as a string (tags included)
    console.log(box.innerHTML);                  // includes <b> and <span> tags

    // textContent returns ALL text, including hidden text, with no tags
    console.log(box.textContent);                // includes "(secret)"

    // innerText returns only the text the user SEES (CSS-aware)
    console.log(box.innerText);                  // "Price: ₹499" — no "(secret)"

    // CSS text-transform affects innerText but not textContent
    const upper = document.getElementById("upper");
    console.log(upper.textContent);              // "zomato" — original case
    console.log(upper.innerText);                // "ZOMATO" — rendered uppercase

    // Writing with textContent: the value is treated as plain text
    const note = document.createElement("p");    // new paragraph
    note.textContent = "<b>Hi</b>";              // stored literally as text
    document.body.appendChild(note);            // page shows: <b>Hi</b> as text

    // Writing with innerHTML: the value is parsed as HTML
    const note2 = document.createElement("p");   // another paragraph
    note2.innerHTML = "<b>Hi</b>";               // becomes a real bold element
    document.body.appendChild(note2);           // page shows bold "Hi"
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `text-props-advanced.html`. It shows a safe renderer that uses `textContent` for user data, `innerHTML` only for trusted markup, and `innerText` to copy visible text.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Safe text rendering</title>
  <style>
    .badge { color: green; font-weight: bold; }  /* trusted style for the badge */
    .debug { display: none; }                    /* internal helper text, not visible */
  </style>
</head>
<body>
  <div id="review"></div>                        <!-- container for a user review -->
  <button id="copy">Copy visible text</button>   <!-- copies only what the user sees -->

  <script>
    // Untrusted input from a user review form (may contain HTML!)
    const userReview = { name: "<i>Aditya</i>", comment: "Great <script>alert(1)</script> food" };

    // Trusted markup written by our own developers (safe to use innerHTML here)
    const trustedBadge = '<span class="badge">Verified</span>';

    // Helper that builds the review card
    function renderReview(container, review) {    // container: node, review: object
      container.textContent = "";                  // clear old content safely

      const name = document.createElement("h3");   // heading for the name
      name.textContent = review.name;              // user data: textContent, never innerHTML

      const comment = document.createElement("p"); // paragraph for the comment
      comment.textContent = review.comment;        // shows the tags as literal text

      const badge = document.createElement("div"); // container for trusted markup
      badge.innerHTML = trustedBadge;              // trusted HTML from our code only

      const debug = document.createElement("span"); // internal helper element
      debug.className = "debug";                   // hidden by CSS
      debug.textContent = " [id=42]";              // helper text for developers

      container.append(name, comment, badge, debug); // add all parts in one call
    }

    const reviewBox = document.getElementById("review"); // find the container
    renderReview(reviewBox, userReview);                 // render the review

    // Copy only visible text: innerText skips the hidden debug span
    document.getElementById("copy").addEventListener("click", async () => {
      const visibleText = reviewBox.innerText;          // what the user actually sees
      try {
        await navigator.clipboard.writeText(visibleText); // modern async clipboard API
        console.log("Copied:", visibleText);             // confirm in console
      } catch (err) {                                     // clipboard may be blocked
        console.error("Copy failed:", err.message);      // log the reason
      }
    });

    // Escape helper for building HTML strings from trusted pieces (string-only, no DOM)
    function escapeHtml(str) {                          // turn special characters into entities
      return str
        .replace(/&/g, "&amp;")                         // must run first
        .replace(/</g, "&lt;")                          // escape less-than
        .replace(/>/g, "&gt;")                          // escape greater-than
        .replace(/"/g, "&quot;");                       // escape double quote
    }
    console.log(escapeHtml(userReview.comment));        // safe to use inside innerHTML
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
The server should send user content as data (JSON or escaped text), not as ready HTML. The browser then decides which property to use. Express can also escape values before they are put into a server-rendered template.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");        // web framework
const app = express();                     // create app

// Helper that escapes text for safe use inside HTML on the server side
function escapeHtml(text) {                // convert special chars to entities
  return String(text)                      // make sure input is a string
    .replace(/&/g, "&amp;")                // escape &
    .replace(/</g, "&lt;")                 // escape <
    .replace(/>/g, "&gt;")                 // escape >
    .replace(/"/g, "&quot;");              // escape "
}

// Route that renders a review page; user name is escaped before insertion
app.get("/review", (req, res) => {         // handle GET /review
  const name = req.query.name || "Guest";  // read ?name= from the URL
  res.send(`                               
    <!DOCTYPE html>
    <html>
      <body>
        <h2>Review by ${escapeHtml(name)}</h2>  <!-- safe: <script> becomes text -->
      </body>
    </html>
  `);
});

// JSON API: the browser receives raw data and sets it with textContent
app.get("/api/review", (req, res) => {     // handle GET /api/review
  res.json({ name: "<i>Aditya</i>", comment: "Great food" }); // raw data, no HTML
});

app.listen(3000, () => console.log("http://localhost:3000/review?name=Aditya"));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `innerHTML` for user-provided text
✅ Correct: Use `textContent` for any text that came from users or APIs.

```javascript
// Wrong — the <img onerror> runs when the browser parses this markup
card.innerHTML = `<h3>${user.name}</h3>`;

// Right — the name is displayed literally
const h3 = document.createElement("h3");
h3.textContent = user.name;
card.appendChild(h3);
```

❌ **Mistake 2:** Expecting `textContent` to skip hidden text
✅ Correct: `textContent` includes hidden text. Use `innerText` if you want only the visible text.

```javascript
// Wrong — copies helper text that the user cannot see
const copied = box.textContent;   // includes display:none content

// Right — only visible text (note: innerText triggers layout)
const visible = box.innerText;
```

❌ **Mistake 3:** Reading `innerText` in a loop after changing styles (layout thrashing)
✅ Correct: Read layout-dependent values once, then write.

```javascript
// Wrong — each read forces a new layout after the previous write
items.forEach((el) => {
  el.style.color = "red";        // write
  console.log(el.innerText);     // read forces layout every time
});

// Right — read all first, then write
const texts = items.map((el) => el.innerText); // one batch of reads
items.forEach((el) => (el.style.color = "red")); // then writes
```

---

## 🧠 Tricky Interview Question
Run this on a page that has `<div id="d">Hi<span style="display:none">X</span></div>` and nothing else.

```javascript
const d = document.getElementById("d");    // the div

console.log(d.textContent);                // ?
console.log(d.innerText);                  // ?
console.log(d.innerHTML);                  // ?

d.innerHTML = "&lt;b&gt;bold&lt;/b&gt;";   // assign escaped text as markup
console.log(d.textContent);                // ?
console.log(d.innerHTML);                  // ?
```

Answer: The outputs are, in order:
```
HiX                                  <- textContent: all text, hidden included
Hi                                   <- innerText: only the visible text
Hi<span style="display: none;">X</span>   <- innerHTML: serialized markup
<b>bold</b>                          <- textContent after the setter: entities were decoded
&lt;b&gt;bold&lt;/b&gt;                 <- innerHTML getter re-escapes the text
```
Explanation: the `innerHTML` setter parses the string `&lt;b&gt;bold&lt;/b&gt;`. The entities `&lt;` and `&gt;` become plain text characters `<` and `>`, not tags. So the element now holds one text node with the text `<b>bold</b>`, and `textContent` returns exactly that. When the `innerHTML` getter serializes a text node containing `<` and `>`, it escapes them back to `&lt;` and `&gt;`, so the output looks the same as the original string. The browser may print the span's style attribute with slightly different spacing, but the CSS is the same. The main lesson: `textContent` includes hidden text (`HiX`), `innerText` does not (`Hi`), and `innerHTML` returns serialized markup, not the rendered output.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `innerHTML` and `textContent`?
A1: `innerHTML` reads or writes markup and parses HTML when it is set. `textContent` reads or writes raw text, and it never parses HTML. For user data, `textContent` is the safe choice.

Q2: What is the difference between `innerText` and `textContent`?
A2: `innerText` returns the rendered text. It skips `display: none` content, respects `text-transform`, and uses line breaks for block elements. `textContent` returns all text in the DOM, including hidden text, and ignores CSS.

Q3: Does `innerText` cause a performance cost?
A3: Yes. Reading `innerText` needs style and layout information, so the browser may recalculate layout before returning. `textContent` does not need layout and is faster.

Q4: Is `innerHTML` always unsafe?
A4: Not always, but it is unsafe with untrusted input. It is fine for markup your own code controls. For user input, use `textContent`, create elements with `createElement`, or sanitize with a library like DOMPurify.

Q5: What does `element.innerHTML = ""` do to event listeners?
A5: It removes all child nodes, which means listeners attached to those children are gone with them. Listeners on the element itself stay. Event delegation on the parent avoids this problem.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `textContent`: showing any user or API text, or clearing an element
- `innerHTML`: inserting trusted, developer-written markup such as an SVG icon or a template
- `innerText`: copying or reading what the user actually sees, such as an on-screen label

❌ Avoid when:
- `innerHTML` with any untrusted input (XSS risk)
- `innerText` in tight loops or animation frames (costs layout)
- `innerHTML` when you only want to change one small text piece (it rebuilds children and loses listeners)

---

## 📊 Visual Diagram
```
<div id="d">Hi <span hidden-by-css>X</span></div>

Property       Returns                         Parses HTML on set?   Uses CSS/layout?
------------   -----------------------------   -------------------   ----------------
innerHTML      "Hi <span ...>X</span>" (markup) YES                   no
textContent    "Hi X"        (all text)         no                    no
innerText      "Hi"          (visible text)     no                    YES (may reflow)

textContent  ── all text nodes ──┐
innerText    ── rendered text ──┴── filtered by display:none, text-transform
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| innerHTML | Markup inside an element, as a string | Element के अंदर का markup string में |
| textContent | All raw text of an element and its descendants | Element का सारा raw text |
| innerText | Text as rendered on screen | Screen पर दिखने वाला text |
| Serialization | Converting nodes back to a string | Nodes को वापस string में बदलना |
| Parsing | Turning an HTML string into nodes | HTML string को nodes में बदलना |
| XSS | Injected script through markup | Markup के ज़रिए injected script |
| Reflow | Recalculating layout | Layout दोबारा निकालना |
| Entity | Escaped character like `&lt;` | `&lt;` जैसा escaped character |

---

## ⚡ 3-Line Summary
**English:**
1. `textContent` is the safe, fast choice for text; `innerHTML` parses markup and is risky with user input.
2. `innerText` returns only visible text, but it costs layout time, so use it only when visibility matters.
3. Choose by question: markup (`innerHTML`), all raw text (`textContent`), or what the user sees (`innerText`).

**Hindi:**
1. Text के लिए `textContent` सुरक्षित और तेज़ विकल्प है; `innerHTML` markup को parse करता है और user input के साथ खतरनाक है।
2. `innerText` सिर्फ visible text देता है, लेकिन इसमें layout का समय लगता है, इसलिए इसे तभी इस्तेमाल करें जब visibility मायने रखे।
3. सवाल के हिसाब से चुनें: markup (`innerHTML`), सारा raw text (`textContent`), या user को क्या दिखता है (`innerText`)।

---

## ➡️ Next Topic
**140. DOM Traversal (parentNode, children, siblings)** — अब सीखेंगे कि tree में parent, child और sibling nodes तक कैसे पहुँचें।
