#!/usr/bin/env python3
"""
创建测试预警数据
"""
import asyncio
from datetime import datetime, timedelta
from database import DatabaseManager
from alert_system import AlertSystem, AlertRule, Alert, AlertType, AlertLevel, AlertStatus

async def create_test_data():
    """创建测试预警数据"""
    
    # 初始化数据库
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    # 初始化预警系统
    alert_system = AlertSystem(db_manager)
    await alert_system.init()
    
    print("🚀 开始创建测试预警数据...")
    
    # 1. 创建预警规则
    rule1 = AlertRule(
        id="rule_fire_001",
        name="火灾预警",
        description="监控火灾相关新闻",
        alert_type=AlertType.KEYWORD,
        level=AlertLevel.HIGH,
        enabled=True,
        conditions={
            "keyword": "火灾",
            "threshold": 3,
            "time_window": 60
        },
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    rule2 = AlertRule(
        id="rule_data_leak_001",
        name="数据泄露预警",
        description="监控数据泄露相关新闻",
        alert_type=AlertType.KEYWORD,
        level=AlertLevel.CRITICAL,
        enabled=True,
        conditions={
            "keyword": "数据泄露",
            "threshold": 2,
            "time_window": 30
        },
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 添加规则
    await alert_system.add_rule(rule1)
    await alert_system.add_rule(rule2)
    print("✅ 创建了2个预警规则")
    
    # 2. 创建预警记录
    alert1 = Alert(
        id="alert_fire_001",
        rule_id="rule_fire_001",
        rule_name="火灾预警",
        alert_type=AlertType.KEYWORD,
        level=AlertLevel.HIGH,
        status=AlertStatus.ACTIVE,
        title="关键词预警: 火灾",
        message="关键词 '火灾' 出现频次 5 次，超过阈值 3",
        data={
            "keyword": "火灾",
            "count": 5,
            "threshold": 3,
            "time_window": 60
        },
        triggered_at=datetime.now() - timedelta(hours=2)
    )
    
    alert2 = Alert(
        id="alert_data_leak_001",
        rule_id="rule_data_leak_001",
        rule_name="数据泄露预警",
        alert_type=AlertType.KEYWORD,
        level=AlertLevel.CRITICAL,
        status=AlertStatus.ACTIVE,
        title="关键词预警: 数据泄露",
        message="关键词 '数据泄露' 出现频次 3 次，超过阈值 2",
        data={
            "keyword": "数据泄露",
            "count": 3,
            "threshold": 2,
            "time_window": 30
        },
        triggered_at=datetime.now() - timedelta(hours=1)
    )
    
    alert3 = Alert(
        id="alert_fire_002",
        rule_id="rule_fire_001",
        rule_name="火灾预警",
        alert_type=AlertType.KEYWORD,
        level=AlertLevel.HIGH,
        status=AlertStatus.RESOLVED,
        title="关键词预警: 火灾",
        message="关键词 '火灾' 出现频次 4 次，超过阈值 3",
        data={
            "keyword": "火灾",
            "count": 4,
            "threshold": 3,
            "time_window": 60
        },
        triggered_at=datetime.now() - timedelta(days=1),
        resolved_at=datetime.now() - timedelta(hours=12)
    )
    
    # 添加预警
    await alert_system.trigger_alert(alert1)
    await alert_system.trigger_alert(alert2)
    await alert_system.trigger_alert(alert3)
    print("✅ 创建了3个预警记录")
    
    print("🎉 测试数据创建完成！")
    print("- 2个预警规则")
    print("- 3个预警记录（2个活跃，1个已解决）")
    
    # 关闭连接
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(create_test_data())
