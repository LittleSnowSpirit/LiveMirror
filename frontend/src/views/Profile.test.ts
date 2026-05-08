import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { setActivePinia, createPinia } from 'pinia';

const mockGetCurrentUser = vi.fn();
const mockFetchQuota = vi.fn();
const mockFetchUsageRecords = vi.fn();
const mockFetchProfile = vi.fn();
const mockUpdateProfile = vi.fn();
const mockUploadAvatar = vi.fn();

vi.mock('../api', () => ({
  getCurrentUser: (...args: unknown[]) => mockGetCurrentUser(...args),
}));

vi.mock('../stores/user', () => ({
  useUserStore: () => ({
    quota: { weekly_limit: 2, used_this_week: 1, remaining: 1, reset_at: '2025-01-06T00:00:00Z' },
    usageRecords: [
      { id: 'u1', task_id: 't1', filename: 'demo.mp4', created_at: '2025-01-01T00:00:00Z', status: 'completed' },
    ],
    profile: {
      id: 1,
      username: 'testuser',
      nickname: 'Test Nick',
      bio: 'Test bio',
      avatar_url: '',
      email: 'test@example.com',
      is_active: true,
      created_at: '2025-01-01T00:00:00Z',
    },
    loading: false,
    fetchQuota: mockFetchQuota,
    fetchUsageRecords: mockFetchUsageRecords,
    fetchProfile: mockFetchProfile,
    updateProfile: mockUpdateProfile,
    uploadAvatar: mockUploadAvatar,
  }),
}));

vi.mock('element-plus', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
  ElCard: { template: '<div class="el-card"><div class="el-card__body"><slot /></div></div>' },
  ElTag: { template: '<span class="el-tag"><slot /></span>', props: ['type', 'size'] },
  ElProgress: { template: '<div class="el-progress" />', props: ['percentage', 'strokeWidth'] },
  ElEmpty: { template: '<div class="el-empty">{{ description }}</div>', props: ['description'] },
  ElSkeleton: { template: '<div class="el-skeleton" />', props: ['rows'] },
  ElInput: {
    template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'placeholder', 'type', 'rows'],
    emits: ['update:modelValue'],
  },
  ElButton: { template: '<button @click="$emit(\'click\')"><slot /></button>', props: ['type', 'loading'] },
}));

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
  ],
});

beforeEach(() => {
  vi.clearAllMocks();
  setActivePinia(createPinia());
  mockGetCurrentUser.mockResolvedValue({
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    created_at: '2025-01-01T00:00:00Z',
  });
  mockFetchProfile.mockResolvedValue({
    id: 1,
    username: 'testuser',
    nickname: 'Test Nick',
    bio: 'Test bio',
    avatar_url: '',
  });
  mockUpdateProfile.mockResolvedValue({
    id: 1,
    username: 'testuser',
    nickname: 'Updated',
    bio: 'Updated bio',
    avatar_url: '',
  });
});

async function mountProfile() {
  const { default: Profile } = await import('./Profile.vue');
  return mount(Profile, {
    global: {
      plugins: [router],
    },
  });
}

describe('Profile.vue', () => {
  it('renders the page title', async () => {
    const wrapper = await mountProfile();
    expect(wrapper.text()).toContain('我的账户');
  });

  it('displays user info', async () => {
    const wrapper = await mountProfile();
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('testuser');
      expect(wrapper.text()).toContain('test@example.com');
    });
  });

  it('displays quota info', async () => {
    const wrapper = await mountProfile();
    expect(wrapper.text()).toContain('1');
    expect(wrapper.text()).toContain('2');
  });

  it('displays usage records', async () => {
    const wrapper = await mountProfile();
    expect(wrapper.text()).toContain('demo.mp4');
  });

  it('calls fetchQuota and fetchUsageRecords on mount', async () => {
    await mountProfile();
    await flushPromises();
    expect(mockFetchQuota).toHaveBeenCalled();
    expect(mockFetchUsageRecords).toHaveBeenCalled();
  });

  it('renders avatar placeholder when no avatar', async () => {
    const wrapper = await mountProfile();
    await flushPromises();
    expect(wrapper.find('.avatar-placeholder').exists()).toBe(true);
  });

  it('renders profile editing form', async () => {
    const wrapper = await mountProfile();
    await flushPromises();
    expect(wrapper.text()).toContain('编辑资料');
    expect(wrapper.text()).toContain('昵称');
    expect(wrapper.text()).toContain('简介');
  });

  it('renders save and cancel buttons', async () => {
    const wrapper = await mountProfile();
    await flushPromises();
    const buttons = wrapper.findAll('button');
    const saveBtn = buttons.find((b) => b.text().includes('保存'));
    const cancelBtn = buttons.find((b) => b.text().includes('取消'));
    expect(saveBtn).toBeTruthy();
    expect(cancelBtn).toBeTruthy();
  });

  it('calls updateProfile on save', async () => {
    const wrapper = await mountProfile();
    await flushPromises();

    const buttons = wrapper.findAll('button');
    const saveBtn = buttons.find((b) => b.text().includes('保存'));
    await saveBtn!.trigger('click');
    await flushPromises();

    expect(mockUpdateProfile).toHaveBeenCalled();
  });

  it('fetches profile on mount', async () => {
    await mountProfile();
    await flushPromises();
    expect(mockFetchProfile).toHaveBeenCalled();
  });
});
