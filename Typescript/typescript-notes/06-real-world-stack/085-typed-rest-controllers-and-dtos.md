# 85. Typed REST Controllers + DTOs
# हिंदी में: Typed REST Controllers + DTOs

> Verified with **TypeScript 5.9.x**. `satisfies` (4.9+) is used for the mapper table; everything else is plain TS.

---

## 🔵 Simple Definition (English)
A **DTO (Data Transfer Object)** is a type describing the exact shape of data crossing a boundary: what a client **sends** (`CreateOrderDto`) and what the API **returns** (`OrderResponseDto`). A **controller** is a thin layer that takes the HTTP request, calls a **service** with typed input, and maps the result to a response DTO. Database/entity types (`OrderRow`) stay private behind the service.

## 🔵 सरल परिभाषा (Hindi)
**DTO (Data Transfer Object)** एक type है जो boundary पार करने वाले data की सटीक shape बताता है: client जो **भेजता** है (`CreateOrderDto`) और API जो **लौटाती** है (`OrderResponseDto`)। **Controller** पतली layer है जो HTTP request लेकर typed input के साथ **service** को call करती है और result को response DTO में map करती है। Database/entity types (`OrderRow`) service के पीछे private रहते हैं।

---

## 🔴 Problem it Solves
When handlers return DB rows directly, you leak columns (`password_hash`, `internal_notes`), couple the API to table names, and a column rename breaks the React app. When controllers contain SQL, business rules and HTTP code together they become untestable. DTOs + layers give: a stable public contract, no accidental data leaks, and services testable without Express.

## 🔴 यह क्यों बना? (Hindi)
जब handlers DB rows सीधे लौटाते हैं तो columns (`password_hash`, `internal_notes`) leak होते हैं, API table names से बंध जाती है और column rename से React app टूट जाता है। जब controllers में SQL, business rules और HTTP code एक साथ हों तो वे test नहीं हो पाते। DTOs + layers स्थिर public contract, accidental leaks से बचाव और Express के बिना testable services देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Request DTOs**: `CreateOrderDto`, `UpdateOrderDto = Partial<Pick<...>>`, `ListOrdersQuery`.
Step 2 → **Entity/Row types**: what the database returns (`OrderRow` with snake_case, `created_at: Date`).
Step 3 → **Response DTOs**: what clients get (`OrderResponseDto` with camelCase, ISO strings, no internals).
Step 4 → **Mapper**: `toOrderDto(row): OrderResponseDto` — the single place where entity becomes DTO.
Step 5 → **Service** takes DTOs/primitive inputs, returns entities or DTOs; no `req`/`res` inside.
Step 6 → **Controller** = parse/validate → call service → map → `res.status().json()`. Validate at runtime with zod (topic 86); DTO types are erased at runtime.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Request DTOs**: `CreateOrderDto`, `UpdateOrderDto = Partial<Pick<...>>`, `ListOrdersQuery`।
Step 2 → **Entity/Row types**: database जो लौटाता है (`OrderRow`, snake_case, `created_at: Date`)।
Step 3 → **Response DTOs**: clients को जो मिलता है (`OrderResponseDto`, camelCase, ISO strings, कोई internals नहीं)।
Step 4 → **Mapper**: `toOrderDto(row): OrderResponseDto` — वो एक जगह जहाँ entity DTO बनती है।
Step 5 → **Service** DTOs/primitives लेती है, entities या DTOs लौटाती है; अंदर `req`/`res` नहीं।
Step 6 → **Controller** = parse/validate → service call → map → `res.status().json()`। Runtime validation zod से (topic 86); DTO types runtime पर erase हो जाते हैं।

---

## 🟡 Real World Example
A **Swiggy orders API**: DB table `orders(id, user_id, total_paise, created_at, internal_notes)`. The public `OrderResponseDto` exposes `{ id, userId, totalRupees, createdAt }` and hides `internal_notes`. When the DB team renames `total_paise` to `amount_paise`, only the mapper changes — React is untouched.

## 🟡 Real Example Hindi mein
**Swiggy orders API**: DB table `orders(id, user_id, total_paise, created_at, internal_notes)`। Public `OrderResponseDto` में `{ id, userId, totalRupees, createdAt }` है और `internal_notes` छिपा है। DB team `total_paise` को `amount_paise` कर दे तो सिर्फ mapper बदलता है — React अछूता रहता है।

---

## 💻 Code Example — Basic

```typescript
// order.dto.ts — contracts at the boundary
export interface CreateOrderDto {           // what the client SENDS
  userId: string;                           // who orders
  items: { sku: string; qty: number }[];    // what they order
  couponCode?: string;                      // optional coupon
}

// Update = any subset of fields except userId (ownership cannot change)
export type UpdateOrderDto = Partial<Omit<CreateOrderDto, "userId">>;

export interface OrderResponseDto {         // what the client GETS
  id: string;
  userId: string;
  totalRupees: number;                      // derived: paise / 100
  status: "pending" | "paid" | "cancelled"; // closed set
  createdAt: string;                        // ISO string, JSON-safe (Date is NOT JSON-typed)
}

// order.entity.ts — database row (INTERNAL, never exported to controllers' responses)
export interface OrderRow {
  id: string;
  user_id: string;
  total_paise: number;
  status: "pending" | "paid" | "cancelled";
  created_at: Date;
  internal_notes: string | null;            // must never leak
}

// Mapper: the ONLY place entity -> DTO happens
export function toOrderDto(row: OrderRow): OrderResponseDto {
  return {
    id: row.id,                              // copy
    userId: row.user_id,                     // rename snake_case -> camelCase
    totalRupees: row.total_paise / 100,      // unit conversion
    status: row.status,                      // same union
    createdAt: row.created_at.toISOString(), // Date -> string
  };                                         // internal_notes is deliberately omitted
}

const row: OrderRow = { id: "o1", user_id: "u1", total_paise: 45000, status: "paid", created_at: new Date(0), internal_notes: "VIP" };
console.log(toOrderDto(row)); // { id:'o1', userId:'u1', totalRupees:450, status:'paid', createdAt:'1970-01-01T00:00:00.000Z' }
```

```typescript
// ❌ DTO mismatch caught at compile time
interface CreateOrderDto { userId: string; total: number }
function create(dto: CreateOrderDto) { return dto; }
create({ userId: "u1", total: "499" });
// error TS2322: Type 'string' is not assignable to type 'number'.
```

## 💻 Code Example — Advanced

```typescript
// layered.ts — service + controller, framework-free service, thin controller
import express, { type Request, type Response, type Router } from "express";

interface CreateOrderDto { userId: string; items: { sku: string; qty: number }[] }
interface OrderResponseDto { id: string; userId: string; totalRupees: number; status: "pending" | "paid" }
interface OrderRow { id: string; user_id: string; total_paise: number; status: "pending" | "paid"; internal_notes: string | null }

// ---- Repository (data access): would be SQL Server in real life (topic 96)
interface OrderRepo {
  insert(userId: string, totalPaise: number): Promise<OrderRow>;
  findById(id: string): Promise<OrderRow | undefined>;
}

// ---- Service: business logic only, no Express types. Constructor injection => easy to mock.
class OrderService {
  constructor(private readonly repo: OrderRepo) {}                    // dependency via interface

  async create(dto: CreateOrderDto): Promise<OrderRow> {
    const paise = dto.items.reduce((s, i) => s + i.qty * 10000, 0);   // dummy pricing: Rs100 each
    return this.repo.insert(dto.userId, paise);                       // persist
  }
  get(id: string): Promise<OrderRow | undefined> { return this.repo.findById(id); }
}

// Mapper table: `satisfies` (TS 4.9) checks shape without widening
const toDto = (r: OrderRow): OrderResponseDto => ({
  id: r.id, userId: r.user_id, totalRupees: r.total_paise / 100, status: r.status,
}) satisfies OrderResponseDto;

// ---- Controller: thin. Parse -> service -> map -> respond.
class OrderController {
  constructor(private readonly service: OrderService) {}

  // Arrow properties keep `this` when passed to router.post(...)
  create = async (req: Request<{}, OrderResponseDto, CreateOrderDto>, res: Response<OrderResponseDto>): Promise<void> => {
    const row = await this.service.create(req.body);   // typed DTO in
    res.status(201).json(toDto(row));                  // typed DTO out (internal_notes cannot leak)
  };

  getOne = async (req: Request<{ id: string }>, res: Response<OrderResponseDto | { error: string }>): Promise<void> => {
    const row = await this.service.get(req.params.id);
    if (!row) { res.status(404).json({ error: "Order not found" }); return; }
    res.json(toDto(row));
  };
}

// ---- Composition root: wires concrete pieces
export function ordersRouter(repo: OrderRepo): Router {
  const controller = new OrderController(new OrderService(repo)); // build chain
  const router = express.Router();
  router.post("/", controller.create);   // POST /orders
  router.get("/:id", controller.getOne); // GET  /orders/:id
  return router;
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// web/src/orders/ordersApi.ts — React side consumes the SAME response DTO
import type { OrderResponseDto } from "../../shared/order.dto"; // type-only; no server code bundled

export async function fetchOrder(id: string): Promise<OrderResponseDto> {
  const res = await fetch(`/api/orders/${id}`);          // call API
  if (!res.ok) throw new Error(`Failed: ${res.status}`);  // basic error
  return (await res.json()) as OrderResponseDto;         // cast; zod parse is safer (topic 86)
}
```

```typescript
// web/src/orders/OrderCard.tsx — component props reuse the DTO via Pick (no duplicate types)
import type { OrderResponseDto } from "../../shared/order.dto";

type OrderCardProps = Pick<OrderResponseDto, "id" | "totalRupees" | "status">; // only what the UI needs

export function OrderCard({ id, totalRupees, status }: OrderCardProps) {
  return <li>#{id} — Rs {totalRupees} ({status})</li>; // renders typed fields
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning the entity/DB row from the controller.
```typescript
// ❌ leaks internal_notes (type is OrderRow, JSON.stringify sends everything)
// res.json(row);
// ✅ res.json(toOrderDto(row));  // response typed Response<OrderResponseDto> makes the leak a compile error
```

❌ Mistake 2: `Date` in a response DTO. After `JSON.stringify` it is a **string**, so the client's `Date` type is a lie. ✅ Use `string` (ISO) in DTOs and convert in the mapper.

❌ Mistake 3: One giant `Order` type used for DB, request, response, and UI. ✅ Separate types; derive with `Pick/Omit/Partial` so they stay in sync.

❌ Mistake 4: Trusting `req.body: CreateOrderDto` as validated. ✅ Parse with zod first (topic 86), then pass the parsed value.

❌ Mistake 5: Passing `controller.create` as a method (`router.post("/", controller.create)`) when it is a normal method — `this` is lost. ✅ Arrow-function class properties or `.bind(controller)`.

---

## 🧠 Tricky Interview Question
**Q:** "`interface Dto { createdAt: Date }` — the API returns it via `res.json(dto)` and the React app declares the same `Dto`. What is wrong?"

**A:** JSON has no Date type. `JSON.stringify` converts the Date to an ISO **string**, and `res.json()` on the client yields a string — but the shared `Dto` claims `Date`, so `dto.createdAt.getTime()` compiles and crashes at runtime. Fix: DTO field is `string`, or use a mapped helper `type Serialized<T> = { [K in keyof T]: T[K] extends Date ? string : T[K] }` for server → wire types, and revive dates explicitly on the client (or let zod `z.coerce.date()` do it).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a DTO and an entity?
A1: An entity mirrors persistence (table/row/ORM model, possibly with internals). A DTO is a purpose-built shape for a boundary (request or response). Mapping between them decouples API from storage.

Q2: Why are DTO `interface`s not enough for validation?
A2: Types are erased at compile time. The client can send anything, so you need runtime schemas (zod, class-validator) that also generate the TS type.

Q3: How do you derive Update/Patch DTOs without duplication?
A3: Utility types: `Partial<Omit<CreateDto, "id">>` or `Partial<Pick<...>>`. When Create changes, Update follows automatically.

Q4: Where do you put business logic: controller or service?
A4: Service. Controllers only translate HTTP ↔ domain. This makes services unit-testable without Express and reusable by queues/CRON jobs.

Q5: Class DTOs vs interface DTOs?
A5: Interfaces/types are zero-cost and fine with zod. Classes (NestJS + class-validator) carry decorators/metadata for runtime validation but add runtime weight (topic 98).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public APIs consumed by React/mobile; multiple consumers of one service
- Entities contain sensitive/internal columns

❌ Avoid / simplify when:
- Tiny internal CRUD tool — mappers are overhead; returning a `Pick<Row,...>` may be enough
- You do not validate at runtime — DTO types alone give false safety

---

## 📊 Visual Diagram
```
 React ──CreateOrderDto──► Controller ──► Service ──► Repo ──► SQL Server
                              │              │          │
                              │ validate     │ business │ OrderRow (snake_case, internals)
                              ▼              ▼          ▼
 React ◄─OrderResponseDto── toOrderDto(row)  ◄──────────┘
        (camelCase, ISO string, no internal_notes)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DTO | Data shape at a boundary | Boundary पर data की shape |
| Entity / Row | Persistence-shaped type | Database-shaped type |
| Mapper | Entity ↔ DTO converter | Entity ↔ DTO converter |
| Controller | HTTP-facing thin layer | HTTP से जुड़ी पतली layer |
| Service | Business logic layer | Business logic layer |
| Repository | Data-access abstraction | Data-access abstraction |
| Serialization | Object → JSON text | Object को JSON text बनाना |

---

## ⚡ 3-Line Summary
English:
1. Use request/response DTOs at the boundary and keep DB row types private behind a mapper.
2. Controller = thin (validate → service → map); service = business logic with no Express types.
3. DTO types are erased — pair them with zod; remember `Date` becomes a string over JSON.

Hindi:
1. Boundary पर request/response DTOs रखो और DB row types mapper के पीछे private रखो।
2. Controller = पतला (validate → service → map); service = बिना Express types की business logic।
3. DTO types erase हो जाते हैं — zod के साथ इस्तेमाल करो; JSON में `Date` string बन जाती है।

---

## ➡️ Next Topic
**86. Runtime Validation with Zod + z.infer** — one schema gives both runtime validation and the TypeScript type.
