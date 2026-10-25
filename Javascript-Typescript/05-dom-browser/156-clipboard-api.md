# 156. Clipboard API
# हिंदी में: Clipboard API — Copy और Paste को JavaScript से control करना

---

## 🔵 Simple Definition (English)
The Clipboard API lets a web page read and write text (and some images) to the user's system clipboard with `navigator.clipboard`. It is Promise-based, so you use `await` or `.then()` to know when the copy or paste finished.

## 🔵 सरल परिभाषा (Hindi)
Clipboard API आपके web page को user के system clipboard में text (और कुछ images) लिखने और पढ़ने देता है, `navigator.clipboard` के through। यह Promise-based है, यानी copy या paste कब पूरा हुआ, यह `await` या `.then()` से पता चलता है।

---

## 🔴 Problem it Solves
Earlier, copying text from a web page needed hacks: you created a hidden `<textarea>`, selected its text, and called `document.execCommand("copy")`. That method is deprecated, breaks on mobile, and cannot read the clipboard at all. Sites like Zomato (copy coupon code), Razorpay (copy payment link) and Google Docs (copy link) needed a clean, safe and async API.

## 🔴 यह क्यों बना? (Hindi)
पहले web page से text copy करने के लिए hacks करने पड़ते थे: एक hidden `<textarea>` बनाना, उसका text select करना और `document.execCommand("copy")` call करना। यह method deprecated है, mobile पर ठीक से नहीं चलता, और clipboard पढ़ भी नहीं सकता था। Zomato (coupon code copy), Razorpay (payment link copy) जैसी sites को एक साफ़, safe और async API चाहिए था।

---

## 🟢 How it Works — Step by Step

Step 1 → Page must be a **secure context**: `https://` or `http://localhost` (check with `window.isSecureContext`)
Step 2 → `navigator.clipboard.writeText(text)` returns a Promise; browser shows no prompt for write after a user gesture
Step 3 → `navigator.clipboard.readText()` returns a Promise; browser asks the user for permission (`clipboard-read`)
Step 4 → Calls must come from a user action (click, keypress) in most browsers, otherwise they are rejected
Step 5 → Handle the Promise: success → show "Copied!", failure → show fallback message

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Page एक **secure context** में होना चाहिए: `https://` या `http://localhost` (`window.isSecureContext` से check करें)
Step 2 → `navigator.clipboard.writeText(text)` एक Promise देता है; user gesture के बाद write के लिए आमतौर पर prompt नहीं आता
Step 3 → `navigator.clipboard.readText()` एक Promise देता है; browser user से permission माँगता है (`clipboard-read`)
Step 4 → ज़्यादातर browsers में ये calls user action (click, keypress) से होने चाहिए, वरना reject हो जाते हैं
Step 5 → Promise को handle करें: सफल हुआ तो "Copied!" दिखाएँ, fail हुआ तो fallback message दिखाएँ

---

## 🟡 Real World Example
Razorpay dashboard: merchant clicks "Copy payment link" next to a link. The button calls `navigator.clipboard.writeText(link)`, then changes its label to "Copied ✓" for 2 seconds. If the browser blocks clipboard access (for example, an iframe without permission), the code shows a small "Press Ctrl+C" message instead of failing silently.

## 🟡 Real Example Hindi mein
Razorpay dashboard: merchant एक link के बगल वाले "Copy payment link" button पर click करता है। Button `navigator.clipboard.writeText(link)` call करता है, फिर 2 सेकंड के लिए label "Copied ✓" हो जाता है। अगर browser clipboard access block कर दे (जैसे permission के बिना iframe), तो code silently fail होने के बजाय छोटा "Ctrl+C दबाएँ" message दिखाता है।

---

## 💻 Code Example — Basic
> Browser-only: the Clipboard API does not exist in Node.js (`navigator.clipboard` is `undefined` in Node). So the runnable example is a self-contained HTML page.
> **How to run:** save as `clipboard-basic.html`, serve it with `python3 -m http.server 8000` in that folder, then open `http://localhost:8000/clipboard-basic.html` in Chrome, Edge or Firefox and click the buttons.

```html
<!-- clipboard-basic.html — full page, JS inside <script> -->
<!DOCTYPE html>
<!-- Declare HTML5 document type -->
<html lang="en">
<!-- Root element, language English -->
<head>
  <!-- Metadata section -->
  <meta charset="UTF-8">
  <!-- Support all characters (including Hindi) -->
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Make page responsive on phones -->
  <title>Clipboard Basic</title>
  <!-- Browser tab title -->
</head>
<body>
  <!-- Visible page content starts -->
  <h2>Coupon Code Copier (Zomato style)</h2>
  <!-- Heading for the demo -->
  <input id="coupon" value="ZOMATO50" readonly>
  <!-- Read-only input that holds the coupon code -->
  <button id="copyBtn">Copy Coupon</button>
  <!-- Button that copies the coupon -->
  <button id="pasteBtn">Paste from Clipboard</button>
  <!-- Button that reads clipboard text -->
  <p id="status"></p>
  <!-- Paragraph to show success or error messages -->

  <script>
    // Get references to the three elements we need
    const couponInput = document.getElementById("coupon");
    // Input element holding the coupon
    const copyBtn = document.getElementById("copyBtn");
    // Copy button element
    const pasteBtn = document.getElementById("pasteBtn");
    // Paste button element
    const statusEl = document.getElementById("status");
    // Status paragraph element

    // Helper to show a message to the user
    function show(msg) {
      // Function declaration to update the status text
      statusEl.textContent = msg;
      // Set text (textContent is safe, no HTML injection)
    }

    // Check that the API exists before using it
    if (!navigator.clipboard || !window.isSecureContext) {
      // Clipboard missing or page not on https/localhost
      show("Clipboard API not available here. Use https or localhost.");
      // Tell the user why it failed
    }

    // Copy the coupon text when the copy button is clicked
    copyBtn.addEventListener("click", async () => {
      // Arrow async function runs on each click
      try {
        // Start error handling block
        await navigator.clipboard.writeText(couponInput.value);
        // Write coupon text to clipboard and wait for result
        show("Copied: " + couponInput.value);
        // Success message
      } catch (err) {
        // Runs if browser refused (no permission or not focused)
        show("Copy failed: " + err.message);
        // Show the reason
      }
    });

    // Read clipboard text when the paste button is clicked
    pasteBtn.addEventListener("click", async () => {
      // Async handler for the paste button
      try {
        // Start error handling block
        const text = await navigator.clipboard.readText();
        // Read clipboard text (browser may ask permission)
        show("Clipboard contains: " + text);
        // Show what was read
      } catch (err) {
        // Permission denied or read not allowed
        show("Paste failed: " + err.message);
        // Show the reason
      }
    });
  </script>
  <!-- Script block ends -->
</body>
<!-- Body ends -->
</html>
<!-- Document ends -->
```

## 💻 Code Example — Advanced
> Browser-only again. This version copies rich data (HTML plus plain text) with `ClipboardItem`, uses `AbortController`-free feedback timers, and handles every failure path. Save as `clipboard-advanced.html` and open via localhost, same as the basic one.

```html
<!-- clipboard-advanced.html — rich copy + fallback + feedback timer -->
<!DOCTYPE html>
<!-- HTML5 document type -->
<html lang="en">
<!-- Root element -->
<head>
  <!-- Head section -->
  <meta charset="UTF-8">
  <!-- UTF-8 so Devanagari renders -->
  <title>Clipboard Advanced</title>
  <!-- Tab title -->
  <style>
    /* Small style for the button and status */
    button { padding: 8px 14px; font-size: 16px; }
    /* Make buttons easy to tap on phones */
    #status { min-height: 1.5em; color: #0a7; }
    /* Status line with a fixed height so layout does not jump */
  </style>
  <!-- End of styles -->
</head>
<body>
  <!-- Visible content -->
  <h2>Payment Link Copier (Razorpay style)</h2>
  <!-- Heading -->
  <a id="link" href="https://rzp.io/l/demo123">https://rzp.io/l/demo123</a>
  <!-- The link to copy -->
  <br><br>
  <!-- Two line breaks for spacing -->
  <button id="copyRich">Copy as Rich Link</button>
  <!-- Copies both HTML and plain text -->
  <button id="copyPlain">Copy Plain URL</button>
  <!-- Copies plain text only -->
  <p id="status" aria-live="polite"></p>
  <!-- aria-live announces changes to screen readers -->

  <script>
    const statusEl = document.getElementById("status");
    // Status element for messages
    const linkEl = document.getElementById("link");
    // Link element we read data from

    let resetTimer = null;
    // Holds the timer id so we can cancel an old timer

    // Show a message and clear it after 2 seconds
    function flash(msg, isError = false) {
      // Optional second argument marks error messages
      statusEl.style.color = isError ? "#c00" : "#0a7";
      // Red for errors, green for success
      statusEl.textContent = msg;
      // Update text safely
      clearTimeout(resetTimer);
      // Cancel the previous timer if one is running
      resetTimer = setTimeout(() => (statusEl.textContent = ""), 2000);
      // Clear the message after 2 seconds
    }

    // Copy rich content (HTML + plain text) using ClipboardItem
    document.getElementById("copyRich").addEventListener("click", async () => {
      // Handler for the rich copy button
      if (!window.ClipboardItem) {
        // Check that ClipboardItem constructor exists in this browser
        flash("Rich copy not supported here", true);
        // Explain the limitation
        return;
        // Stop the function early
      }
      try {
        // Start error handling
        const html = `<a href="${linkEl.href}">Pay now</a>`;
        // Build an HTML anchor for apps that accept HTML paste
        const plain = linkEl.href;
        // Plain text fallback for notepads and terminals
        const item = new ClipboardItem({
          // Create one clipboard item holding two formats
          "text/html": new Blob([html], { type: "text/html" }),
          // HTML version as a Blob
          "text/plain": new Blob([plain], { type: "text/plain" }),
          // Plain text version as a Blob
        });
        await navigator.clipboard.write([item]);
        // Write the item and wait for the browser to finish
        flash("Rich link copied");
        // Success message
      } catch (err) {
        // Handle NotAllowedError, SecurityError and others
        flash("Copy failed: " + err.name, true);
        // Show error name
      }
    });

    // Copy only plain text (most compatible)
    document.getElementById("copyPlain").addEventListener("click", async () => {
      // Handler for the plain copy button
      try {
        // Start error handling
        await navigator.clipboard.writeText(linkEl.href);
        // Write the URL string
        flash("URL copied");
        // Success message
      } catch (err) {
        // Failure path
        flash("Copy failed: " + err.name, true);
        // Show error name
      }
    });
  </script>
  <!-- End script -->
</body>
<!-- End body -->
</html>
<!-- End document -->
```

---

## 🟠 Express.js Integration
The Clipboard API is browser-only, so Express cannot call it. Express's job is to **serve the page** that uses the API and to **receive what the user copied** when the page sends it to a backend (for example, analytics that count coupon copies).

```javascript
// server.js — run with: npm i express   then   node server.js
const express = require("express");
// Import the Express framework
const path = require("path");
// Import path helper for safe file paths

const app = express();
// Create an Express application
app.use(express.json());
// Parse JSON request bodies into req.body
app.use(express.static(path.join(__dirname, "public")));
// Serve files like clipboard-basic.html from the public folder

// POST endpoint: the browser sends analytics after a successful copy
app.post("/api/copy-event", (req, res) => {
  // Route handler for copy events
  const { couponCode, userId } = req.body;
  // Read fields the page sent
  if (!couponCode) {
    // Validate required field
    return res.status(400).json({ error: "couponCode is required" });
    // Reply with 400 Bad Request
  }
  console.log(`[copy] user=${userId} coupon=${couponCode}`);
  // Log the event on the server
  res.status(202).json({ ok: true });
  // 202 Accepted: we received the event
});

app.listen(3000, () => console.log("Open http://localhost:3000/clipboard-basic.html"));
// Start server on port 3000 and print the URL
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `await` and assuming the copy worked, so errors are never caught.
✅ Correct: `writeText` returns a Promise. Without `await`, `try/catch` cannot catch its rejection.

```javascript
// Wrong — the rejection is not caught by try/catch
async function copyCoupon(code) {
  try {
    navigator.clipboard.writeText(code); // no await, Promise ignored
    console.log("Copied!");              // prints even if copy failed
  } catch (err) {
    console.log("Failed", err);          // never runs for async errors
  }
}

// Right — await the Promise so catch receives the error
async function copyCoupon(code) {
  try {
    await navigator.clipboard.writeText(code); // wait for the result
    console.log("Copied!");                    // only prints on success
  } catch (err) {
    console.log("Failed", err.name);           // runs on permission or focus errors
  }
}
```

❌ Mistake 2: Calling `readText()` or `writeText()` on page load, without a user gesture.
✅ Correct: Trigger clipboard calls from a click or keypress handler.

```javascript
// Wrong — runs on load, browser may reject it
navigator.clipboard.readText().then(console.log);

// Right — runs only after the user clicks
document.getElementById("pasteBtn").addEventListener("click", async () => {
  const text = await navigator.clipboard.readText(); // allowed inside a user gesture
  console.log(text);
});
```

❌ Mistake 3: Using `document.execCommand("copy")` in new code.
✅ Correct: It is deprecated. Use `navigator.clipboard.writeText` and keep `execCommand` only as a last-resort fallback for very old browsers.

---

## 🧠 Tricky Interview Question
What will be printed, and why? Assume this runs in a browser console on `http://localhost`, with the user clicking the button.

```javascript
// Tricky Clipboard code
async function copyCoupon() {
  try {
    navigator.clipboard.writeText("ZOMATO50");
    // No await: the Promise is created and then ignored
    console.log("copied");
    // Printed right away
  } catch (err) {
    console.log("failed:", err.name);
    // Only reached for synchronous throws
  }
}

copyCoupon();
// Called from a click handler
```

Answer: The output is just `copied`. `writeText` returns a Promise. The function does not wait for it, so `console.log("copied")` runs immediately and the `catch` block never sees an asynchronous rejection. If the browser later refuses the write (for example, the document is not focused), the rejection becomes an **unhandled promise rejection** shown in the console, and the program still prints `copied` first. The fix is `await navigator.clipboard.writeText("ZOMATO50")`.

---

## ⚫ Interview Questions + Answers

Q1: Why is `navigator.clipboard` undefined on some pages?
A1: It is only available in secure contexts (`https://` or `localhost`). On plain `http://` pages in most browsers, `navigator.clipboard` is missing, so always check `window.isSecureContext` first.

Q2: Does `readText()` need permission?
A2: Yes. Reading the clipboard needs the `clipboard-read` permission, and the browser can show a prompt. `writeText()` is usually allowed after a user gesture without a prompt in modern browsers.

Q3: Can you copy an image?
A3: Yes, with `navigator.clipboard.write([new ClipboardItem({ "image/png": blob })])`. Only supported image types like PNG are allowed in `ClipboardItem`.

Q4: Why is the Clipboard API better than `execCommand("copy")`?
A4: It is async (Promise-based), works with permissions, supports more formats, and `execCommand` is deprecated and unreliable on iOS.

Q5: Can Node.js access the user's clipboard?
A5: Not with the Web API. Node has no `navigator.clipboard`. Desktop tools (for example Electron's `clipboard` module or a native npm package) are needed, and those run in their own process, not in a normal Node server.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A user clicks a "Copy" button for codes, links, API keys or addresses
- You need to copy rich formats (HTML plus plain text) or an image
- You want a Promise-based, non-blocking copy with error handling

❌ Avoid when:
- The page runs on plain `http://` (the API will not exist)
- You need to read the clipboard silently on page load (browsers block it)
- You are writing server code in Node.js (no browser clipboard exists there)

---

## 📊 Visual Diagram
```
User click (gesture)
        |
        v
 navigator.clipboard.writeText("ZOMATO50")
        |
        v
  [ Browser checks: secure context? focus? permission? ]
        |                              |
      allowed                        refused
        |                              |
        v                              v
  Promise resolves              Promise rejects
  -> "Copied!"                  -> catch(err) -> "Copy failed"
        |
        v
  OS system clipboard holds "ZOMATO50"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| navigator.clipboard | Entry point object for the Clipboard API | Clipboard तक पहुँचने का object |
| writeText | Writes plain text to the clipboard | Clipboard में plain text लिखना |
| readText | Reads plain text from the clipboard | Clipboard से plain text पढ़ना |
| ClipboardItem | Container for multiple formats (HTML, PNG) | कई formats रखने वाला container |
| Secure context | https or localhost, required for the API | सुरक्षित context (https या localhost) |
| User gesture | A real click or keypress that allows the action | असली user action (click या keypress) |
| execCommand | Old, deprecated copy method | पुराना, deprecated copy तरीका |

---

## ⚡ 3-Line Summary
English: The Clipboard API (`navigator.clipboard`) copies and reads text or images through Promises.
English: It works only in secure contexts and usually after a user click, so always `await` and handle errors.
English: Node.js has no clipboard, so Express only serves the page or receives copy analytics.
Hindi: Clipboard API (`navigator.clipboard`) Promises के ज़रिए text या images copy और read करता है।
Hindi: यह केवल secure context में और आमतौर पर user click के बाद चलता है, इसलिए हमेशा `await` करें और error handle करें।
Hindi: Node.js में clipboard नहीं होता, इसलिए Express सिर्फ page serve करता है या copy analytics लेता है।

---

## ➡️ Next Topic
157. Geolocation API (`navigator.geolocation`): the next browser permission-based API. It follows the same pattern of user gesture, secure context and async callbacks, and it is a common interview topic for location-based apps like Swiggy and Ola.
