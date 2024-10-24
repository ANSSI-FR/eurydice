<template>
  <v-chip label :color="color">
    <v-icon left> mdi-file </v-icon>
    {{ name }} ({{ progress }}%)
    <v-progress-linear :value="progress" />
  </v-chip>
</template>

<script>
import { mdiFile } from "@mdi/js";

export default {
  name: "DropZoneFile",
  props: {
    name: { type: String, required: true },
    finished: { type: Boolean, default: false, required: false },
    error: { type: Boolean, default: false, required: false },
    progress: { type: Number, default: 0 },
  },
  data: () => ({ mdiFile }),
  computed: {
    color() {
      if (this.finished) return "blue lighten-4";
      if (this.error) return "red lighten-3";
      return null;
    },
  },
};
</script>

<style lang="scss" scoped>
.v-progress-linear {
  position: absolute;
  top: calc(100% - 4px);
}
</style>
