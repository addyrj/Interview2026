# 68. Top Tab Navigator
# हिंदी में: ऊपर वाला Tab Navigator (Material Top Tabs)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76)** with **React Navigation v7** — check current docs — APIs change between SDKs. (v6 में भी लगभग same API है; v7 में कुछ props rename हुए हैं।)

---

## 🔵 Simple Definition (English)
A **Top Tab Navigator** shows tabs at the **top** of the screen and lets users **swipe left/right** between them. In React Navigation it is `createMaterialTopTabNavigator` from `@react-navigation/material-top-tabs`.

## 🔵 सरल परिभाषा (Hindi)
**Top Tab Navigator** screen के **ऊपर** tabs दिखाता है और user **left/right swipe** करके tabs बदल सकता है। React Navigation में यह `@react-navigation/material-top-tabs` का `createMaterialTopTabNavigator` है।

---

## 🔴 Problem it Solves
```
❌ Ek screen par related sections (Orders / Offers / History) dikhane hain
❌ Bottom tabs main navigation ke liye hain, sub-sections ke liye nahi
❌ Manual swipe + tab indicator khud banana mushkil
✅ Top tabs: swipeable pages + animated indicator, ready-made
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ एक screen पर related sections (Orders / Offers / History) दिखाने हैं
❌ Bottom tabs main navigation के लिए होते हैं, sub-sections के लिए नहीं
❌ Swipe + animated indicator खुद बनाना मुश्किल
✅ Top tabs: swipeable pages + indicator पहले से तैयार
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install @react-navigation/material-top-tabs
         react-native-tab-view react-native-pager-view
Step 2 → const Tab = createMaterialTopTabNavigator();
Step 3 → <Tab.Navigator> with <Tab.Screen name component /> children
Step 4 → Navigator renders tab bar (top) + pager (swipe container)
Step 5 → Swipe or tap -> index changes -> screen shown, indicator animates
Step 6 → Place it inside NavigationContainer (or inside a stack screen)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → तीनों packages install करो (material-top-tabs, tab-view, pager-view)
Step 2 → createMaterialTopTabNavigator() से Tab बनाओ
Step 3 → <Tab.Navigator> में <Tab.Screen> रखो
Step 4 → Navigator ऊपर tab bar + swipe वाला pager बनाता है
Step 5 → Swipe या tap -> index बदलता है -> screen दिखती है, indicator animate होता है
Step 6 → इसे NavigationContainer (या किसी stack screen) के अंदर रखो
```

---

## 🟡 Real World Example
**Swiggy "Orders" page**: tabs like *Ongoing / Past*; **Zomato restaurant page**: *Order Online / Reviews / Photos / Menu*; **WhatsApp**: top tabs *Chats / Status / Calls* on Android (the classic look). Each tab is a separate list that you can swipe between.

## 🟡 Real Example Hindi mein
**Swiggy की "Orders" screen**: *Ongoing / Past* tabs; **Zomato restaurant page**: *Order Online / Reviews / Photos / Menu*; **WhatsApp** (Android): ऊपर *Chats / Status / Calls* tabs। हर tab एक अलग list है, जिसे swipe करके बदल सकते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic top tabs: Chats / Status / Calls
// npx expo install @react-navigation/native @react-navigation/material-top-tabs
//                  react-native-tab-view react-native-pager-view
import React from 'react';                                    // React
import { View, Text } from 'react-native';                    // core UI
import { NavigationContainer } from '@react-navigation/native'; // root container
import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs'; // top tabs

const Tab = createMaterialTopTabNavigator();                  // create the navigator

function Screen({ title }) {                                  // small reusable screen
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontSize: 22 }}>{title}</Text>{/* show tab name */}
    </View>
  );
}

const Chats = () => <Screen title="Chats" />;                 // tab 1 screen
const Status = () => <Screen title="Status" />;               // tab 2 screen
const Calls = () => <Screen title="Calls" />;                 // tab 3 screen

export default function App() {
  return (
    <NavigationContainer>{/* required root */}
      <Tab.Navigator>{/* top tab navigator */}
        <Tab.Screen name="Chats" component={Chats} />{/* tab 1 */}
        <Tab.Screen name="Status" component={Status} />{/* tab 2 */}
        <Tab.Screen name="Calls" component={Calls} />{/* tab 3 */}
      </Tab.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: styled scrollable tabs, lazy loading, badge, safe-area top inset
// Zomato-style restaurant page: Menu / Reviews / Photos / About
import React from 'react';                                    // React
import { View, Text, StyleSheet, Platform } from 'react-native'; // RN core
import { SafeAreaView } from 'react-native-safe-area-context'; // safe area (Expo includes it)
import { NavigationContainer } from '@react-navigation/native'; // container
import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs'; // tabs

const Tab = createMaterialTopTabNavigator();                  // navigator

const Simple = ({ label }) => (                               // placeholder content
  <View style={styles.center}><Text>{label}</Text></View>
);

export default function RestaurantTabs() {
  return (
    <NavigationContainer>
      {/* Top tabs have NO automatic status-bar padding, so wrap in SafeAreaView (top edge) */}
      <SafeAreaView style={{ flex: 1 }} edges={['top']}>
        <Tab.Navigator
          initialRouteName="Menu"                             // first visible tab
          screenOptions={{
            lazy: true,                                       // render a tab only when first opened
            swipeEnabled: true,                               // allow swipe (set false on maps/carousels)
            tabBarScrollEnabled: true,                        // scroll tabs if many (like Zomato)
            tabBarActiveTintColor: '#e23744',                 // active label colour (Zomato red)
            tabBarInactiveTintColor: '#888',                  // inactive label colour
            tabBarIndicatorStyle: { backgroundColor: '#e23744', height: 3 }, // underline
            tabBarLabelStyle: { fontWeight: '700', textTransform: 'none' },  // keep normal case
            tabBarItemStyle: { width: 110 },                  // fixed width per tab when scrollable
            tabBarStyle: {                                    // bar container style
              backgroundColor: '#fff',
              elevation: Platform.OS === 'android' ? 2 : 0,  // Android shadow
            },
          }}
        >
          <Tab.Screen name="Menu" children={() => <Simple label="Menu list" />} />
          <Tab.Screen
            name="Reviews"
            children={() => <Simple label="Reviews list" />}
            options={{ tabBarBadge: () => <Text style={styles.badge}>12</Text> }} // badge (check docs for your version)
          />
          <Tab.Screen name="Photos" children={() => <Simple label="Photos grid" />} />
          <Tab.Screen name="About" children={() => <Simple label="About" />} />
        </Tab.Navigator>
      </SafeAreaView>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // centre content
  badge: { color: '#e23744', fontWeight: '700', marginRight: 6 },      // badge text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Convention | Top tabs are very common (Material) | Bottom tabs are convention; top tabs fine for sub-sections |
| Swipe | Works via ViewPager | Works via UIScrollView-based pager (`react-native-pager-view`) |
| Ripple on tab press | Yes (`tabBarPressColor`) | No ripple (opacity) |
| Status bar overlap | Top tabs sit under status bar unless handled | Notch overlap — SafeArea needed |
| Back gesture | Hardware back leaves tab navigator | Swipe-back may conflict with first tab swipe |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo picks versions compatible with your SDK
npx expo install @react-navigation/native @react-navigation/material-top-tabs \
  react-native-tab-view react-native-pager-view react-native-safe-area-context react-native-screens
```
CLI way:
```bash
# CLI: install with npm/yarn, then iOS pods and rebuild (pager-view is a native module)
npm install @react-navigation/material-top-tabs react-native-tab-view react-native-pager-view
cd ios && pod install && cd ..                                # link native iOS code
npx react-native run-android                                  # rebuild, JS reload is not enough
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `react-native-pager-view` (error: "tried to register two views..." or missing module)
✅ Correct: install `react-native-tab-view` + `react-native-pager-view` along with the navigator, then rebuild (CLI).

❌ Mistake 2: Using top tabs for the app's main navigation on iOS-style apps
✅ Correct: bottom tabs for main sections; top tabs for sub-sections inside one screen.

❌ Mistake 3: Inline component functions causing remounts
```jsx
<Tab.Screen name="A" component={() => <A />} />   // ❌ new function each render -> state lost
```
✅ Correct: pass a stable `component={A}` or use `children` carefully.

❌ Mistake 4: Horizontal FlatList/map inside a tab fights the swipe
✅ Correct: `swipeEnabled: false` on that screen, or use `nestedScrollEnabled` / gesture handling.

---

## 🧠 Tricky Interview Question
**Q: Why does the content of a tab disappear/reset when I switch tabs, and why do all tabs load at once?**

**Answer:** By default, material-top-tabs render the **focused tab plus neighbours** for smooth swiping (options like `lazy` and `lazyPreloadDistance` control this). With `lazy: true`, a tab mounts the first time it is visited, and it **stays mounted** afterwards (state is preserved). If your content "resets", you probably passed an inline `component={() => ...}` — a new function each render creates a new component type, so React unmounts/remounts. Move the component outside or use `children` with stable references.

---

## ⚫ Interview Questions + Answers

**Q1: Which package gives top tabs in React Navigation?**
A1: `@react-navigation/material-top-tabs` (depends on `react-native-tab-view` and `react-native-pager-view`).

**Q2: How do you disable swiping?**
A2: `screenOptions={{ swipeEnabled: false }}` on the navigator (or per-screen in `options`).

**Q3: How do you make many tabs scrollable?**
A3: `tabBarScrollEnabled: true` and give each item a width via `tabBarItemStyle`.

**Q4: How to place a top tab navigator inside a stack screen?**
A4: Use it as the `component` of a `Stack.Screen`; the stack header sits above the tabs. That is nesting (see topic 69).

**Q5: Difference between `createBottomTabNavigator` and top tabs?**
A5: Bottom tabs = main app sections, no swipe by default, icons. Top tabs = swipeable sub-sections with an indicator, text labels.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Related sub-sections of one feature (Orders: Ongoing/Past)
- You want swipe between pages
- Many labelled categories (scrollable tabs)

❌ Avoid when:
- It is the main navigation of the app (use bottom tabs/drawer)
- Page has heavy horizontal gestures (maps, carousels)
- Only 1-2 simple states (use a segmented control)

---

## 📊 Visual Diagram
```
┌────────────────────────────────────┐
│ Menu | Reviews | Photos | About    │  <- tab bar (top)
│ ━━━━                               │  <- animated indicator
├────────────────────────────────────┤
│                                    │
│   <-- swipe -->   Screen content   │  <- pager-view
│                                    │
└────────────────────────────────────┘
NavigationContainer
 └─ Tab.Navigator
     ├─ Menu    (screen)
     ├─ Reviews (screen)
     └─ ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Top tabs | Swipeable tabs at the top | ऊपर वाले swipeable tabs |
| Pager view | Native swipeable page container | Swipe वाला page container |
| Indicator | Underline under active tab | Active tab के नीचे लाइन |
| `lazy` | Mount tab only when visited | Visit होने पर ही mount |
| `swipeEnabled` | Allow/deny swiping | Swipe चालू/बंद |
| Scrollable tabs | Tab bar scrolls horizontally | Tab bar का horizontal scroll |

---

## ⚡ 3-Line Summary
**English:**
1. Top tabs = swipeable tabs at the top via `createMaterialTopTabNavigator`.
2. Needs `react-native-tab-view` + `react-native-pager-view`; rebuild native app in CLI.
3. Use for sub-sections; avoid inline components and gesture conflicts.

**Hindi:**
1. Top tabs = ऊपर swipeable tabs, `createMaterialTopTabNavigator` से।
2. `react-native-tab-view` + `react-native-pager-view` चाहिए; CLI में native rebuild करो।
3. Sub-sections के लिए use करो; inline components और gesture conflict से बचो।

---

## ➡️ Next Topic
**69. Nested Navigators** — Stack के अंदर Tabs, Tabs के अंदर Stack कैसे रखें।
