import axiosClient from "@common/utils/request";
import router from "@destination/router";

const UNASSOCIATED_USER_HTTP_STATUS_CODE = 403;

export default function setup() {
  axiosClient.interceptors.response.use(
    (response) => response,
    // eslint-disable-next-line require-await
    async (error) => {
      if (error.response.status === UNASSOCIATED_USER_HTTP_STATUS_CODE) {
        router.push({ name: "userAssociation" });
      }
      throw error;
    }
  );
}
