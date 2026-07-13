# Finance News Intake Sources

## Priority 7x24 Discovery Sources

Use these sources first for hot-spot discovery. They are not final proof for major facts. The default unattended run should cover the latest 30 hours, not only the latest screen of headlines.

| Source | URL or endpoint | Notes |
|---|---|---|
| 财联社电报 | `https://m.cls.cn/telegraph` | A-shares, policy, company announcements, industrial chains. Parse time, content, tags, id/shareurl when available. |
| 东方财富全球财经快讯 | `https://np-weblist.eastmoney.com/comm/web/getFastNewsList?client=web&biz=web_724&fastColumn=102&sortEnd=&pageSize=50&req_trace={timestamp}` | JSON/JSONP fastNewsList. Fields include showTime, title, summary, stockList, realSort, code. |
| 新浪财经 7x24 | `https://app.cj.sina.com.cn/api/news/pc?page=1&size=20` | JSON feed. Fields include rich_text, create_time, tag, docurl/ext, view_num. |
| 华尔街见闻快讯 | `https://wallstreetcn.com/live` | SSR page includes live-news data. Parse display_time, content_text, title, uri, channels, symbols, score when available. |
| 同花顺 7x24 | `http://stock.10jqka.com.cn/thsgd/realtimenews.js`, `http://stock.10jqka.com.cn/thsgd/ywjh.js` | Requires browser User-Agent and GBK/GB18030 decoding. Parse thsRss.item fields. |

## Broader Collection Lanes

- Official/policy: 中国人民银行, 国家统计局, 财政部, 发改委, 证监会, 上交所, 深交所, 北交所, 国务院/部委, Fed, BLS, BEA, ECB, BOJ.
- Market/global: Reuters, AP, CNBC, MarketWatch, official exchange pages, central bank sites, commodity exchange notices.
- China markets/industry: 新华社, 央视财经, 证券时报, 上海证券报, 中国证券报, 第一财经, 财新, 财联社, 21财经, company announcements.
- Company events: exchange filings, company IR, SEC EDGAR, HKEXnews, official press releases.

## Post-close Editorial And Research Sources

Use these as data/reference sources and coverage checks. Do not copy their wording or let their framing substitute for a research question.

| Source | URL/search entry | Use |
|---|---|---|
| 财联社收盘/复盘 | Search `site:cls.cn 收盘 复盘 A股 港股` | Check index, sector, company and post-close announcement coverage. |
| 交易所与公司公告 | 上交所、深交所、北交所、港交所、SEC、公司IR | Establish primary-source facts and exact disclosure times. |
| 权威宏观与政策发布 | 国务院、部委、央行、统计机构、主要央行 | Establish policy wording, effective dates and quantitative baselines. |
| 全球市场权威来源 | Reuters, AP, official exchange and central-bank pages | Cross-check Europe early trade, US premarket and geopolitical claims. |
| 商品与期货来源 | 交易所公告、库存与现货数据、可靠行业机构 | Check settlement, inventory, basis, weather and physical-market evidence. |

## Hot Stock Collection Lane

- Collect company names and tickers from stock tags in 7x24 feeds, exchange announcements, top gainers/losers, high-turnover lists, inquiry letters, abnormal-volatility announcements, and morning editorial sources.
- Search patterns: `{股票名} 公告 异动 问询函 业绩 回购 并购`, `{股票名} 涨停 原因 板块`, `{ticker} earnings guidance SEC`, `{股票名} 港股 美股 中概股`.
- Preserve whether the stock story is confirmed, rumor-driven, announcement-driven, market-only, or a post-close variable.

## Raw Anomaly Search Lane

- Search for observable disagreement: `利好 价格未涨`, `风险升级 黄金 油价 反应`, `指数上涨 个股下跌`, `成交放大 反转`, `公告前 异动`, `现货 期货 背离`.
- Capture the baseline and exact time window. A surprising headline without a market or factual contrast is not yet an anomaly.
- Preserve at least two plausible explanations and the evidence needed to distinguish them.

## Technology Stock Collection Lane

- Broad tech: `纳斯达克 科技股`, `费城半导体指数`, `恒生科技指数`, `科创50`, `创业板 科技股`, `AI 科技股 盘前`, `semiconductor earnings guidance capex`.
- AI infrastructure: `AI 服务器 光模块 液冷 数据中心 电力`, `GPU ASIC AI server optical module capex`, `云厂商 capex AI`.
- AI applications/software: `AI 应用 软件 SaaS 商业化`, `enterprise AI revenue`, `AI agent software stock`.
- Semiconductors: `半导体 设备 材料 EDA 先进封装 存储`, `export controls chip equipment memory foundry`.
- Internet platforms: `互联网平台 财报 回购 广告 游戏 电商 云`, `China internet earnings buyback regulation`.
- Consumer electronics: `消费电子 手机 PC MR 供应链 订单 库存`, `smartphone PC wearable supply chain`.
- Smart vehicles/robotics: `智能驾驶 机器人 人形机器人 汽车电子 激光雷达`, `autonomous driving humanoid robotics auto chip`.
- Digital infrastructure: `光模块 通信设备 数据中心 网络安全 卫星互联网`, `optical module data center power cooling cybersecurity`.
- Preserve subsector, market scope, leading names, peer names, source layer, and whether the driver is confirmed.

## Search Query Patterns

- Chinese policy: `{政策主题} 央行 国家统计局 财政部 发改委 证监会`
- Company event: `{公司名} 公告 业绩 订单 回购 并购 监管`
- Global macro: `{event} Reuters Fed inflation yield dollar oil gold`
- Futures driver: `{品种} 期货 库存 现货 基差 天气 进口 出口 政策`
