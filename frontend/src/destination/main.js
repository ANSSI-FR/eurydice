import App from "@common/App";
import "@common/plugins/dayjs";
import VueAlerts from "@common/plugins/vuealerts";
import vuetify from "@common/plugins/vuetify";
import store from "@common/store";
import intercetorSetup from "@destination/utils/interceptors";
import Vue from "vue";
import router from "./router";

Vue.config.productionTip = false;

Vue.use(VueAlerts);

new Vue({
  router,
  store,
  mounted() {
    intercetorSetup();
  },
  vuetify,
  render: (h) => h(App),
}).$mount("#app");
