// App.jsx — navigation + providers (React Navigation v6/v7 native-stack)
import React from 'react'; // React
import { NavigationContainer } from '@react-navigation/native'; // navigation root
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // stack navigator
import { SafeAreaProvider } from 'react-native-safe-area-context'; // safe area support
import { CartProvider } from './CartContext'; // cart state
import HomeScreen from './screens/HomeScreen'; // screens
import RestaurantScreen from './screens/RestaurantScreen';
import CartScreen from './screens/CartScreen';

const Stack = createNativeStackNavigator(); // stack object

export default function App() {
  return (
    <SafeAreaProvider>
      <CartProvider>
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Deliver to Home' }} />
            <Stack.Screen name="Restaurant" component={RestaurantScreen} />
            <Stack.Screen name="Cart" component={CartScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </CartProvider>
    </SafeAreaProvider>
  );
}
