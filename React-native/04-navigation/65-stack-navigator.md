# 65. Stack Navigator
# हिंदी में: Stack Navigator — Screen Navigation
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Stack Navigator** is the most fundamental React Navigation navigator — it manages screens as a stack (like a pile of cards). Navigate to a new screen → pushes it on top. Press back → pops it off. Each screen remembers its own state. Implements the standard mobile navigation pattern: native-like push/pop transitions, header bar with back button, gesture-to-go-back.

## 🔵 सरल परिभाषा (Hindi)
**Stack Navigator** React Navigation का सबसे basic navigator है — screens को stack (cards की pile) की तरह manage करता है। New screen navigate करो → stack पर push। Back press करो → pop। हर screen अपनी state याद रखती है। Standard mobile navigation pattern: native push/pop transitions, header with back button, gesture-to-go-back।

---

## 🔴 Problem it Solves
```
MOBILE NAVIGATION NEEDS:
  Home → Product Detail → Reviews → User Profile
  Back from User Profile → Reviews (state preserved!)
  Back from Reviews → Product Detail (state preserved!)
  Back from Product Detail → Home

STACK NAVIGATOR PROVIDES:
  ✅ Screen history (back button works)
  ✅ Native transitions (slide on iOS, fade/slide on Android)
  ✅ Header bar with title + back button (automatic)
  ✅ Gesture-to-go-back (swipe from left edge on iOS)
  ✅ Screen state preservation (scroll position, form input)
  ✅ Deep linking support (URL → specific screen)

WITHOUT STACK NAVIGATOR:
  Managing navigation manually = reimplementing the wheel
  Custom back button logic, screen state management...
```

## 🔴 यह क्यों बना? (Hindi)
```
Mobile में screens stack की तरह काम करती हैं।
Stack Navigator: navigate → push, back → pop।
Native transitions, header, back gesture — सब automatic।
Manual navigation = बहुत काम। Stack Navigator = simple।
```

---

## 🟢 How it Works — Step by Step

```
STACK NAVIGATOR INTERNALS:
──────────────────────────────────────────────────────
  Stack = array of route objects
  Initial stack: [{ name: 'Home', params: {} }]

  navigate('ProductDetail', { id: '123' }):
  Stack: [Home, ProductDetail]
  Screen: ProductDetail (top = visible)

  navigate('Reviews', { productId: '123' }):
  Stack: [Home, ProductDetail, Reviews]
  Screen: Reviews (top = visible)

  goBack():
  Stack: [Home, ProductDetail]
  Screen: ProductDetail (ProductDetail's state preserved!)

  navigation.replace('Login'):
  Stack: [Login]    ← replaces current, no back button

  navigation.reset({ index: 0, routes: [{ name: 'Home' }] }):
  Stack: [Home]     ← clears entire history

  SCREEN TRANSITIONS:
  iOS: slide from right (push), slide to right (pop)
  Android: default (fade + slide up)
  Custom: animation: 'slide_from_bottom' etc.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Stack = array of routes।
navigate() → push to stack top।
goBack() → pop from stack।
replace() → current screen swap (no back)।
reset() → entire stack clear।
```

---

## 🟡 Real World Example
**Zomato app:** Home Screen (restaurant list) → Restaurant Detail Screen (menu) → Item Customization Screen (toppings/sizes) → Cart Screen → Payment Screen. Each navigate() pushes to stack. Back from Payment → Cart (with items still in cart form). Back from Cart → Item Customization (selections preserved). This "breadcrumb trail" is exactly what Stack Navigator manages. iOS users can also swipe from left to go back (gesture navigation built-in).

## 🟡 Real Example Hindi मे
**Zomato:** Home → Restaurant Detail → Item Customize → Cart → Payment। हर navigate() stack पर push। Back करो → previous screen state preserved। iOS में left swipe = go back (built-in gesture)। यह सब Stack Navigator automatically handle।

---

## 💻 Code Example — Basic Setup

```tsx
// App.tsx — Root setup
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from './screens/HomeScreen';
import ProductDetailScreen from './screens/ProductDetailScreen';
import ReviewsScreen from './screens/ReviewsScreen';

// 1. DEFINE TYPE for all routes (TypeScript — prevents typos in navigate())
type RootStackParamList = {
  Home: undefined;                        // no params
  ProductDetail: { productId: string; productName: string };  // required params
  Reviews: { productId: string };        // required params
  Settings: undefined;
};

// 2. CREATE navigator instance
const Stack = createNativeStackNavigator<RootStackParamList>();

// 3. DEFINE navigation structure
export default function App() {
  return (
    <NavigationContainer>              {/* Required root component — provides navigation context */}
      <Stack.Navigator
        initialRouteName="Home"        {/* Which screen shows first */}
        screenOptions={{               {/* Default options for ALL screens */}
          headerStyle: { backgroundColor: '#e23744' },
          headerTintColor: '#fff',     {/* Back arrow + title color */}
          headerTitleStyle: { fontWeight: '700' },
          animation: 'slide_from_right',  {/* iOS default anyway, explicit for Android */}
        }}
      >
        {/* Each Screen = one page in the app */}
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Restaurants' }}   {/* Override header title */}
        />
        <Stack.Screen
          name="ProductDetail"
          component={ProductDetailScreen}
          options={({ route }) => ({           {/* Dynamic title from params */}
            title: route.params.productName,
          })}
        />
        <Stack.Screen
          name="Reviews"
          component={ReviewsScreen}
          options={{
            title: 'Reviews',
            presentation: 'modal',    {/* Slides up from bottom (iOS sheet) */}
          }}
        />
        <Stack.Screen
          name="Settings"
          component={SettingsScreen}
          options={{
            headerShown: false,       {/* No header for this screen */}
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

```tsx
// HomeScreen.tsx — navigating to other screens
import React from 'react';
import { View, Text, Pressable, FlatList } from 'react-native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../App';

type HomeNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen({ navigation }: { navigation: HomeNavigationProp }) {
  const products = [
    { id: '1', name: 'Butter Chicken', price: 350 },
    { id: '2', name: 'Biryani', price: 280 },
  ];

  return (
    <FlatList
      data={products}
      keyExtractor={item => item.id}
      renderItem={({ item }) => (
        <Pressable
          onPress={() => navigation.navigate('ProductDetail', {
            productId: item.id,
            productName: item.name,
          })}
        >
          <Text>{item.name} — ₹{item.price}</Text>
        </Pressable>
      )}
    />
  );
}
```

```tsx
// ProductDetailScreen.tsx — receiving params
import React from 'react';
import { View, Text, Pressable } from 'react-native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RouteProp } from '@react-navigation/native';
import type { RootStackParamList } from '../App';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'ProductDetail'>;
  route: RouteProp<RootStackParamList, 'ProductDetail'>;
};

export default function ProductDetailScreen({ navigation, route }: Props) {
  const { productId, productName } = route.params;  // type-safe!

  return (
    <View>
      <Text>{productName} (ID: {productId})</Text>

      <Pressable onPress={() => navigation.navigate('Reviews', { productId })}>
        <Text>View Reviews</Text>
      </Pressable>

      {/* Goes back to previous screen (Home) */}
      <Pressable onPress={() => navigation.goBack()}>
        <Text>← Back</Text>
      </Pressable>

      {/* Update current screen's params (updates header title too) */}
      <Pressable onPress={() => navigation.setParams({ productName: 'Updated Name' })}>
        <Text>Update Title</Text>
      </Pressable>
    </View>
  );
}
```

## 💻 Code Example — Advanced (Custom Header + Nested)

```tsx
// Advanced: Custom header button, nested navigators
import React, { useLayoutEffect } from 'react';
import { View, Pressable, Text } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// NESTED: Tab inside Stack
// Common pattern: Tab is the "logged in" state, Auth screens use Stack
function MainTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        {/* Full-screen tab layout */}
        <Stack.Screen
          name="Main"
          component={MainTabs}
          options={{ headerShown: false }}  {/* Tab has its own header */}
        />
        {/* Screens that overlay the tabs (modals, details) */}
        <Stack.Screen name="ProductDetail" component={ProductDetailScreen} />
        <Stack.Screen
          name="Camera"
          component={CameraScreen}
          options={{
            presentation: 'fullScreenModal',   // full-screen modal
            headerShown: false,
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// CUSTOM HEADER BUTTONS — must use useLayoutEffect
function CartScreen({ navigation }) {
  useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <Pressable
          onPress={() => navigation.navigate('Checkout')}
          style={{ marginRight: 16 }}
        >
          <Text style={{ color: '#e23744', fontWeight: '600' }}>Checkout</Text>
        </Pressable>
      ),
      headerLeft: () => (
        <Pressable onPress={() => navigation.goBack()}>
          <Text>✕</Text>
        </Pressable>
      ),
    });
  }, [navigation]);

  return <View><Text>Cart items...</Text></View>;
}

// NAVIGATION RESET (after login — clear auth stack)
function handleLoginSuccess(navigation) {
  navigation.reset({
    index: 0,
    routes: [{ name: 'Main' }],   // Clear all history, start fresh at Main
  });
}

// NAVIGATION ACTIONS SUMMARY:
// navigation.navigate('Screen', params)    → push (or show existing)
// navigation.push('Screen', params)        → always push (even if exists)
// navigation.replace('Screen', params)     → swap current (no back)
// navigation.goBack()                      → pop
// navigation.popToTop()                    → pop all, go to root
// navigation.reset({ index, routes })      → replace entire stack
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default transition | Fade + slide up | Slide from right |
| Back gesture | Swipe from left edge | Swipe from left edge (same) |
| Physical back button | System back button | Only swipe gesture |
| Header style | Slightly different default font | Native look |
| `presentation: 'modal'` | Slides up | Slides up (native sheet) |
| `headerBackVisible` | Controlled by RN | Controlled by RN |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
npx expo install @react-navigation/native @react-navigation/native-stack
npx expo install react-native-screens react-native-safe-area-context
```

CLI way:
```bash
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context
# iOS: cd ios && pod install
# android: auto-linked
```

Both need this in `App.tsx` (or `index.js`):
```tsx
// Enable react-native-screens (better performance, native screen containers)
import { enableScreens } from 'react-native-screens';
enableScreens();

// Wrap with SafeAreaProvider at app root
import { SafeAreaProvider } from 'react-native-safe-area-context';
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `navigate()` for login → home transition
```tsx
// WRONG: navigate keeps login screen in stack (back button goes back to login!)
navigation.navigate('Home');

// CORRECT: reset clears login from history
navigation.reset({ index: 0, routes: [{ name: 'Home' }] });
```

❌ **Mistake 2:** Passing functions as params
```tsx
// WRONG: Functions are not serializable, causes warnings + issues
navigation.navigate('Screen', {
  onComplete: () => console.log('done'),  // ❌ function in params!
});

// CORRECT: Use navigation.setParams() or a shared store (Zustand) for callbacks
// Or use event emitter: navigation.getParent()?.dispatch(...)
```

❌ **Mistake 3:** Forgetting `headerShown: false` when nesting Tab inside Stack
```tsx
// WRONG: Double header — one from Stack.Navigator + one from Tab.Navigator
<Stack.Screen name="Main" component={MainTabs} />

// CORRECT: Hide the Stack header for the Tab screen
<Stack.Screen
  name="Main"
  component={MainTabs}
  options={{ headerShown: false }}  // Tab Navigator has its own header
/>
```

---

## 🧠 Tricky Interview Question

**Q: User logs in → app navigates to Home using `navigation.navigate('Home')`. User presses back. They're back on the Login screen. How do you prevent this?**

**Answer:** `navigation.navigate()` pushes to the stack (or activates existing screen), but the login screen stays in the history. Solution: use `navigation.reset()` after successful login:
```tsx
navigation.reset({
  index: 0,
  routes: [{ name: 'Home' }],
});
```
This replaces the entire navigation stack with just `Home` — no back button to Login. Alternatively, use `navigation.replace('Home')` which replaces only the current screen (Login), but if there were screens before Login in the stack (like a Splash or Onboarding), they'd still be accessible. `reset` is the safest for authentication flows. For even cleaner auth: use conditional rendering of navigators based on `isLoggedIn` state (recommended pattern in React Navigation docs) — the Auth stack and App stack are separate, so navigation between them is not stack-based at all.

---

## ⚫ Interview Questions + Answers

**Q1: What is a Stack Navigator?**
A1: Stack Navigator manages screens as a push/pop stack — navigate to new screen pushes it on top; pressing back pops it off. It provides native-like transitions (slide on iOS, material on Android), an automatic header with back button, and iOS swipe-to-go-back gesture. Created with `createNativeStackNavigator()` from `@react-navigation/native-stack`.

**Q2: What is the difference between `navigate`, `push`, and `replace`?**
A2: `navigate('Screen')` — if Screen is already in the stack, activates it without duplicating (go to it). If not, pushes new instance. `push('Screen')` — always pushes a new instance even if Screen is already in stack (useful for product detail → related product → product detail). `replace('Screen')` — swaps the current screen with the new one, no back button to the replaced screen (use after OTP, after login, when the previous screen becomes irrelevant).

**Q3: How do you set custom header buttons?**
A3: Use `navigation.setOptions()` inside `useLayoutEffect` (not `useEffect` — layout happens synchronously so the header updates before rendering): `navigation.setOptions({ headerRight: () => <ShareButton />, headerLeft: () => <CancelButton /> })`. Use `useLayoutEffect` to avoid the flash where the default header briefly shows before your custom buttons appear.

**Q4: What is `initialRouteName` and how is it different from navigation.reset()?**
A4: `initialRouteName` is set declaratively in `Stack.Navigator` — it defines which screen is the root/bottom of the stack on initial app launch. `navigation.reset()` is called imperatively at runtime to replace the stack with a new structure. Use `reset()` for events like login/logout where you want to change the navigation root dynamically. `initialRouteName` is static configuration.

**Q5: How does nesting Stack Navigator inside Tab Navigator work?**
A5: Each tab can have its own Stack Navigator, maintaining separate navigation history per tab. Switching tabs: stack history is preserved (going back to that tab resumes where you left off). Example: HomeTab has its own Stack (Home → ProductDetail → Reviews), ProfileTab has its Stack (Profile → EditProfile). Navigating between stacks: use a common parent navigator or pass the parent's `navigation` to navigate to a screen outside the current stack.

---

## 🔷 When to Use + When Not to Use
✅ **Use Stack Navigator for:**
- Any screen that requires navigation history (back button)
- Detail screens (Product Detail, User Profile, Article)
- Forms that are part of a flow (Step 1 → Step 2 → Step 3)
- Auth flow (Login → OTP → Home)

✅ **Use Tab Navigator (bottom tabs) for:**
- Top-level app sections (Home, Search, Orders, Profile)
- Screens of equal importance, always accessible

✅ **Use Drawer Navigator for:**
- Side menu with navigation links
- Admin panels, content-heavy apps

---

## 📊 Visual Diagram

```
STACK NAVIGATOR — Push/Pop Model:
──────────────────────────────────────────────────────

  Initial:
  ┌───────────┐
  │   HOME    │  ← top (visible)
  └───────────┘

  navigate('ProductDetail', { id: '1' }):
  ┌──────────────────┐
  │  PRODUCT DETAIL  │  ← top (visible) + back button shows
  ├──────────────────┤
  │      HOME        │  ← preserved in stack
  └──────────────────┘

  navigate('Reviews'):
  ┌─────────────┐
  │   REVIEWS   │  ← top (visible)
  ├─────────────┤
  │  PRODUCT    │
  ├─────────────┤
  │    HOME     │
  └─────────────┘

  goBack() / back button:
  ┌─────────────┐
  │   PRODUCT   │  ← back (Reviews state gone)
  ├─────────────┤
  │    HOME     │
  └─────────────┘

  navigation.reset({ index: 0, routes: [{ name: 'Home' }] }):
  ┌───────────┐
  │   HOME    │  ← clean slate, no history
  └───────────┘

NAVIGATION ACTIONS QUICK REFERENCE:
  navigate → push or activate existing
  push    → always push new
  replace → swap current (no back to previous)
  goBack  → pop current
  popToTop → pop all, go to root screen
  reset   → replace entire stack
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stack | Ordered list of screens | Screens की ordered list |
| push | Add screen to top of stack | Stack के top पर screen add |
| pop | Remove top screen from stack | Stack के top से screen remove |
| replace | Swap current screen | Current screen swap |
| reset | Replace entire stack | पूरी stack replace |
| params | Data passed to new screen | New screen को data pass करना |
| initialRouteName | Starting screen at app launch | App launch पर पहली screen |
| headerShown | Show/hide navigation header | Navigation header show/hide |
| presentation | Screen animation style | Screen animation style |

---

## ⚡ 3-Line Summary
**English:**
1. Stack Navigator manages screens as a push/pop stack — `navigate()` pushes, back button pops — providing native transitions and automatic header with back button.
2. Use `navigation.reset()` after login/logout to clear navigation history; use `replace()` when the previous screen (OTP, loading) should not be accessible via back.
3. TypeScript: define `RootStackParamList` type for all routes — enables autocomplete and type-safe params in both `navigate()` and `route.params`.

**Hindi:**
1. Stack Navigator screens को push/pop stack की तरह manage — `navigate()` push, back pop — native transitions और automatic header।
2. Login/logout के बाद `navigation.reset()` use करो — history clear। Back नहीं जाना तो `replace()` use करो।
3. TypeScript: `RootStackParamList` define करो — type-safe `navigate()` और `route.params`।

---

## ➡️ Next Topic
**66. Tab Navigator** — Bottom tab navigation, tabBarIcon, badge count।
