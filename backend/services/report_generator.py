"""
数据报表生成服务 - LiveMirror
支持日报/周报/月报自动生成、关键指标汇总、趋势分析、PDF/Excel 导出
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
import csv


class ReportType(Enum):
    """报表类型"""
    DAILY = "daily"      # 日报
    WEEKLY = "weekly"    # 周报
    MONTHLY = "monthly"  # 月报


class ExportFormat(Enum):
    """导出格式"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    CSV = "csv"


@dataclass
class ReportMetric:
    """报表指标"""
    name: str
    value: Any
    unit: str = ""
    change_rate: Optional[float] = None  # 环比变化率
    trend: str = "stable"  # up, down, stable


@dataclass
class ReportSection:
    """报表章节"""
    title: str
    metrics: List[ReportMetric]
    summary: str = ""


@dataclass
class ReportData:
    """报表数据"""
    report_id: str
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    sections: List[ReportSection]
    overall_summary: str = ""


class ReportGeneratorService:
    """报表生成服务"""
    
    def __init__(self, data_dir: str = "data/reports", template_dir: str = "backend/templates/report"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # 报表存储路径
        self.reports_path = self.data_dir / "reports.json"
        self.templates_path = self.data_dir / "templates.json"
        self.schedule_path = self.data_dir / "schedules.json"
        
        # 内存数据
        self.reports: Dict[str, Dict] = {}
        self.templates: Dict[str, Dict] = {}
        self.schedules: List[Dict] = []
        
        # 加载数据
        self._load_reports()
        self._load_templates()
        self._load_schedules()
        
        # 初始化默认模板
        if not self.templates:
            self._init_default_templates()
    
    def _load_reports(self):
        """加载报表历史"""
        if self.reports_path.exists():
            with open(self.reports_path, "r", encoding="utf-8") as f:
                self.reports = json.load(f)
    
    def _save_reports(self):
        """保存报表历史"""
        with open(self.reports_path, "w", encoding="utf-8") as f:
            json.dump(self.reports, f, ensure_ascii=False, indent=2)
    
    def _load_templates(self):
        """加载自定义模板"""
        if self.templates_path.exists():
            with open(self.templates_path, "r", encoding="utf-8") as f:
                self.templates = json.load(f)
    
    def _save_templates(self):
        """保存自定义模板"""
        with open(self.templates_path, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)
    
    def _load_schedules(self):
        """加载定时任务"""
        if self.schedule_path.exists():
            with open(self.schedule_path, "r", encoding="utf-8") as f:
                self.schedules = json.load(f)
    
    def _save_schedules(self):
        """保存定时任务"""
        with open(self.schedule_path, "w", encoding="utf-8") as f:
            json.dump(self.schedules, f, ensure_ascii=False, indent=2)
    
    def _init_default_templates(self):
        """初始化默认报表模板"""
        default_templates = {
            "daily_standard": {
                "name": "日报标准模板",
                "type": "daily",
                "sections": [
                    {
                        "title": "核心指标",
                        "metrics": ["gmv", "view_count", "conversion_rate", "avg_watch_time"]
                    },
                    {
                        "title": "流量分析",
                        "metrics": ["pv", "uv", "new_followers", "engagement_rate"]
                    },
                    {
                        "title": "转化分析",
                        "metrics": ["click_count", "order_count", "refund_rate", "customer_satisfaction"]
                    }
                ],
                "is_default": True
            },
            "weekly_summary": {
                "name": "周报汇总模板",
                "type": "weekly",
                "sections": [
                    {
                        "title": "周度核心指标",
                        "metrics": ["gmv", "view_count", "conversion_rate", "avg_watch_time"]
                    },
                    {
                        "title": "趋势对比",
                        "metrics": ["gmom_gmv", "gmom_views", "gmom_conversion"]
                    },
                    {
                        "title": "TOP 分析",
                        "metrics": ["top_products", "top_streamers", "peak_hours"]
                    }
                ],
                "is_default": True
            },
            "monthly_overview": {
                "name": "月报总览模板",
                "type": "monthly",
                "sections": [
                    {
                        "title": "月度核心指标",
                        "metrics": ["gmv", "view_count", "conversion_rate", "revenue"]
                    },
                    {
                        "title": "月度趋势",
                        "metrics": ["daily_gmv_trend", "daily_views_trend", "conversion_trend"]
                    },
                    {
                        "title": "目标达成",
                        "metrics": ["gmv_target_rate", "view_target_rate", "growth_rate"]
                    }
                ],
                "is_default": True
            }
        }
        
        self.templates = default_templates
        self._save_templates()
    
    def _get_mock_data(self, report_type: ReportType, start_date: datetime, end_date: datetime) -> Dict:
        """获取模拟数据（实际应连接数据库或 API）"""
        import random
        
        days = (end_date - start_date).days + 1
        
        # 根据报表类型调整数据范围
        if report_type == ReportType.DAILY:
            base_gmv = random.uniform(50000, 150000)
            base_views = random.uniform(100000, 300000)
        elif report_type == ReportType.WEEKLY:
            base_gmv = random.uniform(400000, 900000)
            base_views = random.uniform(800000, 2000000)
        else:  # MONTHLY
            base_gmv = random.uniform(1500000, 4000000)
            base_views = random.uniform(3000000, 8000000)
        
        # 生成每日数据
        daily_data = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            daily_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "gmv": base_gmv * random.uniform(0.8, 1.2),
                "view_count": base_views * random.uniform(0.8, 1.2),
                "conversion_rate": random.uniform(0.02, 0.05),
                "avg_watch_time": random.uniform(120, 300),
                "pv": base_views * random.uniform(1.5, 2.5),
                "uv": base_views * random.uniform(0.6, 0.9),
                "new_followers": random.randint(100, 1000),
                "engagement_rate": random.uniform(0.05, 0.15),
                "click_count": random.randint(5000, 20000),
                "order_count": random.randint(500, 2000),
                "refund_rate": random.uniform(0.01, 0.05),
                "customer_satisfaction": random.uniform(4.2, 4.9)
            })
        
        # 计算汇总数据
        total_gmv = sum(d["gmv"] for d in daily_data)
        total_views = sum(d["view_count"] for d in daily_data)
        avg_conversion = sum(d["conversion_rate"] for d in daily_data) / len(daily_data)
        avg_watch_time = sum(d["avg_watch_time"] for d in daily_data) / len(daily_data)
        
        # 计算环比（与上一个周期对比）
        if report_type == ReportType.DAILY:
            prev_period_gmv = total_gmv * random.uniform(0.9, 1.1)
        elif report_type == ReportType.WEEKLY:
            prev_period_gmv = total_gmv * random.uniform(0.85, 1.15)
        else:
            prev_period_gmv = total_gmv * random.uniform(0.8, 1.2)
        
        gmv_change_rate = ((total_gmv - prev_period_gmv) / prev_period_gmv) * 100 if prev_period_gmv else 0
        
        return {
            "daily_data": daily_data,
            "summary": {
                "gmv": total_gmv,
                "view_count": total_views,
                "conversion_rate": avg_conversion,
                "avg_watch_time": avg_watch_time,
                "total_orders": sum(d["order_count"] for d in daily_data),
                "total_clicks": sum(d["click_count"] for d in daily_data),
                "new_followers": sum(d["new_followers"] for d in daily_data),
                "gmv_change_rate": gmv_change_rate,
                "views_change_rate": ((total_views - prev_period_gmv * 2) / (prev_period_gmv * 2)) * 100
            },
            "top_products": [
                {"name": f"产品{i+1}", "gmv": random.uniform(10000, 50000), "orders": random.randint(100, 500)}
                for i in range(5)
            ],
            "peak_hours": [
                {"hour": h, "views": random.uniform(5000, 20000)}
                for h in [10, 14, 20, 21, 22]
            ]
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return "stable"
        
        avg_first = sum(values[:len(values)//2]) / (len(values)//2)
        avg_second = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if avg_second > avg_first * 1.05:
            return "up"
        elif avg_second < avg_first * 0.95:
            return "down"
        return "stable"
    
    def generate_report(
        self,
        report_type: ReportType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        template_id: Optional[str] = None
    ) -> ReportData:
        """生成报表"""
        # 默认时间范围
        now = datetime.now()
        if report_type == ReportType.DAILY:
            if not start_date:
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = start_date.replace(hour=23, minute=59, second=59)
        elif report_type == ReportType.WEEKLY:
            if not start_date:
                # 本周一
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        else:  # MONTHLY
            if not start_date:
                # 本月 1 号
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                # 本月最后一天
                if now.month == 12:
                    end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(seconds=1)
                else:
                    end_date = now.replace(month=now.month + 1, day=1) - timedelta(seconds=1)
        
        # 获取数据
        data = self._get_mock_data(report_type, start_date, end_date)
        
        # 使用模板或默认模板
        if template_id and template_id in self.templates:
            template = self.templates[template_id]
        else:
            # 根据报表类型选择默认模板
            default_map = {
                ReportType.DAILY: "daily_standard",
                ReportType.WEEKLY: "weekly_summary",
                ReportType.MONTHLY: "monthly_overview"
            }
            template = self.templates.get(default_map[report_type], {})
        
        # 构建报表章节
        sections = []
        summary = data["summary"]
        
        # 核心指标章节
        core_metrics = [
            ReportMetric(
                name="GMV",
                value=summary["gmv"],
                unit="元",
                change_rate=summary["gmv_change_rate"],
                trend="up" if summary["gmv_change_rate"] > 0 else "down" if summary["gmv_change_rate"] < 0 else "stable"
            ),
            ReportMetric(
                name="观看次数",
                value=summary["view_count"],
                unit="次",
                change_rate=summary.get("views_change_rate", 0),
                trend="up" if summary.get("views_change_rate", 0) > 0 else "down" if summary.get("views_change_rate", 0) < 0 else "stable"
            ),
            ReportMetric(
                name="转化率",
                value=summary["conversion_rate"] * 100,
                unit="%",
                trend="stable"
            ),
            ReportMetric(
                name="平均观看时长",
                value=summary["avg_watch_time"],
                unit="秒"
            )
        ]
        sections.append(ReportSection(
            title="核心指标",
            metrics=core_metrics,
            summary=f"本期 GMV 为{summary['gmv']:.2f}元，观看{summary['view_count']:.0f}次"
        ))
        
        # 流量分析章节
        traffic_metrics = [
            ReportMetric(name="PV", value=data["daily_data"][-1]["pv"] if data["daily_data"] else 0, unit="次"),
            ReportMetric(name="UV", value=data["daily_data"][-1]["uv"] if data["daily_data"] else 0, unit="人"),
            ReportMetric(name="新增粉丝", value=summary["new_followers"], unit="人"),
            ReportMetric(
                name="互动率",
                value=data["daily_data"][-1]["engagement_rate"] * 100 if data["daily_data"] else 0,
                unit="%"
            )
        ]
        sections.append(ReportSection(
            title="流量分析",
            metrics=traffic_metrics
        ))
        
        # 转化分析章节
        conversion_metrics = [
            ReportMetric(name="点击次数", value=summary["total_clicks"], unit="次"),
            ReportMetric(name="订单数", value=summary["total_orders"], unit="单"),
            ReportMetric(
                name="退款率",
                value=data["daily_data"][-1]["refund_rate"] * 100 if data["daily_data"] else 0,
                unit="%"
            ),
            ReportMetric(
                name="满意度",
                value=data["daily_data"][-1]["customer_satisfaction"] if data["daily_data"] else 0,
                unit="分"
            )
        ]
        sections.append(ReportSection(
            title="转化分析",
            metrics=conversion_metrics
        ))
        
        # 生成报表 ID
        report_id = f"{report_type.value}_{start_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}"
        
        # 生成总体摘要
        overall_summary = (
            f"{'日报' if report_type == ReportType.DAILY else '周报' if report_type == ReportType.WEEKLY else '月报'}"
            f"（{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}）："
            f"GMV {summary['gmv']:.2f}元，"
            f"{'环比' if report_type == ReportType.DAILY else '上周' if report_type == ReportType.WEEKLY else '上月'}"
            f"{'增长' if summary['gmv_change_rate'] > 0 else '下降'}{abs(summary['gmv_change_rate']):.1f}%"
        )
        
        report_data = ReportData(
            report_id=report_id,
            report_type=report_type,
            period_start=start_date,
            period_end=end_date,
            generated_at=datetime.now(),
            sections=sections,
            overall_summary=overall_summary
        )
        
        # 保存报表
        self.reports[report_id] = {
            "report_id": report_id,
            "report_type": report_type.value,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "sections": [
                {
                    "title": s.title,
                    "metrics": [asdict(m) for m in s.metrics],
                    "summary": s.summary
                }
                for s in sections
            ],
            "overall_summary": overall_summary,
            "daily_data": data["daily_data"]
        }
        self._save_reports()
        
        return report_data
    
    def get_report(self, report_id: str) -> Optional[Dict]:
        """获取报表详情"""
        return self.reports.get(report_id)
    
    def list_reports(
        self,
        report_type: Optional[ReportType] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """列出报表"""
        reports = list(self.reports.values())
        
        if report_type:
            reports = [r for r in reports if r["report_type"] == report_type.value]
        
        # 按生成时间倒序
        reports.sort(key=lambda x: x["generated_at"], reverse=True)
        
        return reports[offset:offset + limit]
    
    def export_report(
        self,
        report_id: str,
        format: ExportFormat,
        output_path: Optional[str] = None
    ) -> str:
        """导出报表"""
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"报表不存在：{report_id}")
        
        if output_path:
            output = Path(output_path)
        else:
            output = self.data_dir / f"{report_id}.{format.value}"
        
        if format == ExportFormat.JSON:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        elif format == ExportFormat.CSV:
            with open(output, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(["指标名称", "数值", "单位", "变化率", "趋势"])
                # 写入数据
                for section in report["sections"]:
                    writer.writerow([f"=== {section['title']} ==="])
                    for metric in section["metrics"]:
                        writer.writerow([
                            metric["name"],
                            metric["value"],
                            metric["unit"],
                            f"{metric['change_rate']:.2f}%" if metric.get("change_rate") is not None else "",
                            metric.get("trend", "")
                        ])
                    writer.writerow([])
        
        elif format == ExportFormat.EXCEL:
            # 简化版 Excel 导出（实际可用 openpyxl）
            return self._export_excel_simple(report, output)
        
        elif format == ExportFormat.PDF:
            # 简化版 PDF 导出（实际可用 reportlab）
            return self._export_pdf_simple(report, output)
        
        return str(output)
    
    def _export_excel_simple(self, report: Dict, output: Path) -> str:
        """简化版 Excel 导出"""
        # 使用 CSV 格式作为 Excel 的替代（可直接用 Excel 打开）
        csv_output = output.with_suffix(".csv")
        self.export_report(report["report_id"], ExportFormat.CSV, str(csv_output))
        return str(csv_output)
    
    def _export_pdf_simple(self, report: Dict, output: Path) -> str:
        """简化版 PDF 导出 - 生成文本报告"""
        # 实际项目中应使用 reportlab 或 weasyprint
        # 这里生成一个简化的文本版本
        txt_output = output.with_suffix(".txt")
        
        with open(txt_output, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"LiveMirror {report['report_type']}报表\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"报表 ID: {report['report_id']}\n")
            f.write(f"周期：{report['period_start']} 至 {report['period_end']}\n")
            f.write(f"生成时间：{report['generated_at']}\n\n")
            f.write(f"总体摘要：{report['overall_summary']}\n\n")
            
            for section in report["sections"]:
                f.write(f"\n{'='*40}\n")
                f.write(f"{section['title']}\n")
                f.write(f"{'='*40}\n")
                if section.get("summary"):
                    f.write(f"{section['summary']}\n\n")
                
                for metric in section["metrics"]:
                    change_str = ""
                    if metric.get("change_rate") is not None:
                        change_str = f" (环比{metric['change_rate']:+.2f}%)"
                    trend_str = f" [{metric.get('trend', '')}]" if metric.get("trend") else ""
                    f.write(f"  {metric['name']}: {metric['value']}{metric.get('unit', '')}{change_str}{trend_str}\n")
            
            f.write("\n" + "=" * 60 + "\n")
        
        return str(txt_output)
    
    def create_template(
        self,
        name: str,
        report_type: ReportType,
        sections: List[Dict],
        is_default: bool = False
    ) -> str:
        """创建自定义模板"""
        template_id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.templates[template_id] = {
            "name": name,
            "type": report_type.value,
            "sections": sections,
            "is_default": is_default,
            "created_at": datetime.now().isoformat()
        }
        self._save_templates()
        
        return template_id
    
    def update_template(self, template_id: str, updates: Dict) -> bool:
        """更新模板"""
        if template_id not in self.templates:
            return False
        
        self.templates[template_id].update(updates)
        self._save_templates()
        return True
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        if template_id in self.templates:
            template = self.templates[template_id]
            if template.get("is_default"):
                return False  # 不允许删除默认模板
            del self.templates[template_id]
            self._save_templates()
            return True
        return False
    
    def list_templates(self, report_type: Optional[ReportType] = None) -> List[Dict]:
        """列出模板"""
        templates = list(self.templates.values())
        
        if report_type:
            templates = [t for t in templates if t["type"] == report_type.value]
        
        return templates
    
    def create_schedule(
        self,
        report_type: ReportType,
        cron_expression: str,
        template_id: Optional[str] = None,
        export_format: ExportFormat = ExportFormat.PDF,
        send_email: bool = False,
        email_recipients: Optional[List[str]] = None,
        send_wechat: bool = False
    ) -> str:
        """创建定时报表任务"""
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        schedule = {
            "schedule_id": schedule_id,
            "report_type": report_type.value,
            "cron_expression": cron_expression,
            "template_id": template_id,
            "export_format": export_format.value,
            "send_email": send_email,
            "email_recipients": email_recipients or [],
            "send_wechat": send_wechat,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "next_run": None
        }
        
        self.schedules.append(schedule)
        self._save_schedules()
        
        return schedule_id
    
    def update_schedule(self, schedule_id: str, updates: Dict) -> bool:
        """更新定时任务"""
        for i, schedule in enumerate(self.schedules):
            if schedule["schedule_id"] == schedule_id:
                self.schedules[i].update(updates)
                self._save_schedules()
                return True
        return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """删除定时任务"""
        for i, schedule in enumerate(self.schedules):
            if schedule["schedule_id"] == schedule_id:
                del self.schedules[i]
                self._save_schedules()
                return True
        return False
    
    def list_schedules(self) -> List[Dict]:
        """列出定时任务"""
        return self.schedules
    
    def get_statistics(self) -> Dict:
        """获取报表统计"""
        reports_by_type = {}
        for report in self.reports.values():
            rtype = report["report_type"]
            reports_by_type[rtype] = reports_by_type.get(rtype, 0) + 1
        
        return {
            "total_reports": len(self.reports),
            "reports_by_type": reports_by_type,
            "total_templates": len(self.templates),
            "total_schedules": len(self.schedules),
            "active_schedules": sum(1 for s in self.schedules if s["enabled"])
        }


# 单例实例
_service_instance: Optional[ReportGeneratorService] = None


def get_service() -> ReportGeneratorService:
    """获取服务单例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ReportGeneratorService()
    return _service_instance


# 便捷函数
def generate_daily_report(template_id: Optional[str] = None) -> ReportData:
    """生成日报"""
    return get_service().generate_report(ReportType.DAILY, template_id=template_id)


def generate_weekly_report(template_id: Optional[str] = None) -> ReportData:
    """生成周报"""
    return get_service().generate_report(ReportType.WEEKLY, template_id=template_id)


def generate_monthly_report(template_id: Optional[str] = None) -> ReportData:
    """生成月报"""
    return get_service().generate_report(ReportType.MONTHLY, template_id=template_id)
