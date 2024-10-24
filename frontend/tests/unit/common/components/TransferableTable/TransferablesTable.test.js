import { listTransferables } from "@common/api/transferables";
import TransferablesTable from "@common/components/TransferableTable/main";
import { transferablesPerPage } from "@common/settings";
import { createLocalVue, mount, shallowMount } from "@vue/test-utils";
import Vuetify from "vuetify";
import store from "@/common/store";

jest.mock("@common/api/transferables", () => ({
  listTransferables: jest.fn(),
}));

// hardcode transferablesPerPage
// NOTE: we cannot use a variable here because jest.mock calls are executed before imports
// https://jestjs.io/docs/manual-mocks#using-with-es-module-imports
jest.mock("@common/settings", () => ({
  transferablesPerPage: 10,
}));

describe("TransferablesTable", () => {
  // vuetify instance is not used in shallowMount
  const localVue = createLocalVue();
  let vuetify;

  beforeEach(() => {
    vuetify = new Vuetify();
  });

  const PaginatorControlsStub = {
    template: "<div>PaginatorControlsStub</div>",
    data() {
      return {
        page: 1,
      };
    },
  };

  const dummyProps = {
    headers: [
      { text: "Sith", value: "isJedi" },
      { text: "Jedi", value: "isSith" },
    ],
    states: {
      ALIVE: {
        color: "success lighten-1",
        label: "Vivant",
        icon: "mdi-check",
      },
      DEAD: {
        color: "error lighten-1",
        label: "Mort",
        icon: "mdi-alert-circle",
      },
    },
  };

  // using jest.spyOn to override created lifecycle method because vue-test-utils
  // has no build in tools for that:
  // https://github.com/vuejs/vue-test-utils/issues/166
  jest.spyOn(TransferablesTable, "created").mockImplementation(jest.fn());

  it("renders correctly", async () => {
    const wrapper = mount(TransferablesTable, {
      localVue,
      vuetify,
      stubs: { PaginatorControls: PaginatorControlsStub },
      propsData: dummyProps,
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it.each`
    transferableCount | expectedNumPages
    ${0}              | ${0}
    ${1}              | ${1}
    ${10}             | ${1}
    ${11}             | ${2}
    ${20}             | ${2}
  `(
    `updates page count to $expectedNumPages with $transferableCount transferables`,
    async ({ transferableCount, expectedNumPages }) => {
      const wrapper = shallowMount(TransferablesTable, {
        propsData: dummyProps,
      });
      expect(wrapper.vm.numPages).toBe(0);

      const newTransferables = { count: transferableCount };

      await wrapper.setData({ transferables: newTransferables });

      expect(wrapper.vm.transferables.count).toBe(transferableCount);

      expect(wrapper.vm.numPages).toBe(expectedNumPages);
    }
  );

  it.each([true, false])(
    "getTransferableFrom queries the given URL when initialShowRefresh is %p",
    async (initialShowRefresh) => {
      const wrapper = shallowMount(TransferablesTable, {
        store,
        data() {
          return {
            transferables: {
              pages: { next: "supertoken" },
              showRefresh: initialShowRefresh,
            },
          };
        },
        propsData: dummyProps,
      });

      listTransferables.mockReturnValue({ newItems: true });

      await wrapper.vm.getTransferableFrom("next", false, false);

      expect(listTransferables).toHaveBeenCalledWith(
        {
          page: "supertoken",
          pageSize: transferablesPerPage,
        },
        expect.any(AbortSignal)
      );
      listTransferables.mockClear();

      expect(wrapper.vm.isLoading).toBe(false);
      expect(wrapper.vm.showRefresh).toBe(true);
    }
  );
  it("getTransferablesPage correctly queries the given page", async () => {
    const wrapper = mount(TransferablesTable, {
      localVue,
      vuetify,
      stubs: { PaginatorControls: PaginatorControlsStub },
      propsData: dummyProps,
      data() {
        return {
          transferables: {
            offset: transferablesPerPage * 4,
            pages: { current: "supertoken" },
          },
        };
      },
    });

    const expectedTransferables = { meAnd: "michael" };

    listTransferables.mockReturnValue(expectedTransferables);

    const requestedPage = 2;

    await wrapper.vm.getTransferablesPage(requestedPage);

    expect(listTransferables).toHaveBeenCalledWith({
      delta: -3,
      from: "supertoken",
      pageSize: transferablesPerPage,
    });
    listTransferables.mockClear();

    expect(wrapper.vm.isLoading).toBe(false);
    expect(wrapper.vm.transferables).toEqual(expectedTransferables);
  });
  it("getFreshFirstPage correctly queries the first page", async () => {
    const wrapper = mount(TransferablesTable, {
      localVue,
      vuetify,
      stubs: { PaginatorControls: PaginatorControlsStub },
      propsData: dummyProps,
      data() {
        return {
          showRefresh: true,
        };
      },
    });

    const expectedTransferables = { meAnd: "michael" };

    listTransferables.mockReturnValue(expectedTransferables);

    await wrapper.vm.getFreshFirstPage();

    expect(listTransferables).toHaveBeenCalledWith({
      pageSize: transferablesPerPage,
    });
    listTransferables.mockClear();

    expect(wrapper.vm.showRefresh).toBe(false);
    expect(wrapper.vm.isLoading).toBe(false);
    expect(wrapper.vm.transferables).toEqual(expectedTransferables);
    // If the page change does not come from the PaginatorControls component,
    // the TransferableTable component must change the page number manually
    expect(wrapper.vm.$refs.paginatorControls.page).toEqual(1);
  });
});
