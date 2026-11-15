// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npm i @react-navigation/native @react-navigation/drawer
//          npx expo install react-native-gesture-handler react-native-reanimated react-native-screens react-native-safe-area-context
// Reanimated 3: babel preset babel-preset-expo already adds the plugin in Expo; CLI needs 'react-native-reanimated/plugin' LAST in babel.config.js
import 'react-native-gesture-handler'; // MUST be first import
import React from 'react'; // React
import { Text, View } from 'react-native'; // RN core
import { NavigationContainer } from '@react-navigation/native'; // root
import { createDrawerNavigator } from '@react-navigation/drawer'; // drawer
import CustomDrawerContent from './CustomDrawerContent'; // custom menu

const Drawer = createDrawerNavigator(); // navigator
const Screen = ({ name }) => <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}><Text>{name}</Text></View>; // dummy

export default function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator
        drawerContent={(props) => <CustomDrawerContent {...props} />} // our menu
        screenOptions={{
          drawerType: 'front', // slide over content (use 'slide' to push)
          drawerStyle: { width: 280 }, // width
          headerTintColor: '#E23744', // hamburger colour
        }}
      >
        <Drawer.Screen name="Home" children={() => <Screen name="Home" />} />
        <Drawer.Screen name="Orders" children={() => <Screen name="Orders" />} />
        <Drawer.Screen name="Settings" children={() => <Screen name="Settings" />} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}
