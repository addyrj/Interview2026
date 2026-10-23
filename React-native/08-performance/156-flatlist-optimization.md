# 156. FlatList Optimization
# हिंदी में: FlatList को Optimize कैसे करें?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
FlatList is already virtualized (only visible items rendered), but poor usage causes janky scrolling. Optimization means: stable `keyExtractor`, fast `renderItem` (wrapped in `React.memo`), `getItemLayout` for known item heights, image optimization, `removeClippedSubviews`, and avoiding inline function creation. A properly optimized FlatList handles 10,000+ items at 60fps.

## 🔵 सरल परिभाषा (Hindi)
FlatList already virtualized है (केवल visible items render होते हैं), लेकिन poor usage janky scrolling करती है। Optimization का मतलब: stable `keyExtractor`, fast `renderItem` (`React.memo` में wrap), known item heights के लिए `getItemLayout`, image optimization, `removeClippedSubviews`, और inline function creation से बचाव। Properly optimized FlatList 10,000+ items पर 60fps handle करती है।

---

## 🔴 Problem it Solves
```
COMMON FLATLIST PERFORMANCE ISSUES:
❌ Blank rows during fast scroll (items not rendered fast enough)
❌ Dropped frames (JS thread busy, UI skips frames)
❌ Items re-rendering when they shouldn't (no React.memo)
❌ Slow initial load (large images, complex components)
❌ Wrong key extraction (index as key = bad reordering)
❌ Jump-to-item broken (no getItemLayout = O(n) calculation)

EACH PROBLEM'S CAUSE + FIX:
Blank rows → more initialNumToRender, windowSize
Dropped frames → React.memo on renderItem
Slow items → lighter components, image optimization
Wrong keys → stable unique IDs as keyExtractor
Jump broken → getItemLayout for fixed-height items
```

## 🔴 यह क्यों बना? (Hindi)
```
FlatList virtualized है लेकिन wrong usage performance kill करता है:
- Re-renders: React.memo नहीं = हर scroll पर all visible items re-render
- Blank rows: windowSize कम = fast scroll पर empty space
- Jump: getItemLayout नहीं = scrollToIndex slow
```

---

## 🟢 How it Works — Step by Step

```
FLATLIST VIRTUALIZATION:
──────────────────────────────────────────────────────
  Total items: 1000 restaurant cards

  windowSize={10} (default) means:
  Render items in a window of:
  10 × viewport heights above + current view + 10 × viewport heights below
  ≈ 30-40 items in memory at once (not 1000!)

  As user scrolls:
  - New items enter the window → renderItem called
  - Old items leave the window → unmounted from memory
  - Items at edges re-mount → may see "blank" for a moment

  WHAT SLOWS THIS DOWN:
  1. renderItem creates component from scratch (no memoization)
     → Fast scroll: 30 new mounts per second → slow!

  2. renderItem function reference changes on parent re-render
     → React.memo on item doesn't help (props change = re-render)

  3. No getItemLayout → FlatList can't jump to offset
     → scrollToIndex requires measuring each item = O(n)

OPTIMIZATION TOOLS:
  keyExtractor    → stable, unique key → proper recycling
  React.memo      → skip re-render if props same
  getItemLayout   → pre-computed item height → fast scrollToIndex
  removeClippedSubviews → unload off-screen items from memory
  initialNumToRender → items rendered for first screen
  windowSize      → how many viewports to keep rendered
  maxToRenderPerBatch → items rendered per batch update
```

## 🟢 कैसे काम करता है? (Hindi)
```
FlatList window: viewport × windowSize items in memory।
Scroll करने पर: new items mount, old items unmount।
React.memo: same props → no re-render = fast।
getItemLayout: pre-computed height → scrollToIndex instant।
```

---

## 🟡 Real World Example
**Myntra product listing (10,000+ products):** Unoptimized: scrolling feels laggy, blank white cards appear during fast scroll. Optimized: `React.memo` on `ProductCard` stops unnecessary re-renders, `getItemLayout` (all cards 280px tall) enables `scrollToIndex` for "back to top" button, `keyExtractor={item => item.id}` ensures stable recycling, FastImage for product photos with priority loading, `removeClippedSubviews` on Android saves 40% memory.

## 🟡 Real Example Hindi मे
**Myntra 10,000+ products:** Unoptimized: blank cards, jank। Optimized: `React.memo`, `getItemLayout` (280px cards), `keyExtractor={item => item.id}`, FastImage, `removeClippedSubviews` → smooth 60fps scroll।

---

## 💻 Code Example — Basic

```jsx
import React, { useCallback, memo } from 'react';
import { FlatList, View, Text, Image, StyleSheet } from 'react-native';

// STEP 1: Memoize the item component
// Without memo: re-renders on every parent state change!
const RestaurantCard = memo(function RestaurantCard({ item, onPress }) {
  return (
    <View style={styles.card}>
      <Image
        source={{ uri: item.imageUrl }}
        style={styles.image}
        resizeMode="cover"
      />
      <Text style={styles.name}>{item.name}</Text>
      <Text style={styles.rating}>⭐ {item.rating}</Text>
    </View>
  );
  // memo: only re-renders if item or onPress actually changes
});

function RestaurantList({ restaurants }) {
  // STEP 2: Stable key extractor (use ID, NOT index)
  const keyExtractor = useCallback((item) => item.id, []);

  // STEP 3: Stable renderItem (no inline function!)
  const renderItem = useCallback(({ item }) => (
    <RestaurantCard item={item} onPress={() => {}} />
  ), []);  // empty deps → function never recreates

  // STEP 4: getItemLayout — ONLY if items have FIXED height!
  const ITEM_HEIGHT = 200;  // restaurant card height
  const getItemLayout = useCallback((data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  }), []);

  return (
    <FlatList
      data={restaurants}
      keyExtractor={keyExtractor}          // STEP 2
      renderItem={renderItem}              // STEP 3
      getItemLayout={getItemLayout}        // STEP 4 (fixed height items only)

      // Performance props:
      initialNumToRender={8}               // render first 8 items immediately
      maxToRenderPerBatch={10}             // render 10 items per batch
      windowSize={10}                      // keep 10 viewports rendered
      removeClippedSubviews={true}         // Android: unload off-screen items
      updateCellsBatchingPeriod={50}       // batch render interval (ms)
    />
  );
}

const styles = StyleSheet.create({
  card: { height: 200, marginHorizontal: 16, marginVertical: 8, borderRadius: 12, overflow: 'hidden' },
  image: { width: '100%', height: 130 },
  name: { fontSize: 16, fontWeight: '700', padding: 8 },
  rating: { fontSize: 14, paddingHorizontal: 8 },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useCallback, memo, useMemo } from 'react';
import { FlatList, View, Text, StyleSheet, useWindowDimensions } from 'react-native';
import FastImage from 'react-native-fast-image';

// FULLY OPTIMIZED FlatList — all best practices
const ProductCard = memo(function ProductCard({ item, cardWidth }) {
  // Destructure only what's needed (smaller memo comparison surface)
  const { id, name, price, imageUrl, discount } = item;

  return (
    <View style={[styles.card, { width: cardWidth }]}>
      <FastImage
        source={{
          uri: imageUrl,
          priority: FastImage.priority.normal,
        }}
        style={[styles.image, { height: cardWidth * 1.3 }]}
        resizeMode={FastImage.resizeMode.cover}
      />
      {discount > 0 && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{discount}% OFF</Text>
        </View>
      )}
      <View style={styles.cardInfo}>
        <Text style={styles.productName} numberOfLines={2}>{name}</Text>
        <Text style={styles.productPrice}>₹{price}</Text>
      </View>
    </View>
  );
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if item or cardWidth changes
  return prevProps.item.id === nextProps.item.id &&
         prevProps.item.price === nextProps.item.price &&  // price can change
         prevProps.cardWidth === nextProps.cardWidth;
});

function OptimizedProductGrid({ products, onEndReached }) {
  const { width } = useWindowDimensions();

  // Memoized card dimensions
  const { cardWidth, numColumns, ITEM_HEIGHT } = useMemo(() => {
    const cols = width >= 768 ? 3 : 2;
    const cw = (width - 16 * 2 - 8 * (cols - 1)) / cols;
    return { cardWidth: cw, numColumns: cols, ITEM_HEIGHT: cw * 1.3 + 80 };
  }, [width]);

  const keyExtractor = useCallback((item) => item.id, []);

  const renderItem = useCallback(({ item }) => (
    <ProductCard item={item} cardWidth={cardWidth} />
  ), [cardWidth]);

  // Fixed height = getItemLayout works!
  const getItemLayout = useCallback((data, index) => {
    const row = Math.floor(index / numColumns);
    return {
      length: ITEM_HEIGHT,
      offset: ITEM_HEIGHT * row,
      index,
    };
  }, [ITEM_HEIGHT, numColumns]);

  // List empty component (memoized — doesn't need to change)
  const ListEmptyComponent = useMemo(() => (
    <View style={styles.empty}>
      <Text style={styles.emptyText}>No products found</Text>
    </View>
  ), []);

  // Footer loading indicator (memoized)
  const ListFooterComponent = useMemo(() => (
    <View style={styles.footer}>
      <Text>Loading more...</Text>
    </View>
  ), []);

  return (
    <FlatList
      data={products}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      numColumns={numColumns}
      key={numColumns}                       // remount when columns change
      getItemLayout={getItemLayout}
      ListEmptyComponent={ListEmptyComponent}
      ListFooterComponent={ListFooterComponent}

      // Performance tuning:
      initialNumToRender={12}               // first screen of items
      maxToRenderPerBatch={12}
      windowSize={5}                        // 5 viewports (smaller = less memory)
      removeClippedSubviews                 // Android: unmount off-screen items

      // Infinite scroll:
      onEndReached={onEndReached}
      onEndReachedThreshold={0.5}           // trigger when 50% from bottom

      // Spacing:
      columnWrapperStyle={styles.row}
      contentContainerStyle={styles.content}

      // Scroll indicator:
      showsVerticalScrollIndicator={false}
    />
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 8, borderRadius: 12, overflow: 'hidden', backgroundColor: '#fff' },
  image: { width: '100%' },
  badge: {
    position: 'absolute', top: 8, left: 8,
    backgroundColor: '#f97316', borderRadius: 4, paddingHorizontal: 6, paddingVertical: 2,
  },
  badgeText: { color: '#fff', fontSize: 11, fontWeight: '700' },
  cardInfo: { padding: 8 },
  productName: { fontSize: 13, fontWeight: '500', color: '#333' },
  productPrice: { fontSize: 15, fontWeight: '700', color: '#f97316', marginTop: 4 },
  row: { gap: 8 },
  content: { padding: 16, paddingBottom: 80 },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40 },
  emptyText: { fontSize: 16, color: '#999' },
  footer: { padding: 16, alignItems: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `removeClippedSubviews` | ✅ More impactful (lower memory) | ⚠️ Less impactful, may cause bugs |
| Scroll performance | More prone to jank on low-end devices | Generally smoother |
| Image loading | Fresco (RN) or Glide (FastImage) | SDWebImage (FastImage) |
| Recycler | ViewHolder pattern | UITableViewCell recycling |
| `initialScrollIndex` | ✅ | ✅ (needs `getItemLayout`) |

---

## 🟠 Expo vs CLI Difference

Expo way:
```jsx
// expo-image for better image performance in FlatList
import { Image } from 'expo-image';
// Built-in Expo — better memory management, blurhash placeholders
// No extra native setup needed!
```

CLI way:
```jsx
// react-native-fast-image for Glide/SDWebImage power
import FastImage from 'react-native-fast-image';
// Better cache control + priority loading
// Needs native config after npm install
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Inline renderItem creates new function every render
```jsx
// WRONG: New function on every parent render → React.memo on item is useless!
<FlatList
  renderItem={({ item }) => <ProductCard item={item} />}  // ❌ new function each render
/>

// CORRECT: Stable renderItem with useCallback
const renderItem = useCallback(({ item }) => <ProductCard item={item} />, []);
<FlatList renderItem={renderItem} />  // ✅ same function reference
```

❌ **Mistake 2:** Using array index as key
```jsx
// WRONG: Index as key → wrong animation/re-render on list reorder/filter
<FlatList keyExtractor={(item, index) => String(index)} />  // ❌

// CORRECT: Stable unique ID
<FlatList keyExtractor={(item) => item.id} />  // ✅
```

❌ **Mistake 3:** Using `getItemLayout` with variable-height items
```jsx
// WRONG: All items have different heights but getItemLayout assumes fixed
const getItemLayout = (data, index) => ({
  length: 200,     // ❌ some items are 150px, some 300px!
  offset: 200 * index,   // wrong offset!
  index,
});
// Result: scrollToIndex shows wrong position, items overlap!

// CORRECT: Only use getItemLayout if ALL items have identical height
// If variable heights: remove getItemLayout, live with slower scrollToIndex
```

---

## 🧠 Tricky Interview Question

**Q: You have a FlatList where items have dynamic heights (comments with different text length). How do you still use `scrollToIndex`?**

**Answer:** `scrollToIndex` requires `getItemLayout` OR a fallback `viewabilityConfig`. Without `getItemLayout` on variable-height items, React Native must measure each item to calculate the offset — O(n) operation. Solutions: (1) **Approximate heights** — use `getItemLayout` with an average height. Items may be slightly off-position but scrollToIndex works. (2) **`onScrollToIndexFailed`** callback — when scrollToIndex fails, it provides a fallback index you can handle: scroll to approximate position, let items render, then scroll again more precisely. (3) **Flatten to fixed height** — redesign items to have a max height and use `numberOfLines` to truncate long text. (4) **Virtual layout manager** — measure item heights as they render and cache them in a `Map`, build a custom offset table. This is complex but enables exact scrolling.

---

## ⚫ Interview Questions + Answers

**Q1: Why is it important to memoize renderItem in FlatList?**
A1: FlatList's parent component often re-renders (state changes, context updates). Without memoization, `renderItem` is a new function reference on every render. Even if `React.memo` is on the item component, the new function reference means the item sees a new `renderItem` prop — it re-renders. With `useCallback(() => ..., [])`, the function reference is stable. Combined with `React.memo` on the item component, items only re-render when their own data changes.

**Q2: What is `getItemLayout` and when should you use it?**
A2: `getItemLayout` is an optimization for FlatLists where items have a known, fixed height. It returns `{ length, offset, index }` for any given index without measuring. Benefits: (1) `scrollToIndex`/`scrollToOffset` works instantly — no item measuring needed. (2) Faster initial rendering. (3) Better performance overall. Use ONLY when items have identical heights. If heights vary, skip it or accept approximate values.

**Q3: What is the difference between `windowSize`, `initialNumToRender`, and `maxToRenderPerBatch`?**
A3: `initialNumToRender`: number of items rendered on the first render (for first screen view). `maxToRenderPerBatch`: number of additional items rendered per batch as user scrolls. `windowSize`: total viewport-height units to keep in memory (5 = 2 above + current + 2 below viewports, roughly). Smaller `windowSize` = less memory, more blank rows on fast scroll. Larger = smoother but uses more memory. Default `windowSize=10` is a good balance for most lists.

**Q4: What is `removeClippedSubviews` and when should you use it?**
A4: `removeClippedSubviews={true}` (Android) instructs the native layer to unmount views that are outside the visible window. This can reduce memory usage by ~20-40% for large lists with images. However, it can cause flashes (briefly unmounted items re-mounting) and has known bugs with nested FlatLists. Recommended: enable on Android for long lists with images; be cautious with iOS where it can cause issues. Not a substitute for `windowSize` management — use both together.

**Q5: How do you implement infinite scroll (pagination) with FlatList?**
A5: Use `onEndReached` (fires when scroll position reaches near the end) and `onEndReachedThreshold` (0.5 = trigger when 50% from the bottom — so more data loads before hitting the real end). Pattern: `onEndReached={() => { if (!loading && hasMore) { setPage(p => p + 1); fetchNextPage(); } }}`. Prevent duplicate fetches with a `loading` flag. Show loading indicator in `ListFooterComponent`. Append new items to existing data: `setItems(prev => [...prev, ...newItems])`. Don't reset the whole array (causes full re-render).

---

## 🔷 When to Use + When Not to Use
✅ **Always in production FlatList:**
- `React.memo` on item component
- `useCallback` on `renderItem` + `keyExtractor`
- Stable unique `keyExtractor` (not index)
- `removeClippedSubviews` on Android

✅ **When items have fixed heights:**
- `getItemLayout` for fast scroll-to-index

❌ **Don't over-optimize for small lists:**
- 20 items: `React.memo` not critical
- 50 items: `getItemLayout` not needed if no scroll-to-index
- Focus optimization effort on 200+ item lists

---

## 📊 Visual Diagram

```
FLATLIST WINDOW (windowSize=5):
──────────────────────────────────────────────────────
  ...not rendered (above window)...
  ┌────────────────────────────────────┐  ← 2 viewports above
  │  Item 3 (rendered, not visible)    │
  │  Item 4 (rendered, not visible)    │
  ├────────────────────────────────────┤
  │  Item 5  ← VISIBLE                 │
  │  Item 6  ← VISIBLE                 │
  │  Item 7  ← VISIBLE                 │  ← current viewport
  ├────────────────────────────────────┤
  │  Item 8 (rendered, not visible)    │
  │  Item 9 (rendered, not visible)    │
  └────────────────────────────────────┘  ← 2 viewports below
  ...not rendered (below window)...

OPTIMIZATION CHECKLIST:
──────────────────────────────────────────────────────
  ✅ keyExtractor={item => item.id}         → stable recycling
  ✅ renderItem = useCallback(...)          → stable function
  ✅ ItemComponent = memo(...)             → skip if props unchanged
  ✅ getItemLayout (if fixed height)       → fast scrollToIndex
  ✅ removeClippedSubviews (Android)       → less memory
  ✅ initialNumToRender={8-12}             → fast initial render
  ✅ windowSize={5}                        → balance memory/blanks
  ✅ FastImage or expo-image              → fast image loading
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualization | Render only visible items | केवल visible items render |
| keyExtractor | Stable unique key per item | Item का unique key |
| getItemLayout | Pre-computed height/offset | Pre-computed height/offset |
| windowSize | Viewports to keep in memory | Memory में रखने वाले viewports |
| removeClippedSubviews | Unload off-screen on Android | Off-screen items unload (Android) |
| React.memo | Skip re-render if props same | Same props = no re-render |
| useCallback | Stable function reference | Stable function reference |
| initialNumToRender | First render item count | पहले render में items |

---

## ⚡ 3-Line Summary
**English:**
1. Wrap item components in `React.memo` and `renderItem` in `useCallback` — this prevents unnecessary re-renders as user scrolls.
2. Use stable `keyExtractor={item => item.id}` (never index), and `getItemLayout` only when all items have identical fixed height.
3. `removeClippedSubviews` on Android reduces memory; tune `windowSize` and `initialNumToRender` based on item complexity and target device class.

**Hindi:**
1. Item components को `React.memo` में और `renderItem` को `useCallback` में wrap करो — scroll पर unnecessary re-renders रुकते हैं।
2. Stable `keyExtractor={item => item.id}` (index कभी नहीं), `getItemLayout` only fixed height items के लिए।
3. Android पर `removeClippedSubviews`; `windowSize` और `initialNumToRender` item complexity और target device के अनुसार tune करो।

---

## ➡️ Next Topic
**157. JS Thread Performance — InteractionManager, useTransition** — heavy work को animate करने के बाद defer करना।
