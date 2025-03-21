<template>
  <v-menu offset-y transition="slide-y-transition">
    <template #activator="{ on }">
      <v-btn
        small
        class="delete-btn error delete-all-btn"
        :loading="deleting"
        v-on="on"
      >
        Supprimer tout<v-icon>{{ mdiDelete }}</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-text
        >Vous allez supprimer tous les fichiers. Cette action est définitive,
        êtes-vous sûr ?</v-card-text
      >
      <v-card-actions>
        <v-spacer />
        <v-btn text> Annuler </v-btn>
        <v-btn color="error darken-1" text @click="deleteTransferables">
          Supprimer tout
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script>
import { deleteAllTransferables } from "@destination/api/transferables";
import { mdiDelete } from "@mdi/js";

export default {
  name: "DeleteAllTransferablesButton",
  data() {
    return {
      mdiDelete,
      deleting: false,
      isBulkActionEnabled: false,
    };
  },
  methods: {
    async deleteTransferables() {
      try {
        const res = await deleteAllTransferables();
        this.$alert(res, "info");
      } catch (error) {
        if (error?.response.status !== 200) {
          this.$alert(error.response.data.detail, "error");
        }
      } finally {
        this.$emit("reset-selection");
      }
    },
  },
};
</script>

<style>
.delete-all-btn {
  float: right;
}
</style>
