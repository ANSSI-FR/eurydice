<template>
  <Tag :value="appVersion" severity="secondary" rounded class="!pt-0 !pb-0 !fit-content" />
</template>

<script setup lang="ts">
import { Tag } from 'primevue';

const appVersion = import.meta.env.EURYDICE_VERSION;
</script>
