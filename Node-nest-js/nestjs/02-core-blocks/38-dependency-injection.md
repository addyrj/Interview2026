# 38. Dependency Injection (DI)
# हिंदी में: Dependency Injection — NestJS का Core Pattern

---

## 🔵 Simple Definition (English)
**Dependency Injection** is a design pattern where a class receives its dependencies from an external container rather than creating them itself. In NestJS: mark a class with `@Injectable()` → register it as a `provider` in a module → inject it via constructor. NestJS's DI container creates the instance (singleton by default) and injects it wherever needed. Result: classes are loosely coupled, testable, and reusable.

Without DI: `const service = new OrdersService(new UserRepository(db), new EmailService(smtpConfig))` — manually wiring dependencies.
With DI: just declare what you need in the constructor — NestJS wires it automatically.

## 🔵 सरल परिभाषा (Hindi)
**Dependency Injection** एक design pattern है जहाँ class अपनी dependencies खुद नहीं बनाती — external container से receive करती है। NestJS में: `@Injectable()` mark करो → module में `providers` में register करो → constructor में inject करो। NestJS का DI container instance बनाता है (default singleton) और जहाँ चाहिए inject करता है। Result: loose coupling, testable, reusable classes।

---

## 🔴 Problem it Solves
```
WITHOUT DI (tight coupling nightmare):
  class OrdersService {
    constructor() {
      this.userRepo = new UserRepository(new DatabaseConnection(config));
      this.emailService = new EmailService(new SmtpClient(smtpConfig));
      this.paymentService = new PaymentService(new RazorpayClient(apiKey));
    }
  }
  
  Problems:
  1. OrdersService knows HOW to create UserRepository (wrong!)
  2. Testing: can't mock dependencies easily
     → tests hit real database, real email, real payments
  3. Change DatabaseConnection config? Update everywhere manually
  4. Circular deps: A creates B creates C creates A = stack overflow

WITH DI (NestJS way):
  @Injectable()
  class OrdersService {
    constructor(
      private userRepo: UserRepository,    // injected automatically
      private emailService: EmailService,  // injected automatically
      private paymentService: PaymentService,  // injected automatically
    ) {}
  }
  
  Benefits:
  1. OrdersService doesn't know HOW to create deps — just declares WHAT it needs
  2. Testing: provide mock in TestingModule → no real DB/email/payment
  3. Change implementation? Swap provider in module — OrdersService unaware
  4. DI container handles circular deps + lifecycle management
```

---

## 🟢 How DI Works in NestJS

```
DI CONTAINER LIFECYCLE:
──────────────────────────────────────────────────────────

  Step 1: Register providers in module
    @Module({
      providers: [OrdersService, UserRepository, EmailService]
    })
    
  Step 2: NestJS reads constructor parameters
    constructor(private userRepo: UserRepository) {}
    → Reads TypeScript metadata: "needs UserRepository"
    
  Step 3: DI container checks registry
    "UserRepository registered? YES → create/reuse instance"
    
  Step 4: Inject
    → Creates OrdersService with userRepo instance injected

  SINGLETON SCOPE (default):
    One instance per module
    UserRepository created once → same instance everywhere
    
  REQUEST SCOPE:
    New instance per HTTP request
    Good for: request-specific context (current user, request ID)
    
  TRANSIENT SCOPE:
    New instance every injection
    Good for: stateful helper classes
```

---

## 🟡 Real World Example
**Amazon India order system:** `OrdersService` needs: `UserService` (get buyer info), `InventoryService` (check stock), `PaymentService` (charge), `NotificationService` (send SMS/email), `LogisticsService` (assign delivery). Without DI: OrdersService manually creates all 5 — any change in how PaymentService is created breaks OrdersService. With NestJS DI: OrdersService constructor declares all 5, container injects them. In tests: `overrideProvider(PaymentService).useValue({ charge: jest.fn().mockResolvedValue({ success: true }) })` — test payment flow without Razorpay API.

---

## 💻 Code Example — Basic

```typescript
// ─── BASIC DI FLOW ────────────────────────────────────────────────────────────

// 1. Make a service injectable
import { Injectable, NotFoundException } from '@nestjs/common';

@Injectable()                            // ← marks this as a DI provider
export class UserRepository {
  private users = [
    { id: '1', email: 'rahul@example.com', name: 'Rahul' },
    { id: '2', email: 'priya@example.com', name: 'Priya' },
  ];

  findById(id: string) {
    return this.users.find(u => u.id === id) || null;
  }

  findAll() {
    return this.users;
  }
}

// 2. Inject it into another service
@Injectable()
export class EmailService {
  sendWelcomeEmail(email: string, name: string) {
    console.log(`Sending welcome email to ${email}, Hi ${name}!`);
    // In reality: nodemailer, SendGrid, AWS SES
  }
}

// 3. OrdersService depends on both
@Injectable()
export class OrdersService {
  constructor(
    private readonly userRepository: UserRepository,  // ← injected by NestJS
    private readonly emailService: EmailService,      // ← injected by NestJS
  ) {
    // No "new UserRepository()" — DI container provides it
  }

  async placeOrder(userId: string, items: string[]) {
    // Use injected dependencies
    const user = this.userRepository.findById(userId);
    if (!user) {
      throw new NotFoundException(`User ${userId} not found`);
    }

    // Business logic
    const order = {
      id: Date.now().toString(),
      userId,
      items,
      status: 'pending',
      createdAt: new Date(),
    };

    // Use email service (also injected)
    this.emailService.sendWelcomeEmail(user.email, user.name);

    return order;
  }
}

// 4. Register all in module
import { Module } from '@nestjs/common';

@Module({
  providers: [
    OrdersService,    // ← DI will inject UserRepository + EmailService into this
    UserRepository,   // ← registered, available for injection
    EmailService,     // ← registered, available for injection
  ],
})
export class OrdersModule {}
```

## 💻 Code Example — Advanced

```typescript
// advanced-di.ts — Custom providers, interfaces, scopes

import {
  Injectable, Module, Scope,
  Inject, Optional,
} from '@nestjs/common';
import { REQUEST } from '@nestjs/core';
import { Request } from 'express';

// ─── 1. INTERFACE + INJECTION TOKEN ──────────────────────────────────────────
// Problem: injecting by class type couples you to the implementation
// Solution: inject by interface using a token

// Define an interface (TypeScript only — no runtime presence)
interface IEmailService {
  sendEmail(to: string, subject: string, body: string): Promise<void>;
}

// Token (symbol) used as injection key
const EMAIL_SERVICE = Symbol('IEmailService');

// Two implementations:
@Injectable()
class SendGridEmailService implements IEmailService {
  async sendEmail(to: string, subject: string, body: string) {
    console.log(`SendGrid: ${subject} → ${to}`);
    // real SendGrid call
  }
}

@Injectable()
class MockEmailService implements IEmailService {
  async sendEmail(to: string, subject: string, body: string) {
    console.log(`[MOCK] Email: ${subject} → ${to}`);
    // no real email sent
  }
}

// Register with token in module
@Module({
  providers: [
    {
      provide: EMAIL_SERVICE,                        // injection token
      useClass: process.env.NODE_ENV === 'test'
        ? MockEmailService                           // mock in test
        : SendGridEmailService,                      // real in prod
    },
  ],
  exports: [EMAIL_SERVICE],
})
export class EmailModule {}

// Inject using @Inject(token)
@Injectable()
class UserRegistrationService {
  constructor(
    @Inject(EMAIL_SERVICE) private emailService: IEmailService,  // by token
  ) {}

  async register(email: string) {
    await this.emailService.sendEmail(email, 'Welcome!', 'Thanks for joining.');
  }
}

// ─── 2. PROVIDER SCOPES ──────────────────────────────────────────────────────

// DEFAULT (Singleton): one instance per module, shared everywhere
@Injectable()
export class AppConfigService {
  readonly dbUrl = process.env.DATABASE_URL;
  // Same instance everywhere — good: no extra overhead
}

// REQUEST SCOPE: new instance per HTTP request
@Injectable({ scope: Scope.REQUEST })
export class RequestContextService {
  private requestId: string;
  private startTime: number;

  constructor(@Inject(REQUEST) private request: Request) {
    // Injected Express request object
    this.requestId = request.headers['x-request-id'] as string || Date.now().toString();
    this.startTime = Date.now();
  }

  getRequestId() { return this.requestId; }
  getElapsed() { return Date.now() - this.startTime; }
}

// TRANSIENT: new instance every injection (rare)
@Injectable({ scope: Scope.TRANSIENT })
export class LoggerService {
  private context: string = 'Default';
  
  setContext(context: string) { this.context = context; }
  log(message: string) { console.log(`[${this.context}] ${message}`); }
}

// ─── 3. FACTORY PROVIDERS ────────────────────────────────────────────────────
// Dynamic provider based on config

const DATABASE_CONNECTION = 'DATABASE_CONNECTION';

@Module({
  providers: [
    {
      provide: DATABASE_CONNECTION,
      useFactory: async () => {
        // Async factory: connect to DB before providing
        const { DataSource } = await import('typeorm');
        const ds = new DataSource({
          type: 'postgres',
          url: process.env.DATABASE_URL,
          // ...
        });
        await ds.initialize();
        return ds;
      },
    },
  ],
  exports: [DATABASE_CONNECTION],
})
export class DatabaseModule {}

// ─── 4. OPTIONAL INJECTION ───────────────────────────────────────────────────
@Injectable()
class AnalyticsService {
  constructor(
    @Optional()  // won't throw if not registered
    @Inject('ANALYTICS_PROVIDER')
    private analyticsProvider?: any,
  ) {}

  track(event: string) {
    if (this.analyticsProvider) {
      this.analyticsProvider.track(event);  // use if available
    }
    // gracefully skip if not configured
  }
}

// ─── 5. TESTING WITH DI ──────────────────────────────────────────────────────
import { Test, TestingModule } from '@nestjs/testing';

describe('OrdersService', () => {
  let service: OrdersService;
  let userRepository: jest.Mocked<UserRepository>;

  beforeEach(async () => {
    const mockUserRepository = {
      findById: jest.fn(),
      findAll: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        OrdersService,
        {
          provide: UserRepository,      // replace real class...
          useValue: mockUserRepository,  // ...with mock object
        },
        {
          provide: EmailService,
          useValue: { sendWelcomeEmail: jest.fn() },  // mock email
        },
      ],
    }).compile();

    service = module.get<OrdersService>(OrdersService);
    userRepository = module.get(UserRepository);
  });

  it('should throw NotFoundException if user not found', async () => {
    userRepository.findById.mockReturnValue(null);  // simulate missing user
    
    await expect(
      service.placeOrder('nonexistent-id', ['item1'])
    ).rejects.toThrow(NotFoundException);
  });

  it('should place order for existing user', async () => {
    userRepository.findById.mockReturnValue({
      id: '1', email: 'test@example.com', name: 'Test',
    });
    
    const order = await service.placeOrder('1', ['Phone']);
    expect(order.userId).toBe('1');
    expect(order.items).toContain('Phone');
  });
});
```

---

## 🟠 Express.js vs NestJS Comparison

```typescript
// ─── DEPENDENCY MANAGEMENT COMPARISON ────────────────────────────────────────

// EXPRESS (manual dependency creation):
const db = new Database(config);
const userRepository = new UserRepository(db);
const emailService = new EmailService(smtpConfig);
const orderService = new OrderService(userRepository, emailService);

// To test:
const mockDb = { query: jest.fn() };
const mockUserRepo = new UserRepository(mockDb);  // must create with mock
const mockEmail = { send: jest.fn() };
const testOrderService = new OrderService(mockUserRepo, mockEmail);  // manual

// NESTJS (DI container handles it):
// To use:
@Injectable()
class OrderService {
  constructor(
    private userRepo: UserRepository,    // DI provides automatically
    private emailService: EmailService,  // DI provides automatically
  ) {}
}

// To test:
const module = await Test.createTestingModule({
  providers: [
    OrderService,
    { provide: UserRepository, useValue: { findById: jest.fn() } },
    { provide: EmailService, useValue: { send: jest.fn() } },
  ],
}).compile();
// DI container handles the wiring — test just swaps implementations
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `@Injectable()` on providers
```typescript
// WRONG: No @Injectable() → DI can't use this class
class EmailService {  // ← missing @Injectable()
  sendEmail() {}
}

// Error: "Nest can't resolve dependencies of OrdersService (EmailService)"

// CORRECT:
@Injectable()
class EmailService {
  sendEmail() {}
}
```

❌ **Mistake 2:** Not registering in module's providers array
```typescript
// WRONG: EmailService exists but not in module
@Module({
  providers: [OrdersService],  // EmailService not listed!
})
export class OrdersModule {}

// OrdersService constructor wants EmailService → DI can't find it
// Error: "Nest can't resolve dependencies"

// CORRECT:
@Module({
  providers: [OrdersService, EmailService],  // both registered
})
export class OrdersModule {}
```

❌ **Mistake 3:** Not exporting providers needed by other modules
```typescript
// WRONG: UsersService available only in UsersModule
@Module({
  providers: [UsersService],
  // exports: [] ← not exported!
})
export class UsersModule {}

// OrdersModule imports UsersModule but can't inject UsersService
// Error: "Nest can't resolve dependencies of OrdersService (UsersService)"

// CORRECT:
@Module({
  providers: [UsersService],
  exports: [UsersService],  // ← other modules can now inject it
})
export class UsersModule {}
```

---

## 🧠 Tricky Interview Question

**Q: What is the difference between `useClass`, `useValue`, `useFactory`, and `useExisting` in custom providers?**

**Answer:**
- `useClass`: provide an alternative class. `{ provide: EmailService, useClass: MockEmailService }` — when `EmailService` is injected, `MockEmailService` is instantiated.
- `useValue`: provide a static value/object. `{ provide: CONFIG, useValue: { timeout: 5000 } }` — injects the exact value as-is. Good for config objects, mock objects in tests.
- `useFactory`: use a factory function (sync or async) to create the value. `{ provide: DB_CONNECTION, useFactory: async () => await db.connect() }` — good for async initialization.
- `useExisting`: alias one token to another. `{ provide: NewService, useExisting: OldService }` — both tokens inject the same instance. Good for backwards compatibility.

---

## ⚫ Interview Questions + Answers

**Q1: What is Dependency Injection and why does NestJS use it?**
A1: DI is a pattern where a class declares what it needs (dependencies) in its constructor, and an external container provides those instances. NestJS uses it because: (1) Loose coupling — classes don't create their own dependencies, so implementations can be swapped. (2) Testability — inject mocks in tests without changing class code. (3) Singleton management — container ensures one instance (singleton scope default), preventing multiple DB connections. (4) Circular dependency resolution — container can handle some circular deps via `forwardRef()`. It requires TypeScript (for metadata reflection to know what types to inject) and the `reflect-metadata` package.

**Q2: What is provider scope in NestJS? What are the 3 scopes?**
A2: **DEFAULT (Singleton)**: one instance per module, shared across all requests. Created once, garbage collected when module is destroyed. Best for: stateless services (most services). **REQUEST**: new instance created for each incoming request. Useful for: request-specific logging, audit trails, current-user context. Caveat: any singleton that injects a request-scoped provider also becomes request-scoped. **TRANSIENT**: new instance every time it's injected. Useful for: stateful helpers where each consumer needs its own instance. Avoid unless needed — most expensive scope.

**Q3: How does NestJS know what to inject into a constructor?**
A3: NestJS uses TypeScript's `emitDecoratorMetadata` (enabled in `tsconfig.json`) + `reflect-metadata` library. When you write `constructor(private userService: UserService)`, TypeScript emits metadata about the parameter types. NestJS reads this metadata at runtime: "first param type is UserService." Then looks up `UserService` in the DI container, finds the registered provider, and injects it. For non-class tokens (strings, symbols), use `@Inject(TOKEN)` decorator since TypeScript can't emit metadata for non-class types.

**Q4: What is `forwardRef()` and when do you use it?**
A4: Circular dependencies (A depends on B, B depends on A) can cause `undefined` at module load time since one must be defined first. `forwardRef()` is a lazy reference that defers resolution: `constructor(@Inject(forwardRef(() => BService)) private bService: BService)`. Also used in modules: `imports: [forwardRef(() => BModule)]`. Best practice: avoid circular dependencies by extracting shared functionality to a third module. `forwardRef()` is a workaround, not a design goal.

**Q5: How do you share a service between two different modules?**
A5: Three steps: (1) Make the service `@Injectable()`. (2) In the MODULE that owns the service, add it to `providers` AND `exports`: `@Module({ providers: [UsersService], exports: [UsersService] })`. (3) In the MODULE that needs it, add the owning module to `imports`: `@Module({ imports: [UsersModule], providers: [OrdersService] })`. Now `OrdersService` can inject `UsersService` via constructor. If you want a service available everywhere without repeating imports, use `@Global()` on the module + export the service — then importing it once in `AppModule` makes it available everywhere.

---

## 📊 Visual Diagram

```
DI CONTAINER FLOW:
──────────────────────────────────────────────────────────────────

  MODULE REGISTRATION:
  @Module({
    providers: [OrdersService, UserRepository, EmailService]
  })
  
  DI CONTAINER:
  ┌────────────────────────────────────────────────────────────┐
  │  Registry:                                                  │
  │  UserRepository → instance (singleton)                     │
  │  EmailService   → instance (singleton)                     │
  │  OrdersService  → "needs UserRepository + EmailService"    │
  └──────────────────────────────┬─────────────────────────────┘
                                 │
  When OrdersService is needed:  │
                                 ▼
  ┌────────────────────────────────────────────────────────────┐
  │  1. Create/get UserRepository instance                     │
  │  2. Create/get EmailService instance                       │
  │  3. Create OrdersService(userRepository, emailService)     │
  │  4. Cache as singleton                                     │
  └────────────────────────────────────────────────────────────┘
  
  TESTING WITH DI:
  Real code:                    Test code:
  providers: [                  providers: [
    OrdersService,                OrdersService,
    UserRepository,    →          { provide: UserRepository,
    EmailService,                   useValue: mockRepo },
  ]                               { provide: EmailService,
                                    useValue: mockEmail },
                                ]
  DI container wires it      DI container wires it (with mocks!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dependency Injection | Container provides deps to class | Container class को dependencies देता है |
| @Injectable() | Marks class as DI provider | DI provider के रूप में mark करो |
| Provider | Any injectable class/value/factory | DI से inject होने वाली कोई भी चीज़ |
| Singleton scope | One instance per module | Module में एक ही instance |
| Request scope | New instance per HTTP request | हर HTTP request के लिए नया instance |
| Injection token | Key to identify a provider | Provider identify करने की key |
| forwardRef() | Lazy reference for circular deps | Circular dependency के लिए lazy reference |
| useFactory | Factory function for dynamic provider | Dynamic provider के लिए factory function |
| exports | Make providers available to other modules | दूसरे modules को provider share करना |

---

## ⚡ 3-Line Summary
**English:**
1. DI in NestJS: mark class `@Injectable()` → register in module `providers` → inject via constructor — NestJS container creates and manages singleton instances automatically.
2. Testing superpower: swap any real service with a mock using `overrideProvider()` in `TestingModule` — no real DB or external API calls in unit tests.
3. Common issues: missing `@Injectable()`, not registering in `providers`, not `exports`-ing for cross-module injection — these three cause "can't resolve dependencies" errors.

**Hindi:**
1. NestJS DI: `@Injectable()` mark करो → module `providers` में register करो → constructor में inject करो — container singleton instances automatically बनाता है।
2. Testing: `TestingModule` में `overrideProvider()` से real service को mock से replace — no real DB calls।
3. Common errors: `@Injectable()` missing, `providers` में register नहीं, `exports` में नहीं — तीनों "can't resolve dependencies" error देते हैं।

---

## ➡️ Next Topic
**39. Provider Scopes** — Singleton vs Request vs Transient, performance implications।
