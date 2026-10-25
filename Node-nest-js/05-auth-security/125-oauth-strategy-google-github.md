# 125. OAuth Strategy (Google, GitHub)
# हिंदी में: OAuth Strategy — Google, GitHub से Login

---

## 🔵 Simple Definition (English)
**OAuth strategies** (`passport-google-oauth20`, `passport-github2`) let users log in using their existing Google/GitHub account instead of creating a new password. Your app never sees the user's Google/GitHub password — instead, the provider authenticates the user and hands your app a token plus profile info (name, email, avatar) via a redirect-based handshake (the OAuth 2.0 Authorization Code flow).

## 🔵 सरल परिभाषा (Hindi)
**OAuth strategies** (`passport-google-oauth20`, `passport-github2`) users को उनके existing Google/GitHub account से login करने देती हैं नया password बनाने के बदले। आपका app कभी user का Google/GitHub password नहीं देखता — इसके बदले, provider user को authenticate करता है और आपके app को एक token plus profile info (name, email, avatar) देता है redirect-based handshake (OAuth 2.0 Authorization Code flow) से।

---

## 🔴 Problem it Solves
Requiring every user to create and remember yet another password increases friction (signup abandonment) and your liability (you now store and must protect another set of credentials). OAuth solves this by letting users authenticate with an identity they ALREADY trust and manage (Google/GitHub account, often already logged in on their device), delegating the actual password verification entirely to that provider — your app only needs to verify the OAuth handshake's authenticity and map the returned profile to a local user record, never touching a password at all.

## 🔴 यह क्यों बना? (Hindi)
हर user को एक और password बनाने और याद रखने की ज़रूरत देने से friction बढ़ता है (signup abandonment) और आपकी liability भी (आप अब एक और set of credentials store करते हो और protect करने होते हैं)। OAuth इसे solve करता है users को उस identity से authenticate करने देकर जो वो ALREADY trust करते हैं और manage करते हैं (Google/GitHub account, अक्सर device पर already logged in), actual password verification पूरी तरह उस provider को delegate करते हुए — आपके app को सिर्फ OAuth handshake की authenticity verify करनी होती है और returned profile को local user record से map करना होता है, password को छूना ही नहीं पड़ता।

---

## 🟢 How it Works — Step by Step

Step 1 → User clicks "Login with Google" → your app redirects them to Google's authorization URL (`passport.authenticate('google', { scope: ['profile', 'email'] })` triggers this redirect).
Step 2 → User logs into Google (if not already) and approves your app's requested permissions ("scopes") on Google's own page — your app never sees their Google credentials.
Step 3 → Google redirects the user's browser BACK to your configured `callbackURL` (e.g., `/auth/google/callback`) with an authorization CODE in the query string.
Step 4 → Passport's strategy, mounted on the callback route, exchanges this code (server-to-server, behind the scenes) for an access token and the user's profile data from Google.
Step 5 → Your verify callback `(accessToken, refreshToken, profile, done)` receives the Google profile — you look up or create a matching local user record (keyed by `profile.id`, Google's stable unique ID), then call `done(null, localUser)`, establishing a session exactly like any other Passport strategy.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User "Login with Google" click करता है → आपका app उन्हें Google के authorization URL पर redirect करता है (`passport.authenticate('google', { scope: ['profile', 'email'] })` ये redirect trigger करता है)।
Step 2 → User Google में login करता है (अगर already नहीं है) और Google के own page पर आपके app की requested permissions ("scopes") approve करता है — आपका app कभी उनके Google credentials नहीं देखता।
Step 3 → Google user के browser को आपके configured `callbackURL` पर BACK redirect करता है (जैसे `/auth/google/callback`) query string में authorization CODE के साथ।
Step 4 → Callback route पर mounted Passport की strategy इस code को (server-to-server, behind the scenes) access token और Google से user का profile data पाने के लिए exchange करती है।
Step 5 → आपका verify callback `(accessToken, refreshToken, profile, done)` Google profile receive करता है — आप matching local user record ढूंढते/बनाते हो (`profile.id` से keyed, Google का stable unique ID), फिर `done(null, localUser)` call करते हो, session establish करते हैं exactly किसी अन्य Passport strategy की तरह।

---

## 🟡 Real World Example
**Notion/Linear-style "Continue with Google" for Indian SaaS startups:** A B2B SaaS tool (common pattern for products like Zoho, Freshworks-style apps) offers "Continue with Google" as the PRIMARY signup method, since their target users (corporate employees) already have Google Workspace accounts through their employer. On first login via Google OAuth, the app auto-creates a user record using `profile.emails[0].value` and `profile.displayName`, and critically, uses the VERIFIED email domain (e.g., `@company.com`) to automatically associate the new user with the correct existing organization/workspace in a B2B multi-tenant setup — eliminating manual invite-code entry for most signups.

## 🟡 Real Example Hindi mein
**Notion/Linear-style "Continue with Google" for Indian SaaS startups:** एक B2B SaaS tool (Zoho, Freshworks-style apps जैसा common pattern) "Continue with Google" को PRIMARY signup method के रूप में offer करता है, क्योंकि उनके target users (corporate employees) के पास अपने employer के through already Google Workspace accounts होते हैं। Google OAuth से पहली बार login पर, app automatically `profile.emails[0].value` और `profile.displayName` use करके user record बनाता है, और critically, VERIFIED email domain (जैसे `@company.com`) use करके नए user को B2B multi-tenant setup में सही existing organization/workspace से automatically associate करता है — ज़्यादातर signups के लिए manual invite-code entry eliminate करता है।

---

## 💻 Code Example — Basic

```javascript
// oauth-basic.js
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy; // npm install passport-google-oauth20

const app = express();
app.use(session({ secret: 'secret', resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// Mock user database
const users = [];

passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID, // from Google Cloud Console credentials
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: 'http://localhost:3000/auth/google/callback', // must match Google Console config exactly
    },
    (accessToken, refreshToken, profile, done) => {
      // profile contains: id, displayName, emails[], photos[], etc.
      let user = users.find((u) => u.googleId === profile.id);

      if (!user) {
        // First-time login — create a new local user record
        user = {
          googleId: profile.id,
          email: profile.emails[0].value,
          name: profile.displayName,
        };
        users.push(user);
      }

      return done(null, user);
    }
  )
);

passport.serializeUser((user, done) => done(null, user.googleId));
passport.deserializeUser((id, done) => done(null, users.find((u) => u.googleId === id)));

// Step 1: redirect to Google
app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// Step 2: Google redirects back here with the auth code
app.get(
  '/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => res.redirect('/dashboard') // success — session established
);

app.get('/dashboard', (req, res) => {
  if (!req.isAuthenticated()) return res.redirect('/login');
  res.json({ message: `Welcome ${req.user.name}` });
});

app.listen(3000, () => console.log('OAuth server running on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// oauth-advanced.js — Multiple providers (Google + GitHub) + account linking
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const GitHubStrategy = require('passport-github2').Strategy; // npm install passport-github2

const app = express();
app.use(session({ secret: process.env.SESSION_SECRET, resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// Mock DB: users keyed by internal ID, with multiple linked provider identities
const users = [];
let nextId = 1;

// ─── ACCOUNT LINKING LOGIC — unify by verified email across providers ────────
function findOrCreateUser(provider, profile, done) {
  const email = profile.emails?.[0]?.value;
  if (!email) return done(new Error('Email permission required'));

  // Check if a user with this email already exists (possibly from a DIFFERENT provider)
  let user = users.find((u) => u.email === email);

  if (!user) {
    user = { id: nextId++, email, name: profile.displayName || profile.username, providers: {} };
    users.push(user);
  }

  // Link this provider's ID to the (possibly pre-existing) user account
  user.providers[provider] = profile.id;
  done(null, user);
}

passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: '/auth/google/callback',
    },
    (accessToken, refreshToken, profile, done) => findOrCreateUser('google', profile, done)
  )
);

passport.use(
  new GitHubStrategy(
    {
      clientID: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
      callbackURL: '/auth/github/callback',
      scope: ['user:email'], // GitHub requires explicit scope to return email
    },
    (accessToken, refreshToken, profile, done) => findOrCreateUser('github', profile, done)
  )
);

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => done(null, users.find((u) => u.id === id)));

// ─── ROUTES for both providers, following the same redirect/callback pattern ──
app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));
app.get('/auth/google/callback', passport.authenticate('google', { failureRedirect: '/login' }), (req, res) =>
  res.redirect('/dashboard')
);

app.get('/auth/github', passport.authenticate('github', { scope: ['user:email'] }));
app.get('/auth/github/callback', passport.authenticate('github', { failureRedirect: '/login' }), (req, res) =>
  res.redirect('/dashboard')
);

app.get('/dashboard', (req, res) => {
  if (!req.isAuthenticated()) return res.redirect('/login');
  res.json({ user: req.user, linkedProviders: Object.keys(req.user.providers) });
});

app.listen(3000, () => console.log('Multi-provider OAuth server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const app = express();

app.use(require('express-session')({ secret: process.env.SESSION_SECRET, resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: `${process.env.BASE_URL}/auth/google/callback`,
    },
    async (accessToken, refreshToken, profile, done) => {
      try {
        let user = await User.findOne({ googleId: profile.id }); // Mongoose
        if (!user) {
          user = await User.create({
            googleId: profile.id,
            email: profile.emails[0].value,
            name: profile.displayName,
          });
        }
        done(null, user);
      } catch (err) {
        done(err);
      }
    }
  )
);

const router = express.Router();
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));
router.get('/google/callback', passport.authenticate('google', { failureRedirect: '/login' }), (req, res) =>
  res.redirect('/dashboard')
);

app.use('/auth', router);
app.listen(3000, () => console.log('Production OAuth integration running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `callbackURL` mismatch between your code and the OAuth provider's console configuration
✅ Correct: The exact callback URL (protocol, domain, path) registered in Google Cloud Console / GitHub OAuth App settings must match EXACTLY what your Passport strategy config uses — even a trailing slash difference causes a `redirect_uri_mismatch` error.

```javascript
// Wrong — if Google Console has 'http://localhost:3000/auth/google/callback'
// but code uses a different path, OAuth flow fails with redirect_uri_mismatch
callbackURL: '/google/callback', // relative path might resolve differently than registered

// Right — exact match with what's registered in the provider's developer console
callbackURL: 'http://localhost:3000/auth/google/callback',
```

❌ Mistake 2: Trusting the OAuth profile's email as automatically verified without checking `profile.emails[0].verified`
✅ Correct: Some providers can return an email that technically belongs to the account but isn't necessarily verified — for critical account-linking logic (merging accounts by email), check the verification flag where the provider supplies one.

```javascript
// Wrong — blindly trusts and merges accounts by email without verification check
const user = await User.findOne({ email: profile.emails[0].value });

// Right — check verified status where available before using email for account linking decisions
if (profile.emails[0].verified === false) {
  return done(new Error('Email not verified by provider'));
}
```

---

## 🧠 Tricky Interview Question

```javascript
// User signs up via Google OAuth with email: rahul@gmail.com
// Later, the SAME person tries "Login with GitHub" using a GitHub account
// that ALSO has rahul@gmail.com as its verified email.
```
Does Passport automatically treat these as the SAME user, or does it create a duplicate account?

Answer: By default, Passport does NOT automatically merge accounts across different strategies — each strategy's verify callback runs independently, and unless YOUR code explicitly implements account-linking logic (as shown in the advanced example's `findOrCreateUser` function, which looks up existing users by EMAIL rather than provider-specific ID before creating a new one), you'd end up with TWO separate user records: one created during Google signup (keyed by `googleId`), and a second DUPLICATE created during GitHub login (keyed by `githubId`), even though both represent the same real person with the same email. This is a common real-world gotcha — "account linking" (recognizing that different OAuth providers can represent the same underlying identity via a shared verified email) is YOUR application's responsibility to implement explicitly; Passport provides the raw mechanics but no built-in identity-unification logic across strategies.

---

## ⚫ Interview Questions + Answers

Q1: What's the OAuth 2.0 "Authorization Code" flow, and why is it preferred over directly handling user passwords from third parties?
A1: The Authorization Code flow redirects the user to the PROVIDER's own login page (Google/GitHub), where they enter their credentials directly with the provider — your app never sees or handles their password at all. After approval, the provider issues a temporary authorization CODE (via redirect), which your SERVER (not the client's browser) exchanges server-to-server for an access token and profile data. This design ensures the actual access token exchange happens over a secure backend channel, and your app's only responsibility is verifying the callback and using the returned profile — a much smaller trust/security surface than if you asked users to type their Google password into your own form.

Q2: Why does `passport-github2` require an explicit `scope: ['user:email']` while some providers return email by default?
A2: GitHub's API, by default, only returns PUBLIC profile data — if a user has set their email as private in their GitHub settings, the basic profile request won't include it. Requesting the `user:email` scope explicitly asks GitHub's OAuth consent screen to grant your app permission to read the user's email addresses (including potentially private ones, if the user approves), which is often required by apps to create a complete local user record keyed by email.

Q3: What security risk does the OAuth `state` parameter protect against, and does Passport handle it automatically?
A3: The `state` parameter is a random, unguessable value your app generates before redirecting to the provider, included in the redirect URL, and verified matches when the provider redirects back — this protects against CSRF attacks on the OAuth flow itself (an attacker tricking a victim's browser into completing an OAuth flow initiated by the attacker, potentially linking the attacker's account to the victim's session). Modern versions of `passport-oauth2`-based strategies (which Google/GitHub strategies build on) handle `state` generation and verification automatically by default in recent library versions, but it's worth confirming your specific strategy version does so, especially in older codebases.

Q4: How would you let an ALREADY LOGGED-IN user link an additional OAuth provider (e.g., add Google login to an existing email/password account) rather than creating a new account?
A4: This requires distinguishing between "login via OAuth" (looking for an existing user matching the OAuth profile) and "link OAuth to current session" (associating the OAuth profile's provider ID with the user ALREADY authenticated via `req.user` in the current session) — typically implemented via a separate route (e.g., `/account/link/google`) that, instead of calling Passport's strategy in "login" mode, uses the OAuth callback to update the CURRENTLY authenticated `req.user`'s record with the new provider's ID, rather than running the normal find-or-create-new-user logic.

Q5: What happens to a user's local session if their Google account (used for OAuth login) gets suspended or deleted on Google's side AFTER they've already logged into your app?
A5: Nothing happens immediately to an ACTIVE session — your app's session (cookie + server-side session record, or JWT if used) is independent of the OAuth provider's account status once the initial login handshake completes; you're not continuously re-checking with Google during the session. The impact only surfaces on the NEXT login attempt — if the user tries to "Login with Google" again and their Google account is suspended, the OAuth flow itself would fail at Google's side (they can't even authenticate there), preventing a new session from being established, but any currently active session you've already issued remains valid until it naturally expires per your own session/token expiry rules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reducing signup friction by letting users leverage an existing trusted identity (Google, GitHub, Facebook)
- B2B SaaS tools where corporate Google Workspace/Microsoft accounts are the natural identity source
- Avoiding the liability of storing/managing passwords for users who'd rather not create another one

❌ Avoid when:
- Building apps where users may not have or want to use third-party accounts (e.g., certain regulated/government systems requiring self-contained credential management)
- Your user base skews toward contexts where social accounts aren't universally available/trusted (requires at least a Local Strategy fallback in most real products)

---

## 📊 Visual Diagram
```
OAUTH 2.0 AUTHORIZATION CODE FLOW (Google example):

  Your App                    Google                      Your App
     │                           │                            │
     │── redirect user ─────────▶│                            │
     │  (GET /auth/google)       │                            │
     │                     user logs into Google              │
     │                     user approves scopes                │
     │                           │                            │
     │◀── redirect with code ────│                            │
     │    GET /auth/google/callback?code=XYZ                  │
     │                           │                            │
     │── exchange code for ─────▶│  (server-to-server,        │
     │   access token + profile  │   client secret used here) │
     │◀── access token, profile ─│                            │
     │                           │                            │
     verifyCallback(token, profile, done)
     │
     find/create local user by profile.id
     │
     done(null, user) → session established via serializeUser
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OAuth 2.0 | Delegated authentication protocol | Delegated authentication protocol |
| Authorization Code | Temporary code exchanged for a token | Token के लिए exchange होने वाला temporary code |
| Scope | Permissions requested from the provider | Provider से requested permissions |
| callbackURL | Where the provider redirects after approval | Approval के बाद provider redirect करने वाला URL |
| Account Linking | Unifying identities across providers | Providers के across identities unify करना |
| state parameter | CSRF protection for the OAuth flow | OAuth flow की CSRF protection |

---

## ⚡ 3-Line Summary
English:
1. OAuth strategies let users log in via Google/GitHub without your app ever handling their password — the provider authenticates and hands back profile data via a redirect-based code exchange.
2. Your verify callback maps the returned profile to a local user record (find-or-create, typically keyed by provider ID or verified email).
3. Account linking across multiple providers isn't automatic — your app must explicitly implement logic to unify identities sharing the same verified email.

Hindi:
1. OAuth strategies users को Google/GitHub से login करने देती हैं बिना आपके app को उनका password handle किए — provider authenticate करता है और profile data redirect-based code exchange से वापस देता है।
2. आपका verify callback returned profile को local user record से map करता है (find-or-create, typically provider ID या verified email से keyed)।
3. Multiple providers के across account linking automatic नहीं है — same verified email share करने वाली identities को unify करने के लिए आपके app को explicitly logic implement करना होगा।

---

## ➡️ Next Topic
**126. Session Based Auth** — Deeper focus on cookie+session authentication patterns beyond token-based approaches।
