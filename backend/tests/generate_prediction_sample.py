"""
生成预测样本 - LiveMirror
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.prediction import get_service

def generate_sample():
    service = get_service()
    
    # 预测明天晚间时段
    target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 综合预测
    result = service.predict_all(target_date, "evening", "general")
    
    # 时间推荐
    rec = service.recommend_best_time(category="general", top_n=3)
    
    # 历史趋势
    trends = service.get_historical_trends(days=30)
    
    # 模型性能
    perf = service.get_model_performance()
    
    # 保存为 JSON
    sample_data = {
        "prediction": {
            "target_date": target_date,
            "time_slot": "evening",
            "predicted_gmv": result.predicted_gmv,
            "predicted_viewers": result.predicted_viewers,
            "predicted_conversion_rate": result.predicted_conversion_rate,
            "confidence_interval": result.confidence_interval,
            "model_used": result.model_used,
            "accuracy_score": result.accuracy_score,
            "factors": result.factors
        },
        "recommendation": rec.to_dict(),
        "historical_trends": {
            "days": 30,
            "data_points": len(trends['daily_trends']),
            "slot_summary": trends['slot_summary']
        },
        "model_performance": perf,
        "generated_at": datetime.now().isoformat()
    }
    
    # 确保目录存在
    Path("data/prediction").mkdir(parents=True, exist_ok=True)
    
    with open("data/prediction/sample.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print("Prediction sample generated successfully!")
    print(f"Target Date: {target_date}")
    print(f"Predicted GMV: RMB {result.predicted_gmv:,.2f}")
    print(f"Predicted Viewers: {result.predicted_viewers:,}")
    print(f"Predicted Conversion Rate: {result.predicted_conversion_rate*100:.2f}%")
    print(f"Accuracy: {result.accuracy_score*100:.1f}%")
    print(f"Recommended Slot: {rec.recommended_slot}")
    print(f"Sample saved to: data/prediction/sample.json")

if __name__ == "__main__":
    generate_sample()
