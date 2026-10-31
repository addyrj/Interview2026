---

# Q196. Build Cookie Manager
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `createCookieManager(doc)` with `set(name, value, { days, path })`, `get(name)`, `remove(name)`. Values must be URL-encoded. Inject `doc` (`document` in browsers) so it runs in Node with a fake.

```javascript
const cookies = createCookieManager(document);
cookies.set('theme', 'dark', { days: 7 });
```

---

## 💡 Quick Concept (2 lines only)
`document.cookie` is a weird string API: assigning adds ONE cookie, reading returns ALL as `a=1; b=2`. Parse by splitting on `; `.
हिंदी: document.cookie में assign करने से एक cookie जुड़ती है, और पढ़ने पर सब मिलती हैं — split करके ढूँढो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function createCookieManager(doc) {
  return {
    set(name, value, { days, path = '/' } = {}) {
      let str = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`; // Step 1: encode name=value
      if (days) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();  // Step 2: days -> UTC date
        str += `; expires=${expires}`;           // add expiry
      }
      str += `; path=${path}`;                   // Step 3: scope of cookie
      doc.cookie = str;                          // Step 4: assigning ADDS/updates one cookie
    },
    get(name) {
      const pairs = doc.cookie ? doc.cookie.split('; ') : []; // Step 5: split all cookies
      for (const pair of pairs) {
        const idx = pair.indexOf('=');           // first '=' separates name/value
        if (decodeURIComponent(pair.slice(0, idx)) === name) {
          return decodeURIComponent(pair.slice(idx + 1)); // decode value
        }
      }
      return null;                               // not found
    },
    remove(name, path = '/') {
      doc.cookie = `${encodeURIComponent(name)}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=${path}`; // past date deletes
    },
  };
}

// ============================================
// TEST CASES
// ============================================

// Fake document that mimics browser cookie behaviour
const fakeDoc = {
  jar: new Map(),                                // name -> value
  set cookie(str) {
    const [pair, ...attrs] = str.split('; ');    // first part = name=value
    const idx = pair.indexOf('=');
    const name = pair.slice(0, idx), value = pair.slice(idx + 1);
    const exp = attrs.find((a) => a.startsWith('expires='));
    const expired = exp && new Date(exp.slice(8)).getTime() < Date.now(); // past date = delete
    if (expired) this.jar.delete(name); else this.jar.set(name, value);
  },
  get cookie() {
    return [...this.jar].map(([n, v]) => `${n}=${v}`).join('; '); // "a=1; b=2"
  },
};

const cookies = createCookieManager(fakeDoc);
cookies.set('theme', 'dark', { days: 7 });
cookies.set('user name', 'Adi & Co');            // needs encoding
console.log(cookies.get('theme'));               // Expected: dark
console.log(cookies.get('user name'));           // Expected: Adi & Co
console.log(fakeDoc.cookie);                     // Expected: theme=dark; user%20name=Adi%20%26%20Co
cookies.remove('theme');
console.log(cookies.get('theme'));               // Expected: null
```

---

## 🔍 Why This Works (3 lines max)
Encoding prevents `;` or `=` in values from breaking the cookie string. Deleting works by re-setting the same cookie with an expiry date in the past.
हिंदी: Encode करने से special characters नहीं टूटते, और पुरानी expiry date set करके cookie delete होती है।

---

## ⚡ Alternative Solution
```javascript
// Modern async API (Chromium browsers)
await cookieStore.set({ name: 'theme', value: 'dark', expires: Date.now() + 864e5 });
const c = await cookieStore.get('theme');        // { name: 'theme', value: 'dark', ... }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: `document.cookie = {a:1}` or expecting assign to replace ALL cookies;
// also storing auth tokens in JS-readable cookies
document.cookie = 'token=secret';

// ✅ Correct: server sets tokens with HttpOnly; Secure; SameSite=Lax. JS cookies only for non-sensitive prefs.
```

---

## 🎯 Interview Tip (1 line)
Know cookie flags: HttpOnly, Secure, SameSite, Path, Domain, Max-Age and cookie vs localStorage differences.

---

## 🔗 Related Questions
→ Q195 (local storage wrapper) | Q237 (localStorage wrapper) | Q197 (URL parser) | Q198 (query string builder)
