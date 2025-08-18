"""
舆情监控平台配置文件
"""
import os
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "舆情监控平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://14.103.138.240:27017"
    DATABASE_NAME: str = "sentiment_monitor"
    
    # 数据保留配置
    DATA_TTL_DAYS: int = 180  # 数据保留180天
    
    # 采集配置
    COLLECTION_INTERVAL: int = 300  # 采集间隔（秒）
    MAX_CONCURRENT_REQUESTS: int = 10  # 最大并发请求数
    REQUEST_TIMEOUT: int = 30  # 请求超时时间（秒）
    RETRY_TIMES: int = 3  # 重试次数
    
    # 数据源配置
    PRIMARY_BASE_URL: str = "https://new.0407123.xyz/api/s"
    BACKUP_BASE_URL: str = "https://newsnow.busiyi.world/api/s"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/sentiment_monitor.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 数据源配置
DATA_SOURCES = {
    # 金融类数据源
    "finance": {
        "mktnews": {"name": "MKTNews", "priority": 2},
        "mktnews-flash": {"name": "MKTNews快讯", "priority": 2},
        "wallstreetcn": {"name": "华尔街见闻", "priority": 1},
        "wallstreetcn-quick": {"name": "华尔街见闻快讯", "priority": 1},
        "wallstreetcn-news": {"name": "华尔街见闻新闻", "priority": 1},
        "wallstreetcn-hot": {"name": "华尔街见闻热点", "priority": 1},
        "cls": {"name": "财联社", "priority": 1},
        "cls-telegraph": {"name": "财联社电报", "priority": 1},
        "cls-depth": {"name": "财联社深度", "priority": 1},
        "cls-hot": {"name": "财联社热点", "priority": 1},
        "xueqiu": {"name": "雪球", "priority": 1},
        "xueqiu-hotstock": {"name": "雪球热股", "priority": 1},
        "gelonghui": {"name": "格隆汇", "priority": 2},
        "fastbull": {"name": "法布财经", "priority": 2},
        "fastbull-express": {"name": "法布财经快讯", "priority": 2},
        "fastbull-news": {"name": "法布财经新闻", "priority": 2},
        "jin10": {"name": "金十数据", "priority": 1},
    },
    
    # 科技类数据源
    "tech": {
        "v2ex": {"name": "V2EX", "priority": 3},
        "v2ex-share": {"name": "V2EX分享", "priority": 1},
        "coolapk": {"name": "酷安", "priority": 2},
        "36kr": {"name": "36氪", "priority": 1},
        "36kr-quick": {"name": "36氪快讯", "priority": 1},
        "ithome": {"name": "IT之家", "priority": 1},
        "pcbeta": {"name": "远景论坛", "priority": 2},
        "pcbeta-windows11": {"name": "远景论坛Win11", "priority": 2},
        "solidot": {"name": "Solidot", "priority": 2},
        "hackernews": {"name": "Hacker News", "priority": 2},
        "producthunt": {"name": "Product Hunt", "priority": 2},
        "github": {"name": "Github", "priority": 2},
        "github-trending-today": {"name": "Github今日趋势", "priority": 2},
        "nowcoder": {"name": "牛客", "priority": 2},
        "sspai": {"name": "少数派", "priority": 2},
        "juejin": {"name": "稀土掘金", "priority": 2},
        "chongbuluo": {"name": "虫部落", "priority": 2},
        "chongbuluo-latest": {"name": "虫部落最新", "priority": 2},
        "chongbuluo-hot": {"name": "虫部落热门", "priority": 2},
    },
    
    # 新闻类数据源
    "news": {
        "zaobao": {"name": "联合早报", "priority": 1},
        "toutiao": {"name": "今日头条", "priority": 1},
        "thepaper": {"name": "澎湃新闻", "priority": 1},
        "sputniknewscn": {"name": "卫星通讯社", "priority": 2},
        "cankaoxiaoxi": {"name": "参考消息", "priority": 2},
        "kaopu": {"name": "靠谱新闻", "priority": 2},
        "ifeng": {"name": "凤凰网", "priority": 2},
    },
    
    # 社交类数据源
    "social": {
        "zhihu": {"name": "知乎", "priority": 1},
        "weibo": {"name": "微博", "priority": 1},
        "douyin": {"name": "抖音", "priority": 2},
        "tieba": {"name": "百度贴吧", "priority": 2},
        "baidu": {"name": "百度热搜", "priority": 1},
    },
    
    # 娱乐类数据源
    "entertainment": {
        "bilibili": {"name": "哔哩哔哩", "priority": 1},
        "bilibili-hot-search": {"name": "哔哩哔哩热搜", "priority": 1},
        "bilibili-hot-video": {"name": "哔哩哔哩热门视频", "priority": 1},
        "bilibili-ranking": {"name": "哔哩哔哩排行榜", "priority": 1},
        "kuaishou": {"name": "快手", "priority": 2},
    },
    
    # 体育类数据源
    "sports": {
        "hupu": {"name": "虎扑", "priority": 2},
    }
}

# 获取所有数据源ID列表
def get_all_source_ids() -> List[str]:
    """获取所有数据源ID"""
    source_ids = []
    for category in DATA_SOURCES.values():
        source_ids.extend(category.keys())
    return source_ids

# 获取按优先级分组的数据源
def get_sources_by_priority() -> Dict[int, List[str]]:
    """按优先级分组数据源"""
    priority_groups = {}
    for category in DATA_SOURCES.values():
        for source_id, config in category.items():
            priority = config["priority"]
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(source_id)
    return priority_groups

# 创建配置实例
settings = Settings()
