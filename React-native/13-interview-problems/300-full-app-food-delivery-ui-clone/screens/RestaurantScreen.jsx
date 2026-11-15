// screens/RestaurantScreen.jsx — menu with add / remove steppers
import React from 'react'; // React
import { View, Text, FlatList, Pressable, StyleSheet } from 'react-native'; // UI
import { RESTAURANTS } from '../data'; // data
import { useCart } from '../CartContext'; // cart

export default function RestaurantScreen({ route }) {
  const restaurant = RESTAURANTS.find((r) => r.id === route.params.id); // id from navigation params
  const { qtyOf, add, remove } = useCart(); // cart actions
  if (!restaurant) return <Text>Restaurant not found</Text>; // safety
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{restaurant.name}</Text>
      <FlatList
        data={restaurant.menu}
        keyExtractor={(m) => m.id}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.name}>{item.name}</Text>
              <Text>Rs {item.price}</Text>
            </View>
            {qtyOf(item.id) === 0 ? (
              <Pressable onPress={() => add(item)} style={styles.add} testID={`add-${item.id}`}><Text style={styles.addText}>ADD</Text></Pressable>
            ) : (
              <View style={styles.stepper}>
                <Pressable onPress={() => remove(item.id)} testID={`minus-${item.id}`}><Text style={styles.sym}> - </Text></Pressable>
                <Text testID={`qty-${item.id}`}>{qtyOf(item.id)}</Text>
                <Pressable onPress={() => add(item)} testID={`plus-${item.id}`}><Text style={styles.sym}> + </Text></Pressable>
              </View>
            )}
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 16 },
  title: { fontSize: 22, fontWeight: '800', marginBottom: 12 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderColor: '#eee' },
  name: { fontWeight: '600' },
  add: { borderWidth: 1, borderColor: '#fc8019', paddingHorizontal: 18, paddingVertical: 6, borderRadius: 8 }, addText: { color: '#fc8019', fontWeight: '700' },
  stepper: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fc8019', borderRadius: 8, paddingHorizontal: 6 }, sym: { color: '#fff', fontSize: 20 },
});
