// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useState, useCallback, useEffect } from 'react'; // React + hooks
import { View, Text, FlatList, RefreshControl, StyleSheet, Platform } from 'react-native'; // RN core

// Fake API: returns orders after 800ms (replace with fetch())
const fetchOrders = () =>
  new Promise((resolve) =>
    setTimeout(() => resolve([ // simulate network delay
      { id: String(Date.now()) + 'a', title: 'Biryani - Paradise', time: new Date().toLocaleTimeString() }, // item 1
      { id: String(Date.now()) + 'b', title: 'Masala Dosa - Saravana', time: new Date().toLocaleTimeString() }, // item 2
    ]), 800));

export default function PullToRefreshScreen() {
  const [orders, setOrders] = useState([]); // list data
  const [refreshing, setRefreshing] = useState(false); // spinner state (controlled)
  const [error, setError] = useState(null); // error message

  const load = useCallback(async () => { // shared loader
    try {
      setError(null); // clear old error
      const data = await fetchOrders(); // call API
      setOrders(data); // replace list (refresh = replace, not append)
    } catch (e) {
      setError('Refresh failed. Pull again.'); // show error
    }
  }, []);

  useEffect(() => { load(); }, [load]); // first load on mount

  const onRefresh = useCallback(async () => { // called when user pulls
    setRefreshing(true); // show spinner
    await load(); // wait for data
    setRefreshing(false); // hide spinner (always, even on error)
  }, [load]);

  return (
    <View style={styles.container}>
      {error && <Text style={styles.error}>{error}</Text>}
      <FlatList
        data={orders} // list data
        keyExtractor={(item) => item.id} // stable key
        renderItem={({ item }) => ( // one row
          <View style={styles.row}>
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.time}>{item.time}</Text>
          </View>
        )}
        refreshControl={
          <RefreshControl
            refreshing={refreshing} // controlled spinner
            onRefresh={onRefresh} // pull handler
            tintColor="#E23744" // iOS spinner colour
            colors={['#E23744']} // Android spinner colours
            progressViewOffset={Platform.OS === 'android' ? 8 : 0} // Android only offset
          />
        }
        contentContainerStyle={{ flexGrow: 1 }} // so empty list is still pullable
        ListEmptyComponent={<Text style={styles.empty}>No orders yet</Text>} // empty state
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' }, // full screen
  row: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ddd' }, // row card
  title: { fontSize: 16, fontWeight: '600' }, // title text
  time: { color: '#666', marginTop: 4 }, // sub text
  error: { color: 'red', padding: 8, textAlign: 'center' }, // error banner
  empty: { textAlign: 'center', marginTop: 40, color: '#999' }, // empty text
});
