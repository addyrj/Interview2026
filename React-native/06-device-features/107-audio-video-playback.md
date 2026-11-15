# 107. Audio + Video Playback
# हिंदी में: Audio और Video चलाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 54 (React Native 0.81) — (check current docs — APIs change between SDKs). `expo-av` SDK 54 me deprecated hai; naya `expo-audio` (audio) aur `expo-video` (video) use karo. `expo-audio` SDK 52 me beta, baad me stable.

---

## 🔵 Simple Definition (English)
**Playback** means playing sound or video files (local or from a URL) inside your app. In Expo you use `expo-audio` (`useAudioPlayer`) for music/sounds and `expo-video` (`useVideoPlayer` + `VideoView`) for videos.

## 🔵 सरल परिभाषा (Hindi)
**Playback** का मतलब है app के अंदर sound या video file (local या URL से) चलाना। Expo में music/sound के लिए `expo-audio` (`useAudioPlayer`) और video के लिए `expo-video` (`useVideoPlayer` + `VideoView`) use होते हैं।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ <Video> tag web jaisa nahi hota RN me
❌ Android MediaPlayer/ExoPlayer aur iOS AVPlayer alag-alag APIs
❌ Background audio, silent switch, controls - sab manual
❌ Old expo-av ek hi package me sab - bhaari aur confusing
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ RN में web जैसा <video> tag नहीं होता
❌ Android (ExoPlayer) और iOS (AVPlayer) के अलग APIs
❌ Background audio, silent switch वगैरह manual
✅ अब: expo-audio और expo-video — हल्के, hook based players
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-audio expo-video
Step 2 → Audio: const player = useAudioPlayer(source)
Step 3 → player.play() / pause() / seekTo(seconds) / volume
Step 4 → useAudioPlayerStatus(player) gives currentTime, duration, playing
Step 5 → Video: const player = useVideoPlayer(url, p => { p.loop = true })
Step 6 → <VideoView player={player} nativeControls /> shows the video
Step 7 → Hooks release the player automatically on unmount
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → expo-audio और expo-video install करो
Step 2 → Audio: useAudioPlayer(source) से player बनाओ
Step 3 → player.play() / pause() / seekTo() से control करो
Step 4 → useAudioPlayerStatus से currentTime, duration, playing मिलता है
Step 5 → Video: useVideoPlayer(url) से player बनाओ
Step 6 → <VideoView player={player} /> से video दिखाओ
Step 7 → Unmount पर hook player को खुद release कर देता है
```

---

## 🟡 Real World Example
**Spotify/JioSaavn/Gaana**: music player with play/pause and seek bar. **Instagram Reels / Moj / Josh**: auto-playing vertical videos. **Swiggy** shows a short promo video banner; **Paytm** plays a payment-success sound.

## 🟡 Real Example Hindi mein
**JioSaavn/Gaana** में गाना play/pause और seek bar। **Instagram Reels / Moj / Josh** में अपने-आप चलने वाले vertical videos। **Paytm** में payment success की आवाज़ और **Swiggy** में promo video banner।

---

## 💻 Code Example — Basic
```jsx
// Basic audio player - expo-audio (SDK 52+; verify exact API for your SDK)
import React from 'react';                                         // React
import { View, Button, Text } from 'react-native';                 // UI
import { useAudioPlayer, useAudioPlayerStatus } from 'expo-audio'; // audio hooks

// remote sample mp3 (any HTTPS audio URL works)
const SOURCE = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3';

export default function BasicAudio() {
  const player = useAudioPlayer(SOURCE);          // creates player, auto released on unmount
  const status = useAudioPlayerStatus(player);    // live status: playing, currentTime, duration

  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>
      <Text>{status.playing ? 'Playing...' : 'Paused'}</Text>
      <Text>{Math.floor(status.currentTime)}s / {Math.floor(status.duration)}s</Text>
      {/* play starts from current position */}
      <Button title="Play" onPress={() => player.play()} />
      {/* pause keeps position */}
      <Button title="Pause" onPress={() => player.pause()} />
      {/* seekTo takes seconds */}
      <Button title="Restart" onPress={() => player.seekTo(0)} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Reels-style video with mute, loop, error + focus handling (expo-video)
import React, { useEffect, useState } from 'react';                // hooks
import { View, Pressable, Text, StyleSheet, Platform } from 'react-native'; // UI
import { useVideoPlayer, VideoView } from 'expo-video';            // video player + view
import { useEvent } from 'expo';                                   // subscribe to player events
import { useIsFocused } from '@react-navigation/native';           // pause when screen hidden

export default function ReelVideo({ uri }) {
  const isFocused = useIsFocused();                                // true if this screen visible
  const [muted, setMuted] = useState(true);                        // reels start muted

  // second arg runs once when player is created
  const player = useVideoPlayer(uri, (p) => {
    p.loop = true;                                                 // repeat forever
    p.muted = true;                                                // start muted (autoplay friendly)
    p.play();                                                      // autoplay
  });

  // subscribe to status changes (idle/loading/readyToPlay/error)
  const { status } = useEvent(player, 'statusChange', { status: player.status });

  useEffect(() => {
    if (isFocused) player.play();                                  // resume when screen focused
    else player.pause();                                           // pause when user navigates away
  }, [isFocused, player]);

  useEffect(() => { player.muted = muted; }, [muted, player]);     // sync mute state to player

  return (
    <View style={styles.container}>
      <VideoView
        style={styles.video}
        player={player}                                            // which player to render
        contentFit="cover"                                         // fill like Reels
        nativeControls={false}                                     // custom UI, no default controls
        allowsPictureInPicture={Platform.OS !== 'web'}             // PiP needs config plugin; harmless prop
      />
      {status === 'error' && <Text style={styles.err}>Video load nahi hua</Text>}
      <Pressable style={styles.mute} onPress={() => setMuted((m) => !m)}>
        <Text style={{ color: '#fff' }}>{muted ? 'Unmute' : 'Mute'}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  video: { flex: 1 },
  err: { position: 'absolute', top: 80, alignSelf: 'center', color: '#fff' },
  mute: { position: 'absolute', bottom: 40, right: 20, padding: 10,
    backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: 20 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native engine | ExoPlayer (Media3) | AVPlayer |
| Silent switch | Not applicable | Ring/silent switch can mute audio unless audio mode set (`setAudioModeAsync({ playsInSilentMode: true })`) |
| Background audio | Needs foreground service/notification config | Needs `UIBackgroundModes: audio` (plugin option) |
| Picture-in-Picture | Needs `supportsPictureInPicture` plugin option | Same plugin option |
| Formats | mp4, webm, mkv, HLS, DASH | mp4, mov, HLS (no webm) |
| Lock-screen controls | Via `setActiveForLockScreen` | Via `setActiveForLockScreen` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-audio expo-video
import { useAudioPlayer } from 'expo-audio';          // audio
import { useVideoPlayer, VideoView } from 'expo-video'; // video
```
CLI way:
```jsx
// npm i react-native-video react-native-track-player && cd ios && pod install
import Video from 'react-native-video';               // video component
import TrackPlayer from 'react-native-track-player';  // robust background music player
// <Video source={{ uri }} style={{ flex: 1 }} controls resizeMode="cover" />
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Using deprecated `expo-av` (`Audio.Sound`, `Video`) in new projects.
✅ **Correct:** `expo-audio` + `expo-video` (or `react-native-video` in CLI).

❌ **Mistake 2:** iOS me sound nahi aa raha — silent mode on.
✅ **Correct:** Set audio mode `playsInSilentMode: true` (expo-audio `setAudioModeAsync`).

❌ **Mistake 3:** Videos in a FlatList all playing together.
✅ **Correct:** Play only the visible item (`onViewableItemsChanged`), pause others.

❌ **Mistake 4:** Forgetting to pause on screen blur.
✅ **Correct:** Use `useIsFocused` / AppState to pause.

---

## 🧠 Tricky Interview Question
**Q: In a Reels list of 50 videos, the app crashes with out-of-memory. Why and how to fix?**

**Answer:** Each `useVideoPlayer` holds a native decoder + buffers. Creating 50 players at once exhausts memory. Fix: render player only for the visible item (and maybe next one to preload), use `FlatList` with `windowSize` small, `removeClippedSubviews`, and release players of off-screen items.

---

## ⚫ Interview Questions + Answers

**Q1: Why is expo-av deprecated?**
A1: It was one big package for audio + video with many bugs. Replaced by focused `expo-audio` and `expo-video` (hook based). Check your SDK docs for the removal version.

**Q2: How to stream HLS video?**
A2: Pass an `.m3u8` URL to `useVideoPlayer`; both ExoPlayer and AVPlayer support HLS.

**Q3: How to play audio in background?**
A3: Configure plugin/background modes (iOS `audio` background mode, Android foreground service) and set audio mode to keep playing; for full lock-screen controls use `setActiveForLockScreen`. Not run here — needs a dev build.

**Q4: How to show a seek bar?**
A4: Use `useAudioPlayerStatus` for `currentTime`/`duration`, a Slider, and `player.seekTo(value)`.

**Q5: Do these work in Expo Go?**
A5: Basic playback works in Expo Go; background/PiP config plugins require a development build.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Music/podcast players, short videos, tutorials, notification sounds

❌ **Avoid when:**
- Very advanced DRM/ad-insertion video (use react-native-video with native config)
- Playing a tiny UI click sound often — preload one player and reuse

---

## 📊 Visual Diagram
```
 source (URL / require)
        │
        ▼
 useAudioPlayer / useVideoPlayer ──► native ExoPlayer / AVPlayer
        │                                   │
   play/pause/seek                  decode + output
        │                                   │
        ▼                                   ▼
 status hook (time, playing)        VideoView / speaker
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Player | Object controlling playback | Playback control करने वाला object |
| HLS | Adaptive streaming format (.m3u8) | Adaptive streaming format |
| Seek | Jump to a time | किसी समय पर जाना |
| PiP | Picture in Picture | छोटी floating window |
| Buffering | Loading ahead | आगे का data load करना |
| contentFit | How video fills view | Video कैसे फैले |

---

## ⚡ 3-Line Summary
**English:**
1. Use `expo-audio` for sound and `expo-video` for video; `expo-av` is deprecated.
2. Control with `play/pause/seekTo`, read status via hooks.
3. Pause on blur, limit players in lists, set audio mode for iOS silent switch.

**Hindi:**
1. Sound के लिए `expo-audio`, video के लिए `expo-video`; `expo-av` deprecated है।
2. `play/pause/seekTo` से control और hooks से status पढ़ो।
3. Screen छोड़ने पर pause करो, list में कम players रखो, iOS silent switch के लिए audio mode set करो।

---

## ➡️ Next Topic
**108. Video Recording** — अब video play से आगे camera से video record करना।
