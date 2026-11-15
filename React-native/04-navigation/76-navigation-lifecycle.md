# 76. Navigation Lifecycle
# हिंदी में: Navigation Lifecycle — Screen का Focus, Blur और Unmount
# Platform: Android ✅ | iOS ✅ | Both ✅

> Targets: Expo SDK 52 (React Native 0.76) + React Navigation v7 (check current docs — APIs change between SDKs). v6 में भी ये events वही हैं।

---

## 🔵 Simple Definition (English)
In React Navigation a screen is **not unmounted** when you navigate forward; it stays mounted in the stack and only loses **focus**. So `useEffect` runs once on mount, while `focus` / `blur` events (or `useFocusEffect`) fire every time the screen becomes visible or hidden.

## 🔵 सरल परिभाषा (Hindi)
React Navigation में आगे navigate करने पर पिछली screen **unmount नहीं होती**; वह stack में mounted रहती है और बस **focus** खो देती है। इसलिए `useEffect` सिर्फ mount पर चलता है, जबकि `focus` / `blur` events (या `useFocusEffect`) screen हर बार दिखने/छुपने पर चलते हैं।

---

## 🔴 Problem it Solves
```
Web सोच: नई page = पुरानी page destroy.
RN stack: Home -> Cart -> Payment. Home और Cart अभी भी memory में हैं!

Zomato Cart screen:
  User Payment से वापस Cart आया.
  useEffect([]) दोबारा नहीं चला -> cart total पुराना दिखा.

Swiggy Tracking screen:
  User दूसरी screen पर गया पर WebSocket / timer चलता रहा -> battery drain.
```

## 🔴 यह क्यों बना? (Hindi)
Mobile में back जाने पर पुरानी screen वैसी ही (scroll position, state) चाहिए, इसलिए screens mounted रखी जाती हैं। लेकिन तब "screen दिखी / छुपी" पकड़ने के लिए अलग events चाहिए थे: `focus`, `blur`, `beforeRemove`। ये data refresh करने और timer/socket रोकने के काम आते हैं।

---

## 🟢 How it Works — Step by Step
```
Stack: A -> push B -> push C -> goBack -> goBack

A: mount, focus
push B:  A: blur (mounted रहती है)      B: mount, focus
push C:  B: blur                          C: mount, focus
goBack:  C: beforeRemove, blur, unmount   B: focus
goBack:  B: beforeRemove, blur, unmount   A: focus
```
Events (navigation.addListener):
```
'focus'          screen active हुई
'blur'           screen inactive हुई
'beforeRemove'   screen हटने वाली है (e.preventDefault() से रोक सकते हो)
'state'          navigator का state बदला
'transitionStart' / 'transitionEnd'   (stack navigator animation)
```
Hooks: `useIsFocused()` (boolean, re-render करता है), `useFocusEffect(cb)` (focus पर चले, blur पर cleanup)।

## 🟢 कैसे काम करता है? (Hindi)
```
1. आगे जाने पर पुरानी screen mounted रहती है, सिर्फ blur होती है
2. वापस आने पर वही screen फिर focus होती है (mount दोबारा नहीं)
3. useEffect([]) = सिर्फ पहली बार; useFocusEffect = हर बार focus पर
4. Screen pop होने पर ही असली unmount होता है
5. beforeRemove से "unsaved changes?" alert दिखा सकते हैं
```

---

## 🟡 Real World Example
**Zomato Cart:** Cart screen `useFocusEffect` से हर बार focus पर cart API refetch करती है, ताकि Restaurant screen में item जोड़कर लौटने पर total सही दिखे। **Swiggy Tracking:** socket `focus` पर connect और `blur` पर disconnect होता है।

## 🟡 Real Example Hindi mein
**Paytm Send Money:** user amount भर चुका है और back दबाता है। `beforeRemove` listener "Discard transaction?" का alert दिखाता है; user Cancel करे तो `e.preventDefault()` से screen रुकी रहती है।

---

## 💻 Code Example — Basic
```jsx
import React, { useCallback, useEffect, useState } from 'react'; // React + hooks
import { View, Text, Button } from 'react-native';               // UI
import { useFocusEffect, useNavigation } from '@react-navigation/native'; // lifecycle hooks

export default function CartScreen() {
  const navigation = useNavigation();                 // navigation object
  const [total, setTotal] = useState(0);              // cart total state

  // 1) सिर्फ mount पर एक बार (screen pop होने पर unmount cleanup)
  useEffect(() => {
    console.log('Cart MOUNTED');                      // पहली बार बनी
    return () => console.log('Cart UNMOUNTED');       // pop होने पर ही
  }, []);                                             // खाली deps = सिर्फ mount

  // 2) हर बार focus पर चलेगा; blur पर cleanup चलेगा
  useFocusEffect(
    useCallback(() => {                               // useCallback ज़रूरी है वरना हर render पर चलेगा
      console.log('Cart FOCUSED -> refresh');         // screen दिखी
      setTotal(Math.floor(Math.random() * 500));      // demo: नया total "fetch" किया
      return () => console.log('Cart BLURRED');       // दूसरी screen पर गए
    }, [])                                            // deps
  );

  // 3) event listener का तरीका (class-style, कहीं भी)
  useEffect(() => {
    const unsub = navigation.addListener('focus', () => console.log('focus event')); // subscribe
    return unsub;                                     // unsubscribe cleanup
  }, [navigation]);                                   // navigation stable है

  return (
    <View>
      <Text>Total: ₹{total}</Text>
      <Button title="Go to Payment" onPress={() => navigation.navigate('Payment')} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```tsx
// Unsaved-changes guard + live socket tied to focus + Android back handling
import React, { useCallback, useEffect, useRef, useState } from 'react'; // hooks
import { Alert, Platform, TextInput, View } from 'react-native';          // RN
import { useFocusEffect, useNavigation } from '@react-navigation/native'; // lifecycle

export default function AddressForm() {
  const navigation = useNavigation();                       // navigation
  const [text, setText] = useState('');                     // form data
  const dirty = useRef(false);                              // unsaved flag (re-render नहीं चाहिए)

  // beforeRemove: back button, swipe-back, header back सबको पकड़ता है
  useEffect(() => {
    const unsub = navigation.addListener('beforeRemove', (e) => {
      if (!dirty.current) return;                           // कुछ unsaved नहीं -> जाने दो
      e.preventDefault();                                   // navigation रोको
      Alert.alert('Discard changes?', 'Address save नहीं हुआ.', [
        { text: 'Stay', style: 'cancel' },                  // रुको
        {
          text: 'Discard',
          style: 'destructive',                             // iOS में लाल दिखता है
          onPress: () => navigation.dispatch(e.data.action), // रोकी हुई action फिर चलाओ
        },
      ]);
    });
    return unsub;                                           // cleanup
  }, [navigation]);

  // Live updates सिर्फ तब जब screen दिख रही हो
  useFocusEffect(
    useCallback(() => {
      const ws = new WebSocket('wss://example.com/live');   // socket खोलो
      ws.onerror = (err) => console.warn('socket error', err); // error handling
      return () => ws.close();                              // blur पर बंद -> battery बचत
    }, [])
  );

  return (
    <View style={{ padding: Platform.select({ ios: 16, android: 12 }) }}> {/* platform padding */}
      <TextInput
        value={text}
        onChangeText={(t) => { dirty.current = true; setText(t); }} // dirty mark करो
        placeholder="Flat, Street, City"
      />
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Back trigger | Hardware/gesture back -> `beforeRemove` चलता है | Swipe-back gesture -> `beforeRemove` चलता है |
| Swipe-back रोकना | `gestureEnabled` का असर नहीं (hardware back है) | `gestureEnabled: false` से swipe-back बंद |
| App background जाना | Screen blur नहीं होती; `AppState` use करो | वही; navigation events नहीं चलते |
| Process kill | OS memory के लिए app kill कर सकता है, state खो जाती है | iOS भी suspended app kill कर सकता है |

App background/foreground navigation event नहीं है — उसके लिए `AppState` चाहिए।

---

## 🟠 Expo vs CLI Difference
Expo way (Expo Router):
```jsx
import { useFocusEffect } from 'expo-router';   // expo-router भी useFocusEffect export करता है
import { useCallback } from 'react';
export default function Screen() {
  useFocusEffect(useCallback(() => { console.log('focus'); }, [])); // वही behaviour
  return null;
}
```
CLI way (React Navigation):
```jsx
import { useFocusEffect } from '@react-navigation/native'; // direct import
```
दोनों में lifecycle एक जैसा है, क्योंकि Expo Router React Navigation पर बना है।

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** data fetch `useEffect([])` में करना और सोचना कि वापस आने पर refresh होगा
✅ **Correct:** `useFocusEffect(useCallback(...))` use करो।

❌ **Mistake 2:** `useFocusEffect` में `useCallback` भूल जाना -> effect हर render पर दोबारा चलता है
✅ **Correct:** callback को `useCallback` में wrap करो।

❌ **Mistake 3:** `addListener` का return (unsubscribe) cleanup में न देना -> memory leak, duplicate listeners
✅ **Correct:** `return unsub;`

❌ **Mistake 4:** Tab screens से unmount की उम्मीद (`unmountOnBlur`) — यह option v7 में हटा दिया गया
✅ **Correct:** v7 में focus पर reset के लिए `useFocusEffect` + state reset use करो (अपने version के docs check करो)।

---

## 🧠 Tricky Interview Question
**Q: Stack में A -> B है। B पर `console.log` वाला `useEffect(() => { log('A mounted') }, [])` A में है। B से goBack करें तो क्या A का log फिर छपेगा?**

**Answer:** नहीं। A कभी unmount नहीं हुई थी, सिर्फ blur हुई थी, इसलिए mount effect दोबारा नहीं चलता। A का `focus` event और `useFocusEffect` चलेगा। अगर A को `replace` से बदला जाता तो A unmount होती। Tab navigator में भी screens (lazy mount के बाद) mounted रहती हैं।

---

## ⚫ Interview Questions + Answers
**Q1: `useEffect` और `useFocusEffect` में फर्क?**
A1: `useEffect` component lifecycle (mount/unmount) से बंधा है, `useFocusEffect` navigation focus/blur से। screen mounted रहकर भी बार-बार focus हो सकती है।

**Q2: `useIsFocused` कब use करें?**
A2: जब render में boolean चाहिए (जैसे focused हो तभी `<Camera active>`)। यह focus बदलने पर re-render कराता है, इसलिए side-effects के लिए `useFocusEffect` बेहतर है।

**Q3: `beforeRemove` क्या करता है?**
A3: screen हटने से ठीक पहले चलता है; `e.preventDefault()` से रोककर confirmation दिखा सकते हैं, फिर `navigation.dispatch(e.data.action)` से जारी करते हैं।

**Q4: Screen कब सच में unmount होती है?**
A4: जब वह stack से pop/replace/reset से हटे। आगे navigate या tab बदलने से नहीं।

**Q5: `freezeOnBlur` क्या है?**
A5: `react-native-screens` का option जो blur हुई screens का re-render रोक देता है (performance)। Native stack में `freezeOnBlur: true` से enable होता है; version-dependent, docs देखो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर बार screen दिखने पर data refresh करना हो
- Socket / timer / camera / location को blur पर रोकना हो
- Unsaved changes का confirmation दिखाना हो

❌ Avoid when:
- सिर्फ एक बार का setup (वह `useEffect([])` में)
- Heavy काम focus पर बिना debounce किए (transition lag करेगा) — `InteractionManager.runAfterInteractions` use करो

---

## 📊 Visual Diagram
```
 A        B        C            events
 ●focus
 ○blur -> ●focus                push B   (A mounted रहती है)
          ○blur -> ●focus       push C
          ●focus <- ✕unmount    goBack   (C: beforeRemove, blur, unmount)
 ●focus <- ✕unmount             goBack

 ●=focused  ○=mounted but blurred  ✕=unmounted
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| focus | Screen became active | Screen सक्रिय हुई |
| blur | Screen became inactive | Screen निष्क्रिय हुई |
| mount | Component created | Component बना |
| unmount | Component destroyed | Component हटा |
| beforeRemove | Event before screen removal | हटने से पहले का event |
| useFocusEffect | Effect tied to focus | Focus से जुड़ा effect |

---

## ⚡ 3-Line Summary
English:
1. Screens stay mounted while navigating forward; they only blur, and re-focus on return.
2. Use `useFocusEffect` (with `useCallback`) for refresh and cleanup, `beforeRemove` to guard exits.
3. `useEffect([])` runs once; unmount happens only when the screen is popped or replaced.

Hindi:
1. आगे navigate करने पर screens mounted रहती हैं; सिर्फ blur होती हैं और लौटने पर फिर focus।
2. Refresh और cleanup के लिए `useFocusEffect` (`useCallback` के साथ), बाहर निकलने की जाँच के लिए `beforeRemove`।
3. `useEffect([])` एक बार चलता है; unmount तभी होता है जब screen pop या replace हो।

---

## ➡️ Next Topic
**77. Expo Router (File-based Routing)** — Folder structure से ही navigation बनाना।
