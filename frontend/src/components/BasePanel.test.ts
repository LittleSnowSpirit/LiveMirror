import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BasePanel from './BasePanel.vue';

describe('BasePanel.vue', () => {
  it('renders with title prop', () => {
    const wrapper = mount(BasePanel, {
      props: { title: 'Test Title' },
    });
    expect(wrapper.text()).toContain('Test Title');
    expect(wrapper.find('.panel-title').exists()).toBe(true);
  });

  it('renders with subtitle prop', () => {
    const wrapper = mount(BasePanel, {
      props: { title: 'Title', subtitle: 'Subtitle text' },
    });
    expect(wrapper.text()).toContain('Subtitle text');
    expect(wrapper.find('.panel-subtitle').exists()).toBe(true);
  });

  it('renders default slot content', () => {
    const wrapper = mount(BasePanel, {
      slots: { default: '<p>Panel body</p>' },
    });
    expect(wrapper.text()).toContain('Panel body');
  });

  it('renders header slot', () => {
    const wrapper = mount(BasePanel, {
      slots: { header: '<div class="custom-header">Custom</div>' },
    });
    expect(wrapper.find('.custom-header').exists()).toBe(true);
  });

  it('renders header-right slot', () => {
    const wrapper = mount(BasePanel, {
      props: { title: 'Title' },
      slots: { 'header-right': '<button>Action</button>' },
    });
    expect(wrapper.find('button').exists()).toBe(true);
  });

  it('applies no-padding class when noPadding is true', () => {
    const wrapper = mount(BasePanel, {
      props: { noPadding: true },
    });
    expect(wrapper.find('.no-padding').exists()).toBe(true);
  });

  it('does not show header when no title or header slot', () => {
    const wrapper = mount(BasePanel, {
      slots: { default: '<p>Content</p>' },
    });
    expect(wrapper.find('.panel-header').exists()).toBe(false);
  });
});
