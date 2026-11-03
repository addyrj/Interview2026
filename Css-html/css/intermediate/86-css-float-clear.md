# 86. CSS Float + Clear (legacy)
# हिंदी में: CSS Float और Clear — पुराना Layout तरीका जो अब भी interview में पूछा जाता है

---

## 🔵 Simple Definition (English)
`float: left | right` pushes an element to one side of its container so that text and inline content wrap around it, like a photo in a newspaper article. `clear: left | right | both` stops an element from sitting next to earlier floats and moves it below them. Floats were once used for whole-page layouts, but today they are for text wrap only; Flexbox and Grid handle layout.

## 🔵 सरल परिभाषा (Hindi)
`float: left | right` element को container के एक किनारे पर धकेल देता है और text उसके चारों तरफ लिपट जाता है, जैसे अखबार में photo के आसपास text। `clear: left | right | both` element को पिछले floats के नीचे भेज देता है। पहले पूरे page का layout floats से बनता था; आज floats सिर्फ text wrap के लिए हैं, layout के लिए Flexbox और Grid हैं।

---

## 🔴 Problem it Solves
```
BEFORE FLOAT (1990s):
  - HTML had no way to wrap text around an image except the <img align="left"> attribute
  - Multi-column layouts used <table> tags (bad for accessibility and responsiveness)

FLOAT ERA (2000-2015):
  - float: left on columns gave a 3-column layout without tables
  - Side effects: parent collapses to 0 height, so "clearfix" hacks appeared

TODAY:
  - Flexbox (1D) and Grid (2D) replaced float for layout
  - float remains correct for: text wrapping around an image/pull-quote, and shape-outside effects
  - You must know it for interviews and for reading legacy code (Bootstrap 2/3, old WordPress themes)
```

## 🔴 यह क्यों बना? (Hindi)
```
Float से पहले:
  - Image के आसपास text wrap करने का सिर्फ <img align="left"> था
  - कई columns के लिए <table> use होता था (accessibility और responsive के लिए खराब)

Float का दौर (2000-2015):
  - Columns पर float: left लगाकर table के बिना layout बनता था
  - Side effect: parent की height 0 हो जाती थी, इसलिए "clearfix" hack आया

आज:
  - Layout के लिए Flexbox और Grid
  - Float सिर्फ text wrap, pull-quote और shape-outside के लिए सही है
  - Interview और पुराने code (Bootstrap 3, WordPress themes) पढ़ने के लिए जानना ज़रूरी है
```

---

## 🟢 How it Works — Step by Step

```
1. FLOAT TAKES THE ELEMENT OUT OF NORMAL FLOW (partially):
     img { float: left; margin: 0 16px 8px 0; }
     - The element shifts to the left edge of its containing block
     - Following BLOCK boxes ignore it (they slide underneath as if it wasn't there)
     - Following INLINE content (text) wraps around it
     - A floated element becomes display: block (computed), and shrinks to fit its content
       (so give it a width for layout columns)

2. VALUES: left | right | none (default) | inline-start | inline-end (logical, supports RTL)

3. THE COLLAPSED PARENT PROBLEM:
     <div class="parent">  <div class="child" style="float:left"> ... </div> </div>
     The parent only contains floated children, so its height becomes 0.
     Background/border of the parent disappear around the children.

4. CLEARING:
     clear: left   -> element moves below earlier LEFT floats
     clear: right  -> below RIGHT floats
     clear: both   -> below any float  (most used)
     clear applies to BLOCK-level elements.

5. CLEARFIX (fixing the collapsed parent, 3 ways):
     a) Classic pseudo-element:
          .clearfix::after { content: ""; display: table; clear: both; }
     b) Make parent a block formatting context:
          .parent { overflow: auto; }      (or overflow: hidden)  - may clip shadows/dropdowns
     c) MODERN:
          .parent { display: flow-root; }  - purpose-built, no side effects
          Support: Chrome 58+, Firefox 53+, Safari 13+

6. TEXT WRAP SHAPES:
     .circle { float: left; width: 150px; height: 150px; shape-outside: circle(50%); }
     Text follows the circle edge instead of the rectangle. (shape-outside: Chrome 37+, Safari 10.1+, Firefox 62+.)

7. FLEX/GRID ITEMS IGNORE float: floats have no effect on direct children of flex or grid containers.

8. WHY NOT FOR LAYOUT NOW:
     - Needs clearfix, fragile widths (sub-pixel rounding drops columns), no vertical alignment,
       equal-height columns are hard, source order = visual order, hard to reorder responsively.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. FLOAT element को normal flow से (आंशिक रूप से) बाहर निकाल देता है:
     img { float: left; margin: 0 16px 8px 0; }
     - Element container के बाएँ किनारे पर जाता है
     - बाद के BLOCK elements उसे ignore करते हैं (नीचे से निकल जाते हैं)
     - बाद का text उसके चारों तरफ wrap हो जाता है
     - Float किया element सिकुड़कर content जितना हो जाता है, columns के लिए width दो

2. VALUES: left | right | none (default) | inline-start | inline-end

3. PARENT COLLAPSE की समस्या:
     अगर parent में सिर्फ floated children हों तो parent की height 0 हो जाती है,
     उसका background/border गायब दिखता है।

4. CLEAR:
     clear: left / right / both   -> पिछले floats के नीचे भेजता है (both सबसे ज़्यादा)

5. CLEARFIX (parent को ठीक करने के 3 तरीके):
     a) .clearfix::after { content: ""; display: table; clear: both; }
     b) parent पर overflow: auto/hidden (shadow या dropdown कट सकते हैं)
     c) आधुनिक: .parent { display: flow-root; }  <- सबसे साफ़ तरीका

6. shape-outside: float किए element के आकार (circle) के हिसाब से text wrap कराता है।

7. Flex/Grid के direct children पर float का कोई असर नहीं होता।

8. आज layout के लिए क्यों नहीं: clearfix चाहिए, widths नाज़ुक, vertical center मुश्किल,
   equal-height columns मुश्किल, responsive reorder मुश्किल।
```

---

## 🟡 Real World Example
**Newspaper-style articles, Medium, blogs, old Bootstrap:** A Hindustan Times or Medium article often shows a photo with its caption at the left or right and paragraph text flowing around it: that is `float`. An article pull-quote ("This changed everything") floated right inside the story is another typical case. Legacy sites built on Bootstrap 3 used `float: left` plus `width: 33.33%` for its grid (`.col-md-4`), and old WordPress themes still use `.alignleft` and `.alignright` classes that apply float to images placed in the editor. Today Amazon, Zomato and Gmail layouts are all Flexbox/Grid.

## 🟡 Real Example Hindi mein
**अखबार जैसे articles, Medium, blogs, पुराना Bootstrap:** Hindustan Times या Medium के article में अक्सर photo caption के साथ बाईं या दाईं तरफ होती है और paragraph उसके चारों ओर बहता है: ये `float` है। Article के अंदर दाईं तरफ pull-quote ("This changed everything") भी float का ही उदाहरण है। Bootstrap 3 की grid (`.col-md-4`) `float: left` + `width: 33.33%` पर चलती थी और पुराने WordPress themes में `.alignleft`/`.alignright` classes editor की images पर float लगाती हैं। आज Amazon, Zomato और Gmail के layouts Flexbox/Grid पर हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Float + Clear Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: Georgia, serif; line-height: 1.6; max-width: 720px; margin: 0 auto; padding: 24px; background: #fafafa; }
    h2 { font-family: system-ui, sans-serif; margin: 32px 0 10px; font-size: 1.1rem; border-bottom: 2px solid #333; }

    /* 1. TEXT WRAP AROUND AN IMAGE: the legit modern use of float */
    .photo {
      float: left;                      /* pull to the left, text flows on the right */
      width: 140px; height: 100px;
      margin: 4px 16px 8px 0;           /* space so the text doesn't touch the image */
      background: linear-gradient(135deg, #ff5a5f, #f5a623);
      border-radius: 8px;
    }

    /* 2. PULL QUOTE floated right */
    .pull {
      float: right; width: 200px; margin: 4px 0 8px 16px;
      padding: 10px; border-left: 4px solid #1a73e8; background: #e8f0fe;
      font: italic 1rem/1.4 Georgia, serif;
    }

    /* 3. THE COLLAPSED PARENT PROBLEM */
    .broken { border: 3px solid #e53935; background: #ffebee; }   /* parent with ONLY floated children */
    .box { float: left; width: 80px; height: 60px; margin: 6px; background: #e53935; }

    /* 4. FIX A: classic clearfix with a pseudo-element */
    .clearfix::after { content: ""; display: table; clear: both; }
    .fixed-a { border: 3px solid #fb8c00; background: #fff3e0; }
    .fixed-a .box { background: #fb8c00; }

    /* 5. FIX B: modern display: flow-root (no hacks, no clipping) */
    .fixed-b { display: flow-root; border: 3px solid #43a047; background: #e8f5e9; }
    .fixed-b .box { background: #43a047; }

    /* 6. LEGACY 3-COLUMN LAYOUT with float (for understanding only) */
    .cols { display: flow-root; background: #fff; border: 1px solid #ccc; }
    .col { float: left; width: 33.333%; padding: 12px; font-family: system-ui, sans-serif; font-size: 14px; }
    .col:nth-child(1) { background: #bbdefb; }
    .col:nth-child(2) { background: #c8e6c9; }
    .col:nth-child(3) { background: #ffe0b2; }

    /* 7. CLEAR: force the footer below all floats */
    .footer { clear: both; background: #333; color: #fff; padding: 8px 12px; margin-top: 8px; font-family: system-ui, sans-serif; }

    /* 8. shape-outside: text hugs the circle */
    .round {
      float: left; width: 130px; height: 130px; margin: 0 16px 8px 0;
      border-radius: 50%; background: radial-gradient(circle at 30% 30%, #fff, #8e24aa);
      shape-outside: circle(50%);        /* wrap follows the circle, not the square box */
    }
  </style>
</head>
<body>
  <h1 style="font-family:system-ui">CSS Float + Clear</h1>

  <h2>1-2. Text wrap with image and pull quote</h2>
  <div class="clearfix">
    <div class="photo"></div>
    <div class="pull">"Floats were meant for wrapping text, not for layout."</div>
    <p>Floated elements are taken out of the normal flow and shifted to the left or right edge of their container. Inline content such as this text flows around them. This is how newspaper-style articles place photographs next to the paragraphs. A margin on the floated box keeps the text from touching the image. Resize the window to see how the wrap changes, and notice that the paragraph keeps its natural flow while the image and quote stay at the sides.</p>
  </div>

  <h2>3. Collapsed parent (red): the parent has 0 content height</h2>
  <div class="broken"><div class="box"></div><div class="box"></div><div class="box"></div></div>
  <div style="clear:both"></div>

  <h2>4. Fixed with clearfix (orange)</h2>
  <div class="fixed-a clearfix"><div class="box"></div><div class="box"></div><div class="box"></div></div>

  <h2>5. Fixed with display: flow-root (green)</h2>
  <div class="fixed-b"><div class="box"></div><div class="box"></div><div class="box"></div></div>

  <h2>6. Legacy 3-column float layout</h2>
  <div class="cols">
    <div class="col">Column one. Each column is width 33.333% and floats left.</div>
    <div class="col">Column two. Heights are NOT equal, one reason floats lost to Flexbox.</div>
    <div class="col">Column three. The parent uses flow-root to contain the floats.</div>
  </div>
  <div class="footer">Footer with clear: both</div>

  <h2>8. shape-outside</h2>
  <div class="clearfix">
    <div class="round"></div>
    <p>With <code>shape-outside: circle(50%)</code> the text curves along the circular edge of the floated element instead of following its rectangular box. This only works on floated elements and needs a width and height. It is a small design flourish for editorial layouts and magazine-style pages.</p>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. In modern React apps, float is used mainly for rich-text/article content
//    (CMS HTML or Markdown output) where images should wrap text.

// Tailwind has float utilities: float-left, float-right, float-none, clear-both, clear-left,
// plus `flow-root` (the modern clearfix) and `after:` pseudo-element utilities
<article className="flow-root">                         {/* contains the floats, like a clearfix */}
  <img src="/photo.jpg" alt="Event" className="float-left mr-4 mb-2 h-28 w-40 rounded-lg object-cover" />
  <p>Article text wraps around the floated image...</p>
</article>

// 2. Tailwind Typography (prose) for CMS content: images inside `prose` can be floated
//    with custom classes: <img className="float-right ml-4" />

// 3. Legacy classes in a Next.js app that imports Bootstrap 3 CSS or WordPress content:
//    .alignleft { float: left; margin: 0 1em 1em 0; }
//    .alignright { float: right; margin: 0 0 1em 1em; }
//    .clearfix::after { content: ""; display: table; clear: both; }

// 4. Layout in React should use Flexbox/Grid
<div className="flex gap-4">   {/* NOT floats */}
  <Sidebar /><Main />
</div>

// 5. RTL / i18n: use logical values
//    float: inline-start  (Tailwind v3.3+: float-start / float-end)
<img className="float-start me-4" />
```

---

## ⚫ Interview Questions + Answers

**Q1: What does `float` do and what are the possible values?**
A1: `float` removes the element from normal block flow and shifts it to the left or right of its container, letting inline content (text) wrap around it. Values: `left`, `right`, `none` (default), `inline-start`, `inline-end`. The floated element's `display` computes to `block` and its width shrinks to fit the content unless set.

**Q2: What is the collapsed parent problem and how do you fix it (clearfix)?**
A2: A parent that contains only floated children has zero height because floats are out of flow, so its background and border wrap nothing. Fixes: (1) clearfix pseudo-element: `.clearfix::after { content: ""; display: table; clear: both; }`, (2) `overflow: auto/hidden` on the parent (can clip shadows), (3) modern and best: `display: flow-root` on the parent, which creates a block formatting context with no side effects.

**Q3: What does `clear` do, and what are its values?**
A3: `clear` prevents a block-level element from sitting beside earlier floats and pushes it below them. Values: `left`, `right`, `both`, `none`. `clear: both` is the most used, for footers below floated columns.

**Q4: Why was float replaced by Flexbox and Grid for layout? When is float still appropriate?**
A4: Float layouts need clearfix hacks, fragile percentage widths, have no vertical alignment, no equal-height columns, no easy reordering, and no gap. Flexbox/Grid solve all of these. Float is still the right tool for wrapping text around an image or pull quote (and with `shape-outside` for shaped wraps), because Flexbox/Grid cannot wrap text around items.

**Q5: Does `float` work on flex or grid items? And what is `shape-outside`?**
A5: No. `float` and `clear` are ignored on flex items and grid items (children of a flex/grid container). `shape-outside` defines the shape that inline content wraps around for a floated element, for example `shape-outside: circle(50%)` so text follows a round image's edge. It requires the element to be floated and have dimensions.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to contain floats (parent collapses)
```css
/* WRONG: parent has no height, next section overlaps the floats */
.row .col { float: left; width: 50%; }

/* CORRECT */
.row { display: flow-root; }       /* or .row::after { content:""; display:table; clear:both; } */
```

❌ **Mistake 2:** Using float to build page layout in a new project
```css
/* WRONG (legacy) */
.sidebar { float: left; width: 25%; } .main { float: left; width: 75%; }

/* CORRECT */
.layout { display: grid; grid-template-columns: 1fr 3fr; gap: 16px; }
```

❌ **Mistake 3:** Floating an item inside a flex container and expecting it to move
```css
/* WRONG: float is ignored on flex items */
.flex-parent { display: flex; } .flex-parent .a { float: right; }

/* CORRECT */
.flex-parent .a { margin-left: auto; }   /* pushes it to the right */
```

❌ **Mistake 4:** Using `clear` on the floated element itself, or on inline elements
```css
/* WRONG: clear only affects the element it is placed on (must be block-level) */
span.stop { clear: both; }

/* CORRECT */
div.stop { clear: both; }
```

❌ **Mistake 5:** No margin on the floated image
```css
/* CORRECT: give breathing room so text doesn't touch the image */
.photo { float: left; margin: 0 16px 8px 0; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| float | Push element left/right, text wraps | Element किनारे पर, text उसके चारों ओर |
| clear | Move below earlier floats | पिछले floats के नीचे जाना |
| clearfix | Hack to contain floats in the parent | Parent को floats समेटने देना |
| `display: flow-root` | Modern way to contain floats | आधुनिक clearfix |
| collapsed parent | Parent height 0 with only floated children | Parent की height 0 हो जाना |
| normal flow | Default top-to-bottom layout | सामान्य layout flow |
| BFC | Block formatting context, isolates floats | Floats को अलग रखने वाला context |
| shape-outside | Shaped text wrap for floats | आकार के हिसाब से text wrap |

---

## ⚡ 3-Line Summary
**English:**
1. `float: left/right` moves an element to a side so text wraps around it; `clear` pushes an element below earlier floats.
2. Floated children collapse their parent's height; fix with `display: flow-root` (modern) or the `::after` clearfix.
3. Use Flexbox/Grid for layout, and keep float only for text wrapping and `shape-outside`; it has no effect on flex/grid items.

**Hindi:**
1. `float: left/right` element को किनारे पर ले जाता है ताकि text लिपटे; `clear` element को पिछले floats के नीचे धकेलता है।
2. Floated children से parent की height collapse होती है; `display: flow-root` (आधुनिक) या `::after` clearfix से ठीक करो।
3. Layout के लिए Flexbox/Grid use करो, float सिर्फ text wrap और `shape-outside` के लिए रखो; flex/grid items पर इसका असर नहीं होता।

---

## ➡️ Next Topic
**87. CSS Calc() Function** — अब modern sizing: `calc(100% - 250px)` जैसे mixed units की गणना सीधे CSS में।
