import dayjs from "dayjs";
import "dayjs/locale/fr";
import localizedFormat from "dayjs/plugin/localizedFormat";
import relativeTime from "dayjs/plugin/relativeTime";
import Vue from "vue";

dayjs.locale("fr");

dayjs.extend(relativeTime);
dayjs.extend(localizedFormat);

// https://github.com/Juceztp/vue-dayjs#usage-recommended-without-installing-this-library
Object.defineProperties(Vue.prototype, {
  $date: {
    get() {
      return dayjs;
    },
  },
});
