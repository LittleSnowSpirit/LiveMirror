"""
LiveMirror 多直播间对比分析服务
支持多直播间数据对比、指标计算、AI 差异分析
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
from collections import defaultdict


@dataclass
class LiveRoomMetrics:
    """直播间指标数据"""
    room_id: str
    room_name: str
    total_viewers: int
    avg_duration: float  # 分钟
    engagement_rate: float  # 百分比
    conversion_rate: float  # 百分比
    emotion_avg: float  # 平均情绪值
    emotion_peak: float  # 情绪峰值
    interaction_count: int  # 互动次数
    speech_quality: float  # 话术质量评分
    content_quality: float  # 内容质量评分
    rhythm_control: float  # 节奏把控评分
    retention_rate: float  # 观众留存率


@dataclass
class ComparisonResult:
    """对比分析结果"""
    timestamp: str
    rooms: List[LiveRoomMetrics]
    metrics_comparison: Dict[str, List[Dict[str, Any]]]
    radar_data: Dict[str, List[float]]
    emotion_curves: Dict[str, List[Dict[str, Any]]]
    ai_analysis: Dict[str, Any]
    recommendations: List[str]


class CompareAnalysisService:
    """
    多直播间对比分析服务
    提供数据加载、指标计算、对比分析、AI 报告生成
    """
    
    def __init__(self, db_path: str = "livemirror.db"):
        self.db_path = db_path
        self._cache: Dict[str, Any] = {}
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def load_room_data(self, room_ids: List[str]) -> List[LiveRoomMetrics]:
        """
        加载多个直播间的数据
        
        Args:
            room_ids: 直播间 ID 列表
        
        Returns:
            直播间指标列表
        """
        rooms = []
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            for room_id in room_ids:
                # 查询直播间基础数据
                cursor.execute("""
                    SELECT 
                        room_id,
                        room_name,
                        total_viewers,
                        avg_duration,
                        engagement_rate,
                        conversion_rate,
                        emotion_avg,
                        emotion_peak,
                        interaction_count,
                        speech_quality,
                        content_quality,
                        rhythm_control,
                        retention_rate
                    FROM live_rooms
                    WHERE room_id = ?
                """, (room_id,))
                
                row = cursor.fetchone()
                
                if row:
                    metrics = LiveRoomMetrics(
                        room_id=row['room_id'],
                        room_name=row['room_name'] or f"直播间{room_id}",
                        total_viewers=row['total_viewers'] or 0,
                        avg_duration=row['avg_duration'] or 0.0,
                        engagement_rate=row['engagement_rate'] or 0.0,
                        conversion_rate=row['conversion_rate'] or 0.0,
                        emotion_avg=row['emotion_avg'] or 0.0,
                        emotion_peak=row['emotion_peak'] or 0.0,
                        interaction_count=row['interaction_count'] or 0,
                        speech_quality=row['speech_quality'] or 0.0,
                        content_quality=row['content_quality'] or 0.0,
                        rhythm_control=row['rhythm_control'] or 0.0,
                        retention_rate=row['retention_rate'] or 0.0
                    )
                    rooms.append(metrics)
                else:
                    # 如果没有真实数据，生成模拟数据用于演示
                    metrics = self._generate_mock_data(room_id)
                    rooms.append(metrics)
            
            conn.close()
        except Exception as e:
            print(f"[ERROR] 加载直播间数据失败：{e}")
            conn.close()
            # 返回模拟数据
            for room_id in room_ids:
                rooms.append(self._generate_mock_data(room_id))
        
        return rooms
    
    def _generate_mock_data(self, room_id: str) -> LiveRoomMetrics:
        """生成模拟数据用于演示"""
        import random
        
        # 基于 room_id 生成一致性数据
        seed = hash(room_id) % 1000
        random.seed(seed)
        
        return LiveRoomMetrics(
            room_id=room_id,
            room_name=f"直播间{room_id[-4:]}",
            total_viewers=random.randint(5000, 30000),
            avg_duration=random.uniform(30, 90),
            engagement_rate=random.uniform(70, 95),
            conversion_rate=random.uniform(2, 8),
            emotion_avg=random.uniform(60, 85),
            emotion_peak=random.uniform(85, 98),
            interaction_count=random.randint(1000, 10000),
            speech_quality=random.uniform(75, 95),
            content_quality=random.uniform(70, 92),
            rhythm_control=random.uniform(68, 90),
            retention_rate=random.uniform(65, 88)
        )
    
    def calculate_comparison_metrics(self, rooms: List[LiveRoomMetrics]) -> Dict[str, List[Dict[str, Any]]]:
        """
        计算对比指标
        
        Args:
            rooms: 直播间指标列表
        
        Returns:
            对比指标数据
        """
        metrics_comparison = {
            "conversion_rate": [],
            "engagement_rate": [],
            "emotion_avg": [],
            "retention_rate": [],
            "total_viewers": []
        }
        
        for room in rooms:
            metrics_comparison["conversion_rate"].append({
                "room_id": room.room_id,
                "room_name": room.room_name,
                "value": round(room.conversion_rate, 2)
            })
            metrics_comparison["engagement_rate"].append({
                "room_id": room.room_id,
                "room_name": room.room_name,
                "value": round(room.engagement_rate, 2)
            })
            metrics_comparison["emotion_avg"].append({
                "room_id": room.room_id,
                "room_name": room.room_name,
                "value": round(room.emotion_avg, 2)
            })
            metrics_comparison["retention_rate"].append({
                "room_id": room.room_id,
                "room_name": room.room_name,
                "value": round(room.retention_rate, 2)
            })
            metrics_comparison["total_viewers"].append({
                "room_id": room.room_id,
                "room_name": room.room_name,
                "value": room.total_viewers
            })
        
        return metrics_comparison
    
    def generate_radar_data(self, rooms: List[LiveRoomMetrics]) -> Dict[str, List[float]]:
        """
        生成雷达图数据（五维评分）
        
        Args:
            rooms: 直播间指标列表
        
        Returns:
            雷达图数据
        """
        radar_data = {}
        
        for room in rooms:
            radar_data[room.room_name] = [
                round(room.content_quality, 2),
                round(room.engagement_rate, 2),
                round(room.rhythm_control, 2),
                round(room.speech_quality, 2),
                round(room.retention_rate, 2)
            ]
        
        return radar_data
    
    def generate_emotion_curves(self, room_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        生成情绪曲线数据
        
        Args:
            room_ids: 直播间 ID 列表
        
        Returns:
            情绪曲线数据
        """
        import random
        
        emotion_curves = {}
        
        for room_id in room_ids:
            # 生成模拟情绪曲线数据
            seed = hash(room_id) % 1000
            random.seed(seed)
            
            base_emotion = random.uniform(55, 75)
            curve_data = []
            
            for i in range(10):
                time_label = f"{i*5:02d}:00"
                # 添加随机波动和峰值
                variation = random.uniform(-15, 20)
                if i in [3, 7]:  # 模拟高峰时刻
                    variation += 15
                
                value = min(100, max(0, base_emotion + variation))
                curve_data.append({
                    "time": time_label,
                    "value": round(value, 2)
                })
            
            # 获取房间名称
            room_name = f"直播间{room_id[-4:]}"
            emotion_curves[room_name] = curve_data
        
        return emotion_curves
    
    def generate_ai_analysis(self, rooms: List[LiveRoomMetrics]) -> Dict[str, Any]:
        """
        生成 AI 差异分析报告
        
        Args:
            rooms: 直播间指标列表
        
        Returns:
            AI 分析报告
        """
        if len(rooms) < 2:
            return {"summary": "需要至少两个直播间进行对比", "details": []}
        
        # 找出最优和最差直播间
        best_room = max(rooms, key=lambda r: r.engagement_rate)
        worst_room = min(rooms, key=lambda r: r.engagement_rate)
        
        # 计算各指标的平均值
        avg_conversion = sum(r.conversion_rate for r in rooms) / len(rooms)
        avg_engagement = sum(r.engagement_rate for r in rooms) / len(rooms)
        avg_emotion = sum(r.emotion_avg for r in rooms) / len(rooms)
        
        # 生成分析
        analysis = {
            "summary": f"共对比{len(rooms)}个直播间，{best_room.room_name}表现最佳，{worst_room.room_name}有提升空间",
            "best_performer": {
                "room_name": best_room.room_name,
                "strengths": []
            },
            "needs_improvement": {
                "room_name": worst_room.room_name,
                "weaknesses": []
            },
            "key_differences": [],
            "details": []
        }
        
        # 分析最优直播间优势
        if best_room.conversion_rate > avg_conversion:
            analysis["best_performer"]["strengths"].append(
                f"转化率高达{best_room.conversion_rate:.1f}%，超出平均水平{best_room.conversion_rate - avg_conversion:.1f}%"
            )
        if best_room.engagement_rate > avg_engagement:
            analysis["best_performer"]["strengths"].append(
                f"互动率{best_room.engagement_rate:.1f}%，观众参与度高"
            )
        if best_room.emotion_avg > avg_emotion:
            analysis["best_performer"]["strengths"].append(
                f"平均情绪值{best_room.emotion_avg:.1f}，氛围活跃"
            )
        
        # 分析待改进直播间问题
        if worst_room.conversion_rate < avg_conversion:
            analysis["needs_improvement"]["weaknesses"].append(
                f"转化率{worst_room.conversion_rate:.1f}%，低于平均水平{avg_conversion - worst_room.conversion_rate:.1f}%"
            )
        if worst_room.engagement_rate < avg_engagement:
            analysis["needs_improvement"]["weaknesses"].append(
                f"互动率{worst_room.engagement_rate:.1f}%，需加强观众互动"
            )
        if worst_room.retention_rate < sum(r.retention_rate for r in rooms) / len(rooms):
            analysis["needs_improvement"]["weaknesses"].append(
                f"观众留存率{worst_room.retention_rate:.1f}%，需优化内容吸引力"
            )
        
        # 关键差异分析
        conversion_gap = best_room.conversion_rate - worst_room.conversion_rate
        engagement_gap = best_room.engagement_rate - worst_room.engagement_rate
        
        analysis["key_differences"].append(
            f"转化率差距：{conversion_gap:.1f}%（{best_room.room_name}领先）"
        )
        analysis["key_differences"].append(
            f"互动率差距：{engagement_gap:.1f}%（{best_room.room_name}领先）"
        )
        
        # 详细分析
        for room in rooms:
            performance = "优秀" if room.engagement_rate >= avg_engagement else "待提升"
            analysis["details"].append({
                "room_name": room.room_name,
                "performance": performance,
                "highlights": [
                    f"转化率：{room.conversion_rate:.1f}%",
                    f"互动率：{room.engagement_rate:.1f}%",
                    f"情绪值：{room.emotion_avg:.1f}",
                    f"留存率：{room.retention_rate:.1f}%"
                ]
            })
        
        return analysis
    
    def generate_recommendations(self, rooms: List[LiveRoomMetrics], ai_analysis: Dict[str, Any]) -> List[str]:
        """
        生成优化建议
        
        Args:
            rooms: 直播间指标列表
            ai_analysis: AI 分析报告
        
        Returns:
            优化建议列表
        """
        recommendations = []
        
        # 基于对比结果生成建议
        avg_conversion = sum(r.conversion_rate for r in rooms) / len(rooms)
        
        for room in rooms:
            if room.conversion_rate < avg_conversion * 0.8:
                recommendations.append(
                    f"【{room.room_name}】建议优化产品讲解话术，增加促销引导，提升转化率"
                )
            if room.engagement_rate < 80:
                recommendations.append(
                    f"【{room.room_name}】建议增加互动环节，如抽奖、问答，提升观众参与度"
                )
            if room.retention_rate < 70:
                recommendations.append(
                    f"【{room.room_name}】建议优化开场内容，前 5 分钟设置爆点吸引观众留存"
                )
            if room.emotion_avg < 65:
                recommendations.append(
                    f"【{room.room_name}】建议调整直播节奏，增加高潮环节，提升观众情绪"
                )
        
        # 通用建议
        if len(rooms) >= 3:
            recommendations.append(
                "建议学习表现最佳直播间的话术结构和互动方式"
            )
        
        return recommendations
    
    def compare_rooms(self, room_ids: List[str]) -> ComparisonResult:
        """
        执行多直播间对比分析
        
        Args:
            room_ids: 直播间 ID 列表
        
        Returns:
            对比分析结果
        """
        start_time = time.time()
        
        # 加载数据
        rooms = self.load_room_data(room_ids)
        
        # 计算对比指标
        metrics_comparison = self.calculate_comparison_metrics(rooms)
        
        # 生成雷达图数据
        radar_data = self.generate_radar_data(rooms)
        
        # 生成情绪曲线
        emotion_curves = self.generate_emotion_curves(room_ids)
        
        # 生成 AI 分析
        ai_analysis = self.generate_ai_analysis(rooms)
        
        # 生成建议
        recommendations = self.generate_recommendations(rooms, ai_analysis)
        
        # 构建结果
        result = ComparisonResult(
            timestamp=datetime.now().isoformat(),
            rooms=rooms,
            metrics_comparison=metrics_comparison,
            radar_data=radar_data,
            emotion_curves=emotion_curves,
            ai_analysis=ai_analysis,
            recommendations=recommendations
        )
        
        elapsed = time.time() - start_time
        print(f"[COMPARE] 对比分析完成，耗时{elapsed:.2f}s，对比{len(rooms)}个直播间")
        
        return result
    
    def export_to_pdf(self, result: ComparisonResult, output_path: str) -> bool:
        """
        导出对比报告为 PDF
        
        Args:
            result: 对比分析结果
            output_path: 输出文件路径
        
        Returns:
            是否成功
        """
        try:
            # 使用 reportlab 生成 PDF
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=landscape(A4),
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # 标题
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#303133'),
                spaceAfter=30,
                alignment=1  # 居中
            )
            
            elements.append(Paragraph("📊 直播间对比分析报告", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # 时间戳
            time_style = ParagraphStyle(
                'TimeStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#909399'),
                alignment=1
            )
            elements.append(Paragraph(f"生成时间：{result.timestamp}", time_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # 直播间概览表
            elements.append(Paragraph("直播间概览", styles['Heading2']))
            
            table_data = [["直播间", "观众数", "互动率", "转化率", "情绪值", "留存率"]]
            for room in result.rooms:
                table_data.append([
                    room.room_name,
                    str(room.total_viewers),
                    f"{room.engagement_rate:.1f}%",
                    f"{room.conversion_rate:.1f}%",
                    f"{room.emotion_avg:.1f}",
                    f"{room.retention_rate:.1f}%"
                ])
            
            table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#409EFF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f7fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dcdfe6'))
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
            
            # AI 分析
            elements.append(Paragraph("🤖 AI 差异分析", styles['Heading2']))
            elements.append(Paragraph(result.ai_analysis["summary"], styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
            
            # 关键差异
            elements.append(Paragraph("关键差异:", styles['Heading3']))
            for diff in result.ai_analysis.get("key_differences", []):
                elements.append(Paragraph(f"• {diff}", styles['Normal']))
            
            elements.append(Spacer(1, 0.3*inch))
            
            # 优化建议
            elements.append(Paragraph("💡 优化建议", styles['Heading2']))
            for i, rec in enumerate(result.recommendations, 1):
                elements.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            
            # 生成 PDF
            doc.build(elements)
            
            print(f"[PDF] 报告已导出到 {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] PDF 导出失败：{e}")
            # 降级为 JSON 导出
            return self._export_to_json(result, output_path.replace('.pdf', '.json'))
    
    def _export_to_json(self, result: ComparisonResult, output_path: str) -> bool:
        """降级导出为 JSON"""
        try:
            # 将 dataclass 转换为字典
            result_dict = {
                "timestamp": result.timestamp,
                "rooms": [asdict(room) for room in result.rooms],
                "metrics_comparison": result.metrics_comparison,
                "radar_data": result.radar_data,
                "emotion_curves": result.emotion_curves,
                "ai_analysis": result.ai_analysis,
                "recommendations": result.recommendations
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, ensure_ascii=False, indent=2)
            
            print(f"[JSON] 报告已导出到 {output_path}")
            return True
        except Exception as e:
            print(f"[ERROR] JSON 导出失败：{e}")
            return False


# 全局服务实例
_service_instance: Optional[CompareAnalysisService] = None


def get_service(db_path: str = "livemirror.db") -> CompareAnalysisService:
    """获取全局服务实例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = CompareAnalysisService(db_path)
    return _service_instance


def compare_live_rooms(room_ids: List[str]) -> ComparisonResult:
    """便捷函数：对比直播间"""
    service = get_service()
    return service.compare_rooms(room_ids)


if __name__ == "__main__":
    # 测试服务
    print("="*60)
    print("多直播间对比分析服务测试")
    print("="*60)
    
    # 测试对比 3 个直播间
    room_ids = ["room_001", "room_002", "room_003"]
    result = compare_live_rooms(room_ids)
    
    print(f"\n对比结果:")
    print(f"  直播间数量：{len(result.rooms)}")
    print(f"  时间戳：{result.timestamp}")
    
    print(f"\nAI 分析摘要:")
    print(f"  {result.ai_analysis['summary']}")
    
    print(f"\n关键差异:")
    for diff in result.ai_analysis.get("key_differences", []):
        print(f"  - {diff}")
    
    print(f"\n优化建议:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")
    
    # 测试 PDF 导出
    output_path = "reports/compare_report.pdf"
    Path("reports").mkdir(exist_ok=True)
    
    service = get_service()
    success = service.export_to_pdf(result, output_path)
    print(f"\n报告导出：{'成功' if success else '失败'}")
