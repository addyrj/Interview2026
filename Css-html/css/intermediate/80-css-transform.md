# 80. CSS Transform (translate, rotate, scale, skew)
# हिंदी में: CSS Transform — Element को हिलाना, घुमाना, बड़ा-छोटा करना

---

## 🔵 Simple Definition (English)
`transform` changes how an element is drawn: you can move it (`translate`), rotate it (`rotate`), resize it visually (`scale`), or slant it (`skew`) without changing the layout around it. It works on a copy of the element, so neighbours do not move.

## 🔵 सरल परिभाषा (Hindi)
`transform` element को दिखाने का तरीका बदलता है: उसे खिसका सकते हो (`translate`), घुमा सकते हो (`rotate`), visually बड़ा-छोटा कर सकते हो (`scale`) या तिरछा कर सकते हो (`skew`), और आसपास का layout नहीं बदलता। ये element की एक copy पर काम करता है, इसलिए पड़ोसी elements अपनी जगह रहते हैं।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Moving an element = change top/left/margin -> layout recalculates, other elements shift, janky
  - Rotating/scaling = images or JavaScript canvas tricks
  - Centering absolutely positioned items needed known width/height (negative margin hack)

AFTER:
  .modal { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }
  /* Centers regardless of size. Neighbours are untouched. Animates on the GPU. */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Element हिलाने के लिए top/left/margin बदलते थे, layout दोबारा calculate होता था, लोग lag महसूस करते थे
  - Rotate/scale के लिए image या JS चाहिए था
  - Centering के लिए width/height पता होनी चाहिए थी (negative margin hack)

अब:
  transform: translate(-50%, -50%) से किसी भी size का element center हो जाता है,
  और GPU पर smooth animate होता है।
```

---

## 🟢 How it Works — Step by Step

```
THE 2D FUNCTIONS:
  translate(x, y)   | translateX(20px) | translateY(-10px)   move (% is relative to the ELEMENT's own size)
  rotate(45deg)                                              turn clockwise (negative = anticlockwise); units: deg, turn, rad
  scale(1.2)        | scale(1.2, 0.8)  | scaleX() scaleY()   1 = normal, 2 = double, 0.5 = half
  skew(20deg, 0)    | skewX(20deg)     | skewY()             slant
  matrix(a,b,c,d,e,f)                                        all of the above in one (rarely hand-written)

3D (needs perspective):
  perspective(600px) on the transform, or `perspective: 600px` on the PARENT
  rotateX(), rotateY(), rotateZ(), translateZ(), scale3d()
  transform-style: preserve-3d   keeps children in 3D space
  backface-visibility: hidden    hides the back face (flip cards)

TRANSFORM-ORIGIN: the pivot point. Default is center (50% 50%).
  transform-origin: top left;  -> rotate pivots around the top-left corner.

ORDER MATTERS: functions apply right to left (like matrix multiplication).
  transform: translateX(100px) rotate(45deg);   /* rotate first, then move along the original x axis */
  transform: rotate(45deg) translateX(100px);   /* move along the rotated axis -> ends up diagonal */

INDIVIDUAL PROPERTIES (newer): translate, rotate, scale as separate properties
  translate: 10px 20px;  rotate: 45deg;  scale: 1.2;
  Support: Chrome 104+, Safari 14.1+, Firefox 72+. Handy because animating one
  does not overwrite the others.

KEY FACTS:
  - Does NOT affect layout: the element still occupies its original space.
  - Creates a new stacking context and a containing block for position: fixed children.
  - Only works on transformable elements: block-level and inline-block; plain inline <span> will NOT transform
    (set display: inline-block).
  - GPU-friendly: perfect for transitions and animations.
```

## 🟢 कैसे काम करता है? (Hindi)

```
2D functions:
  translate(x, y)   खिसकाओ (% का मतलब element की अपनी size का %)
  rotate(45deg)     घड़ी की दिशा में घुमाओ
  scale(1.2)        1 = जैसा है, 2 = दोगुना, 0.5 = आधा
  skew(20deg)       तिरछा करो

3D: parent पर `perspective: 600px`, फिर rotateX/rotateY; flip card के लिए
    transform-style: preserve-3d और backface-visibility: hidden.

transform-origin: घूमने का केंद्र बिंदु (default बीच में)।
  transform-origin: top left; = कोने के चारों ओर घूमेगा।

क्रम मायने रखता है: functions दाएँ से बाएँ apply होते हैं।
  translateX(100px) rotate(45deg)  और  rotate(45deg) translateX(100px)  अलग result देते हैं।

ज़रूरी बातें:
  - Layout पर असर नहीं: element की original जगह खाली नहीं होती।
  - Plain inline element (<span>) पर काम नहीं करता, inline-block करो।
  - GPU पर चलता है, इसलिए animations के लिए सबसे अच्छा।
```

---

## 🟡 Real World Example
**Amazon, Instagram, Swiggy:** Amazon's product image zooms when you hover (`transform: scale(1.1)` inside an `overflow: hidden` wrapper). Instagram's heart pops with a quick `scale(1.3)` animation. Swiggy's carousel arrows and the horizontal restaurant slider move with `translateX(-300px)`. Gmail's compose window and many chat widgets slide in from the bottom with `translateY(100%)` to `translateY(0)`. Flip cards on pricing pages use `rotateY(180deg)`.

## 🟡 Real Example Hindi mein
**Amazon, Instagram, Swiggy:** Amazon पर hover करने से product image zoom होती है (`transform: scale(1.1)` और बाहर `overflow: hidden` wrapper)। Instagram का heart like पर `scale(1.3)` से pop होता है। Swiggy के carousel और horizontal slider `translateX(-300px)` से खिसकते हैं। Chat widgets नीचे से `translateY(100%)` से `translateY(0)` तक slide होते हैं। Pricing page की flip cards `rotateY(180deg)` use करती हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Transform Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 24px; background: #f6f6f6; }
    h2 { margin: 32px 0 12px; }
    .row { display: flex; gap: 32px; flex-wrap: wrap; align-items: center; }

    /* Shared look for demo boxes */
    .box {
      width: 90px; height: 90px;
      background: #ff5a5f; color: #fff;
      display: grid; place-items: center;
      border-radius: 10px; font-weight: bold;
      transition: transform 0.4s ease;     /* smooth on hover */
    }

    /* 1. THE FOUR BASIC TRANSFORMS (hover each box) */
    .t-translate:hover { transform: translate(20px, -10px); }
    .t-rotate:hover    { transform: rotate(45deg); }
    .t-scale:hover     { transform: scale(1.3); }
    .t-skew:hover      { transform: skew(20deg, 5deg); }

    /* 2. TRANSFORM-ORIGIN: rotate around the top-left corner */
    .t-origin { transform-origin: top left; }
    .t-origin:hover { transform: rotate(30deg); }

    /* 3. ORDER MATTERS: same functions, different results */
    .order-a { transform: translateX(60px) rotate(45deg); background: #1a73e8; }
    .order-b { transform: rotate(45deg) translateX(60px); background: #34a853; }

    /* 4. IMAGE ZOOM on hover (Amazon style): wrapper clips the overflow */
    .zoom { width: 220px; height: 150px; overflow: hidden; border-radius: 12px; }
    .zoom div {
      width: 100%; height: 100%;
      background: linear-gradient(135deg, #f5a623, #ff5a5f);
      transition: transform 0.5s ease;
    }
    .zoom:hover div { transform: scale(1.15); }

    /* 5. CENTERING with translate (unknown size) */
    .stage { position: relative; width: 240px; height: 140px; background: #fff; border: 2px dashed #bbb; }
    .centered {
      position: absolute;
      top: 50%; left: 50%;                       /* moves top-left corner to center */
      transform: translate(-50%, -50%);          /* pull back by half own size */
      background: #333; color: #fff; padding: 8px 14px; border-radius: 8px;
    }

    /* 6. 3D FLIP CARD */
    .flip { width: 180px; height: 120px; perspective: 600px; }  /* perspective on the PARENT */
    .flip-inner {
      position: relative; width: 100%; height: 100%;
      transform-style: preserve-3d;              /* children keep their 3D position */
      transition: transform 0.7s;
    }
    .flip:hover .flip-inner { transform: rotateY(180deg); }
    .face {
      position: absolute; inset: 0;
      display: grid; place-items: center;
      border-radius: 12px; color: #fff; font-weight: bold;
      backface-visibility: hidden;               /* hide the back side of each face */
    }
    .front { background: #ff5a5f; }
    .back  { background: #1a73e8; transform: rotateY(180deg); }   /* pre-rotated so it faces out after flip */

    /* 7. INLINE ELEMENTS DO NOT TRANSFORM */
    .tag { display: inline-block; background: #ffe082; padding: 2px 8px; }  /* inline-block needed */
    .tag:hover { transform: rotate(-6deg); }

    @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
  </style>
</head>
<body>
  <h1>CSS Transform</h1>

  <h2>1. translate / rotate / scale / skew (hover)</h2>
  <div class="row">
    <div class="box t-translate">move</div>
    <div class="box t-rotate">rotate</div>
    <div class="box t-scale">scale</div>
    <div class="box t-skew">skew</div>
  </div>

  <h2>2. transform-origin: top left (hover)</h2>
  <div class="row"><div class="box t-origin">origin</div></div>

  <h2>3. Order matters (no hover, different results)</h2>
  <div class="row" style="height:160px">
    <div class="box order-a">A</div>
    <div class="box order-b">B</div>
  </div>

  <h2>4. Image zoom (hover)</h2>
  <div class="zoom"><div></div></div>

  <h2>5. Centering with translate(-50%, -50%)</h2>
  <div class="stage"><span class="centered">I am centered</span></div>

  <h2>6. 3D flip card (hover)</h2>
  <div class="flip">
    <div class="flip-inner">
      <div class="face front">Front</div>
      <div class="face back">Back</div>
    </div>
  </div>

  <h2>7. Inline needs inline-block</h2>
  <p>Hover the <span class="tag">tag</span> to tilt it.</p>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Hover zoom card with Tailwind (group lets the child react to parent hover)
<div className="overflow-hidden rounded-xl group">
  <img src="/pizza.jpg" alt="Pizza"
       className="transition-transform duration-500 group-hover:scale-110" />
</div>

// 2. Tailwind transform utilities: translate-x-4, -translate-y-1/2, rotate-45, scale-110, skew-x-6
//    (Tailwind v3+ applies transform automatically, no `transform` class needed)
<div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">Modal</div>

// 3. Dynamic transform in React: use inline style because the value is computed at runtime
function Carousel({ index, children }) {
  return (
    <div className="overflow-hidden">
      <div
        className="flex transition-transform duration-500"
        style={{ transform: `translateX(-${index * 100}%)` }}   // slide by index
      >
        {children}
      </div>
    </div>
  );
}

// 4. Next.js: keep transforms on compositor-friendly elements; pair with `will-change-transform`
//    only for long animations (Tailwind: will-change-transform).

// 5. Styled in a CSS Module:
// .card:hover { transform: translateY(-4px); }
```

---

## ⚫ Interview Questions + Answers

**Q1: What are the main 2D transform functions?**
A1: `translate(x, y)` moves, `rotate(angle)` turns around the origin, `scale(sx, sy)` resizes visually, `skew(ax, ay)` slants, and `matrix()` combines all. They are combined as a space-separated list in one `transform` declaration, for example `transform: translate(10px, 20px) rotate(10deg) scale(1.1)`.

**Q2: Why is `transform` better than `top`/`left`/`margin` for moving elements?**
A2: Transforms do not trigger layout; they change only how the element is painted/composited, so surrounding elements do not reflow and the browser can run the effect on the GPU. Changing `top/left` forces layout and paint on each frame, which can cause jank. The old position remains reserved in layout when using transform.

**Q3: Does the order of transform functions matter?**
A3: Yes. Transforms are applied right-to-left in terms of coordinate systems: each function changes the coordinate space for the next. `translateX(100px) rotate(45deg)` moves along the original x-axis then rotates in place at the new spot. `rotate(45deg) translateX(100px)` rotates the axes first, so the movement goes diagonally.

**Q4: What is `transform-origin`, and what is the default?**
A4: It is the fixed point around which rotate, scale and skew happen. The default is `50% 50%` (center). Setting `transform-origin: top left` makes a rotation swing around the top-left corner; for a dropdown that grows from its anchor, use `transform-origin: top`.

**Q5: How do you center an absolutely positioned element using transform? And what side effect does `transform` have?**
A5: Set `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);`. The percentages in `translate` refer to the element's own size, so no fixed width/height is needed. Side effects: a transform creates a new stacking context and becomes the containing block for `position: fixed` descendants, and it can blur text if it results in half-pixel positions. Modern alternatives: Flexbox/Grid `place-items: center`, or `inset: 0; margin: auto`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Writing two `transform` declarations and expecting them to merge
```css
/* WRONG: second line overrides the first, only scale applies */
.box { transform: rotate(45deg); transform: scale(1.2); }

/* CORRECT: one declaration, list all functions */
.box { transform: rotate(45deg) scale(1.2); }
```

❌ **Mistake 2:** Transforming an inline element
```css
/* WRONG: <span> is inline, transform is ignored */
span { transform: rotate(10deg); }

/* CORRECT */
span { display: inline-block; transform: rotate(10deg); }
```

❌ **Mistake 3:** Overwriting the base transform on hover
```css
/* WRONG: hover loses the centering translate, the element jumps */
.modal { transform: translate(-50%, -50%); }
.modal:hover { transform: scale(1.05); }

/* CORRECT: repeat the full chain (or use individual `scale:` property) */
.modal:hover { transform: translate(-50%, -50%) scale(1.05); }
```

❌ **Mistake 4:** Forgetting `perspective` for 3D, so `rotateY` looks flat
```css
/* CORRECT: set perspective on the parent (or inside transform) */
.flip { perspective: 600px; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| translate | Move along X/Y/Z | खिसकाना |
| rotate | Turn by an angle | घुमाना |
| scale | Visually enlarge/shrink | बड़ा-छोटा करना |
| skew | Slant along an axis | तिरछा करना |
| transform-origin | Pivot point of the transform | घूमने का केंद्र |
| perspective | Depth effect for 3D | 3D की गहराई |
| preserve-3d | Children stay in 3D space | Children 3D में रहें |
| stacking context | New z-index layer created by transform | नई z-index layer |

---

## ⚡ 3-Line Summary
**English:**
1. `transform` moves (`translate`), turns (`rotate`), resizes (`scale`), or slants (`skew`) an element without changing the layout around it.
2. Order matters, `transform-origin` sets the pivot, and it only works on non-inline elements.
3. It is GPU-friendly, so use it (with `opacity`) for transitions and animations instead of `top`/`left`/`width`.

**Hindi:**
1. `transform` element को खिसकाता (`translate`), घुमाता (`rotate`), बड़ा-छोटा (`scale`) या तिरछा (`skew`) करता है, आसपास का layout बदले बिना।
2. क्रम मायने रखता है, `transform-origin` pivot तय करता है, और ये inline elements पर काम नहीं करता।
3. ये GPU-friendly है, इसलिए animations में `top`/`left`/`width` की जगह `transform` (और `opacity`) use करो।

---

## ➡️ Next Topic
**81. CSS Shadows (box-shadow, text-shadow)** — Card lift effect (`translateY` + shadow) बनाने के लिए अब shadow की depth समझनी है।
