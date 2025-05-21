<template>
  <MainNavBarLayout>
    <template #logo>
      <RouterLink :to="{ name: 'home' }" class="flex gap-2 items-center flex-wrap">
        <img :src="logo" class="size-10" />
      </RouterLink>
    </template>
    <template #appInfo>
      <span class="text-xl">{{ appTitle }}</span>
      <EnvironmentBadge />
      <VersionBadge />
    </template>
    <template #end>
      <slot name="navbarAction" />
      <i class="pi pi-user"></i>
      <span>{{ userStore.getCurrentUser?.username }}</span>
    </template>
  </MainNavBarLayout>
</template>

<script setup lang="ts">
import logo from '@assets/img/lyre.svg?no-inline';
import EnvironmentBadge from '@common/components/EnvironmentBadge.vue';
import VersionBadge from '@common/components/VersionBadge.vue';
import MainNavBarLayout from '@common/layouts/MainNavBarLayout.vue';
import { useUserStore } from '@common/store/user.store';

const userStore = useUserStore();
const appTitle = import.meta.env.APP_TITLE ?? 'Eurydice';
</script>
