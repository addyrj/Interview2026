# 51. Pipes — Validation & Transformation
# हिंदी में: Pipes — Data Validate और Transform करो

---

## 🔵 Simple Definition (English)
**Pipes** in NestJS are classes that implement `PipeTransform`. They run before the route handler and do two things: (1) **Transformation** — convert input to desired format (string → number, plain object → class instance), (2) **Validation** — validate input and throw `BadRequestException` if invalid. The most important built-in pipe is `ValidationPipe` with `class-validator` decorators on DTOs. If validation fails, NestJS returns a 400 response automatically — route handler never runs.

## 🔵 सरल परिभाषा (Hindi)
**Pipes** NestJS में `PipeTransform` implement करने वाली classes हैं। Route handler से पहले run होते हैं और दो काम करते हैं: (1) **Transformation** — input को desired format में convert (string → number, plain object → class instance), (2) **Validation** — input validate करो, invalid हो तो `BadRequestException` throw करो। Most important: `ValidationPipe` with `class-validator` decorators on DTOs। Validation fail → 400 response automatically, route handler run नहीं होता।

---

## 🔴 Problem it Solves
```
WITHOUT PIPES (manual validation — tedious):
  @Post('/orders')
  async createOrder(@Body() body: any, @Param('userId') userId: string) {
    // Manual validation — every route handler
    if (!body.items || !Array.isArray(body.items)) {
      throw new BadRequestException('items must be array');
    }
    if (body.items.length === 0) {
      throw new BadRequestException('items cannot be empty');
    }
    if (!body.address || typeof body.address !== 'string') {
      throw new BadRequestException('address must be string');
    }
    // 20 more lines of validation...
    
    const userIdNum = parseInt(userId);  // manual transform
    if (isNaN(userIdNum)) {
      throw new BadRequestException('userId must be a number');
    }
    
    // FINALLY: business logic
    return this.ordersService.create(userIdNum, body.items, body.address);
  }

WITH PIPES:
  @Post('/orders')
  createOrder(
    @Body() dto: CreateOrderDto,      // ← ValidationPipe validates automatically
    @Param('userId', ParseIntPipe) userId: number,  // ← ParseIntPipe transforms
  ) {
    // userId is already a number, dto already validated
    return this.ordersService.create(userId, dto);
    // This is ALL the code needed
  }
```

---

## 🟡 Real World Example
**Zomato order API:** Every order request must have: valid restaurant ID (UUID), non-empty items array, each item with positive quantity, delivery address (min 10 chars), valid payment method (enum: 'upi'|'card'|'cash'). With `ValidationPipe` + `class-validator` on a DTO: 40 lines of manual validation → 10 lines of decorators. Plus: `ParseIntPipe` for route params ensures `/orders/abc` returns 400 instead of letting `NaN` reach the service.

---

## 💻 Code Example — Basic

```typescript
// pipes-basics.ts

// ─── 1. BUILT-IN PIPES ────────────────────────────────────────────────────────
import {
  Controller, Get, Post, Body, Param, Query,
  ParseIntPipe, ParseUUIDPipe, ParseBoolPipe, ParseArrayPipe,
  DefaultValuePipe, ValidationPipe,
  BadRequestException, UsePipes,
} from '@nestjs/common';

@Controller('products')
export class ProductsController {
  // ParseIntPipe: converts string route param → number
  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    // id is guaranteed to be a number
    // GET /products/5 → id = 5
    // GET /products/abc → 400 "Validation failed (numeric string is expected)"
    return this.productsService.findOne(id);
  }

  // ParseUUIDPipe: validates UUID format
  @Get('by-uuid/:uuid')
  findByUuid(@Param('uuid', ParseUUIDPipe) uuid: string) {
    // GET /products/by-uuid/123-invalid → 400 error
    // GET /products/by-uuid/550e8400-e29b-41d4-a716-446655440000 → valid
    return this.productsService.findByUuid(uuid);
  }

  // DefaultValuePipe: provide default if param missing
  @Get()
  findAll(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(10), ParseIntPipe) limit: number,
    @Query('active', new DefaultValuePipe(true), ParseBoolPipe) active: boolean,
  ) {
    // GET /products → page=1, limit=10, active=true (defaults)
    // GET /products?page=2 → page=2, limit=10
    return this.productsService.findAll({ page, limit, active });
  }

  // ValidationPipe on a specific route (can also be global)
  @Post()
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  create(@Body() createProductDto: CreateProductDto) {
    return this.productsService.create(createProductDto);
  }
}
```

## 💻 Code Example — Advanced

```typescript
// advanced-pipes.ts — ValidationPipe + class-validator + custom pipe

// ─── 1. DTO WITH class-validator DECORATORS ───────────────────────────────────
import {
  IsString, IsNumber, IsEmail, IsEnum, IsArray, IsOptional,
  IsUUID, IsUrl, IsPositive, Min, Max, MinLength, MaxLength,
  ArrayMinSize, ArrayMaxSize, IsNotEmpty, ValidateNested, Type,
  IsDateString,
} from 'class-validator';
import { Type as TransformType, Transform } from 'class-transformer';

enum PaymentMethod {
  UPI = 'upi',
  CARD = 'card',
  CASH = 'cash',
  NETBANKING = 'netbanking',
}

class OrderItemDto {
  @IsUUID('4')
  productId: string;

  @IsNumber()
  @IsPositive()
  @Max(100)  // can't order more than 100 of one item
  quantity: number;

  @IsOptional()
  @IsString()
  @MaxLength(200)
  specialInstructions?: string;
}

export class CreateOrderDto {
  @IsUUID('4')
  restaurantId: string;

  @IsArray()
  @ArrayMinSize(1, { message: 'Order must have at least 1 item' })
  @ArrayMaxSize(20, { message: 'Cannot order more than 20 different items' })
  @ValidateNested({ each: true })  // validate each item in array
  @Type(() => OrderItemDto)        // transform each item to OrderItemDto class
  items: OrderItemDto[];

  @IsString()
  @MinLength(10)
  @MaxLength(500)
  deliveryAddress: string;

  @IsEnum(PaymentMethod, {
    message: `paymentMethod must be one of: ${Object.values(PaymentMethod).join(', ')}`,
  })
  paymentMethod: PaymentMethod;

  @IsOptional()
  @IsDateString()  // validates ISO 8601 date string
  scheduledAt?: string;

  @IsOptional()
  @IsString()
  @MaxLength(300)
  deliveryInstructions?: string;

  // Transform: trim whitespace + lowercase email
  @IsEmail()
  @Transform(({ value }) => value?.toLowerCase().trim())
  userEmail: string;
}

// ─── 2. GLOBAL VALIDATION PIPE (set in main.ts) ────────────────────────────────
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';

// main.ts:
async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,          // strip any property NOT in DTO
    forbidNonWhitelisted: true, // throw if unknown property received
    transform: true,           // auto-transform payloads to DTO instances
    transformOptions: {
      enableImplicitConversion: true,  // auto-convert query params to declared types
    },
    exceptionFactory: (errors) => {
      // Custom error format
      const messages = errors.map(err => ({
        field: err.property,
        errors: Object.values(err.constraints || {}),
      }));
      throw new BadRequestException({ errors: messages });
    },
  }));

  await app.listen(3000);
}

// ─── 3. CUSTOM PIPE ───────────────────────────────────────────────────────────
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';

// Custom pipe: validate Indian phone number
@Injectable()
export class IndianPhonePipe implements PipeTransform {
  transform(value: any, metadata: ArgumentMetadata) {
    // metadata.type: 'body' | 'query' | 'param' | 'custom'
    // metadata.data: parameter name
    
    if (!value) return value;  // optional — skip if no value

    // Remove spaces, dashes, country code
    const cleaned = value.toString().replace(/[\s\-\+]/g, '').replace(/^91/, '');

    // Validate Indian mobile number: 10 digits starting with 6-9
    const indianPhoneRegex = /^[6-9]\d{9}$/;
    if (!indianPhoneRegex.test(cleaned)) {
      throw new BadRequestException(
        `${metadata.data || 'phone'} must be a valid Indian mobile number`
      );
    }

    return cleaned;  // return cleaned value (transform!)
  }
}

// Usage:
@Controller('users')
export class UsersController {
  @Post('send-otp')
  sendOtp(@Body('phone', IndianPhonePipe) phone: string) {
    // phone is already cleaned and validated as Indian number
    return this.otpService.sendOtp(phone);
  }
}

// ─── 4. PARSE PIPE WITH CUSTOM ERROR ─────────────────────────────────────────
const idParseIntPipe = new ParseIntPipe({
  errorHttpStatusCode: 422,  // Unprocessable Entity instead of 400
  exceptionFactory: (err) =>
    new BadRequestException(`Invalid ID: must be a positive integer. Got: "${err}"`),
});

@Get(':id')
findById(@Param('id', idParseIntPipe) id: number) {
  return this.service.findById(id);
}
```

---

## 🟠 Express.js vs NestJS Comparison

```typescript
// ─── VALIDATION COMPARISON ────────────────────────────────────────────────────

// EXPRESS (manual — repetitive):
app.post('/orders', async (req, res) => {
  const { restaurantId, items, address } = req.body;

  // Manual validation (using Joi, or raw code):
  if (!restaurantId || typeof restaurantId !== 'string') {
    return res.status(400).json({ error: 'restaurantId required' });
  }
  if (!items || !Array.isArray(items) || items.length === 0) {
    return res.status(400).json({ error: 'items must be non-empty array' });
  }
  // 20 more lines...
});

// NESTJS (declarative — reusable):
// 1. Define DTO once
export class CreateOrderDto {
  @IsUUID() restaurantId: string;
  @IsArray() @ArrayMinSize(1) items: OrderItemDto[];
  @IsString() @MinLength(10) address: string;
}

// 2. Use in controller — validation automatic
@Post('orders')
createOrder(@Body() dto: CreateOrderDto) {
  // dto is valid if we reach here
  return this.ordersService.create(dto);
}

// ─── KEY DIFFERENCE ───────────────────────────────────────────────────────────
// Express: validation is middleware or manual code — developer's responsibility
// NestJS: ValidationPipe is a first-class concept — declarative, reusable DTOs
// NestJS also has: ParseIntPipe, ParseUUIDPipe, ParseBoolPipe built-in
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `@Type()` for nested DTOs
```typescript
// WRONG: nested objects are NOT validated
class CreateOrderDto {
  @IsArray()
  @ValidateNested({ each: true })
  items: OrderItemDto[];  // ← @Type(() => OrderItemDto) missing!
  // Result: items array content is NOT validated
}

// CORRECT:
class CreateOrderDto {
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)  // ← required for nested validation
  items: OrderItemDto[];
}
```

❌ **Mistake 2:** `whitelist: true` without understanding
```typescript
// With whitelist: true:
class UserDto {
  @IsString() name: string;
  @IsEmail() email: string;
  // password NOT in DTO
}

// Request body: { name: 'Rahul', email: 'r@r.com', password: 'secret', isAdmin: true }
// After ValidationPipe: { name: 'Rahul', email: 'r@r.com' }
// password and isAdmin STRIPPED silently ✅
// GOOD: prevents mass assignment attacks!
```

❌ **Mistake 3:** Not enabling `transform: true` for implicit conversion
```typescript
// Route: @Get(':id')
// URL: GET /users/5

// WITHOUT transform: true
@Param('id', ParseIntPipe) id: number  // ParseIntPipe needed explicitly

// WITH transform: true + enableImplicitConversion: true
@Param('id') id: number  // auto-converts string "5" to number 5
// Cleaner, but less explicit
```

---

## 🧠 Tricky Interview Question

**Q: What is the difference between `whitelist: true` and `forbidNonWhitelisted: true` in ValidationPipe?**

**Answer:** `whitelist: true` — strips any property from the request body that is NOT decorated with a class-validator decorator in the DTO. Silently removes extra fields. `{ name: 'Rahul', isAdmin: true }` with `name` in DTO → `isAdmin` is removed, no error. `forbidNonWhitelisted: true` (requires `whitelist: true`) — instead of silently removing extra fields, it THROWS a `BadRequestException` listing the unknown properties. Use `whitelist` alone when you want to be lenient (ignore extra fields); use `forbidNonWhitelisted` when extra fields should be an error (strict API contracts).

---

## ⚫ Interview Questions + Answers

**Q1: What are pipes in NestJS and what are their two main uses?**
A1: Pipes implement `PipeTransform` and run between request parameters and the route handler. Two uses: (1) **Transformation**: convert input data type (string to number via `ParseIntPipe`, plain object to class instance via `ValidationPipe` with `transform: true`, trim whitespace via `Transform` decorator). (2) **Validation**: verify data meets requirements — if not, throw `BadRequestException` (returns 400). Built-in pipes: `ValidationPipe`, `ParseIntPipe`, `ParseUUIDPipe`, `ParseBoolPipe`, `ParseArrayPipe`, `DefaultValuePipe`, `ParseEnumPipe`, `ParseFloatPipe`.

**Q2: How do you set up global validation in NestJS?**
A2: In `main.ts`, call `app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }))` before `app.listen()`. This applies validation to ALL routes. Requires: (1) `class-validator` and `class-transformer` packages installed. (2) DTOs with class-validator decorators (`@IsString()`, `@IsEmail()`, etc.). (3) `@Body() createDto: CreateUserDto` in controller — body is transformed to class instance and all decorators are evaluated. Without global pipe, use `@UsePipes()` per route or bind pipe to specific parameter: `@Body(new ValidationPipe()) dto`.

**Q3: What is `class-transformer` and how does it work with `class-validator`?**
A3: `class-transformer` converts plain JavaScript objects to class instances (`plainToInstance`) and vice versa. `class-validator` then validates the class instance using decorator metadata. When `ValidationPipe` receives `{ name: 'Rahul', age: '25' }` (from JSON body), it: (1) Uses `class-transformer` to convert plain object to `CreateUserDto` instance (applying `@Transform`, `@Type` conversions). (2) Uses `class-validator` to check all decorator constraints (`@IsString`, `@IsNumber`, etc.). Both packages work together — `class-validator` validates, `class-transformer` transforms.

**Q4: What is the execution order of pipes relative to guards and interceptors?**
A4: Order: Middleware → Guards → Interceptors (before handler) → **Pipes** → Route Handler → Interceptors (after handler) → Exception Filters. Pipes run AFTER guards (auth check) because there's no point validating body if the request isn't authorized. Pipes run BEFORE the route handler because handler should receive clean, validated data. If pipe throws `BadRequestException`, route handler never runs, and the exception propagates to exception filters.

**Q5: How do you create a custom pipe?**
A5: Implement `PipeTransform` interface with a `transform(value, metadata)` method. Return the transformed value or throw `BadRequestException`. Example:
```typescript
@Injectable()
class TrimStringPipe implements PipeTransform {
  transform(value: any) {
    if (typeof value === 'string') return value.trim();
    return value;
  }
}
```
Use with `@Body('name', TrimStringPipe) name: string` or `@UsePipes(TrimStringPipe)`. The `metadata` parameter has `type` ('body'/'query'/'param') and `data` (parameter name).

---

## 📊 Visual Diagram

```
PIPE POSITION IN REQUEST LIFECYCLE:
──────────────────────────────────────────────────────────────────

  HTTP POST /orders
  Body: { restaurantId: "550e...", items: [{...}], address: "..." }
       │
       ▼
  [Middleware] cors, helmet
       │
       ▼
  [Guards] JwtAuthGuard → user authenticated?
       │
       ▼
  [Interceptors before]
       │
       ▼
  [PIPES] ← YOU ARE HERE
  ValidationPipe {
    1. plainToInstance(CreateOrderDto, body)    // class-transformer
    2. validate(orderDto)                       // class-validator
    3. errors? → throw BadRequestException(400) // stops here
    4. no errors? → pass orderDto to handler    // continues
  }
       │
       ▼
  [Controller Handler] createOrder(dto: CreateOrderDto)
  dto is guaranteed valid, typed, and transformed!
       │
       ▼
  [Service] → [Repository] → [DB]
       │
       ▼
  [Interceptors after]
       │
       ▼
  HTTP Response

VALIDATION ERROR RESPONSE (400):
  {
    "statusCode": 400,
    "message": [
      "restaurantId must be a UUID",
      "items must contain at least 1 elements"
    ],
    "error": "Bad Request"
  }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pipe | Transform/validate before handler | Handler से पहले transform/validate |
| ValidationPipe | Built-in DTO validation | DTO validate करने वाला built-in pipe |
| class-validator | Decorator-based validation library | Decorator से validation |
| class-transformer | Convert plain object to class instance | Plain object → class instance |
| ParseIntPipe | String → number conversion + validation | String को number में convert |
| whitelist | Strip unknown DTO fields | Unknown fields remove करो |
| @ValidateNested | Validate nested objects | Nested objects को validate करो |
| @Type(() => Cls) | Tell class-transformer the type | class-transformer को type बताओ |

---

## ⚡ 3-Line Summary
**English:**
1. Pipes run before the route handler to transform (string → number via `ParseIntPipe`) or validate (DTO via `ValidationPipe` + `class-validator`) incoming data — invalid data throws 400 automatically.
2. Global setup: `app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }))` in `main.ts` — applies to all routes.
3. Key options: `whitelist: true` strips unknown fields (prevents mass assignment), `forbidNonWhitelisted: true` throws on unknown fields, `transform: true` converts body to DTO class instance.

**Hindi:**
1. Pipes route handler से पहले run होते हैं — transform (`ParseIntPipe`) या validate (`ValidationPipe` + `class-validator`) करते हैं; invalid data → automatic 400।
2. Global setup: `app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }))` main.ts में।
3. Key options: `whitelist` unknown fields strip, `forbidNonWhitelisted` unknown पर throw, `transform` body को DTO instance में convert।

---

## ➡️ Next Topic
**52. class-validator Decorators** — All validation decorators, custom validators, groups।
