"""
预警系统模块
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from loguru import logger
import json
import re


class AlertType(Enum):
    """预警类型"""
    KEYWORD = "keyword"          # 关键词预警
    SENTIMENT = "sentiment"      # 情感预警
    VOLUME = "volume"           # 数据量预警
    SOURCE = "source"           # 数据源预警


class AlertLevel(Enum):
    """预警级别"""
    LOW = "low"                 # 低级预警
    MEDIUM = "medium"           # 中级预警
    HIGH = "high"              # 高级预警
    CRITICAL = "critical"       # 严重预警


class AlertStatus(Enum):
    """预警状态"""
    ACTIVE = "active"           # 激活
    RESOLVED = "resolved"       # 已解决
    SUPPRESSED = "suppressed"   # 已抑制


@dataclass
class AlertRule:
    """预警规则"""
    id: str
    name: str
    description: str
    alert_type: AlertType
    level: AlertLevel
    enabled: bool
    conditions: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class Alert:
    """预警记录"""
    id: str
    rule_id: str
    rule_name: str
    alert_type: AlertType
    level: AlertLevel
    status: AlertStatus
    title: str
    message: str
    data: Dict[str, Any]
    triggered_at: datetime
    resolved_at: Optional[datetime] = None


class AlertSystem:
    """预警系统"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        
    async def init(self):
        """初始化预警系统"""
        try:
            # 创建预警规则集合
            self.rules_collection = self.db_manager.database["alert_rules"]
            self.alerts_collection = self.db_manager.database["alerts"]

            # 创建索引
            await self.rules_collection.create_index("id", unique=True)
            await self.alerts_collection.create_index("id", unique=True)
            await self.alerts_collection.create_index("triggered_at")
            await self.alerts_collection.create_index("status")

            # 加载预警规则
            await self.load_rules()

            # 如果没有预警规则，自动设置默认规则
            if len(self.rules) == 0:
                logger.info("检测到没有预警规则，开始设置默认规则...")
                await self.setup_default_rules()
                await self.load_rules()  # 重新加载规则

            # 加载活跃预警
            await self.load_active_alerts()

            logger.info("预警系统初始化完成")

        except Exception as e:
            logger.error(f"预警系统初始化失败: {e}")
            raise
    
    async def load_rules(self):
        """加载预警规则"""
        try:
            cursor = self.rules_collection.find({"enabled": True})
            async for doc in cursor:
                rule = AlertRule(
                    id=doc["id"],
                    name=doc["name"],
                    description=doc["description"],
                    alert_type=AlertType(doc["alert_type"]),
                    level=AlertLevel(doc["level"]),
                    enabled=doc["enabled"],
                    conditions=doc["conditions"],
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"]
                )
                self.rules[rule.id] = rule
                
            logger.info(f"加载了 {len(self.rules)} 个预警规则")
            
        except Exception as e:
            logger.error(f"加载预警规则失败: {e}")
    
    async def load_active_alerts(self):
        """加载活跃预警"""
        try:
            cursor = self.alerts_collection.find({"status": "active"})
            async for doc in cursor:
                alert = Alert(
                    id=doc["id"],
                    rule_id=doc["rule_id"],
                    rule_name=doc["rule_name"],
                    alert_type=AlertType(doc["alert_type"]),
                    level=AlertLevel(doc["level"]),
                    status=AlertStatus(doc["status"]),
                    title=doc["title"],
                    message=doc["message"],
                    data=doc["data"],
                    triggered_at=doc["triggered_at"],
                    resolved_at=doc.get("resolved_at")
                )
                self.active_alerts[alert.id] = alert
                
            logger.info(f"加载了 {len(self.active_alerts)} 个活跃预警")
            
        except Exception as e:
            logger.error(f"加载活跃预警失败: {e}")
    
    async def add_rule(self, rule: AlertRule) -> bool:
        """添加预警规则"""
        try:
            rule_dict = asdict(rule)
            # 转换枚举为字符串
            rule_dict['alert_type'] = rule.alert_type.value
            rule_dict['level'] = rule.level.value
            await self.rules_collection.insert_one(rule_dict)
            self.rules[rule.id] = rule
            logger.info(f"添加预警规则: {rule.name}")
            return True

        except Exception as e:
            logger.error(f"添加预警规则失败: {e}")
            return False
    
    async def update_rule(self, rule: AlertRule) -> bool:
        """更新预警规则"""
        try:
            rule.updated_at = datetime.now()
            rule_dict = asdict(rule)
            # 转换枚举为字符串
            rule_dict['alert_type'] = rule.alert_type.value
            rule_dict['level'] = rule.level.value
            await self.rules_collection.replace_one({"id": rule.id}, rule_dict)
            self.rules[rule.id] = rule
            logger.info(f"更新预警规则: {rule.name}")
            return True

        except Exception as e:
            logger.error(f"更新预警规则失败: {e}")
            return False
    
    async def delete_rule(self, rule_id: str) -> bool:
        """删除预警规则"""
        try:
            await self.rules_collection.delete_one({"id": rule_id})
            if rule_id in self.rules:
                del self.rules[rule_id]
            logger.info(f"删除预警规则: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除预警规则失败: {e}")
            return False
    
    async def trigger_alert(self, alert: Alert) -> bool:
        """触发预警"""
        try:
            alert_dict = asdict(alert)
            # 转换枚举为字符串
            alert_dict['alert_type'] = alert.alert_type.value
            alert_dict['level'] = alert.level.value
            alert_dict['status'] = alert.status.value
            await self.alerts_collection.insert_one(alert_dict)
            self.active_alerts[alert.id] = alert

            logger.warning(f"触发预警: {alert.title} [{alert.level.value}]")
            return True

        except Exception as e:
            logger.error(f"触发预警失败: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """解决预警"""
        try:
            now = datetime.now()
            await self.alerts_collection.update_one(
                {"id": alert_id},
                {"$set": {"status": "resolved", "resolved_at": now}}
            )
            
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].status = AlertStatus.RESOLVED
                self.active_alerts[alert_id].resolved_at = now
                del self.active_alerts[alert_id]
            
            logger.info(f"解决预警: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"解决预警失败: {e}")
            return False
    
    async def check_keyword_alerts(self, keywords: List[Dict[str, Any]]):
        """检查关键词预警"""
        for rule in self.rules.values():
            if rule.alert_type != AlertType.KEYWORD or not rule.enabled:
                continue
                
            try:
                await self._check_keyword_rule(rule, keywords)
            except Exception as e:
                logger.error(f"检查关键词预警规则失败 {rule.name}: {e}")
    
    async def _check_keyword_rule(self, rule: AlertRule, keywords: List[Dict[str, Any]]):
        """检查单个关键词预警规则"""
        conditions = rule.conditions
        target_keywords = conditions.get("keywords", [])
        threshold = conditions.get("threshold", 0)
        time_window = conditions.get("time_window", 60)  # 分钟
        
        # 检查关键词是否超过阈值
        for keyword_data in keywords:
            keyword = keyword_data.get("word", "")
            count = keyword_data.get("count", 0)
            
            # 检查是否匹配目标关键词
            if self._match_keyword(keyword, target_keywords):
                if count >= threshold:
                    # 生成固定的预警ID（基于规则和关键词，不包含时间）
                    alert_id = f"{rule.id}_{keyword}"

                    # 检查是否已经存在活跃的相同预警
                    existing_alert = await self._get_existing_alert(alert_id)

                    if existing_alert and existing_alert.get('status') == 'active':
                        # 如果存在活跃预警，更新其数据和时间
                        await self._update_existing_alert(alert_id, count, threshold, time_window)
                        logger.info(f"更新现有预警: {alert_id}, 新计数: {count}")
                    elif existing_alert and existing_alert.get('status') == 'resolved':
                        # 如果预警已解决，重新激活它
                        await self._reactivate_alert(alert_id, count, threshold, time_window)
                        logger.info(f"重新激活预警: {alert_id}, 新计数: {count}")
                    elif not existing_alert:
                        # 创建全新的预警
                        alert = Alert(
                            id=alert_id,
                            rule_id=rule.id,
                            rule_name=rule.name,
                            alert_type=rule.alert_type,
                            level=rule.level,
                            status=AlertStatus.ACTIVE,
                            title=f"关键词预警: {keyword}",
                            message=f"关键词 '{keyword}' 出现频次 {count} 次，超过阈值 {threshold}",
                            data={
                                "keyword": keyword,
                                "count": count,
                                "threshold": threshold,
                                "time_window": time_window,
                                "reactivation_count": 0,  # 初始化重新激活计数
                                "created_at": datetime.now().isoformat()
                            },
                            triggered_at=datetime.now()
                        )

                        await self.trigger_alert(alert)
                        logger.info(f"创建新预警: {alert_id}, 计数: {count}")

    async def _get_existing_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """获取现有预警"""
        try:
            return await self.alerts_collection.find_one({"id": alert_id})
        except Exception as e:
            logger.error(f"获取现有预警失败: {e}")
            return None

    async def _update_existing_alert(self, alert_id: str, count: int, threshold: int, time_window: int):
        """更新现有活跃预警的数据"""
        try:
            now = datetime.now()
            update_data = {
                "message": f"关键词预警更新: 出现频次 {count} 次，超过阈值 {threshold}",
                "data.count": count,
                "data.threshold": threshold,
                "data.time_window": time_window,
                "data.last_updated": now.isoformat(),
                "triggered_at": now  # 更新触发时间为最新时间
            }

            await self.alerts_collection.update_one(
                {"id": alert_id},
                {"$set": update_data}
            )

            # 更新内存中的活跃预警
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].message = update_data["message"]
                self.active_alerts[alert_id].data["count"] = count
                self.active_alerts[alert_id].data["last_updated"] = now.isoformat()
                self.active_alerts[alert_id].triggered_at = now

        except Exception as e:
            logger.error(f"更新现有预警失败: {e}")

    async def _reactivate_alert(self, alert_id: str, count: int, threshold: int, time_window: int):
        """重新激活已解决的预警"""
        try:
            now = datetime.now()
            update_data = {
                "status": "active",
                "message": f"关键词预警重新触发: 出现频次 {count} 次，超过阈值 {threshold}",
                "data.count": count,
                "data.threshold": threshold,
                "data.time_window": time_window,
                "data.last_updated": now.isoformat(),
                "triggered_at": now,
                "resolved_at": None,  # 清除解决时间
                "data.reactivation_count": {"$inc": 1}  # 记录重新激活次数
            }

            # 使用 $inc 操作符来增加重新激活计数
            await self.alerts_collection.update_one(
                {"id": alert_id},
                {
                    "$set": {k: v for k, v in update_data.items() if k != "data.reactivation_count"},
                    "$inc": {"data.reactivation_count": 1}
                }
            )

            # 重新加载到活跃预警内存缓存
            alert_doc = await self.alerts_collection.find_one({"id": alert_id})
            if alert_doc:
                alert = Alert(
                    id=alert_doc["id"],
                    rule_id=alert_doc["rule_id"],
                    rule_name=alert_doc["rule_name"],
                    alert_type=AlertType(alert_doc["alert_type"]),
                    level=AlertLevel(alert_doc["level"]),
                    status=AlertStatus.ACTIVE,
                    title=alert_doc["title"],
                    message=alert_doc["message"],
                    data=alert_doc["data"],
                    triggered_at=alert_doc["triggered_at"],
                    resolved_at=None
                )
                self.active_alerts[alert_id] = alert

        except Exception as e:
            logger.error(f"重新激活预警失败: {e}")

    def _match_keyword(self, keyword: str, target_keywords: List[str]) -> bool:
        """匹配关键词"""
        for target in target_keywords:
            if "*" in target or "?" in target:
                # 支持通配符匹配
                pattern = target.replace("*", ".*").replace("?", ".")
                if re.match(pattern, keyword, re.IGNORECASE):
                    return True
            else:
                # 精确匹配或包含匹配
                if target.lower() in keyword.lower():
                    return True
        return False
    
    async def get_alerts(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取预警列表"""
        try:
            query = {}
            if status:
                query["status"] = status
                
            cursor = self.alerts_collection.find(query).sort("triggered_at", -1).limit(limit)
            alerts = []
            
            async for doc in cursor:
                alerts.append({
                    "id": doc["id"],
                    "rule_id": doc["rule_id"],
                    "rule_name": doc["rule_name"],
                    "alert_type": doc["alert_type"],
                    "level": doc["level"],
                    "status": doc["status"],
                    "title": doc["title"],
                    "message": doc["message"],
                    "data": doc["data"],
                    "triggered_at": doc["triggered_at"].isoformat(),
                    "resolved_at": doc["resolved_at"].isoformat() if doc.get("resolved_at") else None
                })
                
            return alerts

        except Exception as e:
            logger.error(f"获取预警列表失败: {e}")
            return []

    async def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取单个预警"""
        try:
            doc = await self.alerts_collection.find_one({"id": alert_id})
            if not doc:
                return None

            return {
                "id": doc["id"],
                "rule_id": doc["rule_id"],
                "rule_name": doc["rule_name"],
                "alert_type": doc["alert_type"],
                "level": doc["level"],
                "status": doc["status"],
                "title": doc["title"],
                "message": doc["message"],
                "data": doc["data"],
                "triggered_at": doc["triggered_at"].isoformat(),
                "resolved_at": doc["resolved_at"].isoformat() if doc.get("resolved_at") else None
            }

        except Exception as e:
            logger.error(f"获取预警详情失败: {e}")
            return None
    
    async def get_rules(self) -> List[Dict[str, Any]]:
        """获取预警规则列表"""
        try:
            cursor = self.rules_collection.find().sort("created_at", -1)
            rules = []
            
            async for doc in cursor:
                rules.append({
                    "id": doc["id"],
                    "name": doc["name"],
                    "description": doc["description"],
                    "alert_type": doc["alert_type"],
                    "level": doc["level"],
                    "enabled": doc["enabled"],
                    "conditions": doc["conditions"],
                    "created_at": doc["created_at"].isoformat(),
                    "updated_at": doc["updated_at"].isoformat()
                })
                
            return rules
            
        except Exception as e:
            logger.error(f"获取预警规则列表失败: {e}")
            return []

    async def setup_default_rules(self):
        """设置默认预警规则"""
        from default_alert_rules import DEFAULT_ALERT_RULES

        try:
            logger.info("开始设置默认预警规则...")
            added_count = 0

            for rule_config in DEFAULT_ALERT_RULES:
                try:
                    # 创建预警规则对象
                    rule = AlertRule(
                        id=rule_config["id"],
                        name=rule_config["name"],
                        description=rule_config["description"],
                        alert_type=AlertType(rule_config["alert_type"]),
                        level=AlertLevel(rule_config["level"]),
                        enabled=rule_config["enabled"],
                        conditions=rule_config["conditions"],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )

                    # 添加规则
                    success = await self.add_rule(rule)
                    if success:
                        added_count += 1
                        logger.info(f"添加默认规则: {rule.name}")

                except Exception as e:
                    logger.error(f"添加默认规则失败 {rule_config['name']}: {e}")

            logger.info(f"默认预警规则设置完成，共添加 {added_count} 个规则")

        except Exception as e:
            logger.error(f"设置默认预警规则失败: {e}")


# 全局预警系统实例
alert_system: Optional[AlertSystem] = None


async def init_alert_system(db_manager):
    """初始化全局预警系统"""
    global alert_system
    alert_system = AlertSystem(db_manager)
    await alert_system.init()
    return alert_system


def get_alert_system() -> AlertSystem:
    """获取预警系统实例"""
    return alert_system
