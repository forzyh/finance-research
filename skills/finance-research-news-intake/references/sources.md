# 财经新闻采集来源

## 优先7x24发现来源

优先使用下列来源发现热点，但它们不能作为重大事实的最终证明。默认无人值守运行应覆盖最近30小时，而不是只读取当前一屏标题。

| 来源 | URL 或端点 | 说明 |
|---|---|---|
| 财联社电报 | `https://m.cls.cn/telegraph` | A股、政策、公司公告、产业链；可取得时解析时间、正文、标签、id/shareurl |
| 东方财富全球财经快讯 | `https://np-weblist.eastmoney.com/comm/web/getFastNewsList?client=web&biz=web_724&fastColumn=102&sortEnd=&pageSize=50&req_trace={timestamp}` | JSON/JSONP `fastNewsList`；字段包括 showTime、title、summary、stockList、realSort、code |
| 新浪财经 7x24 | `https://app.cj.sina.com.cn/api/news/pc?page=1&size=20` | JSON 信息流；字段包括 rich_text、create_time、tag、docurl/ext、view_num |
| 华尔街见闻快讯 | `https://wallstreetcn.com/live` | SSR 页面包含实时新闻；可取得时解析 display_time、content_text、title、uri、channels、symbols、score |
| 同花顺 7x24 | `http://stock.10jqka.com.cn/thsgd/realtimenews.js`, `http://stock.10jqka.com.cn/thsgd/ywjh.js` | 需要浏览器 User-Agent 和 GBK/GB18030 解码；解析 `thsRss.item` 字段 |

## 扩展采集路径

- 官方/政策：中国人民银行、国家统计局、财政部、发改委、证监会、上交所、深交所、北交所、国务院/部委、Fed、BLS、BEA、ECB、BOJ。
- 市场/全球：Reuters、AP、CNBC、MarketWatch、交易所官网、央行网站、商品交易所公告。
- 中国市场/行业：新华社、央视财经、证券时报、上海证券报、中国证券报、第一财经、财新、财联社、21财经、公司公告。
- 公司事件：交易所文件、公司 IR、SEC EDGAR、港交所披露易、官方新闻稿。

## 盘后编辑与研究来源

这些来源用于数据、参考和覆盖检查。不得照抄措辞，也不得让其既有框架代替研究问题。

| 来源 | URL/搜索入口 | 用途 |
|---|---|---|
| 财联社收盘/复盘 | 搜索 `site:cls.cn 收盘 复盘 A股 港股` | 检查指数、行业、公司和盘后公告覆盖 |
| 交易所与公司公告 | 上交所、深交所、北交所、港交所、SEC、公司IR | 确认一手事实和精确披露时间 |
| 权威宏观与政策发布 | 国务院、部委、央行、统计机构、主要央行 | 确认政策措辞、生效日期和量化基准 |
| 全球市场权威来源 | Reuters、AP、交易所和央行官网 | 交叉检查欧洲早盘、美股盘前和地缘论断 |
| 商品与期货来源 | 交易所公告、库存与现货数据、可靠行业机构 | 检查结算、库存、基差、天气和实物市场证据 |

## 热点个股采集路径

- 从7x24股票标签、交易所公告、涨跌幅榜、高成交榜、问询函、异常波动公告和早间编辑来源中采集公司名与代码。
- 搜索式：`{股票名} 公告 异动 问询函 业绩 回购 并购`、`{股票名} 涨停 原因 板块`、`{ticker} earnings guidance SEC`、`{股票名} 港股 美股 中概股`。
- 保留事件属于已确认、传闻驱动、公告驱动、纯市场变化或盘后变量的状态。

## 原始异常搜索路径

- 搜索可观察的不一致：`利好 价格未涨`、`风险升级 黄金 油价 反应`、`指数上涨 个股下跌`、`成交放大 反转`、`公告前 异动`、`现货 期货 背离`。
- 记录基准和精确时间窗口。只有惊人标题、没有市场或事实对比，尚不构成异常。
- 保留至少两个可信解释，以及区分它们所需的证据。

## 科技股采集路径

- 宽基科技：`纳斯达克 科技股`、`费城半导体指数`、`恒生科技指数`、`科创50`、`创业板 科技股`、`AI 科技股 盘前`、`semiconductor earnings guidance capex`。
- AI 基础设施：`AI 服务器 光模块 液冷 数据中心 电力`、`GPU ASIC AI server optical module capex`、`云厂商 capex AI`。
- AI 应用/软件：`AI 应用 软件 SaaS 商业化`、`enterprise AI revenue`、`AI agent software stock`。
- 半导体：`半导体 设备 材料 EDA 先进封装 存储`、`export controls chip equipment memory foundry`。
- 互联网平台：`互联网平台 财报 回购 广告 游戏 电商 云`、`China internet earnings buyback regulation`。
- 消费电子：`消费电子 手机 PC MR 供应链 订单 库存`、`smartphone PC wearable supply chain`。
- 智能车/机器人：`智能驾驶 机器人 人形机器人 汽车电子 激光雷达`、`autonomous driving humanoid robotics auto chip`。
- 数字基础设施：`光模块 通信设备 数据中心 网络安全 卫星互联网`、`optical module data center power cooling cybersecurity`。
- 保留细分赛道、市场范围、龙头、同行、来源层和驱动是否确认。

## 搜索式模板

- 中国政策：`{政策主题} 央行 国家统计局 财政部 发改委 证监会`
- 公司事件：`{公司名} 公告 业绩 订单 回购 并购 监管`
- 全球宏观：`{event} Reuters Fed inflation yield dollar oil gold`
- 期货驱动：`{品种} 期货 库存 现货 基差 天气 进口 出口 政策`
