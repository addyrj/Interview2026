
---

# Q140. Always Encrypted and TDE Concepts
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (concept question; not executed on SQL Server; behaviour per Microsoft docs; Azure SQL enables TDE by default)

---

## ❓ Question
Compare Transparent Data Encryption (TDE), Always Encrypted, column-level encryption and TLS: what each protects against, who holds the keys, what queries still work, and which you would pick for card numbers and national IDs in an Azure SQL backed Node.js app.

---

## 💡 Quick Concept (2 lines only)
TDE encrypts data files, log and backups at rest, transparently; the server holds the key, so it protects stolen disks and backups but not a DBA or an app SQL injection. Always Encrypted encrypts selected columns inside the client driver, so the server never sees plaintext or keys.
हिंदी: TDE disk/backup को encrypt करता है और key server के पास रहती है। Always Encrypted में column client driver में ही encrypt होता है, server को plaintext कभी नहीं मिलता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- TDE (at rest) : on-prem / VM / MI
-- ============================================
USE master;
CREATE MASTER KEY ENCRYPTION BY PASSWORD = N'<<strong-secret>>';
CREATE CERTIFICATE TdeCert WITH SUBJECT = N'TDE certificate';
-- BACK UP the certificate and private key NOW; without them the backups cannot be restored elsewhere.
USE OrdersDb;
CREATE DATABASE ENCRYPTION KEY WITH ALGORITHM = AES_256 ENCRYPTION BY SERVER CERTIFICATE TdeCert;
ALTER DATABASE OrdersDb SET ENCRYPTION ON;

SELECT DB_NAME(database_id) AS DbName, encryption_state, percent_complete
FROM sys.dm_database_encryption_keys;        -- encryption_state 3 = encrypted (documented)

-- Azure SQL Database: TDE is on by default with a service-managed key; optionally customer-managed key in Key Vault (BYOK).

-- ============================================
-- ALWAYS ENCRYPTED (in use / in transit / at rest)
-- ============================================
-- Keys (created via SSMS wizard or PowerShell): Column Master Key (in Key Vault / cert store, client side)
-- and Column Encryption Key. The table column definition looks like:
CREATE TABLE dbo.Patients (
  PatientId INT IDENTITY(1,1) PRIMARY KEY,
  Name      NVARCHAR(100) NOT NULL,
  NationalId CHAR(11) COLLATE Latin1_General_BIN2
    ENCRYPTED WITH (
      COLUMN_ENCRYPTION_KEY = CEK_Auto1,
      ENCRYPTION_TYPE = DETERMINISTIC,                       -- equality lookups, joins, GROUP BY possible
      ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NOT NULL,
  Notes     NVARCHAR(400)
    ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = CEK_Auto1,
                    ENCRYPTION_TYPE = RANDOMIZED,            -- stronger, no server-side comparison
                    ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256') NULL
);
```

```js
// Node.js (mssql/tedious): column encryption support in tedious is limited/version-dependent,
// so verify it for your driver version. The usual pattern: encrypt in the application (e.g. AES-GCM with a key
// from Azure Key Vault) or use .NET/ODBC drivers with "Column Encryption Setting=Enabled".
```

```sql
-- EXPECTED OUTPUT
-- Not executed on SQL Server; behaviour per Microsoft docs.
-- Without driver support, SELECT NationalId returns varbinary ciphertext; WHERE NationalId = @p only works with
-- a parameter that the driver encrypts (DETERMINISTIC). RANDOMIZED columns cannot be compared at all on the server.
-- sys.dm_database_encryption_keys: encryption_state = 3 once TDE completes (documented).
```

| Control | Protects against | Key holder | Server can query/index it |
|---|---|---|---|
| TLS | network sniffing | server cert | n/a |
| TDE | stolen files/backups | server (cert / Key Vault) | yes, fully |
| Always Encrypted | DBA, cloud operator, server compromise | client / Key Vault | limited: equality (deterministic), or secure enclaves for richer ops |
| Column-level (ENCRYPTBYKEY) | casual access | server | no |
| Dynamic masking | accidental viewing | n/a | yes (not security) |

---

## 🔍 Why This Works (3 lines max)
TDE encrypts pages as they hit disk and decrypts in memory, so nothing changes for queries. Always Encrypted moves encryption to the driver, so keys never reach the server and even sysadmins read only ciphertext; the price is restricted server-side operations.
हिंदी: TDE में query पर कोई असर नहीं पड़ता, पर server key रखता है। Always Encrypted में key client पर रहती है, इसलिए DBA भी सिर्फ़ ciphertext देखता है, बदले में server-side operations सीमित हो जाते हैं।

---

## ⚡ Alternative Solution

```sql
-- Secure enclaves (Always Encrypted with secure enclaves, SQL Server 2019+ / Azure SQL with supported attestation)
-- allow richer operations (range, LIKE) on encrypted columns; check current availability and driver support.
-- Tokenisation of card numbers via a payment provider (never store PAN yourself) is usually the best answer for cards.
-- Application-layer envelope encryption with Azure Key Vault keeps the DB schema simple.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: enabling TDE and not backing up the certificate -> backups unrestorable on another server
-- ❌ Wrong: thinking TDE stops SQL injection or a malicious DBA; data is decrypted for any authenticated query
-- ❌ Wrong: DETERMINISTIC encryption on low-cardinality columns (e.g. gender): frequency analysis reveals values
-- ❌ Wrong: designing queries needing LIKE/ORDER BY/range over Always Encrypted columns without enclaves
-- ❌ Wrong: forgetting that TDE also encrypts tempdb, which can slow other databases on the instance
```

---

## 🎯 Interview Tip (1 line)
Say: "TDE is the baseline for compliance and is already on in Azure SQL. For the truly sensitive fields where even DBAs must not read plaintext I add Always Encrypted or tokenisation, accepting query limits. TLS in transit, TDE at rest, Key Vault for keys, rotate keys, and I would never store raw card numbers at all."

---

## 🔗 Related Questions
→ Q139 (Dynamic data masking) | Q136 (Least-privilege permissions) | Q141 (Backup and restore basics) | Q164 (Firewall, private endpoints and TLS)
