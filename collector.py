"""
数据采集模块
"""
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger
from config import settings, DATA_SOURCES, get_all_source_ids
from database import db_manager


class DataCollector:
    """数据采集器"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    def _get_source_category(self, source_id: str) -> str:
        """获取数据源分类"""
        for category, sources in DATA_SOURCES.items():
            if source_id in sources:
                return category
        return "unknown"
    
    def _get_source_info(self, source_id: str) -> Dict[str, Any]:
        """获取数据源信息"""
        for category, sources in DATA_SOURCES.items():
            if source_id in sources:
                return {
                    "category": category,
                    "name": sources[source_id]["name"],
                    "priority": sources[source_id]["priority"]
                }
        return {"category": "unknown", "name": source_id, "priority": 3}
    
    async def _fetch_single_source(self, source_id: str) -> List[Dict[str, Any]]:
        """采集单个数据源"""
        async with self.semaphore:
            source_info = self._get_source_info(source_id)
            
            # 构建URL
            primary_url = f"{settings.PRIMARY_BASE_URL}?id={source_id}"
            backup_url = f"{settings.BACKUP_BASE_URL}?id={source_id}"
            
            # 尝试主服务器
            data = await self._fetch_url(primary_url, source_id)
            
            # 如果主服务器失败，尝试备用服务器
            if not data:
                logger.warning(f"主服务器失败，尝试备用服务器: {source_id}")
                data = await self._fetch_url(backup_url, source_id)
            
            if data:
                # 添加元数据
                for item in data:
                    item.update({
                        "source_id": source_id,
                        "source_name": source_info["name"],
                        "category": source_info["category"],
                        "priority": source_info["priority"],
                        "collected_at": datetime.utcnow()
                    })
                
                logger.info(f"成功采集 {source_id}: {len(data)} 条数据")
                return data
            else:
                logger.error(f"采集失败: {source_id}")
                return []
    
    async def _fetch_url(self, url: str, source_id: str) -> List[Dict[str, Any]]:
        """从URL获取数据"""
        for attempt in range(settings.RETRY_TIMES):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 处理不同的响应格式
                        if isinstance(data, dict):
                            if "data" in data:
                                return data["data"] if isinstance(data["data"], list) else [data["data"]]
                            elif "items" in data:
                                return data["items"] if isinstance(data["items"], list) else [data["items"]]
                            else:
                                return [data]
                        elif isinstance(data, list):
                            return data
                        else:
                            logger.warning(f"未知数据格式: {source_id}")
                            return []
                    else:
                        logger.warning(f"HTTP {response.status}: {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{settings.RETRY_TIMES}): {url}")
            except Exception as e:
                logger.warning(f"请求异常 (尝试 {attempt + 1}/{settings.RETRY_TIMES}): {url} - {e}")
            
            if attempt < settings.RETRY_TIMES - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
        
        return []
    
    async def collect_all_sources(self) -> Dict[str, Any]:
        """采集所有数据源"""
        logger.info("开始采集所有数据源")
        start_time = datetime.now()
        
        source_ids = get_all_source_ids()
        tasks = [self._fetch_single_source(source_id) for source_id in source_ids]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        all_data = []
        success_count = 0
        error_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"采集异常 {source_ids[i]}: {result}")
                error_count += 1
            elif result:
                all_data.extend(result)
                success_count += 1
            else:
                error_count += 1
        
        # 保存到数据库
        if all_data:
            await db_manager.insert_data(all_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "total_sources": len(source_ids),
            "success_count": success_count,
            "error_count": error_count,
            "total_items": len(all_data),
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        logger.info(f"采集完成: {summary}")
        return summary
    
    async def collect_by_priority(self, priority: int) -> Dict[str, Any]:
        """按优先级采集数据源"""
        logger.info(f"开始采集优先级 {priority} 的数据源")
        
        # 获取指定优先级的数据源
        priority_sources = []
        for category, sources in DATA_SOURCES.items():
            for source_id, config in sources.items():
                if config["priority"] == priority:
                    priority_sources.append(source_id)
        
        if not priority_sources:
            logger.warning(f"没有找到优先级为 {priority} 的数据源")
            return {"total_sources": 0, "success_count": 0, "error_count": 0, "total_items": 0}
        
        start_time = datetime.now()
        tasks = [self._fetch_single_source(source_id) for source_id in priority_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        all_data = []
        success_count = 0
        error_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"采集异常 {priority_sources[i]}: {result}")
                error_count += 1
            elif result:
                all_data.extend(result)
                success_count += 1
            else:
                error_count += 1
        
        # 保存到数据库
        if all_data:
            await db_manager.insert_data(all_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "priority": priority,
            "total_sources": len(priority_sources),
            "success_count": success_count,
            "error_count": error_count,
            "total_items": len(all_data),
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        logger.info(f"优先级 {priority} 采集完成: {summary}")
        return summary
    
    async def collect_single_source(self, source_id: str) -> Dict[str, Any]:
        """采集单个数据源"""
        logger.info(f"开始采集单个数据源: {source_id}")
        
        start_time = datetime.now()
        data = await self._fetch_single_source(source_id)
        
        # 保存到数据库
        if data:
            await db_manager.insert_data(data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "source_id": source_id,
            "success": len(data) > 0,
            "total_items": len(data),
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        logger.info(f"单源采集完成: {summary}")
        return summary


# 创建全局采集器实例
collector = DataCollector()
