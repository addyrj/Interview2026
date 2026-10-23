# 28. SectionList Component
# हिंदी में: SectionList — Grouped + Sectioned List
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**SectionList** is a virtualized list component (like FlatList) but designed for **grouped data with section headers** — think contacts sorted A-Z, orders grouped by date, products grouped by category. Each section has a header, and headers can be made sticky (stay visible as you scroll through items in that section). Based on VirtualizedList, so virtualization performance benefits apply.

## 🔵 सरल परिभाषा (Hindi)
**SectionList** virtualized list component है (FlatList की तरह) लेकिन **grouped data with section headers** के लिए — contacts A-Z sorted, orders date-wise grouped, products category-wise। हर section में header होता है, headers sticky बन सकते हैं (section के items scroll होने पर header visible रहे)। VirtualizedList पर based, virtualization performance benefits same।

---

## 🔴 When to Use SectionList vs FlatList
```
USE FLATLIST FOR:
  ✅ Single, flat list of items
  ✅ Restaurant feed, search results, social posts
  ✅ All items same type, same structure

USE SECTIONLIST FOR:
  ✅ Contacts app: A | Aakash, Aman | B | Bharat, Bunty
  ✅ Order history: Today | [orders] | Yesterday | [orders]
  ✅ Settings screen: Account | [items] | Privacy | [items]
  ✅ Product catalog: Starters | [dishes] | Mains | [dishes] | Desserts | [dishes]
  ✅ Any grouped/categorized data with section headers

WITHOUT SECTIONLIST:
  FlatList with manually inserted header items = messy state management
  Hard to make headers sticky
  keyExtractor collision between header items and data items
```

---

## 💻 Code Example — Basic

```tsx
import React from 'react';
import {
  SectionList,
  View,
  Text,
  StyleSheet,
} from 'react-native';

// DATA STRUCTURE for SectionList — MUST have 'title' and 'data' keys
type MenuItem = {
  id: string;
  name: string;
  price: number;
  isVeg: boolean;
};

type MenuSection = {
  title: string;       // section header text
  data: MenuItem[];    // items in this section
};

const menuSections: MenuSection[] = [
  {
    title: 'Starters',
    data: [
      { id: '1', name: 'Paneer Tikka', price: 280, isVeg: true },
      { id: '2', name: 'Chicken Wings', price: 320, isVeg: false },
      { id: '3', name: 'Veg Spring Rolls', price: 220, isVeg: true },
    ],
  },
  {
    title: 'Main Course',
    data: [
      { id: '4', name: 'Butter Chicken', price: 380, isVeg: false },
      { id: '5', name: 'Dal Makhani', price: 280, isVeg: true },
      { id: '6', name: 'Paneer Butter Masala', price: 320, isVeg: true },
    ],
  },
  {
    title: 'Desserts',
    data: [
      { id: '7', name: 'Gulab Jamun', price: 120, isVeg: true },
      { id: '8', name: 'Ice Cream', price: 150, isVeg: true },
    ],
  },
];

export default function RestaurantMenu() {
  return (
    <SectionList
      sections={menuSections}                     // required: array of section objects

      keyExtractor={(item) => item.id}            // required: unique key per ITEM

      renderItem={({ item, section, index }) => ( // render each item
        <View style={styles.item}>
          <View style={styles.vegIndicator(item.isVeg)} />
          <Text style={styles.itemName}>{item.name}</Text>
          <Text style={styles.itemPrice}>₹{item.price}</Text>
        </View>
      )}

      renderSectionHeader={({ section }) => (     // render each section header
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>{section.title}</Text>
          <Text style={styles.sectionCount}>
            {section.data.length} items
          </Text>
        </View>
      )}

      // STICKY HEADERS: section header stays visible as you scroll through items
      stickySectionHeadersEnabled={true}         // default true on iOS, false Android

      ItemSeparatorComponent={() => (
        <View style={styles.separator} />
      )}

      ListHeaderComponent={() => (
        <Text style={styles.menuTitle}>Menu</Text>
      )}

      ListEmptyComponent={() => (
        <Text style={styles.empty}>Menu not available</Text>
      )}
    />
  );
}

const styles = StyleSheet.create({
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: 'white',
  },
  vegIndicator: (isVeg: boolean) => ({
    width: 14,
    height: 14,
    borderRadius: 2,
    borderWidth: 1.5,
    borderColor: isVeg ? '#4CAF50' : '#e23744',
    backgroundColor: isVeg ? '#4CAF50' : '#e23744',
    marginRight: 12,
  }),
  itemName: { flex: 1, fontSize: 15, color: '#1a1a1a' },
  itemPrice: { fontSize: 15, fontWeight: '600', color: '#333' },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#f8f8f8',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#1a1a1a' },
  sectionCount: { fontSize: 13, color: '#888' },
  separator: { height: 1, backgroundColor: '#f5f5f5', marginLeft: 42 },
  menuTitle: { fontSize: 22, fontWeight: '800', padding: 16 },
  empty: { padding: 32, textAlign: 'center', color: '#999' },
});
```

## 💻 Code Example — Advanced (Contacts List with Index)

```tsx
import React, { useState, useCallback, memo } from 'react';
import {
  SectionList,
  View,
  Text,
  TextInput,
  StyleSheet,
  SectionListData,
} from 'react-native';

type Contact = { id: string; name: string; phone: string };
type ContactSection = SectionListData<Contact, { title: string }>;

// Group contacts by first letter of name
function groupContactsByLetter(contacts: Contact[]): ContactSection[] {
  const grouped: Record<string, Contact[]> = {};

  contacts.forEach(contact => {
    const letter = contact.name[0].toUpperCase();
    if (!grouped[letter]) grouped[letter] = [];
    grouped[letter].push(contact);
  });

  return Object.keys(grouped)
    .sort()
    .map(letter => ({
      title: letter,
      data: grouped[letter].sort((a, b) => a.name.localeCompare(b.name)),
    }));
}

const ContactItem = memo(function ContactItem({ item }: { item: Contact }) {
  return (
    <View style={styles.contactItem}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{item.name[0]}</Text>
      </View>
      <View>
        <Text style={styles.contactName}>{item.name}</Text>
        <Text style={styles.contactPhone}>{item.phone}</Text>
      </View>
    </View>
  );
});

const SAMPLE_CONTACTS: Contact[] = [
  { id: '1', name: 'Aakash Sharma', phone: '+91 98765 43210' },
  { id: '2', name: 'Bhavna Patel', phone: '+91 87654 32109' },
  { id: '3', name: 'Arjun Singh', phone: '+91 76543 21098' },
  { id: '4', name: 'Deepika Rao', phone: '+91 65432 10987' },
  { id: '5', name: 'Chetan Kumar', phone: '+91 54321 09876' },
];

export default function ContactsList() {
  const [search, setSearch] = useState('');

  const filteredSections = useCallback(() => {
    const filtered = SAMPLE_CONTACTS.filter(c =>
      c.name.toLowerCase().includes(search.toLowerCase())
    );
    return groupContactsByLetter(filtered);
  }, [search]);

  const renderItem = useCallback(
    ({ item }: { item: Contact }) => <ContactItem item={item} />,
    []
  );

  const renderSectionHeader = useCallback(
    ({ section }: { section: ContactSection }) => (
      <View style={styles.letterHeader}>
        <Text style={styles.letterText}>{section.title}</Text>
      </View>
    ),
    []
  );

  const keyExtractor = useCallback((item: Contact) => item.id, []);

  return (
    <View style={{ flex: 1 }}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search contacts..."
        value={search}
        onChangeText={setSearch}
      />
      <SectionList
        sections={filteredSections()}
        renderItem={renderItem}
        renderSectionHeader={renderSectionHeader}
        keyExtractor={keyExtractor}
        stickySectionHeadersEnabled={true}   // A, B, C headers stick as you scroll
        initialNumToRender={20}
        windowSize={5}
        ListEmptyComponent={() => (
          <Text style={styles.noResults}>No contacts found</Text>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  searchInput: {
    margin: 12,
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 10,
    fontSize: 16,
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: 'white',
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#e23744',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  avatarText: { color: 'white', fontSize: 18, fontWeight: '700' },
  contactName: { fontSize: 15, fontWeight: '600', color: '#1a1a1a' },
  contactPhone: { fontSize: 13, color: '#888', marginTop: 2 },
  letterHeader: {
    backgroundColor: '#f8f8f8',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  letterText: { fontSize: 14, fontWeight: '700', color: '#888' },
  noResults: { padding: 32, textAlign: 'center', color: '#999' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `stickySectionHeadersEnabled` | Default `false` | Default `true` |
| Sticky header behavior | Add `true` explicitly | Works automatically |
| Overscroll | Glow effect | Bounce |

**Note:** Always set `stickySectionHeadersEnabled={true}` explicitly for cross-platform consistency.

---

## 🟠 Expo vs CLI Difference
SectionList is built into React Native — no extra installation. Same for Expo and CLI.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using wrong data structure
```tsx
// WRONG: sections must be an array of { title, data } objects
sections={[
  { header: 'Starters', items: [...] }  // 'header' and 'items' won't work
]}

// CORRECT: 'title' and 'data' are required keys
sections={[
  { title: 'Starters', data: [...] }    // these exact key names
]}
// OR use any keys but provide getItem/getSectionData props
```

❌ **Mistake 2:** Key collision between sections
```tsx
// WRONG: Item in Section 1 has id='1', item in Section 2 also has id='1'
keyExtractor={(item) => item.id}  // collision! React warns

// CORRECT: Make keys globally unique
keyExtractor={(item, index) => `${item.sectionId}-${item.id}`}
// OR ensure IDs are globally unique across all sections
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the data format for SectionList?**
A1: Array of section objects, each with `title` (string) and `data` (array of items): `[{ title: 'Section A', data: [{...}, {...}] }, { title: 'Section B', data: [...] }]`. The `title` is passed to `renderSectionHeader` via `section.title`. TypeScript: use `SectionListData<ItemType>` for proper typing.

**Q2: How do you make section headers sticky?**
A2: Set `stickySectionHeadersEnabled={true}` on SectionList. On iOS this is the default; on Android it defaults to `false`. Sticky headers automatically stay visible at the top as you scroll through items in that section. Useful for contacts (A stays visible while scrolling through A names), restaurant menus (category stays visible while browsing dishes).

**Q3: SectionList vs FlatList — when to use which?**
A3: FlatList: flat, undifferentiated list of items (product feed, search results, timeline). SectionList: items naturally grouped into categories with visible headers (contacts by letter, orders by date, products by category). Don't use FlatList and manually insert header items — SectionList handles sticky headers, section indexing, and the `renderSectionHeader` API properly.

---

## ⚡ 3-Line Summary
**English:**
1. SectionList renders grouped data with section headers — data format: `[{ title: 'A', data: [...] }, { title: 'B', data: [...] }]`.
2. `renderSectionHeader` renders the header for each section; `stickySectionHeadersEnabled={true}` keeps headers visible while scrolling through section items.
3. Use FlatList for flat lists; SectionList for grouped data (contacts, orders by date, menu categories) — don't hack FlatList with manually inserted headers.

**Hindi:**
1. SectionList grouped data को section headers के साथ render करता है — data: `[{ title: 'A', data: [...] }]`।
2. `renderSectionHeader` हर section का header render करता है; `stickySectionHeadersEnabled={true}` headers को visible रखता है।
3. Flat list → FlatList। Grouped data (contacts, orders by date, menu categories) → SectionList।

---

## ➡️ Next Topic
**29. VirtualizedList** — Base class behind FlatList and SectionList।
