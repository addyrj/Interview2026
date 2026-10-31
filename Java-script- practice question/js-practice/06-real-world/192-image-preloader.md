---

# Q192. Build Image Preloader
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build `preloadImages(urls, ImageCtor)` that loads all images in advance and resolves with a result list `{ url, ok }` — a broken image must not reject the whole batch. Inject `ImageCtor` (`Image` in browsers) for Node testing.

```javascript
const results = await preloadImages(['a.png', 'b.png'], Image);
```

---

## 💡 Quick Concept (2 lines only)
Wrap each `new Image()` in a promise (`onload` -> ok, `onerror` -> not ok) and combine with `Promise.all`.
हिंदी: हर image को promise में लपेटो; error आए तो भी batch न रुके, बस ok:false दर्ज करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function preloadImage(url, ImageCtor) {
  return new Promise((resolve) => {              // never rejects -> batch stays safe
    const img = new ImageCtor();                 // Step 1: create image object
    img.onload = () => resolve({ url, ok: true });   // Step 2: success
    img.onerror = () => resolve({ url, ok: false }); // failure is data, not exception
    img.src = url;                               // Step 3: setting src starts the download
  });
}

function preloadImages(urls, ImageCtor) {
  return Promise.all(urls.map((u) => preloadImage(u, ImageCtor))); // Step 4: load in parallel
}

// ============================================
// TEST CASES
// ============================================

// Fake Image: "downloads" for 10ms, fails if url contains "bad"
class FakeImage {
  set src(url) {
    setTimeout(() => (url.includes('bad') ? this.onerror() : this.onload()), 10);
  }
}

preloadImages(['a.png', 'bad.png', 'c.png'], FakeImage).then((results) => {
  console.log(results);
  // Expected:
  // [ { url: 'a.png', ok: true }, { url: 'bad.png', ok: false }, { url: 'c.png', ok: true } ]
  console.log(results.filter((r) => r.ok).length); // Expected: 2
});
```

---

## 🔍 Why This Works (3 lines max)
Browsers cache an image once downloaded, so later `<img>` tags show instantly. Resolving on error keeps `Promise.all` from failing fast.
हिंदी: एक बार download होने पर image cache हो जाती है, और error पर भी resolve करने से बाकी images नहीं रुकतीं।

---

## ⚡ Alternative Solution
```javascript
// Use Promise.allSettled + img.decode() (browser) for decoded-ready images
const loadOne = async (url) => { const i = new Image(); i.src = url; await i.decode(); return i; };
const settled = await Promise.allSettled(urls.map(loadOne)); // each: fulfilled / rejected
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: set src BEFORE handlers -> fast cached images may fire onload before it's attached
img.src = url; img.onload = done;

// ✅ Correct: attach onload/onerror first, then set src
img.onload = done; img.src = url;
```

---

## 🎯 Interview Tip (1 line)
Mention parallel vs limited concurrency, attach handlers before `src`, and `Promise.allSettled`.

---

## 🔗 Related Questions
→ Q093 (Promise.allSettled) | Q191 (lazy loader) | Q203 (limit concurrent promises) | Q228 (lazy load images)
