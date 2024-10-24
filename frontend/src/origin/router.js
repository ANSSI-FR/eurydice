import Vue from "vue";
import VueRouter from "vue-router";
import UserAssociation from "@origin/components/UserAssociation";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    component: () => import("@common/layouts/AppBarLayout"),
    children: [
      {
        path: "/",
        name: "home",
        component: () => import("@origin/views/OriginHome"),
      },
    ],
    props: {
      extraComponent: UserAssociation,
    },
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
