import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { setActivePinia, createPinia } from 'pinia';

const mockFetchShares = vi.fn();
const mockCreateShare = vi.fn();
const mockRemoveShare = vi.fn();

vi.mock('../stores/share', () => ({
  useShareStore: () => ({
    shares: [],
    loading: false,
    fetchShares: mockFetchShares,
    createShare: mockCreateShare,
    removeShare: mockRemoveShare,
  }),
}));

vi.mock('qrcode', () => ({
  default: {
    toCanvas: vi.fn(),
  },
}));

vi.mock('element-plus', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
  ElDialog: {
    template: '<div v-if="modelValue"><div>{{ title }}</div><slot /></div>',
    props: ['modelValue', 'title', 'width', 'closeOnClickModal'],
    emits: ['update:modelValue'],
  },
  ElInput: {
    template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'placeholder', 'maxlength', 'readonly'],
    emits: ['update:modelValue'],
  },
  ElButton: { template: '<button @click="$emit(\'click\')"><slot /></button>', props: ['type', 'loading', 'text', 'size'] },
  ElSelect: {
    template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
    props: ['modelValue'],
    emits: ['update:modelValue'],
  },
  ElOption: { template: '<option :value="value">{{ label }}</option>', props: ['value', 'label'] },
  ElDivider: { template: '<hr />' },
}));

beforeEach(() => {
  vi.clearAllMocks();
  setActivePinia(createPinia());
  mockFetchShares.mockResolvedValue([]);
});

async function mountShareDialog(props = { visible: true, taskId: 't1' }) {
  const { default: ShareDialog } = await import('./ShareDialog.vue');
  return mount(ShareDialog, {
    props,
  });
}

describe('ShareDialog.vue', () => {
  it('renders create form when visible', async () => {
    const wrapper = await mountShareDialog();
    expect(wrapper.text()).toContain('分享报告');
    expect(wrapper.text()).toContain('有效期');
    expect(wrapper.text()).toContain('生成分享链接');
  });

  it('shows expiration options', async () => {
    const wrapper = await mountShareDialog();
    const options = wrapper.findAll('option');
    const labels = options.map((o) => o.text());
    expect(labels).toContain('1 天');
    expect(labels).toContain('7 天');
    expect(labels).toContain('30 天');
    expect(labels).toContain('永久');
  });

  it('creates share link on button click', async () => {
    mockCreateShare.mockResolvedValue({
      id: 's1',
      task_id: 't1',
      token: 'abc123',
      access_code: '1234',
      template_config: null,
      created_at: '2025-01-01T00:00:00Z',
      expires_at: null,
      view_count: 0,
    });

    const wrapper = await mountShareDialog();
    const buttons = wrapper.findAll('button');
    const createBtn = buttons.find((b) => b.text().includes('生成'));
    await createBtn!.trigger('click');
    await flushPromises();

    expect(mockCreateShare).toHaveBeenCalledWith('t1', undefined, 7);
  });

  it('fetches existing shares on open', async () => {
    await mountShareDialog();
    await flushPromises();
    expect(mockFetchShares).toHaveBeenCalled();
  });

  it('shows share result after creation', async () => {
    mockCreateShare.mockResolvedValue({
      id: 's1',
      task_id: 't1',
      token: 'abc123',
      access_code: '5678',
      template_config: null,
      created_at: '2025-01-01T00:00:00Z',
      expires_at: null,
      view_count: 0,
    });

    const wrapper = await mountShareDialog();
    const buttons = wrapper.findAll('button');
    const createBtn = buttons.find((b) => b.text().includes('生成'));
    await createBtn!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('分享链接');
    expect(wrapper.text()).toContain('提取码');
    expect(wrapper.text()).toContain('创建新的分享链接');
  });
});
