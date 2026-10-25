# 184. GraphQL Queries + Mutations
# हिंदी में: GraphQL Queries + Mutations — Read और Write Operations

---

## 🔵 Simple Definition (English)
**Queries** are GraphQL's read operations — fetching data without changing anything on the server (equivalent to REST's `GET`). **Mutations** are write operations — creating, updating, or deleting data (equivalent to REST's `POST`/`PUT`/`PATCH`/`DELETE`). Both use the same query language syntax, but mutations execute SEQUENTIALLY (one after another) while queries can execute fields in PARALLEL.

## 🔵 सरल परिभाषा (Hindi)
**Queries** GraphQL के read operations हैं — server पर कुछ भी बदले बिना data fetch करना (REST के `GET` के बराबर)। **Mutations** write operations हैं — data create, update, या delete करना (REST के `POST`/`PUT`/`PATCH`/`DELETE` के बराबर)। दोनों same query language syntax use करते हैं, पर mutations SEQUENTIALLY (एक के बाद एक) execute होते हैं जबकि queries के fields PARALLEL में execute हो सकते हैं।

---

## 🔴 Problem it Solves
Before this distinction, APIs often didn't clearly separate "operations that are safe to retry/cache/run in parallel" from "operations that change state and must run predictably." GraphQL's spec makes this explicit: Query fields can be resolved concurrently (since reads don't interfere with each other), giving performance benefits — while Mutation fields are GUARANTEED to execute one at a time, in the order written, because unordered/parallel writes could cause race conditions (e.g., two mutations both modifying the same wallet balance). This built-in guarantee removes an entire class of bugs that REST APIs must handle manually (e.g., via explicit locking) if clients happen to batch multiple writes together.

## 🔴 यह क्यों बना? (Hindi)
इस distinction से पहले, APIs अक्सर clearly separate नहीं करते थे "operations जो retry/cache/parallel run करने में safe हैं" को "operations जो state बदलते हैं और predictably run होने चाहिए" से। GraphQL का spec इसे explicit बनाता है: Query fields concurrently resolve हो सकते हैं (क्योंकि reads एक-दूसरे में interfere नहीं करते), performance benefits देते हुए — जबकि Mutation fields GUARANTEED रूप से एक समय में एक, लिखे गए order में execute होते हैं, क्योंकि unordered/parallel writes race conditions cause कर सकते हैं (जैसे दो mutations एक ही wallet balance modify कर रहे हों)। यह built-in guarantee एक पूरी class की bugs हटाता है जो REST APIs को manually handle करनी पड़ती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → A **Query** is written as `query { fieldName(args) { subfields } }` (or just `{ ... }` for anonymous queries) — read-only, no side effects expected.
Step 2 → A **Mutation** is written as `mutation { fieldName(args) { subfields } }` — performs a write, and conventionally RETURNS the affected/created resource so the client gets fresh data in the same round trip.
Step 3 → Multiple fields in ONE query execute in PARALLEL (the GraphQL engine may resolve `field1` and `field2` concurrently since order doesn't matter for reads).
Step 4 → Multiple fields in ONE mutation execute SEQUENTIALLY, left to right, as written — guaranteeing predictable ordering for dependent writes.
Step 5 → Clients typically send **variables** alongside the query/mutation (`mutation($input: OrderInput!) { createOrder(input: $input) { id } }`) rather than string-interpolating values directly — safer and reusable.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक **Query** `query { fieldName(args) { subfields } }` के रूप में लिखी जाती है (या anonymous queries के लिए सिर्फ `{ ... }`) — read-only, कोई side effects expected नहीं।
Step 2 → एक **Mutation** `mutation { fieldName(args) { subfields } }` के रूप में लिखी जाती है — एक write perform करती है, और conventionally affected/created resource RETURN करती है ताकि client को same round trip में fresh data मिले।
Step 3 → ONE query में multiple fields PARALLEL में execute होते हैं (GraphQL engine `field1` और `field2` concurrently resolve कर सकता है क्योंकि reads के लिए order matter नहीं करता)।
Step 4 → ONE mutation में multiple fields SEQUENTIALLY, left to right, written order में execute होते हैं — dependent writes के लिए predictable ordering guarantee करता है।
Step 5 → Clients typically query/mutation के साथ **variables** भेजते हैं (`mutation($input: OrderInput!) { createOrder(input: $input) { id } }`) directly values string-interpolate करने की जगह — safer और reusable।

---

## 🟡 Real World Example
**Shopify's GraphQL Admin API** uses mutations like `productCreate`, `orderUpdate`, `inventoryAdjustQuantity` — EVERY mutation returns the updated resource PLUS a `userErrors` field (a GraphQL convention for business-logic validation errors that aren't exceptions, e.g., "SKU already exists"), letting the client immediately re-render the UI with fresh data and show field-level errors, all from ONE round trip, instead of a separate write call followed by a separate read call (as REST often requires: `POST /products` then `GET /products/:id` to get the full updated object with server-computed fields).

## 🟡 Real Example Hindi mein
**Shopify का GraphQL Admin API** mutations use करता है जैसे `productCreate`, `orderUpdate`, `inventoryAdjustQuantity` — HAR mutation updated resource PLUS एक `userErrors` field return करता है (business-logic validation errors के लिए GraphQL convention, जैसे "SKU already exists"), जो client को ONE round trip में fresh data के साथ UI re-render करने और field-level errors दिखाने देता है, ना कि एक separate write call फिर separate read call (जैसे REST में अक्सर चाहिए: `POST /products` फिर `GET /products/:id`)।

---

## 💻 Code Example — Basic

```javascript
// basic-queries-mutations.js
// Install: npm install @apollo/server graphql

const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');

const typeDefs = `#graphql
  type Todo {
    id: ID!
    text: String!
    done: Boolean!
  }

  type Query {
    todos: [Todo!]!              # read -- lists all todos
  }

  type Mutation {
    addTodo(text: String!): Todo!           # write -- creates a new todo
    toggleTodo(id: ID!): Todo!               # write -- flips done status
  }
`;

let todos = [{ id: '1', text: 'Learn GraphQL', done: false }];

const resolvers = {
  Query: {
    todos: () => todos, // pure read, no side effects
  },
  Mutation: {
    addTodo: (_, { text }) => {
      const todo = { id: String(todos.length + 1), text, done: false };
      todos.push(todo);      // side effect: mutates server state
      return todo;           // convention: return the created resource
    },
    toggleTodo: (_, { id }) => {
      const todo = todos.find(t => t.id === id);
      if (!todo) throw new Error('Todo not found');
      todo.done = !todo.done; // side effect: mutates existing state
      return todo;
    },
  },
};

startStandaloneServer(new ApolloServer({ typeDefs, resolvers }), { listen: { port: 4000 } })
  .then(({ url }) => console.log(`Ready at ${url}`));

// Example mutation: mutation { addTodo(text: "Buy milk") { id text done } }
```

## 💻 Code Example — Advanced

```javascript
// advanced-queries-mutations.js — input types, variables, userErrors convention, sequential mutation guarantee

const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');

const typeDefs = `#graphql
  # Input types group related mutation arguments into a reusable, typed object
  input CreateOrderInput {
    userId: ID!
    items: [OrderItemInput!]!
  }
  input OrderItemInput {
    productId: ID!
    qty: Int!
  }

  type UserError {
    field: String!
    message: String!
  }

  type Order {
    id: ID!
    total: Float!
  }

  # Mutation payload pattern: always return BOTH the result AND any business-logic errors
  type CreateOrderPayload {
    order: Order
    userErrors: [UserError!]!
  }

  type Query {
    ping: String!
  }

  type Mutation {
    createOrder(input: CreateOrderInput!): CreateOrderPayload!
    deductStock(productId: ID!, qty: Int!): Boolean!
  }
`;

const inventory = { p1: 10 };

const resolvers = {
  Query: { ping: () => 'pong' },
  Mutation: {
    createOrder: (_, { input }) => {
      const userErrors = [];
      let total = 0;

      // Validate business rules -- NOT thrown as exceptions, returned as structured userErrors
      for (const item of input.items) {
        const stock = inventory[item.productId];
        if (stock === undefined || stock < item.qty) {
          userErrors.push({ field: 'items', message: `Insufficient stock for ${item.productId}` });
          continue;
        }
        inventory[item.productId] -= item.qty; // deduct stock
        total += item.qty * 100; // pretend price lookup
      }

      if (userErrors.length) {
        return { order: null, userErrors }; // return errors WITHOUT throwing -- client can show them cleanly
      }

      return { order: { id: 'order_1', total }, userErrors: [] };
    },

    deductStock: (_, { productId, qty }) => {
      if (inventory[productId] < qty) throw new Error('Not enough stock'); // true exception -- not a user input issue
      inventory[productId] -= qty;
      return true;
    },
  },
};

startStandaloneServer(new ApolloServer({ typeDefs, resolvers }), { listen: { port: 4000 } })
  .then(({ url }) => console.log(`Ready at ${url}`));

// Example with variables (sent from client):
// mutation CreateOrder($input: CreateOrderInput!) {
//   createOrder(input: $input) { order { id total } userErrors { field message } }
// }
// variables: { "input": { "userId": "u1", "items": [{ "productId": "p1", "qty": 2 }] } }
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
    context: async ({ req }) => ({
      // forward request-scoped info (e.g. auth) into mutations/queries alike
      userId: req.headers['x-user-id'],
    }),
  }));

  app.listen(3000);
}
main();
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Throwing exceptions for expected business-logic failures (like validation) instead of returning structured errors
✅ Correct: Use the `userErrors` payload pattern for EXPECTED failures the client should handle gracefully; reserve thrown exceptions for truly unexpected/system errors.

```javascript
// Wrong -- throws for a normal validation case, forcing client to parse the generic GraphQL errors array
if (!input.email) throw new Error('Email required');

// Right -- returns a structured, field-specific error the UI can map directly to a form field
return { user: null, userErrors: [{ field: 'email', message: 'Email required' }] };
```

❌ Mistake 2: Assuming mutation fields in one request run in parallel like query fields
✅ Correct: Mutations in the SAME request are guaranteed sequential — don't add artificial extra round trips thinking you need to "wait" between them; but DO be aware that unrelated separate GraphQL requests/mutations are NOT ordered relative to each other.

```javascript
// Misunderstanding -- thinking you need two separate requests to ensure order
// mutation 1: deductStock(...)
// mutation 2: createOrder(...)  -- sent as a SEPARATE request, no ordering guarantee vs other concurrent requests

// Better -- combine into ONE mutation request where order IS guaranteed between these two fields
// mutation { deductStock(...) createOrder(...) }
```

---

## 🧠 Tricky Interview Question

```javascript
// mutation {
//   a: toggleTodo(id: "1") { done }
//   b: toggleTodo(id: "1") { done }
// }
// Both fields toggle the SAME todo. What is the final value of todo.done, and why does field order matter here?
```
Answer: Because mutation fields execute **sequentially in the order written**, `a` runs first (flips `done` from, say, `false` to `true`), THEN `b` runs (flips it back to `false`). The final state is `false` — toggled twice, back to its original value. This determinism is a GraphQL spec guarantee specifically for mutations (unlike queries, which may resolve fields in any/parallel order since reads shouldn't have order-dependent side effects) — critical for writing mutations that depend on each other's results within the same request.

---

## ⚫ Interview Questions + Answers

Q1: Why does the GraphQL spec require mutation top-level fields to execute sequentially but allow query fields to execute in any order (including parallel)?
A1: Because mutations have side effects — order matters for correctness (e.g., `deductStock` then `createOrder` must happen in that sequence, not reversed or interleaved unpredictably). Queries are pure reads with no side effects, so their resolution order doesn't affect correctness, allowing the engine to optimize by resolving independent query fields concurrently for better performance.

Q2: What is the "userErrors" / "payload" pattern in GraphQL mutations, and why is it preferred over throwing errors for validation?
A2: Instead of throwing an exception (which gets reported in the generic top-level `errors` array, disconnected from which specific field/mutation caused it, and nulls out the mutation's result), the mutation returns a payload object containing BOTH the (possibly null) result AND a `userErrors` array with field-specific, structured error info. This lets the client map errors directly to form fields and keeps the response `data` fully intact and typed, rather than mixed into GraphQL's generic error-handling machinery meant for unexpected failures.

Q3: Can a single GraphQL request contain BOTH queries and mutations?
A3: No — a single GraphQL OPERATION (document) must be either entirely a query, entirely a mutation, or entirely a subscription; you can't mix top-level Query and Mutation fields in one operation. However, a mutation's SELECTION SET (the `{ ... }` after the mutation field) can request nested read-like data as part of the mutation's response (e.g., `createOrder(...) { order { id total } }` — this IS reading the result, but it's part of the mutation's own return type, not a separate query).

Q4: Why should clients use GraphQL variables instead of string-interpolating values directly into the query text?
A4: Variables (`mutation($id: ID!) { toggleTodo(id: $id) { done } }` with `variables: { id: "1" }`) avoid injection-style bugs, allow the GraphQL server to cache/parse the QUERY STRUCTURE once and reuse it across different variable values (better performance for repeated queries), and avoid manual escaping of special characters in string-interpolated values (quotes, newlines).

Q5: How do you implement optimistic UI updates on the client for a mutation, and what GraphQL client feature supports this?
A5: Clients like Apollo Client support an `optimisticResponse` option — the UI immediately renders an assumed successful result (e.g., showing the new todo as added) BEFORE the server actually responds, then reconciles with the REAL response when it arrives (rolling back if the mutation actually failed). This improves perceived performance for actions where failure is rare, at the cost of needing careful rollback/reconciliation logic for the failure case.

---

## 🔷 When to Use + When Not to Use
✅ Use Queries when:
- Any read-only data fetch, regardless of how nested/related the data is.

✅ Use Mutations when:
- Any operation that creates, updates, or deletes data, or has side effects (sending an email, charging a payment).

❌ Avoid designing mutations that ALSO silently have unrelated side reads/writes beyond their stated purpose — keep each mutation's effect scope clear and documented, since clients rely on the sequential-execution guarantee for predictability.

---

## 📊 Visual Diagram
```
QUERY (parallel-safe):                 MUTATION (sequential, ordered):
──────────────────────                 ────────────────────────────────
query {                                mutation {
  user { name }      ─┐                  deductStock(...)   ← runs FIRST
  products { name }   ├─ run in any       createOrder(...)   ← runs SECOND, can depend on stock
  orders { total }   ─┘   order/parallel  sendConfirmation(...) ← runs THIRD
}                                       }
  No side effects -> order              Side effects -> order
  doesn't matter for correctness        MUST be deterministic
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Query | Read operation | Read operation |
| Mutation | Write operation | Write operation |
| Variables | Parameterized query inputs | Parameterized query inputs |
| Input type | Typed object for mutation arguments | Mutation arguments के लिए typed object |
| userErrors pattern | Structured business-error payload | Structured business-error payload |
| Sequential execution | Mutations run one after another | Mutations एक के बाद एक run होते हैं |

---

## ⚡ 3-Line Summary
English:
1. Queries are read-only and can resolve fields in parallel; mutations have side effects and execute sequentially in the written order.
2. Use the `userErrors` payload pattern for expected validation/business failures instead of throwing exceptions, which are better reserved for unexpected errors.
3. Use input types and variables for mutation arguments — safer, reusable, and avoids manual string interpolation.

Hindi:
1. Queries read-only हैं और fields parallel में resolve हो सकते हैं; mutations में side effects हैं और written order में sequentially execute होते हैं।
2. Expected validation/business failures के लिए `userErrors` payload pattern use करो, exceptions throw करने की जगह जो unexpected errors के लिए बेहतर reserved हैं।
3. Mutation arguments के लिए input types और variables use करो — safer, reusable, और manual string interpolation से बचाता है।

---

## ➡️ Next Topic
**185. GraphQL Subscriptions** — Real-time updates WebSocket के through क्लाइंट्स को push करना।
