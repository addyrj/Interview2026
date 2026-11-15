# 164. Image Optimization
# हिंदी में: Image Optimization (Images को हल्का और तेज़ बनाना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76, `expo-image` (SDK 52 में stable)। Props जैसे `contentFit`, `placeholder` (blurhash), `cachePolicy`, `transition` `expo-image` के हैं — नए SDK में docs जाँचो।

---

## 🔵 Simple Definition (English)
**Image optimization** means showing images with the smallest file size and memory that still look good: right dimensions, modern format (WebP/AVIF), caching, placeholders and lazy loading. Images are usually the biggest cause of memory crashes and slow screens.

## 🔵 सरल परिभाषा (Hindi)
**Image optimization** का मतलब है images को कम से कम file size और memory में दिखाना जो फिर भी अच्छी दिखें: सही size, modern format (WebP/AVIF), caching, placeholder और lazy loading। ज़्यादातर memory crash और slow screens का सबसे बड़ा कारण images ही होती हैं।

---

## 🔴 Problem it Solves
```
4000x3000 JPEG (5 MB) को 100x100 thumbnail में दिखाओ:
  Decoded memory = 4000 × 3000 × 4 bytes ≈ 48 MB (!!) एक image के लिए
  20 ऐसी images = 960 MB → Out Of Memory crash (खासकर Android)

अन्य समस्याएँ:
  ❌ हर बार network से दोबारा download (cache नहीं)
  ❌ Image आने पर layout उछलना (size पता नहीं)
  ❌ सफ़ेद खाली जगह जब तक image load हो
```

## 🔴 यह क्यों बना? (Hindi)
```
4000x3000 की 5 MB image को 100x100 में दिखाओ तो decode होकर ≈ 48 MB RAM।
20 ऐसी images = लगभग 1 GB → crash।
साथ ही बिना cache हर बार download, layout jump और खाली सफ़ेद जगह।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Server/CDN से सही size माँगो (?w=300) — बड़ी image भेजो ही मत
Step 2 → WebP/AVIF format (JPEG/PNG से छोटा)
Step 3 → width/height हमेशा style में दो (layout stable)
Step 4 → Cache: expo-image (disk+memory) / FastImage / RN का cache prop
Step 5 → Placeholder: blurhash/thumbhash या छोटा low-res
Step 6 → Lists में: छोटी thumbnails, lazy load; बड़ी image सिर्फ detail screen में
Step 7 → Local assets: build से पहले compress (tinypng/squoosh), @2x/@3x
Step 8 → Prefetch: अगली screen की image पहले load करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CDN से सही size माँगो (?w=300)
Step 2 → WebP/AVIF format इस्तेमाल करो
Step 3 → style में width/height दो
Step 4 → Cache: expo-image (disk + memory)
Step 5 → Placeholder: blurhash
Step 6 → List में छोटी thumbnails, detail में बड़ी
Step 7 → Local images को build से पहले compress करो
Step 8 → अगली screen की image prefetch करो
```

---

## 🟡 Real World Example
**Swiggy/Zomato** restaurant cards में photo की URL में width parameter होता है (जैसे 300px) और अलग thumbnail/blur placeholder। **Flipkart/Amazon** product grids में हर item की WebP thumbnail आती है; बड़ी image सिर्फ product detail खोलने पर। इससे data (मोबाइल पर महँगा) और RAM दोनों बचते हैं।

## 🟡 Real Example Hindi mein
**Swiggy/Zomato** cards में photo URL में छोटी width (जैसे 300px) और blur placeholder होता है। **Flipkart/Amazon** grids में छोटी WebP thumbnails; बड़ी image सिर्फ detail page पर। इससे mobile data और RAM दोनों बचते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: expo-image से cached, placeholder वाली image
// Install: npx expo install expo-image
import React from 'react';                                           // React
import { View, StyleSheet } from 'react-native';                     // layout
import { Image } from 'expo-image';                                  // तेज़, cached Image component

// blurhash: एक छोटा string जो blurry preview बनाता है (किसी blurhash generator से बनाओ)
const blurhash = 'L6PZfSi_.AyE_3t7t7R**0o#DgR4';

export default function Thumb() {
  return (
    <View style={styles.box}>
      <Image
        source={{ uri: 'https://picsum.photos/300/300' }}            // 300px image (demo URL)
        style={styles.img}                                           // width/height ज़रूरी
        contentFit="cover"                                           // resizeMode जैसा (cover/contain)
        placeholder={{ blurhash }}                                   // load होने तक blur
        transition={200}                                             // fade-in 200ms
        cachePolicy="memory-disk"                                    // disk + memory cache
      />
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 16 },                                              // बाहर की जगह
  img: { width: 120, height: 120, borderRadius: 12 },                // fixed size
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: CDN resize helper, devicePixelRatio, prefetch और fallback
import React, { useMemo, useState } from 'react';
import { PixelRatio, View, Text, Platform, StyleSheet } from 'react-native';
import { Image } from 'expo-image';

// CDN को सही size माँगने वाला helper (URL का format आपके CDN पर निर्भर: Cloudinary/Imgix आदि)
function cdn(url, dpWidth) {
  const px = Math.round(PixelRatio.getPixelSizeForLayoutSize(dpWidth)); // dp → असली pixels
  const w = Math.min(px, 1080);                                      // ऊपरी सीमा
  return `${url}?w=${w}&fm=webp&q=75`;                               // काल्पनिक query: अपने CDN के docs देखो
}

export function RestaurantImage({ url, size = 140 }) {
  const [failed, setFailed] = useState(false);                       // error state
  const src = useMemo(() => ({ uri: cdn(url, size) }), [url, size]); // stable source object

  if (failed) {                                                      // fallback UI
    return <View style={[styles.img, styles.fallback, { width: size, height: size }]}><Text>🍽️</Text></View>;
  }
  return (
    <Image
      source={src}
      style={{ width: size, height: size, borderRadius: 12 }}
      contentFit="cover"
      transition={150}
      recyclingKey={url}                                             // expo-image: list recycling में सही image
      onError={() => setFailed(true)}                                // fail पर fallback
      cachePolicy="memory-disk"
    />
  );
}

// अगली screen के लिए पहले से download (SDK 52 में Image.prefetch उपलब्ध — docs जाँचो)
export function warm(urls) {
  return Image.prefetch(urls);                                       // cache में डाल देता है
}

const styles = StyleSheet.create({
  img: { borderRadius: 12 },
  fallback: { backgroundColor: '#eee', alignItems: 'center', justifyContent: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default RN `<Image>` cache | OS/Fresco आधारित | `cache` prop (`default`, `force-cache`, `only-if-cached`) iOS only |
| Memory risk | ज़्यादा (bitmap RAM, छोटी heap) | कम |
| Fade-in | `fadeDuration` prop (Android only) | अपना transition |
| WebP | पूर्ण support | iOS 14+ में support |
| AVIF | Android 12+ | iOS 16+ |
| GIF/animated | Fresco से | अलग handling |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-image
import { Image } from 'expo-image';
<Image source={{ uri }} style={{ width: 100, height: 100 }} contentFit="cover" cachePolicy="memory-disk" />
```
CLI way:
```jsx
// npm i react-native-fast-image (या expo-image भी bare में चलता है, expo modules के साथ)
// cd ios && pod install
import FastImage from 'react-native-fast-image';
<FastImage source={{ uri, priority: FastImage.priority.normal }} style={{ width: 100, height: 100 }} resizeMode="cover" />
```
FastImage का maintenance सक्रिय है या नहीं, यह repo में जाँचो; नई अपनाने से पहले expo-image देखो।

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Remote `<Image>` में width/height न देना।
✅ Correct: Network images को हमेशा explicit size दो (वरना 0×0 दिखेगी)।

❌ Mistake 2: 4000px image को thumbnail में दिखाना।
✅ Correct: CDN resize, या upload पर कई sizes बनाओ।

❌ Mistake 3: List में हर बार नया `source={{ uri }}` object।
✅ Correct: `useMemo`, या `expo-image` जो खुद URL से cache करता है।

❌ Mistake 4: PNG फ़ोटो के लिए।
✅ Correct: Photos → WebP/JPEG; PNG सिर्फ transparency/icons के लिए।

❌ Mistake 5: Icons के लिए बड़ी PNG।
✅ Correct: SVG (react-native-svg) या icon font।

---

## 🧠 Tricky Interview Question
"Image फ़ाइल सिर्फ 200 KB है, फिर भी 30 ऐसी images वाली screen पर Android पर OOM crash क्यों?"

Answer: File size (compressed) और memory size अलग हैं। Decode होकर हर pixel ≈ 4 bytes लेता है। 200 KB की 4000×3000 JPEG decode होकर ≈ 48 MB बनती है; 30 × 48 MB ≈ 1.4 GB। Fix: सही resolution की image लो (display size × pixel ratio), thumbnails इस्तेमाल करो, और list virtualization रखो।

---

## ⚫ Interview Questions + Answers
Q1: RN के `<Image>` और `expo-image` में क्या अंतर?
A1: `expo-image` में बेहतर disk/memory caching, blurhash placeholders, transitions, AVIF/WebP/SVG support और recycling है; core Image में ये सीमित हैं।

Q2: Blurhash क्या है?
A2: छोटा string (~20-30 chars) जिससे client एक blurry preview बना देता है जब तक असली image लोड हो।

Q3: `resizeMode`/`contentFit` क्या करता है?
A3: Image को box में कैसे fit करें: cover (भरो+crop), contain (पूरी दिखे), stretch आदि।

Q4: Lazy loading कैसे?
A4: FlatList virtualization से सिर्फ visible rows की images load होती हैं; बाकी prefetch/placeholder।

Q5: Memory कैसे घटाएँ?
A5: सही resolution, CDN resize, WebP, कम concurrent images, `windowSize` घटाना, पुरानी images का cache clear (`Image.clearMemoryCache`)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Feeds, grids, product lists
- Slow networks / सस्ते devices

❌ Avoid when:
- 2-3 static icons (साधारण `require` ठीक)
- Resize-on-the-fly का server न हो तो ख़ुद pre-generate करो

---

## 📊 Visual Diagram
```
 Original 4000x3000 (5MB) ──CDN resize──► 300x300 WebP (20KB)
        │                                      │
 Decode: ~48MB RAM                      Decode: ~0.36MB RAM
        ▼                                      ▼
     ❌ OOM risk                          ✅ smooth
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebP/AVIF | Modern compressed formats | आधुनिक compressed formats |
| Blurhash | Tiny string for blur preview | धुंधला preview बनाने वाला छोटा string |
| Prefetch | Download before needed | पहले से download |
| Decode | Convert file to pixels | File से pixels बनाना |
| CDN | Servers close to users | उपयोगकर्ता के पास के servers |

---

## ⚡ 3-Line Summary
English: Use correctly sized WebP images from a CDN, cache them and show placeholders. Decoded memory matters more than file size. expo-image is the modern default.
Hindi: CDN से सही size की WebP images लो, cache करो और placeholder दिखाओ। File size से ज़्यादा decoded memory मायने रखती है। expo-image आधुनिक default है।

---

## ➡️ Next Topic
**165. Hermes Engine Benefits** — JS चलाने वाला engine, startup और memory की जीत।
