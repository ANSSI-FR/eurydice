import apiClient from '@common/api/api-client';
import { toastMessage } from '@common/services/toast-message.service';
import { useUserStore } from '@common/store/user.store';
import { objectKeysToCamelCase } from '@common/utils/case-functions';
import { router } from '@destination/router';
import type { AxiosResponse } from 'axios';
import axios from 'axios';

const LOGIN_ENDPOINT = import.meta.env.VITE_LOGIN_ENDPOINT ?? '/user/login/';

export const snakeCaseToCamelCaseInterceptor = (response: AxiosResponse<any, any>) => {
  return objectKeysToCamelCase(response.data);
};

const hasBasicAuthHeader = (response: AxiosResponse) => {
  const headerName = 'www-authenticate';
  const headerValue = 'Basic';
  const headers = response?.headers;
  if (headers === undefined) {
    return false;
  }
  return headers[headerName]?.includes(headerValue) === true;
};

export const errorInterceptor = (error: any) => {
  // Do not mark canceled transferables as error
  if (error.response === undefined && !(error instanceof axios.Cancel)) {
    toastMessage('Error.Network.title', error.message, 'error', true);
  }

  // Handle missing session cookie if no basic auth header or not contacting login_endpoint
  else if (
    error.response.status === 401 &&
    !hasBasicAuthHeader(error.response) &&
    error.response.config?.url !== LOGIN_ENDPOINT
  ) {
    // We try to reconnect automatically otherwise we display an error
    return apiClient
      .request(LOGIN_ENDPOINT)
      .then(() => apiClient.request(error.config))
      .catch((catchedError) =>
        toastMessage('Error.401.title', catchedError.message, 'error', true),
      );
  }

  // Handle common HTTP errors
  else if ([401, 403, 404, 500, 503].includes(error.response.status)) {
    toastMessage(
      `Error.${error.response.status}.title`,
      `Error.${error.response.status}.message`,
      'error',
      true,
    );
  }
  if (error.response.status === 403 && import.meta.env.VITE_EURYDICE_GUICHET === 'destination') {
    router.push({ name: 'userAssociation' });
  }
  throw error;
};

export const setUserFromResponseInterceptor = (response: AxiosResponse | undefined) => {
  const userStore = useUserStore();
  if (response?.headers['authenticated-user']) {
    userStore.setCurrentUser({ username: response.headers['authenticated-user'] });
  }
};
