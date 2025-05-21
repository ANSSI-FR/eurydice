import apiClient from '@common/api/api-client';
import * as toastMessageService from '@common/services/toast-message.service';
import PreviewDialog from '@destination/components/PreviewDialog.vue';
import { txtTransferableMock } from '@tests/mocks/transferable.mock';
import { flushPromises, mount } from '@vue/test-utils';
import { Textarea } from 'primevue';
import { describe, expect, it, vi } from 'vitest';

describe('PreviewDialog', () => {
  it('Has a Textarea Component with the correct fetched value', async () => {
    const mockFunction = () => Promise.resolve('fake content');
    vi.spyOn(apiClient, 'get').mockImplementation(mockFunction);

    const wrapper = mount(PreviewDialog, {
      props: {
        transferable: txtTransferableMock,
        modelValue: true,
      },
    });
    await flushPromises();

    const previewTextarea = wrapper.findComponent(Textarea);
    expect(previewTextarea.isVisible()).toBeTruthy();
    expect(previewTextarea.attributes('value')).toBe('fake content');
  });
  it('Copies the fetched text to clipboard', async () => {
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: vi.fn().mockResolvedValue(''),
      },
      writable: true,
    });
    const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());
    const spyOnClipboardWrite = vi.spyOn(navigator.clipboard, 'writeText');
    expect(spyOnClipboardWrite).not.toBeCalled();

    const mockFunction = () => Promise.resolve('fake content');
    vi.spyOn(apiClient, 'get').mockImplementation(mockFunction);

    const wrapper = mount(PreviewDialog, {
      props: {
        transferable: txtTransferableMock,
        modelValue: true,
      },
      global: { stubs: { teleport: true } },
    });
    await flushPromises();

    const copyAndCloseBtn = wrapper.find('[data-testid="PreviewDialog_copyAndCloseBtn"]');
    expect(copyAndCloseBtn.isVisible()).toBeTruthy();
    await copyAndCloseBtn.trigger('click');
    expect(spyOnClipboardWrite).toBeCalledWith('fake content');
    expect(spyOnToast).toHaveBeenCalledWith(
      'TransferablePreviewDialog.copyMessage.title',
      'TransferablePreviewDialog.copyMessage.message',
      'success',
      true,
    );
  });
});
