# 手游信息池 Game Info Pool

自动采集 App Store / Google Play 全球榜单，AI 解读异动，生成 Excel 报告，推送企业微信。

**覆盖地区**：美国、英国、德国、法国、日本、韩国、印度尼西亚、泰国、新加坡、越南

---

## 输出内容

- `data/榜单日报_YYYY-MM-DD.xlsx` — 每日自动生成，包含：
  - **今日榜单** sheet：10个地区 × App Store + Google Play 全量数据
  - **今日异动** sheet：新进榜、退榜、大幅变动的游戏
  - **AI分析** sheet：MiniMax 自动撰写的市场解读
  - **说明** sheet：报告元数据
- `data/手游周报_YYYY-MM-DD.xlsx` — 每周一生成，包含各地区 Top10 和 AI 周报
- 企业微信群每日推送异动摘要 + AI 解读

---

## 快速部署（Step by Step）

### 第一步：上传代码到 GitHub

1. 登录 [github.com](https://github.com)，点击右上角 `+` → `New repository`
2. 仓库名填 `game-info-pool`，选 **Private**（私有）
3. 把此项目所有文件上传进去

---

### 第二步：在 GitHub 仓库配置 Secrets

进入仓库页面：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

**必填：**

| Secret 名称 | 填入内容 |
|------------|---------|
| `MINIMAX_API_KEY` | 你的 MiniMax API Key |
| `MINIMAX_GROUP_ID` | MiniMax 控制台的 Group ID |
| `WECOM_WEBHOOK_URL` | 企业微信群机器人的 Webhook URL |

**选填（邮件周报）：**

| Secret 名称 | 填入内容 |
|------------|---------|
| `EMAIL_USER` | 发件邮箱 |
| `EMAIL_PASS` | 邮箱应用密码 |
| `EMAIL_TO` | 收件邮箱，多个用逗号分隔 |

---

### 第三步：开启 GitHub Actions 写权限

`Settings` → `Actions` → `General` → `Workflow permissions` → 选 `Read and write permissions` → Save

---

### 第四步：手动触发第一次运行（测试）

1. 进入仓库的 `Actions` 标签页
2. 左侧点击 `每日榜单采集`
3. 点击 `Run workflow` → `Run workflow`
4. 等待运行完成后，在仓库 `data/` 目录下载 Excel 文件查看

---

## 自动运行时间

| 任务 | 运行时间 |
|------|---------|
| 每日榜单采集 + Excel 生成 | 每天北京时间 **08:00** |
| 每周报告 | 每周一北京时间 **09:00** |

---

## 项目结构

```
game-info-pool/
├── .github/workflows/
│   ├── daily_scrape.yml      # 每日自动采集
│   └── weekly_report.yml     # 每周报告
├── scrapers/
│   ├── appstore_scraper.py   # App Store 榜单（苹果官方 RSS API）
│   ├── googleplay_scraper.py # Google Play 榜单
│   └── change_detector.py   # 异动检测
├── analyzer/
│   └── ai_analyzer.py        # AI 分析（MiniMax）
├── reporter/
│   ├── excel_writer.py       # Excel 报告生成
│   └── notifier.py           # 企业微信 + 邮件推送
├── data/
│   ├── history/              # 每日 JSON 原始数据（用于异动对比）
│   ├── 榜单日报_YYYY-MM-DD.xlsx   # 每日 Excel 报告
│   └── 手游周报_YYYY-MM-DD.xlsx   # 每周 Excel 报告
├── main_daily.py             # 每日入口
├── main_weekly.py            # 每周入口
└── requirements.txt
```

---

## 常见问题

**Q: 企业微信 Webhook 怎么创建？**
A: 在企业微信群 → 右键点群名 → 添加机器人 → 复制 Webhook 地址。

**Q: MiniMax Group ID 在哪里找？**
A: 登录 [MiniMax 开放平台](https://www.minimaxi.com)，进入控制台，Group ID 显示在账号信息页。

**Q: 如何下载 Excel 文件？**
A: 进入 GitHub 仓库 → `data/` 目录 → 点击文件名 → 右上角 Download 按钮。

**Q: Google Play 抓取偶尔失败？**
A: 属于正常现象，代码已加入重试间隔，重新触发 workflow 即可。
