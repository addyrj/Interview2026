---

# Q273. Pub/Sub Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `PubSub` broker with `subscribe(topic, fn)`, `publish(topic, data)` and unsubscribe, where publishers and subscribers don't know each other.

---

## 💡 Quick Concept (2 lines only)
Publishers send messages to named topics on a broker; subscribers listen to topics. Neither knows the other.
हिंदी: Publisher और subscriber एक-दूसरे को नहीं जानते, बीच में broker topic के हिसाब से message बांटता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: topics = Map<topic, Set<fn>>
// Step 2: subscribe adds fn, returns unsubscribe
// Step 3: publish calls all handlers for that topic

class PubSub {
  #topics = new Map();                          // topic -> handlers

  subscribe(topic, fn) {
    if (!this.#topics.has(topic)) this.#topics.set(topic, new Set()); // create bucket
    this.#topics.get(topic).add(fn);            // register handler
    return () => this.#topics.get(topic)?.delete(fn); // unsubscribe handle
  }

  publish(topic, data) {
    this.#topics.get(topic)?.forEach((fn) => fn(data)); // fire if anyone listens
  }
}

// ============================================
// TEST CASES
// ============================================

const bus = new PubSub();                                  // broker
const off = bus.subscribe('order', (d) => console.log('email:', d)); // subscriber 1
bus.subscribe('order', (d) => console.log('sms:', d));     // subscriber 2
bus.subscribe('login', (d) => console.log('audit:', d));   // different topic
bus.publish('order', '#42');                               // Expected: email: #42
                                                           // Expected: sms: #42
off();                                                     // unsubscribe email
bus.publish('order', '#43');                               // Expected: sms: #43
bus.publish('nobody', 1);                                  // Expected: (nothing printed)
```

---

## 🔍 Why This Works (3 lines max)
The broker maps topic names to handler sets, so publish only reaches interested parties. Decoupling is by topic string.
हिंदी: Topic के नाम से handlers चुने जाते हैं, इसलिए दोनों तरफ का code अलग रहता है।

---

## ⚡ Alternative Solution
```javascript
// Using EventTarget (built into Node 15+ and browsers)
const t = new EventTarget();                                    // broker
t.addEventListener('hi', (e) => console.log(e.detail));         // subscribe
t.dispatchEvent(new CustomEvent('hi', { detail: 'yo' }));       // Expected: yo
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting unsubscribe in components → leaks and duplicate calls
// ✅ Correct: call the returned unsubscribe on cleanup (useEffect return)
```

---

## 🎯 Interview Tip (1 line)
Explain difference from Observer: Pub/Sub has a broker/topic layer, so it is more decoupled but harder to trace.

---

## 🔗 Related Questions
→ Q263 (Observer) | Q097 (Pub/sub implement) | Q187 (Event bus)
