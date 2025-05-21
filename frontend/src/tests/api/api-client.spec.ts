import apiClient, { initApiClient } from '@common/api/api-client';
import * as requestInterceptor from '@common/api/request-interceptors';
import * as responseInterceptor from '@common/api/response-interceptors';
import { describe, expect, it, vi } from 'vitest';

describe('Api Client', () => {
  it('has response interceptors', () => {
    vi.stubEnv('VITE_USE_USER_REMOTE_INTERCEPTOR', 'true');
    const spyOnInterceptor = vi
      .spyOn(responseInterceptor, 'snakeCaseToCamelCaseInterceptor')
      .mockImplementation(vi.fn());
    const spyOnErrorInterceptor = vi
      .spyOn(responseInterceptor, 'errorInterceptor')
      .mockImplementation(vi.fn());
    const spyOnSetUserInterceptor = vi
      .spyOn(responseInterceptor, 'setUserFromResponseInterceptor')
      .mockImplementation(vi.fn());

    const responseInterceptorHandler = (apiClient.interceptors.response as any).handlers;
    expect(responseInterceptorHandler).toHaveLength(2);

    // Set user interceptor
    expect(responseInterceptorHandler[0].fulfilled).toBeDefined();
    expect(responseInterceptorHandler[0].rejected).toBeDefined();
    responseInterceptorHandler[0].fulfilled();
    expect(spyOnSetUserInterceptor).toBeCalledTimes(1);
    expect(() => responseInterceptorHandler[0].rejected()).toThrow();
    expect(spyOnSetUserInterceptor).toBeCalledTimes(2);

    // Error interceptor
    expect(responseInterceptorHandler[1].fulfilled).toBeDefined();
    expect(responseInterceptorHandler[1].rejected).toBeDefined();
    responseInterceptorHandler[1].fulfilled();
    expect(spyOnInterceptor).toBeCalled();
    expect(spyOnErrorInterceptor).not.toBeCalled();
    responseInterceptorHandler[1].rejected();
    expect(spyOnErrorInterceptor).toBeCalled();
  });

  it('has request interceptors and calls correct functions', () => {
    const spyOnInterceptor = vi
      .spyOn(requestInterceptor, 'camelCaseToSnakeCaseInterceptor')
      .mockImplementation(vi.fn());
    const spyOnRemoteUserInterceptor = vi
      .spyOn(requestInterceptor, 'remoteUserHeaderForLoginRoute')
      .mockImplementation(vi.fn());
    const requestInterceptorHandler = (apiClient.interceptors.request as any).handlers;
    expect(requestInterceptorHandler).toHaveLength(2);

    // The first should be Remote-User interceptor
    expect(requestInterceptorHandler[0].fulfilled).toBeDefined();
    expect(requestInterceptorHandler[0].rejected).toBeUndefined();
    requestInterceptorHandler[0].fulfilled();
    expect(spyOnRemoteUserInterceptor).toBeCalled();

    expect(requestInterceptorHandler[1].fulfilled).toBeDefined();
    expect(requestInterceptorHandler[1].rejected).toBeUndefined();
    requestInterceptorHandler[1].fulfilled();
    expect(spyOnInterceptor).toBeCalled();
  });

  it('does not use Remote-User Header interceptor if it is deactivated', () => {
    vi.stubEnv('VITE_USE_USER_REMOTE_INTERCEPTOR', 'false');
    const apiClientInitialized = initApiClient();
    const spyOnRemoteUserInterceptor = vi
      .spyOn(requestInterceptor, 'remoteUserHeaderForLoginRoute')
      .mockImplementation(vi.fn());
    vi.spyOn(requestInterceptor, 'camelCaseToSnakeCaseInterceptor').mockImplementation(vi.fn());
    const requestInterceptorHandler = (apiClientInitialized.interceptors.request as any).handlers;
    expect(requestInterceptorHandler).toHaveLength(1);

    // The first should be Remote-User interceptor
    expect(requestInterceptorHandler[0].fulfilled).toBeDefined();
    expect(requestInterceptorHandler[0].rejected).toBeUndefined();
    requestInterceptorHandler[0].fulfilled();
    expect(spyOnRemoteUserInterceptor).not.toBeCalled();
  });

  it('configures through env variables', () => {
    expect(apiClient.getUri()).toEqual('testUrl');
    expect(apiClient.defaults.xsrfCookieName).toEqual('test_csrftoken');
    expect(apiClient.defaults.xsrfHeaderName).toEqual('X-CSRFToken-test');
  });

  it('takes default config if no configuration is set in env variables', () => {
    vi.stubEnv('VITE_API_URL', undefined);
    vi.stubEnv('VITE_API_XSRF_COOKIE_NAME', undefined);
    vi.stubEnv('VITE_API_XSRF_HEADER_NAME', undefined);
    const apiClientInitialized = initApiClient();
    expect(apiClientInitialized.getUri()).toEqual('/api/v1');
    expect(apiClientInitialized.defaults.xsrfCookieName).toEqual('eurydice_csrftoken');
    expect(apiClientInitialized.defaults.xsrfHeaderName).toEqual('X-CSRFToken');
  });
});
