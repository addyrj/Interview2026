# 67. Drawer Navigator
# हिंदी में: Drawer Navigator — Side Menu
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)**, React Navigation 7 (`@react-navigation/drawer`), reanimated 3 — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
A **Drawer Navigator** shows a side menu that slides in from the left edge (swipe or hamburger button). It lists destinations like Home, Orders, Settings. It is built with `@react-navigation/drawer` and needs `react-native-gesture-handler` and `react-native-reanimated`.

## 🔵 सरल परिभाषा (Hindi)
**Drawer Navigator** एक side menu दिखाता है जो बाएँ किनारे से slide होकर आता है (swipe या hamburger button से)। इसमें Home, Orders, Settings जैसे options होते हैं। यह `@react-navigation/drawer` से बनता है और इसे `react-native-gesture-handler` और `react-native-reanimated` चाहिए।

---

## 🔴 Problem it Solves
```
PROBLEM:
  App me 8-10 top-level sections (Profile, Orders, Wallet, Help, Settings)
  Bottom tabs me sirf 3-5 fit hote hain

DRAWER:
  ✅ Bahut saare options chhupa kar rakhta hai
  ✅ Profile header + menu list ek jagah
  ✅ Swipe gesture se open
  ✅ Tablet/landscape me permanent sidebar (drawerType: 'permanent')
```

## 🔴 यह क्यों बना? (Hindi)
```
Bottom tabs में 5 से ज़्यादा items नहीं आते।
Drawer में कई sections छुपा कर रख सकते हैं।
Swipe से खुलता है, और tablet पर हमेशा दिखने वाला sidebar भी बन सकता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install @react-navigation/drawer react-native-gesture-handler react-native-reanimated
Step 2 → babel.config.js: add 'react-native-reanimated/plugin' as LAST plugin
          (Expo SDK 50+: babel-preset-expo adds it automatically — check docs)
Step 3 → Import 'react-native-gesture-handler' at top of entry file (older guides)
Step 4 → createDrawerNavigator() → Drawer.Navigator + Drawer.Screen
Step 5 → Each Drawer.Screen = menu item (title from name / options.drawerLabel)
Step 6 → Open: swipe from left edge, or navigation.openDrawer() / toggleDrawer()
Step 7 → Custom UI: drawerContent={(props) => <CustomDrawer {...props} />}
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → drawer + gesture-handler + reanimated install
Step 2 → Reanimated का Babel plugin (Expo में अक्सर automatic)
Step 3 → createDrawerNavigator() से Drawer.Navigator और Drawer.Screen
Step 4 → हर Drawer.Screen एक menu item
Step 5 → swipe / openDrawer() / toggleDrawer() से खोलो
Step 6 → drawerContent से custom menu बनाओ
```

---

## 🟡 Real World Example
**Zomato / Ola:** hamburger menu on top-left opens a drawer with user photo, "Your Orders", "Favourites", "Payments", "Help", "Logout". Ola's drawer shows the profile header and ride history. In the drawer, Logout is a custom button (not a screen).

## 🟡 Real Example Hindi mein
**Zomato / Ola:** ऊपर-बाएँ hamburger menu से drawer खुलता है — user photo, "Your Orders", "Favourites", "Payments", "Help", "Logout"। Logout एक custom button है (screen नहीं)।

---

## 💻 Code Example — Basic
```jsx
// Basic drawer with 3 screens
// npx expo install @react-navigation/drawer react-native-gesture-handler react-native-reanimated
import React from 'react'; // React
import { View, Text } from 'react-native'; // UI
import { NavigationContainer } from '@react-navigation/native'; // container
import { createDrawerNavigator } from '@react-navigation/drawer'; // drawer factory

const Drawer = createDrawerNavigator(); // create navigator

const Page = ({ title }) => ( // simple page
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text style={{ fontSize: 20 }}>{title}</Text>
  </View>
);

const Home = () => <Page title="Home" />; // stable component references
const Orders = () => <Page title="Your Orders" />;
const Settings = () => <Page title="Settings" />;

export default function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator initialRouteName="Home">{/* first screen */}
        <Drawer.Screen name="Home" component={Home} />{/* menu item 1 */}
        <Drawer.Screen name="Orders" component={Orders} options={{ title: 'My Orders' }} />{/* header title override */}
        <Drawer.Screen name="Settings" component={Settings} />{/* menu item 3 */}
      </Drawer.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: custom drawer content with profile header + logout, drawer options
import React from 'react'; // React
import { View, Text, Image, Alert, StyleSheet } from 'react-native'; // UI
import { NavigationContainer } from '@react-navigation/native'; // container
import {
  createDrawerNavigator, // factory
  DrawerContentScrollView, // scroll container for menu
  DrawerItemList, // renders default items
  DrawerItem, // single custom item
} from '@react-navigation/drawer';

const Drawer = createDrawerNavigator(); // navigator

function CustomDrawer(props) { // receives navigation state via props
  return (
    <DrawerContentScrollView {...props}>{/* keeps safe-area padding */}
      <View style={styles.header}>{/* profile header */}
        <Image source={{ uri: 'https://i.pravatar.cc/100' }} style={styles.avatar} />{/* avatar */}
        <Text style={styles.name}>Aditya Ranjan</Text>{/* user name */}
      </View>
      <DrawerItemList {...props} />{/* default list of Drawer.Screens */}
      <DrawerItem
        label="Logout" // custom item (not a screen)
        onPress={() => Alert.alert('Logout', 'Are you sure?', [{ text: 'Cancel' }, { text: 'Yes', onPress: () => props.navigation.closeDrawer() }])} // confirm
      />
    </DrawerContentScrollView>
  );
}

const Page = ({ title }) => <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}><Text>{title}</Text></View>; // dummy
const Home = () => <Page title="Home" />;
const Orders = () => <Page title="Orders" />;

export default function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator
        drawerContent={(props) => <CustomDrawer {...props} />} // custom UI
        screenOptions={{
          drawerType: 'front', // 'front' | 'back' | 'slide' | 'permanent'
          drawerStyle: { width: 280 }, // drawer width
          drawerActiveTintColor: '#e23744', // active item color
          swipeEdgeWidth: 40, // swipe zone from left edge
          headerTintColor: '#e23744', // hamburger icon color
        }}
      >
        <Drawer.Screen name="Home" component={Home} />
        <Drawer.Screen name="Orders" component={Orders} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  header: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ccc' }, // header box
  avatar: { width: 64, height: 64, borderRadius: 32 }, // round avatar
  name: { marginTop: 8, fontSize: 18, fontWeight: '700' }, // name
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Convention | Drawer is native Material pattern | Less common; iOS prefers tabs |
| Default `drawerType` | `front` | `slide` (default depends on platform) |
| Edge swipe conflict | Conflicts with system back gesture (Android 10+ gesture nav) | Conflicts with swipe-back inside stacks |
| Status bar | Can draw behind (set `statusBarTranslucent` in options if needed) | Safe area handled |
| Gesture handler | Required | Required |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: npx expo install ... (picks compatible gesture-handler & reanimated versions)
// Babel plugin is included by babel-preset-expo in recent SDKs
```
CLI way:
```jsx
// Bare CLI: npm i @react-navigation/drawer react-native-gesture-handler react-native-reanimated
// babel.config.js: plugins: ['react-native-reanimated/plugin']  (must be LAST)
// cd ios && pod install ; rebuild the app (native modules changed)
// Wrap root with GestureHandlerRootView if needed (style flex:1)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting the Reanimated Babel plugin in bare projects.
✅ Correct: Add `react-native-reanimated/plugin` last in `plugins`, clear cache (`npx expo start -c`).

❌ Mistake 2: Drawer inside a Stack that has its own header → two headers.
✅ Correct: `headerShown: false` on the stack screen holding the drawer.

❌ Mistake 3: Too many sections in drawer plus bottom tabs for the same items.
✅ Correct: Pick one primary pattern; use drawer for secondary items.

❌ Mistake 4: Not testing Android edge swipe vs system back gesture.
✅ Correct: Adjust `swipeEdgeWidth` or add a hamburger button.

---

## 🧠 Tricky Interview Question
**Q:** Drawer works in Expo Go but crashes in a bare CLI build with "Reanimated plugin not configured". Why?

**Answer:** Expo's Babel preset adds Reanimated's plugin automatically (in recent SDKs); bare CLI needs you to add `react-native-reanimated/plugin` manually (last in the plugin list), then reset Metro cache and rebuild native app. Expo Go also ships prebuilt native modules, which a bare build does not unless installed and pod-installed.

---

## ⚫ Interview Questions + Answers
Q1: Which libs does drawer need?
A1: `react-native-gesture-handler` and `react-native-reanimated` (plus screens + safe-area-context).

Q2: How to open the drawer programmatically?
A2: `navigation.openDrawer()`, `closeDrawer()`, `toggleDrawer()` or `DrawerActions`.

Q3: How to customize drawer UI?
A3: `drawerContent` prop with `DrawerContentScrollView`, `DrawerItemList`, `DrawerItem`.

Q4: How to keep drawer on tablets always visible?
A4: `drawerType: 'permanent'` (conditionally, based on width via `useWindowDimensions`).

Q5: How to hide a screen from the drawer menu?
A5: Use `drawerItemStyle: { display: 'none' }` in options, or custom `drawerContent` filtering routes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many secondary sections, profile-centric apps, tablets

❌ Avoid when:
- 3-5 main destinations (use bottom tabs)
- iOS-first app where drawers feel foreign

---

## 📊 Visual Diagram
```
┌──────────┬─────────────────────┐
│ [Avatar] │  ☰  Home            │
│ Home     │                     │
│ Orders   │   (screen content)  │
│ Settings │                     │
│ Logout   │   ← swipe from left │
└──────────┴─────────────────────┘
  drawer          main screen
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Drawer | Side sliding menu | Side menu |
| drawerContent | Custom drawer UI | Custom drawer UI |
| drawerType | front/back/slide/permanent | Drawer का प्रकार |
| Gesture handler | Native touch lib | Gesture library |
| swipeEdgeWidth | Swipe start zone | Swipe का क्षेत्र |

---

## ⚡ 3-Line Summary
English: Drawer shows a side menu with many sections via `@react-navigation/drawer`.
Needs gesture-handler and reanimated; customize with `drawerContent`.
Best for many secondary options; avoid conflicts with Android back gesture.

Hindi: Drawer `@react-navigation/drawer` से कई sections वाला side menu देता है।
gesture-handler और reanimated चाहिए; `drawerContent` से customize करो।
कई secondary options के लिए अच्छा; Android back gesture से conflict देखो।

---

## ➡️ Next Topic
**68. Top Tab Navigator** — swipeable tabs jaise "Orders: Ongoing | Past".
