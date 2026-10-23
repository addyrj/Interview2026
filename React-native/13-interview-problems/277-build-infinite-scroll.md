# 277. Interview Problem: Build Infinite Scroll Feed
# हिंदी में: Infinite Scroll Feed बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅
# Difficulty: ⭐⭐⭐ Medium-Hard | Asked at: Zomato, Swiggy, Flipkart, Meesho

---

## 🔴 Problem Statement
Build a product feed with **infinite scroll** (pagination). When the user reaches the end of the list, automatically load the next page of products. Show a loading spinner at the bottom while fetching. Handle: empty state, error state, pull-to-refresh (resets to page 1), and debounce rapid scroll-end triggers.

**Constraints:**
- FlatList (not ScrollView)
- React.memo on item component
- No duplicate items on re-render
- Loading spinner at bottom during pagination
- Pull to refresh resets the list
- Don't make multiple API calls if already loading

---

## 💡 Approach
```
STATE NEEDED:
  products: Product[]     → accumulated list
  page: number            → current page (1-based)
  isLoading: boolean      → initial + page 1 load
  isLoadingMore: boolean  → pagination loading (page 2+)
  hasMore: boolean        → more pages available?
  isRefreshing: boolean   → pull-to-refresh state
  error: string | null    → error message

LOGIC:
  Initial load: useEffect([]) → fetchProducts(page=1) → set products
  Scroll to end: onEndReached → if !isLoadingMore && hasMore → fetch(page+1) → append
  Pull to refresh: onRefresh → reset all state → fetch(page=1)
  API returns: { products, totalPages } → hasMore = page < totalPages

PERFORMANCE:
  React.memo on ProductItem
  useCallback on renderItem, keyExtractor
  keyExtractor: item.id (not index)
```

---

## 💻 Complete Solution

```tsx
import React, { useState, useEffect, useCallback, memo } from 'react';
import {
  View,
  Text,
  FlatList,
  Image,
  Pressable,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  ListRenderItemInfo,
} from 'react-native';

// ─── TYPES ────────────────────────────────────────────────────────────────────
type Product = {
  id: string;
  name: string;
  price: number;
  image: string;
  category: string;
  rating: number;
  reviewCount: number;
};

type ApiResponse = {
  products: Product[];
  page: number;
  totalPages: number;
  totalCount: number;
};

// ─── MOCK API ─────────────────────────────────────────────────────────────────
const PAGE_SIZE = 10;

async function fetchProducts(page: number): Promise<ApiResponse> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));

  const totalCount = 47;  // total products in "database"
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  // Simulate error on page 3 (for testing error handling)
  // if (page === 3) throw new Error('Network error');

  const startIndex = (page - 1) * PAGE_SIZE;
  const endIndex = Math.min(startIndex + PAGE_SIZE, totalCount);

  const products: Product[] = Array.from(
    { length: endIndex - startIndex },
    (_, i) => ({
      id: `prod-${startIndex + i}`,
      name: `Product ${startIndex + i + 1}`,
      price: 299 + (startIndex + i) * 50,
      image: `https://via.placeholder.com/150?text=P${startIndex + i + 1}`,
      category: ['Electronics', 'Clothing', 'Home', 'Books'][
        (startIndex + i) % 4
      ],
      rating: 3 + ((startIndex + i) % 20) * 0.1,
      reviewCount: 50 + (startIndex + i) * 7,
    })
  );

  return { products, page, totalPages, totalCount };
}

// ─── PRODUCT ITEM (memoized) ─────────────────────────────────────────────────
const ProductItem = memo(function ProductItem({
  item,
  onPress,
}: {
  item: Product;
  onPress: (id: string) => void;
}) {
  return (
    <Pressable style={styles.card} onPress={() => onPress(item.id)}>
      <Image
        source={{ uri: item.image }}
        style={styles.productImage}
        resizeMode="cover"
      />
      <View style={styles.productInfo}>
        <Text style={styles.productName} numberOfLines={2}>
          {item.name}
        </Text>
        <Text style={styles.productCategory}>{item.category}</Text>
        <View style={styles.productMeta}>
          <Text style={styles.productRating}>
            ⭐ {item.rating.toFixed(1)} ({item.reviewCount})
          </Text>
          <Text style={styles.productPrice}>₹{item.price}</Text>
        </View>
      </View>
    </Pressable>
  );
});

// ─── MAIN COMPONENT ──────────────────────────────────────────────────────────
export default function InfiniteScrollFeed() {
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ─── FETCH PRODUCTS ─────────────────────────────────────────────────────────
  const loadProducts = useCallback(async (pageNum: number, isRefresh = false) => {
    try {
      if (pageNum === 1) {
        isRefresh ? setIsRefreshing(true) : setIsLoading(true);
      } else {
        setIsLoadingMore(true);
      }
      setError(null);

      const data = await fetchProducts(pageNum);

      setProducts(prev =>
        pageNum === 1
          ? data.products                           // refresh: replace list
          : [...prev, ...data.products]             // paginate: append
      );

      setPage(pageNum);
      setHasMore(pageNum < data.totalPages);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load products');
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
      setIsRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadProducts(1);
  }, [loadProducts]);

  // ─── LOAD MORE (infinite scroll) ────────────────────────────────────────────
  const handleEndReached = useCallback(() => {
    // GUARD: don't fetch if already loading or no more pages
    if (isLoadingMore || isLoading || !hasMore) return;
    loadProducts(page + 1);
  }, [isLoadingMore, isLoading, hasMore, page, loadProducts]);

  // ─── PULL TO REFRESH ────────────────────────────────────────────────────────
  const handleRefresh = useCallback(() => {
    loadProducts(1, true);
  }, [loadProducts]);

  // ─── ITEM PRESS ─────────────────────────────────────────────────────────────
  const handlePress = useCallback((id: string) => {
    console.log('Navigate to product:', id);
    // navigation.navigate('ProductDetail', { productId: id });
  }, []);

  // ─── RENDER ITEM (memoized function) ────────────────────────────────────────
  const renderItem = useCallback(
    ({ item }: ListRenderItemInfo<Product>) => (
      <ProductItem item={item} onPress={handlePress} />
    ),
    [handlePress]
  );

  // ─── KEY EXTRACTOR ──────────────────────────────────────────────────────────
  const keyExtractor = useCallback((item: Product) => item.id, []);

  // ─── FOOTER: loading spinner for pagination ─────────────────────────────────
  const ListFooter = useCallback(() => {
    if (isLoadingMore) {
      return (
        <View style={styles.footerLoader}>
          <ActivityIndicator size="small" color="#e23744" />
          <Text style={styles.footerText}>Loading more...</Text>
        </View>
      );
    }
    if (!hasMore && products.length > 0) {
      return (
        <View style={styles.footerLoader}>
          <Text style={styles.footerText}>
            All {products.length} products loaded
          </Text>
        </View>
      );
    }
    return null;
  }, [isLoadingMore, hasMore, products.length]);

  // ─── EMPTY STATE ────────────────────────────────────────────────────────────
  const ListEmpty = useCallback(() => {
    if (isLoading) return null;  // don't show empty while loading
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>No products found</Text>
      </View>
    );
  }, [isLoading]);

  // ─── ERROR STATE ────────────────────────────────────────────────────────────
  if (error && products.length === 0) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <Pressable style={styles.retryButton} onPress={() => loadProducts(1)}>
          <Text style={styles.retryText}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  // ─── INITIAL LOADING ────────────────────────────────────────────────────────
  if (isLoading && products.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#e23744" />
        <Text style={styles.loadingText}>Loading products...</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={products}
      renderItem={renderItem}
      keyExtractor={keyExtractor}

      // INFINITE SCROLL
      onEndReached={handleEndReached}
      onEndReachedThreshold={0.5}      // trigger at 50% from bottom

      // PULL TO REFRESH
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={handleRefresh}
          colors={['#e23744']}         // Android spinner color
          tintColor="#e23744"          // iOS spinner color
        />
      }

      // FOOTER & EMPTY
      ListFooterComponent={ListFooter}
      ListEmptyComponent={ListEmpty}

      // PERFORMANCE
      removeClippedSubviews={true}
      initialNumToRender={10}
      windowSize={5}
      maxToRenderPerBatch={5}

      // SEPARATOR
      ItemSeparatorComponent={() => <View style={styles.separator} />}
    />
  );
}

// ─── STYLES ──────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 12,
  },
  productImage: {
    width: 90,
    height: 90,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  productInfo: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'space-between',
  },
  productName: { fontSize: 15, fontWeight: '600', color: '#1a1a1a', lineHeight: 20 },
  productCategory: { fontSize: 12, color: '#888', marginTop: 4 },
  productMeta: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 },
  productRating: { fontSize: 13, color: '#666' },
  productPrice: { fontSize: 16, fontWeight: '700', color: '#e23744' },
  separator: { height: 1, backgroundColor: '#f0f0f0' },
  footerLoader: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 20,
    gap: 8,
  },
  footerText: { fontSize: 13, color: '#888' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 },
  loadingText: { color: '#888', fontSize: 15 },
  errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  errorText: { fontSize: 16, color: '#e23744', textAlign: 'center', marginBottom: 16 },
  retryButton: { backgroundColor: '#e23744', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  retryText: { color: 'white', fontWeight: '700' },
  empty: { padding: 48, alignItems: 'center' },
  emptyText: { fontSize: 16, color: '#888' },
});
```

---

## 🧠 Key Interview Points

```
WHAT INTERVIEWERS LOOK FOR:
  1. Guard clause in handleEndReached:
     if (isLoadingMore || isLoading || !hasMore) return;
     → Prevents duplicate API calls during rapid scroll

  2. React.memo on item component
     → Without it: entire list re-renders on every state change
     → With it: only items whose props changed re-render

  3. useCallback on renderItem, keyExtractor, handlers
     → Stable references → memo works correctly

  4. Correct accumulation vs replacement:
     pageNum === 1 → replace (refresh)
     pageNum > 1  → append (pagination)

  5. Loading states separation:
     isLoading    → initial/refresh (shows full-screen spinner)
     isLoadingMore → pagination (shows footer spinner)
     isRefreshing → pull-to-refresh (RefreshControl state)

  6. Error handling:
     During pagination: show error in footer (don't wipe list)
     During initial load: show full-screen error + retry

  7. hasMore flag:
     Don't call API when already on last page
     Derived from: page < totalPages

FOLLOW-UP QUESTIONS:
  Q: How would you add search/filter to this feed?
  A: Add search state → debounce (300ms) → on change:
     reset products=[], page=1, fetch(1, query=searchTerm)

  Q: How would you cache results for offline?
  A: React Query (useInfiniteQuery) caches pages automatically
     OR: MMKV to store page 1 data for offline display

  Q: How would you implement skeleton loading?
  A: Replace isLoading full-screen spinner with
     a FlatList of skeleton placeholder items (gray animated boxes)
     Using Reanimated loop animation (shimmer effect)
```

---

## ⚠️ Common Interview Mistakes

```
❌ Not guarding against duplicate calls:
   User scrolls rapidly → multiple onEndReached → multiple API calls → duplicate items
   Fix: if (isLoadingMore) return;

❌ Resetting to wrong state on refresh:
   Must reset: products=[], page=1, hasMore=true, error=null
   Before fetching page 1 fresh

❌ Setting page BEFORE successful fetch:
   setPage(page + 1)  ← if fetch fails, page is wrong for retry
   Fix: setPage(pageNum) INSIDE the success path after setProducts

❌ Wrong FlatList key = animation glitches:
   keyExtractor={(item, index) => index.toString()} → WRONG
   keyExtractor={(item) => item.id} → CORRECT

❌ Not handling onEndReachedThreshold properly:
   0 = triggers exactly at bottom (too late — user sees no content)
   0.5 = triggers at 50% from bottom (good balance)
   1 = triggers when any part of end is visible (too eager)
```

---

## ⚡ 3-Line Summary
**English:**
1. Key state: `products[]`, `page`, `isLoading`, `isLoadingMore`, `hasMore`, `isRefreshing` — separate initial and pagination loading states for correct UX.
2. Guard in `handleEndReached`: `if (isLoadingMore || isLoading || !hasMore) return` — prevents duplicate API calls during rapid scrolling.
3. Refresh = replace list (`pageNum === 1 ? data : [...prev, ...data]`); pagination = append; `React.memo` + `useCallback` for performance.

**Hindi:**
1. Key state: `products[]`, `page`, `isLoading`, `isLoadingMore`, `hasMore`, `isRefreshing` — initial और pagination loading अलग रखो।
2. `handleEndReached` में guard: `if (isLoadingMore || isLoading || !hasMore) return` — rapid scroll पर duplicate API calls रोको।
3. Refresh = list replace; pagination = append; `React.memo` + `useCallback` performance के लिए।

---

## ➡️ Next Problem
**278. Build a Chat Screen** — Real-time messages, inverted FlatList, keyboard handling।
