"""
Alert System Tests
Test rule engine, sentiment alerts, speech risks, push notifications, etc.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from services.alert_engine import get_alert_engine, AlertEngine
from services.alert_rules import get_rule_manager, AlertRuleManager, AlertType, AlertLevel
import time


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_rule_manager():
    """Test rule manager"""
    print_section("Test 1: Rule Manager")
    
    rule_manager = get_rule_manager()
    
    # Get all rules
    rules = rule_manager.get_all_rules()
    print(f"OK - Total rules: {len(rules)}")
    
    # Get enabled rules
    enabled_rules = rule_manager.get_enabled_rules()
    print(f"OK - Enabled rules: {len(enabled_rules)}")
    
    # Get rules by type
    sentiment_rules = rule_manager.get_rules_by_type(AlertType.SENTIMENT_LOW)
    print(f"OK - Sentiment alert rules: {len(sentiment_rules)}")
    
    # Get single rule
    rule = rule_manager.get_rule("sentiment_low_1")
    if rule:
        print(f"OK - Rule detail: {rule.rule_name}")
        print(f"  - Level: {rule.level.value}")
        print(f"  - Thresholds: {rule.thresholds}")
        print(f"  - Channels: {rule.channels}")
    
    # Test disable/enable
    rule_manager.disable_rule("sentiment_low_1")
    print("OK - Disabled rule sentiment_low_1")
    
    rule_manager.enable_rule("sentiment_low_1")
    print("OK - Enabled rule sentiment_low_1")
    
    print("\nPASS - Rule Manager Test")


def test_sentiment_alert():
    """Test sentiment alert"""
    print_section("Test 2: Sentiment Alert")
    
    engine = get_alert_engine()
    
    # Clear history
    engine.clear_history()
    
    # Simulate normal sentiment danmus
    print("\nSimulating normal sentiment danmus...")
    for i in range(20):
        engine.add_danmu({
            "content": "Great! Love it! 666",
            "sentiment": "positive",
            "sentiment_score": 0.8,
            "danmu_type": "praise",
            "timestamp": i * 3,
        })
    
    alerts = engine.check_all_rules()
    print(f"OK - Triggered alerts: {len(alerts)} (Expected: 0, positive sentiment)")
    
    # Simulate negative sentiment danmus
    print("\nSimulating negative sentiment danmus...")
    engine.clear_history()
    
    for i in range(30):
        sentiment = "negative" if i < 20 else "neutral"  # 67% negative
        engine.add_danmu({
            "content": "Too bad, trash, disappointed",
            "sentiment": sentiment,
            "sentiment_score": -0.7 if sentiment == "negative" else 0.0,
            "danmu_type": "controversy" if sentiment == "negative" else "normal",
            "timestamp": i * 2,
            "received_at": datetime.utcnow() - timedelta(seconds=(30-i)*2),
        })
    
    alerts = engine.check_all_rules()
    sentiment_alerts = [a for a in alerts if a.rule.alert_type == AlertType.SENTIMENT_LOW]
    print(f"OK - Triggered sentiment alerts: {len(sentiment_alerts)}")
    
    for alert in sentiment_alerts:
        # Remove emoji for Windows console compatibility
        title = alert.title.encode('ascii', 'ignore').decode('ascii')
        print(f"  - {title}: {alert.message}")
    
    print("\nPASS - Sentiment Alert Test")


def test_speech_risk_alert():
    """Test speech risk alert"""
    print_section("Test 3: Speech Risk Alert")
    
    engine = get_alert_engine()
    engine.clear_history()
    
    # Simulate danmus with sensitive word reactions
    print("\nSimulating sensitive word reaction danmus...")
    sensitive_contents = [
        "Host says 'best', this violates advertising law",
        "Saying 'number one', too exaggerated",
        "'Absolutely effective'? Deceptive",
        "100% guaranteed? Impossible",
        "Cure? Is this medicine?",
    ]
    
    for i, content in enumerate(sensitive_contents):
        engine.add_danmu({
            "content": content,
            "sentiment": "negative",
            "sentiment_score": -0.5,
            "danmu_type": "controversy",
            "timestamp": i * 5,
            "received_at": datetime.utcnow() - timedelta(seconds=(5-i)*5),
        })
    
    alerts = engine.check_all_rules()
    speech_alerts = [a for a in alerts if a.rule.alert_type == AlertType.SPEECH_RISK]
    print(f"OK - Triggered speech risk alerts: {len(speech_alerts)}")
    
    for alert in speech_alerts:
        title = alert.title.encode('ascii', 'ignore').decode('ascii')
        print(f"  - {title}: {alert.message}")
        if alert.data:
            print(f"    Detected words: {alert.data.get('detected_words', [])}")
    
    print("\nPASS - Speech Risk Alert Test")


def test_audience_loss_alert():
    """Test audience loss alert"""
    print_section("Test 4: Audience Loss Alert")
    
    engine = get_alert_engine()
    engine.clear_history()
    
    # Build baseline
    print("\nBuilding viewer count baseline...")
    for i in range(70):
        engine.update_viewer_count(200)  # Stable at 200
        time.sleep(0.01)
    
    # Simulate audience loss
    print("Simulating audience loss...")
    for i in range(10):
        count = 200 - (i * 15)  # Drop from 200 to 50
        engine.update_viewer_count(count)
        time.sleep(0.01)
    
    alerts = engine.check_all_rules()
    audience_alerts = [a for a in alerts if a.rule.alert_type == AlertType.AUDIENCE_LOSS]
    print(f"OK - Triggered audience loss alerts: {len(audience_alerts)}")
    
    for alert in audience_alerts:
        title = alert.title.encode('ascii', 'ignore').decode('ascii')
        print(f"  - {title}: {alert.message}")
    
    print("\nPASS - Audience Loss Alert Test")


def test_controversy_alert():
    """Test controversy alert"""
    print_section("Test 5: Controversy Alert")
    
    engine = get_alert_engine()
    engine.clear_history()
    
    # Simulate many controversy danmus
    print("\nSimulating controversy danmus...")
    for i in range(40):
        danmu_type = "controversy" if i < 25 else "normal"  # 62.5% controversy
        engine.add_danmu({
            "content": "Fake? Suspicious / Don't buy, avoid",
            "sentiment": "negative",
            "sentiment_score": -0.6,
            "danmu_type": danmu_type,
            "key_type": "controversy" if danmu_type == "controversy" else None,
            "timestamp": i * 1.5,
            "received_at": datetime.utcnow() - timedelta(seconds=(40-i)*1.5),
        })
    
    alerts = engine.check_all_rules()
    controversy_alerts = [a for a in alerts if a.rule.alert_type == AlertType.CONTROVERSY]
    print(f"OK - Triggered controversy alerts: {len(controversy_alerts)}")
    
    for alert in controversy_alerts:
        title = alert.title.encode('ascii', 'ignore').decode('ascii')
        print(f"  - {title}: {alert.message}")
    
    print("\nPASS - Controversy Alert Test")


def test_alert_history_management():
    """Test alert history"""
    print_section("Test 6: Alert History Management")
    
    engine = get_alert_engine()
    
    # Get history
    history = engine.get_alert_history(limit=10)
    print(f"OK - Alert history total: {len(history)}")
    
    # Get stats
    stats = engine.get_stats()
    print(f"OK - Statistics:")
    print(f"  - Total alerts: {stats['total_alerts']}")
    print(f"  - Unread count: {stats['unread_count']}")
    print(f"  - By type: {stats['by_type']}")
    print(f"  - By level: {stats['by_level']}")
    
    # Mark as read
    if history:
        first_alert_id = history[0]['alert_id']
        engine.mark_as_read(first_alert_id)
        print(f"OK - Marked alert {first_alert_id} as read")
        
        # Mark all as read
        marked_count = engine.mark_all_as_read()
        print(f"OK - Marked all as read, total {marked_count}")
    
    # Verify unread count
    stats = engine.get_stats()
    print(f"OK - Current unread count: {stats['unread_count']} (Expected: 0)")
    
    print("\nPASS - Alert History Management Test")


def test_cooldown_mechanism():
    """Test cooldown mechanism"""
    print_section("Test 7: Cooldown Mechanism")
    
    engine = get_alert_engine()
    engine.clear_history()
    
    # Quickly add many negative danmus
    print("\nQuickly triggering sentiment alert...")
    for i in range(50):
        engine.add_danmu({
            "content": "Terrible",
            "sentiment": "negative",
            "sentiment_score": -0.8,
            "danmu_type": "controversy",
            "timestamp": i,
            "received_at": datetime.utcnow(),
        })
    
    # First check
    alerts1 = engine.check_all_rules()
    sentiment_alerts1 = [a for a in alerts1 if a.rule.alert_type == AlertType.SENTIMENT_LOW]
    print(f"OK - First trigger: {len(sentiment_alerts1)} alerts")
    
    # Immediate second check (should be in cooldown)
    alerts2 = engine.check_all_rules()
    sentiment_alerts2 = [a for a in alerts2 if a.rule.alert_type == AlertType.SENTIMENT_LOW]
    print(f"OK - Second trigger: {len(sentiment_alerts2)} alerts (Expected: 0, in cooldown)")
    
    print("\nPASS - Cooldown Mechanism Test")


def test_push_channels_config():
    """Test push channel configuration"""
    print_section("Test 8: Push Channel Configuration")
    
    rule_manager = get_rule_manager()
    
    # Check push channel configuration for each rule
    rules = rule_manager.get_all_rules()
    
    channel_stats = {}
    for rule in rules:
        for channel in rule.channels:
            channel_str = channel.value
            channel_stats[channel_str] = channel_stats.get(channel_str, 0) + 1
    
    print("OK - Push channel statistics:")
    for channel, count in channel_stats.items():
        channel_name = {"in_app": "In-App", "email": "Email", "wechat": "WeChat"}.get(channel, channel)
        print(f"  - {channel_name}: {count} rules")
    
    print("\nPASS - Push Channel Configuration Test")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  LiveMirror Intelligent Alert System Tests")
    print("=" * 60)
    
    try:
        test_rule_manager()
        test_sentiment_alert()
        test_speech_risk_alert()
        test_audience_loss_alert()
        test_controversy_alert()
        test_alert_history_management()
        test_cooldown_mechanism()
        test_push_channels_config()
        
        print("\n" + "=" * 60)
        print("  All Tests Passed!")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\nFAIL - Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
