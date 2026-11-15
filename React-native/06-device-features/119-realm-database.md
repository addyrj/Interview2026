# 119. Realm Database
# हिंदी में: Realm Database — Object-based Local Database
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** Libraries: `realm` + `@realm/react`। Realm में native code है, इसलिए **Expo Go में नहीं चलता**, development build (`expo prebuild` / EAS) चाहिए। ध्यान दें: MongoDB ने Atlas Device Sync / Realm SDKs की deprecation घोषित की है; local-only Realm अभी भी काम करता है, पर नए project में यह जोखिम सोचकर चुनें। Version-dependent: नए RN architecture की support के लिए `realm` का latest version docs में देखो।

---

## 🔵 Simple Definition (English)
**Realm** is an object database for mobile. You define classes (schemas), save JS objects directly, and query them without writing SQL. Results are **live**: when data changes, your UI updates automatically.

## 🔵 सरल परिभाषा (Hindi)
**Realm** mobile के लिए object database है। आप classes (schema) बनाते हैं, JS objects सीधे save करते हैं और SQL लिखे बिना query करते हैं। Results **live** रहते हैं: data बदलते ही UI अपने आप update हो जाती है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  SQLite में rows को बार-बार objects में बदलना (mapping).
  Data बदले तो हाथ से UI refresh करना.

REALM:
  ✅ Objects सीधे store (कोई ORM mapping नहीं)
  ✅ Live queries -> UI auto-update (useQuery)
  ✅ तेज़ (zero-copy lazy loading)
  ✅ Relations (links) और encryption support
```

## 🔴 यह क्यों बना? (Hindi)
SQLite में rows को बार-बार objects में बदलना पड़ता है और data बदलने पर UI खुद refresh करनी पड़ती है। Realm objects सीधे रखता है और live queries देता है, इसलिए code कम और UI अपने आप sync रहती है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install realm @realm/react expo-build-properties (dev build ज़रूरी)
Step 2 → Schema class बनाओ (static schema = {name, properties, primaryKey})
Step 3 → <RealmProvider schema={[Task]}> से app wrap करो
Step 4 → useRealm() से realm, useQuery(Task) से live list
Step 5 → Writes हमेशा realm.write(() => { realm.create(...) }) के अंदर
Step 6 → Data बदलते ही useQuery वाला component अपने आप re-render
Step 7 → Schema बदलो तो schemaVersion बढ़ाओ + migration
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → realm और @realm/react install करो (dev build चाहिए)
Step 2 → Schema class बनाओ
Step 3 → RealmProvider से app wrap करो
Step 4 → useRealm और useQuery से live data
Step 5 → Writes realm.write() के अंदर ही
Step 6 → Data बदलने पर UI अपने आप update
Step 7 → Schema बदलने पर schemaVersion बढ़ाओ
```

---

## 🟡 Real World Example
**Food delivery / to-do जैसे apps** में cart items और tasks Realm में रखे जा सकते हैं: cart में item add करते ही cart badge अपने आप बदल जाता है। Offline-first apps (field-sales, डिलीवरी ऐप) में Realm का live updates वाला व्यवहार सुविधाजनक है। (यह generic उदाहरण है, किसी कंपनी के internal stack का दावा नहीं।)

## 🟡 Real Example Hindi mein
Food delivery जैसे app में cart items Realm में हों तो item जोड़ते ही cart badge अपने आप बदल जाता है। Offline-first apps में live queries से UI हमेशा data के साथ sync रहती है।

---

## 💻 Code Example — Basic
```jsx
// RealmBasic.jsx — Task list with live query
import React from 'react';                                          // React
import { View, Text, Button, FlatList } from 'react-native';        // UI
import Realm from 'realm';                                          // Realm core
import { RealmProvider, useRealm, useQuery } from '@realm/react';   // React bindings

class Task extends Realm.Object {                                   // schema class
  static schema = {                                                 // schema definition
    name: 'Task',                                                   // table नाम
    primaryKey: '_id',                                              // primary key
    properties: {                                                   // columns
      _id: 'objectId',                                              // unique id type
      title: 'string',                                              // title
      done: { type: 'bool', default: false },                       // default false
    },                                                              // properties खत्म
  };                                                                // schema खत्म
}                                                                   // class खत्म

function TaskList() {                                               // screen
  const realm = useRealm();                                         // DB handle
  const tasks = useQuery(Task);                                     // live list: बदलते ही re-render

  const add = () => {                                               // add
    realm.write(() => {                                             // write transaction ज़रूरी
      realm.create(Task, { _id: new Realm.BSON.ObjectId(), title: 'Task ' + (tasks.length + 1) }); // object बनाओ
    });                                                             // write खत्म
  };                                                                // खत्म

  return (                                                          // UI
    <View style={{ flex: 1, padding: 24 }}>{/* container */}
      <Button title="Add task" onPress={add} />{/* add */}
      <FlatList data={tasks} keyExtractor={(t) => t._id.toHexString()} renderItem={({ item }) => <Text>{item.title}</Text>} />{/* list */}
    </View>
  );                                                                // return खत्म
}                                                                   // TaskList खत्म

export default function App() {                                     // root
  return (<RealmProvider schema={[Task]}><TaskList /></RealmProvider>); // provider
}                                                                   // खत्म
```

## 💻 Code Example — Advanced
```jsx
// RealmAdvanced.jsx — filtered/sorted query, update, delete, migration, encryption key
import React, { useMemo } from 'react';                             // hooks
import { View, Text, Pressable, FlatList, StyleSheet } from 'react-native'; // UI
import Realm from 'realm';                                          // core
import { RealmProvider, useRealm, useQuery } from '@realm/react';   // bindings

class Task extends Realm.Object {                                   // schema v2
  static schema = {                                                 // schema
    name: 'Task', primaryKey: '_id',                                // नाम + key
    properties: {                                                   // fields
      _id: 'objectId', title: 'string', done: { type: 'bool', default: false }, // पहले वाले
      priority: { type: 'int', default: 1 },                        // v2 में जोड़ा गया field
    },                                                              // खत्म
  };                                                                // खत्म
}                                                                   // class खत्म

// Migration: schemaVersion बढ़ने पर चलता है
const onMigration = (oldRealm, newRealm) => {                       // दो realms मिलते हैं
  if (oldRealm.schemaVersion < 2) {                                 // v1 से आ रहे users
    newRealm.objects('Task').forEach((t) => { t.priority = 1; });   // पुराने tasks को default priority
  }                                                                 // if खत्म
};                                                                  // खत्म

function Tasks() {                                                  // screen
  const realm = useRealm();                                         // handle
  // Live query: अधूरे tasks, priority घटते क्रम में
  const open = useQuery(Task, (c) => c.filtered('done == false').sorted('priority', true), []); // query + deps

  const toggle = (t) => realm.write(() => { t.done = !t.done; });   // managed object बदलो = update
  const remove = (t) => realm.write(() => { realm.delete(t); });    // delete

  return (                                                          // UI
    <FlatList data={open} keyExtractor={(t) => t._id.toHexString()} renderItem={({ item }) => ( // list
      <Pressable style={s.row} onPress={() => toggle(item)} onLongPress={() => remove(item)}>{/* tap=done, long press=delete */}
        <Text>{item.title} (P{item.priority})</Text>{/* text */}
      </Pressable>
    )} />
  );                                                                // return खत्म
}                                                                   // खत्म

export default function App() {                                     // root
  // Production: key को SecureStore से लो (64 bytes); यहाँ demo के लिए undefined
  const encryptionKey = undefined;                                  // Int8Array(64) हो सकता है
  return (                                                          // provider config
    <RealmProvider schema={[Task]} schemaVersion={2} onMigration={onMigration} encryptionKey={encryptionKey}>
      <Tasks />{/* screen */}
    </RealmProvider>
  );                                                                // return खत्म
}                                                                   // खत्म

const s = StyleSheet.create({ row: { padding: 16, borderBottomWidth: 1, borderColor: '#eee' } }); // style
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native engine | Realm Core (JNI) | Realm Core (Swift/ObjC bridge) |
| Expo Go | ❌ | ❌ (dev build ज़रूरी) |
| Setup | Gradle/NDK auto (Expo prebuild) | `pod install` auto |
| File location | App internal storage | App Documents |
| Hermes | Supported | Supported |
| Encryption | 64-byte key, AES-256 | वही |
| Binary size | App size बढ़ता है (~कई MB) | वही |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: dev build बनाओ (Expo Go में नहीं चलेगा)
// npx expo install realm @realm/react expo-build-properties
// npx expo prebuild   # या eas build --profile development
import { RealmProvider } from '@realm/react';              // वही API
```
CLI way:
```jsx
// CLI: npm i realm @realm/react; cd ios && pod install
import { RealmProvider } from '@realm/react';              // वही API
// Android: कोई अतिरिक्त manifest config आम तौर पर नहीं
// Babel: @babel/plugin-proposal-decorators सिर्फ तब जब decorators-style schema use करो
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `realm.create` या property बदलना `realm.write` के बाहर।
✅ Correct: हमेशा `realm.write(() => {...})` में।

❌ Mistake 2: Realm object को state/redux में रखना या thread/render के बाद पकड़े रखना।
✅ Correct: `useQuery` से लो; ज़रूरत पर plain object में बदलो (`toJSON()`)।

❌ Mistake 3: Schema बदलकर `schemaVersion` न बढ़ाना।
✅ Correct: version बढ़ाओ और `onMigration` लिखो।

❌ Mistake 4: Expo Go में चलाना।
✅ Correct: Development build।

---

## 🧠 Tricky Interview Question
```jsx
const tasks = useQuery(Task);
realm.write(() => { realm.create(Task, {...}); });
console.log(tasks.length);   // इसी line पर
```
`length` नई value दिखाएगा या पुरानी?

Answer: Realm collections live हैं, इसलिए write commit होते ही `tasks.length` में नई गिनती दिखती है। पर component का re-render अगले render cycle में होता है; इसलिए JSX में नई value बाद में दिखेगी। (Live होने का मतलब snapshot नहीं; loop में delete करते समय `.snapshot()` लेना चाहिए।)

---

## ⚫ Interview Questions + Answers
Q1: Realm vs SQLite?
A1: Realm object database है (SQL नहीं), live queries और कम boilerplate; SQLite SQL, ज़्यादा व्यापक tooling और स्थिर ecosystem।

Q2: Live objects का क्या मतलब?
A2: Query results और objects DB से जुड़े रहते हैं; बदलने पर auto-update।

Q3: Primary key क्या?
A3: Unique field (`_id`) जिससे object पहचाना और upsert होता है।

Q4: Encryption कैसे?
A4: 64-byte key से AES-256; key को SecureStore में रखो।

Q5: Sustainability जोखिम?
A5: MongoDB ने Device Sync/SDK deprecation बताई है; local-only उपयोग चलता है पर लंबी अवधि के लिए SQLite/WatermelonDB से तुलना करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reactive UI + local data
- Objects/relations ज़्यादा, SQL कम
- Dev build का उपयोग हो रहा है

❌ Avoid when:
- Expo Go ही चाहिए
- Long-term vendor risk नहीं लेना
- Complex SQL joins/reporting

---

## 📊 Visual Diagram
```
 RealmProvider (schema)
      |
  useQuery(Task) <------ live updates ------+
      |                                      |
   UI list                           realm.write(() => ...)
      ^                                      |
      +-------- auto re-render --------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Object structure | Object की बनावट |
| Live query | Auto-updating results | अपने-आप बदलने वाले results |
| realm.write | Transaction block | Write transaction |
| schemaVersion | Version for migration | Migration के लिए version |
| ObjectId | Unique id type | Unique पहचान |

---

## ⚡ 3-Line Summary
English: Realm stores objects directly and gives live queries that update the UI.
All writes go inside realm.write, and schema changes need schemaVersion and migration.
It needs a development build and has vendor-roadmap risk to consider.

Hindi: Realm objects सीधे रखता है और live queries से UI update करता है।
सभी writes realm.write में होते हैं और schema बदलने पर schemaVersion व migration चाहिए।
इसे development build चाहिए और vendor roadmap का जोखिम भी देखें।

---

## ➡️ Next Topic
**120. WatermelonDB**, बड़े offline-first apps के लिए तेज़ reactive database (SQLite के ऊपर)।
