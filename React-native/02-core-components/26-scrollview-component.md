# 26. ScrollView Component
# हिंदी में: ScrollView Component क्या है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
`ScrollView` is a generic scrollable container — it renders ALL its children at once (even if off-screen) and makes them scrollable. Use it for short to medium content: settings screens, checkout forms, product details, terms & conditions. **Not suitable for long lists** (100+ items) because all items are rendered and kept in memory — use `FlatList` instead.

## 🔵 सरल परिभाषा (Hindi)
`ScrollView` एक generic scrollable container है — यह अपने सभी children एक साथ render करता है (चाहे off-screen हों) और उन्हें scrollable बनाता है। Short to medium content के लिए: settings screens, checkout forms, product details, terms & conditions। **Long lists (100+ items) के लिए suitable नहीं** क्योंकि सभी items memory में रहते हैं — उसके लिए `FlatList` use करो।

---

## 🔴 Problem it Solves
```
PROBLEM: Content taller than screen
  A checkout form with 15 fields:
  ┌─────────────────┐  ← screen top
  │ Name field      │
  │ Address line 1  │
  │ Address line 2  │
  │ City            │
  │ State           │  ← screen bottom (some fields cut off!)
  │ [PIN field]     │  ← not visible!
  │ [Phone]         │  ← not visible!
  └─────────────────┘

  WITHOUT ScrollView: content beyond screen = invisible, inaccessible!
  WITH ScrollView: user can scroll down to access all content ✅

SCROLLVIEW vs FLATLIST:
  ScrollView: renders ALL children immediately
    ✅ Good for < 30 items or screens (forms, settings, details)
    ❌ BAD for 50+ items (all in memory = slow, janky)

  FlatList: renders only VISIBLE items (virtualization)
    ✅ Good for any list size (100s, 1000s of items)
    ✅ Lazy rendering = low memory
    ❌ More complex API (keyExtractor, renderItem required)
```

## 🔴 यह क्यों बना? (Hindi)
```
Screen से बड़ा content दिखाना = ScrollView।
Form, settings, product details → ScrollView।
Long lists → FlatList (ScrollView में 100+ items = memory problem)।
```

---

## 🟢 How it Works — Step by Step

```
SCROLLVIEW RENDERING:
──────────────────────────────────────────────────────
  Step 1 → ScrollView renders ALL children
           (even those off-screen)

  Step 2 → Creates a scroll container (UIScrollView / ScrollView)
           with content height = total children height

  Step 3 → User scrolls → native scroll event fires
           Content moves within the container

  Step 4 → onScroll fires with scroll position data
           { contentOffset: { x, y }, contentSize, layoutMeasurement }

  Step 5 → onMomentumScrollEnd fires when scroll animation ends

SCROLL DIRECTION:
  Vertical (default):   flex-direction: column (default)
  Horizontal:           horizontal={true} prop

KEYBOARD DISMISS:
  keyboardDismissMode="on-drag" → keyboard dismisses as you scroll
  keyboardShouldPersistTaps="handled" → taps don't dismiss keyboard
```

## 🟢 कैसे काम करता है? (Hindi)
```
सभी children एक साथ render → scroll container में।
User scroll → native scroll event → onScroll callback।
All content memory में = fast scroll but high memory usage।
```

---

## 🟡 Real World Example
**Swiggy Restaurant Detail Screen:** Menu categories (not a FlatList — relatively few items), photos gallery, reviews, info section — all in one ScrollView. When user scrolls, the restaurant header sticks to top (`stickyHeaderIndices`). The "Add to Cart" button at the bottom stays fixed outside the ScrollView. This is typical of product/detail screens — structured content, not an infinite list.

## 🟡 Real Example Hindi मे
**Swiggy Restaurant Detail:** Menu categories, photos, reviews, info — एक ScrollView में। Scroll करने पर restaurant header sticky रहता है (`stickyHeaderIndices`)। "Add to Cart" button ScrollView के बाहर fixed — typical detail screen pattern।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';
import {
  ScrollView,
  View,
  Text,
  StyleSheet,
  Platform,
} from 'react-native';

// Vertical ScrollView — Settings screen
function SettingsScreen() {
  return (
    <ScrollView
      style={styles.container}              // outer container style
      contentContainerStyle={styles.content} // inner content style
      showsVerticalScrollIndicator={false}   // hide scrollbar
      bounces={true}                         // iOS: rubber band bounce
    >
      {/* All content rendered at once */}
      <SettingSection title="Account" />
      <SettingSection title="Notifications" />
      <SettingSection title="Privacy" />
      <SettingSection title="Payments" />
      <SettingSection title="About" />
      <SettingSection title="Help" />
    </ScrollView>
  );
}

// Horizontal ScrollView — category pills (like Zomato filter chips)
function CategoryFilter({ categories }) {
  return (
    <ScrollView
      horizontal                              // horizontal scroll!
      showsHorizontalScrollIndicator={false}  // hide horizontal scrollbar
      contentContainerStyle={styles.filterContainer}
    >
      {categories.map((cat) => (
        <View key={cat.id} style={styles.chip}>
          <Text style={styles.chipText}>{cat.name}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9f9f9' },
  content: {
    padding: 16,
    paddingBottom: 40,   // extra bottom padding so last item isn't right at edge
  },
  filterContainer: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  chip: {
    backgroundColor: '#fff',
    borderWidth: 1, borderColor: '#ddd',
    borderRadius: 20,
    paddingHorizontal: 16, paddingVertical: 8,
  },
  chipText: { fontSize: 14, color: '#333' },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useRef } from 'react';
import {
  ScrollView,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
} from 'react-native';

// ADVANCED: ScrollView with sticky header + scroll-to-section
function RestaurantMenu({ sections }) {
  const scrollRef = useRef(null);        // ref to ScrollView
  const sectionRefs = useRef({});        // refs to each section header

  // Scroll to a specific section programmatically
  const scrollToSection = (sectionId) => {
    // measure the section position then scroll to it
    sectionRefs.current[sectionId]?.measure((x, y, width, height, pageX, pageY) => {
      scrollRef.current?.scrollTo({
        y: pageY,           // scroll to section Y position
        animated: true,     // smooth scroll
      });
    });
  };

  return (
    <View style={styles.container}>

      {/* Category tabs — fixed at top */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.tabs}
        contentContainerStyle={styles.tabsContent}
      >
        {sections.map((section) => (
          <TouchableOpacity
            key={section.id}
            onPress={() => scrollToSection(section.id)}
            style={styles.tab}
          >
            <Text style={styles.tabText}>{section.title}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Main content scroll */}
      <ScrollView
        ref={scrollRef}                    // ref for programmatic scroll
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        scrollEventThrottle={16}           // fire onScroll every 16ms (60fps)
        onScroll={({ nativeEvent }) => {
          // detect which section is at top → update active tab
          const scrollY = nativeEvent.contentOffset.y;
          console.log('Scroll Y:', scrollY);
        }}
        keyboardDismissMode="on-drag"      // keyboard dismisses on scroll
        keyboardShouldPersistTaps="handled" // tap on button in scroll = handled
        stickyHeaderIndices={[0]}          // first child sticks to top!
      >
        {/* This header will stick when scrolled past */}
        <View style={styles.stickyHeader}>
          <Text style={styles.stickyTitle}>Menu</Text>
        </View>

        {sections.map((section) => (
          <View
            key={section.id}
            ref={(ref) => { sectionRefs.current[section.id] = ref; }}
          >
            <Text style={styles.sectionTitle}>{section.title}</Text>
            {section.items.map((item) => (
              <MenuItem key={item.id} item={item} />
            ))}
          </View>
        ))}
      </ScrollView>

    </View>
  );
}

// Scroll to top button (appears after scrolling down)
function ScrollTopButton({ scrollRef }) {
  return (
    <TouchableOpacity
      style={styles.scrollTopBtn}
      onPress={() => scrollRef.current?.scrollTo({ y: 0, animated: true })}
    >
      <Text style={styles.scrollTopText}>↑ Top</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  tabs: { backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#eee' },
  tabsContent: { paddingHorizontal: 16, paddingVertical: 12, gap: 8 },
  tab: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, backgroundColor: '#f5f5f5' },
  tabText: { fontSize: 14, fontWeight: '500' },
  scroll: { flex: 1 },
  scrollContent: { paddingBottom: 80 },
  stickyHeader: { backgroundColor: '#fff', padding: 16, borderBottomWidth: 1, borderBottomColor: '#eee' },
  stickyTitle: { fontSize: 18, fontWeight: '700' },
  sectionTitle: { fontSize: 16, fontWeight: '600', padding: 16, backgroundColor: '#f9f9f9' },
  scrollTopBtn: {
    position: 'absolute', right: 16, bottom: 80,
    backgroundColor: '#f97316', borderRadius: 20,
    paddingHorizontal: 16, paddingVertical: 8,
  },
  scrollTopText: { color: '#fff', fontWeight: '600' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Bounce (rubber band) | ❌ no bounce | ✅ natural bounce |
| `bounces` prop | ignored | controls bounce |
| Momentum scroll | ✅ | ✅ |
| Overscroll | Glow effect | Bounce |
| `scrollIndicatorInsets` | not applicable | controls scrollbar position |
| Nested ScrollView | Works but complex | Works but complex |

---

## 🟠 Expo vs CLI Difference

Expo way:
```jsx
// Same ScrollView from react-native
import { ScrollView } from 'react-native';

// Expo also has: @gorhom/bottom-sheet, react-native-reanimated
// for animated scroll-driven behaviors
```

CLI way:
```jsx
// Same ScrollView
import { ScrollView } from 'react-native';

// For better scroll performance in complex screens:
// react-native-gesture-handler's ScrollView (drop-in replacement)
import { ScrollView } from 'react-native-gesture-handler';
// Handles nested scroll gestures better
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using ScrollView for long lists
```jsx
// WRONG: 100 restaurant cards in a ScrollView
<ScrollView>
  {restaurants.map(r => <RestaurantCard key={r.id} item={r} />)}
  {/* ❌ All 100 rendered immediately → slow, high memory */}
</ScrollView>

// CORRECT: Use FlatList for lists
<FlatList
  data={restaurants}
  renderItem={({ item }) => <RestaurantCard item={item} />}
  keyExtractor={item => item.id}
  // ✅ Only visible items rendered
/>
```

❌ **Mistake 2:** ScrollView with flex: 1 child won't scroll
```jsx
// WRONG: Child with flex:1 takes all space → ScrollView can't scroll
<ScrollView>
  <View style={{ flex: 1 }}>  {/* ❌ This takes all available space */}
    <Text>Content</Text>
  </View>
</ScrollView>

// CORRECT: Don't use flex:1 in direct ScrollView children
<ScrollView contentContainerStyle={{ flexGrow: 1 }}>
  <View>
    <Text>Content that will scroll</Text>
  </View>
</ScrollView>
```

❌ **Mistake 3:** Forgetting `scrollEventThrottle` for onScroll
```jsx
// WRONG: onScroll fires on every native frame (60fps = 60 calls/second!)
<ScrollView onScroll={(e) => { /* expensive operation */ }}>

// CORRECT: throttle to a reasonable rate
<ScrollView
  scrollEventThrottle={16}    // fire every ~16ms (60fps max)
  onScroll={(e) => {
    // runs at most 60 times/second
    const y = e.nativeEvent.contentOffset.y;
  }}
>
```

---

## 🧠 Tricky Interview Question

**Q: Why does `<ScrollView style={{ flex: 1 }}>` work but `<ScrollView contentContainerStyle={{ flex: 1 }}>` causes issues?**

**Answer:** `style` on ScrollView applies to the **outer container** (the scroll viewport). `flex: 1` on the outer container correctly makes the viewport take up available space — this is what you want. `contentContainerStyle` applies to the **inner content wrapper** (the scrollable content). Setting `flex: 1` there tells the content to fill the container — but if content fills the container, there's nothing to scroll! The scroll only works when content is LARGER than the container. Use `contentContainerStyle={{ flexGrow: 1 }}` instead — it expands to fill if content is small, but still allows growing beyond if content is large. Common use case: a screen that should scroll if content is too tall but center content if it's small.

---

## ⚫ Interview Questions + Answers

**Q1: When should you use ScrollView vs FlatList?**
A1: `ScrollView`: renders ALL children immediately. Use for static or small content: settings screens (10-20 items), checkout forms, product detail pages, terms & conditions, onboarding screens. Threshold: typically < 30-50 items. `FlatList`: virtualizes — renders only visible items. Use for any dynamic list that could grow: feed, search results, order history, contacts. Even 50 items in ScrollView can feel heavy on low-end Android phones; FlatList handles 10,000+ items efficiently.

**Q2: What is `contentContainerStyle` vs `style` on ScrollView?**
A2: `style` — applies to the outer scroll container (the viewport). Controls: the overall size and position of the scrollable area. `contentContainerStyle` — applies to the inner content wrapper. Controls: padding around the content, alignment of children, flexGrow. Common pattern: `style={{ flex: 1 }}` (viewport takes full space) + `contentContainerStyle={{ paddingBottom: 80 }}` (add bottom padding so last item isn't at the very edge).

**Q3: How do you scroll to a specific position programmatically?**
A3: Use a ref: `const scrollRef = useRef(null)`. Attach: `<ScrollView ref={scrollRef}>`. Then call: `scrollRef.current?.scrollTo({ x: 0, y: 500, animated: true })` to scroll to Y=500. Or `scrollRef.current?.scrollToEnd({ animated: true })` for bottom. For scrolling to a specific child element: use the child's `ref.measure()` callback to get Y position, then `scrollRef.current?.scrollTo({ y: childY })`. Common use case: form validation — scroll to first error field.

**Q4: What is `stickyHeaderIndices` in ScrollView?**
A4: `stickyHeaderIndices` is an array of child indices whose children "stick" to the top of the ScrollView as you scroll past them. Example: `stickyHeaderIndices={[0, 3, 7]}` — children at index 0, 3, and 7 will stick. As you scroll, when a sticky header would go off-screen, it "sticks" to the top. When the next sticky header reaches the top, it pushes the previous one away. Used in menu screens (Zomato/Swiggy) to show category headers that stick as you scroll through that category's items.

**Q5: How do you dismiss the keyboard when user scrolls?**
A5: Use `keyboardDismissMode` prop. Options: `'none'` (default — keyboard stays open), `'on-drag'` — keyboard dismisses as soon as user starts scrolling, `'interactive'` (iOS only) — keyboard moves with the scroll gesture, dismissed when scroll is fast enough. Also: `keyboardShouldPersistTaps="handled"` — taps on interactive elements (buttons, links) inside the ScrollView work without first dismissing the keyboard.

---

## 🔷 When to Use + When Not to Use
✅ **Use ScrollView when:**
- Detail/profile screens (structured content, not a list)
- Forms with multiple fields
- Settings screens
- Onboarding steps
- < 30 children total

❌ **Don't use ScrollView when:**
- Dynamic list that can have many items (use FlatList)
- Social feed, search results, order history (use FlatList)
- Infinite scroll content (definitely FlatList)

---

## 📊 Visual Diagram

```
SCROLLVIEW vs FLATLIST — RENDERING:
──────────────────────────────────────────────────────
  ScrollView:
  ┌─────────────────────────────────┐  ← viewport (visible)
  │ Item 1 (rendered) ◄─ visible   │
  │ Item 2 (rendered) ◄─ visible   │
  └─────────────────────────────────┘
    Item 3 (rendered) ← off-screen but IN MEMORY
    Item 4 (rendered) ← off-screen but IN MEMORY
    Item 5 (rendered) ← off-screen but IN MEMORY
    ...all 100 items in memory!

  FlatList:
  ┌─────────────────────────────────┐  ← viewport (visible)
  │ Item 3 (rendered) ◄─ visible   │
  │ Item 4 (rendered) ◄─ visible   │
  │ Item 5 (rendered) ◄─ visible   │
  └─────────────────────────────────┘
    Item 1 (REMOVED from memory)    ← recycled!
    Item 2 (REMOVED from memory)    ← recycled!
    Items 6-100 (NOT YET CREATED)   ← pending!
    Only ~5-10 items in memory at once!

SCROLLVIEW STRUCTURE:
──────────────────────────────────────────────────────
  <ScrollView style={outerStyle}
              contentContainerStyle={innerStyle}>
    ┌──────────────────────────────────────────────┐ ← outer (viewport)
    │  ┌────────────────────────────────────────┐  │ ← inner (content)
    │  │  Child 1                               │  │
    │  │  Child 2                               │  │
    │  │  Child 3                               │  │
    │  └────────────────────────────────────────┘  │
    └──────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ScrollView | Scrollable container (renders all) | सब children render करे |
| contentContainerStyle | Inner content wrapper style | Inner content की style |
| stickyHeaderIndices | Indices that stick to top | Scroll पर top पर stick होने वाले indices |
| scrollEventThrottle | How often onScroll fires | onScroll कितनी बार fire करे |
| keyboardDismissMode | When keyboard dismisses on scroll | Scroll पर keyboard कब dismiss हो |
| horizontal | Enable horizontal scroll | Horizontal scroll enable करो |
| bounces | iOS rubber band bounce effect | iOS rubber band bounce |
| scrollRef | Ref for programmatic scroll | Programmatic scroll के लिए ref |

---

## ⚡ 3-Line Summary
**English:**
1. `ScrollView` renders all children at once — perfect for detail screens, forms, and settings; use `FlatList` for lists with more than ~30 items.
2. Key props: `horizontal` for horizontal scroll, `stickyHeaderIndices` for sticky headers, `contentContainerStyle` for inner content padding, `scrollEventThrottle` for performance.
3. Always add `keyboardDismissMode="on-drag"` when the screen has TextInput, and `paddingBottom` in `contentContainerStyle` so last item is accessible.

**Hindi:**
1. `ScrollView` सभी children एक साथ render करता है — detail screens, forms, settings के लिए perfect; 30+ items वाले lists के लिए `FlatList` use करो।
2. Key props: horizontal scroll, sticky headers, inner content padding, scroll throttle।
3. TextInput वाले screens पर `keyboardDismissMode="on-drag"` और last item दिखाने के लिए `contentContainerStyle` में `paddingBottom` जरूर add करो।

---

## ➡️ Next Topic
**27. FlatList Component** — virtualized lists, keyExtractor, renderItem, performance optimization।
