import {
  errorInterceptor,
  setUserFromResponseInterceptor,
  snakeCaseToCamelCaseInterceptor,
} from '@common/api/response-interceptors';
import * as toastMessageService from '@common/services/toast-message.service';
import { useUserStore } from '@common/store/user.store';
import { router as destinationRouter } from '@destination/router';
import { router as originRouter } from '@origin/router';
import { flushPromises } from '@vue/test-utils';
import type { AxiosResponse, RawAxiosResponseHeaders } from 'axios';
import { afterEach, describe, expect, it, vi } from 'vitest';

const TEST_CASES = [
  {
    response: undefined,
    expectedAlertTitle: 'Error.Network.title',
    expectedAlertMessage: 'Error.Network.message',
    expectAlertToHaveBeenCalled: true,
    autoExpires: false,
    paramsMessage: { paramsMessage: { errorMessage: undefined } },
  },
  {
    response: { status: 404 },
    expectedAlertTitle: 'Error.404.title',
    expectedAlertMessage: 'Error.404.message',
    expectAlertToHaveBeenCalled: true,
    autoExpires: true,
  },
  {
    response: { status: 500 },
    expectedAlertTitle: 'Error.500.title',
    expectedAlertMessage: 'Error.500.message',
    expectAlertToHaveBeenCalled: true,
    autoExpires: true,
  },
  {
    response: { status: 503 },
    expectedAlertTitle: 'Error.503.title',
    expectedAlertMessage: 'Error.503.message',
    expectAlertToHaveBeenCalled: true,
    autoExpires: true,
  },
  {
    response: { status: 400 },
    expectedAlertTitle: '',
    expectedAlertMessage: 'Cette erreur ne passera pas par toastMessage',
    expectAlertToHaveBeenCalled: false,
    autoExpires: true,
  },
];

describe('Error response interceptor', () => {
  it.each(TEST_CASES)(
    "raises '$expectedAlertMessage' when given response '$response'",
    ({
      response,
      expectedAlertTitle,
      expectedAlertMessage,
      expectAlertToHaveBeenCalled,
      autoExpires,
      paramsMessage,
    }) => {
      const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());
      // We expect the interceptor to pass the exception even after treating it
      expect(() => errorInterceptor({ response })).toThrow();
      if (expectAlertToHaveBeenCalled) {
        if (paramsMessage) {
          expect(spyOnToast).toHaveBeenCalledWith(
            expectedAlertTitle,
            expectedAlertMessage,
            'error',
            autoExpires,
            paramsMessage,
          );
        } else {
          expect(spyOnToast).toHaveBeenCalledWith(
            expectedAlertTitle,
            expectedAlertMessage,
            'error',
            autoExpires,
          );
        }
      } else {
        expect(spyOnToast).not.toHaveBeenCalled();
      }
    },
  );
  it('redirects to /user-association on 403 error', () => {
    vi.stubEnv('VITE_EURYDICE_GUICHET', 'destination');
    const spyOnRouterPush = vi.spyOn(destinationRouter, 'push').mockImplementation(vi.fn());
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });
    expect(spyOnRouterPush).not.toBeCalled();

    const response = { status: 403 };

    // We expect the interceptor to pass the exception even after treating it
    expect(() => errorInterceptor({ response })).toThrow();

    expect(spyOnRouterPush).toHaveBeenCalledWith({ name: 'userAssociation' });
  });

  it('correctly handles errors without an HTTP response', () => {
    const spyOnToast = vi.spyOn(toastMessageService, 'toastMessage').mockImplementation(vi.fn());
    const axiosError = {
      message: 'Network error from server',
    };

    expect(() => errorInterceptor(axiosError)).toThrow();
    expect(spyOnToast).toHaveBeenCalledWith(
      'Error.Network.title',
      'Error.Network.message',
      'error',
      false,
      {
        paramsMessage: {
          errorMessage: axiosError.message,
        },
      },
    );
  });

  it.each([
    { name: 'origin', router: originRouter },
    { name: 'destination', router: destinationRouter },
  ])('redirects to login page after a 401 for $name', async ({ name, router }) => {
    vi.stubEnv('VITE_EURYDICE_GUICHET', name);
    const spyOnRouterPush = vi.spyOn(router, 'push').mockImplementation(vi.fn());

    const axiosError = {
      response: { status: 401, config: { url: '/' } },
      config: 'Error 401 text',
    };

    await errorInterceptor(axiosError);

    await flushPromises();

    expect(spyOnRouterPush).toHaveBeenCalledWith({ name: 'login' });
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
