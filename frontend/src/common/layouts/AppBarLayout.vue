<template>
  <v-app>
    <AppBar :extra-component="extraComponent" />
    <v-alerts-container />

    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
    <EurydiceFooter />
  </v-app>
</template>

<script>
import AppBar from "@common/components/AppBar/main";
import EurydiceFooter from "@common/components/EurydiceFooter";

export default {
  name: "AppBarLayout",

  components: {
    AppBar,
    EurydiceFooter,
  },
  props: {
    extraComponent: {
      type: Object,
      default: null,
    },
  },
};
</script>
