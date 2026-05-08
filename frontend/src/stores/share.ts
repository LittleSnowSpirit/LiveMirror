import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
  createShareLink as apiCreateShareLink,
  getShareLinks as apiGetShareLinks,
  deleteShareLink as apiDeleteShareLink,
} from '../api';
import type { ShareLink } from '../api';

export const useShareStore = defineStore('share', () => {
  const shares = ref<ShareLink[]>([]);
  const loading = ref(false);

  async function fetchShares() {
    loading.value = true;
    try {
      shares.value = await apiGetShareLinks();
    } finally {
      loading.value = false;
    }
  }

  async function createShare(taskId: string, templateConfig?: object, expiresInDays?: number) {
    const share = await apiCreateShareLink(taskId, templateConfig, expiresInDays);
    shares.value.unshift(share);
    return share;
  }

  async function removeShare(token: string) {
    await apiDeleteShareLink(token);
    shares.value = shares.value.filter((s) => s.token !== token);
  }

  return { shares, loading, fetchShares, createShare, removeShare };
});
