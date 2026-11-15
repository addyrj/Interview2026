# 61. Styled Components in React Native
# हिंदी में: Styled Components — CSS-in-JS React Native में
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (React Native 0.76)**, `styled-components` v6 — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**styled-components** lets you write CSS-like text inside JavaScript to create styled components: ``const Title = styled.Text`font-size: 20px;` ``. In React Native you import from `styled-components/native`. The CSS text is converted to a normal RN style object (no real CSS engine runs).

## 🔵 सरल परिभाषा (Hindi)
**styled-components** में JavaScript के अंदर CSS जैसा text लिखकर styled components बनाते हैं: ``const Title = styled.Text`font-size: 20px;` ``। React Native में `styled-components/native` से import करते हैं। CSS text असल में RN style object में बदल जाता है (कोई असली CSS engine नहीं चलता)।

---

## 🔴 Problem it Solves
```
StyleSheet:
  Style alag file/section me, component alag
  Props ke hisaab se style = ternaries
  Theme har jagah manually pass karna

STYLED-COMPONENTS:
  ✅ Style component ke saath hi
  ✅ Props se direct: color: ${p => p.primary ? 'red' : 'gray'}
  ✅ ThemeProvider se global theme
  ✅ Web (React) wali team ke liye familiar
```

## 🔴 यह क्यों बना? (Hindi)
```
Web developers CSS-in-JS के आदी हैं।
Props और theme के हिसाब से style बदलना आसान होता है।
Component और उसका style एक ही जगह रहते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npm install styled-components  (check docs for RN-specific notes)
Step 2 → import styled from 'styled-components/native'
Step 3 → const Box = styled.View`padding: 16px;`
Step 4 → Library parses CSS text → React Native style object (css-to-react-native)
Step 5 → Interpolations ${props => ...} run on every render
Step 6 → Wrap app in <ThemeProvider theme={theme}> → props.theme in all styles
Step 7 → No units needed in RN but "px" is allowed and stripped; numbers only
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → styled-components install
Step 2 → styled-components/native से import
Step 3 → styled.View`...` से component बनाओ
Step 4 → CSS text → RN style object में convert होता है
Step 5 → ${props => ...} हर render पर चलता है
Step 6 → ThemeProvider से global theme मिलता है
```

---

## 🟡 Real World Example
**A Paytm-like button system:** `PrimaryButton`, `SecondaryButton`, `DangerButton` — all derived from one `Button` styled component with a `variant` prop. Brand color and spacing live in a theme object; switching to dark theme just changes the ThemeProvider value.

## 🟡 Real Example Hindi mein
**Paytm जैसा button system:** एक `Button` styled component और `variant` prop से `Primary`, `Secondary`, `Danger` बटन। Brand color और spacing theme object में; dark theme के लिए सिर्फ ThemeProvider की value बदलो।

---

## 💻 Code Example — Basic
```jsx
// Basic styled-components usage
import React from 'react'; // React
import styled from 'styled-components/native'; // NATIVE entry (not 'styled-components')

const Container = styled.View` /* a View with CSS text */
  flex: 1; /* take full height */
  justify-content: center; /* center vertically */
  align-items: center; /* center horizontally */
  background-color: #fff; /* white page */
`;

const Title = styled.Text` /* a Text */
  font-size: 22px; /* size (px is stripped → number) */
  font-weight: 700; /* bold */
  color: #e23744; /* Zomato red */
`;

export default function Basic() { // component
  return (
    <Container>{/* styled View */}
      <Title>Hello styled-components</Title>{/* styled Text */}
    </Container>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: theme + props-based variants + attrs + extending
import React from 'react'; // React
import styled, { ThemeProvider } from 'styled-components/native'; // styled + provider

const light = { bg: '#ffffff', text: '#111111', primary: '#5f259f', danger: '#d32f2f' }; // light theme
const dark = { bg: '#121212', text: '#f5f5f5', primary: '#b388ff', danger: '#ef5350' }; // dark theme

const Screen = styled.View` /* uses theme */
  flex: 1;
  padding: 16px;
  background-color: ${({ theme }) => theme.bg}; /* from ThemeProvider */
`;

const Label = styled.Text`
  color: ${({ theme }) => theme.text}; /* theme color */
  font-size: 16px;
  margin-bottom: 12px;
`;

// Button with variant prop: 'primary' | 'danger'
const Button = styled.Pressable.attrs({ android_ripple: { color: '#ffffff55' } })` /* attrs = default props */
  background-color: ${({ theme, variant }) => (variant === 'danger' ? theme.danger : theme.primary)}; /* pick by variant */
  padding: 14px;
  border-radius: 8px;
  align-items: center;
  opacity: ${({ disabled }) => (disabled ? 0.5 : 1)}; /* dynamic opacity */
`;

const ButtonText = styled.Text`
  color: #fff;
  font-weight: 700;
`;

// Extending: RoundedButton inherits Button styles and adds more
const PillButton = styled(Button)`
  border-radius: 999px; /* override radius */
`;

export default function App() {
  const [isDark, setDark] = React.useState(false); // theme switch state
  return (
    <ThemeProvider theme={isDark ? dark : light}>{/* provides props.theme */}
      <Screen>
        <Label>Wallet balance: ₹1,250</Label>
        <Button variant="primary" onPress={() => setDark((d) => !d)}>{/* toggle theme */}
          <ButtonText>Toggle theme</ButtonText>
        </Button>
        <PillButton variant="danger" disabled style={{ marginTop: 12 }}>{/* extra inline style still works */}
          <ButtonText>Delete account</ButtonText>
        </PillButton>
      </Screen>
    </ThemeProvider>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Library behavior | Same | Same |
| Shadow in CSS text | `elevation: 4;` works | `shadow-color`, `shadow-offset: 0px 2px;`, `shadow-opacity`, `shadow-radius` |
| Platform-specific style | `${Platform.select({ android: 'elevation: 4;', ios: '...' })}` | Same approach |
| Ripple | via `.attrs({ android_ripple })` | Not applicable |
| Performance | Style computed per render on JS thread | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: just install; no native linking
// npx expo install styled-components   (or npm i styled-components)
import styled from 'styled-components/native'; // import
const Box = styled.View`padding: 8px;`; // use
```
CLI way:
```jsx
// Bare CLI: npm i styled-components — pure JS, so no pod install needed
// (Babel plugin 'babel-plugin-styled-components' optional for better names)
import styled from 'styled-components/native'; // import
const Box = styled.View`padding: 8px;`; // same
```
Pure JS library: same in both.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `import styled from 'styled-components'` (web version).
✅ Correct: `import styled from 'styled-components/native'`.

❌ Mistake 2: Using web-only CSS (`display: grid`, `box-shadow`, `:hover`, media queries).
✅ Correct: Only RN-supported properties; use Flexbox.

❌ Mistake 3: Defining a styled component inside another component's render.
✅ Correct: Define at module level (otherwise a new component each render → remounts, state loss).

❌ Mistake 4: Passing custom prop (e.g. `variant`) and expecting no warnings in TypeScript.
✅ Correct: Type the props: `styled.Pressable<{ variant: 'primary' | 'danger' }>`. (v6 also has transient props `$variant` to avoid forwarding.)

---

## 🧠 Tricky Interview Question
**Q:** You wrote `const Box = styled.View` inside a component and the child's state resets on every parent render. Why?

**Answer:** Each render creates a brand-new component type (`Box` is a new function). React sees a different type, unmounts the old tree and mounts a new one, losing state. Move `styled.*` calls outside the component, to module scope.

---

## ⚫ Interview Questions + Answers
Q1: Does styled-components use real CSS in RN?
A1: No. It parses CSS text with `css-to-react-native` into style objects. Unsupported CSS fails or is ignored.

Q2: How do you theme an app?
A2: `<ThemeProvider theme={...}>` at root; read `props.theme` in interpolations.

Q3: StyleSheet vs styled-components performance?
A3: StyleSheet is slightly faster (static objects). styled-components does work at render time; usually fine, but avoid in huge lists with heavy interpolation.

Q4: How to avoid passing a prop to the underlying view?
A4: Use transient props with `$` prefix (v5.1+/v6), e.g. `$active`.

Q5: Alternatives?
A5: NativeWind (Tailwind), Restyle (Shopify), Tamagui, Unistyles, plain StyleSheet.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team knows web styled-components
- Prop-driven variants and theming

❌ Avoid when:
- Performance-critical heavy lists
- You already use NativeWind/Tailwind (avoid mixing approaches)
- Bundle size matters (adds a dependency)

---

## 📊 Visual Diagram
```
styled.View`padding: 16px;`
        │ parse (css-to-react-native)
        ▼
{ padding: 16 }
        │ + props/theme interpolations
        ▼
<View style={{padding:16}} />   → native view
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSS-in-JS | CSS written in JS | JS में CSS |
| ThemeProvider | Supplies theme to tree | Theme देने वाला |
| attrs | Default props for styled comp | Default props |
| Transient prop | `$prop` not forwarded | Forward न होने वाला prop |
| Interpolation | `${...}` inside template | Template में expression |

---

## ⚡ 3-Line Summary
English: Import from `styled-components/native` and write CSS text for RN components.
Props and `ThemeProvider` make variants and themes easy.
Define components at module level; no web-only CSS.

Hindi: `styled-components/native` से import करके RN components पर CSS text लिखो।
Props और `ThemeProvider` से variants और themes आसान हैं।
Components module level पर बनाओ; web-only CSS मत लिखो।

---

## ➡️ Next Topic
**62. NativeWind (Tailwind for RN)** — utility classes (`className="p-4 bg-red-500"`) se styling, aaj ka popular alternative.
