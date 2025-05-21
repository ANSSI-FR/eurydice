<template>
  <div class="w-ful flex justify-center pointer-events-none z-1000" v-show="scrollToTopVisible">
    <Button
      icon="pi pi-arrow-up"
      severity="secondary"
      rounded
      class="pointer-events-auto shadow-lg shadow-(color:--p-content-hover)"
      @click="() => scrollToTop()"
      v-tooltip.top="$t('ScrollToTopButton.tooltip')"
      data-testid="ScrollToTopButton"
    >
    </Button>
  </div>
</template>

<script setup lang="ts">
import { Button } from 'primevue';
import { onBeforeUnmount, onMounted, ref } from 'vue';
const scrollToTopVisible = ref<boolean>(false);

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

const scrollToTop = () => {
  window.scroll({
    top: 0,
    behavior: 'smooth',
  });
};

const handleScroll = () => {
  scrollToTopVisible.value = window.scrollY > 50;
};

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>
