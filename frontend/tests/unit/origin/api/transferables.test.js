import request from "@common/utils/request";
import { TRANSFERABLE_MAX_SIZE } from "@origin/constants";
import {
  createTransferable,
  validateTransferable,
} from "@origin/api/transferables";

jest.mock("@common/utils/request", () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe("Origin transferable-related API calls", () => {
  it("encodes file names correctly", () => {
    const filename = "x=шеллы.lolz";
    const encoded = encodeURI(filename);

    createTransferable({
      name: filename,
      abortController: { signal: null },
    });

    expect(request).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({ "Metadata-Name": encoded }),
      })
    );
  });
  it("checks that file contents are below the configured limit", () => {
    const validate = jest.fn((name, size) =>
      validateTransferable({ name, size })
    );
    validate("foo.txt", 32);
    expect(validate).toHaveReturned();
    expect(() => validate("bar.txt", TRANSFERABLE_MAX_SIZE + 1)).toThrow(
      "413 Content Too Large"
    );
  });
});
