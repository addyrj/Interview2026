# 14. Creating First App (CLI)
# हिंदी में: पहला App बनाना (React Native CLI से)
# Platform: Android ✅ | iOS ✅ (iOS needs Mac) | Both ✅

> Target: React Native 0.76 via `@react-native-community/cli`. Expo SDK NN (check current docs — APIs change between SDKs). Note: the RN team now recommends a framework (Expo) for new apps; the CLI path is still supported.

---

## 🔵 Simple Definition (English)
Creating an app with the **React Native CLI** means running `npx @react-native-community/cli@latest init MyApp`. You get a project with real **`android/`** and **`ios/`** native folders, so you build with Gradle and Xcode yourself.

## 🔵 सरल परिभाषा (Hindi)
**React Native CLI** से app बनाने का मतलब है `npx @react-native-community/cli@latest init MyApp` चलाना। आपको असली **`android/`** और **`ios/`** native folders वाला project मिलता है, और आप Gradle व Xcode से खुद build करते हैं।

---

## 🔴 Problem it Solves
```
❌ Expo Go / managed flow limits full native control
❌ Need to add native code in Kotlin/Java/Swift/ObjC directly
❌ Existing native team wants standard native projects
CLI gives full control from the first minute.
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Expo Go / managed flow में पूरा native control सीमित है
❌ Kotlin/Java/Swift/ObjC में सीधा native code जोड़ना है
❌ पुरानी native team को standard native projects चाहिए
CLI पहले मिनट से पूरा control देता है।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prerequisites ready: Node, JDK 17, Android Studio (+ Xcode, CocoaPods on Mac)

Step 2 → Create:   npx @react-native-community/cli@latest init ShopApp
         (the CLI also runs pod install on Mac)

Step 3 → Enter:    cd ShopApp

Step 4 → Start Metro:  npx react-native start    (terminal 1)

Step 5 → Android:  start an emulator, then
                   npx react-native run-android   (terminal 2)

Step 6 → iOS (Mac): npx react-native run-ios

Step 7 → Edit App.tsx, save -> Fast Refresh
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Prerequisites तैयार: Node, JDK 17, Android Studio (Mac पर Xcode, CocoaPods)
Step 2 → बनाएँ: npx @react-native-community/cli@latest init ShopApp
         (Mac पर CLI खुद pod install भी चलाता है)
Step 3 → Folder में जाएँ: cd ShopApp
Step 4 → Metro start: npx react-native start   (terminal 1)
Step 5 → Android: emulator चालू करें, फिर
         npx react-native run-android          (terminal 2)
Step 6 → iOS (Mac): npx react-native run-ios
Step 7 → App.tsx edit करें, save करें -> Fast Refresh
```

### Screen descriptions (what you will see)
- **Terminal during init:** step list with "Downloading template", "Copying template", "Processing template", "Installing dependencies", "Installing CocoaPods dependencies (this may take a few minutes)" and finally "Run instructions for Android / iOS".
- **Metro terminal:** the React Native ASCII logo and "Welcome to Metro"; keys: `r` reload, `d` open dev menu.
- **First screen on device:** the default "Welcome to React Native" page with "Step One / See Your Changes / Debug / Learn More" sections.

---

## 🟡 Real World Example
A bank like **HDFC / a Paytm-style fintech** adding an RN module to an existing native Android and iOS app uses CLI-style native projects, because their app already contains proprietary SDKs, custom Gradle flavors and security libraries. They need to edit `build.gradle` and the Xcode project directly.

## 🟡 Real Example Hindi mein
**HDFC / Paytm जैसी fintech** अपने मौजूदा native Android और iOS app में RN module जोड़ती है, तो CLI-style native projects use करती है, क्योंकि उनके app में proprietary SDKs, custom Gradle flavors और security libraries पहले से हैं। उन्हें `build.gradle` और Xcode project सीधे बदलना पड़ता है।

---

## 💻 Code Example — Basic

```bash
# Basic: create and run a CLI app (each line commented)
npx @react-native-community/cli@latest init ShopApp   # create project with android/ + ios/
cd ShopApp                                           # enter project
npx react-native start                               # terminal 1: Metro bundler
npx react-native run-android                         # terminal 2: build + install on Android
npx react-native run-ios                             # Mac only: build + run on iOS Simulator
```

## 💻 Code Example — Advanced

```jsx
// Advanced: App.tsx for the CLI template -> product list with Platform-specific styling
// (The CLI template is TypeScript by default.)
import React, { useCallback, useState } from 'react'; // React hooks
import {
  FlatList, // list
  Platform, // platform check
  RefreshControl, // pull to refresh
  SafeAreaView, // safe area
  StatusBar, // status bar control
  StyleSheet, // styles
  Text, // text
  View, // container
} from 'react-native';

// Product type
type Product = { id: string; title: string; price: number };

// Initial data
const initial: Product[] = [
  { id: '1', title: 'Boat Earbuds', price: 1299 },
  { id: '2', title: 'Fastrack Watch', price: 1999 },
  { id: '3', title: 'Puma Shoes', price: 3499 },
];

function App(): React.JSX.Element {
  const [items, setItems] = useState<Product[]>(initial); // list state
  const [refreshing, setRefreshing] = useState(false); // refresh flag

  // Pull-to-refresh handler (simulated)
  const onRefresh = useCallback(() => {
    setRefreshing(true); // show spinner
    setTimeout(() => {
      setItems((prev) => [...prev].reverse()); // fake reload by reversing
      setRefreshing(false); // hide spinner
    }, 700);
  }, []);

  return (
    <SafeAreaView style={styles.safe}>
      {/* Dark text on light background, Android needs explicit colour */}
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <FlatList
        data={items} // data
        keyExtractor={(p) => p.id} // key
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />} // pull refresh
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.title}>{item.title}</Text>
            <Text>Rs {item.price}</Text>
          </View>
        )}
      />
    </SafeAreaView>
  );
}

// Styles
const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#fff' }, // full screen
  card: {
    margin: 12, // outer space
    padding: 16, // inner space
    borderRadius: 10, // rounded
    backgroundColor: '#fff', // card colour
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 6, shadowOffset: { width: 0, height: 2 } }, // iOS shadow
      android: { elevation: 3 }, // Android shadow
    }),
  },
  title: { fontWeight: '700', marginBottom: 4 }, // title
});

export default App; // default export used by index.js
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Run command | `npx react-native run-android` | `npx react-native run-ios` |
| Native folder | `android/` (Gradle, Kotlin) | `ios/` (Xcode, Swift/ObjC, Pods) |
| Dependency step | Gradle sync (automatic) | `pod install` (often automatic after init) |
| Entry file | `MainActivity.kt` + `MainApplication.kt` | `AppDelegate.swift`/`.mm` |
| Min requirements | JDK 17, Android SDK | Xcode, CocoaPods |
| Metro connection | `adb reverse` helps | Simulator uses localhost directly |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx create-expo-app@latest ShopApp   # create
npx expo start                        # run (Expo Go) - no native folders yet
npx expo run:android                  # creates android/ on demand (prebuild)
```
CLI way:
```bash
npx @react-native-community/cli@latest init ShopApp  # android/ + ios/ right away
npx react-native run-android                         # builds with Gradle
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `npx react-native init ShopApp` (old global command).
✅ Correct: use `npx @react-native-community/cli@latest init ShopApp`.

❌ Mistake 2: Not starting Metro or an emulator before `run-android`.
✅ Correct: start an AVD (or plug a device) and check `adb devices`.

❌ Mistake 3: Skipping `pod install` after adding libraries.
✅ Correct: `cd ios && bundle exec pod install`.

❌ Mistake 4: Committing `local.properties` and `Pods/` of your machine.
✅ Correct: keep them in `.gitignore` (the template already does).

---

## 🧠 Tricky Interview Question
**Q:** "`run-android` fails with 'SDK location not found'. Metro and emulator are fine. What is the fix?"

Answer: Gradle cannot find the Android SDK. Set `ANDROID_HOME` or create `android/local.properties` with `sdk.dir=/path/to/Android/sdk`. Metro is irrelevant here because the failure happens at the native build stage.

---

## ⚫ Interview Questions + Answers
Q1: What is in the CLI template that Expo's blank template hides?
A1: Real `android/` and `ios/` folders, Gradle/Podfile, MainActivity/AppDelegate.

Q2: Why is `react-native init` deprecated?
A2: The community CLI is now invoked with its package name; the RN docs recommend frameworks like Expo.

Q3: How do you pick the Android device?
A3: `npx react-native run-android --deviceId <id>` using ids from `adb devices`.

Q4: What does Metro do?
A4: Bundles JS and serves it to the app; supports Fast Refresh.

Q5: How can you set a custom app name?
A5: `app.json` "displayName" for the JS name, and strings.xml / Info.plist for the launcher name.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must edit native code heavily
- Integrating into an existing native app

❌ Avoid when:
- Beginner or small team needing speed
- No Mac but need iOS (EAS Build with Expo is simpler)

---

## 📊 Visual Diagram
```
 init ─► ShopApp/
          ├── android/  (Gradle)  ──► run-android ─► APK on emulator
          ├── ios/      (Xcode)   ──► run-ios     ─► Simulator
          ├── App.tsx
          └── index.js  (registerComponent)
 Metro :8081 ──► JS bundle ──► app
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CLI | Command line interface | Command से चलाने वाला tool |
| Gradle | Android build tool | Android build tool |
| Podfile | iOS dependency list | iOS dependencies की list |
| Metro | JS bundler | JS bundler |
| local.properties | Local SDK path file | SDK path की file |
| AppDelegate | iOS app entry | iOS का entry point |

---

## ⚡ 3-Line Summary
English: `npx @react-native-community/cli@latest init` creates a project with native folders.
Run Metro, then run-android or run-ios.
You get full native control but must maintain native tooling.

Hindi: `npx @react-native-community/cli@latest init` native folders वाला project बनाता है।
Metro चलाएँ, फिर run-android या run-ios।
पूरा native control मिलता है पर native tooling खुद संभालनी पड़ती है।

---

## ➡️ Next Topic
**15. Project Structure — Complete Guide** — understand every file and folder you just generated.

---
