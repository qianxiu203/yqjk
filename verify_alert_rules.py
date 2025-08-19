#!/usr/bin/env python3
"""
验证预警规则设置脚本
用于验证新的默认预警规则是否正确加载和工作
"""
import asyncio
from datetime import datetime
from database import DatabaseManager
from alert_system import AlertSystem
from loguru import logger

async def verify_alert_rules():
    """验证预警规则设置"""
    try:
        logger.info("🔍 开始验证预警规则设置...")
        
        # 初始化数据库
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # 初始化预警系统
        alert_system = AlertSystem(db_manager)
        await alert_system.init()
        
        # 获取当前规则
        rules = await alert_system.get_rules()
        alerts = await alert_system.get_alerts(limit=10)
        
        logger.info("📊 当前预警系统状态:")
        logger.info(f"   - 预警规则总数: {len(rules)}")
        logger.info(f"   - 预警记录总数: {len(alerts)}")
        
        # 验证默认规则
        expected_rules = [
            "security_alert",
            "data_monitoring", 
            "technology_trends",
            "financial_monitoring",
            "emergency_events"
        ]
        
        logger.info("📋 验证默认规则:")
        loaded_rule_ids = [rule.get('id') for rule in rules]
        
        for rule_id in expected_rules:
            if rule_id in loaded_rule_ids:
                rule = next((r for r in rules if r.get('id') == rule_id), None)
                if rule:
                    logger.info(f"   ✅ {rule.get('name')} (级别: {rule.get('level')}, 状态: {'启用' if rule.get('enabled') else '禁用'})")
                else:
                    logger.warning(f"   ⚠️  规则 {rule_id} 存在但数据异常")
            else:
                logger.error(f"   ❌ 缺少规则: {rule_id}")
        
        # 检查额外的规则
        extra_rules = [rule_id for rule_id in loaded_rule_ids if rule_id not in expected_rules]
        if extra_rules:
            logger.info("📋 额外的规则:")
            for rule_id in extra_rules:
                rule = next((r for r in rules if r.get('id') == rule_id), None)
                if rule:
                    logger.info(f"   🔧 {rule.get('name')} (ID: {rule_id})")
        
        # 验证规则配置
        logger.info("🔧 验证规则配置:")
        for rule in rules:
            rule_id = rule.get('id')
            conditions = rule.get('conditions', {})
            keywords = conditions.get('keywords', [])
            threshold = conditions.get('threshold', 0)
            time_window = conditions.get('time_window', 0)
            
            logger.info(f"   📝 {rule.get('name')}:")
            logger.info(f"      - 关键词数量: {len(keywords)}")
            logger.info(f"      - 触发阈值: {threshold}")
            logger.info(f"      - 时间窗口: {time_window} 分钟")
            logger.info(f"      - 预警级别: {rule.get('level')}")
        
        # 测试预警检查功能
        logger.info("🧪 测试预警检查功能:")
        try:
            # 获取测试数据
            test_data = await db_manager.get_data_for_alert_analysis(time_window=60)
            logger.info(f"   - 获取测试数据: {len(test_data)} 条")
            
            if test_data:
                # 模拟预警检查
                from keyword_engine import keyword_engine
                
                for rule in rules[:2]:  # 只测试前两个规则
                    conditions = rule.get('conditions', {})
                    target_keywords = conditions.get('keywords', [])
                    time_window = conditions.get('time_window', 60)
                    
                    if target_keywords:
                        result = await keyword_engine.extract_alert_keywords(
                            data=test_data,
                            target_keywords=target_keywords,
                            time_window=time_window
                        )
                        
                        logger.info(f"   📊 {rule.get('name')} 测试结果:")
                        logger.info(f"      - 匹配关键词: {len(result.matched_keywords)}")
                        logger.info(f"      - 总匹配数: {result.total_matches}")
                        
                        if result.matched_keywords:
                            for match in result.matched_keywords[:3]:
                                logger.info(f"      - '{match['word']}': {match['count']} 次")
            else:
                logger.warning("   ⚠️  没有测试数据，跳过功能测试")
                
        except Exception as e:
            logger.error(f"   ❌ 预警检查测试失败: {e}")
        
        # 显示最近的预警记录
        if alerts:
            logger.info("🚨 最近的预警记录:")
            for i, alert in enumerate(alerts[:5], 1):
                triggered_at = alert.get('triggered_at', 'N/A')
                if isinstance(triggered_at, datetime):
                    triggered_at = triggered_at.strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"   {i}. {alert.get('title', 'N/A')}")
                logger.info(f"      - 级别: {alert.get('level', 'N/A')}")
                logger.info(f"      - 状态: {alert.get('status', 'N/A')}")
                logger.info(f"      - 时间: {triggered_at}")
        else:
            logger.info("✨ 当前没有预警记录")
        
        # 关闭连接
        await db_manager.disconnect()
        
        logger.info("🎉 预警规则验证完成！")
        
        return {
            "success": True,
            "total_rules": len(rules),
            "total_alerts": len(alerts),
            "expected_rules_loaded": len([r for r in expected_rules if r in loaded_rule_ids]),
            "extra_rules": len(extra_rules)
        }
        
    except Exception as e:
        logger.error(f"❌ 验证预警规则失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def reset_and_reload_rules():
    """重置并重新加载默认规则"""
    try:
        logger.info("🔄 重置并重新加载默认规则...")
        
        # 初始化数据库
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        # 初始化预警系统
        alert_system = AlertSystem(db_manager)
        await alert_system.init()
        
        # 删除所有现有规则
        logger.info("🧹 删除现有规则...")
        existing_rules = await alert_system.get_rules()
        deleted_count = 0
        
        for rule in existing_rules:
            rule_id = rule.get('id')
            if rule_id:
                success = await alert_system.delete_rule(rule_id)
                if success:
                    deleted_count += 1
                    logger.info(f"   ✅ 删除规则: {rule.get('name')}")
        
        logger.info(f"📊 删除了 {deleted_count} 个现有规则")
        
        # 重新加载默认规则
        logger.info("📥 重新加载默认规则...")
        await alert_system.setup_default_rules()
        await alert_system.load_rules()
        
        # 验证加载结果
        new_rules = await alert_system.get_rules()
        logger.info(f"📊 重新加载了 {len(new_rules)} 个默认规则")
        
        for rule in new_rules:
            logger.info(f"   ✅ {rule.get('name')} (ID: {rule.get('id')})")
        
        # 关闭连接
        await db_manager.disconnect()
        
        logger.info("🎉 规则重置完成！")
        
        return {
            "success": True,
            "deleted_rules": deleted_count,
            "loaded_rules": len(new_rules)
        }
        
    except Exception as e:
        logger.error(f"❌ 重置规则失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # 重置并重新加载规则
        result = await reset_and_reload_rules()
        if result["success"]:
            print(f"\n🎉 重置成功！删除了 {result['deleted_rules']} 个旧规则，加载了 {result['loaded_rules']} 个新规则")
        else:
            print(f"\n❌ 重置失败: {result['error']}")
    else:
        # 验证当前规则
        result = await verify_alert_rules()
        if result["success"]:
            print(f"\n📊 验证完成！")
            print(f"   - 预警规则: {result['total_rules']} 个")
            print(f"   - 预警记录: {result['total_alerts']} 条")
            print(f"   - 默认规则: {result['expected_rules_loaded']}/5 个已加载")
            if result['extra_rules'] > 0:
                print(f"   - 额外规则: {result['extra_rules']} 个")
        else:
            print(f"\n❌ 验证失败: {result['error']}")

if __name__ == "__main__":
    print("🔍 预警规则验证工具")
    print("用法:")
    print("  python verify_alert_rules.py         # 验证当前规则")
    print("  python verify_alert_rules.py --reset # 重置并重新加载默认规则")
    print()
    
    asyncio.run(main())
