import apiClient from '@common/api/api-client';
import AssociationTokenMenuItem from '@origin/components/AssociationTokenMenuItem.vue';
import { flushPromises, mount } from '@vue/test-utils';
import { Button, Dialog, Textarea } from 'primevue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

describe('Association Token Menu Item', () => {
  beforeEach(() => {
    vi.restoreAllMocks(); // Ensures fresh mocks before each test
  });

  it('Contains a button', () => {
    const wrapper = mount(AssociationTokenMenuItem);
    const btn = wrapper.findComponent(Button);
    expect(btn.exists()).toBe(true);
    expect(btn.text()).toBe("Jeton d'association");
  });
  it('Gets the token via request', async () => {
    const mockFunction = async () => Promise.resolve({ token: 'fake TOKEN' });

    const spyOnGetAssociationToken = vi.spyOn(apiClient, 'get').mockImplementation(mockFunction);
    expect(spyOnGetAssociationToken).not.toBeCalled();
    mount(AssociationTokenMenuItem);
    expect(spyOnGetAssociationToken).toBeCalled();
  });
  it('Shows a Dialog when the button is clicked', async () => {
    const mockFunction = async () => Promise.resolve({ token: 'fake TOKEN' });

    const spyOnGetAssociationToken = vi.spyOn(apiClient, 'get').mockImplementation(mockFunction);
    expect(spyOnGetAssociationToken).not.toBeCalled();
    const wrapper = mount(AssociationTokenMenuItem);

    const btn = wrapper.findComponent(Button);
    await btn.trigger('click');

    const tokenDialog = wrapper.findComponent(Dialog);
    expect(tokenDialog.props('visible')).toBe(true);
  });
  it('Contains the fetched Token in the Dialog', async () => {
    vi.clearAllMocks();
    const wrapper = mount(AssociationTokenMenuItem);
    const btn = wrapper.findComponent(Button);
    await btn.trigger('click');
    await flushPromises();
    const tokenDialog = wrapper.findComponent(Dialog);

    const textarea = tokenDialog.findComponent(Textarea);
    expect(textarea.exists()).toBe(true);
    expect(textarea.attributes('value')).toBe('test token PHRASE');
  });
  it('Copies the Token to the clipboard when Copy button is clicked', async () => {
    vi.clearAllMocks();

    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: vi.fn().mockResolvedValue(''),
      },
      writable: true,
    });
    const spyOnClipboardWrite = vi.spyOn(navigator.clipboard, 'writeText');
    expect(spyOnClipboardWrite).not.toBeCalled();

    const wrapper = mount(AssociationTokenMenuItem, { global: { stubs: { teleport: true } } });
    const btn = wrapper.getComponent(Button);
    await btn.trigger('click');

    await flushPromises();
    const copyBtn = wrapper.find('[data-testid="AssociationToken_copyBtn"]');
    await copyBtn.trigger('click');
    expect(spyOnClipboardWrite).toBeCalledWith('test token PHRASE');
  });
});
