---

# Q310. event bubbling vs capturing
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain event bubbling vs capturing. Show the order in which handlers fire for a click on a nested element, how `stopPropagation` changes it, and how event delegation uses bubbling.

---

## 💡 Quick Concept (2 lines only)
An event travels in 3 phases: capture (window down to target), target, then bubble (target back up to window). Listeners run on bubble by default; pass `true` to run on capture.
हिंदी: Event पहले ऊपर से नीचे (capturing) जाता है, फिर target पर, फिर नीचे से ऊपर (bubbling) लौटता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — runs in plain Node (a tiny DOM-like simulation of the real algorithm)
// ============================================
// Real browser HTML for reference:
//   <div id="grandparent"><div id="parent"><button id="child">Click</button></div></div>
//   el.addEventListener('click', handler)        -> bubble phase (default)
//   el.addEventListener('click', handler, true)  -> capture phase

// Step 1: build the path from the target up to the root
// Step 2: capture phase = run capture listeners root -> target's parent
// Step 3: target phase = run all listeners on the target
// Step 4: bubble phase = run bubble listeners parent -> root
// Step 5: stopPropagation() stops the remaining phases

class Node {
  constructor(name, parent = null) {
    this.name = name;                         // label used in logs
    this.parent = parent;                     // link to parent (like parentNode)
    this.listeners = [];                      // list of { fn, capture }
  }
  on(fn, capture = false) {                   // like addEventListener('click', fn, capture)
    this.listeners.push({ fn, capture });     // store the listener
  }
}

function dispatch(target) {
  const path = [];                            // ancestors of the target, root first
  for (let n = target.parent; n; n = n.parent) path.unshift(n); // walk up and prepend
  let stopped = false;                        // set by stopPropagation
  const event = { stopPropagation() { stopped = true; } };      // minimal event object
  const run = (node, phase) => node.listeners
    .filter((l) => phase === 'target' || l.capture === (phase === 'capture')) // pick matching listeners
    .forEach((l) => l.fn(event));             // call them

  for (const n of path) { if (stopped) return; run(n, 'capture'); } // capture: root -> parent
  if (stopped) return;                        // a capture handler may have stopped it
  run(target, 'target');                      // target phase
  for (const n of [...path].reverse()) { if (stopped) return; run(n, 'bubble'); } // bubble: parent -> root
}

// Helper to build the 3-level tree and attach logging listeners
function build(opts = {}) {
  const gp = new Node('grandparent');         // outermost
  const p = new Node('parent', gp);           // middle
  const c = new Node('child', p);             // innermost (click target)
  gp.on(() => console.log('  grandparent capture'), true);  // capture listener
  gp.on(() => console.log('  grandparent bubble'));         // bubble listener
  p.on((e) => { console.log('  parent capture'); if (opts.stopAtParentCapture) e.stopPropagation(); }, true);
  p.on(() => console.log('  parent bubble'));
  c.on((e) => { console.log('  child (target)'); if (opts.stopAtChild) e.stopPropagation(); });
  return c;                                   // return the target to click
}

// ============================================
// TEST CASES
// ============================================

console.log('1) normal click:');
dispatch(build());
// Expected:
//   grandparent capture
//   parent capture
//   child (target)
//   parent bubble
//   grandparent bubble

console.log('2) child calls stopPropagation:');
dispatch(build({ stopAtChild: true }));
// Expected:
//   grandparent capture
//   parent capture
//   child (target)

console.log('3) parent capture calls stopPropagation:');
dispatch(build({ stopAtParentCapture: true }));
// Expected:
//   grandparent capture
//   parent capture
```

---

## 🔍 Why This Works (3 lines max)
The browser computes the path from `window` to the target, goes down (capture), fires the target, then goes back up (bubble). Stopping propagation cuts the walk, so later nodes never see the event.
हिंदी: Browser पूरा रास्ता बनाकर पहले नीचे जाता है फिर ऊपर लौटता है; `stopPropagation` रास्ता बीच में काट देता है।

---

## ⚡ Alternative Solution
```javascript
// Event delegation — one listener on the parent uses bubbling for many children (browser code)
// document.getElementById('list').addEventListener('click', (e) => {
//   const item = e.target.closest('li');        // which li was actually clicked?
//   if (item) console.log('clicked', item.dataset.id); // handle it
// });
// Other tools: { once: true } option, e.stopImmediatePropagation(), e.eventPhase, e.target vs e.currentTarget
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: stopPropagation everywhere "to be safe" — breaks analytics, dropdown-close handlers
// button.addEventListener('click', (e) => e.stopPropagation());

// ❌ Wrong: confusing e.target (clicked element) with e.currentTarget (element with the listener)

// ✅ Correct: use delegation, check e.target, stop propagation only when truly needed
```

---

## 🎯 Interview Tip (1 line)
Say: "Capture goes root-to-target, bubble goes target-to-root; default listeners use bubble, and delegation relies on bubbling to handle many children with one listener."

---

## 🔗 Related Questions
→ Q022 (this in event listener) | Q130 (fix event listener leak) | Q221 (event delegation) | Q222 (custom event)
