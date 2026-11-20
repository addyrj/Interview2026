# 83. Extending Express Request (Declaration Merging)
# हिंदी में: Express Request को Extend करना (Declaration Merging)

> Verified with **TypeScript 5.9.x** and `@types/express`. Interface merging is old TS; `declare global` works in any module file.

---

## 🔵 Simple Definition (English)
Auth middleware usually does `req.user = decodedToken`. But `Request` has no `user` property, so TS errors. **Declaration merging** lets you re-open the `Express.Request` interface (declared inside `@types/express-serve-static-core`'s global `Express` namespace) and **add** your own fields. Interfaces with the same name in the same scope are merged into one.

## 🔵 सरल परिभाषा (Hindi)
Auth middleware आम तौर पर `req.user = decodedToken` करता है। लेकिन `Request` में `user` property नहीं है, इसलिए TS error देता है। **Declaration merging** से आप global `Express` namespace का `Express.Request` interface दोबारा खोलकर अपनी fields **जोड़** सकते हैं। एक ही scope में एक ही नाम के interfaces मिलकर एक बन जाते हैं।

---

## 🔴 Problem it Solves
Without merging, devs write `(req as any).user` everywhere — losing all type safety — or create a custom `AuthRequest extends Request` and annotate every handler (and Express's `app.get` generics then fight them). Merging gives one global, always-correct `req.user` type that every handler and middleware sees.

## 🔴 यह क्यों बना? (Hindi)
Merging के बिना devs हर जगह `(req as any).user` लिखते हैं — सारी type safety खो जाती है — या custom `AuthRequest extends Request` बनाकर हर handler annotate करते हैं (और Express generics उनसे टकराते हैं)। Merging एक global, हमेशा सही `req.user` type देती है जो हर handler और middleware को दिखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create `src/types/express.d.ts` (or any `.ts` file included by tsconfig).
Step 2 → Make it a **module** (add `export {}`) and use `declare global { namespace Express { interface Request { ... } } }`.
Step 3 → Add your fields as **optional** if middleware may not have run (`user?: AuthUser`), or required if all routes are behind auth.
Step 4 → Ensure tsconfig `include` covers that file (otherwise the augmentation is silently not loaded).
Step 5 → Middleware sets `req.user`; handlers read it. Narrow the optional with `if (!req.user) return ...`.
Step 6 → Under `tsx` no type-check happens — confirm with `tsc --noEmit` in CI.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `src/types/express.d.ts` (या कोई भी `.ts` file जो tsconfig में included हो) बनाओ।
Step 2 → उसे **module** बनाओ (`export {}`) और `declare global { namespace Express { interface Request { ... } } }` लिखो।
Step 3 → Fields **optional** रखो अगर middleware न चला हो (`user?: AuthUser`), या सब routes auth के पीछे हों तो required।
Step 4 → tsconfig `include` में वो file आनी चाहिए (वरना augmentation चुपचाप load नहीं होता)।
Step 5 → Middleware `req.user` set करे; handlers पढ़ें। Optional को `if (!req.user) return ...` से narrow करो।
Step 6 → `tsx` में type-check नहीं होता — CI में `tsc --noEmit` से confirm करो।

---

## 🟡 Real World Example
A **Razorpay dashboard API**: `authenticate` middleware verifies a JWT and sets `req.user = { id, merchantId, role }`; `requestId` middleware sets `req.id`. Every route handler — refunds, settlements, payouts — can now read `req.user.merchantId` with full autocomplete and no casts.

## 🟡 Real Example Hindi mein
**Razorpay dashboard API**: `authenticate` middleware JWT verify करके `req.user = { id, merchantId, role }` set करता है; `requestId` middleware `req.id` set करता है। हर route handler — refunds, settlements, payouts — अब `req.user.merchantId` को पूरे autocomplete के साथ, बिना cast, पढ़ सकता है।

---

## 💻 Code Example — Basic

```typescript
// ❌ Without augmentation: Request has no `user`
import express from "express";
const app = express();
app.get("/me", (req, res) => {
  res.json({ id: req.user.id });
  // error TS2339: Property 'user' does not exist on type 'Request<{}, any, any, ParsedQs, Record<string, any>>'.
});
```

```typescript
// src/types/express.d.ts — the augmentation file
export {}; // makes this file a MODULE, which is required for `declare global`

// Shape of the authenticated user we attach in middleware
interface AuthUser { id: string; merchantId: string; role: "admin" | "viewer" }

declare global {
  namespace Express {            // @types/express-serve-static-core extends this global namespace
    interface Request {          // same name => MERGES with the existing interface
      user?: AuthUser;           // optional: not set on public routes
      requestId: string;         // required: our first middleware always sets it
    }
  }
}
```

```typescript
// src/routes.ts — after the augmentation is included, everything is typed
import express from "express";

const app = express();

// Declare the augmentation inline here so this block compiles on its own
declare global {
  namespace Express {
    interface Request { user?: { id: string; merchantId: string; role: "admin" | "viewer" }; requestId: string }
  }
}

app.get("/me", (req, res) => {
  if (!req.user) {                                 // optional => must narrow first
    res.status(401).json({ error: "Login required" });
    return;                                        // stop
  }
  res.json({ id: req.user.id, merchant: req.user.merchantId, reqId: req.requestId }); // all typed
});
```

## 💻 Code Example — Advanced

```typescript
// auth.ts — middleware that SETS the merged properties, with a runtime-safe guard
import type { Request, Response, NextFunction, RequestHandler } from "express";

interface AuthUser { id: string; merchantId: string; role: "admin" | "viewer" } // domain type

declare global {
  namespace Express {
    interface Request { user?: AuthUser; requestId: string } // merged into every Request
  }
}

// Fake token decoder (in real code: jsonwebtoken.verify returns string | JwtPayload)
function decode(token: string): AuthUser | null {
  return token === "valid" ? { id: "u1", merchantId: "m9", role: "admin" } : null;
}

// Sets requestId on every request
export const requestId: RequestHandler = (req, _res, next) => {
  req.requestId = crypto.randomUUID(); // assignment is type-checked: must be string
  next();
};

// Verifies Bearer token and attaches user
export const authenticate: RequestHandler = (req: Request, res: Response, next: NextFunction) => {
  const header = req.header("authorization");         // string | undefined
  const token = header?.startsWith("Bearer ") ? header.slice(7) : undefined; // extract
  const user = token ? decode(token) : null;           // AuthUser | null
  if (!user) {
    res.status(401).json({ error: "Unauthorized" });   // stop chain
    return;
  }
  req.user = user;                                     // typed assignment
  next();                                              // continue
};

// Role guard factory: after authenticate, user is still typed optional => narrow once here
export function requireRole(role: AuthUser["role"]): RequestHandler {
  return (req, res, next) => {
    if (req.user?.role !== role) {                     // optional chaining handles undefined
      res.status(403).json({ error: "Forbidden" });
      return;
    }
    next();
  };
}
```

```typescript
// Alternative without globals: module augmentation of the package itself (no `namespace Express`)
import "express-serve-static-core"; // forces this file to be a module that references the package

declare module "express-serve-static-core" {
  interface Request {
    tenantId?: string; // merged into the SAME interface Express's Request extends
  }
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// server.ts — wire it all up (middleware order matters)
import express from "express";
import { requestId, authenticate, requireRole } from "./auth.js";

const app = express();
app.use(express.json());   // body parser
app.use(requestId);        // 1) every request gets an id
app.use("/api", authenticate); // 2) everything under /api needs a user

app.get("/api/settlements", requireRole("admin"), (req, res) => {
  // req.user is optional in the type, so use `?.` or `!` consciously (we know authenticate ran)
  res.json({ merchantId: req.user?.merchantId, requestId: req.requestId });
});

app.listen(4000);
```

```typescript
// React side: the SAME role union can be shared so the UI hides buttons the API would reject
// shared/roles.ts
export type Role = "admin" | "viewer"; // imported by Express (AuthUser.role) and React

// web/src/RefundButton.tsx
export function RefundButton({ role }: { role: Role }) {
  return role === "admin" ? <button>Refund</button> : null; // viewers never see it; API still enforces
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: The `.d.ts` is not in `include`, or has no top-level `import/export`, so `declare global` is not allowed / not loaded.
✅ Add `export {}` and make sure tsconfig `include` covers it. Symptom: still `TS2339: Property 'user' does not exist on type 'Request<...>'`.

❌ Mistake 2: `(req as any).user = ...` everywhere.
✅ One augmentation; zero casts.

❌ Mistake 3: Declaring `user: AuthUser` (required) when public routes exist — then `req.user.id` compiles on routes where it is `undefined` at runtime. ✅ Use `user?: AuthUser` and narrow, or build a separate typed handler for authenticated routes.

❌ Mistake 4: Augmenting the wrong place — `declare module "express" { interface Request { viaExpress?: string } }` does nothing useful because `Request` there is a *separate* interface that extends core's; handlers' `req` is typed from `express-serve-static-core`. Real tsc output when reading `req.viaExpress` in `app.get(...)`: `error TS2339: Property 'viaExpress' does not exist on type 'Request<{}, any, any, ParsedQs, Record<string, any>>'.`
✅ Use `declare global { namespace Express { ... } }` (simplest) or `declare module "express-serve-static-core"`.

❌ Mistake 5: Believing the merge is validated at runtime. If `authenticate` is forgotten on a route, `req.requestId` (declared required) is `undefined` at runtime. ✅ Required fields must be guaranteed by app-wide middleware registered first.

---

## 🧠 Tricky Interview Question
**Q:** "Why can't you augment an interface by writing a second `interface Request {...}` in a normal `.ts` file of your project?"

**A:** Interface merging happens only between declarations in the **same scope**. A top-level `interface Request` in your module is a different, module-local symbol — it does not merge with Express's. To merge, you must target the *same* symbol: the global `Express.Request` namespace member via `declare global`, or the package's module declaration via `declare module "express-serve-static-core"`. Also note: type aliases (`type X = ...`) can **not** merge; only interfaces, namespaces and enums can.

---

## ⚫ Interview Questions + Answers

Q1: What is declaration merging?
A1: When the compiler combines multiple declarations of the same name in the same scope (interfaces, namespace+class/function/enum) into one definition. It is how libraries are extended without editing their source.

Q2: Why `export {}` in the augmentation file?
A2: `declare global` is only valid inside a module. A file with no import/export is a script, whose declarations are already global. `export {}` turns it into a module so you can use `declare global`.

Q3: Optional or required `req.user`?
A3: Optional if any route can run without auth. Required only if you can guarantee the middleware is always applied. Optional + narrowing is safer; alternatives are a custom handler type like `AuthedHandler` that asserts user via an assertion function (topic 28).

Q4: How do you do the same for `res.locals`?
A4: Use the `Locals` generic (`RequestHandler<..., Locals>`) or merge into `Express.Locals` interface (`declare global { namespace Express { interface Locals { requestId: string } } }`).

Q5: The augmentation works in VS Code but `tsx`/`ts-node` fails or `tsc` can't see it. Why?
A5: The file is not in `include`/`files`, or ts-node was run without `--files`. `tsx` doesn't type-check at all so it never complains; CI `tsc --noEmit` is the real check.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cross-cutting request data: `user`, `requestId`, `tenantId`, `locale`
- Extending any third-party interface (Window, process.env via `ProcessEnv`, Express)

❌ Avoid when:
- Data belongs to one route only — pass it via function args / `res.locals`
- You would add many unrelated fields — the global type becomes a dumping ground

---

## 📊 Visual Diagram
```
  @types/express-serve-static-core            your src/types/express.d.ts
  ┌─────────────────────────────┐             ┌─────────────────────────┐
  │ namespace Express {         │             │ declare global {        │
  │   interface Request { ... } │  ◄─MERGE──  │  namespace Express {    │
  └─────────────────────────────┘             │   interface Request {   │
                  │                           │     user?: AuthUser }}} │
                  ▼                           └─────────────────────────┘
        Request = original fields + user? + requestId
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Declaration merging | Same-name declarations combine | एक नाम की declarations जुड़ जाती हैं |
| Module augmentation | Extend a package's types | Package के types बढ़ाना |
| `declare global` | Add to the global scope from a module | Module से global scope में जोड़ना |
| Ambient namespace | Type-only namespace (`Express`) | सिर्फ types वाला namespace |
| `export {}` | Marks file as a module | File को module बनाता है |
| Narrowing | Refining a type via checks | Checks से type छोटा करना |
| Shim | Small compatibility declaration | छोटी compatibility declaration |

---

## ⚡ 3-Line Summary
English:
1. Add fields to Express's `Request` with `declare global { namespace Express { interface Request {...} } }` in a module file.
2. Make it optional unless middleware is guaranteed; ensure the file is in tsconfig `include`.
3. Only interfaces merge (not type aliases) and merging must hit the same symbol — never use `as any` casts.

Hindi:
1. Module file में `declare global { namespace Express { interface Request {...} } }` से Express के `Request` में fields जोड़ो।
2. Optional रखो जब तक middleware की guarantee न हो; file tsconfig `include` में होनी चाहिए।
3. सिर्फ interfaces merge होते हैं (type alias नहीं) और merge उसी symbol पर होना चाहिए — `as any` कभी नहीं।

---

## ➡️ Next Topic
**84. Typed Error Handling in Express** — custom `AppError` classes, async wrappers, and a typed error middleware.
