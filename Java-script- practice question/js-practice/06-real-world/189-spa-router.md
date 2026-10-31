---

# Q189. Build Router (SPA)
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build a client-side router: register routes with params (`/user/:id`), `navigate(path)` pushes history and runs the matching handler with `{ params, query }`, with a 404 fallback. Inject `history` so it is testable in Node.

```javascript
router.add('/user/:id', ({ params }) => render(params.id));
router.navigate('/user/42?tab=info');
```

---

## 💡 Quick Concept (2 lines only)
Convert each route pattern to a RegExp, match the path, extract params, and call `history.pushState` (+ listen to `popstate`).
हिंदी: Route pattern को regex बनाओ, URL match करो, params निकालो और page reload के बिना handler चलाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Router {
  constructor(history) {
    this.history = history;                      // Step 1: injected (window.history in browser)
    this.routes = [];                            // list of { regex, keys, handler }
    this.notFound = () => console.log('404');    // default fallback
  }

  add(pattern, handler) {
    const keys = [];                             // param names, e.g. ['id']
    const source = pattern.replace(/:(\w+)/g, (_, k) => { keys.push(k); return '([^/]+)'; }); // Step 2: :id -> capture group
    this.routes.push({ regex: new RegExp(`^${source}$`), keys, handler }); // store compiled route
    return this;                                 // chaining
  }

  navigate(url) {
    this.history.pushState({}, '', url);         // Step 3: change address bar (no reload)
    this.resolve(url);                           // run matching handler
  }

  resolve(url) {
    const [path, qs = ''] = url.split('?');      // Step 4: split path and query
    const query = Object.fromEntries(new URLSearchParams(qs)); // parse query string
    for (const { regex, keys, handler } of this.routes) {
      const m = path.match(regex);               // try each route
      if (m) {
        const params = Object.fromEntries(keys.map((k, i) => [k, m[i + 1]])); // Step 5: build params
        return handler({ params, query });       // call handler
      }
    }
    return this.notFound(path);                  // nothing matched
  }
}

// ============================================
// TEST CASES
// ============================================

const fakeHistory = { pushState: (s, t, url) => console.log('push', url) }; // stand-in for window.history
const router = new Router(fakeHistory);
router
  .add('/', () => console.log('home'))
  .add('/user/:id', ({ params, query }) => console.log('user', params.id, query))
  .add('/post/:pid/comment/:cid', ({ params }) => console.log(params));

router.navigate('/');                            // Expected: push /  then  home
router.navigate('/user/42?tab=info');            // Expected: push /user/42?tab=info  then  user 42 { tab: 'info' }
router.navigate('/post/7/comment/3');            // Expected: push ...  then  { pid: '7', cid: '3' }
router.navigate('/nope');                        // Expected: push /nope  then  404
// Browser wiring: window.addEventListener('popstate', () => router.resolve(location.pathname));
```

---

## 🔍 Why This Works (3 lines max)
`pushState` changes the URL without a reload, and the router re-renders based on the matched pattern. `popstate` handles back/forward buttons.
हिंदी: pushState URL बदलता है बिना reload के, और regex से सही handler और params मिल जाते हैं।

---

## ⚡ Alternative Solution
```javascript
// Hash-based router (works without server config)
window.addEventListener('hashchange', () => router.resolve(location.hash.slice(1) || '/'));
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: <a href> causes full page reload, and no popstate handling
link.href = '/user/1';

// ✅ Correct: intercept click, use pushState, and handle popstate
link.addEventListener('click', (e) => { e.preventDefault(); router.navigate(link.getAttribute('href')); });
```

---

## 🎯 Interview Tip (1 line)
Explain history API vs hash routing, and why servers need a catch-all to index.html for history mode.

---

## 🔗 Related Questions
→ Q197 (URL parser) | Q198 (query string builder) | Q188 (state manager) | Q187 (event bus)
