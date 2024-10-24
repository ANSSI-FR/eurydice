import { listTransferables } from "@common/api/transferables";
import "@common/plugins/dayjs";
import { cancelTransferable } from "@origin/api/transferables";
import OriginTransferableTable from "@origin/components/OriginTransferableTable/main";
import TransferableCancelButton from "@origin/components/OriginTransferableTable/TransferableCancelButton";
import { createLocalVue, mount } from "@vue/test-utils";
import Vue from "vue";
import Vuetify from "vuetify";

jest.mock("@origin/api/transferables", () => ({
  cancelTransferable: jest.fn(),
}));

jest.mock("@common/api/transferables", () => ({
  listTransferables: jest.fn(),
}));

describe("Origin TransferableTable", () => {
  let localVue;
  let vuetify;

  const makeResultsWithState = (state, transferableId) => {
    return {
      offset: 0,
      count: 1,
      newItems: false,
      pages: {
        previous: null,
        current: "tiktoken",
        next: null,
      },
      paginatedAt: "2022-02-01T12:24:53.371410Z",
      results: [
        {
          id: transferableId,
          createdAt: "2022-02-01T10:52:16.174122Z",
          name: "testFile.bin",
          sha1: null,
          size: 10485760,
          userProvidedMeta: { "Metadata-Name": "testFile.bin" },
          submissionSucceeded: false,
          submissionSucceededAt: null,
          state,
          progress: 0,
          bytesTransferred: 0,
          transferFinishedAt: null,
          transferSpeed: 0,
          transferEstimatedFinishDate: null,
        },
      ],
    };
  };

  const makeTransferableWithState = (state, transferableId, progress = 0) => {
    return {
      id: transferableId,
      createdAt: "2022-02-01T10:52:16.174122Z",
      name: "testFile.bin",
      sha1: null,
      size: 10485760,
      userProvidedMeta: { "Metadata-Name": "testFile.bin" },
      submissionSucceeded: false,
      submissionSucceededAt: null,
      state,
      progress,
      bytesTransferred: 0,
      transferFinishedAt: null,
      transferSpeed: 0,
      transferEstimatedFinishDate: null,
    };
  };

  const makeResultsFromTransferables = (transferables) => {
    return {
      offset: 0,
      count: transferables.length,
      newItems: false,
      pages: {
        previous: null,
        current: "tiktoken",
        next: null,
      },
      paginatedAt: "2022-02-01T12:24:53.371410Z",
      results: transferables,
    };
  };

  beforeEach(() => {
    listTransferables.mockClear();
    cancelTransferable.mockClear();
    localVue = createLocalVue();
    vuetify = new Vuetify();
  });

  it.each`
    state         | buttonVisible
    ${"PENDING"}  | ${true}
    ${"SUCCESS"}  | ${false}
    ${"ONGOING"}  | ${true}
    ${"ERROR"}    | ${false}
    ${"CANCELED"} | ${false}
  `(
    "displays a working CANCEL button if appropriate",
    async ({ state, buttonVisible }) => {
      const transferableId = "b45f8674-8037-4867-a74e-935621f71254";
      listTransferables.mockReturnValue(
        new Promise((resolve) => {
          resolve(makeResultsWithState(state, transferableId));
        })
      );
      const wrapper = mount(OriginTransferableTable, {
        localVue,
        vuetify,
      });
      await wrapper.vm.$nextTick();
      const cancelNativeButton = wrapper
        .findComponent(TransferableCancelButton)
        .find("button");
      expect(cancelNativeButton.exists()).toBe(buttonVisible);
      if (buttonVisible) {
        cancelNativeButton.trigger("click");
        expect(cancelTransferable).toHaveBeenCalledWith(transferableId);
      } else {
        expect(cancelTransferable).not.toHaveBeenCalled();
      }
    }
  );
  it("displays an alert if the API responds with 400", async () => {
    Vue.prototype.$alert = jest.fn();

    listTransferables.mockReturnValue(
      new Promise((resolve) => {
        resolve(makeResultsWithState("ONGOING"));
      })
    );
    cancelTransferable.mockReturnValue(
      new Promise((resolve, reject) => {
        const error = new Error("HTTP 400");
        error.response = { status: 400, data: { detail: "testdetail" } };
        reject(error);
      })
    );
    const wrapper = mount(OriginTransferableTable, {
      localVue,
      vuetify,
    });

    await wrapper.vm.$nextTick();

    const cancelNativeButton = wrapper
      .findComponent(TransferableCancelButton)
      .find("button");
    cancelNativeButton.trigger("click");

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(Vue.prototype.$alert).toHaveBeenCalledWith("testdetail", "error");
  });
  it("renders correctly", async () => {
    listTransferables.mockReturnValue(
      new Promise((resolve) => {
        resolve(
          makeResultsFromTransferables([
            makeTransferableWithState(
              "PENDING",
              "f9f55ac9-fe6d-4305-8ad2-32bb2ae33319"
            ),
            makeTransferableWithState(
              "ONGOING",
              "5f160791-b9dc-44f3-ae4f-06cb92beb6d2",
              0
            ),
            makeTransferableWithState(
              "ONGOING",
              "e4d63e3e-f755-416a-9b96-3beb152d54f3",
              33
            ),
            makeTransferableWithState(
              "ONGOING",
              "e4726d7a-b58d-479e-88bf-34819c5d3880",
              100
            ),
            makeTransferableWithState(
              "SUCCESS",
              "27d7e3b2-0fe0-4201-b8c2-9a286d6a460e"
            ),
            makeTransferableWithState(
              "ERROR",
              "30900b8f-8979-4cde-9fb6-7f3eae4c1167"
            ),
            makeTransferableWithState(
              "CANCELED",
              "62feae26-14d6-453a-8710-2d3328874235"
            ),
          ])
        );
      })
    );

    const wrapper = mount(OriginTransferableTable, {
      localVue,
      vuetify,
    });

    await wrapper.vm.$nextTick();

    expect(wrapper.element).toMatchSnapshot();
  });
});
