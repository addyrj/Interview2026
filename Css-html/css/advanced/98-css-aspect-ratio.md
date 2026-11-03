# 98. CSS Aspect-ratio
# हिंदी में: CSS aspect-ratio — Width-Height का अनुपात fix करना

---

## 🔵 Simple Definition (English)
`aspect-ratio` sets the preferred **width : height ratio** of a box, for example `16 / 9` or `1 / 1`. When only one dimension is known (usually the width), the browser calculates the other, keeping the shape stable.

## 🔵 सरल परिभाषा (Hindi)
`aspect-ratio` box का **width : height अनुपात** तय करता है, जैसे `16 / 9` या `1 / 1`। जब सिर्फ एक dimension (आमतौर पर width) पता हो तो browser दूसरी खुद निकाल लेता है, और shape स्थिर रहती है।

---

## 🔴 Problem it Solves
```
BEFORE: the "padding-top hack" to keep a 16:9 video box
  .video-wrap { position: relative; height: 0; padding-top: 56.25%; }   /* 9/16 = 56.25% */
  .video-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; }
  → confusing math, extra wrapper, absolute positioning

ALSO: images without width/height → page JUMPS when they load (Layout Shift, bad CLS score).

NOW:
  .video { aspect-ratio: 16 / 9; width: 100%; }
  img   { aspect-ratio: 4 / 3; width: 100%; object-fit: cover; }
  → one line, no wrapper, no layout shift, responsive automatically.
```

## 🔴 यह क्यों बना? (Hindi)
पहले 16:9 box बनाने के लिए `padding-top: 56.25%` जैसा hack चलता था — math उलझा हुआ, extra wrapper और absolute positioning। Images load होते समय page कूदता था (CLS खराब)। अब एक line `aspect-ratio: 16 / 9` से सब हो जाता है।

---

## 🟢 How it Works — Step by Step

```
SYNTAX:
  aspect-ratio: 16 / 9;        /* width / height */
  aspect-ratio: 1;             /* same as 1 / 1 (square) */
  aspect-ratio: 4 / 3;
  aspect-ratio: auto;          /* default: natural ratio for images/video, none for divs */
  aspect-ratio: auto 16 / 9;   /* use the natural ratio if known, else fall back to 16/9
                                  (great for lazy images before they load) */

HOW THE BROWSER CALCULATES:
  - You give width: 400px  and aspect-ratio: 16/9  → height = 400 × 9/16 = 225px
  - You give height: 225px and aspect-ratio: 16/9  → width  = 400px
  - You give BOTH width and height → ratio is ignored (explicit sizes win)
  - You give NEITHER → block elements fill the width (auto) → height from ratio

IT IS A PREFERRED RATIO, NOT A STRICT ONE (for content overflow):
  - If content is bigger than the box (min-height: auto), the box GROWS to fit content,
    and the ratio is broken. Fix: min-height: 0; overflow: hidden (or hidden/auto).
  - For replaced elements (img, video): ratio is applied to the box; combine with
    object-fit: cover to crop instead of stretch.

COMMON RATIOS:
  1 / 1    square avatars, Instagram posts
  4 / 3    classic photos, Amazon product images
  3 / 2    DSLR photos, blog cards
  16 / 9   video, YouTube thumbnails, hero banners
  9 / 16   Stories, Reels, Shorts (vertical)
  21 / 9   cinematic banners

HTML width/height ATTRIBUTES (modern browsers):
  <img src="a.jpg" width="800" height="450" style="width:100%; height:auto">
  → browser maps the attributes to  aspect-ratio: 800 / 450  automatically → NO layout shift.
  So: always add width and height attributes on <img>.

GRID / FLEX:
  Items in a grid can use aspect-ratio to keep cards uniform: .tile { aspect-ratio: 1 }.
  In flex with align-items: stretch, an explicit stretched height overrides the ratio.

SUPPORT: Chrome 88+, Edge 88+, Firefox 89+, Safari 15+ (all modern browsers; 2021+).
Fallback for very old browsers: padding-top hack inside @supports not (aspect-ratio: 1).
```

## 🟢 कैसे काम करता है? (Hindi)
1. `aspect-ratio: 16 / 9` लिखो; width दो (या block में auto) → height = width × 9/16 अपने आप।
2. अगर आपने width **और** height दोनों दे दीं तो ratio ignore होता है।
3. ये "preferred" ratio है — content बड़ा हुआ तो box बढ़ जाएगा। इसे रोकने के लिए `min-height: 0` और `overflow: hidden`।
4. Image के साथ `object-fit: cover` लगाओ ताकि crop हो, stretch नहीं।
5. `aspect-ratio: auto 16 / 9` — image का natural ratio आने तक 16/9 रखो।
6. `<img>` पर `width` और `height` attributes हमेशा लिखो — browser खुद ratio बना लेता है और layout shift नहीं होता।
7. Support: सभी modern browsers (2021 से)।

---

## 🟡 Real World Example
**Instagram feed:** Har post tile `aspect-ratio: 1 / 1` (square grid on profile), Reels/Stories `9 / 16`.
**YouTube / Netflix:** Thumbnails `16 / 9`, har card ek jaisa dikhta hai chahe image ki original size kuch bhi ho.
**Amazon / Flipkart product listing:** Product image box `1 / 1` ya `4 / 3` taaki grid aligned rahe, `object-fit: contain` se image poori dikhe.
**Zomato / Swiggy restaurant card:** Hero image `16 / 10`; image load hone se pehle bhi card ki jagah reserve rehti hai (no jump).
**Embedded YouTube iframe in blogs:** `aspect-ratio: 16 / 9` replaces the old padding hack.

## 🟡 Real Example Hindi mein
**Instagram:** हर post tile `1 / 1` (profile की square grid), Reels/Stories `9 / 16`।
**YouTube/Netflix:** Thumbnails `16 / 9` — original image कोई भी size की हो, हर card एक जैसा दिखता है।
**Amazon/Flipkart:** Product image box `1 / 1` ताकि grid सीधी रहे।
**Zomato/Swiggy:** Restaurant image `16 / 10`; image load होने से पहले भी जगह reserve रहती है, page कूदता नहीं।
**Blog में YouTube iframe:** `aspect-ratio: 16 / 9` पुराने padding hack की जगह।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS aspect-ratio Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; color: #222; }
    h2 { margin: 26px 0 8px; font-size: 16px; border-bottom: 2px solid #333; padding-bottom: 4px; }

    /* ─── 1. VIDEO BOX: 16 / 9 (replaces padding-top hack) ────────── */
    .video {
      width: 100%; max-width: 480px;
      aspect-ratio: 16 / 9;                  /* height is calculated automatically */
      background: #111; color: #fff;
      display: grid; place-items: center; border-radius: 12px;
    }

    /* ─── 2. SQUARE GRID (Instagram profile) ──────────────────────── */
    .insta-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; max-width: 360px; }
    .insta-grid .tile {
      aspect-ratio: 1;                       /* 1 = 1 / 1 = square */
      background: linear-gradient(135deg, #f58529, #dd2a7b, #8134af);
      display: grid; place-items: center; color: #fff; font-weight: 700;
    }

    /* ─── 3. CARD IMAGES: same ratio, crop with object-fit ────────── */
    .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; max-width: 700px; }
    .card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.15); }
    .card img {
      display: block; width: 100%;
      aspect-ratio: 4 / 3;                   /* every image same shape */
      object-fit: cover;                     /* crop instead of stretching */
      background: #ddd;                      /* placeholder color while loading */
    }
    .card p { margin: 0; padding: 10px 12px; }

    /* ─── 4. auto + fallback ratio for lazy images ─────────────────── */
    .lazy { width: 100%; max-width: 320px; aspect-ratio: auto 3 / 2; background: #cfd8dc; }

    /* ─── 5. STORY / REEL: vertical 9 / 16 ────────────────────────── */
    .story {
      height: 260px;                         /* height given → width = 260 × 9/16 = 146px */
      aspect-ratio: 9 / 16;
      background: #232f3e; color: #fff; border-radius: 14px; display: grid; place-items: center;
    }

    /* ─── 6. RATIO CAN BREAK IF CONTENT IS BIGGER (and the fix) ───── */
    .breaks { width: 200px; aspect-ratio: 1; background: #ffcdd2; padding: 8px; }        /* grows with content */
    .fixed  { width: 200px; aspect-ratio: 1; background: #c8e6c9; padding: 8px;
              min-height: 0; overflow: hidden; }                                          /* stays square */

    /* ─── 7. OLD FALLBACK for browsers without support (very rare) ── */
    @supports not (aspect-ratio: 1) {
      .video { height: 0; padding-top: 56.25%; }
    }
  </style>
</head>
<body>
  <h1>aspect-ratio</h1>

  <h2>1. 16 / 9 video box</h2>
  <div class="video">16 / 9</div>

  <h2>2. Square grid 1 / 1</h2>
  <div class="insta-grid">
    <div class="tile">1</div><div class="tile">2</div><div class="tile">3</div>
    <div class="tile">4</div><div class="tile">5</div><div class="tile">6</div>
  </div>

  <h2>3. Cards with images 4 / 3 (different source sizes)</h2>
  <div class="cards">
    <!-- width/height attributes also give the browser the ratio before load -->
    <div class="card"><img src="https://picsum.photos/id/1015/800/400" width="800" height="400" alt="River valley"><p>Wide image</p></div>
    <div class="card"><img src="https://picsum.photos/id/1025/300/500" width="300" height="500" alt="Dog"><p>Tall image</p></div>
    <div class="card"><img src="https://picsum.photos/id/1035/600/600" width="600" height="600" alt="Waterfall"><p>Square image</p></div>
  </div>

  <h2>4. auto 3 / 2 (fallback before load)</h2>
  <img class="lazy" alt="" loading="lazy" src="https://picsum.photos/id/1040/600/400">

  <h2>5. Vertical story 9 / 16</h2>
  <div class="story">9 / 16</div>

  <h2>6. Content bigger than ratio: red grows, green stays square</h2>
  <div style="display:flex; gap:16px; align-items:flex-start;">
    <div class="breaks">This text is too long for a 200px square, so the box grows taller than wide. Lorem ipsum dolor sit amet consectetur adipiscing.</div>
    <div class="fixed">This text is too long for a 200px square but the box stays square with min-height: 0 and overflow hidden. Lorem ipsum dolor sit amet.</div>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind utilities:
//    aspect-square  → aspect-ratio: 1 / 1
//    aspect-video   → aspect-ratio: 16 / 9
//    aspect-[4/3]   → arbitrary ratio
<div className="aspect-video w-full overflow-hidden rounded-xl bg-black">
  <iframe className="h-full w-full" src="https://www.youtube.com/embed/..." allowFullScreen />
</div>

<img className="aspect-[4/3] w-full object-cover" src={p.image} alt={p.name} />

// 2. next/image: give width and height (prevents layout shift), or use "fill"
//    inside a container that has aspect-ratio:
import Image from 'next/image';
<div className="relative aspect-[4/3] w-full">
  <Image src={product.image} alt={product.name} fill sizes="(max-width: 768px) 100vw, 33vw"
         className="object-cover" />
</div>
// "fill" images need a positioned parent that has a size → aspect-ratio gives it one.

// 3. CSS Modules:
/* Card.module.css */
.thumb { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }

// 4. Inline style in React (camelCase; string value):
<div style={{ aspectRatio: '16 / 9' }} />
<div style={{ aspectRatio: 1 }} />     // number works for ratio 1

// 5. Skeleton loaders keep the layout stable while data loads:
<div className="aspect-[4/3] animate-pulse bg-gray-200 rounded-xl" />
```

---

## ⚫ Interview Questions + Answers

**Q1: What does `aspect-ratio` do and why was it introduced?**
A1: It sets a preferred width-to-height ratio so the browser can compute one dimension from the other. It replaced the `padding-top` percentage hack, makes responsive media boxes easy, and reserves space before images/videos load, which prevents layout shift (CLS).

**Q2: What happens if you set `width`, `height`, and `aspect-ratio` together?**
A2: Explicit width and height win, and the ratio is ignored, because there is nothing left to compute. The ratio is only used when at least one dimension is `auto`. For stretch layouts (flex `align-items: stretch`, grid) the stretched size can also override it.

**Q3: How do you stop content from breaking the ratio?**
A3: `aspect-ratio` is a preferred ratio: with `min-height: auto` the box grows if content is taller. Set `min-height: 0` and `overflow: hidden` (or `auto`) to force the ratio, or make the content scale. For images use `object-fit: cover` so they fill without distortion.

**Q4: How do you avoid layout shift with images?**
A4: Add `width` and `height` attributes in the HTML (browsers use them to compute an intrinsic aspect ratio) with CSS `img { max-width: 100%; height: auto; }`, or set `aspect-ratio` in CSS. With Next.js `<Image>`, provide `width`/`height` or use `fill` in a container with `aspect-ratio`.

**Q5: What does `aspect-ratio: auto 16 / 9` mean?**
A5: Use the element's natural ratio when it has one (an image once loaded); until then (or for elements with no natural ratio) use 16/9. It is helpful for lazy-loaded images and embeds, because the box has the right shape before the content arrives and then adapts to the real ratio.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using the old padding hack in new code
```css
/* WRONG */
.box { height: 0; padding-top: 56.25%; position: relative; }

/* CORRECT */
.box { aspect-ratio: 16 / 9; }
```

❌ **Mistake 2:** Writing the ratio backwards or with a colon
```css
/* WRONG: colon is invalid */
.box { aspect-ratio: 16:9; }

/* CORRECT: slash, width / height */
.box { aspect-ratio: 16 / 9; }
```

❌ **Mistake 3:** Stretching images instead of cropping
```css
/* WRONG: image distorted to fit a 1/1 box */
img { aspect-ratio: 1; width: 100%; height: 100%; }

/* CORRECT */
img { aspect-ratio: 1; width: 100%; object-fit: cover; }
```

❌ **Mistake 4:** Giving fixed height as well
```css
/* WRONG: ratio is silently ignored */
.thumb { width: 300px; height: 300px; aspect-ratio: 16 / 9; }

/* CORRECT: omit height */
.thumb { width: 300px; aspect-ratio: 16 / 9; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| aspect-ratio | Preferred width / height ratio | Width/height का अनुपात |
| Padding hack | Old percentage padding trick | पुराना padding वाला तरीका |
| CLS | Cumulative Layout Shift | Page का अचानक हिलना |
| object-fit | How media fills its box | Media box में कैसे भरे |
| Intrinsic ratio | Natural ratio of an image/video | Image का अपना अनुपात |
| Replaced element | img, video, iframe, canvas | बाहरी content वाले elements |
| Layout shift | Content moving after load | Load के बाद जगह बदलना |
| min-height: auto | Default; lets content enlarge box | Content से box बड़ा हो सकता है |

---

## ⚡ 3-Line Summary
**English:**
1. `aspect-ratio: 16 / 9` computes height from width (or width from height), replacing the padding-top hack.
2. It is a preferred ratio: explicit width + height override it, and big content can enlarge the box unless `min-height: 0; overflow: hidden`.
3. Pair with `object-fit: cover`, add `width`/`height` on images, and use Tailwind `aspect-video` / `aspect-square` to avoid layout shift.

**Hindi:**
1. `aspect-ratio: 16 / 9` width से height निकालता है — padding-top hack की ज़रूरत नहीं।
2. ये preferred ratio है: width + height दोनों दे दीं तो ignore; बड़ा content box बढ़ा देगा जब तक `min-height: 0; overflow: hidden` न हो।
3. `object-fit: cover` के साथ use करो, images पर `width`/`height` दो, Tailwind में `aspect-video`/`aspect-square`।

---

## ➡️ Next Topic
**99. CSS Logical Properties** — left/right की जगह inline-start/inline-end — RTL भाषाओं (Arabic, Urdu) में layout अपने आप सही।
