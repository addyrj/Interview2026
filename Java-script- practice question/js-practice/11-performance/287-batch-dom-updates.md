---

# Q287. Batch DOM Updates
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Insert 1,000 items into the page with one live-DOM insertion instead of 1,000, using a DocumentFragment. (A mock DOM counts live insertions so it runs in Node.)

---

## 💡 Quick Concept (2 lines only)
Build changes off-screen (fragment/string) and attach once, so the browser recalculates layout once instead of N times.
हिंदी: पहले memory में सब बनाओ और फिर एक ही बार DOM में जोड़ो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Mock DOM that counts live-tree insertions
// Step 2: Naive: append each item to the live container
// Step 3: Batched: append to a fragment, then once to the container

class MockNode {
  constructor(live = false) { this.children = []; this.live = live; } // live = attached to page
  appendChild(child) {
    this.children.push(child);                       // add child
    if (this.live) MockNode.liveInserts++;           // count only real-document mutations
    return child;
  }
}
MockNode.liveInserts = 0;                            // static counter

const container = new MockNode(true);                // pretend it's in the document

// Naive: 1000 live mutations
for (let i = 0; i < 1000; i++) container.appendChild(new MockNode()); // each triggers layout

const naive = MockNode.liveInserts;                  // record count
MockNode.liveInserts = 0;                            // reset
const container2 = new MockNode(true);               // fresh live container

// Batched: build in fragment first
const fragment = new MockNode(false);                // off-screen (document.createDocumentFragment())
for (let i = 0; i < 1000; i++) fragment.appendChild(new MockNode()); // free, not live
container2.appendChild(fragment);                    // ONE live mutation

// ============================================
// TEST CASES
// ============================================

console.log(naive);                                  // Expected: 1000
console.log(MockNode.liveInserts);                   // Expected: 1
console.log(container2.children[0].children.length); // Expected: 1000
```

---

## 🔍 Why This Works (3 lines max)
Changes to a detached fragment don't touch the rendered tree, so no layout is triggered until the single attach. The browser then reflows once.
हिंदी: Fragment पर बदलाव screen को छूते नहीं, इसलिए reflow सिर्फ एक बार होता है।

---

## ⚡ Alternative Solution
```javascript
// Browser: build an HTML string, assign once (escape user input!) or use replaceChildren
// const html = items.map((t) => `<li>${t}</li>`).join('');
// ul.innerHTML = html;                         // one parse + one insert
// ul.replaceChildren(...nodes);                // modern one-call batch
const items = ['a', 'b'];                       // sample data
console.log(items.map((t) => `<li>${t}</li>`).join('')); // Expected: <li>a</li><li>b</li>
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: for (...) document.body.appendChild(el) — layout work each iteration
// ✅ Correct: fragment/string, one append (or use framework batching)
```

---

## 🎯 Interview Tip (1 line)
Say React batches state updates into one commit for the same reason.

---

## 🔗 Related Questions
→ Q281 (Efficient DOM updates) | Q288 (Reflow/repaint) | Q226 (Infinite scroll)
