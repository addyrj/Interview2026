# M11. Deep Linking + Universal Links
# हिंदी में: Deep Linking — किसी link, notification या QR code पर tap करते ही ऐप की सही screen सीधे खुलना (जैसे किसी restaurant का page); Universal Links (iOS) और App Links (Android) — आम https वाले link जो ऐप installed हो तो ऐप में और न हो तो website पर खुलें

---

## 🔵 Simple Definition (English)
A **deep link** is a URL that opens a **specific screen inside an app** (not just the home screen), e.g. `https://quickbite.in/restaurant/42` → the Restaurant 42 screen.
Types:
- **Custom URL scheme**: `quickbite://restaurant/42`. Easy, but **any app can claim the same scheme** (insecure), and it doesn't work if the app isn't installed.
- **Universal Links (iOS)** and **Android App Links**: normal **`https://` links verified against your domain** (`/.well-known/apple-app-site-association` and `/.well-known/assetlinks.json`). They open the app if installed, otherwise the website. They're secure (only the domain owner's app can claim them) and the recommended approach.
- **Deferred deep links**: if the app isn't installed, the user goes to the store, installs, opens the app, and **lands on the intended screen** (e.g., a referral or a shared product). Provided by attribution services like Branch, AppsFlyer OneLink and Adjust. (Firebase Dynamic Links was shut down in August 2025.)
- **Platform intents**: e.g., `upi://pay?...` (UPI intent), `tel:`, `mailto:`, `geo:`, WhatsApp `https://wa.me/91XXXXXXXXXX`.
Deep links come from **push notifications, emails/SMS, social shares, QR codes, ads, web banners, and other apps**.

## 🔵 सरल परिभाषा (Hindi)
Deep link = ऐसा URL जो ऐप की किसी ख़ास screen को सीधे खोले (सिर्फ़ home नहीं) — जैसे `https://quickbite.in/restaurant/42`।
प्रकार: custom scheme (`quickbite://`) — आसान पर कोई भी ऐप वही scheme ले सकता है और ऐप न हो तो बेकार; Universal Links (iOS) / App Links (Android) — आपके domain से verified `https://` links, ऐप हो तो ऐप में वरना website पर (सबसे सही); Deferred deep link — ऐप नहीं है तो store → install → खुलते ही सही screen (referral, shared product); और `upi://pay` जैसे platform intents। ये links push, SMS, email, share, QR code, ads से आते हैं।

---

## 🔴 Problem it Solves
Without deep links:
- A user taps "Your order is out for delivery" and lands on the **home screen**, then has to find the order. That's friction and lower conversion.
- A friend shares a restaurant link on WhatsApp, it opens in the **mobile browser** even though the app is installed, and the user must log in again.
- A marketing campaign ("50% off on Biryani") can't take users straight to the offer, so ad spend is wasted.
- Referral programs can't attribute installs to the referrer.
- Insecure custom schemes can be **hijacked** by a malicious app registering the same scheme (e.g., to capture OAuth redirects).
Deep links connect **notifications, marketing, sharing and the web** to the right in-app experience, securely.

## 🔴 यह क्यों बना? (Hindi)
बिना deep link: "आपका order निकल चुका" पर tap → home screen, फिर order ढूँढो; WhatsApp पर share हुआ restaurant link ऐप होते हुए भी browser में खुले; "Biryani पर 50% off" ad सीधे offer तक न ले जाए (पैसा बर्बाद); referral में पता न चले कौन लाया; और custom scheme कोई बुरा ऐप भी ले सकता है (OAuth redirect चुराना)।
Deep links notifications, marketing, sharing और web को ऐप की सही जगह से सुरक्षित तरीके से जोड़ते हैं।

---

## 🟢 How it Works — Step by Step

### Universal Links / App Links verification

```
1. You host on https://quickbite.in (HTTPS, no redirects):
   /.well-known/apple-app-site-association      (JSON, iOS)
   /.well-known/assetlinks.json                 (JSON, Android)
2. App declares the domain:
   iOS: Associated Domains entitlement  applinks:quickbite.in
   Android: intent-filter with android:autoVerify="true", scheme https, host quickbite.in
3. On install/update, the OS fetches the files (iOS via Apple's CDN) and verifies the app ↔ domain link
4. User taps https://quickbite.in/restaurant/42 →
     app installed & verified → OS opens the APP with the URL (no browser)
     not installed            → website opens (which can show "Open in app" / store banner)
Gotchas: iOS doesn't open universal links typed in Safari's address bar or same-domain navigations in
Safari; some in-app browsers (Instagram, some email clients) open the web; keep a web fallback page
```

### Routing inside the app

```
Incoming URL → parse → match route table → validate params → (auth required?) → navigate
  /restaurant/:id        → RestaurantScreen {id}
  /order/:id/track       → TrackScreen {id}           (auth required)
  /offers/:code          → OffersScreen {code}
  /ref/:referrerCode     → store referral, go to signup
  unknown                → home (or open in browser)
Cold start: app launched by the link → wait for navigation + auth bootstrap, then navigate
Warm: app running → handle 'url' event → navigate (don't stack duplicates)
Auth-gated: save pending link → show login → after login, navigate to the saved link
Back stack: build a sensible stack (Home → Restaurant) so "Back" doesn't exit the app
```

### Deferred deep linking (install attribution)

```
User taps https://link.quickbite.in/r/42?ref=ASHA (Branch/AppsFlyer/Adjust link)
 → not installed → service records click (fingerprint/referrer) → redirect to Play Store/App Store
 → user installs & opens → SDK calls service → "this install came from click X" → returns {path: /restaurant/42, ref: ASHA}
 → app navigates + credits referral
Android: Play Install Referrer API gives a reliable referrer string; iOS: probabilistic/clipboard-free
methods are limited by privacy rules (ATT/SKAdNetwork) → match rates lower
```

### Security: links are untrusted input

```
- Validate & whitelist routes and params (ids are numeric/uuid, codes match regex)
- Never perform sensitive actions directly from a link (no "pay ₹5000" or "delete account" without
  explicit user confirmation + auth); treat like a GET request: navigate & show, don't mutate
- Don't put secrets/tokens in deep links (they leak via logs, referrers, screenshots)
- OAuth redirects: use universal/app links or claimed HTTPS redirect URIs + PKCE, not custom schemes
- Validate WebView URLs opened from links (open redirect / phishing)
```

### UPI intent deep links (Indian payments)

```
upi://pay?pa=merchant@okaxis&pn=QuickBite&am=249.00&cu=INR&tn=Order%20123&tr=ORD123
→ Android shows UPI app chooser (PhonePe, GPay, Paytm, BHIM) → user pays → app returns result
→ ALWAYS verify payment status server-side with the PSP/bank (intent result can be spoofed/unclear)
iOS: per-app schemes (phonepe://, tez://, paytmmp://) + LSApplicationQueriesSchemes
```

## 🟢 कैसे काम करता है? (Hindi)
1. अपने domain पर `/.well-known/apple-app-site-association` (iOS) और `/.well-known/assetlinks.json` (Android) रखो; ऐप में Associated Domains / `autoVerify` intent-filter; OS install पर जाँच करता है कि domain और ऐप एक ही मालिक के हैं।
2. Tap पर: ऐप installed और verified → ऐप में खुले; नहीं → website (वहाँ "ऐप में खोलें" banner); WhatsApp/Instagram के in-app browser कभी-कभी web ही खोलते हैं, इसलिए web fallback रखो।
3. ऐप में route table: `/restaurant/:id`, `/order/:id/track` वग़ैरह; params जाँचो; login चाहिए तो link सहेजो → login → फिर वहीं ले जाओ; back stack सही बनाओ।
4. Deferred deep link (Branch/AppsFlyer): ऐप नहीं है → store → install → खुलते ही सही screen और referral credit; Android पर Play Install Referrer भरोसेमंद, iOS पर privacy नियमों से सीमित।
5. Link पर भरोसा मत करो: params जाँचो, link से सीधे payment/delete जैसा काम नहीं (पुष्टि + auth), link में token नहीं; UPI intent (`upi://pay`) से भुगतान के बाद status हमेशा सर्वर से verify करो।

---

## 🟡 Real World Example

**WhatsApp click-to-chat (`wa.me/91…`)** — a universal/app link that opens a chat with a number directly, widely used by Indian small businesses on posters, Instagram bios and QR codes.

**UPI intents** — merchants and apps (Swiggy, Zomato, Flipkart checkout) use `upi://pay` intents so users pick PhonePe, Google Pay or Paytm and pay in two taps. Server-side status verification is mandatory. UPI QR codes in every shop encode the same `upi://pay` URI.

**Swiggy / Zomato / Myntra share links** — sharing a restaurant or product creates an https link that opens the exact screen in the app if installed, or a web page or store otherwise. Referral codes ("Get ₹100 off") rely on deferred deep linking.

**Firebase Dynamic Links shutdown (Aug 2025)** — Google deprecated and shut down FDL, forcing many apps to migrate to native Universal/App Links plus vendors like Branch or AppsFlyer. A reminder not to depend entirely on one vendor for core routing.

## 🟡 Real Example Hindi में
`wa.me/91…` link से सीधे WhatsApp chat खुलती है — भारत के छोटे व्यापारी इसे poster, Instagram bio और QR में इस्तेमाल करते हैं। UPI QR और checkout में `upi://pay` intent से PhonePe/GPay/Paytm चुनकर दो taps में भुगतान (status सर्वर से verify ज़रूरी)।
Swiggy/Zomato/Myntra के share links ऐप हो तो सीधे वही screen खोलते हैं; referral deferred deep link पर चलते हैं; Firebase Dynamic Links अगस्त 2025 में बंद हुआ — कई ऐप्स को migrate करना पड़ा।

---

## 🟠 My Stack Example

### Domain association files (served by Nginx/Next.js at /.well-known/)
```json
// apple-app-site-association (no .json extension, Content-Type: application/json)
{ "applinks": { "details": [ { "appIDs": ["ABCDE12345.in.quickbite.app"],
    "components": [ { "/": "/restaurant/*" }, { "/": "/order/*" }, { "/": "/offers/*" }, { "/": "/ref/*" },
                    { "/": "/account/*", "exclude": true } ] } ] } }
```
```json
// assetlinks.json
[{ "relation": ["delegate_permission/common.handle_all_urls"],
   "target": { "namespace": "android_app", "package_name": "in.quickbite.app",
               "sha256_cert_fingerprints": ["AB:CD:…:EF"] } }]   // Play App Signing certificate fingerprint!
```

### Expo config: associated domains + intent filters + scheme
```json
{ "expo": {
  "scheme": "quickbite",
  "ios": { "bundleIdentifier": "in.quickbite.app", "associatedDomains": ["applinks:quickbite.in"] },
  "android": { "package": "in.quickbite.app", "intentFilters": [{
      "action": "VIEW", "autoVerify": true,
      "data": [{ "scheme": "https", "host": "quickbite.in", "pathPrefix": "/restaurant" },
               { "scheme": "https", "host": "quickbite.in", "pathPrefix": "/order" },
               { "scheme": "https", "host": "quickbite.in", "pathPrefix": "/offers" }],
      "category": ["BROWSABLE", "DEFAULT"] }] } } }
```

### Expo Router: file-based routes are deep-linkable automatically
```
app/restaurant/[id].tsx      ← https://quickbite.in/restaurant/42  or  quickbite://restaurant/42
app/order/[id]/track.tsx     ← https://quickbite.in/order/123/track
app/offers/[code].tsx
app/+native-intent.tsx       ← rewrite/validate incoming URLs before routing
```
```tsx
// app/+native-intent.tsx — validate & normalize every incoming link (Expo Router)
export function redirectSystemPath({ path }: { path: string; initial: boolean }) {
  try {
    const url = new URL(path, 'https://quickbite.in');
    const m = url.pathname.match(/^\/restaurant\/(\d+)$/);
    if (m) return `/restaurant/${m[1]}`;
    if (/^\/order\/[0-9a-f-]{36}\/track$/.test(url.pathname)) return url.pathname;
    if (/^\/offers\/[A-Z0-9]{4,12}$/.test(url.pathname)) return url.pathname;
    if (url.pathname.startsWith('/ref/')) { kv.set('pendingReferral', url.pathname.slice(5, 25)); return '/signup'; }
    return '/';                                                  // unknown → home
  } catch { return '/'; }
}
```

### Auth-gated deep links
```tsx
// app/order/[id]/track.tsx
export default function Track() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { user, ready } = useAuth();
  if (!ready) return <Splash />;
  if (!user) return <Redirect href={{ pathname: '/login', params: { next: `/order/${id}/track` } }} />;
  return <TrackOrder orderId={id} />;
}
// login screen: after success → router.replace(validatedNext ?? '/')
```

### UPI intent checkout (Android) + server verification
```ts
import { Linking } from 'react-native';
export async function payWithUpi(order: { id: string; amountPaise: number }) {
  const { vpa, txnRef } = await http.post(`/payments/upi/intent`, { orderId: order.id }).then(r => r.data);  // server creates txn
  const url = `upi://pay?pa=${vpa}&pn=${encodeURIComponent('QuickBite')}&am=${(order.amountPaise / 100).toFixed(2)}&cu=INR&tr=${txnRef}&tn=${encodeURIComponent('Order ' + order.id)}`;
  await Linking.openURL(url);                                    // user picks PhonePe/GPay/Paytm
  // On return to app: poll server for final status — never trust the intent result alone
  return pollPaymentStatus(txnRef, { timeoutMs: 120_000 });
}
```

### Backend: share link with OG tags + store fallback (Next.js page)
```tsx
// app/restaurant/[id]/page.tsx (web) — also the fallback when app isn't installed
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const r = await getRestaurant((await params).id);
  return { title: `${r.name} — Order on QuickBite`, openGraph: { images: [r.imageUrl] },
           other: { 'apple-itunes-app': `app-id=1234567890, app-argument=https://quickbite.in/restaurant/${r.id}` } };  // Smart App Banner
}
```

### Test deep links
```bash
# iOS simulator
xcrun simctl openurl booted "https://quickbite.in/restaurant/42"
# Android emulator/device
adb shell am start -a android.intent.action.VIEW -d "https://quickbite.in/order/123/track" in.quickbite.app
adb shell pm get-app-links in.quickbite.app        # verification state (verified / none)
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between custom URL schemes and Universal/App Links?**
A1: Custom schemes (`myapp://`) are simple to set up but unverified: any app can register the same scheme, which enables hijacking (e.g., intercepting OAuth redirects). They do nothing if the app isn't installed, and they can show "open with" dialogs. Universal Links (iOS) and App Links (Android) use regular HTTPS URLs verified via files hosted on your domain, so only your app can handle them. They open the app when installed and fall back to the website otherwise, and they work across web, email and social. They're the recommended choice, with custom schemes kept for internal or inter-app cases.

**Q2: How do deferred deep links work?**
A2: When a user without the app taps a smart link, an attribution service records the click (with the Play Install Referrer on Android, or probabilistic matching within iOS privacy limits) and redirects to the app store. After install and first open, the app's SDK queries the service, which matches the install to the click and returns the original link data (route plus parameters like a referral code). The app then navigates there and credits attribution. Match accuracy on iOS is limited by privacy rules (ATT, SKAdNetwork).

**Q3: How do you handle deep links that require login?**
A3: Parse and validate the link, and if the route requires authentication and the user isn't logged in, persist the pending destination (memory, or MMKV for cold starts), show the login flow, and after successful authentication navigate to the saved destination. Validate it against the route allow-list to avoid open redirects. Build a sensible back stack. Handle cold-start timing by waiting until navigation and auth bootstrap are ready before navigating.

**Q4: What security considerations apply to deep links?**
A4: Treat all link data as untrusted input. Allow-list routes and validate parameter formats. Never perform state-changing or sensitive actions directly from a link without explicit confirmation and authentication. Never embed tokens or secrets in links. Use verified HTTPS links (Universal/App Links) for OAuth and payment returns instead of custom schemes. Validate URLs before opening them in WebViews. For payment intents like UPI, always verify the final status on the server rather than trusting the returned intent data.

**Q5: Why might a Universal Link open the website instead of the app?**
A5: The apple-app-site-association file may be invalid, unreachable, redirected or have the wrong content type. The app ID, team ID or path patterns may be wrong, or the associated domains entitlement may be missing. The user may have long-pressed and chosen "Open in Safari" (iOS remembers that). The link may have been typed into Safari's address bar, or be a same-domain navigation. Some in-app browsers don't honour universal links. On Android, App Link verification fails if `assetlinks.json` doesn't match the Play App Signing certificate fingerprint. Debug with OS tools (`pm get-app-links`, the Apple AASA validator) and keep a web fallback with "Open in app".

---

## 🔷 Trade-offs
✅ Universal/App Links: secure, web fallback — ❌ setup/verification gotchas, in-app browser quirks.
✅ Custom schemes: easy — ❌ hijackable, no fallback.
✅ Attribution vendors (Branch/AppsFlyer): deferred links + analytics — ❌ cost, SDK weight, privacy limits, vendor risk.
✅ Rich deep linking everywhere: higher conversion — ❌ more routes to validate/test & keep backward compatible.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Deep link | URL to a specific in-app screen | ऐप की ख़ास screen का link |
| Custom URL scheme | myapp:// style link | अपना scheme |
| Universal Link | iOS verified https link | iOS का verified link |
| App Link | Android verified https link | Android का verified link |
| AASA | apple-app-site-association file | iOS की जाँच file |
| assetlinks.json | Android verification file | Android की जाँच file |
| Deferred deep link | Survives install | install के बाद भी सही screen |
| Attribution | Which link/campaign drove install | install किस link से आया |
| UPI intent | upi://pay deep link | UPI भुगतान link |
| Smart App Banner | iOS web banner to open/install app | ऐप खोलने का banner |

---

## ⚡ 3-Line Summary
**English:**
1. Prefer verified Universal Links/App Links (https + .well-known files) over custom schemes; keep a web fallback; use deferred deep links for installs/referrals.
2. Route centrally: parse → allow-list & validate → handle cold/warm start → auth gate with saved destination → sensible back stack.
3. Treat links as untrusted: no direct sensitive actions, no secrets in URLs, verify payment intents server-side; test with simctl/adb and verification tools.

**Hindi:**
1. Custom scheme की जगह verified Universal/App Links; web fallback; install/referral के लिए deferred deep links।
2. एक जगह routing: parse → जाँच → cold/warm start → login के बाद सही जगह → सही back stack।
3. Links पर भरोसा नहीं: सीधे संवेदनशील काम नहीं, URL में secret नहीं, UPI status सर्वर से जाँचो।

---

## ➡️ Next Topic Suggestion
**M12. Image Loading + Caching on Mobile** — Deep links bring users to image-heavy screens (menus, products, feeds). Next: why images are the top memory and performance risk on phones, and how image loaders decode, cache and prioritize them.
