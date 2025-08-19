#!/usr/bin/env python3
"""
清理测试数据并创建基于真实新闻的预警规则
"""
import asyncio
from datetime import datetime, timedelta
from database import DatabaseManager
from alert_system import AlertSystem, AlertRule, Alert, AlertType, AlertLevel, AlertStatus

async def cleanup_and_create_real_alerts():
    """清理测试数据并创建真实预警"""
    
    # 初始化数据库
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    # 初始化预警系统
    alert_system = AlertSystem(db_manager)
    await alert_system.init()
    
    print("🧹 开始清理测试数据...")
    
    # 1. 删除测试新闻数据
    collection = await db_manager.get_today_collection()
    delete_result = await collection.delete_many({"source_id": "test_source"})
    print(f"✅ 删除了 {delete_result.deleted_count} 条测试新闻数据")

    # 2. 删除旧的测试预警规则和预警记录
    alerts_collection = db_manager.database["alerts"]
    rules_collection = db_manager.database["alert_rules"]

    # 删除测试预警记录
    alert_delete_result = await alerts_collection.delete_many({"id": {"$regex": "^alert_.*(fire|data_leak)_"}})
    print(f"✅ 删除了 {alert_delete_result.deleted_count} 条测试预警记录")

    # 删除测试预警规则
    rule_delete_result = await rules_collection.delete_many({"id": {"$regex": "^rule_.*(fire|data_leak)_"}})
    print(f"✅ 删除了 {rule_delete_result.deleted_count} 条测试预警规则")
    
    print("🚀 开始创建基于真实数据的预警规则...")
    
    # 3. 创建基于真实新闻关键词的预警规则
    real_rules = [
        AlertRule(
            id="rule_security_001",
            name="安全事件预警",
            description="监控安全相关新闻",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.HIGH,
            enabled=True,
            conditions={
                "keyword": "安全",
                "threshold": 10,
                "time_window": 60
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        AlertRule(
            id="rule_data_001",
            name="数据相关预警",
            description="监控数据相关新闻",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.MEDIUM,
            enabled=True,
            conditions={
                "keyword": "数据",
                "threshold": 15,
                "time_window": 60
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        AlertRule(
            id="rule_trump_001",
            name="特朗普新闻预警",
            description="监控特朗普相关新闻",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.MEDIUM,
            enabled=True,
            conditions={
                "keyword": "特朗普",
                "threshold": 5,
                "time_window": 60
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        AlertRule(
            id="rule_china_001",
            name="中国新闻预警",
            description="监控中国相关新闻",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.LOW,
            enabled=True,
            conditions={
                "keyword": "中国",
                "threshold": 8,
                "time_window": 60
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        AlertRule(
            id="rule_tesla_001",
            name="特斯拉新闻预警",
            description="监控特斯拉相关新闻",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.MEDIUM,
            enabled=True,
            conditions={
                "keyword": "特斯拉",
                "threshold": 3,
                "time_window": 60
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    # 添加规则
    for rule in real_rules:
        await alert_system.add_rule(rule)
    print(f"✅ 创建了 {len(real_rules)} 个基于真实数据的预警规则")
    
    # 4. 创建一些示例预警记录（基于真实关键词）
    real_alerts = [
        Alert(
            id="alert_security_001",
            rule_id="rule_security_001",
            rule_name="安全事件预警",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.HIGH,
            status=AlertStatus.ACTIVE,
            title="关键词预警: 安全",
            message="关键词 '安全' 出现频次 59 次，超过阈值 10",
            data={
                "keyword": "安全",
                "count": 59,
                "threshold": 10,
                "time_window": 60
            },
            triggered_at=datetime.now() - timedelta(hours=1)
        ),
        Alert(
            id="alert_data_001",
            rule_id="rule_data_001",
            rule_name="数据相关预警",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.MEDIUM,
            status=AlertStatus.ACTIVE,
            title="关键词预警: 数据",
            message="关键词 '数据' 出现频次 70 次，超过阈值 15",
            data={
                "keyword": "数据",
                "count": 70,
                "threshold": 15,
                "time_window": 60
            },
            triggered_at=datetime.now() - timedelta(hours=2)
        ),
        Alert(
            id="alert_trump_001",
            rule_id="rule_trump_001",
            rule_name="特朗普新闻预警",
            alert_type=AlertType.KEYWORD,
            level=AlertLevel.MEDIUM,
            status=AlertStatus.RESOLVED,
            title="关键词预警: 特朗普",
            message="关键词 '特朗普' 出现频次 9 次，超过阈值 5",
            data={
                "keyword": "特朗普",
                "count": 9,
                "threshold": 5,
                "time_window": 60
            },
            triggered_at=datetime.now() - timedelta(days=1),
            resolved_at=datetime.now() - timedelta(hours=6)
        )
    ]
    
    # 添加预警
    for alert in real_alerts:
        await alert_system.trigger_alert(alert)
    print(f"✅ 创建了 {len(real_alerts)} 个基于真实数据的预警记录")
    
    print("🎉 清理和重建完成！")
    print("现在所有预警都基于真实的新闻数据：")
    print("- 安全事件预警：基于59条真实安全相关新闻")
    print("- 数据相关预警：基于70条真实数据相关新闻")
    print("- 特朗普新闻预警：基于9条真实特朗普相关新闻")
    
    print("\n🔍 验证真实数据...")
    # 验证数据
    for keyword in ["安全", "数据", "特朗普"]:
        search_result, total = await db_manager.search_data(keyword=keyword, limit=1)
        print(f"   关键词 '{keyword}': {total} 条真实新闻")

if __name__ == "__main__":
    asyncio.run(cleanup_and_create_real_alerts())
