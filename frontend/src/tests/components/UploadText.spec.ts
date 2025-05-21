import UploadText from '@origin/components/UploadText.vue';
import * as transferableService from '@origin/services/transferables.service';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('UploadText Component', () => {
  it('Displays text area, button and no error message', () => {
    const wrapper = mount(UploadText);

    const textArea = wrapper.find('[data-testid="UploadText-textArea"]');
    expect(textArea.isVisible()).toBeTruthy();

    const sendButton = wrapper.find('[data-testid="UploadText-sendButton"]');
    expect(sendButton.isVisible()).toBeTruthy();
    expect(sendButton.text()).toContain('Envoyer');
    expect(sendButton.attributes('data-p-disabled')).toEqual('true');

    const errorMessage = wrapper.find('[data-testid="UploadText-errorMessage"]');
    expect(errorMessage.exists()).toBeFalsy();
  });

  it('Calls transferable function when sending text', async () => {
    const textInput = 'This is a test';
    const spyOnTransferableCreate = vi
      .spyOn(transferableService, 'createTransferable')
      .mockImplementation(() => Promise.resolve());
    const wrapper = mount(UploadText);
    const textArea = wrapper.find('[data-testid="UploadText-textArea"]');
    await textArea.setValue(textInput);

    const sendButton = wrapper.find('[data-testid="UploadText-sendButton"]');
    expect(sendButton.attributes('data-p-disabled')).toEqual('false');

    await sendButton.trigger('click');
    await flushPromises();
    expect(spyOnTransferableCreate).toBeCalled();
  });

  it('Show error message when failing send', async () => {
    const textInput = 'This is a test';
    const spyOnTransferableCreate = vi
      .spyOn(transferableService, 'createTransferable')
      .mockImplementation(() => Promise.reject());
    const wrapper = mount(UploadText);
    const textArea = wrapper.find('[data-testid="UploadText-textArea"]');
    await textArea.setValue(textInput);

    const sendButton = wrapper.find('[data-testid="UploadText-sendButton"]');
    expect(sendButton.attributes('data-p-disabled')).toEqual('false');

    await sendButton.trigger('click');
    await flushPromises();
    expect(spyOnTransferableCreate).toBeCalled();

    const errorMessage = wrapper.find('[data-testid="UploadText-errorMessage"]');
    expect(errorMessage.isVisible()).toBeTruthy();
  });
});
