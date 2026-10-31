---

# Q100. Implement Stack Using Array
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a `Stack` class (LIFO) using an array with methods: `push`, `pop`, `peek`, `isEmpty`, `size`.

```javascript
const s = new Stack();
s.push(1); s.push(2);
s.pop(); // 2
```

---

## 💡 Quick Concept (2 lines only)
Stack is Last-In-First-Out: add and remove only from the top (end of array). All operations are O(1).
हिंदी: Stack में आखिरी डाला हुआ element सबसे पहले निकलता है (LIFO)।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: private array to hold items
// Step 2: push adds to end, pop removes from end
// Step 3: peek reads last item without removing
// Step 4: helpers isEmpty and size

class Stack {
  #items = [];                       // private storage (hidden from outside)

  push(item) {
    this.#items.push(item);          // add on top
    return this;                     // allow chaining
  }

  pop() {
    if (this.isEmpty()) return undefined;  // underflow guard
    return this.#items.pop();        // remove and return top
  }

  peek() {
    return this.#items[this.#items.length - 1]; // look at top only
  }

  isEmpty() {
    return this.#items.length === 0; // true when nothing stored
  }

  size() {
    return this.#items.length;       // number of items
  }
}

// ============================================
// TEST CASES
// ============================================

const s = new Stack();               // create stack
s.push(10).push(20).push(30);        // push three items

console.log(s.pop());                // Expected: 30
console.log(s.peek());               // Expected: 20
console.log(s.size());               // Expected: 2
console.log(s.isEmpty());            // Expected: false
s.pop(); s.pop();                    // empty it
console.log(s.pop());                // Expected: undefined
console.log(s.isEmpty());            // Expected: true

// Classic use: balanced brackets
function balanced(str) {
  const st = new Stack();                          // stack of open brackets
  const pairs = { ')': '(', ']': '[', '}': '{' }; // closing -> opening
  for (const ch of str) {
    if ('([{'.includes(ch)) st.push(ch);           // opening => push
    else if (pairs[ch] && st.pop() !== pairs[ch]) return false; // mismatch
  }
  return st.isEmpty();                             // all matched?
}
console.log(balanced('{[()]}'));     // Expected: true
console.log(balanced('{[(])}'));     // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
`push`/`pop` work at the end of an array in O(1). Private field `#items` stops outside code from breaking LIFO order.
हिंदी: Array के आखिर में push/pop O(1) है, और private field बाहर से बदलाव रोकता है।

---

## ⚡ Alternative Solution
```javascript
// Function/closure based stack (no class)
function createStack() {
  const items = [];                              // hidden via closure
  return {
    push: (x) => items.push(x),                  // add
    pop: () => items.pop(),                      // remove
    peek: () => items[items.length - 1],         // top
    size: () => items.length,                    // count
  };
}
const st = createStack();
st.push(1); st.push(2);
console.log(st.pop()); // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using shift/unshift — O(n) because every element moves
const bad = [];
bad.unshift(1);   // add at front (slow)
bad.shift();      // remove from front (slow)

// ✅ Correct: push/pop at the end — O(1)
```

---

## 🎯 Interview Tip (1 line)
Say "LIFO, O(1) push/pop" and give real uses: call stack, undo, bracket matching, DFS.

---

## 🔗 Related Questions
→ Q101 (queue using array) | Q102 (linked list) | Q156 (complete stack class) | Q200 (undo/redo)
