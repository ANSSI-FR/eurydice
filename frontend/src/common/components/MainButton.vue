<script setup lang="ts">
import { Button } from 'primevue';

const {
  icon,
  tkey,
  severity = 'primary',
  tooltipTkey,
} = defineProps<{
  icon?: string;
  tkey?: string;
  severity?: string;
  tooltipTkey?: string;
}>();

const emit = defineEmits(['click']);
</script>

<template>
  <Button
    :label="tkey ? $t(tkey) : undefined"
    :icon="icon"
    :pt="{
      label: 'hidden  sm:flex',
      root: '!rounded-[50%] !h-(--p-button-icon-only-width) sm:!rounded-(--p-button-border-radius)',
    }"
    :outlined="severity !== 'primary'"
    @click="emit('click')"
    :severity="severity"
    v-tooltip.bottom="tooltipTkey ? $t(tooltipTkey) : undefined"
  />
</template>
