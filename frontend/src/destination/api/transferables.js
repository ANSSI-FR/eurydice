import request from "@common/utils/request";

// eslint-disable-next-line import/prefer-default-export
export function deleteTransferable(transferableId) {
  return request({
    url: `/transferables/${transferableId}/`,
    method: "DELETE",
  });
}
