<template>
  <code class="text-caption">{{ version }}</code>
</template>

<script>
import { version } from "@common/settings";

export default {
  name: "VersionChip",
  data: () => ({
    version,
  }),
};
</script>
