// Expo SDK 52 (check current docs - APIs change between SDKs)
import React from 'react'; // React
import { View, Text, StyleSheet } from 'react-native'; // RN core
import { DrawerContentScrollView, DrawerItemList, DrawerItem } from '@react-navigation/drawer'; // helpers

export default function CustomDrawerContent(props) {
  return (
    <DrawerContentScrollView {...props}>
      <View style={styles.header}>
        <Text style={styles.name}>Aditya Ranjan</Text>
        <Text style={styles.sub}>+91 98xxxxxx10</Text>
      </View>
      <DrawerItemList {...props} />
      <DrawerItem
        label="Logout" // extra action
        onPress={() => { props.navigation.closeDrawer(); /* clear token here */ }} // close drawer
      />
    </DrawerContentScrollView>
  );
}

const styles = StyleSheet.create({
  header: { padding: 20, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ddd' }, // profile header
  name: { fontSize: 18, fontWeight: '700' }, // name
  sub: { color: '#777' }, // phone
});
