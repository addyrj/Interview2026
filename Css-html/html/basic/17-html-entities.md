# 17. HTML Entities (&nbsp; &lt; &gt; &amp;)
# हिंदी में: HTML Entities — Special Characters को सुरक्षित तरीके से लिखना

---

## 🔵 Simple Definition (English)
An HTML entity is a code that starts with `&` and ends with `;` and represents a special character, for example `&lt;` for `<`, `&amp;` for `&`, `&nbsp;` for a non-breaking space and `&copy;` for the copyright sign. It lets you show characters that HTML would otherwise read as markup.

## 🔵 सरल परिभाषा (Hindi)
HTML entity एक code है जो `&` से शुरू और `;` पर खत्म होता है और किसी special character को दर्शाता है, जैसे `<` के लिए `&lt;`, `&` के लिए `&amp;`, non-breaking space के लिए `&nbsp;` और copyright चिह्न के लिए `&copy;`। इससे वे characters दिखाए जा सकते हैं जिन्हें HTML वरना markup समझ लेता।

---

## 🔴 Problem it Solves
```
PROBLEM 1: Reserved characters
  <p>Use <div> to make a box</p>
  -> Browser thinks <div> is a real tag! Text disappears, layout breaks.

PROBLEM 2: Extra spaces are collapsed
  <p>Hello          World</p>   -> shows "Hello World" (one space)

PROBLEM 3: Characters not on the keyboard
  (c) (R) TM Euro-sign, arrows, math symbols

SOLUTION: entities
  <p>Use &lt;div&gt; to make a box</p>   -> shows: Use <div> to make a box
  Hello&nbsp;&nbsp;&nbsp;World           -> keeps the spaces
  &copy; 2026                            -> (c) 2026

SECURITY: escaping user text as entities is the core defense against XSS.
  "<script>alert(1)</script>" -> "&lt;script&gt;alert(1)&lt;/script&gt;" (harmless text)
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या 1: Reserved characters
  <p>Box बनाने के लिए <div> use करो</p>
  -> Browser <div> को असली tag समझता है! Text गायब, layout टूटा।

समस्या 2: Extra spaces collapse हो जाती हैं
  <p>Hello          World</p>   -> "Hello World" (सिर्फ एक space)

समस्या 3: Keyboard पर न मिलने वाले characters
  (c) (R) TM Euro-sign, arrows, math symbols

समाधान: entities
  <p>Box बनाने के लिए &lt;div&gt; use करो</p>   -> दिखता है: <div>
  Hello&nbsp;&nbsp;&nbsp;World                   -> spaces बनी रहती हैं
  &copy; 2026                                    -> (c) 2026

SECURITY: user के text को entities में बदलना (escape) XSS से बचाव का मूल तरीका है।
```

---

## 🟢 How it Works — Step by Step

```
FORMS OF AN ENTITY (all start with & and end with ;):
  1. Named      &lt;      &amp;     &copy;
  2. Decimal    &#60;     &#38;     &#169;
  3. Hex        &#x3C;    &#x26;    &#xA9;

THE MUST-KNOW ONES:
  Character   Entity     Why
  ─────────   ────────   ─────────────────────────────────
  <           &lt;       less-than: starts a tag
  >           &gt;       greater-than: ends a tag
  &           &amp;      starts an entity itself
  "           &quot;     inside double-quoted attribute values
  '           &apos; or &#39;   inside single-quoted attribute values
  (space)     &nbsp;     NON-BREAKING space (never wraps, never collapses)
  (c)         &copy;     copyright sign
  (R)         &reg;      registered
  Rupee       &#8377;    Indian rupee sign (also just type the character in UTF-8)
  Euro        &euro;     Euro sign
  Arrow       &rarr;     right arrow
  ...         &hellip;   ellipsis
  Em dash     &mdash;    long dash

HOW THE BROWSER USES THEM:
1. The parser reads text. On "&" it tries to match an entity name.
2. If it matches (e.g. &lt;), it replaces it with the real character in the DOM text.
3. The character is then DISPLAYED as text and never treated as markup.
4. The DOM holds the real character ("<"). The entity is only source-code spelling.

&nbsp; DETAILS:
  - It is a normal-looking space that the browser will not collapse or break at.
  - Good for: "10&nbsp;kg", "Mr.&nbsp;Sharma" (keep words together).
  - Bad for: layout/indentation. Use CSS (margin, padding, gap) instead.

BECAUSE OF UTF-8 you can type most characters directly: (c) Rs arrows, Hindi.
Entities are REQUIRED only for: < > & (and quotes in attribute values).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Entity के रूप (सब & से शुरू, ; पर खत्म):
  1. Named      &lt;      &amp;     &copy;
  2. Decimal    &#60;     &#38;     &#169;
  3. Hex        &#x3C;    &#x26;    &#xA9;

ज़रूरी entities:
  <   -> &lt;      (tag शुरू करता है)
  >   -> &gt;
  &   -> &amp;     (entity खुद & से शुरू होती है)
  "   -> &quot;    (attribute value में)
  space -> &nbsp;  (टूटने या collapse न होने वाली space)
  (c) -> &copy;    Rupee -> &#8377;

Browser कैसे use करता है:
1. Parser "&" देखकर entity का नाम match करता है।
2. Match होने पर DOM text में असली character रख देता है।
3. वह character text की तरह दिखता है, markup की तरह नहीं।

&nbsp; के नियम:
  - यह ऐसी space है जो collapse या line-break नहीं होती।
  - अच्छा: "10&nbsp;kg", "Mr.&nbsp;Sharma" (शब्द साथ रखना)।
  - बुरा: layout/indentation के लिए। इसके लिए CSS (margin, padding, gap) use करो।

UTF-8 की वजह से ज़्यादातर characters सीधे type कर सकते हैं।
Entities ज़रूरी सिर्फ < > & के लिए हैं (और attribute में quotes के लिए)।
```

---

## 🟡 Real World Example
**Stack Overflow / GitHub code blocks:** when a tutorial shows `<div class="box">`, the page source actually contains `&lt;div class="box"&gt;`. **Amazon footers** show "&copy; 1996-2026, Amazon.com, Inc." via `&copy;`. **Swiggy price labels** like "Rs&nbsp;249" keep the currency and number on the same line so it never wraps as "Rs" at the end of a line and "249" on the next. **Comment sections (Instagram):** if you post `<script>alert(1)</script>` as a comment, the site stores/escapes it as entities, so it shows as plain text and does not run.

## 🟡 Real Example Hindi mein
**Stack Overflow / GitHub code blocks:** जब tutorial में `<div class="box">` दिखता है, तो page source में असल में `&lt;div class="box"&gt;` होता है। **Amazon के footer** में "&copy; 1996-2026, Amazon.com, Inc." `&copy;` से बनता है। **Swiggy के price labels** जैसे "Rs&nbsp;249" में currency और number एक ही line पर रहते हैं, कभी "Rs" एक line के अंत में और "249" अगली line में नहीं जाता। **Comment sections (Instagram):** अगर आप `<script>alert(1)</script>` comment करो, तो site उसे entities में escape करती है, इसलिए वह plain text दिखता है और चलता नहीं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"> <!-- UTF-8 lets you type most symbols directly -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Entities Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 680px; margin: 30px auto; padding: 0 16px; line-height: 1.6; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f5f5f5; }
    code { background: #f1f1f1; padding: 1px 6px; border-radius: 4px; }
    .price { background: #fff3e0; padding: 4px 8px; border-radius: 4px; }
    .narrow { width: 90px; border: 1px dashed #999; padding: 4px; }   /* forces wrapping */
    pre { background: #222; color: #cfc; padding: 12px; border-radius: 6px; overflow: auto; }
  </style>
</head>
<body>
  <h1>HTML Entities</h1>

  <!-- 1. Showing tag code on the page: escape < and > -->
  <h2>1. Show code as text</h2>
  <p>To make a box use <code>&lt;div class="box"&gt;Hello&lt;/div&gt;</code></p>

  <!-- 2. Ampersand: a bare & works usually, but &amp; is the correct form,
          especially in URLs inside attributes -->
  <h2>2. Ampersand</h2>
  <p>Tom &amp; Jerry, Q&amp;A, R&amp;D</p>
  <a href="https://example.com/search?q=pizza&amp;city=delhi">Search link (note &amp;amp; in href)</a>

  <!-- 3. Non-breaking space: multiple spaces, and keeping words together -->
  <h2>3. &amp;nbsp;</h2>
  <p>Normal: Hello          World (spaces collapse)</p>
  <p>With nbsp: Hello&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;World</p>
  <div class="narrow">Total: <span class="price">Rs 249</span> only</div>
  <div class="narrow">Total: <span class="price">Rs&nbsp;249</span> only</div>

  <!-- 4. Symbols table: three ways to write the same character -->
  <h2>4. Common symbols</h2>
  <table>
    <tr><th>Shows</th><th>Named</th><th>Decimal</th><th>Hex</th></tr>
    <tr><td>&copy;</td><td><code>&amp;copy;</code></td><td><code>&amp;#169;</code></td><td><code>&amp;#xA9;</code></td></tr>
    <tr><td>&reg;</td><td><code>&amp;reg;</code></td><td><code>&amp;#174;</code></td><td><code>&amp;#xAE;</code></td></tr>
    <tr><td>&#8377;</td><td>(none, use number)</td><td><code>&amp;#8377;</code></td><td><code>&amp;#x20B9;</code></td></tr>
    <tr><td>&rarr;</td><td><code>&amp;rarr;</code></td><td><code>&amp;#8594;</code></td><td><code>&amp;#x2192;</code></td></tr>
    <tr><td>&hellip;</td><td><code>&amp;hellip;</code></td><td><code>&amp;#8230;</code></td><td><code>&amp;#x2026;</code></td></tr>
    <tr><td>&quot;</td><td><code>&amp;quot;</code></td><td><code>&amp;#34;</code></td><td><code>&amp;#x22;</code></td></tr>
  </table>

  <!-- 5. Quotes inside attribute values -->
  <h2>5. Quotes in attributes</h2>
  <input type="text" value="He said &quot;hello&quot;" size="30">

  <!-- 6. Entities vs escaping user input with JavaScript (XSS safety) -->
  <h2>6. XSS: escape user text</h2>
  <input id="userText" value="<img src=x onerror=alert(1)>" size="40">
  <button id="go">Show safely</button>
  <div id="out"></div>
  <pre id="source"></pre>

  <script>
    document.getElementById('go').addEventListener('click', () => {
      const raw = document.getElementById('userText').value;

      // SAFE: textContent treats the string as TEXT (browser shows it literally)
      document.getElementById('out').textContent = raw;

      // Manual escape, shows what entities look like in the generated source
      const escaped = raw.replace(/&/g, '&amp;').replace(/</g, '&lt;')
                         .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
      document.getElementById('source').textContent = escaped;

      // UNSAFE (do not do): out.innerHTML = raw   -> would run the onerror handler
    });
  </script>
</body>
</html>
```

```css
/* Prefer CSS over &nbsp; for layout. */
.tag + .tag { margin-left: 8px; }   /* instead of &nbsp;&nbsp; between tags */
.keep-together { white-space: nowrap; }  /* instead of &nbsp; between words */
.indent { padding-left: 2rem; }          /* instead of &nbsp;&nbsp;&nbsp;&nbsp; */
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. JSX escapes text automatically: {userInput} is rendered as TEXT, so
//    <script> strings cannot run. This protects you from most XSS by default.
function Comment({ text }) {
  return <p>{text}</p>;            // "<b>hi</b>" appears literally, not bold
}

// 2. Entities in JSX text work (JSX understands HTML entities in literal text):
<p>Tom &amp; Jerry &copy; 2026 &nbsp; Rs&nbsp;249</p>

// 3. But entities in a JS STRING do not decode:
<p>{"Tom &amp; Jerry"}</p>         // shows "Tom &amp; Jerry" literally!
// Fix: use the real character, or a unicode escape:
<p>{"Tom & Jerry"}</p>
<p>{" "}</p>                  // non-breaking space via unicode escape
<p>{'Rs 249'}</p>

// 4. Writing < > { } as visible text inside JSX needs care:
<p>{'<div>'}</p>                   // OK as a string expression
<p>&lt;div&gt;</p>                 // OK as entities
// <p><div></p>                    // WRONG: parsed as a real element

// 5. ESLint rule react/no-unescaped-entities warns about raw > " ' } in JSX text.
// 6. dangerouslySetInnerHTML bypasses escaping: sanitize with DOMPurify first.
// 7. Tailwind spacing: use className="mr-2" or "whitespace-nowrap" instead of &nbsp;.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is an HTML entity and why do we need them?**
A1: An entity is an `&name;` or `&#number;` sequence that represents a character. We need them for reserved characters (`<`, `>`, `&`, quotes in attributes) that the parser would treat as markup, for characters hard to type, and for special whitespace like `&nbsp;`.

**Q2: What is `&nbsp;` and how is it different from a normal space?**
A2: `&nbsp;` is a non-breaking space (U+00A0). A normal space can collapse (multiple spaces become one) and the line can wrap at it. A non-breaking space does not collapse and the browser will not break the line there. Use it to keep things like "10 kg" together, but use CSS (`margin`, `padding`, `white-space: nowrap`) for layout.

**Q3: How do you display `<div>` as text on a web page?**
A3: Write `&lt;div&gt;`. In a code sample also wrap it in `<code>` or `<pre>`. Escape at least `<` and `&`; escaping `>` is good practice.

**Q4: How do entities relate to XSS prevention?**
A4: Escaping user-provided text (`<` to `&lt;`, `&` to `&amp;`, quotes to `&quot;`) makes the browser treat it as text, not as tags or scripts. React does this by default for `{value}` in JSX. Risky APIs are `innerHTML` and `dangerouslySetInnerHTML`; prefer `textContent` or sanitize with DOMPurify. The escaping needed depends on the context (HTML text, attribute, URL, JS), so use a library or framework instead of ad-hoc regex.

**Q5: Why does `{"&amp;"}` print `&amp;` in React but `&amp;` in JSX text prints `&`?**
A5: JSX literal text goes through the JSX/HTML entity decoding step at compile time, so `&amp;` becomes `&`. A JavaScript string inside curly braces is a plain string and is not decoded; React then escapes it again for the DOM, so you literally see `&amp;`. Use the real character (`"&"`) or a unicode escape (`" "`).

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `&nbsp;` for layout
```html
<p>&nbsp;&nbsp;&nbsp;&nbsp;Indented text</p>
<br>&nbsp;<br>&nbsp;<br>   <!-- fake spacing -->
```
✅ **Correct way:** `p { padding-left: 2rem; }` and `margin-bottom` for vertical spacing.

❌ **Mistake 2:** Forgetting the semicolon or the `&amp;` in URLs
```html
<p>5 &lt 6</p>                     <!-- missing ; : browsers often still decode, but it's invalid -->
<a href="?a=1&b=2">Link</a>        <!-- "&b" could be misread in some contexts -->
```
✅ **Correct way:** `&lt;` and `href="?a=1&amp;b=2"`.

❌ **Mistake 3:** Putting raw user input into the page
```js
div.innerHTML = userComment;   // XSS risk
```
✅ **Correct way:** `div.textContent = userComment;` or React `{userComment}`.

❌ **Mistake 4:** Using entities inside a JS string in JSX and expecting decoding
✅ **Correct way:** Use the actual character or ` `.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Entity | `&name;` code for a character | Character का code |
| `&lt;` `&gt;` | Less-than, greater-than | `<` और `>` के entities |
| `&amp;` | Ampersand | `&` का entity |
| `&nbsp;` | Non-breaking space | न टूटने वाली space |
| `&copy;` | Copyright sign | Copyright चिह्न |
| Numeric reference | `&#169;` / `&#xA9;` form | संख्या वाला रूप |
| Escaping | Converting special chars to entities | Special chars को entities में बदलना |
| XSS | Injecting scripts via unescaped input | Script inject करने वाला हमला |

---

## ⚡ 3-Line Summary
**English:**
1. Entities (`&lt; &gt; &amp; &nbsp; &copy;`) let you show reserved or special characters that HTML would otherwise read as markup.
2. `&nbsp;` is a non-breaking space for keeping words together; use CSS, not `&nbsp;`, for layout spacing.
3. Escaping user text prevents XSS; React escapes `{value}` automatically, but `dangerouslySetInnerHTML` does not.

**Hindi:**
1. Entities (`&lt; &gt; &amp; &nbsp; &copy;`) से वो special characters दिखते हैं जिन्हें HTML वरना markup समझ लेता।
2. `&nbsp;` शब्दों को साथ रखने वाली space है; layout spacing के लिए CSS use करो, `&nbsp;` नहीं।
3. User text escape करने से XSS रुकता है; React `{value}` को अपने आप escape करता है, पर `dangerouslySetInnerHTML` नहीं।

---

## ➡️ Next Topic
**18. Inline vs Block Elements** — elements page पर कैसे बैठते हैं (पूरी line लेते हैं या सिर्फ अपनी चौड़ाई), यह layout की नींव है।
