import _ from "lodash";

function objectKeysTo(obj, caseFunc) {
  if (Array.isArray(obj)) {
    return obj.map((value) => objectKeysTo(value, caseFunc));
  }
  if (_.isPlainObject(obj)) {
    return _.reduce(
      obj,
      (acc, value, key) => {
        acc[caseFunc(key)] = objectKeysTo(value, caseFunc);
        return acc;
      },
      {}
    );
  }
  return obj;
}

export function objectKeysToCamelCase(obj) {
  return objectKeysTo(obj, _.camelCase);
}

export function objectKeysToSnakeCase(obj) {
  return objectKeysTo(obj, _.snakeCase);
}
