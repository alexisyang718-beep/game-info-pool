# 项目进度 PROGRESS

## 已完成模块

### ✅ 模块一：榜单数据采集与仪表盘

**功能**
- 自动采集 App Store / Google Play 全球榜单（10个地区）
- 异动检测（新进榜、退榜、排名变动≥5）
- AI 市场解读（MiniMax API）
- Excel 日报/周报生成
- 企业微信推送

**文件**
- `scrapers/appstore_scraper.py` - App Store 榜单采集
- `scrapers/googleplay_scraper.py` - Google Play 榜单采集
- `scrapers/change_detector.py` - 异动检测
- `analyzer/ai_analyzer.py` - AI 分析
- `reporter/excel_writer.py` - Excel 报告生成
- `reporter/dashboard_writer.py` - 仪表盘 JSON 输出
- `main_daily.py` - 每日流程入口
- `.github/workflows/daily_scrape.yml` - 每日自动工作流
- `.github/workflows/weekly_report.yml` - 每周报告工作流

**数据覆盖：**
- 地区：美国、英国、德国、法国、日本、韩国、印尼、泰国、新加坡、越南
- 榜单类型：免费游戏榜、付费游戏榜、畅销榜
- 商店：App Store、Google Play

---

### ✅ 模块二：重点地区用户市场概况

**功能**
- 新增「市场概况」Tab 页
- 展示10个地区的手游市场画像
- 自动更新 World Bank 宏观数据
- 静态维护游戏品类偏好和市场特性

**新增文件**
| 文件 | 说明 |
|------|------|
| `data/market_static.json` | 10个地区的品类偏好和市场描述（静态） |
| `scrapers/market_scraper.py` | World Bank API 数据采集脚本 |
| `.github/workflows/monthly_market.yml` | 每月1日自动更新工作流 |
| `data/market.json` | 动态+静态合并的市场数据 |

**数据指标：**
- 手机普及率（台/百人）
- 互联网渗透率（%）
- 人口总数
- 人均 GDP（USD）
- 估算移动设备数
- 游戏品类偏好（Top3）
- 地区市场特性描述

**自动运行：**
- 每月1日 UTC 01:00 自动更新市场数据

**仪表盘访问：**
- https://alexisyang718-beep.github.io/game-info-pool/

---

### ✅ 模块三：设备概况

**功能**
- 新增「设备概况」Tab 页
- 展示10个地区的移动设备市场数据
- iOS/Android 占比分布
- 热门机型排行榜（Top5）
- iOS/Android 系统版本分布

**新增文件**
| 文件 | 说明 |
|------|------|
| `data/device_static.json` | 10个地区的设备数据（静态，IDC/StatCounter/Counterpoint 来源）|
| `scrapers/device_scraper.py` | 读取静态 JSON 并生成 device.json |
| `.github/workflows/monthly_device.yml` | 每月1日自动更新工作流 |
| `data/device.json` | 供仪表盘读取的设备数据 |

**数据指标：**
- iOS 占比（%）
- Android 占比（%）
- 热门机型列表（Top5，含市场份额）
- iOS 版本分布（按版本）
- Android 版本分布（按版本）
- 地区设备Notes描述

**自动运行：**
- 每月1日 UTC 02:00 自动更新设备数据

**仪表盘访问：**
- https://alexisyang718-beep.github.io/game-info-pool/

---

## 待完成模块

### ✅ 模块四：休闲游戏详细分析

**功能**
- 新增「休闲游戏」Tab 页
- 各地区热门休闲游戏 Top 10（人工策展，含细分品类标签）
- 用户画像：年龄段分布、性别比例、付费转化率、月ARPU、日均游玩次数/时长
- 收入趋势相对指数（以2025 Q3=100为基准，季度对比）
- 地区市场洞察文字

**新增文件**
| 文件 | 说明 |
|------|------|
| `data/casual_static.json` | 10个地区的休闲游戏静态数据（手工维护） |
| `scrapers/casual_scraper.py` | 读取静态 JSON 并生成 casual.json |
| `.github/workflows/monthly_casual.yml` | 每季度首月1日自动更新工作流 |
| `data/casual.json` | 供仪表盘读取的输出数据 |

**数据设计：**
- 细分品类标签：三消、纸牌、益智消除、合并、跑酷、棋盘派对、模拟生活、模拟经营、三消+叙事等
- 用户画像基于行业报告（data.ai / App Annie）
- 收入趋势用相对指数避免难以核实的绝对数字
- 每款游戏含 `chart_rank` 字段（在免费总榜的实际排名）作为客观依据

**自动运行：**
- 每季度首月1日 UTC 03:00 自动更新（1月/4月/7月/10月）

### 📋 模块五：仪表盘增强
- 历史趋势图表
- 地区对比功能
- 数据导出功能

---

## 技术栈

- **Python 3.11** - 数据采集和处理
- **Node.js 20** - Google Play 抓取（google-play-scraper）
- **MiniMax API** - AI 分析
- **GitHub Actions** - 自动化工作流
- **GitHub Pages** - 仪表盘托管
- **纯 HTML/CSS/JS** - 前端界面

---

## 仓库信息

- GitHub: https://github.com/alexisyang718-beep/game-info-pool
- 仪表盘: https://alexisyang718-beep.github.io/game-info-pool/
- 分支: `main` (开发), `gh-pages` (部署)
