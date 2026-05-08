import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { setActivePinia, createPinia } from 'pinia';

const mockGetCurrentUser = vi.fn();
const mockFetchQuota = vi.fn();
const mockFetchUsageRecords = vi.fn();

vi.mock('../api', () => ({
  getCurrentUser: (...args: unknown[]) => mockGetCurrentUser(...args),
}));

vi.mock('../stores/user', () => ({
  useUserStore: () => ({
    quota: { weekly_limit: 2, used_this_week: 1, remaining: 1, reset_at: '2025-01-06T00:00:00Z' },
    usageRecords: [
      { id: 'u1', task_id: 't1', filename: 'demo.mp4', created_at: '2025-01-01T00:00:00Z', status: 'completed' },
    ],
    loading: false,
    fetchQuota: mockFetchQuota,
    fetchUsageRecords: mockFetchUsageRecords,
  }),
}));

vi.mock('element-plus', () => ({
  ElCard: { template: '<div class="el-card"><div class="el-card__body"><slot /></div></div>' },
  ElTag: { template: '<span class="el-tag"><slot /></span>', props: ['type', 'size'] },
  ElProgress: { template: '<div class="el-progress" />', props: ['percentage', 'strokeWidth'] },
  ElEmpty: { template: '<div class="el-empty">{{ description }}</div>', props: ['description'] },
  ElSkeleton: { template: '<div class="el-skeleton" />', props: ['rows'] },
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
    expect(mockFetchQuota).toHaveBeenCalled();
    expect(mockFetchUsageRecords).toHaveBeenCalled();
  });
});
