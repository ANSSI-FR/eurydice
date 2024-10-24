import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: () => ({
    username: null,
    maintenance: false,
    serverDown: false,
    serverMetadata: null,
    ongoingTransfer: false,
  }),
  getters: {
    maintenance(state) {
      return state.maintenance;
    },
    serverDown(state) {
      return state.serverDown;
    },
    serverMetadata(state) {
      return state.serverMetadata;
    },
    ongoingTransfer(state) {
      return state.ongoingTransfer;
    },
  },
  mutations: {
    setUsername(state, newUsername) {
      state.username = newUsername;
    },
    setMaintenance(state, newMaintenance) {
      state.maintenance = newMaintenance;
    },
    setServerDown(state, serverDown) {
      state.serverDown = serverDown;
    },
    setServerMetadata(state, serverMetadata) {
      state.serverMetadata = serverMetadata;
    },
    setOngoingTransfer(state, ongoingTransfer) {
      state.ongoingTransfer = ongoingTransfer;
    },
  },
  actions: {},
  // NOTE: consider adding modules to this common store in main.js
  //       when adding origin/destination specific state/mutations
  modules: {},
});
