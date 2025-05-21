<template>
  <RouterView />
  <Toast position="bottom-center" data-testid="Toast"></Toast>
</template>

<script setup lang="ts">
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { Toast } from 'primevue';
import { onMounted, watch } from 'vue';
import { RouterView } from 'vue-router';

const serverMetadataStore = useServerMetadataStore();
onMounted(async () => {
  if (serverMetadataStore.getServerMetadata === undefined) {
    await serverMetadataStore.fetchServerMetadata();
  }
});

watch(serverMetadataStore, () => {
  if (serverMetadataStore.getServerMetadata) {
    document.title = serverMetadataStore.getServerMetadata.badgeContent;
  }
});
</script>
