<template>
  <v-footer padless>
    <v-row justify="center" no-gutters>
      <v-btn href="/api/docs/" text class="my-2">
        Documentation de l'API
      </v-btn>
      <v-dialog v-model="dialogVisible" width="500">
        <template #activator="{ on, attrs }">
          <v-btn v-bind="attrs" text class="my-2" v-on="on">Contact</v-btn>
        </template>
        <v-card>
          <v-card-title>Contact</v-card-title>
          <v-card-text class="align-center">
            En cas de problème ou pour nous faire part de vos retours, veuillez
            nous contacter {{ appContact }}.
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" text @click="dialogVisible = false"
              >Fermer</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
  </v-footer>
</template>

<script>
import getServerConfig from "@common/api/serverMetadata";
import { mapGetters } from "vuex";

export default {
  name: "EurydiceFooter",
  data() {
    return {
      dialogVisible: false,
    };
  },
  computed: {
    ...mapGetters(["serverMetadata"]),
    appContact() {
      return this.serverMetadata?.contact;
    },
    badgeContent() {
      return this.serverMetadata?.badgeContent;
    },
  },
  async beforeCreate() {
    // TODO this should be done by a higher-level component
    const serverMetadata = await getServerConfig();
    this.$store.commit("setServerMetadata", serverMetadata);
  },
};
</script>
