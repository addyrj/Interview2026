# 38. Modal Component
# हिंदी में: Modal — Overlay Screen
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Modal** is a React Native built-in component that renders content in an overlay on top of the current screen — a full-screen or partial overlay that blocks interaction with the content behind it. Use it for: confirmation dialogs, filter sheets, image galleries, custom bottom sheets, alerts. Unlike navigation (new screen), Modal appears on top of the existing screen without leaving it.

## 🔵 सरल परिभाषा (Hindi)
**Modal** React Native का built-in component है जो current screen के ऊपर overlay में content render करता है। Content behind block हो जाता है। Use: confirmation dialogs, filter sheets, image galleries, custom bottom sheets, alerts। Navigation (new screen) के unlike, Modal existing screen के ऊपर आता है — screen नहीं बदलती।

---

## 🔴 Problem it Solves
```
USE CASES FOR MODAL:
  ✅ "Are you sure you want to delete?" → Confirmation dialog
  ✅ Filter/sort options → Bottom sheet
  ✅ Image viewer → Full screen overlay
  ✅ Address picker → Sheet from bottom
  ✅ Alert with custom design → Custom dialog
  ✅ OTP entry → Center modal

WITHOUT MODAL:
  Navigate to a new screen = back button in header = not dialog-like
  Context menus look wrong in a full stack screen
  No way to show content "above" current screen without navigation
```

---

## 💻 Code Example — Basic

```tsx
import React, { useState } from 'react';
import {
  Modal,
  View,
  Text,
  Pressable,
  StyleSheet,
  Alert,
} from 'react-native';

export default function DeleteConfirmModal() {
  const [modalVisible, setModalVisible] = useState(false);

  const handleDelete = () => {
    setModalVisible(false);
    Alert.alert('Deleted!');
  };

  return (
    <View style={styles.container}>
      <Pressable
        style={styles.deleteButton}
        onPress={() => setModalVisible(true)}
      >
        <Text style={styles.deleteText}>Delete Item</Text>
      </Pressable>

      <Modal
        visible={modalVisible}                  // show/hide
        transparent={true}                      // background shows through
        animationType="fade"                    // 'none' | 'slide' | 'fade'
        onRequestClose={() => setModalVisible(false)}  // Android back button
        statusBarTranslucent={true}             // Android: modal covers status bar
      >
        {/* Semi-transparent backdrop */}
        <Pressable
          style={styles.backdrop}
          onPress={() => setModalVisible(false)}  // tap outside to dismiss
        >
          {/* Stop tap propagation to backdrop */}
          <Pressable style={styles.dialog}>
            <Text style={styles.title}>Delete Item?</Text>
            <Text style={styles.message}>
              This action cannot be undone. The item will be permanently deleted.
            </Text>
            <View style={styles.buttons}>
              <Pressable
                style={[styles.btn, styles.cancelBtn]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelText}>Cancel</Text>
              </Pressable>
              <Pressable
                style={[styles.btn, styles.deleteBtn]}
                onPress={handleDelete}
              >
                <Text style={styles.deleteConfirmText}>Delete</Text>
              </Pressable>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  deleteButton: { backgroundColor: '#e23744', padding: 16, borderRadius: 8 },
  deleteText: { color: 'white', fontWeight: '600' },

  // Modal styles
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',   // semi-transparent black
    justifyContent: 'center',
    alignItems: 'center',
  },
  dialog: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 24,
    width: '80%',
    maxWidth: 360,
  },
  title: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
  message: { fontSize: 14, color: '#666', marginBottom: 24, lineHeight: 20 },
  buttons: { flexDirection: 'row', gap: 12 },
  btn: { flex: 1, padding: 14, borderRadius: 8, alignItems: 'center' },
  cancelBtn: { backgroundColor: '#f5f5f5' },
  deleteBtn: { backgroundColor: '#e23744' },
  cancelText: { fontWeight: '600', color: '#333' },
  deleteConfirmText: { fontWeight: '600', color: 'white' },
});
```

## 💻 Code Example — Advanced (Bottom Sheet Modal)

```tsx
import React, { useState, useRef, useEffect } from 'react';
import {
  Modal,
  View,
  Text,
  Pressable,
  StyleSheet,
  Animated,
  Dimensions,
  ScrollView,
} from 'react-native';

const { height: SCREEN_HEIGHT } = Dimensions.get('window');
const SHEET_HEIGHT = SCREEN_HEIGHT * 0.6;  // 60% of screen height

type SortOption = {
  id: string;
  label: string;
  value: string;
};

const SORT_OPTIONS: SortOption[] = [
  { id: '1', label: 'Relevance', value: 'relevance' },
  { id: '2', label: 'Price: Low to High', value: 'price_asc' },
  { id: '3', label: 'Price: High to Low', value: 'price_desc' },
  { id: '4', label: 'Rating', value: 'rating' },
  { id: '5', label: 'Delivery Time', value: 'delivery_time' },
];

export default function SortBottomSheet({
  visible,
  onClose,
  onSelect,
  currentSort,
}: {
  visible: boolean;
  onClose: () => void;
  onSelect: (value: string) => void;
  currentSort: string;
}) {
  const slideAnim = useRef(new Animated.Value(SHEET_HEIGHT)).current;

  useEffect(() => {
    if (visible) {
      // Slide up when opening
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        bounciness: 0,
      }).start();
    } else {
      // Slide down when closing
      Animated.timing(slideAnim, {
        toValue: SHEET_HEIGHT,
        duration: 250,
        useNativeDriver: true,
      }).start();
    }
  }, [visible]);

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="none"       // we handle animation ourselves
      onRequestClose={onClose}
      statusBarTranslucent={true}
    >
      {/* Backdrop */}
      <Pressable style={styles.backdrop} onPress={onClose}>
        {/* Sheet — stop press propagation */}
        <Pressable>
          <Animated.View
            style={[
              styles.sheet,
              { transform: [{ translateY: slideAnim }] },
            ]}
          >
            {/* Handle bar */}
            <View style={styles.handle} />

            <Text style={styles.sheetTitle}>Sort By</Text>

            <ScrollView>
              {SORT_OPTIONS.map(option => (
                <Pressable
                  key={option.id}
                  style={styles.optionRow}
                  onPress={() => {
                    onSelect(option.value);
                    onClose();
                  }}
                >
                  <Text style={styles.optionLabel}>{option.label}</Text>
                  {/* Checkmark for selected option */}
                  {currentSort === option.value && (
                    <Text style={styles.checkmark}>✓</Text>
                  )}
                </Pressable>
              ))}
            </ScrollView>

            <Pressable style={styles.closeButton} onPress={onClose}>
              <Text style={styles.closeText}>Close</Text>
            </Pressable>
          </Animated.View>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',   // sheet at bottom
  },
  sheet: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    height: SHEET_HEIGHT,
    paddingBottom: 32,
  },
  handle: {
    width: 40,
    height: 4,
    backgroundColor: '#ddd',
    borderRadius: 2,
    alignSelf: 'center',
    marginTop: 12,
    marginBottom: 8,
  },
  sheetTitle: {
    fontSize: 16,
    fontWeight: '700',
    textAlign: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  optionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f9f9f9',
  },
  optionLabel: { fontSize: 15, color: '#333' },
  checkmark: { fontSize: 18, color: '#e23744', fontWeight: '700' },
  closeButton: {
    margin: 16,
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    alignItems: 'center',
  },
  closeText: { fontWeight: '600', color: '#333' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `animationType="slide"` | Slides up from bottom | Slides up from bottom |
| Back button | Triggers `onRequestClose` | No hardware back button |
| `statusBarTranslucent` | Needed for full-screen modal | Not needed |
| Native sheet (iOS 15+) | Not available natively | `presentation="formSheet"` in Stack |

---

## 🟠 Expo vs CLI Difference

Both use the same built-in `Modal` from `react-native` — no difference.

For better bottom sheets, both can use:
```bash
npx expo install @gorhom/bottom-sheet  # most popular library
# Needs: react-native-reanimated + react-native-gesture-handler
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `onRequestClose` (Android back button)
```tsx
// WRONG: Android back button does nothing — modal can't be dismissed
<Modal visible={true} transparent>...</Modal>

// CORRECT: Always handle Android back button
<Modal
  visible={true}
  transparent
  onRequestClose={() => setVisible(false)}  // required on Android!
/>
```

❌ **Mistake 2:** Using `animationType="slide"` on transparent Modal
```tsx
// WRONG: Default slide makes entire overlay slide up (looks wrong for dialog)
<Modal visible={true} transparent={true} animationType="slide">

// CORRECT: For center dialogs, use 'fade'. For bottom sheets: 'none' + custom animation
<Modal visible={true} transparent={true} animationType="fade">
```

---

## ⚫ Interview Questions + Answers

**Q1: When should you use Modal vs navigating to a new screen?**
A1: Modal when: content is temporary/contextual (confirm delete, filter options, image preview), shouldn't have its own URL/back-button entry, needs to float above current screen. Navigate when: content is a meaningful app destination (product detail, user profile), needs full screen, should be accessible via deep link, or has its own navigation history. Rule: Modal = "overlay on current context"; Screen = "new destination."

**Q2: What is `transparent` prop in Modal?**
A2: `transparent={true}` makes the Modal's container View have a transparent background — you can see the screen behind. Without it, Modal has a white background covering everything. With it, you can set a semi-transparent backdrop (`backgroundColor: 'rgba(0,0,0,0.5)'`) to create the classic darkened overlay effect. Most modals need `transparent={true}`.

**Q3: How do you make a bottom sheet with Modal?**
A3: Set `transparent={true}`, `animationType="none"` (custom animation), outer view `justifyContent: 'flex-end'` (pushes content to bottom), inner view with `borderTopLeftRadius + borderTopRightRadius`. For the slide animation, use `Animated.Value` + `useEffect` watching `visible` prop. For production: use `@gorhom/bottom-sheet` which provides drag-to-dismiss, snap points, and smooth JSI-based animation.

---

## ⚡ 3-Line Summary
**English:**
1. Modal renders content as an overlay on top of the current screen — use for dialogs, bottom sheets, image viewers; use navigation for full destination screens.
2. Always set `onRequestClose` (Android back button handler), `transparent={true}` for custom backgrounds, and `statusBarTranslucent={true}` on Android for full-screen modals.
3. For production bottom sheets: `@gorhom/bottom-sheet` (Reanimated-based, drag-to-dismiss, snap points) is better than a custom Modal implementation.

**Hindi:**
1. Modal current screen के ऊपर overlay render — dialogs, bottom sheets, image viewers के लिए use। Full destination screens के लिए navigation।
2. हमेशा `onRequestClose` (Android back), `transparent={true}`, Android full-screen modal के लिए `statusBarTranslucent={true}`।
3. Production bottom sheets: `@gorhom/bottom-sheet` (Reanimated-based, drag-to-dismiss) बेहतर है custom Modal से।

---

## ➡️ Next Topic
**39. ActivityIndicator** — Loading spinner component।
