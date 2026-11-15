// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { memo } from 'react'; // memo for list performance
import { View, Text, StyleSheet } from 'react-native'; // RN core

// One chat bubble; mine = true means right side green, else left white
function MessageBubble({ text, mine, time }) {
  return (
    <View style={[styles.row, mine ? styles.rowMine : styles.rowTheirs]}>
      <View style={[styles.bubble, mine ? styles.mine : styles.theirs]}>
        <Text style={styles.text}>{text}</Text>
        <Text style={styles.time}>{time}</Text>
      </View>
    </View>
  );
}

export default memo(MessageBubble); // skip re-render if props same

const styles = StyleSheet.create({
  row: { paddingHorizontal: 10, marginVertical: 3, flexDirection: 'row' }, // row
  rowMine: { justifyContent: 'flex-end' }, // push right
  rowTheirs: { justifyContent: 'flex-start' }, // push left
  bubble: { maxWidth: '80%', padding: 8, borderRadius: 10 }, // bubble box
  mine: { backgroundColor: '#DCF8C6' }, // WhatsApp green
  theirs: { backgroundColor: '#fff' }, // white
  text: { fontSize: 16 }, // message text
  time: { fontSize: 10, color: '#888', alignSelf: 'flex-end', marginTop: 2 }, // timestamp
});
