# 200. Build Simple State Manager
# हिंदी में: Simple State Manager बनाना — Store, Reducer, Dispatch, Subscribe और Memoized Selectors

---

## 🔵 Simple Definition (English)
A state manager keeps the app's data in one object, called the store. The only way to change it is to dispatch an action, which a pure reducer function turns into the next state. Components subscribe to the store and re-render when it changes. Interviews ask you to build this from scratch, because it tests closures, immutability, listener management, and the difference between reading and changing state.

## 🔵 सरल परिभाषा (Hindi)
State manager app का सारा data एक object में रखता है, जिसे store कहते हैं। State बदलने का एक ही तरीका है: action dispatch करना, और एक pure reducer function उसे अगला state बनाता है। Components store को subscribe करते हैं और state बदलने पर फिर से render होते हैं। Interview में इसे शून्य से बनाने को कहा जाता है, क्योंकि इससे closures, immutability, listeners का प्रबंधन, और state पढ़ने व बदलने का फ़र्क परखा जाता है।

---

## 🔴 Problem it Solves
**Problem Statement:** Build a store with `getState`, `dispatch`, and `subscribe`. Changes go through a reducer. Subscribers are called after each dispatch, and `subscribe` returns an unsubscribe function. Add a memoized selector that recomputes only when the data it reads changes.

When many components share data, such as a cart count in the header and the cart total on the checkout page, passing props through every level becomes messy. Mutating shared objects in place causes the worst kind of bug: the screen does not update, or it updates in some places and not others. A store with immutable updates gives one source of truth and a predictable flow.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** एक store बनाओ जिसमें `getState`, `dispatch` और `subscribe` हों। बदलाव reducer से होकर जाएँ। हर dispatch के बाद subscribers बुलाए जाएँ, और `subscribe` एक unsubscribe function लौटाए। एक memoized selector जोड़ो जो तभी दोबारा गणना करे जब उसका डेटा बदले।

जब कई components एक ही data बाँटते हैं, जैसे header में cart count और checkout page पर cart total, तो हर level पर props भेजना उलझन भरा हो जाता है। Shared object को सीधे बदलना सबसे बुरे bug देता है: screen अपडेट नहीं होती, या कुछ जगह होती है और कुछ जगह नहीं। Immutable updates वाला store एक सच्चा स्रोत और अनुमानित flow देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → The store holds one `state` variable. Nothing else holds the data.
Step 2 → `getState()` returns the current state, and components read it from here.
Step 3 → `dispatch(action)` calls `reducer(state, action)`, which returns the new state.
Step 4 → The reducer never mutates the old state; it returns a new object with the changes.
Step 5 → After the state changes, every subscriber is called with the new state.
Step 6 → `subscribe(fn)` returns `unsubscribe`, which removes `fn` from the list.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Store में एक `state` variable होता है। Data कहीं और नहीं रहता।
Step 2 → `getState()` मौजूदा state लौटाता है, components यहीं से पढ़ते हैं।
Step 3 → `dispatch(action)` `reducer(state, action)` बुलाता है, जो नया state लौटाता है।
Step 4 → Reducer पुराने state को कभी नहीं बदलता; वह बदलाव के साथ नया object लौटाता है।
Step 5 → State बदलने के बाद हर subscriber को नया state देकर बुलाया जाता है।
Step 6 → `subscribe(fn)` एक `unsubscribe` लौटाता है, जो `fn` को list से हटाता है।

---

## 🟡 Real World Example
Zomato's cart keeps the items in one store. The header badge, the cart page, and the checkout total all subscribe to it. When the user adds a dish, one action updates the store, and all three views update. Redux, Zustand, and Vuex all use this same pattern.

Scenario: A Flipkart cart has a coupon field. When the user types a coupon, the store gets a `SET_COUPON` action. The product list does not need to re-render, and a memoized selector for the total keeps its cached value, because the `items` reference did not change.

## 🟡 Real Example Hindi mein
Zomato का cart सभी items एक store में रखता है। Header का badge, cart page और checkout का total, तीनों उसे subscribe करते हैं। User जब एक dish जोड़ता है, तो एक action store को अपडेट करता है, और तीनों views बदल जाते हैं। Redux, Zustand और Vuex इसी pattern पर चलते हैं।

उदाहरण: Flipkart के cart में coupon field है। User coupon लिखता है, तो store को `SET_COUPON` action मिलता है। Product list को दोबारा render होने की ज़रूरत नहीं, और total का memoized selector अपना cached value रखता है, क्योंकि `items` का reference नहीं बदला।

---

## 💻 Code Example — Basic
```javascript
// Run with: node file.js

// createStore: one state variable, read with getState, changed only with dispatch
function createStore(reducer, initialState) {
  let state = initialState;                       // the single source of truth
  const listeners = [];                           // functions to call after every change
  return {
    getState: () => state,                        // read the current state
    dispatch(action) {                            // the only way to change the state
      state = reducer(state, action);             // the reducer returns the next state
      listeners.slice().forEach((fn) => fn(state)); // call a copy of the list, so unsubscribing is safe
      return action;                              // return the action, which is handy for logging
    },
    subscribe(fn) {                               // register a listener
      listeners.push(fn);                         // add it to the list
      return () => {                              // the unsubscribe function
        const i = listeners.indexOf(fn);          // find this listener's position
        if (i !== -1) listeners.splice(i, 1);     // remove it; ignore a second call
      };
    },
  };
}

// reducer: a pure function that returns a NEW object for each change, never mutates the old one
function cartReducer(state, action) {
  switch (action.type) {
    case "ADD_ITEM":
      return { ...state, items: [...state.items, action.item] }; // copy the array and add the item
    case "REMOVE_ITEM":
      return { ...state, items: state.items.filter((i) => i.id !== action.id) }; // keep all but one
    case "CLEAR":
      return { ...state, items: [] };               // empty the cart
    default:
      return state;                                 // unknown action: the same state object comes back
  }
}

// selector: reads a value from the state, here the total price of all items
const total = (state) => state.items.reduce((sum, item) => sum + item.price, 0); // add up the prices

const store = createStore(cartReducer, { items: [] }); // start with an empty cart
const unsubscribe = store.subscribe((s) => console.log("items now:", s.items.length)); // a listener

store.dispatch({ type: "ADD_ITEM", item: { id: 1, name: "Chai", price: 20 } }); // Expected output: items now: 1
store.dispatch({ type: "ADD_ITEM", item: { id: 2, name: "Samosa", price: 15 } }); // Expected output: items now: 2
console.log("total:", total(store.getState()));  // Expected output: total: 35
unsubscribe();                                    // stop listening
store.dispatch({ type: "CLEAR" });                // no output: the listener was removed
console.log(store.getState());                    // Expected output: { items: [] }
```

## 💻 Code Example — Advanced
```javascript
// createStore: production-style store with guards, safe listener handling, and a clear error model
function createStore(reducer, initialState) {
  let state = initialState;                         // the single source of truth
  let listeners = [];                               // current listeners; replaced (never mutated) on change
  let isDispatching = false;                        // true while a reducer is running

  function getState() {
    if (isDispatching) throw new Error("getState cannot be called inside a reducer"); // keep reducers pure
    return state;                                   // hand back the current state
  }

  function dispatch(action) {
    if (typeof action !== "object" || action === null || typeof action.type !== "string") {
      throw new TypeError("action must be an object with a string type"); // reject bad actions early
    }
    if (isDispatching) throw new Error("reducers may not dispatch actions"); // stop nested dispatches
    isDispatching = true;                           // mark that a reducer is running
    try {
      state = reducer(state, action);               // compute the next state
    } finally {
      isDispatching = false;                        // always reset, even if the reducer threw
    }
    for (const listener of listeners) listener(state); // listeners is a stable array during this loop
    return action;                                  // return the action
  }

  function subscribe(listener) {
    if (typeof listener !== "function") throw new TypeError("listener must be a function");
    let subscribed = true;                          // lets unsubscribe run safely more than once
    listeners = [...listeners, listener];           // copy-on-write: the running loop is not affected
    return function unsubscribe() {
      if (!subscribed) return;                      // a second call does nothing
      subscribed = false;                           // mark as removed
      listeners = listeners.filter((l) => l !== listener); // build a new list without this listener
    };
  }

  return { getState, dispatch, subscribe };         // the public API
}

// cartReducer: same pure reducer as the basic example, with a coupon field
function cartReducer(state, action) {
  switch (action.type) {
    case "ADD_ITEM": return { ...state, items: [...state.items, action.item] };
    case "CLEAR": return { ...state, items: [] };
    case "SET_COUPON": return { ...state, coupon: action.code }; // only the coupon changes; items keep their reference
    default: return state;                          // unknown action: same state object
  }
}

// createSelector: memoized selector; it recomputes only when the input it reads changes (by reference)
function createSelector(select, compute) {
  let hasRun = false;                               // no cached answer yet
  let lastInput, lastResult;                        // the previous input and its result
  return function selector(state) {
    const input = select(state);                    // pick the part of the state this selector reads
    if (hasRun && input === lastInput) return lastResult; // same reference: reuse the cached answer
    hasRun = true;                                  // remember that we have run once
    lastInput = input;                              // store the new input
    lastResult = compute(input);                    // do the expensive work once
    return lastResult;                              // return the fresh answer
  };
}

// Demo: subscribers, a memoized total, and a coupon change that keeps the items reference
const store = createStore(cartReducer, { items: [], coupon: null }); // starts empty
const selectTotal = createSelector(
  (s) => s.items,                                   // this selector only depends on items
  (items) => { console.log("computing total"); return items.reduce((sum, i) => sum + i.price, 0); },
);
store.subscribe((s) => console.log("listener saw", s.items.length, "items")); // a subscriber
store.dispatch({ type: "ADD_ITEM", item: { id: 1, price: 20 } }); // Expected output: listener saw 1 items
console.log(selectTotal(store.getState()));         // Expected output: computing total, then 20
console.log(selectTotal(store.getState()));         // Expected output: 20 (cached, no "computing total")
store.dispatch({ type: "SET_COUPON", code: "CHAI10" }); // Expected output: listener saw 1 items
console.log(selectTotal(store.getState()));         // Expected output: 20 (cached: items did not change)

// Time:  dispatch is O(r + l), where r is the reducer cost and l is the number of listeners
// Space: O(l) for the listener array; each dispatch creates one new state object
```

### Edge Cases
Paste this after the advanced example. It reuses `createStore` and `cartReducer` from above.
```javascript
// Edge 1: an unknown action returns the same state object, so nothing changed
const before = store.getState();                    // remember the state
store.dispatch({ type: "UNKNOWN" });                // reducer returns state unchanged
console.log(store.getState() === before);           // Expected output: true

// Edge 2: bad actions and bad listeners are rejected with a clear error
try { store.dispatch({}); } catch (e) { console.log(e.message); } // Expected output: action must be an object with a string type
try { store.subscribe("not a function"); } catch (e) { console.log(e.message); } // Expected output: listener must be a function

// Edge 3: a listener can unsubscribe itself during dispatch, and a second unsubscribe is harmless
let calls = 0;                                      // counts how often the listener ran
const unsub = store.subscribe(() => { calls++; unsub(); unsub(); }); // unsubscribe twice inside itself
store.dispatch({ type: "CLEAR" });                  // listener runs once and removes itself
store.dispatch({ type: "CLEAR" });                  // listener is gone, so it does not run again
console.log("listener calls:", calls);              // Expected output: listener calls: 1

// Edge 4: a reducer that dispatches is blocked
const bad = createStore((s, a) => { if (a.type === "GO") bad.dispatch({ type: "NESTED" }); return s; }, {});
try { bad.dispatch({ type: "GO" }); } catch (e) { console.log(e.message); } // Expected output: reducers may not dispatch actions
```

---

## 🟠 Express.js Integration
A server can use the same store for a short-lived per-user state, such as a cart kept in memory during a session. Each cart id gets its own store. The route reads with `getState` and changes state only through `dispatch`, so the API follows the same rules as the browser.

```javascript
// Express.js: in-memory cart per id, using createStore and cartReducer from the advanced example
const express = require("express");               // web framework (install with: npm i express)
const app = express();                            // create the app
app.use(express.json());                          // parse JSON bodies into req.body

const carts = new Map();                          // cartId -> store; in memory, so lost on restart
function getCartStore(cartId) {
  if (!carts.has(cartId)) {                       // first time we see this cart
    carts.set(cartId, createStore(cartReducer, { items: [], coupon: null })); // create its store
  }
  return carts.get(cartId);                       // return the store for this cart
}

app.get("/api/carts/:id", (req, res) => {         // read the cart
  res.json(getCartStore(req.params.id).getState()); // getState returns the current cart
});

app.post("/api/carts/:id/items", (req, res) => {  // add an item to the cart
  const store = getCartStore(req.params.id);      // find this cart's store
  store.dispatch({ type: "ADD_ITEM", item: req.body }); // change state only through dispatch
  res.status(201).json(store.getState());         // return the updated cart
});

app.listen(3000, () => console.log("Cart API on 3000")); // start the server
```

---

## 🌐 Browser Version (HTML, not run with node)
This version uses the same `createStore` idea in a browser page. The subscriber re-renders the list and the total. It saves the cart to `localStorage` inside a `try/catch`, because storage can be blocked in private windows. Save it as an `.html` file and open it in a browser.

```html
<!-- Browser version: NOT run with node. Save as a .html file and open it in a browser. -->
<!doctype html>
<html>
<head>
  <meta charset="utf-8">                                        <!-- text encoding for Hindi -->
  <title>Cart state demo</title>
  <style>body { font-family: system-ui, sans-serif; margin: 16px; }</style>
</head>
<body>
  <button id="add">Add Chai (Rs 20)</button>                    <!-- dispatches ADD_ITEM -->
  <button id="clear">Clear</button>                             <!-- dispatches CLEAR -->
  <ul id="items"></ul>                                          <!-- rendered by the subscriber -->
  <p>Total: <span id="total">0</span></p>                       <!-- rendered by the subscriber -->
  <script>
    function createStore(reducer, initialState) {               // the same store as the node version
      let state = initialState;                                 // single source of truth
      const listeners = [];                                     // subscribers
      return {
        getState: () => state,
        dispatch(action) { state = reducer(state, action); listeners.slice().forEach((fn) => fn(state)); },
        subscribe(fn) {                                         // register a listener
          listeners.push(fn);
          return () => { const i = listeners.indexOf(fn); if (i !== -1) listeners.splice(i, 1); }; // safe unsubscribe
        },
      };
    }

    function cartReducer(state, action) {                        // pure reducer: never mutates
      switch (action.type) {
        case "ADD_ITEM": return { ...state, items: [...state.items, action.item] };
        case "CLEAR": return { ...state, items: [] };
        default: return state;
      }
    }

    let saved = [];                                             // load the saved cart if the browser allows it
    try { saved = JSON.parse(localStorage.getItem("cart") || "[]"); } catch (e) { saved = []; } // storage may be blocked
    const store = createStore(cartReducer, { items: saved });   // the app's only state

    // subscriber: re-render whenever the state changes
    store.subscribe((s) => {
      document.getElementById("items").innerHTML = "";          // clear the old list
      for (const item of s.items) {                             // one <li> per item
        const li = document.createElement("li");                // new list item
        li.textContent = `${item.name} Rs ${item.price}`;       // textContent avoids HTML injection
        document.getElementById("items").appendChild(li);       // add it to the page
      }
      document.getElementById("total").textContent = s.items.reduce((sum, i) => sum + i.price, 0);
      try { localStorage.setItem("cart", JSON.stringify(s.items)); } catch (e) { /* storage blocked: skip */ }
    });

    document.getElementById("add").onclick = () => store.dispatch({ type: "ADD_ITEM", item: { name: "Chai", price: 20 } });
    document.getElementById("clear").onclick = () => store.dispatch({ type: "CLEAR" });
    store.dispatch({ type: "@@INIT" });                         // unknown action: triggers one first render
  </script>
</body>
</html>
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Mutating the state object instead of returning a new one
✅ Correct: subscribers and selectors detect changes by reference. If you mutate, the reference stays the same, so the change is missed.

```javascript
// Wrong: push changes the object in place, so the reference never changes
const prev = { items: [] };
const next = prev;                                  // same object
next.items.push(1);                                 // mutate it
console.log(Object.is(prev, next), prev.items.length); // Expected output: true 1 (the change looks like "no change")
```

```javascript
// Right: copy the object and the array, so the reference changes with the data
const prev2 = { items: [] };
const next2 = { ...prev2, items: [...prev2.items, 1] }; // new object and new array
console.log(Object.is(prev2, next2), prev2.items.length, next2.items.length); // Expected output: false 0 1
```

❌ **Mistake 2:** A reducer with no `default` case
✅ Correct: an unknown action returns `undefined` by accident, which becomes the new state. Always return the current state for unknown actions.

```javascript
// Wrong: no default, so an unknown action makes the state undefined
const reducer = (state, action) => {
  switch (action.type) {
    case "ADD": return { items: [...state.items, action.item] };
  }                                                 // no default branch
};
let state = { items: [] };
state = reducer(state, { type: "UNKNOWN" });        // returns undefined
console.log(state);                                 // Expected output: undefined

// Right: return the current state in the default branch
const reducer2 = (state, action) => {
  switch (action.type) {
    case "ADD": return { items: [...state.items, action.item] };
    default: return state;                          // unknown action: keep the state
  }
};
let state2 = { items: [] };
state2 = reducer2(state2, { type: "UNKNOWN" });     // same state object comes back
console.log(state2);                                // Expected output: { items: [] }
```

---

## 🧠 Tricky Interview Question
Paste this after the advanced example. It reuses `createStore` and `cartReducer` from above.
```javascript
const store2 = createStore(cartReducer, { items: [], coupon: null }); // a fresh store
let renders = 0;                                    // counts subscriber calls
store2.subscribe(() => renders++);                  // a subscriber that only counts
store2.dispatch({ type: "SET_COUPON", code: "CHAI10" }); // changes the coupon
store2.dispatch({ type: "UNKNOWN" });               // unknown action: state unchanged
const saved = store2.getState();                    // remember the state after UNKNOWN
store2.dispatch({ type: "CLEAR" });                 // CLEAR creates a new items array
console.log(renders, saved === store2.getState(), saved.items === store2.getState().items); // what is printed?
```
Answer:
```
3 false false
```
The subscriber runs after every dispatch, including the unknown action, so the count is 3 and not 2. The `UNKNOWN` action returned the same state object, but the subscriber was still called. `CLEAR` builds a new state object with a new empty `items` array, so `saved` and the current state are different objects, and their `items` arrays are different too. Subscribers are notified about every dispatch, and selectors decide whether to recompute by checking references.

---

## ⚫ Interview Questions + Answers

**Q1: Why must a reducer be a pure function?**
A1: A pure reducer always returns the same output for the same input and has no side effects. This makes changes predictable, easy to test, and easy to replay or log.

**Q2: Why do subscribers get called even when the state did not change?**
A2: The store does not compare old and new states. It calls every listener after each dispatch. Components that care about a value should compare the value they read, not depend on the store calling them.

**Q3: Why does `unsubscribe` copy the listener list?**
A3: If a listener unsubscribes while the loop is running, removing items from the same array would skip some listeners. Copying the array (or replacing it, as in the advanced version) keeps the loop safe.

**Q4: How does a memoized selector work?**
A4: It stores the last input and output. If the new input is the same reference as the last one, it returns the cached output. This is why immutable updates matter: a changed reference means "recompute".

**Q5: What are the main pitfalls when building a store?**
A5: Mutating state in place, missing the default case in the reducer, dispatching inside a reducer, and forgetting to unsubscribe. The advanced version guards against the middle two.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several components read and change the same data, such as a cart, a user session, or filters
- You need a predictable history of changes, for example to log or undo actions
- You want to test business rules as pure reducer functions without a UI

❌ Avoid when:
- The data is local to one component; `useState` or a plain variable is enough
- The data comes from the server and is already cached by a library; use that library's cache instead
- The app is tiny; a store adds indirection you do not need

---

## 📊 Visual Diagram
```
           dispatch(action)
UI  ------------------------->  reducer(state, action)
 ^                                      |
 |                                      v  returns NEW state
 |                              +---------------+
 |   subscriber(newState) <-----|     store     |
 |   re-render with new state   | state: {...}  |
 +------------------------------|  listeners[]  |
        getState() reads        +---------------+

Memoized selector:
  select(state) -> input   same reference as last time? -> return cached result
                           different reference?        -> compute again
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Store | Holds the one copy of the app state | सारे state वाला एक object |
| Action | An object that describes a change | बदलाव बताने वाला object |
| Reducer | Pure function that returns the next state | अगला state लौटाने वाला pure function |
| dispatch | The only way to send an action to the store | Action भेजने का एकमात्र रास्ता |
| subscribe | Registers a listener to be called on change | Change पर चलने वाला listener दर्ज करना |
| Selector | Reads a value from the state | State से value पढ़ने वाला function |
| Memoization | Caching a result for the same input | एक ही input के लिए result याद रखना |
| Immutability | Never change the old object; create a new one | पुराने object को न बदलना, नया बनाना |

---

## ⚡ 3-Line Summary
English:
1. A store holds one state; only `dispatch` changes it, through a pure reducer that returns a new object.
2. `subscribe` returns an unsubscribe function, and listeners run after every dispatch.
3. Memoized selectors reuse results by reference, so immutable updates are what make them work.

Hindi:
1. Store एक state रखता है; उसे सिर्फ `dispatch` बदलता है, एक pure reducer से जो नया object लौटाता है।
2. `subscribe` एक unsubscribe function लौटाता है, और हर dispatch के बाद listeners चलते हैं।
3. Memoized selectors reference से results दोबारा इस्तेमाल करते हैं, इसलिए immutable updates ही उन्हें काम का बनाते हैं।

---

## ➡️ Next Topic
**201. Next topic in the curriculum (the next interview problem)** — after building a store, the natural next step is to take the same ideas (state, events, and small utilities) into the next problem set. The exact title of topic 201 is not in this folder, so check the topic index before you start.
