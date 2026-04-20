import axios from 'axios';

export const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL?.trim() || '/api').replace(/\/+$/, '') || '/api';
export const authBaseUrl = (
  import.meta.env.VITE_AUTH_BASE_URL?.trim()
  || (apiBaseUrl.endsWith('/api') ? apiBaseUrl.slice(0, -4) : '')
).replace(/\/+$/, '');

const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 300000
});

const authApi = axios.create({
  baseURL: authBaseUrl || undefined,
  timeout: 300000
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `${localStorage.getItem('token_type') || 'Bearer'} ${token}`;
  }

  return config;
});

authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `${localStorage.getItem('token_type') || 'Bearer'} ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
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

export interface AnalysisResult {
  summary: Record<string, unknown>;
  timeline: Array<Record<string, unknown>>;
  speeches: Array<Record<string, unknown>>;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: number;
  message?: string;
  result?: AnalysisResult;
}

export interface TaskInfo {
  task_id: string;
  filename: string;
  file_size?: number;
  duration?: number | null;
  status: string;
  progress: number;
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

export function getStoredTaskId() {
  return localStorage.getItem('livemirror:last-task-id') || '';
}

export function setStoredTaskId(taskId: string) {
  if (taskId) {
    localStorage.setItem('livemirror:last-task-id', taskId);
  }
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('access_token'));
}

export async function login(payload: URLSearchParams) {
  const response = await authApi.post<AuthTokens>('/auth/login', payload, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });

  return response.data;
}

export async function register(payload: { username: string; password: string; email?: string }) {
  const response = await authApi.post<UserProfile>('/auth/register', payload);
  return response.data;
}

export async function getCurrentUser() {
  const response = await authApi.get<UserProfile>('/auth/me');
  return response.data;
}

export async function uploadFile(file: File, onProgress?: (progress: number) => void) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/upload', formData, {
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
  const response = await api.get<TaskQueryResponse>(`/task/${taskId}`);
  return response.data;
}

export async function getReport(taskId: string) {
  const response = await api.get<ReportResponse>(`/report/${taskId}`);
  return response.data;
}

export async function exportReport(taskId: string, format: 'json' | 'markdown') {
  const response = await api.get<Blob>(`/export/${taskId}/${format}`, {
    responseType: 'blob'
  });
  return response.data;
}

export async function analyzeSuggestion(request: SuggestionRequest) {
  const response = await api.post<SuggestionAnalysisResponse>('/suggestions/analyze', request);
  return response.data;
}

export async function getExcellentExamples(speechType: string, limit = 3) {
  const response = await api.get<Record<string, unknown>>('/suggestions/excellent-examples', {
    params: {
      speech_type: speechType,
      limit
    }
  });
  return response.data;
}

export async function analyzeAttribution(request: AttributionRequest) {
  const response = await api.post<AttributionAnalysisResponse>('/attribution/analyze', request);
  return response.data;
}

export async function getEmotionPeaks(emotionCurve: Array<Record<string, unknown>>, windowSeconds = 30) {
  const response = await api.post<Record<string, unknown>>('/attribution/emotion-peaks', {
    emotion_curve: emotionCurve,
    window_seconds: windowSeconds
  });
  return response.data;
}

export async function getTrendSessions(limit = 10) {
  const response = await api.get<TrendSeriesResponse>('/trends/sessions', {
    params: { limit }
  });
  return response.data;
}

export async function getEmotionTrend(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/trends/emotion', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export async function getSpeechQualityTrend(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/trends/speech-quality', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export async function getEngagementTrend(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/trends/engagement', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export async function getGrowthReport(sessionIds: string[]) {
  const response = await api.get<Record<string, unknown>>('/trends/report', {
    params: { session_ids: sessionIds.join(',') }
  });
  return response.data;
}

export default api;
