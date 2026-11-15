# 187. TypeScript in React Native
# हिंदी में: React Native में TypeScript
# Platform: Both ✅ (Android ✅ | iOS ✅) — compile-time tool, runtime नहीं

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). नए Expo projects में TypeScript template default है (`npx create-expo-app@latest`)। React Navigation v6/v7 के types अलग-अलग तरीके से global declare होते हैं (v7 static API में auto-infer)।

---

## 🔵 Simple Definition (English)
**TypeScript** adds static types to JavaScript. You describe the shape of props, state, API responses and navigation params, and the compiler catches mistakes (typos, wrong types, missing props) before the app runs. Types are erased at build time — no runtime cost.

## 🔵 सरल परिभाषा (Hindi)
**TypeScript** JavaScript में static types जोड़ता है। आप props, state, API response और navigation params का आकार बताते हैं, और compiler गलतियाँ (typo, गलत type, छूटा prop) app चलने से पहले पकड़ लेता है। Types build में हट जाते हैं — runtime पर कोई cost नहीं।

---

## 🔴 Problem it Solves
```
JS में:
  ❌ <Price amount="100" />  → string भेज दिया, "100"+5 = "1005" bug
  ❌ navigation.navigate('Detial') typo → runtime crash
  ❌ API से user.name की जगह user.fullName मान लिया → undefined
  ❌ बड़ी team में refactor डरावना
TS के साथ:
  ✅ Editor में red underline, autocomplete
  ✅ Refactor safe
  ✅ Code खुद documentation
```

## 🔴 यह क्यों बना? (Hindi)
```
JavaScript dynamic है, गलतियाँ runtime पर पता चलती हैं।
Mobile app में crash महँगा है (store update, reviews)।
TS गलती development में ही पकड़ता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Expo: npx create-expo-app@latest (TS default) या CLI में --template
Step 2 → tsconfig.json: "extends": "expo/tsconfig.base", "strict": true
Step 3 → Components में Props type/interface define करो
Step 4 → State/hook generics: useState<User | null>(null)
Step 5 → API response types/ Zod से runtime validation
Step 6 → Navigation: ParamList type बनाओ, screens में NativeStackScreenProps
Step 7 → CI में npx tsc --noEmit चलाओ (type-check)
Step 8 → Metro/Babel सिर्फ types हटाता है; checking tsc करता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
.tsx file लिखो → Babel types हटाकर JS बना देता है (app चलता है)।
Type checking अलग से tsc करता है (editor + CI)।
इसलिए type error होने पर भी app run हो सकता है — CI में tsc ज़रूर चलाओ।
```

---

## 🟡 Real World Example
**Swiggy** जैसे app में `Restaurant`, `MenuItem`, `CartItem` types होते हैं; API बदलकर `price` को `number` से `{ amount, currency }` किया गया तो सारी जगह compile error दिखती है, और production crash से पहले fix हो जाती है। **Paytm** में payment params (`amount: number; upiId: string`) का strict type गलत फ़ोन/amount जाने से बचाता है।

## 🟡 Real Example Hindi mein
Swiggy में API का `price` बदला तो TS ने सारी जगह दिखा दीं जहाँ code टूटेगा। Paytm में `amount` का type `number` तय है, string जाए तो compile error।

---

## 💻 Code Example — Basic
```tsx
import React, { useState } from 'react';                    // React + state
import { View, Text, Pressable, StyleSheet } from 'react-native'; // RN components

// 1. Props का type — interface
interface PriceTagProps {
  label: string;                                            // required text
  amount: number;                                           // required number
  currency?: 'INR' | 'USD';                                 // optional, सिर्फ ये 2 values
  onPress?: (amount: number) => void;                       // optional callback
}

// 2. Component — props typed
export function PriceTag({ label, amount, currency = 'INR', onPress }: PriceTagProps) {
  const [pressed, setPressed] = useState<number>(0);        // generic: number state

  const handle = () => {
    setPressed(p => p + 1);                                 // update count
    onPress?.(amount);                                      // optional chaining
  };

  return (
    <Pressable onPress={handle} style={styles.box}>
      <Text>{label}: {currency === 'INR' ? '₹' : '$'}{amount}</Text>
      <Text>Pressed {pressed} times</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({ box: { padding: 12 } });  // typed styles

// Usage: <PriceTag label="Pizza" amount={299} />            ✅
// <PriceTag label="Pizza" amount="299" />                   ❌ compile error (string)
```

## 💻 Code Example — Advanced
```tsx
// ---------- types.ts ----------
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

export type RootStackParamList = {                          // all routes + params
  Home: undefined;                                          // no params
  Restaurant: { id: string; name: string };                 // required params
  Cart: { items: CartItem[] } | undefined;                  // optional params
};
export type RestaurantProps = NativeStackScreenProps<RootStackParamList, 'Restaurant'>;

export interface CartItem { id: string; name: string; price: number; qty: number }

// Discriminated union — loading/success/error states safe
export type Async<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; message: string };

// ---------- api.ts ----------
export async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(url, { signal });                 // network call
  if (!res.ok) throw new Error(`HTTP ${res.status}`);       // error path
  return (await res.json()) as T;                           // NOTE: cast = trust, runtime validate (Zod) for safety
}

// ---------- useAsync.ts — generic hook ----------
import { useEffect, useState } from 'react';

export function useFetch<T>(url: string): Async<T> {
  const [state, setState] = useState<Async<T>>({ status: 'idle' });
  useEffect(() => {
    const ctrl = new AbortController();                     // cancel on unmount
    setState({ status: 'loading' });
    fetchJson<T>(url, ctrl.signal)
      .then(data => setState({ status: 'success', data }))
      .catch((e: unknown) => {                              // unknown, not any
        if (ctrl.signal.aborted) return;                    // ignore cancel
        setState({ status: 'error', message: e instanceof Error ? e.message : 'Unknown' });
      });
    return () => ctrl.abort();                              // cleanup
  }, [url]);
  return state;
}

// ---------- RestaurantScreen.tsx ----------
import React from 'react';
import { View, Text, ActivityIndicator } from 'react-native';

export function RestaurantScreen({ route }: RestaurantProps) {  // route.params typed
  const { id, name } = route.params;                        // id: string, name: string
  const state = useFetch<{ menu: CartItem[] }>(`https://api.example.com/r/${id}`);

  if (state.status === 'loading') return <ActivityIndicator />;
  if (state.status === 'error') return <Text>{state.message}</Text>;   // message exists here
  if (state.status === 'success') {
    return <View><Text>{name}</Text>{state.data.menu.map(m => <Text key={m.id}>{m.name}</Text>)}</View>;
  }
  return null;                                              // idle
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| TypeScript support | Same | Same |
| Platform types | `Platform.OS: 'android'` | `'ios'` (union type) |
| Platform files | `Foo.android.tsx` | `Foo.ios.tsx` — दोनों का same exported type रखो |
| Native module types | Kotlin/Java side — TS में declare करना पड़ता है | Swift/ObjC — वही |
| Runtime behaviour | कोई फर्क नहीं (types erase) | कोई फर्क नहीं |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx create-expo-app@latest            → TS ready
// tsconfig.json: { "extends": "expo/tsconfig.base", "compilerOptions": { "strict": true } }
// Expo packages अपने types के साथ आते हैं
// expo-router: typed routes → app.json "experiments": { "typedRoutes": true }
```
CLI way:
```jsx
// npx @react-native-community/cli init MyApp   (TS template default)
// tsconfig.json: { "extends": "@react-native/typescript-config" }
// (पुराने versions में "@tsconfig/react-native")
// Third-party library में types न हों तो: npm i -D @types/<name> या declare module
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: हर जगह `any`
✅ Correct: `unknown` + narrowing, या सही type/Zod schema

❌ Mistake 2: `as` cast से API data "valid" मान लेना
✅ Correct: Zod/valibot से runtime validate, फिर type infer

❌ Mistake 3: `useNavigation()` बिना type → `navigate('anything')` allowed
✅ Correct: `useNavigation<NativeStackNavigationProp<RootStackParamList>>()` या global `RootParamList` declare

❌ Mistake 4: `strict: false`
✅ Correct: `strict: true` शुरू से

❌ Mistake 5: सोचना कि type error = app नहीं चलेगा
✅ Correct: Metro types नहीं जाँचता; CI में `tsc --noEmit` ज़रूरी

---

## 🧠 Tricky Interview Question
```ts
type Status = 'idle' | 'loading' | 'done';
function f(s: Status) {
  switch (s) {
    case 'idle': return 1;
    case 'loading': return 2;
  }
}
const x: number = f('done');
```
Q: क्या compile होगा?

Answer: `strict` में नहीं। `f` का return type `1 | 2 | undefined` infer होता है क्योंकि `'done'` case handle नहीं है (noImplicitReturns/strict के साथ error "not all code paths return a value" भी आ सकता है)। `number` में `undefined` assign नहीं होगा → error। Fix: `default` में `never` exhaustiveness check (`const _x: never = s`) लगाओ ताकि नया status जोड़ने पर compiler बताए।

---

## ⚫ Interview Questions + Answers
Q1: `interface` vs `type`?
A1: दोनों object shapes के लिए चलते हैं; `interface` extend/merge होता है, `type` union/intersection/mapped types के लिए बेहतर। Props में कोई भी चलता है, team convention रखो।

Q2: `unknown` और `any` का फर्क?
A2: `any` checks बंद कर देता है; `unknown` use से पहले narrowing माँगता है — सुरक्षित।

Q3: Navigation को type-safe कैसे करें?
A3: `ParamList` type + `NativeStackScreenProps`; या global `declare global { namespace ReactNavigation { interface RootParamList extends RootStackParamList {} } }` (v6/v7 dynamic API)। v7 की static API में auto-infer होता है (check current docs)।

Q4: TS runtime पर चलता है क्या?
A4: नहीं। Babel types हटाता है; सिर्फ JS चलती है। इसलिए API response का runtime validation अलग चाहिए।

Q5: `Pick`, `Omit`, `Partial` कब?
A5: Existing type से नया type: `Omit<User,'password'>` public profile, `Partial<Settings>` update payload।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Production app, team project
- Navigation/API/Redux/Zustand typing
- लंबे समय तक maintain होने वाला code

❌ Avoid when:
- 1 दिन का throwaway prototype (फिर भी Expo default TS है, इसलिए कम ही avoid)

---

## 📊 Visual Diagram
```
  .tsx source
     │
     ├──► tsc --noEmit  ──► type errors (editor/CI)   ← checking
     │
     └──► Babel (Metro) ──► plain JS bundle ──► app   ← types erased
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Interface/type | Shape definition | आकार की परिभाषा |
| Generic | Type parameter `<T>` | सामान्य type |
| Union | One of many types | कई में से एक |
| Narrowing | Refine type by checks | Type संकरा करना |
| `strict` | Strong checks mode | सख्त जाँच |
| Discriminated union | Union with tag field | Tag वाला union |

---

## ⚡ 3-Line Summary
English: TypeScript catches mistakes at compile time and is erased at runtime.
Type props, state, API data and navigation params; prefer `unknown` to `any`.
Run `tsc --noEmit` in CI and validate API data at runtime.

Hindi: TypeScript गलतियाँ compile time पर पकड़ता है, runtime पर हट जाता है।
Props, state, API और navigation type करो; `any` की जगह `unknown`।
CI में `tsc --noEmit` चलाओ और API data runtime पर validate करो।

---

## ➡️ Next Topic
**188. React Native + WebView** — app के अंदर web content (payment page, T&C) दिखाना।

---
