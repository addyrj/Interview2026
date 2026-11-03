# 121. Image Gallery with Grid
# हिंदी में: CSS Grid से Image Gallery

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly; tiles use gradients so no images are needed)

---

## 🔵 Simple Definition (English)
An image gallery arranges photos in a grid where some photos span extra rows or columns. CSS Grid with `grid-auto-rows`, `span`, `grid-auto-flow: dense` and `object-fit: cover` builds a responsive masonry-like layout.

## 🔵 सरल परिभाषा (Hindi)
Image gallery photos को grid में लगाती है जिसमें कुछ photos ज़्यादा rows या columns में फैलती हैं। CSS Grid के `grid-auto-rows`, `span`, `grid-auto-flow: dense` और `object-fit: cover` से responsive masonry जैसा layout बनता है।

---

## 🔴 Problem it Solves
```
BEFORE:
  - float galleries: broken rows when heights differ
  - images of different aspect ratios look stretched or uneven
  - JS libraries (Masonry.js) needed for a "Pinterest" look

NOW: Grid + object-fit gives equal cells, spanning tiles and no stretched images.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - float galleries: heights अलग हों तो rows टूट जाती थीं
  - अलग aspect ratio की images खिंची हुई या बेमेल दिखती थीं
  - "Pinterest" जैसे look के लिए JS libraries (Masonry.js) चाहिए थीं

अब: Grid + object-fit से बराबर cells, फैलने वाली tiles और बिना खिंची images।
```

---

## 🟢 How it Works — Step by Step
```
1. .gallery { display: grid }
2. grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))
     -> columns appear/disappear with width
3. grid-auto-rows: 160px   -> every row has the same fixed height
4. .wide { grid-column: span 2 }, .tall { grid-row: span 2 }, .big = both
5. grid-auto-flow: dense   -> small tiles fill gaps left by big ones
                              (visual order may differ from DOM order)
6. img { width:100%; height:100%; object-fit: cover }  -> fills cell, crops excess
7. overflow:hidden on tile + img scale(1.08) on hover = zoom inside frame
8. figcaption slides up using translateY(100%) -> 0
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. .gallery { display: grid }
2. repeat(auto-fill, minmax(180px, 1fr)) -> width के अनुसार columns घटते-बढ़ते हैं
3. grid-auto-rows: 160px -> हर row की height बराबर
4. .wide { span 2 columns }, .tall { span 2 rows }, .big = दोनों
5. grid-auto-flow: dense -> बड़ी tiles से बचे खाली छेद छोटी tiles भर देती हैं
                            (दिखने का क्रम DOM क्रम से अलग हो सकता है)
6. img { object-fit: cover } -> cell भरती है, ज़्यादा हिस्सा काट देती है
7. tile पर overflow:hidden + hover पर img scale(1.08) = frame के अंदर zoom
8. figcaption translateY(100%) से 0 तक ऊपर सरकता है
```

---

## 🟡 Real World Example
**Instagram profile / Explore:** 3-column grid, with some larger tiles in Explore. **Pinterest** uses a masonry layout. **Zomato / Swiggy** restaurant photo galleries and **Amazon** product thumbnails use consistent cells with `object-fit: cover`. **Google Photos** uses justified rows.

## 🟡 Real Example Hindi mein
**Instagram profile / Explore:** 3-column grid, Explore में कुछ बड़ी tiles भी। **Pinterest** masonry layout use करता है। **Zomato / Swiggy** की restaurant photo gallery और **Amazon** की product thumbnails में `object-fit: cover` वाले बराबर cells होते हैं। **Google Photos** में justified rows होती हैं।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css). With real images:

```html
<section class="gallery">
  <figure class="tile big">
    <!-- width/height attributes prevent layout shift; loading=lazy defers off-screen images -->
    <img src="photo1.jpg" alt="Gateway of India at sunset" width="800" height="600" loading="lazy">
    <figcaption>Mumbai</figcaption>
  </figure>
  <figure class="tile"><img src="photo2.jpg" alt="Goa beach" width="400" height="300" loading="lazy"></figure>
</section>
```

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  grid-auto-rows: 160px;
  grid-auto-flow: dense;
  gap: 10px;
}
.wide { grid-column: span 2; }
.tall { grid-row: span 2; }
.tile { overflow: hidden; border-radius: 10px; }
.tile img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s; }
.tile:hover img { transform: scale(1.08); }
```

---

## 🟠 React/Next.js Connection
```jsx
import Image from 'next/image';

export default function Gallery({ photos }) {
  return (
    // Tailwind: grid with auto-fill columns, fixed row height, dense packing
    <section className="grid auto-rows-[160px] grid-cols-[repeat(auto-fill,minmax(180px,1fr))] gap-2.5 [grid-auto-flow:dense]">
      {photos.map((p) => (
        <figure key={p.id}
          className={`group relative overflow-hidden rounded-xl ${p.big ? 'col-span-2 row-span-2' : ''}`}>
          {/* next/image: lazy, responsive srcset, WebP/AVIF; fill needs a positioned parent */}
          <Image src={p.src} alt={p.alt} fill sizes="(max-width: 600px) 50vw, 25vw"
                 className="object-cover transition-transform duration-500 group-hover:scale-110" />
        </figure>
      ))}
    </section>
  );
}
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make some grid items bigger than others?**
A1: `grid-column: span 2` and `grid-row: span 2` (or explicit line numbers like `1 / 3`). Combined with `grid-auto-rows` for a fixed row height.

**Q2: What does `grid-auto-flow: dense` do and what is the catch?**
A2: It lets the auto-placement algorithm back-fill earlier holes with later items. The catch: visual order can differ from DOM order, which hurts keyboard/screen-reader order.

**Q3: `object-fit: cover` vs `contain`?**
A3: `cover` fills the box and crops overflow; `contain` fits the whole image and leaves empty space. Use `object-position` to choose which part is kept.

**Q4: `auto-fill` vs `auto-fit` here?**
A4: With many items they behave the same. With few items `auto-fit` stretches tiles; `auto-fill` keeps empty columns so tile sizes stay stable, usually preferred for galleries.

**Q5: How do you avoid layout shift and slow loading?**
A5: Set `width`/`height` (or `aspect-ratio`), use `loading="lazy"` for below-the-fold images, modern formats (WebP/AVIF), `srcset`/`sizes`, or `next/image`.

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** Stretching images with fixed width and height and no `object-fit`.
✅ **Correct way:** `object-fit: cover`.

❌ **Mistake 2:** Missing `alt` text.
✅ **Correct way:** Meaningful `alt` (empty `alt=""` only for decorative images).

❌ **Mistake 3:** Scaling the tile instead of the image on hover, which overlaps neighbours.
✅ **Correct way:** `overflow:hidden` on the tile and scale the inner image.

❌ **Mistake 4:** `dense` without thinking about reading order.
✅ **Correct way:** Use it only when order is not meaningful.

❌ **Mistake 5:** Loading all images eagerly.
✅ **Correct way:** `loading="lazy"` plus `priority` only for the first visible image in Next.js.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `span` | Item covers N tracks | N tracks में फैलना |
| `grid-auto-rows` | Size of auto-created rows | अपने-आप बनी rows की height |
| `grid-auto-flow: dense` | Back-fills gaps | खाली जगह भरना |
| `object-fit` | How an image fits its box | Image box में कैसे बैठे |
| `object-position` | Which part of the image shows | Image का कौन सा हिस्सा दिखे |
| Masonry | Pinterest-style uneven columns | Pinterest जैसा layout |
| Lazy loading | Load when near viewport | ज़रूरत पर load |

---

## ⚡ 3-Line Summary
**English:**
1. Use Grid with `auto-fill`/`minmax` columns, a fixed `grid-auto-rows`, and `span` classes for feature tiles.
2. Put `object-fit: cover` on images and `overflow:hidden` on tiles for hover zoom.
3. In Next.js use `next/image` with `fill` and `sizes`; add `alt`, lazy loading and `dense` carefully.

**Hindi:**
1. Grid में `auto-fill`/`minmax` columns, fixed `grid-auto-rows` और बड़ी tiles के लिए `span` classes लगाओ।
2. Images पर `object-fit: cover` और tile पर `overflow:hidden` रखो ताकि hover zoom साफ़ हो।
3. Next.js में `next/image` (`fill`, `sizes`) use करो; `alt`, lazy loading और `dense` सोच-समझकर लगाओ।

---

## ➡️ Next Topic
**122. CSS Tooltip** — hover/focus पर छोटा info box, `::after` और `attr()` से।
