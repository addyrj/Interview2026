// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useState } from 'react'; // state
import { View, Text, Button } from 'react-native'; // RN core
import * as Notifications from 'expo-notifications'; // notifications
import { useNotificationHandler } from './NotificationHandler'; // hook

export default function PushDemoScreen() {
  const [token, setToken] = useState(''); // push token
  const [last, setLast] = useState(null); // last tapped data

  useNotificationHandler((data) => setLast(data), setToken); // wire hook (use navigation.navigate here in real app)

  // Local notification test (works without server)
  const test = () =>
    Notifications.scheduleNotificationAsync({
      content: { title: 'Order on the way', body: 'Rider is 5 mins away', data: { orderId: '42' } }, // payload
      trigger: { seconds: 2 }, // after 2s (newer SDKs may want type: 'timeInterval' - check docs)
    });

  return (
    <View style={{ flex: 1, padding: 20, justifyContent: 'center' }}>
      <Text selectable>Token: {token || 'not available'}</Text>
      <Text>Last tap: {last ? JSON.stringify(last) : '-'}</Text>
      <Button title="Send local test" onPress={test} />
    </View>
  );
}
