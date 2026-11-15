// DarkModeScreen.jsx — demo screen with Light / Dark / System selector
import React from 'react'; // React
import { View, Text, Pressable, Switch, StatusBar, StyleSheet } from 'react-native'; // UI parts
import { ThemeProvider, useTheme } from './ThemeContext'; // our theme code

const OPTIONS = ['system', 'light', 'dark']; // the three choices

function Content() {
  const { mode, isDark, colors, setMode } = useTheme(); // theme values + setter
  return (
    // Background changes with theme
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* StatusBar icons must be light on dark background (and the reverse) */}
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} />
      <Text style={[styles.title, { color: colors.text }]}>Swiggy Settings</Text>

      {/* Simple on/off switch: forces dark or light */}
      <View style={[styles.row, { backgroundColor: colors.card }]}>
        <Text style={{ color: colors.text }}>Dark mode</Text>
        <Switch
          value={isDark} // current state
          onValueChange={(v) => setMode(v ? 'dark' : 'light')} // user choice wins over system
          trackColor={{ true: colors.primary }} // orange when ON
          testID="dark-switch"
        />
      </View>

      {/* Three-way selector */}
      <View style={styles.options}>
        {OPTIONS.map((opt) => (
          <Pressable
            key={opt}
            onPress={() => setMode(opt)} // save choice
            style={[
              styles.chip,
              { backgroundColor: mode === opt ? colors.primary : colors.card }, // highlight selected
            ]}
            testID={`opt-${opt}`}
          >
            <Text style={{ color: mode === opt ? '#fff' : colors.text }}>{opt.toUpperCase()}</Text>
          </Pressable>
        ))}
      </View>
      <Text style={{ color: colors.subtext }}>Current: {mode} ({isDark ? 'dark' : 'light'})</Text>
    </View>
  );
}

// Root: wrap with provider (put this in App.js)
export default function DarkModeScreen() {
  return (
    <ThemeProvider>
      <Content />
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, paddingTop: 60 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 20 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderRadius: 12 },
  options: { flexDirection: 'row', gap: 10, marginVertical: 20 },
  chip: { paddingVertical: 10, paddingHorizontal: 16, borderRadius: 20 },
});
