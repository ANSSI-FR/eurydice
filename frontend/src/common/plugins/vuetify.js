import EurydiceLogo from "@common/components/EurydiceLogo";
import Vue from "vue";
import Vuetify from "vuetify/lib";

Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconfont: "mdiSvg",
    values: {
      eurydiceLogo: {
        component: EurydiceLogo,
      },
    },
  },
});
