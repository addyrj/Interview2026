# 189. Next.js Environment Variables
# हिंदी में: Next.js Environment Variables — Secrets और Config को सुरक्षित रखना

---

## 🔵 Simple Definition (English)
**Environment variables** are key-value settings (API URLs, database passwords, keys) stored outside your code, in `.env` files or the hosting dashboard. In Next.js, variables are server-only by default, and only those starting with `NEXT_PUBLIC_` are sent to the browser.

## 🔵 सरल परिभाषा (Hindi)
**Environment variables** ऐसी key-value settings हैं (API URL, database password, keys) जो code के बाहर `.env` files या hosting dashboard में रखी जाती हैं। Next.js में variables default रूप से सिर्फ server पर रहते हैं, और केवल `NEXT_PUBLIC_` से शुरू होने वाले variables browser को भेजे जाते हैं।

---

## 🔴 Problem it Solves

If you hard-code the payment key or database URL in your source, it ends up in Git and anyone with repo access can see it. Also, development, staging and production need different values (a test database versus the real one). Changing code for each environment is risky. Environment variables keep secrets out of code and let the same code run everywhere with different settings.

```jsx
// PROBLEM: secret inside code, goes to GitHub
const stripe = new Stripe('sk_live_abc123');

// SOLUTION: read from the environment, value lives only on the server
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
```

## 🔴 यह क्यों बना? (Hindi)
अगर आप payment key या database URL सीधे code में लिख दें तो वह Git में चली जाती है और repo access वाला हर व्यक्ति उसे देख सकता है। साथ ही development, staging और production के लिए अलग values चाहिए (test database बनाम असली database)। हर environment के लिए code बदलना जोखिम भरा है। Environment variables secrets को code से बाहर रखते हैं और एक ही code को अलग settings के साथ हर जगह चलने देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create .env.local in the project root (never commit it)
Step 2 → Write KEY=value lines, e.g. DATABASE_URL=postgres://...
Step 3 → Next.js loads env files at startup into process.env (server side)
Step 4 → Variables WITHOUT prefix stay on the server (Server Components, route handlers, Server Actions)
Step 5 → Variables WITH NEXT_PUBLIC_ are inlined into the browser JavaScript at BUILD time
Step 6 → On Vercel/AWS you set the same names in the dashboard instead of files
Step 7 → Changing a NEXT_PUBLIC_ value needs a new build; server-only values are read at runtime
```

Load order (highest priority first): `process.env` (real environment) → `.env.$(NODE_ENV).local` → `.env.local` (not loaded in `test`) → `.env.$(NODE_ENV)` → `.env`. Common files: `.env.development`, `.env.production`.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Project root में .env.local बनाओ (इसे कभी commit मत करो)
Step 2 → KEY=value लाइनें लिखो, जैसे DATABASE_URL=postgres://...
Step 3 → Next.js startup पर env files को process.env में load करता है (server side)
Step 4 → बिना prefix वाले variables server पर ही रहते हैं (Server Components, route handlers, Server Actions)
Step 5 → NEXT_PUBLIC_ वाले variables BUILD के समय browser JavaScript में सीधे भर दिए जाते हैं
Step 6 → Vercel/AWS पर वही नाम dashboard में set करते हैं, files में नहीं
Step 7 → NEXT_PUBLIC_ की value बदलने के लिए नया build चाहिए; server-only values runtime पर पढ़ी जाती हैं
```

---

## 🟡 Real World Example
**Zomato-style app:** The map widget needs a public Maps key (`NEXT_PUBLIC_MAPS_KEY`, restricted by domain) in the browser. The payment gateway secret (`PAYMENT_SECRET`) and database URL (`DATABASE_URL`) must never reach the browser, so they have no prefix and are used only in a Server Action that creates the order. Staging uses a test payment key and production uses the live key, with the same code.

## 🟡 Real Example Hindi mein
**Zomato जैसा app:** Map widget को browser में एक public Maps key चाहिए (`NEXT_PUBLIC_MAPS_KEY`, जो domain से restricted है)। Payment gateway का secret (`PAYMENT_SECRET`) और database URL (`DATABASE_URL`) कभी browser तक नहीं पहुँचने चाहिए, इसलिए इन पर prefix नहीं है और ये सिर्फ order बनाने वाले Server Action में इस्तेमाल होते हैं। Staging में test payment key और production में live key होती है, code वही रहता है।

---

## 💻 Code Example — Basic

```jsx
// .env.local (file in project root, add to .gitignore)
// DATABASE_URL=postgres://user:pass@localhost:5432/food   <- server only
// PAYMENT_SECRET=sk_test_123                              <- server only
// NEXT_PUBLIC_API_BASE=https://api.example.com            <- visible in browser

// app/page.jsx  (Server Component: can read ALL variables)
export default function Page() {
  const secret = process.env.PAYMENT_SECRET;              // available on the server
  const hasSecret = Boolean(secret);                      // never print secrets, only check them
  return <p>Payment configured: {String(hasSecret)}</p>;  // safe output
}
```

```jsx
// app/components/ApiInfo.jsx (Client Component)
'use client';                                              // runs in the browser

export default function ApiInfo() {
  // NEXT_PUBLIC_ is replaced by the real string at build time
  const base = process.env.NEXT_PUBLIC_API_BASE;           // works in the browser
  const secret = process.env.PAYMENT_SECRET;               // undefined here: not sent to the browser
  return <p>API: {base} | secret visible: {String(Boolean(secret))}</p>; // false
}
```

## 💻 Code Example — Advanced

```jsx
// lib/env.js: validate variables once at startup so missing values fail fast
// Server-only module: importing it from a Client Component would be a bug
import 'server-only';                                      // build error if imported in client code

const required = ['DATABASE_URL', 'PAYMENT_SECRET'];       // names we must have

for (const name of required) {                             // check each one
  if (!process.env[name]) {
    throw new Error(`Missing environment variable: ${name}`); // clear error instead of a random crash later
  }
}

export const env = Object.freeze({                         // one typed place to read config
  databaseUrl: process.env.DATABASE_URL,                   // server only
  paymentSecret: process.env.PAYMENT_SECRET,               // server only
  apiBase: process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:4000', // public with fallback
});
```

```jsx
// app/actions.js: Server Action uses the secret safely
'use server';                                              // runs only on the server
import { env } from '@/lib/env';                           // server-only config

export async function createOrder(formData) {
  const itemId = formData.get('itemId');                   // data from the form
  const res = await fetch('https://payments.example.com/charge', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.paymentSecret}` }, // secret stays on the server
    body: JSON.stringify({ itemId }),                      // send only what is needed
  });
  if (!res.ok) throw new Error('Payment failed');          // surface failure to the caller
  return res.json();                                       // return a plain object
}
```

---

## 🟠 Next.js Connection
Environment variables are a Next.js (and general Node) feature rather than a React one. Key points:

```jsx
// next.config.js: you can also expose values here (they are inlined at build time)
module.exports = {
  env: { APP_VERSION: process.env.npm_package_version },  // available as process.env.APP_VERSION in code
};

// Dynamic access does NOT work for client variables:
// const key = 'NEXT_PUBLIC_API_BASE';
// process.env[key]            // undefined in the browser (not inlined)
// process.env.NEXT_PUBLIC_API_BASE  // works, because Next.js replaces this exact text
```

- `.env*.local` files are meant to stay out of Git; `.env` can hold safe defaults (no secrets).
- `NEXT_PUBLIC_` values are frozen at build time. A Docker image built once and promoted from staging to production keeps the staging value unless you rebuild or load config at runtime from a server endpoint.
- Newer Next.js versions also support reading server variables at runtime in dynamic routes; for exact behavior check docs of your version (version-dependent).
- Next.js loads `.env` files by itself; `dotenv` is not needed in the app (but scripts outside Next.js, like migration scripts, may need it).

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting a secret in a `NEXT_PUBLIC_` variable
✅ **Correct:** Keep secrets without the prefix and use them only on the server

```jsx
// Wrong: anyone can read this in the browser's JS bundle
// NEXT_PUBLIC_DB_PASSWORD=hunter2
// Right: DB_PASSWORD=hunter2   (no prefix, read only in server code)
```

❌ **Mistake 2:** Expecting a changed `NEXT_PUBLIC_` value to apply without rebuilding
✅ **Correct:** Rebuild after changing it, or serve runtime config from an API

```jsx
// Wrong: change NEXT_PUBLIC_API_BASE in the dashboard and only restart the server
// Right: trigger a new build/deploy so the new value is inlined into the bundle
```

❌ **Mistake 3:** Reading variables dynamically in client code, or committing `.env.local`
✅ **Correct:** Use the full literal name, and add `.env*.local` to `.gitignore`

```jsx
// Wrong
const k = process.env[`NEXT_PUBLIC_${name}`];   // undefined in the browser
// Right
const k = process.env.NEXT_PUBLIC_API_BASE;     // literal name, inlined by the build
```

---

## 🧠 Tricky Interview Question

```jsx
// .env.local:  API_KEY=abc123

'use client';
export default function Widget() {
  console.log(process.env.API_KEY);          // what prints?
  return <p>{String(process.env.API_KEY)}</p>;
}
```
**Answer:** It prints `undefined` in the browser and the page shows `undefined`. `API_KEY` has no `NEXT_PUBLIC_` prefix, so Next.js does not inline it into client JavaScript. This is a safety feature: a secret never leaks by accident. During server-side rendering of this Client Component the value may exist in Node, which can cause confusing differences between server and browser output (a hydration mismatch). The fix is to read the secret in a Server Component or route handler and pass only the needed safe result as props.

---

## ⚫ Interview Questions + Answers

Q1: Which environment variables are available in the browser in Next.js?
A1: Only those whose names start with `NEXT_PUBLIC_`. Next.js replaces them with their string values at build time. All other variables exist only on the server.

Q2: What is the order of `.env` files?
A2: Real environment variables win first. Then `.env.$(NODE_ENV).local`, `.env.local` (skipped when `NODE_ENV` is `test`), `.env.$(NODE_ENV)`, and finally `.env`. The first place a variable is found is used.

Q3: Why can `NEXT_PUBLIC_` values be wrong after you change them in the dashboard?
A3: They are inlined into the JavaScript during `next build`. Changing the dashboard value does not change the already built bundle, so a new build is required.

Q4: How do you keep secrets safe in a Next.js app?
A4: Never use the `NEXT_PUBLIC_` prefix for them, read them only in Server Components, route handlers or Server Actions, store them in the hosting platform's secret store, do not commit `.env.local`, and import `server-only` in modules that handle secrets so a client import fails the build.

Q5: How do you use different settings for staging and production?
A5: Set different values for the same variable names in each environment (Vercel has Development, Preview and Production scopes), or use `.env.production` for non-secret defaults. The code stays identical.

---

## 🔷 When to Use + When Not to Use
✅ **Use environment variables when:**
- A value changes by environment (API URLs, feature flags, test vs live keys)
- A value is secret (database password, API secret, signing keys)

❌ **Avoid when:**
- The value is a normal constant that never changes (use a plain constant in code)
- You need to change a value per user at runtime (use a database or config service, not env)
- You are tempted to store large JSON blobs or many secrets (use a secrets manager such as AWS Secrets Manager)

---

## 📊 Visual Diagram

```
  .env.local / dashboard
  ┌─────────────────────────────────────────┐
  │ DATABASE_URL=...        (no prefix)     │──► Server only: Server Components,
  │ PAYMENT_SECRET=...      (no prefix)     │    route handlers, Server Actions
  │ NEXT_PUBLIC_API_BASE=.. (public prefix) │──► Server AND browser
  └─────────────────────────────────────────┘      (inlined into JS at BUILD time)

   next build:   process.env.NEXT_PUBLIC_API_BASE  ──►  "https://api.example.com"  (text replaced)
   Browser sees: fetch("https://api.example.com/...")      secrets: NOT in the bundle
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment variable | Setting stored outside code | Code के बाहर रखी गई setting |
| `.env.local` | Local file with private values, not committed | Local private values की file, commit नहीं होती |
| `NEXT_PUBLIC_` | Prefix that exposes a variable to the browser | Variable को browser में खोलने वाला prefix |
| Inlining | Replacing a variable with its value at build time | Build के समय variable की जगह value भर देना |
| Secret | Private value like a password or key | निजी value जैसे password या key |
| `server-only` | Package that blocks client imports of a module | Client में import रोकने वाला package |
| Build time vs runtime | When the value is fixed: at build or when running | Value कब तय होती है: build पर या चलते समय |
| Secrets manager | Service that stores secrets safely | Secrets सुरक्षित रखने वाली service |

---

## ⚡ 3-Line Summary
**English:**
1. Environment variables keep config and secrets out of code; `.env.local` and the platform dashboard supply them.
2. Without a prefix a variable stays on the server; with `NEXT_PUBLIC_` it is inlined into browser JavaScript at build time.
3. Never put secrets in public variables, validate required variables at startup, and rebuild after changing public ones.

**Hindi:**
1. Environment variables config और secrets को code से बाहर रखते हैं; `.env.local` और platform dashboard इन्हें देते हैं।
2. Prefix के बिना variable server पर रहता है; `NEXT_PUBLIC_` के साथ वह build के समय browser JavaScript में भर दिया जाता है।
3. Secrets को कभी public variables में मत रखो, ज़रूरी variables को startup पर check करो, और public values बदलने पर rebuild करो।

---

## ➡️ Next Topic
**190. Next.js Caching Strategies** — अब production में app तेज़ और सस्ता कैसे चले: fetch cache, Full Route Cache, Router Cache और revalidation को एक साथ समझेंगे।
