# 112. Multer — File Uploads
# हिंदी में: Multer — File Upload Handling

---

## 🔵 Simple Definition (English)
**Multer** is an Express middleware for handling `multipart/form-data` — the encoding used by HTML forms and clients to upload files. It parses incoming file uploads, makes them available on `req.file` (single) or `req.files` (multiple), and can save them to disk or hand them off to cloud storage (S3) as in-memory buffers.

## 🔵 सरल परिभाषा (Hindi)
**Multer** एक Express middleware है जो `multipart/form-data` handle करता है — वो encoding जो HTML forms और clients file upload के लिए use करते हैं। ये incoming file uploads parse करता है, उन्हें `req.file` (single) या `req.files` (multiple) पर available कराता है, और disk पर save कर सकता है या cloud storage (S3) को in-memory buffers के रूप में hand off कर सकता है।

---

## 🔴 Problem it Solves
Express's built-in `express.json()` and `express.urlencoded()` body parsers CANNOT parse `multipart/form-data` — the content type required for file uploads (binary data mixed with text fields). Without Multer, `req.body` would be empty/undefined for file upload requests, and there'd be no way to access the uploaded binary file data. Multer bridges this gap, parsing the multipart stream and exposing structured file metadata (originalname, mimetype, size, buffer/path).

## 🔴 यह क्यों बना? (Hindi)
Express के built-in `express.json()` और `express.urlencoded()` body parsers `multipart/form-data` parse नहीं कर सकते — वो content type जो file uploads के लिए ज़रूरी है (binary data text fields के साथ mixed)। Multer के बिना, file upload requests के लिए `req.body` empty/undefined रहेगा, और uploaded binary file data access करने का कोई तरीका नहीं होगा। Multer इस gap को bridge करता है, multipart stream parse करके structured file metadata (originalname, mimetype, size, buffer/path) expose करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends a form with `enctype="multipart/form-data"`, containing file(s) plus optionally other text fields.
Step 2 → Multer middleware (`.single('fieldname')`, `.array()`, or `.fields()`) is applied to the specific route.
Step 3 → Multer streams the multipart body, extracting each part (file or field), and applies the configured `storage` engine (disk or memory).
Step 4 → For disk storage, the file is written to the configured directory with a generated filename; for memory storage, the file content is kept as a `Buffer` in RAM.
Step 5 → Metadata is attached to `req.file` (single upload) or `req.files` (multiple), and non-file fields land in `req.body` as usual; the route handler then processes or persists the file (e.g., uploading the buffer to S3).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client `enctype="multipart/form-data"` वाला form भेजता है, जिसमें file(s) और optionally अन्य text fields होते हैं।
Step 2 → Multer middleware (`.single('fieldname')`, `.array()`, या `.fields()`) specific route पर apply होता है।
Step 3 → Multer multipart body stream करता है, हर part (file या field) extract करता है, और configured `storage` engine (disk या memory) apply करता है।
Step 4 → Disk storage के लिए, file configured directory में generated filename से लिखी जाती है; memory storage के लिए, file content RAM में `Buffer` के रूप में रहता है।
Step 5 → Metadata `req.file` (single upload) या `req.files` (multiple) पर attach होता है, और non-file fields सामान्य रूप से `req.body` में जाते हैं; route handler फिर file को process या persist करता है (जैसे buffer को S3 पर upload करना)।

---

## 🟡 Real World Example
**Swiggy restaurant onboarding — menu image upload:** When a restaurant partner uploads their menu photo or FSSAI license document through Swiggy's partner portal, the form sends `multipart/form-data` with the image file plus text fields (`restaurantId`, `documentType`). Multer, configured with memory storage (not disk — since the server is often stateless/containerized), captures the file as a `Buffer`, validates its mimetype (`image/jpeg`, `image/png`, `application/pdf` only) and size (max 5MB), then the route handler uploads the buffer directly to AWS S3 and saves the resulting S3 URL in the database — the file never touches the container's local disk, which is important since containers can be ephemeral and horizontally scaled.

## 🟡 Real Example Hindi mein
**Swiggy restaurant onboarding — menu image upload:** जब कोई restaurant partner Swiggy के partner portal से अपना menu photo या FSSAI license document upload करता है, form `multipart/form-data` भेजता है image file और text fields (`restaurantId`, `documentType`) के साथ। Multer, memory storage के साथ configured (disk नहीं — क्योंकि server अक्सर stateless/containerized होता है), file को `Buffer` के रूप में capture करता है, mimetype validate करता है (सिर्फ `image/jpeg`, `image/png`, `application/pdf`) और size (max 5MB), फिर route handler buffer को directly AWS S3 पर upload करता है और resulting S3 URL को database में save करता है — file container की local disk को छूती ही नहीं, जो important है क्योंकि containers ephemeral और horizontally scaled होते हैं।

---

## 💻 Code Example — Basic

```javascript
// multer-basic.js
const express = require('express');
const multer = require('multer'); // npm install multer

const app = express();

// Disk storage: save uploaded files to a local 'uploads' folder
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/'); // folder must already exist
  },
  filename: (req, file, cb) => {
    // Generate a unique filename to avoid collisions: timestamp + original name
    const uniqueName = `${Date.now()}-${file.originalname}`;
    cb(null, uniqueName);
  },
});

const upload = multer({ storage });

// Single file upload under form field name 'avatar'
app.post('/upload-avatar', upload.single('avatar'), (req, res) => {
  // req.file contains metadata about the uploaded file
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  res.json({
    message: 'File uploaded successfully',
    filename: req.file.filename,
    size: req.file.size, // size in bytes
    mimetype: req.file.mimetype,
  });
});

app.listen(3000, () => console.log('Server on port 3000 — POST a file to /upload-avatar'));
```

## 💻 Code Example — Advanced

```javascript
// multer-advanced.js — Memory storage + validation + S3 upload + multiple files
const express = require('express');
const multer = require('multer');
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3'); // npm install @aws-sdk/client-s3

const app = express();
const s3 = new S3Client({ region: 'ap-south-1' }); // Mumbai region, India

// ─── 1. MEMORY STORAGE — keeps file as Buffer, no local disk write ────────────
const storage = multer.memoryStorage();

// ─── 2. FILE FILTER — reject disallowed mimetypes before processing ──────────
const fileFilter = (req, file, cb) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
  if (!allowedTypes.includes(file.mimetype)) {
    // Reject with an error — multer surfaces this to the error-handling middleware
    return cb(new Error('Only JPEG, PNG, and PDF files are allowed'), false);
  }
  cb(null, true); // accept file
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024, // max 5 MB per file
    files: 3, // max 3 files in a single request
  },
});

// ─── 3. MULTIPLE FILES UPLOAD + S3 PERSISTENCE ────────────────────────────────
app.post('/restaurant/documents', upload.array('documents', 3), async (req, res, next) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No documents uploaded' });
    }

    // Upload each file buffer to S3 in parallel
    const uploadPromises = req.files.map(async (file) => {
      const key = `restaurant-docs/${Date.now()}-${file.originalname}`;
      await s3.send(
        new PutObjectCommand({
          Bucket: 'swiggy-partner-docs',
          Key: key,
          Body: file.buffer, // in-memory buffer, never touched disk
          ContentType: file.mimetype,
        })
      );
      return `https://swiggy-partner-docs.s3.ap-south-1.amazonaws.com/${key}`;
    });

    const urls = await Promise.all(uploadPromises);
    res.json({ message: 'Documents uploaded', urls });
  } catch (err) {
    next(err); // pass to Express error-handling middleware
  }
});

// ─── 4. MULTER-SPECIFIC ERROR HANDLING ────────────────────────────────────────
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({ error: 'File too large. Max 5MB allowed.' });
    }
    if (err.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json({ error: 'Too many files. Max 3 allowed.' });
    }
    return res.status(400).json({ error: err.message });
  }
  if (err) {
    return res.status(400).json({ error: err.message }); // fileFilter rejection
  }
  next();
});

app.listen(3000, () => console.log('S3 upload server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const multer = require('multer');
const app = express();

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 2 * 1024 * 1024 }, // 2MB limit
});

app.use(express.json()); // for routes WITHOUT file uploads (multer handles its own route)

// Mixed form: profile photo (file) + name/bio (text fields) in one request
app.put('/api/users/:id/profile', upload.single('photo'), async (req, res, next) => {
  try {
    const { name, bio } = req.body; // text fields, parsed by multer alongside the file
    const photoBuffer = req.file?.buffer; // file, if provided (optional upload)

    const updateData = { name, bio };
    if (photoBuffer) {
      updateData.photoUrl = await uploadToS3(photoBuffer, req.file.mimetype); // helper function
    }

    const user = await User.findByIdAndUpdate(req.params.id, updateData, { new: true });
    res.json({ user });
  } catch (err) {
    next(err);
  }
});

app.listen(4000, () => console.log('Profile update API running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using disk storage in a horizontally-scaled/containerized environment
✅ Correct: Disk storage writes files to the LOCAL filesystem of whichever server instance handled the request — in a multi-instance deployment, a file saved on server A isn't visible to server B. Use memory storage + immediately push to shared cloud storage (S3) instead.

```javascript
// Wrong — in a 3-instance deployment, file lands only on the instance that got the request
const upload = multer({ dest: 'uploads/' });

// Right — memory storage, then upload to shared S3 bucket accessible by all instances
const upload = multer({ storage: multer.memoryStorage() });
// ... then await s3.send(new PutObjectCommand({ Body: req.file.buffer, ... }))
```

❌ Mistake 2: Not validating file type/size, allowing arbitrary uploads
✅ Correct: Always set `fileFilter` and `limits` — without them, users could upload executables disguised as images, or massive files that exhaust disk/memory (a DoS vector).

```javascript
// Wrong — no restrictions, accepts anything of any size
const upload = multer({ storage });

// Right — restrict type and size explicitly
const upload = multer({
  storage,
  fileFilter: (req, file, cb) => cb(null, file.mimetype.startsWith('image/')),
  limits: { fileSize: 5 * 1024 * 1024 },
});
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const multer = require('multer');
const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.post('/upload', upload.single('file'), (req, res) => {
  console.log(req.body); // what does this print if the client sends a text field 'caption' too?
  res.json({ ok: true });
});
app.listen(3000);
```
If the client sends a multipart form with a file field `file` AND a text field `caption=hello`, but you forgot to call `upload.single('file')` and used plain `express.json()` instead — what would `req.body` and `req.file` be?

Answer: With plain `express.json()` (which only parses `application/json` bodies), a `multipart/form-data` request would result in `req.body` being an **empty object `{}`** and `req.file`/`req.files` being `undefined` entirely — `express.json()` silently ignores content types it doesn't understand rather than throwing an error. This is a classic gotcha: developers see an empty body and assume the client didn't send data, when really the wrong body-parsing middleware was used. With Multer's `upload.single('file')` correctly applied, `req.body.caption` would correctly be `'hello'` (text fields parsed alongside the file) and `req.file` would contain the file's buffer/metadata.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `multer.diskStorage()` and `multer.memoryStorage()`?
A1: `diskStorage` writes uploaded files directly to a configured directory on the server's local filesystem, giving you `req.file.path`. `memoryStorage` keeps the entire file in RAM as a `Buffer`, giving you `req.file.buffer` — no disk I/O. Memory storage is preferred when immediately forwarding to cloud storage (S3) or when running in ephemeral/containerized environments; disk storage is simpler for apps that genuinely need local file persistence, but risks running out of disk space for large/many uploads and doesn't work well with horizontal scaling.

Q2: What do `.single()`, `.array()`, and `.fields()` do differently in Multer?
A2: `.single(fieldname)` expects exactly one file under that field name, available as `req.file` (singular, not an array). `.array(fieldname, maxCount)` expects multiple files under the SAME field name, available as `req.files` (an array). `.fields([{name, maxCount}, ...])` handles multiple DIFFERENT field names each potentially with multiple files, available as `req.files` (an object keyed by field name, each value an array).

Q3: How do you limit file upload size and reject files exceeding it?
A3: Pass `limits: { fileSize: <bytes> }` to `multer()`. If a file exceeds this, Multer throws a `MulterError` with `code === 'LIMIT_FILE_SIZE'`, which must be caught by Express's error-handling middleware (4-argument `(err, req, res, next)`) to return an appropriate `413 Payload Too Large` response instead of crashing or hanging.

Q4: Why can't `express.json()` or `express.urlencoded()` parse file uploads?
A4: Those parsers handle `application/json` and `application/x-www-form-urlencoded` content types respectively — both are text-based encodings for simple key-value data. File uploads use `multipart/form-data`, a different encoding that splits the body into distinct "parts" separated by boundary markers, each part potentially containing binary data with its own headers (Content-Disposition, Content-Type). This requires specialized streaming parsing logic that Multer (built on the `busboy` library) provides.

Q5: How would you validate that an uploaded "image" file is actually an image and not a renamed malicious file?
A5: Checking `file.mimetype` alone isn't fully trustworthy since it's derived from the client-provided `Content-Type` header, which can be spoofed. For stronger validation: (1) check the file's magic bytes/signature (e.g., using a library like `file-type` that inspects the actual binary header rather than trusting the claimed mimetype), (2) re-process the file through an image library (e.g., `sharp`) which would fail/throw on non-image binary data, effectively validating it, and (3) still enforce `fileFilter` + size limits as a first-pass, cheap rejection layer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Handling any file upload in Express (profile pictures, documents, menu images, attachments)
- Need to validate, limit, and process uploaded files before persisting them
- Building forms with mixed file + text field submissions

❌ Avoid when:
- Uploading very large files (videos, large datasets) directly through the app server — better to use pre-signed S3 URLs so the client uploads directly to S3, bypassing your server entirely (saves server bandwidth/memory)
- Streaming use cases where you want to process file chunks as they arrive rather than buffering (Multer's memory storage buffers the whole file before your handler runs)

---

## 📊 Visual Diagram
```
MULTER FILE UPLOAD FLOW:

  Client (form, multipart/form-data)
     │  file: menu.jpg
     │  field: restaurantId=42
     ▼
  Multer middleware (upload.single('file'))
     │
     ├── parses multipart stream (busboy under the hood)
     ├── applies fileFilter (mimetype check)
     ├── applies limits (size, count)
     │
     ▼
  storage engine
     ├── diskStorage  → writes to local 'uploads/' folder → req.file.path
     └── memoryStorage → keeps Buffer in RAM           → req.file.buffer
     │
     ▼
  req.file = { originalname, mimetype, size, buffer/path }
  req.body = { restaurantId: '42' }  (non-file fields)
     │
     ▼
  Route handler → upload buffer to S3 / save path reference in DB
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multer | Express middleware for multipart/form-data | File upload handling middleware |
| multipart/form-data | Encoding for file + text uploads | File+text uploads की encoding |
| diskStorage | Saves files to local disk | Files को local disk पर save करना |
| memoryStorage | Keeps files as in-memory Buffer | Files को RAM में Buffer रखना |
| fileFilter | Validates file type before accepting | File type validate करना |
| limits | Max file size/count constraints | Max size/count की सीमा |
| req.file / req.files | Parsed uploaded file(s) metadata | Uploaded file(s) का metadata |

---

## ⚡ 3-Line Summary
English:
1. Multer parses `multipart/form-data` requests, exposing uploaded files as `req.file`/`req.files` and other fields as `req.body`.
2. Use memory storage + direct upload to S3 for scalable/containerized deployments; disk storage only for simple single-server apps.
3. Always set `fileFilter` and `limits` to prevent malicious or oversized uploads, and handle `MulterError` in error middleware.

Hindi:
1. Multer `multipart/form-data` requests parse करता है, uploaded files को `req.file`/`req.files` पर और अन्य fields को `req.body` पर expose करता है।
2. Scalable/containerized deployments के लिए memory storage + direct S3 upload use करो; disk storage सिर्फ simple single-server apps के लिए।
3. हमेशा `fileFilter` और `limits` set करो malicious या oversized uploads रोकने के लिए, और error middleware में `MulterError` handle करो।

---

## ➡️ Next Topic
**113. Serving Static Files** — Using `express.static()` to serve CSS, JS, images, and other assets।
