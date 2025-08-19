"""
MongoDB数据库连接和操作模块
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import IndexModel, DESCENDING
from loguru import logger
from config import settings


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.collections: Dict[str, AsyncIOMotorCollection] = {}

    async def connect(self):
        """连接数据库"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.DATABASE_NAME]

            # 测试连接
            await self.client.admin.command('ping')
            logger.info(f"成功连接到MongoDB: {settings.MONGODB_URL}")

            # 初始化集合
            await self._init_collections()

        except Exception as e:
            logger.error(f"连接MongoDB失败: {e}")
            raise

    async def disconnect(self):
        """断开数据库连接"""
        if self.client:
            self.client.close()
            logger.info("已断开MongoDB连接")

    async def _init_collections(self):
        """初始化集合和索引"""
        # 创建数据集合（按日期分集合）
        today = datetime.now().strftime("%Y%m%d")
        collection_name = f"sentiment_data_{today}"

        collection = self.database[collection_name]
        self.collections[collection_name] = collection

        # 创建TTL索引（180天后自动删除）
        ttl_seconds = settings.DATA_TTL_DAYS * 24 * 60 * 60
        indexes = [
            IndexModel([("created_at", DESCENDING)], expireAfterSeconds=ttl_seconds),
            IndexModel([("source_id", 1)]),
            IndexModel([("category", 1)]),
            IndexModel([("priority", 1)]),
            IndexModel([("title", "text"), ("content", "text")]),  # 全文搜索索引
        ]

        try:
            await collection.create_indexes(indexes)
            logger.info(f"成功创建集合 {collection_name} 和索引")
        except Exception as e:
            logger.warning(f"创建索引时出现警告: {e}")

    async def get_today_collection(self) -> AsyncIOMotorCollection:
        """获取今天的数据集合"""
        today = datetime.now().strftime("%Y%m%d")
        collection_name = f"sentiment_data_{today}"

        if collection_name not in self.collections:
            await self._init_collections()

        return self.collections[collection_name]

    async def insert_data(self, data: List[Dict[str, Any]]) -> bool:
        """插入数据"""
        try:
            if not data:
                return True

            collection = await self.get_today_collection()

            # 添加时间戳
            for item in data:
                item["created_at"] = datetime.utcnow()
                item["date"] = datetime.now().strftime("%Y-%m-%d")

            result = await collection.insert_many(data)
            logger.info(f"成功插入 {len(result.inserted_ids)} 条数据")
            return True

        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            return False

    async def find_data(self,
                       source_id: Optional[str] = None,
                       category: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       limit: int = 100,
                       skip: int = 0) -> List[Dict[str, Any]]:
        """查询数据"""
        try:
            collection = await self.get_today_collection()

            # 构建查询条件
            query = {}
            if source_id:
                query["source_id"] = source_id
            if category:
                query["category"] = category
            if start_date or end_date:
                query["created_at"] = {}
                if start_date:
                    query["created_at"]["$gte"] = start_date
                if end_date:
                    query["created_at"]["$lte"] = end_date

            cursor = collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            data = await cursor.to_list(length=limit)

            # 转换ObjectId为字符串
            for item in data:
                item["_id"] = str(item["_id"])

            return data

        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return []

    async def find_data_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """根据ID查询单条数据"""
        try:
            from bson import ObjectId
            collection = await self.get_today_collection()

            # 查询数据
            data = await collection.find_one({"_id": ObjectId(item_id)})

            if data:
                data["_id"] = str(data["_id"])
                return data
            return None

        except Exception as e:
            logger.error(f"根据ID查询数据失败: {e}")
            return None

    async def search_data(self,
                         keyword: str = "",
                         category: str = "",
                         skip: int = 0,
                         limit: int = 20) -> tuple[List[Dict[str, Any]], int]:
        """搜索数据"""
        try:
            collection = await self.get_today_collection()

            # 构建查询条件
            query = {}

            if category:
                query["category"] = category

            if keyword:
                query["$or"] = [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"content": {"$regex": keyword, "$options": "i"}},
                    {"description": {"$regex": keyword, "$options": "i"}}
                ]

            # 获取总数
            total = await collection.count_documents(query)

            # 获取分页数据
            cursor = collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            data = await cursor.to_list(length=limit)

            # 转换ObjectId为字符串
            for item in data:
                item["_id"] = str(item["_id"])

            return data, total

        except Exception as e:
            logger.error(f"搜索数据失败: {e}")
            return [], 0

    async def count_data(self,
                        source_id: Optional[str] = None,
                        category: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> int:
        """统计数据数量"""
        try:
            collection = await self.get_today_collection()

            # 构建查询条件
            query = {}
            if source_id:
                query["source_id"] = source_id
            if category:
                query["category"] = category
            if start_date or end_date:
                query["created_at"] = {}
                if start_date:
                    query["created_at"]["$gte"] = start_date
                if end_date:
                    query["created_at"]["$lte"] = end_date

            count = await collection.count_documents(query)
            return count

        except Exception as e:
            logger.error(f"统计数据失败: {e}")
            return 0

    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            # 获取今天的集合
            today_collection = await self.get_today_collection()
            logger.info(f"获取统计信息 - 今天集合: {today_collection.name}")

            # 按数据源统计（今天的数据）
            source_stats = await today_collection.aggregate([
                {"$group": {"_id": "$source_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]).to_list(length=None)

            # 按分类统计（今天的数据）
            category_stats = await today_collection.aggregate([
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]).to_list(length=None)

            # 今日新增统计（今天集合中的所有数据就是今日新增）
            today_count = await today_collection.count_documents({})
            logger.info(f"今日新增数据量: {today_count}")

            # 总数统计（需要查询所有历史集合）
            total_count = await self._get_total_count_all_collections()
            logger.info(f"总数据量: {total_count}")

            return {
                "total_count": total_count,
                "today_count": today_count,
                "source_stats": source_stats,
                "category_stats": category_stats,
                "total_sources": len(source_stats) if source_stats else 0,
                "success_rate": 99.6,  # 模拟成功率
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                "total_count": 0,
                "today_count": 0,
                "source_stats": [],
                "category_stats": [],
                "total_sources": 0,
                "success_rate": 0,
                "last_updated": datetime.now().isoformat()
            }

    async def _get_total_count_all_collections(self) -> int:
        """获取所有集合的总数据量"""
        try:
            total_count = 0

            # 确保数据库连接存在
            if not self.client:
                logger.error("数据库连接不存在")
                return 0

            db = self.client[settings.DATABASE_NAME]

            # 获取数据库中所有以sentiment_data_开头的集合
            collection_names = await db.list_collection_names()
            sentiment_collections = [name for name in collection_names if name.startswith("sentiment_data_")]

            logger.info(f"找到 {len(sentiment_collections)} 个数据集合")

            # 统计每个集合的数据量
            for collection_name in sentiment_collections:
                collection = db[collection_name]
                count = await collection.count_documents({})
                total_count += count
                logger.debug(f"集合 {collection_name} 数据量: {count}")

            logger.info(f"所有集合总数据量: {total_count}")
            return total_count

        except Exception as e:
            logger.error(f"获取总数据量失败: {e}")
            # 如果获取失败，返回今天的数据量作为备用
            try:
                today_collection = await self.get_today_collection()
                backup_count = await today_collection.count_documents({})
                logger.info(f"使用今天数据量作为备用: {backup_count}")
                return backup_count
            except Exception as backup_error:
                logger.error(f"获取备用数据量也失败: {backup_error}")
                return 0

    async def get_data_for_trending_analysis(self,
                                           days: int = 7,
                                           limit: int = 1000) -> List[Dict[str, Any]]:
        """获取用于热门关键词分析的数据"""
        try:
            # 计算时间范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # 获取多个集合的数据
            all_data = []

            # 获取指定天数内的所有集合
            for i in range(days):
                date = (end_date - timedelta(days=i)).strftime("%Y%m%d")
                collection_name = f"sentiment_data_{date}"

                try:
                    collection = self.database[collection_name]

                    # 查询该天的数据
                    cursor = collection.find({
                        "created_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }).sort("created_at", DESCENDING).limit(limit // days)

                    daily_data = await cursor.to_list(length=limit // days)

                    # 转换ObjectId为字符串
                    for item in daily_data:
                        item["_id"] = str(item["_id"])

                    all_data.extend(daily_data)

                except Exception as e:
                    logger.debug(f"集合 {collection_name} 不存在或查询失败: {e}")
                    continue

            # 按时间排序并限制总数量
            all_data.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
            return all_data[:limit]

        except Exception as e:
            logger.error(f"获取热门分析数据失败: {e}")
            return []

    async def get_data_for_alert_analysis(self,
                                        time_window: int = 60) -> List[Dict[str, Any]]:
        """获取用于预警分析的数据"""
        try:
            # 计算时间窗口
            current_time = datetime.now()
            start_time = current_time - timedelta(minutes=time_window)

            # 获取今天的集合
            collection = await self.get_today_collection()

            # 查询时间窗口内的数据
            cursor = collection.find({
                "created_at": {
                    "$gte": start_time,
                    "$lte": current_time
                }
            }).sort("created_at", DESCENDING)

            data = await cursor.to_list(length=None)

            # 转换ObjectId为字符串
            for item in data:
                item["_id"] = str(item["_id"])

            logger.info(f"获取预警分析数据: {len(data)} 条，时间窗口: {time_window} 分钟")
            return data

        except Exception as e:
            logger.error(f"获取预警分析数据失败: {e}")
            return []

    async def get_historical_keyword_data(self,
                                        keyword: str,
                                        days: int = 30) -> List[Dict[str, Any]]:
        """获取关键词的历史数据（用于趋势分析）"""
        try:
            all_data = []
            end_date = datetime.now()

            # 获取指定天数内的数据
            for i in range(days):
                date = (end_date - timedelta(days=i)).strftime("%Y%m%d")
                collection_name = f"sentiment_data_{date}"

                try:
                    collection = self.database[collection_name]

                    # 搜索包含关键词的数据
                    cursor = collection.find({
                        "$or": [
                            {"title": {"$regex": keyword, "$options": "i"}},
                            {"content": {"$regex": keyword, "$options": "i"}}
                        ]
                    })

                    daily_data = await cursor.to_list(length=None)

                    # 添加日期标记
                    for item in daily_data:
                        item["_id"] = str(item["_id"])
                        item["analysis_date"] = date

                    all_data.extend(daily_data)

                except Exception as e:
                    logger.debug(f"集合 {collection_name} 查询关键词失败: {e}")
                    continue

            return all_data

        except Exception as e:
            logger.error(f"获取关键词历史数据失败: {e}")
            return []



# 创建全局数据库管理器实例
db_manager = DatabaseManager()
