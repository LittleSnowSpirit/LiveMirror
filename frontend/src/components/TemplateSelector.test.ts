import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';

vi.mock('element-plus', () => ({
  ElSwitch: {
    template: '<input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" />',
    props: ['modelValue'],
    emits: ['update:modelValue', 'change'],
  },
  ElButton: { template: '<button @click="$emit(\'click\')"><slot /></button>', props: ['text', 'size', 'disabled'] },
}));

beforeEach(() => {
  vi.clearAllMocks();
});

async function mountTemplateSelector() {
  const { default: TemplateSelector } = await import('./TemplateSelector.vue');
  return mount(TemplateSelector);
}

describe('TemplateSelector.vue', () => {
  it('renders all module labels', async () => {
    const wrapper = await mountTemplateSelector();
    const expected = ['综合得分', '爆点分析', '翻车点', '节奏分析', '互动指标', '情绪曲线', '话术多样性', '建议'];
    expected.forEach((label) => {
      expect(wrapper.text()).toContain(label);
    });
  });

  it('renders preset buttons', async () => {
    const wrapper = await mountTemplateSelector();
    expect(wrapper.text()).toContain('简洁');
    expect(wrapper.text()).toContain('详细');
    expect(wrapper.text()).toContain('数据');
  });

  it('renders toggle switches for each module', async () => {
    const wrapper = await mountTemplateSelector();
    const switches = wrapper.findAll('input[type="checkbox"]');
    expect(switches.length).toBe(8);
  });

  it('renders move up/down buttons', async () => {
    const wrapper = await mountTemplateSelector();
    expect(wrapper.text()).toContain('↑');
    expect(wrapper.text()).toContain('↓');
  });

  it('emits update:config when preset is applied', async () => {
    const wrapper = await mountTemplateSelector();
    const buttons = wrapper.findAll('button');
    const compactBtn = buttons.find((b) => b.text().includes('简洁'));
    await compactBtn!.trigger('click');

    const emitted = wrapper.emitted('update:config');
    expect(emitted).toBeTruthy();
    expect(emitted![0][0]).toHaveProperty('visible');
    expect(emitted![0][0]).toHaveProperty('order');
  });

  it('compact preset hides some modules', async () => {
    const wrapper = await mountTemplateSelector();
    const buttons = wrapper.findAll('button');
    const compactBtn = buttons.find((b) => b.text().includes('简洁'));
    await compactBtn!.trigger('click');

    const emitted = wrapper.emitted('update:config');
    const config = emitted![0][0] as { visible: string[]; order: string[] };
    expect(config.visible).toContain('overall_score');
    expect(config.visible).toContain('suggestions');
    expect(config.visible).not.toContain('rhythm');
    expect(config.visible).not.toContain('emotion_curve');
  });
});
