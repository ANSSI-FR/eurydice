import {
  objectKeysToCamelCase,
  objectKeysToSnakeCase,
} from "@common/utils/convert-object-keys";

const TEST_CASES = [
  [19, 19],
  ["foo", "foo"],
  [{}, {}],
  [[], []],
  [null, null],
  [undefined, undefined],
  [
    ["fooBar", "baz_qux"],
    ["fooBar", "baz_qux"],
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
  [
    { fooBar: { bazQux: { abcXyz: 3 } } },
    { foo_bar: { baz_qux: { abc_xyz: 3 } } },
  ],
];

describe("Convert object keys", () => {
  it.each(TEST_CASES)("should match", (a, b) => {
    expect(objectKeysToSnakeCase(a)).toStrictEqual(b);
    expect(objectKeysToCamelCase(b)).toStrictEqual(a);
  });
});
