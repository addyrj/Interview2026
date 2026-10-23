# 25. TextInput Component
# हिंदी में: TextInput Component क्या है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
`TextInput` is React Native's equivalent of HTML's `<input>` and `<textarea>`. It's the only built-in component for user text input — phone number fields, search bars, passwords, OTP boxes, chat messages, forms. Key difference from web: keyboard management is critical on mobile — you must handle keyboard showing/hiding, focus, and the soft keyboard covering your input.

## 🔵 सरल परिभाषा (Hindi)
`TextInput` React Native का HTML `<input>` और `<textarea>` equivalent है। User text input के लिए एकमात्र built-in component — phone numbers, search, passwords, OTP, chat, forms सब इससे। Web से key difference: mobile पर keyboard management critical है — keyboard show/hide, focus, और soft keyboard input cover करना सब handle करना पड़ता है।

---

## 🔴 Problem it Solves
```
WEB vs RN INPUT:
Web:
  <input type="text" onChange={e => setValue(e.target.value)} />
  → Browser handles keyboard, focus, input events

React Native:
  <TextInput onChangeText={text => setValue(text)} />
  → You handle: keyboard type, return key, focus, dismissal
  → CRITICAL: KeyboardAvoidingView needed to prevent keyboard
    from covering your input fields!

COMMON MOBILE INPUT CHALLENGES:
❌ Keyboard covers input at bottom of screen
❌ Need to dismiss keyboard when tapping outside
❌ Different keyboard types (numeric, email, phone, OTP)
❌ Platform differences (Android back=dismiss, iOS no back)
❌ ref.focus() to programmatically move cursor between fields (OTP!)
```

## 🔴 यह क्यों बना? (Hindi)
```
Mobile पर text input web से complex है:
- Soft keyboard screen space लेती है
- Different keyboard types (number, email, phone)
- OTP fields, form navigation, focus management
- Android vs iOS keyboard behavior अलग
TextInput इन सब को handle करने का tool है।
```

---

## 🟢 How it Works — Step by Step

```
CONTROLLED INPUT (React pattern):
──────────────────────────────────────────────────────
  Step 1 → User taps TextInput
           Native keyboard appears
           Component receives focus

  Step 2 → User types character
           onChangeText fires with new string
           (NOT onchange event with target.value!)

  Step 3 → State updates: setValue(newText)
           React re-renders with new value

  Step 4 → value prop keeps TextInput in sync with state

  Step 5 → User presses Return/Done/Submit
           onSubmitEditing fires
           Can: move focus to next field, submit form, dismiss keyboard

KEYBOARD TYPES:
──────────────────────────────────────────────────────
  'default'         → normal keyboard
  'numeric'         → numbers only (0-9, .)
  'number-pad'      → numbers only, no decimal
  'decimal-pad'     → numbers + decimal
  'phone-pad'       → phone number style
  'email-address'   → with @ and . keys visible
  'url'             → with / and .com keys
  'visible-password'→ shows typed characters
```

## 🟢 कैसे काम करता है? (Hindi)
```
User tap → keyboard appear → onChangeText fire → state update → re-render
onSubmitEditing: next field focus करो या keyboard dismiss करो
keyboardType: किस type का keyboard चाहिए वो specify करो
```

---

## 🟡 Real World Example
**PhonePe UPI Payment Flow:** Step 1: Phone number field (`keyboardType="phone-pad"`, max 10 chars). Step 2: OTP fields (4 separate TextInputs, auto-jump on fill via `ref.focus()`). Step 3: UPI PIN (`secureTextEntry`, `keyboardType="number-pad"`, max 6 chars). Step 4: Amount field (`keyboardType="numeric"`, `returnKeyType="done"`). Each field has specific keyboard type and focus management for smooth UX.

## 🟡 Real Example Hindi मे
**PhonePe Payment:** Phone field (`phone-pad`), OTP fields (4 TextInputs, auto-focus next via ref), UPI PIN (`secureTextEntry`, `number-pad`), Amount (`numeric`). हर field का अलग keyboard type और focus management = smooth UX।

---

## 💻 Code Example — Basic

```jsx
import React, { useState } from 'react';
import {
  View,
  TextInput,
  Text,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';

function LoginForm() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  return (
    // KeyboardAvoidingView: prevents keyboard from covering inputs
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <Text style={styles.title}>Login</Text>

      {/* Phone number input */}
      <TextInput
        style={styles.input}
        placeholder="Phone Number"
        placeholderTextColor="#999"          // placeholder text color
        value={phone}
        onChangeText={setPhone}              // NOT onChange! — direct string
        keyboardType="phone-pad"            // numeric phone keyboard
        maxLength={10}                       // India: 10 digit numbers
        returnKeyType="next"                // shows "Next" on keyboard
      />

      {/* Password input */}
      <TextInput
        style={styles.input}
        placeholder="Password"
        placeholderTextColor="#999"
        value={password}
        onChangeText={setPassword}
        secureTextEntry                     // hides password characters
        returnKeyType="done"               // shows "Done" on keyboard
        onSubmitEditing={() => {
          // Keyboard "Done" pressed → submit form
          console.log('Submitting:', { phone, password });
        }}
      />

      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Login</Text>
      </TouchableOpacity>

    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: '700', marginBottom: 24 },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    marginBottom: 16,
    backgroundColor: '#fafafa',
    color: '#333',                          // text color!
  },
  button: {
    backgroundColor: '#f97316',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useRef, useState } from 'react';
import {
  View, TextInput, Text, StyleSheet, Keyboard
} from 'react-native';

// OTP INPUT — 4 separate boxes, auto-jump on fill
// (Zomato, PhonePe, Swiggy all use this pattern)
function OTPInput({ length = 4, onComplete }) {
  const [otp, setOtp] = useState(Array(length).fill(''));

  // Create refs for each input box
  const inputRefs = useRef(Array(length).fill(null).map(() => React.createRef()));

  const handleChange = (text, index) => {
    // Allow only single digit
    const digit = text.replace(/[^0-9]/g, '').slice(-1);

    // Update OTP array
    const newOtp = [...otp];
    newOtp[index] = digit;
    setOtp(newOtp);

    if (digit) {
      // Auto-move to next box when digit entered
      if (index < length - 1) {
        inputRefs.current[index + 1].current.focus();
      } else {
        // Last box filled — dismiss keyboard, notify parent
        Keyboard.dismiss();
        onComplete(newOtp.join(''));
      }
    }
  };

  const handleKeyPress = ({ nativeEvent: { key } }, index) => {
    // Handle backspace — move to previous box
    if (key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1].current.focus();
    }
  };

  return (
    <View style={styles.otpContainer}>
      {otp.map((digit, index) => (
        <TextInput
          key={index}
          ref={inputRefs.current[index]}      // ref for programmatic focus
          style={[
            styles.otpBox,
            digit ? styles.otpBoxFilled : null,
          ]}
          value={digit}
          onChangeText={(text) => handleChange(text, index)}
          onKeyPress={(e) => handleKeyPress(e, index)}
          keyboardType="number-pad"           // numeric only
          maxLength={1}                        // single digit per box
          selectTextOnFocus                   // select on focus (easy correction)
          textAlign="center"                  // center the digit in box
        />
      ))}
    </View>
  );
}

// SEARCH INPUT with clear button and debounce
function SearchInput({ onSearch }) {
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);

  const handleClear = () => {
    setQuery('');
    inputRef.current?.focus();   // optional chaining — focus back
    onSearch('');
  };

  return (
    <View style={styles.searchContainer}>
      <TextInput
        ref={inputRef}
        style={styles.searchInput}
        placeholder="Search restaurants, dishes..."
        placeholderTextColor="#999"
        value={query}
        onChangeText={(text) => {
          setQuery(text);
          onSearch(text);        // debounce this in production!
        }}
        returnKeyType="search"
        clearButtonMode="while-editing"  // iOS: X button in input
        autoCapitalize="none"
        autoCorrect={false}
      />
      {/* Android clear button (clearButtonMode only works on iOS) */}
      {query.length > 0 && (
        <TouchableOpacity onPress={handleClear} style={styles.clearBtn}>
          <Text style={styles.clearText}>✕</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  otpContainer: { flexDirection: 'row', gap: 12, justifyContent: 'center' },
  otpBox: {
    width: 56, height: 56,
    borderWidth: 1.5, borderColor: '#ddd',
    borderRadius: 8, fontSize: 24, fontWeight: '700',
    backgroundColor: '#fafafa', color: '#333',
  },
  otpBoxFilled: { borderColor: '#f97316', backgroundColor: '#fff7ed' },
  searchContainer: {
    flexDirection: 'row', alignItems: 'center',
    borderWidth: 1, borderColor: '#ddd', borderRadius: 24,
    paddingHorizontal: 16, margin: 16,
    backgroundColor: '#f5f5f5',
  },
  searchInput: { flex: 1, paddingVertical: 12, fontSize: 16, color: '#333' },
  clearBtn: { padding: 4 },
  clearText: { color: '#999', fontSize: 16 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| clearButtonMode | ❌ not supported | ✅ shows X in input |
| Keyboard dismiss | Back button | Dismiss programmatically |
| underlineColorAndroid | ✅ (remove with transparent) | ❌ not applicable |
| returnKeyType 'send' | Shows "Send" | Shows "Send" |
| autoCorrect | ✅ | ✅ |
| secureTextEntry eye | Some keyboards have it | Not built-in |

---

## 🟠 Expo vs CLI Difference

Expo way:
```jsx
// Expo uses the same TextInput from react-native
// No extra setup needed
import { TextInput } from 'react-native';
// Expo also has @expo/vector-icons for search icons to pair with TextInput
```

CLI way:
```jsx
// Same TextInput from react-native
import { TextInput } from 'react-native';
// For advanced inputs: react-native-paper's TextInput (Material UI style)
// npm install react-native-paper
import { TextInput } from 'react-native-paper';
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `onChange` instead of `onChangeText`
```jsx
// WRONG: onChange gives synthetic event (like web), hard to use
<TextInput onChange={(e) => setValue(e.nativeEvent.text)} />

// CORRECT: onChangeText gives the text string directly
<TextInput onChangeText={(text) => setValue(text)} />
// Or shorthand:
<TextInput onChangeText={setValue} />
```

❌ **Mistake 2:** Not handling Android's underline
```jsx
// Android TextInput has a bottom underline by default
// WRONG: Just style without removing Android underline
<TextInput style={styles.input} />

// CORRECT: Remove underline on Android
<TextInput
  style={styles.input}
  underlineColorAndroid="transparent"  // removes Android underline!
/>
// OR set borderBottomWidth: 0 in the style
```

❌ **Mistake 3:** Not wrapping forms in KeyboardAvoidingView
```jsx
// WRONG: Keyboard covers inputs at bottom of screen
<View style={styles.container}>
  <TextInput style={styles.input} />
  <Button title="Submit" />   // covered by keyboard!
</View>

// CORRECT: KeyboardAvoidingView pushes content up
import { KeyboardAvoidingView, Platform } from 'react-native';
<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={styles.container}
>
  <TextInput style={styles.input} />
  <Button title="Submit" />   // ✅ visible above keyboard
</KeyboardAvoidingView>
```

---

## 🧠 Tricky Interview Question

**Q: In an OTP input with 4 boxes, the user pastes their full OTP from SMS. How do you handle paste?**

**Answer:** When user pastes "1234" into the first box, `onChangeText` fires with "1234" (all 4 chars). The standard `maxLength={1}` + `onChangeText` approach only takes the first character. To handle paste: (1) Remove `maxLength={1}`, catch `onChangeText` when text length > 1, distribute characters across boxes: `text.split('').forEach((char, i) => { if (index + i < length) { newOtp[index + i] = char; } })`, then move focus to the last filled box or the first empty box. (2) Alternative: use `onChangeText` on the first box only, treating it as a single hidden input that drives all 4 visible boxes (invisible actual input approach — more complex but handles paste natively).

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `onChange` and `onChangeText` in TextInput?**
A1: `onChange` receives the full event object `{ nativeEvent: { text, target, eventCount } }` — similar to web's synthetic event. `onChangeText` receives just the text string directly. In React Native, `onChangeText` is always preferred — it's simpler and the text string is what you need 99% of the time. `onChange` is only needed when you also need `eventCount` (for input synchronization in complex scenarios).

**Q2: How do you programmatically focus a TextInput?**
A2: Use `ref`: `const inputRef = useRef(null)`. Attach: `<TextInput ref={inputRef} />`. Focus: `inputRef.current?.focus()`. Blur: `inputRef.current?.blur()`. Check focus: `inputRef.current?.isFocused()`. Common use case: OTP input — after filling box 1, auto-focus box 2 by calling `box2Ref.current.focus()`. Also used for: focusing search bar when screen opens, moving focus after form submission failure.

**Q3: How does KeyboardAvoidingView work? When do you use `padding` vs `height`?**
A3: `KeyboardAvoidingView` adjusts its height or padding when the keyboard appears to keep content above the keyboard. `behavior="padding"` (iOS recommended): adds bottom padding equal to keyboard height — content stays in place, space added below. `behavior="height"` (Android): reduces the component's height — content compresses to fit. `behavior="position"`: moves the component's position. Rule: `Platform.OS === 'ios' ? 'padding' : 'height'` — different behaviors work better on each platform. An alternative: `react-native-keyboard-aware-scroll-view` which handles complex forms better.

**Q4: What keyboard types are available and when do you use each?**
A4: `default` — standard keyboard. `numeric` — numbers with . and , (for amounts). `number-pad` — numbers only (for OTP, PIN). `decimal-pad` — numbers + decimal point. `phone-pad` — phone keypad layout (India: use for 10-digit numbers). `email-address` — shows @ and .com (for login/signup email fields). `url` — shows / and .com (for URL inputs). `visible-password` — standard but shows typed chars (for custom password confirm field). Always match keyboard type to expected input for better UX.

**Q5: How do you implement a controlled TextInput?**
A5: Controlled = value is driven by React state. `const [text, setText] = useState('')`. Then: `<TextInput value={text} onChangeText={setText} />`. The `value` prop makes it controlled — the input always shows exactly what's in state. This means you can programmatically change the input (clear it, format it), validate before accepting characters, implement character limits, and format on the fly (e.g., add dashes to phone numbers). Without `value` prop, it's uncontrolled — harder to manipulate.

---

## 🔷 When to Use + When Not to Use
✅ **Use TextInput when:**
- Any user text input: name, phone, email, search, amount
- OTP with multiple boxes (use refs for auto-focus)
- Password (secureTextEntry)
- Multi-line text (multiline prop)

❌ **Don't forget:**
- Always wrap form with KeyboardAvoidingView
- Match keyboardType to input type
- onChangeText (not onChange)
- underlineColorAndroid="transparent" on Android

---

## 📊 Visual Diagram

```
CONTROLLED TEXTINPUT DATA FLOW:
──────────────────────────────────────────────────────
  User types "A"
       │
       ▼
  onChangeText("A")
       │
       ▼
  setText("A")   → React State update
       │
       ▼
  Re-render: value="A" → TextInput shows "A"

OTP AUTO-FOCUS FLOW:
──────────────────────────────────────────────────────
  [1][_][_][_]  ← focus box 1, user types "7"
       │
  onChangeText("7")
  newOtp[0] = "7"
  ref[1].current.focus()  ← auto move to box 2!
       │
  [7][_][_][_]  ← now box 2 is focused
       │
  User types "3" → [7][3][_][_] → focus box 3
  User types "8" → [7][3][8][_] → focus box 4
  User types "2" → [7][3][8][2] → Keyboard.dismiss() + onComplete("7382")

KEYBOARD TYPES (phone):
──────────────────────────────────────────────────────
  phone-pad:    [1][2][3]
                [4][5][6]
                [7][8][9]
                [*][0][#]   (phone layout)

  number-pad:   [1][2][3]
                [4][5][6]
                [7][8][9]
                   [0]     (OTP/PIN layout)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TextInput | Text input component | Text input component |
| onChangeText | Callback with text string | Text string के साथ callback |
| keyboardType | Which keyboard to show | कौन सा keyboard दिखाएं |
| secureTextEntry | Hide characters (password) | Characters छुपाएं (password) |
| returnKeyType | What Return key shows | Return key क्या दिखाए |
| KeyboardAvoidingView | Prevent keyboard from covering inputs | Keyboard inputs cover न करे |
| autoCapitalize | Auto-capitalize behavior | Auto-capitalize behavior |
| multiline | Multi-line input (like textarea) | Multi-line input |

---

## ⚡ 3-Line Summary
**English:**
1. `TextInput` is the only built-in text input in RN — use `onChangeText` (not `onChange`), match `keyboardType` to input type, always set `underlineColorAndroid="transparent"`.
2. For OTP fields: use multiple TextInputs + refs for auto-focus via `ref.current.focus()` between boxes.
3. Always wrap forms in `KeyboardAvoidingView` with `behavior={Platform.OS === 'ios' ? 'padding' : 'height'}` to prevent keyboard from covering inputs.

**Hindi:**
1. `TextInput` RN में एकमात्र text input है — `onChangeText` use करो, `keyboardType` match करो, `underlineColorAndroid="transparent"` set करो।
2. OTP fields: multiple TextInputs + refs → `ref.current.focus()` से auto-focus।
3. हमेशा forms को `KeyboardAvoidingView` में wrap करो — keyboard inputs cover न करे।

---

## ➡️ Next Topic
**26. ScrollView Component** — scrollable content, keyboard dismiss, nested scrolling।
