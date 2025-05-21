<template>
  <div class="w-full flex flex-col gap-2">
    <Message
      severity="error"
      icon="pi pi-exclamation-triangle"
      closable
      v-if="useServerStatusStore().getIsServerInMaintenance"
      data-testid="StatusBanner.maintenanceMessage"
    >
      {{ $t('StatusBanner.maintenanceMessage') }}
    </Message>
    <Message
      severity="error"
      icon="pi pi-exclamation-triangle"
      closable
      v-if="useServerStatusStore().getIsServerDown"
      data-testid="StatusBanner.serverTimeout"
    >
      {{
        $t('StatusBanner.serverTimeout', {
          contactMethod: useServerMetadataStore().getServerMetadata?.contact,
        })
      }}
    </Message>
  </div>
</template>
<script setup lang="ts">
import { refreshServerStatus } from '@common/services/status.service';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { useServerStatusStore } from '@common/store/server-status.store';
import { Message } from 'primevue';
import { onMounted } from 'vue';

onMounted(async () => {
  refreshServerStatus();
  setInterval(refreshServerStatus, import.meta.env.VITE_APP_REFRESH_INTERVAL_IN_MS ?? 5000);
});
</script>
