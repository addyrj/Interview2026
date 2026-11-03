# 62. Border + Border-radius
# हिंदी में: Border और Border-radius — किनारे की रेखा और गोल कोने

---

## 🔵 Simple Definition (English)
`border` draws a line around an element between its padding and margin, defined by **width, style and colour**. `border-radius` **rounds the corners** of that box, from slightly soft to a perfect circle or pill.

## 🔵 सरल परिभाषा (Hindi)
`border` element की padding और margin के बीच एक रेखा बनाता है, जो **width, style और colour** से तय होती है। `border-radius` उस box के **कोनों को गोल** करता है — हल्के गोल से लेकर पूरा circle या pill तक।

---

## 🔴 Problem it Solves
```
BEFORE (2000s):
  Rounded corners = 4 corner images + nested tables/divs + sprite images. Slow and fragile.
  Circle avatars = pre-cropped images.
  Borders: only table-based or image-based decoration.

NOW:
  .card   { border: 1px solid #e5e7eb; border-radius: 12px; }
  .avatar { width: 48px; height: 48px; border-radius: 50%; }   /* circle */
  .pill   { border-radius: 999px; }                             /* capsule */
  One line each, scales to any size, no images.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले गोल कोनों के लिए 4 corner images और nested divs/tables लगते थे — धीमा और नाज़ुक।
Circle avatar के लिए पहले से crop की हुई image चाहिए थी।

अब:
  border-radius: 12px   -> गोल कोने
  border-radius: 50%    -> circle (square box पर)
  border-radius: 999px  -> pill/capsule
हर size पर scale होता है, किसी image की ज़रूरत नहीं।
```

---

## 🟢 How it Works — Step by Step

```
BORDER
  border-width   1px | thin | medium | thick | 2px 4px (v h) | 1px 2px 3px 4px (top right bottom left)
  border-style   none (default!) | solid | dashed | dotted | double | groove | ridge | inset | outset
  border-color   any colour; default = currentColor
  SHORTHAND      border: 1px solid #ddd;     (style is REQUIRED, else no border is drawn)
  SIDES          border-top, border-right, border-bottom, border-left  (each also has -width/-style/-color)
  border-block / border-inline  logical versions (RTL friendly)

  - Border sits INSIDE the margin, OUTSIDE the padding; adds to size under content-box (topic 56).
  - Borders do not affect layout in outline: `outline` does NOT take space (topic below).
  - Where two sides meet, the corner is a diagonal join (that is how CSS triangles work, topic 116).

BORDER-RADIUS
  border-radius: 8px;                 all corners
  border-radius: 8px 0;               TL+BR = 8px, TR+BL = 0
  border-radius: 10px 20px 30px 40px; TL TR BR BL (clockwise from top-left)
  border-radius: 50%;                 circle if box is square, ellipse if not
  border-radius: 999px;               pill for any size (radii are clamped, never overlap)
  Elliptical: border-radius: 50px / 25px;   horizontal / vertical radius
  Longhands: border-top-left-radius ...
  - Also clips backgrounds AND (with overflow:hidden) child content like images.
  - Works on <img> directly: img { border-radius: 50% } (use object-fit: cover to avoid squishing).

BORDER vs OUTLINE vs BOX-SHADOW
  border      part of box model, takes space, follows border-radius
  outline     drawn OUTSIDE border, takes no space, follows border-radius in modern browsers;
              for focus rings; outline-offset moves it
  box-shadow  0 0 0 2px red = fake border that takes no space (good for focus/hover without layout shift)

BORDER-IMAGE (rare): border-image: linear-gradient(...) 1;  (does not combine with border-radius)
GRADIENT BORDER trick: background with two layers + background-clip (padding-box / border-box) + transparent border.
```

## 🟢 कैसे काम करता है? (Hindi)
```
BORDER
  तीन चीज़ें: width, style, color।  border: 1px solid #ddd;
  style न लिखो तो border दिखेगा ही नहीं (default style: none)।
  चारों तरफ: border-top / right / bottom / left अलग से भी।
  Border padding के बाहर और margin के अंदर होता है; content-box में size बढ़ाता है।

BORDER-RADIUS
  8px            -> चारों कोने
  8px 0          -> TL+BR = 8px, TR+BL = 0
  10px 20px 30px 40px -> TL TR BR BL (घड़ी की दिशा)
  50%            -> square पर पूरा circle
  999px          -> pill / capsule
  50px / 25px    -> अंडाकार कोना (horizontal / vertical)
  overflow: hidden के साथ अंदर की image भी गोल कट जाती है।

BORDER vs OUTLINE vs BOX-SHADOW
  border  -> space लेता है
  outline -> बाहर, space नहीं लेता, focus ring के लिए
  box-shadow: 0 0 0 2px red -> layout shift के बिना नकली border
```

---

## 🟡 Real World Example
**Instagram / Amazon / Swiggy:** Instagram's profile avatars are `border-radius: 50%` circles and the story ring is a gradient border. Swiggy and Zomato cards use `border-radius: 12-16px` with a `1px` light border, and filter chips ("Veg", "Rating 4.0+") are pills (`border-radius: 999px`). Amazon's "Add to cart" button has `border-radius: 8px/20px` and a darker bottom border. Gmail's compose button is a rounded rectangle; the selected inbox tab has a 3px bottom border in blue.

## 🟡 Real Example Hindi mein
**Instagram / Amazon / Swiggy:** Instagram के profile avatars `border-radius: 50%` वाले circle हैं और story का ring gradient border है। Swiggy/Zomato के cards में `border-radius: 12-16px` और हल्का `1px` border, और filter chips ("Veg", "Rating 4.0+") pill (`999px`) हैं। Amazon के "Add to cart" button के कोने गोल और नीचे गहरा border है। Gmail में selected tab के नीचे 3px नीला border होता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Border + Border-radius Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }
    h2 { font-size: 14px; margin: 24px 0 8px; color: #374151; }
    .row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    .box { width: 110px; height: 70px; background: #fff; display: grid; place-items: center; font-size: 12px; text-align: center; }

    /* 1. border styles (style is required!) */
    .solid  { border: 2px solid #2563eb; }
    .dashed { border: 2px dashed #16a34a; }
    .dotted { border: 3px dotted #dc2626; }
    .double { border: 6px double #7c3aed; }
    .nostyle { border: 2px #111; }            /* no style -> NO border is drawn */

    /* 2. per-side borders */
    .sides { border-top: 4px solid #f59e0b; border-bottom: 1px solid #d1d5db; }
    .tab   { border-bottom: 3px solid #2563eb; padding: 6px 12px; font-weight: 600; }

    /* 3. radius forms */
    .r8    { border: 1px solid #d1d5db; border-radius: 8px; }
    .r-mix { border: 1px solid #d1d5db; border-radius: 20px 0; }                /* TL+BR round */
    .r-4   { border: 1px solid #d1d5db; border-radius: 10px 20px 30px 40px; }  /* TL TR BR BL */
    .circle{ width: 80px; height: 80px; border-radius: 50%; background: #f59e0b; }
    .ellipse { border-radius: 50%; background: #34d399; }                        /* non-square -> ellipse */
    .leaf  { border-radius: 60px 0; background: #86efac; }
    .pill  { border: 1px solid #d1d5db; border-radius: 999px; padding: 6px 14px; width: auto; height: auto; }

    /* 4. avatar with image (object-fit stops squish) */
    .avatar { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 3px solid #fff; box-shadow: 0 0 0 2px #e11d48; }

    /* 5. card: radius + overflow hidden clips the child image corners */
    .card { width: 220px; border: 1px solid #e5e7eb; border-radius: 16px; overflow: hidden; background: #fff; }
    .card .pic { height: 90px; background: linear-gradient(135deg, #f43f5e, #f59e0b); }
    .card .body { padding: 10px; font-size: 13px; }

    /* 6. gradient border using two backgrounds */
    .grad-border {
      border: 3px solid transparent;
      border-radius: 14px;
      background:
        linear-gradient(#fff, #fff) padding-box,                       /* inside fill */
        linear-gradient(135deg, #f43f5e, #6366f1) border-box;          /* shows through the border */
      padding: 14px; width: 200px;
    }

    /* 7. outline vs border vs shadow ring: hover without layout shift */
    .btn { border: 0; padding: 10px 16px; border-radius: 8px; background: #2563eb; color: #fff; cursor: pointer; font: inherit; }
    .btn:hover { box-shadow: 0 0 0 3px rgb(37 99 235 / .35); }                 /* no layout shift */
    .btn:focus-visible { outline: 3px solid #f59e0b; outline-offset: 3px; }    /* accessible focus ring */
    .btn-bad { border: 0; padding: 10px 16px; background: #fff; border-radius: 8px; border: 1px solid #ccc; }
    .btn-bad:hover { border-width: 4px; }                                      /* box grows by 6px: layout jumps */

    /* 8. CSS triangle with borders (preview of topic 116) */
    .tri { width: 0; height: 0; border-left: 20px solid transparent; border-right: 20px solid transparent; border-bottom: 34px solid #e11d48; }
  </style>
</head>
<body>
  <h2>1. styles</h2>
  <div class="row">
    <div class="box solid">solid</div><div class="box dashed">dashed</div>
    <div class="box dotted">dotted</div><div class="box double">double</div>
    <div class="box nostyle">no style = no border</div>
  </div>

  <h2>2. sides</h2>
  <div class="row"><div class="box sides">top + bottom</div><div class="tab">Inbox (tab)</div></div>

  <h2>3. radius</h2>
  <div class="row">
    <div class="box r8">8px</div><div class="box r-mix">20px 0</div><div class="box r-4">10 20 30 40</div>
    <div class="circle"></div><div class="box ellipse">50% ellipse</div><div class="box leaf">60px 0</div>
    <span class="pill">Veg only</span> <span class="pill">Rating 4.0+</span>
  </div>

  <h2>4. avatar</h2>
  <div class="row"><img class="avatar" alt="avatar" src="https://picsum.photos/id/64/200/200"></div>

  <h2>5. card with clipped corners</h2>
  <div class="card"><div class="pic"></div><div class="body">Paradise Biryani<br>4.5 stars · 30 min</div></div>

  <h2>6. gradient border</h2>
  <div class="grad-border">Story ring style</div>

  <h2>7. hover without layout shift (left) vs with shift (right)</h2>
  <div class="row"><button class="btn">Good hover</button><button class="btn-bad">Bad hover</button></div>

  <h2>8. triangle</h2>
  <div class="tri"></div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind classes
<div className="border border-gray-200 rounded-xl overflow-hidden" />   {/* card */}
<img className="h-12 w-12 rounded-full object-cover" src={user.avatar} alt={user.name} />
<span className="rounded-full border px-3 py-1 text-sm">Veg only</span>   {/* pill */}
<div className="border-t-4 border-amber-500 border-dashed" />            {/* per-side + style */}
<button className="focus-visible:outline-2 focus-visible:outline-offset-2 hover:ring-4 ring-blue-500/30">Go</button>
//   rounded = 4px, rounded-md 6px, rounded-lg 8px, rounded-xl 12px, rounded-2xl 16px, rounded-full 9999px
//   Tailwind Preflight sets border-style: solid and 0 width by default, so `border` alone works.

// 2. Inline style, camelCase; numbers = px
<div style={{ border: "1px solid #e5e7eb", borderRadius: 12 }} />

// 3. next/image with rounded avatar: apply the radius via className and fixed size
import Image from "next/image";
<Image src={user.avatar} alt="" width={48} height={48} className="rounded-full" />

// 4. Design tokens: store radius in a CSS variable and reuse
//   :root { --radius: 12px }   .card { border-radius: var(--radius) }
```

---

## ⚫ Interview Questions + Answers

**Q1: Why is my `border: 2px red` not showing?**
A1: The `border-style` is missing. Its default is `none`, so width and colour are ignored. Use `border: 2px solid red`. (Tailwind and many resets set `border-style: solid` globally so only the width is needed.)

**Q2: How do you make a perfect circle and a pill?**
A2: Circle: a square element (`width = height`) with `border-radius: 50%`. Pill: any rectangle with a very large radius like `border-radius: 999px` (or `9999px`); the browser clamps the radius so corners never overlap. `50%` on a non-square box gives an ellipse.

**Q3: Border vs outline vs box-shadow: when would you use each?**
A3: `border` is part of the box model and takes space. `outline` is drawn outside the border, takes no space, ideal for focus rings (use `outline-offset`). `box-shadow: 0 0 0 2px colour` creates a ring that follows radius and doesn't change layout - great for hover/focus effects without layout shift or for multiple stacked rings.

**Q4: Why does `border-radius` not clip the image inside my card?**
A4: Child content paints over the parent's rounded corners. Add `overflow: hidden` to the parent (or put the radius on the image itself). With `position`/`transform` children, `overflow: hidden` plus the radius still clips in modern browsers.

**Q5: How do you create a CSS triangle, and how is a gradient border made?**
A5: Triangle: zero-size box where one side's border is coloured and the adjacent sides are `transparent`, e.g. `border-left/right: 20px solid transparent; border-bottom: 34px solid red`. Gradient border (radius-friendly): `border: 3px solid transparent; background: linear-gradient(#fff,#fff) padding-box, linear-gradient(...) border-box;`. `border-image` doesn't follow `border-radius`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting the border style
```css
/* WRONG: renders nothing */
.card { border: 1px #ddd; }

/* CORRECT */
.card { border: 1px solid #ddd; }
```

❌ **Mistake 2:** Layout jumps when adding a border on hover
```css
/* WRONG: element grows by 2px on hover */
.item { }  .item:hover { border: 1px solid blue; }

/* CORRECT: reserve space (transparent) or use box-shadow/outline */
.item { border: 1px solid transparent; }  .item:hover { border-color: blue; }
```

❌ **Mistake 3:** Circle from a non-square box
```css
/* WRONG: ellipse */
.avatar { width: 80px; height: 60px; border-radius: 50%; }

/* CORRECT */
.avatar { width: 80px; aspect-ratio: 1; border-radius: 50%; object-fit: cover; }
```

❌ **Mistake 4:** Removing the outline with no replacement
```css
/* WRONG */
button { outline: none; }

/* CORRECT */
button:focus-visible { outline: 3px solid #f59e0b; outline-offset: 2px; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| border | Line around padding box | किनारे की रेखा |
| border-style | solid, dashed, dotted... (default none) | रेखा का प्रकार |
| border-radius | Rounds corners | कोने गोल करना |
| Pill | Fully rounded rectangle (999px) | कैप्सूल आकार |
| outline | Non-layout ring outside border | Space न लेने वाली रेखा |
| box-shadow ring | `0 0 0 2px` fake border | Shadow से बनी रेखा |
| border-image | Image/gradient as border | Border की image |
| overflow: hidden | Clips children to rounded corners | बाहर का हिस्सा काटना |

---

## ⚡ 3-Line Summary
**English:**
1. `border: width style colour` (style is mandatory); sides can be set separately and the border adds to size under `content-box`.
2. `border-radius` rounds corners: `8px` soft, `50%` circle (square box), `999px` pill; add `overflow: hidden` to clip children.
3. For hover/focus effects use `outline` or `box-shadow` to avoid layout shift; Tailwind: `border`, `rounded-xl`, `rounded-full`.

**Hindi:**
1. `border: width style colour` (style ज़रूरी है); हर side अलग से और `content-box` में border size बढ़ाता है।
2. `border-radius`: `8px` हल्का गोल, `50%` circle (square box पर), `999px` pill; अंदर की चीज़ काटने के लिए `overflow: hidden`।
3. Hover/focus के लिए `outline` या `box-shadow` use करो ताकि layout न हिले; Tailwind: `border`, `rounded-xl`, `rounded-full`।

---

## ➡️ Next Topic
**63. CSS Display** — block, inline, inline-block, none — elements page में कैसे बैठते हैं और layout की नींव क्या है।
