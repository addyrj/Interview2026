// CameraScreen.jsx — profile-photo capture using useCamera
import React from 'react'; // React
import { View, Text, Button, Image, StyleSheet } from 'react-native'; // UI
import { CameraView } from 'expo-camera'; // camera preview component
import useCamera from './useCamera'; // our hook

export default function CameraScreen({ onDone }) {
  const cam = useCamera(); // all camera logic

  if (!cam.permission) return <View />; // permission status still loading
  if (!cam.permission.granted) {
    return (
      <View style={styles.center}>
        <Text>We need camera access to take your photo</Text>
        <Button title="Allow camera" onPress={cam.requestPermission} />
      </View>
    );
  }
  if (cam.photo) {
    return (
      <View style={styles.center}>
        <Image source={{ uri: cam.photo.uri }} style={styles.preview} />
        <Button title="Retake" onPress={cam.reset} />
        <Button title="Use photo" onPress={() => onDone?.(cam.photo)} />
      </View>
    );
  }
  return (
    <View style={styles.flex}>
      <CameraView ref={cam.cameraRef} style={styles.flex} facing={cam.facing} flash={cam.flash} />
      <View style={styles.controls}>
        <Button title="Flip" onPress={cam.toggleFacing} />
        <Button title={`Flash: ${cam.flash}`} onPress={cam.toggleFlash} />
        <Button title={cam.busy ? '...' : 'Capture'} onPress={cam.takePhoto} disabled={cam.busy} />
      </View>
      {cam.error && <Text style={styles.error}>{cam.error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  preview: { width: 280, height: 360, borderRadius: 12 },
  controls: { flexDirection: 'row', justifyContent: 'space-around', padding: 16, backgroundColor: '#000' },
  error: { color: 'red', textAlign: 'center' },
});
