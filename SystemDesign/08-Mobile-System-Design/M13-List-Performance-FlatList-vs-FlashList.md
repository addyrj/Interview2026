# M13. List Performance (FlatList vs FlashList)
# हिंदी में: List Performance — React Native में लंबी lists (feed, menu, chats, orders) को 60 fps पर smooth चलाना: FlatList (दिखने वाले items render, बाक़ी हटाओ) बनाम FlashList (पुराने cells को नए items के लिए दोबारा इस्तेमाल करो — recycling)

---

## 🔵 Simple Definition (English)
Most mobile screens are **lists**: feeds, menus, chats, search results, orders. React Native offers:
- **`ScrollView`**: renders **all** children at once. Only for short, fixed content.
- **`FlatList` / `SectionList`** (built on `VirtualizedList`): **virtualizes**, rendering items in a window around the viewport and **unmounting** items far away. Tuning props: `initialNumToRender`, `maxToRenderPerBatch`, `windowSize`, `getItemLayout`, `removeClippedSubviews`.
- **`FlashList`** (by Shopify): **recycles cell components** like Android's RecyclerView and iOS's UICollectionView. When an item scrolls off-screen, its already-mounted component is **reused with new props** instead of unmounting and mounting a new one. This means far less JS work, fewer blank cells and better FPS, especially on low-end Android. **FlashList v2** (built for the New Architecture) measures items automatically (no `estimatedItemSize`) and supports masonry layouts.
- Alternatives: **LegendList** (pure JS, recycling) and native lists via **RecyclerListView**.
Good list performance = **virtualization or recycling + cheap, memoized cells + stable keys + right-sized images + pagination**.

## 🔵 सरल परिभाषा (Hindi)
ज़्यादातर mobile screens lists हैं। ScrollView सब कुछ एक साथ render करता है (सिर्फ़ छोटे content के लिए); FlatList दिखने वाले हिस्से के आसपास के items render करता है और दूर वालों को हटा देता है (virtualization); FlashList (Shopify का) scroll से बाहर गए cell को नए item के लिए दोबारा इस्तेमाल करता है (recycling) — बहुत कम JS काम, कम ख़ाली जगह, सस्ते Android पर भी smooth; v2 नए Architecture के लिए, अपने-आप नाप लेता है।
अच्छी list = virtualization/recycling + हल्के memoized cells + stable keys + सही आकार की images + pagination।

---

## 🔴 Problem it Solves
A Swiggy-style menu with 300 items, an Instagram-like feed with infinite scroll, or a WhatsApp chat with 5,000 messages:
- `ScrollView` with `.map()` renders everything: a **multi-second freeze** on open and **memory blowup**.
- A badly tuned `FlatList`:
  - **Blank white areas** when scrolling fast (the JS thread can't render new items in time).
  - **Dropped frames** from heavy cells (nested views, inline styles and closures, full-size images).
  - **Every cell re-renders** when any state changes (unstable `renderItem`, missing `memo`, wrong `extraData`).
- Mount/unmount churn on low-end Android (the majority of Indian users) is expensive, which FlashList's recycling avoids.
Lists are where users spend most of their time, so **scroll jank is the most visible performance problem** in apps.

## 🔴 यह क्यों बना? (Hindi)
300 items का menu, infinite feed या 5,000 messages वाली chat: ScrollView + `.map()` सब एक साथ render करे — खुलते ही कई सेकंड अटकना और memory भरना; ख़राब FlatList — तेज़ scroll पर सफ़ेद ख़ाली जगह (JS thread समय पर नहीं बना पाता), भारी cells से frames गिरना, किसी भी state बदलाव पर हर cell re-render।
सस्ते Android (भारत के ज़्यादातर यूज़र) पर बार-बार mount/unmount महँगा — FlashList की recycling इससे बचाती है। यूज़र सबसे ज़्यादा समय lists में बिताते हैं, इसलिए scroll का झटका सबसे ज़्यादा दिखता है।

---

## 🟢 How it Works — Step by Step

### FlatList virtualization vs FlashList recycling

```
FlatList (virtualize: mount/unmount)              FlashList (recycle: reuse mounted cells)
 viewport ┌─────────┐                               viewport ┌─────────┐
          │ item 20 │  ← mounted                             │ cell A  │ ← shows item 20
          │ item 21 │                                        │ cell B  │ ← item 21
          │ item 22 │                                        │ cell C  │ ← item 22
          └─────────┘                                        └─────────┘
 scroll ↓: item 15 UNMOUNTED (destroy tree),       scroll ↓: cell A moves to bottom and is RE-RENDERED
           item 30 MOUNTED (create whole tree)                with item 30's props (no new mount)
 Window = windowSize × viewport (default 21 =       Pool of cells by item TYPE (getItemType) →
 10 screens above + 10 below + current)             headers reuse header cells, products reuse product cells
 Costs: lots of component creation/GC on JS thread  Costs: cell must not keep stale local state (reset on new item)
```

### FlatList tuning knobs

```
keyExtractor          stable unique id (never index for dynamic lists)
getItemLayout         if fixed height → skip measurement, instant scrollToIndex
initialNumToRender    enough to fill first screen (e.g., 8) — not 50
maxToRenderPerBatch   items rendered per batch while scrolling (default 10)
windowSize            screens of content kept mounted (default 21 → reduce to 5–11 to save memory)
updateCellsBatchingPeriod  ms between batches
removeClippedSubviews (Android) detach offscreen native views — can help, test for bugs
onEndReached + onEndReachedThreshold (0.5)   pagination trigger
extraData             pass ONLY what affects rendering (e.g., selectedId), not whole state
```

### FlashList essentials

```
<FlashList data renderItem keyExtractor getItemType={(item) => item.kind} />
v1: estimatedItemSize required (approximate height) ; v2: automatic measurement, New Architecture only
Recycling rule: don't rely on useState inside cells for item-specific state without resetting on item
change (FlashList provides useRecyclingState / key off item.id); avoid `key` props inside cells that
change per item (forces remount, defeats recycling)
Masonry (Pinterest-style) layouts, horizontal lists, sticky headers supported
```

### Cell rendering rules (both lists)

```
1. Memoize cells: const Row = memo(RowImpl) with stable props (primitives / stable objects)
2. Stable renderItem: useCallback, no inline arrow creating new components each render
3. No inline style objects/functions inside hot cells → StyleSheet.create, pass ids not closures
4. Keep cells light: fewer nested Views, avoid heavy shadows on Android (use elevation sparingly),
   no expensive computations in render (precompute in selector/useMemo at list level)
5. Images: correctly sized CDN thumbnails + memory/disk cache + recyclingKey (M12)
6. No layout-changing animations in cells; avoid measuring in render
7. Heterogeneous lists: give each type its own component + getItemType (FlashList)
8. Horizontal carousels inside vertical lists: nested FlashList with fixed height, memoized
9. Pagination + avoid holding 10k items in React state unnecessarily (local DB + windowed queries)
10. Measure in RELEASE on low-end Android: Perf Monitor (JS fps & UI fps), Flashlight, React Profiler
```

### Chats: inverted lists & anchoring

```
<FlashList inverted /> (or maintainVisibleContentPosition) → newest at bottom, load older on reaching "end"
Keep scroll anchored when prepending older messages; auto-scroll only if user is near bottom
Group messages by day via sticky headers; ids as keys; optimistic messages with client ids
```

## 🟢 कैसे काम करता है? (Hindi)
1. FlatList: viewport के आसपास (windowSize, default 21 screens) items mount; scroll पर दूर वाले unmount और नए mount — JS thread पर बहुत बनाना-मिटाना।
2. FlashList: कुछ cells का pool; scroll पर ऊपर से निकला cell नीचे जाकर नए item के props के साथ फिर render (mount नहीं) — कम JS काम, सस्ते फ़ोन पर बहुत तेज़; अलग तरह के items के लिए `getItemType`।
3. FlatList tuning: stable `keyExtractor`, fixed height हो तो `getItemLayout`, `initialNumToRender` सिर्फ़ पहली screen जितना, `windowSize` 5–11, `extraData` में सिर्फ़ ज़रूरी चीज़।
4. Cells: `memo`, `useCallback` वाला renderItem, inline style/function नहीं, हल्के views, सही आकार की images + recyclingKey, cell के अंदर item-specific useState नहीं (recycling में पुराना state रह जाता है)।
5. Chat के लिए inverted list, पुराने messages ऊपर जोड़ते समय जगह स्थिर; नापो release build में सस्ते Android पर — Perf Monitor (JS fps और UI fps दोनों), Flashlight।

---

## 🟡 Real World Example

**Shopify (FlashList, 2022)** — built FlashList because FlatList struggled on low-end Android in their apps (Shop, Point of Sale). They reported large improvements in JS and UI thread FPS and far fewer blank cells, and open-sourced it. **FlashList v2** (2025) was rewritten for the New Architecture with automatic sizing.

**Swiggy / Zomato / Blinkit** — menus and category grids with hundreds of image cells and sticky category headers. They use heterogeneous item types (header, item, combo, banner) and recycled native lists so scrolling stays smooth on budget phones.

**WhatsApp / Telegram chats** — inverted, recycled lists with day separators, anchored scrolling when loading history, and lightweight message bubbles (no heavy nested layouts).

**Discord (React Native)** — invested in custom list rendering for chat because message lists were the primary performance bottleneck on Android.

## 🟡 Real Example Hindi में
Shopify ने 2022 में FlashList बनाया क्योंकि उनके ऐप में FlatList सस्ते Android पर धीमा था — JS और UI fps में बड़ा सुधार और कम ख़ाली cells बताए, फिर open-source किया; 2025 में v2 नए Architecture के लिए।
Swiggy/Zomato/Blinkit के menu में सैकड़ों image cells और sticky headers — अलग item types और recycling से सस्ते फ़ोन पर smooth; WhatsApp/Telegram की chat inverted recycled list है।

---

## 🟠 My Stack Example

### Menu with sections using FlashList (heterogeneous types, memoized cells)
```tsx
import { FlashList } from '@shopify/flash-list';

type Row = { kind: 'header'; id: string; title: string } | { kind: 'dish'; id: string; dish: Dish };

export function MenuList({ menu }: { menu: Menu }) {
  const rows = useMemo<Row[]>(() => menu.categories.flatMap((c) => [
    { kind: 'header', id: `h-${c.id}`, title: c.name },
    ...c.dishes.map((d) => ({ kind: 'dish' as const, id: d.id, dish: d })),
  ]), [menu]);
  const stickyIdx = useMemo(() => rows.flatMap((r, i) => (r.kind === 'header' ? [i] : [])), [rows]);

  const renderItem = useCallback(({ item }: { item: Row }) =>
    item.kind === 'header' ? <CategoryHeader title={item.title} /> : <DishRow dish={item.dish} />, []);

  return (
    <FlashList
      data={rows}
      renderItem={renderItem}
      keyExtractor={(r) => r.id}
      getItemType={(r) => r.kind}                 // separate recycle pools for headers and dishes
      stickyHeaderIndices={stickyIdx}
      // estimatedItemSize={96}                    // required in FlashList v1 only
    />
  );
}

const DishRow = memo(function DishRow({ dish }: { dish: Dish }) {
  const qty = useCart((s) => s.items[dish.id]?.qty ?? 0);      // selector → only this row re-renders on change
  const add = useCart((s) => s.add);
  return (
    <View style={styles.row}>
      <DishImage dish={dish} />                                  {/* M12: sized + recyclingKey */}
      <View style={styles.info}><Text style={styles.name}>{dish.name}</Text><Text>₹{dish.price / 100}</Text></View>
      <QtyButton qty={qty} onAdd={() => add(menuId, dish)} accessibilityLabel={`Add ${dish.name}`} />
    </View>
  );
});
const styles = StyleSheet.create({ row: { flexDirection: 'row', padding: 12, minHeight: 96 }, info: { flex: 1, marginLeft: 12 }, name: { fontWeight: '600' } });
```

### Avoid stale state in recycled cells
```tsx
// ❌ local expanded state "leaks" to the next item that reuses this cell
const [expanded, setExpanded] = useState(false);
// ✅ FlashList helper resets when the item changes (or lift state to parent keyed by id)
import { useRecyclingState } from '@shopify/flash-list';
const [expanded, setExpanded] = useRecyclingState(false, [dish.id]);
```

### Tuned FlatList (when you must use it)
```tsx
<FlatList
  data={orders}
  keyExtractor={(o) => o.id}
  renderItem={renderOrder}                 // useCallback
  getItemLayout={(_, i) => ({ length: 88, offset: 88 * i, index: i })}   // fixed height rows
  initialNumToRender={8}
  maxToRenderPerBatch={8}
  windowSize={7}
  removeClippedSubviews={Platform.OS === 'android'}
  onEndReached={loadMore}
  onEndReachedThreshold={0.5}
/>
```

### Chat: inverted list with older-message loading
```tsx
<FlashList
  data={messages}                          // newest first
  inverted
  renderItem={renderBubble}
  keyExtractor={(m) => m.clientId ?? m.id}
  getItemType={(m) => (m.type === 'image' ? 'image' : m.senderId === me ? 'mine' : 'theirs')}
  onEndReached={() => hasOlder && loadOlder()}   // "end" = top in inverted list
  maintainVisibleContentPosition={{ autoscrollToBottomThreshold: 0.2 }}  // FlashList v2: stay anchored
/>
```

### Measure
```
Dev menu → Perf Monitor: watch JS FPS & UI FPS while flinging the list (release build!)
npx flashlight test --bundleId in.quickbite.app --testCommand "maestro test scroll-menu.yaml"   # Android perf score
React DevTools Profiler → which cells re-render on cart change (should be just one)
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between FlatList and FlashList?**
A1: Both avoid rendering entire lists. FlatList virtualizes: it mounts items within a window around the viewport and unmounts those outside, which creates and destroys component trees on the JS thread while scrolling and can cause blank areas and GC pressure on slow devices. FlashList recycles: it keeps a pool of mounted cells per item type and reuses them by re-rendering with new item props, like RecyclerView and UICollectionView. That greatly reduces JS work and blank cells. Recycling requires care that cells don't retain stale local state, and v1 needs an estimated item size (v2 measures automatically).

**Q2: Your list shows blank areas while scrolling fast. Why, and how do you fix it?**
A2: The JS thread can't produce new items fast enough. Cells are too expensive to render, renders block the thread, or the virtualization window is too small. Fixes: switch to FlashList (recycling), memoize cells with stable props and renderItem, simplify cell layouts, size images properly and cache them, move heavy computation out of render, avoid re-rendering all rows on state changes (selectors, correct `extraData`), use `getItemLayout` for fixed sizes, tune batch and window sizes, and verify in release mode on a low-end device.

**Q3: How do you prevent all list rows from re-rendering when one item changes?**
A3: Keep item components memoized with `React.memo` and pass stable, primitive or referentially stable props. Have each row subscribe only to its own slice of state (Zustand or Redux selectors keyed by item ID) instead of passing the whole state through the list. Keep `renderItem` stable with `useCallback`. Pass only the minimal `extraData`. Avoid creating new objects or arrow functions per render for row props. The React Compiler can help automate memoization.

**Q4: How would you build a chat message list?**
A4: Use an inverted recycled list (FlashList) with newest messages first, client-generated IDs as keys for optimistic messages, and item types for bubble variants (mine, theirs, image, system). Load older messages when reaching the top via cursor pagination from the local DB, maintain the visible content position when prepending, auto-scroll to the bottom only if the user is already near it, use sticky day headers, keep bubbles lightweight, and use properly sized, cached media thumbnails.

**Q5: What are common mistakes with lists in React Native?**
A5: Rendering long lists with `ScrollView` and `map`. Using index as the key for dynamic data. Inline functions and styles in `renderItem` and cells. Unmemoized heavy cells. Passing the whole app state as `extraData`. Full-size images in thumbnails. Local state in recycled cells that leaks between items. Nested vertical scroll views. Huge `initialNumToRender`. Measuring performance only in debug mode or on high-end iPhones.

---

## 🔷 Trade-offs
✅ FlashList: best perf on low-end devices — ❌ recycling pitfalls (stale state), v2 requires New Architecture.
✅ FlatList: built-in, simple — ❌ more blank areas/jank on large lists and slow devices.
✅ Larger window/overscan: fewer blanks — ❌ more memory.
✅ getItemLayout/fixed sizes: fast — ❌ less flexible designs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualization | Render only near-viewport items | पास वाले items ही render |
| Recycling | Reuse mounted cells for new items | पुराने cells दोबारा इस्तेमाल |
| windowSize | Screens kept mounted (FlatList) | कितनी screens mounted |
| getItemLayout | Precomputed item size/offset | पहले से तय आकार |
| getItemType | Separate recycle pools by type | type के हिसाब से pool |
| Blank cells | Unrendered areas while scrolling | scroll में ख़ाली जगह |
| Memoization | Skip re-render if props same | props वही तो re-render नहीं |
| extraData | Extra input that triggers re-render | re-render का अतिरिक्त कारण |
| Inverted list | Bottom-anchored list (chat) | उल्टी list |
| JS/UI FPS | Frame rates of both threads | दोनों धागों के frames |

---

## ⚡ 3-Line Summary
**English:**
1. ScrollView renders all; FlatList virtualizes (mount/unmount); FlashList recycles cells by type — fastest on low-end Android.
2. Make cells cheap and stable: memo, stable renderItem/keys, selectors per row, StyleSheet, sized cached images, no stale state in recycled cells.
3. Tune and measure: getItemLayout/window/batch for FlatList, getItemType for FlashList, pagination, inverted lists for chat, test in release on low-end devices.

**Hindi:**
1. ScrollView सब render; FlatList virtualize; FlashList cells recycle करता है — सस्ते Android पर सबसे तेज़।
2. Cells हल्के और स्थिर: memo, stable keys, हर row का अपना selector, सही images, recycled cell में पुराना state नहीं।
3. Tune करो और नापो: getItemLayout, getItemType, pagination, chat के लिए inverted list, release में सस्ते फ़ोन पर जाँच।

---

## ➡️ Next Topic Suggestion
**M14. Mobile Performance (JS Thread vs UI Thread, Memory, Re-renders)** — Lists are one part of performance. Next: the complete picture of React Native performance: two threads, re-render control, animations, memory leaks, and profiling tools.
