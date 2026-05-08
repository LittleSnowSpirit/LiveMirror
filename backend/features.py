"""Feature and router registry for the LiveMirror backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


FeatureStatus = Literal["stable", "beta", "disabled"]


@dataclass(frozen=True)
class FeatureDefinition:
    key: str
    label: str
    group: str
    path: str
    router_module: str | None
    enabled: bool
    status: FeatureStatus
    description: str


FEATURES: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        key="auth",
        label="账号认证",
        group="core",
        path="/auth",
        router_module="routes.core_auth",
        enabled=True,
        status="stable",
        description="注册、登录、刷新令牌和当前用户查询。",
    ),
    FeatureDefinition(
        key="upload",
        label="上传分析",
        group="core",
        path="/api/upload",
        router_module="routes.core_upload",
        enabled=True,
        status="stable",
        description="上传音视频文件并创建后台分析任务。",
    ),
    FeatureDefinition(
        key="task",
        label="任务状态",
        group="core",
        path="/api/task",
        router_module="routes.core_tasks",
        enabled=True,
        status="stable",
        description="查询分析任务状态、进度和错误信息。",
    ),
    FeatureDefinition(
        key="report",
        label="报告",
        group="core",
        path="/api/report",
        router_module="routes.core_reports",
        enabled=True,
        status="stable",
        description="查看任务完成后的分析报告。",
    ),
    FeatureDefinition(
        key="export",
        label="导出",
        group="core",
        path="/api/export",
        router_module="routes.core_export",
        enabled=True,
        status="stable",
        description="导出 JSON 和 Markdown 报告。",
    ),
    FeatureDefinition(
        key="attribution",
        label="归因分析",
        group="analysis",
        path="/api/attribution",
        router_module="routes.attribution",
        enabled=True,
        status="beta",
        description="分析话术与情绪、弹幕互动之间的关联。",
    ),
    FeatureDefinition(
        key="suggestions",
        label="话术建议",
        group="analysis",
        path="/api/suggestions",
        router_module="routes.suggestions",
        enabled=True,
        status="beta",
        description="诊断话术问题并生成改写建议。",
    ),
    FeatureDefinition(
        key="trends",
        label="趋势分析",
        group="analysis",
        path="/api/trends",
        router_module="routes.trends",
        enabled=True,
        status="beta",
        description="跨场次趋势与成长报告。",
    ),
    FeatureDefinition(
        key="monitor",
        label="竞品监控",
        group="operations",
        path="/api/monitor",
        router_module="routes.monitor",
        enabled=True,
        status="beta",
        description="竞品直播间监控、告警规则和运营看板数据。",
    ),
)


def enabled_router_modules() -> list[str]:
    return [feature.router_module for feature in FEATURES if feature.enabled and feature.router_module]


def feature_payload() -> dict:
    features = [_feature_to_payload(feature) for feature in FEATURES]
    groups: dict[str, list[dict]] = {}
    for feature in features:
        groups.setdefault(feature["group"], []).append(feature)

    return {
        "success": True,
        "features": features,
        "groups": [{"id": group, "features": items} for group, items in groups.items()],
    }


def _feature_to_payload(feature: FeatureDefinition) -> dict:
    frontend_routes = {
        "upload": "/upload",
        "report": "/report",
        "attribution": "/attribution",
        "suggestions": "/suggestions",
        "trends": "/trends",
        "monitor": "/monitor",
    }
    navigation_labels = {
        "upload": "上传",
        "report": "报告",
        "attribution": "归因",
        "suggestions": "建议",
        "trends": "趋势",
        "monitor": "监控",
    }

    return {
        "id": feature.key,
        "name": feature.label,
        "group": feature.group,
        "prefix": feature.path,
        "frontend_route": frontend_routes.get(feature.key),
        "navigation_label": navigation_labels.get(feature.key),
        "status": feature.status,
        "enabled": feature.enabled,
        "healthy": feature.enabled and bool(feature.router_module),
        "description": feature.description,
    }
