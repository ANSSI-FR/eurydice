import { TRANSFERABLE_STATES } from "@destination/constants";
import TransferableActions from "@destination/components/DestinationTransferableTable/TransferableActions";
import { shallowMount } from "@vue/test-utils";

describe("TransferableActions", () => {
  it.each`
    transferableStatus             | displayed
    ${TRANSFERABLE_STATES.SUCCESS} | ${true}
    ${TRANSFERABLE_STATES.ONGOING} | ${false}
    ${TRANSFERABLE_STATES.ERROR}   | ${false}
    ${TRANSFERABLE_STATES.REMOVED} | ${false}
    ${TRANSFERABLE_STATES.REVOKED} | ${false}
    ${TRANSFERABLE_STATES.EXPIRED} | ${false}
  `(
    `actions visibility should be $displayed when the transferable status is $transferableStatus`,
    ({ transferableStatus, displayed }) => {
      const wrapper = shallowMount(TransferableActions, {
        attrs: {
          transferable: {
            state: transferableStatus,
            name: "test.txt",
          },
        },
      });

      expect(wrapper.vm.actionsDisabled).toBe(!displayed);
    }
  );
});
