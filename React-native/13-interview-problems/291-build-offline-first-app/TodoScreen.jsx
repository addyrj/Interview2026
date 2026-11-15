// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install @react-native-async-storage/async-storage @react-native-community/netinfo
import React, { useEffect, useMemo, useState, useCallback } from 'react'; // hooks
import { View, Text, TextInput, Button, FlatList, StyleSheet } from 'react-native'; // RN core
import AsyncStorage from '@react-native-async-storage/async-storage'; // disk storage
import NetInfo from '@react-native-community/netinfo'; // connectivity
import { createSyncQueue } from './syncQueue'; // queue logic

const CACHE_KEY = 'todos_cache'; // local copy of list

// Fake server call: replace with fetch(POST). Throw on failure.
const sendToServer = async (action) => { await new Promise((r) => setTimeout(r, 200)); return action; };

export default function TodoScreen() {
  const [todos, setTodos] = useState([]); // list on screen
  const [text, setText] = useState(''); // input
  const [online, setOnline] = useState(true); // network flag
  const [pending, setPending] = useState(0); // unsynced count
  const queue = useMemo(() => createSyncQueue(AsyncStorage, sendToServer), []); // one queue

  // 1) Show cached data instantly on launch (offline-first = read local first)
  useEffect(() => {
    AsyncStorage.getItem(CACHE_KEY).then((v) => v && setTodos(JSON.parse(v)));
    queue.read().then((q) => setPending(q.length));
  }, [queue]);

  // 2) Flush queue whenever internet comes back
  useEffect(() => {
    const unsub = NetInfo.addEventListener(async (s) => {
      const isOnline = !!s.isConnected && s.isInternetReachable !== false; // null = unknown -> treat as ok
      setOnline(isOnline); // update banner
      if (isOnline) { await queue.flush(); setPending((await queue.read()).length); } // sync
    });
    return unsub; // cleanup
  }, [queue]);

  const addTodo = useCallback(async () => {
    if (!text.trim()) return; // ignore empty
    const item = { id: String(Date.now()), title: text.trim() }; // new todo
    const next = [item, ...todos]; // optimistic update (UI first)
    setTodos(next); // show now
    setText(''); // clear
    await AsyncStorage.setItem(CACHE_KEY, JSON.stringify(next)); // persist local copy
    await queue.enqueue({ type: 'ADD_TODO', payload: item, id: item.id }); // remember to sync
    setPending((await queue.read()).length); // update count
  }, [text, todos, queue]);

  return (
    <View style={styles.c}>
      {!online && <Text style={styles.banner}>Offline - changes will sync later ({pending} pending)</Text>}
      <TextInput style={styles.input} value={text} onChangeText={setText} placeholder="New todo" />
      <Button title="Add" onPress={addTodo} />
      <FlatList data={todos} keyExtractor={(t) => t.id} renderItem={({ item }) => <Text style={styles.row}>{item.title}</Text>} />
    </View>
  );
}

const styles = StyleSheet.create({
  c: { flex: 1, padding: 16 }, // container
  banner: { backgroundColor: '#333', color: '#fff', padding: 8, textAlign: 'center', marginBottom: 8 }, // offline bar
  input: { borderWidth: 1, borderColor: '#ccc', padding: 8, marginBottom: 8, borderRadius: 6 }, // input
  row: { paddingVertical: 10, fontSize: 16 }, // row
});
