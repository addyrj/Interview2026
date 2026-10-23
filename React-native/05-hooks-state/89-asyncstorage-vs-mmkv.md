# 89. AsyncStorage vs MMKV
# हिंदी में: AsyncStorage और MMKV में क्या फर्क है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
Both are key-value storage solutions for React Native apps that persist data across app restarts. **AsyncStorage**: async, string-only, slower — the original community solution. **MMKV**: from Tencent's WeChat, synchronous, typed, 10-30x faster using memory-mapped files. MMKV is the modern choice for performance-critical storage.

## 🔵 सरल परिभाषा (Hindi)
दोनों React Native apps में persistent key-value storage हैं। **AsyncStorage**: async, string-only, slower — original community solution। **MMKV**: Tencent के WeChat से, synchronous, typed, 10-30x faster — memory-mapped files use करता है। MMKV performance-critical storage के लिए modern choice है।

---

## 🔴 Problem it Solves
```
STORAGE NEEDS IN MOBILE APPS:
  ✅ Auth token (login session)
  ✅ User preferences (theme, language)
  ✅ Cart items (offline)
  ✅ Recently viewed items
  ✅ Draft form data
  ✅ Onboarding completion flag
  ✅ Push notification preferences

WHY NOT localStorage? (web equivalent)
  → localStorage doesn't exist in React Native!
  → No browser = no window.localStorage
  → Need native storage: AsyncStorage or MMKV

ASYNCSTORAGE PROBLEMS:
  ❌ Always async (even simple reads require await)
  ❌ Stores only strings (must JSON.stringify/parse)
  ❌ Slow on Android (SQLite under the hood)
  ❌ No encryption built-in

MMKV ADVANTAGES:
  ✅ Synchronous reads (no await for simple gets!)
  ✅ Typed: setString/setNumber/setBool/setObject
  ✅ 10-30x faster (mmap = memory-mapped files)
  ✅ Optional encryption
  ✅ Zustand/Redux persistence compatible
```

## 🔴 यह क्यों बना? (Hindi)
```
localStorage web में नहीं है RN में।
AsyncStorage: पुराना, async, string-only।
MMKV: नया, faster, synchronous, typed।
Production apps में MMKV prefer करते हैं।
```

---

## 🟢 How it Works — Step by Step

```
ASYNCSTORAGE INTERNALS:
  Android: SQLite database
  iOS: File system (NSFileManager)
  All operations: async I/O → await required
  Data: always string → manual JSON.stringify/parse

MMKV INTERNALS:
  Uses mmap (memory-mapped files):
  1. File mapped to process memory address space
  2. Reads: direct memory access (no I/O syscall!) → FAST
  3. Writes: writes to memory, OS flushes to disk async
  Result: reads are near-instantaneous
  Typed storage: separate serialization per type
  Optional AES encryption
```

## 🟢 कैसे काम करता है? (Hindi)
```
AsyncStorage: SQLite/File → async I/O → slow
MMKV: mmap → memory-direct access → fast reads
MMKV typed: setString/Number/Bool — JSON serialize नहीं करना
```

---

## 🟡 Real World Example
**PhonePe session management:** Auth token stored in MMKV — every API call reads it synchronously (no await blocking the call). User preferences (UPI PIN saved flag, dark mode) also in MMKV. Order history (large JSON array) uses a database. MMKV is not a database — for large datasets, use SQLite (`expo-sqlite`) or WatermelonDB.

## 🟡 Real Example Hindi मे
**PhonePe:** Auth token MMKV में — हर API call synchronously read करे (no await)। User preferences भी MMKV। Large order history → SQLite। MMKV database नहीं है — small, frequent-access data के लिए।

---

## 💻 Code Example — Basic

```jsx
// ASYNCSTORAGE
import AsyncStorage from '@react-native-async-storage/async-storage';

// STORE (must JSON.stringify objects)
await AsyncStorage.setItem('authToken', 'eyJhbGc...');
await AsyncStorage.setItem('user', JSON.stringify({ id: '123', name: 'Raj' }));

// GET (async, must JSON.parse)
const token = await AsyncStorage.getItem('authToken');
const userStr = await AsyncStorage.getItem('user');
const user = userStr ? JSON.parse(userStr) : null;

// REMOVE
await AsyncStorage.removeItem('authToken');

// MULTIPLE OPERATIONS
const pairs = [['key1', 'val1'], ['key2', 'val2']];
await AsyncStorage.multiSet(pairs);
const values = await AsyncStorage.multiGet(['key1', 'key2']);


// MMKV (react-native-mmkv)
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV();  // create instance

// STORE — typed, synchronous!
storage.set('authToken', 'eyJhbGc...');       // string
storage.set('userId', 123);                    // number (not string!)
storage.set('isLoggedIn', true);              // boolean
storage.set('user', JSON.stringify({ id: '123' }));  // object: still stringify

// GET — synchronous! No await!
const token = storage.getString('authToken'); // string | undefined
const userId = storage.getNumber('userId');  // number | undefined
const isLoggedIn = storage.getBoolean('isLoggedIn');  // boolean | undefined

// DELETE
storage.delete('authToken');

// CHECK EXISTS
if (storage.contains('authToken')) {
  const token = storage.getString('authToken');
}

// Performance comparison:
// AsyncStorage: ~5ms per read on Android
// MMKV: ~0.1ms per read (50x faster!)
```

## 💻 Code Example — Advanced

```jsx
import { MMKV } from 'react-native-mmkv';
import { create } from 'zustand';
import { StateStorage, persist, createJSONStorage } from 'zustand/middleware';

// MMKV instance with encryption
const secureStorage = new MMKV({
  id: 'secure-storage',
  encryptionKey: 'user-specific-encryption-key',  // AES encryption!
});

// Zustand + MMKV persistence (common production pattern)
// Store cart state in MMKV — survives app restart!
const MMKVStateStorage: StateStorage = {
  getItem: (name) => {
    const value = secureStorage.getString(name);
    return value ?? null;
  },
  setItem: (name, value) => {
    secureStorage.set(name, value);
  },
  removeItem: (name) => {
    secureStorage.delete(name);
  },
};

// Zustand store with MMKV persistence
const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],
      totalItems: 0,

      addItem: (item) => set((state) => {
        const existing = state.items.find(i => i.id === item.id);
        if (existing) {
          return {
            items: state.items.map(i =>
              i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
            ),
            totalItems: state.totalItems + 1,
          };
        }
        return {
          items: [...state.items, { ...item, quantity: 1 }],
          totalItems: state.totalItems + 1,
        };
      }),

      clearCart: () => set({ items: [], totalItems: 0 }),
    }),
    {
      name: 'cart-storage',           // MMKV key
      storage: createJSONStorage(() => MMKVStateStorage),  // use MMKV!
    }
  )
);

// Usage: cart persists across app restarts!
// const { items, addItem } = useCartStore();
```

---

## 📱 Android vs iOS Difference
| Feature | AsyncStorage | MMKV |
|---------|-------------|------|
| Android storage | SQLite | mmap file |
| iOS storage | File system | mmap file |
| Android speed | ~5ms | ~0.1ms |
| iOS speed | ~1ms | ~0.05ms |
| Expo Go | ✅ | ❌ (needs Development Build) |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
# AsyncStorage — works in Expo Go
expo install @react-native-async-storage/async-storage

# MMKV — needs Development Build (not Expo Go)
expo install react-native-mmkv
# Then: npx expo prebuild + eas build --profile development
```

CLI way:
```bash
# AsyncStorage
npm install @react-native-async-storage/async-storage
# android/app/build.gradle: auto-linked

# MMKV
npm install react-native-mmkv
# android/app/build.gradle: auto-linked
# ios: pod install
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using AsyncStorage without try/catch
```jsx
// WRONG: No error handling
const token = await AsyncStorage.getItem('token');  // could throw!

// CORRECT:
try {
  const token = await AsyncStorage.getItem('token');
  return token;
} catch (error) {
  console.error('Storage read failed:', error);
  return null;
}
```

❌ **Mistake 2:** Using MMKV for large datasets
```jsx
// WRONG: Storing 500 order history items in MMKV
storage.set('orderHistory', JSON.stringify(orders));  // ❌ too much data!

// CORRECT: MMKV for small/frequent data, SQLite for datasets
// Small (< 10KB): auth token, preferences → MMKV
// Medium (< 100KB): recent orders (10 items) → MMKV is ok
// Large (100KB+): order history, products cache → expo-sqlite / WatermelonDB
```

❌ **Mistake 3:** Accessing MMKV before initialization (concurrent issues)
```jsx
// WRONG: Creating MMKV instance inside component (performance)
function Component() {
  const storage = new MMKV();  // ❌ creates new instance each render!
  const value = storage.getString('key');
}

// CORRECT: Create storage once, outside component
const storage = new MMKV();  // module-level singleton

function Component() {
  const value = storage.getString('key');  // ✅ uses singleton
}
```

---

## 🧠 Tricky Interview Question

**Q: User clears app data on Android. What happens to AsyncStorage and MMKV stored data?**

**Answer:** Both get wiped — AsyncStorage (SQLite) and MMKV files are in the app's data directory (`/data/data/<package>/`). "Clear App Data" on Android removes everything. Same for iOS: deleting the app removes all local storage. This is the expected behavior — these are app-specific storage mechanisms. For critical user data that must survive: (1) Sync to your server (auth tokens can be re-fetched after re-login). (2) Use Keychain (iOS) / KeyStore (Android) via `expo-secure-store` or `react-native-keychain` — these use the OS's secure enclave and survive app reinstall on iOS (but not "Clear Data" on Android). Never store truly critical data only in device storage.

---

## ⚫ Interview Questions + Answers

**Q1: Why use MMKV instead of AsyncStorage?**
A1: Speed and simplicity. MMKV: synchronous reads (no await blocking call chains), 10-30x faster (mmap vs SQLite), typed (`setNumber`, `setBoolean`), optional encryption. AsyncStorage: async everywhere, string-only (manual JSON.stringify/parse), slower. For production apps where auth tokens are read on every API call, synchronous MMKV is significantly cleaner code.

**Q2: Can you use MMKV in Expo Go?**
A2: No. MMKV has native code that requires a custom native build. Expo Go only supports Expo's fixed native shell. For MMKV with Expo: run `npx expo prebuild` to generate `android/ios` folders, then `eas build --profile development` to create a custom development client. Once you have the custom client, MMKV works normally.

**Q3: How do you encrypt sensitive data with MMKV?**
A3: Pass `encryptionKey` to the MMKV constructor: `new MMKV({ id: 'secure', encryptionKey: 'myKey' })`. MMKV uses AES-128 encryption. The encryption key itself should come from a secure source — generate it on first launch and store it in the device's Keychain (iOS) / Keystore (Android) via `expo-secure-store`. This ensures the MMKV data is encrypted and the encryption key is protected by the OS secure enclave.

**Q4: What is the maximum recommended data size for MMKV?**
A4: No hard limit, but practical guideline: MMKV is best for small, frequently-accessed data (< 1-2 MB total). Large data causes the entire mmap file to be large — the whole file is memory-mapped. For datasets > 1MB (caching API responses, product catalogs, order history): use `expo-sqlite` (SQL queries, indexed, paginatable) or WatermelonDB (reactive, offline-first). Think of MMKV as "fast session storage" and SQLite as "app database."

**Q5: How does Zustand + MMKV persistence work?**
A5: Zustand's `persist` middleware can use any storage that implements `getItem`, `setItem`, `removeItem`. Create a `StateStorage` adapter that wraps MMKV's get/set/delete methods. Pass it as `storage: createJSONStorage(() => mmkvAdapter)` to `persist`. Zustand will serialize state to JSON and store it in MMKV on every state change. On app restart, Zustand reads from MMKV and rehydrates the store. Cart contents, user preferences, and filter settings are common candidates.

---

## 🔷 When to Use + When Not to Use
✅ **Use MMKV for:**
- Auth tokens (read on every API call → sync preferred)
- User preferences (theme, language, notification settings)
- Feature flags, app configuration
- Small temporary state (current cart, draft)
- Anything read frequently (< 1MB total)

✅ **Use AsyncStorage for:**
- Projects that need Expo Go compatibility
- Simple cases where async is fine
- Teams familiar with AsyncStorage already

❌ **Use neither for:**
- Large datasets (API cache, order history) → SQLite / WatermelonDB
- Truly sensitive data (private keys, passwords) → expo-secure-store
- Server-side state → just fetch from API

---

## 📊 Visual Diagram

```
STORAGE COMPARISON:
──────────────────────────────────────────────────────
  Feature         │ MMKV      │ AsyncStorage │ SQLite
  ────────────────┼───────────┼──────────────┼────────
  Speed (read)    │ ~0.1ms    │ ~5ms         │ ~2ms
  API type        │ Sync + Async │ Async only │ Async
  Data types      │ Typed     │ String only  │ Types
  Max data        │ ~1MB ideal│ No limit     │ Unlimited
  Encryption      │ Optional  │ No           │ Optional
  Expo Go         │ ❌        │ ✅           │ ✅
  Best for        │ Tokens,   │ Simple data, │ Datasets,
                  │ prefs     │ Expo Go apps │ caching

WHEN TO CHOOSE:
──────────────────────────────────────────────────────
  Auth token → MMKV (sync, fast, encrypted)
  User settings → MMKV (small, frequent)
  Recent search → MMKV or AsyncStorage
  Order history → SQLite (large, queryable)
  Product cache → SQLite or Redux Toolkit Query
  Passwords/keys → expo-secure-store (Keychain)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AsyncStorage | Async key-value storage | Async key-value storage |
| MMKV | Fast synchronous key-value storage | Fast sync key-value storage |
| mmap | Memory-mapped files | Memory-mapped files |
| Persist | Survive app restart | App restart के बाद भी data रहे |
| Synchronous | No await needed | await नहीं चाहिए |
| Encryption | AES-128 with key | AES-128 encryption |
| Zustand persist | Zustand state stored in storage | Zustand state storage में |

---

## ⚡ 3-Line Summary
**English:**
1. AsyncStorage = async, string-only, Expo Go compatible, slower (SQLite); MMKV = synchronous, typed, 10-30x faster (mmap), needs native build.
2. Use MMKV for auth tokens, preferences, and frequently-read small data; AsyncStorage for simpler apps or Expo Go compatibility.
3. For large datasets (order history, product cache): use `expo-sqlite` or WatermelonDB — neither AsyncStorage nor MMKV is a database.

**Hindi:**
1. AsyncStorage = async, string-only, Expo Go compatible, slower; MMKV = synchronous, typed, 10-30x faster, native build चाहिए।
2. MMKV: auth tokens, preferences, frequent small data; AsyncStorage: simple apps या Expo Go।
3. Large datasets (order history, cache): `expo-sqlite` या WatermelonDB — दोनों database नहीं हैं।

---

## ➡️ Next Topic
**90. React Query in React Native** — server state management, caching, background refetch।
