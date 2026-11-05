# 109. mongoexport, mongoimport and Data Migration
# हिंदी में: mongoexport, mongoimport और Data Migration

---

## 🔵 Simple Definition (English)
**`mongoexport`** writes collection data as human-readable **JSON (Extended JSON) or CSV**; **`mongoimport`** loads JSON, CSV or TSV files into a collection. They are for **data interchange** (spreadsheets, seeding, ETL, moving small datasets) — unlike `mongodump/mongorestore`, which keep exact BSON types and indexes. **Data migration** means moving data between systems/schemas/versions: export-import, dump-restore, change streams / live migration, or a custom script with batches.

## 🔵 सरल परिभाषा (Hindi)
**`mongoexport`** collection data को पढ़ने-योग्य **JSON (Extended JSON) या CSV** में लिखता है; **`mongoimport`** JSON, CSV या TSV files को collection में load करता है। ये **data अदला-बदली** (spreadsheets, seeding, ETL, छोटे datasets) के लिए हैं — `mongodump/mongorestore` से अलग, जो exact BSON types और indexes रखते हैं। **Data migration** का मतलब systems/schemas/versions के बीच data ले जाना: export-import, dump-restore, change streams / live migration, या batches वाली custom script।

---

## 🔴 Problem it Solves
Business teams want a CSV for Excel; developers want to seed a test DB from a JSON file; a new system needs yesterday's data in a different shape; you must move a collection from one cluster to another. Writing a one-off program for each is slow. Import/export tools give a command-line, scriptable path — but you must understand their limits (type fidelity, no indexes, CSV flatness).

## 🔴 यह क्यों बना? (Hindi)
Business team को Excel के लिए CSV चाहिए; developer को test DB seed करना है; नए system को दूसरी shape में कल का data चाहिए; collection एक cluster से दूसरे में ले जानी है। हर बार program लिखना धीमा है। Import/export tools command-line, scriptable रास्ता देते हैं — पर उनकी सीमाएँ (type fidelity, indexes नहीं, CSV flat) समझनी ज़रूरी हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `mongoexport --db D --collection C --out file.json` writes one **Extended JSON** document per line (JSON Lines). Types like Date/ObjectId are preserved as `{"$date":...}`/`{"$oid":...}` in canonical/relaxed mode.
Step 2 → CSV export needs `--type=csv --fields a,b` (nested fields via dot notation); arrays/sub-documents don't flatten well.
Step 3 → Filter with `--query '{"amt":{"$gt":100}}'`, `--sort`, `--limit`, `--skip`.
Step 4 → `mongoimport --db D --collection C --file f.json` inserts; `--type=csv --headerline` uses the first row as field names; CSV values are guessed as numbers/strings (`--columnsHaveTypes` for explicit types).
Step 5 → `--mode` controls duplicates: `insert` (default), `upsert` (match on `_id` or `--upsertFields`), `merge`, `delete`. `--drop` empties the collection first.
Step 6 → **Indexes are NOT exported** — recreate them (or use dump/restore). Large migrations: use dump/restore, or batch scripts with `bulkWrite`, verify counts and checksums, cut over with minimal downtime.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `mongoexport --db D --collection C --out file.json` हर line में एक **Extended JSON** document लिखता है (JSON Lines)। Date/ObjectId जैसे types `{"$date":...}`/`{"$oid":...}` के रूप में सुरक्षित रहते हैं।
Step 2 → CSV के लिए `--type=csv --fields a,b` चाहिए (nested fields dot notation से); arrays/sub-documents अच्छे से flat नहीं होते।
Step 3 → `--query '{"amt":{"$gt":100}}'`, `--sort`, `--limit`, `--skip` से filter करो।
Step 4 → `mongoimport --db D --collection C --file f.json` insert करता है; `--type=csv --headerline` पहली row को field names मानता है; CSV values number/string में अंदाज़े से बदलती हैं (`--columnsHaveTypes` से explicit)।
Step 5 → `--mode` duplicates तय करता है: `insert` (default), `upsert`, `merge`, `delete`। `--drop` पहले collection खाली करता है।
Step 6 → **Indexes export नहीं होते** — दोबारा बनाओ (या dump/restore)। बड़ी migration: dump/restore या `bulkWrite` batches, counts/checksums जाँचो, कम downtime में cutover।

---

## 🟡 Real World Example
**Flipkart's** seller-support team asks for "all orders above Rs 100 for seller 77 as an Excel sheet". An engineer runs `mongoexport --type=csv --fields orderId,item,amt --query '{"sellerId":77,"amt":{"$gt":100}}'`. Later, QA seeds a staging DB from a `products.json` file using `mongoimport --drop`. During a re-platforming, the catalog (2 million docs) is moved from an old cluster to a new one with dump/restore, and then a change-stream or timestamp-based delta script copies records modified during the migration.

## 🟡 Real Example Hindi mein
**Flipkart** की seller-support team माँगती है "seller 77 के Rs 100 से ऊपर के सभी orders Excel में"। Engineer `mongoexport --type=csv --fields orderId,item,amt --query '{"sellerId":77,"amt":{"$gt":100}}'` चलाता है। बाद में QA `mongoimport --drop` से `products.json` से staging DB seed करती है। Re-platforming में catalog (20 लाख docs) पुराने cluster से नए में dump/restore से जाता है, फिर change-stream या timestamp आधारित delta script migration के दौरान बदले records कॉपी करती है।

---

## 💻 Code Example — Basic

```bash
# Verified on mongod 8.0.4, port 27131. DB shop.orders has 3 docs.

# 1) JSON export (one document per line)
mongoexport --port 27131 --db shop --collection orders --out o.json
# Output: exported 3 records
cat o.json
# {"_id":1,"item":"Biryani","amt":250}
# {"_id":2,"item":"Naan","amt":40}
# {"_id":3,"item":"Dal","amt":180}

# 2) CSV export with chosen fields
mongoexport --port 27131 --db shop -c orders --type=csv --fields item,amt --out o.csv
# Output: exported 3 records
cat o.csv
# item,amt
# Biryani,250
# Naan,40
# Dal,180

# 3) Import the CSV into another database; first row = field names
mongoimport --port 27131 --db shop2 -c orders --type=csv --headerline --file o.csv
# Output: 3 document(s) imported successfully. 0 document(s) failed to import.

mongosh --port 27131 --quiet --eval 'printjson(db.getSiblingDB("shop2").orders.find({},{_id:0}).toArray())'
# Output: [ { item: 'Biryani', amt: 250 }, { item: 'Dal', amt: 180 }, { item: 'Naan', amt: 40 } ]
# (amt is imported as a number: CSV types are auto-detected; _id are new ObjectIds)

# 4) Import JSON lines with upsert (re-runnable, no duplicates)
mongoimport --port 27131 --db shop2 -c o2 --file o.json --mode=upsert
# Output: 3 document(s) imported successfully. 0 document(s) failed to import.
```
(Log lines are prefixed with a timestamp that varies.)

## 💻 Code Example — Advanced

```javascript
// migrate.js — batched copy between two clusters with transform + verification
const { MongoClient } = require('mongodb');

async function migrate() {
  const src = new MongoClient(process.env.SRC_URI), dst = new MongoClient(process.env.DST_URI);
  await Promise.all([src.connect(), dst.connect()]);
  const from = src.db('shop').collection('orders');
  const to = dst.db('shop_v2').collection('orders');

  const cursor = from.find({}).sort({ _id: 1 }).batchSize(1000); // stable order, memory-friendly
  let batch = [], total = 0;

  for await (const doc of cursor) {
    batch.push({
      replaceOne: {                                  // idempotent: safe to re-run after a crash
        filter: { _id: doc._id },
        replacement: { ...doc, amountPaise: Math.round(doc.amt * 100), migratedAt: new Date() }, // schema change
        upsert: true,
      },
    });
    if (batch.length === 1000) { await to.bulkWrite(batch, { ordered: false }); total += batch.length; batch = []; }
  }
  if (batch.length) { await to.bulkWrite(batch, { ordered: false }); total += batch.length; }

  // verification: counts must match
  const [a, b] = await Promise.all([from.countDocuments(), to.countDocuments()]);
  console.log({ copied: total, srcCount: a, dstCount: b, ok: a === b });
  await src.close(); await dst.close();
}
migrate().catch(console.error);
```

```bash
# Filtered export for a report, newest first, top 100
mongoexport --uri="$MONGO_URI" -c orders \
  --query='{"sellerId":77,"amt":{"$gt":100}}' \
  --sort='{"_id":-1}' --limit=100 --type=csv --fields=orderId,item,amt -o seller77.csv
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// CSV download endpoint (streaming) — alternative to shelling out to mongoexport
const express = require('express');
const mongoose = require('mongoose');
const app = express();
const Order = mongoose.model('Order', new mongoose.Schema({ item: String, amt: Number }));

app.get('/api/orders.csv', async (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.write('item,amt\n');                                   // header row
  for await (const o of Order.find().lean().cursor()) {      // stream: no giant array in memory
    res.write(`${JSON.stringify(o.item)},${o.amt}\n`);       // JSON.stringify quotes strings safely
  }
  res.end();
});
// For bulk import from an uploaded CSV, parse with csv-parse and Order.insertMany(rows, { ordered:false }).
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using export/import as a backup.
```text
Wrong: mongoexport -> mongoimport as "backup": loses indexes, may alter types, no consistency.
Right: mongodump/mongorestore or snapshots for backups; export/import for interchange.
```
❌ Mistake 2: Importing CSV and expecting dates/ObjectIds to be typed. CSV is text: use `--columnsHaveTypes` (`created.date_go(2006-01-02)`) or convert afterwards.

❌ Mistake 3: Importing twice in default `insert` mode -> `E11000 duplicate key` errors. ✅ Use `--mode=upsert` or `--drop`.

❌ Mistake 4: Forgetting indexes after import: queries become collection scans. ✅ Recreate indexes (before or after load — after is faster for huge loads).

---

## 🧠 Tricky Interview Question
**Q:** You `mongoexport` a collection containing `{ price: NumberDecimal("10.10"), at: ISODate(...) }` as relaxed JSON and `mongoimport` it back. Are the types identical?

**Answer:** mongoexport (4.x+) writes **Extended JSON v2 relaxed** by default: Dates become `{"$date":"..."}`, Decimal128 becomes `{"$numberDecimal":"10.10"}`, and `mongoimport` understands them, so Date/Decimal128/ObjectId survive. But relaxed mode writes plain **Int32/Int64/Double as ordinary numbers**, so `NumberLong(5)` may come back as an Int32 or Double depending on the value — numeric width is not guaranteed. Verified: default output was `"l":5,"i":5,"d":5.5`; adding `--jsonFormat=canonical` gives `{"$numberLong":"5"}`, `{"$numberInt":"5"}`, `{"$numberDouble":"5.5"}` and keeps widths. For full fidelity (and indexes) use `mongodump` (BSON). CSV loses everything (all text).

---

## ⚫ Interview Questions + Answers

Q1: mongoexport vs mongodump?
A1: Export gives readable JSON/CSV, no indexes, possible type drift; dump gives binary BSON with exact types and index metadata, faster for restore. Dump for backup/migration between MongoDB instances; export for sharing with humans/other tools.

Q2: How do you import a large CSV efficiently?
A2: `mongoimport --numInsertionWorkers N`, drop indexes first and rebuild after, use `--mode=insert` with unique `_id`, or stream-parse in Node and `insertMany` in 1000-document unordered batches.

Q3: How do you migrate with near-zero downtime?
A3: Initial bulk copy, then apply deltas via change streams (or `updatedAt` polling), verify counts/checksums, switch writes (cutover), keep old DB read-only for rollback. Atlas Live Migrate automates this.

Q4: What does `--mode=merge` do?
A4: Upserts and merges imported fields into the existing document (keeping other fields), unlike `upsert` which replaces the whole document.

Q5: Can mongoexport export nested arrays to CSV?
A5: Not usefully; CSV needs flat fields, so use dot notation for sub-document fields (`address.city`) and pre-flatten arrays with an aggregation (`$unwind`/`$project`) or use JSON.

---

## 🔷 When to Use + When Not to Use
✅ Use export/import when:
- Sharing reports, seeding test data, small one-off moves, converting to/from CSV

✅ Use scripts/change streams when:
- Schema transformation or live migration with ongoing writes

❌ Avoid:
- Backups, multi-TB migrations, or when exact BSON types and indexes must be preserved

---

## 📊 Visual Diagram
```
DATA MOVEMENT TOOLS
────────────────────────────────────────────────
 MongoDB ──mongoexport──▶ JSON lines / CSV ──mongoimport──▶ MongoDB
                │                                   ▲
                ▼                                   │
        Excel / BI / other DB            (--mode insert|upsert|merge, --drop)

 MongoDB ──mongodump──▶ BSON + metadata ──mongorestore──▶ MongoDB   (exact types + indexes)

 LIVE MIGRATION:  bulk copy ─▶ change-stream deltas ─▶ verify ─▶ cutover
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Extended JSON | JSON with BSON types | BSON types वाला JSON |
| JSON Lines | One JSON doc per line | हर line में एक JSON |
| --headerline | First CSV row = fields | पहली row = field names |
| --mode upsert | Insert or replace by key | Key से insert/replace |
| ETL | Extract-Transform-Load | Data निकालो-बदलो-डालो |
| Cutover | Switch traffic to new DB | Traffic नए DB पर ले जाना |
| Delta sync | Copy changes after bulk copy | Bulk के बाद के बदलाव कॉपी |

---

## ⚡ 3-Line Summary
English:
1. `mongoexport`/`mongoimport` move data as JSON/CSV for humans and tools; they do not keep indexes or guarantee exact types.
2. Use `--mode=upsert`, `--drop`, `--headerline`, `--query`, `--fields` to control imports and exports.
3. For backups or big migrations use dump/restore, snapshots or batched scripts with change-stream deltas.

Hindi:
1. `mongoexport`/`mongoimport` data को JSON/CSV में इंसानों और tools के लिए ले जाते हैं; indexes नहीं रखते और exact types guarantee नहीं करते।
2. `--mode=upsert`, `--drop`, `--headerline`, `--query`, `--fields` से import/export नियंत्रित करो।
3. Backup या बड़ी migration के लिए dump/restore, snapshots या change-stream deltas वाली batched scripts इस्तेमाल करो।

---

## ➡️ Next Topic
**110. Monitoring MongoDB (mongostat, Atlas metrics)** — Watching health and performance.
