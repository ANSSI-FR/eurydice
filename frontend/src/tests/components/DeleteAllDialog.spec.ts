import * as toastMessageService from '@common/services/toast-message.service';
import DeleteAllDialog from '@destination/components/DeleteAllDialog.vue';
import * as transferableService from '@destination/services/transferables.service';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('DeleteAllDialog.vue', () => {
  it('Displays correctly a DeleteAllDialog', async () => {
    const wrapper = mount(DeleteAllDialog, {
      props: {
        modelValue: true,
        //Otherwise it's teleported
        appendTo: 'self',
      },
    });
    const dialog = wrapper.find('[data-testid="TransferableDeleteAllDialog"');
    expect(dialog.exists()).toBeTruthy();
    expect(dialog.isVisible()).toBeTruthy();
    const deleteAllButton = wrapper.find(
      '[data-testid="TransferableDeleteAllDialog-deleteAllButton"]',
    );
    expect(deleteAllButton.exists()).toBeTruthy();
    expect(deleteAllButton.isVisible()).toBeTruthy();
    expect(deleteAllButton.text()).toContain('Supprimer tout');
  });

  it('Deletes correctly all DeleteAllDialog', async () => {
    const spyOnDelete = vi
      .spyOn(transferableService, 'deleteAllTransferables')
      .mockImplementation(() => Promise.resolve());
    const spyOnToastMessage = vi
      .spyOn(toastMessageService, 'toastMessage')
      .mockImplementation(vi.fn());

    const wrapper = mount(DeleteAllDialog, {
      props: { modelValue: true, appendTo: 'self' },
    });

    const deleteAllButton = wrapper.find(
      '[data-testid="TransferableDeleteAllDialog-deleteAllButton"]',
    );
    expect(deleteAllButton.isVisible()).toBeTruthy();
    await deleteAllButton.trigger('click');
    await flushPromises();
    expect(spyOnDelete).toBeCalledTimes(1);
    expect(spyOnToastMessage).toBeCalledTimes(1);
  });
});
