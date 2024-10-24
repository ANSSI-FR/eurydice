import AppBar from "@common/components/AppBar/main";
import { shallowMount } from "@vue/test-utils";
import store from "@common/store";

describe("AppBar", () => {
  const UserAssociationStub = {
    render(createElement) {
      return createElement("div", "UserAssociationStub");
    },
  };

  it("renders child components", async () => {
    const wrapper = shallowMount(AppBar, {
      store,
      propsData: { extraComponent: UserAssociationStub },
    });
    expect(wrapper.getComponent(UserAssociationStub).isVisible()).toBe(true);
  });
});
