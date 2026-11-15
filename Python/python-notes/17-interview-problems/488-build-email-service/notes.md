---

# 488. Build Email Service
# हिंदी में: Email Service बनाना (template + SMTP + retry)

Full runnable solution: [main.py](main.py) (templates, pluggable transport, retries, mocked SMTP test; no real mail is sent).

---

## 🔵 Simple Definition (English)
An email service builds a message from a template, hands it to a transport (SMTP or an API like SES), and retries on temporary failures. Keeping the transport swappable makes it testable.

## 🔵 सरल परिभाषा (Hindi)
Email service template से message बनाती है, उसे transport (SMTP या SES जैसी API) को देती है, और अस्थायी failure पर retry करती है। Transport बदला जा सके तो test करना आसान होता है।

---

## 🔴 Problem it Solves
Ad-hoc `smtplib` calls scattered in code are hard to test, easy to leak passwords in, and fail silently when the mail server blips. A small service centralises templates, validation, TLS and retries.

## 🔴 यह क्यों बना? (Hindi)
जगह-जगह बिखरे `smtplib` calls test करने में मुश्किल, password leak का खतरा और mail server के हल्के से error पर चुपचाप फेल होते हैं। एक छोटी service templates, validation, TLS और retries एक जगह रखती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Validate recipient address
Step 2 → Pick (subject, body) template; Template.substitute(context)
Step 3 → Build EmailMessage: headers + plain text + HTML alternative
Step 4 → transport.send(msg): connect, STARTTLS, login, send_message
Step 5 → On SMTPException/OSError: sleep 2**attempt, retry up to N times
Step 6 → Still failing -> raise so the caller / job queue can handle it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Recipient address जाँचो
Step 2 → (subject, body) template लो; Template.substitute(context) से भरो
Step 3 → EmailMessage बनाओ: headers + plain text + HTML विकल्प
Step 4 → transport.send(msg): connect, STARTTLS, login, send_message
Step 5 → SMTPException/OSError पर 2**attempt सेकंड रुककर N बार retry
Step 6 → फिर भी फेल हो तो exception उठाओ ताकि caller / job queue संभाले
```

---

## 🟡 Real World Example
Signup flow of an Indian fintech: OTP email with the code, welcome email after KYC, invoice mail with PDF attached. Provider is SES or SendGrid in production, a local mail catcher (Mailpit) in development, and a fake transport in tests.

## 🟡 Real Example Hindi mein
Fintech के signup flow में code वाली OTP email, KYC के बाद welcome email और PDF लगी invoice email। Production में provider SES या SendGrid, development में Mailpit जैसा local mail catcher और tests में fake transport होता है।

---

## 💻 Code Example — Basic
```python
# Build (not send) an email with the standard library
from email.message import EmailMessage  # message container

msg = EmailMessage()  # create empty message
msg["From"] = "noreply@shop.in"  # sender header
msg["To"] = "asha@example.com"  # recipient header
msg["Subject"] = "Hello"  # subject header
msg.set_content("Plain text body")  # text/plain part
msg.add_alternative("<p>HTML body</p>", subtype="html")  # text/html part
print(msg["Subject"], msg.get_content_type())  # inspect it
print([p.get_content_type() for p in msg.iter_parts()])  # the two parts
# Output:
# Hello multipart/alternative
# ['text/plain', 'text/html']
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: retry around a swappable transport
def send(self, to: str, template: str, **ctx: str) -> int:
    if "@" not in to:
        raise ValueError(f"bad address: {to}")
    msg = self.build(to, template, **ctx)
    for attempt in range(1, self.retries + 1):
        try:
            self.transport.send(msg)
            return attempt  # attempts used
        except (smtplib.SMTPException, OSError):
            if attempt == self.retries:
                raise  # give up
            self.sleep(2 ** attempt)  # backoff (sleep is injectable for tests)
```
Real output of `python main.py` (SMTP was mocked with `unittest.mock`; nothing hit the network):
```
attempts: 3 sleeps: [2, 4]
Your OTP | Hi Asha, your OTP is 482913. Valid for 5 minutes.
ValueError: bad address: nope
KeyError: 'otp'
all ok
```

---

## 🟠 JavaScript vs Python Comparison
Nodemailer's `createTransport` + `sendMail` maps to `smtplib.SMTP` + `send_message`. Templates: Handlebars/EJS in JS, `string.Template` or Jinja2 in Python.

```python
with smtplib.SMTP("smtp.example.com", 587) as s:  # context manager closes socket
    s.starttls()
    s.send_message(msg)
```
```javascript
const t = nodemailer.createTransport({ host: "smtp.example.com", port: 587 });
await t.sendMail({ from, to, subject, text });
```

---

## 🟠 FastAPI Connection
`smtplib` is blocking, so never call it directly in an `async def` route. Use `BackgroundTasks`, a job queue (topic 485), or `fastapi-mail`/`aiosmtplib` for async.

```python
@app.post("/signup", status_code=202)
def signup(email: str, bg: BackgroundTasks) -> dict[str, str]:  # sync def runs in a threadpool
    bg.add_task(svc.send, email, "welcome", name="friend")  # send after the response
    return {"status": "ok"}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hard-coding SMTP passwords in code.
✅ Correct: read from environment/secret manager.

❌ Mistake 2: Building headers by string concatenation with user input, allowing header injection (`\r\nBcc: ...`).
✅ Correct: use `EmailMessage`, which rejects newlines in headers.

```python
# Wrong
raw = f"To: {user_input}\r\nSubject: Hi\r\n\r\nBody"
# Right
msg["To"] = user_input   # ValueError if it contains a newline
```

❌ Mistake 3: Blocking call inside `async def`, freezing the event loop.
✅ Correct: sync route, background task, or an async client.

---

## 🧠 Tricky Interview Question
```python
from string import Template
print(Template("Hi $name").substitute({}))
```
Answer: `KeyError: 'name'`. `substitute` is strict; `safe_substitute` leaves the placeholder untouched. The service uses strict `substitute` so a forgotten variable fails loudly instead of emailing "Hi $name" to a customer.

---

## ⚫ Interview Questions + Answers

Q1: SMTP port 25, 465, 587?
A1: 587 is submission with STARTTLS (recommended), 465 is implicit TLS, 25 is server-to-server and often blocked.

Q2: Why a Protocol/transport abstraction?
A2: Swap SMTP for SES or a fake in tests without changing business code.

Q3: What are SPF, DKIM, DMARC?
A3: DNS-based records proving the sender is authorised and the content is untampered; without them mail lands in spam.

Q4: Which errors to retry?
A4: Temporary ones (connection drop, 4xx). Do not retry permanent failures (invalid mailbox, 5xx).

Q5: How to make sending idempotent?
A5: Store a message id/dedupe key before sending so a retried job does not mail the user twice.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Transactional mail: OTP, receipts, password reset

❌ Avoid when:
- Bulk marketing (use a dedicated ESP with unsubscribe handling)
- Sending directly in the request path (queue it)

---

## 📊 Visual Diagram
```
 route ─► EmailService.send ─► build(template) ─► transport.send ─► SMTP / SES
                 │                                    │ error
                 └──── retry 1..N, sleep 2,4,8 ◄──────┘ (then raise)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SMTP | Protocol to send mail | मेल भेजने का protocol |
| STARTTLS | Upgrade to encrypted link | कनेक्शन को encrypt करना |
| Template | Text with placeholders | खाली जगह वाला text |
| Transport | Delivery backend | भेजने वाला backend |
| Idempotency | Same effect when repeated | दोहराने पर वही असर |

---

## ⚡ 3-Line Summary
English: Build messages with EmailMessage and templates.
Hide delivery behind a transport so tests use a fake.
Retry temporary errors with backoff and run it off the request path.
Hindi: EmailMessage और templates से message बनाओ।
Delivery को transport के पीछे रखो ताकि tests में fake चले।
अस्थायी errors पर backoff के साथ retry करो और request के बाहर चलाओ।

---

## ➡️ Next Topic
489. Build PDF Generator: emails often carry invoices; next we generate those PDFs.

---
