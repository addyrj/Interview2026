# 118. SQLite in React Native
# हिंदी में: React Native में SQLite Database
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** Library: `expo-sqlite`। SDK 52 में नया async API (`openDatabaseAsync`, `runAsync`, `getAllAsync`) है। पुराना `openDatabase` (WebSQL-style) SDK 52 में हटाया गया है। CLI में `react-native-sqlite-storage` / `op-sqlite` common हैं।

---

## 🔵 Simple Definition (English)
**SQLite** is a small SQL database that lives inside your app as a single file on the phone. You create tables, insert rows and run queries with normal SQL. It works offline and handles thousands of rows far better than AsyncStorage.

## 🔵 सरल परिभाषा (Hindi)
**SQLite** एक छोटा SQL database है जो phone में एक file के रूप में आपके app के अंदर रहता है। आप tables बनाते हैं, rows डालते हैं और SQL queries चलाते हैं। यह offline चलता है और हज़ारों rows AsyncStorage से कहीं बेहतर संभालता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  AsyncStorage = key-value, पूरा JSON एक साथ load.
  10,000 orders में "पिछले महीने के orders" खोजना = बहुत धीमा.
  Relations (user -> orders -> items) नहीं.

SQLITE:
  ✅ Tables, indexes, joins, WHERE, ORDER BY
  ✅ Transactions (सब या कुछ नहीं)
  ✅ Offline-first apps
  ✅ Migrations (schema version)
```

## 🔴 यह क्यों बना? (Hindi)
AsyncStorage सिर्फ key-value है और पूरा JSON एक साथ load करता है। हज़ारों orders में filter/sort धीमा और जटिल हो जाता है। SQLite SQL, indexes और transactions देता है, इसलिए offline apps के structured data के लिए सही है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-sqlite
Step 2 → const db = await SQLite.openDatabaseAsync('app.db')   (file बनती/खुलती है)
Step 3 → db.execAsync('CREATE TABLE IF NOT EXISTS ...')        (schema)
Step 4 → db.runAsync('INSERT ... VALUES (?, ?)', [a, b])       (? से SQL injection से बचाव)
Step 5 → db.getAllAsync('SELECT ...', [params])                (rows की array)
Step 6 → बहु-step काम db.withTransactionAsync(async () => {...}) में
Step 7 → App update पर PRAGMA user_version से migration
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → expo-sqlite install करो
Step 2 → openDatabaseAsync से database file खोलो
Step 3 → execAsync से table बनाओ
Step 4 → runAsync में ? placeholders से insert/update
Step 5 → getAllAsync से rows पढ़ो
Step 6 → कई writes transaction में रखो
Step 7 → App update पर user_version से migration
```

---

## 🟡 Real World Example
**Zomato/Swiggy** पिछले orders और saved addresses offline cache के लिए local DB रखते हैं ताकि network न हो तब भी "Past orders" दिखें। **WhatsApp** messages SQLite में रखता है (native SQLite)। **Notes/To-do apps** (Google Keep जैसे) local data के लिए SQLite use करते हैं।

## 🟡 Real Example Hindi mein
Swiggy network न होने पर भी पुराने orders दिखाता है क्योंकि वे local DB में cached हैं। WhatsApp के messages SQLite में रहते हैं। Notes apps local data के लिए SQLite लेते हैं।

---

## 💻 Code Example — Basic
```jsx
// SqliteBasic.jsx — notes table: add + list
import React, { useEffect, useState } from 'react';                 // hooks
import { View, Text, Button, FlatList } from 'react-native';        // UI
import * as SQLite from 'expo-sqlite';                              // npx expo install expo-sqlite

export default function SqliteBasic() {                             // component
  const [db, setDb] = useState(null);                               // database handle
  const [notes, setNotes] = useState([]);                           // rows

  useEffect(() => {                                                 // mount पर
    (async () => {                                                  // async setup
      const d = await SQLite.openDatabaseAsync('notes.db');         // DB file खोलो
      await d.execAsync(                                            // table बनाओ
        'CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL);'
      );                                                            // execAsync खत्म
      setDb(d);                                                     // handle रखो
      setNotes(await d.getAllAsync('SELECT * FROM notes ORDER BY id DESC')); // rows लाओ
    })();                                                           // run
  }, []);                                                           // एक बार

  const add = async () => {                                         // नया note
    if (!db) return;                                                // DB तैयार नहीं
    await db.runAsync('INSERT INTO notes (title) VALUES (?)', ['Note ' + Date.now()]); // ? से safe insert
    setNotes(await db.getAllAsync('SELECT * FROM notes ORDER BY id DESC'));            // refresh
  };                                                                // खत्म

  return (                                                          // UI
    <View style={{ flex: 1, padding: 24 }}>{/* container */}
      <Button title="Add note" onPress={add} />{/* add */}
      <FlatList data={notes} keyExtractor={(n) => String(n.id)} renderItem={({ item }) => <Text>{item.id}. {item.title}</Text>} />{/* list */}
    </View>
  );                                                                // return खत्म
}                                                                   // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// db.js — SQLiteProvider + migrations + transaction + typed repo (Expo SDK 52)
import React from 'react';                                          // React
import { SQLiteProvider, useSQLiteContext } from 'expo-sqlite';     // provider + hook
import { View, Text, Button, FlatList } from 'react-native';        // UI

const DB_VERSION = 2;                                               // schema version

// Migration function: provider इसे DB खुलते ही चलाता है
async function migrate(db) {                                        // db handle मिलता है
  const row = await db.getFirstAsync('PRAGMA user_version');        // मौजूदा version
  let v = row?.user_version ?? 0;                                   // null-safe
  if (v >= DB_VERSION) return;                                      // पहले से latest
  if (v === 0) {                                                    // v0 -> v1
    await db.execAsync(`
      PRAGMA journal_mode = WAL;
      CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT NOT NULL, qty INTEGER NOT NULL);
    `);                                                             // WAL = तेज़ concurrent reads
    v = 1;                                                          // version बढ़ाओ
  }                                                                 // if खत्म
  if (v === 1) {                                                    // v1 -> v2
    await db.execAsync('ALTER TABLE orders ADD COLUMN status TEXT DEFAULT "new";'); // नया column
    v = 2;                                                          // version बढ़ाओ
  }                                                                 // if खत्म
  await db.execAsync(`PRAGMA user_version = ${DB_VERSION}`);        // version save
}                                                                   // migrate खत्म

function Orders() {                                                 // DB use करने वाला screen
  const db = useSQLiteContext();                                    // context से handle
  const [rows, setRows] = React.useState([]);                       // rows state

  const load = React.useCallback(async () => {                      // लोड
    setRows(await db.getAllAsync('SELECT * FROM orders ORDER BY id DESC')); // सब orders
  }, [db]);                                                         // db dependency

  React.useEffect(() => { load(); }, [load]);                       // mount पर लोड

  const addTwo = async () => {                                      // transaction example
    try {                                                           // error handling
      await db.withTransactionAsync(async () => {                   // सब या कुछ नहीं
        await db.runAsync('INSERT INTO orders (item, qty) VALUES (?, ?)', ['Biryani', 1]); // पहला
        await db.runAsync('INSERT INTO orders (item, qty) VALUES (?, ?)', ['Raita', 2]);   // दूसरा
      });                                                           // error आए तो दोनों rollback
      await load();                                                 // refresh
    } catch (e) {                                                   // fail
      console.warn('tx failed', e.message);                         // log
    }                                                               // catch खत्म
  };                                                                // खत्म

  return (                                                          // UI
    <View style={{ flex: 1, padding: 24 }}>{/* container */}
      <Button title="Add 2 items (transaction)" onPress={addTwo} />{/* button */}
      <FlatList data={rows} keyExtractor={(r) => String(r.id)} renderItem={({ item }) => <Text>{item.item} x{item.qty} [{item.status}]</Text>} />{/* list */}
    </View>
  );                                                                // return खत्म
}                                                                   // Orders खत्म

export default function App() {                                     // root
  return (                                                          // provider से wrap
    <SQLiteProvider databaseName="shop.db" onInit={migrate}>{/* onInit में migration */}
      <Orders />{/* screen */}
    </SQLiteProvider>
  );                                                                // return खत्म
}                                                                   // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Engine | Android का bundled SQLite | iOS का system SQLite (expo-sqlite अपना bundled build भी देता है) |
| DB location | `/data/data/<pkg>/databases` (expo: `SQLite` folder) | App के Documents/SQLite |
| Backup | Auto Backup में शामिल हो सकता है | iCloud backup में शामिल (बड़े cache DB को exclude करो) |
| Performance | Device पर निर्भर | आम तौर पर तेज़ |
| Threading | Native thread pool, JS async | वही |
| Web | SDK 52 में experimental/alpha web support | N/A |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo SDK 52: expo-sqlite (async API)
import * as SQLite from 'expo-sqlite';                          // npx expo install expo-sqlite
const db = await SQLite.openDatabaseAsync('app.db');            // open
const rows = await db.getAllAsync('SELECT * FROM t');           // read
```
CLI way:
```jsx
// CLI: react-native-sqlite-storage (या op-sqlite, तेज़)
import SQLite from 'react-native-sqlite-storage';               // npm i react-native-sqlite-storage; cd ios && pod install
SQLite.enablePromise(true);                                     // promise API चालू
const db = await SQLite.openDatabase({ name: 'app.db', location: 'default' }); // open
const [res] = await db.executeSql('SELECT * FROM t');           // read
const rows = res.rows.raw();                                    // rows array
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: SQL string में user input जोड़ना (`'... WHERE name="' + name + '"'`)।
✅ Correct: `?` placeholders और params array।

❌ Mistake 2: Table बनाना हर launch पर बिना `IF NOT EXISTS` के।
✅ Correct: `CREATE TABLE IF NOT EXISTS` या migrations।

❌ Mistake 3: कई writes बिना transaction के (धीमा + आधा data)।
✅ Correct: `withTransactionAsync`।

❌ Mistake 4: Schema बदलकर migration न लिखना, पुराने users का app crash।
✅ Correct: `PRAGMA user_version` से versioned migrations।

---

## 🧠 Tricky Interview Question
1000 rows insert करने हैं। (a) loop में 1000 `runAsync` बिना transaction, (b) एक transaction में 1000। कौन तेज़ और क्यों?

Answer: (b) बहुत तेज़। बिना transaction हर INSERT अपना अलग commit करता है और हर commit disk पर fsync कराता है, इसलिए धीमा। Transaction में सब writes एक commit में जाते हैं, और failure पर सब rollback होता है।

---

## ⚫ Interview Questions + Answers
Q1: SQLite vs AsyncStorage?
A1: SQLite structured, queryable, indexed, transactional है; AsyncStorage सरल key-value और बड़े data पर धीमा।

Q2: SQL injection से कैसे बचें?
A2: Parameter binding (`?`), string concatenation कभी नहीं।

Q3: Migration कैसे?
A3: `PRAGMA user_version` पढ़ो और version के हिसाब से ALTER/CREATE चलाओ।

Q4: `getAllAsync`, `getFirstAsync`, `runAsync`, `execAsync` में फर्क?
A4: सब rows / पहली row / एक statement (insert/update, `lastInsertRowId`) / कई statements बिना params।

Q5: Large datasets पर sync कैसे?
A5: Last-synced timestamp रखो, server से delta लाओ, transaction में upsert करो; बड़े sync के लिए WatermelonDB जैसी library।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Offline-first, structured, relational data
- हज़ारों rows, search/filter/sort
- Chat history, orders, notes

❌ Avoid when:
- सिर्फ़ 2-3 settings (AsyncStorage/MMKV)
- Secrets (SecureStore)
- Reactive UI की बड़ी ज़रूरत हो, तब Realm/WatermelonDB देखो

---

## 📊 Visual Diagram
```
 React component
     |  db.runAsync / getAllAsync
     v
 expo-sqlite (JS API)
     |
     v
 Native SQLite engine
     |
     v
 shop.db (single file on phone)
   [orders]  [users]  [items]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Table / Row | Data grid / one record | तालिका / एक रिकॉर्ड |
| Query | SQL command | SQL आदेश |
| Transaction | Atomic group of writes | सब-या-कुछ-नहीं writes |
| Migration | Schema upgrade | Schema का upgrade |
| WAL | Write-ahead log mode | तेज़ लिखने वाला mode |

---

## ⚡ 3-Line Summary
English: SQLite is an on-device SQL database in a single file.
Use parameter binding, transactions and PRAGMA user_version migrations.
Choose it for structured offline data, not for tiny settings or secrets.

Hindi: SQLite phone पर एक file में रहने वाला SQL database है।
Parameter binding, transactions और user_version migrations use करो।
Structured offline data के लिए चुनो, छोटी settings या secrets के लिए नहीं।

---

## ➡️ Next Topic
**119. Realm Database**, SQL की जगह object-based, reactive local database।
