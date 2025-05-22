<template>
  <ToggleSwitch
    v-model="isDarkMode"
    @valueChange="onDarkModeChange"
    :pt="{
      slider: 'bg-(--p-content-hover-background)! border-(--p-surface-200)!',
    }"
  >
    <template #handle="{ checked }">
      <i :class="['!text-xs pi', { 'pi-sun': checked, 'pi-moon': !checked }]" />
    </template>
  </ToggleSwitch>
</template>

<script setup lang="ts">
import { useUserPreferencesStore } from '@common/store/user-preferences.store';
import { ToggleSwitch } from 'primevue';
import { ref } from 'vue';

const userPreferencesStore = useUserPreferencesStore();
const isDarkMode = ref<boolean>(!userPreferencesStore.getUserPreferences?.darkMode);

const onDarkModeChange = (value: boolean) => {
  userPreferencesStore.setDarkModePreference(!value);
};
</script>
