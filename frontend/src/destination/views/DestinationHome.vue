<template>
  <div>
    <StatusBanner last-packet-field-name="lastPacketReceivedAt" />
    <DestinationTransferableTable />
  </div>
</template>

<script>
import DestinationTransferableTable from "@destination/components/DestinationTransferableTable/main";
import StatusBanner from "@common/components/StatusBanner";

export default {
  name: "DestinationHome",

  components: {
    DestinationTransferableTable,
    StatusBanner,
  },
};
</script>
