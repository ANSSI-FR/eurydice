<template>
  <v-menu v-if="isBulkActionEnabled" offset-y transition="slide-y-transition">
    <template #activator="{ on }">
      <v-btn small class="delete-btn error" :loading="deleting" v-on="on">
        Supprimer <v-icon>{{ mdiDelete }}</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-text>Cette action est définitive, êtes-vous sûr ?</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text> Annuler </v-btn>
        <v-btn color="error darken-1" text @click="deleteTransferables">
          Supprimer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script>
import { mdiDelete } from "@mdi/js";
import { deleteTransferable } from "@destination/api/transferables";

export default {
  name: "SelectedTransferablesDeleteButton",
  props: {
    selectedTransferables: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      mdiDelete,
      deleting: false,
      isBulkActionEnabled: false,
    };
  },
  watch: {
    selectedTransferables: {
      handler(newSelection) {
        this.isBulkActionEnabled = newSelection.length > 0;
      },
      deep: true,
    },
  },
  methods: {
    async deleteTransferables() {
      const requests = [];
      this.selectedTransferables.forEach((transferableId) => {
        requests.push(deleteTransferable(transferableId));
      });

      try {
        await Promise.all(requests);
        this.$alert("Les fichiers ont bien été supprimés", "success");
      } catch (error) {
        if (error?.response.status === 409) {
          this.$alert(error.response.data.detail, "error");
        }
      } finally {
        this.$emit("reset-selection");
      }
    },
  },
};
</script>
