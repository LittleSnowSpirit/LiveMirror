import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { nextTick } from 'vue';

const mockGetLinkInfo = vi.fn();
const mockAnalyzeLink = vi.fn();
const mockGetTaskStatus = vi.fn();
const mockSetStoredTaskId = vi.fn();
const mockElMessage = { warning: vi.fn(), success: vi.fn(), error: vi.fn() };

vi.mock('../api', () => ({
  getLinkInfo: (...args: unknown[]) => mockGetLinkInfo(...args),
  analyzeLink: (...args: unknown[]) => mockAnalyzeLink(...args),
  getTaskStatus: (...args: unknown[]) => mockGetTaskStatus(...args),
  setStoredTaskId: (...args: unknown[]) => mockSetStoredTaskId(...args),
}));

vi.mock('element-plus', () => ({
  ElMessage: mockElMessage,
  ElInput: {
    template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ['modelValue', 'placeholder', 'size', 'clearable', 'disabled'],
    emits: ['update:modelValue', 'input'],
  },
  ElButton: {
    template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /></button>',
    props: ['type', 'size', 'disabled', 'loading'],
    emits: ['click'],
  },
  ElAlert: {
    template: '<div>{{ title }}</div>',
    props: ['title', 'type', 'closable', 'showIcon'],
    emits: ['close'],
  },
  ElProgress: {
    template: '<div>{{ percentage }}</div>',
    props: ['percentage', 'strokeWidth', 'status'],
  },
}));

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/report/:taskId?', name: 'report', component: { template: '<div />' } },
  ],
});

async function mountLinkInput() {
  const { default: LinkInput } = await import('./LinkInput.vue');
  return mount(LinkInput, {
    global: {
      plugins: [router],
    },
  });
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
});

describe('LinkInput.vue', () => {
  it('renders URL input and paste button', async () => {
    const wrapper = await mountLinkInput();
    expect(wrapper.find('input').exists()).toBe(true);
    expect(wrapper.text()).toContain('粘贴');
  });

  it('shows platform tag for douyin URL', async () => {
    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://www.douyin.com/video/123456');
    await nextTick();
    expect(wrapper.text()).toContain('抖音');
    expect(wrapper.find('.platform-tag.douyin').exists()).toBe(true);
  });

  it('shows platform tag for bilibili URL', async () => {
    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://www.bilibili.com/video/BV12345');
    await nextTick();
    expect(wrapper.text()).toContain('B站');
    expect(wrapper.find('.platform-tag.bilibili').exists()).toBe(true);
  });

  it('does not show platform tag for unknown URL', async () => {
    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://example.com/video');
    await nextTick();
    expect(wrapper.find('.platform-tag').exists()).toBe(false);
  });

  it('calls getLinkInfo on preview button click', async () => {
    mockGetLinkInfo.mockResolvedValueOnce({
      platform: 'douyin',
      video_id: '123',
      title: '测试视频',
      duration: 120,
      thumbnail_url: 'https://example.com/thumb.jpg',
      uploader: '主播A',
    });

    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://www.douyin.com/video/123456');
    await nextTick();

    const buttons = wrapper.findAll('button');
    const previewBtn = buttons.find((b) => b.text().includes('解析链接'));
    await previewBtn!.trigger('click');

    await vi.waitFor(() => {
      expect(mockGetLinkInfo).toHaveBeenCalledWith('https://www.douyin.com/video/123456');
    });
  });

  it('renders preview card after successful link info', async () => {
    mockGetLinkInfo.mockResolvedValueOnce({
      platform: 'douyin',
      video_id: '123',
      title: '直播回放：带货专场',
      duration: 3660,
      thumbnail_url: 'https://example.com/thumb.jpg',
      uploader: '带货主播',
    });

    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://www.douyin.com/video/123456');
    await nextTick();

    const buttons = wrapper.findAll('button');
    const previewBtn = buttons.find((b) => b.text().includes('解析链接'));
    await previewBtn!.trigger('click');

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('直播回放：带货专场');
      expect(wrapper.text()).toContain('带货主播');
      expect(wrapper.text()).toContain('61分0秒');
      expect(wrapper.text()).toContain('开始分析');
    });
  });

  it('shows error on link info failure', async () => {
    mockGetLinkInfo.mockRejectedValueOnce({
      response: { data: { detail: '不支持的链接格式' } },
    });

    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://example.com/video');
    await nextTick();

    const buttons = wrapper.findAll('button');
    const previewBtn = buttons.find((b) => b.text().includes('解析链接'));
    await previewBtn!.trigger('click');

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('不支持的链接格式');
    });
  });

  it('calls analyzeLink on start analysis click', async () => {
    mockGetLinkInfo.mockResolvedValueOnce({
      platform: 'bilibili',
      video_id: 'BV123',
      title: 'B站直播',
      duration: 600,
      thumbnail_url: '',
      uploader: 'UP主',
    });
    mockAnalyzeLink.mockResolvedValueOnce({ task_id: 'task-abc' });
    mockGetTaskStatus.mockResolvedValue({
      task: { task_id: 'task-abc', status: 'completed', progress: 100 },
    });

    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://www.bilibili.com/video/BV123');
    await nextTick();

    const buttons = wrapper.findAll('button');
    const previewBtn = buttons.find((b) => b.text().includes('解析链接'));
    await previewBtn!.trigger('click');

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('开始分析');
    });

    const analyzeBtn = wrapper.findAll('button').find((b) => b.text().includes('开始分析'));
    await analyzeBtn!.trigger('click');

    await vi.waitFor(() => {
      expect(mockAnalyzeLink).toHaveBeenCalledWith('https://www.bilibili.com/video/BV123');
      expect(mockSetStoredTaskId).toHaveBeenCalledWith('task-abc');
    });

    vi.advanceTimersByTime(3000);
    await vi.waitFor(() => {
      expect(mockGetTaskStatus).toHaveBeenCalledWith('task-abc');
    });
  });

  it('shows progress steps during analysis', async () => {
    mockGetLinkInfo.mockResolvedValueOnce({
      platform: 'douyin',
      video_id: '123',
      title: '测试',
      duration: 60,
      thumbnail_url: '',
      uploader: '主播',
    });
    mockAnalyzeLink.mockResolvedValueOnce({ task_id: 'task-xyz' });
    mockGetTaskStatus.mockResolvedValue({
      task: { task_id: 'task-xyz', status: 'transcribing', progress: 50 },
    });

    const wrapper = await mountLinkInput();
    const input = wrapper.find('input');
    await input.setValue('https://www.douyin.com/video/123');
    await nextTick();

    // Preview first
    const buttons = wrapper.findAll('button');
    const previewBtn = buttons.find((b) => b.text().includes('解析链接'));
    await previewBtn!.trigger('click');

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('开始分析');
    });

    // Start analysis
    const analyzeBtn = wrapper.findAll('button').find((b) => b.text().includes('开始分析'));
    await analyzeBtn!.trigger('click');

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('下载中');
      expect(wrapper.text()).toContain('转写中');
      expect(wrapper.text()).toContain('分析中');
      expect(wrapper.text()).toContain('完成');
    });
  });
});
