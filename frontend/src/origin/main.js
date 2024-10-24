import App from "@common/App.vue";
import "@common/plugins/dayjs";
import VueAlerts from "@common/plugins/vuealerts";
import vuetify from "@common/plugins/vuetify";
import store from "@common/store";
import Vue from "vue";
import router from "./router";

Vue.config.productionTip = false;

Vue.use(VueAlerts);

new Vue({
  router,
  store,
  vuetify,
  render: (h) => h(App),
}).$mount("#app");
