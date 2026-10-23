# F19. Internationalization (i18n)
# हिंदी में: Internationalization (i18n) — ऐप को ऐसा बनाना कि वो कई भाषाओं और क्षेत्रों में चल सके: अनुवाद (हिंदी, तमिल, बांग्ला…), ₹ और अंकों का सही format, तारीख़ें, बहुवचन, और दाएँ-से-बाएँ (RTL) भाषाएँ

---

## 🔵 Simple Definition (English)
- **Internationalization (i18n)** is **engineering the app so it can support any language/region without code changes**: no hard-coded strings, locale-aware formatting, layouts that handle longer text and RTL scripts.
- **Localization (l10n)** is the actual **adaptation for a specific locale**: translations (Hindi, Tamil, Marathi…), currency (₹), date formats, cultural content.
- A **locale** is a language + region code (BCP 47): `en-IN`, `hi-IN`, `ta-IN`, `ar-AE`.
Key pieces: **message catalogs** (keys → translated strings with ICU MessageFormat for **plurals, gender, variables**), **Intl APIs** (`Intl.NumberFormat`, `DateTimeFormat`, `RelativeTimeFormat`, `PluralRules`), **locale detection & routing** (`/hi/...`), **RTL support** (`dir="rtl"`, logical CSS properties), **fonts** for scripts (Devanagari, Tamil, Bengali) and a **translation workflow** (TMS like Crowdin, Lokalise, Phrase).
Libraries: **i18next/react-i18next**, **FormatJS/react-intl**, **next-intl**, **Lingui**; React Native: i18next + `expo-localization`.

## 🔵 सरल परिभाषा (Hindi)
i18n = ऐप को ऐसे बनाना कि बिना code बदले कोई भी भाषा/क्षेत्र जोड़ सकें — कोई text code में hard-coded नहीं, ₹/अंक/तारीख़ locale के हिसाब से, लंबे शब्दों और RTL के लिए लचीला layout।
l10n = किसी ख़ास भाषा के लिए असली अनुवाद और बदलाव (हिंदी, तमिल)। Locale = भाषा + क्षेत्र (`hi-IN`, `en-IN`)। हिस्से: अनुवाद files (keys → text, बहुवचन के नियम), Intl APIs, URL में भाषा (`/hi/`), RTL, सही fonts, और अनुवाद का workflow।

---

## 🔴 Problem it Solves
India alone has **22 scheduled languages**, and a large share of new internet users prefer content in Indian languages over English. Globally, apps expand to many markets. Without i18n:
- Strings are **hard-coded** in components, so adding Hindi means touching hundreds of files.
- **Wrong formats**: `1,00,000` (Indian grouping) vs `100,000`; `₹1,499.00` vs `INR 1499`; `18/10/2026` vs `10/18/2026`.
- **Broken grammar**: "1 items", wrong plural rules (Hindi, Arabic and Russian plurals differ from English).
- **Broken layouts**: German or Tamil strings are often 30–50% longer and overflow buttons; Arabic/Urdu need right-to-left mirroring.
- **Missing glyphs** (tofu □□□) for Devanagari or Tamil, or **huge font downloads**.
- Translations shipped in one giant bundle, slowing the app.

## 🔴 यह क्यों बना? (Hindi)
भारत में 22 अनुसूचित भाषाएँ हैं और नए internet users का बड़ा हिस्सा अंग्रेज़ी की जगह भारतीय भाषाओं में content पसंद करता है। बिना i18n: text code में फँसा, हिंदी जोड़ने के लिए सैकड़ों files बदलनी पड़ें; ग़लत format (`1,00,000` बनाम `100,000`, तारीख़ उलटी); "1 items" जैसी ग़लत grammar; लंबे तमिल/जर्मन शब्द बटन से बाहर; Urdu/Arabic के लिए RTL नहीं; अक्षर □□□ दिखना; सारे अनुवाद एक भारी bundle में।

---

## 🟢 How it Works — Step by Step

### Architecture

```
                 ┌────────────── Build / CI ───────────────┐
 Developers ──►  │ source strings (en.json) extracted from  │ ──push──► TMS (Crowdin/Lokalise/Phrase)
 add keys        │ code; lint for missing/unused keys       │ ◄─pull─── translators / machine translation
                 └──────────────────────────────────────────┘             + human review
                                   │
                                   ▼
            locales/en/common.json, locales/hi/common.json, locales/ta/checkout.json ...
                                   │  (split by namespace/route → lazy-loaded)
                                   ▼
 Runtime: detect locale → load messages for locale + namespace → t('cart.items', { count }) →
          Intl formatters for numbers, currency, dates → render; <html lang dir>
```

### Locale detection & routing (web)

```
Priority: explicit user choice (saved in profile/cookie) > URL prefix (/hi/...) > Accept-Language header
          > geo/IP hint (only as suggestion) > default (en-IN)
URLs per locale for SEO: https://shop.com/hi/product/… with <link rel="alternate" hreflang="hi-IN" …>
Never auto-redirect on every visit against the user's explicit choice
Mobile: device locale via expo-localization; in-app language switcher (Android 13+ per-app language)
```

### Messages: keys, interpolation, plurals (ICU MessageFormat)

```json
// en.json
{ "cart.items": "{count, plural, =0 {Your cart is empty} one {# item} other {# items}}",
  "order.eta": "Arriving in {minutes} min",
  "greeting": "Hi {name}!" }
// hi.json
{ "cart.items": "{count, plural, =0 {आपका कार्ट ख़ाली है} one {# आइटम} other {# आइटम}}",
  "order.eta": "{minutes} मिनट में पहुँच रहा है",
  "greeting": "नमस्ते {name}!" }
Rules: never concatenate translated fragments ("Arriving in " + n + " min") — word order differs;
       give translators context (description/screenshots); use keys by meaning, not by English text
```

### Formatting with Intl (no manual string building)

```js
new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(149999.5)  // ₹1,49,999.50
new Intl.NumberFormat('hi-IN').format(10000000)                                         // 1,00,00,000
new Intl.NumberFormat('en-IN', { notation: 'compact' }).format(2500000)                 // 25L
new Intl.DateTimeFormat('hi-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(d) // e.g. 18 अक्टू॰ 2026, 7:30 pm
new Intl.RelativeTimeFormat('hi', { numeric: 'auto' }).format(-1, 'day')                // कल
new Intl.PluralRules('hi-IN').select(1)                                                  // "one"
Store timestamps in UTC (ISO 8601); format in the user's time zone (Asia/Kolkata) at display time
```

### RTL (Arabic, Urdu, Hebrew)

```
<html lang="ur" dir="rtl">
Use CSS logical properties: margin-inline-start, padding-inline-end, inset-inline-start, text-align: start
Flip directional icons (back arrows), not universal ones (play button, clocks)
Flexbox/grid follow dir automatically; test bidirectional text (English brand names inside Urdu)
React Native: I18nManager.forceRTL(true) + app restart; use start/end instead of left/right in styles
```

### Performance

```
- Split catalogs by namespace/route; load only the active locale (dynamic import)
- SSR: render with the right locale on the server (no flash of English); pass messages for the page only
- Fonts: load script-specific subsets (Noto Sans Devanagari / Tamil) only for that locale
- Cache catalogs with hashed filenames; OTA-update translations on mobile without app release (M17)
```

### Content beyond UI strings

```
Backend-driven content (product names, restaurant descriptions, notifications, emails, SMS) needs
localized fields in the DB/CMS: name: { en: "Butter Chicken", hi: "बटर चिकन" } or translation tables;
API accepts Accept-Language / ?locale=; search must handle transliteration ("paneer" ≈ "पनीर")
Push notifications/SMS templates per locale (DLT-registered templates in India for SMS)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Code में कोई text नहीं — सिर्फ़ keys (`t('cart.items')`); अनुवाद `en.json`, `hi.json` में; developers नई keys जोड़ें, CI उन्हें TMS (Crowdin/Lokalise) पर भेजे, अनुवादक भरें, वापस ऐप में।
2. भाषा चुनने का क्रम: यूज़र की अपनी पसंद > URL (`/hi/`) > ब्राउज़र की Accept-Language > default; SEO के लिए हर भाषा का अलग URL + hreflang।
3. बहुवचन और variables के लिए ICU format (`{count, plural, one {...} other {...}}`); वाक्य जोड़-तोड़ कर मत बनाओ — हर भाषा में शब्दों का क्रम अलग।
4. ₹, अंक (1,00,000), तारीख़, "कल/2 घंटे पहले" — सब `Intl` से; समय UTC में रखो और दिखाते समय यूज़र के time zone में।
5. RTL (Urdu/Arabic) के लिए `dir="rtl"` और logical CSS (margin-inline-start); सिर्फ़ चालू भाषा का अनुवाद और font लोड करो; DB में product/restaurant नाम भी कई भाषाओं में; search में "paneer" = "पनीर"।

---

## 🟡 Real World Example

**Flipkart** — added Hindi and then several other Indian languages to its app to reach users in smaller towns. Features like vernacular UI and voice search in Indian languages were key parts of reaching the "next 200 million" users.

**Swiggy / Zomato / Meesho / PhonePe** — offer UIs in multiple Indian languages. Meesho, focused on Tier-2/3 India, invested heavily in vernacular UI and content, and PhonePe supports a dozen-plus Indian languages.

**Google / Android** — Android 13 added per-app language preferences. Google products ship to 100+ languages with ICU MessageFormat and centralized translation pipelines.

**Airbnb / Booking.com** — localize prices, dates, legal text and support content per market, with hreflang SEO pages per locale.

## 🟡 Real Example Hindi में
Flipkart ने छोटे शहरों के यूज़र्स तक पहुँचने के लिए हिंदी और फिर कई भारतीय भाषाएँ जोड़ीं, साथ में भारतीय भाषाओं में voice search।
Meesho (Tier-2/3 भारत पर ध्यान) ने vernacular UI पर बहुत निवेश किया; PhonePe दर्जन से ज़्यादा भारतीय भाषाओं में; Android 13 में हर ऐप के लिए अलग भाषा की सुविधा।

---

## 🟠 My Stack Example

### Next.js App Router with next-intl (locale in URL)
```
app/[locale]/layout.tsx       ← sets <html lang dir>, provides messages
app/[locale]/page.tsx
messages/en.json, messages/hi.json
middleware.ts                 ← detects locale, redirects / → /en or /hi
```
```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware';
export default createMiddleware({ locales: ['en', 'hi', 'ta'], defaultLocale: 'en', localeDetection: true });
export const config = { matcher: ['/((?!api|_next|.*\\..*).*)'] };
```
```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
export default async function LocaleLayout({ children, params }: { children: React.ReactNode; params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const messages = await getMessages();
  const dir = ['ar', 'ur'].includes(locale) ? 'rtl' : 'ltr';
  return (<html lang={locale} dir={dir}><body><NextIntlClientProvider messages={messages}>{children}</NextIntlClientProvider></body></html>);
}

// Component
import { useTranslations, useFormatter } from 'next-intl';
export function CartSummary({ count, total }: { count: number; total: number }) {
  const t = useTranslations('cart'); const f = useFormatter();
  return <p>{t('items', { count })} · {f.number(total, { style: 'currency', currency: 'INR' })}</p>;
}
```

### React / React Native with i18next (lazy-loaded namespaces)
```ts
// i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import resourcesToBackend from 'i18next-resources-to-backend';
import * as Localization from 'expo-localization';       // RN; on web use i18next-browser-languagedetector

i18n.use(initReactI18next)
  .use(resourcesToBackend((lng: string, ns: string) => import(`./locales/${lng}/${ns}.json`)))   // code-split per locale
  .init({
    lng: savedLanguage ?? Localization.getLocales()[0]?.languageCode ?? 'en',
    fallbackLng: 'en', ns: ['common'], defaultNS: 'common',
    interpolation: { escapeValue: false },                // React already escapes
  });
export default i18n;
```
```tsx
const { t, i18n } = useTranslation('checkout');
<Text>{t('order.eta', { minutes: 25 })}</Text>
<Button title={t('placeOrder')} onPress={placeOrder} />
<Picker selectedValue={i18n.language} onValueChange={(l) => { i18n.changeLanguage(l); mmkv.set('lang', l); api.updateProfile({ locale: l }); }}>
  <Picker.Item label="English" value="en" /><Picker.Item label="हिन्दी" value="hi" /><Picker.Item label="தமிழ்" value="ta" />
</Picker>
```

### Backend: localized content + Accept-Language (FastAPI)
```python
SUPPORTED = ["en", "hi", "ta"]
def pick_locale(accept_language: str | None, user_locale: str | None) -> str:
    if user_locale in SUPPORTED: return user_locale
    for part in (accept_language or "").split(","):
        lang = part.split(";")[0].strip()[:2]
        if lang in SUPPORTED: return lang
    return "en"

@app.get("/menu/{rid}")
async def menu(rid: int, request: Request, user=Depends(optional_user)):
    loc = pick_locale(request.headers.get("accept-language"), getattr(user, "locale", None))
    items = await db.fetch("SELECT id, price, COALESCE(name->>$2, name->>'en') AS name FROM items WHERE restaurant_id=$1", rid, loc)
    return {"locale": loc, "items": items}       # name stored as JSONB {"en": "...", "hi": "..."}
```

### Lint & CI for translations
```bash
npx i18next-parser          # extract keys from code → en.json; fail CI if keys missing in hi/ta (or mark for TMS)
# Pseudo-localization in dev ("[!! Àççôûñţ ŝéţţîñĝš !!]") to catch hard-coded strings & overflow
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between i18n and l10n?**
A1: Internationalization is the engineering work that makes an app adaptable to any locale without code changes: externalized strings, ICU messages for plurals and variables, locale-aware formatting via Intl, flexible layouts, RTL support, Unicode and fonts, locale routing and detection. Localization is producing the locale-specific adaptations: translations, currency, date conventions, imagery, legal text and cultural tweaks for, e.g., `hi-IN` or `ta-IN`. i18n is done once, l10n per locale.

**Q2: How do you handle plurals and variables correctly?**
A2: Use ICU MessageFormat (or the library's plural syntax), which applies CLDR plural rules per language: `{count, plural, one {# item} other {# items}}`. Languages differ: Arabic has six forms, Russian three, Hindi typically one and other. Never concatenate translated fragments or build sentences in code, because word order and grammar vary. Pass variables into a whole message and give translators context and screenshots.

**Q3: How do you load translations efficiently?**
A3: Split message catalogs by locale and namespace (route or feature), and load only the active locale's namespaces needed for the current page via dynamic import or HTTP with long-cache hashed URLs. For SSR, render with server-side messages for that page only to avoid a flash of untranslated content. Preload on locale switch. On mobile, bundle the default locale and fetch or OTA-update others. Load script-specific font subsets only for that locale.

**Q4: How would you support RTL languages?**
A4: Set `dir="rtl"` and `lang` on the document (or a subtree). Use CSS logical properties (`margin-inline-start`, `inset-inline-end`, `text-align: start`) rather than left and right. Rely on flexbox and grid direction. Mirror directional icons and layouts (back arrows, progress, carousels) but not universal symbols. Handle bidirectional text with proper isolation (`<bdi>`, `dir="auto"` for user content). Test with real RTL content. In React Native, use `I18nManager` and start/end styles.

**Q5: How do you design the backend for multilingual content?**
A5: Store user-facing content with per-locale fields (JSONB maps, translation tables, or CMS locales) and fall back to a default locale. APIs accept the locale via `Accept-Language`, a user profile or a query param, and return localized fields plus locale-aware formatting hints. Templates for notifications, emails and SMS exist per locale. Search indexes per language with analyzers and transliteration (Hinglish "paneer" ↔ "पनीर"). Store times in UTC and money as integer minor units with a currency code. Keep slugs and SEO pages per locale.

---

## 🔷 Trade-offs
✅ Reach new markets & users (vernacular India), better conversion and trust.
❌ Translation cost & workflow, QA per locale, longer strings breaking layouts, more bundle/CDN files.
✅ Machine translation speeds up — ❌ quality issues; human review for core flows (checkout, legal).
✅ Locale in URL: SEO + shareable — ❌ routing complexity vs cookie-only preference.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| i18n | Making app locale-ready | कई भाषाओं के लिए तैयार करना |
| l10n | Adapting for a locale | किसी भाषा के लिए ढालना |
| Locale | Language + region (hi-IN) | भाषा + क्षेत्र |
| Message catalog | Keys → translated strings | अनुवाद की file |
| ICU MessageFormat | Syntax for plurals/variables | बहुवचन का format |
| Intl API | Built-in locale formatting | locale के हिसाब से format |
| RTL | Right-to-left scripts | दाएँ से बाएँ लिखावट |
| hreflang | SEO tag for language versions | भाषा वाले pages का SEO tag |
| TMS | Translation management system | अनुवाद प्रबंधन tool |
| Pseudo-localization | Fake translations for testing | जाँच के लिए नक़ली अनुवाद |

---

## ⚡ 3-Line Summary
**English:**
1. i18n = externalize strings (keys + ICU plurals), format with Intl (₹, lakh grouping, dates, relative time), support RTL and scripts.
2. Detect locale (user choice > URL > Accept-Language), route per locale for SEO, lazy-load catalogs and fonts per locale, SSR in the right language.
3. Localize backend content too (per-locale fields, templates, transliteration search) and run a TMS workflow with CI checks and pseudo-localization.

**Hindi:**
1. Text keys में + ICU बहुवचन, `Intl` से ₹/अंक/तारीख़, RTL और लिपि (fonts) का ध्यान।
2. भाषा पहचानो (यूज़र > URL > ब्राउज़र), हर भाषा का URL, सिर्फ़ चालू भाषा का अनुवाद और font लोड करो।
3. Backend content भी कई भाषाओं में; TMS workflow, CI जाँच, pseudo-localization।

---

## ➡️ Next Topic Suggestion
**F20. Design Systems + Component Libraries** — Accessibility, i18n and consistent UI across many teams are easiest to get right once, in shared components. Next: design tokens, component libraries, theming, documentation and versioning.
