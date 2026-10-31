---

# Q235. File Drag + Drop Upload
# Category: DOM Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Create a drop zone where users can drag image files (or click to browse). Validate type (images only) and size (max 2MB), show previews, and upload via `FormData`.

---

## 💡 Quick Concept (2 lines only)
Read files from `e.dataTransfer.files` on `drop`, validate them, preview with `URL.createObjectURL`, and send using `FormData` + `fetch`.
हिंदी: `drop` पर `dataTransfer.files` से files लो, validate करो, preview दिखाओ और `FormData` से upload करो।

---

## ✅ Answer / Solution

```html
<div id="drop" style="border:2px dashed gray;padding:24px">Drop images here or click</div>
<input id="file" type="file" accept="image/*" multiple hidden>
<div id="previews"></div>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Prevent default drag behaviors (else browser opens file)
// Step 2: handleFiles validates + previews + uploads
// Step 3: Support click-to-browse via hidden input

const drop = document.getElementById('drop');            // drop area
const fileInput = document.getElementById('file');       // hidden input
const previews = document.getElementById('previews');    // preview container
const MAX = 2 * 1024 * 1024;                             // 2MB limit

['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) => { // all drag events
  drop.addEventListener(evt, (e) => e.preventDefault()); // stop browser default
});
drop.addEventListener('dragover', () => drop.classList.add('over'));    // highlight
drop.addEventListener('dragleave', () => drop.classList.remove('over')); // unhighlight

drop.addEventListener('drop', (e) => {                   // files dropped
  drop.classList.remove('over');                         // reset style
  handleFiles(e.dataTransfer.files);                     // process
});
drop.addEventListener('click', () => fileInput.click()); // click -> file dialog
fileInput.addEventListener('change', () => handleFiles(fileInput.files)); // browse result

function handleFiles(fileList) {
  const valid = [];                                      // accepted files
  for (const file of fileList) {                         // FileList is iterable
    if (!file.type.startsWith('image/')) { console.warn('Not image:', file.name); continue; } // type check
    if (file.size > MAX) { console.warn('Too big:', file.name); continue; }                  // size check
    valid.push(file);                                    // accept
    const img = document.createElement('img');           // preview element
    img.src = URL.createObjectURL(file);                 // temporary blob URL
    img.width = 80;                                      // small preview
    img.onload = () => URL.revokeObjectURL(img.src);     // free memory
    previews.appendChild(img);                           // show
  }
  if (valid.length) upload(valid);                       // send accepted files
}

async function upload(files) {
  const body = new FormData();                           // multipart body
  files.forEach((f) => body.append('files', f));         // add each file
  const res = await fetch('/upload', { method: 'POST', body }); // do NOT set Content-Type manually
  console.log('upload status', res.status);              // result
}

// ============================================
// TEST CASES
// ============================================

// Test 1: drop a 500KB .png      -> Expected: preview appears, POST /upload sent
// Test 2: drop a .pdf            -> Expected: warn "Not image: file.pdf", no upload
// Test 3: drop a 5MB .jpg        -> Expected: warn "Too big: file.jpg"
// Test 4: drop without preventDefault (remove handlers) -> Expected: browser navigates to the file
```

---

## 🔍 Why This Works (3 lines max)
Cancelling default drag events lets the page handle the drop instead of the browser. File metadata (`type`, `size`) is available before upload, so we validate client-side. `FormData` builds a multipart request automatically.
हिंदी: Default रोकने से browser file नहीं खोलता, और `FormData` multipart body खुद बना देता है।

---

## ⚡ Alternative Solution
```javascript
// Upload progress with XMLHttpRequest (fetch has no upload progress)
const xhr = new XMLHttpRequest();                        // create request
xhr.upload.onprogress = (e) => console.log(Math.round((e.loaded / e.total) * 100) + '%'); // percent
xhr.open('POST', '/upload');                             // set target
xhr.send(formData);                                      // send body
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: setting Content-Type manually breaks multipart boundary
fetch('/upload', { method: 'POST', body: fd, headers: { 'Content-Type': 'multipart/form-data' } });

// ✅ Correct: let the browser set Content-Type with the boundary
fetch('/upload', { method: 'POST', body: fd });
```

---

## 🎯 Interview Tip (1 line)
Say: "preventDefault on dragover/drop, validate type and size client AND server side, revoke object URLs, and use XHR or chunking for progress."

---

## 🔗 Related Questions
→ Q225 (drag and drop) | Q234 (form validation) | Q220 (stream large data)
