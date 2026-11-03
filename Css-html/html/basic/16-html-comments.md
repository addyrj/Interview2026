# 16. HTML Comments
# हिंदी में: HTML Comments — Code में Notes जो Browser नहीं दिखाता

---

## 🔵 Simple Definition (English)
An HTML comment is text written as `<!-- comment -->`. The browser ignores it and does not display it, but it stays in the page source. Comments explain code, mark sections, or temporarily disable markup. They are **visible to anyone** who views the page source.

## 🔵 सरल परिभाषा (Hindi)
HTML comment वो text है जो `<!-- comment -->` में लिखा जाता है। Browser इसे ignore करता है और page पर नहीं दिखाता, लेकिन यह page source में रहता है। Comments code समझाने, sections mark करने या markup को अस्थायी रूप से बंद करने के काम आते हैं। इन्हें page source देखने वाला **कोई भी पढ़ सकता है**।

---

## 🔴 Problem it Solves
```
WITHOUT COMMENTS:
  <div></div></div></div></div>      <- which </div> closes what?
  - Teammates cannot understand why code exists
  - To test without a block you must DELETE it, then retype it
  - Large HTML files are hard to navigate

WITH COMMENTS:
  <!-- ===== Header ===== -->
  <header>...</header>
  <!-- ===== /Header ===== -->
  - Sections are labeled; closing tags are easy to match
  - TODO / FIXME notes for the team
  - Disable markup temporarily by wrapping it
```

## 🔴 यह क्यों बना? (Hindi)
```
COMMENTS के बिना:
  <div></div></div></div></div>      <- कौन सा </div> किसे बंद कर रहा है?
  - Teammates को समझ नहीं आता कि code क्यों है
  - Test करने के लिए block DELETE करना पड़ता, फिर दोबारा लिखना
  - बड़ी HTML files में navigate करना मुश्किल

COMMENTS के साथ:
  <!-- ===== Header ===== -->
  <header>...</header>
  <!-- ===== /Header ===== -->
  - Sections labeled रहते हैं; closing tags मिलाना आसान
  - टीम के लिए TODO / FIXME notes
  - Markup को wrap करके अस्थायी रूप से बंद करो
```

---

## 🟢 How it Works — Step by Step

```
SYNTAX:
  <!-- single line comment -->

  <!--
     multi-line comment
     spans many lines
  -->

1. Parser sees "<!--" and switches to comment mode.
2. Everything until the first "-->" is treated as a comment node (not rendered).
3. The comment IS part of the DOM (nodeType 8, Comment) but is not displayed.
4. It is downloaded with the page (adds bytes) and is visible in "View Source".

RULES AND GOTCHAS:
  - Comments cannot be nested: <!-- a <!-- b --> c -->  ends at the FIRST -->
    so " c -->" would appear as visible text.
  - Do not put "--" inside the comment text (older spec said illegal;
    HTML5 parsers tolerate it, but avoid it for safety).
  - Comments are allowed almost anywhere: before <html>, inside <head>, <body>.
    NOT inside a tag: <div <!-- x --> class="a"> is broken.
  - Inside <style> use /* css comment */  and inside <script> use // or /* */.
    <!-- --> there is NOT the right syntax.
  - Conditional comments (<!--[if IE]>) were old Internet Explorer only,
    removed in IE10. Do not use now.

GOOD USES:  section markers, explaining "why", TODO notes, temporarily hiding markup
BAD USES:   secrets (passwords, API keys, internal URLs), leaving huge dead code
```

## 🟢 कैसे काम करता है? (Hindi)

```
SYNTAX:
  <!-- single line comment -->
  <!--
     multi-line comment
  -->

1. Parser "<!--" देखता है और comment mode में चला जाता है।
2. पहले "-->" तक सब कुछ comment node माना जाता है (render नहीं होता)।
3. Comment DOM का हिस्सा होता है (nodeType 8) लेकिन दिखता नहीं।
4. यह page के साथ download होता है और "View Source" में दिखता है।

नियम और gotchas:
  - Comments nest नहीं होते: <!-- a <!-- b --> c --> पहले --> पर ही खत्म,
    बाकी " c -->" page पर text की तरह दिखेगा।
  - Tag के अंदर comment नहीं लिख सकते: <div <!-- x --> class="a"> गलत है।
  - <style> में /* */ और <script> में // या /* */ use होता है।
  - Conditional comments (<!--[if IE]>) पुराने Internet Explorer के लिए थे,
    अब use नहीं होते।

अच्छे उपयोग: section markers, "क्यों" समझाना, TODO, markup अस्थायी बंद करना
बुरे उपयोग: secrets (password, API key), बहुत सारा dead code छोड़ना
```

---

## 🟡 Real World Example
**Open any Amazon, Flipkart or Gmail page, press Ctrl+U (view source).** You will find build comments such as `<!-- BEGIN header -->` and `<!-- END footer -->`, ad-slot markers and framework markers. This is why you must never put secrets in comments: they are shipped to every visitor. Also, **Server-side rendered React** emits tiny comments like `<!--$-->` and `<!--/$-->` around Suspense boundaries; React uses them as markers during hydration.

## 🟡 Real Example Hindi mein
**Amazon, Flipkart या Gmail का कोई भी page खोलो और Ctrl+U (view source) दबाओ।** आपको `<!-- BEGIN header -->` और `<!-- END footer -->` जैसे build comments, ad-slot markers और framework markers मिलेंगे। इसीलिए comments में कभी secrets नहीं डालने चाहिए: ये हर visitor तक पहुँचते हैं। साथ ही, **Server-side rendered React** Suspense boundaries के आसपास `<!--$-->` और `<!--/$-->` जैसे छोटे comments डालता है; hydration के समय React इन्हें markers की तरह use करता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<!-- Comments are allowed even before <html> -->
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Comments Demo</title>

  <!-- CSS comments use a different syntax, see inside <style> -->
  <style>
    /* This is a CSS comment: <!-- --> is NOT used here */
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 30px auto; padding: 0 16px; }
    header { background: #e23744; color: #fff; padding: 16px; border-radius: 8px; }
    nav a { color: #fff; margin-right: 12px; }
    .menu { list-style: none; padding: 0; }
    .menu li { padding: 8px 0; border-bottom: 1px solid #eee; }
    footer { margin-top: 24px; color: #777; font-size: 14px; }
  </style>
</head>
<body>

  <!-- ===================== HEADER ===================== -->
  <header>
    <h1>Pizza Palace</h1>
    <nav>
      <a href="#menu">Menu</a>
      <a href="#about">About</a>
    </nav>
  </header>
  <!-- =================== /HEADER ====================== -->


  <!-- ===================== MENU ======================= -->
  <main id="menu">
    <h2>Today's Menu</h2>
    <ul class="menu">
      <li>Margherita - Rs 199</li>
      <li>Farmhouse - Rs 299</li>

      <!-- TODO: add Paneer Tikka pizza after the chef confirms the price -->

      <!-- Temporarily hidden: this item is out of stock. Remove comment to show it.
      <li>Peppy Paneer - Rs 349</li>
      -->

      <!-- Why: price shown WITHOUT GST because the legal team asked for it (ticket #482) -->
      <li>Veggie Delight - Rs 249</li>
    </ul>
  </main>

  <!-- Comments can wrap several elements at once (multi-line) -->
  <!--
  <section id="offers">
    <h2>Offers</h2>
    <p>50% off on Fridays!</p>
  </section>
  -->

  <footer id="about">
    <!-- A DO-NOT-DO example: never write secrets like the line below in real code
         <!-- api_key = "sk_live_123" -->
    -->
    &copy; 2026 Pizza Palace
  </footer>

  <script>
    // JS comments use // or /* */ (not <!-- -->)
    // Read comments from the DOM: they are real nodes (nodeType 8)
    const walker = document.createTreeWalker(document, NodeFilter.SHOW_COMMENT);
    let count = 0;
    while (walker.nextNode()) count++;
    console.log('Comment nodes in this page:', count);   // open DevTools Console
  </script>
</body>
</html>
```

Note on the demo: the "nested" comment inside `<footer>` ends at the first `-->`, so the stray `-->` after it is rendered as visible text. This is deliberate to show why you must not nest comments.

```css
/* CSS has its own comment syntax. Same idea, different markers. */
/* single line */
.card {
  color: red;  /* inline comment after a declaration */
  /* background: blue;   <- disabled declaration */
}
```

---

## 🟠 React/Next.js Connection

```jsx
// HTML comments (<!-- -->) do NOT work in JSX. They are a syntax error
// or would be shown as text. Use JS comments inside braces:

export default function Menu() {
  // Normal JS comment: outside the returned JSX
  return (
    <ul>
      {/* JSX comment: curly braces + block comment */}
      <li>Margherita</li>

      {/* Temporarily hidden item
      <li>Peppy Paneer</li>
      */}

      <li // JS comments are also OK inside a tag between attributes
        className="item"
      >
        Farmhouse
      </li>
    </ul>
  );
}

// 1. JSX comments are REMOVED at build time. Users never see them,
//    unlike HTML comments which are shipped to the browser. (Safer.)
// 2. To output a real HTML comment you need dangerouslySetInnerHTML (rarely needed).
// 3. Tailwind/CSS Modules: use /* */ in .css files.
// 4. Next.js minifies production HTML, but comments written in static .html
//    files or dangerouslySetInnerHTML content still reach the browser.
// 5. Use "TODO:" / "FIXME:" in JS comments; ESLint rules or editor extensions can list them.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you write a comment in HTML and is it visible to users?**
A1: `<!-- comment -->`. The browser does not render it, so it is not visible on the page, but it is sent to the browser and appears in View Source and DevTools. So it is not private.

**Q2: Can HTML comments be nested?**
A2: No. The comment ends at the first `-->`. Anything after it is treated as normal content and can show up as text. To disable a block that already contains a comment, remove the inner comment or use your editor's shortcut (Ctrl+/ or Cmd+/) which handles this correctly for the file type.

**Q3: What is the syntax of comments in CSS and JavaScript, and why not `<!-- -->`?**
A3: CSS uses `/* ... */`. JavaScript uses `// ...` for a single line and `/* ... */` for blocks. HTML comment syntax is only valid in the HTML parser context; inside `<style>` or `<script>` the content is parsed as CSS or JS, so `<!-- -->` is not the right syntax there. In JSX use `{/* ... */}`.

**Q4: Do comments affect performance or SEO?**
A4: They add bytes to the HTML download, so thousands of lines of dead commented code slow it slightly; build tools minify HTML and strip comments in production. They do not help SEO because search engines ignore them. Never rely on a comment to hide content from users or to hide secrets.

**Q5: Are comments part of the DOM?**
A5: Yes. A comment becomes a Comment node (`nodeType === 8`, `node.nodeValue` has the text). It is not in `element.children` (only elements) but is in `childNodes`. Frameworks sometimes use comment nodes as placeholders or markers (for example React hydration markers, or Vue's `<!---->` for `v-if` false).

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Storing secrets or private notes in comments
```html
<!-- admin password: admin123, test API key: sk_test_xxx -->
```
✅ **Correct way:** Keep secrets in server-side environment variables. Treat every HTML comment as public.

❌ **Mistake 2:** Using HTML comment syntax in JSX or CSS
```jsx
<div>
  <!-- wrong in JSX -->
</div>
```
✅ **Correct way:** `{/* correct in JSX */}` and `/* correct in CSS */`.

❌ **Mistake 3:** Commenting out obvious code or leaving big blocks of dead code
```html
<!-- this is a div --> <div>...</div>
```
✅ **Correct way:** Comment the **why**, not the what. Delete dead code; Git remembers history.

❌ **Mistake 4:** Nesting comments or putting `-->` inside the text
✅ **Correct way:** Avoid `--` and `>` sequences inside comment text; close the comment once.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Comment | Text ignored by the browser | Browser जिसे ignore करे वो text |
| `<!-- -->` | HTML comment markers | HTML comment के चिह्न |
| View Source | Shows raw HTML including comments | Raw HTML देखना |
| Comment node | DOM node with nodeType 8 | DOM में comment का node |
| Commenting out | Disabling code by wrapping in a comment | Code को अस्थायी रूप से बंद करना |
| TODO / FIXME | Marker for pending work | बाकी काम का marker |
| `{/* */}` | JSX comment syntax | JSX में comment |

---

## ⚡ 3-Line Summary
**English:**
1. `<!-- ... -->` is ignored by the browser but is still public in View Source, so never put secrets in it.
2. Comments cannot be nested; CSS uses `/* */`, JS uses `//`, and JSX uses `{/* */}`.
3. Write comments to explain the why and to label sections; remove dead code instead of leaving it commented.

**Hindi:**
1. `<!-- ... -->` को browser ignore करता है पर View Source में public रहता है, इसलिए secrets कभी मत डालो।
2. Comments nest नहीं होते; CSS में `/* */`, JS में `//`, और JSX में `{/* */}` लगता है।
3. Comments "क्यों" समझाने और sections label करने के लिए लिखो; dead code को comment में छोड़ने के बजाय हटाओ।

---

## ➡️ Next Topic
**17. HTML Entities (&nbsp; &lt; &gt; &amp;)** — जब page पर `<` या `&` जैसे special characters दिखाने हों तो उन्हें कैसे लिखें।
