import AlertsContainer from "@common/components/AlertsContainer";

export default {
  install(Vue) {
    const VueReference = Vue;

    VueReference.prototype.$alert = (
      message,
      type = "info",
      duration = 5000
    ) => {
      AlertsContainer.allInstances.forEach((alertsContainer) => {
        alertsContainer.push(message, type, duration);
      });
    };

    VueReference.component("VAlertsContainer", AlertsContainer);
  },
};
