import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';

const mockExportPDF = vi.fn();
const mockExportImage = vi.fn();

vi.mock('../api', () => ({
  exportPDF: (...args: unknown[]) => mockExportPDF(...args),
  exportImage: (...args: unknown[]) => mockExportImage(...args),
}));

vi.mock('element-plus', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
  ElButton: { template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /></button>', props: ['disabled', 'type'] },
  ElDropdown: { template: '<div><slot /><slot name="dropdown" /></div>', props: ['trigger'] },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div @click="$emit(\'click\')"><slot /></div>', props: ['command'] },
  ElIcon: { template: '<span><slot /></span>' },
}));

beforeEach(() => {
  vi.clearAllMocks();
});

async function mountExportPanel(props = { taskId: 't1' }) {
  const { default: ExportPanel } = await import('./ExportPanel.vue');
  return mount(ExportPanel, { props });
}

describe('ExportPanel.vue', () => {
  it('renders export buttons', async () => {
    const wrapper = await mountExportPanel();
    expect(wrapper.text()).toContain('导出 PDF');
    expect(wrapper.text()).toContain('导出图片');
    expect(wrapper.text()).toContain('分享');
  });

  it('disables buttons when no taskId', async () => {
    const wrapper = await mountExportPanel({ taskId: '' });
    const buttons = wrapper.findAll('button');
    buttons.forEach((btn) => {
      expect(btn.attributes('disabled')).toBeDefined();
    });
  });

  it('emits share event when share button clicked', async () => {
    const wrapper = await mountExportPanel();
    const buttons = wrapper.findAll('button');
    const shareBtn = buttons.find((b) => b.text().includes('分享'));
    await shareBtn!.trigger('click');
    expect(wrapper.emitted('share')).toBeTruthy();
  });

  it('shows dropdown menu items', async () => {
    const wrapper = await mountExportPanel();
    expect(wrapper.text()).toContain('默认模板');
    expect(wrapper.text()).toContain('简洁模板');
    expect(wrapper.text()).toContain('详细模板');
  });
});
