# 149. Sequelize Associations
# हिंदी में: Sequelize Associations — Models के बीच Relationships

---

## 🔵 Simple Definition (English)
**Sequelize Associations** define relationships between database tables (models) — like `hasOne`, `hasMany`, `belongsTo`, and `belongsToMany`. They let you fetch related data together (e.g., a User with all their Orders) without writing raw JOIN SQL — Sequelize generates it for you.

## 🔵 सरल परिभाषा (Hindi)
**Sequelize Associations** database tables (models) के बीच relationship define करते हैं — `hasOne`, `hasMany`, `belongsTo`, `belongsToMany`। इनसे related data एक साथ fetch कर सकते हो (जैसे User के साथ उसके सारे Orders) बिना raw JOIN SQL लिखे — Sequelize खुद generate करता है।

---

## 🔴 Problem it Solves
Without associations, fetching a user's orders means writing manual SQL joins or multiple queries and manually stitching data together:
```sql
SELECT * FROM users WHERE id = 1;
SELECT * FROM orders WHERE user_id = 1;
-- then manually combine in JS
```
This is error-prone, repeats boilerplate everywhere, and doesn't handle eager/lazy loading, cascading deletes, or foreign key constraints automatically. Associations give a declarative way to say "User hasMany Orders" once, and Sequelize handles the SQL generation, foreign keys, and `include` (eager loading) everywhere.

## 🔴 यह क्यों बना? (Hindi)
Associations के बिना, user के orders fetch करने के लिए manual SQL joins या multiple queries लिखनी पड़ती और data को manually combine करना पड़ता। यह error-prone है और हर जगह boilerplate repeat होता। Associations से एक बार "User hasMany Orders" define करो, Sequelize baaki सब (foreign keys, SQL joins, eager loading) खुद handle करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define two models (e.g., `User`, `Order`) with `sequelize.define()` or class-based models.
Step 2 → Call association method on the model: `User.hasMany(Order)`, `Order.belongsTo(User)`.
Step 3 → Sequelize automatically adds a foreign key column (`userId`) to the `Order` table's migration/schema.
Step 4 → Use `include` option in `findAll`/`findOne` to eager-load related data: `User.findAll({ include: Order })`.
Step 5 → For many-to-many, Sequelize creates a junction table automatically (or you specify `through`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → दो models define करो (`User`, `Order`)।
Step 2 → Model पर association method call करो: `User.hasMany(Order)`, `Order.belongsTo(User)`।
Step 3 → Sequelize automatically foreign key column (`userId`) `Order` table में add कर देता है।
Step 4 → `include` option से related data eager-load करो: `User.findAll({ include: Order })`।
Step 5 → Many-to-many के लिए Sequelize junction table खुद बनाता है (या `through` से specify करो)।

---

## 🟡 Real World Example
**Swiggy's order system:** A `Restaurant` hasMany `MenuItems`. A `User` hasMany `Orders`, and each `Order` belongsTo a `User` and belongsTo a `Restaurant`. An `Order` also hasMany `OrderItems` (belongsToMany `MenuItem` through `OrderItems`). When a customer opens "My Orders", Swiggy's backend runs one query with nested `include`: `Order.findAll({ where: { userId }, include: [Restaurant, { model: OrderItem, include: MenuItem }] })` — returns the full order with restaurant name and item details in a single round trip.

## 🟡 Real Example Hindi mein
**Swiggy का order system:** एक `Restaurant` के many `MenuItems` होते हैं। एक `User` के many `Orders`, हर `Order` एक `User` और एक `Restaurant` से belong करता है। Customer "My Orders" खोलता है तो backend nested `include` के साथ एक query चलाता है — पूरा order, restaurant name और items एक ही बार में मिल जाते हैं।

---

## 💻 Code Example — Basic

```javascript
// sequelize-associations-basic.js
// npm install sequelize sqlite3
const { Sequelize, DataTypes } = require('sequelize');

// In-memory sqlite DB for a runnable demo
const sequelize = new Sequelize('sqlite::memory:', { logging: false });

// Define User model
const User = sequelize.define('User', {
  name: { type: DataTypes.STRING, allowNull: false },
  email: { type: DataTypes.STRING, unique: true },
});

// Define Order model
const Order = sequelize.define('Order', {
  amount: { type: DataTypes.FLOAT, allowNull: false },
  status: { type: DataTypes.STRING, defaultValue: 'pending' },
});

// 1-to-many: a User hasMany Orders, Order belongsTo a User
User.hasMany(Order, { foreignKey: 'userId' }); // adds Order.userId
Order.belongsTo(User, { foreignKey: 'userId' });

async function main() {
  // Sync models to DB (creates tables) — dev only, use migrations in prod
  await sequelize.sync({ force: true });

  // Create a user
  const user = await User.create({ name: 'Rahul', email: 'rahul@example.com' });

  // Create orders linked to the user
  await Order.create({ amount: 450, userId: user.id });
  await Order.create({ amount: 899, userId: user.id });

  // Eager load: fetch user WITH all their orders in one query
  const userWithOrders = await User.findOne({
    where: { id: user.id },
    include: Order, // JOIN happens here
  });

  console.log(JSON.stringify(userWithOrders, null, 2));
  await sequelize.close();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// sequelize-associations-advanced.js
// Production pattern: many-to-many with a junction table + custom attributes
const { Sequelize, DataTypes, Model } = require('sequelize');
const sequelize = new Sequelize('sqlite::memory:', { logging: false });

class Restaurant extends Model {}
Restaurant.init({ name: DataTypes.STRING }, { sequelize, modelName: 'restaurant' });

class MenuItem extends Model {}
MenuItem.init({ title: DataTypes.STRING, price: DataTypes.FLOAT }, { sequelize, modelName: 'menuItem' });

class Order extends Model {}
Order.init({ status: { type: DataTypes.STRING, defaultValue: 'placed' } }, { sequelize, modelName: 'order' });

// Junction model with extra columns (quantity) — belongsToMany "through"
class OrderItem extends Model {}
OrderItem.init({ quantity: { type: DataTypes.INTEGER, defaultValue: 1 } }, { sequelize, modelName: 'orderItem' });

// 1-to-many: Restaurant hasMany MenuItems
Restaurant.hasMany(MenuItem, { foreignKey: 'restaurantId', onDelete: 'CASCADE' });
MenuItem.belongsTo(Restaurant);

// Order belongs to Restaurant
Order.belongsTo(Restaurant);
Restaurant.hasMany(Order);

// Many-to-many: Order <-> MenuItem through OrderItem (with quantity)
Order.belongsToMany(MenuItem, { through: OrderItem, foreignKey: 'orderId' });
MenuItem.belongsToMany(Order, { through: OrderItem, foreignKey: 'menuItemId' });

async function run() {
  try {
    await sequelize.sync({ force: true });

    const restaurant = await Restaurant.create({ name: 'Punjabi Dhaba' });
    const paneer = await MenuItem.create({ title: 'Paneer Tikka', price: 220, restaurantId: restaurant.id });
    const naan = await MenuItem.create({ title: 'Butter Naan', price: 50, restaurantId: restaurant.id });

    const order = await Order.create({ restaurantId: restaurant.id });

    // Add items to order with extra "through" attributes (quantity)
    await order.addMenuItem(paneer, { through: { quantity: 2 } });
    await order.addMenuItem(naan, { through: { quantity: 4 } });

    // Eager load deeply: order -> restaurant + menuItems (+ junction data)
    const fullOrder = await Order.findOne({
      where: { id: order.id },
      include: [
        Restaurant,
        { model: MenuItem, through: { attributes: ['quantity'] } },
      ],
    });

    console.log(JSON.stringify(fullOrder, null, 2));

    // Cascading delete check: deleting restaurant removes its menu items
    await restaurant.destroy();
    const remaining = await MenuItem.count();
    console.log('Menu items remaining after restaurant delete:', remaining); // 0

    await sequelize.close();
  } catch (err) {
    console.error('Association error:', err.message);
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express route using Sequelize associations for a single, efficient query
const express = require('express');
const app = express();
// assume User, Order, Restaurant models + associations are set up (as above)

app.get('/api/users/:id/orders', async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id, {
      include: [{
        model: Order,
        include: [Restaurant], // nested eager load: order's restaurant too
      }],
    });

    if (!user) return res.status(404).json({ error: 'User not found' });

    res.json({ user: user.name, orders: user.Orders });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch orders' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to define the inverse association, causing `include` to fail
```javascript
// Wrong — only one direction defined
User.hasMany(Order);
// Order.belongsTo(User) is missing!
// Order.findOne({ include: User }) → throws "Order is not associated to User"

// Right — define both directions
User.hasMany(Order, { foreignKey: 'userId' });
Order.belongsTo(User, { foreignKey: 'userId' });
```

❌ Mistake 2: Using `sequelize.sync({ force: true })` in production
✅ Correct: Use migrations (`sequelize-cli db:migrate`) in production — `sync({ force: true })` **drops and recreates tables**, destroying data. Only use `sync` in local dev/tests.

---

## 🧠 Tricky Interview Question

```javascript
// What happens here?
User.hasMany(Order, { as: 'orders', foreignKey: 'userId' });
Order.belongsTo(User, { foreignKey: 'userId' });

const user = await User.findOne({ include: Order }); // no alias given
```
Answer: This throws an error — `"Order is associated to User using an alias. You must use the 'as' keyword to include the correct association"`. Because `hasMany` was defined with `as: 'orders'`, Sequelize expects `include: { model: Order, as: 'orders' }` (or `include: 'orders'`), not the bare model. Aliases must match exactly between the association definition and every `include` call that uses it.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `hasOne` and `belongsTo`?
A1: Both represent a 1-to-1 relationship but differ in where the foreign key lives. `hasOne` means the OTHER model holds the foreign key (e.g., `User.hasOne(Profile)` → `Profile` table gets `userId`). `belongsTo` means THIS model holds the foreign key (e.g., `Profile.belongsTo(User)` → `Profile` table gets `userId`). They're usually used together on the two sides of the same relationship.

Q2: How does `belongsToMany` work and what is `through`?
A2: `belongsToMany` creates a many-to-many relationship using a junction/pivot table, specified via `through`. E.g., `Order.belongsToMany(MenuItem, { through: OrderItem })` creates an `OrderItem` table with `orderId` and `menuItemId` columns. You can add extra columns to the junction table (like `quantity`) by defining `through` as a full model instead of a string name.

Q3: What is eager loading vs lazy loading in Sequelize?
A3: Eager loading fetches associated data in the SAME query using `include` — e.g., `User.findAll({ include: Order })` generates a single SQL JOIN. Lazy loading fetches associated data in a SEPARATE query, triggered on demand — e.g., `const orders = await user.getOrders()`. Eager loading is more efficient for known use cases (avoids N+1 queries); lazy loading is simpler when you don't always need the related data.

Q4: What does the N+1 query problem mean, and how do associations help avoid it?
A4: N+1 happens when you fetch N parent records, then run 1 additional query PER record to get related data (e.g., fetch 100 users, then loop and run `user.getOrders()` 100 times = 101 queries). Using eager loading with `include` fixes this: `User.findAll({ include: Order })` generates ONE query with a JOIN (or Sequelize batches sub-queries efficiently), avoiding 100 extra round trips.

Q5: How do you handle cascading deletes with associations?
A5: Pass `onDelete: 'CASCADE'` in the association options: `Restaurant.hasMany(MenuItem, { onDelete: 'CASCADE' })`. This tells the DB (via the foreign key constraint) to automatically delete child rows (MenuItems) when the parent (Restaurant) is deleted. Other options: `'SET NULL'` (sets FK to null instead of deleting child) and `'RESTRICT'` (blocks the delete if children exist).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your data has clear relational structure (users-orders, posts-comments, restaurants-menus)
- You need to fetch related data together frequently (avoid N+1 queries)
- You're using a relational DB (PostgreSQL, MySQL) with Sequelize as the ORM

❌ Avoid when:
- Data is deeply nested/hierarchical and better suited to a document DB (use MongoDB/Mongoose instead)
- You need extreme query performance control — sometimes raw SQL or query builders (Knex) are better for complex reporting queries

---

## 📊 Visual Diagram
```
SEQUELIZE ASSOCIATIONS
──────────────────────────────────────────────
User (1) ──hasMany──────────▶ Order (N)
  ▲                               │
  └──────belongsTo────────────────┘
  (Order table has userId FK)

Order (N) ──belongsToMany──▶ MenuItem (N)
              │  (through: OrderItem)
              ▼
     OrderItem { orderId, menuItemId, quantity }

EAGER LOAD QUERY:
  User.findAll({ include: Order })
       │
       ▼
  SELECT * FROM users
  LEFT JOIN orders ON orders.userId = users.id
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| hasMany | One record owns many related records | एक record के कई related records |
| belongsTo | This model holds the foreign key | इस model में foreign key है |
| belongsToMany | Many-to-many via junction table | Junction table से many-to-many |
| through | Junction table model name | Junction table का model |
| include | Eager-load related data in query | Query में related data load करना |
| foreignKey | Column linking two tables | दो tables को जोड़ने वाला column |
| N+1 problem | Too many separate queries | बहुत ज़्यादा अलग queries |
| CASCADE | Auto-delete children on parent delete | Parent delete होने पर children भी delete |

---

## ⚡ 3-Line Summary
English:
1. Sequelize associations (`hasOne`, `hasMany`, `belongsTo`, `belongsToMany`) declare relationships between models without manual SQL JOINs.
2. `include` enables eager loading — fetching related data in one query, avoiding the N+1 query problem.
3. Many-to-many relations use a `through` junction table, which can hold extra columns like `quantity`.

Hindi:
1. Sequelize associations models के बीच relationship बिना manual SQL JOIN के declare करते हैं।
2. `include` से eager loading होती है — एक query में related data, N+1 problem से बचाव।
3. Many-to-many relations `through` junction table use करते हैं, जिसमें extra columns (जैसे quantity) रख सकते हैं।

---

## ➡️ Next Topic
**150. Sequelize Hooks** — Model lifecycle events (`beforeCreate`, `afterUpdate`) for automatic side effects like password hashing or auditing.
