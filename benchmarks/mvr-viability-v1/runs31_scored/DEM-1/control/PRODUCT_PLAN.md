# c01 — SMS Crop Price Alerts (Kenya)

## v1 (ship in ~3 weeks)
A daily SMS to farmers with the current market price for the 1-2 crops they grow, in their local market. Start with one region (e.g. Rift Valley) and 3-4 high-volume crops (maize, tomatoes, potatoes, beans). Farmer registers by texting a keyword; we ask crop + nearest market via a short USSD/SMS flow.

## Core features
- SMS subscription + crop/market selection.
- Daily price broadcast per crop-market pair.
- On-demand pull: text a crop, get today's price back.
- Simple admin dashboard to enter/update daily prices.

## Tech approach
- Africa's Talking (or Twilio) for SMS + USSD short code — no smartphone required, which is the whole point.
- Small backend (Node or Python + Postgres) holding crops, markets, prices, subscribers.
- Price data sourced first from manual entry by a field agent pulling from KAMIS/local market boards; automate scraping later.
- Cron job fires the morning broadcast. Keep it dumb and reliable.

## Go-to-market
- The "20 bob/week" claim is unproven — do NOT lead with paid. Run a free 4-week pilot with one cooperative or agrovet to prove farmers actually open and act on the SMS.
- Recruit through SACCOs, cooperatives, and agrovet shops who already have farmer lists and trust.
- Once retention is real, introduce billing via a weekly airtime/M-Pesa deduction, and test whether price sensitivity matches the founder's assumption.

## Biggest risk
Data freshness and coverage. If prices are stale or the wrong market, trust dies fast. Nail one region's data quality before expanding.
