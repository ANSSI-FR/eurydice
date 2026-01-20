import Error404View from '@common/views/Error404View.vue';
import LoginView from '@common/views/LoginView.vue';
import type { RouteRecordRaw } from 'vue-router';

export const commonRoutes: RouteRecordRaw[] = [
  {
    path: '/404',
    name: '404',
    component: Error404View,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: {
      name: '404',
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
];
