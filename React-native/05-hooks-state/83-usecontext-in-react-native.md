# 83. useContext in React Native
# हिंदी में: React Native में useContext
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76, React 18.3)** — check current docs — APIs change between SDKs. (React 19 में `<Context>` सीधे Provider की तरह और `use(Context)` भी चलता है।)

---

## 🔵 Simple Definition (English)
**Context** lets you share data (theme, logged-in user, language, cart) with **any component in a subtree** without passing props down every level. You create a context, wrap the tree in a **Provider**, and read the value with `useContext(MyContext)`.

## 🔵 सरल परिभाषा (Hindi)
**Context** से आप data (theme, logged-in user, language, cart) को subtree के **किसी भी component** तक बिना हर level पर props pass किए पहुँचा सकते हो। Context बनाओ, tree को **Provider** में wrap करो, और `useContext(MyContext)` से value पढ़ो।

---

## 🔴 Problem it Solves
```
❌ Prop drilling: App -> Home -> List -> Card -> Button (sirf Button ko user chahiye)
❌ Beech ke components ko un props se kuch lena-dena nahi
✅ Context: jahan chahiye wahin se seedha read karo
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Prop drilling: App -> Home -> List -> Card -> Button (सिर्फ़ Button को user चाहिए)
❌ बीच के components को उन props से कोई मतलब नहीं
✅ Context: जहाँ चाहिए वहीं से सीधा पढ़ो
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → const AuthCtx = createContext(defaultValue)
Step 2 → <AuthCtx.Provider value={...}> wraps part of the tree (usually in App)
Step 3 → Any descendant: const auth = useContext(AuthCtx)
Step 4 → When Provider's value changes (by reference), ALL consumers re-render
Step 5 → Best practice: custom hook useAuth() + provider component AuthProvider
Step 6 → If no Provider above, consumers get the defaultValue
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const AuthCtx = createContext(defaultValue)
Step 2 → <AuthCtx.Provider value={...}> tree के हिस्से को wrap करता है (आमतौर पर App में)
Step 3 → कोई भी descendant: const auth = useContext(AuthCtx)
Step 4 → Provider की value (reference से) बदले तो सारे consumers re-render होते हैं
Step 5 → Best practice: custom hook useAuth() + AuthProvider component
Step 6 → ऊपर Provider न हो तो consumer को defaultValue मिलती है
```

---

## 🟡 Real World Example
**Swiggy**: `AuthContext` (user, token, login/logout), `CartContext` (items, add/remove), `ThemeContext` (dark mode). Header badge reads cart count; Checkout reads the same cart; Profile reads user. **Paytm**: language (Hindi/English) context so every screen shows translated text.

## 🟡 Real Example Hindi mein
**Swiggy**: `AuthContext` (user, token, login/logout), `CartContext` (items, add/remove), `ThemeContext` (dark mode)। Header का badge cart count पढ़ता है; Checkout वही cart पढ़ता है; Profile user पढ़ता है। **Paytm**: language (Hindi/English) context ताकि हर screen translated text दिखाए।

---

## 💻 Code Example — Basic
```jsx
// Basic: Theme context with a toggle
import React, { createContext, useContext, useState } from 'react'; // React APIs
import { View, Text, Button, StyleSheet } from 'react-native';      // UI

const ThemeContext = createContext({ dark: false, toggle: () => {} }); // default value

function ThemeProvider({ children }) {                              // provider component
  const [dark, setDark] = useState(false);                          // the shared state
  const value = { dark, toggle: () => setDark((d) => !d) };         // shared value
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

function Card() {                                                   // deep component
  const { dark } = useContext(ThemeContext);                        // read context
  return (
    <View style={[styles.card, dark && styles.cardDark]}>
      <Text style={{ color: dark ? '#fff' : '#111' }}>Biryani Rs.180</Text>
    </View>
  );
}

function ToggleButton() {
  const { dark, toggle } = useContext(ThemeContext);                // read + action
  return <Button title={dark ? 'Light mode' : 'Dark mode'} onPress={toggle} />;
}

export default function App() {
  return (
    <ThemeProvider>{/* wrap whole tree */}
      <View style={{ padding: 20, gap: 12 }}>
        <ToggleButton />
        <Card />
      </View>
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  card: { padding: 16, borderRadius: 10, backgroundColor: '#eee' },
  cardDark: { backgroundColor: '#222' },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Auth + Cart contexts with useReducer, memoised value, custom hooks with
// safety check, and split contexts (state vs actions) to limit re-renders
import React, {
  createContext, useContext, useReducer, useMemo, useCallback, useState, useEffect,
} from 'react';                                                     // React APIs
import { View, Text, Button, ActivityIndicator } from 'react-native'; // UI
import AsyncStorage from '@react-native-async-storage/async-storage'; // persistence (npx expo install)

// ---------- Cart (reducer) ----------
const CartStateCtx = createContext(null);                           // read-only data
const CartActionsCtx = createContext(null);                         // functions (stable)

function cartReducer(state, action) {                               // pure function
  switch (action.type) {
    case 'ADD': {                                                   // add or increment
      const qty = (state[action.id] ?? 0) + 1;
      return { ...state, [action.id]: qty };
    }
    case 'REMOVE': {                                                // decrement / delete
      const qty = (state[action.id] ?? 0) - 1;
      if (qty <= 0) { const { [action.id]: _x, ...rest } = state; return rest; }
      return { ...state, [action.id]: qty };
    }
    case 'CLEAR': return {};                                        // empty cart
    default: return state;                                          // unknown action
  }
}

export function CartProvider({ children }) {
  const [items, dispatch] = useReducer(cartReducer, {});            // cart state
  // actions never change identity -> components using only actions don't re-render
  const actions = useMemo(() => ({
    add: (id) => dispatch({ type: 'ADD', id }),
    remove: (id) => dispatch({ type: 'REMOVE', id }),
    clear: () => dispatch({ type: 'CLEAR' }),
  }), []);
  return (
    <CartActionsCtx.Provider value={actions}>
      <CartStateCtx.Provider value={items}>{children}</CartStateCtx.Provider>
    </CartActionsCtx.Provider>
  );
}

export function useCartItems() {
  const ctx = useContext(CartStateCtx);
  if (ctx === null) throw new Error('useCartItems must be used inside <CartProvider>'); // guard
  return ctx;
}
export function useCartActions() {
  const ctx = useContext(CartActionsCtx);
  if (ctx === null) throw new Error('useCartActions must be used inside <CartProvider>');
  return ctx;
}

// ---------- Auth (async restore on app start) ----------
const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);                           // logged-in user
  const [booting, setBooting] = useState(true);                     // restoring session?

  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem('user');             // read saved user
        if (raw) setUser(JSON.parse(raw));                          // restore
      } catch (e) { console.log('restore failed', e); }             // ignore corrupt data
      finally { setBooting(false); }                                // done booting
    })();
  }, []);

  const login = useCallback(async (u) => {
    setUser(u);
    await AsyncStorage.setItem('user', JSON.stringify(u));          // persist
  }, []);
  const logout = useCallback(async () => {
    setUser(null);
    await AsyncStorage.removeItem('user');
  }, []);

  const value = useMemo(() => ({ user, booting, login, logout }), [user, booting, login, logout]);
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}

// ---------- Usage ----------
function Gate() {
  const { user, booting, login, logout } = useAuth();
  const items = useCartItems();
  const { add } = useCartActions();
  if (booting) return <ActivityIndicator />;                        // splash while restoring
  return user ? (
    <View>
      <Text>Hi {user.name}, items: {Object.keys(items).length}</Text>
      <Button title="Add biryani" onPress={() => add('b1')} />
      <Button title="Logout" onPress={logout} />
    </View>
  ) : <Button title="Login" onPress={() => login({ name: 'Aditya' })} />;
}

export default function App() {
  return (
    <AuthProvider><CartProvider><Gate /></CartProvider></AuthProvider>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Context behaviour | Same | Same |
| Persisted context data (AsyncStorage) | App data can be cleared by user in Settings | Cleared on uninstall |
| Cold start restore | Android may kill background app often -> restore flow matters | Same but less frequent |
| Theme source | `useColorScheme()` from system | `useColorScheme()` from system |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Router: put providers in app/_layout.jsx so every route can use them
import { Slot } from 'expo-router';
export default function RootLayout() {
  return <AuthProvider><Slot /></AuthProvider>;
}
```
CLI way:
```jsx
// CLI + React Navigation: wrap NavigationContainer in providers (App.js)
export default function App() {
  return <AuthProvider><NavigationContainer>{/* navigators */}</NavigationContainer></AuthProvider>;
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: New object in `value` on every render
```jsx
<Ctx.Provider value={{ user, login }} />   // ❌ new object each render -> all consumers re-render
```
✅ Correct: `useMemo(() => ({ user, login }), [user, login])`.

❌ Mistake 2: Putting fast-changing state (typing text, scroll position) in context
✅ Correct: keep it local or use a store with selectors (Zustand/Redux).

❌ Mistake 3: Using `useContext` outside a Provider silently getting default values
✅ Correct: custom hook that throws a helpful error.

❌ Mistake 4: One giant context for everything
✅ Correct: split by concern (Auth, Cart, Theme) or state vs actions.

---

## 🧠 Tricky Interview Question
**Q: A context value is `{ user, cart }`. A component reads only `user`. When `cart` changes, does it re-render?**

**Answer:** **Yes.** `useContext` has no selector: any change in the Provider's value (by reference) re-renders **every** consumer, even if the slice it reads did not change. `React.memo` on the consumer does **not** help against context changes. Solutions: split into separate contexts (UserContext, CartContext), separate state/actions contexts, or use a library with selectors (Zustand, Redux `useSelector`, `use-context-selector`).

---

## ⚫ Interview Questions + Answers

**Q1: What problem does Context solve?**
A1: Prop drilling — sharing data with deep descendants without passing props manually.

**Q2: Context vs Redux?**
A2: Context is a transport mechanism (no selectors, no middleware, no devtools). Redux/Zustand are state managers with selectors and tooling; they scale better for frequently-changing global state.

**Q3: Does context re-render consumers on every parent render?**
A3: Only when the Provider's `value` reference changes. Memoise the value.

**Q4: Can context be used across Navigator screens?**
A4: Yes if Providers wrap `NavigationContainer` (or the navigator); every screen is inside that tree.

**Q5: Default value — when used?**
A5: Only when no Provider is above the consumer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Rarely changing global data (theme, auth, locale, feature flags)
- Simple dependency injection (API client, analytics)

❌ Avoid when:
- High-frequency updates (typing, animation)
- Big global state with many selectors (use Zustand/Redux Toolkit)
- Server cache (use React Query)

---

## 📊 Visual Diagram
```
<AuthProvider value={user}>
   └─ NavigationContainer
        └─ Home
             └─ List
                  └─ Card
                       └─ Button ── useContext(AuthCtx) ──► user
Without context:  user passed as props through List, Card, ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context | Shared data channel | Shared data का रास्ता |
| Provider | Supplies the value | Value देने वाला component |
| Consumer | Reads the value | Value पढ़ने वाला |
| Prop drilling | Passing props through layers | Layers से props भेजना |
| Memoised value | Stable object reference | Stable reference वाली value |
| Selector | Pick a slice of state | State का हिस्सा चुनना |

---

## ⚡ 3-Line Summary
**English:**
1. Context shares data with deep components without prop drilling.
2. Wrap tree in Provider, read via `useContext`, wrap in a custom hook.
3. All consumers re-render on value change, so memoise and split contexts.

**Hindi:**
1. Context गहरे components तक बिना prop drilling data पहुँचाता है।
2. Tree को Provider में wrap करो, `useContext` से पढ़ो, custom hook में लपेटो।
3. Value बदलने पर सारे consumers re-render होते हैं, इसलिए memoise और contexts split करो।

---

## ➡️ Next Topic
**84. Custom Hooks in React Native** — अपना reusable logic (useFetch, useDebounce, useNetwork) बनाना।
