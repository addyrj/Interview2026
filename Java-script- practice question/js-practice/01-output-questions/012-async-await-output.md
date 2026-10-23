---

# Q012. async/await Output Order
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print, and in what order?

```javascript
async function main() {
  console.log('1');
  
  await Promise.resolve();
  
  console.log('2');
}

console.log('3');
main();
console.log('4');
```

---

## 💡 Quick Concept (2 lines only)
`async` function runs synchronously until the first `await`. After `await`, execution is paused — control returns to caller, and the rest of the function runs as a microtask.
हिंदी: `async` function `await` तक synchronous चलता है — `await` के बाद pause होता है और rest microtask queue में जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

async function main() {
  console.log('1');        // runs synchronously (part of main() call)
  
  await Promise.resolve(); // PAUSE — return control to caller
  
  console.log('2');        // resumes as microtask after call stack is empty
}

console.log('3');  // sync — runs before main()
main();            // starts main() synchronously until await
console.log('4');  // sync — runs after main() pauses at await

// ============================================
// OUTPUT:
// ============================================
// 3   ← sync (before main())
// 1   ← sync inside main() (before await)
// 4   ← sync (after main() pauses)
// 2   ← microtask (after call stack empty)

// EXECUTION FLOW:
// 1. console.log('3')           → prints 3
// 2. main() called              → enters function synchronously
// 3. console.log('1')           → prints 1
// 4. await Promise.resolve()    → schedules '2' as microtask, returns to caller
// 5. console.log('4')           → prints 4
// 6. call stack empty           → event loop picks up microtask
// 7. console.log('2')           → prints 2
```

---

## 🔍 Why This Works (3 lines max)
`main()` is called synchronously — it prints '1' then hits `await`. `await` pauses the async function and returns control to the outer code, which prints '4'. When the call stack is clear, the microtask (code after `await`) runs, printing '2'.
हिंदी: `main()` sync start होता है, '1' print करता है, `await` पर pause होता है, '4' print होती है, फिर '2'।

---

## ⚡ Alternative Solution
```javascript
// More complex example:
async function fetchData() {
  console.log('A');                    // sync
  const result = await delay(100);    // pause 100ms
  console.log('B');                    // after 100ms
  return result;
}

async function main2() {
  console.log('C');                    // sync
  const p = fetchData();              // starts fetchData sync → prints A
  console.log('D');                    // sync (fetchData paused at await)
  await p;                            // wait for fetchData to complete
  console.log('E');                    // after fetchData done
}

main2();
console.log('F');                     // sync

// Output: C, A, D, F, B, E
// C, A = sync before pauses
// D = sync after fetchData pauses
// F = sync after main2 pauses at await p
// B = microtask: fetchData resumes after 100ms
// E = microtask: main2 resumes after p resolves
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking async function runs entirely async
async function test() {
  console.log('x');  // this IS synchronous! runs immediately
  await something();
  console.log('y');  // this is async (microtask)
}
// test() -- 'x' runs synchronously, same tick

// ❌ Wrong: thinking await blocks the whole program
async function slow() {
  await delay(3000);     // only pauses THIS function
  console.log('done');
}
slow();
console.log('immediate'); // prints immediately — NOT 3 seconds later
// async functions pause themselves, not the thread!
```

---

## 🎯 Interview Tip (1 line)
Say: "async function runs sync until first await — then pauses and schedules continuation as microtask; code after the function call runs before the continuation."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q013 (Promise + setTimeout) | Q016 (microtask vs macrotask) | Q300 (Promise vs async/await)
