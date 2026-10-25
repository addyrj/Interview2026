# 181. GraphQL with Node.js
# हिंदी में: GraphQL with Node.js — Flexible Query Language के साथ API बनाना

---

## 🔵 Simple Definition (English)
**GraphQL** is a query language and runtime for APIs where the CLIENT specifies exactly what data it needs in a single request, and the server returns EXACTLY that shape — no more, no less. Unlike REST (fixed endpoints returning fixed shapes), one GraphQL endpoint (`/graphql`) handles all queries, letting clients fetch nested, related data in one round trip.

## 🔵 सरल परिभाषा (Hindi)
**GraphQL** एक query language और runtime है APIs के लिए जहाँ CLIENT exactly बताता है कि उसे कौन सा data चाहिए एक single request में, और server EXACTLY वही shape return करता है — ना ज्यादा, ना कम। REST (fixed endpoints, fixed shapes) के विपरीत, एक GraphQL endpoint (`/graphql`) सारी queries handle करता है, clients को nested, related data एक round trip में fetch करने देता है।

---

## 🔴 Problem it Solves
REST has two common pain points at scale:
1. **Over-fetching**: `GET /users/5` returns the FULL user object (50 fields) even if the mobile app only needs `name` and `avatar` — wasting bandwidth.
2. **Under-fetching / N+1 requests**: To show a user's profile WITH their last 5 orders, REST often needs 2 calls: `GET /users/5` then `GET /users/5/orders`. For a nested feed showing users + their posts + comments on each post, this can balloon into MANY sequential/parallel requests (the classic "N+1 problem").

GraphQL solves both: the client asks for EXACTLY the fields it needs (`{ user { name avatar orders { id total } } }`) in ONE request, and the server resolves all of it in a single round trip.

## 🔴 यह क्यों बना? (Hindi)
REST में scale पर दो common pain points हैं:
1. **Over-fetching**: `GET /users/5` पूरा user object (50 fields) return करता है भले mobile app को सिर्फ `name` और `avatar` चाहिए हो — bandwidth waste।
2. **Under-fetching / N+1 requests**: User का profile उनके last 5 orders के साथ दिखाने के लिए REST को अक्सर 2 calls चाहिए: `GET /users/5` फिर `GET /users/5/orders`। Users + उनके posts + हर post के comments दिखाने वाले nested feed के लिए यह बहुत सारे sequential/parallel requests में बदल सकता है (classic "N+1 problem")।

GraphQL दोनों solve करता है: client exactly वही fields माँगता है जो चाहिए (`{ user { name avatar orders { id total } } }`) ONE request में, और server सब कुछ एक round trip में resolve कर देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define a **schema** describing types (`User`, `Order`), their fields, and relationships, plus `Query`/`Mutation` entry points.
Step 2 → Write **resolver** functions — one per field/type — that know HOW to fetch that specific piece of data (from DB, cache, another API).
Step 3 → Client sends a POST request to the single `/graphql` endpoint with a query string describing exactly what it wants.
Step 4 → The GraphQL server parses the query, validates it against the schema, and calls the appropriate resolvers in the right order (parent fields resolve before nested child fields).
Step 5 → Resolvers' results are assembled into a response JSON that EXACTLY mirrors the shape of the client's query.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक **schema** define करो जो types (`User`, `Order`), उनके fields, relationships, और `Query`/`Mutation` entry points describe करे।
Step 2 → **Resolver** functions लिखो — हर field/type के लिए एक — जो जानते हैं कि वो specific data कैसे fetch करना है (DB, cache, किसी और API से)।
Step 3 → Client single `/graphql` endpoint पर POST request भेजता है एक query string के साथ जो exactly बताती है कि क्या चाहिए।
Step 4 → GraphQL server query को parse करता है, schema के against validate करता है, और सही order में resolvers call करता है (parent fields nested child fields से पहले resolve होते हैं)।
Step 5 → Resolvers के results assemble होकर एक response JSON बनते हैं जो client की query के shape को EXACTLY mirror करता है।

---

## 🟡 Real World Example
**Facebook (creator of GraphQL) and Github's public API** use GraphQL heavily because their data is deeply interconnected (users → posts → comments → likes → reactions). A mobile client building a news feed can request `{ feed { posts { author { name } content likes { count } comments(first: 3) { text author { name } } } } }` in ONE query — fetching users, posts, likes, and the first 3 comments with THEIR authors, all in a single round trip, instead of the dozens of REST calls this would otherwise require.

## 🟡 Real Example Hindi mein
**Facebook (जिसने GraphQL बनाया) और Github का public API** GraphQL heavily use करते हैं क्योंकि उनका data deeply interconnected है (users → posts → comments → likes → reactions)। News feed बनाने वाला mobile client `{ feed { posts { author { name } content likes { count } comments(first: 3) { text author { name } } } } }` जैसी query ONE call में भेज सकता है — users, posts, likes, और पहले 3 comments उनके authors के साथ एक ही round trip में fetch करके, जो otherwise दर्जनों REST calls चाहते।

---

## 💻 Code Example — Basic

```javascript
// basic-graphql.js
// Install: npm install graphql graphql-http express

const express = require('express');
const { createHandler } = require('graphql-http/lib/use/express');
const { buildSchema } = require('graphql');

// 1. Define the schema using GraphQL's Schema Definition Language (SDL)
const schema = buildSchema(`
  type User {
    id: ID!
    name: String!
    email: String!
  }

  type Query {
    user(id: ID!): User
    users: [User!]!
  }
`);

// 2. In-memory data for demo
const users = [
  { id: '1', name: 'Rahul', email: 'rahul@example.com' },
  { id: '2', name: 'Priya', email: 'priya@example.com' },
];

// 3. Resolvers -- one function per Query field, matching the schema
const root = {
  user: ({ id }) => users.find(u => u.id === id), // resolves `user(id: ID!)`
  users: () => users,                              // resolves `users: [User!]!`
};

const app = express();
// Mount the GraphQL handler -- a SINGLE endpoint handles ALL queries
app.all('/graphql', createHandler({ schema, rootValue: root }));

app.listen(4000, () => console.log('GraphQL server on :4000/graphql'));

// Example client query (sent as POST body to /graphql):
// { user(id: "1") { name email } }
// Response: { "data": { "user": { "name": "Rahul", "email": "rahul@example.com" } } }
```

## 💻 Code Example — Advanced

```javascript
// advanced-graphql.js — nested relationships, mutations, DataLoader to avoid N+1 at the resolver level

const express = require('express');
const { createHandler } = require('graphql-http/lib/use/express');
const { buildSchema } = require('graphql');
const DataLoader = require('dataloader'); // npm install dataloader

const schema = buildSchema(`
  type Order {
    id: ID!
    total: Float!
  }

  type User {
    id: ID!
    name: String!
    orders: [Order!]!
  }

  type Query {
    users: [User!]!
  }

  type Mutation {
    createOrder(userId: ID!, total: Float!): Order!
  }
`);

const usersDb = [{ id: '1', name: 'Rahul' }, { id: '2', name: 'Priya' }];
let ordersDb = [{ id: 'o1', userId: '1', total: 500 }, { id: 'o2', userId: '1', total: 1200 }];

// DataLoader batches multiple "load orders for userId X" calls within one tick into ONE query,
// solving the N+1 problem that naive per-user resolvers would otherwise cause
function createOrderLoader() {
  return new DataLoader(async (userIds) => {
    // ONE "query" fetches orders for ALL requested userIds at once
    return userIds.map(id => ordersDb.filter(o => o.userId === id));
  });
}

const root = {
  users: () => usersDb,
  createOrder: ({ userId, total }) => {
    const order = { id: `o${ordersDb.length + 1}`, userId, total };
    ordersDb.push(order); // mutation: writes data, just like a REST POST
    return order;
  },
};

// Resolver for the nested User.orders field -- per-request DataLoader avoids N+1 across the whole query
const userOrdersResolver = {
  User: {
    orders: (user, args, context) => context.orderLoader.load(user.id), // batches internally
  },
};

const app = express();
app.use(express.json());
app.all('/graphql', (req, res, next) => {
  req.context = { orderLoader: createOrderLoader() }; // fresh loader per request -- avoids stale caching across requests
  next();
}, createHandler({
  schema,
  rootValue: { ...root, ...userOrdersResolver.User }, // simplified wiring for buildSchema-style resolvers
  context: (req) => req.raw.context,
}));

app.listen(4000);

// Example mutation:
// mutation { createOrder(userId: "1", total: 999) { id total } }
```

---

## 🟠 Express.js Integration

```javascript
// Mounting GraphQL alongside existing REST routes in the SAME Express app -- common migration pattern
const express = require('express');
const { createHandler } = require('graphql-http/lib/use/express');
const schema = require('./schema');
const rootValue = require('./resolvers');

const app = express();
app.use(express.json());

// Existing REST routes stay untouched
app.use('/api/v1/products', require('./routes/products'));

// New GraphQL endpoint added alongside, for clients that want flexible querying
app.all('/graphql', createHandler({ schema, rootValue }));

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Writing naive resolvers that trigger a DB query PER item in a list (N+1 at the resolver level)
✅ Correct: Use DataLoader (or manual batching) to collapse many individual lookups into one batched query.

```javascript
// Wrong -- fires one query PER user for their orders (N+1!)
orders: (user) => Order.find({ userId: user.id })

// Right -- batches all userIds requested in this tick into ONE query
orders: (user, args, ctx) => ctx.orderLoader.load(user.id)
```

❌ Mistake 2: Allowing arbitrarily deep/complex client queries without limits
✅ Correct: Enforce query depth/complexity limits — a malicious or buggy client could request deeply nested data (`user{orders{items{product{reviews{author{orders{...}}}}}}}`) causing exponential resolver calls (a GraphQL-specific DoS vector).

```javascript
// Wrong -- no limits, vulnerable to deeply nested malicious queries
app.all('/graphql', createHandler({ schema, rootValue }));

// Right -- add query depth/complexity validation (e.g., graphql-depth-limit)
const depthLimit = require('graphql-depth-limit');
// validationRules: [depthLimit(5)] passed to the GraphQL execution setup
```

---

## 🧠 Tricky Interview Question

```javascript
// query { users { name orders { total } } }
// If there are 100 users, how many times does the `orders` resolver function get CALLED
// (not how many DB queries run)?
```
Answer: The resolver function is called **100 times** — once per `User` object in the list, because GraphQL resolves each field of each object in the list independently by default. This is exactly why naive implementations cause the N+1 problem: 100 calls to the `orders` resolver could mean 100 separate DB queries. The FIX (DataLoader) doesn't reduce the number of resolver CALLS (still 100), but it batches them so all 100 calls collapse into ONE actual database query, executed once all 100 `.load()` calls have been queued within the same event loop tick.

---

## ⚫ Interview Questions + Answers

Q1: What's the fundamental architectural difference between REST and GraphQL?
A1: REST exposes MULTIPLE endpoints, each returning a FIXED shape determined by the server. GraphQL exposes a SINGLE endpoint where the CLIENT determines the response shape by specifying exactly which fields it wants, for potentially deeply nested/related data, in one query.

Q2: What are Query, Mutation, and Subscription in GraphQL?
A2: **Query** — read operations (like GET in REST). **Mutation** — write operations that change data (like POST/PUT/PATCH/DELETE in REST) — mutations execute sequentially (not in parallel) per GraphQL spec, unlike queries which can run in parallel. **Subscription** — real-time operations where the server pushes updates to the client over a persistent connection (typically WebSocket), used for live data (chat, notifications).

Q3: What is over-fetching and under-fetching, and how does GraphQL address both?
A3: Over-fetching: a REST endpoint returns more fields than the client needs (wasted bandwidth). Under-fetching: a REST endpoint doesn't return enough related data, forcing additional requests. GraphQL addresses both because the client explicitly specifies the exact fields AND relationships needed in one query — nothing more, nothing less, and nested data comes back in the same request.

Q4: What is the N+1 problem in GraphQL, and how is it typically solved?
A4: When a parent list (e.g., 100 users) each triggers a separate DB call for a nested field (e.g., each user's orders), you get 1 query for users + N queries for orders = N+1 queries, which doesn't scale. It's solved with **DataLoader** (or similar batching utilities), which collects all individual `.load(id)` calls made within the same tick and issues ONE batched query (`WHERE userId IN (...)`) instead of N separate ones.

Q5: Why might you choose GraphQL over REST for a mobile app specifically?
A5: Mobile apps are especially sensitive to over-fetching (limited bandwidth/battery) and under-fetching (multiple round trips add latency, worse on unreliable mobile networks). GraphQL lets a mobile client request EXACTLY the fields it needs for a given screen in ONE request, minimizing both payload size and round trips — directly improving perceived performance and battery/data usage.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Clients have varying data needs (mobile vs web needing different field subsets from the same underlying resources).
- Data is deeply relational/nested and REST would require many chained requests.
- You control both client and server and can invest in schema/resolver design + N+1 mitigation (DataLoader).

❌ Avoid when:
- Simple CRUD APIs with uniform, flat data needs — REST's simplicity (caching, tooling, familiarity) wins.
- File uploads/downloads, streaming, or simple public APIs where REST's HTTP-caching semantics (ETags, CDN caching) are valuable — GraphQL's single endpoint complicates HTTP-level caching.

---

## 📊 Visual Diagram
```
REST (multiple round trips):              GraphQL (one round trip):
───────────────────────────               ──────────────────────────
GET /users/5         → user data          POST /graphql
GET /users/5/orders   → orders              query {
GET /orders/o1/items → items                  user(id: 5) {
                                                  name
  3 separate requests                            orders { total items { name } }
                                                }
                                              }
                                              ONE request, exact shape returned
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Type definitions describing the API | API describe करने वाले type definitions |
| Resolver | Function that fetches a field's data | Field का data fetch करने वाला function |
| Query | Read operation | Read operation |
| Mutation | Write operation | Write operation |
| N+1 problem | Excess per-item queries | Per-item extra queries |
| DataLoader | Batching/caching utility to fix N+1 | N+1 fix करने वाला batching tool |

---

## ⚡ 3-Line Summary
English:
1. GraphQL lets clients specify exactly what data they need in one request, through one endpoint, solving REST's over-fetching and under-fetching problems.
2. A schema defines types/fields, and resolver functions fetch the actual data for each field, often from a database.
3. Watch for the N+1 problem in nested resolvers — use DataLoader to batch per-item lookups into single queries.

Hindi:
1. GraphQL clients को exactly वो data specify करने देता है जो चाहिए, एक request में, एक endpoint से — REST की over-fetching और under-fetching problems solve करता है।
2. Schema types/fields define करता है, और resolver functions हर field का actual data fetch करते हैं, अक्सर database से।
3. Nested resolvers में N+1 problem से सावधान रहो — per-item lookups को single queries में batch करने के लिए DataLoader use करो।

---

## ➡️ Next Topic
**182. Apollo Server** — Production-grade GraphQL server implementation Node.js में।
