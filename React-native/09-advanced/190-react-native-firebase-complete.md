# 190. React Native + Firebase Complete
# हिंदी में: React Native + Firebase (Auth, Firestore, Storage, Messaging)
# Platform: Both ✅ (Android ✅ | iOS ✅) — Expo Go ❌ (React Native Firebase के लिए dev build)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Library: **React Native Firebase** (`@react-native-firebase/app`, `/auth`, `/firestore`, `/storage`, `/messaging`) — native SDKs wrap करती है। Version-dependent: v22+ में modular API (`getAuth`, `collection`...) recommended है और namespaced API deprecated हो रही है — नीचे modular style है (check current docs)। वैकल्पिक: Firebase JS SDK (Expo Go में चलता है, पर native features सीमित)।

---

## 🔵 Simple Definition (English)
**Firebase** is Google's backend-as-a-service: **Auth** (login), **Firestore** (realtime NoSQL database), **Storage** (files), **Cloud Messaging/FCM** (push), plus Analytics, Crashlytics, Remote Config. **React Native Firebase** connects these native SDKs to RN, so you ship features without writing your own server.

## 🔵 सरल परिभाषा (Hindi)
**Firebase** Google का backend-as-a-service है: **Auth** (login), **Firestore** (realtime NoSQL database), **Storage** (files), **Cloud Messaging/FCM** (push), साथ में Analytics, Crashlytics, Remote Config। **React Native Firebase** इन native SDKs को RN से जोड़ता है, ताकि अपना server बनाए बिना features शिप हों।

---

## 🔴 Problem it Solves
```
❌ Login, DB, file upload, push के लिए अपना backend बनाना = हफ़्ते/महीने
❌ Realtime sync (chat, live order status) खुद बनाना कठिन
❌ Phone OTP, Google sign-in integrate करना जटिल
Firebase:
  ✅ Ready auth providers (Phone OTP, Google, Email)
  ✅ Firestore realtime listeners (onSnapshot)
  ✅ Security Rules से server-side access control
  ✅ FCM push free
```

## 🔴 यह क्यों बना? (Hindi)
```
छोटी टीम को backend बनाने का समय नहीं।
Firebase ready services देता है — login, DB, storage, push।
Realtime sync built-in; rules से सुरक्षा।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Firebase Console में project बनाओ
Step 2 → Android app जोड़ो (package name) → google-services.json डाउनलोड
Step 3 → iOS app जोड़ो (bundle id) → GoogleService-Info.plist डाउनलोड
Step 4 → npm/expo install: @react-native-firebase/app (+ auth, firestore, storage, messaging)
Step 5 → Expo: app.json में googleServicesFile paths + plugins ["@react-native-firebase/app"]
Step 6 → iOS: pod install / EAS Build (use_frameworks static config देखो)
Step 7 → Code: Auth → Firestore → Storage → Messaging
Step 8 → Console में Auth providers enable (Phone/Google/Email)
Step 9 → Firestore Security Rules लिखो (default open मत छोड़ो)
Step 10 → SHA-1/SHA-256 fingerprint Console में जोड़ो (Google Sign-In/Phone Auth के लिए Android)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Config file से app Firebase project पहचानता है।
Native SDK असली काम करता है; JS API उसे call करता है।
Firestore listener data बदलते ही callback देता है।
सुरक्षा Security Rules से — client पर नहीं।
```

---

## 🟡 Real World Example
**Swiggy-जैसा order tracking:** Firestore document `orders/123` में `status` बदलता है (preparing → out_for_delivery); app `onSnapshot` से live UI update करता है। **WhatsApp-जैसा chat:** messages collection + FCM push नए message पर। **Paytm-जैसा Phone OTP login:** Firebase Auth phone sign-in। (असली कंपनियाँ अपना stack भी use करती हैं — यहाँ pattern समझाया गया है।)

## 🟡 Real Example Hindi mein
Order status Firestore में बदलते ही customer app पर live दिखता है (`onSnapshot`)। नया chat message आए तो FCM push। Phone OTP से login — Firebase Auth।

---

## 💻 Code Example — Basic
```jsx
// Modular API (React Native Firebase v22+; पुराने में namespaced auth().signIn...)
import React, { useEffect, useState } from 'react';              // React hooks
import { View, Text, Button, FlatList } from 'react-native';     // UI
import { getAuth, onAuthStateChanged, signInAnonymously, signOut } from '@react-native-firebase/auth';
import { getFirestore, collection, addDoc, query, orderBy, onSnapshot, serverTimestamp }
  from '@react-native-firebase/firestore';

export default function Notes() {
  const [user, setUser] = useState(null);                        // logged-in user
  const [notes, setNotes] = useState([]);                        // realtime list

  // 1) Auth state listen
  useEffect(() => {
    const unsub = onAuthStateChanged(getAuth(), u => setUser(u)); // callback on login/logout
    return unsub;                                                // cleanup
  }, []);

  // 2) Firestore realtime listener (user के notes)
  useEffect(() => {
    if (!user) return undefined;                                 // login के बिना नहीं
    const q = query(
      collection(getFirestore(), 'users', user.uid, 'notes'),    // users/{uid}/notes
      orderBy('createdAt', 'desc'));                             // latest first
    const unsub = onSnapshot(q,
      snap => setNotes(snap.docs.map(d => ({ id: d.id, ...d.data() }))), // docs → array
      err => console.warn('snapshot error', err));               // rules/permission error
    return unsub;                                                // listener बंद
  }, [user]);

  const add = () => addDoc(
    collection(getFirestore(), 'users', user.uid, 'notes'),
    { text: 'New note', createdAt: serverTimestamp() });         // server time

  if (!user) return <Button title="Login (guest)" onPress={() => signInAnonymously(getAuth())} />;
  return (
    <View style={{ padding: 20 }}>
      <Button title="Add note" onPress={add} />
      <FlatList data={notes} keyExtractor={n => n.id} renderItem={({ item }) => <Text>{item.text}</Text>} />
      <Button title="Logout" onPress={() => signOut(getAuth())} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Phone OTP login + Storage upload + FCM push — error handling सहित
import { Platform, PermissionsAndroid } from 'react-native';
import { getAuth, signInWithPhoneNumber } from '@react-native-firebase/auth';
import { getStorage, ref, putFile, getDownloadURL } from '@react-native-firebase/storage';
import { getMessaging, requestPermission, getToken, onMessage, AuthorizationStatus }
  from '@react-native-firebase/messaging';

// ---- 1. Phone OTP ----
let confirmation = null;                                         // OTP confirm object
export async function sendOtp(phone /* +919876543210 */) {
  try {
    confirmation = await signInWithPhoneNumber(getAuth(), phone); // SMS भेजता है
    return true;
  } catch (e) {
    // auth/invalid-phone-number, auth/too-many-requests
    console.warn(e.code, e.message);
    return false;
  }
}
export async function verifyOtp(code) {
  try { await confirmation.confirm(code); return true; }          // login हो गया
  catch (e) { return false; }                                     // गलत OTP
}

// ---- 2. Storage upload (local file path → URL) ----
export async function uploadAvatar(uid, localPath) {
  const r = ref(getStorage(), `avatars/${uid}.jpg`);              // cloud path
  await putFile(r, localPath);                                    // upload (RNFirebase API)
  return getDownloadURL(r);                                       // public URL
}

// ---- 3. Push (FCM) ----
export async function setupPush(saveTokenToServer) {
  const messaging = getMessaging();
  if (Platform.OS === 'android' && Platform.Version >= 33) {      // Android 13+ runtime permission
    await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS);
  }
  const status = await requestPermission(messaging);              // iOS dialog
  const ok = status === AuthorizationStatus.AUTHORIZED || status === AuthorizationStatus.PROVISIONAL;
  if (!ok && Platform.OS === 'ios') return;                       // user ने मना किया
  const token = await getToken(messaging);                        // device FCM token
  await saveTokenToServer(token);                                 // server पर save
  return onMessage(messaging, async msg => {                      // foreground messages
    console.log('FCM foreground', msg.notification?.title);
  });
}
// Background handler index.js में (app component से पहले):
// setBackgroundMessageHandler(getMessaging(), async msg => { /* data-only work */ });
// iOS: APNs key Firebase Console में upload + Push capability ज़रूरी
// Not run here — needs Firebase project, native build, device.
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Config file | `google-services.json` | `GoogleService-Info.plist` |
| Push | FCM सीधे; Android 13+ में POST_NOTIFICATIONS permission | FCM + APNs key; permission dialog; real device चाहिए |
| Phone Auth | SHA-1/SHA-256 ज़रूरी; Play Integrity/reCAPTCHA | APNs/ reCAPTCHA fallback; silent push |
| Google Sign-In | SHA fingerprint | URL scheme (REVERSED_CLIENT_ID) |
| Build step | Gradle plugin `com.google.gms.google-services` | CocoaPods, `use_frameworks` setting |
| Simulator push | Emulator (Google APIs image) OK | Simulator पर FCM/APNs सीमित |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-native-firebase/app @react-native-firebase/auth ...
// app.json:
// { "expo": {
//   "android": { "googleServicesFile": "./google-services.json" },
//   "ios": { "googleServicesFile": "./GoogleService-Info.plist" },
//   "plugins": ["@react-native-firebase/app", "@react-native-firebase/auth"] } }
// iOS static frameworks: expo-build-properties → "ios": { "useFrameworks": "static" }
// Expo Go ❌ → EAS Build development build
// Alternative: Firebase JS SDK (firebase package) — Expo Go में चलता है, पर push/analytics/crashlytics native नहीं
```
CLI way:
```jsx
// npm i @react-native-firebase/app
// Android: google-services.json → android/app/ ;
//   android/build.gradle में google-services classpath, app/build.gradle में apply plugin
// iOS: GoogleService-Info.plist Xcode में add ; AppDelegate में [FIRApp configure] (docs देखो)
// cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Firestore Rules `allow read, write: if true;` छोड़ देना
✅ Correct: `allow read, write: if request.auth != null && request.auth.uid == userId;`

❌ Mistake 2: `onSnapshot` का unsubscribe नहीं करना → memory leak + extra reads (बिल)
✅ Correct: `useEffect` cleanup में unsubscribe

❌ Mistake 3: `.get()` को हर render में call
✅ Correct: Listener/React Query + pagination (`limit`)

❌ Mistake 4: Android SHA-1 नहीं जोड़ा → Google/Phone auth fail
✅ Correct: debug और release (Play App Signing) दोनों SHA Console में

❌ Mistake 5: Config files git में public repo पर commit
✅ Correct: Keys secret नहीं हैं पर Rules सख्त रखो; App Check enable करो

---

## 🧠 Tricky Interview Question
Firestore में 1 chat room के 10,000 messages हैं। `onSnapshot(collection('messages'))` से हर user सब सुन रहा है। क्या दिक्कत है और fix?

Answer: Listener पहली बार सारे 10,000 docs पढ़ता है — हर doc read = बिल + धीमा startup, और memory भारी। Fix: `orderBy('createdAt','desc'), limit(30)` से सिर्फ latest, पुराने के लिए `startAfter` pagination। हर नया message सिर्फ बदलाव (docChanges) के रूप में आता है (incremental), पूरा dataset दोबारा नहीं। साथ में composite index और Security Rules में query constraints।

---

## ⚫ Interview Questions + Answers
Q1: Firestore vs Realtime Database?
A1: Firestore documents/collections, बेहतर queries और scaling, per-read pricing। Realtime DB एक बड़ा JSON tree, बहुत low-latency, सरल पर queries सीमित।

Q2: Security Rules क्यों ज़रूरी?
A2: Client app सीधे DB से बात करता है; rules server-side enforce करते हैं कि कौन क्या पढ़/लिख सकता है। Rules न हों तो कोई भी data चुरा/बदल सकता है।

Q3: React Native Firebase बनाम Firebase JS SDK?
A3: RNFirebase native SDKs use करता है — बेहतर performance, push, Crashlytics, पर dev build चाहिए। JS SDK pure JS, Expo Go में चलता है, पर कई native features नहीं।

Q4: FCM notification vs data message?
A4: Notification message OS खुद दिखाता है (background में); data message app का handler चलाता है (iOS में limited/silent push rules)।

Q5: Offline support?
A5: Firestore में local cache default — offline reads/writes queue होते हैं और online होने पर sync।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- MVP/startup, chat, realtime tracking, quick auth
- Small team, backend नहीं बनाना

❌ Avoid when:
- Complex relational queries/reporting (SQL बेहतर)
- Vendor lock-in चिंता, बहुत बड़ा read-heavy scale (cost)
- Data residency की सख्त शर्तें

---

## 📊 Visual Diagram
```
  RN App ── RNFirebase JS API ── Native Firebase SDK ──► Firebase
   │                                                     ├─ Auth (OTP/Google)
   │◄── onSnapshot (realtime) ───────────────────────────├─ Firestore + Rules
   │──── putFile ────────────────────────────────────────├─ Storage
   │◄── FCM push ────────────────────────────────────────└─ Messaging (APNs on iOS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaaS | Backend as a Service | तैयार backend |
| Firestore | Realtime document DB | Document database |
| Security Rules | Server-side access rules | पहुँच के नियम |
| FCM | Firebase push service | Push सेवा |
| APNs | Apple push network | Apple की push सेवा |
| onSnapshot | Realtime listener | Live सुनने वाला |

---

## ⚡ 3-Line Summary
English: Firebase gives Auth, Firestore, Storage and FCM without your own backend.
Use React Native Firebase with a dev build; unsubscribe listeners and write strict Security Rules.
Paginate Firestore queries to control cost.

Hindi: Firebase बिना अपने backend के Auth, Firestore, Storage और FCM देता है।
React Native Firebase + dev build; listeners unsubscribe करो, सख्त Security Rules लिखो।
Cost घटाने के लिए queries paginate करो।

---

## ➡️ Next Topic
**191. Android App Signing — Complete Guide** — app publish करने की पहली ज़रूरत: signing keys।

---
