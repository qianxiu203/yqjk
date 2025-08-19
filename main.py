#!/usr/bin/env python3
"""
舆情监控平台主启动文件
"""
import asyncio
import sys
import os
from pathlib import Path
from loguru import logger
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings
from database import db_manager
from scheduler import task_scheduler
from alert_system import init_alert_system


def setup_logging():
    """配置日志"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置loguru
    logger.remove()  # 移除默认处理器
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 文件输出
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )


async def startup():
    """启动应用"""
    logger.info("=" * 50)
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 50)
    
    try:
        # 连接数据库
        logger.info("连接数据库...")
        await db_manager.connect()
        
        # 启动调度器
        logger.info("启动任务调度器...")
        await task_scheduler.start()

        # 初始化预警系统
        logger.info("初始化预警系统...")
        await init_alert_system(db_manager)

        logger.info("应用启动完成")
        return True
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return False


async def shutdown():
    """关闭应用"""
    logger.info("正在关闭应用...")
    
    try:
        # 停止调度器
        await task_scheduler.stop()
        
        # 断开数据库连接
        await db_manager.disconnect()
        
        logger.info("应用已安全关闭")
        
    except Exception as e:
        logger.error(f"关闭时出现错误: {e}")


def run_server():
    """运行Web服务器"""
    setup_logging()
    
    logger.info(f"启动Web服务器: http://{settings.HOST}:{settings.PORT}")
    
    # 配置uvicorn
    config = uvicorn.Config(
        "api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")
    finally:
        # 确保清理资源
        asyncio.run(shutdown())


async def run_collector_only():
    """仅运行数据采集器（不启动Web服务）"""
    setup_logging()
    
    logger.info("启动数据采集器模式")
    
    if not await startup():
        return
    
    try:
        # 保持运行，让调度器工作
        while True:
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    finally:
        await shutdown()


async def run_single_collection():
    """执行一次性数据采集"""
    setup_logging()
    
    logger.info("执行一次性数据采集")
    
    try:
        # 连接数据库
        await db_manager.connect()
        
        # 执行采集
        from collector import DataCollector
        async with DataCollector() as collector:
            result = await collector.collect_all_sources()
            logger.info(f"采集完成: {result}")
        
    except Exception as e:
        logger.error(f"采集失败: {e}")
    finally:
        await db_manager.disconnect()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="舆情监控平台")
    parser.add_argument(
        "--mode",
        choices=["server", "collector", "once"],
        default="server",
        help="运行模式: server(Web服务), collector(仅采集器), once(单次采集)"
    )
    parser.add_argument(
        "--host",
        default=settings.HOST,
        help=f"服务器地址 (默认: {settings.HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help=f"服务器端口 (默认: {settings.PORT})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    args = parser.parse_args()
    
    # 更新配置
    if args.host != settings.HOST:
        settings.HOST = args.host
    if args.port != settings.PORT:
        settings.PORT = args.port
    if args.debug:
        settings.DEBUG = True
        settings.LOG_LEVEL = "DEBUG"
    
    # 根据模式运行
    if args.mode == "server":
        run_server()
    elif args.mode == "collector":
        asyncio.run(run_collector_only())
    elif args.mode == "once":
        asyncio.run(run_single_collection())


if __name__ == "__main__":
    main()
