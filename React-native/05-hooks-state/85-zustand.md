# 85. Zustand State Management
# हिंदी में: Zustand — React Native में State Management
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Zustand** (German for "state") is a minimal, fast global state management library for React/React Native. Unlike Redux (which needs actions, reducers, dispatch, connect), Zustand is just a function: `create((set) => ({ state, action }))`. No boilerplate, no providers, works with hooks directly. Default choice for new React Native projects.

## 🔵 सरल परिभाषा (Hindi)
**Zustand** (जर्मन में "state") React/React Native के लिए minimal, fast global state management library है। Redux (actions, reducers, dispatch, connect) के unlike, Zustand बस एक function है: `create((set) => ({ state, action }))`। No boilerplate, no providers, hooks से directly काम करता है। New React Native projects के लिए default choice।

---

## 🔴 Problem it Solves
```
GLOBAL STATE CHALLENGES:
  Cart items → needed in ProductList, ProductDetail, CartScreen, Header
  Auth user → needed in ProfileScreen, HomeScreen, API calls, Navigation
  Theme → needed everywhere

WITHOUT GLOBAL STATE:
  Prop drilling: pass cart down 5 components deep
  Context hell: multiple nested providers
  Redux boilerplate: 5+ files per feature

ZUSTAND SOLUTION:
  1 file per store → used anywhere via hook
  const { items, addItem } = useCartStore();
  No Provider, no connect(), no mapStateToProps
```

## 🔴 यह क्यों बना? (Hindi)
```
Cart, auth, theme जैसा global state हर जगह चाहिए।
Prop drilling: 5 levels deep — nightmare।
Redux: 5 files per feature — too much boilerplate।
Zustand: 1 file, 1 hook, use anywhere = simple!
```

---

## 🟢 How it Works — Step by Step

```
ZUSTAND INTERNALS:
──────────────────────────────────────────────────────
  Step 1 → create() creates a store with state + actions

  Step 2 → Store is a React Hook (useCartStore)
           Internally uses useRef + useSyncExternalStore

  Step 3 → Components subscribe to specific slices
           const items = useCartStore(state => state.items)
           Only re-renders when items SPECIFICALLY changes

  Step 4 → Action calls set() to update state
           set() triggers re-render only in subscribed components

  Step 5 → Components outside React (API, interceptors):
           useCartStore.getState()  → current state
           useCartStore.setState()  → update state

  KEY BENEFITS:
  ✅ No Provider needed (global singleton)
  ✅ Selector-based subscriptions (granular re-renders)
  ✅ Works outside React (in API interceptors!)
  ✅ Middleware: persist, devtools, immer
  ✅ TypeScript native support
```

## 🟢 कैसे काम करता है? (Hindi)
```
create() → store (hook) बनाता है।
Component में: const value = useStore(state => state.value) → subscribe।
state.value change → only subscribed components re-render।
Outside React: useStore.getState() → direct access।
```

---

## 🟡 Real World Example
**Swiggy Cart:** User browses restaurants, taps items → adds to cart. Cart count shows in header, cart contents in CartScreen, add/remove buttons in ProductList. All three screens use `useCartStore()`. When user adds an item from ProductList: `addItem(dish)` updates store → CartScreen and Header automatically re-render with new count. No prop drilling, no context hell — Zustand handles it all.

## 🟡 Real Example Hindi मे
**Swiggy Cart:** ProductList में add button → `addItem()` → CartScreen और Header automatically update। तीनों components `useCartStore()` use करते हैं। कोई prop drilling नहीं, कोई context नहीं — Zustand सब handle।

---

## 💻 Code Example — Basic

```typescript
// cartStore.ts — Cart state management
import { create } from 'zustand';

type CartItem = {
  id: string;
  name: string;
  price: number;
  quantity: number;
  restaurantId: string;
};

type CartStore = {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
  restaurantId: string | null;   // can only order from one restaurant at a time

  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
};

export const useCartStore = create<CartStore>((set, get) => ({
  items: [],
  totalItems: 0,
  totalPrice: 0,
  restaurantId: null,

  addItem: (newItem) => {
    const { items, restaurantId } = get();

    // Can't order from two restaurants
    if (restaurantId && restaurantId !== newItem.restaurantId) {
      // Handle "clear cart and add from new restaurant?" flow
      return;
    }

    const existing = items.find(i => i.id === newItem.id);

    if (existing) {
      // Increment quantity
      set((state) => ({
        items: state.items.map(i =>
          i.id === newItem.id ? { ...i, quantity: i.quantity + 1 } : i
        ),
        totalItems: state.totalItems + 1,
        totalPrice: state.totalPrice + newItem.price,
      }));
    } else {
      // Add new item
      set((state) => ({
        items: [...state.items, { ...newItem, quantity: 1 }],
        totalItems: state.totalItems + 1,
        totalPrice: state.totalPrice + newItem.price,
        restaurantId: newItem.restaurantId,
      }));
    }
  },

  removeItem: (itemId) => {
    const item = get().items.find(i => i.id === itemId);
    if (!item) return;

    set((state) => {
      const newItems = item.quantity > 1
        ? state.items.map(i => i.id === itemId ? { ...i, quantity: i.quantity - 1 } : i)
        : state.items.filter(i => i.id !== itemId);

      const isEmpty = newItems.length === 0;
      return {
        items: newItems,
        totalItems: state.totalItems - 1,
        totalPrice: state.totalPrice - item.price,
        restaurantId: isEmpty ? null : state.restaurantId,
      };
    });
  },

  updateQuantity: (itemId, quantity) => {
    if (quantity === 0) {
      get().removeItem(itemId);
      return;
    }
    set((state) => ({
      items: state.items.map(i => i.id === itemId ? { ...i, quantity } : i),
    }));
  },

  clearCart: () => set({ items: [], totalItems: 0, totalPrice: 0, restaurantId: null }),
}));

// USAGE IN COMPONENTS:
// const { items, totalItems, addItem } = useCartStore();

// SELECTIVE SUBSCRIPTION (avoid unnecessary re-renders):
// const totalItems = useCartStore(state => state.totalItems);
// → Only re-renders when totalItems changes, NOT when items array changes
```

## 💻 Code Example — Advanced

```typescript
// Zustand + MMKV Persistence + Middleware
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';  // optional: mutable-style updates
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV({ id: 'zustand-store' });

// MMKV adapter for Zustand persist middleware
const mmkvStorage = {
  getItem: (name: string) => storage.getString(name) ?? null,
  setItem: (name: string, value: string) => storage.set(name, value),
  removeItem: (name: string) => storage.delete(name),
};

// COMBINED STORE: Auth + Cart + Theme (or separate files in real projects)
type AppStore = {
  // Auth slice
  auth: {
    token: string | null;
    user: { id: string; name: string } | null;
    isLoggedIn: boolean;
  };
  setAuth: (token: string, user: any) => void;
  clearAuth: () => void;

  // Theme slice
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
};

export const useAppStore = create<AppStore>()(
  persist(
    immer((set) => ({
      // Auth state
      auth: {
        token: null,
        user: null,
        isLoggedIn: false,
      },
      setAuth: (token, user) => set((state) => {
        // immer: mutate directly! (no need for spread)
        state.auth.token = token;
        state.auth.user = user;
        state.auth.isLoggedIn = true;
      }),
      clearAuth: () => set((state) => {
        state.auth.token = null;
        state.auth.user = null;
        state.auth.isLoggedIn = false;
      }),

      // Theme state
      theme: 'system',
      setTheme: (theme) => set({ theme }),  // simple set for non-nested
    })),
    {
      name: 'app-store',                          // storage key
      storage: createJSONStorage(() => mmkvStorage), // use MMKV!
      partialize: (state) => ({
        // Only persist these fields (not derived state)
        auth: state.auth,
        theme: state.theme,
      }),
    }
  )
);

// OUTSIDE REACT (API interceptor, etc.):
// const token = useAppStore.getState().auth.token;
// useAppStore.getState().clearAuth();  // logout programmatically

// USAGE IN COMPONENT:
// const isLoggedIn = useAppStore(state => state.auth.isLoggedIn);
// const setAuth = useAppStore(state => state.setAuth);
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Zustand | ✅ works | ✅ works |
| MMKV persist | ✅ | ✅ |
| Redux DevTools | With Expo Flipper | With Expo Flipper |
| Performance | Same (JS-based) | Same |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
# Zustand itself — no native code, works in Expo Go
npx expo install zustand

# With MMKV persistence — needs Development Build
npx expo install react-native-mmkv
# For Expo Go: use AsyncStorage for persistence instead
```

CLI way:
```bash
npm install zustand
npm install react-native-mmkv  # for persistence
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Subscribing to entire store (unnecessary re-renders)
```tsx
// WRONG: Re-renders on ANY store change (even unrelated state)
const state = useCartStore();  // entire store!
const items = state.items;

// CORRECT: Select only what you need
const items = useCartStore(state => state.items);      // only re-renders when items change
const totalItems = useCartStore(state => state.totalItems);
```

❌ **Mistake 2:** Calling `set()` with function when not needed
```tsx
// UNNECESSARY: Using function form when accessing current state isn't needed
set((state) => ({ theme: 'dark' }));  // ← function form when no state access needed

// CLEANER: Direct object form when not reading previous state
set({ theme: 'dark' });
```

❌ **Mistake 3:** One giant store (harder to maintain)
```tsx
// BAD: One massive store for everything
// userStore = auth + cart + theme + notifications + orders...

// GOOD: Separate stores by domain
// authStore.ts → auth state
// cartStore.ts → cart state
// themeStore.ts → theme state
// Each file focused, easier to test and maintain
```

---

## 🧠 Tricky Interview Question

**Q: A Zustand action needs to read current state AND set new state. What's the difference between using `set()` with a function vs using `get()` then `set()`?**

**Answer:** Both work, but subtle difference: (1) `set((state) => ({ newVal: state.currentVal + 1 }))` — the function receives the **latest** state at the time React's reconciler applies the update. Safe even if multiple updates are batched. (2) `const current = get(); set({ newVal: current.currentVal + 1 })` — `get()` reads state at the time the action runs. If multiple actions fire in rapid succession and React batches them, both updates would read the same `current.currentVal` → last-write wins instead of cumulative. In practice: always use the function form `set((state) => ...)` when your new value depends on old state. Use `get()` when you need to read state to make a decision (not compute new state), like checking `if (get().isLoading) return`.

---

## ⚫ Interview Questions + Answers

**Q1: What is Zustand and how is it different from Redux?**
A1: Zustand is a minimal state management library. Redux: action types, action creators, reducers, dispatch, connect/useSelector — lots of files per feature, steep learning curve. Zustand: one `create()` call defines state + actions together, a single hook for each store, no Provider needed. For most React Native apps, Zustand is sufficient and much simpler. Redux Toolkit reduces Redux boilerplate significantly; choose it for large teams, complex state, or when Redux DevTools debugging matters.

**Q2: Does Zustand need a Provider?**
A2: No. Zustand stores are module-level singletons — not tied to React's component tree. The `create()` call creates a hook that subscribes to the store directly, without needing a `<Provider>` wrapper. This is a key difference from Context API (needs Provider) and Redux (needs `<Provider store={store}>`). Benefit: you can use the store anywhere — components, utility functions, API interceptors — without wrapping the app.

**Q3: How do you prevent unnecessary re-renders in Zustand?**
A3: Use **selector functions**: `const items = useCartStore(state => state.items)` instead of `const { items } = useCartStore()`. The selector version only re-renders when `state.items` changes; the destructured version re-renders on ANY store change. For complex derived values, combine with `useMemo`. For comparing objects/arrays, pass a custom equality function: `useCartStore(state => state.items, shallow)` — `shallow` from Zustand compares array/object contents, not reference.

**Q4: How do you access Zustand state outside a React component?**
A4: `useCartStore.getState()` returns the current state snapshot. `useCartStore.setState()` updates state. Example in Axios interceptor: `const token = useAuthStore.getState().auth.token`. To subscribe outside React: `const unsubscribe = useCartStore.subscribe(state => console.log(state.items))`. Call `unsubscribe()` to stop. This is impossible with Context API (requires component), making Zustand more versatile for non-React code.

**Q5: What is Zustand middleware and name 3 common ones?**
A5: Middleware wraps the `create()` call to add behavior. (1) **`persist`**: saves/restores state to AsyncStorage, MMKV, or any storage. `persist(stateCreator, { name: 'key', storage: mmkvStorage })`. (2) **`immer`**: enables mutable-style state updates — `state.items.push(item)` instead of `[...state.items, item]`. (3) **`devtools`**: connects to Redux DevTools browser extension for time-travel debugging. (4) **`subscribeWithSelector`**: adds `subscribe(selector, listener)` for granular change listening outside React.

---

## 🔷 When to Use + When Not to Use
✅ **Use Zustand when:**
- Cart, auth, theme — global data multiple screens need
- Simple to complex state that needs actions
- Want easy persistence (MMKV + persist middleware)
- Side effect in interceptors needs store access

✅ **Consider Redux Toolkit when:**
- Large enterprise team (Redux DevTools, stricter patterns)
- Complex async flows (RTK Query for API state)
- Team already knows Redux

❌ **Don't use global state for:**
- Local UI state (open/closed modal) → useState
- Server state (API data) → React Query / TanStack Query
- Form state → react-hook-form

---

## 📊 Visual Diagram

```
ZUSTAND vs REDUX COMPARISON:
──────────────────────────────────────────────────────
  REDUX (lots of files):
  actions/cart.js    → ADD_ITEM, REMOVE_ITEM...
  reducers/cart.js   → switch(action.type)...
  selectors/cart.js  → state.cart.items...
  Component: useSelector + useDispatch + mapStateToProps

  ZUSTAND (1 file):
  cartStore.ts:
    create({
      items: [],
      addItem: (item) => set(state => ({ items: [...state.items, item] }))
    })
  Component: const { items, addItem } = useCartStore();
  Done! ✅

SUBSCRIPTION MODEL:
──────────────────────────────────────────────────────
  Store state: { items: [...], totalItems: 5, theme: 'dark' }
                 │                │                  │
                 │                │                  └─ ThemeComponent
                 │                │                     (re-renders only if theme changes)
                 │                └─ HeaderBadge
                 │                   (re-renders only if totalItems changes)
                 └─ CartScreen
                    (re-renders only if items changes)
  Each component subscribes to ONLY its slice → minimal re-renders!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Zustand | Minimal state management library | Minimal state management library |
| create() | Creates a Zustand store (hook) | Zustand store बनाता है |
| set() | Updates store state | Store state update करता है |
| get() | Reads current store state | Current store state read |
| persist | Save/restore state to storage | State को storage में save/restore |
| selector | Function to pick specific slice | Specific slice pick करने का function |
| shallow | Shallow comparison for selectors | Selectors के लिए shallow comparison |
| immer | Mutable-style state updates | Mutable-style state updates |

---

## ⚡ 3-Line Summary
**English:**
1. Zustand is a minimal global state library — one `create()` call defines state + actions, one hook to use anywhere, no Provider needed.
2. Always use selectors (`useStore(state => state.value)`) to subscribe to specific slices — prevents unnecessary re-renders.
3. Combine with `persist` middleware + MMKV for state that survives app restarts (cart, auth, theme).

**Hindi:**
1. Zustand minimal global state library है — एक `create()` में state + actions, एक hook anywhere, no Provider।
2. हमेशा selectors use करो (`useStore(state => state.value)`) — specific slice subscribe → unnecessary re-renders नहीं।
3. `persist` middleware + MMKV = state app restart पर survive करे (cart, auth, theme)।

---

## ➡️ Next Topic
**86. Redux Toolkit** — Redux without boilerplate, createSlice, RTK Query।
