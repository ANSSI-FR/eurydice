import { useUserStore } from '@common/store/user.store';
import Error404View from '@common/views/Error404View.vue';
import { router as destinationRouter } from '@destination/router';
import { router as originRouter } from '@origin/router';
import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

describe('Display 404 error', () => {
  it.each([
    { name: 'origin', router: originRouter },
    { name: 'destination', router: destinationRouter },
  ])('Displays a text describing the error and redirect to home of $name', (router) => {
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });
    // We mount PageError404 with router
    const wrapper = mount(Error404View, {
      global: {
        plugins: [router.router],
      },
    });
    // We expect an error message to appear
    expect(wrapper.text()).toContain("Erreur 404 - Cette page n'existe pas");
    // We expect the link to redirect to home
    const returnLink = wrapper.find('[data-testid="PageError404.returnHomeLink"]');
    expect(returnLink.html()).toContain("Retour à la page d'accueil");
    expect(returnLink.attributes('href')).toEqual('/');
  });
});
