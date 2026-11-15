# 13. Creating First App (Expo)
# हिंदी में: पहला App बनाना (Expo से)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 / React Native 0.76 (default template uses expo-router). Expo SDK NN (check current docs — APIs and templates change between SDKs).

---

## 🔵 Simple Definition (English)
Creating your first Expo app means running **`npx create-expo-app@latest`**, which scaffolds a ready project (TypeScript, expo-router, example screens). You start it with **`npx expo start`** and open it on a phone with **Expo Go** or on an emulator.

## 🔵 सरल परिभाषा (Hindi)
पहला Expo app बनाने का मतलब है **`npx create-expo-app@latest`** चलाना, जो TypeScript, expo-router और example screens वाला तैयार project बना देता है। फिर **`npx expo start`** से इसे चलाते हैं और **Expo Go** (फ़ोन) या emulator पर खोलते हैं।

---

## 🔴 Problem it Solves
```
❌ Manually configuring Babel, Metro, TypeScript, navigation = hours
❌ Beginners stuck before writing the first line of UI
❌ Team members start with different folder structures
A single command gives a working, standard project.
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Babel, Metro, TypeScript, navigation हाथ से configure करना = घंटे
❌ Beginners पहली UI line से पहले ही अटक जाते हैं
❌ Team में सबका folder structure अलग
एक command से तैयार और standard project मिल जाता है।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Check Node:            node -v   (Node 18+)

Step 2 → Create:                npx create-expo-app@latest FoodApp

Step 3 → Enter folder:          cd FoodApp

Step 4 → Start Metro:           npx expo start
         Terminal shows a QR code + shortcuts (a, i, w, r, j)

Step 5 → Phone: install "Expo Go" (Play Store / App Store),
         scan the QR (Android: inside Expo Go; iOS: Camera app)
         Phone and laptop must be on the same Wi-Fi

Step 6 → Or press "a" (Android emulator) / "i" (iOS Simulator, Mac)

Step 7 → Edit app/(tabs)/index.tsx, save -> Fast Refresh updates the screen
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Node जाँचें:           node -v   (Node 18+)
Step 2 → बनाएँ:                 npx create-expo-app@latest FoodApp
Step 3 → Folder में जाएँ:       cd FoodApp
Step 4 → Metro start:           npx expo start
         Terminal में QR code और shortcuts (a, i, w, r, j) दिखते हैं
Step 5 → फ़ोन में "Expo Go" install करें और QR scan करें
         (Android: Expo Go के अंदर से; iOS: Camera app से)
         फ़ोन और laptop एक ही Wi-Fi पर हों
Step 6 → या "a" (Android emulator) / "i" (iOS Simulator, Mac) दबाएँ
Step 7 → app/(tabs)/index.tsx edit करें, save करें -> Fast Refresh से screen बदल जाती है
```

### Screen descriptions (what you will see)
- **Terminal after `expo start`:** a big black-and-white QR code, a line "Metro waiting on exp://192.168.x.x:8081" and a menu: "› Press a | open Android", "› Press i | open iOS simulator", "› Press w | open web", "› Press r | reload app", "› Press j | open debugger".
- **Expo Go home (phone):** a "Development servers" list; tapping your machine's entry opens the app. A loading bar "Downloading JavaScript bundle 100%" appears first.
- **Default template app:** tab bar with "Home" and "Explore"; Home shows "Welcome!" with a waving hand and "Step 1: Try it".

---

## 🟡 Real World Example
A founder of a **Swiggy-like** tiffin-delivery MVP creates `npx create-expo-app TiffinApp`, replaces the Home screen with a menu list, shares the QR with the co-founder, and the co-founder sees the app on her phone in seconds, with no build needed.

## 🟡 Real Example Hindi mein
**Swiggy जैसे** tiffin-delivery MVP का founder `npx create-expo-app TiffinApp` चलाता है, Home screen में menu list लगाता है, QR co-founder को भेजता है, और co-founder कुछ ही सेकंड में अपने फ़ोन पर app देख लेती है — कोई build नहीं चाहिए।

---

## 💻 Code Example — Basic

```bash
# Basic: create and run the first Expo app (each line commented)
node -v                              # confirm Node 18+
npx create-expo-app@latest FoodApp   # scaffold the default template (TypeScript + expo-router)
cd FoodApp                           # enter the project folder
npx expo start                       # start Metro, shows QR + shortcuts
# Press "a" for Android emulator, "i" for iOS Simulator, or scan QR with Expo Go
```

## 💻 Code Example — Advanced

```jsx
// Advanced: replace app/index.js with a simple restaurant list screen
// Create a blank-style project first:  npx create-expo-app@latest FoodApp --template blank
// (blank = plain App.js, no router). Below is App.js for that template.
import React, { useEffect, useState } from 'react'; // React hooks
import {
  View, // container
  Text, // text
  FlatList, // efficient list
  ActivityIndicator, // spinner
  StyleSheet, // styles
  Platform, // platform check
  SafeAreaView, // avoid notch
} from 'react-native';
import { StatusBar } from 'expo-status-bar'; // Expo status bar

// Fake API so the example works offline (copy-paste ready)
const fakeFetch = () =>
  new Promise((resolve, reject) =>
    setTimeout(() => {
      // 10% chance to simulate a network failure
      Math.random() < 0.1
        ? reject(new Error('Network error'))
        : resolve([
            { id: '1', name: 'Biryani House', rating: 4.5 },
            { id: '2', name: 'Dosa Corner', rating: 4.3 },
            { id: '3', name: 'Chai Point', rating: 4.1 },
          ]);
    }, 800)
  );

export default function App() {
  const [data, setData] = useState([]); // restaurant list
  const [loading, setLoading] = useState(true); // loading flag
  const [error, setError] = useState(null); // error message

  useEffect(() => {
    let alive = true; // avoid updating after unmount
    fakeFetch()
      .then((r) => alive && setData(r)) // save data
      .catch((e) => alive && setError(e.message)) // save error
      .finally(() => alive && setLoading(false)); // stop spinner
    return () => {
      alive = false; // cleanup
    };
  }, []); // run once

  // Show spinner while loading
  if (loading) return <ActivityIndicator style={styles.center} size="large" />;
  // Show error message if failed
  if (error) return <Text style={styles.center}>Error: {error}</Text>;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="auto" />
      <FlatList
        data={data} // list data
        keyExtractor={(i) => i.id} // unique key
        renderItem={({ item }) => (
          <View style={styles.row}>
            <Text style={styles.name}>{item.name}</Text>
            <Text>⭐ {item.rating}</Text>
          </View>
        )}
      />
    </SafeAreaView>
  );
}

// Styles
const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: Platform.OS === 'android' ? 32 : 0 }, // Android status bar space
  center: { flex: 1, textAlign: 'center', marginTop: 100 }, // centred message
  row: { padding: 16, borderBottomWidth: 1, borderColor: '#eee', flexDirection: 'row', justifyContent: 'space-between' }, // row
  name: { fontSize: 16, fontWeight: '600' }, // name
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Open Expo Go via QR | Scan inside Expo Go app | Scan with the Camera app |
| Emulator shortcut | `a` | `i` (Mac only) |
| Status bar | Not auto-padded in plain View/SafeAreaView | SafeAreaView pads for notch |
| Dev menu | Cmd/Ctrl+M or shake | Cmd+D or shake |
| First run | May need to allow "install unknown apps" for dev APK | Needs Developer Mode on iOS 16+ for dev builds |
| Expo Go availability | Play Store | App Store |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx create-expo-app@latest FoodApp   # create
cd FoodApp && npx expo start         # run, scan QR
```
CLI way:
```bash
npx @react-native-community/cli@latest init FoodApp  # create (see topic 14)
cd FoodApp && npx react-native start                 # Metro
npx react-native run-android                         # in a second terminal
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Phone and laptop on different Wi-Fi networks.
✅ Correct: use the same network, or run `npx expo start --tunnel` (needs `@expo/ngrok`, Expo prompts to install).

❌ Mistake 2: Running `npm install -g expo-cli`.
✅ Correct: the global expo-cli is deprecated; use `npx expo ...` (local CLI).

❌ Mistake 3: Using an old Expo Go version with a new SDK.
✅ Correct: Expo Go supports the latest SDK; upgrade Expo Go or use a dev build.

❌ Mistake 4: Editing the template and being confused by the `app/` folder.
✅ Correct: it is expo-router: file name = route. Use `--template blank` for a plain App.js.

---

## 🧠 Tricky Interview Question
**Q:** "You scan the QR code and Expo Go says 'Could not connect to the server'. The app works in the emulator. What do you check?"

Answer: The phone cannot reach the laptop's LAN IP. Same Wi-Fi? Firewall or VPN blocking port 8081? Router "client isolation" (common on public/office Wi-Fi)? Fix: disable the VPN/firewall rule or use `npx expo start --tunnel`.

---

## ⚫ Interview Questions + Answers
Q1: What does create-expo-app generate?
A1: A project with `package.json`, `app.json`, TypeScript config, assets and example screens (expo-router by default).

Q2: What is Expo Go?
A2: A prebuilt app that loads your JS bundle, with a fixed set of native modules.

Q3: How is Fast Refresh triggered?
A3: Saving a file; Metro sends an update and the app re-renders changed components, keeping state when possible.

Q4: How to make a blank project?
A4: `npx create-expo-app@latest MyApp --template blank`.

Q5: What does `--tunnel` do?
A5: Exposes Metro through a public tunnel so devices on other networks can connect.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Learning, prototypes, MVPs
- Need to share a demo quickly

❌ Avoid Expo Go when:
- Using custom native libraries (make a dev build)
- Testing push notifications on newer SDKs (use a dev build)

---

## 📊 Visual Diagram
```
 create-expo-app ─► project ─► npx expo start ─► Metro (8081)
                                         │
                   ┌─────────────────────┼─────────────────┐
                 QR ► Expo Go (phone)   "a" ► Android emu  "i" ► iOS Sim
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| create-expo-app | Project generator | Project बनाने का tool |
| Expo Go | Sandbox testing app | Testing वाला app |
| Metro | JS bundler/dev server | JS bundle बनाने वाला server |
| QR code | Quick link to dev server | Dev server का shortcut |
| Tunnel | Public URL for Metro | Metro का public रास्ता |
| Template | Starter project | शुरुआती project |

---

## ⚡ 3-Line Summary
English: Run create-expo-app, cd into the project and run npx expo start.
Open on Expo Go via QR or on an emulator with a/i.
Edit a file and Fast Refresh shows changes instantly.

Hindi: create-expo-app चलाएँ, project में जाएँ और npx expo start चलाएँ।
QR से Expo Go में या a/i से emulator में खोलें।
File बदलें और Fast Refresh तुरंत बदलाव दिखा देता है।

---

## ➡️ Next Topic
**14. Creating First App (CLI)** — the same idea with the bare React Native CLI.

---
