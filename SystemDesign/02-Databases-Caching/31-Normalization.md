# 31. Normalization
# हिंदी में: Normalization — डेटा को अलग-अलग टेबल में इस तरह बाँटना कि कोई जानकारी दोहराई न जाए और गड़बड़ी (anomaly) न हो

---

## 🔵 Simple Definition (English)
**Normalization** is the process of organizing a relational schema to **remove duplicate data** and **prevent update anomalies**, by splitting data into related tables so that **each fact is stored in exactly one place**. It's done in stages called **normal forms**: 1NF, 2NF, 3NF (and BCNF).

## 🔵 सरल परिभाषा (Hindi)
Normalization यानी टेबल को ऐसे डिज़ाइन करना कि हर जानकारी सिर्फ़ एक जगह रहे — दोहराव न हो।
इससे एक जगह बदलाव करने पर बाक़ी जगह पुराना डेटा नहीं बचता (anomaly नहीं होती)। इसके चरण हैं 1NF, 2NF, 3NF।

---

## 🔴 Problem it Solves
Imagine one big "orders" spreadsheet table:

```
order_id | customer_name | customer_phone | customer_city | restaurant | restaurant_phone | item1, item2, item3 | prices
101      | Aditya        | 98xxxx         | Mumbai        | Behrouz    | 022-xxx          | Biryani, Raita       | 349, 49
102      | Aditya        | 98xxxx         | Mumbai        | Behrouz    | 022-xxx          | Kebab                | 299
```
Problems (**anomalies**):
- **Update anomaly:** Aditya changes his phone → you must update 500 rows; miss one → inconsistent data.
- **Insert anomaly:** you can't add a new restaurant until someone orders from it.
- **Delete anomaly:** delete the only order of a restaurant → you lose the restaurant's phone number.
- **Wasted space + messy queries:** "items" in comma-separated columns can't be queried or indexed.

Normalization fixes all of these.

## 🔴 यह क्यों बना? (Hindi)
एक ही बड़ी टेबल में ग्राहक का फ़ोन 500 rows में दोहराया गया — बदलना पड़े तो 500 जगह, एक छूटी तो गड़बड़।
नया रेस्टोरेंट तभी जुड़ सकता है जब कोई ऑर्डर हो, और आख़िरी ऑर्डर हटाओ तो रेस्टोरेंट की जानकारी भी ग़ायब। Normalization इन सबको ठीक करता है।

---

## 🟢 How it Works — Step by Step

### 1NF — First Normal Form: atomic values, no repeating groups

```
❌ items = "Biryani, Raita"   (list in one cell)     ❌ item1, item2, item3 columns
✅ one row per item:

order_items
order_id | item     | price
101      | Biryani  | 349
101      | Raita    | 49
102      | Kebab    | 299
Rule: each cell holds ONE value; each row unique (has a primary key).
```

### 2NF — no partial dependency on part of a composite key

```
order_items (PK = order_id + item_id)
order_id | item_id | qty | item_name | item_price     ← item_name depends ONLY on item_id ❌
Fix → move item details to their own table:
menu_items(item_id PK, name, price)
order_items(order_id, item_id, qty)   ← now every non-key column depends on the WHOLE key
```

### 3NF — no transitive dependency (non-key → non-key)

```
orders(order_id PK, customer_id, customer_name, customer_city)
  customer_name depends on customer_id, not on order_id ❌ (order_id → customer_id → name)
Fix:
customers(customer_id PK, name, phone, city)
orders(order_id PK, customer_id FK, restaurant_id FK, status, created_at)

"Every non-key column depends on the key, the whole key, and nothing but the key."
```

### BCNF (bonus)
Every determinant must be a candidate key. A stricter 3NF that matters in rare edge cases.

### Final normalized design

```
customers            restaurants              menu_items
(id, name, phone)    (id, name, phone, city)  (id, restaurant_id FK, name, price)
      │                     │                        │
      │ 1:N                 │ 1:N                    │
      ▼                     ▼                        │
            orders (id, customer_id FK, restaurant_id FK, status, created_at)
                           │ 1:N
                           ▼
            order_items (order_id FK, menu_item_id FK, qty, price_at_order)
                                                        ▲
              snapshot of price at order time — NOT redundancy, it's a different fact
              (menu price can change later; the order's price must not)
```

> 💡 **Important nuance:** `price_at_order` looks like duplication, but it's actually a **historical fact**. Same for the shipping address on an invoice. Normalization is about not duplicating the *same* fact.

### Benefits vs cost
```
✅ No anomalies, smaller storage, one source of truth, easier constraints, flexible queries
❌ More tables → more JOINs for reads → can be slower for read-heavy screens
   → fixed with indexes, caching, or selective denormalization (next topic)
```

## 🟢 कैसे काम करता है? (Hindi)
1. 1NF: हर cell में एक ही value — लिस्ट या item1/item2 columns नहीं; हर row की primary key।
2. 2NF: composite key हो तो हर column पूरी key पर निर्भर हो, आधी पर नहीं — नहीं तो अलग टेबल।
3. 3NF: कोई column किसी दूसरे non-key column पर निर्भर न हो (order → customer → city ग़लत) — ग्राहक की अलग टेबल।
4. नतीजा: customers, restaurants, menu_items, orders, order_items — हर तथ्य एक जगह।
5. ऑर्डर के समय की कीमत (price_at_order) दोहराव नहीं, बल्कि इतिहास का अलग तथ्य है।

---

## 🟡 Real World Example

**Banking / accounting systems** — highly normalized (3NF or more): accounts, customers, transactions and ledger entries are separate. Inconsistent customer data in a bank is a regulatory problem.

**Shopify / e-commerce OLTP** — products, variants, inventory levels, orders, line items and customers are normalized tables. Line items store a **snapshot** of title and price, because product data changes after purchase.

**The "spreadsheet startup" story** — many small businesses start with Google Sheets or one big table. When they grow, duplicate customer data with different phone numbers and addresses causes failed deliveries and wrong invoices, and normalization in a proper DB fixes it.

## 🟡 Real Example Hindi में
बैंकों के सिस्टम पूरी तरह normalized होते हैं — ग्राहक, खाते, लेन-देन सब अलग टेबल में, क्योंकि ग़लत डेटा क़ानूनी समस्या है।
Shopify में order की line item में ख़रीद के समय का नाम और कीमत सेव होती है (snapshot), क्योंकि बाद में product बदल सकता है।

---

## 🟠 My Stack Example

### Normalized Postgres schema (food delivery)
```sql
CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT NOT NULL UNIQUE
);
CREATE TABLE addresses (                         -- 1 customer : N addresses
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  line1 TEXT NOT NULL, city TEXT NOT NULL, pincode TEXT NOT NULL,
  location GEOGRAPHY(Point)
);
CREATE TABLE restaurants (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL);
CREATE TABLE menu_items (
  id BIGSERIAL PRIMARY KEY,
  restaurant_id BIGINT NOT NULL REFERENCES restaurants(id),
  name TEXT NOT NULL, price NUMERIC(10,2) NOT NULL CHECK (price > 0)
);
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(id),
  restaurant_id BIGINT NOT NULL REFERENCES restaurants(id),
  delivery_address JSONB NOT NULL,              -- snapshot (address may be edited/deleted later)
  status TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE order_items (
  order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE,
  menu_item_id BIGINT REFERENCES menu_items(id),
  qty INT NOT NULL CHECK (qty > 0),
  price_at_order NUMERIC(10,2) NOT NULL,        -- historical fact
  PRIMARY KEY (order_id, menu_item_id)
);
CREATE INDEX ON orders (customer_id, created_at DESC);
CREATE INDEX ON order_items (menu_item_id);
CREATE INDEX ON menu_items (restaurant_id);
```

### Many-to-many with a join table (tags / cuisines)
```sql
CREATE TABLE cuisines (id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE restaurant_cuisines (
  restaurant_id BIGINT REFERENCES restaurants(id) ON DELETE CASCADE,
  cuisine_id INT REFERENCES cuisines(id),
  PRIMARY KEY (restaurant_id, cuisine_id)
);
-- vs ❌ restaurants.cuisines = 'Mughlai,Biryani'  (violates 1NF; can't index/rename cleanly)
-- (A Postgres TEXT[] array with GIN index is an acceptable pragmatic alternative for simple tags.)
```

### Prisma model (relations make normalization natural)
```prisma
model Customer  { id BigInt @id @default(autoincrement())  phone String @unique  orders Order[]  addresses Address[] }
model Order     { id BigInt @id @default(autoincrement())  customerId BigInt  customer Customer @relation(fields: [customerId], references: [id])
                  items OrderItem[] }
model OrderItem { orderId BigInt  menuItemId BigInt  qty Int  priceAtOrder Decimal @db.Decimal(10,2)
                  order Order @relation(fields: [orderId], references: [id])  @@id([orderId, menuItemId]) }
```

### MongoDB perspective
Document DBs intentionally **denormalize** (embed). The same anomaly risks apply, so embed only data that's owned by the parent or is a snapshot.

---

## ⚫ Interview Questions + Answers

**Q1: What is normalization and why is it important?**
A1: Organizing a relational schema so each fact is stored once, splitting data into related tables based on functional dependencies. It prevents update, insert and delete anomalies, saves space, enforces integrity through keys and constraints, and keeps a single source of truth, which makes the data correct and easier to evolve.

**Q2: Explain 1NF, 2NF and 3NF with examples.**
A2: 1NF: atomic values and no repeating groups, so one row per order item rather than a comma-separated list. 2NF: 1NF plus no non-key column depending on only part of a composite key, so item_name moves from order_items(order_id, item_id) to a menu_items table. 3NF: 2NF plus no transitive dependencies, so customer_city moves out of orders into customers because it depends on customer_id, not order_id. Summary: depend on the key, the whole key, and nothing but the key.

**Q3: Is storing `price_at_order` in order_items a violation of normalization?**
A3: No. It's a different fact: the price the customer actually paid at that time, which must not change when the menu price changes later. Normalization removes duplication of the same fact. Historical snapshots (prices, addresses, tax rates on invoices) are required for correctness and auditing.

**Q4: What are update, insert and delete anomalies?**
A4: Update: the same data is stored in many rows, so changing it requires updating all of them, and missing one leaves the data inconsistent. Insert: you can't store some data without unrelated data (no restaurant without an order). Delete: deleting a row unintentionally removes other facts (the last order deletes the restaurant's info). Normalized schemas avoid these.

**Q5: When would you NOT fully normalize?**
A5: For read-heavy paths where joins become a bottleneck (feeds, dashboards, search listings), for analytics/OLAP schemas (star schemas are intentionally denormalized), and in NoSQL databases designed around access patterns. Then I denormalize selectively with a clear sync strategy: triggers, events, materialized views or a cache. I keep the normalized OLTP tables as the source of truth.

---

## 🔷 Trade-offs
✅ Advantages:
- Data integrity, no anomalies, less storage, simpler writes, single source of truth.

❌ Disadvantages:
- More joins → slower complex reads at large scale.
- More tables to understand; some queries become verbose.
- Over-normalization (too many tiny tables) hurts both performance and readability.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Normalization | Removing duplication via table design | दोहराव हटाने के लिए टेबल बाँटना |
| Anomaly | Inconsistency from bad design | गड़बड़ी |
| 1NF | Atomic values, no repeating groups | हर cell में एक value |
| 2NF | No partial key dependency | पूरी key पर निर्भरता |
| 3NF | No transitive dependency | सिर्फ़ key पर निर्भरता |
| Functional dependency | A determines B | A से B तय होता है |
| Join table | Table linking many-to-many | कई-से-कई जोड़ने वाली टेबल |
| Snapshot | Copy of data at a point in time | उस समय की copy |

---

## ⚡ 3-Line Summary
**English:**
1. Normalization stores each fact once by splitting data into related tables (1NF → 2NF → 3NF).
2. It prevents update/insert/delete anomalies and keeps integrity; historical snapshots are not violations.
3. Normalize the OLTP source of truth; denormalize selectively for read performance.

**Hindi:**
1. Normalization = हर तथ्य एक जगह, टेबल को 1NF → 2NF → 3NF में बाँटकर।
2. इससे anomalies नहीं होतीं; पुराने समय की कीमत/पता सेव करना ग़लत नहीं।
3. मुख्य DB normalized रखो; तेज़ पढ़ने के लिए सोच-समझकर denormalize करो।

---

## ➡️ Next Topic Suggestion
**32. Denormalization** — Normalized data is correct but needs joins. Next: when and how to intentionally duplicate data for speed (counters, read models, embedded docs) and how to keep the copies in sync.
