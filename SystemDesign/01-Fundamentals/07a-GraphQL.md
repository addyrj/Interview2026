# 07a. GraphQL ⭐
# हिंदी में: GraphQL — एक ऐसी API भाषा जिसमें क्लाइंट ख़ुद बताता है कि उसे कौन-सा डेटा चाहिए, और एक ही request में ठीक उतना ही मिलता है

---

## 🔵 Simple Definition (English)
**GraphQL** is a query language for APIs (created by Facebook in 2012). The server exposes **one endpoint** (`/graphql`) with a typed **schema**, and the client sends a **query** describing exactly the fields it wants, including nested related data, and gets exactly that shape back in **one request**.

## 🔵 सरल परिभाषा (Hindi)
GraphQL में सर्वर का एक ही endpoint होता है और एक schema (डेटा का नक्शा)।
क्लाइंट query में लिखता है "मुझे ये-ये fields चाहिए", और सर्वर एक ही बार में ठीक वही डेटा देता है — न कम, न ज़्यादा।

---

## 🔴 Problem it Solves
Facebook's mobile app (2012) had a news feed screen needing: posts + author name/photo + like count + first 2 comments + commenter names. With REST:

```
GET /feed                    → post ids
GET /posts/1, /posts/2 ...   → each post (with 40 fields, needs 5)  ← OVER-fetching
GET /users/9                 → author
GET /posts/1/comments        → comments                             ← UNDER-fetching (many calls)
= 10–30 round trips on a slow 3G network → slow app
```
Also, every new screen or app version needed a new REST endpoint or new fields → backend teams became a bottleneck.

GraphQL: **one request, exact fields, strongly typed, and the frontend evolves without new endpoints.**

## 🔴 यह क्यों बना? (Hindi)
Facebook ऐप की एक स्क्रीन के लिए REST में 10-30 API कॉल लगती थीं, और हर कॉल में ज़रूरत से ज़्यादा डेटा आता था — 3G पर ऐप धीमा हो जाता था।
GraphQL से क्लाइंट एक ही request में सिर्फ़ ज़रूरी डेटा माँग लेता है, और नई स्क्रीन के लिए नया endpoint नहीं बनाना पड़ता।

---

## 🟢 How it Works — Step by Step

### Schema (contract) → Query → Resolvers → Response

```
         Client (React / React Native)
              │  POST /graphql
              │  { query: "query { order(id: 9) { id status restaurant { name } items { name qty } } }" }
              ▼
 ┌─────────────────────────────────────────────┐
 │ GraphQL Server (Apollo / Yoga / Strawberry) │
 │  1. Parse query                             │
 │  2. Validate against SCHEMA (types)         │
 │  3. Execute: call a RESOLVER per field      │
 │       order        → SELECT FROM orders     │
 │       restaurant   → RestaurantService      │
 │       items        → SELECT FROM order_items│
 │  4. Shape result exactly like the query     │
 └─────────────────────────────────────────────┘
              │
              ▼
 { "data": { "order": { "id": 9, "status": "OUT_FOR_DELIVERY",
             "restaurant": { "name": "Behrouz" },
             "items": [{ "name": "Biryani", "qty": 2 }] } } }
```

### Schema (SDL)

```graphql
type User       { id: ID!  name: String!  orders(first: Int, after: String): OrderConnection! }
type Restaurant { id: ID!  name: String!  rating: Float }
type Order      { id: ID!  status: OrderStatus!  total: Int!  restaurant: Restaurant!  items: [OrderItem!]! }
type OrderItem  { name: String!  qty: Int! }
enum OrderStatus { PLACED PREPARING OUT_FOR_DELIVERY DELIVERED CANCELLED }

type Query {
  me: User
  order(id: ID!): Order
  restaurants(near: GeoInput!, first: Int = 20, after: String): RestaurantConnection!
}
type Mutation {
  placeOrder(input: PlaceOrderInput!): Order!
  cancelOrder(id: ID!): Order!
}
type Subscription {
  orderStatusChanged(orderId: ID!): Order!     # real-time over WebSocket
}
```

### 3 operation types

```
Query         → read          (like GET)
Mutation      → write         (like POST/PATCH/DELETE)
Subscription  → live updates  (over WebSocket — order tracking)
```

### The N+1 problem (most asked GraphQL issue)

```
query { orders(first: 50) { id restaurant { name } } }

Naive resolvers:
  1 query  → SELECT * FROM orders LIMIT 50
  50 queries → SELECT * FROM restaurants WHERE id = ?   (one per order!)   = 51 queries ❌

Fix: DataLoader (batch + cache per request)
  1 query → orders
  1 query → SELECT * FROM restaurants WHERE id IN (3, 7, 9, ...)          = 2 queries ✅
```

### REST vs GraphQL

```
┌──────────────────────┬────────────────────────────┬────────────────────────────┐
│                      │ REST                       │ GraphQL                    │
├──────────────────────┼────────────────────────────┼────────────────────────────┤
│ Endpoints            │ Many (/users, /orders)     │ One (/graphql)             │
│ Data shape           │ Server decides             │ Client decides             │
│ Over/under-fetching  │ Common                     │ Solved                     │
│ Typing / docs        │ Optional (OpenAPI)         │ Built-in schema, introspect│
│ HTTP caching / CDN   │ Easy (GET + URL)           │ Hard (POST, one URL) →     │
│                      │                            │ persisted queries, client  │
│                      │                            │ cache (Apollo/urql)        │
│ Error handling       │ HTTP status codes          │ Usually 200 + "errors" []  │
│ File upload          │ Simple (multipart)         │ Awkward (use signed S3 URL)│
│ Rate limiting        │ Per endpoint               │ Needs query cost analysis  │
│ Versioning           │ /v1, /v2                   │ Evolve schema, @deprecated │
│ Best for             │ Public APIs, simple CRUD,  │ Complex UIs, many clients  │
│                      │ webhooks, file/CDN heavy   │ (web+iOS+Android), BFF     │
└──────────────────────┴────────────────────────────┴────────────────────────────┘
```

### Security concerns

```
- Deeply nested / huge queries (DoS):  user { friends { friends { friends ... } } }
  → depth limit, query complexity/cost limit, pagination max (first ≤ 100), timeouts
- Introspection in prod reveals full schema → disable for public or allow-list
- Persisted queries: client sends a HASH of a pre-registered query → server only runs known queries
  (also makes GET + CDN caching possible)
- Authorization per field/resolver, not just per endpoint
```

## 🟢 कैसे काम करता है? (Hindi)
1. सर्वर पर एक schema बनता है — कौन-से types हैं (User, Order) और कौन-से fields।
2. क्लाइंट एक query भेजता है जिसमें लिखा होता है कि ठीक कौन-से fields चाहिए।
3. सर्वर हर field के लिए एक "resolver" function चलाता है जो DB या किसी service से डेटा लाता है।
4. जवाब ठीक query के आकार में वापस आता है।
5. ध्यान रखो: N+1 problem (DataLoader से हल), और बहुत गहरी query पर limit लगाओ।

---

## 🟡 Real World Example

**Facebook / Instagram** — built GraphQL for the mobile news feed; the whole app is powered by it today, with **persisted queries** for performance and security.

**GitHub API v4** — public GraphQL API. One query fetches a repo + last 10 PRs + their reviewers + CI status, which takes 20+ REST calls in v3.

**Shopify Storefront API** — GraphQL so thousands of different storefront designs can fetch exactly the product data they need.

**Swiggy / Airbnb / Netflix (internal)** — GraphQL used as a **BFF / federation layer**: one graph over many microservices. Netflix uses **GraphQL Federation**, where each team owns part of the schema.

## 🟡 Real Example Hindi में
Facebook ने GraphQL अपनी मोबाइल न्यूज़ फ़ीड के लिए बनाया था — एक स्क्रीन का पूरा डेटा एक request में।
GitHub का v4 API GraphQL है — जो काम REST में 20 कॉल से होता है, वो एक query में हो जाता है। Netflix में हर टीम schema का एक हिस्सा संभालती है (Federation)।

---

## 🟠 My Stack Example

### Node.js — Apollo Server + DataLoader
```js
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import DataLoader from 'dataloader';
import depthLimit from 'graphql-depth-limit';

const typeDefs = `#graphql
  type Restaurant { id: ID! name: String! }
  type Order { id: ID! status: String! restaurant: Restaurant! }
  type Query { myOrders(first: Int = 20): [Order!]! }
  type Mutation { cancelOrder(id: ID!): Order! }
`;

const resolvers = {
  Query: {
    myOrders: (_, { first }, ctx) =>
      ctx.db.query('SELECT * FROM orders WHERE user_id=$1 ORDER BY id DESC LIMIT $2',
                   [ctx.user.id, Math.min(first, 100)]).then(r => r.rows),
  },
  Order: {
    restaurant: (order, _, ctx) => ctx.loaders.restaurant.load(order.restaurant_id), // batched ✅
  },
  Mutation: {
    cancelOrder: async (_, { id }, ctx) => {
      if (!ctx.user) throw new GraphQLError('Unauthenticated', { extensions: { code: 'UNAUTHENTICATED' } });
      return orderService.cancel(id, ctx.user.id);
    },
  },
};

const server = new ApolloServer({ typeDefs, resolvers, validationRules: [depthLimit(6)] });
await server.start();

app.use('/graphql', express.json(), expressMiddleware(server, {
  context: async ({ req }) => ({
    user: await verifyJwt(req.headers.authorization),
    db: pool,
    // NEW DataLoader per request (cache must not leak between users)
    loaders: {
      restaurant: new DataLoader(async (ids) => {
        const { rows } = await pool.query('SELECT * FROM restaurants WHERE id = ANY($1)', [ids]);
        const map = new Map(rows.map(r => [String(r.id), r]));
        return ids.map(id => map.get(String(id)));     // same order as ids
      }),
    },
  }),
}));
```

### FastAPI — Strawberry GraphQL
```python
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Order:
    id: strawberry.ID
    status: str

@strawberry.type
class Query:
    @strawberry.field
    async def my_orders(self, info, first: int = 20) -> list[Order]:
        user = info.context["user"]
        return await repo.orders_for(user.id, limit=min(first, 100))

schema = strawberry.Schema(query=Query)
app.include_router(GraphQLRouter(schema, context_getter=get_context), prefix="/graphql")
```

### React Native / Next.js client — Apollo Client
```tsx
const MY_ORDERS = gql`
  query MyOrders { myOrders(first: 10) { id status restaurant { name } } }
`;
function OrdersScreen() {
  const { data, loading, error } = useQuery(MY_ORDERS);   // normalized cache by id
  if (loading) return <Spinner />;
  return <FlatList data={data.myOrders} renderItem={({ item }) =>
    <Text>{item.restaurant.name} — {item.status}</Text>} />;
}
```
- Mobile screen gets **only** `id, status, restaurant.name` → small payload.
- Generate TypeScript types from the schema with **GraphQL Codegen** → shared types web + mobile.

### When to choose in YOUR projects
```
Simple CRUD admin, public API, webhooks, file upload heavy → REST
Web + iOS + Android with different screens, many microservices → GraphQL (as BFF)
Internal service-to-service → gRPC (Topic 95)
Next.js full-stack only → Server Actions / tRPC may be simpler than either
```

---

## ⚫ Interview Questions + Answers

**Q1: What problems does GraphQL solve compared to REST?**
A1: Over-fetching (REST returns fixed, often large payloads), under-fetching (one screen needs many REST calls) and endpoint sprawl (new endpoints for each client need). GraphQL lets clients request exactly the fields and nested relations they need in one round trip, against a strongly typed, self-documenting schema. The schema evolves with deprecations instead of versions.

**Q2: What is the N+1 problem in GraphQL, and how do you solve it?**
A2: When resolving a list, each item's nested field triggers its own DB call: 1 query for N orders plus N queries for their restaurants. The fix is DataLoader, which collects all keys requested in one tick of the event loop, runs a single batched query (`WHERE id IN (...)`) and caches results for the lifetime of the request. Alternatives are SQL joins/look-ahead in resolvers, or tools like Hasura/PostGraphile that compile queries to SQL.

**Q3: Why is caching harder in GraphQL, and how do you handle it?**
A3: Everything is POST to one URL with varying bodies, so HTTP/CDN caching keyed by URL doesn't work naturally. Solutions: client-side normalized caches (Apollo, urql, Relay) keyed by `__typename:id`; persisted queries sent as GET with a hash, which become CDN-cacheable; server-side response caching per query plus variables; and DataLoader/Redis caching at the resolver level. Cache-control hints per field (Apollo) help too.

**Q4: How do you secure a public GraphQL API?**
A4: Authenticate in the context, and authorize at the resolver/field level. Limit query depth and complexity, cap pagination sizes, and set timeouts. Rate-limit by query cost, not request count. Disable introspection or use persisted query allow-lists in production. Mask internal errors. Protect against batching attacks (many operations in one request).

**Q5: When would you NOT use GraphQL?**
A5: For simple CRUD services or a single client; public APIs where HTTP caching and simplicity matter; file upload/download-heavy services; and internal service-to-service calls, where gRPC is better. Also when the team lacks GraphQL experience: it adds complexity (schema design, N+1, cost analysis, monitoring per resolver). It shines as a BFF aggregating many microservices for multiple, rich UIs.

---

## 🔷 Trade-offs
✅ Advantages:
- Exact data, one round trip → great for mobile & complex screens.
- Strong typing + introspection → auto docs, codegen, fewer frontend/backend mismatches.
- Evolve schema without versions; one graph over many services (federation).
- Subscriptions for real-time.

❌ Disadvantages:
- HTTP caching harder; error handling non-standard (200 with errors).
- N+1 performance traps; expensive queries can DoS the server.
- More complex server, monitoring (need per-resolver tracing), and authorization.
- Overkill for simple APIs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Typed definition of all data & operations | डेटा का पूरा नक्शा |
| Query | Read operation | डेटा पढ़ना |
| Mutation | Write operation | डेटा बदलना |
| Subscription | Real-time updates | लाइव अपडेट |
| Resolver | Function that fetches a field's data | field का डेटा लाने वाला function |
| N+1 Problem | One query + N extra queries for nested data | हर item के लिए अलग query |
| DataLoader | Batching + per-request caching tool | कई query को एक में जोड़ना |
| Persisted Query | Pre-registered query sent by hash | पहले से सेव query |
| Federation | Combining many service schemas into one graph | कई service का एक graph |

---

## ⚡ 3-Line Summary
**English:**
1. GraphQL = one endpoint + typed schema; client asks for exact fields → no over/under-fetching.
2. Watch out for N+1 (use DataLoader), caching (client cache, persisted queries) and expensive queries (depth/cost limits).
3. Best as a BFF for rich web + mobile UIs; REST still better for simple/public/file APIs.

**Hindi:**
1. GraphQL = एक endpoint + schema; क्लाइंट ठीक वही fields माँगता है जो चाहिए।
2. N+1 (DataLoader), caching और भारी query का ध्यान रखो।
3. कई UI (web + mobile) के लिए बढ़िया; साधारण API के लिए REST काफ़ी है।

---

## ➡️ Next Topic Suggestion
**08. WebSockets** — Both REST and GraphQL queries are request-response: the client must ask. Next: how WebSockets keep a connection open so the server can **push** data instantly (chat, live order tracking, stock prices).
