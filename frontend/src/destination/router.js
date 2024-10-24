import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    component: () => import("@common/layouts/AppBarLayout"),
    children: [
      {
        path: "/",
        name: "home",
        component: () => import("@destination/views/DestinationHome"),
      },
      {
        path: "/user-association",
        name: "userAssociation",
        component: () => import("@destination/views/UserAssociation"),
      },
    ],
  },
  {
    path: "/404",
    component: () => import("@common/views/404View"),
  },
  { path: "*", redirect: "/404" },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
