import App from "@common/App";
import "@common/plugins/dayjs";
import VueAlerts from "@common/plugins/vuealerts";
import vuetify from "@common/plugins/vuetify";
import store from "@common/store";
import destinationRouter from "@destination/router";
import destinationInterceptorSetup from "@destination/utils/interceptors";
import originRouter from "@origin/router";
import Vue from "vue";

const subdomain = window.location.host.split(".")[0];
const subdomainIsOrigin = subdomain === "origin";

Vue.use(VueAlerts);

new Vue({
  router: subdomainIsOrigin ? originRouter : destinationRouter,
  store,
  mounted() {
    if (!subdomainIsOrigin) {
      destinationInterceptorSetup();
    }
  },
  vuetify,
  render: (h) => h(App),
}).$mount("#app");
