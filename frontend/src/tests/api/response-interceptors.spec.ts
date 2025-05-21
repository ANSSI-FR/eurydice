import apiClient from '@common/api/api-client';
import {
  errorInterceptor,
  setUserFromResponseInterceptor,
  snakeCaseToCamelCaseInterceptor,
} from '@common/api/response-interceptors';
import * as toastMessageService from '@common/services/toast-message.service';
import { useUserStore } from '@common/store/user.store';
import { router } from '@destination/router';
import type { AxiosResponse, RawAxiosResponseHeaders } from 'axios';
import { afterEach, describe, expect, it, vi } from 'vitest';

const TEST_CASES = [
  {
    response: undefined,
    expectedAlertTitle: 'Error.Network.title',
    expectedAlertMessage: undefined,
    expectAlertToHaveBeenCalled: true,
  },
  {
    response: { status: 404 },
    expectedAlertTitle: 'Error.404.title',
    expectedAlertMessage: 'Error.404.message',
    expectAlertToHaveBeenCalled: true,
  },
  {
    response: { status: 500 },
    expectedAlertTitle: 'Error.500.title',
    expectedAlertMessage: 'Error.500.message',
    expectAlertToHaveBeenCalled: true,
  },
  {
    response: { status: 503 },
    expectedAlertTitle: 'Error.503.title',
    expectedAlertMessage: 'Error.503.message',
    expectAlertToHaveBeenCalled: true,
  },
  {
    response: { status: 400 },
    expectedAlertTitle: '',
    expectedAlertMessage: 'Cette erreur ne passera pas par toastMessage',
    expectAlertToHaveBeenCalled: false,
  },
  {
    response: { status: 401, config: { url: '/user/login/' } },
    expectedAlertTitle: 'Error.401.title',
    expectedAlertMessage: 'Error.401.message',
    expectAlertToHaveBeenCalled: true,
  },
];

describe('Error response interceptor', () => {
  it.each(TEST_CASES)(
    "raises '$expectedAlertMessage' when given response '$response'",
    ({ response, expectedAlertTitle, expectedAlertMessage, expectAlertToHaveBeenCalled }) => {
      const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());

      // We expect the interceptor to pass the exception even after treating it
      expect(() => errorInterceptor({ response })).toThrow();
      if (expectAlertToHaveBeenCalled) {
        expect(spyOnToast).toHaveBeenCalledWith(
          expectedAlertTitle,
          expectedAlertMessage,
          'error',
          true,
        );
      } else {
        expect(spyOnToast).not.toHaveBeenCalled();
      }
    },
  );
  it('redirects to /user-association on 403 error', () => {
    vi.stubEnv('VITE_EURYDICE_GUICHET', 'destination');
    const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());
    const spyOnRouterPush = vi.spyOn(router, 'push').mockImplementation(vi.fn());

    expect(spyOnRouterPush).not.toBeCalled();

    const response = { status: 403 };

    // We expect the interceptor to pass the exception even after treating it
    expect(() => errorInterceptor({ response })).toThrow();

    expect(spyOnToast).toHaveBeenCalledWith('Error.403.title', 'Error.403.message', 'error', true);
    expect(spyOnRouterPush).toHaveBeenCalledWith({ name: 'userAssociation' });
  });

  it('correctly handles errors without an HTTP response', () => {
    const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());
    const axiosError = {
      message: 'Evil breaks its chains and runs through the world like a mad dog.',
    };

    expect(() => errorInterceptor(axiosError)).toThrow();
    expect(spyOnToast).toHaveBeenCalledWith(
      'Error.Network.title',
      axiosError.message,
      'error',
      true,
    );
  });

  it('correctly gets session cookie after a 401 error', async () => {
    const axiosError = {
      response: { status: 401 },
      config: 'Evil breaks its chains and runs through the world like a mad dog.',
    };

    const fullfilledResponse = "I'm Worried I Fucked With Your Gender Expression";
    apiClient.request = vi.fn().mockResolvedValue(fullfilledResponse);
    const requestRetryData = await errorInterceptor(axiosError);
    // expect original request to be fullfilled after retry
    expect(requestRetryData).toBe(fullfilledResponse);
    expect(apiClient.request).toHaveBeenCalledTimes(2);
    // expect initial login attempt
    expect(apiClient.request).toHaveBeenNthCalledWith(1, '/user/login/');
    // expect subsequent retry of original request
    expect(apiClient.request).toHaveBeenNthCalledWith(2, axiosError.config);
  });

  it('notifies errors when getting session cookie after a 401 error', async () => {
    const axiosError = {
      response: { status: 401 },
      config: 'Evil breaks its chains and runs through the world like a mad dog.',
    };
    const rejectedResponse = {
      message: "That's Not A Kid, That's My Business Partner",
    };
    const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());

    apiClient.request = vi.fn().mockRejectedValue(rejectedResponse);

    await errorInterceptor(axiosError);
    // expect a login attempt
    expect(apiClient.request).toHaveBeenCalledTimes(1);
    expect(apiClient.request).toHaveBeenCalledWith('/user/login/');
    // expect returned error to have been logged
    expect(spyOnToast).toHaveBeenCalledWith(
      'Error.401.title',
      rejectedResponse.message,
      'error',
      true,
    );
  });
});

const TEST_CASES_1 = [
  { headers: { 'authenticated-user': 'billmurray' }, expectedUser: { username: 'billmurray' } },
  { headers: {}, expectedUser: undefined },
  { headers: { 'authenticated-user': '' }, expectedUser: undefined },
];

describe('User Header interceptor', () => {
  afterEach(() => {
    useUserStore().$reset();
  });
  it.each(TEST_CASES_1)(
    "updates store with username '$expectedUser' from successful response header '$headers'",
    ({ headers, expectedUser }) => {
      const axiosResponse = {
        headers,
      };
      //Verify it sets username in store from response
      setUserFromResponseInterceptor(axiosResponse as AxiosResponse);
      expect(useUserStore().getCurrentUser).toEqual(expectedUser);
    },
  );

  it('updates store with username from error response header', () => {
    const username = 'billmurray';
    const axiosError = {
      response: {
        headers: { 'authenticated-user': username } as RawAxiosResponseHeaders,
      },
      message: 'MSG_123456789', // expect(...).toThrow(x) uses `x.message` for equality
    };
    //Verify it sets username in store from error
    setUserFromResponseInterceptor(axiosError.response as AxiosResponse);
    expect(useUserStore().getCurrentUser).toEqual({ username: username });
  });

  it('skips updating store with username from response when no response', () => {
    const username = 'billmurray';
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: username });
    // Verify it doesn't set the username in store
    setUserFromResponseInterceptor(undefined);
    expect(userStore.getCurrentUser).toEqual({ username: username });
  });
});

const TEST_CASES_2 = [
  {
    response: { data: { barFoo: 'barFoo', foo: { bar: 'barFoo' } } },
    expectedTransformedResponse: { barFoo: 'barFoo', foo: { bar: 'barFoo' } },
  },
];

describe('camelCase to snake_case interceptor', () => {
  it.each(TEST_CASES_2)(
    "transforms '$response' into '$expectedTransformedResponse'",
    ({ response, expectedTransformedResponse }) => {
      const transformedResponse = snakeCaseToCamelCaseInterceptor(response as AxiosResponse);
      expect(transformedResponse).toStrictEqual(expectedTransformedResponse);
    },
  );
});
