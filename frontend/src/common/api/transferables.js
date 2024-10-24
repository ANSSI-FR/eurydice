import request from "@common/utils/request";

export function listTransferables(params = {}, abortSignal) {
  return request({
    url: "/transferables/",
    signal: abortSignal,
    params,
  });
}

export function retrieveTransferable(transferableId, params = {}) {
  return request({
    url: `/transferables/${transferableId}/`,
    params,
  });
}
