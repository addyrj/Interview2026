# 163. React Native Basics
# हिंदी में: React Native Basics — React से असली Mobile Apps बनाना

---

## 🔵 Simple Definition (English)
**React Native** is a framework that lets you build real iOS and Android apps using React and JavaScript. Your components render to native UI widgets (not HTML), so the app feels like a normal mobile app.

## 🔵 सरल परिभाषा (Hindi)
**React Native** एक framework है जिससे आप React और JavaScript से असली iOS और Android apps बना सकते हैं। आपके components HTML की जगह native UI widgets में बदलते हैं, इसलिए app सामान्य mobile app जैसा महसूस होता है।

---

## 🔴 Problem it Solves

Before React Native, a company like Swiggy needed two separate teams: one wrote Swift/Objective-C for iOS and another wrote Kotlin/Java for Android. Features were built twice, bugs were fixed twice and the two apps drifted apart. Hybrid "WebView" apps (Cordova, Ionic) shared code but felt slow because they were a web page inside a shell. React Native gives one JavaScript codebase that still produces native views, so you share most of the logic and keep native performance and look.

## 🔴 यह क्यों बना? (Hindi)
React Native से पहले Swiggy जैसी company को दो अलग teams चाहिए थीं: एक iOS के लिए Swift/Objective-C और दूसरी Android के लिए Kotlin/Java। Features दो बार बनते, bugs दो बार ठीक होते और दोनों apps अलग-अलग हो जाते। Hybrid "WebView" apps (Cordova, Ionic) code share करते थे पर धीमे लगते थे क्योंकि वे shell के अंदर web page थे। React Native एक JavaScript codebase देता है जो फिर भी native views बनाता है, इसलिए ज़्यादातर logic share होता है और native speed व look बनी रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write components with React (hooks, state, props) in JavaScript/TypeScript
Step 2 → You use RN primitives: <View>, <Text>, <Image>, <ScrollView>, <FlatList>
Step 3 → JS runs in a JavaScript engine inside the app (Hermes by default)
Step 4 → React reconciles your tree and produces a "shadow tree" of native view descriptions
Step 5 → The renderer creates real native views: UIView on iOS, android.view.View on Android
Step 6 → Events (touch, scroll) travel from native to JS; state updates travel back as view updates
Step 7 → New Architecture (JSI, Fabric, TurboModules) lets JS and native talk directly, without the old async JSON bridge

NOTE: New Architecture is the default in recent React Native versions (version-dependent: check your RN release notes)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप React (hooks, state, props) से JavaScript/TypeScript में components लिखते हो
Step 2 → आप RN primitives इस्तेमाल करते हो: <View>, <Text>, <Image>, <ScrollView>, <FlatList>
Step 3 → JS app के अंदर JavaScript engine (default में Hermes) में चलता है
Step 4 → React आपका tree reconcile करके native views का "shadow tree" बनाता है
Step 5 → Renderer असली native views बनाता है: iOS पर UIView, Android पर android.view.View
Step 6 → Events (touch, scroll) native से JS जाते हैं; state updates वापस view updates बनकर आते हैं
Step 7 → New Architecture (JSI, Fabric, TurboModules) में JS और native सीधे बात करते हैं, पुराने async JSON bridge के बिना

NOTE: हाल के React Native versions में New Architecture default है (version-dependent: अपने RN release notes देखो)
```

---

## 🟡 Real World Example
**Swiggy-style order list on mobile:** The home screen shows a scrolling list of restaurants. In React Native this is a `FlatList` of `<RestaurantRow>` components. Each row has an `<Image>`, a `<Text>` for the name and a `<Pressable>` to open the menu. The same business logic (fetching restaurants, cart state with Redux Toolkit or Zustand) can be shared with the web app. Companies like Flipkart and Shopify have shipped React Native screens inside production apps.

## 🟡 Real Example Hindi mein
**Swiggy जैसी order list mobile पर:** Home screen पर restaurants की scroll होने वाली list दिखती है। React Native में यह `<RestaurantRow>` components की `FlatList` है। हर row में `<Image>`, नाम के लिए `<Text>` और menu खोलने के लिए `<Pressable>` होता है। वही business logic (restaurants fetch करना, Redux Toolkit या Zustand से cart state) web app के साथ share हो सकता है। Flipkart और Shopify जैसी companies ने production apps में React Native screens चलाई हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic React Native screen: a counter with native components
// Run with Expo: npx create-expo-app@latest, then replace app/index.js (or App.js)
import React, { useState } from 'react';                       // React hook for state
import { View, Text, Pressable, StyleSheet } from 'react-native'; // native building blocks

export default function App() {
  const [count, setCount] = useState(0);                        // cart item count (state works like web React)

  return (
    <View style={styles.container}>                              {/* View is like a <div> but a native view */}
      <Text style={styles.title}>Cart items: {count}</Text>      {/* ALL text must be inside <Text> */}
      <Pressable
        style={styles.button}                                    // style object (no CSS files, no cascade)
        onPress={() => setCount(count + 1)}                      // onPress, not onClick
      >
        <Text style={styles.buttonText}>Add item</Text>          {/* label inside the button */}
      </Pressable>
    </View>
  );
}

// StyleSheet.create keeps styles as plain JS objects (flexbox by default, column direction)
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // center everything
  title: { fontSize: 24, marginBottom: 16 },                              // numbers mean density-independent pixels
  button: { backgroundColor: '#fc8019', padding: 12, borderRadius: 8 },   // Swiggy-orange button
  buttonText: { color: '#fff', fontWeight: 'bold' },                      // white bold label
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a searchable, virtualized restaurant list with loading, error and pull-to-refresh
import React, { useState, useEffect, useCallback, useMemo } from 'react'; // React hooks
import {
  View, Text, TextInput, FlatList, ActivityIndicator, RefreshControl,
  Pressable, StyleSheet, Platform,
} from 'react-native';                                                     // native components

// Row is memoized: FlatList re-renders only rows whose props change
const RestaurantRow = React.memo(function RestaurantRow({ item, onPress }) {
  return (
    <Pressable onPress={() => onPress(item.id)} style={styles.row}>       {/* tap target */}
      <Text style={styles.name}>{item.name}</Text>                         {/* restaurant name */}
      <Text style={styles.meta}>{item.cuisine} · {item.eta} min</Text>     {/* cuisine and delivery time */}
    </Pressable>
  );
});

export default function RestaurantList({ fetchRestaurants, onOpen }) {
  const [items, setItems] = useState([]);          // list data
  const [query, setQuery] = useState('');          // search text
  const [loading, setLoading] = useState(true);    // first load spinner
  const [refreshing, setRefreshing] = useState(false); // pull-to-refresh state
  const [error, setError] = useState(null);        // error message

  const load = useCallback(async () => {            // stable loader function
    try {
      setError(null);                                // clear old error
      const data = await fetchRestaurants();         // prop: returns an array of restaurants
      setItems(data);                                // store the result
    } catch (e) {
      setError('Could not load restaurants');        // show a friendly message
    } finally {
      setLoading(false);                             // first load done
      setRefreshing(false);                          // stop the refresh spinner
    }
  }, [fetchRestaurants]);

  useEffect(() => { load(); }, [load]);              // load on mount

  const onRefresh = useCallback(() => {              // pull-to-refresh handler
    setRefreshing(true);                             // show the native refresh control
    load();                                          // reload data
  }, [load]);

  const visible = useMemo(                           // filter only when items or query change
    () => items.filter(r => r.name.toLowerCase().includes(query.toLowerCase())),
    [items, query]
  );

  const renderItem = useCallback(                    // stable renderItem keeps rows memoized
    ({ item }) => <RestaurantRow item={item} onPress={onOpen} />,
    [onOpen]
  );

  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} />; // native spinner
  if (error) return <Text style={styles.error}>{error}</Text>;         // error state

  return (
    <View style={{ flex: 1 }}>
      <TextInput
        placeholder="Search restaurants"             // hint text
        value={query}                                // controlled input
        onChangeText={setQuery}                      // gives the string directly (not an event)
        style={styles.search}
      />
      <FlatList
        data={visible}                               // only visible rows are mounted (virtualized)
        keyExtractor={r => String(r.id)}             // stable key per row
        renderItem={renderItem}                      // how each row looks
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.meta}>No restaurants found</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  search: { padding: 12, margin: 12, borderWidth: 1, borderColor: '#ddd', borderRadius: 8 },
  row: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ccc' },
  name: { fontSize: 16, fontWeight: '600' },
  meta: { color: '#666', marginTop: 4 },
  error: { color: 'crimson', padding: 16 },
  // Platform.select gives different values per OS
  ...Platform.select({ ios: {}, android: {} }),
});
```

---

## 🟠 Next.js Connection

React Native is not Next.js, but they share the React mental model, so teams share code. With **Expo Router** (file-based routing for React Native) the folder structure feels like the Next.js App Router. A common setup is a monorepo: shared hooks, API clients and validation in a `packages/` folder, a Next.js web app and an Expo mobile app on top. UI components are usually not shared directly (`<div>` vs `<View>`), unless you use a layer like `react-native-web` or Solito (version-dependent: check current docs).

```jsx
// Expo Router file layout (similar idea to Next.js app/ folder)
// app/_layout.jsx        → root layout (like app/layout.jsx in Next.js)
// app/index.jsx          → "/" screen
// app/restaurant/[id].jsx → dynamic route, like Next.js [id]
import { Stack } from 'expo-router';                    // navigation container (native stack)
export default function RootLayout() {
  return <Stack />;                                     // renders the current screen with native transitions
}
```

```jsx
// packages/shared/useRestaurants.js: shared between Next.js web and React Native
import { useQuery } from '@tanstack/react-query';       // TanStack Query v5 works on both platforms
export function useRestaurants(api) {
  return useQuery({
    queryKey: ['restaurants'],                          // cache key
    queryFn: () => api.getRestaurants(),                // API client injected by each app
  });
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using web elements and events (`div`, `span`, `onClick`)
✅ **Correct:** Use `View`, `Text`, `Pressable` and `onPress`

```jsx
// Wrong: these web tags do not exist in React Native
<div onClick={handle}><span>Hello</span></div>

// Right: native components
<Pressable onPress={handle}><Text>Hello</Text></Pressable>
```

❌ **Mistake 2:** Rendering plain strings outside `<Text>`
✅ **Correct:** Wrap all text in `<Text>`

```jsx
// Wrong: raw string inside View crashes ("Text strings must be rendered within a <Text> component")
<View>Hello</View>

// Right
<View><Text>Hello</Text></View>
```

❌ **Mistake 3:** Rendering long lists with `ScrollView` and `.map()`
✅ **Correct:** Use `FlatList` (virtualized) for long lists

```jsx
// Wrong: mounts all 5000 rows at once, uses lots of memory
<ScrollView>{items.map(i => <Row key={i.id} item={i} />)}</ScrollView>

// Right: only rows near the screen are mounted
<FlatList data={items} keyExtractor={i => String(i.id)} renderItem={({ item }) => <Row item={item} />} />
```

---

## 🧠 Tricky Interview Question

```jsx
import { View, Text } from 'react-native';

export default function App() {
  const count = 0;
  return (
    <View>
      {count && <Text>You have items</Text>}
    </View>
  );
}
```
**Answer:** On web React this renders a harmless `0` in the DOM. In React Native it **crashes** with "Text strings must be rendered within a `<Text>` component", because `count && ...` evaluates to the number `0`, and React Native tries to render the raw `0` directly inside `<View>`. This behaviour is well known on older RN versions (version-dependent: newer releases may differ, but do not depend on it). Fix: `{count > 0 && <Text>...</Text>}` or a ternary `count ? <Text>..</Text> : null`.

---

## ⚫ Interview Questions + Answers

Q1: What is React Native and how is it different from a WebView hybrid app?
A1: React Native renders real native UI widgets driven by JavaScript, so scrolling, gestures and look match the platform. A WebView app (Cordova, Ionic) is an HTML page inside a native shell, which is usually slower and less native-feeling.

Q2: What is Hermes?
A2: Hermes is a JavaScript engine built for React Native. It precompiles JavaScript to bytecode, which improves startup time and lowers memory use. It is the default engine in recent RN versions.

Q3: What is the old bridge and what replaced it?
A3: The old architecture sent asynchronous, serialized JSON messages between JS and native, which could become a bottleneck. The New Architecture uses JSI (direct synchronous access from JS to native objects), Fabric (new renderer) and TurboModules (lazy native modules).

Q4: What is the difference between Expo and bare React Native?
A4: Expo is a toolchain and set of libraries that makes starting, building and updating RN apps easy (managed builds, OTA updates, many ready modules). Bare React Native gives full control over native projects. Today Expo supports custom native code too, and the React Native docs recommend starting with a framework like Expo.

Q5: How does styling work in React Native?
A5: Styles are JavaScript objects (usually from `StyleSheet.create`), laid out with Flexbox where the default direction is `column`. There is no CSS cascade, no class names and no inheritance except for some text styles inside nested `<Text>`.

---

## 🔷 When to Use + When Not to Use
✅ **Use React Native when:**
- You need iOS and Android apps with one team and shared logic
- Your team already knows React and JavaScript/TypeScript
- The app is mostly screens, lists, forms and network data (e-commerce, food delivery)

❌ **Avoid React Native when:**
- You need heavy 3D, advanced graphics or very platform-specific low-level APIs (consider fully native or a game engine)
- The product is only a website (use Next.js, or a PWA)
- You cannot accept occasional native-module maintenance work on upgrades

---

## 📊 Visual Diagram

```
   Your React code (JS/TS, hooks, state)
              │
              ▼
   ┌──────────────────────┐
   │ Hermes JS engine      │  runs your components
   └──────────┬───────────┘
              │  JSI (New Architecture: direct calls)
              ▼
   ┌──────────────────────┐
   │ Fabric renderer       │  builds shadow tree
   └──────────┬───────────┘
        ┌─────┴──────┐
        ▼            ▼
   iOS UIView    Android View   ← real native widgets

   <View> → UIView / android.view.ViewGroup
   <Text> → UILabel / TextView
   <FlatList> → UIScrollView / RecyclerView-like virtualization
```

Re-render behavior: a state change re-renders the component and its children just like web React; the renderer then applies only the changed native view updates. Performance impact: use `FlatList`, `React.memo` rows and avoid inline heavy work in render.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| React Native | React framework for native mobile apps | Native mobile apps के लिए React framework |
| Expo | Toolchain and libraries for RN | RN के लिए toolchain और libraries |
| Hermes | JS engine optimized for RN | RN के लिए बना JS engine |
| JSI | Direct JS-to-native interface | JS से native का सीधा interface |
| Fabric | New RN renderer | नया RN renderer |
| TurboModule | Lazily loaded native module | ज़रूरत पर load होने वाला native module |
| FlatList | Virtualized list component | Virtualized list component |
| Pressable | Touchable component with press states | Press states वाला touch component |

---

## ⚡ 3-Line Summary
**English:**
1. React Native lets you write React and get real native iOS and Android views.
2. You use `View`, `Text`, `Pressable`, `FlatList` and style objects instead of HTML and CSS.
3. Share logic (hooks, API, state) with web, and use FlatList and memoization for performance.

**Hindi:**
1. React Native से आप React लिखते हो और असली native iOS व Android views मिलते हैं।
2. HTML और CSS की जगह `View`, `Text`, `Pressable`, `FlatList` और style objects इस्तेमाल होते हैं।
3. Logic (hooks, API, state) web के साथ share करो, और performance के लिए FlatList व memoization इस्तेमाल करो।

---

## ➡️ Next Topic
**164. React Native vs React Web** — दोनों में exactly क्या same है और क्या अलग (components, styling, navigation, storage), ताकि interview में तुलना साफ़ बता सको।
