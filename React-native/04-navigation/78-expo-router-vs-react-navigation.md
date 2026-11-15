# 78. Expo Router vs React Navigation
# हिंदी में: Expo Router बनाम React Navigation
# Platform: Android ✅ | iOS ✅ | Both ✅

> Targets: Expo SDK 52 (React Native 0.76), expo-router v4, React Navigation v7 (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
React Navigation is the core navigation library where you declare navigators and screens in code. Expo Router is a layer on top of it that creates those navigators from the file structure. So it is not "either-or": Expo Router **uses** React Navigation underneath.

## 🔵 सरल परिभाषा (Hindi)
React Navigation core library है जिसमें navigators और screens code में declare होते हैं। Expo Router उसके ऊपर की layer है जो file structure से वही navigators बनाती है। यानी "या तो-या" नहीं — Expo Router नीचे React Navigation ही use करता है।

---

## 🔴 Problem it Solves
```
Team confusion: "नया ऐप किससे बनाएँ?"

React Navigation: पूरा control, पर boilerplate + linking config हाथ से.
Expo Router:     कम boilerplate, deep link/web फ्री, पर file conventions मानने पड़ते हैं.

Paytm जैसा बड़ा ऐप: runtime पर बदलते flows (KYC steps) -> code-defined navigator सुविधाजनक.
Naya startup MVP: files बनाओ, तुरंत चलाओ -> Expo Router.
```

## 🔴 यह क्यों बना? (Hindi)
Navigation को code में लिखना लचीला है पर दोहराव वाला है। Expo Router ने web (Next.js) जैसा सरल तरीका दिया। तुलना जानना interview में इसलिए पूछा जाता है ताकि आप सही tool चुन सको, फैशन में नहीं।

---

## 🟢 How it Works — Step by Step
```
React Navigation:
  Step 1 → NavigationContainer बनाओ
  Step 2 → createNativeStackNavigator() से Stack बनाओ
  Step 3 → हर screen Stack.Screen में register
  Step 4 → linking config हाथ से लिखो (deep link चाहिए तो)

Expo Router:
  Step 1 → app/ में files बनाओ
  Step 2 → _layout.tsx में Stack/Tabs
  Step 3 → Router खुद NavigationContainer + linking बनाता है
  Step 4 → Link / router.push('/path')
```

## 🟢 कैसे काम करता है? (Hindi)
```
React Navigation: सब कुछ code में register करो, linking खुद लिखो
Expo Router:      files देखकर navigators अपने आप बनते हैं
दोनों का runtime engine एक ही है (React Navigation)
Navigation action: navigate('Name', params) बनाम push('/path')
```

---

## 🟡 Real World Example
**Zomato (hypothetical):** पहले React Navigation में 60 screens और हाथ से लिखा linking config। नया "Zomato Lite" ऐप Expo Router से: हर screen एक file, `/restaurant/[id]` से share-links मुफ्त।

## 🟡 Real Example Hindi mein
**Paytm Mini-apps:** screens runtime पर server config से तय होती हैं — यहाँ React Navigation का dynamic `Stack.Screen` mapping आसान है। जबकि एक सामान्य "Orders / Profile / Support" ऐप Expo Router में कम code में बन जाता है।

---

## 💻 Code Example — Basic
```jsx
// ---------- React Navigation (code-defined) ----------
import React from 'react';                                         // React
import { Text, Button } from 'react-native';                       // UI
import { NavigationContainer } from '@react-navigation/native';    // root
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack

const Stack = createNativeStackNavigator();                        // stack object

function Home({ navigation }) {
  return <Button title="Open" onPress={() => navigation.navigate('Detail', { id: 7 })} />; // params
}
function Detail({ route }) {
  return <Text>id: {route.params.id}</Text>;                       // params read
}

export default function App() {
  return (
    <NavigationContainer>                                          {/* manual container */}
      <Stack.Navigator>
        <Stack.Screen name="Home" component={Home} />              {/* register */}
        <Stack.Screen name="Detail" component={Detail} />          {/* register */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```
```tsx
// ---------- Expo Router (file-defined) ----------
// app/_layout.tsx
import { Stack } from 'expo-router';
export default function Layout() { return <Stack />; }             // screens files से अपने आप

// app/index.tsx
import { Button } from 'react-native';
import { router } from 'expo-router';                              // imperative router
export default function Home() {
  return <Button title="Open" onPress={() => router.push('/detail/7')} />; // path से navigate
}

// app/detail/[id].tsx
import { Text } from 'react-native';
import { useLocalSearchParams } from 'expo-router';                // params
export default function Detail() {
  const { id } = useLocalSearchParams();                           // string '7'
  return <Text>id: {id}</Text>;
}
```

## 💻 Code Example — Advanced
```tsx
// Hybrid: Expo Router में भी underlying React Navigation APIs use होते हैं
// app/(tabs)/_layout.tsx
import { Tabs, useNavigation } from 'expo-router';        // Tabs + navigation hook
import { Platform } from 'react-native';                  // platform check
import { useEffect } from 'react';                        // effect

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,                               // custom header
        tabBarStyle: Platform.select({
          ios: { position: 'absolute' },                  // iOS: blur-ready floating bar
          default: {},                                    // Android: default
        }),
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Home' }} />    {/* tab 1 */}
      <Tabs.Screen name="orders" options={{ title: 'Orders' }} /> {/* tab 2 */}
    </Tabs>
  );
}

// एक screen में React Navigation event वैसे ही:
export function OrdersScreen() {
  const navigation = useNavigation();                     // React Navigation object
  useEffect(() => {
    const unsub = navigation.addListener('focus', () => console.log('Orders focused')); // वही events
    return unsub;                                         // cleanup
  }, [navigation]);
  return null;
}
```
Linking को React Navigation में manual config चाहिए; Expo Router में `scheme` ही काफी (`app.json`: `"scheme": "myapp"`)।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| दोनों libraries का behaviour | Native stack (Fragments-based) | Native stack (UINavigationController) |
| Back | Hardware back दोनों में handle | Swipe-back दोनों में |
| Deep link setup | Router: scheme से auto; RN Nav: intent filter + linking config | Router: scheme से auto; RN Nav: URL types + linking config |
| Choice का असर | कोई platform-specific फर्क नहीं | कोई platform-specific फर्क नहीं |

मुख्य फर्क developer experience का है, platform का नहीं।

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Default template: expo-router पहले से configured, "main": "expo-router/entry"
```
CLI way:
```jsx
// bare RN: React Navigation manual install
// npm i @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context
// Expo Router भी चल सकता है पर extra config (babel, metro, scheme) खुद करनी पड़ती है
```
तुलना तालिका:
```
                      React Navigation        Expo Router
Routes define         code में                files से
Deep links            manual linking config   automatic (scheme)
Web support           सीमित/manual            first-class URLs
Typed routes          param list types        experiments.typedRoutes
Dynamic runtime routes आसान                   कठिन
Boilerplate           ज़्यादा                 कम
Learning curve        सीधा                    file conventions
Underlying engine     itself                  React Navigation
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** सोचना कि Expo Router, React Navigation को replace करता है
✅ **Correct:** यह उसी के ऊपर है; `useNavigation`, options, events वही हैं।

❌ **Mistake 2:** Expo Router में `navigation.navigate('Detail')` जैसे नाम से navigate करना
✅ **Correct:** path से: `router.push('/detail/7')`।

❌ **Mistake 3:** दोनों को एक ही ऐप में अलग-अलग `NavigationContainer` से mix करना
✅ **Correct:** Expo Router अपना container बनाता है; एक ही ऐप में दूसरा root container मत लगाओ।

---

## 🧠 Tricky Interview Question
**Q: "Expo Router से performance बेहतर होता है" — सही है?**

**Answer:** नहीं। दोनों का native stack और runtime एक ही है, इसलिए raw performance में बड़ा फर्क नहीं। फायदे developer-experience, deep link और web में हैं। (Expo Router में routes lazy load हो सकते हैं और bundle-splitting web पर काम आती है, पर यह "हमेशा तेज़" का दावा नहीं है। Measure करो।)

---

## ⚫ Interview Questions + Answers
**Q1: दोनों में मुख्य फर्क?**
A1: React Navigation code-based config; Expo Router file-based, उसी के ऊपर बना।

**Q2: Existing React Navigation ऐप को migrate करना चाहिए?**
A2: ज़रूरी नहीं। फायदा (deep links/web) बड़ा हो और team तैयार हो तभी; migration में screen names, params और auth flow दोबारा लिखने पड़ते हैं।

**Q3: Typed navigation दोनों में कैसे?**
A3: React Navigation: `ParamList` types + `RouteProp`. Expo Router: `experiments.typedRoutes` से generated types (version-dependent)।

**Q4: Expo Router में custom navigator?**
A4: `withLayoutContext` से React Navigation navigator को wrap कर सकते हैं।

**Q5: कौन सा interview में default चुनें?**
A5: "नया Expo ऐप = Expo Router (Expo की recommendation); पुराना/dynamic ऐप या heavy customization = React Navigation" — कारण के साथ।

---

## 🔷 When to Use + When Not to Use
✅ Expo Router चुनो जब:
- नया Expo ऐप, deep links/web/universal ऐप
- छोटी-बड़ी team जिसे standard structure चाहिए

✅ React Navigation चुनो जब:
- मौजूदा बड़ा ऐप, runtime-generated routes
- Expo के बाहर bare RN में कम dependencies चाहिए

❌ Avoid:
- सिर्फ trend के कारण migrate करना

---

## 📊 Visual Diagram
```
 Files (app/)            Code (Stack.Screen)
      │                         │
 Expo Router               (सीधे)
      └──────────┬──────────────┘
                 ▼
         React Navigation  (engine)
                 ▼
     react-native-screens (native stack)
                 ▼
         Android / iOS UI
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Code-based routing | Screens registered in code | Code में routes |
| File-based routing | Files are routes | Files ही routes |
| Linking config | URL to screen mapping | URL-से-screen mapping |
| Typed routes | Type-safe hrefs | Type-safe links |
| withLayoutContext | Wrap custom navigator | Custom navigator जोड़ना |

---

## ⚡ 3-Line Summary
English:
1. Expo Router is built on React Navigation, only the way of defining routes differs.
2. Expo Router: less boilerplate, auto deep links/web; React Navigation: max flexibility.
3. Choose by project needs, not performance claims.

Hindi:
1. Expo Router, React Navigation के ऊपर बना है; सिर्फ routes define करने का तरीका अलग है।
2. Expo Router: कम boilerplate, auto deep links/web; React Navigation: ज़्यादा flexibility।
3. चुनाव project की ज़रूरत से करो, performance के दावों से नहीं।

---

## ➡️ Next Topic
**79. All React Hooks Work in RN** — React के hooks RN में कैसे काम करते हैं।
