import _ from 'lodash';

/** Convert 'expand' param value from camelCase to snake_case */
export const expandToSnakeCase = (param: string | [string]) => {
  if (Array.isArray(param)) {
    return param.map(_.snakeCase);
  }
  return _.snakeCase(param);
};

export const objectKeysTo = (obj: any, caseFunc: (key: string) => string): any => {
  if (Array.isArray(obj)) {
    return obj.map((value) => objectKeysTo(value, caseFunc));
  }
  if (_.isPlainObject(obj)) {
    return _.reduce(
      obj,
      (acc: any, value: any, key: string) => {
        acc[caseFunc(key)] = objectKeysTo(value, caseFunc);
        return acc;
      },
      {},
    );
  }
  return obj;
};

export const objectKeysToCamelCase = (obj: any) => {
  return objectKeysTo(obj, _.camelCase);
};

export const objectKeysToSnakeCase = (obj: any) => {
  return objectKeysTo(obj, _.snakeCase);
};
