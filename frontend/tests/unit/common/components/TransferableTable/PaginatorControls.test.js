import PaginatorControls from "@common/components/TransferableTable/PaginatorControls";
import { createLocalVue, mount, shallowMount } from "@vue/test-utils";
import Vuetify from "vuetify";

describe("PaginatorControls", () => {
  it("renders correctly", async () => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();
    const wrapper = mount(PaginatorControls, {
      localVue,
      vuetify,
      propsData: {
        numPages: 6,
      },
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it.each`
    requestedPage                         | result
    ${Number.MIN_SAFE_INTEGER.toString()} | ${1}
    ${"-1"}                               | ${1}
    ${"0"}                                | ${1}
    ${"1"}                                | ${1}
    ${"5"}                                | ${5}
    ${"10"}                               | ${10}
    ${"11"}                               | ${1}
    ${"a"}                                | ${1}
    ${""}                                 | ${1}
    ${Number.MAX_SAFE_INTEGER.toString()} | ${1}
  `(
    `goToPage should set the current page to $result when the page requested is $requestedPage`,
    ({ requestedPage, result }) => {
      const wrapper = shallowMount(PaginatorControls, {
        attrs: {
          page: 1,
          numPages: 10,
        },
      });

      const event = {
        target: { value: requestedPage },
      };

      wrapper.vm.goToPage(event);

      expect(wrapper.vm.page).toBe(result);
    }
  );
});
