// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install expo-camera   (CameraView API exists from SDK 51; older used <Camera>)
import React, { useRef, useState } from 'react'; // hooks
import { View, Text, Image, Pressable, StyleSheet } from 'react-native'; // RN core
import { CameraView, useCameraPermissions } from 'expo-camera'; // camera + permission hook

export default function CameraScreen() {
  const cameraRef = useRef(null); // handle to camera methods
  const [permission, requestPermission] = useCameraPermissions(); // permission state
  const [facing, setFacing] = useState('back'); // 'back' | 'front'
  const [flash, setFlash] = useState('off'); // 'off' | 'on' | 'auto'
  const [photo, setPhoto] = useState(null); // captured photo

  if (!permission) return <View />; // still loading permission status
  if (!permission.granted) { // not allowed yet
    return (
      <View style={styles.center}>
        <Text>Camera access is needed</Text>
        <Pressable style={styles.btn} onPress={requestPermission}>
          <Text style={styles.btnText}>Allow Camera</Text>
        </Pressable>
      </View>
    );
  }

  const capture = async () => {
    try {
      const pic = await cameraRef.current?.takePictureAsync({ quality: 0.8 }); // take photo
      if (pic) setPhoto(pic); // save {uri,width,height}
    } catch (e) {
      console.warn('Capture failed', e); // log error
    }
  };

  if (photo) { // preview mode
    return (
      <View style={styles.flex}>
        <Image source={{ uri: photo.uri }} style={styles.flex} resizeMode="contain" />
        <Pressable style={styles.btn} onPress={() => setPhoto(null)}>
          <Text style={styles.btnText}>Retake</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.flex}>
      <CameraView ref={cameraRef} style={styles.flex} facing={facing} flash={flash} /> 
      <View style={styles.controls}>
        <Pressable onPress={() => setFacing((f) => (f === 'back' ? 'front' : 'back'))}>
          <Text style={styles.ctrl}>Flip</Text>
        </Pressable>
        <Pressable onPress={capture} style={styles.shutter} />
        <Pressable onPress={() => setFlash((f) => (f === 'off' ? 'on' : 'off'))}>
          <Text style={styles.ctrl}>Flash {flash}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 }, // fill
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // centre
  controls: { position: 'absolute', bottom: 40, width: '100%', flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' }, // overlay
  ctrl: { color: '#fff', fontSize: 16 }, // control text
  shutter: { width: 70, height: 70, borderRadius: 35, backgroundColor: '#fff', borderWidth: 4, borderColor: '#ccc' }, // shutter
  btn: { backgroundColor: '#E23744', padding: 12, borderRadius: 8, margin: 16 }, // button
  btnText: { color: '#fff', fontWeight: '600', textAlign: 'center' }, // button text
});
