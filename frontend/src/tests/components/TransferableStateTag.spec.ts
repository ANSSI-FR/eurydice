import TransferableStateTag from '@common/components/TransferableStateTag.vue';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

const TEST_CASES = [
  { value: 'ONGOING', expected: 'En cours', shouldExist: true },
  { value: 'SUCCESS', expected: 'Réussi', shouldExist: true },
  { value: 'ERROR', expected: 'Erreur', shouldExist: true },
  { value: 'REMOVED', expected: 'Supprimé', shouldExist: true },
  { value: 'STATUS_NOT_EXISTING', expected: '', shouldExist: false },
];

describe('TransferableStateTag.vue', () => {
  it.each(TEST_CASES)(
    'Displays correctly a TransferableStateTag with value $value',
    ({ value, expected, shouldExist }) => {
      const wrapper = mount(TransferableStateTag, {
        props: {
          //@ts-expect-error value might not be a real tag
          state: value,
          progress: 50,
        },
      });
      const tag = wrapper.find('[data-testid="TransferableStateTag"]');
      expect(tag.exists()).toBe(shouldExist);
      if (shouldExist) {
        expect(tag.isVisible()).toBeTruthy();
        expect(tag.text()).toContain(expected);
      }
    },
  );
});
