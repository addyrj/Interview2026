# 65. Higher Order Components (HOC)
# हिंदी में: Higher Order Components (HOC) — Component लेकर नया Enhanced Component लौटाना

---

## 🔵 Simple Definition (English)
A **Higher Order Component (HOC)** is a function that takes a component and returns a **new component** with extra behavior or props. Example: `withAuth(Dashboard)` returns a component that checks login before showing `Dashboard`. The original component is not changed; it is wrapped.

## 🔵 सरल परिभाषा (Hindi)
**Higher Order Component (HOC)** एक function है जो एक component लेता है और उसके बदले **नया component** लौटाता है, जिसमें extra behavior या props होते हैं। उदाहरण: `withAuth(Dashboard)` एक ऐसा component लौटाता है जो `Dashboard` दिखाने से पहले login जाँचता है। Original component बदला नहीं जाता, उसे wrap किया जाता है।

---

## 🔴 Problem it Solves

Before hooks, logic like "check auth", "show a spinner while loading", or "log every render" was needed in many components. Components could not share stateful logic directly (there were no hooks), and mixins were discouraged. HOCs gave a way to wrap a component once and reuse the same behavior everywhere. They are still useful for route guards, error reporting, and wrapping third-party components.

```jsx
// PROBLEM: the same auth check is copied into every protected page
function Dashboard() {
  const user = useUser();
  if (!user) return <Redirect to="/login" />;   // ❌ copied everywhere
  return <h1>Dashboard</h1>;
}
function Orders() {
  const user = useUser();
  if (!user) return <Redirect to="/login" />;   // ❌ same code again
  return <h1>Orders</h1>;
}

// SOLUTION: write the check once and wrap each page
const ProtectedDashboard = withAuth(Dashboard);  // ✅ one place for the rule
const ProtectedOrders = withAuth(Orders);
```

## 🔴 यह क्यों बना? (Hindi)
Hooks आने से पहले "auth check करो", "loading में spinner दिखाओ", या "हर render log करो" जैसी logic कई components में चाहिए थी। Components सीधे stateful logic share नहीं कर सकते थे, और mixins को पसंद नहीं किया जाता था। HOC एक बार component को wrap करने और हर जगह वही behavior दोबारा इस्तेमाल करने का तरीका था। आज भी route guards, error reporting और third-party components को wrap करने में काम आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a function: withSomething(WrappedComponent)
Step 2 → Inside, return a new component (function) that renders WrappedComponent
Step 3 → The new component adds behavior: checks, extra props, loading UI, logging
Step 4 → Forward the original props with {...props} so the wrapped component still works
Step 5 → Set displayName so DevTools shows a readable name (withAuth(Dashboard))
Step 6 → Use the enhanced component wherever you need the behavior

KEY: an HOC is a function that returns a component, not a component itself
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Function लिखो: withSomething(WrappedComponent)
Step 2 → अंदर से एक नया component (function) लौटाओ जो WrappedComponent render करे
Step 3 → नया component behavior जोड़ता है: checks, extra props, loading UI, logging
Step 4 → Original props को {...props} से आगे भेजो, ताकि wrapped component काम करता रहे
Step 5 → displayName सेट करो, ताकि DevTools में withAuth(Dashboard) जैसा नाम दिखे
Step 6 → जहाँ behavior चाहिए वहाँ enhanced component इस्तेमाल करो

KEY: HOC एक function है जो component लौटाता है, खुद component नहीं
```

---

## 🟡 Real World Example
**Flipkart seller dashboard:** Many pages require a seller to be logged in and verified. A `withSellerAuth` HOC wraps `OrdersPage`, `ReturnsPage` and `PayoutsPage`. If the seller is not logged in, the HOC redirects to login. If the seller is logged in but not verified, it shows a verification notice. The three pages contain only their own UI, and the rule is written once.

## 🟡 Real Example Hindi mein
**Flipkart seller dashboard:** कई pages के लिए seller का login और verification ज़रूरी है। `withSellerAuth` HOC `OrdersPage`, `ReturnsPage` और `PayoutsPage` को wrap करता है। Login न हो तो HOC login पर redirect करता है। Login हो पर verify न हो तो verification notice दिखाता है। तीनों pages में सिर्फ उनका अपना UI है, और नियम एक ही बार लिखा गया है।

---

## 💻 Code Example — Basic

```jsx
// Basic HOC: withLoading shows a message until data is ready, then renders the wrapped component
import { createRoot } from 'react-dom/client';   // React 18/19 root API

// The HOC: takes a component, returns a new component
function withLoading(WrappedComponent) {
  function WithLoading({ isLoading, ...rest }) { // pull out isLoading, keep other props in rest
    if (isLoading) {                             // still loading?
      return <p>Loading your data…</p>;         // show a placeholder
    }
    return <WrappedComponent {...rest} />;       // forward all other props to the original
  }
  WithLoading.displayName = `withLoading(${WrappedComponent.displayName || WrappedComponent.name})`; // readable name in DevTools
  return WithLoading;                            // the new, enhanced component
}

// The original component: knows nothing about loading
function OrderList({ orders }) {
  return <ul>{orders.map(o => <li key={o.id}>{o.item}</li>)}</ul>; // renders the list
}

// Create the enhanced version once, at module level
const OrderListWithLoading = withLoading(OrderList); // new component with loading behavior

function App() {
  const orders = [{ id: 1, item: 'Biryani' }, { id: 2, item: 'Dosa' }]; // sample data
  return (
    <div>
      <OrderListWithLoading isLoading={true} orders={orders} />   {/* shows Loading… */}
      <OrderListWithLoading isLoading={false} orders={orders} />  {/* shows the list */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Production HOCs: withAuth + withLogging, forwardRef for refs, displayName, composition helper
import { forwardRef, useEffect } from 'react';  // forwardRef passes the ref to the inner DOM node
import { createRoot } from 'react-dom/client';  // React 18/19 root API

// Fake auth hook: a stand-in for a real session check (returns null when logged out)
function useCurrentUser() {
  return { name: 'Aditya', role: 'seller' };    // pretend the user is logged in as a seller
}

// HOC 1: restricts a component to users with a given role
function withRole(requiredRole) {                // outer function receives configuration
  return function (WrappedComponent) {           // inner function receives the component
    const WithRole = forwardRef(function WithRole(props, ref) { // forwardRef keeps refs working
      const user = useCurrentUser();             // read the current user
      if (!user || user.role !== requiredRole) { // role check
        return <p>Access denied: {requiredRole} only</p>; // blocked UI
      }
      return <WrappedComponent {...props} ref={ref} />; // allowed: forward props AND ref
    });
    WithRole.displayName = `withRole(${WrappedComponent.displayName || WrappedComponent.name})`;
    return WithRole;
  };
}

// HOC 2: logs when a component mounts and unmounts (side effect in the wrapper)
function withLogging(WrappedComponent) {
  const WithLogging = forwardRef(function WithLogging(props, ref) { // same ref handling
    useEffect(() => {                            // runs once after mount
      console.log(`[mount] ${WrappedComponent.displayName || WrappedComponent.name}`); // log on mount
      return () => console.log(`[unmount] ${WrappedComponent.displayName || WrappedComponent.name}`); // log on unmount
    }, []);                                      // empty deps: only mount/unmount
    return <WrappedComponent {...props} ref={ref} />; // render the original
  });
  WithLogging.displayName = `withLogging(${WrappedComponent.displayName || WrappedComponent.name})`;
  return WithLogging;
}

// Compose helper: apply several HOCs from right to left, so the code reads top-down
function compose(...hocs) {
  return (Component) => hocs.reduceRight((acc, hoc) => hoc(acc), Component); // apply each HOC
}

// The original component, with a real DOM ref target
const SellerPayouts = forwardRef(function SellerPayouts({ amount }, ref) {
  return <p ref={ref}>Payout: ₹{amount}</p>;     // ref lands on this <p>
});
SellerPayouts.displayName = 'SellerPayouts';    // explicit name for DevTools

// Build the enhanced component: withRole is the OUTER wrapper, withLogging is INNER
const ProtectedPayouts = compose(
  withRole('seller'),                            // outermost: checks the role first
  withLogging                                    // innermost: wraps SellerPayouts directly
)(SellerPayouts);                                // reduceRight applies the RIGHTMOST hoc first

function App() {
  const ref = { current: null };                 // ref object to receive the DOM node
  return (
    <div>
      <ProtectedPayouts amount={2500} ref={ref} /> {/* ref forwarded through both HOCs */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
// The ref points to the <p> element (ref.current is set after mount).
// Logs: [mount] SellerPayouts, and unmount on removal.
```

---

## 🟠 Real App Integration

In Next.js, a "protected page" is usually handled first by `middleware.js` (a server-side redirect before the page runs). A client-side HOC is useful for UI-only gating, such as hiding a seller panel inside a client page. This sketch uses `useRouter` from `next/navigation` and a placeholder session hook.

```jsx
// lib/with-seller-auth.jsx
'use client';                                            // hooks and router need the client
import { useEffect } from 'react';                       // effect to redirect after mount
import { useRouter } from 'next/navigation';             // App Router navigation hook
import { useSessionUser } from '@/lib/session-client';   // placeholder: your client session hook

export function withSellerAuth(WrappedComponent) {
  function WithSellerAuth(props) {                       // the new component
    const router = useRouter();                          // navigation helper
    const user = useSessionUser();                       // null while logged out (placeholder hook)
    useEffect(() => {                                    // redirect after the render, not during it
      if (user === null) router.replace('/login');       // logged out → login page
    }, [user, router]);
    if (!user || user.role !== 'seller') return null;    // render nothing while redirecting
    return <WrappedComponent {...props} />;              // allowed: forward all props
  }
  WithSellerAuth.displayName = `withSellerAuth(${WrappedComponent.displayName || WrappedComponent.name})`;
  return WithSellerAuth;                                 // enhanced component
}
```

```jsx
// app/seller/payouts/page.jsx
'use client';                                            // the wrapped page is a client component
import { withSellerAuth } from '@/lib/with-seller-auth';

function PayoutsPage() {
  return <h1>Payouts</h1>;                               // only reached for logged-in sellers
}
export default withSellerAuth(PayoutsPage);              // wrap once, at module level
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating the HOC inside a render function (a new component type every render, so the state resets)
✅ **Correct:** Create the enhanced component once, at module level

```jsx
// Wrong: a NEW enhanced component is created on each render → remounts, loses state
function Page() {
  const Enhanced = withLoading(OrderList);       // ❌ new component type every render
  return <Enhanced isLoading={false} orders={[]} />;
}

// Right: create it once outside the component
const EnhancedOrderList = withLoading(OrderList); // ✅ same type every render
function Page() {
  return <EnhancedOrderList isLoading={false} orders={[]} />;
}
```

❌ **Mistake 2:** Not forwarding props or refs, so the wrapped component stops working
✅ **Correct:** Spread `{...props}` and use `forwardRef` when refs must pass through

```jsx
// Wrong: the HOC drops every prop and the ref
function withTheme(Wrapped) {
  return function (props) {
    return <Wrapped theme="dark" />;             // ❌ caller's props are lost
  };
}

// Right: forward everything, and forward the ref
const withTheme = (Wrapped) => forwardRef(function (props, ref) {
  return <Wrapped {...props} theme="dark" ref={ref} />; // ✅ props + ref preserved
});
```

---

## 🧠 Tricky Interview Question

```jsx
import { createRoot } from 'react-dom/client';

// HOC that injects a "user" prop
function withUser(WrappedComponent) {
  return function WithUser(props) {
    const currentUser = { name: 'Injected' };    // value the HOC wants to provide
    return <WrappedComponent {...props} user={currentUser} />; // HOC prop comes AFTER spread
  };
}

function Profile({ user }) {                      // shows whatever "user" it receives
  return <p>{user.name}</p>;
}

const Enhanced = withUser(Profile);

createRoot(document.getElementById('root')).render(
  <Enhanced user={{ name: 'Caller' }} />          // the caller also passes "user"
);
```
**Answer:** The output is `<p>Injected</p>`.
The HOC writes `user={currentUser}` after `{...props}`. In JSX, later props override earlier ones with the same name. So the caller's `user` (`Caller`) is overwritten by the HOC's value (`Injected`). If the HOC wrote `<WrappedComponent user={currentUser} {...props} />` instead, the caller's value would win and the output would be `<p>Caller</p>`. Decide the precedence on purpose: put the HOC's value first when the caller must not override it, or put the spread first when the caller should be able to override the default.

---

## ⚫ Interview Questions + Answers

Q1: What is a Higher Order Component?
A1: A function that takes a component and returns a new component with extra behavior. The original component is not modified. The pattern is `const Enhanced = withSomething(Component)`.

Q2: Why must an HOC forward props?
A2: The wrapped component still needs the props that the caller passed. An HOC adds its own props or behavior, but it must spread the rest (`{...props}`), or the original component loses its data.

Q3: What is the problem with refs and HOCs?
A3: `ref` is not a normal prop; React does not pass it to a function component. An HOC that wraps a component needs `forwardRef` to pass the ref through to the inner DOM node or component. Without it, `ref.current` stays `null`.

Q4: Why set `displayName` on an HOC?
A4: Wrapped components all appear with the same inner name in React DevTools. Setting `displayName` (for example `withAuth(Dashboard)`) makes the component tree readable when debugging.

Q5: What are the trade-offs of HOCs compared with hooks?
A5: HOCs add extra layers to the component tree, can cause prop name collisions, and make types harder to write. Hooks share logic without wrapper layers. HOCs are still useful for route guards, error boundary wrappers (which must be classes) and wrapping third-party components. Topic 66 compares both in detail.

---

## 🔷 When to Use + When Not to Use
✅ **Use HOC when:**
- You must wrap a whole component (route guards, layout wrappers, analytics on a page)
- You work with third-party components that you cannot change
- The existing codebase already uses a large HOC pattern and changing it has no value

❌ **Avoid HOC when:**
- A custom hook can share the same stateful logic inside the component
- You wrap many layers, making the DevTools tree deep and confusing
- The HOC injects props with generic names that may collide (`data`, `user`, `loading`)

---

## 📊 Visual Diagram

```
  withAuth(Dashboard)  →  returns  WithAuth component

  ┌──────────── WithAuth (new component returned by HOC) ─────────────┐
  │   check: is the user logged in?                                   │
  │     ├── NO  → return <Redirect to="/login" />                     │
  │     └── YES → return <Dashboard {...props} />  ← original, unchanged │
  └───────────────────────────────────────────────────────────────────┘

  Composition (compose):
  ProtectedPayouts = withRole('seller') ( withLogging ( SellerPayouts ) )

  Render tree in DevTools:
     withRole(withLogging(SellerPayouts))
       └── withLogging(SellerPayouts)
             └── SellerPayouts  → <p>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HOC | Function that takes and returns a component | Component लेकर component लौटाने वाला function |
| Wrapped component | Original component inside the HOC | HOC के अंदर का original component |
| Prop forwarding | Passing caller props to the wrapped component | Caller के props को wrapped component तक भेजना |
| forwardRef | Passes a ref through a function component | Function component से ref आगे भेजना |
| displayName | Readable name shown in DevTools | DevTools में दिखने वाला नाम |
| compose | Applies several HOCs in one line | कई HOCs को एक लाइन में लगाना |
| Prop collision | Two sources setting the same prop | एक ही prop को दो जगह से सेट होना |
| Wrapper hell | Deeply nested wrappers in the tree | Tree में गहरे नेस्ट हुए wrappers |

---

## ⚡ 3-Line Summary
**English:**
1. A HOC is a function that takes a component and returns an enhanced component with extra behavior.
2. Always forward props, use `forwardRef` for refs, set `displayName`, and create the enhanced component at module level.
3. Hooks now cover most sharing needs; HOCs remain useful for route guards and wrapping third-party components.

**Hindi:**
1. HOC एक function है जो component लेता है और extra behavior वाला नया component लौटाता है।
2. Props हमेशा आगे भेजो, refs के लिए `forwardRef` लगाओ, `displayName` सेट करो, और enhanced component module level पर बनाओ।
3. ज़्यादातर sharing अब hooks से होती है; route guards और third-party components को wrap करने में HOC अब भी काम आता है।

---

## ➡️ Next Topic
**66. HOC vs Custom Hooks** — वही logic एक बार HOC से और एक बार custom hook से लिखकर तुलना करना, और यह समझना कि कब कौन-सा तरीका बेहतर है।
