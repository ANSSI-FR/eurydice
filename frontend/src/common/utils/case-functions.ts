import _ from 'lodash';

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
