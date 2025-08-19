#!/usr/bin/env python3
"""
默认预警规则配置
注意：这些规则会在系统首次启动时自动加载
"""
from datetime import datetime
from typing import List, Dict, Any


# 默认预警规则配置（基于实际数据优化）
DEFAULT_ALERT_RULES = [
    {
        "id": "security_alert",
        "name": "安全事件预警",
        "description": "监控网络安全、数据安全相关事件",
        "alert_type": "keyword",
        "level": "high",
        "enabled": True,
        "conditions": {
            "keywords": ["安全", "数据泄露", "黑客", "攻击", "病毒", "勒索", "网络安全", "信息安全"],
            "threshold": 15,  # 基于实际数据中"安全"关键词的频次
            "time_window": 60
        }
    },
    {
        "id": "data_monitoring",
        "name": "数据相关监控",
        "description": "监控数据处理、数据分析相关话题",
        "alert_type": "keyword",
        "level": "medium",
        "enabled": True,
        "conditions": {
            "keywords": ["数据", "大数据", "数据库", "数据分析", "数据处理", "数据中心"],
            "threshold": 20,  # 基于实际数据中"数据"关键词的频次
            "time_window": 60
        }
    },
    {
        "id": "technology_trends",
        "name": "科技趋势监控",
        "description": "监控人工智能、区块链等科技热点",
        "alert_type": "keyword",
        "level": "medium",
        "enabled": True,
        "conditions": {
            "keywords": ["人工智能", "AI", "区块链", "云计算", "5G", "物联网", "机器学习"],
            "threshold": 10,
            "time_window": 120
        }
    },
    {
        "id": "financial_monitoring",
        "name": "金融市场监控",
        "description": "监控股市、经济、投资相关重要动态",
        "alert_type": "keyword",
        "level": "medium",
        "enabled": True,
        "conditions": {
            "keywords": ["股市", "经济", "金融", "投资", "GDP", "通胀", "央行", "利率"],
            "threshold": 12,
            "time_window": 90
        }
    },
    {
        "id": "emergency_events",
        "name": "突发事件预警",
        "description": "监控突发事件、紧急情况",
        "alert_type": "keyword",
        "level": "critical",
        "enabled": True,
        "conditions": {
            "keywords": ["突发", "紧急", "事故", "灾害", "地震", "火灾", "爆炸", "伤亡"],
            "threshold": 3,
            "time_window": 30
        }
    }
]


# 📋 预警规则管理说明
#
# ✅ 自动加载功能已启用
# 系统首次启动时会自动加载以下默认预警规则
# 这些规则基于实际新闻数据进行了优化，阈值设置更加合理
#
# 🎯 默认规则特点：
# - 基于真实数据：阈值根据实际关键词频次设置
# - 分级管理：critical > high > medium > low
# - 时间窗口：根据事件紧急程度调整（30-120分钟）
# - 实用导向：关注安全、科技、金融、突发事件等重要领域
#
# 🔧 如何管理预警规则：
# 1. 通过前端界面：访问 "预警管理" 页面进行增删改查
# 2. 通过API接口：使用 /api/alert-rules 相关接口
# 3. 通过此配置文件：修改 DEFAULT_ALERT_RULES 列表（需重启系统）
#
# 🧹 如何重置规则：
# 运行清理脚本：python clear_default_alert_rules.py
# 然后重启系统，将重新加载默认规则
