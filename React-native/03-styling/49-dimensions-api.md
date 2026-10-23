# 49. Dimensions API
# हिंदी में: Dimensions API क्या है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
`Dimensions` API gives you the current device screen width and height. Unlike CSS `vw`/`vh` units, React Native doesn't support percentage-based dimensions for all cases — so you use `Dimensions.get('window')` to calculate sizes based on actual screen dimensions. The newer `useWindowDimensions` hook is preferred as it updates automatically on orientation change.

## 🔵 सरल परिभाषा (Hindi)
`Dimensions` API आपको device की screen width और height देता है। CSS `vw`/`vh` units के unlike, React Native percentage-based dimensions सभी cases में support नहीं करता — इसलिए `Dimensions.get('window')` से actual screen size based calculations करते हैं। नया `useWindowDimensions` hook prefer किया जाता है क्योंकि orientation change पर automatically update होता है।

---

## 🔴 Problem it Solves
```
RESPONSIVE DESIGN PROBLEM:
Indian users use thousands of different screen sizes:
- Samsung Galaxy A14: 390 x 844 points
- Redmi Note 12: 393 x 852 points
- iPhone SE: 375 x 667 points
- iPad: 1024 x 1366 points
- Foldable phones: changes on fold/unfold!

Without Dimensions:
<View style={{ width: 300 }} />  // 300px — looks different on every device!
  - On small phone: takes 80% of screen
  - On tablet: takes only 30% of screen

With Dimensions:
const { width } = Dimensions.get('window');
<View style={{ width: width * 0.8 }} />  // always 80% of screen!
```

## 🔴 यह क्यों बना? (Hindi)
```
India में हजारों screen sizes।
Fixed pixels → हर device पर अलग दिखे।
Dimensions API → screen size से relative calculations →
हर device पर consistent UI।
```

---

## 🟢 How it Works — Step by Step

```
DIMENSIONS API:
──────────────────────────────────────────────────────
  Dimensions.get('window')
  → Returns: { width, height, scale, fontScale }
    width:     usable screen width (excluding nav bar on Android)
    height:    usable screen height
    scale:     device pixel ratio (1x, 2x, 3x)
    fontScale: user's font size setting (accessibility)

  Dimensions.get('screen')
  → Returns: full screen size including nav bar

  Dimensions.addEventListener('change', handler)
  → Fires when orientation changes (portrait ↔ landscape)
  → Fires on foldable phone fold/unfold

useWindowDimensions Hook (PREFERRED):
──────────────────────────────────────────────────────
  const { width, height, scale, fontScale } = useWindowDimensions();
  → Same data as Dimensions.get('window')
  → BUT: automatically re-renders when dimensions change!
  → Dimensions.get() does NOT re-render on change

ORIENTATION CHANGE:
  Portrait:  width < height
  Landscape: width > height
  Check: const isLandscape = width > height;
```

## 🟢 कैसे काम करता है? (Hindi)
```
Dimensions.get('window') → { width, height, scale, fontScale }
useWindowDimensions → same but auto-update on orientation change
scale: pixel density (Retina = 3x → 1pt = 3 actual pixels)
fontScale: user accessibility setting = big text → 1.5
```

---

## 🟡 Real World Example
**Myntra product grid:** 2 columns on phone, 3 on tablet, 4 on iPad. Using `useWindowDimensions`, the component calculates `numColumns = Math.floor(width / 200)` — automatically adjusts when user rotates device. Also calculates image height as `width / 2 - 16` to maintain aspect ratio. Without Dimensions API, the grid would be hardcoded and broken on tablets.

## 🟡 Real Example Hindi मे
**Myntra product grid:** Phone पर 2 columns, tablet पर 3-4। `useWindowDimensions` से `numColumns = Math.floor(width / 200)` — device rotate पर auto-adjust। Image height भी `width / 2 - 16` से calculate — proper aspect ratio हर device पर।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';
import { View, Text, StyleSheet, Dimensions, useWindowDimensions } from 'react-native';

// METHOD 1: Dimensions.get() — static, doesn't update on rotate
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// METHOD 2: useWindowDimensions hook — PREFERRED (updates on rotate)
function ResponsiveBox() {
  const { width, height } = useWindowDimensions();  // re-renders on change!

  const isTablet = width > 768;     // simple tablet detection
  const isLandscape = width > height; // orientation detection

  return (
    <View style={styles.container}>
      <Text style={styles.info}>
        Screen: {width.toFixed(0)} x {height.toFixed(0)}
      </Text>
      <Text style={styles.info}>
        {isTablet ? '📱 Tablet' : '📱 Phone'} — {isLandscape ? '↔ Landscape' : '↕ Portrait'}
      </Text>

      {/* 80% of screen width */}
      <View style={[styles.box, { width: width * 0.8 }]}>
        <Text>80% of screen width</Text>
      </View>

      {/* Half screen */}
      <View style={[styles.halfBox, { width: width / 2, height: height / 4 }]}>
        <Text>50% wide, 25% tall</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16 },
  info: { fontSize: 14, color: '#666', marginBottom: 8 },
  box: {
    backgroundColor: '#f97316',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  halfBox: {
    backgroundColor: '#0ea5e9',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
```

## 💻 Code Example — Advanced

```jsx
import React from 'react';
import { View, FlatList, StyleSheet, useWindowDimensions } from 'react-native';

// RESPONSIVE GRID — adapts to phone, tablet, landscape
function ProductGrid({ products }) {
  const { width } = useWindowDimensions();

  // Dynamic column count based on screen width
  const getNumColumns = (w) => {
    if (w >= 1024) return 4;  // iPad landscape / large tablet
    if (w >= 768) return 3;   // iPad portrait / small tablet
    if (w >= 480) return 2;   // large phone landscape
    return 2;                  // normal phone (always 2 for products)
  };

  const numColumns = getNumColumns(width);

  // Calculate item width from screen width
  const PADDING = 16;                           // page padding
  const GAP = 8;                                // gap between items
  const totalGaps = (numColumns - 1) * GAP;
  const itemWidth = (width - PADDING * 2 - totalGaps) / numColumns;
  const itemHeight = itemWidth * 1.4;           // 5:7 aspect ratio for product card

  const renderItem = ({ item }) => (
    <View style={[styles.item, { width: itemWidth, height: itemHeight }]}>
      {/* Product card content */}
    </View>
  );

  return (
    <FlatList
      data={products}
      renderItem={renderItem}
      keyExtractor={(item) => item.id}
      numColumns={numColumns}
      key={numColumns}  // IMPORTANT: when numColumns changes, remount FlatList!
      contentContainerStyle={styles.listContent}
      columnWrapperStyle={numColumns > 1 ? styles.row : undefined}
    />
  );
}

// RESPONSIVE LAYOUT — side panel on tablet, full screen on phone
function AppLayout({ leftContent, rightContent }) {
  const { width } = useWindowDimensions();
  const isTablet = width >= 768;

  if (isTablet) {
    // Side-by-side layout for tablets
    return (
      <View style={styles.tabletContainer}>
        <View style={{ width: 300 }}>{leftContent}</View>
        <View style={{ flex: 1 }}>{rightContent}</View>
      </View>
    );
  }

  // Full-screen layout for phones (navigate between them)
  return (
    <View style={{ flex: 1 }}>{rightContent}</View>
  );
}

const styles = StyleSheet.create({
  item: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 8,
  },
  listContent: { padding: 16 },
  row: { gap: 8 },
  tabletContainer: { flex: 1, flexDirection: 'row' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `window` height | Excludes navigation bar | Includes notch area |
| `screen` height | Full physical screen | Full physical screen |
| Orientation event | Fires on rotation | Fires on rotation |
| Foldable support | `window` changes on fold | Not applicable |
| Soft nav bar | Excluded from `window` | Not applicable |

---

## 🟠 Expo vs CLI Difference

Expo way:
```jsx
// useWindowDimensions — same in Expo
import { useWindowDimensions } from 'react-native';
const { width, height } = useWindowDimensions();

// Expo also has: expo-screen-orientation
// import * as ScreenOrientation from 'expo-screen-orientation';
// await ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.PORTRAIT);
```

CLI way:
```jsx
// Same useWindowDimensions
import { useWindowDimensions, Dimensions } from 'react-native';

// For orientation locking: react-native-orientation-locker
// import Orientation from 'react-native-orientation-locker';
// Orientation.lockToPortrait();
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `Dimensions.get()` directly in render (won't update on rotate)
```jsx
// WRONG: Doesn't re-render when orientation changes
const { width } = Dimensions.get('window');
function MyComponent() {
  return <View style={{ width: width * 0.8 }} />;  // ❌ stale on rotate!
}

// CORRECT: useWindowDimensions hook
function MyComponent() {
  const { width } = useWindowDimensions();  // ✅ updates on rotate
  return <View style={{ width: width * 0.8 }} />;
}
```

❌ **Mistake 2:** Not using `key` on FlatList when numColumns changes
```jsx
// WRONG: FlatList with changing numColumns
<FlatList numColumns={numColumns} data={data} renderItem={renderItem} />
// React Native warns: "Changing numColumns requires updating the key prop"

// CORRECT: key forces FlatList to remount when columns change
<FlatList
  key={numColumns}         // ← forces remount when numColumns changes!
  numColumns={numColumns}
  data={data}
  renderItem={renderItem}
/>
```

❌ **Mistake 3:** Assuming percentages work everywhere
```jsx
// In React Native:
// ✅ '100%' works for width/height in a FLEX context
// ❌ '100%' for position, margin, padding — MIGHT not work

// SAFE: Use Dimensions for calculations
const { width } = useWindowDimensions();
const cardWidth = (width - 32) / 2;  // 2 columns with 16px side padding
```

---

## 🧠 Tricky Interview Question

**Q: What is the difference between `Dimensions.get('window')` and `Dimensions.get('screen')` on Android?**

**Answer:** On Android: `screen` returns the full physical screen size (including the soft navigation bar at the bottom). `window` returns the usable area (excluding the navigation bar). Example: on a Samsung Galaxy S21, `screen.height` = 900dp, `window.height` = 840dp (60dp lost to navigation bar). On iOS: `window` and `screen` are usually the same (iOS handles safe areas differently via `SafeAreaView`). Always use `window` for layout calculations — that's the actual space your app can use. Use `screen` only if you need to know the full physical screen dimensions (unusual).

---

## ⚫ Interview Questions + Answers

**Q1: What is the Dimensions API in React Native?**
A1: `Dimensions` is a utility that returns the device's screen dimensions: `width`, `height`, `scale` (pixel density), and `fontScale` (user's accessibility font size multiplier). Use `Dimensions.get('window')` for usable screen area. It's used for responsive layouts where content size should be proportional to screen size. Note: `Dimensions.get()` gives a snapshot — it doesn't update on orientation change. Use `useWindowDimensions` hook instead for reactive dimensions.

**Q2: What is `useWindowDimensions` and when should you use it?**
A2: `useWindowDimensions` is a hook that returns the same `{ width, height, scale, fontScale }` as `Dimensions.get('window')` but re-renders the component when the screen dimensions change (orientation change, foldable fold/unfold, window resize). Use it for: responsive grid columns, adaptive layouts, orientation-dependent content. Rule: if your layout changes when the screen rotates, use `useWindowDimensions`. If dimensions are just used once (e.g., in StyleSheet.create outside a component), `Dimensions.get()` is fine.

**Q3: How do you build a responsive grid that adapts to tablet screens?**
A3: Use `useWindowDimensions` to get width, calculate numColumns based on width threshold (`width >= 768 ? 3 : 2`), calculate itemWidth as `(width - padding * 2 - gap * (numColumns - 1)) / numColumns`, pass both to `FlatList` with `numColumns={numColumns}` and add `key={numColumns}` to the FlatList (forces remount when column count changes). This pattern handles phones (2 columns), tablets (3-4 columns), and landscape mode automatically.

**Q4: What is `scale` and `fontScale` in Dimensions?**
A4: `scale` is the device pixel ratio (density). On a normal display = 1. On Retina/HDPI = 2 or 3. Meaning: if `scale=3`, a 100-point box is actually 300 physical pixels. React Native uses points (logical pixels), not physical pixels, so you don't need to worry about scale in most cases. `fontScale` is the user's accessibility text size multiplier — if user increased text size to 150%, `fontScale = 1.5`. Important for accessibility: if you hardcode text sizes in StyleSheet, large `fontScale` means text overflows containers.

**Q5: How do you detect if the app is running on a tablet?**
A5: Common pattern: `const { width } = useWindowDimensions(); const isTablet = width >= 768;`. More reliable: `import { Platform } from 'react-native'; const isIPad = Platform.isPad;` (iOS only). For Android tablets: there's no built-in API — width-based detection is the standard approach. Libraries like `react-native-device-info` provide `isTablet()` that checks physical screen size. For most responsive design, width-based breakpoints are sufficient and work on both platforms.

---

## 🔷 When to Use + When Not to Use
✅ **Use Dimensions/useWindowDimensions when:**
- Building responsive grids (2-column phone, 3-column tablet)
- Calculating image heights from width
- Orientation-adaptive layouts
- Detecting tablet vs phone

❌ **Don't overcomplicate:**
- Use `flex: 1` and `flexDirection` for most layouts — no Dimensions needed
- `width: '100%'` works for most full-width elements
- Only reach for Dimensions when % or flex can't achieve the layout

---

## 📊 Visual Diagram

```
RESPONSIVE GRID CALCULATION:
──────────────────────────────────────────────────────
  Screen width: 390px
  Page padding: 16px × 2 = 32px
  Gap between cols: 8px × 1 = 8px
  Available: 390 - 32 - 8 = 350px
  Per item: 350 / 2 = 175px wide

  ┌────────────────────────────────────────────┐
  │  ┌─────────────┐  ┌─────────────┐         │
  │  │   item 1    │  │   item 2    │         │
  │  │ 175px wide  │  │ 175px wide  │         │
  │  └─────────────┘  └─────────────┘         │
  └────────────────────────────────────────────┘

DEVICE SIZE BREAKPOINTS:
──────────────────────────────────────────────────────
  < 375px  → small phone (SE, old Android)  → 2 cols
  375-480  → normal phone                   → 2 cols
  481-767  → large phone/landscape          → 2-3 cols
  768-1023 → tablet portrait               → 3-4 cols
  1024+    → tablet landscape / iPad Pro   → 4+ cols

window vs screen (Android):
──────────────────────────────────────────────────────
  Physical screen: ████████████████████  screen.height = 900dp
  Nav bar:         ████████████████████  60dp
  App content:     ████████████████████  window.height = 840dp
  (your layout should use window.height)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dimensions | Screen size utility | Screen size utility |
| window | Usable app area (no nav bar) | App के लिए usable area |
| screen | Full physical screen size | पूरी physical screen |
| scale | Pixel density (1x, 2x, 3x) | Pixel density |
| fontScale | Accessibility text size multiplier | Accessibility text size |
| useWindowDimensions | Hook that updates on resize | Resize पर update होने वाला hook |
| Responsive | Adapts to screen size | Screen size के अनुसार adapt |
| numColumns | Columns in FlatList grid | FlatList grid में columns |

---

## ⚡ 3-Line Summary
**English:**
1. `Dimensions.get('window')` gives screen `{width, height}` — use for responsive size calculations; prefer `useWindowDimensions` hook which re-renders on orientation change.
2. `window` = usable area (minus Android nav bar); `screen` = full physical screen; `scale` = pixel density; `fontScale` = user accessibility text size.
3. For responsive grids: calculate `itemWidth = (screenWidth - padding - gaps) / numColumns` and pass `key={numColumns}` to FlatList when columns change.

**Hindi:**
1. `Dimensions.get('window')` screen `{width, height}` देता है; `useWindowDimensions` hook prefer करो — orientation change पर auto-update करता है।
2. `window` = usable area; `screen` = full screen; `scale` = pixel density; `fontScale` = user text size।
3. Responsive grids: `itemWidth = (screenWidth - padding - gaps) / numColumns`; FlatList पर `key={numColumns}` जरूर।

---

## ➡️ Next Topic
**50. useWindowDimensions Hook** — Dimensions का hook version, orientation handling, responsive patterns।
