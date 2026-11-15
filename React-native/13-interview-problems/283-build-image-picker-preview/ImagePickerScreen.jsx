// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install expo-image-picker
// mediaTypes: ['images'] needs SDK 52+; older SDKs use ImagePicker.MediaTypeOptions.Images
import React, { useState } from 'react'; // state
import { View, Text, Image, Pressable, Alert, Linking, StyleSheet } from 'react-native'; // RN core
import * as ImagePicker from 'expo-image-picker'; // picker module

export default function ImagePickerScreen() {
  const [image, setImage] = useState(null); // picked asset {uri,width,height}

  const pickFromGallery = async () => {
    // Android 13+/iOS photo picker needs no permission, but request is harmless
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync(); // ask permission
    if (!perm.granted) { // user denied
      Alert.alert('Permission needed', 'Allow photo access in Settings', [
        { text: 'Cancel' }, // dismiss
        { text: 'Open Settings', onPress: () => Linking.openSettings() }, // go to settings
      ]);
      return; // stop
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'], // only images
      allowsEditing: true, // crop UI
      aspect: [1, 1], // square crop (Android; iOS ignores)
      quality: 0.7, // compress 0..1
    });
    if (!result.canceled) setImage(result.assets[0]); // assets is an array
  };

  const takePhoto = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync(); // camera permission
    if (!perm.granted) return Alert.alert('Camera permission denied'); // stop if denied
    const result = await ImagePicker.launchCameraAsync({ quality: 0.7 }); // open camera
    if (!result.canceled) setImage(result.assets[0]); // save photo
  };

  return (
    <View style={styles.container}>
      {image ? (
        <Image source={{ uri: image.uri }} style={styles.preview} /> // preview
      ) : (
        <View style={[styles.preview, styles.placeholder]}>
          <Text>No image selected</Text>
        </View>
      )}
      <Pressable style={styles.btn} onPress={pickFromGallery}><Text style={styles.btnText}>Gallery</Text></Pressable>
      <Pressable style={styles.btn} onPress={takePhoto}><Text style={styles.btnText}>Camera</Text></Pressable>
      {image && (
        <Pressable style={[styles.btn, { backgroundColor: '#999' }]} onPress={() => setImage(null)}>
          <Text style={styles.btnText}>Remove</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16 }, // centre
  preview: { width: 250, height: 250, borderRadius: 12, marginBottom: 16 }, // preview box
  placeholder: { backgroundColor: '#eee', alignItems: 'center', justifyContent: 'center' }, // empty box
  btn: { backgroundColor: '#E23744', padding: 12, borderRadius: 8, marginVertical: 4, width: 200 }, // button
  btnText: { color: '#fff', textAlign: 'center', fontWeight: '600' }, // button text
});
