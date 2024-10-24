import TransferableStatusChip from "@common/components/TransferableTable/TransferableStatusChip";
import { createLocalVue, mount } from "@vue/test-utils";
import Vuetify from "vuetify";
import store from "@/common/store";

describe("TransferableStatusChip", () => {
  const localVue = createLocalVue();
  const vuetify = new Vuetify();

  const tooltipText = "The world is a sphere. There is no East or West.";
  const wrapper = mount(TransferableStatusChip, {
    localVue,
    vuetify,
    store,
    propsData: {
      state: "SUCCESS",
      stateLabel: "Succès",
      icon: "mdi-check",
      color: "success",
      tooltipText,
    },
  });
  it("renders correctly", async () => {
    expect(wrapper.element).toMatchSnapshot();
  });
  it("displays given tooltip text", async () => {
    wrapper.findComponent(TransferableStatusChip).trigger("mouseenter");
    await wrapper.vm.$nextTick();

    requestAnimationFrame(() => {
      expect(wrapper.find("span").text()).toBe(tooltipText);
    });
  });
});
