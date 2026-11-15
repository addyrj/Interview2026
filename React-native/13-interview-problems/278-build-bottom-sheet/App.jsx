// App.jsx — demo: Zomato-style "filters" bottom sheet
import React, { useState } from 'react';                         // React + state
import { SafeAreaView, View, Text, Pressable, StyleSheet } from 'react-native'; // UI
import BottomSheet from './BottomSheet';                         // our component

export default function App() {
  const [open, setOpen] = useState(false);                       // sheet visibility
  const [veg, setVeg] = useState(false);                         // example filter state

  return (
    <SafeAreaView style={styles.screen}>
      <Text style={styles.title}>Restaurants</Text>
      {/* Button that opens the sheet */}
      <Pressable style={styles.btn} onPress={() => setOpen(true)} testID="open-btn">
        <Text style={styles.btnText}>Filters</Text>
      </Pressable>

      {/* Sheet with two snap points: 40% and 85% of the screen */}
      <BottomSheet visible={open} onClose={() => setOpen(false)} snapPoints={[0.4, 0.85]}>
        <Text style={styles.h}>Filters</Text>
        <Pressable onPress={() => setVeg((v) => !v)} testID="veg-toggle">
          <Text>{veg ? '[x] Pure Veg' : '[ ] Pure Veg'}</Text>
        </Pressable>
      </BottomSheet>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: '700' },
  btn: { marginTop: 20, backgroundColor: '#E23744', padding: 14, borderRadius: 10 },
  btnText: { color: '#fff', textAlign: 'center', fontWeight: '700' },
  h: { fontSize: 18, fontWeight: '700', marginBottom: 12 },
});
