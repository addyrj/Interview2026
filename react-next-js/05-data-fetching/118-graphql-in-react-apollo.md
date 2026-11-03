# 118. GraphQL in React (Apollo)
# हिंदी में: React में GraphQL (Apollo Client) — सिर्फ़ ज़रूरी Data माँगो

---

## 🔵 Simple Definition (English)
**GraphQL** is a query language for APIs where the client asks for exactly the fields it needs from a single endpoint. **Apollo Client** is the most popular React library for it: it sends queries and mutations, caches results in a normalized cache, and gives hooks like `useQuery` and `useMutation`.

## 🔵 सरल परिभाषा (Hindi)
**GraphQL** APIs के लिए एक query language है जिसमें client एक ही endpoint से बिल्कुल वही fields माँगता है जो उसे चाहिए। **Apollo Client** इसके लिए React की सबसे popular library है: यह queries और mutations भेजती है, results को normalized cache में रखती है, और `useQuery`, `useMutation` जैसे hooks देती है।

---

## 🔴 Problem it Solves

With REST, one screen often needs several endpoints (`/restaurant/1`, `/restaurant/1/menu`, `/restaurant/1/reviews`), which causes many round trips (under-fetching). Each endpoint also returns fixed fields, so a mobile screen that needs only a name and rating still downloads the entire object (over-fetching). GraphQL solves both: one request, exactly the fields requested, with a typed schema that frontend and backend share.

```jsx
// PROBLEM (REST): 3 requests + unused fields
fetch('/api/restaurants/1');          // returns 40 fields, UI needs 3
fetch('/api/restaurants/1/menu');     // second round trip
fetch('/api/restaurants/1/reviews');  // third round trip

// SOLUTION (GraphQL): ONE request, only what the UI needs
const QUERY = gql`
  query { restaurant(id: 1) { name rating menu { name price } reviews(first: 3) { text } } }
`;
```

## 🔴 यह क्यों बना? (Hindi)
REST में एक screen के लिए अक्सर कई endpoints चाहिए (`/restaurant/1`, `/restaurant/1/menu`, `/restaurant/1/reviews`), यानी कई round trips (under-fetching)। हर endpoint fixed fields लौटाता है, इसलिए mobile screen को सिर्फ़ नाम और rating चाहिए तब भी पूरा object आता है (over-fetching)। GraphQL दोनों हल करता है: एक request, सिर्फ़ माँगे गए fields, और frontend-backend के बीच साझा typed schema।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Server exposes ONE endpoint (/graphql) with a typed schema (types, queries, mutations)
Step 2 → Client creates ApolloClient({ uri, cache: new InMemoryCache() })
Step 3 → Wrap the app in <ApolloProvider client={client}>
Step 4 → Write a query with gql`...` listing exactly the fields needed
Step 5 → useQuery(QUERY, { variables }) → returns { data, loading, error, refetch, fetchMore }
Step 6 → Apollo normalizes the result into cache entries by __typename + id
Step 7 → useMutation(MUTATION) updates the server; the cache updates automatically for objects with id,
         or you update it manually (cache.modify / refetchQueries)

KEY: ask for `id` and `__typename` so the cache can normalize and update objects everywhere
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Server एक ही endpoint (/graphql) देता है जिसमें typed schema होता है (types, queries, mutations)
Step 2 → Client में ApolloClient({ uri, cache: new InMemoryCache() }) बनता है
Step 3 → App को <ApolloProvider client={client}> में wrap करो
Step 4 → gql`...` से query लिखो जिसमें बिल्कुल ज़रूरी fields हों
Step 5 → useQuery(QUERY, { variables }) → { data, loading, error, refetch, fetchMore } लौटाता है
Step 6 → Apollo result को __typename + id के हिसाब से cache entries में normalize करता है
Step 7 → useMutation(MUTATION) server को update करता है; id वाले objects का cache अपने आप update होता है,
         वरना cache.modify / refetchQueries से हाथ से करो

KEY: `id` और `__typename` माँगो ताकि cache objects को normalize करके हर जगह update कर सके
```

---

## 🟡 Real World Example
**Swiggy restaurant page:** The page shows restaurant name, rating, top 5 dishes and offers. With GraphQL, the app sends one query asking for exactly those fields, and the server returns one JSON. When the user adds a dish to the cart, a mutation returns the updated cart, and Apollo's normalized cache updates the cart badge and the cart page together without a manual refetch. Big companies such as GitHub (public GraphQL API), Shopify and Airbnb use GraphQL for this reason.

## 🟡 Real Example Hindi mein
**Swiggy restaurant page:** Page पर restaurant का नाम, rating, top 5 dishes और offers दिखते हैं। GraphQL में app एक query भेजता है जिसमें सिर्फ़ यही fields माँगे जाते हैं, और server एक ही JSON लौटाता है। User जब dish cart में डालता है तो mutation अपडेटेड cart लौटाता है, और Apollo का normalized cache cart badge और cart page दोनों को बिना manual refetch के update कर देता है। GitHub (public GraphQL API), Shopify और Airbnb जैसी कंपनियाँ इसी वजह से GraphQL इस्तेमाल करती हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: Apollo Client 3.x with a query (npm install @apollo/client graphql)
import { ApolloClient, InMemoryCache, ApolloProvider, gql, useQuery } from '@apollo/client'; // core pieces
import { createRoot } from 'react-dom/client';                  // React 18/19 root API

const client = new ApolloClient({
  uri: 'https://example.com/graphql',                           // your GraphQL endpoint
  cache: new InMemoryCache(),                                   // normalized cache
});

// the query: ask only for the fields the UI needs (id helps the cache)
const GET_RESTAURANTS = gql`
  query GetRestaurants($city: String!) {
    restaurants(city: $city) {
      id
      name
      rating
    }
  }
`;

function Restaurants({ city }) {
  const { data, loading, error } = useQuery(GET_RESTAURANTS, {
    variables: { city },                                        // sent as GraphQL variables (never string-concat!)
  });

  if (loading) return <p>Loading...</p>;                        // request in flight
  if (error) return <p>Error: {error.message}</p>;              // network or GraphQL error
  return (
    <ul>
      {data.restaurants.map(r => (                              // data has the same shape as the query
        <li key={r.id}>{r.name} ({r.rating})</li>
      ))}
    </ul>
  );
}

createRoot(document.getElementById('root')).render(
  <ApolloProvider client={client}>                              {/* gives hooks access to the client */}
    <Restaurants city="Bengaluru" />
  </ApolloProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: mutation with cache update, pagination with fetchMore, auth link and error handling
import {
  ApolloClient, InMemoryCache, ApolloProvider, ApolloLink, HttpLink,
  gql, useQuery, useMutation,
} from '@apollo/client';
import { setContext } from '@apollo/client/link/context';        // add headers (like a token)
import { onError } from '@apollo/client/link/error';             // global error handling

const httpLink = new HttpLink({ uri: '/graphql' });              // the transport

const authLink = setContext((_, { headers }) => ({
  headers: { ...headers, authorization: localStorage.getItem('token') ?? '' }, // attach token to every request
}));

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) graphQLErrors.forEach(e => console.error('[GraphQL]', e.message)); // server-side errors
  if (networkError) console.error('[Network]', networkError.message);                    // offline etc.
});

const client = new ApolloClient({
  link: ApolloLink.from([errorLink, authLink, httpLink]),         // chain: error → auth → HTTP
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          orders: {
            keyArgs: false,                                       // one list regardless of offset
            merge(existing = [], incoming) { return [...existing, ...incoming]; }, // append pages
          },
        },
      },
    },
  }),
});

const GET_ORDERS = gql`
  query Orders($offset: Int!, $limit: Int!) {
    orders(offset: $offset, limit: $limit) { id item status }
  }
`;
const CANCEL_ORDER = gql`
  mutation Cancel($id: ID!) { cancelOrder(id: $id) { id status } }
`;

function Orders() {
  const { data, loading, error, fetchMore } = useQuery(GET_ORDERS, {
    variables: { offset: 0, limit: 10 },                          // first page
    notifyOnNetworkStatusChange: true,                            // loading=true also during fetchMore
  });

  const [cancel, { loading: cancelling }] = useMutation(CANCEL_ORDER, {
    // optimistic UI: pretend it worked until the server answers
    optimisticResponse: vars => ({
      cancelOrder: { __typename: 'Order', id: vars.id, status: 'CANCELLED' },
    }),
    // result has id + __typename, so Apollo updates that Order in the cache automatically
  });

  if (error) return <p role="alert">{error.message}</p>;
  if (!data) return <p>Loading...</p>;                            // first load only

  return (
    <div>
      <ul>
        {data.orders.map(o => (
          <li key={o.id}>
            {o.item} — {o.status}
            <button disabled={cancelling || o.status === 'CANCELLED'}
                    onClick={() => cancel({ variables: { id: o.id } })}>Cancel</button>
          </li>
        ))}
      </ul>
      <button
        disabled={loading}
        onClick={() => fetchMore({ variables: { offset: data.orders.length } })} // next page; merge() appends
      >
        {loading ? 'Loading...' : 'Load more'}
      </button>
    </div>
  );
}

export default function App() {
  return <ApolloProvider client={client}><Orders /></ApolloProvider>;
}
```

---

## 🟠 Next.js Connection

In the App Router, Server Components can call a GraphQL endpoint with plain `fetch` (no Apollo needed), which is simplest for static or SEO-heavy data. For client-side interactivity you can use Apollo's hooks in Client Components. Apollo provides the package `@apollo/client-integration-nextjs` (earlier `@apollo/experimental-nextjs-app-support`) with `registerApolloClient` and streaming SSR support; the exact API is version-dependent, so check the current Apollo docs.

```jsx
// app/restaurants/page.jsx (Server Component): GraphQL with plain fetch, zero client JS
export default async function Page() {
  const res = await fetch('https://example.com/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: `query($city: String!) { restaurants(city: $city) { id name rating } }`, // the query text
      variables: { city: 'Bengaluru' },                                // variables kept separate
    }),
    next: { revalidate: 60 },                                          // cache for 60 seconds (ISR style)
  });
  const { data, errors } = await res.json();                           // GraphQL returns 200 even with errors
  if (errors) throw new Error(errors[0].message);                      // surface them to error.jsx
  return <ul>{data.restaurants.map(r => <li key={r.id}>{r.name}</li>)}</ul>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not requesting `id` (and `__typename`) so the cache cannot normalize and stays stale
✅ **Correct:** Always include `id` on objects that can change

```jsx
// Wrong: Apollo cannot tell which Order this is, so the mutation does not update the list
gql`query { orders { item status } }`;
// Right: id lets InMemoryCache merge updates by Order:123
gql`query { orders { id item status } }`;
```

❌ **Mistake 2:** Building the query string with user input (injection and cache misses)
✅ **Correct:** Use variables

```jsx
// Wrong: string concatenation
gql(`query { user(name: "${name}") { id } }`);                      // ❌ new document each time
// Right: static query + variables
const Q = gql`query($name: String!) { user(name: $name) { id } }`;
useQuery(Q, { variables: { name } });                               // ✅
```

❌ **Mistake 3:** Treating GraphQL errors like HTTP errors (GraphQL often returns status 200 with an `errors` array and partial `data`)
✅ **Correct:** Check `error`/`errors`, and set `errorPolicy` if you want partial data

```jsx
// Wrong: only checking data
if (data) render(data);                                             // ❌ may be partial, errors ignored
// Right
const { data, error } = useQuery(Q, { errorPolicy: 'all' });        // ✅ get data AND errors
if (error) showToast(error.message);
```

---

## 🧠 Tricky Interview Question

```jsx
const GET_USER = gql`query { user(id: 1) { id name } }`;
const UPDATE_NAME = gql`mutation { updateName(id: 1, name: "Asha") { id name } }`;

function Profile() {
  const { data } = useQuery(GET_USER);
  const [update] = useMutation(UPDATE_NAME);
  return <button onClick={() => update()}>{data?.user.name}</button>;
}
// After the mutation succeeds, does the button text change? Do we need refetch?
```
**Answer:** Yes, it changes and no refetch is needed. The mutation returns an object with `__typename: "User"` and `id: 1`, so Apollo's normalized cache stores it under `User:1` and overwrites the `name` field. `GET_USER` also reads `User:1`, so `useQuery` re-renders with the new name. It would NOT update if the mutation did not return `id` and the changed fields, or if the mutation changes a list (adding or deleting an item), since list membership is not known by the cache: then you need `refetchQueries` or `cache.modify`/`update`. This normalization is what makes Apollo different from REST + React Query, which updates by query key.

---

## ⚫ Interview Questions + Answers

Q1: What are over-fetching and under-fetching, and how does GraphQL fix them?
A1: Over-fetching is getting more fields than needed; under-fetching is needing several requests to get enough data. In GraphQL the client lists the exact fields (including nested relations) in one query, so the server returns exactly that shape.

Q2: What is Apollo's normalized cache?
A2: `InMemoryCache` splits query results into objects, stores each by an identifier such as `User:1` (`__typename:id`), and keeps references between them. When any query or mutation returns that object, every query reading it updates automatically. `keyFields` and `typePolicies` customize identity and merging.

Q3: Query vs mutation vs subscription?
A3: A query reads data, a mutation writes data (and returns the changed result), a subscription keeps a connection (usually WebSocket) open and pushes real-time updates. In Apollo: `useQuery`, `useMutation`, `useSubscription`.

Q4: How do you do pagination with Apollo?
A4: Use `fetchMore` with new variables and a `typePolicies` `merge` function (or `relayStylePagination` helper) to combine pages in the cache. Cursor-based pagination is preferred for changing data.

Q5: GraphQL vs REST: any downsides?
A5: GraphQL has HTTP caching difficulty (single POST endpoint), query complexity and N+1 problems on the server (need DataLoader, depth limits), a learning curve, and heavier client libraries. REST is simpler for small, stable APIs.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Many different clients (web, iOS, Android) need different shapes of the same data
- Screens combine data from many resources, and you want one request
- You want a typed schema, codegen and strong tooling (GraphQL Code Generator)

❌ **Avoid when:**
- The API is small and simple, where REST + React Query is easier
- You depend heavily on HTTP/CDN caching of GET requests (possible with persisted queries, but more work)
- The team has no GraphQL backend experience

---

## 📊 Visual Diagram

```
 React component
    │  useQuery(GET_RESTAURANTS, { variables })
    ▼
 ┌──────────────────────┐   cache hit?   ┌───────────────────────┐
 │ Apollo Client        │ ─────yes─────► │ InMemoryCache         │
 │  (links: auth,error) │                │ Restaurant:1 {...}    │
 └─────────┬────────────┘                │ Restaurant:2 {...}    │
           │ no (or refetch)             └───────────▲───────────┘
           ▼                                         │ normalize by __typename:id
   POST /graphql  { query, variables }               │
           │                                         │
           ▼                                         │
   GraphQL server (schema + resolvers) ──── JSON ────┘

 Re-render: components re-render only when the fields they read change in the cache.
 Performance: smaller payloads (no over-fetching), fewer round trips; but watch query depth on the server.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GraphQL | Query language where client picks fields | Client के fields चुनने वाली query language |
| Apollo Client | React library for GraphQL with cache | Cache वाली GraphQL की React library |
| Query | Read operation | Data पढ़ने का operation |
| Mutation | Write operation | Data बदलने का operation |
| Subscription | Real-time push updates | Real-time अपडेट आना |
| Schema | Typed description of the API | API का typed विवरण |
| InMemoryCache | Apollo's normalized cache | Apollo का normalized cache |
| Over-fetching | Receiving unused fields | बेकार fields मिलना |

---

## ⚡ 3-Line Summary
**English:**
1. GraphQL lets the client request exactly the fields it needs from a single endpoint.
2. Apollo Client gives `useQuery`/`useMutation` and a normalized cache that updates objects by `__typename:id`.
3. Always request `id`, use variables, handle partial errors, and in Next.js use plain `fetch` in Server Components when possible.

**Hindi:**
1. GraphQL में client एक ही endpoint से बिल्कुल वही fields माँगता है जो उसे चाहिए।
2. Apollo Client `useQuery`/`useMutation` और normalized cache देती है जो objects को `__typename:id` से update करता है।
3. हमेशा `id` माँगो, variables इस्तेमाल करो, partial errors संभालो, और Next.js में हो सके तो Server Components में सादा `fetch` इस्तेमाल करो।

---

## ➡️ Next Topic
**119. WebSocket in React** — जब data बार-बार server से push होना हो (chat, live prices), तब WebSocket connection कैसे खोलें, साफ़ करें और reconnect करें।
