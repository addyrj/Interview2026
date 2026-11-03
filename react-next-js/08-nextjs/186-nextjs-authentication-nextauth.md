# 186. Next.js Authentication (NextAuth)
# हिंदी में: Next.js Authentication (NextAuth / Auth.js) — Login, Session और Protected Pages

---

## 🔵 Simple Definition (English)
**NextAuth.js** (now called **Auth.js**) is a library that adds login to a Next.js app: sign-in with Google or GitHub (OAuth), email and password, or magic links. It manages sessions with secure cookies, so you can know who the user is on the server and the client.

## 🔵 सरल परिभाषा (Hindi)
**NextAuth.js** (अब **Auth.js** कहलाता है) एक library है जो Next.js app में login जोड़ती है: Google या GitHub से sign-in (OAuth), email-password, या magic links। यह secure cookies से sessions संभालती है, ताकि आप server और client दोनों पर जान सकें कि user कौन है।

---

## 🔴 Problem it Solves

Writing authentication yourself is risky: password hashing, session cookies, CSRF tokens, OAuth redirect flows, token refresh and logout all have subtle security traps. A mistake means account takeover. Auth.js gives a tested implementation of these flows with providers, callbacks and database adapters, so you configure instead of inventing security code.

```jsx
// PROBLEM: hand-made login
// store plain passwords? forget CSRF? insecure cookie flags? broken OAuth state?

// SOLUTION: configured, battle-tested library
// providers: [Google, Credentials] → secure session cookie → auth() on the server
```

## 🔴 यह क्यों बना? (Hindi)
Authentication खुद लिखना जोखिम भरा है: password hashing, session cookies, CSRF tokens, OAuth redirect flows, token refresh और logout सबमें छोटी-छोटी security गलतियाँ हो सकती हैं, और एक गलती का मतलब account takeover। Auth.js इन flows का परखा हुआ implementation देता है providers, callbacks और database adapters के साथ, तो आप security code बनाने की जगह configure करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install: npm i next-auth@beta  (Auth.js v5 for App Router; the version tag is version-dependent)
Step 2 → Create auth.js at the project root: NextAuth({ providers, callbacks, session })
Step 3 → Export { handlers, auth, signIn, signOut } from it
Step 4 → Create app/api/auth/[...nextauth]/route.js that exports GET and POST from handlers
Step 5 → Set env vars: AUTH_SECRET, AUTH_GOOGLE_ID, AUTH_GOOGLE_SECRET (Auth.js v5 naming)
Step 6 → User clicks "Sign in with Google" → redirect to Google → callback to your app
Step 7 → Auth.js creates a session: a signed/encrypted JWT in an httpOnly cookie (default) or a DB session
Step 8 → On the server call auth() to get the session; in middleware use auth to protect routes

Always authorize on the server; hiding a button on the client is not security
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Install: npm i next-auth@beta  (App Router के लिए Auth.js v5; version tag version-dependent है)
Step 2 → Project root में auth.js बनाओ: NextAuth({ providers, callbacks, session })
Step 3 → उससे { handlers, auth, signIn, signOut } export करो
Step 4 → app/api/auth/[...nextauth]/route.js बनाओ जो handlers से GET और POST export करे
Step 5 → env vars set करो: AUTH_SECRET, AUTH_GOOGLE_ID, AUTH_GOOGLE_SECRET (Auth.js v5 naming)
Step 6 → User "Sign in with Google" दबाता है → Google पर redirect → वापस आपके app पर callback
Step 7 → Auth.js session बनाता है: httpOnly cookie में signed/encrypted JWT (default) या DB session
Step 8 → Server पर session के लिए auth() call करो; routes protect करने के लिए middleware में auth इस्तेमाल करो

Authorization हमेशा server पर करो; client पर बटन छिपाना security नहीं है
```

---

## 🟡 Real World Example
**Zomato / Swiggy login:** A user taps "Continue with Google". After consent, the site knows their name and email, creates a session cookie, and shows "Hi Aditya" in the header. The "Saved addresses" page is only for logged-in users, and `/admin/restaurants` is only for users with the `admin` role. If someone tries to open `/orders` while logged out, they are redirected to the login page and returned to `/orders` after signing in.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy login:** User "Continue with Google" दबाता है। Consent के बाद site को उसका नाम और email पता चलता है, session cookie बनती है, और header में "Hi Aditya" दिखता है। "Saved addresses" page सिर्फ logged-in users के लिए है, और `/admin/restaurants` सिर्फ `admin` role वालों के लिए। Logged-out होकर `/orders` खोलने पर login page पर redirect होता है और sign in के बाद वापस `/orders` आता है।

---

## 💻 Code Example — Basic

```jsx
// auth.js (project root): Auth.js v5 configuration
import NextAuth from 'next-auth';                         // main function
import Google from 'next-auth/providers/google';          // Google OAuth provider

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google,                                               // reads AUTH_GOOGLE_ID / AUTH_GOOGLE_SECRET from env
  ],
  session: { strategy: 'jwt' },                           // store session in an encrypted cookie
});
```

```jsx
// app/api/auth/[...nextauth]/route.js: exposes /api/auth/* endpoints
export { GET, POST } from '@/auth';                       // hmm: re-export from handlers (see below)
```

Note: `handlers` is an object, so the safe form is:

```jsx
// app/api/auth/[...nextauth]/route.js
import { handlers } from '@/auth';                        // import the handlers object
export const { GET, POST } = handlers;                    // expose GET and POST
```

```jsx
// app/page.jsx: Server Component showing login state
import { auth, signIn, signOut } from '@/auth';

export default async function Home() {
  const session = await auth();                           // null when logged out
  if (!session) {
    return (
      <form action={async () => { 'use server'; await signIn('google'); }}> {/* Server Action */}
        <button type="submit">Sign in with Google</button>
      </form>
    );
  }
  return (
    <div>
      <p>Hi {session.user?.name}</p>                      {/* name from the provider */}
      <form action={async () => { 'use server'; await signOut(); }}>
        <button type="submit">Sign out</button>
      </form>
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// auth.js: credentials login + roles in the session + route protection callback
import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import Google from 'next-auth/providers/google';
import bcrypt from 'bcryptjs';                            // npm i bcryptjs (password hashing)
import { prisma } from '@/lib/prisma';                    // see topic 185

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google,
    Credentials({
      credentials: { email: {}, password: {} },           // fields the form sends
      async authorize(credentials) {                      // return a user object or null
        const user = await prisma.user.findUnique({ where: { email: String(credentials.email) } });
        if (!user?.passwordHash) return null;             // unknown user
        const ok = await bcrypt.compare(String(credentials.password), user.passwordHash); // compare hash
        return ok ? { id: String(user.id), name: user.name, email: user.email, role: user.role } : null;
      },
    }),
  ],
  session: { strategy: 'jwt' },                           // credentials provider requires JWT sessions
  pages: { signIn: '/login' },                            // custom login page
  callbacks: {
    jwt({ token, user }) {                                // runs on sign-in and each session check
      if (user) token.role = user.role;                   // copy role into the token at login
      return token;
    },
    session({ session, token }) {                         // shape what auth() returns
      session.user.role = token.role;                     // expose role to server and client
      return session;
    },
    authorized({ auth, request }) {                       // used by middleware (see below)
      const isAdminPath = request.nextUrl.pathname.startsWith('/admin');
      if (isAdminPath) return auth?.user?.role === 'admin'; // only admins
      return true;                                        // everything else is public here
    },
  },
});
```

```jsx
// middleware.js: first-layer protection using the authorized callback
export { auth as middleware } from '@/auth';              // runs authorized() on matched routes

export const config = { matcher: ['/admin/:path*', '/orders/:path*'] }; // protect these paths
```

---

## 🟠 Real App Integration

Client Components read the session through `SessionProvider` and `useSession`. Prefer reading it on the server and passing only what is needed as props, to keep the bundle small.

```jsx
// app/layout.jsx: provide the session to Client Components
import { SessionProvider } from 'next-auth/react';        // client-side session context
import { auth } from '@/auth';

export default async function RootLayout({ children }) {
  const session = await auth();                           // fetched on the server once
  return (
    <html lang="en">
      <body>
        <SessionProvider session={session}>{children}</SessionProvider> {/* no extra fetch on load */}
      </body>
    </html>
  );
}
```

```jsx
// app/orders/page.jsx: authorize in the page too, not only in middleware
import { auth } from '@/auth';
import { redirect } from 'next/navigation';

export default async function Orders() {
  const session = await auth();
  if (!session?.user) redirect('/login');                 // defense in depth
  return <h1>{session.user.name}'s orders</h1>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Checking login only on the client (`useSession`) and trusting it for data access
✅ **Correct:** Always verify the session on the server (`auth()`) before returning data

```jsx
// Wrong: the API returns orders to anyone; the UI only hides the button
export async function GET() {
  return Response.json(await prisma.order.findMany());    // ❌ no auth
}

// Right
export async function GET() {
  const session = await auth();                           // ✅ verify on the server
  if (!session?.user) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  return Response.json(await prisma.order.findMany({ where: { userId: Number(session.user.id) } }));
}
```

❌ **Mistake 2:** Missing or weak `AUTH_SECRET`, or committing OAuth secrets
✅ **Correct:** Generate a long random secret, keep secrets in environment variables

```
# Wrong: .env committed to git with AUTH_SECRET=secret          ❌
# Right: generate with `npx auth secret` (or `openssl rand -base64 32`), set in the host's env UI ✅
AUTH_SECRET=<long-random-value>
AUTH_GOOGLE_ID=<from Google Cloud console>
AUTH_GOOGLE_SECRET=<from Google Cloud console>
```

---

## 🧠 Tricky Interview Question

```jsx
callbacks: {
  session({ session, token }) {
    session.user.role = token.role;
    return session;
  },
}
// (no jwt callback)
```
A user logs in as admin, but `session.user.role` is always `undefined`. Why?

**Answer:** The `session` callback only reads from `token`, but nothing ever put `role` into the token. With JWT sessions, data must flow `authorize()/user` → `jwt` callback (copy `user.role` to `token.role` on sign-in) → `session` callback (copy `token.role` to `session.user.role`). Without the `jwt` callback step, `token.role` is `undefined`. Also remember that role changes made after login do not appear until the token is refreshed, because the JWT is not re-read from the database on every request.

---

## ⚫ Interview Questions + Answers

Q1: What is NextAuth/Auth.js and what does it provide?
A1: An authentication library for Next.js (and other frameworks) with OAuth and credentials providers, secure session handling, CSRF protection, callbacks and database adapters.

Q2: JWT sessions vs database sessions?
A2: JWT sessions store the session in an encrypted cookie, need no DB lookup per request and work on the Edge, but cannot be revoked instantly. Database sessions store a session id in the cookie and the data in the DB, so you can revoke immediately but need a DB call and an adapter.

Q3: How do you protect routes?
A3: Use middleware with the `authorized` callback for a fast first check, and call `auth()` in Server Components, Route Handlers and Server Actions for the real authorization.

Q4: Why is `AUTH_SECRET` important?
A4: It signs and encrypts session tokens and cookies. If it leaks or is weak, attackers can forge sessions. Use a random long value and keep it only in environment variables.

Q5: How do you add roles?
A5: Store the role in the database, copy it into the token in the `jwt` callback at sign-in, copy it from the token to the session in the `session` callback, and check it on the server for every protected action.

---

## 🔷 When to Use + When Not to Use
✅ **Use Auth.js when:**
- You need social login (Google, GitHub) or credentials login quickly
- You want secure cookie handling and CSRF protection out of the box
- You are on Next.js App Router and want `auth()` in server code

❌ **Avoid / reconsider when:**
- You need enterprise SSO, MFA and user management UI (consider Clerk, Auth0, Keycloak, WorkOS)
- You already have a separate auth backend issuing tokens
- You expect to keep a stable API: v5 is long-lived in beta, check docs for current status (version-dependent)

---

## 📊 Visual Diagram

```
  Browser ──click "Sign in with Google"──► /api/auth/signin/google
      ▲                                          │ redirect
      │                                          ▼
      │                                     Google consent
      │                                          │ code
      │      Set-Cookie: authjs.session-token    ▼
      └──────(httpOnly, signed JWT)◄── /api/auth/callback/google
  
  Later request: /orders
      │ cookie
      ▼
  middleware (authorized?) ──no──► redirect /login
      │ yes
      ▼
  Server Component: const session = await auth()  → user data → HTML

  Re-render behavior: useSession re-renders subscribers when the session
  changes; server auth() runs per request. Passing the session from the server
  to SessionProvider avoids an extra fetch.
  Performance: JWT sessions avoid a DB lookup per request; keep tokens small.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Auth.js | New name of NextAuth | NextAuth का नया नाम |
| Provider | Login method (Google, credentials) | Login का तरीका |
| OAuth | Login via another service | दूसरी service से login |
| Session | Logged-in state of a user | User की logged-in state |
| JWT | Signed token stored in cookie | Cookie में रखा signed token |
| Callback | Hook to customize flow | Flow बदलने का hook |
| Adapter | Connects Auth.js to a database | Auth.js को DB से जोड़ना |
| httpOnly cookie | Cookie hidden from JavaScript | JavaScript से छिपी cookie |

---

## ⚡ 3-Line Summary
**English:**
1. Auth.js (NextAuth) provides providers, session cookies and helpers like `auth()`, `signIn` and `signOut`.
2. Data flows through callbacks (`jwt` then `session`), and routes are protected by middleware plus server checks.
3. Always authorize on the server, keep secrets in env vars, and check the current v5 docs because APIs are version-dependent.

**Hindi:**
1. Auth.js (NextAuth) providers, session cookies और `auth()`, `signIn`, `signOut` जैसे helpers देता है।
2. Data callbacks (`jwt` फिर `session`) से बहता है, और routes middleware और server checks दोनों से protect होते हैं।
3. Authorization हमेशा server पर करो, secrets env vars में रखो, और current v5 docs देखो क्योंकि APIs version-dependent हैं।

---

## ➡️ Next Topic
**187. Next.js Performance** — bundle size, Server Components, streaming, caching, image/font/script optimization और Core Web Vitals से Next.js app तेज़ बनाना।
