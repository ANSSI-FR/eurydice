<template>
  <v-tooltip color="black" right>
    <template #activator="{ on }">
      <v-chip text-color="white" :color="color" v-on="on">
        <v-progress-circular
          v-if="state === 'ONGOING'"
          :value="progress"
          :width="7"
          size="17"
          class="mr-2"
        ></v-progress-circular
        ><v-icon v-else class="mr-2" size="17">{{ icon }}</v-icon
        >{{ stateLabel }}
      </v-chip>
    </template>
    <span>{{ tooltipText }}</span>
  </v-tooltip>
</template>
<script>
export default {
  name: "TransferableStatusChip",
  props: {
    state: {
      type: String,
      required: true,
    },
    stateLabel: {
      type: String,
      required: true,
    },
    progress: {
      type: Number,
      required: false,
      default: 100,
    },
    icon: {
      type: String,
      required: true,
    },
    color: {
      type: String,
      required: true,
    },
    tooltipText: {
      type: String,
      required: true,
    },
  },
  mounted() {
    if (this.state === "SUCCESS") {
      this.$store.commit("setOngoingTransfer", false);
    }
  },
};
</script>
<style lang="scss">
.v-progress-circular__underlay {
  display: none;
}
</style>
