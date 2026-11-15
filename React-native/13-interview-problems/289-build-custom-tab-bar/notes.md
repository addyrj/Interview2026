# 289. Interview Problem: Build a Custom Tab Bar
# हिंदी में: Custom Tab Bar बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐ Medium | Asked at: Paytm, PhonePe, Zomato, Swiggy

Files: `CustomTabBar.jsx`, `App.jsx`.
Target: Expo SDK 52, React Navigation v6/v7 bottom-tabs (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
`createBottomTabNavigator` lets you replace its default tab bar with your own component through the `tabBar` prop. React Navigation gives you `state`, `descriptors` and `navigation`; you draw the buttons and call `navigation.navigate`.

## 🔵 सरल परिभाषा (Hindi)
`createBottomTabNavigator` में `tabBar` prop से default tab bar की जगह अपना component लगा सकते हैं। React Navigation आपको `state`, `descriptors` और `navigation` देता है; आप buttons बनाते हैं और `navigation.navigate` call करते हैं।

---

## 🔴 Problem it Solves
The default tab bar can not match a brand design (centre floating button, custom indicator, badges). A custom bar gives full control while keeping navigation logic (state, deep links, back behaviour) from the library.

## 🔴 यह क्यों बना? (Hindi)
Default tab bar brand design से match नहीं करता (बीच का floating button, custom indicator, badge)। Custom bar में पूरा control मिलता है और navigation logic (state, deep link, back) library ही संभालती है।

---

## 🔴 Problem Statement
Build a tab bar with 3 tabs. Highlight the focused tab, support `tabPress` event interception, long press, accessibility, and add safe-area padding at the bottom (home indicator / gesture bar).

## 💡 Approach
```
<Tab.Navigator tabBar={(props) => <CustomTabBar {...props} />}>

CustomTabBar({ state, descriptors, navigation }):
  state.routes[]   -> list of tabs
  state.index      -> focused tab index
  descriptors[key].options -> label / title
  press:  emit 'tabPress' (canPreventDefault) -> if !focused && !defaultPrevented -> navigate
```

## 🟢 How it Works — Step by Step
```
Step 1 → Navigator calls tabBar(props) on every state change
Step 2 → Map state.routes to Pressable buttons
Step 3 → focused = state.index === index -> active colour + top border
Step 4 → onPress: emit tabPress so screens can intercept (scroll to top, etc.)
Step 5 → If not prevented and not already focused -> navigation.navigate(route.name)
Step 6 → paddingBottom = max(insets.bottom, 8) avoids the home indicator
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर state बदलाव पर Navigator tabBar(props) call करता है
Step 2 → state.routes को Pressable buttons में map करो
Step 3 → focused = state.index === index -> active रंग + ऊपर की border
Step 4 → onPress: tabPress event emit करो ताकि screen उसे रोक सके
Step 5 → रोका न गया हो और tab पहले से focused न हो -> navigation.navigate(route.name)
Step 6 → paddingBottom = max(insets.bottom, 8) से home indicator से बचाव
```

---

## 🟡 Real World Example
Paytm / PhonePe bottom bars with a centre "Scan" button, Zomato's Delivery / Dining / Reorder tabs, Instagram's bottom bar with a profile-photo tab.

## 🟡 Real Example Hindi mein
Paytm / PhonePe की bottom bar जिसमें बीच में "Scan" button होता है, Zomato के Delivery / Dining / Reorder tabs, Instagram की bottom bar जिसमें profile photo tab होता है।

---

## 💻 Code Example — Basic
```jsx
import React from 'react';                                       // React
import { Text, View } from 'react-native';                       // UI
import { NavigationContainer } from '@react-navigation/native';  // root
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'; // tabs
import { SafeAreaProvider } from 'react-native-safe-area-context'; // insets provider
import CustomTabBar from './CustomTabBar';                       // our bar

const Tab = createBottomTabNavigator();                          // navigator
const Screen = ({ name }) => <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}><Text>{name}</Text></View>;

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator tabBar={(props) => <CustomTabBar {...props} />}>
          <Tab.Screen name="Home" children={() => <Screen name="Home" />} />
          <Tab.Screen name="Search" children={() => <Screen name="Search" />} />
          <Tab.Screen name="Orders" children={() => <Screen name="Orders" />} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
```

## 💻 Code Example — Advanced
From `CustomTabBar.jsx`:
```jsx
export default function CustomTabBar({ state, descriptors, navigation }) {
  const insets = useSafeAreaInsets();                            // notch / home-indicator space
  return (
    <View style={[styles.bar, { paddingBottom: Math.max(insets.bottom, 8) }]}>
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key];              // screen options
        const label = options.tabBarLabel ?? options.title ?? route.name;
        const focused = state.index === index;                   // active tab?

        const onPress = () => {
          const event = navigation.emit({ type: 'tabPress', target: route.key, canPreventDefault: true });
          if (!focused && !event.defaultPrevented) navigation.navigate(route.name, route.params);
        };
        const onLongPress = () => navigation.emit({ type: 'tabLongPress', target: route.key });

        return (
          <Pressable key={route.key} accessibilityRole="button"
                     accessibilityState={focused ? { selected: true } : {}}
                     onPress={onPress} onLongPress={onLongPress}
                     style={[styles.tab, focused && styles.tabFocused]}>
            <Text style={{ color: focused ? '#E23744' : '#777' }}>{label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}
```
Tip: use `options.tabBarIcon`, `tabBarBadge` from descriptors to stay compatible with screen options; animate the indicator with `Animated`/Reanimated using `state.index`.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Shadow | `elevation: 8` | `shadow*` props or hairline border (as used here) |
| Bottom inset | Gesture-navigation bar inset | Home-indicator inset (~34px) |
| Keyboard | Bar may rise with keyboard; set `tabBarHideOnKeyboard` (default tab bar) or hide it yourself | Not pushed up by default |
| Ripple feedback | `android_ripple` on Pressable | Use opacity style on pressed |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npm i @react-navigation/native @react-navigation/bottom-tabs
// npx expo install react-native-screens react-native-safe-area-context
// (Expo Router alternative: <Tabs tabBar={(props) => <CustomTabBar {...props} />} /> in app/(tabs)/_layout.js)
```
CLI way:
```jsx
// npm i @react-navigation/native @react-navigation/bottom-tabs react-native-screens react-native-safe-area-context
// cd ios && pod install ; rebuild native app
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not wrapping the app in `SafeAreaProvider` -> `useSafeAreaInsets` fails or returns zeros.
✅ Correct: Wrap the root (React Navigation already adds one, but be explicit).

❌ Mistake 2: Calling `navigation.navigate` without emitting `tabPress`.
✅ Correct: Emit it so "tap active tab to scroll to top" and `preventDefault` work.

❌ Mistake 3: `key={index}`.
✅ Correct: `key={route.key}`.

❌ Mistake 4: Defining inline `component={() => <Screen/>}` (re-mounts screens on each render).
✅ Correct: Pass a stable component, or use `children` only for demos (as in this sample).

---

## 🧠 Tricky Interview Question
The user taps the already active tab. Why does the code skip `navigate`?

Answer: Navigating to the focused route does nothing useful and could reset nested stacks unexpectedly. Libraries emit `tabPress` and screens decide what to do (scroll to top, pop to top). `!focused && !event.defaultPrevented` keeps that contract.

---

## ⚫ Interview Questions + Answers
Q1: What props does `tabBar` receive?
A1: `state`, `descriptors`, `navigation`, `insets`.

Q2: How do you add a centre floating button?
A2: Render the middle item differently (bigger, absolute, negative margin) but keep it a normal route or call a modal action.

Q3: How do you show a badge?
A3: `options.tabBarBadge` from `descriptors[route.key].options` and render it.

Q4: Why `useSafeAreaInsets`?
A4: Bottom bar must clear the home indicator / gesture area.

Q5: Custom bar vs `screenOptions` styling?
A5: Use `screenOptions` for colours / icons; custom `tabBar` for layout/animation changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Brand-specific bottom bar, floating action tab, animated indicator

❌ Avoid when:
- `tabBarStyle`, `tabBarIcon`, `tabBarBadge` are enough

---

## 📊 Visual Diagram
```
 Navigator ──► tabBar({ state, descriptors, navigation })
                        │
        ┌───────────────┼───────────────┐
      Home (focused)  Search          Orders
   ▔▔▔▔▔▔▔ red top border   grey          grey
   press ─► emit tabPress ─► (not prevented & not focused) ─► navigate(name)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tabBar prop | Custom tab bar renderer | Custom bar देने वाला prop |
| descriptors | Per-route options | Route के options |
| tabPress | Event on tab tap | Tab दबने का event |
| Safe area inset | Space for notch / home bar | सुरक्षित क्षेत्र |
| Focused | Currently active tab | सक्रिय tab |

---

## ⚡ 3-Line Summary
English: Pass `tabBar` to the Tab navigator and map `state.routes` to buttons.
Emit `tabPress`, then navigate if not focused or prevented.
Add safe-area bottom padding.

Hindi: Tab navigator को `tabBar` दें और `state.routes` को buttons में map करें।
`tabPress` emit करें, फिर focused/prevented न हो तो navigate करें।
नीचे safe-area padding जोड़ें।

---

## ✅ What was verified
`CustomTabBar` was rendered under react-native-web + jsdom with fake `state/descriptors/navigation` and a mocked `useSafeAreaInsets`: labels show, tapping an unfocused tab calls `navigate('Search')`, tapping the focused tab does nothing. `App.jsx` only passed an esbuild syntax check; the real React Navigation integration was not run.

---

## ➡️ Next Topic
290. Build Drawer Navigation — a side menu using the same "custom navigator UI" idea.
