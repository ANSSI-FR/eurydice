import * as toastMessageService from '@common/services/toast-message.service';
import DeleteMultipleDialog from '@destination/components/DeleteMultipleDialog.vue';
import * as transferableService from '@destination/services/transferables.service';
import { transferableListMock } from '@tests/mocks/transferableList.mock';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('DeleteMultipleDialog.vue', () => {
  it('Displays correctly a DeleteMultipleDialog', async () => {
    const wrapper = mount(DeleteMultipleDialog, {
      props: {
        selectedTransferables: transferableListMock,
        modelValue: true,
        //Otherwise it's teleported
        appendTo: 'self',
      },
    });
    const dialog = wrapper.find('[data-testid="TransferableDeleteMultipleDialog"');
    expect(dialog.exists()).toBeTruthy();
    expect(dialog.isVisible()).toBeTruthy();
    const deleteMultipleButton = wrapper.find(
      '[data-testid="TransferableDeleteMultipleDialog-deleteMultipleButton"]',
    );
    expect(deleteMultipleButton.exists()).toBeTruthy();
    expect(deleteMultipleButton.isVisible()).toBeTruthy();
    expect(deleteMultipleButton.text()).toContain('Supprimer les fichiers sélectionnés');

    for (const transferable of transferableListMock) {
      expect(dialog.text()).toContain(transferable.name);
    }
  });

  it('Deletes correctly all transferables from DeleteMultipleDialog', async () => {
    let isVisible: boolean = true;
    const spyOnDelete = vi
      .spyOn(transferableService, 'deleteTransferable')
      .mockImplementation(() => Promise.resolve());
    const spyOnToastMessage = vi
      .spyOn(toastMessageService, 'toastMessage')
      .mockImplementation(vi.fn());

    const wrapper = mount(DeleteMultipleDialog, {
      props: {
        selectedTransferables: transferableListMock,
        modelValue: isVisible,
        //Otherwise it's teleported
        appendTo: 'self',
        'onUpdate:modelValue': (value: boolean | undefined) => {
          isVisible = value ?? false;
        },
      },
    });

    const deleteMultipleButton = wrapper.find(
      '[data-testid="TransferableDeleteMultipleDialog-deleteMultipleButton"]',
    );
    expect(deleteMultipleButton.isVisible()).toBeTruthy();
    await deleteMultipleButton.trigger('click');
    await flushPromises();
    expect(spyOnDelete).toBeCalledTimes(transferableListMock.length);
    for (const transferable of transferableListMock) {
      expect(spyOnDelete).toHaveBeenCalledWith(transferable.id);
    }
    expect(spyOnToastMessage).toBeCalledTimes(1);
    expect(isVisible).toBeFalsy();
  });

  it('Does not call delete if transferable list is undefined', async () => {
    let isVisible: boolean = true;
    const spyOnDelete = vi
      .spyOn(transferableService, 'deleteTransferable')
      .mockImplementation(() => Promise.resolve());
    const spyOnToastMessage = vi
      .spyOn(toastMessageService, 'toastMessage')
      .mockImplementation(vi.fn());

    const wrapper = mount(DeleteMultipleDialog, {
      props: {
        selectedTransferables: undefined,
        modelValue: isVisible,
        //Otherwise it's teleported
        appendTo: 'self',
        'onUpdate:modelValue': (value: boolean | undefined) => {
          isVisible = value ?? false;
        },
      },
    });

    const deleteMultipleButton = wrapper.find(
      '[data-testid="TransferableDeleteMultipleDialog-deleteMultipleButton"]',
    );
    expect(deleteMultipleButton.isVisible()).toBeTruthy();
    await deleteMultipleButton.trigger('click');
    await flushPromises();
    expect(spyOnDelete).not.toBeCalled();
    expect(spyOnToastMessage).toBeCalledTimes(1);
    expect(isVisible).toBeFalsy();
  });
});
