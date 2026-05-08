import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';

const mockGetShareLink = vi.fn();

vi.mock('../api', () => ({
  getShareLink: (...args: unknown[]) => mockGetShareLink(...args),
}));

vi.mock('element-plus', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
  ElCard: { template: '<div class="el-card"><div class="el-card__body"><slot /></div></div>' },
  ElInput: {
    template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'placeholder', 'maxlength', 'readonly'],
    emits: ['update:modelValue'],
  },
  ElButton: { template: '<button @click="$emit(\'click\')"><slot /></button>', props: ['type', 'loading'] },
  ElAlert: { template: '<div v-if="title">{{ title }}</div>', props: ['title', 'type', 'closable', 'showIcon'] },
  ElSkeleton: { template: '<div />', props: ['rows', 'animated'] },
  ElEmpty: { template: '<div>{{ description }}</div>', props: ['description'] },
  ElTable: { template: '<table><slot /></table>', props: ['data', 'border'] },
  ElTableColumn: { template: '<td />', props: ['prop', 'label', 'width', 'minWidth'] },
}));

const router = createRouter({
  history: createMemoryHistory('/share/test-token'),
  routes: [
    { path: '/share/:token', name: 'shared-report', component: { template: '<div />' } },
    { path: '/', component: { template: '<div />' } },
  ],
});

beforeEach(() => {
  vi.clearAllMocks();
});

async function mountSharedReport() {
  router.replace('/share/test-token');
  await router.isReady();
  const { default: SharedReport } = await import('./SharedReport.vue');
  return mount(SharedReport, {
    global: { plugins: [router] },
  });
}

describe('SharedReport.vue', () => {
  it('renders access code form', async () => {
    const wrapper = await mountSharedReport();
    expect(wrapper.text()).toContain('输入提取码');
    expect(wrapper.text()).toContain('查看报告');
  });

  it('shows error when access code is empty', async () => {
    const wrapper = await mountSharedReport();
    const buttons = wrapper.findAll('button');
    const verifyBtn = buttons.find((b) => b.text().includes('查看'));
    await verifyBtn!.trigger('click');
    await flushPromises();
    expect(wrapper.text()).toContain('请输入提取码');
  });

  it('calls getShareLink with token and access code', async () => {
    mockGetShareLink.mockResolvedValue({
      report: { task_id: 't1', filename: 'test.mp4' },
      template_config: null,
    });

    const wrapper = await mountSharedReport();
    const input = wrapper.find('input');
    await input.setValue('1234');

    const buttons = wrapper.findAll('button');
    const verifyBtn = buttons.find((b) => b.text().includes('查看'));
    await verifyBtn!.trigger('click');
    await flushPromises();

    expect(mockGetShareLink).toHaveBeenCalledWith('test-token', '1234');
  });

  it('displays report after successful verification', async () => {
    mockGetShareLink.mockResolvedValue({
      report: {
        task_id: 't1',
        filename: 'demo.mp4',
        duration: 120,
        transcription: 'Hello world',
      },
      template_config: null,
    });

    const wrapper = await mountSharedReport();
    const input = wrapper.find('input');
    await input.setValue('1234');

    const buttons = wrapper.findAll('button');
    const verifyBtn = buttons.find((b) => b.text().includes('查看'));
    await verifyBtn!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('demo.mp4');
    expect(wrapper.text()).toContain('Hello world');
  });

  it('shows error on verification failure', async () => {
    mockGetShareLink.mockRejectedValue({
      response: { data: { detail: '提取码错误' } },
    });

    const wrapper = await mountSharedReport();
    const input = wrapper.find('input');
    await input.setValue('wrong');

    const buttons = wrapper.findAll('button');
    const verifyBtn = buttons.find((b) => b.text().includes('查看'));
    await verifyBtn!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('提取码错误');
  });
});
