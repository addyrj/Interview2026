// LanguageScreen.jsx — demo screen with English / Hindi switch
import React, { useEffect, useState } from 'react'; // React hooks
import { View, Text, Pressable, StyleSheet } from 'react-native'; // UI
import { useTranslation } from 'react-i18next'; // hook giving t() and i18n
import { loadSavedLanguage, setLanguage } from './i18n'; // our helpers (also runs i18n init)

export default function LanguageScreen() {
  const { t, i18n } = useTranslation(); // t = translate function
  const [count, setCount] = useState(1); // cart items

  useEffect(() => { loadSavedLanguage(); }, []); // restore saved language once

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('welcome')}</Text>
      <Text>{t('hello_user', { name: 'Aditya' })}</Text>
      {/* count -> i18next picks _one / _other plural key */}
      <Text testID="count">{t('items_count', { count })}</Text>
      <Pressable onPress={() => setCount((c) => c + 1)} style={styles.btn} testID="add">
        <Text style={styles.btnText}>{t('order_now')} +1</Text>
      </Pressable>

      <Text style={styles.label}>{t('change_language')}</Text>
      <View style={styles.row}>
        {['en', 'hi'].map((lng) => (
          <Pressable
            key={lng}
            testID={`lang-${lng}`}
            onPress={() => setLanguage(lng)} // switch + persist
            style={[styles.chip, i18n.language === lng && styles.active]} // highlight current
          >
            <Text>{lng === 'en' ? 'English' : 'हिंदी'}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, paddingTop: 60 },
  title: { fontSize: 22, fontWeight: '700', marginBottom: 8 },
  btn: { backgroundColor: '#e23744', padding: 12, borderRadius: 8, marginVertical: 12 },
  btnText: { color: '#fff', textAlign: 'center' },
  label: { marginTop: 16, fontWeight: '600' },
  row: { flexDirection: 'row', gap: 10, marginTop: 8 },
  chip: { padding: 10, borderRadius: 16, backgroundColor: '#eee' },
  active: { backgroundColor: '#fcd34d' },
});
