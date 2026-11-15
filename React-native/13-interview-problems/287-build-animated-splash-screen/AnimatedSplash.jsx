// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install expo-splash-screen
// Idea: keep native splash visible -> load assets -> hide native splash -> play JS fade/scale -> show app
import React, { useEffect, useRef, useState, useCallback } from 'react'; // hooks
import { View, Text, Animated, StyleSheet } from 'react-native'; // RN core
import * as SplashScreen from 'expo-splash-screen'; // native splash control

SplashScreen.preventAutoHideAsync().catch(() => {}); // keep native splash until we hide it (call at module level)

function Splash({ onFinish }) {
  const opacity = useRef(new Animated.Value(0)).current; // fade value
  const scale = useRef(new Animated.Value(0.6)).current; // scale value

  useEffect(() => {
    Animated.sequence([
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 600, useNativeDriver: true }), // fade in
        Animated.spring(scale, { toValue: 1, useNativeDriver: true }), // pop in
      ]),
      Animated.delay(400), // hold
      Animated.timing(opacity, { toValue: 0, duration: 400, useNativeDriver: true }), // fade out
    ]).start(() => onFinish()); // tell parent we are done
  }, [opacity, scale, onFinish]);

  return (
    <View style={styles.splash}>
      <Animated.View style={{ opacity, transform: [{ scale }] }}>
        <Text style={styles.logo}>MyApp</Text>
      </Animated.View>
    </View>
  );
}

export default function AppWithSplash({ children }) {
  const [ready, setReady] = useState(false); // assets/data loaded
  const [animDone, setAnimDone] = useState(false); // JS animation finished

  useEffect(() => {
    (async () => {
      try {
        await new Promise((r) => setTimeout(r, 500)); // fake load: fonts, tokens, config
      } finally {
        setReady(true); // always continue
      }
    })();
  }, []);

  const onLayout = useCallback(async () => {
    if (ready) await SplashScreen.hideAsync(); // hide native splash once our view is laid out
  }, [ready]);

  const onFinish = useCallback(() => setAnimDone(true), []); // stable callback

  if (!ready) return null; // native splash still showing

  return (
    <View style={styles.flex} onLayout={onLayout}>
      {animDone ? children : <Splash onFinish={onFinish} />}
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 }, // fill
  splash: { flex: 1, backgroundColor: '#E23744', alignItems: 'center', justifyContent: 'center' }, // same colour as native splash
  logo: { color: '#fff', fontSize: 40, fontWeight: '800' }, // logo text
});
