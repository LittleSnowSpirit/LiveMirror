import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { ref } from 'vue';

const mockUploadFile = vi.fn();
const mockSetStoredTaskId = vi.fn();
const mockElMessage = { warning: vi.fn(), success: vi.fn(), error: vi.fn() };

vi.mock('../api', () => ({
  uploadFile: (...args: unknown[]) => mockUploadFile(...args),
  setStoredTaskId: (...args: unknown[]) => mockSetStoredTaskId(...args),
}));

vi.mock('element-plus', () => ({
  ElMessage: mockElMessage,
  ElCard: { template: '<div><slot /></div>' },
  ElButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
  ElProgress: { template: '<div />' },
  ElAlert: { template: '<div>{{ title }}</div>', props: ['title'] },
  ElTabs: {
    template: '<div><slot /></div>',
    props: ['modelValue'],
    emits: ['update:modelValue'],
  },
  ElTabPane: {
    template: '<div><slot /></div>',
    props: ['label', 'name'],
  },
}));

vi.mock('../components/LinkInput.vue', () => ({
  default: { template: '<div class="link-input-stub" />' },
}));

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/report/:taskId?', name: 'report', component: { template: '<div />' } },
  ],
});

async function mountUpload() {
  const { default: Upload } = await import('./Upload.vue');
  return mount(Upload, {
    global: {
      plugins: [router],
    },
  });
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe('Upload.vue', () => {
  it('renders the upload form with tabs', async () => {
    const wrapper = await mountUpload();
    expect(wrapper.text()).toContain('创建分析任务');
    expect(wrapper.find('input[type="file"]').exists()).toBe(true);
  });

  it('shows file name after file selection', async () => {
    const wrapper = await mountUpload();
    const input = wrapper.find('input[type="file"]');
    const file = new File(['content'], 'test.mp4', { type: 'video/mp4' });

    Object.defineProperty(input.element, 'files', { value: [file] });
    await input.trigger('change');

    expect(wrapper.text()).toContain('test.mp4');
  });

  it('calls uploadFile on upload button click', async () => {
    mockUploadFile.mockResolvedValueOnce({
      task_id: 'task-123',
      filename: 'test.mp4',
      file_size: 1024,
      status: 'pending',
    });

    const wrapper = await mountUpload();
    const file = new File(['content'], 'test.mp4', { type: 'video/mp4' });
    const input = wrapper.find('input[type="file"]');

    Object.defineProperty(input.element, 'files', { value: [file] });
    await input.trigger('change');

    const buttons = wrapper.findAll('button');
    const uploadButton = buttons.find((b) => b.text().includes('上传并创建任务'));
    await uploadButton!.trigger('click');

    await vi.waitFor(() => {
      expect(mockUploadFile).toHaveBeenCalledWith(file, expect.any(Function));
    });
  });

  it('displays result after successful upload', async () => {
    mockUploadFile.mockResolvedValueOnce({
      task_id: 'task-456',
      filename: 'video.mp4',
      file_size: 2048,
      status: 'pending',
    });

    const wrapper = await mountUpload();
    const file = new File(['content'], 'video.mp4', { type: 'video/mp4' });
    const input = wrapper.find('input[type="file"]');

    Object.defineProperty(input.element, 'files', { value: [file] });
    await input.trigger('change');

    const buttons = wrapper.findAll('button');
    const uploadButton = buttons.find((b) => b.text().includes('上传并创建任务'));
    await uploadButton!.trigger('click');

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('task-456');
      expect(wrapper.text()).toContain('video.mp4');
    });
  });

  it('stores task ID after successful upload', async () => {
    mockUploadFile.mockResolvedValueOnce({
      task_id: 'task-789',
      filename: 'f.mp4',
      file_size: 100,
      status: 'pending',
    });

    const wrapper = await mountUpload();
    const file = new File(['x'], 'f.mp4');
    const input = wrapper.find('input[type="file"]');

    Object.defineProperty(input.element, 'files', { value: [file] });
    await input.trigger('change');

    const buttons = wrapper.findAll('button');
    const uploadButton = buttons.find((b) => b.text().includes('上传并创建任务'));
    await uploadButton!.trigger('click');

    await vi.waitFor(() => {
      expect(mockSetStoredTaskId).toHaveBeenCalledWith('task-789');
    });
  });

  it('shows error message on upload failure', async () => {
    mockUploadFile.mockRejectedValueOnce(new Error('upload failed'));

    const wrapper = await mountUpload();
    const file = new File(['x'], 'bad.exe');
    const input = wrapper.find('input[type="file"]');

    Object.defineProperty(input.element, 'files', { value: [file] });
    await input.trigger('change');

    const buttons = wrapper.findAll('button');
    const uploadButton = buttons.find((b) => b.text().includes('上传并创建任务'));
    await uploadButton!.trigger('click');

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('上传失败');
    });
  });
});
