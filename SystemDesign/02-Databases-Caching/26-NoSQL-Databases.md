# 26. NoSQL Databases
# हिंदी में: NoSQL — टेबल और fixed schema के बिना डेटा रखने वाले डेटाबेस (documents, key-value, columns, graph), जो बहुत बड़े स्केल के लिए बने हैं

---

## 🔵 Simple Definition (English)
**NoSQL** ("Not Only SQL") databases store data in models **other than relational tables**, usually with a **flexible schema**, and are designed for **horizontal scaling** and specific access patterns. Four main families:
1. **Document** — JSON-like documents (MongoDB, Firestore, Couchbase)
2. **Key-Value** — key → value (Redis, DynamoDB, Memcached)
3. **Wide-Column** — rows with dynamic columns, partitioned (Cassandra, ScyllaDB, HBase, Bigtable)
4. **Graph** — nodes and edges (Neo4j, Amazon Neptune)

## 🔵 सरल परिभाषा (Hindi)
NoSQL डेटाबेस टेबल की जगह दूसरे तरीकों से डेटा रखते हैं — JSON documents, key-value, columns या graph।
इनका schema लचीला होता है और ये कई मशीनों में आसानी से फैल (scale) जाते हैं।

---

## 🔴 Problem it Solves
Around 2005–2010, Google, Amazon, Facebook and others hit limits of relational DBs:
- **Massive scale:** billions of users, petabytes, millions of writes/sec — a single SQL primary can't take it; manual sharding is painful.
- **Always-on globally:** Amazon's shopping cart had to accept writes **even during network failures** (availability over strict consistency) → Dynamo paper (2007).
- **Changing data shapes:** product catalogs where every category has different attributes; adding columns via migrations on huge tables was slow.
- **Simple access patterns:** "get user session by id", "append event", no joins needed → the relational machinery is overhead.

NoSQL traded some SQL features (joins, multi-row ACID, ad-hoc queries) for **scale, availability, flexibility and speed** on known access patterns.

## 🔴 यह क्यों बना? (Hindi)
Google, Amazon, Facebook के पास अरबों यूज़र और करोड़ों writes प्रति सेकंड थे — एक SQL सर्वर नहीं संभाल पाता था। Amazon का cart नेटवर्क ख़राब होने पर भी चलना चाहिए था।
NoSQL ने joins और कुछ ACID छोड़कर — बहुत बड़ा स्केल, हमेशा उपलब्धता, लचीला schema और तेज़ simple queries दीं।

---

## 🟢 How it Works — Step by Step

### 1. Document DB (MongoDB)

```json
// collection: restaurants  — one document holds related data together
{
  "_id": "r_42",
  "name": "Behrouz Biryani",
  "location": { "type": "Point", "coordinates": [72.83, 19.07] },
  "cuisines": ["Mughlai", "Biryani"],
  "menu": [
    { "id": "m1", "name": "Chicken Biryani", "price": 349, "veg": false },
    { "id": "m2", "name": "Paneer Biryani", "price": 299, "veg": true, "spice": "medium" }
  ],
  "rating": { "avg": 4.3, "count": 12890 }
}
```
```
✅ Data that's read together is stored together → one read, no joins
✅ Flexible fields per document (spice on one item, not others)
✅ Rich queries + secondary indexes + aggregation pipeline, geo queries
⚠️ Multi-document transactions exist (since 4.0) but are costlier; design to avoid them
Use: catalogs, CMS, user profiles, event logs, mobile app backends
```

### 2. Key-Value (Redis, DynamoDB)

```
key                         value
"session:abc123"     →      {"userId": 42, "role": "user"}
"cart:42"            →      {"m1": 2, "m2": 1}
"otp:+919876543210"  →      "482913"   (TTL 300s)

✅ O(1) get/put, extremely fast, easy to partition by key
❌ Query only by key (DynamoDB adds sort keys + secondary indexes)
Use: sessions, caching, carts, feature flags, rate limits, leaderboards (Redis sorted sets)
```

**DynamoDB model:** `Partition key` (decides which partition/server) + optional `Sort key` (orders items inside the partition).
```
PK = USER#42     SK = ORDER#2024-10-01#101   → all orders of user 42, sorted by date
PK = USER#42     SK = PROFILE                → profile in the same partition ("single-table design")
```

### 3. Wide-Column (Cassandra / ScyllaDB)

```
Table: messages_by_channel
PRIMARY KEY ((channel_id, bucket), message_id)   ← partition key, clustering key

partition (channel 7, bucket 2024-10) on node C:
  message_id 9001 | author 42 | text "hi"
  message_id 9002 | author 13 | text "hello"
  ...  (sorted by message_id → fast range reads "latest 50 messages")

✅ Massive write throughput (LSM-tree: append to memory + sequential disk writes)
✅ Linear horizontal scaling, multi-datacenter replication, no single master
✅ Tunable consistency per query (ONE, QUORUM, ALL)
❌ Must design table PER QUERY; no joins, limited ad-hoc queries
Use: chat messages, IoT/time-series, activity feeds, logs — huge append-heavy data
```

### 4. Graph DB (Neo4j)

```
(Aditya)-[:FRIEND]->(Riya)-[:FRIEND]->(Karan)
(Aditya)-[:LIKES]->(Biryani)<-[:SERVES]-(Behrouz)

MATCH (me:User {id: 1})-[:FRIEND*2]->(fof) RETURN fof   // friends of friends
✅ Fast multi-hop relationship traversal (SQL would need many self-joins)
Use: social graphs, recommendations, fraud rings, knowledge graphs
```

### How NoSQL scales: partitioning + replication

```
           hash(partition key)
   key ───────────────────────► token ring / partitions
                ┌────────┬────────┬────────┐
                │ Node A │ Node B │ Node C │   each partition replicated to 3 nodes (RF=3)
                └────────┴────────┴────────┘
Add Node D → some partitions move to it → capacity grows linearly
Choose partition key well: high cardinality + even access (avoid "hot partition")
```

### SQL vs NoSQL vocabulary
```
SQL          MongoDB        DynamoDB         Cassandra
table        collection     table            table
row          document       item             row
column       field          attribute        column
JOIN         $lookup/embed  (avoid)          (avoid — denormalize)
index        index          GSI / LSI        secondary index (limited)
```

### BASE vs ACID
```
ACID (SQL): Atomic, Consistent, Isolated, Durable
BASE (many NoSQL): Basically Available, Soft state, Eventually consistent
(Modern NoSQL often offers stronger options: MongoDB transactions, DynamoDB transactions,
 Cassandra lightweight transactions, Spanner/CockroachDB = distributed SQL.)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Document DB (MongoDB): JSON जैसे document — जो डेटा साथ में पढ़ा जाता है, वो साथ में रखा जाता है।
2. Key-Value (Redis, DynamoDB): key से सीधे value — बहुत तेज़, session/cache/cart के लिए।
3. Wide-Column (Cassandra): बहुत ज़्यादा writes के लिए — चैट मैसेज, IoT डेटा; हर query के लिए अलग टेबल डिज़ाइन।
4. Graph (Neo4j): दोस्त के दोस्त, recommendations जैसे रिश्तों वाले सवाल।
5. Partition key से डेटा कई मशीनों में बँटता है और हर हिस्से की copies (replication) बनती हैं — key सोच-समझकर चुनो।

---

## 🟡 Real World Example

**Discord** — stores trillions of messages. It moved from MongoDB → Cassandra (2017) → ScyllaDB (2022) for predictable latency at huge scale. Messages are partitioned by `(channel_id, time bucket)`.

**Amazon / DynamoDB** — Amazon's Prime Day traffic peaks at tens of millions of DynamoDB requests per second. The shopping cart and order pipelines use key-value access patterns.

**Swiggy / Zomato** — use a mix: MySQL/Postgres for orders and payments, **Cassandra/DynamoDB** for high-volume data like delivery partner location history and event logs, **Redis** for caching and sessions, **Elasticsearch** for restaurant search.

**LinkedIn** — uses graph storage for "People you may know" and 2nd/3rd-degree connections.

**Polyglot persistence** — most large companies use several databases, each for what it's good at.

## 🟡 Real Example Hindi में
Discord अरबों-खरबों मैसेज Cassandra/ScyllaDB में रखता है, `(channel, समय)` के हिसाब से बाँटकर। Amazon Prime Day पर DynamoDB प्रति सेकंड करोड़ों requests संभालता है।
Swiggy ऑर्डर और पेमेंट के लिए SQL, डिलीवरी लोकेशन के लिए Cassandra/DynamoDB, cache के लिए Redis और search के लिए Elasticsearch — सब एक साथ इस्तेमाल करता है।

---

## 🟠 My Stack Example

### MongoDB with Mongoose (Node.js)
```js
const RestaurantSchema = new Schema({
  name: { type: String, required: true },
  location: { type: { type: String, enum: ['Point'] }, coordinates: [Number] },
  cuisines: [String],
  menu: [{ name: String, price: Number, veg: Boolean }],
  rating: { avg: Number, count: Number },
}, { timestamps: true });
RestaurantSchema.index({ location: '2dsphere' });           // geo index
RestaurantSchema.index({ cuisines: 1, 'rating.avg': -1 });  // compound index

// Restaurants within 3 km serving Biryani, best rated first
const list = await Restaurant.find({
  cuisines: 'Biryani',
  location: { $near: { $geometry: { type: 'Point', coordinates: [lng, lat] }, $maxDistance: 3000 } },
}).sort({ 'rating.avg': -1 }).limit(20).lean();

// Aggregation pipeline: average price per cuisine
await Restaurant.aggregate([
  { $unwind: '$menu' }, { $unwind: '$cuisines' },
  { $group: { _id: '$cuisines', avgPrice: { $avg: '$menu.price' } } },
  { $sort: { avgPrice: -1 } },
]);
```

### Embed vs reference (most important MongoDB design decision)
```
Embed when: data is read together, bounded size, owned by parent  → restaurant.menu
Reference when: unbounded growth or shared/independently updated  → reviews (millions) in own collection
Rule: document max 16 MB; never let an array grow without limit.
```

### FastAPI + Motor (async MongoDB)
```python
from motor.motor_asyncio import AsyncIOMotorClient
db = AsyncIOMotorClient(MONGO_URL).foodapp

@app.get("/restaurants/{rid}")
async def get_restaurant(rid: str):
    doc = await db.restaurants.find_one({"_id": rid}, {"menu": 1, "name": 1})
    if not doc: raise HTTPException(404)
    return doc
```

### DynamoDB single-table design (Node, AWS SDK v3)
```js
// Get latest 20 orders for user 42
await ddb.send(new QueryCommand({
  TableName: 'app',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: { ':pk': 'USER#42', ':sk': 'ORDER#' },
  ScanIndexForward: false, Limit: 20,
}));
```

### Redis as a primary store for ephemeral data
```js
await redis.set(`otp:${phone}`, code, { EX: 300 });            // OTP with TTL
await redis.zIncrBy('leaderboard:weekly', 10, `user:${uid}`);   // gaming leaderboard
await redis.zRangeWithScores('leaderboard:weekly', 0, 9, { REV: true });
```

### Typical polyglot setup for your apps
```
PostgreSQL → users, orders, payments (truth, ACID)
MongoDB    → flexible content: CMS, product attributes, app config, logs
Redis      → cache, sessions, OTP, rate limits, queues (BullMQ)
S3         → files
Elasticsearch / OpenSearch → full-text search
```

---

## ⚫ Interview Questions + Answers

**Q1: What are the main types of NoSQL databases? Give a use case for each.**
A1: Document (MongoDB): flexible JSON documents, for catalogs, CMS and user profiles. Key-value (Redis, DynamoDB): fast lookups by key, for sessions, carts, caching and rate limits. Wide-column (Cassandra, ScyllaDB): massive write throughput and partitioned time-ordered data, for chat messages, IoT and activity logs. Graph (Neo4j): relationship traversal, for social networks, recommendations and fraud detection.

**Q2: How do NoSQL databases scale horizontally?**
A2: By partitioning (sharding) data on a partition key, using hashing or ranges, across many nodes, often with consistent hashing so nodes can be added with minimal data movement. Each partition is replicated (e.g. a replication factor of 3) for availability. Queries that include the partition key go to a single partition, so performance stays constant as data grows. Poor key choice creates hot partitions.

**Q3: In MongoDB, when do you embed vs reference?**
A3: Embed when the child data is accessed together with the parent, is bounded in size, and belongs only to that parent (order line items, address, menu of a restaurant), which gives one read and atomic updates. Reference when the child set is unbounded (comments, reviews, events), shared by many parents, or updated independently and frequently, which avoids the 16 MB limit and huge rewrites. Hybrids exist, like embedding the latest 5 reviews plus a reference collection.

**Q4: What is a "hot partition" and how do you avoid it?**
A4: When a disproportionate share of traffic or data hits one partition key, e.g. partitioning by `date` (today's partition gets all writes) or a celebrity user. That node becomes the bottleneck while others idle. Avoid it with high-cardinality keys (userId, orderId), composite keys with bucketing (`channel_id + month`), write sharding (append a random suffix 0–9 and read from all 10), and caching hot reads.

**Q5: Does NoSQL mean no transactions and no consistency?**
A5: Not anymore. Many NoSQL systems offer configurable or strong consistency: MongoDB has multi-document ACID transactions and majority read/write concerns, DynamoDB has strongly consistent reads and transactions, and Cassandra has tunable consistency (QUORUM) and lightweight transactions. They're often more expensive or limited in scope than in SQL databases, so data models are designed so that most operations touch a single document or partition.

---

## 🔷 Trade-offs
✅ Advantages:
- Horizontal scaling and high availability built in.
- Flexible schema; fast iteration.
- Very fast for designed access patterns; great write throughput (wide-column).

❌ Disadvantages:
- Must know access patterns up front; ad-hoc queries/joins are hard.
- Denormalization → data duplication and update complexity.
- Weaker or costlier transactions/consistency; eventual consistency bugs.
- Less standardization; each DB has its own query language and modeling rules.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| NoSQL | Non-relational databases | बिना टेबल-रिश्तों वाले DB |
| Document | JSON-like record | JSON जैसा रिकॉर्ड |
| Collection | Group of documents | documents का समूह |
| Key-Value | Lookup by key only | key से सीधा value |
| Wide-column | Partitioned rows, dynamic columns | बँटी हुई rows वाला DB |
| Partition key | Decides where data lives | डेटा किस मशीन पर जाएगा |
| Replication factor | Number of copies | कितनी copies |
| Hot partition | Overloaded single partition | ज़्यादा भार वाला हिस्सा |
| Polyglot persistence | Using many DB types together | कई तरह के DB साथ में |
| BASE | Basically Available, Soft state, Eventually consistent | धीरे-धीरे consistent |

---

## ⚡ 3-Line Summary
**English:**
1. NoSQL = document, key-value, wide-column and graph DBs with flexible schemas, built to scale out.
2. They partition by key and replicate; design around access patterns and avoid hot partitions.
3. Trade joins/strict ACID for scale and speed — most companies combine SQL + NoSQL (polyglot persistence).

**Hindi:**
1. NoSQL = document, key-value, wide-column, graph — लचीला schema, आसानी से scale।
2. Partition key से डेटा बँटता है; query के हिसाब से डिज़ाइन करो, hot partition से बचो।
3. Joins/ACID कम, स्केल और स्पीड ज़्यादा — ज़्यादातर कंपनियाँ SQL + NoSQL दोनों इस्तेमाल करती हैं।

---

## ➡️ Next Topic Suggestion
**27. SQL vs NoSQL — When to Use** — Now that you know both worlds, next is the exact decision framework interviewers expect: given a system, which database do you pick and why?
