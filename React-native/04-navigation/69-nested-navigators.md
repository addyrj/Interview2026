# 69. Nested Navigators
# हिंदी में: Nested Navigators (Navigator के अंदर Navigator)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76)** with **React Navigation v7** — check current docs — APIs change between SDKs. (Expo Router में nesting folders/layouts से होती है — topic 77।)

---

## 🔵 Simple Definition (English)
**Nesting** means rendering one navigator **inside a screen of another navigator** — e.g. a Stack whose first screen is a Tab navigator, where each tab has its own Stack. It lets you build real app structures: tabs + detail pages + auth flow.

## 🔵 सरल परिभाषा (Hindi)
**Nesting** का मतलब है एक navigator को **दूसरे navigator की screen के अंदर** रखना — जैसे Stack की पहली screen Tab navigator हो और हर tab का अपना Stack हो। इससे असली app structure बनता है: tabs + detail pages + auth flow।

---

## 🔴 Problem it Solves
```
❌ Ek hi flat Stack: har screen par bottom tabs nahi dikhte / ya hamesha dikhte hain
❌ Tabs ke andar "Restaurant Details" kholna ho to tab bar chupana / dikhana?
❌ Login screens (no tabs) aur Home (tabs) ek navigator me mix nahi ho sakte
✅ Nesting: har part ka apna navigator, apni history
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ एक flat Stack: हर screen पर tabs दिखें या कभी न दिखें
❌ Tab के अंदर "Restaurant Details" खोलनी हो तो tab bar रखें या छुपाएँ?
❌ Login screens (बिना tabs) और Home (tabs वाला) एक navigator में मिक्स नहीं हो सकते
✅ Nesting: हर हिस्से का अपना navigator और अपनी history
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Create navigators: RootStack, Tab, HomeStack
Step 2 → Use a navigator component as the `component` of a parent screen
Step 3 → Child navigator manages its own history/state
Step 4 → navigation.navigate('Name') first tries CURRENT navigator,
         then bubbles UP to parents (not down into unknown children)
Step 5 → To go into a nested screen use:
         navigate('Home', { screen: 'Details', params: {id: 1} })
Step 6 → Header: parent + child may both show headers -> hide one (headerShown:false)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Navigators बनाओ: RootStack, Tab, HomeStack
Step 2 → Child navigator को parent की screen का `component` बनाओ
Step 3 → Child अपनी history/state खुद सँभालता है
Step 4 → navigate('Name') पहले CURRENT navigator में ढूँढता है,
         फिर ऊपर parents में bubble करता है
Step 5 → Nested screen खोलने के लिए:
         navigate('Home', { screen: 'Details', params: {id: 1} })
Step 6 → Parent और child दोनों के headers दिखें तो एक में headerShown:false करो
```

---

## 🟡 Real World Example
**Swiggy**: Root Stack -> (Login flow) or (Main). Main = Bottom Tabs (Home, Search, Cart, Account). The Home tab has its own stack: Home -> Restaurant -> Dish detail. Cart opens "Checkout" which hides the tab bar. **Paytm** has the same pattern: tabs + deep stacks + modal for payments.

## 🟡 Real Example Hindi mein
**Swiggy**: Root Stack -> (Login flow) या (Main)। Main = Bottom Tabs (Home, Search, Cart, Account)। Home tab का अपना stack है: Home -> Restaurant -> Dish detail। Cart से "Checkout" खुलता है जिसमें tab bar छुपा होता है। **Paytm** में भी यही pattern है: tabs + deep stacks + payments के लिए modal।

---

## 💻 Code Example — Basic
```jsx
// Basic nesting: Root Stack -> Tabs -> (Home, Profile) + Details on Root
import React from 'react';                                          // React
import { View, Text, Button } from 'react-native';                  // UI
import { NavigationContainer } from '@react-navigation/native';     // container
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';    // tabs

const Stack = createNativeStackNavigator();                         // root stack
const Tabs = createBottomTabNavigator();                            // tabs

function Home({ navigation }) {                                     // Home tab screen
  return (
    <View style={{ flex: 1, justifyContent: 'center' }}>
      <Text>Home</Text>
      {/* Details lives in ROOT stack (parent) -> navigate bubbles up automatically */}
      <Button title="Open Details" onPress={() => navigation.navigate('Details')} />
    </View>
  );
}
const Profile = () => <View style={{ flex: 1 }}><Text>Profile</Text></View>; // Profile tab
const Details = () => <View style={{ flex: 1 }}><Text>Details</Text></View>; // detail screen

function MainTabs() {                                               // a navigator used as a screen
  return (
    <Tabs.Navigator>
      <Tabs.Screen name="Home" component={Home} />{/* tab 1 */}
      <Tabs.Screen name="Profile" component={Profile} />{/* tab 2 */}
    </Tabs.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>{/* ONE container only */}
      <Stack.Navigator>
        {/* hide root header: the tabs show their own headers */}
        <Stack.Screen name="Main" component={MainTabs} options={{ headerShown: false }} />
        <Stack.Screen name="Details" component={Details} />{/* covers the tab bar */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Auth switch + Tabs + per-tab Stack + navigating INTO nested screens
// + typed params with TypeScript-style JSDoc-free JS; real-world Swiggy structure
import React, { useState } from 'react';                            // React + state
import { View, Text, Button } from 'react-native';                  // UI
import { NavigationContainer } from '@react-navigation/native';     // container
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';    // tabs

const Root = createNativeStackNavigator();                          // level 1
const Tab = createBottomTabNavigator();                             // level 2
const HomeStack = createNativeStackNavigator();                     // level 3 (inside Home tab)

function HomeScreen({ navigation }) {
  return (
    <View style={{ flex: 1, justifyContent: 'center' }}>
      <Button title="Biryani House" onPress={() =>
        navigation.navigate('Restaurant', { id: 42 })} />{/* same stack -> simple navigate */}
    </View>
  );
}
function RestaurantScreen({ route, navigation }) {
  return (
    <View style={{ flex: 1, justifyContent: 'center' }}>
      <Text>Restaurant #{route.params.id}</Text>{/* read param */}
      {/* Jump to a screen in a DIFFERENT tab: give parent screen name + nested screen */}
      <Button title="Go to Order History" onPress={() =>
        navigation.navigate('Account', { screen: 'Orders', params: { highlight: 7 } })} />
    </View>
  );
}
function HomeStackScreen() {                                        // stack inside Home tab
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="HomeList" component={HomeScreen} options={{ title: 'Swiggy' }} />
      <HomeStack.Screen name="Restaurant" component={RestaurantScreen} />
    </HomeStack.Navigator>
  );
}
const AccountStack = createNativeStackNavigator();                  // stack inside Account tab
function OrdersScreen({ route }) {
  return <View style={{ flex: 1 }}><Text>Orders (highlight {String(route.params?.highlight)})</Text></View>;
}
function AccountHome() { return <View style={{ flex: 1 }}><Text>Account</Text></View>; }
function AccountStackScreen() {
  return (
    <AccountStack.Navigator>
      <AccountStack.Screen name="AccountHome" component={AccountHome} />
      <AccountStack.Screen name="Orders" component={OrdersScreen} />
    </AccountStack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>{/* child stacks own headers */}
      <Tab.Screen name="Home" component={HomeStackScreen} />
      <Tab.Screen name="Account" component={AccountStackScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  const [signedIn, setSignedIn] = useState(false);                  // fake auth state
  return (
    <NavigationContainer>
      <Root.Navigator screenOptions={{ headerShown: false }}>
        {signedIn ? (
          <Root.Screen name="Main" component={MainTabs} />          // logged-in tree
        ) : (
          <Root.Screen name="Login">
            {() => <View style={{ flex: 1, justifyContent: 'center' }}>
              <Button title="Login" onPress={() => setSignedIn(true)} /></View>}
          </Root.Screen>                                            // logged-out tree
        )}
      </Root.Navigator>
    </NavigationContainer>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Hardware back | Pops innermost navigator first, then parents | No hardware back |
| Swipe back | Not default | Edge swipe pops the focused stack |
| Header duplication | Same problem (double header) | Same problem |
| Tab bar over details | Tab bar hidden when detail is in root stack | Same |
| Native stack animation | Slide-from-right/fade (default varies) | Native push transition |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Router: nesting = folders. app/(tabs)/_layout.jsx is the tab layout,
// app/(tabs)/home/_layout.jsx is a Stack inside the Home tab (see topic 77)
import { Tabs } from 'expo-router';
export default function TabsLayout() { return <Tabs screenOptions={{ headerShown: false }} />; }
```
CLI way:
```jsx
// CLI (React Navigation only): nesting = components, as shown above.
// Extra: install native deps and rebuild
// npm i @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs
// npm i react-native-screens react-native-safe-area-context && cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Two `NavigationContainer`s (one inside a nested navigator)
✅ Correct: exactly ONE `NavigationContainer` at the root.

❌ Mistake 2: Navigating to a screen that is not mounted yet / in a sibling
```jsx
navigation.navigate('Orders');   // ❌ Orders is inside Account tab not yet rendered
```
✅ Correct: `navigation.navigate('Account', { screen: 'Orders' })`.

❌ Mistake 3: Double headers (stack header + tab header)
✅ Correct: `headerShown: false` on the parent that wraps navigators.

❌ Mistake 4: Nesting same navigator type deeply without need (Stack in Stack in Stack)
✅ Correct: keep nesting shallow; use grouped screens (`Stack.Group`) for shared options.

---

## 🧠 Tricky Interview Question
**Q: You call `navigation.navigate('Details')` from a screen inside a tab, but `Details` is defined in the root stack. Does it work? And what if `Details` is inside a *sibling* navigator?**

**Answer:** Yes for the root stack: React Navigation first tries to handle the action in the **current** navigator, and if it cannot, it **bubbles up to the parent**. So root-level `Details` works and opens above the tabs (tab bar hidden). If `Details` is inside a *sibling* navigator, actions do not travel sideways/downwards into unknown navigators — you must target it with `navigate('ParentName', { screen: 'Details' })`. Note: nested screen exists only after the parent navigator is rendered; with `initial: false` you can control whether the nested initial route is also mounted (check docs for your version).

---

## ⚫ Interview Questions + Answers

**Q1: What is a nested navigator?**
A1: A navigator rendered as a screen (component) inside another navigator.

**Q2: How do you navigate to a screen in a nested navigator?**
A2: `navigation.navigate('Parent', { screen: 'Child', params: {...} })`.

**Q3: What happens with the header when nesting?**
A3: Each navigator can show a header, so you may get two. Set `headerShown: false` on the parent screen.

**Q4: How do params work with nesting?**
A4: Params go to the screen you target. Pass them via `params` inside the nested `params`. Parent screens can read nested route info through `useRoute` of their own route only.

**Q5: Where should auth flow go?**
A5: At the root: conditionally render different screens/navigators based on auth state (logged-in vs logged-out groups).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tabs + stack details, drawer + tabs, auth + main
- Each section needs separate back history
- Hiding tab bar on certain screens by placing them in the root

❌ Avoid when:
- A flat stack is enough
- Nesting 4+ levels (hard to debug, many headers, perf)

---

## 📊 Visual Diagram
```
NavigationContainer
└─ Root Stack
   ├─ Login (logged out)
   └─ Main (logged in)  = Tab Navigator
       ├─ Home tab    = Stack [HomeList -> Restaurant]
       ├─ Cart tab
       └─ Account tab = Stack [AccountHome -> Orders]
   └─ Checkout (modal, covers tabs)

navigate bubbles:  child -> parent -> grandparent
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Nesting | Navigator inside a screen | Screen के अंदर navigator |
| Bubbling | Unhandled action goes up | Action का ऊपर जाना |
| `screen` param | Target nested screen | Nested screen का target |
| `headerShown` | Show/hide header | Header दिखाना/छुपाना |
| Auth flow | Logged in/out screen groups | Login/logout screens |
| Navigator state | History of one navigator | एक navigator की history |

---

## ⚡ 3-Line Summary
**English:**
1. Nested navigators = one navigator as a screen of another (Stack > Tabs > Stack).
2. Actions bubble up; to go down use `navigate('Parent', { screen: 'Child' })`.
3. One `NavigationContainer`, hide duplicate headers, keep nesting shallow.

**Hindi:**
1. Nested navigators = एक navigator दूसरे की screen (Stack > Tabs > Stack)।
2. Action ऊपर bubble होता है; नीचे जाने को `navigate('Parent', { screen: 'Child' })`।
3. सिर्फ एक `NavigationContainer`, double header छुपाओ, nesting कम रखो।

---

## ➡️ Next Topic
**70. Navigation Props (navigate, goBack, push, replace)** — screen बदलने के सारे methods।
