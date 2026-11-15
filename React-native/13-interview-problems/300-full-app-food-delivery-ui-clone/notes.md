# 300. Full App — Food Delivery UI Clone
# हिंदी में: पूरा App — Food Delivery UI Clone (Swiggy जैसा)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 / React Native 0.76** (check current docs — APIs change between SDKs). Uses React Navigation v6/v7 `native-stack` (`createNativeStackNavigator`), React Context + `useReducer` for the cart.
> Files: [`App.jsx`](./App.jsx) · [`CartContext.jsx`](./CartContext.jsx) · [`data.js`](./data.js) · [`screens/HomeScreen.jsx`](./screens/HomeScreen.jsx) · [`screens/RestaurantScreen.jsx`](./screens/RestaurantScreen.jsx) · [`screens/CartScreen.jsx`](./screens/CartScreen.jsx)
> Install: `npx expo install @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context`

---

## 🔵 Simple Definition (English)
A **food delivery UI clone** is a small full app with three screens: **Home** (search + category chips + restaurant list), **Restaurant** (menu with ADD / + / - buttons) and **Cart** (bill + place order). A shared **cart context** keeps items across screens.

## 🔵 सरल परिभाषा (Hindi)
**Food delivery UI clone** तीन screens वाला छोटा पूरा app है: **Home** (search + category chips + restaurant list), **Restaurant** (ADD / + / - वाला menu) और **Cart** (bill + order दो)। एक साझा **cart context** items को screens के बीच बनाए रखता है।

---

## 🔴 Problem it Solves
```
❌ Interviewer पूछता है "Swiggy जैसा app बनाओ" - बहुत कुछ एक साथ: navigation, state, list, search
❌ Cart state हर screen में अलग -> Home पर count गलत
❌ prop drilling: cart को 3 levels नीचे भेजना
❌ Cart total / delivery fee का calculation UI में बिखरा
```

## 🔴 यह क्यों बना? (Hindi)
```
Machine-coding round में Swiggy / Zomato clone सबसे आम सवाल है। इसमें दिखता है कि आप
architecture सोच सकते हैं: data -> state (reducer) -> screens -> navigation।
Reducer pure function है, इसलिए test करना आसान है; Context से हर screen को cart मिल जाता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → data.js: RESTAURANTS (with menu) + CATEGORIES (dummy now, API later)
Step 2 → CartContext: useReducer with ADD / REMOVE / CLEAR; state = { id: { item, qty } }
Step 3 → Provider exposes derived values: lines, count, total, qtyOf, add, remove, clear
Step 4 → App.jsx: SafeAreaProvider > CartProvider > NavigationContainer > Stack (Home, Restaurant, Cart)
Step 5 → HomeScreen: search + chip state -> useMemo filter -> FlatList -> navigate('Restaurant', { id })
Step 6 → RestaurantScreen: route.params.id -> find restaurant -> ADD / stepper using qtyOf/add/remove
Step 7 → HomeScreen bottom bar shows "N items | Rs X" -> CartScreen: bill + fee -> Place order -> clear + popToTop
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → data.js में RESTAURANTS (menu सहित) और CATEGORIES (अभी dummy, बाद में API)
Step 2 → CartContext: useReducer में ADD / REMOVE / CLEAR; state = { id: { item, qty } }
Step 3 → Provider से derived values मिलते हैं: lines, count, total, qtyOf, add, remove, clear
Step 4 → App.jsx: SafeAreaProvider > CartProvider > NavigationContainer > Stack (तीन screens)
Step 5 → HomeScreen: search + chip state -> useMemo से filter -> FlatList -> navigate('Restaurant', { id })
Step 6 → RestaurantScreen: route.params.id से restaurant ढूँढो -> ADD / stepper
Step 7 → Home की bottom bar "N items | Rs X" दिखाती है -> Cart: bill + fee -> Place order -> clear + popToTop
```

---

## 🟡 Real World Example
**Swiggy** and **Zomato** have exactly this flow: search and cuisine chips on Home, menu with orange ADD button and a quantity stepper, a sticky "View cart" bar, and a bill with delivery fee. **Blinkit / Zepto** use the same cart pattern for groceries.

## 🟡 Real Example Hindi mein
**Swiggy** और **Zomato** में यही flow है: Home पर search और cuisine chips, menu में नारंगी ADD button और quantity stepper, नीचे चिपकी "View cart" bar, और delivery fee वाला bill। **Blinkit / Zepto** grocery में यही cart pattern use करते हैं।

---

## 💻 Code Example — Basic
Cart logic only (a pure reducer; runs anywhere, even in Node):

```jsx
// Basic: cart as a pure reducer
import React, { useReducer } from 'react'; // React + reducer hook
import { View, Text, Button } from 'react-native'; // UI

// state = { itemId: qty }
function reducer(state, action) {
  if (action.type === 'ADD') return { ...state, [action.id]: (state[action.id] ?? 0) + 1 }; // +1
  if (action.type === 'REMOVE') {
    const qty = (state[action.id] ?? 0) - 1; // -1
    const { [action.id]: _x, ...rest } = state; // copy without this id
    return qty > 0 ? { ...rest, [action.id]: qty } : rest; // drop the line at 0
  }
  return state; // unknown action
}

export default function BasicCart() {
  const [cart, dispatch] = useReducer(reducer, {}); // empty cart
  return (
    <View style={{ padding: 40 }}>
      <Text>Biryani qty: {cart.biryani ?? 0}</Text>
      {/* dispatch actions */}
      <Button title="+" onPress={() => dispatch({ type: 'ADD', id: 'biryani' })} />
      <Button title="-" onPress={() => dispatch({ type: 'REMOVE', id: 'biryani' })} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
Full code in the files above. Key parts:

```jsx
// CartContext.jsx (key part) - derived values memoised once per cart change
const [lines, dispatch] = useReducer(cartReducer, {});          // { id: { item, qty } }
const value = useMemo(() => {
  const list = Object.values(lines);                            // array for FlatList
  return {
    lines: list,
    count: list.reduce((n, l) => n + l.qty, 0),                 // total items
    total: list.reduce((s, l) => s + l.qty * l.item.price, 0),  // total price
    qtyOf: (id) => lines[id]?.qty ?? 0,
    add: (item) => dispatch({ type: 'ADD', item }),
    remove: (id) => dispatch({ type: 'REMOVE', id }),
    clear: () => dispatch({ type: 'CLEAR' }),
  };
}, [lines]);
```
```jsx
// HomeScreen.jsx (key part) - filter only when inputs change
const data = useMemo(() => RESTAURANTS.filter((r) =>
  (category === 'All' || r.cuisine.includes(category)) &&
  r.name.toLowerCase().includes(query.trim().toLowerCase())), [query, category]);
// CartScreen.jsx: const grand = lines.length ? total + DELIVERY_FEE : 0;
```

> Verified: the three screens and `CartProvider` rendered under jsdom (react-native-web) inside a tiny fake navigator (`navigate` / `popToTop`): search "pizza" filters, "zzz" shows the empty state, a chip filters, tapping a restaurant opens its menu, ADD / + / - change quantity (qty 2, and "-" back to ADD), Home bar shows "3 items | Rs 847", Cart shows "Rs 877" (847 + Rs 30 fee), Place order clears the cart and returns Home. `App.jsx` only syntax-checked: real React Navigation transitions, safe areas and header on a device/simulator: not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Back navigation | Hardware / gesture back pops the stack | Swipe-from-left-edge gesture |
| Header title | Left-aligned by default | Centered by default |
| Safe area | Status bar / gesture bar insets | Notch / home indicator insets (use SafeAreaProvider) |
| Shadows (cards) | `elevation` | `shadowColor/Offset/Opacity/Radius` |
| `Alert.alert` look | Material dialog | iOS action alert |
| Keyboard over search | `softwareKeyboardLayoutMode` in app.json | Handled by `KeyboardAvoidingView` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx create-expo-app food-clone                      # blank template
npx expo install @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context
npx expo start                                       # run in Expo Go / dev build
```
CLI way:
```bash
npx @react-native-community/cli init FoodClone       # bare project
npm install @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context
cd ios && pod install && cd ..                       # link iOS pods
npx react-native run-android                         # or run-ios
```
```js
// JS code (App.jsx, screens, CartContext) is the same in both. Only setup/run commands differ.
// Alternative in Expo: expo-router (file-based routes) instead of manual Stack setup.
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Mutating cart state: `state[id].qty++`.
✅ **Correct:** Return a new object in the reducer (`{ ...state, [id]: {...} }`).

❌ **Mistake 2:** Storing `count` and `total` in state as well as lines (they go out of sync).
✅ **Correct:** Derive them with `reduce` from the single source of truth.

❌ **Mistake 3:** `useCart()` outside `CartProvider` returns null -> crash.
✅ **Correct:** Wrap the navigator in `CartProvider` and throw a clear error in `useCart`.

❌ **Mistake 4:** `keyExtractor` using index, or no unique id.
✅ **Correct:** Use stable ids (`r.id`, `m.id`).

❌ **Mistake 5:** Passing the whole restaurant object in navigation params.
✅ **Correct:** Pass only `{ id }` and look up data on the next screen (params stay small and serializable).

---

## 🧠 Tricky Interview Question
**Q:** Every `ADD` tap re-renders every screen that calls `useCart()`, even `CartScreen` far down the stack. Why, and how do you reduce it?

**Answer:** The provider's `value` object changes whenever `lines` changes, and every consumer of the context re-renders on a new value (the stack keeps previous screens mounted). Reduce with: split context into two (state and actions; actions are stable), `React.memo` on list rows, or a selector-based store like Zustand/Redux Toolkit where a component subscribes only to the slice it needs. For this small app, `useMemo` on the value is enough.

---

## ⚫ Interview Questions + Answers

**Q1: Context vs Redux/Zustand for the cart?**
A1: Context + useReducer is fine for small state with few updates. For frequent updates and many consumers, Zustand/Redux give selectors and avoid broad re-renders. Both also need persistence (AsyncStorage) if the cart must survive restarts.

**Q2: Why a reducer instead of several `useState`?**
A2: One pure function describes all transitions, easy to unit test (`cartReducer(state, action)`), and prevents inconsistent updates.

**Q3: How would you replace dummy data with an API?**
A3: Fetch in Home with `useEffect` (or React Query), keep `loading` / `error` states and `ListEmptyComponent`; the menu is fetched by `id` on the Restaurant screen.

**Q4: How to persist the cart across app restarts?**
A4: Save `lines` to AsyncStorage on change (`useEffect`) and hydrate in the provider on start (show splash until loaded).

**Q5: What if the user adds from restaurant A, then opens restaurant B?**
A5: Real apps allow only one restaurant per cart: store `restaurantId` in the cart and on ADD from another restaurant ask "Replace cart?". Our demo allows mixing - mention this as an improvement.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Machine-coding/interview rounds needing navigation + shared state + lists
- Small apps where Context is enough

❌ Avoid when:
- Cart updates are very frequent in a huge app (prefer a selector-based store)
- You need server-side cart sync (cart lives in backend; client only caches)

---

## 📊 Visual Diagram
```
 App
  └ SafeAreaProvider
     └ CartProvider  (useReducer: ADD / REMOVE / CLEAR)
        └ NavigationContainer
           └ Stack
              ├ Home ──(restaurant id)──▶ Restaurant ──▶ ADD/+/-  ┐
              │   ▲ "3 items | Rs 847" bar ◀── count,total ◀─────┘
              └ Cart: lines + fee Rs 30 = "To pay" ─ Place order ─▶ clear() ─▶ popToTop()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reducer | Pure function (state, action) -> new state | State बदलने वाला शुद्ध function |
| Context | Share data without prop drilling | Props नीचे भेजे बिना data साझा करना |
| Derived state | Value computed from other state | दूसरे state से निकाला गया value |
| `useMemo` | Cache a computed value | Computed value को cache करना |
| Stack navigator | Screens pushed/popped like a stack | Screens का stack |
| Route params | Data passed to the next screen | अगली screen को भेजा data |

---

## ⚡ 3-Line Summary
**English:**
1. Build in layers: data, reducer cart, context provider, screens, navigation.
2. Keep one source of truth (`lines`) and derive count, total and bill from it.
3. Pass only ids in route params, memoise filters, and mention one-restaurant-per-cart as an improvement.

**Hindi:**
1. परतों में बनाओ: data, reducer cart, context provider, screens, navigation।
2. एक source of truth (`lines`) रखो और count, total, bill उसी से निकालो।
3. Route params में सिर्फ id भेजो, filter को memoise करो, और "एक cart = एक restaurant" को सुधार के रूप में बताओ।

---

## ➡️ Next Topic
**Section 14 onwards** - यहाँ 13-interview-problems खत्म होता है। अगला: quick-revision cheatsheets और top-50 interview Q&A, ताकि सब कुछ जल्दी दोहरा सको।
