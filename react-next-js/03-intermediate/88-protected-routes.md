# 88. Protected Routes
# हिंदी में: Protected Routes — सिर्फ login वाले users को pages दिखाना

---

## 🔵 Simple Definition (English)
Protected route ek route hai jo sirf tab render hota hai jab user logged in ho (aur kabhi-kabhi sahi role wala ho). Agar user logged in nahi hai, to use login page par redirect kar diya jaata hai, aur login ke baad woh wapas usi page par aata hai. React mein yeh ek guard component se banta hai jo `<Outlet />` ya `<Navigate />` return karta hai.

## 🔵 सरल परिभाषा (Hindi)
Protected route एक route है जो तभी render होता है जब user logged in हो (और कभी-कभी सही role वाला हो)। अगर user logged in नहीं है, तो उसे login page पर redirect कर दिया जाता है, और login के बाद वह वापस उसी page पर आता है। React में यह एक guard component से बनता है जो `<Outlet />` या `<Navigate />` return करता है।

---

## 🔴 Problem it Solves
Har page par `if (!user) redirect` likhna repeat hota है, और भूल जाने पर कोई page खुला रह जाता है। Login के बाद user को उसी page पर वापस लाना भी मुश्किल होता है, क्योंकि redirect होने पर URL की जानकारी खो जाती है। Guard component इन सबको एक जगह रखता है। पर सबसे ज़रूरी बात: यह सिर्फ UX के लिए है। असली security server पर होनी चाहिए, क्योंकि browser code कोई भी बदल सकता है।

## 🔴 यह क्यों बना? (Hindi)
हर page पर `if (!user) redirect` लिखना repeat होता है, और भूल जाने पर कोई page खुला रह जाता है। Login के बाद user को उसी page पर वापस लाना भी मुश्किल होता है, क्योंकि redirect होने पर URL की जानकारी खो जाती है। Guard component इन सबको एक जगह रखता है। पर सबसे ज़रूरी बात: यह सिर्फ UX के लिए है। असली security server पर होनी चाहिए, क्योंकि browser का code कोई भी बदल सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App ke upar AuthProvider: user, status ('loading' | 'in' | 'out') state mein
Step 2 → Mount par /api/me call karo (cookie bheji jaati hai) → status set karo
Step 3 → Guard (RequireAuth) status dekhta hai:
         'loading' → kuch mat dikhao (spinner) — redirect NAHI karna
         'out'     → <Navigate to="/login" state={{ from: location }} replace />
         'in'      → <Outlet /> (child page render)
Step 4 → Login success → navigate(from) — user wahin wapas
Step 5 → Role check (optional): user.role allowed list mein nahi → /forbidden
Step 6 → Server par bhi same check (middleware / route handler) — yeh asli security hai
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → App के ऊपर AuthProvider: user, status ('loading' | 'in' | 'out') state में
Step 2 → Mount पर /api/me call करो (cookie भेजी जाती है) → status set करो
Step 3 → Guard (RequireAuth) status देखता है:
         'loading' → कुछ मत दिखाओ (spinner) — redirect नहीं करना
         'out'     → <Navigate to="/login" state={{ from: location }} replace />
         'in'      → <Outlet /> (child page render)
Step 4 → Login success → navigate(from), user वहीं वापस
Step 5 → Role check (optional): user.role allowed list में नहीं → /forbidden
Step 6 → Server पर भी वही check (middleware / route handler), यही असली security है
```

---

## 🟡 Real World Example
**Zomato Partner (restaurant) app:** Restaurant owner `/dashboard/orders` खोलने की कोशिश करता है। Agar login नहीं है, तो `/login` पर भेजा जाता है, और login के बाद सीधे `/dashboard/orders` खुलता है। Delivery partner का account इस page को नहीं खोल सकता, क्योंकि उसका role `restaurant` नहीं है, इसलिए `/forbidden` दिखता है। और server हर API call पर भी role check करता है, ताकि सिर्फ browser बदलने से कोई data न ले सके।

## 🟡 Real Example Hindi mein
**Zomato Partner (restaurant) app:** Restaurant owner `/dashboard/orders` खोलने की कोशिश करता है। अगर login नहीं है, तो उसे `/login` पर भेजा जाता है, और login के बाद सीधे `/dashboard/orders` खुलता है। Delivery partner का account इस page को नहीं खोल सकता, क्योंकि उसका role `restaurant` नहीं है, इसलिए `/forbidden` दिखता है। और server हर API call पर भी role check करता है, ताकि सिर्फ browser का code बदलकर कोई data न ले सके।

---

## 💻 Code Example — Basic

```jsx
import { createContext, useContext, useState, useEffect } from 'react';   // React tools
import { Navigate, Outlet, useLocation } from 'react-router-dom';         // router tools (v6)

const AuthContext = createContext(null);                 // holds the auth state for the whole app

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);                // the logged-in user, or null
  const [status, setStatus] = useState('loading');       // 'loading' | 'in' | 'out'

  useEffect(() => {
    fetch('/api/me', { credentials: 'include' })         // send the session cookie
      .then(res => (res.ok ? res.json() : null))         // 200 → user JSON, otherwise null
      .then(data => {                                    // answer arrived
        setUser(data);                                   // store the user (or null)
        setStatus(data ? 'in' : 'out');                  // logged in or not
      })
      .catch(() => setStatus('out'));                    // network error → treat as logged out
  }, []);                                                // check once on app start

  return (
    <AuthContext.Provider value={{ user, status, setUser, setStatus }}>
      {children}                                         {/* the rest of the app */}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);                        // read the auth state anywhere
}

// Guard: a layout route that protects its children
export function RequireAuth() {
  const { status } = useAuth();                          // current auth state
  const location = useLocation();                        // URL the user tried to open

  if (status === 'loading') return <p>Checking login…</p>; // wait: do NOT redirect yet
  if (status === 'out') {                                // definitely not logged in
    return <Navigate to="/login" replace state={{ from: location }} />; // remember where to go back
  }
  return <Outlet />;                                     // logged in: render the protected child
}
```

Route setup (in the app root):

```jsx
<Routes>
  <Route path="/login" element={<LoginPage />} />         {/* public page */}
  <Route element={<RequireAuth />}>                       {/* layout route: no path, just a guard */}
    <Route path="/dashboard" element={<Dashboard />} />   {/* protected */}
    <Route path="/dashboard/orders" element={<Orders />} /> {/* protected */}
  </Route>
</Routes>
```

## 💻 Code Example — Advanced

```jsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './auth';                        // the context from the basic example

// Guard with a role list: "admin" or "restaurant", and a clear forbidden page
export function RequireRole({ allowedRoles }) {
  const { status, user } = useAuth();                    // auth state from context
  const location = useLocation();                        // to come back after login

  if (status === 'loading') {                            // session check still running
    return <div role="status" aria-live="polite">Checking access…</div>; // no redirect yet
  }
  if (status === 'out' || !user) {                       // not logged in
    return <Navigate to="/login" replace state={{ from: location }} />; // go to login
  }
  if (!allowedRoles.includes(user.role)) {               // logged in, but wrong role
    return <Navigate to="/forbidden" replace />;         // show a clear "no access" page
  }
  return <Outlet />;                                     // allowed: render the child route
}

// Login page: after success, return the user to the page they wanted
export function LoginPage() {
  const { setUser, setStatus } = useAuth();              // update the global auth state
  const location = useLocation();                        // carries state.from from the guard
  const target = location.state?.from?.pathname ?? '/dashboard'; // default page

  async function handleLogin(email, password) {
    const res = await fetch('/api/login', {              // send credentials to the server
      method: 'POST',                                    // POST for login
      headers: { 'Content-Type': 'application/json' },   // we send JSON
      credentials: 'include',                            // accept the Set-Cookie response
      body: JSON.stringify({ email, password }),         // never log passwords
    });
    if (!res.ok) return false;                           // wrong credentials → stay here
    setUser(await res.json());                           // save the user in context
    setStatus('in');                                     // now the guard lets us in
    return true;                                         // caller can navigate
  }

  return (
    <button onClick={() => handleLogin('a@example.com', 'secret')}> {/* demo button only */}
      Log in and go to {target}
    </button>
  );
}

// Route tree: public, any logged-in user, and admin-only areas
export const routes = [
  { path: '/login', element: <LoginPage /> },           // public
  {
    element: <RequireRole allowedRoles={['admin', 'restaurant']} />, // guard layout
    children: [
      { path: '/dashboard', element: <h1>Dashboard</h1> }, // both roles
      {
        element: <RequireRole allowedRoles={['admin']} />, // extra guard for admin only
        children: [{ path: '/admin', element: <h1>Admin</h1> }],
      },
    ],
  },
  { path: '/forbidden', element: <h1>You do not have access</h1> }, // role error page
];
```

Note: `routes` is a plain array, so a `createBrowserRouter(routes)` call uses it directly. Guards nest the same way in both styles.

---

## 🟠 Real app integration

The client guard only hides screens. The real check belongs on the server, for every API call. A Next.js `middleware.js` file can also redirect early, but it is a convenience, not the only defence:

```javascript
// Express: the real security check, run on every protected API route
function requireAuth(req, res, next) {                  // middleware
  const token = req.cookies?.session;                   // session cookie (cookie-parser needed)
  const user = token ? sessions.get(token) : null;      // lookup your session store (Redis, DB)
  if (!user) return res.status(401).json({ error: 'Login required' }); // 401 Unauthorized
  req.user = user;                                      // attach the user for later handlers
  next();                                               // continue to the route
}

function requireRole(...roles) {                        // factory: returns a middleware
  return (req, res, next) => {
    if (!roles.includes(req.user?.role)) {              // role must be in the list
      return res.status(403).json({ error: 'Forbidden' }); // 403 Forbidden: logged in but not allowed
    }
    next();                                             // allowed
  };
}

app.get('/api/restaurant/orders', requireAuth, requireRole('restaurant'), async (req, res) => {
  // only logged-in restaurant users reach this line
  const { rows } = await db.query('SELECT id, status FROM orders WHERE restaurant_id = $1', [req.user.restaurantId]);
  res.json(rows);                                       // scoped to THIS user's restaurant
});
```

Next.js: a `middleware.js` file at the project root can redirect requests to `/dashboard` when there is no session cookie. In newer Next.js releases this file convention has been renamed, so check the current docs. Whatever the file is called, the page or the API must still verify the session itself:

```javascript
// middleware.js (Next.js) — early redirect for UX; not the only check
import { NextResponse } from 'next/server';

export function middleware(request) {
  const session = request.cookies.get('session');       // read the session cookie
  if (!session) {                                       // no cookie: not logged in
    const url = new URL('/login', request.url);         // build the login URL
    url.searchParams.set('from', request.nextUrl.pathname); // remember the target page
    return NextResponse.redirect(url);                  // send the user to login
  }
  return NextResponse.next();                           // cookie found: continue
}

export const config = { matcher: ['/dashboard/:path*'] }; // only run for these paths
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Redirecting while the session is still loading (logged-in users get sent to login after a refresh)
✅ **Correct:** Keep a `loading` status and render a placeholder until `/api/me` answers.

```jsx
// Wrong: user is null on the first render, so a refresh always redirects
function RequireAuth() {
  const { user } = useAuth();                           // null until /api/me returns
  if (!user) return <Navigate to="/login" replace />;   // ❌ fires too early
  return <Outlet />;
}

// Right: wait for the answer before deciding
function RequireAuth2() {
  const { status } = useAuth();                          // 'loading' | 'in' | 'out'
  if (status === 'loading') return <p>Checking login…</p>; // ✅ no redirect yet
  if (status === 'out') return <Navigate to="/login" replace />;
  return <Outlet />;
}
```

❌ **Mistake 2:** Thinking a client-side guard is security
✅ **Correct:** Anyone can open DevTools and change the React state. Protect every API route on the server.

```jsx
// Wrong: the data is returned to anyone who calls the API, the guard only hides the page
app.get('/api/salary', (req, res) => res.json(salaries));  // ❌ no auth check

// Right: the server checks the session first
app.get('/api/salary', requireAuth, requireRole('hr'), (req, res) => { // ✅
  res.json(salaries);
});
```

❌ **Mistake 3:** Losing the target page on login (user always lands on home)
✅ **Correct:** Save the URL in `state.from` (or a query param) and read it after login.

```jsx
// Wrong: the guard redirects, but the original URL is gone after login
return <Navigate to="/login" replace />;                 // ❌ no memory of /dashboard/orders

// Right: pass the location, read it on the login page, then navigate back
return <Navigate to="/login" replace state={{ from: location }} />; // ✅
// on the login page: navigate(location.state?.from?.pathname ?? '/', { replace: true });
```

---

## 🧠 Tricky Interview Question

```jsx
function ProtectedPage() {
  const { user } = useAuth();                           // user is null on the first render
  if (!user) return <Navigate to="/login" replace />;   // redirect when there is no user
  return <Dashboard />;
}

// AuthProvider loads the user with fetch('/api/me') inside useEffect.
// The user is logged in, and has a valid session cookie.
// The user refreshes the /dashboard page. Where do they end up?
```

**Answer:** They land on `/login`, even though they are logged in. On the first render `user` is still `null`, because the `fetch('/api/me')` inside `useEffect` has not finished. `ProtectedPage` sees `!user` and returns `<Navigate>`, which redirects right away. The session fetch finishes later, but the redirect has already happened. The fix is a three-state `status` (`'loading' | 'in' | 'out'`), so the guard waits while the session is being checked, as shown in the Basic example. The same bug appears when the app reads from `localStorage` in an effect instead of in the initial state.

---

## ⚫ Interview Questions + Answers

**Q1: How do you build a protected route in React Router v6?**
A1: Use a layout route with no path (`<Route element={<RequireAuth />}>`). The guard returns `<Outlet />` when the user is logged in, and `<Navigate to="/login" />` otherwise. Every child route inside it is protected.

**Q2: Why use `replace` on the redirect to login?**
A2: `replace` swaps the current history entry. After login, the Back button does not go back to the protected page and bounce the user to login again.

**Q3: How do you return the user to the page they wanted after login?**
A3: Pass the current `location` in `state` with the redirect (`state={{ from: location }}`). The login page reads `location.state.from` and navigates there after success.

**Q4: Is a client-side protected route secure?**
A4: No. It only controls what the browser shows. Any user can change the JavaScript or call the API directly. Every API endpoint must check the session and the role on the server, and the client guard is only for a smooth experience.

**Q5: Why do we need a `loading` state in the auth check?**
A5: The session is loaded asynchronously. Without a loading state, the guard decides before the answer arrives, and a logged-in user is sent to login on every refresh. A three-state status (loading, in, out) prevents that.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Pages show private data (orders, profile, dashboards, admin screens)
- Different roles see different parts of the app (admin, seller, customer)
- You want a consistent login redirect with "return to where I was"

❌ **Avoid when:**
- Treating the guard as the only security (always add server checks)
- The whole app is public: a guard adds code with no benefit
- The server already renders the page and redirects (for example, a Next.js Server Component that calls `redirect()`): the client guard is not needed there

---

## 📊 Visual Diagram

```
User opens /dashboard/orders
          │
          ▼
  AuthProvider: fetch /api/me (cookie sent)
          │
   ┌──────┼──────────────────────┐
   │      │                      │
status='loading'           status='out'                 status='in' (+ role ok)
   │      │                      │                              │
   ▼      │                      ▼                              ▼
"Checking login…"       <Navigate to="/login"        <Outlet /> → Orders page
(no redirect)            state={{from: /dashboard/orders}} replace />
                                 │
                                 ▼
                       Login success → navigate(from, { replace: true })
                                 │
                                 ▼
                       /dashboard/orders (back where the user started)

Server (every API call):  request → requireAuth → requireRole → handler   ← REAL security
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Protected route | Sirf logged-in users ke liye route | सिर्फ logged-in users के लिए route |
| Guard | Route ko check karne wala component | Route को check करने वाला component |
| Session | Server par user ki login state | Server पर user की login state |
| Role | User ki permission category (admin, restaurant) | User की permission category |
| 401 / 403 | 401 = login nahi hai, 403 = login hai par allowed nahi | 401 = login नहीं, 403 = login है पर allowed नहीं |
| state.from | Redirect se pehle ka URL, login ke baad wapas jaane ke liye | Redirect से पहले का URL |

---

## ⚡ 3-Line Summary
**English:**
1. Layout route wala guard logged-in users ko `<Outlet />` dikhata hai, aur baaki ko `<Navigate to="/login" />` se redirect karta hai।
2. Session check ke dauran `loading` state rakho, aur `state.from` se login ke baad user ko wapas bhejo।
3. Client guard sirf UX hai; asli security har API par server-side session aur role check se hoti hai।

**Hindi:**
1. Layout route वाला guard logged-in users को `<Outlet />` दिखाता है, और बाकी को `<Navigate to="/login" />` से redirect करता है।
2. Session check के दौरान `loading` state रखो, और `state.from` से login के बाद user को वापस भेजो।
3. Client guard सिर्फ UX है; असली security हर API पर server-side session और role check से होती है।

---

## ➡️ Next Topic
**89. Next topic in the React curriculum** — 88 के बाद का अगला React topic (इस batch में शामिल नहीं); उसका title curriculum list में देखें।
