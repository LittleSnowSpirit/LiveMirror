import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getUserQuota, getUsageRecords } from '../api';
import type { UserQuota, UsageRecord } from '../api';

export const useUserStore = defineStore('user', () => {
  const quota = ref<UserQuota | null>(null);
  const usageRecords = ref<UsageRecord[]>([]);
  const loading = ref(false);

  async function fetchQuota() {
    const data = await getUserQuota();
    quota.value = data;
  }

  async function fetchUsageRecords() {
    loading.value = true;
    try {
      const data = await getUsageRecords();
      usageRecords.value = data;
    } finally {
      loading.value = false;
    }
  }

  return { quota, usageRecords, loading, fetchQuota, fetchUsageRecords };
});
