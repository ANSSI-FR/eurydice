import { deleteTransferable } from "@destination/api/transferables";
import TransferableDeleteButton from "@destination/components/DestinationTransferableTable/TransferableDeleteButton";
import { shallowMount } from "@vue/test-utils";
import Vue from "vue";

jest.mock("@destination/api/transferables", () => ({
  deleteTransferable: jest.fn(),
}));

describe("TransferableDeleteButton", () => {
  beforeEach(() => {
    deleteTransferable.mockClear();
  });

  it("should emit async-operation-started and -ended whether api call succeeds or fails", async () => {
    Vue.prototype.$emit = jest.fn();

    const wrapper = shallowMount(TransferableDeleteButton, {
      attrs: {
        transferable: {
          id: 1,
        },
      },
    });

    deleteTransferable.mockRejectedValue({
      response: {
        status: 400,
        data: { detail: "testdetail" },
      },
    });

    await wrapper.vm.deleteAction();

    expect(Vue.prototype.$emit).toHaveBeenCalledWith("async-operation-started");
    expect(Vue.prototype.$emit).toHaveBeenCalledWith("async-operation-ended");

    deleteTransferable.mockResolvedValue();

    await wrapper.vm.deleteAction();

    expect(Vue.prototype.$emit).toHaveBeenCalledWith("async-operation-started");
    expect(Vue.prototype.$emit).toHaveBeenCalledWith("async-operation-ended");
  });

  it(`should alert when the HTTP response code of the deletion api endpoint is 409`, async () => {
    Vue.prototype.$alert = jest.fn();

    deleteTransferable.mockReturnValue(
      new Promise((_, reject) => {
        const error = new Error("HTTP 409");
        error.response = {
          status: 409,
          data: { detail: "testdetail" },
        };
        reject(error);
      })
    );
    const wrapper = shallowMount(TransferableDeleteButton, {
      attrs: {
        transferable: {
          id: 1,
        },
      },
    });

    await wrapper.vm.deleteAction();

    expect(Vue.prototype.$alert).toHaveBeenCalledWith("testdetail", "error");
  });
});
