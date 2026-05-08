"""
种子数据脚本 - 优秀话术示例
运行方式: python scripts/seed_excellent_examples.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import ExcellentExample


SEED_DATA = [
    # 价格促销类
    ExcellentExample(
        speech_type='price_promotion',
        content='平时专柜卖 299 的产品，今天直播间福利价只要 99！立省 200 块！只有今天这个价格，错过就没有了！',
        score=92,
        emotion_impact=0.95,
        engagement_rate=35,
        session_id='seed_001',
        timestamp=120
    ),
    ExcellentExample(
        speech_type='price_promotion',
        content='这个价格我真的亏本在卖！就是为了给大家送福利！抢到就是赚到！',
        score=88,
        emotion_impact=0.88,
        engagement_rate=28,
        session_id='seed_002',
        timestamp=90
    ),
    # 产品介绍类
    ExcellentExample(
        speech_type='product_intro',
        content='这款面膜我连续用了 28 天，皮肤从干燥起皮到现在水嫩嫩的！早上上妆完全不卡粉！同事都问我是不是去做了美容！',
        score=90,
        emotion_impact=0.85,
        engagement_rate=22,
        session_id='seed_003',
        timestamp=150
    ),
    # 限时限量类
    ExcellentExample(
        speech_type='limited_offer',
        content='只剩最后 50 单了！抢完马上下架！3、2、1，上链接！',
        score=95,
        emotion_impact=0.98,
        engagement_rate=45,
        session_id='seed_004',
        timestamp=60
    ),
    # 开场白类
    ExcellentExample(
        speech_type='opening',
        content='家人们晚上好！今天给大家带来三款超值好物，第一款是我自己用了半年的爆款，第二款是品牌方给我们的独家福利，第三款是今天的秒杀品！先关注不迷路！',
        score=87,
        emotion_impact=0.82,
        engagement_rate=25,
        session_id='seed_005',
        timestamp=30
    ),
    # 互动引导类
    ExcellentExample(
        speech_type='interaction',
        content='想要的家人们扣 1！让我看看有多少人想要！人数够了我就去找品牌方再申请一波福利！',
        score=85,
        emotion_impact=0.78,
        engagement_rate=40,
        session_id='seed_006',
        timestamp=180
    ),
]


def seed():
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing = db.query(ExcellentExample).count()
        if existing > 0:
            print(f"已存在 {existing} 条数据，跳过种子数据插入")
            return

        # 插入种子数据
        for example in SEED_DATA:
            db.add(example)
        db.commit()
        print(f"成功插入 {len(SEED_DATA)} 条优秀话术示例")
    except Exception as e:
        db.rollback()
        print(f"插入种子数据失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
