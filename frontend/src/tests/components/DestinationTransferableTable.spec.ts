import * as toastMessageService from '@common/services/toast-message.service';
import * as transferableServiceCommon from '@common/services/transferables.service';
import DestinationTransferableTable from '@destination/components/DestinationTransferableTable.vue';
import * as transferableService from '@destination/services/transferables.service';
import {
  noPreviewTransferableListResponseMock,
  transferableListResponseMock,
} from '@tests/mocks/transferableListResponse.mock';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('DestinationTransferableTable.vue', () => {
  it('Displays correctly a DestinationTransferableTable', async () => {
    const wrapper = mount(DestinationTransferableTable);
    expect(wrapper.find('[data-testid="TransferableTable"').exists()).toBeTruthy();
    expect(wrapper.find('[data-testid="TransferableTable"').isVisible()).toBeTruthy();
    const deleteAllButton = wrapper.find(
      '[data-testid="DestinationTransferableTable-deleteAllButton"]',
    );
    expect(deleteAllButton.exists()).toBeTruthy();
    expect(deleteAllButton.isVisible()).toBeTruthy();
  });
  it(
    'Deletes correctly all transferables from DestinationTransferableTable',
    async () => {
      const spyOnDeleteAll = vi
        .spyOn(transferableService, 'deleteAllTransferables')
        .mockImplementation(() => Promise.resolve());
      const spyOnToastMessage = vi
        .spyOn(toastMessageService, 'toastMessage')
        .mockImplementation(vi.fn());
      const wrapper = mount(DestinationTransferableTable, {
        global: { stubs: { Teleport: true } },
      });
      const deleteAllButton = wrapper.find(
        '[data-testid="DestinationTransferableTable-deleteAllButton"]',
      );
      await deleteAllButton.trigger('click');
      await flushPromises();
      expect(spyOnDeleteAll).not.toBeCalled();
      const deleteAllDialog = wrapper.find('[data-testid="TransferableDeleteAllDialog"]');
      expect(deleteAllDialog.exists()).toBeTruthy();
      const deleteAllDialogButton = wrapper.find(
        '[data-testid="TransferableDeleteAllDialog-deleteAllButton"]',
      );
      expect(deleteAllDialogButton.isVisible()).toBeTruthy();
      await deleteAllDialogButton.trigger('click');
      await flushPromises();
      expect(spyOnDeleteAll).toBeCalled();
      expect(spyOnToastMessage).toBeCalled();
    },
    { timeout: 10000 },
  );

  it('Deletes correctly all selected transferables from DestinationTransferableTable', async () => {
    const spyOnDelete = vi
      .spyOn(transferableService, 'deleteTransferable')
      .mockImplementation(() => Promise.resolve());
    const spyOnToastMessage = vi
      .spyOn(toastMessageService, 'toastMessage')
      .mockImplementation(vi.fn());

    const wrapper = mount(DestinationTransferableTable, { global: { stubs: { Teleport: true } } });

    await flushPromises();

    let deleteMultipleButton = wrapper.find(
      '[data-testid="DestinationTransferableTable-deleteMultipleButton"]',
    );
    expect(deleteMultipleButton.exists()).toBeFalsy();

    // We find the selectAll checkbox of the table
    const selectAllCheckbox = wrapper.find('.p-datatable-column-header-content .p-checkbox-input');

    expect(selectAllCheckbox.exists()).toBeTruthy();

    if (selectAllCheckbox) {
      // We select all transferable in the table
      selectAllCheckbox.setValue(true);
      await selectAllCheckbox.trigger('input');

      deleteMultipleButton = wrapper.find(
        '[data-testid="DestinationTransferableTable-deleteMultipleButton"]',
      );
      // We expect the deleteMultipleButton to be enabled
      expect(deleteMultipleButton.exists()).toBeTruthy();
      await deleteMultipleButton.trigger('click');
      await flushPromises();

      // We expect the function not to be called yet : we wait for confirmation in the dialog
      expect(spyOnDelete).not.toBeCalled();

      // A dialog should be visible
      const deleteMultipleDialog = wrapper.find('[data-testid="TransferableDeleteMultipleDialog"]');
      expect(deleteMultipleDialog.exists()).toBeTruthy();
      const deleteMultipleDialogButton = wrapper.find(
        '[data-testid="TransferableDeleteMultipleDialog-deleteMultipleButton"]',
      );
      expect(deleteMultipleDialogButton.isVisible()).toBeTruthy();
      await deleteMultipleDialogButton.trigger('click');
      await flushPromises();

      // We expect the delete function to be called 5 times because there is only 5 files deletable
      expect(spyOnDelete).toBeCalledTimes(5);
      expect(spyOnToastMessage).toBeCalledTimes(1);
    }
  });

  it('Deletes correctly one item from DestinationTransferableTable', async () => {
    const spyOnDelete = vi
      .spyOn(transferableService, 'deleteTransferable')
      .mockImplementation(() => Promise.resolve());
    const spyOnToastMessage = vi
      .spyOn(toastMessageService, 'toastMessage')
      .mockImplementation(vi.fn());

    const wrapper = mount(DestinationTransferableTable, { global: { stubs: { Teleport: true } } });
    await flushPromises();

    const deleteSingleButtons = wrapper.findAll(
      '[data-testid="DestinationTransferableTable-deleteSingleItemButton"]',
    );
    expect(deleteSingleButtons.length).toEqual(5);

    const deleteSingleButton = deleteSingleButtons[0]!;
    await deleteSingleButton.trigger('click');
    await flushPromises();
    expect(spyOnDelete).not.toBeCalled();
    const deleteSingleDialog = wrapper.find('[data-testid="TransferableDeleteMultipleDialog"]');
    expect(deleteSingleDialog.exists()).toBeTruthy();
    const deleteSingleDialogButton = wrapper.find(
      '[data-testid="TransferableDeleteMultipleDialog-deleteMultipleButton"]',
    );
    expect(deleteSingleDialogButton.isVisible()).toBeTruthy();
    await deleteSingleDialogButton.trigger('click');
    await flushPromises();
    expect(spyOnDelete).toBeCalledTimes(1);
    expect(spyOnToastMessage).toBeCalledTimes(1);
  });

  it('Has the correct href to download individual transferables', async () => {
    vi.spyOn(transferableServiceCommon, 'listTransferables').mockImplementation(() => {
      return Promise.resolve(transferableListResponseMock);
    });
    const wrapper = mount(DestinationTransferableTable, { global: { stubs: { Teleport: true } } });
    await flushPromises();
    const downloadLink = wrapper.findAll('[data-testid="TransferableTable-DownloadButton"]')[0]!;
    const downloadLinkRegexp = new RegExp(
      `${import.meta.env.VITE_API_URL}/transferables/[\\-\\d\\w]+/download`,
    );
    expect(downloadLink.attributes('href')).toMatch(downloadLinkRegexp);
  });

  it('Opens a PreviewDialog Component when click on preview button', async () => {
    const spyOnListTransferables = vi
      .spyOn(transferableServiceCommon, 'listTransferables')
      .mockImplementation(() => {
        return Promise.resolve(transferableListResponseMock);
      });
    const wrapper = mount(DestinationTransferableTable, { global: { stubs: { Teleport: true } } });
    expect(spyOnListTransferables).toBeCalled();
    await flushPromises();

    const previewBtn = wrapper.find('[data-testid="DestinationTransferableTable-previewButton"]');
    expect(previewBtn.isVisible()).toBeTruthy();

    await previewBtn.trigger('click');
    const previewDialog = wrapper.find('[data-testid="TransferablePreviewDialog"]');
    expect(previewDialog.exists()).toBeTruthy();
    expect(previewDialog.isVisible()).toBeTruthy();
  });

  it('Disables preview button on certain conditions', async () => {
    const spyOnListTransferables = vi
      .spyOn(transferableServiceCommon, 'listTransferables')
      .mockImplementation(() => {
        return Promise.resolve(noPreviewTransferableListResponseMock);
      });
    const wrapper = mount(DestinationTransferableTable, { global: { stubs: { Teleport: true } } });
    expect(spyOnListTransferables).toBeCalled();
    await flushPromises();

    const previewBtn = wrapper.find('[data-testid="DestinationTransferableTable-previewButton"]');
    expect(previewBtn.isVisible()).toBeTruthy();

    expect(previewBtn.attributes('disabled')).toBeDefined();
    await previewBtn.trigger('click');
    const previewDialog = wrapper.find('[data-testid="TransferablePreviewDialog"]');
    expect(previewDialog.exists()).toBeFalsy();
  });
});
