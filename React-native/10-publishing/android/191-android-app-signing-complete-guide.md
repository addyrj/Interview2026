# 191. Android App Signing — Complete Guide
# हिंदी में: Android App Signing — पूरी गाइड (Upload Key, Play App Signing)
# Platform: Android ✅ | iOS ❌ (iOS में certificates/provisioning अलग होते हैं)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Play Console और EAS के menu/नाम बदल सकते हैं — screens का वर्णन आम layout पर आधारित है (check current docs)। इस note में commands चलाए नहीं गए (not run) — सिर्फ docs के आधार पर।

---

## 🔵 Simple Definition (English)
**App signing** is attaching a digital signature (made with a private key) to your APK/AAB. Android refuses to install an update unless it carries the same signing identity as the installed app. With **Play App Signing**, Google keeps the real **app signing key**, and you sign uploads with a separate **upload key** — which can be reset if lost.

## 🔵 सरल परिभाषा (Hindi)
**App signing** यानी आपके APK/AAB पर private key से digital signature लगाना। Android तभी update install करता है जब signature वही हो जो installed app का है। **Play App Signing** में असली **app signing key** Google रखता है और आप एक अलग **upload key** से upload sign करते हैं — upload key खो जाए तो reset हो सकती है।

---

## 🔴 Problem it Solves
```
❌ कोई भी आपके app जैसा fake app बनाकर "update" भेज दे
❌ Keystore खो गया → पुराने app को update करना असंभव (पहले)
❌ Key leak → attacker आपके नाम से app जारी कर दे
Signing + Play App Signing:
  ✅ Authenticity (app आपका है)
  ✅ Update safety (सिर्फ same key वाला update)
  ✅ Upload key lost = support से reset (app signing key Google के पास सुरक्षित)
```

## 🔴 यह क्यों बना? (Hindi)
```
Android को पता होना चाहिए कि update असली developer का है।
Keystore खोने की समस्या से बचाने के लिए Google ने Play App Signing बनाया:
असली key Google के पास, आपके पास सिर्फ upload key।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Upload keystore बनाओ (keytool) — या EAS से auto-generate
Step 2 → Build config में keystore का path/password/alias दो
Step 3 → Release AAB build करो (Gradle bundleRelease / eas build)
Step 4 → AAB upload key से signed होता है
Step 5 → Play Console पर upload; पहली बार Play App Signing enroll (new apps में default)
Step 6 → Google AAB को अपनी app signing key से दोबारा sign करके users को APK भेजता है
Step 7 → Keystore/passwords का backup (password manager + encrypted storage)
Step 8 → Key खोई तो: Play Console → Setup → App signing → Request upload key reset
```

## 🟢 कैसे काम करता है? (Hindi)
```
आप AAB को upload key से sign करते हो।
Play Store उसे verify करके अपनी app signing key से re-sign करता है।
Users को Google की key से signed APK मिलता है।
Upload key खो जाए तो Google नई upload key register कर देता है।
```

---

## 🟡 Real World Example
**Swiggy/Zomato** जैसी कंपनियाँ release keystore/upload key सिर्फ CI के secret store (जैसे GitHub Secrets/Vault) में रखती हैं, डेवलपर के laptop पर नहीं — ताकि किसी कर्मचारी के जाने या laptop खोने पर key न खोए। Play App Signing के कारण अगर upload key compromise हो तो वे reset कर सकते हैं और app पर कोई असर नहीं पड़ता।

## 🟡 Real Example Hindi mein
बड़ी कंपनियाँ keystore CI secrets/vault में रखती हैं। Upload key leak हो जाए तो Play Console में reset माँगते हैं; app user के लिए चलता रहता है क्योंकि असली signing key Google के पास है।

---

## 💻 Code Example — Basic
```bash
# ---------- 1. Upload keystore बनाओ (JDK का keytool) ----------
# -genkeypair: नई key pair  -v: verbose  -storetype PKCS12: modern format
# -keyalg RSA -keysize 2048: algorithm  -validity 10000: ~27 साल (Play को 25+ साल चाहिए)
keytool -genkeypair -v -storetype PKCS12 \
  -keystore upload-keystore.jks \
  -alias upload \
  -keyalg RSA -keysize 2048 -validity 10000
# prompt: keystore password, key password, नाम/organization details — सब सुरक्षित लिखो

# ---------- 2. Fingerprint देखो (Console/Firebase में SHA जोड़ने के लिए) ----------
keytool -list -v -keystore upload-keystore.jks -alias upload
# Output में SHA1 और SHA256 मिलेंगे

# ---------- 3. Keystore को repo में commit मत करो ----------
echo "*.jks" >> .gitignore                      # keystore ignore
echo "*.keystore" >> .gitignore
```

## 💻 Code Example — Advanced
```groovy
// ---------- Bare RN / prebuild: android/app/build.gradle ----------
// Passwords को gradle.properties (~/.gradle/gradle.properties — repo के बाहर) में रखो:
//   MYAPP_UPLOAD_STORE_FILE=/secure/path/upload-keystore.jks
//   MYAPP_UPLOAD_KEY_ALIAS=upload
//   MYAPP_UPLOAD_STORE_PASSWORD=*****
//   MYAPP_UPLOAD_KEY_PASSWORD=*****

android {
    signingConfigs {
        release {                                           // release signing config
            if (project.hasProperty('MYAPP_UPLOAD_STORE_FILE')) { // properties मिलें तभी
                storeFile file(MYAPP_UPLOAD_STORE_FILE)     // keystore path
                storePassword MYAPP_UPLOAD_STORE_PASSWORD   // store password
                keyAlias MYAPP_UPLOAD_KEY_ALIAS             // alias
                keyPassword MYAPP_UPLOAD_KEY_PASSWORD       // key password
            }
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release            // release build इसी से sign
            minifyEnabled true                              // R8 shrink (optional पर अच्छा)
        }
    }
}
// Build: cd android && ./gradlew bundleRelease
// Output: android/app/build/outputs/bundle/release/app-release.aab
// Verify (APK के लिए): apksigner verify --print-certs app-release.apk
```
```bash
# ---------- Expo / EAS: credentials manage ----------
eas credentials                    # interactive menu: Android → keystore देखो/upload/download
# EAS पहली build पर keystore अपने आप generate करके अपने server पर सुरक्षित रखता है
eas build --platform android --profile production    # signed AAB बनाता है
# Own keystore use करने के लिए: eas credentials → Android → production →
#   "Keystore: Manage everything needed to build your project" → upload existing
# credentials.json (local) approach: eas.json में "credentialsSource": "local" (docs देखो)
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Identity | Keystore (upload key + Play App Signing key) | Distribution Certificate + Provisioning Profile |
| Who holds key | आप (upload) + Google (app signing) | Apple Developer account में certs (expire होते हैं) |
| Expiry | Key लंबी चलती (25+ साल) | Certificate 1 साल, renew ज़रूरी |
| Lost key | Upload key reset संभव | Certificate revoke/नया बनाओ |
| Tool | keytool, Gradle, EAS | Xcode, EAS, Apple Developer portal |
| Cost | Play account एक बार ~$25 | Apple Developer $99/year |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# EAS सब संभालता है
eas build --platform android --profile production
# पहली बार: "Generate a new Android Keystore?" → Yes
# Keystore EAS server पर; backup के लिए: eas credentials → download keystore
```
CLI way:
```bash
# खुद keystore (ऊपर keytool), build.gradle signingConfigs
cd android && ./gradlew bundleRelease
# CI: keystore को base64 में GitHub Secret, build time पर decode
echo "$KEYSTORE_B64" | base64 -d > upload-keystore.jks
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Debug keystore से release upload (Play reject)
✅ Correct: अलग release/upload keystore

❌ Mistake 2: Keystore repo में commit
✅ Correct: `.gitignore`, secrets manager

❌ Mistake 3: Password लिखा नहीं / backup नहीं
✅ Correct: Password manager + encrypted backup की 2 copies

❌ Mistake 4: Play App Signing opt-in नहीं किया (पुराने app)
✅ Correct: Enroll करो; नए apps में AAB के लिए ज़रूरी है

❌ Mistake 5: Firebase/Google Sign-In में सिर्फ upload key का SHA डाला
✅ Correct: Play Console → App signing page से **App signing key certificate** का SHA-1/256 भी Firebase में जोड़ो (Play से install वाले users के लिए)

---

## 🧠 Tricky Interview Question
आपने app Play App Signing के साथ publish किया। आज आपकी upload keystore खो गई। क्या app update कर पाएंगे?

Answer: हाँ। App signing key Google के पास है, upload key सिर्फ पहचान के लिए है। Play Console → Test and release → Setup → App signing → "Request upload key reset" से नई upload key का certificate (.pem) देकर request करते हैं; Google approve करता है (कुछ दिन लग सकते हैं), फिर नई keystore से upload कर सकते हैं। अगर Play App Signing नहीं था (पुराना self-signed app), तो key खोने पर update असंभव था।

---

## ⚫ Interview Questions + Answers
Q1: Upload key और App signing key में फर्क?
A1: Upload key = आप AAB sign करके Google को देते हो (पहचान)। App signing key = Google users के लिए APK sign करता है; app की असली identity।

Q2: APK और AAB का signing अलग है?
A2: AAB upload key से sign होता है; Google APKs generate करके app signing key से sign करता है। सीधा APK sideload करने पर आपकी साइन की हुई key ही identity होती है।

Q3: v1/v2/v3 signature schemes?
A3: v1 JAR signing, v2 पूरी APK पर (तेज़), v3 key rotation support, v4 incremental install। Modern AGP स्वतः लगाता है।

Q4: Debug keystore क्या है?
A4: `~/.android/debug.keystore` — Android SDK अपने आप बनाता है; सिर्फ development के लिए, publish के लिए नहीं।

Q5: Keystore का SHA-1 कहाँ ज़रूरी?
A5: Firebase (Google Sign-In, Phone Auth), Google Maps API key restriction, App Links (assetlinks.json में SHA-256)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Play Store पर publish/update करना हो
- CI/CD में automated release

❌ Avoid when:
- सिर्फ local testing (debug key काफी)
- Key को email/Slack पर भेजना (कभी नहीं)

---

## 📊 Visual Diagram
```
 You ── AAB signed with UPLOAD KEY ──► Play Console
                                          │ verify
                                          ▼
                           Google re-signs with APP SIGNING KEY (Google vault)
                                          │
                                          ▼
                              Users को signed APK (device-specific)

 Upload key खोई? → Play Console → Request upload key reset ✔
```

---

## 🖥️ Console Screens (वर्णन)
```
Play Console → आपका app → left menu "Test and release" → "Setup" → "App signing":
  - ऊपर "App signing key certificate" कार्ड: SHA-1, SHA-256, MD5 fingerprints के साथ
    "Download certificate" बटन।
  - नीचे "Upload key certificate" कार्ड: वही fingerprints + "Request upload key reset" लिंक।
  - ऊपर status बैनर: "Play App Signing is on" (हरे टिक के साथ)।
EAS: terminal में `eas credentials` → arrow-key menu: Android → production → keystore options।
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Keystore | File holding private keys | Key की file |
| Upload key | Key to sign uploads | Upload sign करने की key |
| App signing key | Key Google uses for users | असली signing key |
| Alias | Key's name in keystore | Key का नाम |
| SHA-1/SHA-256 | Certificate fingerprint | Certificate की पहचान |
| AAB | Android App Bundle | Android bundle format |

---

## ⚡ 3-Line Summary
English: Signing proves an app update comes from you; Play App Signing keeps the real key at Google.
You sign uploads with an upload key that can be reset if lost.
Never commit keystores; back up passwords and add SHA fingerprints to Firebase.

Hindi: Signing साबित करता है कि update आपका है; असली key Play App Signing में Google के पास रहती है।
आप upload key से sign करते हैं, जो खो जाए तो reset हो सकती है।
Keystore commit मत करो; passwords backup और SHA Firebase में जोड़ो।

---

## ➡️ Next Topic
**192. Android Keystore & App Signing** (पहले से लिखा है) — keystore बनाने की गहराई; फिर **194. Build Types (debug vs release)**।

---
