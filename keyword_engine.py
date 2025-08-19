#!/usr/bin/env python3
"""
关键词分析引擎
分离热门关键词分析和预警关键词匹配的逻辑
"""
import re
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass
from loguru import logger
import math


@dataclass
class KeywordResult:
    """关键词分析结果"""
    word: str
    count: int
    trend: str = "stable"
    score: float = 0.0
    category: Optional[str] = None
    sentiment: Optional[str] = None
    sources: List[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []


@dataclass
class TrendingKeywordResult:
    """热门关键词分析结果"""
    keywords: List[KeywordResult]
    total_words: int
    unique_words: int
    analyzed_items: int
    time_range: str
    updated_at: str


@dataclass
class AlertKeywordResult:
    """预警关键词分析结果"""
    matched_keywords: List[Dict[str, Any]]
    total_matches: int
    time_window: int
    analyzed_items: int


class KeywordAnalysisEngine:
    """关键词分析引擎"""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
        self.category_keywords = self._load_category_keywords()
        self.sentiment_keywords = self._load_sentiment_keywords()
    
    def _load_stop_words(self) -> set:
        """加载停用词"""
        return {
            # 基础停用词
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', 
            '自己', '这', '那', '什么', '可以', '这个', '时候', '现在', '知道', '来', '用', 
            '过', '想', '应该', '还', '这样', '最', '大', '为', '以', '如果', '没', '多', 
            '然后', '出', '比', '他', '两', '她', '其', '被', '此', '更', '加', '将', '已', 
            '把', '从', '但', '与', '及', '对', '由', '等', '所', '而', '或',
            # 时间词
            '今天', '昨天', '明天', '今年', '去年', '明年', '今日', '昨日', '明日',
            # 数量词
            '几个', '一些', '很多', '不少', '大量', '少量', '部分', '全部', '所有',
            # 语气词
            '因为', '所以', '虽然', '但是', '如果', '那么', '这么', '怎么', '为什么', 
            '怎样', '哪里', '什么时候', '谁', '哪个', '多少', '怎么样', '可能', '应该',
            # 新闻常用词
            '记者', '报道', '消息', '新闻', '据悉', '了解', '表示', '认为', '指出', '强调',
            '发现', '显示', '证实', '透露', '宣布', '公布', '发布', '介绍', '解释', '说明'
        }
    
    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """加载分类关键词"""
        return {
            'technology': ['科技', '技术', '人工智能', 'AI', '区块链', '云计算', '大数据', '物联网', '5G', '芯片'],
            'finance': ['金融', '股市', '投资', '经济', '银行', '基金', '债券', '货币', '汇率', '财经'],
            'politics': ['政治', '政府', '政策', '法律', '外交', '国际', '会议', '领导', '官员', '部门'],
            'health': ['健康', '医疗', '疫情', '病毒', '疫苗', '医院', '医生', '治疗', '药物', '疾病'],
            'sports': ['体育', '运动', '比赛', '奥运', '足球', '篮球', '游泳', '田径', '冠军', '运动员'],
            'entertainment': ['娱乐', '电影', '音乐', '明星', '演员', '导演', '综艺', '电视', '网红', '直播'],
            'education': ['教育', '学校', '大学', '学生', '老师', '考试', '招生', '毕业', '学习', '培训'],
            'environment': ['环境', '气候', '污染', '环保', '生态', '绿色', '节能', '减排', '可持续', '自然']
        }
    
    def _load_sentiment_keywords(self) -> Dict[str, List[str]]:
        """加载情感关键词"""
        return {
            'positive': ['好', '棒', '优秀', '成功', '胜利', '喜悦', '高兴', '满意', '赞', '支持', '积极', '正面'],
            'negative': ['坏', '差', '失败', '问题', '困难', '危机', '担心', '愤怒', '不满', '批评', '消极', '负面'],
            'neutral': ['一般', '普通', '正常', '平常', '中等', '适中', '标准', '常规', '基本', '简单']
        }
    
    async def extract_trending_keywords(self, 
                                      data: List[Dict[str, Any]], 
                                      limit: int = 50,
                                      time_weight: bool = True,
                                      source_weight: bool = True) -> TrendingKeywordResult:
        """
        提取热门关键词（用于排行榜）
        
        Args:
            data: 新闻数据列表
            limit: 返回关键词数量限制
            time_weight: 是否启用时间权重（最近的新闻权重更高）
            source_weight: 是否启用来源权重（重要媒体权重更高）
        """
        try:
            if not data:
                return TrendingKeywordResult(
                    keywords=[],
                    total_words=0,
                    unique_words=0,
                    analyzed_items=0,
                    time_range="0d",
                    updated_at=datetime.now().isoformat()
                )
            
            # 权重配置
            source_weights = {
                'xinhua': 1.5,      # 新华社
                'peoples': 1.5,     # 人民日报
                'cctv': 1.4,        # 央视
                'cls': 1.3,         # 财联社
                'wallstreetcn': 1.2, # 华尔街见闻
                'jin10': 1.1,       # 金十数据
                'default': 1.0      # 默认权重
            }
            
            # 关键词统计
            keyword_stats = defaultdict(lambda: {
                'count': 0,
                'score': 0.0,
                'sources': set(),
                'latest_time': None,
                'category': None,
                'sentiment': None
            })
            
            current_time = datetime.now()
            
            for item in data:
                # 提取文本
                title = item.get("title", "")
                content = item.get("content", "")
                text = f"{title} {content}"
                
                # 计算时间权重
                time_weight_factor = 1.0
                if time_weight and 'created_at' in item:
                    try:
                        created_at = item['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        
                        # 时间差（小时）
                        time_diff = (current_time - created_at).total_seconds() / 3600
                        # 24小时内权重最高，之后逐渐衰减
                        time_weight_factor = max(0.1, 1.0 - (time_diff / 168))  # 一周内有效
                    except:
                        time_weight_factor = 1.0
                
                # 计算来源权重
                source_weight_factor = 1.0
                if source_weight:
                    source_id = item.get('source_id', 'default')
                    source_weight_factor = source_weights.get(source_id, source_weights['default'])
                
                # 综合权重
                total_weight = time_weight_factor * source_weight_factor
                
                # 提取关键词
                keywords = self._extract_keywords(text)
                
                for word, count in keywords.items():
                    stats = keyword_stats[word]
                    stats['count'] += count
                    stats['score'] += count * total_weight
                    stats['sources'].add(item.get('source_name', '未知'))
                    
                    # 更新最新时间
                    if 'created_at' in item:
                        item_time = item['created_at']
                        if isinstance(item_time, str):
                            try:
                                item_time = datetime.fromisoformat(item_time.replace('Z', '+00:00'))
                            except:
                                item_time = current_time
                        
                        if stats['latest_time'] is None or item_time > stats['latest_time']:
                            stats['latest_time'] = item_time
                    
                    # 分类和情感分析
                    if stats['category'] is None:
                        stats['category'] = self._classify_keyword(word)
                    if stats['sentiment'] is None:
                        stats['sentiment'] = self._analyze_sentiment(word)
            
            # 转换为结果格式
            keyword_results = []
            for word, stats in keyword_stats.items():
                # 计算趋势（简化版本）
                trend = self._calculate_trend(stats['score'], stats['count'])
                
                keyword_result = KeywordResult(
                    word=word,
                    count=stats['count'],
                    trend=trend,
                    score=stats['score'],
                    category=stats['category'],
                    sentiment=stats['sentiment'],
                    sources=list(stats['sources'])
                )
                keyword_results.append(keyword_result)
            
            # 按分数排序
            keyword_results.sort(key=lambda x: x.score, reverse=True)
            
            # 限制数量
            keyword_results = keyword_results[:limit]
            
            return TrendingKeywordResult(
                keywords=keyword_results,
                total_words=sum(stats['count'] for stats in keyword_stats.values()),
                unique_words=len(keyword_stats),
                analyzed_items=len(data),
                time_range=f"{len(data)}items",
                updated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"提取热门关键词失败: {e}")
            return TrendingKeywordResult(
                keywords=[],
                total_words=0,
                unique_words=0,
                analyzed_items=0,
                time_range="error",
                updated_at=datetime.now().isoformat()
            )
    
    async def extract_alert_keywords(self, 
                                   data: List[Dict[str, Any]], 
                                   target_keywords: List[str],
                                   time_window: int = 60) -> AlertKeywordResult:
        """
        提取预警关键词（用于预警检查）
        
        Args:
            data: 新闻数据列表
            target_keywords: 目标关键词列表
            time_window: 时间窗口（分钟）
        """
        try:
            if not data or not target_keywords:
                return AlertKeywordResult(
                    matched_keywords=[],
                    total_matches=0,
                    time_window=time_window,
                    analyzed_items=len(data) if data else 0
                )
            
            # 时间窗口过滤
            current_time = datetime.now()
            time_threshold = current_time - timedelta(minutes=time_window)
            
            filtered_data = []
            for item in data:
                if 'created_at' in item:
                    try:
                        created_at = item['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        
                        if created_at >= time_threshold:
                            filtered_data.append(item)
                    except:
                        # 如果时间解析失败，仍然包含该数据
                        filtered_data.append(item)
                else:
                    filtered_data.append(item)
            
            # 关键词匹配统计
            matched_keywords = []
            keyword_counts = defaultdict(int)
            
            for item in filtered_data:
                title = item.get("title", "")
                content = item.get("content", "")
                text = f"{title} {content}".lower()
                
                for target_keyword in target_keywords:
                    if self._match_keyword_pattern(text, target_keyword):
                        keyword_counts[target_keyword] += 1
            
            # 转换为结果格式
            for keyword, count in keyword_counts.items():
                matched_keywords.append({
                    "word": keyword,
                    "count": count,
                    "time_window": time_window,
                    "matched_at": current_time.isoformat()
                })
            
            return AlertKeywordResult(
                matched_keywords=matched_keywords,
                total_matches=sum(keyword_counts.values()),
                time_window=time_window,
                analyzed_items=len(filtered_data)
            )
            
        except Exception as e:
            logger.error(f"提取预警关键词失败: {e}")
            return AlertKeywordResult(
                matched_keywords=[],
                total_matches=0,
                time_window=time_window,
                analyzed_items=0
            )
    
    def _extract_keywords(self, text: str) -> Counter:
        """提取关键词"""
        # 清理文本
        text = re.sub(r'[^\u4e00-\u9fff\w\s]', ' ', text)
        
        keywords = []
        
        # 提取2-4字的中文词汇
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        keywords.extend(chinese_words)
        
        # 提取英文词汇（3字符以上）
        english_words = re.findall(r'[A-Za-z]{3,}', text)
        keywords.extend(english_words)
        
        # 过滤停用词和短词
        filtered_keywords = [
            word for word in keywords
            if len(word) >= 2 and word not in self.stop_words and word.strip()
        ]
        
        return Counter(filtered_keywords)
    
    def _match_keyword_pattern(self, text: str, pattern: str) -> bool:
        """匹配关键词模式"""
        if "*" in pattern or "?" in pattern:
            # 支持通配符匹配
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            return bool(re.search(regex_pattern, text, re.IGNORECASE))
        else:
            # 精确匹配或包含匹配
            return pattern.lower() in text.lower()
    
    def _classify_keyword(self, word: str) -> Optional[str]:
        """关键词分类"""
        for category, keywords in self.category_keywords.items():
            if any(kw in word for kw in keywords):
                return category
        return None
    
    def _analyze_sentiment(self, word: str) -> Optional[str]:
        """情感分析"""
        for sentiment, keywords in self.sentiment_keywords.items():
            if any(kw in word for kw in keywords):
                return sentiment
        return 'neutral'
    
    def _calculate_trend(self, score: float, count: int) -> str:
        """计算趋势"""
        # 简化的趋势计算
        if score > count * 1.2:
            return "up"
        elif score < count * 0.8:
            return "down"
        else:
            return "stable"


# 创建全局关键词分析引擎实例
keyword_engine = KeywordAnalysisEngine()
