---

# Q139. Fix Race Condition Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
A user types "a" then "ab". The slow response for "a" arrives AFTER the one for "ab" and overwrites the result. Fix it so only the latest request wins.

```javascript
// BUGGY CODE:
let result = '';
const delay = { a: 50, ab: 10 };
const search = (q) => new Promise(r => setTimeout(() => r('results for ' + q), delay[q]));

async function onType(q) {
  result = await search(q);   // older request may finish last
}
onType('a'); onType('ab');
setTimeout(() => console.log(result), 100); // results for a (wrong)
```

---

## 💡 Quick Concept (2 lines only)
Async responses can arrive out of order. Tag each request with an id and ignore responses that are not the latest.
हिंदी: responses उल्टे क्रम में आ सकते हैं — हर request को id दो और सिर्फ latest की value रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

let result = '';                                   // Step 1: shared output
let latestId = 0;                                  // Step 2: counter of newest request
const delay = { a: 50, ab: 10 };                   // 'a' is slower
const search = (q) => new Promise(r => setTimeout(() => r('results for ' + q), delay[q]));

async function onType(q) {
  const myId = ++latestId;                         // Step 3: claim an id for this call
  const data = await search(q);                    // wait for response
  if (myId !== latestId) return;                   // Step 4 (FIX): stale response, ignore
  result = data;                                   // only latest updates state
}

// ============================================
// TEST CASES
// ============================================

onType('a');                                       // slow, older
onType('ab');                                      // fast, newest
setTimeout(() => console.log(result), 100);        // Expected: results for ab
```

---

## 🔍 Why This Works (3 lines max)
Each call remembers its own id; after awaiting, it checks whether a newer call started. Stale responses are dropped so the last request always wins.
हिंदी: हर call अपनी id याद रखती है और पुरानी response को छोड़ देती है।

---

## ⚡ Alternative Solution
```javascript
// AbortController cancels the previous fetch (real apps)
let ctrl;
function run(q) {
  ctrl?.abort();                       // cancel old request
  ctrl = new AbortController();        // fresh controller
  // fetch(url + q, { signal: ctrl.signal });
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assuming responses return in the order requests were sent
// ✅ Correct: version token, AbortController, or debounce the input
```

---

## 🎯 Interview Tip (1 line)
Say: "Network order is not guaranteed — use a request id or AbortController, like React useEffect cleanup."

---

## 🔗 Related Questions
→ Q127 (async state update) | Q081 (debounce) | Q181 (search with debounce) | Q219 (abort fetch)
