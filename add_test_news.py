#!/usr/bin/env python3
"""
添加测试新闻数据，包含"数据泄露"关键词
"""
import asyncio
from datetime import datetime, timedelta
from database import DatabaseManager
import uuid

async def add_test_news():
    """添加测试新闻数据"""
    
    # 初始化数据库
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    print("🚀 开始添加测试新闻数据...")
    
    # 创建包含"数据泄露"关键词的测试新闻
    test_news = [
        {
            "_id": str(uuid.uuid4()),
            "id": f"test_data_leak_{int(datetime.now().timestamp())}001",
            "title": "某大型科技公司发生严重数据泄露事件，影响数百万用户",
            "pubDate": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "url": "https://example.com/news/data-leak-001",
            "extra": {"info": False},
            "source_id": "test_source",
            "source_name": "测试新闻源",
            "category": "technology",
            "priority": 1,
            "collected_at": datetime.now(),
            "created_at": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "_id": str(uuid.uuid4()),
            "id": f"test_data_leak_{int(datetime.now().timestamp())}002",
            "title": "网络安全专家警告：数据泄露事件频发，企业需加强防护",
            "pubDate": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "url": "https://example.com/news/data-leak-002",
            "extra": {"info": False},
            "source_id": "test_source",
            "source_name": "测试新闻源",
            "category": "technology",
            "priority": 1,
            "collected_at": datetime.now(),
            "created_at": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "_id": str(uuid.uuid4()),
            "id": f"test_data_leak_{int(datetime.now().timestamp())}003",
            "title": "政府部门发布数据泄露防护新规定，要求企业严格执行",
            "pubDate": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "url": "https://example.com/news/data-leak-003",
            "extra": {"info": False},
            "source_id": "test_source",
            "source_name": "测试新闻源",
            "category": "policy",
            "priority": 1,
            "collected_at": datetime.now(),
            "created_at": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "_id": str(uuid.uuid4()),
            "id": f"test_data_leak_{int(datetime.now().timestamp())}004",
            "title": "银行业数据泄露案例分析：如何避免客户信息外泄",
            "pubDate": (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "url": "https://example.com/news/data-leak-004",
            "extra": {"info": False},
            "source_id": "test_source",
            "source_name": "测试新闻源",
            "category": "finance",
            "priority": 1,
            "collected_at": datetime.now(),
            "created_at": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "_id": str(uuid.uuid4()),
            "id": f"test_data_leak_{int(datetime.now().timestamp())}005",
            "title": "国际数据泄露事件回顾：2024年十大安全事故盘点",
            "pubDate": (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
            "url": "https://example.com/news/data-leak-005",
            "extra": {"info": False},
            "source_id": "test_source",
            "source_name": "测试新闻源",
            "category": "technology",
            "priority": 1,
            "collected_at": datetime.now(),
            "created_at": datetime.now(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    ]
    
    # 插入测试数据
    result = await db_manager.insert_data(test_news)
    
    if result:
        print(f"✅ 成功添加 {len(test_news)} 条包含'数据泄露'关键词的测试新闻")
        
        # 验证数据是否插入成功
        search_result, total = await db_manager.search_data(keyword="数据泄露", limit=10)
        print(f"✅ 验证：现在数据库中有 {total} 条包含'数据泄露'的新闻")
        
        for i, news in enumerate(search_result[:3], 1):
            print(f"   {i}. {news.get('title', 'N/A')}")
    else:
        print("❌ 添加测试数据失败")
    
    # 关闭连接
    await db_manager.close()
    print("🎉 测试数据添加完成！")

if __name__ == "__main__":
    asyncio.run(add_test_news())
