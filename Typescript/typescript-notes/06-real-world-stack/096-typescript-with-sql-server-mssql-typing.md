# 96. TypeScript with SQL Server — mssql Typing
# हिंदी में: SQL Server के साथ TypeScript — mssql Typing

> Verified with **TypeScript 5.9 (5.x)**, `mssql` 11 + `@types/mssql`. No live SQL Server was used - the code is **type-checked only**; the SQL itself is not executed.

---

## 🔵 Simple Definition (English)
The `mssql` package (Tedious driver) talks to SQL Server. `@types/mssql` gives types for `ConnectionPool`, `Request`, `Transaction` and results. The key generic is `request.query<T>(sql)` which returns `IResult<T>` with `recordset: T[]` - but **`T` is only a promise from you**: the database never checks it. Real type safety = typed query helpers + a mapping layer (row -> domain object) + parameterized inputs (`.input(name, sql.Int, value)`).

## 🔵 सरल परिभाषा (Hindi)
`mssql` package (Tedious driver) SQL Server से बात करता है। `@types/mssql` `ConnectionPool`, `Request`, `Transaction` और results के types देता है। मुख्य generic है `request.query<T>(sql)` जो `IResult<T>` देता है जिसमें `recordset: T[]` होता है - लेकिन **`T` सिर्फ आपका वादा है**: database उसे check नहीं करता। असली type safety = typed query helpers + mapping layer (row -> domain object) + parameterized inputs (`.input(name, sql.Int, value)`)।

---

## 🔴 Problem it Solves
Untyped `recordset` is `any`-ish: column renames (`Amount` -> `TotalAmount`) break at runtime, `DECIMAL` arrives as `number` (precision loss) and `DATETIME` as `Date`, `NULL` columns arrive as `null`. String-concatenated SQL leads to **SQL injection**. Typed rows + parameters catch typos in field names at compile time, force you to handle `null`, and keep user input out of the SQL text.

## 🔴 यह क्यों बना? (Hindi)
Untyped `recordset` लगभग `any` जैसा है: column rename (`Amount` -> `TotalAmount`) runtime पर टूटता है, `DECIMAL` `number` बनकर आता है (precision loss), `DATETIME` `Date` बनकर, और `NULL` columns `null` बनकर। String जोड़कर बनाई SQL से **SQL injection** होता है। Typed rows + parameters field-name की typos compile time पर पकड़ते हैं, `null` handle करवाते हैं और user input को SQL text से बाहर रखते हैं।

---

## 🟢 How it Works — Step by Step
Step 1 → Create ONE shared pool: `const pool = await new sql.ConnectionPool(config).connect()`.
Step 2 → Describe a **row interface** that mirrors the SQL columns exactly (`OrderId: number`, `Note: string | null`).
Step 3 → Run `pool.request().input("id", sql.Int, id).query<OrderRow>("SELECT ... WHERE OrderId = @id")`.
Step 4 → `result.recordset` is `OrderRow[]` (plus `IRecordSet` helpers like `.columns`); `result.rowsAffected` is `number[]`.
Step 5 → Map rows to a camelCase **domain type** (`toOrder(row)`) so SQL naming does not leak into the app.
Step 6 → For multi-step writes use `sql.Transaction`: begin, run requests via `new sql.Request(tx)`, commit/rollback in `try/catch`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक shared pool बनाओ: `const pool = await new sql.ConnectionPool(config).connect()`।
Step 2 → SQL columns जैसा ही **row interface** बनाओ (`OrderId: number`, `Note: string | null`)।
Step 3 → `pool.request().input("id", sql.Int, id).query<OrderRow>("SELECT ... WHERE OrderId = @id")` चलाओ।
Step 4 → `result.recordset` `OrderRow[]` है; `result.rowsAffected` `number[]` है।
Step 5 → Rows को camelCase **domain type** में map करो (`toOrder(row)`) ताकि SQL की naming app में न फैले।
Step 6 → कई-step writes के लिए `sql.Transaction`: begin, `new sql.Request(tx)` से requests, `try/catch` में commit/rollback।

---

## 🟡 Real World Example
**Paytm wallet ledger** in SQL Server: `Wallets(WalletId INT, Balance DECIMAL(18,2), UpdatedAt DATETIME2, Note NVARCHAR(200) NULL)`. A transfer debits one row and credits another inside a **transaction**; the repository returns `Wallet` domain objects, never raw rows. The type of `Note` is `string | null`, so the compiler forces the UI to handle "no note".

## 🟡 Real Example Hindi mein
**Paytm wallet ledger** SQL Server में: `Wallets(WalletId INT, Balance DECIMAL(18,2), UpdatedAt DATETIME2, Note NVARCHAR(200) NULL)`। Transfer एक row debit और दूसरी credit करता है **transaction** के अंदर; repository raw rows नहीं बल्कि `Wallet` domain objects लौटाती है। `Note` का type `string | null` है, इसलिए compiler UI से "note नहीं है" case handle करवाता है।

---

## 💻 Code Example — Basic

```typescript
// mssql-basic.ts — typed query with parameters (type-check only; needs a real server to run)
import sql from "mssql"; // default export has ConnectionPool, Int, NVarChar, ...

// Row shape = EXACT column names/types as SQL Server returns them
interface WalletRow {
  WalletId: number;          // INT -> number
  Balance: number;           // DECIMAL(18,2) -> number (watch precision for money!)
  UpdatedAt: Date;           // DATETIME2 -> Date
  Note: string | null;       // NVARCHAR NULL -> string | null
}

// Connection config is typed by sql.config
const config: sql.config = {
  server: "localhost",       // host
  database: "paytm_demo",    // database name
  user: "app",               // login
  password: process.env.DB_PASSWORD ?? "", // never hard-code secrets
  options: { encrypt: true, trustServerCertificate: false }, // Azure SQL needs encrypt: true
  pool: { max: 10, min: 0, idleTimeoutMillis: 30000 },       // pool settings
};

// Create ONE pool for the whole app
export const poolPromise: Promise<sql.ConnectionPool> = new sql.ConnectionPool(config).connect();

export async function getWallet(id: number): Promise<WalletRow | undefined> {
  const pool = await poolPromise;                              // reuse the pool
  const result = await pool
    .request()                                                 // new request on the pool
    .input("id", sql.Int, id)                                  // parameter: name, SQL type, JS value
    .query<WalletRow>("SELECT WalletId, Balance, UpdatedAt, Note FROM Wallets WHERE WalletId = @id");
  return result.recordset[0];                                  // WalletRow | undefined (noUncheckedIndexedAccess off)
}
```

## 💻 Code Example — Advanced

```typescript
// mssql-advanced.ts — repository, row->domain mapping, transaction, stored procedure, generic helper
import sql from "mssql";

// ---------- raw row vs domain type ----------
interface WalletRow { WalletId: number; Balance: number; Note: string | null; UpdatedAt: Date }
export interface Wallet { id: number; balance: number; note?: string; updatedAt: string } // app-facing

const toWallet = (r: WalletRow): Wallet => ({             // mapping layer isolates SQL naming
  id: r.WalletId,
  balance: r.Balance,
  note: r.Note ?? undefined,                              // null -> undefined
  updatedAt: r.UpdatedAt.toISOString(),                   // Date -> ISO string (JSON safe)
});

// ---------- generic typed helper ----------
type Params = Record<string, { type: sql.ISqlTypeFactoryWithNoParams; value: unknown }>; // named inputs

export async function query<T>(pool: sql.ConnectionPool, text: string, params: Params = {}): Promise<T[]> {
  const req = pool.request();                              // build request
  for (const [name, p] of Object.entries(params)) req.input(name, p.type, p.value); // add each input
  const res = await req.query<T>(text);                    // T is the caller's promise
  return res.recordset;                                    // T[]
}

// ---------- transaction: atomic transfer ----------
export async function transfer(pool: sql.ConnectionPool, from: number, to: number, amount: number): Promise<void> {
  const tx = new sql.Transaction(pool);                    // create transaction on the pool
  await tx.begin();                                        // BEGIN TRAN
  try {
    const debit = await new sql.Request(tx)                // request bound to the transaction
      .input("id", sql.Int, from)
      .input("amt", sql.Decimal(18, 2), amount)            // typed decimal
      .query("UPDATE Wallets SET Balance = Balance - @amt WHERE WalletId = @id AND Balance >= @amt");
    if (debit.rowsAffected[0] !== 1) throw new Error("insufficient funds"); // rowsAffected: number[]
    await new sql.Request(tx)
      .input("id", sql.Int, to)
      .input("amt", sql.Decimal(18, 2), amount)
      .query("UPDATE Wallets SET Balance = Balance + @amt WHERE WalletId = @id");
    await tx.commit();                                     // COMMIT
  } catch (e) {
    await tx.rollback();                                   // ROLLBACK on any error
    throw e instanceof Error ? e : new Error(String(e));   // rethrow typed
  }
}

// ---------- stored procedure with output parameter ----------
interface PlaceOrderOut { NewOrderId: number }
export async function placeOrder(pool: sql.ConnectionPool, userId: number): Promise<number> {
  const res = await pool.request()
    .input("UserId", sql.Int, userId)                      // input param
    .output("NewOrderId", sql.Int)                         // output param
    .execute<unknown>("usp_PlaceOrder");                   // stored proc name
  const out = res.output as PlaceOrderOut;                 // output is a loose record: assert once, here
  return out.NewOrderId;
}

export async function listWallets(pool: sql.ConnectionPool): Promise<Wallet[]> {
  const rows = await query<WalletRow>(pool, "SELECT WalletId, Balance, Note, UpdatedAt FROM Wallets");
  return rows.map(toWallet);                               // map to domain
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express route using the repository; response type is the DOMAIN type, not the raw row.
import express from "express";
import sql from "mssql";

interface WalletRow { WalletId: number; Balance: number; Note: string | null }
interface WalletDTO { id: number; balance: number; note: string | null }   // sent to React

declare const pool: sql.ConnectionPool;                    // created at startup

const app = express();
app.get("/api/wallets/:id", async (req, res) => {
  const id = Number(req.params.id);                        // params are strings
  if (!Number.isInteger(id)) { res.status(400).json({ error: "bad id" }); return; } // validate before SQL
  const r = await pool.request().input("id", sql.Int, id)
    .query<WalletRow>("SELECT WalletId, Balance, Note FROM Wallets WHERE WalletId = @id");
  const row = r.recordset[0];                              // WalletRow | undefined at runtime
  if (!row) { res.status(404).json({ error: "not found" }); return; }       // narrow undefined
  const dto: WalletDTO = { id: row.WalletId, balance: row.Balance, note: row.Note };
  res.json(dto);                                           // React gets WalletDTO
});
```

```tsx
// React consumer uses the same DTO; note can be null so UI handles it
interface WalletDTO { id: number; balance: number; note: string | null }
export const WalletCard = ({ w }: { w: WalletDTO }) => (
  <div>₹{w.balance} {w.note ?? "No note"}</div>             // null handled
);
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong assumption about a column type
```typescript
// ❌ WRONG
import sql from "mssql";
interface Row { id: number }
async function f(p: sql.ConnectionPool) {
  const r = await p.request().input("id", sql.Int, 1).query<Row>("select 1");
  const x: string = r.recordset[0].id;
  // error TS2322: Type 'number' is not assignable to type 'string'.
}
```

❌ Mistake 2: Reading a column that is not in the row type
```typescript
// ❌ WRONG
import sql from "mssql";
interface Row { id: number }
async function f(p: sql.ConnectionPool) {
  const r = await p.request().query<Row>("select 1");
  r.recordset[0].name;
  // error TS2339: Property 'name' does not exist on type 'Row'.
}
```

❌ Mistake 3: Building SQL with string concatenation
```typescript
// ❌ WRONG (compiles! and is a SECURITY HOLE)
import sql from "mssql";
async function f(p: sql.ConnectionPool, name: string) {
  return p.request().query(`SELECT * FROM Users WHERE Name = '${name}'`); // injection: name = "' OR 1=1 --"
}
```
✅ Correct: `p.request().input("name", sql.NVarChar(100), name).query("SELECT * FROM Users WHERE Name = @name")`. TypeScript cannot detect this one - it is a lint/review rule.

❌ Mistake 4: Trusting the `<T>` generic as a guarantee
`query<WalletRow>` does **not** validate. If a DBA renames a column, TS still says `WalletRow`. ✅ Correct: add an integration test per query, or validate rows with zod at the repository boundary.

---

## 🧠 Tricky Interview Question

```typescript
// Why can `result.recordset[0].Balance` crash even though the code type-checks?
import sql from "mssql";
interface Row { Balance: number }
export async function bal(p: sql.ConnectionPool): Promise<number> {
  const r = await p.request().query<Row>("SELECT Balance FROM Wallets WHERE WalletId = -1");
  return r.recordset[0].Balance;
}
```
**Answer:** Two reasons. (1) `recordset[0]` is typed `Row` (not `Row | undefined`) unless `noUncheckedIndexedAccess` is enabled; with no matching row it is `undefined` at runtime, so `.Balance` throws `TypeError`. (2) The `<Row>` generic is unverified: if `Balance` is `NULL` or `DECIMAL` returned differently the value can be `null`. Fixes: enable `noUncheckedIndexedAccess`, check `if (!row)`, mark nullable columns `number | null`, and for money prefer integer paise or `DECIMAL` -> string to avoid float rounding.

---

## ⚫ Interview Questions + Answers

Q1: How does `mssql` map SQL types to JS types?
A1: `INT` -> number, `BIGINT` -> string by default (too large for number), `DECIMAL/MONEY` -> number (precision risk), `DATETIME/DATETIME2` -> Date, `NVARCHAR` -> string, `BIT` -> boolean, `NULL` -> null, `UNIQUEIDENTIFIER` -> string.

Q2: Why parameterize with `.input()`?
A2: It sends values separately from the SQL text (via `sp_executesql`), preventing SQL injection and enabling plan reuse. The explicit `sql.Int`/`sql.NVarChar(n)` also avoids implicit conversions that kill index usage.

Q3: One pool or a new connection per request?
A3: One pool per process, created at startup and shared; a connection per request exhausts SQL Server connections. Close the pool on shutdown.

Q4: How do you make `query<T>` actually safe?
A4: Treat `T` as a contract, not a proof: keep rows in a repository layer, map to domain types, validate with zod (or tests), and enable `noUncheckedIndexedAccess`.

Q5: ORM vs raw `mssql` with TypeScript?
A5: ORMs (Prisma, TypeORM, Kysely, Drizzle) generate/derive types from the schema, so column drift is caught at compile time. Raw `mssql` gives maximum control and performance but you maintain the types yourself. Kysely/Prisma are good middle grounds for SQL Server.

---

## 🔷 When to Use + When Not to Use
✅ Use raw `mssql` + TS when:
- You need stored procedures, bulk copy, TVPs, or hand-tuned SQL
- Team already owns the schema and wants thin repositories

❌ Avoid when:
- The schema changes weekly and nobody updates row interfaces (use a schema-derived query builder/ORM)
- You are tempted to concatenate user input into SQL
- You treat `query<T>` as validation

---

## 📊 Visual Diagram
```
 Express handler
     │ validated input (number)
     ▼
 repository.getWallet(id)
     │ pool.request().input("id", sql.Int, id)
     ▼
 SQL Server  ──rows──►  IResult<WalletRow>.recordset : WalletRow[]
     │
 toWallet(row)  (mapping: Balance -> balance, null -> undefined)
     ▼
 Wallet (domain)  ──► res.json(dto) ──► React
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ConnectionPool | Shared set of DB connections | DB connections का साझा pool |
| recordset | Rows returned by a query | query से मिली rows |
| Parameterized query | Values sent separately from SQL | SQL से अलग भेजी गई values |
| Row vs Domain type | DB shape vs app shape | DB का shape बनाम app का shape |
| Transaction | All-or-nothing group of statements | सब-या-कुछ-नहीं statements का group |
| Output parameter | Value returned by a stored proc | stored proc से लौटी value |

---

## ⚡ 3-Line Summary
English:
1. `query<Row>()` types `recordset: Row[]` but is only your promise - map rows to domain types and validate/test.
2. Always use `.input(name, sql.Type, value)`; never concatenate user input; share ONE pool.
3. Model `NULL` as `T | null`, use transactions for multi-step writes, enable `noUncheckedIndexedAccess`.

Hindi:
1. `query<Row>()` `recordset: Row[]` type करता है पर वह सिर्फ आपका वादा है - rows को domain types में map करो और validate/test करो।
2. हमेशा `.input(name, sql.Type, value)` use करो; user input कभी जोड़ो मत; एक ही pool share करो।
3. `NULL` को `T | null` लिखो, multi-step writes के लिए transactions लो, `noUncheckedIndexedAccess` चालू रखो।

---

## ➡️ Next Topic
**97. TypeScript with Mongoose / MongoDB** — schema typing, hydrated documents and lean queries.
