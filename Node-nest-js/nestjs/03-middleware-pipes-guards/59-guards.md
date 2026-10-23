# 59. Guards — Authentication & Authorization
# हिंदी में: Guards — कौन आ सकता है, क्या कर सकता है

---

## 🔵 Simple Definition (English)
**Guards** in NestJS implement the `CanActivate` interface and determine whether a request should proceed to the route handler. They return `true` (allow) or `false`/throw `ForbiddenException` (deny). Guards are primarily used for: **authentication** (is this user logged in?) and **authorization** (is this user allowed to do this?). They run AFTER middleware but BEFORE pipes and interceptors — perfect for auth because you want to authenticate before validating/transforming data.

## 🔵 सरल परिभाषा (Hindi)
**Guards** NestJS में `CanActivate` interface implement करते हैं और decide करते हैं कि request route handler तक जाए या नहीं। `true` return करे तो allow, `false`/`ForbiddenException` throw करे तो deny। Guards primarily: **authentication** (क्या user logged in है?) और **authorization** (क्या user यह करने का अधिकार रखता है?)। Middleware के बाद, pipes से पहले run होते हैं।

---

## 🔴 Problem it Solves
```
WITHOUT GUARDS:
  Every route handler or service must manually check auth:
  
  @Get('/orders')
  async getOrders(@Headers('authorization') auth: string) {
    if (!auth?.startsWith('Bearer ')) {
      throw new UnauthorizedException();
    }
    const token = auth.split(' ')[1];
    let user;
    try {
      user = jwt.verify(token, process.env.JWT_SECRET);
    } catch {
      throw new UnauthorizedException('Invalid token');
    }
    if (user.role !== 'admin') {
      throw new ForbiddenException('Admin only');
    }
    // FINALLY: actual logic
    return this.ordersService.findAll();
  }
  
  Repeated in EVERY protected route → maintenance nightmare

WITH GUARDS:
  @UseGuards(JwtAuthGuard, AdminGuard)  ← one line
  @Get('/orders')
  getOrders() {
    return this.ordersService.findAll();  // guard ensured auth+authz
  }
```

---

## 🟡 Real World Example
**Meesho seller platform:** 4 user roles: `buyer`, `seller`, `admin`, `superadmin`. Routes: public (product listing), authenticated (order placement), seller-only (add product), admin-only (manage users), superadmin-only (system config). Guards: `JwtAuthGuard` for all protected routes, `RolesGuard` for role-based access. Custom `SellerVerificationGuard`: check if seller's KYC is approved before allowing them to list products. All with `@UseGuards()` decorator — route handler stays clean.

---

## 💻 Code Example — Basic

```typescript
// guards-basics.ts

// ─── 1. JWT AUTH GUARD ────────────────────────────────────────────────────────
import {
  Injectable, CanActivate, ExecutionContext,
  UnauthorizedException, ForbiddenException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private jwtService: JwtService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // ExecutionContext: access HTTP request, WebSocket data, RPC context
    const request = context.switchToHttp().getRequest<Request>();

    const token = this.extractToken(request);
    if (!token) {
      throw new UnauthorizedException('No token provided');
    }

    try {
      const payload = await this.jwtService.verifyAsync(token, {
        secret: process.env.JWT_SECRET,
      });

      // Attach user to request for use in route handlers
      request['user'] = payload;  // { userId, email, role, iat, exp }
      return true;  // ← allow request through

    } catch (err) {
      if (err.name === 'TokenExpiredError') {
        throw new UnauthorizedException('Token expired');
      }
      throw new UnauthorizedException('Invalid token');
    }
  }

  private extractToken(request: Request): string | null {
    const authHeader = request.headers.authorization;
    if (!authHeader?.startsWith('Bearer ')) return null;
    return authHeader.split(' ')[1];
  }
}

// ─── 2. ROLES GUARD (RBAC) ────────────────────────────────────────────────────
import { SetMetadata } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

// Custom decorator to set required roles on routes
export const Roles = (...roles: string[]) => SetMetadata('roles', roles);
// Usage: @Roles('admin', 'superadmin')

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // Read roles from @Roles() decorator on route or controller
    const requiredRoles = this.reflector.getAllAndOverride<string[]>('roles', [
      context.getHandler(),  // method-level decorator (checked first)
      context.getClass(),    // class-level decorator (fallback)
    ]);

    if (!requiredRoles) return true;  // no @Roles() = public route

    const request = context.switchToHttp().getRequest();
    const user = request.user;  // set by JwtAuthGuard

    if (!user) {
      throw new UnauthorizedException('Not authenticated');
    }

    const hasRole = requiredRoles.some(role => user.roles?.includes(role));
    if (!hasRole) {
      throw new ForbiddenException(
        `Access denied. Required roles: ${requiredRoles.join(', ')}`
      );
    }

    return true;
  }
}

// ─── 3. USAGE IN CONTROLLERS ──────────────────────────────────────────────────
import { UseGuards, Get, Post, Controller } from '@nestjs/common';

@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)  // applies to ALL routes in this controller
export class AdminController {
  @Get('users')
  @Roles('admin', 'superadmin')  // only admin or superadmin
  getAllUsers() {
    return this.adminService.getAllUsers();
  }

  @Post('ban-user/:id')
  @Roles('superadmin')  // only superadmin
  banUser(@Param('id') id: string) {
    return this.adminService.banUser(id);
  }
}

@Controller('orders')
export class OrdersController {
  @Get('my-orders')
  @UseGuards(JwtAuthGuard)  // only authenticated, any role
  getMyOrders(@Request() req) {
    return this.ordersService.findByUser(req.user.userId);
  }

  @Get('all')  // public route, no guard
  getAllPublicOrders() {
    return this.ordersService.findPublic();
  }
}
```

## 💻 Code Example — Advanced

```typescript
// advanced-guards.ts — Passport integration, custom decorators, ownership guard

// ─── 1. @nestjs/passport INTEGRATION ─────────────────────────────────────────
import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

// Passport strategy (defined separately in auth module)
// This guard ties to the 'jwt' Passport strategy
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  // Passport handles JWT verification via JwtStrategy
  // We just extend AuthGuard — no manual JWT verification needed!
  
  // Override to customize error messages
  handleRequest(err: any, user: any, info: any) {
    if (err || !user) {
      throw err || new UnauthorizedException(
        info?.message || 'Authentication required'
      );
    }
    return user;
  }
}

// ─── 2. COMBINED AUTH GUARD (optional route) ──────────────────────────────────
// Some routes work for both authenticated and anonymous users
// but provide different data based on auth status
@Injectable()
export class OptionalAuthGuard extends AuthGuard('jwt') {
  handleRequest(err: any, user: any) {
    // Don't throw on auth failure — just return null
    return user || null;  // null for anonymous
  }
}

// Usage: @UseGuards(OptionalAuthGuard)
// req.user = user object if authenticated, null if not

// ─── 3. RESOURCE OWNERSHIP GUARD ─────────────────────────────────────────────
// Ensure users can only modify their own resources
@Injectable()
export class OwnershipGuard implements CanActivate {
  constructor(private ordersService: OrdersService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const user = request.user;  // set by JwtAuthGuard (must run first!)
    const orderId = request.params.id;

    if (!user) throw new UnauthorizedException();

    // Admins can access any order
    if (user.role === 'admin') return true;

    // Regular users can only access their own orders
    const order = await this.ordersService.findById(orderId);
    if (!order) throw new NotFoundException(`Order ${orderId} not found`);

    if (order.userId !== user.userId) {
      throw new ForbiddenException('You can only access your own orders');
    }

    return true;
  }
}

// ─── 4. CUSTOM DECORATOR: @CurrentUser() ──────────────────────────────────────
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export const CurrentUser = createParamDecorator(
  (data: string | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    const user = request.user;
    return data ? user?.[data] : user;
    // @CurrentUser() → whole user object
    // @CurrentUser('email') → just user.email
  },
);

// Usage in controller:
@Controller('profile')
@UseGuards(JwtAuthGuard)
export class ProfileController {
  @Get()
  getProfile(@CurrentUser() user: any) {
    // No req.user access needed — clean!
    return this.usersService.getProfile(user.userId);
  }

  @Get('email-only')
  getEmail(@CurrentUser('email') email: string) {
    return { email };
  }
}

// ─── 5. @Public() DECORATOR — skip guard for specific routes ─────────────────
export const Public = () => SetMetadata('isPublic', true);

@Injectable()
export class GlobalJwtGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) {
    super();
  }

  canActivate(context: ExecutionContext) {
    // Check if route is marked as @Public()
    const isPublic = this.reflector.getAllAndOverride<boolean>('isPublic', [
      context.getHandler(),
      context.getClass(),
    ]);

    if (isPublic) return true;  // skip auth check

    return super.canActivate(context);  // normal JWT check
  }
}

// Usage: enable global guard, then mark specific routes as public
// main.ts: app.useGlobalGuards(new GlobalJwtGuard(reflector))

@Controller('auth')
export class AuthController {
  @Post('login')
  @Public()  // ← this route skips the global JWT guard
  login(@Body() dto: LoginDto) {
    return this.authService.login(dto);
  }

  @Get('me')  // ← this route requires JWT (protected by global guard)
  getMe(@CurrentUser() user: any) {
    return user;
  }
}
```

---

## 🟠 Express.js vs NestJS Comparison

```typescript
// ─── AUTH COMPARISON ──────────────────────────────────────────────────────────

// EXPRESS MIDDLEWARE (manually apply per route):
const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

const requireAdmin = (req, res, next) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  next();
};

// Must manually add to each route:
router.get('/admin/users', authenticate, requireAdmin, (req, res) => {...});
router.post('/admin/ban', authenticate, requireAdmin, (req, res) => {...});

// NESTJS GUARDS (declarative, reusable):
@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)  // ← applies to ALL routes in controller
export class AdminController {
  @Get('users')
  @Roles('admin')
  getUsers() {}

  @Post('ban')
  @Roles('admin')
  banUser() {}
}
// Same level of protection, less repetition, type-safe, testable
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using guards for things that should be middleware
```typescript
// WRONG: CORS or logging in a guard
@Injectable()
export class CorsGuard implements CanActivate {
  canActivate(ctx: ExecutionContext) {
    const req = ctx.switchToHttp().getRequest();
    // Setting CORS headers in a guard
    ctx.switchToHttp().getResponse().setHeader('Access-Control-Allow-Origin', '*');
    return true;
  }
}
// Guards are for auth/authz. CORS, logging, body parsing → middleware

// CORRECT: Use NestJS built-in CORS or helmet middleware
app.enableCors();  // in main.ts
app.use(helmet());
```

❌ **Mistake 2:** Not setting `request.user` in JwtAuthGuard
```typescript
// WRONG: Guard validates token but doesn't attach user
canActivate(ctx: ExecutionContext) {
  const token = extractToken(ctx);
  jwt.verify(token, secret);  // throws if invalid
  return true;  // ← user not attached!
}

// Route handler can't access req.user
@Get('me')
getMe(@Request() req) {
  console.log(req.user);  // undefined!
}

// CORRECT:
canActivate(ctx: ExecutionContext) {
  const request = ctx.switchToHttp().getRequest();
  const payload = jwt.verify(token, secret);
  request['user'] = payload;  // ← attach user!
  return true;
}
```

❌ **Mistake 3:** Wrong guard order (RolesGuard before JwtAuthGuard)
```typescript
// WRONG: RolesGuard runs before JWT sets req.user
@UseGuards(RolesGuard, JwtAuthGuard)  // ← wrong order!
// RolesGuard tries to read req.user → undefined → always fails

// CORRECT: JWT first (sets req.user), then roles (reads req.user)
@UseGuards(JwtAuthGuard, RolesGuard)  // ← correct order
```

---

## 🧠 Tricky Interview Question

**Q: How do you make some routes in a globally-guarded controller public?**

**Answer:** Use the `@Public()` custom decorator pattern:
1. Create `@Public()` decorator: `export const Public = () => SetMetadata('isPublic', true)`
2. In global guard's `canActivate`, use `Reflector.getAllAndOverride('isPublic', [...])` to check if the route is marked public
3. If `isPublic === true`, return `true` immediately (skip JWT check)
4. Otherwise, proceed with normal JWT verification

This is cleaner than removing the global guard and manually adding `@UseGuards(JwtAuthGuard)` to every protected route (which is error-prone — you might forget one).

---

## ⚫ Interview Questions + Answers

**Q1: What are guards in NestJS and how do they differ from middleware?**
A1: Both intercept requests, but: **Middleware** runs before guards, has no access to execution context (can't know which handler will be called, which decorators are on it). **Guards** run after middleware, have access to `ExecutionContext` (can read decorator metadata with `Reflector`, know which controller/method will handle the request). This is why RBAC with custom decorators (`@Roles('admin')`) works in guards but not middleware. Middleware is for: CORS, logging, body parsing. Guards are for: authentication, authorization, feature flags.

**Q2: What is the `ExecutionContext` in NestJS guards?**
A2: `ExecutionContext` is an abstraction that wraps the underlying request/response, supporting multiple transport types. `context.switchToHttp()` for HTTP (Express/Fastify), `context.switchToWs()` for WebSockets, `context.switchToRpc()` for microservices. `.getRequest()` returns the typed request object. `.getHandler()` returns the method being called. `.getClass()` returns the controller class. Guards using `Reflector` read metadata from `getHandler()` and `getClass()` to check decorators like `@Roles()` or `@Public()`.

**Q3: What is the difference between `UnauthorizedException` and `ForbiddenException`?**
A3: **`UnauthorizedException` (401 Unauthorized)**: user is NOT authenticated — no token, invalid token, expired token. User needs to log in. HTTP standard: 401 requires `WWW-Authenticate` header. **`ForbiddenException` (403 Forbidden)**: user IS authenticated but does NOT have permission for this resource. Token is valid but role is wrong. "You are logged in but not allowed here." Always throw 401 for auth failures (use JwtAuthGuard) and 403 for authorization failures (use RolesGuard) — confusing them is a common mistake.

**Q4: How do you test a NestJS guard?**
A4: Create a `TestingModule` with the guard and its dependencies mocked. Test `canActivate()` directly with a mock `ExecutionContext`. Example:
```typescript
const mockContext = {
  switchToHttp: () => ({
    getRequest: () => ({ headers: { authorization: 'Bearer validtoken' } }),
  }),
  getHandler: () => ({}),
  getClass: () => ({}),
};
const result = await guard.canActivate(mockContext as any);
expect(result).toBe(true);
```
For integration tests, use Supertest with `app.useGlobalGuards()` and pass JWT token in headers.

**Q5: What is the `Reflector` and how is it used in guards?**
A5: `Reflector` is a NestJS utility to read metadata set by decorators. When you use `@Roles('admin')` (which calls `SetMetadata('roles', ['admin'])`), the metadata is attached to the route handler. In the guard, `reflector.getAllAndOverride<string[]>('roles', [context.getHandler(), context.getClass()])` reads the `roles` metadata — first from the method (handler), then from the class (controller). `getAllAndOverride` returns the method-level value if present, otherwise the class-level value. Use `getAllAndMerge` to combine both arrays (method + class roles).

---

## 📊 Visual Diagram

```
GUARD POSITION & RBAC FLOW:
──────────────────────────────────────────────────────────────────

  HTTP Request: DELETE /admin/users/123
  Headers: { Authorization: "Bearer eyJ..." }
       │
       ▼
  [Middleware] cors, helmet, express.json
       │
       ▼
  [GUARD 1: JwtAuthGuard]
  ├── Extract token from Authorization header
  ├── jwt.verify(token, secret)
  ├── Valid? → request.user = { userId: '456', role: 'admin' }
  ├── Invalid? → throw UnauthorizedException (401) → STOP
  └── return true → continue
       │
       ▼
  [GUARD 2: RolesGuard]
  ├── Read @Roles() metadata from controller method
  ├── Required: ['superadmin']
  ├── request.user.role = 'admin'
  ├── 'admin' not in ['superadmin']?
  ├── throw ForbiddenException (403) → STOP
  └── return true → continue
       │
       ▼
  [Pipes] ValidationPipe
       │
       ▼
  [Controller Handler] deleteUser(@Param('id') id: string)

ROLE HIERARCHY EXAMPLE:
  @Roles('admin', 'superadmin')  ← allows either
  @Roles('superadmin')           ← superadmin only
  @Public()                      ← no auth needed
  // No decorator + global guard ← any authenticated user
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Guard | Decide allow/deny for request | Request allow/deny का decision |
| CanActivate | Interface guards implement | Guards जो interface implement करते हैं |
| ExecutionContext | Access to request/handler metadata | Request + handler metadata access |
| Reflector | Read decorator metadata | Decorator metadata पढ़ने का tool |
| @Roles() | Custom decorator for role metadata | Role metadata set करने का decorator |
| UnauthorizedException | 401 — not logged in | 401 — login नहीं है |
| ForbiddenException | 403 — no permission | 403 — permission नहीं है |
| @CurrentUser() | Custom param decorator for req.user | req.user का clean access |
| @Public() | Mark route to skip global guard | Global guard skip करने का marker |

---

## ⚡ 3-Line Summary
**English:**
1. Guards implement `CanActivate`, run after middleware but before pipes — return `true` to allow, throw `UnauthorizedException`/`ForbiddenException` to deny.
2. Common pattern: `JwtAuthGuard` (sets `req.user`) + `RolesGuard` (reads `req.user.role` vs `@Roles()` decorator) — always `@UseGuards(JwtAuthGuard, RolesGuard)` in that order.
3. For a global guard with public exceptions: apply globally + `@Public()` decorator + check `isPublic` metadata via `Reflector` in the guard — cleaner than adding `@UseGuards` everywhere.

**Hindi:**
1. Guards `CanActivate` implement करते हैं — `true` return करो allow, `UnauthorizedException`/`ForbiddenException` throw करो deny।
2. Common pattern: `JwtAuthGuard` (req.user set करे) + `RolesGuard` (req.user.role vs @Roles() check करे) — always इसी order में।
3. Global guard + @Public() pattern: global guard set करो, public routes पर `@Public()` decorator लगाओ।

---

## ➡️ Next Topic
**60. Interceptors** — Transform responses, logging, caching — before and after handler।
