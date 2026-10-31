---

# Q158. Complete Pub/Sub System
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks for a topic-based pub/sub where publisher and subscriber don't know each other.

```javascript
const PubSub = {
  topics: new ____(),                            // topic -> Set of handlers
  subscribe(topic, fn) {
    if (!this.topics.has(topic)) this.topics.____(topic, new Set());
    this.topics.get(topic).____(fn);             // add handler
    return () => this.topics.get(topic).____(fn); // unsubscribe
  },
  publish(topic, data) {
    (this.topics.get(topic) ____ []).forEach(fn => fn(data)); // notify
  },
};
```

---

## 💡 Quick Concept (2 lines only)
Pub/Sub decouples senders from receivers via named topics. Publishers send to a topic; all its subscribers get the data.
हिंदी: Pub/Sub में publisher और subscriber एक-दूसरे को नहीं जानते, बीच में topic होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const PubSub = {
  topics: new Map(),                                      // blank 1: topic -> Set
  subscribe(topic, fn) {
    if (!this.topics.has(topic)) this.topics.set(topic, new Set()); // blank 2: create set
    this.topics.get(topic).add(fn);                       // blank 3: register handler
    return () => this.topics.get(topic).delete(fn);       // blank 4: unsubscribe
  },
  publish(topic, data) {
    (this.topics.get(topic) ?? []).forEach(fn => fn(data)); // blank 5: safe if no subscribers
  },
};

// ============================================
// TEST CASES
// ============================================

const off = PubSub.subscribe('news', d => console.log('got', d)); // subscriber 1
PubSub.subscribe('news', d => console.log('also', d));            // subscriber 2
PubSub.publish('news', 'hello');   // Expected: got hello / also hello
off();                             // remove first
PubSub.publish('news', 'bye');     // Expected: also bye
PubSub.publish('none', 'x');       // Expected: (nothing, no error)
```

---

## 🔍 Why This Works (3 lines max)
A Map keyed by topic holds Sets of handlers, so duplicates are avoided and removal is O(1). `?? []` avoids errors for topics nobody listens to.
हिंदी: Map में topic के हिसाब से handlers का Set रहता है, और `?? []` से खाली topic पर error नहीं आता।

---

## ⚡ Alternative Solution
```javascript
// Browser built-in
const bus = new EventTarget();
bus.addEventListener('ping', () => console.log('ping'));
bus.dispatchEvent(new Event('ping')); // ping
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: publish() on unknown topic crashes with undefined.forEach
// ✅ Correct: default to an empty array
```

---

## 🎯 Interview Tip (1 line)
Say: "Pub/Sub uses a central broker (topics); observer has direct subject-to-observer links."

---

## 🔗 Related Questions
→ Q097 (pub/sub) | Q150 (observable) | Q187 (event bus) | Q273 (pub/sub pattern)
