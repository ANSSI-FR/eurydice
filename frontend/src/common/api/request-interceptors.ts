import { objectKeysToSnakeCase } from '@common/utils/case-functions';
import { type InternalAxiosRequestConfig } from 'axios';

export const camelCaseToSnakeCaseInterceptor = (config: InternalAxiosRequestConfig) => {
  // Convert object keys of the parameters from camelCase to snake_case
  if (config.params) {
    config.params = objectKeysToSnakeCase(config.params);
  }
  // Convert object keys of the payload from camelCase to snake_case
  config.data = objectKeysToSnakeCase(config.data);
  return config;
};
