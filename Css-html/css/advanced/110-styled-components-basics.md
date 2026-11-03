# 110. Styled Components Basics
# हिंदी में: Styled Components — JavaScript के अंदर CSS (CSS-in-JS)

---

## 🔵 Simple Definition (English)
**styled-components** is a CSS-in-JS library for React. You write real CSS inside tagged template literals to create components that carry their own styles: `const Button = styled.button\`padding: 8px;\``. Styles are scoped automatically (unique class names) and can change based on **props** and a **theme**.

## 🔵 सरल परिभाषा (Hindi)
**styled-components** React के लिए CSS-in-JS library है। आप tagged template literals के अंदर असली CSS लिखकर ऐसे components बनाते हैं जिनके साथ उनकी styles जुड़ी होती हैं: `const Button = styled.button\`padding: 8px;\``। Styles अपने-आप scoped (unique class names) होती हैं और **props** तथा **theme** के हिसाब से बदल सकती हैं।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Style depends on state ("primary", "disabled", "active") -> you juggle
    class strings: className={"btn " + (primary ? "btn-primary" : "")}
  - Global class collisions; unused CSS left behind after deleting components.
  - Theme values (colors) in CSS and in JS get out of sync.

AFTER (styled-components):
  - <Button $primary> : the style logic lives next to the component, with JS.
  - Auto-scoped class names: no collisions; delete the component, delete the CSS.
  - One theme object shared by JS and CSS through ThemeProvider.
  - Only the styles of rendered components are injected into the page.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Style state पर निर्भर ("primary", "disabled", "active") -> class strings जोड़नी पड़ती हैं:
    className={"btn " + (primary ? "btn-primary" : "")}
  - Global class टकराव; component हटाने के बाद बेकार CSS बचा रहता है।
  - Theme के colors CSS और JS में अलग-अलग हो जाते हैं।

अब (styled-components):
  - <Button $primary> : style की logic component के पास, JS के साथ।
  - Auto-scoped class names: टकराव नहीं; component हटाओ तो CSS भी हटे।
  - ThemeProvider से एक ही theme object JS और CSS दोनों में।
  - सिर्फ render हुए components की styles page में inject होती हैं।
```

---

## 🟢 How it Works — Step by Step

```
1. INSTALL:   npm i styled-components      (v6 is current; React 16.8+)

2. CREATE a styled component (tagged template literal):
       import styled from 'styled-components';
       const Button = styled.button`
         padding: 8px 16px;
         background: ${props => props.$primary ? '#e23744' : '#eee'};
       `;
   -> returns a React component that renders <button class="sc-abc123 xyz789">.

3. USE it like any component:   <Button $primary>Buy</Button>
   Transient props: names starting with $ ($primary) are used for styling only
   and are NOT passed down to the DOM (avoids unknown-attribute warnings). v6 recommends this.

4. EXTEND another one:          const BigButton = styled(Button)`font-size: 20px;`;
   Change tag with `as` prop:   <Button as="a" href="/">Link</Button>

5. NESTING like Sass:
       &:hover { ... }   & + & { ... }   .child { ... }   ${Icon} { margin-right: 4px; }  (target another styled component)

6. THEME:
       <ThemeProvider theme={{ colors: { brand: '#e23744' } }}>
       const Title = styled.h1` color: ${({ theme }) => theme.colors.brand}; `;

7. HELPERS: css`` (reusable snippets), createGlobalStyle`` (resets), keyframes`` (animations),
   .attrs() (default HTML attributes/props).

8. HOW IT WORKS: at runtime the library hashes the CSS, creates a class, injects a <style> tag.
   (Runtime = costs some JS and CPU. In Next.js App Router, Server Components
   cannot use styled-components directly: put it in 'use client' files and add the
   registry / `compiler.styledComponents: true` in next.config.js.)

9. STATUS NOTE: styled-components entered maintenance mode (announced 2025).
   Still widely used in existing codebases and asked in interviews; for new projects consider
   CSS Modules, Tailwind or zero-runtime libs (Panda CSS, vanilla-extract, Linaria).
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. INSTALL:   npm i styled-components      (अभी v6; React 16.8+)

2. Styled component बनाओ (tagged template literal):
       const Button = styled.button`
         padding: 8px 16px;
         background: ${props => props.$primary ? '#e23744' : '#eee'};
       `;
   -> यह एक React component लौटाता है जो <button class="sc-abc123 xyz789"> render करता है।

3. Normal component की तरह use करो:   <Button $primary>Buy</Button>
   Transient props: $ से शुरू होने वाले props सिर्फ styling के लिए हैं, DOM तक नहीं जाते।

4. EXTEND:     const BigButton = styled(Button)`font-size: 20px;`;
   Tag बदलना:   <Button as="a" href="/">Link</Button>

5. Sass जैसा NESTING:  &:hover { ... }   & + & { ... }   ${Icon} { margin-right: 4px; }

6. THEME:
       <ThemeProvider theme={{ colors: { brand: '#e23744' } }}>
       const Title = styled.h1` color: ${({ theme }) => theme.colors.brand}; `;

7. HELPERS: css``, createGlobalStyle``, keyframes``, .attrs()

8. यह runtime पर hash बनाकर class बनाता है और <style> tag inject करता है।
   (Runtime cost है। Next.js App Router में Server Components में सीधे नहीं चलता:
   'use client' files में रखो और registry / compiler.styledComponents: true जोड़ो।)

9. STATUS: styled-components maintenance mode में है (2025 की घोषणा)। पुराने projects और
   interviews में अब भी आम है; नए projects के लिए CSS Modules, Tailwind या zero-runtime
   libraries (Panda CSS, vanilla-extract) देखो।
```

---

## 🟡 Real World Example
**Many React apps (older Airbnb-style design systems, Spotify web player components, Atlassian-era dashboards) used styled-components** for a themable button/card library: `<Button variant="danger" size="lg">` changes color and padding from props, and switching `ThemeProvider` from light to dark theme restyles the whole app without touching any CSS file.

## 🟡 Real Example Hindi mein
**कई React apps (पुराने design systems, music player जैसे components, dashboards) में styled-components use हुआ:** `<Button variant="danger" size="lg">` से props के हिसाब से color और padding बदलता है, और `ThemeProvider` में light से dark theme बदलते ही पूरा app बिना किसी CSS file को छुए restyle हो जाता है।

---

## 💻 Live Code Example

Runs directly in a browser (needs internet): React 18 + Babel + styled-components v5 via CDN. In a real project use `npm i styled-components` and a bundler.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>styled-components Demo</title>

  <!-- React 18 + ReactDOM (UMD builds) -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <!-- styled-components v5 UMD (needs the 'react-is' global first) -->
  <script crossorigin src="https://unpkg.com/react-is@18/umd/react-is.development.js"></script>
  <script crossorigin src="https://unpkg.com/styled-components@5.3.11/dist/styled-components.min.js"></script>
  <!-- Babel to compile JSX in the browser (learning only) -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    // UMD global is "styled", plus ThemeProvider, createGlobalStyle, keyframes
    const styled = window.styled;
    const { ThemeProvider, createGlobalStyle, keyframes, css } = styled;

    // 1. GLOBAL STYLES (reset) : rendered once
    const GlobalStyle = createGlobalStyle`
      * { box-sizing: border-box; }
      body { margin: 0; font-family: system-ui, sans-serif;
             background: ${({ theme }) => theme.bg}; color: ${({ theme }) => theme.text};
             transition: background .2s; }
    `;

    // 2. THEMES: plain JS objects
    const light = { bg: '#f5f5f7', text: '#111', card: '#fff', brand: '#e23744' };
    const dark  = { bg: '#0f172a', text: '#f1f5f9', card: '#1e293b', brand: '#fb7185' };

    // 3. KEYFRAMES: scoped animation name
    const pop = keyframes`
      from { transform: scale(.95); opacity: 0; }
      to   { transform: scale(1);   opacity: 1; }
    `;

    // 4. STYLED COMPONENT using theme
    const Card = styled.div`
      background: ${({ theme }) => theme.card};
      border-radius: 12px;
      padding: 20px;
      max-width: 340px;
      margin: 24px auto;
      box-shadow: 0 4px 14px rgb(0 0 0 / .12);
      animation: ${pop} .3s ease-out;
    `;

    // 5. STYLED COMPONENT with PROPS. "$" = transient prop (not passed to the DOM)
    const Button = styled.button`
      padding: 10px 18px;
      margin-right: 8px;
      border: 2px solid ${({ theme }) => theme.brand};
      border-radius: 8px;
      cursor: pointer;
      font-size: ${({ $size }) => ($size === 'lg' ? '1.1rem' : '0.9rem')};
      background: ${({ $primary, theme }) => ($primary ? theme.brand : 'transparent')};
      color: ${({ $primary, theme }) => ($primary ? '#fff' : theme.brand)};

      /* Nesting with & works like Sass */
      &:hover { opacity: .85; }
      &:disabled { opacity: .4; cursor: not-allowed; }
    `;

    // 6. EXTENDING: same styles + changes
    const PillButton = styled(Button)`
      border-radius: 999px;
    `;

    // 7. Reusable css`` snippet
    const truncate = css`
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    `;
    const Title = styled.h2`
      margin: 0 0 8px;
      ${truncate}
    `;

    function App() {
      const [isDark, setIsDark] = React.useState(false);
      return (
        <ThemeProvider theme={isDark ? dark : light}>
          <GlobalStyle />
          <Card>
            <Title>Biryani House with a very long restaurant name</Title>
            <p>Rating 4.5 &middot; 30 min</p>
            <Button $primary $size="lg">Order</Button>
            <PillButton>Save</PillButton>
            {/* "as" changes the rendered tag */}
            <Button as="a" href="#" style={{ display: 'inline-block', marginTop: 12 }}>Link</Button>
          </Card>
          <div style={{ textAlign: 'center' }}>
            <Button onClick={() => setIsDark(d => !d)}>Toggle theme</Button>
          </div>
        </ThemeProvider>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Normal React project (Vite): npm i styled-components
import styled from 'styled-components';
const Wrapper = styled.section`display: grid; gap: 16px;`;

// 2. Next.js App Router: styled-components needs client rendering + SSR registry
// next.config.js
module.exports = { compiler: { styledComponents: true } };  // better class names, SSR support

// lib/registry.jsx
'use client';
import { useServerInsertedHTML } from 'next/navigation';
import { ServerStyleSheet, StyleSheetManager } from 'styled-components';
import { useState } from 'react';
export default function StyledComponentsRegistry({ children }) {
  const [sheet] = useState(() => new ServerStyleSheet());
  useServerInsertedHTML(() => { const s = sheet.getStyleElement(); sheet.instance.clearTag(); return <>{s}</>; });
  if (typeof window !== 'undefined') return <>{children}</>;
  return <StyleSheetManager sheet={sheet.instance}>{children}</StyleSheetManager>;
}
// Wrap <body> children with <StyledComponentsRegistry> in app/layout.jsx.
// Any file defining styled components must be (or be imported by) a 'use client' file.

// 3. TypeScript props
interface BtnProps { $primary?: boolean }
const Btn = styled.button<BtnProps>`background: ${p => (p.$primary ? 'red' : 'none')};`;

// 4. Alternatives: CSS Modules, Tailwind (zero runtime), Emotion (similar API),
//    Panda CSS / vanilla-extract (CSS-in-JS with zero runtime).
```

---

## ⚫ Interview Questions + Answers

**Q1: What is styled-components and how does it work?**
A1: A CSS-in-JS library. `styled.div\`...\`` creates a React component. At runtime it hashes the CSS, generates a unique class name, injects it in a `<style>` tag and applies the class to the element. Styles can use JS interpolations (props, theme).

**Q2: How do you style based on props? What are transient props?**
A2: Use a function interpolation: `color: ${p => p.$active ? 'red' : 'black'}`. Props prefixed with `$` (transient props) are consumed by styled-components and not forwarded to the DOM element, so you avoid React "unknown prop" warnings and invalid HTML attributes.

**Q3: What are the pros and cons compared with CSS Modules and Tailwind?**
A3: Pros: co-location, dynamic styling with props, theming, no class naming, dead-style elimination. Cons: runtime cost (JS parses and injects styles), larger bundle, extra SSR setup, not directly usable in React Server Components, and the project is in maintenance mode. CSS Modules/Tailwind generate static CSS at build time.

**Q4: How do you implement theming and global styles?**
A4: Wrap the app in `<ThemeProvider theme={obj}>` and access `props.theme` in any styled component. Use `createGlobalStyle` for resets and body styles. Switch the theme object to implement dark mode.

**Q5: How do you extend or reuse styles?**
A5: `styled(BaseComponent)\`...\`` extends; `as` prop changes the tag; `css\`\`` helper creates reusable snippets; `.attrs()` sets default props/attributes; interpolating another styled component (`${Icon} { ... }`) targets it inside a parent's styles.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Defining styled components inside a render function
```jsx
/* WRONG: new component every render -> remounts, loses state, slow */
function Page() { const Box = styled.div`...`; return <Box/>; }
/* CORRECT: define at module level (outside components) */
const Box = styled.div`...`;
function Page() { return <Box/>; }
```

❌ **Mistake 2:** Passing styling props to the DOM
```jsx
/* WRONG: <Box primary> -> warning "primary" attribute leaks into the DOM (non-transient) */
/* CORRECT: <Box $primary> */
```

❌ **Mistake 3:** Using styled-components directly in a Next.js Server Component
```jsx
/* WRONG: error "createContext only works in Client Components" */
/* CORRECT: add 'use client' at top of the file (and set up the registry) */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSS-in-JS | Writing CSS inside JavaScript | JS के अंदर CSS |
| Tagged template | `fn\`...\`` syntax used by styled | Backtick वाला function call |
| Transient prop | `$prop` not passed to DOM | DOM तक न जाने वाला prop |
| ThemeProvider | Supplies theme to all components | सबको theme देने वाला |
| createGlobalStyle | Injects global CSS | Global CSS डालना |
| keyframes | Scoped animation definition | Scoped animation |
| Runtime cost | Work done in browser to make styles | Browser में लगने वाला काम |

---

## ⚡ 3-Line Summary
**English:**
1. styled-components lets you write real CSS in JS tagged templates, creating scoped, reusable styled React components.
2. Props, `$transient` props and `ThemeProvider` make dynamic styling and theming easy; `css`, `keyframes`, `createGlobalStyle` help reuse.
3. It has runtime cost, needs client components plus an SSR registry in Next.js, and is in maintenance mode, so weigh CSS Modules or Tailwind for new projects.

**Hindi:**
1. styled-components से tagged templates में असली CSS लिखकर scoped, reusable styled React components बनते हैं।
2. Props, `$transient` props और `ThemeProvider` से dynamic styling और theming आसान; `css`, `keyframes`, `createGlobalStyle` reuse में मदद करते हैं।
3. इसमें runtime cost है, Next.js में client components और SSR registry चाहिए, और यह maintenance mode में है; नए projects में CSS Modules या Tailwind सोचो।

---

## ➡️ Next Topic
**111. Build a Responsive Navbar** — अब theory से practice: Advanced CSS section खत्म, और पहला interview problem, जिसमें flexbox, media queries और hamburger toggle सब जुड़ेंगे।
