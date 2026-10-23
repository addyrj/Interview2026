---

# 026. SQL Injection — Complete Guide
# हिंदी में: SQL Injection — Database पर सबसे खतरनाक Attack
# Risk Level: ⛔ Critical

---

## 🔵 Simple Definition (English)
SQL Injection (SQLi) is an attack where malicious SQL code is inserted into an application's query. Instead of treating user input as data, the database executes it as SQL code — giving the attacker the ability to read, modify, or delete any data in the database, and sometimes execute OS commands.

## 🔵 सरल परिभाषा (Hindi)
SQL Injection में attacker application के database query में malicious SQL code insert करता है। Database user input को data की जगह SQL command समझ लेता है — जिससे attacker कोई भी data पढ़ सकता है, modify कर सकता है, या पूरा database delete कर सकता है।

---

## ⚠️ The Attack / Threat

```
Attack Flow:
─────────────────────────────────────────────────────────
User Input    → "' OR '1'='1"
                      ↓
App builds    → SELECT * FROM users WHERE username='' OR '1'='1'
                      ↓
DB executes   → Returns ALL users (condition is always true!)
                      ↓
Attacker gets → Entire users table (passwords, emails, PII)
```

**Classic Attack Vectors:**
```
Login bypass:      username: admin'--
                   password: anything
                   Query: SELECT * FROM users WHERE username='admin'--' AND password='...'
                   Result: logs in as admin (-- comments out password check!)

Data extraction:   ' UNION SELECT username, password FROM users--
Drop table:        '; DROP TABLE users;--
Read files:        ' UNION SELECT LOAD_FILE('/etc/passwd')--
```

## ⚠️ हमला कैसे होता है? (Hindi)
Attacker login form में `admin'--` type करता है। App query बनाती है: `SELECT * FROM users WHERE username='admin'--'`. `--` के बाद सब comment हो जाता है — password check skip! Attacker admin बन जाता है बिना password के।

---

## 💀 Real World Breach Example
**Yahoo (2012):** 450,000 user credentials stolen via SQL injection in Yahoo Voices API. Passwords stored in plaintext. Attackers used UNION-based injection to extract entire user table. Damage: massive public exposure, reputation loss, $35 million fine.

**Heartland Payment Systems (2008):** SQL injection on web application → attacker planted malware → 130 million credit card numbers stolen. Cost: $140 million in fines and settlements. Was the largest credit card breach at the time.

---

## 🛡️ How to Prevent — Step by Step

```
Step 1: NEVER concatenate user input into SQL strings
Step 2: Always use Parameterized Queries / Prepared Statements
Step 3: Use an ORM (Sequelize, TypeORM, Prisma) which parameterizes by default
Step 4: Apply Principle of Least Privilege — DB user should have minimum permissions
Step 5: Validate and sanitize ALL input (whitelist, type check, length check)
Step 6: Enable WAF (Web Application Firewall) to detect SQLi patterns
Step 7: Use stored procedures (with parameterization)
Step 8: Error handling — never expose DB errors to user
Step 9: Regular security scanning (SQLMap, OWASP ZAP)
Step 10: Defense in depth — encryption at rest so stolen data is useless
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE CODE — NEVER DO THIS

// Express.js login — STRING CONCATENATION
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  // ❌ CRITICAL VULNERABILITY: user input directly in query string!
  const query = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;
  
  // Attacker input: username = "admin'--"
  // Resulting query: SELECT * FROM users WHERE username='admin'--' AND password='...'
  // '--' comments out rest — password check skipped! Logs in as admin!
  
  const [rows] = await db.query(query);  // executes malicious query
  
  if (rows.length > 0) {
    res.json({ success: true, user: rows[0] });  // ❌ also exposes user object!
  }
});

// ❌ Another vulnerable pattern — dynamic filter building
app.get('/users', async (req, res) => {
  const { sort } = req.query;
  
  // Attacker: sort = "name; DROP TABLE users;--"
  const query = `SELECT * FROM users ORDER BY ${sort}`;  // ❌ no parameterization possible for ORDER BY!
  const [rows] = await db.query(query);
  res.json(rows);
});
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE CODE — USE THIS IN PRODUCTION

// ─── FIX 1: Parameterized Queries (mysql2) ────────────────────
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  // ✅ Validate input first
  if (!username || typeof username !== 'string' || username.length > 50) {
    return res.status(400).json({ error: 'Invalid input' });
  }
  
  // ✅ Parameterized query — ? placeholders, values passed separately
  // DB treats values as DATA, not SQL code — injection impossible!
  const query = 'SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?';
  
  const hashedPwd = await bcrypt.hash(password, 10);  // hash before comparing
  const [rows] = await db.execute(query, [username, hashedPwd]);  // ✅ safe!
  
  if (rows.length === 0) {
    // ✅ Generic error — don't reveal whether username or password was wrong
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  // ✅ Only return what's needed — never expose sensitive fields
  const { id, role } = rows[0];
  const token = generateJWT({ id, username: rows[0].username, role });
  res.json({ token });
});

// ─── FIX 2: Using TypeORM (NestJS) — safe by default ─────────
@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepo: Repository<User>
  ) {}
  
  async findUser(username: string): Promise<User | null> {
    // ✅ TypeORM parameterizes automatically
    return this.userRepo.findOne({ where: { username } });
    
    // ✅ QueryBuilder also safe:
    return this.userRepo
      .createQueryBuilder('user')
      .where('user.username = :username', { username })  // ✅ named param
      .getOne();
    
    // ❌ NEVER do this in QueryBuilder:
    // .where(`user.username = '${username}'`)  // string interpolation = vulnerable!
  }
}

// ─── FIX 3: ORDER BY safety (dynamic column names) ──────────
const ALLOWED_SORT_COLUMNS = ['name', 'created_at', 'email', 'id'];
const ALLOWED_SORT_DIRS = ['ASC', 'DESC'];

app.get('/users', async (req, res) => {
  const sort = req.query.sort || 'id';
  const dir = (req.query.dir || 'ASC').toUpperCase();
  
  // ✅ Whitelist validation — only allow known safe column names
  if (!ALLOWED_SORT_COLUMNS.includes(sort)) {
    return res.status(400).json({ error: 'Invalid sort column' });
  }
  if (!ALLOWED_SORT_DIRS.includes(dir)) {
    return res.status(400).json({ error: 'Invalid sort direction' });
  }
  
  // ✅ Column names can't be parameterized — use whitelist instead
  const query = `SELECT id, name, email FROM users ORDER BY ${sort} ${dir}`;
  const [rows] = await db.execute(query);
  res.json(rows);
});

// ─── FIX 4: Prisma (safe by default) ────────────────────────
const user = await prisma.user.findFirst({
  where: { username: username },  // ✅ always parameterized
  select: { id: true, username: true, role: true }  // ✅ only return needed fields
});

// Prisma raw queries need explicit parameterization:
const users = await prisma.$queryRaw`
  SELECT id, username FROM users WHERE role = ${role}
`;  // ✅ template literal = parameterized
// ❌ NEVER: prisma.$queryRawUnsafe(`... WHERE role = '${role}'`)
```

---

## 🟠 Implementation in My Stack

```javascript
// ─── Node.js + mysql2 Setup (Full Secure Config) ─────────────
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,        // ✅ least-privilege user (SELECT/INSERT only, no DROP)
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  multipleStatements: false,         // ✅ prevents stacked queries ('; DROP TABLE')
});

// Always use execute() not query() for user data:
const [rows] = await pool.execute(
  'SELECT id, email FROM users WHERE id = ?',
  [userId]  // ✅ parameterized
);

// ─── NestJS + TypeORM secure config ──────────────────────────
// typeorm.config.ts
export const typeOrmConfig: TypeOrmModuleOptions = {
  type: 'mysql',
  host: configService.get('DB_HOST'),
  username: configService.get('DB_USER'),
  password: configService.get('DB_PASS'),
  database: configService.get('DB_NAME'),
  synchronize: false,   // ✅ never true in production
  logging: false,       // ✅ don't log queries in production (leaks structure)
  ssl: { rejectUnauthorized: true }  // ✅ encrypted connection
};

// ─── PostgreSQL (node-postgres) ───────────────────────────────
const { Pool } = require('pg');
const pgPool = new Pool({ connectionString: process.env.DATABASE_URL });

// ✅ $1 style parameterization:
const result = await pgPool.query(
  'SELECT * FROM orders WHERE user_id = $1 AND status = $2',
  [userId, status]
);

// ─── MongoDB — prevent NoSQL injection ───────────────────────
// ❌ Vulnerable:
db.users.find({ username: req.body.username });  // could be { $gt: '' }

// ✅ Validate type and sanitize:
const { username } = req.body;
if (typeof username !== 'string') return res.status(400).send('Bad input');
db.users.find({ username: username });  // now safe — string, not object
// OR use mongoose with schema validation (type: String rejects objects)
```

---

## 🔧 Security Tools + Libraries
| Tool | Purpose | Use |
|------|---------|-----|
| `mysql2` | MySQL driver with parameterization | `db.execute(sql, [params])` |
| TypeORM | ORM — parameterizes all queries | `createQueryBuilder` with named params |
| Prisma | ORM — safe by default | `prisma.$queryRaw\`...\`` |
| Mongoose | MongoDB ODM — schema validation | Schema type enforcement |
| `sqlmap` | Automated SQL injection scanner | `sqlmap -u "http://app.com/login"` |
| OWASP ZAP | Web app security scanner | Automated SQLi detection |
| `express-validator` | Input validation middleware | Validate before query |

---

## ⚫ Interview Questions + Answers

**Q1: What is SQL Injection and how does it work?**
A1: SQL Injection is an attack where malicious SQL code is embedded in user input and executed by the database. When an app concatenates user input directly into a SQL string, the database can't distinguish data from SQL commands. Example: `SELECT * FROM users WHERE username='admin'--'` — the `--` comments out the rest, bypassing authentication. Impact: data theft, authentication bypass, data manipulation, and even OS command execution.

**Q2: What's the difference between Parameterized Queries and an ORM — which is safer?**
A2: Parameterized queries use placeholders (`?` or `$1`) — the database driver sends the SQL and data separately, so user input is NEVER interpreted as SQL code. ORMs (TypeORM, Prisma, Sequelize) use parameterization internally and are safe by default — but raw query methods (`$queryRawUnsafe`) can still be vulnerable if you concatenate strings. In production, use ORM `findOne/findMany` for standard queries; use tagged template literals for raw queries (`prisma.$queryRaw\`...\``). Both are equally safe when used correctly.

**Q3: How do you prevent SQL Injection in dynamic ORDER BY clauses?**
A3: Column names and sort directions CANNOT be parameterized — only values can. The safe solution is a strict whitelist: maintain an array of allowed column names and validate the input against it. Example: `const ALLOWED = ['name', 'id', 'created_at']; if (!ALLOWED.includes(sort)) reject;` then safely interpolate the whitelisted value. Never trust user input for column/table names — whitelist only.

**Q4: What is Blind SQL Injection? How is it different?**
A4: In classic SQLi, the app shows the database result directly. In Blind SQLi, there's no visible output — the attacker infers information from application behavior. Time-based: `'; IF (1=1) WAITFOR DELAY '0:0:5'--` — if the response takes 5 seconds, the condition was true. Boolean-based: `' AND 1=1--` vs `' AND 1=2--` — different responses reveal information. Tools like SQLMap automate blind injection extraction. Prevention is the same: parameterized queries prevent all types.

**Q5: What DB permissions should the application user have?**
A5: Principle of Least Privilege — the app's DB user should have ONLY the permissions it needs: typically `SELECT, INSERT, UPDATE` on specific tables. Never `DROP, CREATE, ALTER, TRUNCATE` unless explicitly required. Never use root/admin DB accounts in application code. Create separate DB users per service: read-only user for reporting, write user for app logic, admin user only for migrations. This limits damage even if injection occurs.

---

## ✅ Security Checklist
```
□ Never concatenate user input into SQL strings (use ? or $1 placeholders)
□ Use ORM or prepared statements for ALL database queries
□ Whitelist dynamic SQL parts (column names, sort directions)
□ DB user has minimum required permissions (no DROP/CREATE/ALTER)
□ multipleStatements: false in MySQL connection config
□ Error messages don't expose table names, column names, or stack traces
□ Input validated for type, length, and format before query
□ Regular SQLMap or OWASP ZAP scans in CI/CD pipeline
□ Database connection encrypted (SSL/TLS)
□ Audit logging on sensitive tables (failed queries, unusual access patterns)
□ ORM raw queries use tagged template literals, never string concat
□ Stored procedure parameters also validated
```

---

## 📊 Visual Diagram

```
SQL INJECTION ATTACK vs DEFENSE:

ATTACK FLOW (❌ Vulnerable):
─────────────────────────────────────────────────────────
User Input:  admin' OR '1'='1
                 ↓
App Code:    "SELECT * FROM users WHERE name='" + input + "'"
                 ↓
Final SQL:   SELECT * FROM users WHERE name='admin' OR '1'='1'
                 ↓
DB Result:   Returns ALL rows (OR '1'='1' is always true)
                 ↓
Attacker:    Gets entire users table! ☠️

DEFENSE FLOW (✅ Parameterized):
─────────────────────────────────────────────────────────
User Input:  admin' OR '1'='1
                 ↓
App Code:    db.execute("SELECT * FROM users WHERE name=?", [input])
                 ↓
DB receives: SQL structure + data separately
             SQL:  SELECT * FROM users WHERE name=?
             Data: "admin' OR '1'='1"  ← treated as literal string
                 ↓
DB Result:   No user found with name "admin' OR '1'='1"
                 ↓
Attacker:    Gets nothing. Attack blocked! ✅

INJECTION TYPES:
Classic SQLi → visible results in response
Blind SQLi   → infer from true/false responses
Time-based   → infer from response delay
UNION-based  → extract data from other tables
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SQL Injection | Attack inserting SQL into queries | User input से SQL में malicious code |
| Parameterized Query | SQL with placeholders for data | ? या $1 से safe query बनाना |
| Prepared Statement | Pre-compiled query template | Compile करके data अलग भेजना |
| ORM | Object Relational Mapper | DB को objects से safely access करना |
| Least Privilege | Minimum DB permissions | DB user को minimum access देना |
| Blind SQLi | SQLi without visible output | Response से guess करके data चुराना |
| UNION Attack | Combining results from another table | दूसरी table का data extract करना |
| WAF | Web Application Firewall | Malicious patterns को block करना |

---

## ⚡ 3-Line Summary
**English:**
1. SQL Injection happens when user input is concatenated directly into SQL queries — the DB executes it as code instead of treating it as data.
2. Prevention: ALWAYS use parameterized queries (`?` or `$1`) or ORM methods — the DB driver keeps SQL structure and user data completely separate.
3. Defense in depth: validate all input, use least-privilege DB users, disable detailed error messages, and run regular SQLMap scans.

**Hindi:**
1. SQL Injection में user input को directly SQL query में concatenate करने पर DB उसे code मान लेता है।
2. Fix: हमेशा parameterized queries (?) या ORM use करो — SQL structure और data अलग-अलग जाता है।
3. Input validate करो, DB user को minimum permissions दो, error messages hide करो, regular scanning करो।

---

## 🚨 Red Flag Signs
- Query strings built with `+` or template literals containing `req.body`/`req.query` values
- DB error messages visible in API responses (table names, column names exposed)
- Database user has `root` or `admin` privileges in production
- No input validation on query parameters or form fields
- `multipleStatements: true` in MySQL config
- ORMs using `$queryRawUnsafe()` or `query()` with string interpolation
- No SQL injection tests in test suite

---

## ➡️ Next Topic
**027. SQL Injection Types** — Classic, Blind, Time-based, UNION-based — different attack techniques, how to detect each.
