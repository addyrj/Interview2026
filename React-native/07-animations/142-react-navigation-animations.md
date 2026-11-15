# 142. React Navigation Animations
# हिंदी में: React Navigation Animations — Screen transitions को customize करना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76, `@react-navigation/native` v7, `@react-navigation/native-stack` v7 (v6 में भी `animation` option है)। `@react-navigation/stack` (JS-based) में `cardStyleInterpolator` और `TransitionPresets` मिलते हैं।

---

## 🔵 Simple Definition (English)
**React Navigation animations** control how one screen enters and leaves when you navigate: slide, fade, modal slide-up, or fully custom. You set them with options like `animation`, `presentation`, and `gestureEnabled` on a navigator or on one screen.

## 🔵 सरल परिभाषा (Hindi)
**React Navigation animations** तय करते हैं कि navigate करते समय screen कैसे आए और जाए: slide, fade, नीचे से modal, या पूरी तरह custom। इन्हें `animation`, `presentation`, `gestureEnabled` जैसे options से navigator या किसी एक screen पर set करते हैं।

---

## 🔴 Problem it Solves
```
DEFAULT TRANSITIONS हर जगह सही नहीं:
  Login → Home   : slide नहीं, fade अच्छा लगता है
  Filter sheet   : नीचे से modal चाहिए
  Onboarding     : horizontal slide चाहिए
  Splash → Main  : कोई animation नहीं (none)

बिना customization:
  ❌ सारी screens एक जैसी transition
  ❌ Platform के हिसाब से अलग feel नहीं
```

## 🔴 यह क्यों बना? (Hindi)
```
अलग-अलग flow को अलग transition चाहिए (modal, fade, slide)।
Navigator options से हम बिना native code लिखे ये बदल सकते हैं।
iOS और Android के default अलग होते हैं; हम control ले सकते हैं।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Navigator पर screenOptions में default animation set करो
Step 2 → किसी खास screen पर options={{ animation: 'fade' }} से override
Step 3 → Modal के लिए presentation: 'modal' / 'transparentModal'
Step 4 → Gesture control: gestureEnabled, fullScreenGestureEnabled (iOS)
Step 5 → Custom चाहिए तो @react-navigation/stack में cardStyleInterpolator
Step 6 → Duration: native-stack में animationDuration (iOS), stack में transitionSpec
```

Native-stack `animation` values (docs देखो, version के हिसाब से): `default`, `fade`, `fade_from_bottom`, `flip`, `simple_push`, `slide_from_bottom`, `slide_from_right`, `slide_from_left`, `none`।

## 🟢 कैसे काम करता है? (Hindi)
```
1. screenOptions से सब screens का default animation।
2. options से एक screen का override।
3. presentation से modal जैसा behaviour।
4. gestureEnabled से swipe-back on/off।
5. बहुत custom चाहिए तो JS-based stack में interpolator।
```

---

## 🟡 Real World Example
**Zomato:** Home से Restaurant detail में slide-from-right; "Filters" पर bottom-sheet जैसा modal। **Paytm:** Splash से Home में कोई animation नहीं (`none`) ताकि तेज़ लगे; Payment success screen fade होती है और back gesture बंद रहता है। **Swiggy:** Cart से Checkout में normal push, पर "Add address" modal की तरह नीचे से आती है।

## 🟡 Real Example Hindi mein
**Paytm:** Payment success screen पर `gestureEnabled: false` ताकि user गलती से back न जाए, और screen fade होकर आती है। **Zomato:** Filter screen `presentation: 'modal'` से नीचे से खुलती है, बाकी screens slide-from-right।

---

## 💻 Code Example — Basic

```jsx
// App.jsx — native-stack animations per screen
import React from 'react';                                       // React
import { View, Text, Button } from 'react-native';               // UI primitives
import { NavigationContainer } from '@react-navigation/native';  // root
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack

const Stack = createNativeStackNavigator();                      // navigator

const Screen = ({ navigation, route }) => (                      // generic demo screen
  <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
    <Text>{route.name}</Text>
    <Button title="Next: Filters (modal)" onPress={() => navigation.navigate('Filters')} />
    <Button title="Next: Success (fade)" onPress={() => navigation.navigate('Success')} />
  </View>
);

export default function App() {                                  // root
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{ animation: 'slide_from_right' }}        // default for all screens
      >
        <Stack.Screen name="Home" component={Screen} />          {/* default slide */}
        <Stack.Screen
          name="Filters"
          component={Screen}
          options={{ presentation: 'modal', animation: 'slide_from_bottom' }} // modal from bottom
        />
        <Stack.Screen
          name="Success"
          component={Screen}
          options={{ animation: 'fade', gestureEnabled: false }} // fade + no swipe back
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// advanced.jsx — custom interpolator with JS stack + Platform handling
import React from 'react';                                       // React
import { Platform } from 'react-native';                         // platform check
import { NavigationContainer } from '@react-navigation/native';  // root
import {
  createStackNavigator,                                          // JS-based stack
  CardStyleInterpolators,                                        // ready-made interpolators
  TransitionPresets,                                             // ready-made presets
} from '@react-navigation/stack';                                // requires react-native-gesture-handler

const Stack = createStackNavigator();                            // navigator

// Custom: scale + fade in (written by hand)
const scaleFade = ({ current }) => ({                            // interpolator receives progress
  cardStyle: {
    opacity: current.progress,                                   // 0 → 1 fade in
    transform: [{
      scale: current.progress.interpolate({                      // 0.9 → 1 scale
        inputRange: [0, 1],
        outputRange: [0.9, 1],
      }),
    }],
  },
});

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          // Platform-specific preset: iOS slide, Android fade-from-bottom feel
          ...(Platform.OS === 'ios'
            ? TransitionPresets.SlideFromRightIOS                // iOS style
            : TransitionPresets.FadeFromBottomAndroid),          // Android style
        }}
      >
        <Stack.Screen name="Home" component={() => null} />      {/* placeholder */}
        <Stack.Screen
          name="Detail"
          component={() => null}
          options={{
            cardStyleInterpolator: scaleFade,                    // our custom animation
            transitionSpec: {                                    // timing control
              open: { animation: 'timing', config: { duration: 250 } },
              close: { animation: 'timing', config: { duration: 200 } },
            },
          }}
        />
        <Stack.Screen
          name="Sheet"
          component={() => null}
          options={{
            presentation: 'modal',                               // modal behaviour
            cardStyleInterpolator: CardStyleInterpolators.forVerticalIOS, // vertical slide
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
// Error note: custom interpolator में unknown fields मत लौटाओ; सिर्फ cardStyle/overlayStyle आदि.
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default push | Fade/slide-up (OS version पर depend) | Slide from right |
| Swipe back | System back / predictive back | Edge swipe, `fullScreenGestureEnabled` |
| `animationDuration` (native-stack) | Docs के अनुसार iOS-specific; Android पर ignore हो सकता है | Supported |
| Modal | Full-screen जैसा | Sheet-style card (`presentation: 'modal'`) |
| Custom interpolator | JS stack में same | JS stack में same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-navigation/native @react-navigation/native-stack
// npx expo install react-native-screens react-native-safe-area-context
// JS stack के लिए: npx expo install @react-navigation/stack react-native-gesture-handler
// Expo Router में: <Stack screenOptions={{ animation: 'fade' }} /> (app/_layout.tsx)
```
CLI way:
```jsx
// npm i @react-navigation/native @react-navigation/native-stack
// npm i react-native-screens react-native-safe-area-context
// cd ios && pod install
// Android: MainActivity में onCreate(null) जरूरी (react-native-screens docs देखो)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: native-stack में `cardStyleInterpolator` use करना।
✅ Correct: वह सिर्फ `@react-navigation/stack` में है; native-stack में `animation` string।

❌ Mistake 2: JS stack install करके `react-native-gesture-handler` import न करना।
✅ Correct: entry file के top पर `import 'react-native-gesture-handler'`।

❌ Mistake 3: हर screen पर heavy custom animation।
✅ Correct: Native-stack के built-in animation (native thread) use करो — smoother।

❌ Mistake 4: Success/payment screen पर back gesture खुला छोड़ना।
✅ Correct: `gestureEnabled: false` और `headerBackVisible: false`।

---

## 🧠 Tricky Interview Question
`animation: 'slide_from_bottom'` लगाया, पर iOS पर फिर भी side-slide दिख रहा है। क्यों?

Answer: Screen पर `presentation: 'modal'`/`'card'` और animation का combination देखो। iOS पर कुछ presentation (जैसे `modal`) की अपनी native animation होती है और `animation` option सिर्फ `card`-जैसी presentation पर पूरी तरह लागू होता है (docs में version-wise check करो)। साथ ही option किसी दूसरे navigator पर लगा हो सकता है — screen को सीधे उसी navigator की `options` में दो।

---

## ⚫ Interview Questions + Answers
Q1: native-stack और stack में animation का फर्क?
A1: native-stack native UINavigationController/Fragment use करता है (तेज़, limited custom); stack JS में चलता है (पूरी तरह customizable, थोड़ा धीमा)।

Q2: Modal कैसे दिखाएँ?
A2: `presentation: 'modal'` (या `'transparentModal'`) screen option में।

Q3: Back swipe कैसे बंद करें?
A3: `gestureEnabled: false`; Android hardware back के लिए `beforeRemove` listener या `usePreventRemove`।

Q4: Animation बिल्कुल बंद कैसे करें?
A4: `animation: 'none'` (native-stack)।

Q5: Reanimated से कौन सा transition बनता है?
A5: Screen-level transition के लिए अलग; Reanimated का use element-level animation में (shared element, layout animations)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Flow के हिसाब से transition अलग चाहिए (modal, fade)
- Platform-native feel चाहिए

❌ Avoid when:
- Default काफी है (over-engineering)
- Low-end device पर heavy JS interpolator

---

## 📊 Visual Diagram
```
 Home ──(slide_from_right)──► Detail
 Home ──(modal, bottom)─────► Filters
 Home ──(fade, no gesture)──► Success
 Splash ─(none)─────────────► Home

 native-stack : options.animation (native thread)
 stack (JS)   : cardStyleInterpolator (JS + Animated)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| presentation | card / modal style | Screen दिखाने का तरीका |
| animation | transition type | Transition का प्रकार |
| gestureEnabled | allow swipe back | Swipe-back की अनुमति |
| cardStyleInterpolator | custom JS transition | Custom transition function |
| transitionSpec | timing/spring config | Timing की settings |

---

## ⚡ 3-Line Summary
English: Navigators accept `animation`, `presentation` and gesture options to change transitions.
Use native-stack for speed and `@react-navigation/stack` for fully custom interpolators.
Disable gestures on critical screens like payment success.

Hindi: Navigator के options से transition बदलते हैं (`animation`, `presentation`, gesture)।
Speed के लिए native-stack, पूरी custom के लिए `@react-navigation/stack`।
Payment success जैसी screens पर gesture बंद रखो।

---

## ➡️ Next Topic
**143. Fetch API in React Native** — अब animations से आगे बढ़कर server से data कैसे लाएँ।
