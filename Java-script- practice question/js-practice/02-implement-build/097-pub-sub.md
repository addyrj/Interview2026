---

# Q097. Implement Pub/Sub
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `PubSub` class with `subscribe(topic, cb)` (returns an unsubscribe function), `publish(topic, data)`, and `unsubscribe(topic, cb)`. Publishers and subscribers don't know each other.

```javascript
const unsub = bus.subscribe('news', console.log);
bus.publish('news', 'hello');
```

---

## 💡 Quick Concept (2 lines only)
Store callbacks per topic in a Map of Sets. Publishing calls every callback of that topic.
हिंदी: Pub/Sub में publisher और subscriber एक-दूसरे को नहीं जानते, बीच में topic होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Map<topic, Set<callback>>
// Step 2: subscribe adds callback and returns unsubscribe fn
// Step 3: publish calls all callbacks of the topic
// Step 4: unsubscribe removes callback

class PubSub {
  constructor() {
    this.topics = new Map();                         // topic -> Set of callbacks
  }

  subscribe(topic, cb) {
    if (!this.topics.has(topic)) this.topics.set(topic, new Set()); // create set if new
    this.topics.get(topic).add(cb);                  // add callback
    return () => this.unsubscribe(topic, cb);        // handy unsubscribe function
  }

  unsubscribe(topic, cb) {
    const subs = this.topics.get(topic);             // get callbacks
    if (!subs) return;                               // nothing to remove
    subs.delete(cb);                                 // remove callback
    if (subs.size === 0) this.topics.delete(topic);  // cleanup empty topic
  }

  publish(topic, data) {
    const subs = this.topics.get(topic);             // callbacks for topic
    if (!subs) return 0;                             // no subscribers
    [...subs].forEach((cb) => cb(data));             // copy first so unsubscribing inside is safe
    return subs.size;                                // number notified
  }
}

// ============================================
// TEST CASES
// ============================================

const bus = new PubSub();                            // create bus
const a = (d) => console.log('A got', d);            // subscriber A
const b = (d) => console.log('B got', d);            // subscriber B

const unsubA = bus.subscribe('news', a);
bus.subscribe('news', b);

bus.publish('news', 'v1');   // Expected: A got v1
                             // Expected: B got v1
unsubA();                    // A leaves
bus.publish('news', 'v2');   // Expected: B got v2
console.log(bus.publish('other', 1)); // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
A Set avoids duplicate callbacks and gives O(1) removal. Returning an unsubscribe function prevents memory leaks.
हिंदी: Set से duplicate नहीं होते और unsubscribe function से memory leak रुकता है।

---

## ⚡ Alternative Solution
```javascript
// Minimal object-based version
const events = {};                                       // topic -> array
const sub = (t, cb) => (events[t] ||= []).push(cb);      // add
const pub = (t, d) => (events[t] || []).forEach(cb => cb(d)); // call all

sub('x', d => console.log('x:', d));
pub('x', 7); // Expected: x: 7
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using an array and anonymous callbacks — can't unsubscribe later
bus.subscribe('news', (d) => console.log(d));
bus.unsubscribe('news', (d) => console.log(d)); // different function reference, not removed

// ✅ Correct: keep the reference or use the returned unsubscribe function
```

---

## 🎯 Interview Tip (1 line)
Differentiate from Observer: Pub/Sub has a broker (topics) so publisher and subscriber are fully decoupled.

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q098 (observable) | Q273 (pub/sub pattern) | Q187 (event bus)
