#!/usr/bin/env python3
"""
测试预警重新激活功能
验证预警规则的循环使用机制
"""
import asyncio
from datetime import datetime, timedelta
from database import DatabaseManager
from alert_system import AlertSystem
from loguru import logger

async def test_alert_reactivation():
    """测试预警重新激活功能"""
    try:
        logger.info("🧪 开始测试预警重新激活功能...")
        
        # 初始化数据库和预警系统
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        alert_system = AlertSystem(db_manager)
        await alert_system.init()
        
        # 测试数据
        test_keywords = [
            {"word": "测试关键词", "count": 10},
            {"word": "安全", "count": 20},
            {"word": "数据", "count": 25}
        ]
        
        logger.info("📋 第一轮：触发新预警")
        
        # 第一轮：触发新预警
        for keyword_data in test_keywords:
            await alert_system.check_keyword_alerts([keyword_data])
        
        # 查看活跃预警
        active_alerts = await alert_system.get_alerts(status="active")
        logger.info(f"✅ 第一轮触发后，活跃预警数量: {len(active_alerts)}")
        
        for alert in active_alerts:
            logger.info(f"   - {alert['title']}: {alert['message']}")
        
        # 等待一下
        await asyncio.sleep(1)
        
        logger.info("📋 第二轮：解决所有预警")
        
        # 第二轮：解决所有预警
        for alert in active_alerts:
            await alert_system.resolve_alert(alert['id'])
            logger.info(f"✅ 解决预警: {alert['title']}")
        
        # 验证预警已解决
        active_alerts_after_resolve = await alert_system.get_alerts(status="active")
        resolved_alerts = await alert_system.get_alerts(status="resolved")
        
        logger.info(f"📊 解决后状态:")
        logger.info(f"   - 活跃预警: {len(active_alerts_after_resolve)} 个")
        logger.info(f"   - 已解决预警: {len(resolved_alerts)} 个")
        
        # 等待一下
        await asyncio.sleep(1)
        
        logger.info("📋 第三轮：重新触发相同关键词（应该重新激活）")
        
        # 第三轮：重新触发相同关键词，但计数更高
        enhanced_keywords = [
            {"word": "测试关键词", "count": 15},  # 增加计数
            {"word": "安全", "count": 30},
            {"word": "数据", "count": 35}
        ]
        
        for keyword_data in enhanced_keywords:
            await alert_system.check_keyword_alerts([keyword_data])
        
        # 查看重新激活后的状态
        reactivated_alerts = await alert_system.get_alerts(status="active")
        all_alerts = await alert_system.get_alerts()
        
        logger.info(f"📊 重新激活后状态:")
        logger.info(f"   - 活跃预警: {len(reactivated_alerts)} 个")
        logger.info(f"   - 总预警: {len(all_alerts)} 个")
        
        logger.info("📋 重新激活的预警详情:")
        for alert in reactivated_alerts:
            reactivation_count = alert.get('data', {}).get('reactivation_count', 0)
            last_updated = alert.get('data', {}).get('last_updated', 'N/A')
            
            logger.info(f"   - {alert['title']}")
            logger.info(f"     消息: {alert['message']}")
            logger.info(f"     重新激活次数: {reactivation_count}")
            logger.info(f"     最后更新: {last_updated}")
            logger.info(f"     状态: {alert['status']}")
        
        logger.info("📋 第四轮：再次更新相同关键词（应该更新现有预警）")
        
        # 第四轮：再次更新，测试更新现有活跃预警
        updated_keywords = [
            {"word": "测试关键词", "count": 20},  # 再次增加计数
            {"word": "安全", "count": 40}
        ]
        
        for keyword_data in updated_keywords:
            await alert_system.check_keyword_alerts([keyword_data])
        
        # 查看更新后的状态
        updated_alerts = await alert_system.get_alerts(status="active")
        
        logger.info("📋 更新后的预警详情:")
        for alert in updated_alerts:
            if alert.get('data', {}).get('keyword') in ['测试关键词', '安全']:
                reactivation_count = alert.get('data', {}).get('reactivation_count', 0)
                last_updated = alert.get('data', {}).get('last_updated', 'N/A')
                count = alert.get('data', {}).get('count', 0)
                
                logger.info(f"   - {alert['title']}")
                logger.info(f"     当前计数: {count}")
                logger.info(f"     重新激活次数: {reactivation_count}")
                logger.info(f"     最后更新: {last_updated}")
        
        # 清理测试数据
        logger.info("🧹 清理测试数据...")
        test_alert_ids = []
        for alert in all_alerts:
            if alert.get('data', {}).get('keyword') in ['测试关键词', '安全', '数据']:
                test_alert_ids.append(alert['id'])
        
        # 删除测试预警
        alerts_collection = db_manager.database["alerts"]
        for alert_id in test_alert_ids:
            await alerts_collection.delete_one({"id": alert_id})
            logger.info(f"🗑️  删除测试预警: {alert_id}")
        
        # 关闭连接
        await db_manager.disconnect()
        
        logger.info("🎉 预警重新激活功能测试完成！")
        
        return {
            "success": True,
            "test_results": {
                "initial_alerts": len(active_alerts),
                "resolved_alerts": len(resolved_alerts),
                "reactivated_alerts": len(reactivated_alerts),
                "final_alerts": len(updated_alerts)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 测试预警重新激活功能失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def test_alert_id_consistency():
    """测试预警ID的一致性"""
    try:
        logger.info("🔍 测试预警ID一致性...")
        
        # 初始化数据库和预警系统
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        alert_system = AlertSystem(db_manager)
        await alert_system.init()
        
        # 获取一个测试规则
        rules = await alert_system.get_rules()
        if not rules:
            logger.warning("没有找到预警规则，跳过ID一致性测试")
            return {"success": True, "skipped": True}
        
        test_rule = rules[0]
        test_keyword = "ID测试关键词"
        
        # 生成预警ID（模拟系统逻辑）
        expected_id = f"{test_rule['id']}_{test_keyword}"
        
        logger.info(f"📝 测试规则: {test_rule['name']}")
        logger.info(f"📝 测试关键词: {test_keyword}")
        logger.info(f"📝 期望的预警ID: {expected_id}")
        
        # 触发预警
        await alert_system.check_keyword_alerts([{"word": test_keyword, "count": 100}])
        
        # 查找生成的预警
        alerts_collection = db_manager.database["alerts"]
        generated_alert = await alerts_collection.find_one({"id": expected_id})
        
        if generated_alert:
            logger.info(f"✅ 预警ID一致性测试通过: {generated_alert['id']}")
            
            # 清理测试数据
            await alerts_collection.delete_one({"id": expected_id})
            logger.info("🧹 清理测试数据完成")
            
            result = {"success": True, "id_consistent": True}
        else:
            logger.error(f"❌ 预警ID不一致，期望: {expected_id}")
            result = {"success": False, "id_consistent": False}
        
        await db_manager.disconnect()
        return result
        
    except Exception as e:
        logger.error(f"❌ 测试预警ID一致性失败: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--id-test":
        # 只测试ID一致性
        result = await test_alert_id_consistency()
        if result["success"]:
            if result.get("skipped"):
                print("⚠️  ID一致性测试跳过（没有预警规则）")
            elif result.get("id_consistent"):
                print("✅ 预警ID一致性测试通过")
            else:
                print("❌ 预警ID一致性测试失败")
        else:
            print(f"❌ ID测试失败: {result.get('error', 'Unknown error')}")
    else:
        # 完整的重新激活测试
        result = await test_alert_reactivation()
        if result["success"]:
            test_results = result["test_results"]
            print("🎉 预警重新激活功能测试完成！")
            print(f"📊 测试结果:")
            print(f"   - 初始预警: {test_results['initial_alerts']} 个")
            print(f"   - 解决预警: {test_results['resolved_alerts']} 个")
            print(f"   - 重新激活: {test_results['reactivated_alerts']} 个")
            print(f"   - 最终预警: {test_results['final_alerts']} 个")
        else:
            print(f"❌ 测试失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("🧪 预警重新激活功能测试工具")
    print("用法:")
    print("  python test_alert_reactivation.py           # 完整功能测试")
    print("  python test_alert_reactivation.py --id-test # 只测试ID一致性")
    print()
    
    asyncio.run(main())
