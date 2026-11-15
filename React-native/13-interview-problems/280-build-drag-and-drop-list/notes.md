# 280. Interview Problem: Build a Drag and Drop (Reorderable) List
# हिंदी में: Drag and Drop List बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐⭐ Hard | Asked at: Swiggy, Notion-like apps, PhonePe, Dream11

Files: `DragDropList.jsx` (UI), `reorder.js` (pure logic), `App.jsx` (demo).
Target: Expo SDK 54 / React Native 0.81 (check current docs — APIs change between SDKs). Core RN only; fixed row height.

---

## 🔵 Simple Definition (English)
A list where the user holds a handle and drags a row up or down. When released, the row is dropped at the new position and the data array is reordered.

## 🔵 सरल परिभाषा (Hindi)
ऐसी list जिसमें user handle को पकड़कर row को ऊपर-नीचे खींचता है। छोड़ने पर row नई जगह पर बैठ जाती है और data array का order बदल जाता है।

---

## 🔴 Problem it Solves
Users want to set their own order (favourite dishes, playlist, checklist priorities). "Move up / move down" buttons are slow. Dragging is natural.

## 🔴 यह क्यों बना? (Hindi)
Users अपना order खुद तय करना चाहते हैं (favourite dishes, playlist, priority)। "ऊपर/नीचे" buttons धीमे हैं। Drag करना natural है।

---

## 🔴 Problem Statement
Render rows with a drag handle. Dragging the handle moves the row with the finger. On release compute the target index from the distance moved and reorder the array immutably. Lock the parent scroll while dragging. Keep the logic testable.

## 💡 Approach
```
reorder.js (PURE):
  targetIndex(start, dy, rowH, length) = clamp(start + round(dy / rowH), 0, length-1)
  moveItem(list, from, to) -> NEW array (splice out, splice in)

DragDropList.jsx:
  Row: Animated.Value dy + PanResponder on the HANDLE
  grant   -> active=true, ScrollView scrollEnabled=false
  move    -> dy follows finger
  release -> to = targetIndex(...), reset dy, onMoveEnd(index, to)
  key = `${id}-${index}` so a Row (and its PanResponder closure) is rebuilt after each reorder
```

## 🟢 How it Works — Step by Step
```
Step 1 → User touches the ≡ handle -> row becomes active (highlight, zIndex 10)
Step 2 → Parent ScrollView is disabled so the list does not scroll
Step 3 → Row translateY = finger dy (Animated.event, JS driver)
Step 4 → Release -> shift = round(dy / 56) rows -> clamp to list
Step 5 → dy reset to 0 and moveItem returns a new array -> list re-renders in new order
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → User ≡ handle छूता है -> row active (highlight, zIndex 10)
Step 2 → Parent ScrollView बंद ताकि list scroll न हो
Step 3 → Row का translateY = उंगली का dy
Step 4 → छोड़ने पर shift = round(dy / 56) rows -> list की सीमा में clamp
Step 5 → dy वापस 0, moveItem नया array देता है -> list नए order में दिखती है
```

---

## 🟡 Real World Example
Swiggy / Zomato "Reorder your favourite addresses", Google Keep checklist, Spotify playlist reorder, Paytm "Rearrange shortcuts" on the home screen, Dream11 team batting order.

## 🟡 Real Example Hindi mein
Swiggy / Zomato में favourite addresses reorder करना, Google Keep की checklist, Spotify playlist reorder, Paytm home screen पर shortcuts की जगह बदलना, Dream11 में batting order।

---

## 💻 Code Example — Basic
Pure logic first (`reorder.js`) — always explain this part in the interview:
```js
// Move item from `from` to `to`, return a NEW array
export function moveItem(list, from, to) {
  if (from === to || from < 0 || to < 0 || from >= list.length || to >= list.length) return list; // no-op
  const copy = list.slice();                                     // never mutate state
  const [item] = copy.splice(from, 1);                           // remove dragged item
  copy.splice(to, 0, item);                                      // insert at new place
  return copy;
}
// moveItem(['a','b','c','d'], 0, 2) -> ['b','c','a','d']
```

## 💻 Code Example — Advanced
From `DragDropList.jsx`:
```jsx
const ROW_H = 56;                                                // fixed row height

function Row({ item, index, count, onMoveEnd, onDragState }) {
  const dy = useRef(new Animated.Value(0)).current;              // drag offset
  const [active, setActive] = useState(false);                   // highlight

  const pan = useRef(PanResponder.create({
    onStartShouldSetPanResponder: () => true,                    // handle claims touch
    onPanResponderGrant: () => { setActive(true); onDragState(true); },  // lock parent scroll
    onPanResponderMove: Animated.event([null, { dy }], { useNativeDriver: false }),
    onPanResponderRelease: (_, g) => {
      const to = targetIndex(index, g.dy, ROW_H, count);         // drop position
      setActive(false); onDragState(false); dy.setValue(0);      // reset + unlock
      onMoveEnd(index, to);                                      // reorder in parent
    },
    onPanResponderTerminate: () => { setActive(false); onDragState(false);
      Animated.spring(dy, { toValue: 0, useNativeDriver: false }).start(); },
  })).current;
  ...
}

// parent: key includes index so each Row's PanResponder closure sees the fresh index
<ScrollView scrollEnabled={!dragging}>
  {items.map((item, i) => <Row key={`${item.id}-${i}`} item={item} index={i} count={items.length} ... />)}
</ScrollView>
```
Limits of this simple version: rows have fixed height, other rows do not slide out of the way while dragging, and long lists need virtualization. For production use `react-native-draggable-flatlist` or Reanimated + Gesture Handler.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Dragged-row shadow | `elevation` (also controls z-order) | `shadow*` props, use `zIndex` |
| Haptic on pick-up | `expo-haptics` impact | Same API, stronger feedback |
| Edge gestures | Gesture-nav may conflict at screen edge | Swipe-back near left edge |
| Overscroll | Glow / stretch effect | Bounce |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core-RN version: no install.
// Library: npx expo install react-native-reanimated react-native-gesture-handler
// npm i react-native-draggable-flatlist
```
CLI way:
```jsx
// npm i react-native-reanimated react-native-gesture-handler react-native-draggable-flatlist
// babel plugin 'react-native-reanimated/plugin' LAST, cd ios && pod install
// Wrap root in <GestureHandlerRootView style={{ flex: 1 }}>
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mutating the array (`list.splice(...)` on state).
✅ Correct: Copy first (`slice`) and return a new array.

❌ Mistake 2: Leaving the parent ScrollView enabled, so the list scrolls while dragging.
✅ Correct: `scrollEnabled={!dragging}`.

❌ Mistake 3: Reading a stale `index` inside `PanResponder.create` (created once).
✅ Correct: Rebuild via `key` (as here), keep index in a ref, or use Reanimated shared values.

❌ Mistake 4: Using the array index as the only key.
✅ Correct: Use a stable id (here id + index on purpose to refresh the responder).

---

## 🧠 Tricky Interview Question
A row is dragged 100px down with row height 56px, starting at index 1 in a 4-item list. Where does it land? What if the drag is 500px?

Answer: `round(100/56) = 2` -> index 3 (the last). 500px -> `round(8.9) = 9` -> 10 -> clamped to 3. The clamp stops the row from leaving the list.

---

## ⚫ Interview Questions + Answers
Q1: Why keep reorder logic outside the component?
A1: It is pure, so it is unit-testable and reusable (also for keyboard / a11y "move up").

Q2: How do you show a placeholder gap while dragging?
A2: Track the live target index (`onMove`) and offset other rows by +/- ROW_H with `Animated` or `LayoutAnimation`.

Q3: Variable row heights?
A3: Measure each row with `onLayout`, store cumulative offsets, find the target index by comparing the drop Y with offsets.

Q4: How to persist the order?
A4: Save array of ids (AsyncStorage locally, API call on `onMoveEnd`) — optimistic update, revert on failure.

Q5: Accessibility?
A5: Add "Move up / Move down" `accessibilityActions` since drag gestures are hard for screen readers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- User-defined ordering (playlist, priorities, favourites)

❌ Avoid when:
- Order is determined by data (date, price) - use sort
- Thousands of rows with this simple ScrollView version

---

## 📊 Visual Diagram
```
 Before                 Drag handle of "Butter Chicken" down 2 rows
 ┌───────────────┐
 │ Butter Chicken ≡│  ← finger dy = +112px  =>  round(112/56) = 2
 │ Masala Dosa   ≡│
 │ Pav Bhaji     ≡│
 │ Chole Bhature ≡│
 └───────────────┘
 After  moveItem(list, 0, 2) -> Masala Dosa, Pav Bhaji, Butter Chicken, Chole Bhature
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Drag handle | Part that starts dragging | पकड़ने वाला हिस्सा |
| Immutable update | Return new array | नया array बनाना |
| Clamp | Limit inside range | सीमा में रखना |
| zIndex | Stacking order | ऊपर-नीचे परत |
| Touch target | Tappable area (>=44-48px) | छूने का क्षेत्र |

---

## ⚡ 3-Line Summary
English: A handle with PanResponder moves a row; on release `targetIndex` converts distance to an index.
`moveItem` returns a new array, so React re-renders in the new order.
Lock parent scroll during drag; use libraries for big lists.

Hindi: Handle पर PanResponder row को चलाता है; छोड़ने पर `targetIndex` दूरी को index में बदलता है।
`moveItem` नया array देता है इसलिए React नए order में render करता है।
Drag के दौरान parent scroll बंद रखें; बड़ी lists के लिए library लें।

---

## ✅ What was verified
react-native-web + jsdom: list and handles render. `moveItem` (forward, backward, no-op, no mutation) and `targetIndex` (incl. clamping) run and pass. Real drag gestures were not run (no device).

---

## ➡️ Next Topic
281. Build Pull to Refresh — another gesture-driven list pattern, but with the built-in `RefreshControl`.
