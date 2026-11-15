# 101. Contacts — expo-contacts
# हिंदी में: Contacts — फ़ोन की संपर्क सूची पढ़ना और जोड़ना
# Platform: Android ✅ | iOS ✅ | Both ✅ (Web ❌)

> Target: Expo SDK 52 (React Native 0.76) + `expo-contacts` (check current docs — APIs change between SDKs). Expo Go में चलता है, पर iOS पर पूरा contacts access limited हो सकता है (iOS 18 "limited access"), इसलिए dev build पर test करें।

---

## 🔵 Simple Definition (English)
**expo-contacts** gives read/write access to the phone's address book. You can list contacts (name, phone, email), search them, add a new one, or show the system contact form — after the user grants permission.

## 🔵 सरल परिभाषा (Hindi)
**expo-contacts** फ़ोन की address book को पढ़ने/लिखने का access देता है। User की permission के बाद आप contacts की list (नाम, फ़ोन, email) निकाल सकते हैं, खोज सकते हैं, नया contact जोड़ सकते हैं, या system का contact form दिखा सकते हैं।

---

## 🔴 Problem it Solves
```
❌ Friend ko invite / paise bhejne ke liye number haath se type karna
❌ Native Contacts API (Android ContentResolver, iOS CNContactStore) alag-alag
✅ Ek JS API: getContactsAsync, addContactAsync, presentFormAsync
```

## 🔴 यह क्यों बना? (Hindi)
```
हर बार दोस्त का नंबर हाथ से भरना धीमा है।
Android और iOS के native contacts APIs बिलकुल अलग हैं।
expo-contacts एक ही JS API देता है जो दोनों पर चलता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-contacts
Step 2 → app.json plugin: ["expo-contacts", { "contactsPermission": "..." }]
Step 3 → Contacts.requestPermissionsAsync() -> status 'granted'
Step 4 → Contacts.getContactsAsync({ fields: [Fields.Name, Fields.PhoneNumbers], pageSize })
Step 5 → result.data = [{ id, name, phoneNumbers: [{ number, label }] }]
Step 6 → addContactAsync({...}) ya presentFormAsync() se naya contact
Step 7 → Bade list ke liye pageSize + pageOffset (pagination) use karo
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Package और plugin जोड़ें, iOS के लिए permission text लिखें।
Step 2 → requestPermissionsAsync से अनुमति लें।
Step 3 → getContactsAsync में fields बताएँ (सिर्फ़ वही जो चाहिए)।
Step 4 → data array में contacts मिलते हैं; बड़े फ़ोन में pagination करें।
```

---

## 🟡 Real World Example
**Paytm / PhonePe / Google Pay:** "Pay Contacts" screen lists your phone contacts to send money by name. **Swiggy / Zomato:** "Refer a friend" lets you pick contacts to share your invite code. **WhatsApp:** shows which contacts are on WhatsApp (matches numbers on server).

## 🟡 Real Example Hindi mein
**Paytm / PhonePe:** "Pay Contacts" में आपके फ़ोन के contacts नाम से दिखते हैं ताकि पैसे भेज सकें। **Swiggy / Zomato:** "Refer a friend" में contacts चुनकर invite code शेयर होता है। **WhatsApp:** पता करता है कौन से contacts WhatsApp पर हैं।

---

## 💻 Code Example — Basic
```jsx
// ContactsBasic.jsx — permission lekar contacts ki list dikhao
import React, { useEffect, useState } from 'react';                    // React + hooks
import { View, Text, FlatList } from 'react-native';                   // RN UI
import * as Contacts from 'expo-contacts';                             // contacts API

export default function ContactsBasic() {
  const [list, setList] = useState([]);                                // contacts state
  const [msg, setMsg] = useState('Loading...');                        // status message

  useEffect(() => {
    (async () => {
      const { status } = await Contacts.requestPermissionsAsync();     // permission maango
      if (status !== 'granted') { setMsg('Permission nahi mili'); return; } // deny case
      const { data } = await Contacts.getContactsAsync({               // contacts lao
        fields: [Contacts.Fields.Name, Contacts.Fields.PhoneNumbers],  // sirf zaroori fields
      });
      setList(data);                                                   // state me rakho
      setMsg(data.length ? '' : 'Koi contact nahi');                   // empty message
    })();
  }, []);                                                              // sirf mount par

  return (
    <View style={{ flex: 1, padding: 16 }}>
      {msg ? <Text>{msg}</Text> : null}
      <FlatList
        data={list}                                                    // contacts
        keyExtractor={(c) => c.id}                                     // unique id
        renderItem={({ item }) => (
          <Text>{item.name} — {item.phoneNumbers?.[0]?.number ?? 'no number'}</Text>
        )}
      />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// useContacts.js — pagination + search + add contact + error handling
import { useCallback, useState } from 'react';
import { Platform } from 'react-native';
import * as Contacts from 'expo-contacts';

const PAGE = 50;                                                       // ek baar me 50

export function useContacts() {
  const [items, setItems] = useState([]);                              // loaded contacts
  const [hasNext, setHasNext] = useState(true);                        // aur data hai?
  const [loading, setLoading] = useState(false);                       // duplicate fetch roko
  const [error, setError] = useState(null);                            // error message

  const loadMore = useCallback(async () => {
    if (loading || !hasNext) return;                                   // guard
    setLoading(true);
    try {
      const { granted } = await Contacts.requestPermissionsAsync();    // permission
      if (!granted) throw new Error('Contacts permission denied');
      const res = await Contacts.getContactsAsync({
        fields: [Contacts.Fields.Name, Contacts.Fields.PhoneNumbers, Contacts.Fields.Emails],
        pageSize: PAGE,                                                // page size
        pageOffset: items.length,                                      // kahan se aage
        sort: Contacts.SortTypes.FirstName,                            // naam se sort
      });
      setItems((prev) => [...prev, ...res.data]);                      // append
      setHasNext(res.hasNextPage);                                     // aur pages?
    } catch (e) {
      setError(e.message);                                             // UI me dikhao
    } finally {
      setLoading(false);                                               // hamesha band
    }
  }, [items.length, loading, hasNext]);

  const search = useCallback(async (text) => {                         // naam se khojo
    const { data } = await Contacts.getContactsAsync({ name: text });  // name filter
    setItems(data); setHasNext(false);
  }, []);

  const addFriend = useCallback(async (name, phone) => {               // naya contact
    const id = await Contacts.addContactAsync({
      contactType: Contacts.ContactTypes.Person,                       // person
      name,                                                            // full name
      firstName: name,                                                 // first name
      phoneNumbers: [{ label: 'mobile', number: phone }],              // number
    });
    return id;                                                         // naya id
  }, []);

  // System ka built-in form (user khud save kare) — bahut platforms par safe
  const openForm = useCallback(() => Contacts.presentFormAsync(null, null, { isNew: Platform.OS === 'ios' ? true : undefined }), []);

  return { items, loading, error, hasNext, loadMore, search, addFriend, openForm };
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | `READ_CONTACTS` / `WRITE_CONTACTS` | `NSContactsUsageDescription` (Expo plugin `contactsPermission`) |
| Limited access | Not applicable | iOS 18: user can share only selected contacts |
| `presentFormAsync` | Opens system editor | Opens `CNContactViewController` |
| Account source | Google/SIM/local accounts mix | iCloud / local |
| Some fields (note) | Available | `Fields.Note` needs special entitlement on iOS 13+ |
| Pagination | Supported | Supported |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-contacts ; app.json plugins: [["expo-contacts", { "contactsPermission": "Doston ko invite karne ke liye" }]]
import * as Contacts from 'expo-contacts';                              // JS same
const { data } = await Contacts.getContactsAsync({ fields: [Contacts.Fields.Name] });
```
CLI way:
```jsx
// npm i react-native-contacts ; Android: READ_CONTACTS in manifest ; iOS: NSContactsUsageDescription in Info.plist
import Contacts from 'react-native-contacts';                           // alag library, alag API
await Contacts.requestPermission();                                     // permission
const all = await Contacts.getAll();                                    // sab contacts
// (ya Expo project me bhi expo-contacts use kar sakte ho, expo modules install karke)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Permission के बिना `getContactsAsync` बुलाना।
✅ Correct: `requestPermissionsAsync()` की `granted` जाँचें।

❌ Mistake 2: सारे fields और हज़ारों contacts एक साथ लाना (slow, memory)।
✅ Correct: सिर्फ़ ज़रूरी `fields`, `pageSize` + `pageOffset`।

❌ Mistake 3: iOS permission text न देना।
✅ Correct: plugin में `contactsPermission` लिखें।

❌ Mistake 4: `phoneNumbers` को हमेशा मौजूद मानना।
✅ Correct: `item.phoneNumbers?.[0]?.number` optional chaining।

❌ Mistake 5: Contacts server पर बिना बताए upload करना (privacy / Play-Store policy)।
✅ Correct: कारण बताएँ, hash करें, user की सहमति लें।

---

## 🧠 Tricky Interview Question
`getContactsAsync()` is called with no `fields`. You render `item.phoneNumbers[0].number`. What happens?

Answer: Only the base fields (like `id`, `name`) come back; `phoneNumbers` is `undefined` because it was not requested, so the app crashes with "cannot read property '0' of undefined". Fix: request `Contacts.Fields.PhoneNumbers` and use optional chaining.

हिंदी: `fields` न दें तो `phoneNumbers` आता ही नहीं, इसलिए `undefined[0]` पर crash होता है। Fields माँगें और `?.` इस्तेमाल करें।

---

## ⚫ Interview Questions + Answers
Q1: Contacts कैसे paginate करें?
A1: `pageSize` + `pageOffset` दें और `hasNextPage` देखें।

Q2: iOS पर permission text कहाँ लिखते हैं?
A2: `NSContactsUsageDescription`; Expo में plugin option `contactsPermission`।

Q3: नया contact जोड़ने के दो तरीके?
A3: `addContactAsync` (सीधे) और `presentFormAsync` (system form, user save करता है)।

Q4: Contact data private क्यों है?
A4: यह third-party लोगों का personal data है; Play Store/App Store policies में स्पष्ट consent और कारण ज़रूरी है।

Q5: Contact को नाम से कैसे खोजें?
A5: `getContactsAsync({ name: 'Raj' })`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Invite / refer / pay-to-contact flows
- Contact picker, import contacts
- Dialer-like utility apps

❌ Avoid when:
- सिर्फ़ एक number चुनना है — system contact picker (`presentFormAsync`/native picker) कम invasive है
- बिना कारण full address book माँगना

---

## 📊 Visual Diagram
```
 requestPermissionsAsync() ──denied──▶ fallback (manual number entry)
          │ granted
          ▼
 getContactsAsync({ fields, pageSize, pageOffset })
          │
   Android ContentResolver  |  iOS CNContactStore
          ▼
 { data: [ {id, name, phoneNumbers[]} ], hasNextPage }
          │
   FlatList (onEndReached -> next page)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Address book | Phone's contacts store | फ़ोन की contact सूची |
| Fields | Which data to fetch | कौन सा डेटा लाना है |
| Pagination | Load in pages | हिस्सों में लोड |
| Limited access | iOS selected contacts only | चुने हुए contacts |
| presentFormAsync | System contact form | system का फ़ॉर्म |
| Consent | User's agreement | user की सहमति |

---

## ⚡ 3-Line Summary
English: expo-contacts reads and writes the phone's address book after permission.
Ask for only needed fields and paginate large lists.
Handle denied, limited access and privacy carefully.

Hindi: expo-contacts permission के बाद address book पढ़/लिख सकता है।
सिर्फ़ ज़रूरी fields माँगें और बड़ी list paginate करें।
Denied, limited access और privacy का ध्यान रखें।

---

## ➡️ Next Topic
**102. Calendar — expo-calendar** — device calendar में event / reminder बनाना।

---
