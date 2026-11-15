// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install react-native-maps
// Android needs a Google Maps API key in app.json -> android.config.googleMaps.apiKey (Expo Go has a built-in key)
// iOS uses Apple Maps by default (no key). Add provider={PROVIDER_GOOGLE} for Google on iOS (needs dev build).
import React, { useState, useRef } from 'react'; // hooks
import { View, Text, StyleSheet } from 'react-native'; // RN core
import MapView, { Marker, Callout } from 'react-native-maps'; // map components

const RESTAURANTS = [ // sample data
  { id: '1', name: 'Karims', lat: 28.6507, lng: 77.2334 }, // Old Delhi
  { id: '2', name: 'Bukhara', lat: 28.5973, lng: 77.1722 }, // Chanakyapuri
  { id: '3', name: 'Indian Accent', lat: 28.6139, lng: 77.2090 }, // Central Delhi
];

export default function MapScreen() {
  const mapRef = useRef(null); // to animate camera
  const [selected, setSelected] = useState(null); // tapped marker

  const onSelect = (r) => {
    setSelected(r); // remember
    mapRef.current?.animateToRegion( // smooth zoom
      { latitude: r.lat, longitude: r.lng, latitudeDelta: 0.05, longitudeDelta: 0.05 },
      400 // ms
    );
  };

  return (
    <View style={styles.flex}>
      <MapView
        ref={mapRef} // ref for methods
        style={styles.flex} // must have size or map is invisible
        initialRegion={{ latitude: 28.6139, longitude: 77.209, latitudeDelta: 0.2, longitudeDelta: 0.2 }} // start view
        showsUserLocation={false} // needs location permission if true
      >
        {RESTAURANTS.map((r) => (
          <Marker
            key={r.id} // stable key
            coordinate={{ latitude: r.lat, longitude: r.lng }} // position
            title={r.name} // callout title
            onPress={() => onSelect(r)} // tap handler
            pinColor={selected?.id === r.id ? 'blue' : 'red'} // highlight selected
          >
            <Callout><Text>{r.name}</Text></Callout>
          </Marker>
        ))}
      </MapView>
      {selected && <View style={styles.card}><Text style={styles.name}>{selected.name}</Text></View>}
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 }, // fill
  card: { position: 'absolute', bottom: 30, left: 16, right: 16, backgroundColor: '#fff', padding: 16, borderRadius: 12, elevation: 4 }, // bottom card
  name: { fontSize: 18, fontWeight: '700' }, // card title
});
