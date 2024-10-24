<template>
  <div>
    <v-banner v-show="maintenance" color="error">
      Le transfert de fichiers est temporairement suspendu pour cause de
      maintenance. Des fichiers peuvent toujours être envoyés au guichet origine
      mais ils ne seront pas immédiatement transmis au guichet destination. Ils
      seront transmis dès la fin de la maintenance.
    </v-banner>
    <v-banner v-show="showServerDownBanner" color="error">
      Le transfert de fichiers n'est pas opérationnel. Vous pouvez contacter vos
      administrateurs {{ appContact }}.
    </v-banner>
  </div>
</template>

<script>
import getAppContact from "@common/api/serverMetadata";
import { mapGetters } from "vuex";
import retrieveStatus from "@common/api/status";
import { refreshIntervalInMs, serverDownIntervalInMs } from "@common/settings";

export default {
  props: {
    lastPacketFieldName: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      timer: null,
      appContact: null,
    };
  },
  computed: {
    ...mapGetters(["serverDown", "maintenance"]),
    showServerDownBanner() {
      return !this.maintenance && this.serverDown;
    },
  },
  async beforeCreate() {
    const { contact } = await getAppContact();
    this.appContact = contact;
  },
  async created() {
    this.getStatus();
    this.setupAutoRefresh();
  },
  methods: {
    setupAutoRefresh() {
      if (!this.timer) {
        this.timer = setInterval(this.getStatus, refreshIntervalInMs);
      }
    },
    async getStatus() {
      const status = await retrieveStatus();
      const { maintenance } = status;
      this.$store.commit("setMaintenance", maintenance);
      const lastPacketTimestamp =
        Date.parse(status[this.lastPacketFieldName]) || 0;
      const timeSinceLastPacketInMs = Date.now() - lastPacketTimestamp;
      const serverDown = timeSinceLastPacketInMs > serverDownIntervalInMs;
      this.$store.commit("setServerDown", serverDown);
    },
  },
};
</script>
