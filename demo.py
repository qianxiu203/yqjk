#!/usr/bin/env python3
"""
舆情监控平台功能演示脚本
"""
import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def demo_data_collection():
    """演示数据采集功能"""
    print("🔍 演示数据采集功能")
    print("-" * 30)
    
    try:
        from collector import DataCollector
        from database import db_manager
        
        # 连接数据库
        await db_manager.connect()
        
        # 演示单个数据源采集
        print("1. 采集单个数据源（知乎）...")
        async with DataCollector() as collector:
            result = await collector.collect_single_source("zhihu")
            print(f"   结果: {result}")
        
        # 演示按优先级采集
        print("\n2. 按优先级采集（优先级1）...")
        async with DataCollector() as collector:
            result = await collector.collect_by_priority(1)
            print(f"   结果: 采集了 {result.get('total_items', 0)} 条数据")
        
        # 断开数据库连接
        await db_manager.disconnect()
        
        print("✅ 数据采集演示完成")
        
    except Exception as e:
        print(f"❌ 数据采集演示失败: {e}")


async def demo_database_operations():
    """演示数据库操作功能"""
    print("\n🗄️  演示数据库操作功能")
    print("-" * 30)
    
    try:
        from database import db_manager
        
        # 连接数据库
        await db_manager.connect()
        
        # 获取统计信息
        print("1. 获取统计信息...")
        stats = await db_manager.get_statistics()
        print(f"   总数据量: {stats.get('total_count', 0)}")
        print(f"   今日新增: {stats.get('today_count', 0)}")
        
        # 查询最新数据
        print("\n2. 查询最新数据...")
        latest_data = await db_manager.find_data(limit=5)
        print(f"   查询到 {len(latest_data)} 条最新数据")
        
        # 搜索功能演示
        print("\n3. 搜索功能演示...")
        try:
            search_results = await db_manager.search_data("科技", limit=3)
            print(f"   搜索到 {len(search_results)} 条相关数据")
        except Exception as e:
            print(f"   搜索功能需要全文索引支持: {e}")
        
        # 断开数据库连接
        await db_manager.disconnect()
        
        print("✅ 数据库操作演示完成")
        
    except Exception as e:
        print(f"❌ 数据库操作演示失败: {e}")


async def demo_scheduler():
    """演示调度器功能"""
    print("\n⏰ 演示调度器功能")
    print("-" * 30)
    
    try:
        from scheduler import task_scheduler
        
        # 启动调度器
        print("1. 启动调度器...")
        await task_scheduler.start()
        
        # 获取任务状态
        print("\n2. 获取任务状态...")
        status = task_scheduler.get_job_status()
        print(f"   调度器运行状态: {status['scheduler_running']}")
        print(f"   任务数量: {len(status['jobs'])}")
        
        for job in status['jobs'][:3]:  # 显示前3个任务
            print(f"   - {job['name']}: {job.get('next_run', '未安排')}")
        
        # 等待几秒钟
        print("\n3. 调度器运行中...")
        await asyncio.sleep(3)
        
        # 停止调度器
        print("\n4. 停止调度器...")
        await task_scheduler.stop()
        
        print("✅ 调度器演示完成")
        
    except Exception as e:
        print(f"❌ 调度器演示失败: {e}")


def demo_web_features():
    """演示Web功能"""
    print("\n🌐 Web功能特性")
    print("-" * 30)
    
    features = [
        "📊 系统状态监控 - 实时监控API、数据库、调度器、采集器状态",
        "📈 数据概览 - 55个数据源统计、新闻条目、采集成功率、文档数量",
        "🏷️  关键词分析 - 热门关键词排行、词汇统计、点击搜索、实时更新",
        "🔍 新闻检索 - 最新新闻列表、智能搜索、分页显示、数据源标识",
        "📊 数据可视化 - 7天趋势图、数据源分析、交互式图表、动态切换"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i}. {feature}")
    
    print("\n💡 使用说明:")
    print("   - 启动服务: python main.py")
    print("   - 访问界面: http://localhost:8000")
    print("   - API文档: http://localhost:8000/docs")


async def demo_api_endpoints():
    """演示API接口"""
    print("\n🔌 API接口演示")
    print("-" * 30)
    
    endpoints = [
        ("GET /api/health", "健康检查"),
        ("GET /api/statistics", "统计信息"),
        ("GET /api/data", "查询数据"),
        ("GET /api/search", "全文搜索"),
        ("GET /api/keywords", "热门关键词"),
        ("GET /api/trends", "数据趋势"),
        ("GET /api/system/status", "系统状态"),
        ("POST /api/collect", "手动采集"),
        ("GET /api/scheduler/status", "调度器状态")
    ]
    
    print("可用的API接口:")
    for endpoint, description in endpoints:
        print(f"   {endpoint:<25} - {description}")
    
    print("\n📝 API使用示例:")
    print("   curl http://localhost:8000/api/health")
    print("   curl http://localhost:8000/api/statistics")
    print("   curl 'http://localhost:8000/api/search?keyword=人工智能'")


def demo_deployment():
    """演示部署选项"""
    print("\n🚀 部署选项")
    print("-" * 30)
    
    options = [
        ("本地部署", "python deploy.py && python main.py"),
        ("Docker部署", "docker-compose up -d"),
        ("开发模式", "python main.py --debug"),
        ("仅采集器", "python main.py --mode collector"),
        ("单次采集", "python main.py --mode once")
    ]
    
    for option, command in options:
        print(f"   {option:<10}: {command}")


async def run_full_demo():
    """运行完整演示"""
    print("🎭 舆情监控平台功能演示")
    print("=" * 50)
    
    # 数据采集演示
    await demo_data_collection()
    
    # 数据库操作演示
    await demo_database_operations()
    
    # 调度器演示
    await demo_scheduler()
    
    # Web功能介绍
    demo_web_features()
    
    # API接口介绍
    await demo_api_endpoints()
    
    # 部署选项介绍
    demo_deployment()
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("💡 提示: 运行 'python main.py' 启动完整服务")


async def quick_demo():
    """快速演示"""
    print("⚡ 快速功能演示")
    print("=" * 30)
    
    # Web功能介绍
    demo_web_features()
    
    # API接口介绍
    await demo_api_endpoints()
    
    print("\n✨ 主要特性:")
    print("   - 55个数据源自动采集")
    print("   - MongoDB存储，TTL 180天")
    print("   - 响应式Web界面")
    print("   - 实时系统监控")
    print("   - 关键词分析")
    print("   - 数据可视化")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="舆情监控平台功能演示")
    parser.add_argument(
        "--mode",
        choices=["full", "quick"],
        default="quick",
        help="演示模式: full(完整演示), quick(快速演示)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "full":
            asyncio.run(run_full_demo())
        else:
            asyncio.run(quick_demo())
    except KeyboardInterrupt:
        print("\n👋 演示被中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")


if __name__ == "__main__":
    main()
