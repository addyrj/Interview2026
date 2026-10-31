---

# Q224. Mutation Observer
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Watch a `#container` element and log whenever children are added/removed or its `class` attribute changes.
Show how to stop watching.

---

## 💡 Quick Concept (2 lines only)
`MutationObserver` calls your callback (as a microtask) when DOM nodes or attributes change.
हिंदी: `MutationObserver` बताता है कि DOM में कुछ add, remove या attribute change हुआ।

---

## ✅ Answer / Solution

```html
<div id="container" class="box"></div>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Create observer with a callback receiving mutation records
// Step 2: Call observe(target, options) choosing what to watch
// Step 3: Call disconnect() when done

const container = document.getElementById('container'); // element to watch

const observer = new MutationObserver((mutations) => {  // callback gets list of records
  mutations.forEach((m) => {                             // loop each record
    if (m.type === 'childList') {                        // children changed
      console.log('added:', m.addedNodes.length, 'removed:', m.removedNodes.length);
    } else if (m.type === 'attributes') {                // attribute changed
      console.log('attr', m.attributeName, 'old =', m.oldValue); // which attr + old value
    }
  });
});

observer.observe(container, {                            // start watching
  childList: true,                                       // add/remove children
  attributes: true,                                      // attribute changes
  attributeFilter: ['class'],                            // only the class attribute
  attributeOldValue: true,                               // keep old value
});

// ============================================
// TEST CASES
// ============================================

container.appendChild(document.createElement('p'));      // Expected: added: 1 removed: 0
container.removeChild(container.firstChild);             // Expected: added: 0 removed: 1
container.className = 'box active';                      // Expected: attr class old = box
container.id = 'changed';                                // Expected: nothing (id filtered out)
observer.disconnect();                                   // stop watching
container.className = 'x';                               // Expected: nothing logged
```

---

## 🔍 Why This Works (3 lines max)
The browser batches changes and delivers them as records in a microtask after the current script. Options decide what is tracked, so unrelated changes cost nothing. `disconnect()` releases the observer.
हिंदी: Options से तय होता है क्या देखना है, और `disconnect()` से watching बंद हो जाती है।

---

## ⚡ Alternative Solution
```javascript
// Watch the whole subtree (nested changes) and flush pending records manually
const obs = new MutationObserver(() => console.log('something changed')); // simple callback
obs.observe(document.body, { childList: true, subtree: true });            // deep watch
const pending = obs.takeRecords();                                          // get queued records now
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: observe() without any option — throws TypeError
// observer.observe(container);

// ❌ Wrong: modifying watched DOM inside the callback -> infinite loop
// ✅ Correct: disconnect() before changing, then observe() again, or guard with a flag
```

---

## 🎯 Interview Tip (1 line)
Say: "MutationObserver replaced deprecated Mutation Events; it is batched, async (microtask), and needs at least one of childList/attributes/characterData."

---

## 🔗 Related Questions
→ Q223 (intersection observer) | Q281 (efficient DOM updates) | Q282 (avoid memory leaks)
