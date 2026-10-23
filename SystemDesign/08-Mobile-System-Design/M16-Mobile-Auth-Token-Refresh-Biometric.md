# M16. Mobile Auth (Token Refresh + Biometric Login)
# हिंदी में: Mobile Auth — फ़ोन ऐप में login (OTP, Google/Apple, OAuth), tokens को सुरक्षित तिजोरी में रखना और चुपचाप refresh करना, fingerprint/Face ID से जल्दी unlock, device binding, और सब devices से logout

---

## 🔵 Simple Definition (English)
Mobile authentication covers how users **sign in**, how the app **stays signed in securely**, and how **sensitive actions are protected**:
- **Login methods**: phone + **OTP** (most common in India), with auto-read via Android **SMS Retriever API** and iOS one-time-code autofill; **Google/Apple Sign-In**; **OAuth/OIDC with PKCE via the system browser** (ASWebAuthenticationSession / Chrome Custom Tabs, never an embedded WebView); one-tap providers (e.g., Truecaller SDK); **passkeys**.
- **Tokens**: a short-lived **access token** in memory, and a long-lived **refresh token** in **Keychain/Keystore**, rotated on use, with single-flight refresh on 401 (F11/F16).
- **Biometric login**: Face ID / Touch ID / fingerprint **unlocks a locally stored secret** (refresh token or device key). **Biometric data never leaves the device** and is never sent to your server.
- **Device binding**: a key pair generated in the **Secure Enclave/Keystore** at login. The server stores the public key, and refresh or high-risk requests are signed, so a stolen refresh token alone is useless.
- **Session management**: device list, remote logout, logout everywhere on password or PIN change, and **step-up auth** (PIN/biometric/OTP) for payments.

## 🔵 सरल परिभाषा (Hindi)
Mobile auth = यूज़र कैसे login करे, ऐप सुरक्षित तरीके से logged-in कैसे रहे, और ज़रूरी कामों को कैसे बचाएँ: login — phone + OTP (भारत में सबसे आम, Android SMS Retriever से अपने-आप भरना), Google/Apple Sign-In, system browser से OAuth + PKCE (embedded WebView नहीं), passkeys।
Tokens — access token memory में (छोटी उम्र), refresh token Keychain/Keystore में (हर बार बदलता); biometric (Face ID/fingerprint) सिर्फ़ फ़ोन में रखे secret को खोलता है — biometric डेटा कभी सर्वर पर नहीं जाता; device binding — Secure Enclave/Keystore में key, चोरी हुआ refresh token अकेले बेकार; devices की list, remote logout, payment के लिए step-up।

---

## 🔴 Problem it Solves
Mobile users expect to **open the app and be logged in instantly**, while the app holds valuable access (wallets, UPI, orders, chats). Problems without a solid design:
- **Logged out constantly**: no refresh flow, or refresh races cause random logouts.
- **Token theft**: tokens in AsyncStorage on rooted devices, or tokens copied from backups, give long-term access from another device.
- **OTP abuse**: SMS-pumping fraud (bots requesting OTPs to premium numbers costs lakhs in SMS bills), brute-forcing 4-digit OTPs, SIM-swap account takeovers.
- **OAuth in WebViews**: the app can see passwords, phishing is possible, and Google blocks embedded WebViews for sign-in.
- **No quick re-auth**: typing passwords for every payment kills conversion, while no re-auth at all is risky.
- **Lost or stolen phone**: no way to revoke that device's session.

## 🔴 यह क्यों बना? (Hindi)
यूज़र चाहते हैं ऐप खोलते ही logged-in, जबकि ऐप के पास wallet, UPI, orders जैसी क़ीमती पहुँच है। बिना ठोस design: बार-बार logout (refresh नहीं या race); rooted फ़ोन/backup से token चोरी और दूसरे फ़ोन से इस्तेमाल; OTP का दुरुपयोग (bots से SMS pumping — लाखों का SMS बिल, 4 अंक का OTP brute force, SIM swap); WebView में OAuth (password ऐप देख सकता, Google इसे रोकता है); हर payment पर password = conversion ख़त्म, और बिल्कुल न पूछो तो ख़तरा; फ़ोन खोने पर उस device का session रद्द करने का तरीका नहीं।

---

## 🟢 How it Works — Step by Step

### Phone + OTP login (India default)

```
1. User enters +91 98XXXXXX10 → POST /auth/otp/request {phone, appHash}
   Server: rate-limit (per phone, per device, per IP), bot checks (Play Integrity/App Attest, CAPTCHA
   fallback), generate 6-digit OTP, store HASH + expiry (5 min) + attempts (max 5), send via SMS (DLT-
   registered template) or WhatsApp
2. Android SMS Retriever API: SMS contains "<#> 482913 is your QuickBite OTP. FA+9qCX9VSu"
   (app hash) → app reads it automatically, no SMS permission needed
   iOS: textContentType="oneTimeCode" → keyboard suggests the code from Messages
3. POST /auth/otp/verify {phone, otp, deviceId, devicePublicKey}
   Server: constant-time compare hash, attempts++, on success → create session:
     access token (JWT, 15 min) + refresh token (opaque, 30–90 days, rotation family) + bind device key
4. App: access → memory; refresh → Keychain/Keystore; user profile → MMKV/DB
Abuse controls: exponential cooldown on resend (30 s, 60 s, …), daily caps, block premium/intl number
ranges, monitor SMS spend anomalies (SMS pumping)
```

### Social / OAuth login on mobile

```
Google/Apple native SDKs → ID token (OIDC) → POST /auth/google {idToken} → server verifies signature,
aud, iss, exp, nonce → finds/creates user → issues YOUR session tokens
Generic OAuth/OIDC provider: Authorization Code + PKCE in the SYSTEM browser
  (ASWebAuthenticationSession / Custom Tabs), redirect via Universal/App Link (M11) → exchange code
App Store rule: apps offering third-party social login must also offer an equivalent privacy-focused
option (Sign in with Apple commonly)
```

### Token storage & refresh (mobile)

```
Access token   → memory only (lost on app kill; refreshed on start)
Refresh token  → Keychain (WhenUnlockedThisDeviceOnly) / Keystore-encrypted storage
On app start   → read refresh → POST /auth/refresh (signed with device key) → new access + rotated refresh
On 401         → single-flight refresh, retry original requests (shared http.ts from F11)
Refresh fails  → 401 again: tokens revoked/expired → clear & go to login (keep drafts/outbox for same user)
Reuse detection→ old refresh used again → revoke family → force re-login (possible theft)
```

### Device binding (proof of possession)

```
At login: app generates a key pair INSIDE Secure Enclave (iOS) / Keystore (Android, StrongBox if available)
          → private key never extractable → sends public key → server stores (user_id, device_id, pubkey)
On refresh/payment: server sends nonce → app signs (nonce + request hash) with private key → server
          verifies with stored public key → only THIS device can use the session
Stolen refresh token copied elsewhere → can't produce signature → rejected ✅
UPI apps go further: device binding via SMS sent FROM the registered SIM (proves SIM in this phone)
```

### Biometric login / app lock

```
Biometrics are LOCAL: OS verifies face/finger → releases a Keychain/Keystore item or authorizes key use
Pattern A (unlock stored secret): refresh token stored with access control "biometry required"
  → Face ID prompt → token readable → refresh session
Pattern B (sign challenge): device private key requires user authentication for each use
  → biometric prompt → sign server challenge → step-up for payments
Always offer fallback (app PIN / device passcode); invalidate keys when biometrics change
(new fingerprint enrolled → require full login), respect "Allow biometrics" setting
```

### Session management & step-up

```
Server sessions table: device name, platform, app version, last IP/city, last used, revoked_at
Screens: "Logged-in devices" → revoke one → its refresh family revoked (access dies within 15 min)
Password/PIN change or suspected compromise → revoke all other sessions
Step-up: payment > ₹2,000, adding bank account, changing phone → require biometric/PIN/OTP within last N min
Inactivity timeout for financial apps (e.g., 5–10 min in background → app lock)
```

## 🟢 कैसे काम करता है? (Hindi)
1. OTP login: phone डालो → सर्वर rate limit + bot जाँच (Play Integrity/CAPTCHA), 6 अंक का OTP बनाकर उसका hash 5 मिनट के लिए रखे, SMS (DLT template) भेजे; Android SMS Retriever से OTP अपने-आप भरता है, iOS keyboard सुझाता है; सही OTP पर access + refresh token और device key जोड़ी।
2. Google/Apple: native SDK से ID token → सर्वर signature/aud/exp जाँचकर अपना session token दे; बाक़ी OAuth system browser में PKCE के साथ, redirect Universal/App Link से; WebView नहीं।
3. Access token memory में, refresh Keychain/Keystore में; app start पर और 401 पर एक ही बार refresh (rotation); पुराना refresh दोबारा आए तो पूरा family रद्द।
4. Device binding: login पर Secure Enclave/Keystore में key pair, public key सर्वर पर; refresh/payment पर challenge sign — चोरी हुआ token दूसरे फ़ोन पर बेकार; UPI ऐप registered SIM से SMS भेजकर फ़ोन की पुष्टि करते हैं।
5. Biometric सिर्फ़ फ़ोन पर जाँचता है और Keychain item/key खोलता है; PIN fallback, नया fingerprint जुड़े तो पूरा login; devices की list और remote logout, बड़े payment पर step-up, financial ऐप में कुछ मिनट background के बाद app lock।

---

## 🟡 Real World Example

**Swiggy / Zomato / Zepto / Blinkit** — phone-number OTP login with auto-read (SMS Retriever), Truecaller one-tap on Android in some apps, and long-lived sessions so users rarely log in again.

**UPI apps (PhonePe, Google Pay, Paytm, BHIM)** — device binding through an SMS sent from the registered SIM, an app lock (PIN/biometric) and the **UPI PIN** entered in the NPCI common library for every payment. That's a layered step-up model: device + app lock + transaction PIN.

**Banking apps (HDFC, ICICI iMobile, SBI YONO)** — MPIN/biometric login on registered devices, a single active device per user in many cases, session timeouts, and re-registration when the SIM changes.

**Google's embedded WebView ban (2016–2021)** — Google blocked OAuth sign-in from embedded WebViews, requiring the system browser for security (phishing and credential exposure). The industry standard is RFC 8252 (OAuth for Native Apps).

## 🟡 Real Example Hindi में
Swiggy/Zomato/Zepto में phone OTP login (SMS Retriever से अपने-आप) और लंबे sessions; कुछ ऐप में Truecaller one-tap।
UPI ऐप (PhonePe, Google Pay, Paytm, BHIM) में registered SIM से SMS भेजकर device binding, app lock (PIN/biometric) और हर payment पर NPCI library में UPI PIN — परतों वाली सुरक्षा; बैंक ऐप में registered device पर MPIN/biometric, SIM बदलने पर दोबारा registration; Google ने embedded WebView से OAuth login बंद किया (RFC 8252)।

---

## 🟠 My Stack Example

### OTP request/verify with abuse controls (FastAPI + Redis)
```python
import secrets, hashlib, hmac
OTP_TTL, MAX_ATTEMPTS = 300, 5

@app.post("/auth/otp/request")
async def otp_request(body: OtpRequest, request: Request):
    phone = normalize_in(body.phone)                                   # +91XXXXXXXXXX
    await enforce_limits(phone=phone, ip=request.client.host, device=body.device_id)   # e.g. 3/10min, 10/day
    if not await verify_attestation(body.integrity_token): raise HTTPException(403, "device check failed")
    otp = f"{secrets.randbelow(10**6):06d}"
    await redis.hset(f"otp:{phone}", mapping={"h": hash_otp(phone, otp), "attempts": 0})
    await redis.expire(f"otp:{phone}", OTP_TTL)
    await sms.send(phone, template="LOGIN_OTP", vars={"otp": otp, "hash": body.app_hash})   # DLT template
    return {"retryAfter": 30}

@app.post("/auth/otp/verify")
async def otp_verify(body: OtpVerify):
    key = f"otp:{normalize_in(body.phone)}"
    rec = await redis.hgetall(key)
    if not rec: raise HTTPException(400, "OTP expired")
    if int(rec["attempts"]) >= MAX_ATTEMPTS: raise HTTPException(429, "Too many attempts")
    await redis.hincrby(key, "attempts", 1)
    if not hmac.compare_digest(rec["h"], hash_otp(body.phone, body.otp)): raise HTTPException(401, "Wrong OTP")
    await redis.delete(key)
    user = await get_or_create_user(body.phone)
    return await create_session(user, device_id=body.device_id, device_pubkey=body.device_public_key)

def hash_otp(phone: str, otp: str) -> str:
    return hmac.new(settings.OTP_PEPPER.encode(), f"{phone}:{otp}".encode(), hashlib.sha256).hexdigest()
```

### React Native: OTP auto-fill (Android SMS Retriever + iOS)
```tsx
// iOS + Android autofill hints
<TextInput value={otp} onChangeText={setOtp} keyboardType="number-pad" maxLength={6}
  textContentType="oneTimeCode" autoComplete="sms-otp" accessibilityLabel="OTP" />
// Android auto-read without SMS permission: react-native-otp-verify (SMS Retriever) → getHash() → send hash in OTP request
```

### Token store: refresh in Keychain/Keystore, access in memory, device-signed refresh
```ts
// src/data/session.ts
import * as SecureStore from 'expo-secure-store';
let access: string | null = null;
let refreshing: Promise<string> | null = null;
const OPTS = { keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY };

export const session = {
  access: () => access,
  async save(tokens: { access: string; refresh: string }) { access = tokens.access; await SecureStore.setItemAsync('refresh', tokens.refresh, OPTS); },
  async refresh(): Promise<string> {
    refreshing ??= (async () => {
      const refresh = await SecureStore.getItemAsync('refresh', OPTS);
      if (!refresh) throw new Error('NO_SESSION');
      const { nonce } = await http.get('/auth/nonce').then((r) => r.data);
      const signature = await deviceKey.sign(`${nonce}.${refresh.slice(0, 16)}`);     // native module: Secure Enclave / Keystore
      const r = await http.post('/auth/refresh', { refresh, nonce, signature }, { skipAuth: true } as any);
      await session.save(r.data);
      return r.data.access as string;
    })().finally(() => (refreshing = null));
    return refreshing;
  },
  async clear() { access = null; await SecureStore.deleteItemAsync('refresh', OPTS); },
};
```

### Biometric app unlock / step-up (expo-local-authentication)
```ts
import * as LocalAuthentication from 'expo-local-authentication';
export async function requireBiometric(reason = 'Confirm payment of ₹1,499') {
  const has = (await LocalAuthentication.hasHardwareAsync()) && (await LocalAuthentication.isEnrolledAsync());
  if (!has) return promptAppPin();                                       // fallback
  const res = await LocalAuthentication.authenticateAsync({ promptMessage: reason, fallbackLabel: 'Use PIN', disableDeviceFallback: false });
  return res.success;
}
// Stronger: store refresh token with SecureStore requireAuthentication: true → OS biometric gate to read it
await SecureStore.setItemAsync('refresh', token, { ...OPTS, requireAuthentication: true, authenticationPrompt: 'Unlock QuickBite' });
```

### Google Sign-In: verify ID token on the server (Node)
```js
import { OAuth2Client } from 'google-auth-library';
const client = new OAuth2Client();
app.post('/auth/google', async (req, res) => {
  const ticket = await client.verifyIdToken({ idToken: req.body.idToken, audience: [ANDROID_CLIENT_ID, IOS_CLIENT_ID, WEB_CLIENT_ID] });
  const p = ticket.getPayload();                                   // sub, email, email_verified, name
  if (!p?.email_verified) return res.status(401).end();
  const user = await Users.upsertByGoogleSub(p.sub, { email: p.email, name: p.name });
  res.json(await createSession(user, req.body.deviceId, req.body.devicePublicKey));
});
```

### Devices & remote logout
```sql
CREATE TABLE sessions (id UUID PRIMARY KEY, user_id BIGINT NOT NULL, device_id TEXT NOT NULL, device_name TEXT,
  platform TEXT, device_pubkey TEXT, refresh_family UUID NOT NULL, last_used_at TIMESTAMPTZ, last_city TEXT,
  created_at TIMESTAMPTZ DEFAULT now(), revoked_at TIMESTAMPTZ);
-- revoke one device: UPDATE sessions SET revoked_at=now() WHERE id=$1 AND user_id=$2;  (+ revoke refresh family)
-- logout everywhere except current: UPDATE sessions SET revoked_at=now() WHERE user_id=$1 AND id<>$2;
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you design OTP login for an Indian consumer app?**
A1: The client sends the phone number plus app hash and an attestation token. The server rate-limits per phone, device and IP with exponential resend cooldowns, verifies the device, generates a random 6-digit OTP, stores only its HMAC hash with a 5-minute TTL and an attempt counter, and sends it via a DLT-registered SMS template (or WhatsApp). Android auto-reads it with the SMS Retriever API and iOS uses one-time-code autofill. Verification does a constant-time compare, limits attempts and deletes the OTP on success, then issues a session: a short-lived access token, a rotating refresh token and device-key binding. Monitor SMS costs for pumping fraud and block suspicious number ranges.

**Q2: Where should a React Native app store tokens and how do you refresh them?**
A2: Keep the access token in memory and the refresh token in Keychain/Keystore (expo-secure-store or react-native-keychain) with a this-device-only accessibility class. On app start, read the refresh token and obtain a new access token (ideally with a signature from a device-bound key). On 401, a single-flight refresh shares one in-flight promise across concurrent failures, then retries the queued requests. Rotate refresh tokens on every use with reuse detection. If refresh fails with an auth error, clear the session and route to login, preserving local drafts for the same user.

**Q3: How does biometric login actually work, and what does the server see?**
A3: Biometric verification happens entirely on the device in secure hardware. The app never receives fingerprint or face data, and the server never does either. The OS releases a protected secret (a refresh token stored with biometric access control) or authorizes the use of a hardware-backed private key after a successful biometric match. The server only sees normal token refreshes or signatures over its challenges. Provide PIN or passcode fallback, invalidate keys when biometric enrollment changes, and use biometrics for convenience and step-up, not as the identity proof at first login.

**Q4: What is device binding and why is it valuable?**
A4: At login, the app generates a non-exportable key pair in the Secure Enclave or Android Keystore and registers the public key with the server for that session. Sensitive calls (refresh, payments) include a signature over a server nonce, so possession of the specific device is proven. A refresh token stolen via backup, logs or malware can't be used from another device without the private key. UPI apps add SIM binding by sending an SMS from the registered SIM. Device binding also enables "trusted device" UX and per-device revocation.

**Q5: Why must OAuth on mobile use the system browser instead of a WebView?**
A5: In an embedded WebView the host app can read keystrokes and cookies, so it could capture the user's identity-provider password. Users can't verify the real URL (phishing risk), and they don't benefit from existing browser sessions or password managers. RFC 8252 requires external user agents (ASWebAuthenticationSession, Chrome Custom Tabs) with Authorization Code + PKCE and redirects via claimed HTTPS links or app links. Major providers like Google block sign-in from embedded WebViews.

---

## 🔷 Trade-offs
✅ OTP login: familiar, no passwords — ❌ SMS cost, SIM-swap risk, delivery delays → add device binding/WhatsApp OTP.
✅ Long-lived refresh + biometric unlock: great UX — ❌ must protect with Keystore, rotation, device binding, remote revoke.
✅ Device binding: stops token replay — ❌ complexity, device change/reinstall flows.
✅ Passkeys: phishing-resistant — ❌ ecosystem adoption still growing, account recovery design needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OTP | One-time password | एक बार का पासवर्ड |
| SMS Retriever API | Android OTP auto-read | Android पर OTP अपने-आप पढ़ना |
| PKCE | Code exchange protection for apps | ऐप के लिए OAuth सुरक्षा |
| Refresh token rotation | New refresh token each use | हर बार नया refresh token |
| Secure Enclave / Keystore | Hardware key storage | hardware में key |
| Device binding | Session tied to device key/SIM | session को फ़ोन से बाँधना |
| Biometric auth | Face/fingerprint on device | चेहरा/उँगली से पहचान |
| Step-up auth | Extra check for risky actions | ज़रूरी काम पर अतिरिक्त जाँच |
| SMS pumping | OTP-request fraud for SMS revenue | नक़ली OTP से SMS धोखा |
| Passkey | WebAuthn credential replacing passwords | बिना password की चाबी |

---

## ⚡ 3-Line Summary
**English:**
1. Login: OTP with strong abuse controls + auto-read, native Google/Apple sign-in verified server-side, OAuth via system browser + PKCE; consider passkeys.
2. Session: access in memory, rotating refresh in Keychain/Keystore, single-flight refresh, device-bound keys signing refresh/payments.
3. Biometrics unlock local secrets (never leave device) for quick login & step-up; manage devices, remote logout, timeouts and re-auth for sensitive actions.

**Hindi:**
1. Login: OTP (सख़्त सीमा + अपने-आप पढ़ना), Google/Apple sign-in सर्वर पर जाँच, OAuth system browser + PKCE से।
2. Session: access memory में, refresh Keychain में (rotation), एक ही बार refresh, device key से sign।
3. Biometric फ़ोन में ही secret खोलता है; devices की list, remote logout, timeout और बड़े काम पर दोबारा जाँच।

---

## ➡️ Next Topic Suggestion
**M17. OTA Updates (EAS Update / CodePush)** — Even with great design, bugs ship. Next: how React Native apps push JS fixes over the air without app-store releases, plus runtime-version compatibility, staged rollouts and rollbacks.
