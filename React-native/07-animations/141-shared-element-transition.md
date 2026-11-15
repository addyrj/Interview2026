# 141. Shared Element Transition
# हिंदी में: Shared Element Transition — दो screens के बीच common element का animation
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76, react-native-reanimated 3.16.x. Shared Element Transition Reanimated में **experimental / feature-flag** के पीछे है (`sharedTransitionTag`, `SharedTransition`) और **New Architecture (Fabric) + native-stack** पर ही चलता है। हर SDK में behaviour बदल सकता है — docs देखो।

---

## 🔵 Simple Definition (English)
A **Shared Element Transition** makes one element (like a product photo) appear to *fly* from the first screen to its new position on the second screen. The same image is "shared" between both screens, so the user feels continuity instead of a hard cut.

## 🔵 सरल परिभाषा (Hindi)
**Shared Element Transition** में एक element (जैसे product की photo) पहली screen से उड़कर दूसरी screen की नई जगह पर पहुँचता दिखता है। दोनों screens में वही image "share" होती है, इसलिए user को jump के बजाय smooth continuity महसूस होती है।

---

## 🔴 Problem it Solves
```
WITHOUT SHARED ELEMENT:
  List screen → tap on photo → Detail screen appears (sudden cut)
  User सोचता है: "मैंने कौन सा item खोला?" — context टूट जाता है

WITH SHARED ELEMENT:
  Thumbnail grow होकर hero image बनता है
  ✅ Visual continuity
  ✅ User की eyes को guide करता है
  ✅ App premium लगता है
```

## 🔴 यह क्यों बना? (Hindi)
```
Normal navigation में screen अचानक बदल जाती है।
Shared element से thumbnail ही बड़ा होकर detail image बन जाता है।
इससे context बना रहता है और app polished लगता है।
Material Design और iOS Hero animation दोनों इसी idea पर हैं।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → दोनों screens में same element पर SAME tag लगाओ
          (sharedTransitionTag="product-42")
Step 2 → User navigate करता है (stack.push)
Step 3 → Reanimated पुराने element की position/size measure करता है
Step 4 → नई screen mount होती है, उसी tag वाला element ढूँढा जाता है
Step 5 → Reanimated पुरानी frame से नई frame तक animate करता है
          (position + size + (optionally) borderRadius, opacity)
Step 6 → Back करने पर reverse animation चलता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. दोनों screens के element को एक ही tag दो।
2. Navigate होने पर Reanimated पुराने element का size और position नापता है।
3. नई screen में वही tag वाला element ढूँढता है।
4. बीच का रास्ता animate करता है (UI thread पर, smooth)।
5. Back करने पर reverse animation।
```

---

## 🟡 Real World Example
**Swiggy / Zomato:** Restaurant list में dish की photo पर tap करते ही वही photo बड़ी होकर detail screen के header में बदल जाती है। **Myntra:** product card की image hero बन जाती है। **Spotify:** album art mini-player से full player में shared element की तरह बढ़ता है। यह वही pattern है जो iOS में "Hero / matchedGeometry" और Android में "Material container transform" कहलाता है।

## 🟡 Real Example Hindi mein
**Swiggy:** dish की छोटी photo पर tap → वही photo बड़ी होकर detail screen के top पर बैठ जाती है। **Myntra:** product card की image detail header बन जाती है। इसी से user को लगता है कि वह *उसी* item को खोल रहा है।

---

## 💻 Code Example — Basic

```jsx
// screens.jsx — Basic shared element (Reanimated 3, native-stack)
import React from 'react';                                  // React import
import { View, Text, Pressable, StyleSheet } from 'react-native'; // core UI
import Animated from 'react-native-reanimated';             // Animated.Image/View
import { NavigationContainer } from '@react-navigation/native';   // root container
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // native stack

const Stack = createNativeStackNavigator();                 // stack navigator instance

const IMG = 'https://picsum.photos/id/292/600/400';         // demo image URL

function ListScreen({ navigation }) {                       // first screen
  return (
    <View style={styles.center}>                            {/* centered container */}
      <Pressable onPress={() => navigation.navigate('Detail')}> {/* tap → go to Detail */}
        <Animated.Image
          source={{ uri: IMG }}                             // thumbnail source
          sharedTransitionTag="dish-1"                      // SAME tag on both screens
          style={styles.thumb}                              // small size
        />
      </Pressable>
      <Text>Tap the photo</Text>                            {/* hint */}
    </View>
  );
}

function DetailScreen() {                                   // second screen
  return (
    <View style={styles.full}>                              {/* full width container */}
      <Animated.Image
        source={{ uri: IMG }}                               // same image
        sharedTransitionTag="dish-1"                        // matching tag → animates!
        style={styles.hero}                                 // big size
      />
      <Text style={styles.title}>Butter Chicken</Text>      {/* title */}
    </View>
  );
}

export default function App() {                             // root
  return (
    <NavigationContainer>                                   {/* navigation context */}
      <Stack.Navigator>                                     {/* native stack */}
        <Stack.Screen name="List" component={ListScreen} /> {/* screen 1 */}
        <Stack.Screen name="Detail" component={DetailScreen} /> {/* screen 2 */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // center
  full: { flex: 1 },                                         // fill screen
  thumb: { width: 100, height: 100, borderRadius: 12 },      // small rounded
  hero: { width: '100%', height: 260 },                      // large header
  title: { fontSize: 22, fontWeight: '700', padding: 16 },   // text style
});
```

## 💻 Code Example — Advanced

```jsx
// advanced.jsx — custom transition + Platform fallback + reduced motion
import React from 'react';                                   // React
import { Platform, AccessibilityInfo, View, Text, Pressable } from 'react-native'; // RN APIs
import Animated, { SharedTransition, withSpring } from 'react-native-reanimated'; // Reanimated

// Custom transition: spring instead of default timing
const springTransition = SharedTransition.custom((values) => {
  'worklet';                                                  // runs on UI thread
  return {
    height: withSpring(values.targetHeight),                  // animate height
    width: withSpring(values.targetWidth),                    // animate width
    originX: withSpring(values.targetOriginX),                // animate x
    originY: withSpring(values.targetOriginY),                // animate y
  };
});

export function DishCard({ dish, navigation }) {              // list item
  const [reduceMotion, setReduceMotion] = React.useState(false); // a11y flag

  React.useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled()                 // user prefers less motion?
      .then(setReduceMotion)                                  // store the answer
      .catch(() => setReduceMotion(false));                   // error → assume false
  }, []);

  // Tag only when allowed — fallback = ordinary navigation
  const tag = reduceMotion ? undefined : `dish-${dish.id}`;   // unique tag per item

  return (
    <Pressable onPress={() => navigation.navigate('Detail', { dish })}> {/* go detail */}
      <Animated.Image
        source={{ uri: dish.image }}                          // image
        sharedTransitionTag={tag}                             // unique per item (NOT same for all!)
        sharedTransitionStyle={springTransition}              // custom spring
        style={{ width: 96, height: 96, borderRadius: 10 }}   // thumb style
      />
      <Text>{dish.name}</Text>                                {/* dish name */}
    </Pressable>
  );
}
// NOTE: Android पर native-stack + New Architecture चाहिए; unsupported होने पर
// tag ignore हो जाता है और normal transition चलता है। Behaviour SDK-version dependent है.
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Support | Reanimated 3 में experimental, New Arch चाहिए | Reanimated 3 में experimental, New Arch चाहिए |
| Native alternative | Material "container transform" (native module जरूरी) | UIKit hero / matched geometry (native) |
| Default navigation transition | slide/fade (device पर निर्भर) | slide from right |
| Back gesture + shared element | Predictive back में glitch संभव | Swipe-back interactive, कभी-कभी glitch |
| Performance | Low-end devices पर frame drop संभव | आम तौर पर smooth |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo — Expo Go में Reanimated included होता है, पर shared transition
// के लिए development build (npx expo run:android / eas build) बेहतर है
// npx expo install react-native-reanimated
// babel.config.js: plugins: ['react-native-reanimated/plugin']  // last plugin
```
CLI way:
```jsx
// Bare RN CLI
// npm i react-native-reanimated
// babel.config.js में plugin जोड़ो, फिर:
// cd ios && pod install
// New Architecture enable करो (android/gradle.properties: newArchEnabled=true)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: सभी list items पर एक ही tag (`"image"`) लगा देना।
✅ Correct: हर item का unique tag — `` `dish-${id}` ``।

❌ Mistake 2: Normal `Image` पर `sharedTransitionTag` लगाना।
✅ Correct: `Animated.Image` / `Animated.View` use करो।

❌ Mistake 3: JS-based `@react-navigation/stack` में expect करना।
✅ Correct: `@react-navigation/native-stack` use करो (docs देखो)।

❌ Mistake 4: Babel plugin न जोड़ना या last में न रखना।
✅ Correct: `'react-native-reanimated/plugin'` हमेशा plugins array में आखिरी, फिर cache clear (`npx expo start -c`)।

---

## 🧠 Tricky Interview Question
List में 50 items हैं और सब पर `sharedTransitionTag="photo"` है। Detail में भी `"photo"`। क्या होगा?

Answer: Tag unique होना चाहिए। Same tag वाले कई elements होने पर Reanimated को पता नहीं कौन सा source है; animation गलत element से शुरू हो सकता है या टूट सकता है। हर item को `photo-${id}` जैसा unique tag दो।

---

## ⚫ Interview Questions + Answers
Q1: Shared element transition क्या है?
A1: दो screens के बीच एक ही visual element का position/size animate होना, ताकि visual continuity बने।

Q2: Reanimated में यह कैसे enable होता है?
A2: `Animated.View/Image` पर दोनों screens में same `sharedTransitionTag`। यह feature experimental है, New Architecture और native-stack पर depend करता है।

Q3: Custom animation कैसे दें?
A3: `SharedTransition.custom((values) => { 'worklet'; return {...} })` और `sharedTransitionStyle` prop।

Q4: Reduced-motion users के लिए क्या करें?
A4: `AccessibilityInfo.isReduceMotionEnabled()` check करके tag हटा दो ताकि सामान्य transition चले।

Q5: Alternative क्या है अगर experimental feature stable नहीं?
A5: Manual approach: `measure()` से position लेकर overlay पर clone animate करना, या `react-native-shared-element` library।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- List → Detail में image/card का clear मेल हो
- Premium feel चाहिए (e-commerce, food, music)

❌ Avoid when:
- Low-end Android targets और 100s items की list
- Expo Go/old architecture पर stable behaviour चाहिए
- Production में experimental API का risk नहीं ले सकते

---

## 📊 Visual Diagram
```
 ┌─ List Screen ─────┐        ┌─ Detail Screen ───────┐
 │  ┌────┐            │  tap   │ ┌───────────────────┐ │
 │  │img │ tag=dish-1 │ ─────► │ │   img (big)       │ │
 │  └────┘            │ fly    │ └───────────────────┘ │
 │  ┌────┐            │        │ Butter Chicken        │
 │  │img │ tag=dish-2 │        └───────────────────────┘
 │  └────┘            │   same tag = same element
 └────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shared element | Element common to two screens | दो screens का साझा element |
| sharedTransitionTag | Matching id on both screens | मिलान वाला tag |
| Worklet | Function run on UI thread | UI thread पर चलने वाला function |
| Hero animation | iOS/Flutter name for same idea | Hero animation |
| Fabric | New RN renderer | नया renderer |

---

## ⚡ 3-Line Summary
English: Shared element transition animates one element between two screens.
Give both elements the same unique `sharedTransitionTag` using Reanimated's Animated components.
It is experimental, needs native-stack + New Architecture, so test it on devices.

Hindi: Shared element transition एक element को दो screens के बीच animate करता है।
दोनों जगह `Animated` component पर वही unique `sharedTransitionTag` दो।
यह experimental है, native-stack + New Architecture चाहिए, इसलिए real device पर test करो।

---

## ➡️ Next Topic
**142. React Navigation Animations** — screen transitions (slide, fade, modal) को navigator-level पर कैसे customize करें।
