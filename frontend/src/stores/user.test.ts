import { describe, it, expect, vi, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from './user';

const mockGetUserQuota = vi.fn();
const mockGetUsageRecords = vi.fn();

vi.mock('../api', () => ({
  getUserQuota: (...args: unknown[]) => mockGetUserQuota(...args),
  getUsageRecords: (...args: unknown[]) => mockGetUsageRecords(...args),
}));

beforeEach(() => {
  vi.clearAllMocks();
  setActivePinia(createPinia());
});

describe('useUserStore', () => {
  it('fetches quota', async () => {
    mockGetUserQuota.mockResolvedValueOnce({
      weekly_limit: 2,
      used_this_week: 1,
      remaining: 1,
      reset_at: '2025-01-06T00:00:00Z',
    });

    const store = useUserStore();
    await store.fetchQuota();

    expect(store.quota).not.toBeNull();
    expect(store.quota!.weekly_limit).toBe(2);
    expect(store.quota!.remaining).toBe(1);
  });

  it('fetches usage records', async () => {
    mockGetUsageRecords.mockResolvedValueOnce([
      { id: 'u1', task_id: 't1', filename: 'test.mp4', created_at: '2025-01-01', status: 'completed' },
    ]);

    const store = useUserStore();
    await store.fetchUsageRecords();

    expect(store.usageRecords).toHaveLength(1);
    expect(store.usageRecords[0].filename).toBe('test.mp4');
    expect(store.loading).toBe(false);
  });

  it('sets loading to false after fetch completes', async () => {
    mockGetUsageRecords.mockResolvedValueOnce([]);

    const store = useUserStore();
    expect(store.loading).toBe(false);

    const promise = store.fetchUsageRecords();
    expect(store.loading).toBe(true);

    await promise;
    expect(store.loading).toBe(false);
  });
});
