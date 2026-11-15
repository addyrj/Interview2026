// NetInfoScreen.jsx — demo that blocks payment while offline
import React from 'react'; // React
import { View, Text, Button, Alert, StyleSheet } from 'react-native'; // UI
import NetInfo from '@react-native-community/netinfo'; // for one-time fetch()
import useNetInfo from './useNetInfo'; // our hook
import OfflineBanner from './OfflineBanner'; // banner

export default function NetInfoScreen() {
  const { isOffline, type, isInternetReachable } = useNetInfo(); // live status

  const pay = async () => {
    const s = await NetInfo.fetch(); // fresh check right before the critical action
    if (!s.isConnected) { Alert.alert('Offline', 'Connect to the internet to pay'); return; }
    Alert.alert('Paying...', 'Request sent'); // real code: call payment API
  };

  return (
    <View style={styles.container}>
      <OfflineBanner />
      <Text>Type: {type}</Text>
      <Text>Reachable: {String(isInternetReachable)}</Text>
      <Button title="Pay Rs 499" onPress={pay} disabled={isOffline} />
    </View>
  );
}

const styles = StyleSheet.create({ container: { flex: 1, paddingTop: 60, gap: 12 } });
