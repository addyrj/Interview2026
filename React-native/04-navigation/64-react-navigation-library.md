# 64. React Navigation Library
# हिंदी में: React Navigation Library — Setup और Architecture
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)**, **React Navigation 7** (v6 mostly similar) — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**React Navigation** is the most used navigation library for React Native, written mostly in JavaScript. It provides navigators (stack, tabs, drawer), hooks (`useNavigation`, `useRoute`), deep linking, theming and TypeScript support. It is a set of packages under `@react-navigation/*`.

## 🔵 सरल परिभाषा (Hindi)
**React Navigation** React Native की सबसे ज़्यादा use होने वाली navigation library है, ज़्यादातर JavaScript में लिखी। यह navigators (stack, tabs, drawer), hooks (`useNavigation`, `useRoute`), deep linking, theming और TypeScript support देती है। यह `@react-navigation/*` packages का set है।

---

## 🔴 Problem it Solves
```
BEFORE (2016): NavigationExperimental / Navigator (old, buggy, platform-different)
Different libs for iOS/Android, hard to customize

REACT NAVIGATION:
  ✅ One API for both platforms
  ✅ Composable navigators (nest tabs inside stack)
  ✅ Customizable headers, transitions
  ✅ Hooks + TypeScript
  ✅ Works in Expo and bare CLI
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले RN में navigation के लिए पुराने, buggy और अलग-अलग तरीके थे।
React Navigation एक ही API दोनों platforms पर देती है,
navigators को एक-दूसरे में जोड़ने देती है और customize करना आसान है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Core:     @react-navigation/native
Step 2 → Peer deps: react-native-screens, react-native-safe-area-context
Step 3 → Pick navigator packages:
           @react-navigation/native-stack   (native stack)
           @react-navigation/stack          (JS stack, more customizable)
           @react-navigation/bottom-tabs
           @react-navigation/drawer         (needs gesture-handler + reanimated)
           @react-navigation/material-top-tabs (needs pager-view)
Step 4 → <NavigationContainer> at root
Step 5 → createXNavigator() → Navigator + Screen components
Step 6 → Each screen receives { navigation, route } props
Step 7 → State is a tree: { routes: [...], index } kept by container
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Core: @react-navigation/native
Step 2 → Peer deps: react-native-screens, react-native-safe-area-context
Step 3 → ज़रूरत का navigator package चुनो (native-stack, bottom-tabs, drawer...)
Step 4 → Root पर NavigationContainer
Step 5 → createXNavigator() से Navigator और Screen मिलते हैं
Step 6 → हर screen को navigation और route props मिलते हैं
Step 7 → State एक tree है जिसे container संभालता है
```

---

## 🟡 Real World Example
**Paytm-style app:** Bottom Tabs (Home, Passbook, History) with a root Stack above it for Pay Screen, Scan QR, and Payment Success. Auth screens (Login/OTP) form a separate stack shown conditionally. All composed with React Navigation: tabs inside stack inside container.

## 🟡 Real Example Hindi mein
**Paytm जैसा app:** नीचे Tabs (Home, Passbook, History), ऊपर root Stack जिसमें Pay Screen, Scan QR, Payment Success। Login/OTP screens अलग stack में, condition के हिसाब से दिखती हैं। यह सब React Navigation में tabs → stack → container की तरह जुड़ता है।

---

## 💻 Code Example — Basic
```jsx
// Basic setup with native stack and typed-less params
// npx expo install @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context
import React from 'react'; // React
import { View, Text, Pressable } from 'react-native'; // UI
import { NavigationContainer, DefaultTheme } from '@react-navigation/native'; // container + default theme
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // navigator factory

const Stack = createNativeStackNavigator(); // returns { Navigator, Screen }

// Custom theme (colors used by header, background)
const theme = { ...DefaultTheme, colors: { ...DefaultTheme.colors, primary: '#5f259f', background: '#fff' } };

function Home({ navigation }) { // screen gets navigation prop
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Pressable onPress={() => navigation.navigate('Profile', { name: 'Aditya' })}>{/* pass param */}
        <Text>Open Profile</Text>
      </Pressable>
    </View>
  );
}

function Profile({ route }) { // route prop has params
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text>Hello {route.params?.name}</Text>{/* optional chaining: params may be undefined */}
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer theme={theme}>{/* apply theme */}
      <Stack.Navigator initialRouteName="Home">{/* start screen */}
        <Stack.Screen name="Home" component={Home} />
        <Stack.Screen name="Profile" component={Profile} options={({ route }) => ({ title: route.params?.name ?? 'Profile' })} />{/* dynamic title */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: tabs inside stack, linking config, state persistence hook-in, ref navigation
import React, { useRef } from 'react'; // React + ref
import { Text, View } from 'react-native'; // UI
import { NavigationContainer, createNavigationContainerRef } from '@react-navigation/native'; // container + ref helper
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'; // tabs

// Ref lets you navigate OUTSIDE components (e.g. from notification handler or API interceptor)
export const navRef = createNavigationContainerRef(); // create once
export function navigateOutside(name, params) { // helper
  if (navRef.isReady()) navRef.navigate(name, params); // only when tree is mounted
}

const Stack = createNativeStackNavigator(); // root stack
const Tab = createBottomTabNavigator(); // tabs

const Screen = ({ label }) => <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}><Text>{label}</Text></View>; // dummy screen

function Tabs() { // tab navigator component
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>{/* hide tab headers; stack shows header */}
      <Tab.Screen name="Home" children={() => <Screen label="Home" />} />
      <Tab.Screen name="Passbook" children={() => <Screen label="Passbook" />} />
    </Tab.Navigator>
  );
}

// Deep link config: myapp://pay/123 → Pay screen with id param
const linking = {
  prefixes: ['myapp://'], // custom scheme (also set "scheme" in app.json for Expo)
  config: { screens: { Tabs: { screens: { Home: 'home', Passbook: 'passbook' } }, Pay: 'pay/:id' } }, // path map
};

export default function App() {
  return (
    <NavigationContainer ref={navRef} linking={linking} onReady={() => console.log('nav ready')}>{/* ref + linking */}
      <Stack.Navigator>
        <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />{/* tabs as one stack screen */}
        <Stack.Screen name="Pay" component={() => <Screen label="Pay" />} options={{ presentation: 'modal' }} />{/* modal presentation */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| native-stack | Uses Fragments (react-native-screens) | Uses UINavigationController |
| Header | Material style, left title | Large titles available (`headerLargeTitle`) |
| `presentation: 'modal'` | Slides up (different look) | Native card/sheet modal |
| Gesture back | System back gesture/button | Swipe from edge (`gestureEnabled`) |
| `@react-navigation/stack` (JS) | Same look everywhere (customizable) | Same |
| Hardware back | Handled automatically | N/A |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: install with expo for compatible versions, set URL scheme in app.json for deep links
// npx expo install @react-navigation/native react-native-screens react-native-safe-area-context
// app.json: { "expo": { "scheme": "myapp" } }
```
CLI way:
```jsx
// Bare CLI: npm install + pod install
// npm i @react-navigation/native react-native-screens react-native-safe-area-context
// cd ios && pod install
// Deep links: add intent-filter in AndroidManifest.xml and URL types in Info.plist manually
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing inline `component={() => <Screen/>}`.
✅ Correct: Pass a stable component or use `children` render callback sparingly; inline functions remount the screen on every render (used above only for demo brevity).

❌ Mistake 2: Putting non-serializable values (functions) in params.
✅ Correct: Pass ids/plain data; get functions via context/store (warning appears otherwise).

❌ Mistake 3: Missing peer dependencies, causing red-screen errors.
✅ Correct: Install screens + safe-area-context (+ gesture-handler for drawer).

❌ Mistake 4: Using `@react-navigation/stack` everywhere when native-stack suffices.
✅ Correct: Prefer native-stack for performance; use JS stack only for custom animations.

---

## 🧠 Tricky Interview Question
**Q:** Why does a screen defined as `component={() => <Profile />}` lose its state when the parent re-renders?

**Answer:** The inline arrow function is a new component type each render, so React unmounts and remounts it. Pass the component reference (`component={Profile}`) or use `children` with care, e.g. memoized. This is the same reason defining styled components inside render is bad.

---

## ⚫ Interview Questions + Answers
Q1: native-stack vs stack?
A1: native-stack uses real native navigation primitives (faster, native feel). `stack` is JS-driven (more customizable animations, slower).

Q2: How to navigate outside a component?
A2: `createNavigationContainerRef()` + `navigationRef.navigate(...)` after `isReady()`.

Q3: What are `navigation` and `route` props?
A3: `navigation` has methods (navigate, goBack...). `route` has `name`, `key`, `params`.

Q4: How to type routes in TypeScript?
A4: Define `RootStackParamList` and pass to `createNativeStackNavigator<RootStackParamList>()`.

Q5: What is a static API in v7?
A5: v7 introduced `createStaticNavigation` config-object style (optional). Dynamic API still works. Check v7 docs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Standard app navigation in Expo or CLI
- You need deep linking, theming, typed routes

❌ Avoid when:
- You prefer file-based routing (use Expo Router, which is built on it)
- You need fully native navigation controllers (Wix react-native-navigation)

---

## 📊 Visual Diagram
```
NavigationContainer (state, linking, theme)
   │
   └─ Root Stack
        ├─ Tabs (Bottom Tabs)
        │     ├─ Home
        │     └─ Passbook
        ├─ Pay (modal)
        └─ Auth Stack (Login, OTP)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| NavigationContainer | Root holder of nav state | Root container |
| Navigator | Manages group of screens | Screens का manager |
| route | Current screen info | Route (screen की जानकारी) |
| linking | Deep link config | Deep link config |
| navigationRef | Navigate outside components | Component के बाहर navigation |

---

## ⚡ 3-Line Summary
English: React Navigation is a package family (`@react-navigation/*`) for screens, tabs, drawers.
Needs `react-native-screens` and `react-native-safe-area-context`.
Supports deep links, theming, TypeScript and navigation outside components.

Hindi: React Navigation `@react-navigation/*` packages का family है, screens/tabs/drawers के लिए।
`react-native-screens` और `react-native-safe-area-context` ज़रूरी हैं।
Deep links, theming, TypeScript और component के बाहर navigation सपोर्ट करती है।

---

## ➡️ Next Topic
**65. Stack Navigator** (already available) — fir **67. Drawer Navigator**.
