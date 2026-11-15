# 161. keyExtractor
# हिंदी में: keyExtractor (हर row की unique पहचान)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76. `keyExtractor` core `FlatList`/`SectionList` prop है।

---

## 🔵 Simple Definition (English)
`keyExtractor` is a FlatList prop: `(item, index) => string` that returns a **unique, stable string key** for each row. React uses the key to know which row is which when data changes, so it can reuse, move or remove rows correctly.

## 🔵 सरल परिभाषा (Hindi)
`keyExtractor` FlatList का prop है: `(item, index) => string` जो हर row के लिए **unique, stable string key** लौटाता है। Data बदलने पर React इसी key से पहचानता है कि कौन सी row कौन सी है, ताकि सही row reuse, move या delete हो।

---

## 🔴 Problem it Solves
```
Key न दो तो FlatList पहले item.key, फिर item.id ढूँढता है; दोनों न हों → index और warning:
  "VirtualizedList: missing keys for items, make sure to specify a key or id property
   on each item or provide a custom keyExtractor."

index को key बनाओ और list के बीच में item जोड़ो/हटाओ:
  सारी बाद की rows की key बदल जाती है → बेकार re-render,
  state (checkbox, TextInput text) ग़लत row में चला जाता है
```

## 🔴 यह क्यों बना? (Hindi)
```
Key न हो तो FlatList पहले item.key, फिर item.id देखता है, वरना index और warning।
index key पर बीच में item जोड़ने/हटाने से बाद की सारी rows की key बदलती है
→ सब re-render, और row की state (checkbox, text) ग़लत row में दिखती है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → FlatList हर item पर keyExtractor(item, index) चलाता है
Step 2 → Key string बनती है (जैसे "order_8841")
Step 3 → Data बदलता है (नया item जुड़ा)
Step 4 → React key मिलाता है: जो key पहले थी उसे reuse करता है
Step 5 → सिर्फ नई key वाली row बनती है; हटी key वाली unmount
Step 6 → बाकी rows की state और position सुरक्षित
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर item पर keyExtractor चलता है
Step 2 → String key बनती है
Step 3 → Data बदलता है
Step 4 → React पुरानी keys की rows reuse करता है
Step 5 → सिर्फ नई key की row बनती है, हटी की unmount
Step 6 → बाकी rows की state सुरक्षित
```

---

## 🟡 Real World Example
**Swiggy order history**: हर order का unique `orderId` है। नया order आने पर list के ऊपर जुड़ता है। `keyExtractor={o => o.orderId}` हो तो पुराने orders अपनी जगह नीचे खिसकते हैं और re-render नहीं होते। **WhatsApp** में message `id` से key बनती है ताकि delivered/seen ticks सही message पर बदलें।

## 🟡 Real Example Hindi mein
**Swiggy order history** में हर order का unique `orderId` है। `keyExtractor={o => o.orderId}` से नया order ऊपर जुड़ने पर पुराने orders सिर्फ नीचे खिसकते हैं, दोबारा render नहीं होते। **WhatsApp** में message `id` से key बनती है ताकि ✓✓ सही message पर बदले।

---

## 💻 Code Example — Basic
```jsx
// Basic: id से key बनाना
import React from 'react';                                           // React
import { FlatList, Text, View } from 'react-native';                 // components

const orders = [                                                     // demo data
  { orderId: 8841, name: 'Biryani' },
  { orderId: 8842, name: 'Pizza' },
];

export default function Orders() {
  return (
    <FlatList
      data={orders}                                                  // list data
      keyExtractor={(item) => String(item.orderId)}                  // key हमेशा STRING होनी चाहिए
      renderItem={({ item }) => (
        <View style={{ padding: 16 }}>
          <Text>#{item.orderId} — {item.name}</Text>                 {/* row content */}
        </View>
      )}
    />
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: मिश्रित types, id न होने पर safe key, duplicate-key detector
import React, { useCallback, useMemo } from 'react';
import { FlatList, Text, View } from 'react-native';

// type + id से key: 'ad' और 'order' के id टकराएँ तो भी key अलग रहे
const keyFor = (item, index) => {
  if (item?.type && item?.id != null) return `${item.type}_${item.id}`; // "ad_5", "order_5"
  if (item?.id != null) return String(item.id);                      // साधारण id
  // आख़िरी उपाय: stable hash (index नहीं, क्योंकि order बदलने पर key बदलेगी)
  return `fallback_${item?.title ?? 'x'}_${index}`;                   // सिर्फ तब जब कोई id न हो
};

export default function Mixed({ data }) {
  const keyExtractor = useCallback(keyFor, []);                      // stable function

  // dev mode में duplicate keys पकड़ो (duplicate → "same key" warning + glitches)
  useMemo(() => {
    if (!__DEV__) return;                                            // production में skip
    const seen = new Set();                                          // देखे हुए keys
    data.forEach((d, i) => {
      const k = keyFor(d, i);                                        // key निकालो
      if (seen.has(k)) console.warn('Duplicate key:', k);            // duplicate चेतावनी
      seen.add(k);                                                   // जोड़ो
    });
  }, [data]);

  return (
    <FlatList
      data={data}
      keyExtractor={keyExtractor}
      renderItem={({ item }) => (
        <View style={{ padding: 12 }}>
          <Text>{item.type === 'ad' ? 'Ad: ' : ''}{item.title}</Text>
        </View>
      )}
    />
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| API behaviour | Same | Same |
| Wrong/duplicate key effect | Rows glitch/duplicate, state mix | Same |
| Cell recycling | RN में नहीं (FlashList में है) | नहीं (native recycling UITableView जैसा नहीं) |
| Warning | Dev-mode yellow box / LogBox | Same |

Key React का concept है, native platform से मुक्त।

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// वही core prop। FlashList में भी keyExtractor ऐच्छिक है
<FlatList data={d} keyExtractor={(i) => i.id} renderItem={r} />
```
CLI way:
```jsx
// कोई अंतर नहीं
<FlatList data={d} keyExtractor={(i) => i.id} renderItem={r} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `keyExtractor={(_, index) => index}` (number लौटाना भी ग़लत है)।
✅ Correct: `String(item.id)`; key string होनी चाहिए।

❌ Mistake 2: Duplicate ids (दो items का एक id)।
✅ Correct: Unique composite key: `${type}_${id}`।

❌ Mistake 3: `Math.random()` / `Date.now()` key।
✅ Correct: हर render पर key बदलेगी → हर row remount। Stable id दो।

❌ Mistake 4: Data में `id` है ही नहीं और बिना key छोड़ देना।
✅ Correct: Data लाते समय id जोड़ो (uuid) या natural unique field इस्तेमाल करो।

---

## 🧠 Tricky Interview Question
"List की हर row में `TextInput` है और key = index है। Item #0 delete करने पर बचे हुए items में text ग़लत जगह क्यों दिखता है?"

Answer: Delete के बाद पुराना item #1 अब index 0 पर है और उसकी key `0` हो गई। React key `0` की पुरानी row (पुराने item #0 का component और उसकी internal TextInput state) reuse करता है, इसलिए नया data पुरानी state के साथ मिल जाता है। Stable unique id key बनाओ।

---

## ⚫ Interview Questions + Answers
Q1: keyExtractor न दें तो क्या होगा?
A1: FlatList पहले `item.key`, फिर `item.id` इस्तेमाल करता है; दोनों न हों तो index और warning।

Q2: Key string क्यों होनी चाहिए?
A2: VirtualizedList key को string की तरह इस्तेमाल करता है (cell tracking में); number लौटाने पर warning/ग़लत व्यवहार संभव। `String()` सुरक्षित है।

Q3: Index key कब ठीक है?
A3: जब list static हो, कभी reorder/insert/delete न हो और rows में state न हो।

Q4: keyExtractor में performance cost?
A4: हर item पर चलता है, इसलिए हल्का रखो और `useCallback` से stable function दो।

Q5: Duplicate key का नतीजा?
A5: Warning, rows का duplicate/ग़ायब दिखना, state mix।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर FlatList/SectionList में (हमेशा)
- Data बदल सकता है: add/remove/reorder

❌ Avoid when:
- Index key — सिर्फ पूरी तरह static list में
- Random/time-based keys — कभी नहीं

---

## 📊 Visual Diagram
```
 data: [A(id1), B(id2), C(id3)]   key = id
 A हटाओ →  [B(id2), C(id3)]  → React: id1 unmount, id2/id3 वही rows ✅

 key = index:
 [A(0), B(1), C(2)] → A हटाओ → [B(0), C(1)]
 React: key0 की row अब B दिखाए, key2 unmount → state mix ❌
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| key | Identity of an element in a list | List element की पहचान |
| Reconciliation | React diffing | React का तुलना-प्रक्रिया |
| Stable | Same across renders | हर render में समान |
| Composite key | Built from many fields | कई fields से बनी key |
| Remount | Destroy and recreate | नष्ट करके फिर बनाना |

---

## ⚡ 3-Line Summary
English: keyExtractor returns a unique, stable string key per row. It lets React reuse and move rows correctly. Never use random values; avoid index in dynamic lists.
Hindi: keyExtractor हर row की unique, stable string key देता है। इससे React rows को सही reuse और move करता है। Random values कभी नहीं; dynamic list में index से बचो।

---

## ➡️ Next Topic
**162. removeClippedSubviews** — स्क्रीन से बाहर की native views हटाकर memory बचाना।
