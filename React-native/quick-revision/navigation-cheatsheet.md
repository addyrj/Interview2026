# React Native — Navigation Cheatsheet
# React Navigation Quick Reference
# Quick Revision

---

## 🏗️ Navigator Types

```
Stack Navigator    → push/pop screens (most common)
Tab Navigator      → bottom tabs (Home, Search, Orders, Profile)
Drawer Navigator   → side menu
Material Top Tabs  → swipeable top tabs
Expo Router        → file-system based (like Next.js)
```

---

## ⚡ Setup (install once)

```bash
npx expo install @react-navigation/native @react-navigation/native-stack
npx expo install @react-navigation/bottom-tabs
npx expo install react-native-screens react-native-safe-area-context
```

---

## 📋 Navigation Actions

```tsx
// Navigate (push or activate existing):
navigation.navigate('ScreenName')
navigation.navigate('ScreenName', { id: '123' })

// Always push (even if exists in stack):
navigation.push('ScreenName', params)

// Replace current screen (no back button):
navigation.replace('ScreenName', params)

// Go back:
navigation.goBack()

// Pop to root of stack:
navigation.popToTop()

// Reset entire stack (after login/logout):
navigation.reset({
  index: 0,
  routes: [{ name: 'Home' }],
})

// Navigate to screen inside a tab:
navigation.navigate('CartTab', {
  screen: 'Checkout',
  params: { orderId: '123' },
})
```

---

## 📦 Receiving Params

```tsx
// In the component:
const { productId, name } = route.params;

// OR with useRoute hook:
const { params } = useRoute();

// TypeScript (define in App.tsx):
type RootStackParamList = {
  Home: undefined;
  ProductDetail: { productId: string; name: string };
  Cart: undefined;
};

// In screen component:
type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'ProductDetail'>;
  route: RouteProp<RootStackParamList, 'ProductDetail'>;
};
```

---

## 🏗️ Stack Navigator Setup

```tsx
const Stack = createNativeStackNavigator<RootStackParamList>();

<Stack.Navigator
  initialRouteName="Home"
  screenOptions={{
    headerStyle: { backgroundColor: '#e23744' },
    headerTintColor: '#fff',
  }}
>
  <Stack.Screen name="Home" component={HomeScreen} />
  <Stack.Screen
    name="ProductDetail"
    component={ProductDetailScreen}
    options={({ route }) => ({ title: route.params.name })}
  />
  <Stack.Screen
    name="Reviews"
    component={ReviewsScreen}
    options={{ presentation: 'modal' }}
  />
</Stack.Navigator>
```

---

## 📱 Tab Navigator Setup

```tsx
const Tab = createBottomTabNavigator();

<Tab.Navigator
  screenOptions={({ route }) => ({
    tabBarActiveTintColor: '#e23744',
    tabBarIcon: ({ color, size }) => <Icon name={route.name} />,
    headerShown: false,
  })}
>
  <Tab.Screen name="HomeTab" component={HomeStackNavigator}
    options={{ tabBarLabel: 'Home', tabBarBadge: undefined }} />
  <Tab.Screen name="CartTab" component={CartStack}
    options={{ tabBarBadge: cartCount > 0 ? cartCount : undefined }} />
</Tab.Navigator>
```

---

## 🔐 Auth Flow Pattern

```tsx
function RootNavigator() {
  const { isLoggedIn, isLoading } = useAuthStore();

  if (isLoading) return <SplashScreen />;  // prevent flash!

  return isLoggedIn ? <AppNavigator /> : <AuthNavigator />;
}

// After login:
useAuthStore.getState().setAuth(token, user);
// → RootNavigator re-renders → switches to AppNavigator
// No navigation.navigate() needed!

// After logout:
useAuthStore.getState().clearAuth();
// → switches to AuthNavigator automatically

// After OTP (use replace, not navigate):
navigation.replace('Home');  // removes OTP from history
```

---

## 🔧 Custom Header Buttons

```tsx
useLayoutEffect(() => {
  navigation.setOptions({
    headerRight: () => (
      <Pressable onPress={handleShare} style={{ marginRight: 16 }}>
        <Text>Share</Text>
      </Pressable>
    ),
    headerTitle: 'Custom Title',
    headerBackVisible: false,  // hide back button
  });
}, [navigation]);
```

---

## 🔗 Deep Linking

```tsx
// app.json (Expo):
"scheme": "myapp"
// → myapp://home, myapp://product/123

// In NavigationContainer:
const linking = {
  prefixes: ['myapp://', 'https://myapp.com'],
  config: {
    screens: {
      Home: 'home',
      ProductDetail: 'product/:productId',
      Profile: 'profile/:userId',
    },
  },
};
<NavigationContainer linking={linking}>
```

---

## 📊 Quick Comparison

| Action | navigate() | push() | replace() | reset() |
|--------|-----------|--------|-----------|---------|
| Adds to history | Yes (smart) | Always | No | Clears all |
| Back button | Yes | Yes | No | No |
| Use case | Normal nav | Drill-down | OTP/login | Auth flow |

---

## 🧠 Common Interview Q&A

**navigate vs replace vs reset?**
→ navigate: normal go to screen (smart, checks if exists). replace: swap current (no back). reset: wipe entire stack. Use reset after login/logout.

**Tab state preserved when switching?**
→ Yes — each tab has independent stack. Switching preserves scroll position, loaded data. `unmountOnBlur: true` to disable.

**How to navigate from outside React (API interceptor)?**
→ Create a navigationRef: `const navigationRef = createNavigationContainerRef()`
→ `<NavigationContainer ref={navigationRef}>`
→ `navigationRef.navigate('Login')` anywhere in code

**Pass large data between screens?**
→ DON'T pass objects/arrays in params. Pass only IDs, fetch data in destination. Or use Zustand store.

**How to navigate to nested screen (inside Tab)?**
→ `navigation.navigate('CartTab', { screen: 'Checkout', params: { id: '1' } })`
