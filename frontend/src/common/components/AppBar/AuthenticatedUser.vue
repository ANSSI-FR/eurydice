<template>
  <div>
    <v-layout row justify-center align-center>
      <div class="text-body-1">{{ authenticatedUser }}</div>
      <v-icon right large>{{ mdiAccountCircle }}</v-icon>
    </v-layout>
  </div>
</template>

<script>
import { mdiAccountCircle } from "@mdi/js";

export default {
  name: "AuthenticatedUser",
  data: () => ({
    mdiAccountCircle,
  }),
  computed: {
    authenticatedUser() {
      return this.$store.state.username;
    },
  },
};
</script>
