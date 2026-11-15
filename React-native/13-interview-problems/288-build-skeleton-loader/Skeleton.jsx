// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useEffect, useRef } from 'react'; // hooks
import { Animated, View, StyleSheet } from 'react-native'; // RN core

// One grey block that pulses. Reuse with different width/height.
export function SkeletonBox({ width = '100%', height = 16, radius = 6, style }) {
  const opacity = useRef(new Animated.Value(0.4)).current; // pulse value

  useEffect(() => {
    const loop = Animated.loop( // repeat forever
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 700, useNativeDriver: true }), // brighten
        Animated.timing(opacity, { toValue: 0.4, duration: 700, useNativeDriver: true }), // dim
      ])
    );
    loop.start(); // run
    return () => loop.stop(); // cleanup on unmount (avoid leaks)
  }, [opacity]);

  return <Animated.View style={[{ width, height, borderRadius: radius, backgroundColor: '#E1E1E1', opacity }, style]} />;
}

// Skeleton that mimics a restaurant card (same layout as real card = no layout jump)
export function RestaurantCardSkeleton() {
  return (
    <View style={styles.card}>
      <SkeletonBox height={140} radius={12} />
      <SkeletonBox width="60%" height={18} style={{ marginTop: 10 }} />
      <SkeletonBox width="40%" height={14} style={{ marginTop: 6 }} />
    </View>
  );
}

const styles = StyleSheet.create({
  card: { padding: 16 }, // card spacing
});
