// NotificationScreen.jsx — demo for useNotification
import React from 'react'; // React
import { View, Text, Button, StyleSheet } from 'react-native'; // UI
import useNotification from './useNotification'; // our hook

export default function NotificationScreen() {
  const { expoPushToken, notification, lastResponse, error, scheduleLocal } = useNotification();
  return (
    <View style={styles.container}>
      <Text selectable>Token: {expoPushToken ?? 'loading...'}</Text>
      {error && <Text style={styles.error}>{error}</Text>}
      <Text>Last: {notification?.request.content.title ?? '-'}</Text>
      <Text>Tapped: {lastResponse?.notification.request.content.title ?? '-'}</Text>
      <Button title="Test in 2s" onPress={() => scheduleLocal('Order out for delivery', 'Arrives in 10 min')} />
    </View>
  );
}

const styles = StyleSheet.create({ container: { flex: 1, padding: 24, paddingTop: 60, gap: 12 }, error: { color: 'red' } });
