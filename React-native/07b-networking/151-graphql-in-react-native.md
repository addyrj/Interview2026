# 151. GraphQL in React Native
# हिंदी में: React Native में GraphQL — ज़रूरत जितना ही data माँगना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76, `@apollo/client` 3.x (`npm i @apollo/client graphql`)। Apollo Client pure JS है, native setup नहीं। Apollo 4 आने पर import/setup बदल सकते हैं — docs देखो। (Alternatives: urql, TanStack Query + `graphql-request`।)

---

## 🔵 Simple Definition (English)
**GraphQL** is a query language for APIs. The app sends one request describing exactly which fields it wants, and the server returns exactly those fields — no more, no less. It uses a single endpoint (usually `POST /graphql`).

## 🔵 सरल परिभाषा (Hindi)
**GraphQL** API के लिए query language है। App एक request में बताती है कि उसे कौन से fields चाहिए, और server ठीक वही fields लौटाता है — न ज़्यादा, न कम। इसमें आमतौर पर एक ही endpoint (`POST /graphql`) होता है।

---

## 🔴 Problem it Solves
```
REST में:
  OVER-FETCHING : /users/1 पूरा object (30 fields) जबकि सिर्फ़ name चाहिए
  UNDER-FETCHING: Home screen के लिए 4 अलग endpoints (user, orders, offers, cart)
  Mobile पर: ज़्यादा data = धीमा + महँगा

GraphQL: एक query, सिर्फ़ ज़रूरी fields, एक round trip।
```

## 🔴 यह क्यों बना? (Hindi)
```
Facebook ने mobile के लिए बनाया — कमज़ोर network पर कम data।
Client तय करता है क्या चाहिए।
एक request में कई resources।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Schema (server): types + Query + Mutation + Subscription
Step 2 → App में query लिखो (gql टैग)
Step 3 → Apollo Client query भेजता है: POST /graphql { query, variables }
Step 4 → Server सिर्फ़ माँगे fields लौटाता है: { data, errors }
Step 5 → Apollo response normalize करके cache में रखता है (id + __typename)
Step 6 → useQuery हर cache बदलाव पर UI re-render; useMutation से डेटा बदलना
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Server schema बताता है क्या-क्या माँगा जा सकता है।
2. App सिर्फ़ ज़रूरी fields की query लिखती है।
3. Apollo भेजता है और जवाब cache में रखता है।
4. useQuery से data/loading/error मिलते हैं।
5. Mutation से बदलाव और cache update।
```

---

## 🟡 Real World Example
**Zomato-जैसा restaurant list:** list screen को सिर्फ़ `name, rating, image` चाहिए; detail screen को `menu, reviews, address`। GraphQL में दोनों अलग query, एक endpoint। **Shopify, GitHub, Airbnb** GraphQL APIs देते हैं। नोट: बहुत से Indian apps अब भी REST/BFF पर हैं — GraphQL हमेशा बेहतर नहीं।

## 🟡 Real Example Hindi mein
Restaurant list screen सिर्फ़ `name, rating, image` माँगती है; detail screen `menu, reviews, address` माँगती है। REST में दोनों के लिए अलग endpoints या बड़ा response; GraphQL में हर screen अपनी जरूरत की query करती है।

---

## 💻 Code Example — Basic

```jsx
// App.jsx — Apollo Client setup + useQuery (public Countries API)
import React from 'react';                                        // React
import { View, Text, FlatList, ActivityIndicator } from 'react-native'; // UI
import { ApolloClient, InMemoryCache, ApolloProvider, gql, useQuery } from '@apollo/client'; // Apollo

const client = new ApolloClient({
  uri: 'https://countries.trevorblades.com/graphql',              // public demo endpoint
  cache: new InMemoryCache(),                                     // normalized cache
});

const COUNTRIES = gql`
  query Countries {
    countries { code name emoji }      # सिर्फ़ ये 3 fields
  }
`;

function Countries() {
  const { data, loading, error, refetch } = useQuery(COUNTRIES);  // query चलाओ

  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} />; // loading
  if (error) return <Text onPress={() => refetch()}>Error: {error.message} (tap to retry)</Text>; // error
  return (
    <FlatList
      data={data.countries.slice(0, 30)}                          // पहले 30
      keyExtractor={(c) => c.code}                                // key
      renderItem={({ item }) => <Text style={{ padding: 10 }}>{item.emoji} {item.name}</Text>} // row
    />
  );
}

export default function App() {
  return (
    <ApolloProvider client={client}>                              {/* client सब में उपलब्ध */}
      <View style={{ flex: 1, paddingTop: 50 }}><Countries /></View>
    </ApolloProvider>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// apollo.js — auth link + error link + mutation with optimistic UI
import { ApolloClient, InMemoryCache, HttpLink, ApolloLink, gql, useMutation } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';         // auth header
import { onError } from '@apollo/client/link/error';              // global errors

const httpLink = new HttpLink({ uri: 'https://api.example.com/graphql' }); // endpoint

const authLink = setContext(async (_, { headers }) => {           // हर request से पहले
  const token = await getToken();                                 // अपना function (SecureStore)
  return { headers: { ...headers, authorization: token ? `Bearer ${token}` : '' } };
});

const errorLink = onError(({ graphQLErrors, networkError }) => {  // errors एक जगह
  if (graphQLErrors) graphQLErrors.forEach((e) => {
    if (e.extensions?.code === 'UNAUTHENTICATED') logout();       // server code के अनुसार
  });
  if (networkError) console.warn('Network error', networkError.message); // offline आदि
});

export const client = new ApolloClient({
  link: ApolloLink.from([errorLink, authLink, httpLink]),         // क्रम महत्वपूर्ण
  cache: new InMemoryCache(),
  defaultOptions: { watchQuery: { fetchPolicy: 'cache-and-network' } }, // cache दिखाओ + fresh लाओ
});

const LIKE = gql`
  mutation Like($id: ID!) { likeDish(id: $id) { id liked likes } }
`;

export function useLike() {
  const [like, state] = useMutation(LIKE);                        // mutation hook
  return {
    ...state,
    like: (dish) => like({
      variables: { id: dish.id },                                 // arguments
      optimisticResponse: {                                       // तुरंत UI में दिखाओ
        likeDish: { __typename: 'Dish', id: dish.id, liked: true, likes: dish.likes + 1 },
      },
    }),
  };
}
// नोट: getToken/logout आपके अपने helpers हैं। Query error का मतलब HTTP 200 में भी हो सकता है (errors array)!
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Apollo Client | Same (JS) | Same (JS) |
| Cleartext local server | `10.0.2.2` + cleartext allow | `localhost` + ATS exception |
| Persisted cache | AsyncStorage (apollo3-cache-persist) | वही |
| Subscriptions | WebSocket (`graphql-ws`) | वही |
| Native alternative | Apollo Kotlin (RN में अप्रासंगिक) | Apollo iOS (अप्रासंगिक) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @apollo/client graphql
// (कुछ SDK/Metro versions में `.cjs` resolution के लिए metro.config.js में
//  config.resolver.sourceExts.push('cjs') चाहिए — error आए तो docs देखें)
```
CLI way:
```jsx
// npm i @apollo/client graphql
// Metro में वही .cjs note; native setup कुछ नहीं
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: सोचना कि error पर HTTP status 4xx/5xx आएगा।
✅ Correct: GraphQL अक्सर HTTP 200 के साथ `errors` array देता है — `error.graphQLErrors` जाँचो।

❌ Mistake 2: `id` और `__typename` query में न माँगना → cache normalize नहीं होता।
✅ Correct: Objects में `id` शामिल करो।

❌ Mistake 3: हर बार `fetchPolicy: 'network-only'`।
✅ Correct: Cache का फायदा उठाओ (`cache-first`/`cache-and-network`)।

❌ Mistake 4: Mutation के बाद list stale।
✅ Correct: `refetchQueries` या cache update।

---

## 🧠 Tricky Interview Question
GraphQL server ने `{ "data": { "user": null }, "errors": [{ "message": "Not found" }] }` HTTP 200 में भेजा। Apollo में `useQuery` क्या देगा?

Answer: Default `errorPolicy: 'none'` में `error` set होगा (graphQLErrors में message) और `data` undefined; `errorPolicy: 'all'` में `data` और `error` दोनों मिलेंगे। HTTP 200 का मतलब सफल नहीं — `errors` हमेशा जाँचो।

---

## ⚫ Interview Questions + Answers
Q1: GraphQL vs REST?
A1: GraphQL में client fields चुनता है, एक endpoint, strongly typed schema; REST में fixed endpoints/responses।

Q2: Query, Mutation, Subscription?
A2: Query पढ़ना, Mutation बदलना, Subscription real-time (WebSocket)।

Q3: Apollo cache कैसे काम करता है?
A3: `__typename + id` से objects normalize करके store; एक जगह बदलाव सब queries में दिखता है।

Q4: N+1 problem?
A4: Server-side resolver समस्या; DataLoader से batching।

Q5: GraphQL के नुकसान?
A5: Caching (HTTP cache मुश्किल), complexity, query-cost attacks, बड़ा client bundle।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- कई screens को अलग-अलग shape का data चाहिए
- Over/under-fetching समस्या है

❌ Avoid when:
- छोटा app, सरल CRUD (REST काफी)
- Team को GraphQL server का अनुभव नहीं

---

## 📊 Visual Diagram
```
 REST:    Home ─► /user ─► /orders ─► /offers ─► /cart   (4 round trips, extra fields)
 GraphQL: Home ─► POST /graphql { user{name} orders{id} offers{title} cart{count} }
                 ◄─ { data: {...exactly these...} }   (1 round trip)
 Apollo cache: normalized by __typename:id
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Types the API offers | API के types का ढाँचा |
| Query | Read operation | पढ़ने का operation |
| Mutation | Write operation | बदलाव का operation |
| Resolver | Server function per field | Field का server function |
| Normalized cache | Store by id | id के आधार पर cache |

---

## ⚡ 3-Line Summary
English: GraphQL lets the client ask for exactly the fields it needs from one endpoint.
Apollo Client adds caching, hooks and links for auth and errors.
Always check the `errors` array, even on HTTP 200.

Hindi: GraphQL में client एक endpoint से सिर्फ़ ज़रूरी fields माँगता है।
Apollo Client caching, hooks और auth/error links देता है।
HTTP 200 पर भी `errors` array जाँचो।

---

## ➡️ Next Topic
**152. File Upload (Images/Videos)** — gallery/camera से file चुनकर server पर भेजना।
