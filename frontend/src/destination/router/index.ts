import { commonRoutes } from '@common/router';
import MainView from '@destination/views/MainView.vue';
import UserAssociation from '@destination/views/UserAssociation.vue';
import { createRouter, createWebHistory } from 'vue-router';

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: MainView,
    },
    {
      path: '/user-association',
      name: 'userAssociation',
      component: UserAssociation,
    },

    // Always let commonRoutes at the end
    ...commonRoutes,
  ],
});
