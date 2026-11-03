# 81. CSS Shadows (box-shadow, text-shadow)
# हिंदी में: CSS Shadows — Depth और Glow बनाना

---

## 🔵 Simple Definition (English)
`box-shadow` draws a shadow behind an element's box, and `text-shadow` draws one behind text. Both take `offset-x offset-y blur [spread] colour`. Shadows give depth (cards that float), focus rings, glows, and even inner bevels with `inset`. They never affect layout.

## 🔵 सरल परिभाषा (Hindi)
`box-shadow` element के box के पीछे shadow बनाता है और `text-shadow` text के पीछे। दोनों में `offset-x offset-y blur [spread] colour` लिखते हैं। Shadow से depth (तैरते हुए cards), focus ring, glow और `inset` से अंदर की shadow बनती है। Shadow layout पर कोई असर नहीं डालती।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Depth effect = background images (PNG shadows), extra wrapper divs
  - Cannot resize or recolour image shadows, breaks on rounded corners
  - Highlighting focus = changing border width, which shifts layout

AFTER:
  .card { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
  /* Follows border-radius, scalable, no extra markup, doesn't take layout space */
  .input:focus { box-shadow: 0 0 0 3px rgba(26,115,232,.4); }   /* ring without layout shift */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Depth के लिए PNG shadow images और extra divs लगाने पड़ते थे
  - Rounded corners पर टूट जाती थीं, colour/size नहीं बदल सकते थे
  - Focus दिखाने के लिए border मोटा करते थे, layout हिल जाता था

अब:
  box-shadow border-radius को follow करती है, extra markup नहीं, layout में जगह नहीं लेती।
```

---

## 🟢 How it Works — Step by Step

```
box-shadow SYNTAX:
  box-shadow: [inset] offset-x offset-y [blur] [spread] colour;

  offset-x   +right / -left
  offset-y   +down  / -up
  blur       0 = sharp edge, larger = softer (cannot be negative)
  spread     grows (+) or shrinks (-) the shadow size before blur
  colour     usually rgba() so the shadow stays soft; defaults to currentcolor
  inset      shadow drawn INSIDE the border box

  Example:  box-shadow: 0 4px 12px 0 rgba(0,0,0,0.15);

MULTIPLE SHADOWS: comma separated, first is on top.
  box-shadow: 0 1px 2px rgba(0,0,0,.1), 0 8px 24px rgba(0,0,0,.15);
  Layered shadows look more natural (small tight one + large soft one).

TRICKS:
  Focus ring (no layout shift):  box-shadow: 0 0 0 3px #1a73e8;
  Fake border:                   box-shadow: 0 0 0 1px #ddd;
  Glow:                          box-shadow: 0 0 20px #ff5a5f;
  Neumorphism:                   light shadow top-left + dark shadow bottom-right
  Only one side:                 box-shadow: 0 6px 6px -6px rgba(0,0,0,.4); (negative spread)

text-shadow SYNTAX:
  text-shadow: offset-x offset-y blur colour;   (NO spread, NO inset)
  Used for readability on images, glow, and outline effects.

drop-shadow() (a FILTER, topic 83):
  filter: drop-shadow(0 4px 6px rgba(0,0,0,.3));
  Follows the actual shape (transparent PNG, SVG), whereas box-shadow follows the rectangular box.

PERFORMANCE:
  Large blur radii on many elements are costly to paint. Animating box-shadow repaints every frame.
  Tip: put the big shadow on a ::after pseudo-element and animate its opacity instead.

DARK MODE: black shadows barely show on dark backgrounds, use lighter borders or subtle glows.
```

## 🟢 कैसे काम करता है? (Hindi)

```
box-shadow: [inset] offset-x offset-y [blur] [spread] colour;

  offset-x   + दाएँ / - बाएँ
  offset-y   + नीचे / - ऊपर
  blur       0 = तेज़ किनारा, ज़्यादा = softer
  spread     shadow को फैलाता (+) या सिकोड़ता (-) है
  colour     rgba() use करो ताकि shadow soft रहे
  inset      shadow box के अंदर बनती है

कई shadows: comma से अलग करो; पहली सबसे ऊपर। दो layers (छोटी + बड़ी soft) ज़्यादा natural दिखती हैं।

Tricks:
  Focus ring बिना layout shift: box-shadow: 0 0 0 3px #1a73e8;
  Glow: box-shadow: 0 0 20px #ff5a5f;

text-shadow: offset-x offset-y blur colour (spread और inset नहीं होते)।
  Image के ऊपर text पढ़ने लायक बनाने में काम आता है।

drop-shadow() एक filter है जो असली shape (transparent PNG/SVG) को follow करता है;
box-shadow rectangle को follow करती है।

Performance: बड़ी blur वाली shadow को animate करना महंगा है; ::after पर रखकर उसकी opacity animate करो।
```

---

## 🟡 Real World Example
**Amazon, Zomato, Gmail:** Zomato restaurant cards sit on a light grey page with a faint `0 2px 8px rgba(0,0,0,.08)` shadow; on hover the shadow grows to show lift. Gmail's compose button has a Material-style layered shadow, and the search bar gains a shadow when focused. Hero banners with text over photos (Swiggy, Netflix style) use `text-shadow: 0 2px 4px rgba(0,0,0,.6)` so white text stays readable. Form inputs on Google sign-in use a blue focus glow ring.

## 🟡 Real Example Hindi mein
**Amazon, Zomato, Gmail:** Zomato के restaurant cards हल्के grey page पर हल्की `0 2px 8px rgba(0,0,0,.08)` shadow के साथ होते हैं; hover पर shadow बढ़ती है जिससे card ऊपर उठा दिखता है। Gmail के compose button पर Material style की layered shadow है और search bar focus पर shadow लेता है। Photo के ऊपर सफेद text (Swiggy/Netflix hero) पढ़ने के लिए `text-shadow: 0 2px 4px rgba(0,0,0,.6)` लगाते हैं। Google sign-in के input पर blue focus glow ring होती है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Shadows Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 24px; background: #f0f2f5; }
    h2 { margin: 32px 0 12px; }
    .row { display: flex; gap: 28px; flex-wrap: wrap; }

    .box {
      width: 150px; height: 90px; background: #fff;
      border-radius: 12px; display: grid; place-items: center;
      font-size: 14px; text-align: center; padding: 8px;
    }

    /* 1. ELEVATION SCALE: bigger offset + blur = higher */
    .e1 { box-shadow: 0 1px 3px rgba(0,0,0,.12); }
    .e2 { box-shadow: 0 4px 12px rgba(0,0,0,.15); }
    .e3 { box-shadow: 0 12px 32px rgba(0,0,0,.20); }

    /* 2. LAYERED shadow: tight + soft = more natural */
    .layered {
      box-shadow:
        0 1px 2px rgba(0,0,0,.10),      /* tight contact shadow */
        0 8px 24px rgba(0,0,0,.14);     /* wide soft ambient shadow */
    }

    /* 3. HOVER LIFT using ::after so only opacity animates (cheap) */
    .lift { position: relative; transition: transform .25s; }
    .lift::after {
      content: ""; position: absolute; inset: 0; border-radius: inherit;
      box-shadow: 0 14px 30px rgba(0,0,0,.25);
      opacity: 0; transition: opacity .25s; z-index: -1;   /* behind the box */
    }
    .lift:hover { transform: translateY(-4px); }
    .lift:hover::after { opacity: 1; }

    /* 4. INSET: pressed / input look */
    .inset { box-shadow: inset 0 2px 6px rgba(0,0,0,.25); background: #e8e8e8; }

    /* 5. FOCUS RING with spread = 0 blur (no layout shift) */
    .input {
      padding: 10px 12px; border: 1px solid #ccc; border-radius: 8px;
      font-size: 1rem; outline: none; transition: box-shadow .2s, border-color .2s;
    }
    .input:focus { border-color: #1a73e8; box-shadow: 0 0 0 3px rgba(26,115,232,.35); }

    /* 6. GLOW */
    .glow { background: #111; color: #fff; box-shadow: 0 0 24px 4px rgba(255,90,95,.7); }

    /* 7. ONE-SIDE shadow using negative spread */
    .one-side { box-shadow: 0 10px 8px -8px rgba(0,0,0,.45); }

    /* 8. TEXT-SHADOW */
    .hero {
      height: 140px; border-radius: 12px; display: grid; place-items: center;
      background: linear-gradient(135deg, #f7971e, #ffd200);
    }
    .hero h3 {
      margin: 0; color: #fff; font-size: 2rem;
      text-shadow: 0 2px 4px rgba(0,0,0,.45);        /* readable on light backgrounds */
    }
    .neon {
      background: #0b0b17; color: #fff; padding: 14px 20px; border-radius: 10px;
      font-size: 1.8rem; font-weight: bold;
      text-shadow: 0 0 6px #0ff, 0 0 14px #0ff, 0 0 28px #08f;   /* multiple = glow */
    }

    /* 9. drop-shadow follows the shape; box-shadow follows the rectangle */
    .shape {
      width: 90px; height: 90px; background: #ff5a5f;
      clip-path: polygon(50% 0, 100% 100%, 0 100%);   /* triangle */
    }
    .shape-wrap { filter: drop-shadow(0 6px 6px rgba(0,0,0,.4)); }  /* put filter on the PARENT: clip-path cuts shadows */
  </style>
</head>
<body>
  <h1>CSS Shadows</h1>

  <h2>1. Elevation levels</h2>
  <div class="row">
    <div class="box e1">elevation 1</div>
    <div class="box e2">elevation 2</div>
    <div class="box e3">elevation 3</div>
  </div>

  <h2>2. Layered / 3. Hover lift / 4. Inset</h2>
  <div class="row">
    <div class="box layered">layered</div>
    <div class="box lift e1">hover me</div>
    <div class="box inset">inset</div>
  </div>

  <h2>5. Focus ring</h2>
  <input class="input" placeholder="Click to focus">

  <h2>6. Glow / 7. One side</h2>
  <div class="row">
    <div class="box glow">glow</div>
    <div class="box one-side">bottom only</div>
  </div>

  <h2>8. Text shadow</h2>
  <div class="hero"><h3>Biryani Fest</h3></div>
  <p class="neon">NEON</p>

  <h2>9. drop-shadow on a non-rectangular shape</h2>
  <div class="shape-wrap"><div class="shape"></div></div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind shadow utilities: shadow-sm, shadow, shadow-md, shadow-lg, shadow-xl, shadow-2xl, shadow-inner, shadow-none
<div className="rounded-xl bg-white p-4 shadow-md transition-shadow hover:shadow-xl">Card</div>

// 2. Coloured / arbitrary shadows
<button className="shadow-lg shadow-rose-500/40">Order</button>             {/* coloured shadow, Tailwind v3+ */}
<div className="shadow-[0_8px_24px_rgba(0,0,0,0.15)]">Custom</div>          {/* arbitrary value */}

// 3. Focus ring: Tailwind `ring` utilities are box-shadow under the hood
<input className="focus:outline-none focus:ring-2 focus:ring-blue-500" />

// 4. text-shadow has no default Tailwind v3 utility: use arbitrary property or plugin
<h1 className="text-white [text-shadow:0_2px_4px_rgba(0,0,0,.5)]">Title</h1>

// 5. Design tokens: store the shadow scale as CSS variables (see topic 77)
// :root { --shadow-md: 0 4px 12px rgba(0,0,0,.15); }
// .card { box-shadow: var(--shadow-md); }

// 6. Dark mode in Tailwind: dark:shadow-none dark:ring-1 dark:ring-white/10
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain the box-shadow syntax.**
A1: `box-shadow: [inset] offset-x offset-y blur spread colour`. Offsets move the shadow, `blur` softens the edge (no negatives), `spread` grows or shrinks it, `colour` is its colour, and `inset` draws it inside. Offset-x and offset-y are required. Multiple shadows are separated by commas.

**Q2: How do you add multiple shadows, and which one is on top?**
A2: Separate them with commas. The first shadow in the list is painted on top. Layering a small, tight shadow with a large, soft one gives a more realistic depth, as in Material Design elevation.

**Q3: What is the difference between `box-shadow` and `filter: drop-shadow()`?**
A3: `box-shadow` follows the element's rectangular border box (including border-radius) and can use `spread` and `inset`. `drop-shadow()` follows the actual rendered alpha shape, such as a transparent PNG, SVG or text with transparency, so the shadow hugs the shape. `drop-shadow` has no spread or inset. Also, `clip-path` clips box-shadow away, so for clipped shapes apply `drop-shadow` on a parent.

**Q4: How can you create a focus ring or border without shifting layout?**
A4: Use `box-shadow: 0 0 0 3px colour` (zero offsets and blur, positive spread). Shadows do not take space in the layout, while changing `border-width` would resize the element. Using `outline` with `outline-offset` also avoids layout shift and is better for accessibility because it shows in forced-colors mode; box-shadow rings disappear in Windows high contrast mode, so keep a transparent outline as backup.

**Q5: Are shadows expensive, and how do you animate them efficiently?**
A5: Yes: shadows with large blur are costly to paint, and animating `box-shadow` forces a repaint every frame. A cheaper pattern is to render the target shadow on a pseudo-element and animate its `opacity` (and `transform` on the element). Also limit the number of heavily shadowed elements on one screen, especially long lists.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using solid black shadows
```css
/* WRONG: heavy, dirty look */
.card { box-shadow: 0 4px 10px #000; }

/* CORRECT: low-opacity rgba, ideally tinted to the background */
.card { box-shadow: 0 4px 12px rgba(0,0,0,.12); }
```

❌ **Mistake 2:** Expecting `box-shadow` to follow a clipped or transparent shape
```css
/* WRONG: shadow is cut off by clip-path */
.star { clip-path: polygon(...); box-shadow: 0 4px 8px #000; }

/* CORRECT: filter on a wrapper */
.star-wrap { filter: drop-shadow(0 4px 8px rgba(0,0,0,.4)); }
```

❌ **Mistake 3:** Shadow hidden by a parent with `overflow: hidden`
```css
/* WRONG: card's shadow is clipped at the parent's edge */
.list { overflow: hidden; }

/* CORRECT: add padding to the parent so the shadow has room, or remove overflow hidden */
.list { padding: 24px; }
```

❌ **Mistake 4:** Using `text-shadow` with a spread value
```css
/* WRONG: text-shadow does not support spread, declaration is invalid */
h1 { text-shadow: 0 0 4px 2px red; }

/* CORRECT */
h1 { text-shadow: 0 0 4px red; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| box-shadow | Shadow around the element box | Box के आसपास की shadow |
| text-shadow | Shadow behind text | Text के पीछे की shadow |
| offset | Horizontal/vertical shift of shadow | Shadow का खिसकाव |
| blur | Softness of the edge | किनारे की नरमी |
| spread | Grows/shrinks the shadow size | Shadow का फैलाव |
| inset | Shadow drawn inside the box | अंदर वाली shadow |
| elevation | Perceived height above the page | Page से ऊँचाई का एहसास |
| drop-shadow() | Filter that follows alpha shape | Shape को follow करने वाली shadow |

---

## ⚡ 3-Line Summary
**English:**
1. `box-shadow: offset-x offset-y blur spread colour` (plus `inset`) adds depth, focus rings and glows without affecting layout.
2. Use low-opacity `rgba` and layer two shadows for natural depth; `text-shadow` has no spread or inset.
3. Large animated shadows are costly, so animate a pseudo-element's opacity; use `drop-shadow()` for non-rectangular shapes.

**Hindi:**
1. `box-shadow: offset-x offset-y blur spread colour` (और `inset`) layout बदले बिना depth, focus ring और glow देता है।
2. कम opacity की `rgba` use करो और दो shadows layer करो; `text-shadow` में spread और inset नहीं होते।
3. बड़ी animated shadows महंगी हैं, इसलिए pseudo-element की opacity animate करो; non-rectangular shapes के लिए `drop-shadow()` use करो।

---

## ➡️ Next Topic
**82. CSS Gradients (linear, radial)** — Shadows के बाद अब backgrounds में colour blends: buttons, hero banners और skeleton loaders वही gradients से बनते हैं।
