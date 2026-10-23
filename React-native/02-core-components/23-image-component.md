# 23. Image Component
# हिंदी में: Image Component क्या है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
The `Image` component in React Native displays images — from local files, network URLs, or Base64 data. Unlike web's `<img src="...">`, React Native Image requires the `source` prop with either `{ uri: '...' }` for remote/dynamic images or `require('./path')` for local bundled images. Always set explicit `width` and `height` — Image has no intrinsic size in React Native.

## 🔵 सरल परिभाषा (Hindi)
React Native का `Image` component images display करता है — local files, network URLs, या Base64 data से। Web के `<img src="...">` के unlike, React Native Image में `source` prop चाहिए: remote/dynamic images के लिए `{ uri: '...' }` और local files के लिए `require('./path')`। हमेशा explicit `width` और `height` set करो — React Native में Image का कोई intrinsic size नहीं होता।

---

## 🔴 Problem it Solves
```
WEB vs REACT NATIVE IMAGE:
Web:
  <img src="https://cdn.zomato.com/dish.jpg" />
  → Browser handles: size, loading, caching automatically
  → Image has intrinsic size (shows even without width/height)

React Native:
  <Image source={{ uri: 'https://cdn.zomato.com/dish.jpg' }} />
  ❌ Without width + height: image INVISIBLE (no intrinsic size!)
  ✅ Must specify: style={{ width: 200, height: 150 }}

WHY DIFFERENT?
  Native image views (UIImageView / ImageView) have no intrinsic size
  until the image loads — RN doesn't wait for load to calculate layout
  Solution: always specify dimensions
```

## 🔴 यह क्यों बना? (Hindi)
```
Web img: browser automatically size calculate करता है।
RN Image: native ImageView का intrinsic size नहीं होता।
इसलिए width + height always required — वरना image invisible!
```

---

## 🟢 How it Works — Step by Step

```
LOCAL IMAGE (bundled in app):
──────────────────────────────────────────────────────
  Step 1 → require('./assets/logo.png')
            Metro bundler detects this at build time
  Step 2 → Metro copies image into the bundle
  Step 3 → At runtime, image loaded from app's bundle
  Step 4 → ImageView renders image immediately (no network!)
  Fast, reliable, works offline ✅

NETWORK IMAGE:
──────────────────────────────────────────────────────
  Step 1 → { uri: 'https://cdn.swiggy.com/dish.jpg' }
  Step 2 → React Native's image loading mechanism:
           - Check native cache first
           - If not cached: start HTTP request
           - Download on background thread
  Step 3 → onLoadStart callback fires
  Step 4 → Download completes
  Step 5 → onLoad callback fires, image appears
  Step 6 → Image cached natively (for future loads)

CACHING:
  Android: 4 hours default (uses OkHttp cache)
  iOS: NSURLCache (system cache)
  Custom: use react-native-fast-image for LRU cache control
```

## 🟢 कैसे काम करता है? (Hindi)
```
Local: require() → Metro bundle में include → fast, offline
Network: uri → native cache check → HTTP download → onLoad → display
Fast Image library: LRU cache, progressive loading, better control
```

---

## 🟡 Real World Example
**Zomato Restaurant Cards:** Every restaurant card shows a food image from CDN. Zomato uses `react-native-fast-image` (not the default Image) because: (1) prioritizing loading of visible images above the fold. (2) LRU cache so the same dish photo doesn't re-download as you scroll back up. (3) Progressive JPEG loading — shows blurry image first, sharpens as it loads. (4) Placeholder while loading — prevents layout shift.

## 🟡 Real Example Hindi मे
**Zomato Restaurant Cards:** CDN से dish images। Zomato `react-native-fast-image` use करता है: LRU cache (scroll back → no re-download), priority loading (visible images पहले), progressive loading (blurry → sharp), placeholder (layout shift रोके)।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';
import { Image, View, StyleSheet, Text } from 'react-native';

function ImageExamples() {
  return (
    <View style={styles.container}>

      {/* LOCAL IMAGE — bundled with app */}
      <Image
        source={require('./assets/logo.png')}  // ← require for local files
        style={styles.localImage}
        resizeMode="contain"                   // contain: fit within bounds
      />

      {/* NETWORK IMAGE — from URL */}
      <Image
        source={{ uri: 'https://picsum.photos/200/150' }}  // ← { uri } for network
        style={styles.networkImage}
        resizeMode="cover"                     // cover: fill entire space (may crop)
        onLoad={() => console.log('Image loaded!')}
        onError={(e) => console.log('Image failed:', e.nativeEvent.error)}
      />

      {/* BASE64 IMAGE — inline data */}
      <Image
        source={{ uri: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...' }}
        style={styles.localImage}
      />

    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', padding: 20, gap: 16 },
  localImage: {
    width: 150,
    height: 150,           // REQUIRED — no intrinsic size!
    borderRadius: 12,
  },
  networkImage: {
    width: 200,
    height: 150,           // REQUIRED — no intrinsic size!
    borderRadius: 8,
  },
});

// resizeMode values:
// 'cover'   → fill space, crop if needed (like CSS background-size: cover)
// 'contain' → fit inside bounds, no crop (like CSS object-fit: contain)
// 'stretch' → stretch to fill exactly (may distort aspect ratio)
// 'repeat'  → tile the image (like CSS background-repeat: repeat)
// 'center'  → show at original size, centered
```

## 💻 Code Example — Advanced

```jsx
import React, { useState } from 'react';
import { Image, View, ActivityIndicator, StyleSheet, Text } from 'react-native';

// PATTERN: Image with loading state + error fallback
function SmartImage({ uri, fallbackUri, width, height }) {
  const [loading, setLoading] = useState(true);  // loading state
  const [error, setError] = useState(false);     // error state

  const imageSource = error
    ? { uri: fallbackUri }         // show fallback on error
    : { uri };                     // show actual image

  return (
    <View style={[styles.wrapper, { width, height }]}>
      <Image
        source={imageSource}
        style={[styles.image, { width, height }]}
        resizeMode="cover"
        onLoadStart={() => setLoading(true)}  // starts loading
        onLoad={() => setLoading(false)}       // loaded successfully
        onError={() => {
          setLoading(false);
          setError(true);                     // switch to fallback
        }}
      />
      {/* Show spinner while loading */}
      {loading && (
        <View style={styles.loader}>
          <ActivityIndicator size="small" color="#f97316" />
        </View>
      )}
    </View>
  );
}

// REAL WORLD: Zomato-style dish card
function DishCard({ dish }) {
  return (
    <View style={styles.card}>
      <SmartImage
        uri={`https://cdn.zomato.com/dish/${dish.id}.jpg`}
        fallbackUri="https://cdn.zomato.com/placeholder-dish.jpg"
        width="100%"
        height={200}
      />
      <View style={styles.info}>
        <Text style={styles.name}>{dish.name}</Text>
        <Text style={styles.price}>₹{dish.price}</Text>
      </View>
    </View>
  );
}

// PATTERN: Image with known aspect ratio (dynamic height)
function AspectRatioImage({ uri, aspectRatio = 16 / 9 }) {
  return (
    <Image
      source={{ uri }}
      style={{
        width: '100%',
        aspectRatio,          // height calculated from width automatically!
        borderRadius: 8,
      }}
      resizeMode="cover"
    />
  );
  // aspectRatio: 16/9 = 1.777, 4/3 = 1.333, 1/1 = square
}

const styles = StyleSheet.create({
  wrapper: {
    position: 'relative',
    backgroundColor: '#f5f5f5',   // shows while image loads
    borderRadius: 8,
    overflow: 'hidden',
  },
  image: { position: 'absolute', top: 0, left: 0 },
  loader: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    justifyContent: 'center', alignItems: 'center',
  },
  card: { borderRadius: 12, overflow: 'hidden', backgroundColor: '#fff', margin: 8 },
  info: { padding: 12 },
  name: { fontSize: 16, fontWeight: '700' },
  price: { fontSize: 14, color: '#f97316', marginTop: 4 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default caching | OkHttp (4 hours) | NSURLCache (system) |
| GIF support | ✅ (needs Fresco) | ✅ built-in |
| WebP support | ✅ native | ✅ iOS 14+ |
| Blur effect | `blurRadius` prop | `blurRadius` prop (GPU optimized) |
| Cache control | Limited (use FastImage) | Limited (use FastImage) |

---

## 🟠 Expo vs CLI Difference

Expo way:
```jsx
// expo-image: much better than RN's Image
import { Image } from 'expo-image';  // npm install expo-image

<Image
  source="https://cdn.swiggy.com/dish.jpg"
  style={{ width: 200, height: 150 }}
  placeholder={{ uri: 'https://cdn.swiggy.com/blur.jpg' }}
  contentFit="cover"          // instead of resizeMode
  transition={300}            // fade-in transition ms
  cachePolicy="memory-disk"   // explicit caching
/>
// expo-image: faster, better caching, blurhash placeholder, transition
```

CLI way:
```jsx
// react-native-fast-image: popular alternative for CLI
import FastImage from 'react-native-fast-image';

<FastImage
  source={{
    uri: 'https://cdn.swiggy.com/dish.jpg',
    priority: FastImage.priority.high,   // load this first!
  }}
  style={{ width: 200, height: 150 }}
  resizeMode={FastImage.resizeMode.cover}
/>
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting width and height for network images
```jsx
// WRONG: Image is INVISIBLE!
<Image source={{ uri: 'https://example.com/photo.jpg' }} />

// CORRECT: Always specify dimensions
<Image
  source={{ uri: 'https://example.com/photo.jpg' }}
  style={{ width: 200, height: 150 }}  // required!
/>

// Or use aspectRatio:
<Image
  source={{ uri: 'https://example.com/photo.jpg' }}
  style={{ width: '100%', aspectRatio: 16/9 }}  // also works!
/>
```

❌ **Mistake 2:** Not handling loading and error states
```jsx
// WRONG: Image just disappears on error, no feedback
<Image source={{ uri: brokenUrl }} style={styles.image} />

// CORRECT: Handle both states
<Image
  source={{ uri: brokenUrl }}
  style={styles.image}
  defaultSource={require('./placeholder.png')}  // iOS: shows while loading
  onError={() => setImageError(true)}
/>
```

❌ **Mistake 3:** Using require() with dynamic paths
```jsx
// WRONG: Metro can't resolve dynamic require at build time!
const filename = 'logo';
<Image source={require(`./${filename}.png`)} />  // ❌ Metro error!

// CORRECT: Static require paths only
<Image source={require('./logo.png')} />         // ✅

// For dynamic images: use uri (network or local file path)
<Image source={{ uri: `${ASSETS_BASE}/${filename}.png` }} />  // ✅
```

---

## 🧠 Tricky Interview Question

**Q: What is the difference between `resizeMode="cover"` and `resizeMode="contain"`? And what does `overflow: 'hidden'` on the parent do?**

**Answer:** `cover`: image fills the entire space (like CSS `object-fit: cover` or `background-size: cover`). If the image aspect ratio differs from the container, the image is cropped on the edges that extend beyond the container bounds. `contain`: image fits entirely within the container, showing the full image without cropping. Letterboxing (empty space) appears if aspect ratios don't match. **The gotcha**: resizeMode clips the rendered pixels but the Image component itself doesn't clip its bounds by default. If you have `borderRadius` on the Image and the image extends beyond the border radius curves, you'll see the image peeking outside the rounded corners. Fix: add `overflow: 'hidden'` to the parent `<View>` with the same `borderRadius`. This is a common visual bug in production apps.

---

## ⚫ Interview Questions + Answers

**Q1: How do you display a local image vs a network image in React Native?**
A1: Local: `<Image source={require('./assets/logo.png')} style={{width: 100, height: 100}} />` — Metro bundles the file at build time. Network: `<Image source={{ uri: 'https://...' }} style={{width: 100, height: 100}} />` — loaded at runtime. Critical difference: local images must have static `require()` paths (Metro can't resolve dynamic paths at build time). Both need explicit `width` and `height` — network images especially, as they have no intrinsic size before loading.

**Q2: Why would an Image be invisible even though the source is set correctly?**
A2: Most common reason: missing `width` and `height`. React Native Image components have no intrinsic size — unlike web browsers that calculate size from image metadata. Without explicit dimensions (via `style={{ width, height }}`), the image renders at 0x0 and is invisible. Fix: set explicit dimensions or use `aspectRatio` with a width. Second reason: `resizeMode="contain"` on an image with wrong aspect ratio in a tiny container — image exists but renders at a tiny size.

**Q3: What is `react-native-fast-image` and why is it used instead of the built-in Image?**
A3: `react-native-fast-image` wraps Glide (Android) and SDWebImage (iOS) — industry-standard image caching libraries. Advantages: (1) Proper LRU memory + disk cache (same image never re-downloaded in same session). (2) `priority` prop — high-priority images load first (above-fold images). (3) `preload()` to pre-cache images before they're needed. (4) Better placeholder support. The built-in RN Image has basic caching but less control. For apps with many images (Zomato, Myntra), Fast Image significantly improves scroll performance.

**Q4: How do you handle image loading states?**
A4: Use `onLoadStart`, `onLoad`, `onError` callbacks. Track loading/error state: `onLoadStart` → set loading=true, `onLoad` → set loading=false, `onError` → set error=true (show fallback). Show `<ActivityIndicator>` or a skeleton placeholder while loading. Use `defaultSource` (iOS only) for a static local placeholder. Or use `expo-image` which has built-in `placeholder` and `transition` props for smooth fade-in.

**Q5: What is `aspectRatio` in React Native StyleSheet?**
A5: `aspectRatio` is a number representing `width / height`. When combined with a flex width (e.g., `width: '100%'`), React Native automatically calculates height to maintain the ratio. `aspectRatio: 16/9` ≈ 1.78 means for every 16 units wide, height is 9 units. Very useful for responsive image display: `style={{ width: '100%', aspectRatio: 16/9 }}` — image is always full-width with 16:9 ratio regardless of screen size. Eliminates the need to calculate height from `Dimensions.get('window').width`.

---

## 🔷 When to Use + When Not to Use
✅ **Use `<Image>` when:**
- Displaying product images, avatars, icons, banners
- Static local assets bundled with app
- Network images with loading/error handling

✅ **Use `expo-image` or `react-native-fast-image` when:**
- FlatList with many images (scroll performance)
- Image priority loading needed
- Better cache control required
- Transition/fade effects needed

❌ **Don't forget:**
- Always width + height
- Always onError fallback for network images
- overflow: hidden when using borderRadius

---

## 📊 Visual Diagram

```
resizeMode VISUAL:
──────────────────────────────────────────────────────
  Container:  ┌──────────────┐   Image aspect: 16:9
              │              │   Container: square (1:1)
              │              │
              └──────────────┘

  cover:      ┌──────────────┐   Image fills, edges CROPPED
              │████████████  │   ← cropped sides
              │████████████  │
              └──────────────┘

  contain:    ┌──────────────┐   Full image fits, EMPTY BARS
              │              │   ← empty top/bottom
              │████████████  │
              │              │
              └──────────────┘

  stretch:    ┌──────────────┐   Image DISTORTED to fill
              │████████████  │   aspect ratio changed
              │████████████  │
              └──────────────┘

SOURCE TYPES:
──────────────────────────────────────────────────────
  require('./img.png')     → local bundle (Metro includes at build)
  { uri: 'https://...' }   → network (download at runtime)
  { uri: 'data:...' }      → Base64 inline data
  { uri: 'file://...' }    → local filesystem (camera output, etc.)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| source | Image source prop (require or uri) | Image का source |
| resizeMode | How image fills container | Image container को कैसे fill करे |
| cover | Fill + crop | Fill करे + crop |
| contain | Fit + letterbox | Fit करे + letterbox |
| aspectRatio | Width/height ratio | Width/height ratio |
| defaultSource | Placeholder (iOS only) | iOS के लिए placeholder |
| Fast Image | Library with better caching | Better caching वाली library |
| onLoad | Callback when image loads | Image load होने पर callback |

---

## ⚡ 3-Line Summary
**English:**
1. `Image` displays local (require) or network ({uri}) images — always set explicit width + height, or image is invisible (no intrinsic size in RN).
2. Use `resizeMode="cover"` to fill/crop, `"contain"` to show full image; add `overflow: 'hidden'` to parent for borderRadius to work correctly.
3. For production FlatLists with many images, use `expo-image` (Expo) or `react-native-fast-image` (CLI) for proper LRU caching and priority loading.

**Hindi:**
1. `Image` local (require) या network ({uri}) images दिखाता है — हमेशा explicit width + height set करो, वरना invisible (RN में intrinsic size नहीं)।
2. `resizeMode="cover"` fill+crop के लिए, `"contain"` पूरी image के लिए; borderRadius के साथ parent पर `overflow: 'hidden'` add करो।
3. Production FlatLists में `expo-image` या `react-native-fast-image` use करो — proper LRU caching और priority loading के लिए।

---

## ➡️ Next Topic
**25. TextInput Component** — forms, keyboard handling, controlled inputs।
