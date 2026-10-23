# M05. Local Storage (AsyncStorage, MMKV, SQLite, WatermelonDB, Keychain)
# हिंदी में: Mobile पर Local Storage — फ़ोन के अंदर डेटा रखने के तरीके: छोटी settings के लिए key-value (AsyncStorage, MMKV), बड़े और खोजने लायक डेटा के लिए database (SQLite, WatermelonDB), passwords/tokens के लिए सुरक्षित तिजोरी (Keychain/Keystore), और फ़ोटो/वीडियो के लिए files

---

## 🔵 Simple Definition (English)
Mobile apps persist data on the device for **offline use, fast startup, drafts and caching**. Main options in React Native:
- **AsyncStorage**: simple **async key-value** store (strings). Unencrypted, relatively slow. Fine for small, non-sensitive data. (Legacy default.)
- **MMKV** (`react-native-mmkv`, from Tencent/WeChat): **very fast, synchronous key-value** storage via JSI (memory-mapped files), with optional encryption. Great for prefs, flags, session info and persisted caches.
- **SQLite** (`expo-sqlite`, `op-sqlite`): a full **relational database** with SQL queries, indexes, transactions and full-text search (FTS5). For large structured data (messages, orders, products).
- **WatermelonDB**: a **reactive, lazy-loading database on top of SQLite**, built for RN apps with **tens of thousands of records** and with sync primitives (pull/push changes).
- **Keychain (iOS) / Keystore (Android)** via `expo-secure-store` / `react-native-keychain`: **encrypted, hardware-backed secure storage** for **tokens, passwords, encryption keys**, optionally gated by biometrics.
- **File system** (`expo-file-system`): media, downloads and large blobs (store the path in the DB).
(Realm was popular but MongoDB deprecated Atlas Device Sync/Realm SDKs in 2024–25, so prefer the options above for new apps.)

## 🔵 सरल परिभाषा (Hindi)
फ़ोन में डेटा रखना offline, तेज़ startup, drafts और cache के लिए ज़रूरी है। AsyncStorage = आसान async key-value (धीमा, encrypted नहीं); MMKV = बहुत तेज़ sync key-value (WeChat का बनाया, JSI पर); SQLite = पूरा database (queries, indexes, transactions — messages/orders के लिए); WatermelonDB = SQLite के ऊपर reactive DB, हज़ारों records और sync के लिए; Keychain/Keystore = tokens/passwords के लिए encrypted तिजोरी (biometric के साथ भी); File system = फ़ोटो/वीडियो (path DB में)।

---

## 🔴 Problem it Solves
Choosing the wrong storage causes real issues:
- **Tokens in AsyncStorage/MMKV unencrypted**: on rooted/jailbroken devices or via backups, credentials can be extracted.
- **Thousands of chat messages stored as one big JSON string** in AsyncStorage: slow reads, the whole blob is parsed on every launch, and there's no querying. Android AsyncStorage also has size limits by default.
- **Synchronous reads at startup from slow storage** delay the first screen (M03).
- **No schema migrations**: app v5 changes the table shape, and users upgrading from v3 crash on launch.
- **Unbounded caches** fill the phone's storage, so users uninstall the app.
Picking the right store per data type gives **speed, queryability, security and maintainability**.

## 🔴 यह क्यों बना? (Hindi)
ग़लत storage से असली समस्याएँ: token बिना encryption के AsyncStorage/MMKV में (rooted फ़ोन या backup से चोरी); हज़ारों messages एक बड़ी JSON string में (हर launch पर पूरा parse, query नहीं); startup पर धीमे storage से पढ़ना; schema migration नहीं — नया version पुराने यूज़र्स के लिए crash; बिना सीमा cache से फ़ोन भर जाए और यूज़र ऐप हटा दे।
हर तरह के डेटा के लिए सही store = तेज़ी, query, सुरक्षा और आसान रख-रखाव।

---

## 🟢 How it Works — Step by Step

### Which storage for which data

```
┌──────────────────────────────┬──────────────────────────────┬───────────────────────────────────┐
│ Data                         │ Store                        │ Why                               │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ Access/refresh tokens, PIN,  │ Keychain / Keystore          │ Encrypted, hardware-backed,       │
│ DB encryption key            │ (expo-secure-store)          │ biometric gating, not in backups  │
│ Settings, flags, onboarding  │ MMKV                         │ Sync & fast (µs), tiny values     │
│ done, last city, theme       │                              │                                   │
│ Persisted query cache (small)│ MMKV                         │ Fast boot render                  │
│ Messages, orders, products,  │ SQLite / WatermelonDB        │ Query, sort, index, paginate,     │
│ contacts, offline outbox     │                              │ transactions, large volumes        │
│ Full-text search offline     │ SQLite FTS5                  │ Fast local search                 │
│ Images, videos, PDFs, voice  │ File system (+ DB metadata)  │ Big blobs don't belong in DB/KV   │
│ notes                        │                              │                                   │
│ Image cache                  │ expo-image / FastImage disk  │ Managed LRU cache                 │
│                              │ cache                        │                                   │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────────┘
```

### Characteristics

```
              API      Speed        Encrypted     Query    Size sweet spot     Notes
AsyncStorage  async    slow-ish     no            no       < few MB            simple, legacy
MMKV          sync     very fast    optional key  no       KBs–few MBs        JSI; keep values small
SQLite        async*   fast         SQLCipher opt yes(SQL) MBs–GBs             migrations needed
WatermelonDB  async    fast, lazy   via SQLCipher yes      10k–100k+ records   reactive observe(), sync
SecureStore   async    slow-ish     yes (OS)      no       tiny (≤ ~2 KB/item) secrets only
File system   async    I/O bound    OS protection n/a      large files         manage cleanup
(*op-sqlite offers sync JSI calls for small queries)
```

### Data lifecycle concerns

```
Migrations: version your local schema; run migrations at startup in a transaction; test upgrade paths
            v1→v5 (users skip versions!)
Eviction:   LRU caps (media 500 MB, messages keep last N per chat or by age); iOS may purge Caches dir
            under storage pressure → treat caches as disposable
Backups:    iOS iCloud/Android Auto Backup may include app files → exclude secrets & large caches;
            Keychain items can be set "ThisDeviceOnly" (not migrated to new devices)
Logout:     wipe user data (DB, MMKV, files, secure store) to avoid leaking to next user (shared phones!)
Encryption: Keychain/Keystore for keys; SQLCipher or MMKV encryptionKey for sensitive local data;
            OS file protection (iOS NSFileProtectionComplete)
Multi-user: namespace storage by userId if account switching is supported
```

### Performance tips

```
- Don't store huge JSON blobs in KV; normalize into tables
- Index columns used in WHERE/ORDER BY (chat_id, created_at)
- Batch writes in transactions (1000 inserts → 1 transaction, not 1000)
- Paginate reads (LIMIT/OFFSET or keyset) for long lists; observe only visible queries
- Do heavy DB work off the JS thread (native SQLite runs on background threads)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Tokens, PIN, DB की encryption key → Keychain/Keystore (encrypted, hardware-backed, backup में नहीं); छोटी settings/flags → MMKV (बहुत तेज़, sync)।
2. Messages, orders, products, outbox → SQLite या WatermelonDB (query, index, transactions); offline search → SQLite FTS5; फ़ोटो/वीडियो → file system, उसका path DB में।
3. Local schema का version रखो, startup पर transaction में migration चलाओ, और v1 से सीधे v5 वाला upgrade भी जाँचो (यूज़र versions छोड़ते हैं)।
4. Cache की सीमा (media 500 MB, पुराने messages हटाओ), iOS Caches folder ख़ुद साफ़ कर सकता है; logout पर सब मिटाओ (shared फ़ोन!); secrets को backup से बाहर रखो।
5. बड़ी JSON को KV में मत रखो, tables बनाओ; WHERE/ORDER BY वाले columns पर index; कई writes एक transaction में; लंबी list के लिए pagination।

---

## 🟡 Real World Example

**WhatsApp** — stores messages in a local SQLite database (the well-known `msgstore.db` on Android), with media as files on disk. That's why chats load instantly offline. Backups are encrypted (end-to-end encrypted backups since 2021).

**WeChat → MMKV** — Tencent built MMKV for WeChat's need for very fast, crash-safe key-value storage on mobile and open-sourced it. `react-native-mmkv` brings it to RN via JSI (~30× faster than AsyncStorage in benchmarks).

**Nozbe → WatermelonDB** — Nozbe built WatermelonDB for its Nozbe Teams app to handle tens of thousands of records smoothly in RN, with lazy loading and a sync protocol.

**Signal** — uses SQLCipher-encrypted SQLite for its message database, with keys protected by the OS keystore.

**Banking/UPI apps (PhonePe, Google Pay, bank apps)** — store tokens and device-binding keys in Keychain/Keystore (often hardware-backed), never in plain storage, and wipe local data on logout or SIM change.

## 🟡 Real Example Hindi में
WhatsApp messages को local SQLite (`msgstore.db`) में और media को files में रखता है — इसलिए offline भी chats तुरंत खुलती हैं। Tencent ने WeChat के लिए MMKV बनाया (बहुत तेज़ key-value), जो अब RN में JSI से आता है।
Nozbe ने हज़ारों records के लिए WatermelonDB बनाया; Signal SQLCipher से encrypted SQLite इस्तेमाल करता है; PhonePe/Google Pay जैसे UPI ऐप tokens और device-binding keys Keychain/Keystore में रखते हैं और logout या SIM बदलने पर local डेटा मिटा देते हैं।

---

## 🟠 My Stack Example

### MMKV: fast settings + encrypted instance (key from secure store)
```ts
// src/data/kv.ts
import { MMKV } from 'react-native-mmkv';
import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';

export const kv = new MMKV();                                   // non-sensitive prefs
kv.set('settings.lang', 'hi'); kv.set('onboarding.done', true);
const lang = kv.getString('settings.lang') ?? 'en';             // sync — safe at startup

export async function getSecureKv() {
  let key = await SecureStore.getItemAsync('mmkv.key');
  if (!key) { key = Crypto.randomUUID().replace(/-/g, ''); await SecureStore.setItemAsync('mmkv.key', key); }
  return new MMKV({ id: 'secure', encryptionKey: key.slice(0, 16) });   // MMKV key max 16 bytes
}
```

### Secure tokens (Keychain/Keystore) with biometric option
```ts
// src/data/secure.ts
import * as SecureStore from 'expo-secure-store';
const opts = { keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY };
export const secure = {
  saveRefresh: (t: string) => SecureStore.setItemAsync('auth.refresh', t, opts),
  getRefresh: () => SecureStore.getItemAsync('auth.refresh', opts),
  saveRefreshWithBiometric: (t: string) => SecureStore.setItemAsync('auth.refresh', t, { ...opts, requireAuthentication: true }),  // Face ID / fingerprint to read
  clear: () => SecureStore.deleteItemAsync('auth.refresh'),
};
```

### SQLite (expo-sqlite) with migrations, indexes, transactions, FTS
```ts
// src/data/db/index.ts
import * as SQLite from 'expo-sqlite';
export const db = SQLite.openDatabaseSync('app.db');

const migrations: string[] = [
  /* v1 */ `CREATE TABLE messages (id TEXT PRIMARY KEY, client_id TEXT UNIQUE, chat_id TEXT NOT NULL,
            sender_id TEXT, body TEXT, status TEXT, created_at INTEGER NOT NULL);
          CREATE INDEX idx_msg_chat_time ON messages(chat_id, created_at DESC);`,
  /* v2 */ `ALTER TABLE messages ADD COLUMN media_path TEXT;`,
  /* v3 */ `CREATE VIRTUAL TABLE messages_fts USING fts5(body, content='messages', content_rowid='rowid');`,
];

export function migrate() {
  const { user_version } = db.getFirstSync<{ user_version: number }>('PRAGMA user_version')!;
  db.withTransactionSync(() => {
    for (let v = user_version; v < migrations.length; v++) db.execSync(migrations[v]);
    db.execSync(`PRAGMA user_version = ${migrations.length}`);
  });
}

export async function insertMessages(rows: Message[]) {
  await db.withTransactionAsync(async () => {                      // one transaction for the batch
    const stmt = await db.prepareAsync(`INSERT OR REPLACE INTO messages (id, client_id, chat_id, sender_id, body, status, created_at) VALUES (?,?,?,?,?,?,?)`);
    try { for (const m of rows) await stmt.executeAsync([m.id, m.clientId, m.chatId, m.senderId, m.body, m.status, m.createdAt]); }
    finally { await stmt.finalizeAsync(); }
  });
}

export const pageMessages = (chatId: string, before: number, limit = 50) =>
  db.getAllAsync<Message>(`SELECT * FROM messages WHERE chat_id=? AND created_at < ? ORDER BY created_at DESC LIMIT ?`, [chatId, before, limit]);
```

### WatermelonDB: reactive lists + sync
```ts
// model
class Order extends Model { static table = 'orders'; @field('status') status!: string; @date('created_at') createdAt!: Date; }
// component re-renders automatically when matching records change
const enhance = withObservables([], () => ({ orders: database.get<Order>('orders').query(Q.sortBy('created_at', Q.desc), Q.take(50)) }));
export default enhance(OrderList);

// sync with backend (pull changes since last sync, push local changes)
await synchronize({
  database,
  pullChanges: async ({ lastPulledAt }) => (await api.get('/sync/pull', { params: { since: lastPulledAt ?? 0 } })).data,   // { changes, timestamp }
  pushChanges: async ({ changes, lastPulledAt }) => { await api.post('/sync/push', { changes, lastPulledAt }); },
});
```

### Files: store media, keep metadata in DB, cap cache size
```ts
import * as FileSystem from 'expo-file-system';     // Expo SDK 54+: this classic API is at 'expo-file-system/legacy'
const MEDIA_DIR = FileSystem.documentDirectory + 'media/';          // persistent (vs cacheDirectory = purgeable)
export async function saveIncomingMedia(url: string, messageId: string) {
  await FileSystem.makeDirectoryAsync(MEDIA_DIR, { intermediates: true });
  const { uri } = await FileSystem.downloadAsync(url, `${MEDIA_DIR}${messageId}.jpg`);
  db.runSync('UPDATE messages SET media_path=? WHERE id=?', [uri, messageId]);
}
```

### Logout: wipe everything for the user
```ts
export async function wipeLocalData() {
  db.closeSync(); await SQLite.deleteDatabaseAsync('app.db');
  kv.clearAll(); (await getSecureKv()).clearAll(); await secure.clear();
  await FileSystem.deleteAsync(MEDIA_DIR, { idempotent: true });
  queryClient.clear();
}
```

---

## ⚫ Interview Questions + Answers

**Q1: Which storage would you use for tokens, settings and chat messages in a React Native app?**
A1: Tokens and secrets go in Keychain/Keystore via expo-secure-store or react-native-keychain: encrypted, hardware-backed where available, excluded from device-transfer backups with "ThisDeviceOnly", and optionally biometric-gated. Settings and small flags go in MMKV for synchronous, fast reads at startup. Chat messages go in SQLite or WatermelonDB with indexes on chat and time, pagination, transactions and FTS for search, with media as files and paths in the DB.

**Q2: Why is MMKV faster than AsyncStorage?**
A2: MMKV uses memory-mapped files with an efficient protobuf-based append format, so reads and writes are close to memory speed, and react-native-mmkv calls it synchronously through JSI with no async bridge round trip or JSON serialization. AsyncStorage is asynchronous and historically bridged through native modules backed by SQLite (Android) or files (iOS), adding overhead per call. MMKV also supports encryption and multiple instances. It's still a key-value store, so large structured data belongs in a database.

**Q3: How do you handle local database migrations across app versions?**
A3: Track a schema version (`PRAGMA user_version` or the library's schema version) and maintain an ordered list of migrations. On startup, apply every migration from the current version to the latest inside a transaction, because users may jump from v1 to v5. Prefer additive changes, backfill data where needed, and test upgrade paths from old versions with real data. For irrecoverable issues, have a fallback that resets the cache tables and resyncs from the server, without losing unsynced outbox data.

**Q4: How do you keep local data secure?**
A4: Store secrets only in Keychain/Keystore. Encrypt sensitive databases (SQLCipher) and KV stores (MMKV encryption) with keys held in the secure store, and use OS file protection classes. Exclude sensitive files from backups. Avoid logging PII. Wipe user data on logout and account switch. Consider root/jailbreak detection for high-risk apps, and minimize what is stored locally (e.g., no full card numbers). Clear clipboard-sensitive data and screenshots of sensitive screens where required (M15).

**Q5: When would you choose WatermelonDB over plain SQLite?**
A5: When the app has large, relational datasets (thousands to hundreds of thousands of records) that the UI must observe reactively, such as task lists, CRM data or chat. WatermelonDB provides lazy loading (records instantiated only when needed), observable queries that re-render components on change, a model layer and a built-in pull/push sync protocol, all on SQLite. Plain SQLite (op-sqlite/expo-sqlite) is simpler and more flexible when you want direct SQL control, have smaller datasets, or use another sync solution.

---

## 🔷 Trade-offs
✅ MMKV: fastest KV — ❌ not for big/structured data; memory mapped size considerations.
✅ SQLite: powerful queries & scale — ❌ schema design + migrations.
✅ WatermelonDB: reactive + sync for big data — ❌ learning curve, model boilerplate.
✅ Secure store: strongest protection — ❌ small values only, slower, can be lost on device reset/restore.
✅ AsyncStorage: simplest — ❌ slow, unencrypted, not for large data.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Key-value store | Store values by key | key से मान रखना |
| AsyncStorage | RN async KV store | RN का async KV |
| MMKV | Fast mmap-based KV (JSI) | तेज़ key-value |
| SQLite | Embedded relational DB | फ़ोन का database |
| WatermelonDB | Reactive DB on SQLite | reactive database |
| Keychain / Keystore | OS secure credential storage | OS की तिजोरी |
| SQLCipher | Encrypted SQLite | encrypted SQLite |
| Migration | Schema upgrade step | schema बदलाव |
| FTS | Full-text search | पूरे text में खोज |
| Eviction | Removing old cached data | पुराना cache हटाना |

---

## ⚡ 3-Line Summary
**English:**
1. Secrets → Keychain/Keystore; small prefs/flags/caches → MMKV; structured data → SQLite/WatermelonDB; media → files (+ DB metadata).
2. Design for scale: indexes, transactions, pagination, FTS, versioned migrations tested across version jumps.
3. Secure & tidy: encrypt sensitive data with keys in secure storage, exclude from backups, cap caches, wipe on logout.

**Hindi:**
1. Secrets → Keychain; छोटी settings → MMKV; बड़ा डेटा → SQLite/WatermelonDB; media → files।
2. Index, transaction, pagination, FTS और version वाली migrations (versions छोड़ने वाले यूज़र्स के लिए भी)।
3. संवेदनशील डेटा encrypt, backup से बाहर, cache की सीमा, logout पर सब साफ़।

---

## ➡️ Next Topic Suggestion
**M06. Offline-First Architecture** — With storage chosen, design apps that work fully offline: the local DB as source of truth, an outbox for writes, sync on reconnect, and UI states for pending changes.
