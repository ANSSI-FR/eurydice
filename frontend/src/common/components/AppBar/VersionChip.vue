<template>
  <code class="text-caption">{{ releaseCycle }} {{ version }}</code>
</template>

<script>
import { releaseCycle, version } from "@common/settings";

export default {
  name: "VersionChip",
  data: () => ({
    version,
    releaseCycle,
  }),
};
</script>
