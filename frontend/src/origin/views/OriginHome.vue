<template>
  <div>
    <StatusBanner last-packet-field-name="lastPacketSentAt" />
    <DropZone />
    <OriginTransferableTable />
  </div>
</template>

<script>
import DropZone from "@origin/components/DropZone";
import OriginTransferableTable from "@origin/components/OriginTransferableTable/main";
import StatusBanner from "@common/components/StatusBanner";

export default {
  name: "OriginHome",

  components: {
    DropZone,
    OriginTransferableTable,
    StatusBanner,
  },
};
</script>
