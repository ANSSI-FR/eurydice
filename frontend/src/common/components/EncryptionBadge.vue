<template>
  <Tag
    value="Chiffrement activé"
    severity="success"
    icon="pi pi-lock"
    rounded
    class="!pt-0 !pb-0 !fit-content"
    v-if="
      serverMetadataStore.getServerMetadata &&
      serverMetadataStore.getServerMetadata?.encryptionEnabled
    "
  />
</template>

<script setup lang="ts">
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { Tag } from 'primevue';

const serverMetadataStore = useServerMetadataStore();
</script>
