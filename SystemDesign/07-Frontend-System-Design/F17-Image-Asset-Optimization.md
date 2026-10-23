# F17. Image + Asset Optimization
# हिंदी में: Image + Asset Optimization — तस्वीरें, fonts और दूसरी files को छोटा, सही आकार और सही format में, सही समय पर भेजना ताकि पेज जल्दी खुले, data कम लगे और कुछ न खिसके

---

## 🔵 Simple Definition (English)
Images (and fonts, videos, icons) are usually **the largest bytes on a page** and often the **LCP element**. Asset optimization means:
- **Right format**: AVIF/WebP for photos, SVG for icons/logos, PNG only when needed; video (MP4/WebM) instead of GIF.
- **Right size**: responsive images (`srcset` + `sizes`), so a phone doesn't download a 4000-px desktop image; serve DPR-aware sizes.
- **Right compression**: quality ~60–80, stripped metadata.
- **Right time**: lazy-load below-the-fold images; **prioritize** the LCP image (`fetchpriority="high"`, preload, never lazy).
- **No layout shift**: width/height or `aspect-ratio`, plus placeholders (blur/BlurHash/dominant color).
- **Delivery**: an **image CDN** that resizes and converts on the fly (Cloudinary, imgix, CloudFront + Lambda, Next.js Image), with long cache + immutable URLs.
- **Fonts**: WOFF2, subset (Latin/Devanagari), `font-display: swap/optional`, preload, self-host.

## 🔵 सरल परिभाषा (Hindi)
Images अक्सर पेज की सबसे भारी चीज़ होती हैं और LCP भी। Optimization = सही format (फ़ोटो के लिए AVIF/WebP, icons के लिए SVG, GIF की जगह video), सही आकार (फ़ोन को छोटी image — `srcset`), सही compression, सही समय (नीचे वाली images lazy, hero image पहले), जगह पहले से तय (width/height, blur placeholder), image CDN से resize/convert, और fonts छोटे (WOFF2, सिर्फ़ ज़रूरी अक्षर, swap)।

---

## 🔴 Problem it Solves
Typical unoptimized page: a 3 MB hero JPEG at 4000 px shown in a 400-px slot, 40 product images loading at once, and a GIF banner of 5 MB. The result:
- **Slow LCP** (seconds on 4G), high **data cost** for users on prepaid plans, wasted CDN bandwidth (₹₹).
- **CLS** when images pop in without reserved space.
- **Memory pressure and crashes** on low-end Android devices decoding huge bitmaps (especially in React Native lists).
- Invisible text (FOIT) while big custom fonts load.
Optimizing assets is often the **single biggest performance win** with the least code change.

## 🔴 यह क्यों बना? (Hindi)
आम ग़लती: 400 px की जगह में 4000 px की 3 MB JPEG, 40 product images एक साथ, 5 MB का GIF banner — नतीजा: धीमा LCP, prepaid data पर यूज़र का पैसा, CDN का बिल, images आने पर content खिसकना (CLS), सस्ते Android पर बड़ी images से memory भरकर crash, और fonts आने तक अक्षर ग़ायब।
Assets optimize करना अक्सर कम मेहनत में सबसे बड़ा performance फ़ायदा देता है।

---

## 🟢 How it Works — Step by Step

### Format guide

```
┌──────────────┬───────────────────────────────────────────┬───────────────────────────────┐
│ Format       │ Use for                                   │ Notes                         │
├──────────────┼───────────────────────────────────────────┼───────────────────────────────┤
│ AVIF         │ Photos, banners (best compression)        │ ~30–50% smaller than JPEG;    │
│              │                                           │ slower encode; wide support   │
│ WebP         │ Photos + transparency (universal fallback)│ ~25–35% smaller than JPEG     │
│ JPEG         │ Legacy fallback for photos                │ Progressive JPEG for big ones │
│ PNG          │ Screenshots/graphics needing lossless     │ Often replace with WebP/SVG   │
│ SVG          │ Logos, icons, illustrations               │ Tiny, crisp at any size;      │
│              │                                           │ sanitize user SVGs (XSS!)     │
│ MP4/WebM     │ Animations (instead of GIF)               │ 5–20× smaller than GIF        │
│ Lottie/Rive  │ Vector animations (onboarding, loaders)   │ Small JSON, needs runtime     │
└──────────────┴───────────────────────────────────────────┴───────────────────────────────┘
Serve via <picture> or content negotiation (Accept: image/avif,image/webp) at the image CDN.
```

### Responsive images

```html
<img
  src="https://img.cdn.com/p/42.jpg?w=800"
  srcset="https://img.cdn.com/p/42.jpg?w=400 400w,
          https://img.cdn.com/p/42.jpg?w=800 800w,
          https://img.cdn.com/p/42.jpg?w=1200 1200w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 400px"
  width="800" height="800" alt="Paneer Butter Masala" loading="lazy" decoding="async" />
Browser picks the smallest candidate ≥ slot width × device pixel ratio (DPR)
Phone 360 px wide, DPR 3 → needs ~1080 px; cap DPR at 2 for most photos to save bytes
```

### Loading priority

```
Above the fold LCP image:  fetchpriority="high", NOT lazy, preload if discovered late (CSS bg, JS)
Other above-the-fold:      normal eager
Below the fold:            loading="lazy" (native) or IntersectionObserver; decoding="async"
Carousels:                 load first slide eagerly, others lazily
Background images in CSS:  discovered late → prefer <img> for important visuals
```

### Placeholders & CLS

```
Always reserve space: width+height attributes or CSS aspect-ratio
Placeholder options: dominant color box → LQIP (tiny 20 px blurred) → BlurHash/ThumbHash string (~30 bytes)
Store blurhash + width/height with the image record in DB (computed at upload by a worker)
```

### Image pipeline (upload → serve)

```
User/merchant uploads (presigned S3 URL, Topic 51a)
   → S3 event → worker (sharp/Pillow): validate type, strip EXIF (GPS privacy!), generate
     variants (320/640/1080/1600) in AVIF+WebP, compute blurhash, store dimensions
   → or on-the-fly image CDN: https://img.cdn.com/{key}?w=640&fm=avif&q=70 (cached at edge)
   → URLs are immutable (new upload = new key) → Cache-Control: max-age=31536000, immutable
```

### Fonts

```
- WOFF2 only; subset to needed scripts (Latin + Devanagari for Hindi UI), variable fonts for many weights
- font-display: swap (show fallback text immediately) or optional (no swap if late → zero CLS)
- Preload the 1–2 critical fonts; self-host (next/font does this) to avoid third-party connection
- size-adjust / fallback metric overrides to minimize shift when swapping
- System font stack is the fastest option for app UIs
```

### Other assets

```
Icons: SVG sprite or icon components (tree-shaken), not a whole icon font
Video: poster image, preload="none"/"metadata", adaptive streaming (HLS) for long video (Topic 121)
Compression: brotli for text assets (JS/CSS/SVG/JSON) at CDN
Third-party embeds (YouTube, maps): facade (static thumbnail) → load iframe on click
```

## 🟢 कैसे काम करता है? (Hindi)
1. फ़ोटो के लिए AVIF/WebP (JPEG से 30–50% छोटा), logo/icon के लिए SVG, GIF की जगह MP4; image CDN `Accept` header देखकर सही format भेजता है।
2. `srcset` + `sizes` से ब्राउज़र स्क्रीन के हिसाब से सबसे छोटी काफ़ी image चुनता है — फ़ोन को 4000 px नहीं; DPR 2 तक सीमित रखो।
3. LCP (hero) image को `fetchpriority="high"`, lazy नहीं; नीचे की images `loading="lazy"`; carousel में पहली slide तुरंत, बाक़ी बाद में।
4. जगह पहले से: width/height या aspect-ratio; placeholder के लिए BlurHash (upload पर worker बनाकर DB में रखे); upload पर EXIF (GPS location) हटाओ।
5. Fonts: WOFF2, सिर्फ़ ज़रूरी अक्षर (Latin + देवनागरी), `font-display: swap`, preload, self-host; YouTube/maps embed के लिए पहले सिर्फ़ thumbnail, click पर असली iframe।

---

## 🟡 Real World Example

**Swiggy / Zomato** — show hundreds of dish and restaurant images. They serve them through an image CDN with on-the-fly resizing (width parameters in URLs), modern formats and aggressive caching, with placeholders while scrolling.

**Pinterest** — uses dominant-colour placeholders for every pin, so the masonry grid has no layout shift and feels instant while images stream in.

**Instagram / Facebook** — generate multiple resolutions per upload and use progressive and modern formats, picking the variant by device and network quality. Facebook pioneered tiny preview thumbnails (~200 bytes) embedded in the feed response for instant blurred previews.

**Google Fonts and next/font** — font subsetting by unicode-range means a Hindi page downloads only the Devanagari subset needed.

## 🟡 Real Example Hindi में
Swiggy/Zomato सैकड़ों dish images image CDN से भेजते हैं — URL में width देकर resize, नया format, लंबा cache, scroll में placeholder।
Pinterest हर pin के लिए dominant color placeholder दिखाता है (कोई खिसकाव नहीं); Facebook feed के जवाब में ही ~200 bytes का छोटा preview भेजता है ताकि तुरंत धुंधली image दिखे; Google Fonts हिंदी पेज के लिए सिर्फ़ देवनागरी हिस्सा भेजता है।

---

## 🟠 My Stack Example

### Next.js `<Image>` — responsive, lazy, modern formats, placeholder
```tsx
import Image from 'next/image';

// LCP hero
<Image src={banner.url} alt={banner.alt} width={1200} height={500} priority sizes="100vw" />

// Grid item (lazy by default) with blur placeholder from DB
<Image src={dish.imageUrl} alt={dish.name} width={320} height={240}
       sizes="(max-width: 640px) 50vw, 320px"
       placeholder="blur" blurDataURL={dish.blurDataUrl} />
```
```js
// next.config.js — allow CDN host, prefer AVIF then WebP
module.exports = { images: { formats: ['image/avif', 'image/webp'], remotePatterns: [{ protocol: 'https', hostname: 'img.cdn.myapp.com' }] } };
```

### Upload processing worker (Node + sharp) — variants + blurhash + EXIF strip
```js
import sharp from 'sharp';
import { encode } from 'blurhash';

export async function processImage(buffer, key) {
  const img = sharp(buffer, { failOn: 'error' }).rotate();          // auto-orient, then metadata dropped by default
  const { width, height } = await img.metadata();
  const sizes = [320, 640, 1080, 1600].filter((w) => w <= width);
  await Promise.all(sizes.flatMap((w) => [
    img.clone().resize({ width: w }).avif({ quality: 55 }).toBuffer().then((b) => s3Put(`${key}/${w}.avif`, b, 'image/avif')),
    img.clone().resize({ width: w }).webp({ quality: 70 }).toBuffer().then((b) => s3Put(`${key}/${w}.webp`, b, 'image/webp')),
  ]));
  const { data, info } = await img.clone().resize(32, 32, { fit: 'inside' }).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const blurhash = encode(new Uint8ClampedArray(data), info.width, info.height, 4, 3);
  await db.images.update({ key }, { width, height, blurhash, variants: sizes });   // dimensions → no CLS
}
```

### FastAPI equivalent with Pillow (thumbnail)
```python
from PIL import Image, ImageOps
def make_webp(src_path: str, dst_path: str, width: int):
    with Image.open(src_path) as im:
        im = ImageOps.exif_transpose(im)                # orient, then save without EXIF
        im.thumbnail((width, width * 4))
        im.save(dst_path, "WEBP", quality=70, method=6)
```

### `<picture>` fallback (plain HTML/React)
```html
<picture>
  <source type="image/avif" srcset="/img/42/640.avif 640w, /img/42/1080.avif 1080w" sizes="100vw" />
  <source type="image/webp" srcset="/img/42/640.webp 640w, /img/42/1080.webp 1080w" sizes="100vw" />
  <img src="/img/42/640.jpg" width="1080" height="720" alt="Biryani" loading="lazy" decoding="async" />
</picture>
```

### YouTube facade (huge JS saved until click)
```tsx
function YouTubeLite({ id, title }: { id: string; title: string }) {
  const [play, setPlay] = useState(false);
  return play
    ? <iframe src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1`} title={title} allow="autoplay; encrypted-media" allowFullScreen style={{ aspectRatio: '16/9', width: '100%' }} />
    : <button onClick={() => setPlay(true)} aria-label={`Play ${title}`} style={{ aspectRatio: '16/9', width: '100%', background: `url(https://i.ytimg.com/vi/${id}/hqdefault.jpg) center/cover` }}>▶</button>;
}
```

### Fonts with next/font (Hindi + English)
```ts
import { Noto_Sans_Devanagari, Inter } from 'next/font/google';
export const inter = Inter({ subsets: ['latin'], display: 'swap', variable: '--font-inter' });
export const hindi = Noto_Sans_Devanagari({ subsets: ['devanagari'], weight: ['400', '600'], display: 'swap', variable: '--font-hi' });
```

### React Native (details in M12)
```tsx
import { Image } from 'expo-image';
<Image source={{ uri: `${dish.imageUrl}?w=${Math.round(160 * PixelRatio.get())}` }} placeholder={{ blurhash: dish.blurhash }}
       style={{ width: 160, height: 120 }} contentFit="cover" transition={150} cachePolicy="memory-disk" />
// Request device-sized images from the CDN — decoding 4000px bitmaps in a list crashes low-end phones
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you optimize images on an e-commerce product listing page?**
A1: Serve images through an image CDN that resizes and converts on the fly (AVIF/WebP with fallback) with immutable long-cache URLs. Use responsive `srcset`/`sizes` matched to the grid slot and capped DPR. Lazy-load below-the-fold items while giving the first-row or LCP image high priority. Reserve space with dimensions or aspect-ratio and show BlurHash or dominant-colour placeholders. Compress at sensible quality and strip metadata. Virtualize long grids. Precompute dimensions and placeholders at upload time.

**Q2: Why shouldn't you lazy-load the LCP image?**
A2: Lazy loading delays the request until layout determines the image is in the viewport, and lazy images get low priority, so the largest above-the-fold element loads late and LCP worsens. The LCP image should be in the initial HTML, eagerly loaded with `fetchpriority="high"` (or preloaded if referenced from CSS or JS), properly sized and served from a fast CDN.

**Q3: How do `srcset` and `sizes` work?**
A3: `srcset` lists candidate image URLs with their intrinsic widths (`400w, 800w, …`). `sizes` tells the browser how wide the image will be displayed at different viewport widths (`(max-width: 600px) 100vw, 400px`) before layout is known. The browser multiplies the slot width by the device pixel ratio and picks the most appropriate candidate, so small screens download small files. `<picture>` with `<source type>` adds format selection or art direction.

**Q4: How do you prevent layout shift from images and fonts?**
A4: For images, always provide width and height attributes (browsers derive the aspect ratio) or CSS `aspect-ratio`, reserve containers for ads and embeds, and use placeholders. For fonts, use `font-display: swap` or `optional`, preload critical fonts, subset them, and use fallback fonts with metric overrides (`size-adjust`, ascent and descent overrides; `next/font` automates this) so swapping doesn't reflow text.

**Q5: Design the image pipeline for user uploads (e.g., restaurant menu photos).**
A5: The client uploads directly to object storage using a presigned URL, after client-side resizing to limit size. A storage event triggers a worker that validates file type and size, strips EXIF (privacy), auto-orients, generates multiple widths in AVIF and WebP (or relies on an on-the-fly image CDN), computes BlurHash and dimensions, and stores metadata in the DB. Images are served through a CDN with immutable URLs and long caching. Optionally add moderation (NSFW detection) and a deduplication hash.

---

## 🔷 Trade-offs
✅ AVIF: smallest files — ❌ slower to encode; occasional decode cost on low-end devices.
✅ On-the-fly image CDN: flexible sizes — ❌ cost per transformation, cold-cache latency.
✅ Pre-generated variants: predictable, cheap to serve — ❌ storage, fixed sizes.
✅ Lazy loading: saves bytes — ❌ late images if misapplied (LCP) or no placeholder (CLS).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AVIF / WebP | Modern compressed formats | नए छोटे formats |
| srcset / sizes | Responsive image candidates | स्क्रीन के हिसाब से image |
| DPR | Device pixel ratio | screen की pixel घनता |
| Lazy loading | Load when near viewport | पास आने पर लोड |
| fetchpriority | Browser fetch priority hint | लोड की प्राथमिकता |
| Placeholder / BlurHash | Preview before image loads | पहले धुंधली झलक |
| Image CDN | Resizes/converts at edge | image बदलने वाला CDN |
| EXIF | Photo metadata (may include GPS) | फ़ोटो की छुपी जानकारी |
| Font subsetting | Only needed glyphs | सिर्फ़ ज़रूरी अक्षर |
| font-display | Font loading behaviour | font लोड का तरीका |

---

## ⚡ 3-Line Summary
**English:**
1. Right format (AVIF/WebP, SVG, video not GIF), right size (srcset/sizes, capped DPR), right compression, via an image CDN with immutable caching.
2. Prioritize the LCP image (eager + fetchpriority high), lazy-load the rest, reserve space and show blur placeholders.
3. Process uploads in a pipeline (validate, strip EXIF, variants, blurhash, dimensions); optimize fonts (WOFF2, subset, swap, preload).

**Hindi:**
1. सही format (AVIF/WebP, SVG, GIF नहीं), सही आकार (srcset), सही compression, image CDN + लंबा cache।
2. Hero image पहले, बाक़ी lazy; जगह पहले से और blur placeholder।
3. Upload pipeline (जाँच, EXIF हटाना, variants, blurhash); fonts छोटे — WOFF2, subset, swap, preload।

---

## ➡️ Next Topic Suggestion
**F18. Accessibility (a11y)** — Fast apps must also be usable by everyone: screen-reader users, keyboard users, people with low vision. Next: semantic HTML, ARIA, focus management, colour contrast, and accessible patterns in React and React Native.
