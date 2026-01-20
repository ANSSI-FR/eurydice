import { toastMessage } from '@common/services/toast-message.service';
import { useUserStore } from '@common/store/user.store';
import { objectKeysToCamelCase } from '@common/utils/case-functions';
import { router as destinationRouter } from '@destination/router';
import { router as originRouter } from '@origin/router';
import type { AxiosResponse } from 'axios';
import axios from 'axios';

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

export const errorInterceptor = (error: any): any => {
  const userStore = useUserStore();
  // Do not mark canceled transferables as error
  if (error.response === undefined && !(error instanceof axios.Cancel)) {
    // We stop all autoRefreshed calls if a network error happens
    toastMessage('Error.Network.title', 'Error.Network.message', 'error', false, {
      paramsMessage: { errorMessage: error.message },
    });
  }

  // Handle missing session cookie if no basic auth header or not contacting login_endpoint we redirect to login page
  else if (
    error.response.status === 401 &&
    !hasBasicAuthHeader(error.response) &&
    !error.response.config?.url.startsWith('/user/login')
  ) {
    if (import.meta.env.VITE_EURYDICE_GUICHET === 'destination') {
      destinationRouter.push({ name: 'login' });
    } else {
      originRouter.push({ name: 'login' });
    }
    return;
  }

  // Handle user association token not set in destination
  else if (
    userStore.isUserKnown &&
    error.response.status === 403 &&
    import.meta.env.VITE_EURYDICE_GUICHET === 'destination'
  ) {
    destinationRouter.push({ name: 'userAssociation' });
  }

  // Handle common HTTP errors
  else if ([404, 403, 500, 503].includes(error.response.status)) {
    toastMessage(
      `Error.${error.response.status}.title`,
      `Error.${error.response.status}.message`,
      'error',
      true,
    );
  }
  throw error;
};

export const setUserFromResponseInterceptor = (response: AxiosResponse | undefined) => {
  const userStore = useUserStore();
  if (response?.headers['authenticated-user']) {
    userStore.setCurrentUser({ username: response.headers['authenticated-user'] });
  }
};
