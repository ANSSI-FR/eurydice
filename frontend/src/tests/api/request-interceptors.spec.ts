import {
  camelCaseToSnakeCaseInterceptor,
  remoteUserHeaderForLoginRoute,
} from '@common/api/request-interceptors';
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

const TEST_CASES_1 = [
  {
    request: { url: '/user/login/', headers: {} },
    expectedTransformedRequest: { url: '/user/login/', headers: { 'X-Remote-User': 'billmurray' } },
  },
  {
    request: { url: '/toto/', headers: {} },
    expectedTransformedRequest: { url: '/toto/', headers: {} },
  },
  {
    request: { url: '/user/login/', headers: { 'X-Remote-User': 'toto', 'Other-Header': 'tata' } },
    expectedTransformedRequest: {
      url: '/user/login/',
      headers: { 'X-Remote-User': 'billmurray', 'Other-Header': 'tata' },
    },
  },
  {
    request: {
      url: '/user/login/',
      headers: { 'X-Remote-User': 'toto', 'Other-Header': 'tata' },
      data: { barFoo: 'barFoo', foo: { fooBar: 'bar_foo' } },
      params: { fooBar: 'fooBar', expand: ['toto', 'tataToto'] },
    },
    expectedTransformedRequest: {
      url: '/user/login/',
      headers: { 'X-Remote-User': 'billmurray', 'Other-Header': 'tata' },
      data: { barFoo: 'barFoo', foo: { fooBar: 'bar_foo' } },
      params: { fooBar: 'fooBar', expand: ['toto', 'tataToto'] },
    },
  },
];

describe('remote user header on /user/login/ route', () => {
  it.each(TEST_CASES_1)(
    "transforms '$request' into '$expectedTransformedRequest'",
    ({ request, expectedTransformedRequest }) => {
      const transformedRequest = remoteUserHeaderForLoginRoute(
        request as InternalAxiosRequestConfig,
      );
      expect(transformedRequest).toStrictEqual(expectedTransformedRequest);
    },
  );
});
