# 8. Database and Collection Commands
# हिंदी में: Database और Collection Commands

---

## 🔵 Simple Definition (English)
MongoDB creates databases and collections **lazily**: `use shop` only switches context, and the database appears after the first write. Core commands: `show dbs`, `use`, `db.getName()`, `db.createCollection()`, `show collections` / `db.getCollectionNames()`, `db.coll.drop()`, `db.dropDatabase()`, `db.coll.renameCollection()`, `db.coll.stats()`.

## 🔵 सरल परिभाषा (Hindi)
MongoDB databases और collections को **lazily** बनाता है: `use shop` सिर्फ context बदलता है, और database पहले write के बाद दिखता है। मुख्य commands: `show dbs`, `use`, `db.getName()`, `db.createCollection()`, `show collections` / `db.getCollectionNames()`, `db.coll.drop()`, `db.dropDatabase()`, `db.coll.renameCollection()`, `db.coll.stats()`।

---

## 🔴 Problem it Solves
In SQL you must `CREATE DATABASE` and `CREATE TABLE` before inserting. MongoDB removes that ceremony for fast prototyping, but it also means a typo in a collection name silently creates a new empty collection. These commands let you manage, inspect and clean namespaces deliberately, and `createCollection` is needed when you want options (capped, validator, collation, time series).

## 🔴 यह क्यों बना? (Hindi)
SQL में insert से पहले `CREATE DATABASE` और `CREATE TABLE` करना पड़ता है। MongoDB यह औपचारिकता हटाकर prototyping तेज़ करता है, पर इसका मतलब है कि collection name में typo चुपचाप नई खाली collection बना देगी। ये commands namespaces को सोच-समझकर manage, inspect और clean करने देते हैं, और options (capped, validator, collation, time series) चाहिए तो `createCollection` ज़रूरी है।

---

## 🟢 How it Works — Step by Step

Step 1 → `use shop` selects (not creates) the database; `db` variable now points to it.
Step 2 → The first `insertOne` into `db.orders` creates both the `shop` database and `orders` collection implicitly.
Step 3 → `show dbs` lists only databases that hold data (empty ones are hidden). `show collections` lists the current database's collections.
Step 4 → Use `db.createCollection(name, options)` when you need explicit options.
Step 5 → `drop()` removes a collection with its indexes (returns `true`); `dropDatabase()` removes the whole database. Both are irreversible.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `use shop` database select करता है (बनाता नहीं); `db` variable अब उसी की ओर इशारा करता है।
Step 2 → `db.orders` में पहला `insertOne` `shop` database और `orders` collection दोनों implicitly बना देता है।
Step 3 → `show dbs` सिर्फ वही databases दिखाता है जिनमें data है (खाली छुपे रहते हैं)। `show collections` current database की collections दिखाता है।
Step 4 → Explicit options चाहिए तो `db.createCollection(name, options)` इस्तेमाल करो।
Step 5 → `drop()` collection को indexes के साथ हटाता है (`true` return); `dropDatabase()` पूरा database हटाता है। दोनों irreversible हैं।

---

## 🟡 Real World Example
A Swiggy-style backend has one database per environment (`swiggy_dev`, `swiggy_test`) and collections like `restaurants`, `orders`, `riders`. QA's integration tests call `db.dropDatabase()` in `afterAll` to start clean for every run, while a nightly job renames `orders_tmp` to `orders_2026_q1` for archival using `renameCollection`.

## 🟡 Real Example Hindi mein
Swiggy जैसे backend में हर environment का अलग database होता है (`swiggy_dev`, `swiggy_test`) और collections जैसे `restaurants`, `orders`, `riders`। QA के integration tests हर run साफ शुरू करने के लिए `afterAll` में `db.dropDatabase()` चलाते हैं, जबकि nightly job archival के लिए `renameCollection` से `orders_tmp` को `orders_2026_q1` नाम देती है।

---

## 💻 Code Example — Basic

Run on mongod 8.0.4:

```javascript
use mh                                   // switch to database "mh" (not created yet)
db.getName()                             // Output: 'mh'
db.getMongo().getDBNames().includes("mh")// Output: false  -> database not visible before first write

db.users.insertOne({ name: "Aman" })     // first write creates db "mh" AND collection "users"
db.getCollectionNames()                  // Output: [ 'users' ]
show collections                         // Output: users

db.createCollection("logs")              // explicit creation, Output: { ok: 1 }
db.getCollectionNames()                  // Output: [ 'logs', 'users' ]  (sorted)
db.logs.drop()                           // Output: true  (collection removed)
db.logs.drop()                           // Output: false (already gone, no error)
```

## 💻 Code Example — Advanced

```javascript
// Create a collection WITH options (validator + collation)
db.createCollection("products", {
  validator: { $jsonSchema: { required: ["name", "price"] } }, // reject docs missing these
  collation: { locale: "en", strength: 2 }                     // case-insensitive comparisons
})
// Output: { ok: 1 }

// Rename a collection (target must not exist unless dropTarget: true)
db.products.renameCollection("catalog")          // Output: { ok: 1 }
db.catalog.renameCollection("products", true)    // second arg true = drop target if exists

// Inspect size/counts
db.products.stats().count                        // number of documents
db.products.totalSize()                          // bytes: data + indexes

// List databases in a script (nameOnly keeps it light)
db.adminCommand({ listDatabases: 1, nameOnly: true }).databases.map(d => d.name)
// Output (this test server): [ 'admin', 'config', 'local', 'mh' ]

// Drop a whole database (current one)
db.dropDatabase()                                // Output: { ok: 1, dropped: 'mh' }
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose creates the collection lazily too; its name is the pluralised lowercase model name.
const mongoose = require('mongoose');
const User = mongoose.model('User', new mongoose.Schema({ name: String })); // collection: "users"

await User.createCollection();      // explicitly create (useful before transactions)
await User.syncIndexes();           // make DB indexes match the schema
await User.collection.drop();       // drop collection (e.g., in test teardown)
await mongoose.connection.dropDatabase(); // wipe test DB -- NEVER on production
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Typo in the collection name
```javascript
db.ordres.insertOne({ total: 10 })   // Wrong: silently creates a new collection "ordres"
db.orders.insertOne({ total: 10 })   // Right
```

❌ Mistake 2: Expecting `use newdb` to show up in `show dbs`
✅ Correct: It appears only after data is written.

❌ Mistake 3: Running `db.dropDatabase()` on the wrong `db`
✅ Correct: Print `db.getName()` first; protect production with roles that lack `dropDatabase`.

---

## 🧠 Tricky Interview Question
Q: After `use blog`, `show dbs` does not list `blog`. Is it broken?
Answer: No. `use` only sets the shell's current database. MongoDB allocates the database on the first write that creates data. Same for `db.createCollection` on an otherwise empty DB: it creates the collection (and makes the DB visible) because it writes metadata/files.

---

## ⚫ Interview Questions + Answers

Q1: How do you create a database in MongoDB?
A1: You do not explicitly; `use name` then insert data. The database is created on first write.

Q2: Difference between `drop()` and `deleteMany({})`?
A2: `drop()` removes the collection including indexes and metadata instantly; `deleteMany({})` removes documents one by one (oplog entries) and keeps the collection and indexes.

Q3: When must you use `createCollection`?
A3: For options: capped, validator, collation, time series, clustered, or pre-creating a collection before multi-document transactions on older versions.

Q4: What are the reserved databases?
A4: `admin`, `local` and `config`.

Q5: How do you list collections programmatically?
A5: `db.getCollectionNames()` in mongosh, or `db.listCollections().toArray()` which includes options.

---

## 🔷 When to Use + When Not to Use
✅ Use `createCollection` when:
- You need validators, capped, TTL/time-series or collation options

❌ Avoid when:
- Relying on lazy creation in code that takes collection names from user input (typo/injection risk)

---

## 📊 Visual Diagram
```
mongod
 ├── admin   (system)
 ├── local   (system, oplog)
 ├── config  (system)
 └── shop    <-- created on first write
      ├── users    (collection)
      ├── orders
      └── products  (created via createCollection with options)
use shop          -> select
insertOne(...)    -> create
drop()/dropDatabase() -> destroy (irreversible)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Namespace | `db.collection` full name | db.collection का पूरा नाम |
| Lazy creation | Created on first write | पहले write पर बनना |
| drop | Remove collection | Collection हटाना |
| renameCollection | Change collection name | Collection का नाम बदलना |
| listCollections | Lists collections + options | Collections की list |

---

## ⚡ 3-Line Summary
English:
1. Databases and collections are created lazily on first write.
2. Use `createCollection` only when you need options; `drop` is instant and irreversible.
3. Typos create new collections silently, so double check names.

Hindi:
1. Databases और collections पहले write पर lazily बनते हैं।
2. Options चाहिए तभी `createCollection` इस्तेमाल करो; `drop` तुरंत और irreversible है।
3. Typos चुपचाप नई collection बना देते हैं, इसलिए नाम दोबारा जाँचो।

---

## ➡️ Next Topic
**9. Documents — embedding and arrays basics** — How nested objects and arrays live inside one document.
