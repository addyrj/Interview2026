# 42. KeyboardAvoidingView
# हिंदी में: KeyboardAvoidingView — Keyboard से Content Hide न हो
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**KeyboardAvoidingView** automatically adjusts its height or padding when the keyboard appears, preventing the keyboard from covering `TextInput` fields or buttons. Without it, the keyboard slides up and hides whatever is at the bottom of the screen — common issue on login screens, comment forms, and chat interfaces.

## 🔵 सरल परिभाषा (Hindi)
**KeyboardAvoidingView** keyboard appear होने पर automatically अपनी height या padding adjust करता है — keyboard नीचे के content को hide न करे। इसके बिना: keyboard slide up → bottom पर जो भी है (TextInput, button) वो hide। Login screens, comment forms, chat interfaces पर common problem।

---

## 🔴 Problem it Solves
```
PROBLEM: Keyboard covers content
  Login screen:
  ┌────────────────────┐
  │   App Logo         │
  │   Email Input      │
  │   Password Input   │
  │   [Login Button]   │  ← Button at bottom
  └────────────────────┘
  User taps Email → Keyboard appears:
  ┌────────────────────┐
  │   App Logo         │
  │   Email Input      │    ← User can't see what they're typing!
  │   ████████████████ │  ← KEYBOARD covers Password + Button!
  │   ████████████████ │
  └────────────────────┘

  With KeyboardAvoidingView:
  ┌────────────────────┐
  │   Email Input      │  ← Scrolled up to be visible
  │   Password Input   │
  │   [Login Button]   │  ← Button still visible above keyboard!
  │   ████████████████ │
  │   ████████████████ │
  └────────────────────┘
```

---

## 💻 Code Example — Basic

```tsx
import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  ScrollView,
  TextInput,
  Pressable,
  Text,
  StyleSheet,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        // iOS: 'padding' — adds padding to push content up
        // Android: 'height' — shrinks the view height
        // Note: Android often handles this with windowSoftInputMode in AndroidManifest
        keyboardVerticalOffset={0}  // offset from top (useful with headers)
      >
        <ScrollView
          contentContainerStyle={styles.container}
          keyboardShouldPersistTaps="handled"  // tap outside dismisses keyboard
        >
          <Text style={styles.title}>Welcome Back</Text>

          <TextInput
            style={styles.input}
            placeholder="Email"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            placeholder="Password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <Pressable style={styles.button}>
            <Text style={styles.buttonText}>Login</Text>
          </Pressable>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 24,
  },
  title: { fontSize: 28, fontWeight: '700', marginBottom: 32 },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#e23744',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: { color: 'white', fontSize: 16, fontWeight: '700' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | iOS | Android |
|---------|-----|---------|
| Best `behavior` | `'padding'` | `'height'` |
| AndroidManifest alternative | N/A | `windowSoftInputMode="adjustResize"` in AndroidManifest.xml automatically pushes content up — many devs use this instead of KAV on Android |
| Header offset | `keyboardVerticalOffset={header_height}` | Usually not needed |

**Android tip:** Add to `AndroidManifest.xml`:
```xml
<activity android:windowSoftInputMode="adjustResize">
```
This often handles keyboard avoidance automatically on Android without needing `KeyboardAvoidingView` at all.

---

## 🟠 Expo vs CLI Difference
Both use the same built-in `KeyboardAvoidingView`. No library needed.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Same `behavior` for both platforms
```tsx
// WRONG: 'padding' on Android often causes a double-shift effect
<KeyboardAvoidingView behavior="padding">

// CORRECT: Platform-specific behavior
<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
/>
```

❌ **Mistake 2:** Forgetting `flex: 1` on KeyboardAvoidingView
```tsx
// WRONG: No flex — KAV doesn't fill screen, content gets cut
<KeyboardAvoidingView behavior="padding">

// CORRECT:
<KeyboardAvoidingView style={{ flex: 1 }} behavior="padding">
```

❌ **Mistake 3:** Nesting inside another view with `flex: 1` issues
```tsx
// Common: KAV inside SafeAreaView
// CORRECT pattern:
<SafeAreaView style={{ flex: 1 }}>
  <KeyboardAvoidingView style={{ flex: 1 }} behavior="padding">
    <ScrollView>...</ScrollView>
  </KeyboardAvoidingView>
</SafeAreaView>
```

---

## ⚫ Interview Questions + Answers

**Q1: What is KeyboardAvoidingView and when is it needed?**
A1: A component that adjusts its height/padding when the soft keyboard appears, preventing inputs and buttons from being obscured. Needed on: login/signup screens, comment/reply forms, chat message input bars, any form with inputs near the bottom of the screen. On Android, `windowSoftInputMode="adjustResize"` in AndroidManifest.xml often handles it automatically, making KAV optional there.

**Q2: What's the difference between `behavior="padding"` and `behavior="height"`?**
A2: `padding`: Adds bottom padding to push content up — best for iOS. Content stays same size, just shifts up. `height`: Reduces the view's height so content above the keyboard fits — better for Android. `position`: Uses absolute positioning to shift up. In practice: `Platform.OS === 'ios' ? 'padding' : 'height'` is the standard pattern.

**Q3: What is `keyboardVerticalOffset`?**
A3: An offset (in pixels) added to the keyboard height for calculation. Use when your KAV is inside a component with a header — set it to the header's height so the calculation is correct. Example: `keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}` for a screen with a 90px header.

---

## ⚡ 3-Line Summary
**English:**
1. KeyboardAvoidingView prevents the soft keyboard from covering TextInput fields and buttons — wrap your form content with it.
2. Always use `behavior={Platform.OS === 'ios' ? 'padding' : 'height'}` — iOS and Android behave differently.
3. Android alternative: add `windowSoftInputMode="adjustResize"` to the activity in AndroidManifest.xml — often works without any KAV code.

**Hindi:**
1. KeyboardAvoidingView soft keyboard को TextInput और buttons hide करने से रोकता है।
2. हमेशा `behavior={Platform.OS === 'ios' ? 'padding' : 'height'}` — iOS और Android अलग।
3. Android alternative: AndroidManifest में `windowSoftInputMode="adjustResize"` — अक्सर KAV के बिना काम करता है।

---

## ➡️ Next Topic
**43. RefreshControl** — Pull-to-refresh for ScrollView and FlatList।
