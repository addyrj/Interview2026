# 172. Fabric Renderer
# हिंदी में: Fabric Renderer (नया UI Rendering System)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Fabric is on by default in new projects (RN 0.76+).

---

## 🔵 Simple Definition (English)
**Fabric** is React Native's new renderer. It turns your React element tree into a **shadow tree in C++**, computes layout with **Yoga**, then mounts real native views. Because the core is shared C++ and talks over JSI, reads like `measure` can be **synchronous** and updates can be prioritized.

## 🔵 सरल परिभाषा (Hindi)
**Fabric** React Native का नया renderer है। यह आपके React tree को **C++ में shadow tree** बनाता है, **Yoga** से layout निकालता है और फिर real native views mount करता है। Core shared C++ है और JSI से बात करता है, इसलिए `measure` जैसे reads **synchronous** हो सकते हैं और updates को priority दी जा सकती है।

---

## 🔴 Problem it Solves
```
OLD RENDERER (Paper):
❌ Layout computed, then sent async over bridge to UI thread
❌ JS could not read layout synchronously (measure was async callback)
❌ Fast scroll -> blank areas (UI not ready when JS is busy)
❌ Two shadow trees (Java/ObjC + JS) duplicated logic per platform
❌ No React 18 concurrent features
```

## 🔴 यह क्यों बना? (Hindi)
```
पुराना renderer (Paper):
❌ Layout async भेजा जाता था bridge से UI thread को
❌ JS layout sync नहीं पढ़ सकता था (measure async callback था)
❌ Fast scroll पर blank जगह दिखती थी
❌ हर platform पर shadow tree का अलग code (duplicate)
❌ React 18 concurrent features नहीं थे
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Render phase: React creates React element tree (JS)
Step 2 → Fabric clones nodes into an immutable C++ shadow tree
Step 3 → Yoga calculates flexbox layout in C++
Step 4 → Commit phase: new tree is committed (can be on any thread)
Step 5 → Diffing: Fabric compares old/new tree -> list of mutations
Step 6 → Mount phase: UI thread applies mutations (create/update/delete views)
Step 7 → View flattening removes layout-only views to cut native view count
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Render phase: React, JS में element tree बनाता है
Step 2 → Fabric nodes को immutable C++ shadow tree में clone करता है
Step 3 → Yoga, C++ में flexbox layout निकालता है
Step 4 → Commit phase: नया tree commit होता है (किसी भी thread पर)
Step 5 → Diffing: पुराने/नए tree की तुलना -> mutations की list
Step 6 → Mount phase: UI thread mutations apply करता है (views बनाना/बदलना/हटाना)
Step 7 → View flattening: सिर्फ layout वाले views हटाकर native views कम करता है
```

---

## 🟡 Real World Example
**Swiggy restaurant list**: a card has many wrapper `<View>`s only for layout (padding, row, column). Fabric's **view flattening** removes those layout-only native views, so the list uses fewer native views and scrolls smoother. **Zomato**'s bottom-sheet measuring uses synchronous layout in `useLayoutEffect` to position a tooltip without a visible flicker.

## 🟡 Real Example Hindi mein
**Swiggy restaurant list**: एक card में कई wrapper `<View>` सिर्फ layout (padding, row, column) के लिए होते हैं। Fabric की **view flattening** ऐसे views हटा देती है, इसलिए native views कम होते हैं और scroll smooth रहता है। **Zomato** की bottom-sheet में tooltip बिना flicker के रखने के लिए `useLayoutEffect` में synchronous layout पढ़ा जाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: synchronous measurement with useLayoutEffect (works best with Fabric)
// Android + iOS
import React, { useLayoutEffect, useRef, useState } from 'react'; // hooks
import { View, Text, StyleSheet } from 'react-native'; // UI parts

export default function Tooltip() {
  const boxRef = useRef(null);                 // reference to the native view
  const [width, setWidth] = useState(0);       // measured width

  // useLayoutEffect runs BEFORE the screen is painted
  useLayoutEffect(() => {
    // measureInWindow gives x, y, width, height (callback; on Fabric it is fast)
    boxRef.current?.measureInWindow((x, y, w) => {
      setWidth(w); // store the width -> re-render before first paint
    });
  }, []); // run once on mount

  return (
    <View style={styles.wrap}>
      {/* the view we measure */}
      <View ref={boxRef} style={styles.box}>
        <Text style={styles.t}>Order from Swiggy</Text>
      </View>
      {/* show the measured width */}
      <Text>Width measured: {Math.round(width)} px</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { marginTop: 80, alignItems: 'center' }, // center horizontally
  box: { backgroundColor: '#fde68a', padding: 16, borderRadius: 10 }, // yellow card
  t: { fontSize: 18, fontWeight: '600' }, // label
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: React concurrent features that Fabric enables — useTransition keeps typing smooth
// while an expensive filtered list renders at low priority (React 18+ / RN 0.69+; best on Fabric)
import React, { useMemo, useState, useTransition } from 'react';
import { View, Text, TextInput, FlatList, ActivityIndicator, Platform, StyleSheet } from 'react-native';

// 5,000 fake restaurant names (heavy to filter on every key press)
const ALL = Array.from({ length: 5000 }, (_, i) => ({ id: String(i), name: `Restaurant ${i}` }));

export default function Search() {
  const [query, setQuery] = useState('');        // urgent state: input text
  const [filter, setFilter] = useState('');      // non-urgent state: list filter
  const [isPending, startTransition] = useTransition(); // transition helper

  const onChange = (text) => {
    setQuery(text);                              // update input immediately (high priority)
    startTransition(() => {
      setFilter(text);                           // list update can be interrupted (low priority)
    });
  };

  // recompute filtered list only when `filter` changes
  const data = useMemo(
    () => ALL.filter((r) => r.name.toLowerCase().includes(filter.toLowerCase())),
    [filter]
  );

  return (
    <View style={styles.container}>
      <TextInput value={query} onChangeText={onChange} placeholder="Search..." style={styles.input} />
      {/* small spinner while the low-priority render is pending */}
      {isPending && <ActivityIndicator style={styles.spin} />}
      <FlatList
        data={data}
        keyExtractor={(r) => r.id}                 // stable id
        renderItem={({ item }) => <Text style={styles.row}>{item.name}</Text>}
        initialNumToRender={12}                    // keep first render small
        windowSize={5}                             // render window ~ 5 screens
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: Platform.select({ ios: 60, android: 40 }), paddingHorizontal: 16 }, // per-platform top gap
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, borderRadius: 8 }, // input
  spin: { marginVertical: 6 }, // spinner space
  row: { paddingVertical: 8 }, // row
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Mounting layer | Java/Kotlin `MountingManager` | Objective-C++ `RCTMountingManager` |
| View flattening | Yes (removes layout-only views) | Yes |
| Layout engine | Yoga (C++, shared) | Yoga (C++, shared) |
| Common view types | `android.view.ViewGroup`, `TextView` | `UIView`, `UILabel` |
| Debug inspector | Layout Inspector (Android Studio) | View Debugger (Xcode) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "newArchEnabled": true } }
```
```bash
npx expo prebuild --clean && npx expo run:android   # rebuild with Fabric
```
CLI way:
```bash
# android/gradle.properties  -> newArchEnabled=true
cd ios && RCT_NEW_ARCH_ENABLED=1 bundle exec pod install   # iOS Fabric
npx react-native run-android
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Relying on `collapsable={false}` everywhere
✅ Correct: Use it only when you need the native view to exist (e.g., `measure`, animations); otherwise let flattening work.

❌ Mistake 2: Assuming a layout-only `<View>` always exists natively
✅ Correct: Fabric may flatten it; native code looking up that view can fail.

❌ Mistake 3: Using `findNodeHandle` heavily
✅ Correct: Prefer refs and component methods; `findNodeHandle` is legacy and discouraged in new arch.

---

## 🧠 Tricky Interview Question
**Q: In Fabric a `<View>` with only `padding` and children disappears from the Android Layout Inspector. Is it a bug?**

**Answer:** No. It is **view flattening**: layout-only views (no background, border, touch handling, etc.) are not materialized natively; their effect is folded into children positions. To force a native view, add `collapsable={false}`.

---

## ⚫ Interview Questions + Answers

**Q1: What is a shadow tree?**
A1: An immutable C++ tree of nodes holding props and layout; Fabric diffs successive trees to know what native views to change.

**Q2: Who calculates layout in Fabric?**
A2: Yoga, the C++ flexbox engine, running in the shared core.

**Q3: What are the render, commit and mount phases?**
A3: Render = React builds the tree; Commit = Fabric lays out and promotes the tree; Mount = UI thread applies mutations to native views.

**Q4: Why is synchronous layout useful?**
A4: You can measure and position UI (tooltips, popovers) before paint, avoiding flicker.

**Q5: What is view flattening?**
A5: Optimization that removes layout-only views from the native hierarchy to reduce memory and speed up drawing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building new apps (default)
- You need smooth lists, concurrent React features, sync measure

❌ Avoid when:
- A required library only supports the old renderer and has no interop path

---

## 📊 Visual Diagram
```
 React (JS)  ──►  Shadow Tree (C++, immutable)
                       │  Yoga layout
                       ▼
                 Commit (any thread)
                       │  diff old vs new
                       ▼
                 Mutations list
                       │
                       ▼
                 UI thread: Mount -> Native Views
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shadow tree | C++ tree for layout | Layout वाला C++ tree |
| Yoga | Flexbox layout engine | Flexbox layout engine |
| Commit | Finalize new tree | नया tree पक्का करना |
| Mount | Apply to native views | Native views पर लागू करना |
| Flattening | Remove layout-only views | सिर्फ layout वाले views हटाना |
| Concurrent rendering | Interruptible renders | बीच में रोके जा सकने वाले renders |

---

## ⚡ 3-Line Summary
**English:**
1. Fabric builds a C++ shadow tree, lays out with Yoga, then mounts native views.
2. It allows synchronous layout reads and React concurrent features.
3. View flattening reduces native views; use `collapsable={false}` when needed.

**Hindi:**
1. Fabric C++ shadow tree बनाता है, Yoga से layout करता है, फिर native views mount करता है।
2. Synchronous layout reads और React concurrent features मिलते हैं।
3. View flattening native views घटाती है; ज़रूरत हो तो `collapsable={false}` लगाओ।

---

## ➡️ Next Topic
**173. TurboModules** — native functionality (camera, storage) को lazy और type-safe तरीके से JS में लाना।
