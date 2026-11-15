// DragDropList.jsx — reorder a list by dragging the handle (core RN: Animated + PanResponder)
// Fixed row height keeps the maths simple. For production lists use
// react-native-reanimated + gesture-handler libraries (e.g. react-native-draggable-flatlist).
import React, { useRef, useState } from 'react';                 // React + hooks
import { Animated, PanResponder, ScrollView, StyleSheet, Text, View } from 'react-native';
import { moveItem, targetIndex } from './reorder';               // pure helpers

const ROW_H = 56;                                                // fixed row height in px

function Row({ item, index, count, onMoveEnd, onDragState }) {
  const dy = useRef(new Animated.Value(0)).current;              // drag offset for this row
  const [active, setActive] = useState(false);                   // is this row being dragged?

  const pan = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,                  // handle claims the touch
      onPanResponderGrant: () => { setActive(true); onDragState(true); }, // lock parent scroll
      onPanResponderMove: Animated.event([null, { dy }], { useNativeDriver: false }),
      onPanResponderRelease: (_, g) => {
        const to = targetIndex(index, g.dy, ROW_H, count);       // where did we drop?
        setActive(false); onDragState(false);                    // unlock scroll
        dy.setValue(0);                                          // reset visual offset (list re-renders in new order)
        onMoveEnd(index, to);                                    // tell parent to reorder
      },
      onPanResponderTerminate: () => { setActive(false); onDragState(false); Animated.spring(dy, { toValue: 0, useNativeDriver: false }).start(); },
    })
  ).current;
  // NOTE: `index`/`count` are read inside the handlers; Row is keyed by item.id and re-created
  // on reorder, so we rebuild the responder each render via the key trick in the parent.

  return (
    <Animated.View
      testID={`row-${item.id}`}
      style={[styles.row, active && styles.active, { transform: [{ translateY: dy }], zIndex: active ? 10 : 0 }]}
    >
      <Text style={styles.title}>{item.title}</Text>
      {/* Only the handle starts the drag */}
      <View {...pan.panHandlers} style={styles.handle} testID={`handle-${item.id}`}>
        <Text style={styles.grip}>≡</Text>
      </View>
    </Animated.View>
  );
}

export default function DragDropList({ initial }) {
  const [items, setItems] = useState(initial);                   // list state
  const [dragging, setDragging] = useState(false);               // true while a row is dragged

  const handleMoveEnd = (from, to) => setItems((list) => moveItem(list, from, to));

  return (
    <ScrollView style={styles.container} testID="list" scrollEnabled={!dragging}>
      {items.map((item, i) => (
        // key includes index so Row (and its PanResponder closure) refresh after each reorder
        <Row key={`${item.id}-${i}`} item={item} index={i} count={items.length}
             onMoveEnd={handleMoveEnd} onDragState={setDragging} />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  row: {
    height: ROW_H, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    backgroundColor: '#fff', paddingHorizontal: 14, marginBottom: 0,
    borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ddd',
  },
  active: { backgroundColor: '#fff7e6', elevation: 6, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 6 },
  title: { fontSize: 16 },
  handle: { width: 48, height: ROW_H, alignItems: 'center', justifyContent: 'center' }, // 48px touch target
  grip: { fontSize: 24, color: '#888' },
});
