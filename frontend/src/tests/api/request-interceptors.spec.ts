import { camelCaseToSnakeCaseInterceptor } from '@common/api/request-interceptors';
import type { InternalAxiosRequestConfig } from 'axios';
import { describe, expect, it } from 'vitest';

const TEST_CASES = [
  {
    request: {
      data: { barFoo: 'barFoo', foo: { bar: 'bar_foo' } },
      params: { fooBar: 'fooBar' },
      headers: {},
    },
    expectedTransformedRequest: {
      data: { bar_foo: 'barFoo', foo: { bar: 'bar_foo' } },
      params: { foo_bar: 'fooBar' },
      headers: {},
    },
  },
  {
    request: {
      data: { barFoo: 'barFoo', foo: { fooBar: 'bar_foo' } },
      params: { fooBar: 'fooBar', expand: ['toto', 'tataToto'] },
      headers: { headerTest: 'test' },
    },
    expectedTransformedRequest: {
      data: { bar_foo: 'barFoo', foo: { foo_bar: 'bar_foo' } },
      params: { foo_bar: 'fooBar', expand: ['toto', 'tata_toto'] },
      headers: { headerTest: 'test' },
    },
  },
];

describe('camelCase to snake_case request interceptor', () => {
  it.each(TEST_CASES)(
    "transforms '$request' into '$expectedTransformedRequest'",
    ({ request, expectedTransformedRequest }) => {
      const transformedRequest = camelCaseToSnakeCaseInterceptor(
        request as InternalAxiosRequestConfig,
      );
      expect(transformedRequest).toStrictEqual(expectedTransformedRequest);
    },
  );
});
