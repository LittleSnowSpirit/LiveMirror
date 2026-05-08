# P0-1：数据持久化 + 用户配额

## 需求概述

将当前 SQLite + 内存队列的存储方案升级为 PostgreSQL + Redis + Celery，实现数据持久化和用户配额管理。新增独立的历史任务页面和个人中心页面。

## 用户需求

| 需求 | 决策 |
|------|------|
| 功能范围 | 持久化 + 配额（历史数据 + 每月配额管理） |
| 历史页面 | 独立历史页，卡片列表布局 |
| 任务状态 | 详细状态（排队中/转写中/分析中/已完成/失败）+ 进度百分比 + 预计剩余时间 |
| 配额提示 | 个人中心页面显示用量详情 |
| 历史操作 | 查看报告、删除任务、批量导出 |
| 配额规则 | 每周 2 次免费分析 |
| 历史保留 | 保留 3 个月，更早的自动清理 |
| 影响范围 | 可能有影响，需要重新测试 |
| 开发时间 | 3-5 天 |
| 部署方式 | 先本地开发，后续部署到服务器 |

## 技术方案（Lead 决策）

| 技术 | 选择 | 理由 |
|------|------|------|
| 数据库 | PostgreSQL | 用户选择，生产级数据库 |
| 缓存/队列 | Redis | 任务队列 + 结果缓存 |
| 任务队列 | Celery + Redis broker | 成熟方案，支持重试、监控 |
| 前端状态 | Pinia | Vue 3 标准状态管理 |
| 迁移工具 | Alembic | 已在项目中使用 |
| 数据迁移 | 全新开始 | 开发环境无重要数据 |
| 部署 | Docker Compose | 包含 backend + PostgreSQL + Redis |

## 功能清单

### 1. 后端改造

#### 1.1 数据库切换
- `config.py`：支持 `DATABASE_URL` 环境变量，默认 `postgresql://...`
- `database.py`：移除 SQLite 特定逻辑（pragmas、check_same_thread、StaticPool）
- `requirements.txt`：添加 `psycopg2-binary`、`celery[redis]`、`redis`

#### 1.2 数据模型重新设计
- `models.py`：重新审视所有模型
  - Task：JSON 字段改用 JSONB，添加 `user_id` 外键、`created_at` 索引
  - 新增 `UserQuota` 模型：记录用户每周使用量
  - 新增 `UsageRecord` 模型：记录每次分析的使用记录
  - 优化索引和关系

#### 1.3 任务队列改造
- `services/task_queue.py`：用 Celery 替换 ThreadPoolExecutor
- 任务状态持久化到数据库
- 支持任务重试（失败自动重试 3 次）

#### 1.4 Redis 缓存
- 缓存分析结果（TTL 1 小时）
- 缓存用户配额信息

#### 1.5 路由修复
- 所有路由改用 FastAPI `Depends(get_db)` 依赖注入
- 新增 `/api/history` 路由（任务历史列表）
- 新增 `/api/user/quota` 路由（用户配额信息）
- 新增 `/api/user/usage` 路由（使用记录）

### 2. 前端改造

#### 2.1 状态管理
- 新增 `stores/task.ts`：Pinia store 管理任务列表
- 新增 `stores/user.ts`：Pinia store 管理用户信息和配额

#### 2.2 历史页面
- 新增 `views/History.vue`：独立历史任务页面
  - 卡片列表布局
  - 显示：文件名、状态（带颜色标签）、进度条、创建时间、时长
  - 操作：查看报告、删除任务、批量导出
  - 筛选：按状态筛选、搜索文件名
- 路由：`/history`，需要认证

#### 2.3 个人中心页面
- 新增 `views/Profile.vue`：用户个人中心
  - 显示用户信息
  - 显示本周配额：已用 X/2 次，下次重置时间
  - 显示使用记录列表
- 路由：`/profile`，需要认证

#### 2.4 API 客户端更新
- `api/index.ts`：新增以下 API 调用
  - `getHistory(params)`：获取历史任务列表（支持分页、筛选）
  - `deleteTask(taskId)`：已有，确认可用
  - `batchExport(taskIds, format)`：批量导出
  - `getUserQuota()`：获取用户配额
  - `getUsageRecords()`：获取使用记录

#### 2.5 导航更新
- `App.vue`：导航栏添加"历史记录"和"个人中心"入口

### 3. 基建改造

#### 3.1 Docker Compose
- 新增 `docker-compose.yml`：
  - `backend` 服务（FastAPI）
  - `postgres` 服务（PostgreSQL 15）
  - `redis` 服务（Redis 7）
  - `celery-worker` 服务
  - `frontend` 服务（Nginx 静态文件）

#### 3.2 环境配置
- 新增 `.env.example`：所有环境变量模板
- 配置项：DATABASE_URL、REDIS_URL、SECRET_KEY、CORS_ORIGINS

#### 3.3 Alembic 迁移
- 初始化 PostgreSQL 迁移脚本
- 包含所有表的创建

## API 合约

### GET /api/history

```
请求参数：
  page: number (默认 1)
  page_size: number (默认 20)
  status: string (可选，筛选状态)
  search: string (可选，搜索文件名)

响应：
{
  "success": true,
  "items": [
    {
      "task_id": "string",
      "filename": "string",
      "status": "pending|transcribing|analyzing|completed|failed",
      "progress": 0-100,
      "file_size": number,
      "duration": number,
      "created_at": "ISO8601",
      "completed_at": "ISO8601|null"
    }
  ],
  "total": number,
  "page": number,
  "page_size": number
}
```

### GET /api/user/quota

```
响应：
{
  "success": true,
  "quota": {
    "weekly_limit": 2,
    "used_this_week": 1,
    "remaining": 1,
    "reset_at": "ISO8601"
  }
}
```

### POST /api/batch-export

```
请求体：
{
  "task_ids": ["string"],
  "format": "json|markdown"
}

响应：ZIP 文件（包含多个报告文件）
```

## 验收标准

1. 后端测试通过（`python3 -m pytest tests/ -v`）
2. 前端测试通过（`npm run test`）
3. 类型检查通过（`npm run typecheck`）
4. 构建成功（`npm run build`）
5. Docker Compose 一键启动成功
6. 上传文件 → 查看历史 → 查看报告 → 删除任务 全流程可用
7. 配额限制生效：每周超过 2 次提示"已达本周上限"
8. 移动端（PWA）页面显示正常
