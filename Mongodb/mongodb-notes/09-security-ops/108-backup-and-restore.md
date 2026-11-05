# 108. Backup and Restore (mongodump, mongorestore, snapshots)
# हिंदी में: Backup और Restore (mongodump, mongorestore, snapshots)

---

## 🔵 Simple Definition (English)
**Backup** is a safe copy of your data you can restore after deletion, corruption or disaster. MongoDB offers three main methods: (1) **`mongodump` / `mongorestore`** — logical backups that export BSON (+ metadata/indexes) — simple, good for small/medium data; (2) **Filesystem / volume snapshots** (LVM, EBS) — fast physical backups for large data, needing journaling or `fsyncLock`; (3) **Managed backup** — Atlas Cloud Backup, Ops Manager/Cloud Manager with **point-in-time recovery** using the oplog. Replication is NOT a backup: a bad `deleteMany` replicates instantly.

## 🔵 सरल परिभाषा (Hindi)
**Backup** आपके data की सुरक्षित copy है जिसे delete, corruption या disaster के बाद restore किया जा सके। MongoDB में तीन मुख्य तरीके हैं: (1) **`mongodump` / `mongorestore`** — logical backup जो BSON (+ metadata/indexes) export करता है — छोटे/मध्यम data के लिए आसान; (2) **Filesystem / volume snapshots** (LVM, EBS) — बड़े data के लिए तेज़ physical backup; (3) **Managed backup** — Atlas Cloud Backup, Ops Manager, जिसमें oplog से **point-in-time recovery** मिलता है। Replication backup नहीं है: गलत `deleteMany` तुरंत सभी replicas पर चला जाता है।

---

## 🔴 Problem it Solves
Hardware fails, engineers run `dropDatabase()` on the wrong terminal, ransomware encrypts files, and bugs corrupt records silently. A replica set protects against a *server* dying, not against *logical* mistakes. You need an independent, restorable, tested copy with a known **RPO** (how much data you can lose) and **RTO** (how long recovery takes).

## 🔴 यह क्यों बना? (Hindi)
Hardware fail होता है, engineer गलत terminal में `dropDatabase()` चला देता है, ransomware files encrypt करता है, और bugs चुपचाप records बिगाड़ देते हैं। Replica set *server* मरने से बचाता है, *logical* गलतियों से नहीं। आपको एक स्वतंत्र, restore-योग्य, tested copy चाहिए जिसका **RPO** (कितना data खो सकते हैं) और **RTO** (recovery में कितना समय) पता हो।

---

## 🟢 How it Works — Step by Step

Step 1 → **mongodump** connects as a normal client, reads each collection and writes `<coll>.bson` plus `<coll>.metadata.json` (indexes, options) per database; `--gzip` compresses, `--archive` writes one file.
Step 2 → **mongorestore** reads those files and inserts documents, then rebuilds indexes. `--drop` removes the existing collection first; `--nsFrom/--nsTo` renames namespaces.
Step 3 → For a consistent dump of a replica set use `--oplog` (full-instance dump) so changes during the dump are replayed; restore with `--oplogReplay`.
Step 4 → **Snapshots:** on a replica set secondary (or after `db.fsyncLock()`), snapshot the data volume; restore by attaching the volume. Fast for TBs but copies the whole disk.
Step 5 → **PITR:** keep a base snapshot + continuous oplog; restore to any second (Atlas continuous backup).
Step 6 → **Test restores regularly** and store backups off-site, encrypted, with retention rules (3-2-1 rule).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **mongodump** सामान्य client की तरह connect होकर हर collection पढ़ता है और हर database के लिए `<coll>.bson` और `<coll>.metadata.json` (indexes, options) लिखता है; `--gzip` compress करता है, `--archive` एक ही file बनाता है।
Step 2 → **mongorestore** उन files को पढ़कर documents insert करता है फिर indexes बनाता है। `--drop` पहले मौजूदा collection हटाता है; `--nsFrom/--nsTo` namespace rename करता है।
Step 3 → Replica set का consistent dump चाहिए तो `--oplog` इस्तेमाल करो ताकि dump के दौरान हुए बदलाव replay हों; restore में `--oplogReplay`।
Step 4 → **Snapshots:** secondary पर (या `db.fsyncLock()` के बाद) data volume का snapshot लो; restore में volume attach करो। TBs के लिए तेज़ पर पूरी disk copy होती है।
Step 5 → **PITR:** base snapshot + लगातार oplog रखो; किसी भी सेकंड पर restore करो (Atlas continuous backup)।
Step 6 → **नियमित restore test** करो, backups off-site, encrypted और retention के साथ रखो (3-2-1 rule)।

---

## 🟡 Real World Example
**Swiggy's** order DB runs on a 3-node replica set. A developer accidentally runs `db.orders.deleteMany({})` on production at 2:14 PM; all replicas obey within milliseconds. Ops uses **point-in-time restore** to 2:13 PM into a new cluster, then exports just the `orders` collection and merges back. A nightly `mongodump --gzip` of small reference collections (cities, coupons) to S3 serves as a second safety net. A quarterly "restore drill" proves the backups actually work.

## 🟡 Real Example Hindi mein
**Swiggy** का order DB 3-node replica set पर है। दोपहर 2:14 पर developer गलती से production में `db.orders.deleteMany({})` चला देता है; सभी replicas milliseconds में मान लेते हैं। Ops **point-in-time restore** से 2:13 PM की state नए cluster में बनाता है, सिर्फ `orders` collection export करके वापस merge करता है। छोटे reference collections (cities, coupons) का रात का `mongodump --gzip` S3 में दूसरा सुरक्षा कवच है। तिमाही "restore drill" साबित करती है कि backups सच में काम करते हैं।

---

## 💻 Code Example — Basic

```bash
# All commands run against mongod 8.0.4 on port 27131 (database "shop", 3 orders)

# 1) Folder dump of one database
mongodump --port 27131 --db shop --out ./dump
# Output (tail):
#   writing shop.orders to ./dump/shop/orders.bson
#   done dumping shop.orders (3 documents)
ls ./dump/shop
# Output: orders.bson  orders.metadata.json

# 2) Single compressed archive file (easier to ship to S3)
mongodump --port 27131 --db shop --archive=shop.gz --gzip
# Output: done dumping shop.orders (3 documents)

# 3) Simulate disaster
mongosh --port 27131 --quiet --eval 'db.getSiblingDB("shop").dropDatabase().ok'
# Output: 1

# 4) Restore from the archive
mongorestore --port 27131 --archive=shop.gz --gzip
# Output: no indexes to restore for collection shop.orders
#         3 document(s) restored successfully. 0 document(s) failed to restore.

mongosh --port 27131 --quiet --eval 'db.getSiblingDB("shop").orders.countDocuments()'
# Output: 3

# 5) Restore again over existing data: --drop avoids duplicate-key failures
mongorestore --port 27131 --archive=shop.gz --gzip --drop
# Output: 3 document(s) restored successfully. 0 document(s) failed to restore.
```
(Timestamps in tool log lines vary.)

## 💻 Code Example — Advanced

```bash
# Replica set: consistent full dump including changes made while dumping
mongodump --uri="mongodb://u:p@n1,n2,n3/?replicaSet=rs0&readPreference=secondary" \
  --oplog --gzip --out /backups/$(date +%F)       # --oplog only works for full-instance dumps (no --db)

mongorestore --uri="mongodb://u:p@target/" --oplogReplay --gzip /backups/2026-11-04

# Restore one collection into a different DB name (safe side-by-side inspection)
mongorestore --port 27131 --nsInclude='shop.orders' \
  --nsFrom='shop.orders' --nsTo='shop_restore.orders' ./dump

# Snapshot-based backup on a self-hosted node (brief write freeze)
mongosh --eval 'db.fsyncLock()'      # flush to disk and block writes
#   ... take LVM / EBS snapshot here ...
mongosh --eval 'db.fsyncUnlock()'    # resume writes
# (With journaling on the same volume you can skip fsyncLock and snapshot an unlocked secondary.)
```

```javascript
// backup-job.js — nightly Node job wrapper with retention
const { execFile } = require('child_process');
const fs = require('fs');
const stamp = new Date().toISOString().slice(0, 10);          // 2026-11-04
const out = `/backups/shop-${stamp}.gz`;

execFile('mongodump', ['--uri', process.env.MONGO_URI, `--archive=${out}`, '--gzip'], (err, so, se) => {
  if (err) { console.error('BACKUP FAILED', se); process.exit(1); } // alert on failure!
  console.log('backup ok', fs.statSync(out).size, 'bytes');
  // next: upload to S3 with SSE-KMS, delete files older than 30 days
});
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Admin-only endpoint to trigger an on-demand backup (use a job queue in real life)
const express = require('express');
const { spawn } = require('child_process');
const app = express();

app.post('/admin/backup', requireAdmin, (req, res) => {          // requireAdmin = your auth middleware
  const file = `/backups/manual-${Date.now()}.gz`;
  const p = spawn('mongodump', ['--uri', process.env.MONGO_URI, `--archive=${file}`, '--gzip']);
  p.on('close', (code) => code === 0
    ? res.json({ file })                                          // success
    : res.status(500).json({ error: 'backup failed' }));
});
// Mongoose needs nothing special: backups work at the DB level, not through models.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: "We have a replica set, so we have backups."
```text
Wrong: deleteMany({}) replicates to every secondary in milliseconds.
Right: take independent backups (dump/snapshot/PITR) stored elsewhere.
```
❌ Mistake 2: Never testing a restore. ✅ Correct: schedule restore drills; a backup you haven't restored is a hope, not a backup.

❌ Mistake 3: Restoring without `--drop` into existing data -> duplicate key errors (`E11000`), partial restore.

❌ Mistake 4: Dumping the primary during peak traffic.
✅ Correct: dump from a hidden/secondary node (`readPreference=secondary`) to avoid slowing production.

❌ Mistake 5: Using `mongodump` for multi-TB data (hours to restore, rebuilding every index). ✅ Use snapshots / Atlas backup.

---

## 🧠 Tricky Interview Question
**Q:** Is a `mongodump` of a busy replica set a consistent snapshot of the database?

**Answer:** No. Without `--oplog`, mongodump reads collections one after another while writes continue, so the result is **not point-in-time consistent** across collections (an order may exist but its payment, written later, is missing). Adding `--oplog` records the oplog entries made during the dump and `mongorestore --oplogReplay` applies them to reach one consistent moment. `--oplog` is allowed only for whole-instance dumps (no `--db/--collection`). For sharded clusters mongodump is unsuitable for consistency; use Atlas/Ops Manager coordinated snapshots.

---

## ⚫ Interview Questions + Answers

Q1: mongodump vs filesystem snapshot — when each?
A1: mongodump is portable, selective (db/collection/query) and simple but slow to restore for big data (re-inserts + reindex). Snapshots are fast and exact for large data but copy the whole volume and need coordination (journal/fsyncLock).

Q2: What does a dump contain?
A2: `.bson` data files and `.metadata.json` with index definitions/options. Users/roles are dumped only with `--db admin` or full dumps (`--dumpDbUsersAndRoles`).

Q3: What is point-in-time recovery?
A3: Restoring to an exact moment using a snapshot plus oplog replay up to that timestamp (Atlas continuous backup). It undoes accidental deletes with low RPO.

Q4: RPO and RTO?
A4: RPO = maximum tolerable data loss (time between backups); RTO = maximum tolerable downtime to restore. Choose method to meet them.

Q5: How to restore only one collection?
A5: `mongorestore --nsInclude 'db.coll' dump/` (optionally `--nsFrom/--nsTo` to rename).

---

## 🔷 When to Use + When Not to Use
✅ Use mongodump when:
- Small to medium data, migrating between versions/environments, backing up selected collections

✅ Use snapshots/Atlas PITR when:
- Large production clusters needing fast restores and low RPO

❌ Avoid:
- Relying on replication as a backup, or on dumps taken from a heavily loaded primary

---

## 📊 Visual Diagram
```
BACKUP METHODS
─────────────────────────────────────────────────────────
 mongod ──read──▶ mongodump ──▶ *.bson + *.metadata.json (or archive.gz)
                                   │
                                   ▼  mongorestore (--drop, --oplogReplay)
                              new / same mongod

 Volume ──fsyncLock──▶ [LVM/EBS snapshot] ──▶ restore = attach volume
 Snapshot + oplog stream ──▶ PITR: restore to 14:13:00 exactly
 Replica set ≠ backup  (bad write replicates everywhere)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mongodump | Logical backup tool | Logical backup tool |
| mongorestore | Loads dump back | Dump वापस load करता है |
| Snapshot | Volume-level copy | Volume की copy |
| PITR | Restore to exact time | किसी भी समय पर restore |
| RPO | Max data loss window | अधिकतम data loss समय |
| RTO | Max recovery time | अधिकतम recovery समय |
| fsyncLock | Flush & block writes | Flush करके writes रोकना |

---

## ⚡ 3-Line Summary
English:
1. `mongodump`/`mongorestore` give portable logical backups; snapshots and Atlas PITR suit large data.
2. Replication is not a backup; use `--oplog` for consistency and `--drop` when restoring over data.
3. Test restores regularly and keep encrypted copies off-site.

Hindi:
1. `mongodump`/`mongorestore` portable logical backup देते हैं; बड़े data के लिए snapshots और Atlas PITR।
2. Replication backup नहीं है; consistency के लिए `--oplog` और data के ऊपर restore में `--drop` इस्तेमाल करो।
3. Restore नियमित test करो और encrypted copies off-site रखो।

---

## ➡️ Next Topic
**109. mongoexport, mongoimport and Data Migration** — Moving data as JSON/CSV.
