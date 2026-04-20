"""
LiveMirror 导出服务
支持 PDF/Markdown/JSON 格式导出，批量导出为 ZIP
"""

import os
import json
import zipfile
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import BytesIO, StringIO
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from models import Danmu, DanmuBatch


class ExportService:
    """导出服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_to_json(self, danmus: List[Danmu], metadata: Optional[Dict] = None) -> str:
        """
        导出为 JSON 格式
        
        Args:
            danmus: 弹幕列表
            metadata: 元数据信息
        
        Returns:
            JSON 字符串
        """
        data = {
            "metadata": metadata or {
                "export_time": datetime.utcnow().isoformat(),
                "total_count": len(danmus)
            },
            "danmus": [danmu.to_dict() for danmu in danmus]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def export_to_markdown(self, danmus: List[Danmu], metadata: Optional[Dict] = None) -> str:
        """
        导出为 Markdown 格式
        
        Args:
            danmus: 弹幕列表
            metadata: 元数据信息
        
        Returns:
            Markdown 字符串
        """
        lines = []
        
        # 标题
        lines.append("# LiveMirror 弹幕分析报告")
        lines.append("")
        
        # 元数据
        if metadata:
            lines.append("## 导出信息")
            lines.append("")
            lines.append(f"- 导出时间：{metadata.get('export_time', datetime.utcnow().isoformat())}")
            lines.append(f"- 总弹幕数：{metadata.get('total_count', len(danmus))}")
            if 'time_range' in metadata:
                lines.append(f"- 时间范围：{metadata['time_range']}")
            if 'video_title' in metadata:
                lines.append(f"- 视频标题：{metadata['video_title']}")
            lines.append("")
        
        # 统计信息
        lines.append("## 统计概览")
        lines.append("")
        
        total = len(danmus)
        positive = sum(1 for d in danmus if d.sentiment == 'positive')
        negative = sum(1 for d in danmus if d.sentiment == 'negative')
        neutral = sum(1 for d in danmus if d.sentiment == 'neutral')
        
        lines.append(f"| 情感类型 | 数量 | 占比 |")
        lines.append(f"|---------|------|------|")
        lines.append(f"| 正面 | {positive} | {positive/total*100:.1f}% |")
        lines.append(f"| 负面 | {negative} | {negative/total*100:.1f}% |")
        lines.append(f"| 中性 | {neutral} | {neutral/total*100:.1f}% |")
        lines.append("")
        
        # 关键弹幕
        key_danmus = [d for d in danmus if d.is_key_danmu]
        if key_danmus:
            lines.append("## 关键弹幕")
            lines.append("")
            for i, danmu in enumerate(key_danmus[:20], 1):  # 限制显示 20 条
                lines.append(f"{i}. **[{danmu.key_type}]** {danmu.content}")
                lines.append(f"   - 时间：{danmu.timestamp:.2f}s | 情感：{danmu.sentiment}")
            lines.append("")
        
        # 完整弹幕列表
        lines.append("## 完整弹幕列表")
        lines.append("")
        lines.append("| 时间 | 用户 | 内容 | 情感 |")
        lines.append("|------|------|------|------|")
        
        for danmu in danmus[:500]:  # 限制显示 500 条
            content = danmu.content.replace("|", "\\|")[:100]
            lines.append(
                f"| {danmu.timestamp:.2f}s | {danmu.username or '匿名'} | {content} | {danmu.sentiment} |"
            )
        
        if len(danmus) > 500:
            lines.append("")
            lines.append(f"*... 还有 {len(danmus) - 500} 条弹幕未显示*")
        
        return "\n".join(lines)
    
    def export_to_pdf(self, danmus: List[Danmu], metadata: Optional[Dict] = None) -> bytes:
        """
        导出为 PDF 格式
        
        Args:
            danmus: 弹幕列表
            metadata: 元数据信息
        
        Returns:
            PDF 二进制数据
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # 创建临时文件
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            
            # 注册中文字体（如果有的话）
            # 注意：实际部署时需要中文字体文件
            try:
                # 尝试注册系统字体
                font_paths = [
                    "C:/Windows/Fonts/simsun.ttc",  # 宋体
                    "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
                    "/usr/share/fonts/chinese/simsun.ttf",
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        break
                else:
                    # 如果没有中文字体，使用默认字体
                    pdfmetrics.registerFont(TTFont('Chinese', 'Helvetica'))
            except Exception:
                pass
            
            # 样式
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            # 标题
            elements.append(Paragraph("LiveMirror 弹幕分析报告", title_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # 元数据
            if metadata:
                meta_text = f"""
                <b>导出时间：</b>{metadata.get('export_time', datetime.utcnow().isoformat())}<br/>
                <b>总弹幕数：</b>{metadata.get('total_count', len(danmus))}<br/>
                """
                if 'time_range' in metadata:
                    meta_text += f"<b>时间范围：</b>{metadata['time_range']}<br/>"
                if 'video_title' in metadata:
                    meta_text += f"<b>视频标题：</b>{metadata['video_title']}"
                
                elements.append(Paragraph(meta_text, styles['Normal']))
                elements.append(Spacer(1, 0.3*inch))
            
            # 统计表格
            total = len(danmus)
            positive = sum(1 for d in danmus if d.sentiment == 'positive')
            negative = sum(1 for d in danmus if d.sentiment == 'negative')
            neutral = sum(1 for d in danmus if d.sentiment == 'neutral')
            
            data = [
                ['情感类型', '数量', '占比'],
                ['正面', str(positive), f'{positive/total*100:.1f}%'],
                ['负面', str(negative), f'{negative/total*100:.1f}%'],
                ['中性', str(neutral), f'{neutral/total*100:.1f}%'],
            ]
            
            table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(Paragraph("统计概览", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
            
            # 弹幕列表（限制数量）
            elements.append(Paragraph("弹幕列表（前 100 条）", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))
            
            danmu_data = [['时间', '用户', '内容', '情感']]
            for danmu in danmus[:100]:
                content = danmu.content[:50] + '...' if len(danmu.content) > 50 else danmu.content
                danmu_data.append([
                    f'{danmu.timestamp:.1f}s',
                    danmu.username or '匿名',
                    content,
                    danmu.sentiment
                ])
            
            danmu_table = Table(danmu_data, colWidths=[1*inch, 1.5*inch, 4*inch, 1*inch])
            danmu_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(danmu_table)
            
            if len(danmus) > 100:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(f"*... 还有 {len(danmus) - 100} 条弹幕未显示*", styles['Italic']))
            
            # 构建 PDF
            doc.build(elements)
            
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except ImportError:
            # 如果没有安装 reportlab，返回 Markdown 作为备选
            md_content = self.export_to_markdown(danmus, metadata)
            return md_content.encode('utf-8')
        except Exception as e:
            # 出错时返回 JSON
            error_data = {
                "error": str(e),
                "fallback": True,
                "danmus": [danmu.to_dict() for danmu in danmus[:100]]
            }
            return json.dumps(error_data, ensure_ascii=False).encode('utf-8')
    
    def create_zip_archive(
        self,
        files: List[Dict[str, Any]],
        archive_name: str = "export.zip"
    ) -> bytes:
        """
        创建 ZIP 压缩包
        
        Args:
            files: 文件列表，每个元素包含 {name: str, content: bytes/str}
            archive_name: 压缩包名称
        
        Returns:
            ZIP 二进制数据
        """
        buffer = BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_info in files:
                filename = file_info['name']
                content = file_info['content']
                
                # 如果是字符串，编码为字节
                if isinstance(content, str):
                    content = content.encode('utf-8')
                
                zip_file.writestr(filename, content)
        
        zip_data = buffer.getvalue()
        buffer.close()
        
        return zip_data
    
    def get_danmus_for_export(
        self,
        batch_id: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 10000
    ) -> List[Danmu]:
        """
        获取要导出的弹幕数据
        
        Args:
            batch_id: 批次 ID（可选）
            user_id: 用户 ID（可选）
            limit: 数量限制
        
        Returns:
            弹幕列表
        """
        query = self.db.query(Danmu)
        
        if batch_id:
            query = query.filter(Danmu.speech_segment_id == batch_id)
        
        if user_id:
            query = query.filter(Danmu.user_id == user_id)
        
        # 按时间排序
        query = query.order_by(Danmu.timestamp)
        
        # 限制数量
        query = query.limit(limit)
        
        return query.all()
    
    def get_batch_info(self, batch_id: str) -> Optional[DanmuBatch]:
        """获取批次信息"""
        return self.db.query(DanmuBatch).filter(
            DanmuBatch.batch_id == batch_id
        ).first()


class AsyncExportTask:
    """异步导出任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}  # task_id -> task_info
    
    def create_task(
        self,
        task_id: str,
        user_id: int,
        export_format: str,
        batch_ids: List[str],
        total_files: int
    ) -> Dict:
        """创建导出任务"""
        task_info = {
            "task_id": task_id,
            "user_id": user_id,
            "export_format": export_format,
            "batch_ids": batch_ids,
            "total_files": total_files,
            "processed_files": 0,
            "status": "pending",  # pending, processing, completed, failed
            "progress": 0,  # 0-100
            "result_url": None,
            "error_message": None,
            "created_at": datetime.utcnow(),
            "completed_at": None
        }
        self.tasks[task_id] = task_info
        return task_info
    
    def update_progress(self, task_id: str, processed: int, status: Optional[str] = None):
        """更新任务进度"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task["processed_files"] = processed
        task["progress"] = int((processed / task["total_files"]) * 100)
        
        if status:
            task["status"] = status
    
    def complete_task(self, task_id: str, result_url: str):
        """完成任务"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task["status"] = "completed"
        task["progress"] = 100
        task["result_url"] = result_url
        task["completed_at"] = datetime.utcnow()
    
    def fail_task(self, task_id: str, error_message: str):
        """任务失败"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task["status"] = "failed"
        task["error_message"] = error_message
        task["completed_at"] = datetime.utcnow()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        cutoff = datetime.utcnow()
        from datetime import timedelta
        cutoff = cutoff - timedelta(hours=max_age_hours)
        
        to_remove = [
            task_id for task_id, task in self.tasks.items()
            if task["completed_at"] and task["completed_at"] < cutoff
        ]
        
        for task_id in to_remove:
            del self.tasks[task_id]


# 全局异步任务管理器实例
async_task_manager = AsyncExportTask()


def get_async_task_manager() -> AsyncExportTask:
    """获取异步任务管理器实例"""
    return async_task_manager
