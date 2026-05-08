import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getHistory, deleteTask, batchExport as apiBatchExport } from '../api';
import type { HistoryItem, HistoryParams } from '../api';

export interface TaskItem {
  task_id: string;
  filename: string;
  status: 'pending' | 'transcribing' | 'analyzing' | 'completed' | 'failed';
  progress: number;
  file_size: number;
  duration: number | null;
  created_at: string;
  completed_at: string | null;
}

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<TaskItem[]>([]);
  const loading = ref(false);
  const total = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  function mapItem(item: HistoryItem): TaskItem {
    return {
      task_id: item.task_id,
      filename: item.filename,
      status: (item.status || 'pending') as TaskItem['status'],
      progress: item.progress ?? 0,
      file_size: (item.file_size as number) ?? 0,
      duration: (item.duration as number) ?? null,
      created_at: item.created_at ?? '',
      completed_at: item.completed_at ?? null,
    };
  }

  async function fetchTasks(params?: HistoryParams) {
    loading.value = true;
    try {
      const response = await getHistory(params);
      tasks.value = response.items.map(mapItem);
      total.value = response.total;
      if (response.page) currentPage.value = response.page;
      if (response.page_size) pageSize.value = response.page_size;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTaskItem(taskId: string) {
    await deleteTask(taskId);
    tasks.value = tasks.value.filter((t) => t.task_id !== taskId);
    total.value = Math.max(0, total.value - 1);
  }

  async function batchExport(taskIds: string[], format: 'json' | 'markdown') {
    return apiBatchExport(taskIds, format);
  }

  return { tasks, loading, total, currentPage, pageSize, fetchTasks, deleteTaskItem, batchExport };
});
