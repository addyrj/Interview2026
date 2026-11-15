# 286. Interview Problem: Build a Chat UI (WhatsApp style)
# हिंदी में: Chat UI बनाओ (WhatsApp जैसा)
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐ Medium | Asked at: Zomato, Swiggy, ShareChat, Hike, Slack-like apps

Files: `ChatScreen.jsx`, `MessageBubble.jsx`.
Target: Expo SDK 52 (check current docs — APIs change between SDKs). Core RN only.

---

## 🔵 Simple Definition (English)
A chat screen shows messages as bubbles (mine on the right, theirs on the left), keeps the newest message at the bottom, and has an input bar that stays above the keyboard.

## 🔵 सरल परिभाषा (Hindi)
Chat screen में messages bubbles की तरह दिखते हैं (मेरे दाईं तरफ, उनके बाईं तरफ), सबसे नया message नीचे रहता है, और input bar keyboard के ऊपर रहता है।

---

## 🔴 Problem it Solves
A normal list starts from the top, but chat must start from the bottom and keep the latest message visible when the keyboard opens. Also bubbles must not re-render on every key press.

## 🔴 यह क्यों बना? (Hindi)
सामान्य list ऊपर से शुरू होती है, लेकिन chat नीचे से शुरू होनी चाहिए और keyboard खुलने पर भी latest message दिखना चाहिए। साथ ही हर key press पर सारे bubbles re-render नहीं होने चाहिए।

---

## 🔴 Problem Statement
Build a chat screen: bubbles with time, mine vs theirs styles, an inverted list anchored to the bottom, a multiline input with Send button, empty messages ignored, and the input must not be hidden by the keyboard on iOS or Android.

## 💡 Approach
```
messages: NEWEST FIRST  (index 0 = bottom, because FlatList is `inverted`)
send: trim -> ignore empty -> [new, ...prev] -> clear input
MessageBubble = React.memo (only new rows render)
KeyboardAvoidingView: behavior='padding' on iOS, none on Android (window resizes)
keyboardShouldPersistTaps='handled' so Send works with one tap
```

## 🟢 How it Works — Step by Step
```
Step 1 → State holds messages (newest first) and the input text
Step 2 → FlatList with `inverted` renders index 0 at the bottom
Step 3 → User types -> only the input state changes; memoized bubbles stay as is
Step 4 → Send -> trim, skip if empty, prepend new message, clear the input
Step 5 → KeyboardAvoidingView lifts the input bar above the keyboard
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State में messages (नया पहले) और input text रखते हैं
Step 2 → `inverted` FlatList में index 0 नीचे दिखता है
Step 3 → User type करे तो सिर्फ input state बदलती है; memo वाले bubbles दोबारा नहीं बनते
Step 4 → Send -> trim, खाली हो तो रोक दो, नया message आगे जोड़ो, input साफ़ करो
Step 5 → KeyboardAvoidingView input bar को keyboard के ऊपर उठा देता है
```

---

## 🟡 Real World Example
WhatsApp, Telegram, Swiggy rider chat ("Call / Chat with delivery partner"), Zomato support chat, Ola driver chat, ShareChat DMs.

## 🟡 Real Example Hindi mein
WhatsApp, Telegram, Swiggy में delivery partner से chat, Zomato support chat, Ola driver chat, ShareChat DM।

---

## 💻 Code Example — Basic
```jsx
import React, { memo } from 'react';                             // memo for list rows
import { View, Text } from 'react-native';                       // UI

// One bubble: mine = right side green, theirs = left side white
function MessageBubble({ text, mine, time }) {
  return (
    <View style={{ flexDirection: 'row', justifyContent: mine ? 'flex-end' : 'flex-start', padding: 4 }}>
      <View style={{ maxWidth: '80%', padding: 8, borderRadius: 10, backgroundColor: mine ? '#DCF8C6' : '#fff' }}>
        <Text>{text}</Text>
        <Text style={{ fontSize: 10, color: '#888', alignSelf: 'flex-end' }}>{time}</Text>
      </View>
    </View>
  );
}
export default memo(MessageBubble);                              // skip re-render if props are same
```

## 💻 Code Example — Advanced
From `ChatScreen.jsx`:
```jsx
const send = useCallback(() => {
  const text = input.trim();                                     // remove spaces
  if (!text) return;                                             // ignore empty
  setMessages((prev) => [{ id: String(Date.now()), text, mine: true, time: now() }, ...prev]); // newest first
  setInput('');                                                  // clear
}, [input]);

const renderItem = useCallback(({ item }) => <MessageBubble {...item} />, []); // stable renderer

<KeyboardAvoidingView
  style={styles.flex}
  behavior={Platform.OS === 'ios' ? 'padding' : undefined}       // iOS only
  keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}        // header height - tune it
>
  <FlatList data={messages} inverted keyExtractor={(m) => m.id} renderItem={renderItem}
            keyboardShouldPersistTaps="handled" />
  <View style={styles.inputBar}>
    <TextInput value={input} onChangeText={setInput} placeholder="Message" multiline />
    <Pressable onPress={send} accessibilityLabel="Send"><Text>Send</Text></Pressable>
  </View>
</KeyboardAvoidingView>
```
Real app additions: message status ticks, date separators, "load older" via `onEndReached` (inverted: end = top), WebSocket / Firestore for live data, optimistic send with `sending/failed` state.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Keyboard | Window resizes (`adjustResize`, Expo default) | Needs `KeyboardAvoidingView behavior="padding"` |
| Offset | Usually 0 | Header height via `keyboardVerticalOffset` |
| Multiline input | Fine | Needs `maxHeight` or it grows too far |
| Safe area | Nav bar inset | Home-indicator inset (use `SafeAreaView`) |
| Time format | `toLocaleTimeString` may differ by device locale | Same, test both |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Works out of the box. Android keyboard mode comes from app.json:
// { "expo": { "android": { "softwareKeyboardLayoutMode": "resize" } } }
```
CLI way:
```jsx
// AndroidManifest.xml -> <activity android:windowSoftInputMode="adjustResize" ...>
// iOS: nothing to configure; KeyboardAvoidingView is enough
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Normal list + `scrollToEnd` hacks.
✅ Correct: `inverted` FlatList with newest-first data.

❌ Mistake 2: No `memo` on bubbles; typing re-renders 500 rows.
✅ Correct: `React.memo` + stable `renderItem`.

❌ Mistake 3: `keyExtractor` using index (ids shift when you prepend).
✅ Correct: Unique ids (server id or timestamp).

❌ Mistake 4: Tapping Send first dismisses the keyboard and does not send.
✅ Correct: `keyboardShouldPersistTaps="handled"`.

---

## 🧠 Tricky Interview Question
You use `inverted` and render messages oldest-first. What happens?

Answer: Newest-at-top. `inverted` flips the list, so index 0 is drawn at the bottom. Data must be newest-first, and "load more history" is `onEndReached` (which is now the visual top).

---

## ⚫ Interview Questions + Answers
Q1: Why `inverted`?
A1: Starts at the bottom, new messages appear without scrolling, keyboard friendly.

Q2: How do you add real-time messages?
A2: WebSocket / Firebase listener appends to state; dedupe by id.

Q3: How do you avoid duplicate sends on a flaky network?
A3: Client-generated id, "sending" status, server idempotency.

Q4: How to group by date?
A4: Insert separator items into the data or use `SectionList` (inverted).

Q5: Performance with thousands of messages?
A5: memo rows, `getItemLayout` if fixed height, `windowSize`, pagination.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Conversation-like feeds (chat, comments, support)

❌ Avoid when:
- Very rich chat needs (reactions, threads, media) - consider `react-native-gifted-chat` or Stream/Sendbird SDK

---

## 📊 Visual Diagram
```
 ┌───────────────────────────┐
 │                  Hello! ✓ │  ← index 1 (mine)
 │ Haan bhai, bolo           │  ← index 0 ... (bottom-most)
 │                           │
 ├───────────────────────────┤
 │ (Message...)     [ Send ] │  ← input bar above keyboard
 └───────────────────────────┘
 data = [newest, ..., oldest]  with  inverted
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| inverted | List drawn bottom-up | उल्टी list |
| Bubble | Message box | संदेश का डिब्बा |
| KeyboardAvoidingView | Moves content above keyboard | Keyboard से बचाने वाला view |
| memo | Skip re-render if props equal | अनावश्यक render रोकना |
| Optimistic update | Show before server confirms | पहले दिखाओ, बाद में confirm |

---

## ⚡ 3-Line Summary
English: Inverted FlatList + newest-first data gives a bottom-anchored chat.
Memoized bubbles and a stable `renderItem` keep typing fast.
KeyboardAvoidingView (iOS) keeps the input visible; Android resizes the window.

Hindi: Inverted FlatList + नया-पहले data से नीचे से शुरू होने वाला chat बनता है।
Memo वाले bubbles और stable `renderItem` से typing तेज़ रहती है।
iOS में KeyboardAvoidingView input दिखाता है; Android में window resize होती है।

---

## ✅ What was verified
react-native-web + jsdom: screen renders seeded messages, typing into the input and pressing Send adds a message and clears the input, an empty send is ignored. Keyboard behaviour (KeyboardAvoidingView) and the inverted layout were not run (no device).

---

## ➡️ Next Topic
287. Build Animated Splash Screen — first impression of the app, uses `Animated` and `expo-splash-screen`.
