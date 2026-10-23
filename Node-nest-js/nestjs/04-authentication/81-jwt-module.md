# 81. JWT Module + Passport in NestJS
# हिंदी में: NestJS में JWT Auth Setup

---

## 🔵 Simple Definition (English)
NestJS's `@nestjs/jwt` module wraps `jsonwebtoken` with DI support. `@nestjs/passport` integrates the Passport.js ecosystem with NestJS's guard system. Together: `JwtModule.register({ secret, signOptions })` → `JwtService` injectable everywhere → `JwtStrategy` (Passport strategy) verifies tokens → `JwtAuthGuard extends AuthGuard('jwt')` protects routes. This is the standard NestJS authentication pattern used by most enterprise APIs.

## 🔵 सरल परिभाषा (Hindi)
NestJS का `@nestjs/jwt` module `jsonwebtoken` को DI support के साथ wrap करता है। `@nestjs/passport` Passport.js को NestJS guards के साथ integrate करता है। Together: `JwtModule.register({ secret })` → `JwtService` कहीं भी inject → `JwtStrategy` tokens verify करता है → `JwtAuthGuard` routes protect करता है। यह NestJS का standard authentication pattern है।

---

## 🔴 Problem it Solves
```
WITHOUT @nestjs/jwt (raw jsonwebtoken in NestJS):
  Every service that needs to sign/verify tokens:
    const jwt = require('jsonwebtoken');  // manual require
    const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '15m' });
    // Hard to test (can't inject a mock JWT signer)
    // Secret not centralized (might be different in different services)
    // Can't configure once and use everywhere

WITH @nestjs/jwt:
  // Configure once in AuthModule:
  JwtModule.register({ secret: process.env.JWT_SECRET, signOptions: { expiresIn: '15m' } })
  
  // Use anywhere via DI:
  constructor(private jwtService: JwtService) {}
  const token = this.jwtService.sign(payload);  // uses configured secret
  const payload = this.jwtService.verify(token);
  
  // Easy to test: provide mock JwtService in TestingModule
```

---

## 🟡 Real World Example
**Swiggy delivery partner app:** Partners authenticate with phone OTP → get JWT. Every delivery partner action (accept order, update location, mark delivered) needs JWT verification. `JwtStrategy` verifies token and attaches partner profile to request. `@UseGuards(JwtAuthGuard)` protects all partner routes. `RolesGuard` ensures `delivery_partner` role can't access `restaurant_owner` endpoints. `JwtModule.registerAsync` loads secret from `ConfigService` so it works in test (with test secret) and production.

---

## 💻 Code Example — Basic

```typescript
// Installation:
// npm install @nestjs/passport @nestjs/jwt passport passport-jwt
// npm install --save-dev @types/passport-jwt

// ─── auth/auth.module.ts ──────────────────────────────────────────────────────
import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { JwtStrategy } from './strategies/jwt.strategy';
import { UsersModule } from '../users/users.module';

@Module({
  imports: [
    UsersModule,  // for UsersService (to find users on login)
    PassportModule,

    // Option A: register with static config (simpler)
    JwtModule.register({
      secret: process.env.JWT_SECRET,
      signOptions: { expiresIn: '15m' },
    }),

    // Option B: registerAsync (use ConfigService — better for testing)
    JwtModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        secret: config.get<string>('JWT_SECRET'),
        signOptions: { expiresIn: config.get<string>('JWT_EXPIRES_IN', '15m') },
      }),
    }),
  ],
  controllers: [AuthController],
  providers: [AuthService, JwtStrategy],
  exports: [JwtService, AuthService],  // export JwtService for other modules
})
export class AuthModule {}

// ─── auth/strategies/jwt.strategy.ts ─────────────────────────────────────────
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';
import { UsersService } from '../users/users.service';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy, 'jwt') {
  // 'jwt' is the strategy name — AuthGuard('jwt') refers to this

  constructor(
    private configService: ConfigService,
    private usersService: UsersService,
  ) {
    super({
      // Where to extract token from (Authorization: Bearer <token>)
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),

      // Reject expired tokens
      ignoreExpiration: false,

      // Same secret used to sign tokens
      secretOrKey: configService.get<string>('JWT_SECRET'),
    });
  }

  // validate() called after Passport verifies the JWT signature
  // Whatever this returns is attached to request.user
  async validate(payload: { userId: string; email: string; role: string }) {
    // Optional: fetch fresh user from DB (for up-to-date role, etc.)
    // Trade-off: every request hits DB (loses stateless benefit)
    // If you don't need fresh data: just return payload
    
    const user = await this.usersService.findById(payload.userId);
    if (!user) {
      throw new UnauthorizedException('User no longer exists');
    }
    if (!user.isActive) {
      throw new UnauthorizedException('Account deactivated');
    }

    // This is available as req.user in controllers
    return {
      userId: user.id,
      email: user.email,
      role: user.role,
    };
  }
}

// ─── auth/guards/jwt-auth.guard.ts ────────────────────────────────────────────
import { Injectable, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { Reflector } from '@nestjs/core';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) {
    super();
  }

  canActivate(context: ExecutionContext) {
    // Check @Public() decorator
    const isPublic = this.reflector.getAllAndOverride<boolean>('isPublic', [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    return super.canActivate(context);
  }

  handleRequest(err: any, user: any, info: any) {
    if (err || !user) {
      throw err || new UnauthorizedException(
        info?.message === 'jwt expired' ? 'Token expired' : 'Invalid token'
      );
    }
    return user;
  }
}
```

## 💻 Code Example — Advanced

```typescript
// advanced-jwt-nestjs.ts — Access + Refresh tokens, logout, token rotation

// ─── auth/auth.service.ts ─────────────────────────────────────────────────────
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { User } from '../users/entities/user.entity';
import { LoginDto } from './dto/login.dto';
import { RegisterDto } from './dto/register.dto';

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    private jwtService: JwtService,
    private configService: ConfigService,
  ) {}

  async register(dto: RegisterDto) {
    const existing = await this.userRepository.findOne({ where: { email: dto.email } });
    if (existing) {
      throw new ConflictException('Email already registered');
    }

    const passwordHash = await bcrypt.hash(dto.password, 12);
    const user = await this.userRepository.save({
      email: dto.email,
      name: dto.name,
      passwordHash,
      role: 'user',
    });

    return this.generateTokens(user);
  }

  async login(dto: LoginDto) {
    const user = await this.userRepository.findOne({ where: { email: dto.email } });
    const dummyHash = '$2b$12$dummy.hash.for.timing.attack.protection.00000000';
    const isMatch = await bcrypt.compare(dto.password, user?.passwordHash || dummyHash);

    if (!user || !isMatch) {
      throw new UnauthorizedException('Invalid credentials');
    }

    return this.generateTokens(user);
  }

  async generateTokens(user: User) {
    const payload = { userId: user.id, email: user.email, role: user.role };

    // Access token: short-lived, for API requests
    const accessToken = this.jwtService.sign(payload, {
      secret: this.configService.get('JWT_SECRET'),
      expiresIn: '15m',
    });

    // Refresh token: long-lived, for getting new access tokens
    const refreshToken = this.jwtService.sign(
      { userId: user.id },  // minimal payload
      {
        secret: this.configService.get('JWT_REFRESH_SECRET'),
        expiresIn: '30d',
      }
    );

    // Store refresh token hash in DB
    const refreshTokenHash = await bcrypt.hash(refreshToken, 10);  // 10 rounds (less sensitive)
    await this.userRepository.update(user.id, { refreshTokenHash });

    return { accessToken, refreshToken, user: { id: user.id, email: user.email } };
  }

  async refreshTokens(refreshToken: string) {
    let payload: any;
    try {
      payload = this.jwtService.verify(refreshToken, {
        secret: this.configService.get('JWT_REFRESH_SECRET'),
      });
    } catch {
      throw new UnauthorizedException('Invalid refresh token');
    }

    const user = await this.userRepository.findOne({ where: { id: payload.userId } });
    if (!user?.refreshTokenHash) {
      throw new UnauthorizedException('Refresh token not found');
    }

    // Verify the token matches what we stored
    const tokenMatches = await bcrypt.compare(refreshToken, user.refreshTokenHash);
    if (!tokenMatches) {
      // Possible token reuse — invalidate everything
      await this.userRepository.update(user.id, { refreshTokenHash: null });
      throw new UnauthorizedException('Refresh token reuse detected');
    }

    return this.generateTokens(user);  // rotate: new access + refresh tokens
  }

  async logout(userId: string) {
    await this.userRepository.update(userId, { refreshTokenHash: null });
  }
}

// ─── auth/auth.controller.ts ──────────────────────────────────────────────────
import {
  Controller, Post, Body, Get, Res, Req,
  UseGuards, HttpCode, HttpStatus,
} from '@nestjs/common';
import { Response, Request } from 'express';
import { Public } from '../common/decorators/public.decorator';
import { CurrentUser } from '../common/decorators/current-user.decorator';

@Controller('auth')
export class AuthController {
  constructor(private authService: AuthService) {}

  @Post('register')
  @Public()
  async register(@Body() dto: RegisterDto, @Res({ passthrough: true }) res: Response) {
    const { accessToken, refreshToken, user } = await this.authService.register(dto);

    // Set refresh token as HttpOnly cookie
    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 30 * 24 * 60 * 60 * 1000,  // 30 days
    });

    return { accessToken, user };
  }

  @Post('login')
  @Public()
  @HttpCode(HttpStatus.OK)
  async login(@Body() dto: LoginDto, @Res({ passthrough: true }) res: Response) {
    const { accessToken, refreshToken, user } = await this.authService.login(dto);

    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 30 * 24 * 60 * 60 * 1000,
    });

    return { accessToken, user };
  }

  @Post('refresh')
  @Public()
  @HttpCode(HttpStatus.OK)
  async refresh(@Req() req: Request, @Res({ passthrough: true }) res: Response) {
    const refreshToken = req.cookies['refreshToken'];
    if (!refreshToken) {
      throw new UnauthorizedException('No refresh token');
    }

    const { accessToken, refreshToken: newRefreshToken, user } =
      await this.authService.refreshTokens(refreshToken);

    // Set new refresh token cookie (rotation)
    res.cookie('refreshToken', newRefreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 30 * 24 * 60 * 60 * 1000,
    });

    return { accessToken, user };
  }

  @Post('logout')
  @HttpCode(HttpStatus.OK)
  async logout(
    @CurrentUser('userId') userId: string,
    @Res({ passthrough: true }) res: Response,
  ) {
    await this.authService.logout(userId);
    res.clearCookie('refreshToken');
    return { message: 'Logged out successfully' };
  }

  @Get('me')  // Protected by global JwtAuthGuard
  getMe(@CurrentUser() user: any) {
    return user;
  }
}
```

---

## 🟠 Express.js vs NestJS Comparison

```typescript
// ─── JWT AUTH COMPARISON ──────────────────────────────────────────────────────

// EXPRESS (manual setup):
const jwt = require('jsonwebtoken');

// Sign
const token = jwt.sign(
  { userId: '123', email: 'r@r.com' },
  process.env.JWT_SECRET,
  { expiresIn: '15m' }
);

// Verify middleware
const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// NESTJS (DI + Strategy pattern):
// JwtModule handles config centrally
// JwtStrategy is Passport strategy with validate() hook
// JwtAuthGuard is reusable, testable, decorator-based
// Differences:
// 1. TypeScript types throughout
// 2. JwtService injected anywhere needed (not require() everywhere)
// 3. JwtStrategy.validate() can do additional DB checks + return user object
// 4. Guard: @UseGuards(JwtAuthGuard) one line on route/controller
// 5. @CurrentUser() decorator: clean access to req.user without req.user
// 6. @Public() pattern: opt-out from global guard cleanly
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not using `registerAsync` for config
```typescript
// WRONG: secret hardcoded or read directly from env
JwtModule.register({
  secret: 'hardcoded-secret',  // ← in code = security risk
  // OR:
  secret: process.env.JWT_SECRET,  // ← works but not testable
});

// CORRECT: registerAsync with ConfigService
JwtModule.registerAsync({
  imports: [ConfigModule],
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    secret: config.get('JWT_SECRET'),  // ← injectable, testable, validated
  }),
});
```

❌ **Mistake 2:** Missing `PassportModule` in imports
```typescript
// WRONG: JwtStrategy won't work without PassportModule
@Module({
  imports: [JwtModule.register({...})],  // PassportModule missing!
  providers: [JwtStrategy],
})

// CORRECT:
@Module({
  imports: [PassportModule, JwtModule.register({...})],
  providers: [JwtStrategy],
})
```

❌ **Mistake 3:** Returning sensitive data from JwtStrategy.validate()
```typescript
// WRONG: passwordHash ends up in req.user (every request!)
async validate(payload: any) {
  const user = await this.usersService.findById(payload.userId);
  return user;  // includes passwordHash, refreshTokenHash, etc.!
}

// CORRECT: Return only what's needed
async validate(payload: any) {
  const user = await this.usersService.findById(payload.userId);
  if (!user) throw new UnauthorizedException();
  return { userId: user.id, email: user.email, role: user.role };
}
```

---

## 🧠 Tricky Interview Question

**Q: What is the difference between returning early from `JwtStrategy.validate()` vs throwing `UnauthorizedException`?**

**Answer:** In `JwtStrategy.validate()`: if you return a user object → it becomes `req.user`. If you throw `UnauthorizedException` → Passport catches it and triggers `handleRequest` in the guard, which then re-throws it as a 401 response. If you return `null` or `false` → Passport also triggers `handleRequest` with an error. The key: `validate()` is called ONLY after Passport successfully verifies the JWT signature. If the JWT is expired, malformed, or has wrong signature → `validate()` is never called (Passport throws before). So `validate()` is for business logic checks (user still exists, account not banned), NOT for signature verification.

---

## ⚫ Interview Questions + Answers

**Q1: What is `@nestjs/passport` and why is it used?**
A1: `@nestjs/passport` is a NestJS wrapper around Passport.js, the Node.js authentication middleware. It provides: (1) `PassportStrategy(Strategy, 'name')` base class for creating strategies, (2) `AuthGuard('name')` to create guards from strategies, (3) NestJS DI integration (strategies can inject services). Passport itself has 500+ authentication strategies (Local, JWT, OAuth, SAML, etc.). NestJS uses it to stay framework-agnostic on auth — swap strategies without changing route handlers.

**Q2: What does `JwtStrategy.validate()` do and when is it called?**
A2: `validate()` is called by Passport AFTER the JWT signature is verified. Passport: extracts token → verifies signature with `secretOrKey` → decodes payload → calls `validate(payload)`. What you return from `validate()` becomes `req.user`. You can use this to: fetch fresh user data from DB, check if user is active/banned, add permissions. Caveat: if you DB-query on every request, you lose JWT's stateless benefit. Compromise: use short TTL (15 min), skip DB unless needed, add `tokenVersion` to JWT payload and only check DB when version might be stale.

**Q3: How do you set up refresh token rotation in NestJS?**
A3: (1) Sign refresh token with a DIFFERENT secret (`JWT_REFRESH_SECRET`). (2) Store hash of refresh token in user DB (`bcrypt.hash(refreshToken, 10)` stored in `users.refreshTokenHash`). (3) On `/auth/refresh`: verify refresh token → check hash matches DB → issue new access + refresh tokens → update DB with new refresh token hash (rotation). (4) On reuse detection (token hash doesn't match DB): someone used old token → revoke ALL refresh tokens for user (set `refreshTokenHash = null`) → force re-login. (5) On logout: clear `refreshTokenHash` from DB + clear cookie.

**Q4: How do you make `JwtModule` available across multiple modules?**
A4: Option 1: Put `JwtModule.registerAsync({...})` in `AuthModule` and `exports: [JwtModule, JwtService]`. Other modules that need to sign/verify tokens: `imports: [AuthModule]`. Option 2: Create a shared `JwtHelperModule` that wraps `JwtModule` with `isGlobal: true` → available everywhere without importing. In `main.ts` or `AppModule`. Best practice: centralize token signing in `AuthService` and only export `AuthService` — other modules shouldn't sign tokens directly.

**Q5: How do you test a NestJS service that uses JwtService?**
A5:
```typescript
const module = await Test.createTestingModule({
  providers: [
    AuthService,
    {
      provide: JwtService,
      useValue: {
        sign: jest.fn().mockReturnValue('mock.jwt.token'),
        verify: jest.fn().mockReturnValue({ userId: '123', email: 'test@example.com' }),
      },
    },
    { provide: ConfigService, useValue: { get: jest.fn().mockReturnValue('secret') } },
    // ... other mocks
  ],
}).compile();
```
Providing a mock `JwtService` as `useValue` replaces the real JWT signing with a predictable mock. Test can verify that `sign()` was called with correct payload without running actual JWT operations.

---

## 📊 Visual Diagram

```
NESTJS JWT AUTH FLOW:
──────────────────────────────────────────────────────────────────────

  POST /auth/login { email, password }
       │
       ▼
  AuthService.login()
  ├── bcrypt.compare(password, user.passwordHash)
  ├── JwtService.sign(payload, { secret, expiresIn: '15m' })
  └── Returns: { accessToken, refreshToken }
       │
       ▼
  Client stores:
  ├── accessToken in memory
  └── refreshToken in HttpOnly cookie

  GET /api/orders (protected route)
  Headers: Authorization: Bearer <accessToken>
       │
       ▼
  [JwtAuthGuard extends AuthGuard('jwt')]
       │
       ▼
  [Passport: extract token from Authorization header]
  [Passport: jwt.verify(token, JWT_SECRET)]
  ├── Invalid/expired → UnauthorizedException (401)
  └── Valid → call JwtStrategy.validate(payload)
       │
       ▼
  [JwtStrategy.validate(payload)]
  ├── DB lookup (optional)
  ├── Check user active
  └── return { userId, email, role } → request.user
       │
       ▼
  [Controller] @CurrentUser() user
  ├── user.userId, user.email, user.role available
  └── Calls OrdersService

  TOKEN REFRESH FLOW:
  POST /auth/refresh
  Cookie: refreshToken=<long-lived-token>
       │
       ▼
  JwtService.verify(refreshToken, JWT_REFRESH_SECRET)
  ├── Verify hash matches DB
  ├── Issue new accessToken + refreshToken
  └── Update DB + set new cookie (rotation)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JwtModule | NestJS module wrapping jsonwebtoken | DI-integrated JWT module |
| JwtService | Injectable service for sign/verify | Sign/verify के लिए injectable service |
| PassportStrategy | Base class for Passport strategies | Passport strategy का base class |
| JwtStrategy | Strategy that verifies JWT | JWT verify करने वाली strategy |
| AuthGuard('jwt') | Guard using JwtStrategy | JwtStrategy use करने वाला guard |
| validate() | Called after signature verification | Signature verify के बाद call होता है |
| registerAsync | Factory-based module config | Factory से module config करना |
| @CurrentUser() | Param decorator for req.user | req.user access करने का clean decorator |

---

## ⚡ 3-Line Summary
**English:**
1. NestJS JWT setup: `PassportModule` + `JwtModule.registerAsync()` in auth module → `JwtStrategy extends PassportStrategy(Strategy)` extracts + verifies token → `JwtAuthGuard extends AuthGuard('jwt')` protects routes.
2. `JwtStrategy.validate(payload)` is called after signature verification — return user object → becomes `req.user` — use `@CurrentUser()` decorator to access it cleanly in controllers.
3. Refresh token pattern: different secret + store hash in DB + rotate on each use + detect reuse by checking if hash matches.

**Hindi:**
1. NestJS JWT: `PassportModule` + `JwtModule.registerAsync()` → `JwtStrategy` token verify करे → `JwtAuthGuard` routes protect करे।
2. `validate()` signature verify के बाद call होता है — return किया object `req.user` बनता है — `@CurrentUser()` से access करो।
3. Refresh token: different secret, DB में hash store, हर use पर rotate, reuse detect करो।

---

## ➡️ Next Topic
**82. Access + Refresh Token Full Implementation** — Complete auth system with rotation, logout, device management।
