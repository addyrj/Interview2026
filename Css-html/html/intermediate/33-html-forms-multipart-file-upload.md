# 33. HTML Forms — Multipart + File Upload
# हिंदी में: HTML Forms — Multipart और File Upload

---

## 🔵 Simple Definition (English)
To upload a file, use `<input type="file">` inside a `<form method="post" enctype="multipart/form-data">`. The `multipart/form-data` encoding splits the request body into separate **parts** (one per field/file), each with its own headers, so binary file data can travel safely together with normal text fields.

## 🔵 सरल परिभाषा (Hindi)
File upload के लिए `<form method="post" enctype="multipart/form-data">` के अंदर `<input type="file">` use करें। `multipart/form-data` encoding request body को अलग-अलग **parts** में बाँट देती है (हर field/file का एक part, अपने headers के साथ), ताकि binary file data और सामान्य text fields साथ में सुरक्षित जा सकें।

---

## 🔴 Problem it Solves
```
DEFAULT FORM ENCODING: application/x-www-form-urlencoded
  name=Aditya&city=Delhi            <- good for text

If you try to send a file this way, the browser sends ONLY the filename
("photo.jpg"), not the bytes. Binary data also cannot be URL-encoded
efficiently (every byte would become %XX, ~3x larger).

multipart/form-data:
  - Sends raw bytes of the file as one part, text fields as other parts.
  - Each part says its own Content-Disposition, filename and Content-Type.
  - Needed for: profile photo, resume PDF, Instagram post, KYC documents.
```

## 🔴 यह क्यों बना? (Hindi)
```
Default form encoding: application/x-www-form-urlencoded
  name=Aditya&city=Delhi            <- text के लिए ठीक

इससे file भेजने पर browser सिर्फ filename ("photo.jpg") भेजता है, file के bytes नहीं।
Binary data को URL-encode करने पर हर byte %XX बन जाता है (~3 गुना बड़ा)।

multipart/form-data:
  - File के असली bytes एक part में, text fields दूसरे parts में।
  - हर part अपना Content-Disposition, filename और Content-Type बताता है।
  - ज़रूरी है: profile photo, resume PDF, Instagram post, KYC documents के लिए।
```

---

## 🟢 How it Works — Step by Step

```
THE FORM RULES (all three required):
  1. method="post"                       (GET cannot carry a body)
  2. enctype="multipart/form-data"       (without it only the filename is sent)
  3. <input type="file" name="avatar">   (needs a name to be submitted)

THREE enctype VALUES:
  application/x-www-form-urlencoded  (default)  text only
  multipart/form-data                           text + files
  text/plain                                    debugging only, rarely used

WHAT THE REQUEST LOOKS LIKE:
  POST /upload HTTP/1.1
  Content-Type: multipart/form-data; boundary=----X123

  ------X123
  Content-Disposition: form-data; name="username"

  Aditya
  ------X123
  Content-Disposition: form-data; name="avatar"; filename="me.png"
  Content-Type: image/png

  <binary bytes of me.png>
  ------X123--
  (Browser generates the boundary. NEVER set Content-Type manually in fetch with FormData,
   or the boundary will be missing.)

FILE INPUT ATTRIBUTES:
  accept=".pdf,.doc,image/*"  hint to the file picker (NOT security; users can bypass)
  multiple                    choose many files
  capture="environment"       on mobile, open the camera directly
  required                    must pick a file
  webkitdirectory             select a whole folder (non-standard but widely supported)

JAVASCRIPT:
  input.files               FileList of File objects (name, size, type, lastModified)
  new FormData(form)        builds the multipart body automatically
  fetch(url, {method:'POST', body: formData})
  URL.createObjectURL(file) instant image preview, no upload needed
  FileReader                read content (readAsDataURL / readAsText)
  XMLHttpRequest            progress events (xhr.upload.onprogress); fetch has no upload progress

SERVER SIDE: Express uses multer, Next.js route handler uses request.formData(),
             Python uses Flask request.files, etc.

VALIDATE ON BOTH SIDES: client (size/type for fast feedback) AND server (real security:
  check size, MIME by content/magic bytes, rename file, store outside web root, virus scan).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Form के तीन ज़रूरी नियम:
  1. method="post"                     (GET में body नहीं होती)
  2. enctype="multipart/form-data"     (नहीं लगाया तो सिर्फ filename जाएगा)
  3. <input type="file" name="avatar"> (name ज़रूरी है)

Request ऐसी दिखती है: Content-Type में boundary होती है, हर field/file एक part में,
file का हिस्सा अपने filename और Content-Type के साथ। Boundary browser खुद बनाता है।
fetch में FormData भेजते समय Content-Type हाथ से न लगाएँ, वरना boundary गायब हो जाएगी।

File input attributes: accept (picker को hint, security नहीं), multiple, capture (mobile camera),
required।

JavaScript: input.files (File objects), new FormData(form), fetch(..., {body: formData}),
URL.createObjectURL(file) से तुरंत preview, upload progress के लिए XMLHttpRequest।

Validation दोनों तरफ करें: client पर तेज़ feedback के लिए, और server पर असली सुरक्षा के लिए
(size, content से type जाँच, file का नाम बदलना, virus scan)।
```

---

## 🟡 Real World Example
**Instagram "New post":** choose photo -> instant preview via `URL.createObjectURL` -> upload with a progress bar. **Zomato "Add review with photos":** `multiple` file input, `accept="image/*"`, each file limited to 5 MB. **Naukri / LinkedIn resume upload:** `accept=".pdf,.doc,.docx"`. **Bank / Paytm KYC:** `capture` opens the phone camera for the document photo. **Gmail attachments:** drag-and-drop zone plus a hidden file input, files uploaded in the background.

## 🟡 Real Example Hindi mein
**Instagram "New post":** photo चुनें -> `URL.createObjectURL` से तुरंत preview -> progress bar के साथ upload। **Zomato "Review with photos":** `multiple` file input, `accept="image/*"`, हर file 5 MB तक। **Naukri / LinkedIn resume upload:** `accept=".pdf,.doc,.docx"`। **Bank / Paytm KYC:** `capture` से phone का camera document photo के लिए खुलता है। **Gmail attachments:** drag-and-drop zone + छुपा file input, files background में upload।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>File Upload Form</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="page">
    <h1>Create profile</h1>

    <!-- enctype is REQUIRED for files; action is a demo endpoint that just echoes -->
    <form id="form" action="https://httpbin.org/post" method="post" enctype="multipart/form-data">

      <label for="name">Name</label>
      <input id="name" name="name" type="text" required>

      <!-- single image, with picker hint -->
      <label for="avatar">Profile photo (max 2 MB)</label>
      <input id="avatar" name="avatar" type="file" accept="image/*" required>
      <img id="preview" class="preview" alt="Selected photo preview" hidden>

      <!-- multiple documents -->
      <label for="docs">Documents (PDF, multiple)</label>
      <input id="docs" name="docs" type="file" accept="application/pdf" multiple>
      <ul id="fileList" class="files"></ul>

      <p id="error" class="error" role="alert"></p>

      <button type="submit">Upload</button>
      <progress id="bar" value="0" max="100" hidden></progress>
    </form>

    <pre id="result"></pre>
  </main>

  <script>
    const MAX = 2 * 1024 * 1024;               // 2 MB client-side limit (server must re-check!)
    const form = document.getElementById('form');
    const avatar = document.getElementById('avatar');
    const preview = document.getElementById('preview');
    const docs = document.getElementById('docs');
    const err = document.getElementById('error');

    // 1. Instant preview with object URL (no upload yet)
    avatar.addEventListener('change', () => {
      const file = avatar.files[0];
      err.textContent = '';
      if (!file) return;
      if (file.size > MAX) {                    // size check
        err.textContent = 'Photo is larger than 2 MB.';
        avatar.value = '';                      // clear the selection
        preview.hidden = true;
        return;
      }
      preview.src = URL.createObjectURL(file);  // blob: URL
      preview.onload = () => URL.revokeObjectURL(preview.src); // free memory after load
      preview.hidden = false;
    });

    // 2. List selected files
    docs.addEventListener('change', () => {
      const list = document.getElementById('fileList');
      list.innerHTML = '';
      for (const f of docs.files) {
        const li = document.createElement('li');
        li.textContent = f.name + ' (' + (f.size / 1024).toFixed(1) + ' KB)';  // textContent = safe
        list.append(li);
      }
    });

    // 3. Upload with progress. XHR is used because fetch cannot report upload progress.
    form.addEventListener('submit', (e) => {
      e.preventDefault();                        // stay on the page
      const data = new FormData(form);           // builds the multipart body for us
      const xhr = new XMLHttpRequest();
      const bar = document.getElementById('bar');
      bar.hidden = false;

      xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable) bar.value = (ev.loaded / ev.total) * 100;
      };
      xhr.onload = () => {
        document.getElementById('result').textContent =
          'Status ' + xhr.status + '\n' + xhr.responseText.slice(0, 400) + '...';
      };
      xhr.onerror = () => { err.textContent = 'Upload failed (offline?)'; };
      xhr.open('POST', form.action);             // do NOT set Content-Type manually
      xhr.send(data);
    });

    /* Simple fetch version (no progress):
       fetch(form.action, { method: 'POST', body: new FormData(form) }); */
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #222; }
.page { max-width: 480px; margin: 0 auto; padding: 24px 16px; }

form { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.1); }
label { display: block; margin: 14px 0 4px; font-weight: 600; font-size: 14px; }
input[type="text"] { width: 100%; padding: 8px 10px; border: 1px solid #bbb; border-radius: 6px; }

/* Style the file button part of the input */
input[type="file"] { width: 100%; font-size: 14px; }
input[type="file"]::file-selector-button {
  padding: 6px 12px; margin-right: 10px; border: 0; border-radius: 6px;
  background: #e0e0e0; cursor: pointer;
}
input[type="file"]::file-selector-button:hover { background: #ccc; }

.preview { display: block; width: 96px; height: 96px; object-fit: cover; border-radius: 50%; margin-top: 8px; }
.files { margin: 8px 0 0; padding-left: 18px; font-size: 14px; }
.error { color: #c62828; min-height: 1.2em; font-size: 14px; }

button { padding: 10px 18px; border: 0; border-radius: 8px; background: #e23744; color: #fff; cursor: pointer; }
progress { display: block; width: 100%; margin-top: 12px; }
pre { white-space: pre-wrap; background: #212121; color: #a5d6a7; padding: 12px; border-radius: 8px; font-size: 12px; }
pre:empty { display: none; }
```

---

## 🟠 React/Next.js Connection

```jsx
"use client";
import { useState } from "react";

export default function Upload() {
  const [preview, setPreview] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);      // picks up all named inputs
    // Do NOT set headers: {'Content-Type': ...}; the browser adds the boundary
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    console.log(await res.json());
  }

  function onPick(e) {
    const file = e.target.files?.[0];
    if (file) setPreview(URL.createObjectURL(file));      // remember to revoke on cleanup
  }

  return (
    <form onSubmit={onSubmit} className="space-y-3">
      {/* File inputs are UNCONTROLLED in React (value cannot be set) */}
      <input name="avatar" type="file" accept="image/*" onChange={onPick} />
      {preview && <img src={preview} alt="preview" className="h-24 w-24 rounded-full object-cover" />}
      <button className="rounded bg-red-600 px-4 py-2 text-white">Upload</button>
    </form>
  );
}
```

```js
// app/api/upload/route.js  (Next.js Route Handler)
export async function POST(request) {
  const formData = await request.formData();            // parses multipart for you
  const file = formData.get("avatar");                   // File object
  if (!(file instanceof File) || file.size > 2 * 1024 * 1024) {
    return Response.json({ error: "Invalid file" }, { status: 400 });   // SERVER validation
  }
  // const bytes = Buffer.from(await file.arrayBuffer()); // save to S3/Cloudinary here
  return Response.json({ name: file.name, size: file.size });
}
```
- Next.js **Server Actions** also accept `FormData` directly: `<form action={uploadAction}>`.
- For big files, upload **directly to S3/Cloudinary** with a pre-signed URL so the file never passes through your server (Vercel has request size limits).
- Libraries: `react-dropzone` (drag-and-drop), `uploadthing`, `multer` (Express).

---

## ⚫ Interview Questions + Answers

Q1: Why do we need `enctype="multipart/form-data"`?
A1: The default urlencoded format cannot carry binary; only the filename would be sent. Multipart splits the body into parts separated by a boundary so raw file bytes and text fields travel together.

Q2: Can you upload files with GET?
A2: No. GET has no body (data would go in the URL). File upload needs POST (or PUT/PATCH with a body).

Q3: Does `accept="image/*"` secure the upload?
A3: No. It only filters the file picker UI. Users can choose "All files" or send a crafted request. Always validate type, size and content on the server.

Q4: How do you upload with `fetch` and why not set `Content-Type`?
A4: `fetch(url, {method:'POST', body: formData})`. The browser sets `multipart/form-data; boundary=...` itself; setting it manually drops the boundary and the server cannot parse the body.

Q5: How do you show a preview and upload progress?
A5: Preview with `URL.createObjectURL(file)` or `FileReader.readAsDataURL`. Progress with `XMLHttpRequest.upload.onprogress` (fetch lacks upload progress). For large files use chunked or pre-signed direct uploads.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: Forgetting `enctype`, so the server receives only the filename.
✅ Correct way: `enctype="multipart/form-data"` and `method="post"`.

❌ Mistake 2: File input without `name`, so nothing is sent.
✅ Correct way: Always give `name`.

❌ Mistake 3: Only client-side validation.
✅ Correct way: Re-validate size, MIME (magic bytes) and extension on the server, rename files, store safely.

❌ Mistake 4: Setting `Content-Type: multipart/form-data` manually in fetch/axios.
✅ Correct way: Let the browser set it with the boundary.

❌ Mistake 5: Not revoking object URLs (memory leak) or trying to set a file input's `value` in React.
✅ Correct way: `URL.revokeObjectURL`; treat file inputs as uncontrolled (clear with a `ref` or `key` change).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| enctype | How form body is encoded | Form data की encoding |
| multipart/form-data | Body split into parts, supports files | File वाला form encoding |
| boundary | Separator string between parts | Parts को अलग करने वाली string |
| FormData | JS object that builds form body | Form body बनाने वाला JS object |
| File / FileList | Selected file objects | चुनी हुई files |
| createObjectURL | Temporary URL for a File | File का अस्थायी URL |
| accept | File picker filter hint | Picker का filter hint |
| Pre-signed URL | Time-limited direct upload link | सीधे upload का अस्थायी link |

---

## ⚡ 3-Line Summary
English: File uploads need `method="post"`, `enctype="multipart/form-data"` and a named `<input type="file">`.
`FormData` builds the multipart body; never set Content-Type manually, and use `createObjectURL` for previews.
`accept` and client checks are only UX; always validate on the server.

Hindi: File upload के लिए `method="post"`, `enctype="multipart/form-data"` और name वाला `<input type="file">` चाहिए।
`FormData` multipart body बनाता है; Content-Type हाथ से न लगाएँ, preview के लिए `createObjectURL` use करें।
`accept` और client checks सिर्फ UX हैं; असली validation server पर ही करें।

---

## ➡️ Next Topic
**34. Picture Tag + Responsive Images** — Files upload करने के बाद उन्हें हर device पर सही size/format में दिखाना।

---
