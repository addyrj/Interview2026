# Node.js + NestJS Interview Guide
# 3-5 Year Experience Level
# 600 Topics Total (300 Node.js + 300 NestJS)

---

## 📁 Node.js Guide

| Folder | Topics | Count |
|--------|--------|-------|
| 01-basics/ | What is Node, V8, Non-blocking I/O, Event Loop, npm, CommonJS, ES Modules, process, dotenv | 01-30 |
| 02-core-modules/ | fs, path, os, http, crypto, EventEmitter, Streams, Buffer, child_process, cluster, worker_threads | 31-65 |
| 03-event-loop/ | Event Loop Phases, Timers, Poll, Check, nextTick, Promises, setImmediate, Blocking | 66-83 |
| 04-express/ | Express server, Middleware, Routes, Validation, Error handling, CORS, Rate limiting, Multer | 84-115 |
| 05-auth-security/ | JWT, bcrypt, Passport, OAuth, RBAC, CSRF, XSS, SQL injection, OWASP Top 10 | 116-142 |
| 06-database/ | MySQL, Sequelize, Prisma, PostgreSQL, MongoDB, Mongoose, Redis, Transactions | 143-172 |
| 07-api-design/ | REST, Pagination, GraphQL, WebSocket, Socket.io, SSE, Swagger | 173-194 |
| 08-async-patterns/ | Callbacks, Promises, async/await, Worker Threads, Cluster, PM2 | 195-207 |
| 09-testing/ | Jest, Supertest, Mocking, TDD, E2E | 208-215 |
| 10-performance/ | Memory leaks, Caching, N+1, Connection pooling, Load balancing | 216-230 |
| 11-microservices/ | Microservices, RabbitMQ, Kafka, BullMQ, Docker, Logging, Monitoring | 231-257 |
| 12-deployment/ | VPS, Nginx, PM2, AWS EC2, Lambda, GitHub Actions | 258-272 |
| 13-interview-problems/ | REST API, Auth, Socket.io chat, Rate limiter, Caching, OTP | 273-300 |
| quick-revision/ | Cheatsheets, Top 50 Q&A, Event Loop, Tricky Output Questions | — |

---

## 📁 NestJS Guide (nestjs/ subfolder)

| Folder | Topics | Count |
|--------|--------|-------|
| nestjs/01-basics/ | What is NestJS, Decorators, Project structure, Bootstrap, CLI | 01-20 |
| nestjs/02-core-blocks/ | Modules, Controllers, Providers, Services, DI, Provider Scopes | 21-46 |
| nestjs/03-middleware-pipes-guards/ | Middleware, Pipes, DTOs, Guards, Interceptors, Exception Filters | 47-76 |
| nestjs/04-authentication/ | Passport, JWT Module, Access+Refresh Token, RBAC, OAuth | 77-94 |
| nestjs/05-database/ | TypeORM, TypeORM Relations, Migrations, Prisma, Mongoose, Multiple DBs | 95-118 |
| nestjs/06-advanced-features/ | Config Module, Caching, File Upload, Rate Limiting, Swagger, Health, Cron, WebSockets | 119-150 |
| nestjs/07-microservices/ | @nestjs/microservices, Transport layers, RabbitMQ, Kafka, gRPC | 151-170 |
| nestjs/08-queues/ | Bull, BullMQ, Queue Processors, Job lifecycle, Retry | 171-181 |
| nestjs/09-testing/ | Unit testing, Test.createTestingModule, Mocking, E2E, Supertest | 182-193 |
| nestjs/10-graphql/ | Code First, Resolvers, DataLoader, Apollo Federation | 194-205 |
| nestjs/11-performance-production/ | Performance, Logging, Distributed Tracing, Graceful Shutdown | 206-225 |
| nestjs/12-deployment/ | Docker, Multi-stage build, AWS, PM2, GitHub Actions | 226-240 |
| nestjs/13-design-patterns/ | Repository, CQRS, Event Sourcing, Clean Architecture, DDD | 241-255 |
| nestjs/14-interview-problems/ | Auth System, CRUD APIs, WebSocket chat, BullMQ jobs, complete apps | 256-300 |
| nestjs/quick-revision/ | Cheatsheets, Top 50 Q&A, DI/Decorator tricky questions | — |

---

## ⭐ Most Important Topics (Interview Priority)

### Node.js
1. **Event Loop** (66-83) — most-asked at 3-5 YOE level
2. **Non-blocking I/O** (07) — foundational concept
3. **Streams** (47-53) — senior-level topic
4. **JWT + bcrypt** (117-121) — every backend interview
5. **Middleware** (91-95) — Express core
6. **Connection pooling** (145) — production knowledge
7. **N+1 problem** (222) — database interview
8. **PM2 + Cluster** (206, 226-227) — deployment

### NestJS
1. **Dependency Injection** (38-40) — NestJS foundation
2. **Pipes + DTOs + class-validator** (51-57) — validation pattern
3. **Guards + JWT** (59-62, 84) — auth flow
4. **Interceptors** (66-70) — transform responses
5. **TypeORM + Prisma** (96-109) — database
6. **Microservices + BullMQ** (151-170, 171-181) — advanced
7. **CQRS + Clean Architecture** (247, 250) — senior interviews

---

## 🚀 Format Notes

**Node.js files:** JavaScript code, `## 🟠 Express.js Integration` section
**NestJS files:** TypeScript code, `## 🟠 Express.js vs NestJS Comparison` section
**Both:** English + Hindi sections, 5 Q&As, visual diagram, 3-line summary

**Real examples used:** Zomato, Swiggy, Razorpay, Paytm, PhonePe, Amazon, Flipkart, Meesho
