import EurydiceFooter from "@common/components/EurydiceFooter";
import { mount } from "@vue/test-utils";
import store from "@common/store";

describe("Mounted EurydiceFooter", () => {
  const wrapper = mount(EurydiceFooter, { store });

  it("renders correctly", async () => {
    await wrapper.setData({
      links: [
        { label: "foo", url: "bar" },
        {
          label: "i like",
          url: "waffles",
        },
      ],
    });
    expect(wrapper.element).toMatchSnapshot();
  });
});
