import { bytesToString } from '@common/utils/bytes-functions';

import { describe, expect, it } from 'vitest';

const TEST_CASES = [
  {
    numberOfBytes: 0,
    string: '0 octets',
  },
  {
    numberOfBytes: 1610612736,
    string: '1.5 Gio',
  },
  {
    numberOfBytes: 1649267441664,
    string: '1.5 Tio',
  },
  {
    numberOfBytes: 1323923669,
    string: '1.23 Gio',
  },
];

const TEST_CASES_1 = [
  {
    numberOfBytes: 0,
    string: '0 octets',
  },
  {
    numberOfBytes: 1610612736,
    string: '2 Gio',
  },
  {
    numberOfBytes: 1649267441664,
    string: '2 Tio',
  },
  {
    numberOfBytes: 1323923669,
    string: '1 Gio',
  },
];
describe('Bytes functions', () => {
  it.each(TEST_CASES)('converts $numberOfBytes into $string', ({ numberOfBytes, string }) => {
    expect(bytesToString(numberOfBytes)).toEqual(string);
  });

  it.each(TEST_CASES_1)('rounds decimal $numberOfBytes to $string', ({ numberOfBytes, string }) => {
    expect(bytesToString(numberOfBytes, -5)).toEqual(string);
  });
});
