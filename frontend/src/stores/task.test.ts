import { describe, it, expect, vi, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useTaskStore } from './task';

const mockGetHistory = vi.fn();
const mockDeleteTask = vi.fn();
const mockBatchExport = vi.fn();

vi.mock('../api', () => ({
  getHistory: (...args: unknown[]) => mockGetHistory(...args),
  deleteTask: (...args: unknown[]) => mockDeleteTask(...args),
  batchExport: (...args: unknown[]) => mockBatchExport(...args),
}));

beforeEach(() => {
  vi.clearAllMocks();
  setActivePinia(createPinia());
});

describe('useTaskStore', () => {
  it('fetches tasks and maps fields', async () => {
    mockGetHistory.mockResolvedValueOnce({
      success: true,
      items: [
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
      ],
      total: 1,
      page: 1,
      page_size: 20,
    });

    const store = useTaskStore();
    await store.fetchTasks();

    expect(store.tasks).toHaveLength(1);
    expect(store.tasks[0].task_id).toBe('t1');
    expect(store.tasks[0].filename).toBe('test.mp4');
    expect(store.tasks[0].status).toBe('completed');
    expect(store.total).toBe(1);
  });

  it('passes params to getHistory', async () => {
    mockGetHistory.mockResolvedValueOnce({
      success: true,
      items: [],
      total: 0,
      page: 2,
      page_size: 10,
    });

    const store = useTaskStore();
    await store.fetchTasks({ page: 2, page_size: 10, status: 'completed' });

    expect(mockGetHistory).toHaveBeenCalledWith({ page: 2, page_size: 10, status: 'completed' });
    expect(store.currentPage).toBe(2);
    expect(store.pageSize).toBe(10);
  });

  it('deletes a task and updates list', async () => {
    mockGetHistory.mockResolvedValueOnce({
      success: true,
      items: [
        { task_id: 't1', filename: 'a.mp4', status: 'completed', progress: 100, created_at: '' },
        { task_id: 't2', filename: 'b.mp4', status: 'pending', progress: 0, created_at: '' },
      ],
      total: 2,
      page: 1,
      page_size: 20,
    });
    mockDeleteTask.mockResolvedValueOnce({});

    const store = useTaskStore();
    await store.fetchTasks();
    await store.deleteTaskItem('t1');

    expect(store.tasks).toHaveLength(1);
    expect(store.tasks[0].task_id).toBe('t2');
    expect(store.total).toBe(1);
  });

  it('calls batchExport', async () => {
    const fakeBlob = new Blob(['data']);
    mockBatchExport.mockResolvedValueOnce(fakeBlob);

    const store = useTaskStore();
    const result = await store.batchExport(['t1', 't2'], 'markdown');

    expect(mockBatchExport).toHaveBeenCalledWith(['t1', 't2'], 'markdown');
    expect(result).toBe(fakeBlob);
  });
});
