# 64. $graphLookup
# हिंदी में: $graphLookup

---

## 🔵 Simple Definition (English)
**`$graphLookup`** performs a **recursive** search on a collection. Starting from a value in the current document, it repeatedly follows a link field (like `boss` or `parentId`) to find connected documents: a whole management chain, a category tree, or a friend network, in one stage.

## 🔵 सरल परिभाषा (Hindi)
**`$graphLookup`** collection पर **recursive** search करता है। मौजूदा document की किसी value से शुरू करके यह बार-बार link field (जैसे `boss` या `parentId`) follow करता है और जुड़े हुए documents ढूँढता है: पूरी management chain, category tree या friend network, एक ही stage में।

---

## 🔴 Problem it Solves
Hierarchies have unknown depth. "Who are all the managers above Dev?" with `$lookup` needs one join per level and you do not know how many levels exist. `$graphLookup` walks the graph for you until no new documents are found (or `maxDepth` is reached).

## 🔴 यह क्यों बना? (Hindi)
Hierarchies की depth पहले से पता नहीं होती। "Dev के ऊपर सारे managers कौन हैं?" `$lookup` से हर level के लिए एक join चाहिए और levels कितने हैं पता नहीं। `$graphLookup` तब तक graph में चलता है जब तक नए documents मिलना बंद न हो जाएँ (या `maxDepth` आ जाए)।

---

## 🟢 How it Works — Step by Step

Step 1 → `from`: the collection to search (often the same collection).
Step 2 → `startWith`: expression giving the first value(s) to look for, e.g. `"$boss"`.
Step 3 → `connectToField`: field in `from` compared with the current value, e.g. `name`.
Step 4 → `connectFromField`: field of each found document whose value becomes the NEXT search value, e.g. `boss`.
Step 5 → Repeats until nothing new is found. Results go into the `as` array (unordered!). `depthField` records the hop number (0 = first hop). `maxDepth` limits recursion; `restrictSearchWithMatch` filters.
Step 6 → Index `connectToField` (e.g. `name`) or each hop does a collection scan. The `as` array must fit in 16 MB.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `from`: जिस collection में खोजना है (अक्सर वही collection)।
Step 2 → `startWith`: पहली value(s) देने वाला expression, जैसे `"$boss"`।
Step 3 → `connectToField`: `from` का field जिससे मौजूदा value compare होती है, जैसे `name`।
Step 4 → `connectFromField`: मिले हुए document का field जिसकी value अगली search value बनती है, जैसे `boss`।
Step 5 → तब तक दोहराता है जब तक कुछ नया न मिले। नतीजे `as` array में जाते हैं (क्रम तय नहीं!)। `depthField` hop number लिखता है (0 = पहला hop)। `maxDepth` recursion सीमित करता है; `restrictSearchWithMatch` filter करता है।
Step 6 → `connectToField` (जैसे `name`) पर index बनाओ वरना हर hop पर collection scan होगा। `as` array 16 MB में आना चाहिए।

---

## 🟡 Real World Example
**Flipkart's category tree**: `Electronics > Mobiles > Smartphones`, each category stores `parentId`. To list all sub-categories under Electronics (any depth) for a filter menu, `$graphLookup` starts at Electronics and follows `parentId` links downward. The same idea powers org charts (Razorpay HR) and "people you may know" (friend-of-friend with `maxDepth: 2`).

## 🟡 Real Example Hindi mein
**Flipkart का category tree**: `Electronics > Mobiles > Smartphones`, हर category `parentId` रखती है। Filter menu के लिए Electronics के नीचे की सभी sub-categories (किसी भी depth तक) `$graphLookup` से मिलती हैं, जो Electronics से शुरू होकर `parentId` links नीचे की ओर follow करता है। यही idea org charts (HR) और "people you may know" (friend-of-friend, `maxDepth: 2`) में चलता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4
// emp: {_id:1,name:"CEO"}, {_id:2,name:"VP",boss:"CEO"}, {_id:3,name:"Mgr",boss:"VP"}, {_id:4,name:"Dev",boss:"Mgr"}
db.emp.aggregate([
  { $match: { name: "Dev" } },                       // start from Dev
  { $graphLookup: {
      from: "emp",                                   // search the same collection
      startWith: "$boss",                            // first value to look for: "Mgr"
      connectFromField: "boss",                      // after finding a doc, next search value = its boss
      connectToField: "name",                        // compare against emp.name
      as: "chain",                                   // all ancestors land here
      depthField: "lvl"                              // 0 for first hop, 1 for next, ...
  } },
  { $project: { name: 1, "chain.name": 1, "chain.lvl": 1 } }
])
// Output (real; the chain order is NOT guaranteed, lvl is a 64-bit number):
// { _id: 4, name: 'Dev', chain: [
//     { name: 'CEO', lvl: Long('2') },
//     { name: 'VP',  lvl: Long('1') },
//     { name: 'Mgr', lvl: Long('0') } ] }
```

## 💻 Code Example — Advanced

```javascript
// Limit hops and sort the result into a readable path (Node driver)
const rows = await db.collection("emp").aggregate([
  { $match: { name: "Dev" } },
  { $graphLookup: {
      from: "emp", startWith: "$boss", connectFromField: "boss", connectToField: "name",
      as: "chain", depthField: "lvl",
      maxDepth: 1                                    // only 2 hops: Mgr (0) and VP (1)
  } },
  { $unwind: "$chain" },                             // turn the array into rows
  { $sort: { "chain.lvl": 1 } },                     // closest boss first
  { $group: { _id: "$name", path: { $push: "$chain.name" } } } // rebuild an ordered array
]).toArray();
// Output (real): [{ _id: 'Dev', path: ['Mgr', 'VP'] }]  (CEO is cut off by maxDepth: 1)

// Index that makes each hop an index lookup
await db.collection("emp").createIndex({ name: 1 });
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/emp/:name/chain (Mongoose; same graphLookup pipeline tested in mongosh)
const Emp = mongoose.model("Emp", new mongoose.Schema({ name: String, boss: String }), "emp");

app.get("/api/emp/:name/chain", async (req, res) => {
  const [doc] = await Emp.aggregate([
    { $match: { name: req.params.name } },
    { $graphLookup: { from: "emp", startWith: "$boss", connectFromField: "boss",
                      connectToField: "name", as: "chain", depthField: "lvl" } }
  ]);
  if (!doc) return res.status(404).json({ error: "Not found" });
  // sort in JS because the chain array is unordered: closest boss first
  res.json(doc.chain.sort((a, b) => a.lvl - b.lvl).map(c => c.name));  // ["Mgr","VP","CEO"]
});
```
Note: `from` is the collection NAME (`"emp"`), not the Mongoose model name.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Swapping `connectFromField` and `connectToField`
```javascript
// Wrong for "go up" — this walks DOWN the tree (finds subordinates). Starting at CEO it returns VP, Mgr, Dev (verified)
{ connectFromField: "name", connectToField: "boss" }
// Right for "go up": from the found doc's boss -> match a doc's name
{ connectFromField: "boss", connectToField: "name" }
```

❌ Mistake 2: Assuming `as` is ordered
✅ Order is not guaranteed. Use `depthField` and sort (as above).

❌ Mistake 3: No index and no `maxDepth` on big trees
✅ Each hop queries the collection. Index `connectToField`, and set `maxDepth` for large or cyclic graphs.

---

## 🧠 Tricky Interview Question
Q: What is `lvl` for the direct boss, 0 or 1?
Answer: 0. `depthField` counts hops starting at zero for the documents matched by `startWith`. In our output Mgr (Dev's direct boss) has lvl 0, VP 1, CEO 2. Also `maxDepth: 0` means a single hop (same as a `$lookup`). And cycles are safe: each document is visited once.

---

## ⚫ Interview Questions + Answers

Q1: What does `$graphLookup` do that `$lookup` cannot?
A1: Recursion with unknown depth: transitive closure over a link field.

Q2: What are `connectFromField` and `connectToField`?
A2: `connectFromField` is read from each found document to produce the next search values; `connectToField` is the field in `from` that is matched against them.

Q3: How to limit work?
A3: `maxDepth`, `restrictSearchWithMatch`, and indexing `connectToField`.

Q4: Common schema choices for trees in MongoDB?
A4: Parent reference (works with `$graphLookup`), child references, materialized path, nested sets. `$graphLookup` suits parent references.

Q5: Limits?
A5: Result array in the 16 MB doc limit, stage memory limit of 100 MB (spills to disk with `allowDiskUse`), and `from` cannot be sharded in older versions (allowed from 5.1).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Org charts, category trees, bill of materials, social graphs
- Depth is unknown

❌ Avoid when:
- Depth is fixed and small (plain `$lookup`s or embedding)
- Tree is huge and read often (store a materialized path instead)

---

## 📊 Visual Diagram
```
 CEO ◄── VP ◄── Mgr ◄── Dev
  ▲       ▲       ▲       │ start: Dev.boss = "Mgr"
  │lvl 2  │lvl 1  │lvl 0  │
  └───────┴───────┴───────┘
 hop0: find name="Mgr" -> its boss "VP"
 hop1: find name="VP"  -> its boss "CEO"
 hop2: find name="CEO" -> no boss, stop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$graphLookup` | Recursive lookup | Recursive lookup |
| `startWith` | First search value | पहली search value |
| `connectFromField` | Field giving next value | अगली value देने वाला field |
| `connectToField` | Field matched in `from` | `from` में match होने वाला field |
| `depthField` | Records hop number | Hop number लिखता है |
| `maxDepth` | Limits recursion | Recursion की सीमा |

---

## ⚡ 3-Line Summary
English:
1. `$graphLookup` follows a link field recursively (org chart, category tree).
2. `connectFromField` = next value source, `connectToField` = field to match; `as` is unordered.
3. Index `connectToField`, set `maxDepth`, sort by `depthField`.

Hindi:
1. `$graphLookup` link field को recursively follow करता है (org chart, category tree)।
2. `connectFromField` = अगली value का source, `connectToField` = match होने वाला field; `as` unordered है।
3. `connectToField` पर index बनाओ, `maxDepth` लगाओ, `depthField` से sort करो।

---

## ➡️ Next Topic
**65. $expr, $cond, $switch Expressions** — conditional logic inside queries and pipelines.
