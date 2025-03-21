import {
  createTransferable,
  validateTransferable,
} from "@origin/api/transferables";
import DropZone from "@origin/components/DropZone";
import { createLocalVue, mount } from "@vue/test-utils";
import Vue from "vue";
import store from "@/common/store";
import Vuetify from "vuetify";
import { Cancel } from "axios";

jest.mock("@origin/api/transferables", () => ({
  createTransferable: jest.fn(),
  validateTransferable: jest.fn(),
}));

describe("DropZone", () => {
  let wrapper;

  const mockedFile =
    "A society that devours its own young deserves no automatic or unquestioning allegiance";
  const fileEntry = {
    isFile: true,
  };
  const directoryEntry = {
    isFile: false,
    isDirectory: true,
  };
  const fileDataTransferItem = {
    webkitGetAsEntry: () => fileEntry,
    getAsFile: () => mockedFile,
  };
  const fileDataTransferItemWithGetAsEntry = {
    getAsEntry: () => fileEntry,
    getAsFile: () => mockedFile,
  };
  const directoryDataTransferItem = {
    webkitGetAsEntry: () => directoryEntry,
  };

  beforeEach(() => {
    const localVue = createLocalVue();
    const vuetify = new Vuetify();
    wrapper = mount(DropZone, { localVue, vuetify, store });
  });
  afterEach(() => {
    jest.resetAllMocks();
  });
  it("renders correctly when sender is working", async () => {
    store.commit("setServerDown", false);
    store.commit("setMaintenance", false);
    await wrapper.vm.$nextTick();
    expect(wrapper.element).toMatchSnapshot();
  });
  it("renders correctly when sender is not working", async () => {
    store.commit("setServerDown", true);
    store.commit("setMaintenance", false);
    await wrapper.vm.$nextTick();
    expect(wrapper.element).toMatchSnapshot();
  });
  it("updates files to ONGOING and SUCCESS states", async () => {
    let createTransferableReturn = null;
    createTransferable.mockReturnValue(
      new Promise((resolve) => {
        createTransferableReturn = resolve;
      })
    );

    wrapper.vm.uploadFiles([{ name: "coucou.exe" }]);
    await wrapper.vm.$nextTick();

    expect(createTransferable).toHaveBeenCalled();
    expect(wrapper.vm.files[0].state).toBe(wrapper.vm.STATES.ONGOING);
    expect(wrapper.find("span.v-chip").classes()).not.toContain("blue");

    createTransferableReturn({ submissionSucceeded: true });
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.files[0].state).toBe(wrapper.vm.STATES.SUCCESS);
    expect(wrapper.find("span.v-chip").classes()).toContain("blue");
  });
  it("updates progress as the file is uploaded", async () => {
    const file = { name: "coucou.exe" };
    // Mock API call so that it doesn't return immediately.
    // Else, the progress would immediately be 100%.
    createTransferable.mockReturnValue(new Promise(() => {}));
    wrapper.vm.uploadFiles([file]);
    await wrapper.vm.$nextTick();

    expect(wrapper.find(".v-progress-linear").attributes("aria-valuenow")).toBe(
      "0"
    );

    file.progressUpdater({ loaded: 84, total: 200 });
    await wrapper.vm.$nextTick();

    expect(wrapper.find(".v-progress-linear").attributes("aria-valuenow")).toBe(
      "42"
    );
  });
  it("shows 100% progress on empty file upload", async () => {
    const file = { name: "coucou.exe", size: 0 };
    createTransferable.mockReturnValue({
      id: "00002800-0000-1000-8000-00805f9b34fb",
    });

    wrapper.vm.uploadFiles([file]);
    await wrapper.vm.$nextTick();

    expect(wrapper.find(".v-progress-linear").attributes("aria-valuenow")).toBe(
      "100"
    );
  });
  it("calls uploadFilesFromEvent on drop event", async () => {
    wrapper.vm.uploadFilesFromEvent = jest.fn();
    wrapper.find(".drop-zone").trigger("drop");

    expect(wrapper.vm.uploadFilesFromEvent).toHaveBeenCalledTimes(1);
  });
  it("uploads files in drop event", async () => {
    const event = {
      dataTransfer: {
        items: [fileDataTransferItem],
      },
    };
    wrapper.vm.uploadFiles = jest.fn();

    wrapper.vm.uploadFilesFromEvent(event);

    expect(wrapper.vm.uploadFiles).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.uploadFiles).toHaveBeenCalledWith([mockedFile]);
  });
  it("only uploads files in drop event", async () => {
    const event = {
      dataTransfer: {
        items: [fileDataTransferItem, directoryDataTransferItem],
      },
    };
    wrapper.vm.uploadFiles = jest.fn();

    wrapper.vm.uploadFilesFromEvent(event);

    expect(wrapper.vm.uploadFiles).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.uploadFiles).toHaveBeenCalledWith([mockedFile]);
  });
  it("alerts when directories are in drop event", async () => {
    Vue.prototype.$alert = jest.fn();
    const event = {
      dataTransfer: {
        items: [directoryDataTransferItem],
      },
    };
    wrapper.vm.uploadFiles = jest.fn();

    wrapper.vm.uploadFilesFromEvent(event);

    expect(Vue.prototype.$alert).toHaveBeenCalledWith(
      "Il n'est pas possible d'envoyer des dossiers, ceux-ci ont été ignorés.",
      "warning"
    );
  });
  it("has a file input field allowing multiple files but forbidding directory upload", async () => {
    const nativeFileInput = wrapper.get("input[type='file']");

    expect(nativeFileInput.attributes()).toHaveProperty("multiple");
    expect(nativeFileInput.attributes()).not.toHaveProperty("webkitdirectory");
    expect(nativeFileInput.attributes()).not.toHaveProperty("allowdirs");
  });
  it("uploads files in drop event if webkitGetAsEntry has been replaced by getAsEntry", async () => {
    const event = {
      dataTransfer: {
        items: [fileDataTransferItemWithGetAsEntry],
      },
    };
    wrapper.vm.uploadFiles = jest.fn();

    wrapper.vm.uploadFilesFromEvent(event);

    expect(wrapper.vm.uploadFiles).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.uploadFiles).toHaveBeenCalledWith([mockedFile]);
  });
  it("alerts when http429 is received because backend is throttling", async () => {
    Vue.prototype.$alert = jest.fn();

    createTransferable.mockReturnValue(
      new Promise((_, reject) => {
        const error = new Error("HTTP 429");
        error.response = {
          status: 429,
          data: { detail: "Request was throttled." },
        };
        reject(error);
      })
    );

    wrapper.vm.uploadFiles([{ name: "coucou.exe" }]);
    await wrapper.vm.$nextTick();

    expect(Vue.prototype.$alert).toHaveBeenCalledWith(
      "Request was throttled.",
      "error"
    );
  });
  it("alerts when http413 is received because the file is too large", async () => {
    Vue.prototype.$alert = jest.fn();

    validateTransferable.mockImplementation(() => {
      const error = new Error("Content Too Large.");
      error.response = {
        status: 413,
        data: { detail: "Content Too Large." },
      };
      throw error;
    });

    wrapper.vm.uploadFiles([{ name: "dump.big" }]);
    await wrapper.vm.$nextTick();

    expect(Vue.prototype.$alert).toHaveBeenCalledWith(
      "Content Too Large.",
      "error"
    );
  });
  it("handles transfer cancellations", async () => {
    Vue.prototype.$alert = jest.fn();

    // The "canceled" string is hardcoded in the axios' source code:
    // https://github.com/axios/axios/blob/1025d1231a7747503188459dd5a6d1effdcea928/lib/adapters/xhr.js#L194
    createTransferable.mockRejectedValue(new Cancel("canceled"));

    wrapper.vm.uploadFiles([{ name: "foo.bar" }]);

    const file = wrapper.vm.files[0];

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(file.state).toBe(wrapper.vm.STATES.CANCELED);
    expect(Vue.prototype.$alert).toHaveBeenCalledWith(
      "Le transfert a été interrompu",
      "info"
    );
  });
});
