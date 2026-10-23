# 01. What is React Native + Why Use It
# हिंदी में: React Native क्या है और क्यों Use करें
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**React Native** is a JavaScript framework by Meta (Facebook) that lets you build **real native mobile apps** for Android and iOS using **React**. You write one codebase in JavaScript/TypeScript, and React Native converts it to native Android (Java/Kotlin) and iOS (Swift/ObjC) components — not a website inside an app, but actual native UI.

## 🔵 सरल परिभाषा (Hindi)
**React Native** Meta (Facebook) का JavaScript framework है जो आपको **React use करके real native mobile apps** बनाने देता है Android और iOS के लिए। आप एक बार JavaScript/TypeScript में code लिखते हो, React Native उसे native Android और iOS components में convert करता है — यह app के अंदर website नहीं है, बल्कि actual native UI है।

---

## 🔴 Problem it Solves
```
BEFORE React Native:
❌ Android app → Java/Kotlin (separate team, separate code)
❌ iOS app → Swift/Objective-C (separate team, separate code)
❌ Two codebases = 2x cost + 2x time + 2x bugs
❌ Web developers couldn't build mobile apps
❌ "Hybrid" apps (Cordova) = website in a shell → slow, not native
```

## 🔴 यह क्यों बना? (Hindi)
```
React Native से पहले:
❌ Android → Java/Kotlin (अलग team, अलग code)
❌ iOS → Swift/Objective-C (अलग team, अलग code)
❌ दो codebases = 2x cost + 2x time
❌ Web developers mobile apps नहीं बना सकते थे
React Native ने solve किया: एक code → दोनों platforms!
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write JavaScript + React code (JSX)

Step 2 → Metro Bundler compiles your JS code into a bundle

Step 3 → Your JS runs on a JavaScript engine (Hermes/JSC)

Step 4 → React Native's Bridge (old) or JSI (new) connects
         JS side ←→ Native side

Step 5 → React Native maps React components to native:
         <View>   → android.view.View  | UIView (iOS)
         <Text>   → android.widget.TextView | UILabel (iOS)
         <Image>  → ImageView | UIImageView (iOS)

Step 6 → Real native widgets render on screen
         → Looks and feels like a native app!
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप JavaScript + React code लिखते हो
Step 2 → Metro Bundler JS को bundle में compile करता है
Step 3 → JS, Hermes engine पर run होता है
Step 4 → Bridge/JSI: JS side ←→ Native side connect करता है
Step 5 → React Native components को native widgets में map करता है:
         <View> → Android का View | iOS का UIView
         <Text> → Android का TextView | iOS का UILabel
Step 6 → Real native widgets screen पर render होते हैं
         → Actual native app जैसा feel!
```

---

## 🟡 Real World Example
**Swiggy, Zomato, ShareChat, PhonePe, Myntra** — all built with React Native. Zomato's food ordering flow, Swiggy's live order tracking map, PhonePe's payment screens — all native UI built in JavaScript. Meta's own Facebook and Instagram apps use React Native for large portions of their UI.

## 🟡 Real Example Hindi mein
**Swiggy, Zomato, ShareChat, PhonePe, Myntra** — सब React Native से बने हैं। Zomato का food ordering flow, Swiggy का live tracking map, PhonePe के payment screens — सब JavaScript में बने native UI हैं। Meta के Facebook और Instagram apps भी React Native use करते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic React Native App — HelloWorld
// Works on both Android and iOS!

import React from 'react';
import {
  View,        // like <div> in web
  Text,        // like <p> or <h1> in web
  StyleSheet,  // like CSS but for native
  SafeAreaView // avoids notch + status bar
} from 'react-native';

// Component looks like React.js!
function App() {
  return (
    // SafeAreaView: content stays in safe zone (avoids notch)
    <SafeAreaView style={styles.container}>
      <View style={styles.card}>
        {/* Text: the ONLY component that can show text in RN */}
        <Text style={styles.title}>🚀 Namaste React Native!</Text>
        <Text style={styles.subtitle}>
          This renders as NATIVE UI on Android + iOS
        </Text>
        <Text style={styles.info}>
          Not a website. Real native app!
        </Text>
      </View>
    </SafeAreaView>
  );
}

// StyleSheet: like CSS-in-JS but optimized for native
const styles = StyleSheet.create({
  container: {
    flex: 1,                    // take full screen
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 12,
    // shadow on iOS:
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    // shadow on Android:
    elevation: 3,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 4,
  },
  info: {
    fontSize: 14,
    color: '#f97316', // orange
    fontStyle: 'italic',
  },
});

export default App;
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Platform-aware + Interactive Zomato-style card
import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Platform,       // to check Android vs iOS
  StyleSheet,
  Alert,
} from 'react-native';

function RestaurantCard({ restaurant }) {
  const [isLiked, setIsLiked] = useState(false);

  const handleOrder = () => {
    // Platform-specific behavior
    Alert.alert(
      'Order Placed! 🎉',
      `Your order from ${restaurant.name} is confirmed.`,
      [{ text: 'OK', onPress: () => console.log('OK') }]
    );
  };

  return (
    <View style={[
      styles.card,
      // Platform-specific shadow
      Platform.OS === 'ios' ? styles.iosShadow : styles.androidShadow
    ]}>
      {/* Restaurant info */}
      <View style={styles.info}>
        <Text style={styles.name}>{restaurant.name}</Text>
        <Text style={styles.cuisine}>{restaurant.cuisine}</Text>
        <View style={styles.meta}>
          <Text style={styles.rating}>⭐ {restaurant.rating}</Text>
          <Text style={styles.dot}>•</Text>
          <Text style={styles.time}>{restaurant.deliveryTime} min</Text>
          <Text style={styles.dot}>•</Text>
          <Text style={styles.price}>{restaurant.priceRange}</Text>
        </View>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        {/* Wishlist button */}
        <TouchableOpacity
          onPress={() => setIsLiked(l => !l)}
          style={styles.likeBtn}
        >
          <Text style={styles.likeIcon}>{isLiked ? '❤️' : '🤍'}</Text>
        </TouchableOpacity>

        {/* Order button */}
        <TouchableOpacity
          onPress={handleOrder}
          style={styles.orderBtn}
          activeOpacity={0.8}
        >
          <Text style={styles.orderText}>Order Now</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    margin: 12,
    padding: 16,
  },
  iosShadow: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
  },
  androidShadow: {
    elevation: 4, // Android only
  },
  info: { marginBottom: 12 },
  name: { fontSize: 18, fontWeight: '700', color: '#111' },
  cuisine: { fontSize: 13, color: '#888', marginTop: 2 },
  meta: { flexDirection: 'row', marginTop: 6, alignItems: 'center' },
  rating: { fontSize: 13, color: '#f97316' },
  dot: { marginHorizontal: 6, color: '#ccc' },
  time: { fontSize: 13, color: '#555' },
  price: { fontSize: 13, color: '#555' },
  actions: { flexDirection: 'row', alignItems: 'center' },
  likeBtn: { padding: 8, marginRight: 10 },
  likeIcon: { fontSize: 22 },
  orderBtn: {
    flex: 1,
    backgroundColor: '#f97316',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  orderText: { color: '#fff', fontWeight: '700', fontSize: 15 },
});

export default RestaurantCard;
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Shadow | `elevation: 4` | `shadowColor, shadowOffset, shadowOpacity, shadowRadius` |
| Default font | Roboto | San Francisco (SF) |
| Back button | Hardware back button | Swipe from left edge |
| Status bar | Controlled with `StatusBar` | Auto-hidden / notch area |
| Safe area | Varies by device | Always needed (notch) |
| Store | Google Play Store | Apple App Store |
| Build format | APK / AAB | IPA |

---

## 🟠 Expo vs CLI Difference

**Expo way:** (Recommended for beginners)
```bash
# Install Expo CLI
npm install -g expo-cli

# Create project
npx create-expo-app MyZomatoApp

# Run
cd MyZomatoApp
npx expo start
# Scan QR code with Expo Go app on phone!
```

**React Native CLI way:** (More control, required for native modules)
```bash
# Requirements: Android Studio + Xcode installed
npx react-native@latest init MyZomatoApp

# Run on Android
cd MyZomatoApp
npx react-native run-android

# Run on iOS (Mac only)
npx react-native run-ios
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Thinking React Native = Web inside an app
```
WRONG: React Native is NOT a WebView or Cordova hybrid
React Native components map to REAL native widgets
<Text> → actual TextView (Android) / UILabel (iOS)
This is why performance is near-native!
```
✅ **Correct:** React Native uses real native UI components, not HTML/CSS

❌ **Mistake 2:** Using `<div>`, `<p>`, `<img>` in React Native
```jsx
// WRONG: HTML elements don't work in React Native!
function App() {
  return <div>Hello</div>; // ❌ Error! div doesn't exist in RN
}

// CORRECT: Use RN components
function App() {
  return <View><Text>Hello</Text></View>; // ✅
}
```

❌ **Mistake 3:** Putting text directly in View (without Text component)
```jsx
// WRONG: text must be inside <Text>!
<View>Hello World</View>     // ❌ Error!

// CORRECT:
<View><Text>Hello World</Text></View>  // ✅
```

---

## 🧠 Tricky Interview Question

**Q: If React Native uses JavaScript, why is it faster than Cordova/Ionic hybrid apps?**

**Answer:** Cordova renders an actual website inside a WebView — it's HTML/CSS/JS running in a browser engine. React Native does NOT use a WebView. It has a Bridge/JSI that communicates between JavaScript and the native layer. Each React Native component (`<View>`, `<Text>`) maps to an actual native widget. So the final UI is rendered by the platform's native rendering engine (same as Swift/Java apps), not by a browser. That's why React Native performance is near-native while Cordova feels slow.

---

## ⚫ Interview Questions + Answers

**Q1: What is React Native and how is it different from regular React?**
A1: React Native is a framework for building native mobile apps using JavaScript and React. React.js renders to the browser DOM using HTML elements (`div`, `p`, `span`). React Native renders to native mobile UI components (`View`, `Text`, `Image`) — no browser, no HTML, no CSS. React Native uses the same component model, JSX, hooks, and state management as React.js but with platform-specific components and APIs.

**Q2: What does "native" mean in React Native?**
A2: "Native" means the UI is built with the platform's own rendering engine — the same one used by apps written in Swift (iOS) or Kotlin/Java (Android). A React Native `<View>` becomes an actual `UIView` on iOS and `android.view.View` on Android. This means the app looks, feels, and performs like a platform-native app, responds to device themes, respects accessibility, and uses native animations.

**Q3: What companies use React Native in production?**
A3: Meta/Facebook (Instagram, Facebook), Microsoft (Outlook, Teams), Shopify (mobile app), Walmart, Discord, Pinterest, Bloomberg, and in India: Zomato, Swiggy, ShareChat, PhonePe, OYO, Myntra. These are large-scale, millions-of-users production apps — proving React Native's production readiness.

**Q4: What are the main advantages of React Native?**
A4: (1) Code sharing — 60-90% code shared between Android and iOS. (2) Fast development — JavaScript devs can build mobile apps without learning Swift/Kotlin. (3) Hot Reload/Fast Refresh — see changes instantly. (4) Large ecosystem — npm packages, React knowledge transfers. (5) OTA updates — push JavaScript updates without going through app store review. (6) Near-native performance — real native UI, not WebView.

**Q5: What are the limitations of React Native?**
A5: (1) Complex native features need native modules (Kotlin/Swift code). (2) Performance-critical animation/rendering is still slightly behind fully native. (3) Bridge architecture (old) had serialization overhead — JSI/New Architecture addresses this. (4) Debugging can be complex across JS and native layers. (5) Some libraries lack quality cross-platform support. (6) Large team updates (React Native releases) can cause breaking changes.

---

## 🔷 When to Use + When Not to Use
✅ **Use React Native when:**
- Your team knows React/JavaScript
- Need Android + iOS from one codebase
- Building business apps (e-commerce, delivery, fintech)
- Startup — fast time to market
- Significant code sharing is possible

❌ **Avoid React Native when:**
- App is graphics/game intensive (use Unity/native)
- App requires very deep hardware integration (AR/VR, very specific hardware)
- Pure iOS app where extreme UI polish matters more than cross-platform
- Very small app where learning React Native overhead isn't worth it

---

## 📊 Visual Diagram

```
REACT NATIVE ARCHITECTURE:
──────────────────────────────────────────────────
  YOUR CODE (JavaScript/TypeScript)
  ┌────────────────────────────────────────────┐
  │  <View>  <Text>  <Image>  <FlatList>  ...  │
  └────────────────────────────────────────────┘
                      │
                      │ Bridge (old) / JSI (new)
                      ▼
  REACT NATIVE LAYER
  ┌────────────────────────────────────────────┐
  │  Maps React components to native widgets   │
  └────────────────────────────────────────────┘
           │                        │
           ▼                        ▼
  ANDROID NATIVE              iOS NATIVE
  ┌──────────────┐        ┌──────────────┐
  │ View         │        │ UIView       │
  │ TextView     │        │ UILabel      │
  │ ImageView    │        │ UIImageView  │
  │ RecyclerView │        │ UITableView  │
  └──────────────┘        └──────────────┘
           │                        │
           ▼                        ▼
   Android Screen            iOS Screen
  (Native rendering)      (Native rendering)

COMPARISON:
──────────────────────────────────────────────────
  Cordova/Ionic    → JS → WebView → HTML/CSS
  React Native     → JS → Bridge/JSI → Native UI  ✅
  Flutter          → Dart → Skia Canvas → Own UI
  Native (Java/Swift) → Platform Lang → Native UI
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| React Native | JS framework for native mobile apps | Native mobile apps के लिए JS framework |
| Bridge | Old way JS ↔ Native communicated | पुराना JS ↔ Native communication |
| JSI | New way JS ↔ Native (direct, fast) | नया, fast JS ↔ Native communication |
| Metro Bundler | Dev server that bundles JS | JS bundle करने वाला dev server |
| Native Module | Custom native code called from JS | JS से call होने वाला native code |
| Hermes | Facebook's JS engine for RN | Facebook का JS engine |
| Expo | Managed platform on top of RN | RN के ऊपर managed platform |
| EAS | Expo Application Services (build+submit) | Build और submit service |

---

## ⚡ 3-Line Summary
**English:**
1. React Native = write JavaScript + React → get real native Android & iOS apps (not a website in an app shell).
2. Your components (`<View>`, `<Text>`) map to actual native widgets — so the UI looks, feels, and performs natively.
3. One codebase for both platforms = 60-90% code shared, saving time, cost, and team size.

**Hindi:**
1. React Native = JavaScript + React लिखो → real native Android & iOS apps मिलते हैं (app के अंदर website नहीं)।
2. आपके components (`<View>`, `<Text>`) actual native widgets बनते हैं — UI native जैसा look, feel, और performance देता है।
3. दोनों platforms के लिए एक codebase = 60-90% code shared → time, cost, और team size बचती है।

---

## ➡️ Next Topic
**02. React Native vs Flutter vs Native** — तीनों का comparison — कब क्या choose करना चाहिए।

---

## 📚 Go Deeper — External Resources
| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — React Native](https://www.youtube.com/results?search_query=react+native+tutorial+hindi+akshay+saini) | RN in Hindi |
| 📺 YouTube | [Pradip Debnath — React Native](https://www.youtube.com/results?search_query=react+native+complete+course+pradip+debnath) | Complete RN course |
| 📝 Docs | [reactnative.dev](https://reactnative.dev) | Official React Native docs |
| 📝 Docs | [expo.dev/docs](https://docs.expo.dev) | Expo documentation |
