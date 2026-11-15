# 110. App State (foreground/background)
# हिंदी में: App State (app सामने है या पीछे)
# Platform: Android ✅ | iOS ✅ | Both ✅ (`inactive` सिर्फ़ iOS)

> Target: Expo SDK 52 (React Native 0.76) — `AppState` React Native core में है, अलग package नहीं (check current docs — APIs change between SDKs). Expo Go और CLI दोनों में चलता है।

---

## 🔵 Simple Definition (English)
**AppState** tells you whether the app is in the **foreground** (`active`), **background**, or (iOS only) **inactive** (a transition like the app switcher or incoming call). You listen to changes to refresh data, pause video, or lock the app.

## 🔵 सरल परिभाषा (Hindi)
**AppState** बताता है कि app **foreground** (`active`) में है, **background** में है, या (सिर्फ़ iOS) **inactive** है (जैसे app switcher या call आना)। आप इन बदलावों को सुनकर data refresh, video pause या app lock जैसे काम करते हैं।

---

## 🔴 Problem it Solves
```
❌ User app se bahar jaake wapas aaye to purana data dikhta hai
❌ Video/music background me bhi chalta rehta hai
❌ Banking app me screen lock nahi hota
✅ 'change' event sunke sahi samay par sahi kaam
```

## 🔴 यह क्यों बना? (Hindi)
```
User दूसरे app से लौटे तो पुराना data दिखता है।
Background में video/timer चलते रहते हैं और battery जाती है।
Banking app को वापस आने पर PIN माँगना होता है।
AppState से पता चलता है कि app कब आगे/पीछे हुआ।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → import { AppState } from 'react-native'
Step 2 → AppState.currentState -> 'active' | 'background' | 'inactive' (iOS) | 'unknown'
Step 3 → const sub = AppState.addEventListener('change', (next) => ...)
Step 4 → Pichhla state useRef me rakho: background -> active = "foreground me wapas"
Step 5 → Us transition par refetch / unlock-screen / resume
Step 6 → Unmount par sub.remove()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → addEventListener('change') से हर बदलाव की सूचना मिलती है।
Step 2 → पिछला state useRef में रखें ताकि बदलाव पहचान सकें।
Step 3 → background/inactive -> active हो तो data refresh करें।
Step 4 → unmount पर subscription हटाएँ।
```

---

## 🟡 Real World Example
**Paytm / PhonePe / banking apps:** app comes back from background after 30 seconds -> asks for PIN/biometric. **Swiggy:** returning to the app refreshes live order tracking. **Hotstar / YouTube:** pause video when app goes to background (unless PiP). **Zomato:** hide card details in the app switcher.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe:** 30 सेकंड बाद background से लौटने पर PIN/biometric माँगते हैं। **Swiggy:** वापस आने पर live order tracking refresh होती है। **Hotstar:** background में जाने पर video pause। **Zomato:** app switcher में card details छुपाना।

---

## 💻 Code Example — Basic
```jsx
// AppStateBasic.jsx — state live dikhao
import React, { useEffect, useState } from 'react';                    // React + hooks
import { View, Text, AppState } from 'react-native';                   // RN + AppState

export default function AppStateBasic() {
  const [state, setState] = useState(AppState.currentState);           // abhi ka state

  useEffect(() => {
    const sub = AppState.addEventListener('change', (next) => {        // har badlav par
      setState(next);                                                  // state update
      console.log('AppState ->', next);                                // log
    });
    return () => sub.remove();                                         // cleanup (zaroori)
  }, []);                                                              // ek baar subscribe

  return (
    <View style={{ padding: 40 }}>
      <Text>Current: {state}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// useAppState.js — "foreground me wapas" + background duration + app lock
import { useEffect, useRef } from 'react';
import { AppState } from 'react-native';

// Pure logic: kya lock dikhana chahiye? (test karna aasan)
export function shouldLock(backgroundedAt, now, thresholdMs = 30000) {
  if (backgroundedAt == null) return false;                            // kabhi background nahi gaya
  return now - backgroundedAt >= thresholdMs;                          // 30s+ background tha
}

export function useAppState({ onForeground, onBackground, lockAfterMs = 30000, onLock }) {
  const prev = useRef(AppState.currentState);                          // pichhla state
  const bgAt = useRef(null);                                           // background time

  // Callbacks ko ref me rakho taaki listener baar-baar na lage
  const cbs = useRef({});
  cbs.current = { onForeground, onBackground, onLock };

  useEffect(() => {
    const sub = AppState.addEventListener('change', (next) => {
      const was = prev.current;
      // active -> background (Android) ya active -> inactive -> background (iOS)
      if (was === 'active' && /inactive|background/.test(next)) {
        if (next === 'background') {
          bgAt.current = Date.now();                                   // time note karo
          cbs.current.onBackground?.();                                // pause/save
        }
      }
      // background/inactive -> active
      if (/inactive|background/.test(was) && next === 'active') {
        cbs.current.onForeground?.();                                  // refetch
        if (shouldLock(bgAt.current, Date.now(), lockAfterMs)) {
          cbs.current.onLock?.();                                      // PIN/biometric screen
        }
        bgAt.current = null;                                           // reset
      }
      prev.current = next;                                             // update
    });
    return () => sub.remove();                                         // cleanup
  }, [lockAfterMs]);
}

// Use:
// useAppState({ onForeground: () => queryClient.invalidateQueries(), onLock: () => nav.navigate('Lock') });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| States | `active`, `background` | `active`, `inactive`, `background` |
| `inactive` | ❌ Not used | ✅ App switcher, call/notification center, Face ID prompt |
| Permission dialog | Dialog खुलने पर कभी `active` बना रहता है | Permission/biometric sheet पर अक्सर `inactive` -> `active` (false "foreground" trigger!) |
| Home button | -> `background` | -> `inactive` -> `background` |
| Screen lock | -> `background` | -> `inactive` -> `background` |
| Initial value | Sometimes `unknown`/null before first event | Same caveat |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
import { AppState } from 'react-native';                               // core API, koi install nahi
const sub = AppState.addEventListener('change', (s) => console.log(s)); // same
// Extra: expo-screen-capture se screenshots block (alag topic)
```
CLI way:
```jsx
import { AppState } from 'react-native';                               // bilkul wahi
const sub = AppState.addEventListener('change', (s) => console.log(s)); // same
// Android native: Activity lifecycle onPause/onResume, iOS: applicationDidEnterBackground (native modules me)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: पुराना `AppState.addEventListener(...)` का return न लेना और `removeEventListener` use करना।
✅ Correct: Modern API subscription लौटाता है: `const sub = ...; sub.remove()`।

❌ Mistake 2: Cleanup भूल जाना (listeners जमा होते हैं)।
✅ Correct: `useEffect` return में `sub.remove()`।

❌ Mistake 3: iOS में `inactive` को background मानना।
✅ Correct: सिर्फ़ `background` पर भारी pause/lock करें।

❌ Mistake 4: हर `active` पर refetch (permission dialog भी trigger करता है)।
✅ Correct: पिछला state `background` था यह जाँचें, और throttle करें।

❌ Mistake 5: `useState` वाले पिछले state पर निर्भर होना (stale closure)।
✅ Correct: `useRef` में पिछला state रखें।

---

## 🧠 Tricky Interview Question
On iOS, the user taps "Allow" on a location permission dialog. Your `AppState` listener refetches whenever state becomes `active`. Why do you see an unexpected refetch?

Answer: When a system dialog appears, iOS moves the app `active -> inactive`, and after dismissal `inactive -> active`. Your handler treats that as "came to foreground" and refetches. Fix: refetch only on `background -> active` (track previous state in a ref) and debounce.

हिंदी: System dialog से iOS में `active -> inactive -> active` होता है, जो असली foreground नहीं है। सिर्फ़ `background -> active` पर refetch करें।

---

## ⚫ Interview Questions + Answers
Q1: AppState के कितने values हैं?
A1: `active`, `background`, `inactive` (iOS), और कभी-कभी `unknown`।

Q2: AppState और navigation focus में फ़र्क?
A2: AppState पूरे app का lifecycle है; focus एक screen का (`useFocusEffect`)। App background से लौटे तो screen focus नहीं बदलता।

Q3: Listener कैसे हटाएँ?
A3: `addEventListener` जो subscription लौटाता है उस पर `.remove()`।

Q4: Background में timer चलता है?
A4: नहीं भरोसेमंद नहीं; OS JS को suspend कर सकता है। समय का हिसाब `Date.now()` के अंतर से लगाएँ।

Q5: App lock कैसे बनाएँ?
A5: background होने का समय सहेजें; `active` पर अंतर threshold से ज़्यादा हो तो lock screen/biometric दिखाएँ।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Foreground पर data refresh
- Video/audio pause, socket disconnect/reconnect
- App lock / privacy screen

❌ Avoid when:
- किसी एक screen का focus जानना हो (`useFocusEffect`)
- Background में काम चलाना हो (Background Tasks)
- Permission dialog वाले `inactive` बदलाव पर निर्भर logic

---

## 📊 Visual Diagram
```
  Launch ──▶ active ──home/switch──▶ (iOS: inactive) ──▶ background
               ▲                                            │
               └──────────── app reopen ◀───────────────────┘
  Android: active ⇄ background (no inactive)

  listener('change', next):
     background|inactive ─▶ active  => refetch / lock check
     active ─▶ background            => pause / save timestamp
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| active | App in foreground | app सामने है |
| background | App hidden | app पीछे है |
| inactive | iOS transition state | iOS का बीच का state |
| Subscription | Listener handle with remove() | सुनने वाला handle |
| Lifecycle | App's life stages | app के चरण |
| Stale closure | Old value captured | पुराना मान फँसना |

---

## ⚡ 3-Line Summary
English: AppState reports active, background and (iOS) inactive.
Listen to change, keep the previous state in a ref and act on background to active.
Always remove the subscription on cleanup.

Hindi: AppState active, background और (iOS) inactive बताता है।
change सुनें, पिछला state ref में रखें और background से active पर काम करें।
Cleanup में subscription ज़रूर हटाएँ।

---

## ➡️ Next Topic
**111. NetInfo — Network State** — internet है या नहीं और कौन सा network (WiFi/Cellular) यह जानना।

---
