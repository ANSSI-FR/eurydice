<template>
  <transition-group name="alerts-container" class="alerts-container">
    <v-layout
      v-for="alertMessage in alertMessages"
      :key="alertMessage.id"
      class="alerts-container-item"
    >
      <v-flex>
        <v-alert
          :id="alertMessage.id"
          class="mx-10"
          elevation="3"
          dismissible
          :type="alertMessage.type"
          @input="pop(alertMessage)"
        >
          <div>{{ alertMessage.message }}</div>
          <div v-if="alertMessage.count > 1">(x{{ alertMessage.count }})</div>
        </v-alert>
      </v-flex>
    </v-layout>
  </transition-group>
</template>

<script>
const allInstances = [];

export default {
  name: "AlertsContainer",
  data() {
    return {
      alertsCounter: 0,
      alertMessages: [],
    };
  },
  mounted() {
    allInstances.push(this);
  },
  destroyed() {
    allInstances.splice(allInstances.indexOf(this), 1);
  },
  methods: {
    findMessage(message, type) {
      return this.alertMessages.find(
        (element) => element.type === type && element.message === message
      );
    },
    pushNewInstance(message, type, duration) {
      const newInstance = {
        id: `alert-message-alert-${this.alertsCounter}`,
        message,
        type,
        count: 1,
        timeout: null,
      };

      newInstance.timeout = setTimeout(() => {
        this.pop(newInstance);
      }, duration);

      this.alertMessages.splice(0, 0, newInstance);
      this.alertsCounter += 1;
    },
    addCountToExistingInstance(instance, duration) {
      /* eslint-disable no-param-reassign */
      instance.count += 1;

      clearTimeout(instance.timeout);
      instance.timeout = setTimeout(() => {
        this.pop(instance);
      }, duration);
      /* eslint-enable no-param-reassign */
    },

    push(message, type, duration) {
      const existing = this.findMessage(message, type);
      if (existing !== undefined) {
        this.addCountToExistingInstance(existing, duration);
      } else {
        this.pushNewInstance(message, type, duration);
      }
    },
    pop(alertMessage) {
      const index = this.alertMessages.indexOf(alertMessage);
      if (index !== -1) this.alertMessages.splice(index, 1);
    },
  },
  allInstances,
};
</script>
<style scoped>
.alerts-container {
  position: fixed;
  right: 5%;
  top: 80px;
  width: min(90%, 600px);
  z-index: 20;
}

.alerts-container-item {
  transition: all 0.5s ease;
}

.alerts-container-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.alerts-container-enter {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
