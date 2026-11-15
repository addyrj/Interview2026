# 154. Certificate Pinning
# हिंदी में: Certificate Pinning (सर्वर का भरोसेमंद certificate fix करना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, React Native 0.76. Pinning के लिए native code चाहिए, इसलिए **Expo Go में काम नहीं करता** — development build / prebuild चाहिए।

---

## 🔵 Simple Definition (English)
**Certificate pinning** means your app trusts only one specific server certificate (or its public key) instead of trusting every certificate that the phone's OS trusts. If someone intercepts the traffic with a fake certificate, the connection is rejected.

## 🔵 सरल परिभाषा (Hindi)
**Certificate pinning** का मतलब है कि आपका app सिर्फ एक specific server certificate (या उसकी public key) पर भरोसा करता है, फ़ोन का OS जिन सब certificates पर भरोसा करता है उन पर नहीं। अगर कोई fake certificate लगाकर traffic बीच में पकड़े (MITM), तो connection reject हो जाता है।

---

## 🔴 Problem it Solves
```
NORMAL HTTPS:
  Phone trusts ~150 Certificate Authorities (CAs)
  Attacker installs his own CA on phone (or hacks one CA)
  → Attacker's fake cert for api.paytm.com looks VALID
  → He reads/modifies your payment API traffic (MITM)

WITH PINNING:
  App says: "I only accept the cert with THIS public-key hash"
  → Fake cert hash doesn't match → connection FAILS
```

## 🔴 यह क्यों बना? (Hindi)
```
सामान्य HTTPS में फ़ोन ~150 CAs पर भरोसा करता है।
Attacker अपना CA फ़ोन में install करवा ले (Burp/Charles, public WiFi)
→ fake certificate भी "valid" दिखता है → उसे आपका data दिखता है।

Pinning से: app सिर्फ अपने server का हैश जानता है
→ हैश match नहीं → connection तुरंत fail → data सुरक्षित।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Get your server's public key hash (SPKI SHA-256)
Step 2 → Embed the hash(es) in the app (config / native code)
Step 3 → App opens TLS connection to api.example.com
Step 4 → Server sends its certificate chain
Step 5 → Native TLS layer hashes the public key
Step 6 → Hash in pinned list?  YES → request continues
                               NO  → connection aborted (error)
Step 7 → Always ship a BACKUP pin (next key) to survive rotation
```

Hash निकालने का command:
```bash
# Server की public key का SHA-256 (base64) निकालो
openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null 2>/dev/null \
  | openssl x509 -pubkey -noout \
  | openssl pkey -pubin -outform der \
  | openssl dgst -sha256 -binary | openssl enc -base64
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Server की public key का SHA-256 hash निकालो
Step 2 → वह hash app में रखो (config में)
Step 3 → App server से TLS connection खोलता है
Step 4 → Server अपना certificate chain भेजता है
Step 5 → Native TLS layer public key का hash बनाती है
Step 6 → Hash list में है → request चलती है; नहीं है → connection बंद
Step 7 → हमेशा BACKUP pin रखो, वरना certificate बदलते ही app बंद!
```

---

## 🟡 Real World Example
Banking and UPI apps (**Paytm, PhonePe, HDFC PayZapp**) pin their API certificates. If a user is on a cafe WiFi where someone runs a proxy with a fake certificate, the app shows "Network error" instead of leaking the OTP or payment request. RBI security guidelines for mobile banking recommend this kind of protection. **Swiggy/Zomato** usually pin only for payment/login endpoints, not for the image CDN.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe** जैसे UPI apps अपने API certificates pin करते हैं। अगर आप cafe के WiFi पर हैं और कोई fake certificate वाला proxy चला रहा है, तो app OTP या payment request leak करने की जगह "Network error" दिखा देता है। **Zomato/Swiggy** अक्सर सिर्फ login और payment endpoints pin करते हैं, image CDN नहीं।

---

## 💻 Code Example — Basic
Library: `react-native-ssl-public-key-pinning` (native module, कोई Expo Go support नहीं)।

```bash
# Library install करो
npm install react-native-ssl-public-key-pinning
# Expo में dev build बनाओ (Expo Go नहीं चलेगा)
npx expo prebuild
```

```jsx
// Basic: एक domain के लिए pinning चालू करना
import { useEffect, useState } from 'react';                       // React hooks import
import { View, Text } from 'react-native';                         // UI components
import { initializeSslPinning } from 'react-native-ssl-public-key-pinning'; // pinning init function

export default function App() {
  const [msg, setMsg] = useState('Loading...');                    // screen पर दिखने वाला message

  useEffect(() => {                                                // app start पर एक बार चलेगा
    (async () => {                                                 // async IIFE क्योंकि await चाहिए
      try {
        await initializeSslPinning({                               // pinning rules register करो
          'api.example.com': {                                     // इस domain पर rules लागू होंगे
            includeSubdomains: true,                               // subdomains भी pinned
            publicKeyHashes: [                                     // allowed SPKI SHA-256 (base64) hashes
              'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',      // primary pin (placeholder — अपना डालो)
              'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=',      // BACKUP pin (अगली key)
            ],
          },
        });
        const res = await fetch('https://api.example.com/ping');   // अब fetch pinned चलेगा
        setMsg(`Status: ${res.status}`);                           // success पर status दिखाओ
      } catch (e) {
        setMsg('Blocked: pin mismatch or network error');          // pin fail पर यहाँ आएगा
      }
    })();
  }, []);                                                          // empty deps = सिर्फ एक बार

  return (
    <View style={{ flex: 1, justifyContent: 'center' }}>
      <Text>{msg}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: env के हिसाब से pins, error handling, और pin-fail पर graceful UX
import { Platform, Alert } from 'react-native';                    // platform check + alert
import {
  initializeSslPinning,                                            // rules set करो
  disableSslPinning,                                               // dev में बंद करने के लिए
  isSslPinningAvailable,                                           // native support check
} from 'react-native-ssl-public-key-pinning';

// Pins को remote config से भी लाया जा सकता है, पर bundle में fallback रखो
const PINS = {
  'api.myshop.in': {
    includeSubdomains: false,                                      // सिर्फ यही host
    publicKeyHashes: [
      process.env.EXPO_PUBLIC_PIN_PRIMARY,                         // EXPO_PUBLIC_ env, build time पर inline होता है
      process.env.EXPO_PUBLIC_PIN_BACKUP,                          // backup pin अनिवार्य
    ].filter(Boolean),                                             // undefined हटाओ
  },
};

export async function setupPinning() {
  if (__DEV__) {                                                   // dev में Charles/Proxyman चलाने देने के लिए
    await disableSslPinning();                                     // pinning बंद (सिर्फ dev!)
    return;
  }
  if (!isSslPinningAvailable()) {                                  // Expo Go आदि में native module नहीं
    console.warn('SSL pinning native module missing');             // log करो
    return;                                                        // crash मत करो
  }
  try {
    await initializeSslPinning(PINS);                              // production में rules लगाओ
  } catch (e) {
    console.error('Pinning init failed', e);                       // init fail log
    Alert.alert('Security error', 'Please update the app.');       // user को बताओ
  }
}

// Generic API wrapper: pin failure को अलग पहचानो
export async function api(path, opts) {
  try {
    const res = await fetch(`https://api.myshop.in${path}`, opts); // pinned fetch
    return await res.json();                                       // JSON return
  } catch (e) {
    // Android में message "Certificate pinning failure" होता है,
    // iOS में NSURLErrorDomain -999/-1202 जैसा error आता है
    const pinFail = /pin|certificate|-1202|-999/i.test(String(e)); // rough detection
    if (pinFail) Alert.alert('Unsafe network', 'Switch network and retry.');
    throw e;                                                       // ऊपर भी propagate
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native mechanism | OkHttp `CertificatePinner` / Network Security Config | `URLSession` delegate / ATS `NSPinnedDomains` (iOS 14+) |
| Config without library | `res/xml/network_security_config.xml` `<pin-set>` | Info.plist `NSAppTransportSecurity > NSPinnedDomains` |
| Pin type | SPKI SHA-256 | SPKI SHA-256 |
| Expiry of pin-set | `expiration` attribute supported | No built-in expiry |
| Error text | "Certificate pinning failure!" | `NSURLErrorCancelled (-999)` |
| User-installed CAs | Android 7+ ignores them by default for apps | Trusted if user installs profile |

---

## 🟠 Expo vs CLI Difference
Expo way (config plugin + dev build; Expo Go में नहीं चलेगा):
```jsx
// app.json में plugin जोड़ने की ज़रूरत library docs के अनुसार हो सकती है; फिर:
// npx expo prebuild && npx expo run:android
import { initializeSslPinning } from 'react-native-ssl-public-key-pinning'; // JS API वही रहती है
await initializeSslPinning({ 'api.example.com': { publicKeyHashes: ['<primary>', '<backup>'] } });
```
CLI way (bare RN):
```jsx
// npm i library && cd ios && pod install; Android autolink होता है
// कोड वही; चाहें तो Android में network_security_config.xml भी manually लिख सकते हैं
import { initializeSslPinning } from 'react-native-ssl-public-key-pinning';
await initializeSslPinning({ 'api.example.com': { publicKeyHashes: ['<primary>', '<backup>'] } });
```
Plugin की exact config key library के version के docs में देखो (मैं यहाँ कोई key नहीं बना रहा)।

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: सिर्फ एक pin रखना, backup नहीं।
✅ Correct: कम से कम 2 pins (current + backup key)। Certificate rotate होते ही बिना backup सारे users का app बंद हो जाएगा।

❌ Mistake 2: Leaf certificate pin करना जो हर 90 दिन में बदलता है (Let's Encrypt)।
✅ Correct: **Public key (SPKI)** pin करो और key rotate न करो, या intermediate CA pin करो।

❌ Mistake 3: Expo Go में test करके "काम कर गया" मान लेना।
✅ Correct: Dev build पर test करो; Expo Go में native module नहीं है।

❌ Mistake 4: Pinning को अकेली security मान लेना।
✅ Correct: Rooted phones पर Frida/objection से bypass हो सकता है — यह defense-in-depth है।

---

## 🧠 Tricky Interview Question
"आपने pinning लगाया, app Play Store पर गया। 3 महीने बाद server team ने certificate renew किया और app सबके phone पर 'Network error' देने लगा। क्यों, और fix क्या?"

Answer: Renew में key pair भी बदली, इसलिए नया SPKI hash pinned hash से match नहीं हुआ। Fix के लिए नया app release चाहिए, जो users के update करने तक काम नहीं करेगा — यही pinning का सबसे बड़ा risk है। Prevention: backup pin पहले से ship करो, key को renew पर वही रखो (same key CSR), या pins को signed remote config से भेजो और kill-switch रखो।

---

## ⚫ Interview Questions + Answers
Q1: Certificate pinning क्या है?
A1: App का सिर्फ अपने server के known certificate/public key पर भरोसा करना, ताकि MITM fake certificate reject हो।

Q2: Certificate pinning vs public key pinning?
A2: Certificate pin पूरा cert hash करता है (renew पर टूटता है); public key pin सिर्फ key hash करता है, इसलिए same key पर renew होने से बचता है।

Q3: Pinning कब fail हो सकती है production में?
A3: Cert/key rotation, corporate proxy, ग़लत hash, backup pin न होना।

Q4: क्या pinning bypass हो सकता है?
A4: हाँ, rooted/jailbroken device पर Frida, objection, या patched APK से। इसलिए root detection और server-side checks भी चाहिए।

Q5: Expo Go में pinning चलेगी?
A5: नहीं। Native module चाहिए, इसलिए dev build / EAS build ज़रूरी है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Banking, payments, health, login/OTP जैसे sensitive APIs
- Compliance (RBI, PCI) माँगती हो
- Public WiFi पर users का बड़ा हिस्सा हो

❌ Avoid when:
- Third-party APIs जिनका certificate आप control नहीं करते
- आपके पास rotation process / backup pin / kill switch नहीं
- Simple public content app (news, blog) जहाँ risk कम है

---

## 📊 Visual Diagram
```
 Without pinning                   With pinning
 ───────────────                   ────────────
 App ──► Attacker proxy ──► Server  App ──► Attacker proxy ✖
        (fake cert, OS trusts it)         fake key hash ≠ pinned hash
        data leaks                        connection aborted
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MITM | Attacker sits between app and server | बीच में बैठा हमलावर |
| SPKI | Subject Public Key Info of a cert | Certificate की public key जानकारी |
| Pin | Stored trusted hash | भरोसेमंद hash जो app में रखा है |
| Backup pin | Hash of next key for rotation | अगली key का hash |
| CA | Certificate Authority | Certificate जारी करने वाली संस्था |
| Network Security Config | Android XML for TLS rules | Android की TLS नीति file |

---

## ⚡ 3-Line Summary
English: Pinning makes the app trust only your server's key hash. It blocks MITM even with fake-but-OS-trusted certificates. Always ship a backup pin and test on a dev build, not Expo Go.
Hindi: Pinning से app सिर्फ आपके server की key hash पर भरोसा करता है। Fake पर OS-trusted certificate होने पर भी MITM रुक जाता है। हमेशा backup pin रखो और Expo Go नहीं, dev build पर test करो।

---

## ➡️ Next Topic
**155. React Native Performance Issues** — security के बाद app की speed: क्यों slow होता है और कैसे ढूँढें।
