<template>
  <v-btn
    icon
    :href="`/api/v1/transferables/${transferable.id}/download`"
    target="_blank"
  >
    <v-icon>{{ mdiDownload }}</v-icon>
  </v-btn>
</template>

<script>
import { mdiDownload } from "@mdi/js";

export default {
  name: "TransferableDownloadButton",
  props: {
    transferable: {
      type: Object,
      required: true,
    },
  },
  data: () => ({ mdiDownload }),
};
</script>
