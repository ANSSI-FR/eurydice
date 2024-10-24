import request from "@common/utils/request";

export default function (params = {}) {
  return request({
    url: `/status/`,
    params,
  });
}
