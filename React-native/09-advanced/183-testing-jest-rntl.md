# 183. Testing in React Native (Jest + RNTL)
# हिंदी में: React Native में Testing — Jest + React Native Testing Library
# Platform: Both ✅ (Android ✅ | iOS ✅) — tests Node में चलते हैं, device नहीं चाहिए

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). `jest-expo` preset और `@testing-library/react-native` v12/v13 use किए गए हैं।

---

## 🔵 Simple Definition (English)
**Jest** is the test runner (finds tests, runs them, mocks things). **React Native Testing Library (RNTL)** renders your components in a fake environment and lets you test them like a user would: find text, press buttons, type in inputs. No emulator needed — tests run in Node in milliseconds.

## 🔵 सरल परिभाषा (Hindi)
**Jest** test runner है (tests ढूँढता है, चलाता है, mocks देता है)। **RNTL** आपके components को fake environment में render करता है और user की तरह test करता है: text ढूँढो, button दबाओ, input में type करो। Emulator नहीं चाहिए — tests Node में milliseconds में चलते हैं।

---

## 🔴 Problem it Solves
```
BEFORE TESTS:
  ❌ हर change के बाद manually app खोलकर check करना
  ❌ Login fix किया → Cart टूट गया, पता production में चला
  ❌ Refactor करने से डर लगता है
WITH JEST + RNTL:
  ✅ 1 command में 500 tests → 10 सेकंड
  ✅ CI (GitHub Actions) पर हर PR में auto-run
  ✅ Refactor safe — tests बताते हैं क्या टूटा
```

## 🔴 यह क्यों बना? (Hindi)
```
Manual testing slow और भरोसेमंद नहीं है।
Jest + RNTL = automatic safety net।
Code बदलो, tests चलाओ, bug तुरंत पकड़ो।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → jest-expo preset Babel/Metro जैसा transform करता है (JSX, TS)
Step 2 → render(<Component />) → fake native tree बनता है (real UI नहीं)
Step 3 → screen.getByText / getByRole से element ढूँढो (user जैसा)
Step 4 → fireEvent.press / userEvent.press से action करो
Step 5 → expect(...) से result verify करो
Step 6 → Native modules (camera, AsyncStorage) jest.mock() से fake करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Preset code को Jest-readable बनाता है
Step 2 → render() fake tree बनाता है, screen नहीं दिखती
Step 3 → Text/role से element ढूँढो — testID आखिरी option
Step 4 → press/type से user action simulate करो
Step 5 → expect() से check करो
Step 6 → Native चीज़ें mock करो क्योंकि Node में native code नहीं है
```

---

## 🟡 Real World Example
**Swiggy** का "Add to Cart" button: test लिखा जाता है — render MenuItem, "ADD" दबाओ, check करो कि quantity stepper "1" दिखाए और `onAdd` callback एक बार call हुआ। **Paytm** का amount input: "-50" type करो → error "Enter valid amount" दिखना चाहिए। ये logic बिना phone खोले CI में हर PR पर verify होता है।

## 🟡 Real Example Hindi mein
**Swiggy** में ADD button दबाओ → quantity 1 दिखे — यह test CI में auto चलता है। **Paytm** में गलत amount डालो → error message दिखे। बिना phone के, सेकंडों में, हर PR पर check।

---

## 💻 Code Example — Basic
```jsx
// ---------- package.json (relevant parts) ----------
// "scripts": { "test": "jest" },
// "jest": { "preset": "jest-expo" }
// Install: npx expo install jest-expo jest @types/jest --dev
//          npm i -D @testing-library/react-native

// ---------- Counter.jsx ----------
import React, { useState } from 'react';                 // React + state hook
import { View, Text, Pressable } from 'react-native';    // RN core components

export function Counter({ initial = 0 }) {               // prop: starting number
  const [count, setCount] = useState(initial);           // count state
  return (
    <View>
      <Text>Count: {count}</Text>                        {/* shows the count */}
      <Pressable accessibilityRole="button" onPress={() => setCount(count + 1)}>
        <Text>Increase</Text>                            {/* button label */}
      </Pressable>
    </View>
  );
}

// ---------- Counter.test.jsx ----------
import React from 'react';                               // needed for JSX
import { render, screen, fireEvent } from '@testing-library/react-native'; // RNTL
import { Counter } from './Counter';                     // component under test

describe('Counter', () => {                              // group of tests
  test('starts at given initial value', () => {          // one test case
    render(<Counter initial={5} />);                     // render in fake env
    expect(screen.getByText('Count: 5')).toBeTruthy();   // element must exist
  });

  test('increments when button pressed', () => {
    render(<Counter />);                                 // default initial = 0
    fireEvent.press(screen.getByRole('button', { name: 'Increase' })); // tap
    expect(screen.getByText('Count: 1')).toBeTruthy();   // UI updated
  });
});
```

## 💻 Code Example — Advanced
```jsx
// ---------- LoginForm.jsx — async + API call + error handling ----------
import React, { useState } from 'react';
import { View, Text, TextInput, Pressable, ActivityIndicator } from 'react-native';
import { loginApi } from './api';                        // network function (will be mocked)

export function LoginForm({ onSuccess }) {
  const [phone, setPhone] = useState('');                // phone input value
  const [error, setError] = useState('');                // error message
  const [loading, setLoading] = useState(false);         // spinner flag

  async function submit() {                              // runs on button press
    if (phone.length !== 10) {                           // validation
      setError('Enter 10 digit number');                 // show error
      return;                                            // stop here
    }
    setLoading(true);                                    // show spinner
    try {
      const user = await loginApi(phone);                // call server
      onSuccess(user);                                   // tell parent
    } catch (e) {
      setError('Server error, try again');               // API failed
    } finally {
      setLoading(false);                                 // hide spinner always
    }
  }

  return (
    <View>
      <TextInput placeholder="Phone" value={phone} onChangeText={setPhone} />
      {error ? <Text>{error}</Text> : null}
      {loading ? <ActivityIndicator /> : (
        <Pressable accessibilityRole="button" onPress={submit}><Text>Login</Text></Pressable>
      )}
    </View>
  );
}

// ---------- LoginForm.test.jsx ----------
import React from 'react';
import { render, screen, userEvent, waitFor } from '@testing-library/react-native';
import { LoginForm } from './LoginForm';
import { loginApi } from './api';

jest.mock('./api');                                      // auto-mock the API module

test('shows error for short phone number', async () => {
  const user = userEvent.setup();                        // userEvent = realistic interaction (RNTL v12.4+)
  render(<LoginForm onSuccess={jest.fn()} />);
  await user.type(screen.getByPlaceholderText('Phone'), '123');   // type 3 digits
  await user.press(screen.getByRole('button', { name: 'Login' })); // press login
  expect(screen.getByText('Enter 10 digit number')).toBeTruthy();  // error visible
  expect(loginApi).not.toHaveBeenCalled();               // API never called
});

test('calls onSuccess when API succeeds', async () => {
  loginApi.mockResolvedValue({ id: 1 });                 // fake success response
  const onSuccess = jest.fn();                           // spy function
  const user = userEvent.setup();
  render(<LoginForm onSuccess={onSuccess} />);
  await user.type(screen.getByPlaceholderText('Phone'), '9876543210');
  await user.press(screen.getByRole('button', { name: 'Login' }));
  await waitFor(() => expect(onSuccess).toHaveBeenCalledWith({ id: 1 })); // async wait
});

test('shows server error when API fails', async () => {
  loginApi.mockRejectedValue(new Error('500'));          // fake failure
  const user = userEvent.setup();
  render(<LoginForm onSuccess={jest.fn()} />);
  await user.type(screen.getByPlaceholderText('Phone'), '9876543210');
  await user.press(screen.getByRole('button', { name: 'Login' }));
  expect(await screen.findByText('Server error, try again')).toBeTruthy(); // findBy = waits
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Jest/RNTL tests | Node में चलते हैं, same | Node में चलते हैं, same |
| `Platform.OS` | Default 'ios' होता है; `Platform.OS = 'android'` set करके दूसरा branch test करो | वही |
| Platform-specific code | `jest.mock('react-native/Libraries/Utilities/Platform', ...)` या `Platform.select` mock | वही |
| Real behaviour (keyboard, gestures, permissions dialog) | Jest नहीं पकड़ता → Detox/Maestro चाहिए | वही |
| Test Bug | Android-only bug (back button) unit test में नहीं दिखता | iOS-only bug (safe area) भी नहीं दिखता |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: preset ready-made
// npx expo install jest-expo jest --dev
// package.json → "jest": { "preset": "jest-expo" }
// Expo modules (expo-camera etc.) की mocks preset में आती हैं
```
CLI way:
```jsx
// Bare RN CLI: preset 'react-native'
// package.json → "jest": { "preset": "react-native" }
// babel.config.js में 'module:@react-native/babel-preset' (new RN) चाहिए
// transformIgnorePatterns में RN libraries add करनी पड़ती हैं:
// "transformIgnorePatterns": ["node_modules/(?!(react-native|@react-native|@react-navigation)/)"]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Implementation test करना (`state.count === 1` check)
✅ Correct: Screen पर जो user देखता है वह test करो (`getByText('Count: 1')`)

❌ Mistake 2: Async UI के लिए `getByText` use करना → "not found"
✅ Correct: `await screen.findByText(...)` या `waitFor`

❌ Mistake 3: Native module mock नहीं किया → "Cannot read property of null"
✅ Correct: `jest.mock('@react-native-async-storage/async-storage', () => require('@react-native-async-storage/async-storage/jest/async-storage-mock'))`

❌ Mistake 4: हर चीज़ में `testID` लगाना
✅ Correct: पहले `getByRole`, `getByText`, `getByLabelText`; testID last resort

❌ Mistake 5: Snapshot tests पर सब भरोसा
✅ Correct: Snapshots छोटे रखो, behaviour tests मुख्य रखो

---

## 🧠 Tricky Interview Question
```jsx
test('x', () => {
  render(<Counter />);
  fireEvent.press(screen.getByText('Increase'));
  fireEvent.press(screen.getByText('Increase'));
  expect(screen.getByText('Count: 2')).toBeTruthy();
});
```
Q: यह pass क्यों होता है जबकि setState async है?

Answer: RNTL का `fireEvent` React के `act()` में wrap होता है। `act` सारे state updates और effects flush करके ही वापस आता है, इसलिए हर press के बाद UI updated है। अगर आप खुद `act` के बाहर state change करेंगे तो "not wrapped in act(...)" warning आएगी। Network/timers वाले async updates के लिए `waitFor/findBy` चाहिए।

---

## ⚫ Interview Questions + Answers
Q1: Jest और RNTL में क्या फर्क है?
A1: Jest runner + assertion + mocking है। RNTL React components render करने और user-style queries (getByText, getByRole) देने की library है। दोनों साथ चलते हैं।

Q2: Enzyme क्यों नहीं use करते?
A2: Enzyme maintained नहीं है और React 18+ को support नहीं करता। यह internals (state/instance) test करता था; RNTL behaviour test करता है।

Q3: Native module को कैसे mock करें?
A3: `jest.mock('module-name', () => ({ ... }))` या `jest.setup.js` में (`setupFiles`/`setupFilesAfterEach`). Expo modules के लिए `jest-expo` बहुत से mocks देता है।

Q4: `getBy`, `queryBy`, `findBy` का फर्क?
A4: `getBy` न मिले तो error फेंकता है; `queryBy` null देता है (absence check: `expect(queryByText('x')).toBeNull()`); `findBy` async है और timeout तक wait करता है।

Q5: Custom hook कैसे test करें?
A5: RNTL का `renderHook(() => useCart())`, फिर `result.current` पढ़ो और बदलाव `act(() => result.current.add(item))` में करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Business logic, forms, validation, conditional UI
- Reducers/hooks/utils (pure logic)
- Regression रोकना हो (CI)

❌ Avoid when:
- Real gestures, animations, native permissions, push — Detox/Maestro/manual device test चाहिए
- Pixel-perfect styling — snapshot से भरोसा मत करो

---

## 📊 Visual Diagram
```
        TESTING PYRAMID (RN)
              /\
             /E2E\        Detox/Maestro — कम, धीमे, real device
            /------\
           / RNTL   \     Component tests — बीच में
          /----------\
         /  Jest unit  \  Logic/utils/hooks — ज़्यादा, तेज़
        /--------------\
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Jest | Test runner + mocks | Test चलाने वाला tool |
| RNTL | Render + query components | Component test library |
| Mock | Fake replacement | नकली version |
| `act()` | Flush state updates | Updates पूरे होने तक रुकना |
| Snapshot | Saved output compare | Output की तस्वीर compare |
| testID | Hidden id for queries | Element की पहचान |

---

## ⚡ 3-Line Summary
English: Jest runs tests; RNTL renders components and queries them like a user.
Use `findBy`/`waitFor` for async, mock native modules, and test behaviour, not internals.
Unit/component tests are fast; real device behaviour needs E2E.

Hindi: Jest tests चलाता है; RNTL components user की तरह test करता है।
Async के लिए `findBy`/`waitFor`, native modules mock करो, internals नहीं behaviour test करो।
Device वाली चीज़ों के लिए E2E (Detox) चाहिए।

---

## ➡️ Next Topic
**184. E2E Testing (Detox)** — unit tests real device behaviour नहीं पकड़ते; Detox real app को emulator/simulator पर चलाकर full user flow test करता है।

---
