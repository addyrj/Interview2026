# 51a. Object Storage (AWS S3) ⭐
# हिंदी में: Object Storage — फ़ाइलों (images, videos, PDFs, backups) को "objects" के रूप में असीमित, सस्ते और बहुत टिकाऊ तरीके से रखने की सेवा, जैसे AWS S3

---

## 🔵 Simple Definition (English)
**Object storage** stores data as **objects**: the file bytes + **metadata** + a unique **key**, inside a flat **bucket** (no real folders). You access objects over **HTTP APIs** (PUT/GET/DELETE). It scales to **unlimited** size, is very cheap per GB, and is extremely durable.
**AWS S3** is the standard; alternatives: Google Cloud Storage, Azure Blob, Cloudflare R2, MinIO (self-hosted), DigitalOcean Spaces.

## 🔵 सरल परिभाषा (Hindi)
Object storage में हर फ़ाइल एक "object" है — फ़ाइल का डेटा + जानकारी (metadata) + एक key — जो एक "bucket" में रहती है।
इसे HTTP API से पढ़ते-लिखते हैं। यह असीमित, सस्ता और बहुत टिकाऊ (S3: 99.999999999% durability) होता है — images, videos, backups के लिए सबसे सही जगह।

---

## 🔴 Problem it Solves
Storing user files on your app server's disk (`./uploads`) breaks quickly:
- **Not scalable:** the disk fills up; you can't add servers (files exist on only one).
- **Stateless violation:** a load balancer sends the next request to another server, and the file isn't there.
- **Durability:** the disk dies → files gone. Backups are manual.
- **Bandwidth:** serving videos from the app server consumes CPU and egress.
- **DB is the wrong place:** storing images as BLOBs bloats the DB, slows backups and replication.

Object storage gives **infinite, durable, cheap, HTTP-accessible storage** that every server and client can use, and plugs straight into CDNs.

## 🔴 यह क्यों बना? (Hindi)
सर्वर की disk पर `./uploads` में फ़ाइलें रखो तो disk भरेगी, दूसरे सर्वर पर फ़ाइल नहीं मिलेगी, disk ख़राब हुई तो सब गया। DB में images रखना DB को भारी बना देता है।
S3 जैसी object storage असीमित, टिकाऊ, सस्ती है और हर सर्वर/ऐप HTTP से इस्तेमाल कर सकता है — CDN से भी सीधे जुड़ती है।

---

## 🟢 How it Works — Step by Step

### Data model

```
Bucket: myapp-uploads (region ap-south-1)
  Key                                         Object
  users/42/avatar.jpg                     →   bytes + metadata (Content-Type: image/jpeg, size, ETag,
  orders/9001/invoice.pdf                       custom x-amz-meta-*, storage class, version id)
  videos/abc/720p/segment_001.ts
"/" in keys LOOKS like folders, but the namespace is flat (prefixes).
```

### Block vs File vs Object storage

```
┌──────────────┬───────────────────────────┬──────────────────────────┬────────────────────────────┐
│              │ Block (EBS)               │ File (EFS/NFS)           │ Object (S3)                │
├──────────────┼───────────────────────────┼──────────────────────────┼────────────────────────────┤
│ Access       │ attached disk to 1 VM     │ shared filesystem (POSIX)│ HTTP API (GET/PUT)         │
│ Unit         │ blocks                    │ files & directories      │ objects (key + metadata)   │
│ Scale        │ fixed size volumes        │ grows, shared            │ unlimited                  │
│ Latency      │ lowest (µs–ms)            │ ms                       │ tens of ms                 │
│ Update       │ in-place byte writes      │ in-place                 │ replace whole object       │
│ Use          │ DB data files, OS disk    │ shared configs, legacy   │ media, backups, logs, data │
│              │                           │ apps, ML datasets        │ lakes, static websites     │
└──────────────┴───────────────────────────┴──────────────────────────┴────────────────────────────┘
```

### Direct upload from client with presigned URL (THE pattern)

```
 RN App / Browser                 Your API (Node/FastAPI)                     S3
     │ 1. POST /uploads {type, size}   │                                        │
     │────────────────────────────────►│ 2. validate (auth, type, size limit)   │
     │                                 │    create presigned PUT URL (5 min)    │
     │◄──── {url, key} ────────────────│                                        │
     │ 3. PUT file bytes directly ─────────────────────────────────────────────►│
     │◄──────────────────────────────────────────────────────── 200 OK ─────────│
     │ 4. POST /uploads/complete {key} │                                        │
     │────────────────────────────────►│ 5. save key in DB, trigger processing  │
                                         (or S3 Event → SQS/Lambda: resize, virus scan, transcode)
Server never handles the file bytes → no bandwidth/memory load; scales infinitely.
```

### Durability & consistency

```
Durability 99.999999999% (11 nines): object stored redundantly across ≥3 AZs.
  (Store 10 million objects → expect to lose 1 every ~10,000 years.)
Availability: 99.99% (Standard)
Consistency: strong read-after-write for PUTs and DELETEs (since Dec 2020) and LIST.
```

### Storage classes & lifecycle (cost)

```
S3 Standard            → hot data, frequent access            ~$0.023/GB-month
S3 Intelligent-Tiering → auto moves between tiers by access   (good default for unknown patterns)
S3 Standard-IA         → infrequent access, cheaper storage, retrieval fee
S3 Glacier Instant/Flexible/Deep Archive → archives, minutes–hours retrieval, ~$0.001/GB-month

Lifecycle rule example:
  logs/*      → IA after 30 days → Glacier after 90 days → delete after 365 days
  uploads/tmp/* → delete after 1 day (abandoned uploads)
  abort incomplete multipart uploads after 7 days
```

### Other important features

```
Multipart upload     → large files in parts (≥5 MB each), parallel, resumable; required > 5 GB
Versioning           → keep old versions; protects from overwrite/delete mistakes
Object Lock / WORM   → can't delete for N days (compliance, ransomware protection)
Encryption           → SSE-S3 / SSE-KMS by default; HTTPS in transit
Block Public Access  → ON by default; serve via CloudFront + OAC instead of public bucket
Event notifications  → ObjectCreated → SQS / SNS / Lambda / EventBridge (async processing)
Replication          → cross-region replication (DR, latency)
Key design           → no hot-prefix limits anymore (3,500 PUT / 5,500 GET per sec PER PREFIX,
                       scales automatically by adding prefixes)
```

## 🟢 कैसे काम करता है? (Hindi)
1. फ़ाइल bucket में एक key (जैसे `users/42/avatar.jpg`) के साथ object बनकर रहती है; "folders" सिर्फ़ नाम का हिस्सा हैं।
2. Upload का सही तरीका: ऐप API से presigned URL माँगता है → फ़ाइल सीधे S3 पर भेजता है → API में सिर्फ़ key सेव होती है।
3. S3 हर object को कम से कम 3 AZ में रखता है — 11 nines durability।
4. पुराने डेटा को lifecycle rule से सस्ती storage (IA, Glacier) में भेजो या delete करो।
5. Bucket को public मत करो — CloudFront (OAC) या signed URLs से फ़ाइलें दो; upload होते ही S3 event से resize/scan चलाओ।

---

## 🟡 Real World Example

**Netflix** — the entire video library (masters and encoded versions) lives in S3. Encoding pipelines read from and write to S3, and the encoded files are pushed to Open Connect CDN boxes.

**Airbnb / Pinterest / Instagram-style apps** — every photo upload goes to object storage. Thumbnails and resized versions are generated asynchronously from S3 events and served through a CDN.

**Data lakes (Swiggy, Flipkart, Uber)** — event logs and analytics data are stored as Parquet files in S3 and queried with Athena, Spark, Presto or Trino. S3 is the cheapest durable store for petabytes.

**Capital One breach (2019)** — a misconfigured WAF allowed SSRF to fetch IAM credentials from instance metadata, and the attacker downloaded 100M customer records from S3 buckets. Lesson: least-privilege IAM, IMDSv2, and bucket policies matter.

## 🟡 Real Example Hindi में
Netflix की पूरी video library S3 में है। Instagram जैसे ऐप में हर फ़ोटो S3 में जाती है, और S3 event से thumbnails बनते हैं जो CDN से दिखते हैं।
2019 में Capital One में ग़लत setting से हैकर ने S3 से 10 करोड़ ग्राहकों का डेटा निकाल लिया — इसलिए IAM permissions कम से कम रखो।

---

## 🟠 My Stack Example

### Node.js (AWS SDK v3) — presigned upload URL
```js
import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
const s3 = new S3Client({ region: 'ap-south-1' });

const ALLOWED = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp' };

app.post('/api/v1/uploads', auth, async (req, res) => {
  const { contentType, size } = req.body;
  if (!ALLOWED[contentType]) return res.status(415).json({ error: 'Unsupported type' });
  if (size > 10 * 1024 * 1024) return res.status(413).json({ error: 'Max 10 MB' });

  const key = `users/${req.user.id}/uploads/${crypto.randomUUID()}.${ALLOWED[contentType]}`;
  const url = await getSignedUrl(s3, new PutObjectCommand({
    Bucket: process.env.UPLOAD_BUCKET, Key: key, ContentType: contentType, ContentLength: size,
  }), { expiresIn: 300 });

  res.json({ url, key });
});

app.post('/api/v1/uploads/complete', auth, async (req, res) => {
  const { key } = req.body;
  if (!key.startsWith(`users/${req.user.id}/`)) return res.sendStatus(403);   // ownership check
  await db.query('UPDATE users SET avatar_key = $1 WHERE id = $2', [key, req.user.id]);
  res.json({ avatarUrl: `https://cdn.myapp.com/${key}` });
});

// private download (invoice) → short-lived presigned GET
const invoiceUrl = await getSignedUrl(s3, new GetObjectCommand({ Bucket: B, Key: `orders/${id}/invoice.pdf` }), { expiresIn: 60 });
```

### FastAPI (boto3)
```python
s3 = boto3.client("s3", region_name="ap-south-1")

@app.post("/uploads")
async def presign(body: UploadIn, user=Depends(current_user)):
    key = f"users/{user.id}/uploads/{uuid4()}.jpg"
    post = s3.generate_presigned_post(
        Bucket=BUCKET, Key=key, ExpiresIn=300,
        Conditions=[["content-length-range", 1, 10 * 1024 * 1024], {"Content-Type": "image/jpeg"}],
        Fields={"Content-Type": "image/jpeg"})
    return {"post": post, "key": key}      # presigned POST enforces size limit server-side
```

### React Native — upload directly to S3
```ts
const { url, key } = await api.post('/api/v1/uploads', { contentType: 'image/jpeg', size: file.size }).then(r => r.data);
await FileSystem.uploadAsync(url, file.uri, {                        // expo-file-system
  httpMethod: 'PUT', uploadType: FileSystem.FileSystemUploadType.BINARY_CONTENT,
  headers: { 'Content-Type': 'image/jpeg' },
});
await api.post('/api/v1/uploads/complete', { key });
// For big videos: multipart upload with per-part presigned URLs → resumable on flaky networks (Topic M21)
```

### Async processing on upload (S3 event → SQS → worker)
```
S3 ObjectCreated (prefix users/) → SQS queue → Node/Python worker:
  - virus scan (ClamAV), validate real MIME type (magic bytes, not just header)
  - generate thumbnails 150/400/1080 px WebP (sharp / Pillow)
  - write to processed/ prefix, update DB status = READY
  - push notification / WebSocket "your photo is ready"
```

### Local dev: MinIO (S3-compatible) in Docker
```yaml
minio:
  image: minio/minio
  command: server /data --console-address ":9001"
  ports: ["9000:9000", "9001:9001"]
  environment: { MINIO_ROOT_USER: minio, MINIO_ROOT_PASSWORD: minio123 }
# S3Client({ endpoint: 'http://localhost:9000', forcePathStyle: true, credentials: {...} })
```

### Bucket security checklist
```
✓ Block Public Access ON; serve via CloudFront + Origin Access Control
✓ IAM: app role can only s3:PutObject/GetObject on its prefix
✓ Default encryption (SSE-S3/KMS); TLS-only bucket policy (aws:SecureTransport)
✓ Versioning on important buckets; lifecycle for tmp and old versions
✓ Validate type/size; never trust client filename; random keys (no enumeration)
✓ CORS configured only for your domains (needed for browser direct upload)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is object storage and how is it different from block and file storage?**
A1: Object storage keeps data as immutable objects (bytes + metadata + key) in a flat namespace, accessed via HTTP APIs. It scales without limit, is cheap and very durable, but has higher latency and no in-place edits. Block storage (EBS) provides raw disks attached to one machine, with the lowest latency, used for databases and OS disks. File storage (EFS/NFS) provides a shared hierarchical filesystem for multiple machines. Use object storage for media, backups, logs and data lakes.

**Q2: How do you design file uploads from a mobile app at scale?**
A2: The client asks the API for a presigned URL (the API authenticates the user, validates type and size, and generates a random key scoped to that user). The client uploads directly to S3, using multipart with per-part presigned URLs for large files, which allows resume and parallel parts. On completion the client notifies the API, or an S3 event triggers processing (virus scan, MIME validation, thumbnails or transcoding) via a queue. Store only the key and metadata in the DB, and serve files through a CDN (signed URLs if private). Lifecycle rules clean up abandoned uploads.

**Q3: How durable is S3 and how is that achieved?**
A3: S3 Standard is designed for 99.999999999% (11 nines) durability. Objects are stored redundantly across multiple devices in at least three Availability Zones, with checksums and automatic repair of lost copies. Durability is different from availability (99.99%) and doesn't protect against your own deletes or overwrites. Use versioning, Object Lock, replication and backups for that.

**Q4: How would you reduce S3 storage costs for a large media app?**
A4: Use lifecycle policies to move older objects to cheaper classes (Standard-IA, Glacier) or Intelligent-Tiering for unknown access patterns. Delete temporary and abandoned uploads, incomplete multipart uploads, and old versions after N days. Compress and transcode media to efficient formats (WebP/AVIF, H.265/AV1). Deduplicate by content hash. Serve via CDN to reduce request and egress costs, and use VPC endpoints so internal traffic doesn't go through the NAT gateway. Review S3 Storage Lens.

**Q5: How do you serve private user files (like invoices or paid videos) securely?**
A5: Keep the bucket private with Block Public Access. When an authorized user requests a file, the API checks permissions and returns a short-lived presigned GET URL, or a CloudFront signed URL or cookie for CDN delivery. Use non-guessable keys, encrypt at rest (SSE-KMS for sensitive data), log access, and keep expiry times short. For video, use HLS with signed URLs and optional segment encryption or DRM.

---

## 🔷 Trade-offs
✅ Advantages:
- Unlimited scale, very cheap, 11 nines durability, HTTP-accessible, integrates with CDN and events.
- Makes app servers stateless; direct client uploads offload servers.

❌ Disadvantages:
- Higher latency than disks; no partial in-place updates (rewrite whole object).
- Not a filesystem (no atomic rename of folders, listing is prefix-based).
- Misconfiguration (public buckets, broad IAM) → major breaches.
- Request and egress costs can surprise at high volumes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Object storage | Store data as objects via HTTP | HTTP से फ़ाइलें रखने का तरीका |
| Bucket | Container of objects | objects का डिब्बा |
| Key | Unique name/path of object | object का नाम |
| Presigned URL | Temporary signed access link | अस्थायी हस्ताक्षरित लिंक |
| Multipart upload | Upload big file in parts | बड़ी फ़ाइल टुकड़ों में |
| Storage class | Price/performance tier | storage का स्तर |
| Lifecycle policy | Auto move/delete rules | अपने आप move/delete नियम |
| Durability | Data won't be lost | डेटा नहीं खोएगा |
| Versioning | Keep old versions | पुराने version रखना |
| OAC | CloudFront-only access to bucket | सिर्फ़ CDN से bucket access |

---

## ⚡ 3-Line Summary
**English:**
1. Object storage (S3) stores files as objects in buckets via HTTP — unlimited, cheap, 11-nines durable.
2. Upload directly from clients with presigned URLs; process asynchronously via S3 events; serve via CDN.
3. Keep buckets private, least-privilege IAM, lifecycle rules for cost, versioning for safety.

**Hindi:**
1. S3 = bucket में objects, HTTP से — असीमित, सस्ता, बहुत टिकाऊ।
2. Upload सीधे ऐप से presigned URL द्वारा; प्रोसेसिंग S3 event से; दिखाना CDN से।
3. Bucket प्राइवेट, कम permissions, ख़र्च के लिए lifecycle, सुरक्षा के लिए versioning।

---

## ➡️ Next Topic Suggestion
**52. Consistent Hashing** — CDNs, caches and sharded databases all need to decide "which node holds this key?" without reshuffling everything when nodes change. Next: consistent hashing and virtual nodes.
