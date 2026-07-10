# c09 — 15-Minute Grocery Delivery (Accra)

## v1 (prove the unit economics before the promise)
15-minute delivery from dark stores is operationally brutal and has bankrupted well-funded players globally. Be honest with the founder: v1 should test whether one dark store in one dense Accra neighborhood can deliver a tight SKU range fast and profitably. Consider "fast" (30-45 min) over a hard 15-min SLA until the model works. v1 = one store, one zone, one app.

## Core features
- Customer app: browse a curated ~1,000-2,000 SKU range, order, live ETA, delivery.
- Real-time inventory tied to the dark store (can't sell what's not on the shelf).
- Rider dispatch + picking workflow for staff.
- Payments: Mobile Money (MTN MoMo) + card; cash optional.

## Tech approach
- Flutter/React Native customer app; internal picker + rider apps/web.
- Node/Postgres + Redis for live inventory and dispatch.
- Maps/routing for the delivery radius; keep the zone tight so ETAs are physically achievable.

## Go-to-market
- Single high-density catchment where average basket + order frequency can cover rider + store costs. Delivery radius is everything — small radius, fast times, real margins.
- Acquire via hyperlocal digital ads and launch promos; watch retention and contribution margin per order like a hawk.
- Expand only by cloning a proven, profitable store — never subsidize your way into new zones.

## Biggest risk
Unit economics. Speed promises + subsidies burn cash fast. Prove one store makes money before scaling, and don't over-commit to "15 minutes" if it breaks the math.
