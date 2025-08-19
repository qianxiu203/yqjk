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
from alert_system import get_alert_system


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

        # 7. 预警检查（每10分钟执行一次）
        self.scheduler.add_job(
            self._check_alerts,
            trigger=IntervalTrigger(minutes=10),
            id="check_alerts",
            name="预警检查",
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

    async def _check_alerts(self):
        """检查预警（优化版）"""
        try:
            logger.info("开始预警检查...")

            alert_system = get_alert_system()
            if not alert_system:
                logger.warning("预警系统未初始化，跳过预警检查")
                return

            # 使用新的关键词分析引擎进行预警检查
            try:
                from keyword_engine import keyword_engine

                # 获取预警分析数据（最近60分钟）
                data = await db_manager.get_data_for_alert_analysis(time_window=60)

                if not data:
                    logger.info("没有找到预警分析数据，跳过预警检查")
                    return

                # 获取所有启用的预警规则
                rules = await alert_system.get_rules()
                if not rules:
                    logger.info("没有启用的预警规则，跳过预警检查")
                    return

                # 为每个关键词预警规则执行检查
                total_checks = 0
                for rule in rules:
                    if rule.get('alert_type') != 'keyword' or not rule.get('enabled'):
                        continue

                    try:
                        # 获取规则的目标关键词
                        conditions = rule.get('conditions', {})
                        target_keywords = conditions.get('keywords', [])
                        time_window = conditions.get('time_window', 60)

                        if not target_keywords:
                            continue

                        # 使用关键词分析引擎进行匹配
                        alert_result = await keyword_engine.extract_alert_keywords(
                            data=data,
                            target_keywords=target_keywords,
                            time_window=time_window
                        )

                        # 检查是否触发预警
                        threshold = conditions.get('threshold', 0)
                        for matched_keyword in alert_result.matched_keywords:
                            if matched_keyword['count'] >= threshold:
                                # 构造预警数据格式（兼容原有接口）
                                keyword_data = {
                                    "word": matched_keyword['word'],
                                    "count": matched_keyword['count']
                                }

                                # 调用原有的预警检查方法
                                await alert_system.check_keyword_alerts([keyword_data])

                        total_checks += len(alert_result.matched_keywords)

                    except Exception as e:
                        logger.error(f"检查预警规则失败 {rule.get('name', 'unknown')}: {e}")

                logger.info(f"预警检查完成，检查了 {total_checks} 个关键词匹配")

            except Exception as e:
                logger.error(f"获取预警分析数据失败: {e}")

        except Exception as e:
            logger.error(f"预警检查失败: {e}")


# 创建全局调度器实例
task_scheduler = TaskScheduler()
