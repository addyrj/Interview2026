---

# Q222. Custom Event Example
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Create and dispatch a custom event `cart:add` carrying data `{ id, qty }`.
Another part of the page should listen and log the data. The event should bubble to `document`.

---

## 💡 Quick Concept (2 lines only)
`new CustomEvent(name, { detail, bubbles })` creates your own event; `dispatchEvent` fires it and listeners read `event.detail`.
हिंदी: `CustomEvent` से अपना event बनाओ, `detail` में data भेजो, और `dispatchEvent` से fire करो।

---

## ✅ Answer / Solution

```html
<button id="addBtn">Add to cart</button>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Create a CustomEvent with detail payload
// Step 2: Listen on document for the event name
// Step 3: Dispatch from the button

const btn = document.getElementById('addBtn');        // source element

document.addEventListener('cart:add', (e) => {        // listener on document
  console.log('Cart add:', e.detail.id, e.detail.qty); // read payload from detail
});

btn.addEventListener('click', () => {                 // when button clicked
  const event = new CustomEvent('cart:add', {         // create custom event
    detail: { id: 101, qty: 2 },                      // data to send
    bubbles: true,                                    // let it bubble up to document
    cancelable: true,                                 // allow preventDefault()
  });
  const notCancelled = btn.dispatchEvent(event);      // fire it; returns false if prevented
  console.log('Not cancelled?', notCancelled);        // show result
});

// ============================================
// TEST CASES
// ============================================

// Test 1: btn.click()  -> Expected: Cart add: 101 2  then  Not cancelled? true
// Test 2: with bubbles:false -> Expected: document listener never fires
// Test 3: add listener calling e.preventDefault(), click -> Expected: Not cancelled? false
```

---

## 🔍 Why This Works (3 lines max)
The event is dispatched on the button and, with `bubbles: true`, travels up to `document` where our listener catches it. Data travels inside `detail`. `cancelable` lets listeners veto via `preventDefault()`.
हिंदी: `bubbles: true` से event document तक पहुँचता है, और data `detail` में मिलता है।

---

## ⚡ Alternative Solution
```javascript
// Using EventTarget as a standalone event bus (no DOM needed)
const bus = new EventTarget();                        // plain event target
bus.addEventListener('ping', (e) => console.log(e.detail)); // listen
bus.dispatchEvent(new CustomEvent('ping', { detail: 'hi' })); // logs: hi
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: data placed on a plain Event — it is lost / not typed
const e1 = new Event('cart:add');
e1.data = { id: 1 };               // non-standard, easy to break

// ✅ Correct: use CustomEvent + detail, and set bubbles if parents must hear it
const e2 = new CustomEvent('cart:add', { detail: { id: 1 }, bubbles: true });
```

---

## 🎯 Interview Tip (1 line)
Say: "CustomEvent decouples components — emitter doesn't know listeners; remember bubbles defaults to false and data goes in detail."

---

## 🔗 Related Questions
→ Q221 (event delegation) | Q096 (event emitter) | Q187 (event bus) | Q097 (pub/sub)
