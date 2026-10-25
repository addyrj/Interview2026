# 281. Build Email Service (Nodemailer)
# हिंदी में: Nodemailer से Email Service बनाना

---

## 🔵 Simple Definition (English)
**Nodemailer** is the standard Node.js library for sending emails — transactional (order confirmations, password resets) or bulk — via SMTP or third-party providers (SendGrid, AWS SES). A production email service wraps Nodemailer with templates, retries, and queueing so a slow/flaky mail provider never blocks your API.

## 🔵 सरल परिभाषा (Hindi)
**Nodemailer** Node.js की standard library है emails भेजने के लिए — transactional (order confirmations, password resets) या bulk — SMTP या third-party providers (SendGrid, AWS SES) के through। Production email service Nodemailer को templates, retries, और queueing के साथ wrap करती है जिससे slow mail provider API को block न करे।

---

## 🔴 Problem it Solves
Sending email directly inside an HTTP request handler ties your API's response time to an external SMTP server's latency — if the mail provider is slow or temporarily down, your "create account" endpoint hangs or fails entirely, even though account creation itself succeeded. A proper email service decouples "accept the send request" from "actually deliver it," adds templating (so transactional emails look consistent and are easy to update), and retries transient failures without manual intervention.

## 🔴 यह क्यों बना? (Hindi)
Email directly HTTP request handler के अंदर भेजना API की response time को external SMTP server की latency से जोड़ देता है — provider slow हो या down हो तो "create account" endpoint hang हो सकता है। Proper email service "send request accept करना" को "actually deliver करना" से अलग करती है, templating add करती है, transient failures retry करती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install Nodemailer and create a **transporter** — the object configured with your SMTP provider's credentials (host, port, auth) or a service shorthand (`service: 'gmail'` for quick testing, but real production uses SendGrid/SES/Mailgun SMTP).
Step 2 → Build a **template system**: HTML templates with placeholders (Handlebars, EJS, or simple string interpolation) for things like order confirmations, so content/design is separate from sending logic.
Step 3 → Create a `sendEmail({ to, subject, template, data })` function that renders the template and calls `transporter.sendMail()`.
Step 4 → Wrap sending in a background job queue (BullMQ) so API requests don't wait for the actual SMTP round-trip.
Step 5 → Add retry logic for transient SMTP failures (connection timeout, temporary provider rate limit) with exponential backoff.
Step 6 → Verify the transporter configuration at startup (`transporter.verify()`) so misconfigured credentials fail fast at boot, not silently on the first real send attempt.
Step 7 → Track delivery status via provider webhooks (bounce, spam complaint, delivered) if the provider supports them (SendGrid/SES do) to maintain sender reputation.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Nodemailer install करो, **transporter** बनाओ — SMTP provider credentials के साथ configured object।
Step 2 → **Template system** बनाओ — HTML templates placeholders के साथ।
Step 3 → `sendEmail({ to, subject, template, data })` function बनाओ जो template render करके `sendMail()` call करे।
Step 4 → Sending को background job queue में wrap करो ताकि API wait न करे।
Step 5 → Transient SMTP failures के लिए retry logic add करो।
Step 6 → Startup पर transporter config verify करो (`transporter.verify()`)।
Step 7 → Provider webhooks से delivery status track करो (bounce, spam, delivered)।

---

## 🟡 Real World Example
**Flipkart's** order confirmation emails are sent through AWS SES via Nodemailer's SMTP transport, triggered by a BullMQ job after checkout completes. Templates are pre-rendered with Handlebars using order data (items, total, delivery estimate), and the job retries up to 3 times on transient SES throttling errors before falling back to an alert for manual review. SES bounce/complaint webhooks feed back into Flipkart's system to auto-suppress sending to permanently-bouncing addresses, protecting their sender reputation score which affects inbox placement for ALL their emails.

## 🟡 Real Example Hindi mein
**Flipkart** के order confirmation emails AWS SES के through Nodemailer SMTP transport से भेजे जाते हैं, checkout complete होने पर BullMQ job trigger करता है। Templates Handlebars से pre-rendered होते हैं, transient SES throttling errors पर 3 बार तक retry होता है। SES bounce/complaint webhooks permanently-bouncing addresses को auto-suppress करते हैं, sender reputation protect करते हैं।

---

## 💻 Code Example — Basic

```javascript
// basic-email.js — minimal Nodemailer send
// npm install nodemailer
// Run: node basic-email.js (uses Ethereal test account — safe sandbox, no real emails sent)

const nodemailer = require('nodemailer');

async function main() {
  // Ethereal creates a disposable test SMTP account — great for demos/tests
  const testAccount = await nodemailer.createTestAccount();

  const transporter = nodemailer.createTransport({
    host: testAccount.smtp.host,
    port: testAccount.smtp.port,
    secure: testAccount.smtp.secure,
    auth: { user: testAccount.user, pass: testAccount.pass },
  });

  const info = await transporter.sendMail({
    from: '"MyApp" <noreply@myapp.com>',
    to: 'customer@example.com',
    subject: 'Welcome to MyApp!',
    text: 'Thanks for signing up.',
    html: '<b>Thanks for signing up!</b>',
  });

  console.log('Message sent:', info.messageId);
  console.log('Preview URL:', nodemailer.getTestMessageUrl(info)); // view the sent email in browser
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// advanced-email-service.js — templated, retried, production-ready wrapper
// npm install nodemailer handlebars

const nodemailer = require('nodemailer');
const handlebars = require('handlebars');

class EmailService {
  constructor(config) {
    this.transporter = nodemailer.createTransport({
      host: config.host,
      port: config.port,
      secure: config.port === 465,
      auth: { user: config.user, pass: config.pass },
      pool: true,       // reuse SMTP connections instead of opening new ones per email
      maxConnections: 5,
      rateDelta: 1000,
      rateLimit: 10,     // max 10 emails/second to this provider — avoid tripping their limits
    });

    this.templates = {
      welcome: handlebars.compile('<h1>Welcome, {{name}}!</h1><p>Your account is ready.</p>'),
      orderConfirmation: handlebars.compile(
        '<h1>Order #{{orderId}} Confirmed</h1><p>Total: ₹{{total}}</p><p>Delivery by {{deliveryDate}}</p>'
      ),
    };
  }

  async verifyConnection() {
    // Fail fast at startup if SMTP credentials/config are wrong
    await this.transporter.verify();
    console.log('Email service: SMTP connection verified');
  }

  async send({ to, subject, template, data }, retries = 3) {
    const renderFn = this.templates[template];
    if (!renderFn) throw new Error(`Unknown template: ${template}`);

    const html = renderFn(data);

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const info = await this.transporter.sendMail({
          from: '"MyApp" <noreply@myapp.com>',
          to,
          subject,
          html,
        });
        return { success: true, messageId: info.messageId };
      } catch (err) {
        console.warn(`Email send attempt ${attempt} failed:`, err.message);
        if (attempt === retries) {
          throw new Error(`Failed to send email after ${retries} attempts: ${err.message}`);
        }
        // Exponential backoff before retrying
        await new Promise((r) => setTimeout(r, 2 ** attempt * 1000));
      }
    }
  }
}

module.exports = EmailService;

// Usage:
// const emailService = new EmailService({ host: 'smtp.sendgrid.net', port: 587, user: '...', pass: '...' });
// await emailService.verifyConnection();
// await emailService.send({
//   to: 'user@example.com',
//   subject: 'Order Confirmed',
//   template: 'orderConfirmation',
//   data: { orderId: 1001, total: 2499, deliveryDate: '26 Oct' },
// });
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { Queue } = require('bullmq');
const EmailService = require('./advanced-email-service');

const app = express();
app.use(express.json());

const emailQueue = new Queue('emails', { connection: { host: '127.0.0.1', port: 6379 } });

app.post('/api/signup', async (req, res) => {
  const { name, email } = req.body;
  // ... create user in DB ...

  // Don't block signup response on email delivery — enqueue it
  await emailQueue.add('welcome-email', { to: email, name });

  res.status(201).json({ message: 'Account created' });
});

// worker.js (separate process):
// const worker = new Worker('emails', async (job) => {
//   const emailService = new EmailService({ ...smtpConfig });
//   await emailService.send({
//     to: job.data.to,
//     subject: 'Welcome!',
//     template: 'welcome',
//     data: { name: job.data.name },
//   });
// }, { connection });

app.listen(3000, () => console.log('Signup API on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending emails synchronously inside the request handler
✅ Correct: Enqueue to a background job (BullMQ) so a slow mail provider never delays the HTTP response.

```javascript
// Wrong: signup response waits for the SMTP round-trip
app.post('/signup', async (req, res) => {
  await createUser(req.body);
  await transporter.sendMail({ ... }); // blocks response, fails signup if SMTP is down
  res.status(201).json({ message: 'done' });
});

// Right: enqueue, respond immediately
app.post('/signup', async (req, res) => {
  await createUser(req.body);
  await emailQueue.add('welcome-email', { email: req.body.email });
  res.status(201).json({ message: 'done' });
});
```

❌ Mistake 2: Not setting a rate limit on the transporter, tripping the provider's abuse detection
✅ Correct: Configure `rateLimit`/`rateDelta` (or the provider's documented limits) — sending too fast can get your sending IP/domain throttled or flagged as spam.

```javascript
// Wrong: no rate limiting, bulk-sends 10,000 emails as fast as possible
for (const user of allUsers) { await transporter.sendMail({ to: user.email, ... }); }

// Right: rate-limited transporter + queue-based throttled processing
const transporter = nodemailer.createTransport({ ...config, rateLimit: 10, rateDelta: 1000 });
```

---

## 🧠 Tricky Interview Question

```javascript
// Why might this "welcome email" be sent TWICE to the same user?
app.post('/signup', async (req, res) => {
  await createUser(req.body);
  await emailQueue.add('welcome-email', { email: req.body.email }); // no jobId specified
  res.status(201).json({ message: 'done' });
});
// Client's network is flaky — the signup request times out on their end,
// so their app retries the SAME signup POST a few seconds later.
```
Answer: Without idempotency protection, a client-side retry of the signup request re-runs the whole handler — if `createUser` doesn't reject duplicate signups cleanly (or the retry happens before the first request's response even returns), the welcome email gets enqueued and sent TWICE. The fix spans two layers: (1) the signup endpoint itself should be idempotent (check if the user already exists before creating, perhaps keyed by a client-supplied idempotency key or by unique email constraint), and (2) the job queue add can use a deterministic `jobId` (e.g. `welcome-${userId}`) so BullMQ itself de-duplicates identical enqueue attempts even if the API layer's idempotency check has a gap.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between SMTP relay (Nodemailer+SES/SendGrid SMTP) and using a provider's HTTP API directly?
A1: SMTP relay uses the standard email protocol over a persistent connection — Nodemailer's `createTransport` with SMTP settings works universally across providers with minimal code changes if you switch providers. Provider HTTP APIs (SendGrid's REST API, SES's `SendEmail` API call) offer provider-specific features (templates hosted on their side, detailed analytics, batch sending) but lock you into that provider's SDK. Many production systems use SMTP for portability and simplicity, switching to the HTTP API only when a provider-specific feature is needed.

Q2: How do you prevent your emails from landing in spam folders?
A2: Key factors: (1) **SPF/DKIM/DMARC** DNS records authenticating that your domain authorizes the sending server — without these, many inbox providers heavily penalize or reject mail. (2) Consistent sending patterns and low bounce/complaint rates (sender reputation) — hence tracking and suppressing bounced addresses. (3) Avoiding spammy content patterns (excessive caps, suspicious links). (4) Using a reputable ESP (SendGrid, SES, Mailgun) rather than a random SMTP server, since major inbox providers trust established senders more.

Q3: Why use connection pooling (`pool: true`) in the Nodemailer transporter?
A3: Without pooling, Nodemailer opens a new SMTP connection (TCP handshake + TLS negotiation + SMTP auth) for EVERY email sent — expensive overhead if sending many emails. `pool: true` with `maxConnections` reuses a small set of persistent connections across multiple sends, dramatically reducing per-email overhead for high-volume sending, while `rateLimit` prevents overwhelming the provider even with pooled connections.

Q4: How would you handle a transactional email that MUST be delivered (e.g. a password reset link) vs a promotional email that's best-effort?
A4: Transactional emails (password reset, order confirmation) warrant a higher-priority queue with more aggressive retries and alerting on final failure (a failed password-reset email directly blocks the user). Promotional/marketing emails can tolerate best-effort delivery, lower priority, and fewer retries, since occasional failures are low-stakes. In BullMQ terms: separate queues with different `attempts`/`priority` settings, or at minimum different failure-handling logic in the `failed` event listener.

Q5: What's the role of templating (Handlebars/EJS) in an email service, and what are the risks of raw string concatenation instead?
A5: Templating cleanly separates email CONTENT/DESIGN from the sending logic, letting designers/marketers update email copy without touching application code, and ensures consistent structure across all transactional emails. Raw string concatenation (`` `<h1>Hi ${userInput}</h1>` ``) risks HTML/script injection if user-supplied data (like a name field) contains malicious HTML — proper templating engines auto-escape interpolated values by default (Handlebars does `{{var}}` escaped, `{{{var}}}` unescaped), closing this injection vector unless explicitly bypassed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any transactional email need (signup confirmation, password reset, receipts, notifications)
- You control the SMTP/provider credentials and need fine-grained templating/retry control

❌ Avoid when:
- Sending large marketing campaigns to big lists — dedicated ESP campaign tools (Mailchimp, SendGrid Marketing Campaigns) handle list management, unsubscribes, and analytics far better than hand-rolled Nodemailer loops
- Extremely latency-sensitive "email must arrive in under 1 second" requirements — email delivery inherently has provider-side queuing/delay outside your control

---

## 📊 Visual Diagram
```
API REQUEST                 JOB QUEUE (BullMQ)            EMAIL WORKER
────────────                ───────────────────           ───────────────────
POST /signup
   │
   ▼
createUser()
   │
   ▼
emailQueue.add('welcome', data) ──► [waiting] ◄──pull──  Worker picks up job
   │                                                            │
   ▼                                                            ▼
201 Created (fast response)                            render Handlebars template
                                                                 │
                                                                 ▼
                                                         transporter.sendMail()
                                                                 │
                                                        success ─┴─ fail (retry w/ backoff)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transporter | Nodemailer object configured with SMTP credentials | SMTP credentials वाला Nodemailer object |
| SMTP | Protocol used for sending email | Email भेजने का protocol |
| Template Engine | Renders dynamic content into HTML (Handlebars, EJS) | Dynamic content को HTML में render करता है |
| Sender Reputation | Trust score affecting inbox vs spam placement | Inbox vs spam placement तय करने वाला trust score |
| Connection Pooling | Reusing SMTP connections across sends | Sends के बीच SMTP connections reuse करना |
| Idempotency Key | Identifier preventing duplicate processing | Duplicate processing रोकने वाला identifier |

---

## ⚡ 3-Line Summary
English: 1. A production email service wraps Nodemailer with templating, connection pooling, and retries, decoupled from the request cycle via a background job queue. 2. Always enqueue email sending rather than awaiting it synchronously in an API handler. 3. Protect sender reputation with SPF/DKIM/DMARC, bounce handling, and rate-limited sending.
Hindi: 1. Production email service Nodemailer को templating, connection pooling, retries के साथ wrap करती है, background job queue से request cycle से decoupled। 2. Email sending को हमेशा enqueue करो, API handler में synchronously await मत करो। 3. SPF/DKIM/DMARC, bounce handling, rate-limited sending से sender reputation protect करो।

---

## ➡️ Next Topic
**282. Build SMS Service (Twilio)** — Twilio से SMS/OTP service बनाना, delivery tracking के साथ।
