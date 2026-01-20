<template>
  <TransferableTable>
    <template #actionColumn="{ data }">
      <Button
        icon="pi pi-ban"
        rounded
        @click="onCancel(data.id)"
        severity="danger"
        v-if="data.state === 'ONGOING'"
        :disabled="isCancellingTransferable"
      />
    </template>
  </TransferableTable>
</template>

<script setup lang="ts">
import TransferableTable from '@common/components/TransferableTable.vue';
import { cancelTransferable } from '@origin/services/transferables/main';
import { Button } from 'primevue';
import { ref } from 'vue';

const isCancellingTransferable = ref<boolean>(false);

const onCancel = (id: string) => {
  isCancellingTransferable.value = true;
  cancelTransferable(id).finally(() => (isCancellingTransferable.value = false));
};
</script>
