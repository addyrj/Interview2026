# 70. Navigation Props (navigate, goBack, push, replace)
# हिंदी में: Navigation Props — navigate, goBack, push, replace
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76)** with **React Navigation v7** — check current docs — APIs change between SDKs. (v7 में `navigate` का behaviour बदला: अब यह नई instance नहीं बनाता, existing route पर जाता है; duplicate चाहिए तो `push` या `navigate(..., { pop: ... })` — docs देखें।)

---

## 🔵 Simple Definition (English)
Every screen registered in a navigator receives a **`navigation` prop** (and a `route` prop). The `navigation` object has methods to move around: `navigate`, `goBack`, `push`, `replace`, `popToTop`, `setOptions`, `dispatch`, etc.

## 🔵 सरल परिभाषा (Hindi)
Navigator में register हर screen को एक **`navigation` prop** (और `route` prop) मिलता है। `navigation` object में screen बदलने के methods होते हैं: `navigate`, `goBack`, `push`, `replace`, `popToTop`, `setOptions`, `dispatch` आदि।

---

## 🔴 Problem it Solves
```
❌ Screens ko ek dusre se jodne ka koi standard tarika nahi
❌ "Back" kaise kare, "naya page" kaise khole, "login ke baad Home" kaise?
❌ Web me URL badalte hain; mobile me history stack ka khud management
✅ navigation prop: stack/tab/drawer sab me ek jaisa API
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Screens को आपस में जोड़ने का standard तरीका नहीं था
❌ "Back" कैसे करें, "नया page" कैसे खोलें, "login के बाद Home" कैसे?
❌ Web में URL बदलता है; mobile में history stack खुद सँभालनी पड़ती
✅ navigation prop: stack/tab/drawer सब में एक जैसा API
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Screen registered via <Stack.Screen name="A" component={A} />
Step 2 → Navigator injects props: { navigation, route } into A
Step 3 → navigation.navigate('B', params)  -> go to B (reuse if exists in stack)
Step 4 → navigation.push('B', params)      -> ALWAYS add new B on top
Step 5 → navigation.goBack()               -> pop one screen
Step 6 → navigation.replace('B')           -> swap current screen with B (no back to A)
Step 7 → navigation.popToTop()             -> go back to first screen in stack
Step 8 → Screens NOT registered with navigator (deep child components)
         don't get the prop -> use useNavigation() hook (topic 72)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <Stack.Screen name="A" component={A} /> से screen register होती है
Step 2 → Navigator A को props देता है: { navigation, route }
Step 3 → navigate('B', params) -> B पर जाओ (stack में हो तो वही use होती है)
Step 4 → push('B', params)     -> हमेशा ऊपर नई B जोड़ता है
Step 5 → goBack()              -> एक screen पीछे
Step 6 → replace('B')          -> current को B से बदलो (A पर back नहीं)
Step 7 → popToTop()            -> stack की पहली screen पर
Step 8 → Deep child components को prop नहीं मिलता -> useNavigation() hook (topic 72)
```

---

## 🟡 Real World Example
**Swiggy**: restaurant list -> `navigate('Restaurant', {id})`; "Add to cart" -> `navigate('Cart')`; after payment success -> `replace('OrderConfirmed')` so the back button doesn't return to payment; "Order again" -> `popToTop()`. **Paytm**: after OTP verify -> `replace('Home')` so user can't go back to OTP.

## 🟡 Real Example Hindi mein
**Swiggy**: restaurant list -> `navigate('Restaurant', {id})`; "Add to cart" -> `navigate('Cart')`; payment सफल होने पर -> `replace('OrderConfirmed')` ताकि back दबाने पर payment screen न आए; "Order again" -> `popToTop()`। **Paytm**: OTP verify के बाद `replace('Home')`, ताकि user OTP पर वापस न जा सके।

---

## 💻 Code Example — Basic
```jsx
// Basic: all four methods in one demo app
import React from 'react';                                         // React
import { View, Text, Button } from 'react-native';                 // UI
import { NavigationContainer } from '@react-navigation/native';    // container
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack

const Stack = createNativeStackNavigator();                        // stack navigator

function Home({ navigation }) {                                    // navigation prop injected
  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 20 }}>
      <Text>Home</Text>
      {/* navigate: go to Details, pass params */}
      <Button title="navigate Details" onPress={() => navigation.navigate('Details', { n: 1 })} />
      {/* replace: Home is removed from history; back won't return here */}
      <Button title="replace with Login" onPress={() => navigation.replace('Login')} />
    </View>
  );
}

function Details({ navigation, route }) {                          // also gets route
  const n = route.params?.n ?? 0;                                  // safe read of params
  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 20 }}>
      <Text>Details #{n}</Text>
      {/* push: always adds a NEW Details on top (n+1) */}
      <Button title="push Details again" onPress={() => navigation.push('Details', { n: n + 1 })} />
      {/* goBack: pop one */}
      <Button title="goBack" onPress={() => navigation.goBack()} />
      {/* popToTop: jump to first screen in this stack */}
      <Button title="popToTop" onPress={() => navigation.popToTop()} />
    </View>
  );
}

const Login = () => <View style={{ flex: 1 }}><Text>Login</Text></View>; // simple screen

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={Home} />
        <Stack.Screen name="Details" component={Details} />
        <Stack.Screen name="Login" component={Login} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: safe go-back, setOptions, reset after login, unsaved-changes guard
import React, { useLayoutEffect, useState, useCallback } from 'react'; // hooks
import { View, Text, Button, TextInput, Alert, Platform } from 'react-native'; // UI
import { CommonActions } from '@react-navigation/native';          // reset helper

// 1. Safe back: if nothing to go back to (e.g. deep link), go to Home
export function safeBack(navigation) {
  if (navigation.canGoBack()) {                                    // is there history?
    navigation.goBack();                                           // yes -> go back
  } else {
    navigation.navigate('Home');                                   // no -> fallback screen
  }
}

// 2. After login: wipe history so back button cannot return to Login
export function resetToHome(navigation) {
  navigation.dispatch(                                             // low-level action
    CommonActions.reset({
      index: 0,                                                    // active route = first in list
      routes: [{ name: 'Home' }],                                  // new history = [Home]
    })
  );
}

// 3. Screen using setOptions + beforeRemove guard
export function AddressForm({ navigation }) {
  const [text, setText] = useState('');                            // form input
  const dirty = text.length > 0;                                   // user typed something

  // setOptions: change header from inside the screen
  useLayoutEffect(() => {
    navigation.setOptions({
      title: 'Add Address',                                        // header title
      headerRight: () => (                                         // save button in header
        <Button title="Save" onPress={() => { setText(''); safeBack(navigation); }} />
      ),
    });
  }, [navigation]);

  // beforeRemove: runs on ANY way of leaving (header back, Android back, iOS swipe)
  useLayoutEffect(() => {
    const unsub = navigation.addListener('beforeRemove', (e) => {
      if (!dirty) return;                                          // nothing typed -> allow
      e.preventDefault();                                          // stop leaving
      Alert.alert('Discard changes?', 'You have unsaved address.', [
        { text: 'Stay', style: 'cancel' },                         // do nothing
        {
          text: 'Discard',
          style: 'destructive',                                    // red on iOS
          onPress: () => navigation.dispatch(e.data.action),       // continue original action
        },
      ]);
    });
    return unsub;                                                  // cleanup listener
  }, [navigation, dirty]);

  return (
    <View style={{ padding: 20 }}>
      <TextInput value={text} onChangeText={setText} placeholder="House, street, city" />
      <Text>{Platform.OS === 'android' ? 'Try the back button' : 'Try swipe-back'}</Text>
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `goBack()` trigger | Header back, hardware back button | Header back, edge swipe gesture |
| `beforeRemove` guard | Also catches hardware back | Also catches swipe gesture |
| `replace` animation | Native stack default animation | Push transition (customisable) |
| Hardware back at root | Exits app (or handled via `BackHandler`) | N/A |
| Gesture disable | `gestureEnabled: false` iOS only effect | Disables swipe back |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Router: imperative API via `router` (expo-router)
import { router } from 'expo-router';
router.push('/details/1');       // like push
router.navigate('/details/1');   // like navigate
router.replace('/login');        // like replace
router.back();                   // like goBack
```
CLI way:
```jsx
// CLI + React Navigation: use the navigation prop / hook (same on Expo with React Navigation)
navigation.navigate('Details', { id: 1 });
navigation.replace('Login');
navigation.goBack();
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `navigate` when you want a new copy (list of same screen type)
✅ Correct: use `push` for "Details -> Details" drill-down (v6; in v7 `navigate` re-uses only when params match rules — check docs).

❌ Mistake 2: Using `navigate('Home')` after login (back returns to Login)
✅ Correct: `replace('Home')` or `CommonActions.reset`, or switch conditional auth screens.

❌ Mistake 3: Calling `goBack()` when there's no history (nothing happens / warning)
✅ Correct: check `navigation.canGoBack()`.

❌ Mistake 4: Passing functions/non-serializable values as params
```jsx
navigation.navigate('B', { onDone: () => {} });   // ❌ warning, breaks state persistence/deep links
```
✅ Correct: pass ids; use events/context/store for callbacks.

---

## 🧠 Tricky Interview Question
**Q: Stack is `[Home, Details(id:1)]`. You call `navigation.navigate('Details', {id: 2})` on Details. What is the stack? What with `push`?**

**Answer:** In **React Navigation 6**, `navigate` to the *same route name that is already focused* does **not** add a new screen; it updates params of the existing one -> stack `[Home, Details(id:2)]`. `push` always adds -> `[Home, Details(1), Details(2)]`. In **v7** `navigate` was changed to a stricter "go to existing route in history or add new" semantics, and `push` remains the explicit way to always add (check the v7 upgrade guide for your version). Interview tip: always say "depends on version — use push when you need a new instance".

---

## ⚫ Interview Questions + Answers

**Q1: navigate vs push?**
A1: `navigate` goes to a screen (re-using an existing one by name in many cases). `push` always adds a new instance on top (stack navigator only).

**Q2: replace vs navigate?**
A2: `replace` swaps the current screen, so back goes to the previous one, not the replaced one. Used after login/payment.

**Q3: How do you go back N screens?**
A3: `navigation.pop(n)` in a stack, or `popToTop()`; `goBack()` goes one.

**Q4: How to read params?**
A4: Via `route.params` or `useRoute()`; set defaults with `initialParams`.

**Q5: How to prevent leaving a screen?**
A5: `navigation.addListener('beforeRemove', e => e.preventDefault())` and ask user to confirm.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Simple screen-to-screen moves with props from the navigator
- `replace`/`reset` for flows that must not be revisited (login, payment)

❌ Avoid when:
- Deep child component (not a screen) needs navigation: use `useNavigation` instead of prop-drilling
- Using Expo Router: prefer `router`/`Link`

---

## 📊 Visual Diagram
```
Stack: [Home]
navigate('Details')   -> [Home, Details]
push('Details')       -> [Home, Details, Details]
goBack()              -> [Home, Details]
replace('Login')      -> [Home, Login]       (Details gone)
popToTop()            -> [Home]
reset(routes:[Home])  -> [Home]  (history wiped)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `navigation` prop | Object with nav methods | Navigation methods वाला object |
| `route` prop | Current route name + params | Current route और params |
| `push` | Add new screen on top | ऊपर नई screen जोड़ना |
| `replace` | Swap current screen | Current screen बदलना |
| `popToTop` | Go to first screen | पहली screen पर वापस |
| `canGoBack` | Is back possible | Back संभव है या नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. Screens receive `navigation` and `route`; use `navigate`, `push`, `replace`, `goBack`, `popToTop`.
2. Use `replace`/`reset` after login/payment; `push` for same-screen drill-down.
3. Check `canGoBack()`, pass serializable params, and mind v6 vs v7 `navigate` behaviour.

**Hindi:**
1. Screens को `navigation` और `route` मिलते हैं; `navigate`, `push`, `replace`, `goBack`, `popToTop` use करो।
2. Login/payment के बाद `replace`/`reset`; same screen drill-down के लिए `push`।
3. `canGoBack()` check करो, serializable params दो, और v6 बनाम v7 `navigate` का फ़र्क याद रखो।

---

## ➡️ Next Topic
**71. Passing Params** — screens के बीच data भेजना (पहले से मौजूद note) और **72. useNavigation Hook** — बिना prop के navigation।
