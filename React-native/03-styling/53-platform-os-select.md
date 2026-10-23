# 53. Platform.OS + Platform.select
# हिंदी में: Platform.OS और Platform.select क्या हैं?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
`Platform.OS` is a string — `'android'` or `'ios'` (or `'web'`) — that tells you which platform the code is running on. `Platform.select()` is a utility that picks the right value from a map based on the current platform. Use these for: different shadow styles, font weights, status bar heights, navigation behavior, or any Android/iOS divergence.

## 🔵 सरल परिभाषा (Hindi)
`Platform.OS` एक string है — `'android'` या `'ios'` — जो बताती है कि code किस platform पर run हो रहा है। `Platform.select()` एक utility है जो current platform के आधार पर map से सही value pick करती है। Use करते हैं: shadow styles, font weights, status bar heights, navigation behavior, या किसी भी Android/iOS divergence के लिए।

---

## 🔴 Problem it Solves
```
PLATFORM DIFFERENCES — WHY THEY EXIST:
Android (Google) and iOS (Apple) have different:

SHADOWS:
  Android uses 'elevation' (Material Design)
  iOS uses box-shadow style properties
  (shadowColor, shadowOffset, shadowOpacity, shadowRadius)

FONTS:
  Android default: Roboto
  iOS default: SF Pro
  Font weight '700' renders differently!

STATUS BAR:
  Android: has a colored status bar that can overlap content
  iOS: has notch/Dynamic Island + safe area
  Heights differ per model!

NAVIGATION:
  Android: hardware/software back button
  iOS: swipe from left edge to go back

KEYBOARD:
  Android: back button dismisses keyboard
  iOS: must tap outside or have a "Done" button

Platform.OS + Platform.select fix all these differences.
```

## 🔴 यह क्यों बना? (Hindi)
```
Android और iOS के UI rules अलग हैं:
- Shadow: Android = elevation, iOS = shadow* properties
- Status bar: Android overlap, iOS safe area
- Fonts: Roboto vs SF Pro
- Back navigation: hardware button vs swipe
Platform.OS इन सब differences handle करता है।
```

---

## 🟢 How it Works — Step by Step

```
PLATFORM.OS:
──────────────────────────────────────────────────────
  import { Platform } from 'react-native';

  Platform.OS         → 'android' | 'ios' | 'web' | 'windows' | 'macos'
  Platform.Version    → Android API level (33) | iOS version number ('16.4')
  Platform.isPad      → true if iPad (iOS only)
  Platform.isTV       → true if Apple TV or Android TV
  Platform.isTesting  → true in test environment

PLATFORM.SELECT:
──────────────────────────────────────────────────────
  Platform.select({
    ios: valueForIOS,
    android: valueForAndroid,
    default: fallbackValue,     // for web or unknown
  });
  → Returns the value for the current platform
  → 'default' is used if current platform not in the map

USE IN STYLESHEETS:
──────────────────────────────────────────────────────
  StyleSheet.create({
    shadow: Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
      },
      android: {
        elevation: 4,
      },
    }),
  })
```

## 🟢 कैसे काम करता है? (Hindi)
```
Platform.OS → current platform string
Platform.select({ ios: ..., android: ... }) → platform का value return
StyleSheet में: shadows, fonts, spacing — platform-specific values
```

---

## 🟡 Real World Example
**Paytm app:** The UPI payment card looks identical to the designer's spec on both Android and iOS, but uses `elevation: 8` on Android and `shadowColor/Offset/Opacity/Radius` on iOS for shadows. The status bar height (for the translucent status bar effect) uses `Platform.OS === 'android' ? StatusBar.currentHeight : 44` as the header top padding. These look the same to users but require different code for each platform.

## 🟡 Real Example Hindi मे
**Paytm:** UPI card दोनों platforms पर same दिखती है, लेकिन Android पर `elevation: 8` और iOS पर `shadow*` properties — same visual result, different code। Status bar height भी platform-specific।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';
import { View, Text, StyleSheet, Platform, StatusBar } from 'react-native';

// Platform.OS — conditional logic
function PlatformInfo() {
  const isAndroid = Platform.OS === 'android';
  const isIOS = Platform.OS === 'ios';

  return (
    <View style={styles.container}>
      <Text>Running on: {Platform.OS}</Text>
      <Text>
        Version: {Platform.Version}
        {/* Android: API level (e.g., 33 = Android 13) */}
        {/* iOS: version string (e.g., "16.4") */}
      </Text>
      {isAndroid && <Text>Status Bar Height: {StatusBar.currentHeight}px</Text>}
      {isIOS && Platform.isPad && <Text>Running on iPad!</Text>}
    </View>
  );
}

// Platform.select — pick the right value
const styles = StyleSheet.create({
  container: {
    flex: 1,
    // Platform-specific padding for status bar
    paddingTop: Platform.select({
      android: StatusBar.currentHeight,  // Android status bar height
      ios: 44,                           // iOS safe area approximation
      default: 0,
    }),
    padding: 16,
  },

  // THE MOST COMMON USE: shadows
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    // Platform.select for shadows:
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.15,
        shadowRadius: 8,
      },
      android: {
        elevation: 4,  // Android Material elevation
      },
    }),
  },

  // Font weight — render differently per platform
  heading: {
    fontSize: 18,
    fontWeight: Platform.select({ ios: '600', android: '700' }),
    // iOS: 600 = SemiBold looks similar to Android 700 = Bold
    // Due to different font families
  },
});
```

## 💻 Code Example — Advanced

```jsx
import React from 'react';
import {
  View, Text, TouchableNativeFeedback, TouchableOpacity,
  StyleSheet, Platform, StatusBar
} from 'react-native';

// PATTERN: Platform-specific button
// Android: Material ripple effect
// iOS: opacity fade
function PlatformButton({ onPress, children, style }) {
  if (Platform.OS === 'android') {
    return (
      <TouchableNativeFeedback
        onPress={onPress}
        background={TouchableNativeFeedback.Ripple('#fff3', false)}  // ripple effect
      >
        <View style={[styles.button, style]}>
          <Text style={styles.buttonText}>{children}</Text>
        </View>
      </TouchableNativeFeedback>
    );
  }

  // iOS
  return (
    <TouchableOpacity onPress={onPress} style={[styles.button, style]} activeOpacity={0.8}>
      <Text style={styles.buttonText}>{children}</Text>
    </TouchableOpacity>
  );
}

// PATTERN: Platform-specific header with proper status bar handling
function AppHeader({ title }) {
  const statusBarHeight = Platform.select({
    android: StatusBar.currentHeight || 24,  // Android actual status bar height
    ios: 44,   // iOS standard: 44pt for notched devices
    default: 0,
  });

  const headerHeight = 56 + statusBarHeight;

  return (
    <View style={[styles.header, { height: headerHeight, paddingTop: statusBarHeight }]}>
      <StatusBar
        barStyle={Platform.select({
          ios: 'dark-content',     // iOS: dark icons on light header
          android: 'light-content', // Android: light icons on dark header
        })}
        backgroundColor={Platform.OS === 'android' ? '#f97316' : 'transparent'}
        translucent={Platform.OS === 'android'}  // translucent on Android
      />
      <Text style={styles.headerTitle}>{title}</Text>
    </View>
  );
}

// PATTERN: Platform-specific keyboard avoidance
import { KeyboardAvoidingView } from 'react-native';
function Form() {
  return (
    <KeyboardAvoidingView
      // iOS: 'padding' works best
      // Android: 'height' works best
      behavior={Platform.select({ ios: 'padding', android: 'height' })}
      style={{ flex: 1 }}
    >
      {/* form fields */}
    </KeyboardAvoidingView>
  );
}

// PATTERN: Check Android version for features
function AndroidFeature() {
  if (Platform.OS === 'android' && Platform.Version >= 31) {
    // Android 12+ (API 31+): can use splash screen API, dynamic color, etc.
    return <Text>Android 12+ feature available!</Text>;
  }
  return null;
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#f97316',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: { color: '#fff', fontWeight: '700' },
  header: {
    backgroundColor: '#f97316',
    paddingHorizontal: 16,
    justifyContent: 'flex-end',
    paddingBottom: 12,
  },
  headerTitle: { color: '#fff', fontSize: 20, fontWeight: '700' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Shadow API | `elevation` | `shadow*` properties |
| Status bar height | `StatusBar.currentHeight` | Usually 44pt (notch) or 20pt |
| Font weight '700' | Bold Roboto | Bold SF Pro |
| Back gesture | Hardware back button | Swipe from left |
| Ripple effect | `TouchableNativeFeedback` | `TouchableOpacity` |
| Platform.Version | API level (number: 33) | Version string ('16.4') |

---

## 🟠 Expo vs CLI Difference

Expo way:
```jsx
import { Platform } from 'react-native';
// Platform works the same in Expo
// Expo adds: expo-constants for device info
import Constants from 'expo-constants';
// Constants.statusBarHeight → accurate on all Expo devices
```

CLI way:
```jsx
import { Platform, StatusBar } from 'react-native';
// Platform.OS and Platform.select work the same
// StatusBar.currentHeight for Android (may be null — use fallback)
const statusBarHeight = StatusBar.currentHeight ?? 24;
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using iOS shadow properties on Android (they're silently ignored)
```jsx
// WRONG: This only works on iOS!
const styles = StyleSheet.create({
  card: {
    shadowColor: '#000',       // ← Android IGNORES this
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  }
});

// CORRECT: Platform-specific shadows
const styles = StyleSheet.create({
  card: {
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 4,
      },
      android: {
        elevation: 4,
      },
    }),
  }
});
```

❌ **Mistake 2:** Hardcoding status bar height
```jsx
// WRONG: Hardcoded — breaks on different Android phones
const HEADER_TOP = 24;  // ❌ varies by device!

// CORRECT: Dynamic
const HEADER_TOP = Platform.select({
  android: StatusBar.currentHeight || 24,  // actual height
  ios: 44,                                  // safe area inset
});
```

❌ **Mistake 3:** Platform.Version type mismatch
```jsx
// TRAP: Platform.Version is a NUMBER on Android but STRING on iOS!
if (Platform.Version > 30) {}  // ❌ On iOS: '16.4' > 30 = true?! (string comparison)

// CORRECT: Check platform first
if (Platform.OS === 'android' && Platform.Version >= 31) {
  // Android 12+
}
if (Platform.OS === 'ios') {
  const majorVersion = parseInt(Platform.Version as string, 10);
  if (majorVersion >= 16) { /* iOS 16+ */ }
}
```

---

## 🧠 Tricky Interview Question

**Q: Why does `elevation` on Android not clip properly with `borderRadius`? How do you fix it?**

**Answer:** Android's `elevation` creates a shadow based on the View's shape, but the shadow can "bleed" through child views that have the same or higher elevation. Also, `elevation` doesn't respect `overflow: 'hidden'` — an elevated view can still show its shadow outside a parent with hidden overflow. Fix for shadow clipping: (1) Keep the elevated view and the `borderRadius`/overflow view separate — use a wrapper. (2) Set `elevation` on the outer view and `overflow: 'hidden'` on the inner view at the same z-level. (3) For Android 5+ (Lollipop, API 21+), use `android_ripple={{ color: '#fff3', borderless: false }}` in `Pressable` with the same `borderRadius` as the view for the ripple to respect rounded corners.

---

## ⚫ Interview Questions + Answers

**Q1: What is `Platform.OS` and what values can it return?**
A1: `Platform.OS` is a string from the `Platform` module that identifies the current platform: `'android'` for Android devices, `'ios'` for iPhone/iPad, `'web'` when running in a browser (Expo Web), `'windows'` for Windows apps (React Native for Windows), `'macos'` for macOS apps (React Native for macOS). In most React Native projects, you only deal with `'android'` and `'ios'`.

**Q2: How do you add shadows that work on both Android and iOS?**
A2: Android uses `elevation` (a single number, Material Design's z-elevation). iOS uses four properties: `shadowColor`, `shadowOffset: {width, height}`, `shadowOpacity`, `shadowRadius`. Solution: `...Platform.select({ ios: { shadowColor: '#000', shadowOffset: {width: 0, height: 2}, shadowOpacity: 0.15, shadowRadius: 4 }, android: { elevation: 4 } })`. Many projects create a `shadow` utility or use a `Card` component that handles this internally.

**Q3: What is the difference between `Platform.OS === 'ios'` and `Platform.isPad`?**
A3: `Platform.OS === 'ios'` is true for ALL iOS devices — iPhone AND iPad. `Platform.isPad` is true ONLY for iPads. Use `Platform.OS === 'ios'` when behavior should differ from Android in general. Use `Platform.isPad` when behavior should differ for iPads specifically (e.g., showing a sidebar on iPad, using split screen layout). `Platform.isTV` is similar for Apple TV / Android TV. Note: `Platform.isPad` is iOS-specific — it's always `false` on Android.

**Q4: When would you use platform-specific files vs Platform.select?**
A4: Two approaches: (1) **`Platform.select()`** in code — fine for simple value differences (shadow, font size, padding). (2) **Platform-specific files** (`Button.ios.tsx`, `Button.android.tsx`) — better for large code differences where each platform needs significantly different implementation. Metro automatically picks the right file. Rule: if the platforms share 80%+ of the code, use `Platform.select` inline. If each platform has a unique implementation, use separate files.

**Q5: How do you check the Android API level / iOS version number?**
A5: `Platform.Version` — but be careful: on Android it returns a number (API level, e.g., 33 for Android 13); on iOS it returns a string (version, e.g., "16.4"). Usage: `Platform.OS === 'android' && Platform.Version >= 31` (API 31+ = Android 12). For iOS: `Platform.OS === 'ios' && parseInt(Platform.Version, 10) >= 16`. Common use case: enabling a feature only on newer OS versions that support a specific API (e.g., Material You dynamic colors on Android 12+).

---

## 🔷 When to Use + When Not to Use
✅ **Use Platform.OS / Platform.select when:**
- Different shadow implementations
- KeyboardAvoidingView behavior
- Status bar height calculation
- Checking API level for feature availability
- Button ripple vs opacity effect

❌ **Avoid over-using — prefer cross-platform approaches:**
- `SafeAreaView` handles iOS safe areas better than manual Platform checks
- `Pressable` with `android_ripple` is more idiomatic than Platform-switching button components
- `react-native-safe-area-context` for accurate safe areas without Platform.OS hacks

---

## 📊 Visual Diagram

```
PLATFORM.SELECT FLOW:
──────────────────────────────────────────────────────
  Platform.select({
    ios: 'SF Pro font weight 600',
    android: 'Roboto font weight 700',
    default: 'system default',
  })
              │
              ▼
  Platform.OS === 'ios'?  → return 'SF Pro font weight 600'
  Platform.OS === 'android'? → return 'Roboto font weight 700'
  else → return 'system default'

SHADOW COMPARISON:
──────────────────────────────────────────────────────
  Android (elevation):           iOS (shadow*):
  ┌──────────────────┐           ┌──────────────────┐
  │   Card           │           │   Card           │
  └──────────────────┘           └──────────────────┘
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           ░░░░░░░░░░░░░░░░░░
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           ░░░░░░░░░░░░░░░░░░
  Material elevation             Soft blur shadow
  (all sides, equal)             (directional, soft)
  elevation: 4                   shadowOffset: {x:0,y:2}
                                 shadowOpacity: 0.15
                                 shadowRadius: 4

PLATFORM.VERSION TYPE TRAP:
──────────────────────────────────────────────────────
  Android: Platform.Version = 33      (NUMBER)
  iOS:     Platform.Version = '16.4'  (STRING)
  ⚠️ Always check Platform.OS first, then use Version!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Platform.OS | Current platform string | Current platform string |
| Platform.select | Pick value based on platform | Platform के अनुसार value चुनो |
| Platform.Version | OS version (number/string) | OS version |
| Platform.isPad | Is this an iPad? | iPad है? |
| elevation | Android Material shadow | Android का shadow |
| shadow* | iOS shadow properties | iOS के shadow properties |
| StatusBar.currentHeight | Android status bar height | Android status bar height |

---

## ⚡ 3-Line Summary
**English:**
1. `Platform.OS` returns `'android'` or `'ios'`; `Platform.select({ ios: ..., android: ... })` picks the right value for current platform.
2. Most common uses: shadows (`elevation` vs `shadow*`), `KeyboardAvoidingView` behavior (`padding` vs `height`), status bar height, button feedback (ripple vs opacity).
3. `Platform.Version` is a number on Android (API level) but a string on iOS (version) — always check `Platform.OS` first before using Version.

**Hindi:**
1. `Platform.OS` `'android'` या `'ios'` return करता है; `Platform.select()` current platform के लिए सही value pick करता है।
2. Common uses: shadows, `KeyboardAvoidingView` behavior, status bar height, button feedback।
3. `Platform.Version` Android पर number (API level), iOS पर string — Version use से पहले `Platform.OS` check करो।

---

## ➡️ Next Topic
**54. Platform-Specific Files** — `.android.tsx` और `.ios.tsx` files, Metro resolution।
