// useNotification.js — permission + Expo push token + listeners (expo-notifications)
import { useEffect, useRef, useState } from 'react'; // hooks
import { Platform } from 'react-native'; // OS check
import * as Notifications from 'expo-notifications'; // notifications API
import * as Device from 'expo-device'; // is this a real phone?
import Constants from 'expo-constants'; // reads app.json / EAS config

// Show banner + sound even when app is open (set ONCE, outside the hook)
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true, // older SDKs
    shouldShowBanner: true, // newer SDKs (SDK 53+ split alert into banner/list) — unknown keys are ignored
    shouldShowList: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

async function registerForPush() {
  if (Platform.OS === 'android') {
    // Android 8+ needs a channel BEFORE asking permission (Android 13+ prompt appears after channel exists)
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
    });
  }
  if (!Device.isDevice) throw new Error('Push needs a physical device'); // push tokens do not work on emulators

  const existing = await Notifications.getPermissionsAsync(); // current status
  let status = existing.status;
  if (status !== 'granted') {
    status = (await Notifications.requestPermissionsAsync()).status; // OS dialog
  }
  if (status !== 'granted') throw new Error('Notification permission denied');

  // projectId comes from EAS (app.json -> extra.eas.projectId)
  const projectId = Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId;
  if (!projectId) throw new Error('Missing EAS projectId');
  const token = (await Notifications.getExpoPushTokenAsync({ projectId })).data; // "ExponentPushToken[xxxx]"
  return token;
}

export default function useNotification() {
  const [expoPushToken, setToken] = useState(null); // send this to your backend
  const [notification, setNotification] = useState(null); // last received while app open
  const [lastResponse, setLastResponse] = useState(null); // last notification the user TAPPED
  const [error, setError] = useState(null); // permission/token error
  const receivedSub = useRef(null); // subscription refs for cleanup
  const responseSub = useRef(null);

  useEffect(() => {
    registerForPush().then(setToken).catch((e) => setError(e.message)); // get token once

    receivedSub.current = Notifications.addNotificationReceivedListener(setNotification); // foreground arrival
    responseSub.current = Notifications.addNotificationResponseReceivedListener(setLastResponse); // user tap

    return () => { // cleanup
      receivedSub.current?.remove();
      responseSub.current?.remove();
    };
  }, []);

  // Local test notification (no server needed)
  const scheduleLocal = (title, body, seconds = 2) =>
    Notifications.scheduleNotificationAsync({
      content: { title, body, data: { screen: 'Orders' } }, // data used for deep-linking
      trigger: { type: Notifications.SchedulableTriggerInputTypes?.TIME_INTERVAL ?? 'timeInterval', seconds }, // SDK 52+ needs `type`
    });

  return { expoPushToken, notification, lastResponse, error, scheduleLocal };
}
