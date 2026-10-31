---

# Q228. Lazy Load Images
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Lazy load images: keep the real URL in `data-src` and set `src` only when the image is about to enter the viewport.

---

## 💡 Quick Concept (2 lines only)
Put the real URL in `data-src`, observe each image, and copy it to `src` when it is near the viewport.
हिंदी: असली URL `data-src` में रखो और image दिखने से पहले उसे `src` में डालो।

---

## ✅ Answer / Solution

```html
<img class="lazy" data-src="https://picsum.photos/400/300?1" width="400" height="300" alt="one">
<img class="lazy" data-src="https://picsum.photos/400/300?2" width="400" height="300" alt="two">
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Select all images with class lazy
// Step 2: Observer swaps data-src -> src when near viewport
// Step 3: Fallback to loading all when IntersectionObserver is missing

const images = document.querySelectorAll('img.lazy');    // all lazy images

function loadImage(img) {
  img.src = img.dataset.src;                             // start real download
  img.removeAttribute('data-src');                       // cleanup
  img.classList.remove('lazy');                          // mark as loaded
}

if ('IntersectionObserver' in window) {                  // modern browsers
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {                         // each changed image
      if (!entry.isIntersecting) return;                 // skip if not near view
      loadImage(entry.target);                           // load it
      obs.unobserve(entry.target);                       // stop watching
    });
  }, { rootMargin: '200px 0px' });                       // start 200px before visible
  images.forEach((img) => observer.observe(img));        // observe all
} else {
  images.forEach(loadImage);                             // fallback: load everything
}

// ============================================
// TEST CASES
// ============================================

// Test 1: on page load, images below fold -> img.getAttribute('src') // Expected: null
// Test 2: scroll near an image -> img.src // Expected: its data-src URL
// Test 3: Network tab -> Expected: request for an image starts only after scroll
// Test 4: document.querySelectorAll('img.lazy').length // Expected: decreases as images load
```

---

## 🔍 Why This Works (3 lines max)
Without a `src` the browser makes no request. The observer sets it just before the image becomes visible, saving bandwidth. `width/height` attributes avoid layout shift.
हिंदी: `src` न हो तो browser download नहीं करता; observer सही समय पर `src` सेट कर देता है।

---

## ⚡ Alternative Solution
```html
<!-- Native lazy loading: no JS needed -->
<img src="photo.jpg" loading="lazy" width="400" height="300" alt="photo">
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: putting src directly in HTML and hiding with CSS — image still downloads
// <img src="big.jpg" style="display:none">

// ✅ Correct: use data-src (or loading="lazy") so the request is deferred
```

---

## 🎯 Interview Tip (1 line)
Say: "Prefer native loading='lazy'; use IntersectionObserver for custom thresholds, and always set width/height to prevent layout shift."

---

## 🔗 Related Questions
→ Q223 (intersection observer) | Q191 (lazy loader) | Q192 (image preloader)
