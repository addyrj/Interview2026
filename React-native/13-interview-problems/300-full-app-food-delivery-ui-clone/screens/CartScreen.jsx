// screens/CartScreen.jsx — bill summary + place order
import React from 'react'; // React
import { View, Text, FlatList, Pressable, Alert, StyleSheet } from 'react-native'; // UI
import { useCart } from '../CartContext'; // cart

const DELIVERY_FEE = 30; // flat fee for demo

export default function CartScreen({ navigation }) {
  const { lines, total, clear } = useCart(); // cart data
  const grand = lines.length ? total + DELIVERY_FEE : 0; // no fee for empty cart

  const placeOrder = () => {
    Alert.alert('Order placed', `Total Rs ${grand}`); // real app: POST to backend
    clear(); // empty the cart
    navigation.popToTop(); // go back to Home
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={lines}
        keyExtractor={(l) => l.item.id}
        ListEmptyComponent={<Text style={styles.empty}>Your cart is empty</Text>}
        renderItem={({ item: l }) => (
          <View style={styles.row}><Text>{l.qty} x {l.item.name}</Text><Text>Rs {l.qty * l.item.price}</Text></View>
        )}
      />
      {lines.length > 0 && (
        <>
          <View style={styles.row}><Text>Delivery fee</Text><Text>Rs {DELIVERY_FEE}</Text></View>
          <View style={styles.row}><Text style={styles.bold}>To pay</Text><Text style={styles.bold} testID="grand">Rs {grand}</Text></View>
          <Pressable style={styles.btn} onPress={placeOrder} testID="place"><Text style={styles.btnText}>Place order</Text></Pressable>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 16 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8 },
  bold: { fontWeight: '800' }, empty: { textAlign: 'center', marginTop: 40, color: '#888' },
  btn: { backgroundColor: '#fc8019', padding: 14, borderRadius: 10, marginTop: 12 }, btnText: { color: '#fff', textAlign: 'center', fontWeight: '700' },
});
