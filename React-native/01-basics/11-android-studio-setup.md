# 11. Android Studio Setup
# हिंदी में: Android Studio Setup (SDK + Emulator)
# Platform: Android ✅ | iOS ❌ | Android only (works on Mac/Windows/Linux)

> Target: Expo SDK 52 / React Native 0.76 (Android compileSdk 35 in recent templates; check your template's `build.gradle`). Expo SDK NN (check current docs — required SDK/NDK versions change between SDKs).

---

## 🔵 Simple Definition (English)
**Android Studio** is Google's official IDE. For React Native you mainly need it for the **Android SDK**, **platform-tools (adb)**, **build-tools** and the **Android Virtual Device (AVD) emulator**, not for writing JS code.

## 🔵 सरल परिभाषा (Hindi)
**Android Studio** Google का official IDE है। React Native में इसकी ज़रूरत मुख्य रूप से **Android SDK**, **platform-tools (adb)**, **build-tools** और **Android Virtual Device (AVD) emulator** के लिए होती है, JS code लिखने के लिए नहीं।

---

## 🔴 Problem it Solves
```
❌ Cannot run the app on an Android emulator
❌ Gradle cannot find Android SDK / build-tools
❌ No adb to install the APK or read logs
❌ Testing only on one physical phone (different screen sizes missed)
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ App को Android emulator पर नहीं चला सकते
❌ Gradle को Android SDK / build-tools नहीं मिलते
❌ APK install करने या logs देखने के लिए adb नहीं
❌ सिर्फ एक phone पर test = अलग screen sizes छूट जाते हैं
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Download Android Studio from developer.android.com/studio and install

Step 2 → First launch wizard: choose "Standard" install
         (installs SDK, platform-tools, emulator)

Step 3 → Open More Actions -> SDK Manager (Settings -> Languages & Frameworks
         -> Android SDK)
         SDK Platforms tab: tick a recent Android version (e.g. Android 15 "VanillaIceCream", API 35)
         SDK Tools tab: tick Android SDK Build-Tools, Platform-Tools,
         Emulator, Command-line Tools (latest)

Step 4 → Set ANDROID_HOME and PATH (see topic 10)

Step 5 → Device Manager -> Create Device -> choose Pixel -> choose a
         system image (x86_64 on Intel / Windows, arm64 on Apple Silicon)

Step 6 → Press Play on the device to boot the emulator

Step 7 → Run the app: npx expo start -> press "a"
         or npx react-native run-android
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → developer.android.com/studio से Android Studio download + install
Step 2 → पहली बार wizard में "Standard" install चुनें (SDK, platform-tools, emulator)
Step 3 → SDK Manager खोलें (Settings -> Languages & Frameworks -> Android SDK)
         SDK Platforms: एक नया Android version (जैसे API 35) tick करें
         SDK Tools: Build-Tools, Platform-Tools, Emulator, Command-line Tools tick करें
Step 4 → ANDROID_HOME और PATH सेट करें (topic 10)
Step 5 → Device Manager -> Create Device -> Pixel चुनें -> system image
         (Intel/Windows पर x86_64, Apple Silicon पर arm64)
Step 6 → Device पर Play दबाकर emulator boot करें
Step 7 → App चलाएँ: npx expo start -> "a" दबाएँ
         या npx react-native run-android
```

### Screen descriptions (what you will see)
- **Welcome screen:** dark window with buttons "New Project", "Open", and a three-dot "More Actions" menu; SDK Manager and Virtual Device Manager are under More Actions.
- **SDK Manager:** a settings dialog with two tabs, "SDK Platforms" (list of Android versions with checkboxes) and "SDK Tools" (list of tools with checkboxes); a line at top shows "Android SDK Location" (copy this for ANDROID_HOME).
- **Device Manager:** a list of virtual devices with a green Play triangle; "Create Device" opens a phone catalogue, then a system image picker with a Download link.

---

## 🟡 Real World Example
A QA engineer at a **Paytm-like** company must test the checkout on a small 5-inch screen and a big tablet. In Device Manager she creates a "Pixel 4a" and a "Pixel Tablet" emulator, runs the same app on both and finds a button cut off on the small screen, without buying devices.

## 🟡 Real Example Hindi mein
**Paytm जैसी** company की QA engineer को checkout 5-inch छोटी screen और बड़े tablet दोनों पर test करना है। Device Manager में वह "Pixel 4a" और "Pixel Tablet" emulator बनाती है, एक ही app दोनों पर चलाती है और छोटी screen पर कटा हुआ button पकड़ लेती है — बिना कोई device ख़रीदे।

---

## 💻 Code Example — Basic

```bash
# Basic: verify the Android toolchain from terminal (every line commented)
echo $ANDROID_HOME            # should print the SDK path (Mac/Linux)
adb --version                 # prints adb version if PATH is correct
sdkmanager --list | head -20  # list SDK packages (needs cmdline-tools in PATH)
emulator -list-avds           # list virtual devices you created
emulator -avd Pixel_6_API_35  # boot a device by name (replace with your AVD name)
adb devices                   # confirm emulator appears as "device"
```

## 💻 Code Example — Advanced

```bash
# Advanced: install everything from CLI + common fixes
# 1) Accept licenses (fixes "License for package ... not accepted")
yes | sdkmanager --licenses                                   # accept all licenses

# 2) Install packages without the GUI (adjust versions to your template)
sdkmanager "platform-tools" "platforms;android-35" "build-tools;35.0.0" "emulator"  # core tools
sdkmanager "system-images;android-35;google_apis;arm64-v8a"   # Apple Silicon image (use x86_64 on Intel)

# 3) Create an emulator from terminal
avdmanager create avd -n Pixel_35 -k "system-images;android-35;google_apis;arm64-v8a" -d pixel_6  # make AVD

# 4) Fix "SDK location not found" in a CLI project: create android/local.properties
echo "sdk.dir=$ANDROID_HOME" > android/local.properties          # tell Gradle the SDK path

# 5) Emulator cannot reach Metro? forward the port
adb reverse tcp:8081 tcp:8081                                    # device -> computer Metro

# 6) Clean a broken Gradle build
cd android && ./gradlew clean && cd ..                            # Windows: gradlew.bat clean
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| IDE | Android Studio | Xcode |
| Emulator name | AVD (Android Virtual Device) | iOS Simulator |
| Emulator architecture | Runs real Android image (x86/arm) | Runs on Mac (simulated iOS, not real iPhone hardware) |
| CLI tool | `adb`, `sdkmanager`, `avdmanager` | `xcrun simctl` |
| OS support | Win/Mac/Linux | Mac only |
| Dev menu shortcut | Ctrl+M (Win/Linux) / Cmd+M (Mac) | Cmd+D |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo: Android Studio is only needed for the emulator/SDK
npx expo start      # then press "a" -> Expo opens the emulator and installs Expo Go
npx expo run:android  # builds a dev build locally (needs full SDK + JDK 17)
```
CLI way:
```bash
# CLI: Android Studio setup is mandatory
npx react-native run-android   # builds with Gradle using your SDK
npx react-native doctor        # can suggest fixes for the Android environment
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Installing the wrong emulator image on Apple Silicon (x86).
✅ Correct: choose **arm64-v8a** images on M1/M2/M3 Macs; x86_64 on Intel/AMD.

❌ Mistake 2: Not enabling virtualization (Windows: HAXM/Hyper-V/WHPX; BIOS VT-x).
✅ Correct: enable virtualization in BIOS and Windows features; the emulator is very slow or fails otherwise.

❌ Mistake 3: Opening the whole project root in Android Studio for a CLI/Expo app.
✅ Correct: open only the `android/` folder (after prebuild) if you need Android Studio.

❌ Mistake 4: Skipping license acceptance.
✅ Correct: run `sdkmanager --licenses`.

---

## 🧠 Tricky Interview Question
**Q:** "The emulator shows a red screen: 'Unable to load script. Make sure Metro is running', but Metro is running on your Mac. Why?"

Answer: The emulator cannot reach `localhost:8081` of your computer by itself. Run `adb reverse tcp:8081 tcp:8081` (or use `10.0.2.2:8081`, the emulator's alias for the host). Also check that a firewall is not blocking port 8081.

---

## ⚫ Interview Questions + Answers
Q1: What is adb?
A1: Android Debug Bridge, a command line tool to talk to devices/emulators (install apps, logs, port forward).

Q2: Do I need to write code in Android Studio?
A2: No. VS Code is used for JS. Android Studio is for SDK, emulator and native debugging.

Q3: What is `10.0.2.2`?
A3: In the Android emulator it points to the host computer's localhost.

Q4: Where do you set the SDK path for Gradle?
A4: `ANDROID_HOME` env variable or `android/local.properties` (`sdk.dir=...`).

Q5: How do you view native Android logs?
A5: `adb logcat` or Logcat window in Android Studio.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local emulator testing and native Android debugging
- Building release builds locally

❌ Avoid when:
- Only learning with Expo Go on a real phone
- Weak laptop (<8 GB RAM): use a physical device or EAS Build

---

## 📊 Visual Diagram
```
 Android Studio
    ├── SDK Manager ──► Platforms + Build-Tools + Platform-Tools(adb)
    ├── Device Manager ──► AVD (emulator)
    └── Logcat / Profiler

 Metro (:8081) ◄── adb reverse ──► Emulator/Device ──► your app
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SDK | Android software dev kit | Android बनाने के tools |
| AVD | Virtual Android device | नकली Android फ़ोन |
| Gradle | Android build system | Android build tool |
| Logcat | Android log viewer | Android logs देखने की जगह |
| System image | OS image for an emulator | Emulator का OS |
| Platform-tools | adb and friends | adb वगैरह tools |

---

## ⚡ 3-Line Summary
English: Install Android Studio, add SDK platform, build-tools and platform-tools.
Create an AVD in Device Manager and set ANDROID_HOME.
Use adb reverse if the emulator cannot reach Metro.

Hindi: Android Studio install करें, SDK platform, build-tools और platform-tools जोड़ें।
Device Manager में AVD बनाएँ और ANDROID_HOME सेट करें।
Emulator Metro तक न पहुँचे तो adb reverse use करें।

---

## ➡️ Next Topic
**12. Xcode Setup (Mac only)** — the iOS equivalent: Xcode, simulators and CocoaPods.

---
