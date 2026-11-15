// LocationScreen.jsx — uses useLocation; Zomato-style "Deliver to"
import React from 'react'; // React
import { View, Text, Button, ActivityIndicator, Linking, StyleSheet } from 'react-native'; // UI
import useLocation from './useLocation'; // our hook

export default function LocationScreen() {
  const { coords, error, loading, permission, refresh } = useLocation(); // one-time fetch
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Deliver to</Text>
      {loading && <ActivityIndicator />}
      {coords && (
        <Text testID="coords">{coords.latitude.toFixed(4)}, {coords.longitude.toFixed(4)}</Text>
      )}
      {error && <Text style={styles.error}>{error}</Text>}
      {permission === 'denied' && (
        // After "Don't ask again" the OS dialog won't show; send user to Settings
        <Button title="Open Settings" onPress={() => Linking.openSettings()} />
      )}
      <Button title="Refresh" onPress={refresh} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, paddingTop: 60, gap: 12 },
  title: { fontSize: 22, fontWeight: '700' },
  error: { color: '#b91c1c' },
});
