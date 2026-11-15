// Expo SDK 52 (check current docs - APIs change between SDKs)
import React from 'react'; // React
import { Text, View } from 'react-native'; // RN core
import { NavigationContainer } from '@react-navigation/native'; // root
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'; // tabs
import { SafeAreaProvider } from 'react-native-safe-area-context'; // insets provider
import CustomTabBar from './CustomTabBar'; // our bar

const Tab = createBottomTabNavigator(); // navigator
const Screen = ({ name }) => <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}><Text>{name}</Text></View>; // dummy

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator tabBar={(props) => <CustomTabBar {...props} />}>
          <Tab.Screen name="Home" children={() => <Screen name="Home" />} />
          <Tab.Screen name="Search" children={() => <Screen name="Search" />} />
          <Tab.Screen name="Orders" children={() => <Screen name="Orders" />} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
