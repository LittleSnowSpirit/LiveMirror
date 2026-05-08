import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { ElMessage } from 'element-plus';

type RetriableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

function normalizeBaseUrl(value: string) {
  return value.trim().replace(/\/+$/, '');
}

const configuredApiBaseUrl = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL || '/api');
export const appBaseUrl = configuredApiBaseUrl.endsWith('/api')
  ? configuredApiBaseUrl.slice(0, -4)
  : configuredApiBaseUrl;
export const apiBaseUrl = `${appBaseUrl || ''}/api`;
export const authBaseUrl = normalizeBaseUrl(import.meta.env.VITE_AUTH_BASE_URL || appBaseUrl);

const api = axios.create({
  baseURL: appBaseUrl || undefined,
  timeout: 300000
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `${localStorage.getItem('token_type') || 'Bearer'} ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableRequestConfig | undefined;
    const status = error.response?.status;
    const url = originalRequest?.url || '';
    const canRefresh = Boolean(
      originalRequest
      && status === 401
      && !originalRequest._retry
      && !url.includes('/auth/login')
      && !url.includes('/auth/register')
      && !url.includes('/auth/refresh')
    );

    if (canRefresh && originalRequest) {
      originalRequest._retry = true;

      try {
        const tokens = await refreshAuthToken();
        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `${tokens.token_type || 'Bearer'} ${tokens.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        handleAuthFailure();
        return Promise.reject(refreshError);
      }
    }

    if (status === 401 && !url.includes('/auth/login') && !url.includes('/auth/register')) {
      handleAuthFailure();
    } else if (!url.includes('/auth/login') && !url.includes('/auth/register')) {
      showApiError(error);
    }

    return Promise.reject(error);
  }
);

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: number;
  username: string;
  nickname: string;
  bio: string;
  avatar_url: string;
  email?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface UploadResponse {
  task_id: string;
  filename: string;
  file_size: number;
  status: string;
  message?: string;
}

export interface SpeechItem {
  id?: string;
  type?: string;
  content?: string;
  text?: string;
  start_time?: number;
  end_time?: number;
  start?: number;
  end?: number;
  [key: string]: unknown;
}

export interface EmotionPoint {
  timestamp: number;
  score: number;
  level?: string;
  [key: string]: unknown;
}

export interface AnalysisResult {
  summary: Record<string, unknown>;
  timeline: Array<Record<string, unknown>>;
  speeches: SpeechItem[];
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: number;
  current_step?: string;
  provider?: string | null;
  started_at?: string | null;
  message?: string;
  error_message?: string | null;
  result?: AnalysisResult;
}

export interface TaskInfo {
  task_id: string;
  filename: string;
  file_size?: number;
  duration?: number | null;
  status: string;
  progress: number;
  current_step?: string;
  provider?: string | null;
  started_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  completed_at?: string | null;
  error_message?: string | null;
}

export interface TaskQueryResponse {
  task: TaskInfo;
}

export interface ReportData {
  task_id: string;
  filename: string;
  duration?: number | null;
  transcription?: string;
  segments?: Array<Record<string, unknown>>;
  speaking_techniques?: Array<Record<string, unknown>>;
  attribution_analysis?: Array<Record<string, unknown>>;
  suggestions?: Array<Record<string, unknown>>;
  summary?: string | Record<string, unknown>;
  summary_text?: string;
  created_at?: string | null;
}

export interface ReportResponse {
  success: boolean;
  data: ReportData;
}

export interface SpeechInput {
  id: string;
  type: string;
  content: string;
  start_time: number;
  end_time: number;
}

export interface MetricsInput {
  emotion_impact?: number;
  engagement_rate?: number;
  overall_score?: number;
}

export interface SuggestionRequest {
  speech: SpeechInput;
  metrics?: MetricsInput;
}

export interface SuggestionAnalysisResponse {
  success: boolean;
  data?: Record<string, unknown>;
  issues?: Array<Record<string, unknown>>;
  rewrite?: Record<string, unknown> | null;
  excellent_examples?: Array<Record<string, unknown>>;
  count?: number;
}

export interface AttributionRequest {
  speech_segments: Array<Record<string, unknown>>;
  emotion_curve: Array<Record<string, unknown>>;
  danmu_list: Array<Record<string, unknown>>;
  top_n?: number;
}

export interface AttributionAnalysisResponse {
  success: boolean;
  message?: string;
  data?: Record<string, unknown>;
}

export interface TrendSession {
  id: string;
  date: string;
  duration_minutes?: number;
  overall_score: number;
  anchor_name?: string;
}

export interface TrendSeriesResponse {
  success: boolean;
  data?: Record<string, unknown>;
  report?: Record<string, unknown>;
  sessions?: TrendSession[];
  total?: number;
}

export interface FeatureInfo {
  id: string;
  name: string;
  group: string;
  prefix: string | null;
  frontend_route: string | null;
  navigation_label: string | null;
  status: string;
  enabled: boolean;
  healthy: boolean;
}

export interface FeatureGroup {
  id: string;
  features: FeatureInfo[];
}

export interface FeatureResponse {
  success: boolean;
  features: FeatureInfo[];
  groups: FeatureGroup[];
}

export interface DanmuBatch {
  batch_id: string;
  filename: string;
  total_count: number;
  success_count: number;
  failed_count: number;
  status: string;
  created_at: string;
}

export interface DanmuBatchDetail extends DanmuBatch {
  items?: Array<Record<string, unknown>>;
}

export interface DanmuAnalysisResult {
  batch_id: string;
  status: string;
  emotion_curve: Array<{ time: number; score: number; count: number; positive: number; negative: number; neutral: number }>;
  keywords: KeywordItem[];
  metrics: {
    total_count: number;
    danmu_density: number;
    sentiment_volatility: number;
    sentiment_distribution: { positive: number; negative: number; neutral: number };
  };
  highlights: Array<{ time: number; count: number; avg_score: number; sample_danmus: string[] }>;
  echarts?: Record<string, unknown>;
  correlation?: CorrelationItem[];
}

export interface KeywordItem {
  word: string;
  count: number;
  sentiment: string;
}

export interface CorrelationItem {
  time: number;
  text: string;
  danmu_count: number;
  danmu_score: number;
}

export interface NotificationItem {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  link?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface LinkInfo {
  platform: string;
  video_id: string;
  title: string;
  duration: number;
  thumbnail_url: string;
  uploader: string;
  error?: string;
}

export interface HistoryItem {
  task_id: string;
  filename: string;
  status: string;
  progress?: number;
  file_size?: number;
  duration?: number | null;
  created_at?: string | null;
  completed_at?: string | null;
  [key: string]: unknown;
}

export interface HistoryParams {
  page?: number;
  page_size?: number;
  status?: string;
  search?: string;
}

export interface HistoryResponse {
  success: boolean;
  items: HistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserQuota {
  weekly_limit: number;
  used_this_week: number;
  remaining: number;
  reset_at: string;
}

export interface UsageRecord {
  id: string;
  task_id: string;
  filename: string;
  created_at: string;
  status: string;
}

export interface ShareLink {
  id: string;
  task_id: string;
  token: string;
  access_code: string;
  template_config: string | null;
  created_at: string;
  expires_at: string | null;
  view_count: number;
}

export interface SharedReportData {
  report: ReportData;
  template_config: string | null;
}

export function setAuthTokens(tokens: AuthTokens) {
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
  localStorage.setItem('token_type', tokens.token_type || 'Bearer');
}

export function clearAuthTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token_type');
}

export function logout() {
  clearAuthTokens();
}

export function getAccessToken() {
  return localStorage.getItem('access_token');
}

export function getToken() {
  return getAccessToken();
}

export function getStoredTaskId() {
  return localStorage.getItem('livemirror:last-task-id') || '';
}

export function setStoredTaskId(taskId: string) {
  if (taskId) {
    localStorage.setItem('livemirror:last-task-id', taskId);
  }
}

export function isAuthenticated() {
  return Boolean(getAccessToken());
}

export async function login(payload: URLSearchParams) {
  const response = await api.post<AuthTokens>('/auth/login', payload, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });

  return response.data;
}

export async function register(payload: { username: string; password: string; email?: string }) {
  const response = await api.post<UserProfile>('/auth/register', payload);
  return response.data;
}

export async function refreshAuthToken() {
  const refreshToken = localStorage.getItem('refresh_token');

  if (!refreshToken) {
    throw new Error('No refresh token is available.');
  }

  const response = await api.post<AuthTokens>('/auth/refresh', {
    refresh_token: refreshToken
  });

  setAuthTokens(response.data);
  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get<UserProfile>('/auth/me');
  return response.data;
}

export async function uploadFile(file: File, onProgress?: (progress: number) => void) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    }
  });

  return response.data;
}

export async function getTaskStatus(taskId: string) {
  const response = await api.get<TaskQueryResponse>(`/api/task/${taskId}`);
  return response.data;
}

export async function getReport(taskId: string) {
  const response = await api.get<ReportResponse>(`/api/report/${taskId}`);
  return response.data;
}

export async function exportReport(taskId: string, format: 'json' | 'markdown') {
  const response = await api.get<Blob>(`/api/export/${taskId}/${format}`, {
    responseType: 'blob'
  });
  return response.data;
}

export async function analyzeSuggestion(request: SuggestionRequest) {
  const response = await api.post<SuggestionAnalysisResponse>('/api/suggestions/analyze', request);
  return response.data;
}

export async function getExcellentExamples(speechType: string, limit = 3) {
  const response = await api.get<Record<string, unknown>>('/api/suggestions/excellent-examples', {
    params: {
      speech_type: speechType,
      limit
    }
  });
  return response.data;
}

export async function analyzeAttribution(request: AttributionRequest) {
  const response = await api.post<AttributionAnalysisResponse>('/api/attribution/analyze', request);
  return response.data;
}

export async function getEmotionPeaks(emotionCurve: Array<Record<string, unknown>>, windowSeconds = 30) {
  const response = await api.post<Record<string, unknown>>('/api/attribution/emotion-peaks', {
    emotion_curve: emotionCurve,
    window_seconds: windowSeconds
  });
  return response.data;
}

export async function getTrendSessions(limit = 10) {
  const response = await api.get<TrendSeriesResponse>('/api/trends/sessions', {
    params: { limit }
  });
  return response.data;
}

export async function getEmotionTrend(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/api/trends/emotion', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export async function getSpeechQualityTrend(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/api/trends/speech-quality', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export async function getEngagementTrend(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/api/trends/engagement', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export async function getGrowthReport(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/api/trends/report', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export async function getFeatures() {
  const response = await api.get<FeatureResponse>('/api/features');
  return response.data;
}

export async function getHistory(params?: HistoryParams) {
  if (params) {
    const response = await api.get<HistoryResponse>('/api/history', { params });
    return response.data;
  }
  const response = await api.get<{ success: boolean; items?: HistoryItem[]; tasks?: HistoryItem[] }>('/api/task');
  return { success: true, items: response.data.items || response.data.tasks || [], total: 0, page: 1, page_size: 20 };
}

export async function deleteTask(taskId: string) {
  const response = await api.delete<Record<string, unknown>>(`/api/task/${taskId}`);
  return response.data;
}

export async function getUserQuota() {
  const response = await api.get<{ success: boolean; quota: UserQuota }>('/api/user/quota');
  return response.data.quota;
}

export async function getUsageRecords() {
  const response = await api.get<{ success: boolean; records: UsageRecord[] }>('/api/user/usage');
  return response.data.records;
}

export async function batchExport(taskIds: string[], format: 'json' | 'markdown') {
  const response = await api.post<Blob>('/api/batch-export', { task_ids: taskIds, format }, {
    responseType: 'blob'
  });
  return response.data;
}

export async function createShareLink(taskId: string, templateConfig?: object, expiresInDays?: number) {
  const response = await api.post<ShareLink>('/api/share', {
    task_id: taskId,
    template_config: templateConfig ? JSON.stringify(templateConfig) : undefined,
    expires_in_days: expiresInDays,
  });
  return response.data;
}

export async function getShareLink(token: string, accessCode: string) {
  const response = await api.get<SharedReportData>(`/api/share/${token}`, {
    params: { access_code: accessCode },
  });
  return response.data;
}

export async function deleteShareLink(token: string) {
  await api.delete(`/api/share/${token}`);
}

export async function getShareLinks() {
  const response = await api.get<{ success: boolean; shares: ShareLink[] }>('/api/share');
  return response.data.shares;
}

export async function getLinkInfo(url: string): Promise<LinkInfo> {
  const { data } = await api.get('/api/link-info', { params: { url } });
  return data;
}

export async function analyzeLink(url: string): Promise<{ task_id: string }> {
  const { data } = await api.post('/api/analyze-link', { url });
  return data;
}

export async function getNotifications(params: { page?: number; page_size?: number; unread_only?: boolean; type?: string }) {
  const response = await api.get<{ notifications: NotificationItem[]; total: number; unread_count: number }>('/api/notifications', { params });
  return response.data;
}

export async function getUnreadCount() {
  const response = await api.get<{ unread_count: number }>('/api/notifications/unread-count');
  return response.data.unread_count;
}

export async function markNotificationsRead(ids: number[]) {
  await api.post('/api/notifications/mark-read', { ids });
}

export async function markAllNotificationsRead() {
  await api.post('/api/notifications/mark-all-read');
}

export async function deleteNotification(id: number) {
  await api.delete(`/api/notifications/${id}`);
}

export async function getVapidKey() {
  const response = await api.get<{ public_key: string }>('/api/notifications/vapid-public-key');
  return response.data.public_key;
}

export async function pushSubscribe(subscription: { endpoint: string; keys: { p256dh: string; auth: string } }) {
  await api.post('/api/notifications/push-subscribe', subscription);
}

export async function pushUnsubscribe(endpoint: string) {
  await api.delete('/api/notifications/push-unsubscribe', { data: { endpoint } });
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export async function exportPDF(taskId: string, template?: string) {
  const params: Record<string, string> = {};
  if (template) params.template = template;
  const response = await api.get<Blob>(`/api/export/${taskId}/pdf`, {
    responseType: 'blob',
    params,
  });
  downloadBlob(response.data, `livemirror-report-${taskId}.pdf`);
}

export async function exportImage(taskId: string) {
  const response = await api.get<Blob>(`/api/export/${taskId}/image`, {
    responseType: 'blob',
  });
  downloadBlob(response.data, `livemirror-report-${taskId}.png`);
}

export async function uploadAvatar(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<{ avatar_url: string }>('/api/user/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function updateProfile(data: { nickname?: string; bio?: string }) {
  const response = await api.put<UserProfile>('/api/user/profile', data);
  return response.data;
}

export async function getProfile() {
  const response = await api.get<UserProfile>('/api/user/profile');
  return response.data;
}

export async function uploadDanmuFile(file: File, onProgress?: (progress: number) => void) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<{ batch_id: string; total_count: number; success_count: number; failed_count: number }>(
    '/api/danmu/upload',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress(Math.round((event.loaded * 100) / event.total));
        }
      },
    }
  );

  return response.data;
}

export async function getDanmuBatches() {
  const response = await api.get<{ success: boolean; batches: DanmuBatch[] }>('/api/danmu/batches');
  return response.data.batches;
}

export async function getDanmuBatchDetail(batchId: string) {
  const response = await api.get<DanmuBatchDetail>(`/api/danmu/batch/${batchId}`);
  return response.data;
}

export async function triggerDanmuAnalysis(batchId: string) {
  await api.post(`/api/danmu/batch/${batchId}/analyze`);
}

export async function getDanmuAnalysis(batchId: string) {
  const response = await api.get<DanmuAnalysisResult>(`/api/danmu/analysis/${batchId}`);
  return response.data;
}

export async function getDanmuKeywords(batchId: string) {
  const response = await api.get<{ success: boolean; keywords: KeywordItem[] }>(`/api/danmu/analysis/${batchId}/keywords`);
  return response.data.keywords;
}

export async function getDanmuCorrelation(batchId: string, taskId: string) {
  const response = await api.get<{ success: boolean; correlation: CorrelationItem[] }>(`/api/danmu/analysis/${batchId}/correlation?task_id=${taskId}`);
  return response.data.correlation;
}

function handleAuthFailure() {
  clearAuthTokens();

  if (typeof window === 'undefined') {
    return;
  }

  const currentPath = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  const isAuthPage = currentPath.startsWith('/login') || currentPath.startsWith('/register');
  const redirect = isAuthPage ? '' : `?redirect=${encodeURIComponent(currentPath)}`;
  window.location.assign(`/login${redirect}`);
}

function showApiError(error: AxiosError) {
  const message = extractErrorMessage(error);

  if (message) {
    ElMessage.error(message);
  }
}

function extractErrorMessage(error: AxiosError) {
  const data = error.response?.data as { detail?: unknown; message?: unknown } | undefined;
  const detail = data?.detail ?? data?.message;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => {
      if (typeof item === 'string') {
        return item;
      }
      if (item && typeof item === 'object' && 'msg' in item) {
        return String(item.msg);
      }
      return String(item);
    }).join('; ');
  }

  if (error.message) {
    return error.message;
  }

  return 'Request failed.';
}

export default api;
