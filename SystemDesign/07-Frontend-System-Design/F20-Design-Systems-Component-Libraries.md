# F20. Design Systems + Component Libraries
# हिंदी में: Design System — पूरी कंपनी के लिए UI की एक साझा भाषा: रंग, font, spacing के नियम (design tokens), तैयार components (Button, Modal, Input), उनके इस्तेमाल के नियम और documentation — ताकि हर टीम एक जैसा, accessible और तेज़ UI बनाए

---

## 🔵 Simple Definition (English)
A **design system** is the **single source of truth for building UI** across products and teams. It includes:
- **Design tokens**: named values for colour, typography, spacing, radius, shadows, motion and breakpoints (`color.brand.primary = #FC8019`, `space.4 = 16px`), shared between design (Figma) and code (CSS variables, JS/TS, React Native styles).
- **Component library**: reusable, tested, accessible components (Button, Input, Select, Modal, Toast, Tabs, Card, DataTable), with a clear **API (props)**, variants and states.
- **Patterns & guidelines**: how to compose components (forms, empty states, error handling, navigation), content style (tone, i18n), accessibility rules.
- **Tooling & governance**: Storybook docs, visual regression tests, versioning (semver), contribution process, adoption metrics.
Examples: Google **Material**, Apple HIG, Shopify **Polaris**, Atlassian, IBM **Carbon**, GitHub **Primer**; headless primitives like **Radix**, **React Aria**; styling via **Tailwind**, CSS Modules, vanilla-extract.

## 🔵 सरल परिभाषा (Hindi)
Design system = पूरी कंपनी के UI का एक ही सच्चा स्रोत: design tokens (रंग, font, spacing के नाम वाले मान — Figma और code दोनों में एक जैसे), तैयार और जाँचे हुए components (Button, Modal, Input — accessible), इस्तेमाल के नियम (forms, empty/error states), और tooling (Storybook docs, visual tests, versioning, योगदान का तरीका)।
उदाहरण: Material, Polaris, Carbon, Primer; headless primitives जैसे Radix, React Aria।

---

## 🔴 Problem it Solves
As a company grows to many teams and products (customer app, restaurant/seller panel, delivery app, admin):
- **Inconsistent UI**: 14 shades of orange, 9 button styles, different modals per team.
- **Duplicated effort**: every team builds its own date picker, dropdown and table, each with bugs.
- **Accessibility and i18n regress** because every custom component re-solves focus, ARIA and RTL (often badly).
- **Rebranding or dark mode** means editing thousands of hard-coded colours.
- **Slow design → dev handoff**: pixel debates, no shared vocabulary.

A design system gives **consistency, speed (build features from blocks), quality (a11y, performance baked in) and easy theming**.

## 🔴 यह क्यों बना? (Hindi)
कंपनी बढ़ने पर (customer app, restaurant panel, delivery app, admin) हर टीम अपना UI बनाती है: नारंगी के 14 रंग, 9 तरह के buttons, अलग-अलग modals; हर टीम अपना date picker/table बनाती है — bugs के साथ; accessibility और RTL हर बार टूटते हैं; rebrand या dark mode के लिए हज़ारों जगह रंग बदलने पड़ते हैं।
Design system = एकरूपता, तेज़ी (तैयार blocks से features), गुणवत्ता (a11y, performance पहले से), और आसान theming।

---

## 🟢 How it Works — Step by Step

### Layers

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Products: Customer web (Next.js) · Customer app (RN) · Partner panel · Admin│
├───────────────────────────────────────────────────────────────────────────┤
│ Patterns / templates: checkout form, list+filters page, empty states       │
├───────────────────────────────────────────────────────────────────────────┤
│ Components: Button, IconButton, Input, Select, Combobox, Modal, Toast,     │
│             Tabs, Card, Badge, Skeleton, DataTable, DatePicker              │
├───────────────────────────────────────────────────────────────────────────┤
│ Primitives (headless behaviour + a11y): Radix / React Aria / custom hooks  │
├───────────────────────────────────────────────────────────────────────────┤
│ Design tokens: color, typography, spacing, radius, elevation, motion, z    │
│   (source: JSON/Figma Variables → Style Dictionary → CSS vars, TS, RN)     │
└───────────────────────────────────────────────────────────────────────────┘
```

### Tokens: global → semantic → component

```
Global (raw):     orange.500 = #FC8019, gray.900 = #1C1C1C, space.4 = 16
Semantic (intent): color.action.primary = {orange.500}, color.text.default = {gray.900},
                   color.bg.surface = white (light) / #121212 (dark)
Component:        button.primary.bg = {color.action.primary}
→ Themes (dark mode, brand B, high contrast) swap semantic values; components never use raw hex
Pipeline: tokens.json (or Figma Variables) → Style Dictionary → tokens.css (CSS vars), tokens.ts, RN theme
```

### Component API design principles

```
- Small, consistent prop vocabulary: variant ("primary"|"secondary"|"ghost"), size ("sm"|"md"|"lg"),
  tone ("danger"), isDisabled/isLoading — same names everywhere
- Accessible by default: correct roles, keyboard, focus, labels required (TS forces aria-label for IconButton)
- Composition over configuration: <Card><Card.Header/><Card.Body/></Card> or slots, instead of 40 props
- Controlled + uncontrolled modes (value/onChange and defaultValue)
- Forward refs, spread rest props to the root (className, data-*, aria-*)
- Polymorphism where useful: <Button as="a" href> or asChild (Radix)
- i18n-ready: no hard-coded text inside components (labels passed in), RTL via logical CSS
- Performance: tree-shakable exports, no heavy deps in core, CSS without runtime cost
```

### Styling approach options

```
CSS variables + CSS Modules / vanilla-extract → zero runtime, themeable ✅
Tailwind with token-based config (theme.extend.colors from tokens) → fast, consistent ✅
CSS-in-JS runtime (styled-components/Emotion) → flexible but runtime cost; issues with RSC ⚠️
React Native: StyleSheet + theme object, or Tamagui / NativeWind / Restyle / Unistyles
Cross-platform: share tokens + behaviour hooks; separate web and native renderers (or React Native Web)
```

### Distribution, versioning, governance

```
Monorepo package: @quickbite/tokens, @quickbite/ui-web, @quickbite/ui-native, @quickbite/icons
Semver + changesets → CHANGELOG; deprecate before removal; codemods for breaking changes
Docs: Storybook (props table, a11y addon, interactive examples) + usage guidelines; Figma library in sync
Quality gates: unit tests (Testing Library), a11y tests (axe), visual regression (Chromatic/Playwright screenshots)
Governance: core team + contribution model (RFC → review → release), adoption dashboards (usage per component)
```

## 🟢 कैसे काम करता है? (Hindi)
1. परतें: tokens (रंग, spacing) → primitives (behaviour + a11y, जैसे Radix) → components (Button, Modal) → patterns (checkout form) → products।
2. Tokens तीन स्तर पर: raw (`orange.500`), semantic (`color.action.primary`), component (`button.primary.bg`); dark mode/नया brand = सिर्फ़ semantic मान बदलो; Style Dictionary से CSS vars, TS और RN theme बनें।
3. Component API: हर जगह एक जैसे prop नाम (variant, size, isLoading), default से accessible, composition (`<Card.Header>`), controlled/uncontrolled दोनों, ref forward, कोई hard-coded text नहीं।
4. Styling: CSS variables + CSS Modules या Tailwind (बिना runtime ख़र्च); RN के लिए theme object या Tamagui/NativeWind; tokens और logic साझा, renderer अलग।
5. Monorepo packages + semver + changelog + codemods; Storybook docs, axe a11y tests, visual regression; योगदान का तरीका और usage dashboard।

---

## 🟡 Real World Example

**Shopify Polaris** — the design system for the Shopify admin and apps. Thousands of third-party app developers use it so their apps feel native to Shopify, with tokens, React components, content and a11y guidelines.

**Google Material Design** — spans Android, web and Flutter, with Material 3 dynamic colour derived from the user's wallpaper via token-based theming.

**Atlassian Design System** — unified Jira, Confluence and Trello UIs with tokens, which enabled dark mode across products by switching semantic tokens.

**Indian companies (Razorpay Blade, CRED NeoPOP, Swiggy, Zomato)** — Razorpay open-sourced **Blade**, a cross-platform (web and React Native) design system with tokens and accessibility built in. CRED open-sourced **NeoPOP**, its distinctive visual design system.

## 🟡 Real Example Hindi में
Shopify Polaris से हज़ारों third-party apps Shopify जैसी दिखती हैं; Material Design में wallpaper से रंग लेकर token theming; Atlassian ने semantic tokens बदलकर Jira/Confluence में dark mode दिया।
भारत में Razorpay ने **Blade** open-source किया — web और React Native दोनों के लिए, tokens और accessibility के साथ; CRED का **NeoPOP** भी open-source design system है।

---

## 🟠 My Stack Example

### Tokens (JSON) → Style Dictionary → CSS variables, TS, RN
```json
// tokens/color.json
{ "color": {
    "orange": { "500": { "value": "#FC8019" } }, "gray": { "900": { "value": "#1C1C1C" } },
    "action": { "primary": { "value": "{color.orange.500}" } },
    "text": { "default": { "value": "{color.gray.900}" } } },
  "space": { "2": { "value": "8px" }, "4": { "value": "16px" } }, "radius": { "md": { "value": "8px" } } }
```
```css
/* generated tokens.css — dark theme overrides semantic vars */
:root { --color-action-primary: #FC8019; --color-text-default: #1C1C1C; --color-bg-surface: #fff; --space-4: 16px; --radius-md: 8px; }
[data-theme='dark'] { --color-text-default: #F2F2F2; --color-bg-surface: #121212; }
```

### Accessible, typed Button (web)
```tsx
// packages/ui-web/src/Button.tsx
import { forwardRef } from 'react';
import { Slot } from '@radix-ui/react-slot';
import clsx from 'clsx';
import s from './Button.module.css';

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost'; size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean; asChild?: boolean;
};
export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = 'primary', size = 'md', isLoading, asChild, disabled, children, className, ...rest }, ref) {
  const Comp = asChild ? Slot : 'button';
  return (
    <Comp ref={ref} className={clsx(s.btn, s[variant], s[size], className)}
          disabled={disabled || isLoading} aria-busy={isLoading || undefined} {...rest}>
      {isLoading ? <span className={s.spinner} aria-hidden="true" /> : null}
      <span className={isLoading ? s.hiddenLabel : undefined}>{children}</span>
    </Comp>
  );
});

// IconButton REQUIRES an accessible label at the type level
type IconButtonProps = Omit<Props, 'children'> & { icon: React.ReactNode; 'aria-label': string };
export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(({ icon, ...p }, ref) => <Button ref={ref} {...p}>{icon}</Button>);
```
```css
/* Button.module.css — uses semantic tokens, logical properties */
.btn { border-radius: var(--radius-md); padding-block: var(--space-2); padding-inline: var(--space-4); min-height: 44px; }
.primary { background: var(--color-action-primary); color: #fff; }
.btn:focus-visible { outline: 3px solid var(--color-focus, #1a73e8); outline-offset: 2px; }
```

### Compound component with headless primitive (Modal on Radix Dialog)
```tsx
import * as Dialog from '@radix-ui/react-dialog';
export const Modal = {
  Root: Dialog.Root, Trigger: Dialog.Trigger,
  Content: ({ title, children }: { title: string; children: React.ReactNode }) => (
    <Dialog.Portal>
      <Dialog.Overlay className="overlay" />
      <Dialog.Content className="modal">                {/* focus trap, Esc, aria-modal handled */}
        <Dialog.Title>{title}</Dialog.Title>{children}
        <Dialog.Close asChild><IconButton icon={<XIcon />} aria-label="Close" variant="ghost" /></Dialog.Close>
      </Dialog.Content>
    </Dialog.Portal>
  ),
};
```

### React Native counterpart using the same tokens
```tsx
// packages/ui-native/src/Button.tsx
import { tokens } from '@quickbite/tokens';            // generated TS
export function Button({ title, onPress, variant = 'primary', isLoading, disabled }: NativeButtonProps) {
  return (
    <Pressable onPress={onPress} disabled={disabled || isLoading} accessibilityRole="button"
      accessibilityState={{ disabled: disabled || isLoading, busy: isLoading }}
      style={({ pressed }) => [{ minHeight: 48, borderRadius: tokens.radius.md, paddingHorizontal: tokens.space[4],
        backgroundColor: variant === 'primary' ? tokens.color.action.primary : 'transparent', opacity: pressed ? 0.85 : 1,
        alignItems: 'center', justifyContent: 'center' }]}>
      {isLoading ? <ActivityIndicator color="#fff" /> : <Text style={{ color: '#fff', fontWeight: '600' }}>{title}</Text>}
    </Pressable>
  );
}
```

### Storybook story + visual/a11y tests
```tsx
// Button.stories.tsx
export default { title: 'Actions/Button', component: Button, parameters: { a11y: { test: 'error' } } };
export const Primary = { args: { children: 'Place order' } };
export const Loading = { args: { children: 'Placing…', isLoading: true } };
// CI: storybook test-runner + axe, Chromatic/Playwright screenshots on PR → catch visual regressions
```

### Release with changesets (monorepo)
```bash
npx changeset          # "minor: add Button size 'lg'"
npx changeset version  # bump versions + CHANGELOG
npx changeset publish  # publish @quickbite/ui-web to private npm registry (GitHub Packages)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a design system and what does it contain?**
A1: It's a shared source of truth for building UI consistently across products. It contains design tokens (colour, type, spacing, radius, elevation, motion), a component library with documented APIs, variants and states, accessibility built in, usage guidelines and patterns (forms, errors, empty states, content style), Figma libraries synced with code, and tooling and governance (Storybook docs, tests, versioning, contribution process, adoption tracking). It speeds up delivery, ensures consistency and quality, and makes theming and rebranding cheap.

**Q2: What are design tokens and why use semantic tokens?**
A2: Tokens are named, platform-agnostic design values stored in a source format (JSON or Figma Variables) and transformed into CSS variables, TS constants and native themes. Global tokens hold raw values (`orange.500`). Semantic tokens express intent (`color.action.primary`, `color.bg.surface`) and reference global ones. Components use semantic tokens, so themes like dark mode, high contrast or sub-brands are just different mappings of semantic to raw values, with no component changes.

**Q3: How do you design a good component API?**
A3: Keep a consistent, minimal prop vocabulary across components (variant, size, tone, isDisabled, isLoading). Make the accessible path the default and enforce required labels with TypeScript. Prefer composition (compound components or slots) over many boolean props. Support controlled and uncontrolled usage, forward refs and pass through native attributes. Allow polymorphism (`as`/`asChild`) carefully. Avoid hard-coded text (i18n) and directional CSS (RTL). Keep components tree-shakable and lightweight, and document with examples and do's and don'ts.

**Q4: How do you roll out breaking changes to a design system used by 20 teams?**
A4: Use semantic versioning and changelogs. Deprecate first with console warnings and docs, providing the replacement. Ship codemods (jscodeshift) to automate migrations. Support old and new versions in parallel for a period, use adoption dashboards to track who's on which version, communicate via release notes and office hours, and batch breaking changes into planned majors. Visual regression tests in consumer apps catch unintended changes.

**Q5: How would you share a design system between React web and React Native?**
A5: Share the token source (generated into CSS variables for web and a TS theme for RN), shared TypeScript types and prop contracts, and headless logic hooks (state, formatting, validation), while implementing platform-specific renderers (DOM elements with CSS versus RN primitives with StyleSheet) for native look, performance and accessibility. Alternatives: React Native Web or universal libraries (Tamagui, NativeWind, Razorpay Blade's approach) for higher code reuse, trading some platform fidelity.

---

## 🔷 Trade-offs
✅ Consistency, speed, accessibility, easy theming, shared vocabulary between design & dev.
❌ Upfront investment + dedicated team; can become a bottleneck if governance is too rigid.
❌ Over-generalized components get bloated; too rigid → teams fork/detach.
✅ Headless primitives (Radix/React Aria): a11y solved — ❌ styling and wrapping effort.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Design system | Shared UI source of truth | साझा UI नियम और components |
| Design token | Named design value | नाम वाला design मान |
| Semantic token | Intent-based token | उद्देश्य वाला token |
| Component library | Reusable UI components | दोबारा इस्तेमाल होने वाले components |
| Headless component | Behaviour without styles | बिना style का behaviour |
| Compound component | Composable sub-components | जोड़कर बनने वाले हिस्से |
| Theming | Swapping token values | रंग/रूप बदलना |
| Storybook | Component docs & playground | components का showroom |
| Visual regression | Screenshot diff testing | तस्वीर मिलाकर जाँच |
| Codemod | Automated code migration | अपने-आप code बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. Design system = tokens + accessible components + patterns/guidelines + tooling/governance, shared by design and code.
2. Use global → semantic → component tokens (Style Dictionary) so themes/dark mode are mappings; components follow a consistent, composable, accessible API.
3. Distribute via monorepo packages with semver, Storybook docs, a11y + visual tests, deprecations and codemods; share tokens/logic across web and RN.

**Hindi:**
1. Design system = tokens + accessible components + नियम + tooling, design और code दोनों के लिए।
2. Raw → semantic → component tokens; dark mode = mapping बदलना; components का API एक जैसा और accessible।
3. Monorepo packages, semver, Storybook, a11y/visual tests, codemods; web और RN में tokens/logic साझा।

---

## ➡️ Next Topic Suggestion
**F21. Micro-Frontends + Monorepo** — When many teams share one big frontend, how do you split ownership and deployments? Next: micro-frontend approaches (Module Federation, route-level splits), monorepos (Turborepo, Nx), and when each is worth it.
