# 34. Error Handling — try/catch/finally, Custom Errors
# हिंदी में: Error Handling — Errors को Gracefully Handle करना

---

## 🔵 Simple Definition (English)
Error handling lets you **catch and respond to runtime errors** instead of crashing. `try` wraps risky code, `catch` handles errors, `finally` always runs (cleanup). Custom errors extend `Error` for domain-specific error types.

## 🔵 सरल परिभाषा (Hindi)
Error handling आपको runtime errors को **catch करके respond** करने देता है — app crash नहीं होता। `try` risky code को wrap करता है, `catch` error handle करता है, `finally` हमेशा run होता है (cleanup)। Custom errors domain-specific error types के लिए `Error` extend करते हैं।

---

## 🔴 Problem it Solves
```javascript
// Without try/catch:
const data = JSON.parse("invalid json"); // crashes entire app!

// With try/catch:
try {
  const data = JSON.parse("invalid json");
} catch (e) {
  console.log("Invalid JSON, using defaults"); // graceful
}
```

---

## 🟢 How it Works

```javascript
try {
  // Code that might throw
} catch (error) {
  // Runs only if try throws — error object available here
  // error.name, error.message, error.stack
} finally {
  // ALWAYS runs — with or without error
  // Use for cleanup (close connections, hide loading spinner)
}
```

---

## 🟡 Real World Example
```javascript
async function placeOrder(userId, cartId) {
  let connection;
  try {
    connection = await db.connect();
    const cart = await Cart.findById(cartId);

    if (!cart) throw new NotFoundError("Cart", cartId);
    if (cart.items.length === 0) throw new ValidationError("Cart is empty");

    const order = await Order.create({ userId, items: cart.items });
    await cart.delete();
    return { success: true, orderId: order.id };

  } catch (error) {
    if (error instanceof ValidationError) {
      return { success: false, message: error.message, code: 400 };
    }
    if (error instanceof NotFoundError) {
      return { success: false, message: error.message, code: 404 };
    }
    console.error("Unexpected error:", error);
    return { success: false, message: "Order failed", code: 500 };

  } finally {
    if (connection) await connection.close(); // always close!
  }
}
```

---

## 💻 Code Example — Basic
```javascript
// ── TRY/CATCH BASICS ─────────────────────

// Synchronous:
try {
  const result = JSON.parse('{"name": "Aditya"}');
  console.log(result.name); // "Aditya"
} catch (error) {
  console.log("Parse failed:", error.message);
}

try {
  JSON.parse("not valid json!"); // throws SyntaxError
} catch (error) {
  console.log(error.name);    // "SyntaxError"
  console.log(error.message); // "Unexpected token n in JSON at position 0"
  console.log(error.stack);   // stack trace string
}

// ── FINALLY ──────────────────────────────

function readFile(filename) {
  let file = null;
  try {
    file = openFile(filename);
    return processFile(file); // may throw
  } catch (error) {
    console.error("Error reading file:", error.message);
    return null;
  } finally {
    if (file) file.close(); // ALWAYS runs — even on return/throw
    console.log("Cleanup done");
  }
}
// "Cleanup done" prints whether or not error occurred

// ── THROW ────────────────────────────────

// Can throw anything — but always throw Error objects:
throw new Error("Something went wrong");
throw new TypeError("Expected a number");
throw new RangeError("Value out of range");

// AVOID: throwing non-errors (no stack trace, no type info)
// throw "something went wrong"; // ❌ hard to handle
// throw { code: 500 };          // ❌ better to extend Error

// ── BUILT-IN ERROR TYPES ─────────────────

// Error — generic base
// TypeError — wrong type: null.property, arr.nonMethod()
// ReferenceError — undefined variable
// SyntaxError — invalid syntax (caught at parse time usually)
// RangeError — out of bounds: new Array(-1), toFixed(200)
// URIError — invalid URI component

try { null.toString(); }         catch(e) { console.log(e.name); } // TypeError
try { undeclaredVar; }           catch(e) { console.log(e.name); } // ReferenceError
try { new Array(-1); }           catch(e) { console.log(e.name); } // RangeError

// ── CUSTOM ERRORS ────────────────────────

class AppError extends Error {
  constructor(message, statusCode = 500, code = "INTERNAL_ERROR") {
    super(message);
    this.name = this.constructor.name; // "AppError" not "Error"
    this.statusCode = statusCode;
    this.code = code;
  }
}

class ValidationError extends AppError {
  constructor(message, fields = {}) {
    super(message, 400, "VALIDATION_ERROR");
    this.fields = fields;
  }
}

class NotFoundError extends AppError {
  constructor(resource, id) {
    super(`${resource} with id "${id}" not found`, 404, "NOT_FOUND");
  }
}

class AuthError extends AppError {
  constructor(message = "Not authenticated") {
    super(message, 401, "UNAUTHORIZED");
  }
}

// Usage:
try {
  throw new ValidationError("Invalid input", { email: "Email is required" });
} catch (error) {
  if (error instanceof ValidationError) {
    console.log(error.fields); // { email: "Email is required" }
    console.log(error.statusCode); // 400
  }
}
```

## 💻 Code Example — Advanced
```javascript
// ── ASYNC/AWAIT ERROR HANDLING ────────────

// With try/catch:
async function fetchUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new NotFoundError("User", id); // custom error
    }
    const user = await response.json();
    return { data: user, error: null };
  } catch (error) {
    return { data: null, error: error.message };
  }
}

// ── ERROR BOUNDARY PATTERN ────────────────

// Wrap async with error handling — functional approach
async function withError(promise) {
  try {
    const data = await promise;
    return [null, data]; // [error, data] — Go-style
  } catch (error) {
    return [error, null];
  }
}

// Clean usage:
const [err, user] = await withError(fetchUser(123));
if (err) {
  console.log("Failed:", err.message);
} else {
  console.log("User:", user.name);
}

// ── GLOBAL ERROR HANDLERS ────────────────

// Browser — catch uncaught errors:
window.addEventListener("error", (event) => {
  console.error("Uncaught error:", event.error);
  // Send to error tracking service
  Sentry.captureException(event.error);
});

// Browser — catch unhandled promise rejections:
window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled rejection:", event.reason);
  event.preventDefault(); // prevent default browser error
});

// Node.js:
process.on("uncaughtException", (error) => {
  console.error("Uncaught:", error);
  process.exit(1); // MUST exit — app is in unknown state
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled rejection at:", promise, "reason:", reason);
});

// ── ERROR CHAINING ───────────────────────

class DatabaseError extends AppError {
  constructor(message, originalError) {
    super(message, 500, "DB_ERROR");
    this.cause = originalError; // preserve original error
  }
}

async function findUser(id) {
  try {
    return await db.users.findById(id);
  } catch (error) {
    throw new DatabaseError(`Failed to fetch user ${id}`, error);
    // Original error preserved in .cause
  }
}

// ── RETRY PATTERN WITH ERRORS ─────────────

async function withRetry(fn, retries = 3, delay = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === retries - 1) throw error; // last attempt — rethrow
      if (error instanceof ValidationError) throw error; // don't retry validation errors
      await new Promise(r => setTimeout(r, delay * (i + 1))); // exponential backoff
      console.log(`Retry ${i + 1}/${retries}...`);
    }
  }
}

const data = await withRetry(() => fetchExternalAPI(), 3, 500);
```

---

## 🟠 React/Next.js Connection
```jsx
// ── ERROR BOUNDARIES (Class Component) ───

class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("Component error:", error, info.componentStack);
    // Log to error tracking: Sentry.captureException(error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-page">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Usage:
function App() {
  return (
    <ErrorBoundary>
      <ProductList /> {/* if this crashes, ErrorBoundary catches it */}
    </ErrorBoundary>
  );
}

// ── API ROUTES — EXPRESS STYLE ─────────────
function errorHandler(error, req, res, next) {
  if (error instanceof ValidationError) {
    return res.status(400).json({
      error: error.message,
      code: error.code,
      fields: error.fields,
    });
  }

  if (error instanceof NotFoundError) {
    return res.status(404).json({ error: error.message, code: error.code });
  }

  if (error instanceof AuthError) {
    return res.status(401).json({ error: error.message });
  }

  // Unexpected error — don't expose internals
  console.error("Unexpected:", error);
  res.status(500).json({ error: "Internal server error" });
}

app.use(errorHandler); // register last

// ── NEXT.JS API ROUTES ─────────────────────
export async function POST(req) {
  try {
    const body = await req.json();

    if (!body.email) {
      throw new ValidationError("Validation failed", { email: "Required" });
    }

    const user = await createUser(body);
    return Response.json({ user }, { status: 201 });

  } catch (error) {
    if (error instanceof AppError) {
      return Response.json(
        { error: error.message, code: error.code },
        { status: error.statusCode }
      );
    }
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Swallowing errors silently
```javascript
// WRONG: hides the bug!
try {
  riskyOperation();
} catch (e) {
  // nothing here — error disappears
}

// CORRECT: at minimum, log
try {
  riskyOperation();
} catch (e) {
  console.error("Operation failed:", e);
  // OR rethrow: throw e; OR throw new AppError(...)
}
```

❌ **Mistake 2:** Using `catch` for control flow
```javascript
// WRONG: using try/catch to check if something exists
try {
  user.address.city; // throws if address is null
} catch {
  city = "Unknown"; // using error for normal flow!
}

// CORRECT: check first
const city = user?.address?.city ?? "Unknown";
```

❌ **Mistake 3:** Not handling async errors
```javascript
// WRONG: unhandled rejection
async function fetchData() {
  const data = await fetch("/api/data").then(r => r.json()); // no catch!
  return data;
}

// CORRECT: handle errors
async function fetchData() {
  try {
    const response = await fetch("/api/data");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Fetch failed:", error);
    throw error; // rethrow for caller to handle
  }
}
```

---

## 🧠 Tricky Interview Output Question
```javascript
function riskyOp() {
  try {
    throw new Error("oops");
  } catch (e) {
    console.log("caught:", e.message);
    return "from catch";
  } finally {
    console.log("finally runs");
    // return "from finally"; // if uncommented, overrides catch return!
  }
}

console.log(riskyOp());
```
**Answer:**
```
"caught: oops"
"finally runs"
"from catch"
```
**Why:** `finally` runs BEFORE the `return "from catch"` completes. If `finally` had its own `return`, it would override the catch return.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between try/catch and `.catch()` on promises?**
A1: Both catch errors, but in different contexts. `try/catch` works with `async/await` syntax — the `await` expression turns a rejected promise into a thrown error. `.catch()` is the Promise chain method. With async/await, `try/catch` is usually cleaner. Both can be combined: `try { await promise } catch (e) {}` is equivalent to `promise.catch(e => ...)`.

**Q2: What always executes in a try/catch/finally?**
A2: `finally` always executes, regardless of whether an error was thrown, caught, or not. Even if `try` or `catch` has a `return` statement, `finally` runs before the function actually returns. If `finally` itself has a `return`, it **overrides** any return from `try` or `catch`. Use `finally` for cleanup that must happen regardless (close database connections, hide loading spinners, release resources).

**Q3: Why create custom error classes?**
A3: Custom errors give you: (1) **Type checking** — `instanceof ValidationError` lets handlers respond specifically. (2) **Extra properties** — `statusCode`, `code`, `fields` for structured error info. (3) **Better names** — `error.name === "ValidationError"` vs "Error". (4) **Separation of concerns** — HTTP status codes stay in error class, not scattered throughout business logic. Centralized, consistent error handling.

**Q4: What is the difference between throwing an Error vs throwing a plain value?**
A4: Always throw `Error` objects (or subclasses). Throwing a plain value like `throw "message"` or `throw { code: 404 }` loses: (1) Stack trace (the most valuable debugging info). (2) `name` property. (3) `instanceof` type checking. (4) Error tracking tools (Sentry, etc.) expect Error objects. Rule: always `throw new Error(...)` or custom error classes.

**Q5: How do you handle errors in a React component?**
A5: (1) **Error Boundaries** — class components with `componentDidCatch` and `getDerivedStateFromError` — catches render-time errors in child components. (2) `try/catch` in event handlers and async functions. (3) Display error states with `useState`: `const [error, setError] = useState(null)`. (4) React Query / SWR handle async errors automatically with `isError`/`error` return values.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📝 Article | [javascript.info — Error handling](https://javascript.info/error-handling) | Complete try/catch guide |
| 📝 Article | [MDN — Error types](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error) | All built-in error types |
| 📺 YouTube | [Fireship — Error handling](https://www.youtube.com/results?search_query=javascript+error+handling+async+await+fireship) | Async errors explained |
| 📝 Article | [React — Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary) | Official React error boundary docs |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| try/catch | Error catching block | Error पकड़ने का block |
| finally | Always runs, cleanup | हमेशा run होता है, cleanup |
| throw | Manually trigger an error | Error manually trigger करना |
| Custom error | Extended Error class | Extended Error class |
| Error boundary | React's render error catcher | React का render error catcher |
| Unhandled rejection | Promise error not caught | Promise error जो catch न हो |
| Stack trace | Error call history | Error की call history |

---

## ⚡ 3-Line Summary
**English:**
1. `try/catch/finally` — wrap risky code, handle errors, always cleanup. `finally` runs even with `return`.
2. Create custom error classes extending `Error` — add `statusCode`, `code`, `fields` for structured handling with `instanceof`.
3. Never silently swallow errors; always handle async errors; use Error Boundaries in React for render-time crashes.

**Hindi:**
1. `try/catch/finally` — risky code wrap, errors handle, cleanup हमेशा। `finally` `return` पर भी run करता है।
2. `Error` extend करके custom error classes बनाओ — `statusCode`, `code`, `fields` add करो structured handling के लिए।
3. Errors कभी silently ignore मत करो; async errors हमेशा handle करो; React में render crashes के लिए Error Boundaries।

---

## ➡️ Next Topic
**35. Modules — import/export, CommonJS vs ES Modules** — JavaScript module system — code organize और share करना। (02-intermediate/ folder शुरू)
