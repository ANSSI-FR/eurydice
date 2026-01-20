<template>
  <RouterView />
  <Toast position="bottom-center" data-testid="Toast"></Toast>
</template>

<script setup lang="ts">
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { Toast } from 'primevue';
import { onMounted, watch } from 'vue';
import { RouterView } from 'vue-router';

import SodiumTools from '@origin/utils/sodiumTools';
import _sodium from 'libsodium-wrappers';

const serverMetadataStore = useServerMetadataStore();

onMounted(async () => {
  if (serverMetadataStore.getServerMetadata === undefined) {
    await serverMetadataStore.fetchServerMetadata();
  }

  // Init SodiumTools
  if (serverMetadataStore.getServerMetadata?.encryptionEnabled) {
    const encodedPublicKey = serverMetadataStore.getServerMetadata?.encodedPublicKey;
    await _sodium.ready;
    new SodiumTools(_sodium, encodedPublicKey);
  }
});

watch(serverMetadataStore, () => {
  if (serverMetadataStore.getServerMetadata) {
    document.title = serverMetadataStore.getServerMetadata.badgeContent;
  }
});
</script>
