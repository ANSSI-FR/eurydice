import request from "@common/utils/request";

// eslint-disable-next-line import/prefer-default-export
export function postAssociationToken(token) {
  return request({
    url: `/user/association/`,
    method: "POST",
    data: { token },
  });
}
