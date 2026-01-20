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
      <EncryptionBadge />
    </template>
    <template #end>
      <slot name="navbarAction" />
      <DarkmodeSwitch></DarkmodeSwitch>
      <UserMenu />
    </template>
  </MainNavBarLayout>
</template>

<script setup lang="ts">
import logo from '@assets/img/lyre.svg?no-inline';
import DarkmodeSwitch from '@common/components/DarkmodeSwitch.vue';
import EncryptionBadge from '@common/components/EncryptionBadge.vue';
import EnvironmentBadge from '@common/components/EnvironmentBadge.vue';
import UserMenu from '@common/components/UserMenu.vue';
import VersionBadge from '@common/components/VersionBadge.vue';
import MainNavBarLayout from '@common/layouts/MainNavBarLayout.vue';

const appTitle = import.meta.env.APP_TITLE ?? 'Eurydice';
</script>
