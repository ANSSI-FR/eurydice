import type { UserPreferences } from '@common/models/UserPreferences';
import { defineStore } from 'pinia';
import { readonly, ref } from 'vue';

export const useUserPreferencesStore = defineStore('userPreferencesStore', () => {
  const LOCAL_STORAGE_KEY: string = 'userPreferences';

  const updateDarkModeInHTML = (darkMode: boolean | undefined) => {
    if (darkMode) {
      document.querySelector('html')!.classList.add('dark');
    } else {
      document.querySelector('html')!.classList.remove('dark');
    }
  };

  const initFromLocalStorage = () => {
    let preferences;
    const localStoragePreferences = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (localStoragePreferences) {
      preferences = JSON.parse(localStoragePreferences);
    } else {
      const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)')?.matches ?? false;
      preferences = { darkMode: systemDarkMode };
    }
    updateDarkModeInHTML(preferences.darkMode);
    return preferences;
  };

  const saveUserPreferencesToLocalStorage = () => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(userPreferences.value));
  };

  const userPreferences = ref<UserPreferences | undefined>(initFromLocalStorage());

  const getUserPreferences = readonly(userPreferences);

  const setDarkModePreference = (darkMode: boolean) => {
    if (!userPreferences.value) {
      userPreferences.value = {};
    }
    if (userPreferences.value.darkMode !== darkMode) {
      userPreferences.value.darkMode = darkMode;
      saveUserPreferencesToLocalStorage();
      updateDarkModeInHTML(darkMode);
    }
  };

  return {
    getUserPreferences,
    setDarkModePreference,
  };
});
