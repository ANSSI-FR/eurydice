<template>
  <div
    class="!text-(--p-content-color) flex justify-between p-2 bg-(--p-content-background) border-b border-(--p-content-border-color) shadow-sm shadow-(color:--p-content-hover)"
  >
    <div
      class="flex gap-2 justify-center items-center flex-wrap p-1"
      data-testid="MainNavbarHeader"
    >
      <slot name="logo">
        <Skeleton shape="circle" class="!size-10"></Skeleton>
      </slot>
      <div class="flex flex-col md:flex-row gap-1 md:gap-2 justify-center items-center">
        <slot name="appInfo">
          <Skeleton shape="rectangle" class="!w-20 !h-5"></Skeleton>
        </slot>
      </div>
    </div>
    <div class="flex gap-2 justify-center items-center flex-wrap p-1">
      <slot name="end">
        <Skeleton shape="circle" class="!size-10"></Skeleton>
        <Skeleton shape="rectangle" class="!w-20 !h-5"></Skeleton>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Skeleton } from 'primevue';
</script>
