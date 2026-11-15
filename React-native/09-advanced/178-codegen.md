# 178. Codegen
# हिंदी में: Codegen (Spec से अपने आप Native Code)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Codegen runs automatically during Gradle build / `pod install` when New Architecture is enabled. Run commands below are **not run** here.

---

## 🔵 Simple Definition (English)
**Codegen** reads your typed JS/TS **spec** files (`NativeXxx.ts`, `XxxNativeComponent.ts`) and automatically **generates** native glue code (C++, Java, Objective-C++) so JS and native agree on method names and types.

## 🔵 सरल परिभाषा (Hindi)
**Codegen** आपके typed JS/TS **spec** files (`NativeXxx.ts`, `XxxNativeComponent.ts`) को पढ़कर native glue code (C++, Java, Objective-C++) **अपने आप बनाता** है, ताकि JS और native में method names और types एक जैसे रहें।

---

## 🔴 Problem it Solves
```
❌ Hand-written bridge code: typo in method name -> crash at runtime
❌ Type mismatch (JS sends string, native expects number) -> silent bugs
❌ Duplicate boilerplate for Android + iOS
✅ One TS spec = typed, generated code = compile-time errors
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ हाथ से लिखा bridge code: method name में typo -> runtime crash
❌ Type mismatch (JS string भेजे, native number माँगे) -> छुपे bugs
❌ Android + iOS के लिए duplicate boilerplate
✅ एक TS spec = typed generated code = compile time पर error
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Write spec: src/NativeXxx.ts (TurboModule) or XxxNativeComponent.ts
Step 2 → package.json: add "codegenConfig" {name, type, jsSrcsDir, android.javaPackageName}
Step 3 → Build starts (Gradle task generateCodegenArtifactsFromSchema / pod install)
Step 4 → Codegen parses specs into a JSON schema
Step 5 → Generates: Java abstract classes, ObjC++ protocols, C++ props/event emitters
Step 6 → You implement generated interfaces in native code
Step 7 → Mismatched signature -> compile error (not a runtime crash)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Spec लिखो: src/NativeXxx.ts (TurboModule) या XxxNativeComponent.ts
Step 2 → package.json में "codegenConfig" जोड़ो
Step 3 → Build पर Gradle task / pod install Codegen चलाता है
Step 4 → Codegen specs से JSON schema बनाता है
Step 5 → Java abstract classes, ObjC++ protocols, C++ props/event emitters generate करता है
Step 6 → आप generated interfaces को native में implement करते हो
Step 7 → Signature गलत हो -> compile error (runtime crash नहीं)
```

---

## 🟡 Real World Example
A **Paytm-style** SDK team keeps one `NativePaymentSdk.ts` spec. Android (Kotlin) and iOS (Swift/ObjC++) engineers both implement the generated interface. When someone changes `pay(amount: number)` to `pay(amount: string)`, both builds fail immediately, instead of crashing in production.

## 🟡 Real Example Hindi mein
**Paytm जैसी** SDK team एक `NativePaymentSdk.ts` spec रखती है। Android (Kotlin) और iOS (Swift/ObjC++) engineers दोनों generated interface implement करते हैं। कोई `pay(amount: number)` को `pay(amount: string)` कर दे तो दोनों builds तुरंत fail होते हैं — production crash की जगह।

---

## 💻 Code Example — Basic
```ts
// src/NativeCalculator.ts — module spec (Codegen input)
import type { TurboModule } from 'react-native';        // base type
import { TurboModuleRegistry } from 'react-native';     // runtime lookup

export interface Spec extends TurboModule {
  add(a: number, b: number): number;                    // sync method -> double, double -> double
  multiplyAsync(a: number, b: number): Promise<number>; // async method
  getConfig(): { appName: string; debug: boolean };     // object return type
  // callback style: first param to JS callback
  onDone(callback: (result: string) => void): void;
}

export default TurboModuleRegistry.getEnforcing<Spec>('NativeCalculator'); // name used by native
```
```json
{
  "name": "react-native-calculator",
  "version": "1.0.0",
  "codegenConfig": {
    "name": "CalculatorSpec",
    "type": "modules",
    "jsSrcsDir": "src",
    "android": { "javaPackageName": "com.calculator" }
  }
}
```

## 💻 Code Example — Advanced
```ts
// src/NativeGaugeViewNativeComponent.ts — component spec with typed props + default values + events
import type { ViewProps, HostComponent, ColorValue } from 'react-native';
import type {
  Float, Int32, WithDefault, DirectEventHandler,
} from 'react-native/Libraries/Types/CodegenTypes';        // Codegen helper types
import codegenNativeComponent from 'react-native/Libraries/Utilities/codegenNativeComponent';

// event payload type
type ChangeEvent = Readonly<{ value: Float }>;

export interface NativeProps extends ViewProps {
  value?: WithDefault<Float, 0>;                 // default 0 when JS omits it
  max?: WithDefault<Int32, 100>;                 // default 100
  trackColor?: ColorValue;                       // RN color type
  label?: string;                                // plain string prop
  onValueChange?: DirectEventHandler<ChangeEvent>; // native -> JS event
}

export default codegenNativeComponent<NativeProps>('GaugeView') as HostComponent<NativeProps>;
```
```bash
# Inspect what Codegen produced (after a build):
# Android: android/build/generated/source/codegen/java/com/facebook/react/viewmanagers/
# iOS:     ios/build/generated/ios/  (path may differ by RN version)
# Run codegen manually for an app (RN CLI) — check your RN version's docs for exact script:
node node_modules/react-native/scripts/generate-codegen-artifacts.js --help
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Output | Java abstract classes + C++ JNI | ObjC++ protocols + C++ |
| Trigger | Gradle build task | `pod install` |
| You implement | `NativeXxxSpec` subclass | `<NativeXxxSpec>` protocol |
| Config | `android.javaPackageName` | `ios` (library name via `name`) |
| Output location | `android/build/generated/...` | `ios/build/generated/...` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo apps run Codegen when you build native code
npx expo prebuild --clean     # generate android/ios
npx expo run:android          # Gradle runs Codegen automatically
# Expo Go cannot run your custom specs.
```
CLI way:
```bash
cd ios && bundle exec pod install   # runs Codegen for iOS
npx react-native run-android        # Gradle runs Codegen for Android
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Editing generated files by hand
✅ Correct: They are overwritten on every build; change the spec.

❌ Mistake 2: Using unsupported TS types
✅ Correct: Stick to `string, number, boolean, Object, Array<T>, Promise<T>`, `Int32/Float/Double`, `WithDefault`, enums limited to literal unions.

❌ Mistake 3: Wrong `jsSrcsDir` or file naming
✅ Correct: Keep specs in `jsSrcsDir`; module files start with `Native`, component files end with `NativeComponent`.

---

## 🧠 Tricky Interview Question
**Q: You add a new method to the spec, build succeeds on iOS but fails on Android. Why is that actually good?**

**Answer:** Codegen generated an abstract method in the Java base class; the Android implementation does not override it yet, so the compiler fails. That is the whole point: the spec forces both platforms to implement every method, catching missing code at build time instead of runtime.

---

## ⚫ Interview Questions + Answers

**Q1: What does Codegen consume and produce?**
A1: Consumes typed spec files; produces native interfaces, C++ props/events and module glue.

**Q2: Where is it configured?**
A2: `codegenConfig` in `package.json`.

**Q3: What does `type` accept?**
A3: `modules`, `components`, or `all`.

**Q4: When does it run?**
A4: During native builds (Gradle / `pod install`) when New Architecture is on.

**Q5: Does Codegen need Flow or TypeScript?**
A5: Either; both are supported spec languages.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing TurboModules / Fabric components
- You want compile-time safety between JS and native

❌ Avoid when:
- Using only JS/Expo packages (nothing to generate)

---

## 📊 Visual Diagram
```
 NativeXxx.ts (spec)
       │ parse
       ▼
   JSON schema
    ├──► Java abstract class (Android)
    ├──► ObjC++ protocol (iOS)
    └──► C++ props / event emitters (shared)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Spec | Typed interface file | Typed interface file |
| Schema | Parsed JSON form | Parse किया JSON रूप |
| codegenConfig | package.json settings | Codegen settings |
| jsSrcsDir | Folder with specs | Specs का folder |
| WithDefault | Prop default value | Prop का default |
| DirectEventHandler | Event prop type | Event prop का type |

---

## ⚡ 3-Line Summary
**English:**
1. Codegen turns TS specs into typed native glue code.
2. It runs automatically at build time via `codegenConfig`.
3. Missing/mismatched methods fail at compile time.

**Hindi:**
1. Codegen TS specs को typed native glue code में बदलता है।
2. `codegenConfig` से build के समय अपने आप चलता है।
3. Missing/mismatch methods compile time पर पकड़े जाते हैं।

---

## ➡️ Next Topic
**179. C++ in React Native** — एक बार C++ लिखो, दोनों platforms पर चलाओ।
