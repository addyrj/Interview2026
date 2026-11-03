# 71. One-to-One, One-to-Many, Many-to-Many Modeling
# हिंदी में: One-to-One, One-to-Many, Many-to-Many Modeling

---

## 🔵 Simple Definition (English)
**Relationship modeling** decides how two kinds of entities are linked: **1:1** (user ↔ profile), **1:N** (restaurant → menu items; split into *one-to-few*, *one-to-many*, *one-to-squillions*), and **N:N** (students ↔ courses). MongoDB offers two tools — embed or reference — and the right combination depends on *how many* related items there are and *how they are read*. The MongoDB blog's classification: one-to-few (embed), one-to-many (array of references or parent-reference), one-to-squillions (always reference from the child to the parent).

## 🔵 सरल परिभाषा (Hindi)
**Relationship modeling** तय करती है कि दो तरह की entities कैसे जुड़ें: **1:1** (user ↔ profile), **1:N** (restaurant → menu items; इसे *one-to-few*, *one-to-many*, *one-to-squillions* में बाँटा जाता है), और **N:N** (students ↔ courses)। MongoDB के दो औज़ार हैं — embed या reference — और सही combination इस पर निर्भर है कि related items *कितने* हैं और *कैसे पढ़े* जाते हैं। MongoDB blog का वर्गीकरण: one-to-few (embed), one-to-many (references का array या parent-reference), one-to-squillions (हमेशा child से parent का reference)।

---

## 🔴 Problem it Solves
Without a rule per cardinality people use one approach everywhere: an array of ids that grows into millions, or a collection per relationship even for 2 phone numbers. Models for many-to-many are especially error-prone: storing ids on the wrong side forces a full scan to answer "which students take DBMS?". Clear patterns give you: bounded documents, index-backed lookups in both directions, and updates that stay cheap.

## 🔴 यह क्यों बना? (Hindi)
हर cardinality के लिए नियम न हो तो लोग हर जगह एक ही तरीका लगाते हैं: ids का array जो लाखों तक बढ़ जाता है, या 2 phone numbers के लिए भी अलग collection। Many-to-many में गलती ज़्यादा होती है: ids गलत तरफ़ रखने पर "कौन से students DBMS लेते हैं?" का जवाब पूरे scan से मिलता है। साफ़ patterns से documents bounded रहते हैं, दोनों दिशाओं में index-backed lookup मिलता है, और updates सस्ते रहते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **1:1**: embed as a sub-object (`user.profile`) unless the part is large/rarely read (then separate doc with same `_id` or a reference).
Step 2 → **One-to-few** (a handful: addresses, phone numbers): embed an array.
Step 3 → **One-to-many** (hundreds to thousands, e.g. menu items of a restaurant, products of a part): either an array of child `_id`s in the parent, or `parentId` in each child with an index — pick by which side you query from.
Step 4 → **One-to-squillions** (millions: logs, events, reviews): never an array in the parent; the child stores `parentId` and you index `{ parentId: 1, createdAt: -1 }`.
Step 5 → **Many-to-many**: store an array of ids on the side that is small and bounded (`student.courseIds`), add a multikey index, and for the reverse direction query that index. For unbounded both ways use a **junction collection** (`enrollments { studentId, courseId }`) with two indexes.
Step 6 → Join when needed with `$lookup` (arrays of ids work directly as `localField`) or `populate()`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **1:1**: sub-object के रूप में embed (`user.profile`), जब तक वह हिस्सा बड़ा/कम पढ़ा जाने वाला न हो (तब वही `_id` वाला अलग doc या reference)।
Step 2 → **One-to-few** (मुट्ठी भर: addresses, phone numbers): array embed करो।
Step 3 → **One-to-many** (सैकड़ों से हज़ारों, जैसे restaurant के menu items): या तो parent में child `_id`s का array, या हर child में `parentId` + index — चुनाव इस पर कि किस तरफ़ से query करते हो।
Step 4 → **One-to-squillions** (लाखों: logs, events, reviews): parent में कभी array नहीं; child में `parentId` रखो और `{ parentId: 1, createdAt: -1 }` पर index।
Step 5 → **Many-to-many**: छोटी और bounded तरफ़ ids का array (`student.courseIds`), multikey index, और उल्टी दिशा के लिए उसी index से query। दोनों तरफ़ unbounded हो तो **junction collection** (`enrollments { studentId, courseId }`) और दो indexes।
Step 6 → ज़रूरत पर `$lookup` (ids का array सीधे `localField` बन सकता है) या `populate()` से join।

---

## 🟡 Real World Example
**Unacademy-style platform**: a **user ↔ profile** is 1:1 (embedded `profile`). A user has **3 saved addresses** (one-to-few, embedded). A **course has 300 lessons** (one-to-many: lessons reference `courseId`). **Students ↔ courses** is many-to-many: a student has at most ~50 enrolled courses, so `courseIds` lives on the student with an index, while a course with 5 lakh students is answered by the same index. Millions of **lesson-progress events** (one-to-squillions) go into `progress` with `studentId` + `lessonId`.

## 🟡 Real Example Hindi mein
**Unacademy जैसा platform**: **user ↔ profile** 1:1 है (embedded `profile`)। एक user के **3 saved addresses** (one-to-few, embedded)। **एक course में 300 lessons** (one-to-many: lessons में `courseId` reference)। **Students ↔ courses** many-to-many है: एक student के ज़्यादा से ज़्यादा ~50 courses, इसलिए `courseIds` student पर index के साथ, और 5 लाख students वाले course का जवाब उसी index से मिलता है। लाखों **lesson-progress events** (one-to-squillions) `progress` में `studentId` + `lessonId` के साथ।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4)
use t71

// 1:1 and one-to-few -> embed
db.users.insertOne({
  _id: "u1",
  name: "Asha",
  profile: { bio: "Learner", avatar: "a.png" },            // 1:1 sub-object
  addresses: [ { label: "home", pin: "411001" },           // one-to-few array
               { label: "work", pin: "560034" } ]
})

// one-to-squillions -> child holds the parent id, indexed for "events of a user, latest first"
db.progress.insertOne({ studentId: "u1", lessonId: "l9", watched: 0.8, at: new Date() })
db.progress.createIndex({ studentId: 1, at: -1 })          // compound: equality then sort

// MANY-TO-MANY with ids on the small side
db.students.insertMany([
  { _id: "s1", name: "Asha", courseIds: ["c1", "c2"] },
  { _id: "s2", name: "Ravi", courseIds: ["c2"] }
])
db.courses.insertMany([ { _id: "c1", title: "DSA" }, { _id: "c2", title: "DBMS" } ])
db.students.createIndex({ courseIds: 1 })                  // multikey index: one entry per array element

// Which students take DBMS? -> index lookup on the array element
db.students.find({ courseIds: "c2" }, { name: 1, _id: 0 })
// Output: [ { name: 'Asha' }, { name: 'Ravi' } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — join many-to-many, and the junction collection for unbounded N:N

// 1) $lookup with an ARRAY localField: matches every element against foreignField
db.students.aggregate([
  { $lookup: { from: "courses", localField: "courseIds", foreignField: "_id", as: "courses" } },
  { $project: { name: 1, "courses.title": 1 } }          // keep only the titles
])
// Output (real, order of courses follows collection order):
// [ { _id: 's1', name: 'Asha', courses: [ { title: 'DBMS' }, { title: 'DSA' } ] },
//   { _id: 's2', name: 'Ravi', courses: [ { title: 'DBMS' } ] } ]

// 2) Junction collection (both sides can be huge, e.g. users <-> followed creators)
db.enrollments.insertMany([
  { studentId: "s1", courseId: "c1", enrolledAt: new Date("2026-01-10") },
  { studentId: "s1", courseId: "c2", enrolledAt: new Date("2026-01-11") },
  { studentId: "s2", courseId: "c2", enrolledAt: new Date("2026-02-01") }
])
db.enrollments.createIndex({ studentId: 1, courseId: 1 }, { unique: true }) // also prevents double enrollment
db.enrollments.createIndex({ courseId: 1 })                                   // reverse direction: students of a course

db.enrollments.countDocuments({ courseId: "c2" })       // how many students in DBMS?
// Output: 2

// 3) Remove a course from a student atomically ($pull on an array) and keep the index consistent
db.students.updateOne({ _id: "s1" }, { $pull: { courseIds: "c1" } })
// Output: { acknowledged: true, insertedId: null, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }
// (junction collection: just deleteOne({studentId:"s1",courseId:"c1"}))
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const mongoose = require('mongoose');
const express = require('express');
const { Schema } = mongoose;

// N:N with ids on the student side; ref enables populate()
const Course = mongoose.model('Course', new Schema({ title: String }));
const Student = mongoose.model('Student', new Schema({
  name: String,
  courses: [{ type: Schema.Types.ObjectId, ref: 'Course', index: true }] // multikey index on the array
}));

const app = express();
app.use(express.json());

// Enroll: $addToSet avoids duplicates (idempotent), unlike $push
app.post('/students/:id/enroll/:courseId', async (req, res) => {
  const r = await Student.updateOne(
    { _id: req.params.id },
    { $addToSet: { courses: req.params.courseId } }   // Mongoose casts the string to ObjectId
  );
  res.json({ modified: r.modifiedCount });
});

// Student with course titles
app.get('/students/:id', async (req, res) => {
  const s = await Student.findById(req.params.id).populate('courses', 'title').lean();
  s ? res.json(s) : res.status(404).json({ error: 'Not found' });
});

// Students of a course: the reverse direction uses the multikey index
app.get('/courses/:id/students', async (req, res) => {
  res.json(await Student.find({ courses: req.params.id }, 'name').lean());
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: One-to-squillions as an array in the parent
```javascript
// Wrong — a popular creator with 5M followers: array hits 16 MB, every follow rewrites a giant doc
db.creators.updateOne({ _id: "c1" }, { $push: { followers: "u9" } })
// Right — junction/child docs: { creatorId, followerId } with unique compound index
db.follows.insertOne({ creatorId: "c1", followerId: "u9" })
```

❌ Mistake 2: Many-to-many ids with no index (or on the huge side)
```javascript
// Wrong — find({ courseIds: "c2" }) scans every student
// Right
db.students.createIndex({ courseIds: 1 })
```
✅ Also: using `$push` instead of `$addToSet` and creating duplicate ids in the array.

---

## 🧠 Tricky Interview Question

In `students.courseIds` you index the array. A student has 3 courses. How many index entries does that one document create, and what does `db.students.find({ courseIds: ["c1","c2"] })` match?

Answer: A **multikey index** creates one entry **per array element** (3 entries). The query `{ courseIds: ["c1","c2"] }` is an **exact array match**: it matches only documents where `courseIds` is exactly `["c1","c2"]` in that order (or contains that array as an element). To find students enrolled in *both* use `{ courseIds: { $all: ["c1","c2"] } }`, and for *either*, `{ courseIds: { $in: ["c1","c2"] } }`.

---

## ⚫ Interview Questions + Answers

Q1: What are the three kinds of one-to-N?
A1: One-to-few (embed an array), one-to-many (array of references or `parentId` on children), one-to-squillions (always `parentId` on the child, never an array on the parent) — based on how large N can grow.

Q2: How do you model many-to-many in MongoDB?
A2: Put an array of ids on the side with the smaller, bounded count (add a multikey index) or, if both sides are unbounded, use a junction collection with a unique compound index and an index on each direction.

Q3: Where should the foreign key live in a 1:N relationship?
A3: On the "many" (child) side when N is large (`review.restaurantId`); in the parent as an array only when N is bounded and you usually read children from the parent.

Q4: How is a 1:1 relationship modeled when part of it is big?
A4: Embed the small, hot fields in the main doc and move the large/rare part (e.g. KYC document scans) to another collection keyed by the same `_id` or referencing it — read it only when needed.

Q5: How do you keep a many-to-many consistent when deleting a course?
A5: With the array approach, `updateMany({ courseIds: id }, { $pull: { courseIds: id } })` (ideally in a transaction if both collections must change atomically); with a junction collection, `deleteMany({ courseId: id })`.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- Arrays of ids on the small side when N is bounded (< a few hundred)
- Junction collection when relationships carry data (enrolledAt, role) or are unbounded
- Child-to-parent reference for logs/events/reviews

❌ Avoid:
- Unbounded arrays in a parent document
- Referencing for 1:1 data that is always read with the parent

---

## 📊 Visual Diagram
```
1:1           user ─────────► { profile: {...} }            (embed)
1:few         user ─────────► { addresses: [a, b, c] }       (embed array)
1:many        restaurant ◄──── menuItem.restaurantId         (child ref, index)
1:squillions  creator    ◄──── follow { creatorId, followerId }  (junction/child)

N:N (bounded one side)             N:N (both unbounded)
 student { courseIds:[c1,c2] }      enrollments { studentId, courseId }
   multikey index on courseIds        idx(studentId,courseId) unique
                                      idx(courseId)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cardinality | How many items relate | कितने items जुड़े हैं |
| One-to-squillions | Unbounded child count | असीमित child count |
| Junction collection | Collection storing relation pairs | Relation pairs की collection |
| Multikey index | Index entry per array element | Array के हर element की entry |
| `$addToSet` | Add to array only if absent | नहीं हो तो ही जोड़ना |
| `$all` / `$in` | Match all / any of listed values | सभी / कोई एक |
| `$pull` | Remove matching items from array | Array से हटाना |

---

## ⚡ 3-Line Summary
English:
1. 1:1 and one-to-few embed; one-to-many references either way; one-to-squillions always child-to-parent.
2. Many-to-many: ids array on the small side with a multikey index, or a junction collection when both sides grow.
3. Index every reference field, use `$addToSet` to avoid duplicates, and never keep unbounded arrays in a parent.

Hindi:
1. 1:1 और one-to-few embed; one-to-many में reference किसी भी तरफ़; one-to-squillions में हमेशा child से parent।
2. Many-to-many: छोटी तरफ़ ids का array + multikey index, या दोनों तरफ़ बढ़ें तो junction collection।
3. हर reference field पर index, duplicates से बचने को `$addToSet`, और parent में unbounded array कभी नहीं।

---

## ➡️ Next Topic
**72. Schema Design Patterns — Bucket, Outlier, Computed** — tame time-series data, rare giants and expensive recalculations.
