# M12. Image Loading + Caching on Mobile
# हिंदी में: Mobile पर Image Loading + Caching — फ़ोन पर सैकड़ों images (menu, products, feed) को तेज़, कम memory और कम data में दिखाना: सही आकार में decode करना, memory और disk cache, प्राथमिकता, scroll से बाहर जाने पर cancel, और placeholders

---

## 🔵 Simple Definition (English)
An **image loading pipeline** fetches, decodes, transforms, caches and displays images efficiently:
- **Request** sized for the view (CDN resizing: `?w=360&dpr=3`).
- **Cache layers**: **memory cache** (decoded bitmaps, LRU, instant) → **disk cache** (encoded files, survives restarts) → **network** (deduplicated in-flight requests).
- **Decode off the main thread** and **downsample** to the target view size (a 4000×3000 photo is ~48 MB as a bitmap!).
- **Prioritize** visible images, **cancel** requests for cells scrolled away, and **prefetch** upcoming ones.
- **Placeholders** (BlurHash/ThumbHash, dominant colour) and **transitions** for perceived speed.
Libraries:
- React Native: **expo-image** (built on SDWebImage on iOS and Glide on Android), react-native-fast-image (older), the core `Image`.
- Native: **Glide**, **Coil**, Fresco (Android); **SDWebImage**, **Kingfisher**, Nuke (iOS).
"Design an image loading library" is a classic mobile system design question.

## 🔵 सरल परिभाषा (Hindi)
Image loading pipeline = image को लाना, decode करना, छोटा करना, cache करना और दिखाना — कुशलता से: view के आकार की image माँगो (CDN से resize); पहले memory cache (decoded, तुरंत), फिर disk cache (restart के बाद भी), फिर network (एक जैसी requests एक); decode main thread से बाहर और view के आकार में (4000×3000 फ़ोटो bitmap में ~48 MB!); दिखने वाली images पहले, scroll से बाहर गई cancel, आने वाली prefetch; blurhash placeholder।
RN में expo-image (iOS पर SDWebImage, Android पर Glide)।

---

## 🔴 Problem it Solves
Images are the **#1 cause of memory crashes (OOM)** and janky scrolling in mobile apps:
- **Memory**: bitmap size = width × height × 4 bytes. Ten 12 MP photos decoded at full size is ~480 MB, which crashes a 3 GB Android phone.
- **Jank**: decoding large JPEGs on the main/UI thread drops frames while scrolling a menu.
- **Data waste**: downloading 2 MB originals for 120-px thumbnails burns users' data.
- **Repeated downloads**: no disk cache means every app open refetches the same restaurant images.
- **Wrong images in recycled cells**: a slow request for row 5 finishes after the cell was reused for row 25, so the wrong dish photo shows.
- **Flicker and layout jumps** without placeholders and fixed dimensions.

## 🔴 यह क्यों बना? (Hindi)
Images mobile ऐप में memory crash (OOM) और झटकेदार scrolling की सबसे बड़ी वजह हैं: bitmap = चौड़ाई × ऊँचाई × 4 bytes — 12 MP की 10 फ़ोटो पूरे आकार में ~480 MB (3 GB फ़ोन crash); main thread पर बड़ी JPEG decode करने से frames गिरते हैं; 120 px thumbnail के लिए 2 MB original = data बर्बाद; disk cache नहीं तो हर बार वही images दोबारा; recycle हुए cell में पुरानी धीमी request ग़लत फ़ोटो दिखा दे; placeholder और fixed size नहीं तो झपकना और खिसकना।

---

## 🟢 How it Works — Step by Step

### Pipeline (what a good loader does)

```
load(url, targetSize=120×90 @3x, priority=HIGH, into: cell#7)
  │
  ├─► key = hash(url + targetSize + transforms)
  ├─► MEMORY CACHE (decoded bitmap, LRU by bytes, ~15–25% of app memory) ── hit ──► display (sync, no flicker)
  │      miss
  ├─► DISK CACHE (encoded bytes, LRU by size, e.g. 250–500 MB) ── hit ──► decode (bg thread) ─┐
  │      miss                                                                                │
  ├─► IN-FLIGHT MAP: same url already downloading? → attach to it (dedupe)                   │
  ├─► NETWORK (priority queue, limited concurrency ~4–6 per host, HTTP/2)                    │
  │      → write encoded bytes to disk cache                                                  │
  │      → decode on background thread WITH DOWNSAMPLING to 360×270 px (not 4000×3000)  ◄────┘
  │      → transforms (rounded corners, crop) → put in memory cache
  └─► main thread: if cell#7 still wants this key → display with fade; else drop (recycled cell)
Cancel: cell scrolled off / screen unmounted → cancel pending request (unless shared by another view)
Prefetch: next N items in list → low priority download to disk cache (no decode)
```

### Memory math (say this in interviews)

```
Bitmap bytes ≈ width_px × height_px × 4 (ARGB_8888)
  Full 4000×3000 photo:   48 MB        ❌
  Downsampled 1080×810:   ~3.5 MB
  Thumbnail 360×270:      ~0.4 MB      ✅ (what a list cell actually needs at 3x density)
Request the right size from CDN AND decode at view size (both matter)
Android: RGB_565 (2 bytes/px) for opaque images halves memory (Glide option); hardware bitmaps (Android 8+)
iOS: decode via ImageIO downsampling (CGImageSourceCreateThumbnailAtIndex), not UIImage(named:) full decode
Respond to memory warnings: trim memory cache (onTrimMemory / didReceiveMemoryWarning)
```

### Cache design decisions

```
Memory cache: LRU by BYTES (not count); keyed by url+size; cleared on memory pressure
Disk cache:   LRU by total size; key = url (+ transform); respects Cache-Control or app-defined TTL;
              stored in Caches dir (OS may purge → fine, it's a cache)
Invalidation: immutable URLs (new image = new URL/hash) → no invalidation needed (best);
              for mutable URLs (avatars at /users/7/avatar) → ETag revalidation or version param ?v=12
Separate caches/policies: thumbnails vs full-screen images vs user avatars
```

### Perceived performance

```
Placeholders: blurhash/thumbhash from API (~20–30 chars) → instant blurred preview, no network
Fixed aspect ratio boxes → no layout jump (CLS on mobile)
Progressive JPEG / low-res first then high-res (Instagram-style)
Fade-in transition 100–200 ms; no fade when served from memory (avoids flicker on scroll back)
Prefetch: next screen's hero image on tap-down; next 10 list items while idle
```

### Formats on mobile

```
WebP: supported everywhere (Android 4+, iOS 14+) → good default
AVIF: Android 12+, iOS 16+ → smaller, but decode cost on low-end devices; let CDN negotiate by Accept header
HEIC: iOS camera default → convert on upload for cross-platform
Animated: prefer short MP4/WebP animations over GIF (memory & CPU)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Key = URL + आकार; पहले memory cache (decoded, तुरंत दिखे), फिर disk cache (encoded, decode background thread पर), फिर network — और अगर वही URL पहले से download हो रहा है तो उसी से जुड़ जाओ (dedupe)।
2. Decode करते समय view के आकार में downsample — list cell के लिए 360×270 (~0.4 MB), 4000×3000 (48 MB) नहीं; CDN से भी सही आकार माँगो — दोनों ज़रूरी।
3. Memory cache bytes के हिसाब से LRU, memory चेतावनी पर ख़ाली करो; disk cache आकार की सीमा के साथ; image बदलने पर नया URL (immutable) — invalidation की ज़रूरत नहीं।
4. Scroll से बाहर गया cell → request cancel; recycled cell में सिर्फ़ वही image दिखाओ जो अभी उसे चाहिए; अगले items prefetch (low priority)।
5. Blurhash placeholder + fixed aspect ratio + हल्का fade; WebP default, AVIF नए फ़ोन पर; GIF की जगह छोटी MP4/WebP animation।

---

## 🟡 Real World Example

**Instagram / Facebook** — Facebook built **Fresco** (Android) to manage image memory on older Android devices (storing bitmaps outside the Java heap on pre-Lollipop) and to support progressive JPEG. Instagram shows low-res previews first and prefetches the next feed images.

**Pinterest** — dominant-colour placeholders and aggressive prefetching keep its image-only masonry feed smooth. Their engineering posts discuss image loading and memory as core performance work.

**Swiggy / Zomato / Blinkit menus** — hundreds of item images per restaurant or category. They request CDN-resized thumbnails for list cells and larger images only on the item detail sheet, with disk caching so repeat visits are instant and cheap on data.

**Glide (Google-recommended) & SDWebImage** — the de facto native loaders. expo-image wraps both, giving React Native apps memory and disk caching, downsampling, blurhash placeholders and priority handling.

## 🟡 Real Example Hindi में
Facebook ने पुराने Android फ़ोन पर image memory संभालने के लिए **Fresco** बनाया; Instagram पहले धुंधली छोटी image और फिर साफ़ दिखाता है और अगली images पहले से लाता है; Pinterest dominant color placeholder से feed smooth रखता है।
Swiggy/Zomato/Blinkit के menu में सैकड़ों images — list में CDN से छोटे thumbnails, detail पर बड़ी image, disk cache से दोबारा खोलने पर तुरंत और data बचत; expo-image अंदर से Glide (Android) और SDWebImage (iOS) इस्तेमाल करता है।

---

## 🟠 My Stack Example

### expo-image in a menu list (sized URL, blurhash, caching, priority)
```tsx
import { Image } from 'expo-image';
import { PixelRatio } from 'react-native';

const CELL_W = 120, CELL_H = 90;
const sized = (tpl: string, w: number) => tpl.replace('{w}', String(Math.round(w * Math.min(PixelRatio.get(), 3))));  // cap at 3x

export const DishImage = memo(function DishImage({ dish }: { dish: Dish }) {
  return (
    <Image
      source={{ uri: sized(dish.image.urlTemplate, CELL_W) }}
      placeholder={{ blurhash: dish.image.blurhash }}
      style={{ width: CELL_W, height: CELL_H, borderRadius: 8 }}
      contentFit="cover"
      transition={150}
      cachePolicy="memory-disk"                       // memory + disk cache
      recyclingKey={dish.id}                          // correct image in recycled FlashList cells
      priority="normal"
      accessibilityLabel={dish.name}
    />
  );
});
```

### Prefetch next items and hero image on press
```ts
import { Image } from 'expo-image';
// While idle: warm disk cache for the next page of items
export const prefetchDishImages = (dishes: Dish[]) => Image.prefetch(dishes.slice(0, 10).map((d) => sized(d.image.urlTemplate, CELL_W)), 'disk');
// On press-in (before navigation), start fetching the detail-size hero
<Pressable onPressIn={() => Image.prefetch(sized(dish.image.urlTemplate, 400))} onPress={() => router.push(`/dish/${dish.id}`)} />
```

### Memory pressure handling
```ts
import { AppState } from 'react-native';
AppState.addEventListener('memoryWarning', () => { Image.clearMemoryCache(); });   // keep disk cache
// Settings screen: "Clear image cache" → Image.clearDiskCache()
```

### Backend/CDN contract for images (from API)
```json
{ "image": { "urlTemplate": "https://img.quickbite.in/dishes/9f3a.webp?w={w}&q=70", "width": 1600, "height": 1200, "blurhash": "LKO2?U%2Tw=w]~RBVZRi};RPxuwH" } }
```

### Designing an image loader (interview sketch in TypeScript-like pseudocode)
```ts
class ImageLoader {
  private mem = new LruCache<string, Bitmap>({ maxBytes: deviceMemory * 0.15, sizeOf: (b) => b.byteCount });
  private disk = new DiskLru({ maxBytes: 300 * MB, dir: cachesDir });
  private inflight = new Map<string, Promise<Uint8Array>>();
  private queue = new PriorityQueue<Job>({ concurrency: 6 });

  async load(req: { url: string; w: number; h: number; priority: Priority; target: ViewRef }) {
    const key = `${req.url}|${req.w}x${req.h}`;
    const hit = this.mem.get(key);
    if (hit) return req.target.show(hit, { animate: false });                  // instant, no flicker
    req.target.bind(key);                                                      // remember what this view wants
    let bytes = await this.disk.get(req.url);
    if (!bytes) {
      bytes = await (this.inflight.get(req.url) ?? this.fetchOnce(req.url, req.priority, req.target.cancelSignal));
      this.disk.put(req.url, bytes);
    }
    const bmp = await decodeOnWorker(bytes, { maxW: req.w, maxH: req.h });     // downsample, background thread
    this.mem.set(key, bmp);
    if (req.target.boundKey() === key) req.target.show(bmp, { animate: true }); // drop if cell was recycled
  }
  private fetchOnce(url: string, p: Priority, signal: AbortSignal) {
    const job = this.queue.add(() => http.getBytes(url, { signal }), p).finally(() => this.inflight.delete(url));
    this.inflight.set(url, job);
    return job;
  }
  onMemoryWarning() { this.mem.trimTo(0.25); }
}
```

### Upload side: generate sizes + blurhash (see F17 pipeline)
```
Merchant uploads dish photo → S3 → worker (sharp): 320/640/1080/1600 widths WebP/AVIF + blurhash + dims
→ catalog API returns urlTemplate + dims + blurhash → apps request exactly what they render
```

---

## ⚫ Interview Questions + Answers

**Q1: Design an image loading library for a mobile app.**
A1: Expose an API like `load(url, targetSize, options) → into(view)` with placeholders, transformations, priority and cancellation. Internally, a two-level cache: a memory LRU of decoded bitmaps sized by bytes (cleared on memory pressure) and a disk LRU of encoded bytes with size limits and TTL or immutable-URL semantics. Deduplicate identical in-flight requests, use a prioritized download queue with limited concurrency, and decode and downsample on background threads to the target size. Bind requests to views to avoid wrong images in recycled cells, cancel when views detach, support prefetching into the disk cache, and record metrics (hit rates, decode time, memory).

**Q2: Why do images cause OOM crashes, and how do you prevent them?**
A2: A decoded bitmap uses roughly width × height × 4 bytes regardless of the compressed file size, so a 12 MP photo is about 48 MB in memory. Loading several full-size images, especially in lists, exhausts the heap on low-memory devices. Prevent it by requesting appropriately sized images from the CDN, downsampling during decode to the view's pixel size, using memory-efficient configs (RGB_565 or hardware bitmaps), bounding the memory cache by bytes, releasing images for off-screen views, and trimming caches on memory warnings.

**Q3: How do you avoid showing the wrong image in a recycled list cell?**
A3: Associate each view with the key (URL plus size) it currently needs, set at bind time. When an async load completes, display it only if the view's current key still matches, otherwise just cache it. Cancel or detach the previous request when the cell is rebound, clear or set a placeholder immediately on rebind, and use library features like `recyclingKey` (expo-image) or Glide's lifecycle-aware request clearing.

**Q4: How should caching and invalidation work for images?**
A4: Use immutable, content-addressed URLs (a new upload gets a new URL or hash) so cached images never need invalidation and can be cached for a long time on CDN, disk and memory. For mutable resources like avatars at fixed URLs, add a version parameter from the API (`?v=12`) or rely on HTTP revalidation (ETag) with a reasonable TTL. Keep the disk cache in the OS caches directory with an LRU size cap, since the OS may purge it, and use the memory cache only for the current session.

**Q5: How do you make image-heavy screens feel fast?**
A5: Render fixed-size placeholders immediately (BlurHash or dominant colour from the API) to avoid layout shifts. Serve from memory cache without animation when scrolling back. Prefetch the next items and the next screen's hero on press-in. Request correctly sized, modern formats (WebP) from a nearby CDN. Prioritize visible images over prefetches, use progressive or low-res-first loading for large images, limit concurrent downloads, and virtualize lists (FlashList) so only visible cells load.

---

## 🔷 Trade-offs
✅ Large memory cache: instant scroll-back — ❌ OOM risk on low-end devices (size by bytes, trim on pressure).
✅ Aggressive prefetch: smooth UX — ❌ wasted data/battery if users don't scroll (limit on cellular).
✅ AVIF: smallest bytes — ❌ slower decode on old devices.
✅ Disk cache: offline & cheaper repeat views — ❌ storage use (cap it, allow user clear).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bitmap | Decoded pixel buffer | decode हुई image |
| Downsampling | Decode at smaller size | छोटे आकार में decode |
| Memory cache | Decoded images in RAM | RAM में images |
| Disk cache | Encoded images on storage | storage में images |
| LRU | Least recently used eviction | सबसे पुराना इस्तेमाल हटाओ |
| In-flight dedupe | Share identical downloads | एक जैसे download साझा |
| Prefetch | Load before needed | पहले से लाना |
| Recycled cell | Reused list item view | दोबारा इस्तेमाल cell |
| BlurHash | Compact blurred placeholder | छोटा धुंधला placeholder |
| OOM | Out-of-memory crash | memory ख़त्म crash |

---

## ⚡ 3-Line Summary
**English:**
1. Pipeline: memory cache → disk cache → deduped prioritized network → background decode with downsampling → memory cache → display if view still wants it.
2. Memory = w × h × 4: request CDN-sized images and decode at view size; bound caches by bytes; trim on memory warnings.
3. Feel fast: blurhash placeholders, fixed aspect ratios, prefetch next items/hero, cancel off-screen loads, immutable URLs; use expo-image (Glide/SDWebImage).

**Hindi:**
1. Pipeline: memory cache → disk cache → dedupe network → background decode (छोटे आकार में) → दिखाओ अगर view को अभी वही चाहिए।
2. Memory = w × h × 4: CDN से सही आकार, view के आकार में decode, cache की bytes सीमा, memory चेतावनी पर ख़ाली।
3. तेज़ महसूस: blurhash, fixed आकार, prefetch, scroll से बाहर पर cancel, immutable URLs; expo-image।

---

## ➡️ Next Topic Suggestion
**M13. List Performance (FlatList vs FlashList)** — Images live inside long lists. Next: how FlatList virtualization and FlashList cell recycling work, and the techniques that keep 60 fps scrolling on low-end Android.
