#!/usr/bin/env python3
"""
舆情监控平台快速启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True


def check_dependencies():
    """检查依赖包"""
    try:
        import fastapi
        import uvicorn
        import pymongo
        import motor
        import aiohttp
        import loguru
        import apscheduler
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def create_directories():
    """创建必要的目录"""
    directories = ["logs", "static"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ 目录结构检查通过")


def check_mongodb_connection():
    """检查MongoDB连接"""
    try:
        from pymongo import MongoClient
        from config import settings
        
        client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        client.close()
        print("✅ MongoDB连接检查通过")
        return True
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        print(f"请检查MongoDB服务是否运行，连接地址: {settings.MONGODB_URL}")
        return False


def test_data_source():
    """测试数据源连接"""
    try:
        import requests
        from config import settings
        
        test_url = f"{settings.PRIMARY_BASE_URL}?id=zhihu"
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 数据源连接检查通过")
            return True
        else:
            print(f"⚠️  数据源连接异常: HTTP {response.status_code}")
            return True  # 不阻止启动
    except Exception as e:
        print(f"⚠️  数据源连接测试失败: {e}")
        return True  # 不阻止启动


def main():
    """主函数"""
    print("🚀 舆情监控平台启动检查")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 检查依赖包
    if not check_dependencies():
        return False
    
    # 创建目录
    create_directories()
    
    # 检查MongoDB连接
    if not check_mongodb_connection():
        print("\n💡 提示: 如果MongoDB未安装，可以使用Docker快速启动:")
        print("docker run -d --name mongodb -p 27017:27017 mongo:latest")
        return False
    
    # 测试数据源
    test_data_source()
    
    print("\n" + "=" * 50)
    print("✅ 所有检查通过，启动应用...")
    print("=" * 50)
    
    # 启动应用
    try:
        from main import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
