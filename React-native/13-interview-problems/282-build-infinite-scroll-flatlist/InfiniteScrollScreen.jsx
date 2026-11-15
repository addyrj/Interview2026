// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useState, useEffect, useRef, useCallback, memo } from 'react'; // hooks
import { View, Text, FlatList, ActivityIndicator, StyleSheet } from 'react-native'; // RN core

const PAGE_SIZE = 10; // items per page
const TOTAL = 45; // fake total items on server

// Fake paginated API: page is 1-based
const fetchPage = (page) =>
  new Promise((resolve) =>
    setTimeout(() => {
      const start = (page - 1) * PAGE_SIZE; // first index of this page
      const items = Array.from({ length: PAGE_SIZE }, (_, i) => start + i) // ids
        .filter((n) => n < TOTAL) // stop at TOTAL
        .map((n) => ({ id: 'p' + n, name: 'Product ' + (n + 1) })); // build item
      resolve({ items, hasMore: start + PAGE_SIZE < TOTAL }); // response shape
    }, 500));

const Row = memo(function Row({ item }) { // memo: skip re-render if item same
  return (
    <View style={styles.row}>
      <Text>{item.name}</Text>
    </View>
  );
});

export default function InfiniteScrollScreen() {
  const [items, setItems] = useState([]); // accumulated list
  const [page, setPage] = useState(1); // current page
  const [hasMore, setHasMore] = useState(true); // more pages left?
  const [loading, setLoading] = useState(false); // state for spinner footer
  const loadingRef = useRef(false); // sync guard (state is async, ref is instant)

  const loadMore = useCallback(async () => {
    if (loadingRef.current || !hasMore) return; // block duplicate calls
    loadingRef.current = true; // lock
    setLoading(true); // show footer spinner
    try {
      const res = await fetchPage(page); // fetch current page
      setItems((prev) => { // append without duplicates
        const seen = new Set(prev.map((p) => p.id)); // existing ids
        return [...prev, ...res.items.filter((i) => !seen.has(i.id))]; // only new
      });
      setHasMore(res.hasMore); // update flag
      setPage((p) => p + 1); // next page number
    } finally {
      loadingRef.current = false; // unlock
      setLoading(false); // hide spinner
    }
  }, [page, hasMore]);

  useEffect(() => { loadMore(); }, []); // eslint-disable-line - first page once

  const renderItem = useCallback(({ item }) => <Row item={item} />, []); // stable fn

  return (
    <FlatList
      data={items} // list data
      keyExtractor={(i) => i.id} // id key, not index
      renderItem={renderItem} // row renderer
      onEndReached={loadMore} // reached bottom -> next page
      onEndReachedThreshold={0.5} // fire at half a screen from end
      ListFooterComponent={loading ? <ActivityIndicator style={{ margin: 16 }} /> : null} // bottom spinner
    />
  );
}

const styles = StyleSheet.create({
  row: { padding: 20, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ddd' }, // row style
});
