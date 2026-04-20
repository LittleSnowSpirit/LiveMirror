/**
 * 模拟 API 响应（用于演示）
 */

import type { UploadResponse, AnalysisResult, TaskStatus } from './index'

// 模拟的直播话术分析结果
const MOCK_ANALYSIS: AnalysisResult = {
  summary: {
    totalDuration: 96,
    totalSpeeches: 15,
    avgEmotion: 0.65,
    highlightCount: 5,
    issueCount: 3,
  },
  timeline: [
    { timestamp: 0, emotion: 0.5, label: '开场' },
    { timestamp: 10, emotion: 0.7, label: '产品介绍' },
    { timestamp: 20, emotion: 0.8, label: '价格公布' },
    { timestamp: 30, emotion: 0.6, label: '互动环节' },
    { timestamp: 40, emotion: 0.9, label: '促单' },
    { timestamp: 50, emotion: 0.75, label: '使用演示' },
    { timestamp: 60, emotion: 0.85, label: '买家秀' },
    { timestamp: 70, emotion: 0.95, label: '限时优惠' },
    { timestamp: 80, emotion: 0.7, label: '答疑' },
    { timestamp: 90, emotion: 0.9, label: '倒计时' },
  ],
  speeches: [
    {
      id: '1',
      timestamp: 0,
      duration: 10,
      content: '欢迎宝宝们来到直播间！今天是我们的年度大促，全场五折起！',
      type: 'normal',
      emotion: 0.5,
      tags: ['开场白', '欢迎'],
    },
    {
      id: '2',
      timestamp: 10,
      duration: 15,
      content: '首先给大家介绍一下我们今天的爆款一号链接，这个产品我自己已经用了三个月了，效果真的非常好。原价 299，今天直播间只要 99 元！',
      type: 'highlight',
      emotion: 0.8,
      tags: ['产品介绍', '价格优惠'],
      suggestion: '可以增加更多使用细节',
    },
    {
      id: '3',
      timestamp: 25,
      duration: 10,
      content: '来，我给大家展示一下。你们看这个质地，非常细腻，涂在脸上很服帖。',
      type: 'normal',
      emotion: 0.7,
      tags: ['产品展示'],
    },
    {
      id: '4',
      timestamp: 35,
      duration: 8,
      content: '宝宝们，这个库存只有 500 单，抢完就没有了。',
      type: 'highlight',
      emotion: 0.85,
      tags: ['促单', '稀缺性'],
    },
    {
      id: '5',
      timestamp: 43,
      duration: 12,
      content: '现在下单还送价值 199 元的赠品，包括面膜、精华小样。',
      type: 'highlight',
      emotion: 0.9,
      tags: ['赠品', '促单'],
    },
    {
      id: '6',
      timestamp: 55,
      duration: 10,
      content: '有宝宝问敏感肌能不能用，可以的，我们这个是温和配方，敏感肌放心拍。',
      type: 'normal',
      emotion: 0.6,
      tags: ['答疑', '互动'],
    },
    {
      id: '7',
      timestamp: 65,
      duration: 15,
      content: '我给大家演示一下：第一步，洁面之后，取适量涂抹在脸上；第二步，轻轻按摩至吸收；第三步，再涂上面霜锁住水分。',
      type: 'highlight',
      emotion: 0.75,
      tags: ['使用教学'],
    },
    {
      id: '8',
      timestamp: 80,
      duration: 10,
      content: '现在下单的宝宝，我们再加赠一片面膜。但是只有前 100 单有这个福利，抓紧时间！',
      type: 'highlight',
      emotion: 0.95,
      tags: ['限时优惠', '促单'],
    },
    {
      id: '9',
      timestamp: 90,
      duration: 6,
      content: '来，倒计时 5 个数，5、4、3、2、1，上链接！',
      type: 'normal',
      emotion: 0.9,
      tags: ['倒计时', '成交'],
    },
  ],
}

// 模拟延迟
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export async function mockUpload(file: File): Promise<UploadResponse> {
  await delay(1000) // 模拟 1 秒上传时间
  
  return {
    task_id: `mock-${Date.now()}`,
    filename: file.name,
    file_size: file.size,
    status: 'completed',
    message: '上传成功',
  }
}

export async function mockGetTaskStatus(taskId: string): Promise<TaskStatus> {
  await delay(500) // 模拟 0.5 秒延迟
  
  // 模拟任务进度
  if (taskId.includes('mock')) {
    return {
      task_id: taskId,
      status: 'completed',
      progress: 100,
      message: '分析完成',
      result: MOCK_ANALYSIS,
    }
  }
  
  return {
    task_id: taskId,
    status: 'pending',
    progress: 0,
  }
}

export async function mockGetAnalysisResult(_taskId: string): Promise<AnalysisResult> {
  return MOCK_ANALYSIS
  await delay(1000) // 模拟 1 秒延迟
  return MOCK_ANALYSIS
}
