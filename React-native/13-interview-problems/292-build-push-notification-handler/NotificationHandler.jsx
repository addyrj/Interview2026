// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install expo-notifications expo-device expo-constants
// Remote push does NOT work in Expo Go on Android (SDK 53+) -> use a development build.
// Physical device required for push tokens. Needs EAS projectId + FCM (Android) / APNs (iOS) credentials.
import { useEffect, useRef } from 'react'; // hooks
import { Platform } from 'react-native'; // platform check
import * as Notifications from 'expo-notifications'; // notifications
import * as Device from 'expo-device'; // device info
import Constants from 'expo-constants'; // projectId

// How to show a notification while the app is OPEN (foreground). Call once at module level.
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true, // SDK <=52; in SDK 53+ use shouldShowBanner + shouldShowList
    shouldPlaySound: true, // play sound
    shouldSetBadge: false, // no badge change
  }),
});

async function registerForPush() {
  if (Platform.OS === 'android') { // Android 8+ needs a channel BEFORE asking token/permission (Android 13+)
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Default', // shown in settings
      importance: Notifications.AndroidImportance.MAX, // heads-up
    });
  }
  if (!Device.isDevice) return null; // simulator cannot get token
  let { status } = await Notifications.getPermissionsAsync(); // current permission
  if (status !== 'granted') ({ status } = await Notifications.requestPermissionsAsync()); // ask user
  if (status !== 'granted') return null; // denied
  const projectId = Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId; // EAS project
  const token = await Notifications.getExpoPushTokenAsync({ projectId }); // Expo push token
  return token.data; // "ExponentPushToken[xxxx]" -> send to your backend
}

// onOpen(data) is called when user taps a notification -> navigate to the right screen
export function useNotificationHandler(onOpen, onToken) {
  const received = useRef(null); // foreground listener subscription
  const response = useRef(null); // tap listener subscription

  useEffect(() => {
    registerForPush().then((t) => t && onToken?.(t)).catch((e) => console.warn('Push setup failed', e)); // get token

    received.current = Notifications.addNotificationReceivedListener((n) => {
      console.log('Foreground notification', n.request.content.title); // app open
    });
    response.current = Notifications.addNotificationResponseReceivedListener((r) => {
      onOpen?.(r.notification.request.content.data); // user tapped
    });
    // App killed -> opened by tap: read the last response once
    Notifications.getLastNotificationResponseAsync().then((r) => r && onOpen?.(r.notification.request.content.data));

    return () => { // cleanup
      received.current?.remove(); // remove listener
      response.current?.remove(); // remove listener
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
}
