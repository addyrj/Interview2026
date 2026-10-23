# 56. OpenID Connect (OIDC)
# हिंदी में: OpenID Connect — OAuth 2.0 के ऊपर बनी पहचान (identity) की परत, जो "ID token" से ऐप को बताती है कि login करने वाला यूज़र कौन है

---

## 🔵 Simple Definition (English)
**OpenID Connect (OIDC)** is an **authentication layer on top of OAuth 2.0**. Along with the access token, the authorization server (now called the **OpenID Provider**, e.g. Google, Microsoft, Okta, Auth0, Keycloak) returns an **ID token**: a **signed JWT** stating **who the user is** (`sub`, `email`, `name`), **who issued it** (`iss`), **for which app** (`aud`), and **when** they logged in.
It also standardizes **discovery**, **JWKS keys**, the **UserInfo endpoint**, and **Single Sign-On (SSO)**.

## 🔵 सरल परिभाषा (Hindi)
OIDC, OAuth 2.0 के ऊपर "पहचान" जोड़ता है। Login के बाद access token के साथ एक ID token (signed JWT) भी मिलता है, जो बताता है कि यूज़र कौन है (id, email, name) और किसने (Google) प्रमाणित किया।
इसी से "Login with Google" और कंपनियों में एक बार login से सारे ऐप (SSO) चलते हैं।

---

## 🔴 Problem it Solves
OAuth 2.0 only says *"this app may access X"*. Developers misused OAuth for **login**:
- They called a provider API with the access token to fetch "me", and every provider did it **differently** (Facebook `/me`, Google `/userinfo`, GitHub `/user`).
- **Token substitution attacks:** an access token issued to **another app** could be passed to your app, and your app would log the attacker in as the victim.
- No standard for session info, logout or key discovery.

OIDC fixes this with a **standard, verifiable identity token** issued **specifically for your app** (`aud` = your client_id), plus standard endpoints, so login works the same way across all providers.

## 🔴 यह क्यों बना? (Hindi)
OAuth सिर्फ़ "पहुँच" देता है, पहचान नहीं। लोग login के लिए OAuth का ग़लत इस्तेमाल करते थे — हर provider का अलग तरीका, और दूसरे ऐप का token आपके ऐप में डालकर किसी और के रूप में login हो जाता था।
OIDC एक मानक ID token देता है, जो सिर्फ़ आपके ऐप के लिए बना होता है (aud), और हर provider के साथ login का एक ही तरीका।

---

## 🟢 How it Works — Step by Step

### Same as OAuth Authorization Code + PKCE, plus `openid` scope

```
1. Client → /authorize?response_type=code&scope=openid email profile
           &client_id=..&redirect_uri=..&state=..&nonce=RANDOM&code_challenge=..
2. User logs in at the OpenID Provider (OP) (password, MFA, passkey — OP's job)
3. OP → redirect_uri?code=..&state=..
4. Client → POST /token (code + code_verifier)
5. OP → { access_token, id_token, refresh_token, expires_in }
6. Client VERIFIES the id_token, then creates its own session for that user
```

### The ID token (JWT)

```json
{
  "iss": "https://accounts.google.com",        // who issued it — must match expected issuer
  "sub": "110169484474386276334",              // stable unique user id at this provider ⭐ use this
  "aud": "1234-abc.apps.googleusercontent.com",// YOUR client_id — reject if not yours
  "exp": 1729254000, "iat": 1729250400,        // validity
  "nonce": "n-0S6_WzA2Mj",                     // must equal the nonce you sent (replay protection)
  "auth_time": 1729250390,                     // when user actually authenticated
  "amr": ["pwd", "mfa"],                       // how (methods) — e.g. MFA used
  "email": "aditya@gmail.com", "email_verified": true,
  "name": "Aditya Ranjan", "picture": "https://..."
}
```

### ID token validation checklist
```
✓ Signature valid using provider's JWKS (fetched via discovery; cache; rotate by kid)
✓ alg is expected (RS256/ES256), never "none"
✓ iss == expected issuer
✓ aud contains YOUR client_id (and azp if multiple audiences)
✓ exp in future, iat reasonable
✓ nonce == the one stored for this login attempt
✓ email_verified == true before trusting email for account linking
Then identify the user by (iss, sub) — NOT by email (emails can change / be reassigned).
```

### ID token vs Access token (common confusion)

```
┌──────────────────┬─────────────────────────────────┬──────────────────────────────────┐
│                  │ ID token                        │ Access token                     │
├──────────────────┼─────────────────────────────────┼──────────────────────────────────┤
│ Purpose          │ Tell the CLIENT who logged in   │ Let client call an API           │
│ Audience         │ The client app (client_id)      │ The resource server/API          │
│ Format           │ Always JWT                      │ JWT or opaque                    │
│ Send to APIs?    │ ❌ No                           │ ✅ Yes (Bearer)                  │
│ Contains         │ identity claims                 │ scopes/permissions               │
└──────────────────┴─────────────────────────────────┴──────────────────────────────────┘
```

### Discovery & standard endpoints

```
GET https://accounts.google.com/.well-known/openid-configuration
{
  "issuer": "https://accounts.google.com",
  "authorization_endpoint": ".../o/oauth2/v2/auth",
  "token_endpoint": "https://oauth2.googleapis.com/token",
  "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
  "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
  "end_session_endpoint": "...",          (logout, for providers that support it)
  "scopes_supported": ["openid","email","profile"], ...
}
Libraries read this → no hardcoding of endpoints/keys.
Standard scopes: openid (required), profile, email, address, phone, offline_access (refresh token)
```

### SSO (Single Sign-On)

```
Employee logs into Okta/Azure AD (OP) once in the morning.
Opens Jira → redirect to OP → OP sees an existing session → instantly redirects back with code
Opens Slack → same → no password again
OP session = one login for all apps. Logout can be propagated (front/back-channel logout).
(SAML 2.0 = older XML-based SSO standard, still common in enterprises; OIDC is the modern JSON/JWT one.)
```

### Your app's own session after OIDC
```
After verifying the ID token, the app should create ITS OWN session/token (Topic 54/57).
Don't keep using the provider's tokens as your session — they're for the provider's APIs.
Account linking: users table + identities table (provider, provider_sub) → one user, many login methods.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Flow वही OAuth Code + PKCE है, बस scope में `openid` जोड़ते हो और एक random `nonce` भेजते हो।
2. Token endpoint से access token के साथ ID token (JWT) मिलता है — उसमें sub (यूज़र id), email, iss, aud होते हैं।
3. ID token को जाँचो: signature (JWKS से), iss, aud = आपका client_id, exp, nonce, email_verified।
4. यूज़र को (iss, sub) से पहचानो, email से नहीं; फिर अपने ऐप का session/टोकन बनाओ।
5. Discovery URL (`/.well-known/openid-configuration`) से सारे endpoints और keys अपने आप मिलते हैं; एक OP पर login से कई ऐप में SSO।

---

## 🟡 Real World Example

**Login with Google / Apple / Microsoft** — all OIDC. "Sign in with Apple" also offers **private relay emails** and requires apps on iOS that offer third-party login to also offer Apple login. The `sub` stays stable even if the user hides their email.

**Corporate SSO (Okta, Azure AD / Entra ID, Google Workspace)** — Infosys, TCS and startups use OIDC/SAML so employees log in once to access Slack, Jira, AWS, GitHub and internal tools, with central MFA and instant offboarding (disable the user once and access is gone everywhere).

**Auth0, Clerk, Cognito, Keycloak, Supabase Auth** — act as your OpenID Provider, so your app supports Google, Apple, email OTP, passkeys and enterprise SSO with one integration.

**Email-based account takeover bugs** — some apps linked accounts by **email** from social providers without checking `email_verified` or the provider's trust. Attackers created accounts with unverified emails on a lax provider and took over victims' accounts. Use `(iss, sub)` and verified emails only.

## 🟡 Real Example Hindi में
Login with Google/Apple/Microsoft सब OIDC हैं। कंपनियों में Okta/Azure AD से सुबह एक बार login करके Slack, Jira, AWS सब खुल जाते हैं (SSO), और कर्मचारी जाए तो एक जगह से सब access बंद।
कुछ ऐप्स ने बिना `email_verified` जाँचे email से अकाउंट जोड़े — हैकर्स ने दूसरों के अकाउंट हथिया लिए। इसलिए हमेशा (iss, sub) से पहचानो।

---

## 🟠 My Stack Example

### Accounts schema supporting many login methods
```sql
CREATE TABLE users (id BIGSERIAL PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE identities (
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider    TEXT NOT NULL,           -- 'google' | 'apple' | 'microsoft' | 'phone'
  provider_sub TEXT NOT NULL,          -- OIDC sub (stable id)
  email       TEXT,
  email_verified BOOLEAN,
  PRIMARY KEY (provider, provider_sub)
);
```

### Node — generic OIDC client (`openid-client`), works with any provider
```js
import * as client from 'openid-client';

const config = await client.discovery(new URL('https://accounts.google.com'), GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET);

app.get('/auth/google/start', async (req, res) => {
  const code_verifier = client.randomPKCECodeVerifier();
  const state = client.randomState(), nonce = client.randomNonce();
  req.session.oidc = { code_verifier, state, nonce };
  const url = client.buildAuthorizationUrl(config, {
    redirect_uri: `${APP_URL}/auth/google/callback`, scope: 'openid email profile',
    code_challenge: await client.calculatePKCECodeChallenge(code_verifier), code_challenge_method: 'S256',
    state, nonce,
  });
  res.redirect(url.href);
});

app.get('/auth/google/callback', async (req, res) => {
  const { code_verifier, state, nonce } = req.session.oidc;
  const tokens = await client.authorizationCodeGrant(config, new URL(req.url, APP_URL), {
    pkceCodeVerifier: code_verifier, expectedState: state, expectedNonce: nonce,
  });                                                  // validates id_token: sig, iss, aud, exp, nonce
  const claims = tokens.claims();                      // { sub, email, email_verified, name, ... }
  const user = await findOrCreateByIdentity('google', claims.sub, claims);
  req.session.regenerate(() => { req.session.userId = user.id; res.redirect('/dashboard'); });
});
```

### Verify an ID token sent from a mobile app (FastAPI)
```python
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

@app.post("/auth/google/mobile")
async def google_mobile(body: IdTokenIn):
    try:
        info = id_token.verify_oauth2_token(body.id_token, grequests.Request(),
                                            audience=[ANDROID_CLIENT_ID, IOS_CLIENT_ID])
    except ValueError:
        raise HTTPException(401, "invalid id token")
    if info["iss"] not in ("accounts.google.com", "https://accounts.google.com") or not info.get("email_verified"):
        raise HTTPException(401)
    user = await find_or_create_identity("google", info["sub"], info)
    return issue_app_tokens(user)            # your own access/refresh tokens
```

### React Native — Sign in with Apple (required on iOS if you offer other social logins)
```tsx
import * as AppleAuthentication from 'expo-apple-authentication';
const cred = await AppleAuthentication.signInAsync({
  requestedScopes: [AppleAuthentication.AppleAuthenticationScope.FULL_NAME, AppleAuthentication.AppleAuthenticationScope.EMAIL],
  nonce: hashedNonce,
});
await api.post('/auth/apple', { identityToken: cred.identityToken, rawNonce });   // backend verifies against Apple JWKS
```

### Using a managed OP (simplest path)
```
Auth0 / Clerk / Cognito / Keycloak = your OpenID Provider
  ✓ Google, Apple, phone OTP, email magic link, passkeys, enterprise SAML/OIDC SSO
  ✓ Your APIs only verify THEIR JWTs via JWKS (one integration)
Self-host Keycloak if you need control / data residency.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is OpenID Connect and how does it differ from OAuth 2.0?**
A1: OIDC is an identity layer on OAuth 2.0. OAuth provides delegated authorization through access tokens for APIs. OIDC adds authentication: the `openid` scope makes the provider return an ID token, a signed JWT with standard claims about the user and the login event (iss, sub, aud, exp, nonce, auth_time). It also standardizes discovery, JWKS, the UserInfo endpoint and logout, so login works uniformly across providers and SSO is possible.

**Q2: How do you validate an ID token?**
A2: Fetch the provider's keys via discovery or `jwks_uri` (cached, rotated by `kid`). Verify the signature with an expected algorithm, check `iss` equals the provider's issuer, `aud` includes your client_id (and `azp` if present), `exp`/`iat` are valid, and `nonce` matches the one you generated for this login. Before trusting the email, require `email_verified`. Then identify the user by the (iss, sub) pair.

**Q3: Should you send the ID token to your backend APIs as a bearer token?**
A3: No. The ID token's audience is the client application, and it describes a login event. Its purpose is to let the client establish who the user is. APIs should receive access tokens whose audience is the API, with scopes or permissions, or the app's own session or token issued after login. Mixing them causes audience confusion and security issues.

**Q4: Why identify users by `sub` instead of email?**
A4: `sub` is a stable, unique identifier for the user at that issuer and never changes. Emails can change, be reassigned (corporate addresses reused), be unverified at some providers, or be hidden (Apple private relay). Linking accounts purely by email enables account-takeover attacks. Store (provider/iss, sub) in an identities table, and only link by email when it's verified and from a trusted provider, ideally with user confirmation.

**Q5: How does SSO work with OIDC?**
A5: All apps trust the same OpenID Provider. When the user first logs into app A, they authenticate at the OP, which sets its own session cookie. When they open app B, it redirects to the OP, which sees the existing session and immediately redirects back with an authorization code without prompting, and B gets its own ID token. Central MFA, password policies and offboarding are enforced at the OP. Single logout uses OIDC front-channel or back-channel logout to notify the apps.

---

## 🔷 Trade-offs
✅ Advantages:
- Standard, secure login across providers; verifiable identity (signed, audience-bound).
- SSO, MFA, passkeys handled by the provider; less password handling for you.
- Discovery & JWKS make integration and key rotation easy.

❌ Disadvantages:
- Dependency on external identity providers (outages, policy changes).
- Complexity: redirects, nonce/state, token validation, account linking edge cases.
- Privacy/UX variations (Apple hidden email, missing fields).
- Logout across apps is harder than login.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OIDC | Identity layer on OAuth 2.0 | OAuth के ऊपर पहचान की परत |
| OpenID Provider (OP) | Issues ID tokens (Google, Okta) | पहचान देने वाला |
| Relying Party (RP) | App that trusts the OP | OP पर भरोसा करने वाला ऐप |
| ID token | JWT describing the user | यूज़र की पहचान वाला JWT |
| sub | Stable user identifier | यूज़र की स्थायी id |
| nonce | Random value to prevent replay | replay रोकने का random value |
| Discovery | .well-known configuration | अपने आप endpoints जानना |
| UserInfo endpoint | API returning user claims | यूज़र जानकारी API |
| SSO | Single sign-on across apps | एक login, कई ऐप |
| SAML | Older XML-based SSO standard | पुराना SSO मानक |

---

## ⚡ 3-Line Summary
**English:**
1. OIDC = OAuth 2.0 + ID token (signed JWT about who logged in) + discovery/JWKS/UserInfo standards.
2. Validate signature, iss, aud (your client_id), exp, nonce, email_verified; identify users by (iss, sub).
3. ID token is for the client, access token is for APIs; after login, create your own app session. OIDC powers social login and SSO.

**Hindi:**
1. OIDC = OAuth 2.0 + ID token (कौन login हुआ) + discovery/JWKS के मानक।
2. Signature, iss, aud, exp, nonce, email_verified जाँचो; यूज़र को (iss, sub) से पहचानो।
3. ID token क्लाइंट के लिए, access token API के लिए; login के बाद अपना session बनाओ। Social login और SSO इसी से।

---

## ➡️ Next Topic Suggestion
**57. Session vs Token Auth** — After login (password or OIDC), your app needs to remember the user. Next: server-side sessions with cookies vs stateless tokens (JWT), and which to choose for web, mobile and microservices.
