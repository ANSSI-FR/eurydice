import { listTransferables } from "@common/api/transferables";
import "@common/plugins/dayjs";
import DestinationTransferableTable from "@destination/components/DestinationTransferableTable/main";
import { createLocalVue, mount } from "@vue/test-utils";
import Vuetify from "vuetify";

jest.mock("@common/api/transferables", () => ({
  listTransferables: jest.fn(),
}));

describe("Destination TransferableTable", () => {
  let localVue;
  let vuetify;

  beforeEach(() => {
    listTransferables.mockClear();
    localVue = createLocalVue();
    vuetify = new Vuetify();
  });

  it("updates files to ONGOING and SUCCESS states", async () => {
    const filename = "x=шеллы.lolz";
    const encoded = encodeURI(filename);

    listTransferables.mockReturnValue(
      new Promise((resolve) => {
        resolve({
          offset: 0,
          count: 1,
          new_items: false,
          pages: {
            previous: null,
            current: "tiktoken",
            next: null,
          },
          paginated_at: "2022-01-31T15:08:48.385392Z",
          results: [
            {
              id: "9da121e7-df9a-4649-b2c8-ce7153938df2",
              created_at: "2022-01-31T13:41:04.345837Z",
              name: encoded,
              sha1: "610cab90c8e691518047d006a91e6a051b402ae4",
              size: 1024,
              user_provided_meta: { "Metadata-Name": encoded },
              state: "SUCCESS",
              progress: 100,
              finished_at: "2022-01-31T13:41:04.347656Z",
              expires_at: "2022-02-01T13:41:04.347656Z",
              bytes_received: 1024,
            },
          ],
        });
      })
    );
    const wrapper = mount(DestinationTransferableTable, {
      localVue,
      vuetify,
    });
    await wrapper.vm.$nextTick();
    expect(wrapper.find("tbody").html()).toContain(filename);
  });
});
