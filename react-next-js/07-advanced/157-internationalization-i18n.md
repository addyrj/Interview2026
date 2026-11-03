# 157. Internationalization (i18n)
# हिंदी में: Internationalization (i18n) — App को कई भाषाओं और regions में चलाना

---

## 🔵 Simple Definition (English)
**Internationalization (i18n)** means designing your app so it can show different languages and regional formats (dates, numbers, currency, plurals, text direction) without changing the code. **Localization (l10n)** is the actual work of adding a specific language or region, such as Hindi for India.

## 🔵 सरल परिभाषा (Hindi)
**Internationalization (i18n)** का मतलब है app को ऐसे बनाना कि वह code बदले बिना अलग भाषाएँ और क्षेत्रीय formats (तारीख, संख्या, मुद्रा, plurals, text की दिशा) दिखा सके। **Localization (l10n)** किसी खास भाषा या क्षेत्र को जोड़ने का असली काम है, जैसे भारत के लिए Hindi।

---

## 🔴 Problem it Solves

Hard-coded text like `<h1>Welcome</h1>` makes translation impossible without editing every component. Formatting by hand breaks: `12/03/2025` means 12 March in India but 3 December in the US; `1,00,000` (lakh) vs `100,000`; "1 item / 2 items" plural rules differ (Hindi treats 0 and 1 as singular, Arabic has six plural forms); Arabic and Urdu are written right-to-left. A product like Zomato, with users across India speaking Hindi, Tamil, Bengali and English, would lose customers if it only supports English.

## 🔴 यह क्यों बना? (Hindi)
`<h1>Welcome</h1>` जैसा hard-coded text हर component बदले बिना अनुवाद असंभव कर देता है। हाथ से formatting टूटती है: `12/03/2025` भारत में 12 मार्च है पर अमेरिका में 3 दिसंबर; `1,00,000` (लाख) बनाम `100,000`; "1 item / 2 items" के plural नियम अलग हैं (Hindi में 0 और 1 एकवचन माने जाते हैं, Arabic में छह plural रूप हैं); Arabic और Urdu दाएँ से बाएँ लिखी जाती हैं। Zomato जैसे product के users पूरे भारत में हैं जो Hindi, Tamil, Bengali और English बोलते हैं, अगर वह सिर्फ English रखे तो ग्राहक खो देगा।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a library: react-i18next (most popular), react-intl (FormatJS), or next-intl (Next.js)
Step 2 → Move every user-visible string into translation files: en.json, hi.json
Step 3 → Replace text in JSX with keys: t('cart.title') instead of "Your Cart"
Step 4 → Detect the language: URL (/hi/...), cookie, browser Accept-Language, or user setting
Step 5 → Load the matching JSON; fall back to English if a key is missing
Step 6 → Use interpolation: t('greeting', { name }) → "नमस्ते, Aditya"
Step 7 → Use plural rules: t('items', { count: 3 }) picks the correct plural form
Step 8 → Format numbers, dates and currency with Intl APIs (built into browsers) or the library
Step 9 → Set <html lang> and dir="rtl" for right-to-left languages
Step 10 → Lazy-load translations per language/namespace to keep the bundle small
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Library चुनो: react-i18next (सबसे लोकप्रिय), react-intl (FormatJS), या next-intl (Next.js के लिए)
Step 2 → हर दिखने वाला string translation files में डालो: en.json, hi.json
Step 3 → JSX में text की जगह keys लगाओ: "Your Cart" की जगह t('cart.title')
Step 4 → भाषा पहचानो: URL (/hi/...), cookie, browser का Accept-Language, या user की setting
Step 5 → मिलती-जुलती JSON load करो; कोई key न मिले तो English पर fallback
Step 6 → Interpolation इस्तेमाल करो: t('greeting', { name }) → "नमस्ते, Aditya"
Step 7 → Plural नियम इस्तेमाल करो: t('items', { count: 3 }) सही plural रूप चुनता है
Step 8 → संख्या, तारीख और मुद्रा को Intl APIs (browser में built-in) या library से format करो
Step 9 → <html lang> और दाएँ-से-बाएँ भाषाओं के लिए dir="rtl" सेट करो
Step 10 → bundle छोटा रखने के लिए translations को भाषा/namespace के हिसाब से lazy-load करो
```

---

## 🟡 Real World Example
**Zomato India.** The same order screen shows "Your order is on the way" in English and "आपका ऑर्डर रास्ते में है" in Hindi. The total appears as `₹1,24,500` for an Indian-locale user (lakh grouping) and `₹124,500` for an English-US locale. The label "3 items" in English becomes "3 आइटम" in Hindi. A language switcher in the profile menu stores the choice in a cookie; the server reads it so the first HTML is already in the right language, avoiding a flash of English.

## 🟡 Real Example Hindi mein
**Zomato India।** एक ही order screen English में "Your order is on the way" और Hindi में "आपका ऑर्डर रास्ते में है" दिखाती है। कुल रकम भारतीय locale वाले user को `₹1,24,500` (लाख वाला grouping) और English-US locale में `₹124,500` दिखती है। "3 items" Hindi में "3 आइटम" बन जाता है। Profile menu का language switcher चुनाव को cookie में रखता है; server उसे पढ़ता है ताकि पहला HTML ही सही भाषा में आए और English की झलक न दिखे।

---

## 💻 Code Example — Basic

```jsx
// Basic i18n with Intl only (no library), good to understand the core ideas
// Browser built-ins: Intl.NumberFormat, Intl.DateTimeFormat, Intl.PluralRules
const messages = {                                          // tiny translation dictionary
  en: { title: 'Your Cart', items: { one: '{count} item', other: '{count} items' } },
  hi: { title: 'आपकी कार्ट', items: { one: '{count} आइटम', other: '{count} आइटम' } },
};

function formatItems(locale, count) {
  const rule = new Intl.PluralRules(locale).select(count);  // returns 'one' | 'other' | ... per language
  const template = messages[locale].items[rule] ?? messages[locale].items.other; // safe fallback
  return template.replace('{count}', count);                // fill the placeholder
}

export function CartSummary({ locale = 'en', count, total, date }) {
  const money = new Intl.NumberFormat(locale === 'hi' ? 'hi-IN' : 'en-IN', {
    style: 'currency', currency: 'INR',                     // ₹ with correct digit grouping
  }).format(total);
  const day = new Intl.DateTimeFormat(locale === 'hi' ? 'hi-IN' : 'en-IN', {
    dateStyle: 'long',                                      // e.g. "2 November 2026" / "2 नवंबर 2026"
  }).format(date);
  return (
    <section lang={locale}>                                 {/* tells screen readers the language */}
      <h2>{messages[locale].title}</h2>
      <p>{formatItems(locale, count)}</p>
      <p>{money}</p>
      <p>{day}</p>
    </section>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// react-i18next setup (v13+ API). Install: npm i i18next react-i18next
// i18n.js : configure once, import at the app entry
import i18n from 'i18next';                                 // core engine
import { initReactI18next } from 'react-i18next';           // React bindings
import LanguageDetector from 'i18next-browser-languagedetector'; // reads localStorage / browser language

i18n
  .use(LanguageDetector)                                    // auto-detect user language
  .use(initReactI18next)                                    // connect with React
  .init({
    fallbackLng: 'en',                                      // use English if key/language missing
    supportedLngs: ['en', 'hi'],
    interpolation: { escapeValue: false },                  // React already escapes output (XSS safe)
    resources: {                                            // in real apps: load JSON files lazily
      en: { translation: {
        greeting: 'Hello, {{name}}',
        cart_one: '{{count}} item in cart',                 // plural suffixes: _one, _other (i18next v21+)
        cart_other: '{{count}} items in cart',
      } },
      hi: { translation: {
        greeting: 'नमस्ते, {{name}}',
        cart_one: 'कार्ट में {{count}} आइटम',
        cart_other: 'कार्ट में {{count}} आइटम',
      } },
    },
  });

export default i18n;
```

```jsx
// CartHeader.jsx : use translations in a component
import { useTranslation } from 'react-i18next';             // hook: re-renders on language change

export function CartHeader({ user, count }) {
  const { t, i18n } = useTranslation();                     // t = translate, i18n = instance
  const lang = i18n.resolvedLanguage;                       // actual language in use

  return (
    <header dir={lang === 'ar' ? 'rtl' : 'ltr'} lang={lang}>{/* direction + language for a11y */}
      <h1>{t('greeting', { name: user })}</h1>              {/* interpolation */}
      <p>{t('cart', { count })}</p>                         {/* plural chosen by count */}
      <p>{new Intl.NumberFormat(lang === 'hi' ? 'hi-IN' : 'en-IN').format(1250000)}</p> {/* 12,50,000 */}
      <select
        value={lang}
        onChange={(e) => i18n.changeLanguage(e.target.value)} // switch language, all useTranslation users re-render
        aria-label="Language"
      >
        <option value="en">English</option>
        <option value="hi">हिन्दी</option>
      </select>
    </header>
  );
}
```

---

## 🟠 Next.js Connection

Next.js has built-in i18n **routing for the Pages Router** (`i18n` in `next.config.js`: `locales`, `defaultLocale`). **The App Router has no built-in i18n config**: you implement it with a `[locale]` route segment and middleware (called `proxy` in newer Next.js versions, version-dependent), usually with the `next-intl` library (or `next-i18next` for Pages Router). Translations can be used in **Server Components**, which keeps translation JSON out of the client bundle.

```jsx
// app/[locale]/page.jsx : next-intl in a Server Component (next-intl v3/v4, version-dependent API)
import { getTranslations, setRequestLocale } from 'next-intl/server'; // server-side helpers

export default async function Home({ params }) {
  const { locale } = await params;                           // Next.js 15+: params is a Promise
  setRequestLocale(locale);                                  // enables static rendering per locale
  const t = await getTranslations('Home');                   // namespace "Home" from messages/hi.json
  return <h1>{t('title')}</h1>;                              // rendered on the server, zero client JS
}
```

```jsx
// app/[locale]/layout.jsx : set lang and dir on <html>, provide messages to client components
import { NextIntlClientProvider } from 'next-intl';          // makes useTranslations work in Client Components
import { getMessages } from 'next-intl/server';

export default async function LocaleLayout({ children, params }) {
  const { locale } = await params;
  const messages = await getMessages();                      // load only this locale's messages
  return (
    <html lang={locale} dir={['ar', 'ur'].includes(locale) ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider messages={messages}>{children}</NextIntlClientProvider>
      </body>
    </html>
  );
}
```

```js
// middleware.js : detect the locale and redirect "/" → "/hi" or "/en" (next-intl)
import createMiddleware from 'next-intl/middleware';         // handles detection, cookie and redirects

export default createMiddleware({
  locales: ['en', 'hi'],                                     // supported languages
  defaultLocale: 'en',                                       // fallback
});
export const config = { matcher: ['/((?!api|_next|.*\\..*).*)'] }; // skip API, assets, static files
```

SEO: use separate URLs per language (`/hi/...`), and add `alternates.languages` in `generateMetadata` for `hreflang` tags.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Building sentences by concatenating translated pieces
✅ **Correct:** Translate whole sentences with placeholders (word order differs between languages)

```jsx
// Wrong: Hindi word order is different, so this reads badly
<p>{t('you_have')} {count} {t('items_in_cart')}</p>

// Right: one key, one full sentence
<p>{t('cart', { count })}</p>            // "कार्ट में {{count}} आइटम"
```

❌ **Mistake 2:** Hand-written formatting for dates, numbers, currency and plurals (`count === 1 ? 'item' : 'items'`)
✅ **Correct:** Use `Intl` or library helpers

```jsx
// Wrong: US-style date and naive plural
const label = `${count} item${count === 1 ? '' : 's'}`;
const date = `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;

// Right
const date2 = new Intl.DateTimeFormat('hi-IN', { dateStyle: 'medium' }).format(d);
const label2 = t('items', { count });    // plural rules come from the language
```

❌ **Mistake 3:** Loading every language in the main bundle, or flashing English before the saved language loads
✅ **Correct:** Lazy-load per language, and detect the language on the server in Next.js

```jsx
// Wrong: importing all translations up front
import en from './locales/en.json';
import hi from './locales/hi.json';
import ta from './locales/ta.json';          // bundle grows with each language

// Right: load only what is needed
const messages = (await import(`./locales/${locale}.json`)).default; // dynamic import per locale
```

---

## 🧠 Tricky Interview Question

```jsx
const { t } = useTranslation();
// en: "welcome": "Welcome, {{name}}"   | name = "<img src=x onerror=alert(1)>"
return <h1>{t('welcome', { name })}</h1>;
```
With `interpolation: { escapeValue: false }`, is this an XSS risk?

**Answer:** No, in this form it is safe. `t()` returns a plain string, and React escapes strings when rendering them as text children, so the `<img>` is shown as visible text, not executed. That is why `escapeValue: false` is recommended with React (otherwise values get double-escaped, showing `&lt;`). It becomes dangerous only if you pass the result to `dangerouslySetInnerHTML` or use the `<Trans>` component with unescaped user HTML. If you need HTML in translations, use `<Trans>` with allowed tags only, and never inject raw user data there.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between i18n and l10n?
A1: i18n (internationalization) is preparing the app to support many locales: externalized strings, locale-aware formatting, flexible layouts. l10n (localization) is adapting it to a specific locale: translating text, currency, images and cultural details. You do i18n once and l10n per language.

Q2: How do you handle plurals and gender in translations?
A2: Use ICU MessageFormat (react-intl, next-intl) or i18next plural suffixes (`_one`, `_other`, `_few`...). Languages have different plural categories (CLDR rules), so you provide the forms each language needs and pass a `count`. Never use `count === 1 ? ... : ...`.

Q3: How would you add i18n to a Next.js App Router app?
A3: Create an `app/[locale]` segment, middleware to detect and redirect the locale, message files per language, and a library such as `next-intl`. Use server-side translation functions in Server Components, a `NextIntlClientProvider` for Client Components, set `<html lang dir>`, generate static params per locale, and add `hreflang` alternates for SEO.

Q4: How do you format numbers, dates and currency?
A4: With the built-in `Intl` APIs (`Intl.NumberFormat`, `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat`, `Intl.PluralRules`) or the library wrappers. They know local rules, such as lakh grouping for `en-IN`. Store dates in UTC or ISO format and format only for display, with the user's time zone.

Q5: What layout problems appear with translations and how do you handle them?
A5: Text length varies (German and Hindi can be 30% longer than English), so avoid fixed widths. RTL languages need `dir="rtl"` and CSS logical properties (`margin-inline-start` instead of `margin-left`). Fonts must support the script (for example Noto Sans Devanagari). Test with pseudo-localization (long fake text) to catch breakage early.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Your users speak several languages or live in different regions
- You sell across countries (currency, tax, date formats differ)
- Government or public apps in India that must support regional languages

❌ **Avoid (or defer) when:**
- A short-lived internal tool with one audience (but still avoid hard-coding if growth is likely)
- You cannot maintain translations (stale or machine-only translations hurt trust)
- Adding a heavy library only for one date format (use `Intl` directly)

**Re-render and performance note:** `useTranslation` subscribes the component to language changes, so changing the language re-renders those components (expected and cheap). Avoid creating `Intl.NumberFormat` objects inside hot render loops; create once and reuse with `useMemo` or a module-level cache because constructing them is relatively costly. Lazy-load translation files so each user downloads only their language. Server-side translations keep the JSON out of the client bundle.

---

## 📊 Visual Diagram

```
   Request "/hi/cart"
        │
        ▼
   middleware ──► detect locale (URL > cookie > Accept-Language) ──► "hi"
        │
        ▼
   app/[locale]/cart/page.jsx
        │  load messages/hi.json   (only Hindi is loaded)
        ▼
   t('cart.title') ─► "आपकी कार्ट"
   Intl.NumberFormat('hi-IN')  ─► "₹1,24,500"
   <html lang="hi" dir="ltr">

   en.json ─┐                            key              en              hi
   hi.json ─┼─► translation catalog ──►  cart.title  "Your Cart"   "आपकी कार्ट"
   ta.json ─┘                            greeting    "Hello, {{n}}" "नमस्ते, {{n}}"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| i18n | Internationalization: preparing for many languages | कई भाषाओं के लिए तैयारी |
| l10n | Localization: adapting to one locale | किसी एक locale के लिए ढालना |
| Locale | Language + region code (hi-IN, en-US) | भाषा + क्षेत्र का code |
| Interpolation | Inserting values into a message | Message में values डालना |
| Pluralization | Choosing word forms by count | गिनती से शब्द का रूप चुनना |
| ICU MessageFormat | Standard syntax for plurals and select | Plurals के लिए मानक syntax |
| RTL | Right-to-left writing direction | दाएँ से बाएँ लिखावट |
| Fallback language | Language used when a key is missing | Key न मिलने पर इस्तेमाल होने वाली भाषा |
| hreflang | SEO tag linking page language versions | भाषा-संस्करणों को जोड़ने वाला SEO tag |

---

## ⚡ 3-Line Summary
**English:**
1. i18n moves all text into translation files and uses locale-aware formatting so one codebase serves many languages.
2. Use react-i18next, react-intl or next-intl with keys, interpolation, plural rules and `Intl` for dates, numbers and currency.
3. In Next.js App Router use a `[locale]` segment, middleware and server translations, and set `lang`/`dir` on `<html>`.

**Hindi:**
1. i18n सारा text translation files में रखता है और locale के हिसाब से formatting करता है, ताकि एक codebase कई भाषाएँ चलाए।
2. Keys, interpolation, plural नियम और तारीख, संख्या व मुद्रा के लिए `Intl` के साथ react-i18next, react-intl या next-intl इस्तेमाल करो।
3. Next.js App Router में `[locale]` segment, middleware और server translations इस्तेमाल करो, और `<html>` पर `lang`/`dir` सेट करो।

---

## ➡️ Next Topic
**158. React + TypeScript Complete** — अब type safety सीखो: props, state, events, hooks और context को TypeScript से सुरक्षित बनाना, ताकि translation keys और API data जैसी गलतियाँ code चलाने से पहले ही पकड़ में आ जाएँ।
