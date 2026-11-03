# 76. Tree Structures in MongoDB
# हिंदी में: MongoDB में Tree Structures

---

## 🔵 Simple Definition (English)
Hierarchical data (category trees, org charts, comment threads, folder structures) can be modeled in MongoDB in several ways: **Parent References** (each node stores `parent`), **Child References** (each node stores an array of children), **Array of Ancestors**, **Materialized Path** (a string like `,Food,Indian,Biryani,`), and **Nested Sets**. MongoDB also has the **`$graphLookup`** aggregation stage that walks parent/child links recursively inside the database. You choose by which questions you ask most: "children of X", "all descendants of X", "path to root", "move a subtree".

## 🔵 सरल परिभाषा (Hindi)
Hierarchical data (category trees, org charts, comment threads, folder structures) को MongoDB में कई तरीकों से model किया जा सकता है: **Parent References** (हर node में `parent`), **Child References** (हर node में children का array), **Array of Ancestors**, **Materialized Path** (जैसे `,Food,Indian,Biryani,` string), और **Nested Sets**। MongoDB में **`$graphLookup`** aggregation stage भी है जो parent/child links को database के अंदर recursively चलता है। चुनाव इस पर कि आप सबसे ज़्यादा कौन से सवाल पूछते हैं: "X के children", "X के सभी descendants", "root तक path", "subtree move करना"।

---

## 🔴 Problem it Solves
SQL needs recursive CTEs for trees. In MongoDB a naive approach (nested sub-documents several levels deep) can't be queried for "all descendants anywhere" or re-parented easily, and a flat model with only `parent` forces N queries to climb or descend (one per level). Each tree model optimizes different operations; picking wrong makes menus, breadcrumbs or "all items under category X" slow or hard to update.

## 🔴 यह क्यों बना? (Hindi)
SQL में trees के लिए recursive CTEs चाहिए। MongoDB में naive तरीका (कई levels तक nested sub-documents) "कहीं भी के सभी descendants" query या आसान re-parenting नहीं होने देता, और सिर्फ़ `parent` वाला flat model ऊपर-नीचे जाने के लिए N queries (हर level पर एक) माँगता है। हर tree model अलग operations के लिए optimized है; गलत चुनाव से menus, breadcrumbs या "category X के नीचे सब items" slow या update करने में कठिन हो जाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Parent References**: `{ _id: "Biryani", parent: "Indian" }`. Children = `find({ parent: "Indian" })` (index `parent`). Easy to move a node (change one field). Ancestors/descendants need many queries or `$graphLookup`.
Step 2 → **Child References**: `{ _id: "Indian", children: ["Biryani", ...] }`. Fast "children" read; no good for finding the parent or for big fan-out.
Step 3 → **Array of Ancestors**: `{ _id: "Biryani", ancestors: ["Food", "Indian"], parent: "Indian" }`. One query returns the path (breadcrumb) or all descendants `find({ ancestors: "Indian" })` (multikey index). Moving a subtree = update all descendants' arrays.
Step 4 → **Materialized Path**: `{ path: ",Food,Indian," }`. Descendants via a regex on a prefix (`/^,Food,Indian,/` uses the index); sortable path gives a tree order. Moving a subtree = rewrite the prefix.
Step 5 → **`$graphLookup`**: recursively follows `connectFromField → connectToField` starting from `startWith`, returning matches with an optional `depthField` and `maxDepth`. Works with the plain parent-reference model; index `connectToField`.
Step 6 → Pick: mostly "children" + moves → Parent; mostly "subtree/ancestor reads" → Ancestors or Path; arbitrary graph → `$graphLookup`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Parent References**: `{ _id: "Biryani", parent: "Indian" }`। Children = `find({ parent: "Indian" })` (index `parent`)। Node move करना आसान (एक field बदलो)। Ancestors/descendants के लिए कई queries या `$graphLookup`।
Step 2 → **Child References**: `{ _id: "Indian", children: ["Biryani", ...] }`। "Children" read तेज़; parent ढूँढने या बड़े fan-out के लिए ठीक नहीं।
Step 3 → **Array of Ancestors**: `{ _id: "Biryani", ancestors: ["Food", "Indian"], parent: "Indian" }`। एक query से path (breadcrumb) या सभी descendants `find({ ancestors: "Indian" })` (multikey index)। Subtree move = सभी descendants के arrays update।
Step 4 → **Materialized Path**: `{ path: ",Food,Indian," }`। Prefix regex (`/^,Food,Indian,/`, index इस्तेमाल करता है) से descendants; sort करने योग्य path से tree order। Subtree move = prefix rewrite।
Step 5 → **`$graphLookup`**: `startWith` से शुरू होकर `connectFromField → connectToField` को recursively follow करता है, optional `depthField` और `maxDepth` के साथ। सादे parent-reference model के साथ चलता है; `connectToField` पर index लगाओ।
Step 6 → चुनाव: ज़्यादातर "children" + moves → Parent; ज़्यादातर "subtree/ancestor reads" → Ancestors या Path; arbitrary graph → `$graphLookup`।

---

## 🟡 Real World Example
**Zomato/Swiggy cuisine category tree**: `Food → Indian → Biryani → Hyderabadi`, plus `Food → Chinese`. The app shows a breadcrumb (needs ancestors), a sidebar of direct sub-categories (needs children), and "all restaurants under Indian" (needs all descendant category ids). The team stores `parent` and a materialized `path` on each node: the sidebar uses `parent`, the breadcrumb splits `path`, and the "under Indian" filter uses a prefix match on `path`. Renames and re-parenting happen a few times a month, so rewriting a subtree's path is acceptable.

## 🟡 Real Example Hindi mein
**Zomato/Swiggy की cuisine category tree**: `Food → Indian → Biryani → Hyderabadi` और `Food → Chinese`। App breadcrumb (ancestors), direct sub-categories की sidebar (children) और "Indian के नीचे सारे restaurants" (सभी descendant category ids) दिखाता है। Team हर node पर `parent` और materialized `path` रखती है: sidebar `parent` से, breadcrumb `path` को split करके, और "Indian के नीचे" filter `path` के prefix match से। Renames और re-parenting महीने में कुछ बार होते हैं, इसलिए subtree का path rewrite करना ठीक है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4)
use t76
db.cats.insertMany([
  { _id: "Food",       parent: null,       path: null },                           // root
  { _id: "Indian",     parent: "Food",     path: ",Food," },
  { _id: "Biryani",    parent: "Indian",   path: ",Food,Indian," },
  { _id: "Hyderabadi", parent: "Biryani",  path: ",Food,Indian,Biryani," },
  { _id: "Chinese",    parent: "Food",     path: ",Food," }
])
db.cats.createIndex({ path: 1 })                    // supports anchored-prefix regex on path
db.cats.createIndex({ parent: 1 })                  // supports "children of X" and $graphLookup

// 1) Direct children (Parent Reference)
db.cats.find({ parent: "Food" }).toArray().map(d => d._id)
// Output: [ 'Indian', 'Chinese' ]

// 2) All descendants of "Indian" (Materialized Path - contains-match)
db.cats.find({ path: /,Indian,/ }).toArray().map(d => d._id)
// Output: [ 'Biryani', 'Hyderabadi' ]
// Better for index use: anchor the prefix:  { path: /^,Food,Indian,/ }  (use the full path from the root)

// 3) Move "Biryani" under "Chinese"? (Parent Ref: one field. Path: must also fix the subtree)
db.cats.updateOne({ _id: "Biryani" }, { $set: { parent: "Chinese", path: ",Food,Chinese," } })
db.cats.updateMany({ path: /,Biryani,/ },                                    // every descendant of Biryani
  [ { $set: { path: { $replaceOne: { input: "$path", find: ",Food,Indian,Biryani,", replacement: ",Food,Chinese,Biryani," } } } } ])
// Output: the descendant "Hyderabadi" now has path ',Food,Chinese,Biryani,'
```

## 💻 Code Example — Advanced

```javascript
// mongosh — $graphLookup: recursive traversal in the database (on the ORIGINAL tree, before the move above)

// All descendants of Food, with depth (0 = direct child)
db.cats.aggregate([
  { $match: { _id: "Food" } },
  { $graphLookup: {
      from: "cats",                  // collection to walk (can be the same one)
      startWith: "$_id",             // start from Food's _id ...
      connectFromField: "_id",       // ... take each found node's _id ...
      connectToField: "parent",      // ... and find nodes whose parent equals it (goes DOWN)
      as: "desc",                    // result array
      depthField: "depth"            // adds depth to each found doc
  } },
  { $project: { _id: 0, desc: { $map: { input: "$desc", in: { id: "$$this._id", d: "$$this.depth" } } } } }
])
// Output (real; order of array not guaranteed):
// [ { desc: [ { id: 'Chinese', d: Long('0') }, { id: 'Hyderabadi', d: Long('2') },
//             { id: 'Biryani', d: Long('1') }, { id: 'Indian', d: Long('0') } ] } ]

// All ancestors of Hyderabadi (goes UP: connect parent -> _id)
db.cats.aggregate([
  { $match: { _id: "Hyderabadi" } },
  { $graphLookup: {
      from: "cats", startWith: "$parent",       // begin at its parent
      connectFromField: "parent",               // keep following parent links ...
      connectToField: "_id",                    // ... matching them to _id
      as: "ancestors"
  } },
  { $project: { _id: 0, anc: "$ancestors._id" } }
])
// Output (real): [ { anc: [ 'Biryani', 'Food', 'Indian' ] } ]  (order is not guaranteed; sort by depthField if needed)

// Options worth knowing: maxDepth: 2 (limit recursion), restrictSearchWithMatch: { active: true } (filter nodes),
// and the 100 MB memory limit per $graphLookup stage (cannot spill to disk).
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

const Category = mongoose.model('Category', new Schema({
  _id: String,
  parent: { type: String, index: true, default: null },
  path: { type: String, index: true, default: null }      // materialized path like ",Food,Indian,"
}));

const app = express();

// Direct children (sidebar)
app.get('/categories/:id/children', async (req, res) => {
  res.json(await Category.find({ parent: req.params.id }).lean());
});

// All descendants using the materialized path - escape user input before building a RegExp!
const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
app.get('/categories/:id/descendants', async (req, res) => {
  const node = await Category.findById(req.params.id).lean();
  if (!node) return res.status(404).json({ error: 'Not found' });
  const prefix = `${node.path || ','}${node._id},`;           // children's path begins with this
  res.json(await Category.find({ path: new RegExp('^' + escapeRe(prefix)) }).lean());
});

// Breadcrumb with $graphLookup (no path needed)
app.get('/categories/:id/ancestors', async (req, res) => {
  const [row] = await Category.aggregate([
    { $match: { _id: req.params.id } },
    { $graphLookup: { from: 'categories', startWith: '$parent', connectFromField: 'parent', connectToField: '_id', as: 'ancestors', depthField: 'up' } }
  ]);
  res.json(row ? row.ancestors.sort((a, b) => b.up - a.up).map(a => a._id) : []);  // root first
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deeply nested sub-documents as a tree
```javascript
// Wrong — can't index/query "Biryani" at unknown depth, can't re-parent without rewriting the whole doc
{ _id: "Food", children: [ { name: "Indian", children: [ { name: "Biryani", children: [] } ] } ] }
// Right — one document per node with parent / path / ancestors fields
```

❌ Mistake 2: Unanchored regex and unescaped input on the path
```javascript
// Wrong — /,Indian,/ is not anchored: cannot use the index efficiently (scans the whole index),
// and matches any category named Indian anywhere
db.cats.find({ path: /,Indian,/ })
// Right — anchor to the full prefix so the index range-scans:
db.cats.find({ path: /^,Food,Indian,/ })
```
✅ Also: forgetting an index on `connectToField` for `$graphLookup`, and letting trees get so deep that `$graphLookup` hits its memory limit (then use ancestors/path).

---

## 🧠 Tricky Interview Question

You store `path: ",Food,Indian,Biryani,"` and query descendants of "Indian" with `{ path: /^,Food,Indian,/ }`. After renaming the category "Indian" to "Desi", what must you do?

Answer: Rename affects every descendant's stored `path` (they each contain ",Indian,"). You must rewrite the prefix for the node itself and all nodes below it, ideally with a single `updateMany({ path: /^,Food,Indian,/ }, [ { $set: { path: { $replaceOne: { input: "$path", find: ",Food,Indian,", replacement: ",Food,Desi," } } } } ])`, plus the node's own `_id` handling (since `_id` is immutable, use a separate `name` field and an opaque id, not the name, as `_id`/path segment). This is the main cost of Materialized Path/Ancestors: **cheap reads, expensive subtree rewrites**. Using stable ids (not display names) in `path` avoids rename rewrites entirely.

---

## ⚫ Interview Questions + Answers

Q1: Which tree model would you use for a comment thread?
A1: Parent References plus a materialized path (or ancestors). Display "all replies to a comment" by prefix match and children by `parent`; sort by path for threaded order. For reddit-scale, also limit depth and paginate by subtree.

Q2: What does `$graphLookup` do and what are its limits?
A2: It performs a recursive search over a collection, following `connectFromField → connectToField` from `startWith`. It supports `maxDepth`, `depthField` and `restrictSearchWithMatch`. Limits: 100 MB memory (no disk spill) and output document limit of 16 MB; it needs an index on `connectToField` for speed.

Q3: Compare Parent Reference vs Array of Ancestors.
A3: Parent: simplest, cheapest moves and writes, slow ancestor/descendant queries. Ancestors: one query gets all descendants (`ancestors: X`) or the full path, but a subtree move updates every descendant and arrays take space.

Q4: Why use stable ids rather than names in a path?
A4: Names change; ids don't. A path of ids never needs a rewrite on rename; only a move changes it.

Q5: How would you fetch a whole subtree in one query?
A5: With ancestors: `find({ ancestors: nodeId })`; with materialized path: anchored regex prefix; with parent refs: `$graphLookup`.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- Parent Reference: frequent re-parenting, simple trees
- Ancestors/Materialized Path: read-heavy hierarchies (catalogs, breadcrumbs)
- `$graphLookup`: occasional traversals, org charts, social graphs (bounded depth)

❌ Avoid:
- Nested sub-documents for trees of unknown depth
- Path/ancestors models for trees where whole subtrees are reorganised constantly
- `$graphLookup` for huge, deep graphs in hot request paths

---

## 📊 Visual Diagram
```
            Food
           /    \
       Indian   Chinese
         |
      Biryani
         |
     Hyderabadi

Parent ref:    Hyderabadi { parent: "Biryani" }
Ancestors:     Hyderabadi { ancestors: ["Food","Indian","Biryani"] }
Mat. path:     Hyderabadi { path: ",Food,Indian,Biryani," }
$graphLookup:  start Food ──parent<-_id──► Indian,Chinese ──► Biryani ──► Hyderabadi
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parent reference | Node stores its parent id | Node में parent का id |
| Materialized path | Path string stored on each node | हर node पर path string |
| Array of ancestors | Node stores all ancestor ids | सभी ancestors के ids |
| `$graphLookup` | Recursive lookup stage | Recursive lookup stage |
| depthField | Distance from start in results | Start से दूरी |
| Subtree move | Re-parenting a node and its children | Node + children को दूसरे parent में ले जाना |
| Anchored regex | Regex starting with `^` | `^` से शुरू regex |

---

## ⚡ 3-Line Summary
English:
1. Store one document per node and choose parent references, ancestors or materialized path based on whether you mostly move nodes or read subtrees.
2. `$graphLookup` traverses parent/child links recursively inside the database (index `connectToField`).
3. Use stable ids in paths, anchor prefix regexes, and avoid deeply nested sub-documents.

Hindi:
1. हर node का एक document रखो और parent references, ancestors या materialized path इस आधार पर चुनो कि nodes ज़्यादा move होते हैं या subtrees ज़्यादा पढ़े जाते हैं।
2. `$graphLookup` parent/child links को database में recursively चलता है (`connectToField` पर index लगाओ)।
3. Paths में stable ids इस्तेमाल करो, prefix regex anchor करो, और गहरे nested sub-documents से बचो।

---

## ➡️ Next Topic
**77. Anti-Patterns — Unbounded Arrays, Massive Documents** — how schemas go wrong and how to fix them.
