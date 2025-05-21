import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useServerStatusStore = defineStore('serverStatusStore', () => {
  const isServerDown = ref<boolean>(false);
  const isServerInMaintenance = ref<boolean>(false);

  const getIsServerDown = computed(() => isServerDown.value);
  const setIsServerDown = (value: boolean) => {
    isServerDown.value = value;
  };

  const getIsServerInMaintenance = computed(() => isServerInMaintenance.value);
  const setIsServerInMaintenance = (value: boolean) => {
    isServerInMaintenance.value = value;
  };

  const $reset = () => {
    isServerDown.value = false;
    isServerInMaintenance.value = false;
  };
  return {
    getIsServerDown,
    setIsServerDown,
    getIsServerInMaintenance,
    setIsServerInMaintenance,
    $reset,
  };
});
