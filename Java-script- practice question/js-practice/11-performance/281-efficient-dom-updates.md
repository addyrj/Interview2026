---

# Q281. Efficient DOM Updates
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Update a list of items in the DOM by touching only the nodes whose text actually changed (a mini diff). Use a tiny fake DOM so it runs in Node.

---

## 💡 Quick Concept (2 lines only)
DOM writes are expensive; compare old vs new state and update only what changed instead of re-rendering everything.
हिंदी: DOM बदलना महंगा है, इसलिए सिर्फ वही nodes बदलो जिनकी value सच में बदली है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Mock DOM node that counts writes
// Step 2: Compare new value with current before writing
// Step 3: Add/remove only extra or missing nodes

let domWrites = 0;                                  // counts expensive operations

class FakeNode {
  constructor(text) { this._text = text; domWrites++; } // creating = a write
  set textContent(v) { this._text = v; domWrites++; }   // each write counted
  get textContent() { return this._text; }              // reading is free here
}

function update(nodes, items) {
  items.forEach((item, i) => {
    if (!nodes[i]) nodes[i] = new FakeNode(item);       // new item → create node
    else if (nodes[i].textContent !== item) nodes[i].textContent = item; // changed → update
    // unchanged → skip (no DOM touch)
  });
  nodes.length = items.length;                          // drop removed items
}

const nodes = [];                                       // our "list" of DOM nodes

// ============================================
// TEST CASES
// ============================================

update(nodes, ['a', 'b', 'c']);                         // initial render: 3 creates
console.log(domWrites);                                 // Expected: 3
update(nodes, ['a', 'X', 'c']);                         // only index 1 changed
console.log(domWrites);                                 // Expected: 4
update(nodes, ['a', 'X', 'c']);                         // identical → no writes
console.log(domWrites);                                 // Expected: 4
update(nodes, ['a', 'X']);                              // removal → no text writes
console.log(nodes.map((n) => n.textContent));           // Expected: [ 'a', 'X' ]
```

---

## 🔍 Why This Works (3 lines max)
Comparing plain JS values is cheap while DOM writes can trigger style/layout work. Skipping unchanged nodes cuts the write count to the minimum.
हिंदी: JS में compare सस्ता है और DOM write महंगा, इसलिए पहले compare करते हैं।

---

## ⚡ Alternative Solution
```javascript
// Browser: prefer textContent over innerHTML, and use event-free updates
// el.textContent = value;               // no HTML parsing, XSS-safe
// Use a framework's virtual DOM (React) / keyed lists to automate this diff.
const prev = 'hi', next = 'hi';          // pretend current vs new text
console.log(prev !== next);              // Expected: false (skip the write)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: container.innerHTML = items.map(render).join('') on every change
//   (destroys and rebuilds all nodes, loses focus/state)
// ✅ Correct: update changed nodes only, use stable keys for reorder
```

---

## 🎯 Interview Tip (1 line)
Say: "That's what React's reconciliation does — diff in memory, commit minimal DOM mutations."

---

## 🔗 Related Questions
→ Q287 (Batch DOM updates) | Q288 (Reflow/repaint) | Q073 (Reconciliation notes)
