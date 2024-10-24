<template>
  <v-menu offset-y transition="slide-y-transition" left>
    <template #activator="{ on, attrs }">
      <v-btn icon :loading="deleting" v-bind="attrs" v-on="on">
        <v-icon>{{ mdiDelete }}</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-text>Cette action est définitive, êtes-vous sûr ?</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text> Annuler </v-btn>
        <v-btn color="error darken-1" text @click="deleteAction">
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
  name: "TransferableDeleteButton",
  props: {
    transferable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      mdiDelete,
      deleting: false,
    };
  },
  methods: {
    async deleteAction() {
      try {
        this.deleting = true;
        this.$emit("async-operation-started");

        await deleteTransferable(this.transferable.id);
        this.$alert("Le fichier a bien été supprimé", "success");
      } catch (error) {
        // if deleting failed, keep the button enabled so the user can try again
        this.deleting = false;

        if (error?.response.status === 409) {
          this.$alert(error.response.data.detail, "error");
        }
      } finally {
        // keep the button disabled, a refresh is coming to replace this line in the table
        this.$emit("async-operation-ended");
      }
    },
  },
};
</script>
