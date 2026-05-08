import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { ref } from 'vue';
import { setActivePinia, createPinia } from 'pinia';

const mockFetchTasks = vi.fn();
const mockDeleteTaskItem = vi.fn();
const mockBatchExport = vi.fn();
const mockTasks = ref<any[]>([]);

vi.mock('../stores/task', () => ({
  useTaskStore: () => ({
    tasks: mockTasks,
    loading: false,
    total: 1,
    currentPage: 1,
    pageSize: 20,
    fetchTasks: mockFetchTasks,
    deleteTaskItem: mockDeleteTaskItem,
    batchExport: mockBatchExport,
  }),
}));

vi.mock('element-plus', () => ({
  ElMessage: { warning: vi.fn(), success: vi.fn(), error: vi.fn() },
  ElMessageBox: { confirm: vi.fn().mockResolvedValue('confirm') },
  ElCard: { template: '<div class="el-card"><div class="el-card__body"><slot /></div></div>' },
  ElInput: { template: '<input />', props: ['modelValue', 'placeholder'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue'] },
  ElOption: { template: '<option />', props: ['label', 'value'] },
  ElButton: { template: '<button @click="$emit(\'click\')"><slot /></button>', props: ['type', 'size'] },
  ElTag: { template: '<span class="el-tag"><slot /></span>', props: ['type', 'size'] },
  ElProgress: { template: '<div class="el-progress" />', props: ['percentage', 'strokeWidth'] },
  ElPagination: { template: '<div class="el-pagination" />', props: ['currentPage', 'total', 'pageSize', 'layout'] },
  ElEmpty: { template: '<div class="el-empty">{{ description }}</div>', props: ['description'] },
  ElSkeleton: { template: '<div class="el-skeleton" />', props: ['rows'] },
}));

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/report/:taskId?', name: 'report', component: { template: '<div />' } },
  ],
});

beforeEach(() => {
  vi.clearAllMocks();
  mockTasks.value = [];
  setActivePinia(createPinia());
  mockFetchTasks.mockImplementation(() => {
    mockTasks.value = [
      {
        task_id: 't1',
        filename: 'test.mp4',
        status: 'completed',
        progress: 100,
        file_size: 1024,
        duration: 120,
        created_at: '2025-01-01T00:00:00Z',
        completed_at: '2025-01-01T00:05:00Z',
      },
    ];
  });
});

async function mountHistory() {
  const { default: History } = await import('./History.vue');
  return mount(History, {
    global: {
      plugins: [router],
    },
  });
}

describe('History.vue', () => {
  it('renders the page title', async () => {
    const wrapper = await mountHistory();
    expect(wrapper.text()).toContain('历史记录');
  });

  it('calls fetchTasks on mount', async () => {
    await mountHistory();
    expect(mockFetchTasks).toHaveBeenCalled();
  });

  it('renders task cards after fetch', async () => {
    const wrapper = await mountHistory();
    await vi.waitFor(() => {
      expect(wrapper.findAll('.task-card').length).toBeGreaterThan(0);
    });
  });

  it('renders delete buttons for tasks', async () => {
    const wrapper = await mountHistory();
    await vi.waitFor(() => {
      expect(wrapper.findAll('button').length).toBeGreaterThan(0);
    });
  });

  it('has search and filter inputs', async () => {
    const wrapper = await mountHistory();
    expect(wrapper.find('input').exists()).toBe(true);
  });
});
