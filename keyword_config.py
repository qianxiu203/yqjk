#!/usr/bin/env python3
"""
关键词分析配置文件
"""

# 关键词分析配置
KEYWORD_ANALYSIS_CONFIG = {
    # 热门关键词分析配置
    "trending": {
        "default_days": 7,
        "max_days": 365,
        "default_limit": 50,
        "max_limit": 200,
        "enable_time_weight": True,
        "enable_source_weight": True,
        "time_decay_hours": 168,  # 一周内有效
        "min_word_length": 2,
        "max_word_length": 10
    },
    
    # 预警关键词分析配置
    "alert": {
        "default_time_window": 60,  # 分钟
        "max_time_window": 1440,    # 24小时
        "check_interval": 10,       # 检查间隔（分钟）
        "max_keywords_per_rule": 50,
        "enable_fuzzy_match": True,
        "enable_regex_match": True
    },
    
    # 来源权重配置
    "source_weights": {
        # 官方媒体
        "xinhua": 1.5,          # 新华社
        "peoples": 1.5,         # 人民日报
        "cctv": 1.4,            # 央视
        "chinanews": 1.3,       # 中新网
        
        # 财经媒体
        "cls": 1.3,             # 财联社
        "wallstreetcn": 1.2,    # 华尔街见闻
        "jin10": 1.1,           # 金十数据
        "eastmoney": 1.1,       # 东方财富
        
        # 科技媒体
        "ithome": 1.2,          # IT之家
        "36kr": 1.1,            # 36氪
        "techcrunch": 1.1,      # TechCrunch
        
        # 社交媒体
        "weibo": 0.9,           # 微博
        "toutiao": 0.8,         # 今日头条
        "baidu": 0.7,           # 百度热搜
        
        # 默认权重
        "default": 1.0
    },
    
    # 分类关键词配置
    "category_keywords": {
        "technology": {
            "keywords": ["科技", "技术", "人工智能", "AI", "区块链", "云计算", "大数据", "物联网", "5G", "芯片", "算法", "机器学习", "深度学习", "自动驾驶", "虚拟现实", "增强现实"],
            "weight": 1.2
        },
        "finance": {
            "keywords": ["金融", "股市", "投资", "经济", "银行", "基金", "债券", "货币", "汇率", "财经", "IPO", "融资", "并购", "上市", "财报", "GDP"],
            "weight": 1.1
        },
        "politics": {
            "keywords": ["政治", "政府", "政策", "法律", "外交", "国际", "会议", "领导", "官员", "部门", "法规", "条例", "决议", "声明"],
            "weight": 1.3
        },
        "health": {
            "keywords": ["健康", "医疗", "疫情", "病毒", "疫苗", "医院", "医生", "治疗", "药物", "疾病", "健康", "养生", "医学", "临床"],
            "weight": 1.2
        },
        "sports": {
            "keywords": ["体育", "运动", "比赛", "奥运", "足球", "篮球", "游泳", "田径", "冠军", "运动员", "联赛", "世界杯", "锦标赛"],
            "weight": 0.9
        },
        "entertainment": {
            "keywords": ["娱乐", "电影", "音乐", "明星", "演员", "导演", "综艺", "电视", "网红", "直播", "游戏", "动漫", "小说"],
            "weight": 0.8
        },
        "education": {
            "keywords": ["教育", "学校", "大学", "学生", "老师", "考试", "招生", "毕业", "学习", "培训", "课程", "教学", "研究"],
            "weight": 1.0
        },
        "environment": {
            "keywords": ["环境", "气候", "污染", "环保", "生态", "绿色", "节能", "减排", "可持续", "自然", "保护", "治理"],
            "weight": 1.1
        }
    },
    
    # 情感关键词配置
    "sentiment_keywords": {
        "positive": {
            "keywords": ["好", "棒", "优秀", "成功", "胜利", "喜悦", "高兴", "满意", "赞", "支持", "积极", "正面", "突破", "创新", "发展", "增长", "提升", "改善"],
            "score": 1.0
        },
        "negative": {
            "keywords": ["坏", "差", "失败", "问题", "困难", "危机", "担心", "愤怒", "不满", "批评", "消极", "负面", "下降", "减少", "恶化", "危险", "风险", "损失"],
            "score": -1.0
        },
        "neutral": {
            "keywords": ["一般", "普通", "正常", "平常", "中等", "适中", "标准", "常规", "基本", "简单", "维持", "保持", "稳定"],
            "score": 0.0
        }
    },
    
    # 停用词配置
    "stop_words": {
        # 基础停用词
        "basic": [
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", 
            "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", 
            "自己", "这", "那", "什么", "可以", "这个", "时候", "现在", "知道", "来", "用", 
            "过", "想", "应该", "还", "这样", "最", "大", "为", "以", "如果", "没", "多", 
            "然后", "出", "比", "他", "两", "她", "其", "被", "此", "更", "加", "将", "已", 
            "把", "从", "但", "与", "及", "对", "由", "等", "所", "而", "或"
        ],
        
        # 时间词
        "time": [
            "今天", "昨天", "明天", "今年", "去年", "明年", "今日", "昨日", "明日",
            "上午", "下午", "晚上", "早上", "中午", "深夜", "凌晨", "傍晚"
        ],
        
        # 数量词
        "quantity": [
            "几个", "一些", "很多", "不少", "大量", "少量", "部分", "全部", "所有",
            "第一", "第二", "第三", "首个", "最后", "唯一", "单个", "多个"
        ],
        
        # 语气词
        "modal": [
            "因为", "所以", "虽然", "但是", "如果", "那么", "这么", "怎么", "为什么", 
            "怎样", "哪里", "什么时候", "谁", "哪个", "多少", "怎么样", "可能", "应该",
            "或许", "也许", "大概", "估计", "似乎", "好像", "据说", "听说"
        ],
        
        # 新闻常用词
        "news": [
            "记者", "报道", "消息", "新闻", "据悉", "了解", "表示", "认为", "指出", "强调",
            "发现", "显示", "证实", "透露", "宣布", "公布", "发布", "介绍", "解释", "说明",
            "采访", "报告", "通知", "公告", "声明", "回应", "澄清", "确认"
        ]
    },
    
    # 趋势计算配置
    "trend_calculation": {
        "up_threshold": 1.2,      # 上升趋势阈值
        "down_threshold": 0.8,    # 下降趋势阈值
        "stable_range": 0.2,      # 稳定范围
        "min_sample_size": 5,     # 最小样本数
        "time_weight_decay": 0.1  # 时间权重衰减
    }
}

# 预警规则模板
ALERT_RULE_TEMPLATES = {
    "emergency": {
        "name": "紧急事件预警模板",
        "keywords": ["紧急", "事故", "灾害", "火灾", "地震", "洪水", "爆炸"],
        "threshold": 3,
        "time_window": 30,
        "level": "high"
    },
    "security": {
        "name": "安全事件预警模板", 
        "keywords": ["数据泄露", "黑客", "攻击", "病毒", "勒索", "钓鱼"],
        "threshold": 2,
        "time_window": 60,
        "level": "high"
    },
    "economic": {
        "name": "经济事件预警模板",
        "keywords": ["经济危机", "金融风险", "股市暴跌", "破产", "倒闭"],
        "threshold": 4,
        "time_window": 120,
        "level": "medium"
    }
}

# 性能优化配置
PERFORMANCE_CONFIG = {
    "cache": {
        "trending_keywords_ttl": 300,    # 热门关键词缓存时间（秒）
        "alert_check_ttl": 60,           # 预警检查缓存时间（秒）
        "max_cache_size": 1000,          # 最大缓存条目数
        "enable_redis": False            # 是否启用Redis缓存
    },
    
    "database": {
        "max_connections": 10,           # 最大数据库连接数
        "connection_timeout": 30,        # 连接超时时间（秒）
        "query_timeout": 60,             # 查询超时时间（秒）
        "batch_size": 1000,              # 批处理大小
        "index_optimization": True       # 是否启用索引优化
    },
    
    "analysis": {
        "max_text_length": 10000,       # 最大文本长度
        "parallel_processing": True,     # 是否启用并行处理
        "max_workers": 4,                # 最大工作线程数
        "chunk_size": 100,               # 数据块大小
        "memory_limit_mb": 512           # 内存限制（MB）
    }
}

# 导出配置
__all__ = [
    'KEYWORD_ANALYSIS_CONFIG',
    'ALERT_RULE_TEMPLATES', 
    'PERFORMANCE_CONFIG'
]
