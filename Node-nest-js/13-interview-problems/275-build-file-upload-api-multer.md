# 275. Build File Upload API (Multer)
# हिंदी में: Multer से File Upload API बनाना

---

## 🔵 Simple Definition (English)
**Multer** is Express middleware for handling `multipart/form-data` — the encoding used when uploading files from HTML forms or mobile apps. It parses the incoming file stream, validates it (size, type), and saves it to disk or memory before your route handler runs.

## 🔵 सरल परिभाषा (Hindi)
**Multer** Express middleware है जो `multipart/form-data` handle करता है — ये encoding file upload (HTML forms, mobile apps) में use होती है। ये incoming file stream parse करता है, validate करता है (size, type), और route handler चलने से पहले disk या memory में save करता है।

---

## 🔴 Problem it Solves
Express's built-in `express.json()` only parses JSON bodies — it cannot handle binary file data mixed with form fields (`multipart/form-data`). Parsing multipart data manually means dealing with raw buffer boundaries, content-disposition headers, and streaming large files without exhausting memory — genuinely tricky low-level work. Multer abstracts all of this: it streams uploaded files directly to disk (or memory for small files), enforces size/type limits, and exposes parsed files as `req.file`/`req.files`.

## 🔴 यह क्यों बना? (Hindi)
Express का built-in `express.json()` सिर्फ JSON bodies parse करता है — binary file data (`multipart/form-data`) handle नहीं कर सकता। Multipart data manually parse करना मुश्किल काम है — raw buffer boundaries, content-disposition headers, बड़ी files को memory खत्म किए बिना stream करना। Multer ये सब abstract करता है: files को directly disk पर stream करता है, size/type limits लगाता है, parsed files को `req.file`/`req.files` में expose करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install and configure Multer with a **storage engine**: `diskStorage` (saves to filesystem with custom filename logic) or `memoryStorage` (keeps file as a Buffer in RAM — good for small files or piping straight to cloud storage).
Step 2 → Define a **fileFilter** function to reject disallowed file types (e.g. only images) BEFORE the file is fully written.
Step 3 → Set **limits** (`fileSize`, `files` count) to prevent abuse (someone uploading a 5GB file to exhaust disk).
Step 4 → Attach Multer as middleware on the specific route: `.single('fieldname')` for one file, `.array('fieldname', maxCount)` for multiple, `.fields([...])` for mixed named fields.
Step 5 → Inside the route handler, `req.file` (single) or `req.files` (multiple) contains metadata: `originalname`, `mimetype`, `size`, `path`/`buffer`.
Step 6 → For production, upload the file onward to cloud storage (S3, Cloudinary) rather than keeping it on the app server's local disk (ephemeral in containers, doesn't scale across instances).
Step 7 → Handle Multer-specific errors (`MulterError`) distinctly — e.g. `LIMIT_FILE_SIZE` should return a clear 413 to the client.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Multer को **storage engine** के साथ configure करो: `diskStorage` या `memoryStorage`।
Step 2 → **fileFilter** function बनाओ disallowed file types reject करने के लिए।
Step 3 → **limits** (`fileSize`, `files`) set करो abuse रोकने के लिए।
Step 4 → Multer को specific route पर middleware की तरह attach करो: `.single()`, `.array()`, `.fields()`।
Step 5 → Route handler में `req.file`/`req.files` में metadata मिलता है।
Step 6 → Production में file को cloud storage (S3, Cloudinary) पर आगे upload करो, local disk पर नहीं।
Step 7 → Multer-specific errors (`MulterError`) अलग से handle करो — जैसे `LIMIT_FILE_SIZE` पर clear 413 response।

---

## 🟡 Real World Example
**Zomato's** restaurant onboarding flow lets owners upload menu photos and FSSAI license documents. The API uses Multer with `memoryStorage` (files are small, <5MB), a `fileFilter` restricting to `image/jpeg`, `image/png`, `application/pdf`, and a `fileSize` limit of 5MB. Accepted files are immediately streamed to an S3 bucket from the buffer — never written to the Node server's local disk, since Zomato runs multiple ECS container instances behind a load balancer and local disk storage wouldn't be accessible from other instances.

## 🟡 Real Example Hindi mein
**Zomato** का restaurant onboarding flow owners को menu photos और FSSAI license documents upload करने देता है। API Multer `memoryStorage` use करता है, `fileFilter` से `image/jpeg`, `image/png`, `application/pdf` तक restrict करता है, 5MB `fileSize` limit। Accepted files buffer से directly S3 bucket में stream होती हैं — local disk पर कभी नहीं लिखी जातीं, क्योंकि Zomato multiple ECS container instances चलाता है जहाँ local disk दूसरे instances से accessible नहीं होती।

---

## 💻 Code Example — Basic

```javascript
// basic-upload.js — minimal single-file upload with disk storage
// npm install express multer
// Run: node basic-upload.js, then test with:
// curl -F "photo=@/path/to/image.jpg" http://localhost:3000/upload

const express = require('express');
const multer = require('multer');
const app = express();

// Save uploaded files to ./uploads/ with a timestamp-prefixed name
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, 'uploads/'), // folder must exist
  filename: (req, file, cb) => {
    // Avoid filename collisions: prefix with timestamp
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});

const upload = multer({ storage });

// 'photo' must match the form field name the client sends
app.post('/upload', upload.single('photo'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  res.json({
    message: 'File uploaded successfully',
    filename: req.file.filename,
    size: req.file.size,
    mimetype: req.file.mimetype,
  });
});

app.listen(3000, () => console.log('Upload server on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-upload.js — production pattern: memory storage + validation + S3 upload
// npm install express multer aws-sdk (or @aws-sdk/client-s3 for v3 SDK)

const express = require('express');
const multer = require('multer');
const app = express();

const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

const upload = multer({
  storage: multer.memoryStorage(), // keep file as Buffer, don't write to disk
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: 3, // max 3 files per request
  },
  fileFilter: (req, file, cb) => {
    // Reject BEFORE the file is fully buffered — saves bandwidth/memory
    if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
      return cb(new multer.MulterError('LIMIT_UNEXPECTED_FILE', file.fieldname));
    }
    cb(null, true); // accept
  },
});

// Mock "upload to S3" function — in real code, use @aws-sdk/client-s3's PutObjectCommand
async function uploadToS3(buffer, filename, mimetype) {
  // await s3Client.send(new PutObjectCommand({ Bucket, Key: filename, Body: buffer, ContentType: mimetype }));
  console.log(`[mock] Uploaded ${filename} (${buffer.length} bytes, ${mimetype}) to S3`);
  return `https://my-bucket.s3.amazonaws.com/${filename}`;
}

app.post(
  '/api/documents/upload',
  upload.array('documents', 3), // field name 'documents', max 3 files
  async (req, res, next) => {
    try {
      if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'At least one file is required' });
      }

      // Upload each file to S3 in parallel
      const uploadResults = await Promise.all(
        req.files.map((file) => {
          const key = `documents/${Date.now()}-${file.originalname}`;
          return uploadToS3(file.buffer, key, file.mimetype);
        })
      );

      res.status(201).json({
        message: `${uploadResults.length} file(s) uploaded`,
        urls: uploadResults,
      });
    } catch (err) {
      next(err); // forward to error handler
    }
  }
);

// ─── Multer-specific error handling ────────────────────────────────────────
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    const messages = {
      LIMIT_FILE_SIZE: 'File too large (max 5MB)',
      LIMIT_FILE_COUNT: 'Too many files',
      LIMIT_UNEXPECTED_FILE: 'File type not allowed',
    };
    return res.status(413).json({ error: messages[err.code] || 'Upload error' });
  }
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(3000, () => console.log('Advanced upload server on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Mixed-field upload: avatar (1 file) + gallery (up to 5 files) in one request
const express = require('express');
const multer = require('multer');
const app = express();

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 10 * 1024 * 1024 } });

app.post(
  '/api/profile',
  upload.fields([
    { name: 'avatar', maxCount: 1 },
    { name: 'gallery', maxCount: 5 },
  ]),
  (req, res) => {
    const avatar = req.files.avatar?.[0];
    const gallery = req.files.gallery || [];
    res.json({
      avatarReceived: !!avatar,
      galleryCount: gallery.length,
    });
  }
);

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `fileFilter` or `limits` — any file type/size accepted
✅ Correct: Always restrict mimetype and set a `fileSize` limit — unrestricted uploads are a common attack/abuse vector (disk exhaustion, malicious file execution).

```javascript
// Wrong: accepts ANYTHING, unlimited size
const upload = multer({ dest: 'uploads/' });

// Right: explicit limits and type filtering
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    cb(null, file.mimetype.startsWith('image/'));
  },
});
```

❌ Mistake 2: Trusting the client-supplied `mimetype`/filename blindly
✅ Correct: `file.mimetype` comes from the client's `Content-Type` header — it can be spoofed (a `.exe` renamed with `image/png` mimetype). For strict security, verify actual file content with a library like `file-type` that inspects magic bytes.

```javascript
// Wrong: trusting req.file.mimetype as the final word on file safety
if (req.file.mimetype === 'image/png') { /* assume it's really a PNG */ }

// Right: verify actual content for security-sensitive uploads
const FileType = require('file-type');
const type = await FileType.fromBuffer(req.file.buffer);
if (!type || type.mime !== 'image/png') {
  return res.status(400).json({ error: 'File content does not match claimed type' });
}
```

---

## 🧠 Tricky Interview Question

```javascript
// What happens if the client sends a file LARGER than the fileSize limit?
const upload = multer({ limits: { fileSize: 1024 } }); // 1KB limit
app.post('/upload', upload.single('file'), (req, res) => {
  res.json({ received: true }); // does this line ever run?
});
```
Answer: No — if the uploaded file exceeds `fileSize`, Multer throws a `MulterError` with code `LIMIT_FILE_SIZE` BEFORE your route handler executes. Multer streams the file while enforcing the limit (it doesn't wait for the full upload to complete before checking) — the moment the limit is exceeded, it aborts the stream and passes the error to Express's next registered error-handling middleware (4-argument `(err, req, res, next)`). If no such error handler exists, Express's default error handler sends a generic 500 — which is why defining a custom Multer error handler (as in the advanced example) is essential for returning a proper 413 with a clear message.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `diskStorage` and `memoryStorage` in Multer, and when would you use each?
A1: `diskStorage` writes the file directly to the server's local filesystem as it streams in — good for large files since it doesn't hold the whole file in RAM, but ties the file to that specific server instance (problematic for horizontally-scaled/containerized apps where local disk isn't shared). `memoryStorage` buffers the entire file in RAM as a `Buffer`, exposed via `req.file.buffer` — convenient for immediately forwarding to cloud storage (S3) without a disk round-trip, but risky for very large files (can exhaust memory under concurrent uploads) — hence pairing it with a strict `fileSize` limit.

Q2: How would you validate that an uploaded file is actually an image, not just that its extension/mimetype claims so?
A2: Client-supplied `mimetype` and filename extension are untrustworthy (easily spoofed). Proper validation reads the file's "magic bytes" (the first few bytes of the actual binary content that identify the true file format) using a library like `file-type`. For images specifically, you can also attempt to process the buffer with `sharp` — if it fails to parse as a valid image, reject it. This defends against disguised-executable attacks.

Q3: How do you handle very large file uploads (e.g. 500MB videos) without exhausting server memory?
A3: Use `diskStorage` (not `memoryStorage`) so Multer streams directly to disk in chunks rather than buffering in RAM. For truly massive files or scale, better architecture is to have the CLIENT upload directly to cloud storage using a **pre-signed URL** (the Node server generates a time-limited S3 upload URL and returns it to the client, which then PUTs the file directly to S3, bypassing the Node server entirely for the actual bytes) — this avoids the Node server being a bottleneck/single point of failure for large transfers.

Q4: What security risks exist in file upload endpoints, and how does Multer config mitigate them?
A4: Risks: (1) Disk/storage exhaustion via large or many files — mitigated by `limits.fileSize` and `limits.files`. (2) Malicious file execution if uploads are served from a path that's also executable — mitigate by serving uploads from a separate, non-executable static directory/CDN, never the app's own code directory. (3) Path traversal via crafted filenames (`../../etc/passwd`) — mitigate by NEVER using the client-supplied filename directly for storage; generate your own safe filename (UUID/timestamp). (4) Content-type spoofing — mitigate with magic-byte verification as in Q2.

Q5: How would you show upload progress to the client for a large file?
A5: Pure Express/Multer on the server side doesn't provide built-in progress events to the CLIENT (Multer processes the request once fully received by Node's HTTP layer in most configurations). For real progress feedback, the client-side `XMLHttpRequest`/`fetch` with a `ProgressEvent` listener on the upload (`xhr.upload.onprogress`) is the typical approach, OR use the pre-signed-URL-to-S3 pattern where the client uploads directly and tracks progress against S3's response, decoupling it from the Node server entirely.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Handling any `multipart/form-data` file upload in an Express app (profile photos, documents, CSVs)
- You need validation (type/size) before accepting files into your system
- Small-to-medium files that fit comfortably through your app server

❌ Avoid when:
- Extremely large files (multi-GB) at scale — use direct-to-S3 pre-signed URLs instead of routing bytes through your Node server
- You're building a non-Express framework (Fastify, NestJS have their own file-upload plugins, though some wrap Multer internally)

---

## 📊 Visual Diagram
```
CLIENT                    EXPRESS + MULTER                  STORAGE
──────                    ────────────────                  ───────
<form multipart/form-data>
  file: photo.jpg
        │
        │ POST /upload
        ▼
  ┌─────────────────┐
  │ Multer middleware │
  │ 1. fileFilter()   │──reject if bad type──► 400/413 response
  │ 2. check limits    │──reject if too big───► 413 response
  │ 3. stream to:      │
  │   diskStorage ─────┼──────────────────────► local disk (uploads/)
  │   OR                │
  │   memoryStorage ────┼──► req.file.buffer ──► manually upload to S3
  └─────────┬────────┘
            ▼
      req.file / req.files populated
            ▼
      your route handler runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| multipart/form-data | Encoding for file + form field uploads | File + form fields upload की encoding |
| diskStorage | Multer engine saving files to filesystem | Files को filesystem में save करने वाला Multer engine |
| memoryStorage | Multer engine keeping files as Buffer in RAM | Files को RAM में Buffer की तरह रखने वाला engine |
| fileFilter | Function to accept/reject files by type | File type के आधार पर accept/reject करने वाला function |
| MulterError | Error type for upload-specific failures | Upload-specific failures का error type |
| Pre-signed URL | Time-limited direct-upload URL to cloud storage | Cloud storage पर direct upload के लिए time-limited URL |

---

## ⚡ 3-Line Summary
English: 1. Multer parses `multipart/form-data`, exposing uploaded files as `req.file`/`req.files` with built-in size/type restriction support. 2. Use `memoryStorage` + immediate cloud upload for scalable, container-friendly architectures; `diskStorage` for simple single-server setups. 3. Always set `fileFilter` and `limits`, and verify actual file content (not just claimed mimetype) for security-sensitive uploads.
Hindi: 1. Multer `multipart/form-data` parse करता है, files को `req.file`/`req.files` में expose करता है, built-in size/type restrictions के साथ। 2. Scalable architectures के लिए `memoryStorage` + immediate cloud upload; simple single-server setups के लिए `diskStorage`। 3. हमेशा `fileFilter` और `limits` set करो, और security-sensitive uploads के लिए actual file content verify करो।

---

## ➡️ Next Topic
**276. Build Real-Time Chat (Socket.io)** — Socket.io से real-time bidirectional chat application बनाना।
