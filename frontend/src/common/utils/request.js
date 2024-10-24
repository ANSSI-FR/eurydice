import { baseURL } from "@common/settings";
import store from "@common/store";
import {
  objectKeysToCamelCase,
  objectKeysToSnakeCase,
} from "@common/utils/convert-object-keys";
import axios from "axios";
import _ from "lodash";
import Vue from "vue";

const ERROR_MESSAGES = {
  401: "Authentification nécessaire.",
  404: "Cette ressource n'existe pas.",
  500: "Une erreur serveur est survenue.",
};

// create an axios instance
export const service = axios.create({
  baseURL, // url = base url + request url
  // withCredentials: true, // send cookies when cross-domain requests
  xsrfCookieName: "eurydice_csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

/** Convert 'expand' param value from camelCase to snake_case */
function expandParamValueToSnakeCase(param) {
  if (Array.isArray(param)) {
    return param.map(_.snakeCase);
  }
  return _.snakeCase(param);
}

let moduleDevelopmentAuthenticationInterceptorIndex;
if (process.env.NODE_ENV === "development") {
  moduleDevelopmentAuthenticationInterceptorIndex =
    service.interceptors.request.use((config) => {
      /* eslint-disable no-param-reassign */
      if (config.url === "/user/login/") {
        config.headers["X-Remote-User"] = "billmurray";
      }
      /* eslint-enable no-param-reassign */
      return config;
    });
}

export const developmentAuthenticationInterceptorIndex =
  moduleDevelopmentAuthenticationInterceptorIndex;

// request interceptor
export const caseRequestModifierInterceptorIndex =
  service.interceptors.request.use((config) => {
    /* eslint-disable no-param-reassign */
    // Convert object keys of the parameters from camelCase to snake_case
    if (config.params) {
      config.params = objectKeysToSnakeCase(config.params);

      if (config.params.expand) {
        config.params.expand = expandParamValueToSnakeCase(
          config.params.expand
        );
      }
    }

    // Convert object keys of the payload from camelCase to snake_case
    config.data = objectKeysToSnakeCase(config.data);
    /* eslint-enable no-param-reassign */

    return config;
  });

const setUsernameFromResponse = (response) => {
  store.commit("setUsername", response.headers["authenticated-user"] || null);
};

// Sets the username in the store from the response headers
export const setUsernameResponseInterceptorIndex =
  service.interceptors.response.use(
    (response) => {
      setUsernameFromResponse(response);
      return response;
    },
    (error) => {
      if (error.response) {
        setUsernameFromResponse(error.response);
      }
      throw error;
    }
  );

const hasBasicAuthHeader = (response) => {
  const headerName = "www-authenticate";
  const headerValue = "Basic";
  const headers = response?.headers;
  if (headers === undefined) {
    return false;
  }
  return headers[headerName]?.includes(headerValue) === true;
};

export function handleResponseError(error) {
  // Handle network errors
  if (error.response === undefined) {
    if (!(error instanceof axios.Cancel)) {
      Vue.prototype.$alert(error.message, "error", 10000);
    }
  }
  // handle missing session cookie
  else if (
    error.response.status === 401 &&
    !hasBasicAuthHeader(error.response)
  ) {
    const LOGIN_ENDPOINT = "/user/login/";
    if (error.response.config?.url === LOGIN_ENDPOINT) {
      Vue.prototype.$alert("Authentication error", "error", 10000);
    } else {
      return service
        .request(LOGIN_ENDPOINT)
        .then(() => service.request(error.config))
        .catch((authenticationError) =>
          Vue.prototype.$alert(authenticationError.message, "error", 10000)
        );
    }
  }
  // handle common HTTP errors
  else if (error.response.status in ERROR_MESSAGES) {
    Vue.prototype.$alert(ERROR_MESSAGES[error.response.status], "error", 10000);
  }
  throw error;
}

// response interceptor
export const responseInterceptorIndex = service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
   */
  (response) => {
    // Convert object keys of the payload from snake_case to camelCase
    return objectKeysToCamelCase(response.data);
  },
  handleResponseError
);

export default service;
