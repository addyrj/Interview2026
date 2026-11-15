# 177. Native UI Components
# हिंदी में: Native UI Components (अपना Native View React Native में)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Native code **not run** here. Fabric components use Codegen (`codegenNativeComponent`); legacy used `requireNativeComponent`.

---

## 🔵 Simple Definition (English)
A **Native UI Component** wraps a platform view (Android `View`, iOS `UIView`) so you can use it in JSX like `<MyMap />`. Props go from JS to native; events come back via callbacks. Use it for things RN has no built-in view for: maps, charts, video players, camera previews.

## 🔵 सरल परिभाषा (Hindi)
**Native UI Component** एक platform view (Android `View`, iOS `UIView`) को wrap करता है ताकि आप उसे JSX में `<MyMap />` की तरह use कर सकें। Props JS से native जाते हैं; events callbacks से वापस आते हैं। जिनके लिए RN में built-in view नहीं है — maps, charts, video player, camera preview — उनके लिए use होता है।

---

## 🔴 Problem it Solves
```
❌ RN has View/Text/Image only; no Google Map, PDF viewer, ExoPlayer
❌ Drawing complex UI in JS is slow
❌ You want to reuse existing native UI (company SDK)
✅ Wrap native view once -> use everywhere as a React component
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ RN में View/Text/Image हैं; Google Map, PDF viewer, ExoPlayer नहीं
❌ जटिल UI JS में बनाना धीमा
❌ कंपनी का मौजूदा native UI reuse करना है
✅ Native view एक बार wrap करो -> React component की तरह हर जगह use करो
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Write the native view (Android View / iOS UIView)
Step 2 → Write a ViewManager (Android) / RCTViewManager (iOS) that creates it
Step 3 → Export props with annotations (@ReactProp / RCT_EXPORT_VIEW_PROPERTY)
Step 4 → Define JS spec: codegenNativeComponent<NativeProps>('MyView')
Step 5 → Props are typed in TS; Codegen generates native props/events
Step 6 → JS renders <MyView color="#f00" onTap={...} /> like any component
Step 7 → Events: native dispatches event -> JS callback runs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Native view लिखो (Android View / iOS UIView)
Step 2 → ViewManager (Android) / RCTViewManager (iOS) लिखो जो उसे बनाए
Step 3 → Props export करो (@ReactProp / RCT_EXPORT_VIEW_PROPERTY)
Step 4 → JS spec: codegenNativeComponent<NativeProps>('MyView')
Step 5 → Props TS में typed; Codegen native props/events बनाता है
Step 6 → JS में <MyView color="#f00" onTap={...} /> आम component जैसा
Step 7 → Events: native event भेजता है -> JS callback चलता है
```

---

## 🟡 Real World Example
**Zomato/Swiggy** live tracking uses **Google Maps / Mapbox** native views. **Ola/Uber** style apps render the map natively for 60fps panning. **Hotstar/JioCinema** use native video players (ExoPlayer on Android, AVPlayer on iOS) wrapped as RN components.

## 🟡 Real Example Hindi mein
**Zomato/Swiggy** live tracking में **Google Maps / Mapbox** native views use होते हैं। **Ola/Uber** जैसे apps map को native render करते हैं ताकि 60fps पर pan हो। **Hotstar/JioCinema** native video players (Android पर ExoPlayer, iOS पर AVPlayer) को RN component की तरह wrap करते हैं।

---

## 💻 Code Example — Basic
```ts
// ColorBoxNativeComponent.ts — JS spec for a Fabric native component
import type { ViewProps, HostComponent } from 'react-native';              // base view props
import type { Int32, DirectEventHandler } from 'react-native/Libraries/Types/CodegenTypes'; // codegen types
import codegenNativeComponent from 'react-native/Libraries/Utilities/codegenNativeComponent'; // factory

// Event payload sent from native -> JS
type TapEvent = Readonly<{ x: Int32; y: Int32 }>;

// All props the native view accepts
export interface NativeProps extends ViewProps {
  color?: string;                                // background color string
  onBoxTap?: DirectEventHandler<TapEvent>;       // event callback
}

// 'ColorBoxView' must match the native component name
export default codegenNativeComponent<NativeProps>('ColorBoxView') as HostComponent<NativeProps>;
```
```jsx
// Usage in a screen (Android + iOS once native side is implemented)
import React from 'react';
import { View, Text } from 'react-native';
import ColorBoxView from './ColorBoxNativeComponent'; // the spec file

export default function Screen() {
  return (
    <View style={{ flex: 1, paddingTop: 80 }}>
      <Text>Native view below</Text>
      {/* style works like any View; color is our custom prop */}
      <ColorBoxView
        style={{ width: 200, height: 200 }}                       // size via style
        color="#f97316"                                          // orange
        onBoxTap={(e) => console.log('tapped', e.nativeEvent.x)} // native event
      />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```kotlin
// Android: ViewManager for the component (Kotlin) — creates and updates the native view
package com.colorbox

import android.graphics.Color
import android.view.View
import com.facebook.react.uimanager.SimpleViewManager      // base for simple views
import com.facebook.react.uimanager.ThemedReactContext      // context for creating views
import com.facebook.react.uimanager.annotations.ReactProp   // marks a JS prop
import com.facebook.react.module.annotations.ReactModule

@ReactModule(name = ColorBoxViewManager.NAME)               // name must match JS 'ColorBoxView'
class ColorBoxViewManager : SimpleViewManager<View>() {
  override fun getName() = NAME                             // component name

  // Create the real Android view
  override fun createViewInstance(ctx: ThemedReactContext): View = View(ctx)

  // JS prop 'color' -> this setter
  @ReactProp(name = "color")
  fun setColor(view: View, color: String?) {
    try {
      view.setBackgroundColor(Color.parseColor(color ?: "#cccccc")) // parse "#rrggbb"
    } catch (e: IllegalArgumentException) {
      view.setBackgroundColor(Color.GRAY)                    // invalid color -> fallback
    }
  }

  companion object { const val NAME = "ColorBoxView" }
}
```
```objc
// iOS: ColorBoxViewManager.m (Objective-C, legacy-style view manager; also works via Fabric interop)
#import <React/RCTViewManager.h>
#import <UIKit/UIKit.h>

@interface ColorBoxViewManager : RCTViewManager
@end

@implementation ColorBoxViewManager
RCT_EXPORT_MODULE(ColorBoxView)                  // JS name
- (UIView *)view { return [[UIView alloc] init]; } // create the native view
RCT_EXPORT_VIEW_PROPERTY(backgroundColor, UIColor) // map a standard prop (color handled by RN)
@end
// For a custom 'color' string prop you would add a custom setter with RCT_CUSTOM_VIEW_PROPERTY.
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| View class | `android.view.View` | `UIView` |
| Manager | `SimpleViewManager<T>` / `ViewGroupManager<T>` | `RCTViewManager` |
| Prop annotation | `@ReactProp` | `RCT_EXPORT_VIEW_PROPERTY` / `RCT_CUSTOM_VIEW_PROPERTY` |
| Events | `RCTEventEmitter` / `EventDispatcher` | `RCTDirectEventBlock` |
| Package registration | `ReactPackage.createViewManagers` | Automatic |
| UI thread | Main thread | Main thread |

---

## 🟠 Expo vs CLI Difference
Expo way:
```tsx
// Expo Modules API (JS side) — view declared in Swift/Kotlin with the View definition
import { requireNativeViewManager } from 'expo-modules-core';
const NativeView = requireNativeViewManager('ColorBoxExpo'); // name from native `Name("ColorBoxExpo")`
export default NativeView;  // use like <NativeView color="#f97316" />
// Needs development build, not Expo Go.
```
CLI way:
```bash
# Library skeleton with Fabric view
npx create-react-native-library@latest color-box   # pick "Fabric view"
# Codegen runs during build
cd ios && bundle exec pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting size
✅ Correct: Native views often have 0 size by default; give `style={{width, height}}` or flex.

❌ Mistake 2: Updating views from a background thread
✅ Correct: All view work happens on the main/UI thread.

❌ Mistake 3: Name mismatch between JS and native
✅ Correct: `codegenNativeComponent('ColorBoxView')` must equal the native registered name exactly.

---

## 🧠 Tricky Interview Question
**Q: Your native component renders on iOS but shows blank on Android with no error. First thing to check?**

**Answer:** Check that the ViewManager is registered in a `ReactPackage` (`createViewManagers`) and the package is added to the app (autolinking for libraries); also confirm the view has non-zero size. Name mismatch usually throws a red box, so blank often means a size/registration problem.

---

## ⚫ Interview Questions + Answers

**Q1: Native Module vs Native UI Component?**
A1: Module exposes functions/data; UI component exposes a visible view you place in JSX.

**Q2: How do events go native -> JS?**
A2: Native dispatches a direct event; JS gets it via a prop like `onBoxTap` and reads `event.nativeEvent`.

**Q3: What is `codegenNativeComponent`?**
A3: A helper used in a typed spec file; Codegen generates native props/state classes for Fabric.

**Q4: Why wrap a native map instead of using WebView?**
A4: Native maps give 60fps gestures, offline tiles and platform integration.

**Q5: Is `requireNativeComponent` still used?**
A5: It is the legacy approach; works through interop but new code should use Codegen spec.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a platform view RN lacks (maps, players, charts)
- Existing native SDK UI must be embedded

❌ Avoid when:
- Pure JS libs (react-native-svg, Skia) can draw it
- Only Expo Go available

---

## 📊 Visual Diagram
```
<ColorBoxView color="#f97316" onBoxTap=... />
     │ props (typed by Codegen)
     ▼
ViewManager ──creates──► Android View / iOS UIView
     ▲
     └── events (nativeEvent) ◄── user taps
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ViewManager | Creates/updates native view | Native view बनाने वाला manager |
| ReactProp | Prop binding annotation | Prop जोड़ने वाला annotation |
| HostComponent | Type of native component | Native component का type |
| nativeEvent | Event payload | Event का data |
| Codegen | Generates glue | Glue code बनाना |
| Autolinking | Auto register libs | Libraries अपने आप जोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. Native UI components let you use platform views as JSX tags.
2. Props flow JS -> native, events flow native -> JS.
3. Use a Codegen spec + ViewManager; needs a native rebuild.

**Hindi:**
1. Native UI components से platform views JSX tag की तरह use होते हैं।
2. Props JS -> native, events native -> JS जाते हैं।
3. Codegen spec + ViewManager use करो; native rebuild ज़रूरी है।

---

## ➡️ Next Topic
**178. Codegen** — spec से अपने आप native code कैसे बनता है।
