import request from "@common/utils/request";
import { TRANSFERABLE_MAX_SIZE } from "@origin/constants";

export function cancelTransferable(transferableId) {
  return request({
    url: `/transferables/${transferableId}/`,
    method: "DELETE",
  });
}

export function createTransferable(file) {
  return request({
    url: "/transferables/",
    method: "POST",
    data: file,
    headers: {
      "Content-Type": "application/octet-stream",
      "Metadata-Name": encodeURI(file.name),
    },
    onUploadProgress: file.progressUpdater,
    signal: file.abortController.signal,
    timeout: 0,
  });
}

export function validateTransferable(file) {
  if (file?.size > TRANSFERABLE_MAX_SIZE) {
    const err = new Error("413 Content Too Large");
    err.response = {
      status: 413,
      data: {
        detail: `La taille du fichier dépasse le maximum autorisé (${TRANSFERABLE_MAX_SIZE})`,
      },
    };
    throw err;
  }
}
