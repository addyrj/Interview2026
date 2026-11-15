// BottomSheet.jsx — reusable bottom sheet with snap points (Expo SDK 54 / RN 0.81)
// Uses only core RN: Animated + PanResponder (no extra libraries). Works on Android + iOS.
import React, { useEffect, useMemo, useRef } from 'react';      // React + hooks
import {
  Animated,        // animation engine
  PanResponder,    // gesture handling for the drag handle
  Pressable,       // tappable backdrop
  StyleSheet,      // styles
  View,            // layout
  useWindowDimensions, // screen height (updates on rotation)
  Platform,        // platform checks
} from 'react-native';

// PURE helper: given a position, velocity and list of snap positions,
// return the snap position the sheet should settle at.
// y = current translateY, vy = release velocity (px/ms), positions = array of translateY values
export function pickSnap(y, vy, positions) {
  // Project where the sheet would end up if it kept moving a little (inertia)
  const projected = y + vy * 120;
  // Find the closest snap position to the projected spot
  return positions.reduce(
    (best, p) => (Math.abs(p - projected) < Math.abs(best - projected) ? p : best),
    positions[0]
  );
}

// PURE helper: clamp a number between min and max
export const clamp = (n, min, max) => Math.min(Math.max(n, min), max);

export default function BottomSheet({
  visible,                    // boolean: should the sheet be open?
  onClose,                    // called when the sheet is dismissed
  snapPoints = [0.4, 0.85],   // visible height as FRACTION of screen (sorted small -> large)
  children,                   // content inside the sheet
}) {
  const { height: screenH } = useWindowDimensions();            // current screen height
  const sheetH = screenH * snapPoints[snapPoints.length - 1];   // sheet is as tall as the biggest snap
  // translateY positions: 0 = fully open at biggest snap, sheetH = hidden below screen
  const positions = useMemo(
    () => [...snapPoints.map((f) => sheetH - screenH * f), sheetH], // last item = closed
    [snapPoints, sheetH, screenH]
  );
  const openPositions = positions.slice(0, -1);                 // without "closed"
  const closedY = sheetH;                                       // hidden position

  const translateY = useRef(new Animated.Value(closedY)).current; // starts hidden
  const currentY = useRef(closedY);                             // plain number copy of the value
  const startY = useRef(closedY);                               // value when the drag began

  // Keep currentY in sync with the animated value
  useEffect(() => {
    const id = translateY.addListener(({ value }) => { currentY.current = value; });
    return () => translateY.removeListener(id);                 // cleanup listener
  }, [translateY]);

  // Animate to a position; call onClose if we ended hidden
  const snapTo = (toValue, velocity = 0) => {
    Animated.spring(translateY, {
      toValue,                       // target position
      velocity,                      // carry the finger's speed
      useNativeDriver: true,         // run on UI thread (transform is supported)
      bounciness: 0,                 // no wobble
    }).start(() => { if (toValue === closedY) onClose?.(); });
  };

  // Open / close when `visible` changes
  useEffect(() => {
    snapTo(visible ? openPositions[0] : closedY);               // open to first snap
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible, screenH]);

  // Gesture handler attached to the drag handle area
  const pan = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => true,               // claim the touch
        onPanResponderGrant: () => {
          translateY.stopAnimation();                           // stop running spring
          startY.current = currentY.current;                    // remember start
        },
        onPanResponderMove: (_, g) => {
          // follow the finger but never above fully-open position
          translateY.setValue(clamp(startY.current + g.dy, openPositions[openPositions.length - 1], closedY));
        },
        onPanResponderRelease: (_, g) => {
          snapTo(pickSnap(currentY.current, g.vy, positions), g.vy); // settle on nearest snap
        },
        onPanResponderTerminate: () => snapTo(pickSnap(currentY.current, 0, positions)),
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [positions]
  );

  // Backdrop fades in as the sheet rises
  const backdropOpacity = translateY.interpolate({
    inputRange: [0, closedY],     // open -> closed
    outputRange: [0.5, 0],        // dim -> clear
    extrapolate: 'clamp',         // never outside range
  });

  return (
    // box-none: wrapper itself never blocks touches; only children do
    <View style={StyleSheet.absoluteFill} pointerEvents={visible ? 'auto' : 'none'}>
      {/* Dark backdrop; tapping it closes the sheet */}
      <Animated.View style={[styles.backdrop, { opacity: backdropOpacity }]}>
        <Pressable style={StyleSheet.absoluteFill} onPress={() => snapTo(closedY)} testID="backdrop" />
      </Animated.View>

      {/* The sheet itself */}
      <Animated.View
        testID="sheet"
        style={[styles.sheet, { height: sheetH, transform: [{ translateY }] }]}
      >
        {/* Drag handle: only this area responds to the pan gesture */}
        <View {...pan.panHandlers} style={styles.handleArea} testID="handle">
          <View style={styles.handle} />
        </View>
        {/* Sheet content */}
        <View style={styles.content}>{children}</View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  backdrop: { ...StyleSheet.absoluteFillObject, backgroundColor: '#000' }, // full-screen dim layer
  sheet: {
    position: 'absolute', left: 0, right: 0, bottom: 0,   // stick to bottom
    backgroundColor: '#fff',
    borderTopLeftRadius: 20, borderTopRightRadius: 20,     // rounded top corners
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 10, shadowOffset: { width: 0, height: -3 } },
      android: { elevation: 16 },                          // Android shadow
      default: {},
    }),
  },
  handleArea: { paddingVertical: 12, alignItems: 'center' }, // big touch area (44px+ tall)
  handle: { width: 40, height: 5, borderRadius: 3, backgroundColor: '#ccc' }, // grey pill
  content: { flex: 1, paddingHorizontal: 16 },
});
