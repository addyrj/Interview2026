# 185. GraphQL Subscriptions
# हिंदी में: GraphQL Subscriptions — Real-Time Updates Push करना

---

## 🔵 Simple Definition (English)
**Subscriptions** are GraphQL's real-time operation type — instead of the client asking once and getting one response (like Query/Mutation), the client opens a long-lived connection (typically WebSocket) and the SERVER pushes new data to it whenever a relevant event happens, without the client needing to re-request.

## 🔵 सरल परिभाषा (Hindi)
**Subscriptions** GraphQL का real-time operation type हैं — client एक बार पूछकर एक response लेने (Query/Mutation जैसे) की जगह, एक long-lived connection खोलता है (typically WebSocket) और SERVER जब भी relevant event हो, उसे नया data push करता है, बिना client को फिर से request किये।

---

## 🔴 Problem it Solves
Without subscriptions, getting "live" data via GraphQL requires **polling** — the client repeatedly sends the SAME query every few seconds (`setInterval(() => refetch(), 3000)`). This is wasteful (most polls return unchanged data), adds latency (updates only show up on the next poll interval, not instantly), and doesn't scale well (many clients polling frequently = heavy server load for mostly-empty responses). Subscriptions solve this by flipping the model: the server PUSHES data the INSTANT something relevant changes, over a persistent connection — true real-time updates with minimal wasted requests.

## 🔴 यह क्यों बना? (Hindi)
Subscriptions के बिना, GraphQL से "live" data लेने के लिए **polling** चाहिए — client हर कुछ seconds में SAME query repeatedly भेजता है (`setInterval(() => refetch(), 3000)`)। यह wasteful है (ज़्यादातर polls unchanged data return करते हैं), latency बढ़ाता है (updates सिर्फ next poll interval पर दिखते हैं, instantly नहीं), और scale नहीं करता (बहुत सारे clients frequently poll करें = server पर heavy load mostly-empty responses के लिए)। Subscriptions इस model को flip करके solve करते हैं: server किसी relevant change के INSTANT data PUSH करता है, एक persistent connection पर — true real-time updates minimal wasted requests के साथ।

---

## 🟢 How it Works — Step by Step

Step 1 → Define a `Subscription` type in the schema with fields (e.g., `orderStatusChanged(orderId: ID!): Order!`).
Step 2 → Implement the resolver with a `subscribe` function (not a normal resolver) that returns an **AsyncIterator** — commonly backed by a **PubSub** mechanism (in-memory for single server, Redis-backed for multiple servers).
Step 3 → Client connects via WebSocket (using the `graphql-ws` protocol) and sends a subscription operation, specifying which fields/arguments it cares about.
Step 4 → Whenever the relevant event is published (e.g., when a mutation updates an order's status, it calls `pubsub.publish('ORDER_STATUS_CHANGED', { orderStatusChanged: updatedOrder })`), the subscription resolver's AsyncIterator yields the new value.
Step 5 → GraphQL pushes the new value down the WebSocket to EVERY client currently subscribed, each client's connection stays open until it unsubscribes or disconnects.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Schema में `Subscription` type define करो fields के साथ (जैसे `orderStatusChanged(orderId: ID!): Order!`)।
Step 2 → Resolver को एक `subscribe` function से implement करो (normal resolver नहीं) जो एक **AsyncIterator** return करता है — commonly एक **PubSub** mechanism से backed (single server के लिए in-memory, multiple servers के लिए Redis-backed)।
Step 3 → Client WebSocket से connect करता है (`graphql-ws` protocol use करके) और एक subscription operation भेजता है, बताते हुए कि कौन से fields/arguments चाहिए।
Step 4 → जब भी relevant event publish हो (जैसे जब कोई mutation order की status update करे, वो `pubsub.publish('ORDER_STATUS_CHANGED', { orderStatusChanged: updatedOrder })` call करे), subscription resolver का AsyncIterator नयी value yield करता है।
Step 5 → GraphQL नयी value को WebSocket से HAR currently subscribed client को push करता है, हर client की connection तब तक खुली रहती है जब तक वो unsubscribe या disconnect ना हो।

---

## 🟡 Real World Example
**Uber/Ola's live ride-tracking** (conceptually similar to how many real-time delivery apps work with GraphQL subscriptions) uses a pattern where the rider's app subscribes to `rideLocationUpdated(rideId: "123")`. As the driver's app periodically sends GPS coordinates (via a mutation `updateDriverLocation`), the backend publishes to the PubSub channel, and EVERY rider currently subscribed to that specific `rideId` gets the new coordinates pushed instantly, updating the map marker in real time — without the rider's app needing to poll the server every few seconds asking "where's my driver now?"

## 🟡 Real Example Hindi mein
**Uber/Ola का live ride-tracking** (conceptually कई real-time delivery apps जैसा जो GraphQL subscriptions use करते हैं) एक pattern use करता है जहाँ rider का app `rideLocationUpdated(rideId: "123")` subscribe करता है। जैसे ही driver का app periodically GPS coordinates भेजता है (mutation `updateDriverLocation` के through), backend PubSub channel पर publish करता है, और उस specific `rideId` को subscribe किये हर rider को नये coordinates instantly push हो जाते हैं, map marker real time में update होता है — बिना rider के app को हर कुछ seconds में server से पूछना पड़े "मेरा driver अभी कहाँ है?"

---

## 💻 Code Example — Basic

```javascript
// basic-subscriptions.js
// Install: npm install graphql graphql-subscriptions

const { PubSub } = require('graphql-subscriptions'); // simple in-memory PubSub for single-server demos

const pubsub = new PubSub();
const COMMENT_ADDED = 'COMMENT_ADDED'; // event name/channel identifier

const typeDefs = `#graphql
  type Comment {
    id: ID!
    text: String!
  }

  type Query {
    comments: [Comment!]!
  }

  type Mutation {
    addComment(text: String!): Comment!
  }

  type Subscription {
    commentAdded: Comment!    # fires whenever a new comment is added
  }
`;

let comments = [];

const resolvers = {
  Query: {
    comments: () => comments,
  },
  Mutation: {
    addComment: (_, { text }) => {
      const comment = { id: String(comments.length + 1), text };
      comments.push(comment);
      pubsub.publish(COMMENT_ADDED, { commentAdded: comment }); // notify all subscribers
      return comment;
    },
  },
  Subscription: {
    commentAdded: {
      // subscribe returns an AsyncIterator that yields whenever pubsub.publish is called for this event
      subscribe: () => pubsub.asyncIterableIterator([COMMENT_ADDED]),
    },
  },
};

module.exports = { typeDefs, resolvers, pubsub };

// Client subscribes with: subscription { commentAdded { id text } }
// Every time addComment mutation runs (from ANY client), all subscribers receive the new comment instantly
```

## 💻 Code Example — Advanced

```javascript
// advanced-subscriptions.js — Apollo Server v4 + graphql-ws over a real WebSocket server + filtered subscriptions

const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');          // npm install ws
const { useServer } = require('graphql-ws/lib/use/ws'); // npm install graphql-ws
const { makeExecutableSchema } = require('@graphql-tools/schema'); // npm install @graphql-tools/schema
const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');
const { ApolloServerPluginDrainHttpServer } = require('@apollo/server/plugin/drainHttpServer');
const { PubSub, withFilter } = require('graphql-subscriptions');

const pubsub = new PubSub();
const ORDER_STATUS_CHANGED = 'ORDER_STATUS_CHANGED';

const typeDefs = `#graphql
  type Order { id: ID! status: String! }
  type Query { ping: String! }
  type Mutation { updateOrderStatus(orderId: ID!, status: String!): Order! }
  type Subscription { orderStatusChanged(orderId: ID!): Order! }
`;

const resolvers = {
  Query: { ping: () => 'pong' },
  Mutation: {
    updateOrderStatus: (_, { orderId, status }) => {
      const order = { id: orderId, status };
      pubsub.publish(ORDER_STATUS_CHANGED, { orderStatusChanged: order }); // publish to ALL listeners
      return order;
    },
  },
  Subscription: {
    orderStatusChanged: {
      // withFilter ensures a client subscribed to orderId="5" does NOT receive updates for orderId="9"
      subscribe: withFilter(
        () => pubsub.asyncIterableIterator([ORDER_STATUS_CHANGED]),
        (payload, variables) => payload.orderStatusChanged.id === variables.orderId
      ),
    },
  },
};

async function startServer() {
  const app = express();
  const httpServer = http.createServer(app);
  const schema = makeExecutableSchema({ typeDefs, resolvers });

  // Separate WebSocket server for subscriptions -- HTTP handles Query/Mutation, WS handles Subscription
  const wsServer = new WebSocketServer({ server: httpServer, path: '/graphql' });
  const serverCleanup = useServer({ schema }, wsServer); // wires graphql-ws protocol to our schema

  const apolloServer = new ApolloServer({
    schema,
    plugins: [
      ApolloServerPluginDrainHttpServer({ httpServer }),
      {
        // ensures the WebSocket server also shuts down cleanly alongside Apollo Server
        async serverWillStart() {
          return { async drainServer() { await serverCleanup.dispose(); } };
        },
      },
    ],
  });

  await apolloServer.start();
  app.use('/graphql', express.json(), expressMiddleware(apolloServer));

  httpServer.listen(4000, () => console.log('HTTP+WS server on :4000/graphql'));
}

startServer();

// Client subscribes with variables: subscription($orderId: ID!) { orderStatusChanged(orderId: $orderId) { status } }
// variables: { "orderId": "5" } -- only receives updates for order 5, thanks to withFilter
```

---

## 🟠 Express.js Integration

```javascript
// Subscriptions run over a separate WebSocket layer alongside the normal Express HTTP app,
// both sharing the SAME underlying httpServer instance (as shown in advanced example above).
// Queries/Mutations use normal POST /graphql; Subscriptions use ws://.../graphql
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using in-memory `PubSub` (from `graphql-subscriptions`) across multiple server instances
✅ Correct: The default in-memory PubSub only works within ONE process — if you scale to multiple Node.js instances, a mutation handled by server A won't notify subscribers connected to server B. Use a Redis-backed PubSub (`graphql-redis-subscriptions`) for multi-instance deployments.

```javascript
// Wrong at scale -- in-memory PubSub doesn't broadcast across server instances
const pubsub = new PubSub();

// Right -- Redis-backed, works across all instances
const { RedisPubSub } = require('graphql-redis-subscriptions');
const pubsub = new RedisPubSub({ connection: process.env.REDIS_URL });
```

❌ Mistake 2: Forgetting to filter subscriptions, sending ALL events to ALL subscribers
✅ Correct: Without `withFilter` (or equivalent manual filtering), every subscribed client receives EVERY published event for that subscription field, even ones irrelevant to them (e.g., every order's status change, not just the one they care about) — wasting bandwidth and potentially leaking data.

```javascript
// Wrong -- all subscribers get ALL order updates, including other users' orders
subscribe: () => pubsub.asyncIterableIterator([ORDER_STATUS_CHANGED])

// Right -- only forwards events matching the client's requested orderId
subscribe: withFilter(() => pubsub.asyncIterableIterator([ORDER_STATUS_CHANGED]),
  (payload, vars) => payload.orderStatusChanged.id === vars.orderId)
```

---

## 🧠 Tricky Interview Question

```javascript
// A client subscribes to `orderStatusChanged(orderId: "5")`.
// Before the subscription connects, a mutation already changed order 5's status.
// Does the subscribing client receive that earlier change?
```
Answer: **No.** Like Redis Pub/Sub (which `graphql-subscriptions`' PubSub is often built on or modeled after), GraphQL subscriptions are fire-and-forget — a client only receives events published WHILE it is actively subscribed. Any change that happened BEFORE the subscription connection was established is missed. If clients need the CURRENT state plus future updates, the typical pattern is: first run a Query to fetch current state, THEN start the Subscription for ongoing updates — two separate operations combined client-side.

---

## ⚫ Interview Questions + Answers

Q1: Why do Subscriptions typically use WebSocket instead of plain HTTP?
A1: Plain HTTP request/response is fundamentally request-initiated — the client must ask, then the server responds once, then the connection (logically) ends. Subscriptions need the SERVER to push data to the client at arbitrary times, which requires a persistent, bidirectional connection — WebSocket (or alternatives like Server-Sent Events) provides this, unlike standard HTTP.

Q2: What does the `subscribe` function need to return, and how does it differ from a normal resolver?
A2: A normal resolver returns a VALUE (or a Promise resolving to one). A subscription's `subscribe` function must return an **AsyncIterator** — an object that can be iterated with `for await...of`, yielding a new value each time an event occurs. GraphQL's execution engine consumes this iterator and pushes each yielded value to the client as a new subscription message.

Q3: Why is filtering (e.g., by `orderId`) necessary in subscription resolvers?
A3: Without filtering, a published event broadcasts to EVERY client subscribed to that FIELD NAME, regardless of which specific entity (order, chat room, user) they care about — this can leak OTHER users' data to clients who shouldn't see it, and wastes bandwidth sending irrelevant updates. `withFilter` (or manual filtering inside the AsyncIterator) ensures only matching, authorized events reach each specific subscriber.

Q4: How would you scale GraphQL subscriptions across multiple server instances behind a load balancer?
A4: Use a distributed PubSub backend (Redis Pub/Sub via `graphql-redis-subscriptions`, or a managed service) so that an event published by the server instance handling a mutation reaches ALL other instances, which then forward it to their own locally-connected WebSocket subscribers — the same cross-instance broadcast pattern used for scaling Socket.IO.

Q5: What's an alternative to GraphQL Subscriptions for real-time features, and when might you prefer it?
A5: Plain WebSocket/Socket.IO (without GraphQL) or Server-Sent Events (SSE) are simpler alternatives when you don't need GraphQL's typed query language for the real-time channel itself — e.g., a simple "new notification" ping doesn't need a rich subscription schema. GraphQL Subscriptions are most valuable when the real-time payload itself benefits from GraphQL's type safety, nested field selection, and consistency with the rest of your existing GraphQL API/schema.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Real-time features (live tracking, chat, notifications, live dashboards) where you already have a GraphQL API and want consistent typing/tooling for the real-time layer too.

❌ Avoid when:
- Simple, infrequent updates where basic polling (refetch every N seconds) is simpler and "good enough" — subscriptions add infrastructure complexity (WebSocket servers, PubSub backends) that isn't always justified.
- You need guaranteed delivery/durability — subscriptions (like Pub/Sub) are fire-and-forget; use a message queue if lost events are unacceptable.

---

## 📊 Visual Diagram
```
GRAPHQL SUBSCRIPTION FLOW:
──────────────────────────────────────────────────────────
Client A ──WebSocket──▶ subscribe(orderStatusChanged, orderId: "5")
Client B ──WebSocket──▶ subscribe(orderStatusChanged, orderId: "9")

Mutation updateOrderStatus(orderId: "5", status: "SHIPPED")
         │
         ▼
   pubsub.publish(ORDER_STATUS_CHANGED, {...order 5...})
         │
         ▼
   withFilter checks each subscriber's orderId
         │
    ┌────┴─────┐
    ▼          ▼
Client A      Client B
(orderId=5)   (orderId=9)
RECEIVES ✓    FILTERED OUT ✗ (doesn't match)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Subscription | Real-time push operation type | Real-time push operation type |
| AsyncIterator | Object yielding values over time | समय के साथ values yield करने वाला object |
| PubSub | Publish/subscribe event mechanism | Publish/subscribe event mechanism |
| withFilter | Filters events per-subscriber | Per-subscriber events filter करता है |
| graphql-ws | WebSocket protocol for GraphQL | GraphQL के लिए WebSocket protocol |

---

## ⚡ 3-Line Summary
English:
1. Subscriptions push real-time data to clients over WebSocket, avoiding the latency and waste of polling.
2. The resolver's `subscribe` function returns an AsyncIterator backed by a PubSub mechanism that fires when relevant mutations publish events.
3. Always filter subscription events per-subscriber (`withFilter`) and use a Redis-backed PubSub when scaling across multiple server instances.

Hindi:
1. Subscriptions real-time data को WebSocket से clients तक push करते हैं, polling की latency और waste से बचते हुए।
2. Resolver का `subscribe` function एक AsyncIterator return करता है जो PubSub mechanism से backed है, जो relevant mutations event publish करने पर fire होता है।
3. हमेशा subscription events को per-subscriber filter करो (`withFilter`) और multiple server instances पर scale करते वक़्त Redis-backed PubSub use करो।

---

## ➡️ Next Topic
**186. REST vs GraphQL** — दोनों approaches का detailed comparison और कब कौन सा चुनें।
