# 183. GraphQL Schema + Resolvers
# हिंदी में: GraphQL Schema + Resolvers — Types, Fields, और Resolution Patterns

---

## 🔵 Simple Definition (English)
The **schema** is the contract defining every type, field, and operation your GraphQL API supports (written in Schema Definition Language — SDL). **Resolvers** are the functions that actually implement HOW each field's value is fetched/computed. The schema is the "what's possible," resolvers are the "how it actually happens."

## 🔵 सरल परिभाषा (Hindi)
**Schema** वो contract है जो GraphQL API के हर type, field, और operation को define करता है (Schema Definition Language — SDL में लिखा)। **Resolvers** वो functions हैं जो actually implement करते हैं कि हर field की value कैसे fetch/compute होती है। Schema "क्या possible है" है, resolvers "actually कैसे होता है" हैं।

---

## 🔴 Problem it Solves
Without a strongly-typed schema, an API's shape is implicit and discoverable only by reading server code or hitting endpoints and guessing. GraphQL's schema makes the ENTIRE API contract explicit and machine-readable: every type, every field's type (`String`, `Int`, nullable vs `!` non-null, lists `[Type]`), every argument. This enables: auto-generated documentation, client-side type generation (TypeScript types from the schema), compile-time query validation (catching typos/invalid queries before runtime), and tooling like GraphQL Playground/introspection. Resolvers then cleanly separate "what shape of data exists" (schema) from "where/how that data actually comes from" (resolver implementation — DB, cache, another API).

## 🔴 यह क्यों बना? (Hindi)
Strongly-typed schema के बिना, API का shape implicit होता है, सिर्फ server code पढ़कर या endpoints hit करके guess करने से पता चलता है। GraphQL का schema पूरे API contract को explicit और machine-readable बनाता है: हर type, हर field का type (`String`, `Int`, nullable vs `!` non-null, lists `[Type]`), हर argument। यह enable करता है: auto-generated documentation, client-side type generation (schema से TypeScript types), compile-time query validation, और tooling जैसे GraphQL Playground/introspection। Resolvers फिर cleanly separate करते हैं "कौन सा data shape exists करता है" (schema) को "वो data actually कहाँ से/कैसे आता है" (resolver implementation) से।

---

## 🟢 How it Works — Step by Step

Step 1 → Define **scalar** types (`String`, `Int`, `Float`, `Boolean`, `ID`) and **object** types (`type User { id: ID! name: String! }`) in SDL.
Step 2 → Mark fields **non-nullable** with `!` (e.g., `name: String!` means this field will NEVER be null in a valid response) — a strong contract enforced by the GraphQL execution engine itself.
Step 3 → Define the special root types: `Query` (read operations), `Mutation` (write operations), `Subscription` (real-time operations).
Step 4 → For EVERY field, GraphQL calls a resolver — if you don't define one explicitly, a DEFAULT resolver looks for a matching property on the parent object (so trivial fields often need no explicit resolver).
Step 5 → Resolver function signature: `(parent, args, context, info) => value`. `parent` is the resolved value of the parent field (e.g., the `User` object when resolving `User.orders`); `args` are the field's arguments; `context` is shared per-request data; `info` has schema/query metadata.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → SDL में **scalar** types (`String`, `Int`, `Float`, `Boolean`, `ID`) और **object** types (`type User { id: ID! name: String! }`) define करो।
Step 2 → Fields को `!` से **non-nullable** mark करो (जैसे `name: String!` मतलब यह field valid response में कभी null नहीं होगा) — GraphQL execution engine द्वारा enforced strong contract।
Step 3 → Special root types define करो: `Query` (read operations), `Mutation` (write operations), `Subscription` (real-time operations)।
Step 4 → हर field के लिए, GraphQL एक resolver call करता है — अगर तुमने explicitly define नहीं किया, तो एक DEFAULT resolver parent object पर matching property ढूँढता है (इसलिए trivial fields को अक्सर explicit resolver नहीं चाहिए)।
Step 5 → Resolver function signature: `(parent, args, context, info) => value`। `parent` parent field की resolved value है; `args` field के arguments हैं; `context` per-request shared data है; `info` schema/query metadata रखता है।

---

## 🟡 Real World Example
**Github's GraphQL API** schema defines hundreds of types (`Repository`, `Issue`, `PullRequest`, `User`) with deeply typed relationships. A field like `Repository.issues(first: 10, states: [OPEN])` has a resolver that translates GraphQL arguments into an actual database/search query, applies pagination (`first`), filters by state, and returns a connection object. The STRICT typing (e.g., `states: [IssueState!]` where `IssueState` is an enum of `OPEN`/`CLOSED`) means invalid queries (`states: ["INVALID"]`) are rejected at validation time, BEFORE any resolver even runs — catching client bugs early without wasting server resources.

## 🟡 Real Example Hindi mein
**Github का GraphQL API** schema सैकड़ों types (`Repository`, `Issue`, `PullRequest`, `User`) define करता है deeply typed relationships के साथ। `Repository.issues(first: 10, states: [OPEN])` जैसे field का resolver GraphQL arguments को actual database/search query में translate करता है, pagination apply करता है (`first`), state से filter करता है, और एक connection object return करता है। STRICT typing (जैसे `states: [IssueState!]` जहाँ `IssueState` एक enum है `OPEN`/`CLOSED` का) का मतलब invalid queries (`states: ["INVALID"]`) validation time पर ही reject हो जाती हैं, किसी resolver के run होने से पहले — client bugs जल्दी catch होते हैं बिना server resources waste किये।

---

## 💻 Code Example — Basic

```javascript
// basic-schema-resolvers.js
// Install: npm install @apollo/server graphql

const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');

const typeDefs = `#graphql
  # Enum: a restricted set of allowed string values
  enum OrderStatus {
    PLACED
    SHIPPED
    DELIVERED
  }

  type Order {
    id: ID!
    total: Float!
    status: OrderStatus!     # non-null -- resolver must always return a valid enum value
    note: String             # nullable -- can legitimately be null/absent
  }

  type Query {
    order(id: ID!): Order        # argument `id` is required (ID!)
    orders(status: OrderStatus): [Order!]!  # optional filter argument
  }
`;

const ordersDb = [
  { id: '1', total: 500, status: 'PLACED', note: null },
  { id: '2', total: 1200, status: 'DELIVERED', note: 'left at gate' },
];

const resolvers = {
  Query: {
    // (parent, args, context, info) -- parent is unused at the root Query level (often named `_`)
    order: (_, { id }) => ordersDb.find(o => o.id === id) || null,
    orders: (_, { status }) => status ? ordersDb.filter(o => o.status === status) : ordersDb,
  },
};

startStandaloneServer(new ApolloServer({ typeDefs, resolvers }), { listen: { port: 4000 } })
  .then(({ url }) => console.log(`Ready at ${url}`));

// Example query: { orders(status: DELIVERED) { id total note } }
```

## 💻 Code Example — Advanced

```javascript
// advanced-schema-resolvers.js — nested types, default resolvers, custom scalar, resolver chaining

const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');
const { GraphQLScalarType, Kind } = require('graphql');

// Custom scalar type for Date -- GraphQL has no built-in Date type, so we define serialization rules
const DateScalar = new GraphQLScalarType({
  name: 'Date',
  description: 'ISO date string',
  serialize: (value) => value.toISOString(),             // JS Date -> string sent to client
  parseValue: (value) => new Date(value),                 // client input string -> JS Date
  parseLiteral: (ast) => ast.kind === Kind.STRING ? new Date(ast.value) : null,
});

const typeDefs = `#graphql
  scalar Date

  type User {
    id: ID!
    name: String!
  }

  type Order {
    id: ID!
    total: Float!
    createdAt: Date!
    user: User!          # nested object -- needs its OWN resolver (not just a property lookup)
  }

  type Query {
    orders: [Order!]!
  }
`;

const ordersDb = [{ id: '1', total: 500, userId: 'u1', createdAt: new Date() }];
const usersDb = [{ id: 'u1', name: 'Rahul' }];

const resolvers = {
  Date: DateScalar, // wire up the custom scalar's serialize/parse logic

  Query: {
    orders: () => ordersDb,
  },

  Order: {
    // Fields like `id`, `total`, `createdAt` need NO explicit resolver here --
    // GraphQL's DEFAULT resolver automatically reads order.id, order.total, order.createdAt
    // because ordersDb objects already have matching property names.

    // `user` DOES need an explicit resolver, because `order.user` doesn't exist directly --
    // we must look it up via order.userId
    user: (order) => usersDb.find(u => u.id === order.userId),
  },
};

startStandaloneServer(new ApolloServer({ typeDefs, resolvers }), { listen: { port: 4000 } })
  .then(({ url }) => console.log(`Ready at ${url}`));

// Example query: { orders { id total createdAt user { name } } }
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');

async function main() {
  const app = express();
  const server = new ApolloServer({ typeDefs, resolvers });
  await server.start();

  app.use('/graphql', express.json(), expressMiddleware(server, {
    // Pass req so resolvers/context can access headers for auth, etc.
    context: async ({ req }) => ({ req }),
  }));

  app.listen(3000);
}
main();
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Marking a field non-nullable (`!`) when the resolver can legitimately return null
✅ Correct: If there's ANY chance a field is missing/null, don't use `!` — GraphQL will throw an execution error (and null out the ENTIRE parent object, "null bubbling") if a non-null field resolves to null.

```javascript
// Wrong -- note can genuinely be null in the data, but schema promises it's always present
note: String!

// Right -- schema honestly reflects that note may be absent
note: String
```

❌ Mistake 2: Writing a resolver for a field that doesn't need one (property name mismatch confusion)
✅ Correct: Only write explicit resolvers for fields that need COMPUTED or RELATED data; let the default resolver handle direct property matches, but ensure your data object's property names actually MATCH the schema field names, or add a resolver to bridge the gap.

```javascript
// Wrong -- schema field is `total`, but DB object has `totalAmount` -- default resolver finds undefined!
type Order { total: Float! }   // but order.total is undefined because DB uses totalAmount

// Right -- add an explicit resolver to bridge the naming mismatch
Order: { total: (order) => order.totalAmount }
```

---

## 🧠 Tricky Interview Question

```javascript
// type Order { user: User! }   (non-null)
// Resolver: user: (order) => usersDb.find(u => u.id === order.userId)
// If the matching user doesn't exist in usersDb, find() returns undefined.
// What happens to the ENTIRE query response?
```
Answer: GraphQL treats `undefined` the same as `null` for a non-nullable field — since `User!` promises the field can NEVER be null, this triggers a **null bubbling / error propagation**: GraphQL throws an error for this field, and because the field is non-nullable, the error propagates UP to the nearest NULLABLE ancestor field, nulling it out instead (or nulling the entire `data` object if everything up the chain is non-nullable). This is why schema nullability choices matter — an overly strict `!` on a field that CAN realistically be missing can cause much larger parts of a response to disappear than expected.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `String` and `String!` in a GraphQL schema?
A1: `String` means the field is nullable — it can return a string value OR `null`. `String!` means NON-NULL — the field must always resolve to an actual string value; if the resolver returns `null`/`undefined`, GraphQL treats it as a schema-violation error and bubbles the null up to the nearest nullable ancestor.

Q2: What are the four resolver function arguments, and what does each represent?
A2: `(parent, args, context, info)`. **parent** — the resolved value of the field's parent object (useful for nested fields needing data from the parent, like `order.userId`). **args** — the arguments passed to this field in the query (e.g., `{ id: "5" }` for `order(id: "5")`). **context** — shared, per-request data available to ALL resolvers (auth info, DataLoaders, DB connections). **info** — metadata about the execution state (field name, schema, query AST) — rarely used except for advanced tooling.

Q3: When does a field NOT need an explicit resolver?
A3: When the field name on the schema type exactly matches a property name on the object returned by the PARENT resolver, GraphQL's default resolver automatically reads that property. E.g., if `Query.orders` returns `[{ id, total }]` and the schema has `type Order { id: ID! total: Float! }`, no explicit resolver is needed for `id` or `total` — only for fields requiring extra lookups/computation (like `user` needing a separate DB call).

Q4: What is an Enum type used for in a GraphQL schema, and what's its benefit over using a plain String?
A4: An Enum restricts a field's possible values to a fixed, named set (e.g., `enum OrderStatus { PLACED SHIPPED DELIVERED }`). Unlike a plain `String`, GraphQL validates at the QUERY level that only these exact values are used as arguments/returned — catching typos (`"SHIPED"`) and invalid values before they ever reach a resolver, and giving clients auto-complete/documentation of valid options via introspection.

Q5: How would you handle a field that's expensive to compute and rarely requested, like `User.totalLifetimeSpend`?
A5: Because GraphQL only calls a field's resolver IF the client actually requests that field in their query, expensive/rarely-needed fields are naturally "lazy" — if a client's query doesn't include `totalLifetimeSpend`, its resolver never runs at all. This is one of GraphQL's built-in efficiency benefits over REST, where a fixed endpoint response always computes ALL its fields regardless of whether the client needs them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a strongly-typed, self-documenting contract for your API that both humans and tools (codegen, validation) can rely on.
- Resolvers need to compose data from multiple sources (DB + cache + another API) behind a clean, unified field.

❌ Avoid when:
- The data model is extremely simple/flat with no real relationships to traverse — the schema/resolver machinery adds overhead with little benefit over a plain REST JSON response.

---

## 📊 Visual Diagram
```
SCHEMA (the "what")              RESOLVERS (the "how")
───────────────────────          ─────────────────────────────
type Order {                     Order: {
  id: ID!                          // no resolver needed -- default property lookup
  total: Float!                    // no resolver needed -- default property lookup
  user: User!                      user: (order) => usersDb.find(u => u.id === order.userId)
}                                 }

Query resolution order:
Query.orders() → returns [{id, total, userId}, ...]
      │
      ▼
For EACH order, Order.user(order) resolver runs
      │
      ▼
Final shape exactly matches the client's requested fields
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SDL | Schema Definition Language | Schema Definition Language |
| Non-null (!) | Field must never be null | कभी null ना होने वाला field |
| Default resolver | Auto property lookup resolver | Auto property lookup resolver |
| Enum | Restricted set of allowed values | Allowed values का restricted set |
| Null bubbling | Error propagation on non-null violation | Non-null violation पर error propagation |
| Custom scalar | User-defined primitive type | User-defined primitive type |

---

## ⚡ 3-Line Summary
English:
1. The schema (SDL) defines types, fields, and nullability as a strict, self-documenting API contract.
2. Resolvers implement how each field's value is actually fetched; fields matching parent object properties get a free default resolver.
3. Be careful with non-null (`!`) fields — a resolver returning null/undefined for one bubbles the error up, potentially nulling large parts of the response.

Hindi:
1. Schema (SDL) types, fields, और nullability को एक strict, self-documenting API contract के रूप में define करता है।
2. Resolvers implement करते हैं कि हर field की value actually कैसे fetch होती है; parent object properties से match होने वाले fields को free default resolver मिलता है।
3. Non-null (`!`) fields से सावधान रहो — resolver अगर null/undefined return करे तो error bubble होकर response के बड़े हिस्से को null कर सकता है।

---

## ➡️ Next Topic
**184. GraphQL Queries + Mutations** — Read और write operations को properly structure करना।
