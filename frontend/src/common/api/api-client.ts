import { camelCaseToSnakeCaseInterceptor } from '@common/api/request-interceptors';
import {
  errorInterceptor,
  setUserFromResponseInterceptor,
  snakeCaseToCamelCaseInterceptor,
} from '@common/api/response-interceptors';
import axios from 'axios';

// Create an apiClient instance
export const initApiClient = () => {
  const API_URL = import.meta.env.VITE_API_URL ?? '/api/v1';
  const XSRF_COOKIE_NAME = import.meta.env.VITE_API_XSRF_COOKIE_NAME ?? 'eurydice_csrftoken';
  const XSRF_HEADER_NAME = import.meta.env.VITE_API_XSRF_HEADER_NAME ?? 'X-CSRFToken';

  const apiClient = axios.create({
    baseURL: API_URL,
    xsrfCookieName: XSRF_COOKIE_NAME,
    xsrfHeaderName: XSRF_HEADER_NAME,
    headers: {
      Accept: 'application/json',
    },
    timeout: Number(import.meta.env.VITE_API_TIMEOUT ?? '10000'),
  });

  // Request interceptor : converts camelCase request to snake_case
  apiClient.interceptors.request.use((config) => camelCaseToSnakeCaseInterceptor(config));

  // Response Interceptor : Set user from header
  apiClient.interceptors.response.use(
    (response) => {
      setUserFromResponseInterceptor(response);
      return response;
    },
    (error) => {
      setUserFromResponseInterceptor(error?.response);
      throw error;
    },
  );

  // Response Interceptor : Transforms snake_case to camelCase and intercepts errors
  apiClient.interceptors.response.use(
    (value) => snakeCaseToCamelCaseInterceptor(value),
    (error) => errorInterceptor(error),
  );

  return apiClient;
};

export const apiClient = initApiClient();
export default apiClient;
