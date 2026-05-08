import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { setActivePinia, createPinia } from 'pinia';

const mockGetTaskStatus = vi.fn();
const mockGetReport = vi.fn();
const mockExportReport = vi.fn();
const mockGetStoredTaskId = vi.fn();
const mockSetStoredTaskId = vi.fn();

vi.mock('../api', () => ({
  getTaskStatus: (...args: unknown[]) => mockGetTaskStatus(...args),
  getReport: (...args: unknown[]) => mockGetReport(...args),
  exportReport: (...args: unknown[]) => mockExportReport(...args),
  getStoredTaskId: (...args: unknown[]) => mockGetStoredTaskId(...args),
  setStoredTaskId: (...args: unknown[]) => mockSetStoredTaskId(...args),
}));

vi.mock('../components/ExportPanel.vue', () => ({
  default: { template: '<div class="export-panel-stub" />', props: ['taskId'], emits: ['share'] },
}));

vi.mock('../components/ShareDialog.vue', () => ({
  default: { template: '<div class="share-dialog-stub" />', props: ['visible', 'taskId'], emits: ['update:visible'] },
}));

vi.mock('element-plus', () => ({
  ElMessage: { warning: vi.fn(), success: vi.fn(), error: vi.fn() },
  ElCard: { template: '<div><slot /></div>' },
  ElButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
  ElInput: {
    template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'placeholder'],
    emits: ['update:modelValue'],
  },
  ElProgress: { template: '<div />', props: ['percentage', 'strokeWidth'] },
  ElAlert: { template: '<div v-if="title">{{ title }}</div>', props: ['title', 'type', 'closable', 'showIcon'] },
  ElTag: { template: '<span><slot /></span>', props: ['type', 'effect'] },
  ElSkeleton: { template: '<div />', props: ['rows', 'animated'] },
  ElEmpty: { template: '<div>{{ description }}</div>', props: ['description'] },
  ElTable: { template: '<table><slot /></table>', props: ['data', 'border'] },
  ElTableColumn: { template: '<td />', props: ['prop', 'label', 'width', 'minWidth'] },
}));

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/report/:taskId?', name: 'report', component: { template: '<div />' } },
  ],
});

async function mountReport() {
  router.replace('/');
  await router.isReady();
  const { default: Report } = await import('./Report.vue');
  return mount(Report, {
    global: { plugins: [router] },
  });
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  setActivePinia(createPinia());
  mockGetStoredTaskId.mockReturnValue('');
  mockGetTaskStatus.mockReset();
  mockGetReport.mockReset();
});

describe('Report.vue', () => {
  it('renders the report page', async () => {
    const wrapper = await mountReport();
    expect(wrapper.text()).toContain('查看任务报告');
  });

  it('loads report when user enters task ID and clicks load', async () => {
    mockGetTaskStatus.mockResolvedValue({
      task: { task_id: 't1', filename: 'test.mp4', status: 'completed', progress: 100 },
    });
    mockGetReport.mockResolvedValue({
      success: true,
      data: { task_id: 't1', filename: 'test.mp4', transcription: 'hello world' },
    });

    const wrapper = await mountReport();
    const input = wrapper.find('input');
    await input.setValue('t1');

    const buttons = wrapper.findAll('button');
    const loadButton = buttons.find((b) => b.text().includes('加载'));
    await loadButton!.trigger('click');
    await flushPromises();

    expect(mockGetTaskStatus).toHaveBeenCalledWith('t1');
    expect(wrapper.text()).toContain('test.mp4');
    expect(wrapper.text()).toContain('hello world');
  });

  it('shows task status info', async () => {
    mockGetTaskStatus.mockResolvedValue({
      task: { task_id: 't2', filename: 'video.mp4', status: 'processing', progress: 50 },
    });

    const wrapper = await mountReport();
    const input = wrapper.find('input');
    await input.setValue('t2');

    const buttons = wrapper.findAll('button');
    const loadButton = buttons.find((b) => b.text().includes('加载'));
    await loadButton!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('video.mp4');
    expect(wrapper.text()).toContain('50');
  });

  it('does not fetch report when task is not completed', async () => {
    mockGetTaskStatus.mockResolvedValue({
      task: { task_id: 't3', filename: 'v.mp4', status: 'processing', progress: 30 },
    });

    const wrapper = await mountReport();
    const input = wrapper.find('input');
    await input.setValue('t3');

    const buttons = wrapper.findAll('button');
    const loadButton = buttons.find((b) => b.text().includes('加载'));
    await loadButton!.trigger('click');
    await flushPromises();

    expect(mockGetReport).not.toHaveBeenCalled();
  });

  it('shows error message on load failure', async () => {
    mockGetTaskStatus.mockRejectedValue({
      response: { data: { detail: '任务不存在' } },
    });

    const wrapper = await mountReport();
    const input = wrapper.find('input');
    await input.setValue('bad-id');

    const buttons = wrapper.findAll('button');
    const loadButton = buttons.find((b) => b.text().includes('加载'));
    await loadButton!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('任务不存在');
  });

  it('shows transcription text', async () => {
    mockGetTaskStatus.mockResolvedValue({
      task: { task_id: 't5', filename: 'f.mp4', status: 'completed', progress: 100 },
    });
    mockGetReport.mockResolvedValue({
      success: true,
      data: { task_id: 't5', filename: 'f.mp4', transcription: '转写文本内容' },
    });

    const wrapper = await mountReport();
    const input = wrapper.find('input');
    await input.setValue('t5');

    const buttons = wrapper.findAll('button');
    const loadButton = buttons.find((b) => b.text().includes('加载'));
    await loadButton!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('转写文本内容');
  });

  it('loads report from stored task ID on mount', async () => {
    mockGetStoredTaskId.mockReturnValue('stored-task');
    mockGetTaskStatus.mockResolvedValue({
      task: { task_id: 'stored-task', filename: 'f.mp4', status: 'completed', progress: 100 },
    });
    mockGetReport.mockResolvedValue({
      success: true,
      data: { task_id: 'stored-task', filename: 'f.mp4' },
    });

    const wrapper = await mountReport();
    await flushPromises();

    expect(mockGetTaskStatus).toHaveBeenCalledWith('stored-task');
    expect(wrapper.text()).toContain('f.mp4');
  });
});
