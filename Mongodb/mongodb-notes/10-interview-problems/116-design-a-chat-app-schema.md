# 116. Design a Chat App Schema
# हिंदी में: Chat App का Schema Design

---

## 🔵 Simple Definition (English)
A **chat app schema** (WhatsApp/Slack style) stores rooms (1-to-1 or group), the messages inside them, and per-user state such as **read receipts** and **unread counts**. The interview problem tests the classic MongoDB decision: **embed vs reference** (why messages must NOT be embedded in the room), **cursor pagination** by time for infinite scroll, and the right **compound index** `{ roomId, ts }`.

## 🔵 सरल परिभाषा (Hindi)
**Chat app schema** (WhatsApp/Slack जैसा) rooms (1-to-1 या group), उनके अंदर के messages, और हर user की state जैसे **read receipts** और **unread counts** रखता है। यह interview problem MongoDB का क्लासिक फ़ैसला जाँचती है: **embed बनाम reference** (messages को room में embed क्यों नहीं करना), समय के हिसाब से infinite scroll के लिए **cursor pagination**, और सही **compound index** `{ roomId, ts }`।

---

## 🔴 Problem it Solves
Chat rooms grow without bound. If you embed messages in a `rooms` document as an array, the document eventually crosses the **16 MB limit**, every new message rewrites a growing document, and loading the room's header pulls the whole history. Also, "show the last 20 messages, then load older ones as I scroll" with `skip(N)` becomes slower the deeper you scroll. And you need "who has read what" without a write storm for every message in a group of 500.

## 🔴 यह क्यों बना? (Hindi)
Chat rooms बिना सीमा के बढ़ते हैं। अगर messages को `rooms` document में array की तरह embed करो तो document आख़िर **16 MB limit** पार कर लेता है, हर नया message बढ़ते document को दोबारा लिखता है, और room का header खोलने पर पूरा history आ जाता है। साथ ही "आख़िरी 20 messages दिखाओ, scroll पर पुराने लोड करो" `skip(N)` से जितना नीचे जाओ उतना धीमा होता जाता है। और 500 लोगों के group में हर message पर write storm किए बिना "किसने क्या पढ़ा" भी चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → **`rooms`** (small, mutable): `{ _id, type, members: [userIds], lastMsg: { text, ts } }`. Denormalize the *last message* here so the inbox list needs one query, not N.
Step 2 → **`messages`** (huge, append-only): one document per message `{ roomId, from, text, ts, readBy: [] }` — **reference** to the room via `roomId`.
Step 3 → **Index** `{ roomId: 1, ts: -1 }`: matches the query "messages of this room, newest first" so no in-memory sort.
Step 4 → **Load a page**: `find({ roomId }).sort({ ts: -1 }).limit(20)`.
Step 5 → **Older page (cursor)**: remember the oldest `ts` from the previous page and query `{ roomId, ts: { $lt: lastTs } }` — constant speed regardless of depth (no `skip`). If two messages can share a `ts`, use `(ts, _id)` as the cursor.
Step 6 → **Send**: insert into `messages` and update `rooms.lastMsg` (two writes; use a transaction only if you must keep them strictly consistent).
Step 7 → **Read receipts**: for 1-to-1, `$addToSet` the reader into `readBy`. For big groups, store a per-user **`lastReadTs`** in `rooms.members` instead (unread = messages with `ts > lastReadTs`) to avoid one write per message per reader.
Step 8 → **Retention / scale**: TTL for disappearing messages; shard `messages` on `{ roomId: 1, ts: 1 }` or hashed `roomId`; use change streams to push new messages over WebSockets.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **`rooms`** (छोटा, बदलने वाला): `{ _id, type, members: [userIds], lastMsg: { text, ts } }`। *आख़िरी message* यहाँ denormalize करो ताकि inbox list के लिए N नहीं, एक ही query लगे।
Step 2 → **`messages`** (विशाल, सिर्फ append): हर message का एक document `{ roomId, from, text, ts, readBy: [] }` — `roomId` से room का **reference**।
Step 3 → **Index** `{ roomId: 1, ts: -1 }`: "इस room के messages, नए पहले" वाली query से match करता है, इसलिए memory में sort नहीं होता।
Step 4 → **Page लोड करो**: `find({ roomId }).sort({ ts: -1 }).limit(20)`।
Step 5 → **पुराना page (cursor)**: पिछले page का सबसे पुराना `ts` याद रखो और `{ roomId, ts: { $lt: lastTs } }` query करो — गहराई चाहे जितनी हो, speed constant (`skip` नहीं)। अगर दो messages का `ts` same हो सकता है तो cursor `(ts, _id)` रखो।
Step 6 → **Send**: `messages` में insert करो और `rooms.lastMsg` update करो (दो writes; strict consistency चाहिए तभी transaction)।
Step 7 → **Read receipts**: 1-to-1 में reader को `readBy` में `$addToSet` करो। बड़े groups में `rooms.members` में हर user का **`lastReadTs`** रखो (unread = `ts > lastReadTs` वाले messages) ताकि हर message पर हर reader के लिए write न हो।
Step 8 → **Retention / scale**: disappearing messages के लिए TTL; `messages` को `{ roomId: 1, ts: 1 }` या hashed `roomId` पर shard करो; नए messages WebSocket से भेजने के लिए change streams।

---

## 🟡 Real World Example
**Swiggy's delivery-partner chat** and **Flipkart's seller-buyer chat** keep one `rooms` doc per order (members: customer + partner) and thousands of `messages` per day. The app inbox reads `rooms` sorted by `lastMsg.ts`; opening a conversation loads the last 20 messages; scrolling up fetches older pages with a timestamp cursor. When an order is delivered, messages are given a TTL (`expireAt = deliveredAt + 30 days`) to honour data-retention policy.

## 🟡 Real Example Hindi mein
**Swiggy की delivery-partner chat** और **Flipkart की seller-buyer chat** हर order के लिए एक `rooms` doc (members: customer + partner) और रोज़ हज़ारों `messages` रखती हैं। App का inbox `rooms` को `lastMsg.ts` से sort करके पढ़ता है; conversation खोलने पर आख़िरी 20 messages आते हैं; ऊपर scroll करने पर timestamp cursor से पुराने pages आते हैं। Order deliver होने पर data-retention policy के लिए messages पर TTL (`expireAt = deliveredAt + 30 days`) लगता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
use("chat");

// 1) The index that makes "latest messages of a room" fast (no in-memory sort)
db.messages.createIndex({ roomId: 1, ts: -1 });

// 2) A room (small doc) with the denormalized last message
db.rooms.insertOne({ _id: "r1", members: [1, 2], lastMsg: null });

// 3) Insert 5 messages, 1 second apart, alternating senders
const base = Date.now();
for (let i = 1; i <= 5; i++) {
  db.messages.insertOne({
    roomId: "r1",
    from: i % 2 ? 1 : 2,                 // odd -> user 1, even -> user 2
    text: "msg" + i,
    ts: new Date(base + i * 1000),       // increasing timestamps
    readBy: []                           // read receipts (user ids)
  });
}
db.rooms.updateOne({ _id: "r1" }, { $set: { lastMsg: { text: "msg5", ts: new Date() } } });

// 4) First page: newest 2 messages
const page1 = db.messages.find({ roomId: "r1" }, { _id: 0, text: 1, ts: 1 })
  .sort({ ts: -1 }).limit(2).toArray();
page1.map(x => x.text);                  // Output: [ 'msg5', 'msg4' ]

// 5) Next page: cursor = oldest ts of page1 (no skip!)
db.messages.find({ roomId: "r1", ts: { $lt: page1[1].ts } }, { _id: 0, text: 1 })
  .sort({ ts: -1 }).limit(2).toArray();
// Output: [ { text: 'msg3' }, { text: 'msg2' } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — read receipts, unread counts and index proof, tested on MongoDB 8.0.4
use("chat");

// A) User 2 opens the room: mark everything sent by OTHERS as read by 2 (idempotent $addToSet)
db.messages.updateMany(
  { roomId: "r1", from: { $ne: 2 }, readBy: { $ne: 2 } }, // only messages user 2 hasn't read yet
  { $addToSet: { readBy: 2 } }
).modifiedCount;                          // Output: 3 (msg1, msg3, msg5)

// B) Unread count for user 1 (messages from others that 1 has not read)
db.messages.aggregate([
  { $match: { roomId: "r1", from: { $ne: 1 }, readBy: { $ne: 1 } } },
  { $count: "unread" }
]);                                       // Output: [ { unread: 2 } ] (msg2, msg4)

// C) Large groups: per-member watermark instead of per-message flags
// rooms.members = [ { userId: 1, lastReadTs: ISODate(...) }, ... ]
// unread = db.messages.countDocuments({ roomId, ts: { $gt: lastReadTs } })

// D) Proof the compound index serves the page query: only 2 docs examined for limit(2)
db.messages.find({ roomId: "r1" }).sort({ ts: -1 }).limit(2)
  .explain("executionStats").executionStats.totalDocsExamined;  // Output: 2

// E) Inbox: rooms for a user, newest activity first (index on members + lastMsg.ts)
db.rooms.createIndex({ members: 1, "lastMsg.ts": -1 });         // multikey index on members array
db.rooms.find({ members: 1 }).sort({ "lastMsg.ts": -1 }).limit(20);
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const messageSchema = new mongoose.Schema({
  roomId: { type: String, required: true },
  from:   { type: Number, required: true },
  text:   { type: String, required: true, maxlength: 4000 },
  ts:     { type: Date, default: Date.now },
  readBy: { type: [Number], default: [] },
});
messageSchema.index({ roomId: 1, ts: -1 }); // the critical compound index (declare BEFORE mongoose.model)
const Message = mongoose.model('Message', messageSchema);

// GET /rooms/:id/messages?before=2026-01-01T10:00:00.000Z&limit=20 — cursor pagination
app.get('/rooms/:id/messages', async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100); // cap page size
  const q = { roomId: req.params.id };
  if (req.query.before) q.ts = { $lt: new Date(req.query.before) }; // cursor, not skip
  const items = await Message.find(q).sort({ ts: -1 }).limit(limit).lean();
  res.json({ items, nextCursor: items.length ? items[items.length - 1].ts : null });
});

// POST /rooms/:id/messages — send
app.post('/rooms/:id/messages', async (req, res) => {
  const msg = await Message.create({ roomId: req.params.id, from: req.user.id, text: req.body.text });
  // also update the denormalized preview used by the inbox
  await mongoose.connection.collection('rooms').updateOne(
    { _id: req.params.id }, { $set: { lastMsg: { text: msg.text, ts: msg.ts } } });
  res.status(201).json(msg);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Embedding messages in the room document
```javascript
// Wrong — unbounded array: 16 MB limit, rewrites on each message
db.rooms.updateOne({ _id: "r1" }, { $push: { messages: { text: "hi" } } });

// Right — one document per message, referenced by roomId
db.messages.insertOne({ roomId: "r1", from: 1, text: "hi", ts: new Date() });
```

❌ Mistake 2: `skip()` pagination for infinite scroll
✅ Correct: `skip(10000)` still walks 10000 index entries. Use a `ts` (or `(ts,_id)`) cursor with `$lt`. Also add `_id` as tie-breaker, since two messages in the same millisecond would otherwise be skipped or repeated.

❌ Mistake 3: Index on `{ ts: -1, roomId: 1 }` (wrong order)
✅ Correct: Put the equality field first: `{ roomId: 1, ts: -1 }` (ESR rule: Equality, Sort, Range).

---

## 🧠 Tricky Interview Question

```javascript
// 500-member group, 100 messages/min. Each message has readBy: [userIds].
// What goes wrong, and how do you fix it?
```
Answer: Each message could receive up to 500 `readBy` updates — 50,000 writes/min plus a `readBy` array of 500 ids growing every message, wasting space and I/O. Fix: store a **watermark per member** (`lastReadTs` or `lastReadMsgId`) in the room/membership doc — one tiny write when a user opens the chat. "Seen by" for a message = members whose watermark >= message `ts`. Keep per-message `readBy` only for small 1-to-1 chats where exact receipts matter.

---

## ⚫ Interview Questions + Answers

Q1: Why separate `rooms` and `messages` collections?
A1: Messages are unbounded and append-only; rooms are small and mutable. Embedding messages would violate the 16 MB cap and force whole-document rewrites. The rule: embed when the child set is small and bounded and read together; reference when it is large/unbounded.

Q2: How do you paginate older messages efficiently?
A2: Keyset (cursor) pagination: `{ roomId, ts: { $lt: cursor } }` sorted by `ts: -1` with `limit`, supported by `{ roomId: 1, ts: -1 }`. Time is O(page size), unlike `skip`, which is O(skipped).

Q3: How would you deliver messages in real time?
A3: Write to MongoDB, then push through WebSockets. Use a message broker or a **change stream** (needs a replica set) on `messages` to fan out inserts to connected clients. MongoDB is the source of truth, not the transport.

Q4: How do you keep `lastMsg` consistent with `messages`?
A4: Usually accept eventual consistency (two writes, the preview can be recomputed). If it must be atomic, use a multi-document transaction (needs a replica set) — but it costs throughput.

Q5: How do you shard a chat database?
A5: Shard `messages` on hashed `roomId` (even distribution, all of a room's messages on one shard so a page query is targeted) or `{ roomId: 1, ts: 1 }` for ranges. Avoid shard key `ts` alone — monotonic keys create a hot shard.

---

## 🔷 When to Use + When Not to Use
✅ Use this design when:
- Conversations are long-lived and per-room history is read newest-first
- You need flexible message types (text, image, location, reactions) as different fields

❌ Avoid when:
- You need end-to-end message-ordering guarantees at massive scale (Cassandra/Kafka-backed stores are often chosen) or very high fan-out presence/typing events (use Redis)
- Messages are always tiny, bounded and fully read together (then embedding in a single doc is fine)

---

## 📊 Visual Diagram
```
CHAT SCHEMA
──────────────────────────────────────────────────────
 rooms (small)                     messages (huge, append-only)
 ┌──────────────────────┐          ┌──────────────────────────────┐
 │ _id: "r1"            │ 1 ─── ∞  │ roomId: "r1"   ◄─ reference  │
 │ members: [1,2]       │          │ from, text, ts, readBy[]     │
 │ lastMsg:{text,ts}    │          └──────────────────────────────┘
 └──────────────────────┘             index { roomId:1, ts:-1 }

 Infinite scroll (cursor, no skip):
   page1: roomId=r1, sort ts desc, limit 20      → ts: 10:05 … 10:01
   page2: roomId=r1, ts < 10:01, limit 20        → ts: 10:00 … 09:56
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embed | Store child inside parent doc | Child को parent doc के अंदर रखना |
| Reference | Store id pointing to another doc | दूसरे doc की id रखना |
| Cursor pagination | Next page by last seen key | आख़िरी देखी key से अगला page |
| Read receipt | Who has read a message | किसने message पढ़ा |
| Watermark | Per-user last-read position | हर user की आख़िरी-पढ़ी position |
| Denormalize | Copy data for faster reads | तेज़ reads के लिए data की copy |
| Compound index | Index on several fields | कई fields पर index |

---

## ⚡ 3-Line Summary
English:
1. Keep `rooms` small and put each message in its own `messages` document referenced by `roomId`.
2. Index `{ roomId: 1, ts: -1 }` and paginate with a `ts` cursor (`$lt`), never `skip`.
3. Use `$addToSet` read receipts for small chats and per-member watermarks for large groups.

Hindi:
1. `rooms` को छोटा रखो और हर message को `roomId` से जुड़े अपने `messages` document में रखो।
2. `{ roomId: 1, ts: -1 }` index बनाओ और `ts` cursor (`$lt`) से paginate करो, `skip` से कभी नहीं।
3. छोटे chats में `$addToSet` read receipts और बड़े groups में per-member watermark इस्तेमाल करो।

---

## ➡️ Next Topic
**117. Top N per Group Query** — leaderboards per category using `$topN`, `$firstN` and window functions.
