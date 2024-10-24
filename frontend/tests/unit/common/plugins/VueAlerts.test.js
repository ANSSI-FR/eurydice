import VueAlerts from "@common/plugins/vuealerts";
import { createLocalVue, mount } from "@vue/test-utils";
import Vuetify from "vuetify";

describe("VueAlerts", () => {
  const localVue = createLocalVue();
  localVue.use(VueAlerts);
  let vuetify;

  beforeEach(() => {
    vuetify = new Vuetify();
  });

  const TestComponent = {
    template: `<div><v-alerts-container></v-alerts-container></div>`,
    methods: {
      openAlert() {
        this.$alert("Bonjour ceci est un AlertMessage 13371337");
      },
    },
  };

  it("renders correctly", async () => {
    const wrapper = mount(TestComponent, {
      localVue,
      vuetify,
      stubs: {
        "transition-group": {
          render(createElement) {
            // eslint-disable-next-line no-underscore-dangle
            return createElement("div", this.$options._renderChildren);
          },
        },
      },
    });
    expect(wrapper.find(".v-alert__content").exists()).toBe(false);
    await wrapper.vm.openAlert();
    expect(wrapper.find(".v-alert__content").text()).toBe(
      "Bonjour ceci est un AlertMessage 13371337"
    );
    wrapper.find(".v-alert__dismissible").trigger("click");
    await wrapper.vm.$nextTick();
    expect(wrapper.find(".v-alert__content").exists()).toBe(false);
  });
});
