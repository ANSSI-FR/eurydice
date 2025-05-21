import TransferableTable from '@common/components/TransferableTable.vue';
import * as transferableService from '@common/services/transferables.service';
import { transferableListMock } from '@tests/mocks/transferableList.mock';
import {
  newItemsTransferableListResponseMock,
  transferableListResponseMock,
  transferableListResponseMockPage1,
  transferableListResponseMockPage2,
  transferableListResponseMockPage3WithNewItems,
  transferableListResponseMockPage4,
} from '@tests/mocks/transferableListResponse.mock';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('TransferableTable.vue', () => {
  it('Displays correctly a TransferableTable', async () => {
    const spyOnListTransferables = vi
      .spyOn(transferableService, 'listTransferables')
      .mockImplementation(() => {
        return Promise.resolve(transferableListResponseMock);
      });
    const wrapper = mount(TransferableTable);
    expect(wrapper.find('[data-testid="TransferableTable"').exists()).toBeTruthy();
    expect(wrapper.find('[data-testid="TransferableTable"').isVisible()).toBeTruthy();
    expect(spyOnListTransferables).toBeCalled();
    await flushPromises();
    expect(wrapper.findAll('[data-testid="TransferableStateTag"]').length).toEqual(8);

    // Expect to find column names
    for (const columnName of ['Nom', 'SHA-1', 'Taille', 'État', 'Créé le', 'Actions']) {
      expect(wrapper.text()).toContain(columnName);
    }

    // Expect to find the name of each files
    for (const fileName of transferableListResponseMock.results.map((fileItem) => fileItem.name)) {
      expect(wrapper.text()).toContain(fileName);
    }

    // Expect to find no action
    const noActionSlots = wrapper.findAll('[data-testid="TransferableTable.noAction"]');
    expect(noActionSlots.length).toEqual(transferableListMock.length);
  });

  it('Paginates correctly', async () => {
    const pageSize = 2;
    vi.stubEnv('VITE_TRANSFERABLES_PER_PAGE', pageSize.toString());
    const spyOnListTransferables = vi
      .spyOn(transferableService, 'listTransferables')
      .mockImplementation(() => {
        return Promise.resolve(transferableListResponseMockPage1);
      });
    const wrapper = mount(TransferableTable, {
      global: {
        stubs: {
          Teleport: true,
        },
      },
    });
    await flushPromises();
    expect(spyOnListTransferables).toBeCalledWith({
      delta: undefined,
      from: undefined,
      pageSize,
    });
    const paginatorPages = wrapper.findAll('.p-paginator-page');
    expect(paginatorPages.length).toEqual(transferableListMock.length / pageSize);

    const paginatorSelectedPage = wrapper.findAll('.p-paginator-page-selected');
    expect(paginatorSelectedPage.length).toEqual(1);

    expect(wrapper.findAll('[data-testid="TransferableStateTag"]').length).toEqual(pageSize);

    spyOnListTransferables.mockImplementation(() => {
      return Promise.resolve(transferableListResponseMockPage2);
    });
    const nextPageButton = wrapper.findAll('.p-paginator-next');
    expect(nextPageButton.length).toEqual(1);

    await nextPageButton[0].trigger('click');
    await flushPromises();
    expect(spyOnListTransferables).toBeCalledWith({
      delta: 1,
      from: 'pageOld',
      pageSize,
    });

    spyOnListTransferables.mockImplementation(() => {
      return Promise.resolve(transferableListResponseMockPage4);
    });
    const fourthPage = paginatorPages.find(
      (paginatorPage) => paginatorPage.attributes('aria-label') === 'Page 4',
    );
    expect(fourthPage).toBeDefined();

    await fourthPage?.trigger('click');
    await flushPromises();
    expect(spyOnListTransferables).toBeCalledWith({
      delta: 2,
      from: 'pageOld',
      pageSize,
    });

    spyOnListTransferables.mockImplementation(() => {
      return Promise.resolve(transferableListResponseMockPage3WithNewItems);
    });
    const thirdPage = paginatorPages.find(
      (paginatorPage) => paginatorPage.attributes('aria-label') === 'Page 3',
    );
    expect(thirdPage).toBeDefined();
    await thirdPage?.trigger('click');
    await flushPromises();
    expect(spyOnListTransferables).toBeCalledWith({
      delta: -1,
      from: 'pageOld',
      pageSize,
    });

    const refreshButton = wrapper.find('[data-testid="TransferableTable-refreshNewItemsButton"]');
    expect(refreshButton.exists()).toBeTruthy();

    spyOnListTransferables.mockImplementation(() => {
      return Promise.resolve(newItemsTransferableListResponseMock);
    });
    await refreshButton.trigger('click');
    await flushPromises();
    expect(spyOnListTransferables).toBeCalledWith({
      delta: undefined,
      from: undefined,
      pageSize,
    });

    await nextPageButton[0].trigger('click');
    await flushPromises();
    expect(spyOnListTransferables).toBeCalledWith({
      delta: 1,
      from: 'pageNew',
      pageSize,
    });
  });
});
