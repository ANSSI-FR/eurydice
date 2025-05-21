import * as toastMessageService from '@common/services/toast-message.service';
import UploadFile from '@origin/components/UploadFile.vue';
import * as transferableService from '@origin/services/transferables.service';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('UploadFile Component', () => {
  it('Displays a text to drag n drop files when empty', () => {
    const wrapper = mount(UploadFile);
    const dragndropZone = wrapper.find('[data-testid="UploadFile.emptyDragndropZone"]');
    expect(dragndropZone.isVisible()).toBeTruthy();
    expect(dragndropZone.text()).toContain('Déposez vos fichiers ici');

    const uploadFileButton = wrapper.find('[data-testid="UploadFile.uploadFileButton"]');
    expect(uploadFileButton.isVisible()).toBeTruthy();
    expect(uploadFileButton.text()).toContain('Ajouter un nouveau fichier');

    const total = wrapper.find('[data-testid="UploadFile.total"]');
    expect(total.isVisible()).toBeTruthy();
    expect(total.text()).toContain('Aucun fichier (0 octets)');
  });

  const TEST_CASES: {
    situation: string;
    mockCreateTransferable: () => Promise<void>;
    expectedFileStatus: string;
    successToast: boolean;
    clearAll: boolean;
  }[] = [
    {
      situation: 'succès',
      mockCreateTransferable: async () => Promise.resolve(),
      expectedFileStatus: 'Terminé',
      successToast: true,
      clearAll: true,
    },
    {
      situation: 'erreur',
      mockCreateTransferable: async () => Promise.reject(),
      expectedFileStatus: 'Erreur',
      successToast: false,
      clearAll: true,
    },
    {
      situation: 'en cours',
      mockCreateTransferable: async () =>
        new Promise((resolve) => {
          setTimeout(() => {
            resolve();
          }, 1000);
        }),
      expectedFileStatus: 'En cours (0%)',
      successToast: false,
      clearAll: false,
    },
  ];

  it.each(TEST_CASES)(
    'Uploads correctly in $situation situation',
    async ({ mockCreateTransferable, expectedFileStatus, successToast, clearAll }) => {
      const files: File[] = [
        new File(['foo'], 'foo.txt', {
          type: 'text/plain',
        }),
        new File(['foo1'], 'foo1.txt', {
          type: 'text/plain',
        }),
      ];

      const spyOnTransferableCreate = vi
        .spyOn(transferableService, 'createTransferable')
        .mockImplementation(mockCreateTransferable);
      const spyOnToastMessageService = vi
        .spyOn(toastMessageService, 'toastMessage')
        .mockImplementation(vi.fn());
      const wrapper = mount(UploadFile);
      await wrapper.trigger('upload-test', { files: files });
      await flushPromises();
      expect(spyOnTransferableCreate).toHaveBeenCalledTimes(2);
      expect(spyOnToastMessageService).toHaveBeenCalledTimes(successToast ? 2 : 0);

      const dragndropZone = wrapper.find('[data-testid="UploadFile.emptyDragndropZone"]');
      expect(dragndropZone.exists()).toBeFalsy();

      let fileItems = wrapper.findAll('[data-testid="UploadFileItem"]');
      const fileItemNames = wrapper.findAll('[data-testid="UploadFileItem.name"');

      expect(fileItemNames.length).toEqual(2);
      for (const item of fileItemNames) {
        expect(['foo.txt', 'foo1.txt']).toContain(item.text());
      }

      for (const item of fileItems) {
        expect(item.text()).toContain(expectedFileStatus);
      }

      const clearDownloadsButton = wrapper.find('[data-testid="UploadFile.clearFilesButton"]');
      expect(clearDownloadsButton.exists()).toBeTruthy();
      expect(clearDownloadsButton.isVisible()).toBeTruthy();

      const total = wrapper.find('[data-testid="UploadFile.total"]');
      expect(total.isVisible()).toBeTruthy();
      expect(total.text()).toContain('2 fichiers (7 octets)');

      await clearDownloadsButton.trigger('click');
      fileItems = wrapper.findAll('[data-testid="UploadFileItem"]');
      expect(fileItems.length).toEqual(clearAll ? 0 : 2);

      if (clearAll) {
        const total = wrapper.find('[data-testid="UploadFile.total"]');
        expect(total.isVisible()).toBeTruthy();
        expect(total.text()).toContain('Aucun fichier (0 octets)');
      }
    },
  );
});
