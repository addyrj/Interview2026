# M21. Media Upload from Mobile (Chunked + Resumable)
# हिंदी में: Mobile से Media Upload — फ़ोटो/वीडियो/documents को टूटते नेटवर्क पर भरोसे से भेजना: फ़ोन पर ही छोटा करना (compress), सीधे S3 पर presigned URL से, फ़ाइल को टुकड़ों (chunks) में भेजना, बीच में रुके तो वहीं से फिर शुरू (resumable), और ऐप background में हो तब भी

---

## 🔵 Simple Definition (English)
Uploading media from phones reliably and cheaply involves:
- **Client-side preparation**: pick or capture (camera, gallery), **compress/resize** images (e.g., 1600 px long edge, JPEG/WebP ~0.7 quality) and **transcode** videos (H.264/HEVC, lower bitrate/resolution), strip EXIF GPS if not needed, and compute a checksum.
- **Direct-to-storage uploads** with **presigned URLs** (S3/GCS/Azure). Bytes go phone → object storage, not through your API servers (Topic 51a).
- **Chunked uploads**: split large files into parts (S3 **multipart upload**: parts ≥ 5 MB except the last, up to 10,000 parts; or the **tus** resumable protocol), upload parts with limited parallelism, and retry only failed chunks.
- **Resumability**: persist upload state (uploadId, completed parts and ETags) in the local DB, so after a network drop, app kill or reboot the upload **continues from the last completed chunk**.
- **Background transfers**: iOS background URLSession and Android WorkManager / foreground service with a progress notification (M04).
- **Finalize & process**: complete the multipart upload, notify the backend with an idempotent API call, then process asynchronously on the server (virus scan, transcoding into adaptive streams, thumbnails, moderation) and show status.

## 🔵 सरल परिभाषा (Hindi)
फ़ोन से media भरोसे और सस्ते में भेजना: (1) फ़ोन पर तैयारी — फ़ोटो छोटी (1600 px, quality ~0.7), वीडियो कम bitrate पर, ज़रूरत न हो तो GPS (EXIF) हटाओ; (2) presigned URL से सीधे S3 पर (आपके API servers से होकर नहीं); (3) बड़ी file को टुकड़ों में (S3 multipart — हर हिस्सा ≥ 5 MB, या tus), सिर्फ़ fail हुआ टुकड़ा दोबारा; (4) upload की स्थिति (uploadId, पूरे हुए हिस्से) local DB में — नेटवर्क टूटे या ऐप बंद हो तो वहीं से आगे; (5) background में भी (iOS URLSession, Android WorkManager); (6) आख़िर में complete + backend को बताओ, सर्वर पर scan, transcoding, thumbnails।

---

## 🔴 Problem it Solves
Users upload from phones constantly: WhatsApp media, Instagram reels, delivery proof photos, KYC documents (Aadhaar/PAN), product photos for sellers (Meesho), insurance claims, YouTube Shorts. Naive single-request uploads fail:
- A 200 MB video over 4G that drops at 95% **restarts from zero**, wasting data, time and patience.
- **App switch or screen lock kills the upload** (M04).
- Uploading 12 MP originals (5–8 MB each) when a 300 KB version suffices **burns data and storage**.
- **Proxying through API servers** ties up app servers and bandwidth, and timeouts kill long uploads.
- **Duplicates** when the user taps "Send" twice or retries after a timeout.
- No progress feedback leads to rage-taps and support tickets.

## 🔴 यह क्यों बना? (Hindi)
फ़ोन से लगातार uploads: WhatsApp media, Instagram reels, delivery की फ़ोटो, KYC documents (Aadhaar/PAN), Meesho sellers की product फ़ोटो, insurance claims। एक ही request वाले upload fail होते हैं: 200 MB वीडियो 95% पर टूटे तो शुरू से; ऐप बदलने या screen lock पर upload मरे; 300 KB काफ़ी हो वहाँ 5–8 MB की original; API servers से होकर भेजना — servers फँसें, timeout; दो बार "Send" = duplicate; progress नहीं तो बार-बार tap और शिकायतें।

---

## 🟢 How it Works — Step by Step

### End-to-end flow (S3 multipart)

```
Phone                                   Backend (Node/FastAPI)                     S3
─────                                   ─────────────────────                     ──
1. pick/capture → compress/transcode
   → file 48 MB, sha256, mime
2. POST /uploads {fileName, size, mime, ─► validate (type, size quota, auth),
   sha256, purpose:"reel", clientId}       create DB row (status=INITIATED,
                                           clientId unique → idempotent)
                                           CreateMultipartUpload ──────────────────► uploadId
                                       ◄── {uploadId, key, partSize: 8 MB, parts: [{n, presignedUrl}, …]}
3. persist upload record in local DB (uploadId, key, partSize, done parts = [])
4. PUT part 1..6 (2–3 in parallel) ──────────────────────────────────────────────► each returns ETag
   after each part: save {partNumber, ETag} locally; retry failed part with backoff
   network lost / app killed → on resume: GET /uploads/:id/parts (ListParts) → skip done → continue
5. POST /uploads/:id/complete {parts:[{n, etag}]} ─► CompleteMultipartUpload ─────► object assembled
                                                    status=UPLOADED → enqueue processing
6. Processing (async): virus scan → transcode (HLS renditions) → thumbnails → moderation →
   status=READY → push/WS event → app shows reel/photo as ready
Abandoned uploads: S3 lifecycle rule AbortIncompleteMultipartUpload after N days (no storage leak)
```

### Choosing chunk size & parallelism

```
S3 minimum part size 5 MB (except last); max 10,000 parts; max object 5 TB (multipart)
Mobile defaults: 5–8 MB parts on 4G/Wi-Fi; smaller (5 MB) on weak networks; adaptive based on measured speed
Parallelism: 2–3 concurrent parts on cellular, 4–6 on Wi-Fi (too many → contention, radio/battery cost)
Small files (< ~10 MB images): single presigned PUT is fine (simpler); retry whole file
tus protocol: PATCH with Upload-Offset → resume at exact byte offset (great for very flaky networks)
```

### Client-side compression guidelines

```
Photos: resize long edge to 1280–2048 px, JPEG/WebP q≈0.7 → 200–600 KB; keep original only if product requires
        (e.g., "HD" option); strip EXIF GPS unless needed (privacy), keep orientation
Videos: transcode to H.264 (compat) or HEVC, 720p/1080p, ~2–5 Mbps; trim before upload; this can take time
        → show "Preparing…" progress; do it natively (AVFoundation/MediaCodec via libraries), not in JS
Docs (KYC): PDF/JPEG; enhance contrast; size limits; validate on server (OCR/KYC vendors)
```

### Reliability, UX & integrity

```
- Upload queue in local DB (like the outbox, M06): status QUEUED → UPLOADING (x/y parts) → UPLOADED → PROCESSING → READY / FAILED
- Background: iOS background URLSession per part; Android WorkManager with network constraint +
  foreground notification "Uploading 3/6 parts…"
- Wi-Fi-only option for large media/backups; pause/resume/cancel controls
- Idempotency: clientId per media; /complete is idempotent; server dedupes by sha256 (optional)
- Integrity: per-part checksums (x-amz-checksum-sha256 / Content-MD5) + whole-file hash verified on server
- Optimistic UI: show local thumbnail immediately in chat/post with progress ring; "Retry" on failure
- Security: presigned URLs short-lived (15 min), scoped to exact key & content-type; private bucket; validate
  file type by magic bytes on server (not just extension); scan for malware; never trust client mime
```

### Speculative/eager upload (UX trick)

```
Start uploading as soon as the user selects media — while they write the caption/apply filters.
If they cancel, abort the upload. When they tap "Post", the media is often already uploaded → instant post.
```

## 🟢 कैसे काम करता है? (Hindi)
1. फ़ोन पर compress (फ़ोटो 1600 px/q 0.7 → कुछ सौ KB, वीडियो 720p/1080p native library से) → `POST /uploads` (size, type, hash, clientId) → backend जाँचकर S3 multipart शुरू करता है और हर हिस्से का presigned URL देता है।
2. Upload का record local DB में; 2–3 हिस्से साथ-साथ PUT; हर हिस्से का ETag save; fail हुआ हिस्सा backoff से दोबारा; नेटवर्क टूटे या ऐप बंद हो तो ListParts से देखकर बाक़ी हिस्से ही भेजो।
3. सब हिस्से पूरे → `/complete` (idempotent) → S3 file जोड़ता है → सर्वर पर async: virus scan, transcoding (HLS), thumbnails, moderation → READY होने पर push/WS से ख़बर; अधूरे uploads S3 lifecycle rule से अपने-आप हटें।
4. Chunk 5–8 MB (कमज़ोर नेटवर्क पर छोटा), cellular पर 2–3 parallel; छोटी images के लिए एक ही presigned PUT; बहुत flaky नेटवर्क के लिए tus (byte offset से resume)।
5. UX और सुरक्षा: local thumbnail + progress तुरंत, Wi-Fi-only विकल्प, pause/retry, background notification; presigned URL 15 मिनट और उसी key/type के लिए, सर्वर पर magic bytes से type जाँच और malware scan; caption लिखते समय ही upload शुरू (eager upload)।

---

## 🟡 Real World Example

**Instagram** — famously starts uploading the photo or video as soon as the user picks it, while they edit filters and write the caption. When they tap Share, the upload is often done, so posting feels instant.

**WhatsApp** — compresses images and videos on the device by default (with an "HD" option), shows local previews with progress immediately, and resumes or retries media uploads after network drops, with end-to-end encrypted media blobs on its servers.

**YouTube & Vimeo** — YouTube offers a resumable upload protocol. Vimeo is a key adopter and contributor to the open **tus** resumable upload protocol, which lets uploads continue from the last byte after interruptions.

**Indian apps (Meesho sellers, delivery proof, KYC)** — seller apps upload multiple product photos over 3G/4G from small towns, delivery partners upload proof-of-delivery photos from basements, and fintech apps upload KYC documents. All benefit from compression, queued resumable uploads and background transfer.

## 🟡 Real Example Hindi में
Instagram फ़ोटो/वीडियो चुनते ही upload शुरू कर देता है — जब तक आप filter और caption करते हैं, upload अक्सर पूरा; Share पर तुरंत post। WhatsApp फ़ोन पर ही compress करता है ("HD" विकल्प के साथ), तुरंत preview + progress, नेटवर्क टूटने पर फिर से।
YouTube का resumable upload protocol और Vimeo का **tus** protocol आख़िरी byte से आगे बढ़ाते हैं; भारत में Meesho sellers की product फ़ोटो, delivery की proof फ़ोटो और KYC documents — सबमें compression, queue और resumable upload ज़रूरी।

---

## 🟠 My Stack Example

### Backend: initiate / presign parts / complete (Node + AWS SDK v3)
```js
import { S3Client, CreateMultipartUploadCommand, UploadPartCommand, CompleteMultipartUploadCommand, ListPartsCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
const s3 = new S3Client({ region: 'ap-south-1' });                       // Mumbai region
const BUCKET = 'quickbite-media-private';
const ALLOWED = new Set(['image/jpeg', 'image/webp', 'video/mp4']);

app.post('/uploads', auth, async (req, res) => {
  const { clientId, size, mime, sha256, purpose } = req.body;
  if (!ALLOWED.has(mime) || size > 500 * 1024 * 1024) return res.status(422).json({ error: { code: 'UNSUPPORTED_MEDIA' } });
  const existing = await Uploads.findByClientId(req.user.id, clientId);  // idempotent initiate
  if (existing) return res.json(await presignRemaining(existing));
  const key = `${purpose}/${req.user.id}/${crypto.randomUUID()}`;
  const { UploadId } = await s3.send(new CreateMultipartUploadCommand({ Bucket: BUCKET, Key: key, ContentType: mime }));
  // (web clients also need bucket CORS with ExposeHeaders: ["ETag"]; native RN apps aren't subject to CORS)
  const partSize = 8 * 1024 * 1024, partCount = Math.ceil(size / partSize);
  const up = await Uploads.create({ userId: req.user.id, clientId, key, uploadId: UploadId, size, mime, sha256, partSize, partCount, status: 'INITIATED' });
  res.json(await presignRemaining(up));
});

async function presignRemaining(up) {
  const done = await s3.send(new ListPartsCommand({ Bucket: BUCKET, Key: up.key, UploadId: up.uploadId }));
  const doneNums = new Set((done.Parts ?? []).map((p) => p.PartNumber));
  const parts = await Promise.all([...Array(up.partCount).keys()].map((i) => i + 1).filter((n) => !doneNums.has(n))
    .map(async (n) => ({ n, url: await getSignedUrl(s3, new UploadPartCommand({ Bucket: BUCKET, Key: up.key, UploadId: up.uploadId, PartNumber: n }), { expiresIn: 900 }) })));
  return { id: up.id, uploadId: up.uploadId, partSize: up.partSize, partCount: up.partCount, parts, completed: [...doneNums] };
}

app.post('/uploads/:id/complete', auth, async (req, res) => {
  const up = await Uploads.get(req.params.id, req.user.id);
  if (up.status !== 'INITIATED') return res.json(up);                        // idempotent
  await s3.send(new CompleteMultipartUploadCommand({ Bucket: BUCKET, Key: up.key, UploadId: up.uploadId,
    MultipartUpload: { Parts: req.body.parts.sort((a, b) => a.n - b.n).map((p) => ({ PartNumber: p.n, ETag: p.etag })) } }));
  await Uploads.update(up.id, { status: 'UPLOADED' });
  await queue.publish('media.uploaded', { uploadId: up.id, key: up.key, mime: up.mime });   // scan → transcode → thumbs
  res.json({ ...up, status: 'UPLOADED' });
});
```

### React Native: compress, then resumable chunked upload with persisted state
```ts
import * as ImageManipulator from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';      // SDK 54+: 'expo-file-system/legacy' for this API

export async function prepareImage(uri: string) {
  const out = await ImageManipulator.manipulateAsync(uri, [{ resize: { width: 1600 } }], { compress: 0.7, format: ImageManipulator.SaveFormat.WEBP });
  return out.uri;                                                          // ~200–500 KB
}

export async function uploadMedia(localUri: string, mime: string, purpose: string) {
  const info = await FileSystem.getInfoAsync(localUri, { size: true }) as any;
  const clientId = uuid();
  await db.runAsync(`INSERT INTO uploads (client_id, uri, mime, size, status) VALUES (?,?,?,?, 'QUEUED')`, [clientId, localUri, mime, info.size]);
  return resumeUpload(clientId, purpose);
}

export async function resumeUpload(clientId: string, purpose: string) {
  const row = await db.getFirstAsync<any>(`SELECT * FROM uploads WHERE client_id=?`, [clientId]);
  const plan = await http.post('/uploads', { clientId, size: row.size, mime: row.mime, purpose }).then((r) => r.data);   // idempotent
  const etags: Record<number, string> = JSON.parse(row.etags ?? '{}');
  const queue = plan.parts.filter((p: any) => !etags[p.n]);
  const workers = Array.from({ length: 3 }, async () => {                  // 3 parallel parts on cellular
    for (let p = queue.shift(); p; p = queue.shift()) {
      const chunkPath = await sliceToTempFile(row.uri, (p.n - 1) * plan.partSize, plan.partSize);   // native helper: read range → temp file
      const etag = await withRetry(async () => {
        const r = await FileSystem.uploadAsync(p.url, chunkPath, { httpMethod: 'PUT',
          uploadType: FileSystem.FileSystemUploadType.BINARY_CONTENT, sessionType: FileSystem.FileSystemSessionType.BACKGROUND });
        if (r.status !== 200) throw new Error(`part ${p.n} ${r.status}`);
        return r.headers.ETag ?? r.headers.etag;
      });
      etags[p.n] = etag;
      await db.runAsync(`UPDATE uploads SET etags=?, status='UPLOADING' WHERE client_id=?`, [JSON.stringify(etags), clientId]);   // persist progress
      emitProgress(clientId, Object.keys(etags).length / plan.partCount);
      await FileSystem.deleteAsync(chunkPath, { idempotent: true });
    }
  });
  await Promise.all(workers);
  const parts = Object.entries(etags).map(([n, etag]) => ({ n: Number(n), etag }));
  const done = await http.post(`/uploads/${plan.id}/complete`, { parts }).then((r) => r.data);
  await db.runAsync(`UPDATE uploads SET status='UPLOADED', server_id=? WHERE client_id=?`, [done.id, clientId]);
  return done;
}
// On app start / connectivity regained: SELECT client_id FROM uploads WHERE status IN ('QUEUED','UPLOADING') → resumeUpload()
```

### S3 lifecycle rule for abandoned multipart uploads (Terraform)
```hcl
resource "aws_s3_bucket_lifecycle_configuration" "media" {
  bucket = aws_s3_bucket.media.id
  rule {
    id     = "abort-incomplete-mpu"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload { days_after_initiation = 3 }
  }
}
```

### Server-side processing worker (FastAPI/Python sketch)
```python
async def on_media_uploaded(evt):
    head = await s3_head(evt["key"])
    kind = sniff_magic_bytes(await s3_range(evt["key"], 0, 64))         # don't trust client mime
    if kind not in {"jpeg", "webp", "mp4"}: return await reject(evt, "BAD_TYPE")
    if not await antivirus_scan(evt["key"]): return await reject(evt, "MALWARE")
    if kind == "mp4":
        await mediaconvert_hls(evt["key"], renditions=[240, 480, 720])      # adaptive streaming (Topic 121)
    await make_thumbnails(evt["key"], widths=[160, 320, 640])
    await moderation_check(evt["key"])
    await mark_ready(evt["uploadId"]); await notify_user(evt["uploadId"])   # push / WebSocket
```

---

## ⚫ Interview Questions + Answers

**Q1: Design video upload for a mobile app on flaky networks.**
A1: On the device, trim and transcode to a reasonable resolution and bitrate natively, compute a hash and create a local upload record. The backend validates the request and starts an S3 multipart upload, returning presigned part URLs (5–8 MB parts). The app uploads 2–3 parts in parallel via background-capable transfers, persists each part's ETag, retries failed parts with backoff, and on interruption resumes by listing completed parts. It then calls an idempotent complete endpoint. The server processes asynchronously (scan, transcode to HLS, thumbnails, moderation) and notifies when ready. The UI shows progress and a pending post, offers a Wi-Fi-only option, and a lifecycle rule cleans abandoned uploads.

**Q2: Why use presigned URLs instead of uploading through your API servers?**
A2: Direct-to-storage uploads offload bandwidth and long-lived connections from application servers to highly scalable object storage. That avoids API timeouts and load-balancer limits for large files, reduces cost and latency (regional endpoints, transfer acceleration), and keeps authorization in your backend (it issues short-lived URLs scoped to a specific key, method and content type). The backend still validates metadata, enforces quotas and processes files after upload via events.

**Q3: How does a resumable upload work after the app is killed?**
A3: Upload state is persisted in local storage: upload ID, object key, part size and completed part numbers with ETags, or a byte offset for tus. On the next launch or when connectivity returns, the app resumes pending uploads, asks the server or S3 which parts are complete (ListParts, or a HEAD for the tus offset), uploads only the remaining parts with fresh presigned URLs, and completes. Background transfer APIs (iOS background URLSession, Android WorkManager) can continue parts even while the app is suspended. Idempotent initiate and complete calls with a client ID prevent duplicates.

**Q4: Should you compress media on the client? What are the trade-offs?**
A4: Usually yes. Resizing photos to 1.5–2K pixels and transcoding videos to a sensible bitrate cuts upload size by 5–20×, saving user data, time and storage costs, and improving success rates on weak networks. The trade-offs are CPU and battery on device, processing time before upload (show progress), some quality loss (offer HD options where needed), and device variability (use native encoders). Keep originals only when the product needs them (photo backup, professional sellers) and still process server-side for standardized renditions.

**Q5: How do you secure user uploads?**
A5: Authenticate initiation and issue short-lived presigned URLs bound to an exact key, content type and size limits. Keep buckets private and serve via signed CDN URLs if content is private. Validate file type by magic bytes server-side, enforce size quotas and rate limits, scan for malware, strip or handle EXIF metadata (GPS privacy), run content moderation for user-generated media, use checksums for integrity, store under unguessable keys, and clean up incomplete uploads with lifecycle rules.

---

## 🔷 Trade-offs
✅ Multipart/tus resumable: survives drops — ❌ more client & server complexity.
✅ Client compression: less data & cost — ❌ device CPU/battery, quality loss.
✅ Direct-to-S3 presigned: scalable — ❌ must handle post-upload validation asynchronously.
✅ Eager upload: instant posting — ❌ wasted uploads if users cancel (abort + lifecycle cleanup).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Presigned URL | Temporary signed upload URL | अस्थायी हस्ताक्षरित URL |
| Multipart upload | Upload file in parts | file को हिस्सों में भेजना |
| Chunk / part | One piece of a file | file का टुकड़ा |
| Resumable upload | Continue after interruption | रुकने के बाद आगे से |
| tus | Open resumable upload protocol | resumable upload protocol |
| ETag (part) | Part identifier for completion | हिस्से की पहचान |
| Transcoding | Convert video format/bitrate | वीडियो format बदलना |
| Magic bytes | File signature for type check | file की असली पहचान |
| Lifecycle rule | Auto-cleanup policy in S3 | अपने-आप सफ़ाई का नियम |
| Eager upload | Start upload before user confirms | पहले से upload शुरू |

---

## ⚡ 3-Line Summary
**English:**
1. Prepare on device (resize/transcode, hash, strip GPS), then upload directly to object storage via short-lived presigned URLs.
2. Large files: S3 multipart (5–8 MB parts, 2–3 parallel) or tus; persist part progress locally, retry per part, resume after kills via ListParts; use background transfers.
3. Finalize idempotently, process async (scan, transcode, thumbnails, moderation), show progress & status, secure with validation and clean up abandoned uploads.

**Hindi:**
1. फ़ोन पर तैयारी (छोटा करो, hash, GPS हटाओ), फिर presigned URL से सीधे S3 पर।
2. बड़ी file: multipart (5–8 MB हिस्से, 2–3 साथ) या tus; हर हिस्से की प्रगति save, सिर्फ़ fail हिस्सा दोबारा, ऐप बंद होने के बाद भी आगे।
3. Idempotent complete, सर्वर पर async processing, progress दिखाओ, जाँच से सुरक्षा, अधूरे uploads साफ़।

---

## ➡️ Next Topic Suggestion
**M22. Crash Reporting + Analytics (Sentry, Firebase)** — The last mobile topic: knowing what happens in the field. Next: crash and ANR reporting, symbolication, breadcrumbs, product analytics events, funnels, and privacy-safe instrumentation for mobile apps.
