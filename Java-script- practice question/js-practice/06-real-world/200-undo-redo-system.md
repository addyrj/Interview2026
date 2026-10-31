---

# Q200. Build Undo/Redo System
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `History` class holding states with `push(state)`, `undo()`, `redo()`, `canUndo`, `canRedo`, `current`. A new `push` after an undo must discard the redo branch. Optional `limit` caps memory.

```javascript
const h = new History('');
h.push('a'); h.push('ab'); h.undo(); // current = 'a'
```

---

## 💡 Quick Concept (2 lines only)
Keep an array of states and an index pointer; undo = index--, redo = index++, push = cut the future and append.
हिंदी: States की array और एक pointer रखो — undo पर pointer पीछे, redo पर आगे, नया push भविष्य मिटा देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class History {
  constructor(initial, limit = 100) {
    this.states = [initial];                     // Step 1: timeline of states
    this.index = 0;                              // pointer to current state
    this.limit = limit;                          // max remembered states
  }

  get current() { return this.states[this.index]; } // Step 2: state at pointer
  get canUndo() { return this.index > 0; }           // anything behind?
  get canRedo() { return this.index < this.states.length - 1; } // anything ahead?

  push(state) {
    this.states = this.states.slice(0, this.index + 1); // Step 3: drop redo branch
    this.states.push(state);                     // add new state
    if (this.states.length > this.limit) this.states.shift(); // Step 4: forget oldest
    this.index = this.states.length - 1;         // move pointer to newest
  }

  undo() {
    if (this.canUndo) this.index--;              // Step 5: go back one step
    return this.current;
  }

  redo() {
    if (this.canRedo) this.index++;              // go forward one step
    return this.current;
  }
}

// ============================================
// TEST CASES
// ============================================

const h = new History('');
h.push('a'); h.push('ab'); h.push('abc');
console.log(h.current);                          // Expected: abc
console.log(h.undo(), h.undo());                 // Expected: ab a
console.log(h.redo());                           // Expected: ab
h.push('abX');                                   // new branch -> redo history discarded
console.log(h.canRedo, h.current);               // Expected: false abX
console.log(h.undo(), h.undo(), h.undo());       // Expected: "ab a " (3rd value is '' the initial state)
```

---

## 🔍 Why This Works (3 lines max)
The pointer separates "past" (left) from "future" (right). Pushing after an undo slices off the future, exactly like text editors behave.
हिंदी: Pointer के बाएँ past और दाएँ future होता है; नया push करने पर future कट जाता है।

---

## ⚡ Alternative Solution
```javascript
// Two-stack version
const undoStack = [], redoStack = [];            // past and future
let present = '';
function change(next) { undoStack.push(present); present = next; redoStack.length = 0; } // clear future
function undo() { if (undoStack.length) { redoStack.push(present); present = undoStack.pop(); } }
function redo() { if (redoStack.length) { undoStack.push(present); present = redoStack.pop(); } }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: storing references to the SAME mutated object -> every history entry changes together
history.push(state); state.text = 'new';

// ✅ Correct: store immutable snapshots (spread / structuredClone) or store commands (diffs)
history.push({ ...state });
```

---

## 🎯 Interview Tip (1 line)
Mention snapshot vs command pattern (store diffs to save memory) and clearing redo on new action.

---

## 🔗 Related Questions
→ Q267 (command pattern) | Q188 (state manager) | Q199 (deep diff) | Q101 (queue using array)
