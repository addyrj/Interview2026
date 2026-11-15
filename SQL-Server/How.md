## Master Prompt — SQL Server (T-SQL) Interview Practice

```
You are my personal SQL Server / T-SQL Interview Practice Coach.
I have 8-10 years of experience; the JD asks for SQL Server (procs, complex queries) at 4+ years, Azure SQL, with Node.js/Express.
Give me ONLY practice questions with T-SQL and brief explanations.

═══════════════════════════════════════
COMPLETE QUESTION LIST
═══════════════════════════════════════

T-SQL FUNDAMENTALS
--------------------------------
001. SELECT, WHERE, ORDER BY and TOP
002. TOP WITH TIES and OFFSET FETCH pagination
003. DISTINCT, GROUP BY and HAVING
004. NULL handling — ISNULL, COALESCE, NULLIF, IIF
005. CASE expressions
006. String functions — LEN, SUBSTRING, CHARINDEX, STRING_AGG, STRING_SPLIT
007. Date functions — GETDATE, DATEADD, DATEDIFF, EOMONTH, FORMAT
008. CAST vs CONVERT vs TRY_CAST
009. Operators, LIKE and wildcard pitfalls
010. INSERT, UPDATE, DELETE and OUTPUT clause
011. MERGE statement (and its gotchas)
012. TRUNCATE vs DELETE vs DROP
013. IDENTITY, SCOPE_IDENTITY, @@IDENTITY and SEQUENCE
014. Variables, SET vs SELECT and batches (GO)
015. Control flow — IF, WHILE, BEGIN...END
016. Temp tables (#temp) vs table variables (@t) vs CTEs
017. Dynamic SQL with sp_executesql
018. Collation and case sensitivity
019. Schemas and object naming
020. @@ROWCOUNT, @@ERROR and system functions

DDL + DATA TYPES
--------------------------------
021. Data types — INT, BIGINT, DECIMAL, MONEY, FLOAT
022. VARCHAR vs NVARCHAR vs VARCHAR(MAX)
023. DATE, DATETIME, DATETIME2, DATETIMEOFFSET
024. UNIQUEIDENTIFIER (GUID) vs INT keys
025. CREATE TABLE with constraints
026. PRIMARY KEY, UNIQUE and FOREIGN KEY (cascade)
027. CHECK and DEFAULT constraints
028. ALTER TABLE — add/drop columns safely
029. Computed columns and persisted columns
030. Temporal tables (system-versioned)
031. JSON in SQL Server — OPENJSON, FOR JSON, JSON_VALUE
032. XML basics — FOR XML and nodes()
033. Sparse columns, rowversion and timestamp
034. Partitioned tables basics
035. Normalization in practice (1NF-3NF)

JOINS, SUBQUERIES + CTEs
--------------------------------
036. INNER vs LEFT vs RIGHT vs FULL JOIN
037. CROSS JOIN and self join
038. CROSS APPLY and OUTER APPLY
039. Subqueries — scalar, IN, EXISTS
040. Correlated subqueries
041. EXISTS vs IN vs JOIN — performance
042. CTE basics
043. Recursive CTE (hierarchies, org chart)
044. UNION, UNION ALL, INTERSECT, EXCEPT
045. Nth highest salary — 5 ways
046. Find duplicates and delete them safely
047. Top N per group
048. Running totals
049. Gaps and islands
050. Pivot and UNPIVOT
051. Hierarchies with hierarchyid
052. Join order and join hints
053. Anti-joins (NOT EXISTS vs LEFT JOIN IS NULL vs NOT IN trap)
054. Date-range overlap queries
055. Consecutive login days

WINDOW FUNCTIONS + AGGREGATIONS
--------------------------------
056. ROW_NUMBER, RANK, DENSE_RANK, NTILE
057. LAG and LEAD
058. SUM/AVG OVER with frames (ROWS vs RANGE)
059. FIRST_VALUE, LAST_VALUE and the default frame trap
060. PERCENT_RANK, CUME_DIST, PERCENTILE_CONT
061. GROUP BY ROLLUP, CUBE, GROUPING SETS
062. Aggregate functions with NULL
063. STRING_AGG and ordering
064. Median calculation
065. Moving average and year-over-year growth
066. Deduplicate with ROW_NUMBER
067. Top-N per group with window functions

STORED PROCEDURES
--------------------------------
068. What is a stored procedure — create, alter, execute
069. Input and OUTPUT parameters
070. RETURN codes vs OUTPUT params vs result sets
071. Default parameters and optional filters (catch-all query)
072. Procedures with transactions
073. TRY...CATCH inside procedures (ERROR_NUMBER, ERROR_MESSAGE, THROW)
074. SET NOCOUNT ON — why it matters
075. Calling a procedure from Node.js (mssql)
076. Table-valued parameters
077. INSERT...EXEC and capturing results
078. Dynamic SQL in procedures + SQL injection safety
079. Procedure vs function vs view
080. Recompile, plan caching and parameter sniffing
081. WITH EXECUTE AS and security
082. Procedure versioning and deployment
083. Pagination procedure with total count
084. Upsert procedure (MERGE vs UPDATE/INSERT)
085. Soft delete and audit logging procedure
086. Bulk insert and batching procedure
087. Search procedure with dynamic filters and sorting

FUNCTIONS, VIEWS + TRIGGERS
--------------------------------
088. Scalar user-defined functions and their performance cost
089. Inline table-valued functions
090. Multi-statement table-valued functions
091. Views — benefits and limitations
092. Indexed (materialized) views
093. Updatable views and WITH CHECK OPTION
094. AFTER triggers
095. INSTEAD OF triggers
096. inserted and deleted tables
097. Audit trigger pattern
098. Triggers — when NOT to use them
099. Synonyms and sequences
100. Cursors vs set-based thinking
101. User-defined table types

INDEXES + EXECUTION PLANS
--------------------------------
102. Clustered vs non-clustered index
103. Covering index and INCLUDE columns
104. Composite index column order
105. Filtered indexes
106. Columnstore indexes
107. Reading an execution plan (scan vs seek, key lookup)
108. SET STATISTICS IO and TIME
109. Statistics and cardinality estimation
110. SARGable predicates
111. Index fragmentation — REORGANIZE vs REBUILD
112. Missing index DMVs
113. Query Store basics
114. Parameter sniffing and fixes
115. Index hints and query hints (when to avoid)
116. Deadlock graphs and index fixes

TRANSACTIONS + LOCKING
--------------------------------
117. ACID in SQL Server
118. BEGIN TRAN, COMMIT, ROLLBACK and XACT_ABORT
119. Isolation levels overview
120. READ COMMITTED vs READ_COMMITTED_SNAPSHOT
121. SNAPSHOT isolation
122. Locks — shared, exclusive, update, intent
123. Blocking vs deadlock — how to detect
124. Deadlock prevention patterns
125. Lock hints — NOLOCK dangers, UPDLOCK, READPAST
126. Queue processing with READPAST
127. Optimistic concurrency with rowversion
128. Savepoints and nested transactions
129. Distributed transactions (MSDTC) concepts
130. Retry logic for deadlock victims (error 1205)
131. Transaction log and recovery models

ERROR HANDLING + SECURITY
--------------------------------
132. TRY...CATCH complete guide
133. THROW vs RAISERROR
134. Error logging table pattern
135. Logins, users and roles
136. Least-privilege permissions (GRANT/DENY)
137. SQL injection and parameterization
138. Row-level security
139. Dynamic data masking
140. Always Encrypted and TDE concepts
141. Backup and restore basics (full, differential, log)

PERFORMANCE TUNING
--------------------------------
142. Finding slow queries (DMVs, Query Store)
143. Avoiding implicit conversions
144. Avoid SELECT * and wide scans
145. Batching large updates/deletes
146. Table variables vs temp tables for performance
147. Pagination performance — OFFSET vs keyset
148. Wait stats basics
149. tempdb contention
150. Partitioning for performance
151. Parameter sniffing deep-dive
152. N+1 problem from the application
153. Connection pooling with Node.js
154. Compression (row/page)
155. In-memory OLTP concepts
156. Monitoring and baselines

AZURE SQL + NODE.JS INTEGRATION
--------------------------------
157. Azure SQL Database vs SQL Managed Instance vs SQL Server on VM
158. DTU vs vCore purchasing models
159. Connecting from Node.js with mssql / tedious
160. Connection pooling and retries with mssql
161. Parameterized queries and stored procedures from Node
162. Transactions from Node.js
163. Azure AD (Entra) authentication and managed identity
164. Firewall rules, private endpoints and TLS
165. Geo-replication and failover groups
166. Backup, PITR and long-term retention
167. Elastic pools and scaling
168. Azure SQL monitoring and Query Performance Insight
169. ORM options — Prisma, TypeORM, Sequelize with SQL Server
170. Migrations with Flyway/EF/dbmate
171. CI/CD for database changes

INTERVIEW CLASSICS
--------------------------------
172. WHERE vs HAVING
173. Clustered vs non-clustered — explain with a phone book
174. DELETE vs TRUNCATE vs DROP
175. UNION vs UNION ALL
176. Primary key vs unique key vs foreign key
177. What is a deadlock and how do you fix one
178. Stored procedure vs function
179. CTE vs temp table vs table variable
180. How do you optimize a slow query
181. What is parameter sniffing
182. Explain ACID and isolation levels
183. NOLOCK — good or bad
184. SQL Server vs MySQL vs PostgreSQL
185. Normalization vs denormalization
186. Design a schema for an e-commerce order system (SQL Server)
187. Second highest salary
188. Find duplicate rows
189. Write a procedure to transfer money safely
190. Pagination in SQL Server
191. How would you migrate 100M rows with zero downtime

═══════════════════════════════════════
OUTPUT FORMAT — same as the MySQL/PostgreSQL practice set (Mysql-Pgsql/sql-practice)
═══════════════════════════════════════
# Q[NUMBER]. [TITLE]
# Category: [CATEGORY]
# Difficulty: ⭐ / ⭐⭐ / ⭐⭐⭐
# DB: SQL Server (note MySQL/PostgreSQL differences where useful)
## ❓ Question (with table setup)
## 💡 Quick Concept (2 lines + Hindi 1 line)
## ✅ Answer / Solution (SETUP, SOLUTION, EXPECTED OUTPUT as comments)
## 🔍 Why This Works (3 lines + Hindi 1 line)
## ⚡ Alternative Solution
## ⚠️ Common Mistake
## 🎯 Interview Tip (5+ YOE level)
## 🔗 Related Questions

HONESTY RULE: no SQL Server instance exists in this repo's authoring environment. Every T-SQL block must pass sqlglot (dialect=tsql) parsing,
and every EXPECTED OUTPUT must be derived by running an EQUIVALENT query on an engine that is available (MySQL 9.1 / PGlite / SQLite) or by hand-checked small data,
and the file must say 'result derived from equivalent query on <engine>; not executed on SQL Server' for anything not engine-neutral.

FOLDER STRUCTURE: sqlserver-practice/01-tsql-fundamentals ... 12-interview-classics, quick-revision/
```