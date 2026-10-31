---

# Q188. Build State Manager
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a mini Redux: `createStore(reducer, initialState)` with `getState`, `dispatch(action)`, `subscribe(listener)` (returns unsubscribe). State must change only through reducers.

```javascript
const store = createStore(reducer, { count: 0 });
store.dispatch({ type: 'inc' });
```

---

## 💡 Quick Concept (2 lines only)
State lives in a closure; `dispatch` runs `reducer(state, action)` to produce a new state, then notifies subscribers.
हिंदी: State closure में रहती है; dispatch पर reducer नया state बनाता है और listeners को खबर मिलती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function createStore(reducer, initialState) {
  let state = initialState;                      // Step 1: private state (closure)
  const listeners = new Set();                   // subscribers

  const getState = () => state;                  // Step 2: read-only access

  const dispatch = (action) => {
    state = reducer(state, action);              // Step 3: compute NEW state
    listeners.forEach((l) => l(state));          // Step 4: notify everyone
    return action;                               // return action like Redux
  };

  const subscribe = (listener) => {
    listeners.add(listener);                     // Step 5: register
    return () => listeners.delete(listener);     // unsubscribe function
  };

  dispatch({ type: '@@INIT' });                  // let reducer set defaults
  return { getState, dispatch, subscribe };      // public API
}

// ============================================
// TEST CASES
// ============================================

function reducer(state = { count: 0 }, action) {
  switch (action.type) {
    case 'inc': return { ...state, count: state.count + 1 };            // new object, no mutation
    case 'add': return { ...state, count: state.count + action.payload };
    default: return state;                       // unknown action -> same state
  }
}

const store = createStore(reducer, { count: 0 });
const unsub = store.subscribe((s) => console.log('state ->', s.count)); // log on change

store.dispatch({ type: 'inc' });                 // Expected: state -> 1
store.dispatch({ type: 'add', payload: 5 });     // Expected: state -> 6
unsub();                                         // stop listening
store.dispatch({ type: 'inc' });                 // (no log)
console.log(store.getState());                   // Expected: { count: 7 }
```

---

## 🔍 Why This Works (3 lines max)
The reducer is a pure function returning a new object, so changes are predictable and detectable by reference. Subscribers are notified after every dispatch.
हिंदी: Reducer हमेशा नया object लौटाता है, इसलिए state predictable रहती है।

---

## ⚡ Alternative Solution
```javascript
// Tiny setState-style store (like Zustand)
function createSimpleStore(initial) {
  let state = initial, subs = new Set();         // state + subscribers
  return {
    get: () => state,                            // read
    set: (patch) => { state = { ...state, ...patch }; subs.forEach((f) => f(state)); }, // merge + notify
    subscribe: (f) => (subs.add(f), () => subs.delete(f)),
  };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: mutating state -> same reference, subscribers/React can't detect change
case 'inc': state.count++; return state;

// ✅ Correct: return a new object
case 'inc': return { ...state, count: state.count + 1 };
```

---

## 🎯 Interview Tip (1 line)
Stress immutability, pure reducers, and that React re-renders by comparing references.

---

## 🔗 Related Questions
→ Q097 (pub/sub) | Q187 (event bus) | Q200 (undo/redo) | Q263 (observer pattern)
