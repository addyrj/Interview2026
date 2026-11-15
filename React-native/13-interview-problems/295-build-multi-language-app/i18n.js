// i18n.js — set up i18next once; import this file at the top of App.js
import i18n from 'i18next'; // translation engine
import { initReactI18next } from 'react-i18next'; // connects i18next to React hooks
import { getLocales } from 'expo-localization'; // phone language (Expo SDK 51+ API)
import AsyncStorage from '@react-native-async-storage/async-storage'; // remember user choice
import en from './locales/en.json'; // English strings
import hi from './locales/hi.json'; // Hindi strings

const LANG_KEY = 'app-language'; // storage key
export const SUPPORTED = ['en', 'hi']; // languages we ship

// Device language code like 'hi' or 'en' (fallback 'en')
const deviceLang = getLocales()[0]?.languageCode ?? 'en';

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, hi: { translation: hi } }, // all strings bundled in app
  lng: SUPPORTED.includes(deviceLang) ? deviceLang : 'en', // start with device language
  fallbackLng: 'en', // missing key -> English
  interpolation: { escapeValue: false }, // React already escapes
});

// Apply saved language (call once on startup)
export async function loadSavedLanguage() {
  try {
    const saved = await AsyncStorage.getItem(LANG_KEY); // read
    if (saved && SUPPORTED.includes(saved)) await i18n.changeLanguage(saved); // apply
  } catch (e) {} // ignore storage errors
}

// Change language + save it
export async function setLanguage(lang) {
  await i18n.changeLanguage(lang); // UI re-renders automatically
  try { await AsyncStorage.setItem(LANG_KEY, lang); } catch (e) {} // persist
}

export default i18n;
