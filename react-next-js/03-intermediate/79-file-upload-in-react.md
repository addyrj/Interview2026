# 79. File Upload in React
# हिंदी में: React में File Upload

---

## 🔵 Simple Definition (English)
File upload ka matlab hai user ke device se file (image, PDF, CSV) choose karke server ya cloud storage par bhejna. React mein hum `<input type="file">` use karte hain, selected `File` object ko state mein rakhte hain, aur `FormData` ke through `fetch` ya `XMLHttpRequest` se send karte hain.

## 🔵 सरल परिभाषा (Hindi)
File upload का मतलब है user के device से कोई file (image, PDF, CSV) चुनकर server या cloud storage पर भेजना। React में हम `<input type="file">` इस्तेमाल करते हैं, चुनी हुई `File` object को state में रखते हैं, और `FormData` के ज़रिए `fetch` या `XMLHttpRequest` से भेजते हैं।

---

## 🔴 Problem it Solves
Pehle file upload ke liye poora page reload hota tha (HTML form POST). SPA mein bina reload ke upload karna, upload se pehle validation (size, type) karna, progress bar aur preview dikhana zaroori ho gaya. Sabse important baat: client-side validation sirf UX ke liye hai, security ke liye nahi. Server ko bhi har cheez dobara check karna padta hai, kyunki client se koi bhi kuch bhi bhej sakta hai.

## 🔴 यह क्यों बना? (Hindi)
पहले file upload के लिए पूरा page reload होता था (HTML form POST)। SPA में बिना page reload के upload करना, upload से पहले size और type check करना, progress bar और preview दिखाना ज़रूरी हो गया। सबसे ज़रूरी बात: client-side validation सिर्फ user experience के लिए है, security के लिए नहीं। Server को भी हर चीज़ दोबारा check करनी होती है, क्योंकि client से कोई भी कुछ भी भेज सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User <input type="file"> se file choose karta hai
Step 2 → onChange mein e.target.files[0] se File object milta hai
Step 3 → Client validation: type aur size check (UX ke liye)
Step 4 → Valid file ko state mein save karo (file input khud controlled nahi hota)
Step 5 → FormData mein append('avatar', file) karo
Step 6 → fetch POST karo — browser khud multipart/form-data header aur boundary set karta hai
Step 7 → Server validation (magic bytes se type, size limit) aur storage (S3 / Cloudinary / disk)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User <input type="file"> से file चुनता है
Step 2 → onChange में e.target.files[0] से File object मिलता है
Step 3 → Client validation: type और size check (सिर्फ UX के लिए)
Step 4 → Valid file को state में रखो (file input खुद controlled नहीं होता)
Step 5 → FormData में append('avatar', file) करो
Step 6 → fetch से POST करो, browser multipart header और boundary खुद सेट करता है
Step 7 → Server पर फिर से validation (magic bytes से type, size limit) और storage
```

---

## 🟡 Real World Example
**Zomato restaurant owner onboarding:** Restaurant owner apna FSSAI license (PDF, max 5 MB) aur shop photo (JPEG/PNG) upload karta hai. Frontend turant bata deta hai "PDF nahi, sirf JPEG/PNG" aur "5 MB se badi file allowed nahi". Server phir check karta hai ki file sach mein image hai (sirf `.jpg` naam rakhne se kuch nahi hota), aur file S3 bucket mein store hoti hai.

## 🟡 Real Example Hindi mein
**Zomato restaurant owner onboarding:** Restaurant owner अपना FSSAI license (PDF, अधिकतम 5 MB) और shop की photo (JPEG/PNG) upload करता है। Frontend तुरंत बता देता है "PDF नहीं, सिर्फ JPEG/PNG" और "5 MB से बड़ी file allowed नहीं"। Server फिर check करता है कि file सच में image है (सिर्फ `.jpg` नाम रखने से कुछ नहीं होता), और file S3 bucket में store होती है।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';                          // React state hook

// ── BASIC FILE UPLOAD ─────────────────────────────────
const MAX_SIZE_BYTES = 5 * 1024 * 1024;                    // 5 MB limit, in bytes
const ALLOWED_TYPES = ['image/png', 'image/jpeg'];         // allowed MIME types

function AvatarUpload() {
  const [file, setFile] = useState(null);                  // the chosen File object
  const [error, setError] = useState('');                  // validation message for the user
  const [status, setStatus] = useState('');                // "Uploading..." / "Uploaded"

  function handleChange(e) {
    const selected = e.target.files[0];                    // first file from the picker
    if (!selected) return;                                 // user pressed Cancel, nothing chosen
    if (!ALLOWED_TYPES.includes(selected.type)) {          // MIME type reported by the browser
      setError('Only PNG or JPEG allowed');                // tell the user why
      setFile(null);                                       // discard the invalid file
      return;                                              // stop here
    }
    if (selected.size > MAX_SIZE_BYTES) {                  // size is given in bytes
      setError('File must be 5 MB or smaller');            // tell the user why
      setFile(null);                                       // discard the invalid file
      return;                                              // stop here
    }
    setError('');                                          // clear the old error
    setFile(selected);                                     // keep the valid file in state
  }

  async function handleUpload() {
    if (!file) return;                                     // nothing to upload
    const formData = new FormData();                       // builds a multipart/form-data body
    formData.append('avatar', file);                       // field name must match the server
    setStatus('Uploading...');                             // show status text
    try {
      const res = await fetch('/api/avatar', {             // send the POST request
        method: 'POST',                                    // HTTP method
        body: formData,                                    // browser sets the multipart boundary
      });                                                  // do NOT set Content-Type yourself
      setStatus(res.ok ? 'Uploaded ✅' : 'Failed ❌');      // 2xx = success
    } catch {
      setStatus('Network error ❌');                       // fetch throws only on network failure
    }
  }

  return (
    <div>
      <input type="file" accept="image/png,image/jpeg" onChange={handleChange} /> {/* file picker */}
      {error && <p style={{ color: 'red' }}>{error}</p>}  {/* validation message */}
      <button onClick={handleUpload} disabled={!file}>Upload</button> {/* enabled only with a valid file */}
      <p>{status}</p>                                      {/* status text */}
    </div>
  );
}

export default AvatarUpload;                               // make it importable
```

## 💻 Code Example — Advanced

```jsx
import { useEffect, useRef, useState } from 'react';       // hooks we need

// ── Limits in ONE place (client UX; the server enforces them again) ──
const LIMITS = {
  maxBytes: 5 * 1024 * 1024,                               // 5 MB
  types: ['image/png', 'image/jpeg', 'image/webp'],        // allowed MIME types
};

// Pure validation: returns an error message, or null when the file is valid
function validateFile(file) {
  if (!LIMITS.types.includes(file.type)) return 'Only PNG, JPEG or WEBP allowed'; // type check
  if (file.size > LIMITS.maxBytes) return 'File must be 5 MB or smaller';         // size check
  return null;                                             // null = valid
}

// Custom hook: XHR gives upload progress (fetch cannot), and supports abort
function useFileUpload(url) {
  const [progress, setProgress] = useState(0);             // 0 to 100
  const [status, setStatus] = useState('idle');            // idle | uploading | done | error
  const xhrRef = useRef(null);                             // keeps the live request across renders

  function upload(file) {
    const form = new FormData();                           // multipart body
    form.append('avatar', file);                           // field name the server reads
    setStatus('uploading');                                // update UI
    setProgress(0);                                        // reset the bar
    const xhr = new XMLHttpRequest();                      // create the request object
    xhrRef.current = xhr;                                  // store it so cancel() can reach it
    xhr.open('POST', url);                                 // method and URL
    xhr.responseType = 'json';                             // auto-parse JSON responses
    xhr.upload.onprogress = (e) => {                       // fires while bytes are being sent
      if (e.lengthComputable) {                            // total size is known
        setProgress(Math.round((e.loaded / e.total) * 100)); // percent done
      }
    };
    xhr.onload = () => {                                   // request finished (any HTTP status)
      setStatus(xhr.status >= 200 && xhr.status < 300 ? 'done' : 'error'); // 2xx = success
    };
    xhr.onerror = () => setStatus('error');                // network failure
    xhr.onabort = () => setStatus('idle');                 // user cancelled
    xhr.send(form);                                        // start the upload
  }

  function cancel() {
    xhrRef.current?.abort();                               // stop the request (safe if none)
  }

  return { upload, cancel, progress, status };             // expose what the UI needs
}

function AvatarPicker() {
  const { upload, cancel, progress, status } = useFileUpload('/api/avatar'); // hook call
  const [file, setFile] = useState(null);                  // valid File chosen by the user
  const [preview, setPreview] = useState(null);            // blob: URL shown in <img>
  const [error, setError] = useState(null);                // validation message

  // Make a preview URL whenever the chosen file changes
  useEffect(() => {
    if (!file) {                                           // nothing chosen
      setPreview(null);                                    // clear the preview
      return;                                              // no cleanup needed
    }
    const url = URL.createObjectURL(file);                 // temporary in-memory URL
    setPreview(url);                                       // show the preview
    return () => URL.revokeObjectURL(url);                 // free memory on change or unmount
  }, [file]);

  function handleChange(e) {
    const picked = e.target.files[0];                      // first file or undefined
    if (!picked) return;                                   // user cancelled the dialog
    const problem = validateFile(picked);                  // run the rules
    setError(problem);                                     // show the message (or null)
    setFile(problem ? null : picked);                      // keep only valid files
  }

  return (
    <div>
      <input type="file" accept="image/png,image/jpeg,image/webp" onChange={handleChange} /> {/* accept is only a UI hint */}
      {error && <p role="alert">{error}</p>}               {/* validation error */}
      {preview && <img src={preview} alt="Preview" width={120} />} {/* local preview */}
      {status === 'uploading' && <progress value={progress} max={100} />} {/* native progress bar */}
      <button disabled={!file || status === 'uploading'} onClick={() => upload(file)}>
        Upload
      </button>
      {status === 'uploading' && <button onClick={cancel}>Cancel</button>} {/* only while sending */}
      {status === 'done' && <p>Uploaded ✅</p>}            {/* success text */}
    </div>
  );
}

export default AvatarPicker;                               // make it importable
```

---

## 🟠 Real app integration

Next.js App Router Route Handler (server side, the real security check):

```javascript
// app/api/avatar/route.js — Next.js Route Handler (App Router)
const MAX_BYTES = 5 * 1024 * 1024;                         // server-side size limit (never trust the client)
const PNG_SIG = [0x89, 0x50, 0x4e, 0x47];                  // PNG magic bytes
const JPEG_SIG = [0xff, 0xd8, 0xff];                       // JPEG magic bytes

export async function POST(request) {                      // handles POST /api/avatar
  const declared = Number(request.headers.get('content-length') ?? 0); // size claimed by the client
  if (declared > MAX_BYTES + 1024) {                       // reject early, before parsing the body
    return Response.json({ error: 'Too large' }, { status: 413 }); // 413 Payload Too Large
  }
  const formData = await request.formData();               // parse multipart body
  const file = formData.get('avatar');                     // a File, a string, or null
  if (!(file instanceof File)) {                           // must be an uploaded file
    return Response.json({ error: 'No file' }, { status: 400 }); // 400 Bad Request
  }
  if (file.size > MAX_BYTES) {                             // real size check on the parsed file
    return Response.json({ error: 'Too large' }, { status: 413 }); // 413
  }
  const head = new Uint8Array(await file.slice(0, 8).arrayBuffer()); // read only the first 8 bytes
  const startsWith = (sig) => sig.every((byte, i) => head[i] === byte); // compare magic numbers
  if (!startsWith(PNG_SIG) && !startsWith(JPEG_SIG)) {    // real content check, not the file name
    return Response.json({ error: 'Not an image' }, { status: 415 }); // 415 Unsupported Media Type
  }
  // const url = await uploadToS3(file);                   // hand off to real storage (S3 / Cloudinary)
  return Response.json({ ok: true }, { status: 201 });     // 201 Created
}
```

Express with multer (`npm i express multer`):

```javascript
const express = require('express');                        // web framework
const multer = require('multer');                          // multipart/form-data parser
const app = express();                                     // create the app

const upload = multer({
  storage: multer.memoryStorage(),                         // keep the file in RAM (use diskStorage for big files)
  limits: { fileSize: 5 * 1024 * 1024, files: 1 },         // hard limits: 5 MB and one file
  fileFilter: (req, file, cb) => {                         // runs before the file is stored
    const ok = ['image/png', 'image/jpeg'].includes(file.mimetype); // mimetype is client-declared
    cb(null, ok);                                          // false = silently skip this file
  },
});

app.post('/api/avatar', upload.single('avatar'), (req, res) => { // field name must match the client
  if (!req.file) return res.status(400).json({ error: 'No valid file' }); // skipped or missing
  // req.file.buffer holds the bytes; check magic numbers here too, then store it
  res.status(201).json({ ok: true, size: req.file.size });   // respond with metadata
});

app.use((err, req, res, next) => {                         // error middleware
  if (err.code === 'LIMIT_FILE_SIZE') {                    // multer size error
    return res.status(413).json({ error: 'File too large' }); // 413
  }
  res.status(500).json({ error: 'Upload failed' });        // generic message, no stack trace
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `Content-Type` khud set karna
✅ **Correct:** Browser ko boundary set karne do.

```jsx
// Wrong: the server cannot find the multipart boundary
fetch('/api/avatar', {
  method: 'POST',
  headers: { 'Content-Type': 'multipart/form-data' }, // ❌ boundary is missing
  body: formData,
});

// Right: let the browser set the header and boundary
fetch('/api/avatar', {
  method: 'POST',
  body: formData,                                      // ✅ browser adds the boundary
});
```

❌ **Mistake 2:** Sirf file ke naam ya `file.type` par bharosa karna
✅ **Correct:** Server par file ke asli bytes (magic bytes) check karo.

```javascript
// Wrong: the user can rename virus.exe to photo.png
if (file.name.endsWith('.png')) saveFile(file);        // ❌ trivially faked

// Right: read the first bytes and compare with the PNG signature
const head = new Uint8Array(await file.slice(0, 4).arrayBuffer()); // first 4 bytes
const isPng = head[0] === 0x89 && head[1] === 0x50 && head[2] === 0x4e && head[3] === 0x47; // ✅
```

❌ **Mistake 3:** File input ko `value` prop se control karna
✅ **Correct:** File input read-only hai. `onChange` se File state mein save karo, aur reset ke liye `e.target.value = ''` use karo.

```jsx
// Wrong: a file input cannot be set to a File from React state
<input type="file" value={file} />                     // ❌ DOM throws InvalidStateError

// Right: uncontrolled input, state holds the chosen File
<input type="file" onChange={(e) => setFile(e.target.files[0])} /> // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Uploader() {
  const [name, setName] = useState('none');               // shown on screen
  function handleChange(e) {
    e.target.value = '';                                  // step A: clear the input
    const file = e.target.files[0];                       // step B: read the file AFTER clearing
    setName(file ? file.name : 'none');                   // step C: use it
  }
  return <input type="file" onChange={handleChange} />;
}
// Pick "photo.png" in the browser. What is shown in `name`?
```

**Answer:** `name` becomes `'none'`. Setting `input.value = ''` empties the input's list of selected files (the HTML spec says so). So at step B, `e.target.files` is empty and `files[0]` is `undefined`. The code does not crash because of the ternary, but the file name is silently lost. The fix is to read `const file = e.target.files[0]` **before** clearing the input. A `File` object you already hold keeps working after the input is reset.

---

## ⚫ Interview Questions + Answers

**Q1: Why can't a file input be controlled with `value` in React?**
A1: For security, the browser allows only an empty string as the `value` of `<input type="file">`. Setting any other value throws an `InvalidStateError`. So the input stays uncontrolled, and you store the chosen `File` in your own state inside `onChange`.

**Q2: How do you validate a file's size and type, and why isn't client validation enough?**
A2: On the client, check `file.size` (bytes) and `file.type` (MIME) before upload, so the user gets fast feedback. But both values come from the browser or the user's machine and can be faked. The server must check the size limit again and verify the real content (magic bytes), then store the file with a generated name.

**Q3: Why use `FormData` instead of JSON for file uploads?**
A3: JSON cannot carry binary data efficiently. `FormData` sends `multipart/form-data`, which holds the binary file and text fields in one request. The browser writes the boundary header for you, which is why you must not set `Content-Type` yourself.

**Q4: How do you show upload progress?**
A4: `fetch` does not expose upload progress. Use `XMLHttpRequest` and listen to `xhr.upload.onprogress`, which gives `loaded` and `total` bytes. Use `lengthComputable` before dividing.

**Q5: How do you cancel an upload in progress?**
A5: With `fetch`, create an `AbortController`, pass its `signal` to the request, and call `controller.abort()`. With `XMLHttpRequest`, call `xhr.abort()`, which fires `onabort`. Always handle the abort case so the UI returns to idle.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Users upload avatars, documents, or receipts that the server must store
- You need validation messages before the upload starts
- You want progress bars or cancel buttons (use XHR, or fetch with stream helpers)

❌ **Avoid when:**
- Files are very large (hundreds of MB or GB): use a presigned URL (S3) or a resumable protocol (tus) so the browser uploads straight to storage
- You need to upload many files in parallel with retries: a dedicated uploader library is safer
- The file is data the server can receive as text: JSON is simpler

---

## 📊 Visual Diagram

```
Browser                                         Server                    Storage
───────                                         ──────                    ───────
<input type="file">
   │ onChange: File object
   ▼
Client validation (UX only)
   │ type ok? size ok?
   ▼
FormData.append('avatar', file)
   │ POST multipart/form-data  ─────────────►  Re-check size (limit)
   │                                          Check magic bytes (real type)
   │                                          Rename file (UUID)  ──────────►  S3 / disk
   ◄─────────────────────────────────────────  201 Created { url }
Show "Uploaded ✅"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| File object | Browser ka object jo selected file ko represent karta hai | Selected file का browser object |
| FormData | Key-value body builder, file ke saath | File के साथ body बनाने वाला object |
| Multipart | Ek request mein text + binary parts bhejne ka format | एक request में text और binary भेजने का format |
| Boundary | Multipart parts ko alag karne wala separator | Parts को अलग करने वाला separator |
| Magic bytes | File ke shuru ke bytes jo asli type batate hain | File के शुरू के bytes जो असली type बताते हैं |
| Progress event | Upload ke dauran bytes count batane wala event | Upload के दौरान bytes बताने वाला event |

---

## ⚡ 3-Line Summary
**English:**
1. File input ko uncontrolled rakho, `onChange` se `File` state mein save karo, aur `FormData` se bhejo.
2. Client par size/type check UX ke liye hai, server par magic bytes aur size limit security ke liye.
3. Progress chahiye to XHR, cancel ke liye AbortController, aur bahut badi files ke liye presigned URL.

**Hindi:**
1. File input को uncontrolled रखो, `onChange` से `File` को state में save करो, और `FormData` से भेजो।
2. Client पर size/type check UX के लिए है, server पर magic bytes और size limit security के लिए।
3. Progress के लिए XHR, cancel के लिए AbortController, और बहुत बड़ी files के लिए presigned URL।

---

## ➡️ Next Topic
**80. Infinite Scroll in React** — list ke end par automatically next page load karna, IntersectionObserver aur cursor pagination ke saath।
