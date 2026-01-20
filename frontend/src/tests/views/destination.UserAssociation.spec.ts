import apiClient from '@common/api/api-client';
import { useUserStore } from '@common/store/user.store';
import { router } from '@destination/router';
import UserAssociation from '@destination/views/UserAssociation.vue';
import { flushPromises, mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe('Main View Origin', () => {
  it('Contains the Token textarea, its messages and buttons', () => {
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });
    // We mount origin MainView without content
    const wrapper = mount(UserAssociation, {
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.find('[data-testid="TokenTextArea"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="TokenSuccessMsg"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="AssociationBtn"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="ContinueBtn"]').exists()).toBe(false);
  });
  it.each([
    { input: '', errorMsg: 'Veuillez saisir le token.' },
    { input: 'test', errorMsg: "Le jeton doit être composé d'exactement 18 mots." },
  ])('Shows errors when token is not in correct format before sending', async (item) => {
    vi.stubEnv('VITE_TOKEN_WORD_COUNT', '18');
    const wrapper = mount(UserAssociation, {
      global: {
        plugins: [router],
      },
    });
    const tokenArea = wrapper.get('[data-testid="TokenTextArea"]');
    tokenArea.setValue(item.input);
    await tokenArea.trigger('input');
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').text()).toBe(item.errorMsg);
  });
  it('Shows success message when sent token is correct', async () => {
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });
    const mockFunction = async () => Promise.resolve(new Response(null, { status: 203 }));

    const spyOnPostAssociationToken = vi.spyOn(apiClient, 'post').mockImplementation(mockFunction);
    expect(spyOnPostAssociationToken).not.toBeCalled();
    const wrapper = mount(UserAssociation, {
      global: {
        plugins: [router],
      },
    });
    const tokenArea = wrapper.get('[data-testid="TokenTextArea"]');
    tokenArea.setValue('un 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 fin');
    await tokenArea.trigger('input');
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(false);

    const tokenForm = wrapper.get('[data-testid="TokenForm"]');
    tokenForm.trigger('submit');
    await flushPromises();

    expect(spyOnPostAssociationToken).toBeCalled();
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(false);

    const successMsg = wrapper.find('[data-testid="TokenSuccessMsg"]');
    expect(successMsg.exists()).toBe(true);
    expect(successMsg.text()).toBe(
      'Votre compte est maintenant associé. Veuillez cliquer pour continuer vers la page principale.',
    );
    expect(wrapper.find('[data-testid="ContinueBtn"]').exists()).toBe(true);
  });
  it('Shows success message when sent token is correct but user is already connected', async () => {
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });
    const mockFunction = async () =>
      Promise.reject(Object.assign(new Error('Conflict Error'), { status: 409 }));

    const spyOnPostAssociationToken = vi.spyOn(apiClient, 'post').mockImplementation(mockFunction);
    expect(spyOnPostAssociationToken).not.toBeCalled();
    const wrapper = mount(UserAssociation, {
      global: {
        plugins: [router],
      },
    });
    const tokenArea = wrapper.get('[data-testid="TokenTextArea"]');
    tokenArea.setValue('un 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 fin');
    await tokenArea.trigger('input');
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(false);

    const tokenForm = wrapper.get('[data-testid="TokenForm"]');
    tokenForm.trigger('submit');
    await flushPromises();

    expect(spyOnPostAssociationToken).toBeCalled();
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(false);

    const successMsg = wrapper.find('[data-testid="TokenSuccessMsg"]');
    expect(successMsg.exists()).toBe(true);
    expect(successMsg.text()).toBe(
      "L'utilisateur est déjà associé avec le guichet origine, cliquez pour continuer vers la page principale.",
    );
    expect(wrapper.find('[data-testid="ContinueBtn"]').exists()).toBe(true);
  });
  it('Shows errors when sent token is incorrect', async () => {
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });
    const mockFunction = async () =>
      Promise.reject(Object.assign(new Error('Error'), { status: 400 }));

    const spyOnPostAssociationToken = vi.spyOn(apiClient, 'post').mockImplementation(mockFunction);
    expect(spyOnPostAssociationToken).not.toBeCalled();
    const wrapper = mount(UserAssociation, {
      global: {
        plugins: [router],
      },
    });
    const tokenArea = wrapper.get('[data-testid="TokenTextArea"]');
    tokenArea.setValue('un 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 fin');
    await tokenArea.trigger('input');
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(false);

    const tokenForm = wrapper.get('[data-testid="TokenForm"]');
    tokenForm.trigger('submit');
    await flushPromises();

    expect(spyOnPostAssociationToken).toBeCalled();
    expect(wrapper.find('[data-testid="TokenSuccessMsg"]').exists()).toBe(false);
    const errorMsg = wrapper.find('[data-testid="TokenErrorMsg"]');
    expect(errorMsg.exists()).toBe(true);
    expect(errorMsg.text()).toBe('Le token est incorrect ou a expiré.');
    expect(wrapper.find('[data-testid="ContinueBtn"]').exists()).toBe(false);
  });
  it('Shows errors when sent token returns a server error 500', async () => {
    vi.stubEnv('VITE_TOKEN_WORD_COUNT', '18');
    const userStore = useUserStore();
    userStore.setCurrentUser({ username: 'billmuray' });

    const mockFunction = async () =>
      Promise.reject(Object.assign(new Error('Error'), { status: 500 }));

    const spyOnPostAssociationToken = vi.spyOn(apiClient, 'post').mockImplementation(mockFunction);
    expect(spyOnPostAssociationToken).not.toBeCalled();
    const wrapper = mount(UserAssociation, {
      global: {
        plugins: [router],
      },
    });
    const tokenArea = wrapper.get('[data-testid="TokenTextArea"]');
    tokenArea.setValue('un 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 fin');
    await tokenArea.trigger('input');
    expect(wrapper.find('[data-testid="TokenErrorMsg"]').exists()).toBe(false);

    const tokenForm = wrapper.get('[data-testid="TokenForm"]');
    tokenForm.trigger('submit');
    await flushPromises();

    expect(spyOnPostAssociationToken).toBeCalled();
    expect(wrapper.find('[data-testid="TokenSuccessMsg"]').exists()).toBe(false);
    const errorMsg = wrapper.find('[data-testid="TokenErrorMsg"]');
    expect(errorMsg.exists()).toBe(true);
    expect(errorMsg.text()).toBe('Une erreur serveur est survenue.');
    expect(wrapper.find('[data-testid="ContinueBtn"]').exists()).toBe(false);
  });
});
