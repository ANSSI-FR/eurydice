import { objectKeysToCamelCase, objectKeysToSnakeCase } from '@common/utils/case-functions';
import { describe, expect, it } from 'vitest';

const TEST_CASES: any[] = [
  [19, 19],
  ['foo', 'foo'],
  [{}, {}],
  [[], []],
  [null, null],
  [undefined, undefined],
  [
    ['fooBar', 'baz_qux'],
    ['fooBar', 'baz_qux'],
  ],
  [{ fooBar: 9 }, { foo_bar: 9 }],
  [
    { fooBar: 9, bazQux: 10 },
    { foo_bar: 9, baz_qux: 10 },
  ],
  [[{ fooBar: 9 }], [{ foo_bar: 9 }]],
  [
    [{ fooBar: 9 }, { bazQux: 10 }],
    [{ foo_bar: 9 }, { baz_qux: 10 }],
  ],
  [{ fooBar: { bazQux: 10 } }, { foo_bar: { baz_qux: 10 } }],
  [{ fooBar: [{ bazQux: 10 }] }, { foo_bar: [{ baz_qux: 10 }] }],
  [{ fooBar: { bazQux: { abcXyz: 3 } } }, { foo_bar: { baz_qux: { abc_xyz: 3 } } }],
];

describe('Convert object keys', () => {
  it.each(TEST_CASES)('%s should match %s', (a: any, b: any) => {
    expect(objectKeysToSnakeCase(a)).toStrictEqual(b);
    expect(objectKeysToCamelCase(b)).toStrictEqual(a);
  });
});
