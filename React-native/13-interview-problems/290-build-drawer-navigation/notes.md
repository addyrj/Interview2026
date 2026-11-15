# 290. Interview Problem: Build Drawer Navigation
# हिंदी में: Drawer Navigation बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐ Medium | Asked at: Flipkart, Zomato, Swiggy, Paytm

Files: `App.jsx`, `CustomDrawerContent.jsx`.
Target: Expo SDK 52, React Navigation v6/v7 + Reanimated 3 (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
A drawer is a side menu that slides in from the left edge (or via a hamburger button). The user picks a screen (Home, Orders, Settings) from it.

## 🔵 सरल परिभाषा (Hindi)
Drawer एक side menu है जो बाएँ किनारे से (या hamburger button से) slide होकर आता है। User उसमें से screen (Home, Orders, Settings) चुनता है।

---

## 🔴 Problem it Solves
Bottom tabs fit about 5 destinations. Apps with more sections (profile, orders, addresses, help, logout) need a place to list them without crowding the main UI.

## 🔴 यह क्यों बना? (Hindi)
Bottom tabs में लगभग 5 जगहें ही आती हैं। ज़्यादा sections (profile, orders, addresses, help, logout) वाले apps को उन्हें दिखाने के लिए अलग जगह चाहिए, मुख्य UI भरे बिना।

---

## 🔴 Problem Statement
Create a drawer with 3 screens, a profile header (name + phone), the standard item list, and a custom "Logout" action that closes the drawer. Drawer should slide over the content (width 280).

## 💡 Approach
```
createDrawerNavigator + drawerContent={(props) => <CustomDrawerContent {...props} />}
CustomDrawerContent:
   DrawerContentScrollView  (scroll + safe-area handled)
     header (profile)
     DrawerItemList  (auto items from screens)
     DrawerItem      (extra action: Logout)
screenOptions: drawerType 'front' | 'slide', drawerStyle width
```

## 🟢 How it Works — Step by Step
```
Step 1 → import 'react-native-gesture-handler' as the FIRST line of the entry file
Step 2 → NavigationContainer + Drawer.Navigator with the 3 screens
Step 3 → The header gets a hamburger button automatically; swiping from the left edge also opens
Step 4 → drawerContent renders our custom menu (header + list + logout)
Step 5 → Selecting an item navigates and closes the drawer
Step 6 → Logout: closeDrawer(), then clear the token / reset navigation
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → entry file की पहली line में import 'react-native-gesture-handler'
Step 2 → NavigationContainer + 3 screens वाला Drawer.Navigator
Step 3 → Header में hamburger button अपने आप आता है; बाएँ किनारे से swipe करने पर भी खुलता है
Step 4 → drawerContent हमारा custom menu (header + list + logout) दिखाता है
Step 5 → Item चुनने पर navigate होता है और drawer बंद होता है
Step 6 → Logout: closeDrawer(), फिर token हटाओ / navigation reset करो
```

---

## 🟡 Real World Example
Flipkart's side menu (Categories, My Orders, Account), Zomato's profile menu, Gmail's drawer, Google Maps' left menu.

## 🟡 Real Example Hindi mein
Flipkart का side menu (Categories, My Orders, Account), Zomato का profile menu, Gmail का drawer, Google Maps का left menu।

---

## 💻 Code Example — Basic
```jsx
import 'react-native-gesture-handler';                           // MUST be first import
import React from 'react';                                       // React
import { Text, View } from 'react-native';                       // UI
import { NavigationContainer } from '@react-navigation/native';  // root
import { createDrawerNavigator } from '@react-navigation/drawer'; // drawer

const Drawer = createDrawerNavigator();                          // navigator
const Screen = ({ name }) => <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}><Text>{name}</Text></View>;

export default function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator>
        <Drawer.Screen name="Home" children={() => <Screen name="Home" />} />
        <Drawer.Screen name="Orders" children={() => <Screen name="Orders" />} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced
From `App.jsx` and `CustomDrawerContent.jsx`:
```jsx
<Drawer.Navigator
  drawerContent={(props) => <CustomDrawerContent {...props} />}  // our menu
  screenOptions={{
    drawerType: 'front',                                         // slide over content ('slide' pushes it)
    drawerStyle: { width: 280 },                                 // width
    headerTintColor: '#E23744',                                  // hamburger colour
  }}
>

export default function CustomDrawerContent(props) {
  return (
    <DrawerContentScrollView {...props}>
      <View style={styles.header}>
        <Text style={styles.name}>Aditya Ranjan</Text>
        <Text style={styles.sub}>+91 98xxxxxx10</Text>
      </View>
      <DrawerItemList {...props} />                              {/* default items */}
      <DrawerItem label="Logout"
        onPress={() => { props.navigation.closeDrawer(); /* clear token here */ }} />
    </DrawerContentScrollView>
  );
}
```
Real app: put logout in an auth context so the root navigator switches to the Login stack; use `drawerIcon`, `drawerLabel`, and `drawerActiveTintColor` options.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Edge swipe | Gesture-nav back swipe may compete with drawer swipe | Interactive-pop back swipe may compete |
| Default type | `front` | `slide` (React Navigation picks by platform) |
| Hardware back | Closes the open drawer first | n/a |
| Status bar | May overlap header on edge-to-edge | Safe area handled |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npm i @react-navigation/native @react-navigation/drawer
// npx expo install react-native-gesture-handler react-native-reanimated react-native-screens react-native-safe-area-context
// babel-preset-expo already includes the Reanimated plugin
```
CLI way:
```jsx
// npm i the same packages ; babel.config.js plugins: ['react-native-reanimated/plugin'] (LAST)
// cd ios && pod install ; rebuild ; clear Metro cache: npx react-native start --reset-cache
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `react-native-gesture-handler` not imported first -> crash "no gesture handler" in production.
✅ Correct: First line of the entry file.

❌ Mistake 2: Missing Reanimated babel plugin on CLI -> "Reanimated plugin not configured" error.
✅ Correct: Add plugin last and restart Metro with cache reset.

❌ Mistake 3: Putting logout logic only in the drawer, leaving old screens in history.
✅ Correct: Reset navigation / switch to the auth stack.

❌ Mistake 4: Drawer for 3 items.
✅ Correct: Use tabs for primary navigation, drawer for secondary.

---

## 🧠 Tricky Interview Question
The app crashes only in a release build with a message about gesture handler / reanimated, but runs in dev. Why?

Answer: Dev mode can mask a missing setup. A release build exposes a missing `import 'react-native-gesture-handler'` at the top of the entry file or a missing Reanimated babel plugin (needs the cache reset). Also check that you did a native rebuild after installing the libraries.

---

## ⚫ Interview Questions + Answers
Q1: `drawerType` options?
A1: `front`, `back`, `slide`, `permanent` (for large screens/tablets).

Q2: How to open the drawer from code?
A2: `navigation.openDrawer()` / `toggleDrawer()` / `closeDrawer()`.

Q3: Why `DrawerContentScrollView`?
A3: Scrolls long menus and applies safe-area padding.

Q4: Drawer + tabs together?
A4: Tab navigator as a screen inside the drawer (or the reverse), depending on the main flow.

Q5: How to disable the swipe gesture?
A5: `swipeEnabled: false` in `screenOptions`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many secondary destinations, profile-style menus

❌ Avoid when:
- Few primary destinations (tabs are more discoverable)

---

## 📊 Visual Diagram
```
 ┌─────────────┬───────────────────┐
 │ Aditya R.   │   Header  ☰       │
 │ +91 98xxx   │                   │
 │ ─────────── │                   │
 │ ▸ Home      │   Screen content │
 │   Orders    │   (dimmed when    │
 │   Settings  │    drawer open)   │
 │   Logout    │                   │
 └─────────────┴───────────────────┘
   drawer (280px, type: front)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Drawer | Side menu | साइड मेनू |
| drawerContent | Custom drawer renderer | Custom menu |
| Gesture handler | Native touch library | Gesture library |
| Reanimated | UI-thread animation lib | Animation library |
| Hamburger | ☰ menu icon | ☰ आइकन |

---

## ⚡ 3-Line Summary
English: `createDrawerNavigator` gives a side menu; `drawerContent` customises it.
Import gesture-handler first and configure the Reanimated plugin.
Use `closeDrawer()` for custom actions like Logout.

Hindi: `createDrawerNavigator` side menu देता है; `drawerContent` से उसे बदलते हैं।
gesture-handler सबसे पहले import करें और Reanimated plugin लगाएँ।
Logout जैसे custom action के लिए `closeDrawer()` इस्तेमाल करें।

---

## ✅ What was verified
Both files passed an esbuild JSX syntax check only. Navigation, gestures and the drawer animation were not run (needs React Navigation + native modules and a device).

---

## ➡️ Next Topic
291. Build Offline-First App — storage, network detection and a sync queue.
