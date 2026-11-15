# 60. Dynamic Styling
# हिंदी में: Dynamic Styling — State/Props के हिसाब से Style बदलना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**Dynamic styling** means changing styles at runtime based on state, props, theme, screen size or platform. In React Native, `style` accepts an object or an **array** of objects, so you can combine a base style with conditional ones: `style={[styles.btn, active && styles.btnActive]}`.

## 🔵 सरल परिभाषा (Hindi)
**Dynamic styling** का मतलब runtime पर state, props, theme, screen size या platform के हिसाब से style बदलना। React Native में `style` एक object या **array** लेता है, इसलिए base style के साथ conditional style जोड़ सकते हैं: `style={[styles.btn, active && styles.btnActive]}`।

---

## 🔴 Problem it Solves
```
STATIC STYLES:
  Selected chip ka color alag? Dark mode? Error border red?
  Alag components banana = duplicate code

DYNAMIC:
  ✅ Ek component, kai states
  ✅ Theme (light/dark) automatic
  ✅ Screen size ke hisaab se size
  ✅ Press feedback (pressed state)
```

## 🔴 यह क्यों बना? (Hindi)
```
UI की state बदलती है: selected, disabled, error, dark mode।
हर state के लिए अलग component बनाना गलत है।
Style array + conditions से एक ही component सब state संभालता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Define base style in StyleSheet.create
Step 2 → Define variants (active, error, disabled) as separate keys
Step 3 → style={[base, cond && variant, inlineOverride]}
Step 4 → Later items in array OVERRIDE earlier ones
Step 5 → false/null/undefined in array are ignored
Step 6 → Theme: useColorScheme() → pick color palette
Step 7 → Size: useWindowDimensions() → re-renders on rotate
Step 8 → Pressable: style={({pressed}) => [...]}
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Base style StyleSheet में
Step 2 → Variants (active, error) अलग keys में
Step 3 → style={[base, condition && variant]}
Step 4 → Array में बाद वाला style पहले वाले को override करता है
Step 5 → false/null/undefined ignore हो जाते हैं
Step 6 → Dark mode: useColorScheme()
Step 7 → Screen size: useWindowDimensions()
```

---

## 🟡 Real World Example
**Zomato filter chips:** "Veg", "Rating 4.0+", "Fast Delivery". Tapping a chip turns its border red and background light red (selected). **Paytm** form: the input border turns red with an error message when the UPI ID is invalid. **Instagram** follows system dark mode — all colors swap based on theme.

## 🟡 Real Example Hindi mein
**Zomato filter chips:** "Veg", "Rating 4.0+" पर tap करो तो border लाल और background हल्का लाल (selected)। **Paytm** form में UPI ID गलत हो तो input का border लाल + error message। **Instagram** system dark mode follow करता है — theme के हिसाब से सारे colors बदलते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: selectable chips with conditional style
import React, { useState } from 'react'; // React + state
import { View, Text, Pressable, StyleSheet } from 'react-native'; // core

const FILTERS = ['Veg', 'Rating 4.0+', 'Fast Delivery']; // chip labels

export default function Chips() { // component
  const [selected, setSelected] = useState([]); // selected chip labels

  const toggle = (label) => { // toggle on tap
    setSelected((prev) => // functional update
      prev.includes(label) ? prev.filter((l) => l !== label) : [...prev, label] // remove or add
    );
  };

  return (
    <View style={styles.row}>{/* row of chips */}
      {FILTERS.map((label) => {
        const active = selected.includes(label); // is this chip selected?
        return (
          <Pressable
            key={label} // key for list
            onPress={() => toggle(label)} // tap handler
            style={[styles.chip, active && styles.chipActive]} // base + conditional
          >
            <Text style={[styles.text, active && styles.textActive]}>{label}</Text>{/* text style also changes */}
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, padding: 16 }, // wrap chips
  chip: { borderWidth: 1, borderColor: '#ccc', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6 }, // base chip
  chipActive: { borderColor: '#e23744', backgroundColor: '#fde8ea' }, // selected chip
  text: { color: '#333' }, // base text
  textActive: { color: '#e23744', fontWeight: '700' }, // selected text
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: theme hook + responsive width + validated input + pressed state
import React, { useMemo, useState } from 'react'; // hooks
import { View, Text, TextInput, Pressable, StyleSheet, useColorScheme, useWindowDimensions, Platform } from 'react-native'; // core

// Palettes for light/dark
const palettes = {
  light: { bg: '#ffffff', text: '#111111', border: '#cccccc', primary: '#e23744' }, // light colors
  dark: { bg: '#121212', text: '#f5f5f5', border: '#444444', primary: '#ff6b78' }, // dark colors
};

// Custom hook returns theme-aware styles; recomputed only when inputs change
function useStyles(hasError) {
  const scheme = useColorScheme(); // 'light' | 'dark' | null
  const { width } = useWindowDimensions(); // updates on rotation / split-screen
  const c = palettes[scheme === 'dark' ? 'dark' : 'light']; // pick palette (null → light)
  return useMemo(() => StyleSheet.create({ // build once per change
    screen: { flex: 1, backgroundColor: c.bg, padding: 16, alignItems: 'center' }, // page
    form: { width: width > 600 ? 480 : '100%' }, // tablet: fixed width, phone: full
    label: { color: c.text, marginBottom: 6 }, // label
    input: { borderWidth: 1, borderColor: hasError ? '#d32f2f' : c.border, color: c.text, borderRadius: 8, padding: Platform.OS === 'ios' ? 12 : 8 }, // error border
    error: { color: '#d32f2f', marginTop: 4 }, // error text
    btn: { backgroundColor: c.primary, padding: 14, borderRadius: 8, marginTop: 16, alignItems: 'center' }, // button
    btnText: { color: '#fff', fontWeight: '700' }, // button text
  }), [c, width, hasError]); // dependencies
}

export default function UpiForm() {
  const [upi, setUpi] = useState(''); // input value
  const [touched, setTouched] = useState(false); // validate after blur
  const hasError = touched && !/^[\w.\-]{2,}@[a-zA-Z]{2,}$/.test(upi); // simple UPI regex
  const s = useStyles(hasError); // dynamic styles

  return (
    <View style={s.screen}>
      <View style={s.form}>
        <Text style={s.label}>UPI ID</Text>
        <TextInput
          value={upi} // controlled
          onChangeText={setUpi} // update
          onBlur={() => setTouched(true)} // mark touched
          autoCapitalize="none" // UPI ids are lowercase
          style={s.input} // dynamic border
          placeholder="name@bank"
          placeholderTextColor="#888"
        />
        {hasError && <Text style={s.error}>Invalid UPI ID</Text>}{/* conditional message */}
        <Pressable style={({ pressed }) => [s.btn, pressed && { opacity: 0.7 }]}>{/* pressed state */}
          <Text style={s.btnText}>Pay</Text>
        </Pressable>
      </View>
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Style arrays | Same | Same |
| `useColorScheme` | Works (needs `userInterfaceStyle` set in Expo config) | Works (needs `userInterfaceStyle`) |
| Pressed feedback | `android_ripple` | opacity via `pressed` |
| TextInput padding | Has default vertical padding | None by default → set manually |
| Font scale | System font scale applies; use `allowFontScaling` | Dynamic Type applies |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json: allow automatic dark mode (default is "light" in older templates)
// { "expo": { "userInterfaceStyle": "automatic" } }
// Without it useColorScheme() may always return 'light' on a built app
import { useColorScheme } from 'react-native'; // same hook
const scheme = useColorScheme(); // read theme
```
CLI way:
```jsx
// Bare CLI: iOS Info.plist UIUserInterfaceStyle (remove "Light" to follow system)
// Android: Theme.AppCompat.DayNight in styles.xml + MainActivity handles uiMode configChanges
import { useColorScheme } from 'react-native'; // same hook
const scheme = useColorScheme(); // read theme
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating inline objects everywhere: `style={{...}}` in big lists.
✅ Correct: Use `StyleSheet.create` for static parts, inline only for truly dynamic values.

❌ Mistake 2: `style={active ? styles.a : styles.b}` duplicating the base.
✅ Correct: `style={[styles.base, active && styles.a]}`.

❌ Mistake 3: Putting a string/number `0` in the array: `{count && <X/>}` renders `0`.
✅ Correct: `count > 0 && ...`.

❌ Mistake 4: Dark mode does not work in the built app.
✅ Correct: Set `"userInterfaceStyle": "automatic"` in app.json.

---

## 🧠 Tricky Interview Question
**Q:** `style={[{color:'red'}, {color:'blue'}]}` — what color is the text?

**Answer:** Blue. Arrays are flattened left to right; later styles override earlier ones. Falsy entries (`false`, `null`, `undefined`) are skipped.

---

## ⚫ Interview Questions + Answers
Q1: How to apply conditional styles?
A1: Style array with `&&` or ternary: `[styles.a, cond && styles.b]`.

Q2: How to detect dark mode?
A2: `useColorScheme()` from react-native (returns `'light'`, `'dark'` or null) or `Appearance.addChangeListener`.

Q3: Difference between `Dimensions.get` and `useWindowDimensions`?
A3: `Dimensions.get` is a one-time snapshot; `useWindowDimensions` re-renders when size changes (rotation, foldables).

Q4: Is inline style slow?
A4: Small cost (new object each render). Fine for few dynamic values; keep static styles in `StyleSheet.create`.

Q5: How to style a pressed button?
A5: `Pressable` `style` accepts a function `({ pressed }) => style`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Selected/disabled/error states, theming, responsive sizes

❌ Avoid when:
- Style never changes (use plain StyleSheet)
- Heavy computation inside style building on every render (use `useMemo`)

---

## 📊 Visual Diagram
```
 state/props/theme/size
        │
        ▼
 style = [ base , cond && variant , override ]
        │ flatten (right wins)
        ▼
 final style object ──► native view
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Style array | Multiple styles merged | Style array |
| Conditional style | Style based on condition | शर्त वाला style |
| useColorScheme | Hook for light/dark | Theme hook |
| useWindowDimensions | Reactive screen size | Screen size hook |
| Variant | Named style version | Style का प्रकार |

---

## ⚡ 3-Line Summary
English: `style` accepts arrays, so combine base and conditional styles.
Use `useColorScheme` and `useWindowDimensions` for theme and size.
Use `useMemo` for expensive style creation.

Hindi: `style` array लेता है, इसलिए base और conditional styles जोड़ो।
Theme और size के लिए `useColorScheme` और `useWindowDimensions` use करो।
भारी style बनाने पर `useMemo` use करो।

---

## ➡️ Next Topic
**61. Styled Components in React Native** — CSS-in-JS tareeke se styles likhna aur props se dynamic banana.
