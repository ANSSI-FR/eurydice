<template>
  <v-app-bar outlined app flat>
    <!-- constrain app-bar content inside container -->
    <!-- https://stackoverflow.com/a/66885896 -->
    <v-container class="pa-0 fill-height">
      <v-app-bar-nav-icon class="mx-1" @click="navigateHome"
        ><v-icon large>$vuetify.icons.eurydiceLogo</v-icon></v-app-bar-nav-icon
      >
      <v-app-bar-title class="mx-1">Eurydice</v-app-bar-title>
      <VersionChip class="mx-1 my-auto" />
      <v-badge
        class="mx-1 my-auto"
        :inline="true"
        :content="badgeContent"
        :color="badgeColor"
      />
      <v-spacer />
      <component
        :is="extraComponent"
        v-if="extraComponent !== null"
        class="appbar-menu-element ma-2 mx-4"
      />
      <AuthenticatedUser class="appbar-menu-element ma-2 mx-4" />
      <v-menu class="hamburger-menu">
        <template #activator="{ on }">
          <v-btn icon v-on="on">
            <v-icon>{{ mdiDotsVertical }}</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <AuthenticatedUser class="ma-2 mx-4" />
          </v-list-item>
          <v-list-item>
            <component
              :is="extraComponent"
              v-if="extraComponent !== null"
              class="ma-2 mx-4"
            />
          </v-list-item>
        </v-list>
      </v-menu>
    </v-container>
  </v-app-bar>
</template>

<script>
import AuthenticatedUser from "@common/components/AppBar/AuthenticatedUser";
import { mapGetters } from "vuex";
import { version } from "@common/settings";
import VersionChip from "@common/components/AppBar/VersionChip";
import { mdiDotsVertical } from "@mdi/js";

export default {
  name: "AppBar",
  components: {
    AuthenticatedUser,
    VersionChip,
  },
  props: {
    extraComponent: {
      type: Object,
      default: null,
    },
  },
  data: () => ({
    version,
    mdiDotsVertical,
  }),
  computed: {
    ...mapGetters(["serverMetadata"]),
    badgeContent() {
      return this.serverMetadata?.badgeContent;
    },
    badgeColor() {
      return this.serverMetadata?.badgeColor;
    },
  },
  methods: {
    navigateHome() {
      if (this.$route.path !== "/") {
        this.$router.push("/");
      }
    },
  },
};
</script>

<style scoped>
.hamburger-menu + .v-btn {
  display: none;
}

@media only screen and (max-width: 680px) {
  .appbar-menu-element {
    display: none;
  }

  .hamburger-menu + .v-btn {
    display: block;
    margin-left: auto;
  }
}

@media only screen and (max-width: 600px) {
  .spacer {
    display: none;
  }
}
</style>
