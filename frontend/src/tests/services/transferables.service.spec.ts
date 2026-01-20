import apiClient from '@common/api/api-client';
import * as toastMessageService from '@common/services/toast-message.service';
import { listTransferables, retrieveTransferable } from '@common/services/transferables.service';
import {
  deleteAllTransferables,
  deleteTransferable,
  getTransferableData,
} from '@destination/services/transferables.service';
import * as originTransferableService from '@origin/services/transferables';
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

    originTransferableService.createTransferable(
      file,
      false,
      vi.fn(),
      new AbortController().signal,
    );
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
      originTransferableService.createTransferable(
        file,
        false,
        vi.fn(),
        new AbortController().signal,
      ),
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
    await expect(
      originTransferableService.createTransferable(
        file,
        true,
        vi.fn(),
        new AbortController().signal,
      ),
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
  /* ======================= ENCRYPTION ======================= */
  it('use encryption upload when encryption is enabled', async () => {
    const initEncryptedMultipartUploadSpyOn = vi.spyOn(
      originTransferableService,
      'initEncryptedMultipartUpload',
    );
    const uploadEncryptedFilePartsSpyOn = vi.spyOn(
      originTransferableService,
      'uploadEncryptedFileParts',
    );
    const finalizeEncryptedMultipartUploadSpyOn = vi.spyOn(
      originTransferableService,
      'finalizeEncryptedMultipartUpload',
    );

    const file: File = new File(['foo'], 'foo.txt', {
      type: 'text/plain',
    });
    const onUploadProgress = vi.fn();

    console.log('create transferable ', originTransferableService.createTransferable);

    await originTransferableService.createTransferable(
      file,
      true,
      onUploadProgress,
      new AbortController().signal,
    );

    expect(initEncryptedMultipartUploadSpyOn).toHaveBeenCalled();
    expect(uploadEncryptedFilePartsSpyOn).toHaveBeenCalled();
    expect(finalizeEncryptedMultipartUploadSpyOn).toHaveBeenCalled();
  });

  it.each([
    { partSize: 1, expected: 9 },
    { partSize: 2, expected: 5 },
    { partSize: 9, expected: 1 },
    { partSize: 10, expected: 1 },
  ])('yieldFileParts function succeeds', async ({ partSize, expected }) => {
    const file: File = new File(['123456789'], 'foo.txt', {
      type: 'text/plain',
    });

    const nbTotalParts = Math.ceil(file.size / partSize);

    const partsGenerator = originTransferableService.yieldFileParts(file, partSize, nbTotalParts);
    const fileParts = [];
    let result = partsGenerator.next();
    while (!result.done) {
      fileParts.push(result.value);
      result = partsGenerator.next();
    }

    expect(fileParts.length).toBe(expected);
    const last_part = fileParts[fileParts.length - 1];
    if (last_part) {
      expect(last_part.index).toBe(expected - 1);
    }
  });
});
