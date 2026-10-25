# 151. Form Events (submit, change, input, focus, blur)
# हिंदी में: Form Events (submit, change, input, focus, blur)

---

## 🔵 Simple Definition (English)
Form events tell you what the user is doing with form fields. `input` fires on every change to a value, `change` fires when the value is committed, `focus` and `blur` fire when a field gets or loses focus, and `submit` fires when the form is sent. Call `preventDefault()` on `submit` to stop the page from reloading.

## 🔵 सरल परिभाषा (Hindi)
Form events बताते हैं कि user form fields के साथ क्या कर रहा है। `input` हर value बदलने पर चलता है, `change` value commit होने पर चलता है, `focus` और `blur` field में आने और निकलने पर चलते हैं, और `submit` form भेजे जाने पर चलता है। `submit` पर `preventDefault()` लगाने से page reload नहीं होता।

---

## 🔴 Problem it Solves
A plain HTML form sends the data to the server and reloads the whole page, even if the user only made a typo. Before form events, validation happened only after submit, so users waited for a round trip to learn that their email was wrong. Form events let the page check values as the user types, show errors on blur, format input (like card numbers), and send data with `fetch` without a reload.

## 🔴 यह क्यों बना? (Hindi)
एक साधारण HTML form data server को भेजता है और पूरा page reload करता है, भले ही user ने बस एक typo किया हो। Form events से पहले validation सिर्फ submit के बाद होता था, इसलिए user को server के जवाब तक इंतज़ार करना पड़ता था कि email गलत है। Form events से page type करते समय values check कर सकता है, blur पर errors दिखा सकता है, input format कर सकता है (जैसे card number), और बिना reload के `fetch` से data भेज सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → The user types in a field. Each keystroke or paste fires `input` on that field.
Step 2 → When the user leaves a text field (Tab or click elsewhere), `change` fires if the value changed, and `blur` fires.
Step 3 → Clicking a submit button, or pressing Enter in a text field, fires `submit` on the `<form>`.
Step 4 → Your handler calls `e.preventDefault()` to stop the browser's default page navigation.
Step 5 → You read the data with `new FormData(form)` and send it with `fetch`.
Step 6 → `focus` and `blur` do not bubble, so use `focusin` and `focusout` when you need event delegation on the form.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User field में type करता है। हर keystroke या paste पर उस field पर `input` चलता है।
Step 2 → जब user text field छोड़ता है (Tab या किसी और जगह click), value बदली हो तो `change` चलता है, और `blur` भी चलता है।
Step 3 → Submit button click करने पर, या text field में Enter दबाने पर `<form>` पर `submit` चलता है।
Step 4 → आपका handler `e.preventDefault()` चलाता है ताकि browser की default page navigation रुक जाए।
Step 5 → `new FormData(form)` से data पढ़ें और `fetch` से भेजें।
Step 6 → `focus` और `blur` bubble नहीं करते, इसलिए form पर event delegation चाहिए तो `focusin` और `focusout` इस्तेमाल करें।

---

## 🟡 Real World Example
On Flipkart's address form, typing a 6-digit pincode and leaving the field (`change`) fills in the city and state automatically. Razorpay's card form uses `input` to add spaces every four digits as the user types. Paytm's login form shows "Enter a valid mobile number" on `blur`, so the error does not appear while the user is still typing. When the user presses Enter or taps Pay, the `submit` handler stops the reload and sends the data with `fetch`.

## 🟡 Real Example Hindi mein
Flipkart के address form में 6-digit pincode type करके field छोड़ने पर (`change`) city और state अपने-आप भर जाते हैं। Razorpay के card form में `input` से user के type करते समय हर चार digits के बाद space जुड़ता है। Paytm के login form में `blur` पर "valid mobile number डालें" दिखता है, इसलिए user type करते समय error नहीं दिखता। User Enter दबाए या Pay पर tap करे, तो `submit` handler reload रोकता है और `fetch` से data भेजता है।

---

## 💻 Code Example — Basic
Save as `form-events-basic.html` and open it in a browser. Type in the fields, Tab between them, and press Enter to submit. Watch the Console.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 so Hindi text displays correctly -->
  <title>Form Events Basic</title>                  <!-- tab title -->
</head>
<body>
  <form id="signup">                                <!-- the form we listen to -->
    <input id="name" name="name" placeholder="Name"> <!-- text field -->
    <input id="email" name="email" type="email">    <!-- email field, browser checks the format -->
    <select id="city" name="city">                  <!-- dropdown -->
      <option value="">Choose city</option>         <!-- empty value means nothing chosen -->
      <option value="Delhi">Delhi</option>          <!-- a city option -->
      <option value="Pune">Pune</option>            <!-- another city option -->
    </select>
    <button type="submit">Sign up</button>          <!-- clicking this fires submit -->
  </form>

  <script>
    const form = document.getElementById("signup"); // the form element
    const nameInput = document.getElementById("name"); // the name input (not "name": window.name exists)
    const city = document.getElementById("city");  // the city select

    form.addEventListener("input", (e) => {        // input bubbles up from any field in the form
      console.log("input in", e.target.name, "value:", e.target.value); // fires on every keystroke
    });

    form.addEventListener("change", (e) => {       // change bubbles up too, fires on commit
      console.log("change in", e.target.name, "value:", e.target.value); // fires after blur or select
    });

    nameInput.addEventListener("focus", () => {         // focus does NOT bubble, so attach it to the field
      console.log("name field focused");           // runs when the user enters this field
    });

    nameInput.addEventListener("blur", () => {          // blur does NOT bubble, so attach it to the field
      console.log("name field left");              // runs when the user leaves this field
    });

    form.addEventListener("submit", (e) => {       // fires when the form is submitted
      e.preventDefault();                          // stop the browser from reloading the page
      const data = new FormData(form);             // read all named fields from the form
      console.log("submitted:", Object.fromEntries(data)); // convert to a plain object and print
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `form-events-advanced.html`. It validates on blur, shows a live character count on `input`, guards against double submits, and sends the data with `fetch`. The `fetch` call uses a local endpoint, so the request will fail on a static file; the error path shows how to handle that.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Form Events Advanced</title>               <!-- tab title -->
  <style>
    .error { color: #b00; font-size: 0.9em; }       /* red text for validation messages */
  </style>
</head>
<body>
  <form id="order" novalidate>                      <!-- novalidate: we run our own checks -->
    <input id="address" name="address" maxlength="80" placeholder="Delivery address"> <!-- address -->
    <span id="count">0/80</span>                    <!-- live character counter -->
    <input id="pin" name="pincode" placeholder="6-digit pincode"> <!-- pincode field -->
    <span id="pinError" class="error"></span>       <!-- error message for the pincode -->
    <button id="send" type="submit">Place order</button> <!-- submit button -->
  </form>

  <script>
    const form = document.getElementById("order");  // the form
    const pin = document.getElementById("pin");     // pincode input
    const pinError = document.getElementById("pinError"); // where the pin error shows
    const count = document.getElementById("count"); // character counter element
    let submitting = false;                         // guard flag against double submits

    form.addEventListener("input", (e) => {         // live feedback while typing
      if (e.target.id === "address") {              // only the address field has a counter
        count.textContent = `${e.target.value.length}/80`; // show current length
      }
    });

    pin.addEventListener("blur", () => {            // validate when the user leaves the field
      const ok = /^\d{6}$/.test(pin.value);         // exactly six digits
      pinError.textContent = ok ? "" : "Pincode must be 6 digits"; // show or clear the message
    });

    form.addEventListener("submit", async (e) => {  // async so we can await fetch
      e.preventDefault();                           // never let the browser reload the page
      if (submitting) return;                       // ignore a second submit while one is running
      if (!/^\d{6}$/.test(pin.value)) {             // final check before sending
        pin.focus();                                // move the cursor to the bad field
        return;                                     // stop here, nothing is sent
      }
      submitting = true;                            // lock the form
      document.getElementById("send").disabled = true; // disable the button while sending
      try {
        const data = Object.fromEntries(new FormData(form)); // read all fields as a plain object
        const res = await fetch("/api/orders", {    // send the order as JSON
          method: "POST",                           // POST creates a new order
          headers: { "Content-Type": "application/json" }, // tell the server the body is JSON
          body: JSON.stringify(data),               // convert the object to a JSON string
        });
        if (!res.ok) throw new Error(`Server returned ${res.status}`); // non-2xx is an error
        console.log("Order placed");                // success path
      } catch (err) {                               // network error or non-2xx status
        console.error("Order failed:", err.message); // show the problem in the console
      } finally {                                   // runs whether it worked or not
        submitting = false;                         // unlock the form
        document.getElementById("send").disabled = false; // enable the button again
      }
    });
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
A plain HTML form posts `application/x-www-form-urlencoded` data, so Express needs `express.urlencoded()` to read it. Validate on the server too, because client checks can be bypassed. After a successful POST, redirect with `303 See Other` (Post/Redirect/Get) so a page refresh does not submit the form again.

```javascript
// server.js — npm install express ; run: node server.js
const express = require("express");                // web framework
const app = express();                             // create the app
app.use(express.urlencoded({ extended: false }));  // parse form posts (name=value&...)
app.use(express.json());                           // parse JSON posts from fetch
app.use(express.static("public"));                 // serve the HTML form page

app.post("/checkout/address", (req, res) => {      // handle the form POST
  const { name = "", email = "", pincode = "" } = req.body; // default missing fields to ""
  const errors = {};                               // collect every error, not just the first
  if (name.trim().length < 2) errors.name = "Name is too short";            // rule 1
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errors.email = "Email looks invalid"; // rule 2
  if (!/^\d{6}$/.test(pincode)) errors.pincode = "Pincode must be 6 digits"; // rule 3

  if (Object.keys(errors).length > 0) {            // any rule failed
    return res.status(422).json({ errors });       // 422 Unprocessable Entity with the messages
  }
  // A real app saves the address to a database here
  res.redirect(303, "/checkout/payment");          // 303: after POST, show the next page with GET
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `preventDefault()` on `submit`, so the page reloads and your JavaScript state is lost
✅ Correct: Call `e.preventDefault()` first in the submit handler, then do your work.

```javascript
// Wrong — the page reloads right after the handler runs; the fetch may not finish
form.addEventListener("submit", () => {
  fetch("/api/save", { method: "POST", body: new FormData(form) }); // request may be cancelled by the reload
});

// Right — stop the reload, then send the data ourselves
form.addEventListener("submit", (e) => {
  e.preventDefault();                                              // keep the page alive
  fetch("/api/save", { method: "POST", body: new FormData(form) }); // safe to finish
});
```

❌ **Mistake 2:** Using `change` for live typing feedback, so the message appears only after the user leaves the field
✅ Correct: Use `input` for live feedback, and use `change` or `blur` for validation messages that should wait.

```javascript
// Wrong — the counter only updates after the user leaves the field
countEl.addEventListener("change", () => {       // fires on commit, not on each keystroke
  countEl.textContent = input.value.length;      // stale while typing
});

// Right — input fires on every keystroke
input.addEventListener("input", () => {          // fires on every keystroke and paste
  countEl.textContent = input.value.length;      // always up to date
});
```

❌ **Mistake 3:** Using `focus` or `blur` for delegation on the form
✅ Correct: `focus` and `blur` do not bubble, so a listener on the form never sees them. Use `focusin` and `focusout`, which do bubble.

```javascript
// Wrong — the form never receives blur events from its children
form.addEventListener("blur", () => console.log("left a field")); // does not fire here

// Right — focusout bubbles up to the form
form.addEventListener("focusout", (e) => {        // bubbles from every child field
  console.log("left", e.target.name);             // e.target is the field that lost focus
});
```

---

## 🧠 Tricky Interview Question
What is printed by this code? The page has a text input with id `name` and the value "abc". Assume the listeners below are attached first.

```javascript
const field = document.getElementById("name");      // text input, initial value "abc"
field.addEventListener("input", () => console.log("input"));   // listener A
field.addEventListener("change", () => console.log("change")); // listener B
field.value = "xyz";                                 // code changes the value: no event fires
field.dispatchEvent(new Event("input"));             // we fire a fake input event by hand
field.dispatchEvent(new Event("change"));            // we fire a fake change event by hand
```

Answer: The output is:
```
input
change
```
Explanation: Assigning `field.value` in JavaScript fires no `input` or `change` event, because those events describe user actions. The two lines at the end fire events manually with `dispatchEvent`, so only those two prints appear, in the order we dispatched them. The lesson is that events do not follow `.value` changes automatically; code that depends on user typing must use `input`, and code that runs after a user commits the value must use `change`. In a real browser, when the user types "d" and then presses Tab, the order is `input`, then `change` (because the value changed), then `blur`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `input` and `change`?
A1: `input` fires on every change to the value, including each keystroke and paste. `change` fires only when the user commits the value, which for text fields happens on blur, and for checkboxes and selects happens right away.

Q2: Why does `submit` fire when the user presses Enter in a text field?
A2: Browsers run implicit submission. If a form has a submit button (or only one text field), pressing Enter in a field triggers the form's `submit` event, which is why you should handle `submit` and not the button's `click`.

Q3: Does `form.submit()` fire the `submit` event?
A3: No. `form.submit()` sends the form directly and skips the `submit` event, so validation in your listener is bypassed. Use `form.requestSubmit()` instead, which fires `submit` and respects validation.

Q4: Why are `focus` and `blur` not delegated, and what should you use instead?
A4: They do not bubble, so a parent listener does not see them. Use `focusin` and `focusout`, which bubble, when you need one listener on the form or container.

Q5: How do you read all values from a form?
A5: Create `new FormData(form)` and read entries with `Object.fromEntries(data)`. FormData includes only named fields, so give each field a `name` attribute.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want live feedback while typing (`input`) or validation after leaving a field (`blur`)
- You want to intercept a submit, check the data, and send it with `fetch`
- You need to format input as the user types, such as card numbers or phone numbers

❌ Avoid when:
- A native attribute (`required`, `type="email"`, `pattern`) already does the check and you do not need custom messages
- You rely on client-side checks alone for security; always validate on the server too
- You use `input` to run a heavy request on every keystroke; debounce it instead

---

## 📊 Visual Diagram
```
User action                 Event fired on the field          Event on <form>
───────────                 ─────────────────────────         ───────────────
types "d"               ──► input (bubbles)              ──►  input listener
Tab / click elsewhere   ──► change (bubbles, if changed) ──►  change listener
                        ──► blur (does NOT bubble)
                        ──► focusout (bubbles)           ──►  focusout listener
clicks Sign up / Enter  ──► submit (bubbles, on form)    ──►  submit listener
                                                                  │
                                       preventDefault()? ◄────────┘
                                         yes: stay on page, use fetch
                                         no:  browser sends the form and reloads
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `input` | Fires on every value change by the user | हर value change पर चलने वाला event |
| `change` | Fires when the value is committed | Value commit होने पर चलने वाला event |
| `focus` / `blur` | Field gets or loses focus (no bubbling) | Field में आना या निकलना (bubble नहीं होता) |
| `focusin` / `focusout` | Same as focus/blur but bubbles | Focus/blur जैसा, पर bubble होता है |
| `submit` | Form is being sent | Form भेजे जाने का event |
| `preventDefault()` | Stops the default action such as page reload | Default action (जैसे reload) रोकना |
| `FormData` | Object that holds the form's named fields | Form के named fields को रखने वाला object |
| Implicit submission | Enter in a field submits the form | Field में Enter से form submit होना |
| Post/Redirect/Get | POST, then 303 redirect, then GET | POST के बाद redirect, ताकि refresh से दोबारा submit न हो |

---

## ⚡ 3-Line Summary
**English:**
1. `input` runs on every keystroke, `change` runs on commit, and `focus`/`blur` run when a field gets or loses focus.
2. Handle `submit` on the form, call `preventDefault()`, and read the data with `new FormData(form)`.
3. Validate on the client for speed and on the server for safety, and use `focusin`/`focusout` when you need delegation.

**Hindi:**
1. `input` हर keystroke पर चलता है, `change` commit पर चलता है, और `focus`/`blur` field में आने-निकलने पर चलते हैं।
2. Form पर `submit` handle करें, `preventDefault()` लगाएँ, और `new FormData(form)` से data पढ़ें।
3. Client पर speed के लिए और server पर सुरक्षा के लिए validate करें, और delegation के लिए `focusin`/`focusout` इस्तेमाल करें।

---

## ➡️ Next Topic
**152. Window Events (load, resize, scroll, DOMContentLoaded)** — अगला topic page-level events बताता है, यानी page कब तैयार होता है और window कब बदलता है, जो layout और lazy loading के लिए ज़रूरी है।
