# 85. CSS Clip-path
# हिंदी में: CSS Clip-path — Element को किसी भी Shape में काटना

---

## 🔵 Simple Definition (English)
`clip-path` cuts an element into a shape. Only the part inside the shape is visible; everything outside is hidden (and also stops receiving clicks). Shapes can be `circle()`, `ellipse()`, `inset()`, `polygon()`, `path()` or a reference to an SVG `<clipPath>` with `url(#id)`.

## 🔵 सरल परिभाषा (Hindi)
`clip-path` element को किसी shape में काट देता है। Shape के अंदर का हिस्सा दिखता है, बाहर का छिप जाता है (और वहाँ click भी नहीं पहुँचता)। Shapes: `circle()`, `ellipse()`, `inset()`, `polygon()`, `path()` या SVG `<clipPath>` का `url(#id)`।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Non-rectangular shapes = cropped PNGs / SVG exports / extra wrapper hacks
  - Triangles used the border trick (topic 116), diagonals used rotated pseudo-elements
  - Hexagon avatars, arrow buttons, slanted hero sections = lots of fragile CSS

AFTER:
  .hero    { clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%); }     /* slanted bottom */
  .avatar  { clip-path: circle(50%); }                                 /* circle crop */
  /* Percentages scale with the element, so it's responsive */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Rectangle से अलग shape के लिए PNG crop या SVG export
  - Triangle के लिए border trick, तिरछे banner के लिए rotate किए हुए pseudo-elements
  - Hexagon avatar या arrow button बनाना बहुत नाज़ुक CSS था

अब:
  clip-path: polygon(...) से कोई भी shape, और percentages होने से responsive भी।
```

---

## 🟢 How it Works — Step by Step

```
BASIC SHAPES:
  circle(radius at x y)           circle(50% at 50% 50%)    50% radius = circle on a square
  ellipse(rx ry at x y)           ellipse(50% 35% at 50% 50%)
  inset(top right bottom left round radius)    inset(10px 20px round 12px)    rectangle crop with rounded corners
  polygon(x1 y1, x2 y2, ...)      polygon(50% 0, 100% 100%, 0 100%)           triangle
  path('M0 0 L100 0 ...')         SVG path syntax in px (not responsive)

COORDINATES: measured from the element's top-left of the reference box (default border-box).
  0% 0% = top-left, 100% 0% = top-right, 100% 100% = bottom-right, 0% 100% = bottom-left.

POLYGON RECIPES (all percentages):
  Triangle   polygon(50% 0, 100% 100%, 0 100%)
  Diamond    polygon(50% 0, 100% 50%, 50% 100%, 0 50%)
  Trapezoid  polygon(20% 0, 80% 0, 100% 100%, 0 100%)
  Hexagon    polygon(25% 5%, 75% 5%, 100% 50%, 75% 95%, 25% 95%, 0 50%)
  Arrow/tag  polygon(0 0, 85% 0, 100% 50%, 85% 100%, 0 100%)
  Slant      polygon(0 0, 100% 0, 100% 85%, 0 100%)

ANIMATION / TRANSITION:
  You can transition between two clip-paths IF both use the SAME shape function with
  the SAME number of points. e.g. polygon(...) with 4 points to polygon(...) with 4 points.
  Reveal effects: clip-path: inset(0 100% 0 0) -> inset(0 0 0 0)

REFERENCE BOX: clip-path: circle(50%) border-box;  (default). Others: padding-box, content-box, margin-box.

SIDE EFFECTS:
  - Clipped area is NOT clickable/hoverable. The element's hit-testing follows the shape.
  - It clips box-shadow, outline and borders that fall outside. Use filter: drop-shadow() on a PARENT.
  - Creates a stacking context.
  - Not responsive when you use `path()` (fixed px) or polygon with px values.

SUPPORT: basic shapes are in all modern browsers (Chrome 55+, Firefox 54+, Safari 9.1+ with -webkit- prefix in older versions).

Related: `mask-image` (soft edges / gradients / images). clip-path = hard edge, mask = soft edge.
Tool tip: Clippy (bennettfeely.com/clippy) generates polygons visually.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Basic shapes:
  circle(50% at 50% 50%)                   गोला
  ellipse(50% 35% at 50% 50%)              अंडाकार
  inset(10px 20px round 12px)              rectangle crop
  polygon(x1 y1, x2 y2, ...)               कोई भी बहुभुज
  path('M0 0 ...')                         SVG path (px में, responsive नहीं)

Coordinates: element के top-left से नापे जाते हैं।
  0% 0% = ऊपर-बाएँ, 100% 0% = ऊपर-दाएँ, 100% 100% = नीचे-दाएँ, 0% 100% = नीचे-बाएँ।

Recipes:
  Triangle   polygon(50% 0, 100% 100%, 0 100%)
  Diamond    polygon(50% 0, 100% 50%, 50% 100%, 0 50%)
  Slant      polygon(0 0, 100% 0, 100% 85%, 0 100%)

Animation: दो clip-paths तभी animate होते हैं जब दोनों में एक ही function और एक जितने points हों।
  Reveal effect: inset(0 100% 0 0) से inset(0 0 0 0)

ज़रूरी: कटा हुआ हिस्सा click नहीं लेता; box-shadow भी कट जाती है (parent पर drop-shadow लगाओ)।
clip-path = कड़ा किनारा, mask-image = नरम किनारा।
```

---

## 🟡 Real World Example
**Landing pages, Instagram, Swiggy:** Many SaaS landing pages and Stripe-style heroes end with a slanted bottom edge made by `polygon(0 0, 100% 0, 100% 90%, 0 100%)`. Instagram-style hexagon or circle avatars and the story ring crop use `circle(50%)`. Swiggy/Zomato-style offer tags ("50% OFF") use an arrow or ribbon polygon. Portfolio sites reveal images on scroll by animating `clip-path: inset(0 0 100% 0)` to `inset(0)`.

## 🟡 Real Example Hindi mein
**Landing pages, Instagram, Swiggy:** कई SaaS landing pages का hero नीचे से तिरछा कटा होता है: `polygon(0 0, 100% 0, 100% 90%, 0 100%)`। Hexagon या circle avatar `circle(50%)` से बनते हैं। Swiggy/Zomato के "50% OFF" offer tags arrow या ribbon polygon होते हैं। Portfolio sites में scroll पर image का reveal `clip-path: inset(0 0 100% 0)` से `inset(0)` तक animate करके बनता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS clip-path Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 24px; background: #f7f7f7; }
    h2 { margin: 28px 0 10px; }
    .row { display: flex; gap: 18px; flex-wrap: wrap; align-items: center; }

    /* Base coloured block for the shape demos */
    .shape {
      width: 120px; height: 120px;
      background: linear-gradient(135deg, #ff5a5f, #f5a623);
      display: grid; place-items: center; color: #fff; font-size: 12px; font-weight: bold;
    }

    /* 1. BASIC SHAPES */
    .circle   { clip-path: circle(50%); }
    .ellipse  { clip-path: ellipse(50% 35%); }
    .inset    { clip-path: inset(10px 20px round 16px); }   /* top/bottom 10, left/right 20, rounded */

    /* 2. POLYGON RECIPES */
    .triangle { clip-path: polygon(50% 0, 100% 100%, 0 100%); }
    .diamond  { clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); }
    .hexagon  { clip-path: polygon(25% 5%, 75% 5%, 100% 50%, 75% 95%, 25% 95%, 0 50%); }
    .arrow    { clip-path: polygon(0 0, 75% 0, 100% 50%, 75% 100%, 0 100%); }
    .star     { clip-path: polygon(50% 0, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%); }

    /* 3. SLANTED HERO: responsive because the cut uses percentages */
    .hero {
      height: 180px; color: #fff; padding: 24px;
      background: linear-gradient(120deg, #1a73e8, #6a11cb);
      clip-path: polygon(0 0, 100% 0, 100% 80%, 0 100%);   /* bottom edge slants up to the right */
    }
    .hero h3 { margin: 0; font-size: 1.6rem; }

    /* 4. HOVER REVEAL: same function + same point count so it can transition */
    .reveal {
      width: 200px; height: 120px; background: linear-gradient(135deg, #34a853, #1a73e8);
      clip-path: inset(0 100% 0 0);                 /* fully hidden from the right */
      transition: clip-path .6s ease;
    }
    .reveal-wrap { width: 200px; height: 120px; border: 2px dashed #bbb; }
    .reveal-wrap:hover .reveal { clip-path: inset(0 0 0 0); }   /* fully visible */

    /* 5. TRANSITION BETWEEN POLYGONS (4 points each) */
    .morph {
      width: 120px; height: 120px; background: #e91e63;
      clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);      /* square */
      transition: clip-path .5s;
    }
    .morph:hover { clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); }  /* diamond */

    /* 6. SHADOW: clip-path cuts box-shadow, so apply drop-shadow on the PARENT */
    .shadow-wrap { filter: drop-shadow(0 8px 8px rgba(0,0,0,.4)); }

    /* 7. Clipped area is not clickable */
    .click { cursor: pointer; }
  </style>
</head>
<body>
  <h1>CSS clip-path</h1>

  <h2>1. Basic shapes</h2>
  <div class="row">
    <div class="shape circle">circle</div>
    <div class="shape ellipse">ellipse</div>
    <div class="shape inset">inset</div>
  </div>

  <h2>2. Polygons</h2>
  <div class="row">
    <div class="shape triangle">triangle</div>
    <div class="shape diamond">diamond</div>
    <div class="shape hexagon">hexagon</div>
    <div class="shape arrow">arrow</div>
    <div class="shape star">star</div>
  </div>

  <h2>3. Slanted hero</h2>
  <div class="hero"><h3>Free delivery this week</h3></div>

  <h2>4. Hover to reveal (inset)</h2>
  <div class="reveal-wrap"><div class="reveal"></div></div>

  <h2>5. Hover to morph square to diamond</h2>
  <div class="morph"></div>

  <h2>6. Shadow on a clipped shape (via parent filter)</h2>
  <div class="shadow-wrap" style="width:fit-content">
    <div class="shape hexagon click" onclick="alert('Clicked inside the hexagon')">click me</div>
  </div>
  <p style="font-size:13px;color:#666">Clicks in the clipped-away corners do nothing.</p>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind has no clip-path utilities in core (v3): use arbitrary properties
//    Spaces become underscores inside [].
<div className="h-40 bg-indigo-600 [clip-path:polygon(0_0,100%_0,100%_80%,0_100%)]" />
<img src="/me.jpg" alt="Me" className="h-24 w-24 object-cover [clip-path:circle(50%)]" />
// (Plain `rounded-full` is simpler for circles; use clip-path for polygons.)

// 2. CSS Modules / global CSS for reuse
/* Hero.module.css */
/* .slant { clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%); } */

// 3. Scroll reveal with state: toggle between two inset() values
function RevealImage({ src, alt }) {
  const [shown, setShown] = React.useState(false);
  return (
    <img
      src={src} alt={alt}
      onLoad={() => setShown(true)}
      style={{
        clipPath: shown ? 'inset(0 0 0 0)' : 'inset(0 100% 0 0)',   // camelCase in React
        transition: 'clip-path 0.8s ease',
      }}
    />
  );
}

// 4. Next.js <Image> works with clip-path via className/style on the Image itself.
//    Shadow trick still needs the wrapper: <div className="drop-shadow-lg"> ... </div>
//    (Tailwind drop-shadow-lg is filter: drop-shadow)

// 5. Framer Motion can animate clipPath strings if point counts match.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is `clip-path` and which shape functions does it support?**
A1: `clip-path` defines a visible region for an element; everything outside is hidden. Functions: `circle()`, `ellipse()`, `inset()`, `polygon()`, `path()`, and `url(#svgClipPath)` to reference an SVG clipPath. Percentages are relative to the reference box (border-box by default), so shapes are responsive.

**Q2: How is `clip-path` different from `overflow: hidden` and `border-radius`?**
A2: `overflow: hidden` clips children to the element's rectangular padding box; it does not clip the element itself. `border-radius` rounds only corners. `clip-path` clips the element and its children to any arbitrary shape, including polygons. Also, clip-path does not affect layout: the element's box still occupies its original rectangle.

**Q3: What happens to clicks and shadows on the clipped-away area?**
A3: The clipped area does not receive pointer events (hover and click follow the shape). Box-shadows, outlines and borders that fall outside the shape are clipped too. To get a shadow, wrap the element in a parent and apply `filter: drop-shadow()` to the parent.

**Q4: Can you animate `clip-path`? Any limitations?**
A4: Yes, you can transition or animate it when both states use the same basic shape function with the same number of points (e.g. two 4-point `polygon()`s or two `inset()`s). Different functions or point counts will switch instantly instead. Common uses are reveal animations with `inset()` and morphs between polygons.

**Q5: When would you pick `clip-path` vs `mask-image` vs an SVG?**
A5: `clip-path`: hard-edged geometric shapes (polygon slants, hexagon, circle), cheap and simple. `mask-image`: soft or partial transparency (gradient fades, image-shaped cutouts); needs `-webkit-` prefix in some browsers. SVG clipPath/inline SVG: complex organic shapes or when you also need strokes and animation control. `path()` in clip-path uses fixed px values, so it will not scale responsively; use SVG with `clipPathUnits="objectBoundingBox"` for scalable curved shapes.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `box-shadow` on a clipped element
```css
/* WRONG: shadow is clipped away completely */
.tag { clip-path: polygon(0 0, 85% 0, 100% 50%, 85% 100%, 0 100%); box-shadow: 0 4px 8px #000; }

/* CORRECT: parent gets a drop-shadow filter */
.tag-wrap { filter: drop-shadow(0 4px 6px rgba(0,0,0,.4)); }
```

❌ **Mistake 2:** Mixing different shape functions or point counts in a transition
```css
/* WRONG: no smooth animation (switches instantly) */
.a { clip-path: circle(50%); transition: clip-path .4s; }
.a:hover { clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%); }

/* CORRECT: same function, same number of points */
.b { clip-path: inset(0 round 50%); transition: clip-path .4s; }
.b:hover { clip-path: inset(0 round 0); }
```

❌ **Mistake 3:** Using px in `polygon()` / `path()` and expecting responsiveness
```css
/* WRONG: breaks when the element resizes */
.hero { clip-path: polygon(0 0, 1200px 0, 1200px 300px, 0 400px); }

/* CORRECT */
.hero { clip-path: polygon(0 0, 100% 0, 100% 75%, 0 100%); }
```

❌ **Mistake 4:** Forgetting that clipped parts can still be focusable or hidden content
```css
/* CORRECT: keep interactive controls inside the visible shape, and don't clip away focus outlines */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| clip-path | Region of the element that stays visible | Element का दिखने वाला हिस्सा |
| polygon() | Shape from a list of points | Points से बनी बहुभुज shape |
| inset() | Rectangular crop with optional rounding | Rectangle crop |
| circle() | Circular crop | गोल crop |
| reference box | Box that percentages refer to | Percentage किस box के हिसाब से |
| drop-shadow | Filter shadow that follows shape | Shape वाली shadow |
| mask-image | Soft-edged alternative to clip-path | नरम किनारे वाला विकल्प |
| hit-testing | Where clicks are detected | Click कहाँ पहुँचता है |

---

## ⚡ 3-Line Summary
**English:**
1. `clip-path` hides everything outside a shape (`circle()`, `inset()`, `polygon()`, `path()`), without changing layout.
2. Use percentages for responsive shapes, and apply `filter: drop-shadow()` on a parent because box-shadow gets clipped.
3. It can be animated only between the same shape type with the same number of points; clipped areas do not get clicks.

**Hindi:**
1. `clip-path` shape (`circle()`, `inset()`, `polygon()`, `path()`) के बाहर सब छिपा देता है, layout नहीं बदलता।
2. Responsive shapes के लिए percentages use करो, और box-shadow कट जाती है इसलिए parent पर `filter: drop-shadow()` लगाओ।
3. केवल एक ही shape type और बराबर points के बीच animate होता है; कटे हुए हिस्से पर click नहीं जाता।

---

## ➡️ Next Topic
**86. CSS Float + Clear (legacy)** — Modern layout (Flexbox/Grid) से पहले का तरीका; interview में अब भी पूछा जाता है, खासकर "clearfix" और text wrap के लिए।
