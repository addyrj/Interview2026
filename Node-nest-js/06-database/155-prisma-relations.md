# 155. Prisma Relations
# हिंदी में: Prisma Relations — Models के बीच Relationships

---

## 🔵 Simple Definition (English)
**Prisma Relations** connect models together — 1-to-1, 1-to-many, and many-to-many — declared directly in `schema.prisma` using `@relation`. Unlike Sequelize, there's no separate `.hasMany()` call; the relation lives in the schema itself, and querying it uses `include`/`select` plus **nested writes** (create/update/connect related records in a single call).

## 🔵 सरल परिभाषा (Hindi)
**Prisma Relations** models को आपस में जोड़ते हैं — 1-to-1, 1-to-many, many-to-many — `schema.prisma` में `@relation` से directly declared। Sequelize के उलट अलग से `.hasMany()` call नहीं चाहिए; relation schema में ही है, query करने के लिए `include`/`select` और **nested writes** (create/update/connect related records एक ही call में) इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
Without a declarative relation system, inserting a parent AND its children (e.g., an Order with its OrderItems) requires multiple separate queries wrapped manually in a transaction, and fetching related data requires manual joins or multiple round trips. Prisma's nested writes let you create/connect/update an entire object graph in ONE call, and `include`/`select` let you fetch deeply nested related data in ONE typed query — all validated against the schema's declared relations.

## 🔴 यह क्यों बना? (Hindi)
Declarative relation system के बिना, parent + children दोनों insert करने के लिए (जैसे Order + उसके OrderItems) multiple separate queries manually transaction में wrap करनी पड़तीं। Prisma के nested writes से पूरा object graph एक ही call में create/connect/update हो जाता है, और `include`/`select` से deeply nested related data एक typed query में मिल जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **1-to-1**: `Profile.userId` is `@unique` + `@relation`, meaning each User has at most one Profile.
Step 2 → **1-to-many**: the "many" side holds the foreign key field + `@relation`; the "one" side just declares a list field (`posts Post[]`) with no column.
Step 3 → **Many-to-many**: either implicit (Prisma auto-creates a hidden join table — simplest, when no extra columns needed) or explicit (you define the join model yourself, needed when the relation needs extra fields like `quantity`).
Step 4 → **Reading**: use `include: { relationName: true }` or nested `select` to fetch related data in the same query.
Step 5 → **Writing**: use nested `create`, `connect` (link to an existing record by id), `connectOrCreate`, or `disconnect` inside `data` to manage relations atomically.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **1-to-1**: `Profile.userId` `@unique` + `@relation` है — हर User का ज़्यादा से ज़्यादा एक Profile।
Step 2 → **1-to-many**: "many" side FK field + `@relation` रखता है; "one" side सिर्फ list field (`posts Post[]`) declare करता है।
Step 3 → **Many-to-many**: implicit (Prisma hidden join table खुद बनाता है) या explicit (खुद join model define करो, extra columns चाहिए हों तो)।
Step 4 → **Reading**: `include: { relationName: true }` या nested `select` से related data एक query में।
Step 5 → **Writing**: `create`, `connect` (existing record से link), `connectOrCreate`, `disconnect` — nested writes `data` के अंदर।

---

## 🟡 Real World Example
**Amazon India's cart service** models `Cart hasMany CartItems`, each `CartItem belongsTo Product`. When a user checks out, the service runs one nested write: `prisma.order.create({ data: { userId, items: { create: cart.items.map(i => ({ productId: i.productId, quantity: i.quantity })) } }, include: { items: { include: { product: true } } } })` — creating the Order AND all its OrderItems atomically, then immediately returning the full nested object (with product details) in the response, without a second round trip.

## 🟡 Real Example Hindi mein
**Amazon India की cart service** `Cart hasMany CartItems` मॉडल करती है, हर `CartItem` एक `Product` से belong करता है। Checkout पर एक nested write से Order AND उसके सारे OrderItems atomically create होते हैं, फिर पूरा nested object (product details के साथ) एक ही बार में response में मिल जाता है।

---

## 💻 Code Example — Basic

```javascript
// prisma-relations-basic.js
// schema.prisma (for context):
/*
model User {
  id      Int      @id @default(autoincrement())
  email   String   @unique
  profile Profile?                 // 1-to-1 (optional, no column)
  posts   Post[]                    // 1-to-many (no column)
}
model Profile {
  id     Int    @id @default(autoincrement())
  bio    String?
  userId Int    @unique             // FK column, @unique makes it 1-to-1
  user   User   @relation(fields: [userId], references: [id])
}
model Post {
  id       Int    @id @default(autoincrement())
  title    String
  authorId Int
  author   User   @relation(fields: [authorId], references: [id])
}
*/
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  // Nested CREATE: create a User AND its Profile AND two Posts in ONE call
  const user = await prisma.user.create({
    data: {
      email: 'anjali@example.com',
      profile: { create: { bio: 'Loves hiking' } },       // 1-to-1 nested create
      posts: { create: [{ title: 'Hello World' }, { title: 'Second Post' }] }, // 1-to-many
    },
    include: { profile: true, posts: true }, // return everything nested
  });
  console.log(JSON.stringify(user, null, 2));

  await prisma.$disconnect();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// prisma-relations-advanced.js — explicit many-to-many + connect/connectOrCreate
// schema.prisma (for context):
/*
model Order {
  id    Int         @id @default(autoincrement())
  items OrderItem[]
}
model Product {
  id    Int         @id @default(autoincrement())
  name  String
  items OrderItem[]
}
model OrderItem {                       // explicit join model (needed for `quantity`)
  id        Int     @id @default(autoincrement())
  orderId   Int
  order     Order   @relation(fields: [orderId], references: [id])
  productId Int
  product   Product @relation(fields: [productId], references: [id])
  quantity  Int
  @@unique([orderId, productId])
}
*/
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function createOrderWithExistingProducts(userId, cartItems) {
  // cartItems: [{ productId: 1, quantity: 2 }, { productId: 5, quantity: 1 }]
  return prisma.order.create({
    data: {
      userId,
      items: {
        create: cartItems.map((item) => ({
          quantity: item.quantity,
          // "connect" links to an ALREADY EXISTING Product by id — no new Product created
          product: { connect: { id: item.productId } },
        })),
      },
    },
    include: { items: { include: { product: true } } },
  });
}

async function addItemConnectOrCreate(orderId, sku, name, quantity) {
  // connectOrCreate: link to existing Product by sku, or create it if it doesn't exist
  return prisma.orderItem.create({
    data: {
      quantity,
      order: { connect: { id: orderId } },
      product: {
        connectOrCreate: {
          where: { sku },
          create: { sku, name },
        },
      },
    },
  });
}

async function run() {
  try {
    const order = await createOrderWithExistingProducts(1, [
      { productId: 1, quantity: 2 },
      { productId: 2, quantity: 1 },
    ]);
    console.log('Order with connected products:', order);

    // Disconnect example: remove an item's link without deleting the Product
    await prisma.orderItem.deleteMany({ where: { orderId: order.id, productId: 2 } });
    console.log('Removed item, product itself still exists');
  } catch (err) {
    console.error('Relation operation failed:', err.message);
  } finally {
    await prisma.$disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express checkout route using nested writes + nested includes
const express = require('express');
const { PrismaClient } = require('@prisma/client');
const app = express();
app.use(express.json());
const prisma = new PrismaClient();

app.post('/api/checkout', async (req, res) => {
  const { userId, items } = req.body; // items: [{ productId, quantity }]
  try {
    const order = await prisma.order.create({
      data: {
        userId,
        items: { create: items.map((i) => ({ quantity: i.quantity, product: { connect: { id: i.productId } } })) },
      },
      include: { items: { include: { product: true } } },
    });
    res.status(201).json(order); // full nested order returned in one response
  } catch (err) {
    res.status(400).json({ error: 'Checkout failed — check product IDs', detail: err.message });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `create` instead of `connect` for an already-existing related record
```javascript
// Wrong — creates a DUPLICATE Product instead of linking the existing one!
await prisma.orderItem.create({
  data: { quantity: 2, product: { create: { id: existingProductId, name: 'Shoe' } } },
});
// Errors (duplicate id) or creates unwanted duplicate data

// Right — connect to the EXISTING record by its unique field
await prisma.orderItem.create({
  data: { quantity: 2, product: { connect: { id: existingProductId } } },
});
```

❌ Mistake 2: Forgetting `@unique` on the FK field for a 1-to-1 relation
✅ Correct: Without `@unique` on `Profile.userId`, Prisma treats it as a 1-to-many relation (one User could have MANY Profiles), which breaks the intended 1-to-1 semantics and `user.profile` won't work as a single object.

---

## 🧠 Tricky Interview Question

```javascript
const order = await prisma.order.create({
  data: {
    items: { create: [{ productId: 1, quantity: 2 }] },
  },
});
console.log(order.items); // ???
```
Answer: `order.items` is `undefined` — NOT the created items array. By default, `create` returns only the SCALAR fields of the top-level model, never nested relations, even when the nested write succeeded. You must explicitly add `include: { items: true }` (or `select`) to the `create` call to get the nested data back in the response. This is a very common bug: data IS created correctly in the DB, but the returned object looks incomplete.

---

## ⚫ Interview Questions + Answers

Q1: How do you model a 1-to-1 relation in Prisma, and what makes it different from 1-to-many?
A1: A 1-to-1 relation requires the foreign key field to ALSO be marked `@unique` (e.g., `Profile.userId Int @unique`). Without `@unique`, the same schema shape (`User` has `profile Profile?`, `Profile` has `userId` + `@relation`) would represent a 1-to-many relation instead, because nothing prevents multiple Profile rows from pointing to the same userId.

Q2: What's the difference between `connect`, `create`, and `connectOrCreate` in a nested write?
A2: `connect` links to an ALREADY EXISTING related record by a unique identifier — no new row created. `create` makes a BRAND NEW related record and links it. `connectOrCreate` tries to find an existing record matching `where`; if found, links it (connect); if not found, creates a new one with the given `create` data — all atomically in one operation.

Q3: What is the difference between implicit and explicit many-to-many relations?
A3: **Implicit**: both models just declare array fields pointing at each other (e.g., `Post posts Tag[]` and `Tag posts Post[]`), and Prisma auto-creates a hidden join table you never interact with directly — simplest when the relation has NO extra data. **Explicit**: you define the join table as its OWN model (e.g., `OrderItem`) with its own fields (`quantity`), `@relation` to both sides, and you query/write through that model directly — required whenever the relationship itself needs extra attributes.

Q4: How do you prevent the N+1 query problem when fetching nested relations in Prisma?
A4: Use `include` or nested `select` to fetch related data in the SAME query (Prisma internally optimizes this into efficient joins or batched queries), rather than looping over parent records and calling a separate query per record. E.g., `prisma.order.findMany({ include: { items: true } })` fetches all orders AND their items in a controlled number of queries, not one query per order.

Q5: Can you update a relation (e.g., move a Post to a different author) using nested writes?
A5: Yes — using `update` with a nested `connect`/`disconnect`: `prisma.post.update({ where: { id }, data: { author: { connect: { id: newAuthorId } } } })` re-links to a different author. For optional relations, `disconnect: true` removes the link (sets FK to null) without deleting either record.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need atomic creation of a parent + its related children in one call (nested writes)
- You want deeply nested, typed reads without manual joins (`include`)
- The relation needs extra attributes (use explicit join model)

❌ Avoid when:
- The relationship is extremely dynamic/polymorphic (e.g., "comments can belong to a Post OR a Photo OR a Video") — Prisma doesn't natively support polymorphic relations; you'd need separate FK columns or a workaround table

---

## 📊 Visual Diagram
```
PRISMA RELATION TYPES
──────────────────────────────────────────────
1-to-1:    User ◄──────────► Profile
           profile Profile?   userId Int @unique
                               (FK + @unique = 1-to-1)

1-to-many: User ◄──────────── Post[]
           posts Post[]        authorId Int
           (no column)         (FK column, many side)

many-to-many (explicit):
  Order[] ◄── OrderItem ──► Product[]
           { orderId, productId, quantity }
           (extra column needs explicit join model)

NESTED WRITE:
  prisma.order.create({
    data: { items: { create: [...] } }   ◄── atomic, one call
  })
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| @relation | Declares the relation + FK | Relation + FK declare करना |
| connect | Link to existing record | Existing record से link करना |
| connectOrCreate | Link or create if missing | Link या नहीं हो तो create |
| nested write | Create/update related data in one call | एक call में related data create/update |
| implicit m2m | Auto-managed join table | Auto-managed join table |
| explicit m2m | Custom join model with extra fields | Custom join model, extra fields के साथ |
| disconnect | Remove a relation link | Relation link हटाना |

---

## ⚡ 3-Line Summary
English:
1. Prisma relations are declared once in `schema.prisma` via `@relation`, with `include`/`select` for reads and nested writes (`create`, `connect`, `connectOrCreate`) for atomic writes.
2. Use `connect` for existing records and `create` for new ones — mixing them up causes duplicate data or errors.
3. Explicit join models are required only when the many-to-many relation needs extra fields (like `quantity`); otherwise implicit relations are simpler.

Hindi:
1. Prisma relations `schema.prisma` में `@relation` से एक बार declare होते हैं, reads के लिए `include`/`select` और atomic writes के लिए nested writes (`create`, `connect`, `connectOrCreate`)।
2. Existing records के लिए `connect`, नए records के लिए `create` — mix करने से duplicate data या error आता है।
3. Explicit join models सिर्फ तब चाहिए जब many-to-many relation को extra fields (जैसे quantity) चाहिए हों।

---

## ➡️ Next Topic
**156. Prisma vs Sequelize** — Comparing the two ORMs on type safety, migrations, query API, and performance.
