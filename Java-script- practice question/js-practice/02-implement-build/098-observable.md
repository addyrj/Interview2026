---

# Q098. Implement Observable
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement a minimal `Observable` (RxJS-style) with `subscribe(observer)` returning a subscription with `unsubscribe()`, plus a `map` operator. The producer function receives an observer with `next`, `error`, `complete`.

```javascript
const obs = new Observable(o => { o.next(1); o.next(2); o.complete(); });
obs.map(x => x * 2).subscribe(console.log);
```

---

## 💡 Quick Concept (2 lines only)
An Observable is a lazy producer: nothing runs until someone subscribes. Operators like `map` return a new Observable wrapping the old one.
हिंदी: Observable lazy होता है — subscribe करने पर ही data बहना शुरू होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: constructor stores the producer function
// Step 2: subscribe builds a safe observer and runs producer
// Step 3: unsubscribe stops further events and runs cleanup
// Step 4: map returns a new Observable

class Observable {
  constructor(producer) {
    this.producer = producer;                       // function(observer) => cleanup?
  }

  subscribe(observerOrNext) {
    const observer = typeof observerOrNext === 'function'
      ? { next: observerOrNext }                    // allow subscribe(fn)
      : observerOrNext;                             // or full observer object
    let closed = false;                             // stops events after unsubscribe/complete
    let cleanup;                                    // teardown from producer

    const safe = {                                  // guarded observer
      next: (v) => { if (!closed && observer.next) observer.next(v); },
      error: (e) => { if (!closed) { closed = true; observer.error && observer.error(e); } },
      complete: () => { if (!closed) { closed = true; observer.complete && observer.complete(); } },
    };

    cleanup = this.producer(safe);                  // start the producer
    return {
      unsubscribe: () => {                          // subscription handle
        closed = true;                              // ignore future events
        if (typeof cleanup === 'function') cleanup(); // run teardown
      },
    };
  }

  map(fn) {
    return new Observable((observer) =>             // wrap source
      this.subscribe({
        next: (v) => observer.next(fn(v)),          // transform each value
        error: (e) => observer.error(e),            // forward error
        complete: () => observer.complete(),        // forward complete
      }).unsubscribe                                // returned as cleanup
    );
  }
}

// ============================================
// TEST CASES
// ============================================

const nums = new Observable((o) => { o.next(1); o.next(2); o.next(3); o.complete(); });

nums.map((x) => x * 10).subscribe({
  next: (v) => console.log('value', v),   // Expected: value 10
                                          // Expected: value 20
                                          // Expected: value 30
  complete: () => console.log('done'),    // Expected: done
});

const ticker = new Observable((o) => {               // interval producer
  let i = 0;
  const id = setInterval(() => o.next(++i), 20);     // emit every 20ms
  return () => { clearInterval(id); console.log('cleaned'); }; // teardown
});
const sub = ticker.subscribe((v) => console.log('tick', v)); // Expected: tick 1, tick 2
setTimeout(() => sub.unsubscribe(), 50);              // Expected: cleaned
```

---

## 🔍 Why This Works (3 lines max)
The producer runs only on subscribe, giving laziness. The `closed` flag guarantees no events after unsubscribe, and cleanup frees resources like timers.
हिंदी: Producer सिर्फ subscribe पर चलता है, और unsubscribe पर cleanup से timers बंद हो जाते हैं।

---

## ⚡ Alternative Solution
```javascript
// Simple "Subject" style (hot observable): shares one source with many observers
class Subject {
  constructor() { this.observers = new Set(); }          // all listeners
  subscribe(fn) { this.observers.add(fn); return () => this.observers.delete(fn); }
  next(v) { this.observers.forEach((fn) => fn(v)); }     // broadcast
}
const s = new Subject();
s.subscribe((v) => console.log('S1', v));
s.next('hi');  // Expected: S1 hi
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: running producer in the constructor — not lazy, runs even without subscribers
constructor(producer) { producer(this.observer); }

// ✅ Correct: store producer; run it inside subscribe()
```

---

## 🎯 Interview Tip (1 line)
Highlight "lazy, cancellable, composable" vs Promise (eager, one value, not cancellable).

---

## 🔗 Related Questions
→ Q096 (event emitter) | Q097 (pub/sub) | Q150 (complete observable) | Q263 (observer pattern)
