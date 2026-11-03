# 120. Leaderboard with Aggregation
# हिंदी में: Aggregation से Leaderboard

---

## 🔵 Simple Definition (English)
A **leaderboard** ranks players (or sellers, drivers, merchants) by a score. With MongoDB you either **compute** the ranking on demand — `$group` to total the scores, then `$setWindowFields` with `$rank`/`$denseRank` (5.0+) — or **store** one running total per player with an index on the score for instant top-N reads and a cheap rank lookup (`count of players with a higher score + 1`).

## 🔵 सरल परिभाषा (Hindi)
**Leaderboard** खिलाड़ियों (या sellers, drivers, merchants) को उनके score से rank करता है। MongoDB में आप या तो ranking माँग पर **compute** करते हैं — scores का total `$group` से, फिर `$rank`/`$denseRank` वाला `$setWindowFields` (5.0+) — या हर player का एक running total **store** करते हैं जिसपर score का index हो, ताकि top-N तुरंत मिले और rank (`ज़्यादा score वाले players की गिनती + 1`) सस्ते में निकले।

---

## 🔴 Problem it Solves
Naively sorting and numbering players in application code means loading every score. Real leaderboards need: (1) *total score across many matches* (aggregate), (2) **ties** handled fairly (two players with 110 points share rank 2, the next is rank 4 or 3), (3) "what is MY rank?" for a user who is not in the top 10, (4) fast reads when millions of players are playing and scores change every second. Choosing between compute-on-read and a precomputed score changes cost by orders of magnitude.

## 🔴 यह क्यों बना? (Hindi)
Application code में players को sort करके number देने का मतलब है हर score लोड करना। असली leaderboards को चाहिए: (1) *कई matches का कुल score* (aggregate), (2) **ties** का न्यायसंगत handling (110 points वाले दो players rank 2 साझा करें, अगला rank 4 या 3), (3) top 10 से बाहर के user के लिए "मेरा rank क्या है?", (4) जब लाखों players खेल रहे हों और scores हर सेकंड बदलें तब तेज़ reads। compute-on-read या precomputed score का चुनाव cost में कई गुना फर्क डालता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Raw events**: `scores { p, g, pts }` — one doc per match result (append-only, audit-friendly).
Step 2 → **Total per player**: `$group: { _id: "$p", total: { $sum: "$pts" } }`.
Step 3 → **Rank**: `$setWindowFields: { sortBy: { total: -1 }, output: { rank: { $rank: {} }, dense: { $denseRank: {} } } }`. `$rank` leaves gaps after ties (1,2,2,4); `$denseRank` does not (1,2,2,3).
Step 4 → **Top N**: `$sort` + `$limit` after ranking (or `$sort`+`$limit` before when you do not need rank numbers).
Step 5 → **A user's rank**: count how many totals are strictly greater and add 1. In a pipeline: group → `$match: { total: { $gt: myTotal } }` → `$count`.
Step 6 → **Precomputed board (scale)**: keep a `leaderboard { _id: player, pts }` collection updated with `$inc` on every score event, with index `{ pts: -1 }`. Top-N = `find().sort({ pts: -1 }).limit(N)` (index scan of N entries). Rank = `countDocuments({ pts: { $gt: myPts } }) + 1` (index-only count).
Step 7 → **Periodic boards** (daily/weekly): add a `period` field (`"2026-W10"`) to the key or `$match` on a date range before `$group`.
Step 8 → **Heavy loads**: Redis sorted sets (`ZADD/ZREVRANK`) are an alternative for million-per-second updates; MongoDB is fine for most apps and is the durable source of truth.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Raw events**: `scores { p, g, pts }` — हर match result का एक doc (append-only, audit के लिए अच्छा)।
Step 2 → **हर player का total**: `$group: { _id: "$p", total: { $sum: "$pts" } }`।
Step 3 → **Rank**: `$setWindowFields: { sortBy: { total: -1 }, output: { rank: { $rank: {} }, dense: { $denseRank: {} } } }`। `$rank` ties के बाद gap छोड़ता है (1,2,2,4); `$denseRank` नहीं (1,2,2,3)।
Step 4 → **Top N**: ranking के बाद `$sort` + `$limit` (या rank number न चाहिए तो पहले ही `$sort`+`$limit`)।
Step 5 → **किसी user का rank**: strictly ज़्यादा totals गिनो और 1 जोड़ो। Pipeline में: group → `$match: { total: { $gt: myTotal } }` → `$count`।
Step 6 → **Precomputed board (scale)**: `leaderboard { _id: player, pts }` collection रखो जो हर score event पर `$inc` से update हो, और index `{ pts: -1 }`। Top-N = `find().sort({ pts: -1 }).limit(N)` (सिर्फ N index entries)। Rank = `countDocuments({ pts: { $gt: myPts } }) + 1` (index-only count)।
Step 7 → **Periodic boards** (daily/weekly): key में `period` field (`"2026-W10"`) जोड़ो या `$group` से पहले date range पर `$match` करो।
Step 8 → **भारी load**: लाखों updates प्रति सेकंड के लिए Redis sorted sets (`ZADD/ZREVRANK`) विकल्प हैं; ज़्यादातर apps के लिए MongoDB ठीक है और durable source of truth रहता है।

---

## 🟡 Real World Example
**Dream11-style fantasy contests** and **Swiggy's "top delivery partners this week"** rank users by points. Each match result is stored as an event; the contest page shows the top 50 plus "Your rank: 1,284" for the logged-in user. The weekly board stores `{ week, userId, pts }` and uses `$inc` per event with an index on `{ week: 1, pts: -1 }` so both reads stay fast even with millions of players.

## 🟡 Real Example Hindi mein
**Dream11 जैसे fantasy contests** और **Swiggy के "इस हफ्ते के top delivery partners"** users को points से rank करते हैं। हर match result event की तरह store होता है; contest page top 50 और लॉग-इन user के लिए "Your rank: 1,284" दिखाता है। Weekly board `{ week, userId, pts }` रखता है, हर event पर `$inc` करता है, और `{ week: 1, pts: -1 }` पर index होता है ताकि लाखों players के बावजूद दोनों reads तेज़ रहें।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
use("game");
db.scores.insertMany([
  { p: "Ravi",  g: "g1", pts: 50 },  { p: "Asha",  g: "g1", pts: 70 },
  { p: "Ravi",  g: "g2", pts: 60 },  { p: "Kunal", g: "g1", pts: 120 },
  { p: "Asha",  g: "g2", pts: 40 },  { p: "Meera", g: "g1", pts: 60 }
]);

// Total per player, then rank with BOTH tie styles
db.scores.aggregate([
  { $group: { _id: "$p", total: { $sum: "$pts" } } },       // Ravi 110, Asha 110, Kunal 120, Meera 60
  { $setWindowFields: {
      sortBy: { total: -1 },                                 // highest first
      output: {
        rank:  { $rank: {} },                                // ties share rank, then a GAP
        dense: { $denseRank: {} }                            // ties share rank, NO gap
      }
  } },
  { $sort: { rank: 1, _id: 1 } }                             // stable output order
]);
// Output (JSON):
// [ {_id:"Kunal", total:120, rank:1, dense:1},
//   {_id:"Asha",  total:110, rank:2, dense:2},
//   {_id:"Ravi",  total:110, rank:2, dense:2},
//   {_id:"Meera", total:60,  rank:4, dense:3} ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — "what is MY rank?" and the precomputed leaderboard. Tested on 8.0.4
use("game");

// A) Rank of Meera (total 60) = players with a strictly higher total + 1
const myTotal = 60;
const ahead = db.scores.aggregate([
  { $group: { _id: "$p", total: { $sum: "$pts" } } },
  { $match: { total: { $gt: myTotal } } },                   // strictly greater
  { $count: "ahead" }
]).toArray()[0].ahead;                                       // Output: 3
const myRank = ahead + 1;                                    // Output: 4  (matches $rank above)

// B) Precomputed leaderboard: one doc per player, updated atomically per event
db.lb.createIndex({ pts: -1 });                              // makes top-N and rank counts index scans
db.lb.insertMany([{ _id: "a", pts: 10 }, { _id: "b", pts: 30 }, { _id: "c", pts: 20 }]);

// New score event: upsert + $inc is atomic, no read-modify-write race
db.lb.updateOne({ _id: "a" }, { $inc: { pts: 5 } }, { upsert: true });

// Top 2 (reads only 2 index entries)
db.lb.find().sort({ pts: -1 }).limit(2).toArray();
// Output (before the update above): [ {_id:'b',pts:30}, {_id:'c',pts:20} ]

// Rank of player c (pts 20): count strictly higher + 1, uses the pts index
db.lb.countDocuments({ pts: { $gt: 20 } }) + 1;              // Output: 2 (before player a moved to 15)

// C) Weekly board: filter the period BEFORE grouping so the index on (week, pts) can be used
// db.weekly.createIndex({ week: 1, pts: -1 });
// db.weekly.find({ week: "2026-W10" }).sort({ pts: -1 }).limit(50);
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const boardSchema = new mongoose.Schema({
  _id: String,                   // player id
  pts: { type: Number, default: 0, index: -1 }, // descending index for ranking
});
const Board = mongoose.model('Board', boardSchema);

// POST /score  { player, pts } — atomic increment, creates the player if missing
app.post('/score', async (req, res) => {
  const pts = Number(req.body.pts);
  if (!Number.isFinite(pts)) return res.status(400).json({ error: 'pts must be a number' });
  await Board.updateOne({ _id: String(req.body.player) }, { $inc: { pts } }, { upsert: true });
  res.sendStatus(204);
});

// GET /leaderboard?limit=10 — top N plus the caller's own rank
app.get('/leaderboard', async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 10, 100);
  const top = await Board.find().sort({ pts: -1, _id: 1 }).limit(limit).lean();
  let me = null;
  if (req.query.player) {
    const doc = await Board.findById(req.query.player).lean();
    if (doc) me = { pts: doc.pts, rank: (await Board.countDocuments({ pts: { $gt: doc.pts } })) + 1 };
  }
  res.json({ top, me });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Read-modify-write for scores
```javascript
// Wrong — two concurrent events overwrite each other (lost update)
const p = await Board.findById(id); p.pts += 10; await p.save();

// Right — atomic server-side increment
await Board.updateOne({ _id: id }, { $inc: { pts: 10 } }, { upsert: true });
```

❌ Mistake 2: Using array index as the rank
✅ Correct: Position in a sorted array ignores ties (two players with 110 points would get ranks 2 and 3). Use `$rank` / `$denseRank`, or count strictly greater scores + 1.

❌ Mistake 3: Recomputing `$group` over millions of events on every request
✅ Correct: Maintain a precomputed totals collection (or a `$merge`d materialized view refreshed every minute) and index the score.

❌ Mistake 4: No tie-breaker in `sort`
✅ Correct: `sort({ pts: -1, _id: 1 })` so equal scores always appear in the same order across pages.

---

## 🧠 Tricky Interview Question

```javascript
// Totals: Kunal 120, Asha 110, Ravi 110, Meera 60.
// What are the ranks with $rank and with $denseRank, and what is Meera's rank
// via "count of strictly higher totals + 1"?
```
Answer: `$rank` → 1, 2, 2, **4**; `$denseRank` → 1, 2, 2, **3**; the count method gives 3 higher + 1 = **4**, i.e. it matches `$rank` (competition ranking, like Olympic medals). Which is "correct" is a product decision, so state it. In the interview also mention that the count approach is O(number of players ahead) and fine for a one-off rank, but for rank of every player use window functions.

---

## ⚫ Interview Questions + Answers

Q1: How do you compute a leaderboard from raw score events?
A1: `$group` by player with `$sum`, then `$setWindowFields` with `sortBy: { total: -1 }` and `$rank` / `$denseRank`, then `$sort` and `$limit`. Add a `$match` before the group for time periods.

Q2: How do you get one user's rank without ranking everyone?
A2: Count players with a strictly higher score and add 1 (`countDocuments({ pts: { $gt: myPts } }) + 1`) against an indexed `pts`. That is an index-only count, no sort of the whole board.

Q3: How do you keep reads fast with millions of players?
A3: Maintain precomputed totals via `$inc` (atomic), index `{ pts: -1 }`, serve top-N from the index, cache the top list for a few seconds, and refresh derived boards with `$merge` on a schedule. For extreme update rates use Redis sorted sets and persist in MongoDB.

Q4: How do you handle ties?
A4: Decide the policy: shared rank with gaps (`$rank`), without gaps (`$denseRank`), or unique rank using a tie-breaker such as earliest achievement time (`$rowNumber` with `sortBy: { pts: -1, updatedAt: 1 }`).

Q5: Can the leaderboard be partitioned (per game/region)?
A5: Yes: `partitionBy: "$game"` in `$setWindowFields`, or keep a `{ game, pts }` compound index with per-game queries (`{ game: 1, pts: -1 }`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Rankings change at moderate rates and need durable history (MongoDB as source of truth)
- You need period boards, partitions and ties handled with real queries

❌ Avoid when:
- Millions of rank updates per second with sub-millisecond rank lookup: Redis sorted sets are purpose-built
- You recompute full `$group` over all events on every page view without caching

---

## 📊 Visual Diagram
```
LEADERBOARD
──────────────────────────────────────────────────────
 scores (events)         $group total      $setWindowFields
 Ravi 50, 60  ──┐        Ravi  110 ──┐     sortBy total desc
 Asha 70, 40  ──┼──────► Asha  110 ──┼───► Kunal 120  rank 1  dense 1
 Kunal 120    ──┤        Kunal 120 ──┤     Asha  110  rank 2  dense 2
 Meera 60     ──┘        Meera  60 ──┘     Ravi  110  rank 2  dense 2
                                           Meera  60  rank 4  dense 3

 Scale: lb {_id, pts} + index{pts:-1}
   event ─► $inc pts   top N: IXSCAN N entries   my rank: count(pts > mine)+1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| $rank | Rank with gaps after ties | Ties के बाद gap वाला rank |
| $denseRank | Rank without gaps | बिना gap का rank |
| $rowNumber | Unique position number | अलग-अलग position number |
| $setWindowFields | Window function stage (5.0+) | Window function stage |
| Tie | Equal scores | बराबर scores |
| Materialized view | Precomputed result stored | पहले से निकाला गया result store |
| $inc | Atomic add | Atomic जोड़ |

---

## ⚡ 3-Line Summary
English:
1. Total scores with `$group`, then rank using `$rank` (gaps) or `$denseRank` (no gaps) in `$setWindowFields`.
2. A player's rank is the count of strictly higher scores plus 1, fast with an index on the score.
3. At scale keep a precomputed board updated with atomic `$inc`, index `{ pts: -1 }`, and add a tie-breaker to every sort.

Hindi:
1. Scores का total `$group` से निकालो, फिर `$setWindowFields` में `$rank` (gap) या `$denseRank` (बिना gap) से rank दो।
2. किसी player का rank = strictly ज़्यादा scores की गिनती + 1, score के index से तेज़ होता है।
3. Scale पर atomic `$inc` से update होने वाला precomputed board रखो, `{ pts: -1 }` index लगाओ, और हर sort में tie-breaker जोड़ो।

---

## ➡️ Next Topic
**121. Soft Delete + Audit Log Pattern** — never lose data: `deletedAt`, partial unique indexes and an audit trail.
