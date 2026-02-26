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

## 待完成模块

### 📋 模块三：设备概况
- 设备渗透率
- 设备型号分布
- iOS/Android 系统版本占比

### 📋 模块四：休闲游戏详细分析
- 热门休闲游戏排行
- 用户画像分析
- 收入趋势

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
