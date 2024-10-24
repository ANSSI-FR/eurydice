<template>
  <TransferableTable :states="states" :headers="headers">
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
      <TransferableCancelButton :transferable="transferable" />
    </template>
  </TransferableTable>
</template>

<script>
import {
  mdiAlertCircle,
  mdiCheck,
  mdiClock,
  mdiCloseNetwork,
  mdiUploadNetwork,
} from "@mdi/js";
import TransferableTable from "@common/components/TransferableTable/main";
import TransferableStatusChip from "@common/components/TransferableTable/TransferableStatusChip";
import bytes from "bytes";
import { TRANSFERABLE_STATES } from "@origin/constants";
import TransferableCancelButton from "@origin/components/OriginTransferableTable/TransferableCancelButton";

export default {
  name: "OriginTransferableTable",

  components: {
    TransferableTable,
    TransferableStatusChip,
    TransferableCancelButton,
  },
  data() {
    return {
      headers: [
        { text: "Nom", value: "name" },
        { text: "SHA-1", value: "sha1" },
        { text: "Taille", value: "size" },
        { text: "État", value: "state" },
        { text: "Créé le", value: "createdAt" },
        { text: "Actions", value: "actions" },
      ],
      states: {
        [TRANSFERABLE_STATES.PENDING]: {
          color: "warning lighten-1",
          label: "En Attente",
          icon: mdiClock,
          tooltipText: "En attente de transfert vers le guichet destination",
        },
        [TRANSFERABLE_STATES.SUCCESS]: {
          color: "success lighten-1",
          label: "Succès",
          icon: mdiCheck,
          tooltipText: "Envoyé vers le guichet destination avec succès",
        },
        [TRANSFERABLE_STATES.ONGOING]: {
          color: "info lighten-1",
          label: "En Cours",
          icon: mdiUploadNetwork,
          tooltipText: "En cours de transfert vers le guichet destination",
        },
        [TRANSFERABLE_STATES.ERROR]: {
          color: "error lighten-1",
          label: "Erreur",
          icon: mdiAlertCircle,
          tooltipText: "Erreur lors du transfert",
        },
        [TRANSFERABLE_STATES.CANCELED]: {
          color: "grey lighten-1",
          label: "Annulé",
          icon: mdiCloseNetwork,
          tooltipText: "Transfert annulé à la demande de l'utilisateur",
        },
      },
    };
  },
  methods: {
    formatDate(date) {
      return this.$date(date).format("lll");
    },
    formatSize(size) {
      return bytes.format(size);
    },
  },
};
</script>
