// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useEffect, useState } from 'react'; // hooks
import { View, Text, FlatList } from 'react-native'; // RN core
import { RestaurantCardSkeleton } from './Skeleton'; // skeleton

export default function RestaurantListScreen() {
  const [data, setData] = useState(null); // null = loading

  useEffect(() => {
    const t = setTimeout(() => setData([{ id: '1', name: 'Paradise' }, { id: '2', name: 'Barbeque Nation' }]), 1500); // fake API
    return () => clearTimeout(t); // cleanup
  }, []);

  if (!data) { // loading -> show 4 skeletons
    return (
      <View>
        {[0, 1, 2, 3].map((i) => <RestaurantCardSkeleton key={i} />)}
      </View>
    );
  }
  return (
    <FlatList
      data={data}
      keyExtractor={(i) => i.id}
      renderItem={({ item }) => <Text style={{ padding: 16, fontSize: 18 }}>{item.name}</Text>}
    />
  );
}
