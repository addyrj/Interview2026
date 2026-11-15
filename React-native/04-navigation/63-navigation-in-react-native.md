# 63. Navigation in React Native
# हिंदी में: React Native में Navigation (Screens के बीच जाना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)**, React Navigation 7 / Expo Router 4 — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**Navigation** is how users move between screens in an app. React Native has **no built-in router** like a browser URL bar, so you use a library: **React Navigation** (most popular) or **Expo Router** (file-based, built on React Navigation). Navigation also handles the back button, headers, tabs, drawers and gestures.

## 🔵 सरल परिभाषा (Hindi)
**Navigation** का मतलब है user का app की एक screen से दूसरी screen पर जाना। React Native में browser जैसा **built-in router नहीं** है, इसलिए library use करते हैं: **React Navigation** (सबसे popular) या **Expo Router** (file-based, React Navigation पर बना)। Navigation back button, header, tabs, drawer और gestures भी संभालता है।

---

## 🔴 Problem it Solves
```
WEB:
  URL change → browser page load → back button free

MOBILE (no router):
  Ek hi screen ko state se toggle: if (page==='cart') ...
  ❌ Android hardware back button kaam nahi
  ❌ iOS swipe-back gesture nahi
  ❌ Screen state kho jata hai
  ❌ Deep links (zomato://restaurant/12) nahi

WITH NAVIGATION LIBRARY:
  ✅ Screen stack + back handling
  ✅ Native transitions + gestures
  ✅ Deep linking
  ✅ Tabs/Drawer/Stack patterns
```

## 🔴 यह क्यों बना? (Hindi)
```
Mobile में URL नहीं होता, इसलिए screens manage करने का system चाहिए।
Manual state से Android back button, iOS swipe back, deep links काम नहीं करते।
Navigation library यह सब native-जैसा संभालती है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Choose library: React Navigation (manual) or Expo Router (file-based)
Step 2 → Install navigator packages + peer deps (screens, safe-area-context)
Step 3 → Wrap app in NavigationContainer (state + linking holder)
Step 4 → Create navigator (Stack / Tabs / Drawer)
Step 5 → Register screens: name + component
Step 6 → navigation.navigate('Name', params) changes navigation state
Step 7 → Library renders screens with native transitions (react-native-screens)
Step 8 → Back button / gesture pops state
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Library चुनो (React Navigation / Expo Router)
Step 2 → Packages और peer dependencies install
Step 3 → NavigationContainer में app wrap
Step 4 → Navigator बनाओ (Stack/Tabs/Drawer)
Step 5 → Screens register करो
Step 6 → navigate('Name', params) से state बदलती है
Step 7 → Native transitions के साथ screen दिखती है
```

---

## 🟡 Real World Example
**Swiggy:** Bottom tabs (Food, Instamart, Dineout), inside Food a stack: Restaurant List → Restaurant → Cart → Checkout. Tapping a push notification "Your order is out for delivery" opens directly the Order Tracking screen (deep link). Android back button goes back one screen at a time.

## 🟡 Real Example Hindi mein
**Swiggy:** नीचे tabs (Food, Instamart, Dineout), Food के अंदर stack: Restaurant List → Restaurant → Cart → Checkout। Push notification "Order out for delivery" tap करने पर सीधे Order Tracking screen खुलती है (deep link)। Android back button एक-एक screen पीछे ले जाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic navigation between 2 screens (React Navigation)
// Install: npx expo install @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context
import React from 'react'; // React
import { View, Text, Button } from 'react-native'; // UI
import { NavigationContainer } from '@react-navigation/native'; // root container
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack navigator

const Stack = createNativeStackNavigator(); // create navigator

function Home({ navigation }) { // navigation prop injected by navigator
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Home</Text>
      <Button title="Go to Details" onPress={() => navigation.navigate('Details')} />{/* go forward */}
    </View>
  );
}

function Details({ navigation }) {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Details</Text>
      <Button title="Go back" onPress={() => navigation.goBack()} />{/* go back */}
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>{/* must be ONE at the root */}
      <Stack.Navigator>
        <Stack.Screen name="Home" component={Home} />{/* first screen = initial */}
        <Stack.Screen name="Details" component={Details} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Expo Router (file-based) equivalent + hardware back handling
// File structure:
//   app/_layout.jsx      → root layout (Stack)
//   app/index.jsx        → "/"
//   app/details/[id].jsx → "/details/12"

// app/_layout.jsx
import React from 'react'; // React
import { Stack } from 'expo-router'; // Stack from expo-router

export default function RootLayout() {
  return (
    <Stack screenOptions={{ headerStyle: { backgroundColor: '#e23744' }, headerTintColor: '#fff' }}>{/* default header style */}
      <Stack.Screen name="index" options={{ title: 'Restaurants' }} />{/* file app/index.jsx */}
      <Stack.Screen name="details/[id]" options={{ title: 'Details' }} />{/* dynamic route */}
    </Stack>
  );
}

// app/index.jsx
import { View, Text } from 'react-native'; // UI
import { Link } from 'expo-router'; // declarative navigation

export default function Index() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Link href="/details/12">Open restaurant 12</Link>{/* navigate by URL */}
    </View>
  );
}

// app/details/[id].jsx
import { View, Text, BackHandler, Platform } from 'react-native'; // UI + back handler
import { useLocalSearchParams, useRouter } from 'expo-router'; // params + router
import { useEffect } from 'react'; // effect

export default function Details() {
  const { id } = useLocalSearchParams(); // read :id
  const router = useRouter(); // imperative navigation

  useEffect(() => {
    if (Platform.OS !== 'android') return; // BackHandler is Android only
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      router.back(); // custom back behaviour
      return true; // true = we handled it, don't exit app
    });
    return () => sub.remove(); // cleanup
  }, [router]);

  return <View><Text>Restaurant {id}</Text></View>;
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Back navigation | Hardware/system back button + gesture | Swipe from left edge + header back button |
| Default transition | Fade/slide-up style (Material) | Slide from right |
| Header title | Left aligned | Centered |
| Back button label | Arrow only | Arrow + previous screen title (large title options) |
| `BackHandler` | Available | Not available |
| Predictive back gesture | Android 13+/14 (opt-in, check docs) | N/A |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: npx expo install handles correct versions
// npx expo install @react-navigation/native react-native-screens react-native-safe-area-context
// OR use Expo Router: npx create-expo-app@latest (default template uses expo-router)
import { Stack } from 'expo-router'; // file-based
```
CLI way:
```jsx
// Bare CLI:
// npm i @react-navigation/native react-native-screens react-native-safe-area-context
// cd ios && pod install       (iOS native modules)
// Android: usually autolinked; in MainActivity (older docs) override onCreate to pass null for screens (check docs)
import { NavigationContainer } from '@react-navigation/native'; // manual setup
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Two `NavigationContainer`s (nested).
✅ Correct: Only one at the root.

❌ Mistake 2: Using state to fake navigation (`if screen === 'cart'`).
✅ Correct: Use a navigator so back/gestures/deep links work.

❌ Mistake 3: Installing versions manually and mismatching.
✅ Correct: `npx expo install` picks compatible versions for your SDK.

❌ Mistake 4: Navigating to a name that is not registered.
✅ Correct: Names are case-sensitive and must match `Stack.Screen name`.

---

## 🧠 Tricky Interview Question
**Q:** User opens Home → Details → Home (via navigate). Is the stack `[Home, Details, Home]` or `[Home]`?

**Answer:** It depends on the version. In React Navigation 6, `navigate('Home')` goes back to the existing Home, so the stack becomes `[Home]`. In React Navigation 7, `navigate` no longer pops back to an existing screen in a stack (it pushes a new one), so you get `[Home, Details, Home]`; use `popTo('Home')` to go back (check the v7 upgrade guide). `push('Home')` always adds a new copy. This is why `navigate` vs `push` is a favorite question.

---

## ⚫ Interview Questions + Answers
Q1: Does React Native ship a router?
A1: No. Use React Navigation or Expo Router (or native libs like react-native-navigation by Wix).

Q2: React Navigation vs Expo Router?
A2: React Navigation = code-based config. Expo Router = file-based routes (like Next.js) built on React Navigation, with automatic deep links and typed routes.

Q3: Why `react-native-screens`?
A3: It uses native screen containers (UIViewController / Fragment) for better memory and performance.

Q4: What does `NavigationContainer` do?
A4: Holds navigation state, handles linking and theme; one per app.

Q5: How is state preserved on back?
A5: Screens in the stack stay mounted below the top; popping returns to the still-mounted screen.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any app with 2+ screens

❌ Avoid when:
- Single-screen utility app (a library adds weight)
- Using fully native navigation (Wix react-native-navigation) for special needs

---

## 📊 Visual Diagram
```
NavigationContainer
   └── Stack Navigator
          ├── Home        (bottom of stack)
          ├── Details     (pushed)
          └── Payment     (top = visible)

navigate('X') → push/find   goBack() → pop top
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Navigator | Component managing screens | Screens संभालने वाला |
| Screen | One page in app | एक page |
| Route | Screen entry with name + params | Route |
| Stack | Last-in-first-out screens | Screens का stack |
| Deep link | URL that opens specific screen | सीधे screen खोलने वाला link |

---

## ⚡ 3-Line Summary
English: RN has no built-in router; use React Navigation or Expo Router.
One `NavigationContainer` wraps navigators; screens are registered by name.
Navigation gives back handling, gestures and deep links.

Hindi: RN में built-in router नहीं; React Navigation या Expo Router use करो।
एक `NavigationContainer` navigators को wrap करता है; screens नाम से register होती हैं।
Navigation back handling, gestures और deep links देता है।

---

## ➡️ Next Topic
**64. React Navigation Library** — iske packages, setup aur architecture detail me.
