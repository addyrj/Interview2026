# 60. Text Properties (align, transform, decoration, spacing)
# हिंदी में: Text Properties — Alignment, Case, Underline और Spacing

---

## 🔵 Simple Definition (English)
Text properties control the **layout and decoration** of text inside a box: `text-align` (left/center/right), `text-transform` (UPPERCASE/lowercase), `text-decoration` (underline, line-through), and spacing (`letter-spacing`, `word-spacing`, `text-indent`, `white-space`, `text-overflow`).

## 🔵 सरल परिभाषा (Hindi)
Text properties box के अंदर text की **alignment और सजावट** तय करती हैं: `text-align` (बाएँ/बीच/दाएँ), `text-transform` (बड़े/छोटे अक्षर), `text-decoration` (underline, line-through), और spacing (`letter-spacing`, `word-spacing`, `text-indent`, `white-space`, `text-overflow`)।

---

## 🔴 Problem it Solves
```
PROBLEM:
  - Want a heading centred? Old HTML: <center> or align="center" (deprecated).
  - Want ALL CAPS button labels? Retyping text in caps hurts SEO/accessibility and translation.
  - Links always underlined in blue (browser default) - unwanted in navbars.
  - Long product title overflows its card.

SOLUTION (CSS only, content stays untouched):
  h1 { text-align: center; }
  .btn { text-transform: uppercase; letter-spacing: .05em; }
  nav a { text-decoration: none; }
  .title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  - Heading बीच में चाहिए: पहले <center> tag (अब deprecated)।
  - Button में CAPS चाहिए: text को CAPS में टाइप करना SEO/translation के लिए अच्छा नहीं।
  - Links पर default नीला underline navbar में बुरा लगता है।
  - लंबा product title card से बाहर निकल जाता है।

हल: सिर्फ CSS से — text वैसा ही रहता है, दिखावट बदल जाती है।
```

---

## 🟢 How it Works — Step by Step

```
text-align        left | right | center | justify | start | end
                  Works on the BLOCK container (aligns its inline content), not on the block itself.
                  Use start/end for RTL languages (Arabic, Urdu) support.
                  Does NOT centre a block element: use margin: 0 auto / flex for that.

text-transform    none | uppercase | lowercase | capitalize (first letter of each word)
                  Only visual: the DOM text is unchanged.

text-decoration   shorthand: line style color thickness
                  text-decoration: underline wavy red 2px;
                  Longhands: text-decoration-line (underline | overline | line-through | none),
                             -style (solid|dashed|dotted|wavy), -color, -thickness
                  text-underline-offset: 4px;   (nicer underline gap)
                  Note: child can't remove a parent's underline with "none" - needs display:inline-block.

letter-spacing    space between letters (em recommended): 0.05em;  negative = tighter
word-spacing      space between words
text-indent       indent of first line: 2em
line-height       (topic 59)
white-space       normal | nowrap | pre | pre-wrap | pre-line
overflow-wrap     break-word (long words/URLs wrap)   word-break: break-all (aggressive)
text-overflow     ellipsis (needs: overflow:hidden; white-space:nowrap; and a width)
-webkit-line-clamp  multi-line ellipsis (needs display:-webkit-box; -webkit-box-orient: vertical;
                    overflow:hidden). Now widely supported incl. Firefox; newer line-clamp is coming.
text-shadow       0 1px 2px rgba(0,0,0,.4)
text-wrap         balance (even heading lines) | pretty   (Chrome 114+, Safari 17.5+, Firefox 121+ for balance)
vertical-align    for inline/table-cell content (not block centring!)
user-select       none (prevents selecting, use sparingly)
```

## 🟢 कैसे काम करता है? (Hindi)
```
text-align: left | right | center | justify
   -> container के अंदर के text को align करता है। Block element को खुद center नहीं करता
      (उसके लिए margin: 0 auto या flex)।

text-transform: uppercase | lowercase | capitalize
   -> सिर्फ दिखावट बदलती है, असली text वही रहता है।

text-decoration: underline | line-through | none
   -> links से underline हटाने के लिए none; style/color/thickness भी दे सकते हैं।

letter-spacing: अक्षरों के बीच जगह (em में); word-spacing: शब्दों के बीच।
text-indent: पहली line की indentation।

एक line में ellipsis (...) के लिए तीन चीज़ें साथ चाहिए:
   white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
कई lines में: -webkit-line-clamp: 2 (display:-webkit-box के साथ)।

overflow-wrap: break-word -> लंबे URL/शब्द wrap हो जाते हैं।
text-wrap: balance -> heading की lines बराबर बँटती हैं (नया)।
```

---

## 🟡 Real World Example
**Amazon / Swiggy / Instagram:** Swiggy restaurant names use `white-space: nowrap; text-overflow: ellipsis` so one long name doesn't break the card grid. Amazon product titles are clamped to 2 lines with `-webkit-line-clamp: 2`. Button labels ("ADD TO CART") are `text-transform: uppercase; letter-spacing: .05em`. Instagram captions use `white-space: pre-wrap` to keep line breaks and `overflow-wrap: anywhere` for long hashtags. Navigation links have `text-decoration: none` with underline appearing only on hover.

## 🟡 Real Example Hindi mein
**Amazon / Swiggy / Instagram:** Swiggy में restaurant का लंबा नाम `white-space: nowrap; text-overflow: ellipsis` से कट जाता है और card टूटता नहीं। Amazon के product titles `-webkit-line-clamp: 2` से 2 lines में रुकते हैं। "ADD TO CART" जैसे button labels में `text-transform: uppercase; letter-spacing: .05em`। Instagram captions में `white-space: pre-wrap` से line breaks बने रहते हैं। Nav links में `text-decoration: none` और hover पर underline।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Text Properties Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; line-height: 1.5; padding: 20px; background: #f9fafb; max-width: 640px; }
    h2 { font-size: 14px; margin: 22px 0 6px; color: #6b7280; text-transform: uppercase; letter-spacing: .08em; }
    .box { background: #fff; border: 1px solid #e5e7eb; padding: 10px; border-radius: 6px; }

    /* 1. text-align */
    .left    { text-align: left; }
    .center  { text-align: center; }
    .right   { text-align: right; }
    .justify { text-align: justify; }

    /* 2. text-transform (DOM text unchanged) */
    .upper { text-transform: uppercase; }
    .lower { text-transform: lowercase; }
    .cap   { text-transform: capitalize; }

    /* 3. text-decoration */
    .under  { text-decoration: underline; }
    .strike { text-decoration: line-through; color: #9ca3af; }     /* old price */
    .wavy   { text-decoration: underline wavy #dc2626 1px; }        /* spell-check look */
    .nice   { text-decoration: underline; text-underline-offset: 4px; text-decoration-thickness: 2px; text-decoration-color: #f59e0b; }
    a.nav   { text-decoration: none; color: #2563eb; }
    a.nav:hover { text-decoration: underline; }                     /* underline only on hover */

    /* 4. spacing */
    .ls   { letter-spacing: 0.15em; }
    .ls-n { letter-spacing: -0.03em; }
    .ws   { word-spacing: 0.5em; }
    .ind  { text-indent: 2em; }

    /* 5. single-line ellipsis */
    .ellipsis { width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; background: #fff7ed; padding: 4px; }

    /* 6. multi-line clamp (2 lines) */
    .clamp {
      width: 240px; background: #ecfeff; padding: 4px;
      display: -webkit-box;               /* required for the clamp */
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;              /* show 2 lines */
      line-clamp: 2;                      /* standard name (newer browsers) */
      overflow: hidden;
    }

    /* 7. white-space and wrapping */
    .pre  { white-space: pre-wrap; background: #f3f4f6; padding: 6px; }     /* keep line breaks and spaces */
    .long { width: 200px; overflow-wrap: anywhere; background: #fef2f2; padding: 4px; }

    /* 8. Button label styling + text-wrap: balance */
    .btn { background: #f59e0b; border: 0; padding: 10px 18px; border-radius: 6px; font: inherit;
           font-weight: 700; text-transform: uppercase; letter-spacing: .06em; cursor: pointer; }
    .balance { text-wrap: balance; max-width: 300px; font-size: 1.4rem; font-weight: 700; }

    /* 9. text-shadow */
    .shadow { font-size: 1.6rem; font-weight: 800; color: #fff; background: #4f46e5; padding: 10px;
              text-shadow: 0 2px 4px rgba(0,0,0,.5); }
  </style>
</head>
<body>
  <h2>text-align</h2>
  <div class="box left">Left (default)</div>
  <div class="box center">Centered</div>
  <div class="box right">Right</div>
  <div class="box justify">Justify stretches the spaces so both edges are flush, but it can create ugly gaps on narrow columns, so use it with care for long wrapped paragraphs.</div>

  <h2>text-transform</h2>
  <div class="box"><span class="upper">uppercase text</span> | <span class="lower">LOWERCASE TEXT</span> | <span class="cap">capitalize each word</span></div>

  <h2>text-decoration</h2>
  <div class="box">
    <span class="under">underline</span> |
    <span class="strike">Rs. 999</span> <strong>Rs. 499</strong> |
    <span class="wavy">wavy</span> |
    <span class="nice">styled underline</span> |
    <a class="nav" href="#">Nav link (hover me)</a>
  </div>

  <h2>spacing</h2>
  <div class="box"><span class="ls">WIDE LETTERS</span> | <span class="ls-n">tight letters</span> | <span class="ws">wide word spacing</span><p class="ind">Indented first line of a paragraph.</p></div>

  <h2>ellipsis (1 line)</h2>
  <div class="ellipsis">Paradise Biryani Restaurant and Family Dining, Hyderabad</div>

  <h2>line-clamp (2 lines)</h2>
  <div class="clamp">Apple iPhone 15 (128 GB) - Black with a very long product title that keeps going on and on and on to show the clamp</div>

  <h2>white-space / overflow-wrap</h2>
  <div class="pre">line one
    indented line two (kept)</div>
  <br>
  <div class="long">https://example.com/a/very/long/url/that/would/overflow/the/box/without/wrapping</div>

  <h2>button and balance</h2>
  <button class="btn">Add to cart</button>
  <p class="balance">Balanced headings avoid a single lonely word on the last line</p>

  <h2>text-shadow</h2>
  <div class="shadow">Shadow text</div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind has a utility for every property here
<h1 className="text-center uppercase tracking-wide underline decoration-amber-500 underline-offset-4">Title</h1>
<p className="truncate w-56">Long restaurant name...</p>          {/* nowrap + hidden + ellipsis */}
<p className="line-clamp-2">Long product title...</p>            {/* multi-line clamp (built in v3.3+) */}
<p className="text-balance">Heading text</p>                      {/* text-wrap: balance */}
<p className="whitespace-pre-wrap break-words">{caption}</p>

// 2. Capitalising user data: prefer CSS over JS string manipulation
//    WRONG: <span>{name.toUpperCase()}</span>   (changes the text itself, copy-paste, screen readers)
//    RIGHT: <span className="uppercase">{name}</span>

// 3. Inline style uses camelCase
<p style={{ textAlign: "center", textTransform: "uppercase", letterSpacing: "0.05em" }}>Hi</p>

// 4. Next.js <Link> renders <a>: underline is the browser default, remove it with CSS
<Link href="/cart" className="no-underline hover:underline">Cart</Link>

// 5. Truncate in a flex child: add min-w-0, otherwise ellipsis won't work
<div className="flex"><span className="min-w-0 truncate">Long name</span></div>
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you center text vs center a block element?**
A1: `text-align: center` on the **parent** centres inline content (text, inline-block, images) inside it. A block element is centred with `margin: 0 auto` (needs a width) or by making the parent flex/grid. `text-align` doesn't move the block itself.

**Q2: How do you truncate text with an ellipsis (one line and multiple lines)?**
A2: One line: `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;` plus a constrained width. Multi-line: `display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3; overflow: hidden;` (Tailwind `line-clamp-3`). In a flex child also add `min-width: 0`.

**Q3: What is the difference between `text-transform` and typing uppercase text?**
A3: `text-transform` is presentation only: the DOM/text content, copy-paste, SEO and screen-reader text remain unchanged, and it respects language rules. Typing caps changes the data itself and can read letter by letter in some screen readers.

**Q4: How do you remove the underline from links and add it back on hover? Any accessibility concern?**
A4: `a { text-decoration: none } a:hover { text-decoration: underline }`. Concern: colour alone must not be the only cue for links inside paragraphs (WCAG 1.4.1); keep underlines on in-text links or ensure 3:1 contrast with surrounding text plus another indicator.

**Q5: Difference between `word-break`, `overflow-wrap` and `white-space`?**
A5: `white-space` controls whether text wraps/collapses spaces (`nowrap`, `pre-wrap`). `overflow-wrap: break-word/anywhere` breaks a long word only when it would overflow. `word-break: break-all` breaks words at any character even when not needed (aggressive, ugly for Latin). Use `overflow-wrap` for URLs.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `text-align: center` to centre a div
```css
/* WRONG */
.card { text-align: center; width: 300px; }   /* text centred INSIDE, card stays left */

/* CORRECT */
.card { width: 300px; margin: 0 auto; }
```

❌ **Mistake 2:** Ellipsis missing one of the three ingredients
```css
/* WRONG: no overflow hidden, no width -> nothing happens */
.title { text-overflow: ellipsis; }

/* CORRECT */
.title { max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
```

❌ **Mistake 3:** Uppercasing with JS
```jsx
/* WRONG */ <span>{label.toUpperCase()}</span>
/* CORRECT */ <span className="uppercase">{label}</span>
```

❌ **Mistake 4:** Using px for letter-spacing
```css
/* WRONG: doesn't scale with font size */
h1 { letter-spacing: 2px; }

/* CORRECT */
h1 { letter-spacing: 0.05em; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| text-align | Horizontal alignment of inline content | Text की alignment |
| text-transform | Change case visually | अक्षरों का case बदलना |
| text-decoration | Underline / line-through | रेखा लगाना |
| letter-spacing | Space between letters | अक्षरों के बीच जगह |
| word-spacing | Space between words | शब्दों के बीच जगह |
| text-overflow | How clipped text is shown (ellipsis) | कटे text का ... |
| line-clamp | Limit to N lines | N lines तक सीमित |
| white-space | Wrapping and spaces control | Wrap/space नियंत्रण |

---

## ⚡ 3-Line Summary
**English:**
1. `text-align` aligns inline content in a container; `text-transform` and `text-decoration` change look without changing the text.
2. Ellipsis needs `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`; multi-line uses `line-clamp`.
3. Use `em` for letter-spacing, and Tailwind classes (`truncate`, `line-clamp-2`, `uppercase`) in React.

**Hindi:**
1. `text-align` container के अंदर text align करता है; `text-transform` और `text-decoration` text बदले बिना दिखावट बदलते हैं।
2. Ellipsis के लिए `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`; कई lines के लिए `line-clamp`।
3. `letter-spacing` em में लिखो, React में Tailwind classes (`truncate`, `line-clamp-2`, `uppercase`) use करो।

---

## ➡️ Next Topic
**61. Background Properties** — color, image, size, position, repeat, gradients, ताकि cards, banners और hero sections सजा सको।
