# 27. FlatList Component
# हिंदी में: FlatList — Virtualized List Component
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**FlatList** is React Native's performant list component that uses **virtualization** — it only renders items currently visible on screen plus a small buffer. Unlike `ScrollView` (renders ALL children), FlatList renders 10-20 items at a time regardless of list size. Critical for any dynamic list: feeds, search results, orders, contacts, products.

## 🔵 सरल परिभाषा (Hindi)
**FlatList** React Native का performant list component है जो **virtualization** use करता है — सिर्फ screen पर visible items render होते हैं, सब नहीं। `ScrollView` (सभी children render) के unlike, FlatList list size कितनी भी हो — सिर्फ 10-20 items render। Dynamic lists के लिए critical: feeds, search results, orders, contacts, products।

---

## 🔴 Problem it Solves
```
PROBLEM WITH SCROLLVIEW FOR LONG LISTS:
  Swiggy restaurant list: 200 restaurants
  ScrollView: renders ALL 200 items on mount
    → 200 × component creation
    → 200 × image + text layout
    → HIGH memory usage
    → Slow initial render
    → Janky scroll performance

FLATLIST SOLUTION (Virtualization):
  Only renders items currently visible + small buffer
  Device screen shows ~8 restaurants at a time
  FlatList renders ~20 (windowSize buffer)
  User scrolls → new items mount, old items unmount
  Memory stays constant regardless of list size!

RESULT:
  ScrollView 200 items: ~400MB RAM
  FlatList 200 items: ~40MB RAM (10x less!)
```

## 🔴 यह क्यों बना? (Hindi)
```
ScrollView 200 items = सब render = slow + high memory।
FlatList = सिर्फ visible items render = fast + low memory।
Swiggy 500 restaurants? FlatList handles easily।
ScrollView 500 restaurants? App crash।
```

---

## 🟢 How it Works — Step by Step

```
FLATLIST VIRTUALIZATION:
──────────────────────────────────────────────────────
  Screen shows items 0-7 (visible viewport)
  FlatList renders items: 0-15 (windowSize buffer)
  Items 16-199: NOT rendered (just placeholders)

  USER SCROLLS DOWN:
    Items 0-3 scroll off screen → UNMOUNTED (freed from memory)
    Items 16-19 enter buffer → MOUNTED
    Items 8-15 still visible + rendered

  ALWAYS MOUNTED: windowSize * screen_height worth of items
  Default windowSize=21 → 10 screens above + 10 below + 1 visible

  KEY INTERNALS:
    RecyclerView (Android) / UICollectionView (iOS) under the hood
    VirtualizedList is the base class (FlatList wraps it)
    SectionList is VirtualizedList with section headers
```

## 🟢 कैसे काम करता है? (Hindi)
```
FlatList सिर्फ visible items + windowSize buffer render करता है।
Scroll करो → old items unmount, new items mount।
Memory constant रहती है।
Internally: Android RecyclerView / iOS UICollectionView।
```

---

## 🟡 Real World Example
**Zomato Food Feed:** 500+ restaurants in city. FlatList loads first 10 visible restaurants instantly. User scrolls → lazy loads next restaurants, images start loading as they enter viewport. Without FlatList: all 500 restaurant cards with images would render at once — 10-second load, 500MB RAM spike, app freeze. With FlatList: smooth 60fps scroll, constant ~50MB RAM, images load progressively.

## 🟡 Real Example Hindi मे
**Zomato:** 500+ restaurants. FlatList पहले 10 दिखाता है। Scroll करो → next restaurants load। बिना FlatList: 500 cards एकसाथ → 10 second load, 500MB RAM, app freeze। FlatList से: 60fps scroll, constant 50MB RAM, progressive image loading।

---

## 💻 Code Example — Basic

```tsx
import React from 'react';
import { FlatList, View, Text, StyleSheet, Image } from 'react-native';

// Type for each list item
type Restaurant = {
  id: string;
  name: string;
  cuisine: string;
  rating: number;
  deliveryTime: number;
  imageUrl: string;
};

// SAMPLE DATA
const restaurants: Restaurant[] = Array.from({ length: 100 }, (_, i) => ({
  id: `rest-${i}`,
  name: `Restaurant ${i + 1}`,
  cuisine: ['North Indian', 'Chinese', 'Pizza', 'Biryani'][i % 4],
  rating: 3.5 + (i % 15) * 0.1,
  deliveryTime: 20 + (i % 20),
  imageUrl: `https://via.placeholder.com/150?text=Food${i}`,
}));

// ITEM COMPONENT — extracted outside parent (important for performance)
function RestaurantCard({ item }: { item: Restaurant }) {
  return (
    <View style={styles.card}>
      <Image
        source={{ uri: item.imageUrl }}
        style={styles.image}
        resizeMode="cover"
      />
      <View style={styles.info}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.cuisine}>{item.cuisine}</Text>
        <Text style={styles.meta}>⭐ {item.rating.toFixed(1)} • {item.deliveryTime} min</Text>
      </View>
    </View>
  );
}

export default function RestaurantList() {
  return (
    <FlatList
      data={restaurants}                         // required: array of items

      renderItem={({ item }) => (                // required: renders each item
        <RestaurantCard item={item} />
      )}

      keyExtractor={(item) => item.id}           // required: unique key per item
                                                 // ALWAYS use item.id, NOT index!

      // OPTIONAL BUT RECOMMENDED:
      ItemSeparatorComponent={() => (            // divider between items
        <View style={styles.separator} />
      )}
      ListHeaderComponent={() => (              // sticky-able header
        <Text style={styles.header}>Restaurants near you</Text>
      )}
      ListFooterComponent={() => (              // footer (loading indicator)
        <Text style={styles.footer}>End of list</Text>
      )}
      ListEmptyComponent={() => (              // shown when data=[] (no results)
        <Text style={styles.empty}>No restaurants found</Text>
      )}
    />
  );
}

const styles = StyleSheet.create({
  card: { flexDirection: 'row', padding: 12, backgroundColor: 'white' },
  image: { width: 80, height: 80, borderRadius: 8 },
  info: { flex: 1, marginLeft: 12 },
  name: { fontSize: 16, fontWeight: '600' },
  cuisine: { fontSize: 14, color: '#666', marginTop: 4 },
  meta: { fontSize: 13, color: '#888', marginTop: 4 },
  separator: { height: 1, backgroundColor: '#f0f0f0' },
  header: { padding: 16, fontSize: 20, fontWeight: '700' },
  footer: { padding: 16, textAlign: 'center', color: '#999' },
  empty: { padding: 40, textAlign: 'center', color: '#999', fontSize: 16 },
});
```

## 💻 Code Example — Advanced (Full Optimized FlatList)

```tsx
import React, { useState, useCallback, useRef, memo } from 'react';
import {
  FlatList,
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  ListRenderItemInfo,
} from 'react-native';

// TYPE
type Product = {
  id: string;
  name: string;
  price: number;
  category: string;
};

// ITEM HEIGHT (fixed) — enables getItemLayout optimization
const ITEM_HEIGHT = 80;

// ───────────────────────────────────────────────────────
// OPTIMIZATION 1: memo wrapping — prevents re-render if item hasn't changed
// ───────────────────────────────────────────────────────
const ProductItem = memo(function ProductItem({
  item,
  onPress,
}: {
  item: Product;
  onPress: (id: string) => void;
}) {
  return (
    <View style={styles.item}>
      <View style={styles.itemLeft}>
        <Text style={styles.itemName}>{item.name}</Text>
        <Text style={styles.itemCategory}>{item.category}</Text>
      </View>
      <Text style={styles.itemPrice}>₹{item.price}</Text>
    </View>
  );
},
// CUSTOM COMPARISON FUNCTION (optional)
// Only re-render if id or price changed (ignore other fields)
(prevProps, nextProps) =>
  prevProps.item.id === nextProps.item.id &&
  prevProps.item.price === nextProps.item.price
);

// ───────────────────────────────────────────────────────
// PARENT COMPONENT
// ───────────────────────────────────────────────────────
export default function ProductList() {
  const [products, setProducts] = useState<Product[]>([
    ...Array.from({ length: 50 }, (_, i) => ({
      id: `prod-${i}`,
      name: `Product ${i + 1}`,
      price: 99 + i * 10,
      category: ['Electronics', 'Clothing', 'Food'][i % 3],
    })),
  ]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [page, setPage] = useState(1);

  const flatListRef = useRef<FlatList>(null);

  // ─────────────────────────────────────────
  // OPTIMIZATION 2: useCallback on renderItem
  // Without this, new function ref each render → child re-renders even with memo
  // ─────────────────────────────────────────
  const handlePress = useCallback((id: string) => {
    console.log('pressed:', id);
  }, []);

  const renderItem = useCallback(
    ({ item }: ListRenderItemInfo<Product>) => (
      <ProductItem item={item} onPress={handlePress} />
    ),
    [handlePress]
  );

  // ─────────────────────────────────────────
  // OPTIMIZATION 3: stable keyExtractor
  // ─────────────────────────────────────────
  const keyExtractor = useCallback((item: Product) => item.id, []);

  // ─────────────────────────────────────────
  // OPTIMIZATION 4: getItemLayout — enables instant scroll to index
  // ONLY use when ALL items have the same fixed height!
  // ─────────────────────────────────────────
  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: ITEM_HEIGHT,
      offset: ITEM_HEIGHT * index,
      index,
    }),
    []
  );

  // PULL-TO-REFRESH
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsRefreshing(false);
  }, []);

  // INFINITE SCROLL (load more when near end)
  const handleEndReached = useCallback(async () => {
    if (isLoadingMore) return;
    setIsLoadingMore(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    const newProducts = Array.from({ length: 10 }, (_, i) => ({
      id: `prod-${products.length + i}`,
      name: `Product ${products.length + i + 1}`,
      price: 99 + (products.length + i) * 10,
      category: ['Electronics', 'Clothing', 'Food'][(products.length + i) % 3],
    }));
    setProducts(prev => [...prev, ...newProducts]);
    setIsLoadingMore(false);
    setPage(prev => prev + 1);
  }, [isLoadingMore, products.length]);

  // FOOTER: loading indicator for infinite scroll
  const ListFooter = useCallback(() => (
    isLoadingMore ? (
      <View style={styles.footer}>
        <ActivityIndicator size="small" color="#e23744" />
      </View>
    ) : null
  ), [isLoadingMore]);

  return (
    <FlatList
      ref={flatListRef}
      data={products}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      getItemLayout={getItemLayout}           // OPTIMIZATION 4

      // PULL TO REFRESH
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={handleRefresh}
          colors={['#e23744']}               // Android
          tintColor="#e23744"                // iOS
        />
      }

      // INFINITE SCROLL
      onEndReached={handleEndReached}
      onEndReachedThreshold={0.5}            // trigger when 50% from end

      ListFooterComponent={ListFooter}

      // PERFORMANCE PROPS:
      removeClippedSubviews={true}           // Android: unmount off-screen items
      initialNumToRender={8}                 // first batch (above fold)
      maxToRenderPerBatch={5}               // items rendered per scroll batch
      windowSize={5}                         // items kept rendered: 2 screens above/below
      updateCellsBatchingPeriod={50}         // ms between batches

      // SCROLL TO TOP button would use:
      // flatListRef.current?.scrollToOffset({ offset: 0, animated: true })
      // Or by index: flatListRef.current?.scrollToIndex({ index: 5 })
    />
  );
}

const styles = StyleSheet.create({
  item: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: ITEM_HEIGHT,
    paddingHorizontal: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  itemLeft: { flex: 1 },
  itemName: { fontSize: 15, fontWeight: '600', color: '#1a1a1a' },
  itemCategory: { fontSize: 13, color: '#888', marginTop: 4 },
  itemPrice: { fontSize: 16, fontWeight: '700', color: '#e23744' },
  footer: { paddingVertical: 20, alignItems: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native backing | RecyclerView | UICollectionView |
| `removeClippedSubviews` | ✅ Effective | Less impact (iOS handles itself) |
| Overscroll effect | Glow effect | Bounce effect |
| `scrollIndicatorInsets` | Not applicable | Scroll bar insets |
| Performance baseline | Slightly lower | Slightly higher |

---

## 🟠 Expo vs CLI Difference

Expo way:
```tsx
// FlatList is built-in — no installation needed
import { FlatList } from 'react-native';
// No difference between Expo and CLI for FlatList
```

CLI way:
```tsx
import { FlatList } from 'react-native';
// Same — FlatList is part of React Native core
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using array index as keyExtractor
```tsx
// WRONG: Index as key causes bugs when list reorders/filters
keyExtractor={(item, index) => index.toString()}

// CORRECT: Use stable unique ID
keyExtractor={(item) => item.id}
// Or: keyExtractor={(item) => `${item.id}-${item.version}`}
```

❌ **Mistake 2:** Defining renderItem inline (kills memo optimization)
```tsx
// WRONG: New function ref every parent render → ItemComponent always re-renders!
<FlatList
  renderItem={({ item }) => <ItemComponent item={item} />}  // inline arrow fn!
/>

// CORRECT: useCallback makes the function reference stable
const renderItem = useCallback(({ item }) => <ItemComponent item={item} />, []);
<FlatList renderItem={renderItem} />
```

❌ **Mistake 3:** Using getItemLayout with variable heights
```tsx
// WRONG: Items have different heights but getItemLayout assumes fixed
const getItemLayout = (_, index) => ({
  length: 80,   // ← but some items are 100px, some 60px!
  offset: 80 * index,
  index,
});
// RESULT: scrollToIndex goes to wrong position, misaligned items

// CORRECT: Only use getItemLayout when ALL items are the same height
// For variable heights: don't use getItemLayout (slight perf trade-off)
```

❌ **Mistake 4:** Forgetting ListEmptyComponent (bad UX)
```tsx
// WRONG: Empty list shows nothing — confusing for user
<FlatList data={filteredResults} renderItem={renderItem} />

// CORRECT: Always handle empty state
<FlatList
  data={filteredResults}
  renderItem={renderItem}
  ListEmptyComponent={() => (
    <View style={styles.empty}>
      <Text>No results found for your search</Text>
    </View>
  )}
/>
```

---

## 🧠 Tricky Interview Question

**Q: You have a FlatList where items have `React.memo` applied, but items are still re-rendering when parent state changes that shouldn't affect them. Why?**

**Answer:** `React.memo` does a shallow comparison of props. Three common culprits: (1) **`renderItem` is an inline arrow function** — new function reference every parent render → memo sees new `onPress` prop → re-renders. Fix: `useCallback`. (2) **Item data contains object references** — `item={{ ...oldItem, extra: 'static' }}` creates new object reference each render even if contents are same. Fix: don't create new objects during render; keep items stable or use a custom comparison function as the second arg to `memo`. (3) **Passing a callback to the item** — `onPress={() => handlePress(item.id)}` is a new function each render. Fix: `useCallback` in parent + pass the stable callback. Always profile with React DevTools (Flipper) to confirm which props changed.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between FlatList and ScrollView?**
A1: ScrollView renders **all** children immediately on mount — fine for small, fixed content (< 30 items, forms, settings). FlatList uses **virtualization** — renders only items in the visible viewport plus a buffer (windowSize). For a dynamic list of 100+ items (restaurant feed, product catalog), FlatList is required: ScrollView would render all 100 items upfront causing high memory, slow initial load, and janky scroll.

**Q2: What are the 3 required props for FlatList?**
A2: (1) `data`: the array of items. (2) `renderItem`: function that receives `{item, index, separators}` and returns a React element. (3) `keyExtractor`: function that returns a unique string key for each item. While `keyExtractor` is technically optional (FlatList falls back to `item.key` or `item.id`), always provide it explicitly to ensure correct behavior when list items reorder.

**Q3: What is `getItemLayout` and when should you NOT use it?**
A3: `getItemLayout` tells FlatList the height (or width for horizontal lists) of each item without measuring it, enabling instant `scrollToIndex`. Returns `{ length, offset, index }`. **Only use it when all items have the same fixed height** — if heights vary, `getItemLayout` provides wrong offsets and `scrollToIndex` goes to wrong positions. For variable-height lists, omit it (FlatList measures items as they render) and use `scrollToOffset` with manually tracked positions for scroll-to-index behavior.

**Q4: How does `removeClippedSubviews` work?**
A4: On Android, it detaches items that have scrolled far off-screen from the native view tree (without unmounting the JS component). This reduces GPU rendering work. Most effective on Android with long lists of complex items. On iOS, UICollectionView's native recycling already handles this well, so the prop has less impact. Potential downside: occasional flicker when items scroll back into view on slow devices. Test carefully; sometimes the default without it is smoother.

**Q5: How do you scroll FlatList to a specific item programmatically?**
A5: Three methods via `ref.current`: (1) `scrollToIndex({ index: 5, animated: true })` — requires `getItemLayout` for variable-height items; (2) `scrollToOffset({ offset: 400, animated: true })` — scroll to pixel offset; (3) `scrollToItem({ item: specificItem, animated: true })` — O(n) search, slower. Most common: use `scrollToOffset` with a pre-calculated position, or `scrollToIndex` if `getItemLayout` is already set. Always wrap in `InteractionManager.runAfterInteractions` if called right after navigation to avoid janky transitions.

---

## 🔷 When to Use + When Not to Use
✅ **Use FlatList for:**
- Any list with 30+ items (restaurant list, product catalog, search results)
- Lists where items load dynamically / infinite scroll
- Lists with pull-to-refresh
- Any list where you don't know the count ahead of time

✅ **Use ScrollView when:**
- Content is short and fixed (settings screen, profile page, forms)
- Mixed content (not just a list — sections, images, paragraphs between items)
- You need `stickyHeaderIndices`
- < 30 items, static content

✅ **Use SectionList when:**
- Grouped data with section headers (contacts by letter, orders by date)
- FlatList but with sticky section headers

---

## 📊 Visual Diagram

```
SCROLLVIEW vs FLATLIST — Memory Model:
──────────────────────────────────────────────────────

  ScrollView (100 items):
  ┌──────────────────────────────┐
  │ Item 1  ← rendered           │  ← VISIBLE VIEWPORT
  │ Item 2  ← rendered           │
  │ Item 3  ← rendered           │
  └──────────────────────────────┘
    Item 4  ← rendered (off-screen, still in memory!)
    Item 5  ← rendered (off-screen)
    ...
    Item 100 ← rendered (off-screen)
  ALL 100 items in memory at all times!

  FlatList (100 items, windowSize=5):
  ┌──────────────────────────────┐
  │ Item 5  ← rendered           │
  │ Item 6  ← rendered           │  ← VISIBLE VIEWPORT
  │ Item 7  ← rendered           │
  │ Item 8  ← rendered           │
  └──────────────────────────────┘
    Item 9  ← rendered (buffer below)   │
    Item 10 ← rendered (buffer below)   │ windowSize buffer
    Item 4  ← rendered (buffer above)   │
    Item 3  ← rendered (buffer above)   │
    
    Item 1, 2  → UNMOUNTED (too far above)
    Item 11-100 → NOT YET MOUNTED

  Only ~10 items in memory regardless of list size!

PERFORMANCE COMPARISON (100 restaurant items):
  ScrollView: ~400ms initial render, 200MB RAM, 45fps scroll
  FlatList:   ~50ms initial render,  40MB RAM, 60fps scroll
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualization | Only render visible items | सिर्फ visible items render |
| keyExtractor | Unique key function for each item | हर item के लिए unique key function |
| renderItem | Function that renders each list row | हर list row render करने वाला function |
| windowSize | Screens worth of items to keep rendered | Render रखने वाले items की count |
| getItemLayout | Pre-defined item heights for fast scroll | Fast scroll के लिए item heights |
| removeClippedSubviews | Detach off-screen items (Android) | Off-screen items detach करो |
| onEndReached | Callback when near list end | List end के पास callback |
| ListEmptyComponent | Component shown when data=[] | Empty data पर दिखने वाला component |
| memo | Prevents unnecessary re-renders | Unnecessary re-renders रोकता है |

---

## ⚡ 3-Line Summary
**English:**
1. FlatList uses virtualization — only renders visible items + buffer, keeping memory constant regardless of list size; ScrollView renders everything at once.
2. For performance: `React.memo` on item component, `useCallback` on `renderItem`, stable `keyExtractor` (never index), `getItemLayout` for fixed-height items.
3. FlatList props: `ListEmptyComponent` (no results), `refreshControl` (pull-to-refresh), `onEndReached` + `onEndReachedThreshold` (infinite scroll).

**Hindi:**
1. FlatList virtualization use करता है — सिर्फ visible items + buffer render, memory constant। ScrollView सब render करता है।
2. Performance के लिए: item पर `React.memo`, `renderItem` पर `useCallback`, stable `keyExtractor` (index नहीं), fixed height items के लिए `getItemLayout`।
3. FlatList props: `ListEmptyComponent` (no results), `refreshControl` (pull-to-refresh), `onEndReached` (infinite scroll)।

---

## ➡️ Next Topic
**28. SectionList** — FlatList with grouped sections and sticky section headers।
