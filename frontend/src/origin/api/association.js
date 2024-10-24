import request from "@common/utils/request";

// eslint-disable-next-line import/prefer-default-export
export function getAssociationToken(params = {}) {
  return request({
    url: `/user/association/`,
    params,
  });
}
