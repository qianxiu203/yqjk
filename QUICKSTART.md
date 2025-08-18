# 🚀 舆情监控平台快速启动指南

## 📋 前置要求

- Python 3.8+
- MongoDB 4.0+（或使用Docker）
- 网络连接（访问数据源API）

## ⚡ 快速启动（推荐）

### 方式一：使用部署脚本（最简单）

```bash
# 1. 下载项目
git clone <repository-url>
cd sentiment-monitor

# 2. 运行自动部署脚本
python deploy.py

# 3. 启动应用
python main.py
```

### 方式二：使用Docker（推荐生产环境）

```bash
# 1. 启动所有服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f sentiment-monitor

# 3. 访问应用
# Web界面: http://localhost
# API文档: http://localhost/docs
```

### 方式三：手动安装

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置MongoDB连接等

# 5. 启动应用
python main.py
```

## 🔧 配置说明

### 环境变量配置（.env文件）

```bash
# MongoDB配置（必须）
MONGODB_URL=mongodb://14.103.138.240:27017
DATABASE_NAME=sentiment_monitor

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据保留天数
DATA_TTL_DAYS=180

# 采集配置
COLLECTION_INTERVAL=300
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
```

### MongoDB连接配置

如果您没有MongoDB，可以使用以下方式快速启动：

```bash
# 使用Docker启动MongoDB
docker run -d --name mongodb -p 27017:27017 mongo:latest

# 或者使用Docker Compose
docker-compose up -d mongodb
```

## 🌐 访问应用

启动成功后，您可以访问：

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

## 📊 功能验证

### 1. 检查系统状态

```bash
# 运行系统测试
python test_system.py

# 快速检查
python test_system.py --mode quick
```

### 2. 手动触发数据采集

```bash
# 执行一次性采集
python main.py --mode once

# 或通过API触发
curl -X POST http://localhost:8000/api/collect
```

### 3. 查看数据

```bash
# 获取最新数据
curl http://localhost:8000/api/data/latest

# 搜索数据
curl "http://localhost:8000/api/search?keyword=人工智能"

# 获取统计信息
curl http://localhost:8000/api/statistics
```

## 🔍 故障排除

### 常见问题

1. **MongoDB连接失败**
   ```bash
   # 检查MongoDB是否运行
   docker ps | grep mongo

   # 测试连接
   python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017').admin.command('ping')"
   ```

2. **端口被占用**
   ```bash
   # 更改端口
   python main.py --port 8080

   # 或修改.env文件中的PORT配置
   ```

3. **数据采集失败**
   ```bash
   # 检查网络连接
   curl "https://new.0407123.xyz/api/s?id=zhihu"

   # 查看详细日志
   tail -f logs/sentiment_monitor.log
   ```

4. **API接口404错误**
   ```bash
   # 检查服务是否正常启动
   curl http://localhost:8000/api/health

   # 运行修复验证测试
   python test_fixes.py
   ```

5. **控制台JavaScript错误**
   - 确保Chart.js库正确加载
   - 检查浏览器控制台错误信息
   - 清除浏览器缓存后重新访问

### 🆕 最新修复

**v1.1.0 修复内容:**
- ✅ 修复API接口404错误
- ✅ 实现真实关键词数据提取（替换演示数据）
- ✅ 将"最新新闻"更改为"新闻看板"
- ✅ 修复JavaScript控制台错误
- ✅ 增强错误处理和安全检查
- ✅ 优化图表初始化逻辑

### 日志查看

```bash
# 实时查看日志
tail -f logs/sentiment_monitor.log

# 查看错误日志
grep ERROR logs/sentiment_monitor.log

# Docker环境查看日志
docker-compose logs -f sentiment-monitor
```

## 📈 使用指南

### Web界面功能

1. **数据浏览**: 查看最新采集的舆情数据
2. **分类筛选**: 按金融、科技、新闻等分类查看
3. **关键词搜索**: 全文搜索功能
4. **实时统计**: 查看数据采集统计信息
5. **手动采集**: 触发立即数据采集

### API使用

```python
import requests

# 获取数据
response = requests.get('http://localhost:8000/api/data?limit=10')
data = response.json()

# 搜索数据
response = requests.get('http://localhost:8000/api/search?keyword=股市')
results = response.json()

# 触发采集
response = requests.post('http://localhost:8000/api/collect')
```

## 🔧 高级配置

### 自定义采集频率

编辑 `scheduler.py` 文件，修改定时任务配置：

```python
# 高优先级数据源每3分钟采集
self.scheduler.add_job(
    self._collect_high_priority,
    trigger=IntervalTrigger(minutes=3),  # 修改这里
    ...
)
```

### 添加新数据源

在 `config.py` 文件中添加新的数据源：

```python
DATA_SOURCES = {
    "your_category": {
        "your_source_id": {"name": "数据源名称", "priority": 1}
    }
}
```

### 生产环境部署

1. **使用Nginx反向代理**
2. **配置SSL证书**
3. **设置系统服务**
4. **配置日志轮转**
5. **设置监控告警**

## 📞 获取帮助

- 查看完整文档: `README.md`
- 运行系统测试: `python test_system.py`
- 查看API文档: http://localhost:8000/docs
- 检查日志文件: `logs/sentiment_monitor.log`

## 🎯 下一步

1. 根据需要调整采集频率和数据源优先级
2. 配置数据备份策略
3. 设置监控和告警
4. 根据业务需求定制Web界面
5. 集成到现有系统中

---

🎉 **恭喜！您的舆情监控平台已经成功启动！**
