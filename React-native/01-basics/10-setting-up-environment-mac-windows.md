# 10. Setting Up Environment (Mac/Windows)
# हिंदी में: Development Environment Setup (Mac / Windows)
# Platform: Android ✅ | iOS ✅ (iOS = Mac only) | Both ✅

> Target: Expo SDK 52 / React Native 0.76 (Node 18+, JDK 17). Expo SDK NN (check current docs — required Node/JDK versions change between SDKs).

---

## 🔵 Simple Definition (English)
Environment setup means installing the tools a React Native app needs: **Node.js, a package manager, a JDK, Android Studio (Android SDK), Xcode (Mac only), Watchman and CocoaPods**, plus setting environment variables like `ANDROID_HOME`.

## 🔵 सरल परिभाषा (Hindi)
Environment setup का मतलब है React Native app के लिए ज़रूरी tools install करना: **Node.js, package manager, JDK, Android Studio (Android SDK), Xcode (सिर्फ Mac), Watchman और CocoaPods**, और `ANDROID_HOME` जैसे environment variables सेट करना।

---

## 🔴 Problem it Solves
```
❌ "command not found: adb"
❌ "SDK location not found"
❌ "Unsupported class file major version" (wrong JDK)
❌ Different team members on different Node versions = random bugs
A correct, repeatable setup removes 80% of "works on my machine" errors.
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ "command not found: adb"
❌ "SDK location not found"
❌ "Unsupported class file major version" (गलत JDK)
❌ अलग-अलग Node versions = अजीब bugs
सही और दोहराने लायक setup से "मेरे laptop पर चल रहा है" वाली समस्या कम होती है।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install Node.js LTS (use nvm / fnm to switch versions)

Step 2 → Install Git + VS Code

Step 3 → Mac: install Homebrew, then Watchman
         Windows: install Chocolatey (optional), Git for Windows

Step 4 → Install JDK 17 (e.g. Zulu / Temurin)

Step 5 → Install Android Studio -> SDK Platform + Platform-Tools
         (detailed in topic 11)

Step 6 → Mac only: Xcode + Command Line Tools + CocoaPods
         (detailed in topic 12)

Step 7 → Set ANDROID_HOME and PATH, then verify with
         node -v, java -version, adb --version, npx expo-doctor
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Node.js LTS install करें (nvm / fnm से version बदलें)
Step 2 → Git + VS Code install करें
Step 3 → Mac: Homebrew फिर Watchman
         Windows: Git for Windows (Chocolatey optional)
Step 4 → JDK 17 install करें (Zulu / Temurin)
Step 5 → Android Studio -> SDK Platform + Platform-Tools (topic 11)
Step 6 → सिर्फ Mac: Xcode + Command Line Tools + CocoaPods (topic 12)
Step 7 → ANDROID_HOME और PATH सेट करें, फिर verify करें:
         node -v, java -version, adb --version, npx expo-doctor
```

---

## 🟡 Real World Example
An intern joining a **Swiggy-like** team gets a laptop. The onboarding doc says: install `nvm`, `nvm install 20`, JDK 17, Android Studio, and run `npx expo-doctor`. With a pinned Node version (`.nvmrc`) the intern builds the app on day one instead of fighting version errors.

## 🟡 Real Example Hindi mein
**Swiggy जैसी** team में नया intern laptop पाता है। Onboarding doc कहता है: `nvm` install करो, `nvm install 20`, JDK 17, Android Studio, और `npx expo-doctor` चलाओ। `.nvmrc` में Node version fixed होने से intern पहले ही दिन app build कर लेता है।

---

## 💻 Code Example — Basic

```bash
# Basic: macOS setup (Terminal) - every line commented
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"  # install Homebrew
brew install node        # install Node.js (or use nvm for multiple versions)
brew install watchman    # file watcher used by Metro
brew install --cask zulu@17   # install JDK 17 (Android builds)
node -v                  # verify Node version
java -version            # verify JDK version
```

## 💻 Code Example — Advanced

```bash
# Advanced: shell profile variables + verification (macOS: ~/.zshrc)
# Windows: set the same variables in System Properties -> Environment Variables

# ---- macOS ~/.zshrc ----
export ANDROID_HOME=$HOME/Library/Android/sdk          # Android SDK location (Mac default)
export PATH=$PATH:$ANDROID_HOME/emulator               # emulator command
export PATH=$PATH:$ANDROID_HOME/platform-tools         # adb command
export JAVA_HOME=$(/usr/libexec/java_home -v 17)       # point to JDK 17

# ---- Windows (PowerShell, one time) ----
# setx ANDROID_HOME "$env:LOCALAPPDATA\Android\Sdk"    # Android SDK location (Windows default)
# Add to Path: %ANDROID_HOME%\platform-tools and %ANDROID_HOME%\emulator

# ---- Pin Node for the team ----
echo "20" > .nvmrc          # tell everyone to use Node 20
nvm use                     # switch to the pinned version

# ---- Verify ----
source ~/.zshrc             # reload profile (Mac)
adb --version               # Android tools reachable?
npx expo-doctor             # checks the Expo project health
npx react-native doctor     # CLI projects: diagnose missing pieces
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| OS needed | Windows / Mac / Linux | **macOS only** |
| Main tool | Android Studio + SDK | Xcode |
| Language runtime | JDK 17 | Ruby/CocoaPods (iOS native deps) |
| Env variable | `ANDROID_HOME` | None (Xcode path via `xcode-select`) |
| Device bridge | `adb` | `xcrun simctl` / Xcode |
| Disk space | ~15-20 GB | ~40+ GB (Xcode + simulators) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Minimum for Expo Go: Node + phone with Expo Go app. No Android Studio/Xcode needed
npx create-expo-app@latest MyApp   # create project
cd MyApp && npx expo start         # scan QR in Expo Go
```
CLI way:
```bash
# CLI needs everything: JDK, Android Studio (+ Xcode on Mac), Watchman, CocoaPods
npx @react-native-community/cli@latest init MyApp  # create project
cd MyApp && npx react-native run-android           # needs emulator/device + SDK
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Installing the newest JDK (21/22) for Android.
✅ Correct: Use **JDK 17** for current RN/Expo Gradle builds.

❌ Mistake 2: Forgetting `ANDROID_HOME` / `platform-tools` in PATH.
✅ Correct: Set variables, restart terminal, test `adb --version`.

❌ Mistake 3: Using Node installed with sudo and permission errors.
✅ Correct: Use `nvm`/`fnm`, never `sudo npm install -g`.

❌ Mistake 4: Trying to build iOS on Windows.
✅ Correct: Use a Mac or EAS Build (cloud).

---

## 🧠 Tricky Interview Question
**Q:** "A developer on Windows says: 'I installed Expo and Xcode via WSL, why does iOS Simulator not open?'"

Answer: Xcode and the iOS Simulator run **only on macOS**. WSL cannot run them. Options: use a Mac, a cloud Mac, or **EAS Build** for builds and a real iPhone with Expo Go/dev build for testing.

---

## ⚫ Interview Questions + Answers
Q1: Which tools are mandatory for Expo Go development?
A1: Node.js and a phone with the Expo Go app (or an emulator). No Android Studio needed.

Q2: Why is Watchman used?
A2: It watches files efficiently so Metro reloads quickly (recommended on macOS).

Q3: What does ANDROID_HOME do?
A3: Tells Gradle/CLI where the Android SDK lives.

Q4: What does `npx expo-doctor` do?
A4: Checks the project for dependency/config mismatches with the current SDK.

Q5: Why nvm?
A5: To switch Node versions per project without conflicts.

---

## 🔷 When to Use + When Not to Use
✅ Use full local setup when:
- You need Android emulator/iOS simulator
- You build native code locally

❌ Avoid heavy setup when:
- Just learning: Expo Go on a phone is enough
- Low disk space: use EAS Build in cloud

---

## 📊 Visual Diagram
```
 Node (nvm) ──► npm/yarn ──► Metro (+Watchman)
      │
      ├── JDK 17 ──► Android Studio ──► Android SDK ──► adb / emulator
      │
      └── (Mac) Xcode ──► CLT ──► CocoaPods ──► iOS Simulator
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| nvm | Node version manager | Node version बदलने का tool |
| JDK | Java Development Kit | Java बनाने के tools |
| ANDROID_HOME | Path of Android SDK | Android SDK का रास्ता |
| adb | Android Debug Bridge | Android से बात करने का tool |
| Watchman | File watcher by Meta | file बदलाव देखने वाला tool |
| CocoaPods | iOS dependency manager | iOS libraries का manager |

---

## ⚡ 3-Line Summary
English: Install Node (nvm), JDK 17, Android Studio and, on Mac, Xcode with CocoaPods.
Set ANDROID_HOME and PATH, then verify with doctor commands.
For quick learning, Expo Go needs only Node and a phone.

Hindi: Node (nvm), JDK 17, Android Studio और Mac पर Xcode + CocoaPods install करें।
ANDROID_HOME और PATH सेट करें, फिर doctor commands से जाँचें।
जल्दी सीखने के लिए Expo Go को सिर्फ Node और फ़ोन चाहिए।

---

## ➡️ Next Topic
**11. Android Studio Setup** — install the SDK, create an emulator and fix common Android errors.

---
