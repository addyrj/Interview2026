# 96. TypeORM Basics in NestJS
# हिंदी में: TypeORM — NestJS में Database का ORM

---

## 🔵 Simple Definition (English)
**TypeORM** is a TypeScript ORM (Object-Relational Mapper) that lets you interact with SQL databases (PostgreSQL, MySQL, SQLite) using TypeScript classes and decorators instead of raw SQL. In NestJS, `@nestjs/typeorm` provides DI integration — `@InjectRepository(Entity)` injects a typed repository. TypeORM supports: entities, relations (OneToMany, ManyToMany), migrations, query builder, and transactions.

## 🔵 सरल परिभाषा (Hindi)
**TypeORM** एक TypeScript ORM है जो SQL databases (PostgreSQL, MySQL) को TypeScript classes और decorators से interact करने देता है — raw SQL नहीं। NestJS में `@nestjs/typeorm` DI integration देता है — `@InjectRepository(Entity)` typed repository inject करता है। TypeORM supports: entities, relations, migrations, query builder, transactions।

---

## 🔴 Problem it Solves
```
WITHOUT ORM (raw SQL — maintenance nightmare):
  async getUserWithOrders(userId: string) {
    const result = await db.query(`
      SELECT u.id, u.email, u.name, o.id as order_id, o.amount
      FROM users u
      LEFT JOIN orders o ON o.user_id = u.id
      WHERE u.id = $1 AND u.is_active = true
    `, [userId]);
    
    // Manual mapping:
    const user = { id: result[0].id, email: result[0].email };
    user.orders = result.map(row => ({ id: row.order_id, amount: row.amount }));
    return user;
  }
  
  Problems:
  - Raw SQL strings: no type safety, typos cause runtime errors
  - Manual mapping: tedious, error-prone
  - Database schema changes: update SQL in every query
  - No migration tracking

WITH TYPEORM:
  async getUserWithOrders(userId: string) {
    return this.userRepo.findOne({
      where: { id: userId, isActive: true },
      relations: ['orders'],
    });
  }
  // TypeScript typed, no SQL, automatic mapping!
```

---

## 🟡 Real World Example
**Zomato restaurant management:** Entities: `Restaurant`, `Menu`, `MenuItem`, `Order`, `OrderItem`, `Review`. Relations: Restaurant → many Menus (OneToMany), Menu → many MenuItems, Order → many OrderItems. With TypeORM: define entities once, TypeORM generates SQL, handles JOINs via `relations: ['menu', 'menu.items']`, migrations track schema changes across environments. Repository pattern: `restaurantRepo.find({ where: { city: 'Mumbai', rating: MoreThan(4.0) } })`.

---

## 💻 Code Example — Basic

```typescript
// ─── INSTALLATION ─────────────────────────────────────────────────────────────
// npm install @nestjs/typeorm typeorm pg  (PostgreSQL)
// npm install @nestjs/typeorm typeorm mysql2  (MySQL)

// ─── app.module.ts: TypeORM Setup ────────────────────────────────────────────
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),

    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        host: config.get('DB_HOST'),
        port: config.get<number>('DB_PORT', 5432),
        username: config.get('DB_USER'),
        password: config.get('DB_PASSWORD'),
        database: config.get('DB_NAME'),
        entities: [__dirname + '/**/*.entity.{ts,js}'],  // auto-find entities
        synchronize: config.get('NODE_ENV') !== 'production',  // auto-create tables (dev only!)
        logging: config.get('NODE_ENV') === 'development',
        ssl: config.get('NODE_ENV') === 'production' ? { rejectUnauthorized: false } : false,
      }),
    }),
  ],
})
export class AppModule {}

// ─── USER ENTITY ──────────────────────────────────────────────────────────────
import {
  Entity, PrimaryGeneratedColumn, Column, CreateDateColumn,
  UpdateDateColumn, OneToMany, Index, BeforeInsert,
} from 'typeorm';
import * as bcrypt from 'bcrypt';

@Entity('users')  // table name
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  @Index()  // creates DB index for fast email lookup
  email: string;

  @Column()
  name: string;

  @Column({ name: 'password_hash', select: false })
  // select: false → excluded from SELECT * (won't be in query results by default)
  passwordHash: string;

  @Column({ type: 'enum', enum: ['user', 'admin', 'vendor'], default: 'user' })
  role: string;

  @Column({ name: 'is_active', default: true })
  isActive: boolean;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  // Relations:
  @OneToMany(() => Order, order => order.user)
  orders: Order[];

  // Hook: runs before INSERT
  @BeforeInsert()
  async hashPassword() {
    if (this.passwordHash) {
      this.passwordHash = await bcrypt.hash(this.passwordHash, 12);
    }
  }
}

// ─── ORDER ENTITY ─────────────────────────────────────────────────────────────
import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, OneToMany, JoinColumn } from 'typeorm';

@Entity('orders')
export class Order {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  amount: number;

  @Column({ type: 'enum', enum: ['pending', 'completed', 'cancelled'], default: 'pending' })
  status: string;

  @Column({ name: 'user_id' })
  userId: string;

  @ManyToOne(() => User, user => user.orders)
  @JoinColumn({ name: 'user_id' })
  user: User;

  @OneToMany(() => OrderItem, item => item.order, { cascade: true })
  items: OrderItem[];

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;
}

// ─── USERS MODULE ─────────────────────────────────────────────────────────────
@Module({
  imports: [TypeOrmModule.forFeature([User, Order])],  // register entities
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}

// ─── USERS SERVICE ────────────────────────────────────────────────────────────
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private userRepo: Repository<User>,  // typed Repository<User>
  ) {}

  findAll() {
    return this.userRepo.find();
  }

  async findOne(id: string) {
    const user = await this.userRepo.findOne({ where: { id } });
    if (!user) throw new NotFoundException(`User ${id} not found`);
    return user;
  }

  findWithOrders(id: string) {
    return this.userRepo.findOne({
      where: { id },
      relations: ['orders', 'orders.items'],  // eager load relations
    });
  }

  create(dto: CreateUserDto) {
    const user = this.userRepo.create(dto);  // creates entity instance (no DB)
    return this.userRepo.save(user);         // INSERT/UPDATE
  }

  async update(id: string, dto: UpdateUserDto) {
    const user = await this.findOne(id);
    return this.userRepo.save({ ...user, ...dto });  // UPDATE
  }

  async remove(id: string) {
    const user = await this.findOne(id);
    await this.userRepo.remove(user);  // DELETE
    // OR soft delete:
    // await this.userRepo.softRemove(user);  // sets deletedAt timestamp
  }
}
```

## 💻 Code Example — Advanced

```typescript
// advanced-typeorm.ts — QueryBuilder, transactions, custom repository

import { Injectable } from '@nestjs/common';
import { InjectRepository, InjectDataSource } from '@nestjs/typeorm';
import { Repository, DataSource, Between, MoreThan, Like, In } from 'typeorm';

@Injectable()
export class OrdersService {
  constructor(
    @InjectRepository(Order) private orderRepo: Repository<Order>,
    @InjectRepository(User) private userRepo: Repository<User>,
    @InjectDataSource() private dataSource: DataSource,  // for transactions
  ) {}

  // ─── 1. FIND WITH CONDITIONS ────────────────────────────────────────────────
  async findWithFilters(filters: {
    userId?: string;
    status?: string;
    minAmount?: number;
    dateFrom?: Date;
    dateTo?: Date;
  }) {
    const where: any = {};
    if (filters.userId) where.userId = filters.userId;
    if (filters.status) where.status = filters.status;
    if (filters.minAmount) where.amount = MoreThan(filters.minAmount);
    if (filters.dateFrom && filters.dateTo) {
      where.createdAt = Between(filters.dateFrom, filters.dateTo);
    }

    return this.orderRepo.find({
      where,
      relations: ['user', 'items'],
      order: { createdAt: 'DESC' },
      take: 20,  // LIMIT
      skip: 0,   // OFFSET
    });
  }

  // ─── 2. QUERY BUILDER (complex queries) ─────────────────────────────────────
  async findTopOrders(limit: number) {
    return this.orderRepo
      .createQueryBuilder('order')        // alias 'order'
      .leftJoinAndSelect('order.user', 'user')
      .leftJoinAndSelect('order.items', 'item')
      .where('order.status = :status', { status: 'completed' })
      .andWhere('user.isActive = :active', { active: true })
      .andWhere('order.amount > :minAmount', { minAmount: 500 })
      .orderBy('order.amount', 'DESC')
      .limit(limit)
      .getMany();
  }

  // Aggregate queries:
  async getOrderStats(userId: string) {
    const result = await this.orderRepo
      .createQueryBuilder('order')
      .select('COUNT(order.id)', 'totalOrders')
      .addSelect('SUM(order.amount)', 'totalAmount')
      .addSelect('AVG(order.amount)', 'avgAmount')
      .where('order.userId = :userId', { userId })
      .andWhere('order.status = :status', { status: 'completed' })
      .getRawOne();

    return {
      totalOrders: parseInt(result.totalOrders) || 0,
      totalAmount: parseFloat(result.totalAmount) || 0,
      avgAmount: parseFloat(result.avgAmount) || 0,
    };
  }

  // ─── 3. TRANSACTIONS ─────────────────────────────────────────────────────────
  async placeOrder(userId: string, items: { productId: string; qty: number }[]) {
    return this.dataSource.transaction(async (manager) => {
      // All operations use the same transaction manager
      // Either ALL succeed, or ALL rollback on error

      // Check and lock inventory (SELECT FOR UPDATE)
      for (const item of items) {
        const product = await manager.findOne(Product, {
          where: { id: item.productId },
          lock: { mode: 'pessimistic_write' },  // SELECT FOR UPDATE
        });

        if (!product || product.stock < item.qty) {
          throw new BadRequestException(`Insufficient stock for ${product?.name}`);
          // Error here → transaction rolls back → no partial changes
        }

        await manager.decrement(Product, { id: item.productId }, 'stock', item.qty);
      }

      // Create order
      const order = manager.create(Order, {
        userId,
        status: 'pending',
        amount: await this.calculateTotal(items),
      });
      const savedOrder = await manager.save(order);

      // Create order items
      const orderItems = items.map(item => manager.create(OrderItem, {
        orderId: savedOrder.id,
        productId: item.productId,
        quantity: item.qty,
      }));
      await manager.save(orderItems);

      return savedOrder;
    });
    // If any operation throws → entire transaction rolls back
    // If all succeed → commit
  }

  // ─── 4. PAGINATION HELPER ────────────────────────────────────────────────────
  async findPaginated(page: number, limit: number, userId?: string) {
    const [items, total] = await this.orderRepo.findAndCount({
      where: userId ? { userId } : {},
      order: { createdAt: 'DESC' },
      skip: (page - 1) * limit,
      take: limit,
    });

    return {
      items,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
        hasNextPage: page * limit < total,
      },
    };
  }

  // ─── 5. SOFT DELETE ──────────────────────────────────────────────────────────
  // Entity needs @DeleteDateColumn() deletedAt: Date
  async softDelete(id: string) {
    await this.orderRepo.softDelete(id);  // sets deletedAt, doesn't remove row
  }

  async restore(id: string) {
    await this.orderRepo.restore(id);     // clears deletedAt
  }

  async findWithDeleted() {
    return this.orderRepo.find({ withDeleted: true });  // includes soft-deleted
  }
}
```

---

## 🟠 Express.js vs NestJS Comparison

```typescript
// ─── DATABASE ACCESS COMPARISON ───────────────────────────────────────────────

// EXPRESS with raw TypeORM (manual setup):
const { DataSource } = require('typeorm');
const ds = new DataSource({ ... });
await ds.initialize();
const userRepo = ds.getRepository(User);

// Then in every route:
app.get('/users/:id', async (req, res) => {
  const user = await userRepo.findOne({ where: { id: req.params.id } });
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});

// NESTJS with @nestjs/typeorm:
// 1. DI: @InjectRepository(User) automatically provided
// 2. Lifecycle: TypeORM connection managed by NestJS
// 3. Testing: easy to mock with { provide: getRepositoryToken(User), useValue: mock }
// 4. Transactions: @InjectDataSource() + dataSource.transaction()
// 5. Everything TypeScript with full type safety
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `synchronize: true` in production
```typescript
// WRONG: synchronize auto-alters tables — can delete columns with data!
TypeOrmModule.forRoot({
  synchronize: true,  // ❌ never in production!
});

// CORRECT:
synchronize: process.env.NODE_ENV !== 'production',

// In production: use migrations
// typeorm migration:generate src/migrations/AddUserPhoneColumn
// typeorm migration:run
```

❌ **Mistake 2:** Not using `cascade` on relations
```typescript
// WRONG: Saving user doesn't save orders
const user = userRepo.create({ name: 'Rahul', orders: [...] });
await userRepo.save(user);  // orders NOT saved!

// CORRECT: Enable cascade
@OneToMany(() => Order, order => order.user, { cascade: true })
orders: Order[];
// Now: saving user also saves/updates its orders
```

❌ **Mistake 3:** N+1 problem
```typescript
// WRONG: N+1 queries
const orders = await orderRepo.find();
for (const order of orders) {
  const user = await userRepo.findOne({ where: { id: order.userId } });
  // 1 query for orders + N queries for users = N+1!
}

// CORRECT: Load relations in one query
const orders = await orderRepo.find({
  relations: ['user'],  // JOIN in one query
});
// OR with QueryBuilder:
const orders = await orderRepo
  .createQueryBuilder('order')
  .leftJoinAndSelect('order.user', 'user')
  .getMany();
```

---

## 🧠 Tricky Interview Question

**Q: What is the difference between `save()`, `insert()`, and `update()` in TypeORM?**

**Answer:** 
- `save(entity)`: INSERT if no `id`/primary key, UPDATE if entity has an `id`. Runs entity hooks (`@BeforeInsert`, `@BeforeUpdate`). Loads entity from DB first if updating (to merge). Slower but safe.
- `insert(data)`: Raw INSERT only. No hooks. No load-before-save. Faster for bulk inserts. Throws on duplicate key.
- `update(id, partialEntity)`: Raw UPDATE by id. No hooks. No entity load. Fastest for partial updates. Won't cascade.
- `save()` for most cases (includes hooks, handles upsert). `insert()` + `update()` for performance-critical paths where hooks aren't needed.

---

## ⚫ Interview Questions + Answers

**Q1: What is an ORM and why use TypeORM over raw SQL?**
A1: ORM (Object-Relational Mapper) maps database tables to TypeScript classes. TypeORM benefits: (1) Type safety — TypeScript knows entity shape, IDE autocompletion; (2) No SQL string concatenation — eliminates SQL injection risk; (3) Relations — define `@OneToMany`, `@ManyToOne` and TypeORM handles JOINs; (4) Migrations — track schema changes as code, apply/rollback; (5) Database agnostic — switch from MySQL to PostgreSQL by changing `type` config. Trade-off: complex queries may be harder to express than raw SQL, and generated SQL can be suboptimal (use QueryBuilder for control).

**Q2: What is `TypeOrmModule.forFeature()` used for?**
A2: `TypeOrmModule.forFeature([User, Order])` registers specific entities for the current module and provides their repositories for DI injection. Without `forFeature`, `@InjectRepository(User)` in that module's services would fail. `forRoot()` sets up the global database connection. `forFeature()` scopes specific entity repositories to a module. Each module that needs to work with `User` must import `TypeOrmModule.forFeature([User])` in its imports (unless you use a global repository — less common).

**Q3: How do you handle transactions in NestJS with TypeORM?**
A3: Inject `DataSource` with `@InjectDataSource()`. Use `dataSource.transaction(async manager => {...})` — all operations inside use the same DB transaction. If any operation throws, the entire transaction rolls back. Inside the callback: use `manager.save()`, `manager.findOne()`, etc. (not the regular repository). For pessimistic locking (prevent race conditions): `manager.findOne(Product, { lock: { mode: 'pessimistic_write' } })` → SELECT FOR UPDATE. Essential for: financial transfers, inventory decrement, order placement.

**Q4: What is the N+1 problem and how do you fix it with TypeORM?**
A4: N+1 problem: you fetch N records (1 query), then for each record fetch a related entity (N queries) = N+1 total queries. Example: fetch 100 orders (1 query) + fetch user for each order (100 queries) = 101 queries. TypeORM fix: `relations: ['user']` in `find()` options → generates LEFT JOIN → 1 query total. With QueryBuilder: `.leftJoinAndSelect('order.user', 'user')`. Avoid lazy loading relations in TypeORM (deprecated in v0.3+) — it generates a query per access (N+1). Always eager-load what you need.

**Q5: What is the difference between `@Column({ select: false })` and `@Exclude()`?**
A5: `@Column({ select: false })`: TypeORM-level — column is excluded from all `SELECT *` queries by default. To include it, must explicitly select: `userRepo.findOne({ where: { id }, select: { passwordHash: true, email: true } })`. Good for: sensitive columns you never want accidentally returned. `@Exclude()` from `class-transformer`: serialization-level — the field is in the entity object but excluded when `ClassSerializerInterceptor` serializes the response to JSON. Works for: excluding from API responses while still being able to use the value in business logic. Use both for passwords: `select: false` (no accidental DB fetch) + `@Exclude()` (no accidental JSON response).

---

## 📊 Visual Diagram

```
TYPEORM IN NESTJS:
──────────────────────────────────────────────────────────────────

  AppModule
  ├── TypeOrmModule.forRoot({ type: 'postgres', ... })
  │   Manages: connection pool, migrations
  │
  ├── UsersModule
  │   ├── TypeOrmModule.forFeature([User])
  │   │   └── Provides: Repository<User> for DI
  │   ├── UsersController
  │   └── UsersService
  │       └── @InjectRepository(User) userRepo: Repository<User>
  │
  └── OrdersModule
      ├── TypeOrmModule.forFeature([Order, OrderItem])
      └── OrdersService
          ├── @InjectRepository(Order) orderRepo
          └── @InjectDataSource() dataSource  (for transactions)

ENTITY RELATIONSHIPS:
  User (1) ────────── (*) Order (1) ────── (*) OrderItem
  @OneToMany          @ManyToOne           @ManyToOne
  orders: Order[]     user: User           order: Order
                      items: OrderItem[]   product: Product

QUERY EXAMPLES:
  // Simple find:
  userRepo.findOne({ where: { email }, relations: ['orders'] })
  
  // Complex with QueryBuilder:
  orderRepo.createQueryBuilder('o')
    .leftJoinAndSelect('o.user', 'u')
    .where('o.amount > :amount', { amount: 500 })
    .orderBy('o.createdAt', 'DESC')
    .getMany()

  // Transaction:
  dataSource.transaction(async manager => {
    await manager.save(Order, { ... });
    await manager.decrement(Product, { id }, 'stock', qty);
  })
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Entity | TypeScript class = database table | Class जो DB table represent करे |
| Repository | CRUD methods for an entity | Entity के CRUD methods |
| @InjectRepository | DI inject Repository | Repository को inject करना |
| synchronize | Auto-create tables from entities | Entities से tables auto-create |
| Relations | OneToMany, ManyToOne, etc. | Tables के बीच relationships |
| QueryBuilder | Complex SQL queries with TypeScript | TypeScript से complex SQL |
| Transaction | All-or-nothing DB operations | सब complete हों या कोई नहीं |
| Migration | Versioned schema change scripts | Schema change का version control |
| N+1 problem | N extra queries for N records | N records के लिए N extra queries |
| Cascade | Auto-save/delete related entities | Related entities भी auto-save |

---

## ⚡ 3-Line Summary
**English:**
1. TypeORM in NestJS: `TypeOrmModule.forRoot()` sets up connection, `forFeature([Entity])` in each module registers repositories, `@InjectRepository(Entity)` injects typed repository into services.
2. Key patterns: `find({ where, relations, order, take, skip })` for common queries, `createQueryBuilder()` for complex SQL with JOINs/aggregates, `dataSource.transaction()` for atomic operations.
3. Production must-haves: `synchronize: false` in prod (use migrations), load relations upfront (avoid N+1), `select: false` on sensitive columns.

**Hindi:**
1. NestJS TypeORM: `forRoot()` connection setup, `forFeature([Entity])` module में register, `@InjectRepository()` service में inject।
2. Key patterns: `find({ where, relations })` common queries, `createQueryBuilder()` complex queries, `dataSource.transaction()` atomic operations।
3. Production: `synchronize: false` (migrations use करो), relations eagerly load (N+1 avoid), sensitive columns पर `select: false`।

---

## ➡️ Next Topic
**97. TypeORM Relations** — OneToMany, ManyToMany, eager/lazy loading, cascade।
