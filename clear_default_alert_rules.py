#!/usr/bin/env python3
"""
清理默认预警规则脚本
用于删除数据库中的所有默认预警规则和相关预警记录
"""
import asyncio
from datetime import datetime
from database import DatabaseManager
from alert_system import AlertSystem
from loguru import logger

# 默认预警规则ID列表（需要删除的规则）
DEFAULT_RULE_IDS = [
    "emergency_keywords",
    "negative_sentiment", 
    "security_keywords",
    "health_emergency",
    "economic_crisis",
    "political_sensitive",
    "environmental_disaster",
    "technology_crisis",
    "high_frequency_keywords",
    "spam_keywords",
    # 之前创建的测试规则
    "rule_security_001",
    "rule_data_001",
    "rule_trump_001",
    "rule_china_001",
    "rule_tesla_001",
    "rule_fire_001",
    "rule_data_leak_001"
]

async def clear_default_alert_rules():
    """清理默认预警规则"""
    try:
        logger.info("🧹 开始清理默认预警规则...")
        
        # 初始化数据库
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # 初始化预警系统
        alert_system = AlertSystem(db_manager)
        await alert_system.init()
        
        # 统计信息
        deleted_rules = 0
        deleted_alerts = 0
        
        # 1. 删除预警规则
        logger.info("📋 删除预警规则...")
        for rule_id in DEFAULT_RULE_IDS:
            try:
                success = await alert_system.delete_rule(rule_id)
                if success:
                    deleted_rules += 1
                    logger.info(f"✅ 删除预警规则: {rule_id}")
                else:
                    logger.debug(f"⚠️  预警规则不存在: {rule_id}")
            except Exception as e:
                logger.error(f"❌ 删除预警规则失败 {rule_id}: {e}")
        
        # 2. 删除相关的预警记录
        logger.info("🚨 删除相关预警记录...")
        try:
            alerts_collection = db_manager.database["alerts"]
            
            # 删除与默认规则相关的预警记录
            for rule_id in DEFAULT_RULE_IDS:
                result = await alerts_collection.delete_many({"rule_id": rule_id})
                if result.deleted_count > 0:
                    deleted_alerts += result.deleted_count
                    logger.info(f"✅ 删除预警记录 {result.deleted_count} 条，规则ID: {rule_id}")
            
            # 删除包含特定关键词的预警记录（清理测试数据）
            test_keywords = ["火灾", "数据泄露", "特朗普", "安全", "数据"]
            for keyword in test_keywords:
                result = await alerts_collection.delete_many({
                    "title": {"$regex": keyword, "$options": "i"}
                })
                if result.deleted_count > 0:
                    deleted_alerts += result.deleted_count
                    logger.info(f"✅ 删除包含'{keyword}'的预警记录 {result.deleted_count} 条")
                    
        except Exception as e:
            logger.error(f"❌ 删除预警记录失败: {e}")
        
        # 3. 验证清理结果
        logger.info("🔍 验证清理结果...")
        remaining_rules = await alert_system.get_rules()
        remaining_alerts = await alert_system.get_alerts(limit=1000)
        
        logger.info("🎉 清理完成！")
        logger.info(f"📊 清理统计:")
        logger.info(f"   - 删除预警规则: {deleted_rules} 个")
        logger.info(f"   - 删除预警记录: {deleted_alerts} 条")
        logger.info(f"   - 剩余预警规则: {len(remaining_rules)} 个")
        logger.info(f"   - 剩余预警记录: {len(remaining_alerts)} 条")
        
        # 显示剩余的规则（如果有）
        if remaining_rules:
            logger.info("📋 剩余的预警规则:")
            for rule in remaining_rules:
                logger.info(f"   - {rule.get('name', 'N/A')} (ID: {rule.get('id', 'N/A')})")
        else:
            logger.info("✨ 所有默认预警规则已清理完毕，系统现在是干净状态")
        
        # 关闭连接
        await db_manager.disconnect()
        
        return {
            "success": True,
            "deleted_rules": deleted_rules,
            "deleted_alerts": deleted_alerts,
            "remaining_rules": len(remaining_rules),
            "remaining_alerts": len(remaining_alerts)
        }
        
    except Exception as e:
        logger.error(f"❌ 清理默认预警规则失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def show_current_rules():
    """显示当前的预警规则"""
    try:
        logger.info("📋 查看当前预警规则...")
        
        # 初始化数据库
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # 初始化预警系统
        alert_system = AlertSystem(db_manager)
        await alert_system.init()
        
        # 获取所有规则
        rules = await alert_system.get_rules()
        alerts = await alert_system.get_alerts(limit=100)
        
        logger.info(f"📊 当前状态:")
        logger.info(f"   - 预警规则总数: {len(rules)}")
        logger.info(f"   - 预警记录总数: {len(alerts)}")
        
        if rules:
            logger.info("📋 当前预警规则列表:")
            for i, rule in enumerate(rules, 1):
                logger.info(f"   {i}. {rule.get('name', 'N/A')} (ID: {rule.get('id', 'N/A')}, 级别: {rule.get('level', 'N/A')})")
        else:
            logger.info("✨ 当前没有预警规则")
        
        if alerts:
            logger.info("🚨 最近的预警记录:")
            for i, alert in enumerate(alerts[:5], 1):
                logger.info(f"   {i}. {alert.get('title', 'N/A')} (状态: {alert.get('status', 'N/A')})")
        else:
            logger.info("✨ 当前没有预警记录")
        
        # 关闭连接
        await db_manager.disconnect()
        
    except Exception as e:
        logger.error(f"❌ 查看当前规则失败: {e}")

async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--show":
        # 只显示当前规则，不删除
        await show_current_rules()
    else:
        # 执行清理操作
        print("⚠️  警告：此操作将删除所有默认预警规则和相关预警记录！")
        print("📋 将要删除的规则ID:")
        for rule_id in DEFAULT_RULE_IDS:
            print(f"   - {rule_id}")
        
        confirm = input("\n确认执行清理操作吗？(输入 'yes' 确认): ")
        if confirm.lower() == 'yes':
            result = await clear_default_alert_rules()
            if result["success"]:
                print(f"\n🎉 清理成功！删除了 {result['deleted_rules']} 个规则和 {result['deleted_alerts']} 条预警记录")
            else:
                print(f"\n❌ 清理失败: {result['error']}")
        else:
            print("❌ 操作已取消")

if __name__ == "__main__":
    print("🧹 默认预警规则清理工具")
    print("用法:")
    print("  python clear_default_alert_rules.py          # 清理默认规则")
    print("  python clear_default_alert_rules.py --show   # 只查看当前规则")
    print()
    
    asyncio.run(main())
