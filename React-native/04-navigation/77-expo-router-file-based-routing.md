# 77. Expo Router (File-based Routing)
# हिंदी में: Expo Router — Files से Routes बनाना
# Platform: Android ✅ | iOS ✅ | Both ✅ (Web ✅ भी)

> Targets: Expo SDK 52 (React Native 0.76, expo-router v4) (check current docs — APIs change between SDKs). Newer SDKs में कुछ defaults और typed-routes बदले हैं; upgrade से पहले changelog देखो।

---

## 🔵 Simple Definition (English)
Expo Router is a file-based router for React Native: every file inside the `app/` folder becomes a screen and its path becomes the URL. `app/restaurant/[id].tsx` is the route `/restaurant/123`. It is built on top of React Navigation and gives deep linking automatically.

## 🔵 सरल परिभाषा (Hindi)
Expo Router file-based router है: `app/` folder की हर file एक screen बन जाती है और उसका path ही URL होता है। `app/restaurant/[id].tsx` = route `/restaurant/123`। यह React Navigation के ऊपर बना है और deep linking अपने आप मिलती है।

---

## 🔴 Problem it Solves
```
React Navigation में हाथ से:
  - हर screen import + Stack.Screen में register
  - deep link config का अलग linking object
  - screens बढ़ें तो navigator file बहुत बड़ी

Swiggy जैसे ऐप में 80+ screens:
  navigator file 500 lines, linking config अलग, दोनों sync में रखना मुश्किल.

Expo Router: file बनाओ = screen + URL + deep link तैयार.
```

## 🔴 यह क्यों बना? (Hindi)
Web में Next.js की तरह folder structure ही routes है — यह सोच RN में लाने के लिए Expo Router बना। इससे navigator का boilerplate खत्म, deep links और web URLs अपने आप, और नई screen = नई file।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx create-expo-app@latest (default template में expo-router है)
Step 2 → app/_layout.tsx root layout बनाओ (Stack/Tabs यहाँ)
Step 3 → app/index.tsx = "/" (Home)
Step 4 → app/restaurant/[id].tsx = dynamic route
Step 5 → Link / router.push('/restaurant/12') से navigate
Step 6 → useLocalSearchParams() से id पढ़ो
```
Special file names:
```
_layout.tsx      navigator (Stack/Tabs/Drawer) define करता है
index.tsx        folder का default route
[id].tsx         dynamic segment
[...rest].tsx    catch-all
(tabs)/          group: URL में नहीं दिखता, सिर्फ organize/navigator के लिए
+not-found.tsx   404 screen
+html.tsx        (web) root HTML
```
package.json में `"main": "expo-router/entry"` होना चाहिए (template में पहले से है)।

## 🟢 कैसे काम करता है? (Hindi)
```
1. app/ folder में file बनाओ -> route बन गया
2. _layout.tsx से तय करो कि screens Stack में होंगी या Tabs में
3. [id] वाली file dynamic route है
4. (group) folder URL में नहीं आता, बस screens को group करता है
5. <Link href> या router.push() से जाओ
```

---

## 🟡 Real World Example
**Zomato-जैसा ऐप:**
```
app/
  _layout.tsx              Root Stack
  (tabs)/
    _layout.tsx            Bottom Tabs
    index.tsx              Home         -> /
    orders.tsx             Orders       -> /orders
    profile.tsx            Profile      -> /profile
  restaurant/[id].tsx      /restaurant/r123
  +not-found.tsx           अमान्य link
```
`zomato://restaurant/r123` deep link सीधे Restaurant screen खोलता है — कोई अलग config नहीं।

## 🟡 Real Example Hindi mein
**Swiggy:** WhatsApp पर share किया restaurant link `https://swiggy.example/restaurant/55` ऐप में सीधे उसी restaurant की file `restaurant/[id].tsx` खोल देता है, क्योंकि file path ही URL है।

---

## 💻 Code Example — Basic
```tsx
// app/_layout.tsx — root layout
import { Stack } from 'expo-router';                    // Stack navigator

export default function RootLayout() {
  return (
    <Stack>                                             {/* सारी screens stack में */}
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} /> {/* tabs का अपना header */}
      <Stack.Screen name="restaurant/[id]" options={{ title: 'Restaurant' }} /> {/* detail header */}
    </Stack>
  );
}
```
```tsx
// app/(tabs)/_layout.tsx — bottom tabs
import { Tabs } from 'expo-router';                     // Tabs navigator

export default function TabsLayout() {
  return (
    <Tabs>                                              {/* bottom tab bar */}
      <Tabs.Screen name="index" options={{ title: 'Home' }} />     {/* app/(tabs)/index.tsx */}
      <Tabs.Screen name="orders" options={{ title: 'Orders' }} />  {/* app/(tabs)/orders.tsx */}
    </Tabs>
  );
}
```
```tsx
// app/(tabs)/index.tsx — Home
import { View, Text } from 'react-native';              // UI
import { Link } from 'expo-router';                     // declarative navigation

export default function Home() {
  return (
    <View style={{ padding: 20 }}>
      <Text>Home</Text>
      {/* /restaurant/r123 पर ले जाता है */}
      <Link href="/restaurant/r123">Open Barbeque Nation</Link>
    </View>
  );
}
```
```tsx
// app/restaurant/[id].tsx — dynamic route
import { Text, View } from 'react-native';              // UI
import { useLocalSearchParams } from 'expo-router';     // params hook

export default function Restaurant() {
  const { id } = useLocalSearchParams<{ id: string }>(); // URL segment से id (हमेशा string)
  return (
    <View style={{ padding: 20 }}>
      <Text>Restaurant id: {id}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
```tsx
// Auth guard + imperative navigation + query params + 404
// app/_layout.tsx
import { useEffect, useState } from 'react';              // hooks
import { Slot, useRouter, useSegments } from 'expo-router'; // Slot = child render, hooks
import * as SplashScreen from 'expo-splash-screen';       // splash control

SplashScreen.preventAutoHideAsync();                      // load पूरा होने तक splash रखो

export default function RootLayout() {
  const router = useRouter();                             // imperative router
  const segments = useSegments();                         // current path segments, e.g. ['(auth)','login']
  const [ready, setReady] = useState(false);              // token load हुआ?
  const [token, setToken] = useState<string | null>(null); // login token

  useEffect(() => {
    (async () => {
      try {
        // यहाँ SecureStore.getItemAsync('token') आएगा (demo में null)
        setToken(null);                                   // logged-out मान लो
      } finally {
        setReady(true);                                   // हमेशा ready करो
        SplashScreen.hideAsync();                         // splash हटाओ
      }
    })();
  }, []);

  useEffect(() => {
    if (!ready) return;                                   // load तक इंतज़ार
    const inAuth = segments[0] === '(auth)';              // क्या auth group में हैं
    if (!token && !inAuth) router.replace('/(auth)/login'); // login नहीं -> login पर
    if (token && inAuth) router.replace('/');             // login है -> home
  }, [ready, token, segments]);                           // deps

  return <Slot />;                                        // matching child layout/screen
}

// कहीं से भी navigate:
// router.push({ pathname: '/restaurant/[id]', params: { id: 'r9', tab: 'reviews' } }); // params + query
// router.back();                                         // पीछे
// router.replace('/orders');                             // history बदले बिना

// app/+not-found.tsx
// import { Link } from 'expo-router';
// export default () => <Link href="/">Page नहीं मिला — Home जाओ</Link>;
```
नोट: `(auth)/login.tsx` file भी बनानी होगी; auth guard का यह तरीका docs में recommended pattern जैसा है, पर navigation-ready होने से पहले `router.replace` call करने पर error आता है — इसलिए `ready` flag है।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Routing code | Same | Same |
| Back | Hardware back -> `router.back()` जैसा | Swipe-back / header back |
| Deep link scheme | `app.json` `scheme` + intent filters (prebuild बनाता है) | `scheme` + Info.plist; Universal Links के लिए Associated Domains |
| Web links verify | Android App Links: `assetlinks.json` | Apple: `apple-app-site-association` |
| Tabs look | Material-style bar | iOS-style bar |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app/orders.tsx — file बनाना ही routing
import { Link } from 'expo-router';
export default () => <Link href="/orders">Orders</Link>;
```
CLI way (bare RN) — manual React Navigation:
```jsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
const Stack = createNativeStackNavigator();
// हर screen को हाथ से register + linking config अलग
<NavigationContainer linking={{ prefixes: ['zomato://'], config: { screens: { Orders: 'orders' } } }}>
  <Stack.Navigator><Stack.Screen name="Orders" component={Orders} /></Stack.Navigator>
</NavigationContainer>
```
Expo Router bare RN में भी चल सकता है (expo package install करके), पर setup Expo project में सबसे आसान है।

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** `app/` के बाहर screens रखना
✅ **Correct:** Routes सिर्फ `app/` में; components `components/` में रखो (वरना हर file route बन जाएगी)।

❌ **Mistake 2:** `useLocalSearchParams` का `id` को number मान लेना
✅ **Correct:** यह string (या string[]) है: `Number(id)`।

❌ **Mistake 3:** `useGlobalSearchParams` हर जगह use करना -> बिना ज़रूरत re-render
✅ **Correct:** आम तौर पर `useLocalSearchParams` use करो।

❌ **Mistake 4:** Root `_layout` में navigator mount होने से पहले `router.replace` call करना
✅ **Correct:** `useEffect` में, ready flag के बाद (ऊपर Advanced example)।

---

## 🧠 Tricky Interview Question
**Q: `app/(tabs)/profile.tsx` और `app/profile.tsx` दोनों हों तो क्या होगा?**

**Answer:** दोनों का URL `/profile` बनता है (group `(tabs)` URL में नहीं आता) — conflict/ambiguity होती है और Expo Router warn या error देता है। Group sibling routes का नाम unique रखो।

---

## ⚫ Interview Questions + Answers
**Q1: Expo Router क्या है और किस पर बना है?**
A1: File-based router, React Navigation के ऊपर; navigators वही हैं, config files से बनती है।

**Q2: `_layout.tsx` क्या करता है?**
A2: अपने folder की screens के लिए navigator (Stack/Tabs/Drawer/Slot) define करता है और shared UI/providers रखने की जगह है।

**Q3: Dynamic route कैसे बनाते हैं?**
A3: File का नाम `[id].tsx`; params `useLocalSearchParams()` से।

**Q4: Deep linking के लिए क्या चाहिए?**
A4: `app.json` में `scheme`; Router बाकी mapping खुद करता है। Universal/App Links के लिए domain verification अलग से।

**Q5: Expo Go में चलता है?**
A5: हाँ (SDK के साथ आने वाले modules), पर custom native modules पर development build चाहिए।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- नया Expo ऐप, deep links/web चाहिए
- बड़ी team, screens की साफ structure
- Typed routes (experiments.typedRoutes) चाहिए

❌ Avoid when:
- पहले से बड़ा React Navigation ऐप जिसमें कस्टम dynamic navigator logic है (migration cost)
- पूरी तरह code-defined/runtime-generated routes चाहिए

---

## 📊 Visual Diagram
```
app/                               URL
├─ _layout.tsx   (Stack)
├─ (tabs)/
│   ├─ _layout.tsx (Tabs)
│   ├─ index.tsx            ->  /
│   └─ orders.tsx           ->  /orders
├─ restaurant/
│   └─ [id].tsx             ->  /restaurant/:id
└─ +not-found.tsx           ->  कोई match नहीं
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| File-based routing | File path = route | File का path ही route |
| _layout | Navigator wrapper file | Navigator वाली file |
| Dynamic route | [param] segment | बदलने वाला segment |
| Group (name) | Folder not in URL | URL में न दिखने वाला folder |
| Slot | Renders matched child | Match हुआ child दिखाता है |
| Typed routes | Type-checked hrefs | Type-checked links |

---

## ⚡ 3-Line Summary
English:
1. Files in `app/` become routes; `_layout.tsx` defines the navigator.
2. `[id]` is dynamic, `(group)` is hidden from the URL, `+not-found` handles 404.
3. Navigate with `Link` / `router`, read params with `useLocalSearchParams`; deep links come built-in.

Hindi:
1. `app/` की files routes बनती हैं; `_layout.tsx` navigator तय करती है।
2. `[id]` dynamic है, `(group)` URL में नहीं दिखता, `+not-found` 404 संभालता है।
3. `Link` / `router` से navigate, `useLocalSearchParams` से params; deep links अंतर्निहित हैं।

---

## ➡️ Next Topic
**78. Expo Router vs React Navigation** — कब कौन सा चुनें।
