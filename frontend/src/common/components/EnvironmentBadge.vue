<template>
  <Tag
    :value="serverMetadataStore.getServerMetadata?.badgeContent"
    severity="secondary"
    rounded
    class="!pt-0 !pb-0 !fit-content !text-white"
    :style="{ 'background-color': serverMetadataStore.getServerMetadata?.badgeColor ?? '#01426a' }"
    v-if="serverMetadataStore.getServerMetadata"
  />
</template>

<script setup lang="ts">
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { Tag } from 'primevue';

const serverMetadataStore = useServerMetadataStore();
</script>
