# 124. Local Strategy
# हिंदी में: Local Strategy — Username/Password Authentication

---

## 🔵 Simple Definition (English)
Passport's **Local Strategy** (`passport-local`) implements traditional username/password authentication — the user submits credentials via a form, your verify function checks them against your own database (typically comparing a hashed password with bcrypt/argon2), and Passport establishes a session on success. It's "local" because credential verification happens entirely within your own app, unlike OAuth which delegates to a third party.

## 🔵 सरल परिभाषा (Hindi)
Passport की **Local Strategy** (`passport-local`) traditional username/password authentication implement करती है — user form से credentials submit करता है, आपका verify function उन्हें आपके own database के against check करता है (typically bcrypt/argon2 से hashed password compare करके), और success पर Passport session establish करता है। ये "local" है क्योंकि credential verification पूरी तरह आपके own app के अंदर होता है, OAuth के विपरीत जो third party को delegate करता है।

---

## 🔴 Problem it Solves
Without a standardized strategy pattern, every app writes its own custom username/password verification logic from scratch each time, inconsistently integrated with session management. Passport's Local Strategy provides a consistent, battle-tested interface: you ONLY write the credential-checking logic (DB lookup + password comparison) inside a verify callback, and Passport handles extracting form fields, calling your callback at the right time, and wiring the result into `req.user`/session — consistent with however OTHER strategies (Google, GitHub) behave in the same app.

## 🔴 यह क्यों बना? (Hindi)
एक standardized strategy pattern के बिना, हर app अपनी custom username/password verification logic scratch से हर बार लिखती है, session management के साथ inconsistently integrated। Passport की Local Strategy एक consistent, battle-tested interface देती है: आप सिर्फ credential-checking logic (DB lookup + password comparison) verify callback के अंदर लिखते हो, और Passport form fields extract करना, आपके callback को सही समय पर call करना, और result को `req.user`/session में wire करना handle करता है — consistent इस बात से कि same app में अन्य strategies (Google, GitHub) कैसे behave करती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Client submits a login form with `username` (or custom field name like `email`) and `password` fields via POST request.
Step 2 → `passport.authenticate('local')` middleware intercepts the request, extracts these two fields from `req.body` by default.
Step 3 → It calls your registered verify function: `(username, password, done) => {...}` with the extracted values.
Step 4 → Inside, you look up the user by username/email in your DB, then compare the submitted password against the stored HASH (using `bcrypt.compare()` or `argon2.verify()` — never plain comparison).
Step 5 → You call `done(null, user)` on success (Passport logs the user in, establishes session via serializeUser), `done(null, false, {message})` on invalid credentials (Passport responds 401 or redirects), or `done(err)` on a genuine system error (DB connection failure, etc.).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client login form submit करता है `username` (या custom field name जैसे `email`) और `password` fields के साथ POST request से।
Step 2 → `passport.authenticate('local')` middleware request intercept करता है, by default `req.body` से ये दो fields extract करता है।
Step 3 → ये आपके registered verify function को call करता है: `(username, password, done) => {...}` extracted values के साथ।
Step 4 → अंदर, आप username/email से DB में user ढूंढते हो, फिर submitted password को stored HASH के against compare करते हो (`bcrypt.compare()` या `argon2.verify()` use करके — कभी plain comparison नहीं)।
Step 5 → Success पर `done(null, user)` call करो (Passport user को login करता है, serializeUser से session establish करता है), invalid credentials पर `done(null, false, {message})` (Passport 401 respond करता है या redirect करता है), या genuine system error पर `done(err)` (DB connection failure, etc.)।

---

## 🟡 Real World Example
**Nykaa account login:** When a customer logs in on Nykaa's website with their email and password (as opposed to using OTP or social login), the Local Strategy verify function looks up the user by email in MongoDB, then uses `bcrypt.compare(submittedPassword, user.passwordHash)`. If the user doesn't exist OR the password doesn't match, Nykaa returns the SAME generic "Invalid email or password" message in both cases — a deliberate security practice to avoid "username enumeration" (not revealing whether the email exists in their system at all, which an attacker could otherwise use to build a list of valid registered emails for further targeted attacks).

## 🟡 Real Example Hindi mein
**Nykaa account login:** जब कोई customer Nykaa की website पर अपने email और password से login करता है (OTP या social login के बदले), Local Strategy का verify function MongoDB में email से user ढूंढता है, फिर `bcrypt.compare(submittedPassword, user.passwordHash)` use करता है। अगर user exist नहीं करता OR password match नहीं करता, Nykaa दोनों cases में SAME generic "Invalid email or password" message return करता है — एक deliberate security practice "username enumeration" रोकने के लिए (ये reveal न करना कि email उनके system में exist करता है या नहीं, जिसे attacker otherwise valid registered emails की list बनाने के लिए use कर सकता है further targeted attacks के लिए)।

---

## 💻 Code Example — Basic

```javascript
// local-strategy-basic.js
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy; // npm install passport-local
const bcrypt = require('bcrypt');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(session({ secret: 'secret', resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// Mock user with a pre-hashed password (in real apps, generated during registration)
const users = [{ id: 1, email: 'priya@example.com', passwordHash: null }];

// Pre-hash a demo password at startup (normally done once during registration)
bcrypt.hash('mySecurePass123', 10).then((hash) => { users[0].passwordHash = hash; });

// ─── CONFIGURE LocalStrategy with a custom field name ('email' instead of 'username') ──
passport.use(
  new LocalStrategy(
    { usernameField: 'email', passwordField: 'password' }, // tell Passport which req.body fields to read
    async (email, password, done) => {
      const user = users.find((u) => u.email === email);
      if (!user) return done(null, false, { message: 'Invalid email or password' }); // generic message!

      const isMatch = await bcrypt.compare(password, user.passwordHash);
      if (!isMatch) return done(null, false, { message: 'Invalid email or password' }); // SAME message

      return done(null, user); // success
    }
  )
);

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => done(null, users.find((u) => u.id === id)));

app.post('/login', passport.authenticate('local', { failureRedirect: '/login-failed' }), (req, res) => {
  res.json({ message: 'Logged in', email: req.user.email });
});

app.get('/login-failed', (req, res) => res.status(401).json({ error: 'Invalid email or password' }));

app.listen(3000, () => console.log('Local strategy server running on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// local-strategy-advanced.js — Custom callback, rate-limiting, account lockout
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const bcrypt = require('bcrypt');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(express.json());
app.use(session({ secret: process.env.SESSION_SECRET, resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// Mock DB with account lockout tracking fields
const users = [
  { id: 1, email: 'amit@example.com', passwordHash: null, failedAttempts: 0, lockedUntil: null },
];

passport.use(
  new LocalStrategy({ usernameField: 'email' }, async (email, password, done) => {
    try {
      const user = users.find((u) => u.email === email);
      if (!user) return done(null, false, { message: 'Invalid credentials' });

      // ─── ACCOUNT LOCKOUT CHECK ────────────────────────────────────────────
      if (user.lockedUntil && user.lockedUntil > Date.now()) {
        return done(null, false, { message: 'Account temporarily locked due to failed attempts' });
      }

      const isMatch = await bcrypt.compare(password, user.passwordHash);
      if (!isMatch) {
        user.failedAttempts += 1;
        if (user.failedAttempts >= 5) {
          user.lockedUntil = Date.now() + 15 * 60 * 1000; // lock for 15 minutes after 5 failures
          return done(null, false, { message: 'Too many failed attempts, account locked for 15 min' });
        }
        return done(null, false, { message: 'Invalid credentials' });
      }

      // Success: reset failure tracking
      user.failedAttempts = 0;
      user.lockedUntil = null;
      return done(null, user);
    } catch (err) {
      return done(err); // genuine system error (DB down, etc.)
    }
  })
);

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => done(null, users.find((u) => u.id === id)));

// ─── RATE-LIMITED LOGIN ROUTE + CUSTOM CALLBACK for JSON API responses ────────
const loginLimiter = rateLimit({ windowMs: 10 * 60 * 1000, max: 10 });

app.post('/login', loginLimiter, (req, res, next) => {
  // Custom callback form: manual control instead of default redirect/401 behavior
  passport.authenticate('local', (err, user, info) => {
    if (err) return next(err); // system error — pass to Express error handler
    if (!user) return res.status(401).json({ error: info?.message || 'Authentication failed' });

    req.login(user, (loginErr) => {
      // req.login() establishes the session — required when using the custom callback form
      if (loginErr) return next(loginErr);
      res.json({ message: 'Logged in successfully', email: user.email });
    });
  })(req, res, next); // note the extra invocation — custom callback form requires this
});

app.listen(3000, () => console.log('Hardened local strategy server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const bcrypt = require('bcrypt');
const app = express();

app.use(express.json());
app.use(require('express-session')({ secret: process.env.SESSION_SECRET, resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

passport.use(
  new LocalStrategy({ usernameField: 'email' }, async (email, password, done) => {
    const user = await User.findOne({ email }); // Mongoose query
    if (!user) return done(null, false, { message: 'Invalid credentials' });
    const match = await bcrypt.compare(password, user.passwordHash);
    if (!match) return done(null, false, { message: 'Invalid credentials' });
    return done(null, user);
  })
);

passport.serializeUser((user, done) => done(null, user._id));
passport.deserializeUser(async (id, done) => {
  const user = await User.findById(id).select('-passwordHash'); // never expose hash in req.user
  done(null, user);
});

app.post('/api/auth/login', passport.authenticate('local'), (req, res) => {
  res.json({ user: req.user });
});

app.listen(4000, () => console.log('API with local strategy running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Giving different error messages for "user not found" vs "wrong password"
✅ Correct: Use the SAME generic message for both failure cases — otherwise an attacker can enumerate valid email/usernames by observing which error they get.

```javascript
// Wrong — reveals whether the email exists, enabling username enumeration attacks
if (!user) return done(null, false, { message: 'No account with this email' });
if (!match) return done(null, false, { message: 'Wrong password' });

// Right — identical message regardless of WHICH check failed
if (!user) return done(null, false, { message: 'Invalid email or password' });
if (!match) return done(null, false, { message: 'Invalid email or password' });
```

❌ Mistake 2: Comparing passwords directly instead of using bcrypt/argon2 compare
✅ Correct: Passwords must NEVER be stored or compared in plain text — always store a hash and use the hashing library's compare function.

```javascript
// Wrong — plain text comparison implies plain text storage, catastrophic if DB leaks
if (user.password === password) return done(null, user);

// Right — hash comparison, plain password never persisted anywhere
const isMatch = await bcrypt.compare(password, user.passwordHash);
if (isMatch) return done(null, user);
```

---

## 🧠 Tricky Interview Question

```javascript
passport.use(new LocalStrategy(
  { usernameField: 'email' },
  async (email, password, done) => {
    const user = await User.findOne({ email });
    if (!user) return done(null, false);
    const match = await bcrypt.compare(password, user.passwordHash);
    return done(null, match ? user : false);
  }
));

app.post('/login', passport.authenticate('local'), (req, res) => {
  res.json({ success: true });
});
```
If `req.body` contains `{ username: 'test@test.com', password: 'x' }` (notice: `username`, not `email`), what happens?

Answer: The verify function receives `email` as `undefined`, because Passport's default field-reading behavior respects the `usernameField` OPTION configured (`'email'`) — it looks for `req.body.email`, not `req.body.username`, when that option is set. Since the client sent the field as `username` instead of `email`, `req.body.email` is `undefined`. `User.findOne({ email: undefined })` would either match no document (most likely, if no document literally has `email: undefined`/missing) or, in a worst-case misconfigured schema, could unexpectedly match a document lacking an `email` field at all — a subtle bug depending on your schema and DB. The verify function then proceeds with `user` being `null`/not found, correctly calling `done(null, false)`, resulting in a 401. This demonstrates the importance of exactly matching the CLIENT's form field names to the `usernameField`/`passwordField` configuration — a mismatch here is a common integration bug, not a security flaw, but it causes confusing "always fails" login behavior that's easy to miss in code review.

---

## ⚫ Interview Questions + Answers

Q1: What does `usernameField` and `passwordField` configure in `passport-local`?
A1: By default, `passport-local` expects the submitted credentials in `req.body.username` and `req.body.password`. If your form/API uses different field names (e.g., `email` instead of `username`), you must configure `new LocalStrategy({ usernameField: 'email' }, verifyCallback)` so Passport correctly extracts the right fields before passing them to your verify function.

Q2: Why should login error messages be generic ("Invalid credentials") rather than specific ("User not found" vs "Wrong password")?
A2: Specific messages enable "username/account enumeration" — an attacker submitting many email addresses and observing which specific error comes back can build a list of which emails ARE registered in your system (a privacy leak and a precursor to further targeted attacks like password spraying or phishing specifically targeted at confirmed real accounts). A generic, identical message for both failure cases prevents this information leakage.

Q3: What's the difference between using `passport.authenticate('local', options)` directly as middleware vs. using the custom callback form?
A3: Direct middleware usage (`passport.authenticate('local', { failureRedirect: '/login' })`) handles success/failure automatically with built-in behaviors (redirect, default 401, or calling `next()` on success). The custom callback form (`passport.authenticate('local', (err, user, info) => {...})(req, res, next)`) gives you FULL manual control — you decide exactly how to respond in each case (useful for JSON APIs needing custom response shapes), but you must manually call `req.login(user, callback)` yourself to establish the session on success, since the automatic behavior is bypassed.

Q4: How would you implement account lockout after repeated failed login attempts using the Local Strategy?
A4: Track failure count and a lockout timestamp per user record (in the DB). Inside the verify callback, BEFORE checking the password, check if `lockedUntil` is in the future — if so, immediately fail with a lockout message without even attempting password comparison. On a failed password check, increment the failure counter; if it crosses a threshold (e.g., 5), set `lockedUntil` to some future time (e.g., 15 minutes). On a SUCCESSFUL login, reset both the counter and lockout timestamp to zero/null.

Q5: Why is it important that `deserializeUser` excludes the password hash when reconstructing `req.user`?
A5: `req.user` is often directly exposed in API responses (`res.json({ user: req.user })`) or accessible to various parts of the app. If `deserializeUser` includes the password hash in the returned user object, there's a real risk of accidentally leaking the hash to the client in a response, or exposing it to other code paths that don't need it (increasing the attack surface if that hash were ever logged, cached, or sent somewhere unintended). Best practice: explicitly exclude sensitive fields (`.select('-passwordHash')` in Mongoose, or manually omit) when reconstructing the user object for `req.user`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building traditional username/password login alongside (or instead of) social/OAuth login options
- Need full control over credential storage and verification logic within your own database
- Want consistent integration with other Passport strategies in a multi-method auth system

❌ Avoid when:
- Your app exclusively uses third-party identity providers (Google/GitHub only, no native password accounts) — Local Strategy becomes unnecessary dead weight
- Building a stateless JWT-only API with no session requirement — a simpler custom `bcrypt.compare()` + `jwt.sign()` flow (without Passport overhead) may be more straightforward

---

## 📊 Visual Diagram
```
LOCAL STRATEGY LOGIN FLOW:

  Client POST /login { email, password }
            │
            ▼
  passport.authenticate('local')
            │
            ▼
  extract req.body[usernameField], req.body[passwordField]
            │
            ▼
  verifyCallback(email, password, done)
            │
     ┌──────┴──────────┐
  user not found    user found
     │                  │
done(null,false)   bcrypt.compare(password, hash)
     │                  │
     │           ┌──────┴──────┐
     │        no match      match
     │           │              │
     │     done(null,false) done(null, user)
     │           │              │
     ▼           ▼              ▼
   401        401        req.login(user) → session established → next()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| passport-local | Strategy for username/password auth | Username/password auth की strategy |
| usernameField | Config for custom field name | Custom field name की configuration |
| verifyCallback | Your credential-checking function | Credential-checking function |
| Account lockout | Temporary block after failed attempts | Failed attempts के बाद temporary block |
| Username enumeration | Leaking which accounts exist via errors | Errors से accounts exist होने का leak |
| req.login() | Manually establishes a Passport session | Manually Passport session establish करना |

---

## ⚡ 3-Line Summary
English:
1. Passport's Local Strategy handles username/password authentication via a verify callback you write, comparing submitted credentials against your DB using bcrypt/argon2.
2. Always use identical error messages for "user not found" and "wrong password" to prevent username enumeration attacks.
3. Add rate limiting and account lockout on top of the basic strategy for production-grade brute-force protection.

Hindi:
1. Passport की Local Strategy username/password authentication handle करती है आपके लिखे verify callback से, submitted credentials को bcrypt/argon2 use करके DB के against compare करती है।
2. "user not found" और "wrong password" के लिए हमेशा identical error messages use करो username enumeration attacks रोकने के लिए।
3. Production-grade brute-force protection के लिए basic strategy के ऊपर rate limiting और account lockout जोड़ो।

---

## ➡️ Next Topic
**125. OAuth Strategy (Google, GitHub)** — Delegating authentication to third-party identity providers।
