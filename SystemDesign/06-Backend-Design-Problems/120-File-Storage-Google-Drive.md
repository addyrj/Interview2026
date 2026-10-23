# 120. File Storage & Sync (Google Drive / Dropbox)
# हिंदी में: File Storage System — यूज़र की फ़ाइलें cloud में सुरक्षित रखना, सारे devices पर sync करना, बड़ी फ़ाइलें टुकड़ों में upload, पुराने versions, और दूसरों के साथ share करना

---

## 🔵 Simple Definition (English)
Design a cloud file storage and sync service like **Google Drive / Dropbox / OneDrive**: users **upload, download, organize (folders), share (permissions/links), and version** files, and changes **sync automatically across devices** (desktop, mobile, web). Key techniques: **chunking**, **content-hash deduplication**, **delta sync**, **metadata service vs blob storage separation**, **resumable uploads**, **change notifications**, and **conflict handling**.

## 🔵 सरल परिभाषा (Hindi)
Google Drive जैसा सिस्टम: फ़ाइलें upload/download, folders, share (कौन देख/बदल सकता है), पुराने versions, और लैपटॉप-फ़ोन-वेब सब पर अपने आप sync।
मुख्य तरीके: फ़ाइल को टुकड़ों (chunks) में बाँटना, एक जैसे टुकड़े दोबारा न रखना (dedup), सिर्फ़ बदला हुआ हिस्सा भेजना, metadata और असली डेटा अलग रखना।

---

## 🔴 Problem it Solves
- Uploading a 5 GB video over flaky mobile internet fails halfway → must **resume**, not restart.
- Editing one slide in a 200 MB presentation shouldn't **re-upload 200 MB**.
- Millions of users store the **same files** (popular PDFs, OS installers), so storing every copy wastes petabytes.
- Edits on a laptop must appear on the phone within seconds; **offline edits on two devices** must not silently overwrite each other.
- Sharing must be **secure** (permissions, link sharing, revocation).

## 🔴 यह क्यों बना? (Hindi)
5 GB की फ़ाइल mobile नेटवर्क पर आधी अपलोड होकर टूटे तो फिर से नहीं, वहीं से शुरू होनी चाहिए; 200 MB फ़ाइल में एक बदलाव पर पूरी दोबारा नहीं भेजनी; करोड़ों लोग एक जैसी फ़ाइलें रखते हैं — हर copy रखना बर्बादी; दो devices पर offline बदलाव एक-दूसरे को मिटाएँ नहीं; और sharing सुरक्षित हो।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional: upload/download (large files), folders, rename/move/delete (trash), versions/restore,
            share with users (viewer/commenter/editor) & links, sync across devices, offline edits,
            search by name, previews/thumbnails
Non-functional: durability 11 nines (never lose files), high availability, sync latency seconds,
                efficient bandwidth (resume, dedup, delta), strong consistency for metadata ops
                (rename/move/permissions), scale to billions of files / exabytes
```

### 2. Estimation

```
Users 500M, active 100M; avg storage 10 GB/user → 5 EB total (!) → object storage, dedup, tiering
Uploads: 1B file changes/day ≈ 12k/s; avg 1 MB → ~12 GB/s ingest peak-ish
Metadata: 500B files/folders × 1 KB ≈ 500 TB metadata (sharded DB)
Chunks: 4 MB chunks → dedup savings 30–60% typical for consumer data
```

### 3. Architecture: separate metadata from blocks

```
           Desktop/Mobile/Web client (sync engine + local DB of file state)
              │ 1. split file into chunks, hash each (SHA-256)
              │ 2. ask: which chunk hashes are new?
              ▼
 ┌────────────────────────┐        ┌──────────────────────────────┐
 │ METADATA SERVICE       │        │ BLOCK SERVICE / UPLOAD API   │
 │ files, folders, versions│◄──────►│ presigned URLs per chunk     │──► Object storage (S3/GCS)
 │ chunk lists, permissions│        │ resumable multipart          │    chunks by content hash
 │ (sharded SQL: per user/ │        └──────────────────────────────┘    (immutable, deduped)
 │  namespace)             │
 └──────────┬─────────────┘
            │ commit new version (atomic): file X v7 = [h1, h2, h9, h4]
            ▼
   Change log / journal per namespace (cursor-based) ──► Notification svc (long-poll/WebSocket/push)
            │                                                    │ "namespace 42 changed"
            ▼                                                    ▼
   Search index, thumbnail/preview workers, virus scan    Other devices pull changes since cursor
```

### 4. Upload flow (chunked + dedup + resumable)

```
1. Client: file → chunks (fixed 4 MB, or content-defined chunking for better delta) → hash each
2. POST /files/{id}/upload-session { chunkHashes[] } → server replies with MISSING hashes only
3. Client uploads missing chunks directly to object storage (presigned PUTs, parallel, retry each)
4. POST /files/{id}/commit { baseVersion: 6, chunkHashes[...] } → metadata svc atomically creates v7
   (optimistic concurrency: if current version ≠ 6 → conflict)
5. Append to change journal → notify other devices
Resume: interrupted upload → re-ask which chunks are missing → continue
Dedup scope: per user (safer, privacy) or global (bigger savings, but beware "confirmation of file" attacks)
```

### 5. Sync (download side)

```
Each device keeps a CURSOR into the user's change journal (namespace).
Device online: long-poll / WebSocket "changes available" → GET /changes?cursor=c123 → list of changes
  → for each changed file: compare chunk list with local → download only missing chunks → assemble
Device offline for days: same cursor-based catch-up (or full re-scan if cursor too old)
Mobile: sync on demand (download when opened) + background refresh; avoid full mirror to save storage/data
```

### 6. Conflicts

```
Laptop & phone both edit report.docx (base v6) while offline:
  Laptop commits v7 ✓ ; phone commits with baseVersion 6 → CONFLICT (current is v7)
  Resolution: keep both → "report (Aditya's phone conflicted copy).docx" (Dropbox approach)
  Real-time co-editing (Google Docs) uses OT/CRDT instead — different system (Topic P05)
Folder ops conflicts (move vs delete) → server is source of truth; deterministic rules
```

### 7. Data model

```
namespaces(id, owner_id)                         -- a user's drive or a shared drive
files(id, namespace_id, parent_id, name, is_folder, current_version, size, mime, trashed, updated_at)
  UNIQUE(namespace_id, parent_id, name)
file_versions(file_id, version, chunk_hashes[], size, created_by, created_at)
chunks(hash PRIMARY KEY, size, storage_key, ref_count)   -- content-addressed
permissions(file_id, principal(user/group/link), role, expires_at)
journal(namespace_id, seq, file_id, op, version, ts)      -- change log for sync (cursor = seq)
Sharding: by namespace_id (all of a user's metadata together)
```

### 8. Other deep dives
```
Durability: object storage replication (multi-AZ / multi-region), checksums on every chunk, background scrubbing
Versioning & trash: keep N versions / 30 days; garbage-collect chunks when ref_count = 0 (careful, async)
Storage tiering: cold files → infrequent-access / archive tiers
Sharing: ACL checks in metadata service on every op; share links = unguessable tokens with expiry;
         permission changes propagate via journal to collaborators' devices
Security: encryption at rest (KMS), in transit (TLS); optional client-side encryption; virus scanning
Search: index file names, metadata, extracted text (OCR for images/PDFs) asynchronously
Rate & quota: per-user storage quota enforced at commit; bandwidth throttling for sync clients
```

## 🟢 कैसे काम करता है? (Hindi)
1. Client फ़ाइल को 4 MB के टुकड़ों में बाँटकर हर टुकड़े का hash निकालता है; सर्वर बताता है कौन-से टुकड़े नए हैं — सिर्फ़ वही upload (dedup + delta)।
2. टुकड़े presigned URLs से सीधे S3 में; बीच में टूटे तो बाक़ी टुकड़ों से आगे बढ़ो (resume)।
3. Metadata service नया version बनाती है (v7 = टुकड़ों की सूची) — base version न मिले तो conflict।
4. हर बदलाव change journal में; दूसरे devices को सूचना → वो अपने cursor से बदलाव लेकर सिर्फ़ नए टुकड़े download करते हैं।
5. दो devices पर offline बदलाव → "conflicted copy" बनाओ; sharing permissions हर operation पर जाँचो; पुराने versions और trash रखो।

---

## 🟡 Real World Example

**Dropbox** — splits files into 4 MB blocks with content hashing and dedup. It moved storage off S3 to its own exabyte-scale system ("Magic Pocket", 2016), uses a metadata service plus a journal-based sync protocol, and its desktop sync engine was rewritten in Rust ("Nucleus") for correctness.

**Google Drive** — Colossus/Spanner-backed storage. Google Docs editing uses operational transformation, not file sync. Drive for desktop streams files on demand.

**iCloud Drive / OneDrive** — "files on demand" placeholders: the OS shows all files but downloads content only when opened, which saves device storage.

**Indian context (DigiLocker)** — the government document wallet, built on object storage with issuer integrations and secure sharing, at a scale of hundreds of millions of users.

## 🟡 Real Example Hindi में
Dropbox फ़ाइलों को 4 MB blocks में बाँटकर hash से dedup करता है; 2016 में S3 छोड़कर अपना exabyte-स्तर का storage ("Magic Pocket") बनाया और sync engine Rust में दोबारा लिखा।
iCloud/OneDrive "files on demand" से सारी फ़ाइलें दिखाते हैं पर खोलने पर ही download करते हैं। DigiLocker करोड़ों भारतीयों के दस्तावेज़ सुरक्षित रखता है।

---

## 🟠 My Stack Example

### Upload session: tell client which chunks are missing (Node + Postgres)
```js
app.post('/api/v1/files/:id/upload-session', authenticate, async (req, res) => {
  await authz.require(req.user.id, req.params.id, 'editor');
  const hashes = z.array(z.string().regex(/^[a-f0-9]{64}$/)).max(2500).parse(req.body.chunkHashes);   // ≤ 10 GB
  const { rows } = await db.query('SELECT hash FROM chunks WHERE hash = ANY($1)', [hashes]);
  const have = new Set(rows.map((r) => r.hash));
  const missing = hashes.filter((h) => !have.has(h));
  const urls = await Promise.all(missing.map((h) => presignPut(`chunks/${h.slice(0, 2)}/${h}`, 'application/octet-stream', 4 * 1024 * 1024)));
  res.json({ missing: missing.map((h, i) => ({ hash: h, url: urls[i] })) });
});
```

### Commit new version with optimistic concurrency
```js
app.post('/api/v1/files/:id/commit', authenticate, async (req, res) => {
  const { baseVersion, chunkHashes, size } = req.body;
  const result = await withTx(db, async (tx) => {
    const { rows: [f] } = await tx.query('SELECT current_version, namespace_id FROM files WHERE id=$1 FOR UPDATE', [req.params.id]);
    if (f.current_version !== baseVersion) return { conflict: true, current: f.current_version };
    await verifyChunksExist(tx, chunkHashes);                                   // uploaded & checksummed
    const v = baseVersion + 1;
    await tx.query('INSERT INTO file_versions(file_id, version, chunk_hashes, size, created_by) VALUES ($1,$2,$3,$4,$5)',
                   [req.params.id, v, chunkHashes, size, req.user.id]);
    await tx.query('UPDATE files SET current_version=$1, size=$2, updated_at=now() WHERE id=$3', [v, size, req.params.id]);
    await tx.query('UPDATE chunks SET ref_count = ref_count + 1 WHERE hash = ANY($1)', [chunkHashes]);
    await tx.query("INSERT INTO journal(namespace_id, file_id, op, version) VALUES ($1,$2,'update',$3)", [f.namespace_id, req.params.id, v]);
    return { version: v, namespaceId: f.namespace_id };
  });
  if (result.conflict) return res.status(409).json({ error: 'VERSION_CONFLICT', currentVersion: result.current });
  await redis.publish(`ns:${result.namespaceId}`, 'changed');                   // wake other devices
  res.json(result);
});
```

### Change feed for devices (cursor-based)
```js
app.get('/api/v1/changes', authenticate, async (req, res) => {
  const ns = await namespaceOf(req.user.id);
  const cursor = Number(req.query.cursor ?? 0);
  const { rows } = await db.query('SELECT seq, file_id, op, version FROM journal WHERE namespace_id=$1 AND seq > $2 ORDER BY seq LIMIT 1000', [ns, cursor]);
  res.json({ changes: rows, cursor: rows.at(-1)?.seq ?? cursor, hasMore: rows.length === 1000 });
});
```

### Client-side chunking & hashing (React Native / Node desktop)
```ts
async function chunkAndHash(uri: string, size: number) {
  const CHUNK = 4 * 1024 * 1024, chunks = [];
  for (let offset = 0; offset < size; offset += CHUNK) {
    const b64 = await FileSystem.readAsStringAsync(uri, { encoding: 'base64', position: offset, length: Math.min(CHUNK, size - offset) });
    chunks.push({ offset, hash: await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, b64, { encoding: Crypto.CryptoEncoding.HEX }) });
  }
  return chunks;   // (hash raw bytes in production; base64 hashing shown for brevity)
}
```

### Download a version (assemble from chunks via signed URLs)
```python
@app.get("/files/{fid}/download")
async def download(fid: str, user=Depends(current_user)):
    await authz.require(user["id"], fid, "viewer")
    v = await current_version(fid)
    return {"chunks": [{"hash": h, "url": presign_get(chunk_key(h), 300)} for h in v.chunk_hashes], "size": v.size}
```

---

## ⚫ Interview Questions + Answers

**Q1: Why split files into chunks?**
A1: Chunking enables resumable uploads (retry only the failed chunks), parallel transfer, delta sync (when part of a file changes, only the affected chunks are uploaded, especially with content-defined chunking), deduplication (identical chunks across versions or users are stored once by content hash), and easier integrity verification per chunk. The file version is just an ordered list of chunk hashes.

**Q2: How does sync across devices work?**
A2: Each change (create, update, move, delete) is committed to the metadata service and appended to a per-namespace change journal with a monotonically increasing sequence. Devices keep a cursor. A notification channel (long-poll, WebSocket or push) tells them changes exist, and they fetch changes since their cursor, then download only the chunks they lack. Offline devices catch up from their cursor when they reconnect, or do a full rescan if the cursor is too old.

**Q3: How do you handle conflicting edits from two offline devices?**
A3: Commits carry the base version. The metadata service uses optimistic concurrency, so the first commit wins and the second sees a version mismatch. The client then preserves the user's work as a "conflicted copy" file (or offers a merge for supported formats) rather than overwriting. Real-time collaborative documents avoid file-level conflicts by using OT or CRDT co-editing instead of whole-file sync.

**Q4: How would you design storage for exabytes of data cost-effectively?**
A4: Separate metadata (sharded SQL or distributed DB) from content (object storage). Use content-addressed, deduplicated chunks, with compression where useful. Tier storage by access frequency (hot SSD-backed vs infrequent-access vs archive), use erasure coding instead of 3× replication for cold data, and garbage-collect unreferenced chunks safely and asynchronously. Enforce quotas and keep only limited version history. At very large scale, consider building your own storage, as Dropbox did with Magic Pocket.

**Q5: How do you implement sharing securely?**
A5: Store ACLs (user, group or link principal with role and optional expiry) in the metadata service, and check permissions on every metadata and download operation, issuing short-lived presigned URLs only after authorization. Share links use unguessable tokens with optional password and expiry, and can be revoked. Permission changes are propagated via the journal so collaborators' clients update. Audit sharing events, support domain restrictions for organizations, and scan files for malware.

---

## 🔷 Trade-offs
✅ Fixed-size chunks: simple — ❌ insertions shift all chunks (poor delta); content-defined chunking fixes it at CPU cost.
✅ Global dedup: max savings — ❌ privacy side channels; per-user dedup is safer.
✅ Full local mirror: offline access — ❌ device storage; files-on-demand saves space but needs connectivity.
✅ Conflicted copies: no data loss — ❌ user must merge manually.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunking | Splitting files into blocks | फ़ाइल को टुकड़ों में बाँटना |
| Content hash | Hash identifying chunk content | टुकड़े की पहचान hash |
| Deduplication | Store identical chunks once | एक जैसे टुकड़े एक बार |
| Delta sync | Transfer only changed parts | सिर्फ़ बदला हिस्सा भेजना |
| Resumable upload | Continue after interruption | रुकने के बाद आगे से |
| Metadata service | Files, folders, versions, ACLs | फ़ाइलों की जानकारी वाली सेवा |
| Change journal | Ordered log of changes | बदलावों का क्रमबद्ध log |
| Cursor | Device's position in journal | device की journal में जगह |
| Conflicted copy | Saved duplicate on conflict | टकराव पर बनी अलग copy |
| ACL | Access control list | अनुमति सूची |

---

## ⚡ 3-Line Summary
**English:**
1. Separate metadata (files, versions, ACLs, journal) from content (content-addressed chunks in object storage).
2. Upload = chunk + hash → upload only missing chunks (presigned, resumable) → atomic version commit with optimistic concurrency; dedup by hash.
3. Sync via per-namespace change journal + cursors + notifications; conflicts → conflicted copies; ACL checks + short-lived URLs for sharing.

**Hindi:**
1. Metadata (फ़ाइलें, versions, अनुमतियाँ, journal) और content (hash वाले टुकड़े S3 में) अलग।
2. Upload: टुकड़े + hash → सिर्फ़ नए टुकड़े (resume के साथ) → version commit (base version जाँच)।
3. Sync: journal + cursor + सूचना; टकराव पर conflicted copy; sharing में हर बार अनुमति जाँच।

---

## ➡️ Next Topic Suggestion
**121. Video Streaming (YouTube)** — From files to video: next, video upload, transcoding into multiple resolutions, adaptive bitrate streaming (HLS/DASH), CDNs, views counting, and recommendations at YouTube/Netflix scale.
