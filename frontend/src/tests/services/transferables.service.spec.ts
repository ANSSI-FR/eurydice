import apiClient from '@common/api/api-client';
import * as toastMessageService from '@common/services/toast-message.service';
import { listTransferables, retrieveTransferable } from '@common/services/transferables.service';
import {
  deleteAllTransferables,
  deleteTransferable,
  getTransferableData,
} from '@destination/services/transferables.service';
import * as originTransferableService from '@origin/services/transferables.service';
import { describe, expect, it, vi } from 'vitest';

describe('Transferable service', () => {
  it('calls the correct endpoints', () => {
    const id = 'f3f2e850-b5d4-11ef-ac7e-96584d5248b2';
    const file: File = new File(['foo'], 'foo.txt', {
      type: 'text/plain',
    });
    const getSpyOn = vi.spyOn(apiClient, 'get').mockImplementation(vi.fn());
    const deleteSpyOn = vi.spyOn(apiClient, 'delete').mockImplementation(vi.fn());
    const postSpyOn = vi.spyOn(apiClient, 'post').mockImplementation(vi.fn());
    listTransferables();

    expect(getSpyOn).toBeCalledTimes(1);
    retrieveTransferable(id);

    expect(getSpyOn).toBeCalledTimes(2);
    expect(getSpyOn).toHaveBeenLastCalledWith(expect.stringContaining(id));

    getTransferableData(id);
    expect(getSpyOn).toBeCalledTimes(3);
    expect(getSpyOn).toHaveBeenLastCalledWith(
      expect.stringContaining(id),
      expect.objectContaining({ responseType: 'text' }),
    );

    deleteTransferable(id);
    expect(deleteSpyOn).toBeCalledTimes(1);
    expect(deleteSpyOn).toHaveBeenLastCalledWith(expect.stringContaining(id));

    deleteAllTransferables();
    expect(deleteSpyOn).toBeCalledTimes(2);

    originTransferableService.createTransferable(file, vi.fn(), new AbortController().signal);
    expect(postSpyOn).toBeCalledTimes(1);

    originTransferableService.cancelTransferable(id);
    expect(deleteSpyOn).toBeCalledTimes(3);
    expect(deleteSpyOn).toHaveBeenLastCalledWith(expect.stringContaining(id));
  });

  it('verifies correctly the file size', () => {
    vi.stubEnv('VITE_TRANSFERABLE_MAX_SIZE', '5');
    const file: File = new File(['foo'], 'foo.txt', {
      type: 'text/plain',
    });
    expect(originTransferableService.validateTransferable(file)).toBeTruthy();
    expect(originTransferableService.validateTransferable({ size: 6 })).toBeFalsy();

    vi.stubEnv('VITE_TRANSFERABLE_MAX_SIZE', undefined);

    expect(originTransferableService.validateTransferable({ size: 6 })).toBeTruthy();
    expect(originTransferableService.validateTransferable({ size: 54975581388801 })).toBeFalsy();

    expect(originTransferableService.validateTransferable({})).toBeFalsy();
  });

  it('verifies the file size before create transferable', async () => {
    vi.stubEnv('VITE_TRANSFERABLE_MAX_SIZE', '5');
    const file: File = new File(['This is more than 5 Bytes'], 'foo.txt', {
      type: 'text/plain',
    });

    const postSpyOn = vi.spyOn(apiClient, 'post').mockImplementation(vi.fn());
    const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());
    await expect(
      originTransferableService.createTransferable(file, vi.fn(), new AbortController().signal),
    ).rejects.toThrow();
    expect(spyOnToast).toHaveBeenCalledWith(
      'ValidateTansferable.fileTooLargeTitle',
      'ValidateTansferable.fileTooLargeMessage',
      'error',
      true,
      {
        paramsMessage: {
          fileSize: '25 octets',
          maxFileSize: '5 octets',
        },
      },
    );
    expect(postSpyOn).not.toHaveBeenCalled();
  });
});
