# 30. Closures
# हिंदी में: Closures — Function जो अपने Outer Scope को "याद" रखता है

---

## 🔵 Simple Definition (English)
A **closure** is a function that **remembers the variables from its outer scope** even after the outer function has finished executing. The inner function "closes over" the outer variables — they stay alive as long as the inner function exists.

## 🔵 सरल परिभाषा (Hindi)
Closure एक function है जो अपने outer scope के variables को **याद रखता है** — भले ही outer function finish हो जाए। Inner function outer variables को "close" कर लेता है — वो variables तब तक जीवित रहते हैं जब तक inner function जीवित है।

---

## 🔴 Problem it Solves
Without closures: no private state, no factory functions, no React hooks. Closures enable:
- Private data (encapsulation)
- Memoization / caching
- Event handlers that remember context
- React's `useState` under the hood
- Module pattern (before ES modules)

---

## 🟢 How it Works

```javascript
function outer() {
  let count = 0;       // outer variable

  function inner() {
    count++;           // inner closes over 'count'
    return count;
  }

  return inner;        // return inner function (not its result!)
}

const increment = outer(); // outer() runs and finishes
// But 'count' is still alive — inner function holds a reference!

increment(); // 1
increment(); // 2
increment(); // 3
// count is PRIVATE — not accessible from outside
```

---

## 🟡 Real World Example
```javascript
// Cart with private state — closure protects the items array

function createCart() {
  let items = []; // private — not accessible from outside

  return {
    add(item) {
      items.push(item);
      console.log(`Added ${item.name}. Cart has ${items.length} items.`);
    },
    remove(id) {
      items = items.filter(i => i.id !== id);
    },
    getTotal() {
      return items.reduce((sum, i) => sum + i.price, 0);
    },
    getItems() {
      return [...items]; // return copy, not reference!
    }
  };
}

const cart = createCart();
cart.add({ id: 1, name: "Pizza", price: 299 });
cart.add({ id: 2, name: "Coke",  price: 49 });
console.log(cart.getTotal()); // 348

// cart.items → undefined! (private via closure)
```

---

## 💻 Code Example — Basic
```javascript
// ── BASIC CLOSURE ────────────────────────

function makeGreeter(greeting) {
  // greeting is "closed over" by the returned function
  return function(name) {
    return `${greeting}, ${name}!`;
  };
}

const sayHello = makeGreeter("Hello");
const sayNamaste = makeGreeter("Namaste");

sayHello("Aditya");   // "Hello, Aditya!"
sayNamaste("Priya");  // "Namaste, Priya!"

// Each closure has its OWN copy of `greeting`

// ── COUNTER — CLASSIC CLOSURE ────────────

function makeCounter(start = 0) {
  let count = start; // private state

  return {
    increment() { return ++count; },
    decrement() { return --count; },
    reset()     { count = start; return count; },
    value()     { return count; },
  };
}

const c1 = makeCounter(0);
const c2 = makeCounter(10); // independent counter

c1.increment(); // 1
c1.increment(); // 2
c2.increment(); // 11

console.log(c1.value()); // 2
console.log(c2.value()); // 11
// c1 and c2 don't share state!

// ── CLOSURE REMEMBERS EVEN AFTER OUTER RUNS ──

function outerFunc() {
  const secret = "I'm private";
  let callCount = 0;

  return function reveal() {
    callCount++;
    console.log(`Secret: ${secret}, called ${callCount} times`);
  };
}

const reveal = outerFunc(); // outerFunc finishes
// BUT secret and callCount live on in the closure!

reveal(); // "Secret: I'm private, called 1 times"
reveal(); // "Secret: I'm private, called 2 times"

// ── EACH CLOSURE IS INDEPENDENT ──────────

function multiplier(factor) {
  return (num) => num * factor; // closes over factor
}

const double = multiplier(2);
const triple = multiplier(3);
const tenTimes = multiplier(10);

double(5);   // 10
triple(5);   // 15
tenTimes(5); // 50
```

## 💻 Code Example — Advanced
```javascript
// ── MEMOIZATION — CLOSURE AS CACHE ────────

function memoize(fn) {
  const cache = {}; // closed over — persists between calls

  return function(...args) {
    const key = JSON.stringify(args);
    if (cache[key] !== undefined) {
      console.log("Cache hit:", key);
      return cache[key];
    }
    const result = fn(...args);
    cache[key] = result;
    return result;
  };
}

function expensiveCalc(n) {
  console.log(`Computing for ${n}...`);
  return n * n * n; // simulate expensive work
}

const memoCalc = memoize(expensiveCalc);
memoCalc(5);  // Computing for 5... → 125
memoCalc(5);  // Cache hit: [5] → 125 (no recompute!)
memoCalc(10); // Computing for 10... → 1000

// ── PARTIAL APPLICATION / CURRYING ────────

function withTax(taxRate) {
  return function(price) {
    return price * (1 + taxRate);
  };
}

const withGST = withTax(0.18);       // 18% GST
const withServiceTax = withTax(0.12); // 12%

withGST(299);         // 352.82
withServiceTax(299);  // 334.88

// ── IIFE — Immediately Invoked Function Expression ───

// Classic module pattern using closure:
const userModule = (() => {
  let users = []; // private
  let idCounter = 1;

  return {
    create(name, email) {
      const user = { id: idCounter++, name, email };
      users.push(user);
      return user;
    },
    getAll() { return [...users]; },
    findById(id) { return users.find(u => u.id === id); },
    count() { return users.length; },
  };
})(); // immediately invoked

userModule.create("Aditya", "a@example.com");
userModule.create("Priya", "p@example.com");
console.log(userModule.count()); // 2
// userModule.users → undefined (private!)

// ── CLOSURE IN LOOPS — THE FIX ───────────

// BUG with var:
for (var i = 1; i <= 3; i++) {
  setTimeout(() => console.log(`var: ${i}`), i * 100);
}
// var: 4, var: 4, var: 4 (all share same var i)

// FIX 1: let (own binding per iteration)
for (let j = 1; j <= 3; j++) {
  setTimeout(() => console.log(`let: ${j}`), j * 100);
}
// let: 1, let: 2, let: 3 ✅

// FIX 2: closure with IIFE (old pattern)
for (var k = 1; k <= 3; k++) {
  ((n) => setTimeout(() => console.log(`iife: ${n}`), n * 100))(k);
}
// iife: 1, iife: 2, iife: 3 ✅

// ── DEBOUNCE — REAL WORLD CLOSURE ────────

function debounce(fn, delay) {
  let timerId; // private via closure

  return function(...args) {
    clearTimeout(timerId);
    timerId = setTimeout(() => fn(...args), delay); // timerId remembered!
  };
}

const handleSearch = debounce((query) => {
  console.log(`Searching for: ${query}`);
  // fetch API call here
}, 300);

// Called on every keystroke — only runs after 300ms of silence:
handleSearch("p");      // timer set
handleSearch("pi");     // previous timer cleared, new set
handleSearch("piz");    // previous cleared, new set
// ... 300ms later: "Searching for: piz" (only once!)
```

---

## 🟠 React/Next.js Connection
```jsx
// ── useState IS A CLOSURE ────────────────

// React's useState works via closures internally
// Each render captures its own closure scope

function Counter() {
  const [count, setCount] = useState(0);

  // handleClick is a new closure each render
  // It "closes over" the current count value
  const handleClick = () => {
    // Using functional update avoids stale closure:
    setCount(prev => prev + 1); // ✅ always gets latest
    // vs setCount(count + 1); // ❌ stale closure if called multiple times
  };

  return <button onClick={handleClick}>Count: {count}</button>;
}

// ── EVENT HANDLERS CLOSE OVER STATE ──────

function OrderCard({ order }) {
  const [status, setStatus] = useState(order.status);

  // Each render creates a new closure for handleCancel
  // It captures the current 'status' value
  const handleCancel = async () => {
    if (status === "preparing") {
      await cancelOrder(order.id);
      setStatus("cancelled");
    }
  };

  return (
    <div>
      <p>Status: {status}</p>
      <button onClick={handleCancel} disabled={status !== "preparing"}>
        Cancel Order
      </button>
    </div>
  );
}

// ── CUSTOM HOOKS ARE CLOSURES ─────────────

function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);

  // These functions close over setCount:
  const increment = useCallback(() => setCount(c => c + 1), []);
  const decrement = useCallback(() => setCount(c => c - 1), []);
  const reset = useCallback(() => setCount(initialValue), [initialValue]);

  return { count, increment, decrement, reset };
}

// ── DEBOUNCE IN REACT ─────────────────────

function SearchBox() {
  const [query, setQuery] = useState("");

  // useMemo/useCallback to avoid recreating debounce on each render:
  const debouncedSearch = useCallback(
    debounce((q) => {
      console.log("Fetching:", q);
      // fetch API
    }, 300),
    [] // created once, persists
  );

  return (
    <input
      value={query}
      onChange={(e) => {
        setQuery(e.target.value);
        debouncedSearch(e.target.value); // closure remembers the timer!
      }}
    />
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Stale closure in React
```javascript
// WRONG: count is captured at render time (stale closure)
function BadCounter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCount(count + 1); // ❌ 'count' is always 0 (captured from first render)
    }, 1000);
    return () => clearInterval(timer);
  }, []); // empty deps — closure captures count=0 forever
}

// CORRECT: functional update (no stale closure)
function GoodCounter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCount(prev => prev + 1); // ✅ always gets latest
    }, 1000);
    return () => clearInterval(timer);
  }, []);
}
```

❌ **Mistake 2:** Memory leaks — closures keeping large objects alive
```javascript
function processLargeData() {
  const bigArray = new Array(1000000).fill("data"); // 1M items

  return function() {
    // Only needs the length, but entire bigArray is kept alive!
    return bigArray.length;
  };
}

// Fix: extract only what's needed
function processLargeData() {
  const bigArray = new Array(1000000).fill("data");
  const length = bigArray.length; // extract before closure

  return function() {
    return length; // bigArray can be garbage collected
  };
}
```

❌ **Mistake 3:** Expecting all closures to share state
```javascript
// WRONG assumption: all counters share same count
const counter1 = makeCounter();
const counter2 = makeCounter();

counter1.increment(); // 1
counter2.increment(); // 1 (NOT 2 — each has independent state!)
```

---

## 🧠 Tricky Interview Output Question
```javascript
function makeAdder(x) {
  return function(y) {
    return x + y;
  };
}

const add5 = makeAdder(5);
const add10 = makeAdder(10);

console.log(add5(3));          // ?
console.log(add10(3));         // ?
console.log(add5(add10(2)));   // ?
```
**Answer:**
```
8    ← add5(3): x=5, y=3 → 8
13   ← add10(3): x=10, y=3 → 13
17   ← add10(2)=12, add5(12): x=5, y=12 → 17
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a closure and give a practical example?**
A1: A closure is a function that retains access to its outer scope's variables even after the outer function has returned. Practical example: a counter factory — `function makeCounter() { let n=0; return () => ++n; }`. The returned arrow function closes over `n` — each call to `makeCounter()` creates a separate `n` (private state).

**Q2: How is closure different from just having access to outer scope?**
A2: Regular scope access (lexical scope) means inner functions CAN see outer variables while the outer function is still executing. Closure is specifically about what happens AFTER the outer function returns — the inner function keeps a reference to those outer variables, preventing them from being garbage collected. Closure = scope access that outlives the outer function's execution.

**Q3: What are practical uses of closures?**
A3: (1) **Private state/encapsulation** — hide implementation details, expose only methods. (2) **Factory functions** — `makeAdder(5)` creates specialized functions. (3) **Memoization/caching** — store results privately. (4) **Event handlers** — remember which item was clicked. (5) **Debounce/throttle** — remember timer IDs privately. (6) **React hooks** — `useState`, `useCallback`, `useEffect` all use closures internally.

**Q4: What is a stale closure and how do you fix it in React?**
A4: A stale closure captures an old value of a variable and keeps using it even after the variable has been updated. Common in React: `useEffect` with empty deps captures the initial state value. Fix: (1) Include the dependency in the deps array. (2) Use functional updates: `setState(prev => prev + 1)` instead of `setState(count + 1)`. (3) Use `useRef` for values that shouldn't trigger re-renders.

**Q5: Can closures cause memory leaks?**
A5: Yes — if a closure holds a reference to a large object (like a DOM element, large array), that object can't be garbage collected as long as the closure exists. Common sources: event listeners added but never removed, timers not cleared, large data captured unnecessarily. Fix: extract only what you need before the closure, or nullify references when done.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Closures in JS](https://www.youtube.com/results?search_query=closures+javascript+akshay+saini+namaste) | Deep dive with examples |
| 📺 YouTube | [Fireship — JavaScript Closures](https://www.youtube.com/results?search_query=closures+javascript+fireship) | 5-min visual explanation |
| 📝 Article | [javascript.info — Closure](https://javascript.info/closure) | Complete closure chapter |
| 📝 Article | [MDN — Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures) | Official reference with examples |
| 📖 Book | [You Don't Know JS — Scope & Closures](https://github.com/getify/You-Dont-Know-JS/tree/2nd-ed/scope-closures) | Deep understanding |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Closure | Function + its outer scope memory | Function + outer scope की memory |
| Close over | Capture outer variable reference | Outer variable को capture करना |
| Private state | Data not accessible from outside | बाहर से accessible न हो |
| Stale closure | Old captured value, not updated | पुरानी value पकड़े रखना |
| Factory function | Returns specialized functions | Specialized functions बनाना |
| Memoization | Cache results via closure | Results cache करना |
| Garbage collection | Memory freed when no references | Memory free होना |

---

## ⚡ 3-Line Summary
**English:**
1. A closure = inner function + reference to outer scope variables — outer function's variables live as long as inner function lives.
2. Key uses: private state (counters, carts), factory functions (makeAdder), memoization, debounce, React hooks.
3. Stale closure = capturing old value — fix with functional setState (`prev => prev + 1`) or proper deps in useEffect.

**Hindi:**
1. Closure = inner function + outer scope variables की reference — outer function की variables तब तक जीती हैं।
2. Key uses: private state (counters, carts), factory functions, memoization, debounce, React hooks।
3. Stale closure = पुरानी value capture — fix: functional setState (`prev => prev + 1`) या useEffect में proper deps।

---

## ➡️ Next Topic
**31. `this` Keyword** — `this` का value कहाँ और क्यों बदलता है — most confusing JS concept।
