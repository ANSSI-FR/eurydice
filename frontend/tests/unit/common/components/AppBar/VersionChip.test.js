import VersionChip from "@common/components/AppBar/VersionChip";
import { shallowMount } from "@vue/test-utils";

jest.mock("@common/settings", () => ({
  version: "Tony",
  releaseCycle: "Stark",
}));

describe("VersionChip", () => {
  it("displays correct version", async () => {
    const wrapper = shallowMount(VersionChip);
    const version = wrapper.find("code");

    expect(version.isVisible()).toBe(true);
    expect(version.text()).toBe("Stark Tony");
  });
});
