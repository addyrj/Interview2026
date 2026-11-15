// App.jsx — demo deck of restaurant cards; swipe right = save, left = skip
import React, { useState } from 'react';
import { SafeAreaView, Text, View, StyleSheet } from 'react-native';
import SwipeableCard from './SwipeableCard';

const DECK = [
  { id: '1', name: 'Biryani Blues', info: 'Hyderabadi - 4.4' },
  { id: '2', name: 'Dosa Plaza', info: 'South Indian - 4.1' },
  { id: '3', name: 'Chaayos', info: 'Cafe - 4.3' },
];

export default function App() {
  const [index, setIndex] = useState(0);              // which card is on top
  const [saved, setSaved] = useState([]);             // right-swiped ids

  // Called after the card has flown away
  const handleSwipe = (dir, item) => {
    if (dir === 'right') setSaved((s) => [...s, item.id]); // save
    setIndex((i) => i + 1);                                // show next
  };

  const card = DECK[index];                           // current card (undefined when done)
  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.stack}>
        {card ? (
          // key forces a fresh animated position per card
          <SwipeableCard key={card.id} item={card} onSwipe={handleSwipe}>
            <Text style={styles.name}>{card.name}</Text>
            <Text>{card.info}</Text>
          </SwipeableCard>
        ) : (
          <Text testID="done">No more cards. Saved: {saved.length}</Text>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  stack: { flex: 1, justifyContent: 'center' },
  name: { fontSize: 22, fontWeight: '700', marginTop: 60 },
});
