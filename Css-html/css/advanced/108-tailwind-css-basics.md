# 108. Tailwind CSS Basics
# हिंदी में: Tailwind CSS — Utility-First Styling, HTML में ही Design

---

## 🔵 Simple Definition (English)
**Tailwind CSS** is a **utility-first** CSS framework. Instead of writing custom CSS classes, you compose small single-purpose classes directly in your markup: `class="flex items-center gap-4 p-4 rounded-lg bg-white shadow"`. A build step scans your files and generates only the CSS you actually use.

## 🔵 सरल परिभाषा (Hindi)
**Tailwind CSS** एक **utility-first** CSS framework है। अपनी custom CSS classes लिखने की जगह आप छोटी single-purpose classes सीधे markup में जोड़ते हैं: `class="flex items-center gap-4 p-4 rounded-lg bg-white shadow"`। Build step आपकी files scan करके सिर्फ वही CSS बनाता है जो आपने सच में use किया।

---

## 🔴 Problem it Solves
```
BEFORE (traditional CSS):
  - Naming is hard: .card-wrapper-inner-title-text ? (BEM names get long)
  - Switching between HTML and CSS files all day.
  - CSS only grows: nobody dares to delete old classes (dead CSS).
  - Inconsistent spacing/colors: padding 13px here, 15px there.

AFTER (Tailwind):
  - No naming: style where you write markup.
  - A design scale: p-4 = 1rem, p-6 = 1.5rem; colors from one palette.
  - CSS size stays small and stops growing (only used classes are generated).
  - Responsive, hover and dark variants in the same class list: md:flex hover:bg-blue-700 dark:bg-gray-900
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (traditional CSS):
  - Naming मुश्किल: .card-wrapper-inner-title-text? (BEM names लंबे हो जाते हैं)
  - दिन भर HTML और CSS files के बीच switch करना।
  - CSS सिर्फ बढ़ता है: पुरानी classes हटाने की हिम्मत नहीं होती (dead CSS)।
  - Spacing/colors inconsistent: कहीं 13px, कहीं 15px।

अब (Tailwind):
  - Naming नहीं: जहाँ markup लिखते हो वहीं style।
  - Design scale: p-4 = 1rem, p-6 = 1.5rem; colors एक palette से।
  - CSS size छोटा रहता है (सिर्फ use हुई classes बनती हैं)।
  - Responsive, hover, dark variants उसी class list में: md:flex hover:bg-blue-700 dark:bg-gray-900
```

---

## 🟢 How it Works — Step by Step

```
1. INSTALL (Next.js / Vite):   npm i tailwindcss @tailwindcss/postcss   (v4)
   v4 CSS entry:                @import "tailwindcss";
   v3 CSS entry:                @tailwind base; @tailwind components; @tailwind utilities;
   (v3 also needs tailwind.config.js with a `content: ["./src/**/*.{js,jsx,ts,tsx}"]` list)

2. WRITE classes in markup:
       <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
3. BUILD: Tailwind scans source files for class names (as plain strings) and
   generates a CSS file containing only those utilities (JIT engine).
4. NAMING CHEAT-SHEET:
     Spacing   p-4 px-2 py-6 m-4 mx-auto mt-8 gap-4 space-y-2   (1 unit = 0.25rem)
     Sizing    w-full w-1/2 w-64 h-screen max-w-md min-h-0
     Layout    flex grid block hidden  items-center justify-between  grid-cols-3
     Text      text-sm text-lg font-bold text-gray-700 leading-6 tracking-wide
     Color     bg-white text-blue-600 border-gray-200
     Border    border rounded-lg ring-2 shadow-md
     Position  relative absolute inset-0 top-4 z-10 sticky
5. VARIANTS (prefix:class):
     State       hover: focus: active: disabled: group-hover: peer-checked:
     Responsive  sm: md: lg: xl: 2xl:    (mobile-first! min-width breakpoints)
     Dark        dark:bg-gray-900
     Other       first: last: odd: before: after: placeholder: print:
6. ARBITRARY VALUES: w-[320px] bg-[#ff5722] top-[13px] grid-cols-[1fr_2fr]
7. CUSTOMIZE: v3 -> tailwind.config.js theme.extend; v4 -> @theme { --color-brand: #e47911; }
8. REUSE: do NOT use @apply everywhere. Extract React components instead.

BREAKPOINTS (default): sm 640px, md 768px, lg 1024px, xl 1280px, 2xl 1536px.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. INSTALL (Next.js / Vite):   npm i tailwindcss @tailwindcss/postcss   (v4)
   v4 CSS में:                  @import "tailwindcss";
   v3 CSS में:                  @tailwind base; @tailwind components; @tailwind utilities;
   (v3 में tailwind.config.js में `content` list भी चाहिए)

2. Markup में classes लिखो:
       <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
3. BUILD: Tailwind source files में class names (plain strings) ढूँढकर सिर्फ वही utilities बनाता है।
4. NAMING CHEAT-SHEET:
     Spacing   p-4 px-2 py-6 m-4 mx-auto mt-8 gap-4   (1 unit = 0.25rem)
     Sizing    w-full w-1/2 w-64 h-screen max-w-md
     Layout    flex grid hidden items-center justify-between grid-cols-3
     Text      text-sm text-lg font-bold text-gray-700 leading-6
     Color     bg-white text-blue-600 border-gray-200
     Border    border rounded-lg ring-2 shadow-md
5. VARIANTS (prefix:class):
     State       hover: focus: active: disabled: group-hover:
     Responsive  sm: md: lg: xl: 2xl:   (mobile-first, min-width)
     Dark        dark:bg-gray-900
6. ARBITRARY VALUES: w-[320px] bg-[#ff5722] grid-cols-[1fr_2fr]
7. CUSTOMIZE: v3 -> tailwind.config.js; v4 -> @theme { --color-brand: #e47911; }
8. REUSE: @apply हर जगह मत लगाओ; React component बनाओ।
```

---

## 🟡 Real World Example
**Netflix (marketing pages), GitHub, Shopify admin and countless Next.js startups use Tailwind.** A Swiggy-style restaurant card is built in one JSX block: an image with `aspect-video object-cover`, title `text-lg font-semibold`, rating badge `bg-green-600 text-white rounded px-2 text-sm`, and a hover lift `hover:-translate-y-1 hover:shadow-lg transition`. No CSS file is touched.

## 🟡 Real Example Hindi mein
**Netflix (marketing pages), GitHub, Shopify admin और कई Next.js startups Tailwind use करते हैं।** Swiggy जैसा restaurant card एक JSX block में बनता है: image पर `aspect-video object-cover`, title `text-lg font-semibold`, rating badge `bg-green-600 text-white rounded px-2 text-sm`, और hover पर उठना `hover:-translate-y-1 hover:shadow-lg transition`। CSS file को छूना नहीं पड़ता।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tailwind CSS Basics Demo</title>

  <!-- Tailwind Play CDN (v3): for LEARNING/PROTOTYPES only, not production.
       Needs internet. In real projects use the build step (PostCSS/CLI). -->
  <script src="https://cdn.tailwindcss.com"></script>

  <script>
    // Optional: customize theme (same as tailwind.config.js in v3)
    tailwind.config = {
      theme: { extend: { colors: { brand: '#e23744' } } }   // adds bg-brand, text-brand ...
    };
  </script>
</head>

<!-- bg-gray-100: page background, min-h-screen: at least full height -->
<body class="bg-gray-100 min-h-screen p-6 font-sans text-gray-800">

  <!-- Container: centered, max width, mobile-first padding -->
  <div class="mx-auto max-w-5xl">
    <h1 class="mb-6 text-2xl font-bold md:text-3xl">Restaurants near you</h1>

    <!-- Responsive grid: 1 column (mobile) -> 2 (md) -> 3 (lg) -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">

      <!-- CARD 1. "group" lets children react to hover on the card -->
      <article class="group overflow-hidden rounded-xl bg-white shadow transition hover:-translate-y-1 hover:shadow-lg">
        <!-- Image placeholder: aspect-video = 16/9 -->
        <div class="aspect-video bg-gradient-to-br from-orange-300 to-red-400"></div>

        <div class="space-y-2 p-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold group-hover:text-brand">Biryani House</h2>
            <!-- Rating badge -->
            <span class="rounded bg-green-600 px-2 py-0.5 text-sm font-medium text-white">4.5</span>
          </div>
          <p class="text-sm text-gray-500">North Indian &middot; 30 min</p>

          <!-- Button with states: hover, focus ring, disabled -->
          <button class="w-full rounded-lg bg-brand py-2 font-medium text-white
                         hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2
                         disabled:cursor-not-allowed disabled:opacity-50">
            Order now
          </button>
        </div>
      </article>

      <!-- CARD 2: arbitrary values + sold out state -->
      <article class="overflow-hidden rounded-xl bg-white shadow">
        <div class="aspect-video bg-gradient-to-br from-sky-300 to-indigo-400"></div>
        <div class="space-y-2 p-4">
          <h2 class="text-lg font-semibold">Pizza Corner</h2>
          <p class="text-sm text-gray-500">Italian &middot; 25 min</p>
          <!-- Arbitrary value: exact width and hex color -->
          <span class="inline-block w-[120px] rounded bg-[#ffedd5] px-2 py-1 text-center text-xs text-[#9a3412]">
            Closed now
          </span>
          <button disabled class="w-full rounded-lg bg-brand py-2 font-medium text-white
                                  disabled:cursor-not-allowed disabled:opacity-50">
            Unavailable
          </button>
        </div>
      </article>

      <!-- CARD 3: dark: variant works with class="dark" on <html> (darkMode: 'class') or system (default 'media') -->
      <article class="overflow-hidden rounded-xl bg-white shadow dark:bg-gray-800 dark:text-white">
        <div class="aspect-video bg-gradient-to-br from-emerald-300 to-teal-500"></div>
        <div class="p-4">
          <h2 class="text-lg font-semibold">Salad Bar</h2>
          <p class="text-sm text-gray-500 dark:text-gray-300">Healthy &middot; 20 min</p>
        </div>
      </article>
    </div>
  </div>
</body>
</html>
```

```css
/* What Tailwind GENERATES for "px-4" and "md:flex" (you never write this) */
.px-4 { padding-left: 1rem; padding-right: 1rem; }
@media (min-width: 768px) { .md\:flex { display: flex; } }
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Next.js: `npx create-next-app@latest` asks "Use Tailwind CSS?" -> yes.
//    app/globals.css contains the Tailwind import. Use className everywhere.

// 2. Extract a COMPONENT (not @apply) for repeated styles
export function Button({ children, variant = 'primary', ...props }) {
  const styles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    ghost:   'bg-transparent text-blue-600 hover:bg-blue-50',
  };
  return (
    <button
      className={`rounded-lg px-4 py-2 font-medium transition ${styles[variant]}`}
      {...props}
    >
      {children}
    </button>
  );
}

// 3. IMPORTANT: Tailwind finds classes as WHOLE strings in source.
//    WRONG (dynamic string building, class is never generated):
<div className={`bg-${color}-500`} />
//    CORRECT (complete class names):
const colors = { red: 'bg-red-500', blue: 'bg-blue-500' };
<div className={colors[color]} />

// 4. Conditional classes: use clsx / classnames; resolve conflicts: tailwind-merge
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';
<div className={twMerge(clsx('p-4 bg-white', isActive && 'bg-blue-100', className))} />
//    shadcn/ui uses this exact "cn()" helper (clsx + tailwind-merge).
```

---

## ⚫ Interview Questions + Answers

**Q1: What is utility-first CSS and how is Tailwind different from Bootstrap?**
A1: Utility-first means building designs by combining small single-purpose classes (`p-4`, `flex`, `text-center`). Bootstrap gives prebuilt components (`.btn`, `.card`) with a fixed look. Tailwind gives no components, only low-level utilities, so every site can look unique and you rarely override anything.

**Q2: Isn't it just inline styles? What are the differences?**
A2: No. Utilities support what inline styles cannot: media queries (`md:`), pseudo-classes (`hover:`, `focus:`), dark mode, group/peer states, and a constrained design scale for consistency. They are also reusable classes, cached by the browser, and compatible with CSP.

**Q3: How does Tailwind keep CSS small, and why do dynamic class names fail?**
A3: The compiler scans your source files for class-name strings and generates only those. It does not execute your code. So `` `bg-${color}-500` `` never appears as a complete string and no CSS is produced. Use full class names in a lookup object or a safelist.

**Q4: How does responsive design work in Tailwind?**
A4: Mobile-first: unprefixed classes apply to all sizes, and prefixed ones (`sm:`, `md:`, `lg:`) apply from that min-width and up. Example: `flex-col md:flex-row` = column on mobile, row from 768px.

**Q5: What are the downsides and how do you manage them?**
A5: Long class lists, learning the names, harder to read raw HTML. Manage by extracting components (React), using `clsx`/`cva` for variants, Prettier plugin to sort classes, and `@apply` only sparingly. Also be careful with specificity when mixing with other CSS (use `@layer`).

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Building class names dynamically
```jsx
/* WRONG */ <p className={`text-${size}`}>Hi</p>
/* CORRECT */ <p className={size === 'lg' ? 'text-lg' : 'text-sm'}>Hi</p>
```

❌ **Mistake 2:** Thinking `sm:` means "small screens only"
```html
<!-- WRONG: expecting only mobile. sm: means 640px and UP -->
<div class="sm:hidden">   <!-- hidden from 640px upward -->
<!-- CORRECT: write mobile style first, override at breakpoints -->
<div class="block md:hidden">
```

❌ **Mistake 3:** Using the Play CDN in production
```html
<!-- WRONG: runtime compiler, big and slow -->
<script src="https://cdn.tailwindcss.com"></script>
<!-- CORRECT: Tailwind CLI / PostCSS / Vite plugin build -->
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Utility class | One class = one CSS job | एक class एक काम |
| Variant | Prefix like `hover:` / `md:` | Condition का prefix |
| JIT | Generates CSS on demand | ज़रूरत पर CSS बनाना |
| Arbitrary value | `w-[320px]` custom value | अपनी value |
| @apply | Inline utilities into a class | Utilities को class में जोड़ना |
| Mobile-first | Base = mobile, prefixes = larger | पहले mobile, फिर बड़ी screen |
| twMerge | Resolves conflicting Tailwind classes | टकराते classes सुलझाना |

---

## ⚡ 3-Line Summary
**English:**
1. Tailwind is utility-first: style by combining small classes in markup; only used classes are generated.
2. Variants (`hover:`, `md:`, `dark:`) are mobile-first and add states and responsiveness in the same class list.
3. In React, extract components (not `@apply`), never build class names dynamically, and use `clsx` + `tailwind-merge`.

**Hindi:**
1. Tailwind utility-first है: markup में छोटी classes जोड़कर style करो; सिर्फ use हुई classes बनती हैं।
2. Variants (`hover:`, `md:`, `dark:`) mobile-first हैं और states व responsiveness उसी class list में जोड़ते हैं।
3. React में components बनाओ (`@apply` नहीं), class names dynamic मत बनाओ, और `clsx` + `tailwind-merge` use करो।

---

## ➡️ Next Topic
**109. CSS Modules** — Tailwind का दूसरा तरीका: normal CSS लिखो पर class names अपने-आप component तक scoped हो जाएँ।
