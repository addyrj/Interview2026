# 71. Passing Params Between Screens
# हिंदी में: Screens के बीच Params कैसे Pass करें?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
In React Navigation, you pass data between screens using **route params**. Navigate with: `navigation.navigate('ProductDetail', { productId: 123 })`. Receive with: `route.params.productId` (or `useRoute()` hook). Unlike web's URL query params, RN route params are in-memory objects — any JavaScript type works (objects, arrays, functions).

## 🔵 सरल परिभाषा (Hindi)
React Navigation में screens के बीच data pass करने के लिए **route params** use होते हैं। Navigate: `navigation.navigate('ProductDetail', { productId: 123 })`। Receive: `route.params.productId` (या `useRoute()` hook)। Web के URL query params के unlike, RN route params in-memory objects हैं — कोई भी JavaScript type काम करता है (objects, arrays, functions)।

---

## 🔴 Problem it Solves
```
COMMON NAVIGATION DATA NEEDS:
Zomato app:
  Restaurant List → tap restaurant → Restaurant Detail
  How does Detail screen know WHICH restaurant?
  Answer: pass restaurantId as param!

PhonePe:
  Contact List → tap contact → Send Money
  Send Money screen needs: contact name, phone number
  Answer: pass { name, phone } as params!

Myntra:
  Product List → tap product → Product Detail
  Product Detail needs: product ID, source (list/search/wishlist)
  Answer: pass { productId, source } as params!

WITHOUT PARAMS: Every screen shows same data (wrong!)
WITH PARAMS: Each screen shows correct contextual data
```

## 🔴 यह क्यों बना? (Hindi)
```
Restaurant list → detail screen, product list → detail screen —
किस item का detail दिखाना है? Params से बताओ!
navigate('Detail', { id: 123 }) → Detail screen में route.params.id = 123
```

---

## 🟢 How it Works — Step by Step

```
PASSING PARAMS:
──────────────────────────────────────────────────────
  Step 1 → User taps item in list screen
           onPress triggers navigate

  Step 2 → navigation.navigate('DetailScreen', {
              id: 123,
              title: 'Butter Chicken',
              price: 350,
            })

  Step 3 → React Navigation creates route object:
           { name: 'DetailScreen', params: { id: 123, title: '...', price: 350 } }

  Step 4 → DetailScreen mounts
           route.params available immediately

  Step 5 → Use params: const { id, title, price } = route.params;

UPDATING PARAMS (same screen):
  navigation.setParams({ price: 400 })  // updates current screen's params

INITIAL PARAMS (default values):
  <Stack.Screen
    name="Detail"
    component={DetailScreen}
    initialParams={{ source: 'unknown' }}  // fallback values
  />

GOING BACK WITH RESULT (like Android's onActivityResult):
  In child screen: navigation.navigate('Parent', { selectedId: 5 })
  In parent screen: useEffect on route.params changes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Screen A: navigation.navigate('ScreenB', { id: 123, name: 'abc' })
Screen B: const { id, name } = route.params;  // या useRoute().params
Params in-memory रहते हैं — कोई भी JS type works!
```

---

## 🟡 Real World Example
**Zomato Order Flow:** (1) Home → tap restaurant → `navigate('Restaurant', { restaurantId: 'r123', restaurantName: 'Barbeque Nation' })`. (2) Restaurant → tap dish → `navigate('DishDetail', { dishId: 'd456', restaurantId: 'r123' })`. (3) DishDetail → add to cart → `navigate('Cart', { newItemAdded: true })`. Each screen gets exactly the data it needs — no global state needed for this simple flow.

## 🟡 Real Example Hindi मे
**Zomato:** Home → restaurant tap → `navigate('Restaurant', { restaurantId: 'r123' })` → dish tap → `navigate('DishDetail', { dishId: 'd456' })` → cart। हर screen को exactly जरूरी data मिलता है — simple flows के लिए global state की जरूरत नहीं।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';

// SCREEN 1: Product List — sends params
function ProductListScreen() {
  const navigation = useNavigation();

  const products = [
    { id: '1', name: 'Butter Chicken', price: 350, category: 'North Indian' },
    { id: '2', name: 'Masala Dosa', price: 120, category: 'South Indian' },
    { id: '3', name: 'Biryani', price: 280, category: 'Hyderabadi' },
  ];

  const handleProductPress = (product) => {
    // Pass params to next screen
    navigation.navigate('ProductDetail', {
      productId: product.id,        // string
      productName: product.name,    // string
      price: product.price,         // number
      category: product.category,   // string
      // Can pass any type: object, array, etc.
    });
  };

  return (
    <FlatList
      data={products}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <TouchableOpacity
          style={styles.item}
          onPress={() => handleProductPress(item)}
        >
          <Text style={styles.itemName}>{item.name}</Text>
          <Text style={styles.itemPrice}>₹{item.price}</Text>
        </TouchableOpacity>
      )}
    />
  );
}

// SCREEN 2: Product Detail — receives params
function ProductDetailScreen() {
  const route = useRoute();          // useRoute hook

  // Destructure params
  const { productId, productName, price, category } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{productName}</Text>
      <Text style={styles.category}>{category}</Text>
      <Text style={styles.price}>₹{price}</Text>
      <Text style={styles.id}>ID: {productId}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  item: {
    flexDirection: 'row', justifyContent: 'space-between',
    padding: 16, borderBottomWidth: 1, borderBottomColor: '#eee',
  },
  itemName: { fontSize: 16, fontWeight: '500' },
  itemPrice: { fontSize: 16, color: '#f97316', fontWeight: '600' },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 8 },
  category: { fontSize: 14, color: '#666', marginBottom: 4 },
  price: { fontSize: 20, color: '#f97316', fontWeight: '700', marginBottom: 4 },
  id: { fontSize: 12, color: '#999' },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';

// PATTERN: TypeScript types for route params (prevents bugs!)
// In your types file or at top of screen:
type RootStackParamList = {
  Home: undefined;                    // no params
  ProductDetail: {
    productId: string;
    productName: string;
    price: number;
    source: 'list' | 'search' | 'wishlist';
  };
  Checkout: {
    items: Array<{ id: string; quantity: number }>;
    couponCode?: string;              // optional param
  };
};

// Typed navigation hook
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';

type ProductDetailNavProp = NativeStackNavigationProp<RootStackParamList, 'ProductDetail'>;
type ProductDetailRouteProp = RouteProp<RootStackParamList, 'ProductDetail'>;

function ProductDetailScreen() {
  const navigation = useNavigation<ProductDetailNavProp>();
  const route = useRoute<ProductDetailRouteProp>();

  // TypeScript knows all params and their types!
  const { productId, productName, price, source } = route.params;
  // route.params.productId → string (typed!)
  // route.params.price → number (typed!)

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{productName}</Text>
      <Text>₹{price}</Text>
      <Text>Opened from: {source}</Text>
    </View>
  );
}

// PATTERN: Passing result back to parent screen
// (like selecting an address and returning to checkout)
function AddressListScreen() {
  const navigation = useNavigation();

  const selectAddress = (address) => {
    // Go BACK and pass data to the previous screen
    navigation.navigate('Checkout', {
      selectedAddress: address,     // this updates Checkout's params!
    });
  };

  return (
    <View>
      <TouchableOpacity onPress={() => selectAddress({ id: 'a1', line: 'MG Road' })}>
        <Text>MG Road, Bangalore</Text>
      </TouchableOpacity>
    </View>
  );
}

// In Checkout screen: listen for the returned address
function CheckoutScreen() {
  const route = useRoute();
  const navigation = useNavigation();

  // Listen for when params change (address was selected and we came back)
  useEffect(() => {
    if (route.params?.selectedAddress) {
      console.log('Address selected:', route.params.selectedAddress);
      // Update local state with new address
    }
  }, [route.params?.selectedAddress]);  // react to param changes

  return (
    <View>
      <Text>Checkout Screen</Text>
      <TouchableOpacity onPress={() => navigation.navigate('AddressList')}>
        <Text>Select Address</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 8 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Back + params | Hardware back sends no params | Swipe back sends no params |
| Deep linking | params from URL | params from URL |
| Param persistence | In memory (lost on app kill) | In memory (lost on app kill) |
| URL encoding | Not needed (in-memory) | Not needed (in-memory) |

---

## 🟠 Expo vs CLI Difference

Expo way (Expo Router):
```jsx
// Expo Router uses file-based routing — params in URL
// app/product/[id].tsx
import { useLocalSearchParams } from 'expo-router';

export default function ProductDetail() {
  const { id } = useLocalSearchParams();  // from URL
  // navigate: router.push('/product/123')
}
```

CLI way (React Navigation):
```jsx
// React Navigation — in-memory params
import { useRoute } from '@react-navigation/native';

function ProductDetail() {
  const route = useRoute();
  const { id } = route.params;  // from navigate() call
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Passing non-serializable data (functions, class instances)
```jsx
// WRONG: Functions and class instances as params
navigation.navigate('Detail', {
  onSuccess: () => { /* callback */ },   // ❌ function in params
  productInstance: new Product(123),     // ❌ class instance in params
});
// React Navigation may warn about non-serializable params
// Deep linking and state persistence will FAIL

// CORRECT: Pass IDs, primitives, plain objects
navigation.navigate('Detail', {
  productId: 123,                        // ✅ primitive
  productData: { id: 123, name: '...' }, // ✅ plain object
});
// Load callbacks/instances inside the screen using the ID
```

❌ **Mistake 2:** Not providing default values for optional params
```jsx
// WRONG: Crashes if param is missing
function DetailScreen() {
  const route = useRoute();
  const { productId } = route.params;  // ❌ crashes if no params!
}

// CORRECT: Default values
function DetailScreen() {
  const route = useRoute();
  const { productId = null, source = 'unknown' } = route.params ?? {};
  // OR use initialParams on Screen definition
}
```

❌ **Mistake 3:** Storing large objects in params instead of using a store
```jsx
// WRONG: Passing huge data in params
navigation.navigate('Detail', {
  product: { ...fullProductObject },  // ❌ 50+ fields, images, nested data
  reviews: [...allReviewsArray],      // ❌ 100 reviews as params
});

// CORRECT: Pass ID, let screen fetch or get from store
navigation.navigate('Detail', {
  productId: product.id,   // ✅ just the ID
});
// In DetailScreen: fetch by ID or get from Zustand/Redux store by ID
```

---

## 🧠 Tricky Interview Question

**Q: A user is on Screen C (grandchild). They want to go back to Screen A (grandparent), skipping Screen B. How do you pass data back to Screen A?**

**Answer:** Three approaches: (1) **`navigation.popToTop()`** goes to root without passing data. (2) **`navigation.navigate('ScreenA', { result: data })`** — this pops to ScreenA and passes params. The navigate call finds ScreenA in the stack and pops everything above it, passing the new params. ScreenA should have a `useEffect` watching `route.params?.result`. (3) **Shared state (Zustand/Redux/Context)** — instead of passing params back, update global state in Screen C. Screen A reads from the store. This is the cleanest pattern for complex nested navigation results. Avoid option 2 for passing large data.

---

## ⚫ Interview Questions + Answers

**Q1: How do you pass data between screens in React Navigation?**
A1: `navigation.navigate('TargetScreen', { key: value, ... })` passes params. The target screen receives them via `route.params` (from the prop) or `useRoute().params` (hook). Params are in-memory objects — any JavaScript type is valid (strings, numbers, arrays, plain objects). Unlike web URLs, no serialization is needed for in-app navigation.

**Q2: What is `useRoute()` hook?**
A2: `useRoute()` is a React Navigation hook that returns the current screen's `route` object: `{ name: 'ScreenName', params: { ... }, key: '...' }`. Equivalent to the `route` prop passed to screen components. Use it to access params without prop drilling: `const { params } = useRoute()`. Also useful in nested components that aren't directly screen components (can't receive the `route` prop directly).

**Q3: How do you set default param values for a screen?**
A3: Two ways: (1) **In Screen definition**: `<Stack.Screen name="Detail" component={DetailScreen} initialParams={{ source: 'unknown', page: 1 }} />` — these are the defaults, overridden when navigate passes params. (2) **In component**: destructure with defaults: `const { productId, source = 'list' } = route.params ?? {}`. Both approaches are safe; `initialParams` is better for documenting expected params per screen.

**Q4: Can you pass a callback function as a route param?**
A4: Technically yes, but it's strongly discouraged. React Navigation may warn about non-serializable params, deep linking breaks (can't serialize functions to URL), and state persistence (saving navigation state to disk) fails. Better alternative: (1) Use a ref in the parent screen and expose it via context. (2) Use a callback registered in Zustand/Redux. (3) Use `navigation.navigate()` back to parent with result data and `useEffect` to watch param changes.

**Q5: How do you update the current screen's params without navigating?**
A5: `navigation.setParams({ key: newValue })` updates the current screen's params without navigating. Useful for: updating the header dynamically (e.g., selected item count in a filter screen), storing selection state in params so it's preserved during back/forward navigation. Example: in a filter screen, as user selects filters, `navigation.setParams({ selectedCount: filters.length })` — the header can show "Filters (3)" by reading `route.params.selectedCount`.

---

## 🔷 When to Use + When Not to Use
✅ **Use route params when:**
- Passing an ID to a detail screen
- Passing simple selection data (selected tab, source screen)
- Small plain objects that describe what to show

❌ **Don't use route params for:**
- Large data objects (user's full profile, all products)
- Functions/callbacks
- Shared mutable state (use Zustand/Redux)
- Data that multiple screens need (use a store)

---

## 📊 Visual Diagram

```
PARAMS FLOW:
──────────────────────────────────────────────────────
  ProductList Screen
  ┌──────────────────────────────────────────────────┐
  │  onPress → navigation.navigate('Detail', {       │
  │    productId: '123',                             │
  │    name: 'Butter Chicken',                       │
  │    price: 350                                    │
  │  })                                              │
  └──────────────────────────────────────────────────┘
       │  navigate with params
       ▼
  Stack: [ProductList] → [ProductDetail {id:'123', name:'...', price:350}]

  ProductDetail Screen
  ┌──────────────────────────────────────────────────┐
  │  const { productId, name, price } = route.params │
  │  → productId: '123'                              │
  │  → name: 'Butter Chicken'                        │
  │  → price: 350                                    │
  └──────────────────────────────────────────────────┘

RETURNING DATA (via navigate back):
──────────────────────────────────────────────────────
  Screen C (Grandchild)
  navigation.navigate('ScreenA', { selectedItem: item })
       │
       ▼
  Stack pops to ScreenA: [ScreenA {selectedItem: item}]
       │
       ▼
  ScreenA: useEffect watches route.params?.selectedItem
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| route.params | Current screen's params object | Current screen के params |
| navigate | Go to screen + pass params | Screen पर जाओ + params pass |
| useRoute | Hook to access route object | Route object access करने का hook |
| initialParams | Default params for a screen | Screen के default params |
| setParams | Update current screen's params | Current screen के params update |
| Deep linking | Opening screen via URL | URL से screen open करना |
| Stack | Navigation history | Navigation history |

---

## ⚡ 3-Line Summary
**English:**
1. Pass data with `navigation.navigate('Screen', { key: value })`, receive with `const { key } = route.params` or `useRoute().params` — any JS type works.
2. Use `initialParams` for default values, `navigation.setParams()` to update current screen's params, TypeScript route types to prevent runtime errors.
3. Don't pass large objects, functions, or class instances as params — pass IDs and fetch/get full data in the target screen from a store.

**Hindi:**
1. Pass करो: `navigation.navigate('Screen', { key: value })`, receive करो: `route.params` या `useRoute().params` — कोई भी JS type।
2. Default values: `initialParams`; current screen update: `navigation.setParams()`; type safety: TypeScript route types।
3. Large objects, functions, class instances params में mat pass करो — IDs pass करो, target screen में store से fetch करो।

---

## ➡️ Next Topic
**72. useNavigation Hook** — navigation prop के बिना navigate करना, nested components में use।
