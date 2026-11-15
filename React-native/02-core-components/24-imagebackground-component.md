# 24. ImageBackground Component
# हिंदी में: ImageBackground Component (Image के ऊपर Content)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). `ImageBackground` core RN component है।

---

## 🔵 Simple Definition (English)
`<ImageBackground>` shows an image as a background and lets you put children (text, buttons, views) on top of it. It accepts all `Image` props and works like a `View` that has an image behind its children.

## 🔵 सरल परिभाषा (Hindi)
`<ImageBackground>` एक image को background बनाता है और उसके ऊपर children (text, buttons, views) रखने देता है। यह सारे `Image` props लेता है और `View` की तरह काम करता है, बस पीछे image होती है।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ <Image> के अंदर children नहीं रख सकते (Image children नहीं लेता)
❌ Workaround: position:'absolute' से Image + View stack करना
❌ हर बार width/height और zIndex का झंझट
```

## 🔴 यह क्यों बना? (Hindi)
```
RN का <Image> children support नहीं करता।
Banner, hero section, login background में image के ऊपर text चाहिए।
ImageBackground यह stacking खुद कर देता है:
✅ कम code, कम bugs
✅ imageStyle से सिर्फ image की style
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → <ImageBackground source={...} style={...}> लिखो
Step 2 → अंदर RN एक container View बनाता है (style उसे मिलती है)
Step 3 → उसमें absolute-fill Image रखता है (imageStyle उसे मिलती है)
Step 4 → आपके children Image के ऊपर render होते हैं
Step 5 → resizeMode (cover/contain/stretch) तय करता है image कैसे fit हो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → source और style के साथ <ImageBackground> लगाओ
Step 2 → अंदर एक container View बनता है (style इसी की)
Step 3 → पीछे full-size Image लगती है (imageStyle इसी की)
Step 4 → आपके children Image के ऊपर दिखते हैं
Step 5 → resizeMode बताता है image कैसे fit होगी
```

---

## 🟡 Real World Example
**Swiggy** के home पर offer banner ("60% OFF up to ₹120") — पीछे food photo और ऊपर offer text। **Zomato** के restaurant page का hero image जिस पर restaurant name और rating लिखी होती है। **Paytm** की splash/login screen का gradient-photo background।

## 🟡 Real Example Hindi mein
Swiggy के banner में पीछे खाने की photo और ऊपर "60% OFF" लिखा होता है — यही `ImageBackground` है। Zomato के restaurant hero पर नाम और rating image के ऊपर दिखती है।

---

## 💻 Code Example — Basic
```jsx
// Basic ImageBackground — Android + iOS दोनों
import React from 'react';                                  // React
import { ImageBackground, Text, StyleSheet } from 'react-native'; // components

export default function Banner() {
  return (
    <ImageBackground
      // remote image: width/height देना ज़रूरी है (network image का size पता नहीं)
      source={{ uri: 'https://picsum.photos/600/300' }}
      resizeMode="cover"                 // image पूरी जगह भरे, crop हो सकती है
      style={styles.banner}              // container की style
      imageStyle={styles.image}          // सिर्फ image की style (rounded corners)
    >
      {/* image के ऊपर text */}
      <Text style={styles.offer}>60% OFF up to ₹120</Text>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  banner: { height: 160, justifyContent: 'flex-end', padding: 16, margin: 12 }, // नीचे text
  image: { borderRadius: 16 },           // corners round (style में borderRadius के साथ overflow भी चाहिए)
  offer: { color: '#fff', fontSize: 22, fontWeight: '800' }, // सफ़ेद text
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: loading/error fallback + dark overlay + local fallback + accessibility
import React, { useState } from 'react';
import { ImageBackground, View, Text, ActivityIndicator, StyleSheet, Platform } from 'react-native';

export default function RestaurantHero({ imageUrl, name, rating }) {
  const [loading, setLoading] = useState(true);   // image load हो रही है?
  const [failed, setFailed] = useState(false);    // load fail हुई?

  return (
    <ImageBackground
      // fail होने पर placeholder (local असली app में require('./placeholder.png'))
      source={failed ? { uri: 'https://picsum.photos/id/1/600/300' } : { uri: imageUrl }}
      style={styles.hero}
      imageStyle={styles.img}
      resizeMode="cover"
      onLoadEnd={() => setLoading(false)}          // load पूरा (success/fail दोनों)
      onError={() => setFailed(true)}              // error पर fallback
      accessibilityLabel={`${name} restaurant photo`} // screen reader
    >
      {/* dark overlay — ताकि सफ़ेद text साफ पढ़ा जाए */}
      <View style={styles.overlay} />

      {/* loader जब तक image आए */}
      {loading && <ActivityIndicator style={StyleSheet.absoluteFill} color="#fff" />}

      {/* नीचे info */}
      <View style={styles.info}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.rating}>⭐ {rating}</Text>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  hero: { height: 220, justifyContent: 'flex-end', backgroundColor: '#ddd' },
  img: { opacity: 1 },
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.35)' },
  info: { padding: 16 },
  name: { color: '#fff', fontSize: 24, fontWeight: '700' },
  rating: {
    color: '#ffd166',
    marginTop: 4,
    // iOS पर हल्का text shadow, Android पर भी चलता है
    ...Platform.select({ ios: { textShadowColor: '#000', textShadowRadius: 2 }, android: {} }),
  },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Rounded corners | `imageStyle={{borderRadius}}` काम करता है | ✅ वही |
| Network image caching | Fresco/OkHttp cache | NSURLCache (default) |
| `blurRadius` | ✅ support | ✅ support |
| GIF / WebP | GIF के लिए पहले gradle dependency चाहिए रही है | GIF native; animated WebP पर limits |
| Large image memory | OOM का risk ज़्यादा | अपेक्षाकृत बेहतर |
| Default resize | `cover` | `cover` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo में बेहतर caching/placeholder के लिए expo-image (separate package) भी option है
// npx expo install expo-image
import { Image } from 'expo-image';
import { StyleSheet, View, Text } from 'react-native';

export default function Hero() {
  return (
    <View style={{ height: 160 }}>
      {/* expo-image को absolute fill करके ऊपर children रखो (ImageBackground जैसा) */}
      <Image source="https://picsum.photos/600/300" style={StyleSheet.absoluteFill} contentFit="cover" />
      <Text style={{ color: '#fff' }}>Offer</Text>
    </View>
  );
}
```
CLI way:
```jsx
// CLI में core ImageBackground वही है, कोई extra setup नहीं
import { ImageBackground, Text } from 'react-native';
<ImageBackground source={require('./assets/bg.png')} style={{ height: 160 }}>
  <Text>Offer</Text>
</ImageBackground>
// Caching चाहिए तो react-native-fast-image (native link; pod install ज़रूरी)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Remote image पर height/width न देना → image दिखती ही नहीं
```jsx
<ImageBackground source={{ uri }}><Text>Hi</Text></ImageBackground>  // ❌ height 0 भी हो सकती है
```
✅ Correct: `style={{ height: 160 }}` (और width/flex) दो।

❌ Mistake 2: `borderRadius` को `style` में देना और image corners round न होना
✅ Correct: `imageStyle={{ borderRadius: 16 }}` का use करो (और style में भी borderRadius + `overflow:'hidden'`)।

❌ Mistake 3: Text के पीछे busy image में text पढ़ा न जाना
✅ Correct: अर्ध-पारदर्शी overlay View लगाओ।

---

## 🧠 Tricky Interview Question
**Q: `ImageBackground` और `Image` + `position: 'absolute'` में क्या फ़र्क है? और `<Image>` के अंदर children रखें तो क्या होगा?**

Answer: `ImageBackground` असल में इसी absolute stacking का wrapper है, यानी वही नतीजा, कम code। `<Image>` के अंदर children रखने पर वे **render नहीं होते** (Image children support नहीं करता, पुराने version में warning आता था)। इसलिए overlay content के लिए `ImageBackground` या absolute stacking use करो। `style` container पर लगती है, `imageStyle` image पर — यही अक्सर पूछा जाता है।

---

## ⚫ Interview Questions + Answers
Q1: `style` और `imageStyle` में क्या फ़र्क है?
A1: `style` बाहरी container View की है (size, padding, alignment); `imageStyle` अंदर की Image की (borderRadius, opacity, tintColor)।

Q2: `resizeMode` के options?
A2: `cover`, `contain`, `stretch`, `repeat` (iOS only), `center`।

Q3: Local और remote image में source कैसे अलग है?
A3: Local: `source={require('./bg.png')}` (size auto पता)। Remote: `source={{ uri }}` और style में size देना ज़रूरी।

Q4: Image load error कैसे संभालें?
A4: `onError` में state बदलकर fallback source दो; `onLoadEnd` से loader बंद करो।

Q5: बड़ी लिस्ट में ImageBackground का performance?
A5: हर item में बड़ी images memory खाती हैं। सही size की image, `expo-image`/FastImage caching, और `FlatList` virtualization use करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Banner, hero, splash/login background
- Image के ऊपर text/buttons चाहिए

❌ Avoid when:
- सिर्फ image दिखानी हो (`Image`)
- Advanced caching/blurhash चाहिए (`expo-image`)
- Gradient background (`expo-linear-gradient`)

---

## 📊 Visual Diagram
```
<ImageBackground style=container imageStyle=image>
┌────────────────────────────────┐ ← container View
│  [ Image (absolute fill) ]     │ ← पीछे की image
│   ┌────────────────────────┐   │
│   │  children (Text, View) │   │ ← ऊपर का content
│   └────────────────────────┘   │
└────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ImageBackground | Image with children on top | image के ऊपर children |
| imageStyle | Style for inner image | अंदर की image की style |
| resizeMode | How image fits | image कैसे fit होगी |
| Overlay | Semi-transparent layer | अर्ध-पारदर्शी परत |
| absoluteFill | Fill parent fully | parent को पूरा भरना |

---

## ⚡ 3-Line Summary
English:
1. `ImageBackground` = Image + children on top.
2. `style` is the container, `imageStyle` is the image.
3. Remote images need explicit size; add overlay for readable text.

Hindi:
1. `ImageBackground` = image के ऊपर children।
2. `style` container की, `imageStyle` image की।
3. Remote image में size दो; text पढ़ने के लिए overlay लगाओ।

---

## ➡️ Next Topic
**29. FlatList vs ScrollView vs SectionList** — कौन सा list component कब use करें।
