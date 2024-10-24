<template>
  <div class="TransferableCancelButton">
    <template v-if="!actionsDisabled">
      <TransferableDownloadButton :transferable="transferable" />
      <TransferablePreviewButton
        :disabled="!isPreviewable(transferable)"
        :transferable="transferable"
      />
      <TransferableDeleteButton
        :transferable="transferable"
        v-on="$listeners"
      />
    </template>
    <v-icon v-else disabled>{{ mdiMinus }}</v-icon>
  </div>
</template>

<script>
import { mdiMinus } from "@mdi/js";
import { TRANSFERABLE_STATES } from "@destination/constants";
import TransferableDeleteButton from "@destination/components/DestinationTransferableTable/TransferableDeleteButton";
import TransferableDownloadButton from "@destination/components/DestinationTransferableTable/TransferableDownloadButton";
import TransferablePreviewButton from "@destination/components/DestinationTransferableTable/TransferablePreviewButton";

export default {
  name: "TransferableActions",

  components: {
    TransferableDeleteButton,
    TransferableDownloadButton,
    TransferablePreviewButton,
  },
  props: {
    transferable: {
      type: Object,
      required: true,
    },
  },
  data: () => ({ mdiMinus }),
  computed: {
    actionsDisabled() {
      return this.transferable.state !== TRANSFERABLE_STATES.SUCCESS;
    },
  },
  methods: {
    isPreviewable(transferable) {
      const extensions = ["txt", "md", "json", "xml"];
      const parts = transferable.name.split(".");
      const MB = 1000000;
      if (
        parts.length > 1 &&
        extensions.includes(parts.pop().toLowerCase()) &&
        transferable.size < 1 * MB
      ) {
        return true;
      }
      return false;
    },
  },
};
</script>

<style lang="scss" scoped>
@use "sass:map";
/* stylelint-disable */
@import "~vuetify/src/components/VBtn/_variables";
/* stylelint-enable */
.TransferableCancelButton {
  display: flex;
  justify-content: center;
  width: 100%;
}
</style>
