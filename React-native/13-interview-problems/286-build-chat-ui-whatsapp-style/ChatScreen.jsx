// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useState, useCallback } from 'react'; // hooks
import { View, FlatList, TextInput, Pressable, Text, KeyboardAvoidingView, Platform, StyleSheet } from 'react-native'; // RN core
import MessageBubble from './MessageBubble'; // bubble

const now = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); // HH:MM

export default function ChatScreen() {
  // NEWEST FIRST because FlatList is inverted
  const [messages, setMessages] = useState([
    { id: '2', text: 'Haan bhai, bolo', mine: false, time: now() },
    { id: '1', text: 'Hello!', mine: true, time: now() },
  ]);
  const [input, setInput] = useState(''); // text box value

  const send = useCallback(() => {
    const text = input.trim(); // remove spaces
    if (!text) return; // ignore empty
    setMessages((prev) => [{ id: String(Date.now()), text, mine: true, time: now() }, ...prev]); // add on top (index 0 = bottom)
    setInput(''); // clear box
  }, [input]);

  const renderItem = useCallback(({ item }) => <MessageBubble {...item} />, []); // stable renderer

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined} // iOS needs padding; Android resizes window (adjustResize default in Expo)
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0} // header height offset (tune it)
    >
      <FlatList
        data={messages} // newest first
        inverted // bottom-anchored list, keyboard friendly
        keyExtractor={(m) => m.id} // stable key
        renderItem={renderItem} // bubble
        contentContainerStyle={{ paddingVertical: 8 }} // spacing
        keyboardShouldPersistTaps="handled" // tap send without closing keyboard first
        style={styles.list}
      />
      <View style={styles.inputBar}>
        <TextInput
          style={styles.input}
          value={input} // controlled
          onChangeText={setInput} // update
          placeholder="Message" // hint
          multiline // grow for long text
        />
        <Pressable style={styles.send} onPress={send} accessibilityLabel="Send"><Text style={{ color: '#fff' }}>Send</Text></Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: '#ECE5DD' }, // chat background
  list: { flex: 1 }, // fill
  inputBar: { flexDirection: 'row', padding: 8, alignItems: 'flex-end' }, // bottom bar
  input: { flex: 1, backgroundColor: '#fff', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, maxHeight: 120 }, // input
  send: { backgroundColor: '#075E54', borderRadius: 20, paddingHorizontal: 16, justifyContent: 'center', marginLeft: 6, height: 40 }, // send button
});
