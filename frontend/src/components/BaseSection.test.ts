import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseSection from './BaseSection.vue';

describe('BaseSection.vue', () => {
  it('renders with title prop', () => {
    const wrapper = mount(BaseSection, {
      props: { title: 'Section Title' },
    });
    expect(wrapper.text()).toContain('Section Title');
    expect(wrapper.find('.section-title').exists()).toBe(true);
  });

  it('renders with kicker prop', () => {
    const wrapper = mount(BaseSection, {
      props: { kicker: 'Eyebrow text' },
    });
    expect(wrapper.text()).toContain('Eyebrow text');
    expect(wrapper.find('.kicker').exists()).toBe(true);
  });

  it('renders both kicker and title', () => {
    const wrapper = mount(BaseSection, {
      props: { title: 'Title', kicker: 'Kicker' },
    });
    expect(wrapper.find('.kicker').exists()).toBe(true);
    expect(wrapper.find('.section-title').exists()).toBe(true);
  });

  it('renders slot content', () => {
    const wrapper = mount(BaseSection, {
      slots: { default: '<p>Section body</p>' },
    });
    expect(wrapper.text()).toContain('Section body');
  });

  it('does not render kicker when not provided', () => {
    const wrapper = mount(BaseSection, {
      props: { title: 'Title' },
    });
    expect(wrapper.find('.kicker').exists()).toBe(false);
  });

  it('does not render title when not provided', () => {
    const wrapper = mount(BaseSection, {
      props: { kicker: 'Kicker' },
    });
    expect(wrapper.find('.section-title').exists()).toBe(false);
  });
});
