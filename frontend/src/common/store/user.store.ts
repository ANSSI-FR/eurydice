import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import apiClient from '@common/api/api-client';

export const useUserStore = defineStore('userStore', () => {
  const currentUser = ref<User>();

  const getCurrentUser = computed(() => currentUser.value);
  const isUserKnown = computed(() => !!currentUser.value);
  const setCurrentUser = (user: User | undefined) => {
    currentUser.value = user;
  };
  const $reset = () => {
    currentUser.value = undefined;
  };
  async function getUserInfo() {
    const user: User = await apiClient.get('/user/me/');
    setCurrentUser(user); // this is not mandatory because a response interceptor (setUserFromResponseInterceptor)
    // is set and will do this assigment. But do it here in case of interceptor update.
  }

  return {
    getCurrentUser,
    setCurrentUser,
    getUserInfo,
    isUserKnown,
    $reset,
  };
});
