import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
  getUserQuota,
  getUsageRecords,
  getProfile,
  updateProfile as apiUpdateProfile,
  uploadAvatar as apiUploadAvatar,
} from '../api';
import type { UserQuota, UsageRecord, UserProfile } from '../api';

export const useUserStore = defineStore('user', () => {
  const quota = ref<UserQuota | null>(null);
  const usageRecords = ref<UsageRecord[]>([]);
  const profile = ref<UserProfile | null>(null);
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

  async function fetchProfile() {
    const data = await getProfile();
    profile.value = data;
    return data;
  }

  async function updateProfile(data: { nickname?: string; bio?: string }) {
    const updated = await apiUpdateProfile(data);
    profile.value = updated;
    return updated;
  }

  async function uploadAvatar(file: File) {
    const result = await apiUploadAvatar(file);
    if (profile.value) {
      profile.value.avatar_url = result.avatar_url;
    }
    return result;
  }

  return {
    quota,
    usageRecords,
    profile,
    loading,
    fetchQuota,
    fetchUsageRecords,
    fetchProfile,
    updateProfile,
    uploadAvatar,
  };
});
