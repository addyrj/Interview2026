# 81. TypeScript with Node.js + Express Setup
# हिंदी में: Node.js + Express के साथ TypeScript Setup

> Verified with **TypeScript 5.9.x**, `@types/node`, Express 4/5 types, `tsx`. `moduleResolution: "bundler"` is 5.0+.

---

## 🔵 Simple Definition (English)
Setting up TypeScript with Node.js + Express means: install `typescript`, `@types/node`, `@types/express`; write a `tsconfig.json` (strict, `outDir`, `rootDir`); use **`tsx`** (or `ts-node`) for development with auto-reload; and **`tsc`** to build `dist/` for production. Express itself is JavaScript, so its types come from the separate `@types/express` package.

## 🔵 सरल परिभाषा (Hindi)
Node.js + Express के साथ TypeScript setup का मतलब: `typescript`, `@types/node`, `@types/express` install करो; `tsconfig.json` लिखो (strict, `outDir`, `rootDir`); development में **`tsx`** (या `ts-node`) auto-reload के लिए, और production के लिए **`tsc`** से `dist/` बनाओ। Express खुद JavaScript है, इसलिए उसके types अलग package `@types/express` से आते हैं।

---

## 🔴 Problem it Solves
Plain Express apps rely on `req.body` being "whatever" and on developers remembering route param names. Typos (`req.pramas.id`), wrong response shapes, and missing env vars only show up at runtime. A TS setup moves these to **compile time**, gives autocomplete on `req`/`res`, and enforces one build pipeline for local, CI, and Azure App Service.

## 🔴 यह क्यों बना? (Hindi)
Plain Express apps में `req.body` "कुछ भी" हो सकता है और route param names याद रखने पड़ते हैं। Typos (`req.pramas.id`), गलत response shapes और missing env vars सिर्फ runtime पर दिखते हैं। TS setup इन्हें **compile time** पर ले आता है, `req`/`res` पर autocomplete देता है, और local, CI, Azure App Service के लिए एक ही build pipeline देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm init -y`, then `npm i express` and `npm i -D typescript tsx @types/node @types/express`.
Step 2 → Create `tsconfig.json`: `strict`, `target ES2022`, `module NodeNext`, `rootDir src`, `outDir dist`.
Step 3 → Put code in `src/`: split `app.ts` (builds the Express app, exports it) from `server.ts` (calls `listen`). This keeps tests easy.
Step 4 → Scripts: `dev` = `tsx watch src/server.ts`, `build` = `tsc`, `start` = `node dist/server.js`, `typecheck` = `tsc --noEmit`.
Step 5 → Deploy: Azure runs `npm run build && npm start`; set `NODE_OPTIONS=--enable-source-maps` (topic 78).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm init -y`, फिर `npm i express` और `npm i -D typescript tsx @types/node @types/express`।
Step 2 → `tsconfig.json` बनाओ: `strict`, `target ES2022`, `module NodeNext`, `rootDir src`, `outDir dist`।
Step 3 → Code `src/` में: `app.ts` (Express app बनाकर export करे) और `server.ts` (`listen` call करे) अलग रखो। इससे tests आसान होते हैं।
Step 4 → Scripts: `dev` = `tsx watch src/server.ts`, `build` = `tsc`, `start` = `node dist/server.js`, `typecheck` = `tsc --noEmit`।
Step 5 → Deploy: Azure `npm run build && npm start` चलाता है; `NODE_OPTIONS=--enable-source-maps` set करो (topic 78)।

---

## 🟡 Real World Example
A **Zomato-style order service**: `GET /health`, `POST /orders`, `GET /orders/:id`. `app.ts` builds the app (JSON parser, routes, error handler). `server.ts` reads `PORT`, starts listening, and handles `SIGTERM` for graceful shutdown on Azure. Supertest imports `app` from `app.ts` without opening a port.

## 🟡 Real Example Hindi mein
**Zomato जैसी order service**: `GET /health`, `POST /orders`, `GET /orders/:id`। `app.ts` app बनाता है (JSON parser, routes, error handler)। `server.ts` `PORT` पढ़ता है, listen शुरू करता है और Azure पर graceful shutdown के लिए `SIGTERM` संभालता है। Supertest `app.ts` से `app` import करता है, बिना port खोले।

---

## 💻 Code Example — Basic

```json
// tsconfig.json — server-side config (comments are allowed in tsconfig)
{
  "compilerOptions": {
    "target": "ES2022",              // Node 18+/20 supports ES2022 natively
    "module": "NodeNext",            // Node-style modules (ESM/CJS decided by package.json "type")
    "moduleResolution": "NodeNext",  // resolution matches Node: relative imports need .js in ESM
    "rootDir": "src",                // source root
    "outDir": "dist",                // compiled output
    "strict": true,                  // the whole strict family (topic 71)
    "esModuleInterop": true,         // `import express from "express"` works
    "skipLibCheck": true,            // faster, ignores node_modules typing errors
    "sourceMap": true,               // debugging in prod (topic 78)
    "resolveJsonModule": true        // allow `import pkg from "./package.json"`
  },
  "include": ["src"]                 // compile only src/
}
```

```typescript
// src/app.ts — builds and EXPORTS the app (no listen here)
import express, { type Express } from "express"; // `type` import is erased

// Factory function: tests can create fresh apps
export function createApp(): Express {
  const app = express();            // Express instance, typed as Express
  app.use(express.json());          // parse JSON bodies into req.body

  // Health probe for Azure / load balancer; `_req` unused so prefixed with _
  app.get("/health", (_req, res) => {
    res.json({ status: "ok", uptime: process.uptime() }); // typed Response.json
  });

  return app;                       // hand back to server.ts / tests
}
```

```typescript
// src/server.ts — starts the HTTP server
import { createApp } from "./app.js";   // NodeNext ESM: use the .js extension even in .ts files

const port = Number(process.env.PORT ?? 3000); // env vars are string | undefined -> convert + default
const app = createApp();                       // build app

const server = app.listen(port, () => {       // listen returns http.Server
  console.log(`Order service on :${port}`);   // startup log
});

// Graceful shutdown: Azure sends SIGTERM before stopping the container
process.on("SIGTERM", () => {
  server.close(() => process.exit(0));        // stop accepting, finish in-flight, then exit
});
```

## 💻 Code Example — Advanced

```typescript
// src/app.ts (advanced) — typed routes, in-memory store, error handler, 404
import express, { type Express, type Request, type Response, type NextFunction } from "express";

interface Order { id: number; userId: string; total: number } // our domain type
interface CreateOrderBody { userId: string; total: number }   // POST body shape

export function createApp(): Express {
  const app = express();                  // create app
  app.use(express.json());                // body parser
  const orders = new Map<number, Order>(); // fake DB: id -> order
  let nextId = 1;                          // auto-increment id

  // Request<Params, ResBody, ReqBody, Query>  — generics explained in topic 82
  app.post("/orders", (req: Request<{}, Order, CreateOrderBody>, res: Response<Order>) => {
    const order: Order = { id: nextId++, ...req.body }; // spread typed body
    orders.set(order.id, order);                         // store
    res.status(201).json(order);                         // res.json only accepts Order here
  });

  app.get("/orders/:id", (req: Request<{ id: string }>, res: Response<Order | { error: string }>) => {
    const order = orders.get(Number(req.params.id)); // params are ALWAYS strings -> convert
    if (!order) {
      res.status(404).json({ error: "Order not found" }); // early return pattern
      return;                                              // handler returns void in Express 4 types
    }
    res.json(order);                                       // typed success body
  });

  // 404 for unknown routes
  app.use((_req, res) => { res.status(404).json({ error: "Not found" }); });

  // Error middleware: 4 params, `err` is unknown in strict code
  app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
    const message = err instanceof Error ? err.message : "Unknown error"; // narrow unknown
    res.status(500).json({ error: message });                             // consistent error shape
  });

  return app;
}
```

```json
// package.json (scripts + deps excerpt)
{
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": { "express": "^4.19.0" },
  "devDependencies": {
    "typescript": "^5.4.0",
    "tsx": "^4.0.0",
    "@types/node": "^20.0.0",
    "@types/express": "^4.17.21"
  }
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// shared/api-types.ts — ONE file of types shared by Express and React (monorepo or path alias)
export interface Order { id: number; userId: string; total: number } // response shape
export interface CreateOrderBody { userId: string; total: number }   // request shape
```

```typescript
// web/src/api.ts — React side calls the same typed contract
import type { Order, CreateOrderBody } from "../../shared/api-types"; // types only, zero runtime cost

// Typed POST helper used from components / Redux thunks
export async function createOrder(body: CreateOrderBody): Promise<Order> {
  const res = await fetch("/api/orders", {            // proxied to Express by Vite (topic 79)
    method: "POST",                                    // HTTP verb
    headers: { "Content-Type": "application/json" },   // tell Express to parse JSON
    body: JSON.stringify(body),                        // serialize
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);  // fetch does not throw on 4xx/5xx
  return (await res.json()) as Order;                  // res.json() is any; we assert (validate: topic 86)
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `@types/express` — the import compiles to `any`/errors.
✅ `npm i -D @types/express @types/node`. Without them under strict you get `error TS7016: Could not find a declaration file for module 'express'`.

❌ Mistake 2: Treating `req.params.id` as a number.
```typescript
import express from "express";
const app = express();
app.get("/orders/:id", (req, res) => {
  // ❌ params are strings
  const id: number = req.params.id;
  // error TS2322: Type 'string' is not assignable to type 'number'.
  res.json({ id });
});
// ✅ const id = Number(req.params.id);
```

❌ Mistake 3: Assuming `req.body` is typed. With no generics it is `any`, so `req.body.total.toFixed(2)` compiles even if `total` is missing — and crashes at runtime. Type the body generic AND validate with zod (topic 86).

❌ Mistake 4: Running `ts-node` in production (slow start, memory).
✅ Build with `tsc`, run `node dist/server.js`.

❌ Mistake 5: Putting `app.listen` inside `app.ts` — tests then open real ports and hang.
✅ Export `createApp()`, call `listen` only in `server.ts`.

---

## 🧠 Tricky Interview Question
**Q:** "With `module: NodeNext` and `"type": "module"`, why does `import { createApp } from './app'` fail, and why do we write `./app.js` in a `.ts` file?"

**A:** In Node's native ESM, relative imports need the **final runtime filename extension**. TS does not rewrite import paths, so you write what Node will see: `./app.js` (TS maps it back to `app.ts` while type-checking). Under `moduleResolution: "bundler"` (Vite/esbuild) extensionless imports are allowed, but plain Node ESM output is not a bundler. Alternatively use CJS (`"type": "commonjs"`, `module: "CommonJS"`), where extensionless works.

---

## ⚫ Interview Questions + Answers

Q1: Why separate `app.ts` and `server.ts`?
A1: So tests (Supertest) can import the app without binding a port, and so the app can be created per-test with different config. `server.ts` owns side effects: listen, signals, DB connect.

Q2: `tsx` vs `ts-node` vs compile with `tsc` — which when?
A2: `tsx` (esbuild-based, no type-check) for fast dev/watch. `ts-node` can type-check but is slow. For production always `tsc` → `node dist`. Keep `tsc --noEmit` in CI since tsx does not type-check.

Q3: Why `@types/node`?
A3: Node's globals (`process`, `Buffer`, `__dirname`) and modules (`fs`, `http`) are not part of the TS lib; `@types/node` declares them. Missing → `Cannot find name 'process'`.

Q4: How do you read env vars safely?
A4: `process.env.X` is `string | undefined`. Parse and validate once at startup (zod, topic 87), export a typed `config` object, never read `process.env` scattered through code.

Q5: Where does the Express `listen` callback/graceful shutdown matter on Azure?
A5: Azure App Service/Container Apps send `SIGTERM` and wait a grace period; `server.close()` stops new connections and lets in-flight requests finish, preventing dropped payments mid-request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any Express service beyond a throwaway script
- Shared contracts with a React frontend (monorepo)

❌ Avoid / consider alternatives when:
- Very small one-file scripts (`tsx script.ts` is enough, no build)
- You need full framework structure/DI: consider NestJS (topic 98)

---

## 📊 Visual Diagram
```
 src/
  ├─ app.ts      createApp(): Express   ◄── imported by tests (Supertest)
  ├─ server.ts   listen(PORT), SIGTERM  ◄── entry point
  └─ routes/ ...
        │ dev:   tsx watch src/server.ts      (no type-check, instant)
        │ ci:    tsc --noEmit                 (type-check)
        └ prod:  tsc → dist/ → node dist/server.js
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `@types/express` | Type declarations for Express | Express के type declarations |
| `tsx` | Run TS directly (dev) | TS को सीधे चलाना (dev) |
| `outDir` / `rootDir` | Output / source folders | Output / source folders |
| `NodeNext` | Node-accurate module mode | Node जैसा module mode |
| Graceful shutdown | Finish requests, then exit | Requests पूरी करके बंद होना |
| App factory | Function that builds the app | App बनाने वाला function |
| `esModuleInterop` | Smooth default imports of CJS | CJS के default imports आसान |

---

## ⚡ 3-Line Summary
English:
1. Install `typescript`, `tsx`, `@types/node`, `@types/express`; use a strict `tsconfig` with `src` to `dist`.
2. Split `app.ts` (factory) from `server.ts` (listen), dev with `tsx`, build with `tsc`, run `node dist`.
3. `req.params` are strings and `req.body` is `any` by default — type and validate them.

Hindi:
1. `typescript`, `tsx`, `@types/node`, `@types/express` install करो; strict `tsconfig` में `src` से `dist`।
2. `app.ts` (factory) और `server.ts` (listen) अलग रखो; dev में `tsx`, build में `tsc`, चलाओ `node dist`।
3. `req.params` strings होते हैं और `req.body` default में `any` — इन्हें type और validate करो।

---

## ➡️ Next Topic
**82. Typing Express Request, Response and Middleware** — the four generics of `Request`, `RequestHandler`, and typed middleware.
