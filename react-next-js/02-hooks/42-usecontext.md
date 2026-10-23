# 42. useContext — Complete Guide
# हिंदी में: useContext — Component Tree में Data Share करना

---

## 🔵 Simple Definition (English)
`useContext` lets a component **read and subscribe to a Context**. Context provides a way to pass data through the component tree **without manually passing props at every level** — solving "prop drilling." Any component that calls `useContext(MyContext)` will re-render when the context value changes.

## 🔵 सरल परिभाषा (Hindi)
`useContext` किसी component को **Context read और subscribe** करने देता है। Context component tree में data pass करने का तरीका है **बिना हर level पर manually props pass किए** — "prop drilling" problem solve करता है। जो भी component `useContext(MyContext)` call करता है, वो context value बदलने पर re-render होता है।

---

## 🔴 Problem it Solves

```jsx
// PROP DRILLING — data passes through components that don't need it!
// App → Layout → Sidebar → NavItem → UserAvatar
//                                     ↑ only this needs user!

function App() {
  const user = { name: 'Aditya', avatar: '/avatar.jpg' };
  return <Layout user={user} />;           // Layout doesn't use user...
}

function Layout({ user }) {
  return <Sidebar user={user} />;          // Sidebar doesn't use user...
}

function Sidebar({ user }) {
  return <NavItem user={user} />;          // NavItem doesn't use user...
}

function NavItem({ user }) {
  return <UserAvatar user={user} />;       // Finally used here!
}
// Every intermediate component carries 'user' prop — painful to maintain!
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// PROP DRILLING — data हर level से गुज़रता है जिन्हें उसकी ज़रूरत नहीं!
// App → Layout → Sidebar → NavItem → UserAvatar
// सिर्फ UserAvatar को user चाहिए, पर सबको prop लेनी पड़ती है
// Context से UserAvatar directly App का data access कर सकता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create Context
         const ThemeContext = React.createContext(defaultValue);

Step 2 → Wrap with Provider (at the top of your tree)
         <ThemeContext.Provider value={theme}>
           <App />
         </ThemeContext.Provider>

Step 3 → Consume in any nested component
         const theme = useContext(ThemeContext);
         // No props needed — directly gets value from Provider!

Step 4 → When Provider value changes:
         All components calling useContext(ThemeContext) re-render
         Components NOT using this context are NOT affected
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Context बनाओ
         const ThemeContext = React.createContext('light');

Step 2 → Provider से wrap करो (tree के top पर)
         <ThemeContext.Provider value="dark">
           <App />
         </ThemeContext.Provider>

Step 3 → किसी भी nested component में consume करो
         const theme = useContext(ThemeContext);
         // Props की ज़रूरत नहीं — directly Provider से value मिलती है!

Step 4 → Provider value बदलने पर:
         useContext(ThemeContext) call करने वाले सब re-render होते हैं
```

---

## 🟡 Real World Example
**Instagram Dark Mode:** You toggle dark mode in settings. The theme preference needs to be accessible by the Navbar, PostCard, Stories, Comments, Profile — dozens of components. Instead of passing `isDark` prop through every component, store it in a `ThemeContext`. Any component calls `useContext(ThemeContext)` to get the theme — one change updates the whole app.

## 🟡 Real Example Hindi mein
**Instagram Dark Mode:** Settings में dark mode toggle करो। Theme preference Navbar, PostCard, Stories, Comments, Profile — दर्जनों components को चाहिए। हर component में `isDark` prop pass करने के बजाय, `ThemeContext` में store करो। कोई भी component `useContext(ThemeContext)` से theme ले सकता है — एक change पूरी app update!

---

## 💻 Code Example — Basic

```jsx
import { createContext, useContext, useState } from 'react';

// ── STEP 1: Create the Context ────────────
// createContext(defaultValue) — default used when no Provider above
const ThemeContext = createContext('light'); // default = 'light'

// ── STEP 2: Create Provider Component ─────
// This wraps the part of tree that needs the data
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(t => t === 'light' ? 'dark' : 'light');
  };

  // value can be anything: string, object, function
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// ── STEP 3: Consume in any component ──────
// No props needed! Works at any depth in the tree

function Navbar() {
  const { theme, toggleTheme } = useContext(ThemeContext); // ← direct access!

  return (
    <nav style={{ background: theme === 'dark' ? '#333' : '#fff' }}>
      <h1>Logo</h1>
      <button onClick={toggleTheme}>
        {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
      </button>
    </nav>
  );
}

function PostCard({ post }) {
  const { theme } = useContext(ThemeContext); // same context, different component

  return (
    <div style={{
      background: theme === 'dark' ? '#222' : '#fff',
      color: theme === 'dark' ? '#fff' : '#000',
    }}>
      <h2>{post.title}</h2>
    </div>
  );
}

// ── STEP 4: Wrap the app ──────────────────
function App() {
  return (
    <ThemeProvider>          {/* Provider at the top */}
      <Navbar />             {/* uses context */}
      <PostCard post={{ title: 'Hello' }} /> {/* uses context */}
      {/* No props passed! Both components get theme from context */}
    </ThemeProvider>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { createContext, useContext, useState, useCallback, useMemo } from 'react';

// ── REAL PATTERN: Auth Context ────────────
// Used in Amazon/Zomato — user auth throughout app

// 1. Types + Context
const AuthContext = createContext(null);

// 2. Custom hook — wraps useContext with validation
function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
    // Without this: context = null (default), no helpful error
  }
  return context;
}

// 3. Provider — manages auth state
function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in (on mount)
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) setUser(JSON.parse(savedUser));
    setLoading(false);
  }, []);

  // Memoize callbacks so consumers don't re-render unnecessarily
  const login = useCallback(async (email, password) => {
    const userData = await api.login(email, password);
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('user');
  }, []);

  // Memoize value — only changes when user/loading changes
  const value = useMemo(
    () => ({ user, loading, login, logout, isLoggedIn: !!user }),
    [user, loading, login, logout]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// 4. Usage in components — clean, no prop drilling!
function ProfilePage() {
  const { user, logout, isLoggedIn } = useAuth();

  if (!isLoggedIn) return <LoginPage />;

  return (
    <div>
      <h1>Hello, {user.name}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

function CartButton() {
  const { user } = useAuth(); // any component, any depth!
  return <button>{user ? `${user.name}'s Cart` : 'Login to Cart'}</button>;
}

// ── MULTIPLE CONTEXTS ─────────────────────
// Apps often have several contexts for different concerns
function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <CartProvider>
          <Router>
            {/* All components can access auth, theme, cart */}
            <Layout />
          </Router>
        </CartProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// Context works in Next.js Client Components
// For Server Components: pass data as props from server to client

// app/layout.jsx — root layout (Client Component for providers)
'use client';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {/* Providers wrap entire app */}
        <AuthProvider>
          <ThemeProvider>
            {children}
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

// Server Component can use context indirectly via Client Components
// but Server Components themselves CAN'T use useContext

// BEST PRACTICE for Next.js:
// 1. Server Component fetches data (fast, SEO-friendly)
// 2. Passes initial data to Client Component as prop
// 3. Client Component puts in context for children

async function DashboardPage() {
  const user = await getCurrentUser(); // server-side auth check

  return (
    <DashboardClient initialUser={user} /> // pass to client
  );
}

'use client';
function DashboardClient({ initialUser }) {
  const [user, setUser] = useState(initialUser); // now in client state
  // Can put in context, use useContext, etc.
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting everything in one big context
```jsx
// WRONG: one massive context causes all consumers to re-render on ANY change
const AppContext = createContext();
function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [cart, setCart] = useState([]);
  const [notifications, setNotifications] = useState([]);

  return (
    <AppContext.Provider value={{ user, theme, cart, notifications, ...all setters }}>
      {children}
    </AppContext.Provider>
  );
}
// Adding an item to cart → ALL consumers (including Navbar for user) re-render!

// CORRECT: separate contexts for separate concerns
// UserContext, ThemeContext, CartContext, NotificationContext
```

❌ **Mistake 2:** Not memoizing context value
```jsx
// WRONG: new object on every render → all consumers re-render!
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  return (
    // New object literal on every render!
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// CORRECT: useMemo so value only changes when content changes
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const value = useMemo(
    () => ({ theme, setTheme }),
    [theme] // new object only when theme actually changes
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
const CountContext = createContext(0);

function Parent() {
  const [count, setCount] = useState(0);
  return (
    <CountContext.Provider value={count}>
      <Child />
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </CountContext.Provider>
  );
}

function Child() {
  const count = useContext(CountContext);
  console.log('Child rendered');
  return <div>{count}</div>;
}
```
**Question:** How many times does "Child rendered" log when you click the button 3 times?

**Answer:** 4 times total (1 initial + 3 clicks). Every time `count` changes in Parent, the `CountContext.Provider` value changes, causing ALL consumers (`Child`) to re-render. This is by design — context consumers re-render on every value change. For optimization, split contexts or use `React.memo` with careful value memoization.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between Context and props?**
A1: Props pass data from parent to direct child — each level must explicitly receive and forward. Context creates a "global" value accessible by any descendant without intermediate components needing to pass it. Use props for data used by 1-2 levels; context for data needed widely (theme, auth, language). Context is not a replacement for all props — component isolation is usually better.

**Q2: What is prop drilling and how does Context solve it?**
A2: Prop drilling = passing props through multiple component layers just to reach a deeply nested component, even though intermediate components don't use the prop. Context solves it by making data available globally in the subtree — any component calls `useContext()` to get the value directly, skipping intermediate layers entirely.

**Q3: When does a context consumer re-render?**
A3: A component using `useContext(MyContext)` re-renders whenever the `value` prop of the nearest `<MyContext.Provider>` above it changes. React uses `Object.is` to compare old and new values. If you pass an object literal as value (new object on every render), ALL consumers re-render every time the provider renders — fix with `useMemo`.

**Q4: What is the defaultValue in createContext used for?**
A4: The default value is used when a component calls `useContext(MyContext)` but there is NO `<MyContext.Provider>` above it in the tree. It's not the initial state of the Provider — the Provider always uses its own `value` prop. Default values are useful for: testing individual components in isolation, components used outside the provider, TypeScript type inference.

**Q5: What is the difference between Context API and Redux?**
A5: Context API is built into React — no library, good for low-frequency updates (theme, auth, language). It re-renders all consumers on change (can be slow for frequent updates), no built-in devtools, no middleware. Redux is an external library with a single store, time-travel debugging, middleware (redux-thunk, saga), and selective subscription. Use Context for simple global state; Redux (or Zustand/Jotai) for complex state with frequent updates or large teams.

---

## 🔷 When to Use + When Not to Use
✅ **Use Context when:**
- Theme (dark/light mode)
- Authentication (user data throughout app)
- Language/locale
- Global UI state (sidebar open, modal)

❌ **Avoid Context when:**
- Frequently changing data (every keystroke, scroll position) → use Zustand/Redux
- Data only needed 1-2 levels down → just use props
- Performance is critical → context causes broad re-renders
- Server Components (Next.js) → use props or server-side solutions

---

## 📊 Visual Diagram

```
PROP DRILLING (old way):
───────────────────────────────────────────
  App (user) ──props──► Layout (user)
                          │
                     ──props──► Sidebar (user)
                                  │
                            ──props──► NavItem (user)
                                          │
                                    ──props──► Avatar ← USES user

CONTEXT (new way):
───────────────────────────────────────────
  UserContext.Provider (user)
  │
  ├── Layout          ← no prop needed
  │   ├── Sidebar     ← no prop needed
  │   │   └── NavItem ← no prop needed
  │   │       └── Avatar ← useContext() → gets user directly! ✅
  │   └── Content     ← no prop needed
  └── Footer          ← no prop needed

CONTEXT PROVIDER + CONSUMER:
───────────────────────────────────────────
  createContext() → { Provider, Consumer }

  <Provider value={data}>    ← broadcasts value
    <A />
      <B />
        <C>
          useContext() → receives data ✅
        </C>
  </Provider>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context | Global data store for a tree | Tree के लिए global data store |
| Provider | Component that supplies context value | Context value provide करने वाला component |
| Consumer | Component that uses context | Context use करने वाला component |
| Prop drilling | Passing props through many layers | कई layers से props pass करना |
| createContext | Creates a context object | Context object बनाना |
| defaultValue | Value when no Provider above | ऊपर कोई Provider न हो तो default |

---

## ⚡ 3-Line Summary
**English:**
1. `useContext(MyContext)` lets any component read the nearest `<MyContext.Provider value={...}>` above it — no prop drilling.
2. Component re-renders whenever context value changes — don't put frequently-updating data in context.
3. Pattern: `createContext` → wrap with `Provider` → consume anywhere with `useContext` — often wrap in a custom hook with error check.

**Hindi:**
1. `useContext(MyContext)` किसी भी component को सबसे नज़दीकी `<MyContext.Provider value={...}>` से data लेने देता है — कोई prop drilling नहीं।
2. Context value बदलने पर component re-render होता है — frequently-updating data context में मत रखो।
3. Pattern: `createContext` → `Provider` से wrap → कहीं भी `useContext` से consume — अक्सर custom hook में wrap करो।

---

## ➡️ Next Topic
**43. Context API — Complete Guide** — Context के सभी patterns — multiple contexts, performance optimization, और real-world architecture।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Context API](https://www.youtube.com/results?search_query=context+api+react+akshay+saini+namaste) | Context explained in Hindi |
| 📺 YouTube | [Jack Herrington — useContext](https://www.youtube.com/results?search_query=usecontext+hook+react+jack+herrington) | Performance patterns |
| 📝 Article | [react.dev — useContext](https://react.dev/reference/react/useContext) | Official reference + patterns |
| 📝 Article | [react.dev — Passing Data Deeply](https://react.dev/learn/passing-data-deeply-with-context) | Context tutorial with examples |
