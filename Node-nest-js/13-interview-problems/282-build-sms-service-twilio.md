# 282. Build SMS Service (Twilio)
# हिंदी में: Twilio से SMS Service बनाना

---

## 🔵 Simple Definition (English)
A Twilio-based SMS service sends text messages (OTPs, delivery alerts, order updates) from your Node.js app via Twilio's API, which handles the actual carrier-network delivery. A production-grade service wraps the Twilio SDK with OTP generation/verification, retry logic, and delivery-status tracking via webhooks.

## 🔵 सरल परिभाषा (Hindi)
Twilio-based SMS service आपके Node.js app से text messages (OTPs, delivery alerts, order updates) भेजती है Twilio API के through, जो actual carrier-network delivery handle करता है। Production-grade service Twilio SDK को OTP generation/verification, retry logic, और webhooks से delivery-status tracking के साथ wrap करती है।

---

## 🔴 Problem it Solves
Sending SMS directly requires integration with telecom carriers in every country you operate in — hugely complex and impractical for most companies. Twilio (and similar providers like MSG91, AWS SNS) abstracts this: one unified API sends messages globally, handling carrier routing, number formatting, and delivery retries internally. On the app side, the remaining problems are: generating and verifying OTPs securely, handling Twilio API failures/rate limits gracefully, and not blocking user-facing flows (login, checkout) on SMS delivery latency.

## 🔴 यह क्यों बना? (Hindi)
Direct SMS भेजने के लिए हर देश के telecom carriers से integration चाहिए — ज़्यादातर companies के लिए impractical। Twilio (और MSG91, AWS SNS जैसे providers) ये abstract करते हैं: एक unified API globally messages भेजती है, carrier routing, number formatting, delivery retries internally handle करती है। App side पर बचे काम: OTPs securely generate/verify करना, Twilio API failures gracefully handle करना, user-facing flows को SMS latency पर block न करना।

---

## 🟢 How it Works — Step by Step

Step 1 → Sign up for Twilio, get `accountSid`, `authToken`, and a Twilio phone number (or use a messaging service SID for better deliverability/routing).
Step 2 → Install `twilio` SDK, initialize the client with credentials (from env vars, never hardcoded).
Step 3 → For OTP flows: generate a random N-digit code, store it (with expiry, e.g. 5 minutes) keyed by phone number — in Redis for fast, auto-expiring storage.
Step 4 → Send the OTP via `client.messages.create({ body, from, to })`.
Step 5 → On verification, compare the user-submitted code against the stored one; invalidate it after use (single-use) or after N failed attempts (prevent brute-force guessing of a 4-6 digit code).
Step 6 → Handle Twilio errors distinctly: invalid phone number format, unreachable carrier, rate limit exceeded — each needs different user-facing messaging.
Step 7 → Use Twilio's **status callback webhook** to track delivery status (`queued → sent → delivered` or `failed`) asynchronously, useful for critical alerts where you need delivery confirmation.
Step 8 → Rate-limit OTP requests per phone number (e.g. max 3 per 10 minutes) to prevent SMS-bombing abuse (which also costs real money per message).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Twilio account बनाओ, credentials और phone number लो।
Step 2 → `twilio` SDK install/initialize करो env vars से।
Step 3 → OTP flows के लिए random N-digit code generate करो, Redis में expiry के साथ store करो।
Step 4 → `client.messages.create()` से OTP भेजो।
Step 5 → Verification पर submitted code compare करो, use के बाद invalidate करो या failed attempts पर।
Step 6 → Twilio errors अलग से handle करो।
Step 7 → **Status callback webhook** से delivery status track करो।
Step 8 → Phone number के हिसाब से OTP requests rate-limit करो abuse रोकने के लिए।

---

## 🟡 Real World Example
**Paytm's** login flow sends OTP via Twilio (and backup providers for redundancy/cost optimization) — the OTP is a 6-digit code stored in Redis with a 5-minute TTL, keyed by `otp:<phoneNumber>`. The send endpoint is rate-limited to 3 requests per phone number per 10 minutes to prevent SMS-pumping fraud (where attackers trigger thousands of OTP sends to a victim's number, running up the company's Twilio bill — a real and costly attack vector). Verification allows only 5 attempts before the OTP is invalidated entirely, forcing a fresh request.

## 🟡 Real Example Hindi mein
**Paytm** का login flow Twilio से OTP भेजता है (और backup providers redundancy/cost के लिए) — 6-digit code Redis में 5-minute TTL के साथ store होता है। Send endpoint हर phone number पर 10 मिनट में 3 requests तक rate-limited है SMS-pumping fraud रोकने के लिए (attackers हज़ारों OTP sends trigger करके company का Twilio bill बढ़ा सकते हैं)। Verification सिर्फ 5 attempts allow करता है।

---

## 💻 Code Example — Basic

```javascript
// basic-sms.js — minimal Twilio send
// npm install twilio
// Run: TWILIO_SID=xxx TWILIO_TOKEN=xxx TWILIO_PHONE=+1xxx node basic-sms.js

const twilio = require('twilio');

const client = twilio(process.env.TWILIO_SID, process.env.TWILIO_TOKEN);

async function sendSMS(to, body) {
  try {
    const message = await client.messages.create({
      body,
      from: process.env.TWILIO_PHONE, // your Twilio number
      to,                              // recipient, E.164 format: +91XXXXXXXXXX
    });
    console.log(`Message sent: ${message.sid}, status: ${message.status}`);
    return message;
  } catch (err) {
    // Twilio errors have a `code` — e.g. 21211 = invalid 'To' number
    console.error(`SMS send failed [${err.code}]:`, err.message);
    throw err;
  }
}

sendSMS('+911234567890', 'Your OTP is 482913. Valid for 5 minutes.');
```

## 💻 Code Example — Advanced

```javascript
// advanced-otp-service.js — OTP generation, Redis storage, rate limiting, verification
// npm install twilio redis

const twilio = require('twilio');
const { createClient } = require('redis');

class OtpService {
  constructor({ twilioSid, twilioToken, twilioPhone, redisUrl }) {
    this.client = twilio(twilioSid, twilioToken);
    this.fromNumber = twilioPhone;
    this.redis = createClient({ url: redisUrl });
  }

  async connect() {
    await this.redis.connect();
  }

  generateOtp() {
    return String(Math.floor(100000 + Math.random() * 900000)); // 6-digit code
  }

  async requestOtp(phoneNumber) {
    // ─── Rate limit: max 3 OTP requests per phone per 10 minutes ───────────
    const rateLimitKey = `otp-rate:${phoneNumber}`;
    const requestCount = await this.redis.incr(rateLimitKey);
    if (requestCount === 1) {
      await this.redis.expire(rateLimitKey, 600); // 10 minutes
    }
    if (requestCount > 3) {
      throw new Error('Too many OTP requests. Please try again later.');
    }

    const otp = this.generateOtp();
    const otpKey = `otp:${phoneNumber}`;

    // Store OTP + reset attempt counter, expires in 5 minutes
    await this.redis.set(otpKey, otp, { EX: 300 });
    await this.redis.del(`otp-attempts:${phoneNumber}`); // reset failed-attempt counter

    try {
      await this.client.messages.create({
        body: `Your verification code is ${otp}. Valid for 5 minutes. Do not share this code.`,
        from: this.fromNumber,
        to: phoneNumber,
        statusCallback: 'https://yourapp.com/webhooks/sms-status', // async delivery tracking
      });
      return { success: true, message: 'OTP sent' };
    } catch (err) {
      await this.redis.del(otpKey); // don't leave a dangling OTP if sending failed
      throw new Error(`Failed to send OTP: ${err.message}`);
    }
  }

  async verifyOtp(phoneNumber, submittedOtp) {
    const otpKey = `otp:${phoneNumber}`;
    const attemptsKey = `otp-attempts:${phoneNumber}`;

    const storedOtp = await this.redis.get(otpKey);
    if (!storedOtp) {
      return { success: false, error: 'OTP expired or not requested' };
    }

    // ─── Limit verification attempts to prevent brute-forcing a 6-digit code ─
    const attempts = await this.redis.incr(attemptsKey);
    await this.redis.expire(attemptsKey, 300);
    if (attempts > 5) {
      await this.redis.del(otpKey); // invalidate after too many wrong guesses
      return { success: false, error: 'Too many failed attempts. Request a new OTP.' };
    }

    if (submittedOtp !== storedOtp) {
      return { success: false, error: 'Invalid OTP', attemptsRemaining: 5 - attempts };
    }

    // Success — invalidate immediately (single-use)
    await this.redis.del(otpKey);
    await this.redis.del(attemptsKey);
    return { success: true };
  }
}

module.exports = OtpService;
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const OtpService = require('./advanced-otp-service');

const app = express();
app.use(express.json());

const otpService = new OtpService({
  twilioSid: process.env.TWILIO_SID,
  twilioToken: process.env.TWILIO_TOKEN,
  twilioPhone: process.env.TWILIO_PHONE,
  redisUrl: process.env.REDIS_URL,
});
otpService.connect();

app.post('/auth/request-otp', async (req, res) => {
  const { phoneNumber } = req.body;
  if (!/^\+[1-9]\d{9,14}$/.test(phoneNumber)) { // basic E.164 format check
    return res.status(400).json({ error: 'Invalid phone number format' });
  }
  try {
    await otpService.requestOtp(phoneNumber);
    res.json({ message: 'OTP sent successfully' });
  } catch (err) {
    res.status(429).json({ error: err.message });
  }
});

app.post('/auth/verify-otp', async (req, res) => {
  const { phoneNumber, otp } = req.body;
  const result = await otpService.verifyOtp(phoneNumber, otp);
  if (!result.success) return res.status(400).json(result);
  // ... issue JWT access token here on success ...
  res.json({ message: 'Phone verified', success: true });
});

// Twilio calls this asynchronously as the message moves through delivery states
app.post('/webhooks/sms-status', express.urlencoded({ extended: false }), (req, res) => {
  console.log(`Message ${req.body.MessageSid} status: ${req.body.MessageStatus}`);
  res.status(200).end();
});

app.listen(3000, () => console.log('OTP service on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No rate limiting on OTP requests, enabling SMS-pumping fraud
✅ Correct: Rate-limit OTP sends per phone number AND per IP — unrestricted endpoints are routinely abused to drain a company's Twilio balance by triggering mass sends to premium-rate numbers.

```javascript
// Wrong: anyone can POST any phone number repeatedly, racking up real SMS costs
app.post('/send-otp', (req, res) => { sendOtp(req.body.phoneNumber); });

// Right: rate-limited per phone and per IP (as shown in advanced example)
```

❌ Mistake 2: Comparing OTPs without a limit on verification attempts
✅ Correct: A 6-digit OTP has only 1,000,000 combinations — without an attempt limit, brute-forcing it within the 5-minute validity window is feasible with automated requests; always cap attempts (e.g. 5) and invalidate after exceeding.

```javascript
// Wrong: unlimited verification attempts
if (submittedOtp === storedOtp) { /* success */ }

// Right: track and limit attempts (see advanced example's otp-attempts counter)
```

---

## 🧠 Tricky Interview Question

```javascript
// What's wrong with storing the OTP comparison result this way?
const storedOtp = await redis.get(`otp:${phone}`);
if (submittedOtp == storedOtp) { // note: == not ===
  // verification passes
}
```
Answer: Beyond the `==` vs `===` type-coercion sloppiness (minor here since both are strings from Redis), the REAL issue is using a NON-constant-time string comparison for a secret value. While less critical for a short-lived 6-digit OTP compared to, say, comparing cryptographic signatures, the broader interview point is: whenever comparing a secret (API keys, tokens, OTPs) against user input, prefer timing-safe comparison (`crypto.timingSafeEqual`) for genuinely sensitive values, since naive string comparison can theoretically leak information via response-time differences (how many leading characters matched before the comparison short-circuited). For OTPs specifically, the attempt-limiting (max 5 tries) is a FAR more practical defense than timing-safety, since the search space (1 million combos) makes timing attacks impractical anyway — this question tests whether you understand WHICH mitigation matters most for which threat.

---

## ⚫ Interview Questions + Answers

Q1: Why use Redis instead of a regular database table for storing OTPs?
A1: OTPs are short-lived (minutes) by design — Redis's native `EX` (expiry) support handles automatic cleanup without needing a cron job to purge old rows, and Redis's sub-millisecond read/write latency matters for a flow that's in the user's critical login/verification path. A regular DB table would work but requires manual TTL management and adds unnecessary latency for a transient value.

Q2: What is "SMS pumping fraud" and how do you defend against it?
A2: SMS pumping (also called "toll fraud") is when attackers exploit an open OTP-send endpoint to trigger massive volumes of SMS to premium-rate or attacker-controlled numbers, the attacker profiting from a revenue-share with the receiving carrier while the victim company pays Twilio per message — costing real money with no legitimate traffic involved. Defenses: rate limiting per phone number AND per IP/session, CAPTCHA before allowing an OTP request, geographic/carrier anomaly detection (Twilio offers fraud-guard features), and monitoring for unusual spikes in OTP-send volume.

Q3: How would you design the system to work even if Twilio itself is down (multi-provider fallback)?
A3: Abstract the SMS-sending logic behind an interface (`sendSms(to, body)`) with multiple provider implementations (Twilio, MSG91, AWS SNS). On failure from the primary provider, fall back to a secondary. This also helps with COST optimization — route different countries/volumes to whichever provider is cheapest/most reliable for that corridor, a common practice at scale (Paytm-scale companies often use 2-3 SMS providers simultaneously).

Q4: Should the OTP verification endpoint also check the rate-limit or just the OTP endpoint?
A4: Both. The send endpoint's rate limit prevents send-flooding (cost/fraud). A SEPARATE attempt-limit on the VERIFY endpoint (as in the advanced example's `otp-attempts` key) prevents brute-forcing the OTP value itself once it's been sent — these are two distinct attack surfaces requiring two distinct protections, and interviewers often check if candidates conflate them into a single rate limit.

Q5: What status callback information does Twilio provide, and why would a Node app care about asynchronous delivery status after already getting a response from `messages.create()`?
A5: `messages.create()` returns almost immediately with the message queued for sending (status `queued` or `sent`) — it does NOT confirm actual delivery to the recipient's device. Twilio's status callback webhook later reports `delivered`, `undelivered`, or `failed` as the message progresses through the carrier network, sometimes seconds to minutes later. For critical flows (e.g. confirming a payment alert actually reached the user), tracking the final delivery status via webhook — not just the initial API response — matters for accurate monitoring/alerting and potentially triggering a fallback (e.g. an email) if SMS delivery ultimately fails.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Phone-number verification (OTP login/signup), delivery alerts, critical time-sensitive notifications
- You need guaranteed-ish, carrier-routed delivery independent of app installation (unlike push notifications, which require the app to be installed)

❌ Avoid when:
- The user already has your app installed and push notifications would be cheaper/sufficient — SMS costs real money per message, push notifications are essentially free
- Non-critical informational updates where email suffices — reserve SMS for time-sensitive/high-importance messages given its cost

---

## 📊 Visual Diagram
```
OTP REQUEST FLOW
─────────────────
Client               Server                    Redis              Twilio
  │ POST /request-otp   │                         │                  │
  │ ────────────────────►│  rate-limit check       │                  │
  │                       │ ───────────────────────►│                  │
  │                       │  generate OTP, SET+EX    │                  │
  │                       │ ───────────────────────►│                  │
  │                       │  send SMS                 │                  │
  │                       │ ─────────────────────────────────────────►│
  │ ◄────────────────────│  "OTP sent"                                │
  │                       │                                              │
  │                       │ ◄────────── status callback (async) ───────│
  │                       │  update delivery status log                 │

VERIFY FLOW
────────────
  │ POST /verify-otp { otp } │
  │ ─────────────────────────►│  GET otp:phone, check attempts
  │                            │ ──────────────────────► Redis
  │ ◄──────────────────────── │  match → DEL keys, success
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OTP | One-Time Password, short-lived verification code | Short-lived verification code |
| E.164 | International phone number format (+countrycode...) | International phone number format |
| Status Callback | Webhook reporting async delivery status | Async delivery status बताने वाला webhook |
| SMS Pumping | Fraud exploiting open SMS endpoints for profit | Open SMS endpoints का fraud exploitation |
| Rate Limiting | Capping requests per identity in a time window | Time window में identity के हिसाब से requests cap करना |
| Single-use | Value invalidated immediately after successful use | Successful use के बाद immediately invalid |

---

## ⚡ 3-Line Summary
English: 1. Twilio abstracts carrier-network SMS delivery behind one API; production OTP flows store codes in Redis with TTL for auto-expiry. 2. Rate-limit both OTP sends (anti-fraud, cost control) and verification attempts (anti-brute-force) as two separate protections. 3. Track async delivery status via Twilio's status callback webhook rather than assuming the initial API response means the message was actually delivered.
Hindi: 1. Twilio carrier-network SMS delivery को एक API के पीछे abstract करता है; production OTP flows Redis में TTL के साथ codes store करते हैं। 2. OTP sends (anti-fraud) और verification attempts (anti-brute-force) दोनों को अलग-अलग rate-limit करो। 3. Async delivery status Twilio के status callback webhook से track करो, initial API response को final delivery मत मानो।

---

## ➡️ Next Topic
**283. Build PDF Generator** — server-side PDF generation (invoices, reports) बनाना।
