// screens/HomeScreen.jsx — search + category chips + restaurant list
import React, { useMemo, useState } from 'react'; // hooks
import { View, Text, TextInput, FlatList, Pressable, StyleSheet } from 'react-native'; // UI
import { RESTAURANTS, CATEGORIES } from '../data'; // dummy data
import { useCart } from '../CartContext'; // cart info for the bottom bar

export default function HomeScreen({ navigation }) {
  const [query, setQuery] = useState(''); // search text
  const [category, setCategory] = useState('All'); // selected chip
  const { count, total } = useCart(); // cart summary

  // Filter only when inputs change
  const data = useMemo(
    () => RESTAURANTS.filter((r) =>
      (category === 'All' || r.cuisine.includes(category)) &&
      r.name.toLowerCase().includes(query.trim().toLowerCase())),
    [query, category]
  );

  return (
    <View style={styles.container}>
      <TextInput placeholder="Search restaurants" value={query} onChangeText={setQuery} style={styles.search} testID="search" />
      <View style={styles.chips}>
        {CATEGORIES.map((c) => (
          <Pressable key={c} onPress={() => setCategory(c)} style={[styles.chip, category === c && styles.chipOn]} testID={`cat-${c}`}>
            <Text style={category === c && styles.chipTextOn}>{c}</Text>
          </Pressable>
        ))}
      </View>
      <FlatList
        data={data} // list data
        keyExtractor={(r) => r.id} // unique key
        ListEmptyComponent={<Text style={styles.empty}>No restaurants found</Text>}
        renderItem={({ item }) => (
          <Pressable style={styles.card} onPress={() => navigation.navigate('Restaurant', { id: item.id })} testID={`rest-${item.id}`}>
            <Text style={styles.name}>{item.name}</Text>
            <Text style={styles.meta}>{item.cuisine}</Text>
            <Text style={styles.meta}>{item.rating} star | {item.time} min</Text>
            <Text style={styles.offer}>{item.offer}</Text>
          </Pressable>
        )}
      />
      {count > 0 && (
        <Pressable style={styles.bar} onPress={() => navigation.navigate('Cart')} testID="cart-bar">
          <Text style={styles.barText}>{count} items | Rs {total}  -  View cart</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 12 },
  search: { backgroundColor: '#f1f1f1', borderRadius: 10, padding: 12 },
  chips: { flexDirection: 'row', gap: 8, marginVertical: 10 },
  chip: { paddingVertical: 6, paddingHorizontal: 12, borderRadius: 16, backgroundColor: '#eee' },
  chipOn: { backgroundColor: '#fc8019' }, chipTextOn: { color: '#fff' },
  card: { padding: 14, borderRadius: 12, backgroundColor: '#fafafa', marginBottom: 10 },
  name: { fontSize: 17, fontWeight: '700' }, meta: { color: '#666', marginTop: 2 }, offer: { color: '#2563eb', marginTop: 4 },
  empty: { textAlign: 'center', marginTop: 30, color: '#888' },
  bar: { backgroundColor: '#fc8019', padding: 14, borderRadius: 10 }, barText: { color: '#fff', textAlign: 'center', fontWeight: '700' },
});
