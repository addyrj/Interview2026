---

# Q267. Command Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a calculator where each operation is a command object with `execute()` and `undo()`, managed by an invoker that supports undo.

---

## 💡 Quick Concept (2 lines only)
Command wraps a request as an object so it can be stored, queued, executed or undone later.
हिंदी: Command हर action को object बना देता है, जिससे उसे save और undo किया जा सके।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Receiver holds the state
// Step 2: Commands know how to execute and undo
// Step 3: Invoker runs commands and keeps history

class Calculator {
  value = 0;                                   // receiver state
}

class AddCommand {
  constructor(calc, n) { this.calc = calc; this.n = n; } // store target and operand
  execute() { this.calc.value += this.n; }     // do the action
  undo() { this.calc.value -= this.n; }        // reverse the action
}

class MultiplyCommand {
  constructor(calc, n) { this.calc = calc; this.n = n; } // store target and operand
  execute() { this.prev = this.calc.value; this.calc.value *= this.n; } // remember old value
  undo() { this.calc.value = this.prev; }      // restore (multiplying by 0 isn't reversible by division)
}

class Invoker {
  history = [];                                // executed commands
  run(cmd) { cmd.execute(); this.history.push(cmd); } // execute and record
  undo() { this.history.pop()?.undo(); }       // undo last command if any
}

// ============================================
// TEST CASES
// ============================================

const calc = new Calculator();                 // value = 0
const inv = new Invoker();                     // history manager
inv.run(new AddCommand(calc, 5));              // 0 + 5
inv.run(new MultiplyCommand(calc, 3));         // 5 * 3
console.log(calc.value);                       // Expected: 15
inv.undo();                                    // undo multiply
console.log(calc.value);                       // Expected: 5
inv.undo();                                    // undo add
console.log(calc.value);                       // Expected: 0
inv.undo();                                    // nothing left, safe no-op
console.log(calc.value);                       // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Each action is an object with its own reverse logic, so the invoker just stacks them. Undo is popping the stack.
हिंदी: हर command अपना undo जानता है, इसलिए history stack से pop करके undo हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Closure-based commands
const makeCmd = (doIt, undoIt) => ({ execute: doIt, undo: undoIt }); // pair of functions
let n = 0;                                                            // state
const inc = makeCmd(() => n++, () => n--);                            // increment command
inc.execute(); inc.execute(); inc.undo();                             // +1 +1 -1
console.log(n);                                                       // Expected: 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: undo via inverse math when operation is lossy (x * 0)
// ✅ Correct: store previous state (memento) inside the command
```

---

## 🎯 Interview Tip (1 line)
Link it to undo/redo, task queues and Redux actions (actions are commands).

---

## 🔗 Related Questions
→ Q200 (Undo/redo) | Q188 (State manager) | Q095 (Async queue)
