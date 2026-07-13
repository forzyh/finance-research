# Market And Futures Instruments

## Chinese Futures Watchlist

The script uses Sina continuous futures symbols when available.

| Category | Name | Sina symbol | Why it matters |
|---|---|---|---|
| Agricultural | 鸡蛋 | `nf_JD0` | Protein consumption, feed costs, seasonal supply. |
| Agricultural | 玉米 | `nf_C0` | Feed grain, hog/poultry cost, inflation signal. |
| Agricultural | 豆粕 | `nf_M0` | Feed protein, soybean import and livestock chain. |
| Agricultural | 豆一 | `nf_A0` | Domestic soybean chain. |
| Agricultural | 豆油 | `nf_Y0` | Oils and fats, food inflation. |
| Agricultural | 棕榈油 | `nf_P0` | Global edible oil and import-cost channel. |
| Agricultural | 菜粕 | `nf_RM0` | Feed alternative and aquaculture chain. |
| Agricultural | 白糖 | `nf_SR0` | Food CPI and weather/supply shocks. |
| Agricultural | 棉花 | `nf_CF0` | Textile/export chain. |
| Agricultural | 苹果 | `nf_AP0` | Seasonal agricultural price signal. |
| Agricultural | 生猪 | `nf_LH0` | Protein CPI, feed demand, farming margin. |
| Black | 螺纹钢 | `nf_RB0` | Construction demand and real-estate chain. |
| Black | 热卷 | `nf_HC0` | Manufacturing and steel demand. |
| Black | 铁矿石 | `nf_I0` | Steel cost and China demand. |
| Black | 玻璃 | `nf_FG0` | Property completion chain. |
| Black | 纯碱 | `nf_SA0` | Glass and photovoltaic glass costs. |
| Energy/Chemicals | 上海原油 | `nf_SC0` | Domestic crude benchmark and geopolitics. |
| Energy/Chemicals | 燃油 | `nf_FU0` | Shipping/energy cost. |
| Energy/Chemicals | LPG | `nf_PG0` | Petrochemical and residential fuel. |
| Energy/Chemicals | PTA | `nf_TA0` | Polyester/textile chain. |
| Energy/Chemicals | 甲醇 | `nf_MA0` | Coal chemical and energy chain. |
| Metals | 铜 | `nf_CU0` | Global growth and electrification demand. |
| Metals | 铝 | `nf_AL0` | Power cost, construction, manufacturing. |
| Metals | 锌 | `nf_ZN0` | Infrastructure and industrial demand. |
| Metals | 镍 | `nf_NI0` | Stainless steel and batteries. |
| Precious | 黄金 | `nf_AU0` | Real rates, dollar, risk hedge. |
| Precious | 白银 | `nf_AG0` | Precious and industrial hybrid. |

## Cross-Asset Snapshot Checklist

- Equities: 上证指数, 深成指, 创业板指, 科创50, 恒生指数, 恒生科技, S&P 500, Nasdaq, Dow.
- Rates: 中债收益率, 美债 2Y/10Y, Fed rate expectations where available.
- FX: USD/CNY, USD/CNH, dollar index.
- Commodities: Brent/WTI, Shanghai crude, gold, silver, copper, iron ore.
- Crypto: BTC and ETH only when there is material news or large price action.

For post-close runs, record A-share and Hong Kong close times, domestic-futures day-session time, Europe early-trade time, and US futures/premarket time separately. Never present these asynchronous observations as one simultaneous close.

## Interpretation Hints

- Agricultural futures need driver checks: weather, disease, feed cost, inventory, imports, policy reserves, spot basis, and seasonality.
- Industrial futures often transmit through property/infrastructure, manufacturing PMIs, export orders, and inventory.
- Energy and precious metals often transmit through geopolitics, dollar, rates, shipping, and inflation expectations.

## Anomaly Checks

- Index versus breadth, turnover, size and growth/value spread.
- Headline severity versus oil, gold, dollar, rates and shipping response.
- Spot, futures, basis, inventory and physical-market disagreement.
- A/H technology versus US futures or the preceding US close after aligning sessions.
- Large gap followed by intraday retracement or failed follow-through.

An anomaly must preserve the baseline and operands so a research agent can reproduce it.
