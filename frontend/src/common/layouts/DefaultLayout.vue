<template>
  <div class="flex flex-col justify-center min-h-screen bg-(--p-content-background)">
    <header class="sticky top-0 z-1000">
      <slot name="navbar"><Skeleton height="10vh" class="mb-2"></Skeleton></slot>
    </header>
    <main class="flex-1">
      <slot name="main"><Skeleton height="30vh" class="mb-2"></Skeleton></slot>
    </main>
    <footer class="sticky bottom-0 z-1000 pointer-events-none">
      <slot name="footer"><Skeleton height="10vh"></Skeleton></slot>
    </footer>
  </div>
</template>

<script setup lang="ts">
import Skeleton from 'primevue/skeleton';
</script>
