"""
LiveMirror Prediction Service
直播效果预测服务 - 使用 AI 预测 GMV/观看人数/转化率等
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os


class PredictionService:
    """直播预测服务"""
    
    def __init__(self):
        self.model_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 'historical.json'
        )
        self._load_historical_data()
    
    def _load_historical_data(self):
        """加载历史数据"""
        if os.path.exists(self.model_data_path):
            with open(self.model_data_path, 'r', encoding='utf-8') as f:
                self.historical_data = json.load(f)
        else:
            # 生成模拟历史数据用于测试
            self.historical_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[Dict]:
        """生成模拟历史数据"""
        data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            # 周末效果通常更好
            is_weekend = date.weekday() >= 5
            base_viewers = 5000 if is_weekend else 3000
            base_gmv = 50000 if is_weekend else 30000
            
            # 添加随机波动
            viewers = int(base_viewers * (0.8 + np.random.random() * 0.4))
            gmv = int(base_gmv * (0.7 + np.random.random() * 0.6))
            conversion_rate = round((gmv / viewers) * 0.001 * (0.8 + np.random.random() * 0.4), 4)
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'day_of_week': date.weekday(),
                'hour': 20,  # 默认晚上 8 点
                'viewers': viewers,
                'gmv': gmv,
                'conversion_rate': conversion_rate,
                'duration_minutes': 120
            })
        
        return data
    
    def predict_gmv(self, 
                   expected_viewers: int,
                   historical_gmv: Optional[List[int]] = None,
                   confidence: float = 0.85) -> Dict:
        """
        GMV 预测
        
        Args:
            expected_viewers: 预期观看人数
            historical_gmv: 历史 GMV 数据
            confidence: 置信度
            
        Returns:
            预测结果包含预测值、置信区间等
        """
        if historical_gmv is None:
            historical_gmv = [item['gmv'] for item in self.historical_data]
        
        # 计算历史转化率
        historical_viewers = [item['viewers'] for item in self.historical_data]
        if historical_viewers:
            avg_conversion_value = np.mean([
                g / v if v > 0 else 0 
                for g, v in zip(historical_gmv, historical_viewers)
            ])
        else:
            avg_conversion_value = 10.0  # 默认每人贡献 10 元
        
        # 预测 GMV
        predicted_gmv = int(expected_viewers * avg_conversion_value)
        
        # 计算置信区间 (基于历史标准差)
        # 置信度越高，区间应该越宽
        if len(historical_gmv) > 1:
            std_dev = np.std(historical_gmv)
            # 置信度 0.95 -> 2 倍标准差，置信度 0.80 -> 1.28 倍标准差
            z_score = {
                0.95: 2.0,
                0.90: 1.64,
                0.85: 1.44,
                0.80: 1.28
            }.get(round(confidence, 2), 1.5)
            margin = std_dev * z_score
        else:
            margin = predicted_gmv * 0.2 * (confidence * 2)
        
        return {
            'predicted_gmv': predicted_gmv,
            'confidence_interval': {
                'lower': int(predicted_gmv - margin),
                'upper': int(predicted_gmv + margin),
                'confidence': confidence
            },
            'avg_conversion_value': round(avg_conversion_value, 2),
            'data_points': len(historical_gmv)
        }
    
    def predict_viewers(self,
                       day_of_week: int,
                       hour: int,
                       historical_viewers: Optional[List[Dict]] = None) -> Dict:
        """
        观看人数预测
        
        Args:
            day_of_week: 星期几 (0-6)
            hour: 小时 (0-23)
            historical_viewers: 历史观看数据
            
        Returns:
            预测结果
        """
        if historical_viewers is None:
            historical_viewers = self.historical_data
        
        # 按星期和小时分组统计
        filtered_data = [
            item for item in historical_viewers
            if item.get('day_of_week') == day_of_week or True  # 简化：使用所有数据
        ]
        
        if not filtered_data:
            viewers_list = [item['viewers'] for item in historical_viewers]
        else:
            viewers_list = [item['viewers'] for item in filtered_data]
        
        if not viewers_list:
            return {'predicted_viewers': 3000, 'trend': 'stable'}
        
        # 简单时间序列预测 (使用移动平均)
        recent_viewers = viewers_list[-7:] if len(viewers_list) >= 7 else viewers_list
        predicted_viewers = int(np.mean(recent_viewers))
        
        # 计算趋势
        if len(viewers_list) >= 14:
            old_avg = np.mean(viewers_list[:7])
            new_avg = np.mean(viewers_list[-7:])
            trend = 'increasing' if new_avg > old_avg * 1.1 else 'decreasing' if new_avg < old_avg * 0.9 else 'stable'
        else:
            trend = 'stable'
        
        # 时段系数
        time_multiplier = self._get_time_multiplier(hour, day_of_week)
        predicted_viewers = int(predicted_viewers * time_multiplier)
        
        return {
            'predicted_viewers': predicted_viewers,
            'trend': trend,
            'time_multiplier': round(time_multiplier, 2),
            'peak_hours': self._get_peak_hours()
        }
    
    def _get_time_multiplier(self, hour: int, day_of_week: int) -> float:
        """获取时段系数"""
        # 晚上 8-10 点是黄金时段
        if 19 <= hour <= 22:
            base = 1.3
        elif 12 <= hour <= 14:
            base = 1.0
        else:
            base = 0.7
        
        # 周末加成
        weekend_bonus = 1.2 if day_of_week >= 5 else 1.0
        
        return base * weekend_bonus
    
    def _get_peak_hours(self) -> List[int]:
        """获取高峰时段"""
        return [19, 20, 21, 22]
    
    def predict_conversion_rate(self,
                                product_category: str = 'general',
                                price_range: str = 'medium') -> Dict:
        """
        转化率预测
        
        Args:
            product_category: 产品类别
            price_range: 价格区间
            
        Returns:
            预测转化率
        """
        # 基础转化率 (电商直播平均 1-5%)
        base_rate = 0.02
        
        # 类别调整
        category_multipliers = {
            'fashion': 1.2,
            'electronics': 0.8,
            'beauty': 1.3,
            'food': 1.1,
            'general': 1.0
        }
        
        # 价格区间调整
        price_multipliers = {
            'low': 1.3,
            'medium': 1.0,
            'high': 0.7
        }
        
        predicted_rate = base_rate * category_multipliers.get(product_category, 1.0) * price_multipliers.get(price_range, 1.0)
        
        # 添加历史数据修正
        historical_rates = [item.get('conversion_rate', 0.02) for item in self.historical_data]
        if historical_rates:
            hist_avg = np.mean(historical_rates)
            predicted_rate = (predicted_rate + hist_avg) / 2
        
        return {
            'predicted_conversion_rate': round(predicted_rate, 4),
            'predicted_conversion_rate_percent': round(predicted_rate * 100, 2),
            'category': product_category,
            'price_range': price_range,
            'benchmark': 0.02
        }
    
    def recommend_best_time(self,
                           target_audience: str = 'general',
                           duration_minutes: int = 120) -> Dict:
        """
        推荐最佳直播时间
        
        Args:
            target_audience: 目标受众
            duration_minutes: 预计直播时长
            
        Returns:
            推荐的时间段
        """
        # 分析历史数据找出最佳表现的时间
        time_performance = {}
        
        for item in self.historical_data:
            key = f"{item.get('day_of_week', 0)}_{item.get('hour', 20)}"
            if key not in time_performance:
                time_performance[key] = []
            time_performance[key].append(item.get('gmv', 0))
        
        # 计算每个时间段的平均 GMV
        best_time = None
        best_avg_gmv = 0
        
        for key, gmv_list in time_performance.items():
            avg_gmv = np.mean(gmv_list)
            if avg_gmv > best_avg_gmv:
                best_avg_gmv = avg_gmv
                day, hour = map(int, key.split('_'))
                best_time = {'day': day, 'hour': hour}
        
        # 如果没有历史数据，使用默认推荐
        if best_time is None:
            best_time = {'day': 5, 'hour': 20}  # 周六晚上 8 点
        
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        return {
            'recommended_day': best_time['day'],
            'recommended_day_name': day_names[best_time['day']],
            'recommended_hour': best_time['hour'],
            'recommended_time_str': f"{day_names[best_time['day']]} {best_time['hour']}:00",
            'expected_performance': int(best_avg_gmv),
            'alternative_times': [
                {'day': 6, 'hour': 20, 'label': '周日 20:00'},
                {'day': 5, 'hour': 19, 'label': '周六 19:00'},
                {'day': 4, 'hour': 20, 'label': '周五 20:00'}
            ],
            'duration_minutes': duration_minutes
        }
    
    def evaluate_accuracy(self,
                         predictions: List[Dict],
                         actuals: List[Dict]) -> Dict:
        """
        评估预测准确度
        
        Args:
            predictions: 预测值列表
            actuals: 实际值列表
            
        Returns:
            准确度评估结果
        """
        if len(predictions) != len(actuals) or len(predictions) == 0:
            return {'error': '预测值和实际值数量不匹配或为空'}
        
        mae_gmv = []
        mape_gmv = []
        mae_viewers = []
        
        for pred, actual in zip(predictions, actuals):
            # GMV 误差
            if 'gmv' in pred and 'gmv' in actual:
                pred_gmv = pred['gmv']
                actual_gmv = actual['gmv']
                mae_gmv.append(abs(pred_gmv - actual_gmv))
                if actual_gmv > 0:
                    mape_gmv.append(abs(pred_gmv - actual_gmv) / actual_gmv)
            
            # 观看人数误差
            if 'viewers' in pred and 'viewers' in actual:
                pred_viewers = pred['viewers']
                actual_viewers = actual['viewers']
                mae_viewers.append(abs(pred_viewers - actual_viewers))
        
        result = {
            'total_predictions': len(predictions),
            'metrics': {}
        }
        
        if mae_gmv:
            result['metrics']['gmv'] = {
                'mae': int(np.mean(mae_gmv)),
                'mape': round(np.mean(mape_gmv) * 100, 2) if mape_gmv else None,
                'rmse': int(np.sqrt(np.mean([x**2 for x in mae_gmv])))
            }
        
        if mae_viewers:
            # 计算 viewers 的 MAPE
            mape_viewers = []
            for p, a in zip([p.get('viewers', 0) for p in predictions], 
                           [a.get('viewers', 0) for a in actuals]):
                if a > 0:
                    mape_viewers.append(abs(p - a) / a * 100)
            
            result['metrics']['viewers'] = {
                'mae': int(np.mean(mae_viewers)),
                'mape': round(np.mean(mape_viewers), 2) if mape_viewers else 0,
                'accuracy': round(100 - np.mean(mape_viewers), 2) if mape_viewers else 100
            }
        
        # 整体评分 (0-100)
        if result['metrics']:
            # 使用 MAPE 计算准确度 (MAPE=0 表示 100% 准确)
            accuracies = []
            for m in result['metrics'].values():
                if m.get('mape') is not None:
                    # MAPE 是百分比误差，100 - MAPE = 准确度
                    accuracies.append(100 - m['mape'])
                else:
                    accuracies.append(80)  # 默认准确度
            
            avg_accuracy = np.mean(accuracies)
            result['overall_accuracy'] = round(min(100, max(0, avg_accuracy)), 2)
            result['rating'] = '优秀' if avg_accuracy >= 90 else '良好' if avg_accuracy >= 75 else '一般'
        
        return result
    
    def get_trend_data(self, days: int = 30) -> Dict:
        """
        获取趋势数据用于可视化
        
        Args:
            days: 天数
            
        Returns:
            趋势数据
        """
        recent_data = self.historical_data[-days:] if len(self.historical_data) >= days else self.historical_data
        
        return {
            'dates': [item['date'] for item in recent_data],
            'gmv': [item['gmv'] for item in recent_data],
            'viewers': [item['viewers'] for item in recent_data],
            'conversion_rates': [item['conversion_rate'] for item in recent_data],
            'summary': {
                'total_gmv': sum(item['gmv'] for item in recent_data),
                'avg_viewers': int(np.mean([item['viewers'] for item in recent_data])),
                'avg_conversion_rate': round(np.mean([item['conversion_rate'] for item in recent_data]), 4),
                'trend': self._calculate_trend([item['gmv'] for item in recent_data])
            }
        }
    
    def _calculate_trend(self, values: List[int]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return 'stable'
        
        first_half = np.mean(values[:len(values)//2])
        second_half = np.mean(values[len(values)//2:])
        
        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def generate_sample_prediction(self) -> Dict:
        """生成示例预测用于测试"""
        viewers_pred = self.predict_viewers(day_of_week=5, hour=20)
        gmv_pred = self.predict_gmv(viewers_pred['predicted_viewers'])
        conversion_pred = self.predict_conversion_rate()
        time_rec = self.recommend_best_time()
        trend_data = self.get_trend_data()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'viewers_prediction': viewers_pred,
            'gmv_prediction': gmv_pred,
            'conversion_prediction': conversion_pred,
            'time_recommendation': time_rec,
            'trend_data': trend_data,
            'model_info': {
                'version': '1.0.0',
                'data_points': len(self.historical_data),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }


# 单例实例
prediction_service = PredictionService()


if __name__ == '__main__':
    # 测试代码
    service = PredictionService()
    result = service.generate_sample_prediction()
    print(json.dumps(result, ensure_ascii=False, indent=2))
