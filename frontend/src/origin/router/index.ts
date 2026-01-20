import { commonRoutes } from '@common/router';
import { useUserStore } from '@common/store/user.store';
import MainView from '@origin/views/MainView.vue';
import { createRouter, createWebHistory } from 'vue-router';

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: MainView,
    },
    // Always let commonRoutes at the end
    ...commonRoutes,
  ],
});

router.beforeEach(async (to) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const loginPage = ['/login'];
  const baseToPath = to.path.split('?')[0] ?? '';
  const isLoginPage = loginPage.includes(baseToPath);
  const userStore = useUserStore();

  if (isLoginPage) {
    return;
  }

  // If the user is not known to the store, try to get his info by calling backend.
  // This is in case the session is valid but the store doesn't have the info.
  if (!userStore.isUserKnown) {
    await userStore.getUserInfo(); // if user is not authenticated, this call does not fail
  }

  // user authenticated and already on login page,
  // redirect him to home
  if (userStore.isUserKnown && isLoginPage) {
    return '/';
  }

  // user not authenticated, redirect him to login page
  if (!userStore.isUserKnown && !isLoginPage) {
    return '/login';
  }
});
