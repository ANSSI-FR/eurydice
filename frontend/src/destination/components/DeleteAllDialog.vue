<template>
  <Dialog
    v-model:visible="isDeleteAllDialogVisible"
    :header="$t('TransferableDeleteAllDialog.title')"
    closable
    modal
    data-testid="TransferableDeleteAllDialog"
    class="w-sm"
  >
    <p>
      {{ $t('TransferableDeleteAllDialog.message') }}
    </p>
    <template #footer>
      <MainButton
        severity="secondary"
        icon="pi pi-times"
        tkey="Actions.cancel"
        @click="
          () => {
            isDeleteAllDialogVisible = false;
          }
        "
        data-testid="TransferableDeleteAllDialog-cancelButton"
      />
      <MainButton
        icon="pi pi-trash"
        severity="danger"
        tkey="Actions.deleteAll"
        @click="deleteAll"
        data-testid="TransferableDeleteAllDialog-deleteAllButton"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import MainButton from '@common/components/MainButton.vue';
import { toastMessage } from '@common/services/toast-message.service';
import { deleteAllTransferables } from '@destination/services/transferables.service';
import { Dialog } from 'primevue';

const isDeleteAllDialogVisible = defineModel<boolean>();

const deleteAll = () => {
  deleteAllTransferables()
    .then(() => {
      toastMessage(
        'TransferableDeleteAllDialog.successMessageTitle',
        'TransferableDeleteAllDialog.successMessageMessage',
        'success',
        true,
      );
    })
    .finally(() => {
      isDeleteAllDialogVisible.value = false;
    });
};
</script>
