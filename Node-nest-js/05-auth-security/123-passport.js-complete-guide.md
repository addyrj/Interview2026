# 123. Passport.js — Complete Guide
# हिंदी में: Passport.js — Complete Guide

---

## 🔵 Simple Definition (English)
**Passport.js** is a flexible, modular authentication middleware for Node.js/Express. It doesn't implement authentication logic itself — instead it provides a consistent framework (`strategies`) for plugging in different authentication methods (local username/password, Google OAuth, GitHub OAuth, JWT, SAML — 500+ strategies exist), handling session serialization and the common login/logout flow uniformly.

## 🔵 सरल परिभाषा (Hindi)
**Passport.js** Node.js/Express के लिए एक flexible, modular authentication middleware है। ये खुद authentication logic implement नहीं करता — इसके बदले एक consistent framework (`strategies`) देता है अलग-अलग authentication methods plug-in करने के लिए (local username/password, Google OAuth, GitHub OAuth, JWT, SAML — 500+ strategies exist करती हैं), session serialization और common login/logout flow को uniformly handle करता है।

---

## 🔴 Problem it Solves
Every authentication method (password login, Google login, GitHub login, API key) has different verification logic, but apps often need to support MULTIPLE methods simultaneously, each integrated consistently with session management and route protection. Writing custom integration code for each provider from scratch is repetitive and error-prone. Passport.js abstracts this into a plugin ("strategy") pattern — you install a strategy package, configure it with your credentials/verify function, and Passport handles the uniform plumbing (calling your verify callback, managing `req.user`, session serialization) regardless of which strategy is active.

## 🔴 यह क्यों बना? (Hindi)
हर authentication method (password login, Google login, GitHub login, API key) की अलग verification logic होती है, पर apps को अक्सर MULTIPLE methods simultaneously support करने होते हैं, हर एक session management और route protection के साथ consistently integrated। हर provider के लिए scratch से custom integration code लिखना repetitive और error-prone है। Passport.js इसे एक plugin ("strategy") pattern में abstract करता है — आप एक strategy package install करते हो, अपने credentials/verify function से configure करते हो, और Passport uniform plumbing handle करता है (आपके verify callback को call करना, `req.user` manage करना, session serialization) चाहे कोई भी strategy active हो।

---

## 🟢 How it Works — Step by Step

Step 1 → Install and configure a strategy (e.g., `passport-local`, `passport-google-oauth20`) by calling `passport.use(new Strategy(options, verifyCallback))`.
Step 2 → The `verifyCallback` contains YOUR custom logic to check credentials (DB lookup, password compare) and calls `done(error, user)` on completion — `done(null, user)` for success, `done(null, false)` for failed auth, `done(err)` for a system error.
Step 3 → `passport.serializeUser((user, done) => done(null, user.id))` defines how to store a minimal reference to the user in the session (just the ID, not the whole object).
Step 4 → `passport.deserializeUser((id, done) => { ...lookup user by id...; done(null, user) })` defines how to reconstruct the full user object from the session's stored ID on each subsequent request.
Step 5 → `app.use(passport.initialize())` and `app.use(passport.session())` wire Passport into Express; `passport.authenticate('strategyName')` is used as route middleware to trigger authentication for specific routes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक strategy install और configure करो (जैसे `passport-local`, `passport-google-oauth20`) `passport.use(new Strategy(options, verifyCallback))` call करके।
Step 2 → `verifyCallback` में आपकी custom logic होती है credentials check करने के लिए (DB lookup, password compare) और complete होने पर `done(error, user)` call करती है — success के लिए `done(null, user)`, failed auth के लिए `done(null, false)`, system error के लिए `done(err)`।
Step 3 → `passport.serializeUser((user, done) => done(null, user.id))` define करता है कि session में user का minimal reference कैसे store करें (सिर्फ ID, पूरा object नहीं)।
Step 4 → `passport.deserializeUser((id, done) => { ...id से user lookup...; done(null, user) })` define करता है कि हर बाद की request पर session के stored ID से पूरा user object कैसे reconstruct करें।
Step 5 → `app.use(passport.initialize())` और `app.use(passport.session())` Passport को Express में wire करते हैं; `passport.authenticate('strategyName')` route middleware के रूप में use होता है specific routes के लिए authentication trigger करने के लिए।

---

## 🟡 Real World Example
**MakeMyTrip login options:** MakeMyTrip's website offers multiple login methods on the same page — email/password, Google Sign-In, Facebook Login. Behind the scenes, their Express backend configures THREE Passport strategies: `passport-local` (email/password against their user DB), `passport-google-oauth20` (delegating identity verification to Google), `passport-facebook` (delegating to Facebook). Regardless of which method a user picks, Passport's consistent `req.login()`/`req.user`/session flow means the rest of the application (booking flow, profile page, order history) doesn't need to know or care which authentication method was used — it just sees an authenticated `req.user` with a consistent shape.

## 🟡 Real Example Hindi mein
**MakeMyTrip login options:** MakeMyTrip की website एक ही page पर multiple login methods offer करती है — email/password, Google Sign-In, Facebook Login। Behind the scenes, उनका Express backend तीन Passport strategies configure करता है: `passport-local` (email/password उनके user DB के against), `passport-google-oauth20` (identity verification Google को delegate करते हुए), `passport-facebook` (Facebook को delegate करते हुए)। User कोई भी method चुने, Passport का consistent `req.login()`/`req.user`/session flow मतलब बाकी application (booking flow, profile page, order history) को जानने की ज़रूरत नहीं कि कौन सा authentication method use हुआ — उसे सिर्फ consistent shape वाला authenticated `req.user` दिखता है।

---

## 💻 Code Example — Basic

```javascript
// passport-basic.js
const express = require('express');
const session = require('express-session');
const passport = require('passport'); // npm install passport
const LocalStrategy = require('passport-local').Strategy; // npm install passport-local

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(session({ secret: 'session-secret', resave: false, saveUninitialized: false }));
app.use(passport.initialize()); // sets up Passport's machinery on req
app.use(passport.session()); // integrates Passport with express-session

// Mock user database
const users = [{ id: 1, username: 'rahul', password: 'pass123' }]; // real apps: hashed password!

// ─── CONFIGURE a Local Strategy ────────────────────────────────────────────────
passport.use(
  new LocalStrategy((username, password, done) => {
    const user = users.find((u) => u.username === username);
    if (!user) return done(null, false, { message: 'User not found' });
    if (user.password !== password) return done(null, false, { message: 'Wrong password' }); // use bcrypt.compare in real apps
    return done(null, user); // success — passes the user object forward
  })
);

// ─── SERIALIZE/DESERIALIZE for session storage ─────────────────────────────────
passport.serializeUser((user, done) => done(null, user.id)); // store only the ID in session
passport.deserializeUser((id, done) => {
  const user = users.find((u) => u.id === id);
  done(null, user); // reconstructs req.user on every request
});

// ─── LOGIN ROUTE using passport.authenticate() ────────────────────────────────
app.post('/login', passport.authenticate('local', { failureRedirect: '/login-failed' }), (req, res) => {
  res.json({ message: 'Logged in', user: req.user }); // req.user set by Passport on success
});

app.get('/login-failed', (req, res) => res.status(401).json({ error: 'Invalid credentials' }));

app.get('/profile', (req, res) => {
  if (!req.isAuthenticated()) return res.status(401).json({ error: 'Not logged in' }); // Passport helper
  res.json({ user: req.user });
});

app.listen(3000, () => console.log('Passport basic server running on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// passport-advanced.js — Multiple strategies (local + JWT) + custom middleware
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const { Strategy: JwtStrategy, ExtractJwt } = require('passport-jwt'); // npm install passport-jwt
const bcrypt = require('bcrypt');

const app = express();
app.use(express.json());
app.use(session({ secret: process.env.SESSION_SECRET || 'secret', resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// Mock DB
const users = [{ id: 1, email: 'rahul@example.com', passwordHash: null, role: 'customer' }];

// ─── 1. LOCAL STRATEGY (for login form, issues a session) ────────────────────
passport.use(
  new LocalStrategy({ usernameField: 'email' }, async (email, password, done) => {
    try {
      const user = users.find((u) => u.email === email);
      if (!user) return done(null, false, { message: 'Invalid credentials' });

      const match = await bcrypt.compare(password, user.passwordHash || '');
      if (!match) return done(null, false, { message: 'Invalid credentials' });

      return done(null, user);
    } catch (err) {
      return done(err);
    }
  })
);

// ─── 2. JWT STRATEGY (for API routes authenticated via Bearer token) ─────────
passport.use(
  new JwtStrategy(
    {
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(), // reads Authorization: Bearer <token>
      secretOrKey: process.env.JWT_SECRET || 'jwt-secret',
    },
    (payload, done) => {
      const user = users.find((u) => u.id === payload.userId);
      if (!user) return done(null, false);
      return done(null, user);
    }
  )
);

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => done(null, users.find((u) => u.id === id)));

// ─── 3. SESSION-BASED LOGIN ROUTE (for browser form login) ───────────────────
app.post('/login', passport.authenticate('local'), (req, res) => {
  res.json({ message: 'Session established', user: { id: req.user.id, email: req.user.email } });
});

// ─── 4. JWT-PROTECTED API ROUTE (for mobile/API clients) ─────────────────────
app.get(
  '/api/profile',
  passport.authenticate('jwt', { session: false }), // session: false since JWT is stateless
  (req, res) => {
    res.json({ user: req.user });
  }
);

// ─── 5. ROLE-BASED AUTHORIZATION built on top of Passport's req.user ─────────
function requireRole(role) {
  return (req, res, next) => {
    if (req.user?.role !== role) return res.status(403).json({ error: 'Forbidden' });
    next();
  };
}

app.get('/admin', passport.authenticate('jwt', { session: false }), requireRole('admin'), (req, res) => {
  res.json({ message: 'Admin area' });
});

app.listen(3000, () => console.log('Multi-strategy Passport server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const passport = require('passport');
const session = require('express-session');
const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(session({ secret: process.env.SESSION_SECRET, resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

require('./config/passport')(passport); // separate file configuring all strategies, common pattern

const router = express.Router();

router.get('/login', (req, res) => res.render('login')); // GET — render the login form
router.post(
  '/login',
  passport.authenticate('local', {
    successRedirect: '/dashboard',
    failureRedirect: '/login',
    failureFlash: true, // requires connect-flash for error messages across redirects
  })
);
router.get('/logout', (req, res) => {
  req.logout((err) => {
    // Passport's logout clears req.user and the login session
    res.redirect('/login');
  });
});

app.use('/auth', router);
app.listen(4000, () => console.log('Traditional server-rendered auth app running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `app.use(passport.session())` when using session-based strategies
✅ Correct: Without this, `passport.serializeUser`/`deserializeUser` never run, so `req.user` won't persist across requests even after a successful login — each request appears "unauthenticated."

```javascript
// Wrong — missing passport.session(), login "works" once but req.user is lost on next request
app.use(passport.initialize());

// Right — both middlewares required for persistent session-based auth
app.use(passport.initialize());
app.use(passport.session());
```

❌ Mistake 2: Using `session: true` (default) with a stateless JWT strategy
✅ Correct: JWT is inherently stateless — there's no need for Passport to manage a server-side session for JWT-authenticated requests. Omitting `{ session: false }` wastes resources trying to serialize/deserialize sessions unnecessarily.

```javascript
// Wrong — tries to create/manage a session even though JWT needs none
app.get('/api/data', passport.authenticate('jwt'), handler);

// Right — explicitly stateless for JWT strategy
app.get('/api/data', passport.authenticate('jwt', { session: false }), handler);
```

---

## 🧠 Tricky Interview Question

```javascript
passport.use(new LocalStrategy((username, password, done) => {
  const user = findUser(username);
  if (!user) return done(null, false); // user not found
  if (user.password !== password) return done(null, false); // wrong password
  return done(null, user);
}));

app.post('/login', passport.authenticate('local'), (req, res) => {
  res.json({ message: 'Success' }); // does this ever run on FAILED login?
});
```
If login fails (`done(null, false)` is called), does the route handler `(req, res) => {...}` after `passport.authenticate('local')` ever execute? What does the client receive instead?

Answer: **No**, the route handler does NOT execute on failure. When the strategy calls `done(null, false)` (indicating authentication failure, not an error), Passport's `authenticate()` middleware, by default (with no `failureRedirect` or custom callback configured), automatically sends a `401 Unauthorized` response itself and does NOT call `next()` — meaning the route handler code after it is skipped entirely. This is a common point of confusion: developers sometimes expect to handle the failure case themselves inside the route handler, but `passport.authenticate()` intercepts and handles both success (calls `next()`, letting the handler run with `req.user` set) and failure (sends 401 directly) cases itself, unless you provide a custom callback function as the SECOND argument to `authenticate()` to override this default behavior and handle both outcomes manually.

---

## ⚫ Interview Questions + Answers

Q1: What's the purpose of `serializeUser` and `deserializeUser` in Passport.js?
A1: They define how Passport persists and retrieves user identity across requests when using session-based authentication. `serializeUser(user, done)` runs ONCE after successful login, deciding what minimal data to store in the session (almost always just the user's ID, to keep the session small). `deserializeUser(id, done)` runs on EVERY subsequent request that has a valid session, taking the stored ID and looking up (usually via a DB query) the full user object, which Passport then attaches to `req.user`.

Q2: Why doesn't Passport.js implement authentication logic itself?
A2: Passport.js is intentionally a FRAMEWORK/abstraction layer, not an authentication provider — this design lets it support hundreds of different authentication methods (strategies) through a plugin architecture without needing opinions on HOW each one verifies credentials. Each strategy package (passport-local, passport-google-oauth20, passport-jwt, etc.) implements the actual protocol-specific logic (password comparison, OAuth handshake, JWT verification), while Passport provides the uniform `req.user`, session integration, and route-middleware pattern around any of them.

Q3: Can you use multiple Passport strategies in the same Express app simultaneously?
A3: Yes — this is a core strength of Passport.js. You register multiple strategies with `passport.use(new Strategy1(...))`, `passport.use(new Strategy2(...))`, each given a NAME (either explicit or default, like `'local'`, `'jwt'`, `'google'`). Different routes can then use `passport.authenticate('strategyName')` to specify which strategy applies to that specific route — e.g., a web login form route uses `'local'`, while an API route uses `'jwt'`.

Q4: What's the difference between `passport.authenticate()`'s `failureRedirect` option and providing a custom callback?
A4: `failureRedirect: '/login'` is a simple built-in option that automatically redirects the browser to a given URL on authentication failure (common for traditional server-rendered apps with HTML forms). A custom callback — `passport.authenticate('local', (err, user, info) => {...})` used as a wrapping function rather than direct middleware — gives you full manual control to inspect WHY authentication failed (`info.message`) and decide exactly how to respond (e.g., returning a specific JSON error for an API, rather than an HTML redirect).

Q5: How would you integrate Passport's Google OAuth strategy and what callback mechanics are involved?
A5: Install `passport-google-oauth20`, configure it with `clientID`, `clientSecret`, and `callbackURL` (a route on your server Google redirects back to after the user approves access). The strategy's verify callback receives `(accessToken, refreshToken, profile, done)` where `profile` contains the user's Google identity info — you typically look up or create a corresponding user record in your own DB keyed by `profile.id` (Google's unique user ID), then call `done(null, localUser)`. Two routes are needed: one that redirects to Google (`passport.authenticate('google', { scope: ['profile', 'email'] })`), and the callback route (`/auth/google/callback`) that Google redirects to, which also uses `passport.authenticate('google')` to complete the flow and establish the session.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Supporting multiple authentication methods (local + social logins) in the same app with consistent session/user handling
- Building traditional server-rendered apps needing session-based login flows out of the box
- Wanting a well-tested, widely-adopted ecosystem of pre-built strategies instead of hand-rolling OAuth/JWT integration

❌ Avoid when:
- Building a simple, single-method stateless JWT API where Passport's abstraction overhead (strategies, serialization) adds little value over directly writing a small `jwt.verify()` middleware
- Projects wanting fine-grained control without an abstraction layer, or using newer alternatives (Auth.js/NextAuth, Lucia) that some teams find more modern/lightweight for specific frameworks

---

## 📊 Visual Diagram
```
PASSPORT.JS ARCHITECTURE:

  Express App
     │
     ├── passport.initialize()  ◀── sets up req.login(), req.logout(), req.isAuthenticated()
     ├── passport.session()     ◀── hooks into express-session for persistence
     │
     ├── passport.use(LocalStrategy)   ──┐
     ├── passport.use(GoogleStrategy)  ──┼──▶ pluggable strategies, each with own verify logic
     ├── passport.use(JwtStrategy)     ──┘
     │
     ├── passport.serializeUser   ──▶ user object → minimal session data (ID)
     ├── passport.deserializeUser ──▶ session data (ID) → full user object → req.user
     │
     ▼
  Route: passport.authenticate('local') ──▶ runs verify callback ──▶ done(err, user)
                                                  │
                                    success: req.login(user), next()
                                    failure: 401 or failureRedirect
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Strategy | Pluggable auth method implementation | Pluggable auth method implementation |
| verifyCallback | Your custom credential-checking function | Custom credential-checking function |
| serializeUser | Defines session storage format | Session storage format define करना |
| deserializeUser | Reconstructs user from session data | Session data से user reconstruct करना |
| req.isAuthenticated() | Checks if a session is logged in | Session logged in है या नहीं check करना |
| req.login() / req.logout() | Establishes/clears a Passport session | Passport session set/clear करना |

---

## ⚡ 3-Line Summary
English:
1. Passport.js is a pluggable authentication middleware — strategies implement provider-specific logic, Passport handles uniform session/user plumbing.
2. Configure `serializeUser`/`deserializeUser` for session persistence, and use `session: false` for stateless strategies like JWT.
3. Multiple strategies can coexist in one app, letting you support local login, social OAuth, and API token auth consistently via `req.user`.

Hindi:
1. Passport.js एक pluggable authentication middleware है — strategies provider-specific logic implement करती हैं, Passport uniform session/user plumbing handle करता है।
2. Session persistence के लिए `serializeUser`/`deserializeUser` configure करो, और JWT जैसी stateless strategies के लिए `session: false` use करो।
3. एक app में multiple strategies coexist कर सकती हैं, local login, social OAuth, और API token auth को `req.user` से consistently support करने देती हैं।

---

## ➡️ Next Topic
**124. Local Strategy** — Deep dive into Passport's username/password authentication strategy।
