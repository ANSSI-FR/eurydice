<template>
  <div>
    <div class="top-actions">
      <v-btn small @click="toggleSelectAll">Tout sélectionner</v-btn>
      <SelectedTransferablesDeleteButton
        :selected-transferables="selectedTransferables"
        @reset-selection="selectedTransferables = []"
      />
      <DeleteAllTransferablesButton />
    </div>
    <TransferableTable
      ref="transferableTable"
      :states="states"
      :headers="headers"
    >
      <template #selected="{ transferable: { id, state } }">
        <v-checkbox
          v-model="selectedTransferables"
          :disabled="selectionDisabled(state)"
          name="selection"
          :value="id"
        />
      </template>
      <template #state="{ transferable: { state, progress } }">
        <TransferableStatusChip
          :state="state"
          :state-label="states[state].label"
          :color="states[state].color"
          :icon="states[state].icon"
          :tooltip-text="states[state].tooltipText"
          :progress="progress"
        />
      </template>
      <template #name="{ transferable: { name } }">
        {{ decodeURI(name) }}
      </template>
      <template #size="{ transferable: { size } }">
        {{ formatSize(size) }}
      </template>
      <template #createdAt="{ transferable: { createdAt } }">
        {{ formatDate(createdAt) }}
      </template>
      <template #actions="{ transferable }">
        <TransferableActions
          :transferable="transferable"
          @async-operation-started="disableAutoRefresh"
          @async-operation-ended="enableAutoRefresh"
        />
      </template>
    </TransferableTable>
  </div>
</template>

<script>
import TransferableTable from "@common/components/TransferableTable/main";
import TransferableStatusChip from "@common/components/TransferableTable/TransferableStatusChip";
import SelectedTransferablesDeleteButton from "@destination/components/DestinationTransferableTable/SelectedTransferablesDeleteButton";
import TransferableActions from "@destination/components/DestinationTransferableTable/TransferableActions";
import { TRANSFERABLE_STATES } from "@destination/constants";
import {
  mdiAlertCircle,
  mdiCheck,
  mdiClockRemove,
  mdiCloseNetwork,
  mdiDelete,
  mdiDownloadNetwork,
  mdiTrashCanOutline,
} from "@mdi/js";

import DeleteAllTransferablesButton from "@destination/components/DestinationTransferableTable/DeleteAllTransferablesButton";
import bytes from "bytes";

export default {
  name: "DestinationTransferableTable",

  components: {
    TransferableTable,
    TransferableStatusChip,
    TransferableActions,
    SelectedTransferablesDeleteButton,
    DeleteAllTransferablesButton,
  },
  data() {
    return {
      headers: [
        { text: "Sélection", value: "selected" },
        { text: "Nom", value: "name" },
        { text: "SHA-1", value: "sha1" },
        { text: "Taille", value: "size" },
        { text: "État", value: "state" },
        { text: "Créé le", value: "createdAt" },
        { text: "Actions", value: "actions" },
      ],
      states: {
        [TRANSFERABLE_STATES.SUCCESS]: {
          color: "success lighten-1",
          label: "Succès",
          icon: mdiCheck,
          tooltipText: "Fichier reçu et intègre",
        },
        [TRANSFERABLE_STATES.ONGOING]: {
          color: "info lighten-1",
          label: "En Cours",
          icon: mdiDownloadNetwork,
          tooltipText: "Fichier en cours de réception",
        },
        [TRANSFERABLE_STATES.ERROR]: {
          color: "error lighten-1",
          label: "Erreur",
          icon: mdiAlertCircle,
          tooltipText: "Transfert abandonné à cause d'une erreur",
        },
        [TRANSFERABLE_STATES.REMOVED]: {
          color: "grey lighten-1",
          label: "Supprimé",
          icon: mdiTrashCanOutline,
          tooltipText: "Fichier supprimé à la demande de l'utilisateur",
        },
        [TRANSFERABLE_STATES.REVOKED]: {
          color: "grey lighten-1",
          label: "Révoqué",
          icon: mdiCloseNetwork,
          tooltipText: "Transfert interrompu à la demande du guichet origine",
        },
        [TRANSFERABLE_STATES.EXPIRED]: {
          color: "grey lighten-1",
          label: "Expiré",
          icon: mdiClockRemove,
          tooltipText: "Fichier supprimé après le délai d'expiration",
        },
      },
      selectedTransferables: [],
      deleting: false,
      mdiDelete,
    };
  },
  methods: {
    formatDate(date) {
      return this.$date(date).format("lll");
    },
    formatSize(size) {
      return bytes.format(size);
    },
    disableAutoRefresh() {
      this.$refs.transferableTable.cancelAutoRefresh();
    },
    enableAutoRefresh() {
      this.$refs.transferableTable.setupAutoRefresh();
      this.$refs.transferableTable.getTransferableFrom("current");
    },
    selectionDisabled(transferableState) {
      return transferableState !== TRANSFERABLE_STATES.SUCCESS;
    },
    toggleSelectAll() {
      const allIds = [...this.$refs.transferableTable.transferables.results]
        .filter((input) => input.state === TRANSFERABLE_STATES.SUCCESS)
        .map((input) => input.id);
      if (allIds.length === this.selectedTransferables.length) {
        this.selectedTransferables = [];
      } else {
        this.selectedTransferables = allIds;
      }
    },
  },
};
</script>

<style>
.top-actions {
  margin-bottom: 10px;
}

.top-actions .v-btn {
  margin-right: 10px;
}
</style>
