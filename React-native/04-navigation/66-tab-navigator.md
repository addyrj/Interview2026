# 66. Tab Navigator (Bottom Tabs)
# हिंदी में: Tab Navigator — Bottom Navigation
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Bottom Tab Navigator** creates the standard mobile bottom navigation bar — tabs at the bottom of the screen (Home, Search, Orders, Profile). Each tab maintains its own navigation stack independently. Tapping a tab switches to that screen; tapping the same tab again scrolls to top or resets to root of that tab's stack. The most-used navigation pattern in mobile apps.

## 🔵 सरल परिभाषा (Hindi)
**Bottom Tab Navigator** standard mobile bottom navigation bar create करता है — screen के bottom पर tabs (Home, Search, Orders, Profile)। हर tab अपना navigation stack independently maintain करती है। Tab tap → उस screen पर switch। Same tab tap → top पर scroll या root screen पर reset। Mobile apps में सबसे ज़्यादा use होने वाला navigation pattern।

---

## 🔴 Problem it Solves
```
TOP-LEVEL NAVIGATION NEEDS:
  Zomato: Home | Search | Orders | Cart | Profile
  Swiggy: Home | Search | Offers | Account
  PhonePe: Home | Transactions | Scan | Rewards

WITHOUT TAB NAVIGATOR:
  Only Stack = must navigate to Home/Search/Orders explicitly
  No persistent bottom bar
  User loses current stack when switching "sections"
  No badge counts (cart: 3 items)

TAB NAVIGATOR PROVIDES:
  ✅ Persistent bottom bar always visible
  ✅ Each tab = separate navigation stack (independent history!)
  ✅ Tab badge numbers (cart count, notification count)
  ✅ Custom icons per tab
  ✅ Tab state preserved when switching tabs
  ✅ Active/inactive tab styles
```

---

## 🟢 How it Works — Step by Step

```
TAB NAVIGATOR STATE MANAGEMENT:
──────────────────────────────────────────────────────
  Each tab has its own Stack:
  HomeTab Stack:    [Home → ProductDetail → Reviews]
  SearchTab Stack:  [Search → Results]
  OrdersTab Stack:  [Orders]
  ProfileTab Stack: [Profile → EditProfile]

  User in HomeTab navigates: Home → ProductDetail → Reviews
  User switches to SearchTab:
    → HomeTab stack PRESERVED (still at Reviews internally)
    → SearchTab shows its own current screen
  User switches back to HomeTab:
    → Sees Reviews (exactly where they left off!)

  LAZY LOADING:
  By default: tabs are lazy-loaded (not rendered until first visit)
  After first visit: tab component stays mounted (state preserved)

  unmountOnBlur: true → unmount tab when switching away (resets state)
  → Use only if you WANT tabs to reset (like a "refresh" behavior)
```

---

## 🟡 Real World Example
**Myntra shopping app:** Home (trending products), Search (filter by brand/category), Wishlist, Bag (cart with badge count), Profile. When user taps "Bag" tab — bag icon shows badge "3" (3 items in cart). On iOS, tapping the currently active "Home" tab scrolls the product list back to the top. On Android, similar behavior. Each section maintains its own navigation depth — user can be 3 levels deep in "Search" results while Cart stays intact.

---

## 💻 Code Example — Basic

```tsx
// App.tsx — Tab Navigator setup
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text } from 'react-native';

// Simple screen components (replace with actual screens)
function HomeScreen() { return <View><Text>Home</Text></View>; }
function SearchScreen() { return <View><Text>Search</Text></View>; }
function OrdersScreen() { return <View><Text>Orders</Text></View>; }
function ProfileScreen() { return <View><Text>Profile</Text></View>; }

type TabParamList = {
  Home: undefined;
  Search: undefined;
  Orders: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<TabParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        initialRouteName="Home"
        screenOptions={{
          tabBarActiveTintColor: '#e23744',     // active tab icon + label color
          tabBarInactiveTintColor: '#888',       // inactive color
          tabBarStyle: {
            backgroundColor: 'white',
            borderTopWidth: 1,
            borderTopColor: '#f0f0f0',
            paddingBottom: 4,
            height: 60,
          },
          tabBarLabelStyle: {
            fontSize: 11,
            fontWeight: '500',
          },
          headerShown: false,                    // typically false — screens handle their own header
        }}
      >
        <Tab.Screen
          name="Home"
          component={HomeScreen}
          options={{
            tabBarLabel: 'Home',
            tabBarIcon: ({ color, size }) => (
              // Use an icon library like @expo/vector-icons or react-native-vector-icons
              <Text style={{ color, fontSize: size }}>🏠</Text>
            ),
          }}
        />
        <Tab.Screen
          name="Search"
          component={SearchScreen}
          options={{
            tabBarLabel: 'Search',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>🔍</Text>
            ),
          }}
        />
        <Tab.Screen
          name="Orders"
          component={OrdersScreen}
          options={{
            tabBarLabel: 'Orders',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>📦</Text>
            ),
            tabBarBadge: 2,              // badge number (show 2 pending orders)
          }}
        />
        <Tab.Screen
          name="Profile"
          component={ProfileScreen}
          options={{
            tabBarLabel: 'Profile',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>👤</Text>
            ),
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
```

## 💻 Code Example — Advanced (Nested Stack + Dynamic Badge)

```tsx
// REAL PATTERN: Tab Navigator + Stack inside each tab + Dynamic cart badge
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Ionicons from '@expo/vector-icons/Ionicons';  // from @expo/vector-icons

// Zustand store for cart badge count
import { useCartStore } from '../stores/cartStore';

// ─── SCREEN IMPORTS ─────────────────────────────
import HomeScreen from '../screens/HomeScreen';
import ProductDetailScreen from '../screens/ProductDetailScreen';
import SearchScreen from '../screens/SearchScreen';
import CartScreen from '../screens/CartScreen';
import CheckoutScreen from '../screens/CheckoutScreen';
import ProfileScreen from '../screens/ProfileScreen';

// ─── STACK FOR EACH TAB ──────────────────────────
const HomeStack = createNativeStackNavigator();
function HomeStackNavigator() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="HomeMain" component={HomeScreen} options={{ title: 'Zomato' }} />
      <HomeStack.Screen name="ProductDetail" component={ProductDetailScreen} />
    </HomeStack.Navigator>
  );
}

const CartStack = createNativeStackNavigator();
function CartStackNavigator() {
  return (
    <CartStack.Navigator>
      <CartStack.Screen name="CartMain" component={CartScreen} options={{ title: 'Your Cart' }} />
      <CartStack.Screen name="Checkout" component={CheckoutScreen} options={{ title: 'Checkout' }} />
    </CartStack.Navigator>
  );
}

// ─── TAB NAVIGATOR ───────────────────────────────
const Tab = createBottomTabNavigator();

export default function App() {
  const cartItemCount = useCartStore(state => state.totalItems);  // dynamic badge!

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarActiveTintColor: '#e23744',
          tabBarInactiveTintColor: '#999',
          tabBarStyle: { backgroundColor: '#fff', paddingBottom: 8, height: 64 },

          // DYNAMIC ICON based on route name + focused state
          tabBarIcon: ({ focused, color, size }) => {
            const icons: Record<string, { focused: string; unfocused: string }> = {
              HomeTab:    { focused: 'home',         unfocused: 'home-outline' },
              SearchTab:  { focused: 'search',       unfocused: 'search-outline' },
              CartTab:    { focused: 'cart',         unfocused: 'cart-outline' },
              ProfileTab: { focused: 'person',       unfocused: 'person-outline' },
            };
            const iconName = focused
              ? icons[route.name].focused
              : icons[route.name].unfocused;

            return <Ionicons name={iconName as any} size={size} color={color} />;
          },
        })}
      >
        <Tab.Screen
          name="HomeTab"
          component={HomeStackNavigator}
          options={{ tabBarLabel: 'Home' }}
        />
        <Tab.Screen
          name="SearchTab"
          component={SearchScreen}
          options={{ tabBarLabel: 'Search' }}
        />
        <Tab.Screen
          name="CartTab"
          component={CartStackNavigator}
          options={{
            tabBarLabel: 'Cart',
            // DYNAMIC BADGE from Zustand store
            tabBarBadge: cartItemCount > 0 ? cartItemCount : undefined,
            tabBarBadgeStyle: { backgroundColor: '#e23744' },
          }}
        />
        <Tab.Screen
          name="ProfileTab"
          component={ProfileScreen}
          options={{ tabBarLabel: 'Profile' }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

// NAVIGATING TO A TAB FROM WITHIN A STACK:
// From ProductDetailScreen (inside HomeStack):
// navigation.navigate('CartTab')  → jumps to Cart tab
// navigation.navigate('CartTab', {
//   screen: 'Checkout',          → goes to specific screen inside CartStack
//   params: { orderId: '123' }
// })
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Tab position | Bottom | Bottom |
| Tab style | Material Design style | iOS native style |
| Haptic on tap | No (by default) | Yes (subtle haptic) |
| Safe area | No notch issue | Needs safe area for home bar |
| Icon behavior | Label always visible | Label only for active tab (optional) |
| Tap active tab | No default behavior | Scrolls to top (if configured) |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
npx expo install @react-navigation/bottom-tabs
npx expo install @expo/vector-icons  # icons included in Expo SDK
```

CLI way:
```bash
npm install @react-navigation/bottom-tabs
npm install react-native-vector-icons  # need additional native setup
# android: android/app/build.gradle → apply from: "../../node_modules/react-native-vector-icons/fonts.gradle"
# ios: pod install + Info.plist font registration
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Nesting Tab inside Stack incorrectly (double header)
```tsx
// WRONG: Stack screen shows header + Tab screens also show header
<Stack.Screen name="MainTabs" component={TabNavigator} />
// → Double header: Stack header + individual screen headers

// CORRECT: Hide Stack header for the tab container
<Stack.Screen
  name="MainTabs"
  component={TabNavigator}
  options={{ headerShown: false }}  // Screens manage their own headers
/>
```

❌ **Mistake 2:** Using `navigation.navigate('HomeTab')` when already on HomeTab
```tsx
// In some edge cases this causes unexpected behavior
// Instead: navigate to the specific screen within the tab
navigation.navigate('HomeTab', {
  screen: 'HomeMain'  // specify the screen inside the tab's stack
})
```

❌ **Mistake 3:** Dynamic badge from non-reactive source
```tsx
// WRONG: Static badge, never updates
<Tab.Screen options={{ tabBarBadge: 3 }} />

// CORRECT: Dynamic badge from reactive state
const cartCount = useCartStore(state => state.totalItems);
<Tab.Screen
  options={{ tabBarBadge: cartCount > 0 ? cartCount : undefined }}
/>
// undefined removes the badge dot entirely (cleaner than 0)
```

---

## 🧠 Tricky Interview Question

**Q: User is on `HomeTab → ProductDetail` (3 levels deep). They tap `CartTab`. They come back to `HomeTab`. Are they back at `HomeScreen` or still at `ProductDetail`?**

**Answer:** Still at `ProductDetail`. Each tab maintains its own navigation stack independently. When you switch tabs, the current tab's stack is preserved in memory (the component stays mounted). Coming back to `HomeTab` resumes exactly where you left off — `ProductDetail` is still the active screen. This is the expected behavior that users depend on: "I was browsing a product, I checked my cart, now I'm back to the product." To change this behavior (reset tab on each visit): set `unmountOnBlur: true` in `screenOptions`. This unmounts the tab when leaving it, so returning always shows the root screen. But this also resets any scroll position, loaded data, etc. — use thoughtfully.

---

## ⚫ Interview Questions + Answers

**Q1: What is a Tab Navigator and when do you use it?**
A1: Tab Navigator creates a bottom navigation bar where each tab is an independent section of the app. Use it for top-level, peer sections of equal importance (Home, Search, Orders, Profile) — things a user wants to switch between frequently. Each tab maintains its own navigation stack. Don't use tabs for sequential flows (onboarding, checkout) — use Stack for those.

**Q2: How do you show a badge count on a tab icon?**
A2: Use `tabBarBadge` in the screen's `options`. For dynamic badges: connect to your state (Zustand, Redux): `tabBarBadge: cartCount > 0 ? cartCount : undefined`. Setting to `undefined` removes the badge entirely (pass `0` shows "0" badge — pass `undefined` to hide it). Style with `tabBarBadgeStyle`.

**Q3: How does each tab maintain its own navigation stack?**
A3: Wrap each Tab.Screen's component with its own Stack Navigator. Each Stack is independent. HomeTab has Stack [Home → ProductDetail]; CartTab has Stack [Cart → Checkout]. Switching tabs: the new tab's stack becomes active; the old tab's stack is preserved in memory (stays mounted). Tab state is preserved unless `unmountOnBlur: true`.

**Q4: How do you navigate to a specific screen inside another tab?**
A4: `navigation.navigate('CartTab', { screen: 'Checkout', params: { orderId: '123' } })`. The first argument is the tab name, `screen` is the screen within that tab's stack, `params` are passed to that screen. Without `screen`, it navigates to the tab's current active screen (or root if first visit).

**Q5: What is `screenOptions` vs individual screen `options`?**
A5: `screenOptions` on `Tab.Navigator` (or can be a function `({ route }) => ({...})`) sets defaults for ALL tabs. Individual `<Tab.Screen options={{}}>` overrides for that specific tab. For icons and badges, usually define icons in `screenOptions` with route name switching (`route.name`), and use individual `options` for per-tab differences like `tabBarBadge`.

---

## 📊 Visual Diagram

```
TAB NAVIGATOR STRUCTURE:
──────────────────────────────────────────────────────

  NavigationContainer
  └── Tab.Navigator
      ├── HomeTab (Stack)
      │   ├── HomeScreen         ← current
      │   └── ProductDetail      ← user navigated here
      │
      ├── SearchTab (standalone)
      │   └── SearchScreen
      │
      ├── CartTab (Stack)
      │   ├── CartScreen
      │   └── CheckoutScreen
      │
      └── ProfileTab (standalone)
          └── ProfileScreen

  ┌──────────────────────────────────┐
  │                                  │
  │      PRODUCT DETAIL SCREEN       │
  │    (HomeTab → current screen)    │
  │                                  │
  │                                  │
  └──────────────────────────────────┘
  ┌────┬──────┬──────┬───────────────┐
  │ 🏠 │  🔍  │ 🛒 3 │       👤      │
  │Home│Search│ Cart │    Profile    │
  └────┴──────┴──────┴───────────────┘
         Bottom Tab Bar
         (always visible, 🛒 shows badge "3")

INDEPENDENT STACK PER TAB:
  HomeTab:    Home → ProductDetail [← user is here]
  SearchTab:  Search                [preserved independently]
  CartTab:    Cart → Checkout       [preserved independently]
  ProfileTab: Profile               [preserved independently]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tab Navigator | Bottom navigation bar | Bottom navigation bar |
| tabBarBadge | Number shown on tab icon | Tab icon पर number |
| tabBarIcon | Icon for each tab | हर tab के लिए icon |
| tabBarActiveTintColor | Active tab color | Active tab का color |
| unmountOnBlur | Reset tab on switching away | Switch करने पर tab reset |
| initialRouteName | First tab shown | पहले दिखने वाला tab |
| nested navigators | Stack inside Tab | Tab के अंदर Stack |

---

## ⚡ 3-Line Summary
**English:**
1. Tab Navigator creates a persistent bottom bar where each tab maintains its own independent navigation stack — switching tabs preserves each tab's history.
2. Dynamic cart badges: `tabBarBadge: cartCount > 0 ? cartCount : undefined` — connect to Zustand store so badge updates automatically when items are added.
3. Nest each Tab.Screen inside its own Stack Navigator for tabs that need sub-navigation (Product list → Product detail within the same tab).

**Hindi:**
1. Tab Navigator persistent bottom bar बनाता है — हर tab अपना independent navigation stack maintain करती है।
2. Dynamic cart badge: Zustand store से `totalItems` connect करो → items add करने पर badge automatically update।
3. Sub-navigation चाहिए (Product → Detail)? हर Tab.Screen के अंदर अपना Stack Navigator nest करो।

---

## ➡️ Next Topic
**67. Drawer Navigator** — Side menu navigation, custom drawer content।
