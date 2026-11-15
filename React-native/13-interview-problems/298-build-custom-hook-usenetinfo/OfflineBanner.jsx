// OfflineBanner.jsx — red bar shown while offline (Paytm / PhonePe style)
import React from 'react'; // React
import { Text, StyleSheet } from 'react-native'; // UI
import useNetInfo from './useNetInfo'; // our hook

export default function OfflineBanner() {
  const { isOffline, type } = useNetInfo(); // network status
  if (!isOffline) return null; // online -> render nothing
  return <Text style={styles.banner} testID="offline">No internet connection ({type})</Text>;
}

const styles = StyleSheet.create({
  banner: { backgroundColor: '#b91c1c', color: '#fff', textAlign: 'center', padding: 8 },
});
