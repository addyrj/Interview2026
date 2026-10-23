# 276. Interview Problem: Build OTP Verification Screen
# हिंदी में: OTP Verification Screen बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅
# Difficulty: ⭐⭐⭐ Medium-Hard (asked in Swiggy, Paytm, PhonePe interviews)

---

## 🎯 Problem Statement

Build a complete OTP verification screen as used in Indian fintech/food delivery apps:
- 6-digit OTP input with 6 separate boxes
- Auto-focus next box on digit entry
- Auto-focus previous box on backspace
- SMS auto-fill (handle paste of full OTP)
- Timer countdown (30 seconds) with "Resend OTP" button
- Loading state while verifying
- Error state if OTP is wrong
- On success: navigate to next screen

## 🎯 Problem Statement (Hindi)
Complete OTP verification screen बनाओ:
- 6 अलग boxes, auto-focus next/prev
- SMS paste support
- 30-second countdown + Resend button
- Loading + Error states
- Success पर navigate

---

## 💡 Approach (Before coding)
```
STEP 1: State needed
  - otp: string[] (6 items)
  - timeLeft: number (countdown)
  - loading: boolean
  - error: string | null
  - canResend: boolean (when timer = 0)

STEP 2: Refs
  - inputRefs: useRef(Array(6)) — for auto-focus
  - timerRef: useRef — for clearing interval

STEP 3: Handlers
  - handleChange(text, index) → fill digit + focus next
  - handleKeyPress(key, index) → backspace = focus prev
  - handlePaste (when text.length > 1 in onChangeText)
  - startTimer() → countdown from 30
  - handleResend() → reset + start timer
  - handleVerify() → API call, show loading/error

STEP 4: Layout
  KeyboardAvoidingView → OTP boxes row → Timer/Resend → Verify button
```

---

## 💻 Complete Solution

```jsx
import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
  Keyboard,
} from 'react-native';

const OTP_LENGTH = 6;

function OTPVerificationScreen({ navigation, route }) {
  const { phoneNumber } = route.params;  // phone number to display

  // ── State ────────────────────────────────────────────────────────
  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(''));
  const [timeLeft, setTimeLeft] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const canResend = timeLeft === 0;
  const isComplete = otp.every(d => d !== '');

  // ── Refs ─────────────────────────────────────────────────────────
  // Create refs for all 6 input boxes
  const inputRefs = useRef(
    Array.from({ length: OTP_LENGTH }, () => React.createRef())
  );
  const timerRef = useRef(null);

  // ── Timer ─────────────────────────────────────────────────────────
  const startTimer = useCallback(() => {
    setTimeLeft(30);
    if (timerRef.current) clearInterval(timerRef.current);  // clear previous

    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current);  // stop at 0
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  // Start timer on mount
  useEffect(() => {
    startTimer();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);  // cleanup!
    };
  }, [startTimer]);

  // ── OTP Input Handlers ────────────────────────────────────────────
  const handleChange = useCallback((text, index) => {
    // Handle paste: if text length > 1, distribute across all boxes
    if (text.length > 1) {
      const digits = text.replace(/[^0-9]/g, '').split('').slice(0, OTP_LENGTH);
      const newOtp = Array(OTP_LENGTH).fill('');
      digits.forEach((d, i) => { newOtp[i] = d; });
      setOtp(newOtp);
      setError(null);

      // Focus last filled box or last box
      const lastIndex = Math.min(digits.length - 1, OTP_LENGTH - 1);
      inputRefs.current[lastIndex]?.current?.focus();

      // Auto-verify if paste filled all 6
      if (digits.length === OTP_LENGTH) {
        Keyboard.dismiss();
        // Auto-verify after small delay (let state settle)
        setTimeout(() => verifyOTP(digits.join('')), 100);
      }
      return;
    }

    // Single digit entry
    const digit = text.replace(/[^0-9]/g, '');  // digits only
    const newOtp = [...otp];
    newOtp[index] = digit;
    setOtp(newOtp);
    setError(null);  // clear error on new input

    if (digit) {
      if (index < OTP_LENGTH - 1) {
        // Move to next box
        inputRefs.current[index + 1]?.current?.focus();
      } else {
        // Last box filled
        Keyboard.dismiss();
      }
    }
  }, [otp]);

  const handleKeyPress = useCallback(({ nativeEvent: { key } }, index) => {
    if (key === 'Backspace') {
      if (!otp[index] && index > 0) {
        // Current box empty → go back to previous
        const newOtp = [...otp];
        newOtp[index - 1] = '';  // clear previous
        setOtp(newOtp);
        inputRefs.current[index - 1]?.current?.focus();
      }
    }
  }, [otp]);

  // ── Verify OTP ────────────────────────────────────────────────────
  const verifyOTP = useCallback(async (otpString) => {
    setLoading(true);
    setError(null);

    try {
      // Simulate API call (replace with real API)
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simulated: OTP "123456" is correct
      if (otpString === '123456') {
        navigation.replace('Home');  // replace so user can't go back to OTP
      } else {
        setError('Incorrect OTP. Please try again.');
        // Clear OTP on error
        setOtp(Array(OTP_LENGTH).fill(''));
        inputRefs.current[0]?.current?.focus();
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [navigation]);

  const handleVerifyPress = useCallback(() => {
    const otpString = otp.join('');
    if (otpString.length !== OTP_LENGTH) return;
    verifyOTP(otpString);
  }, [otp, verifyOTP]);

  // ── Resend OTP ────────────────────────────────────────────────────
  const handleResend = useCallback(async () => {
    if (!canResend) return;

    setOtp(Array(OTP_LENGTH).fill(''));
    setError(null);
    startTimer();
    inputRefs.current[0]?.current?.focus();

    // API call to resend OTP
    try {
      // await resendOTP(phoneNumber);
      Alert.alert('OTP Sent', `New OTP sent to ${phoneNumber}`);
    } catch (err) {
      setError('Failed to resend OTP');
    }
  }, [canResend, phoneNumber, startTimer]);

  // ── Render ────────────────────────────────────────────────────────
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        {/* Header */}
        <Text style={styles.title}>Verify Your Number</Text>
        <Text style={styles.subtitle}>
          Enter the 6-digit code sent to{'\n'}
          <Text style={styles.phone}>+91 {phoneNumber}</Text>
        </Text>

        {/* OTP Boxes */}
        <View style={styles.otpContainer}>
          {otp.map((digit, index) => (
            <TextInput
              key={index}
              ref={inputRefs.current[index]}
              style={[
                styles.otpBox,
                digit ? styles.otpBoxFilled : null,
                error ? styles.otpBoxError : null,
              ]}
              value={digit}
              onChangeText={(text) => handleChange(text, index)}
              onKeyPress={(e) => handleKeyPress(e, index)}
              keyboardType="number-pad"     // number keyboard
              maxLength={OTP_LENGTH}        // allow paste (will handle in onChangeText)
              selectTextOnFocus             // easy correction
              textAlign="center"            // center digit in box
              editable={!loading}           // disable during verify
              caretHidden                   // hide cursor in box
            />
          ))}
        </View>

        {/* Error message */}
        {error && <Text style={styles.errorText}>{error}</Text>}

        {/* Timer / Resend */}
        <View style={styles.timerRow}>
          {canResend ? (
            <TouchableOpacity onPress={handleResend}>
              <Text style={styles.resendText}>Resend OTP</Text>
            </TouchableOpacity>
          ) : (
            <Text style={styles.timerText}>
              Resend OTP in <Text style={styles.timerCount}>{timeLeft}s</Text>
            </Text>
          )}
        </View>

        {/* Verify Button */}
        <TouchableOpacity
          style={[
            styles.verifyButton,
            (!isComplete || loading) && styles.verifyButtonDisabled,
          ]}
          onPress={handleVerifyPress}
          disabled={!isComplete || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.verifyButtonText}>Verify OTP</Text>
          )}
        </TouchableOpacity>

        {/* Help text */}
        <Text style={styles.helpText}>
          Didn't receive the OTP?{' '}
          <Text style={styles.helpLink} onPress={() => Alert.alert('Support', 'Contact support@app.com')}>
            Get Help
          </Text>
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

// ── Styles ────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    padding: 24,
    paddingTop: 48,
    alignItems: 'center',
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    color: '#111',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 15,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 36,
  },
  phone: {
    fontWeight: '600',
    color: '#333',
  },
  otpContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  otpBox: {
    width: 48,
    height: 56,
    borderWidth: 1.5,
    borderColor: '#ddd',
    borderRadius: 12,
    fontSize: 22,
    fontWeight: '700',
    color: '#111',
    backgroundColor: '#fafafa',
  },
  otpBoxFilled: {
    borderColor: '#f97316',
    backgroundColor: '#fff7ed',
  },
  otpBoxError: {
    borderColor: '#ef4444',
    backgroundColor: '#fef2f2',
  },
  errorText: {
    color: '#ef4444',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 12,
  },
  timerRow: {
    marginVertical: 20,
  },
  timerText: {
    fontSize: 14,
    color: '#888',
  },
  timerCount: {
    color: '#f97316',
    fontWeight: '600',
  },
  resendText: {
    color: '#f97316',
    fontWeight: '600',
    fontSize: 15,
    textDecorationLine: 'underline',
  },
  verifyButton: {
    width: '100%',
    backgroundColor: '#f97316',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  verifyButtonDisabled: {
    backgroundColor: '#fdba74',  // lighter orange when disabled
  },
  verifyButtonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '700',
  },
  helpText: {
    fontSize: 14,
    color: '#888',
  },
  helpLink: {
    color: '#f97316',
    fontWeight: '500',
  },
});

export default OTPVerificationScreen;
```

---

## 🔧 Edge Cases to Handle

```
1. User pastes full OTP from SMS:
   onChangeText receives "123456" (6 chars)
   → text.length > 1 → distribute → auto-verify

2. User enters wrong OTP:
   → Show error
   → Clear all boxes
   → Focus back to first box
   → Don't start new timer (timer continues)

3. Timer reaches 0 but user is typing:
   → canResend becomes true
   → User can still finish typing the old OTP
   → Tapping Resend resets OTP + timer

4. User taps Verify before filling all boxes:
   → Button is disabled (isComplete = false)

5. Loading state:
   → All inputs disabled
   → Button shows ActivityIndicator
   → Prevent double-submit

6. Component unmounts during verify:
   → setLoading(false) would warn "state update on unmounted component"
   → Fix: isMountedRef pattern or AbortController for real API
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| SMS auto-fill | `@react-native-community/sms-retriever` | Automatic SMS suggestions |
| Number keyboard | `number-pad` | `number-pad` |
| Paste from clipboard | Works in onChangeText | Works in onChangeText |
| `caretHidden` | ✅ works | ✅ works |

---

## 🧠 Interview Follow-up Questions

**Q1: How would you implement SMS auto-read on Android?**
```
Use @react-native-community/sms-retriever or expo-sms
→ App registers as SMS listener with specific hash
→ OTP SMS contains app hash → Android auto-reads it
→ Call startSmsRetriever() → onSmsReceived → parse OTP → fill boxes
iOS: OS shows OTP suggestion above keyboard automatically (no code needed!)
```

**Q2: How do you prevent the timer from causing memory leaks?**
```javascript
useEffect(() => {
  startTimer();
  return () => {
    // CLEANUP: Clear interval when component unmounts
    if (timerRef.current) clearInterval(timerRef.current);
  };
}, []);
```

**Q3: How would you handle the case where the user backgrounds the app during the timer?**
```
Use AppState to detect when app returns to foreground
Check remaining time: if OTP expired on server, show "OTP expired" state
Adjust timer based on actual elapsed time (Date.now() comparison)
```

**Q4: How do you auto-verify when SMS OTP is received?**
```javascript
// When SMS is received and OTP extracted:
const otpFromSMS = extractOTPFromSMS(smsBody);  // "Your OTP is 847293"
const digits = otpFromSMS.split('');
setOtp(digits);
// Trigger verification:
setTimeout(() => verifyOTP(otpFromSMS), 100);
```

---

## ✅ What Interviewers Evaluate

```
✅ auto-focus between boxes
✅ backspace handling (go to previous box)
✅ paste handling (SMS auto-fill flow)
✅ proper timer with cleanup (no memory leak)
✅ loading/error/success states
✅ TypeScript (bonus)
✅ Platform differences (Android vs iOS keyboard)
✅ Accessibility (selectTextOnFocus, caretHidden)
✅ UX details (disable button when incomplete, ActivityIndicator)
✅ navigation.replace (not navigate, so back button doesn't show OTP again)
```

---

## ⚡ 3-Line Summary
**English:**
1. 6 TextInputs with refs — auto-focus next on digit entry, auto-focus previous on Backspace; handle paste in `onChangeText` when `text.length > 1`.
2. Timer: `setInterval` in `useEffect` with `clearInterval` cleanup; `canResend` computed from `timeLeft === 0`.
3. States: loading (disable inputs + show spinner), error (show message + clear boxes), success (navigate.replace so back button doesn't work).

**Hindi:**
1. 6 TextInputs + refs: digit enter → next focus, Backspace → prev focus; `onChangeText` में `text.length > 1` = paste handle।
2. Timer: `useEffect` में `setInterval`, cleanup में `clearInterval`; `canResend = timeLeft === 0`।
3. States: loading (inputs disable + spinner), error (message show + boxes clear), success (`navigate.replace`)।

---

## ➡️ Next Problem
**277. Build a Product List with Infinite Scroll + Filter** — Myntra/Amazon style listing screen।
