import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import StatCard from './StatCard.vue';

describe('StatCard.vue', () => {
  it('renders value and label', () => {
    const wrapper = mount(StatCard, {
      props: { value: '42', label: 'Users' },
    });
    expect(wrapper.find('.stat-value').text()).toBe('42');
    expect(wrapper.find('.stat-label').text()).toBe('Users');
  });

  it('renders numeric value', () => {
    const wrapper = mount(StatCard, {
      props: { value: 128, label: 'Tasks' },
    });
    expect(wrapper.find('.stat-value').text()).toBe('128');
  });

  it('renders icon when provided', () => {
    const wrapper = mount(StatCard, {
      props: { value: '10', label: 'Items', icon: '📊' },
    });
    expect(wrapper.find('.stat-icon').exists()).toBe(true);
    expect(wrapper.find('.stat-icon').text()).toBe('📊');
  });

  it('does not render icon when not provided', () => {
    const wrapper = mount(StatCard, {
      props: { value: '10', label: 'Items' },
    });
    expect(wrapper.find('.stat-icon').exists()).toBe(false);
  });

  it('renders positive trend with up class', () => {
    const wrapper = mount(StatCard, {
      props: { value: '100', label: 'Growth', trend: 15 },
    });
    const trend = wrapper.find('.stat-trend');
    expect(trend.exists()).toBe(true);
    expect(trend.text()).toBe('+15%');
    expect(trend.classes()).toContain('up');
  });

  it('renders negative trend with down class', () => {
    const wrapper = mount(StatCard, {
      props: { value: '80', label: 'Decline', trend: -5 },
    });
    const trend = wrapper.find('.stat-trend');
    expect(trend.exists()).toBe(true);
    expect(trend.text()).toBe('-5%');
    expect(trend.classes()).toContain('down');
  });

  it('does not render trend when not provided', () => {
    const wrapper = mount(StatCard, {
      props: { value: '50', label: 'Stable' },
    });
    expect(wrapper.find('.stat-trend').exists()).toBe(false);
  });

  it('does not render trend when null', () => {
    const wrapper = mount(StatCard, {
      props: { value: '50', label: 'Stable', trend: undefined },
    });
    expect(wrapper.find('.stat-trend').exists()).toBe(false);
  });
});
