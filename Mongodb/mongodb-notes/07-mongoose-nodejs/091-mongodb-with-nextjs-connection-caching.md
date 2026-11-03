# 91. MongoDB with Next.js (connection caching)
# हिंदी में: Next.js के साथ MongoDB (connection caching)

---

## 🔵 Simple Definition (English)
**Connection caching** means storing the MongoDB client/connection promise in a place that survives re-execution of your module (the Node `global` object in development, module scope in production), so every API route, Server Component, and Server Action reuses ONE connection pool instead of opening a new one on each call or each hot reload.

## 🔵 सरल परिभाषा (Hindi)
**Connection caching** का मतलब है MongoDB client/connection promise को ऐसी जगह रखना जो आपके module के दोबारा execute होने पर भी बची रहे (development में Node का `global` object, production में module scope), ताकि हर API route, Server Component और Server Action **एक ही** connection pool reuse करे — हर call या हर hot reload पर नया न खोले।

---

## 🔴 Problem it Solves
Next.js is not a long-running Express server. In **development**, Hot Module Replacement re-evaluates your `lib/mongodb.js` on every file save, so each save creates a brand-new `MongoClient` while the old pool stays open. In **serverless production** (Vercel, AWS Lambda), every cold start is a new process; hundreds of concurrent invocations can each open a pool. The result: `MongoServerError: too many connections` on Atlas (M0 allows 500 connections), slow cold starts, and exhausted database resources. Caching the connection promise fixes the dev leak and reuses connections across warm invocations in prod.

## 🔴 यह क्यों बना? (Hindi)
Next.js कोई हमेशा चलने वाला Express server नहीं है। **Development** में Hot Module Replacement हर file save पर `lib/mongodb.js` दोबारा चलाता है, तो हर save पर नया `MongoClient` बनता है जबकि पुराना pool खुला रहता है। **Serverless production** (Vercel, AWS Lambda) में हर cold start नया process है; सैकड़ों concurrent invocations हर एक अपना pool खोल सकते हैं। नतीजा: Atlas पर `too many connections` error (M0 में 500 connections की limit), धीमे cold starts और database resources खत्म। Connection promise cache करने से dev का leak रुकता है और prod में warm invocations connection reuse करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → A helper file (`lib/mongodb.js` or `lib/dbConnect.js`) exports a function that returns a connected client/Mongoose instance.
Step 2 → First call: no cache exists → start `connect()` and store the **promise** (not just the result) in the cache.
Step 3 → Concurrent calls arriving while connecting `await` the SAME stored promise — no duplicate connects (race-safe).
Step 4 → In **development** the cache lives on `global` (`global._mongoClientPromise`) because HMR re-runs module code but `global` survives.
Step 5 → In **production** a plain module-level variable is enough; a warm serverless instance reuses it across invocations.
Step 6 → Keep `maxPoolSize` small for serverless (e.g. 1–10) because many instances run in parallel; use `bufferCommands: false` with Mongoose so failures surface immediately.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक helper file (`lib/mongodb.js`) एक function export करती है जो connected client/Mongoose instance लौटाता है।
Step 2 → पहली call: cache नहीं है → `connect()` शुरू करो और **promise** (सिर्फ result नहीं) cache में रखो।
Step 3 → Connect होने के दौरान आई concurrent calls उसी stored promise को `await` करती हैं — duplicate connect नहीं होता।
Step 4 → **Development** में cache `global` पर रहता है (`global._mongoClientPromise`) क्योंकि HMR module code दोबारा चलाता है पर `global` बचा रहता है।
Step 5 → **Production** में साधारण module-level variable काफी है; warm serverless instance उसे invocations के बीच reuse करता है।
Step 6 → Serverless के लिए `maxPoolSize` छोटा रखो (1–10) क्योंकि कई instances parallel चलते हैं; Mongoose में `bufferCommands: false` रखो ताकि failure तुरंत दिखे।

---

## 🟡 Real World Example
**Flipkart-style product pages built on Next.js and deployed on Vercel**: during the Big Billion Days sale, hundreds of lambda instances serve `/product/[id]`. Each instance imports the cached `clientPromise`; a warm instance handles thousands of requests over one pool of 5 connections. Without caching, each request opened its own connection and the Atlas cluster hit its connection limit, returning 500s at the worst possible moment. Developers also stopped seeing "Atlas connections" alerts triggered by their own `next dev` hot reloads.

## 🟡 Real Example Hindi mein
**Vercel पर deploy Next.js से बना Flipkart-जैसा product page**: Big Billion Days sale में सैकड़ों lambda instances `/product/[id]` serve करते हैं। हर instance cached `clientPromise` import करता है; एक warm instance 5 connections के एक pool पर हज़ारों requests संभालता है। Caching न हो तो हर request अपना connection खोलती, Atlas cluster अपनी connection limit पर पहुँचता और सबसे ज़रूरी समय पर 500 errors आते। Developers के अपने `next dev` hot reload से आने वाले "Atlas connections" alerts भी बंद हो गए।

---

## 💻 Code Example — Basic

Native driver version (`lib/mongodb.js`), the pattern recommended in the Next.js examples:

```javascript
// lib/mongodb.js — npm i mongodb
import { MongoClient } from 'mongodb';

const uri = process.env.MONGODB_URI;               // set in .env.local, never commit it
if (!uri) throw new Error('Please define MONGODB_URI');

const options = { maxPoolSize: 10 };               // small pool: many instances run in parallel

let clientPromise;                                  // exported promise of a connected client

if (process.env.NODE_ENV === 'development') {
  // DEV: HMR re-runs this file on every save. A normal variable would reset,
  // so keep the promise on `global`, which survives hot reloads.
  if (!global._mongoClientPromise) {
    global._mongoClientPromise = new MongoClient(uri, options).connect(); // create ONCE
  }
  clientPromise = global._mongoClientPromise;
} else {
  // PROD: module scope is cached by Node per process; each warm instance reuses it.
  clientPromise = new MongoClient(uri, options).connect();
}

export default clientPromise;                       // import this everywhere
```

Using it in a Route Handler (App Router):

```javascript
// app/api/products/route.js
import clientPromise from '@/lib/mongodb';
import { NextResponse } from 'next/server';

export async function GET() {
  const client = await clientPromise;               // already connected after first call
  const products = await client.db('shop').collection('products')
    .find({}).limit(20).project({ name: 1, price: 1 }).toArray();
  return NextResponse.json(products);
}
```

## 💻 Code Example — Advanced

Mongoose version with the promise cache (`lib/dbConnect.js`). We ran this exact caching logic in Node with three concurrent calls plus one more after, simulating parallel requests:

```javascript
// lib/dbConnect.js — npm i mongoose
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI;

// Reuse the cache across hot reloads: store on global
let cached = global._mongoose;
if (!cached) cached = global._mongoose = { conn: null, promise: null };

export default async function dbConnect() {
  if (cached.conn) return cached.conn;               // fast path: already connected

  if (!cached.promise) {                              // first caller creates the promise
    cached.promise = mongoose.connect(MONGODB_URI, {
      bufferCommands: false,                          // fail fast instead of queueing forever
      maxPoolSize: 10,
    }).then((m) => m);
  }

  try {
    cached.conn = await cached.promise;               // everyone awaits the SAME promise
  } catch (e) {
    cached.promise = null;                            // IMPORTANT: allow retry after failure
    throw e;
  }
  return cached.conn;
}
```

Real test output (3 parallel calls + 1 sequential call):
```text
creating NEW connection        <- printed only once
readyState 1 connections objects: 1
```
`readyState 1` means connected; only ONE connection object existed even though `dbConnect()` ran four times.

Defining models safely under HMR (otherwise `OverwriteModelError`):
```javascript
// models/Product.js
import mongoose from 'mongoose';
const schema = new mongoose.Schema({ name: String, price: Number });
// Reuse existing model if HMR already compiled it, else compile it
export default mongoose.models.Product || mongoose.model('Product', schema);
```

---

## 🟠 Express.js / Mongoose Integration

A Server Component and a Server Action sharing the cache (App Router):

```javascript
// app/products/page.js — Server Component, runs on the server only
import dbConnect from '@/lib/dbConnect';
import Product from '@/models/Product';

export default async function Page() {
  await dbConnect();                                   // cheap after the first call
  const items = await Product.find().limit(10).lean(); // lean() gives plain objects
  // Convert ObjectId to string before passing to Client Components
  const safe = items.map((p) => ({ ...p, _id: p._id.toString() }));
  return <ul>{safe.map((p) => <li key={p._id}>{p.name}</li>)}</ul>;
}

// app/actions.js — Server Action
'use server';
export async function addProduct(formData) {
  await dbConnect();
  await Product.create({ name: formData.get('name'), price: Number(formData.get('price')) });
}
```
(The Next.js files themselves could not be run here; the caching logic was verified in plain Node as shown above.)

Express comparison: in Express you connect once in `app.listen`; in Next.js there is no single startup hook, so every entry point calls the cached helper.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating a client inside the handler
```javascript
// Wrong — new pool per request; breaks under load
export async function GET() {
  const client = new MongoClient(uri);
  await client.connect();
  return Response.json(await client.db('shop').collection('p').find().toArray());
}

// Right — import the cached promise
import clientPromise from '@/lib/mongodb';
export async function GET() { const client = await clientPromise; /* ... */ }
```

❌ Mistake 2: Calling `client.close()` after every request
✅ Correct: Closing destroys the cached pool; the next request must reconnect and the cached promise now points to a closed client. Never close in request handlers.

❌ Mistake 3: Caching the connection result, not the promise
✅ Correct: Two concurrent first requests both see `conn === null` and both connect. Cache the **promise** so the second request awaits the first.

❌ Mistake 4: Large `maxPoolSize` on serverless
✅ Correct: 100 lambdas × pool of 100 = 10,000 connections. Use 1–10 and consider Atlas connection-string limits or a connection proxy.

❌ Mistake 5: Not resetting the cached promise after failure
✅ Correct: A rejected promise stays cached forever and every request fails. Set `cached.promise = null` in the `catch`.

---

## 🧠 Tricky Interview Question

Q: "We cache the client in a module-level `let client` and it works in production, but in `next dev` Atlas shows connection counts growing every time I save a file. Why?"

Answer: HMR re-evaluates the module on each save, creating a fresh module scope, so `let client` is `undefined` again and a new `MongoClient` connects while the old one (still referenced by older module instances) keeps its sockets open. `global` is not reset by HMR, so the cache must live on `global` in development. In production there is no HMR, so module scope is fine. Also note that serverless freezes/destroys instances, so "one connection per process" still means one pool per concurrent instance, not one per app.

---

## ⚫ Interview Questions + Answers

Q1: Why can't you just use the Express pattern (connect once in `listen`) in Next.js?
A1: Next.js has no single long-lived server entry point; routes are separate modules/functions, often executed in different serverless instances. You need a lazy, idempotent "connect if not connected" helper.

Q2: Why cache a promise rather than the connected client?
A2: To make concurrent first calls race-safe. All callers await the same in-flight promise, so only one connection attempt is made.

Q3: What error do you get with `mongoose.model('Product', schema)` twice under HMR?
A3: `OverwriteModelError: Cannot overwrite 'Product' model once compiled`. Use `mongoose.models.Product || mongoose.model(...)`.

Q4: How do you handle connection limits on Atlas with serverless?
A4: Keep `maxPoolSize` small, use `minPoolSize: 0`, cache the connection, size the cluster tier for peak concurrent instances, and consider a connection pooler/proxy or Atlas Data API-style layer if concurrency is extreme.

Q5: Can `ObjectId` values be passed from a Server Component to a Client Component?
A5: No — they are not plain serializable objects. Convert with `_id.toString()` (or `JSON.parse(JSON.stringify(doc))`) before passing props.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running Next.js (App/Pages Router) or any serverless/function platform with MongoDB
- You see `too many connections`, slow cold starts, or growing connection counts in `next dev`

❌ Avoid / be careful when:
- Using the Edge runtime — the Node driver needs TCP sockets and is not supported there; use the Node runtime (`export const runtime = 'nodejs'`) or an HTTP-based data layer
- Very high concurrency with a tiny cluster — caching alone will not fix an undersized database

---

## 📊 Visual Diagram
```
  WITHOUT CACHE                        WITH CACHED PROMISE
  ───────────────                      ─────────────────────
  req1 ─► new pool ─┐                  req1 ─┐
  req2 ─► new pool ─┤                  req2 ─┼─► global._mongoClientPromise
  req3 ─► new pool ─┼─► MongoDB        req3 ─┘            │
  save ─► new pool ─┘  (connections                       ▼
                        explode)                  ONE pool (maxPoolSize 10)
                                                          │
                                                          ▼
                                                      MongoDB

  Dev HMR:  module re-runs, `global` survives ► same promise reused
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HMR | Hot Module Replacement, re-runs changed modules | Changed modules को live दोबारा चलाना |
| Cold start | New serverless instance boots | नया serverless instance शुरू होना |
| Connection pool | Reusable set of open connections | Reuse होने वाले खुले connections का set |
| `global` | Node object that outlives module reloads | Module reload के बाद भी बचा रहने वाला object |
| `maxPoolSize` | Max connections per client | प्रति client अधिकतम connections |
| `bufferCommands` | Mongoose queues commands before connect | Connect से पहले commands queue करना |
| Serverless | Short-lived on-demand functions | Short-lived on-demand functions |

---

## ⚡ 3-Line Summary
English:
1. Next.js re-runs modules (HMR) and spawns many serverless instances, so a naive `new MongoClient` per call leaks connections.
2. Cache the connection **promise** — on `global` in development, module scope in production — and reset it on failure.
3. Keep `maxPoolSize` small, never `close()` in handlers, and guard Mongoose models with `mongoose.models.X || mongoose.model(...)`.

Hindi:
1. Next.js modules दोबारा चलाता है (HMR) और कई serverless instances बनाता है, इसलिए हर call पर `new MongoClient` connections leak करता है।
2. Connection **promise** cache करो — development में `global` पर, production में module scope में — और failure पर reset करो।
3. `maxPoolSize` छोटा रखो, handlers में कभी `close()` मत करो, और Mongoose models को `mongoose.models.X || mongoose.model(...)` से guard करो।

---

## ➡️ Next Topic
**92. Pagination in MongoDB — skip/limit vs Cursor-based** — How to return big lists page by page without slowing down at page 5000.
