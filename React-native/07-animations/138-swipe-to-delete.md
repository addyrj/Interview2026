# 138. Swipe to Delete
# हिंदी में: Swipe to Delete — खींचकर item हटाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-gesture-handler 2.x + react-native-reanimated 3.x (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
Swipe-to-delete lets the user drag a list row sideways to reveal or trigger a delete action. It is built with a Pan gesture (horizontal) + Reanimated: the row follows the finger, and if dragged past a threshold it slides out, collapses its height, then is removed from data.

## 🔵 सरल परिभाषा (Hindi)
Swipe-to-delete में user list की row को बगल में खींचकर delete action दिखाता या चलाता है। यह horizontal Pan gesture + Reanimated से बनता है: row उंगली के साथ चलती है, threshold से ज़्यादा खींचने पर बाहर खिसकती है, उसकी height सिकुड़ती है और फिर data से हटती है।

---

## 🔴 Problem it Solves
```
Mobile lists need fast actions without extra buttons (Gmail archive, WhatsApp, Swiggy cart remove).
Problems to solve:
  - Do not fight vertical list scrolling (only horizontal activation)
  - Smooth exit animation (slide out + collapse) BEFORE data removal
  - Undo possibility / confirmation for destructive actions
```

## 🔴 यह क्यों बना? (Hindi)
```
Mobile lists में बिना extra button के तेज़ actions चाहिए (Gmail archive, WhatsApp, Swiggy cart remove)।
हल करने वाली दिक्कतें:
  - vertical list scroll से न टकराए (सिर्फ horizontal में activate)
  - data हटने से PEHLE smooth exit animation (slide out + collapse)
  - destructive action के लिए undo / confirmation
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Row wrapped in GestureDetector with Pan: activeOffsetX([-10,10]), failOffsetY([-10,10])
Step 2 → onUpdate: translateX = clamp(e.translationX, -MAX, 0) (left swipe only)
Step 3 → onEnd: if translateX < -THRESHOLD (e.g. 35% width) -> delete, else spring back
Step 4 → Delete: translateX -> -screenWidth (withTiming), then height -> 0, opacity -> 0
Step 5 → When finished callback fires -> runOnJS(onRemove)(id) to update data
Step 6 → Red background with trash icon sits behind the row (absolute positioned)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Row को Pan वाले GestureDetector में लपेटो: activeOffsetX([-10,10]), failOffsetY([-10,10])
Step 2 → onUpdate: translateX = clamp(e.translationX, -MAX, 0) (सिर्फ बाएँ swipe)
Step 3 → onEnd: translateX < -THRESHOLD (जैसे चौड़ाई का 35%) हो तो delete, वरना spring से वापस
Step 4 → Delete: translateX -> -screenWidth (withTiming), फिर height -> 0, opacity -> 0
Step 5 → finished callback पर runOnJS(onRemove)(id) से data update
Step 6 → पीछे लाल background + trash icon (absolute) रहता है
```

---

## 🟡 Real World Example
**Swiggy cart & WhatsApp/Gmail:** in the Swiggy cart you can swipe a dish left to remove it, with a red strip behind. Gmail archives mail with swipe. Paytm's saved-bank-accounts list also uses swipe actions.

## 🟡 Real Example Hindi mein
**Swiggy cart और WhatsApp/Gmail:** Swiggy cart में dish को बाएँ swipe करके हटा सकते हैं, पीछे लाल पट्टी दिखती है। Gmail swipe से mail archive करता है। Paytm की saved bank accounts list में भी swipe actions होते हैं।

---

## 💻 Code Example — Basic

```jsx
import React, { useState } from 'react';                        // React + state
import { View, Text, FlatList, StyleSheet, useWindowDimensions } from 'react-native'; // core
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withTiming, runOnJS } from 'react-native-reanimated';

function Row({ item, onRemove }) {
  const { width } = useWindowDimensions();                       // screen width
  const x = useSharedValue(0);                                   // horizontal offset
  const startX = useSharedValue(0);                              // offset at drag start
  const THRESHOLD = -width * 0.35;                               // delete at 35% swipe

  const pan = Gesture.Pan()
    .activeOffsetX([-10, 10])                                    // activate after 10px horizontal move
    .failOffsetY([-10, 10])                                      // vertical move => let list scroll
    .onBegin(() => { startX.value = x.value; })                  // save start
    .onUpdate((e) => { x.value = Math.min(0, startX.value + e.translationX); }) // only left
    .onEnd(() => {
      if (x.value < THRESHOLD) {                                 // passed threshold
        x.value = withTiming(-width, { duration: 200 }, (finished) => { // slide out
          if (finished) runOnJS(onRemove)(item.id);              // remove data on JS thread
        });
      } else {
        x.value = withTiming(0);                                 // not enough: go back
      }
    });

  const rowStyle = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }] })); // move row

  return (
    <View style={styles.wrap}>
      <View style={styles.bg}><Text style={styles.bgText}>🗑 Delete</Text></View>
      <GestureDetector gesture={pan}>
        <Animated.View style={[styles.row, rowStyle]}><Text style={styles.name}>{item.name}</Text></Animated.View>
      </GestureDetector>
    </View>
  );
}

export default function SwipeBasic() {
  const [data, setData] = useState([
    { id: '1', name: 'Masala Dosa x1' }, { id: '2', name: 'Filter Coffee x2' }, { id: '3', name: 'Vada x3' },
  ]);
  const remove = (id) => setData((d) => d.filter((i) => i.id !== id)); // delete by id

  return (
    <GestureHandlerRootView style={{ flex: 1, paddingTop: 60 }}>
      <FlatList data={data} keyExtractor={(i) => i.id} renderItem={({ item }) => <Row item={item} onRemove={remove} />} />
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  wrap: { backgroundColor: '#d32f2f' },                          // red shows behind the row
  bg: { position: 'absolute', right: 20, top: 0, bottom: 0, justifyContent: 'center' },
  bgText: { color: '#fff', fontWeight: '700' },
  row: { backgroundColor: '#fff', padding: 20, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ccc' },
  name: { fontSize: 16 },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useState, useCallback, useRef } from 'react';   // React
import { View, Text, Pressable, FlatList, Platform, StyleSheet, useWindowDimensions, LayoutAnimation, UIManager } from 'react-native';
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, withSpring, runOnJS, interpolate, Extrapolation, LinearTransition,
} from 'react-native-reanimated';

// Android needs this flag only if you use core LayoutAnimation; we use Reanimated layout transition instead.
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);        // harmless, kept for completeness
}

const ROW_H = 72;                                               // fixed row height

function CartRow({ item, onRemove }) {
  const { width } = useWindowDimensions();
  const x = useSharedValue(0);
  const startX = useSharedValue(0);
  const h = useSharedValue(ROW_H);                              // row height (collapses on delete)
  const THRESHOLD = -width * 0.3;

  const finishDelete = (id) => onRemove(id);                    // JS side

  const pan = Gesture.Pan()
    .activeOffsetX([-12, 12])
    .failOffsetY([-12, 12])
    .onBegin(() => { startX.value = x.value; })
    .onUpdate((e) => { x.value = Math.min(0, startX.value + e.translationX); })
    .onEnd((e) => {
      const fling = e.velocityX < -800;                         // fast flick also deletes
      if (x.value < THRESHOLD || fling) {
        x.value = withTiming(-width, { duration: 180 });        // slide out
        h.value = withTiming(0, { duration: 220 }, (done) => {  // then collapse height
          if (done) runOnJS(finishDelete)(item.id);             // remove from list
        });
      } else {
        x.value = withSpring(0, { damping: 20 });               // snap back
      }
    });

  const rowStyle = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }] }));
  const wrapStyle = useAnimatedStyle(() => ({
    height: h.value,                                            // collapse
    opacity: interpolate(h.value, [0, ROW_H], [0, 1], Extrapolation.CLAMP),
  }));
  const iconStyle = useAnimatedStyle(() => ({                   // trash icon grows as you swipe
    transform: [{ scale: interpolate(x.value, [-120, -20], [1.2, 0.6], Extrapolation.CLAMP) }],
  }));

  return (
    <Animated.View style={[styles.wrap, wrapStyle]} layout={LinearTransition}>
      <Animated.View style={[styles.bg, iconStyle]}><Text style={styles.icon}>🗑</Text></Animated.View>
      <GestureDetector gesture={pan}>
        <Animated.View style={[styles.row, rowStyle]}>
          <Text style={styles.name}>{item.name}</Text>
          <Text style={styles.price}>₹{item.price}</Text>
        </Animated.View>
      </GestureDetector>
    </Animated.View>
  );
}

export default function Cart() {
  const [items, setItems] = useState([
    { id: 'a', name: 'Paneer Butter Masala', price: 280 },
    { id: 'b', name: 'Butter Naan', price: 60 },
    { id: 'c', name: 'Gulab Jamun', price: 90 },
  ]);
  const [last, setLast] = useState(null);                       // for UNDO
  const timer = useRef(null);
  const itemsRef = useRef(items);                               // latest items for callbacks
  itemsRef.current = items;                                     // keep in sync each render

  const remove = useCallback((id) => {
    const idx = itemsRef.current.findIndex((i) => i.id === id); // position for undo
    if (idx >= 0) setLast({ item: itemsRef.current[idx], idx });  // remember for undo
    setItems((prev) => prev.filter((i) => i.id !== id));        // pure updater, no side effects
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setLast(null), 4000);      // undo window 4s
  }, []);

  const undo = () => {
    if (!last) return;
    setItems((prev) => { const n = [...prev]; n.splice(last.idx, 0, last.item); return n; }); // restore
    setLast(null);
  };

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <FlatList
        data={items}
        keyExtractor={(i) => i.id}
        renderItem={({ item }) => <CartRow item={item} onRemove={remove} />}
        contentContainerStyle={{ paddingTop: Platform.OS === 'ios' ? 60 : 24 }}
      />
      {last && (
        <Pressable style={styles.snack} onPress={undo}>
          <Text style={{ color: '#fff' }}>Removed {last.item.name}. UNDO</Text>
        </Pressable>
      )}
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  wrap: { backgroundColor: '#d32f2f', overflow: 'hidden' },
  bg: { position: 'absolute', right: 24, top: 0, bottom: 0, justifyContent: 'center' },
  icon: { fontSize: 24 },
  row: { height: ROW_H, backgroundColor: '#fff', paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  name: { fontSize: 16 },
  price: { fontSize: 16, fontWeight: '700' },
  snack: { position: 'absolute', bottom: 32, left: 16, right: 16, padding: 14, backgroundColor: '#333', borderRadius: 8 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Feel | Often paired with Snackbar + UNDO (Material) | Trailing "Delete" red button (HIG) |
| System back gesture | Edge swipes can conflict (leave margin) | Left-edge back swipe conflicts for right swipes |
| Haptics | `Vibration` | Taptic via expo-haptics |
| Overflow clip | `overflow: hidden` ok | ok |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Gesture Handler ships a ready component: ReanimatedSwipeable
// import ReanimatedSwipeable from 'react-native-gesture-handler/ReanimatedSwipeable';  (RNGH 2.14+, check docs)
// npx expo install react-native-gesture-handler react-native-reanimated
```
CLI way:
```jsx
// Same code; npm i both libs, pod install, babel plugin, rebuild.
// Older RNGH: import Swipeable from 'react-native-gesture-handler/Swipeable' (deprecated in newer versions)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `failOffsetY`, so vertical list scrolling gets blocked or row moves while scrolling.
✅ Correct: `activeOffsetX` + `failOffsetY`.

❌ Mistake 2: Removing data immediately (row vanishes abruptly, other rows jump).
✅ Correct: animate out first, remove in the completion callback; use `layout={LinearTransition}`.

❌ Mistake 3: Using array index as key.
✅ Correct: stable unique id keys, otherwise wrong row animates after delete.

❌ Mistake 4: Deleting with no undo for important data.
✅ Correct: Snackbar UNDO or confirmation.

---

## 🧠 Tricky Interview Question
After the swipe animation finishes you call `setItems(filter)`. The row below briefly "jumps" up. Why, and how to fix?

Answer: Because the removed row still occupied its height until React removed it, then layout changed instantly. Collapse the row's height to 0 with animation before removal (or use `layout={LinearTransition}` / `exiting` animations) so neighbours slide smoothly.

---

## ⚫ Interview Questions + Answers
Q1: How to avoid conflict with FlatList scroll?
A1: Pan with `activeOffsetX([-10,10])` and `failOffsetY([-10,10])`.

Q2: What is velocity-based deletion?
A2: Check `e.velocityX` in onEnd; a fast flick deletes even if below threshold.

Q3: Which components are ready-made?
A3: RNGH `ReanimatedSwipeable` (new) / `Swipeable` (older, deprecated).

Q4: Why runOnJS for removal?
A4: Data lives in React state (JS thread); worklets run on UI thread.

Q5: Why must keys be stable?
A5: Otherwise React reuses the wrong component instance, and shared values (x, h) belong to the wrong item.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cart, inbox, notifications, saved addresses

❌ Avoid when:
- Action is dangerous with no undo
- Accessibility: also provide a button alternative (swipe is hidden)

---

## 📊 Visual Diagram
```
 ┌──────────────────────────────┐
 │ [row content]        ← drag  │   x = 0
 └──────────────────────────────┘
 ┌──────────────────────────────┐
 │ row content ◄━━  🗑 (red bg)  │   x < THRESHOLD
 └──────────────────────────────┘
   release → slide out → height 0 → remove(id)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| threshold | distance to trigger | trigger की दूरी |
| activeOffsetX | horizontal slop | horizontal activation दूरी |
| failOffsetY | vertical fail zone | vertical में fail होने की सीमा |
| LinearTransition | layout animation | layout बदलने की animation |
| UNDO | revert delete | delete वापस |

---

## ⚡ 3-Line Summary
English: Horizontal Pan moves the row; past threshold it slides out.
Collapse height, then remove data via runOnJS.
Add undo and an accessible button alternative.

Hindi: Horizontal Pan row को चलाता है; threshold पार होने पर row बाहर खिसकती है।
height सिकोड़ो, फिर runOnJS से data हटाओ।
undo और accessible button विकल्प भी दो।

---

## ➡️ Next Topic
**139. Lottie Animations** — designer की बनाई JSON animations चलाना।
