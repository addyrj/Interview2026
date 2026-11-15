// App.jsx — demo: reorder your "Favourite dishes"
import React from 'react';
import { SafeAreaView, Text, StyleSheet } from 'react-native';
import DragDropList from './DragDropList';

const DATA = [
  { id: 'a', title: 'Butter Chicken' },
  { id: 'b', title: 'Masala Dosa' },
  { id: 'c', title: 'Pav Bhaji' },
  { id: 'd', title: 'Chole Bhature' },
];

export default function App() {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <Text style={styles.h}>Drag the handle to reorder</Text>
      <DragDropList initial={DATA} />
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({ h: { fontSize: 20, fontWeight: '700', padding: 16 } });
