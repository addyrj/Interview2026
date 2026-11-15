// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install expo-camera   (barcode scanning is inside CameraView from SDK 51+)
import React, { useRef, useState } from 'react'; // hooks
import { View, Text, Pressable, Linking, Alert, StyleSheet } from 'react-native'; // RN core
import { CameraView, useCameraPermissions } from 'expo-camera'; // camera

export default function QRScannerScreen() {
  const [permission, requestPermission] = useCameraPermissions(); // permission
  const [scanned, setScanned] = useState(null); // last result
  const lock = useRef(false); // sync lock: onBarcodeScanned fires many times per second

  if (!permission) return <View />; // loading
  if (!permission.granted) { // ask
    return (
      <View style={styles.center}>
        <Text>Camera permission needed to scan QR</Text>
        <Pressable style={styles.btn} onPress={requestPermission}><Text style={styles.btnText}>Allow</Text></Pressable>
      </View>
    );
  }

  const onScan = ({ data, type }) => {
    if (lock.current) return; // ignore duplicates
    lock.current = true; // lock
    setScanned({ data, type }); // store
    if (/^https?:\/\//.test(data)) { // only open web links, never blindly open any scheme
      Alert.alert('Open link?', data, [
        { text: 'Cancel', onPress: reset }, // unlock
        { text: 'Open', onPress: () => { Linking.openURL(data); reset(); } }, // open
      ]);
    }
  };
  const reset = () => { lock.current = false; setScanned(null); }; // scan again

  return (
    <View style={styles.flex}>
      <CameraView
        style={styles.flex}
        facing="back" // rear camera
        barcodeScannerSettings={{ barcodeTypes: ['qr'] }} // only QR
        onBarcodeScanned={scanned ? undefined : onScan} // stop listening after a hit
      />
      <View style={styles.frame} pointerEvents="none" />
      {scanned && (
        <View style={styles.result}>
          <Text selectable>{scanned.data}</Text>
          <Pressable style={styles.btn} onPress={reset}><Text style={styles.btnText}>Scan again</Text></Pressable>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 }, // fill
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // centre
  frame: { position: 'absolute', top: '30%', left: '15%', width: '70%', aspectRatio: 1, borderWidth: 3, borderColor: '#fff', borderRadius: 16 }, // scan box
  result: { position: 'absolute', bottom: 40, left: 16, right: 16, backgroundColor: '#fff', padding: 16, borderRadius: 12 }, // result card
  btn: { backgroundColor: '#E23744', padding: 12, borderRadius: 8, marginTop: 8 }, // button
  btnText: { color: '#fff', textAlign: 'center', fontWeight: '600' }, // text
});
