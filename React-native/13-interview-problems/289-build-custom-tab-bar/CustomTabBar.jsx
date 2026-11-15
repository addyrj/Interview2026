// Expo SDK 52 (check current docs - APIs change between SDKs)
// React Navigation v6/v7: npm i @react-navigation/native @react-navigation/bottom-tabs
import React from 'react'; // React
import { View, Text, Pressable, StyleSheet, Platform } from 'react-native'; // RN core
import { useSafeAreaInsets } from 'react-native-safe-area-context'; // notch / home-indicator space

// Receives state, descriptors, navigation from the navigator via tabBar prop
export default function CustomTabBar({ state, descriptors, navigation }) {
  const insets = useSafeAreaInsets(); // bottom inset

  return (
    <View style={[styles.bar, { paddingBottom: Math.max(insets.bottom, 8) }]}>
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key]; // screen options
        const label = options.tabBarLabel ?? options.title ?? route.name; // label
        const focused = state.index === index; // is active?

        const onPress = () => {
          const event = navigation.emit({ type: 'tabPress', target: route.key, canPreventDefault: true }); // let screen intercept
          if (!focused && !event.defaultPrevented) navigation.navigate(route.name, route.params); // go to tab
        };
        const onLongPress = () => navigation.emit({ type: 'tabLongPress', target: route.key }); // long press event

        return (
          <Pressable
            key={route.key} // stable key
            accessibilityRole="button" // a11y
            accessibilityState={focused ? { selected: true } : {}} // a11y selected
            onPress={onPress}
            onLongPress={onLongPress}
            style={[styles.tab, focused && styles.tabFocused]} // active style
          >
            <Text style={{ color: focused ? '#E23744' : '#777', fontWeight: focused ? '700' : '400' }}>{label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: { flexDirection: 'row', backgroundColor: '#fff', paddingTop: 8, elevation: 8, borderTopWidth: Platform.OS === 'ios' ? StyleSheet.hairlineWidth : 0 }, // bar
  tab: { flex: 1, alignItems: 'center', paddingVertical: 8 }, // each tab
  tabFocused: { borderTopWidth: 2, borderColor: '#E23744' }, // active indicator
});
