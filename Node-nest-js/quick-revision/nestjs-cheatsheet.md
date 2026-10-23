# NestJS Quick Revision — Top Concepts Cheatsheet

---

## ⚡ Core Architecture

```typescript
// Three building blocks:
// Module → groups code
// Controller → handles HTTP
// Service → business logic

// 1. MODULE
@Module({
  imports: [TypeOrmModule.forFeature([User])],  // external modules
  controllers: [UsersController],                // HTTP handlers
  providers: [UsersService],                     // injectable services
  exports: [UsersService],                       // share with other modules
})
export class UsersModule {}

// 2. CONTROLLER
@Controller('users')  // path prefix
export class UsersController {
  constructor(private usersService: UsersService) {}  // DI injection

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    return this.usersService.findOne(id);  // throws NotFoundException → 404
  }

  @Post()
  @HttpCode(201)
  create(@Body() dto: CreateUserDto) {  // validated by ValidationPipe
    return this.usersService.create(dto);
  }
}

// 3. SERVICE
@Injectable()  // marks for DI container
export class UsersService {
  constructor(@InjectRepository(User) private repo: Repository<User>) {}

  async findOne(id: number) {
    const user = await this.repo.findOne({ where: { id } });
    if (!user) throw new NotFoundException(`User ${id} not found`);
    return user;
  }
}
```

---

## ⚡ Dependency Injection

```typescript
// SINGLETON (default): one instance per module
@Injectable()
class DatabaseService { /* ... */ }

// REQUEST: new instance per HTTP request
@Injectable({ scope: Scope.REQUEST })
class RequestLogger { /* ... */ }

// TRANSIENT: new instance per injection
@Injectable({ scope: Scope.TRANSIENT })
class StatefulHelper { /* ... */ }

// Custom provider patterns:
@Module({
  providers: [
    // Class provider (default):
    UsersService,
    
    // Value provider:
    { provide: 'CONFIG', useValue: { timeout: 5000 } },
    
    // Factory provider (async):
    { provide: 'DB', useFactory: async () => await connectDB() },
    
    // Alias:
    { provide: OldService, useExisting: NewService },
  ],
})

// Inject with custom token:
constructor(@Inject('CONFIG') private config: any) {}
```

---

## ⚡ Request Lifecycle (Order)

```
HTTP Request
  ↓
[Middleware]     → cors, helmet, morgan (Express-style)
  ↓
[Guards]         → canActivate() → auth check
  ↓
[Interceptors]   → before handler (logging, transform request)
  ↓
[Pipes]          → validate/transform params + body
  ↓
[Controller]     → route handler method
  ↓
[Service]        → business logic
  ↓
[Interceptors]   → after handler (transform response)
  ↓
[ExceptionFilters] → catch any thrown exceptions
  ↓
HTTP Response
```

---

## ⚡ ValidationPipe + DTOs

```typescript
// main.ts: global setup
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,              // strip unknown fields (prevents mass assignment)
  forbidNonWhitelisted: true,   // throw on unknown fields
  transform: true,              // auto-convert to DTO class instances
}));

// DTO with class-validator:
export class CreateUserDto {
  @IsString() @MinLength(2) name: string;
  @IsEmail() email: string;
  @IsString() @MinLength(8) password: string;
  @IsOptional() @IsString() phone?: string;
}

// Nested objects:
export class CreateOrderDto {
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)  // ← REQUIRED for nested validation
  items: OrderItemDto[];
}

// ParseIntPipe for route params:
@Get(':id')
findOne(@Param('id', ParseIntPipe) id: number) { }
// GET /users/abc → 400 Bad Request (not a number)
// GET /users/5 → id = 5 (as number)
```

---

## ⚡ Guards + RBAC

```typescript
// Custom @Roles() decorator:
export const Roles = (...roles: string[]) => SetMetadata('roles', roles);
export const Public = () => SetMetadata('isPublic', true);

// JwtAuthGuard:
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) { super(); }
  
  canActivate(context: ExecutionContext) {
    const isPublic = this.reflector.getAllAndOverride<boolean>('isPublic', [
      context.getHandler(), context.getClass(),
    ]);
    if (isPublic) return true;
    return super.canActivate(context);
  }
}

// RolesGuard:
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  
  canActivate(ctx: ExecutionContext): boolean {
    const required = this.reflector.getAllAndOverride<string[]>('roles', [
      ctx.getHandler(), ctx.getClass(),
    ]);
    if (!required) return true;
    const { user } = ctx.switchToHttp().getRequest();
    return required.some(r => user.roles?.includes(r));
  }
}

// Usage:
@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)  // ← order matters: JWT first!
export class AdminController {
  @Get('users') @Roles('admin') getUsers() {}
  @Get('public') @Public() getPublic() {}  // ← skips JWT check
}
```

---

## ⚡ JWT + Passport Auth

```typescript
// auth.module.ts:
JwtModule.registerAsync({
  imports: [ConfigModule],
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    secret: config.get('JWT_SECRET'),
    signOptions: { expiresIn: '15m' },
  }),
})

// jwt.strategy.ts:
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy, 'jwt') {
  constructor(private config: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.get('JWT_SECRET'),
    });
  }

  async validate(payload: any) {
    return { userId: payload.userId, email: payload.email, role: payload.role };
    // ↑ becomes req.user
  }
}

// @CurrentUser() custom decorator:
export const CurrentUser = createParamDecorator(
  (data: string | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    return data ? request.user?.[data] : request.user;
  },
);

// Usage: @CurrentUser() user, @CurrentUser('email') email
```

---

## ⚡ TypeORM Patterns

```typescript
// Entity:
@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid') id: string;
  @Column({ unique: true }) email: string;
  @Column() name: string;
  @CreateDateColumn() createdAt: Date;

  @OneToMany(() => Order, order => order.user)
  orders: Order[];
}

// Service patterns:
async findWithRelations(id: string) {
  return this.userRepo.findOne({
    where: { id },
    relations: ['orders', 'orders.items'],  // eager load
  });
}

async findWithQueryBuilder(email: string) {
  return this.userRepo.createQueryBuilder('user')
    .leftJoinAndSelect('user.orders', 'order')
    .where('user.email = :email', { email })
    .andWhere('order.status = :status', { status: 'active' })
    .getMany();
}

// Transaction:
async transfer(fromId: string, toId: string, amount: number) {
  return this.dataSource.transaction(async (manager) => {
    await manager.decrement(Account, { id: fromId }, 'balance', amount);
    await manager.increment(Account, { id: toId }, 'balance', amount);
  });
}
```

---

## ⚡ Common Tricky Questions

```typescript
// Q1: What is the difference between @Module imports and providers?
// providers: classes that live IN this module (injectable within module)
// imports: other modules whose exports become available in this module
// exports: make this module's providers available to importers

// Q2: What causes "Nest can't resolve dependencies" error?
// 1. Missing @Injectable() on the class
// 2. Not listed in module's providers
// 3. Not exported from the module that owns it
// 4. Circular dependency (use forwardRef())

// Q3: What is the ExecutionContext?
// Wraps request context, supports multiple transports:
// context.switchToHttp().getRequest()  → Express request
// context.switchToWs().getData()       → WebSocket data
// context.switchToRpc().getData()      → Microservice data
// context.getHandler()                 → decorated method
// context.getClass()                   → controller class

// Q4: Exception response codes:
// NotFoundException (404), BadRequestException (400)
// UnauthorizedException (401), ForbiddenException (403)
// ConflictException (409), InternalServerErrorException (500)

// Q5: Test a NestJS service:
const module = await Test.createTestingModule({
  providers: [
    UsersService,
    { provide: getRepositoryToken(User), useValue: { findOne: jest.fn() } },
  ],
}).compile();
const service = module.get<UsersService>(UsersService);
```

---

## ⚡ NestJS CLI Commands

```bash
# Generate boilerplate:
nest g module users          # creates users.module.ts
nest g controller users      # creates users.controller.ts + spec
nest g service users         # creates users.service.ts + spec
nest g resource users        # creates CRUD module+controller+service+dto+entity

# Full resource creates:
# users.module.ts
# users.controller.ts (with CRUD methods + Swagger decorators)
# users.service.ts
# entities/user.entity.ts
# dto/create-user.dto.ts
# dto/update-user.dto.ts

# Other:
nest g guard auth/jwt-auth    # creates guards/jwt-auth.guard.ts
nest g interceptor logging    # creates logging.interceptor.ts
nest g pipe validation        # creates validation.pipe.ts
nest g filter http-exception  # creates http-exception.filter.ts
```

---

## ⚡ NestJS Production Checklist

```
Security:
  ✅ helmet() in main.ts
  ✅ CORS with origin whitelist
  ✅ Rate limiting (ThrottlerModule)
  ✅ ValidationPipe global (whitelist + forbidNonWhitelisted)
  ✅ JWT guards on all protected routes
  ✅ RBAC with RolesGuard
  ✅ Passwords with bcrypt(12)

Performance:
  ✅ ConfigModule.forRoot({ cache: true })
  ✅ CacheModule (Redis) for frequent reads
  ✅ TypeORM connection pooling
  ✅ Exclude sensitive fields from responses (@Exclude())

Reliability:
  ✅ app.enableShutdownHooks() — graceful shutdown
  ✅ Global exception filter — consistent error responses
  ✅ Health check with @nestjs/terminus (/health)
  ✅ Request ID for log tracing
  ✅ Structured logging (Winston/Pino)
```
