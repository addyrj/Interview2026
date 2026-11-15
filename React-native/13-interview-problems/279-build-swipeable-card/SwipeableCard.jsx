// SwipeableCard.jsx — Tinder-style swipe card (Expo SDK 54 / RN 0.81), core RN only
import React, { useMemo, useRef } from 'react';                  // React + hooks
import { Animated, PanResponder, StyleSheet, Text, View, useWindowDimensions } from 'react-native';

// PURE helper: decide what a release means.
// dx = horizontal distance, vx = horizontal velocity, width = screen width
// returns 'left' | 'right' | null (null = snap back)
export function decideSwipe(dx, vx, width) {
  const threshold = width * 0.3;                // must drag 30% of the screen...
  const fast = Math.abs(vx) > 0.8;              // ...or flick fast
  if (dx > threshold || (fast && dx > 20)) return 'right';
  if (dx < -threshold || (fast && dx < -20)) return 'left';
  return null;                                  // not enough: return to center
}

export default function SwipeableCard({ item, onSwipe, children }) {
  const { width } = useWindowDimensions();      // screen width
  const pos = useRef(new Animated.ValueXY()).current; // card position (x, y)

  // Rotate card a little while dragging: -15deg ... +15deg
  const rotate = pos.x.interpolate({
    inputRange: [-width, 0, width],
    outputRange: ['-15deg', '0deg', '15deg'],
  });
  // Show LIKE label when dragging right, NOPE when left
  const likeOpacity = pos.x.interpolate({ inputRange: [0, width * 0.3], outputRange: [0, 1], extrapolate: 'clamp' });
  const nopeOpacity = pos.x.interpolate({ inputRange: [-width * 0.3, 0], outputRange: [1, 0], extrapolate: 'clamp' });

  const panResponder = useMemo(
    () =>
      PanResponder.create({
        // Only start when the finger moves more horizontally than vertically
        // (so vertical ScrollViews around still work)
        onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dx) > 8 && Math.abs(g.dx) > Math.abs(g.dy),
        // Move the card with the finger
        onPanResponderMove: Animated.event([null, { dx: pos.x, dy: pos.y }], { useNativeDriver: false }),
        onPanResponderRelease: (_, g) => {
          const dir = decideSwipe(g.dx, g.vx, width);        // what did the user mean?
          if (dir) {
            // Fly the card off screen, then tell the parent
            Animated.timing(pos, {
              toValue: { x: dir === 'right' ? width * 1.5 : -width * 1.5, y: g.dy },
              duration: 220,
              useNativeDriver: false,                        // ValueXY with event => JS driver
            }).start(() => onSwipe?.(dir, item));
          } else {
            // Snap back with a spring
            Animated.spring(pos, { toValue: { x: 0, y: 0 }, useNativeDriver: false, friction: 6 }).start();
          }
        },
        onPanResponderTerminate: () =>
          Animated.spring(pos, { toValue: { x: 0, y: 0 }, useNativeDriver: false }).start(),
      }),
    [width, item, onSwipe, pos]
  );

  return (
    <Animated.View
      testID="card"
      {...panResponder.panHandlers}
      style={[styles.card, { transform: [{ translateX: pos.x }, { translateY: pos.y }, { rotate }] }]}
    >
      {children}
      {/* Overlay labels */}
      <Animated.View style={[styles.label, styles.like, { opacity: likeOpacity }]}><Text style={styles.labelText}>LIKE</Text></Animated.View>
      <Animated.View style={[styles.label, styles.nope, { opacity: nopeOpacity }]}><Text style={styles.labelText}>NOPE</Text></Animated.View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    position: 'absolute', width: '90%', height: 380, alignSelf: 'center',
    backgroundColor: '#fff', borderRadius: 16, padding: 20,
    shadowColor: '#000', shadowOpacity: 0.15, shadowRadius: 8, elevation: 5, // iOS + Android shadow
  },
  label: { position: 'absolute', top: 24, paddingHorizontal: 10, borderWidth: 3, borderRadius: 6 },
  like: { left: 20, borderColor: '#2ecc71' },
  nope: { right: 20, borderColor: '#e74c3c' },
  labelText: { fontWeight: '800', fontSize: 22 },
});
