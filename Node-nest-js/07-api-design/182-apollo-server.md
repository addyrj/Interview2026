# 182. Apollo Server
# हिंदी में: Apollo Server — Production-Grade GraphQL Server

---

## 🔵 Simple Definition (English)
**Apollo Server** is the most widely used, production-grade GraphQL server library for Node.js. It builds on top of the base `graphql` package, adding features needed for real applications: plugins, caching, error formatting, performance tracing, schema federation (splitting a schema across microservices), and easy integration with Express/standalone HTTP servers.

## 🔵 सरल परिभाषा (Hindi)
**Apollo Server** Node.js के लिए सबसे widely used, production-grade GraphQL server library है। यह base `graphql` package के ऊपर बनता है, और real applications के लिए ज़रूरी features add करता है: plugins, caching, error formatting, performance tracing, schema federation (schema को microservices में split करना), और Express/standalone HTTP servers के साथ आसान integration।

---

## 🔴 Problem it Solves
The raw `graphql` library gives you just the query execution engine — building a real production GraphQL API with it directly means manually handling: HTTP transport, request parsing, error formatting, introspection/playground tooling, caching headers, authentication context injection, and performance monitoring. Apollo Server packages all of this into a batteries-included server, so teams don't reinvent these production concerns for every GraphQL project. It also pioneered **Apollo Federation**, letting large organizations split one giant GraphQL schema across multiple independently-deployed microservices while still presenting ONE unified graph to clients.

## 🔴 यह क्यों बना? (Hindi)
Raw `graphql` library सिर्फ query execution engine देती है — इससे directly production GraphQL API बनाने में manually handle करना पड़ता: HTTP transport, request parsing, error formatting, introspection/playground tooling, caching headers, authentication context injection, performance monitoring। Apollo Server इन सबको एक batteries-included server में package करता है, ताकि teams हर GraphQL project के लिए यह production concerns दोबारा ना बनाएं। इसने **Apollo Federation** भी pioneer किया, जो बड़ी organizations को एक giant GraphQL schema को multiple independently-deployed microservices में split करने देता है, फिर भी clients को ONE unified graph दिखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define `typeDefs` (the schema, same SDL syntax as raw GraphQL) and `resolvers` (an object mapping type/field names to resolver functions).
Step 2 → Create an `ApolloServer` instance passing `typeDefs` and `resolvers`.
Step 3 → Start the server and attach it to an Express app (or use it standalone) via `expressMiddleware` (Apollo Server v4) — this handles HTTP request/response plumbing.
Step 4 → Optionally add a `context` function that runs per-request, extracting things like the authenticated user from headers and making it available to all resolvers.
Step 5 → Add plugins for logging, caching, error tracking, or metrics — Apollo Server's plugin system hooks into the request lifecycle (`requestDidStart`, `willSendResponse`, etc.).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `typeDefs` (schema, same SDL syntax) और `resolvers` (type/field names को resolver functions से map करने वाला object) define करो।
Step 2 → `typeDefs` और `resolvers` pass करके `ApolloServer` instance बनाओ।
Step 3 → Server start करो और Express app से attach करो (या standalone use करो) `expressMiddleware` (Apollo Server v4) से — यह HTTP request/response plumbing handle करता है।
Step 4 → Optionally एक `context` function add करो जो per-request चलता है, headers से authenticated user extract करके सारे resolvers को available कराता है।
Step 5 → Logging, caching, error tracking, metrics के लिए plugins add करो — Apollo Server का plugin system request lifecycle में hook करता है (`requestDidStart`, `willSendResponse`, आदि)।

---

## 🟡 Real World Example
**Expedia and Airbnb** (both well-known Apollo adopters) use Apollo Federation to let dozens of independent backend teams (flights, hotels, user accounts, reviews) each own and deploy their OWN piece of the GraphQL schema (a "subgraph"), while a Gateway composes them into ONE graph that frontend teams query against — without frontend teams needing to know or care which backend team/service actually serves which field. This solves the organizational scaling problem of "one giant monolithic GraphQL schema maintained by one team" becoming a bottleneck.

## 🟡 Real Example Hindi mein
**Expedia और Airbnb** (दोनों well-known Apollo adopters) Apollo Federation use करते हैं ताकि दर्जनों independent backend teams (flights, hotels, user accounts, reviews) अपना-अपना GraphQL schema का हिस्सा ("subgraph") own और deploy करें, जबकि एक Gateway उन्हें ONE graph में compose करता है जिसे frontend teams query करती हैं — बिना यह जाने/सोचे कि कौन सा backend team/service actually कौन सा field serve करता है। यह "एक giant monolithic GraphQL schema, एक team maintain करे" वाली organizational scaling problem solve करता है।

---

## 💻 Code Example — Basic

```javascript
// basic-apollo.js
// Install: npm install @apollo/server graphql

const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');

// Schema definition (SDL) -- same syntax as raw graphql-js
const typeDefs = `#graphql
  type Book {
    title: String!
    author: String!
  }

  type Query {
    books: [Book!]!
  }
`;

const books = [
  { title: 'The Pragmatic Programmer', author: 'David Thomas' },
  { title: 'Clean Code', author: 'Robert C. Martin' },
];

// Resolvers -- Apollo Server expects this shape: { TypeName: { fieldName: fn } }
const resolvers = {
  Query: {
    books: () => books, // resolves the `books` query field
  },
};

async function startServer() {
  const server = new ApolloServer({ typeDefs, resolvers });

  // startStandaloneServer runs its own HTTP server (good for quick starts, not inside existing Express)
  const { url } = await startStandaloneServer(server, { listen: { port: 4000 } });
  console.log(`Apollo Server ready at ${url}`);
}

startServer();

// Example query: { books { title author } }
```

## 💻 Code Example — Advanced

```javascript
// advanced-apollo.js — integrated with Express, auth context, error formatting, DataLoader

const express = require('express');
const http = require('http');
const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');
const { ApolloServerPluginDrainHttpServer } = require('@apollo/server/plugin/drainHttpServer');
const jwt = require('jsonwebtoken'); // npm install jsonwebtoken
const DataLoader = require('dataloader');

const typeDefs = `#graphql
  type User {
    id: ID!
    name: String!
  }
  type Order {
    id: ID!
    total: Float!
    user: User!
  }
  type Query {
    myOrders: [Order!]!
  }
`;

const ordersDb = [{ id: 'o1', userId: 'u1', total: 500 }];
const usersDb = [{ id: 'u1', name: 'Rahul' }];

const resolvers = {
  Query: {
    // `context.user` is injected per-request from the JWT -- resolvers never parse headers directly
    myOrders: (_, __, context) => {
      if (!context.user) throw new Error('Not authenticated'); // auth check inside the resolver
      return ordersDb.filter(o => o.userId === context.user.id);
    },
  },
  Order: {
    user: (order, _, context) => context.userLoader.load(order.userId), // batched via DataLoader
  },
};

async function startServer() {
  const app = express();
  const httpServer = http.createServer(app);

  const server = new ApolloServer({
    typeDefs,
    resolvers,
    // Drain plugin ensures graceful shutdown -- in-flight requests finish before the server closes
    plugins: [ApolloServerPluginDrainHttpServer({ httpServer })],
    // Centralized error formatting -- hide internal details from clients in production
    formatError: (formattedError, error) => {
      console.error('GraphQL error:', error); // full details logged server-side
      if (process.env.NODE_ENV === 'production' && !formattedError.extensions?.code) {
        return { message: 'Internal server error' }; // strip stack traces etc from client-facing error
      }
      return formattedError;
    },
  });

  await server.start(); // MUST be awaited before applying middleware

  app.use(
    '/graphql',
    express.json(),
    expressMiddleware(server, {
      // context runs per-request, building fresh DataLoaders (avoids cross-request cache leaks)
      context: async ({ req }) => {
        const token = req.headers.authorization?.replace('Bearer ', '');
        let user = null;
        try {
          if (token) user = jwt.verify(token, process.env.JWT_SECRET); // decode authenticated user
        } catch { /* invalid/expired token -> treat as unauthenticated */ }

        const userLoader = new DataLoader(async (ids) => ids.map(id => usersDb.find(u => u.id === id)));
        return { user, userLoader };
      },
    })
  );

  await new Promise((resolve) => httpServer.listen({ port: 4000 }, resolve));
  console.log('Apollo Server (Express) ready at http://localhost:4000/graphql');
}

startServer();
```

---

## 🟠 Express.js Integration

```javascript
// Running Apollo Server ALONGSIDE existing REST routes in the same Express app
const express = require('express');
const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');

async function main() {
  const app = express();

  // Existing REST endpoints stay untouched
  app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

  const server = new ApolloServer({ typeDefs, resolvers });
  await server.start();

  app.use('/graphql', express.json(), expressMiddleware(server, {
    context: async ({ req }) => ({ user: req.user }), // assume auth middleware ran earlier, set req.user
  }));

  app.listen(3000, () => console.log('Server with REST + GraphQL on 3000'));
}

main();
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to `await server.start()` before mounting the Express middleware
✅ Correct: Apollo Server v4 requires an explicit async start before `expressMiddleware` can be used — skipping it causes requests to hang or error.

```javascript
// Wrong
const server = new ApolloServer({ typeDefs, resolvers });
app.use('/graphql', expressMiddleware(server)); // server not started yet!

// Right
await server.start();
app.use('/graphql', expressMiddleware(server));
```

❌ Mistake 2: Putting authentication logic inside every resolver instead of the `context` function
✅ Correct: Decode auth ONCE per request in `context`, then resolvers just read `context.user` — avoids duplicated/inconsistent auth logic.

```javascript
// Wrong -- duplicated across resolvers
myOrders: (_, __, { req }) => { const token = req.headers.authorization; /* decode again */ }

// Right -- decoded once in context, reused everywhere
context: async ({ req }) => ({ user: decodeToken(req.headers.authorization) })
```

---

## 🧠 Tricky Interview Question

```javascript
// Two different GraphQL requests hit the server concurrently.
// If `context` creates a new DataLoader instance each time, do requests ever share cached data?
```
Answer: **No, and that's intentional.** Each request gets its OWN `context` (and thus its own fresh `DataLoader` instance), so caching is scoped strictly to a SINGLE request's lifetime. This is correct behavior — if DataLoader caches were shared ACROSS requests, one user's resolved data could leak into another user's response (a serious bug/security issue), or stale data could be served after an update. DataLoader's caching is meant only to deduplicate/batch calls WITHIN one request's resolution, not across requests.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `startStandaloneServer` and `expressMiddleware` in Apollo Server v4?
A1: `startStandaloneServer` spins up its OWN minimal HTTP server — quick for standalone GraphQL services or prototypes, but you can't easily add custom Express middleware (session handling, REST routes alongside it). `expressMiddleware` integrates Apollo Server INTO an existing Express app, letting you combine GraphQL with REST routes, custom middleware, and full control over the HTTP server setup.

Q2: What is Apollo Federation and why would a large company use it?
A2: Federation lets you split a single large GraphQL schema into multiple independently deployable "subgraphs," each owned by a different team/service, then compose them via a Gateway into one unified graph for clients. This solves organizational scaling: without it, one team/schema becomes a bottleneck for a large company with many backend teams each owning different domains (users, orders, payments).

Q3: How does Apollo Server handle errors differently from a raw try/catch in resolvers?
A3: Any error thrown (or rejected promise) inside a resolver is automatically caught by Apollo Server, formatted into the GraphQL spec's `errors` array in the response (alongside any partial `data` that WAS successfully resolved), and can be customized globally via the `formatError` function — centralizing error shaping instead of needing try/catch in every single resolver.

Q4: Why is `context` created freshly per-request rather than once per server instance?
A4: Because context often holds request-specific data: the authenticated user, request-scoped DataLoader caches, tracing/request IDs. Sharing one context object across requests would leak data between different users' requests (a serious security bug) and break DataLoader's per-request caching guarantees.

Q5: What built-in protections does Apollo Server offer against malicious/expensive queries?
A5: Apollo Server supports plugins/validation rules for query depth limiting, query complexity analysis (assigning a "cost" to each field and rejecting overly expensive queries), and (in Apollo Server's landscape) tools like `graphql-query-complexity` or `graphql-depth-limit` integrate as validation rules. It also supports disabling introspection and the GraphQL Playground in production to reduce attack surface/information leakage.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building a production GraphQL API in Node.js and need battle-tested tooling (error formatting, plugins, tracing) rather than hand-rolling it on raw `graphql`.
- Operating at an organizational scale where Apollo Federation's multi-team schema composition is valuable.

❌ Avoid when:
- A tiny prototype/internal tool where the raw `graphql` package or a lighter alternative (e.g., Mercurius for Fastify) is simpler and sufficient.
- Your team has no GraphQL-specific needs (varying client data shapes, deep relational queries) — plain REST may be simpler overall.

---

## 📊 Visual Diagram
```
APOLLO SERVER REQUEST LIFECYCLE:
──────────────────────────────────────────────────
Client POST /graphql { query: "{ myOrders { total user { name } } }" }
         │
         ▼
  context() runs — decode JWT, build fresh DataLoaders
         │
         ▼
  Query validated against schema (typeDefs)
         │
         ▼
  Resolvers execute (Query.myOrders → Order.user, batched via DataLoader)
         │
         ▼
  formatError (if any errors) + response assembled
         │
         ▼
  { data: { myOrders: [...] } }  returned to client
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| typeDefs | Schema definition string | Schema definition string |
| resolvers | Functions implementing schema fields | Schema fields implement करने वाले functions |
| context | Per-request shared data for resolvers | Resolvers के लिए per-request shared data |
| Apollo Federation | Multi-team schema composition | Multi-team schema composition |
| formatError | Global error-shaping hook | Global error-shaping hook |

---

## ⚡ 3-Line Summary
English:
1. Apollo Server is the production-grade GraphQL server for Node.js, adding error formatting, plugins, and Express integration on top of raw `graphql`.
2. Always `await server.start()` before mounting it, and build request-scoped `context` (auth, DataLoaders) fresh per request.
3. Apollo Federation lets large orgs split one graph across many independently-deployed subgraphs owned by different teams.

Hindi:
1. Apollo Server Node.js के लिए production-grade GraphQL server है, जो raw `graphql` के ऊपर error formatting, plugins, Express integration add करता है।
2. Mount करने से पहले हमेशा `await server.start()` करो, और request-scoped `context` (auth, DataLoaders) हर request पर fresh बनाओ।
3. Apollo Federation बड़ी organizations को एक graph को कई independently-deployed subgraphs में split करने देता है, जो अलग teams own करती हैं।

---

## ➡️ Next Topic
**183. GraphQL Schema + Resolvers** — Schema types, fields, और resolver patterns को गहराई से समझना।
