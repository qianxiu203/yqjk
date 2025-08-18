"""
定时任务调度模块
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from config import settings, get_sources_by_priority
from collector import DataCollector
from database import db_manager


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已经在运行")
            return
        
        try:
            # 确保数据库连接
            await db_manager.connect()
            
            # 添加定时任务
            await self._add_scheduled_jobs()
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info("任务调度器启动成功")
            
        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
            raise
    
    async def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        
        # 断开数据库连接
        await db_manager.disconnect()
        
        logger.info("任务调度器已停止")
    
    async def _add_scheduled_jobs(self):
        """添加定时任务"""
        
        # 1. 高优先级数据源（每5分钟采集一次）
        self.scheduler.add_job(
            self._collect_high_priority,
            trigger=IntervalTrigger(minutes=5),
            id="collect_high_priority",
            name="采集高优先级数据源",
            max_instances=1,
            coalesce=True
        )
        
        # 2. 中优先级数据源（每15分钟采集一次）
        self.scheduler.add_job(
            self._collect_medium_priority,
            trigger=IntervalTrigger(minutes=15),
            id="collect_medium_priority",
            name="采集中优先级数据源",
            max_instances=1,
            coalesce=True
        )
        
        # 3. 低优先级数据源（每30分钟采集一次）
        self.scheduler.add_job(
            self._collect_low_priority,
            trigger=IntervalTrigger(minutes=30),
            id="collect_low_priority",
            name="采集低优先级数据源",
            max_instances=1,
            coalesce=True
        )
        
        # 4. 全量采集（每小时执行一次）
        self.scheduler.add_job(
            self._collect_all_sources,
            trigger=CronTrigger(minute=0),  # 每小时的0分执行
            id="collect_all_hourly",
            name="全量数据采集",
            max_instances=1,
            coalesce=True
        )
        
        # 5. 数据库维护任务（每天凌晨2点执行）
        self.scheduler.add_job(
            self._database_maintenance,
            trigger=CronTrigger(hour=2, minute=0),
            id="database_maintenance",
            name="数据库维护",
            max_instances=1,
            coalesce=True
        )
        
        # 6. 统计报告生成（每天早上8点执行）
        self.scheduler.add_job(
            self._generate_daily_report,
            trigger=CronTrigger(hour=8, minute=0),
            id="daily_report",
            name="生成日报",
            max_instances=1,
            coalesce=True
        )
        
        logger.info("定时任务添加完成")
    
    async def _collect_high_priority(self):
        """采集高优先级数据源（优先级1）"""
        logger.info("开始执行高优先级数据采集任务")
        try:
            async with DataCollector() as collector:
                result = await collector.collect_by_priority(1)
                logger.info(f"高优先级采集完成: {result}")
        except Exception as e:
            logger.error(f"高优先级采集失败: {e}")
    
    async def _collect_medium_priority(self):
        """采集中优先级数据源（优先级2）"""
        logger.info("开始执行中优先级数据采集任务")
        try:
            async with DataCollector() as collector:
                result = await collector.collect_by_priority(2)
                logger.info(f"中优先级采集完成: {result}")
        except Exception as e:
            logger.error(f"中优先级采集失败: {e}")
    
    async def _collect_low_priority(self):
        """采集低优先级数据源（优先级3）"""
        logger.info("开始执行低优先级数据采集任务")
        try:
            async with DataCollector() as collector:
                result = await collector.collect_by_priority(3)
                logger.info(f"低优先级采集完成: {result}")
        except Exception as e:
            logger.error(f"低优先级采集失败: {e}")
    
    async def _collect_all_sources(self):
        """全量采集所有数据源"""
        logger.info("开始执行全量数据采集任务")
        try:
            async with DataCollector() as collector:
                result = await collector.collect_all_sources()
                logger.info(f"全量采集完成: {result}")
        except Exception as e:
            logger.error(f"全量采集失败: {e}")
    
    async def _database_maintenance(self):
        """数据库维护任务"""
        logger.info("开始执行数据库维护任务")
        try:
            # 这里可以添加数据库清理、索引优化等操作
            stats = await db_manager.get_statistics()
            logger.info(f"数据库统计信息: {stats}")
            
            # 可以添加更多维护操作，如：
            # - 清理过期数据
            # - 重建索引
            # - 数据压缩等
            
        except Exception as e:
            logger.error(f"数据库维护失败: {e}")
    
    async def _generate_daily_report(self):
        """生成日报"""
        logger.info("开始生成日报")
        try:
            stats = await db_manager.get_statistics()
            
            # 生成报告内容
            report = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "statistics": stats,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"日报生成完成: {report}")
            
            # 这里可以添加报告发送逻辑，如：
            # - 发送邮件
            # - 推送到消息系统
            # - 保存到文件等
            
        except Exception as e:
            logger.error(f"生成日报失败: {e}")
    
    def get_job_status(self) -> dict:
        """获取任务状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.is_running,
            "jobs": jobs
        }
    
    async def run_job_now(self, job_id: str) -> bool:
        """立即执行指定任务"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now())
                logger.info(f"任务 {job_id} 已安排立即执行")
                return True
            else:
                logger.warning(f"未找到任务: {job_id}")
                return False
        except Exception as e:
            logger.error(f"执行任务失败 {job_id}: {e}")
            return False


# 创建全局调度器实例
task_scheduler = TaskScheduler()
