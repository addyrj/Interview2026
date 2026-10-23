# M15. Mobile Security (Secure Storage, SSL Pinning, Root/Jailbreak)
# हिंदी में: Mobile Security — फ़ोन ऐप को हमलों से बचाना: tokens और डेटा सुरक्षित तिजोरी में रखना, नेटवर्क पर बीच में सुनने वाले (MITM) से बचने के लिए SSL pinning, rooted/jailbroken फ़ोन की पहचान, असली ऐप की पुष्टि (attestation), और app के अंदर कोई secret न रखना

---

## 🔵 Simple Definition (English)
Mobile security protects **users' data, credentials and money** when your app runs on devices **you don't control**. Attackers can decompile the app, run it on rooted or jailbroken phones, intercept traffic with a proxy, tamper with the binary, or install malware alongside it.
Key areas (aligned with **OWASP MASVS** and the **OWASP Mobile Top 10**):
- **Secure storage**: secrets only in **Keychain/Keystore**, encrypted local DBs, no PII in logs or backups (M05).
- **Secure communication**: HTTPS only (iOS ATS, Android Network Security Config, no cleartext), plus **certificate/public-key pinning** for high-risk apps.
- **Auth & session**: short-lived tokens, refresh rotation, biometrics, device binding (M16).
- **Platform integrity**: **root/jailbreak detection**, **app attestation** (Google **Play Integrity API**, Apple **App Attest/DeviceCheck**), anti-tampering and anti-debugging, obfuscation (R8/ProGuard).
- **No secrets in the app**: anything in the bundle (API keys, Hermes bytecode, assets) can be extracted, so keep secrets on the server.
- **Input & platform hardening**: validate deep links (M11), secure WebViews, protect sensitive screens (block screenshots, blur in the app switcher), clipboard hygiene, least-privilege permissions.

## 🔵 सरल परिभाषा (Hindi)
Mobile security = ऐसे फ़ोन पर चल रहे ऐप में यूज़र का डेटा, पहचान और पैसा बचाना जो आपके नियंत्रण में नहीं — हमलावर ऐप को खोलकर पढ़ सकता है, rooted फ़ोन पर चला सकता है, proxy से traffic सुन सकता है, ऐप बदल सकता है।
मुख्य बातें: secrets सिर्फ़ Keychain/Keystore में; सिर्फ़ HTTPS + ज़रूरत हो तो SSL pinning; छोटे tokens, biometric, device binding; root/jailbreak पहचान और Play Integrity/App Attest से असली ऐप की पुष्टि; ऐप में कोई secret नहीं (सब निकाला जा सकता है); deep links/WebView की जाँच, संवेदनशील screens पर screenshot रोकना।

---

## 🔴 Problem it Solves
Real mobile attack scenarios:
- **Hard-coded secrets**: security researchers (e.g., Symantec in 2022) found over a thousand apps with **hard-coded cloud (AWS) credentials** that exposed backend data. Anyone can unzip an APK/IPA.
- **Man-in-the-middle**: on public Wi-Fi or with a user-installed CA certificate, traffic can be intercepted and modified if the app trusts any CA or ignores TLS errors.
- **Rooted devices / malware**: overlay attacks, screen readers abused by banking trojans, keyloggers, extracting tokens from app storage.
- **Tampered/repackaged apps**: cracked versions that bypass payments or inject malware, then republished on third-party stores.
- **Insecure storage**: tokens in AsyncStorage/SharedPreferences readable on rooted devices or via backups.
- **Fraud and bots**: scripts calling your API pretending to be your app (fake sign-ups, coupon abuse, credential stuffing).
For fintech, UPI and banking apps in India, **RBI and NPCI guidelines** expect controls like device binding, root detection and secure storage.

## 🔴 यह क्यों बना? (Hindi)
असली हमले: ऐप में hard-coded secrets (2022 में Symantec जैसे शोधकर्ताओं को हज़ार से ज़्यादा ऐप में AWS credentials मिले — APK/IPA कोई भी खोल सकता है); public Wi-Fi पर MITM; rooted फ़ोन पर malware/banking trojans जो overlay या accessibility का ग़लत इस्तेमाल करते हैं; बदला हुआ (cracked) ऐप जो payment bypass करे; AsyncStorage में token; और bots जो आपका ऐप बनकर API चलाएँ (नक़ली signups, coupon का दुरुपयोग)।
भारत में fintech/UPI/बैंकिंग ऐप्स से RBI और NPCI device binding, root detection, secure storage जैसे नियंत्रण की उम्मीद करते हैं।

---

## 🟢 How it Works — Step by Step

### Threat model (who attacks what)

```
┌────────────────────────┬──────────────────────────────────┬────────────────────────────────────┐
│ Attacker               │ Capability                       │ Defence                            │
├────────────────────────┼──────────────────────────────────┼────────────────────────────────────┤
│ Network (public Wi-Fi, │ intercept/modify traffic         │ TLS everywhere, no cleartext, cert │
│ malicious hotspot)     │                                  │ validation, pinning (high risk)    │
│ Reverse engineer       │ decompile APK/IPA, read strings, │ no secrets in app, obfuscation,    │
│                        │ hook functions (Frida)           │ server-side checks, attestation    │
│ Device owner w/ root   │ read app storage, bypass checks, │ Keystore/Keychain (hardware),      │
│ (fraudster)            │ automate app                     │ root detection + risk scoring,     │
│                        │                                  │ Play Integrity / App Attest        │
│ Malware on device      │ overlays, accessibility abuse,   │ FLAG_SECURE, overlay detection,    │
│                        │ SMS/OTP stealing, screen capture │ device binding, txn confirmation   │
│ Bot/scripted client    │ call API directly at scale       │ attestation tokens, rate limits,   │
│                        │                                  │ device fingerprint, behaviour risk │
│ Thief with phone       │ open app, read data              │ app lock (biometric/PIN), short    │
│                        │                                  │ sessions, remote logout            │
└────────────────────────┴──────────────────────────────────┴────────────────────────────────────┘
```

### Secure communication & pinning

```
Baseline (every app):
- HTTPS only: iOS App Transport Security (default), Android Network Security Config cleartextTrafficPermitted=false
- Never disable certificate validation ("trust all" code from StackOverflow ❌)
- Android 7+: user-installed CAs not trusted by default for apps (good) — don't override for release

Certificate / public-key pinning (banking, payments, high-value):
- App embeds hashes of your server's PUBLIC KEY (SPKI), not the whole cert → survives cert renewal if key reused
- Pin intermediate or leaf key + at least one BACKUP pin (next key) → avoid bricking the app on rotation
- Failure → refuse connection, report to backend
- Risks: misconfigured rotation = app can't connect for ALL users until update (with no OTA fix for
  native config!) → have expiry dates, backup pins, remote kill-switch strategy, monitoring
- Pinning raises the bar vs MITM on compromised CAs/corporate proxies; rooted devices with Frida can
  still bypass → combine with attestation & server-side risk checks
```

### Root/jailbreak detection & app attestation

```
Root/jailbreak signals: su binaries, Magisk, Cydia/Sileo, writable system paths, hooking frameworks
(Frida, Xposed), debuggers, emulators
→ Client-side checks are bypassable → use as RISK SIGNALS, not the only gate
App attestation (stronger, server-verified):
  Android Play Integrity API: app requests integrity token → backend verifies with Google →
     verdicts: app recognized (genuine binary from Play), device integrity (basic/device/strong),
     account licensing
  iOS App Attest (DeviceCheck): Secure Enclave key attests the app is genuine & unmodified;
     assertions sign requests
Use for: login, high-value transactions, sign-up/coupon abuse prevention, API access by genuine apps only
Policy examples: block payments on rooted devices (bank), allow browsing but require OTP+limits (fintech),
                 only log risk (e-commerce)
```

### Binary hardening

```
Android: R8/ProGuard minify + obfuscate, remove debug logs, android:debuggable=false, android:allowBackup=false
         (or backup rules excluding sensitive files), exported=false for internal components
iOS: strip symbols, no debug entitlements, protect against dylib injection (best effort)
RN: Hermes bytecode is NOT encryption — it can be decompiled → never ship secrets in JS
Tamper detection: verify signing certificate at runtime + server-side via attestation
RASP (runtime app self-protection) SDKs (e.g., freeRASP, commercial) for banking-grade apps
```

### Data protection on device

```
- Tokens & keys → Keychain (kSecAttrAccessibleWhenUnlockedThisDeviceOnly) / Android Keystore (hardware-backed, StrongBox)
- Encrypted DB for sensitive data (SQLCipher), key in Keystore
- Don't log tokens/PII (Sentry beforeSend scrubbing), don't put PII in analytics events
- Sensitive screens: Android FLAG_SECURE (no screenshots/screen recording, hidden in recents);
  iOS: blur/cover view when app goes to background (app switcher snapshot)
- Clipboard: don't auto-copy OTP/card data; clear sensitive copies
- Keyboard: secureTextEntry for passwords/PIN; disable autocorrect/suggestions on sensitive fields
- Wipe on logout; remote session revocation
```

### Secrets: where should API keys live?

```
❌ In app (.env baked into bundle, strings.xml, Info.plist) → extractable
✅ On your backend: app calls YOUR API with user auth → backend calls third-party (maps, SMS, LLM, payment)
   with secret keys
⚠️ Some keys are meant to be public (Maps SDK keys, Firebase config, Razorpay key_id, Sentry DSN)
   → restrict them (bundle id / package + SHA-1 restrictions, domain restrictions, quotas)
```

## 🟢 कैसे काम करता है? (Hindi)
1. खतरे पहचानो: नेटवर्क पर सुनने वाला, ऐप खोलकर पढ़ने वाला (Frida से hook), root वाला धोखेबाज़, फ़ोन पर malware, bots, फ़ोन चोर — और हर एक का बचाव।
2. हमेशा HTTPS (ATS, cleartext बंद), "सब certificate मान लो" वाला code कभी नहीं; बैंक/payment ऐप में public-key pinning + backup pin (rotation में ग़लती = सबके लिए ऐप बंद, इसलिए सावधानी)।
3. Root/jailbreak की जाँच bypass हो सकती है — इसे जोखिम संकेत मानो; पक्का भरोसा सर्वर पर verify होने वाले Play Integrity (Android) और App Attest (iOS) से — login, बड़े लेन-देन, coupon दुरुपयोग पर।
4. Binary: R8/ProGuard, debuggable false, backup में संवेदनशील files नहीं; Hermes bytecode encryption नहीं है — JS में कोई secret नहीं; secret keys सिर्फ़ backend पर, public keys (Maps, Razorpay key_id) को package/SHA से सीमित करो।
5. Device पर: tokens Keychain/Keystore में, संवेदनशील DB SQLCipher से, logs/analytics में PII नहीं, payment/OTP screens पर FLAG_SECURE और app switcher में blur, clipboard साफ़, logout पर सब मिटाओ।

---

## 🟡 Real World Example

**Indian banking & UPI apps (SBI YONO, HDFC, PhonePe, Google Pay, BHIM)** — device binding (SMS sent from the registered SIM to verify the device), root/jailbreak detection (many banking apps refuse to run on rooted phones), Keystore-protected keys, app-lock PIN or biometrics, FLAG_SECURE on sensitive screens, and short sessions, in line with RBI and NPCI security expectations.

**Hard-coded cloud credentials research (2022)** — Symantec reported finding over 1,800 iOS and Android apps with hard-coded AWS credentials, some exposing millions of records. It's the classic proof that client-side secrets aren't secret.

**Play Integrity / SafetyNet** — Google replaced SafetyNet Attestation with Play Integrity. Games, fintech and streaming apps use it to block modded clients, emulator farms and cheaters at the API level.

**Banking trojans (e.g., Anatsa, SharkBot)** — Android malware abusing accessibility services and overlays to steal banking credentials, which is why banks add overlay and accessibility-abuse detection, transaction confirmation and anomaly detection.

## 🟡 Real Example Hindi में
SBI YONO, HDFC, PhonePe, Google Pay, BHIM जैसे ऐप device binding (registered SIM से SMS भेजकर फ़ोन की पुष्टि), root detection (कई बैंक ऐप rooted फ़ोन पर चलते ही नहीं), Keystore keys, PIN/biometric app lock, संवेदनशील screens पर FLAG_SECURE और छोटे sessions रखते हैं — RBI/NPCI की अपेक्षाओं के अनुसार।
2022 में Symantec को 1,800+ ऐप में hard-coded AWS credentials मिले — सबूत कि ऐप के अंदर का secret secret नहीं; Android banking trojans (Anatsa, SharkBot) accessibility और overlay से credentials चुराते हैं।

---

## 🟠 My Stack Example

### Android Network Security Config: no cleartext + public-key pins with backup
```xml
<!-- android/app/src/main/res/xml/network_security_config.xml (via Expo config plugin in managed apps) -->
<network-security-config>
  <base-config cleartextTrafficPermitted="false" />
  <domain-config>
    <domain includeSubdomains="true">api.quickbite.in</domain>
    <pin-set expiration="2027-06-30">                       <!-- after expiry, pinning disabled (safety valve) -->
      <pin digest="SHA-256">7HIpactkIAq2Y49orFOOQKurWxmmSFZhBCoQYcRhJ3Y=</pin>   <!-- current key -->
      <pin digest="SHA-256">fwza0LRMXouZHRC8Ei+4PyuldPDcf3UKgO/04cDM1oE=</pin>   <!-- backup key -->
    </pin-set>
  </domain-config>
</network-security-config>
```
```
iOS: TrustKit or NSPinnedDomains (Info.plist, iOS 14+) with the same SPKI hashes + backup pin
Generate SPKI hash: openssl s_client -connect api.quickbite.in:443 | openssl x509 -pubkey -noout |
                    openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64
```

### Play Integrity / App Attest verification on the backend (sketch, Node)
```js
// Client obtains an integrity token bound to a nonce from our server, sends it with sensitive calls
app.post('/payments/initiate', auth, async (req, res) => {
  const verdict = await verifyIntegrity(req.get('X-Integrity-Token'), req.user.nonce);   // Google API (Android) / App Attest assertion (iOS)
  const risk = scoreRisk({ verdict, rooted: req.get('X-Device-Risk') === 'rooted', ip: req.ip, user: req.user });
  if (risk === 'BLOCK') return res.status(403).json({ error: { code: 'DEVICE_NOT_TRUSTED' } });
  if (risk === 'STEP_UP') return res.status(401).json({ error: { code: 'STEP_UP_REQUIRED', methods: ['OTP', 'BIOMETRIC'] } });
  res.json(await payments.initiate(req.user.id, req.body));
});
// verdict fields (Android): appIntegrity.appRecognitionVerdict === 'PLAY_RECOGNIZED',
//                           deviceIntegrity.deviceRecognitionVerdict includes 'MEETS_DEVICE_INTEGRITY'
```

### Root/jailbreak signal as a risk input (React Native)
```ts
import JailMonkey from 'jail-monkey';
export function deviceRiskHeader() {
  const rooted = JailMonkey.isJailBroken() || JailMonkey.hookDetected?.();
  return rooted ? 'rooted' : 'ok';                 // sent to backend; backend decides (never trust client alone)
}
```

### Protect sensitive screens
```tsx
import * as ScreenCapture from 'expo-screen-capture';
export default function PaymentPinScreen() {
  ScreenCapture.usePreventScreenCapture();          // Android FLAG_SECURE; iOS blocks recording where possible
  return <PinPad secure onComplete={submitPin} />;
}
// App switcher privacy (iOS/Android): cover sensitive content when backgrounded
AppState.addEventListener('change', (s) => setPrivacyCover(s !== 'active'));
```

### Keep secrets on the server: proxy third-party calls
```python
# FastAPI — app never holds the SMS/LLM/maps secret key
@app.post("/places/autocomplete")
async def autocomplete(q: str, user=Depends(current_user)):
    await rate_limit(user.id, "places", per_minute=30)
    r = await httpx_client.get("https://maps.example.com/autocomplete",
                               params={"q": q, "region": "in"}, headers={"X-Api-Key": settings.MAPS_SECRET})
    return trim(r.json())
```

### Android release hardening (app.json / gradle)
```json
{ "expo": { "android": { "allowBackup": false },
  "plugins": [["expo-build-properties", { "android": { "enableProguardInReleaseBuilds": true, "enableShrinkResourcesInReleaseBuilds": true } }]] } }
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you store secrets and sensitive data securely on mobile?**
A1: Store credentials, tokens and encryption keys only in the platform secure stores: iOS Keychain with an appropriate accessibility class (WhenUnlockedThisDeviceOnly) and Android Keystore (hardware-backed or StrongBox where available), optionally gated by biometrics. Encrypt sensitive local databases with keys from those stores. Exclude sensitive files from backups, never log PII or tokens, and wipe data on logout. Never embed server secrets in the app binary, since it can be decompiled. Keep secrets on the backend and proxy third-party calls.

**Q2: What is SSL pinning and what are its risks?**
A2: Pinning makes the app trust only specific server public keys or certificates (by hash) instead of any CA-trusted certificate, preventing man-in-the-middle attacks using rogue or compromised CAs or user-installed proxy certificates. Pin SPKI hashes of your key plus at least one backup key. The risks are operational: if certificates or keys rotate without matching pins in shipped apps, all users lose connectivity until they update, and native config can't be OTA-fixed. Mitigate with backup pins, pin expiration dates, coordinated rotation, monitoring of pin failures, and limiting pinning to high-risk apps and endpoints. Determined attackers on rooted devices can bypass pinning, so combine it with server-side controls.

**Q3: Should apps block rooted or jailbroken devices?**
A3: It depends on risk. Client-side root and jailbreak detection can be bypassed (hooking frameworks), so treat it as one risk signal combined with server-verified attestation (Play Integrity, App Attest), device fingerprinting and behavioural signals. High-risk apps (banking, UPI, trading) often block sensitive actions on compromised devices or require step-up verification, consistent with regulatory expectations. Consumer apps might only increase monitoring or limits. Blocking outright can exclude legitimate users, so explain clearly when you do.

**Q4: How do you stop bots or modified apps from abusing your API?**
A4: Use app attestation (Play Integrity verdicts, App Attest assertions) bound to server-issued nonces and verify them server-side before sensitive operations (sign-up, login, coupons, payments). Combine with authentication, rate limiting per user, device and IP, device-binding keys stored in the Keystore that sign requests, risk scoring (velocity, emulator signals, ASN reputation), and challenges (OTP, CAPTCHA) for suspicious traffic. Never rely only on API keys in the app, since they are extractable.

**Q5: What should never be in a mobile app bundle?**
A5: Server-side secrets: database credentials, cloud access keys, payment-gateway secret keys, private signing keys, LLM or SMS provider secret keys, admin endpoints or backdoors, and debug flags that disable security. Hermes bytecode, minified JS, resources and native binaries are all extractable. Keys that must be public (Maps SDK keys, Firebase config, Razorpay key_id, Sentry DSN) should be restricted by package name and signing certificate, bundle ID, referrers and quotas, with privileged operations done by your backend.

---

## 🔷 Trade-offs
✅ Pinning: strong MITM defence — ❌ rotation outages, maintenance, bypassable on rooted devices.
✅ Root blocking: lower fraud — ❌ excludes some legit users; bypassable → needs attestation.
✅ Attestation (Play Integrity/App Attest): strong genuineness signal — ❌ quotas, latency, platform dependency, not available on all devices (e.g., non-Play Android).
✅ RASP/obfuscation: raises attacker cost — ❌ SDK cost, performance, false positives.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OWASP MASVS | Mobile security standard | mobile सुरक्षा मानक |
| MITM | Man-in-the-middle attack | बीच में सुनने वाला हमला |
| SSL/public-key pinning | Trust only specific keys | सिर्फ़ ख़ास keys पर भरोसा |
| Root / jailbreak | Device with privileged access | पूरे अधिकार वाला फ़ोन |
| App attestation | Proof app/device is genuine | असली ऐप/फ़ोन का सबूत |
| Play Integrity | Google attestation API | Google की पुष्टि सेवा |
| App Attest | Apple attestation API | Apple की पुष्टि सेवा |
| Obfuscation | Making code hard to read | code को उलझाना |
| FLAG_SECURE | Block screenshots (Android) | screenshot रोकना |
| Device binding | Tie account to device/SIM | account को फ़ोन से जोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. Assume the device and binary are hostile: no secrets in the app, Keychain/Keystore for credentials, encrypted sensitive data, no PII in logs/backups.
2. Transport: HTTPS-only, never disable validation, SPKI pinning with backup pins & expiry for high-risk apps; integrity: root detection as a signal + server-verified Play Integrity/App Attest.
3. Harden & protect: R8/obfuscation, allowBackup false, FLAG_SECURE/app-switcher cover, deep link & WebView validation, device binding, risk-based step-up — enforced server-side.

**Hindi:**
1. फ़ोन और ऐप को असुरक्षित मानो: ऐप में secret नहीं, credentials Keychain/Keystore में, संवेदनशील डेटा encrypted।
2. सिर्फ़ HTTPS, ज़रूरत पर backup pin के साथ pinning; root जाँच एक संकेत + सर्वर पर Play Integrity/App Attest।
3. R8, backup बंद, FLAG_SECURE, deep link/WebView जाँच, device binding, जोखिम पर step-up — सब सर्वर पर लागू।

---

## ➡️ Next Topic Suggestion
**M16. Mobile Auth (Token Refresh + Biometric Login)** — Security comes together in authentication. Next: OTP/OAuth login on mobile, token storage and refresh, biometric unlock with Keychain/Keystore, device binding and session management.
