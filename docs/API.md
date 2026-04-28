# LiveMirror API

最后更新：2026-04-20

## 基础信息

- Base URL: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- 数据格式：JSON，上传接口使用 `multipart/form-data`
- 认证方式：`Authorization: Bearer <access_token>`

公开接口只有 `/`、`/health` 和 `/auth/*`。所有业务 `/api/**` 默认需要登录态。

## 认证

### 注册

```http
POST /auth/register
```

请求：

```json
{
  "username": "demo",
  "password": "Passw0rd!",
  "email": "demo@example.com"
}
```

### 登录

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

表单字段：`username`、`password`

响应：

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 刷新令牌

```http
POST /auth/refresh
```

```json
{
  "refresh_token": "..."
}
```

### 当前用户

```http
GET /auth/me
```

## 功能注册表

```http
GET /api/features
```

返回当前后端模块清单、启用状态、前端导航入口和健康状态。前端恢复历史页面时，应先让对应模块在这里转为 `enabled: true` 并补齐路由、API 封装、类型和测试。

响应示例：

```json
{
  "success": true,
  "features": [
    {
      "id": "upload",
      "name": "上传分析",
      "group": "core",
      "prefix": "/api/upload",
      "frontend_route": "/upload",
      "navigation_label": "上传",
      "status": "stable",
      "enabled": true,
      "healthy": true
    }
  ],
  "groups": [
    {
      "id": "core",
      "features": []
    }
  ]
}
```

## 上传与任务

### 上传文件

```http
POST /api/upload
Content-Type: multipart/form-data
```

字段：`file`

响应：

```json
{
  "task_id": "uuid-string",
  "filename": "sample.wav",
  "file_size": 12345,
  "status": "pending",
  "message": "Upload accepted. Processing has started."
}
```

### 查询任务

```http
GET /api/task/{task_id}
GET /api/task/{task_id}/progress
```

任务对象包含：

```json
{
  "task_id": "uuid-string",
  "filename": "sample.wav",
  "status": "completed",
  "progress": 100,
  "current_step": "completed",
  "provider": "mock",
  "started_at": "2026-04-20T10:00:00+00:00",
  "completed_at": "2026-04-20T10:00:04+00:00",
  "error_message": null
}
```

`current_step`、`provider`、`started_at` 是向后兼容字段，旧客户端可以忽略。

## 报告与导出

```http
GET /api/report/{task_id}
GET /api/export/{task_id}/json
GET /api/export/{task_id}/markdown
```

报告接口在任务未完成时返回 `success: false` 和当前任务状态；任务失败时返回 400。

## 分析模块

当前已挂载并要求登录：

- `/api/attribution/*`：话术归因、情绪峰值、配置查询
- `/api/suggestions/*`：话术诊断、改写、完整分析、优秀案例、批量分析
- `/api/trends/*`：历史场次、情绪趋势、话术质量趋势、互动趋势、成长报告、场次对比

这些模块仍处于逐个转正阶段。接口名保持兼容，但内部数据源会继续从 mock/示例数据迁移到数据库。

## 状态码

- `200`：成功
- `201`：创建成功
- `400`：请求参数错误或任务状态不满足
- `401`：未登录或令牌无效
- `403`：账号不可用
- `404`：资源不存在
- `500`：服务端错误
