# 120. WatermelonDB
# हिंदी में: WatermelonDB — बड़े Offline-First Apps का Database
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** Library: `@nozbe/watermelondb`। Native code है, इसलिए Expo Go में नहीं; development build + config plugin (`@morrowdigital/watermelondb-expo-plugin`, community) और JSI/SQLite setup चाहिए। Version-dependent: setup steps WatermelonDB docs में देखो।

---

## 🔵 Simple Definition (English)
**WatermelonDB** is a reactive database built on top of SQLite for large React Native apps. It loads data **lazily** (only when needed), runs queries on a native thread, and updates components through observables. It also has a built-in **sync** protocol with your server.

## 🔵 सरल परिभाषा (Hindi)
**WatermelonDB** बड़े React Native apps के लिए SQLite के ऊपर बना reactive database है। यह data **lazily** (ज़रूरत पर) load करता है, queries native thread पर चलाता है और observables से components update करता है। Server के साथ built-in **sync** protocol भी है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  हज़ारों-लाखों records वाला app: सब कुछ JS memory में load -> app धीमा start.
  Redux + SQLite में हाथ से sync/refresh logic.

WATERMELONDB:
  ✅ Lazy loading: app launch तुरंत (record तभी load जब चाहिए)
  ✅ Native thread पर SQLite queries (JS thread free)
  ✅ Observable queries -> UI auto-update
  ✅ Built-in sync (pullChanges / pushChanges)
```

## 🔴 यह क्यों बना? (Hindi)
लाखों records में सब कुछ JS memory में load करने से app धीमा शुरू होता है। WatermelonDB records को ज़रूरत पर load करता है, queries native thread पर चलाता है और sync का standard तरीका देता है, इसलिए बड़े offline-first apps में तेज़ रहता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npm i @nozbe/watermelondb (+ dev build / native setup)
Step 2 → Schema (appSchema + tableSchema) और Model classes लिखो
Step 3 → SQLiteAdapter के साथ Database बनाओ
Step 4 → Writes हमेशा database.write(async () => { collection.create(...) })
Step 5 → Component को withObservables या hooks से query observe कराओ
Step 6 → Data बदले तो सिर्फ प्रभावित component re-render
Step 7 → synchronize({ pullChanges, pushChanges }) से server sync
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → library install करो और native setup करो
Step 2 → Schema और Model classes लिखो
Step 3 → SQLiteAdapter से Database बनाओ
Step 4 → Writes database.write() के अंदर
Step 5 → withObservables से query observe करो
Step 6 → बदलने पर सिर्फ संबंधित component re-render
Step 7 → synchronize से server sync
```

---

## 🟡 Real World Example
**Nozbe** (इसके बनाने वाले) जैसे बड़े task apps में बहुत सारे records होते हैं। भारतीय संदर्भ में सोचो: **Swiggy/Zomato** जैसे ऐप में restaurants, menu items, orders के लाखों records offline-first रखने हों, तो lazy-loading और sync वाला DB उपयोगी है। **Field-sales / retail POS apps** (हज़ारों products offline) इसके अच्छे उदाहरण हैं। (Illustrative उदाहरण; किसी कंपनी के internal stack का दावा नहीं।)

## 🟡 Real Example Hindi mein
हज़ारों products वाला retail POS app offline चलना चाहिए और बाद में server से sync हो, यहाँ WatermelonDB अच्छा है। Swiggy जैसे बड़े catalog में lazy loading से app तुरंत खुलता है (यह सिर्फ़ समझाने के लिए उदाहरण है)।

---

## 💻 Code Example — Basic
```jsx
// db/index.js — schema + model + database
import { Database, Model, appSchema, tableSchema } from '@nozbe/watermelondb';       // core
import SQLiteAdapter from '@nozbe/watermelondb/adapters/sqlite';                      // native adapter
import { field } from '@nozbe/watermelondb/decorators';                               // decorators

// Schema: tables और columns
export const schema = appSchema({                                                     // app schema
  version: 1,                                                                         // schema version
  tables: [                                                                           // tables
    tableSchema({                                                                     // posts table
      name: 'products',                                                               // table नाम
      columns: [                                                                      // columns
        { name: 'title', type: 'string' },                                            // string column
        { name: 'price', type: 'number' },                                            // number column
      ],                                                                              // columns खत्म
    }),                                                                               // table खत्म
  ],                                                                                  // tables खत्म
});                                                                                   // schema खत्म

// Model class: decorators के लिए Babel decorators plugin चाहिए (legacy)
export class Product extends Model {                                                  // model
  static table = 'products';                                                          // table से जोड़ो
  @field('title') title;                                                              // title field
  @field('price') price;                                                              // price field
}                                                                                     // model खत्म

const adapter = new SQLiteAdapter({ schema, jsi: true });                             // JSI = तेज़ (supported setup पर)
export const database = new Database({ adapter, modelClasses: [Product] });           // database
```
```jsx
// ProductList.jsx — observe + create
import React from 'react';                                                            // React
import { View, Text, Button, FlatList } from 'react-native';                          // UI
import { withObservables } from '@nozbe/watermelondb/react';                          // HOC
import { database } from './db';                                                      // database

const ProductList = ({ products }) => (                                               // plain component
  <View style={{ flex: 1, padding: 24 }}>{/* container */}
    <Button title="Add" onPress={() => database.write(async () => {                   // write block
      await database.get('products').create((p) => { p.title = 'Biryani'; p.price = 249; }); // record बनाओ
    })} />{/* add button */}
    <FlatList data={products} keyExtractor={(p) => p.id} renderItem={({ item }) => <Text>{item.title} ₹{item.price}</Text>} />{/* list */}
  </View>
);                                                                                    // खत्म

// observable query को prop बनाकर दो
const enhance = withObservables([], () => ({ products: database.get('products').query().observe() })); // live
export default enhance(ProductList);                                                  // export
```

## 💻 Code Example — Advanced
```jsx
// sync.js — server sync (pull then push) with error handling
import { synchronize } from '@nozbe/watermelondb/sync';                               // sync helper
import { database } from './db';                                                      // database

const API = 'https://api.example.com';                                                // तुम्हारा backend

export async function syncNow(token) {                                                // sync चलाओ
  try {                                                                               // error handling
    await synchronize({                                                               // sync call
      database,                                                                       // हमारा DB
      pullChanges: async ({ lastPulledAt, schemaVersion, migration }) => {            // server से बदलाव लाओ
        const res = await fetch(                                                      // API call
          `${API}/sync?last_pulled_at=${lastPulledAt ?? 0}&schema_version=${schemaVersion}`, // delta query
          { headers: { Authorization: `Bearer ${token}` } }                           // auth header
        );                                                                            // fetch खत्म
        if (!res.ok) throw new Error('Pull failed ' + res.status);                    // fail पर throw
        const { changes, timestamp } = await res.json();                              // {changes:{table:{created,updated,deleted}}, timestamp}
        return { changes, timestamp };                                                // यही format चाहिए
      },                                                                              // pull खत्म
      pushChanges: async ({ changes, lastPulledAt }) => {                             // local बदलाव भेजो
        const res = await fetch(`${API}/sync?last_pulled_at=${lastPulledAt}`, {       // POST
          method: 'POST',                                                             // method
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, // headers
          body: JSON.stringify(changes),                                              // changes
        });                                                                           // fetch खत्म
        if (!res.ok) throw new Error('Push failed ' + res.status);                    // fail पर throw
      },                                                                              // push खत्म
      migrationsEnabledAtVersion: 1,                                                  // schema migrations के साथ sync
    });                                                                               // synchronize खत्म
    return { ok: true };                                                              // सफल
  } catch (e) {                                                                       // network/server error
    return { ok: false, error: e.message };                                           // UI को बताओ, बाद में retry
  }                                                                                   // catch खत्म
}                                                                                     // function खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| JSI adapter | Supported (Hermes) | Supported |
| Native setup | Gradle में WatermelonDB package + Kotlin/Java setup docs के अनुसार | CocoaPods (`simdjson` pod docs के अनुसार) |
| Expo Go | ❌ | ❌ |
| Expo plugin | Community config plugin | Community config plugin |
| Storage | SQLite file | SQLite file |
| Debug | Android Studio / Flipper-alternatives | Xcode |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: dev build + community config plugin
// npm i @nozbe/watermelondb @morrowdigital/watermelondb-expo-plugin expo-build-properties
// app.json plugins में plugin जोड़ो (docs देखो), फिर: npx expo prebuild
import { Database } from '@nozbe/watermelondb';           // वही API
```
CLI way:
```jsx
// CLI: npm i @nozbe/watermelondb; cd ios && pod install
// Android: settings.gradle / MainApplication में package register (docs के अनुसार)
// Babel: ['@babel/plugin-proposal-decorators', { legacy: true }]
import { Database } from '@nozbe/watermelondb';           // वही API
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `create/update` को `database.write` के बाहर करना (error)।
✅ Correct: हमेशा `await database.write(async () => {...})`।

❌ Mistake 2: Decorators के लिए Babel plugin भूल जाना।
✅ Correct: `@babel/plugin-proposal-decorators` (legacy: true) जोड़ो।

❌ Mistake 3: Schema बदलकर version/migrations न देना।
✅ Correct: `schema.version` बढ़ाओ + `schemaMigrations`।

❌ Mistake 4: सारे records `.fetch()` करके array में लाना।
✅ Correct: `.observe()` और query conditions (`Q.where`)।

---

## 🧠 Tricky Interview Question
WatermelonDB में `database.get('products').query().fetch()` और `.observe()` में क्या फर्क है, और कब `fetch` ग़लत है?

Answer: `fetch()` एक बार की list देता है (snapshot) जो बाद में बदलाव पर अपडेट नहीं होती। `.observe()` Observable देता है जो हर बदलाव पर नई list emit करता है, इसलिए UI के लिए सही है। UI में `fetch` से state भरने पर data बदलने पर screen stale रहेगी; और बहुत बड़े table पर `fetch` सब कुछ memory में लाकर lazy-loading का फायदा खो देता है।

---

## ⚫ Interview Questions + Answers
Q1: WatermelonDB क्यों तेज़ है?
A1: Lazy loading, native thread पर SQLite और JSI adapter।

Q2: SQLite से इसका संबंध?
A2: यह SQLite के ऊपर की layer है; storage SQLite ही है।

Q3: Sync कैसे काम करता है?
A3: `pullChanges` (server से delta) और `pushChanges` (local बदलाव) के साथ `synchronize()`, `lastPulledAt` timestamp से।

Q4: `withObservables` क्या करता है?
A4: Observable queries को component props से जोड़ता है ताकि डेटा बदलने पर component re-render हो।

Q5: Realm और Watermelon में चुनाव?
A5: Realm: आसान API, पर vendor जोखिम; Watermelon: बहुत बड़े offline-first और custom sync के लिए, पर setup ज़्यादा।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हज़ारों-लाखों records, offline-first
- Server sync चाहिए
- Reactive UI चाहिए

❌ Avoid when:
- छोटा app / कुछ दर्जन records (expo-sqlite काफी)
- Expo Go ही उपयोग करना है
- Team को setup/maintenance का समय नहीं

---

## 📊 Visual Diagram
```
 UI (withObservables)  <--- observe() --- Database
        |                                    |
   database.write()  ------------------>  SQLiteAdapter (JSI)
                                             |
                                          SQLite file
 Sync:  Server <-- pullChanges / pushChanges --> Database
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lazy loading | Load only when needed | ज़रूरत पर ही load |
| Observable | Stream of updates | बदलावों की धारा |
| Model | Class for a table row | Row की class |
| Adapter | Storage connector | Storage से जोड़ने वाली layer |
| Sync | Align local & server | Local और server मिलाना |

---

## ⚡ 3-Line Summary
English: WatermelonDB is a lazy, reactive layer over SQLite for large offline-first apps.
Writes go inside database.write, and UI observes queries with observables.
It has built-in sync but needs a development build and more setup.

Hindi: WatermelonDB बड़े offline-first apps के लिए SQLite के ऊपर lazy, reactive layer है।
Writes database.write में होते हैं और UI observables से queries देखती है।
इसमें built-in sync है पर development build और ज़्यादा setup चाहिए।

---

## ➡️ Next Topic
**121. Animations in React Native**, अब storage से हटकर UI में गति (animation) की दुनिया शुरू करेंगे।
