---

# Q156. Complete Stack Class
# Category: Complete the Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Fill in the blanks for a LIFO stack.

```javascript
class Stack {
  constructor() { this.items = []; }
  push(x) { this.items.____(x); }                // add on top
  pop() { return this.items.____(); }            // remove top
  peek() { return this.items[this.items.length ____ 1]; } // see top
  isEmpty() { return this.items.length ____ 0; }
  get size() { return this.items.____; }
}
```

---

## 💡 Quick Concept (2 lines only)
A stack is Last-In-First-Out: only the top is accessed, using push and pop in O(1).
हिंदी: Stack में last में डाली चीज़ सबसे पहले निकलती है (LIFO)।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Stack {
  constructor() { this.items = []; }                        // Step 1: backing array
  push(x) { this.items.push(x); }                           // blank 1: add to end (top)
  pop() { return this.items.pop(); }                        // blank 2: remove from end
  peek() { return this.items[this.items.length - 1]; }      // blank 3: last element
  isEmpty() { return this.items.length === 0; }             // blank 4: empty check
  get size() { return this.items.length; }                  // blank 5: count
}

// ============================================
// TEST CASES
// ============================================

const s = new Stack();
s.push(1); s.push(2); s.push(3);
console.log(s.peek());      // Expected: 3
console.log(s.pop());       // Expected: 3
console.log(s.size);        // Expected: 2
console.log(new Stack().isEmpty()); // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
The array end acts as the top; push/pop there are O(1). Peek reads the last element without removing it.
हिंदी: array का आखिरी हिस्सा stack का top है, इसलिए push/pop तेज़ हैं।

---

## ⚡ Alternative Solution
```javascript
// Private field to hide internals
class Stack2 {
  #a = [];
  push(x) { this.#a.push(x); }
  pop() { return this.#a.pop(); }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: unshift/shift for a stack is O(n)
// ✅ Correct: push/pop on the end
```

---

## 🎯 Interview Tip (1 line)
Say: "Stacks power undo, call stack, bracket matching and DFS."

---

## 🔗 Related Questions
→ Q100 (stack using array) | Q157 (queue class) | Q200 (undo/redo) | Q296 (call stack vs event loop)
