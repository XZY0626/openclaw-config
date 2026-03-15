# Scrapling Skill - 自适应网页爬虫框架

## 概述
基于 [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) v0.4.2 的高可靠网页抓取能力。
支持静态请求、JavaScript 渲染、浏览器自动化、反爬对抗。

## 能力范围
- **静态抓取**：requests/httpx 快速模式（无 JS）
- **动态渲染**：Playwright/Selenium 模式（stealth 插件）
- **浏览器自动化**：表单填写、点击、滚动、等待
- **爬取策略**：并发控制、请求延迟、随机 User-Agent
- **反爬对抗**：IP 代理池、headless 检测绕过、验证码处理（browserless）

## 接口方法

### fetch_html(url, mode='auto', **kwargs) -> str
抓取网页并返回 HTML（已渲染或原始）。

**参数：**
- `url` (str): 目标网页
- `mode` (str): 'static' | 'dynamic' | 'auto'（默认 auto）
- `wait_after` (int): 动态渲染后等待秒数
- `proxy` (str): 代理地址（可选）
- `timeout` (int): 超时秒数

**返回：** str HTML（失败返回空字符串）

**示例：**
```python
html = scrapling.fetch_html("https://example.com", mode='auto')
```

---

### extract_links(html, selector='a[href]') -> List[str]
从 HTML 中提取链接。

**参数：**
- `html` (str): 页面 HTML
- `selector` (str): CSS 选择器（默认所有 `<a>` 链接）

**返回：** List of URLs（绝对 URL）

**示例：**
```python
links = scrapling.extract_links(html, selector='.article-card a')
```

---

### extract_data(html, selectors: dict) -> dict
按选择器批量提取数据。

**参数：**
- `html` (str): 页面 HTML
- `selectors` (dict): 字段名 → CSS 选择器

**返回：** dict 字段 → 提取值（列表）

**示例：**
```python
data = scrapling.extract_data(html, {
    'title': 'h1',
    'content': 'article p',
    'author': '.author-name'
})
```

---

### crawl_site(start_url, rules: dict, max_pages=10) -> List[PageResult]
自动化全站爬取（遵循 robots.txt）。

**参数：**
- `start_url`: 起始 URL
- `rules`: 爬取规则（包含 `link_selector`, `data_selectors`）
- `max_pages`: 最大爬取页数

**返回：** List of `PageResult` 对象（含 url, html, extracted_data）

---

## 安全与合规
- **L0.1**：禁止修改系统目录，仅在 allowed 网络范围使用
- **隐私**：不收集用户数据，爬取结果仅用于合法用途
- **礼貌原则**：自动遵守 `robots.txt`，默认 1s 请求间隔
- **输出隔离**：结果保存到 `workspace/scrape_output/`（自动创建）

## 配置
环境变量（可选）：
- `SCRAPLING_TIMEOUT`：默认超时（秒）
- `SCRAPLING_PROXY`：默认代理
- `SCRAPLING_USER_AGENT`：自定义 UA 字符串

## 依赖
```bash
pip install scrapling[live]   # 包含 Playwright
playwright install chromium   # 安装浏览器
```

## 更新策略
- 监控官方 releases：https://github.com/D4Vinci/Scrapling/releases
- 每季度检查一次，评估升级必要性
- 升级前必须在沙箱测试接口兼容性
- 记录 changelog 到 `skills/scrapling/CHANGELOG.md`

## 版本
- **当前集成版本**：scrapling 0.4.2
- **安装日期**：2026-03-15
- **测试状态**：待集成

## 注意事项
- 动态渲染模式消耗较大内存（浏览器进程）
- 避免高频请求，防止 IP 被封
- 部分网站需要登录或验证码，需额外配置
