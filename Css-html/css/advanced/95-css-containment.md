# 95. CSS Containment
# हिंदी में: CSS Containment — Browser को बताओ "ये हिस्सा अलग है"

---

## 🔵 Simple Definition (English)
CSS Containment (`contain` and `content-visibility`) lets you tell the browser that a part of the page is **independent**: its layout, paint, size or style will not affect the rest. The browser can then **skip work** for that subtree (for example, off-screen sections), making large pages faster.

## 🔵 सरल परिभाषा (Hindi)
CSS Containment (`contain` और `content-visibility`) से आप browser को बताते हैं कि page का एक हिस्सा **स्वतंत्र** है: उसका layout, paint, size या style बाकी page पर असर नहीं डालेगा। तब browser उस हिस्से का काम **छोड़ सकता है** (जैसे off-screen sections), और बड़े pages तेज़ हो जाते हैं।

---

## 🔴 Problem it Solves
```
WITHOUT CONTAINMENT:
  A page with 1,000 product cards.
  Change the text of ONE card → browser may re-check layout for a large part of the page,
  because it cannot be sure that card does not push other things around.
  Also: ALL 1,000 cards are laid out and painted at load, even though only 8 are on screen.
  → Slow first render (high Layout cost), slow updates, janky scroll.

WITH CONTAINMENT:
  .card { contain: layout paint; }                  /* "my insides do not leak out" */
  .card { content-visibility: auto; }               /* "skip me until I am near the viewport" */
  → Changes inside a card are limited to that card.
  → Off-screen cards cost almost nothing at load. Big win for long lists, feeds and dashboards.
```

## 🔴 यह क्यों बना? (Hindi)
Browser को पता नहीं होता कि एक element के अंदर की बदलाव बाहर तक असर डालेंगे या नहीं, इसलिए वो ज़्यादा हिस्से का layout दोबारा जाँचता है। और 1000 cards होने पर सब का layout/paint load पर ही हो जाता है, जबकि screen पर सिर्फ 8 दिखते हैं। Containment से ये फालतू काम बचता है।

---

## 🟢 How it Works — Step by Step

```
THE contain PROPERTY:
──────────────────────────────────────────────────────────
  contain: none | strict | content | size | layout | style | paint | inline-size

  layout      → element's internals do not affect outside layout, and outside layout
                does not affect inside. Also creates a new stacking context and a
                containing block for absolute/fixed children.
  paint       → descendants are NOT painted outside the element's box (like overflow: clip),
                so off-screen contents can be skipped. Also creates a containing block
                for fixed/absolute children and a stacking context.
  size        → element's size does NOT depend on its children (treats it as empty).
                YOU must give it a width AND height, or it collapses to 0.
  style       → counters/quotes scoped (rarely useful)
  inline-size → size containment in the inline direction only (the base of Container Queries)

  SHORTHANDS:
    contain: content  =  layout paint style      (safe default for widgets/cards)
    contain: strict   =  size layout paint style (needs explicit width/height)

THE content-visibility PROPERTY (the powerful one):
──────────────────────────────────────────────────────────
  content-visibility: visible   (default) → normal
  content-visibility: hidden    → content is NOT rendered (like display:none but the
                                   rendering state is cached → fast to show again)
  content-visibility: auto      → browser applies layout+paint+style containment, and
                                   SKIPS rendering when the element is off-screen.
                                   Rendered when it gets near the viewport.

  PROBLEM with auto: a skipped section has size 0 (size containment applies when
  skipped) → scrollbar jumps. SOLUTION:
    contain-intrinsic-size: auto 500px;    /* placeholder size; "auto" remembers the real size once rendered */

  Also: skipped content is still searchable (Ctrl+F), accessible to screen readers
  and focusable via find-in-page (it stays in the accessibility tree).

SUPPORT (be careful in interviews):
  contain: layout/paint/size/style → Chrome 52+, Firefox 69+, Safari 15.4+
  content-visibility: auto/hidden  → Chrome 85+, Edge 85+, Firefox 125+, Safari 18+
  contain-intrinsic-size           → same era as content-visibility
  → Safe to use as progressive enhancement: unsupported browsers just ignore it.

WHAT TO MEASURE: Chrome DevTools → Performance → "Rendering" time
  Web.dev case study: content-visibility: auto gave about 7x faster initial rendering on a long page.
```

## 🟢 कैसे काम करता है? (Hindi)
1. `contain: layout` — element के अंदर का layout बाहर को प्रभावित नहीं करता।
2. `contain: paint` — बच्चे element के box के बाहर paint नहीं होते (जैसे `overflow: clip`), तो off-screen हिस्सा skip हो सकता है।
3. `contain: size` — element का size बच्चों पर निर्भर नहीं; आपको width और height देनी होगी, नहीं तो 0 हो जाएगा।
4. `contain: content` = layout + paint + style (सुरक्षित shorthand)। `strict` = size भी।
5. `content-visibility: auto` — screen से बाहर वाले elements का rendering browser skip करता है और पास आने पर render करता है।
6. Skip होने पर size 0 हो जाता है, इसलिए `contain-intrinsic-size: auto 500px` से अंदाज़ा दो ताकि scrollbar कूदे नहीं।
7. Skipped content Ctrl+F और screen readers के लिए फिर भी उपलब्ध रहता है।

---

## 🟡 Real World Example
**Instagram / Twitter(X) / Swiggy feeds:** Hazaaron posts ya restaurant cards wali infinite list me har card par `contain: layout paint` aur lambi sections par `content-visibility: auto` use hota hai, taaki jo cards screen se bahar hain unka rendering skip ho jaye.
**Amazon product page:** Neeche ke "Customer reviews" aur "Related products" sections par `content-visibility: auto` laga kar first load ke time kharcha bachaya ja sakta hai.
**Gmail:** Har email row ek independent unit hai; ek row ka update poori list ka layout dobara nahi chalata.
**Third-party widgets (chat, ads):** `contain: layout paint` laga ke unke chhote-moti layout changes se baaki page ko bachate hain.

## 🟡 Real Example Hindi mein
**Instagram/X/Swiggy feeds:** हज़ारों posts या cards की list में हर card पर `contain: layout paint` और लंबे sections पर `content-visibility: auto` लगाते हैं ताकि screen से बाहर वाले cards का rendering skip हो।
**Amazon product page:** नीचे के "Customer reviews" और "Related products" sections पर `content-visibility: auto` से first load तेज़ होता है।
**Gmail:** हर email row independent है; एक row बदलने से पूरी list का layout दोबारा नहीं चलता।
**Third-party widgets:** `contain: layout paint` से उनके बदलाव बाकी page को नहीं छूते।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Containment Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
    h2 { margin: 20px 0 8px; font-size: 16px; border-bottom: 2px solid #333; padding-bottom: 4px; }

    /* ─── 1. contain: layout paint → independent widget ───────────── */
    .widget {
      contain: layout paint;          /* internals cannot leak outside the box */
      width: 260px; height: 100px;
      background: #fff; border: 2px solid #1976d2; border-radius: 8px;
      position: relative;
    }
    .widget .leak {
      position: absolute; left: 200px; top: 60px;     /* tries to stick OUT of the box */
      width: 120px; padding: 6px; background: #ffcdd2;
      /* because of contain: paint, the part outside .widget is CLIPPED */
    }

    /* ─── 2. contain: size → needs explicit size ──────────────────── */
    .fixed-box {
      contain: size;                  /* size no longer depends on children */
      width: 200px; height: 60px;     /* MUST set, otherwise it becomes 0 x 0 */
      background: #c8e6c9; overflow: hidden;
    }

    /* ─── 3. contain: content for each card in a list ─────────────── */
    .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
    .card {
      contain: content;               /* = layout + paint + style: safe shorthand */
      background: #fff; padding: 14px; border-radius: 10px; border: 1px solid #ddd;
    }

    /* ─── 4. content-visibility: auto → skip off-screen sections ─── */
    .section {
      content-visibility: auto;             /* render only when near the viewport */
      contain-intrinsic-size: auto 400px;   /* placeholder height; "auto" remembers real height */
      background: #fff; margin-bottom: 14px; padding: 16px; border-radius: 10px;
    }
    .section p { margin: 6px 0; color: #555; }

    /* ─── 5. content-visibility: hidden → cheap show/hide (cached) ── */
    .tab-panel[data-hidden="true"] { content-visibility: hidden; }  /* kept in memory but not rendered */
    .tab-panel { background: #fff3e0; padding: 10px; margin-top: 8px; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>CSS Containment</h1>

  <h2>1. contain: layout paint clips the red leak box</h2>
  <div class="widget">
    Widget content
    <div class="leak">I try to leave the widget</div>
  </div>

  <h2>2. contain: size (explicit width/height required)</h2>
  <div class="fixed-box">Size does not depend on me. Even long text will not grow this box because it is contained and overflow is hidden. Lorem ipsum dolor sit amet consectetur.</div>

  <h2>3. contain: content on cards</h2>
  <div class="card-grid" id="cards"></div>

  <h2>4. content-visibility: auto sections (scroll down; use DevTools Elements to inspect)</h2>
  <div id="sections"></div>

  <h2>5. content-visibility: hidden</h2>
  <button onclick="
    const p = document.getElementById('panel');
    /* toggle between rendered and not rendered; state is cached by the browser */
    p.setAttribute('data-hidden', p.getAttribute('data-hidden') === 'true' ? 'false' : 'true');
  ">Toggle panel</button>
  <div class="tab-panel" id="panel" data-hidden="false">Panel content (heavy UI could be here)</div>

  <script>
    // Generate demo content so the page is long
    const cards = document.getElementById('cards');
    for (let i = 1; i <= 8; i++) {
      cards.insertAdjacentHTML('beforeend', '<div class="card">Card ' + i + '<br><small>contain: content</small></div>');
    }
    const sections = document.getElementById('sections');
    for (let i = 1; i <= 30; i++) {
      sections.insertAdjacentHTML('beforeend',
        '<section class="section"><h3>Section ' + i + '</h3>' +
        '<p>Long review / related products content goes here. '.repeat(8) + '</p></section>');
    }
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Containment is plain CSS: put it in a CSS Module or global CSS.
/* Feed.module.css */
.post {
  content-visibility: auto;            /* skip rendering off-screen posts */
  contain-intrinsic-size: auto 480px;  /* estimated post height */
}
.widget { contain: layout paint; }

// 2. Tailwind (v3.3+/v4) arbitrary properties:
<article className="[content-visibility:auto] [contain-intrinsic-size:auto_480px]">
  {post.title}
</article>
// Newer Tailwind versions may include content-visibility utilities (check your version's docs).

// 3. React list with 1,000 items: choose between
//    a) content-visibility: auto  → simple, keeps all DOM nodes, works with Ctrl+F
//    b) virtualization (react-window, @tanstack/react-virtual) → removes DOM nodes
//       (better for 10,000+ items; breaks Ctrl+F)

// 4. Third-party embeds (ads, chat widget) wrapper:
export const Embed = ({ children }) => (
  <div style={{ contain: 'layout paint', width: 300, height: 250 }}>{children}</div>
);
// camelCase in the style object: contain, contentVisibility, containIntrinsicSize

// 5. Container Queries (topic 104) rely on containment internally:
//    container-type: inline-size  applies inline-size containment.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is CSS containment and why does it improve performance?**
A1: It lets you declare with `contain` or `content-visibility` that a subtree is independent of the rest of the page (layout, paint, size, style). The browser can then limit style recalculation, layout and painting to that subtree, and skip rendering of off-screen content. Result: faster initial render and cheaper updates on large pages.

**Q2: Explain the values of `contain`.**
A2: `layout`: inside layout and outside layout do not affect each other; `paint`: descendants are clipped to the box, can be skipped when off-screen; `size`: the element's size ignores its children (you must set size); `style`: counters and quotes scoped; `inline-size`: size containment only in the inline axis. `content` = layout + paint + style; `strict` = content + size.

**Q3: What is `content-visibility: auto` and what is the role of `contain-intrinsic-size`?**
A3: `auto` makes the browser skip layout and paint of an element while it is off-screen, rendering it when it nears the viewport. While skipped, the element behaves as if it has size containment, so its height would be 0 and the scrollbar jumps. `contain-intrinsic-size: auto 500px` gives a placeholder size (and `auto` remembers the last real size) to keep scroll stable.

**Q4: Side effects of `contain: layout` or `paint`?**
A4: They make the element a stacking context and a containing block for `position: absolute/fixed` descendants; `paint` clips descendants to the box (dropdowns, tooltips, or shadows that overflow will be cut off); `size` collapses the element unless width/height are set. Test overlays and popovers inside contained elements.

**Q5: `content-visibility: hidden` vs `display: none`?**
A5: Both stop the content from being displayed. `display: none` throws away the render state, so showing it again needs full re-rendering. `content-visibility: hidden` keeps the render state cached, so toggling back is much faster; it is good for tabs, virtual scrollers and off-screen UI. Unlike `visibility: hidden`, it also skips rendering work.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** `contain: size` or `strict` without dimensions
```css
/* WRONG: the box collapses to 0 x 0 */
.box { contain: strict; }

/* CORRECT */
.box { contain: strict; width: 300px; height: 200px; }
/* or use content */
.box { contain: content; }
```

❌ **Mistake 2:** `content-visibility: auto` without intrinsic size
```css
/* WRONG: scrollbar jumps as sections get rendered */
.section { content-visibility: auto; }

/* CORRECT */
.section { content-visibility: auto; contain-intrinsic-size: auto 600px; }
```

❌ **Mistake 3:** Containing elements that have dropdowns or tooltips
```css
/* WRONG: the dropdown is clipped by paint containment */
.navbar { contain: paint; }
.navbar .dropdown { position: absolute; top: 100%; }

/* CORRECT: do not contain parents of overflowing UI, or contain only inner cards */
```

❌ **Mistake 4:** Applying it to the above-the-fold hero
```css
/* WRONG: delays the very content that must show first */
.hero { content-visibility: auto; }

/* CORRECT: only below-the-fold sections */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| contain | Promise that a subtree is independent | "ये हिस्सा स्वतंत्र है" का वादा |
| layout containment | Inside layout does not affect outside | अंदर का layout बाहर असर नहीं डालता |
| paint containment | Clip painting to the box | Box के बाहर paint नहीं |
| size containment | Size ignores children | Size बच्चों पर निर्भर नहीं |
| content-visibility | Skip rendering of off-screen content | Off-screen का rendering skip |
| contain-intrinsic-size | Placeholder size when skipped | Skip होने पर अनुमानित size |
| Stacking context | Isolated z-index group | z-index का अलग समूह |
| Virtualization | Render only visible list items | सिर्फ दिखने वाले items render |

---

## ⚡ 3-Line Summary
**English:**
1. `contain` tells the browser a subtree is independent (layout, paint, size, style) so work stays local.
2. `content-visibility: auto` skips rendering off-screen sections; pair it with `contain-intrinsic-size` to avoid scroll jumps.
3. Watch side effects: clipping (paint), collapsing (size), new stacking context; support is good in modern browsers and safe as progressive enhancement.

**Hindi:**
1. `contain` से browser को पता चलता है कि हिस्सा स्वतंत्र है, इसलिए काम सिर्फ वहीं सीमित रहता है।
2. `content-visibility: auto` off-screen sections का rendering skip करता है; scroll कूदे नहीं इसलिए `contain-intrinsic-size` दो।
3. Side effects देखो: clipping (paint), collapse (size), नया stacking context; modern browsers में progressive enhancement की तरह सुरक्षित।

---

## ➡️ Next Topic
**96. CSS Will-change Property** — animation से पहले browser को hint देकर GPU layer बनवाना, और इसे कब नहीं करना चाहिए।
