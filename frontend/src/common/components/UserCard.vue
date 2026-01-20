<script setup lang="ts">
import { useUserStore } from '@common/store/user.store';
import { Button } from 'primevue';
const userStore = useUserStore();
</script>

<template>
  <div class="grid grid-rows-1 grid-flow-col items-center gap-x-2">
    <Button class="row-span-2" :icon="'pi pi-user'" rounded severity="secondary" />
    <span class="cursor-pointer" data-testid="UserCard-username">{{
      userStore.getCurrentUser?.username
    }}</span>
  </div>
</template>
