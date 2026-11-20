# 87. Typed Environment Config
# हिंदी में: Typed Environment Config

> Verified with **TypeScript 5.9.x**, **zod 4.x**, `@types/node`. Outputs are real `tsx` runs. `node --env-file` needs Node 20.6+; `process.loadEnvFile` Node 21.7+/20.12+.

---

## 🔵 Simple Definition (English)
Environment variables (`process.env.X`) are **always `string | undefined`** — never numbers or booleans, and they might be missing. A **typed environment config** reads and **validates** them **once at startup**, converts them (`"8080"` → `8080`, `"true"` → `true`), applies defaults, and exports a single immutable, fully typed `config` object. The app crashes immediately with a clear message if something is wrong.

## 🔵 सरल परिभाषा (Hindi)
Environment variables (`process.env.X`) **हमेशा `string | undefined`** होते हैं — कभी number या boolean नहीं, और missing भी हो सकते हैं। **Typed environment config** उन्हें **startup पर एक बार** पढ़कर **validate** करता है, convert करता है (`"8080"` → `8080`, `"true"` → `true`), defaults लगाता है, और एक immutable, पूरी तरह typed `config` object export करता है। कुछ गलत हो तो app तुरंत साफ़ message के साथ crash हो जाता है।

---

## 🔴 Problem it Solves
Scattered `process.env.PORT` reads cause: `PORT` typo → `undefined` at 3 AM; `Number(process.env.TIMEOUT)` → `NaN`; `process.env.ENABLE_X === true` never true; missing `DB_URL` discovered only when the first request hits the DB, after the deploy "succeeded". Validate-at-boot fails fast (the Azure slot swap never goes live) and removes every `?? ""` and `!` from the codebase.

## 🔴 यह क्यों बना? (Hindi)
बिखरे हुए `process.env.PORT` reads से: `PORT` की typo → रात 3 बजे `undefined`; `Number(process.env.TIMEOUT)` → `NaN`; `process.env.ENABLE_X === true` कभी true नहीं; `DB_URL` missing हो तो पहली request पर पता चलता है, जबकि deploy "सफल" दिख चुका। Boot पर validate करने से जल्दी fail होता है (Azure slot swap live ही नहीं होता) और पूरे codebase से `?? ""` और `!` हट जाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Load `.env` in dev (`node --env-file=.env`, `dotenv`, or Azure App Settings in prod). Nothing is typed yet: `process.env` is `NodeJS.ProcessEnv` (`string | undefined` values).
Step 2 → Define a zod schema: required (`z.string().min(1)`), numbers (`z.coerce.number()`), enums (`z.enum([...])`), defaults (`.default(...)`).
Step 3 → Parse `process.env` **once** in `src/config.ts`; on failure print **all** problems and `process.exit(1)` / throw.
Step 4 → Export `config` (frozen). Type = `z.infer<typeof EnvSchema>`.
Step 5 → Import `config` everywhere; never touch `process.env` elsewhere (add an ESLint rule `no-process-env`).
Step 6 → Optionally augment `NodeJS.ProcessEnv` so direct reads at least autocomplete; and expose only safe parts to the browser (Vite: `import.meta.env.VITE_*`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Dev में `.env` load करो (`node --env-file=.env`, `dotenv`, या prod में Azure App Settings)। अभी कुछ typed नहीं: `process.env` का type `NodeJS.ProcessEnv` है (values `string | undefined`)।
Step 2 → Zod schema बनाओ: required (`z.string().min(1)`), numbers (`z.coerce.number()`), enums (`z.enum([...])`), defaults (`.default(...)`)।
Step 3 → `src/config.ts` में `process.env` **एक बार** parse करो; fail हो तो **सारी** problems print करके `process.exit(1)` / throw।
Step 4 → `config` export करो (frozen)। Type = `z.infer<typeof EnvSchema>`।
Step 5 → हर जगह `config` import करो; और कहीं `process.env` नहीं छुओ (ESLint rule `no-process-env`)।
Step 6 → Optionally `NodeJS.ProcessEnv` augment करो ताकि direct reads में autocomplete मिले; browser को सिर्फ safe हिस्से दो (Vite: `import.meta.env.VITE_*`)।

---

## 🟡 Real World Example
A **Swiggy order service** needs `DB_URL` (SQL Server connection string), `JWT_SECRET` (≥ 16 chars), `PORT`, `NODE_ENV`, and a feature flag `ENABLE_COUPONS`. A staging deploy on Azure forgot `JWT_SECRET`. Because config validates at boot, the new slot never became healthy, so the swap was blocked and production stayed on the old version. Without validation, logins would have failed with `secretOrPrivateKey must have a value` for real users.

## 🟡 Real Example Hindi mein
**Swiggy order service** को `DB_URL` (SQL Server connection string), `JWT_SECRET` (≥ 16 chars), `PORT`, `NODE_ENV` और feature flag `ENABLE_COUPONS` चाहिए। Azure staging deploy में `JWT_SECRET` भूल गए। Config boot पर validate होता है, इसलिए नया slot कभी healthy नहीं हुआ, swap रुक गया और production पुराने version पर बना रहा। Validation न होती तो असली users के logins `secretOrPrivateKey must have a value` से fail होते।

---

## 💻 Code Example — Basic

```typescript
// ❌ Raw process.env is string | undefined — the compiler stops the obvious mistakes
const env = { PORT: process.env.PORT };
const p: number = env.PORT;
// error TS2322: Type 'string | undefined' is not assignable to type 'number'.
//   Type 'undefined' is not assignable to type 'number'.
const url = process.env.DB_URL.toLowerCase();
// error TS18048: 'process.env.DB_URL' is possibly 'undefined'.
```

```typescript
// config.ts — validate once, export typed config. Run: DB_URL=x JWT_SECRET=... npx tsx config.ts
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"), // union type, default
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),                   // "8080" -> 8080
  DB_URL: z.string().min(1),                                                       // required, no default (secret!)
  JWT_SECRET: z.string().min(16),                                                  // enforce minimum strength
  // env booleans are strings: parse explicitly (z.coerce.boolean() would make "false" => true!)
  ENABLE_COUPONS: z.enum(["true", "false"]).default("false").transform((v) => v === "true"),
});

export type Env = z.infer<typeof EnvSchema>; // { NODE_ENV: ...; PORT: number; ...; ENABLE_COUPONS: boolean }

// Pure function taking the source => easy to unit test (no global state)
export function loadEnv(source: Record<string, string | undefined>): Env {
  const r = EnvSchema.safeParse(source);                       // validate everything at once
  if (!r.success) {
    const lines = r.error.issues.map((i) => `  ${i.path.join(".")}: ${i.message}`); // one line per problem
    throw new Error(`Invalid environment:\n${lines.join("\n")}`);
  }
  return r.data;                                               // typed + coerced
}

// Real output of these two calls (tsx):
console.log(loadEnv({ DB_URL: "Server=tcp:db", JWT_SECRET: "a-very-long-secret-1", PORT: "8080", ENABLE_COUPONS: "true" }));
// {
//   NODE_ENV: 'development',
//   PORT: 8080,
//   DB_URL: 'Server=tcp:db',
//   JWT_SECRET: 'a-very-long-secret-1',
//   ENABLE_COUPONS: true
// }
try { loadEnv({ PORT: "abc" }); } catch (e) { console.log((e as Error).message); }
// Invalid environment:
//   PORT: Invalid input: expected number, received NaN
//   DB_URL: Invalid input: expected string, received undefined
//   JWT_SECRET: Invalid input: expected string, received undefined
```

## 💻 Code Example — Advanced

```typescript
// config.ts (production style) — singleton, frozen, secret-safe logging, per-environment rules
import { z } from "zod";

const Base = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().default(3000),
  DB_URL: z.string().min(1),
  JWT_SECRET: z.string().min(16),
  REDIS_URL: z.string().url().optional(),                  // optional integration
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
});

// Cross-field rule: in production, REDIS_URL becomes mandatory
const EnvSchema = Base.superRefine((e, ctx) => {
  if (e.NODE_ENV === "production" && !e.REDIS_URL) {
    ctx.addIssue({ code: "custom", path: ["REDIS_URL"], message: "required in production" });
  }
});
type Env = z.infer<typeof EnvSchema>;

// Group into a nested, readable config object for the app
function build(env: Env) {
  return {
    isProd: env.NODE_ENV === "production",                 // derived boolean, computed once
    server: { port: env.PORT },
    db: { url: env.DB_URL },
    auth: { jwtSecret: env.JWT_SECRET },
    redis: env.REDIS_URL ? { url: env.REDIS_URL } : null,  // null when not configured
    log: { level: env.LOG_LEVEL },
  } as const;                                              // readonly literal types
}

const parsed = EnvSchema.safeParse(process.env);           // process.env is NodeJS.ProcessEnv (compatible)
if (!parsed.success) {
  console.error("Invalid environment", z.flattenError(parsed.error).fieldErrors); // do NOT print values (secrets)
  process.exit(1);                                         // fail fast so Azure keeps the old slot
}
export const config = Object.freeze(build(parsed.data));   // immutable at runtime too
export type Config = typeof config;                        // reusable in function signatures (DI)
```

```typescript
// env.d.ts — optional: autocomplete for any remaining direct process.env reads (e.g. in scripts)
export {};                                   // module so `declare global` is legal
declare global {
  namespace NodeJS {
    interface ProcessEnv {                   // merges into @types/node's ProcessEnv (topic 35/83)
      NODE_ENV?: "development" | "test" | "production";
      DB_URL?: string;                       // still optional: the type cannot prove it is set
    }
  }
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// server.ts — consume config, never process.env
import express from "express";

// stand-in for: import { config } from "./config.js";
const config = { server: { port: 3000 }, isProd: false } as const;

const app = express();
app.get("/health", (_req, res) => {
  res.json({ ok: true, env: config.isProd ? "prod" : "dev" }); // typed boolean derived once
});
app.listen(config.server.port); // number, not string | undefined
```

```typescript
// vite-env.d.ts — React/Vite: only VITE_-prefixed vars reach the browser; type them
// (a global script file: NO import/export, so these interfaces merge into the global ones)
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;   // e.g. https://api.myapp.in
  readonly VITE_ENABLE_COUPONS?: "true" | "false";
}
interface ImportMeta { readonly env: ImportMetaEnv } // declaration merging with the built-in ImportMeta
```

```typescript
// src/main.tsx — usage (needs vite-env.d.ts in the program)
const base: string = import.meta.env.VITE_API_BASE_URL; // typed; remember: it is PUBLIC, never put secrets here
console.log(base);
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `process.env.DB_URL!` sprinkled everywhere — the `!` silences the compiler, runtime still gets `undefined`.
✅ Validate once at startup; export typed config.

❌ Mistake 2: `z.coerce.boolean()` for flags — `"false"` becomes `true` (non-empty string).
✅ `z.enum(["true","false"]).transform(v => v === "true")`.

❌ Mistake 3: `Number(process.env.PORT) || 3000` — `PORT=0` becomes 3000 and `PORT=abc` silently falls back.
✅ Schema with `z.coerce.number().int()` fails loudly on garbage.

❌ Mistake 4: Logging the whole config on startup (leaks `JWT_SECRET` into Azure logs).
✅ Log only safe keys, or redact.

❌ Mistake 5: Putting secrets in `VITE_*` — they are inlined into the public JS bundle.
✅ Secrets stay server-side (Azure Key Vault / App Settings), browser gets only public config.

---

## 🧠 Tricky Interview Question
**Q:** "I declared `interface ProcessEnv { DB_URL: string }` via `declare global`. Is `process.env.DB_URL` now safe?"

**A:** No. The augmentation only changes the **compile-time** type; it makes TS believe the variable exists. At runtime it can still be missing, so the type is a lie — worse than `string | undefined` because the compiler no longer warns. The honest options are to keep it optional in the augmentation and validate at startup, or (best) validate with a schema and export a `config` whose type comes from the validated result. Types never validate; only runtime code does.

---

## ⚫ Interview Questions + Answers

Q1: Why is `process.env.X` typed `string | undefined`?
A1: Environment variables are text, and TS can't know which exist. `@types/node` declares `ProcessEnv` as `{ [key: string]: string | undefined }`, so you must handle undefined and convert types yourself.

Q2: Why validate at startup rather than lazily?
A2: Fail fast: a bad deploy crashes before taking traffic (Azure slot swap health check fails), the error lists every missing variable at once, and the rest of the code can trust `config`.

Q3: How do you test code that depends on config?
A3: Make `loadEnv(source)` a pure function of an input record, and pass the `Config` (or pieces) into constructors (dependency injection). Tests call `loadEnv({...})` with fixtures instead of mutating `process.env`.

Q4: dotenv vs `--env-file` vs Azure App Settings?
A4: `dotenv`/`--env-file` load a `.env` file for local dev (never commit it). In Azure App Service, App Settings (and Key Vault references) are injected as real environment variables, so no file is needed in prod.

Q5: How are frontend env vars different?
A5: Vite/CRA/Next inline `VITE_*` / `REACT_APP_*` / `NEXT_PUBLIC_*` at **build time** into the public bundle; they are not secret and not changeable at runtime without a rebuild. Type them with `ImportMetaEnv`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every service with more than 2 env vars (basically all of them)
- You deploy to multiple environments (dev/stage/prod) and want deterministic failures

❌ Avoid when:
- A throwaway script — a couple of `process.env` reads are fine
- You use a framework that already validates config (e.g. NestJS `ConfigModule` with a schema) — do not duplicate

---

## 📊 Visual Diagram
```
 .env / Azure App Settings / Key Vault
            │  (strings only)
            ▼
   process.env : { [k]: string | undefined }
            │
            ▼   EnvSchema.safeParse()   ← ONE place, at boot
   ┌── fail ──► print ALL issues ─► process.exit(1) ─► slot never goes live
   └── ok ────► config (typed: number, boolean, enum, frozen)
                    │
                    ▼  import { config } everywhere   (no process.env elsewhere)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `process.env` | Node's env var map | Node का env variables map |
| Fail fast | Crash early on bad config | खराब config पर जल्दी crash |
| Coercion | String → number/boolean | String को number/boolean बनाना |
| `.env` file | Local dev variables file | Local dev के variables की file |
| App Settings | Azure env variable store | Azure का env variable store |
| `ProcessEnv` | Node's typed env interface | Node का typed env interface |
| Feature flag | Boolean config toggling a feature | Feature चालू/बंद करने वाला config |

---

## ⚡ 3-Line Summary
English:
1. `process.env` is `string | undefined`; validate and convert it once at startup with a schema.
2. Export one frozen, typed `config`; never read `process.env` elsewhere; never log secrets.
3. Declaring env types via `declare global` does not validate anything; and `VITE_*` values are public.

Hindi:
1. `process.env` `string | undefined` है; startup पर एक बार schema से validate और convert करो।
2. एक frozen, typed `config` export करो; और कहीं `process.env` नहीं; secrets कभी log नहीं।
3. `declare global` से env types लिखने पर कोई validation नहीं होती; और `VITE_*` values public होती हैं।

---

## ➡️ Next Topic
**88. Typed fetch / axios API Client** — a generic, typed HTTP client for the React side (and server-to-server calls).
