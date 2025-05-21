import UploadFileStatus from '@origin/components/UploadFileStatus.vue';
import { mount } from '@vue/test-utils';
import { describe } from 'node:test';
import { expect, it } from 'vitest';

describe('Upload File status tag', () => {
  const TEST_CASES: {
    fileData: { status: 'uploading' | 'uploaded' | 'aborted'; progress: number };
    expected: { class: string[]; text: string };
  }[] = [
    {
      fileData: { status: 'uploading', progress: 52 },
      expected: { class: ['.pi-spinner', '.p-tag-info'], text: 'En cours (52%)' },
    },
    {
      fileData: { status: 'uploaded', progress: 100 },
      expected: { class: ['.pi-check', '.p-tag-success'], text: 'Terminé' },
    },
    {
      fileData: { status: 'aborted', progress: 100 },
      expected: { class: ['.pi-exclamation-triangle', '.p-tag-warn'], text: 'Annulé' },
    },
  ];
  it.each(TEST_CASES)(
    'displays correct information for $fileData.status',
    ({ fileData, expected }) => {
      const wrapper = mount(UploadFileStatus, {
        props: {
          status: fileData.status,
          progress: fileData.progress,
        },
      });
      for (const expectedClass of expected.class) {
        expect(wrapper.find(expectedClass).exists()).toBeTruthy();
      }
    },
  );

  it('upgrades on progress change', async () => {
    const wrapper = mount(UploadFileStatus, {
      props: {
        status: 'uploading',
        progress: 20,
      },
    });
    expect(wrapper.text()).toEqual('En cours (20%)');

    await wrapper.setProps({
      status: 'uploading',
      progress: 40,
    });

    expect(wrapper.text()).toEqual('En cours (40%)');
    await wrapper.setProps({
      status: 'uploaded',
      progress: 100,
    });
    expect(wrapper.text()).toEqual('Terminé');
  });
});
