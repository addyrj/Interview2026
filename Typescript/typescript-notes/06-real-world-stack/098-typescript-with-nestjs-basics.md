# 98. TypeScript with NestJS Basics
# हिंदी में: NestJS के साथ TypeScript के Basics

> Verified with **TypeScript 5.9 (5.x)**, `@nestjs/common` 11, compiled with `--experimentalDecorators --emitDecoratorMetadata` (Nest still uses the **legacy/experimental** decorators; TC39 standard decorators are TS 5.0+ and are a different system - see note 67).

---

## 🔵 Simple Definition (English)
NestJS is a TypeScript-first Node framework (Express or Fastify under the hood) built on **classes, decorators and dependency injection**. TypeScript is not optional here: `@Controller`, `@Get`, `@Injectable`, `@Body()` are decorators, and Nest reads **constructor parameter types** (via `emitDecoratorMetadata`) to know which provider to inject. DTOs are classes (not interfaces) because decorators and runtime validation need a real value at runtime.

## 🔵 सरल परिभाषा (Hindi)
NestJS TypeScript-first Node framework है (अंदर Express या Fastify) जो **classes, decorators और dependency injection** पर बना है। यहाँ TypeScript optional नहीं है: `@Controller`, `@Get`, `@Injectable`, `@Body()` decorators हैं, और Nest **constructor parameter types** (`emitDecoratorMetadata` से) पढ़कर तय करता है कि कौन सा provider inject करना है। DTOs classes होते हैं (interfaces नहीं) क्योंकि decorators और runtime validation को runtime पर असली value चाहिए।

---

## 🔴 Problem it Solves
Large Express apps become a pile of files with hand-wired dependencies: `new OrdersService(new Db())` in many places, hard to test, no clear structure. Nest gives a module system, DI container, and conventions (controller -> service -> repository). With TS types, injection is by type, DTO classes define request shapes **and** validation rules in one place, and the compiler checks controller/service contracts.

## 🔴 यह क्यों बना? (Hindi)
बड़े Express apps files का ढेर बन जाते हैं जिनमें dependencies हाथ से जुड़ी होती हैं: कई जगह `new OrdersService(new Db())`, test करना मुश्किल, structure साफ़ नहीं। Nest module system, DI container और conventions (controller -> service -> repository) देता है। TS types के साथ injection type से होती है, DTO classes request shape **और** validation rules एक ही जगह रखती हैं, और compiler controller/service contracts check करता है।

---

## 🟢 How it Works — Step by Step
Step 1 → `tsconfig.json`: `experimentalDecorators: true`, `emitDecoratorMetadata: true`, `strictPropertyInitialization` handled with `!` on DTO fields.
Step 2 → `@Injectable() class OrdersService {}` - marks a provider.
Step 3 → `@Controller("orders") class OrdersController { constructor(private readonly svc: OrdersService) {} }` - Nest reads the constructor's **type** `OrdersService` and injects the instance.
Step 4 → Route params: `@Get(":id") get(@Param("id", ParseIntPipe) id: number)` - the pipe converts string -> number so the TS type matches runtime.
Step 5 → `@Post() create(@Body() dto: CreateOrderDto)` - a **class** DTO + global `ValidationPipe` validates and (with `transform: true`) turns JSON into a real instance.
Step 6 → Register in `@Module({ controllers: [...], providers: [...] })`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `tsconfig.json`: `experimentalDecorators: true`, `emitDecoratorMetadata: true`, और DTO fields पर `!` से `strictPropertyInitialization` संभालो।
Step 2 → `@Injectable() class OrdersService {}` - provider चिह्नित करता है।
Step 3 → `@Controller("orders") class OrdersController { constructor(private readonly svc: OrdersService) {} }` - Nest constructor का **type** `OrdersService` पढ़कर instance inject करता है।
Step 4 → Route params: `@Get(":id") get(@Param("id", ParseIntPipe) id: number)` - pipe string -> number बदलता है ताकि TS type और runtime मेल खाएँ।
Step 5 → `@Post() create(@Body() dto: CreateOrderDto)` - **class** DTO + global `ValidationPipe` validate करता है और (`transform: true` के साथ) JSON को असली instance बनाता है।
Step 6 → `@Module({ controllers: [...], providers: [...] })` में register करो।

---

## 🟡 Real World Example
**Razorpay-style "payments" module**: `PaymentsController` (HTTP) -> `PaymentsService` (business rules) -> `PaymentsRepository` (SQL Server). A unit test replaces `PaymentsRepository` with a fake via DI - no network or DB. `CreatePaymentDto` declares `amount` must be an integer >= 100 (paise), so bad requests never reach the service.

## 🟡 Real Example Hindi mein
**Razorpay जैसा "payments" module**: `PaymentsController` (HTTP) -> `PaymentsService` (business rules) -> `PaymentsRepository` (SQL Server)। Unit test में DI से `PaymentsRepository` की जगह fake लगा देते हैं - न network, न DB। `CreatePaymentDto` बताता है कि `amount` कम से कम 100 (paise) का integer हो, इसलिए खराब requests service तक पहुँचती ही नहीं।

---

## 💻 Code Example — Basic

```typescript
// orders.module.ts — controller + service + DTO (single file for the demo)
import "reflect-metadata"; // Nest imports this for you in a real app
import { Body, Controller, Get, Injectable, Module, NotFoundException, Param, ParseIntPipe, Post } from "@nestjs/common";
import { IsInt, IsString, Min } from "class-validator"; // validation decorators

// DTO = CLASS (not interface): decorators need a runtime value
export class CreateOrderDto {
  @IsString()                // must be a string
  item!: string;             // `!` = "Nest/ValidationPipe will assign it" (strictPropertyInitialization)

  @IsInt() @Min(1)           // integer >= 1
  qty!: number;
}

// The data returned to clients
export interface Order { id: number; item: string; qty: number }

@Injectable()                // makes it injectable
export class OrdersService {
  private readonly orders: Order[] = [];                     // in-memory store for the demo

  create(dto: CreateOrderDto): Order {                       // typed in, typed out
    const order: Order = { id: this.orders.length + 1, item: dto.item, qty: dto.qty };
    this.orders.push(order);
    return order;
  }

  find(id: number): Order {
    const o = this.orders.find((x) => x.id === id);          // Order | undefined
    if (!o) throw new NotFoundException(`Order ${id} not found`); // Nest turns this into HTTP 404
    return o;                                                // narrowed to Order
  }
}

@Controller("orders")        // base route /orders
export class OrdersController {
  constructor(private readonly svc: OrdersService) {}        // injected by TYPE (emitDecoratorMetadata)

  @Post()                    // POST /orders
  create(@Body() dto: CreateOrderDto): Order {               // body is a validated DTO instance
    return this.svc.create(dto);
  }

  @Get(":id")                // GET /orders/:id
  get(@Param("id", ParseIntPipe) id: number): Order {        // pipe converts "5" -> 5
    return this.svc.find(id);
  }
}

@Module({ controllers: [OrdersController], providers: [OrdersService] }) // wire everything
export class OrdersModule {}
```

## 💻 Code Example — Advanced

```typescript
// advanced: interface-based DI token, custom param decorator, mapped-type DTOs, typed config
import "reflect-metadata";
import { Controller, Get, Inject, Injectable, Module, createParamDecorator, type ExecutionContext } from "@nestjs/common";
import { PartialType, OmitType } from "@nestjs/mapped-types"; // may be re-exported from @nestjs/swagger too
import { IsInt, IsOptional, IsString, Min } from "class-validator";

// 1) Interfaces are erased, so inject them with a TOKEN
export interface PaymentGateway { charge(amountPaise: number): Promise<{ txnId: string }> }
export const PAYMENT_GATEWAY = Symbol("PAYMENT_GATEWAY");     // runtime token

@Injectable()
export class RazorpayGateway implements PaymentGateway {      // real implementation
  async charge(amountPaise: number) { return { txnId: `rzp_${amountPaise}` }; }
}
@Injectable()
export class FakeGateway implements PaymentGateway {          // test double
  async charge() { return { txnId: "fake" }; }
}

@Injectable()
export class CheckoutService {
  constructor(@Inject(PAYMENT_GATEWAY) private readonly gw: PaymentGateway) {} // token + interface type
  pay(amountPaise: number) { return this.gw.charge(amountPaise); }              // fully typed call
}

// 2) Custom param decorator: typed access to the authenticated user
interface AuthUser { id: string; role: "admin" | "customer" }
export const CurrentUser = createParamDecorator((_data: unknown, ctx: ExecutionContext): AuthUser => {
  const req = ctx.switchToHttp().getRequest<{ user: AuthUser }>();  // generic gives a typed request
  return req.user;
});

// 3) DTO reuse with mapped types: Create -> Update (all optional) and Create without a field
export class CreateProductDto {
  @IsString() name!: string;
  @IsInt() @Min(0) price!: number;
  @IsString() sku!: string;
}
export class UpdateProductDto extends PartialType(CreateProductDto) {}          // like Partial<>
export class ProductSummaryDto extends OmitType(CreateProductDto, ["sku"] as const) {} // like Omit<>

export class QueryDto {
  @IsOptional() @IsInt() @Min(1) page?: number;                                  // optional query param
}

@Controller("checkout")
export class CheckoutController {
  constructor(private readonly checkout: CheckoutService) {}
  @Get("me")
  me(@CurrentUser() user: AuthUser): string { return `${user.role}:${user.id}`; } // user is AuthUser
}

@Module({
  controllers: [CheckoutController],
  providers: [
    CheckoutService,
    { provide: PAYMENT_GATEWAY, useClass: RazorpayGateway },   // swap with FakeGateway in tests
  ],
})
export class CheckoutModule {}
```

---

## 🟠 Node/Express + React Integration

```typescript
// main.ts — bootstrap on the Express adapter with global validation
import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { Module, ValidationPipe } from "@nestjs/common";
import type { NestExpressApplication } from "@nestjs/platform-express"; // typed Express app

@Module({}) class AppModule {}

export async function bootstrap(): Promise<void> {
  const app = await NestFactory.create<NestExpressApplication>(AppModule); // typed adapter
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,              // strip unknown properties
    forbidNonWhitelisted: true,   // 400 if extra properties sent
    transform: true,              // JSON -> DTO instance, "5" -> 5 with @Type
  }));
  app.enableCors({ origin: "http://localhost:5173" }); // React dev server
  await app.listen(3000);                              // Express (under the hood) starts
}
```

```tsx
// React: share DTO SHAPES (not the decorated classes) with the frontend via an interface package
export interface CreateOrderRequest { item: string; qty: number }   // mirrors CreateOrderDto
export async function createOrder(body: CreateOrderRequest): Promise<{ id: number; item: string; qty: number }> {
  const r = await fetch("http://localhost:3000/orders", {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);        // Nest sends {statusCode, message, error}
  return (await r.json()) as { id: number; item: string; qty: number };
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: DTO property without initializer or `!`
```typescript
// ❌ WRONG
import { IsString } from "class-validator";
class CreateOrderDto {
  @IsString() item: string;
}
// error TS2564: Property 'item' has no initializer and is not definitely assigned in the constructor.
```
✅ Correct: `item!: string;` (or `item = ""`).

❌ Mistake 2: Passing the wrong type to a service method
```typescript
// ❌ WRONG
import { Injectable } from "@nestjs/common";
@Injectable() class OrdersService { find(id: number): { id: number } { return { id }; } }
class C { constructor(private readonly svc: OrdersService) {} get() { return this.svc.find("1"); } }
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```
✅ Correct: use `ParseIntPipe` on the route param so a number arrives at the service.

❌ Mistake 3: Using an `interface` as a DTO or injection type
`@Body() dto: CreateOrderDto` with an **interface** compiles, but interfaces are erased - `ValidationPipe` has nothing to validate against and the decorator metadata becomes `Object`. ✅ Correct: use a class for DTOs; use a `Symbol`/string token + `@Inject()` for interface-based providers.

❌ Mistake 4: Forgetting `import "reflect-metadata"` / `emitDecoratorMetadata`
Nest fails at startup with "Nest can't resolve dependencies of the OrdersController (?)" because the constructor param type metadata is missing. ✅ Correct: enable both flags in `tsconfig.json` (Nest CLI does this).

---

## 🧠 Tricky Interview Question

```typescript
// This compiles. Why does Nest still fail to inject at runtime?
import { Injectable } from "@nestjs/common";
export interface Mailer { send(to: string): void }
@Injectable()
export class NotifyService {
  constructor(private readonly mailer: Mailer) {}   // interface as the injection type
}
```
**Answer:** TypeScript erases interfaces, so `emitDecoratorMetadata` records `Object` for `Mailer`; Nest cannot map `Object` to a provider and throws "Nest can't resolve dependencies of the NotifyService (?)". Provide a token: `constructor(@Inject(MAILER) private readonly mailer: Mailer)` with `{ provide: MAILER, useClass: SmtpMailer }`, or inject an abstract **class** (classes survive erasure and can act as both type and token).

---

## ⚫ Interview Questions + Answers

Q1: Why does NestJS need `emitDecoratorMetadata`?
A1: So the compiler emits `design:paramtypes` metadata (the constructor parameter classes). Nest's DI container reads it to know which provider to inject without manual wiring.

Q2: Experimental decorators vs TC39 standard decorators (TS 5.0+)?
A2: Nest (and TypeORM, class-validator) rely on the legacy `experimentalDecorators` + metadata. TS 5.0+ standard decorators have a different API and no parameter decorators/metadata emit, so they are not drop-in compatible. Keep `experimentalDecorators: true` for Nest.

Q3: DTO class vs interface?
A3: A DTO needs runtime presence for validation (`class-validator`) and transformation (`class-transformer`), so it must be a class. Interfaces are fine for response shapes that need no runtime checks.

Q4: How do you reuse DTOs?
A4: `PartialType`, `PickType`, `OmitType`, `IntersectionType` from `@nestjs/mapped-types` (or `@nestjs/swagger`) - the runtime-aware versions of `Partial`, `Pick`, `Omit` that keep validation decorators.

Q5: Nest vs plain Express with TypeScript?
A5: Express is minimal and flexible: you design structure/DI yourself. Nest enforces modules, DI, pipes/guards/interceptors, and is easier to test and scale in big teams, at the cost of more boilerplate and decorator magic. It can run on Express or Fastify.

---

## 🔷 When to Use + When Not to Use
✅ Use NestJS when:
- Large team / long-lived backend needing structure, DI and testability
- Microservices, GraphQL, WebSockets in one TypeScript framework

❌ Avoid when:
- Tiny API or serverless function where bootstrapping DI is overhead
- Team dislikes decorators / wants functional style (use Fastify/Hono/Express)
- You depend on TC39-only standard decorators (Nest does not use them)

---

## 📊 Visual Diagram
```
HTTP POST /orders {"item":"dosa","qty":2}
        │
 ValidationPipe (CreateOrderDto: @IsString item, @IsInt qty)
        ▼
 OrdersController  ◄── constructor(svc: OrdersService)  injected by TYPE
        ▼
 OrdersService.create(dto): Order
        ▼
 Repository / SQL Server

 tsconfig: experimentalDecorators + emitDecoratorMetadata
 interfaces are erased  ──►  use @Inject(TOKEN)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator | `@x` annotation on class/method/param | class/method/param पर `@x` annotation |
| Provider | Injectable class/value | inject होने वाला class/value |
| DI | Framework supplies dependencies | framework dependencies देता है |
| DTO | Data Transfer Object (request shape) | request का shape |
| Pipe | Transforms/validates input | input को बदलता/validate करता है |
| Token | Key used to look up a provider | provider ढूँढने की key |

---

## ⚡ 3-Line Summary
English:
1. Nest = TS classes + decorators + DI; enable `experimentalDecorators` and `emitDecoratorMetadata`.
2. DTOs are classes (validation needs runtime values); use `ParseIntPipe`/`ValidationPipe` so runtime matches types.
3. Interfaces vanish at runtime - inject them with a token (`@Inject(TOKEN)`) or use abstract classes.

Hindi:
1. Nest = TS classes + decorators + DI; `experimentalDecorators` और `emitDecoratorMetadata` चालू रखो।
2. DTOs classes होते हैं (validation को runtime values चाहिए); `ParseIntPipe`/`ValidationPipe` से runtime को types से मिलाओ।
3. Interfaces runtime पर गायब हो जाते हैं - उन्हें token (`@Inject(TOKEN)`) से inject करो या abstract classes use करो।

---

## ➡️ Next Topic
**99. TypeScript with Jest and Testing Library** — typed tests, mocks and component testing.
