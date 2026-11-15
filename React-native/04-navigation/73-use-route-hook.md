# 73. useRoute Hook
# हिंदी में: useRoute Hook — Current Screen की Route Info पाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Targets: Expo SDK 52 (React Native 0.76) + React Navigation v7 (check current docs — APIs change between SDKs). v6 में भी `useRoute` वैसा ही है।

---

## 🔵 Simple Definition (English)
`useRoute()` is a React Navigation hook that returns the **route object** of the screen it is called in: `{ key, name, params, path? }`. It lets any component (even deeply nested, not a screen) read the current screen's params without receiving the `route` prop.

## 🔵 सरल परिभाषा (Hindi)
`useRoute()` एक React Navigation hook है जो उस screen का **route object** देता है जिसमें इसे call किया गया: `{ key, name, params, path? }`। इससे कोई भी component (nested भी, जो screen नहीं है) बिना `route` prop मिले current screen के params पढ़ सकता है।

---

## 🔴 Problem it Solves
```
BEFORE useRoute (prop drilling):
  DetailScreen({ route })            <- route prop मिला
    └─ <Header route={route} />      <- pass करना पड़ा
         └─ <Title route={route} />  <- फिर pass करना पड़ा

Zomato Restaurant screen:
  restaurantId चाहिए: Header, MenuList, ReviewList, CartBar सबको.
  हर जगह prop pass करना = messy code.

WITH useRoute:
  हर child खुद: const { params } = useRoute();  // prop drilling खत्म
```

## 🔴 यह क्यों बना? (Hindi)
Screen को `route` prop मिलता है, लेकिन उसके नीचे के components को नहीं। Prop drilling से बचने के लिए `useRoute()` बना — कोई भी child component सीधे अपनी screen का route पढ़ सकता है। Class components में यह hook नहीं चलता (वहाँ `route` prop use करो)।

---

## 🟢 How it Works — Step by Step
```
Step 1 → NavigationContainer हर screen को एक RouteContext में wrap करता है
Step 2 → Screen render होती है; उसके अंदर के सारे components उसी context में हैं
Step 3 → component में useRoute() call होता है
Step 4 → Hook nearest screen का route object return करता है
Step 5 → route.params, route.name, route.key पढ़ो
Step 6 → navigation.setParams() से params बदले → route नया object बनता है → re-render
```

Route object का shape:
```
{
  key:    'ProductDetail-aB3xY',   // unique id of this screen instance
  name:   'ProductDetail',         // screen का नाम
  params: { productId: '42' },     // navigate() में भेजा data (undefined भी हो सकता है!)
  path:   '/product/42'            // सिर्फ deep link से खुला तो
}
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Navigator हर screen को RouteContext में रखता है
2. Screen के अंदर कहीं भी useRoute() बुलाओ
3. Hook सबसे पास वाली screen का route object देता है
4. route.params से data पढ़ो (undefined भी हो सकता है, इसलिए default दो)
5. setParams() से params बदलें तो component दोबारा render होता है
```

---

## 🟡 Real World Example
**Zomato Restaurant page:** Home से `navigate('Restaurant', { restaurantId: 'r123' })`. Restaurant screen के अंदर `MenuList`, `OffersBanner`, `CartBar` — तीनों अलग components हैं और तीनों को `restaurantId` चाहिए। हर एक में `useRoute().params.restaurantId` पढ़ा जाता है; screen से कोई prop pass नहीं करना पड़ता।

## 🟡 Real Example Hindi mein
**Swiggy:** Order tracking screen `navigate('Track', { orderId })` से खुलती है। Map, Delivery-partner card और ETA bar अलग components हैं; सब `useRoute()` से `orderId` लेकर अपना-अपना API call करते हैं।

---

## 💻 Code Example — Basic
```jsx
import React from 'react';                                  // React import
import { View, Text, StyleSheet, Pressable } from 'react-native'; // RN UI components
import { NavigationContainer, useRoute, useNavigation } from '@react-navigation/native'; // hooks + container
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack navigator

const Stack = createNativeStackNavigator();                 // stack बनाओ

// Nested child component — screen नहीं है, फिर भी route पढ़ सकता है
function DishTitle() {
  const route = useRoute();                                 // current screen का route
  const { dishName = 'Unknown' } = route.params ?? {};      // params undefined हो सकता है, default दो
  return <Text style={styles.title}>{dishName}</Text>;      // title दिखाओ
}

// Home screen: list से detail पर जाओ
function HomeScreen() {
  const navigation = useNavigation();                       // navigation object
  return (
    <View style={styles.center}>
      <Pressable
        onPress={() => navigation.navigate('Dish', { dishName: 'Butter Chicken', price: 350 })} // params भेजो
      >
        <Text>Open Butter Chicken</Text>
      </Pressable>
    </View>
  );
}

// Detail screen: route prop की जगह child में hook use हो रहा है
function DishScreen() {
  const route = useRoute();                                 // इस screen का route
  return (
    <View style={styles.center}>
      <DishTitle />                                         {/* बिना prop के title */}
      <Text>Screen name: {route.name}</Text>                {/* 'Dish' */}
      <Text>Price: ₹{route.params?.price}</Text>            {/* optional chaining से safe */}
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>                                   {/* navigation root */}
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} /> {/* पहली screen */}
        <Stack.Screen name="Dish" component={DishScreen} /> {/* detail screen */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // center layout
  title: { fontSize: 22, fontWeight: '700' },                           // title style
});
```

## 💻 Code Example — Advanced
```tsx
// TypeScript: typed route + custom hook + params update + Android/iOS handling
import React, { useEffect, useLayoutEffect } from 'react';              // React hooks
import { Platform, Text, View, Button } from 'react-native';            // RN basics
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native'; // nav hooks + type
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'; // nav type

// सारी screens और उनके params का type
type RootStackParamList = {
  Home: undefined;                                                      // Home को params नहीं
  Restaurant: { restaurantId: string; tab?: 'menu' | 'reviews' };       // tab optional
};

// Custom hook: typed params + safe default, किसी भी child में reuse
function useRestaurantParams() {
  const route = useRoute<RouteProp<RootStackParamList, 'Restaurant'>>(); // typed route
  return {
    restaurantId: route.params.restaurantId,                            // required param
    tab: route.params.tab ?? 'menu',                                    // default tab
  };
}

function TabSwitcher() {
  const { tab } = useRestaurantParams();                                // child में params
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList, 'Restaurant'>>(); // typed nav
  return (
    <View>
      <Text>Current tab: {tab}</Text>
      {/* setParams सिर्फ current screen के params merge करता है, नई screen नहीं खोलता */}
      <Button title="Reviews" onPress={() => navigation.setParams({ tab: 'reviews' })} />
    </View>
  );
}

export default function RestaurantScreen() {
  const { restaurantId } = useRestaurantParams();                       // id पढ़ो
  const navigation = useNavigation();                                   // header set करने के लिए

  useLayoutEffect(() => {
    navigation.setOptions({ title: `Restaurant #${restaurantId}` });    // header title dynamic
  }, [navigation, restaurantId]);                                       // deps

  useEffect(() => {
    const controller = new AbortController();                           // unmount पर request cancel
    fetch(`https://api.example.com/restaurants/${restaurantId}`, { signal: controller.signal }) // fetch
      .then((r) => r.json())                                            // JSON parse
      .catch((e) => { if (e.name !== 'AbortError') console.warn(e); }); // error handling
    return () => controller.abort();                                    // cleanup
  }, [restaurantId]);                                                   // id बदले तो फिर fetch

  return (
    <View style={{ paddingTop: Platform.OS === 'android' ? 8 : 0 }}>   {/* platform-specific padding */}
      <TabSwitcher />
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `useRoute()` behaviour | Same JS API | Same JS API |
| Hardware back button | Screen pop → पिछली screen का route active | N/A (swipe-back gesture) |
| Params persistence on app kill | Android OS process kill करे तो state लौटाने के लिए `initialState` persistence चाहिए | iOS में भी वही; automatic नहीं |
| Deep link `route.path` | Intent URL से भरता है | Universal Link / URL scheme से भरता है |

Hook खुद platform-independent है — फर्क सिर्फ इस बात में है कि route कैसे बना (deep link, back, gesture)।

---

## 🟠 Expo vs CLI Difference
Expo way (Expo Router — `useRoute` की जगह अलग hooks):
```jsx
// app/restaurant/[id].js  — Expo Router में route object नहीं, hooks मिलते हैं
import { useLocalSearchParams } from 'expo-router';   // params पढ़ने का hook
export default function Restaurant() {
  const { id } = useLocalSearchParams();              // /restaurant/123 -> id = '123' (हमेशा string)
  return null;
}
```
CLI way (React Navigation, bare RN):
```jsx
import { useRoute } from '@react-navigation/native';  // standard hook
function Restaurant() {
  const { params } = useRoute();                      // params.id (original type, number भी हो सकता है)
  return null;
}
```
Note: Expo में भी React Navigation manually install करके `useRoute` use कर सकते हैं (Expo Router खुद React Navigation पर बना है)।

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** `route.params` को सीधे destructure करना
```jsx
const { id } = useRoute().params;      // ❌ params undefined हो तो crash
```
✅ **Correct:**
```jsx
const { id } = useRoute().params ?? {}; // ✅ safe default
```

❌ **Mistake 2:** `useRoute()` को screen से बाहर (NavigationContainer के बाहर) call करना
```jsx
// App.js में NavigationContainer के ऊपर useRoute() -> Error: Couldn't find a route object
```
✅ **Correct:** सिर्फ screen या उसके child component में use करो; global जगह के लिए `useNavigationContainerRef` use करो।

❌ **Mistake 3:** `route.params` को mutate करना (`route.params.x = 1`)
✅ **Correct:** `navigation.setParams({ x: 1 })` use करो।

---

## 🧠 Tricky Interview Question
**Q: Stack में Home -> Detail(id=1) -> Detail(id=2) है। Detail के अंदर `useRoute().params.id` क्या देगा, और ऊपर वाली Detail का id क्या रहता है?**

**Answer:** अगर दूसरी Detail `navigation.push('Detail', {id:2})` से बनी है तो stack में दो अलग screen instances हैं, हर एक का अपना `route.key` और अपने params। `useRoute()` हमेशा **उस component की अपनी screen** का route देता है, पूरे stack का नहीं — इसलिए ऊपर वाली Detail `id=2` और नीचे वाली `id=1` देखती है। `navigate` का behaviour (नई instance बनाना या मौजूदा को reuse/update करना) React Navigation v6 और v7 में अलग है, इसलिए नई instance चाहिए तो `push` use करो और अपने version के docs देखो।

---

## ⚫ Interview Questions + Answers
**Q1: `useRoute` और `route` prop में क्या फर्क है?**
A1: दोनों same object हैं। prop सिर्फ screen component को मिलता है; hook किसी भी nested function component में मिलता है।

**Q2: क्या `useRoute` class component में चलता है?**
A2: नहीं, hooks सिर्फ function components में हैं। Class में `this.props.route` use करो या `withNavigation`-style wrapper बनाओ।

**Q3: `route.key` किसलिए है?**
A3: हर screen instance की unique id। `setParams` को दूसरी screen के लिए `{source: key}` देने या state restore में काम आती है।

**Q4: `useRoute` और `useNavigation` में फर्क?**
A4: `useRoute` = "मैं कहाँ हूँ और मुझे क्या data मिला" (read). `useNavigation` = "अब कहाँ जाऊँ" (actions: navigate, goBack, setParams).

**Q5: Params बदलने पर component re-render होता है?**
A5: हाँ, `setParams` के बाद route object बदलता है और `useRoute` वाले components re-render होते हैं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Nested components को screen के params चाहिए
- Custom hook बनाना है जो route params पर depend करे
- Prop drilling कम करनी है

❌ Avoid when:
- Screen component में पहले से `route` prop है और सिर्फ एक level है (prop ही सरल है)
- Navigation से बाहर का global state चाहिए (Zustand/Redux use करो)
- Expo Router use कर रहे हो (वहाँ `useLocalSearchParams`)

---

## 📊 Visual Diagram
```
NavigationContainer
  └─ Stack.Navigator
       └─ Screen "Restaurant" (route = {name, key, params})
            │   RouteContext.Provider value=route
            ├─ <Header />     -> useRoute() -> route
            ├─ <MenuList />   -> useRoute() -> route
            └─ <CartBar />    -> useRoute() -> route

Screen "Cart" का अपना अलग RouteContext है (अलग route object)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| route | Object describing current screen | Current screen का object |
| params | Data passed during navigate | navigate के साथ भेजा data |
| route.key | Unique screen instance id | Screen instance की unique id |
| RouteContext | Context that carries route | Route ले जाने वाला context |
| setParams | Merge new params into route | Params update करना |
| RouteProp | TypeScript type for route | Route का TypeScript type |

---

## ⚡ 3-Line Summary
English:
1. `useRoute()` returns the current screen's `{ key, name, params }` from any nested component.
2. It removes prop drilling; read-only — change params using `navigation.setParams`.
3. Always default `params` (`?? {}`) and type it with `RouteProp`; Expo Router uses `useLocalSearchParams`.

Hindi:
1. `useRoute()` किसी भी nested component में current screen का `{ key, name, params }` देता है।
2. Prop drilling खत्म; यह read-only है — params बदलने के लिए `navigation.setParams` use करो।
3. `params` को हमेशा default दो (`?? {}`) और `RouteProp` से type करो; Expo Router में `useLocalSearchParams` है।

---

## ➡️ Next Topic
**76. Navigation Lifecycle** — Screen focus/blur/unmount कैसे होते हैं और data कब refresh करें।
