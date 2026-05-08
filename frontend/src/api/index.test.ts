import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

vi.mock('axios', () => {
  const instance = {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  };
  return {
    default: {
      create: vi.fn(() => instance),
    },
  };
});

vi.mock('element-plus', () => ({
  ElMessage: { error: vi.fn() },
}));

const mockAxiosInstance = (axios.create as unknown as () => {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
  interceptors: {
    request: { use: ReturnType<typeof vi.fn> };
    response: { use: ReturnType<typeof vi.fn> };
  };
})();

let mod: typeof import('./index');

beforeEach(async () => {
  localStorage.clear();
  vi.clearAllMocks();
  mod = await import('./index');
});

afterEach(() => {
  localStorage.clear();
});

// ---- Token management ----

describe('token management', () => {
  it('setAuthTokens stores tokens in localStorage', () => {
    mod.setAuthTokens({
      access_token: 'acc',
      refresh_token: 'ref',
      token_type: 'Bearer',
      expires_in: 3600,
    });
    expect(localStorage.getItem('access_token')).toBe('acc');
    expect(localStorage.getItem('refresh_token')).toBe('ref');
    expect(localStorage.getItem('token_type')).toBe('Bearer');
  });

  it('clearAuthTokens removes tokens', () => {
    localStorage.setItem('access_token', 'x');
    localStorage.setItem('refresh_token', 'y');
    mod.clearAuthTokens();
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
  });

  it('getAccessToken returns stored token', () => {
    localStorage.setItem('access_token', 'tok');
    expect(mod.getAccessToken()).toBe('tok');
  });

  it('getToken is an alias for getAccessToken', () => {
    localStorage.setItem('access_token', 'abc');
    expect(mod.getToken()).toBe('abc');
  });

  it('isAuthenticated returns true when token exists', () => {
    expect(mod.isAuthenticated()).toBe(false);
    localStorage.setItem('access_token', 'tok');
    expect(mod.isAuthenticated()).toBe(true);
  });

  it('logout clears tokens', () => {
    localStorage.setItem('access_token', 'tok');
    mod.logout();
    expect(mod.isAuthenticated()).toBe(false);
  });
});

// ---- Task ID storage ----

describe('task ID storage', () => {
  it('setStoredTaskId stores and getStoredTaskId retrieves', () => {
    mod.setStoredTaskId('task-123');
    expect(mod.getStoredTaskId()).toBe('task-123');
  });

  it('setStoredTaskId ignores empty string', () => {
    mod.setStoredTaskId('');
    expect(localStorage.getItem('livemirror:last-task-id')).toBeNull();
  });

  it('getStoredTaskId returns empty string when not set', () => {
    expect(mod.getStoredTaskId()).toBe('');
  });
});

// ---- API functions ----

describe('API functions', () => {
  it('login sends POST to /auth/login', async () => {
    const tokens = { access_token: 'a', refresh_token: 'r', token_type: 'Bearer', expires_in: 3600 };
    mockAxiosInstance.post.mockResolvedValueOnce({ data: tokens });

    const params = new URLSearchParams({ username: 'u', password: 'p' });
    const result = await mod.login(params);

    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    expect(result).toEqual(tokens);
  });

  it('register sends POST to /auth/register', async () => {
    const user = { id: 1, username: 'u', is_active: true, created_at: '' };
    mockAxiosInstance.post.mockResolvedValueOnce({ data: user });

    const result = await mod.register({ username: 'u', password: 'p' });
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/register', { username: 'u', password: 'p' });
    expect(result).toEqual(user);
  });

  it('getCurrentUser sends GET to /auth/me', async () => {
    const user = { id: 1, username: 'u', is_active: true, created_at: '' };
    mockAxiosInstance.get.mockResolvedValueOnce({ data: user });

    const result = await mod.getCurrentUser();
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/auth/me');
    expect(result).toEqual(user);
  });

  it('getTaskStatus sends GET to /api/task/:id', async () => {
    const resp = { task: { task_id: 't1', status: 'done', progress: 100 } };
    mockAxiosInstance.get.mockResolvedValueOnce({ data: resp });

    const result = await mod.getTaskStatus('t1');
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/task/t1');
    expect(result).toEqual(resp);
  });

  it('getReport sends GET to /api/report/:id', async () => {
    const resp = { success: true, data: { task_id: 't1' } };
    mockAxiosInstance.get.mockResolvedValueOnce({ data: resp });

    const result = await mod.getReport('t1');
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/report/t1');
    expect(result).toEqual(resp);
  });

  it('exportReport sends GET with responseType blob', async () => {
    const blob = new Blob(['{}']);
    mockAxiosInstance.get.mockResolvedValueOnce({ data: blob });

    const result = await mod.exportReport('t1', 'json');
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/export/t1/json', { responseType: 'blob' });
    expect(result).toBe(blob);
  });

  it('uploadFile sends POST with FormData', async () => {
    const resp = { task_id: 't1', filename: 'f.mp4', file_size: 100, status: 'ok' };
    mockAxiosInstance.post.mockResolvedValueOnce({ data: resp });

    const file = new File(['content'], 'test.mp4');
    const onProgress = vi.fn();
    const result = await mod.uploadFile(file, onProgress);

    expect(mockAxiosInstance.post).toHaveBeenCalledWith(
      '/api/upload',
      expect.any(FormData),
      expect.objectContaining({
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    );
    expect(result).toEqual(resp);
  });

  it('analyzeSuggestion sends POST to /api/suggestions/analyze', async () => {
    const resp = { success: true, data: {} };
    mockAxiosInstance.post.mockResolvedValueOnce({ data: resp });

    const req = { speech: { id: '1', type: 'opening', content: 'hi', start_time: 0, end_time: 5 } };
    const result = await mod.analyzeSuggestion(req);
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/suggestions/analyze', req);
    expect(result).toEqual(resp);
  });

  it('getExcellentExamples sends GET with params', async () => {
    const resp = { success: true, examples: [] };
    mockAxiosInstance.get.mockResolvedValueOnce({ data: resp });

    await mod.getExcellentExamples('opening', 5);
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/suggestions/excellent-examples', {
      params: { speech_type: 'opening', limit: 5 },
    });
  });

  it('analyzeAttribution sends POST to /api/attribution/analyze', async () => {
    const resp = { success: true };
    mockAxiosInstance.post.mockResolvedValueOnce({ data: resp });

    const req = { speech_segments: [], emotion_curve: [], danmu_list: [] };
    await mod.analyzeAttribution(req);
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/api/attribution/analyze', req);
  });

  it('getTrendSessions sends GET with limit param', async () => {
    const resp = { success: true, sessions: [] };
    mockAxiosInstance.get.mockResolvedValueOnce({ data: resp });

    await mod.getTrendSessions(5);
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/trends/sessions', { params: { limit: 5 } });
  });

  it('getEmotionTrend joins session IDs with comma', async () => {
    mockAxiosInstance.get.mockResolvedValueOnce({ data: {} });

    await mod.getEmotionTrend(['a', 'b', 'c']);
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/trends/emotion', {
      params: { session_ids: 'a,b,c' },
    });
  });

  it('getFeatures sends GET to /api/features', async () => {
    const resp = { success: true, features: [], groups: [] };
    mockAxiosInstance.get.mockResolvedValueOnce({ data: resp });

    const result = await mod.getFeatures();
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/features');
    expect(result).toEqual(resp);
  });

  it('getHistory extracts items array', async () => {
    mockAxiosInstance.get.mockResolvedValueOnce({
      data: { success: true, items: [{ task_id: '1' }] },
    });
    const result = await mod.getHistory();
    expect(result.items).toEqual([{ task_id: '1' }]);
  });

  it('getHistory falls back to tasks array', async () => {
    mockAxiosInstance.get.mockResolvedValueOnce({
      data: { success: true, tasks: [{ task_id: '2' }] },
    });
    const result = await mod.getHistory();
    expect(result.items).toEqual([{ task_id: '2' }]);
  });

  it('deleteTask sends DELETE to /api/task/:id', async () => {
    mockAxiosInstance.delete.mockResolvedValueOnce({ data: { success: true } });

    await mod.deleteTask('t1');
    expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/api/task/t1');
  });

  it('refreshAuthToken throws when no refresh token', async () => {
    await expect(mod.refreshAuthToken()).rejects.toThrow('No refresh token');
  });

  it('refreshAuthToken sends POST and stores new tokens', async () => {
    localStorage.setItem('refresh_token', 'old-ref');
    const tokens = { access_token: 'new-acc', refresh_token: 'new-ref', token_type: 'Bearer', expires_in: 3600 };
    mockAxiosInstance.post.mockResolvedValueOnce({ data: tokens });

    const result = await mod.refreshAuthToken();
    expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/refresh', { refresh_token: 'old-ref' });
    expect(result).toEqual(tokens);
    expect(localStorage.getItem('access_token')).toBe('new-acc');
  });
});
