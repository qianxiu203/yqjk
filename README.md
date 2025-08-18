# 舆情监控平台

一个基于Python的全栈舆情监控平台，支持55个数据源的自动采集、存储和展示。

## 功能特性

- 🚀 **多数据源采集**: 支持55个数据源，包括金融、科技、新闻、社交、娱乐、体育等分类
- 📊 **实时监控**: 基于优先级的定时采集策略，高优先级数据源每5分钟采集一次
- 💾 **数据存储**: 使用MongoDB存储，支持TTL自动过期删除（180天）
- 🌐 **Web界面**: 响应式Web界面，支持搜索、过滤、分页等功能
- 📈 **统计分析**: 实时统计信息和数据可视化
- ⚡ **高性能**: 异步并发采集，支持主备服务器自动切换
- 🔧 **易部署**: 支持多种运行模式，配置简单

### 🆕 新增功能模块

#### 1. 系统状态监控
- **实时状态**: API、数据库、Redis、调度器状态监控
- **健康检查**: 4个核心组件健康状态实时显示
- **运行时间**: 系统运行时间动态更新

#### 2. 数据概览仪表板
- **数据源统计**: 55个数据源实时状态
- **新闻条目**: 实时新闻数量统计
- **采集成功率**: 数据采集质量监控
- **文档数量**: 数据库文档统计

#### 3. 关键词分析
- **热门排行**: 可配置1天/7天/30天统计周期
- **词汇统计**: 总词汇数和唯一词汇数统计
- **点击搜索**: 点击关键词直接跳转搜索
- **实时更新**: 5分钟自动刷新机制

#### 4. 智能新闻检索
- **最新新闻**: 实时新闻列表展示
- **智能搜索**: 全文搜索功能
- **搜索结果**: 分页显示搜索结果
- **数据源标识**: 清晰的新闻来源标签

#### 5. 数据可视化
- **时间趋势图**: 7天/30天数据采集趋势
- **数据源分析**: 按分类和TOP10统计
- **交互式图表**: 支持缩放和悬停交互
- **动态切换**: 图表类型和时间周期切换

## 系统架构

```
舆情监控平台
├── 数据采集层
│   ├── 55个数据源API
│   ├── 主备服务器切换
│   └── 并发采集控制
├── 数据存储层
│   ├── MongoDB数据库
│   ├── TTL索引管理
│   └── 数据分片存储
├── 业务逻辑层
│   ├── FastAPI后端服务
│   ├── 任务调度系统
│   └── 数据处理引擎
└── 展示层
    ├── Web前端界面
    ├── 实时数据展示
    └── 统计图表
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- MongoDB 4.0+
- 网络连接（访问数据源API）

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

复制并编辑环境配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置MongoDB连接等参数。

### 4. 运行应用

```bash
# 启动完整Web服务（推荐）
python main.py --mode server

# 仅运行数据采集器
python main.py --mode collector

# 执行一次性数据采集
python main.py --mode once

# 调试模式
python main.py --mode server --debug
```

### 5. 访问界面

打开浏览器访问：
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs

## 数据源配置

平台支持55个数据源，按分类如下：

### 金融类 (17个)
- 华尔街见闻、财联社、雪球、金十数据等

### 科技类 (19个)  
- V2EX、36氪、IT之家、GitHub、掘金等

### 新闻类 (7个)
- 联合早报、今日头条、澎湃新闻等

### 社交类 (6个)
- 知乎、微博、百度热搜等

### 娱乐类 (5个)
- 哔哩哔哩、快手等

### 体育类 (1个)
- 虎扑

## 采集策略

系统采用基于优先级的分层采集策略：

- **优先级1**: 每5分钟采集一次（重要数据源）
- **优先级2**: 每15分钟采集一次（一般数据源）  
- **优先级3**: 每30分钟采集一次（低频数据源）
- **全量采集**: 每小时执行一次完整采集

## API接口

### 主要接口

#### 数据查询接口
- `GET /api/data` - 查询数据
- `GET /api/data/latest` - 获取最新数据
- `GET /api/search` - 全文搜索
- `GET /api/statistics` - 获取统计信息

#### 分析接口
- `GET /api/keywords` - 获取热门关键词
- `GET /api/trends` - 获取数据趋势
- `GET /api/categories` - 获取数据源分类

#### 系统接口
- `GET /api/health` - 健康检查
- `GET /api/system/status` - 系统状态
- `GET /api/scheduler/status` - 调度器状态
- `POST /api/collect` - 手动触发采集
- `POST /api/scheduler/run/{job_id}` - 执行指定任务

### 查询参数

```bash
# 按数据源查询
GET /api/data?source_id=zhihu&limit=50

# 按分类查询
GET /api/data?category=finance&limit=100

# 时间范围查询
GET /api/data?start_date=2024-01-01&end_date=2024-01-31

# 全文搜索
GET /api/search?keyword=人工智能&limit=50
```

## Web界面功能

### 📊 数据概览页面
- **系统状态监控**: 实时显示API、数据库、调度器、采集器状态
- **关键指标展示**: 数据源数量、新闻条目、采集成功率、文档数量
- **最新新闻预览**: 显示最新采集的新闻条目

### 🏷️ 关键词分析页面
- **热词云图**: 可视化展示热门关键词，支持点击搜索
- **排行榜**: TOP10热门关键词排行榜
- **统计信息**: 总词汇数、唯一词汇数实时统计
- **时间筛选**: 支持1天/7天/30天数据统计周期

### 🔍 新闻检索页面
- **智能搜索**: 全文搜索功能，支持关键词检索
- **分类筛选**: 按金融、科技、新闻等6大分类查看
- **分页浏览**: 支持分页查看大量数据
- **数据源标识**: 清晰显示新闻来源和优先级

### 📈 数据可视化页面
- **趋势图表**: 7天/30天数据采集趋势分析
- **分布图表**: 数据源分类分布和TOP10统计
- **实时监控**: 采集成功/失败状态实时监控
- **交互功能**: 支持图表缩放、悬停、类型切换

## 数据库设计

### 集合结构

```javascript
{
  "_id": ObjectId,
  "title": "标题",
  "content": "内容",
  "source_id": "数据源ID",
  "source_name": "数据源名称", 
  "category": "分类",
  "priority": 1,
  "url": "原文链接",
  "created_at": ISODate,
  "collected_at": ISODate,
  "date": "2024-01-01"
}
```

### 索引设计

- TTL索引：`created_at` (180天自动删除)
- 查询索引：`source_id`, `category`, `priority`
- 全文索引：`title`, `content`

## 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t sentiment-monitor .

# 运行容器
docker run -d \
  --name sentiment-monitor \
  -p 8000:8000 \
  -e MONGODB_URL=mongodb://your-mongo-host:27017 \
  sentiment-monitor
```

### 系统服务

创建systemd服务文件：

```ini
[Unit]
Description=Sentiment Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/sentiment-monitor
ExecStart=/path/to/venv/bin/python main.py --mode server
Restart=always

[Install]
WantedBy=multi-user.target
```

## 监控和维护

### 日志管理

日志文件位置：`logs/sentiment_monitor.log`

- 自动按天轮转
- 保留30天历史
- 支持压缩存储

### 性能监控

- 采集成功率统计
- 响应时间监控
- 数据库性能指标
- 系统资源使用

### 数据维护

- 自动TTL过期删除
- 定期索引优化
- 数据统计报告

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MongoDB服务状态
   - 验证连接字符串配置
   - 确认网络连通性

2. **数据采集失败**
   - 检查网络连接
   - 验证API地址可访问性
   - 查看错误日志详情

3. **Web界面无法访问**
   - 确认端口未被占用
   - 检查防火墙设置
   - 验证静态文件路径

### 调试模式

```bash
# 启用详细日志
python main.py --mode server --debug

# 查看实时日志
tail -f logs/sentiment_monitor.log
```

#### 关键词过滤调试

1. **浏览器调试**：
   - 打开浏览器开发者工具 (F12)
   - 切换到 Console 标签页
   - 运行测试命令：`monitor.testFilterRules()`

2. **添加过滤规则测试**：
   ```javascript
   // 在浏览器控制台中测试
   monitor.testFilterRules();

   // 查看当前规则
   monitor.getStoredFilterRules();

   // 手动应用过滤
   monitor.applyFilterRules();
   ```

3. **常见调试场景**：
   - 黑名单规则不生效：检查关键词是否包含大小写问题
   - 正则表达式错误：在控制台查看错误信息
   - 规则冲突：多个规则可能相互影响，建议逐个测试

4. **调试步骤**：
   - 点击关键词标签页中的"测试过滤"按钮
   - 查看控制台输出的详细过滤过程
   - 确认规则是否正确应用

## 开发指南

### 项目结构

```
sentiment-monitor/
├── main.py              # 主启动文件
├── config.py            # 配置管理
├── database.py          # 数据库操作
├── collector.py         # 数据采集器
├── scheduler.py         # 任务调度器
├── api.py              # Web API服务
├── static/             # 静态文件
│   ├── index.html      # 主页面
│   └── app.js          # 前端脚本
├── requirements.txt    # 依赖包
├── .env               # 环境配置
└── README.md          # 说明文档
```

### 添加新数据源

1. 在 `config.py` 中添加数据源配置
2. 确保API返回格式兼容
3. 测试采集功能
4. 更新文档

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题请提交Issue或联系开发团队。
