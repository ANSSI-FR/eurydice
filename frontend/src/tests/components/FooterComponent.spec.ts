import FooterComponent from '@common/components/FooterComponent.vue';
import { useServerMetadataStore } from '@common/store/server-metadata.store';
import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

describe.concurrent('Footer Component', () => {
  it('Contains 2 items and a scroll button', () => {
    const wrapper = mount(FooterComponent);
    const menubar = wrapper.find('[data-testid="Footer"]');
    expect(menubar.findAll('button').length).toBe(2);

    const scrollButton = wrapper.find('[data-testid="Footer.scrollButton"]');
    expect(scrollButton.exists()).toBeTruthy();
    expect(scrollButton.isVisible()).toBeFalsy();
  });
  it('Documentation link is working', async () => {
    const wrapper = mount(FooterComponent);
    expect(wrapper.findAll('a').length).toBe(1);
    const documentationLink = wrapper.find("[data-testid='footer-api-docs']");
    expect(documentationLink.text()).toContain("Documentation de l'API");
    expect(documentationLink.attributes('href')).toBe(
      import.meta.env.VITE_API_DOCS_URL ?? '/api/docs',
    );
  });
  it('Contact button is working', async () => {
    const wrapper = mount(FooterComponent, { global: { stubs: { teleport: true } } });
    const contactLink = wrapper.find("[data-testid='footer-contact']");
    expect(wrapper.find("[data-testid='footer-contact-dialog']").exists()).toBe(false);
    expect(contactLink.text()).toContain('Contact');
    await contactLink.trigger('click');
    const contactDialog = wrapper.get("[data-testid='footer-contact-dialog']");
    expect(contactDialog.isVisible()).toBe(true);
  });
  it('Contact Dialog is closing correctly', async () => {
    const wrapper = mount(FooterComponent, { global: { stubs: { teleport: true } } });
    await wrapper.find("[data-testid='footer-contact']").trigger('click');
    const dialogCloseBtn = wrapper.get("[data-testid='footer-contact-dialog']").find('button');
    expect(dialogCloseBtn.exists()).toBe(true);
    await dialogCloseBtn.trigger('click');
    expect(wrapper.find("[data-testid='footer-contact-dialog']").exists()).toBe(false);
  });
  it('Contact Text is set according to request', async () => {
    const serverMetadataStore = useServerMetadataStore();
    serverMetadataStore.setServerMetadata({
      contact: 'test',
      badgeColor: 'blue',
      badgeContent: 'TEST',
    });
    const metadataStore = useServerMetadataStore();
    await metadataStore.fetchServerMetadata();

    const wrapper = mount(FooterComponent, { global: { stubs: { teleport: true } } });
    await wrapper.vm.$nextTick();
    await wrapper.find("[data-testid='footer-contact']").trigger('click');
    const contactDialog = wrapper.get("[data-testid='footer-contact-dialog']");
    expect(contactDialog.text()).toContain('test');
  });

  it('Shows scroll button when scrolling', async () => {
    //@ts-expect-error Scroll function is supposed to take number apparently... But it is not our case...
    const spyOnScroll = vi.spyOn(window, 'scroll').mockImplementation(({ top }) => {
      window.scrollY = top;
    });
    window.scrollY = 500;
    const wrapper = mount(FooterComponent);
    const scrollButton = wrapper.find('[data-testid="ScrollToTopButton"]');
    expect(scrollButton.exists()).toBeTruthy();
    expect(scrollButton.isVisible()).toBeFalsy();
    await window.dispatchEvent(new CustomEvent('scroll'));
    expect(scrollButton.isVisible()).toBeTruthy();
    await scrollButton.trigger('click');
    await wrapper.vm.$nextTick();
    expect(spyOnScroll).toBeCalledWith({ top: 0, behavior: 'smooth' });
    expect(window.scrollY).toEqual(0);
  });
});
