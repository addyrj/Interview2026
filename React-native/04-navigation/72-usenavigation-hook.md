# 72. useNavigation Hook
# हिंदी में: useNavigation Hook — बिना prop के navigation
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76)** with **React Navigation v7** — check current docs — APIs change between SDKs. (Expo Router में `useRouter()` इसका equivalent है।)

---

## 🔵 Simple Definition (English)
`useNavigation()` is a hook from `@react-navigation/native` that returns the **`navigation` object** of the nearest screen — so **any component** (not only screens) can navigate without receiving `navigation` as a prop.

## 🔵 सरल परिभाषा (Hindi)
`useNavigation()` `@react-navigation/native` का hook है जो सबसे नज़दीकी screen का **`navigation` object** लौटाता है — इसलिए **कोई भी component** (सिर्फ़ screens नहीं) बिना prop लिए navigate कर सकता है।

---

## 🔴 Problem it Solves
```
❌ Screen -> Card -> Button: navigation prop 3 level neeche pass karna (prop drilling)
❌ Sirf registered screens ko navigation prop milta hai
❌ Reusable components (Header, ProductCard) screen-specific nahi hone chahiye
✅ useNavigation(): jahan zarurat, wahin hook
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Screen -> Card -> Button: navigation prop 3 level नीचे pass करना (prop drilling)
❌ सिर्फ़ registered screens को navigation prop मिलता है
❌ Reusable components (Header, ProductCard) screen-specific नहीं होने चाहिए
✅ useNavigation(): जहाँ ज़रूरत, वहीं hook
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → NavigationContainer provides navigation context
Step 2 → Each screen is wrapped in its own context (that screen's navigation)
Step 3 → Child component calls const navigation = useNavigation()
Step 4 → React reads nearest screen context -> returns navigation object
Step 5 → Call navigation.navigate(...) / goBack() / setOptions(...)
Step 6 → Rendering outside any screen/container -> error:
         "Couldn't find a navigation object"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → NavigationContainer navigation context देता है
Step 2 → हर screen अपने context में wrap होती है
Step 3 → Child component में const navigation = useNavigation() लिखो
Step 4 → React सबसे नज़दीकी screen का context पढ़कर object देता है
Step 5 → navigation.navigate(...) / goBack() / setOptions(...) call करो
Step 6 → किसी screen/container के बाहर use करोगे तो error आएगा:
         "Couldn't find a navigation object"
```

---

## 🟡 Real World Example
**Zomato**: a reusable `<RestaurantCard />` used in Home, Search and Favourites. The card itself calls `useNavigation()` and opens the restaurant page on tap. **Swiggy**: a header `<CartIcon />` inside every screen's header uses the hook to open Cart. **Paytm**: a shared `<BackButton />` component.

## 🟡 Real Example Hindi mein
**Zomato**: `<RestaurantCard />` Home, Search और Favourites तीनों में use होता है। Card खुद `useNavigation()` से tap पर restaurant page खोलता है। **Swiggy**: हर screen के header में `<CartIcon />` hook से Cart खोलता है। **Paytm**: shared `<BackButton />` component।

---

## 💻 Code Example — Basic
```jsx
// Basic: reusable button that navigates without props
import React from 'react';                                         // React
import { View, Text, Pressable, StyleSheet } from 'react-native';  // UI
import { NavigationContainer, useNavigation } from '@react-navigation/native'; // hook
import { createNativeStackNavigator } from '@react-navigation/native-stack';   // stack

const Stack = createNativeStackNavigator();                        // stack

// Reusable component: NOT a screen, so no `navigation` prop here
function CartButton() {
  const navigation = useNavigation();                              // get navigation via hook
  return (
    <Pressable style={styles.btn} onPress={() => navigation.navigate('Cart')}>
      <Text style={styles.txt}>Go to Cart</Text>
    </Pressable>
  );
}

function Home() {                                                  // screen
  return (
    <View style={styles.center}>
      <Text>Home</Text>
      <CartButton />{/* no props passed */}
    </View>
  );
}
const Cart = () => <View style={styles.center}><Text>Cart</Text></View>; // screen

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={Home} />
        <Stack.Screen name="Cart" component={Cart} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // centre
  btn: { backgroundColor: '#f97316', padding: 12, borderRadius: 8 },   // orange button
  txt: { color: '#fff', fontWeight: '700' },                           // white text
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: typed-style custom hook wrapping useNavigation + header button via setOptions
// + safe usage in event handlers and effects (production pattern)
import React, { useCallback, useEffect } from 'react';             // React hooks
import { Pressable, Text, Platform, BackHandler } from 'react-native'; // RN
import { useNavigation, useFocusEffect } from '@react-navigation/native'; // nav hooks

// Custom hook: app-specific navigation helpers (one place to change routes)
export function useAppNav() {
  const navigation = useNavigation();                              // base hook
  return {
    openRestaurant: useCallback(                                   // stable function reference
      (id) => navigation.navigate('Restaurant', { id }),
      [navigation]
    ),
    goHomeClean: useCallback(() => {
      // after logout: reset so back can't return
      navigation.reset({ index: 0, routes: [{ name: 'Home' }] });
    }, [navigation]),
    back: useCallback(() => {
      if (navigation.canGoBack()) navigation.goBack();             // safe back
    }, [navigation]),
  };
}

// Reusable card used on many screens
export function RestaurantCard({ item }) {
  const { openRestaurant } = useAppNav();                          // use helper
  return (
    <Pressable
      onPress={() => openRestaurant(item.id)}                      // navigate on tap
      android_ripple={{ color: '#eee' }}                           // Android ripple
      style={{ padding: 16 }}
    >
      <Text>{item.name}</Text>
    </Pressable>
  );
}

// Screen-level: set header button + handle Android back only while focused
export function CheckoutScreen() {
  const navigation = useNavigation();                              // hook inside a screen too
  const { back } = useAppNav();

  useEffect(() => {
    navigation.setOptions({                                        // customise header
      headerRight: () => <Text onPress={back}>Close</Text>,
    });
  }, [navigation, back]);

  useFocusEffect(                                                  // run only when screen focused
    useCallback(() => {
      if (Platform.OS !== 'android') return undefined;             // Android-only logic
      const sub = BackHandler.addEventListener('hardwareBackPress', () => {
        back();                                                    // custom back behaviour
        return true;                                               // we handled it
      });
      return () => sub.remove();                                   // cleanup on blur
    }, [back])
  );
  return null;
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Hook behaviour | Identical | Identical |
| Hardware back | Use `useFocusEffect` + `BackHandler` with the hook | No hardware back |
| Back gesture | n/a | `beforeRemove` also covers swipe |
| Header buttons via `setOptions` | Material-style header | Large-title/iOS style header |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Router: useRouter() replaces useNavigation for simple navigation
import { useRouter } from 'expo-router';
const router = useRouter();
router.push('/cart');
// useNavigation() from 'expo-router' / '@react-navigation/native' still works for setOptions etc.
```
CLI way:
```jsx
// CLI + React Navigation
import { useNavigation } from '@react-navigation/native';
const navigation = useNavigation();
navigation.navigate('Cart');
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling the hook outside a component / inside a callback
```jsx
const onPress = () => { const nav = useNavigation(); nav.navigate('X'); }  // ❌ hooks rule
```
✅ Correct: call at the top level of the component, use `nav` inside the handler.

❌ Mistake 2: Using it in a component rendered outside `NavigationContainer` (e.g. wrapper at app root)
✅ Correct: place such components inside a screen, or use a `navigationRef` (`createNavigationContainerRef()`).

❌ Mistake 3: Prop-drilling `navigation` to deep components "because it works"
✅ Correct: use the hook where needed.

❌ Mistake 4: Assuming the hook returns the ROOT navigator
✅ Correct: it returns the navigation of the **nearest screen**; use `navigation.getParent()` to reach parent navigators.

---

## 🧠 Tricky Interview Question
**Q: You call `useNavigation()` inside a component that is rendered by a stack screen inside a tab. You call `navigation.openDrawer()` — the Drawer is the grandparent. Does it work?**

**Answer:** `useNavigation()` gives the navigation object of the *nearest* screen (the stack screen), which has stack methods. Navigator-specific methods like `openDrawer` exist only on navigation objects of that navigator type. However, React Navigation **forwards unknown navigator actions upward** for actions such as `openDrawer`/`toggleDrawer` (they are dispatched as actions and bubble to a navigator that can handle them), so it usually works; the safe approach is `navigation.getParent('DrawerId')?.openDrawer()` with an `id` set on the drawer navigator, or `navigation.dispatch(DrawerActions.openDrawer())`. Mention that TypeScript will complain unless you type the hook.

---

## ⚫ Interview Questions + Answers

**Q1: Why use `useNavigation` instead of the prop?**
A1: Non-screen components don't get `navigation`; the hook avoids prop drilling.

**Q2: Does `useNavigation` work outside `NavigationContainer`?**
A2: No — error "Couldn't find a navigation object". Use `createNavigationContainerRef` for outside access.

**Q3: How to navigate from outside React (e.g. an axios 401 interceptor)?**
A3: `const navigationRef = createNavigationContainerRef(); <NavigationContainer ref={navigationRef}>` then `if (navigationRef.isReady()) navigationRef.navigate('Login')`.

**Q4: Is `useNavigation` the same object as the screen's prop?**
A4: Yes, for that screen. In nested components it is the nearest screen's navigation.

**Q5: How do you access the parent navigator?**
A5: `navigation.getParent()` (optionally with an id).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reusable/deep components need to navigate
- Custom hooks that wrap navigation logic
- Header buttons set from inside a screen

❌ Avoid when:
- Code runs outside React (use `navigationRef`)
- Component is outside `NavigationContainer`
- You only have a screen and the prop is available (prop is fine)

---

## 📊 Visual Diagram
```
NavigationContainer
 └─ Stack.Screen "Home"        <- navigation context for Home
      └─ <FlatList>
           └─ <RestaurantCard>
                └─ <Pressable>
                     useNavigation()  ──► reads nearest context
                                         (Home's navigation)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `useNavigation` | Hook returning navigation object | Navigation object देने वाला hook |
| Prop drilling | Passing props down many levels | Props को कई level नीचे भेजना |
| `navigationRef` | Navigate outside components | Component के बाहर navigate |
| `getParent` | Parent navigator's navigation | Parent navigator का navigation |
| `useFocusEffect` | Effect only while focused | सिर्फ़ focus में चलने वाला effect |
| Context | React's shared data mechanism | React का shared data तरीका |

---

## ⚡ 3-Line Summary
**English:**
1. `useNavigation()` returns the nearest screen's navigation object for any component.
2. Must run inside `NavigationContainer`; use `navigationRef` outside React.
3. Replaces prop drilling; use `getParent()` for parent navigators.

**Hindi:**
1. `useNavigation()` किसी भी component को नज़दीकी screen का navigation object देता है।
2. `NavigationContainer` के अंदर चलाओ; React के बाहर `navigationRef` use करो।
3. Prop drilling हटाता है; parent navigator के लिए `getParent()`।

---

## ➡️ Next Topic
**73. useRoute Hook** — बिना prop के current route और params पढ़ना।
