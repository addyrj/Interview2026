# 01. What is NestJS?
# हिंदी में: NestJS क्या है?

---

## 🔵 Simple Definition (English)
**NestJS** is a progressive Node.js framework for building scalable, maintainable server-side applications. It's built with TypeScript, uses decorators (`@Controller`, `@Get`, `@Injectable`) heavily, and is heavily inspired by Angular's architecture. Under the hood it uses Express (or Fastify) as the HTTP layer, but adds: Dependency Injection, modules, opinionated architecture, and TypeScript-first development. Think of it as "Angular for the backend."

Key pillars: **Modules** (organize code), **Controllers** (handle HTTP), **Providers/Services** (business logic + DI).

## 🔵 सरल परिभाषा (Hindi)
**NestJS** एक progressive Node.js framework है scalable, maintainable server-side applications बनाने के लिए। TypeScript-first, decorators (`@Controller`, `@Get`, `@Injectable`) heavy use करता है, Angular architecture से inspire है। Under the hood Express या Fastify है, लेकिन ऊपर से: Dependency Injection, modules, opinionated architecture add करता है। "Backend के लिए Angular" समझो।

Key pillars: **Modules** (code organize), **Controllers** (HTTP handle), **Providers/Services** (business logic + DI)।

---

## 🔴 Problem it Solves
```
PLAIN EXPRESS PROBLEMS (at scale):
  ├── No folder structure enforced
  │     routes/, utils/, middleware/ — everyone organizes differently
  ├── No DI (Dependency Injection)
  │     const userService = new UserService(new UserRepository(db));
  │     Manually creating dependencies = tight coupling
  ├── Testing is hard
  │     Cannot easily mock dependencies
  ├── No TypeScript support out of box
  ├── 10 developers × 10 different patterns = chaos

NESTJS SOLUTION:
  ├── Enforced architecture: Module → Controller → Service
  ├── Built-in DI container: @Injectable() + constructor injection
  ├── TypeScript first — interfaces, generics, decorators
  ├── Testing: TestingModule with easy mocking
  ├── CLI: nest generate controller/service/module
  ├── Built-in support: validation, serialization, guards, pipes
  
RESULT:
  LinkedIn, Roblox, Autodesk use NestJS in production
  New developer joins: sees same structure across all modules
  Tests: mock any service with one line
```

---

## 🟢 How it Works

```
NESTJS APPLICATION STRUCTURE:
──────────────────────────────────────────────────────────────

  src/
  ├── main.ts                  ← bootstrap: NestFactory.create()
  ├── app.module.ts            ← root module (all other modules imported here)
  │
  ├── users/                   ← feature module (all user-related code together)
  │   ├── users.module.ts      ← declares and connects: controller + service
  │   ├── users.controller.ts  ← handles HTTP: @Get(), @Post(), etc.
  │   ├── users.service.ts     ← business logic: @Injectable()
  │   ├── users.repository.ts  ← DB access (optional)
  │   ├── dto/
  │   │   ├── create-user.dto.ts    ← validates request body
  │   │   └── update-user.dto.ts
  │   └── entities/
  │       └── user.entity.ts        ← TypeORM entity / Mongoose schema
  │
  └── orders/
      ├── orders.module.ts
      ├── orders.controller.ts
      └── orders.service.ts

REQUEST FLOW:
  HTTP Request
       │
       ▼
  GUARDS       → Are you allowed? (authentication, authorization)
       │
       ▼
  PIPES        → Is the data valid? (validation, transformation)
       │
       ▼
  CONTROLLER   → Which handler? (@Get('/users/:id'))
       │
       ▼
  SERVICE      → Business logic (DI-injected)
       │
       ▼
  REPOSITORY   → Database access
       │
       ▼
  INTERCEPTORS → Transform response, logging
       │
       ▼
  HTTP Response
```

---

## 🟡 Real World Example
**Flipkart seller API:** 500+ seller-facing endpoints across: products, inventory, orders, payments, analytics, shipping. With raw Express: scattered files, inconsistent patterns, impossible to test, new developers lost. With NestJS: `ProductsModule`, `OrdersModule`, `PaymentsModule` — each self-contained. New developer: run `nest g module shipping` → instant boilerplate. Service injection: `OrdersService` injects `PaymentsService` via constructor — no `new` keyword. Tests: `TestingModule.overrideProvider(PaymentsService).useValue(mockPaymentsService)`.

---

## 💻 Code Example — Basic

```typescript
// ─── main.ts — Application Bootstrap ─────────────────────────────────────────
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global validation pipe: validates all DTOs
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,       // strip unknown fields
    forbidNonWhitelisted: true,  // throw error on unknown fields
    transform: true,       // transform body to DTO class instances
  }));

  // API prefix
  app.setGlobalPrefix('api/v1');

  await app.listen(3000);
  console.log('NestJS app running on http://localhost:3000');
}
bootstrap();

// ─── app.module.ts — Root Module ──────────────────────────────────────────────
import { Module } from '@nestjs/common';
import { UsersModule } from './users/users.module';
import { OrdersModule } from './orders/orders.module';

@Module({
  imports: [UsersModule, OrdersModule],  // all feature modules here
})
export class AppModule {}

// ─── users/users.module.ts ────────────────────────────────────────────────────
import { Module } from '@nestjs/common';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';

@Module({
  controllers: [UsersController],  // handles HTTP for this module
  providers: [UsersService],       // services available in this module
  exports: [UsersService],         // export so other modules can inject it
})
export class UsersModule {}

// ─── users/users.controller.ts ────────────────────────────────────────────────
import { Controller, Get, Post, Put, Delete, Body, Param, HttpCode, HttpStatus } from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

@Controller('users')  // prefix: /users
export class UsersController {
  constructor(private readonly usersService: UsersService) {}
  // NestJS injects UsersService automatically via DI

  @Get()
  findAll() {
    return this.usersService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(id);
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)  // 201 status
  create(@Body() createUserDto: CreateUserDto) {
    // createUserDto is already validated by ValidationPipe
    return this.usersService.create(createUserDto);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateUserDto: UpdateUserDto) {
    return this.usersService.update(id, updateUserDto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)  // 204 status
  remove(@Param('id') id: string) {
    return this.usersService.remove(id);
  }
}

// ─── users/users.service.ts ───────────────────────────────────────────────────
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';

@Injectable()  // marks this class as a DI provider
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,  // TypeORM repo injected
  ) {}

  async findAll(): Promise<User[]> {
    return this.userRepository.find();
  }

  async findOne(id: string): Promise<User> {
    const user = await this.userRepository.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException(`User ${id} not found`);
      // NestJS catches this and returns 404 automatically!
    }
    return user;
  }

  async create(createUserDto: CreateUserDto): Promise<User> {
    const user = this.userRepository.create(createUserDto);
    return this.userRepository.save(user);
  }

  async update(id: string, updateUserDto: UpdateUserDto): Promise<User> {
    const user = await this.findOne(id);  // throws 404 if not found
    Object.assign(user, updateUserDto);
    return this.userRepository.save(user);
  }

  async remove(id: string): Promise<void> {
    const user = await this.findOne(id);
    await this.userRepository.remove(user);
  }
}

// ─── users/dto/create-user.dto.ts ─────────────────────────────────────────────
import { IsEmail, IsString, MinLength, IsOptional } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @MinLength(2)
  name: string;

  @IsEmail()
  email: string;

  @IsString()
  @MinLength(8)
  password: string;

  @IsOptional()
  @IsString()
  phone?: string;
}
```

---

## 🟠 Express.js vs NestJS Comparison

```typescript
// ─── SAME ENDPOINT: GET /users/:id ───────────────────────────────────────────

// EXPRESS:
const express = require('express');
const router = express.Router();

router.get('/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json(user);
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
});

// NESTJS:
@Controller('users')
export class UsersController {
  constructor(private usersService: UsersService) {}

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(id);  // throws NotFoundException if not found
    // NestJS handles: 404 NotFoundException → 404 response
    // NestJS handles: any uncaught error → 500 response
    // Cleaner, no try/catch needed in most cases
  }
}

// ─── KEY DIFFERENCES SUMMARY ─────────────────────────────────────────────────
/*
  FEATURE              EXPRESS              NESTJS
  ──────────────────────────────────────────────────────────────
  Architecture         Roll your own        Enforced (Module/Controller/Service)
  TypeScript           Manual setup         Built-in, TypeScript-first
  Dependency Injection None (manual new())  Built-in DI container
  Validation           Manual / joi         Built-in ValidationPipe + class-validator
  Error handling       Manual try/catch     Exception filters + built-in exceptions
  Testing              Complex              TestingModule with easy mocking
  CLI                  None                 nest g resource/controller/service
  Learning curve       Low                  Higher (Angular patterns)
  Flexibility          High                 Opinionated (less flexibility)
  Performance          Raw Node speed        Slight overhead (abstractions)
  Best for             Small APIs, scripts  Large teams, enterprise APIs
*/
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Circular dependencies between modules
```typescript
// WRONG: A imports B, B imports A → circular!
@Module({ imports: [BModule] })
export class AModule {}

@Module({ imports: [AModule] })  // circular!
export class BModule {}

// CORRECT: Use forwardRef() or extract shared service to a SharedModule
@Module({ imports: [forwardRef(() => BModule)] })
export class AModule {}

@Module({ imports: [forwardRef(() => AModule)] })
export class BModule {}
```

❌ **Mistake 2:** Putting business logic in controllers
```typescript
// WRONG: Controller has business logic
@Controller('orders')
export class OrdersController {
  @Post()
  async createOrder(@Body() dto: CreateOrderDto) {
    const user = await this.db.users.findById(dto.userId);  // DB logic in controller!
    const payment = await this.stripe.charge(dto.amount);   // Payment logic in controller!
    const order = await this.db.orders.create({...});        // More DB in controller!
    await this.emailService.send(user.email, order);         // Email in controller!
    return order;
  }
}

// CORRECT: Controller → Service → Repository
@Controller('orders')
export class OrdersController {
  @Post()
  createOrder(@Body() dto: CreateOrderDto) {
    return this.ordersService.createOrder(dto);  // all logic in service
  }
}
```

❌ **Mistake 3:** Not exporting services needed by other modules
```typescript
// WRONG: UsersService not exported — OrdersModule can't use it
@Module({
  providers: [UsersService],
  // exports: [] ← missing!
})
export class UsersModule {}

// OrdersModule tries to inject UsersService:
// "Nest can't resolve dependencies of OrdersService" error

// CORRECT:
@Module({
  providers: [UsersService],
  exports: [UsersService],  // now other modules can inject UsersService
})
export class UsersModule {}
```

---

## 🧠 Tricky Interview Question

**Q: What is the difference between `@Module` imports and providers? When do you use each?**

**Answer:** `providers` — declares services (injectables) that belong to THIS module and can be injected within this module. `imports` — imports other MODULES whose exported providers become available in this module. `exports` — makes this module's providers available to other modules that import this module.

Example: `TypeOrmModule.forFeature([User])` goes in `imports` (it's a module that provides `UserRepository`). `UsersService` goes in `providers` (it's a service defined in this module). If `OrdersModule` needs `UsersService`, `UsersModule` must `exports: [UsersService]` AND `OrdersModule` must `imports: [UsersModule]`.

---

## ⚫ Interview Questions + Answers

**Q1: What is NestJS and how is it different from Express?**
A1: NestJS is a TypeScript framework built on top of Express (or Fastify) that adds: enforced architecture (Module/Controller/Service), built-in Dependency Injection, decorators-based routing, built-in validation/serialization, and Angular-like patterns. Express is a minimal, unopinionated HTTP framework. NestJS solves Express's biggest weakness at scale: no enforced structure leads to inconsistent code across teams. NestJS adds architectural guardrails, making large codebases maintainable. Trade-off: more opinionated, higher learning curve, slight performance overhead from abstractions.

**Q2: What are the 3 core building blocks of NestJS?**
A2: **Modules** (`@Module`): organizational units that group related functionality. Each module declares its controllers, providers, imports, and exports. `AppModule` is the root. **Controllers** (`@Controller`): handle HTTP requests. Decorated with `@Get`, `@Post`, etc. Thin — only handle routing and calling services. **Providers/Services** (`@Injectable`): contain business logic. Injected via constructor. Can be: services, repositories, factories, helpers. The DI container creates and manages their lifecycle.

**Q3: What is the NestJS request lifecycle? (Which things run in order?)**
A3: Order: (1) **Middleware** — runs first (like Express middleware), before guards. (2) **Guards** — authentication/authorization check (`canActivate()`). (3) **Interceptors** (before) — before handler (logging, transform request). (4) **Pipes** — validate/transform parameters and body. (5) **Controller Handler** — actual route handler method. (6) **Interceptors** (after) — after handler (transform response, logging). (7) **Exception Filters** — catch exceptions thrown anywhere in the chain. Applies to all requests.

**Q4: How do you run NestJS in production?**
A4: (1) Build: `npm run build` → compiles TypeScript to `dist/`. (2) Start: `node dist/main.js` or `npm run start:prod`. (3) Process manager: `pm2 start dist/main.js --name api` for auto-restart, clustering. (4) Docker: multi-stage build — build stage (tsc) + production stage (copy dist, node_modules prod only). (5) Environment: `ConfigModule.forRoot({ envFilePath: '.env' })` for env vars. (6) Helmet + CORS: `app.use(helmet())` in main.ts. (7) Graceful shutdown: `app.enableShutdownHooks()` for SIGTERM handling.

**Q5: How do you test a NestJS service?**
A5: Use `@nestjs/testing`'s `Test.createTestingModule()`. Create a testing module with the service and mock its dependencies. Example:
```typescript
const module = await Test.createTestingModule({
  providers: [
    UsersService,
    { provide: getRepositoryToken(User), useValue: mockRepository },
  ],
}).compile();
const service = module.get<UsersService>(UsersService);
```
This replaces real TypeORM repository with a mock, so tests don't hit the database. `mockRepository` is a plain object with jest spy functions. E2E tests use `supertest` with a real HTTP server.

---

## 📊 Visual Diagram

```
NESTJS MODULE SYSTEM:
──────────────────────────────────────────────────────────────

  AppModule (root)
  ├── imports: [UsersModule, OrdersModule, DatabaseModule]
  │
  ├── UsersModule
  │   ├── imports: [TypeOrmModule.forFeature([User])]
  │   ├── controllers: [UsersController]
  │   ├── providers: [UsersService, UsersRepository]
  │   └── exports: [UsersService]  ← other modules can use this
  │
  ├── OrdersModule
  │   ├── imports: [UsersModule]   ← gets access to UsersService
  │   │            [TypeOrmModule.forFeature([Order])]
  │   ├── controllers: [OrdersController]
  │   └── providers: [OrdersService]
  │         └── OrdersService can inject UsersService ✅
  │
  └── DatabaseModule (global)
      ├── TypeOrmModule.forRoot({...})
      └── exports: [TypeOrmModule]

REQUEST LIFECYCLE:
  HTTP POST /api/v1/users
       │
       ├─ [Middleware] → cors, helmet, morgan
       ├─ [Guards]     → JwtAuthGuard: is token valid?
       ├─ [Pipes]      → ValidationPipe: is body valid?
       ├─ [Controller] → UsersController.create(@Body() dto)
       ├─ [Service]    → UsersService.create(dto)
       ├─ [Repository] → userRepository.save(user)
       └─ [Interceptor]→ TransformResponseInterceptor
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Module | Organizes related code | Related code का container |
| Controller | Handles HTTP routes | HTTP routes handle करता है |
| Provider/Service | Business logic + DI | Business logic + inject होने वाली class |
| @Injectable() | Marks class for DI | DI container के लिए mark |
| DI Container | Manages service instances | Service instances manage करता है |
| Decorator | TypeScript annotation (@Get, etc.) | TypeScript annotation |
| Guards | Auth/authz check | Authentication/authorization check |
| Pipes | Validate/transform data | Data validate+transform करो |
| Interceptors | Before/after handler logic | Handler के before/after logic |

---

## ⚡ 3-Line Summary
**English:**
1. NestJS is a TypeScript-first Node.js framework built on Express, adding enforced architecture (Module → Controller → Service), built-in Dependency Injection, and Angular-inspired patterns for scalable codebases.
2. Core flow: HTTP request → Guards (auth) → Pipes (validate) → Controller (route) → Service (logic) → Repository (DB) → Interceptors (transform) → Response.
3. Advantage over Express: consistent architecture across large teams, easy testing via `TestingModule`, TypeScript-first — but with a steeper learning curve and more boilerplate.

**Hindi:**
1. NestJS = TypeScript-first Node.js framework on top of Express — enforced architecture (Module → Controller → Service), built-in DI, Angular-inspired।
2. Core flow: request → Guards → Pipes → Controller → Service → Repository → Interceptors → Response।
3. Express vs NestJS: large teams + scalability के लिए NestJS; simple APIs के लिए Express काफी है।

---

## ➡️ Next Topic
**02. NestJS Project Structure** — Folder organization, CLI commands, naming conventions।
