# 61. Background Properties
# हिंदी में: Background Properties — रंग, Image, Gradient और उनकी Position

---

## 🔵 Simple Definition (English)
Background properties paint the area **behind an element's content** (inside its border box by default). They set a colour, one or more images or gradients, and control the image's **size, position, repeat, attachment and clipping**.

## 🔵 सरल परिभाषा (Hindi)
Background properties element के content के **पीछे** का हिस्सा रंगती हैं (default में border box तक)। इनसे रंग, एक या ज़्यादा image/gradient लगते हैं, और image का **size, position, repeat, attachment और clip** control होता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  - Decorative images added with <img> pollute HTML and hurt accessibility (alt text noise).
  - Text over a photo is unreadable.
  - Image smaller than the box tiles (repeats) by default.
  - Need a hero banner that always covers its area on any screen size.

SOLUTION:
  .hero {
    background: linear-gradient(rgb(0 0 0 / .5), rgb(0 0 0 / .5)),  /* dark overlay on top */
                url(hero.jpg) center / cover no-repeat;              /* picture below */
  }
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  - सजावटी images के लिए <img> लगाने से HTML गंदा होता है।
  - Photo के ऊपर text पढ़ने में नहीं आता।
  - छोटी image default में बार-बार repeat होती है।
  - हर screen size पर पूरा cover करने वाला hero banner चाहिए।

हल: background-image + overlay gradient + background-size: cover।
```

---

## 🟢 How it Works — Step by Step

```
LONGHANDS
  background-color       #fff | rgb() | transparent (default)
  background-image       url("a.jpg") | linear-gradient(...) | radial-gradient(...) | none
                         multiple layers separated by comma; FIRST is on TOP
  background-repeat      repeat (default) | no-repeat | repeat-x | repeat-y | space | round
  background-position    center | top left | 50% 20% | 10px 30px
  background-size        auto (default) | cover | contain | 100% | 200px 100px
         cover   = scale to FILL the box, may crop the image
         contain = scale to FIT fully inside, may leave empty space
  background-attachment  scroll (default) | fixed (parallax-like) | local
         (fixed is janky/unsupported on iOS Safari - avoid on mobile)
  background-origin      where position 0 0 starts: padding-box (default) | border-box | content-box
  background-clip        how far paint extends: border-box (default) | padding-box | content-box | text
         text trick: background-clip: text + transparent colour = gradient text
                     (needs -webkit-background-clip: text in some browsers)
  background-blend-mode  multiply | overlay ... blends layers

SHORTHAND ORDER (any order mostly, but position/size need a slash)
  background: [color] [image] [position / size] [repeat] [attachment] [origin] [clip];
  background: #111 url(a.jpg) center / cover no-repeat;
  NOTE: the shorthand RESETS every omitted sub-property to its default.
  Put background-color LAST among layers: background: url(a.jpg), linear-gradient(..), #fff;  (colour only in final layer)

PAINT ORDER (bottom -> top)
  background-color  ->  last image layer ... first image layer  ->  border  ->  content

PERFORMANCE
  Use compressed WebP/AVIF; add a background-color placeholder while image loads.
  CSS backgrounds are not lazy-loaded and not in the HTML: for meaningful/LCP images prefer <img>/<picture>/next/image.
```

## 🟢 कैसे काम करता है? (Hindi)
```
background-color    रंग
background-image    url() या gradient; कई layers comma से, पहली layer सबसे ऊपर
background-repeat   repeat (default) | no-repeat
background-position center | top left | 50% 20%
background-size     cover  -> पूरा भर दो (कट सकती है)
                    contain -> पूरी दिखे (खाली जगह बच सकती है)
background-attachment fixed -> scroll पर स्थिर (mobile पर avoid)
background-clip     border-box | padding-box | content-box | text (gradient text)

Shorthand: background: #111 url(a.jpg) center / cover no-repeat;
   (position और size के बीच slash /)
   Shorthand में जो न लिखो वो default पर reset हो जाता है।
   Multiple layers में colour सिर्फ आखिरी layer में लिखो।

Meaningful image (product photo) के लिए <img> use करो, सजावट के लिए background।
```

---

## 🟡 Real World Example
**Zomato / Amazon / Instagram:** Zomato's hero search area is a food photo with a dark gradient overlay (`linear-gradient + url() cover`) so the white text is readable. Amazon's category tiles use `background-size: cover` so differently shaped photos fill identical boxes. Instagram's gradient story ring and gradient "Follow" text use `background-clip: text`. Dashboard cards use `background: #fff` with subtle `radial-gradient` accents. Pattern backgrounds (dots, stripes) are created with repeating gradients, no image file needed.

## 🟡 Real Example Hindi mein
**Zomato / Amazon / Instagram:** Zomato के hero में food की photo पर गहरा gradient overlay होता है (`linear-gradient + url() cover`) ताकि सफेद text पढ़ा जा सके। Amazon के category tiles में `background-size: cover` है इसलिए अलग-अलग shape की photos एक जैसे box भर देती हैं। Instagram के gradient वाले text में `background-clip: text` use होता है। Dots/stripes जैसे patterns repeating gradient से बनते हैं, image file के बिना।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Background Properties Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 20px; background: #f3f4f6; }
    h2 { font-size: 14px; margin: 22px 0 6px; color: #374151; }
    .tile { height: 140px; border-radius: 8px; color: #fff; padding: 10px; font-weight: 700; text-shadow: 0 1px 3px rgba(0,0,0,.6); }

    /* Using a public sample image: if offline, the colour fallback below still shows */
    :root { --img: url("https://picsum.photos/id/1080/800/500"); }

    /* 1. color + repeat default vs no-repeat (small SVG tile as data URI) */
    .t-repeat {
      background-color: #fde68a;                                            /* fallback colour */
      background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><circle cx='10' cy='10' r='4' fill='%23f59e0b'/></svg>");
      background-repeat: repeat;                                            /* tiles dots everywhere */
      color: #111; text-shadow: none;
    }

    /* 2. cover vs contain */
    .t-cover   { background: #1f2937 var(--img) center / cover no-repeat; }    /* fills, may crop */
    .t-contain { background: #1f2937 var(--img) center / contain no-repeat; }  /* fits, may leave bars */

    /* 3. position */
    .t-pos { background: #1f2937 var(--img) right bottom / 60% no-repeat; }

    /* 4. gradient overlay on top of image (first layer is top) */
    .t-overlay {
      background:
        linear-gradient(to top, rgb(0 0 0 / .75), rgb(0 0 0 / .1)),   /* TOP layer: dark bottom fade */
        var(--img) center / cover no-repeat,                           /* image below */
        #111;                                                          /* colour in the LAST layer */
      display: flex; align-items: flex-end;
    }

    /* 5. gradients only */
    .t-linear { background: linear-gradient(135deg, #f43f5e, #f59e0b); }
    .t-radial { background: radial-gradient(circle at 30% 30%, #60a5fa, #1e3a8a); }
    .t-stripes { background: repeating-linear-gradient(45deg, #fde68a 0 10px, #fcd34d 10px 20px); color:#111; text-shadow:none; }

    /* 6. gradient text with background-clip */
    .grad-text {
      font-size: 2rem; font-weight: 800;
      background: linear-gradient(90deg, #f43f5e, #6366f1);
      -webkit-background-clip: text;        /* Safari/older Chrome */
      background-clip: text;                /* standard */
      color: transparent;                   /* reveal the background through text */
    }

    /* 7. background-clip: padding-box vs border-box with dashed border */
    .clip { border: 8px dashed rgb(0 0 0 / .3); padding: 10px; background: #34d399; background-clip: padding-box; }

    /* 8. fixed attachment (parallax-ish) - desktop only */
    .t-fixed { height: 160px; background: var(--img) center / cover fixed; }

    /* 9. blend mode */
    .t-blend { background: #e11d48 var(--img) center / cover; background-blend-mode: multiply; }
  </style>
</head>
<body>
  <h2>1. repeat (SVG dots)</h2><div class="tile t-repeat">repeat</div>
  <h2>2. cover</h2><div class="tile t-cover">cover</div>
  <h2>2b. contain</h2><div class="tile t-contain">contain</div>
  <h2>3. position + size %</h2><div class="tile t-pos">right bottom / 60%</div>
  <h2>4. overlay (gradient over image)</h2><div class="tile t-overlay">Biryani Special</div>
  <h2>5. gradients</h2>
  <div class="tile t-linear">linear</div><br>
  <div class="tile t-radial">radial</div><br>
  <div class="tile t-stripes">repeating</div>
  <h2>6. gradient text</h2><div class="grad-text">Foodie Gradient</div>
  <h2>7. background-clip: padding-box</h2><div class="clip">Colour stops at the padding edge, the dashed border area shows page colour</div>
  <h2>8. fixed (scroll the page)</h2><div class="tile t-fixed">fixed</div>
  <h2>9. blend mode</h2><div class="tile t-blend">multiply</div>
  <div style="height:300px"></div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Dynamic background image in React: inline style (url string)
<div style={{
  backgroundImage: `url(${product.image})`,
  backgroundSize: "cover",
  backgroundPosition: "center",
}} className="h-48 rounded-lg" />

// 2. Tailwind
<div className="bg-gray-900 bg-cover bg-center bg-no-repeat bg-[url('/hero.jpg')]" />
<div className="bg-gradient-to-r from-rose-500 to-amber-500" />       {/* v3; v4: bg-linear-to-r */}
<h1 className="bg-gradient-to-r from-pink-500 to-indigo-500 bg-clip-text text-transparent">Gradient text</h1>
<div className="bg-black/50" />                                         {/* alpha colour */}

// 3. Next.js: images in /public are referenced as url('/hero.jpg').
//    Importing from CSS modules: background: url('/hero.jpg') center / cover;

// 4. SEO/performance: a meaningful hero image should be <Image fill priority className="object-cover" />
//    instead of CSS background, because next/image gives responsive sizes, lazy loading and AVIF/WebP.
import Image from "next/image";
<div className="relative h-64">
  <Image src="/hero.jpg" alt="Biryani" fill priority className="object-cover" />
  <div className="absolute inset-0 bg-black/40" />   {/* overlay */}
</div>
```

---

## ⚫ Interview Questions + Answers

**Q1: `background-size: cover` vs `contain`?**
A1: `cover` scales the image to completely fill the box, keeping aspect ratio and cropping overflow, so there are no empty gaps. `contain` scales to fit the whole image inside, so the entire image shows but empty bands may remain. Hero banners use `cover`; logos use `contain`.

**Q2: How do you overlay a dark layer on a background image for readable text?**
A2: Stack a semi-transparent gradient on top as the first background layer: `background: linear-gradient(rgb(0 0 0 / .5), rgb(0 0 0 / .5)), url(img.jpg) center / cover;`. Alternatively an `::before` overlay element. Don't use `opacity` on the container (it fades the text).

**Q3: Background image vs `<img>` - when to use which?**
A3: `<img>` for meaningful content (product photos, article images): it has `alt` (accessibility/SEO), `srcset`, native lazy loading and is discoverable by crawlers and LCP. CSS background for decorative visuals, patterns and gradients where content layering matters.

**Q4: What does the `background` shorthand reset, and how are multiple backgrounds ordered?**
A4: The shorthand resets all omitted sub-properties (size, repeat, position...) to defaults, which can erase earlier longhand rules. With several layers separated by commas, the first listed layer sits on top and the colour may only be in the final layer. Position and size are written `position / size`.

**Q5: How do you make gradient text?**
A5: Set a gradient as `background`, apply `background-clip: text` (plus `-webkit-background-clip: text` for broader support) and set `color: transparent`. Tailwind: `bg-clip-text text-transparent bg-gradient-to-r ...`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Overriding with a shorthand after longhands
```css
/* WRONG: shorthand resets size/position set above */
.hero { background-size: cover; background-position: center; }
.hero { background: url(a.jpg); }

/* CORRECT */
.hero { background: url(a.jpg) center / cover no-repeat; }
```

❌ **Mistake 2:** Text unreadable over image
```css
/* WRONG */
.hero { background: url(a.jpg) center / cover; color: #fff; }

/* CORRECT: overlay */
.hero { background: linear-gradient(rgb(0 0 0 / .5), rgb(0 0 0 / .5)), url(a.jpg) center / cover; }
```

❌ **Mistake 3:** Container has no height so the image doesn't show
```css
/* WRONG: empty div has 0 height */
.banner { background: url(a.jpg) center / cover; }

/* CORRECT */
.banner { min-height: 300px; /* or aspect-ratio: 16 / 9 */ background: url(a.jpg) center / cover; }
```

❌ **Mistake 4:** `background-attachment: fixed` on mobile
```css
/* WRONG: broken/janky on iOS Safari */
.hero { background-attachment: fixed; }

/* CORRECT: only on large screens with hover/fine pointer, or use position: sticky tricks */
@media (min-width: 1024px) and (hover: hover) { .hero { background-attachment: fixed; } }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| background-color | Fill colour | भरने का रंग |
| background-image | Image or gradient layers | Image/gradient layers |
| background-size | cover / contain / length | Image का size |
| background-position | Where image sits | Image कहाँ बैठे |
| background-repeat | Tiling behaviour | दोहराव |
| background-clip | Paint extent (text, padding-box) | Paint कहाँ तक |
| Gradient | Colour transition image | रंगों का मिश्रण |
| Overlay | Translucent layer for readability | पारदर्शी परत |

---

## ⚡ 3-Line Summary
**English:**
1. Backgrounds paint colour, images and gradients behind content, with size, position, repeat, attachment and clip controls.
2. Use `center / cover no-repeat` for hero images and a gradient overlay for text readability; the shorthand resets omitted values.
3. Use `<img>`/`next/image` for meaningful images; CSS backgrounds for decoration and gradients.

**Hindi:**
1. Background content के पीछे रंग, image और gradient लगाता है, size/position/repeat/clip control के साथ।
2. Hero के लिए `center / cover no-repeat` और text पढ़ने के लिए gradient overlay; shorthand बाकी values reset कर देता है।
3. ज़रूरी images के लिए `<img>`/`next/image`, सजावट और gradients के लिए CSS background।

---

## ➡️ Next Topic
**62. Border + Border-radius** — borders, rounded corners, circles, pills और outline vs border का फर्क।
