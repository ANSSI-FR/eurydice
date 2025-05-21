import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useUserStore = defineStore('userStore', () => {
  const currentUser = ref<User>();

  const getCurrentUser = computed(() => currentUser.value);
  const setCurrentUser = (user: User | undefined) => {
    currentUser.value = user;
  };
  const $reset = () => {
    currentUser.value = undefined;
  };
  return {
    getCurrentUser,
    setCurrentUser,
    $reset,
  };
});
