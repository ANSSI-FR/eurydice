import AuthenticatedUser from "@common/components/AppBar/AuthenticatedUser";
import { createLocalVue, mount } from "@vue/test-utils";
import Vuetify from "vuetify";
import Vuex from "vuex";

describe("AuthenticatedUser", () => {
  let localVue;
  let vuetify;
  let store;

  const username = "billmurray";

  beforeEach(() => {
    vuetify = new Vuetify();
    localVue = createLocalVue();
    localVue.use(Vuex);
    store = new Vuex.Store({
      state: () => ({ username }),
    });
  });

  it("displays username from vuex store", async () => {
    // mock child components
    const wrapper = mount(AuthenticatedUser, {
      localVue,
      vuetify,
      store,
    });
    expect(wrapper.find(".text-body-1").text()).toBe(username);
  });
});
