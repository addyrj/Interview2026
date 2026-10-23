# 75. Authentication Flow with Navigation
# हिंदी में: Navigation के साथ Authentication Flow
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
An **auth flow** in React Navigation conditionally renders either the Auth Stack (Login/Signup) or the App Stack (Home/Profile) based on whether the user is logged in. The key: when auth state changes (login/logout), React Navigation automatically swaps stacks — no `navigation.navigate()` needed. Store auth state in Zustand/Context, persist token in MMKV.

## 🔵 सरल परिभाषा (Hindi)
React Navigation में **auth flow** user logged in है या नहीं उस पर based Auth Stack (Login/Signup) या App Stack (Home/Profile) conditionally render करता है। Key: auth state change होने पर (login/logout) React Navigation automatically stacks swap करता है — `navigation.navigate()` की जरूरत नहीं। Auth state Zustand/Context में, token MMKV में persist।

---

## 🔴 Problem it Solves
```
AUTH FLOW CHALLENGES:
❌ User taps back after login → goes back to Login screen (wrong!)
❌ User closes app while logged in → sees Login screen on reopen (wrong!)
❌ User logs out → can still press back to access Home screen (security!)
❌ Deep link to protected screen → must redirect to Login first

CORRECT BEHAVIOR:
✅ After login: Home screen, Back button shows nothing (stack reset)
✅ After app restart: check stored token → go directly to Home
✅ After logout: Login screen, Back button doesn't show Home
✅ Deep link to Profile when not logged in → Login first → Profile
```

## 🔴 यह क्यों बना? (Hindi)
```
Login के बाद back button Login screen दिखाना गलत है।
App reopen पर Login screen दिखाना (already logged in) wrong।
Logout के बाद back button Home accessible होना security issue।
React Navigation's conditional stack pattern यह सब fix करता है।
```

---

## 🟢 How it Works — Step by Step

```
AUTH FLOW PATTERN:
──────────────────────────────────────────────────────
  Step 1 → App starts → check MMKV for stored token
           isLoading: true

  Step 2 → Token found → isLoggedIn = true
           Token not found → isLoggedIn = false
           isLoading: false

  Step 3 → NavigationContainer renders:
           if isLoading → <SplashScreen />
           if !isLoading && !isLoggedIn → <AuthStack />
           if !isLoading && isLoggedIn → <AppStack />

  Step 4 → User enters credentials → API call → success
           Set token in MMKV
           Set isLoggedIn = true in auth store

  Step 5 → React Navigation detects isLoggedIn changed
           Automatically switches from AuthStack to AppStack
           AuthStack is UNMOUNTED (back button won't reach it)

  Step 6 → User taps Logout
           Delete token from MMKV
           Set isLoggedIn = false
           React Navigation unmounts AppStack, mounts AuthStack
           Login screen appears (back button won't reach Home)

  WHY THIS WORKS:
  React Navigation's navigator is CONDITIONAL
  When auth state changes → navigator re-renders
  → Different screens are in the tree → previous screens are gone!
```

## 🟢 कैसे काम करता है? (Hindi)
```
Conditional navigation: isLoggedIn → App screens, else → Auth screens।
Login: MMKV में token save → isLoggedIn = true → Auto switch।
Logout: MMKV से token delete → isLoggedIn = false → Auth screens।
Back button: previous stack unmounted → history clear।
```

---

## 🟡 Real World Example
**Paytm app flow:** First time: `OnboardingStack` (phone entry). After OTP: `MainStack` (tabs: Home, Scan, History, Profile). On app reopen with session: directly `MainStack`. Session expired: `AuthStack` with message "Session expired, please log in again". The key: when session expires (401 from API), Paytm's auth handler sets `isLoggedIn = false` → whole `MainStack` disappears → `AuthStack` appears — no back button to Home.

## 🟡 Real Example Hindi मे
**Paytm:** First time → OTP screen। Auth success → MainStack (tabs)। App reopen with session → directly MainStack। 401 error → `isLoggedIn = false` → MainStack disappear → AuthStack। Back button History या Home कभी नहीं जाएगा।

---

## 💻 Code Example — Complete Auth Flow

```jsx
// ── 1. Auth Store (Zustand) ──────────────────────────────────────
// authStore.ts
import { create } from 'zustand';
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV({ id: 'auth' });

type AuthStore = {
  isLoggedIn: boolean;
  isLoading: boolean;
  user: { id: string; name: string; phone: string } | null;
  initializeAuth: () => void;
  login: (token: string, user: any) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthStore>((set) => ({
  isLoggedIn: false,
  isLoading: true,    // true while checking stored token
  user: null,

  // Called on app start — check for existing session
  initializeAuth: () => {
    const token = storage.getString('authToken');
    const userStr = storage.getString('user');
    const user = userStr ? JSON.parse(userStr) : null;

    set({
      isLoggedIn: !!token,
      user,
      isLoading: false,  // done checking
    });
  },

  // Called after successful login API
  login: (token, user) => {
    storage.set('authToken', token);
    storage.set('user', JSON.stringify(user));
    set({ isLoggedIn: true, user, isLoading: false });
  },

  // Called on logout button press or 401 response
  logout: () => {
    storage.delete('authToken');
    storage.delete('user');
    set({ isLoggedIn: false, user: null });
  },
}));

// ── 2. Navigation (App.tsx) ──────────────────────────────────────
// App.tsx
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, ActivityIndicator } from 'react-native';
import { useAuthStore } from './authStore';

// Auth screens
import LoginScreen from './screens/LoginScreen';
import OTPScreen from './screens/OTPScreen';
import OnboardingScreen from './screens/OnboardingScreen';

// App screens
import HomeScreen from './screens/HomeScreen';
import ProfileScreen from './screens/ProfileScreen';
import ProductDetailScreen from './screens/ProductDetailScreen';

const AuthStack = createNativeStackNavigator();
const AppStack = createNativeStackNavigator();

// Auth screens (not logged in)
function AuthNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="OTP" component={OTPScreen} />
      <AuthStack.Screen name="Onboarding" component={OnboardingScreen} />
    </AuthStack.Navigator>
  );
}

// App screens (logged in)
function AppNavigator() {
  return (
    <AppStack.Navigator>
      <AppStack.Screen name="Home" component={HomeScreen} />
      <AppStack.Screen name="Profile" component={ProfileScreen} />
      <AppStack.Screen name="ProductDetail" component={ProductDetailScreen} />
    </AppStack.Navigator>
  );
}

// Root Navigator — the key auth flow logic
function RootNavigator() {
  const { isLoggedIn, isLoading } = useAuthStore();

  // Show splash/loading while checking stored token
  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#f97316" />
      </View>
    );
  }

  // KEY: Conditionally render based on auth state
  // When isLoggedIn changes, React Navigation automatically swaps!
  return isLoggedIn ? <AppNavigator /> : <AuthNavigator />;
}

export default function App() {
  const initializeAuth = useAuthStore(state => state.initializeAuth);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <NavigationContainer>
      <RootNavigator />
    </NavigationContainer>
  );
}

// ── 3. Login Screen ───────────────────────────────────────────────
// LoginScreen.tsx
import { useAuthStore } from '../authStore';
import { View, Text, TouchableOpacity, TextInput, StyleSheet, Alert } from 'react-native';

function LoginScreen({ navigation }) {
  const login = useAuthStore(state => state.login);
  const [phone, setPhone] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      // Your actual login API call
      const response = await loginAPI({ phone });
      // On success: update auth store → navigator automatically switches!
      login(response.token, response.user);
      // NO navigation.navigate('Home') needed!
      // The conditional navigator handles it automatically.
    } catch (error) {
      Alert.alert('Login Failed', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>
      <TextInput
        style={styles.input}
        placeholder="Phone Number"
        keyboardType="phone-pad"
        value={phone}
        onChangeText={setPhone}
      />
      <TouchableOpacity style={styles.button} onPress={handleLogin}>
        <Text style={styles.buttonText}>Send OTP</Text>
      </TouchableOpacity>
    </View>
  );
}

// ── 4. Logout (from any screen) ───────────────────────────────────
// ProfileScreen.tsx
function ProfileScreen() {
  const logout = useAuthStore(state => state.logout);

  return (
    <View style={styles.container}>
      <Text>Profile</Text>
      <TouchableOpacity onPress={logout} style={styles.logoutButton}>
        <Text>Logout</Text>
        {/* Tapping this: logout() → isLoggedIn = false → AuthNavigator shown */}
        {/* Back button CANNOT reach ProfileScreen anymore! */}
      </TouchableOpacity>
    </View>
  );
}

// ── 5. Auto-logout on 401 ─────────────────────────────────────────
// api.ts — axios interceptor
import axios from 'axios';

const api = axios.create({ baseURL: 'https://api.myapp.com' });

api.interceptors.request.use((config) => {
  const token = storage.getString('authToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Session expired — auto logout!
      useAuthStore.getState().logout();
      // NavigationContainer auto-switches to AuthNavigator
    }
    return Promise.reject(error);
  }
);

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: '700', marginBottom: 24 },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 14, marginBottom: 16 },
  button: { backgroundColor: '#f97316', padding: 16, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '700' },
  logoutButton: { padding: 16, borderRadius: 8, borderWidth: 1, alignItems: 'center', marginTop: 16 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Back after logout | Hardware back → same (AuthStack) | Swipe back → same (AuthStack) |
| Biometric login | Fingerprint / Face | Face ID / Touch ID |
| Deep links | Intent filters in AndroidManifest | Universal Links in Info.plist |
| Session storage | MMKV / Keystore | MMKV / Keychain |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
# expo-secure-store for token (more secure than MMKV for sensitive tokens)
expo install expo-secure-store
# import * as SecureStore from 'expo-secure-store';
# await SecureStore.setItemAsync('token', token);

# Expo Router: app/(auth)/_layout.tsx + app/(tabs)/_layout.tsx
# File-based conditional routes
```

CLI way:
```bash
# react-native-keychain for secure token storage
npm install react-native-keychain
# Similar concept — just different secure storage
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using navigation.navigate() for auth state changes
```jsx
// WRONG: Manually navigating — back button still shows Login!
const handleLoginSuccess = () => {
  setToken(token);
  navigation.navigate('Home');  // ❌ Login is still in the stack!
};

// CORRECT: Update auth state — navigator switches automatically
const handleLoginSuccess = () => {
  login(token, user);  // auth store update → conditional navigator renders Home
  // NO navigation.navigate() — Auth stack is UNMOUNTED entirely
};
```

❌ **Mistake 2:** Not handling the loading state
```jsx
// WRONG: Show Login screen briefly before checking stored token
function App() {
  const { isLoggedIn } = useAuthStore();  // isLoggedIn starts false!
  return isLoggedIn ? <AppNavigator /> : <AuthNavigator />;
  // User with valid token sees Login flash briefly!
}

// CORRECT: Show loading/splash until check is done
function App() {
  const { isLoggedIn, isLoading } = useAuthStore();
  if (isLoading) return <SplashScreen />;  // wait for token check
  return isLoggedIn ? <AppNavigator /> : <AuthNavigator />;
}
```

❌ **Mistake 3:** Not handling 401 responses globally
```jsx
// WRONG: Each screen handles 401 separately
// → Some screens miss it → user stuck with expired session

// CORRECT: Axios/Fetch interceptor handles 401 globally
// One place handles all unauthorized responses
// → Automatic logout everywhere
```

---

## 🧠 Tricky Interview Question

**Q: User is on the HomeScreen and their session expires (API returns 401). Without the user doing anything, they should see the Login screen. How do you implement this?**

**Answer:** Set up an Axios (or Fetch) response interceptor that catches all 401 responses. In the interceptor: `useAuthStore.getState().logout()` — call the store's logout action directly (outside React, using Zustand's `getState()`). The logout action: deletes token from MMKV, sets `isLoggedIn = false`. The `RootNavigator` component reads `isLoggedIn` from Zustand. When it becomes `false`, React Navigation unmounts `AppNavigator` and mounts `AuthNavigator`. The user sees the Login screen — no button press needed. Key: `useAuthStore.getState()` is Zustand's way to access store outside React components (in interceptors, utilities).

---

## ⚫ Interview Questions + Answers

**Q1: Why do we use conditional navigation for auth instead of navigating programmatically?**
A1: Programmatic navigation (`navigation.navigate('Home')`) pushes a new screen onto the stack — the Login screen stays in history. User can press Back to return to Login. With conditional navigation: AuthStack and AppStack are different navigators. When `isLoggedIn` changes, the entire wrong navigator is UNMOUNTED and the correct one MOUNTED. No history of the previous state exists. This is the correct pattern for auth — the two states (logged-in vs logged-out) should never coexist in the navigation history.

**Q2: Where should you store the auth token?**
A2: For most apps: MMKV (`react-native-mmkv`) — fast, synchronous, can be encrypted. For high-security apps (banking, fintech): `expo-secure-store` (Expo) or `react-native-keychain` (CLI) — stores in iOS Keychain / Android Keystore, survives app reinstall on iOS, hardware-backed encryption. Never store sensitive tokens in AsyncStorage (no encryption) or Redux state (no persistence).

**Q3: How do you persist auth state across app restarts?**
A3: On login: save token to MMKV/Keychain. On app startup (`useEffect` in App.tsx): read token from storage, if exists set `isLoggedIn = true`, if not set to `false`. The `isLoading` flag prevents the login screen from flashing while checking. The `initializeAuth()` function handles this check. Token expires: on next API call, 401 received → interceptor calls `logout()` → `isLoggedIn = false` → Login screen.

**Q4: How do you handle deep linking to a protected screen?**
A4: React Navigation's `linking` config maps URLs to screens. If the user deep links to `myapp://profile` while not logged in: the AuthNavigator is active, `Profile` screen isn't in it. React Navigation can't navigate there. Solution: (1) Store the intended deep link URL in state during auth. After successful login, navigate to the intended URL. (2) Or, use a "redirect after login" pattern: save the deep link path, after login, call `navigation.navigate(savedPath)`.

**Q5: What is the `isLoading` state in auth flow?**
A5: When the app starts, auth state is unknown (`isLoggedIn = false` by default). Checking the stored token (even MMKV sync) takes a render cycle. Without `isLoading`: user sees Login screen for one frame before switching to Home — the "flash of unauthenticated content" (FOUC equivalent). With `isLoading = true` initially: app shows SplashScreen or ActivityIndicator until `initializeAuth()` completes. `isLoading` starts `true`, becomes `false` after token check. This prevents the login screen flash.

---

## 🔷 When to Use + When Not to Use
✅ **This pattern works for:**
- Standard login/logout flow
- Session expiry (401 auto-logout)
- Multiple user roles (show different stacks per role)
- Onboarding flows (show onboarding only on first install)

❌ **This pattern doesn't directly handle:**
- Partial auth (guest user with limited access) — needs more complex logic
- Multi-account switching — needs stack for each account
- Social login (OAuth flows) — need to handle redirect from browser back to app

---

## 📊 Visual Diagram

```
AUTH FLOW ARCHITECTURE:
──────────────────────────────────────────────────────
  App Start:
  isLoading=true → Splash/Loading Screen
       │
       ▼ initializeAuth() checks MMKV
       │
  ┌────┴────────────────────┐
  │                         │
  Token NOT found          Token found
  isLoggedIn=false         isLoggedIn=true
       │                         │
       ▼                         ▼
  AuthNavigator             AppNavigator
  ┌─────────────┐          ┌─────────────┐
  │ Login       │          │ Home        │
  │ OTP         │          │ Profile     │
  │ Onboarding  │          │ Settings    │
  └─────────────┘          └─────────────┘
  Back = exits app         Back = exits app (no Login!)

  LOGIN SUCCESS:
  login(token, user) → isLoggedIn=true → AppNavigator MOUNTED
                                          AuthNavigator UNMOUNTED
  (automatic! no navigation.navigate needed)

  LOGOUT / 401:
  logout() → isLoggedIn=false → AuthNavigator MOUNTED
                                  AppNavigator UNMOUNTED
  (automatic! no history of Home/Profile accessible)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Auth Flow | Login/logout navigation pattern | Login/logout navigation pattern |
| Conditional Navigator | Render different stacks based on condition | Condition के अनुसार different stacks |
| isLoggedIn | Auth state flag | Auth state flag |
| isLoading | Waiting for auth check | Auth check के लिए wait |
| Token | Session authentication credential | Session auth credential |
| Auto-logout | 401 → logout automatically | 401 → automatic logout |
| initializeAuth | Check stored token on startup | Startup पर stored token check |

---

## ⚡ 3-Line Summary
**English:**
1. Use conditional navigation — render `AuthNavigator` or `AppNavigator` based on `isLoggedIn` state; when it changes, React Navigation auto-swaps stacks (no `navigate()` needed).
2. Always have an `isLoading` state while checking stored token on startup — prevents login screen flash for already-authenticated users.
3. Handle 401 globally in Axios interceptor calling `authStore.getState().logout()` — any expired session automatically returns to Login, from any screen.

**Hindi:**
1. Conditional navigation: `isLoggedIn` के based `AuthNavigator` या `AppNavigator` render; state change पर React Navigation auto-swap करता है।
2. Startup पर stored token check के दौरान `isLoading` state रखो — already-logged-in users को Login screen flash नहीं होगा।
3. Axios interceptor में 401 globally handle करो `authStore.getState().logout()` से — किसी भी screen से expired session Login पर redirect।

---

## ➡️ Next Topic
**76. Navigation Lifecycle** — screen focus/blur events, navigation state, back button handling।
