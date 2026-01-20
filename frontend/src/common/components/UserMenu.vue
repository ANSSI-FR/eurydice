<script setup lang="ts">
import APITokenCard from '@common/components/APITokenCard.vue';
import UserCard from '@common/components/UserCard.vue';
import { Dialog, Menu } from 'primevue';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const userMenuItems = computed(() => [
  {
    label: t('UserMenu.apiToken'),
    command: () => (isDialogVisible.value = true),
  },
]);

const userMenu = ref();
const isDialogVisible = ref(false);

const toggleUserMenu = (event: Event) => {
  userMenu.value.toggle(event);
};
</script>
<template>
  <div class="grid grid-flow-col gap-4 items-center">
    <div @click="toggleUserMenu">
      <UserCard />
    </div>
    <Menu ref="userMenu" :model="userMenuItems" :popup="true" class="mt-10"></Menu>
  </div>
  <Dialog v-model:visible="isDialogVisible" modal closable class="w-xl" header="API Token">
    <APITokenCard />
  </Dialog>
</template>
