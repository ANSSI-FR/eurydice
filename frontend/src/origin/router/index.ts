import { createRouter, createWebHistory } from 'vue-router';

import { commonRoutes } from '@common/router';
import MainView from '@origin/views/MainView.vue';

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
