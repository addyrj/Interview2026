---

# Q197. Build URL Parser
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `parseUrl(url)` returning `{ protocol, hostname, port, pathname, query, hash }` (query as an object, repeated keys become arrays) — without using the `URL` class.

```javascript
parseUrl('https://a.com:8080/p/q?x=1&y=2#top');
```

---

## 💡 Quick Concept (2 lines only)
One regex splits the URL into parts; then split the query on `&` and `=` and decode each piece.
हिंदी: एक regex से URL के हिस्से अलग करो, फिर query को `&` और `=` से तोड़कर decode करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function parseQuery(qs) {
  const out = {};                                // result object
  if (!qs) return out;                           // empty query
  for (const part of qs.split('&')) {            // Step 1: each key=value
    if (!part) continue;                         // skip empty (a=1&&b=2)
    const [k, v = ''] = part.split('=');         // value optional
    const key = decodeURIComponent(k.replace(/\+/g, ' ')); // '+' means space
    const val = decodeURIComponent(v.replace(/\+/g, ' '));
    if (key in out) out[key] = [].concat(out[key], val);   // Step 2: repeated key -> array
    else out[key] = val;
  }
  return out;
}

function parseUrl(url) {
  const re = /^(\w+):\/\/([^/:?#]+)(?::(\d+))?([^?#]*)(?:\?([^#]*))?(?:#(.*))?$/; // Step 3: master regex
  const m = url.match(re);
  if (!m) return null;                           // invalid URL
  const [, protocol, hostname, port, pathname, query, hash] = m; // Step 4: destructure groups
  return {
    protocol: protocol + ':',
    hostname,
    port: port || '',
    pathname: pathname || '/',
    query: parseQuery(query),
    hash: hash ? '#' + hash : '',
  };
}

// ============================================
// TEST CASES
// ============================================

console.log(parseUrl('https://a.com:8080/p/q?x=1&y=hello+world#top'));
// Expected: { protocol: 'https:', hostname: 'a.com', port: '8080', pathname: '/p/q',
//             query: { x: '1', y: 'hello world' }, hash: '#top' }
console.log(parseUrl('http://site.org'));
// Expected: { protocol: 'http:', hostname: 'site.org', port: '', pathname: '/', query: {}, hash: '' }
console.log(parseUrl('https://a.com/s?tag=js&tag=node').query);
// Expected: { tag: [ 'js', 'node' ] }
console.log(parseUrl('not a url'));              // Expected: null
```

---

## 🔍 Why This Works (3 lines max)
Each regex group matches one URL part, optional parts use `?`, and the query step handles decoding plus repeated keys. Returning `null` signals an invalid URL.
हिंदी: हर regex group URL का एक हिस्सा पकड़ता है, और query वाला step decoding व repeated keys संभालता है।

---

## ⚡ Alternative Solution
```javascript
// Built-in (preferred in real code)
const u = new URL('https://a.com:8080/p/q?x=1&y=2#top'); // throws on invalid URL
console.log(u.hostname, u.port, u.pathname, u.hash);     // a.com 8080 /p/q #top
console.log(Object.fromEntries(u.searchParams));         // { x: '1', y: '2' }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: naive split breaks on '=' inside values and skips decoding
const [k, v] = pair.split('=');                  // "a=b=c" loses "=c"

// ✅ Correct: decodeURIComponent, handle '+', and use only the first '=' as separator
```

---

## 🎯 Interview Tip (1 line)
Say you would use `new URL()` / `URLSearchParams` in production, but you can explain the parsing by hand.

---

## 🔗 Related Questions
→ Q189 (SPA router) | Q198 (query string builder) | Q074 (get value by path) | Q196 (cookie manager)
